import argparse
import yaml
import pandas as pd
from profit_analyzer.utils.logger import setup_logging
from profit_analyzer.utils.class_loader import initialize_from_config, discover_classes
from profit_analyzer.core.price_provider import YFinancePriceProvider
from profit_analyzer.utils.common_utils import log_dataframe_details


def build_equity_curve(trades: pd.DataFrame, price_provider) -> pd.Series:
    """
    Mark-to-market equity curve:
      - Fetch daily close for each *priceable* symbol.
      - Forward-fill positions.
      - Sum(position * price) per day.
      - If nothing is priceable, fallback to cash-flow cumulative sum.
    """
    t = trades.copy()
    t['date'] = pd.to_datetime(t['datetime']).dt.date

    symbols = sorted(t['symbol'].unique())
    start = str(min(t['date']))
    end =  str(pd.Timestamp.today().normalize().date())

    frames = []
    for sym in symbols:
        px = price_provider.history(sym, start, end)
        if px is None or px.empty:
            continue
        # Add symbol column; ensure index is named 'date' for uniform reset
        px = px.rename_axis('date')
        px['symbol'] = sym
        px = px.rename(columns={'close': 'price'})
        frames.append(px)

    if not frames:
        # No priceable symbols (e.g., only options/crypto without mapping) – fallback to cash-only equity
        cf = t.groupby('date')['cash_flow'].sum().sort_index()
        equity = cf.cumsum()
        equity.index = pd.to_datetime(equity.index)
        return equity

    prices = pd.concat(frames).reset_index()
    log_dataframe_details(prices)

    # Normalize column name to 'date' just in case
    # rename_date = {c: 'date' for c in prices.columns if c.lower() == 'date'}
    # prices = prices.rename(columns=rename_date)
    prices['date'] = pd.to_datetime(prices['date']).dt.date

    # Daily end-of-day position per symbol
    t['position'] = t.groupby('symbol')['qty'].cumsum()
    pos = t.groupby(['date', 'symbol'])['position'].last().unstack().sort_index()
    pos = pos.ffill().fillna(0.0)
    price_pivot = prices.pivot(index='date', columns='symbol', values='price').sort_index().ffill()

    # Align indices
    idx = sorted(set(pos.index) | set(price_pivot.index))
    pos = pos.reindex(idx).ffill().fillna(0.0)
    price_pivot = price_pivot.reindex(idx).ffill()

    equity = (pos * price_pivot).sum(axis=1)
    equity = pd.Series(equity.values, index=pd.to_datetime(list(equity.index)))
    log_dataframe_details(equity)

    return equity

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='src/profit_analyzer/config/config.yaml')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    logcfg = config.get('logging', {})
    logger = setup_logging(level=logcfg.get('level', 'INFO'),
                           logfile=logcfg.get('logfile', './logs/profit_analyzer.log'),
                           max_bytes=logcfg.get('max_bytes', 1048576),
                           backup_count=logcfg.get('backup_count', 5))
    logger.info("Starting Profit Analyzer")
    # instances = initialize_from_config(config, package_root='profit_analyzer')
    loaded_config = initialize_from_config(config, package_root='profit_analyzer')

    # class_map = {inst.__class__.__name__: inst for inst in instances}

    # file_loader = class_map['FileLoader']
    # webull_parser = class_map['WebullParser']
    portfolio_builder = loaded_config['folio_builder']
    profit_calc = loaded_config['profic_calculator']
    # price_provider = loaded_config['folio_builder']
    # bench = class_map['BenchmarkComparator']
    plotter = loaded_config['plotter']

    trades_raw_df = loaded_config['trades_data']['loader'].load_files()
    logger.info(f"Loaded {len(trades_raw_df)} rows from CSVs")

    trades = loaded_config['trades_data']['data_parser'].parse(trades_raw_df)
    logger.info(f"Parsed {len(trades)} filled trades across {trades['symbol'].nunique()} symbols")    
    if loaded_config.get("transfers_data"):
        transfers_raw_df = loaded_config['transfers_data']['loader'].load_files()
        transfers_cf = loaded_config['transfers_data']['data_parser'].parse(transfers_raw_df)
        if transfers_cf is not None and not transfers_cf.empty:
            logger.info(f"Loaded {len(transfers_raw_df)} rows from transfer CSVs, "
                        f"built {len(transfers_cf)} external cash-flow dates for MWR.")
        else:
            logger.info("No external transfers found or parsed; will fall back to trade-based flows.")

    positions = portfolio_builder.build_positions(trades)
    cash_flows = portfolio_builder.cash_flows(trades).set_index('date')['cash_flow']
    log_dataframe_details(trades)
    equity = build_equity_curve(trades, loaded_config['trades_data']['price_provider'])


    if trades.empty:
        logger.warning("No filled trades parsed after cleaning. Check Status values, timestamps, or column names.")
        print("No filled trades parsed. Please re-run after the parser update.")
        return
    # Returns time series (portfolio cumulative % return)
    port_pct = equity.pct_change().fillna(0).add(1).cumprod().sub(1).mul(100.0)

    # Metrics
    if profit_calc.method == 'money_weighted':
        mwr = profit_calc.compute_money_weighted(cash_flows, terminal_value=float(equity.iloc[-1]))
        logger.info(f"Money-weighted return (XIRR): {mwr:.2f}%")
    else:
        twr = profit_calc.compute_time_weighted(equity)
        logger.info(f"Time-weighted return: {twr:.2f}%")

    # Benchmark
    bcfg = loaded_config['benchmark']
    bench_df = bcfg['comparator'].compare(loaded_config['benchmark']['price_provider'], bcfg.get('start_date','2020-01-01'), bcfg.get('end_date','2030-12-31'))

    # Plots
    plotter.plot_equity_curve(equity, label="Portfolio")
    plotter.plot_vs_benchmark(port_pct, bench_df)

if __name__ == "__main__":
    main()

import pandas as pd
from collections import defaultdict

class PortfolioBuilder:
    """Aggregates parsed trades into position and cash-flow tables."""
    def __init__(self):
        pass

    def build_positions(self, trades: pd.DataFrame) -> pd.DataFrame:
        # cumulative position per symbol over time
        trades = trades.copy()
        trades['position'] = trades.groupby('symbol')['qty'].cumsum()
        return trades

    def cash_flows(self, trades: pd.DataFrame) -> pd.DataFrame:
        cf = trades[['datetime','cash_flow']].copy()
        # aggregate cash flows per day
        cf['date'] = pd.to_datetime(cf['datetime']).dt.date
        cf = cf.groupby('date')['cash_flow'].sum().reset_index()
        cf['date'] = pd.to_datetime(cf['date'])
        return cf

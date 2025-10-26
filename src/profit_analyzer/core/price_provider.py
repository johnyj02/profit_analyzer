from abc import ABC, abstractmethod
import pandas as pd
import re
import yfinance as yf


class PriceProvider(ABC):
    @abstractmethod
    def history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        ...

def _normalize_symbol_for_yf(sym: str) -> str | None:
    s = sym.upper().strip()

    # Skip OCC-style option symbols: e.g., TSLA250613P00360000
    if re.search(r"\d{6}[CP]\d{8}$", s):
        return None

    # Common crypto mappings
    crypto_map = {
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "SHIBUSD": "SHIB-USD",
        "DOGEUSD": "DOGE-USD",
    }
    if s in crypto_map:
        return crypto_map[s]

    # Valid equity/ETF tickers typically <=5 chars, but keep general.
    return s

class YFinancePriceProvider(PriceProvider):
    def history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        norm = _normalize_symbol_for_yf(symbol)
        if not norm:
            return pd.DataFrame()  # skip non-priced symbols (e.g., options)
        data = yf.download(norm, start=start, end=end, progress=False, auto_adjust=False )
        if data is None or data.empty:
            return pd.DataFrame()
        # Ensure a consistent DatetimeIndex and column name
        data.columns = [i[0] for i in data.columns]
        data = data[['Close']].rename(columns={'Close': 'close'})
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        return data

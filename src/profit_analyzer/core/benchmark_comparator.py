import pandas as pd

class BenchmarkComparator:
    def __init__(self, ticker: str = "VTI", price_provider: str | None = None):
        self.ticker = ticker
        self.price_provider_name = price_provider

    def compare(self, price_provider, start_date: str, end_date: str) -> pd.DataFrame:
        data = price_provider.history(self.ticker, start=start_date, end=end_date)
        if data.empty:
            return data
        data = data.copy()
        data['return_pct'] = (data['close'] / data['close'].iloc[0] - 1.0) * 100.0
        return data

import numpy as np
import pandas as pd

class ProfitCalculator:
    def __init__(self, method: str = "time_weighted"):
        self.method = method

    @staticmethod
    def _irr(cash_flows: pd.Series) -> float:
        # cash_flows indexed by date, values are cash (out negative, in positive)
        # numpy.irr expects equally spaced, so we compute XIRR via Newton method
        dates = pd.to_datetime(cash_flows.index).to_numpy()
        amounts = cash_flows.values.astype(float)
        if len(amounts) < 2:
            return 0.0

        # day count in years
        days = (dates - dates[0]).astype('timedelta64[D]').astype(float)
        years = days / 365.25

        def npv(rate):
            return (amounts / np.power(1 + rate, years)).sum()

        # bracket search
        low, high = -0.9999, 10.0
        for _ in range(100):
            mid = (low + high) / 2
            val = npv(mid)
            if abs(val) < 1e-8:
                return mid
            if val > 0:
                low = mid
            else:
                high = mid
        return mid

    def compute_time_weighted(self, equity_curve: pd.Series) -> float:
        # equity_curve: portfolio value over time (index: dates)
        returns = equity_curve.pct_change().dropna()
        growth = (1 + returns).prod() - 1.0
        return float(growth) * 100.0

    def compute_money_weighted(self, cash_flows: pd.Series, terminal_value: float) -> float:
        # Append terminal value as an inflow at the end
        cf = cash_flows.copy()
        last_date = cf.index.max()
        end_date = last_date + pd.Timedelta(days=1)
        cf.loc[end_date] = terminal_value
        rate = self._irr(cf.sort_index())
        return float(rate) * 100.0

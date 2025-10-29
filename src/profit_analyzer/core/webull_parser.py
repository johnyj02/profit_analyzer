import pandas as pd
import numpy as np
import re

# Handles Webull orders for equities & options. Produces signed cash flows.
class WebullParser:
    def __init__(self):
        pass

    @staticmethod
    def _normalize_side(s: str) -> str:
        if not isinstance(s, str):
            return "buy"
        s = s.strip().lower()
        # treat 'sell', 'sell to close', etc. as sell; everything else as buy
        return "sell" if s.startswith("sell") else "buy"

    @staticmethod
    def _strip_tz_suffix(series: pd.Series) -> pd.Series:
        # Remove trailing timezone tokens like " EDT", " PST"
        # (Pandas will soon error on unknown tz abbrevs)
        return series.astype(str).str.replace(r"\s+[A-Z]{2,4}$", "", regex=True)

    def parse(self, df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()

        # Rename only columns that exist
        rename_map = {
            'Name':'name',
            'Symbol':'symbol',
            'Side':'side',
            'Status':'status',
            'Filled':'filled_qty',
            'Total Qty':'total_qty',
            'Price':'price',
            'Avg Price':'avg_price',
            'Placed Time':'placed_time',
            'Filled Time':'filled_time'
        }
        d = d.rename(columns={k:v for k,v in rename_map.items() if k in d.columns})

        # Filter 'Filled' robustly
        if 'status' in d.columns:
            is_filled = d['status'].astype(str).str.contains('fill', case=False, na=False)
            d = d[is_filled].copy()
        if d.empty:
            return d.assign(datetime=pd.NaT, cash_flow=np.nan).iloc[0:0]

        # Parse times; drop unknown tz suffixes first
        if 'filled_time' in d.columns:
            dt_filled = pd.to_datetime(self._strip_tz_suffix(d['filled_time']), errors='coerce', utc=False)
        else:
            dt_filled = pd.Series(pd.NaT, index=d.index)

        if 'placed_time' in d.columns:
            dt_placed = pd.to_datetime(self._strip_tz_suffix(d['placed_time']), errors='coerce', utc=False)
        else:
            dt_placed = pd.Series(pd.NaT, index=d.index)

        datetime_col = dt_filled.fillna(dt_placed)
        d = d[~datetime_col.isna()].copy()
        if d.empty:
            return d.assign(datetime=pd.NaT, cash_flow=np.nan).iloc[0:0]

        d['datetime'] = datetime_col
        d['date'] = pd.to_datetime(d['datetime']).dt.date

        # Prices: prefer avg_price; fallback to price
        price = pd.to_numeric(d.get('avg_price', pd.Series(np.nan, index=d.index)), errors='coerce')
        fallback = pd.to_numeric(d.get('price', pd.Series(np.nan, index=d.index)), errors='coerce')
        d['price'] = price.where(~price.isna(), fallback)

        # Quantity: prefer 'Filled'; fallback to 'Total Qty'
        qty = pd.to_numeric(d.get('filled_qty', d.get('total_qty', pd.Series(np.nan, index=d.index))), errors='coerce').fillna(0.0)

        # Side & signed quantities
        side = d.get('side', 'Buy').astype(str).apply(self._normalize_side)
        d['qty'] = np.where(side == 'buy', qty, -qty)

        # Cash flows: Buy -> negative (outflow), Sell -> positive (inflow)
        gross = d['price'] * qty
        d['cash_flow'] = np.where(side == 'sell', gross, -gross)

        # Clean symbol
        d['symbol'] = d['symbol'].astype(str).str.strip().str.upper()

        parsed = d[['datetime', 'date', 'symbol', 'qty', 'price', 'cash_flow']].dropna(subset=['datetime', 'price'])
        parsed = parsed.sort_values('datetime').reset_index(drop=True)
        return parsed

class TransfersParser:
    """
    Parses brokerage transfer CSVs into a daily Series of EXTERNAL cash flows for MWR/XIRR.

    Expected columns (case-insensitive, tolerant):
      - transfer_type       e.g., 'Ach Incoming', 'ACH Incoming', 'Wire Outgoing', etc.
      - transfer_date       e.g., '05/04/2021 16:07 EDT'
      - transfer_status     e.g., 'Completed'
      - transfer_amount     numeric (pos)

    Sign convention (aligned with XIRR in ProfitCalculator):
      - Deposit INTO portfolio: NEGATIVE cash flow (your money goes in)  -> e.g., 'Incoming'
      - Withdrawal FROM portfolio: POSITIVE cash flow (money comes back) -> e.g., 'Outgoing'
    """
    def __init__(self, completed_only: bool = True):
        self.completed_only = completed_only

    @staticmethod
    def _strip_tz(s: pd.Series) -> pd.Series:
        return s.astype(str).str.replace(r"\s+[A-Z]{2,4}$", "", regex=True)

    def parse(self, df: pd.DataFrame) -> pd.Series:
        if df is None or df.empty:
            return pd.Series(dtype=float)

        d = df.copy()
        # Normalize columns
        lower = {c.lower().strip(): c for c in d.columns}
        def getcol(name_alts):
            for n in name_alts:
                if n in lower:
                    return lower[n]
            return None

        col_type   = getcol(["transfer_type", "type"])
        col_date   = getcol(["transfer_date", "date", "time"])
        col_status = getcol(["transfer_status", "status"])
        col_amount = getcol(["transfer_amount", "amount", "value"])

        missing = [n for n,c in {
            "transfer_type": col_type,
            "transfer_date": col_date,
            "transfer_status": col_status,
            "transfer_amount": col_amount
        }.items() if c is None]
        if missing:
            # Return empty if columns are not present
            return pd.Series(dtype=float)

        # Filter completed if requested
        if self.completed_only and col_status in d.columns:
            d = d[d[col_status].astype(str).str.contains("complete", case=False, na=False)]

        # Parse date (strip EDT/EST etc.)
        dt = pd.to_datetime(self._strip_tz(d[col_date]), errors="coerce", utc=False)
        d = d[~dt.isna()].copy()
        d["date"] = pd.to_datetime(dt.dt.date)

        # Amount
        amt = pd.to_numeric(d[col_amount], errors="coerce").fillna(0.0)

        # Map type to sign
        t = d[col_type].astype(str).str.lower().str.strip()
        # use keyword matching
        is_incoming  = t.str.contains("incoming") | t.str.contains("deposit") | t.str.contains("inbound")
        is_outgoing  = t.str.contains("outgoing") | t.str.contains("withdraw") | t.str.contains("outbound")

        cash_flow = np.where(is_incoming, -amt, np.where(is_outgoing, +amt, np.nan))
        # Drop unknown directions
        d["cash_flow"] = cash_flow
        d = d[~pd.isna(d["cash_flow"])].copy()

        # Aggregate per day
        s = d.groupby("date")["cash_flow"].sum().sort_index()
        # Ensure DateTimeIndex (day resolution)
        s.index = pd.to_datetime(s.index)
        return s
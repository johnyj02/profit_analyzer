import pandas as pd
from profit_analyzer.core.profit_calculator import ProfitCalculator

"""
Unit tests for the ProfitCalculator module.

───────────────────────────────
1. Time-Weighted Return (TWR)
───────────────────────────────
**Definition:**
Measures the compound rate of growth in a portfolio, eliminating the
distortion caused by the timing and size of cash flows. It isolates
the your performance from investor-driven deposits or withdrawals.

**Formula:**
If the portfolio is divided into N subperiods where external cash flows occur,
and R₁, R₂, …, Rₙ are the returns for each subperiod:

    TWR = (Π (1 + Rᵢ)) – 1

where  
    Rᵢ = (Vᵢ₊₁ – Vᵢ) / Vᵢ  
and Vᵢ = portfolio value at start of subperiod i.

**Intuition:**
TWR shows *how well the investments performed* regardless of
when money was added or withdrawn. It’s the industry standard for
evaluating professional managers.

─────────────────────────────────────
2. Money-Weighted Return (MWR / XIRR)
─────────────────────────────────────
**Definition:**
Measures the internal rate of return (IRR) that equates the present
value of all cash inflows and outflows — including the final portfolio value —
to zero. It incorporates both investment performance and the timing of cash flows.

**Formula:**
Find the rate r that satisfies:

    Σ [ CFₜ / (1 + r)^(Δt/365) ] = 0

where  
    CFₜ = cash flow at time t (negative for investment, positive for withdrawal),  
    Δt = number of days from the initial cash flow to time t.

**Intuition:**
MWR answers *“what was my personal return?”*, factoring in when and
how much capital was invested. It’s sensitive to cash flow timing.

"""

def test_time_weighted():
    """
    Test that time-weighted return (TWR) computation executes correctly.

    Creates a small synthetic equity curve with four daily values
    representing portfolio equity over time and ensures that the
    computed time-weighted return is a float.

    This test checks:
      - The function runs without raising errors.
      - The return value is a float (scalar percentage).

    Example equity curve:
        2023-01-01 -> 100
        2023-01-02 -> 110
        2023-01-03 -> 99
        2023-01-04 -> 120
    """
    eq = pd.Series([100, 110, 99, 120], index=pd.date_range('2023-01-01', periods=4, freq='D'))
    twr = ProfitCalculator('time_weighted').compute_time_weighted(eq)
    assert isinstance(twr, float)

def test_money_weighted():
    """
    Test that money-weighted return (MWR / XIRR) computation executes correctly.

    Uses a small set of dated cash flows representing investments and withdrawals,
    along with a terminal portfolio value, to confirm that the computed money-weighted
    return is a float.

    This test checks:
      - The function runs without raising numerical or convergence errors.
      - The return value is a float (scalar percentage).

    Example cash flows:
        2023-01-01 -> -1000 (initial investment)
        2023-02-01 -> +200  (intermediate cash inflow)
        2023-03-01 -> +200  (second inflow)
        Terminal value = 700
    """
    cf = pd.Series([-1000, 200, 200], index=pd.to_datetime(['2023-01-01','2023-02-01','2023-03-01']))
    mwr = ProfitCalculator('money_weighted').compute_money_weighted(cf, terminal_value=700)
    assert isinstance(mwr, float)

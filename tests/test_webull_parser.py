import pandas as pd
from profit_analyzer.core.webull_parser import WebullParser

def test_parse():
    df = pd.DataFrame({
        'Name':['X','X'],
        'Symbol':['AAA','AAA'],
        'Side':['Buy','Sell'],
        'Status':['Filled','Filled'],
        'Filled':[10,10],
        'Total Qty':[10,10],
        'Price':[10,12],
        'Avg Price':[10,12],
        'Time-in-Force':['GTC','GTC'],
        'Placed Time':['10/10/2025 10:10:10 EDT','10/11/2025 10:10:10 EDT'],
        'Filled Time':['10/10/2025 10:10:10 EDT','10/11/2025 10:10:10 EDT'],
    })
    out = WebullParser().parse(df)
    assert set(['datetime','symbol','qty','price','cash_flow']).issubset(out.columns)

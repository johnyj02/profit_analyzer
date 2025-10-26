import pandas as pd
from profit_analyzer.core.benchmark_comparator import BenchmarkComparator

class DummyPP:
    def history(self, symbol, start, end):
        idx = pd.date_range('2023-01-01', periods=3, freq='D')
        return pd.DataFrame({'close':[100, 101, 103]}, index=idx)

def test_bench():
    b = BenchmarkComparator('VTI')
    df = b.compare(DummyPP(), '2023-01-01', '2023-01-10')
    assert 'return_pct' in df.columns

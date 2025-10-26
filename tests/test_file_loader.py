import os, pandas as pd, tempfile
from profit_analyzer.core.file_loader import FileLoader

def test_file_loader(tmp_path):
    p = tmp_path / 'data.csv'
    pd.DataFrame({'a':[1,2]}).to_csv(p, index=False)
    fl = FileLoader(str(tmp_path), ['*.csv'])
    df = fl.load_files()
    assert len(df)==2

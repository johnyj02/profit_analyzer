import pandas as pd
import numpy as np
import logging
import inspect
import socket


logger = logging.getLogger(__name__)

def pretty_print(df: pd.DataFrame, rows: int = 5):
    """
    Nicely print DataFrames, Series, or other objects to stdout without truncation.
    """
    if isinstance(df, pd.DataFrame):
        with pd.option_context('display.max_rows', rows,
                               'display.max_columns', None,
                               'display.width', 140,
                               'display.max_colwidth', 200):
            print(df.head(rows).to_string(index=True))
    elif isinstance(df, pd.Series):
        with pd.option_context('display.max_rows', rows,
                               'display.width', 140,
                               'display.max_colwidth', 200):
            print(df.head(rows).to_string())
    else:
        print(repr(df))


def _get_variable_name(var) -> str:
    """
    Introspects the calling frame to get the variable name passed in.
    """
    frame = inspect.currentframe()
    try:
        outer = frame.f_back.f_back  # skip current and wrapper
        for name, val in outer.f_locals.items():
            if val is var:
                return name
    finally:
        del frame
    return "DataFrame"


def log_dataframe_details(df: pd.DataFrame,
                          name: str | None = None,
                          max_rows: int = 5) -> None:
    """
    Logs and pretty-prints details about a DataFrame, auto-detecting variable name if possible.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to inspect.
    name : str | None
        Optional name override; defaults to inferred variable name.
    logger : logging.Logger | None
        Logger instance; if None, root logger is used.
    max_rows : int
        Number of rows to show in preview.
    """
    
    name = name or _get_variable_name(df)

    top_line = f"\n{'=' * 40}  📊 {name}  {'=' * 40}\n"
    line = f"\n{'=' * 100}\n"

    print(top_line)

    if df is None:
        msg = f"{name}: None (no DataFrame provided)"
        logger.warning(msg)
        print(line)
        return

    if not isinstance(df, pd.DataFrame):
        msg = f"{name}: not a DataFrame (type={type(df)})"
        logger.warning(msg)
        logger.info(df)
        print(line)
        return

    n_rows, n_cols = df.shape
    col_summary = ", ".join(df.columns[:10]) + ("..." if len(df.columns) > 10 else "")

    logger.info(f"🔹 {name}: shape={df.shape}, columns=[{col_summary}]")
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Columns: [{col_summary}]")

    if n_rows > 0:
        null_counts = int(df.isna().sum().sum())
        logger.info(f"   total NaN cells={null_counts}")
        num_cols = df.select_dtypes(include=[np.number])
        if not num_cols.empty:
            desc = num_cols.describe().T[['mean', 'std', 'min', 'max']]
            logger.debug(f"Numeric summary for {name}:\n{desc}")

    logger.info(f"\nPreview (first {min(max_rows, n_rows)} rows):")
    logger.info(pretty_print(df, rows=max_rows))
    print(line)

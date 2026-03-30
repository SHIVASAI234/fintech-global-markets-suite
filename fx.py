import pandas as pd
from .utils import fetch_price_data
from .config import DEFAULT_START_DATE, DEFAULT_END_DATE


def get_fx_pair(pair, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Fetch FX pair price data using Yahoo Finance tickers.
    Example pairs:
        - 'EURUSD=X'
        - 'GBPUSD=X'
        - 'JPY=X'
    """
    return fetch_price_data(pair, start, end)


def compute_fx_returns(pairs, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Fetch multiple FX pairs and compute daily returns.
    Returns a DataFrame of returns for each pair.
    """
    data = {}

    for p in pairs:
        df = get_fx_pair(p, start, end)
        if "Close" in df.columns:
            data[p] = df["Close"].pct_change()
        else:
            data[p] = pd.Series(dtype=float)

    return pd.DataFrame(data).dropna()


def compute_fx_correlation(pairs, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Compute correlation matrix for a list of FX pairs.
    """
    returns = compute_fx_returns(pairs, start, end)
    return returns.corr()

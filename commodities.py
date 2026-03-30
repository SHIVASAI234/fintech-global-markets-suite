import pandas as pd
from .utils import fetch_price_data
from .config import DEFAULT_START_DATE, DEFAULT_END_DATE


def get_commodity_data(ticker, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Fetch commodity price data using Yahoo Finance tickers.
    Common examples:
        - 'GC=F'  (Gold)
        - 'CL=F'  (Crude Oil)
        - 'NG=F'  (Natural Gas)
        - 'SI=F'  (Silver)
        - 'HG=F'  (Copper)
    """
    return fetch_price_data(ticker, start, end)


def compute_commodity_returns(tickers, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Fetch multiple commodities and compute daily returns.
    Returns a DataFrame of returns for each commodity.
    """
    data = {}

    for t in tickers:
        df = get_commodity_data(t, start, end)
        if "Close" in df.columns:
            data[t] = df["Close"].pct_change()
        else:
            data[t] = pd.Series(dtype=float)

    return pd.DataFrame(data).dropna()


def compute_commodity_correlation(tickers, start=DEFAULT_START_DATE, end=DEFAULT_END_DATE):
    """
    Compute correlation matrix for a list of commodities.
    """
    returns = compute_commodity_returns(tickers, start, end)
    return returns.corr()

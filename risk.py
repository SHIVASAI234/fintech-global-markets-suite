import numpy as np
import pandas as pd


def compute_var(returns, confidence_level=0.95):
    """
    Compute Historical Value at Risk (VaR).

    returns: Series or DataFrame of returns
    confidence_level: e.g., 0.95 for 95% VaR
    """
    if isinstance(returns, pd.DataFrame):
        returns = returns.mean(axis=1)

    return returns.quantile(1 - confidence_level)


def compute_cvar(returns, confidence_level=0.95):
    """
    Compute Conditional Value at Risk (CVaR), also known as Expected Shortfall.
    """
    if isinstance(returns, pd.DataFrame):
        returns = returns.mean(axis=1)

    var = compute_var(returns, confidence_level)
    tail_losses = returns[returns <= var]

    if len(tail_losses) == 0:
        return np.nan

    return tail_losses.mean()


def correlation_matrix(returns):
    """
    Compute correlation matrix for a DataFrame of returns.
    """
    return returns.corr()


def stress_scenario_shock(returns, shock_factor=-0.05):
    """
    Apply a simple stress shock to returns.
    Example:
        shock_factor = -0.05 applies a -5% shock.
    """
    return returns + shock_factor


def rolling_volatility(returns, window=30):
    """
    Compute rolling volatility over a given window.
    """
    return returns.rolling(window).std() * np.sqrt(252)

import numpy as np
import pandas as pd


def normalize_weights(weights):
    """
    Normalize a list/array of weights so they sum to 1.
    """
    weights = np.array(weights, dtype=float)
    total = weights.sum()

    if total == 0:
        raise ValueError("Weights cannot sum to zero.")

    return weights / total


def compute_portfolio_stats(returns, weights, freq=252):
    """
    Compute annualized return and volatility for a portfolio.

    returns: DataFrame of asset returns
    weights: array-like of portfolio weights (must sum to 1)
    freq: trading days per year (default 252)
    """
    weights = normalize_weights(weights)

    mean_returns = returns.mean() * freq
    cov_matrix = returns.cov() * freq

    portfolio_return = float(np.dot(weights, mean_returns))
    portfolio_volatility = float(np.sqrt(weights.T @ cov_matrix @ weights))

    return {
        "annual_return": portfolio_return,
        "annual_volatility": portfolio_volatility,
    }


def compute_portfolio_returns(price_data):
    """
    Convert price data into daily returns for portfolio calculations.
    """
    return price_data.pct_change().dropna()


def simulate_random_portfolios(returns, num_portfolios=5000, freq=252):
    """
    Generate random portfolios for exploratory analysis or efficient frontier prototypes.
    """
    num_assets = returns.shape[1]
    results = []

    for _ in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights = normalize_weights(weights)

        stats = compute_portfolio_stats(returns, weights, freq)
        results.append({
            "return": stats["annual_return"],
            "volatility": stats["annual_volatility"],
            "weights": weights
        })

    return results

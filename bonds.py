import pandas as pd
import numpy as np

def build_yield_curve(maturities, yields):
    """
    Construct a simple yield curve DataFrame.

    maturities: list of maturities in years (e.g., [0.25, 1, 2, 5, 10])
    yields: list of yields in decimal form (e.g., [0.03, 0.032, 0.035, 0.04, 0.045])
    """
    curve = pd.DataFrame({
        "maturity": maturities,
        "yield": yields
    })
    return curve.sort_values("maturity").reset_index(drop=True)


def macaulay_duration(cash_flows, times, y):
    """
    Calculate Macaulay Duration.

    cash_flows: list of cash flows
    times: list of time periods in years
    y: yield (annual, decimal)
    """
    discounted = [cf / (1 + y)**t for cf, t in zip(cash_flows, times)]
    pv = sum(discounted)

    if pv == 0:
        return np.nan

    weighted = [t * d for t, d in zip(times, discounted)]
    return sum(weighted) / pv


def modified_duration(macaulay_dur, y):
    """
    Modified Duration = Macaulay Duration / (1 + yield)
    """
    return macaulay_dur / (1 + y)


def convexity(cash_flows, times, y):
    """
    Approximate convexity of a bond.

    cash_flows: list of CFs
    times: list of time periods in years
    y: yield (annual, decimal)
    """
    numerator = sum([cf * t * (t + 1) / (1 + y)**(t + 2) for cf, t in zip(cash_flows, times)])
    denominator = sum([cf / (1 + y)**t for cf, t in zip(cash_flows, times)])

    if denominator == 0:
        return np.nan

    return numerator / denominator

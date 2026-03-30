import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src import equities
from src import fx
from src import commodities
from src import portfolio
from src import risk
from src import utils
from src.config import (
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    DEFAULT_EQUITY_TICKERS,
    DEFAULT_FX_PAIRS,
    DEFAULT_COMMODITY_TICKERS,
    TRADING_DAYS,
)


st.set_page_config(
    page_title="FinTech Global Markets Suite",
    layout="wide",
)


# -----------------------------
# Sidebar configuration
# -----------------------------
st.sidebar.title("FinTech Global Markets Suite")

st.sidebar.markdown("### Date Range")
start_date = st.sidebar.date_input("Start date", pd.to_datetime(DEFAULT_START_DATE))
end_date = st.sidebar.date_input("End date", pd.to_datetime("today"))

if end_date <= start_date:
    st.sidebar.error("End date must be after start date.")


st.sidebar.markdown("---")
st.sidebar.markdown("### Asset Selection")

equity_tickers = st.sidebar.multiselect(
    "Equities",
    DEFAULT_EQUITY_TICKERS,
    default=DEFAULT_EQUITY_TICKERS,
)

fx_pairs = st.sidebar.multiselect(
    "FX Pairs",
    DEFAULT_FX_PAIRS,
    default=DEFAULT_FX_PAIRS,
)

commodity_tickers = st.sidebar.multiselect(
    "Commodities",
    DEFAULT_COMMODITY_TICKERS,
    default=DEFAULT_COMMODITY_TICKERS,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Portfolio Weights")

st.sidebar.caption("Weights should roughly sum to 1. They will be normalized in calculations.")

all_assets = equity_tickers + fx_pairs + commodity_tickers
weights_input = {}

for asset in all_assets:
    weights_input[asset] = st.sidebar.number_input(
        f"Weight: {asset}",
        min_value=0.0,
        max_value=1.0,
        value=1.0 / max(len(all_assets), 1),
        step=0.01,
    )


# -----------------------------
# Helper to fetch combined price data
# -----------------------------
@st.cache_data(show_spinner=True)
def fetch_all_price_data(equities_list, fx_list, commodities_list, start, end):
    frames = []

    for t in equities_list:
        df = utils.fetch_price_data(t, start=start, end=end)
        if not df.empty and "Close" in df.columns:
            frames.append(df[["Close"]].rename(columns={"Close": t}))

    for p in fx_list:
        df = fx.get_fx_pair(p, start=start, end=end)
        if not df.empty and "Close" in df.columns:
            frames.append(df[["Close"]].rename(columns={"Close": p}))

    for c in commodities_list:
        df = commodities.get_commodity_data(c, start=start, end=end)
        if not df.empty and "Close" in df.columns:
            frames.append(df[["Close"]].rename(columns={"Close": c}))

    if not frames:
        return pd.DataFrame()

    prices = pd.concat(frames, axis=1).dropna()
    return prices


# -----------------------------
# Main layout
# -----------------------------
st.title("FinTech Global Markets Suite")
st.markdown(
    """
A modular multi‑asset analytics suite for **equities**, **FX**, **commodities**, **portfolio construction**, and **risk**.
Built for asset‑management and global‑markets workflows.
"""
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Equities", "FX & Commodities", "Portfolio", "Risk"]
)


# -----------------------------
# Overview tab
# -----------------------------
with tab1:
    st.subheader("Market Overview")

    prices = fetch_all_price_data(
        equity_tickers,
        fx_pairs,
        commodity_tickers,
        start_date,
        end_date,
    )

    if prices.empty:
        st.warning("No price data available for the selected configuration.")
    else:
        st.markdown("### Price History")
        fig = px.line(prices, x=prices.index, y=prices.columns)
        fig.update_layout(xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Daily Returns (Head)")
        returns = prices.pct_change().dropna()
        st.dataframe(returns.head())


# -----------------------------
# Equities tab
# -----------------------------
with tab2:
    st.subheader("Equity Analytics")

    if not equity_tickers:
        st.info("Select at least one equity in the sidebar.")
    else:
        eq_ticker = st.selectbox("Select equity", equity_tickers)

        eq_data = utils.fetch_price_data(eq_ticker, start=str(start_date), end=str(end_date))
        if eq_data.empty or "Close" not in eq_data.columns:
            st.warning("No data available for this equity.")
        else:
            prices_eq = eq_data["Close"]

            st.markdown("### Price History")
            fig_eq = px.line(prices_eq, x=prices_eq.index, y=prices_eq.values, labels={"x": "Date", "y": "Price"})
            st.plotly_chart(fig_eq, use_container_width=True)

            st.markdown("### Equity Metrics")
            metrics = equities.compute_equity_metrics(prices_eq, freq=TRADING_DAYS)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Annual Return", f"{metrics['annual_return']:.2%}")
            col2.metric("Annual Volatility", f"{metrics['annual_volatility']:.2%}")
            col3.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            col4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")


# -----------------------------
# FX & Commodities tab
# -----------------------------
with tab3:
    st.subheader("FX & Commodities Analytics")

    col_fx, col_cmd = st.columns(2)

    # FX
    with col_fx:
        st.markdown("### FX Correlation")
        if len(fx_pairs) < 2:
            st.info("Select at least two FX pairs in the sidebar to see correlations.")
        else:
            fx_corr = fx.compute_fx_correlation(fx_pairs, start=str(start_date), end=str(end_date))
            st.dataframe(fx_corr.style.background_gradient(cmap="RdBu_r"))

    # Commodities
    with col_cmd:
        st.markdown("### Commodity Correlation")
        if len(commodity_tickers) < 2:
            st.info("Select at least two commodities in the sidebar to see correlations.")
        else:
            cmd_corr = commodities.compute_commodity_correlation(
                commodity_tickers,
                start=str(start_date),
                end=str(end_date),
            )
            st.dataframe(cmd_corr.style.background_gradient(cmap="RdBu_r"))


# -----------------------------
# Portfolio tab
# -----------------------------
with tab4:
    st.subheader("Portfolio Analytics")

    if not all_assets:
        st.info("Select at least one asset in the sidebar.")
    else:
        prices_all = fetch_all_price_data(
            equity_tickers,
            fx_pairs,
            commodity_tickers,
            start_date,
            end_date,
        )

        if prices_all.empty:
            st.warning("No price data available for the selected assets.")
        else:
            returns_all = portfolio.compute_portfolio_returns(prices_all)

            # Build weights vector in correct order
            weights = [weights_input[a] for a in prices_all.columns]

            stats = portfolio.compute_portfolio_stats(returns_all, weights, freq=TRADING_DAYS)

            st.markdown("### Portfolio Metrics")
            c1, c2 = st.columns(2)
            c1.metric("Annual Return", f"{stats['annual_return']:.2%}")
            c2.metric("Annual Volatility", f"{stats['annual_volatility']:.2%}")

            st.markdown("### Random Portfolio Simulation (Efficient Frontier Prototype)")
            num_portfolios = st.slider("Number of random portfolios", 100, 5000, 1000, step=100)
            sim_results = portfolio.simulate_random_portfolios(returns_all, num_portfolios=num_portfolios, freq=TRADING_DAYS)

            sim_df = pd.DataFrame(
                {
                    "return": [r["return"] for r in sim_results],
                    "volatility": [r["volatility"] for r in sim_results],
                }
            )

            fig_pf = px.scatter(
                sim_df,
                x="volatility",
                y="return",
                labels={"volatility": "Volatility", "return": "Return"},
                title="Random Portfolios (Return vs Volatility)",
            )
            st.plotly_chart(fig_pf, use_container_width=True)


# -----------------------------
# Risk tab
# -----------------------------
with tab5:
    st.subheader("Risk Analytics")

    prices_all = fetch_all_price_data(
        equity_tickers,
        fx_pairs,
        commodity_tickers,
        start_date,
        end_date,
    )

    if prices_all.empty:
        st.warning("No price data available for the selected assets.")
    else:
        returns_all = prices_all.pct_change().dropna()

        st.markdown("### Correlation Matrix")
        corr = risk.correlation_matrix(returns_all)
        st.dataframe(corr.style.background_gradient(cmap="RdBu_r"))

        st.markdown("### Portfolio Risk (VaR & CVaR)")
        weights = [weights_input[a] for a in prices_all.columns]
        weights = portfolio.normalize_weights(weights)

        # Portfolio returns as weighted sum
        port_ret_series = (returns_all * weights).sum(axis=1)

        confidence = st.slider("Confidence Level", 0.90, 0.99, 0.95, step=0.01)
        var = risk.compute_var(port_ret_series, confidence_level=confidence)
        cvar = risk.compute_cvar(port_ret_series, confidence_level=confidence)

        c1, c2 = st.columns(2)
        c1.metric(f"{int(confidence*100)}% Historical VaR", f"{var:.2%}")
        c2.metric(f"{int(confidence*100)}% Historical CVaR", f"{cvar:.2%}")

        st.markdown("### Rolling Volatility")
        window = st.slider("Rolling window (days)", 10, 120, 30, step=5)
        rolling_vol = risk.rolling_volatility(port_ret_series, window=window)

        fig_rv = px.line(rolling_vol, x=rolling_vol.index, y=rolling_vol.values,
                         labels={"x": "Date", "y": "Rolling Volatility"},
                         title="Rolling Portfolio Volatility")
        st.plotly_chart(fig_rv, use_container_width=True)

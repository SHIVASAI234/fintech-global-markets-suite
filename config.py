from datetime import datetime

# Default date range for all analytics modules
DEFAULT_START_DATE = "2015-01-01"
DEFAULT_END_DATE = None   # None = fetch up to the latest available date

# Trading days per year (used for annualization)
TRADING_DAYS = 252

# Common tickers for quick testing or dashboards
DEFAULT_EQUITY_TICKERS = ["AAPL", "MSFT", "GOOGL"]
DEFAULT_FX_PAIRS = ["EURUSD=X", "GBPUSD=X", "JPY=X"]
DEFAULT_COMMODITY_TICKERS = ["GC=F", "CL=F", "SI=F"]

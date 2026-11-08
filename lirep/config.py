"""Configuration for the Li (2025) replication.

Li, S. (2025). "Momentum, volume and investor sentiment study for U.S.
technology sector stocks - A hidden Markov model based principal component
analysis." PLOS ONE 20(9): e0331658. doi:10.1371/journal.pone.0331658

Section 4.1: ten years of weekly Yahoo Finance data, 2015-01-01 to 2024-12-31.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"
DEFAULT_RESULTS_DIR = PROJECT_DIR / "results"

START_DATE = "2015-01-01"
END_DATE = "2024-12-31"  # yfinance treats `end` as exclusive

# The seven large tech stocks in the paper.
TECH_TICKERS = ["AMZN", "AAPL", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]

# PCA input sets (--pca-set). Each maps a series name to its yfinance ticker.
#
# "li" (default): the 12 market/macro series of Li's Table 1 (p. 10), with
#   5 principal components ("The PCA step involves construct five principal
#   components", Section 4.2, p. 10).
# "original": the September 2026 replication, 7 series, keeping enough
#   components for >= 75% of the variance (at most 5), which gives 4.
PCA_SETS = {
    "li": {
        "series": {
            "NASDAQ": "^IXIC",            # Nasdaq Index
            "SP500": "^GSPC",             # S&P 500 Index
            "RATE_13W": "^IRX",           # 13 Wk Treasury
            "RATE_5Y": "^FVX",            # 5 Yr Treasury
            "RATE_10Y": "^TNX",           # 10 Yr Treasury
            "RATE_30Y": "^TYX",           # 30 Yr Treasury
            "CRUDE_OIL": "CL=F",          # Crude Oil (WTI front month)
            "GOLD": "GC=F",               # Gold (front month)
            "NATURAL_GAS": "NG=F",        # Natural Gas (front month)
            "EUR_USD": "EURUSD=X",        # EUR/USD
            "JPY_USD": "JPYUSD=X",        # JPY/USD (USD per yen)
            "AUD_USD": "AUDUSD=X",        # AUD/USD
        },
        "n_components": 5,
    },
    "original": {
        "series": {
            "SP500": "^GSPC",
            "NASDAQ": "^IXIC",
            "RATE_10Y": "^TNX",
            "RATE_13W": "^IRX",
            "GOLD": "GC=F",
            "CRUDE_OIL": "CL=F",
            "USD_INDEX": "DX-Y.NYB",
        },
        "variance_target": 0.75,
        "max_components": 5,
    },
}
DEFAULT_PCA_SET = "li"
# Rate series are differenced; all others enter as weekly percentage returns.
RATE_SERIES = {"RATE_13W", "RATE_5Y", "RATE_10Y", "RATE_30Y"}

# Market control in the regressions (S&P 500 weekly return).
BENCHMARK_TICKER = "^GSPC"

# HMM: 4 hidden states (the paper's AIC/BIC-based choice), fitted on the
# full sample as in the paper.
HMM_N_STATES = 4
HMM_N_ITER = 1000
HMM_CANDIDATE_STATES = (2, 3, 4, 5, 6)
SEED = 42

# Momentum: one-lag autocovariance of weekly return "in the past month
# (4 weeks)" (Section 4.3, p. 11; no equation is given).
#   "li": window = weeks t-4..t-1 (excludes week t). This reproduces Li's
#         Table 3 correlations and Table 4 all-weeks momentum coefficients.
#   "september": window = weeks t-3..t (includes week t), as in the
#         September 2026 code.
# --momentum defaults to "september" with --pca-set original (so that setup
# reproduces the September results) and to "li" otherwise.
MOMENTUM_LOOKBACK_WEEKS = 4
MOMENTUM_DEFINITIONS = ("li", "september")

# Eq. 17 is skipped for a state with fewer weeks than this.
MIN_OBS_PER_STATE = 6

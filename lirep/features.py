"""Weekly stock indicators (return, volume, price range, momentum) and the
macro-series returns that feed the PCA (Section 4.1, Table 1)."""

import numpy as np
import pandas as pd

from .config import MOMENTUM_LOOKBACK_WEEKS, RATE_SERIES


def weekly_return(df):
    return df["Close"].pct_change()


def price_range(df):
    return (df["High"] - df["Low"]) / df["Close"]


def momentum(returns, definition="li", lookback=MOMENTUM_LOOKBACK_WEEKS):
    """One-lag autocovariance of weekly return over a rolling `lookback`-week
    window ("autocovariance with one lag ... in the past month (4 weeks)").

    definition="li": the window ends at week t-1 (the past 4 weeks).
    definition="september": the window ends at week t (September 2026 code).
    """
    def _autocov_lag1(x):
        if len(x) < 2 or np.all(np.isnan(x)):
            return np.nan
        x = x - np.nanmean(x)
        return np.nanmean(x[1:] * x[:-1])

    mom = returns.rolling(window=lookback).apply(_autocov_lag1, raw=True)
    if definition == "li":
        return mom.shift(1)
    if definition == "september":
        return mom
    raise ValueError(f"unknown momentum definition: {definition}")


def build_stock_features(df, momentum_definition="li"):
    out = pd.DataFrame(index=df.index)
    out["return"] = weekly_return(df)
    out["volume"] = df["Volume"]
    out["price_range"] = price_range(df)
    out["momentum"] = momentum(out["return"], momentum_definition)
    return out.dropna()


def build_macro_returns(macro_data):
    """Wide table of weekly macro returns. Rate series are differenced, since
    the percentage change of a yield near zero is unstable."""
    series = {}
    for name, df in macro_data.items():
        if name in RATE_SERIES:
            series[name] = df["Close"].diff()
        else:
            series[name] = df["Close"].pct_change()
    return pd.DataFrame(series).dropna()

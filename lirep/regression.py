"""Section 4.3, OLS (statsmodels):

  Eq. 16: return_t = a + b1*SP500_t + b2*momentum_t + b3*volume_t
                       + sum_k c_k * 1[state_t = k] + e_t
  Eq. 17: the same regression without dummies, run within each HMM state,
          and on all weeks (Li's Table 4, second row per stock).
"""

import pandas as pd
import statsmodels.api as sm

from .config import MIN_OBS_PER_STATE

REGRESSORS = ["sp500_return", "momentum", "volume"]


def build_regression_frame(stock_features, states, benchmark_returns):
    df = stock_features.join(states, how="inner")
    df = df.join(benchmark_returns.rename("sp500_return"), how="inner")
    return df.dropna()


def run_eq16(df):
    dummies = pd.get_dummies(df["state"], prefix="state", drop_first=True)
    X = sm.add_constant(pd.concat([df[REGRESSORS], dummies], axis=1)).astype(float)
    return sm.OLS(df["return"].astype(float), X, missing="drop").fit()


def state_dummies_ftest(model):
    """Joint F-test that all Eq. 16 state dummies are zero (does not depend
    on which state is the omitted base)."""
    cols = [c for c in model.params.index if c.startswith("state_")]
    f = model.f_test(", ".join(f"{c} = 0" for c in cols))
    return {"F": float(f.fvalue), "df_num": int(f.df_num), "df_denom": int(f.df_denom),
            "pvalue": float(f.pvalue)}


def run_eq17_all_weeks(df):
    """Eq. 17 on all weeks (no state dummies): the second row per stock in
    Li's Table 4, used in Section 4.3.3 to compare with Eq. 16."""
    X = sm.add_constant(df[REGRESSORS]).astype(float)
    return sm.OLS(df["return"].astype(float), X, missing="drop").fit()


def run_eq17(df):
    results = {}
    for state, sub in df.groupby("state"):
        if len(sub) < MIN_OBS_PER_STATE:
            continue
        X = sm.add_constant(sub[REGRESSORS]).astype(float)
        results[state] = sm.OLS(sub["return"].astype(float), X, missing="drop").fit()
    return results


def tidy(model, ticker, label, state=None):
    return pd.DataFrame({
        "ticker": ticker, "model": label, "state": state,
        "term": model.params.index,
        "coef": model.params.values, "se": model.bse.values,
        "pvalue": model.pvalues.values, "nobs": int(model.nobs),
        "r2": model.rsquared, "r2_adj": model.rsquared_adj,
    })

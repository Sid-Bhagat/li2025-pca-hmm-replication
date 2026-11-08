"""Sections 3.2-3.3: a Gaussian HMM per stock on the PCA components plus the
stock's own return, volume and price range. The decoded states are the
paper's investor-sentiment regimes. Fitted on the full 2015-2024 sample, as
in the paper."""

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

from .config import HMM_N_STATES, HMM_N_ITER, HMM_CANDIDATE_STATES, SEED


def _hmm_inputs(stock_features, pca_components):
    merged = stock_features.join(pca_components, how="inner").dropna()
    # Momentum is used in the regressions, not as an HMM input.
    feature_cols = ["return", "volume", "price_range"] + list(pca_components.columns)
    return merged, merged[feature_cols].values


def fit_hmm_for_stock(stock_features, pca_components, seed=SEED):
    """Returns (states Series, fitted model, log-likelihood of the fit)."""
    merged, X = _hmm_inputs(stock_features, pca_components)

    # Standardize: returns are ~1e-2 and volume ~1e7.
    X_std = X.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_norm = (X - X.mean(axis=0)) / X_std

    model = GaussianHMM(
        n_components=HMM_N_STATES, covariance_type="diag",
        n_iter=HMM_N_ITER, random_state=seed,
    )
    model.fit(X_norm)
    raw_states = model.predict(X_norm)

    # Deterministic labels: state 0 = lowest mean weekly return, state 3 =
    # highest. The fitted parameters are permuted, so the model and its
    # decoded states use the same labels. The fit itself is unchanged.
    means = [merged["return"].values[raw_states == s].mean() for s in range(HMM_N_STATES)]
    order = np.argsort(means, kind="stable")
    model.startprob_ = model.startprob_[order]
    model.transmat_ = model.transmat_[np.ix_(order, order)]
    model.means_ = model.means_[order]
    model._covars_ = model._covars_[order]
    states = model.predict(X_norm)
    assert np.array_equal(states, np.argsort(order)[raw_states]), "relabelling changed the decoding"

    return pd.Series(states, index=merged.index, name="state"), model, model.score(X_norm)


def select_n_states(stock_features, pca_components, seed=SEED,
                    candidate_states=HMM_CANDIDATE_STATES):
    """AIC/BIC for each candidate state count (the paper's selection step)."""
    merged, X = _hmm_inputs(stock_features, pca_components)
    X_norm = (X - X.mean(axis=0)) / X.std(axis=0)

    rows = []
    for k in candidate_states:
        model = GaussianHMM(
            n_components=k, covariance_type="diag",
            n_iter=HMM_N_ITER, random_state=seed,
        )
        model.fit(X_norm)
        logL = model.score(X_norm)
        n_params = k * (k - 1) + k * X_norm.shape[1] * 2  # transitions + (mean, var) per state
        n_obs = X_norm.shape[0]
        rows.append({
            "n_states": k, "logL": logL,
            "AIC": -2 * logL + 2 * n_params,
            "BIC": -2 * logL + n_params * np.log(n_obs),
        })
    return pd.DataFrame(rows)

"""Section 3.1: standardize the macro series and run PCA.

Li's setup keeps a fixed 5 components (Section 4.2). The September setup
keeps enough components for >= a variance target (at most a maximum)."""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def run_pca(macro_returns, n_components=None, variance_target=None, max_components=5):
    """Pass either n_components (fixed) or variance_target (+ max_components).
    Returns (component scores, explained-variance table, n_keep)."""
    X = StandardScaler().fit_transform(macro_returns.values)

    pca_full = PCA(n_components=min(max(max_components, n_components or 0), X.shape[1]))
    pca_full.fit(X)
    cum_var = np.cumsum(pca_full.explained_variance_ratio_)
    if n_components is not None:
        n_keep = n_components
    else:
        n_keep = int(np.searchsorted(cum_var, variance_target) + 1)
        n_keep = min(n_keep, max_components)

    pca = PCA(n_components=n_keep)
    scores = pca.fit_transform(X)
    components = pd.DataFrame(
        scores, index=macro_returns.index,
        columns=[f"PC{i+1}" for i in range(n_keep)],
    )

    variance = pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(len(cum_var))],
        "explained_variance_ratio": pca_full.explained_variance_ratio_,
        "cumulative": cum_var,
        "retained": [i < n_keep for i in range(len(cum_var))],
    })
    loadings = pd.DataFrame(pca.components_.T, index=macro_returns.columns,
                            columns=components.columns).rename_axis("series")
    print(f"PCA: {X.shape[1]} series, kept {n_keep} components explaining "
          f"{cum_var[n_keep-1]*100:.1f}% of variance")
    return components, variance, n_keep, loadings

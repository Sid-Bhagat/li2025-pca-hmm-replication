"""Li (2025) PCA-HMM replication: end-to-end entry point.

    python run.py                          # cache in ./data, results in ./results
    python run.py --pca-set original --data-dir old/data --results-dir path/to/output

Missing tickers in the data directory are downloaded from Yahoo Finance.
"""

import os

# One thread for BLAS/OpenMP: multithreaded sums change the last bits of the
# HMM log-likelihoods between runs. Must be set before numpy is imported.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import argparse
import json
import platform
import random
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from lirep.config import (
    TECH_TICKERS, PCA_SETS, DEFAULT_PCA_SET, MOMENTUM_DEFINITIONS,
    BENCHMARK_TICKER, HMM_N_STATES, SEED, DEFAULT_DATA_DIR, DEFAULT_RESULTS_DIR,
    PROJECT_DIR,
)
from lirep.data import load_all_data
from lirep.features import build_stock_features, build_macro_returns, weekly_return
from lirep.pca_step import run_pca
from lirep.hmm_step import fit_hmm_for_stock, select_n_states
from lirep.regression import (
    build_regression_frame, run_eq16, run_eq17, run_eq17_all_weeks, tidy,
    state_dummies_ftest,
)
from lirep.plots import plot_price_trend, plot_state_boxplots
from lirep.io_utils import save_csv, save_text

warnings.filterwarnings("ignore")


def _portable_path(path):
    """Path relative to the project folder, so run_info.json holds no
    machine-specific absolute paths; outside paths keep only their name."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(PROJECT_DIR))
    except ValueError:
        return f"<outside project>/{p.name}"


def state_summary(ticker, model, reg_df):
    g = reg_df.groupby("state")
    out = pd.DataFrame({
        "ticker": ticker,
        "n_weeks": g.size(),
        "share_of_weeks": g.size() / len(reg_df),
        "mean_return": g["return"].mean(),
        "std_return": g["return"].std(),
        "mean_momentum": g["momentum"].mean(),
        "mean_volume": g["volume"].mean(),
        "mean_price_range": g["price_range"].mean(),
        "mean_sp500_return": g["sp500_return"].mean(),
        "expected_duration_weeks": [1 / (1 - model.transmat_[s, s]) for s in g.size().index],
    })
    return out.rename_axis("state").reset_index()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR,
                    help="folder with the per-ticker weekly CSV cache (default: ./data)")
    ap.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR,
                    help="output folder (default: ./results)")
    ap.add_argument("--pca-set", choices=sorted(PCA_SETS), default=DEFAULT_PCA_SET,
                    help="PCA inputs: 'li' = Li's 12 Table 1 series, 5 PCs (default); "
                         "'original' = the September 2026 7 series, 75%% rule (4 PCs)")
    ap.add_argument("--momentum", choices=MOMENTUM_DEFINITIONS, default=None,
                    help="'li' = window t-4..t-1; 'september' = window t-3..t "
                         "(default: 'september' with --pca-set original, else 'li')")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    if args.momentum is None:
        args.momentum = "september" if args.pca_set == "original" else "li"
    pca_cfg = PCA_SETS[args.pca_set]
    macro_tickers = pca_cfg["series"]

    random.seed(args.seed)
    np.random.seed(args.seed)
    out = args.results_dir
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Data: {args.data_dir} | PCA set: {args.pca_set} | momentum: {args.momentum} ===")
    raw = load_all_data(args.data_dir, macro_tickers.values())

    print("=== PCA on macro series ===")
    macro = build_macro_returns({name: raw[t] for name, t in macro_tickers.items()})
    pcs, variance, n_pcs, loadings = run_pca(
        macro, n_components=pca_cfg.get("n_components"),
        variance_target=pca_cfg.get("variance_target"),
        max_components=pca_cfg.get("max_components", 5),
    )
    save_csv(variance, out / "pca_explained_variance.csv", index=False)
    save_csv(loadings, out / "pca_loadings.csv")

    benchmark = weekly_return(raw[BENCHMARK_TICKER]).rename("return")

    eq16_rows, eq17_rows, eq17_all_rows, ftest_rows, desc_rows = [], [], [], [], []
    state_rows, fit_rows, sel_rows, state_series = [], [], [], []
    for ticker in TECH_TICKERS:
        print(f"=== {ticker} ===")
        feats = build_stock_features(raw[ticker], args.momentum)

        sel = select_n_states(feats, pcs, seed=args.seed)
        sel.insert(0, "ticker", ticker)
        sel_rows.append(sel)

        states, model, logL = fit_hmm_for_stock(feats, pcs, seed=args.seed)
        state_series.append(states.rename(ticker))

        plot_price_trend(ticker, raw[ticker]["Close"], states, fig_dir)
        plot_state_boxplots(ticker, feats.join(states, how="inner"), fig_dir)

        reg_df = build_regression_frame(feats, states, benchmark)
        m16 = run_eq16(reg_df)
        m17 = run_eq17(reg_df)
        eq16_rows.append(tidy(m16, ticker, "eq16"))
        ftest_rows.append({"ticker": ticker, **state_dummies_ftest(m16)})
        # Li Table 2 analogue: weekly return, momentum and volume on the regression sample.
        for var in ["return", "momentum", "volume"] + (["sp500_return"] if ticker == TECH_TICKERS[0] else []):
            s = reg_df[var]
            desc_rows.append({"series": "S&P 500" if var == "sp500_return" else ticker,
                              "variable": "return" if var == "sp500_return" else var,
                              "mean": s.mean(), "std": s.std(), "max": s.max(),
                              "min": s.min(), "n": len(s)})
        eq17_all_rows.append(tidy(run_eq17_all_weeks(reg_df), ticker, "eq17_all"))
        for s, m in m17.items():
            eq17_rows.append(tidy(m, ticker, "eq17", state=s))

        state_rows.append(state_summary(ticker, model, reg_df))
        fit_rows.append({
            "ticker": ticker, "n_states": HMM_N_STATES, "n_weeks": len(states),
            "logL": logL,
            "converged": bool(model.monitor_.converged), "em_iterations": model.monitor_.iter,
        })

    save_csv(pd.concat(eq16_rows, ignore_index=True), out / "eq16.csv", index=False)
    save_csv(pd.concat(eq17_rows, ignore_index=True), out / "eq17.csv", index=False)
    save_csv(pd.concat(eq17_all_rows, ignore_index=True), out / "eq17_all_weeks.csv", index=False)
    save_csv(pd.DataFrame(ftest_rows), out / "eq16_state_dummies_ftest.csv", index=False)
    save_csv(pd.DataFrame(desc_rows), out / "descriptive_stats.csv", index=False)
    save_csv(pd.concat(state_rows, ignore_index=True), out / "hmm_states.csv", index=False)
    save_csv(pd.DataFrame(fit_rows), out / "hmm_fit.csv", index=False)
    save_csv(pd.concat(sel_rows, ignore_index=True), out / "hmm_state_selection.csv", index=False)
    save_csv(pd.concat(state_series, axis=1).rename_axis("date"), out / "hmm_states_weekly.csv")

    import hmmlearn, matplotlib, sklearn, statsmodels, yfinance
    info = {
        "data_dir": _portable_path(args.data_dir),
        "seed": args.seed,
        "pca_set": args.pca_set,
        "pca_series": macro_tickers,
        "momentum": args.momentum,
        "n_pcs": n_pcs,
        "pca_cumulative_variance": float(variance["cumulative"].iloc[n_pcs - 1]),
        "weeks_per_ticker": {t: int(len(raw[t])) for t in raw},
        "first_week": str(min(df.index.min() for df in raw.values()).date()),
        "last_week": str(max(df.index.max() for df in raw.values()).date()),
        "python": platform.python_version(),
        "versions": {m.__name__: m.__version__ for m in
                     (np, pd, hmmlearn, sklearn, statsmodels, yfinance, matplotlib)},
    }
    save_text(json.dumps(info, indent=2) + "\n", out / "run_info.json")
    print(f"Done. Results in {out}")


if __name__ == "__main__":
    main()

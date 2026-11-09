# Li (2025) PCA-HMM replication

Replication of:

> Li, S. (2025). Momentum, volume and investor sentiment study for U.S. technology sector stocks—A hidden Markov model based principal component analysis. *PLOS ONE* 20(9): e0331658. doi:10.1371/journal.pone.0331658

The paper has no public code, so this is a from-scratch implementation of its Sections 3–4. It replicates the analysis of the seven large tech stocks:

1. **PCA** on the standardized weekly market/macro series of Li's Table 1, keeping 5 components.
2. A **4-state Gaussian HMM** for each stock, fitted on the full 2015–2024 sample (as in the paper). Its inputs are the PCs plus the stock's weekly return, volume and price range (High − Low) / Close. States are labelled by mean weekly return (0 = lowest).
3. **Eq. 16**: OLS of weekly return on the S&P 500 return, momentum, volume and state dummies.
4. **Eq. 17**: the same OLS without dummies, within each state and on all weeks.

Momentum is the lag-1 autocovariance of weekly returns over the past 4 weeks (t−4..t−1), following Section 4.3, p. 11. `COMPARISON.md` explains why the window excludes week t.

Not included: the sub-sector stocks (Table 5), the risk-aversion parameter γ, and Fig 4.
`COMPARISON.md` compares every finding with the paper and documents the reproducibility checks.

## Data

Yahoo Finance via `yfinance`, **weekly** bars (`interval="1wk"`, auto-adjusted), from **2015-01-01 to 2024-12-31**. `end` is exclusive, so the last bar is the week of 2024-12-26.
Each series has 522 weeks. The regressions use 517 (Li reports 518).

Stocks: AMZN, AAPL, GOOGL, META, MSFT, NVDA, TSLA. The regressions' market control is the S&P 500 weekly return (^GSPC).

PCA inputs (`--pca-set li`, the default) are the 12 series of Li's Table 1 (p. 10). Each has a direct yfinance equivalent:

| Li Table 1 series | yfinance ticker | Note |
|---|---|---|
| Nasdaq Index | `^IXIC` | Nasdaq Composite |
| S&P 500 Index | `^GSPC` | |
| 13 Wk Treasury Note Index | `^IRX` | 13-week T-bill yield index; differenced |
| 5 Yr Treasury Note Index | `^FVX` | 5-year yield index; differenced |
| 10 Yr Treasury Note Index | `^TNX` | 10-year yield index; differenced |
| 30 Yr Treasury Note Index | `^TYX` | 30-year yield index; differenced |
| Crude Oil | `CL=F` | WTI continuous front-month future |
| Gold | `GC=F` | continuous front-month future |
| Natural Gas | `NG=F` | continuous front-month future |
| EUR/USD | `EURUSD=X` | USD per euro |
| JPY/USD | `JPYUSD=X` | USD per yen, as Li writes it (`JPY=X` is the inverse quote) |
| AUD/USD | `AUDUSD=X` | USD per Australian dollar |

The four rate series enter as first differences, and the others as weekly percentage returns. All are then standardized.

The first run downloads every series into `data/` (one CSV per ticker), and later runs reuse that cache. The committed results come from a download on 2026-11-08. Yahoo revises its history: our September 2026 and November 2026 downloads differ for gold futures (see `COMPARISON.md`).

### The September 2026 setup (`--pca-set original`)

The first version of this replication (September 2026) used 7 PCA series: ^GSPC, ^IXIC, ^TNX, ^IRX, GC=F, CL=F and the US Dollar Index DX-Y.NYB. It kept enough PCs for 75% of the variance (4 PCs), and its momentum window included week t (t−3..t).

`--pca-set original` reproduces that setup, using September momentum by default. It deviates from the paper and is kept so the reproducibility checks still hold.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
git clone https://github.com/Sid-Bhagat/li2025-pca-hmm-replication.git
cd li2025-pca-hmm-replication
uv venv --python 3.12
uv pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python run.py                                # Li setup; cache in data/, outputs in results/
.venv/bin/python run.py --pca-set original --results-dir results/original_setup
.venv/bin/python run.py --data-dir path/to/cache       # use another CSV cache
./run_all.sh                                           # all committed results (Li, original, variants)
```

| Option | Values |
|---|---|
| `--pca-set` | `li` (default): 12 series, 5 PCs. `original`: September 7 series, 75% rule (4 PCs). |
| `--momentum` | `li`: window t−4..t−1. `september`: t−3..t. The default is `september` with `--pca-set original` and `li` otherwise. |
| `--data-dir`, `--results-dir` | Cache and output folders (defaults `data/`, `results/`). |
| `--seed` | HMM seed, default 42. |

A run takes about 10 seconds once the data is cached. BLAS runs single-threaded, so repeated runs give byte-identical output.

## Expected outputs (`results/`)

| File | Contents |
|---|---|
| `pca_explained_variance.csv` | Explained-variance ratio for PC1–PC5, cumulative share, and which PCs were retained (Li setup: 5, 79.6%) |
| `pca_loadings.csv` | Loadings of each input series on the retained PCs |
| `hmm_states.csv` | Per stock and state: weeks, share of weeks, mean/sd return, mean momentum, volume, price range, S&P 500 return, and expected duration |
| `hmm_fit.csv` | Number of states (4), weeks, log-likelihood, and EM convergence per stock |
| `hmm_state_selection.csv` | Log-likelihood, AIC and BIC for 2–6 states per stock |
| `hmm_states_weekly.csv` | Decoded state for each week and stock |
| `eq16.csv` | Eq. 16: coefficient, SE, p-value, N, R² and adjusted R² per stock and term |
| `eq16_state_dummies_ftest.csv` | Joint F-test that all Eq. 16 state dummies are zero |
| `eq17.csv` | Eq. 17 within each state: coefficient, SE, p-value, N, R² and adjusted R² |
| `eq17_all_weeks.csv` | Eq. 17 on all weeks (the second row per stock in Li's Table 4) |
| `descriptive_stats.csv` | Li Table 2 analogue: return, momentum and volume statistics |
| `figures/price_trend_<T>.png` | Weekly close coloured by HMM state (Fig 2 analogue) |
| `figures/state_boxplots_<T>.png` | Return, momentum and volume by state (Fig 3 analogue) |
| `run_info.json` | Data folder, setup, seed, date range, row counts, and package versions |
| `original_setup/` | The same outputs for `--pca-set original` |
| `variants/` | CSVs for the two mixed setups (one change at a time) |
| `reproducibility/` | The checks behind `COMPARISON.md` |

## Reproducibility checks

`check_reproducibility.sh` runs `--pca-set original` on the September 2026 cache and compares the result with the September outputs. It also checks that two runs of each setup are byte-identical, and lists coefficient changes between the September and fresh data.
It needs `old/` (the September code, cache and outputs), which is kept locally and not in git, and the results from `run_all.sh`.

## Layout

```
run.py                    entry point
run_all.sh                produces all committed results
lirep/config.py           dates, tickers, PCA sets, momentum options, HMM settings, seed
lirep/data.py             yfinance download and CSV cache
lirep/features.py         returns, momentum, price range, macro returns
lirep/pca_step.py         PCA
lirep/hmm_step.py         Gaussian HMM, state ordering, AIC/BIC
lirep/regression.py       Eq. 16 / Eq. 17 OLS, dummy F-test
lirep/plots.py            figures
compare.py                reproducibility comparisons
check_reproducibility.sh  runs all reproducibility checks
```

## AI use

Code written and cleaned up with assistance from Claude (Anthropic).

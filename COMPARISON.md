# Li (2025) vs this replication

Paper: Li, S. (2025), PLOS ONE 20(9): e0331658, doi:10.1371/journal.pone.0331658.
Page numbers are the paper's own (x / 30).

Our numbers come from the fresh yfinance run in `results/`, downloaded 2026-11-08, 2015-01-01 to 2024-12-31, weekly. They use the default **Li setup**:

- the 12 PCA series of Li's Table 1, with 5 PCs;
- Li's momentum timing (see below);
- N = 517 weeks per stock in the regressions (Li: 518).

The **original setup** is the September 2026 replication: 7 series, 4 PCs, and momentum that includes week t. Its results are in `results/original_setup/`. The section "Verdicts that change between the two setups" lists the differences.

Significance is judged at 5%. Li marks 10/5/1% as \*/\*\*/\*\*\*, and the detail tables below use the same marks.
Verdicts are **match**, **same sign, not significant** (Li significant, ours not), or **mismatch**. **Deviation** marks a choice in our original setup that departs from the paper.

## Momentum definition

Li gives no equation for momentum. The only definition is in the text of Section 4.3 (p. 11): "The momentum of stock return is captured by autocovariance with one lag for stock percentage return in the past month (4 weeks)". It enters Eqs. 16 and 17 (p. 11) as momentum_t.

The September code computed it over weeks t−3..t, which includes the current week, the same week as the dependent return. "In the past month" suggests weeks t−4..t−1 instead.

The data confirm this. With the window ending at week t−1, the Eq. 17 all-weeks regression, which uses no HMM output, reproduces Li's Table 4 momentum coefficients for all 7 stocks: TSLA −0.0417 vs −0.0417, MSFT 1.762 vs 1.772, AMZN 0.402 vs 0.401.
The Table 3 correlations (p. 22) also match to within 0.01, for example MSFT corr(momentum, volume) = −0.182 vs Li's −0.18. With week t included, MSFT's coefficient is 5.95 and that correlation is −0.27.

The Li setup therefore uses weeks t−4..t−1 (`--momentum li`). The original setup keeps the September definition (`--momentum september`).

## Findings (Li setup)

| # | Li finding | Li's reported result (source) | Our replication (Li setup) | Verdict |
|---|---|---|---|---|
| 1 | PCA variance explained | 5 PCs from 12 series (Table 1, p. 10) explain more than 75% (§4.2, p. 10). | 5 PCs from the same 12 series explain **79.6%** (`pca_explained_variance.csv`). The original setup's 7 series and 4 PCs (84.3%) were a **deviation**. | **match** |
| 2 | Number of regimes | 4 states. AIC/BIC "not significantly varying"; 4 is where "most models depict the lowest AIC and BIC" (§4.2, pp. 10–11). | 4 states, as fixed in the config. AIC is lowest at 6 states for every stock. BIC is lowest at 4 only for META and NVDA (3 for GOOGL; 5 for AMZN, MSFT; 6 for AAPL, TSLA) (`hmm_state_selection.csv`). | **mismatch** |
| 3 | Market beta (S&P 500 return) | Significant at 1% for all 7 stocks in Eq. 16 and in Eq. 17 on all weeks (Table 4, pp. 23–24). | Significant at 1% for all 7 stocks in both. Eq. 17 all-weeks betas are within 0.004 of Li's (detail A). | **match** |
| 4 | Momentum | "Nearly all large tech companies show no momentum effect at both stock level and individual state level" (§4.3.1, p. 14). Table 4: no stock-level coefficient is significant, and 1 of 27 state regressions is significant at 5%. | Not significant for any stock in Eq. 16 or Eq. 17 all weeks. Eq. 17 all-weeks coefficients are within 0.15 of Li's. 2 of 27 state regressions are significant at 5% (detail A, C). | **match** |
| 5 | Volume (Eq. 17, all weeks) | Significant at 1% for GOOGL, META (negative), MSFT, TSLA; at 5% for NVDA; n.s. for AMZN, AAPL (§4.3.2, p. 20; Table 4). | The same stocks at the same levels: GOOGL\*\*\*, META\*\*\* (negative), MSFT\*\*\*, TSLA\*\*\*, NVDA\*\*, AMZN and AAPL n.s. (detail A). | **match** |
| 6 | Volume effect absorbed by regimes | GOOGL, META and NVDA lose their volume significance once state dummies are added (Eq. 16); MSFT and TSLA keep it; AMZN is significant at 1% in Eq. 16 (§4.3.3, p. 21; Table 4). | GOOGL and NVDA lose it; MSFT\*\*\* keeps it. **META keeps it** (−1.67e-10, p < 0.01). TSLA and AMZN are n.s. in Eq. 16 (detail B). | **match** for GOOGL, NVDA, MSFT; **mismatch** for META; **same sign, not significant** for TSLA and AMZN |
| 7 | Regime dummies (investor-sentiment effect) | Most states significant, "universally under 1%", for all stocks **except AAPL and TSLA** (§4.3.3, p. 20; Table 4). | The joint F-test of the Eq. 16 dummies is significant for **all 7** stocks: AAPL p = 3e-45, TSLA p = 7e-13, META p = 0.008, the rest p < 1e-9 (detail B). | **match** for 5 stocks; **mismatch** for AAPL and TSLA |
| 8a | Per-regime effects: beta | Beta significant at 1% in almost every state with more than ~10 weeks; the tiny states (1–9 weeks) are n.s. or undefined (Table 4). | Significant at 5% in 24 of 27 state regressions. The exceptions are AMZN state 0 (31 weeks), GOOGL state 3 (27) and NVDA state 0 (75) (detail C). | **match** (with 3 exceptions, in larger states than Li's n.s. ones) |
| 8b | Per-regime effects: volume | Volume matters in several states for every stock except AAPL (§4.3.2, p. 20). Table 4 shows 5%-significant, positive coefficients in AMZN (2 states), META, NVDA and TSLA (2 states); none in AAPL, GOOGL or MSFT. | 5%-significant only in META (negative), MSFT (positive) and TSLA (negative), one state each. None in AAPL, AMZN, GOOGL or NVDA (detail C). | **mismatch** (AAPL with no effect matches) |
| 8c | Per-regime effects: state sizes | Very uneven, with tiny states: AAPL 6 and 11 weeks, GOOGL 5, META 7, TSLA 1, 9 and 17 (Table 4). | Also uneven: MSFT 3 weeks (Eq. 17 skipped), TSLA 13, AAPL 21, GOOGL 27 and 28 (`hmm_states.csv`). | **match** (qualitatively) |

Not replicated: Table 5 (sub-sector stocks), the risk-aversion parameter γ in Tables 4–5, and Fig 4 (PC box plots). Table 3 is used only as the momentum check above.

### Detail A: Eq. 17 on all weeks, no state dummies (Li Table 4, second row per stock)

These regressions use no HMM output.

| Stock | β Li | β ours | Momentum Li | Momentum ours | Volume Li | Volume ours | adj. R² Li / ours |
|---|---|---|---|---|---|---|---|
| AMZN | 1.2327\*\*\* | 1.2327\*\*\* | 0.4013 | 0.4018 | 9.259e-12 | 9.252e-12 | 0.397 / 0.397 |
| AAPL | 1.0856\*\*\* | 1.0821\*\*\* | 0.8070 | 0.9540 | 9.541e-13 | 1.096e-12 | 0.462 / 0.462 |
| GOOGL | 1.1565\*\*\* | 1.1565\*\*\* | 1.0433 | 1.0892 | 4.775e-11\*\*\* | 4.802e-11\*\*\* | 0.479 / 0.479 |
| META | 1.2881\*\*\* | 1.2879\*\*\* | 0.6951 | 0.6912 | −8.105e-11\*\*\* | −8.144e-11\*\*\* | 0.333 / 0.333 |
| MSFT | 1.0609\*\*\* | 1.0613\*\*\* | 1.7722 | 1.7617 | 6.484e-11\*\*\* | 6.509e-11\*\*\* | 0.553 / 0.553 |
| NVDA | 1.8787\*\*\* | 1.8790\*\*\* | 0.7547 | 0.7466 | 4.799e-12\*\* | 4.804e-12\*\* | 0.409 / 0.409 |
| TSLA | 1.9008\*\*\* | 1.9009\*\*\* | −0.0417 | −0.0417 | 5.391e-11\*\*\* | 5.394e-11\*\*\* | 0.307 / 0.307 |

### Detail B: Eq. 16 (with state dummies)

Li reports a constant plus all four state dummies. We omit state 0 (the lowest-return state), so we compare the dummies as a block, using a joint F-test (`eq16_state_dummies_ftest.csv`).

| Stock | β Li / ours | Momentum Li / ours | Volume Li / ours | Li: dummies sig. at 5% | Ours: joint F p-value | adj. R² Li / ours |
|---|---|---|---|---|---|---|
| AMZN | 1.1607\*\*\* / 0.7692\*\*\* | −0.2381 / −1.5398 | 4.393e-11\*\*\* / 6.601e-12 | 3 of 4 | 6.1e-18 | 0.431 / 0.485 |
| AAPL | 1.0817\*\*\* / 0.7002\*\*\* | 0.5415 / 3.1120\* | −5.307e-13 / 2.417e-12 | 0 of 4 | 3e-45 | 0.461 / 0.641 |
| GOOGL | 1.1700\*\*\* / 0.9215\*\*\* | 0.8977 / 0.2649 | 1.373e-12 / 3.620e-11 | 3 of 4 | 2.9e-16 | 0.485 / 0.548 |
| META | 1.3197\*\*\* / 1.3284\*\*\* | 0.9048 / 1.1486 | 1.931e-11 / −1.668e-10\*\*\* | 4 of 4 | 0.0079 | 0.382 / 0.344 |
| MSFT | 1.0629\*\*\* / 0.8438\*\*\* | 1.9075 / 1.1406 | 5.847e-11\*\*\* / 7.595e-11\*\*\* | 1 of 4 | 1.9e-10 | 0.553 / 0.591 |
| NVDA | 1.9372\*\*\* / 1.4184\*\*\* | 1.4888 / 1.6040\* | 3.037e-12 / −1.375e-12 | 3 of 4 | 3.3e-14 | 0.417 / 0.478 |
| TSLA | 1.8884\*\*\* / 1.6072\*\*\* | −0.1905 / 0.0189 | 5.068e-11\*\*\* / 8.565e-12 | 0 of 4 | 7.2e-13 | 0.306 / 0.379 |

### Detail C: Eq. 17 within states (5%-significant terms; weeks per state in brackets)

State labels are arbitrary, so states can't be matched one-to-one between Li and us. Ours are ordered by mean return (0 = lowest).

| Stock | Li (Table 4, states 1–4) | Ours (states 0–3) |
|---|---|---|
| AMZN | [15, 219, 72, 212]; β in 2, 3, 4; volume + in 2, 4 | [31, 46, 320, 120]; β in 1, 2, 3; momentum + in 1 |
| AAPL | [247, 6, 11, 254]; β in 1, 3, 4 | [121, 21, 272, 103]; β in all |
| GOOGL | [65, 246, 202, 5]; β in 1, 2, 3 | [28, 175, 287, 27]; β in 0, 1, 2 |
| META | [147, 7, 273, 91]; β in 1, 3, 4; momentum + in 3; volume + in 4 | [34, 112, 142, 229]; β in all; volume − in 0 |
| MSFT | [147, 109, 14, 248]; β in all | [3 (skipped), 44, 346, 124]; β in all; volume + in 3 |
| NVDA | [130, 22, 174, 192]; β in all; volume + in 3 | [75, 38, 233, 171]; β in 1, 2, 3 |
| TSLA | [1 (undefined), 9, 17, 491]; β in 3, 4; volume + in 2, 4 | [81, 312, 13, 111]; β in all; momentum + in 3; volume − in 0 |

### Data check against Li's Table 2 (p. 21)

`descriptive_stats.csv` (Li setup) reproduces Li's Table 2 to about three significant figures:

- Mean weekly return: AMZN 0.00575 vs 0.00574; S&P 500 0.00230 vs 0.00229; NVDA 0.01304 vs 0.01301; TSLA 0.00977 vs 0.00975.
- Extremes: AMZN maximum 0.15334 vs 0.15334; TSLA minimum −0.43046 vs −0.43045.
- Momentum statistics, for example TSLA mean −0.00168 and minimum −0.09652, the same as Li's.

Our sample has 517 weeks against Li's 518, so Li's data probably has one more week at the end. With the September momentum, the sample included an earlier week (AMZN +20.0%) that isn't in Li's Table 2.

## Verdicts that change between the two setups

The original setup is 7 series, 4 PCs and momentum including week t (`results/original_setup/`). The Li setup is 12 series, 5 PCs and momentum over t−4..t−1 (`results/`). Both use the same fresh data.

| # | Finding | Original setup | Li setup | What changes it |
|---|---|---|---|---|
| 1 | PCA | 7 series, 4 PCs (84.3%): **deviation** | 12 series, 5 PCs (79.6%): **match** | PCA inputs |
| 4 | Momentum | **match** for 6 stocks; **mismatch** for MSFT (5.95\*\*\* vs Li's 1.77) | **match** for all 7 | Momentum timing: the original PCA with Li momentum also fixes MSFT |
| 6 | Volume absorbed by regimes | TSLA keeps volume in Eq. 16: **match** | TSLA n.s. in Eq. 16: **same sign, not significant** | HMM regimes (see below) |
| 7 | Regime dummies | Mismatch: TSLA significant (AAPL n.s., as in Li) | Mismatch: AAPL and TSLA both significant | HMM regimes (see below) |

Rows 2, 3, 5 and 8a–c keep their verdicts. Row 3's beta gap shrinks from 0.02 to 0.004, and row 5 now matches Li's significance levels exactly. AMZN goes from 10% to n.s.

The regime-based results (rows 6–8) are not stable enough to pin on one input. We also ran the two mixed setups (`results/variants/`):

| Setup | Eq. 16 dummies n.s. (joint F, 5%) | Li |
|---|---|---|
| original PCA, September momentum | AAPL | AAPL, TSLA |
| original PCA, Li momentum | AMZN, NVDA | |
| Li PCA, September momentum | NVDA, TSLA | |
| Li PCA, Li momentum (default) | none | |

Momentum isn't an HMM input. Changing its timing only drops the first week from the HMM sample, and that alone changes which stocks have significant regimes.

## Reproducibility

Scripts: `run_all.sh`, `check_reproducibility.sh` and `compare.py`. Outputs are in `results/reproducibility/`.
These checks use the **original setup** (`--pca-set original`), because that is what the September 2026 code ran.

### Step 3: the September cache (`old/data`) vs the September outputs (`old/outputs`)

- **Ported code, September labelling:** 266 of 266 values match (Eq. 16 and Eq. 17 coefficients and p-values, and the AIC/BIC tables), with a maximum relative difference of 1.1e-11. The HMM state labels are identical.
  13 of 14 figures are pixel-identical. In the GOOGL price trend, 8 pixels at the corners of the axes frame differ, while the plotted data is the same.
  The September run **was seeded** (`random_state=42`), so no difference comes from a missing seed, and nothing had to be forced to match.
- **Final code** (states ordered by mean weekly return; BLAS pinned to one thread):
  - Every ticker's states map one-to-one onto the September states.
  - Eq. 17 matches to 2e-13 and AIC/BIC to 1e-14.
  - Eq. 16 matches to 1.3e-4 relative. That largest gap is the volume coefficient: the omitted base state changed, and raw volume (~1e8) makes the design matrix badly conditioned.
  - No coefficient changes sign or 5% significance.
  - The figures differ only because the state colours follow the new order.
- **Two runs give byte-identical output** (25 of 25 files; `run_info.json` excluded), for both the original and the Li setup. With multithreaded BLAS, the HMM log-likelihoods differed in the last bits between runs (at most 5.5e-13 relative), so BLAS is pinned to one thread.
- **Earlier output:** the fresh original-setup run in `results/original_setup/` is byte-identical to the default output committed before the Li setup was added (24 of 24 CSV and PNG files).

### Step 4: fresh yfinance download (2026-11-08) vs September, original setup

- **Data:** the same 14 series, 522 weekly rows each, on the same dates.
  Yahoo has **revised gold futures (GC=F)**: 228 weeks from 2020-05-28 onward differ by up to 1.9%.
  The stock series differ from September by at most 1.4e-6 in weekly returns. The other macro series are identical.
  The 6 extra Li series (^FVX, ^TYX, NG=F, EURUSD=X, JPYUSD=X, AUDUSD=X) each have 522 rows on the same dates. There is no September copy of them.
- **PCA:** 84.32% → 84.29% for 4 PCs.
- **HMM states:** the share of weeks that stay in the matched state is 99.6% for AMZN, 99.8% for MSFT and 98.8% for NVDA, but only 74% for AAPL, 72% for GOOGL, 71% for META and 54% for TSLA.
- **Cause, verified:** we reran the fresh data with only the September GC=F file swapped in. That reproduces the September states for 100% of weeks, with 0 sign or significance changes. The gold revision is the only cause.
- **Changes:** 28 of 169 comparable coefficients changed sign or 5% significance (1 in Eq. 16, 27 in Eq. 17, 0 in Eq. 17 on all weeks).
  Where the Eq. 16 base state maps to a different September state (AAPL, GOOGL, META, TSLA), the Eq. 16 constant and dummies are not comparable and are left out of the table.
  The joint F-test of the dummies, which doesn't depend on the base state, **does change**. AAPL goes from p = 1e-46 (September) to p = 0.66 (fresh), and TSLA from p = 0.18 to p = 8e-18. The other five stocks stay significant at 5%.
  "Sept." states below are this code's mean-return labels on the September cache; each maps one-to-one onto the September labels.

| Stock | Table | State (fresh → Sept.) | Term | Sept. coef (p) | Fresh coef (p) | Change |
|---|---|---|---|---|---|---|
| AAPL | Eq. 16 | all | volume | -1.53e-12 (0.673) | 1.18e-12 (0.803) | sign |
| AAPL | Eq. 17 | 2 → 0 | const | -0.0317 (1.17e-09) | -0.00299 (0.601) | 5% sig. |
| GOOGL | Eq. 17 | 0 → 1 | const | 0.0385 (0.0781) | -0.0463 (0.0774) | sign |
| GOOGL | Eq. 17 | 0 → 1 | sp500_return | 0.215 (0.362) | 1.08 (1.75e-06) | 5% sig. |
| GOOGL | Eq. 17 | 0 → 1 | volume | -1.5e-10 (0.118) | 1.61e-10 (0.0598) | sign |
| GOOGL | Eq. 17 | 1 → 0 | const | -0.0254 (0.00012) | -0.00587 (0.451) | 5% sig. |
| GOOGL | Eq. 17 | 1 → 0 | volume | -5.98e-11 (0.0258) | 7.11e-12 (0.873) | sign, 5% sig. |
| GOOGL | Eq. 17 | 3 → 3 | const | 0.014 (0.354) | 0.0808 (0.00431) | 5% sig. |
| GOOGL | Eq. 17 | 3 → 3 | volume | 1.12e-10 (0.044) | -2.47e-10 (0.0179) | sign |
| META | Eq. 17 | 0 → 1 | const | 0.0815 (0.0283) | 0.0639 (0.0944) | 5% sig. |
| META | Eq. 17 | 0 → 1 | momentum | 0.771 (0.841) | -0.0384 (0.991) | sign |
| META | Eq. 17 | 1 → 2 | const | -0.00274 (0.494) | 0.0023 (0.605) | sign |
| META | Eq. 17 | 1 → 2 | volume | 9.81e-11 (0.0387) | 1.67e-11 (0.773) | 5% sig. |
| META | Eq. 17 | 2 → 3 | const | 0.0353 (0.00114) | -0.00158 (0.85) | sign, 5% sig. |
| META | Eq. 17 | 2 → 3 | sp500_return | 0.317 (0.108) | 1.17 (1.16e-20) | 5% sig. |
| META | Eq. 17 | 3 → 0 | const | -0.0239 (0.014) | -0.00142 (0.978) | 5% sig. |
| META | Eq. 17 | 3 → 0 | sp500_return | 0.251 (0.0544) | 1.01 (0.0388) | 5% sig. |
| META | Eq. 17 | 3 → 0 | volume | -9.57e-11 (0.183) | 1.44e-10 (0.683) | sign |
| NVDA | Eq. 17 | 0 → 0 | volume | -3.44e-14 (0.995) | 1.14e-13 (0.984) | sign |
| NVDA | Eq. 17 | 3 → 3 | volume | -1.16e-11 (0.0263) | -1.02e-11 (0.0541) | 5% sig. |
| TSLA | Eq. 17 | 0 → 2 | const | 0.00459 (0.624) | -0.0391 (0.0616) | sign |
| TSLA | Eq. 17 | 0 → 2 | sp500_return | 0.851 (6.67e-05) | 0.25 (0.341) | 5% sig. |
| TSLA | Eq. 17 | 0 → 2 | momentum | 2.24 (0.338) | -1.03 (0.652) | sign |
| TSLA | Eq. 17 | 0 → 2 | volume | 1.19e-11 (0.695) | -8.81e-11 (0.012) | sign, 5% sig. |
| TSLA | Eq. 17 | 2 → 1 | const | -0.000505 (0.969) | 0.0073 (0.351) | sign |
| TSLA | Eq. 17 | 2 → 1 | momentum | -0.673 (0.656) | -3.11 (0.039) | 5% sig. |
| TSLA | Eq. 17 | 3 → 3 | const | -0.0383 (0.152) | 0.0146 (0.567) | sign |
| TSLA | Eq. 17 | 3 → 3 | volume | 7.21e-11 (0.0157) | 4.42e-11 (0.0879) | 5% sig. |

## Why results differ from Li

1. **The results that don't depend on the HMM match; the HMM-based ones don't.** With Li's momentum timing, Eq. 17 on all weeks reproduces Li's Table 4 almost exactly: betas to 0.004, momentum to 0.15, and volume at the same significance levels. Adjusted R² matches to three decimals, and Table 2 to about three significant figures. Our data and OLS are therefore Li's, and the remaining gaps come from the regimes.
2. **The HMM fit is fragile.** EM runs from a single seeded start and finds a local optimum. A 2% revision to one PCA input (gold) moved 26–46% of the weeks to a different state for four stocks. Dropping one week from the sample changed which stocks have significant regime dummies.
   Li gives neither the seed nor the hmmlearn version. Li also doesn't specify the covariance type, or whether the HMM inputs are standardized (we standardize and use diagonal covariances).
   So the exact regimes can't be recovered from the paper. State labels are arbitrary, which means per-state results can only be compared as patterns.
3. **PCA details the paper leaves open.** Li lists the 12 series and says they are standardized, but not whether they enter as levels or weekly changes. We use percentage returns, with first differences for the four Treasury rates, as the September code did.
   Commodity series are Yahoo's continuous front-month futures, which Yahoo revises (see Step 4).
4. **Specification details the paper leaves open:**
   - Eq. 16 as printed has a constant and all four state indicators, which are perfectly collinear. How Li identified it is unclear; we omit one state.
   - The AIC/BIC parameter count isn't given.
   - Our sample is one week shorter (517 vs 518).
5. **The regimes are partly built from the dependent variable.** The HMM sees each stock's own weekly return, so state dummies will "explain" returns to some degree by construction. Ours are ordered by mean return, which makes that visible. This applies to Li's design as well. It means the regime-dummy finding (row 7) is weaker evidence of a sentiment effect than it looks.
6. **Data vintage.** Yahoo revises adjusted prices and continuous futures contracts, and Li's download date is unknown. Our own September and November downloads already differ for gold.

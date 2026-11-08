#!/usr/bin/env bash
# Produce every committed result from the data/ cache (downloaded if missing):
#   results/                      Li's setup: 12 Table 1 series, 5 PCs, Li momentum
#   results/original_setup/       the September 2026 setup: 7 series, 4 PCs, September momentum
#   results/variants/li_pca_september_momentum/    one change at a time,
#   results/variants/original_pca_li_momentum/     to attribute verdict changes (CSVs only)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

$PY run.py
$PY run.py --pca-set original --results-dir results/original_setup
$PY run.py --pca-set li --momentum september --results-dir results/variants/li_pca_september_momentum
$PY run.py --pca-set original --momentum li --results-dir results/variants/original_pca_li_momentum
rm -rf results/variants/*/figures

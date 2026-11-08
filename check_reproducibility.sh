#!/usr/bin/env bash
# Reproducibility checks (see COMPARISON.md, "Reproducibility"). Needs old/
# (the September 2026 cache and outputs, not in git) and run_all.sh first.
#   1. the September setup (--pca-set original) on old/data vs old/outputs
#   2. a second run on old/data, byte-compared with the first
#   3. the fresh run of the September setup (results/original_setup) vs the
#      September-cache run: sign / 5% significance changes
#   4. two runs of the default (Li) setup on data/, byte-compared
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
TMP=$(mktemp -d)
REF=results/reproducibility/september_cache_run
OUT=results/reproducibility
mkdir -p "$REF"

$PY run.py --pca-set original --data-dir old/data --results-dir "$TMP/run1" > "$TMP/run1.log"
$PY run.py --pca-set original --data-dir old/data --results-dir "$TMP/run2" > "$TMP/run2.log"
$PY run.py --results-dir "$TMP/li1" > "$TMP/li1.log"
$PY run.py --results-dir "$TMP/li2" > "$TMP/li2.log"
cp "$TMP"/run1/*.csv "$REF"/

{
  echo "## 1. September setup on old/data vs old/outputs (September)"
  $PY compare.py september "$TMP/run1" --save "$OUT/september_vs_final.csv" | grep -E 'mapping|values match|figures' || true
  echo
  echo "## 2. Two runs of the September setup on old/data"
  $PY compare.py identical "$TMP/run1" "$TMP/run2"
  echo
  echo "## 4. Two runs of the default (Li) setup on data/"
  $PY compare.py identical "$TMP/li1" "$TMP/li2"
} > "$OUT/checks.txt.tmp"
mv "$OUT/checks.txt.tmp" "$OUT/checks.txt"

$PY compare.py changes "$REF" results/original_setup --save "$OUT/fresh_vs_september" > "$OUT/fresh_vs_september.txt.tmp"
mv "$OUT/fresh_vs_september.txt.tmp" "$OUT/fresh_vs_september.txt"
rm -rf "$TMP"
cat "$OUT/checks.txt"
grep 'changed sign' "$OUT/fresh_vs_september.txt"

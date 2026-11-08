"""Weekly OHLCV data from Yahoo Finance (yfinance), cached as one CSV per
ticker in the data directory. The paper's Data Availability statement names
Yahoo Finance and the yfinance library as the data source."""

import os
import time
from pathlib import Path

import pandas as pd

from .config import START_DATE, END_DATE, TECH_TICKERS, BENCHMARK_TICKER


def cache_path(data_dir, ticker):
    safe_name = ticker.replace("^", "").replace("=", "_").replace("/", "_")
    return Path(data_dir) / f"{safe_name}.csv"


def download_weekly(ticker, data_dir, retries=3, pause=2.0):
    """Load one ticker from the cache, downloading it first if missing."""
    path = cache_path(data_dir, ticker)
    if path.exists():
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        if not df.empty:
            return df

    import yfinance as yf  # only needed when the cache is empty

    os.makedirs(data_dir, exist_ok=True)
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(
                ticker,
                start=START_DATE,
                end=END_DATE,
                interval="1wk",
                progress=False,
                auto_adjust=True,
            )
            if isinstance(df.columns, pd.MultiIndex):
                # yfinance can return MultiIndex columns for a single ticker.
                df.columns = df.columns.get_level_values(0)
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")
            tmp = path.with_name(path.name + ".tmp")
            df.to_csv(tmp)
            os.replace(tmp, path)
            # Verify the write: it opens and has the same rows.
            check = pd.read_csv(path, index_col=0, parse_dates=True)
            assert len(check) == len(df), f"{ticker}: row count mismatch after write"
            print(f"  downloaded {ticker}: {len(df)} rows, "
                  f"{df.index.min().date()}..{df.index.max().date()}, "
                  f"{path.stat().st_size} bytes")
            return check
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[warn] attempt {attempt}/{retries} failed for {ticker}: {e}")
            time.sleep(pause)

    raise RuntimeError(f"Failed to download {ticker} after {retries} attempts: {last_err}")


def load_all_data(data_dir, macro_tickers):
    """The stocks, the benchmark and the given PCA series:
    {ticker: OHLCV DataFrame}."""
    tickers = list(dict.fromkeys(list(TECH_TICKERS) + [BENCHMARK_TICKER] + list(macro_tickers)))
    return {t: download_weekly(t, data_dir) for t in tickers}

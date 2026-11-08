"""Figures: weekly price coloured by HMM state (paper Fig 2 analogue) and
return / momentum / volume by state (Fig 3 analogue)."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .io_utils import save_figure


def plot_price_trend(ticker, close, states, outdir):
    fig, ax = plt.subplots(figsize=(10, 4))
    merged = pd.DataFrame({"close": close}).join(states, how="inner")
    colors = plt.cm.tab10.colors
    for state, sub in merged.groupby("state"):
        ax.scatter(sub.index, sub["close"], s=8, color=colors[state % 10],
                   label=f"State {state}")
    ax.set_title(f"{ticker} weekly close price, colored by HMM state")
    ax.set_ylabel("Close price")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    save_figure(fig, outdir / f"price_trend_{ticker}.png")
    plt.close(fig)


def plot_state_boxplots(ticker, df, outdir):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, col, title in zip(axes, ["return", "momentum", "volume"],
                              ["Weekly return", "Momentum", "Volume"]):
        df.boxplot(column=col, by="state", ax=ax)
        ax.set_title(title)
        ax.set_xlabel("HMM state")
    fig.suptitle(f"{ticker}: return / momentum / volume by state")
    fig.tight_layout()
    save_figure(fig, outdir / f"state_boxplots_{ticker}.png")
    plt.close(fig)

"""Atomic file writes: write to a temporary file, then rename it into place,
so a crash never leaves a half-written output."""

import os
from pathlib import Path


def save_csv(df, path, **kwargs):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    df.to_csv(tmp, **kwargs)
    os.replace(tmp, path)


def save_text(text, path):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def save_figure(fig, path, dpi=150):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    # Fixed metadata so identical figures give identical bytes.
    fig.savefig(tmp, dpi=dpi, format="png", metadata={"Software": None})
    os.replace(tmp, path)

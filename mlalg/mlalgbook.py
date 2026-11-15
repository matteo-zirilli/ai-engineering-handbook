"""mlalgbook — small helpers shared by the chapters of Part IV.

* `setup()` applies the figure style of Part III (`ml/mlbook.py`: light
  surface, recessive grid, the fixed categorical order `COLORS`) and the same
  print options.
* `regions()` draws the decision regions of a fitted 2-D classifier with the
  class colours of `COLORS`, so that a class keeps its colour in every figure.
* `grid()` evaluates a fitted model on a regular grid (used to pass
  precomputed results to the interactive widgets with `ojs_define`).
* `load_fruits()` reads the data of the project from the companion repository
  `ai-projects`, pinned to the commit that added the file (network needed).

Cells run with the chapter's folder (`mlalg/`) as working directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, to_rgb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ml"))
import mlbook  # noqa: E402  (Part III helper: style and palette)

COLORS, INK, INK2, MUTED = mlbook.COLORS, mlbook.INK, mlbook.INK2, mlbook.MUTED
SURFACE = "#fcfcfb"

# The fruit data of the project: byte-identical copy of the course's file in
# matteo-zirilli/ai-projects, pinned to the commit that added it.
FRUITS_COMMIT = "dec0cb2fa1c4706f63f63dd3e5822a5084e8e5ff"
FRUITS_URL = (f"https://raw.githubusercontent.com/matteo-zirilli/ai-projects/"
              f"{FRUITS_COMMIT}/fruits.csv")
FRUITS_MD5 = "1f5d3d3ec83265951fb8d4eee0f6d1c6"


def setup() -> None:
    """Seed, display options and figure style for a chapter (as in Part III)."""
    mlbook.setup()


def tint(color: str, amount: float = 0.75) -> tuple:
    """Mix a colour with the surface: amount 0 = colour, 1 = surface."""
    c, s = np.array(to_rgb(color)), np.array(to_rgb(SURFACE))
    return tuple((1 - amount) * c + amount * s)


def grid(xlim, ylim, n: int = 200):
    """A regular n x n grid over the rectangle xlim x ylim: (xx, yy, points)."""
    xs, ys = np.linspace(*xlim, n), np.linspace(*ylim, n)
    xx, yy = np.meshgrid(xs, ys)
    return xx, yy, np.column_stack([xx.ravel(), yy.ravel()])


def regions(ax, model, X, y, *, n: int = 250, pad: float = 0.5, xlim=None, ylim=None,
            labels=None, s: float = 18, boundary: bool = True, points: bool = True):
    """Shade the predicted class of a fitted 2-D classifier and overlay the points.

    Classes are the sorted unique values of y; class i gets COLORS[i] (tinted
    for the background), so colours agree across figures.
    """
    X, y = np.asarray(X, float), np.asarray(y)
    classes = np.unique(y)
    if xlim is None:
        xlim = (X[:, 0].min() - pad, X[:, 0].max() + pad)
    if ylim is None:
        ylim = (X[:, 1].min() - pad, X[:, 1].max() + pad)
    xx, yy, P = grid(xlim, ylim, n)
    pred = np.searchsorted(classes, model.predict(P)).reshape(xx.shape)
    k = len(classes)
    ax.pcolormesh(xx, yy, pred, cmap=ListedColormap([tint(c) for c in COLORS[:k]]),
                  vmin=-0.5, vmax=k - 0.5, shading="auto", rasterized=True)
    if boundary and k > 1:
        ax.contour(xx, yy, pred, levels=np.arange(k) + 0.5, colors=INK2, linewidths=0.8)
    if points:
        for i, c in enumerate(classes):
            m = y == c
            ax.scatter(X[m, 0], X[m, 1], s=s, color=COLORS[i], edgecolor=SURFACE, linewidth=0.5,
                       label=str(c) if labels is None else labels[i], zorder=3)
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(False)
    return ax


def load_fruits(check: bool = True) -> pd.DataFrame:
    """The 500 fruits of the project, read from the pinned copy in ai-projects."""
    import hashlib
    import urllib.request
    raw = urllib.request.urlopen(FRUITS_URL, timeout=60).read()
    if check and hashlib.md5(raw).hexdigest() != FRUITS_MD5:
        raise ValueError("fruits.csv: checksum mismatch")
    import io
    return pd.read_csv(io.BytesIO(raw))

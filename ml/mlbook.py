"""mlbook — small helpers shared by the chapters of Part III.

* `setup()` fixes the random seed, the print precision and a quiet, consistent
  Matplotlib style (thin marks, recessive grid, a fixed categorical order).
* `load_housing()` reads the house-sales data used throughout the part and in
  the project (provenance: `_data/README.md` and the project chapter).
* `COLORS` is the fixed categorical order used by every figure: series keep the
  same colour in every chart of the part.

Cells run with the chapter's folder (`ml/`) as working directory.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl

DATA = Path(__file__).resolve().parent / "_data"

# Fixed categorical order (validated for colour-vision deficiencies on a light
# surface for the first three slots in scatter plots, all eight in line/bar charts).
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"

YES_NO = ["mainroad", "guestroom", "basement", "hotwaterheating", "airconditioning", "prefarea"]


def setup() -> None:
    """Seed, display options and figure style for a chapter."""
    np.set_printoptions(precision=4, suppress=True)
    pd.set_option("display.precision", 4)
    pd.set_option("display.width", 100)
    pd.set_option("display.max_columns", 20)
    mpl.rcParams.update({
        "figure.figsize": (7.5, 3.6),
        "figure.dpi": 110,
        "savefig.dpi": 110,
        "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb",
        "axes.prop_cycle": mpl.cycler(color=COLORS),
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#e4e3df",
        "grid.linewidth": 0.6,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "scatter.edgecolors": "#fcfcfb",
        "font.size": 10,
    })


def load_housing(encoded: bool = False) -> pd.DataFrame:
    """The 545 house sales (Kaggle "Housing Prices Dataset", CC0; Windsor 1987).

    encoded=False: as distributed (yes/no strings, furnishing as text).
    encoded=True:  yes/no -> 1/0 and furnishing as the integer codes used by the
                   copy of the file distributed with the course
                   (furnished=1, semi-furnished=2, unfurnished=0).
    """
    df = pd.read_csv(DATA / "housing.csv")
    if encoded:
        df = df.copy()
        for c in YES_NO:
            df[c] = (df[c] == "yes").astype(int)
        df["furnishingstatus"] = df["furnishingstatus"].map(
            {"furnished": 1, "semi-furnished": 2, "unfurnished": 0})
    return df

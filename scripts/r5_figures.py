"""Repaired coverage figure: per-rule Monte-Carlo dispersion, no bands."""
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from common import FIGURES, RESULTS
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04})
TEAL, RUST, OCHRE, SLATE = "#0D6B6E", "#A8442B", "#7A6112", "#5A6672"
C = pd.read_csv(RESULTS / "r5_curves.csv")
M = pd.read_csv(RESULTS / "r5_matched.csv")
fig, ax = plt.subplots(figsize=(6.5, 3.2))
STY = {"top-k": ("o", TEAL, "top-$k$ by volume"),
       "volume-proportional": ("s", OCHRE, "volume-proportional"),
       "uniform-random": ("^", RUST, "uniform random")}
for r, (mk, col, lbl) in STY.items():
    d = C[C.rule == r].sort_values("coverage")
    ax.fill_between(d.coverage*100, (d.recovered-d.sd)*100,
                    (d.recovered+d.sd)*100, color=col, alpha=.13)
    ax.plot(d.coverage*100, d.recovered*100, "-", lw=1.2, color=col, alpha=.7)
    ax.scatter(d.coverage*100, d.recovered*100, marker=mk, s=40, color=col,
               label=lbl, zorder=3, edgecolor="white", lw=.6)
ax.axvline(55, color=SLATE, lw=1, ls="-.")
ax.text(56, 22, "rules converge\nabove ~55% coverage", fontsize=7.4, color=SLATE)
for _, r in M.iterrows():
    ax.annotate(f"{r.spread:.3f}", (r.coverage*100, 8), fontsize=6.6,
                color=SLATE, ha="center")
ax.text(3, 3, "spread between rules at matched coverage:", fontsize=6.6, color=SLATE)
ax.set_xlabel("share of incidents covered (%)")
ax.set_ylabel("% of item-identity gain recovered")
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
ax.set_ylim(-2, 108)
fig.savefig(FIGURES / "figG2_coverage.png"); plt.close(fig)
print("figG2 regenerated from r5_curves")

"""Figures for the final draft."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import FIGURES, RESULTS

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04,
})
TEAL, RUST, OCHRE, SLATE = "#0D6B6E", "#A8442B", "#7A6112", "#5A6672"

R = pd.read_csv(RESULTS / "r3_targeting.csv")
base, full = R.base.iloc[0], R.full.iloc[0]

# ---------------------------------------------------------------- Figure 1
# The transferable result: recovery tracks incident coverage, whatever
# selection rule produced that coverage.
fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.0))

a = axes[0]
STY = {"top-k": ("o", TEAL, "top-$k$ by volume"),
       "volume-proportional": ("s", OCHRE, "volume-proportional draw"),
       "uniform-random": ("^", RUST, "uniform random draw")}
for s, (mk, col, lbl) in STY.items():
    d = R[(R.strategy == s) & (R.coverage < 0.999)].sort_values("coverage")
    a.scatter(d.coverage * 100, d.recovered * 100, marker=mk, s=42, color=col,
              label=lbl, zorder=3, edgecolor="white", lw=.6)
sub = R[R.strategy.isin(STY) & (R.coverage < 0.999)]
lin = np.polyfit(sub.coverage, sub.recovered, 1)
xs = np.linspace(0, 1, 50)
a.plot(xs * 100, np.polyval(lin, xs) * 100, color=SLATE, lw=1.2, ls="--", zorder=1)
a.text(4, 88, "$R^2=0.94$\nacross all three rules", fontsize=7.4, color=SLATE)
a.set_xlabel("share of incidents covered (%)")
a.set_ylabel("% of item-identity gain recovered")
a.legend(frameon=False, fontsize=7, loc="lower right")
a.set_title("(a) recovery follows coverage,\nnot how you chose", fontsize=8.5)

b = axes[1]
d = R[R.strategy == "top-k"].sort_values("k")
b.fill_between(d.k, d.rec_lo * 100, d.rec_hi * 100, color=TEAL, alpha=.15)
b.plot(d.k, d.recovered * 100, "-o", ms=4.5, lw=1.8, color=TEAL)
p = R[R.strategy == "k random buckets"].sort_values("k")
b.plot(p.k, p.recovered * 100, "-s", ms=3.6, lw=1.4, color=OCHRE,
       label="all items, $k$ random buckets")
b.axhline(100, color="#888", lw=1, ls=":")
b.axvline(128, color=TEAL, lw=.9, ls="-.")
b.annotate("128 items\n82% of incidents\n95% recovered", (128, 40), fontsize=7,
           color=TEAL, ha="left", xytext=(6, 0), textcoords="offset points")
b.set_xscale("log", base=2)
b.set_xlabel("items individually identified ($k$)")
b.set_ylabel("% of gain recovered")
b.legend(frameon=False, fontsize=7, loc="lower right")
b.set_title("(b) top-$k$, with bootstrap band", fontsize=8.5)
fig.savefig(FIGURES / "figF1_coverage.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
# What the baseline you choose does to the headline.
fig, ax = plt.subplots(figsize=(6.4, 2.5))
labels = ["intake fields\nonly", "+ intake\nrouting queue",
          "+ item\nidentity", "+ class\nhierarchy"]
vals = [0.562, 0.644, 0.748, 0.744]
cols = [SLATE, SLATE, TEAL, RUST]
xs = np.arange(4)
ax.bar(xs, vals, .55, color=cols, edgecolor="none")
for x, v in zip(xs, vals):
    ax.text(x, v + .006, f"{v:.3f}", ha="center", fontsize=8, fontweight="bold",
            color="#222")
ax.annotate("", xy=(2, 0.775), xytext=(0, 0.775),
            arrowprops=dict(arrowstyle="<->", color=RUST, lw=1.2))
ax.text(1, 0.783, "+0.185 if the queue is omitted", ha="center", fontsize=7.4,
        color=RUST)
ax.annotate("", xy=(2, 0.700), xytext=(1, 0.700),
            arrowprops=dict(arrowstyle="<->", color=TEAL, lw=1.4))
ax.text(1.5, 0.706, "+0.103 actual", ha="center", fontsize=7.6, color=TEAL,
        fontweight="bold")
ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=7.6)
ax.set_ylabel("AUC")
ax.set_ylim(0.50, 0.81)
fig.savefig(FIGURES / "figF2_baseline.png")
plt.close(fig)

print("written: figF1_coverage.png, figF2_baseline.png")

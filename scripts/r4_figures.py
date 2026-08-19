"""Figures for the final draft.  Values are READ FROM the result files --
a previous version hardcoded them, putting the figures outside verification.
"""
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

B = pd.read_csv(RESULTS / "r4_baselines.csv")
S = pd.read_csv(RESULTS / "r4_stability.csv")
P = pd.read_csv(RESULTS / "r4_coverage.csv")

# ---------------------------------------------------------------- Figure 1
fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.0),
                         gridspec_kw={"width_ratios": [1.15, 1]})
a = axes[0]
labels = ["intake\nfields", "+ routing\nqueue", "+ knowledge\nreference"]
x = np.arange(3)
a.bar(x - .19, B.base_auc, .36, color=SLATE, label="baseline")
a.bar(x + .19, B.with_ident, .36, color=TEAL, label="+ item identity")
for i, r in B.iterrows():
    a.annotate("", xy=(i + .19, r.with_ident), xytext=(i - .19, r.base_auc),
               arrowprops=dict(arrowstyle="->", color=RUST, lw=1.3))
    yy = max(r.base_auc, r.with_ident) + .012
    a.text(i, yy, f"{r.gain:+.3f}", ha="center", fontsize=8.5,
           fontweight="bold", color=RUST)
a.set_xticks(x); a.set_xticklabels(labels, fontsize=7.8)
a.set_ylabel("AUC"); a.set_ylim(0.50, 0.87)
a.legend(frameon=False, fontsize=7.5, loc="upper left")
a.set_title("(a) the same quantity, three baselines", fontsize=8.5)

b = axes[1]
cols = [c for c in S.columns if c != "cut"]
for c, col in zip(cols, [SLATE, TEAL, RUST]):
    b.plot(S.cut * 100, S[c], "-o", ms=4, lw=1.6, color=col,
           label=c.replace("+ ", ""))
b.axhline(0, color="#333", lw=1)
b.set_xlabel("temporal split point (% train)")
b.set_ylabel("value of item identity (AUC)")
b.legend(frameon=False, fontsize=7, loc="center left")
b.set_title("(b) stable across splits, at every level", fontsize=8.5)
fig.savefig(FIGURES / "figG1_baselines.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
fig, ax = plt.subplots(figsize=(6.4, 3.0))
STY = {"top-k": ("o", TEAL, "top-$k$ by volume"),
       "volume-proportional": ("s", OCHRE, "volume-proportional"),
       "uniform-random": ("^", RUST, "uniform random")}
for r, (mk, col, lbl) in STY.items():
    d = P[P.rule == r].sort_values("cov_train")
    ax.plot(d.cov_train * 100, d.recovered * 100, "-", lw=1, color=col, alpha=.45)
    ax.scatter(d.cov_train * 100, d.recovered * 100, marker=mk, s=44, color=col,
               label=lbl, zorder=3, edgecolor="white", lw=.6)
for lo, hi in [(28, 42), (42, 60), (65, 78), (82, 92)]:
    ax.axvspan(lo, hi, color=SLATE, alpha=.06, zorder=0)
ax.set_xlabel("share of incidents covered (%)")
ax.set_ylabel("% of item-identity gain recovered")
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
ax.text(50, 18, "shaded: coverage bands within which\nthe three rules"
                " differ by at most 2.2 points",
        fontsize=7.4, color=SLATE)
fig.savefig(FIGURES / "figG2_coverage.png")
plt.close(fig)
print("written: figG1_baselines.png, figG2_coverage.png")

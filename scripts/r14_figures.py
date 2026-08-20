"""Replacement figG5: the dose-response and the scoping curve.

The previous figG5 plotted one split's scoping curve, which is not monotone
at this resolution and invited an explanation for a wiggle that turned out
to be noise (see r14_scope.py).  This version plots the split-averaged curve
with its across-split band, and pairs it with the dose-response that is the
new mechanism evidence.

Every value is READ FROM a result file.  An earlier figure script hardcoded
numbers, which put the figures outside verification; that is not repeated.
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
TEAL, RUST, SLATE = "#0D6B6E", "#A8442B", "#5A6672"

RED = pd.read_csv(RESULTS / "r13_reduced.csv")
CUR = pd.read_csv(RESULTS / "r14_curve_queue.csv")

# Column width in this template is 3.31in.  The artwork is drawn at that
# size and stacked, so it renders about 1:1 and its 9pt labels stay 9pt.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.31, 4.5))

# ---- (a) dose-response: shrinkage against the queue's resolution ----------
lv = RED.levels.values
sh = RED.shrink_pct.values
ax1.plot(lv, sh, "-o", color=TEAL, lw=1.8, ms=6, zorder=3)
# The 2 and 4 levels sit close together on a log axis, so inline name
# labels collided ("binary" over "top 3") and so did the 27%/28% callouts.
# The names move onto the tick labels, and the percentages alternate above
# and below the line.
OFF = [(0, 11), (0, -17), (0, 11), (0, 11)]
for j, (x, y) in enumerate(zip(lv, sh)):
    ax1.annotate(f"{y:.0f}%", (x, y), textcoords="offset points",
                 xytext=OFF[j], ha="center", fontsize=8.5,
                 color=TEAL, fontweight="bold")
ax1.set_xscale("log")
ax1.set_xticks(lv)
ax1.set_xticklabels([f"{v}\n({n})" for v, n in
                     zip(lv, ["binary", "top 3", "top 10", "full"])],
                    fontsize=8)
ax1.minorticks_off()
ax1.set_xlabel("levels retained in the opening group")
ax1.set_ylabel("shrinkage in the item's\nmeasured value (%)")
ax1.set_ylim(19, 51)
ax1.set_xlim(1.75, 62)
ax1.set_title("(a) graded in the field's resolution", fontsize=9)

# ---- (b) scoping curve, split-averaged, with band ------------------------
cov = 100 * CUR.coverage.values
rec = 100 * CUR.recovered.values
lo = 100 * CUR.lo.values
hi = 100 * CUR.hi.values
ax2.fill_between(cov, lo, hi, color=TEAL, alpha=.18, lw=0,
                 label="across-split range")
ax2.plot(cov, rec, "-o", color=TEAL, lw=1.8, ms=5, zorder=3,
         label="mean of five splits")
for k in (8, 64, 128):
    r = CUR[CUR.k == k].iloc[0]
    ax2.annotate(f"top {k}", (100 * r.coverage, 100 * r.recovered),
                 textcoords="offset points", xytext=(5, -12),
                 fontsize=8, color=SLATE)
ax2.set_xlabel("share of incidents covered (%)")
ax2.set_ylabel("% of the $+0.103$ recovered")
ax2.set_title("(b) a partial CMDB recovers most of it", fontsize=9)
ax2.legend(frameon=False, fontsize=8, loc="lower right")
ax2.set_ylim(15, 105)
ax2.set_xlim(14, 99)

fig.tight_layout(h_pad=1.6)
for d in (FIGURES, Path(__file__).resolve().parent.parent / "paper"):
    fig.savefig(d / "figG5_scope.png")
print("wrote figG5_scope.png")
print(f"  (a) levels {list(lv)} -> shrinkage {[round(s,1) for s in sh]}")
print(f"  (b) k {list(CUR.k)} -> recovered {[round(r,1) for r in rec]}")

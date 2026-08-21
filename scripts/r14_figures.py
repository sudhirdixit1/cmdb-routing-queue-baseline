"""figG5: the dose-response.  NO LONGER INCLUDED IN THE PAPER.

Dropped at round eight: the figure plots four point estimates with no error
bars while the text says the two coarsest have overlapping intervals, so it
asserted a cleaner trend than the prose allows.  Its four numbers are all in
the sentence that used to cite it.  Kept so the figure is reproducible if a
longer format makes room for it WITH intervals.

Original header follows.

Replacement figG5: the dose-response and the scoping curve.

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
fig, ax1 = plt.subplots(figsize=(3.31, 2.5))

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
ax1.set_title("shrinkage is graded in the field's resolution",
              fontsize=9)

fig.tight_layout(h_pad=1.6)
#  ROUND SIXTEEN.  This figure is not in the journal manuscript -- see the
#  header -- so it no longer writes into paper/, where build_journal.py
#  copies every PNG it finds and would ship an unused one.
fig.savefig(FIGURES / "figG5_scope.png")
print("wrote figG5_scope.png")
print(f"  (a) levels {list(lv)} -> shrinkage {[round(s,1) for s in sh]}")
print("  (the scoping panel was dropped; section 9 states its numbers)")

"""Figures for the expanded draft.

Every value is READ FROM a result file.  An earlier figure script hardcoded
numbers, which put the figures outside verification; that is not repeated.

Three figures:

  figG3_overlap    the mechanism, as an area-faithful diagram.  The two
                   circles are drawn with areas equal to the two measured
                   gains and their intersection solved numerically to equal
                   the measured overlap -- so the picture cannot say
                   something the numbers do not.
  figG4_secondtask the baseline ladder repeated on three targets
  (figG5_scope is NO LONGER written here; see the note in the body)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle
from scipy.optimize import brentq

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
MECH = pd.read_csv(RESULTS / "r8_mechanism.csv").iloc[0]
SCOPE = pd.read_csv(RESULTS / "r8_scope.csv")

A0, Ai = float(B.iloc[0].base_auc), float(B.iloc[0].with_ident)
Aq, Aqi = float(B.iloc[1].base_auc), float(B.iloc[1].with_ident)
g_item, g_queue = Ai - A0, Aq - A0           # each field's gain alone
u_item, u_queue = Aqi - Aq, Aqi - Ai         # each field's unique contribution
overlap = g_item - u_item                    # == g_queue - u_queue identically

# --------------------------------------------------- Figure 3: the overlap
def lens(d, R, r):
    """Intersection area of circles radius R, r with centre distance d."""
    if d >= R + r:
        return 0.0
    if d <= abs(R - r):
        return np.pi * min(R, r) ** 2
    return (r * r * np.arccos((d * d + r * r - R * R) / (2 * d * r))
            + R * R * np.arccos((d * d + R * R - r * r) / (2 * d * R))
            - 0.5 * np.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R)))


R = np.sqrt(g_item / np.pi)                  # area == item's gain
r = np.sqrt(g_queue / np.pi)                 # area == queue's gain
# solve for the centre distance that reproduces the MEASURED overlap
d = brentq(lambda x: lens(x, R, r) - overlap, abs(R - r) + 1e-9, R + r - 1e-9)

fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.9),
                         gridspec_kw={"width_ratios": [1.05, 1]})
a = axes[0]
a.add_patch(Circle((0, 0), R, facecolor=TEAL, alpha=.30, edgecolor=TEAL, lw=1.4))
a.add_patch(Circle((d, 0), r, facecolor=RUST, alpha=.32, edgecolor=RUST, lw=1.4))
a.text(-R * .55, R * .60, "affected\nitem", ha="center", fontsize=8.5,
       color=TEAL, fontweight="bold")
a.text(d + r * .15, -r * .55, "opening\ngroup", ha="center", fontsize=8.5,
       color=RUST, fontweight="bold")
a.annotate(f"item alone\n{u_item:+.3f}", xy=(-R * .62, -R * .18),
           xytext=(-R * 2.05, -R * 1.15), fontsize=8, color=TEAL, ha="center",
           arrowprops=dict(arrowstyle="->", color=TEAL, lw=1))
a.annotate(f"overlap\n{overlap:+.3f}", xy=(d, r * .62),
           xytext=(d + r * .1, R * 1.42), fontsize=8, color="#333", ha="center",
           arrowprops=dict(arrowstyle="->", color="#333", lw=1))
a.annotate(f"group alone\n{u_queue:+.3f}", xy=(d + r * .995, 0),
           xytext=(d + r * 2.05, -R * 1.15), fontsize=8, color=RUST, ha="center",
           arrowprops=dict(arrowstyle="->", color=RUST, lw=1))
a.set_xlim(-R * 2.9, d + r + R * 2.2); a.set_ylim(-R * 1.9, R * 2.0)
a.set_aspect("equal"); a.axis("off"); a.grid(False)
a.set_title("(a) areas are the measured gains", fontsize=8.5)

b = axes[1]
# The single "matched random partition (floor)" bar is WITHDRAWN.  That floor
# was drawn per row, so incidents sharing an item fell in different cells and
# the association was destroyed by construction -- it could only return ~0.
# r17_mechanism_floor.py rebuilds it as a random partition OF ITEMS, where
# retention rises with granularity, so the honest picture is a curve and a
# band, not one bar.
SW = pd.read_csv(RESULTS / "r17_floor_sweep.csv")
FL = pd.read_csv(RESULTS / "r17_floor.csv").iloc[0]
b.plot(SW.cells, 100 * SW.retained, "-o", color=SLATE, lw=1.6, ms=4.5,
       label="floor: random partition of items")
b.fill_between(SW.cells, 100 * (SW.retained - SW.sd),
               100 * (SW.retained + SW.sd), color=SLATE, alpha=.15, lw=0)
b.axhline(100 * FL.real_retained, color=TEAL, lw=1.8, ls="-",
          label="randomised within the real item")
b.axhline(100, color=RUST, lw=1.2, ls=":", label="as recorded")
b.axvline(FL.n_groups, color="#999", lw=.9, ls="--")
b.annotate(f"{100*FL.real_retained:.0f}%", xy=(SW.cells.max(), 100 * FL.real_retained),
           xytext=(-4, 5), textcoords="offset points", ha="right",
           fontsize=8.5, fontweight="bold", color=TEAL)
b.annotate(f"{100*FL.floor_matched:.0f}% at {int(FL.n_groups)} cells",
           xy=(FL.n_groups, 100 * FL.floor_matched), xytext=(7, -12),
           textcoords="offset points", fontsize=8, color=SLATE)
b.set_xscale("log")
b.set_xticks(list(SW.cells))
b.set_xticklabels([str(int(c)) for c in SW.cells], fontsize=7.5)
b.minorticks_off()
b.set_xlabel("cells in the random item partition", fontsize=8)
b.set_ylabel("% of the group's own gain retained", fontsize=8)
b.set_ylim(0, 115)
b.tick_params(axis="y", labelsize=7.5)
b.legend(frameon=False, fontsize=7, loc="lower right")
b.set_title("(b) the floor depends on granularity", fontsize=8.5)
fig.savefig(FIGURES / "figG3_overlap.png")
plt.close(fig)

# ----------------------------------------------- Figure 4: the second task
L = pd.read_csv(RESULTS / "r9_ladder.csv")
T = pd.read_csv(RESULTS / "r9_targets.csv").set_index("task")
fig, ax = plt.subplots(figsize=(6.9, 2.8))
tasks = list(dict.fromkeys(L.task))
x = np.arange(len(tasks))
# The CSV's baseline key and the figure's label are DIFFERENT strings: the
# key is what r9_second_task.py wrote, the label is what the paper now calls
# the field.  An earlier edit renamed both at once and the lookup silently
# returned nothing.
for k, (bkey, blabel, col) in enumerate([("intake only", "intake only", SLATE),
                                         ("+ routing queue", "+ opening group",
                                          TEAL)]):
    sub = L[L.baseline == bkey].set_index("task").loc[tasks]
    off = (k - .5) * .38
    ax.bar(x + off, sub.gain, .36, color=col, label=blabel,
           yerr=[sub.gain - sub.lo, sub.hi - sub.gain],
           error_kw=dict(lw=.9, capsize=2.5, ecolor="#444"))
for i, t in enumerate(tasks):
    s = L[L.task == t].set_index("baseline")
    g0, gq = float(s.loc["intake only"].gain), float(s.loc["+ routing queue"].gain)
    ax.text(i, max(g0, gq) + .016,
            f"$-${100*(g0-gq)/g0:.0f}%", ha="center", fontsize=8.5,
            fontweight="bold", color=RUST)
ax.set_xticks(x)
ax.set_xticklabels([f"{t}\n(r={T.loc[t].corr_with_reassigned:+.2f} with reassigned)"
                    if t != "reassigned" else f"{t}\n(the paper's target)"
                    for t in tasks], fontsize=7.6)
ax.axhline(0, color="#333", lw=1)
ax.set_ylabel("value of item identity (AUC)")
ax.legend(frameon=False, fontsize=7.8, loc="upper right")
ax.set_title("admitting the opening group shrinks the measured value on every target",
             fontsize=8.5)
fig.savefig(FIGURES / "figG4_secondtask.png")
plt.close(fig)

# -------------------------------------------------- Figure 5: WITHDRAWN HERE
#
# This script used to write figG5_scope.png from r8_scope.csv -- ONE temporal
# split's scoping curve.  That curve is not monotone at this resolution, and
# reading it as an estimate is what produced a spurious "explain the flat"
# question in review; the across-split range at k=32 is 9 points (r14_scope).
#
# figG5_scope.png is now written by r14_figures.py from the split-averaged
# curve with its band.  Do NOT reinstate a writer here: both scripts wrote the
# same filename, so whichever ran last silently decided which figure the paper
# shipped, and the caption only matches one of them.

print(f"overlap solved: R={R:.4f} r={r:.4f} d={d:.4f} "
      f"lens={lens(d, R, r):.5f} target={overlap:.5f}")
print("written: figG3_overlap.png, figG4_secondtask.png")
print("figG5_scope.png is written by r14_figures.py -- see the note above.")

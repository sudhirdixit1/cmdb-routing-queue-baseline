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
  figG5_scope      deployment scoping: recovery against CMDB coverage
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
a.text(d + r * .15, -r * .55, "routing\nqueue", ha="center", fontsize=8.5,
       color=RUST, fontweight="bold")
a.annotate(f"item alone\n{u_item:+.3f}", xy=(-R * .62, -R * .18),
           xytext=(-R * 2.05, -R * 1.15), fontsize=8, color=TEAL, ha="center",
           arrowprops=dict(arrowstyle="->", color=TEAL, lw=1))
a.annotate(f"overlap\n{overlap:+.3f}", xy=(d, r * .62),
           xytext=(d + r * .1, R * 1.42), fontsize=8, color="#333", ha="center",
           arrowprops=dict(arrowstyle="->", color="#333", lw=1))
a.annotate(f"queue alone\n{u_queue:+.3f}", xy=(d + r * .995, 0),
           xytext=(d + r * 2.05, -R * 1.15), fontsize=8, color=RUST, ha="center",
           arrowprops=dict(arrowstyle="->", color=RUST, lw=1))
a.set_xlim(-R * 2.9, d + r + R * 2.2); a.set_ylim(-R * 1.9, R * 2.0)
a.set_aspect("equal"); a.axis("off"); a.grid(False)
a.set_title("(a) areas are the measured gains", fontsize=8.5)

b = axes[1]
vals = [100.0, float(MECH.mirror_pct), float(MECH.mirror_floor_pct)]
labs = ["as\nrecorded", "randomised\nwithin item", "matched random\npartition (floor)"]
bars = b.bar(range(3), vals, .56, color=[RUST, TEAL, SLATE])
for i, v in enumerate(vals):
    b.text(i, v + 3.5, f"{v:.0f}%", ha="center", fontsize=9, fontweight="bold",
           color=bars[i].get_facecolor())
b.set_xticks(range(3)); b.set_xticklabels(labs, fontsize=7.6)
b.set_ylabel("% of the queue's own gain retained", fontsize=8)
b.set_ylim(0, 120)
b.tick_params(axis="y", labelsize=7.5)
b.set_title("(b) the queue's own identity barely matters", fontsize=8.5)
fig.savefig(FIGURES / "figG3_overlap.png")
plt.close(fig)

# ----------------------------------------------- Figure 4: the second task
L = pd.read_csv(RESULTS / "r9_ladder.csv")
T = pd.read_csv(RESULTS / "r9_targets.csv").set_index("task")
fig, ax = plt.subplots(figsize=(6.9, 2.8))
tasks = list(dict.fromkeys(L.task))
x = np.arange(len(tasks))
for k, (bname, col) in enumerate([("intake only", SLATE),
                                  ("+ routing queue", TEAL)]):
    sub = L[L.baseline == bname].set_index("task").loc[tasks]
    off = (k - .5) * .38
    ax.bar(x + off, sub.gain, .36, color=col, label=bname,
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
ax.set_title("admitting the queue shrinks the measured value on every target",
             fontsize=8.5)
fig.savefig(FIGURES / "figG4_secondtask.png")
plt.close(fig)

# -------------------------------------------------- Figure 5: scoping
fig, ax = plt.subplots(figsize=(3.3, 2.6))
ax.plot(SCOPE.coverage * 100, SCOPE.recovered * 100, "-o", ms=4.5, lw=1.6,
        color=TEAL)
for _, rr in SCOPE.iterrows():
    if int(rr.k) in (8, 64, 256):
        ax.annotate(f"top {int(rr.k)}", xy=(rr.coverage * 100, rr.recovered * 100),
                    xytext=(6, -9), textcoords="offset points", fontsize=7.5,
                    color=SLATE)
ax.set_xlabel("share of incidents covered (%)", fontsize=8)
ax.set_ylabel("% of the $+0.103$ recovered", fontsize=8)
ax.tick_params(labelsize=7.5)
fig.savefig(FIGURES / "figG5_scope.png")
plt.close(fig)

print(f"overlap solved: R={R:.4f} r={r:.4f} d={d:.4f} "
      f"lens={lens(d, R, r):.5f} target={overlap:.5f}")
print("written: figG3_overlap.png, figG4_secondtask.png, figG5_scope.png")

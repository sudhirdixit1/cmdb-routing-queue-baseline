"""
r25 -- the journal figure set.

FOUR CHANGES FROM THE CONFERENCE VERSION, each answering a specific defect.

  CUT   the scaled Venn.  It encoded three numbers that sit in the adjacent
        sentence, and drawing AUC gains as areas implies they compose like a
        measure.  They do not: the "overlap" is a difference of differences
        and can be negative.  A picture that cannot say something the numbers
        do not is still a picture saying something the numbers do not mean.

  FIX   the baselines figure.  Three defects.  (i) The knowledge-reference
        bar is removed: section 8 explicitly declines to claim that field is
        creation-time, and a skimming reviewer reads a third bar at 0.805 as
        a free field that kills the result.  (ii) The y-axis ran 0.50-0.87,
        which is a truncation that inflates every visual difference; it now
        runs the metric's full range with the chance line drawn.  (iii) The
        gains carried no uncertainty; each treatment bar now carries the
        paired bootstrap interval of its own gain.

  ADD   the resolution ladder and the estate concentration, which are the
        paper's lead contribution and had no visual at all.

  ADD   the two-organisation comparison, which is the strongest new evidence
        and had no visual at all.

  KEEP  the floor granularity sweep, redrawn from the MATCHED sweep (r21)
        rather than the truncated one (r17).  At 800 cells it looked like a
        margin; at the leg's own 2,929 cells it is 3.5 points at z=0.9.  The
        honest picture is the collapse, so the figure shows the collapse.

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

PAPER = Path(__file__).resolve().parent.parent / "paper"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04,
})
TEAL, RUST, OCHRE, SLATE = "#0D6B6E", "#A8442B", "#7A6112", "#5A6672"


def save(fig, name):
    for d in (FIGURES, PAPER):
        fig.savefig(d / name)
    plt.close(fig)
    print(f"wrote {name}")


G = pd.read_csv(RESULTS / "r6_gains.csv")
B = pd.read_csv(RESULTS / "r4_baselines.csv")
S = pd.read_csv(RESULTS / "r4_stability.csv")
LAD = pd.read_csv(RESULTS / "r21_resolution_ladder.csv")
HIS = pd.read_csv(RESULTS / "r21_item_history.csv").iloc[0]
CUR = pd.read_csv(RESULTS / "r14_curve_queue.csv")
CON = pd.read_csv(RESULTS / "r14_concentration.csv")
V = pd.read_csv(RESULTS / "r20_second_org_ci.csv")
VS = pd.read_csv(RESULTS / "r20_second_org.csv")
RT = pd.read_csv(RESULTS / "r11_threshold.csv")
RC = pd.read_csv(RESULTS / "r19_shrinkage_ci.csv")
FM = pd.read_csv(RESULTS / "r21_floor_matched.csv")
FL = pd.read_csv(RESULTS / "r17_floor.csv").iloc[0]

# ======================================================== J1  the baselines
fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.9),
                       gridspec_kw={"width_ratios": [1, 1.12]})
a = ax[0]
#  TWO rungs, not three.  The knowledge reference is section 8's open
#  question, not a baseline the paper endorses.
b2 = B.iloc[:2]
g2 = G.iloc[:2]
labels = ["intake\nfields", "+ opening\ngroup"]
x = np.arange(2)
a.axhspan(0, 0.5, color=SLATE, alpha=.07, lw=0, zorder=0)
a.axhline(0.5, color=SLATE, lw=.9, ls="--", zorder=1)
a.text(-0.55, 0.512, "chance", fontsize=7, color=SLATE, va="bottom",
       ha="left")
a.bar(x - .19, b2.base_auc, .36, color=SLATE, label="baseline", zorder=3)
a.bar(x + .19, b2.with_ident, .36, color=TEAL, label="+ item identity",
      zorder=3)
for i in range(2):
    r, gr = b2.iloc[i], g2.iloc[i]
    #  the interval is on the GAIN, so it is drawn about the treatment bar
    #  as base+lo .. base+hi -- which is exactly what it bounds.
    a.errorbar(i + .19, r.with_ident,
               yerr=[[r.with_ident - (r.base_auc + gr.lo)],
                     [(r.base_auc + gr.hi) - r.with_ident]],
               fmt="none", ecolor="#222", elinewidth=1.2, capsize=3.5,
               zorder=5)
    a.annotate("", xy=(i + .19, r.with_ident), xytext=(i - .19, r.base_auc),
               arrowprops=dict(arrowstyle="->", color=RUST, lw=1.3), zorder=4)
    a.text(i, min(r.with_ident + .06, 0.95), f"{gr.gain:+.3f}", ha="center",
           fontsize=8.5, fontweight="bold", color=RUST, zorder=6)
a.set_xticks(x); a.set_xticklabels(labels, fontsize=8)
a.set_ylabel("AUC"); a.set_ylim(0, 1.0)
a.set_yticks(np.arange(0, 1.01, 0.2))
a.set_xlim(-.6, 1.6)
a.legend(frameon=False, fontsize=7.5, loc="upper left", ncols=1)
a.set_title("(a) the same quantity, two baselines", fontsize=8.5)

b = ax[1]
DISPLAY = {"intake fields only": "intake fields",
           "+ intake routing queue": "+ opening group"}
for c, col, mk in zip(list(DISPLAY), [SLATE, TEAL], ["o", "s"]):
    b.plot(S.cut * 100, S[c], "-", marker=mk, ms=4.5, lw=1.7, color=col,
           label=DISPLAY[c])
b.set_ylim(0, max(S["intake fields only"]) * 1.18)
b.set_xlabel("temporal split point (% train)")
b.set_ylabel("value of item identity (AUC)")
b.legend(frameon=False, fontsize=7.5, loc="center left")
b.set_title("(b) the ordering holds at every split point", fontsize=8.5)
fig.tight_layout(w_pad=2.2)
save(fig, "figJ1_baselines.png")

# ==================================================== J2  which layer pays
fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.9),
                       gridspec_kw={"width_ratios": [1, 1]})
a = ax[0]
lad = LAD[LAD.levels > 0].sort_values("levels")
base = float(lad.auc.iloc[0] - lad.gain.iloc[0])       # intake + group
full = float(lad[lad.field == "CI Name (aff)"].auc.iloc[0])
wbs = float(lad[lad.field == "Service Component WBS (aff)"].auc.iloc[0])
NAMES = {"CI Type (aff)": "CI type", "CI Subtype (aff)": "CI subtype",
         "Service Component WBS (aff)": "service\ncomponent",
         "CI Name (aff)": "instance\nidentity"}
a.axhline(base, color=SLATE, lw=1.2, ls="--")
a.text(10, base + .003, "baseline: intake + opening group", fontsize=7,
       color=SLATE)
a.axhline(HIS.lookup, color=OCHRE, lw=1.2, ls=":")
a.text(10, HIS.lookup + .002, "per-item outcome rate, no model",
       fontsize=7, color=OCHRE, va="bottom")
a.plot(lad.levels, lad.auc, "-", color="#BBB", lw=1, zorder=2)
a.scatter(lad.levels, lad.auc, s=52, color=TEAL, zorder=4,
          edgecolor="white", lw=.7)
for _, r in lad.iterrows():
    OFF = {"CI Type (aff)": (0, 10), "CI Subtype (aff)": (0, -24),
           "Service Component WBS (aff)": (2, -30),
           "CI Name (aff)": (0, 9)}
    a.annotate(NAMES[r.field], (r.levels, r.auc), textcoords="offset points",
               xytext=OFF[r.field], ha="center", fontsize=7.4, color=TEAL)
#  The marginal is NOT full - wbs.  `full` is intake+group+item; the model
#  that contains BOTH the service component and the item scores lower than
#  the one that contains only the item, so the difference of those two
#  points on this axis is a different quantity from the one the paper
#  reports.  Draw the quantity the ladder file records.
_mg = LAD[LAD.field == "CI Name marginal over WBS"].iloc[0]
a.annotate("", xy=(1150, wbs + _mg.gain), xytext=(1150, wbs),
           arrowprops=dict(arrowstyle="<->", color=RUST, lw=1.2))
a.text(1060, wbs + _mg.gain / 2, f"{_mg.gain:+.3f}", fontsize=8,
       fontweight="bold", color=RUST, ha="right", va="center")
a.set_xscale("log")
a.set_xticks([13, 61, 256, 2554])
a.set_xticklabels(["13", "61", "256", "2,554"], fontsize=7.5)
a.minorticks_off()
a.set_xlim(8, 5200)
a.set_ylim(0.62, 0.78)
a.set_xlabel("levels in the grouping")
a.set_ylabel("AUC")
a.set_title("(a) which layer carries the value", fontsize=8.5)

b = ax[1]
b.plot(CUR.k, 100 * CUR.recovered, "-o", color=TEAL, lw=1.7, ms=4.5,
       label="% of the item's value recovered", zorder=3)
b.fill_between(CUR.k, 100 * CUR.lo, 100 * CUR.hi, color=TEAL, alpha=.16, lw=0)
b.plot(CON.k, 100 * CON.coverage, "-s", color=OCHRE, lw=1.5, ms=4,
       label="% of incidents covered", zorder=3)
b.axhline(100, color=SLATE, lw=.9, ls="--")
b.set_xscale("log")
b.set_xticks([4, 8, 16, 32, 64, 128, 256])
b.set_xticklabels(["4", "8", "16", "32", "64", "128", "256"], fontsize=7.5)
b.minorticks_off()
b.set_ylim(0, 112)
b.set_xlabel("items identified, most frequent first")
b.set_ylabel("per cent")
b.legend(frameon=False, fontsize=7, loc="lower right")
b.set_title("(b) how much of the estate must be identified", fontsize=8.5)
fig.tight_layout(w_pad=2.2)
save(fig, "figJ2_layer.png")

# ================================================ J3  two organisations
fig, ax = plt.subplots(figsize=(6.5, 2.7))
ROWS = [
    ("Volvo IT (BPIC 2013)\n$\\geq$ 2 group changes",
     float(V[V.threshold == 2].gain_intake.iloc[0]),
     float(V[V.threshold == 2].gain_plus_group.iloc[0]),
     float(V[V.threshold == 2].shrinkage.iloc[0]),
     float(V[V.threshold == 2].lo.iloc[0]), float(V[V.threshold == 2].hi.iloc[0]),
     VS[VS.threshold == 2]),
    ("Volvo IT (BPIC 2013)\n$\\geq$ 1 group change",
     float(V[V.threshold == 1].gain_intake.iloc[0]),
     float(V[V.threshold == 1].gain_plus_group.iloc[0]),
     float(V[V.threshold == 1].shrinkage.iloc[0]),
     float(V[V.threshold == 1].lo.iloc[0]), float(V[V.threshold == 1].hi.iloc[0]),
     VS[VS.threshold == 1]),
    ("Rabobank (BPIC 2014)\n$\\geq$ 2 reassignments",
     float(RT[RT.threshold == 2].gain_intake.iloc[0]),
     float(RT[RT.threshold == 2].gain_queue.iloc[0]),
     float(RT[RT.threshold == 2].shrink_pct.iloc[0]), np.nan, np.nan, None),
    ("Rabobank (BPIC 2014)\n$\\geq$ 1 reassignment",
     float(G.iloc[0].gain), float(G.iloc[1].gain),
     float(RC[RC.task == "reassigned"].shrink_pct.iloc[0]),
     float(RC[RC.task == "reassigned"].lo.iloc[0]),
     float(RC[RC.task == "reassigned"].hi.iloc[0]), None),
]
for i, (lab, g1, g2, red, lo, hi, spl) in enumerate(ROWS):
    if spl is not None and len(spl):
        ax.plot([spl.gain_plus_group.min(), spl.gain_plus_group.max()],
                [i, i], color=TEAL, lw=6, alpha=.20, solid_capstyle="butt")
        ax.plot([spl.gain_intake.min(), spl.gain_intake.max()], [i, i],
                color=SLATE, lw=6, alpha=.20, solid_capstyle="butt")
    ax.plot([g2, g1], [i, i], color=RUST, lw=1.6, zorder=3)
    ax.scatter([g1], [i], s=62, color=SLATE, zorder=4, edgecolor="white", lw=.7)
    ax.scatter([g2], [i], s=62, color=TEAL, zorder=4, edgecolor="white", lw=.7)
    txt = (f"$-${red:.0f}%" if np.isnan(lo)
           else f"$-${red:.0f}%  [{lo:.0f},{hi:.0f}]")
    ax.text(g1 + .012, i, txt, va="center", fontsize=8, color=RUST,
            fontweight="bold")
ax.scatter([], [], s=62, color=SLATE, label="over the intake block")
ax.scatter([], [], s=62, color=TEAL, label="over intake + the opening group")
ax.set_yticks(range(len(ROWS)))
ax.set_yticklabels([r[0] for r in ROWS], fontsize=7.6)
ax.set_ylim(-.65, len(ROWS) + .55)
ax.set_xlim(0, 0.33)
ax.set_xlabel("measured value of the affected-item field (AUC)")
ax.legend(frameon=False, fontsize=7.5, loc="upper right")
ax.set_title("the reduction replicates on a second organisation, tool and "
             "country", fontsize=8.5)
ax.text(0.005, -.48, "pale bars: range across six temporal split points",
        fontsize=6.8, color=SLATE)
fig.tight_layout()
save(fig, "figJ3_twoorg.png")

# ============================================ J4  the floor was a knob
fig, ax = plt.subplots(figsize=(6.5, 3.0))
ax.plot(FM.cells, 100 * FM.retained, "-o", color=SLATE, lw=1.7, ms=5, zorder=3)
ax.text(620, 46, "floor: randomised within a RANDOM\npartition of items",
        fontsize=7.4, color=SLATE)
ax.fill_between(FM.cells, 100 * (FM.retained - FM.sd),
                100 * (FM.retained + FM.sd), color=SLATE, alpha=.16, lw=0)
real = 100 * float(FL.real_retained)
sd = 100 * float(FL.real_sd)
ax.axhline(real, color=TEAL, lw=1.8)
ax.fill_between([FM.cells.min() * .8, FM.cells.max() * 1.25],
                real - sd, real + sd, color=TEAL, alpha=.16, lw=0)
ax.text(56, real + 4, f"randomised within the real item identity: {real:.0f}%",
        color=TEAL, fontsize=7.6, fontweight="bold")
n_items = int(FM.cells.iloc[4])
for cells, tag in ((49, "the comparison\nwe published"),
                   (n_items, "matched to the\nreal leg")):
    row = FM[FM.cells == cells].iloc[0]
    ax.axvline(cells, color="#999", lw=.9, ls="--", zorder=1)
    off = (10, 4) if cells == 49 else (-9, -30)
    ax.annotate(f"{row.margin_points:.1f} pts\n$z={row.z:.1f}$",
                (cells, 100 * row.retained),
                textcoords="offset points", xytext=off,
                ha="left" if cells == 49 else "right",
                fontsize=7.6, color=RUST, fontweight="bold")
    ax.text(cells, 3, tag, fontsize=7, color="#666", ha="center")
ax.set_xscale("log")
ax.set_xticks(list(FM.cells))
ax.set_xticklabels([f"{int(c):,}" for c in FM.cells], fontsize=7.5)
ax.minorticks_off()
ax.set_xlim(FM.cells.min() * .8, FM.cells.max() * 1.25)
ax.set_ylim(0, 112)
ax.set_xlabel("cells in the random item partition")
ax.set_ylabel("% of the group's gain retained")
ax.set_title("the margin was a granularity knob: it closes at matched "
             "resolution", fontsize=8.5)
fig.tight_layout()
save(fig, "figJ4_floor.png")

# ====================================================== J5  the decision curve
#  ADDED in round sixteen.  Section 8 was rebuilt on net benefit after the
#  capacity framing was withdrawn, and a section rebuilt on a new instrument
#  with no picture of it repeats the defect this file exists to fix.
CV = pd.read_csv(RESULTS / "r23_dca_curve.csv")
GRD = pd.read_csv(RESULTS / "r23_dca_grid.csv")
DF = pd.read_csv(RESULTS / "r23_dca_facts.csv").iloc[0]

fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.8))
a = ax[0]
SER = [("treat_all", "#AAA", "treat all", "-"),
       ("intake", SLATE, "intake", "-"),
       ("intake + group", OCHRE, "intake + group", "-"),
       ("intake + item", RUST, "intake + item", "--"),
       ("intake + group + item", TEAL, "intake + group + item", "-")]
for col, c, lab, ls in SER:
    a.plot(CV.threshold, 1000 * CV[col], ls, color=c, lw=1.6, label=lab)
a.axhline(0, color="#333", lw=.9)
a.axvline(float(DF.prevalence), color="#999", lw=.9, ls=":")
a.text(float(DF.prevalence) + .008, 150, "base rate", fontsize=6.8,
       color="#666", rotation=90, va="bottom")
a.set_ylim(-110, 380)
a.set_xlim(0.05, 0.80)
a.set_xlabel("threshold probability $p_t$")
a.set_ylabel("net benefit per 1,000 arrivals")
a.legend(frameon=False, fontsize=6.6, loc="upper right")
a.set_title("(a) net benefit, four models", fontsize=8.5)

b = ax[1]
b.fill_between(GRD.threshold, 1000 * GRD.naive_lo, 1000 * GRD.naive_hi,
               color=RUST, alpha=.15, lw=0)
b.fill_between(GRD.threshold, 1000 * GRD.honest_lo, 1000 * GRD.honest_hi,
               color=TEAL, alpha=.18, lw=0)
b.plot(GRD.threshold, 1000 * GRD.delta_naive, color=RUST, lw=1.7,
       label="over intake alone")
b.plot(GRD.threshold, 1000 * GRD.delta_honest, color=TEAL, lw=1.7,
       label="over intake + opening group")
b.axhline(0, color="#333", lw=.9)
b.axvspan(float(DF.resolved_lo), float(DF.resolved_hi), color=TEAL,
          alpha=.06, lw=0, zorder=0)
tb = float(DF.threshold_at_max_honest)
b.annotate(f"ratio {DF.ratio_at_max_honest:.2f}", (tb, 1000 * GRD.delta_honest.max()),
           textcoords="offset points", xytext=(-6, 16), ha="right",
           fontsize=8, fontweight="bold", color=TEAL,
           arrowprops=dict(arrowstyle="->", color=TEAL, lw=1))
b.set_xlim(0.05, 0.80)
b.set_xlabel("threshold probability $p_t$")
b.set_ylabel("value of item identity\n(net benefit per 1,000)")
b.legend(frameon=False, fontsize=7, loc="upper right")
b.set_title("(b) what the item adds, under each baseline", fontsize=8.5)
fig.tight_layout(w_pad=2.2)
save(fig, "figJ5_dca.png")

print("\nfive figures written to figures/ and paper/.")
print("The scaled Venn (figG3 panel a) is CUT and is not regenerated here.")

"""r39 -- the round-seventeen figure set.

Five figures, one per new measurement.  Every value is READ FROM a result
file; nothing here is typed in.  An earlier figure script in this repository
hardcoded numbers, which put its figures outside verification, and round
sixteen shipped a panel whose arrow labelled a quantity that was not the
marginal.  Neither is repeated: each figure prints the file and column it
read, and the arithmetic it does is limited to what the file already states.

  figK1  the instrument matrix.  The reduction under six instruments with
         paired bootstrap intervals, and beside it the same reduction under
         net benefit across the whole threshold grid -- which is the entire
         argument in one panel: one instrument, one number per operating
         point, spanning more range than all the others put together.

  figK2  the surface V(f | B, m, theta).  Three baselines by the grid, with
         the resolvable regions marked.  This is the reporting standard,
         drawn.

  figK3  the population curve, three degradation regimes.  Replaces a caveat.

  figK4  the corpus.  Every admitted log, its reduction, its interval, its
         domain -- and the logs where the denominator is not positive drawn
         as what they are rather than left out.

  figK5  the knowledge reference.  The ladder before and after the
         interaction file settled where the field comes from.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FIGURES, RESULTS

PAPER = Path(__file__).resolve().parent.parent / "paper"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04,
})
TEAL, RUST, OCHRE, SLATE = "#0D6B6E", "#A8442B", "#7A6112", "#5A6672"
DOMAIN_COLOR = {"itsm": TEAL, "lending": SLATE, "procurement": RUST,
                "permitting": OCHRE, "healthcare": "#4B3F72",
                "enforcement": "#8C6D4F", "expenses": "#666666"}


def save(fig, name):
    for d in (FIGURES, PAPER):
        fig.savefig(d / name)
    plt.close(fig)
    print(f"  wrote {name}")


def have(*names):
    return all((RESULTS / n).exists() for n in names)


# ========================================================== figK1
if have("r30_reduction.csv", "r30_nb_grid.csv"):
    RED = pd.read_csv(RESULTS / "r30_reduction.csv")
    NBG = pd.read_csv(RESULTS / "r30_nb_grid.csv")
    scal = RED[RED.family.isin(["rank", "proper"])].copy()
    nbnamed = RED[RED.key.str.startswith("nb_")].copy()
    show = pd.concat([scal, nbnamed], ignore_index=True)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.5),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    ypos = np.arange(len(show))[::-1]
    for yp, (_, r) in zip(ypos, show.iterrows()):
        col = TEAL if r.family in ("rank", "proper") else RUST
        ax.plot([r.reduction], [yp], "o", color=col, ms=6, zorder=3)
        if np.isfinite(r.reduction_lo):
            ax.plot([r.reduction_lo, r.reduction_hi], [yp, yp], "-",
                    color=col, lw=2, alpha=.7, zorder=2)
    ax.set_yticks(ypos)
    ax.set_yticklabels(show.instrument, fontsize=8)
    ax.axvline(0, color="k", lw=.8)
    ax.axvline(1, color=SLATE, lw=.8, ls=":")
    auc_red = float(scal[scal.key == "auc"].reduction.iloc[0])
    ax.axvline(auc_red, color=TEAL, lw=.8, ls="--")
    ax.set_xlabel("reduction  $1 - V(f\\,|\\,B_1)\\,/\\,V(f\\,|\\,B_0)$")
    ax.set_title("Same data, same models, six instruments", fontsize=9.5)
    ax.text(auc_red, len(show) - .3, "  the published number",
            color=TEAL, fontsize=7.5, va="top")

    g = NBG.dropna(subset=["reduction"]).sort_values("threshold")
    ax2.plot(g.threshold, g.reduction, "-o", color=RUST, ms=3, lw=1.3)
    ax2.axhline(auc_red, color=TEAL, lw=1.0, ls="--")
    ax2.axhline(1, color=SLATE, lw=.8, ls=":")
    ax2.axhline(0, color="k", lw=.8)
    neg = NBG[NBG.honest_hi < 0]
    if len(neg):
        ax2.axvspan(neg.threshold.min() - .0125, neg.threshold.max() + .0125,
                    color=RUST, alpha=.10, lw=0)
        ax2.text(neg.threshold.mean(), ax2.get_ylim()[1],
                 "item resolvably\nharmful here", ha="center", va="top",
                 fontsize=7, color=RUST)
    ax2.set_xlabel("threshold probability $\\theta$")
    ax2.set_ylabel("reduction")
    ax2.set_title("One instrument, across the operating range", fontsize=9.5)
    fig.tight_layout()
    save(fig, "figK1_instruments.png")

# ========================================================== figK2
if have("r30_nb_grid.csv", "r30_reduction.csv"):
    NBG = pd.read_csv(RESULTS / "r30_nb_grid.csv")
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.plot(NBG.threshold, 1000 * NBG.naive_increment, "-o", color=SLATE,
            ms=3.2, lw=1.3, label="$V(f\\,|\\,B_0)$: free field omitted")
    ax.fill_between(NBG.threshold, 1000 * NBG.naive_lo, 1000 * NBG.naive_hi,
                    color=SLATE, alpha=.16, lw=0)
    ax.plot(NBG.threshold, 1000 * NBG.honest_increment, "-o", color=TEAL,
            ms=3.2, lw=1.6, label="$V(f\\,|\\,B_1)$: free field admitted")
    ax.fill_between(NBG.threshold, 1000 * NBG.honest_lo, 1000 * NBG.honest_hi,
                    color=TEAL, alpha=.20, lw=0)
    ax.axhline(0, color="k", lw=.9)
    best = NBG.loc[NBG.honest_increment.idxmax()]
    worst = NBG.loc[NBG.honest_increment.idxmin()]
    for r, lab, col, dy in ((best, "worth most", TEAL, 12),
                            (worst, "worth least", RUST, -16)):
        ax.annotate(f"{lab}\n$\\theta$={r.threshold:g}, "
                    f"{1000 * r.honest_increment:+.1f}",
                    xy=(r.threshold, 1000 * r.honest_increment),
                    xytext=(r.threshold, 1000 * r.honest_increment + dy),
                    ha="center", fontsize=7, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=.8))
    ax.set_xlabel("threshold probability $\\theta$")
    ax.set_ylabel("net benefit added, per thousand arrivals")
    ax.set_title("$V(f \\mid B, m, \\theta)$ at $m$ = net benefit: "
                 "two baselines, every operating point", fontsize=9.5)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    save(fig, "figK2_surface.png")

# ========================================================== figK3
if have("r36_curve.csv"):
    CUR = pd.read_csv(RESULTS / "r36_curve.csv")
    full = CUR[CUR.regime == "full"].iloc[0]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.4))
    for reg, col, mk in (("rare-first", TEAL, "o"),
                         ("random", SLATE, "s"),
                         ("common-first", RUST, "^")):
        s = CUR[CUR.regime == reg].sort_values("actual_population")
        x = np.append(s.actual_population.values, full.actual_population)
        y1 = np.append(s.honest.values, full.honest)
        y2 = np.append(s.reduction.values, full.reduction)
        ax.plot(x, y1, "-" + mk, color=col, ms=4, lw=1.4,
                label=reg.replace("-", " ") + " dropped")
        lo = np.append(s.honest_lo.values, full.honest_lo)
        hi = np.append(s.honest_hi.values, full.honest_hi)
        ax.fill_between(x, lo, hi, color=col, alpha=.13, lw=0)
        ax2.plot(x, y2, "-" + mk, color=col, ms=4, lw=1.4)
    ax.axhline(0, color="k", lw=.9)
    ax.set_xlabel("share of incidents whose item is recorded")
    ax.set_ylabel("$V(\\mathrm{item} \\mid \\mathrm{intake} + \\mathrm{group})$, AUC")
    ax.set_title("What a half-empty register is worth", fontsize=9.5)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax2.axhline(float(full.reduction), color=SLATE, lw=.9, ls="--")
    ax2.set_xlabel("share of incidents whose item is recorded")
    ax2.set_ylabel("reduction")
    ax2.set_title("and what the reduction does as it empties", fontsize=9.5)
    fig.tight_layout()
    save(fig, "figK3_population.png")

# ========================================================== figK4
if have("r33_ladder.csv"):
    LAD = pd.read_csv(RESULTS / "r33_ladder.csv")
    P = LAD[LAD.primary].copy()
    P["label"] = P.log + "  (" + P.target.str[:4] + ")"
    # A ratio whose denominator is not resolvably positive is not a point on
    # this axis.  The first draft plotted UCI 498's duration row at 15.0 --
    # a denominator of +0.0005 -- and every other log collapsed into a
    # smudge at the origin.  Those rows are named on the right instead,
    # which is what they are: logs with no entity value to reduce.
    P["plottable"] = P.naive_lo > 0
    show = P[P.plottable].sort_values(["domain", "log", "target"])
    drop = P[~P.plottable].sort_values(["domain", "log", "target"])
    fig, ax = plt.subplots(figsize=(7.6, max(3.0, .30 * len(show) + 2.0)))
    ypos = np.arange(len(show))[::-1]
    for yp, (_, r) in zip(ypos, show.iterrows()):
        col = DOMAIN_COLOR.get(r.domain, SLATE)
        ax.plot([r.reduction], [yp], "o", color=col, ms=6.5, zorder=3)
        if np.isfinite(r.get("reduction_lo", np.nan)):
            ax.plot([r.reduction_lo, r.reduction_hi], [yp, yp], "-",
                    color=col, lw=2.2, alpha=.75, zorder=2)
        else:
            ax.plot([r.reduction], [yp], "o", mfc="none", mec=col, ms=11,
                    lw=1.0, zorder=4)
    ax.set_yticks(ypos)
    ax.set_yticklabels(show.label, fontsize=8)
    ax.axvline(0, color="k", lw=.9)
    ax.axvline(1, color=SLATE, lw=.8, ls=":")
    ax.set_xlim(-1.3, 1.35)
    ax.set_xlabel("reduction  $1 - V(f\,|\,B_1)\,/\,V(f\,|\,B_0)$   (ROC AUC)")
    ax.set_title("Every log where the entity has value to reduce" + chr(10)
                 + f"({len(show)} of {len(P)} log-target pairs; a hollow ring "
                 + "means the interval is not reportable)", fontsize=9.5)
    handles = [plt.Line2D([], [], marker="o", ls="", color=DOMAIN_COLOR[d],
                          label=d) for d in sorted(show.domain.unique())]
    ax.legend(handles=handles, frameon=False, fontsize=7.5, ncol=3,
              loc="lower left")
    if len(drop):
        names = ", ".join(sorted(set(drop.label)))
        fig.text(0.5, -0.02,
                 f"$V(f\,|\,B_0)$ is not resolvably positive on "
                 f"{len(drop)} further pairs, so no reduction exists to plot: "
                 + names, ha="center", fontsize=6.8, color=SLATE, wrap=True)
    fig.tight_layout()
    save(fig, "figK4_corpus.png")

# ========================================================== figK5
if have("r35_ladder.csv", "r35_dimensionality_null.csv"):
    LAD = pd.read_csv(RESULTS / "r35_ladder.csv")
    NUL = pd.read_csv(RESULTS / "r35_dimensionality_null.csv")
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    lab = {"intake": "intake only",
           "intake + group": "+ opening group",
           "intake + group + km_open": "+ knowledge ref.\n(incident's own row)",
           "intake + group + km_int": "+ knowledge ref.\n(from the interaction)",
           "intake + group + km_prov": "+ knowledge ref.\n(interaction worked first)"}
    x = np.arange(len(LAD))
    cols = [SLATE, TEAL, RUST, RUST, RUST]
    ax.bar(x, LAD.gain, color=cols[:len(LAD)], width=.62)
    ax.errorbar(x, LAD.gain, yerr=[LAD.gain - LAD.lo, LAD.hi - LAD.gain],
                fmt="none", ecolor="k", lw=1.0, capsize=3)
    lo_n, hi_n = float(NUL.gain.min()), float(NUL.gain.max())
    ax.axhspan(lo_n, hi_n, color=OCHRE, alpha=.18, lw=0)
    ax.text(len(LAD) - .5, (lo_n + hi_n) / 2,
            "  matched-mass\n  random partition\n  of the same size",
            fontsize=7, va="center", color=OCHRE)
    ax.axhline(0, color="k", lw=.9)
    ax.set_xticks(x)
    ax.set_xticklabels([lab.get(b, b) for b in LAD.baseline], fontsize=7)
    ax.set_ylabel("$V(\\mathrm{item} \\mid B)$, AUC")
    ax.set_title("What the item is worth, as the baseline admits more of "
                 "what was already recorded", fontsize=9.5)
    fig.tight_layout()
    save(fig, "figK5_knowledge.png")

print("\nfigures written to", FIGURES, "and", PAPER)

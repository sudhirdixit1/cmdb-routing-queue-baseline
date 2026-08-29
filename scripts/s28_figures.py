"""s28 -- the round-twenty figures.

Every figure the round-twenty corrections change is regenerated here from the
corrected result files, and the file names are the ones the manuscript already
cites, so a figure cannot be a stale picture of a withdrawn number.

  figS2_sobol.png       the decomposition, WITHIN INSTRUMENT, with the total
                        higher-order remainder drawn rather than left implicit
  figS3_regions.png     the robustness index from the WHOLE-SURFACE band
  figS4_dca.png         the decision curve on CALIBRATED probabilities, with
                        the pointwise interval and the simultaneous band
  figS6_coverage.png    simulation coverage with Monte Carlo error bars
  figS7_calibration.png calibration before and after, on the case study

    python s28_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAPER = HERE.parent / "paper"
plt.rcParams.update({"font.size": 8, "figure.dpi": 400,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "axes.grid": False})
DARK = "0.20"


def load(n):
    for p in (RESULTS / n, RESULTS / (n + ".gz")):
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:  # noqa: BLE001
                return None
    return None


# --------------------------------------------------------------------------
def fig_sobol():
    """ROUND TWENTY-FIVE, round 24's minor comment 8.

    This figure was a stacked bar per pair whose segments were MEDIANS over
    the five instruments.  Medians do not add, so the bars did not sum to one
    -- several exceeded it -- and the caption had to tell the reader not to
    perform the addition the picture invites.  A referee said to plot one
    pair's decomposition exactly instead, with the corpus summarised as
    points and intervals, and they were right: a stacked bar is a promise
    that the parts make the whole, and only the left panel can keep it.

    LEFT.  One pair, one instrument, so the components are a decomposition
    and sum to one exactly.  The pair is the case study's own log and the
    reference target, selected by the same rule the rest of the paper uses
    rather than chosen for its shape.
    RIGHT.  Every axis's first-order index across the corpus: the median over
    pairs as a point, with the range the middle pairs occupy as a bar and the
    full range as a rule.  Nothing here is stacked, so nothing invites an
    addition that would be wrong.
    """
    IDX = load("s22_indices.csv")
    SUM = load("s22_summary.csv")
    if IDX is None or SUM is None:
        return None
    pr = IDX[(IDX.scale == "raw-within-metric")
             & (IDX.measure == "equal-level")]
    s = SUM[(SUM.scale == "raw-within-metric")
            & (SUM.measure == "equal-level")]
    if pr.empty or s.empty:
        return None

    order = [c for c in ("split", "rung", "quality_level", "learner")
             if c in set(pr.axis)]
    labels = {"rung": "baseline", "learner": "pipeline",
              "quality_level": "register quality", "split": "split"}
    shades = ["0.15", "0.38", "0.58", "0.76"]

    #  the exact panel: the largest pair in the corpus, at the reference
    #  instrument, which is the cell every other table reports at
    REF_METRIC = "auc"
    big = (pr.groupby(["log", "target"]).n_cells.max().idxmax()
           if "n_cells" in pr.columns
           else tuple(pr.groupby(["log", "target"]).size().idxmax()))
    one = pr[(pr.log == big[0]) & (pr.target == big[1])
             & (pr.metric == REF_METRIC)]
    one_rem = s[(s.log == big[0]) & (s.target == big[1])
                & (s.metric == REF_METRIC)]
    if one.empty or one_rem.empty:
        return None
    parts = [float(one[one.axis == c].S.iloc[0]) if (one.axis == c).any()
             else 0.0 for c in order]
    remainder = float(one_rem.interaction_total.iloc[0])

    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(6.9, 2.9), gridspec_kw=dict(width_ratios=[1.0, 1.55]))

    left = 0.0
    for k, (c, v) in enumerate(zip(order, parts)):
        axL.bar([0], [v], bottom=[left], width=0.55,
                color=shades[k % len(shades)], edgecolor="white",
                linewidth=0.6, label=labels.get(c, c))
        if v > 0.045:
            axL.text(0, left + v / 2, "%.2f" % v, ha="center", va="center",
                     fontsize=6.4, color="white" if k < 2 else "0.1")
        left += v
    axL.bar([0], [remainder], bottom=[left], width=0.55, color="white",
            edgecolor="0.25", linewidth=0.7, hatch="////",
            label="higher-order total")
    if remainder > 0.045:
        axL.text(0, left + remainder / 2, "%.2f" % remainder, ha="center",
                 va="center", fontsize=6.4, color="0.1")
    axL.set_xlim(-0.55, 0.55)
    axL.set_ylim(0, 1.0)
    axL.set_xticks([])
    axL.set_ylabel("share of the variance of $V_s$")
    axL.set_title("%s / %s, %s\n(one decomposition: the parts sum to one)"
                  % (big[0], big[1], REF_METRIC), fontsize=7.2)
    for sp in ("top", "right"):
        axL.spines[sp].set_visible(False)

    #  the corpus panel: a point and two ranges per axis, plus the remainder
    per = pr.groupby(["log", "target", "axis"]).S.median().reset_index()
    rem = s.groupby(["log", "target"]).interaction_total.median().reset_index()
    rows = [(labels.get(c, c), per[per.axis == c].S.values) for c in order]
    rows.append(("higher-order total", rem.interaction_total.values))
    ys = np.arange(len(rows))[::-1]
    for y, (name, v) in zip(ys, rows):
        v = np.asarray(v, float)
        v = v[np.isfinite(v)]
        if not len(v):
            continue
        axR.hlines(y, v.min(), v.max(), color="0.72", lw=1.0, zorder=1)
        axR.hlines(y, np.percentile(v, 25), np.percentile(v, 75),
                   color="0.35", lw=4.0, zorder=2)
        axR.plot([np.median(v)], [y], "o", ms=4.6, color="black", zorder=3)
    axR.set_yticks(ys)
    axR.set_yticklabels([r[0] for r in rows], fontsize=7.2)
    axR.set_xlim(0, 1.0)
    axR.set_xlabel("first-order index across the \\nPairs\\ pairs"
                   .replace("\\nPairs\\", "%d" % per.groupby(
                       ["log", "target"]).ngroups))
    axR.set_title("the corpus: median, middle half, full range", fontsize=7.2)
    axR.grid(axis="x", color="0.9", lw=0.5, zorder=0)
    for sp in ("top", "right", "left"):
        axR.spines[sp].set_visible(False)

    #  a legend anchored to the LEFT axes ran across the right panel's own
    #  x-axis label; it belongs to the figure, under both panels
    h, l = axL.get_legend_handles_labels()
    fig.legend(h, l, frameon=False, ncol=5, fontsize=6.4,
               loc="lower center", bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(bottom=0.30, top=0.84, wspace=0.30)
    p = PAPER / "figS2_sobol.png"
    fig.savefig(p)
    plt.close(fig)
    return p

def fig_regions():
    #  ROUND TWENTY-ONE.  The article's regions and rho are computed under a
    #  COVERAGE-CALIBRATED critical value, so the figure must be too, or the
    #  caption and the picture disagree.  s33 carries both; the nominal bar is
    #  drawn behind the calibrated one so the size of the correction is what
    #  the reader sees rather than something they have to be told.
    #  ROUND TWENTY-SEVEN.  This drew the COVERAGE-CALIBRATED labels when a
    #  calibrated file existed and fell back to the nominal ones otherwise.
    #  The designed surface has no calibrated file: the K/n calibration was
    #  fitted on the old surface's plane, and this round's coverage
    #  measurement says the widening the new families need is LARGER than
    #  that calibration supplies (1.36-1.88 against an applied 1.18-1.77).
    #  Applying a calibration known to be under-sized, and drawing it as the
    #  operative one, would be worse than drawing the nominal band and saying
    #  so -- which is what the caption now does.
    #
    #  The fallback is NOT left pointing at the old surface.  A figure that
    #  silently draws a surface the manuscript no longer reports, the moment
    #  a file is absent, is the defect this round found four times.
    G = None
    REG = load("s48w_regions.csv")
    if G is not None and not G.empty:
        d = G.sort_values("rho_calibrated")
        rho, rho_nom = d.rho_calibrated.values, d.rho.values
        region = d.region_calibrated.values
    elif REG is not None and not REG.empty:
        d = REG.sort_values("rho")
        rho, rho_nom, region = d.rho.values, None, d.region.values
    else:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 0.30 * len(d) + 1.2))
    y = np.arange(len(d))
    if rho_nom is not None:
        ax.barh(y, rho_nom, color="0.86", height=0.72,
                label="nominal critical value")
    ax.barh(y, rho, color=np.where(rho >= 0, DARK, "0.55"), height=0.45,
            label="coverage-calibrated")
    ax.axvline(0, color="0.2", lw=0.8)
    ax.axvline(1, color="0.2", lw=0.6, ls=":")
    ax.set_yticks(y)
    ax.set_yticklabels(["%s / %s  (%s)" % (a, b, c)
                        for a, b, c in zip(d.log, d.target, region)],
                       fontsize=6.5)
    if rho_nom is not None:
        ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    ax.set_xlabel("robustness index $\\rho$, whole-surface simultaneous band"
                  "   ($\\rho=1$: one number is safe)")
    ax.set_xlim(-1.05, 1.05)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    p = PAPER / "figS3_regions.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_dca():
    B = load("s26_bands.csv")
    if B is None or B.empty:
        return None
    d = B[(B.rung == "B_intake_g") & (B.learner == "logit")]
    if d.empty:
        d = B[B.rung == B.rung.iloc[0]]
    d = d.sort_values("threshold")
    fig, ax = plt.subplots(figsize=(5.6, 3.1))
    ax.fill_between(d.threshold, d.sim_lo, d.sim_hi, color="0.86",
                    label="simultaneous band")
    ax.plot(d.threshold, d.pt_lo, color="0.45", lw=0.7, ls="--",
            label="pointwise interval")
    ax.plot(d.threshold, d.pt_hi, color="0.45", lw=0.7, ls="--")
    ax.plot(d.threshold, d.dnb, color=DARK, lw=1.4,
            label="net-benefit increment")
    ax.axhline(0, color="0.2", lw=0.8)
    ax.set_xlabel("threshold probability $\\theta$ (calibrated)")
    ax.set_ylabel("$\\Delta$ net benefit per case")
    ax.legend(frameon=False, fontsize=6.6, loc="best")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    p = PAPER / "figS4_dca.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_coverage():
    #  s31 when it has run and s10 when it has not, which is the same rule
    #  round20_numbers and verify_numbers follow.  A figure drawn from the
    #  200-replicate run beside a table printed from the 1000-replicate one
    #  would be two different experiments on one page.
    C = load("s31_coverage.csv")
    if C is not None and len(C) and "experiment" in C.columns:
        C = C[C.experiment == "core"]
    if C is None or C.empty:
        C = load("s10_coverage.csv")
    if C is None or C.empty:
        return None
    need = {"world", "estimand", "interval", "coverage"}
    if not need.issubset(C.columns):
        return None
    #  the estimator's own limit is the estimand a resampling interval can
    #  cover; the oracle comparison is a separate row in the same file and is
    #  discussed in the text rather than drawn here.
    d = C[C.estimand == "V_limit"]
    if d.empty:
        d = C
    n = float(d.n.iloc[0]) if "n" in d.columns else 200.0
    keep = [i for i in ("naive", "naive_pct", "nested", "nested_pct",
                        "nested_basic", "nested_bc", "nested_mofn")
            if i in set(d.interval)]
    piv = d.pivot_table(index="world", columns="interval", values="coverage")
    cols = [c for c in keep if c in piv.columns] or list(piv.columns)
    piv = piv[cols]
    LBL = {"naive": "fixed-model percentile",
           "naive_pct": "fixed-model percentile",
           "nested": "nested percentile", "nested_pct": "nested percentile",
           "nested_basic": "nested basic (reported)",
           "nested_bc": "nested bias-corrected",
           "nested_mofn": "nested $m$-out-of-$n$"}
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    w = 0.8 / max(1, len(cols))
    x = np.arange(len(piv))
    shades = ["0.78", "0.55", "0.20", "0.40", "0.66"]
    for k, c in enumerate(cols):
        v = piv[c].values.astype(float)
        se = np.sqrt(np.clip(v, 0, 1) * (1 - np.clip(v, 0, 1)) / n)
        ax.bar(x + k * w, v, width=w * 0.9, color=shades[k % len(shades)],
               label=LBL.get(c, c), yerr=1.96 * se, capsize=1.6,
               error_kw=dict(lw=0.6))
    ax.axhline(0.95, color="0.15", lw=0.8, ls="--")
    ax.set_xticks(x + w * (len(cols) - 1) / 2.0)
    ax.set_xticklabels(piv.index, fontsize=7)
    ax.set_ylabel("coverage of the estimator's own limit")
    ax.set_ylim(0, 1.02)
    ax.legend(frameon=False, fontsize=6.4, ncol=2, loc="lower right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    p = PAPER / "figS6_coverage.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_calibration():
    C = load("s26_curve.csv")
    if C is None or C.empty:
        return None
    d = C[(C.log == "BPIC14") & (C.target == "handover")
          & (C.rung == "B_intake_g")]
    if d.empty:
        d = C[C.log == C.log.iloc[0]]
    fig, ax = plt.subplots(figsize=(4.0, 3.6))
    ax.plot([0, 1], [0, 1], color="0.6", lw=0.8, ls="--")
    marks = {"raw": "o", "platt": "s", "isotonic": "^"}
    for kind, g in d.groupby("calibration"):
        gg = g.groupby("bin")[["p_mean", "y_mean"]].mean().sort_index()
        ax.plot(gg.p_mean, gg.y_mean, marker=marks.get(kind, "o"),
                ms=3.2, lw=1.0, label=kind)
    ax.set_xlabel("mean predicted risk")
    ax.set_ylabel("observed rate")
    ax.legend(frameon=False, fontsize=6.8, loc="best")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    p = PAPER / "figS7_calibration.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def main():
    made = []
    for fn in (fig_sobol, fig_regions, fig_dca, fig_coverage, fig_calibration):
        try:
            p = fn()
        except Exception as e:  # noqa: BLE001
            print("  %-16s FAILED: %s" % (fn.__name__, e))
            continue
        if p:
            made.append(p.name)
            print("  wrote %s" % p.name)
        else:
            print("  %-16s skipped: its source is not present" % fn.__name__)
    print("s28_figures: %d figures" % len(made))


if __name__ == "__main__":
    main()

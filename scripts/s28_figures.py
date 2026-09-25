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

Beside each PNG a vector PDF of the same name is written: the journal asks
for vector art, and the PNG stays because other documents embed it.

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
#  pdf.fonttype 42 embeds the text as TrueType so it stays text in the vector
#  file (type 3, the default, outlines every glyph).
plt.rcParams.update({"font.size": 8, "figure.dpi": 400,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "axes.grid": False,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
DARK = "0.20"


def load(n):
    for p in (RESULTS / n, RESULTS / (n + ".gz")):
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:  # noqa: BLE001
                return None
    return None


def save(fig, stem):
    """Write paper/<stem>.png (400 dpi, for the documents that embed raster)
    and paper/<stem>.pdf (vector, what the journal build includes)."""
    p = PAPER / (stem + ".png")
    fig.savefig(p)
    fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    return p


def panel_letter(ax, tag):
    """The panel letter, inside the axes at the top right, where Figure 1
    puts its own; the journal wants no title above a plot, so what the two
    titles said is in the caption and the letters are how it points."""
    ax.text(0.995, 0.97, tag, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="top", ha="right")


# --------------------------------------------------------------------------
#  IJF print geometry for the article's Figure 3: drawn at the text width
#  (468 TeX pt, elsarticle 3p) on a fixed canvas, so at
#  \includegraphics[width=\textwidth] it prints at 1:1 with 8 pt text.
TEXTWIDTH_IN = 468.0 / 72.27
FIG_FONT = 8.0

#  The reference pair of panel (a): named, not chosen by a tie-break.  It is
#  the case study's pair, the one Figure 1 draws, at the instrument every
#  other table reports first.
REF_PAIR = ("BPIC14", "handover")
REF_METRIC = "auc"

#  The four strata of eq. (strata), in the order the text names them, with
#  a greyscale fill that differs in HATCH as well as tone.
STRATA = (
    ("share_resampling", "split-involving\n(resampling)",
     dict(facecolor="white", hatch="////")),
    ("share_analyst", "analyst choices",
     dict(facecolor="0.62", hatch=None)),
    ("share_counterfactual", "register-quality\ncounterfactual",
     dict(facecolor="white", hatch="....")),
    ("share_mixed", "mixed", dict(facecolor="0.88", hatch="\\\\\\\\")),
)


def fig_sobol():
    """FIGURE 3.  The decomposition with the split as an error stratum.

    ROUND TWENTY-EIGHT (IJF editor's review).  The previous figure drew the
    POOLED first-order decomposition, which the text calls secondary, and not
    the stratum partition behind the headline share.  This one draws the
    partition of eq. (strata), from the file Table tab:strata and its macros
    are made from (s42_strata.csv, every split level):

    (a) the exact four-stratum partition for ONE declared pair at ONE
        instrument, which sums to one;
    (b) the four stratum shares for every pair -- each pair's median over
        the instruments, the row Table tab:strata prints -- with the corpus
        median (the \\share...StratumPct macros) marked and the case study's
        two pairs drawn open, since the text names them as the exception.
    Both panels share one x axis, the share of the variance of V_s.
    """
    ST = load("s42_strata.csv")
    if ST is None or ST.empty:
        return None
    a = ST[ST.split_set == "all"]
    cols = [c for c, _, _ in STRATA]
    one = a[(a.log == REF_PAIR[0]) & (a.target == REF_PAIR[1])
            & (a.metric == REF_METRIC)]
    if one.empty:
        return None
    parts = [float(one[c].iloc[0]) for c in cols]
    pp = a.groupby(["log", "target"])[cols].median()
    med = pp.median()
    case = [i for i in pp.index if i[0] == REF_PAIR[0]]

    W = TEXTWIDTH_IN
    #  R leaves room for half the "100%" tick label, which a standard bbox
    #  would otherwise clip (2026-09-25 copy-edit read)
    L, R = 1.62, 0.26
    ha_, hb_ = 0.95, 2.10
    bottom, mid, top = 0.46, 0.14, 0.04
    H = bottom + hb_ + mid + ha_ + top
    fig = plt.figure(figsize=(W, H))
    fw = (W - L - R) / W
    axA = fig.add_axes([L / W, (bottom + hb_ + mid) / H, fw, ha_ / H])
    axB = fig.add_axes([L / W, bottom / H, fw, hb_ / H], sharex=axA)

    #  ---- (a) one pair, one instrument: an exact partition ----------------
    left = 0.0
    centres = []
    for (c, name, sty), v in zip(STRATA, parts):
        axA.barh([0], [v], left=[left], height=0.5, edgecolor="black",
                 linewidth=0.6, **sty)
        centres.append(left + v / 2)
        left += v
    axA.set_ylim(-1.05, 1.05)
    axA.set_xlim(0, 1)
    #  direct labels with leaders: two above the bar, two below, so the
    #  narrow segments at either end are named without crowding
    place = {0: ("above", "left"), 1: ("above", "center"),
             2: ("below", "right"), 3: ("above", "right")}
    short = {0: "split-involving", 1: "analyst choices",
             2: "register-quality counterfactual", 3: "mixed"}
    for k, (v, xc) in enumerate(zip(parts, centres)):
        side, al = place[k]
        sgn = 1 if side == "above" else -1
        axA.plot([xc, xc], [sgn * 0.25, sgn * 0.60], color="black", lw=0.6)
        axA.text(xc, sgn * 0.64, "%s %.1f%%" % (short[k], 100 * v),
                 ha=al, va="bottom" if side == "above" else "top",
                 fontsize=FIG_FONT, color="black")
    axA.axis("off")

    #  ---- (b) every pair, per stratum ------------------------------------
    ys = np.arange(len(STRATA))[::-1].astype(float)
    rng = np.random.default_rng(20260925)       # fixed, for the jitter only
    jit = rng.uniform(-0.14, 0.14, size=len(pp))
    is_case = np.array([i in case for i in pp.index])
    for y, (c, name, sty) in zip(ys, STRATA):
        v = pp[c].values
        axB.axhspan(y - 0.45, y + 0.45, color="0.95", lw=0, zorder=0)
        axB.scatter(v[~is_case], y + jit[~is_case], s=16, marker="o",
                    facecolors="black", edgecolors="black", linewidths=0.4,
                    zorder=3)
        axB.scatter(v[is_case], y + jit[is_case], s=26, marker="o",
                    facecolors="white", edgecolors="black", linewidths=0.9,
                    zorder=3)
        m = float(med[c])
        axB.plot([m, m], [y - 0.42, y + 0.42], color="black", lw=2.2,
                 solid_capstyle="butt", zorder=4)
        #  the median's value in the band above the points, clear of them
        axB.text(m + 0.010, y + 0.435, "median %.1f%%" % (100 * m),
                 ha="left", va="top", fontsize=FIG_FONT, zorder=5)
        #  a swatch of panel (a)'s fill beside the row label ties the two
        axB.add_patch(plt.Rectangle(
            (-0.075, y - 0.13), 0.05, 0.26, transform=axB.transData,
            clip_on=False, edgecolor="black", linewidth=0.5, **sty))
    axB.set_yticks(ys)
    axB.set_yticklabels([name for _, name, _ in STRATA], fontsize=FIG_FONT,
                        linespacing=1.0)
    axB.tick_params(axis="y", length=0, pad=34)
    axB.set_ylim(-0.5, len(STRATA) - 0.5)
    axB.set_xlim(0, 1)
    axB.set_xticks(np.linspace(0, 1, 6))
    axB.set_xticklabels(["%d%%" % t for t in range(0, 101, 20)])
    axB.tick_params(axis="x", labelsize=FIG_FONT, length=3)
    axB.set_xlabel("share of the variance of $V_s$", fontsize=FIG_FONT)
    for sp in ("top", "right", "left"):
        axB.spines[sp].set_visible(False)
    #  the key to the markers, where every row is empty
    from matplotlib.lines import Line2D
    keys = [Line2D([], [], ls="none", marker="o", ms=4, mfc="black",
                   mec="black", label="one pair (median over metrics)"),
            Line2D([], [], ls="none", marker="o", ms=5, mfc="white",
                   mec="black", mew=0.9,
                   label="the case study's two %s pairs" % REF_PAIR[0])]
    axB.legend(handles=keys, loc="lower right", frameon=True,
               fontsize=FIG_FONT, handletextpad=0.3, borderpad=0.3,
               facecolor="white", edgecolor="0.6", framealpha=1.0,
               bbox_to_anchor=(1.0, 0.08))

    fig.text(0.02 / W, (bottom + hb_ + mid + ha_) / H, "(a)", fontsize=9,
             fontweight="bold", va="top", ha="left")
    fig.text(0.02 / W, (bottom + hb_ + 0.02) / H, "(b)", fontsize=9,
             fontweight="bold", va="top", ha="left")
    fig.text((L - 0.10) / W, (bottom + hb_ + mid + ha_ / 2) / H,
             "%s / %s\nat %s" % (REF_PAIR[0], REF_PAIR[1],
                                 REF_METRIC.upper()),
             ha="right", va="center", fontsize=FIG_FONT)
    p = PAPER / "figS2_sobol.png"
    with plt.rc_context({"savefig.bbox": "standard"}):
        fig.savefig(p)
        fig.savefig(p.with_suffix(".pdf"))
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
    return save(fig, "figS3_regions")


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
    return save(fig, "figS4_dca")


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
    #  above the axes: inside them it overprinted the bars (2026-09-25)
    ax.legend(frameon=False, fontsize=6.4, ncol=3, loc="lower center",
              bbox_to_anchor=(0.5, 1.01))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    return save(fig, "figS6_coverage")


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
    return save(fig, "figS7_calibration")


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

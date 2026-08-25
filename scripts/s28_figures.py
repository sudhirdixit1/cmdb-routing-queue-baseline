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
    IDX = load("s22_indices.csv")
    SUM = load("s22_summary.csv")
    if IDX is None or SUM is None:
        return None
    pr = IDX[(IDX.scale == "raw-within-metric")
             & (IDX.measure == "equal-level")]
    if pr.empty:
        return None
    piv = (pr.groupby(["log", "target", "axis"]).S.median()
           .unstack("axis").fillna(0.0))
    s = SUM[(SUM.scale == "raw-within-metric") & (SUM.measure == "equal-level")]
    rem = (s.groupby(["log", "target"]).interaction_total.median()
           .reindex(piv.index).fillna(0.0))
    order = [c for c in ("split", "rung", "quality_level", "learner")
             if c in piv.columns]
    piv = piv[order]
    piv = piv.assign(_rem=rem.values).sort_values("_rem")
    fig, ax = plt.subplots(figsize=(6.6, 0.30 * len(piv) + 1.5))
    left = np.zeros(len(piv))
    shades = ["0.15", "0.38", "0.58", "0.76"]
    labels = {"rung": "baseline", "learner": "learner",
              "quality_level": "register quality", "split": "split"}
    for k, c in enumerate(order):
        ax.barh(range(len(piv)), piv[c].values, left=left,
                color=shades[k % len(shades)], edgecolor="white",
                linewidth=0.4, label=labels.get(c, c))
        left = left + piv[c].values
    ax.barh(range(len(piv)), piv._rem.values, left=left, color="white",
            edgecolor="0.25", linewidth=0.6, hatch="////",
            label="higher-order total")
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels(["%s / %s" % (a, b) for a, b in piv.index], fontsize=6.5)
    ax.set_xlabel("share of the variance of $V_s$, within instrument, "
                  "equal-level measure")
    #  ROUND TWENTY-TWO.  Each segment is a MEDIAN over instruments and
    #  medians do not add, so several bars sum to slightly more than one.  A
    #  fixed 1.02 limit clipped exactly the bars that show it.  The limit
    #  comes from the data now, a dotted rule marks one, and the caption
    #  says why the bars need not sum to it.
    _tot = float((piv[order].sum(axis=1) + piv._rem).max())
    ax.set_xlim(0, max(1.02, _tot * 1.02))
    ax.axvline(1.0, color="0.6", lw=0.6, ls=":", zorder=0)
    ax.legend(frameon=False, ncol=5, fontsize=6.2, loc="upper center",
              bbox_to_anchor=(0.5, -0.11))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
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
    G = load("s33_regions.csv")
    REG = load("s21_regions.csv")
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

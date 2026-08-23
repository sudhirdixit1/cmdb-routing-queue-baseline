"""s12 -- THE FIGURES.

Round nineteen.  The referee's last compliance item on the previous version's
graphics was blunt: "Replace the clipped, extremely dense Figure 1."  It was a
five-by-seven grid of cells each containing a clipped curve and a printed
number, and it was unreadable at print size.

Figure 1 is now a SPECIFICATION CURVE.  Every admissible cell of the primary
surface is one point, sorted by the increment; the panel below it says which
level of which axis each cell occupies.  A reader can see, in one glance,
where the sign changes and which choice changes it.  That is the paper's
claim, drawn.

    python s12_figures.py

Outputs: paper/figS1_speccurve.png, figS2_sobol.png, figS3_regions.png,
         figS4_dca.png, figS5_tipping.png, figS6_coverage.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

PAPER = HERE.parent / "paper"
plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6,
                     "figure.dpi": 200, "savefig.bbox": "tight"})

GREY = "0.35"
DARK = "0.15"


def load(n):
    p = RESULTS / n
    return pd.read_csv(p) if p.exists() else None


# --------------------------------------------------------------------------
def fig_speccurve():
    """FIGURE 1.  The specification curve for the primary log."""
    SUR = load("s01_surface.csv")
    if SUR is None:
        return None
    d = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
            & (~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
            & (SUR.metric.isin(list(S.SCALARS)))].copy()
    if d.empty:
        return None
    d["quality_level"] = (d.quality.astype(str)
                          + d.level.map(lambda x: "" if x == 1.0
                                        else "@%.2f" % x))
    d = d.sort_values("V").reset_index(drop=True)
    x = np.arange(len(d))

    AX = [("rung", "baseline"), ("learner", "learner"),
          ("metric", "metric"), ("quality_level", "register"),
          ("split", "split")]
    levels = []
    for col, _lab in AX:
        for lv in sorted(d[col].unique()):
            levels.append((col, lv))
    h = 2.6 + 0.10 * len(levels)
    fig, (ax0, ax1) = plt.subplots(
        2, 1, figsize=(7.0, h), sharex=True,
        gridspec_kw=dict(height_ratios=[2.2, 0.10 * len(levels) + 0.4],
                         hspace=0.05))

    pos = d.V.values > 0
    ax0.axhline(0, color=DARK, lw=0.8)
    ax0.scatter(x[pos], d.V.values[pos], s=3, color=DARK, marker="o",
                linewidths=0, label="increment $>0$")
    ax0.scatter(x[~pos], d.V.values[~pos], s=3, color="0.6", marker="x",
                linewidths=0.5, label="increment $\\leq 0$")
    ax0.set_ylabel("increment $V_s(f)$")
    ax0.legend(frameon=False, loc="upper left", fontsize=7)
    share = float(pos.mean())
    ax0.set_title("Every admissible specification for one register on one "
                  "log, sorted by the increment\n"
                  "(%d cells; %.0f%% positive, %.0f%% not)"
                  % (len(d), 100 * share, 100 * (1 - share)), fontsize=8.5)

    for i, (col, lv) in enumerate(levels):
        hit = (d[col].values == lv)
        ax1.scatter(x[hit], np.full(hit.sum(), len(levels) - i - 1), s=1.4,
                    color=DARK, marker="|", linewidths=0.5)
    ax1.set_yticks(range(len(levels)))
    ax1.set_yticklabels([("%s: %s" % (dict(AX)[c], str(v)))[:34]
                         for c, v in levels][::-1], fontsize=6)
    ax1.set_ylim(-0.6, len(levels) - 0.4)
    ax1.set_xlabel("specification, ordered by the increment")
    for a in (ax0, ax1):
        a.spines["top"].set_visible(False)
        a.spines["right"].set_visible(False)
    p = PAPER / "figS1_speccurve.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_sobol():
    SOB = load("s03_sobol.csv")
    if SOB is None:
        return None
    h = SOB[SOB.scale == "headroom"]
    if h.empty:
        return None
    piv = h.pivot_table(index=["log", "target"], columns="axis", values="S")
    piv = piv.fillna(0.0)
    order = ["rung", "learner", "quality_level", "metric", "split"]
    order = [c for c in order if c in piv.columns]
    piv = piv[order].sort_values(order[0])
    fig, ax = plt.subplots(figsize=(6.6, 0.28 * len(piv) + 1.4))
    left = np.zeros(len(piv))
    shades = ["0.15", "0.35", "0.55", "0.72", "0.87"]
    labels = {"rung": "baseline", "learner": "learner",
              "quality_level": "register quality", "metric": "metric",
              "split": "split"}
    for k, c in enumerate(order):
        ax.barh(range(len(piv)), piv[c].values, left=left,
                color=shades[k % len(shades)], edgecolor="white",
                linewidth=0.4, label=labels.get(c, c))
        left = left + piv[c].values
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels(["%s / %s" % (a, b) for a, b in piv.index], fontsize=6.5)
    ax.set_xlabel("first-order sensitivity index $S_i$ (headroom scale)")
    ax.set_xlim(0, 1)
    ax.legend(frameon=False, ncol=5, fontsize=6.5,
              loc="upper center", bbox_to_anchor=(0.5, -0.13))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = PAPER / "figS2_sobol.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_regions():
    REG = load("s03_regions.csv")
    if REG is None or REG.empty:
        return None
    d = REG.sort_values("rho")
    fig, ax = plt.subplots(figsize=(6.4, 0.28 * len(d) + 1.2))
    y = np.arange(len(d))
    ax.barh(y, d.rho.values, color=np.where(d.rho.values >= 0, DARK, "0.65"),
            height=0.6)
    ax.axvline(0, color="0.2", lw=0.8)
    ax.axvline(1, color="0.2", lw=0.6, ls=":")
    ax.set_yticks(y)
    ax.set_yticklabels(["%s / %s  (%s)" % (r.log, r.target, r.region)
                        for r in d.itertuples()], fontsize=6.5)
    ax.set_xlabel("robustness index $\\rho$   "
                  "($\\rho=1$: one number is safe)")
    ax.set_xlim(-1.05, 1.05)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = PAPER / "figS3_regions.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_dca():
    BN = load("s02_bands.csv")
    CE = load("s02_cells.csv")
    if BN is None or CE is None:
        return None
    sel = dict(log="BPIC14", target="handover", learner="logit",
               quality="clean", rung="B_intake_g")
    b = BN.copy()
    c = CE.copy()
    for k, v in sel.items():
        b = b[b[k] == v]
        c = c[c[k] == v]
    b = b[(b.family == "decision-curve")]
    c = c[c.metric.astype(str).str.startswith("nb_")]
    if b.empty or c.empty:
        return None
    b = b.assign(theta=b.metric.str.slice(3).astype(float)).sort_values("theta")
    c = c.assign(theta=c.metric.str.slice(3).astype(float)).sort_values("theta")
    m = b.merge(c[["theta", "lo", "hi"]], on="theta", how="left")
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    ax.axhline(0, color=DARK, lw=0.8)
    ax.fill_between(m.theta, 1000 * m.sim_lo, 1000 * m.sim_hi, color="0.85",
                    label="simultaneous max-$t$ band")
    ax.fill_between(m.theta, 1000 * m.lo, 1000 * m.hi, color="0.65",
                    label="pointwise 95\\% interval")
    ax.plot(m.theta, 1000 * m.V, color=DARK, lw=1.2, label="increment")
    ax.set_xlabel("operating point $\\theta$ "
                  "(exchange rate $\\theta/(1-\\theta)$)")
    ax.set_ylabel("net benefit increment\nper thousand arrivals")
    ax.legend(frameon=False, fontsize=7, loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = PAPER / "figS4_dca.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_tipping():
    T = load("s08_tipping.csv")
    L = load("s08_ladder.csv")
    if T is None or T.empty:
        return None
    fig, ax = plt.subplots(figsize=(5.4, 3.0))
    ax.plot(T.lambda_posthoc, T.V_auc, color=DARK, marker="o", ms=3, lw=1.1)
    if "sd" in T.columns:
        ax.fill_between(T.lambda_posthoc, T.V_auc - T.sd, T.V_auc + T.sd,
                        color="0.85")
    ax.axhline(0, color="0.3", lw=0.8)
    if L is not None and len(L):
        g = L[L.baseline == "intake + group"]
        if len(g):
            ax.axhline(float(g.V_auc.iloc[0]), color="0.4", lw=0.8, ls="--")
            ax.text(0.02, float(g.V_auc.iloc[0]),
                    " value at $\\tau_2$ without the knowledge reference",
                    va="bottom", fontsize=6.5, color="0.3")
    ax.set_xlabel("$\\lambda$: share of knowledge references assumed post-hoc")
    ax.set_ylabel("increment of the register (AUC)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = PAPER / "figS5_tipping.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig_coverage():
    C = load("s10_coverage.csv")
    if C is None or C.empty:
        return None
    d = C[C.estimand == "V_limit"]
    worlds = list(dict.fromkeys(d.world))
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    w = 0.36
    x = np.arange(len(worlds))
    for k, kind in enumerate(("naive", "nested")):
        v = [float(d[(d.world == wd) & (d.interval == kind)].coverage.iloc[0])
             for wd in worlds]
        ax.bar(x + (k - 0.5) * w, v, width=w,
               color=DARK if kind == "nested" else "0.7",
               label="nested (refit)" if kind == "nested"
               else "fixed-model")
    ax.axhline(0.95, color="0.2", lw=0.8, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(worlds, rotation=20, ha="right")
    ax.set_ylabel("coverage of $V_{\\mathrm{limit}}$")
    ax.set_ylim(0.6, 1.02)
    ax.legend(frameon=False, fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = PAPER / "figS6_coverage.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def main():
    made = []
    for fn in (fig_speccurve, fig_sobol, fig_regions, fig_dca, fig_tipping,
               fig_coverage):
        try:
            p = fn()
        except Exception as e:  # noqa: BLE001
            print("  %-16s FAILED %s" % (fn.__name__, e))
            continue
        if p is None:
            print("  %-16s skipped: source not generated yet" % fn.__name__)
        else:
            print("  %-16s -> %s" % (fn.__name__, p.name))
            made.append(p)
    print("%d figures written" % len(made))


if __name__ == "__main__":
    main()

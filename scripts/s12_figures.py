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
         -- and, beside each PNG, a vector PDF of the same name.  The journal
         asks for vector art; the PNG stays because other documents embed it.
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
#  pdf.fonttype 42 embeds the text as TrueType so it stays text in the vector
#  file (type 3, the default, outlines every glyph and production cannot
#  search or re-set it).
plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6,
                     "figure.dpi": 400, "savefig.bbox": "tight",
                     "pdf.fonttype": 42, "ps.fonttype": 42})

GREY = "0.35"
DARK = "0.15"


def load(n):
    """Read a result file, compressed or not; None if it is missing or is an
    empty placeholder."""
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


# --------------------------------------------------------------------------
#  IJF PRINT GEOMETRY.  The article's text block is 468 TeX points wide
#  (elsarticle 3p), and every figure is included at \textwidth.  Figures 1-3
#  are drawn AT that width, on a fixed canvas (no tight bounding box), so
#  they print at 1:1 and a font size set here is the size on the page.
TEXTWIDTH_IN = 468.0 / 72.27
FIG_FONT = 8.0          # every label, tick and legend in Figures 1-3


def save_fixed(fig, stem):
    """Like save(), but on the fixed canvas: the PDF is exactly the figure
    size, so \\includegraphics[width=\\textwidth] prints it unscaled."""
    p = PAPER / (stem + ".png")
    with plt.rc_context({"savefig.bbox": "standard"}):
        fig.savefig(p)
        fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    return p


#  Human labels for panel (b).  The level of a mask_* condition is the share
#  of rows that stay POPULATED (spec.degrade); corrupt's is the share of rows
#  given a wrong identity, duplicate's the share of identities split in two.
FIG1_LEVEL_LABEL = {
    ("rung", "B_half"): "half the arrival attributes",
    ("rung", "B_intake"): "arrival attributes",
    ("rung", "B_intake_g"): "arrival + team",
    ("rung", "B_intake_g_km"): "arrival + team + article ref.",
    ("learner", "logit"): "logistic, one-hot",
    ("learner", "logit_fr"): "logistic, frequency enc.",
    ("learner", "hgb"): "boosting, target enc.",
    ("learner", "hgb_iso"): "boosting, isotonic",
    ("split", "holdout70"): "single holdout",
}
FIG1_QUALITY_LABEL = {
    "clean": "clean",
    "stale": "stale",
    "corrupt": "wrong item, %d%% of rows",
    "duplicate": "duplicated, %d%% of items",
    "mask_rare": "rare items absent, %d%% filled",
    "mask_common": "common items absent, %d%% filled",
    "mask_random": "absent at random, %d%% filled",
}
#  Figure 1 draws the primary instrument only.  The five scalar instruments
#  are not on a common scale (Remark prop:nonid), so one axis cannot carry
#  them; AUC is the instrument every other table reports first.
FIG1_METRICS = ("auc",)


def _fig1_quality(kind, level):
    fmt = FIG1_QUALITY_LABEL.get(kind, kind)
    return fmt % round(100 * level) if "%d" in fmt else fmt


def fig_speccurve():
    """FIGURE 1.  The specification curve for the case-study pair, at AUC.

    Drawn at the article's text width with 8-point text.  (a) the sorted
    increments, the sign carried by the marker's FILL (filled > 0, open <= 0)
    rather than by a grey level, so the non-positive cells are as visible as
    the rest in greyscale print.  (b) for each level of each varied axis, the
    share of the cells in each sorted bin that sit at that level -- an
    occupancy map, rows grouped by axis with the axis named once.
    """
    SUR = load("s01_surface.csv")
    if SUR is None:
        return None
    d = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
            & (~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
            & (SUR.metric.isin(list(FIG1_METRICS)))].copy()
    if d.empty:
        return None
    d["quality_level"] = list(zip(d.quality.astype(str),
                                  d.level.astype(float)))
    d = d.sort_values("V", kind="mergesort").reset_index(drop=True)
    n = len(d)
    x = np.arange(n)
    V = d.V.values
    pos = V > 0
    share = float(pos.mean())
    n_neg = int((~pos).sum())

    #  groups of panel (b), top to bottom
    GROUPS = [("rung", "baseline"), ("learner", "learner"),
              ("quality_level", "register"), ("split", "split")]

    def _levels(col):
        lv = sorted(d[col].unique())
        if col == "quality_level":   # clean first, then by kind and level
            lv = sorted(lv, key=lambda t: (t[0] != "clean", t[0] == "stale",
                                           t[0], t[1]))
        if col == "split":           # holdout, then the folds in order
            lv = sorted(lv, key=lambda s: (s != "holdout70", s))
        return lv

    def _label(col, v):
        if col == "quality_level":
            return _fig1_quality(*v)
        if col == "split" and str(v).startswith("rolling"):
            return "expanding fold %s" % str(v)[len("rolling"):]
        return FIG1_LEVEL_LABEL.get((col, v), str(v))

    rows = []            # (y, group index, column, level)
    y = 0.0
    GAP = 0.7
    for g, (col, _name) in enumerate(GROUPS):
        for lv in _levels(col):
            rows.append((y, g, col, lv))
            y += 1.0
        y += GAP
    y_top = y - GAP      # rows occupy [0, y_top)

    #  occupancy: the share of each bin's cells at each level
    BIN = 20
    edges = np.arange(0, n + BIN, BIN)
    edges[-1] = n
    b = np.minimum(x // BIN, len(edges) - 2)
    nb = np.bincount(b, minlength=len(edges) - 1).astype(float)

    #  ---- fixed canvas, in inches ------------------------------------------
    W = TEXTWIDTH_IN
    PITCH = 0.126                          # inches per row of panel (b)
    hb = PITCH * y_top
    ha = 1.55
    bottom, mid, top = 0.62, 0.20, 0.08
    H = bottom + hb + mid + ha + top
    L, R = 2.22, 0.08
    fig = plt.figure(figsize=(W, H))
    fw = (W - L - R) / W
    ax0 = fig.add_axes([L / W, (bottom + hb + mid) / H, fw, ha / H])
    ax1 = fig.add_axes([L / W, bottom / H, fw, hb / H], sharex=ax0)

    #  ---- (a) the curve --------------------------------------------------
    ax0.axhline(0, color="black", lw=0.7, zorder=1)
    ax0.scatter(x[pos], V[pos], s=7, marker="o", facecolors="black",
                edgecolors="black", linewidths=0.4, zorder=3,
                label="increment $>0$: %.0f%% of cells" % (100 * share))
    ax0.scatter(x[~pos], V[~pos], s=7, marker="o", facecolors="white",
                edgecolors="black", linewidths=0.5, zorder=3,
                label="increment $\\leq 0$: %.0f%% (%d cells)"
                % (100 * (1 - share), n_neg))
    ax0.set_ylabel("AUC increment $V_s(f)$", fontsize=FIG_FONT)
    #  the non-positive cells are the finding, so their stretch of the curve
    #  is shaded as well as drawn open, and the legend sits clear of it
    ax0.axvspan(-0.5, n_neg - 0.5, color="0.86", lw=0, zorder=0)
    ax0.legend(frameon=False, loc="upper left", fontsize=FIG_FONT,
               bbox_to_anchor=((n_neg + 12) / n, 1.0),
               handletextpad=0.3, borderaxespad=0.2, markerscale=1.6)
    ax0.tick_params(labelsize=FIG_FONT, labelbottom=False, length=3)
    ax0.set_xlim(-0.5, n - 0.5)
    for a in (ax0, ax1):
        a.axvline(n_neg - 0.5, color="black", lw=0.6, ls=(0, (3, 2)),
                  zorder=4)

    #  ---- (b) the occupancy map ------------------------------------------
    import matplotlib.colors as mcolors
    cmap = plt.get_cmap("Greys")
    norm = mcolors.Normalize(vmin=0.0, vmax=1.0)
    for yy, g, col, lv in rows:
        hit = (d[col].values == lv) if col != "quality_level" else \
            np.array([t == lv for t in d[col].values])
        occ = np.bincount(b[hit], minlength=len(nb)) / nb
        ax1.pcolormesh(edges - 0.5, [yy + 0.06, yy + 0.94],
                       occ[None, :], cmap=cmap, norm=norm,
                       shading="flat", rasterized=False, linewidth=0,
                       edgecolors="face")
    #  separators between axis groups, and each group named once
    trans = ax1.get_yaxis_transform()
    starts = {}
    for yy, g, col, lv in rows:
        starts.setdefault(g, [yy, yy])
        starts[g][1] = yy + 1.0
    for g, (y0, y1) in starts.items():
        if g > 0:
            ax1.axhline(y0 - GAP / 2, color="black", lw=0.5, xmin=0,
                        xmax=1, clip_on=False, zorder=5)
        ax1.text((0.10 - L) / (W - L - R), (y0 + y1) / 2, GROUPS[g][1],
                 transform=trans, ha="center", va="center", rotation=90,
                 fontsize=FIG_FONT, fontweight="bold")
        ax1.plot([(0.20 - L) / (W - L - R)] * 2, [y0 + 0.1, y1 - 0.1],
                 transform=trans, color="black", lw=0.6, clip_on=False)
    ax1.set_yticks([yy + 0.5 for yy, *_ in rows])
    ax1.set_yticklabels([_label(col, lv) for _, _, col, lv in rows],
                        fontsize=FIG_FONT)
    ax1.set_ylim(y_top + 0.05, -0.05)      # first group at the top
    ax1.tick_params(axis="y", length=0, pad=3)
    ax1.tick_params(axis="x", labelsize=FIG_FONT, length=3)
    ax1.set_xlabel("specification (%d cells), ordered by the increment"
                   % n, fontsize=FIG_FONT)
    for a in (ax0, ax1):
        a.spines["top"].set_visible(False)
        a.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)

    #  the key to the greys, under panel (b)'s labels, at the left
    cax = fig.add_axes([0.10 / W, 0.20 / H, 1.10 / W, 0.07 / H])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                      orientation="horizontal", ticks=[0, 0.5, 1])
    cb.ax.tick_params(labelsize=FIG_FONT, length=2, pad=1)
    cb.outline.set_linewidth(0.5)
    cb.ax.set_xticklabels(["0", "0.5", "1"])
    fig.text(0.02 / W, 0.43 / H, "grey: share of a bin's %d cells\n"
             "at that level" % BIN, ha="left", va="center",
             fontsize=FIG_FONT, linespacing=1.1)

    #  panel letters in the left margin, level with the top of each panel
    fig.text(0.02 / W, (bottom + hb + mid + ha) / H, "(a)", fontsize=9,
             fontweight="bold", va="top", ha="left")
    fig.text(0.02 / W, (bottom + hb + mid) / H, "(b)", fontsize=9,
             fontweight="bold", va="top", ha="left")
    return save_fixed(fig, "figS1_speccurve")


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
    return save(fig, "figS2_sobol")


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
    return save(fig, "figS3_regions")


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
                    label="pointwise 95% interval")   # matplotlib, not LaTeX
    ax.plot(m.theta, 1000 * m.V, color=DARK, lw=1.2, label="increment")
    ax.set_xlabel("operating point $\\theta$ "
                  "(exchange rate $\\theta/(1-\\theta)$)")
    ax.set_ylabel("net benefit increment\nper thousand arrivals")
    ax.legend(frameon=False, fontsize=7, loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "figS4_dca")


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
    return save(fig, "figS5_tipping")


def fig_coverage():
    C = load("s10_coverage.csv")
    if C is None or C.empty:
        return None
    d = C[C.estimand == "V_limit"]
    worlds = list(dict.fromkeys(d.world))
    KINDS = [("naive_pct", "fixed-model, percentile", "0.78"),
             ("nested_pct", "nested, percentile", "0.55"),
             ("nested_basic", "nested, basic (used)", DARK)]
    KINDS = [k for k in KINDS if (d.interval == k[0]).any()]
    if not KINDS:
        KINDS = [("naive", "fixed-model", "0.7"), ("nested", "nested", DARK)]
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    w = 0.8 / len(KINDS)
    x = np.arange(len(worlds))
    for k, (kind, lab, col) in enumerate(KINDS):
        v = [float(d[(d.world == wd) & (d.interval == kind)].coverage.iloc[0])
             if len(d[(d.world == wd) & (d.interval == kind)]) else np.nan
             for wd in worlds]
        ax.bar(x + (k - (len(KINDS) - 1) / 2.0) * w, v, width=w,
               color=col, label=lab)
    ax.axhline(0.95, color="0.2", lw=0.8, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(worlds, rotation=20, ha="right")
    ax.set_ylabel("coverage of $V_{\\mathrm{limit}}$")
    #  The floor is derived, not chosen.  A fixed 0.6 clipped the sparse
    #  world's nested percentile bar -- 0.420, the single most important
    #  number in this figure -- to nothing, so the one construction the
    #  figure exists to indict was the one a reader could not see.
    lo = float(np.nanmin([b for b in
                          [float(d[(d.world == wd) & (d.interval == kind)]
                                 .coverage.iloc[0])
                           for wd in worlds for kind, _l, _c in KINDS
                           if len(d[(d.world == wd) & (d.interval == kind)])]
                          ]))
    ax.set_ylim(max(0.0, lo - 0.06), 1.02)
    ax.legend(frameon=False, fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "figS6_coverage")


def main():
    made = []
    #  fig_sobol is NOT run here: Figure 3 (figS2_sobol) is drawn by
    #  s28_figures.fig_sobol, and running this older pooled version on its
    #  own would overwrite the article's figure with a withdrawn design.
    for fn in (fig_speccurve, fig_regions, fig_dca, fig_tipping,
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

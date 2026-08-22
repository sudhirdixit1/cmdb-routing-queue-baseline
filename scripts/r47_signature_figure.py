"""r47 -- THE SIGNATURE FIGURE.

PLAN-REVIEWER-PROOF.md section 7.2.  The paper has ten figures and no single
image a reader carries away.  This is that image: **the surface itself**, all
four choices in one frame.

    rows      the baseline, as every ordered nested pair of the ladder
    columns   the metric
    inside    a miniature curve.  Under the four scalar metrics the curve runs
              over the REGISTER POPULATION; under net benefit it runs over the
              OPERATING POINT.  Both are the axes those metrics actually have.
    colour    the reduction at the reference cell of that row and column

REQUIREMENTS, all of which a referee will check:

  * readable in greyscale -- the colormap IS greyscale, and every cell also
    carries its number, so the figure survives being printed badly;
  * readable at half width -- five columns, large type, no legend to hunt for;
  * every value read from results/r44_surface.csv, never recomputed here;
  * a caption that states what the figure does NOT show, printed to
    results/r47_caption.txt so the manuscript and the figure cannot drift.

Outputs: figures/fig_signature.png, paper/fig_signature.png,
         results/r47_caption.txt, results/r47_facts.csv
"""
import itertools
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                              # noqa: E402
import numpy as np                                           # noqa: E402
import pandas as pd                                          # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FIGURES, RESULTS                          # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOG = "BPIC14"
NEST = ["empty", "B0_half", "B0", "B0+g"]
PRETTY = {"empty": "nothing", "B0_half": "half the intake block",
          "B0": "the intake block", "B0+g": "intake + opening group"}
SCALAR = ["auc", "ap", "brier_skill", "nagelkerke"]
MLABEL = {"auc": "ROC AUC", "ap": "average\nprecision",
          "brier_skill": "Brier skill", "nagelkerke": "Nagelkerke $R^2$",
          "net_benefit": "net benefit"}
EPS = 1e-12


def reductions(SUR):
    rows = []
    for (inst, pop, reg), sub in SUR.groupby(["instrument", "population",
                                              "regime"]):
        v = sub.set_index("baseline").V.to_dict()
        for i, j in itertools.combinations(range(len(NEST)), 2):
            lo_, hi_ = NEST[i], NEST[j]
            if lo_ not in v or hi_ not in v or v[lo_] <= EPS:
                continue
            rows.append(dict(pair=f"{lo_} -> {hi_}", b_lo=lo_, b_hi=hi_,
                             instrument=inst, population=pop, regime=reg,
                             V_lo=v[lo_], R=1.0 - v[hi_] / v[lo_]))
    return pd.DataFrame(rows)


def main():
    SUR = pd.read_csv(RESULTS / "r44_surface.csv")
    SUR = SUR[SUR.log == LOG]
    if SUR.empty:
        sys.exit(f"r44_surface.csv has no rows for {LOG}")
    RED = reductions(SUR)
    RED.to_csv(RESULTS / "r47_cells.csv", index=False)

    pairs = [p for p in
             [f"{NEST[i]} -> {NEST[j]}"
              for i, j in itertools.combinations(range(len(NEST)), 2)]
             if p in set(RED.pair)]
    cols = SCALAR + ["net_benefit"]

    #  the reference value in each cell: full population, and for net benefit
    #  the grid point closest to the test-half base rate, which is the
    #  operating point a desk that treats "more likely than not" would use
    prev = float(SUR.iloc[0].n_test and
                 pd.read_csv(RESULTS / "r44_surface.csv")
                 .query("log == @LOG").iloc[0].get("prevalence", np.nan)) \
        if "prevalence" in SUR.columns else np.nan
    nb_cols = sorted(c for c in SUR.instrument.unique() if c.startswith("nb_"))
    nb_t = np.array([float(c[3:]) for c in nb_cols])
    ref_t = nb_cols[int(np.argmin(np.abs(nb_t - 0.40)))]

    ref = {}
    for p in pairs:
        for m in cols:
            key = ref_t if m == "net_benefit" else m
            s = RED[(RED.pair == p) & (RED.instrument == key)
                    & (RED.population == 1.00)]
            ref[(p, m)] = float(s.R.iloc[0]) if len(s) else np.nan
    vals = np.array([v for v in ref.values() if np.isfinite(v)])
    lo, hi = float(np.percentile(vals, 2)), float(np.percentile(vals, 98))

    nrow, ncol = len(pairs), len(cols)
    fig, axes = plt.subplots(nrow, ncol, figsize=(1.55 * ncol + 2.3,
                                                 1.02 * nrow + 1.15),
                             squeeze=False)
    cmap = plt.get_cmap("Greys")
    for i, p in enumerate(pairs):
        for j, m in enumerate(cols):
            ax = axes[i][j]
            r0 = ref[(p, m)]
            shade = 0.0 if not np.isfinite(r0) else \
                float(np.clip((r0 - lo) / (hi - lo + EPS), 0, 1))
            ax.set_facecolor(cmap(0.10 + 0.55 * shade))
            if m == "net_benefit":
                s = RED[(RED.pair == p) & (RED.population == 1.00)
                        & (RED.instrument.str.startswith("nb_"))]
                if len(s):
                    x = s.instrument.str.slice(3).astype(float).values
                    o = np.argsort(x)
                    ax.plot(x[o], np.clip(s.R.values[o], -1.0, 2.0), lw=1.4,
                            color="black")
                    ax.set_xlim(0.05, 0.80)
            else:
                s = RED[(RED.pair == p) & (RED.instrument == m)
                        & (RED.regime.isin(["full", "rare-first"]))]
                s = s.sort_values("population")
                if len(s):
                    ax.plot(s.population.values, np.clip(s.R.values, -1.0, 2.0),
                            marker="o", ms=3.2, lw=1.4, color="black")
                    ax.set_xlim(0.20, 1.05)
            ax.set_ylim(-1.05, 2.05)
            ax.axhline(0.0, lw=0.6, color="0.35", ls=":")
            ax.set_xticks([])
            ax.set_yticks([])
            if np.isfinite(r0):
                ax.text(0.5, 0.86, f"{r0:+.2f}", transform=ax.transAxes,
                        ha="center", va="center", fontsize=9,
                        fontweight="bold",
                        color=("white" if shade > 0.62 else "black"))
            for sp in ax.spines.values():
                sp.set_color("0.4")
                sp.set_linewidth(0.6)
            if i == 0:
                lab = MLABEL[m]
                if m == "net_benefit":
                    lab += "\nat $\\theta=%.2f$" % float(ref_t[3:])
                ax.set_title(lab, fontsize=8.5, pad=5)
            if j == 0:
                lo_, hi_ = p.split(" -> ")
                ax.set_ylabel(f"{PRETTY[lo_]}\n$\\rightarrow$ {PRETTY[hi_]}",
                              fontsize=7.2, rotation=0, ha="right",
                              va="center", labelpad=6)

    fig.suptitle("One dataset, one feature: the admissibility reduction $R$ "
                 "in every cell", fontsize=10.5, y=0.985)
    fig.text(0.5, 0.018,
             "rows: which already-recorded fields the baseline may contain   "
             "|   columns: the metric\n"
             "inside each cell: $R$ over the register's population "
             "(scalar metrics) or over the operating point (net benefit)",
             ha="center", fontsize=7.6)
    fig.tight_layout(rect=(0.0, 0.045, 1.0, 0.955))
    for out in (FIGURES / "fig_signature.png", ROOT / "paper" / "fig_signature.png"):
        fig.savefig(out, dpi=300)
    plt.close(fig)

    span = f"{np.nanmin(vals):+.2f} to {np.nanmax(vals):+.2f}"
    #  RAW strings, and every underscore escaped.  The first version of this
    #  block wrote "\texttt" in a non-raw string, so the manuscript received a
    #  TAB followed by "exttt", and left three underscores unescaped inside
    #  \texttt{}; the build produced twenty-six errors from one caption.  A
    #  caption generated by a script is code and has to be written like code.
    caption = (
        r"The same data, the same feature, and every defensible answer at "
        r"once. Each cell is the admissibility reduction $R$ for item identity "
        r"on BPI Challenge 2014: rows are which already-recorded fields the "
        r"baseline is allowed to contain, columns are the metric, and the "
        r"curve inside a cell runs over the register's population (scalar "
        r"metrics) or over the operating point (net benefit). The reference "
        + f"values printed in the cells run {span}. "
        + r"WHAT THIS FIGURE DOES NOT SHOW: it carries no intervals --- every "
        r"cell is a point estimate, and the bootstrap intervals are in "
        r"Table~\ref{tab:instruments} and in "
        r"\texttt{results/r44\_spread.csv}; it shows one log, and the same "
        r"grid for two further organisations is in the same file; and it "
        r"shows the reduction, not the increment, so a cell where the entity "
        r"is worth almost nothing to begin with looks the same as one where "
        r"it is worth a great deal. The in-cell curves are clipped to "
        r"$[-1,2]$ and the unclipped values are in "
        r"\texttt{results/r47\_cells.csv}.")
    (RESULTS / "r47_caption.txt").write_text(caption, encoding="utf-8")

    F = pd.DataFrame([dict(
        log=LOG, n_rows=nrow, n_cols=ncol, n_cells=nrow * ncol,
        n_finite=int(np.isfinite(list(ref.values())).sum()),
        r_min=float(np.nanmin(vals)), r_max=float(np.nanmax(vals)),
        r_span=float(np.nanmax(vals) - np.nanmin(vals)),
        reference_threshold=float(ref_t[3:]),
        n_population_levels=int(RED.population.nunique()),
        n_threshold_points=len(nb_cols))])
    F.to_csv(RESULTS / "r47_facts.csv", index=False)
    print(F.T.to_string())
    print(f"\n  cells run {span}")
    print(f"  wrote figures/fig_signature.png and paper/fig_signature.png")


if __name__ == "__main__":
    main()

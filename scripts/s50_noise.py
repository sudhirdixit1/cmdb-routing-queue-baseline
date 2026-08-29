"""s50 -- HOW A CELL'S OWN UNCERTAINTY COMPARES WITH THE SPREAD ACROSS CELLS.

READ THIS FIRST.  The file was written to bound how much of the
decomposition's variance is estimation error, and IT DOES NOT DO THAT.  Its
`share_correlated' column exceeds one on 7 of the 13 pairs it was first run
on, which is impossible for a share of a variance and is the file telling its
author the quantity was ill-posed.  The reason is worth more than the number
would have been, and it is this:

    sigma-hat comes from the NESTED bootstrap, which resamples the TRAINING
    half as well as the test half, because this paper's estimand deliberately
    contains training-sample variability (Section 4.1).  The cross-cell
    variance the decomposition partitions is computed at FIXED training data
    --- it is the spread across specifications ON ONE DATASET.  So the two are
    not commensurable, and their ratio is not a noise share.

Answering the original question needs a FIXED-TRAINING standard error, which
is a different resampling scheme and a separate run.  Until that exists,
nothing in this file may be quoted as a share of the decomposition, and no
macro reads it.

WHAT IT DOES SUPPORT, and what is worth carrying: the comparison of a cell's
own standard error against the standard deviation across cells.  Both are in
the metric's own units, neither needs a decomposition model, and the answer is
stark on the small logs --- a single specification's standard error is larger
than the entire spread across specifications.  That is a statement about which
uncertainty dominates, and it corroborates from a second direction what
Section 6.3 already reports as scarcity of resolved cells: on most of this
corpus, WHICH specification you choose moves the answer less than not knowing
the answer does.

The original derivation is kept below because the mistake in it is instructive
and because the arithmetic is right for what it computes.

--- ORIGINAL HEADER, superseded by the note above ---

HOW MUCH OF THE SURFACE'S VARIANCE IS ESTIMATION ERROR.

Round twenty-seven.  Round twenty-six made the split an error stratum, which
removes BETWEEN-FOLD variation from the analyst-choice share.  It does not
remove WITHIN-CELL estimation error: every $V_s$ is estimated on a finite
test half, and that error is still inside the decomposition, spread across
every component including `analyst choice'.  So "analyst latitude carries
13.3% of the variance" is an UPPER BOUND, and a referee who notices that the
paper corrected one noise source and not the other has a fair objection --
the more so because separating noise from latitude is this paper's own
headline contribution.

WHAT THIS FILE COMPUTES, AND WHAT IT DOES NOT.  It is a bound, not a fourth
reporting object.  The project's own rule is that an object reporting a null
is a check and not a result, and this one exists to make an existing number
honest rather than to add one.

THE ARITHMETIC, STATED SO IT CAN BE CHECKED.  Write the observed increment at
cell $c$ as $V_c = \\theta_c + \\varepsilon_c$, where $\\theta_c$ is what the
cell would give with infinite test data and $\\varepsilon_c$ is estimation
error.  The quantity the decomposition is taken over is the spread of $V$
ACROSS CELLS, and its expectation separates:

    E[ (1/n) sum_c (V_c - Vbar)^2 ]
        =  (1/n) sum_c (theta_c - thetabar)^2        <- the signal
         +  sigmabar^2 - (1/n^2) sum_c sum_c' cov(eps_c, eps_c')

The cells share a test half, so their errors are strongly correlated, and
that correlation is what keeps the noise term small: with a common standard
error and a common correlation rho the second line is sigmabar^2 (1 - rho) to
order 1/n.  Independent noise would contribute sigmabar^2; correlated noise
contributes a fraction (1 - rho) of it.  Both are computed here, because the
gap between them is the whole reason the bound is not alarming.

WHY THE CORRELATION IS MEASURED AND NOT ASSUMED.  A draw is a resample of the
data every cell is evaluated on, so the draw-to-draw movement of two cells is
correlated by construction, and the size of that correlation is a property of
the pair rather than a constant.  It is estimated from the bootstrap draws
themselves -- the same draws the bands are built from -- so the bound costs no
refits.

WHAT IT IS NOT.  It is not a correction to the decomposition: the components
are not re-estimated, and nothing in Section 6.2's table moves.  It bounds how
much of the variance those components partition could be estimation error, so
that a share can be read as "at most this much of me is noise" rather than as
a clean signal.  A bound stated once is worth more than an adjustment nobody
can check.

    python s50_noise.py --draws-dir s44_weighted

Outputs: results/s50_noise.csv    one row per (pair, instrument)
         results/s50_facts.csv
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

#: the reference rung is excluded from no admissible set, but the
#: intercept-only rung is not present in the designed surface at all, so no
#: exclusion is needed here.  Stated so a reader does not go looking for one.
INSTRUMENTS = ("auc", "ap", "brier_skill", "nagelkerke", "logloss_skill")


def one_pair(df: pd.DataFrame, metric: str) -> dict | None:
    """The bound for one (pair, instrument).

    `df` carries every draw of every cell for one log--target pair.  Draw -1
    is the point estimate: it is the observed surface, and it is what the
    decomposition is computed on, so it supplies the denominator.  Draws 0 and
    up are the bootstrap and supply the standard errors and the correlation.
    """
    d = df[df.metric == metric]
    if d.empty:
        return None
    cell = ["learner", "split", "quality", "level", "rung"]
    point = d[d.draw < 0]
    boot = d[d.draw >= 0]
    if len(point) < 3 or boot.empty:
        return None

    #  the denominator: the cross-cell variance the decomposition partitions
    var_surface = float(np.var(point.V.values, ddof=0))
    if not np.isfinite(var_surface) or var_surface <= 0:
        return None

    #  a cell-by-draw matrix.  Cells with a draw missing are dropped rather
    #  than filled: a filled cell would contribute a correlation it did not
    #  earn, and this is a bound, so the honest direction is to compute it on
    #  the cells that have the evidence.
    W = boot.pivot_table(index="draw", columns=cell, values="V",
                         aggfunc="mean")
    W = W.dropna(axis=1, how="any")
    if W.shape[1] < 3 or W.shape[0] < 8:
        return None

    se = W.std(axis=0, ddof=1).values            # one standard error per cell
    sigma2 = float(np.mean(se ** 2))

    #  the mean off-diagonal correlation of the cells' draw vectors
    C = np.corrcoef(W.values, rowvar=False)
    n = C.shape[0]
    off = ~np.eye(n, dtype=bool)
    rho = float(np.nanmean(C[off]))
    if not np.isfinite(rho):
        rho = 0.0

    #  the two bounds.  `independent' is what a reader who ignored the shared
    #  test half would compute, and it is reported because the gap between the
    #  two is the point.
    noise_independent = sigma2
    noise_correlated = sigma2 * (1.0 - rho)
    return dict(
        metric=metric,
        n_cells=int(n),
        n_draws=int(W.shape[0]),
        var_surface=var_surface,
        mean_se=float(np.mean(se)),
        sigma2=sigma2,
        rho_mean=rho,
        noise_independent=noise_independent,
        noise_correlated=noise_correlated,
        share_independent=noise_independent / var_surface,
        share_correlated=noise_correlated / var_surface,
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws-dir", default="s44_weighted",
                    help="the directory under results/ holding the draw files")
    a = ap.parse_args(argv)
    t0 = time.time()
    src = RESULTS / a.draws_dir
    files = sorted(src.glob("draws_*.csv.gz"))
    if not files:
        raise SystemExit("no draw files in %s -- has s44 finished?" % src)

    rows = []
    for fn in files:
        df = pd.read_csv(fn)
        #  a draw count far below the declared one means a smoke run, and a
        #  bound computed on four draws is not a bound.  Refuse rather than
        #  print, because a number this file prints will be quoted.
        if df.draw.max() < 30:
            print("  SKIP %-34s only %d draws -- smoke run?"
                  % (fn.name, int(df.draw.max()) + 1))
            continue
        log = str(df.log.iloc[0])
        target = str(df.target.iloc[0])
        for m in INSTRUMENTS:
            r = one_pair(df, m)
            if r:
                rows.append(dict(log=log, target=target, **r))
        print("  %-20s %-9s %d instruments" % (log, target,
                                               sum(1 for r in rows
                                                   if r["log"] == log
                                                   and r["target"] == target)))

    if not rows:
        raise SystemExit("no pair carried enough draws; nothing written")

    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "s50_noise.csv", index=False)

    #  the headline is the median over pairs of the median over instruments,
    #  which is the aggregation Section 6.2 uses for the decomposition, so the
    #  bound is on the same scale as the number it bounds.
    per_pair = D.groupby(["log", "target"])[
        ["share_correlated", "share_independent", "rho_mean"]].median()
    facts = dict(
        n_pairs=int(per_pair.shape[0]),
        n_rows=int(len(D)),
        draws_dir=a.draws_dir,
        share_correlated_median=float(per_pair.share_correlated.median()),
        share_correlated_max=float(per_pair.share_correlated.max()),
        share_correlated_min=float(per_pair.share_correlated.min()),
        share_independent_median=float(per_pair.share_independent.median()),
        rho_median=float(per_pair.rho_mean.median()),
        rho_min=float(per_pair.rho_mean.min()),
        n_above_tenth=int((per_pair.share_correlated > 0.10).sum()),
        n_above_quarter=int((per_pair.share_correlated > 0.25).sum()),
        runtime_s=round(time.time() - t0, 1),
    )
    pd.DataFrame([facts]).to_csv(RESULTS / "s50_facts.csv", index=False)

    print()
    print("  cross-cell variance that is estimation error, per pair:")
    print("    median %.1f%%   min %.1f%%   max %.1f%%"
          % (100 * facts["share_correlated_median"],
             100 * facts["share_correlated_min"],
             100 * facts["share_correlated_max"]))
    print("    (ignoring the shared test half it would be %.1f%% -- the gap"
          % (100 * facts["share_independent_median"]))
    print("     is the correlation, median %.3f)" % facts["rho_median"])
    print("  pairs above a tenth: %d   above a quarter: %d"
          % (facts["n_above_tenth"], facts["n_above_quarter"]))
    print("  wrote s50_noise.csv, s50_facts.csv in %.1fs"
          % facts["runtime_s"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

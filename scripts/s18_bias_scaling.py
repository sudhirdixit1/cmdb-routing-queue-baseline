"""s18 -- THE TWO FINITE-SAMPLE EXPLANATIONS, BOTH REFUTED.

Round nineteen.  s10 measures coverage against two estimands in six simulated
worlds.  s17's basic interval repairs the failure it was built for --- on the
SPARSE world the nested percentile interval covers 0.42 and the basic one
covers 0.93 --- and on the NOISY world every construction still failed, 0.04
to 0.08.

The tempting reading was that the estimator is biased there and no interval
repairs a bias.  This file tested the two explanations that reading implies,
either of which could have refuted it, and BOTH refuted it:

  ARM 1, sample size.  Estimate V at n = 2k .. 64k in every world.  A
  finite-sample gap closes as n grows.  The sparse world's did, from 0.019 to
  about zero.  The noisy world's did not: still 0.024 at n = 64,000.

  ARM 2, the penalty.  Hold n at 4,000 and weaken the L2 penalty by four
  orders of magnitude, since a fixed penalty is not scale-free and could
  masquerade as bias.  The noisy world's gap did not move at all.

WHAT WAS ACTUALLY WRONG.  Neither arm surviving is what sent us to look at the
TARGET rather than the estimator, and the target was wrong.  s10 approximated
both estimands by enumerating the generator's own cells -- the TRUE register
value -- while in the noisy world the estimator only ever sees a value that is
replaced by a uniform draw 20% of the time.  The estimator was being scored
against a population it is not sampling from.  `observed_population` in
s10_simulation2.py now marginalises the noise exactly, which moves the noisy
world's V_limit from +0.1135 to +0.0804 --- and the estimator, whose mean was
+0.0781 all along, is within a fifth of an interval width of it.  There was no
bias.  There was a wrong estimand, in our own simulation, and two arms of
evidence against every explanation that was not that.

This file is kept, and re-run against the corrected target, because the two
arms are what a reader should ask for before believing "the method fails
here", and because a gap that closes with n (sparse) and a gap that does not
(anything misspecified) are worth telling apart.

    python s18_bias_scaling.py [--reps 30] [--procs 6]

Outputs: results/s18_scaling.csv, s18_penalty.csv, s18_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402
from s10_simulation2 import (SEED, WORLD_SEED, WORLDS, draw,  # noqa: E402
                             limit_estimand, truth, world_spec)

#  SEED is imported from s10 and NOT taken from spec: s10 carries its own,
#  and a world built under a different seed is a different world.  This file
#  studied six worlds that were not the ones s10 measured until that was
#  noticed, and every number it produced was about the wrong six.
N_TEST = 20000            # big enough that test noise is not the story
SIZES = (2000, 4000, 8000, 16000, 32000, 64000)
PENALTIES = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)
N_AT_PENALTY = 4000
TAG = "s18_"


def _fit(tr, te, cols, C_):
    return S._onehot_logit(tr, te, cols, tr["_y"].values, SEED, C_=C_)


def _one(args):
    """One (world, n, C, rep) cell: the estimate at that specification."""
    world, n, C_, rep = args
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(SEED + 1013 * rep + WORLD_SEED[world] + n)
    W = world_spec(world, np.random.default_rng(SEED + WORLD_SEED[world]))
    tr = draw(W, n, 1, rng)
    te = draw(W, N_TEST, 2, rng)
    y = te["_y"].values
    if len(np.unique(y)) < 2:
        return None
    p0 = _fit(tr, te, ["b", "g"], C_)
    p1 = _fit(tr, te, ["b", "g", "f"], C_)
    return dict(world=world, n=n, C=C_, rep=rep,
                V=float(roc_auc_score(y, p1) - roc_auc_score(y, p0)))


def run(tasks, procs):
    out, t0 = [], time.time()
    with ProcessPoolExecutor(max_workers=procs) as ex:
        for k, r in enumerate(ex.map(_one, tasks, chunksize=1), 1):
            if r is not None:
                out.append(r)
            if k % 50 == 0:
                print("    %d/%d  %.0fs" % (k, len(tasks), time.time() - t0),
                      flush=True)
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--legacy-target", action="store_true",
                    help="measure the gap against the PRE-CORRECTION V_limit, which weighted the enumerated cells by the generator's table rather than by what the estimator samples. This regenerates Appendix G's evidence.")
    a = ap.parse_args(argv)
    t0 = time.time()
    global TAG
    TAG = "s18_legacy_" if a.legacy_target else "s18_"

    print("=" * 92)
    print("s18  IS THE NOISY WORLD'S GAP A BIAS, AND IS THE PENALTY ITS CAUSE")
    print("=" * 92)

    #  the target every gap is measured against, and the oracle beside it
    lim = {}
    for w in WORLDS:
        rng = np.random.default_rng(SEED + 5000 + WORLD_SEED[w])
        W = world_spec(w, np.random.default_rng(SEED + WORLD_SEED[w]))
        lim[w] = dict(V_limit=float(limit_estimand(
            W, rng, observed=not a.legacy_target)),
                      V_oracle=float(truth(W)["V_oracle"]))
        print("  %-11s V_limit %+.4f   V_oracle %+.4f"
              % (w, lim[w]["V_limit"], lim[w]["V_oracle"]), flush=True)

    # ---- ARM 1: the gap against sample size ------------------------------
    print("\n  ARM 1  the gap against sample size, penalty held at C = 1")
    tasks = [(w, n, 1.0, r) for w in WORLDS for n in SIZES
             for r in range(a.reps)]
    A = run(tasks, a.procs)
    A["V_limit"] = A.world.map(lambda w: lim[w]["V_limit"])
    A["gap"] = A.V_limit - A.V
    SC = (A.groupby(["world", "n"])
          .agg(V_mean=("V", "mean"), V_sd=("V", "std"),
               gap=("gap", "mean"), n_reps=("V", "size"),
               V_limit=("V_limit", "first")).reset_index())
    SC.to_csv(RESULTS / (TAG + "scaling.csv"), index=False)
    print()
    print(SC.pivot_table(index="world", columns="n", values="gap")
          .round(4).to_string())

    # ---- ARM 2: the gap against the penalty, n held fixed -----------------
    print("\n  ARM 2  the gap against the penalty, n held at %d"
          % N_AT_PENALTY)
    tasks = [(w, N_AT_PENALTY, c, r) for w in WORLDS for c in PENALTIES
             for r in range(a.reps)]
    B = run(tasks, a.procs)
    B["V_limit"] = B.world.map(lambda w: lim[w]["V_limit"])
    B["gap"] = B.V_limit - B.V
    PN = (B.groupby(["world", "C"])
          .agg(V_mean=("V", "mean"), gap=("gap", "mean"),
               n_reps=("V", "size")).reset_index())
    PN.to_csv(RESULTS / (TAG + "penalty.csv"), index=False)
    print()
    print(PN.pivot_table(index="world", columns="C", values="gap")
          .round(4).to_string())

    # ---- the two numbers the manuscript quotes ---------------------------
    def g(df, w, col, val):
        r = df[(df.world == w) & (df[col] == val)]
        return float(r.gap.iloc[0]) if len(r) else np.nan

    facts = dict(
        n_reps=a.reps, n_test=N_TEST,
        size_lo=SIZES[0], size_hi=SIZES[-1],
        penalty_lo=PENALTIES[0], penalty_hi=PENALTIES[-1],
        noisy_gap_small_n=g(SC, "noisy", "n", 4000),
        noisy_gap_large_n=g(SC, "noisy", "n", SIZES[-1]),
        noisy_gap_tight_penalty=g(PN, "noisy", "C", 1.0),
        noisy_gap_loose_penalty=g(PN, "noisy", "C", PENALTIES[-1]),
        linear_gap_small_n=g(SC, "linear", "n", 4000),
        linear_gap_large_n=g(SC, "linear", "n", SIZES[-1]),
        sparse_gap_small_n=g(SC, "sparse", "n", 4000),
        sparse_gap_large_n=g(SC, "sparse", "n", SIZES[-1]),
        runtime_s=round(time.time() - t0, 1))
    #  the share of the small-n gap that weakening the penalty alone removes
    facts["noisy_penalty_share"] = (
        1.0 - facts["noisy_gap_loose_penalty"] / facts["noisy_gap_tight_penalty"]
        if facts["noisy_gap_tight_penalty"] else np.nan)
    facts["noisy_size_share"] = (
        1.0 - facts["noisy_gap_large_n"] / facts["noisy_gap_small_n"]
        if facts["noisy_gap_small_n"] else np.nan)
    pd.DataFrame([facts]).to_csv(RESULTS / (TAG + "facts.csv"),
                                 index=False)
    print()
    print(pd.Series(facts).to_string())
    print()
    print("  growing n from %d to %d removes %.0f%% of the noisy world's gap"
          % (4000, SIZES[-1], 100 * facts["noisy_size_share"]))
    print("  weakening the penalty at n = %d removes %.0f%% of it"
          % (N_AT_PENALTY, 100 * facts["noisy_penalty_share"]))


if __name__ == "__main__":
    main()

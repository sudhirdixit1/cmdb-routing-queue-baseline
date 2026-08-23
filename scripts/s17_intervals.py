"""s17 -- THE INTERVAL THE SIMULATION SAYS TO USE.

Round nineteen, and this file exists because the simulation caught the
paper's own recommended interval failing.

WHAT WENT WRONG.  The nested bootstrap of s02 resamples the training half and
refits.  With a high-cardinality register --- 3,019 levels on the primary log
--- a bootstrap training resample contains only about 63% of the distinct
levels, so EVERY refit sees a sparser register than the real training half and
the increment shrinks.  The bootstrap distribution therefore sits BELOW the
estimate, and a percentile interval taken from it sits below the estimand and
misses no matter how wide it is.  s10 measures the failure: on the sparse and
noisy worlds the percentile interval covers far below nominal, and the nested
one covers WORSE than the fixed-model one, which is the opposite of what the
refit is for.

THE FIX, which is standard and which we should have used from the start: take
the BASIC (pivotal) interval,

    [ 2*V_hat - q_{1-a/2},  2*V_hat - q_{a/2} ],

which pivots the shift out, and report the bias-corrected percentile beside
it.  This file recomputes every interval and every max-t band in s02's output
from the STORED DRAWS, so nothing is refitted and the correction costs
seconds.

    python s17_intervals.py

Outputs: results/s17_cells.csv     per-cell percentile, basic and BC intervals
         results/s17_bands.csv     max-t bands built on the basic construction
         results/s17_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

ALPHA = 0.05
KEY = ["log", "target", "learner", "quality", "level", "rung", "metric"]


def three(a, v):
    """Percentile, basic and bias-corrected intervals from one draw set."""
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10 or not np.isfinite(v):
        return (np.nan,) * 6 + (np.nan,)
    qa = float(np.percentile(a, 100 * ALPHA / 2))
    qb = float(np.percentile(a, 100 * (1 - ALPHA / 2)))
    share = float(np.mean(a < v))
    share = min(max(share, 1.0 / (2 * len(a))), 1 - 1.0 / (2 * len(a)))
    z0 = float(norm.ppf(share))
    za, zb = norm.ppf(ALPHA / 2), norm.ppf(1 - ALPHA / 2)
    pa = float(norm.cdf(2 * z0 + za)) * 100
    pb = float(norm.cdf(2 * z0 + zb)) * 100
    return (qa, qb, 2 * v - qb, 2 * v - qa,
            float(np.percentile(a, pa)), float(np.percentile(a, pb)),
            float(np.median(a)) - v)


def main():
    t0 = time.time()
    D = S.read_results("s02_draws.csv.gz")
    print("=" * 92)
    print("s17  RECENTRED INTERVALS AND BANDS FROM THE STORED DRAWS")
    print("=" * 92)
    print("  %d draw rows" % len(D))
    point = D[D.draw < 0].set_index(KEY).V
    boot = D[D.draw >= 0]

    rows = []
    for k, sub in boot.groupby(KEY):
        v = float(point.get(k, np.nan)) if k in point.index else np.nan
        qa, qb, ba, bb, ca, cb, shift = three(sub.V.values, v)
        rows.append(dict(zip(KEY, k)) | dict(
            V=v, se=float(sub.V.std(ddof=1)), n_draws=len(sub),
            pct_lo=qa, pct_hi=qb, basic_lo=ba, basic_hi=bb,
            bc_lo=ca, bc_hi=cb, boot_shift=shift))
    C = pd.DataFrame(rows)
    for kind in ("pct", "basic", "bc"):
        C[kind + "_resolved"] = ((C[kind + "_lo"] > 0)
                                 | (C[kind + "_hi"] < 0))
    #  `lo`, `hi` and `resolved` are aliases for the BASIC construction, which
    #  is the one the paper reports, so a consumer that asks a cell file for
    #  its interval without naming a construction gets the paper's answer
    #  rather than the percentile interval the simulation rejected.  Every
    #  construction stays in the file under its own name.
    C["lo"], C["hi"], C["resolved"] = C.basic_lo, C.basic_hi, C.basic_resolved
    C.to_csv(RESULTS / "s17_cells.csv", index=False)

    #  ---- max-t bands, built on the basic construction -------------------
    #  The band is  V_hat +- q * se  recentred by the same pivot: the shift is
    #  a property of the draws, so subtracting it once fixes every cell in the
    #  family at the same time.
    FAM = ["log", "target", "learner", "quality", "level", "rung"]
    bands = []
    for k, sub in boot.groupby(FAM):
        for fam, sel in (("scalars", sub[~sub.metric.str.startswith("nb_")]),
                         ("decision-curve",
                          sub[sub.metric.str.startswith("nb_")])):
            if sel.empty:
                continue
            W = sel.pivot_table(index="draw", columns="metric", values="V")
            se = W.std(axis=0, ddof=1)
            mu = W.mean(axis=0)
            ok = se[se > 1e-15].index
            if len(ok) == 0:
                continue
            T = ((W[ok] - mu[ok]).abs() / se[ok]).max(axis=1)
            q = float(np.nanpercentile(T, 100 * (1 - ALPHA)))
            for m in ok:
                key = tuple(k) + (m,)
                v = float(point.get(key, np.nan)) if key in point.index else np.nan
                shift = float(W[m].median()) - v
                bands.append(dict(zip(FAM, k)) | dict(
                    family=fam, n_family=len(ok), metric=m, V=v,
                    se=float(se[m]), q_maxt=q, boot_shift=shift,
                    sim_lo=v - shift - q * float(se[m]),
                    sim_hi=v - shift + q * float(se[m]),
                    raw_lo=v - q * float(se[m]),
                    raw_hi=v + q * float(se[m])))
    B = pd.DataFrame(bands)
    if len(B):
        B["sim_resolved"] = (B.sim_lo > 0) | (B.sim_hi < 0)
        B["raw_resolved"] = (B.raw_lo > 0) | (B.raw_hi < 0)
    B.to_csv(RESULTS / "s17_bands.csv", index=False)

    facts = dict(
        n_cells=len(C), n_bands=len(B),
        median_shift=float(C.boot_shift.median()),
        max_abs_shift=float(C.boot_shift.abs().max()),
        share_shift_negative=float((C.boot_shift < 0).mean()),
        n_resolved_pct=int(C.pct_resolved.sum()),
        n_resolved_basic=int(C.basic_resolved.sum()),
        n_resolved_bc=int(C.bc_resolved.sum()),
        n_band_resolved_raw=int(B.raw_resolved.sum()) if len(B) else 0,
        n_band_resolved_recentred=int(B.sim_resolved.sum()) if len(B) else 0,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s17_facts.csv", index=False)
    print()
    print(pd.Series(facts).to_string())
    print()
    print("  the bootstrap distribution sits BELOW the estimate in %.1f%% of "
          "cells" % (100 * facts["share_shift_negative"]))


if __name__ == "__main__":
    main()

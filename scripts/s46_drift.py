"""s46 -- IS THE INCREMENT STATIONARY ACROSS THE TEST HALF?

Round twenty-seven.  Section 11 names two assumptions and says neither is
tested: "the moving-block construction needs stationarity and mixing that an
event log is not guaranteed to have, and the same assumption is what makes
Definition 1's population limit well defined under a temporal split".  That is
an honest statement of an untested assumption, and an untested assumption in a
paper whose subject is what a reported number depends on is worth one cheap
experiment.

WHAT THIS MEASURES.  At the reference cell of every admitted pair, the model
is fitted ONCE on the training half and then evaluated on the test half cut
into `--blocks` consecutive equal blocks in time.  If the estimand is a
population limit under a stationary process, the increment should vary across
blocks only by sampling error.  Three things are reported per pair:

  the SPREAD    max minus min of the per-block increment, AGAINST A
                STATIONARITY NULL.  A block is a fifth of the test half, so it
                carries more sampling error than the whole and some spread is
                guaranteed.  The null therefore re-partitions the same test
                rows into blocks of the same sizes AT RANDOM, destroying the
                time order and nothing else, and the observed spread is
                reported as a percentile of that reference.  Comparing the
                spread with the pair's own interval width, which the first
                version of this file did, compares a fifth-sample statistic
                with a whole-sample one and would call ordinary noise drift.
                Both are reported; the percentile is the one that means
                something.
  the TREND     Spearman correlation of the increment with the block index,
                which separates drift from noise: noise has no order.
  the PREVALENCE and REGISTER TURNOVER per block -- the share of test-half
                register levels in a block that were never seen in training,
                which is the mechanism by which a register decays.

WHAT IT DOES NOT DO.  It does not repair anything, and a pair that drifts is
not thereby wrong: it is a pair whose estimand is a moving target, which is a
statement a reader should be given rather than an error to be corrected.  The
diagnostic is reported for every pair, including the ones that pass.

    python s46_drift.py                # every admitted pair
    python s46_drift.py --blocks 4

Outputs: results/s46_drift.csv (one row per pair per block),
         results/s46_summary.csv (one row per pair), results/s46_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402

#: the reference cell, as everywhere else in the paper
REF_RUNG = "B_intake_g"
REF_LEARNER = "logit"
BLOCKS = 5


def one_pair(log, target, n_blocks, n_perm=400):
    d, ladder, f, meta = S01.prepare(log, target)
    if d is None or not ladder:
        return []
    rungs = {nm: cols for nm, cols in ladder}
    cols = list(rungs.get(REF_RUNG) or [])
    if not cols:
        return []
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tr, te = d.iloc[:cut], d.iloc[cut:]
    if len(te) < 5 * n_blocks:
        return []
    seen = set(tr[f].astype(str).unique())
    p0 = S.LEARNERS[REF_LEARNER](tr, te, cols, tr["_y"].values, S.SEED)
    p1 = S.LEARNERS[REF_LEARNER](tr, te, cols + [f], tr["_y"].values, S.SEED)
    y = te["_y"].values
    fv = te[f].astype(str).values
    edges = np.linspace(0, len(te), n_blocks + 1).astype(int)
    rows = []
    for b in range(n_blocks):
        i, j = edges[b], edges[b + 1]
        yb = y[i:j]
        if len(np.unique(yb)) < 2:
            rows.append(dict(log=log, target=target, block=b, n=int(j - i),
                             prevalence=float(yb.mean()), V=np.nan,
                             base_auc=np.nan, with_auc=np.nan,
                             unseen_share=float(np.mean(
                                 [v not in seen for v in fv[i:j]]))))
            continue
        a0 = roc_auc_score(yb, p0[i:j])
        a1 = roc_auc_score(yb, p1[i:j])
        rows.append(dict(log=log, target=target, block=b, n=int(j - i),
                         prevalence=float(yb.mean()),
                         base_auc=float(a0), with_auc=float(a1),
                         V=float(a1 - a0),
                         unseen_share=float(np.mean(
                             [v not in seen for v in fv[i:j]]))))
    #  the whole-test-half value, which is the number the paper reports
    a0 = roc_auc_score(y, p0)
    a1 = roc_auc_score(y, p1)
    for r in rows:
        r["V_whole"] = float(a1 - a0)

    #  THE STATIONARITY NULL.  The same rows, the same block sizes, the time
    #  order destroyed.  Everything else -- the fitted model, the test half,
    #  the class balance overall -- is held fixed, so the only thing the
    #  reference lacks is the ordering, and a spread that the reference
    #  reproduces is a spread the block size explains.
    sizes = np.diff(edges)
    rng = np.random.default_rng(S.SEED + 977)
    null = []
    for _ in range(n_perm):
        perm = rng.permutation(len(te))
        s, vals = 0, []
        for m in sizes:
            idx = perm[s:s + m]
            s += m
            yb = y[idx]
            if len(np.unique(yb)) < 2:
                continue
            vals.append(roc_auc_score(yb, p1[idx]) - roc_auc_score(yb, p0[idx]))
        if len(vals) >= 3:
            null.append(max(vals) - min(vals))
    obs = [r["V"] for r in rows if np.isfinite(r["V"])]
    spread = (max(obs) - min(obs)) if len(obs) >= 3 else np.nan
    pct = (float(np.mean(np.asarray(null) <= spread))
           if null and np.isfinite(spread) else np.nan)
    for r in rows:
        r["spread_null_median"] = (float(np.median(null)) if null else np.nan)
        r["spread_percentile"] = pct
        r["n_perm"] = len(null)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", type=int, default=BLOCKS)
    ap.add_argument("--perm", type=int, default=400,
                    help="random re-partitions for the "
                         "stationarity null")
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s46  IS THE INCREMENT STATIONARY ACROSS THE TEST HALF?")
    print("=" * 92)
    rows = []
    for log, target, domain in S01.admitted_pairs():
        try:
            rows += one_pair(log, target, a.blocks, a.perm)
        except Exception as e:  # noqa: BLE001
            print("  %s/%s failed: %s" % (log, target, e))
    D = pd.DataFrame(rows)
    if not len(D):
        print("  nothing produced")
        return 1
    D.to_csv(RESULTS / "s46_drift.csv", index=False)

    #  the pair-level summary, compared against the pair's own interval width
    CE = None
    p = RESULTS / "s21_cells.csv"
    if p.exists():
        C = pd.read_csv(p)
        CE = C[(C.metric == "auc") & (C.quality == "clean")
               & (C.rung == REF_RUNG) & (C.learner == REF_LEARNER)]
        if "split" in CE.columns:
            CE = CE[CE.split == "holdout70"]
        CE = CE.drop_duplicates(["log", "target"]).set_index(["log", "target"])

    out = []
    for (log, target), sub in D.groupby(["log", "target"]):
        v = sub.V.dropna()
        if len(v) < 3:
            continue
        rho, pv = spearmanr(sub.block[sub.V.notna()], v)
        width = np.nan
        if CE is not None and (log, target) in CE.index:
            r = CE.loc[(log, target)]
            width = float(r.hi - r.lo)
        spread = float(v.max() - v.min())
        out.append(dict(
            log=log, target=target, n_blocks=int(len(v)),
            V_whole=float(sub.V_whole.iloc[0]),
            V_min=float(v.min()), V_max=float(v.max()), spread=spread,
            sign_varies=bool((v > 0).any() and (v < 0).any()),
            trend_rho=float(rho), trend_p=float(pv),
            interval_width=width,
            spread_over_width=(spread / width if width and np.isfinite(width)
                               and width > 0 else np.nan),
            spread_null_median=float(sub.spread_null_median.iloc[0]),
            spread_over_null=(spread / float(sub.spread_null_median.iloc[0])
                              if float(sub.spread_null_median.iloc[0]) > 0
                              else np.nan),
            spread_percentile=float(sub.spread_percentile.iloc[0]),
            drifts=bool(float(sub.spread_percentile.iloc[0]) >= 0.95),
            prevalence_spread=float(sub.prevalence.max()
                                    - sub.prevalence.min()),
            unseen_first=float(sub.unseen_share.iloc[0]),
            unseen_last=float(sub.unseen_share.iloc[-1])))
    Sm = pd.DataFrame(out).sort_values(["log", "target"])
    Sm.to_csv(RESULTS / "s46_summary.csv", index=False)
    print(Sm[["log", "target", "V_whole", "V_min", "V_max", "spread",
              "spread_null_median", "spread_percentile", "drifts",
              "trend_rho", "sign_varies"]]
          .to_string(index=False, float_format=lambda x: "%.4f" % x))

    ex = Sm[Sm.spread_over_width > 1]
    facts = dict(
        n_pairs=len(Sm), n_blocks=a.blocks,
        spread_median=float(Sm.spread.median()),
        spread_max=float(Sm.spread.max()),
        spread_over_width_median=float(Sm.spread_over_width.median(skipna=True))
        if Sm.spread_over_width.notna().any() else np.nan,
        n_spread_exceeds_interval=int(len(ex)),
        n_perm=int(a.perm),
        spread_null_median=float(Sm.spread_null_median.median()),
        spread_over_null_median=float(Sm.spread_over_null.median()),
        spread_over_null_max=float(Sm.spread_over_null.max()),
        n_drifts=int(Sm.drifts.sum()),
        n_pairs_above_null_median=int((Sm.spread_percentile >= 0.5).sum()),
        n_sign_varies_across_blocks=int(Sm.sign_varies.sum()),
        n_trend_significant=int((Sm.trend_p < 0.05).sum()),
        trend_rho_median=float(Sm.trend_rho.median()),
        prevalence_spread_median=float(Sm.prevalence_spread.median()),
        prevalence_spread_max=float(Sm.prevalence_spread.max()),
        unseen_first_median=float(Sm.unseen_first.median()),
        unseen_last_median=float(Sm.unseen_last.median()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s46_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())

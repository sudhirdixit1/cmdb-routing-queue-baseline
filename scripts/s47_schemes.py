"""s47 -- THE TWO RESAMPLING SCHEMES, COMPARED ON ONE DESIGN.

Round twenty-seven.  Section 11 named a defect, named the repair, and said the
comparison was not run.  `s44_designed.py` runs both schemes over the same
balanced design at the same draw count with the same seeds, so this file is
the comparison and nothing in it is a re-derivation of an argument: every
number is a difference between two runs that differ in one declared thing.

WHAT THE DEFECT IS.  A moving-block resample holds about $1 - e^{-1}$ of the
rows of a draw, so a register level present in few rows is absent from many
draws.  A refit that cannot see a level is a refit of a smaller register than
the estimand is about, so the bootstrap distribution is displaced.  Three
consequences are measurable and all three are measured here.

  1.  LEVEL COVERAGE.  What share of the register's training levels does a
      draw actually contain?  Under weights the answer is one by construction
      and the file checks it rather than asserting it.

  2.  DISPLACEMENT.  The bootstrap median minus the point estimate, per cell.
      Under an unbiased scheme this is Monte Carlo noise around zero and
      shrinks like B^-1/2; under a displaced one it is a bias and does not.
      It is reported against the register's cardinality, which is the
      mechanism, and against n, which is what a bias does not shrink with.

  3.  THE INTERVAL THAT EXCLUDES ITS OWN POINT ESTIMATE.  The pivotal
      interval is 2V - Q(1-a/2), 2V - Q(a/2); when the bootstrap distribution
      is displaced far enough this excludes V.  Round twenty-five counted 74
      of 3,900 cells.  The count under each scheme is the headline of this
      file, because it is a defect a reader can see without believing any
      theory about why it happens.

AND WHAT IT COSTS.  A repair that fixed the displacement by widening
everything would not be a repair.  Interval width, the critical value, and the
number of cells each scheme RESOLVES are reported side by side, so the cost of
the repair is visible next to its benefit.

    python s47_schemes.py

Outputs: results/s47_cells.csv    per cell, both schemes
         results/s47_levels.csv   register-level coverage per pair
         results/s47_summary.csv  per pair
         results/s47_facts.csv
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
import s44_designed as D44  # noqa: E402
from common import RESULTS  # noqa: E402

SCHEMES = ("multinomial", "weighted")
CELLKEY = ["learner", "split", "quality", "level", "rung", "metric"]
ALPHA = 0.05


def cells_for(scheme):
    """Per cell: the point estimate, the bootstrap median, the pivotal
    interval, and whether that interval contains the point estimate."""
    rows = []
    d = RESULTS / ("s44_" + scheme)
    for fn in sorted(d.glob("draws_*.csv.gz")):
        Dd = pd.read_csv(fn)
        if not len(Dd):
            continue
        log, target = str(Dd.log.iloc[0]), str(Dd.target.iloc[0])
        pt = Dd[Dd.draw < 0].set_index(CELLKEY).V
        bt = Dd[Dd.draw >= 0]
        for k, sub in bt.groupby(CELLKEY):
            if k not in pt.index:
                continue
            v = float(pt.loc[k])
            if not np.isfinite(v):
                continue
            x = sub.V.values.astype(float)
            x = x[np.isfinite(x)]
            if len(x) < 20:
                continue
            lo = 2 * v - float(np.percentile(x, 100 * (1 - ALPHA / 2)))
            hi = 2 * v - float(np.percentile(x, 100 * (ALPHA / 2)))
            rows.append(dict(zip(CELLKEY, k)) | dict(
                log=log, target=target, scheme=scheme, V=v,
                boot_median=float(np.median(x)),
                displacement=float(np.median(x)) - v,
                se=float(x.std(ddof=1)), n_draws=int(len(x)),
                lo=lo, hi=hi, width=hi - lo,
                excludes_point=bool(v < lo or v > hi),
                resolved=bool(lo > 0 or hi < 0)))
    return pd.DataFrame(rows)


def level_coverage(n_draws=200):
    """What share of the training half's register levels does one draw hold?

    Under the resample this is the quantity the whole argument is about and it
    has never been measured on this corpus; under weights it is one unless the
    construction is wrong, so measuring it is also the construction's test.
    It needs no fit: it is a property of the resampling scheme and the log.
    """
    rows = []
    for log, target, domain in S01.admitted_pairs():
        try:
            d, ladder, f, meta = S01.prepare(log, target)
        except Exception:  # noqa: BLE001
            continue
        if d is None:
            continue
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        vals = d[f].astype(str).values[:cut]
        uniq = pd.unique(vals)
        card = len(uniq)
        code = pd.Series(vals).map({v: i for i, v in enumerate(uniq)}).values
        rng = np.random.default_rng(S.SEED)
        shares_m, shares_w = [], []
        for b in range(n_draws):
            idx = S.block_indices(cut, rng)
            shares_m.append(len(np.unique(code[idx])) / card)
            w = S.block_weights(cut, rng)
            shares_w.append(float(np.mean(
                np.bincount(code, weights=(w > 0).astype(float),
                            minlength=card) > 0)))
        rows.append(dict(
            log=log, target=target, n_train=cut, card_register=card,
            share_multinomial=float(np.mean(shares_m)),
            share_multinomial_min=float(np.min(shares_m)),
            share_weighted=float(np.mean(shares_w)),
            share_weighted_min=float(np.min(shares_w)),
            n_draws=n_draws))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--level-draws", type=int, default=200)
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s47  THE MULTINOMIAL BLOCK RESAMPLE AGAINST THE BLOCK-WEIGHTED ONE")
    print("=" * 92)

    C = pd.concat([cells_for(s) for s in SCHEMES], ignore_index=True)
    if not len(C):
        print("  s44 has produced nothing yet")
        return 1
    C.to_csv(RESULTS / "s47_cells.csv", index=False)

    L = level_coverage(a.level_draws)
    L.to_csv(RESULTS / "s47_levels.csv", index=False)
    print("\nREGISTER LEVELS PRESENT IN ONE DRAW OF THE TRAINING HALF")
    print(L[["log", "target", "card_register", "share_multinomial",
             "share_multinomial_min", "share_weighted"]]
          .to_string(index=False, float_format=lambda x: "%.4f" % x))

    #  per pair, the two schemes side by side
    out = []
    for (log, target), sub in C.groupby(["log", "target"]):
        r = dict(log=log, target=target)
        for s in SCHEMES:
            q = sub[sub.scheme == s]
            if not len(q):
                continue
            r["n_cells_" + s] = int(len(q))
            r["excludes_" + s] = int(q.excludes_point.sum())
            r["resolved_" + s] = int(q.resolved.sum())
            r["width_" + s] = float(q.width.median())
            r["displacement_" + s] = float(q.displacement.abs().median())
            r["displacement_max_" + s] = float(q.displacement.abs().max())
        out.append(r)
    Sm = pd.DataFrame(out).sort_values(["log", "target"])
    Sm.to_csv(RESULTS / "s47_summary.csv", index=False)
    print("\nPER PAIR")
    print(Sm.to_string(index=False, float_format=lambda x: "%.4f" % x))

    def agg(s, col, how="sum"):
        q = C[C.scheme == s]
        return float(getattr(q[col], how)()) if len(q) else np.nan

    m, w = "multinomial", "weighted"
    facts = dict(
        n_cells=int(len(C[C.scheme == m])),
        n_pairs=int(Sm.shape[0]),
        n_draws=int(C.n_draws.median()),
        #  1: level coverage
        level_share_multinomial=float(L.share_multinomial.mean()),
        level_share_multinomial_min=float(L.share_multinomial_min.min()),
        level_share_weighted=float(L.share_weighted.min()),
        level_worst_pair=str(L.loc[L.share_multinomial.idxmin(), "log"])
        + "/" + str(L.loc[L.share_multinomial.idxmin(), "target"]),
        level_share_worst=float(L.share_multinomial.min()),
        card_max=int(L.card_register.max()),
        #  2: displacement
        displacement_median_multinomial=float(
            C[C.scheme == m].displacement.abs().median()),
        displacement_median_weighted=float(
            C[C.scheme == w].displacement.abs().median()),
        displacement_max_multinomial=float(
            C[C.scheme == m].displacement.abs().max()),
        displacement_max_weighted=float(
            C[C.scheme == w].displacement.abs().max()),
        #  3: the interval that excludes its own point estimate
        n_excludes_multinomial=int(agg(m, "excludes_point")),
        n_excludes_weighted=int(agg(w, "excludes_point")),
        share_excludes_multinomial=float(
            C[C.scheme == m].excludes_point.mean()),
        share_excludes_weighted=float(C[C.scheme == w].excludes_point.mean()),
        n_pairs_excludes_multinomial=int(
            (Sm.get("excludes_" + m, pd.Series(dtype=float)) > 0).sum()),
        n_pairs_excludes_weighted=int(
            (Sm.get("excludes_" + w, pd.Series(dtype=float)) > 0).sum()),
        #  and what the repair costs
        width_median_multinomial=float(C[C.scheme == m].width.median()),
        width_median_weighted=float(C[C.scheme == w].width.median()),
        width_ratio=float(C[C.scheme == w].width.median()
                          / C[C.scheme == m].width.median()),
        n_resolved_multinomial=int(agg(m, "resolved")),
        n_resolved_weighted=int(agg(w, "resolved")),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s47_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())

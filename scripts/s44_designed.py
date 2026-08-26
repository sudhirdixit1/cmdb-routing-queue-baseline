"""s44 -- THE DESIGNED INFERENCE SURFACE, UNDER A DECLARED RESAMPLING SCHEME.

Round twenty-seven.  Section 11 named two defects in the inference surface and
one repair for each, and ran neither.  This file runs both, and runs the
comparison that decides whether the repair was worth making.

THE FIRST DEFECT IS THE RESAMPLING SCHEME.  `spec.block_indices` resamples
blocks of rows with replacement, so about $e^{-1}$ of the rows are absent from
any one draw.  On a register with three thousand levels that is not a nuisance:
a level absent from a draw cannot be fitted in it, so every refit is of a
smaller register than the one the estimand is about.  The bootstrap
distribution is displaced, the displacement is a bias rather than a variance,
and it therefore does not shrink with $n$ while the interval's half-width does.
The visible symptom in round twenty-five was that the pivotal interval excluded
its own point estimate on 74 of 3,900 cells.  The repair is `spec.block_weights`:
a draw is a weight vector, not a subset, so every row -- and therefore every
register level -- is present in every refit.

THE SECOND DEFECT IS THE SURFACE ITSELF.  The old inference surface was chosen
by row count: four learners on the case study and two elsewhere, three quality
conditions except on the two largest logs, four rungs on one pair and three on
the rest.  It was axis-complete and it was UNBALANCED, so the functional-ANOVA
decomposition could not be computed on it and its cell mix differed from the
declared surface's.  This file declares ONE design and runs it on every pair:
two learners, two splits, three quality conditions, three rungs, crossed --
thirty-six cells, balanced and orthogonal, which is a full factorial and so a
strictly stronger guarantee than the resolution-IV fraction Section 11 asked
for.  It costs less per draw than the old surface did, which is what pays for

THE THIRD THING, WHICH IS THE DRAW COUNT.  Round twenty-five measured the
band's family-wise coverage against a known answer and found the binding
constraint was the number of draws: 82.0% at 33 draws and 95.8% at 400.  The
old surface ran 40 to 150.  This one runs 400 on every pair, which is the
number at which the coverage measurement says the band attains its level.

    python s44_designed.py --plan            # the design, run nothing
    python s44_designed.py --scheme weighted --draws 400
    python s44_designed.py --scheme multinomial --draws 400
    python s44_designed.py --smoke           # four draws, both schemes

Outputs: results/s44_<scheme>/draws_<log>_<target>.csv.gz
         results/s44_grid.csv     the declared design, written before any draw
         results/s44_facts.csv
"""
from __future__ import annotations

import os

#  see s01_surface.py.  The pool parallelises over draws; each draw must be
#  single-threaded or OpenMP oversubscribes the machine by an order of
#  magnitude.  These must precede the numpy import.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402

SCHEMES = ("weighted", "multinomial")

#  ---- THE DESIGN.  One declaration, the same on every pair. ---------------
#  Declared here, printed by --plan, and written to results/s44_grid.csv
#  before any draw is taken.  Nothing below reads a result.
DESIGN_LEARNERS = ("logit", "hgb")
DESIGN_SPLITS = ("holdout70", "rolling5")
DESIGN_QUALITY = (("clean", 1.00), ("mask_rare", 0.50), ("stale", 1.00))
#  the three rungs every admitted pair's ladder carries.  B_empty is
#  inadmissible by definition (spec.IMPLAUSIBLE_RUNGS) and B_intake_g_km
#  exists on the case study alone, so including either would unbalance the
#  design -- which is the defect this file exists to remove.
DESIGN_RUNGS = ("B_half", "B_intake", "B_intake_g")
DESIGN_DRAWS = 400

CELLS_PER_PAIR = (len(DESIGN_LEARNERS) * len(DESIGN_SPLITS)
                  * len(DESIGN_QUALITY) * len(DESIGN_RUNGS))

OUTROOT = RESULTS


def outdir(scheme):
    d = OUTROOT / ("s44_" + scheme)
    d.mkdir(parents=True, exist_ok=True)
    return d


# --------------------------------------------------------------------------
def _split_index(n, name):
    """The (train, test) index pair for one named split condition."""
    if name == "holdout70":
        cut = int(n * S.TRAIN_FRAC)
        return np.arange(cut), np.arange(cut, n)
    for nm, tri, tei in S.splits(n, "rolling", n_folds=5):
        if nm == name:
            return tri, tei
    return None, None


_PREPARED = {}


def prepare_cached(log, target):
    key = (log, target)
    if key not in _PREPARED:
        _PREPARED.clear()
        _PREPARED[key] = S01.prepare(log, target)
    return _PREPARED[key]


def one_draw(task):
    """One draw over the whole design for one pair, under one scheme.

    `b < 0` is the point estimate: no resampling and no weights, under either
    scheme, so the two runs share a point estimate exactly and every
    difference between them is the scheme.

    Under `multinomial` a draw is a moving-block resample of the row indices,
    which is what the surface has always used.  Under `weighted` a draw is a
    block-weight vector: the rows are the rows, and the weight enters the fit
    and the metric.  Train and test are drawn independently, as they are under
    the resample, because the split is fixed within a draw.
    """
    log, target, b, scheme = task
    try:
        d, ladder, f, meta = prepare_cached(log, target)
        if d is None:
            return []
        n = len(d)
        rungs = {nm: cols for nm, cols in ladder}
        use_rungs = [r for r in DESIGN_RUNGS if rungs.get(r)]
        if len(use_rungs) != len(DESIGN_RUNGS):
            sys.stderr.write("%s/%s is missing a design rung: has %s\n"
                             % (log, target, sorted(rungs)))
            return []
        rng = np.random.default_rng(S.SEED + 7919 * (b if b >= 0 else 0)
                                    + (0 if scheme == "multinomial" else 104729))
        rows = []
        for split_name in DESIGN_SPLITS:
            tri0, tei0 = _split_index(n, split_name)
            if tri0 is None or len(tri0) < 50 or len(tei0) < 50:
                continue
            wtr = wte = None
            if b < 0:
                tri, tei = tri0, tei0
            elif scheme == "multinomial":
                tri = tri0[S.block_indices(len(tri0), rng)]
                tei = tei0[S.block_indices(len(tei0), rng)]
            else:
                tri, tei = tri0, tei0
                wtr = S.block_weights(len(tri0), rng)
                wte = S.block_weights(len(tei0), rng)
            yte = d["_y"].values[tei]
            if len(np.unique(yte)) < 2:
                continue
            #  the training prevalence is the reference every skill score is
            #  taken against, so under weights it is the WEIGHTED prevalence
            ytr = d["_y"].values[tri]
            prev_tr = (float(ytr.mean()) if wtr is None
                       else float(np.dot(ytr, wtr) / wtr.sum()))
            frames = {}
            for kind, level in DESIGN_QUALITY:
                rng_q = np.random.default_rng(S.SEED + 104729 * max(b, 0))
                dd = d.copy()
                dd["_f"] = S.degrade(d[f], kind, level, rng_q, tri0)
                frames[(kind, level)] = (dd.iloc[tri], dd.iloc[tei])
            base_tr, base_te = frames[DESIGN_QUALITY[0]]
            for rung in use_rungs:
                cols = list(rungs[rung])
                for learner in DESIGN_LEARNERS:
                    #  the baseline arm does not contain the register, so one
                    #  fit serves every quality condition at this cell
                    p0 = S.LEARNERS[learner](base_tr, base_te, cols,
                                             base_tr["_y"].values, S.SEED,
                                             wtr)
                    M0 = S.all_metrics(p0, yte, prev_tr, w=wte)
                    for kind, level in DESIGN_QUALITY:
                        tr, te = frames[(kind, level)]
                        p1 = S.LEARNERS[learner](tr, te, cols + ["_f"],
                                                 tr["_y"].values, S.SEED, wtr)
                        M1 = S.all_metrics(p1, yte, prev_tr, w=wte)
                        for m in M0:
                            rows.append(dict(
                                log=log, target=target, learner=learner,
                                split=split_name, quality=kind, level=level,
                                rung=rung, metric=m, draw=b,
                                V=M1[m] - M0[m], without_f=M0[m],
                                with_f=M1[m]))
        return rows
    except Exception:  # noqa: BLE001
        sys.stderr.write("draw %s/%s/%d/%s\n%s\n"
                         % (log, target, b, scheme,
                            traceback.format_exc()[-600:]))
        return []


def plan(draws=DESIGN_DRAWS):
    """The declared design, one row per pair.  Written before any draw."""
    rows = []
    for log, target, domain in S01.admitted_pairs():
        try:
            d, ladder, f, meta = S01.prepare(log, target)
            have = [nm for nm, cols in (ladder or []) if cols]
        except Exception:  # noqa: BLE001
            have = []
        missing = [r for r in DESIGN_RUNGS if r not in have]
        rows.append(dict(
            log=log, target=target, domain=domain,
            n=(0 if d is None else len(d)),
            learners="|".join(DESIGN_LEARNERS),
            splits="|".join(DESIGN_SPLITS),
            quality="|".join("%s@%.2f" % t for t in DESIGN_QUALITY),
            rungs="|".join(DESIGN_RUNGS),
            n_learners=len(DESIGN_LEARNERS), n_splits=len(DESIGN_SPLITS),
            n_quality=len(DESIGN_QUALITY), n_rungs=len(DESIGN_RUNGS),
            n_scalar_metrics=len(S.SCALARS), n_thresholds=len(S.NB_GRID),
            draws=draws, cells=CELLS_PER_PAIR,
            scalar_cells=CELLS_PER_PAIR * len(S.SCALARS),
            balanced=(not missing),
            missing_rungs="|".join(missing)))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scheme", choices=SCHEMES + ("both",), default="both")
    ap.add_argument("--draws", type=int, default=DESIGN_DRAWS)
    ap.add_argument("--only", default=None,
                    help="one log, or log/target")
    ap.add_argument("--procs", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="skip a pair whose output already carries the "
                         "requested draw count")
    a = ap.parse_args(argv)
    if a.smoke:
        a.draws = 4

    P = plan(a.draws)
    P.to_csv(RESULTS / "s44_grid.csv", index=False)
    print("=" * 92)
    print("s44  THE DESIGNED INFERENCE SURFACE -- BALANCED, %d CELLS A PAIR"
          % CELLS_PER_PAIR)
    print("=" * 92)
    print(P[["log", "target", "n", "n_learners", "n_splits", "n_quality",
             "n_rungs", "cells", "scalar_cells", "draws", "balanced"]]
          .to_string(index=False))
    unbalanced = P[~P.balanced]
    if len(unbalanced):
        print("\n  NOT BALANCED -- these pairs lack a design rung:")
        print(unbalanced[["log", "target", "missing_rungs"]].to_string(index=False))
    print("\n  %d pairs, %d cells, %d scalar family members, %d draws each"
          % (len(P), int(P.cells.sum()), int(P.scalar_cells.sum()), a.draws))
    if a.plan:
        return 0

    schemes = SCHEMES if a.scheme == "both" else (a.scheme,)
    pairs = [(r.log, r.target) for r in P.itertuples()]
    if a.only:
        want = a.only.split("/")
        pairs = [p for p in pairs
                 if p[0] == want[0] and (len(want) == 1 or p[1] == want[1])]

    from multiprocessing import Pool
    t_all = time.time()
    written = []
    for scheme in schemes:
        od = outdir(scheme)
        for log, target in pairs:
            fn = od / ("draws_%s_%s.csv.gz" % (log, target))
            if a.resume and fn.exists():
                try:
                    have = pd.read_csv(fn, usecols=["draw"])
                    if have.draw.max() >= a.draws - 1:
                        print("  %-9s %-20s %-9s already at %d draws"
                              % (scheme, log, target, int(have.draw.max()) + 1))
                        continue
                except Exception:  # noqa: BLE001
                    pass
            t0 = time.time()
            tasks = [(log, target, b, scheme) for b in [-1] + list(range(a.draws))]
            out = []
            with Pool(a.procs) as pool:
                for chunk in pool.imap_unordered(one_draw, tasks, chunksize=1):
                    out.extend(chunk)
            if not out:
                print("  %-9s %-20s %-9s NOTHING" % (scheme, log, target))
                continue
            D = pd.DataFrame(out)
            D.to_csv(fn, index=False, compression="gzip")
            el = time.time() - t0
            written.append(dict(scheme=scheme, log=log, target=target,
                                rows=len(D), draws=a.draws, seconds=el))
            print("  %-9s %-20s %-9s %8d rows  %6.1fs"
                  % (scheme, log, target, len(D), el))
    W = pd.DataFrame(written)
    if len(W):
        W.to_csv(RESULTS / "s44_written.csv", index=False)
        pd.DataFrame([dict(
            n_pairs=len(pairs), n_schemes=len(schemes), draws=a.draws,
            cells_per_pair=CELLS_PER_PAIR,
            n_cells=int(CELLS_PER_PAIR * len(pairs)),
            n_scalar_cells=int(CELLS_PER_PAIR * len(pairs) * len(S.SCALARS)),
            balanced=bool(P.balanced.all()),
            runtime_s=round(time.time() - t_all, 1))]).to_csv(
                RESULTS / "s44_facts.csv", index=False)
    print("\n  total %.1f min" % ((time.time() - t_all) / 60.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())

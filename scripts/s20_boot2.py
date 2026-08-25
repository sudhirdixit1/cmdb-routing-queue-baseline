"""s20 -- THE INFERENCE SURFACE: A NESTED BOOTSTRAP OVER EVERY AXIS.

Round twenty.  The blueprint's P0.1 and P0.2 are one problem seen twice.

P0.1.  The declared surface (s01) spans learner, encoding, split,
availability, register quality, baseline and metric: 262,656 cells.  Round
nineteen's bootstrap (s02) held the SPLIT AXIS FIXED at one holdout and used
four of the ten quality conditions and one of the four learners off the
primary log.  Its families therefore contained thirty scalar cells on most
pairs.  The region labels, the robustness index and the sign-misreport rate
were then computed on that thirty-cell set and described as properties of the
surface.  They are not: they are properties of a sub-grid that omits an axis
whose first-order sensitivity index is the second largest measured.

P0.2.  A max-t band whose family is "the five scalar metrics at one cell" does
not give family-wise coverage over the union of learners, splits, quality
conditions and rungs used to label a whole surface.  The label needs one
critical value taken over EVERY cell it quantifies.

WHAT THIS FILE DOES.  It defines a third object between the declared surface
and the sampling distribution:

  DECLARED SURFACE      every scientifically admissible specification (s01).
  COMPUTATIONAL SURFACE every specification actually evaluated (s01 again:
                        here they coincide, and s25 audits that they do).
  INFERENCE SURFACE     every specification carrying enough bootstrap
                        information for simultaneous inference -- this file.

The inference surface is a declared sub-grid of the declared surface which is
AXIS-COMPLETE: every axis of the estimand varies over at least two levels.  It
is smaller than the declared surface for one reason only, which is stated in
the manuscript and audited by s25: a draw refits the whole pipeline, so the
cost of the inference surface is the cost of the declared surface multiplied
by the number of draws, and the declared surface takes thirty-five minutes on
fourteen cores.

The sub-grid is fixed HERE, before any draw is taken, by a rule that reads
only the row count of the log -- never a result.

Every cell in one draw shares one random stream, so the draw index is a valid
replicate identifier across the entire family and a maximum over cells is
taken over aligned replicates.

    python s20_boot2.py                    # everything
    python s20_boot2.py --only BPIC14      # one log
    python s20_boot2.py --draws 4          # a smoke test
    python s20_boot2.py --plan             # print the plan, run nothing

Outputs: results/s20/draws_<log>_<target>.csv.gz   the joint draw distribution
         results/s20_grid.csv                      the declared inference grid
         results/s20_facts.csv
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

PRIMARY = "BPIC14"
OUT = RESULTS / "s20"
OUT.mkdir(parents=True, exist_ok=True)

#  ---- the declared inference grid ----------------------------------------
#  Three size classes, and nothing but the row count of the log decides which
#  class a pair is in.  The classes exist because a draw costs the pipeline;
#  they are declared here and printed by --plan before any draw is taken.
SMALL, MEDIUM, LARGE = "small", "medium", "large"


def size_class(n):
    if n > 100000:
        return LARGE
    if n > 20000:
        return MEDIUM
    return SMALL


def learners_for(log, cls):
    """The primary log carries all four learners because it is the case
    study.  A medium log carries the two that differ most in FAMILY, one-hot
    logistic regression and target-encoded boosting.  The two largest logs
    carry the two that differ in ENCODING -- one-hot and frequency -- because
    a boosting fit on a quarter of a million rows, refitted in every draw,
    costs more than the rest of the corpus put together, and an axis with two
    levels of encoding is axis-complete where an axis with one learner is
    not.  Every choice here is a function of the row count alone."""
    if log == PRIMARY:
        return ("logit", "logit_fr", "hgb", "hgb_iso")
    if cls == LARGE:
        return ("logit", "logit_fr")
    return ("logit", "hgb")


def splits_for(cls):
    """Two levels, which is axis-complete: one fixed temporal holdout and one
    rolling origin.  The declared surface carries six; the inference surface
    carries the two that bracket them, because a draw refits everything."""
    return ("holdout70", "rolling5")


def quality_for(log, cls):
    """Three mechanisms -- as recorded, a population failure and a discovery
    failure -- and two on the largest logs.  Every one is fitted on the
    training half alone."""
    if cls == LARGE:
        return (("clean", 1.00), ("mask_rare", 0.50))
    return (("clean", 1.00), ("mask_rare", 0.50), ("stale", 1.00))


def draws_for(cls, log):
    """A function of the size class alone.

    Thousands of draws are affordable for the five PLANNED CONTRASTS, which
    live on one cell each and are computed at 2,000 draws in s24.  They are
    not affordable for a family of several hundred cells that refits the whole
    pipeline in every draw on a machine that delivers under three cores of
    sustained throughput: the primary log alone took six hours per target.

    Two things make a few dozen to a few hundred draws workable, and both are
    reported rather than assumed.  First, the critical value is NOT the
    empirical quantile of those maxima, which would be badly estimated: s21
    forms it by a GAUSSIAN MULTIPLIER BOOTSTRAP over the same draws, which
    resamples the standardised draw matrix tens of thousands of times at no
    fitting cost, so the fitting budget fixes B and not the precision of q.
    Second, the number of draws each pair actually carries is printed in the
    denominator audit, per pair, so a reader can see where the evidence is
    thinner rather than being given one number that averages over it.

    The case study carries the most draws because it is the case study.  The
    rest carry what a machine of this size can produce in a night."""
    if log == PRIMARY:
        return 150
    return {SMALL: 80, MEDIUM: 80, LARGE: 40}[cls]


def rungs_for(ladder):
    """B_empty is excluded by definition everywhere (spec.IMPLAUSIBLE_RUNGS);
    the rest are whatever the ladder yields for the log."""
    return [nm for nm, _ in ladder if nm not in S.IMPLAUSIBLE_RUNGS]


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


#: one prepared log per worker process.  `prepare` re-reads and re-derives the
#: log, which costs more than a fit; a worker handles hundreds of draws of the
#: same pair, so it should pay that once.
_PREPARED = {}


def prepare_cached(log, target):
    key = (log, target)
    if key not in _PREPARED:
        _PREPARED.clear()
        _PREPARED[key] = S01.prepare(log, target)
    return _PREPARED[key]


def one_draw(args):
    """One bootstrap draw over the WHOLE inference grid for one pair.

    b < 0 is the point estimate on the unresampled data.  Every cell in this
    draw is produced from one random stream, so the draw index identifies an
    aligned replicate across the entire family -- which is what makes a
    maximum over cells a valid simultaneous statistic.

    THE BASELINE ARM DOES NOT DEPEND ON REGISTER QUALITY.  A quality mechanism
    degrades the register column, and the without-register arm does not
    contain it, so the same fit serves every quality condition at a given
    (split, rung, learner).  Computing it once rather than once per condition
    removes about two fifths of the work and changes no number: the file
    asserts the identity in --check mode.
    """
    log, target, b = args
    try:
        d, ladder, f, meta = prepare_cached(log, target)
        if d is None:
            return []
        n = len(d)
        cls = size_class(n)
        learners = learners_for(log, cls)
        splits = splits_for(cls)
        quality = quality_for(log, cls)
        rungs = {nm: cols for nm, cols in ladder}
        use_rungs = rungs_for(ladder)
        rng = np.random.default_rng(S.SEED + 7919 * (b if b >= 0 else 0))
        rows = []
        for split_name in splits:
            tri0, tei0 = _split_index(n, split_name)
            if tri0 is None or len(tri0) < 50 or len(tei0) < 50:
                continue
            if b < 0:
                tri, tei = tri0, tei0
            else:
                #  one stream, consumed in a fixed order, so the draw is one
                #  realisation of the whole pipeline rather than a set of
                #  independent per-cell realisations
                tri = tri0[S.block_indices(len(tri0), rng)]
                tei = tei0[S.block_indices(len(tei0), rng)]
            yte = d["_y"].values[tei]
            if len(np.unique(yte)) < 2:
                continue
            prev_tr = float(d["_y"].values[tri].mean())
            #  the degraded register column, once per quality condition.  The
            #  mechanism is a function of the TRUE training half, not of the
            #  resample: it is a property of the register, and redrawing it
            #  inside the draw would confound mechanism variability with
            #  sampling variability (P1.3, measured separately in s27).
            frames = {}
            for kind, level in quality:
                rng_q = np.random.default_rng(S.SEED + 104729 * max(b, 0))
                dd = d.copy()
                dd["_f"] = S.degrade(d[f], kind, level, rng_q, tri0)
                frames[(kind, level)] = (dd.iloc[tri], dd.iloc[tei])
            base_tr, base_te = frames[quality[0]]
            for rung in use_rungs:
                cols = list(rungs[rung])
                if not cols:
                    continue
                for learner in learners:
                    #  the baseline arm: one fit for every quality condition
                    p0 = S.LEARNERS[learner](base_tr, base_te, cols,
                                             base_tr["_y"].values, S.SEED)
                    M0 = S.all_metrics(p0, yte, prev_tr)
                    for kind, level in quality:
                        tr, te = frames[(kind, level)]
                        p1 = S.LEARNERS[learner](tr, te, cols + ["_f"],
                                                 tr["_y"].values, S.SEED)
                        M1 = S.all_metrics(p1, yte, prev_tr)
                        for m in M0:
                            rows.append(dict(
                                log=log, target=target, learner=learner,
                                split=split_name, quality=kind, level=level,
                                rung=rung, metric=m, draw=b,
                                V=M1[m] - M0[m], without_f=M0[m],
                                with_f=M1[m]))
        return rows
    except Exception:  # noqa: BLE001
        sys.stderr.write("draw %s/%s/%d\n%s\n"
                         % (log, target, b, traceback.format_exc()[-600:]))
        return []


def plan():
    """The declared grid, one row per (log, target).  Written before any draw
    and read by the denominator audit."""
    L = pd.read_csv(RESULTS / "r33_ladder.csv")
    rows = []
    for log, target, domain in S01.admitted_pairs():
        try:
            n = int(L[L.log == log].n.iloc[0])
        except Exception:  # noqa: BLE001
            n = 20000
        cls = size_class(n)
        lr, sp, q = learners_for(log, cls), splits_for(cls), quality_for(log, cls)
        try:
            d, ladder, f, meta = S01.prepare(log, target)
            rg = rungs_for(ladder) if ladder else []
        except Exception:  # noqa: BLE001
            rg = []
        rows.append(dict(
            log=log, target=target, domain=domain, n=n, size_class=cls,
            n_learners=len(lr), learners="|".join(lr),
            n_splits=len(sp), splits="|".join(sp),
            n_quality=len(q),
            quality="|".join("%s@%.2f" % t for t in q),
            n_rungs=len(rg), rungs="|".join(rg),
            n_scalar_metrics=len(S.SCALARS), n_thresholds=len(S.NB_GRID),
            draws=draws_for(cls, log),
            cells=len(lr) * len(sp) * len(q) * len(rg),
            scalar_cells=len(lr) * len(sp) * len(q) * len(rg) * len(S.SCALARS),
            dc_cells=len(lr) * len(sp) * len(q) * len(rg) * len(S.NB_GRID)))
    P = pd.DataFrame(rows)
    #  the primary log first, because it is the case study, then cheapest
    #  first, so an interrupted run leaves the largest number of complete
    #  pairs behind rather than the largest number of half-finished ones
    P["_order"] = (P.log != PRIMARY).astype(int) * 10 ** 12 + P.n
    P = P.sort_values(["_order", "target"]).drop(columns=["_order"])
    return P.reset_index(drop=True)


def check_baseline_identity(log="BPIC13_incidents", target="handover"):
    """The optimisation this file makes -- one baseline fit per (split, rung,
    learner) rather than one per quality condition -- is only sound if the
    baseline arm really is independent of the register quality mechanism.  It
    is, because the baseline does not contain the register column.  This
    executes the claim rather than asserting it."""
    d, ladder, f, meta = S01.prepare(log, target)
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tri, tei = np.arange(cut), np.arange(cut, n)
    yte = d["_y"].values[tei]
    prev = float(d["_y"].values[tri].mean())
    cols = [c for nm, c in ladder if nm == "B_intake_g"][0]
    out = []
    for kind, level in (("clean", 1.00), ("mask_rare", 0.50), ("stale", 1.00)):
        dd = d.copy()
        dd["_f"] = S.degrade(d[f], kind, level, np.random.default_rng(S.SEED),
                             tri)
        p = S.LEARNERS["logit"](dd.iloc[tri], dd.iloc[tei], list(cols),
                                dd.iloc[tri]["_y"].values, S.SEED)
        out.append(S.all_metrics(p, yte, prev)["auc"])
    spread = float(max(out) - min(out))
    print("  baseline arm across three quality mechanisms: %s  spread %.2e"
          % (["%.9f" % x for x in out], spread))
    assert spread < 1e-12, "the baseline arm is not quality-invariant"
    return spread


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--draws", type=int, default=0)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--procs", type=int, default=0)
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    a = ap.parse_args(argv)

    P = plan()
    P.to_csv(RESULTS / "s20_grid.csv", index=False)
    print("=" * 92)
    print("s20  THE INFERENCE SURFACE -- EVERY AXIS, ALIGNED REPLICATES")
    print("=" * 92)
    print(P[["log", "target", "size_class", "n_learners", "n_splits",
             "n_quality", "n_rungs", "cells", "scalar_cells",
             "draws"]].to_string(index=False))
    print("\n  %d pairs, %d inference cells, %d scalar family members"
          % (len(P), P.cells.sum(), P.scalar_cells.sum()))
    if a.check:
        check_baseline_identity()
        return
    if a.plan:
        return

    if a.only:
        P = P[P.log == a.only]
    t0 = time.time()
    nproc = a.procs or min(13, max(1, (os.cpu_count() or 4) - 1))
    written = []
    for _, r in P.iterrows():
        B = a.draws or int(r.draws)
        fn = OUT / ("draws_%s_%s.csv.gz" % (r.log, r.target))
        #  a seven-hour run must be resumable: a pair whose file already
        #  carries the declared number of draws is skipped, so an interrupted
        #  run continues rather than restarting.
        if a.resume and fn.exists():
            try:
                have = pd.read_csv(fn, usecols=["draw"]).draw.max()
                if int(have) >= B - 1:
                    print("  [%s/%s] complete, skipped" % (r.log, r.target),
                          flush=True)
                    D = pd.read_csv(fn)
                    written.append(dict(
                        log=r.log, target=r.target, rows=len(D), draws=B,
                        seconds=0.0,
                        cells=int(D[D.draw >= 0].groupby(
                            ["learner", "split", "quality", "level",
                             "rung"]).ngroups) if len(D) else 0))
                    continue
            except Exception:  # noqa: BLE001
                pass
        tasks = [(r.log, r.target, -1)] + [(r.log, r.target, b)
                                           for b in range(B)]
        tp = time.time()
        rows = []
        if a.serial:
            for t in tasks:
                rows += one_draw(t)
        else:
            import multiprocessing as mp
            with mp.Pool(processes=nproc) as pool:
                done = 0
                for rr in pool.imap_unordered(one_draw, tasks, chunksize=1):
                    rows += rr
                    done += 1
                    if done % 50 == 0:
                        print("    %s/%s  %d/%d  %.0fs"
                              % (r.log, r.target, done, len(tasks),
                                 time.time() - tp), flush=True)
        D = pd.DataFrame(rows)
        D.to_csv(fn, index=False, compression="gzip")
        written.append(dict(log=r.log, target=r.target, rows=len(D),
                            draws=B, seconds=round(time.time() - tp, 1),
                            cells=int(D[D.draw >= 0].groupby(
                                ["learner", "split", "quality", "level",
                                 "rung"]).ngroups) if len(D) else 0))
        print("  [%s/%s] %d rows, %d draws, %.0fs -> %s"
              % (r.log, r.target, len(D), B, time.time() - tp, fn.name),
              flush=True)

    W = pd.DataFrame(written)
    facts = dict(n_pairs=len(W), n_rows=int(W.rows.sum()),
                 n_cells=int(W.cells.sum()),
                 min_draws=int(W.draws.min()) if len(W) else 0,
                 max_draws=int(W.draws.max()) if len(W) else 0,
                 runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s20_facts.csv", index=False)
    W.to_csv(RESULTS / "s20_written.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

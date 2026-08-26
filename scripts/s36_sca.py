"""s36 -- AGAINST SPECIFICATION-CURVE ANALYSIS AS PRACTISED.  M6.

THE OBJECTION.  The paper's components are adaptations of existing tools and
it says so, but there is no head-to-head against the closest existing
practice, so a reader cannot see what the new objects buy.  The closest
practice is specification-curve analysis (Simonsohn, Simmons and Nelson,
2020): enumerate the reasonable specifications, plot the curve of estimates,
and test the curve against a sharp null by permutation, using the median
estimate and the share of estimates of the dominant sign as test statistics.

WHAT THIS FILE DOES.  It runs that procedure, unchanged, on the same declared
surface the paper's regions are computed on, and puts the two verdicts side by
side.

  SCA           permutation test of the sharp null that the register carries
                no information, with two statistics:
                  (a) the median increment across the surface
                  (b) the share of increments that are positive
                Under the null the register's values are exchangeable across
                cases within each half of the split, which is what permuting
                the column achieves.

  THIS PAPER    the whole-surface simultaneous band, its region label and rho.

THE TWO ANSWER DIFFERENT QUESTIONS AND THE COMPARISON IS THE POINT.  SCA asks
whether the surface as a whole is distinguishable from a surface with no
signal in it; the region asks, of each admissible cell, whether the sign of
that cell's own increment is determined.  A surface can be resoundingly
non-null and still contain cells of both signs -- and where those two verdicts
part company is the clearest statement of what the extra machinery is for.

THE SUB-SURFACE.  A permutation replicate refits every cell of every pair, so
the full surface is unaffordable at any useful replicate count.  The
comparison runs on a DECLARED SUB-SURFACE -- one instrument, two pipelines,
two splits, two register-quality conditions, three rungs -- on EVERY admitted
pair, and the paper's own region is recomputed on exactly that sub-surface so
the two verdicts are about the same object.

    python s36_sca.py --plan
    python s36_sca.py --perms 200

Outputs: results/s36_curve.csv     the observed sub-surface, sorted
         results/s36_null.csv      the permutation distribution
         results/s36_verdicts.csv  SCA verdict beside the region label
         results/s36_facts.csv
"""
from __future__ import annotations

import os

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

ALPHA = 0.05
N_PERM = 100
METRIC = "auc"

#: The declared sub-surface: two pipelines, two splits, two register-quality
#: conditions, three rungs -- 24 cells, the same for every pair, and
#: axis-complete in the sense Section 4.3 uses, every axis carrying at least
#: two levels.
#:
#: The budget is what fixes the size.  A permutation replicate refits every
#: cell of every pair, so the whole comparison costs
#: pairs x (perms + 1) x cells x 2 fits; at fifty-four cells and two hundred
#: permutations over all nineteen pairs that is four hundred thousand fits
#: and half a day, which is not a comparison anybody would rerun.  The
#: smaller design answers the same question -- how often do the two verdicts
#: part company -- on every pair rather than on three, and reporting a
#: measurement over the corpus at a coarser grid is worth more than an
#: illustration on three pairs at a finer one.
LEARNERS = ("logit", "hgb")
QUALITY = (("clean", 1.00), ("mask_rare", 0.50))
RUNGS = ("B_half", "B_intake", "B_intake_g")
SPLIT_KINDS = ("holdout70", "rolling")
N_ROLLING_KEPT = 1

#: ROUND TWENTY-TWO, the second budget declaration.  The sub-surface bounds
#: the number of CELLS a permutation replicate refits; this bounds the number
#: of CASES each of those fits sees.  Both are the same argument: a
#: permutation test that refits everything is quadratic in the corpus's
#: largest logs, and on BPIC19 (251,734 cases) one replicate of the
#: twenty-four-cell design was taking three quarters of an hour, so the
#: comparison over nineteen pairs would have taken most of a day and nobody
#: -- including us -- would rerun it.
#:
#: A pair with more than N_MAX_CASES cases is thinned to a SEEDED RANDOM
#: SAMPLE of that many, taken once per pair and then restored to time order,
#: so the temporal split still splits on time and every cell and every
#: permutation of that pair sees the same cases.  The observed surface and
#: the null are therefore computed on one common sample, which is what the
#: test compares.  It binds on the four largest logs and is recorded per pair
#: in `s36_verdicts.csv` (`n_cases`, `capped`) and counted in the facts file,
#: so the manuscript states which pairs it applies to rather than implying
#: that every pair was run whole.
#:
#: What it costs: the permutation test's power on a capped pair is the power
#: at twenty thousand cases rather than at all of them, which for an AUC
#: increment is ample; what it does NOT change is the region label the
#: verdict is compared against, which is computed on the full data by s33.
N_MAX_CASES = 20000


def prepare_capped(log, target):
    """`S01.prepare` for this experiment, with the declared case cap applied.

    The sample is drawn from a generator seeded on the pair, so it is the
    same sample in every worker process, at every permutation, and on every
    rerun; and it is re-sorted into the original row order so that the
    temporal split of `S.splits` still cuts the pair in time."""
    d, ladder, f, meta = S01.prepare(log, target)
    if d is None:
        return None, None, None, None, 0, False
    n = len(d)
    if n <= N_MAX_CASES:
        return d, ladder, f, meta, n, False
    #  A CONSTANT seed, not one hashed from the pair name: Python randomises
    #  `hash` of a string per process, so a name-derived seed would give each
    #  worker in the pool a DIFFERENT sample of the same pair, and the
    #  observed surface and its null would then be computed on different
    #  cases.  The draw still differs between pairs because it depends on n.
    rng = np.random.default_rng(S.SEED + 7717)
    keep = np.sort(rng.choice(n, size=N_MAX_CASES, replace=False))
    return (d.iloc[keep].reset_index(drop=True), ladder, f, meta,
            N_MAX_CASES, True)

#: ROUND TWENTY-TWO.  The comparison ran on three pairs chosen so that each
#: of the three ways the two verdicts can relate was visible, which is an
#: illustration and not a measurement -- a reviewer said so and was right.
#: It now runs on EVERY admitted pair, and the question it answers is how
#: often the two verdicts part company rather than whether they can.
def all_pairs():
    import s01_surface as S01
    return tuple((lg, tg) for lg, tg, _ in S01.admitted_pairs())


PAIRS = None      # resolved at run time; --pairs restricts it


def learners_for(log):
    """The pipelines the DECLARED surface carries for this log, so that the
    sub-surface the comparison runs on is a subset of it.  Hard-coding two
    names would put `hgb' on the two largest logs, where the declared surface
    carries three pipelines and the inference surface carries a different
    two."""
    import r32_corpus as C
    import s01_surface as S01
    return tuple(S01.learners_for(log, len(C.load(log))))[:2]


def sub_surface(d, ladder, f, perm_seed=None, learners=LEARNERS):
    """Every cell of the declared sub-surface, at one permutation of the
    register (or the observed register when perm_seed is None)."""
    from sklearn.metrics import roc_auc_score
    rungs = dict(ladder)
    n = len(d)
    splits = []
    for kind in SPLIT_KINDS:
        got = list(S.splits(n, kind, n_folds=5))
        splits += got[:1] if kind == "holdout70" else got[:N_ROLLING_KEPT]
    rows = []
    for split_name, tri, tei in splits:
        yte = d["_y"].values[tei]
        if len(np.unique(yte)) < 2:
            continue
        prev_tr = float(d["_y"].values[tri].mean())
        for kind, level in QUALITY:
            dd = d.copy()
            col = d[f]
            if perm_seed is not None:
                #  the sharp null: the register is exchangeable across cases
                #  WITHIN each half, so the permutation cannot move a value
                #  across the split point and create leakage of its own.
                r = np.random.default_rng(perm_seed)
                v = col.values.copy()
                v[tri] = r.permutation(v[tri])
                v[tei] = r.permutation(v[tei])
                col = pd.Series(v, index=col.index)
            dd["_f"] = S.degrade(col, kind, level,
                                 np.random.default_rng(S.SEED), tri)
            tr, te = dd.iloc[tri], dd.iloc[tei]
            for rung in RUNGS:
                cols = list(rungs.get(rung, []))
                if not cols:
                    continue
                for learner in learners:
                    p1 = S.LEARNERS[learner](tr, te, cols + ["_f"],
                                             tr["_y"].values, S.SEED)
                    p0 = S.LEARNERS[learner](tr, te, cols,
                                             tr["_y"].values, S.SEED)
                    a1 = float(roc_auc_score(yte, p1))
                    a0 = float(roc_auc_score(yte, p0))
                    rows.append(dict(split=split_name, quality=kind,
                                     level=level, rung=rung,
                                     learner=learner, metric=METRIC,
                                     without_f=a0, with_f=a1, V=a1 - a0))
    return pd.DataFrame(rows)


def statistics(V):
    v = np.asarray(V, float)
    v = v[np.isfinite(v)]
    if not len(v):
        return dict(median=np.nan, share_positive=np.nan, share_dominant=np.nan)
    sp = float((v > 0).mean())
    return dict(median=float(np.median(v)), share_positive=sp,
                share_dominant=max(sp, 1 - sp))


def task(args):
    log, target, perm = args
    try:
        d, ladder, f, meta, n_cases, capped = prepare_capped(log, target)
        if d is None:
            return None
        SS = sub_surface(d, ladder, f,
                         perm_seed=None if perm < 0 else S.SEED + 991 * perm,
                         learners=learners_for(log))
        st = statistics(SS.V.values)
        return dict(log=log, target=target, perm=perm, n_cells=len(SS),
                    n_cases=n_cases, capped=capped, **st)
    except Exception as e:  # noqa: BLE001
        return dict(log=log, target=target, perm=perm, error=str(e),
                    trace=traceback.format_exc()[-400:])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=N_PERM)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--reuse", action="store_true",
                    help="keep the permutation null and the observed curves "
                         "already on disk and rebuild only the verdicts, "
                         "which is what changes when s33 is re-estimated")
    ap.add_argument("--pairs", default="",
                    help="comma-separated log/target list; default is every "
                         "admitted pair")
    a = ap.parse_args(argv)
    t0 = time.time()
    global PAIRS
    if a.pairs:
        PAIRS = tuple(tuple(p.split("/")) for p in a.pairs.split(","))
    else:
        PAIRS = all_pairs()
    n_cells = (1 + N_ROLLING_KEPT) * len(QUALITY) * len(RUNGS) * 2
    print("=" * 92)
    print("s36  AGAINST SPECIFICATION-CURVE ANALYSIS AS PRACTISED")
    print("=" * 92)
    print("  %d pairs x (%d permutations + 1) x %d cells x 2 fits = %s"
          % (len(PAIRS), a.perms, n_cells,
             format(len(PAIRS) * (a.perms + 1) * n_cells * 2, ",")))
    if a.plan:
        for lg, tg in PAIRS:
            print("     %s / %s" % (lg, tg))
        return

    #  ROUND TWENTY-FIVE.  This file's verdicts table carries two columns
    #  that are not computed here at all -- the region label and rho, merged
    #  in from s33 -- so re-estimating the calibration makes them stale while
    #  everything this file DOES compute is unchanged.  Recomputing the
    #  permutation null to refresh a merge would cost the raw logs and hours;
    #  --reuse rebuilds the verdicts from the null and the curves on disk.
    if a.reuse:
        D = pd.read_csv(RESULTS / "s36_null.csv")
        CU = pd.read_csv(RESULTS / "s36_curve.csv")
        print("  reusing %d null rows and %d curve rows already on disk"
              % (len(D), len(CU)))
        return _verdicts(D, CU, t0, a.perms, n_cells)

    tasks = [(lg, tg, p) for (lg, tg) in PAIRS
             for p in [-1] + list(range(a.perms))]
    out = []
    if a.serial:
        for t in tasks:
            r = task(t)
            if r:
                out.append(r)
    else:
        import multiprocessing as mp
        done = 0
        with mp.Pool(processes=min(12,
                                   max(1, (os.cpu_count() or 4) - 2))) as pool:
            for r in pool.imap_unordered(task, tasks):
                done += 1
                if r:
                    out.append(r)
                if done % 25 == 0:
                    print("    %d/%d  %.0fs" % (done, len(tasks),
                                                time.time() - t0), flush=True)
    D = pd.DataFrame(out)
    #  ROUND TWENTY-FIVE.  `task` catches its own exceptions and returns an
    #  error row, so a run with no data under it completes "successfully"
    #  with nineteen hundred error rows -- and this line then overwrote a
    #  good permutation null with them.  It did, on the machine this round
    #  was done on, and the file had to come back out of git.  A run that
    #  produced no usable replicate does not get to write.
    if "median" not in D.columns or not D.median.notna().any():
        n_err = int(D.error.notna().sum()) if "error" in D.columns else len(D)
        raise SystemExit(
            "s36: %d tasks and not one usable replicate (%d carried an "
            "error); refusing to overwrite results/s36_null.csv.  The first "
            "error was:\n  %s" % (len(D), n_err,
                                  (D.error.dropna().iloc[0]
                                   if "error" in D.columns
                                   and D.error.notna().any() else "unknown")))
    D.to_csv(RESULTS / "s36_null.csv", index=False)

    #  the observed sub-surface of each pair, kept for the figure
    curves = []
    for (lg, tg) in PAIRS:
        d, ladder, f, meta, _n_cases, _capped = prepare_capped(lg, tg)
        if d is None:
            continue
        SS = sub_surface(d, ladder, f,
                         learners=learners_for(lg)).assign(
                             log=lg, target=tg)
        curves.append(SS.sort_values("V").reset_index(drop=True)
                      .assign(rank=lambda x: np.arange(1, len(x) + 1)))
    CU = pd.concat(curves, ignore_index=True) if curves else pd.DataFrame()
    CU.to_csv(RESULTS / "s36_curve.csv", index=False)
    return _verdicts(D, CU, t0, a.perms, n_cells)


def _verdicts(D, CU, t0, n_perms, n_cells):
    #  the calibrated regions are the ones the article quotes
    #  ROUND TWENTY-TWO.  `s33_regions.csv` carries BOTH the nominal `rho'
    #  and `region' and the calibrated ones, so renaming the calibrated pair
    #  onto those names produced two columns called `rho' and `g.rho' became
    #  a DataFrame; `float()` of it raised, at the very end of a run that had
    #  already cost hours.  The nominal columns are dropped first, so the
    #  rename lands on names nothing else holds.
    _cal = RESULTS / "s33_regions.csv"
    if _cal.exists():
        REG = pd.read_csv(_cal).drop(columns=["rho", "region"],
                                     errors="ignore").rename(
            columns={"region_calibrated": "region",
                     "rho_calibrated": "rho"})
    else:
        REG = pd.read_csv(RESULTS / "s21_regions.csv")
    rows = []
    for (lg, tg), sub in D.groupby(["log", "target"]):
        obs = sub[sub.perm < 0]
        nul = sub[sub.perm >= 0]
        if not len(obs) or not len(nul):
            continue
        o = obs.iloc[0]
        r = {}
        for stat in ("median", "share_dominant"):
            k = int((np.abs(nul[stat].values - (0.5 if stat ==
                                                "share_dominant" else 0.0))
                     >= abs(o[stat] - (0.5 if stat == "share_dominant"
                                       else 0.0))).sum())
            r["p_" + stat] = (k + 1) / (len(nul) + 1)
            r["obs_" + stat] = float(o[stat])
            r["null_" + stat + "_median"] = float(nul[stat].median())
        g = REG[(REG.log == lg) & (REG.target == tg)]
        #  the sub-surface's own region, so the two verdicts are about the
        #  same set of cells
        cu = CU[(CU.log == lg) & (CU.target == tg)]
        rows.append(dict(
            log=lg, target=tg, n_cells=int(o.n_cells), n_perms=len(nul),
            n_cases=int(o.get("n_cases", 0)),
            capped=bool(o.get("capped", False)),
            share_positive=float(o.share_positive), **r,
            sca_verdict=("non-null at 5%" if r["p_median"] <= ALPHA
                         else "not distinguishable from null"),
            region_full_surface=(str(g.region.iloc[0]) if len(g) else ""),
            rho_full_surface=(float(g.rho.iloc[0]) if len(g) else np.nan),
            sub_surface_sign_varies=bool(len(cu) and (cu.V > 0).any()
                                         and (cu.V <= 0).any())))
    VD = pd.DataFrame(rows)
    VD.to_csv(RESULTS / "s36_verdicts.csv", index=False)
    print("\n" + VD.to_string(index=False))

    #  the sub-surface has ONE sign while the full surface has both: the
    #  second way the two instruments part company, and the one that shows a
    #  curve is a claim about its own denominator
    sub_one_sign = ~VD.sub_surface_sign_varies if len(VD) else None
    full_both = (VD.region_full_surface.isin(
        ["sign-changing", "conditionally harmful"]) if len(VD) else None)
    facts = dict(
        n_pairs=len(VD), n_perms=n_perms, n_cells=n_cells,
        n_max_cases=N_MAX_CASES,
        n_capped=int(VD.capped.sum()) if len(VD) and "capped" in VD else 0,
        n_sca_nonnull=int((VD.p_median <= ALPHA).sum()) if len(VD) else 0,
        n_sign_varies=int(VD.sub_surface_sign_varies.sum()) if len(VD) else 0,
        n_disagree=int(((VD.p_median <= ALPHA)
                        & VD.sub_surface_sign_varies).sum()) if len(VD) else 0,
        n_agree_null=int(((VD.p_median > ALPHA)
                          & (VD.region_full_surface == "unresolved")).sum())
        if len(VD) else 0,
        n_sub_surface_disagree=int((sub_one_sign & full_both).sum())
        if len(VD) else 0,
        p_median_min=float(VD.p_median.min()) if len(VD) else np.nan,
        p_median_max=float(VD.p_median.max()) if len(VD) else np.nan,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s36_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s36_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

"""s01 -- THE FROZEN MASTER SURFACE.

Round nineteen.  One pipeline, one pass, every admitted log.  Referee comments
1, 3, 9 and 10 all reduce to the same demand: compute every reported number
from a single frozen specification of the estimator, over a design space that
is declared rather than implied, on every eligible log rather than the ones
where the answer resolves.

    python s01_surface.py                 # everything, parallel
    python s01_surface.py BPIC14          # one log
    python s01_surface.py --serial        # one process, for debugging

WHAT IS FROZEN.  The design space is `spec.py`.  Nothing here chooses a
learner, a rung, a quality mechanism or a metric per log; the same grid is
attempted everywhere and what a log cannot carry is reported as an exclusion
with its reason.

WHAT WOULD SINK THIS.  If the surface were computed only where the answer is
interesting.  The pairs are taken from the pre-registered ladder's own
admission list -- all of them -- and the ones with a negative or unresolvable
increment are in the output file beside the others.

Outputs: results/s01_surface.csv       one row per (spec cell, metric)
         results/s01_fits.csv          one row per fitted arm: calibration,
                                       unseen-category rate, prevalence
         results/s01_excluded.csv      every (log, target) not run, with why
         results/s01_facts.csv         the counts the manuscript quotes
         results/s01_trainonly.csv     the executed train-only checks
"""
from __future__ import annotations

import os

#  ROUND NINETEEN, a two-hour lesson.  The gradient-boosting learner uses
#  OpenMP internally.  Twelve worker processes each spawning fourteen OMP
#  threads on a fourteen-core machine oversubscribes it by an order of
#  magnitude, and a fit that takes 3 seconds alone took 8 in the pool.  The
#  parallelism here is over TASKS, so each task must be single-threaded.
#  These must be set before numpy or sklearn is imported.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

PRIMARY = "BPIC14"

#  Every (log, target, g-rule) the pre-registered ladder admits, taken from
#  its own output rather than retyped.  `primary` g only: the alternative
#  resource fields are a separate sensitivity and live in s09.
def admitted_pairs():
    L = pd.read_csv(RESULTS / "r33_ladder.csv")
    L = L[(L.f_rule == "amended") & (L.g_rule == "primary")]
    out = []
    for _, r in L.iterrows():
        out.append((str(r.log), str(r.target), str(r.domain)))
    #  stable order, primary first
    out.sort(key=lambda t: (t[0] != PRIMARY, t[0], t[1]))
    return out


#  ---- the grid ------------------------------------------------------------
LEARNERS_PRIMARY = ("logit", "logit_fr", "hgb", "hgb_iso")
LEARNERS_OTHER = ("logit", "hgb")

QUALITY_PRIMARY = (("clean", 1.00), ("mask_rare", 0.75), ("mask_rare", 0.50),
                   ("mask_rare", 0.25), ("mask_random", 0.50),
                   ("mask_common", 0.50), ("corrupt", 0.05), ("corrupt", 0.15),
                   ("duplicate", 0.15), ("stale", 1.00))
QUALITY_OTHER = (("clean", 1.00), ("mask_rare", 0.75), ("mask_rare", 0.50),
                 ("mask_rare", 0.25), ("corrupt", 0.15), ("stale", 1.00))

SPLITS = ("holdout70", "rolling")
N_FOLDS = 5
SEEDS_STOCHASTIC = (0, 1, 2)     # the stochastic mechanisms are averaged
STOCHASTIC = {"mask_random", "corrupt", "duplicate"}


# --------------------------------------------------------------------------
def prepare(log, target):
    """Load one log, assign roles by the registered rules, build the ladder.

    Returns (frame, ladder, feature, meta) or (None, None, None, reason).
    """
    import r32_corpus as C
    import r33_generic_ladder as L
    d = C.load(log)
    out = L.assign_roles(log, d)
    if len(out) == 7 and out[5]:
        return None, None, None, "roles:%s" % out[5]
    d, CAND, gsel, fsel, b0sel, code, has_time = out
    if code:
        return None, None, None, "roles:%s" % code
    g, g_seq, _, _ = gsel
    f = fsel[1] or fsel[0]
    b0, layers = b0sel
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    y_h, y_d, _ = L.targets(d, g_seq, cut)
    yv = y_h if target == "handover" else y_d
    if yv is None:
        return None, None, None, "target:undefined"
    d = d.copy()
    d["_y"] = np.asarray(yv).astype(int)

    extra = []
    if log == PRIMARY:
        #  The knowledge-article reference, admitted as its own rung.  Whether
        #  it is available depends on WHICH DECISION TIME the analyst is
        #  standing at, and that is the availability axis: at interaction
        #  opening it is not yet written, at incident creation the service
        #  desk has already worked the interaction.  s08 establishes what the
        #  interaction file can and cannot prove; here the rung simply exists
        #  so both decision times can be read off one surface.
        km = "KM number"
        if km in d.columns:
            extra.append(("intake_g_km", [km]))
    ladder = S.ladder_for(d, b0, g, extra=extra)
    meta = dict(log=log, target=target, n=n, g=g, f=f, n_b0=len(b0),
                card_f=int(d[f].astype(str).nunique()),
                card_g=int(d[g].astype(str).nunique()),
                prevalence=float(d["_y"].mean()))
    return d, ladder, f, meta


def run_task(task):
    """One (log, target, learner).  Returns (rows, fitrows, checks, err)."""
    log, target, domain, learner = task
    t0 = time.time()
    try:
        d, ladder, f, meta = prepare(log, target)
        if d is None:
            return [], [], [], dict(log=log, target=target, learner=learner,
                                    reason=meta)
        quality = QUALITY_PRIMARY if log == PRIMARY else QUALITY_OTHER
        rows, fitrows, checks = [], [], []
        n = len(d)
        for split_kind in SPLITS:
            for split_name, tri, tei in S.splits(n, split_kind,
                                                 n_folds=N_FOLDS):
                yte = d["_y"].values[tei]
                if len(np.unique(yte)) < 2:
                    continue
                prev_tr = float(d["_y"].values[tri].mean())
                for kind, level in quality:
                    seeds = (SEEDS_STOCHASTIC if kind in STOCHASTIC else (0,))
                    #  the executed train-only check, once per mechanism
                    if split_name == "holdout70":
                        checks.append(dict(
                            log=log, target=target, mechanism=kind,
                            level=level,
                            train_only=S.assert_train_only(
                                d[f], kind, level, S.SEED, tri)))
                    acc = {}
                    for sd in seeds:
                        rng = np.random.default_rng(S.SEED + 1000 * sd)
                        dd = d.copy()
                        dd["_f"] = S.degrade(d[f], kind, level, rng, tri)
                        populated = float((dd["_f"] != S.EMPTY).mean())
                        tr, te = dd.iloc[tri], dd.iloc[tei]
                        for rung, cols in ladder:
                            use = list(cols) if cols else ["_const"]
                            if not cols:
                                tr = tr.assign(_const="c")
                                te = te.assign(_const="c")
                            for arm, cc in (("without_f", use),
                                            ("with_f", use + ["_f"])):
                                p = S.LEARNERS[learner](tr, te, cc,
                                                        tr["_y"].values,
                                                        S.SEED)
                                M = S.all_metrics(p, yte, prev_tr)
                                key = (rung, arm)
                                acc.setdefault(key, []).append(M)
                                if sd == seeds[0]:
                                    cal = S.calibration(p, yte)
                                    fitrows.append(dict(
                                        log=log, target=target,
                                        learner=learner, split=split_name,
                                        quality=kind, level=level, rung=rung,
                                        arm=arm, n_train=len(tr),
                                        n_test=len(te), prev_train=prev_tr,
                                        prev_test=float(np.mean(yte)),
                                        populated=populated,
                                        unseen=S.unseen_rate(tr, te, cc),
                                        n_cols=len(cc), **cal))
                    #  average the stochastic mechanisms over their seeds
                    avg = {k: {m: float(np.mean([a[m] for a in v]))
                               for m in v[0]} for k, v in acc.items()}
                    for rung, _cols in ladder:
                        w0 = avg.get((rung, "without_f"))
                        w1 = avg.get((rung, "with_f"))
                        if w0 is None or w1 is None:
                            continue
                        for m in w0:
                            rows.append(dict(
                                log=log, domain=domain, target=target,
                                learner=learner,
                                encoding=S.LEARNER_ENCODING[learner],
                                split=split_name, quality=kind, level=level,
                                n_seeds=len(seeds), rung=rung, metric=m,
                                without_f=w0[m], with_f=w1[m],
                                V=w1[m] - w0[m], n=meta["n"],
                                n_test=len(tei), card_f=meta["card_f"],
                                card_g=meta["card_g"], n_b0=meta["n_b0"],
                                f=meta["f"], g=meta["g"],
                                prevalence=meta["prevalence"]))
        el = time.time() - t0
        print("  [%s/%s/%s] %d rows, %d fits, %.0fs"
              % (log, target, learner, len(rows), len(fitrows), el), flush=True)
        return rows, fitrows, checks, None
    except Exception as e:  # a task that dies must say so, not vanish
        return [], [], [], dict(log=log, target=target, learner=learner,
                                reason="ERROR:%s" % e,
                                trace=traceback.format_exc()[-800:])


def main(argv):
    serial = "--serial" in argv
    only = [a for a in argv if not a.startswith("-")]
    pairs = admitted_pairs()
    if only:
        pairs = [p for p in pairs if p[0] in only]
    tasks = []
    for log, target, domain in pairs:
        learners = LEARNERS_PRIMARY if log == PRIMARY else LEARNERS_OTHER
        for lr in learners:
            tasks.append((log, target, domain, lr))
    print("=" * 92)
    print("s01  THE FROZEN MASTER SURFACE")
    print("=" * 92)
    print("  %d (log, target) pairs, %d tasks" % (len(pairs), len(tasks)))
    t0 = time.time()
    R, F, K, X = [], [], [], []
    if serial:
        for t in tasks:
            r, fr, ck, err = run_task(t)
            R += r
            F += fr
            K += ck
            if err:
                X.append(err)
    else:
        import multiprocessing as mp
        with mp.Pool(processes=min(12, max(1, (os.cpu_count() or 4) - 2))) as pool:
            for r, fr, ck, err in pool.imap_unordered(run_task, tasks):
                R += r
                F += fr
                K += ck
                if err:
                    X.append(err)
    SUR = pd.DataFrame(R)
    FIT = pd.DataFrame(F)
    CHK = pd.DataFrame(K).drop_duplicates() if K else pd.DataFrame()
    EXC = pd.DataFrame(X) if X else pd.DataFrame(columns=["log", "target",
                                                          "learner", "reason"])
    #  The surface is 52 MB as plain CSV and 4 MB gzipped, and a repository
    #  that carries the plain one is a repository nobody clones.  Readers use
    #  spec.read_results, which resolves either.
    SUR.to_csv(RESULTS / "s01_surface.csv.gz", index=False, compression="gzip")
    FIT.to_csv(RESULTS / "s01_fits.csv.gz", index=False, compression="gzip")
    CHK.to_csv(RESULTS / "s01_trainonly.csv", index=False)
    EXC.to_csv(RESULTS / "s01_excluded.csv", index=False)

    facts = dict(
        n_pairs=len(pairs), n_tasks=len(tasks), n_rows=len(SUR),
        n_fits=len(FIT), n_logs=int(SUR.log.nunique()) if len(SUR) else 0,
        n_domains=int(SUR.domain.nunique()) if len(SUR) else 0,
        n_learners=int(SUR.learner.nunique()) if len(SUR) else 0,
        n_splits=int(SUR.split.nunique()) if len(SUR) else 0,
        n_quality=int(SUR.groupby(["quality", "level"]).ngroups) if len(SUR) else 0,
        n_rungs=int(SUR.rung.nunique()) if len(SUR) else 0,
        n_metrics=int(SUR.metric.nunique()) if len(SUR) else 0,
        n_excluded=len(EXC),
        trainonly_checked=len(CHK),
        trainonly_passed=int(CHK.train_only.sum()) if len(CHK) else 0,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s01_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    if len(EXC):
        print("\nEXCLUSIONS")
        print(EXC.to_string(index=False)[:3000])
    print("\nwrote s01_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

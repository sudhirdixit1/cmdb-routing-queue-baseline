"""s02 -- UNCERTAINTY THAT INCLUDES THE MODEL.

Round nineteen.  The referee's eighth major comment is that the round-eighteen
intervals bootstrap test rows while holding the fitted models fixed, and so
exclude training-sample variability, model-selection variability, encoder
variability, temporal-split uncertainty and the temporal dependence between
incidents.  This file replaces them.

WHAT EACH DRAW DOES.  A draw resamples the TRAINING half by moving blocks,
REFITS every arm of every rung under every learner and every quality
mechanism on that resample, and evaluates on a moving-block resample of the
TEST half.  Encoders, frequency tables, target encodings, register-frequency
rankings and calibrators are all rebuilt inside the draw.  Blocks carry the
temporal dependence.

WHAT THE DRAWS ARE THEN USED FOR.

  1  per-cell bootstrap standard errors and percentile intervals;
  2  SIMULTANEOUS max-t bands over a declared family of cells, so a statement
     about a whole decision curve or a whole ladder has family-wise coverage
     rather than pointwise coverage;
  3  FIELLER intervals for the ratio R, which is the referee's fifth comment:
     a ratio whose denominator is near zero has an interval that is a union or
     the whole line, and Fieller says so where the percentile method silently
     does not;
  4  five PRE-SPECIFIED CONFIRMATORY contrasts with Holm correction.  Every
     other comparison in the paper is exploratory and is labelled as such.

    python s02_boot.py                # everything
    python s02_boot.py --primary      # BPIC14 only
    python s02_boot.py --draws 50     # a short run, for a smoke test

Outputs: results/s02_draws.csv.gz    every draw x cell (the joint distribution)
         results/s02_cells.csv       point estimate, se, percentile interval
         results/s02_bands.csv       max-t simultaneous bands, per family
         results/s02_fieller.csv     Fieller intervals for R
         results/s02_confirmatory.csv the five registered contrasts, Holm
         results/s02_facts.csv
"""
from __future__ import annotations

import os

#  see s01_surface.py: the pool parallelises over tasks, so each task must be
#  single-threaded or OpenMP oversubscribes the machine.
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
ALPHA = 0.05
Z = 1.959963984540054

#  the headline design space the bootstrap covers.  Declared here, before any
#  draw is taken, and the same for every log that can carry it.
HEADLINE_RUNGS = ("B_half", "B_intake", "B_intake_g", "B_intake_g_km")
#  FOUR quality conditions rather than the surface's ten.  The bootstrap
#  refits the whole pipeline in every draw, so its cost is the product of the
#  grid and the draw count; the full grid at 250 draws is a twelve-hour run on
#  this machine and the four conditions below span the two mechanisms that
#  matter for a REGION label -- coverage and discovery -- at the levels the
#  manuscript quotes.  The remaining six conditions are point estimates on the
#  master surface and are reported there.  This is a declared reduction, not a
#  reduction chosen after seeing which cells resolved.
HEADLINE_QUALITY = (("clean", 1.00), ("mask_rare", 0.75), ("mask_rare", 0.50),
                    ("stale", 1.00))
OTHER_QUALITY = (("clean", 1.00), ("mask_rare", 0.50))
LEARNERS_PRIMARY = ("logit", "logit_fr", "hgb", "hgb_iso")
LEARNERS_OTHER = ("logit",)

#  the five CONFIRMATORY contrasts.  Everything else in the manuscript is
#  exploratory.  Each is (name, cell_a, cell_b or None, direction).
#  A cell is (rung, metric, quality, level).
CONFIRMATORY = [
    ("C1 register adds to the intake baseline",
     ("B_intake", "auc", "clean", 1.00), None, "gt"),
    ("C2 register adds once the free field is admitted",
     ("B_intake_g", "auc", "clean", 1.00), None, "gt"),
    ("C3 register adds at the later decision time",
     ("B_intake_g_km", "auc", "clean", 1.00), None, "gt"),
    ("C4 absorption by the free field is positive",
     ("B_intake", "auc", "clean", 1.00),
     ("B_intake_g", "auc", "clean", 1.00), "gt"),
    ("C5 a half-empty register is worth less",
     ("B_intake_g", "auc", "clean", 1.00),
     ("B_intake_g", "auc", "mask_rare", 0.50), "gt"),
]


def draws_for(n, log=None):
    """Fewer draws on the larger logs and on the log that carries four
    learners, declared as a function of size rather than chosen per log after
    seeing a result.  The max-t band is formed over the draws a cell actually
    has, so a cell with fewer draws gets a wider band, not a wrong one."""
    if log == PRIMARY:
        return 200
    if n > 100000:
        return 120
    return 250


def one_draw(args):
    """One bootstrap draw for one (log, target, learner).  b < 0 means the
    point estimate on the unresampled data."""
    log, target, learner, b, n_draws = args
    try:
        d, ladder, f, meta = S01.prepare(log, target)
        if d is None:
            return []
        quality = HEADLINE_QUALITY if log == PRIMARY else OTHER_QUALITY
        rungs = {nm: cols for nm, cols in ladder}
        use_rungs = [r for r in HEADLINE_RUNGS if r in rungs]
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri0, tei0 = np.arange(cut), np.arange(cut, n)
        if b < 0:
            tri, tei = tri0, tei0
        else:
            rng = np.random.default_rng(S.SEED + 7919 * b)
            tri = tri0[S.block_indices(len(tri0), rng)]
            tei = tei0[S.block_indices(len(tei0), rng)]
        yte = d["_y"].values[tei]
        if len(np.unique(yte)) < 2:
            return []
        prev_tr = float(d["_y"].values[tri].mean())
        rows = []
        for kind, level in quality:
            rng_q = np.random.default_rng(S.SEED)
            dd = d.copy()
            dd["_f"] = S.degrade(d[f], kind, level, rng_q, tri0)
            tr, te = dd.iloc[tri], dd.iloc[tei]
            for rung in use_rungs:
                cols = list(rungs[rung])
                M = {}
                for arm, cc in (("without_f", cols), ("with_f", cols + ["_f"])):
                    p = S.LEARNERS[learner](tr, te, cc, tr["_y"].values, S.SEED)
                    M[arm] = S.all_metrics(p, yte, prev_tr)
                for m in M["without_f"]:
                    rows.append(dict(log=log, target=target, learner=learner,
                                     quality=kind, level=level, rung=rung,
                                     metric=m, draw=b,
                                     V=M["with_f"][m] - M["without_f"][m],
                                     without_f=M["without_f"][m],
                                     with_f=M["with_f"][m]))
        return rows
    except Exception:  # noqa: BLE001
        sys.stderr.write(traceback.format_exc()[-500:])
        return []


# --------------------------------------------------------------------------
# Fieller
# --------------------------------------------------------------------------
def fieller(v0, v1, s00, s11, s01, z=Z):
    """Fieller's theorem for theta = v1 / v0.  Returns (lo, hi, kind) where
    kind is 'bounded', 'unbounded' (the confidence set is the whole line) or
    'exclusive' (the set is the complement of an interval).  A percentile
    interval reports a bounded interval in all three cases, which is the
    referee's point."""
    a = v0 * v0 - z * z * s00
    b = -2.0 * (v0 * v1 - z * z * s01)
    c = v1 * v1 - z * z * s11
    disc = b * b - 4 * a * c
    if a > 0:
        if disc < 0:
            return np.nan, np.nan, "empty"
        r = np.sqrt(disc)
        return (-b - r) / (2 * a), (-b + r) / (2 * a), "bounded"
    if disc < 0:
        return -np.inf, np.inf, "unbounded"
    r = np.sqrt(disc)
    lo, hi = sorted([(-b - r) / (2 * a), (-b + r) / (2 * a)])
    return lo, hi, "exclusive"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", action="store_true")
    ap.add_argument("--draws", type=int, default=0)
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args(argv)
    pairs = S01.admitted_pairs()
    if a.primary:
        pairs = [p for p in pairs if p[0] == PRIMARY]
    t0 = time.time()

    tasks = []
    sizes = {}
    for log, target, _dom in pairs:
        learners = LEARNERS_PRIMARY if log == PRIMARY else LEARNERS_OTHER
        try:
            L = pd.read_csv(RESULTS / "r33_ladder.csv")
            n = int(L[(L.log == log)].n.iloc[0])
        except Exception:  # noqa: BLE001
            n = 20000
        sizes[log] = n
        B = a.draws or draws_for(n, log)
        for lr in learners:
            tasks.append((log, target, lr, -1, B))
            for b in range(B):
                tasks.append((log, target, lr, b, B))
    print("=" * 92)
    print("s02  NESTED MOVING-BLOCK BOOTSTRAP, PIPELINE REFITTED IN EVERY DRAW")
    print("=" * 92)
    print("  %d (log, target) pairs, %d draw-tasks" % (len(pairs), len(tasks)))

    rows = []
    if a.serial:
        for i, t in enumerate(tasks):
            rows += one_draw(t)
            if (i + 1) % 25 == 0:
                print("    %d/%d  %.0fs" % (i + 1, len(tasks), time.time() - t0),
                      flush=True)
    else:
        import multiprocessing as mp
        nproc = min(12, max(1, (os.cpu_count() or 4) - 2))
        with mp.Pool(processes=nproc) as pool:
            for i, r in enumerate(pool.imap_unordered(one_draw, tasks,
                                                      chunksize=1)):
                rows += r
                if (i + 1) % 100 == 0:
                    print("    %d/%d  %.0fs" % (i + 1, len(tasks),
                                                time.time() - t0), flush=True)
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "s02_draws.csv.gz", index=False, compression="gzip")
    print("  %d draw-rows in %.0fs" % (len(D), time.time() - t0))

    KEY = ["log", "target", "learner", "quality", "level", "rung", "metric"]
    point = D[D.draw < 0].set_index(KEY)[["V", "without_f", "with_f"]]
    boot = D[D.draw >= 0]
    agg = boot.groupby(KEY).V.agg(
        se="std", lo=lambda x: float(np.nanpercentile(x, 100 * ALPHA / 2)),
        hi=lambda x: float(np.nanpercentile(x, 100 * (1 - ALPHA / 2))),
        n_draws="count", mean="mean")
    C = point.join(agg, how="left").reset_index()
    C["resolved"] = (C.lo > 0) | (C.hi < 0)
    C.to_csv(RESULTS / "s02_cells.csv", index=False)

    # --- simultaneous max-t bands over declared families -------------------
    bands = []
    for (log, target, learner, quality, level, rung), sub in boot.groupby(
            ["log", "target", "learner", "quality", "level", "rung"]):
        for fam, sel in (("scalars", sub[~sub.metric.str.startswith("nb_")]),
                         ("decision-curve", sub[sub.metric.str.startswith("nb_")])):
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
                pv = point.reset_index()
                p_ = pv[(pv.log == log) & (pv.target == target)
                        & (pv.learner == learner) & (pv.quality == quality)
                        & (pv.level == level) & (pv.rung == rung)
                        & (pv.metric == m)]
                if p_.empty:
                    continue
                v = float(p_.V.iloc[0])
                bands.append(dict(log=log, target=target, learner=learner,
                                  quality=quality, level=level, rung=rung,
                                  family=fam, n_family=len(ok), metric=m,
                                  V=v, se=float(se[m]), q_maxt=q,
                                  sim_lo=v - q * float(se[m]),
                                  sim_hi=v + q * float(se[m])))
    BND = pd.DataFrame(bands)
    if len(BND):
        BND["sim_resolved"] = (BND.sim_lo > 0) | (BND.sim_hi < 0)
    BND.to_csv(RESULTS / "s02_bands.csv", index=False)

    # --- Fieller intervals for R over every ordered rung pair --------------
    NEST = ["B_half", "B_intake", "B_intake_g", "B_intake_g_km"]
    fie = []
    for (log, target, learner, quality, level, metric), sub in boot.groupby(
            ["log", "target", "learner", "quality", "level", "metric"]):
        W = sub.pivot_table(index="draw", columns="rung", values="V")
        pv = point.reset_index()
        p_ = pv[(pv.log == log) & (pv.target == target)
                & (pv.learner == learner) & (pv.quality == quality)
                & (pv.level == level) & (pv.metric == metric)]
        pm = p_.set_index("rung").V.to_dict()
        present = [r for r in NEST if r in W.columns and r in pm]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                lo_r, hi_r = present[i], present[j]
                v0, v1 = pm[lo_r], pm[hi_r]
                cov = np.cov(np.c_[W[lo_r].values, W[hi_r].values].T)
                s00, s11, s01 = cov[0, 0], cov[1, 1], cov[0, 1]
                th_lo, th_hi, kind = fieller(v0, v1, s00, s11, s01)
                #  R = 1 - theta, so the interval reverses
                R_lo = 1.0 - th_hi if np.isfinite(th_hi) else -np.inf
                R_hi = 1.0 - th_lo if np.isfinite(th_lo) else np.inf
                fie.append(dict(log=log, target=target, learner=learner,
                                quality=quality, level=level, metric=metric,
                                b_lo=lo_r, b_hi=hi_r, V_lo=v0, V_hi=v1,
                                D=v0 - v1,
                                D_se=float(np.std(W[lo_r] - W[hi_r], ddof=1)),
                                D_lo=float(np.nanpercentile(W[lo_r] - W[hi_r],
                                                            100 * ALPHA / 2)),
                                D_hi=float(np.nanpercentile(W[lo_r] - W[hi_r],
                                                            100 * (1 - ALPHA / 2))),
                                R=1.0 - v1 / v0 if abs(v0) > 1e-12 else np.nan,
                                R_fieller_lo=R_lo, R_fieller_hi=R_hi,
                                fieller_kind=kind,
                                denom_t=v0 / np.sqrt(s00) if s00 > 0 else np.nan))
    FIE = pd.DataFrame(fie)
    FIE.to_csv(RESULTS / "s02_fieller.csv", index=False)

    # --- the five confirmatory contrasts, Holm-corrected -------------------
    conf = []
    for name, ca, cb, direction in CONFIRMATORY:
        sel = lambda df, c: df[(df.rung == c[0]) & (df.metric == c[1])
                               & (df.quality == c[2])
                               & (np.isclose(df.level, c[3]))]
        sub = boot[(boot.log == PRIMARY) & (boot.target == "handover")
                   & (boot.learner == "logit")]
        A = sel(sub, ca).set_index("draw").V
        if A.empty:
            continue
        if cb is None:
            stat = A
            pt = point.reset_index()
            p_ = pt[(pt.log == PRIMARY) & (pt.target == "handover")
                    & (pt.learner == "logit") & (pt.rung == ca[0])
                    & (pt.metric == ca[1]) & (pt.quality == ca[2])
                    & (np.isclose(pt.level, ca[3]))]
            est = float(p_.V.iloc[0]) if len(p_) else float(A.mean())
        else:
            Bv = sel(sub, cb).set_index("draw").V
            stat = (A - Bv).dropna()
            pt = point.reset_index()

            def pv1(c):
                q = pt[(pt.log == PRIMARY) & (pt.target == "handover")
                       & (pt.learner == "logit") & (pt.rung == c[0])
                       & (pt.metric == c[1]) & (pt.quality == c[2])
                       & (np.isclose(pt.level, c[3]))]
                return float(q.V.iloc[0]) if len(q) else np.nan
            est = pv1(ca) - pv1(cb)
        #  a one-sided bootstrap p-value for H0: quantity <= 0
        p = float((stat <= 0).mean())
        p = min(1.0, 2 * min(p, 1 - p)) if direction == "two" else p
        conf.append(dict(contrast=name, estimate=est,
                         se=float(stat.std(ddof=1)),
                         lo=float(np.nanpercentile(stat, 100 * ALPHA / 2)),
                         hi=float(np.nanpercentile(stat, 100 * (1 - ALPHA / 2))),
                         p_raw=p, n_draws=int(len(stat))))
    CF = pd.DataFrame(conf)
    if len(CF):
        k = len(CF)
        s = CF.sort_values("p_raw").reset_index(drop=True)
        adj, run = [], 0.0
        for i, r in s.iterrows():
            run = max(run, min(1.0, r.p_raw * (k - i)))
            adj.append(run)
        s["p_holm"] = adj
        s["reject_holm_05"] = s.p_holm < 0.05
        CF = s
    CF.to_csv(RESULTS / "s02_confirmatory.csv", index=False)

    facts = dict(n_pairs=len(pairs), n_draw_tasks=len(tasks),
                 n_draw_rows=len(D), n_cells=len(C),
                 n_bands=len(BND), n_fieller=len(FIE),
                 fieller_unbounded=int((FIE.fieller_kind != "bounded").sum())
                 if len(FIE) else 0,
                 fieller_total=len(FIE),
                 n_confirmatory=len(CF),
                 n_confirmatory_reject=int(CF.reject_holm_05.sum())
                 if len(CF) else 0,
                 max_q_maxt=float(BND.q_maxt.max()) if len(BND) else np.nan,
                 median_q_maxt=float(BND.q_maxt.median()) if len(BND) else np.nan,
                 runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s02_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    if len(CF):
        print("\nCONFIRMATORY CONTRASTS (Holm)")
        print(CF.to_string(index=False, float_format=lambda x: "%+.5f" % x))


if __name__ == "__main__":
    main()

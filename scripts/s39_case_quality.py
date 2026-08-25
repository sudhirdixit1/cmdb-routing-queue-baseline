"""s39 -- THE CASE STUDY'S QUALITY AND ABSORPTION, ON THE CASE STUDY'S COHORT.

Round twenty-one, review comment M1, second half.

THE DEFECT.  Section 7 opened on the estate's own cohort and reassignment
target and then, without saying so, printed its register-quality and
absorption tables on the registered cohort and the handover target.  The two
disagree: the register is worth about +0.10 against intake plus group on the
first and about +0.17 on the second.  A reader who compared the section's
first table with its fifth was comparing two different questions.

THIS FILE PUTS THEM ON ONE COHORT.  Every mechanism of Section 4, the three
dependent mechanisms and the discovery lag, plus the absorption ladder with
its Fieller sets, computed on:

    cohort   the estate's own, 45,455 incidents at the registered cutoff
    target   reassignment to another group before resolution
    order    sorted in time, ties broken by incident identifier
    learner  one-hot logistic regression, the reference cell
    split    the single temporal holdout

The corpus versions stay where they belong, in Section 6 and the supplement,
and both are labelled.

The mechanisms are IMPORTED from s27, not reimplemented: the dependent ones
took two attempts to get right and a copy would let the two drift.

    python s39_case_quality.py --draws 400
    python s39_case_quality.py --draws 10       # smoke test

Outputs: results/s39_quality.csv     one row per (mechanism, level)
         results/s39_integrals.csv   the severity integral per mechanism
         results/s39_absorption.csv  D and R with Fieller sets, per pair of
                                     rungs and per instrument
         results/s39_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import itertools
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

ALPHA = 0.05
N_BOOT = 400
IDENT = "CI Name (aff)"
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
GROUP = "intake_group"
KM = "km_number"

RUNGS = [("B_half", INTAKE[:2]),
         ("B_intake", INTAKE),
         ("B_intake_g", INTAKE + [GROUP]),
         ("B_intake_g_km", INTAKE + [GROUP, KM])]
REFERENCE_RUNG = "B_intake_g"

#: the mechanisms and the severities the section's four findings quote, plus
#: the fine grid the severity integral is taken over
POINTS = (("clean", 1.00), ("mask_rare", 0.75), ("mask_rare", 0.50),
          ("mask_rare", 0.25), ("mask_random", 0.50), ("mask_common", 0.50),
          ("corrupt", 0.05), ("corrupt", 0.15), ("corrupt", 0.30),
          ("duplicate", 0.15), ("duplicate", 0.50), ("duplicate", 1.00),
          ("stale", 1.00), ("stale_lag", 0.10), ("stale_lag", 0.25),
          ("stale_lag", 0.50))
SWEEP_KINDS = ("mask_rare", "time", "content", "propensity")
SWEEP_LEVELS = tuple(np.round(np.linspace(0.0, 1.0, 11), 2))
SEEDS = (0, 1, 2)
STOCHASTIC = {"mask_random", "corrupt", "duplicate", "content", "propensity"}

_D = None


def cohort():
    """The case study's cohort, under a declared tie-break."""
    global _D
    if _D is not None:
        return _D
    import base14 as B
    d = B.D.copy()
    d = d.sort_values(["_t", "Incident ID"],
                      kind="mergesort").reset_index(drop=True)
    _D = d
    return d


def stale_lag(col, lag, train_index):
    """Identities first used in the last `lag` share of the TRAINING window
    are absent everywhere: a discovery lag rather than a hard cut-off.
    Imported in spirit from s09; the two must agree and s39 asserts nothing
    the other does not."""
    s = col.astype(str).copy()
    tr = s.iloc[train_index]
    n_tr = len(tr)
    cut = int(n_tr * (1.0 - lag))
    known = set(tr.iloc[:cut].unique())
    return s.where(s.isin(known), S.EMPTY)


def degrade(col, kind, level, rng, tri, d):
    import s27_quality as Q27
    if kind == "clean":
        return col.astype(str)
    if kind == "stale_lag":
        return stale_lag(col, level, tri)
    if kind in ("time", "content", "propensity"):
        return Q27.degrade_extra(col, kind, level, rng, tri, d, "BPIC14")
    return S.degrade(col, kind, level, rng, tri)


def one(task):
    kind, level, seed, rung, cols, want = task
    try:
        from sklearn.metrics import roc_auc_score
        d = cohort()
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri = np.arange(cut)
        dd = d.copy()
        dd["_f"] = degrade(d[IDENT], kind, level,
                           np.random.default_rng(S.SEED + 1000 * seed), tri, d)
        populated = float((dd["_f"] != S.EMPTY).mean())
        tr, te = dd.iloc[:cut], dd.iloc[cut:]
        y = te["_y"].values
        prev = float(tr["_y"].mean())
        p1 = S._onehot_logit(tr, te, list(cols) + ["_f"], tr["_y"].values,
                             S.SEED)
        p0 = S._onehot_logit(tr, te, list(cols), tr["_y"].values, S.SEED)
        M1 = S.all_metrics(p1, y, prev, grid=())
        M0 = S.all_metrics(p0, y, prev, grid=())
        row = dict(mechanism=kind, level=level, seed=seed, rung=rung,
                   populated=populated, want=want)
        for m in S.SCALARS:
            row["V_" + m] = M1[m] - M0[m]
            row["base_" + m] = M0[m]
        row["V"] = row["V_auc"]
        return row, None
    except Exception as e:  # noqa: BLE001
        return None, dict(mechanism=kind, level=level, rung=rung,
                          reason="ERROR:%s" % e,
                          trace=traceback.format_exc()[-500:])


def absorb_draw(b):
    """One draw of the whole ladder, so that D and R and their Fieller sets
    come from the same resample."""
    from sklearn.metrics import roc_auc_score
    d = cohort()
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tri0, tei0 = np.arange(cut), np.arange(cut, n)
    if b < 0:
        tri, tei = tri0, tei0
    else:
        rng = np.random.default_rng(S.SEED + 7919 * b)
        tri = tri0[S.block_indices(len(tri0), rng)]
        tei = tei0[S.block_indices(len(tei0), rng)]
    tr, te = d.iloc[tri], d.iloc[tei]
    y = te["_y"].values
    if len(np.unique(y)) < 2:
        return None
    prev = float(tr["_y"].mean())
    out = {}
    for rung, cols in RUNGS:
        p1 = S._onehot_logit(tr, te, list(cols) + [IDENT], tr["_y"].values,
                             S.SEED)
        p0 = S._onehot_logit(tr, te, list(cols), tr["_y"].values, S.SEED)
        M1 = S.all_metrics(p1, y, prev, grid=())
        M0 = S.all_metrics(p0, y, prev, grid=())
        for m in S.SCALARS:
            out[(rung, m)] = M1[m] - M0[m]
    return dict(draw=b, **{"%s|%s" % k: v for k, v in out.items()})


def fieller(a_hat, b_hat, cov, alpha=ALPHA):
    """The Fieller set for R = 1 - b/a, with its kind.  A ratio whose
    denominator is not resolvably away from zero has an unbounded or
    exclusive set, and saying so is the point of using Fieller at all."""
    from scipy.stats import norm
    z = float(norm.ppf(1 - alpha / 2))
    v_aa, v_ab, v_bb = cov
    A = a_hat ** 2 - z ** 2 * v_aa
    B = -2.0 * (a_hat * b_hat - z ** 2 * v_ab)
    C = b_hat ** 2 - z ** 2 * v_bb
    disc = B ** 2 - 4 * A * C
    if A > 0 and disc >= 0:
        r1 = (-B - np.sqrt(disc)) / (2 * A)
        r2 = (-B + np.sqrt(disc)) / (2 * A)
        lo, hi = sorted((1 - r2, 1 - r1))
        return lo, hi, "bounded"
    if disc < 0:
        return np.nan, np.nan, "empty"
    r1 = (-B - np.sqrt(disc)) / (2 * A)
    r2 = (-B + np.sqrt(disc)) / (2 * A)
    lo, hi = sorted((1 - r2, 1 - r1))
    return lo, hi, "exclusive"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=N_BOOT)
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    d = cohort()
    print("=" * 92)
    print("s39  THE CASE STUDY'S QUALITY AND ABSORPTION, ON ITS OWN COHORT")
    print("=" * 92)
    print("  cohort %d  prevalence %.4f  register levels %d"
          % (len(d), float(d["_y"].mean()), int(d[IDENT].nunique())))

    cols_ref = dict(RUNGS)[REFERENCE_RUNG]
    tasks = []
    for kind, level in POINTS:
        seeds = SEEDS if kind in STOCHASTIC else (0,)
        for sd in seeds:
            tasks.append((kind, level, sd, REFERENCE_RUNG, tuple(cols_ref),
                          "point"))
    for kind in SWEEP_KINDS:
        seeds = SEEDS if kind in STOCHASTIC else (0,)
        for lv in SWEEP_LEVELS:
            for sd in seeds:
                tasks.append((kind, float(lv), sd, REFERENCE_RUNG,
                              tuple(cols_ref), "sweep"))
    print("  %d quality fits" % (2 * len(tasks)), flush=True)

    R, X = [], []
    if a.serial:
        for t in tasks:
            r, e = one(t)
            (R if r else X).append(r or e)
    else:
        import multiprocessing as mp
        done = 0
        with mp.Pool(processes=min(12,
                                   max(1, (os.cpu_count() or 4) - 2))) as pool:
            for r, e in pool.imap_unordered(one, tasks, chunksize=2):
                done += 1
                if r:
                    R.append(r)
                else:
                    X.append(e)
                if done % 25 == 0:
                    print("    %d/%d  %.0fs" % (done, len(tasks),
                                                time.time() - t0), flush=True)
    Q = pd.DataFrame(R)
    #  average the stochastic mechanisms over their seeds, and keep the
    #  spread as its own column: mechanism variability is not sampling
    #  variability and the two are reported separately
    agg = (Q.groupby(["want", "mechanism", "level"])
           .agg(V=("V", "mean"), V_sd=("V", lambda x: float(np.std(x, ddof=1))
                                       if len(x) > 1 else 0.0),
                populated=("populated", "mean"),
                n_seeds=("seed", "nunique")).reset_index())
    POINTS_T = agg[agg.want == "point"].drop(columns=["want"])
    POINTS_T.to_csv(RESULTS / "s39_quality.csv", index=False)
    print("\n" + POINTS_T.to_string(index=False))

    SW = agg[agg.want == "sweep"]
    rows = []
    for kind, g in SW.groupby("mechanism"):
        g = g.sort_values("level")
        integral = float(np.trapezoid(g.V.values, g.level.values)) \
            if hasattr(np, "trapezoid") else float(np.trapz(g.V.values,
                                                            g.level.values))
        coarse = g[g.level.isin([0.0, 0.25, 0.5, 0.75, 1.0])].sort_values("level")
        ic = (float(np.trapezoid(coarse.V.values, coarse.level.values))
              if hasattr(np, "trapezoid")
              else float(np.trapz(coarse.V.values, coarse.level.values))) \
            if len(coarse) > 1 else np.nan
        rows.append(dict(mechanism=kind, n_levels=len(g),
                         n_seeds=int(g.n_seeds.max()), integral=integral,
                         integral_coarse=ic, grid_shift=abs(integral - ic),
                         seed_sd_median=float(g.V_sd.median()),
                         V_at_clean=float(g[g.level == 1.0].V.iloc[0])
                         if (g.level == 1.0).any() else np.nan,
                         V_at_empty=float(g[g.level == 0.0].V.iloc[0])
                         if (g.level == 0.0).any() else np.nan))
    IN = pd.DataFrame(rows)
    IN.to_csv(RESULTS / "s39_integrals.csv", index=False)
    print("\n" + IN.to_string(index=False))

    # ---- the absorption ladder ------------------------------------------
    print("\n  absorption: %d draws" % a.draws, flush=True)
    draws = [-1] + list(range(a.draws))
    if a.serial:
        AB = [absorb_draw(b) for b in draws]
    else:
        import multiprocessing as mp
        with mp.Pool(processes=min(12,
                                   max(1, (os.cpu_count() or 4) - 2))) as pool:
            AB = list(pool.imap_unordered(absorb_draw, draws))
    AB = pd.DataFrame([x for x in AB if x])
    pt = AB[AB.draw < 0].iloc[0]
    bs = AB[AB.draw >= 0]
    rows = []
    names = [r[0] for r in RUNGS]
    for m in S.SCALARS:
        for i, j in itertools.combinations(range(len(names)), 2):
            b0, b1 = names[i], names[j]
            ka, kb = "%s|%s" % (b0, m), "%s|%s" % (b1, m)
            a_hat, b_hat = float(pt[ka]), float(pt[kb])
            D = a_hat - b_hat
            da, db = bs[ka].values, bs[kb].values
            cov = (float(np.var(da, ddof=1)),
                   float(np.cov(da, db, ddof=1)[0, 1]),
                   float(np.var(db, ddof=1)))
            dd = da - db
            lo, hi = (2 * D - float(np.percentile(dd, 97.5)),
                      2 * D - float(np.percentile(dd, 2.5)))
            R_hat = 1.0 - b_hat / a_hat if abs(a_hat) > 1e-12 else np.nan
            f_lo, f_hi, kind = fieller(a_hat, b_hat, cov)
            rows.append(dict(metric=m, b_lo=b0, b_hi=b1, V_lo=a_hat,
                             V_hi=b_hat, D=D, D_lo=lo, D_hi=hi, R=R_hat,
                             R_fieller_lo=f_lo, R_fieller_hi=f_hi,
                             fieller_kind=kind))
    AS = pd.DataFrame(rows)
    AS.to_csv(RESULTS / "s39_absorption.csv", index=False)
    print("\n" + AS[AS.metric == "auc"].to_string(index=False))

    ref = AS[(AS.metric == "auc") & (AS.b_lo == "B_intake")
             & (AS.b_hi == "B_intake_g")]
    q = POINTS_T.set_index(["mechanism", "level"]).V
    facts = dict(
        n_cohort=len(d), prevalence=float(d["_y"].mean()),
        card_register=int(d[IDENT].nunique()),
        n_quality_points=len(POINTS_T), n_sweep_levels=len(SWEEP_LEVELS),
        n_seeds=len(SEEDS), n_draws=a.draws, n_failed=len(X),
        V_clean=float(q.get(("clean", 1.00), np.nan)),
        V_rare_half=float(q.get(("mask_rare", 0.50), np.nan)),
        V_common_half=float(q.get(("mask_common", 0.50), np.nan)),
        V_random_half=float(q.get(("mask_random", 0.50), np.nan)),
        V_corrupt_thirty=float(q.get(("corrupt", 0.30), np.nan)),
        V_duplicate_all=float(q.get(("duplicate", 1.00), np.nan)),
        V_stale=float(q.get(("stale", 1.00), np.nan)),
        V_lag_half=float(q.get(("stale_lag", 0.50), np.nan)),
        D_ref=float(ref.D.iloc[0]) if len(ref) else np.nan,
        D_ref_lo=float(ref.D_lo.iloc[0]) if len(ref) else np.nan,
        D_ref_hi=float(ref.D_hi.iloc[0]) if len(ref) else np.nan,
        R_ref=float(ref.R.iloc[0]) if len(ref) else np.nan,
        R_ref_kind=str(ref.fieller_kind.iloc[0]) if len(ref) else "",
        n_fieller=len(AS),
        n_fieller_unbounded=int((AS.fieller_kind != "bounded").sum()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s39_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s39_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

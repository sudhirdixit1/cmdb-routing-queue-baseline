"""s32 -- THE COHORT RECONCILIATION.  Round twenty-one, review comment M1.

THE DEFECT.  BPI Challenge 2014 carries the case study of Section 7 and one
row of the corpus of Section 6, and the two disagree about the sign of the
register's increment at the later decision time.  Section 7.1 reports
-0.0032 [-0.0079, +0.0013] against intake + group + knowledge and calls it
indistinguishable from zero; the planned contrast PC3 reports +0.00768 with a
Holm-adjusted p of 0.0025 and rejects.  Both numbers are computed by this
repository, both are correct for what they compute, and the manuscript did not
say what the difference was.

THIS FILE MEASURES IT, ONE FACTOR AT A TIME.  Three things differ between the
two analyses and each is an axis of this paper's own design space:

  ORDERING   both analyses sort the log in time and split at 70% of the row
             order, and 270 incidents share a timestamp with another.  How
             those ties are broken decides which cases fall either side of
             the split point.  Neither analysis declared a rule.
  COHORT     the case study admits incidents opened on or after the registered
             cutoff (45,455 of them); the corpus rules admit 46,606.  The
             first set is a strict subset of the second.
  TARGET     the case study predicts reassignment to another group before
             resolution (prevalence 0.372); the corpus rules define handover
             between activity groups (prevalence 0.927).

TWO FURTHER DIFFERENCES WERE SUSPECTED AND ARE NOT ONES.  The two analyses
reach the assignment-group and knowledge-reference fields by different routes
-- one from the Open event of the activity file, one from the incident file --
and this file checks whether they agree row by row rather than assuming it.
They agree on every row.  The intake block and the register agree on every row
as well.  So the field-definition axis is degenerate here and is reported as
such rather than left as a possibility a reader has to rule out.

THE TIE-BREAK IS A FINDING, NOT ONLY A NUISANCE.  The published case-study
number came from `sort_values`, whose default is not a stable sort, so the
order among tied timestamps was neither declared nor reproducible.  This file
sweeps the tie-break over random permutations and reports the spread it
induces, which is a specification axis nobody declares and which this paper's
own case study was standing on.

The design is the full 2 x 2 x 2 factorial at three rungs of the ladder, one
estimator, one seed, and a nested moving-block bootstrap in every cell.  The
output is the reconciliation table Section 7 prints, and an exact ANOVA
decomposition of the discrepancy over the three factors -- which is the same
decomposition Section 4 applies to the surface, applied to this paper's own
inconsistency.

    python s32_cohort.py                 # 400 draws, all 24 cells
    python s32_cohort.py --draws 20      # smoke test

Outputs: results/s32_cells.csv       one row per (ordering, cohort, target,
                                     rung): V, se, basic interval, resolved
         results/s32_anova.csv       the exact decomposition of the
                                     discrepancy at the knowledge rung
         results/s32_path.csv        the one-factor-at-a-time path from the
                                     published case-study cell to PC3's cell
         results/s32_tiebreak.csv    the increment under random tie-breaks
         results/s32_facts.csv
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
N_TIEBREAK = 25

ORDERINGS = ("source_order", "identifier")
COHORTS = ("reassignment", "registered")
TARGETS = ("reassignment", "handover")
RUNGS = ("B_intake", "B_intake_g", "B_intake_g_km")

INTAKE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"
GFIELD = "assignment group"
KMFIELD = "KM number"

RUNG_COLS = {
    "B_intake": INTAKE,
    "B_intake_g": INTAKE + [GFIELD],
    "B_intake_g_km": INTAKE + [GFIELD, KMFIELD],
}

_FRAME = None


# --------------------------------------------------------------------------
def base_frame():
    """One frame carrying every row either analysis admits, both orderings,
    both targets, and the check that the two routes to the group and
    knowledge fields agree."""
    global _FRAME
    if _FRAME is not None:
        return _FRAME
    import base14 as B
    import s01_surface as S01

    d, ladder, f, meta = S01.prepare("BPIC14", "handover")
    if f != IDENT:
        raise RuntimeError("the register is %r, not %r" % (f, IDENT))
    A = B.D
    iid = d["Incident ID"].astype(str)

    #  the case study's own fields and target, carried over by incident id
    m_g = dict(zip(A["Incident ID"].astype(str), A["intake_group"].astype(str)))
    m_k = dict(zip(A["Incident ID"].astype(str), A["km_number"].astype(str)))
    m_y = dict(zip(A["Incident ID"].astype(str), A["_y"].astype(int)))

    d = d.copy()
    d["_cs_g"] = iid.map(m_g)
    d["_cs_km"] = iid.map(m_k)
    d["_in_case_cohort"] = iid.isin(m_y).values
    d["_y_handover"] = d["_y"].astype(int)
    ra = pd.to_numeric(d["# Reassignments"], errors="coerce")
    d["_y_reassignment"] = (ra >= 1).astype("Int64")

    #  the time key both analyses sort on, and the source file's row order,
    #  which is the only tie-break either of them could have been using.
    d["_t"] = pd.to_datetime(d["Open Time"], format="%d/%m/%Y %H:%M:%S",
                             errors="coerce", dayfirst=True)
    from common import RAW
    raw = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                      encoding="latin-1")
    raw.columns = [c.strip() for c in raw.columns]
    file_row = dict(zip(raw["Incident ID"].astype(str),
                        np.arange(len(raw), dtype=float)))
    d["_file_row"] = iid.map(file_row).values
    d.attrs["n_ties"] = int(d["_t"].duplicated().sum())

    #  the field-definition check: does the activity-file route agree with the
    #  incident-file route wherever both exist?
    m = d["_cs_g"].notna()
    agree_g = float((d.loc[m, "_cs_g"].astype(str)
                     == d.loc[m, GFIELD].astype(str)).mean())
    agree_km = float((d.loc[m, "_cs_km"].astype(str)
                      == d.loc[m, KMFIELD].astype(str)).mean())
    d.attrs["agree_g"] = agree_g
    d.attrs["agree_km"] = agree_km
    d.attrs["n_case_cohort"] = int(d["_in_case_cohort"].sum())
    d.attrs["n_registered"] = int(len(d))
    #  the case study drops rows whose reassignment count will not parse; the
    #  registered cohort does not, so the target is undefined on some of its
    #  rows and this is how many.
    d.attrs["n_target_undefined"] = int(d["_y_reassignment"].isna().sum())
    _FRAME = d
    return d


def cell_frame(ordering, cohort, tiebreak_seed=None):
    """The rows and the row order one (ordering, cohort) combination gives.

    Both orderings sort on the same timestamp.  They differ only in what
    breaks a tie: the source file's row order, or the incident identifier.
    `tiebreak_seed` replaces both with a random permutation, which is how the
    tie-break sweep measures the axis rather than asserting it is small.
    """
    d = base_frame()
    if cohort == "reassignment":
        d = d[d["_in_case_cohort"]]
    d = d[d["_t"].notna()]
    if tiebreak_seed is not None:
        key = np.random.default_rng(tiebreak_seed).permutation(len(d))
        d = d.assign(_tb=key)
    elif ordering == "source_order":
        d = d.assign(_tb=d["_file_row"].values)
    else:
        d = d.assign(_tb=d["Incident ID"].astype(str).values)
    return d.sort_values(["_t", "_tb"], kind="mergesort").reset_index(
        drop=True)


def point(task):
    """One cell.  Returns (row, err)."""
    ordering, cohort, target, rung, draws = task
    t0 = time.time()
    try:
        d = cell_frame(ordering, cohort)
        yv = d["_y_reassignment" if target == "reassignment"
               else "_y_handover"]

        keep = yv.notna().values
        d = d[keep].reset_index(drop=True)
        d = d.assign(_y=yv[keep].astype(int).values)
        cols = list(RUNG_COLS[rung])
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri0, tei0 = np.arange(cut), np.arange(cut, n)

        def one(tri, tei):
            tr, te = d.iloc[tri], d.iloc[tei]
            y = te["_y"].values
            if len(np.unique(y)) < 2:
                return np.nan
            from sklearn.metrics import roc_auc_score
            p1 = S._onehot_logit(tr, te, cols + [IDENT], tr["_y"].values,
                                 S.SEED)
            p0 = S._onehot_logit(tr, te, cols, tr["_y"].values, S.SEED)
            return float(roc_auc_score(y, p1) - roc_auc_score(y, p0))

        V = one(tri0, tei0)
        draws_v = []
        for b in range(draws):
            rng = np.random.default_rng(S.SEED + 7919 * b)
            v = one(tri0[S.block_indices(len(tri0), rng)],
                    tei0[S.block_indices(len(tei0), rng)])
            if np.isfinite(v):
                draws_v.append(v)
        a = np.asarray(draws_v, float)
        if len(a) >= 10:
            qa = float(np.percentile(a, 100 * ALPHA / 2))
            qb = float(np.percentile(a, 100 * (1 - ALPHA / 2)))
            lo, hi = V - (qb - V), V - (qa - V)
            se = float(a.std(ddof=1))
            #  the one-sided plus-one p-value for V <= 0, the estimator PC3
            #  uses, computed here from the same draws as the interval so the
            #  two cannot be read as inconsistent without the reader seeing
            #  both.
            p_one = float((int((a <= 0).sum()) + 1) / (len(a) + 1))
        else:
            lo = hi = se = p_one = np.nan
        return dict(ordering=ordering, cohort=cohort, target=target,
                    rung=rung, n=n, n_train=cut, n_test=n - cut,
                    prevalence=float(d["_y"].mean()), V=V, se=se, lo=lo,
                    hi=hi, p_one_sided=p_one, n_draws=len(a),
                    resolved=bool(np.isfinite(lo) and (lo > 0 or hi < 0)),
                    runtime_s=round(time.time() - t0, 1)), None
    except Exception as e:
        return None, dict(ordering=ordering, cohort=cohort, target=target,
                          rung=rung, reason="ERROR:%s" % e,
                          trace=traceback.format_exc()[-600:])


def tiebreak_one(task):
    """One random tie-break, at the case study's own cell."""
    seed, rung = task
    from sklearn.metrics import roc_auc_score
    d = cell_frame("source_order", "reassignment", tiebreak_seed=seed)
    d = d.assign(_y=d["_y_reassignment"].astype(int).values)
    cols = list(RUNG_COLS[rung])
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tr, te = d.iloc[:cut], d.iloc[cut:]
    y = te["_y"].values
    p1 = S._onehot_logit(tr, te, cols + [IDENT], tr["_y"].values, S.SEED)
    p0 = S._onehot_logit(tr, te, cols, tr["_y"].values, S.SEED)
    return dict(seed=seed, rung=rung,
                V=float(roc_auc_score(y, p1) - roc_auc_score(y, p0)))


def published_cell(rung):
    """The number the manuscript printed, recomputed from the case study's own
    loader so that the reconciliation's anchor is the published object rather
    than a reconstruction of it."""
    import base14 as B
    from sklearn.metrics import roc_auc_score
    d = B.D
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tr, te = d.iloc[:cut], d.iloc[cut:]
    cols = [c if c not in (GFIELD, KMFIELD) else
            {"assignment group": "intake_group",
             "KM number": "km_number"}[c] for c in RUNG_COLS[rung]]
    y = te["_y"].values
    p1 = S._onehot_logit(tr, te, cols + [IDENT], tr["_y"].values, S.SEED)
    p0 = S._onehot_logit(tr, te, cols, tr["_y"].values, S.SEED)
    return float(roc_auc_score(y, p1) - roc_auc_score(y, p0))


def anova(C, rung, ordering="source_order"):
    """The exact two-factor decomposition of V over the cohort x target design
    at one rung, at a fixed tie-break rule.  With two levels per factor every
    effect is a single contrast and the decomposition is exact, which is the
    same statement Section 4 makes about the surface.  The tie-break is held
    fixed here and swept separately, because a factor whose two declared
    levels coincide exactly would contribute a zero share and read as an
    error rather than as the finding it is."""
    sub = C[(C.rung == rung) & (C.ordering == ordering)]
    idx = {(r.cohort, r.target): float(r.V) for r in sub.itertuples()}
    if len(idx) != 4:
        return pd.DataFrame()
    lev = dict(cohort=COHORTS, target=TARGETS)
    names = ("cohort", "target")

    def code(f, v):
        return -1.0 if v == lev[f][0] else 1.0

    rows = []
    grand = float(np.mean(list(idx.values())))
    rows.append(dict(rung=rung, effect="grand mean", value=grand,
                     share=np.nan))
    ss_tot = float(np.sum([(v - grand) ** 2 for v in idx.values()]))
    for r in (1, 2):
        for combo in itertools.combinations(range(2), r):
            tot = 0.0
            for k in idx:
                c = 1.0
                for j in combo:
                    c *= code(names[j], k[j])
                tot += c * idx[k]
            eff = tot / 4.0
            ss = 4.0 * eff ** 2
            rows.append(dict(rung=rung,
                             effect=" x ".join(names[j] for j in combo),
                             value=2.0 * eff,
                             share=ss / ss_tot if ss_tot > 0 else np.nan))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=N_BOOT)
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    d = base_frame()
    print("=" * 92)
    print("s32  THE COHORT RECONCILIATION")
    print("=" * 92)
    print("  registered cohort            %d" % d.attrs["n_registered"])
    print("  case-study cohort            %d" % d.attrs["n_case_cohort"])
    print("  incidents sharing a timestamp %d" % d.attrs["n_ties"])
    print("  group field agreement        %.6f" % d.attrs["agree_g"])
    print("  knowledge field agreement    %.6f" % d.attrs["agree_km"])
    print("  reassignment target undefined on %d registered rows"
          % d.attrs["n_target_undefined"])

    tasks = [(o, c, t, r, a.draws)
             for o in ORDERINGS for c in COHORTS
             for t in TARGETS for r in RUNGS]
    print("  %d cells at %d draws" % (len(tasks), a.draws), flush=True)
    R, X = [], []
    if a.serial:
        for t in tasks:
            row, err = point(t)
            (R if row else X).append(row or err)
            print("   .", flush=True)
    else:
        import multiprocessing as mp
        with mp.Pool(processes=min(12, max(1, (os.cpu_count() or 4) - 2))) as pool:
            for row, err in pool.imap_unordered(point, tasks):
                if row:
                    R.append(row)
                    print("  [%s/%s/%s/%s] V=%+.5f [%+.5f,%+.5f] %.0fs"
                          % (row["ordering"], row["cohort"], row["target"],
                             row["rung"], row["V"], row["lo"], row["hi"],
                             row["runtime_s"]), flush=True)
                else:
                    X.append(err)
                    print("  FAILED %s" % err, flush=True)
    C = pd.DataFrame(R).sort_values(["rung", "ordering", "cohort", "target"])
    C.to_csv(RESULTS / "s32_cells.csv", index=False)

    AN = pd.concat([anova(C, r) for r in RUNGS], ignore_index=True) \
        if len(C) else pd.DataFrame()
    AN.to_csv(RESULTS / "s32_anova.csv", index=False)

    #  the tie-break sweep, at the case study's own cell
    TB = []
    tb_tasks = [(1000 + i, "B_intake_g_km") for i in range(N_TIEBREAK)]
    if a.serial:
        TB = [tiebreak_one(t) for t in tb_tasks]
    else:
        import multiprocessing as mp
        with mp.Pool(processes=min(12, max(1, (os.cpu_count() or 4) - 2))) as pool:
            TB = list(pool.imap_unordered(tiebreak_one, tb_tasks))
    TBD = pd.DataFrame(TB).sort_values("seed")
    v_pub = published_cell("B_intake_g_km")
    TBD["published"] = v_pub
    TBD.to_csv(RESULTS / "s32_tiebreak.csv", index=False)

    #  the one-factor-at-a-time path from the published case-study cell to
    #  PC3's cell, at the knowledge rung
    path_keys = [("source_order", "reassignment", "reassignment",
                  "the case study, tie-break declared"),
                 ("identifier", "reassignment", "reassignment",
                  "then the other tie-break rule"),
                 ("identifier", "registered", "reassignment",
                  "then the registered cohort"),
                 ("identifier", "registered", "handover",
                  "then the registered target")]
    P = [dict(step="the case study as published", ordering="undeclared",
              cohort="reassignment", target="reassignment", V=v_pub,
              lo=np.nan, hi=np.nan, resolved=False, delta=np.nan)]
    prev = v_pub
    for o, c, t, lab in path_keys:
        m = C[(C.ordering == o) & (C.cohort == c) & (C.target == t)
              & (C.rung == "B_intake_g_km")]
        if not len(m):
            continue
        v = float(m.V.iloc[0])
        P.append(dict(step=lab, ordering=o, cohort=c, target=t, V=v,
                      lo=float(m.lo.iloc[0]), hi=float(m.hi.iloc[0]),
                      resolved=bool(m.resolved.iloc[0]),
                      delta=(np.nan if prev is None else v - prev)))
        prev = v
    PA = pd.DataFrame(P)
    PA.to_csv(RESULTS / "s32_path.csv", index=False)

    km = C[C.rung == "B_intake_g_km"]
    facts = dict(
        n_registered=d.attrs["n_registered"],
        n_case_cohort=d.attrs["n_case_cohort"],
        n_extra=d.attrs["n_registered"] - d.attrs["n_case_cohort"],
        n_ties=d.attrs["n_ties"],
        agree_g=d.attrs["agree_g"], agree_km=d.attrs["agree_km"],
        n_target_undefined=d.attrs["n_target_undefined"],
        n_cells=len(C), n_failed=len(X), n_draws=a.draws,
        n_resolved=int(km.resolved.sum()) if len(km) else 0,
        n_km_cells=len(km),
        n_sign_positive=int((km.V > 0).sum()) if len(km) else 0,
        v_published_case=v_pub,
        n_tiebreak=len(TBD),
        tiebreak_min=float(TBD.V.min()), tiebreak_max=float(TBD.V.max()),
        tiebreak_sd=float(TBD.V.std(ddof=1)),
        tiebreak_range=float(TBD.V.max() - TBD.V.min()),
        tiebreak_sign_positive=int((TBD.V > 0).sum()),
        v_pc3=float(
            C[(C.ordering == "identifier") & (C.cohort == "registered")
              & (C.target == "handover")
              & (C.rung == "B_intake_g_km")].V.iloc[0]) if len(C) else np.nan,
        share_target=float(
            AN[(AN.rung == "B_intake_g_km")
               & (AN.effect == "target")].share.iloc[0]) if len(AN) else np.nan,
        share_cohort=float(
            AN[(AN.rung == "B_intake_g_km")
               & (AN.effect == "cohort")].share.iloc[0]) if len(AN) else np.nan,
        share_interaction=float(
            AN[(AN.rung == "B_intake_g_km")
               & (AN.effect == "cohort x target")].share.iloc[0])
        if len(AN) else np.nan,
        n_ordering_rules_agree=int(
            (C[C.ordering == "source_order"].sort_values(
                ["cohort", "target", "rung"]).V.values
             == C[C.ordering == "identifier"].sort_values(
                ["cohort", "target", "rung"]).V.values).sum())
        if len(C) == 24 else 0,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s32_facts.csv", index=False)
    print("\n" + C.to_string(index=False))
    print("\n" + AN.to_string(index=False))
    print("\n" + PA.to_string(index=False))
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s32_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

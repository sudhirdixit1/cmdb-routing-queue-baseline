"""s27 -- REGISTER QUALITY: SEVERITY CURVES, TWENTY SEEDS, AND MECHANISMS
THAT DEPEND ON SOMETHING.

Round twenty, blueprint P1.3.

Round nineteen's register-quality axis had three defects.  It sampled each
stochastic mechanism at three seeds, which cannot separate what the mechanism
does from what one realisation of it did.  It sampled severity at two or three
arbitrary points, so a conclusion could be moved by refining the grid.  And
every mechanism was independent of everything -- a register value went missing
because a coin came up tails, never because of when the row was created, what
kind of item it was, or how the incident behaved.

Real registers do not fail at random.  A configuration management database is
populated late for a new service, is thin for a class of items nobody
discovers, and is missing exactly where the work is unusual.

WHAT THIS FILE ADDS.

  1  SEVERITY CURVES.  Every mechanism is swept over a fine grid rather than
     evaluated at two points, and the summary quantity is an integral against
     a declared continuous measure on severity, so refining the grid does not
     move it.  The coarse and fine grids are both computed and compared.

  2  TWENTY SEEDS for every stochastic mechanism, and MECHANISM VARIABILITY IS
     REPORTED SEPARATELY FROM SAMPLING VARIABILITY: the spread across seeds at
     a fixed cell answers "what could this mechanism have done", which is a
     different question from "how precisely is this estimated", and s20's
     bootstrap answers the second.

  3  THREE DEPENDENT MECHANISMS, none of which touches a test outcome:

     time      the register was populated late.  A row's probability of
               carrying an identity rises with its position in time; the
               profile is fixed a priori, not fitted.
     content   discovery covers some item classes and not others.  The
               probability that a value survives depends on ANOTHER recorded
               field of the same row -- the item's type -- through a map
               estimated on the TRAINING half alone.
     propensity the register is missing where the work is unusual.  The
               probability is a function of a training-estimated propensity
               score built from the intake block only.  This is
               outcome-dependent missingness in the sense that matters --
               missingness correlated with the outcome -- built without ever
               reading a test outcome, which `assert_train_only` verifies.

  4  WHAT `duplicate` MEANS.  An identity that exists twice in the register:
     the same physical item reconciled under two keys, so half its rows carry
     one and half the other.  That is a reconciliation failure, and it is
     distinct from a population failure because no row is empty.

    python s27_quality.py
    python s27_quality.py --seeds 5 --levels 5     # a smoke test

Outputs: results/s27_curves.csv     every (mechanism, severity, seed) cell
         results/s27_summary.csv    integrals, seed spread, grid comparison
         results/s27_leakage.csv    the executed train-only checks
         results/s27_facts.csv
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

PRIMARY = "BPIC14"
RUNG = "B_intake_g"
LEARNERS = ("logit", "hgb")

DETERMINISTIC = ("mask_rare", "mask_common", "time")
STOCHASTIC = ("mask_random", "corrupt", "duplicate", "content", "propensity")

MECH_MEANING = {
    "mask_rare": "population: the long tail of identities is absent",
    "mask_common": "population: the core identities are absent",
    "mask_random": "population: absent independently of everything",
    "corrupt": "accuracy: a share of rows carry the wrong identity",
    "duplicate": "reconciliation: one item exists under two keys",
    "time": "discovery: the register was populated late",
    "content": "discovery: coverage depends on the item's type",
    "propensity": "missing where the work is unusual: a training-estimated "
                  "propensity drives the missingness",
}


# --------------------------------------------------------------------------
def degrade_extra(col, kind, level, rng, train_index, d, log):
    """The three dependent mechanisms.  `level` is the share POPULATED, so
    level = 1 is a clean register and level = 0 an empty one, matching the
    mask_* convention.  Nothing here reads an outcome of a test row."""
    s = col.astype(str).copy()
    n = len(s)
    if kind == "time":
        #  a linear ramp in position: the earliest rows are the least likely
        #  to carry an identity, which is what a register populated over time
        #  looks like when read backwards.  The profile is fixed a priori.
        pos = np.arange(n) / float(max(1, n - 1))
        keep_p = np.clip(2.0 * level * pos, 0.0, 1.0)
        #  deterministic: keep the rows whose ramp value exceeds the
        #  complement, so the mechanism has no seed
        return s.where(keep_p >= (1.0 - keep_p), S.EMPTY)
    if kind == "content":
        #  coverage by item type, with the per-type keep probability drawn
        #  once from the TRAINING distribution of that type's frequency
        c = None
        for cand in ("CI Type (aff)", "CI Subtype (aff)", "Category",
                     "product", "impact"):
            if cand in d.columns:
                c = cand
                break
        if c is None:
            return s
        t = d[c].astype(str)
        tr_t = t.iloc[train_index]
        types = sorted(tr_t.unique())
        #  a type's keep probability is level scaled by a type-specific
        #  factor drawn once; identical types share a fate, which is what
        #  makes this dependent rather than independent noise
        fac = rng.random(len(types))
        m = dict(zip(types, np.clip(2.0 * level * fac, 0.0, 1.0)))
        p = t.map(m).fillna(float(level)).values.astype(float)
        return s.where(rng.random(n) < p, S.EMPTY)
    if kind == "propensity":
        #  a propensity built on the TRAINING half only, from the intake
        #  block, and used to drive missingness.  The propensity model sees
        #  training outcomes; the test rows are only SCORED by it, so no test
        #  outcome is read.  assert_train_only checks the whole map.
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import OneHotEncoder
        cols = [c for c in ("Category", "Impact", "Urgency", "Priority",
                            "impact", "product", "category", "urgency")
                if c in d.columns][:4]
        if not cols:
            return s
        e = OneHotEncoder(handle_unknown="ignore")
        X = e.fit_transform(d[cols].astype(str).iloc[train_index])
        y = d["_y"].values[train_index]
        if len(np.unique(y)) < 2:
            return s
        mdl = LogisticRegression(max_iter=1000).fit(X, y)
        pr = mdl.predict_proba(e.transform(d[cols].astype(str)))[:, 1]
        #  Rank-normalise so `level` is the share populated in expectation,
        #  and let the propensity decide WHICH rows survive.
        #
        #  THE RANK MUST BE TAKEN AGAINST THE TRAINING HALF ALONE.  A rank
        #  over all rows makes a training row's rank depend on the test
        #  rows' propensities, so perturbing the test half changes the
        #  training half's degraded values -- which is exactly what
        #  `assert_train_only_extra` is for, and exactly what it caught when
        #  this mechanism was first written.  The training empirical CDF is
        #  fitted once and every row, training or test, is mapped through it.
        ref = np.sort(pr[train_index])
        r = np.searchsorted(ref, pr, side="right") / float(max(1, len(ref)))
        keep = np.clip(2.0 * level * (1.0 - r), 0.0, 1.0)
        return s.where(rng.random(n) < keep, S.EMPTY)
    return S.degrade(col, kind, level, rng, train_index)


def assert_train_only_extra(d, f, kind, level, seed, train_index, log):
    """The dependent mechanisms must not change when the TEST half changes."""
    a = degrade_extra(d[f], kind, level, np.random.default_rng(seed),
                      train_index, d, log)
    d2 = d.copy()
    tail = np.arange(len(d)) > int(np.max(train_index))
    for c in d2.columns:
        #  Perturb the columns a mechanism can READ, which are the recorded
        #  attributes.  Writing a string into a float or datetime column
        #  would only produce a dtype warning and a coerced value, and the
        #  point of the check is what a mechanism does with a CHANGED TEST
        #  HALF, not what pandas does with a type error.
        if c == "_y" or d2[c].dtype.kind not in "OUS":
            continue
        d2.loc[tail, c] = "__PERTURBED__"
    b = degrade_extra(d2[f], kind, level, np.random.default_rng(seed),
                      train_index, d2, log)
    return bool((a.iloc[train_index].values
                 == b.iloc[train_index].values).all())


# --------------------------------------------------------------------------
#: one prepared log per worker.  Without this, `prepare` is re-run for every
#: one of the several thousand cells and costs more than the fits do.
_PREPARED = {}


def prepare_cached(log, target):
    key = (log, target)
    if key not in _PREPARED:
        _PREPARED.clear()
        _PREPARED[key] = S01.prepare(log, target)
    return _PREPARED[key]


def one_cell(args):
    log, target, learner, kind, level, seed = args
    try:
        d, ladder, f, meta = prepare_cached(log, target)
        rungs = {nm: c for nm, c in ladder}
        cols = list(rungs[RUNG])
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri, tei = np.arange(cut), np.arange(cut, n)
        yte = d["_y"].values[tei]
        prev = float(d["_y"].values[tri].mean())
        rng = np.random.default_rng(S.SEED + 7919 * seed)
        dd = d.copy()
        dd["_f"] = degrade_extra(d[f], kind, level, rng, tri, d, log)
        tr, te = dd.iloc[tri], dd.iloc[tei]
        p0 = S.LEARNERS[learner](tr, te, cols, tr["_y"].values, S.SEED)
        p1 = S.LEARNERS[learner](tr, te, cols + ["_f"], tr["_y"].values,
                                 S.SEED)
        M0 = S.all_metrics(p0, yte, prev)
        M1 = S.all_metrics(p1, yte, prev)
        out = []
        for m in S.SCALARS:
            out.append(dict(log=log, target=target, learner=learner,
                            mechanism=kind, level=level, seed=seed, metric=m,
                            V=M1[m] - M0[m], without_f=M0[m], with_f=M1[m],
                            populated=float((dd["_f"] != S.EMPTY).mean())))
        return out
    except Exception:  # noqa: BLE001
        sys.stderr.write("%s\n" % traceback.format_exc()[-400:])
        return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--levels", type=int, default=21)
    ap.add_argument("--procs", type=int, default=0)
    ap.add_argument("--targets", default="handover,duration",
                    help="comma-separated, for a smoke test")
    a = ap.parse_args(argv)
    t0 = time.time()
    nproc = a.procs or min(12, max(1, (os.cpu_count() or 4) - 2))

    levels = np.round(np.linspace(0.0, 1.0, a.levels), 4)
    tasks = []
    for target in [x for x in a.targets.split(",") if x]:
        for learner in LEARNERS:
            for kind in DETERMINISTIC:
                for lv in levels:
                    tasks.append((PRIMARY, target, learner, kind, float(lv), 0))
            for kind in STOCHASTIC:
                lv_levels = (levels if kind != "corrupt"
                             else np.round(levels * 0.5, 4))
                for lv in lv_levels:
                    for sd in range(a.seeds):
                        tasks.append((PRIMARY, target, learner, kind,
                                      float(lv), sd))
    print("=" * 92)
    print("s27  SEVERITY CURVES, %d SEEDS, DEPENDENT MECHANISMS" % a.seeds)
    print("=" * 92)
    print("  %d cells" % len(tasks))

    rows = []
    import multiprocessing as mp
    with mp.Pool(processes=nproc) as pool:
        for i, r in enumerate(pool.imap_unordered(one_cell, tasks,
                                                  chunksize=4)):
            rows += r
            if (i + 1) % 400 == 0:
                print("    %d/%d  %.0fs" % (i + 1, len(tasks),
                                            time.time() - t0), flush=True)
    C = pd.DataFrame(rows)
    C.to_csv(RESULTS / "s27_curves.csv.gz", index=False, compression="gzip")

    # ---- leakage checks -------------------------------------------------
    lk = []
    for target in ("handover", "duration"):
        d, ladder, f, meta = S01.prepare(PRIMARY, target)
        n = len(d)
        tri = np.arange(int(n * S.TRAIN_FRAC))
        for kind in list(DETERMINISTIC) + list(STOCHASTIC):
            ok = assert_train_only_extra(d, f, kind, 0.5, S.SEED, tri, PRIMARY)
            lk.append(dict(log=PRIMARY, target=target, mechanism=kind,
                           meaning=MECH_MEANING[kind], train_only=bool(ok)))
    LK = pd.DataFrame(lk)
    LK.to_csv(RESULTS / "s27_leakage.csv", index=False)
    print("\nTRAIN-ONLY CHECKS: %d of %d passed"
          % (int(LK.train_only.sum()), len(LK)))

    # ---- severity integrals and grid refinement -------------------------
    #  The summary is the integral of the increment against a UNIFORM measure
    #  on severity, computed by the trapezoid rule.  Refining the grid under
    #  the same measure must not move it.
    summ = []
    for (target, learner, mech, metric), g in C.groupby(
            ["target", "learner", "mechanism", "metric"]):
        m = g.groupby("level").V.mean().sort_index()
        if len(m) < 3:
            continue
        fine = float(np.trapezoid(m.values, m.index.values)
                     / (m.index.max() - m.index.min()))
        coarse_idx = m.index[::4]
        mc = m.loc[coarse_idx]
        #  a coarse grid of fewer than three points has no integral worth
        #  comparing; the smoke-test grids are that small and the real ones
        #  are not, so this reports NaN rather than a number that means
        #  nothing.
        coarse = (float(np.trapezoid(mc.values, mc.index.values)
                        / (mc.index.max() - mc.index.min()))
                  if len(mc) >= 3 and mc.index.max() > mc.index.min()
                  else np.nan)
        #  mechanism variability: the spread ACROSS SEEDS at a fixed severity
        sd = g.groupby("level").V.std(ddof=1)
        summ.append(dict(
            target=target, learner=learner, mechanism=mech,
            meaning=MECH_MEANING[mech], metric=metric,
            n_levels=len(m), n_seeds=int(g.seed.nunique()),
            integral_fine=fine, integral_coarse=coarse,
            grid_shift=abs(fine - coarse),
            V_at_clean=float(m.loc[m.index.max()]),
            V_at_half=float(m.iloc[len(m) // 2]),
            V_at_empty=float(m.loc[m.index.min()]),
            seed_sd_median=float(sd.median()) if sd.notna().any() else 0.0,
            seed_sd_max=float(sd.max()) if sd.notna().any() else 0.0,
            n_sign_changes=int((np.diff(np.sign(m.values)) != 0).sum())))
    SM = pd.DataFrame(summ)
    SM.to_csv(RESULTS / "s27_summary.csv", index=False)
    print("\nSEVERITY INTEGRALS, AUC, handover")
    sel = SM[(SM.metric == "auc") & (SM.target == "handover")]
    print(sel[["learner", "mechanism", "integral_fine", "integral_coarse",
               "grid_shift", "seed_sd_median", "V_at_clean",
               "V_at_empty"]].to_string(
        index=False, float_format=lambda x: "%.4f" % x))

    #  mechanism variability against sampling variability, where s20 has a
    #  matching cell
    #  This block reads s21's per-cell standard errors, so s27 must run AFTER
    #  s21.  It did not, for one round: the chain ran s27 first, the file was
    #  the previous round's, no cell matched, and the comparison silently
    #  produced nothing -- which reached the manuscript as an unresolved
    #  macro rather than as a wrong number, but only because every macro is
    #  checked.  The dependency is now stated in the wave list, and the
    #  failure below is printed rather than swallowed.
    cmp_rows = []
    try:
        src = RESULTS / "s21_cells.csv"
        if not src.exists():
            raise FileNotFoundError(
                "results/s21_cells.csv does not exist; s27 must run after "
                "s21_bands.py, which produces it")
        CE = pd.read_csv(src)
        for _, r in SM[SM.metric == "auc"].iterrows():
            q = CE[(CE.log == PRIMARY) & (CE.target == r.target)
                   & (CE.learner == r.learner) & (CE.rung == RUNG)
                   & (CE.metric == "auc")]
            if len(q):
                cmp_rows.append(dict(
                    target=r.target, learner=r.learner,
                    mechanism=r.mechanism,
                    mechanism_sd=r.seed_sd_median,
                    sampling_se=float(q.se.median()),
                    ratio=(r.seed_sd_median / float(q.se.median())
                           if float(q.se.median()) > 0 else np.nan)))
    except Exception as exc:  # noqa: BLE001
        print("  !! mechanism-vs-sampling comparison skipped: %s" % exc,
              flush=True)
    CMP = pd.DataFrame(cmp_rows)
    if not len(CMP):
        print("  !! no s21 cell matched a mechanism summary row, so "
              "mechanism_vs_sampling_median is NaN and the macro that reads "
              "it will be unresolved", flush=True)
    if len(CMP):
        CMP.to_csv(RESULTS / "s27_variability.csv", index=False)

    st = SM[SM.metric == "auc"]
    facts = dict(
        n_cells=len(C), n_seeds=a.seeds, n_levels=a.levels,
        n_mechanisms=int(C.mechanism.nunique()),
        n_dependent_mechanisms=3,
        leakage_checked=len(LK), leakage_passed=int(LK.train_only.sum()),
        grid_shift_max=float(st.grid_shift.max()),
        grid_shift_median=float(st.grid_shift.median()),
        seed_sd_max=float(st.seed_sd_max.max()),
        seed_sd_median=float(st.seed_sd_median.median()),
        n_mechanisms_sign_changing=int((st.n_sign_changes > 0).sum()),
        mechanism_vs_sampling_median=float(CMP.ratio.median())
        if len(CMP) else np.nan,
        runtime_s=round(time.time() - t0, 1))
    for mech in list(DETERMINISTIC) + list(STOCHASTIC):
        g = st[(st.mechanism == mech) & (st.target == "handover")
               & (st.learner == "logit")]
        if len(g):
            facts["integral_" + mech] = float(g.integral_fine.iloc[0])
            facts["empty_" + mech] = float(g.V_at_empty.iloc[0])
    pd.DataFrame([facts]).to_csv(RESULTS / "s27_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

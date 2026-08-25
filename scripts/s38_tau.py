"""s38 -- THE DECISION TIME AS AN AXIS THAT DOES SOMETHING.  M2.

THE OBJECTION.  Table 13's rows for the two decision times were identical to
every digit, because nothing changed between them except which baseline was
admissible.  A decision time implemented as a relabelling of the baseline
ladder is not a separate axis, and the manuscript should either implement it
or fold it into the baseline and say so.

THIS FILE IMPLEMENTS IT.  A decision time in this estate names a moment in the
service-desk process, and three things change with it: WHICH CASES ARE IN
SCOPE, WHAT IS KNOWN ABOUT THEM, and WHICH FIELDS ARE ADMISSIBLE.  Three
moments are estimated, and the pairwise differences isolate the three
mechanisms.

  T0  FIRST TOUCH, EVERY CALL.  A caller reaches the desk and an interaction
      is opened.  The population is every interaction; the desk does not yet
      know which will escalate.  The register is the interaction's own
      affected configuration item; the baseline is the interaction's intake
      block.  The question is whether this call will become an incident that
      bounces between groups.

  T1  FIRST TOUCH, THE CALLS THAT ESCALATE.  The same moment and the same
      fields, restricted to the calls that did become incidents.  Comparing
      T1 with T0 isolates the COHORT AT THE DECISION TIME, holding the
      information constant.

  T2  INCIDENT CREATION.  The desk has worked the interaction and escalated
      it.  The population is the incidents; the register is the incident's
      affected item, and the assignment group and knowledge reference exist.
      Comparing T2 with T1 isolates the FEATURE SNAPSHOT and the admissible
      set, holding the cases constant.

THE DECISION IS THE SAME AT ALL THREE and is fixed before any of them: will
this case be reassigned to another group before it is resolved.  That is what
makes the three comparable at all.

WHAT THIS COSTS.  T0 carries 145,478 rows and a register of 4,034 levels, so
its bootstrap is the expensive part of the file; the draws are parallelised
rather than the cells.

    python s38_tau.py                 # 300 draws
    python s38_tau.py --draws 10      # smoke test

Outputs: results/s38_ladder.csv     one row per (decision time, rung)
         results/s38_scope.csv      what is in scope at each decision time
         results/s38_facts.csv
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
from common import RAW, RESULTS  # noqa: E402

ALPHA = 0.05
N_BOOT = 300
CUTOFF = "2013-10-01"
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"

#: (decision time, rung name, columns beyond the register).  The rungs are the
#: admissible sets at that moment and nothing more.
LADDER = {
    "t0_first_touch_all": [("B_intake", INTAKE)],
    "t1_first_touch_escalating": [("B_intake", INTAKE)],
    #  ROUND TWENTY-TWO.  A referee checked the table's own columns against
    #  the sentence above it and was right: T1 carries 44,513 cases and T2
    #  carries 45,455, so "the same cases, changing what is known but not who
    #  is in scope" was false, and the information step was confounded with a
    #  two-per-cent change of population.  T2 MATCHED is T2 restricted to the
    #  cases that have an interaction record -- exactly T1's population -- so
    #  T1 -> T2 matched is the information step with the population held
    #  fixed, and T2 matched -> T2 is the residual the 942 incidents with no
    #  interaction record are worth.  Only the intake rung is needed, because
    #  that is the rung the two deltas are computed at.
    "t2_matched": [("B_intake", INTAKE)],
    "t2_incident_creation": [("B_intake", INTAKE),
                             ("B_intake_g", INTAKE + ["_g"]),
                             ("B_intake_g_km", INTAKE + ["_g", "_km"])],
}

_FRAMES = None


def frames():
    """The three cohorts, built once, each sorted in time and each carrying
    the same target."""
    global _FRAMES
    if _FRAMES is not None:
        return _FRAMES
    import base14 as B

    inc = B.D.copy()                       # the case study's own incidents
    inc["_g"] = inc["intake_group"].astype(str)
    inc["_km"] = inc["km_number"].astype(str)
    inc["_key"] = inc["Incident ID"].astype(str)

    itr = pd.read_csv(RAW / "Detail_Interaction.csv", sep=";",
                      low_memory=False, encoding="latin-1")
    itr.columns = [c.strip() for c in itr.columns]
    itr["_t"] = pd.to_datetime(itr["Open Time (First Touch)"],
                               errors="coerce", dayfirst=True)
    itr = itr.dropna(subset=["_t"])
    itr = itr[itr["_t"] >= CUTOFF]
    itr["_key"] = itr["Related Incident"].astype(str)

    #  the decision, fixed once: is the case reassigned before it resolves.
    #  A call that never becomes an incident is never reassigned, so its
    #  outcome is zero rather than missing.
    y_of = dict(zip(inc["_key"], inc["_y"].astype(int)))
    itr["_y"] = itr["_key"].map(y_of).fillna(0).astype(int)
    itr["_escalates"] = itr["_key"].isin(y_of).astype(int)

    t0 = itr.sort_values(["_t", "Interaction ID"],
                         kind="mergesort").reset_index(drop=True)
    #  T1: the FIRST interaction of each escalating case, at first touch
    esc = itr[itr._escalates == 1]
    t1 = (esc.sort_values(["_t", "Interaction ID"], kind="mergesort")
          .drop_duplicates("_key", keep="first").reset_index(drop=True))
    t2 = inc.sort_values(["_t", "Incident ID"],
                         kind="mergesort").reset_index(drop=True)
    #  T2 on T1's population: the incidents that have an interaction record,
    #  which is what makes the T1 -> T2 step an information step alone.
    t2m = t2[t2["_key"].isin(set(t1["_key"]))].reset_index(drop=True)
    _FRAMES = {"t0_first_touch_all": t0,
               "t1_first_touch_escalating": t1,
               "t2_matched": t2m,
               "t2_incident_creation": t2}
    return _FRAMES


def one(task):
    """One (decision time, rung, draw)."""
    tau, rung, cols, b = task
    from sklearn.metrics import roc_auc_score
    d = frames()[tau]
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
    p1 = S._onehot_logit(tr, te, list(cols) + [IDENT], tr["_y"].values, S.SEED)
    p0 = S._onehot_logit(tr, te, list(cols), tr["_y"].values, S.SEED)
    a1, a0 = float(roc_auc_score(y, p1)), float(roc_auc_score(y, p0))
    return dict(tau=tau, rung=rung, draw=b, base_auc=a0, with_auc=a1,
                V=a1 - a0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=N_BOOT)
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s38  THE DECISION TIME AS AN AXIS THAT DOES SOMETHING")
    print("=" * 92)
    F = frames()
    scope = []
    for tau, d in F.items():
        scope.append(dict(
            decision_time=tau, n=len(d),
            n_train=int(len(d) * S.TRAIN_FRAC),
            prevalence=float(d["_y"].mean()),
            card_register=int(d[IDENT].astype(str).nunique()),
            n_rungs=len(LADDER[tau]),
            escalation_rate=(float(d["_escalates"].mean())
                             if "_escalates" in d.columns else 1.0)))
        print("  %-28s n=%-7d prev=%.4f K=%-5d rungs=%d"
              % (tau, len(d), d["_y"].mean(),
                 d[IDENT].astype(str).nunique(), len(LADDER[tau])))
    SC = pd.DataFrame(scope)
    SC.to_csv(RESULTS / "s38_scope.csv", index=False)

    tasks = []
    for tau, rungs in LADDER.items():
        for rung, cols in rungs:
            for b in [-1] + list(range(a.draws)):
                tasks.append((tau, rung, tuple(cols), b))
    print("  %d fits" % (2 * len(tasks)), flush=True)
    out = []
    if a.serial:
        for t in tasks:
            r = one(t)
            if r:
                out.append(r)
    else:
        import multiprocessing as mp
        done = 0
        with mp.Pool(processes=min(12,
                                   max(1, (os.cpu_count() or 4) - 2))) as pool:
            for r in pool.imap_unordered(one, tasks, chunksize=4):
                done += 1
                if r:
                    out.append(r)
                if done % 200 == 0:
                    print("    %d/%d  %.0fs" % (done, len(tasks),
                                                time.time() - t0), flush=True)
    D = pd.DataFrame(out)
    rows = []
    for (tau, rung), sub in D.groupby(["tau", "rung"]):
        pt = sub[sub.draw < 0]
        bs = sub[sub.draw >= 0].V.values
        if not len(pt):
            continue
        V = float(pt.V.iloc[0])
        if len(bs) >= 10:
            qa = float(np.percentile(bs, 100 * ALPHA / 2))
            qb = float(np.percentile(bs, 100 * (1 - ALPHA / 2)))
            lo, hi = V - (qb - V), V - (qa - V)
            se = float(bs.std(ddof=1))
        else:
            lo = hi = se = np.nan
        s = SC[SC.decision_time == tau].iloc[0]
        rows.append(dict(
            decision_time=tau, rung=rung, n=int(s.n),
            prevalence=float(s.prevalence), card_register=int(s.card_register),
            base_auc=float(pt.base_auc.iloc[0]),
            with_auc=float(pt.with_auc.iloc[0]), V=V, se=se, lo=lo, hi=hi,
            n_draws=len(bs),
            resolved=bool(np.isfinite(lo) and (lo > 0 or hi < 0))))
    L = pd.DataFrame(rows).sort_values(["decision_time", "rung"])
    L.to_csv(RESULTS / "s38_ladder.csv", index=False)
    print("\n" + L.to_string(index=False))

    def get(tau, rung="B_intake"):
        m = L[(L.decision_time == tau) & (L.rung == rung)]
        return float(m.V.iloc[0]) if len(m) else np.nan

    v0 = get("t0_first_touch_all")
    v1 = get("t1_first_touch_escalating")
    v2 = get("t2_incident_creation")
    facts = dict(
        n_decision_times=len(F), n_draws=a.draws,
        n_t0=int(SC[SC.decision_time == "t0_first_touch_all"].n.iloc[0]),
        n_t1=int(SC[SC.decision_time
                    == "t1_first_touch_escalating"].n.iloc[0]),
        n_t2=int(SC[SC.decision_time == "t2_incident_creation"].n.iloc[0]),
        prev_t0=float(SC[SC.decision_time
                         == "t0_first_touch_all"].prevalence.iloc[0]),
        prev_t2=float(SC[SC.decision_time
                         == "t2_incident_creation"].prevalence.iloc[0]),
        card_t0=int(SC[SC.decision_time
                       == "t0_first_touch_all"].card_register.iloc[0]),
        card_t2=int(SC[SC.decision_time
                       == "t2_incident_creation"].card_register.iloc[0]),
        n_t2_matched=int(SC[SC.decision_time == "t2_matched"].n.iloc[0]),
        n_t2_unmatched=int(SC[SC.decision_time
                              == "t2_incident_creation"].n.iloc[0]
                           - SC[SC.decision_time == "t2_matched"].n.iloc[0]),
        prev_t1=float(SC[SC.decision_time
                         == "t1_first_touch_escalating"].prevalence.iloc[0]),
        prev_t2_matched=float(SC[SC.decision_time
                                 == "t2_matched"].prevalence.iloc[0]),
        V_t0_intake=v0, V_t1_intake=v1, V_t2_intake=v2,
        V_t2_matched_intake=get("t2_matched"),
        #  ROUND TWENTY-TWO.  delta_snapshot was V(T2) - V(T1) across two
        #  populations that differ by 942 cases.  It is now the step on the
        #  MATCHED population, which is the information change alone, and the
        #  residual is reported beside it rather than folded into it.
        delta_cohort=v1 - v0,
        delta_snapshot=get("t2_matched") - v1,
        delta_population_residual=v2 - get("t2_matched"),
        delta_snapshot_unmatched=v2 - v1,
        V_t2_group=get("t2_incident_creation", "B_intake_g"),
        V_t2_knowledge=get("t2_incident_creation", "B_intake_g_km"),
        n_resolved=int(L.resolved.sum()), n_cells=len(L),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s38_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s38_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

"""s08 -- TWO DECISION TIMES, TWO SURFACES, AND A LEAKAGE TIPPING POINT.

Round nineteen.  The referee's seventh major comment is the sharpest one in
the report: the knowledge-article reference is load-bearing -- it takes the
item's increment from +0.103 to about +0.001 -- and the evidence that it was
available at prediction time is not conclusive.  Only five interactions were
formally CLOSED before their incident was created; agreement with a closed
record cannot establish creation-time availability; and a baseline AUC near
0.805 from one field is itself a reason for suspicion.

The referee names three defensible responses and this file takes the third,
which is also the one that makes the paper better rather than smaller:

    DEFINE TWO DECISION TIMES AND ESTIMATE A SURFACE FOR EACH.

  T1  INTERACTION OPENING.  The service desk has just picked up the call.
      The knowledge reference has not been written.  Admissible: the intake
      block.
  T2  INCIDENT CREATION.  The desk has worked the interaction and escalated
      it.  The group that logged it is known.  The knowledge reference is
      written on the interaction in 91.1% of cases and the recorded handling
      time had elapsed in 98.6% -- so at T2 it is PROBABLY available, and
      probably is not proof.

Neither surface is "the" answer.  The paper reports both, says which decision
a reader is standing at when each applies, and never uses the T2 surface to
retire a claim the T1 surface supports.

THE TIPPING POINT.  Because availability at T2 is probable rather than proven,
this file also computes the value of the item as a function of the share
lambda of knowledge references that are assumed to be POST-HOC -- written
after the incident existed, and therefore inadmissible.  Masking a random
lambda share of the field and re-estimating traces a curve from the permissive
end (lambda = 0, the field fully admissible) to the conservative end
(lambda = 1, equivalent to T2 without the field).  The reader can then place
their own belief about lambda on the curve rather than accepting ours.

    python s08_decision_time.py

Outputs: results/s08_ladder.csv, s08_tipping.csv, s08_evidence.csv,
         s08_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

SEED = 20260823
N_BOOT = 400
ALPHA = 0.05
LAMBDAS = tuple(np.round(np.arange(0.0, 1.0001, 0.1), 2))


def load_cohort():
    import base14 as B
    D = B.D.copy()
    intake = list(B.INTAKE)
    ident = B.IDENT
    q = B.Q
    km = "KM number"
    if km not in D.columns:
        raise RuntimeError("the knowledge reference is not in the cohort")
    return D, intake, ident, q, km, B


def fit_eval(tr, te, cols, seed=SEED):
    return S._onehot_logit(tr, te, cols, tr["_y"].values, seed)


def main():
    t0 = time.time()
    D, intake, ident, q, km, B = load_cohort()
    cut = int(len(D) * 0.70)
    TR, TE = D.iloc[:cut], D.iloc[cut:]
    yte = TE["_y"].values
    prev_tr = float(TR["_y"].mean())
    print("=" * 92)
    print("s08  TWO DECISION TIMES ON THE PRIMARY LOG")
    print("=" * 92)
    print("  cohort %d  train %d  test %d  prevalence %.4f"
          % (len(D), len(TR), len(TE), float(yte.mean())))
    print("  intake %s" % intake)
    print("  item %r   group %r   knowledge %r" % (ident, q, km))

    #  ---- the two ladders -------------------------------------------------
    LADDERS = {
        "T1 interaction opening": [("intake", list(intake))],
        "T2 incident creation": [("intake", list(intake)),
                                 ("intake + group", list(intake) + [q]),
                                 ("intake + group + knowledge",
                                  list(intake) + [q, km])],
    }
    rows = []
    rng = np.random.default_rng(SEED)
    for dt, ladder in LADDERS.items():
        for name, cols in ladder:
            p0 = fit_eval(TR, TE, cols)
            p1 = fit_eval(TR, TE, cols + [ident])
            base = S.all_metrics(p0, yte, prev_tr, grid=())
            with_ = S.all_metrics(p1, yte, prev_tr, grid=())
            #  a nested moving-block bootstrap: the pipeline is refitted in
            #  every draw, on a block resample of the training half, and
            #  evaluated on a block resample of the test half.
            draws = []
            for b in range(N_BOOT):
                r = np.random.default_rng(SEED + 7919 * b)
                itr = S.block_indices(len(TR), r)
                ite = S.block_indices(len(TE), r)
                tr_b, te_b = TR.iloc[itr], TE.iloc[ite]
                y_b = te_b["_y"].values
                if len(np.unique(y_b)) < 2:
                    continue
                pr = float(tr_b["_y"].mean())
                a = fit_eval(tr_b, te_b, cols)
                c = fit_eval(tr_b, te_b, cols + [ident])
                draws.append(S.all_metrics(c, y_b, pr, grid=())["auc"]
                             - S.all_metrics(a, y_b, pr, grid=())["auc"])
            draws = np.array(draws, float)
            rows.append(dict(decision_time=dt, baseline=name,
                             n_fields=len(cols),
                             base_auc=base["auc"], with_auc=with_["auc"],
                             V_auc=with_["auc"] - base["auc"],
                             V_ap=with_["ap"] - base["ap"],
                             V_brier=with_["brier_skill"] - base["brier_skill"],
                             V_logloss=(with_["logloss_skill"]
                                        - base["logloss_skill"]),
                             se=float(np.nanstd(draws, ddof=1)),
                             lo=float(np.nanpercentile(draws, 100 * ALPHA / 2)),
                             hi=float(np.nanpercentile(draws,
                                                       100 * (1 - ALPHA / 2))),
                             n_draws=len(draws)))
            print("  [%s] %-30s base %.4f  V %+.4f [%+.4f, %+.4f]"
                  % (dt[:2], name, base["auc"], rows[-1]["V_auc"],
                     rows[-1]["lo"], rows[-1]["hi"]), flush=True)
    L = pd.DataFrame(rows)
    L["resolved"] = (L.lo > 0) | (L.hi < 0)
    L.to_csv(RESULTS / "s08_ladder.csv", index=False)

    #  ---- the leakage tipping point --------------------------------------
    print("\n  LEAKAGE TIPPING POINT: the item's value against the share of")
    print("  knowledge references assumed to be written after the incident")
    base_cols = list(intake) + [q]
    tip = []
    for lam in LAMBDAS:
        vals = []
        for s in range(5):
            r = np.random.default_rng(SEED + 101 * s)
            d = D.copy()
            hide = r.random(len(d)) < lam
            d["_km"] = np.where(hide, S.EMPTY, d[km].astype(str))
            tr, te = d.iloc[:cut], d.iloc[cut:]
            p0 = fit_eval(tr, te, base_cols + ["_km"])
            p1 = fit_eval(tr, te, base_cols + ["_km", ident])
            from sklearn.metrics import roc_auc_score
            vals.append(roc_auc_score(yte, p1) - roc_auc_score(yte, p0))
        tip.append(dict(lambda_posthoc=float(lam), V_auc=float(np.mean(vals)),
                        sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                        n_seeds=len(vals)))
        print("    lambda %.1f   V = %+.4f" % (lam, tip[-1]["V_auc"]),
              flush=True)
    T = pd.DataFrame(tip)
    T.to_csv(RESULTS / "s08_tipping.csv", index=False)

    #  the lambda at which the item recovers half of its T2-without-knowledge
    #  value, by linear interpolation on the computed grid
    v0 = float(L[(L.decision_time == "T2 incident creation")
                 & (L.baseline == "intake + group")].V_auc.iloc[0])
    target = 0.5 * v0
    lam_half = np.nan
    xs, ys = T.lambda_posthoc.values, T.V_auc.values
    for i in range(len(xs) - 1):
        if (ys[i] - target) * (ys[i + 1] - target) <= 0 and ys[i + 1] != ys[i]:
            lam_half = xs[i] + (target - ys[i]) * (xs[i + 1] - xs[i]) / (
                ys[i + 1] - ys[i])
            break

    #  ---- what the interaction file can and cannot prove -----------------
    try:
        F = pd.read_csv(RESULTS / "r35_facts.csv").iloc[0]
        ev = pd.DataFrame([
            dict(evidence="interactions in the file", value=int(F.n_interactions),
                 establishes="the population the knowledge reference is "
                             "written in"),
            dict(evidence="interactions that never became incidents",
                 value=int(F.n_orphans),
                 establishes="the field is written by the service-desk "
                             "process, not by the incident process"),
            dict(evidence="knowledge reference populated on those",
                 value=float(F.km_populated_orphan),
                 establishes="the same, quantitatively"),
            dict(evidence="interactions CLOSED before the incident was opened",
                 value=int(F.n_closed_before),
                 establishes="airtight pre-incident availability, on five "
                             "cases, which is not enough to rest a headline on"),
            dict(evidence="interactions whose recorded handling time had "
                          "elapsed before the incident was opened",
                 value=int(F.n_worked_before),
                 establishes="that the desk had worked the interaction, which "
                             "is not a timestamped field-value history"),
            dict(evidence="knowledge reference populated on the joined cohort",
                 value=float(F.km_prov_populated),
                 establishes="coverage, not timing"),
            dict(evidence="base AUC from the knowledge reference alone",
                 value=float(F.null_base_auc_max),
                 establishes="the field is highly predictive, which is a "
                             "reason for suspicion and not for confidence"),
        ])
    except Exception:  # noqa: BLE001
        ev = pd.DataFrame()
    ev.to_csv(RESULTS / "s08_evidence.csv", index=False)
    if len(ev):
        print("\n" + ev.to_string(index=False))

    facts = dict(
        n_cohort=len(D), n_train=len(TR), n_test=len(TE),
        prevalence=float(yte.mean()),
        V_T1=float(L[L.decision_time.str.startswith("T1")].V_auc.iloc[0]),
        V_T1_lo=float(L[L.decision_time.str.startswith("T1")].lo.iloc[0]),
        V_T1_hi=float(L[L.decision_time.str.startswith("T1")].hi.iloc[0]),
        V_T2_group=v0,
        V_T2_group_lo=float(L[(L.decision_time == "T2 incident creation")
                              & (L.baseline == "intake + group")].lo.iloc[0]),
        V_T2_group_hi=float(L[(L.decision_time == "T2 incident creation")
                              & (L.baseline == "intake + group")].hi.iloc[0]),
        V_T2_knowledge=float(L[L.baseline.str.contains("knowledge")].V_auc.iloc[0]),
        V_T2_knowledge_lo=float(L[L.baseline.str.contains("knowledge")].lo.iloc[0]),
        V_T2_knowledge_hi=float(L[L.baseline.str.contains("knowledge")].hi.iloc[0]),
        lambda_half=lam_half,
        n_boot=N_BOOT, runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s08_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

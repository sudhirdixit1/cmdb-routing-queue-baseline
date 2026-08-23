"""s04 -- WHAT ONE NUMBER COSTS: THE SPECIFICATION-REGRET BENCHMARK.

Round nineteen.  The referee's second major comment ends with the one thing
the round-eighteen paper never did: BENCHMARK the proposed reporting against
conventional single-specification reporting.  Saying "report more numbers" is
advice.  Measuring what the single number gets wrong, on every eligible log,
is a result.

THE DECISION.  A reader of a feature-value claim decides whether to adopt the
field.  A one-number report gives them V_s for ONE specification s, and the
decision rule is `adopt iff V_s > 0`.  The surface report gives them the
resolution region of s03, and the decision rule is `adopt iff uniformly
beneficial; decline iff harmful; report unresolved otherwise`.

THE LOSS.  Adoption is wrong when the feature is not in fact beneficial under
the specification the reader will actually run, which is drawn from the same
admissible set.  So for a one-number report at s, the misreport rate is

    M(s) = P_{s'}[ sign V_{s'} != sign V_s ],

and the expected regret in net-benefit units at the reader's own operating
point is

    G(s) = E_{s'}[ max(0, -V_{s'}) | V_s > 0 ]  +  E_{s'}[ max(0, V_{s'}) | V_s <= 0 ],

the value destroyed by adopting when the reader's cell is harmful, plus the
value forgone by declining when it is beneficial.  Both are computed over the
admissible set with the intercept-only rung removed, because no analyst builds
it.

WHAT WOULD SINK THIS.  If M(s) were near zero, the paper would have no case:
one number would be a safe summary and the surface would be ceremony.  M(s) is
printed whatever it is, per log and per specification, and the logs where it
is small are named.

    python s04_regret.py

Outputs: results/s04_regret.csv, s04_by_axis.csv, s04_rules.csv, s04_facts.csv
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

#  The conventional report, as the audit finds it: one learner, one baseline,
#  one metric, the full register, one split.  These are the cells a
#  single-number paper would occupy.
CONVENTIONAL = dict(quality="clean", split="holdout70", metric="auc")


# --------------------------------------------------------------------------
#  THREE DECISION RULES UNDER ONE LOSS
#
#  Comparing "the surface report never asserts a sign where the region is not
#  uniform" against "one number always does" is a definitional win, not a
#  measured one, and a referee is right to discount it.  This is the measured
#  version.
#
#  A reader must decide whether to adopt the field.  Their own specification
#  s' is drawn from the admissible set under a declared weighting.  Their loss
#  is what the decision costs them in the metric's own units:
#
#      adopt   -> max(0, -V_{s'})     the performance the field destroys
#      decline -> max(0,  V_{s'})     the performance the field would have
#                                     added
#
#  Three rules are compared under that loss:
#
#      ONE-NUMBER   adopt iff V_s > 0 at the conventional cell
#      UNIFORM      adopt iff every admissible cell is positive
#      MAJORITY     adopt iff more than half of the admissible cells are
#                   positive
#
#  and the ORACLE loss -- the smallest achievable by a rule that knew the
#  reader's cell -- is zero by construction, so the numbers below are regrets
#  rather than losses.  The comparison is reported under two weightings, to
#  make the uniform-draw assumption visible rather than silent:
#
#      uniform            every admissible cell equally likely
#      reference-adjacent a cell's weight falls with the number of axes on
#                         which it differs from the reference specification,
#                         which is what a reader who mostly follows the
#                         conventional recipe looks like.
# --------------------------------------------------------------------------
REFERENCE = dict(learner="logit", split="holdout70", quality="clean",
                 metric="auc", rung="B_intake_g")


def _weights(A, kind):
    if kind == "uniform":
        return np.ones(len(A)) / len(A)
    d = np.zeros(len(A))
    for col, val in REFERENCE.items():
        if col in A.columns:
            d = d + (A[col].astype(str).values != val).astype(float)
    w = 0.5 ** d
    return w / w.sum()


def decision_rules(SUR):
    rows = []
    for (log, target), sub in SUR.groupby(["log", "target"]):
        A = sub[sub.metric.isin(S.SCALARS)].copy()
        if len(A) < 8:
            continue
        v = A.V.values
        conv = A[(A.quality == CONVENTIONAL["quality"])
                 & (A.split == CONVENTIONAL["split"])
                 & (A.metric == CONVENTIONAL["metric"])
                 & (A.learner == REFERENCE["learner"])
                 & (A.rung == REFERENCE["rung"])]
        v_conv = float(conv.V.iloc[0]) if len(conv) else float(np.median(v))
        for wkind in ("uniform", "reference-adjacent"):
            w = _weights(A, wkind)
            loss_adopt = float((w * np.maximum(0.0, -v)).sum())
            loss_decline = float((w * np.maximum(0.0, v)).sum())
            share_pos = float((w * (v > 0)).sum())
            rules = {
                "one-number": v_conv > 0,
                "uniform-beneficial": bool((v > 0).all()),
                "majority": share_pos > 0.5,
            }
            for name, adopt in rules.items():
                rows.append(dict(
                    log=log, target=target, weighting=wkind, rule=name,
                    adopts=bool(adopt),
                    regret=loss_adopt if adopt else loss_decline,
                    share_positive=share_pos, n_cells=len(A)))
    return pd.DataFrame(rows)


def main():
    t0 = time.time()
    SUR = S.read_results("s01_surface.csv")
    SUR = SUR[~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS)].copy()
    print("=" * 92)
    print("s04  SPECIFICATION REGRET: WHAT ONE NUMBER COSTS")
    print("=" * 92)

    rows, axis_rows = [], []
    for (log, target), sub in SUR.groupby(["log", "target"]):
        #  the admissible set: scalar instruments only, so the loss is on one
        #  scale; net benefit is handled separately below because its units
        #  are per-case value rather than a discrimination index.
        A = sub[sub.metric.isin(S.SCALARS)].copy()
        if len(A) < 8:
            continue
        v = A.V.values
        pos = v > 0
        p_pos = float(pos.mean())
        #  M(s) for every s, in closed form: if V_s > 0 the disagreeing share
        #  is 1 - p_pos, else p_pos.
        M = np.where(pos, 1.0 - p_pos, p_pos)
        neg_mass = float(np.mean(np.maximum(0.0, -v)))
        pos_mass = float(np.mean(np.maximum(0.0, v)))
        G = np.where(pos, neg_mass, pos_mass)
        for i, r in enumerate(A.itertuples()):
            rows.append(dict(log=log, target=target, learner=r.learner,
                             split=r.split, quality=r.quality, level=r.level,
                             rung=r.rung, metric=r.metric, V=r.V,
                             misreport=M[i], regret=G[i],
                             conventional=bool(
                                 r.quality == CONVENTIONAL["quality"]
                                 and r.split == CONVENTIONAL["split"]
                                 and r.metric == CONVENTIONAL["metric"])))
        #  how much of the disagreement each axis is responsible for: the
        #  share of ORDERED PAIRS of cells that differ in sign and differ only
        #  on that axis.
        for axis in ("learner", "split", "rung", "metric"):
            others = [c for c in ("learner", "split", "quality", "level",
                                  "rung", "metric") if c != axis]
            flips = tot = 0
            for _key, g in A.groupby(others):
                s_ = (g.V.values > 0)
                if len(s_) < 2:
                    continue
                tot += len(s_) * (len(s_) - 1) // 2
                k = int(s_.sum())
                flips += k * (len(s_) - k)
            axis_rows.append(dict(log=log, target=target, axis=axis,
                                  pairs=tot, sign_flips=flips,
                                  flip_rate=flips / tot if tot else np.nan))
        #  the quality axis, separately, because its levels are (kind, level)
        others = ["learner", "split", "rung", "metric"]
        flips = tot = 0
        for _key, g in A.groupby(others):
            s_ = (g.V.values > 0)
            if len(s_) < 2:
                continue
            tot += len(s_) * (len(s_) - 1) // 2
            k = int(s_.sum())
            flips += k * (len(s_) - k)
        axis_rows.append(dict(log=log, target=target, axis="quality",
                              pairs=tot, sign_flips=flips,
                              flip_rate=flips / tot if tot else np.nan))
    R = pd.DataFrame(rows)
    AX = pd.DataFrame(axis_rows)
    R.to_csv(RESULTS / "s04_regret.csv.gz", index=False, compression="gzip")
    AX.to_csv(RESULTS / "s04_by_axis.csv", index=False)

    #  --- the two reporting rules, compared -------------------------------
    try:
        REG = pd.read_csv(RESULTS / "s03_regions.csv")
    except Exception:  # noqa: BLE001  -- missing OR empty, both mean "not yet"
        REG = pd.DataFrame()
    rules = []
    for (log, target), sub in R.groupby(["log", "target"]):
        conv = sub[sub.conventional]
        if conv.empty:
            conv = sub
        m_conv = float(conv.misreport.mean())
        g_conv = float(conv.regret.mean())
        m_any = float(sub.misreport.mean())
        row = dict(log=log, target=target,
                   one_number_misreport_conventional=m_conv,
                   one_number_misreport_any=m_any,
                   one_number_regret_conventional=g_conv,
                   share_cells_positive=float((sub.V > 0).mean()))
        if len(REG):
            rr = REG[(REG.log == log) & (REG.target == target)]
            if len(rr):
                row["region"] = rr.region.iloc[0]
                row["rho"] = float(rr.rho.iloc[0])
                #  the surface rule asserts a sign only when the region is
                #  uniform, so its misreport rate is zero by construction
                #  there and it declines to speak elsewhere.
                row["surface_asserts"] = rr.region.iloc[0] in (
                    "uniformly beneficial", "harmful")
                row["surface_misreport"] = 0.0 if row["surface_asserts"] else np.nan
        rules.append(row)
    RU = pd.DataFrame(rules)
    RU.to_csv(RESULTS / "s04_rules.csv", index=False)

    #  --- the three decision rules under one loss -------------------------
    DR = decision_rules(SUR)
    DR.to_csv(RESULTS / "s04_decision_rules.csv", index=False)
    print(chr(10) + "THREE DECISION RULES UNDER ONE LOSS  (mean regret "
          "per pair, in the metric own units)")

    piv = DR.pivot_table(index="weighting", columns="rule", values="regret",
                         aggfunc="mean")
    print(piv.to_string(float_format=lambda x: "%.4f" % x))
    print(chr(10)+"  rule adopts on N of %d pairs:" % DR.log.nunique())
    print(DR[DR.weighting == "uniform"].groupby("rule").adopts.sum().to_string())
    print(RU.to_string(index=False, float_format=lambda x: "%.3f" % x))

    print("\nSIGN FLIPS ATTRIBUTABLE TO EACH AXIS (share of same-everything-"
          "else pairs)")
    piv = AX.pivot_table(index=["log", "target"], columns="axis",
                         values="flip_rate")
    print(piv.to_string(float_format=lambda x: "%.3f" % x))

    facts = dict(
        n_cells=len(R), n_pairs=int(R.groupby(["log", "target"]).ngroups),
        misreport_median=float(RU.one_number_misreport_conventional.median()),
        misreport_max=float(RU.one_number_misreport_conventional.max()),
        misreport_min=float(RU.one_number_misreport_conventional.min()),
        n_pairs_misreport_over_25pct=int(
            (RU.one_number_misreport_conventional > 0.25).sum()),
        n_pairs_misreport_over_10pct=int(
            (RU.one_number_misreport_conventional > 0.10).sum()),
        flip_rate_rung=float(AX[AX.axis == "rung"].flip_rate.median()),
        flip_rate_learner=float(AX[AX.axis == "learner"].flip_rate.median()),
        flip_rate_metric=float(AX[AX.axis == "metric"].flip_rate.median()),
        flip_rate_split=float(AX[AX.axis == "split"].flip_rate.median()),
        flip_rate_quality=float(AX[AX.axis == "quality"].flip_rate.median()),
        regret_one_number=float(DR[(DR.rule == "one-number")
                                   & (DR.weighting == "uniform")].regret.mean()),
        regret_uniform_rule=float(DR[(DR.rule == "uniform-beneficial")
                                     & (DR.weighting == "uniform")].regret.mean()),
        regret_majority=float(DR[(DR.rule == "majority")
                                 & (DR.weighting == "uniform")].regret.mean()),
        regret_one_number_adj=float(DR[(DR.rule == "one-number")
                                       & (DR.weighting == "reference-adjacent")]
                                    .regret.mean()),
        regret_majority_adj=float(DR[(DR.rule == "majority")
                                     & (DR.weighting == "reference-adjacent")]
                                  .regret.mean()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s04_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

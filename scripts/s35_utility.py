"""s35 -- THE DECISION IN UNITS A SERVICE DESK USES.  Round twenty-one, M5.

THE OBJECTION.  The regret comparison is thin.  Out of sample the one-number
report costs 0.00451 AUC against the weighted mean's 0.00002; under rolling
folds the ordering reverses; and on net benefit -- the one utility with an
operational meaning -- three of the four rules tie at zero.  A reader is left
with an apparatus that wins by half a hundredth of an AUC point in the setting
most favourable to it and ties in the units a desk actually uses.

WHY THEY TIE, AND WHAT FIXES IT.  Three things were flattening the comparison.

  1  UNIFORM WEIGHT OVER AN OPERATING RANGE NOBODY OPERATES AT.  The declared
     range runs from a threshold of 0.05 to 0.80.  A service desk deciding
     whether to pre-empt a reassignment is not indifferent across it: the
     exchange rate between an unnecessary review and an avoidable
     reassignment is a few to one, not twenty to one and not one to four.
     This file declares a DESK DISTRIBUTION over the exchange rate, states
     where its mass comes from, and reports the fixed rates beside it so a
     reader who rejects the distribution still has a number.

  2  MODELS THAT ARE NOT PROBABILITIES.  A threshold is a cost ratio only if
     the score is calibrated.  Four pairs carry recalibrated slopes below 0.4
     or above 2.5, at which a net-benefit increment is not interpretable.  A
     REGISTERED EXCLUSION RULE removes them from the decision-analytic
     reading and names what it removed, rather than averaging them in.

  3  A UNIT NOBODY BUDGETS IN.  Net benefit per case is a rate near zero and
     three decimal places of it look like a tie.  Reported per thousand
     cases, against the pair's own volume, it is a quantity with a size.

WHAT IS AND IS NOT CLAIMED.  These are predictive-performance differences
expressed in a decision-analytic unit under a declared exchange rate.  They
are not a business case: no cost figure here comes from an organisation, and
the desk distribution is an assumption whose sensitivity is reported, not an
estimate.

    python s35_utility.py

Outputs: results/s35_rules.csv       four rules x pair x threshold measure
         results/s35_excluded.csv    what the calibration rule removed, why
         results/s35_curve.csv       excess regret as a function of threshold
         results/s35_facts.csv
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
import s22_anova as A22  # noqa: E402
import s23_regret as S23  # noqa: E402
from common import RESULTS  # noqa: E402

#: THE REGISTERED CALIBRATION RULE.  A recalibrated model whose Cox slope is
#: outside this interval is not usable as a probability: at slope 0.03 the
#: score's spread carries almost no information about the odds, and a
#: threshold read as a cost ratio is meaningless.  The bounds are the
#: conventional "severe miscalibration" range and are declared here rather
#: than chosen after seeing which pairs they remove.
SLOPE_LO, SLOPE_HI = 0.5, 2.0
CALIBRATION = "isotonic"

#: THE DESK DISTRIBUTION.  t = C_fp / (C_fp + C_fn) is the exchange rate at
#: which a desk is indifferent.  For a pre-emptive routing review the false
#: positive costs a specialist's few minutes; the false negative costs a
#: re-triage, a second queue wait and the service-level exposure that goes
#: with it.  Ratios between three and ten to one put t between 0.09 and 0.25.
#: The Beta below places 90% of its mass on [0.08, 0.34] with a median near
#: 0.18, and the fixed rates beside it are reported so the distribution is a
#: summary rather than a load-bearing assumption.
DESK_A, DESK_B = 4.0, 16.0

#: the fixed exchange rates, named as ratios because that is how a desk states
#: them: 1:r means the false negative costs r times the false positive, so
#: t = 1/(1+r).
FIXED_RATES = (2, 4, 9, 19)

PER = 1000.0    # cases; net benefit is a per-case rate and a desk budgets per


def threshold_measures(grid):
    """Every declared measure over the operating grid, each summing to one."""
    from scipy.stats import beta
    g = np.asarray(sorted(grid), float)
    out = {}
    u = np.ones(len(g))
    out["uniform over the declared range"] = dict(zip(g, u / u.sum()))
    d = beta.pdf(g, DESK_A, DESK_B)
    out["desk distribution"] = dict(zip(g, d / d.sum()))
    for r in FIXED_RATES:
        t = 1.0 / (1.0 + r)
        w = np.zeros(len(g))
        w[int(np.argmin(np.abs(g - t)))] = 1.0
        out["fixed 1:%d" % r] = dict(zip(g, w))
    return out


def exclusion(C):
    """The registered calibration rule, applied at the level it belongs at.

    A net-benefit increment compares two fitted models at one threshold, so
    the rule is a property of the (pair, learner, rung) triple and both of its
    arms -- not of a whole log.  Excluding a pair because one of its twenty-
    four models is uncalibrated throws away the other twenty-three; excluding
    the model keeps the surface and removes only what cannot be read.
    """
    c = C[C.calibration == CALIBRATION].copy()
    c["ok"] = c.cal_slope.between(SLOPE_LO, SLOPE_HI)
    g = (c.groupby(["log", "target", "learner", "rung"])
         .agg(slope_min=("cal_slope", "min"), slope_max=("cal_slope", "max"),
              n_arms=("ok", "size"), n_ok=("ok", "sum")).reset_index())
    g["admitted"] = g.n_ok == g.n_arms
    g["reason"] = np.where(
        g.admitted, "",
        np.where(g.slope_min < SLOPE_LO,
                 "recalibrated slope below %.1f" % SLOPE_LO,
                 "recalibrated slope above %.1f" % SLOPE_HI))
    return g


def wrong_decision_time(D, TM, log="BPIC14", target="handover"):
    """What a desk loses by deploying at a decision time other than the one
    its report was computed at.

    This is the decision the case study actually poses.  The register's
    increment against the intake block alone is large; against the intake
    block plus the group and the knowledge reference it is not.  A desk that
    read the first number and deployed where the second applies gets the
    second's benefit, and the difference is the cost of a report that did not
    name its decision time.
    """
    rows = []
    sub = D[(D.log == log) & (D.target == target)]
    if not len(sub):
        return pd.DataFrame()
    for tname, tw in TM.items():
        for learner, s0 in sub.groupby("learner"):
            got = {}
            for rung, g in s0.groupby("rung"):
                w = g.threshold.map(tw).values
                if w.sum() <= 0:
                    continue
                got[rung] = float((w * g.dnb.values).sum() / w.sum())
            if "B_intake" not in got:
                continue
            for rung, v in got.items():
                if rung == "B_intake":
                    continue
                rows.append(dict(
                    log=log, target=target, learner=learner,
                    threshold_measure=tname, promised_rung="B_intake",
                    deployed_rung=rung,
                    promised_per_1000=got["B_intake"] * PER,
                    delivered_per_1000=v * PER,
                    shortfall_per_1000=(got["B_intake"] - v) * PER))
    return pd.DataFrame(rows)


def main():
    t0 = time.time()
    print("=" * 92)
    print("s35  THE DECISION IN UNITS A SERVICE DESK USES")
    print("=" * 92)
    D = S.read_results("s26_dca.csv.gz")
    D = D[D.calibration == CALIBRATION].copy()
    C = pd.read_csv(RESULTS / "s26_calibration.csv")
    EX = exclusion(C)
    EX.to_csv(RESULTS / "s35_excluded.csv", index=False)
    ok = set(zip(EX[EX.admitted].log, EX[EX.admitted].target,
                 EX[EX.admitted].learner, EX[EX.admitted].rung))
    D["admitted"] = [(l, t, lr, r) in ok for l, t, lr, r
                     in zip(D.log, D.target, D.learner, D.rung)]
    n_pairs_all = D.groupby(["log", "target"]).ngroups
    D = D[D.admitted]
    print("  registered calibration rule: slope in [%.1f, %.1f] after "
          "%s recalibration, both arms" % (SLOPE_LO, SLOPE_HI, CALIBRATION))
    print("  admitted %d of %d (pair, learner, rung) models; %d of %d pairs "
          "keep at least one"
          % (int(EX.admitted.sum()), len(EX),
             D.groupby(["log", "target"]).ngroups, n_pairs_all))

    TM = threshold_measures(D.threshold.unique())
    WD = wrong_decision_time(S.read_results("s26_dca.csv.gz")
                             .query("calibration == @CALIBRATION"), TM)
    WD.to_csv(RESULTS / "s35_decisiontime.csv", index=False)

    rows, curve = [], []
    for (log, target), sub in D.groupby(["log", "target"]):
        admitted = True
        for tname, tw in TM.items():
            s = sub.copy()
            s["_tw"] = s.threshold.map(tw)
            spec_w = np.ones(len(s))
            for a in ("learner", "rung"):
                lv = sorted(s[a].astype(str).unique())
                spec_w = spec_w * s[a].astype(str).map(
                    {x: 1.0 / len(lv) for x in lv}).values
            w = spec_w * s._tw.values
            if w.sum() <= 0:
                continue
            w = w / w.sum()
            v = s.dnb.values.astype(float)
            conv = s[(s.learner == "logit")
                     & (s.rung == A22.REFERENCE["rung"])
                     & (np.isclose(s.threshold, 0.20))]
            v_conv = float(conv.dnb.iloc[0]) if len(conv) else float(
                np.median(v))
            res, agg = S23.rules_on(v, w, v_conv)
            for nm, r in res.items():
                rows.append(dict(
                    log=log, target=target, admitted=admitted,
                    threshold_measure=tname, rule=nm, n_cells=len(s),
                    adopts=r["adopts"],
                    loss_per_1000=r["loss"] * PER,
                    excess_per_1000=r["excess"] * PER,
                    rel_excess=r["rel_excess"],
                    share_positive=agg["share_positive"],
                    mean_dnb_per_1000=agg["mean"] * PER))
        for t, g in sub.groupby("threshold"):
            v = g.dnb.values.astype(float)
            w = np.ones(len(v)) / len(v)
            res, agg = S23.rules_on(v, w, float(np.median(v)))
            curve.append(dict(
                log=log, target=target, admitted=admitted,
                threshold=float(t),
                excess_one_number_per_1000=res["one-number"]["excess"] * PER,
                excess_majority_per_1000=res["majority"]["excess"] * PER,
                excess_uniform_per_1000=(
                    res["uniform-beneficial"]["excess"] * PER),
                share_positive=agg["share_positive"]))
    R = pd.DataFrame(rows)
    R.to_csv(RESULTS / "s35_rules.csv", index=False)
    CU = pd.DataFrame(curve)
    CU.to_csv(RESULTS / "s35_curve.csv", index=False)

    adm = R[R.admitted]
    piv = (adm.pivot_table(index="threshold_measure", columns="rule",
                           values="excess_per_1000", aggfunc="median"))
    print("\n  MEDIAN EXCESS REGRET, net benefit per %d cases, admitted "
          "pairs only" % int(PER))
    print(piv.to_string())
    nsep = {}
    for tname, g in adm.groupby("threshold_measure"):
        p = g.pivot_table(index=["log", "target"], columns="rule",
                          values="excess_per_1000")
        #  a pair SEPARATES the rules when they do not all lose the same
        nsep[tname] = int((p.max(axis=1) - p.min(axis=1) > 1e-9).sum())
    print("\n  pairs on which the four rules do not tie:")
    for k, v in nsep.items():
        print("    %-34s %d of %d" % (k, v, adm.groupby(
            ["log", "target"]).ngroups))

    desk = adm[adm.threshold_measure == "desk distribution"]
    uni = adm[adm.threshold_measure == "uniform over the declared range"]

    def med(df, rule):
        s = df[df.rule == rule].excess_per_1000
        return float(s.median()) if len(s) else np.nan

    wd = WD[(WD.threshold_measure == "desk distribution")
            & (WD.deployed_rung == "B_intake_g_km")] if len(WD) \
        else pd.DataFrame()
    facts = dict(
        slope_lo=SLOPE_LO, slope_hi=SLOPE_HI, calibration=CALIBRATION,
        n_models=int(len(EX)), n_models_admitted=int(EX.admitted.sum()),
        n_models_excluded=int((~EX.admitted).sum()),
        n_pairs=int(n_pairs_all),
        n_pairs_with_a_model=int(D.groupby(["log", "target"]).ngroups),
        n_pairs_fully_excluded=int(
            n_pairs_all - D.groupby(["log", "target"]).ngroups),
        promised_per_1000=float(wd.promised_per_1000.median())
        if len(wd) else np.nan,
        delivered_per_1000=float(wd.delivered_per_1000.median())
        if len(wd) else np.nan,
        shortfall_per_1000=float(wd.shortfall_per_1000.median())
        if len(wd) else np.nan,
        desk_a=DESK_A, desk_b=DESK_B,
        desk_q05=float(__import__("scipy.stats", fromlist=["beta"])
                       .beta.ppf(0.05, DESK_A, DESK_B)),
        desk_q50=float(__import__("scipy.stats", fromlist=["beta"])
                       .beta.ppf(0.50, DESK_A, DESK_B)),
        desk_q95=float(__import__("scipy.stats", fromlist=["beta"])
                       .beta.ppf(0.95, DESK_A, DESK_B)),
        n_separating_desk=nsep.get("desk distribution", 0),
        n_separating_uniform=nsep.get("uniform over the declared range", 0),
        excess_one_number_desk=med(desk, "one-number"),
        excess_majority_desk=med(desk, "majority"),
        excess_uniform_desk=med(desk, "uniform-beneficial"),
        excess_mean_desk=med(desk, "weighted-mean"),
        excess_one_number_uniform=med(uni, "one-number"),
        excess_mean_uniform=med(uni, "weighted-mean"),
        max_excess_one_number_desk=float(
            desk[desk.rule == "one-number"].excess_per_1000.max()),
        n_one_number_worst_desk=int(sum(
            1 for _, g in desk.groupby(["log", "target"])
            if len(g) and g.loc[g.excess_per_1000.idxmax(), "rule"]
            == "one-number")),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s35_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s35_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

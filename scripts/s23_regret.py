"""s23 -- SPECIFICATION REGRET ON A COHERENT SCALE.

Round twenty, blueprint P0.3.

WHAT WAS WRONG.  Round nineteen averaged the loss over an admissible set that
ranged across five scalar instruments and then called the result "in the
metric's own units".  Once AUC, average precision, Brier skill, log-loss skill
and Nagelkerke R-squared are in the same average there is no metric whose
units they are.  A 0.02 AUC loss and a 0.02 Brier-skill loss are not the same
quantity of anything.

WHAT THIS FILE DOES.  All three of the designs the blueprint offers, so a
reader can see which conclusions need which assumption.

  A  METRIC-SPECIFIC REGRET (always reported).  The loss is computed inside
     one instrument at a time and never averaged across instruments.  Each
     value carries the name of its unit.  The corpus summary is the
     distribution of relative excess regret across log-target pairs WITHIN an
     instrument, and the question asked of it is whether the DIRECTION of the
     conclusion is the same in all five.

  B  COMMON OPERATIONAL UTILITY (the preferred design).  Net benefit is an
     explicitly operational utility measured in true positives per case at a
     declared exchange rate, so losses at different thresholds are cardinally
     comparable.  It is computed only on CALIBRATED probabilities (s26),
     because a threshold read as a cost ratio requires one, and the result is
     called decision regret rather than predictive-performance regret.

  C  PARTIAL IDENTIFICATION.  If a reader insists on one number across
     instruments, the answer depends on the utility map from an instrument's
     units to theirs.  A family of monotone maps is declared and the range of
     the conclusion over that family is reported, together with the
     conclusions that are invariant to every member of it.

WHAT ELSE WAS WRONG.  The weighted-mean rule minimises expected loss on the
same surface the loss is averaged over.  That is an algebraic identity, and
round nineteen reported it as though the mean rule had won a contest.  This
file evaluates every rule OUT OF SAMPLE in three ways -- on held-out
specifications, on held-out time, and on held-out logs -- and reports the
in-sample identity separately, as a check on the algebra rather than as
evidence.

    python s23_regret.py

Outputs: results/s23_metric_regret.csv   design A, per metric, per measure
         results/s23_utility_regret.csv  design B, net benefit, calibrated
         results/s23_partial.csv         design C, the utility-map envelope
         results/s23_heldout.csv         the out-of-sample evaluations
         results/s23_facts.csv
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
from common import RESULTS  # noqa: E402

AXES = ("learner", "split", "quality_level", "rung")
MEASURES = ("equal-level", "reference", "concentrated")

#: the units every reported loss is expressed in, by instrument.  A regret
#: value without one of these is a defect, and s13 checks for it.
UNIT = {"auc": "AUC", "ap": "average precision",
        "brier_skill": "Brier skill", "nagelkerke": "Nagelkerke R2",
        "logloss_skill": "log-loss skill",
        "net_benefit": "net benefit (true positives per case)"}


def product_weights(df, measure, axes=AXES, rng=None):
    """The weight of every ROW of `df` under the declared product measure.
    Sums to one; invariant to duplicating a level whose weight is split."""
    w = np.ones(len(df), float)
    for a in axes:
        lv = sorted(df[a].astype(str).unique())
        pv = A22.level_weights(lv, a, measure, rng)
        m = dict(zip(lv, pv))
        w = w * df[a].astype(str).map(m).values
    #  a complete factorial makes this already sum to one; normalising costs
    #  nothing and makes an incomplete one explicit rather than silent
    s = w.sum()
    return w / s if s > 0 else w


def rules_on(v, w, v_conv):
    """The four decision rules and the loss of each, under weights w."""
    L_adopt = float((w * np.maximum(0.0, -v)).sum())
    L_decline = float((w * np.maximum(0.0, v)).sum())
    mean_v = float((w * v).sum())
    share_pos = float((w * (v > 0)).sum())
    acts = {"one-number": bool(v_conv > 0),
            "uniform-beneficial": bool((v > 0).all()),
            "majority": bool(share_pos > 0.5),
            "weighted-mean": bool(mean_v > 0)}
    best = min(L_adopt, L_decline)
    out = {}
    for nm, adopt in acts.items():
        loss = L_adopt if adopt else L_decline
        out[nm] = dict(adopts=adopt, loss=loss, excess=loss - best,
                       rel_excess=(loss - best) / best if best > 1e-12
                       else np.nan)
    return out, dict(L_adopt=L_adopt, L_decline=L_decline, best=best,
                     mean=mean_v, share_positive=share_pos)


def reference_value(sub):
    """The increment a conventional one-number report would print: the
    reference level on every axis."""
    q = sub
    for a, ref in A22.REFERENCE.items():
        if a in q.columns:
            r = q[q[a].astype(str) == ref]
            if len(r):
                q = r
    return float(q.V.iloc[0]) if len(q) else float(np.median(sub.V.values))


# --------------------------------------------------------------------------
def design_A(SC):
    """Metric-specific regret.  No average crosses an instrument."""
    rows = []
    for (log, target, metric), sub in SC.groupby(["log", "target", "metric"]):
        if len(sub) < 8:
            continue
        v = sub.V.values.astype(float)
        v_conv = reference_value(sub)
        for meas in MEASURES:
            w = product_weights(sub, meas)
            res, agg = rules_on(v, w, v_conv)
            for nm, r in res.items():
                rows.append(dict(log=log, target=target, metric=metric,
                                 unit=UNIT[metric], measure=meas, rule=nm,
                                 n_cells=len(sub), **r, **agg))
    return pd.DataFrame(rows)


def misreport(SC):
    """The sign-disagreement rate of a one-number report, under each declared
    measure.

    A SIGN comparison has no unit, so this one quantity may be pooled across
    instruments where an expected loss may not: the metric enters as a fifth
    axis of the product measure rather than as a scale to average over.  What
    it may not do is duck the measure, which is why it is computed under all
    three: the blueprint's objection to the earlier version of this number was
    that its weights were grid-dependent, and the answer to that is to show
    the number under several grids rather than to defend one.
    """
    rows = []
    axes5 = tuple(list(AXES) + ["metric"])
    for (log, target), sub in SC.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        v = sub.V.values.astype(float)
        v_conv = reference_value(sub[sub.metric == A22.REFERENCE["metric"]]) \
            if (sub.metric == A22.REFERENCE["metric"]).any() \
            else reference_value(sub)
        for meas in MEASURES:
            w = product_weights(sub, meas, axes=axes5)
            share_pos = float((w * (v > 0)).sum())
            rows.append(dict(
                log=log, target=target, measure=meas, n_cells=len(sub),
                v_reference=v_conv, share_positive=share_pos,
                misreport=(1.0 - share_pos) if v_conv > 0 else share_pos))
    return pd.DataFrame(rows)


def design_B(threshold_measures):
    """Common operational utility: calibrated net benefit."""
    try:
        D = S.read_results("s26_dca.csv.gz")
    except Exception:  # noqa: BLE001
        return pd.DataFrame(), pd.DataFrame()
    D = D[D.calibration == "isotonic"].copy()
    if not len(D):
        return pd.DataFrame(), pd.DataFrame()
    rows, curve = [], []
    for (log, target), sub in D.groupby(["log", "target"]):
        for tname, tw in threshold_measures.items():
            sub = sub.copy()
            sub["_tw"] = sub.threshold.map(tw)
            #  the specification axes here are learner and rung; the
            #  threshold is the operating point and carries its own measure
            spec_w = np.ones(len(sub))
            for a in ("learner", "rung"):
                lv = sorted(sub[a].astype(str).unique())
                spec_w = spec_w * sub[a].astype(str).map(
                    {x: 1.0 / len(lv) for x in lv}).values
            w = spec_w * sub._tw.values
            w = w / w.sum()
            v = sub.dnb.values.astype(float)
            conv = sub[(sub.learner == "logit")
                       & (sub.rung == A22.REFERENCE["rung"])
                       & (np.isclose(sub.threshold, 0.20))]
            v_conv = float(conv.dnb.iloc[0]) if len(conv) else float(np.median(v))
            res, agg = rules_on(v, w, v_conv)
            for nm, r in res.items():
                rows.append(dict(log=log, target=target,
                                 unit=UNIT["net_benefit"],
                                 threshold_measure=tname, rule=nm,
                                 n_cells=len(sub), **r, **agg))
        #  regret as a function of the threshold, so no distribution over
        #  thresholds has to be assumed at all
        for t, g in sub.groupby("threshold"):
            v = g.dnb.values.astype(float)
            w = np.ones(len(v)) / len(v)
            res, agg = rules_on(v, w, float(np.median(v)))
            curve.append(dict(log=log, target=target, threshold=float(t),
                              unit=UNIT["net_benefit"],
                              excess_one_number=res["one-number"]["excess"],
                              excess_majority=res["majority"]["excess"],
                              excess_uniform=res["uniform-beneficial"]["excess"],
                              share_positive=agg["share_positive"]))
    return pd.DataFrame(rows), pd.DataFrame(curve)


#: design C.  Five monotone maps from an instrument's increment to a common
#: utility.  Each is increasing and fixes zero, so the SIGN of an increment is
#: invariant to all of them; what varies is the relative magnitude an
#: instrument contributes to a mixed average.
UTILITY_MAPS = {
    "identity": lambda v, hr, sd: v,
    "headroom": lambda v, hr, sd: v / np.maximum(hr, 1e-6),
    "standardised": lambda v, hr, sd: v / max(sd, 1e-9),
    "square-root": lambda v, hr, sd: np.sign(v) * np.sqrt(np.abs(v)),
    "rank-logistic": lambda v, hr, sd: np.tanh(v / max(sd, 1e-9)),
}


def design_C(SC):
    """Partial identification over monotone utility maps."""
    rows = []
    for (log, target), sub in SC.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        for mapname, phi in UTILITY_MAPS.items():
            parts = []
            for metric, g in sub.groupby("metric"):
                sd = float(g.V.std(ddof=0))
                hr = (1.0 - g.without_f.values)
                parts.append(pd.DataFrame(dict(
                    u=phi(g.V.values.astype(float), hr, sd),
                    learner=g.learner.values, split=g.split.values,
                    quality_level=g.quality_level.values,
                    rung=g.rung.values, metric=metric)))
            U = pd.concat(parts, ignore_index=True)
            w = product_weights(U, "equal-level",
                                axes=tuple(list(AXES) + ["metric"]))
            v = U.u.values
            res, agg = rules_on(v, w, float(np.median(v)))
            rows.append(dict(log=log, target=target, utility_map=mapname,
                             unit="utility(" + mapname + ")",
                             excess_one_number=res["one-number"]["excess"],
                             excess_majority=res["majority"]["excess"],
                             one_number_adopts=res["one-number"]["adopts"],
                             majority_adopts=res["majority"]["adopts"],
                             mean_adopts=res["weighted-mean"]["adopts"],
                             share_positive=agg["share_positive"]))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def held_out(SC, n_rep=200):
    """Three out-of-sample evaluations, because the weighted-mean rule is
    optimal ON THE SURFACE IT AVERAGES by construction and an in-sample win is
    an identity, not evidence."""
    rng = np.random.default_rng(S.SEED)
    rows = []
    for (log, target, metric), sub in SC.groupby(["log", "target", "metric"]):
        if len(sub) < 16:
            continue
        v_all = sub.V.values.astype(float)
        v_conv = reference_value(sub)

        #  (a) HELD-OUT SPECIFICATIONS.  Choose the action on a random half of
        #      the admissible cells; pay the loss on the other half.
        for rep in range(n_rep):
            idx = rng.permutation(len(sub))
            h = len(idx) // 2
            fit, ev = idx[:h], idx[h:]
            w_ev = np.ones(len(ev)) / len(ev)
            L_ad = float((w_ev * np.maximum(0.0, -v_all[ev])).sum())
            L_de = float((w_ev * np.maximum(0.0, v_all[ev])).sum())
            best = min(L_ad, L_de)
            acts = {"one-number": v_conv > 0,
                    "uniform-beneficial": bool((v_all[fit] > 0).all()),
                    "majority": float((v_all[fit] > 0).mean()) > 0.5,
                    "weighted-mean": float(v_all[fit].mean()) > 0}
            for nm, ad in acts.items():
                rows.append(dict(log=log, target=target, metric=metric,
                                 unit=UNIT[metric], design="held-out cells",
                                 rep=rep, rule=nm,
                                 excess=(L_ad if ad else L_de) - best))

        #  (b) HELD-OUT TIME.  Choose the action on the earlier rolling folds;
        #      pay the loss on the later ones.  Nothing about the evaluation
        #      period is visible when the action is chosen.
        early = sub[sub.split.isin(["rolling1", "rolling2", "rolling3"])]
        late = sub[sub.split.isin(["rolling4", "rolling5"])]
        if len(early) >= 4 and len(late) >= 4:
            ve, vl = early.V.values.astype(float), late.V.values.astype(float)
            w = np.ones(len(vl)) / len(vl)
            L_ad = float((w * np.maximum(0.0, -vl)).sum())
            L_de = float((w * np.maximum(0.0, vl)).sum())
            best = min(L_ad, L_de)
            acts = {"one-number": v_conv > 0,
                    "uniform-beneficial": bool((ve > 0).all()),
                    "majority": float((ve > 0).mean()) > 0.5,
                    "weighted-mean": float(ve.mean()) > 0}
            for nm, ad in acts.items():
                rows.append(dict(log=log, target=target, metric=metric,
                                 unit=UNIT[metric], design="held-out time",
                                 rep=0, rule=nm,
                                 excess=(L_ad if ad else L_de) - best))
    R = pd.DataFrame(rows)

    #  (c) HELD-OUT LOGS.  Leave one log out, and ask whether the ORDERING of
    #      two named rules established on the rest survives on the one left
    #      out.  The comparison is PAIRWISE and is scored only where the two
    #      rules actually differ on both sides: with five instruments and
    #      nineteen pairs most cells have several rules tied at zero excess,
    #      and an argmin over ties measures the tie-break, not the rules.
    TOL = 1e-6
    lo = []
    if len(R):
        base = (R[R.design == "held-out cells"]
                .groupby(["log", "metric", "rule"]).excess.mean().reset_index())
        for a_rule, b_rule in (("one-number", "majority"),
                               ("one-number", "weighted-mean"),
                               ("majority", "weighted-mean")):
            for log in base.log.unique():
                for metric in base.metric.unique():
                    rest = base[(base.log != log) & (base.metric == metric)]
                    held = base[(base.log == log) & (base.metric == metric)]
                    if not len(rest) or not len(held):
                        continue
                    ra = rest[rest.rule == a_rule].excess.mean()
                    rb = rest[rest.rule == b_rule].excess.mean()
                    ha = held[held.rule == a_rule].excess.mean()
                    hb = held[held.rule == b_rule].excess.mean()
                    if not np.isfinite([ra, rb, ha, hb]).all():
                        continue
                    scored = bool(abs(ra - rb) >= TOL and abs(ha - hb) >= TOL)
                    lo.append(dict(held_out_log=log, metric=metric,
                                   comparison=a_rule + " vs " + b_rule,
                                   scored=scored,
                                   agrees=(bool((ra < rb) == (ha < hb))
                                           if scored else np.nan)))
    return R, pd.DataFrame(lo)


def main():
    t0 = time.time()
    SUR = S.read_results("s01_surface.csv")
    SUR = SUR[~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS)].copy()
    SUR["quality_level"] = (SUR.quality.astype(str) + "@"
                            + SUR.level.map(lambda x: "%.2f" % x))
    SC = SUR[SUR.metric.isin(S.SCALARS)].copy()

    print("=" * 92)
    print("s23  SPECIFICATION REGRET ON A COHERENT SCALE")
    print("=" * 92)

    A = design_A(SC)
    A.to_csv(RESULTS / "s23_metric_regret.csv", index=False)
    print("\nDESIGN A -- METRIC-SPECIFIC.  MEAN excess regret over the pairs,")
    print("in each instrument's own units, under the equal-level measure.")
    print("(The MEDIAN is zero for every rule and instrument: on most pairs")
    print(" every rule picks the same action, and the disagreement is what")
    print(" the mean and the counts below measure.)")
    piv = (A[A.measure == "equal-level"]
           .pivot_table(index="metric", columns="rule", values="excess",
                        aggfunc="mean"))
    print(piv.to_string(float_format=lambda x: "%.5f" % x))
    print("\nPAIRS ON WHICH A RULE IS STRICTLY SUBOPTIMAL")
    cnt = (A[A.measure == "equal-level"].assign(bad=lambda d: d.excess > 1e-9)
           .pivot_table(index="metric", columns="rule", values="bad",
                        aggfunc="sum"))
    print(cnt.to_string())

    #  the only cross-instrument statement design A permits: does the
    #  DIRECTION agree?
    direction = []
    for metric, g in A[A.measure == "equal-level"].groupby("metric"):
        one = g[g.rule == "one-number"].set_index(["log", "target"]).excess
        maj = g[g.rule == "majority"].set_index(["log", "target"]).excess
        k = one.index.intersection(maj.index)
        direction.append(dict(metric=metric, unit=UNIT[metric],
                              n_pairs=len(k),
                              one_number_worse=int((one[k] > maj[k]).sum()),
                              majority_worse=int((maj[k] > one[k]).sum()),
                              tied=int(np.isclose(one[k], maj[k]).sum()),
                              median_excess_one_number=float(one[k].median()),
                              median_excess_majority=float(maj[k].median())))
    DIR = pd.DataFrame(direction)
    DIR.to_csv(RESULTS / "s23_direction.csv", index=False)
    print("\nDIRECTION AGREEMENT ACROSS INSTRUMENTS")
    print(DIR.to_string(index=False, float_format=lambda x: "%.5f" % x))

    #  --- design B ---------------------------------------------------------
    tg = np.array(S.NB_GRID, float)
    tmeas = {
        "uniform over the declared operating range":
            dict(zip(tg, np.full(len(tg), 1.0 / len(tg)))),
        "concentrated on a 1:4 exchange rate":
            dict(zip(tg, np.exp(-((tg - 0.20) ** 2) / (2 * 0.05 ** 2))
                     / np.exp(-((tg - 0.20) ** 2) / (2 * 0.05 ** 2)).sum())),
    }
    B, BC = design_B(tmeas)
    if len(B):
        B.to_csv(RESULTS / "s23_utility_regret.csv", index=False)
        BC.to_csv(RESULTS / "s23_utility_curve.csv", index=False)
        print("\nDESIGN B -- COMMON OPERATIONAL UTILITY (calibrated net "
              "benefit, per case)")
        print(B[B.threshold_measure.str.startswith("uniform")]
              .groupby("rule").excess.median()
              .to_string(float_format=lambda x: "%.6f" % x))
    else:
        print("\nDESIGN B -- skipped: s26 has not produced calibrated curves")

    MIS = misreport(SC)
    MIS.to_csv(RESULTS / "s23_misreport.csv", index=False)
    print()
    print("SIGN DISAGREEMENT OF A ONE-NUMBER REPORT, BY MEASURE")
    print(MIS.groupby("measure").misreport.describe()[["50%", "min", "max"]]
          .to_string(float_format=lambda x: "%.3f" % x))

    C = design_C(SC)
    C.to_csv(RESULTS / "s23_partial.csv", index=False)
    print("\nDESIGN C -- PARTIAL IDENTIFICATION over monotone utility maps")
    print(C.groupby("utility_map")[["excess_one_number", "excess_majority"]]
          .median().to_string(float_format=lambda x: "%.5f" % x))
    inv = C.groupby(["log", "target"]).agg(
        n_maps=("utility_map", "nunique"),
        agree_one=("one_number_adopts", "nunique"),
        agree_mean=("mean_adopts", "nunique")).reset_index()
    n_invariant = int(((inv.agree_one == 1) & (inv.agree_mean == 1)).sum())
    print("  the adopt/decline conclusion is the same under all five maps on "
          "%d of %d pairs" % (n_invariant, len(inv)))

    H, LO = held_out(SC)
    H.to_csv(RESULTS / "s23_heldout.csv.gz", index=False, compression="gzip")
    LO.to_csv(RESULTS / "s23_leaveoneout.csv", index=False)
    print("\nOUT OF SAMPLE -- mean excess regret, by design and rule")
    hp = H.pivot_table(index=["design", "metric"], columns="rule",
                       values="excess", aggfunc="mean")
    print(hp.to_string(float_format=lambda x: "%.5f" % x))

    #  the in-sample identity, reported as a check on the algebra
    ins = A[A.measure == "equal-level"]
    ident = ins[ins.rule == "weighted-mean"].excess.abs().max()

    facts = dict(
        n_metric_regret=len(A), n_partial=len(C), n_heldout=len(H),
        misreport_equal=float(MIS[MIS.measure == "equal-level"].misreport.median()),
        misreport_reference=float(MIS[MIS.measure == "reference"].misreport.median()),
        misreport_concentrated=float(
            MIS[MIS.measure == "concentrated"].misreport.median()),
        misreport_measure_spread=float(
            MIS.groupby("measure").misreport.median().max()
            - MIS.groupby("measure").misreport.median().min()),
        n_misreport_over_ten=int(
            (MIS[MIS.measure == "equal-level"].misreport > 0.10).sum()),
        identity_max_abs_excess=float(ident),
        n_instruments=int(A.metric.nunique()),
        n_pairs=int(A.groupby(["log", "target"]).ngroups),
        n_maps_invariant=n_invariant, n_pairs_maps=len(inv),
        runtime_s=round(time.time() - t0, 1))
    for m in S.SCALARS:
        g = A[(A.measure == "equal-level") & (A.metric == m)]
        facts["excess_one_number_" + m] = float(
            g[g.rule == "one-number"].excess.median())
        facts["excess_majority_" + m] = float(
            g[g.rule == "majority"].excess.median())
        h = H[(H.metric == m) & (H.design == "held-out cells")]
        facts["oos_one_number_" + m] = float(
            h[h.rule == "one-number"].excess.mean())
        facts["oos_majority_" + m] = float(
            h[h.rule == "majority"].excess.mean())
        facts["oos_mean_" + m] = float(
            h[h.rule == "weighted-mean"].excess.mean())
    if len(LO):
        sc = LO[LO.scored]
        facts["leaveoneout_agree"] = (float(sc.agrees.mean()) if len(sc)
                                      else np.nan)
        facts["leaveoneout_n"] = int(len(sc))
        facts["leaveoneout_unscored"] = int((~LO.scored).sum())
    for m in S.SCALARS:
        g = A[(A.measure == "equal-level") & (A.metric == m)]
        facts["mean_excess_one_number_" + m] = float(
            g[g.rule == "one-number"].excess.mean())
        facts["mean_excess_majority_" + m] = float(
            g[g.rule == "majority"].excess.mean())
        facts["n_bad_one_number_" + m] = int(
            (g[g.rule == "one-number"].excess > 1e-9).sum())
        facts["n_bad_majority_" + m] = int(
            (g[g.rule == "majority"].excess > 1e-9).sum())
        facts["n_bad_uniform_" + m] = int(
            (g[g.rule == "uniform-beneficial"].excess > 1e-9).sum())
    if len(B):
        for nm in ("one-number", "majority", "weighted-mean",
                   "uniform-beneficial"):
            g = B[B.threshold_measure.str.startswith("uniform")
                  & (B.rule == nm)]
            facts["nb_excess_" + nm.replace("-", "_")] = float(
                g.excess.median())
    ht = H[H.design == "held-out time"]
    if len(ht):
        for nm in ("one-number", "majority", "weighted-mean"):
            facts["oost_" + nm.replace("-", "_")] = float(
                ht[ht.rule == nm].excess.mean())
    pd.DataFrame([facts]).to_csv(RESULTS / "s23_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

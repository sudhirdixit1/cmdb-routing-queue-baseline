"""s42 -- ROUND TWENTY-SIX.  THE FIVE QUANTITIES THE SIXTH REFEREE ASKED FOR
THAT CAN BE COMPUTED WITHOUT A NEW BOOTSTRAP.

The sixth report's Phase A has seven items.  Four of them (A1 the weighted
bootstrap, A2 four hundred draws on a designed inference surface, A6
degradation on both halves, A7 a prefix axis) need the corpus refetched and
every arm refitted, and this round does not run them; Section 11 and the
response letter say so.  The other three -- A3, A4, A5 -- and three of the
Phase B items are functions of files this repository already carries, and
they are computed here.

A3.  SPLIT IS AN ERROR STRATUM, NOT AN ANALYST CHOICE.  Five of the split
axis's six levels are expanding-origin folds on the same data.  A functional
ANOVA that pools them reports sampling variability as specification
sensitivity, and "no single axis dominates" and "56.0% is higher-order" are
both inflated by it.  The repair is exact rather than approximate: because the
decomposition is orthogonal over a complete factorial, the components
partition into those that involve the split and those that do not, and

    resampling share      = sum over u containing `split' of S_u
    analyst-choice share  = sum over non-empty u contained in {pipeline, rung}
    counterfactual share  = S_quality
    mixed share           = the rest of the split-free components

sum to one exactly.  The first is what fold-averaging removes; the surface a
reader should be shown is the one that remains, so the three remaining axes
are also decomposed again ON the fold-averaged surface, where the shares are
renormalised to that surface's own variance and the higher-order share is net
of resampling.  Nothing is estimated here that was not already exact.

A4.  A SIGN FLIP BETWEEN +0.003 AND -0.003 IS NOT A MISSTATEMENT.  The
manuscript's disagreement rate counts a cell whenever its sign differs from
the reference cell's, at any magnitude, and eight of nineteen reference
increments are inside a hundredth of an AUC point.  A minimal practically
important difference is declared -- MPID = 0.01 AUC, the width the clinical
prediction literature treats as the smallest increment worth acting on -- and
three further quantities are reported beside the existing rate:

  MPID-RESTRICTED   both the reference cell and the comparison cell must
                    exceed the MPID in absolute value before a disagreement
                    between them is counted
  REFERENCE-CONDITIONED  the rate computed only on pairs whose OWN reference
                    cell the band resolves; on six pairs it does not, and
                    there the "misstatement" is against a coin flip
  MEAN ABSOLUTE DEVIATION  the average |V_s - V_ref| over resolved cells, in
                    AUC, which is a magnitude and not a rate

A5.  WHAT WAS ACTUALLY VARIED.  Definition 1 lists nine axes, Table 2 has no
target row, and the per-pair factorial is five axes wide.  The inventory is
read off the master surface -- per pair, per axis, the number of levels that
ran -- so the manuscript's claim about its own design space is a table
generated from the design space rather than a sentence.

B3.  A DIRECTIONAL LABEL ON TWO CELLS OF A HUNDRED AND EIGHTY.  The region
label reports a direction whenever some cell resolves and none resolves the
other way, however few, and rho hides how few.  The triple (beneficial,
harmful, unresolved) is computed per pair, and the labels are recomputed under
a minimum resolved share, at three thresholds, so the cost of the condition is
measured rather than asserted.

M5.  THE BASELINE SPREAD OVER RUNGS AN ANALYST WOULD BUILD.  The headline
spread ranges over the half-of-intake rung, which is the same kind of
impoverished counterfactual as the intercept-only rung the manuscript already
excludes.  The spread is recomputed over the rungs that remain.

    python s42_round26.py

Outputs: results/s42_strata.csv    the four-way variance partition, per pair
         results/s42_foldavg.csv   indices on the fold-averaged surface
         results/s42_mpid.csv      the MPID-restricted rates, per pair
         results/s42_axes.csv      levels per axis per pair
         results/s42_regions.csv   the resolution triple and the minimum-share
                                   labels
         results/s42_spread.csv    the baseline spread, both rung sets
         results/s42_facts.csv
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
import s34_reporting as S34  # noqa: E402
from common import RESULTS  # noqa: E402

#: the declared minimal practically important difference, in AUC.  One
#: hundredth of an AUC point: the increment the clinical-prediction literature
#: treats as the smallest worth acting on, and the width inside which eight of
#: this corpus's nineteen reference increments sit.  It is declared here, in
#: one place, and every quantity that uses it reads it from here.
MPID_AUC = 0.01

#: the minimum share of a pair's inference family that must resolve before a
#: DIRECTIONAL region label is applied.  Three are reported; the middle one is
#: the manuscript's.
MIN_RESOLVED_SHARES = (0.01, 0.05, 0.10)
MIN_RESOLVED_DECLARED = 0.05

#: the axes of the pooled decomposition, and the kind of thing each one is
AXES = ("learner", "split", "quality_level", "rung")
ANALYST = ("learner", "rung")
COUNTERFACTUAL = ("quality_level",)
RESAMPLING = ("split",)

#: the rungs a spread over "the baseline" should range over.  B_empty is
#: already excluded everywhere (spec.IMPLAUSIBLE_RUNGS); B_half is the same
#: argument one rung later -- half of an intake block, chosen by cardinality,
#: is not a baseline anybody reports against.
IMPOVERISHED_RUNGS = ("B_half",)


# --------------------------------------------------------------------------
def surface():
    """The admissible scalar surface, named as the other round-twenty scripts
    name it, so a cell here is the same cell there."""
    SUR = S.read_results("s01_surface.csv")
    SUR = SUR[~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS)].copy()
    SUR["quality_level"] = (SUR.quality.astype(str) + "@"
                            + SUR.level.map(lambda x: "%.2f" % x))
    return SUR[SUR.metric.isin(S.SCALARS)].copy()


# --------------------------------------------------------------------------
# A3 -- the split as an error stratum
# --------------------------------------------------------------------------
def strata(SC, split_set="all"):
    """The exact four-way partition, and the fold-averaged decomposition.

    Both are taken under the equal-level measure, within each instrument, and
    the median over instruments is what a pair carries -- the same aggregation
    Section 6.2 uses, so the two decompositions are comparable line for line.

    `split_set` controls what the split axis is allowed to be.  Under `all' it
    is the declared six levels, of which five are expanding-origin folds and
    one is the single temporal holdout --- so the axis mixes five replicates
    with one genuine analyst choice, WHICH SPLIT RULE, and calling the whole
    of it resampling overstates the stratum.  Under `rolling' the holdout is
    dropped and every remaining level is a fold of the same rule, so the share
    is resampling and nothing else.  Both are reported; the second is the one
    that cannot be argued with.
    """
    if split_set == "rolling":
        SC = SC[SC["split"].astype(str).str.startswith("rolling")].copy()
    part_rows, fold_rows = [], []
    for (log, target, metric), sub in SC.groupby(["log", "target", "metric"]):
        res = A22.decompose(sub, AXES, "V", "equal-level")
        if res is None:
            continue
        #  components are keyed by tuples of AXIS INDICES; name them
        named = {frozenset(AXES[j] for j in u): v
                 for u, v in res["components"].items()}
        split_involved = sum(v for u, v in named.items()
                             if RESAMPLING[0] in u)
        analyst = sum(v for u, v in named.items()
                      if u and u <= set(ANALYST))
        counterfactual = sum(v for u, v in named.items()
                             if u == set(COUNTERFACTUAL))
        mixed = sum(v for u, v in named.items()
                    if u and RESAMPLING[0] not in u
                    and not (u <= set(ANALYST)) and u != set(COUNTERFACTUAL))
        part_rows.append(dict(
            log=log, target=target, metric=metric, split_set=split_set,
            share_resampling=split_involved,
            share_analyst=analyst,
            share_counterfactual=counterfactual,
            share_mixed=mixed,
            check_sum=split_involved + analyst + counterfactual + mixed,
            var_pooled=res["var"]))

        #  the fold-averaged surface: the same cells with the split
        #  marginalised out under equal weights, which is exactly the
        #  conditional mean the components not involving `split' are built
        #  from.  Decomposing it again gives indices renormalised to the
        #  variance that survives fold-averaging.
        fa = (sub.groupby(["learner", "quality_level", "rung"], as_index=False)
                 .agg(V=("V", "mean"), n_folds=("split", "nunique")))
        r2 = A22.decompose(fa, ("learner", "quality_level", "rung"), "V",
                           "equal-level")
        if r2 is None:
            continue
        s_first = sum(r2["first"].values())
        fold_rows.append(dict(
            log=log, target=target, metric=metric, split_set=split_set,
            S_learner=r2["first"]["learner"],
            S_quality=r2["first"]["quality_level"],
            S_rung=r2["first"]["rung"],
            largest_first_order=max(r2["first"].values()),
            largest_first_order_axis=max(r2["first"], key=r2["first"].get),
            interaction_total=1.0 - s_first,
            var_foldavg=r2["var"],
            var_pooled=res["var"],
            var_ratio=r2["var"] / res["var"] if res["var"] > 0 else np.nan,
            n_folds=int(fa.n_folds.max())))
    return pd.DataFrame(part_rows), pd.DataFrame(fold_rows)


# --------------------------------------------------------------------------
# A4 -- the minimal practically important difference
# --------------------------------------------------------------------------
def mpid_rates(SC, RES):
    """Per pair: the existing rate, the MPID-restricted rate, whether the
    reference cell itself resolves, and the mean absolute deviation from the
    reference over resolved cells.

    The MPID is declared in AUC, so the restriction is applied on the AUC
    sub-surface: an increment in average precision and an increment in AUC are
    not the same units and one threshold cannot serve both (Proposition 1).
    The unrestricted rate is recomputed on the same sub-surface beside it, so
    the two differ by the restriction and not by the instrument.
    """
    key = [c for c in S34.CELLKEY if c in RES.columns]
    rows = []
    for (log, target), sub in SC.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        r = RES[(RES.log == log) & (RES.target == target)]
        sub = sub.copy()
        if len(r):
            sub = sub.merge(r.drop(columns=["log", "target"]), on=key,
                            how="left")
        for c in ("resolved_nominal", "resolved_calibrated"):
            if c not in sub.columns:
                sub[c] = False
            sub[c] = np.where(sub[c].isna(), False, sub[c]).astype(bool)

        v_conv = S23.reference_value(
            sub[sub.metric == A22.REFERENCE["metric"]]
            if (sub.metric == A22.REFERENCE["metric"]).any() else sub)

        #  is the REFERENCE cell one the band resolves?  A rate that counts a
        #  disagreement with an unresolved reference is counting a
        #  disagreement with a coin flip.
        ref_mask = np.ones(len(sub), bool)
        for a, lv in A22.REFERENCE.items():
            if a in sub.columns:
                ref_mask &= (sub[a].astype(str) == lv).values
        ref_resolved = bool(sub.loc[ref_mask, "resolved_calibrated"].any())

        auc = sub[sub.metric == "auc"].copy()
        v = auc.V.values.astype(float)
        disagree = (v > 0) if v_conv <= 0 else (v <= 0)
        big = np.abs(v) >= MPID_AUC
        ref_big = abs(v_conv) >= MPID_AUC
        res_cal = auc.resolved_calibrated.values

        both_big = big & ref_big
        #  THE THIRD RESTRICTION.  Section 6.4 already imposes two -- the
        #  axes an analyst chooses, and the cells the band resolves -- and
        #  says the joint rate "is the number this section's own argument
        #  asks for".  The MPID is a third of the same kind, and the argument
        #  asks for all three at once or it does not mean what it says.
        lat = ((auc.quality.astype(str) == "clean")
               & (auc["split"].astype(str) == "holdout70")).values
        full = lat & res_cal & both_big
        rows.append(dict(
            log=log, target=target,
            v_reference=v_conv,
            reference_above_mpid=bool(ref_big),
            reference_resolved=ref_resolved,
            n_auc_cells=int(len(auc)),
            n_auc_above_mpid=int(big.sum()),
            share_auc_above_mpid=float(big.mean()) if len(auc) else np.nan,
            n_disagree_auc=int(disagree.sum()),
            rate_auc=float(disagree.mean()) if len(auc) else np.nan,
            n_disagree_mpid=int((disagree & both_big).sum()),
            n_cells_mpid=int(both_big.sum()),
            rate_mpid=(float(disagree[both_big].mean())
                       if both_big.sum() else np.nan),
            n_resolved_auc=int(res_cal.sum()),
            n_disagree_resolved_auc=int((disagree & res_cal).sum()),
            rate_resolved_auc=(float(disagree[res_cal].mean())
                               if res_cal.sum() else np.nan),
            n_resolved_mpid=int((res_cal & both_big).sum()),
            n_disagree_resolved_mpid=int((disagree & res_cal & both_big).sum()),
            rate_resolved_mpid=(float(disagree[res_cal & both_big].mean())
                                if (res_cal & both_big).sum() else np.nan),
            n_full=int(full.sum()),
            n_disagree_full=int((disagree & full).sum()),
            rate_full=(float(disagree[full].mean())
                       if full.sum() else np.nan),
            n_latitude_auc=int(lat.sum()),
            n_disagree_latitude_auc=int((disagree & lat).sum()),
            mad_resolved=(float(np.abs(v[res_cal] - v_conv).mean())
                          if res_cal.sum() else np.nan),
            mad_full=(float(np.abs(v[full] - v_conv).mean())
                      if full.sum() else np.nan),
            mad_all=float(np.abs(v - v_conv).mean()) if len(auc) else np.nan,
        ))
    return pd.DataFrame(rows)


def by_instrument(SC, RES):
    """Where the corpus's resolved-cell disagreement actually lives.

    The MPID is declared in AUC and can only be applied there, so a reader is
    owed the AUC sub-surface's own unrestricted rate beside the corpus rate
    the abstract quotes -- otherwise the fall from one to the other reads as
    the MPID's doing when part of it is the instrument's.
    """
    key = [c for c in S34.CELLKEY if c in RES.columns]
    rows = []
    for (log, target), sub in SC.groupby(["log", "target"]):
        r = RES[(RES.log == log) & (RES.target == target)]
        sub = sub.copy()
        if len(r):
            sub = sub.merge(r.drop(columns=["log", "target"]), on=key,
                            how="left")
        if "resolved_calibrated" not in sub.columns:
            continue
        sub["resolved_calibrated"] = np.where(
            sub.resolved_calibrated.isna(), False,
            sub.resolved_calibrated).astype(bool)
        v_conv = S23.reference_value(
            sub[sub.metric == A22.REFERENCE["metric"]]
            if (sub.metric == A22.REFERENCE["metric"]).any() else sub)
        for metric, g in sub.groupby("metric"):
            v = g.V.values.astype(float)
            dis = (v > 0) if v_conv <= 0 else (v <= 0)
            m = g.resolved_calibrated.values
            rows.append(dict(log=log, target=target, metric=metric,
                             n_cells=len(g), n_resolved=int(m.sum()),
                             n_disagree_resolved=int((dis & m).sum())))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# A5 -- what was actually varied, per pair
# --------------------------------------------------------------------------
def axis_inventory(SUR):
    """Levels per axis per pair, read off the surface itself.

    `pipeline' is one axis in the manuscript and two things in the data, so
    both counts are given: the number of pipelines that ran and the number of
    distinct model families among them.
    """
    rows = []
    for (log, target), sub in SUR.groupby(["log", "target"]):
        fam = {S.LEARNER_ENCODING.get(l, l).split("+")[0]: 1
               for l in sub.learner.unique()}
        rows.append(dict(
            log=log, target=target, domain=sub.domain.iloc[0],
            register_field=sub.f.iloc[0], free_field=sub.g.iloc[0],
            n_pipeline=int(sub.learner.nunique()),
            n_encoding=len(fam),
            n_family=len({("hgb" if l.startswith("hgb") else "logit")
                          for l in sub.learner.unique()}),
            n_split=int(sub["split"].nunique()),
            n_quality=int(sub.quality_level.nunique()),
            n_rung=int(sub.rung.nunique()),
            n_instrument=int(sub.metric.isin(S.SCALARS).groupby(
                sub.metric).any().sum()),
            n_cells=int(len(sub)),
            n_train=int(sub.n.iloc[0]),
            card_f=int(sub.card_f.iloc[0]),
            prevalence=float(sub.prevalence.iloc[0])))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# B3 -- the resolution triple, and a minimum resolved share
# --------------------------------------------------------------------------
def region_triple():
    G = pd.read_csv(RESULTS / "s48w_regions.csv")
    G = G.copy()
    #  ROUND TWENTY-SEVEN.  This read `s33_regions', the COVERAGE-CALIBRATED
    #  labels for the previous inference surface, and used its column names.
    #  The designed surface has no calibrated file --- the calibration was
    #  fitted on the old plane and the coverage measurement now says the new
    #  families need a LARGER widening than it supplies --- so the operative
    #  labels are the nominal ones, and they are aliased here to the names the
    #  rest of this function was written against.  Aliasing rather than
    #  renaming throughout keeps the diff to the read.
    G["cells"] = G.n_cells
    G["beneficial_cal"] = G.n_beneficial
    G["harmful_cal"] = G.n_harmful
    G["unresolved_cal"] = G.n_unresolved
    G["rho_calibrated"] = G.rho
    G["region_calibrated"] = G.region
    G["n_family"] = G.cells
    G["share_beneficial"] = G.beneficial_cal / G.cells
    G["share_harmful"] = G.harmful_cal / G.cells
    G["share_unresolved"] = G.unresolved_cal / G.cells
    G["share_resolved"] = 1.0 - G.share_unresolved
    for th in MIN_RESOLVED_SHARES:
        col = "region_min%02d" % int(round(th * 100))
        G[col] = np.where(
            (G.share_resolved < th)
            & (G.region_calibrated.astype(str) != "unresolved"),
            "unresolved (below minimum share)", G.region_calibrated)
        G["changed_min%02d" % int(round(th * 100))] = (
            G[col].astype(str) != G.region_calibrated.astype(str))
    return G


# --------------------------------------------------------------------------
# M5 -- the baseline spread over rungs an analyst would build
# --------------------------------------------------------------------------
def baseline_spread(SC):
    """At the reference cell in every axis but the rung, the range of the
    increment over (a) every admissible rung, which is what the abstract
    quotes, and (b) the rungs left once the impoverished one goes."""
    rows = []
    ref = dict(A22.REFERENCE)
    for (log, target), sub in SC.groupby(["log", "target"]):
        q = sub
        for a, lv in ref.items():
            if a == "rung" or a not in q.columns:
                continue
            q = q[q[a].astype(str) == lv]
        if not len(q):
            continue
        allr = q.groupby("rung", as_index=False).V.mean()
        realistic = allr[~allr.rung.isin(IMPOVERISHED_RUNGS)]
        if len(allr) < 2 or len(realistic) < 2:
            continue
        rows.append(dict(
            log=log, target=target,
            n_rung_all=len(allr), n_rung_realistic=len(realistic),
            spread_all=float(allr.V.max() - allr.V.min()),
            spread_realistic=float(realistic.V.max() - realistic.V.min()),
            v_reference=float(
                allr.loc[allr.rung == ref["rung"], "V"].iloc[0])
            if (allr.rung == ref["rung"]).any() else np.nan))
    R = pd.DataFrame(rows)
    if len(R):
        R["exceeds_increment_all"] = R.spread_all > R.v_reference.abs()
        R["exceeds_increment_realistic"] = (R.spread_realistic
                                            > R.v_reference.abs())
    return R


# --------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 92)
    print("s42  ROUND TWENTY-SIX -- A3, A4, A5, B3 AND M5")
    print("=" * 92)

    SUR = surface()
    RES = S34.resolved_map()
    print("  %d admissible scalar rows, %d pairs"
          % (len(SUR), SUR.groupby(["log", "target"]).ngroups))

    Pa, Fa = strata(SUR, "all")
    Pr, Fr = strata(SUR, "rolling")
    P = pd.concat([Pa, Pr], ignore_index=True)
    F = pd.concat([Fa, Fr], ignore_index=True)
    P.to_csv(RESULTS / "s42_strata.csv", index=False)
    F.to_csv(RESULTS / "s42_foldavg.csv", index=False)
    pp = Pa.groupby(["log", "target"]).median(numeric_only=True)
    ppr = Pr.groupby(["log", "target"]).median(numeric_only=True)
    print("\nA3  THE FOUR-WAY PARTITION, median over instruments, then over "
          "pairs")
    print("    %-22s %8s %8s" % ("", "all six", "rolling"))
    for c in ("share_analyst", "share_counterfactual", "share_mixed",
              "share_resampling"):
        print("    %-22s %8.3f %8.3f" % (c, pp[c].median(), ppr[c].median()))
    print("    identity sum_u S_u = 1 holds to %.2e"
          % float(np.abs(P.check_sum - 1.0).max()))
    ff = Fa.groupby(["log", "target"]).median(numeric_only=True)
    print("\nA3  ON THE FOLD-AVERAGED SURFACE (shares of ITS variance)")
    for c in ("S_learner", "S_quality", "S_rung", "interaction_total",
              "var_ratio"):
        print("    %-22s %6.3f   [%.3f, %.3f]"
              % (c, ff[c].median(), ff[c].min(), ff[c].max()))

    M = mpid_rates(SUR, RES)
    M.to_csv(RESULTS / "s42_mpid.csv", index=False)
    print("\nA4  THE MPID-RESTRICTED RATE  (MPID = %.3f AUC)" % MPID_AUC)
    print(M[["log", "target", "v_reference", "reference_above_mpid",
             "reference_resolved", "rate_auc", "rate_mpid",
             "rate_resolved_auc", "rate_resolved_mpid", "mad_resolved"]]
          .to_string(index=False, float_format=lambda x: "%.4f" % x))

    BI = by_instrument(SUR, RES)
    BI.to_csv(RESULTS / "s42_instrument.csv", index=False)
    print("\nA4  WHERE THE RESOLVED-CELL DISAGREEMENT LIVES, by instrument")
    gi = BI.groupby("metric")[["n_resolved", "n_disagree_resolved"]].sum()
    gi["rate"] = gi.n_disagree_resolved / gi.n_resolved.replace(0, np.nan)
    print(gi.to_string(float_format=lambda x: "%.4f" % x))

    A = axis_inventory(SUR)
    A.to_csv(RESULTS / "s42_axes.csv", index=False)
    print("\nA5  LEVELS PER AXIS PER PAIR")
    print(A[["log", "target", "n_pipeline", "n_split", "n_quality", "n_rung",
             "n_instrument", "register_field", "free_field"]]
          .to_string(index=False))

    G = region_triple()
    G.to_csv(RESULTS / "s42_regions.csv", index=False)
    col = "changed_min%02d" % int(round(MIN_RESOLVED_DECLARED * 100))
    print("\nB3  THE RESOLUTION TRIPLE, and the minimum-share condition")
    print(G[["log", "target", "n_family", "beneficial_cal", "harmful_cal",
             "unresolved_cal", "share_resolved", "region_calibrated",
             col]].to_string(index=False,
                             float_format=lambda x: "%.3f" % x))
    print("    %d of %d directional labels fall to the %.0f%% condition"
          % (int(G[col].sum()), len(G), 100 * MIN_RESOLVED_DECLARED))

    R = baseline_spread(SUR)
    R.to_csv(RESULTS / "s42_spread.csv", index=False)
    print("\nM5  THE BASELINE SPREAD, both rung sets")
    print(R.to_string(index=False, float_format=lambda x: "%.4f" % x))

    facts = dict(
        mpid_auc=MPID_AUC,
        min_resolved_declared=MIN_RESOLVED_DECLARED,
        n_pairs=int(SUR.groupby(["log", "target"]).ngroups),
        share_analyst_median=float(pp.share_analyst.median()),
        share_counterfactual_median=float(pp.share_counterfactual.median()),
        share_mixed_median=float(pp.share_mixed.median()),
        share_resampling_median=float(pp.share_resampling.median()),
        share_analyst_rolling_median=float(ppr.share_analyst.median()),
        share_counterfactual_rolling_median=float(
            ppr.share_counterfactual.median()),
        share_mixed_rolling_median=float(ppr.share_mixed.median()),
        share_resampling_rolling_median=float(ppr.share_resampling.median()),
        n_resampling_largest=int((pp.share_resampling
                                  > pp[["share_analyst",
                                        "share_counterfactual",
                                        "share_mixed"]].max(axis=1)).sum()),
        partition_max_error=float(np.abs(P.check_sum - 1.0).max()),
        foldavg_interaction_median=float(ff.interaction_total.median()),
        #  ROUND TWENTY-SEVEN.  This alone among the fold-averaged
        #  statistics pooled BOTH split sets; `foldavg_interaction_median'
        #  and `var_ratio_median' beside it are computed on `Fa', the `all'
        #  set, and the manuscript quotes all three in one sentence as
        #  properties of the same surface.  Pooling moved it from 38.9 to
        #  38.8 per cent --- a tenth of a point, and a different population
        #  from its own neighbours.
        foldavg_largest_first_median=float(
            Fa.groupby(["log", "target"]).largest_first_order.median()
            .median()),
        var_ratio_median=float(ff.var_ratio.median()),
        spread_all_median=float(R.spread_all.median()),
        spread_realistic_median=float(R.spread_realistic.median()),
        spread_realistic_max=float(R.spread_realistic.max()),
        n_exceeds_realistic=int(R.exceeds_increment_realistic.sum()),
        n_exceeds_all=int(R.exceeds_increment_all.sum()),
        n_full=int(M.n_full.sum()),
        n_disagree_full=int(M.n_disagree_full.sum()),
        mad_full_median=float(M.mad_full.median()),
        n_ref_below_mpid=int((~M.reference_above_mpid).sum()),
        n_ref_unresolved=int((~M.reference_resolved).sum()),
        n_labels_lost_to_min_share=int(G[col].sum()),
        elapsed_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s42_facts.csv", index=False)
    print("\n  wrote results/s42_*.csv in %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

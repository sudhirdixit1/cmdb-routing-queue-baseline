"""round20_numbers -- the macros and tables round twenty adds.

Kept beside `make_numbers.py` rather than inside it, because that file is
already thirteen hundred lines and the round-twenty quantities come from a
disjoint set of result files.  `make_numbers.main` calls `emit` once, after
its own macros are defined and before `numbers.tex` is written, so there is
still exactly one writer of the macro file and exactly one of each number.

Every macro here resolves to the visible `??` marker if its result file is
absent, which is what makes a partial build visibly partial.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


#  How the five scalar instruments are named in prose, so that a macro
#  holding a LIST of them prints the manuscript's own words rather than the
#  result file's column values.
_LABEL = {
    "auc": "ROC AUC",
    "ap": "average precision",
    "brier_skill": "Brier skill",
    "logloss_skill": "log-loss skill",
    "nagelkerke": "Nagelkerke $R^2$",
}


def emit(mn):
    """Define every round-twenty macro.  `mn` is the make_numbers module, so
    this file uses that module's put/load/pct/num/sig helpers and writes into
    the same macro table."""
    put, load, pct, num, sig, first = (mn.put, mn.load, mn.pct, mn.num,
                                       mn.sig, mn.first)
    thousands = mn.thousands

    # ================================================================
    # s25 -- the denominator audit
    # ================================================================
    A25 = load("s25_facts.csv")
    AUD = load("s25_audit.csv")
    REP = load("s25_representative.csv")
    put("nDeclaredCells", thousands(first(A25, "declared_cells_total")))
    put("nDeclaredScalar", thousands(first(A25, "declared_scalar_total")))
    put("nDeclaredAdmissible", thousands(first(A25, "declared_admissible_total")))
    put("nDeclaredAdmissibleScalar",
        thousands(first(A25, "declared_admissible_scalar_total")))
    put("nDeclaredAdmissibleDC",
        thousands(first(A25, "declared_admissible_dc_total")))
    put("nComputationalCells",
        thousands(first(A25, "declared_admissible_scalar_total")))
    put("nComputationalRows", thousands(first(A25, "computational_rows_total")))
    put("nDuplicateCells", thousands(first(A25, "duplicates_total")))
    put("nMissingCells", thousands(first(A25, "missing_total")))
    put("nExclusionRows", thousands(first(A25, "n_exclusions")))
    if REP is not None and len(REP):
        gap = (REP.share_positive_declared
               - REP.share_positive_inference).abs()
        put("repGapMedian", num(float(gap.median()), 3))
        put("repGapMax", num(float(gap.max()), 3))
    else:
        put("repGapMedian", None)
        put("repGapMax", None)

    # ================================================================
    # s20/s21 -- the inference surface and its bands
    # ================================================================
    G20 = load("s44_grid.csv")
    #  ROUND TWENTY-SEVEN.  `s20_facts.csv' was loaded here and never
    #  read -- one occurrence in the file.  It was found while writing the
    #  re-pointing diff for the new surface, as the one site that would
    #  have needed its columns checked by hand; a load nothing consumes
    #  needs no columns and no successor.  Removed rather than re-pointed.
    F21 = load("s48w_facts.csv")
    Q21 = load("s48w_critical.csv")
    R21 = load("s48w_regions.csv")
    if G20 is not None and len(G20):
        put("nInferenceCells", thousands(int(G20.cells.sum())))
        put("nInferenceScalar", thousands(int(G20.scalar_cells.sum())))
    else:
        put("nInferenceCells", None)
        put("nInferenceScalar", None)
    #  The DRAW COUNT is read from the files that were written, not from the
    #  plan that requested them.  A run can be resumed, extended or trimmed,
    #  and what a reader needs to know is how many draws each pair actually
    #  carries -- which the denominator audit prints per pair.
    if AUD is not None and len(AUD) and AUD.inference_draws.max() > 0:
        dr = AUD.inference_draws[AUD.inference_draws > 0]
        put("nDrawsSurface", thousands(int(dr.median())))
        put("nDrawsSurfaceMin", thousands(int(dr.min())))
        put("nDrawsSurfaceMax", thousands(int(dr.max())))
        #  ROUND TWENTY-THREE.  The DECLARED budget is not the EFFECTIVE one:
        #  a replicate missing any cell of a family is dropped, because a
        #  maximum over a moving set is not a maximum, and two families
        #  retain 33 of 40.  A referee asked for the effective range and was
        #  right that it is the number a reader needs.
        INC = load("s48w_incomplete.csv")
        if INC is not None and len(INC) and "n_draws_complete" in INC.columns:
            put("nDrawsEffectiveMin",
                thousands(int(min(int(dr.min()),
                                  int(INC.n_draws_complete.min())))))
        else:
            put("nDrawsEffectiveMin", thousands(int(dr.min())))
    elif G20 is not None and len(G20):
        put("nDrawsSurface", thousands(int(G20.draws.median())))
        put("nDrawsSurfaceMin", thousands(int(G20.draws.min())))
        put("nDrawsSurfaceMax", thousands(int(G20.draws.max())))
        put("nDrawsEffectiveMin", thousands(int(G20.draws.min())))
    else:
        for k in ("nDrawsSurface", "nDrawsSurfaceMin", "nDrawsSurfaceMax",
                  "nDrawsEffectiveMin"):
            put(k, None)
    #  ROUND TWENTY-SEVEN.  TWO denominators, because the manuscript uses two
    #  and one macro was serving both.
    #
    #  `computational_cells` is s25_denominator's count of the arms actually
    #  evaluated on the FULL declared grid, and the full grid carries the
    #  intercept-only rung -- the rung Table~\ref{tab:axes} calls "in the
    #  surface, out of every admissible set" and Table~\ref{tab:denominator}
    #  prints under `model fits'.  A share against it is therefore the share
    #  of the MASTER SURFACE FILE, not of any admissible set.
    #
    #  `declared_admissible_cells` is the same product with that rung removed:
    #  s25_denominator.py builds it as learner x split x quality_level x
    #  ADMISSIBLE rung from the declared axis levels it writes to
    #  s25_axis_levels.csv, which is the file Table~\ref{tab:axes} and
    #  Table~\ref{tab:denominator} are generated from.  It is READ from the
    #  audit file the numerator comes from rather than multiplied out again
    #  here, so the two shares cannot drift apart; and the audit's own
    #  `missing' column certifies that the declared count is the observed one,
    #  which is what makes a declared denominator legitimate under an observed
    #  numerator.
    #
    #  Both ratios are invariant to the instrument axis, because numerator and
    #  denominator alike expand by the scalar instruments: on the median pair
    #  36/288 = 180/1,440 = 12.5% and 36/216 = 180/1,080 = 16.7%.
    if AUD is not None and len(AUD) and G20 is not None and len(G20):
        sh = (AUD.inference_cells_observed
              / AUD.computational_cells.replace(0, np.nan))
        put("inferenceShareMedianPct", pct(float(sh.median()), 1))
        if "declared_admissible_cells" in AUD.columns:
            adm = (AUD.inference_cells_observed
                   / AUD.declared_admissible_cells.replace(0, np.nan))
            put("inferenceShareAdmissibleMedianPct",
                pct(float(adm.median()), 1))
        else:
            put("inferenceShareAdmissibleMedianPct", None)
    else:
        put("inferenceShareMedianPct", None)
        put("inferenceShareAdmissibleMedianPct", None)

    #  ROUND TWENTY-EIGHT.  The critical value the article quotes is the
    #  OPERATIVE one -- whichever estimator s21 was run with -- and the two
    #  estimators are quoted by name beside it.  `q_op_median' is absent from
    #  a bands run older than this round, in which case the operative value
    #  is the multiplier's, as it was then.
    _qop = first(F21, "q_op_median") if F21 is not None and "q_op_median" in F21.columns else None
    put("maxTSurfaceMedian", num(_qop if _qop is not None else first(F21, "q_median"), 2))
    put("maxTSurfaceMultMedian", num(first(F21, "q_median"), 2))
    put("maxTSurfaceEmpMedian", num(first(F21, "q_emp_median"), 2))
    put("bandOperative", str(first(F21, "operative"))
        if F21 is not None and "operative" in F21.columns else "mult")
    #  the operative value's range, from the critical-value file, which
    #  carries `q_op' per family since round twenty-eight
    _qc = load("s48w_critical.csv")
    if _qc is not None and "q_op" in _qc.columns:
        _qw = _qc[_qc.family == "whole-surface"].q_op
        put("maxTSurfaceMin", num(float(_qw.min()), 2))
        put("maxTSurfaceMax", num(float(_qw.max()), 2))
    else:
        put("maxTSurfaceMin", num(first(F21, "q_min"), 2))
        put("maxTSurfaceMax", num(first(F21, "q_max"), 2))
    put("maxTWithinMedian", num(first(F21, "q_within_instrument_median"), 2))
    put("familySizeMedian", thousands(first(F21, "family_size_median")))
    put("nRegionChangedByFamily",
        thousands(first(F21, "n_region_changed_by_family")))
    put("nRegionChangedByMC", thousands(first(F21, "n_region_changed_by_mc")))
    put("nResolvedWhole", thousands(first(F21, "n_resolved_whole")))
    put("nResolvedWithin", thousands(first(F21, "n_resolved_within")))
    put("resolutionLostPct", pct(first(F21, "share_resolution_lost")))
    put("nMultiplier", thousands(first(F21, "n_mult")))
    put("qEmpWidth", num(first(F21, "q_emp_width_median"), 2))
    put("qMultWidth", num(first(F21, "q_mult_width_median"), 3))
    put("dcaQ", num(first(F21, "q_dc_median"), 2))
    #  Families whose bands rest on fewer complete replicates than the draw
    #  count declares.  A bootstrap replicate is dropped from a family when a
    #  resample leaves some cell of it without outcome variation, which
    #  happens on the smallest logs.  The count and the worst shortfall are
    #  reported in Section 4.4 rather than left in a file, because a band
    #  built from 33 of 40 draws is a band with a noisier standard error and
    #  a reader is entitled to know which.
    #  ROUND TWENTY-SEVEN.  A fixed filename again: this read the RETIRED
    #  surface's incomplete-family file and reported a band built from 33 of
    #  40 draws.  On the reported surface no family is incomplete -- the
    #  weighted scheme cannot drop an arm -- so the file is empty and these
    #  two macros should be ABSENT rather than carry a retired surface's
    #  worst case.  `nIncompleteFamilies' is zero and says so.
    INC21 = load("s48w_incomplete.csv")
    put("nIncompleteFamilies", thousands(first(F21, "n_incomplete_families")))
    if INC21 is not None and len(INC21) and "n_draws_complete" in INC21.columns:
        share = (INC21.n_draws_complete / INC21.n_draws_declared).min()
        put("minDrawSharePct", pct(float(share), 0))
        put("minDrawsComplete", thousands(int(INC21.n_draws_complete.min())))
    #  and if the file is empty NOTHING IS EMITTED, because the ?? marker
    #  means "this number should exist and the analysis did not produce it",
    #  which is the opposite of the truth here: no family is incomplete, so
    #  the worst incomplete family does not exist to be reported.

    if R21 is not None and len(R21):
        put("nUniformlyBeneficial",
            thousands(int((R21.region == "uniformly beneficial").sum())))
        put("nCondBeneficial",
            thousands(int((R21.region == "conditionally beneficial").sum())))
        put("nCondHarmful",
            thousands(int((R21.region == "conditionally harmful").sum())))
        put("nUniformlyHarmful",
            thousands(int((R21.region == "uniformly harmful").sum())))
        put("nSignChanging",
            thousands(int((R21.region == "sign-changing").sum())))
        put("nUnresolvedPairs",
            thousands(int((R21.region == "unresolved").sum())))
        put("rhoMedian", num(float(R21.rho.median()), 3))
        put("rhoMin", num(float(R21.rho.min()), 3))
        put("rhoMax", num(float(R21.rho.max()), 3))
        put("nPairsBanded", thousands(len(R21)))

    #  Where THIS CORPUS sits on the ratio the simulation's grid varies.
    #  A coverage result about K/n is only useful beside the K/n the paper's
    #  own pairs have, and on this corpus the median is not small.
    SUR0 = load("s01_surface.csv")
    if SUR0 is not None and len(SUR0) and {"n", "n_test", "card_f"} <= set(SUR0.columns):
        per = SUR0.groupby(["log", "target"])[["n", "n_test", "card_f"]].first()
        ratio = (per.card_f / (per.n - per.n_test)).sort_values()
        put("corpusRatioMedian", num(float(ratio.median()), 3))
        put("corpusRatioMax", num(float(ratio.max()), 3))
        put("corpusRatioMin", num(float(ratio.min()), 3))
        put("nPairsRatioAboveTenth",
            thousands(int((ratio > 0.10).sum())))
        if ("BPIC14", "handover") in ratio.index:
            put("caseRatio", num(float(ratio.loc[("BPIC14", "handover")]), 3))
        else:
            put("caseRatio", None)
    else:
        for k in ("corpusRatioMedian", "corpusRatioMax", "corpusRatioMin",
                  "nPairsRatioAboveTenth", "caseRatio"):
            put(k, None)

    # ================================================================
    # s22 -- the corrected decomposition
    # ================================================================
    F22 = load("s22_facts.csv")
    M22 = load("s22_measures.csv")
    I22 = load("s22_indices.csv")
    put("nDecompositions", thousands(first(F22, "n_decompositions")))
    put("nAnovaComponents", thousands(first(F22, "n_components")))
    put("interactionTotalPct", pct(first(F22, "interaction_total_median")))
    put("interactionMinPct", pct(first(F22, "interaction_total_min")))
    put("interactionMaxPct", pct(first(F22, "interaction_total_max")))
    lo, hi = first(F22, "interaction_total_lo"), first(F22, "interaction_total_hi")
    put("interactionTotalCI",
        (r"95\%\ interval " + mn.pct(lo) + " to " + mn.pct(hi))
        if (lo is not None and hi is not None
            and np.isfinite(lo) and np.isfinite(hi)) else None)
    put("largestInvolvementPct", pct(first(F22, "largest_involvement_median")))
    put("largestFirstOrderPct", pct(first(F22, "largest_first_order_median")))
    #  The spread across the THREE PRODUCT MEASURES, which are corpus
    #  medians computed the same way.  s22's own `measure_spread` takes the
    #  range over all four rows of the measures table, and the fourth is the
    #  Dirichlet envelope -- computed on the primary pair alone, not on the
    #  corpus.  A range that mixes a corpus median with a single-pair value
    #  is not a range of anything, and it made the number 37.9 points where
    #  the comparable one is 29.2.  The envelope is reported beside them with
    #  its own label instead.
    if M22 is not None and len(M22):
        prod = M22[M22.measure != "envelope"]
        if len(prod):
            put("measureSpreadPct",
                pct(float(prod.interaction_total_median.max()
                          - prod.interaction_total_median.min())))
        env = M22[M22.measure == "envelope"]
        put("interactionEnvelopePct",
            pct(float(env.interaction_total_median.iloc[0]))
            if len(env) else None)
    else:
        put("measureSpreadPct", None)
        put("interactionEnvelopePct", None)
    put("topIndexPct", pct(first(F22, "top_index")))
    AXLAB = {"learner": "the learner", "split": "the split",
             "quality_level": "the register-quality condition",
             "rung": "the baseline rung", "metric": "the metric"}
    ax = first(F22, "top_axis")
    put("topIndexAxis", AXLAB.get(str(ax), str(ax)) if ax is not None else None)
    put("topIndexPair", str(first(F22, "top_pair"))
        if first(F22, "top_pair") is not None else None)
    put("nAxesLeading", thousands(first(F22, "n_axes_leading")))
    a2 = first(F22, "modal_leading_axis")
    put("modalLeadingAxis",
        AXLAB.get(str(a2), str(a2)) if a2 is not None else None)
    put("modalLeadingSharePct", pct(first(F22, "modal_leading_share"), 0))
    put("concentratedFirstOrderPct", pct(first(F22, "concentrated_first_order")))
    put("nConcentratedExceeds", thousands(first(F22, "concentrated_exceeds")))
    put("nEqualExceeds", thousands(first(F22, "equal_exceeds")))
    for ax, nm in (("learner", "sLearnerPct"), ("split", "sSplitPct"),
                   ("quality_level", "sQualityPct"), ("rung", "sRungPct")):
        put(nm, pct(first(F22, "S_%s_median" % ax)))
    for ax, nm in (("learner", "shLearnerPct"), ("split", "shSplitPct"),
                   ("quality_level", "shQualityPct"), ("rung", "shRungPct"),
                   ("metric", "shMetricPct")):
        put(nm, pct(first(F22, "Sh_%s_median" % ax)))
    if M22 is not None and len(M22):
        for meas, nm in (("reference", "interactionTotalReferencePct"),
                         ("concentrated", "interactionTotalConcentratedPct"),
                         ("envelope", "interactionTotalEnvelopePct")):
            r = M22[M22.measure == meas]
            put(nm, pct(float(r.interaction_total_median.iloc[0]))
                if len(r) else None)
    INV = load("s22_invariance.csv")
    if INV is not None and len(INV):
        d = INV[INV.test == "duplicate-level"]
        put("invarianceDuplicateShift",
            mn.sci(float(d.max_abs_change.max())) if len(d) else None)
        g = INV[INV.axis == "threshold:delta"]
        put("invarianceGridShift",
            num(float(g.max_abs_change.iloc[0]), 3) if len(g) else None)
        put("nInvariancePassed", thousands(int(INV.passed.sum())))
        put("nInvarianceTests", thousands(len(INV)))
    else:
        for k in ("invarianceDuplicateShift", "invarianceGridShift",
                  "nInvariancePassed", "nInvarianceTests"):
            put(k, None)

    # ================================================================
    # s23 -- regret on a coherent scale
    # ================================================================
    F23 = load("s23_facts.csv")
    put("excessOneNumberAuc", num(first(F23, "mean_excess_one_number_auc"), 4))
    put("excessMajorityAuc", num(first(F23, "mean_excess_majority_auc"), 4))
    put("nBadOneNumberAuc", thousands(first(F23, "n_bad_one_number_auc")))
    put("nBadMajorityAuc", thousands(first(F23, "n_bad_majority_auc")))
    put("nBadUniformAuc", thousands(first(F23, "n_bad_uniform_auc")))
    D23 = load("s23_metric_regret.csv")
    if D23 is not None and len(D23):
        g = D23[(D23.measure == "equal-level") & (D23.metric == "auc")
                & (D23.rule == "uniform-beneficial")]
        put("excessUniformAuc", num(float(g.excess.mean()), 4) if len(g) else None)
        #  HOW MANY instruments a cross-instrument DIRECTION claim actually
        #  holds in.  The manuscript said "the same in all five" of two
        #  orderings; neither was.  A claim about five instruments is a
        #  count, so it is one, and the exception is named by the macro
        #  beside it rather than by a sentence somebody has to keep true.
        t = (D23[D23.measure == "equal-level"]
             .groupby(["metric", "rule"]).excess.mean().unstack())
        if {"uniform-beneficial", "one-number"} <= set(t.columns):
            worst = t.idxmax(axis=1)
            n_u = int((worst == "uniform-beneficial").sum())
            put("nInstrumentsUniformWorst", thousands(n_u))
            put("nInstruments", thousands(len(t)))
            other = sorted(worst[worst != "uniform-beneficial"].index)
            put("instrumentsUniformNotWorst",
                ", ".join(_LABEL.get(m, m) for m in other))
    else:
        put("excessUniformAuc", None)
        for k in ("nInstrumentsUniformWorst", "nInstruments",
                  "instrumentsUniformNotWorst"):
            put(k, None)
    #  and the same for the OUT-OF-SAMPLE three-way ordering
    H23 = load("s23_heldout.csv")
    if H23 is not None and len(H23):
        hh = (H23[H23.design == "held-out cells"]
              .groupby(["metric", "rule"]).excess.mean().unstack())
        need = {"one-number", "majority", "weighted-mean"}
        if need <= set(hh.columns):
            ok = ((hh["one-number"] > hh["majority"])
                  & (hh["majority"] >= hh["weighted-mean"]))
            put("nInstrumentsOosOrdering", thousands(int(ok.sum())))
            bad = sorted(ok[~ok].index)
            put("instrumentsOosOrderingFails",
                ", ".join(_LABEL.get(m, m) for m in bad) if bad else "none")
            #  the part that DOES hold everywhere
            put("nInstrumentsOneNumberWorse",
                thousands(int((hh["one-number"] > hh["majority"]).sum())))
    else:
        for k in ("nInstrumentsOosOrdering", "instrumentsOosOrderingFails",
                  "nInstrumentsOneNumberWorse"):
            put(k, None)
    #  FIVE decimals, not four.  The weighted-mean rule's excess regret is
    #  exactly zero IN sample, by the lemma, and small but NOT zero out of it
    #  -- which is the whole reason the rules are evaluated out of sample.
    #  Four decimals round it to 0.0000 and print the in-sample identity as
    #  though it survived, which is the opposite of what the section argues.
    put("oosOneNumberAuc", num(first(F23, "oos_one_number_auc"), 5))
    put("oosMajorityAuc", num(first(F23, "oos_majority_auc"), 5))
    put("oosMeanAuc", num(first(F23, "oos_mean_auc"), 5))
    put("oostOneNumber", num(first(F23, "oost_one_number"), 5))
    put("oostMajority", num(first(F23, "oost_majority"), 5))
    put("oostMean", num(first(F23, "oost_weighted_mean"), 4))
    put("leaveOneOutAgreePct", pct(first(F23, "leaveoneout_agree"), 0))
    put("nLeaveOneOut", thousands(first(F23, "leaveoneout_n")))
    put("identityMaxExcess", mn.sci(first(F23, "identity_max_abs_excess")))
    put("nMapsInvariant", thousands(first(F23, "n_maps_invariant")))
    put("nbExcessOneNumber", num(first(F23, "nb_excess_one_number"), 5))
    put("nbExcessMajority", num(first(F23, "nb_excess_majority"), 5))
    put("nbExcessMean", num(first(F23, "nb_excess_weighted_mean"), 5))
    put("nbExcessUniform", num(first(F23, "nb_excess_uniform_beneficial"), 5))
    put("misreportEqualPct", pct(first(F23, "misreport_equal")))
    put("misreportReferencePct", pct(first(F23, "misreport_reference")))
    put("misreportConcentratedPct", pct(first(F23, "misreport_concentrated")))
    put("misreportMeasureSpreadPct", pct(first(F23, "misreport_measure_spread")))

    # ================================================================
    # s24 -- the planned contrasts
    # ================================================================
    F24 = load("s24_facts.csv")
    put("nDrawsPlanned", thousands(first(F24, "n_independent_draws")))
    put("pMinAttainableRaw", num(first(F24, "p_min_attainable_raw"), 5))
    put("pMinAttainableHolm", num(first(F24, "p_min_attainable_holm"), 5))
    put("nPlannedReject", thousands(first(F24, "n_reject")))
    put("pPlannedMin", num(first(F24, "p_holm_min"), 5))
    put("nPlannedContrasts", thousands(first(F24, "n_contrasts")))

    # ================================================================
    # s26 -- calibration and the decision curve
    # ================================================================
    F26 = load("s26_facts.csv")
    CAL26 = load("s26_calibration.csv")
    put("slopeRawMedian", num(first(F26, "slope_raw_median"), 2))
    put("slopeIsoMedian", num(first(F26, "slope_iso_median"), 2))
    put("slopePlattMedian", num(first(F26, "slope_platt_median"), 2))
    put("eceRawMedian", num(first(F26, "ece_raw_median"), 3))
    put("eceIsoMedian", num(first(F26, "ece_iso_median"), 3))
    put("nSlopeOutRaw", thousands(first(F26, "n_raw_slope_outside_half_two")))
    put("nSlopeOutIso", thousands(first(F26, "n_iso_slope_outside_half_two")))
    put("dcaSignChangePct", pct(first(F26, "dca_sign_change_share")))
    put("nDcaFamily", thousands(first(F26, "dca_n_family")))
    put("dcaHarmfulPointwise", thousands(first(F26, "dca_harmful_pointwise")))
    put("dcaHarmfulSimultaneous",
        thousands(first(F26, "dca_harmful_simultaneous")))
    if CAL26 is not None and len(CAL26):
        r = CAL26[CAL26.calibration == "raw"]
        put("slopeWorstRaw", num(float(r.cal_slope.min()), 2) if len(r) else None)
    else:
        put("slopeWorstRaw", None)

    #  THE DECISION-CURVE MACROS MUST COME FROM THE CALIBRATED CURVES.
    #  make_numbers reads them from s17/s02, which are the round-nineteen
    #  bands: an uncalibrated score, and a family that is the thresholds at
    #  one cell rather than the whole net-benefit surface.  Section 8 now
    #  reads the calibrated curve with its own declared family, so these
    #  override the earlier definitions -- emit() runs last, so the override
    #  is the value the manuscript prints.
    B26 = load("s26_bands.csv")
    if B26 is not None and len(B26):
        b = B26[(B26.rung == "B_intake_g") & (B26.learner == "logit")]
        if not len(b):
            b = B26
        put("nDcGrid", thousands(len(b)))
        put("dcBandWidth", num(float((b.sim_hi - b.sim_lo).median()), 4))
        put("dcPointWidth", num(float((b.pt_hi - b.pt_lo).median()), 4))
        put("nBeneficialSimultaneous", thousands(int((b.sim_lo > 0).sum())))
        put("nBeneficialPointwise", thousands(int((b.pt_lo > 0).sum())))
        put("nHarmfulSimultaneous", thousands(int((b.sim_hi < 0).sum())))
        put("nHarmfulPointwise", thousands(int((b.pt_hi < 0).sum())))
        #  s26 names the critical value q_maxt; s21 names it q.  This reads
        #  whichever the file carries rather than assuming, because a
        #  KeyError here would surface as a missing macro at the end of a
        #  six-hour chain.
        qcol = "q_maxt" if "q_maxt" in b.columns else "q"
        put("dcaQ", num(float(b[qcol].iloc[0]), 2))
        put("nDcaFamily", thousands(int(b.n_family.iloc[0])))
        #  The threshold a reader looking at the figure would worry about:
        #  where the simultaneous band's LOWER edge reaches furthest below
        #  zero.  Not argmin of the increment itself -- on this curve the
        #  increment never goes below zero, and its minimum is a plateau of
        #  exact zeros at the low thresholds where both arms nominate
        #  everything, which is not what a reader sees.
        dip = b.loc[b.sim_lo.idxmin()] if "sim_lo" in b.columns else None
        put("dcaDipTheta", num(float(dip.threshold), 2)
            if dip is not None else None)
        put("dcaDipValue", num(float(dip.sim_lo), 4)
            if dip is not None else None)

    # ================================================================
    # s27 -- register quality
    # ================================================================
    F27 = load("s27_facts.csv")
    put("nQualitySeeds", thousands(first(F27, "n_seeds")))
    put("nQualityLevels", thousands(first(F27, "n_levels")))
    put("gridShiftMax", num(first(F27, "grid_shift_max"), 4))
    put("gridShiftMedian", num(first(F27, "grid_shift_median"), 4))
    put("seedSdMedian", num(first(F27, "seed_sd_median"), 4))
    put("seedSdMax", num(first(F27, "seed_sd_max"), 4))
    put("mechanismVsSamplingMedian",
        num(first(F27, "mechanism_vs_sampling_median"), 2))
    put("nQualityLeakChecked", thousands(first(F27, "leakage_checked")))
    put("nQualityLeakPassed", thousands(first(F27, "leakage_passed")))
    for mech in ("time", "content", "propensity", "mask_rare", "mask_common",
                 "mask_random", "corrupt", "duplicate"):
        put("integral" + "".join(w.capitalize() for w in mech.split("_")),
            sig(first(F27, "integral_" + mech)))

    # ================================================================
    # s29 -- the propositions
    # ================================================================
    F29 = load("s29_facts.csv")
    put("nInvarianceChecks", thousands(first(F29, "n_invariance_checks")))
    put("invarianceMaxShift", mn.sci(first(F29, "invariance_max_shift")))
    put("nCertificates", thousands(first(F29, "n_certificates")))
    put("nPsiFamilies", thousands(first(F29, "n_psis")))
    put("certificateMinShift", num(first(F29, "certificate_min_shift"), 3))
    put("certificateMaxShift", num(first(F29, "certificate_max_shift"), 3))
    put("widerMChangeAffine", num(first(F29, "wider_m_change_affine"), 3))
    put("widerRShiftAffine", mn.sci(first(F29, "wider_R_shift_affine")))
    put("widerRShiftNonAffine", num(first(F29, "wider_R_shift_nonaffine"), 3))
    #  Proposition 1's construction is regenerated here with parameters the
    #  script ASSERTS -- the two configurations must share R_AUC and separate
    #  R_AP -- so these override the round-nineteen values, which came from a
    #  file with no such assertion.  emit() runs after make_numbers' own puts,
    #  so the override is the last writer and there is still one of each
    #  number.
    P1 = load("s29_prop1.csv")
    if P1 is not None and len(P1) >= 2:
        put("propOneAucGap", mn.sci(first(F29, "prop1_auc_gap")))
        put("propOneApGap", num(first(F29, "prop1_ap_gap"), 3))
        put("nPropP", thousands(200))
        put("nPropN", thousands(600))
        put("propOneRho", thousands(3))
        put("propOneSweepAuc", mn.sci(first(F29, "prop1_auc_gap")))
        put("propOneSweepAp", num(first(F29, "prop1_ap_gap"), 3))
        r = P1.iloc[0]
        put("propOneRauc", num(float(r.R_auc), 3))
        put("propOneRapA", num(float(P1.R_ap.iloc[0]), 3))
        put("propOneRapB", num(float(P1.R_ap.iloc[1]), 3))

    # ================================================================
    # s30 -- the pilot's variance
    # ================================================================
    F30 = load("s30_facts.csv")
    put("auditWeightIn", num(first(F30, "weight_in"), 3))
    put("auditWeightOut", num(first(F30, "weight_out"), 3))
    put("auditDesignWidthPct", pct(first(F30, "design_width_median"), 0))
    put("auditBootWidthPct", pct(first(F30, "boot_width_median"), 0))
    put("auditWilsonWidthPct", pct(first(F30, "wilson_width_median"), 0))
    put("auditMaxGapPct",
        pct(max(first(F30, "max_lo_gap") or 0.0,
                first(F30, "max_hi_gap") or 0.0), 0)
        if first(F30, "max_lo_gap") is not None else None)
    put("nPilotBoot", thousands(first(F30, "n_boot")))
    put("nWilsonInsideDesign", thousands(first(F30, "n_wilson_inside_design")))

    # ================================================================
    # s10 -- Monte Carlo precision of the simulation, which the blueprint
    # asks for and which costs nothing to state from the replicate count
    # ================================================================
    F10 = load("s10_facts.csv")
    n_reps = first(F10, "n_reps")
    if n_reps and np.isfinite(n_reps) and n_reps > 0:
        se = float(np.sqrt(0.95 * 0.05 / float(n_reps)) * 100.0)
        put("simCoverageSE", num(se, 1))
        put("simCoverageHalfWidth", num(1.96 * se, 1))
    else:
        put("simCoverageSE", None)
        put("simCoverageHalfWidth", None)
    S10C = load("s10_coverage.csv")
    if S10C is not None and len(S10C) and "n" in S10C.columns:
        put("nSimRuns", thousands(int(S10C.n.sum())))

    # ================================================================
    # s31 -- the simulation at the size the method claim needs.
    #
    # This block OVERRIDES the coverage macros make_numbers defines from
    # s10 whenever s31 has run.  The override is deliberate and is the only
    # one in the build: the blueprint's P1.1 asks for at least a thousand
    # replicates per world, s10 ran two hundred, and reporting the smaller
    # run as the headline while the larger one sits in results/ would be a
    # choice nobody could defend.  s10's numbers remain in
    # results/s10_*.csv and Appendix H still reads them, because the
    # noisy-world diagnosis was made on that run.  scripts/verify_numbers.py
    # checks each of these against s31 when it exists and against s10 when
    # it does not, so the verifier never checks a macro against a file the
    # generator did not use.
    # ================================================================
    F31 = load("s31_facts.csv")
    C31 = load("s31_coverage.csv")
    if F31 is not None and len(F31):
        n_core = first(F31, "n_reps_core")
        put("nSimReps", thousands(n_core))
        if n_core and np.isfinite(n_core) and n_core > 0:
            se = float(np.sqrt(0.95 * 0.05 / float(n_core)) * 100.0)
            put("simCoverageSE", num(se, 1))
            put("simCoverageHalfWidth", num(1.96 * se, 1))
        put("coverageNaiveMedian", pct(first(F31, "cov_naive_pct_median")))
        put("coverageNaiveBasicMedian",
            pct(first(F31, "cov_naive_basic_median")))
        put("coverageNestedMedian", pct(first(F31, "cov_nested_pct_median")))
        put("coverageNestedMin", pct(first(F31, "cov_nested_pct_min")))
        put("coverageNestedBasicMedian",
            pct(first(F31, "cov_nested_basic_median")))
        put("coverageNestedBasicMin",
            pct(first(F31, "cov_nested_basic_min")))
        put("coverageNestedBcMedian", pct(first(F31, "cov_nested_bc_median")))
        put("coverageNestedBcMin", pct(first(F31, "cov_nested_bc_min")))
        put("coverageSparsePct", pct(first(F31, "cov_sparse_pct")))
        put("coverageSparseBasic", pct(first(F31, "cov_sparse_basic")))
        put("coverageSparseBc", pct(first(F31, "cov_sparse_bc")))
        #  the constructions and designs s10 did not carry
        put("coverageMofnMedian", pct(first(F31, "cov_mofn_median")))
        put("coverageSparseMofn", pct(first(F31, "cov_sparse_mofn")))
        put("nSimGridCells", thousands(first(F31, "n_grid_cells")))
        put("nSimBlockLengths", thousands(first(F31, "n_block_lengths")))
        put("coverageGridMin", pct(first(F31, "cov_grid_basic_min")))
        put("coverageGridMedian", pct(first(F31, "cov_grid_basic_median")))
        #  THE RESULT THE (n, K) GRID EXISTS TO PRODUCE.  Coverage of the
        #  reported interval is governed by the RATIO of register
        #  cardinality to training size, not by either alone, and it
        #  degrades sharply as that ratio grows.  These name the regime,
        #  because the review's pass condition is "near-nominal coverage, or
        #  the manuscript must clearly delimit the regimes in which it does
        #  not", and the second clause is the one this study meets.
        gr = (C31[(C31.experiment == "grid")
                  & (C31.estimand == "V_limit")
                  & (C31.interval == "nested_basic")]
              if C31 is not None and "experiment" in getattr(C31, "columns", [])
              else None)
        if gr is not None and len(gr):
            gr = gr.assign(ratio=gr.K / gr.n_train).sort_values("ratio")
            put("simGridRatioMin", num(float(gr.ratio.min()), 3))
            put("simGridRatioMax", num(float(gr.ratio.max()), 3))
            #  the largest ratio at which the interval still covers within
            #  five points of nominal, and the smallest at which it is below
            #  three quarters
            #  ROUND TWENTY-THREE.  `simGridCoverageSafe' was the minimum
            #  coverage among the cells that attain 0.90, and the manuscript
            #  read it as a guarantee over the whole range below
            #  `simGridRatioSafe' -- "it holds at or above 90.0% while K/n is
            #  at most 0.050".  That is an extremum over a SELECTED subset,
            #  and it is false as a statement about the range: the cells at
            #  or below that ratio cover as little as 0.887.  A referee
            #  checked the grid and found it.  The macros are now the honest
            #  range over every cell in the band, and the old pair is not
            #  emitted, so the sentence cannot be rebuilt from them.
            ok = gr[gr.coverage >= 0.90]
            put("simGridRatioSafe", num(float(ok.ratio.max()), 3)
                if len(ok) else None)
            below = (gr[gr.ratio <= float(ok.ratio.max())]
                     if len(ok) else gr.iloc[0:0])
            put("coverageGridSafeMin", pct(float(below.coverage.min()))
                if len(below) else None)
            put("coverageGridSafeMax", pct(float(below.coverage.max()))
                if len(below) else None)
            put("nPlaneGridReps", thousands(int(gr.n.median()))
                if "n" in gr.columns else None)
            bad = gr[gr.coverage < 0.75]
            put("simGridRatioBad", num(float(bad.ratio.min()), 3)
                if len(bad) else None)
            #  the WORST-COVERING cell, not the largest-ratio one: the two
            #  are different because n enters as well as K/n, and the number
            #  a reader needs is how bad it gets.
            worst = gr.loc[gr.coverage.idxmin()]
            put("simGridWorstRatio", num(float(worst.ratio), 3))
            put("simGridWorstCoverage", pct(float(worst.coverage)))
            put("simGridWorstK", thousands(int(worst.K)))
            put("simGridWorstN", thousands(int(worst.n_train)))
        else:
            for k in ("simGridRatioMin", "simGridRatioMax", "simGridRatioSafe",
                      "coverageGridSafeMin", "coverageGridSafeMax",
                      "nPlaneGridReps", "simGridRatioBad",
                      "simGridWorstRatio", "simGridWorstCoverage",
                      "simGridWorstK", "simGridWorstN"):
                put(k, None)
        put("coverageBlockMin", pct(first(F31, "cov_block_basic_min")))
        put("coverageBlockMax", pct(first(F31, "cov_block_basic_max")))
        #  The block experiment runs at its own replicate count and its own
        #  refit budget, so it has its own Monte Carlo resolution and must
        #  not be read against the core's.  And the quantity that matters is
        #  the spread WITHIN a world across the three lengths, not the range
        #  over both worlds, which is dominated by the difference between the
        #  worlds.
        blk = C31[(C31.experiment == "block")
                  & (C31.estimand == "V_limit")] if C31 is not None             and "experiment" in getattr(C31, "columns", []) else None
        if blk is not None and len(blk):
            bb = blk[blk.interval == "nested_basic"]
            if len(bb):
                spread = (bb.groupby("world").coverage.max()
                          - bb.groupby("world").coverage.min())
                put("coverageBlockSpreadMax", pct(float(spread.max()), 1))
                n_b = float(bb.n.median())
                put("simCoverageSEBlock",
                    num(float(np.sqrt(0.95 * 0.05 / n_b) * 100.0), 1)
                    if n_b > 0 else None)
                put("nRepsBlock", thousands(int(n_b)))
            wide = blk.pivot_table(index=["world", "block_mult"],
                                   columns="interval", values="coverage")
            if {"nested_basic", "nested_pct"} <= set(wide.columns):
                sp = wide.loc["sparse"] if "sparse" in                     wide.index.get_level_values(0) else None
                if sp is not None and len(sp):
                    gap = (sp["nested_basic"] - sp["nested_pct"]).min()
                    put("blockSparseGapMin", pct(float(gap), 1))
                else:
                    put("blockSparseGapMin", None)
        else:
            for k in ("coverageBlockSpreadMax", "simCoverageSEBlock",
                      "nRepsBlock", "blockSparseGapMin"):
                put(k, None)
        put("simKMax", thousands(first(F31, "k_max")))
        put("simNMax", thousands(first(F31, "n_max")))
    else:
        for k in ("coverageNaiveBasicMedian", "coverageNestedBcMin",
                  "coverageMofnMedian", "coverageSparseMofn",
                  "nSimGridCells", "nSimBlockLengths", "coverageGridMin",
                  "coverageGridMedian", "coverageBlockMin",
                  "coverageBlockMax", "simKMax", "simNMax"):
            put(k, None)
    if C31 is not None and len(C31):
        #  the rows the prose names by world rather than by summary.  The
        #  experiment is part of the key: the block experiment repeats the
        #  linear and sparse worlds at the same (K, n, multiplier) as the
        #  core, at a smaller budget, as its own control.
        if "experiment" in C31.columns:
            C31 = C31[C31.experiment == "core"]

        def c31(world, interval, estimand="V_limit", **eq):
            d = C31[(C31.world == world) & (C31.interval == interval)
                    & (C31.estimand == estimand)]
            for k, v in eq.items():
                d = d[d[k] == v]
            return float(d.coverage.iloc[0]) if len(d) else None

        put("coverageDriftOracle",
            pct(max([v for v in
                     (c31("drift", i, "V_oracle")
                      for i in ("naive_pct", "nested_pct", "nested_basic",
                                "nested_bc"))
                     if v is not None] or [float("nan")])))
        put("coverageNoisyAfter", pct(c31("noisy", "nested_basic")))
        put("nSimRuns", thousands(int(C31.n.sum())))
        #  "the fixed-model interval undercovers and the nested one does
        #  not" is a claim about SIX worlds, so it is a count.  What the
        #  1000-replicate run supports is the weaker and true statement: the
        #  nested basic interval covers at least as well as the fixed-model
        #  percentile one on every world.
        piv = (C31[C31.estimand == "V_limit"]
               .pivot_table(index="world", columns="interval",
                            values="coverage"))
        if {"nested_basic", "naive_pct"} <= set(piv.columns):
            ok = (piv["nested_basic"] >= piv["naive_pct"] - 1e-12)
            put("nWorldsNestedAtLeastNaive", thousands(int(ok.sum())))
            put("nWorldsSim", thousands(int(len(piv))))
        else:
            put("nWorldsNestedAtLeastNaive", None)
            put("nWorldsSim", None)
        if "nested_mofn" in piv.columns:
            mo = piv["nested_mofn"].dropna()
            bs = piv["nested_basic"].reindex(mo.index)
            put("nWorldsMofnBeatsBasic",
                thousands(int((mo > bs + 1e-12).sum())))
            put("nWorldsMofnPriced", thousands(int(len(mo))))
        else:
            put("nWorldsMofnBeatsBasic", None)
            put("nWorldsMofnPriced", None)

        orc = C31[C31.estimand == "V_oracle"]
        put("biasOracleMax", num(float(orc.bias.abs().max()), 4)
            if len(orc) else None)

    # ---- ITSM-like pairs, for the construct discussion -----------------
    SUR = mn.load("s01_surface.csv")
    if SUR is not None and len(SUR) and "domain" in SUR.columns:
        it = SUR[SUR.domain == "itsm"]
        put("nITSMPairs", thousands(int(it.groupby(["log", "target"]).ngroups)))
    else:
        put("nITSMPairs", None)

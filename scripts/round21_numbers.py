"""round21_numbers -- the macros and tables round twenty-one adds.

The review's twelve major comments produce quantities from seven new result
files (s32 to s38).  They are defined here rather than inside make_numbers.py
for the same reason round twenty's are: that file is long enough, and these
come from a disjoint set of sources.  `make_numbers.main` calls `emit` once,
so there is still one writer of the macro file and one of each number.

Every macro resolves to the visible `??' marker when its result file is
absent, which is what makes a partial build visibly partial.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

#: the five highlights, read from the submission file so the manuscript and
#: the file Elsevier collects cannot drift apart.
HIGHLIGHTS_FILE = "submission/highlights.txt"

#: how the reconciliation's factors are named in prose
_STEP = {"the case study as published": "as published",
         "the case study, tie-break declared": "tie-break declared",
         "then the other tie-break rule": "the other tie-break rule",
         "then the registered cohort": "the registered cohort",
         "then the registered target": "the registered target"}

_TAU = {"t0_first_touch_all": "$\\tau_0$ first touch, every call",
        "t1_first_touch_escalating": "$\\tau_1$ first touch, escalating calls",
        "t2_incident_creation": "$\\tau_2$ incident creation"}


def emit(mn):
    put, load, pct, num, sig, first = (mn.put, mn.load, mn.pct, mn.num,
                                       mn.sig, mn.first)
    thousands = mn.thousands

    # ================================================================
    # highlights, so the PDF prints the file Elsevier is given
    # ================================================================
    try:
        txt = (mn.SRC_ROOT / HIGHLIGHTS_FILE).read_text(encoding="utf-8")
        tail = txt.split("without the length prefixes --")[-1]
        items = [l.strip() for l in tail.splitlines() if l.strip()]

        #  The highlights file is PLAIN TEXT -- that is what Elsevier's field
        #  takes -- so a percent sign in it is a percent sign.  Dropping it
        #  into a macro unescaped makes it a LaTeX comment, which swallows
        #  the rest of the line including the macro's closing brace: the
        #  build died on a runaway argument the moment a highlight first
        #  quoted a rate.
        def _tex(s):
            for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"),
                         ("%", "\\%"), ("#", "\\#"), ("_", "\\_"),
                         ("{", "\\{"), ("}", "\\}"), ("$", "\\$")):
                s = s.replace(a, b)
            return s

        put("highlightsList",
            " ".join("\\item %s" % _tex(i) for i in items) if items
            else None)
        put("nHighlights", str(len(items)) if items else None)
        put("highlightMaxChars",
            str(max(len(i) for i in items)) if items else None)
    except Exception:  # noqa: BLE001
        put("highlightsList", None)
        put("nHighlights", None)
        put("highlightMaxChars", None)

    #  the model identifier behind the generative-AI declaration
    put("aiModelId", "claude-opus-5")
    put("aiModelDate", "2026-08-24")

    # ================================================================
    # the family-relative separation (Proposition 2, Remark 3)
    #
    # ROUND TWENTY-TWO.  The corollary claimed a non-rank-based instrument
    # whose reduction is invariant, and the witness is invariant only inside
    # the AFFINE family: this file's own s29_wider records shifts up to 0.64
    # outside it.  The proposition is now stated relative to a declared
    # family and these are the numbers that bound the separation.
    # ================================================================
    W29 = load("s29_wider.csv")
    if W29 is not None and len(W29):
        aff = W29[W29.is_affine]
        non = W29[~W29.is_affine]
        put("widerRShiftNonAffine",
            num(float(non.R_shift.max()), 3) if len(non) else None)
        put("widerRShiftNonAffineMedian",
            num(float(non.R_shift.median()), 3) if len(non) else None)
        put("nPsiFamiliesNonAffine",
            thousands(int(non.psi.nunique())) if len(non) else None)
        put("widerPsiWorst",
            str(non.loc[non.R_shift.idxmax(), "psi"]) if len(non) else None)
    else:
        for k in ("widerRShiftNonAffine", "widerRShiftNonAffineMedian",
                  "nPsiFamiliesNonAffine", "widerPsiWorst"):
            put(k, None)

    # ================================================================
    # s40 -- the critical value against the other estimate of itself
    #
    # ROUND TWENTY-TWO.  The multiplier quantile the bands use lies below the
    # whole order-statistic interval of the empirical quantile on most
    # families, in the anti-conservative direction.  Both counts are macros
    # so the manuscript reports how much of its resolution belongs to the
    # data and how much to the estimator.
    # ================================================================
    F40 = load("s40_facts.csv")
    put("nQbelowEmpWhole", thousands(first(F40, "n_below_whole")))
    put("nQbelowEmpDca", thousands(first(F40, "n_below_dca")))
    put("nFamiliesWhole", thousands(first(F40, "n_families_whole")))
    put("nFamiliesDca", thousands(first(F40, "n_families_dca")))
    put("qEmpWholeMedian", num(first(F40, "q_emp_whole_median"), 2))
    put("qDcaMedian", num(first(F40, "q_dca_median"), 2))
    put("qEmpDcaMedian", num(first(F40, "q_emp_dca_median"), 2))
    put("qRatioWholeMedian", num(first(F40, "ratio_whole_median"), 2))
    put("qRatioDcaMedian", num(first(F40, "ratio_dca_median"), 2))
    put("nResolvedWholeMult", thousands(first(F40, "resolved_whole_mult")))
    put("nResolvedWholeEmp", thousands(first(F40, "resolved_whole_emp")))
    put("nResolvedDcaMult", thousands(first(F40, "resolved_dca_mult")))
    put("nResolvedDcaEmp", thousands(first(F40, "resolved_dca_emp")))

    #  ROUND TWENTY-THREE.  The calibration plane is estimated at three
    #  training sizes and applied to a corpus whose training sizes span three
    #  orders of magnitude, in a paper that elsewhere shows K/n alone does
    #  not determine coverage.  A referee called this the single most
    #  important thing to fix.  The reach of the extrapolation is now a
    #  number the manuscript states where the factor is applied.
    C33 = load("s33_cells.csv")
    SUR33 = load("s01_surface.csv.gz")
    if (C33 is not None and len(C33) and SUR33 is not None and len(SUR33)
            and "n_train" in C33.columns):
        lo, hi = int(C33.n_train.min()), int(C33.n_train.max())
        per = (SUR33.groupby(["log", "target"])[["n", "n_test"]]
               .first().reset_index())
        per["n_train"] = per.n - per.n_test
        put("planeNtrainLo", thousands(lo))
        put("planeNtrainHi", thousands(hi))
        put("nPairsInsidePlaneN", thousands(int(
            ((per.n_train >= lo) & (per.n_train <= hi)).sum())))
        put("nPairsBelowPlaneN", thousands(int((per.n_train < lo).sum())))
        put("nPairsAbovePlaneN", thousands(int((per.n_train > hi).sum())))
        put("corpusNtrainLo", thousands(int(per.n_train.min())))
        put("corpusNtrainHi", thousands(int(per.n_train.max())))
    else:
        for k in ("planeNtrainLo", "planeNtrainHi", "nPairsInsidePlaneN",
                  "nPairsBelowPlaneN", "nPairsAbovePlaneN",
                  "corpusNtrainLo", "corpusNtrainHi"):
            put(k, None)

    #  ROUND TWENTY-TWO.  Two referees independently said the same thing
    #  about "no surface is uniformly beneficial": the label is unreachable
    #  by construction, because a cell with a negative POINT estimate can
    #  never be beneficial at any critical value and every pair has one.  The
    #  informative reading of the region column is how the pairs that resolve
    #  anything divide, so those counts are macros now.
    G33 = load("s33_regions.csv")
    if G33 is not None and len(G33):
        _any = G33[(G33.beneficial_cal + G33.harmful_cal) > 0]
        put("nPairsResolvingAny", thousands(int(len(_any))))
        put("nPairsResolveBothSigns", thousands(int(
            ((G33.beneficial_cal > 0) & (G33.harmful_cal > 0)).sum())))
    else:
        put("nPairsResolvingAny", None)
        put("nPairsResolveBothSigns", None)
    #  ROUND TWENTY-TWO.  The layer paragraph said the coarse layers are
    #  "close to free" and that knowing a case concerns a laptop "is worth
    #  little".  On the case study's own log the type layer alone is worth
    #  more than half the item's increment on one target and a third on the
    #  other.  The claim that survives is about the item's MARGINAL
    #  contribution over the coarse layers, so those are the macros.
    R34 = load("r34_layers.csv")
    if R34 is not None and len(R34):
        b = R34[R34.log == "BPIC14"]

        def _lay(target, level):
            s = b[(b.target == target) & (b.level == level)]
            return float(s.gain_over_b0.iloc[0]) if len(s) else None

        for tg, nm in (("handover", "Handover"), ("duration", "Duration")):
            put("layerType" + nm, sig(_lay(tg, "CI Type (aff)"), 3))
            put("layerSubtype" + nm, sig(_lay(tg, "CI Subtype (aff)"), 3))
            put("layerItem" + nm, sig(_lay(tg, "CI Name (aff)"), 3))
            s = b[(b.target == tg)
                  & (b.level == "CI Name (aff) marginal over CI Subtype (aff)")]
            put("layerItemMarginal" + nm,
                sig(float(s.gain_over_b0.iloc[0]), 3) if len(s) else None)
    else:
        for nm in ("Handover", "Duration"):
            for k in ("layerType", "layerSubtype", "layerItem",
                      "layerItemMarginal"):
                put(k + nm, None)

    B21 = load("s21_bands.csv.gz")
    if B21 is not None and len(B21):
        _w = B21[B21.family == "whole-surface"]
        _m = _w.groupby(["log", "target"]).V.min()
        put("nPairsWithNegativeCell", thousands(int((_m < 0).sum())))
    else:
        put("nPairsWithNegativeCell", None)

    # ================================================================
    # s32 -- the cohort reconciliation (M1)
    # ================================================================
    F32 = load("s32_facts.csv")
    C32 = load("s32_cells.csv")
    P32 = load("s32_path.csv")
    CF24 = load("s24_contrasts.csv")
    A32 = load("s32_anova.csv")
    T32 = load("s32_tiebreak.csv")
    put("nRegisteredCohort", thousands(first(F32, "n_registered")))
    put("nExtraCases", thousands(first(F32, "n_extra")))
    put("nTiedTimestamps", thousands(first(F32, "n_ties")))
    put("fieldAgreement", num(first(F32, "agree_g"), 3))
    put("VpublishedTauTwo", sig(first(F32, "v_published_case"), 4))
    put("VregisteredTauTwo", sig(first(F32, "v_pc3"), 5))
    put("shareTargetPct", pct(first(F32, "share_target")))
    put("shareCohortPct", pct(first(F32, "share_cohort")))
    put("shareCohortTargetPct", pct(first(F32, "share_interaction")))
    put("tiebreakRange", num(first(F32, "tiebreak_range"), 5))
    put("tiebreakSd", num(first(F32, "tiebreak_sd"), 5))
    put("nTiebreakDraws", thousands(first(F32, "n_tiebreak")))
    put("nTiebreakPositive", thousands(first(F32, "tiebreak_sign_positive")))
    put("nCohortCells", thousands(first(F32, "n_cells")))
    put("nCohortDraws", thousands(first(F32, "n_draws")))
    if C32 is not None and len(C32):
        h = C32[(C32.cohort == "registered") & (C32.target == "handover")]
        put("prevRegisteredHandover",
            num(float(h.prevalence.iloc[0]), 3) if len(h) else None)
        km = C32[C32.rung == "B_intake_g_km"]
        put("nCohortSignPositive", thousands(int((km.V > 0).sum())))
        put("nCohortResolved", thousands(int(km.resolved.sum())))
    else:
        for k in ("nCohortSignPositive", "nCohortResolved",
                  "prevRegisteredHandover"):
            put(k, None)

    #  ------------------------------------------------------------------
    #  PC3, and the run it is quoted from.  ROUND TWENTY-TWO.
    #
    #  A referee found the same contrast printed with two different
    #  intervals: the article gave [-0.00161, +0.01217] and Table S15 gave
    #  [-0.00059, +0.01210].  Both were right about their own file -- s32
    #  runs the cohort experiment at 400 draws and s24 runs the planned
    #  contrasts at 2,000 -- and the POINT ESTIMATE agrees to seven figures,
    #  so nothing was wrong with either number.  What was wrong is that the
    #  article's Section 4.4 quoted the 400-draw interval in the same
    #  paragraph as the 2,000-draw budget, beside a table printing the
    #  2,000-draw interval, under a supplement abstract promising that a
    #  quantity cannot differ between the two documents.
    #
    #  Every PC3 macro now comes from s24, which is the planned-contrast run
    #  and the one Table S15 prints, and `round21_verify` has an ESTIMANDS
    #  entry so the two can never diverge again.
    if CF24 is not None and len(CF24):
        r = CF24[CF24.contrast == "PC3"]
    else:
        r = None
    if r is not None and len(r):
        V = float(r.estimate.iloc[0])
        lo, hi = float(r.basic_lo.iloc[0]), float(r.basic_hi.iloc[0])
        put("pcThreePraw", num(float(r.p_raw.iloc[0]), 5))
        put("pcThreePholm", num(float(r.p_holm.iloc[0]), 5))
        put("pcThreeLo", sig(lo, 5))
        put("pcThreeHi", sig(hi, 5))
        put("nDrawsPcThree", thousands(int(r.n_draws.iloc[0])))
        #  the bootstrap quantiles the basic interval was pivoted from, which
        #  is what makes the one-sided p and the interval consistent rather
        #  than contradictory.  basic = (2V - q_hi, 2V - q_lo), so the
        #  quantiles are recoverable from the interval and the estimate and
        #  cannot be quoted from a different run.
        put("pcThreeQlo", sig(2 * V - hi, 5))
        put("pcThreeQhi", sig(2 * V - lo, 5))
        put("pcThreeShift", num(((2 * V - hi) + (2 * V - lo)) / 2.0 - V, 5))
    else:
        for k in ("pcThreePraw", "pcThreePholm", "pcThreeLo", "pcThreeHi",
                  "nDrawsPcThree", "pcThreeQlo", "pcThreeQhi",
                  "pcThreeShift"):
            put(k, None)
    if P32 is not None and len(P32):
        d = {r.step: r for r in P32.itertuples()}
        put("deltaTiebreak", sig(float(
            d["the case study, tie-break declared"].delta), 5))
        put("deltaCohortStep", sig(float(
            d["then the registered cohort"].delta), 5))
        put("deltaTargetStep", sig(float(
            d["then the registered target"].delta), 5))
    else:
        for k in ("deltaTiebreak", "deltaCohortStep", "deltaTargetStep"):
            put(k, None)

    # ================================================================
    # s33 -- the coverage-calibrated critical value (M3)
    # ================================================================
    F33 = load("s33_facts.csv")
    G33 = load("s33_regions.csv")
    put("nPlaneCells", thousands(first(F33, "n_cells")))
    put("nPlaneReps", thousands(first(F33, "n_reps")))
    put("planeKnMin", num(first(F33, "kn_min"), 4))
    put("planeKnMax", num(first(F33, "kn_max"), 3))
    put("calSlope", num(first(F33, "c_slope"), 3))
    put("calSlopeSe", num(first(F33, "c_slope_se"), 3))
    put("calIntercept", num(first(F33, "c_intercept"), 3))
    put("calAtMedianPair", num(first(F33, "c_at_median_pair"), 2))
    put("nRegionsChangedByCalibration",
        thousands(first(F33, "n_regions_changed")))
    put("rhoMedianCalibrated", num(first(F33, "rho_median_calibrated"), 3))
    put("nResolvedCellsNominal",
        thousands(first(F33, "n_resolved_cells_nominal")))
    put("nResolvedCellsCalibrated",
        thousands(first(F33, "n_resolved_cells_calibrated")))
    put("nUniformlyBeneficialCalibrated",
        thousands(first(F33, "n_uniformly_beneficial_calibrated")))
    put("nUnresolvedCalibrated",
        thousands(first(F33, "n_unresolved_calibrated")))
    #  M8: how much of the conclusion the calibration itself is carrying
    S33 = load("s33_sensitivity.csv")
    if S33 is not None and len(S33):
        s = S33.set_index("setting")
        for lab, key in (("nominal (c = 1)", "Nominal"),
                         ("calibrated", "Calibrated"),
                         ("calibrated, upper Monte Carlo end", "Upper")):
            if lab in s.index:
                put("nResolvedSens" + key,
                    thousands(int(s.loc[lab, "resolved"])))
                put("rhoSens" + key, num(float(s.loc[lab, "rho_median"]), 3))
                put("nUnifBenSens" + key,
                    thousands(int(s.loc[lab, "n_uniformly_beneficial"])))
    else:
        for key in ("Nominal", "Calibrated", "Upper"):
            for pre in ("nResolvedSens", "rhoSens", "nUnifBenSens"):
                put(pre + key, None)

    if G33 is not None and len(G33):
        put("calMin", num(float(G33.c.min()), 2))
        put("calMax", num(float(G33.c.max()), 2))
        put("qCalibratedMedian", num(float(G33.q_calibrated.median()), 2))
        #  the region counts UNDER THE CALIBRATED BAND, which are the ones the
        #  article quotes; the nominal ones keep round twenty's names
        vc = G33.region_calibrated.value_counts()
        for lab, nm in (("conditionally beneficial", "nCondBeneficialCal"),
                        ("conditionally harmful", "nCondHarmfulCal"),
                        ("sign-changing", "nSignChangingCal"),
                        ("uniformly harmful", "nUniformlyHarmfulCal"),
                        ("uniformly beneficial", "nUniformlyBeneficialCal")):
            put(nm, thousands(int(vc.get(lab, 0))))
        lost = 1.0 - (G33.beneficial_cal + G33.harmful_cal).sum() / max(
            1.0, float((G33.beneficial + G33.harmful).sum()))
        put("resolutionLostToCalibrationPct", pct(float(lost)))
    else:
        for k in ("calMin", "calMax", "qCalibratedMedian",
                  "resolutionLostToCalibrationPct", "nCondBeneficialCal",
                  "nCondHarmfulCal", "nSignChangingCal",
                  "nUniformlyHarmfulCal", "nUniformlyBeneficialCal"):
            put(k, None)

    #  the corpus-wide decision-curve counts, which existed and were not
    #  printed while the case study's were
    F26 = load("s26_facts.csv")
    put("nDcaRows", thousands(first(F26, "n_dca_rows")))
    put("dcaHarmfulPointwise", thousands(first(F26, "dca_harmful_pointwise")))
    put("dcaHarmfulSimultaneous",
        thousands(first(F26, "dca_harmful_simultaneous")))

    #  the tipping curve's seed count, which is smaller than the quality
    #  mechanisms' and was not stated
    S8T = load("s08_tipping.csv")
    put("nTippingSeeds",
        thousands(int(S8T.n_seeds.max())) if S8T is not None and len(S8T)
        else None)

    #  the logs downloaded as a held-out set and never offered to the
    #  admission rules.  The exclusion ledger now names them; this is the
    #  count the data-availability statement quotes.
    HO = load("r43_holdout.csv")
    put("nHeldOutLogs",
        thousands(int(HO.log.nunique())) if HO is not None and len(HO)
        else None)

    #  M9: how many rows of the layer table are on pairs the registered rules
    #  exclude.  The table drops them; this is the count it names.
    LY = load("r34_layers.csv")
    if LY is None:
        LY = load("e10b_layers.csv")
    SUR0 = load("s01_surface.csv")
    if LY is not None and len(LY) and SUR0 is not None and len(SUR0):
        adm = set(zip(SUR0.log.astype(str), SUR0.target.astype(str)))
        n_out = sum(1 for a, b in zip(LY.log, LY.target)
                    if (str(a), str(b)) not in adm)
        put("nLayerRowsExcluded", thousands(n_out))
    else:
        put("nLayerRowsExcluded", None)

    #  K/n per pair, computed from the surface by the same expression the
    #  denominator table prints, so the two cannot disagree
    SUR = load("s01_surface.csv")
    if SUR is not None and len(SUR):
        per = (SUR[["log", "target", "card_f", "n", "n_test"]]
               .groupby(["log", "target"]).first().reset_index())
        kn = (per.card_f / (per.n - per.n_test)).astype(float)
        put("medianKoverN", num(float(kn.median()), 3))
        put("maxKoverN", num(float(kn.max()), 3))
        put("nPairsAboveTenth", thousands(int((kn > 0.10).sum())))
        #  how many pairs carry only the two-level pipeline axis
        lv = SUR.groupby(["log", "target"]).learner.nunique()
        put("nPairsTwoLearners", thousands(int((lv <= 2).sum())))
        put("nPairsOther", thousands(int(lv.shape[0] - (lv > 2).sum())))
    else:
        for k in ("medianKoverN", "maxKoverN", "nPairsAboveTenth",
                  "nPairsTwoLearners", "nPairsOther"):
            put(k, None)

    # ================================================================
    # s34 -- what the sign-disagreement rate counts (M4, M10)
    # ================================================================
    F34 = load("s34_facts.csv")
    M34 = load("s34_misreport.csv")
    FAM = load("s34_family.csv")
    put("misreportPooledResolvedPct",
        pct(first(F34, "misreport_pooled_resolved")))
    put("misreportPooledResolvedNominalPct",
        pct(first(F34, "misreport_pooled_resolved_nominal")))
    put("nResolvedCorpus", thousands(first(F34, "n_resolved_total")))
    put("nDisagreeResolved", thousands(first(F34, "n_disagree_total")))
    #  ROUND TWENTY-THREE.  The headline is a POOLED ratio quoted at ONE of
    #  three critical values, with both of its own corrections applied
    #  separately and never together, over a denominator concentrated in
    #  three logs.  All four facts are macros now.
    put("misreportPooledResolvedLatitudePct",
        pct(first(F34, "misreport_pooled_resolved_latitude")))
    put("nResolvedLatitude", thousands(first(F34, "n_resolved_latitude_total")))
    put("nDisagreeLatitude",
        thousands(first(F34, "n_disagree_latitude_total")))
    put("nDisagreeTopThree", thousands(first(F34, "n_disagree_top_three")))
    put("nLogsDisagree", thousands(first(F34, "n_logs_disagree")))
    if M34 is not None and len(M34):
        _e = M34[M34.measure == "equal-level"]
        put("nResolvedMax", thousands(int(_e.n_resolved_calibrated.max())))
    else:
        put("nResolvedMax", None)
    #  ROUND TWENTY-THREE.  A rate under the EMPIRICAL band was drafted
    #  here and withdrawn: it needs the pair's reference cell, which is
    #  `s23.reference_value' and not the first row of a group, and the
    #  quick version got 4.7% where the correct one is near 11%.  The
    #  nominal comparison below is computed by s34 with the right
    #  reference and makes the same point; the empirical band's
    #  RESOLUTION count is in s40 and is quoted instead.  Do not put a
    #  rate back here without routing it through s34.
    put("nResolvedCorpusNominal",
        thousands(first(F34, "n_resolved_total_nominal")))
    put("misreportMagnitudePct", pct(first(F34, "misreport_magnitude_median")))
    put("nPairsNoResolvedDisagreement",
        thousands(first(F34, "n_pairs_no_resolved_disagreement")))
    put("nPairsSomeResolvedDisagreement",
        thousands(first(F34, "n_pairs_some_resolved_disagreement")))
    put("nPairsNoResolvedCell", thousands(first(F34, "n_pairs_no_resolved_cell")))
    put("nResolvedMedian", thousands(first(F34, "n_resolved_median")))
    #  the denominator the resolved count is out of is the INFERENCE surface's
    #  band family, not the declared surface: a cell resolves or not only
    #  where it carries a band.  Reading it out of the regions file rather
    #  than the misreport file is what keeps the two on the same basis.
    if G33 is not None and len(G33):
        put("nCellsPerPairMedian", thousands(float(G33.cells.median())))
    else:
        put("nCellsPerPairMedian", None)
    put("misreportItsmPct", pct(first(F34, "misreport_itsm_median")))
    #  ROUND TWENTY-TWO.  These three were defined from the round-nineteen
    #  s04 file, differ from the round-twenty-one ones on ten of nineteen
    #  pairs, and are used nowhere in the manuscript.  A dead macro carrying
    #  a superseded value, in a file whose whole purpose is provenance, is a
    #  hazard rather than a spare part: they are redefined here from the
    #  current file so that a future sentence that reaches for one gets the
    #  number the rest of the paper uses.
    if M34 is not None and len(M34):
        e = M34[M34.measure == "equal-level"]
        put("misreportMedianPct", pct(float(e.misreport_all.median())))
        put("misreportMaxPct", pct(float(e.misreport_all.max())))
        put("misreportMinPct", pct(float(e.misreport_all.min())))
        put("nMisreportOverTen",
            thousands(int((e.misreport_all > 0.10).sum())))
        put("nMisreportOverQuarter",
            thousands(int((e.misreport_all > 0.25).sum())))
    #  M4b: the rate over the axes an analyst actually chooses, and the
    #  partition of the variance into the three kinds of axis
    put("misreportLatitudePct", pct(first(F34, "misreport_latitude_median")))
    put("nCellsLatitude", thousands(first(F34, "n_cells_latitude")))
    #  ROUND TWENTY-FIVE.  These three are the partition taken on the
    #  PRIMARY scale, which decomposes INSIDE each instrument and takes the
    #  median across instruments -- so the instrument is a stratum and the
    #  latitude share below is the pipeline and the rung, NOT the pipeline,
    #  the rung and the instrument as three rounds of prose claimed.  The
    #  `Cross' trio is the same partition on the scale where the instrument
    #  is an axis, and the two order latitude and resampling oppositely,
    #  which is why both are printed wherever either is.
    put("shareLatitudePct", pct(first(F34, "share_latitude")))
    put("shareResamplingPct", pct(first(F34, "share_resampling")))
    put("shareCounterfactualPct", pct(first(F34, "share_counterfactual")))
    put("shareLatitudeCrossPct", pct(first(F34, "share_latitude_cross")))
    put("shareResamplingCrossPct", pct(first(F34, "share_resampling_cross")))
    put("shareCounterfactualCrossPct",
        pct(first(F34, "share_counterfactual_cross")))
    put("nPairsResamplingOverLatitude",
        thousands(first(F34, "n_pairs_resampling_over_latitude")))
    put("nPairsResamplingOverLatitudeCross",
        thousands(first(F34, "n_pairs_resampling_over_latitude_cross")))
    #  M5: the headline is LOWER on the population the paper is about
    put("misreportPooledItsmPct",
        pct(first(F34, "misreport_pooled_resolved_itsm")))
    put("misreportPooledOtherPct",
        pct(first(F34, "misreport_pooled_resolved_other")))
    put("misreportMagnitudeItsmPct",
        pct(first(F34, "misreport_magnitude_itsm_median")))
    put("nItsmPairs", thousands(first(F34, "n_itsm")))
    if FAM is not None and len(FAM):
        #  index by the COLUMN NAME rather than by itertuples' positional
        #  alias: `itsm 8' contains a space, so itertuples calls it `_4', and
        #  a positional alias moves the moment a column is added.
        f = FAM.set_index("statistic")

        def fam(stat, col, d=3, as_pct=False):
            if stat not in f.index or col not in f.columns:
                return None
            v = float(f.loc[stat, col])
            if not np.isfinite(v):
                return None
            return pct(v) if as_pct else num(v, d)

        put("itsmHigherOrderPct",
            fam("higher-order share", "itsm 8", as_pct=True))
        put("itsmSpread", fam("baseline spread (AUC)", "itsm 8"))
        put("itsmLargestFirstOrderPct",
            fam("largest first-order index", "itsm 8", as_pct=True))
        put("otherHigherOrderPct",
            fam("higher-order share", "other 11", as_pct=True))
        put("otherLargestFirstOrderPct",
            fam("largest first-order index", "other 11", as_pct=True))
    else:
        for k in ("itsmHigherOrderPct", "itsmSpread",
                  "itsmLargestFirstOrderPct", "otherHigherOrderPct",
                  "otherLargestFirstOrderPct"):
            put(k, None)

    # ================================================================
    # s35 -- the decision in units a desk uses (M5)
    # ================================================================
    F35 = load("s35_facts.csv")
    put("nModelsDca", thousands(first(F35, "n_models")))
    put("nModelsDcaAdmitted", thousands(first(F35, "n_models_admitted")))
    put("nModelsDcaExcluded", thousands(first(F35, "n_models_excluded")))
    put("nPairsDcaExcluded", thousands(first(F35, "n_pairs_fully_excluded")))
    put("slopeLo", num(first(F35, "slope_lo"), 1))
    put("slopeHi", num(first(F35, "slope_hi"), 1))
    put("deskQlo", num(first(F35, "desk_q05"), 2))
    put("deskQmid", num(first(F35, "desk_q50"), 2))
    put("deskQhi", num(first(F35, "desk_q95"), 2))
    put("nSeparatingDesk", thousands(first(F35, "n_separating_desk")))
    put("nOneNumberWorstDesk", thousands(first(F35, "n_one_number_worst_desk")))
    put("excessOneNumberDesk", num(first(F35, "excess_one_number_desk"), 3))
    put("excessUniformDesk", num(first(F35, "excess_uniform_desk"), 3))
    put("maxExcessOneNumberDesk",
        num(first(F35, "max_excess_one_number_desk"), 3))
    put("promisedPerThousand", num(first(F35, "promised_per_1000"), 2))
    put("deliveredPerThousand", num(first(F35, "delivered_per_1000"), 3))
    put("shortfallPerThousand", num(first(F35, "shortfall_per_1000"), 2))

    # ================================================================
    # s36 -- against specification-curve analysis (M6)
    # ================================================================
    F36 = load("s36_facts.csv")
    V36 = load("s36_verdicts.csv")
    put("nScaPairs", thousands(first(F36, "n_pairs")))
    put("nScaPerms", thousands(first(F36, "n_perms")))
    put("nScaCells", thousands(first(F36, "n_cells")))
    #  ROUND TWENTY-TWO.  The second declared budget for this experiment: a
    #  permutation replicate refits every cell, so the cases each fit sees
    #  are capped as well as the cells.  Both numbers are in the manuscript.
    put("nScaMaxCases", thousands(first(F36, "n_max_cases")))
    put("nScaCapped", thousands(first(F36, "n_capped")))
    put("nScaNonNull", thousands(first(F36, "n_sca_nonnull")))
    put("nScaSignVaries", thousands(first(F36, "n_sign_varies")))
    put("nScaDisagree", thousands(first(F36, "n_disagree")))
    put("nScaAgreeNull", thousands(first(F36, "n_agree_null")))
    put("nScaSubSurfaceDisagree",
        thousands(first(F36, "n_sub_surface_disagree")))
    put("scaPmax", num(first(F36, "p_median_max"), 3))
    put("scaPmin", num(first(F36, "p_median_min"), 3))
    if V36 is not None and len(V36):
        dis = V36[(V36.p_median <= 0.05) & V36.sub_surface_sign_varies]
        put("rhoScaDisagree", num(float(dis.rho_full_surface.iloc[0]), 3)
            if len(dis) else None)
        put("scaDisagreePair", "%s/%s" % (dis.log.iloc[0], dis.target.iloc[0])
            if len(dis) else None)
    else:
        put("rhoScaDisagree", None)
        put("scaDisagreePair", None)

    # ================================================================
    # s37 -- learner and encoding, crossed (M7)
    # ================================================================
    F37 = load("s37_facts.csv")
    put("nPipelines", thousands(first(F37, "n_pipelines")))
    put("sFamilyPct", pct(first(F37, "share_family")))
    put("sEncodingPct", pct(first(F37, "share_encoding")))
    put("sFamilyEncodingPct", pct(first(F37, "share_family_x_encoding")))
    put("crossedHigherOrderPct", pct(first(F37, "higher_order_share")))
    v = F37.larger_axis.iloc[0] if (F37 is not None and len(F37)) else None
    put("largerPipelineAxis", v)

    # ================================================================
    # s39 -- the case study's quality and absorption, on ITS OWN cohort
    #
    # These OVERRIDE the corpus-cohort values that round twenty defined under
    # the same names, because Section 7 is a section about the estate's own
    # cohort and reassignment target and every number in it must be that.
    # The corpus versions keep their own names and are printed in the
    # supplement beside the rest of the corpus.
    # ================================================================
    F39 = load("s39_facts.csv")
    Q39 = load("s39_quality.csv")
    A39 = load("s39_absorption.csv")
    if F39 is not None and len(F39):
        for old in ("qClean", "qRareHalf", "qCommonHalf", "qRandomHalf",
                    "qCorruptThirty", "qDuplicateAll", "qStaleDelta",
                    "qLagHalfDelta", "Dabs", "DabsLo", "DabsHi", "Rref",
                    "RrefKind"):
            #  keep the corpus value under a name of its own before it is
            #  overwritten, so the supplement can print both
            if old in mn._MACROS:
                mn._MACROS[old + "Corpus"] = mn._MACROS[old]
        #  LEVELS and DELTAS are different quantities and the manuscript
        #  reads some of each.  A macro whose name does not end in `Delta'
        #  holds the increment ITSELF under that mechanism; one that does
        #  holds the change from the clean field.  Mixing them is how a
        #  sentence comes to say `moves by +0.07' when it means `is +0.07'.
        clean = first(F39, "V_clean")
        put("qClean", sig(clean, 4))
        put("qRareHalf", sig(first(F39, "V_rare_half"), 4))
        put("qCommonHalf", sig(first(F39, "V_common_half"), 4))
        put("qRandomHalf", sig(first(F39, "V_random_half"), 4))
        put("qCorruptThirty", sig(first(F39, "V_corrupt_thirty"), 4))
        put("qCorruptThirtyDelta",
            sig(first(F39, "V_corrupt_thirty") - clean, 4))
        put("qRareHalfDelta", sig(first(F39, "V_rare_half") - clean, 4))
        put("qCommonHalfDelta", sig(first(F39, "V_common_half") - clean, 4))
        put("qDuplicateAll", sig(first(F39, "V_duplicate_all"), 4))
        put("qDuplicateAllDelta",
            sig(first(F39, "V_duplicate_all") - clean, 4))
        put("qStaleDelta", sig(first(F39, "V_stale") - clean, 4))
        put("qLagHalfDelta", sig(first(F39, "V_lag_half") - clean, 4))
        put("Dabs", sig(first(F39, "D_ref"), 4))
        put("DabsLo", sig(first(F39, "D_ref_lo"), 4))
        put("DabsHi", sig(first(F39, "D_ref_hi"), 4))
        put("Rref", num(first(F39, "R_ref"), 3))
        v = F39.R_ref_kind.iloc[0]
        put("RrefKind", str(v) if isinstance(v, str) else None)
        put("nFiellerCase", thousands(first(F39, "n_fieller")))
        put("nFiellerUnboundedCase",
            thousands(first(F39, "n_fieller_unbounded")))
        put("nCaseQualityPoints", thousands(first(F39, "n_quality_points")))
        put("nCaseSweepLevels", thousands(first(F39, "n_sweep_levels")))
    else:
        #  a macro whose source is absent must still EXIST, or the build dies
        #  on an undefined control sequence instead of printing the visible
        #  `??' marker that makes a partial build visibly partial
        for k in ("nFiellerCase", "nFiellerUnboundedCase",
                  "nCaseQualityPoints", "nCaseSweepLevels"):
            put(k, None)
    if Q39 is not None and len(Q39):
        q = Q39.set_index(["mechanism", "level"])
        try:
            put("qLagHalfPopulated",
                pct(float(q.loc[("stale_lag", 0.50), "populated"])))
        except Exception:  # noqa: BLE001
            pass
    I39 = load("s39_integrals.csv")
    if I39 is not None and len(I39):
        g = I39.set_index("mechanism").integral
        for k, nm in (("time", "integralTime"), ("content", "integralContent"),
                      ("propensity", "integralPropensity"),
                      ("mask_rare", "integralMaskRare")):
            if k in g.index:
                put(nm, sig(float(g.loc[k]), 4))
        put("gridShiftMaxCase", num(float(I39.grid_shift.max()), 4))
        put("seedSdMedianCase", num(float(I39.seed_sd_median.median()), 4))
    else:
        for k in ("gridShiftMaxCase", "seedSdMedianCase"):
            put(k, None)

    # ================================================================
    # s38 -- the decision time as an axis (M2)
    # ================================================================
    F38 = load("s38_facts.csv")
    put("nTauDraws", thousands(first(F38, "n_draws")))
    put("nDecisionTimes", thousands(first(F38, "n_decision_times")))
    put("nTauZero", thousands(first(F38, "n_t0")))
    put("nTauOne", thousands(first(F38, "n_t1")))
    put("nTauTwo", thousands(first(F38, "n_t2")))
    put("prevTauZero", num(first(F38, "prev_t0"), 3))
    put("prevTauTwo", num(first(F38, "prev_t2"), 3))
    put("cardTauZero", thousands(first(F38, "card_t0")))
    put("VtauZero", sig(first(F38, "V_t0_intake"), 4))
    put("VtauOne", sig(first(F38, "V_t1_intake"), 4))
    put("VtauTwo", sig(first(F38, "V_t2_intake"), 4))
    put("deltaCohortAtTau", sig(first(F38, "delta_cohort"), 4))
    #  ROUND TWENTY-TWO.  `delta_snapshot' was V(T2) - V(T1) across two
    #  populations that differ by 942 cases, and the manuscript called it
    #  "the same cases, changing what is known but not who is in scope".  It
    #  is now the step on the MATCHED population -- the information change
    #  with the population held fixed -- and the residual the 942 unmatched
    #  incidents are worth is a macro of its own rather than folded into it.
    #  The information step was overstated by three quarters.
    put("deltaSnapshotAtTau", sig(first(F38, "delta_snapshot"), 4))
    put("deltaPopulationResidual",
        sig(first(F38, "delta_population_residual"), 4))
    put("deltaSnapshotUnmatched",
        sig(first(F38, "delta_snapshot_unmatched"), 4))
    put("nTauTwoMatched", thousands(first(F38, "n_t2_matched")))
    put("nTauTwoUnmatched", thousands(first(F38, "n_t2_unmatched")))
    put("prevTauOne", num(first(F38, "prev_t1"), 3))
    put("VtauTwoMatched", sig(first(F38, "V_t2_matched_intake"), 4))
    put("VtauTwoKnowledge", sig(first(F38, "V_t2_knowledge"), 4))
    L38 = load("s38_ladder.csv")
    if L38 is not None and len(L38):
        r = L38[(L38.decision_time == "t0_first_touch_all")
                & (L38.rung == "B_intake")]
        put("VtauZeroLo", sig(float(r.lo.iloc[0]), 4) if len(r) else None)
        put("VtauZeroHi", sig(float(r.hi.iloc[0]), 4) if len(r) else None)
        r2 = L38[(L38.decision_time == "t1_first_touch_escalating")
                 & (L38.rung == "B_intake")]
        put("VtauOneLo", sig(float(r2.lo.iloc[0]), 4) if len(r2) else None)
        put("VtauOneHi", sig(float(r2.hi.iloc[0]), 4) if len(r2) else None)
    else:
        for k in ("VtauZeroLo", "VtauZeroHi", "VtauOneLo", "VtauOneHi"):
            put(k, None)


def _texname(s):
    """A log name is data, and BPIC15_5 carries an underscore.  A macro whose
    value holds an unescaped LaTeX special is a live grenade -- texlint check
    7c exists because one of them once commented out its own closing brace --
    so a name that reaches the prose is escaped where it is defined."""
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"),
                 ("#", "\\#"), ("_", "\\_"), ("$", "\\$"),
                 ("{", "\\{"), ("}", "\\}")):
        s = s.replace(a, b)
    return s


def emit_round25(mn):
    """ROUND TWENTY-FIVE.  The quantities the round-24 minor comments need,
    and the ones s41 produces.

    Kept in its own function rather than appended to `emit` because they come
    from a disjoint set of sources and because a reader tracing a round-25
    number should land on the round-25 block.  `make_numbers.main` calls this
    once, immediately after `emit`.
    """
    put, load, pct, num, sig, first = (mn.put, mn.load, mn.pct, mn.num,
                                       mn.sig, mn.first)
    thousands = mn.thousands

    # ================================================================
    # the admission window, and how close the largest pair sits to it
    # ================================================================
    #  ROUND TWENTY-FOUR, minor 7.  The headroom rule admits a pair whose
    #  prevalence IN THE FULL LOG lies inside [prevLo, prevHi].  A referee
    #  observed that the pair carrying the most cells of any in the corpus
    #  sits close to the upper edge, and that logs not much further out are
    #  excluded by the same rule -- so the paper's largest single
    #  contribution rests on a margin worth naming.
    #
    #  WHAT EACH MACRO RANGES OVER (rule 7 of the handoff):
    #    prevAdmittedMax   the MAXIMUM prevalence over the 19 ADMITTED pairs
    #    prevExcludedMin   the MINIMUM prevalence over the pairs excluded by
    #                      the headroom rule ALONE -- not over all exclusions,
    #                      most of which are excluded for other reasons
    #    nCellsLargestPair the declared admissible scalar cells of the ONE
    #                      pair attaining prevAdmittedMax
    H = load("r33_headroom_sensitivity.csv")
    A = load("s25_audit.csv")
    if H is not None and len(H) and A is not None and len(A):
        adm = H[H.admitted_as_registered.astype(bool)]
        exc = H[~H.admitted_as_registered.astype(bool)]
        if len(adm):
            top = adm.loc[adm.prevalence_full.idxmax()]
            put("prevAdmittedMax", num(float(top.prevalence_full), 3))
            put("logAdmittedMaxPrev",
                _texname("%s/%s" % (top.log, top.target)))
            cell = A[(A.log == top.log) & (A.target == top.target)]
            put("nCellsLargestPair",
                thousands(int(cell.declared_admissible_scalar.iloc[0]))
                if len(cell) else None)
        else:
            for k in ("prevAdmittedMax", "logAdmittedMaxPrev",
                      "nCellsLargestPair"):
                put(k, None)
        #  The comparison the referee drew is at the UPPER edge, so the set
        #  is the pairs the headroom rule turned away for being ABOVE the
        #  window, not every pair it turned away: the corpus also contains
        #  exclusions far below the lower edge, and the minimum over all
        #  exclusions is one of those and answers a different question.
        hi = float(mn.PREV_HI)
        above = exc[exc.prevalence_full > hi]
        if len(above):
            bot = above.loc[above.prevalence_full.idxmin()]
            put("prevExcludedAboveMin", num(float(bot.prevalence_full), 3))
            put("logExcludedAboveMin", _texname("%s/%s" % (bot.log,
                                                           bot.target)))
            put("nExcludedAbove", thousands(int(len(above))))
        else:
            for k in ("prevExcludedAboveMin", "logExcludedAboveMin",
                      "nExcludedAbove"):
                put(k, None)
    else:
        for k in ("prevAdmittedMax", "logAdmittedMaxPrev",
                  "nCellsLargestPair", "prevExcludedAboveMin",
                  "logExcludedAboveMin", "nExcludedAbove"):
            put(k, None)

    # ================================================================
    # the (n, K) grid's Monte Carlo precision, which it never stated
    # ================================================================
    #  ROUND TWENTY-FOUR, minor 3.  Table S30 prints ten coverages to three
    #  decimals and says nothing about how well any of them is determined.
    #  They come from the GRID experiment, which trades replicates for
    #  coverage of the plane and runs at a fraction of the core's count, so
    #  the standard error the manuscript quotes for the simulation -- the
    #  core's -- is the wrong one to carry over to that table.  Worse, the
    #  grid's coverages are nowhere near 0.95, and a standard error computed
    #  at the nominal rate understates the error at an observed rate of 0.2
    #  or 0.5.  The macros below are taken from the OBSERVED rate of each
    #  cell, which is what s31 already writes per row.
    #
    #  WHAT EACH MACRO RANGES OVER (rule 7):
    #    simGridReps         the replicate count of every grid cell
    #    simGridSEMedian     the MEDIAN over the ten grid cells of the
    #                        per-cell Monte Carlo standard error of coverage,
    #                        each at that cell's own observed rate
    #    simGridSEMax        the MAXIMUM of the same ten
    #    simGridSERatio      simGridSEMedian divided by the CORE experiment's
    #                        standard error, which is the one section 10.2
    #                        quotes
    C31 = load("s31_coverage.csv")
    if C31 is not None and len(C31) and "coverage_se" in C31.columns:
        gr = C31[(C31.estimand == "V_limit") & (C31.experiment == "grid")
                 & (C31.interval == "nested_basic")]
        co = C31[(C31.estimand == "V_limit") & (C31.experiment == "core")
                 & (C31.interval == "nested_basic")]
        if len(gr) and len(co):
            gse = float(gr.coverage_se.median()) * 100.0
            cse = float(co.coverage_se.median()) * 100.0
            put("simGridReps", thousands(int(gr.n.max())))
            put("simGridSEMedian", num(gse, 1))
            put("simGridSEMax", num(float(gr.coverage_se.max()) * 100.0, 1))
            put("simGridSERatio", num(gse / cse, 1) if cse else None)
            put("simCoreReps", thousands(int(co.n.max())))
        else:
            for k in ("simGridReps", "simGridSEMedian", "simGridSEMax",
                      "simGridSERatio", "simCoreReps"):
                put(k, None)
    else:
        for k in ("simGridReps", "simGridSEMedian", "simGridSEMax",
                  "simGridSERatio", "simCoreReps"):
            put(k, None)

    # ================================================================
    # the two comparisons section 10.3 makes on the (n, K) plane
    # ================================================================
    #  ROUND TWENTY-FIVE.  Section 10.3 argued that K/n is not sufficient by
    #  naming two cells at nearly the same ratio and quoting their coverages,
    #  and it quoted them as LITERALS -- inside $...$, which is why the
    #  no-numeric-literals check never saw them: `body_of` strips inline math
    #  before it looks.  Three coverages of a simulation were typed into the
    #  prose of a paper whose first rule is that no number is.  texlint now
    #  reads inside math against an allowlist, and these are macros.
    #
    #  The cells are SELECTED BY RULE rather than named, so that re-running
    #  s31 on a different grid moves the sentence with it:
    #    the same-ratio pair   the two grid cells whose K/n ratios are closest
    #                          to each other IN RELATIVE terms -- smallest
    #                          |log(ratio_a) - log(ratio_b)| -- among cells
    #                          that differ in both K and n.  Relative and not
    #                          absolute: the plane's ratios span two orders of
    #                          magnitude, and an absolute rule calls 0.010 and
    #                          0.025 closer than 0.100 and 0.125 when they
    #                          differ by a factor of two and a half.
    #    the fixed-K pair      the smallest and largest n at the largest K
    #                          that the grid runs at more than one n
    if C31 is not None and len(C31) and "coverage_se" in C31.columns:
        g = C31[(C31.estimand == "V_limit") & (C31.experiment == "grid")
                & (C31.interval == "nested_basic")].copy()
    else:
        g = None
    if g is not None and len(g) > 2:
        g["ratio"] = g.K / g.n_train
        rows = list(g.itertuples())
        best = None
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                if a.K == b.K or a.n_train == b.n_train:
                    continue
                d = abs(np.log(a.ratio) - np.log(b.ratio))
                if best is None or d < best[0]:
                    best = (d, a, b)
        _d, a, b = best
        #  print the smaller-n cell first, which is the order the sentence
        #  reads in and the order the plane is drawn in
        if a.n_train > b.n_train:
            a, b = b, a
        put("simGridSameRatioKa", thousands(int(a.K)))
        put("simGridSameRatioNa", thousands(int(a.n_train)))
        put("simGridSameRatioCovA", num(float(a.coverage), 3))
        put("simGridSameRatioKb", thousands(int(b.K)))
        put("simGridSameRatioNb", thousands(int(b.n_train)))
        put("simGridSameRatioCovB", num(float(b.coverage), 3))
        gap = abs(float(a.coverage) - float(b.coverage))
        se = float(np.sqrt(a.coverage_se ** 2 + b.coverage_se ** 2))
        put("simGridSameRatioGapSE", num(gap / se, 1) if se else None)

        counts = g.groupby("K").n_train.nunique()
        multi = counts[counts > 1]
        if len(multi):
            kk = int(multi.index.max())
            s = g[g.K == kk].sort_values("n_train")
            lo, hi = s.iloc[0], s.iloc[-1]
            put("simGridFixedK", thousands(kk))
            put("simGridFixedNa", thousands(int(lo.n_train)))
            put("simGridFixedNb", thousands(int(hi.n_train)))
            put("simGridFixedCovA", num(float(lo.coverage), 3))
            put("simGridFixedCovB", num(float(hi.coverage), 3))
        else:
            for k in ("simGridFixedK", "simGridFixedNa", "simGridFixedNb",
                      "simGridFixedCovA", "simGridFixedCovB"):
                put(k, None)
    else:
        for k in ("simGridSameRatioKa", "simGridSameRatioNa",
                  "simGridSameRatioCovA", "simGridSameRatioKb",
                  "simGridSameRatioNb", "simGridSameRatioCovB",
                  "simGridSameRatioGapSE", "simGridFixedK", "simGridFixedNa",
                  "simGridFixedNb", "simGridFixedCovA", "simGridFixedCovB"):
            put(k, None)

    # ================================================================
    # s41 -- the band's family-wise coverage, against a known answer
    # ================================================================
    #  ROUND TWENTY-FIVE.  The gap section 4.3 named in its own last sentence.
    #
    #  WHAT EACH MACRO RANGES OVER (rule 7), because this is the file that
    #  makes the point about macros ranging over selected subsets:
    #    every `cov*' macro below is over the SIX GRID CELLS of s41 --
    #    (K, B) matched to the corpus's own families -- and NOT over the
    #    draw-count sensitivity rows, which share (family, K) with a grid cell
    #    and would otherwise be pooled into the same median.  s41 selects them
    #    on K_nom and B together; selecting on the realised K silently dropped
    #    every degenerate-regime row and reported a minimum of 0.835 where the
    #    experiment had measured 0.392.
    #    the `B*' macros are ONE cell -- the modal surface family, K = 180,
    #    under the heavy regime -- at five draw counts.
    F41 = load("s41_facts.csv")
    P41 = load("s41_profile.csv")
    put("nBandCoverageReps", thousands(first(F41, "n_reps")))
    put("nBandCoverageCells", thousands(first(F41, "n_cells")))
    put("bandCoverageSEMax", pct(first(F41, "coverage_se_max")))
    for tag, key in (("Gauss", "gaussian"), ("Heavy", "heavy"),
                     ("Degen", "degenerate")):
        for mac, cand in (("Mult", "q_mult"), ("MultHi", "q_mult_hi"),
                          ("Emp", "q_emp"), ("EmpHi", "q_emp_hi"),
                          ("Rad", "q_rad")):
            put("cov%s%sMedian" % (mac, tag),
                pct(first(F41, "cov_%s_%s_median" % (cand, key))))
            put("cov%s%sMin" % (mac, tag),
                pct(first(F41, "cov_%s_%s_min" % (cand, key))))
    #  a LaTeX control word is letters only, so the draw count is spelled
    #  into the macro name; `\covMultBoot1000' does not compile and the
    #  failure is a runaway argument several files later.
    for b, word in ((33, "ThirtyThree"), (80, "Eighty"), (150, "OneFifty"),
                    (400, "FourHundred"), (1000, "OneThousand")):
        put("covMultBoot" + word, pct(first(F41, "cov_mult_B%d" % b)))
        put("covPercellBoot" + word, pct(first(F41, "cov_percell_B%d" % b)))
        put("nBoot" + word, thousands(b))
    put("widthEmpHiOverMult", num(first(F41, "width_q_emp_hi_over_mult_heavy"),
                                  2))
    put("nDegenerateCellsDca", thousands(first(F41, "n_degenerate_dca")))
    put("nDegenerateCellsWhole", thousands(first(F41, "n_degenerate_whole")))
    put("shareDegenerateDcaMaxPct",
        pct(first(F41, "share_degenerate_dca_max")))
    put("ratioDcaAll", num(first(F41, "ratio_dca_all"), 2))
    put("ratioDcaAdmissible", num(first(F41, "ratio_dca_adm"), 2))
    put("nQbelowEmpDcaAdmissible", thousands(first(F41, "n_below_dca_adm")))
    put("nQbelowEmpWholeAdmissible",
        thousands(first(F41, "n_below_whole_adm")))
    put("corpusKurtMedWhole", num(first(F41, "corpus_kurt_med_whole"), 2))
    put("corpusKurtNinetyWhole", num(first(F41, "corpus_kurt_p90_whole"), 1))
    put("corpusKurtMedDca", num(first(F41, "corpus_kurt_med_dca_adm"), 2))
    put("corpusKurtNinetyDca", num(first(F41, "corpus_kurt_p90_dca_adm"), 1))
    if P41 is not None and len(P41):
        dc41 = P41[P41.family == "decision-curve"]
        put("nDcaFamiliesWithDegenerate",
            thousands(int((dc41.n_degenerate > 0).sum())))
    else:
        put("nDcaFamiliesWithDegenerate", None)

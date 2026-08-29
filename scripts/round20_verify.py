"""round20_verify -- independent re-derivations of the round-twenty macros.

`make_numbers.py` reads a `*_facts.csv` row and formats it.  This file
recomputes the same quantity from the ROW-LEVEL result file with code written
against the definition, so a wrong aggregation in an analysis script produces
a disagreement here rather than a manuscript that is consistently wrong.

Where make_numbers reads a summary, this reads the detail.  Where make_numbers
reads a median of a stored column, this recomputes the column.  It is called
from `verify_numbers.main`, shares its `eq` helper, and adds to its failure
list.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def check(vn, M):
    """`vn` is the verify_numbers module; `M` the macro table."""
    eq, load = vn.eq, vn.load
    fmt_pct, fmt_num, fmt_thousands = vn.fmt_pct, vn.fmt_num, vn.fmt_thousands
    fmt_sig = vn.fmt_sig

    # ---- s25: the denominator, recounted from the surface itself --------
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import spec as S

    SUR = load("s01_surface.csv")
    if SUR is not None and len(SUR):
        adm = SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                  & (SUR.metric.isin(S.SCALARS))]
        #  the admissible scalar surface, counted by grouping rather than by
        #  reading a stored total
        n = int(adm.groupby(["log", "target", "learner", "split", "quality",
                             "level", "rung", "metric"]).ngroups)
        eq("nDeclaredAdmissibleScalar", fmt_thousands(n), M,
           "recounted from s01_surface by grouping")
        dup = len(adm) - n
        eq("nDuplicateCells", fmt_thousands(dup), M, "recounted")

    #  The design space's axis count is a WORD in the manuscript
    #  ("nine axes"), typed into make_numbers rather than derived, and the
    #  axis table is generated.  If somebody adds an axis the table grows and
    #  the word does not, so the word is checked against the table.
    AX = load("s25_axis_levels.csv")
    if AX is not None and len(AX):
        WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
                 11: "eleven", 12: "twelve"}
        #  the axis table prints one row per axis NAME the walker reports
        n_ax = int(AX.axis.nunique())
        eq("nAxes", WORDS.get(n_ax, str(n_ax)), M,
           "counted from the axis-level file the design-space table is built "
           "from")

    # ---- s22: the decomposition, recomputed from the index file ---------
    IDX = load("s22_indices.csv")
    SUM = load("s22_summary.csv")
    if IDX is not None and len(IDX):
        pr = IDX[(IDX.scale == "raw-within-metric")
                 & (IDX.measure == "equal-level")]
        #  total higher-order share = 1 - sum of first-order indices, summed
        #  per (pair, metric) and then reduced by the same two medians
        s1 = pr.groupby(["log", "target", "metric"]).S.sum()
        inter = 1.0 - s1
        per_pair = inter.groupby(level=[0, 1]).median()
        eq("interactionTotalPct", fmt_pct(float(per_pair.median())), M,
           "1 - sum of first-order indices, recomputed from s22_indices")
        eq("interactionMinPct", fmt_pct(float(per_pair.min())), M)
        eq("interactionMaxPct", fmt_pct(float(per_pair.max())), M)
        top = pr.groupby(["log", "target", "metric"]).S.max()
        eq("largestFirstOrderPct",
           fmt_pct(float(top.groupby(level=[0, 1]).median().median())), M)
        inv = (pr.assign(d=pr.S_total - pr.S)
               .groupby(["log", "target", "metric"]).d.max())
        eq("largestInvolvementPct",
           fmt_pct(float(inv.groupby(level=[0, 1]).median().median())), M)
        for ax, nm in (("learner", "sLearnerPct"), ("split", "sSplitPct"),
                       ("quality_level", "sQualityPct"), ("rung", "sRungPct")):
            v = (pr[pr.axis == ax].groupby(["log", "target"]).S.median()
                 .median())
            eq(nm, fmt_pct(float(v)), M)
    if SUM is not None and len(SUM):
        #  the identity the whole correction rests on: the disjoint
        #  components sum to one on every decomposition
        bad = int(((SUM.check_sum - 1.0).abs() > 1e-8).sum())
        if bad:
            vn.FAILS.append("s22: %d decompositions whose disjoint ANOVA "
                            "components do not sum to one" % bad)

    # ---- s23: regret, recomputed from the per-cell file -----------------
    A23 = load("s23_metric_regret.csv")
    if A23 is not None and len(A23):
        g = A23[(A23.measure == "equal-level") & (A23.metric == "auc")]
        one = g[g.rule == "one-number"]
        eq("excessOneNumberAuc", fmt_num(float(one.excess.mean()), 4), M,
           "mean over pairs, recomputed from s23_metric_regret")
        eq("nBadOneNumberAuc",
           fmt_thousands(int((one.excess > 1e-9).sum())), M)
        maj = g[g.rule == "majority"]
        eq("excessMajorityAuc", fmt_num(float(maj.excess.mean()), 4), M)
        uni = g[g.rule == "uniform-beneficial"]
        eq("nBadUniformAuc", fmt_thousands(int((uni.excess > 1e-9).sum())), M)
        wm = g[g.rule == "weighted-mean"]
        if len(wm) and float(wm.excess.abs().max()) > 1e-9:
            vn.FAILS.append("s23: the weighted-mean rule is not optimal in "
                            "sample, which contradicts Lemma 1")
    H23 = load("s23_heldout.csv")
    if H23 is not None and len(H23):
        h = H23[(H23.design == "held-out cells") & (H23.metric == "auc")]
        for rule, nm in (("one-number", "oosOneNumberAuc"),
                         ("majority", "oosMajorityAuc"),
                         ("weighted-mean", "oosMeanAuc")):
            v = h[h.rule == rule].excess.mean()
            eq(nm, fmt_num(float(v), 5), M,
               "mean over replications, recomputed from s23_heldout")

    #  C. the CROSS-INSTRUMENT DIRECTION claims, recounted.  The manuscript
    #  said two orderings held "in all five instruments" and neither did; the
    #  counts are macros now, and this re-derives them from the same tables
    #  the prose reads so that a sentence and a table cannot disagree again.
    if A23 is not None and len(A23):
        t = (A23[A23.measure == "equal-level"]
             .groupby(["metric", "rule"]).excess.mean().unstack())
        if {"uniform-beneficial", "one-number"} <= set(t.columns):
            worst = t.idxmax(axis=1)
            eq("nInstrumentsUniformWorst",
               fmt_thousands(int((worst == "uniform-beneficial").sum())), M,
               "recounted from s23_metric_regret")
            eq("nInstruments", fmt_thousands(len(t)), M)
        #  "the median excess regret of the one-number rule is zero in every
        #  instrument" -- a universal, so a check rather than a sentence.
        med = (A23[(A23.measure == "equal-level")
                   & (A23.rule == "one-number")]
               .groupby("metric").excess.median())
        if len(med) and float(med.abs().max()) > 1e-12:
            vn.FAILS.append(
                "s23: the manuscript says the one-number rule's median "
                "excess regret is zero in every instrument; it is %.5f under "
                "%s" % (float(med.abs().max()), med.abs().idxmax()))
    if H23 is not None and len(H23):
        hh = (H23[H23.design == "held-out cells"]
              .groupby(["metric", "rule"]).excess.mean().unstack())
        if {"one-number", "majority", "weighted-mean"} <= set(hh.columns):
            ok = ((hh["one-number"] > hh["majority"])
                  & (hh["majority"] >= hh["weighted-mean"]))
            eq("nInstrumentsOosOrdering", fmt_thousands(int(ok.sum())), M,
               "recounted from s23_heldout")
            eq("nInstrumentsOneNumberWorse",
               fmt_thousands(int((hh["one-number"] > hh["majority"]).sum())),
               M)

    #  D. every regret aggregation has ONE unit, and no two units are ever
    #  averaged together.  This is the check the blueprint asks for by name,
    #  and it is cheap because s23 carries the unit as a column.
    if A23 is not None and len(A23):
        for keys, g in A23.groupby(["log", "target", "metric", "measure",
                                    "rule"]):
            if g.unit.nunique() != 1:
                vn.FAILS.append("s23: %s aggregates %d different units"
                                % (str(keys), g.unit.nunique()))
                break
        if A23.groupby("metric").unit.nunique().max() > 1:
            vn.FAILS.append("s23: an instrument carries more than one unit "
                            "name")
        #  the review's assertion 4: the cells regret averages over must be
        #  the DECLARED regret population, not whatever the file happened to
        #  contain.  Every rule at a (pair, instrument, measure) must average
        #  over the same cells, and that count must equal the admissible
        #  scalar cells of that pair-instrument counted from s01.
        n_by_rule = A23.groupby(["log", "target", "metric",
                                 "measure"]).n_cells.nunique()
        if int(n_by_rule.max() or 0) > 1:
            vn.FAILS.append("s23: two decision rules are compared over "
                            "different cell sets, so their losses are not "
                            "comparable")
        if SUR is not None and len(SUR):
            cells = (SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                         & (SUR.metric.isin(S.SCALARS))]
                     [["log", "target", "metric", "learner", "split",
                       "quality", "level", "rung"]].drop_duplicates())
            declared = cells.groupby(["log", "target", "metric"]).size()
            got = (A23.groupby(["log", "target", "metric"]).n_cells.max())
            join = declared.rename("declared").to_frame().join(
                got.rename("used"), how="inner")
            off = join[join.declared != join.used]
            if len(off):
                vn.FAILS.append(
                    "s23: on %d pair-instruments the regret population is "
                    "not the declared admissible set (declared %s, used %s)"
                    % (len(off), list(off.declared)[:3],
                       list(off.used)[:3]))

    # ---- headline quantities that had no independent re-derivation ------
    #  The claim registry reports which macros the verifier re-derives, and
    #  it showed only ten of the twenty-nine HEADLINE macros -- the ones the
    #  abstract, the introduction and the conclusion print.  These are the
    #  rest that can be recomputed from a row-level file.
    REP = load("s25_representative.csv")
    if REP is not None and len(REP):
        gap = (REP.share_positive_declared
               - REP.share_positive_inference).abs()
        eq("repGapMedian", fmt_num(float(gap.median()), 3), M,
           "recomputed per pair from s25_representative")
        eq("repGapMax", fmt_num(float(gap.max()), 3), M)
    MEA = load("s22_measures.csv")
    if MEA is not None and len(MEA):
        prod = MEA[MEA.measure != "envelope"]
        if len(prod):
            spread = float(prod.interaction_total_median.max()
                           - prod.interaction_total_median.min())
            eq("measureSpreadPct", fmt_pct(spread), M,
               "range over the three PRODUCT measures, which are the three "
               "corpus medians; the envelope is a single-pair quantity and "
               "is excluded")
        c = MEA[MEA.measure == "concentrated"]
        if len(c) and "n_pairs_first_order_exceeds" in c.columns:
            eq("nConcentratedExceeds",
               fmt_thousands(int(c.n_pairs_first_order_exceeds.iloc[0])), M)
        e = MEA[MEA.measure == "equal-level"]
        if len(e) and "n_pairs_first_order_exceeds" in e.columns:
            eq("nEqualExceeds",
               fmt_thousands(int(e.n_pairs_first_order_exceeds.iloc[0])), M)
    AUD2 = load("s25_audit.csv")
    if AUD2 is not None and len(AUD2) and "inference_draws" in AUD2.columns:
        dr = AUD2.inference_draws[AUD2.inference_draws > 0]
        if len(dr):
            eq("nDrawsSurfaceMin", fmt_thousands(int(dr.min())), M,
               "recounted from the denominator audit")
            eq("nDrawsSurfaceMax", fmt_thousands(int(dr.max())), M)
            eq("nDrawsSurface", fmt_thousands(int(dr.median())), M)
        #  ROUND TWENTY-SEVEN.  The inference family's share of a pair's
        #  surface, against BOTH denominators the manuscript names, and with
        #  each denominator MULTIPLIED OUT of the declared axis levels rather
        #  than read from the audit's own column -- which is what this file is
        #  for: make_numbers reads a stored count, this recomputes it.
        #
        #  The two denominators differ by ONE axis level.  The full declared
        #  grid carries the intercept-only rung; every admissible set excludes
        #  it by declaration (Table~\ref{tab:axes} prints the exclusion and
        #  its reason).  One macro was serving both sentences, so a share of
        #  the master surface file was printed where a share of the admissible
        #  surface was claimed.
        AXL = load("s25_axis_levels.csv")
        if AXL is not None and len(AXL) and "n_levels" in AXL.columns:
            lev = {(r.log, r.target, r.axis): int(r.n_levels)
                   for r in AXL.itertuples()}

            def _levels(log, target, axes):
                n = 1
                for a in axes:
                    if (log, target, a) not in lev:
                        return None
                    n *= lev[(log, target, a)]
                return n

            _base = ["learner", "split", "quality_level"]
            s_all, s_adm = [], []
            for r in AUD2.itertuples():
                full = _levels(r.log, r.target, _base + ["rung"])
                adm = _levels(r.log, r.target, _base + ["admissible_rung"])
                if not full or not adm:
                    continue
                s_all.append(float(r.inference_cells_observed) / full)
                s_adm.append(float(r.inference_cells_observed) / adm)
            if s_all:
                eq("inferenceShareMedianPct",
                   fmt_pct(float(np.median(s_all)), 1), M,
                   "inference arms over the FULL declared grid, multiplied "
                   "out of the axis levels; that grid carries the "
                   "intercept-only rung")
                eq("inferenceShareAdmissibleMedianPct",
                   fmt_pct(float(np.median(s_adm)), 1), M,
                   "inference arms over the ADMISSIBLE grid, the "
                   "intercept-only rung removed as every admissible set "
                   "removes it")
    #  the corpus spread and the sign-varying count, recomputed from the
    #  master surface rather than from the generator's own filter
    if SUR is not None and len(SUR):
        #  every axis but the rung is held at its reference level, which is
        #  what the sentence this number appears in claims
        A = SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (SUR.metric == "auc") & (SUR.quality == "clean")
                & (SUR.learner == "logit")
                & (SUR.split == "holdout70")]
        if len(A):
            sp = A.groupby(["log", "target"]).V.apply(
                lambda x: float(x.max() - x.min()))
            eq("spreadMedian", fmt_num(float(sp.median()), 3), M,
               "max minus min over the RUNG alone at the reference cell")
            eq("spreadMax", fmt_num(float(sp.max()), 3), M)
        B = SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (SUR.metric.isin(S.SCALARS))]
        g = B.groupby(["log", "target"]).V.apply(
            lambda x: float((x > 0).mean()))
        eq("nSignVaries",
           fmt_thousands(int(((g > 0.10) & (g < 0.90)).sum())), M,
           "recounted from the surface")

    #  the target-agreement headline, recomputed from the per-log file
    T16 = load("s16_target_agreement.csv")
    if T16 is not None and len(T16) and "agreement" in T16.columns:
        eq("targetAgreement", fmt_pct(float(T16.agreement.median()), 0), M,
           "median over logs, recomputed from s16_target_agreement")
        eq("targetAgreementLo", fmt_pct(float(T16.agreement.min()), 0), M)
        eq("targetAgreementHi", fmt_pct(float(T16.agreement.max()), 0), M)
    if MEA is not None and len(MEA):
        env = MEA[MEA.measure == "envelope"]
        if len(env):
            eq("interactionEnvelopePct",
               fmt_pct(float(env.interaction_total_median.iloc[0])), M,
               "the envelope row of s22_measures, which is the primary pair "
               "and not a corpus median")

    # ---- s21: the bands, recomputed from the band file ------------------
    B21 = load("s21_bands.csv")
    R21 = load("s21_regions.csv")
    #  families s21 could not build from complete replicates.  Recorded by
    #  s21 rather than raised there; a build in which any exist is a build a
    #  reader must be told about, so it fails here.
    #  A replicate is dropped from a family when a resample leaves one of its
    #  cells without outcome variation, which happens on the smallest logs.
    #  The manuscript REPORTS the shortfall (Section 4.4), so its existence is
    #  not a failure; what fails is a family whose band rests on too little to
    #  be a band at all, or one whose critical value came out below the
    #  pointwise one, which cannot happen if the maximum was taken correctly.
    INC = load("s21_incomplete.csv")
    if INC is not None and len(INC):
        if "q_below_pointwise" in INC.columns \
                and INC.q_below_pointwise.notna().any():
            vn.FAILS.append(
                "s21: a whole-surface critical value came out below the "
                "pointwise 1.96, which the maximum over a family cannot do; "
                "see results/s21_incomplete.csv")
        if "n_draws_complete" in INC.columns:
            share = (INC.n_draws_complete / INC.n_draws_declared)
            if float(share.min()) < 0.75 or int(INC.n_draws_complete.min()) < 20:
                vn.FAILS.append(
                    "s21: a band family rests on %d of %d declared replicates "
                    "(%.0f%%); below three quarters, or below twenty, the "
                    "band is not reportable"
                    % (int(INC.n_draws_complete.min()),
                       int(INC.loc[share.idxmin(), "n_draws_declared"]),
                       100 * float(share.min())))

    if B21 is not None and len(B21):
        ws = B21[B21.family == "whole-surface"]
        #  a simultaneous band is never narrower than a pointwise one
        if len(ws) and float(ws.q.min()) < 1.959963984540054 - 1e-9:
            vn.FAILS.append("s21: a whole-surface critical value below the "
                            "pointwise 1.96")
        #  and the whole-surface family is never smaller than the
        #  within-instrument family it replaces
        wi_ = B21[B21.family == "within-instrument"]
        if len(wi_) and float(ws.n_family.min()) < float(wi_.n_family.max()):
            vn.FAILS.append("s21: the whole-surface family is smaller than "
                            "the within-instrument family")
        per = ws.groupby(["log", "target"]).q.first()
        eq("maxTSurfaceMedian", fmt_num(float(per.median()), 2), M,
           "median over pairs, recomputed from s21_bands")
        eq("maxTSurfaceMin", fmt_num(float(per.min()), 2), M)
        eq("maxTSurfaceMax", fmt_num(float(per.max()), 2), M)
        fam = ws.groupby(["log", "target"]).n_family.first()
        eq("familySizeMedian", fmt_thousands(float(fam.median())), M)
        wi = B21[B21.family == "within-instrument"]
        if len(wi):
            eq("maxTWithinMedian", fmt_num(float(wi.q.median()), 2), M)
    if R21 is not None and len(R21):
        eq("nRegionChangedByFamily",
           fmt_thousands(int((R21.region
                              != R21.region_within_instrument).sum())), M,
           "recounted from s21_regions")
        eq("rhoMedian", fmt_num(float(R21.rho.median()), 3), M)
        eq("nUniformlyBeneficial",
           fmt_thousands(int((R21.region == "uniformly beneficial").sum())), M)
        eq("nSignChanging",
           fmt_thousands(int((R21.region == "sign-changing").sum())), M)
        #  a region label must be consistent with its own cell counts
        bad = R21[(R21.region == "uniformly beneficial")
                  & (R21.n_unresolved + R21.n_harmful > 0)]
        if len(bad):
            vn.FAILS.append("s21: %d surfaces labelled uniformly beneficial "
                            "while carrying an unresolved or harmful cell"
                            % len(bad))
        #  the review's assertion 3: the cells a region label ranges over
        #  must be exactly the cells the simultaneous family controls.  The
        #  three labelled counts must therefore partition the family, and the
        #  family size is read from the band file rather than from this one.
        parts = R21.n_beneficial + R21.n_harmful + R21.n_unresolved
        off = R21[parts != R21.n_cells]
        if len(off):
            vn.FAILS.append("s21: on %d pairs the region's three labelled "
                            "counts do not partition its own cell count"
                            % len(off))
        if B21 is not None and len(B21):
            fam = (B21[B21.family == "whole-surface"]
                   .groupby(["log", "target"]).n_family.first())
            joined = R21.set_index(["log", "target"]).join(
                fam.rename("n_family"), how="inner")
            mism = joined[joined.n_cells != joined.n_family]
            if len(mism):
                vn.FAILS.append(
                    "s21: on %d pairs the region label ranges over a "
                    "different cell set from the simultaneous family that "
                    "licenses it (n_cells != n_family)" % len(mism))

    # ---- s26: the decision-curve bands ----------------------------------
    B26 = load("s26_bands.csv")
    if B26 is not None and len(B26):
        #  Section 4.2 says every interval in the manuscript is the basic
        #  (pivotal) construction.  The decision curve's pointwise interval
        #  was a percentile interval until round twenty's second session, and
        #  nothing said so, so the band file now declares its construction and
        #  this refuses a build in which it is anything else.
        if "construction" not in B26.columns:
            vn.FAILS.append("s26: the decision-curve band file does not "
                            "declare its interval construction")
        elif set(B26.construction.unique()) != {"basic"}:
            vn.FAILS.append("s26: a decision-curve interval is %s, and the "
                            "manuscript says every interval in it is basic"
                            % sorted(set(B26.construction.unique())))
        #  s26 counts the harmful points into s26_facts.csv over the WHOLE
        #  declared family; the manuscript's harmful counts are over the
        #  reference curve alone, which is a different population and must
        #  not be compared with it -- the first version of this check did
        #  compare them and reported a disagreement that was a definition,
        #  not a defect.  What is checked here is the facts file against the
        #  band file it summarises.
        eq("dcaHarmfulSimultaneous",
           fmt_thousands(int((B26.sim_hi < 0).sum())), M,
           "recounted over the whole family from s26_bands")
        eq("dcaHarmfulPointwise",
           fmt_thousands(int((B26.pt_hi < 0).sum())), M,
           "recounted over the whole family from s26_bands")
        #  a simultaneous interval is never narrower than the pointwise one
        #  built from the same draws, once both are the same construction
        if {"sim_lo", "sim_hi", "pt_lo", "pt_hi"} <= set(B26.columns):
            narrow = B26[(B26.sim_hi - B26.sim_lo)
                         < (B26.pt_hi - B26.pt_lo) - 1e-12]
            if len(narrow):
                vn.FAILS.append("s26: %d simultaneous decision-curve "
                                "intervals are narrower than their pointwise "
                                "counterparts" % len(narrow))

    # ---- s24: the planned contrasts -------------------------------------
    C24 = load("s24_contrasts.csv")
    if C24 is not None and len(C24):
        B = int(C24.n_draws.max())
        eq("nDrawsPlanned", fmt_thousands(B), M, "from the contrast file")
        eq("pMinAttainableRaw", fmt_num(1.0 / (B + 1.0), 5), M,
           "the plus-one floor, recomputed")
        eq("pMinAttainableHolm", fmt_num(len(C24) / (B + 1.0), 5), M)
        eq("nPlannedReject",
           fmt_thousands(int((C24.p_holm < 0.05).sum())), M)
        if float(C24.p_raw.min()) <= 0 or float(C24.p_holm.min()) <= 0:
            vn.FAILS.append("s24: a bootstrap p-value of zero, which the "
                            "plus-one estimator cannot produce")
        if float(C24.p_raw.min()) < 1.0 / (B + 1.0) - 1e-12:
            vn.FAILS.append("s24: a raw p-value below the floor the draw "
                            "count permits")
        #  Holm, re-derived independently
        p = list(C24.p_raw.values)
        k = len(p)
        order = np.argsort(p)
        out = [0.0] * k
        run = 0.0
        for i, j in enumerate(order):
            run = max(run, min(1.0, p[j] * (k - i)))
            out[j] = run
        if not np.allclose(out, C24.p_holm.values, atol=1e-12):
            vn.FAILS.append("s24: the Holm adjustment does not reproduce")

    # ---- s26: calibration ------------------------------------------------
    CAL = load("s26_calibration.csv")
    if CAL is not None and len(CAL):
        for kind, nm in (("raw", "slopeRawMedian"),
                         ("isotonic", "slopeIsoMedian"),
                         ("platt", "slopePlattMedian")):
            v = CAL[CAL.calibration == kind].cal_slope.median()
            eq(nm, fmt_num(float(v), 2), M, "recomputed from s26_calibration")
        for kind, nm in (("raw", "eceRawMedian"), ("isotonic", "eceIsoMedian")):
            v = CAL[CAL.calibration == kind].ece.median()
            eq(nm, fmt_num(float(v), 3), M)
        eq("nSlopeOutRaw", fmt_thousands(int(
            ((CAL.calibration == "raw")
             & ((CAL.cal_slope < 0.5) | (CAL.cal_slope > 2.0))).sum())), M)

    # ---- s27: register quality ------------------------------------------
    Q27 = load("s27_summary.csv")
    if Q27 is not None and len(Q27):
        st = Q27[Q27.metric == "auc"]
        eq("gridShiftMax", fmt_num(float(st.grid_shift.max()), 4), M,
           "recomputed from s27_summary")
        eq("seedSdMedian", fmt_num(float(st.seed_sd_median.median()), 4), M)

    # ---- s29: the propositions -------------------------------------------
    INV29 = load("s29_invariance.csv")
    CER29 = load("s29_certificates.csv")
    WID29 = load("s29_wider.csv")
    if INV29 is not None and len(INV29):
        eq("nInvarianceChecks", fmt_thousands(len(INV29)), M)
        v = float(INV29.abs_shift.max())
        if v > 1e-9:
            vn.FAILS.append("s29: a rank-based instrument's reduction moved "
                            "under a monotone recalibration by %.3e" % v)
    if CER29 is not None and len(CER29):
        eq("nCertificates", fmt_thousands(len(CER29)), M)
        eq("certificateMinShift", fmt_num(float(CER29.R_shift.min()), 3), M)
        #  a certificate is only a certificate if the two ratios differ
        if float(CER29.ratio_gap.min()) <= 0:
            vn.FAILS.append("s29: a certificate whose two ratios agree")
    if WID29 is not None and len(WID29):
        aff = WID29[WID29.is_affine]
        if len(aff):
            if float(aff.R_shift.max()) > 1e-9:
                vn.FAILS.append("s29: the wider witness's reduction is not "
                                "invariant under the affine family")
            if float(aff.m_changed.max()) < 1e-6:
                vn.FAILS.append("s29: the wider witness is rank-based after "
                                "all, so it witnesses nothing")

    # ---- s30: the pilot's variance ---------------------------------------
    P30 = load("s30_proportions.csv")
    if P30 is not None and len(P30):
        eq("auditDesignWidthPct",
           fmt_pct(float((P30.design_hi - P30.design_lo).median()), 0), M,
           "recomputed from the endpoints")
        eq("auditBootWidthPct",
           fmt_pct(float((P30.boot_hi - P30.boot_lo).median()), 0), M)
        eq("auditWilsonWidthPct",
           fmt_pct(float((P30.wilson_hi - P30.wilson_lo).median()), 0), M)

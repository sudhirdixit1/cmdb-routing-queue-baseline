"""round27_numbers -- THE QUANTITIES ROUND TWENTY-SEVEN'S NEW FILES PRODUCE.

Kept in its own module for the reason the round-twenty and round-twenty-one
modules are: the sources are disjoint from the rest, and a reader tracing one
of these numbers should land here rather than in the middle of a thousand-line
generator.  It writes into `make_numbers`'s macro table, so there is still one
writer of `numbers.tex` and one writer of each number.

Sources
    results/s44_facts.csv, s44_grid.csv     the designed inference surface
    results/s45_prefix.csv, s45_facts.csv   the prefix axis
    results/s46_summary.csv, s46_facts.csv  the stationarity diagnostic
    results/s47_*                           the two schemes compared
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def emit(mn):
    put, load, first = mn.put, mn.load, mn.first
    num, pct, sig, thousands = mn.num, mn.pct, mn.sig, mn.thousands

    # ================================================================
    # r34 -- the OTHER logs' layer ladders
    # ================================================================
    #  Round twenty-two corrected the article's claim that a register's coarse
    #  layers are "close to free": on the case study the item's type is worth
    #  a third to a half of what the item is worth.  The SUPPLEMENT's layer
    #  section still carried the withdrawn reading, and it carried it about a
    #  table holding three logs on which the answer differs.  The corrected
    #  statement needs the other two logs' numbers, so they are macros.
    R34 = load("r34_layers.csv")
    if R34 is not None and len(R34):
        def lay(log, target, level):
            s = R34[(R34.log == log) & (R34.target == target)
                    & (R34.level == level)]
            return float(s.gain_over_b0.iloc[0]) if len(s) else None

        put("layerHelpdeskCoarseMax",
            sig(max([v for v in (lay("Helpdesk", "duration", "service_type"),
                                 lay("Helpdesk", "duration",
                                     "support_section"))
                     if v is not None], default=None), 3))
        put("layerHelpdeskItem", sig(lay("Helpdesk", "duration", "product"), 3))
        put("layerBpicNineteenCoarseMax",
            sig(max([v for v in (lay("BPIC19", "handover",
                                     "case:Item Category"),
                                 lay("BPIC19", "handover",
                                     "case:Spend area text"))
                     if v is not None], default=None), 3))
        put("layerBpicNineteenItem",
            sig(lay("BPIC19", "handover", "case:Item"), 3))
        put("layerBpicNineteenItemMarginal",
            sig(lay("BPIC19", "handover",
                    "case:Item marginal over case:Item Category"), 3))
        #  the share of the item's increment the coarsest layer reaches, on
        #  the case study's two targets -- the quantity the withdrawn claim
        #  got wrong
        for tg, nm in (("handover", "Handover"), ("duration", "Duration")):
            it = lay("BPIC14", tg, "CI Name (aff)")
            ty = lay("BPIC14", tg, "CI Type (aff)")
            put("layerTypeSharePct" + nm,
                pct(ty / it, 0) if it and ty else None)
    else:
        for k in ("layerHelpdeskCoarseMax", "layerHelpdeskItem",
                  "layerBpicNineteenCoarseMax", "layerBpicNineteenItem",
                  "layerBpicNineteenItemMarginal",
                  "layerTypeSharePctHandover", "layerTypeSharePctDuration"):
            put(k, None)

    # ================================================================
    # s45 -- the prefix axis, on one log
    # ================================================================
    P = load("s45_prefix.csv")
    F = load("s45_facts.csv")
    if P is not None and len(P):
        P = P.sort_values("prefix")
        put("nPrefixLevels", int(len(P)))
        put("prefixMax", int(P.prefix.max()))
        put("prefixLog", str(P.log.iloc[0]).replace("_", "\\_"))
        put("nPrefixResolved", int(P.resolved.sum()))
        put("nPrefixUnresolved", int((~P.resolved.astype(bool)).sum()))
        put("nPrefixDraws", thousands(int(P.n_draws.max())))
        a = P[P.prefix == 0]
        if len(a):
            put("VPrefixZero", sig(float(a.V.iloc[0]), 3))
            put("VPrefixZeroLo", sig(float(a.lo.iloc[0]), 3))
            put("VPrefixZeroHi", sig(float(a.hi.iloc[0]), 3))
            put("nPrefixZero", thousands(int(a.n.iloc[0])))
            put("basePrefixZero", num(float(a.base_auc.iloc[0]), 3))
        for k in (2, 3, 8):
            r = P[P.prefix == k]
            nm = {2: "Two", 3: "Three", 8: "Eight"}[k]
            if len(r):
                put("VPrefix" + nm, sig(float(r.V.iloc[0]), 3))
                put("VPrefix" + nm + "Lo", sig(float(r.lo.iloc[0]), 3))
                put("VPrefix" + nm + "Hi", sig(float(r.hi.iloc[0]), 3))
                put("nPrefix" + nm, thousands(int(r.n.iloc[0])))
            else:
                for s in ("", "Lo", "Hi"):
                    put("VPrefix" + nm + s, None)
                put("nPrefix" + nm, None)
        #  the share of the creation-time increment the deepest prefix keeps,
        #  which is the number the PPM objection turns on
        put("prefixRetainedPct", pct(first(F, "share_of_creation_retained"), 0))
        put("prefixDropFactor",
            num(float(P[P.prefix == 0].V.iloc[0])
                / float(P[P.prefix == P.prefix.max()].V.iloc[0]), 1)
            if len(P[P.prefix == 0]) and float(
                P[P.prefix == P.prefix.max()].V.iloc[0]) != 0 else None)
        put("prefixVmin", sig(first(F, "v_min"), 3))
        put("prefixVmax", sig(first(F, "v_max"), 3))
    else:
        for k in ("nPrefixLevels", "prefixMax", "prefixLog", "nPrefixResolved",
                  "nPrefixUnresolved", "nPrefixDraws", "VPrefixZero",
                  "VPrefixZeroLo", "VPrefixZeroHi", "nPrefixZero",
                  "basePrefixZero", "prefixRetainedPct", "prefixDropFactor",
                  "prefixVmin", "prefixVmax"):
            put(k, None)
        for nm in ("Two", "Three", "Eight"):
            for s in ("", "Lo", "Hi"):
                put("VPrefix" + nm + s, None)
            put("nPrefix" + nm, None)

    # ================================================================
    # s41 -- THE NON-ZERO-TRUTH REGIME
    # ================================================================
    #  Round twenty-seven added a fourth coverage regime, and it is the one
    #  that speaks to a region label.  Under a zero truth every rejection is an
    #  error, so coverage there cannot distinguish a band that resolves
    #  CORRECTLY from one that never resolves at all.  With a heterogeneous
    #  non-zero truth a cell can be correctly resolved, and the family-wise
    #  coverage is then the quantity the label actually depends on.
    F41 = load("s41_facts.csv")
    if F41 is not None and len(F41) and "cov_q_mult_nonzero_median" in F41.columns:
        put("covMultNonzeroMedian", pct(first(F41, "cov_q_mult_nonzero_median"), 1))
        put("covMultNonzeroMin", pct(first(F41, "cov_q_mult_nonzero_min"), 1))
    else:
        put("covMultNonzeroMedian", None)
        put("covMultNonzeroMin", None)

    # ================================================================
    # s47 -- THE TWO RESAMPLING SCHEMES, COMPARED ON ONE DESIGN
    # ================================================================
    #  Section 11 named this comparison as owed and did not run it.  It is run
    #  now, and the macros are emitted in PAIRS so that no sentence can quote
    #  one scheme's number without its partner being available.
    #
    #  The comparison is not symmetric and the manuscript must say so.  When a
    #  draw produces no value for a cell, `s21_bands' refuses the cell and
    #  `s47' drops the missing draws and computes from what remains.  So every
    #  multinomial statistic below is conditioned on the draws in which the arm
    #  could be FITTED --- and those are not a random subset: the cells short
    #  of a full draw count carry roughly twice the displacement of the rest.
    #  The old scheme's numbers are therefore the flattered ones, which makes
    #  the smallness of the displacement difference more striking and not less.
    F47 = load("s47_facts.csv")
    if F47 is not None and len(F47):
        put("schemeCells", thousands(int(first(F47, "n_cells"))))
        put("levelShareMult", pct(first(F47, "level_share_multinomial"), 1))
        put("levelShareMultMin",
            pct(first(F47, "level_share_multinomial_min"), 1))
        put("levelShareWeighted", pct(first(F47, "level_share_weighted"), 0))
        put("nExcludesMult", thousands(int(first(F47, "n_excludes_multinomial"))))
        put("nExcludesWeighted", thousands(int(first(F47, "n_excludes_weighted"))))
        put("shareExcludesMultPct",
            pct(first(F47, "share_excludes_multinomial"), 1))
        put("shareExcludesWeightedPct",
            pct(first(F47, "share_excludes_weighted"), 1))
        put("dispMedianMult", num(first(F47, "displacement_median_multinomial"), 4))
        put("dispMedianWeighted", num(first(F47, "displacement_median_weighted"), 4))
        put("nResolvedSchemeMult", thousands(int(first(F47, "n_resolved_multinomial"))))
        put("nResolvedSchemeWeighted", thousands(int(first(F47, "n_resolved_weighted"))))
        put("schemeWidthRatio", num(first(F47, "width_ratio"), 3))
    else:
        for k in ("schemeCells", "levelShareMult", "levelShareMultMin",
                  "levelShareWeighted", "nExcludesMult", "nExcludesWeighted",
                  "shareExcludesMultPct", "shareExcludesWeightedPct",
                  "dispMedianMult", "dispMedianWeighted",
                  "nResolvedSchemeMult", "nResolvedSchemeWeighted",
                  "schemeWidthRatio"):
            put(k, None)

    # ================================================================
    # CELLS THAT CANNOT BE BANDED AT ALL
    # ================================================================
    #  Found in round twenty-seven by a gate written for another purpose.  A
    #  multinomial resample can lose enough register levels that an arm cannot
    #  be fitted in a draw at all, so the cell is ABSENT from that draw rather
    #  than merely noisy; the median down its column is then undefined and the
    #  cell gets no centre and no band.
    #
    #  Such a cell is not resolved, so every table counted it as UNRESOLVED --
    #  indistinguishable from a cell that was banded and straddled zero.  That
    #  put cells the data were never given a chance to resolve inside the
    #  denominator of every `the data resolve so little' statement.  The count
    #  is small and the paper's subject is denominators, which is exactly why
    #  it has to be a number in the manuscript rather than a silent zero.
    _bandfile = None
    for _cand in ("s48w_bands.csv.gz", "s21_bands.csv.gz"):
        if (mn.RESULTS / _cand).exists():
            _bandfile = _cand
            break
    if _bandfile:
        _b = pd.read_csv(mn.RESULTS / _bandfile)
        _w = _b[_b.family == "whole-surface"]
        _n = int(_w.sim_lo.isna().sum())
        put("nUnbandableCells", thousands(_n))
        #  the PREVIOUS surface's count, so Section 4.1 can quote both ends of
        #  the comparison without either being typed.  It is read from the old
        #  bands file, which the archive still carries.
        _old = mn.RESULTS / "s21_bands.csv.gz"
        if _old.exists():
            _ob = pd.read_csv(_old)
            _ow = _ob[_ob.family == "whole-surface"]
            put("nUnbandableOldCells", thousands(int(_ow.sim_lo.isna().sum())))
        else:
            put("nUnbandableOldCells", None)
        put("nUnbandablePairs",
            thousands(int(_w[_w.sim_lo.isna()]
                          .groupby(["log", "target"]).ngroups)))
    else:
        put("nUnbandableCells", None)
        put("nUnbandablePairs", None)
        put("nUnbandableOldCells", None)

    # ================================================================
    # s37 --itsm -- DOES `THE ENCODING BEATS THE FAMILY' TRAVEL?
    # ================================================================
    #  Section 11 conceded that the crossing runs on the case study's log
    #  alone.  It now runs on the eight ITSM pairs, and the answer is the one
    #  rule 2 predicts for a claim the paper likes: it PARTIALLY replicates.
    #  The encoding is the larger first-order axis on six of the eight, and on
    #  the other two the family is --- decisively, at four hundredths and a
    #  third of the encoding's share.  That is a better result than a clean
    #  replication would have been, because it is an instance of this paper's
    #  own thesis rather than an exception to it: WHICH AXIS LEADS IS A
    #  PROPERTY OF THE PAIR.
    #
    #  The aggregation is named because Section 6.2 insists it must be: this
    #  is the median over the five instruments WITHIN a pair, then a count
    #  over pairs.  It is not the pooled median the case-study macros use, and
    #  the two are not interchangeable.
    IDX = load("s37_indices_itsm.csv")
    if IDX is not None and len(IDX):
        def _per_pair(term):
            return (IDX[IDX.term == term].groupby(["log", "target"])
                    .share.median())
        fam, enc = _per_pair("family"), _per_pair("encoding")
        both = pd.concat([fam.rename("f"), enc.rename("e")], axis=1).dropna()
        put("nItsmCrossed", int(len(both)))
        put("nEncodingLargerItsm", int((both.e > both.f).sum()))
        put("nFamilyLargerItsm", int((both.f >= both.e).sum()))
        #  the two pairs that go the other way do so decisively, and saying
        #  so is what stops `six of eight' reading as a near-miss
        if (both.f >= both.e).any():
            worst = (both.e / both.f)[both.f >= both.e].min()
            put("encOverFamItsmMin", num(float(worst), 2))
        else:
            put("encOverFamItsmMin", None)
    else:
        for k in ("nItsmCrossed", "nEncodingLargerItsm", "nFamilyLargerItsm",
                  "encOverFamItsmMin"):
            put(k, None)

    # ================================================================
    # THE PLANNED CONTRASTS, COUNTED THE WAY THIS PAPER SAYS TO COUNT THEM
    # ================================================================
    #  Section 4.4 said five of five survive at alpha = 0.05, three lines above
    #  its own rule that A CONTRAST IS CALLED RESOLVED ONLY WHEN THE INTERVAL
    #  SAYS SO --- and it then says PC3's p-value and interval disagree.  So
    #  the paper printed the count its own rule rejects, and named the
    #  exception in the next sentence without changing the count.  Both counts
    #  are macros now: `nPlannedReject' is what the p-values give and
    #  `nPlannedResolved' is what the rule gives, and the prose prints the
    #  second as the one that follows from the paper's own definition.
    CN = load("s24_contrasts.csv")
    if CN is not None and len(CN) and {"basic_lo", "basic_hi"} <= set(CN.columns):
        excl = ((CN.basic_lo > 0) | (CN.basic_hi < 0))
        put("nPlannedResolved", thousands(int(excl.sum())))
    else:
        put("nPlannedResolved", None)

    # ================================================================
    # THE ESTATE'S OWN REGISTER CARDINALITY, AND THE TIE-BREAK IN SHARES
    # ================================================================
    #  Two findings of the same shape.  Section 7 quoted \cardF --- BPIC14's
    #  cardinality on the REGISTERED cohort --- while stating that every
    #  number in the section is on the ESTATE's cohort, whose register carries
    #  a different count at each decision time.  And the tie-break paragraph
    #  said `a quarter of the point estimate's own magnitude' about two
    #  different quantities: the range over 25 random tie orders, and the
    #  displacement the undeclared sort actually caused.  Neither is a
    #  quarter, and they are not each other.  Both are now shares of one
    #  declared denominator --- the increment the declared rules give --- so
    #  that `that magnitude' refers to one thing.
    F38 = load("s38_facts.csv")
    if F38 is not None and len(F38):
        put("cardTauTwo", thousands(int(first(F38, "card_t2"))))
    else:
        put("cardTauTwo", None)

    F32 = load("s32_facts.csv")
    C32 = load("s32_cells.csv")
    if F32 is not None and len(F32) and C32 is not None and len(C32):
        sel = C32[(C32.ordering == "identifier")
                  & (C32.cohort == "reassignment")
                  & (C32.target == "reassignment")
                  & (C32.rung == "B_intake_g_km")]
        if len(sel) == 1:
            #  the unrounded increment the declared rules give; the rounded
            #  display macro would put the shares out by two points
            v = abs(float(sel.V.iloc[0]))
            rng = float(first(F32, "tiebreak_range"))
            pub = float(first(F32, "v_published_case"))
            put("tiebreakRangeSharePct", pct(rng / v, 1))
            put("tiebreakShiftPct", pct(abs(pub - float(sel.V.iloc[0])) / v, 1))
        else:
            put("tiebreakRangeSharePct", None)
            put("tiebreakShiftPct", None)
    else:
        put("tiebreakRangeSharePct", None)
        put("tiebreakShiftPct", None)

    # ================================================================
    # THE REGION COUNTS DEFINITION 3 ACTUALLY YIELDS
    # ================================================================
    #  An internal audit found the supplement asserting that one conditionally
    #  harmful surface exists while the article's master table shows none.
    #  Both were right about their own object and the pair contradicted: the
    #  `Cal' counts are the region column of the calibrated-band table, which
    #  is the label BEFORE Definition 3's minimum resolved share, and the
    #  master table prints the label after it.  Four pairs lose a direction
    #  there, and one of them is the only conditionally harmful surface the
    #  band reaches --- so the two label systems disagree about whether this
    #  corpus contains any harmful surface at all.
    #
    #  Both sets of counts are now macros, so a sentence can say which system
    #  it is quoting instead of leaving a reader to discover that there are
    #  two.  The column name is built from the declared threshold rather than
    #  typed, so these track the convention if it ever moves.
    R42 = load("s42_regions.csv")
    F42 = load("s42_facts.csv")
    _MS = ("nCondBeneficialMinShare", "nSignChangingMinShare",
           "nCondHarmfulMinShare", "nUnresolvedMinShare")
    if R42 is not None and len(R42) and F42 is not None and len(F42):
        thr = float(first(F42, "min_resolved_declared"))
        col = "region_min%02d" % int(round(thr * 100))
        if col in R42.columns:
            lab = R42[col].astype(str)
            put("nCondBeneficialMinShare",
                int((lab == "conditionally beneficial").sum()))
            put("nSignChangingMinShare", int((lab == "sign-changing").sum()))
            put("nCondHarmfulMinShare",
                int((lab == "conditionally harmful").sum()))
            #  a withdrawn direction is unresolved, and the file spells the
            #  two states differently, so both count here
            put("nUnresolvedMinShare",
                int(lab.str.startswith("unresolved").sum()))
        else:
            for k in _MS:
                put(k, None)
    else:
        for k in _MS:
            put(k, None)

    #  The single conditionally harmful surface the calibrated band reaches,
    #  by the counts it rests on.  Section 4.6 used to assert the label's
    #  existence without them, which put the article body at odds with its own
    #  master table; the counts are what make the withdrawal legible rather
    #  than a second opinion.
    if R42 is not None and len(R42):
        _h = R42[R42.log.astype(str).str.contains("Helpdesk", case=False,
                                                  na=False)]
        if len(_h) == 1:
            _r = _h.iloc[0]
            put("nHelpdeskResolved",
                thousands(int(_r.beneficial_cal) + int(_r.harmful_cal)))
            put("nHelpdeskFamily", thousands(int(_r.n_family)))
        else:
            put("nHelpdeskResolved", None)
            put("nHelpdeskFamily", None)
    else:
        put("nHelpdeskResolved", None)
        put("nHelpdeskFamily", None)

    # ================================================================
    # HOW MANY TABLES THE ARTICLE PRINTS
    # ================================================================
    #  The supplement said "the seven tables a reader needs" while the article
    #  printed eight.  texlint's spelled-out-count check does not fire on this
    #  shape, and a hard-coded 8 goes stale exactly as `seven' did, so the
    #  count is taken from the source: the article's own body parts, which are
    #  the numbered ones -- an appendix's tables are not the article's.
    try:
        import re as _re
        #  mn.PAPER, not a path built from the repo root: the corruption tests
        #  redirect it, and a checker that reads the real tree while the
        #  suite corrupts a copy is a hole this project has had before.
        _parts = sorted((mn.PAPER / "parts").glob("[0-9]*.tex"))
        _n = sum(len(_re.findall(r"\\input\{tables/", p.read_text(
            encoding="utf-8", errors="ignore"))) for p in _parts)
        put("nArticleTables", int(_n) if _n else None)
    except Exception:
        put("nArticleTables", None)

    # ================================================================
    # s49 -- THE DECISION-CURVE BAND, WIDENED BY ITS MEASURED SHORTFALL
    # ================================================================
    #  Section 10.4 measured that the decision-curve families need a
    #  multiplicative widening of about two, and Section 8.3 printed counts
    #  from a band that had not received it -- then told the reader in
    #  Section 11 to distrust them.  Unlike the resampling repair this one
    #  never had a cost defence: widening an already-computed critical value
    #  is arithmetic on draws that exist.  s49 applies it.
    #
    #  WHICH FACTOR, AND WHY IT IS NOT THE RATIO.  `ratio_dca_all' and
    #  `ratio_dca_adm' are medians of q_emp/q -- a ratio of two marginal
    #  quantiles -- and s41 carries a comment recording that an earlier
    #  version applied one and was wrong, because q and t_max are estimated
    #  from the same draws and move together.  The factor that attains the
    #  level is the within-replicate quantile of t_max/q, which is
    #  `shortfall_factor'.  The choice is therefore between s41's REGIMES,
    #  and this family is measured into one rather than assigned to it: 2 of
    #  its 248 cells are degenerate against a corpus maximum of 17.2%, and
    #  its excess kurtosis matches the `heavy' regime, so the heavy factor
    #  applies and the degenerate one is reported beside it.
    F49 = load("s49_facts.csv")
    if F49 is not None and len(F49):
        put("dcaQWidened", num(first(F49, "q_widened"), 2))
        put("dcaWidenFactor", num(first(F49, "factor_applied"), 2))
        put("dcaWidenFactorAll", num(first(F49, "factor_all_cells"), 2))
        put("nBeneficialSimultaneousWidened",
            thousands(int(first(F49, "n_beneficial_sim_widened"))))
        put("nBeneficialSimultaneousAllCells",
            thousands(int(first(F49, "n_beneficial_sim_all_cells"))))
        put("nHarmfulSimultaneousWidened",
            thousands(int(first(F49, "n_harmful_sim_widened"))))
        put("nBeneficialLostToWidening",
            thousands(int(first(F49, "n_beneficial_lost_to_widening"))))
        put("thetaBeneficialWidenedMin",
            num(first(F49, "theta_min_beneficial_widened"), 2))
        put("dcBandWidthWidened", num(first(F49, "width_sim_widened"), 4))
        put("nDegenerateCellsBand",
            thousands(int(first(F49, "n_degenerate_band"))))
        #  the whole 248-cell family, for the supplement's band section
        put("dcaHarmfulSimultaneousWidened",
            thousands(int(first(F49, "n_family_harmful_widened"))))
        put("dcaBeneficialSimultaneousWidened",
            thousands(int(first(F49, "n_family_beneficial_widened"))))
        put("dcaDipThetaWidened", num(first(F49, "dip_theta_widened"), 3))
        put("dcaDipValueWidened", num(first(F49, "dip_value_widened"), 4))
    else:
        for k in ("dcaQWidened", "dcaWidenFactor", "dcaWidenFactorAll",
                  "nBeneficialSimultaneousWidened",
                  "nBeneficialSimultaneousAllCells",
                  "nHarmfulSimultaneousWidened", "nBeneficialLostToWidening",
                  "thetaBeneficialWidenedMin", "dcBandWidthWidened",
                  "nDegenerateCellsBand", "dcaHarmfulSimultaneousWidened",
                  "dcaBeneficialSimultaneousWidened", "dcaDipThetaWidened",
                  "dcaDipValueWidened"):
            put(k, None)

    # ================================================================
    # s46 -- is the increment stationary across the test half?
    # ================================================================
    D = load("s46_summary.csv")
    DF = load("s46_facts.csv")
    if D is not None and len(D):
        put("nDriftPairs", int(len(D)))
        put("nDriftBlocks", int(first(DF, "n_blocks")))
        put("nDriftPerm", thousands(int(first(DF, "n_perm"))))
        put("nDrifts", int(first(DF, "n_drifts")))
        put("nDriftSignVaries", int(first(DF, "n_sign_varies_across_blocks")))
        put("nDriftTrend", int(first(DF, "n_trend_significant")))
        put("driftSpreadMedian", sig(first(DF, "spread_median"), 3))
        put("driftSpreadMax", sig(first(DF, "spread_max"), 3))
        put("driftOverNullMedian", num(first(DF, "spread_over_null_median"), 2))
        put("driftOverNullMax", num(first(DF, "spread_over_null_max"), 1))
        put("nDriftAboveNullMedian",
            int(first(DF, "n_pairs_above_null_median")))
        put("driftPrevSpreadMedian", num(first(DF, "prevalence_spread_median"), 2))
        put("driftPrevSpreadMax", num(first(DF, "prevalence_spread_max"), 2))
        put("driftUnseenFirstPct", pct(first(DF, "unseen_first_median"), 1))
        put("driftUnseenLastPct", pct(first(DF, "unseen_last_median"), 1))
        dr = D[D.drifts.astype(bool)].sort_values("spread", ascending=False)
        put("driftWorstPair",
            ("%s/%s" % (str(dr.log.iloc[0]).replace("_", "\\_"),
                        dr.target.iloc[0])) if len(dr) else None)
    else:
        for k in ("nDriftPairs", "nDriftBlocks", "nDriftPerm", "nDrifts",
                  "nDriftSignVaries", "nDriftTrend", "driftSpreadMedian",
                  "driftSpreadMax", "driftOverNullMedian", "driftOverNullMax",
                  "nDriftAboveNullMedian", "driftPrevSpreadMedian",
                  "driftPrevSpreadMax", "driftUnseenFirstPct",
                  "driftUnseenLastPct", "driftWorstPair"):
            put(k, None)


def tables(mn):
    """The two tables the new evidence needs.  Written here because the data
    are here; the supplement inputs them by name."""
    load, TABLES, tex_table = mn.load, mn.TABLES, mn.tex_table
    fmt = mn.fmt_fixed

    P = load("s45_prefix.csv")
    if P is not None and len(P):
        d = P.sort_values("prefix").copy()
        d["interval"] = ["[%+.3f, %+.3f]" % (a, b) for a, b in zip(d.lo, d.hi)]
        d = d[["prefix", "n", "prevalence_test", "card_register", "base_auc",
               "with_auc", "V", "interval", "resolved"]]
        (TABLES / "prefix.tex").write_text(
            tex_table(d,
                      "A PREFIX AXIS ON ONE LOG. At prefix $k$ the analyst "
                      "stands after the case's $k$-th assignment event: the "
                      "population is the cases still at risk --- more than "
                      "$k$ events and no group change yet --- the target is "
                      "whether a change occurs AFTER event $k$, and the "
                      "baseline is the intake block plus what the prefix has "
                      "revealed. $k = 0$ is case creation, which is the "
                      "prediction point every other result in this paper "
                      "uses, and it is the anchor the rest are read against. "
                      "Every interval is the pointwise basic construction "
                      "under the block-weighted bootstrap at "
                      "\\nPrefixDraws\\ draws.",
                      "tab:prefix",
                      colnames={"prevalence_test": "prevalence",
                                "card_register": "register levels",
                                "base_auc": "base auc",
                                "with_auc": "with auc"}),
            encoding="utf-8")

    D = load("s46_summary.csv")
    if D is not None and len(D):
        d = D.sort_values(["log", "target"]).copy()
        d["log"] = d.log.astype(str).str.replace("_", "\\_", regex=False)
        d["range over blocks"] = ["[%+.3f, %+.3f]" % (a, b)
                                  for a, b in zip(d.V_min, d.V_max)]
        d["spread"] = [fmt(v, 3) for v in d.spread]
        d["null median"] = [fmt(v, 3) for v in d.spread_null_median]
        d["percentile"] = [fmt(100 * v, 1) for v in d.spread_percentile]
        d["V"] = [fmt(v, 3) for v in d.V_whole]
        d["trend"] = [fmt(v, 2) for v in d.trend_rho]
        cols = ["log", "target", "V", "range over blocks", "spread",
                "null median", "percentile", "trend", "sign_varies", "drifts"]
        (TABLES / "drift.tex").write_text(
            tex_table(d[cols],
                      "IS THE INCREMENT STATIONARY ACROSS THE TEST HALF? The "
                      "reference cell's model is fitted once on the training "
                      "half and evaluated on the test half cut into "
                      "\\nDriftBlocks\\ consecutive blocks in time. `spread' "
                      "is the range of the per-block increment; `null median' "
                      "is the median spread over \\nDriftPerm\\ RANDOM "
                      "re-partitions of the same rows into blocks of the same "
                      "sizes, which destroys the time order and nothing else; "
                      "`percentile' places the observed spread in that "
                      "reference. A block is a fifth of the test half and so "
                      "carries more sampling error than the whole, which is "
                      "why the comparison is against the null and not against "
                      "the pair's own interval. `trend' is the Spearman "
                      "correlation of the increment with the block index: it "
                      "separates drift, which has an order, from "
                      "heterogeneity, which does not. `drifts' marks a "
                      "percentile in the null's upper tail at the declared "
                      "level $\\alpha = 0.05$.",
                      "tab:drift",
                      colnames={"sign_varies": "sign varies"}),
            encoding="utf-8")

"""round26_numbers -- the macros and tables round twenty-six adds.

The sixth referee's Phase A items A3, A4 and A5, its Phase B item B3 and its
major comment M5 are computed by `s42_round26.py`; this file turns those five
result files into macros and into the three tables the report asks to be moved
or created in the main text.  It is a separate module for the reason round
twenty's and round twenty-one's are: `make_numbers.py` is long enough, and
these read a disjoint set of sources.

Every macro resolves to the visible `??' marker when its result file is
absent, so a partial build is visibly partial rather than quietly wrong.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

#: how a rung is named in a table column
_RUNG = {"B_half": "half of intake", "B_intake": "intake",
         "B_intake_g": "intake + free field",
         "B_intake_g_km": "+ knowledge ref."}

#: THE AFFILIATION.  The Guide for Authors asks for a city and a country and
#: the sixth referee found neither.  They are not derivable from any result
#: file, so they are declared here, in the one place the manuscript reads its
#: names and numbers from.  Setting either to None resolves it to the visible
#: ?? marker, exactly as a missing result does, so an omission would be on the
#: page rather than in a checklist.
AFFILIATION_CITY = "Apex"
AFFILIATION_COUNTRY = "United States"


def emit(mn):
    put, load, pct, num, sig = mn.put, mn.load, mn.pct, mn.num, mn.sig
    thousands = mn.thousands

    F = load("s42_facts.csv")
    P = load("s42_strata.csv")
    FA = load("s42_foldavg.csv")
    M = load("s42_mpid.csv")
    AX = load("s42_axes.csv")
    RG = load("s42_regions.csv")
    SP = load("s42_spread.csv")

    put("affiliationCity", AFFILIATION_CITY)
    put("affiliationCountry", AFFILIATION_COUNTRY)

    #  M2.  THE REFIT'S JUSTIFICATION, IN THE UNITS THE SIMULATION RESOLVES.
    #  Section 4.1 quoted two coverages a percentage point apart and let the
    #  larger one justify the design.  The sixth referee measured the gap
    #  against the Monte Carlo standard error the paper itself states, and it
    #  is not a difference.  Both numbers come from the same file as the
    #  standard error, so the ratio cannot be quoted against the wrong run.
    F31 = load("s31_facts.csv")
    if F31 is not None and len(F31):
        n_core = mn.first(F31, "n_reps_core")
        a = mn.first(F31, "cov_nested_basic_median")
        b = mn.first(F31, "cov_naive_pct_median")
        if all(v is not None and np.isfinite(float(v))
               for v in (n_core, a, b)) and float(n_core) > 0:
            se = float(np.sqrt(0.95 * 0.05 / float(n_core)))
            put("nestedGainInSe", num(abs(float(a) - float(b)) / se, 1))
            put("simMcSe", pct(se))

    def fact(name, default=None):
        if F is None or name not in F.columns or not len(F):
            return default
        v = F[name].iloc[0]
        return None if pd.isna(v) else v

    # ==================================================================
    # A3 -- the split as an error stratum
    # ==================================================================
    #  The four shares partition the POOLED variance exactly.  Each macro is
    #  the median over pairs of the median over instruments, which is the
    #  aggregation Section 6.2 already uses for every other index, so the two
    #  decompositions can be read down the same column.
    put("shareAnalystStratumPct", pct(fact("share_analyst_median")))
    put("shareCounterfactualStratumPct",
        pct(fact("share_counterfactual_median")))
    put("shareMixedStratumPct", pct(fact("share_mixed_median")))
    put("shareResamplingStratumPct", pct(fact("share_resampling_median")))
    put("shareResamplingRollingPct",
        pct(fact("share_resampling_rolling_median")))
    put("shareAnalystRollingPct", pct(fact("share_analyst_rolling_median")))
    put("nResamplingLargest", fact("n_resampling_largest"))
    #  the identity is asserted numerically, as the pooled decomposition's is
    put("stratumPartitionError", mn.sci(fact("partition_max_error")))

    #  on the fold-averaged surface: the indices a reader who wants to know
    #  which ANALYST choice moves the answer should be given
    put("foldInteractionTotalPct", pct(fact("foldavg_interaction_median")))
    put("foldLargestFirstOrderPct",
        pct(fact("foldavg_largest_first_median")))
    put("foldVarRatioPct", pct(fact("var_ratio_median")))
    if FA is not None and len(FA):
        fa = FA[FA.split_set == "all"] if "split_set" in FA.columns else FA
        per = fa.groupby(["log", "target"]).median(numeric_only=True)
        for macro, col in (("foldSPipelinePct", "S_learner"),
                           ("foldSQualityPct", "S_quality"),
                           ("foldSRungPct", "S_rung")):
            put(macro, pct(float(per[col].median())))
        #  which axis leads on the fold-averaged surface, and on how many
        #  pairs the corpus's own answer is not the same one
        lead = (fa.groupby(["log", "target"]).largest_first_order_axis
                .agg(lambda s: s.value_counts().idxmax()))
        put("nFoldLeadPairsRung", int((lead == "rung").sum()))
        put("nFoldLeadPairsQuality", int((lead == "quality_level").sum()))
        put("nFoldLeadPairsPipeline", int((lead == "learner").sum()))
        #  DOES THE HEADLINE SURVIVE?  On the pooled surface the higher-order
        #  share exceeds the largest first-order index at the median pair.
        #  Net of resampling it does not, and the count says on how many
        #  pairs, because a median is not a vote.
        big = per.interaction_total > per.largest_first_order
        put("nFoldInteractionExceeds", int(big.sum()))
        put("nFoldPairs", int(len(per)))
        #  and the same count on the POOLED surface, computed here from the
        #  same aggregation so that the two are comparable pair for pair.  A
        #  claim that reverses is worth a count and not only two medians.
        SM = load("s22_summary.csv")
        if SM is not None and len(SM):
            #  THE BASIS HAS TO BE THE CANONICAL ONE.  s22_summary carries a
            #  sixth `metric' group, ALL_SCALAR -- the demoted
            #  cross-instrument headroom scale -- and including it moves the
            #  pooled medians to 52.5% and 29.1%, which is NOT what
            #  \interactionTotalPct and \largestFirstOrderPct hold.  Two
            #  numbers for one idea is the defect this repository has a
            #  registry for; the filter below reproduces the canonical
            #  56.0% and 28.7%, and round21_verify.ESTIMANDS now enforces it.
            e = SM[(SM.measure == "equal-level")
                   & (SM.metric.astype(str) != "ALL_SCALAR")]
            pooled = e.groupby(["log", "target"]).median(numeric_only=True)
            put("nPooledInteractionExceeds",
                int((pooled.interaction_total
                     > pooled.largest_first_order).sum()))
            put("pooledInteractionMedianPct",
                pct(float(pooled.interaction_total.median())))
            put("pooledLargestFirstMedianPct",
                pct(float(pooled.largest_first_order.median())))

    # ==================================================================
    # A4 -- the minimal practically important difference
    # ==================================================================
    put("mpidAuc", num(fact("mpid_auc"), 2))
    put("nRefBelowMpid", fact("n_ref_below_mpid"))
    put("nRefUnresolvedCell", fact("n_ref_unresolved"))
    if M is not None and len(M):
        n_auc = int(M.n_auc_cells.sum())
        n_mpid = int(M.n_cells_mpid.sum())
        n_res = int(M.n_resolved_auc.sum())
        n_res_mpid = int(M.n_resolved_mpid.sum())
        d_auc = int(M.n_disagree_auc.sum())
        d_mpid = int(M.n_disagree_mpid.sum())
        d_res = int(M.n_disagree_resolved_auc.sum())
        d_res_mpid = int(M.n_disagree_resolved_mpid.sum())
        put("nCellsAuc", thousands(n_auc))
        put("nCellsAboveMpid", thousands(n_mpid))
        put("nCellsResolvedAuc", n_res)
        put("nCellsResolvedMpid", n_res_mpid)
        put("nDisagreeAuc", thousands(d_auc))
        put("nDisagreeMpid", d_mpid)
        put("nDisagreeResolvedAuc", d_res)
        put("nDisagreeResolvedMpid", d_res_mpid)
        put("misreportAucAllPct", pct(d_auc / n_auc) if n_auc else None)
        put("misreportAucMpidPct", pct(d_mpid / n_mpid) if n_mpid else None)
        put("misreportAucResolvedPct", pct(d_res / n_res) if n_res else None)
        put("misreportAucResolvedMpidPct",
            pct(d_res_mpid / n_res_mpid) if n_res_mpid else None)
        put("shareCellsAboveMpidPct", pct(n_mpid / n_auc) if n_auc else None)
        #  THE MAGNITUDE, WHICH IS NOT A RATE.  The referee's objection is
        #  that a sign flip near zero is not worth acting on; the answer to
        #  it is not another rate but the distance itself.
        #  ALL THREE RESTRICTIONS AT ONCE.  Section 6.4 imposes two and calls
        #  the joint rate the one its argument asks for; the MPID is a third
        #  of the same kind, and the argument does not stop at two.
        n_full = int(M.n_full.sum())
        d_full = int(M.n_disagree_full.sum())
        put("nCellsFullyRestricted", n_full)
        put("nDisagreeFullyRestricted", d_full)
        put("misreportFullyRestrictedPct",
            pct(d_full / n_full) if n_full else None)
        put("madFullyRestrictedMedian", num(float(M.mad_full.median()), 4))
        put("madResolvedMedian", num(float(M.mad_resolved.median()), 4))
        put("madResolvedMax", num(float(M.mad_resolved.max()), 4))
        put("madAllMedian", num(float(M.mad_all.median()), 4))
        put("nPairsRefResolved", int(M.reference_resolved.sum()))

    #  WHERE THE POOLED RESOLVED-CELL RATE LIVES.  It is quoted over five
    #  instruments; the MPID can only be applied to one of them, so a reader
    #  comparing the two is owed the per-instrument rates or they will read
    #  the instrument's contribution as the MPID's.
    BI = load("s42_instrument.csv")
    if BI is not None and len(BI):
        g = BI.groupby("metric")[["n_resolved", "n_disagree_resolved"]].sum()
        g["rate"] = g.n_disagree_resolved / g.n_resolved.replace(0, np.nan)
        g = g.dropna(subset=["rate"])
        if len(g):
            put("misreportResolvedInstrumentMinPct",
                pct(float(g.rate.min())))
            put("misreportResolvedInstrumentMaxPct",
                pct(float(g.rate.max())))
            put("instrumentLeastDisagreement",
                {"auc": "ROC AUC", "ap": "average precision",
                 "brier_skill": "Brier skill",
                 "logloss_skill": "log-loss skill",
                 "nagelkerke": "Nagelkerke $R^2$"}.get(
                     str(g.rate.idxmin()), str(g.rate.idxmin())))
            put("instrumentMostDisagreement",
                {"auc": "ROC AUC", "ap": "average precision",
                 "brier_skill": "Brier skill",
                 "logloss_skill": "log-loss skill",
                 "nagelkerke": "Nagelkerke $R^2$"}.get(
                     str(g.rate.idxmax()), str(g.rate.idxmax())))

    # ==================================================================
    # B3 -- the resolution triple and the minimum resolved share
    # ==================================================================
    put("minResolvedSharePct", pct(fact("min_resolved_declared"), 0))
    put("nLabelsLostToMinShare", fact("n_labels_lost_to_min_share"))
    if RG is not None and len(RG):
        put("resolvedShareMedianPct", pct(float(RG.share_resolved.median())))
        put("resolvedShareMaxPct", pct(float(RG.share_resolved.max())))
        #  ROUND TWENTY-SEVEN, S10.  A SIGN-CHANGING LABEL CARRIES NO
        #  DIRECTION.  This counted every pair whose label is not
        #  `unresolved', which is thirteen, and the three sign-changing pairs
        #  are inside that thirteen.  Four sentences in the manuscript --- the
        #  master table's caption, the triple table's caption below,
        #  Definition 3's paragraph and the limitations --- read
        #  "\nLabelsLostToMinShare of the \nDirectionalLabels pairs THAT
        #  CARRY A DIRECTION", so each of them printed a denominator over a
        #  set three larger than the set the words describe.  A direction is a
        #  sign, and only the two labels that name a sign carry one: the
        #  conditionally beneficial and the conditionally harmful.  The
        #  numerator was never wrong -- all four withdrawals come out of that
        #  set -- so only the denominator moves, from thirteen to ten.
        _DIRECTIONAL = ("conditionally beneficial", "conditionally harmful")
        d = RG[RG.region_calibrated.astype(str).isin(_DIRECTIONAL)]
        put("nDirectionalLabels", int(len(d)))
        #  and the numerator is recounted over THE SAME ROWS as the
        #  denominator rather than read from a separate total, so a count
        #  taken over one set can never again be printed against a total
        #  taken over another.  It agrees with `n_labels_lost_to_min_share'
        #  in the facts file, which is what this macro was read from above.
        if len(d) and "changed_min05" in RG.columns:
            put("nLabelsLostToMinShare", int(d.changed_min05.sum()))
        if len(d):
            put("resolvedShareDirectionalMinPct",
                pct(float(d.share_resolved.min())))
        #  A LaTeX control sequence cannot contain a digit, so these are
        #  spelled out.  `\nLabelsLostMin01' parses as `\nLabelsLostMin'
        #  followed by the characters 01, which is a build failure at best
        #  and a silent wrong number at worst.
        for th, word in ((1, "One"), (10, "Ten")):
            c = "changed_min%02d" % th
            if c in RG.columns:
                put("nLabelsLostMin" + word, int(RG[c].sum()))

    # ==================================================================
    # M5 -- the baseline spread over rungs an analyst would build
    # ==================================================================
    put("spreadRealisticMedian", num(fact("spread_realistic_median"), 4))
    put("spreadRealisticMax", num(fact("spread_realistic_max"), 4))
    put("nSpreadExceedsRealistic", fact("n_exceeds_realistic"))
    if SP is not None and len(SP):
        put("nPairsTwoRealisticRungs",
            int((SP.n_rung_realistic == 2).sum()))
        put("nPairsThreeRealisticRungs",
            int((SP.n_rung_realistic >= 3).sum()))

    #  Section 5.3: the exclusion a reader of the roles table will ask about,
    #  from the exclusion file rather than from a sentence.
    EX = load("r33_excluded.csv")
    if EX is not None and len(EX):
        r = EX[EX.log.astype(str) == "BPIC15_2"]
        if len(r):
            d = str(r.detail.iloc[0])
            put("nBpicFifteenTwoRows",
                thousands(float(d.split("=")[-1].replace(",", "")))
                if "=" in d else None)

    #  Section 6.5 and 6.6: two quantities a referee had to compute for
    #  themselves because the manuscript printed the inputs and not the
    #  conclusion.  The permutation budget's p-value floor is (1)/(B+1) under
    #  the same plus-one estimator section 4.4 uses; the out-of-sample gap is
    #  the difference the sentence is about.
    SCA = load("s36_facts.csv")
    if SCA is not None and len(SCA) and "n_perms" in SCA.columns:
        perms = float(SCA.n_perms.iloc[0])
        if np.isfinite(perms) and perms > 0:
            put("scaPFloor", num(1.0 / (perms + 1.0), 3))
    NB = load("s23_facts.csv")
    if (NB is not None and len(NB)
            and {"oos_one_number_auc", "oos_mean_auc"} <= set(NB.columns)):
        put("oosMeanVsOneNumber",
            num(float(NB.oos_one_number_auc.iloc[0])
                - float(NB.oos_mean_auc.iloc[0]), 5))

    #  Section 9.3.  The referee asked whether two indices printed identically
    #  to three figures were a copy error.  They are not -- they differ in the
    #  fourth -- and the way to show that is to print the fourth rather than to
    #  assert it, so these two macros exist beside the rounded pair.
    S14 = load("s14_facts.csv")
    if S14 is not None and len(S14):
        for macro, col in (("exSbaselineFine", "S_baseline"),
                           ("exSmetricFine", "S_metric")):
            if col in S14.columns:
                put(macro, pct(float(S14[col].iloc[0]), 2))

    #  The calibration-slope window was a literal typed inside `$...$', which
    #  is the one place the no-typed-numbers rule does not look --- the same
    #  hole round twenty-five found in section 10.3.  It is a macro now, and
    #  it is the interval the exclusion rule in s26 actually applies.
    put("calSlopeWindow", "$[0.5, 2]$")

    #  M8.  The layer result moves into the main text, so the cardinality of
    #  each layer has to be a macro rather than a number typed beside it.
    LY = load("r34_layers.csv")
    if LY is not None and len(LY) and "level" in LY.columns:
        b14 = LY[(LY.log == "BPIC14") & (LY.target == "handover")]
        for macro, name in (("nLayerTypeLevels", "CI Type (aff)"),
                            ("nLayerSubtypeLevels", "CI Subtype (aff)")):
            r = b14[b14.level.astype(str) == name]
            put(macro, thousands(float(r.cardinality.iloc[0]))
                if len(r) and "cardinality" in r.columns else None)

    # ==================================================================
    # A5 -- the per-pair axis inventory
    # ==================================================================
    if AX is not None and len(AX):
        #  Figure 1's cell count, and the product that gives it.  A referee
        #  had to reconstruct the arithmetic from five numbers scattered
        #  across two sections; the caption now states it, from the design
        #  space rather than from a sentence.
        one = AX[(AX.log == "BPIC14") & (AX.target == "handover")]
        if len(one):
            r = one.iloc[0]
            #  NOT \nPipelines, which is the CROSSED factorial (families x
            #  encodings x targets) and is three times this.  A caption that
            #  multiplied the wrong one printed a product that missed its own
            #  stated total by a factor of three.
            put("nPipelineLevelsCase", int(r.n_pipeline))
            put("nRungsFigOne", int(r.n_rung))
            put("nQualityFigOne", int(r.n_quality))
            put("nCellsFigOne", thousands(int(r.n_pipeline) * int(r.n_rung)
                                          * int(r.n_quality)
                                          * int(r.n_split)
                                          * int(r.n_instrument)))
        #  M16 and section 5.3: how much of the corpus's cell count one pair
        #  carries.  A pooled corpus statistic is partly a statement about it.
        cells = (AX.n_pipeline * AX.n_split * AX.n_quality * AX.n_rung
                 * AX.n_instrument)
        b14 = cells[(AX.log == "BPIC14")]
        if len(b14):
            put("nCellsBpicFourteen", thousands(int(b14.sum())))
        #  ONE PAIR IS NOT ONE LOG.  Section~\\ref{sec:design} and
        #  Section~\\ref{sec:lim} both say "that pair carries N of the
        #  corpus's admissible cells" about the REGISTERED HANDOVER TARGET,
        #  and both printed the log's total -- the sum over its two targets,
        #  which is twice the pair's.  The pair's own count is its own macro.
        b14h = cells[(AX.log == "BPIC14") & (AX.target == "handover")]
        put("nCellsBpicFourteenHandover",
            thousands(int(b14h.sum())) if len(b14h) else None)
        put("nPairsFourPipelines", int((AX.n_pipeline == 4).sum()))
        put("nPairsThreePipelines", int((AX.n_pipeline == 3).sum()))
        put("nPairsFourRungs", int((AX.n_rung >= 4).sum()))
        put("nPerPairAxes", 5)
        put("cardFMedian", thousands(float(AX.card_f.median())))
        put("cardFMax", thousands(float(AX.card_f.max())))

    # ==================================================================
    # the three tables the report asks for in the main text
    # ==================================================================
    _tables(mn, AX, P, M, RG)


# --------------------------------------------------------------------------
#: C2.  THE GLOSSARY.  The sixth referee's complaint was that the manuscript
#: runs a private vocabulary --- register, free field, intake block, rung,
#: instrument, cell, surface, resolved, family --- and never collects it.  The
#: third column is the case study's own value for the term, because a
#: definition a reader cannot instantiate is a second definition to remember.
GLOSSARY = [
    ("register $f$", "the recorded field whose worth is in question: "
     "high-cardinality, maintained, reused across cases",
     "the affected configuration item"),
    ("free field $g$", "a resource-like field that is recorded anyway and "
     "that the register has to beat", "the assignment group"),
    ("intake block $B_0$", "what is known when the case arrives, excluding "
     "the register and the free field",
     "category, impact, urgency, priority"),
    ("rung", "one baseline in the nested ladder $B_0 \\subset B_1 \\subset "
     "\\cdots$ the increment is measured against",
     "intake $+$ group $+$ knowledge reference"),
    ("instrument", "the scalar metric an increment is read in; five are "
     "declared and they are not on a common scale", "ROC AUC"),
    ("cell", "one complete assignment to every varied axis: a point of the "
     "surface", "one-hot logistic, holdout, clean register, intake $+$ "
     "group, AUC"),
    ("specification surface", "the map from cells to increments over a "
     "declared design space", "the \\nCellsFigOne\\ cells of Figure~1"),
    ("declared / computational / inference surface",
     "what is admissible, what was computed, and what carries bootstrap "
     "draws --- three denominators, audited apart",
     "\\nDeclaredAdmissibleScalar, the same, and \\nInferenceScalar"),
    ("resolved", "the cell's simultaneous band excludes zero, so the data "
     "determine the sign of that cell's increment",
     "\\nCellsResolvedAuc\\ of \\nCellsAuc\\ AUC cells corpus-wide"),
    ("family $\\mathcal{F}$", "the set of cells a claim quantifies over, "
     "which is what a simultaneous band must cover",
     "a median \\familySizeMedian\\ cells per pair"),
    ("resolution region", "the label a surface earns from its resolved "
     "cells: uniformly or conditionally beneficial or harmful, "
     "sign-changing, unresolved", "sign-changing"),
    ("robustness index $\\rho$", "(beneficial $-$ harmful) $/\\,|\\mathcal{F}|$, "
     "always printed with the counts behind it", "see Table~\\ref{tab:triple}"),
    ("MPID", "the minimal practically important difference, declared before "
     "any disagreement is counted", "\\mpidAuc\\ AUC"),
]


def _tables(mn, AX, P, M, RG):
    tex_table, TABLES = mn.tex_table, mn.TABLES

    #  ---- C2: the glossary ------------------------------------------------
    #  Written directly rather than through tex_table, because every cell is
    #  LaTeX the escaper would break -- a $\mathcal{F}$ escaped is a dollar
    #  sign and a backslash on the page.
    rows = "\n".join(
        "%s & %s & %s \\\\[2pt]" % (t, d, e) for t, d, e in GLOSSARY)
    (TABLES / "glossary.tex").write_text(
        "\\begin{table}[t]\n\\centering\\footnotesize\n"
        "\\setlength{\\tabcolsep}{5pt}%\n"
        "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{0.20\\linewidth}"
        ">{\\raggedright\\arraybackslash}p{0.44\\linewidth}"
        ">{\\raggedright\\arraybackslash}p{0.28\\linewidth}}\n"
        "\\toprule\nterm & what it means & on the case study's log \\\\\n"
        "\\midrule\n" + rows + "\n\\bottomrule\n\\end{tabular}\n"
        "\\caption{THE VOCABULARY, IN ONE PLACE. Every term this paper uses "
        "in a sense a reader could not guess, with the case study's own value "
        "for it. The terms are defined again where they are first used; this "
        "table exists so that a reader who meets one in Section~"
        "\\ref{sec:multilog} does not have to find that place.}\n"
        "\\label{tab:glossary}\n\\end{table}\n", encoding="utf-8")

    #  ---- A5 + M7: roles and levels, per pair, in the MAIN TEXT ----------
    #  This is Supplement Table S11 and the axis inventory in one object.  A
    #  reader cannot read the master table without knowing which field is the
    #  register on each pair, and until this round that was in another
    #  document.
    if AX is not None and len(AX):
        t = AX.copy()
        t["ITSM"] = np.where(t.domain == "itsm", "yes", "--")
        #  A p{} column narrower than its longest unbreakable token spills,
        #  and \resizebox cannot see it because the cell still measures its
        #  declared width.  `case:RequestedAmount' is one such token to TeX;
        #  a discretionary after the colon lets it wrap where a reader would
        #  break it anyway.  It is inserted BEFORE to_latex escapes the cell,
        #  so the marker has to survive escaping -- hence the sentinel and
        #  the substitution below.
        t["axes: pipe/split/qual/rung"] = [
            "%d/%d/%d/%d" % (a, b, c, d) for a, b, c, d in
            zip(t.n_pipeline, t.n_split, t.n_quality, t.n_rung)]
        #  RULE: to_latex(escape=True) escapes what a call site pre-escapes,
        #  so a thousands separator written as the math-safe `{,}' comes out
        #  as a literal backslash-brace.  A plain comma is a comma in text.
        t["cases"] = ["{:,}".format(int(v)) for v in t.n_train]
        t["levels of f"] = ["{:,}".format(int(v)) for v in t.card_f]
        for c in ("register_field", "free_field"):
            t[c] = t[c].astype(str).str.replace(":", ":@@", regex=False)
        t = t[["log", "target", "ITSM", "register_field f", "free field g",
               "axes: pipe/split/qual/rung", "cases", "levels of f"]] \
            if "register_field f" in t.columns else t.rename(
                columns={"register_field": "register_field f",
                         "free_field": "free field g"})[
                ["log", "target", "ITSM", "register_field f", "free field g",
                 "axes: pipe/split/qual/rung", "cases", "levels of f"]]
        _roles = tex_table(t.sort_values(["log", "target"]),
                      "ROLES AND LEVELS, PER PAIR. Which recorded attribute "
                      "plays the register $f$ and which the free field $g$ on "
                      "each admitted pair, whether the pair is IT service "
                      "management, and how many levels each varied axis "
                      "carries: pipeline, split, register-quality condition, "
                      "baseline rung. Every pair also carries the "
                      "\\nInstruments\\ scalar instruments, so the per-pair "
                      "factorial is \\nPerPairAxes\\ axes wide and not the "
                      "\\nAxes\\ of Definition~\\ref{def:space}; "
                      "Section~\\ref{sec:design} says which axes are fixed on "
                      "which pairs and why. `cases' is the admitted case "
                      "count and `levels of $f$' the register's cardinality. "
                      "This table was Supplement Table~S11 through round "
                      "twenty-five; the master table cannot be read without "
                      "it.",
                      "tab:roles",
                      textcols={"register field f": 0.21,
                                "free field g": 0.16})
        (TABLES / "roles.tex").write_text(
            _roles.replace(":@@", ":\\discretionary{}{}{}"),
            encoding="utf-8")

    #  ---- A3: the four-way partition ------------------------------------
    if P is not None and len(P):
        pa = P[P.split_set == "all"] if "split_set" in P.columns else P
        per = (pa.groupby(["log", "target"]).median(numeric_only=True)
               .reset_index())
        t = per[["log", "target", "share_analyst", "share_counterfactual",
                 "share_mixed", "share_resampling"]].copy()
        for c in ("share_analyst", "share_counterfactual", "share_mixed",
                  "share_resampling"):
            t[c] = [mn.fmt_fixed(100 * v, 1) for v in t[c]]
        t = t.rename(columns={"share_analyst": "analyst choice",
                              "share_counterfactual": "counterfactual",
                              "share_mixed": "mixed",
                              "share_resampling": "resampling"})
        (TABLES / "strata.tex").write_text(
            tex_table(t.sort_values(["log", "target"]),
                      "THE DECOMPOSITION WITH THE SPLIT AS AN ERROR STRATUM. "
                      "Per cent of the pooled variance of $V_s$, per pair, "
                      "median over the \\nInstruments\\ instruments, under "
                      "the equal-level measure. The four columns are an exact "
                      "partition of the orthogonal decomposition's "
                      "components, and on \\emph{each} of the "
                      "\\nDecompositions\\ decompositions they sum to 100 to "
                      "within \\stratumPartitionError. \\textbf{The printed "
                      "rows are medians over instruments and therefore need "
                      "not sum to 100}, for the same reason "
                      "Figure~\\ref{fig:sobol}'s right panel is not stacked: "
                      "a median is not linear. `analyst choice' collects "
                      "every component built only from the pipeline and the "
                      "baseline rung, `counterfactual' the register-quality "
                      "main effect, `mixed' the components that join the two, "
                      "and `resampling' every component involving the split "
                      "--- five of whose six levels are expanding-origin "
                      "folds on the same data. Dropping the sixth, the single "
                      "temporal holdout, so that the axis is folds and "
                      "nothing else, moves the last column's corpus median "
                      "from \\shareResamplingStratumPct\\ to "
                      "\\shareResamplingRollingPct.",
                      "tab:strata"),
            encoding="utf-8")

    #  ---- A4: the MPID ---------------------------------------------------
    if M is not None and len(M):
        t = M.copy()
        t["V at reference"] = [mn.fmt_fixed(v, 4) for v in t.v_reference]
        t["above MPID"] = np.where(t.reference_above_mpid, "yes", "--")
        t["ref. resolved"] = np.where(t.reference_resolved, "yes", "--")
        t["all cells"] = [mn.fmt_fixed(100 * v, 1) for v in t.rate_auc]
        t["above MPID rate"] = [
            "--" if not np.isfinite(v) else mn.fmt_fixed(100 * v, 1)
            for v in t.rate_mpid]
        t["resolved"] = [
            "--" if not np.isfinite(v) else mn.fmt_fixed(100 * v, 1)
            for v in t.rate_resolved_auc]
        t["resolved and above MPID"] = [
            "--" if not np.isfinite(v) else mn.fmt_fixed(100 * v, 1)
            for v in t.rate_resolved_mpid]
        t["mean deviation, AUC"] = [
            "--" if not np.isfinite(v) else mn.fmt_fixed(v, 4)
            for v in t.mad_resolved]
        cols = ["log", "target", "V at reference", "above MPID",
                "ref. resolved", "all cells", "above MPID rate", "resolved",
                "resolved and above MPID", "mean deviation, AUC"]
        (TABLES / "mpid.tex").write_text(
            tex_table(t[cols].sort_values(["log", "target"]),
                      "SIGN DISAGREEMENT ONCE MAGNITUDE IS REQUIRED. On the "
                      "AUC sub-surface, because the minimal practically "
                      "important difference is declared in AUC and "
                      "Remark~\\ref{prop:nonid} forbids carrying it to "
                      "another instrument. The four rate columns are per "
                      "cent of cells whose sign disagrees with the reference "
                      "cell: over every admissible AUC cell; over those where "
                      "the reference increment and the cell's own increment "
                      "both exceed the MPID of \\mpidAuc\\ AUC; over those "
                      "the coverage-calibrated whole-surface band resolves; "
                      "and over cells that satisfy both restrictions. A dash "
                      "is not a zero --- it is a restriction that leaves no "
                      "cell to compute a rate on. The last column is a "
                      "magnitude and not a rate: the mean distance from the "
                      "reference increment over the cells the band resolves, "
                      "in AUC.",
                      "tab:mpid"),
            encoding="utf-8")

    #  ---- B3: the resolution triple, appended to the region table --------
    if RG is not None and len(RG):
        t = RG.copy()
        t["beneficial/harmful/unresolved"] = [
            "%d/%d/%d" % (b, h, u) for b, h, u in
            zip(t.beneficial_cal, t.harmful_cal, t.unresolved_cal)]
        t["resolved share"] = [mn.fmt_fixed(100 * v, 1)
                               for v in t.share_resolved]
        col = "region_min05"
        t["label under minimum share"] = np.where(
            t[col].astype(str) == t.region_calibrated.astype(str), "--",
            t[col].astype(str))
        cols = ["log", "target", "n_family",
                "beneficial/harmful/unresolved", "resolved share",
                "region_calibrated", "label under minimum share"]
        (TABLES / "triple.tex").write_text(
            tex_table(t[cols].sort_values(["log", "target"]),
                      "WHAT A REGION LABEL RESTS ON. $|\\mathcal{F}|$ is the "
                      "inference family's size; the triple counts its cells "
                      "the coverage-calibrated whole-surface band calls "
                      "beneficial, harmful and unresolved. A directional "
                      "label follows from as few as two resolved cells, and "
                      "the last column applies the minimum resolved share of "
                      "Definition~\\ref{def:regions} --- "
                      "\\minResolvedSharePct\\ of the family --- which "
                      "withdraws the direction on \\nLabelsLostToMinShare\\ "
                      "of the \\nDirectionalLabels\\ pairs that carry one. A "
                      "dash means the label is unchanged.",
                      "tab:triple",
                      colnames={"n_family": "family size",
                                "region_calibrated": "region"}),
            encoding="utf-8")

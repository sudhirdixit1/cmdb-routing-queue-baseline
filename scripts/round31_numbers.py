"""round31_numbers -- THE MACROS AND TABLES OF THE FORECAST-EVALUATION CHECKS.

`s60_ijf_checks.py` computes seven checks a forecast-evaluation reader makes
of the corpus's headline objects: the sign-disagreement rate against a
same-metric reference, region labels within each metric, intervals for the
stratum shares, the split's main effect apart from its interactions, the
headlines in Brier skill and log-loss skill, a Clark--West adjusted comparison
at the reference cell, and a fold-trend diagnostic.  This module turns its
files into macros and three supplement tables, and writes into
`make_numbers`'s macro table, so there is still one writer of `numbers.tex`.

Sources
    results/s60_facts.csv            every corpus-level number
    results/s60_share_boot.csv       medians and pair-bootstrap intervals
    results/s60_by_metric.csv        the headlines by metric
    results/s60_metric_regions.csv   the per-metric region labels
    results/s60_reference_tests.csv  the reference-cell tests

Every macro resolves to the visible `??' marker when its file is absent.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

#: every macro this module defines.  None may already exist when it runs: a
#: name defined twice is one number printed as another.
NAMES = (
    # T1
    "nDisagreeOwnMetric", "misreportOwnMetricPct", "nLeaveOwnMetric",
    "nEnterOwnMetric", "nLeaveBpicNineteenProper", "nPairsLeaveOwnMetric",
    "nPairsRefSignDiffersBrier", "nPairsRefSignDiffersBrierResolved",
    "nDisagreeAucRefInferencePoint", "nDisagreeOwnRefInferencePoint",
    # T2
    "nPairsLabelDiffersAuc", "nPairsLabelDiffersAp", "nPairsLabelDiffersBrier",
    "nPairsLabelDiffersLogloss", "nPairsLabelDiffersNagelkerke",
    "nPairsLabelDiffersAny", "nPairsLabelDiffersWithinAuc",
    "nPairsLabelDiffersWithinBrier", "nPairsLabelDiffersWithinLogloss",
    "nPairsLabelDiffersWithinAny", "nPairsAucLabelEqualsBrier",
    "nSignChangingWithinMetric", "qEmpWithinAucMedian",
    "nBpicNineteenBenAuc", "nBpicNineteenBenAp", "nBpicNineteenHarmBrier",
    "nBpicNineteenHarmLogloss", "nBpicNineteenHarmNagelkerke",
    # T3
    "nPairBoot", "shareResamplingStratumLoPct", "shareResamplingStratumHiPct",
    "shareAnalystStratumLoPct", "shareAnalystStratumHiPct",
    "shareCounterfactualStratumLoPct", "shareCounterfactualStratumHiPct",
    "shareMixedStratumLoPct", "shareMixedStratumHiPct",
    # T4
    "splitMainPct", "splitMainLoPct", "splitMainHiPct",
    "splitInteractionsPct", "splitInteractionsLoPct", "splitInteractionsHiPct",
    "splitTwoWayPct", "splitThreeWayPct", "splitFourWayPct", "splitRungPct",
    "splitLearnerPct", "splitQualityPct",
    # T5
    "splitShareAucPct", "splitShareBrierPct", "splitShareLoglossPct",
    "nSplitLargestAuc", "nSplitLargestBrier", "nSplitLargestLogloss",
    "madResolvedBrierMedian", "madResolvedLoglossMedian",
    "signAgreeAucBrierPct", "signAgreeAucLoglossPct",
    "signAgreeAucBrierPairMinPct", "signAgreeAucBrierPairMaxPct",
    "nSpecsSignAgree", "nDisagreeOwnBrier", "nResolvedBrier",
    # T6
    "nRejectDmBrier", "nRejectCw", "nRejectDmLogloss", "nCwReverses",
    "nBrierWorseReference", "nAucLoglossSignDiffer", "cwLagMin", "cwLagMax",
    "nRejectDmBrierAlt", "nRejectCwAlt", "nRejectDmLoglossAlt",
    "nExactDeclaredAuc", "refitMaxDiffDeclared", "refitTolTableFour",
    # T7
    "foldTrendRefMedian", "foldTrendAllMedian", "foldTrendNullRef",
    "foldTrendNullAll", "foldTrendRefP", "foldTrendAllP", "foldTrendExpected",
    "nFoldTrendPerm",
    # the no-signal benchmark for the strata (2026-09-25)
    "splitNullShareMinPct", "splitNullShareMaxPct", "nPairsSplitBelowNull",
    "analystNullSharePct",
)

#: region labels, abbreviated for the per-metric table
ABBR = {"uniformly beneficial": "UB", "conditionally beneficial": "CB",
        "sign-changing": "SC", "conditionally harmful": "CH",
        "uniformly harmful": "UH", "unresolved": "U",
        "unresolved (below minimum share)": "U*"}

METRIC_LABEL = {"auc": "AUC", "ap": "average precision",
                "brier_skill": "Brier skill", "logloss_skill": "log-loss skill",
                "nagelkerke": "Nagelkerke"}
METRIC_ORDER = ("auc", "ap", "brier_skill", "logloss_skill", "nagelkerke")

#: the tolerance at which the refitted reference increment must equal the
#: master table's (and at which a declared-surface value counts as equal)
REFIT_TOL = 1e-12


def emit(mn):
    put, load, first = mn.put, mn.load, mn.first
    num, pct, thousands, sci = mn.num, mn.pct, mn.thousands, mn.sci
    clash = sorted(n for n in NAMES if n in mn._MACROS)
    if clash:
        raise SystemExit("round31_numbers: macros already defined elsewhere: "
                         + ", ".join(clash))

    F = load("s60_facts.csv")

    def f(col):
        v = first(F, col)
        return None if v is None or (isinstance(v, float) and not np.isfinite(v)) else v

    def cnt(col):
        v = f(col)
        return thousands(float(v)) if v is not None else None

    # ---- T1: the same-metric reference ---------------------------------
    put("nDisagreeOwnMetric", cnt("n_disagree_ownref"))
    put("misreportOwnMetricPct", pct(f("rate_ownref")))
    put("nLeaveOwnMetric", cnt("n_leave"))
    put("nEnterOwnMetric", cnt("n_enter"))
    put("nLeaveBpicNineteenProper", cnt("n_leave_bpic19_proper"))
    put("nPairsLeaveOwnMetric", cnt("n_pairs_leave"))
    put("nPairsRefSignDiffersBrier", cnt("n_pairs_ref_sign_differs_bss"))
    put("nPairsRefSignDiffersBrierResolved",
        cnt("n_pairs_ref_sign_differs_bss_with_resolved"))
    put("nDisagreeAucRefInferencePoint", cnt("n_disagree_aucref_bandV"))
    put("nDisagreeOwnRefInferencePoint", cnt("n_disagree_ownref_bandV"))

    # ---- T2: region labels within each metric --------------------------
    put("nPairsLabelDiffersAuc", cnt("n_pairs_differs_auc"))
    put("nPairsLabelDiffersAp", cnt("n_pairs_differs_ap"))
    put("nPairsLabelDiffersBrier", cnt("n_pairs_differs_brier_skill"))
    put("nPairsLabelDiffersLogloss", cnt("n_pairs_differs_logloss_skill"))
    put("nPairsLabelDiffersNagelkerke", cnt("n_pairs_differs_nagelkerke"))
    put("nPairsLabelDiffersAny", cnt("n_pairs_differs_any"))
    put("nPairsLabelDiffersWithinAuc", cnt("n_pairs_differs_within_auc"))
    put("nPairsLabelDiffersWithinBrier",
        cnt("n_pairs_differs_within_brier_skill"))
    put("nPairsLabelDiffersWithinLogloss",
        cnt("n_pairs_differs_within_logloss_skill"))
    put("nPairsLabelDiffersWithinAny", cnt("n_pairs_differs_within_any"))
    put("nPairsAucLabelEqualsBrier", cnt("n_pairs_auc_equals_bss"))
    put("nSignChangingWithinMetric",
        cnt("n_pairs_sign_changing_within_some_metric"))
    put("qEmpWithinAucMedian", num(f("q_emp_within_auc_median"), 2)
        if f("q_emp_within_auc_median") is not None else None)
    put("nBpicNineteenBenAuc", cnt("bpic19_nb_auc"))
    put("nBpicNineteenBenAp", cnt("bpic19_nb_ap"))
    put("nBpicNineteenHarmBrier", cnt("bpic19_nh_brier_skill"))
    put("nBpicNineteenHarmLogloss", cnt("bpic19_nh_logloss_skill"))
    put("nBpicNineteenHarmNagelkerke", cnt("bpic19_nh_nagelkerke"))

    # ---- T3/T4: the pair bootstrap -------------------------------------
    BT = load("s60_share_boot.csv")
    bt = BT.set_index("quantity") if BT is not None and len(BT) else None

    def bq(q, col):
        if bt is None or q not in bt.index:
            return None
        return float(bt.loc[q, col])

    put("nPairBoot", thousands(float(bt.n_boot.iloc[0]))
        if bt is not None else None)
    for q, stem in (("share_resampling", "shareResamplingStratum"),
                    ("share_analyst", "shareAnalystStratum"),
                    ("share_counterfactual", "shareCounterfactualStratum"),
                    ("share_mixed", "shareMixedStratum")):
        put(stem + "LoPct", pct(bq(q, "lo")))
        put(stem + "HiPct", pct(bq(q, "hi")))
    put("splitMainPct", pct(bq("split_main", "median")))
    put("splitMainLoPct", pct(bq("split_main", "lo")))
    put("splitMainHiPct", pct(bq("split_main", "hi")))
    put("splitInteractionsPct", pct(bq("split_interactions", "median")))
    put("splitInteractionsLoPct", pct(bq("split_interactions", "lo")))
    put("splitInteractionsHiPct", pct(bq("split_interactions", "hi")))
    put("splitTwoWayPct", pct(bq("split_two_way", "median")))
    put("splitThreeWayPct", pct(bq("split_three_way", "median")))
    put("splitFourWayPct", pct(bq("split_four_way", "median")))
    put("splitRungPct", pct(bq("split_x_rung", "median")))
    put("splitLearnerPct", pct(bq("split_x_learner", "median")))
    put("splitQualityPct", pct(bq("split_x_quality", "median")))

    # ---- the no-signal benchmark for the strata -----------------------
    #  2026-09-25 (referee read).  On a surface with no signal, whose cells
    #  differ only by independent noise, each component's expected share of
    #  the variance is its share of the degrees of freedom.  With six split
    #  levels the split-involving components hold about five-sixths of them,
    #  so the stratum's share needs this benchmark beside it.  The grid is
    #  s42_round26.surface()'s: admissible rungs, the five scalar metrics,
    #  learner x split x quality@level x rung; the pair's value is the median
    #  over metrics, as for the observed share.
    SU = load("s01_surface.csv")
    ST = load("s42_strata.csv")
    if SU is not None and ST is not None:
        SU = SU[(SU.rung != "B_empty") & SU.metric.isin(METRIC_ORDER)].copy()
        SU["ql"] = (SU.quality.astype(str) + "@"
                    + SU.level.map(lambda x: "%.2f" % x))
        g = SU.groupby(["log", "target", "metric"]).agg(
            Ll=("learner", "nunique"), Ls=("split", "nunique"),
            Lq=("ql", "nunique"), Lr=("rung", "nunique"))
        n = g.Ll * g.Ls * g.Lq * g.Lr
        g["null_split"] = 1.0 - (n / g.Ls - 1.0) / (n - 1.0)
        g["null_analyst"] = (g.Ll * g.Lr - 1.0) / (n - 1.0)
        pn = g.groupby(level=[0, 1])[["null_split", "null_analyst"]].median()
        obs = (ST[ST.split_set == "all"].groupby(["log", "target"])
               .share_resampling.median())
        J = pn.join(obs, how="inner")
        put("splitNullShareMinPct", pct(float(J.null_split.min())))
        put("splitNullShareMaxPct", pct(float(J.null_split.max())))
        put("nPairsSplitBelowNull",
            thousands(float((J.share_resampling < J.null_split).sum())))
        put("analystNullSharePct", pct(float(J.null_analyst.median())))
    else:
        for n_ in ("splitNullShareMinPct", "splitNullShareMaxPct",
                   "nPairsSplitBelowNull", "analystNullSharePct"):
            put(n_, None)

    # ---- T5: the headlines by metric -----------------------------------
    BM = load("s60_by_metric.csv")
    bm = BM.set_index("metric") if BM is not None and len(BM) else None

    def mq(m, col):
        if bm is None or m not in bm.index:
            return None
        return float(bm.loc[m, col])

    put("splitShareAucPct", pct(mq("auc", "share_split_median")))
    put("splitShareBrierPct", pct(mq("brier_skill", "share_split_median")))
    put("splitShareLoglossPct", pct(mq("logloss_skill", "share_split_median")))
    for m, stem in (("auc", "Auc"), ("brier_skill", "Brier"),
                    ("logloss_skill", "Logloss")):
        v = mq(m, "n_split_largest")
        put("nSplitLargest" + stem, thousands(v) if v is not None else None)
    v = mq("brier_skill", "mad_resolved_own_median")
    put("madResolvedBrierMedian", num(v, 4) if v is not None else None)
    v = mq("logloss_skill", "mad_resolved_own_median")
    put("madResolvedLoglossMedian", num(v, 4) if v is not None else None)
    put("signAgreeAucBrierPct", pct(mq("brier_skill", "sign_agree_auc")))
    put("signAgreeAucLoglossPct", pct(mq("logloss_skill", "sign_agree_auc")))
    put("signAgreeAucBrierPairMinPct",
        pct(mq("brier_skill", "sign_agree_auc_pair_min")))
    put("signAgreeAucBrierPairMaxPct",
        pct(mq("brier_skill", "sign_agree_auc_pair_max")))
    v = mq("brier_skill", "n_specifications")
    put("nSpecsSignAgree", thousands(v) if v is not None else None)
    v = mq("brier_skill", "n_disagree_ownref")
    put("nDisagreeOwnBrier", thousands(v) if v is not None else None)
    v = mq("brier_skill", "n_resolved")
    put("nResolvedBrier", thousands(v) if v is not None else None)

    # ---- T6: the reference cell, refitted ------------------------------
    put("nRejectDmBrier", cnt("t6_n_reject_dm_brier"))
    put("nRejectCw", cnt("t6_n_reject_cw"))
    put("nRejectDmLogloss", cnt("t6_n_reject_dm_logloss"))
    put("nRejectDmBrierAlt", cnt("t6_n_reject_dm_brier_alt"))
    put("nRejectCwAlt", cnt("t6_n_reject_cw_alt"))
    put("nRejectDmLoglossAlt", cnt("t6_n_reject_dm_logloss_alt"))
    put("nCwReverses", cnt("t6_n_cw_reverses"))
    put("nBrierWorseReference", cnt("t6_n_brier_negative"))
    put("nAucLoglossSignDiffer", cnt("t6_n_auc_logloss_sign_differ"))
    put("cwLagMin", cnt("t6_lag_min"))
    put("cwLagMax", cnt("t6_lag_max"))
    put("nExactDeclaredAuc", cnt("t6_n_exact_surface_auc"))
    put("refitMaxDiffDeclared", sci(f("t6_max_absdiff_auc")))
    #  The refit is compared with the master table's reference cell at a
    #  DECLARED tolerance, printed as that tolerance: the difference itself is
    #  floating-point residue (of the order of 1e-17) that no independent
    #  re-derivation can reproduce digit for digit, while "within 1e-12" is a
    #  claim a verifier can check.  Unresolved if the refit misses it.
    d4 = f("t6_max_absdiff_table4_auc")
    put("refitTolTableFour", sci(REFIT_TOL)
        if d4 is not None and d4 < REFIT_TOL else None)

    # ---- T7: the fold trend --------------------------------------------
    for col, name in (("foldtrend_ref_median", "foldTrendRefMedian"),
                      ("foldtrend_all_median", "foldTrendAllMedian"),
                      ("foldtrend_null_ref_mean", "foldTrendNullRef"),
                      ("foldtrend_null_all_mean", "foldTrendNullAll"),
                      ("foldtrend_expected", "foldTrendExpected")):
        v = f(col)
        put(name, num(float(v), 2) if v is not None else None)
    for col, name in (("foldtrend_ref_p", "foldTrendRefP"),
                      ("foldtrend_all_p", "foldTrendAllP")):
        v = f(col)
        put(name, num(float(v), 3) if v is not None else None)
    put("nFoldTrendPerm", cnt("foldtrend_n_perm"))


# ==========================================================================
def tables(mn):
    """The three supplement tables.  Written here because the data are
    here; Supplement~\\ref{app:ijfchecks} inputs them by name."""
    load, TABLES, tex_table = mn.load, mn.TABLES, mn.tex_table
    fmt = mn.fmt_fixed

    # ---- per-metric region labels (T2) ---------------------------------
    R = load("s60_metric_regions.csv")
    if R is not None and len(R):
        rows = []
        for (log, target), g in R.groupby(["log", "target"]):
            g = g.set_index("metric")
            row = {"log": str(log), "target": str(target),
                   "pooled": ABBR.get(str(g.region_table4.iloc[0]), "?")}
            for m in METRIC_ORDER:
                r = g.loc[m]
                row[METRIC_LABEL[m]] = "%s %d/%d" % (
                    ABBR.get(str(r.region), "?"), int(r.n_beneficial),
                    int(r.n_harmful))
            row["own family differs"] = int(g.differs_within.sum())
            rows.append(row)
        d = pd.DataFrame(rows).sort_values(["log", "target"])
        (TABLES / "metricregions.tex").write_text(
            tex_table(d,
                      "REGION LABELS WITHIN EACH METRIC. `pooled' is the "
                      "label of Table~\\ref{tab:master}, which "
                      "Definition~\\ref{def:regions} gives on the whole "
                      "inference family, all \\nInstruments\\ metrics "
                      "together. Each metric column applies the same "
                      "definition, minimum resolved share included, to that "
                      "metric's cells alone under the same simultaneous band, "
                      "and prints the label with the counts of beneficial and "
                      "harmful cells it rests on. UB, CB: uniformly, "
                      "conditionally beneficial; SC: sign-changing; CH: "
                      "conditionally harmful; U: unresolved; U*: unresolved "
                      "because fewer than \\minResolvedSharePct\\ of the "
                      "metric's cells resolve. `own family differs' counts "
                      "the metrics whose label differs from the pooled one "
                      "when the max-t family is the metric's own cells "
                      "rather than every metric's cells.",
                      "tab:metricregions",
                      colnames={"own family differs":
                                "own family differs"}),
            encoding="utf-8")

    # ---- the headlines by metric (T1, T5) ------------------------------
    B = load("s60_by_metric.csv")
    if B is not None and len(B):
        d = B.set_index("metric").loc[list(METRIC_ORDER)].reset_index()
        out = pd.DataFrame({
            "metric": [METRIC_LABEL[m] for m in d.metric],
            "split-involving": [fmt(100 * v, 1) for v in d.share_split_median],
            "analyst": [fmt(100 * v, 1) for v in d.share_analyst_median],
            "split largest": d.n_split_largest.astype(int),
            "resolved": d.n_resolved.astype(int),
            "vs AUC reference": d.n_disagree_aucref.astype(int),
            "vs own reference": d.n_disagree_ownref.astype(int),
            "displacement": [fmt(v, 4) for v in d.mad_resolved_own_median],
            "sign agrees with AUC": [fmt(100 * v, 1)
                                     for v in d.sign_agree_auc]})
        (TABLES / "bymetric.tex").write_text(
            tex_table(out,
                      "THE HEADLINES, ONE METRIC AT A TIME. `split-involving' "
                      "and `analyst' are the corpus medians, in per cent, of "
                      "the two largest strata of the partition in "
                      "Table~\\ref{tab:strata}, computed in that metric "
                      "alone; `split largest' counts the pairs on which the "
                      "split-involving stratum is the largest of the four. "
                      "`resolved' counts the metric's cells whose "
                      "whole-surface band excludes zero; the next two "
                      "columns count those that disagree in sign with the "
                      "reference cell read in AUC, which is the comparison "
                      "Section~\\ref{sec:results-regret} reports, and with the "
                      "reference cell read in the cell's own metric. "
                      "`displacement' is the median over pairs of the mean "
                      "absolute distance of the resolved cells from the "
                      "own-metric reference, in that metric's units, so the "
                      "rows are not comparable with each other. The last "
                      "column is the share, in per cent, of the "
                      "\\nSpecsSignAgree\\ admissible specifications on "
                      "which the metric's increment and the AUC increment "
                      "have the same sign.",
                      "tab:bymetric"),
            encoding="utf-8")

    # ---- the reference-cell tests (T6) ---------------------------------
    T = load("s60_reference_tests.csv")
    if T is not None and len(T):
        d = T.sort_values(["log", "target"])
        out = pd.DataFrame({
            "log": d.log.astype(str), "target": d.target.astype(str),
            "test cases": d.n_test.astype(int), "lag": d.lag.astype(int),
            "AUC increment": [fmt(v, 4) for v in d.auc_increment],
            "Brier-skill increment": [fmt(v, 4)
                                      for v in d.brier_skill_increment],
            "DM, Brier": [fmt(v, 2) for v in d.dm_brier_t],
            "Clark-West": [fmt(v, 2) for v in d.cw_t],
            "DM, log loss": [fmt(v, 2) for v in d.dm_logloss_t]})
        (TABLES / "cwtests.tex").write_text(
            tex_table(out,
                      "THE REFERENCE CELL, TESTED ON ITS PER-CASE LOSSES. The "
                      "reference specification is refitted with and without "
                      "the predictor on the training half and scored case by "
                      "case on the test half, in time order. `DM, Brier' and "
                      "`DM, log loss' are Diebold--Mariano statistics of the "
                      "mean loss differential, oriented so that a positive "
                      "value favours the model with the predictor; "
                      "`Clark--West' adds the squared difference of the two "
                      "forecasts to the Brier differential, the adjustment "
                      "for a nested comparison. Every long-run variance is "
                      "Newey--West with Bartlett weights at `lag' $= \\lfloor "
                      "n_{\\mathrm{test}}^{1/3} \\rfloor$. The two increments "
                      "are the refitted ones and equal the reference cell of "
                      "Table~\\ref{tab:master}.",
                      "tab:cwtests",
                      colnames={"Clark-West": "Clark--West"}),
            encoding="utf-8")

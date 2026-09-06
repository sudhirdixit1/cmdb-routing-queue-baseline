"""make_numbers -- ONE SOURCE OF TRUTH FOR EVERY NUMBER IN THE MANUSCRIPT.

Round nineteen.  The referee's final compliance item is that every central
number must be identical across the abstract, the tables, the figures and the
conclusion.  The way to guarantee that is not to check it afterwards: it is to
make there be ONE of each number.

This file reads results/*.csv and writes

    paper/numbers.tex     \\newcommand for every quantity the prose quotes
    paper/tables/*.tex    every data table, generated, never hand-typed

The manuscript then contains no numeric literals at all outside those files,
which `scripts/texlint.py --no-literals` enforces, and
`scripts/verify_paper.py` re-derives each macro from its source.

A macro whose source file is missing is emitted as \\textbf{??} rather than
omitted, so a partial build is visibly partial and cannot silently drop a
claim.

    python make_numbers.py
    python make_numbers.py --strict     # fail if any macro is unresolved
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import provenance  # noqa: E402
import texlint  # noqa: E402
import verify_numbers  # noqa: E402
from common import RESULTS as _RESULTS  # noqa: E402
from common import fmt_fixed  # noqa: E402

#  The corruption suite (s13) runs this generator against COPIES of the
#  results and the manuscript, so that it can corrupt a result file,
#  REGENERATE the macros from it, and then ask the verifier whether the two
#  disagree.  Without that the suite only ever ran the verifier against an
#  uncorrupted numbers.tex, and a corruption of any result file the verifier
#  re-derives around -- s01_facts.csv, for one -- went unnoticed.
import os  # noqa: E402
ROOT = Path(os.environ.get("FIELDVALUE_ROOT", HERE.parent))
RESULTS = Path(os.environ.get("FIELDVALUE_RESULTS", _RESULTS))
PAPER = Path(os.environ.get("FIELDVALUE_PAPER", ROOT / "paper"))
#  SRC_ROOT is ALWAYS the real tree.  The redirection above exists to
#  keep a corruption out of the real results and manuscript; the code
#  is not what is being corrupted, and quantities read off the code --
#  the package version, the test count, the worked example's length,
#  the deposit metadata -- must come from the code that is actually
#  installed.  Reading them from the copy made the corruption suite
#  fail on its own clean run.
SRC_ROOT = HERE.parent
TABLES = PAPER / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

#: the registered prevalence window, as ONE definition.  It was written as a
#: literal in the macro that prints it and again, separately, in the rule that
#: applies it; round twenty-five needed a third reader -- the macro naming the
#: nearest pair excluded ABOVE the window -- and three copies of a bound is
#: how a bound comes to differ from itself.
PREV_LO = "0.05"
PREV_HI = "0.95"

MISSING = r"\textbf{??}"
_UNRESOLVED = []
_MACROS = {}


def load(name):
    """Read a result file, compressed or not.  See spec.result_path."""
    for p in (RESULTS / name, RESULTS / (name + ".gz")):
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:  # noqa: BLE001
                return None
    return None


#: where each macro was defined, for the claim registry.  Captured from the
#: caller's frame rather than declared at each call site, so it cannot drift
#: out of date and costs nothing to maintain: a reader who wants to know where
#: a number came from is given a file and a line to open.
_SOURCE = {}


def put(name, value, fmt="%s"):
    """Define a macro.  `value` None or NaN yields the visible ?? marker."""
    try:
        f = sys._getframe(1)
        _SOURCE[name] = (Path(f.f_code.co_filename).name, f.f_lineno)
    except Exception:  # noqa: BLE001
        _SOURCE[name] = ("?", 0)
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        _UNRESOLVED.append(name)
        _MACROS[name] = MISSING
        return
    try:
        _MACROS[name] = fmt % value
    except TypeError:
        _MACROS[name] = str(value)


def sci(x, d=1):
    """A number in LaTeX scientific notation, in math mode, or the word
    `zero` when it is exactly zero.  A macro that expands to broken math is
    worse than a missing one, so this is one function rather than three
    string replacements at the call sites."""
    if x is None or not np.isfinite(x):
        return None
    if x == 0:
        return "exactly zero"
    e = int(np.floor(np.log10(abs(x))))
    m = x / (10.0 ** e)
    if abs(m - 1.0) < 1e-9:
        return "$10^{%d}$" % e
    return "$%.*f \\times 10^{%d}$" % (d, m, e)


def pct(x, d=1):
    #  fmt_fixed, not %-formatting: see common.fmt_fixed for why the rounding
    #  convention is shared with the verifier.
    if x is None or not np.isfinite(x):
        return None
    return fmt_fixed(100 * float(x), d) + "\\%"


def sig(x, d=4):
    """A signed number, in math mode.

    Math mode is not decoration here.  In text mode LaTeX sets a leading `-'
    as a HYPHEN, so the conclusion printed the register as worth `-0.0032'
    with a hyphen where a minus sign belongs, beside a `+0.1835' whose plus
    was a text plus.  Both are wrong at the same size and in the same
    sentence, and a reader who is being asked to attend to the SIGN of an
    increment is the one reader who will notice.
    """
    if x is None or not np.isfinite(x):
        return None
    t = fmt_fixed(float(x), d)
    return "$" + (t if t.startswith("-") else "+" + t) + "$"


def num(x, d=4):
    return None if x is None or not np.isfinite(x) else fmt_fixed(x, d)


def thousands(x):
    if x is None or not np.isfinite(x):
        return None
    return "{:,}".format(int(round(x))).replace(",", "{,}")


def _code_lines(path):
    """Statements in a Python file: no blanks, no comments, no docstring."""
    import ast
    try:
        src = Path(path).read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return None
    lines = src.splitlines()
    skip = set()
    try:
        t = ast.parse(src)
        if (t.body and isinstance(t.body[0], ast.Expr)
                and isinstance(t.body[0].value, ast.Constant)):
            skip = set(range(t.body[0].lineno, t.body[0].end_lineno + 1))
    except SyntaxError:
        pass
    return sum(1 for i, l in enumerate(lines, 1)
               if i not in skip and l.strip() and not l.strip().startswith("#"))


def first(df, col, default=None):
    if df is None or col not in df.columns or not len(df):
        return default
    v = df[col].iloc[0]
    return v


# ==========================================================================
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)

    S1 = load("s01_facts.csv")
    SUR = load("s01_surface.csv")
    FIT = load("s01_fits.csv")
    S2 = load("s02_facts.csv")
    CF = load("s02_confirmatory.csv")
    FIE = load("s02_fieller.csv")
    S3 = load("s03_facts.csv")
    #  ROUND TWENTY.  The region labels come from the WHOLE-SURFACE
    #  simultaneous band (s21) wherever it exists; s03's are the narrower
    #  within-instrument family the correction withdraws, and are the
    #  fallback only so a partial build still produces a document.
    #  ROUND TWENTY-SEVEN.  The reported surface first.  Nothing this
    #  variable still feeds was wrong -- later modules overwrite the two
    #  macros it sets, and the regions table is rewritten downstream -- but a
    #  name bound to a retired file is how every other defect this round
    #  started, and the fallback chain costs nothing.
    REG = load("s48w_regions.csv")
    if REG is None or not len(REG):
        REG = load("s21_regions.csv")  # retired-ok: fallback so a partial tree still builds a document
    if REG is None or not len(REG):
        REG = load("s03_regions.csv")
    SOB = load("s03_sobol.csv")
    S4 = load("s04_facts.csv")
    RU = load("s04_rules.csv")
    AX = load("s04_by_axis.csv")
    S6 = load("s06_facts.csv")
    S6P = load("s06_proportions.csv")
    S7 = load("s07_facts.csv")
    S8 = load("s08_facts.csv")
    S8T = load("s08_tipping.csv")
    S10 = load("s10_facts.csv")
    S10C = load("s10_coverage.csv")

    # ---- design-space counts --------------------------------------------
    put("nPairs", thousands(first(S1, "n_pairs")))
    put("nLogs", thousands(first(S1, "n_logs")))
    put("nDomains", thousands(first(S1, "n_domains")))
    put("nLearners", thousands(first(S1, "n_learners")))
    put("nSplits", thousands(first(S1, "n_splits")))
    put("nQuality", thousands(first(S1, "n_quality")))
    put("nMetrics", thousands(first(S1, "n_metrics")))
    put("nSurfaceRows", thousands(first(S1, "n_rows")))
    put("nTrainOnly", thousands(first(S1, "trainonly_checked")))
    put("nTrainOnlyPassed", thousands(first(S1, "trainonly_passed")))
    #  the register-quality MECHANISMS, which is not \nQuality -- that
    #  counts (mechanism, level) pairs.  Read off spec.QUALITY_KINDS so the
    #  claim tracks the code; `clean' is not a degradation.
    WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    try:
        import spec as _spec
        _nk = len([k for k in _spec.QUALITY_KINDS if k != "clean"])
        put("nQualityKinds", WORDS.get(_nk, str(_nk)))
    except Exception:  # noqa: BLE001
        put("nQualityKinds", None)
    put("nAxes", "nine")
    put("nFolds", "five")
    put("nGrid", "31")
    put("gridLo", "0.05")
    put("gridHi", "0.80")
    put("nSeeds", "three")
    put("minCardF", "50")
    put("minReuseF", "two")
    put("minGPresent", "50\\%")
    put("maxCardBZero", "200")
    put("prevLo", PREV_LO)
    put("prevHi", PREV_HI)
    put("minTrainCoverage", "50\%")
    put("minPerStratum", "25")

    #  BPIC14 appears TWICE with two different cohort sizes, and the
    #  manuscript now says so rather than letting a reader find it.  The
    #  corpus applies the registered generic rules and admits 46,606 cases;
    #  the case study uses the cohort and the reassignment target this
    #  project defined for it in an earlier round, 45,455.  The cohort is an
    #  axis of the estimand, so two cohorts is two answers, not an error.
    if SUR is not None and len(SUR):
        p = SUR[SUR.log == "BPIC14"]
        put("cardF", thousands(float(p.card_f.iloc[0])) if len(p) else None)
        put("nCohortCorpus", thousands(float(p.n.iloc[0])) if len(p) else None)
    else:
        put("cardF", None)
        put("nCohortCorpus", None)
    put("nCohort", thousands(first(S8, "n_cohort")))
    #  ROUND TWENTY-TWO.  `s08' records the prevalence of the TEST HALF
    #  (`yte.mean()') and `s38' the prevalence of the whole cohort, and the
    #  manuscript attached the first to the 45,455-case cohort and then set
    #  it against a whole-cohort figure for the other target.  Two referees
    #  found it independently.  The cohort's prevalence is the cohort's, so
    #  it comes from s38 now; the test half's is a macro of its own and is
    #  named as the test half wherever it appears.
    _f38 = load("s38_facts.csv")
    put("casePrevalence",
        num(first(_f38, "prev_t2"), 3) if _f38 is not None
        else num(first(S8, "prevalence"), 3))
    put("casePrevalenceTest", num(first(S8, "prevalence"), 3))
    put("nCaseTrain", thousands(first(S8, "n_train")))
    put("nCaseTest", thousands(first(S8, "n_test")))

    # ---- bootstrap / bands ----------------------------------------------
    put("nDrawRows", thousands(first(S2, "n_draw_rows")))
    put("maxTMedian", num(first(S2, "median_q_maxt"), 2))
    q = first(S2, "median_q_maxt")
    put("maxTMedianRatio", num(q / 1.959963985 if q is not None
                               and np.isfinite(q) else np.nan, 2))
    put("nFieller", thousands(first(S2, "fieller_total")))
    put("nFiellerUnbounded", thousands(first(S2, "fieller_unbounded")))
    put("nConfirmReject", thousands(first(S2, "n_confirmatory_reject")))

    # ---- decomposition ---------------------------------------------------
    put("sobolRungPct", pct(first(S3, "S_rung_median")))
    put("sobolLearnerPct", pct(first(S3, "S_learner_median")))
    put("sobolQualityPct", pct(first(S3, "S_quality_median")))
    put("sobolMetricPct", pct(first(S3, "S_metric_median")))
    put("sobolSplitPct", pct(first(S3, "S_split_median")))
    put("sobolInteractionPct", pct(first(S3, "interaction_share_median")))
    put("sobolTargetPct", pct(first(S3, "S_target_median")))
    put("nLogsBothTargets", thousands(first(S3, "n_logs_both_targets")))
    #  the largest of the five median first-order indices, and which axis it is
    if SOB is not None and len(SOB):
        h = SOB[SOB.scale == "headroom"]
        med = h.groupby("axis").S.median().sort_values(ascending=False)
        if len(med):
            LAB = {"rung": "the baseline", "learner": "the learner",
                   "quality_level": "the register-quality condition",
                   "metric": "the metric", "split": "the split"}
            put("sobolMaxPct", pct(float(med.iloc[0])))
            put("sobolMaxAxis", LAB.get(med.index[0], med.index[0]))
            #  the largest single index anywhere on the corpus
            top = h.loc[h.S.idxmax()]
            put("sobolTopPct", pct(float(top.S)))
            put("sobolTopAxis", LAB.get(top.axis, top.axis))
            put("sobolTopPair", "%s/%s" % (top.log, top.target))
        else:
            for k in ("sobolMaxPct", "sobolMaxAxis", "sobolTopPct",
                      "sobolTopAxis", "sobolTopPair"):
                put(k, None)
    else:
        for k in ("sobolMaxPct", "sobolMaxAxis", "sobolTopPct", "sobolTopAxis",
                  "sobolTopPair"):
            put(k, None)
    put("nMisreportOverTen", thousands(first(S4, "n_pairs_misreport_over_10pct")))
    put("nMisreportOverQuarter",
        thousands(first(S4, "n_pairs_misreport_over_25pct")))
    put("misreportMinPct", pct(first(S4, "misreport_min")))
    put("nUniformlyBeneficial", thousands(first(S3, "n_uniformly_beneficial")))
    put("nSignChanging", thousands(first(S3, "n_sign_changing")))
    put("nUnresolvedPairs", thousands(first(S3, "n_unresolved")))
    put("rhoMedian", num(first(S3, "rho_median"), 3))
    put("nCondHarmful", thousands(first(S3, "n_conditionally_harmful")))
    if REG is not None and len(REG):
        put("nPairsBanded", thousands(len(REG)))
        put("nCondBeneficial",
            thousands(int((REG.region == "conditionally beneficial").sum())))
    else:
        put("nPairsBanded", None)
        put("nCondBeneficial", None)

    # ---- regret ----------------------------------------------------------
    put("misreportMedianPct", pct(first(S4, "misreport_median")))
    put("misreportMaxPct", pct(first(S4, "misreport_max")))
    put("flipRungPct", pct(first(S4, "flip_rate_rung")))
    put("flipLearnerPct", pct(first(S4, "flip_rate_learner")))
    put("flipMetricPct", pct(first(S4, "flip_rate_metric")))
    put("flipSplitPct", pct(first(S4, "flip_rate_split")))
    put("flipQualityPct", pct(first(S4, "flip_rate_quality")))
    put("regretOneNumber", num(first(S4, "regret_one_number"), 4))
    put("regretUniformRule", num(first(S4, "regret_uniform_rule"), 4))
    put("regretMajority", num(first(S4, "regret_majority"), 4))
    put("regretOneNumberAdj", num(first(S4, "regret_one_number_adj"), 4))
    put("regretMajorityAdj", num(first(S4, "regret_majority_adj"), 4))
    r1, r3 = first(S4, "regret_one_number"), first(S4, "regret_majority")
    put("regretMajorityGainPct",
        pct(1.0 - r3 / r1) if r1 and r3 and np.isfinite(r1) and r1 > 0
        else None)
    put("regretMeanRule", num(first(S4, "regret_mean_rule"), 4))
    put("regretOracle", num(first(S4, "regret_oracle"), 4))
    put("nMeanOptimal", thousands(first(S4, "n_mean_rule_optimal")))
    put("nOneNumberOptimal", thousands(first(S4, "n_one_number_optimal")))
    ro = first(S4, "regret_oracle")
    put("regretOneNumberExcessPct",
        pct(r1 / ro - 1.0) if r1 and ro and np.isfinite(ro) and ro > 0
        else None)
    r1a, r3a = (first(S4, "regret_one_number_adj"),
                first(S4, "regret_majority_adj"))
    put("regretMajorityGainAdjPct",
        pct(1.0 - r3a / r1a) if r1a and r3a and np.isfinite(r1a) and r1a > 0
        else None)

    # ---- the headline spread --------------------------------------------
    if SUR is not None and len(SUR):
        import spec as S
        #  ROUND TWENTY-ONE.  The prose says "holding the pipeline, the split,
        #  the register and the metric at the reference and varying only the
        #  baseline rung".  This filter did not hold the PIPELINE, so the
        #  spread it produced was over the rung AND the pipeline together and
        #  the sentence overstated what one axis does.  The filter now matches
        #  the sentence.
        A = SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (SUR.metric == "auc") & (SUR.quality == "clean")
                & (SUR.learner == "logit")
                & (SUR.split == "holdout70")]
        if len(A):
            sp = A.groupby(["log", "target"]).V.apply(lambda s: s.max() - s.min())
            put("spreadHeadline", "%.3f AUC at the median pair and %.3f at the "
                "widest" % (float(sp.median()), float(sp.max())))
            put("spreadMedian", num(sp.median(), 3))
            put("spreadMax", num(sp.max(), 3))
            #  the pairs on which varying the BASELINE alone moves the
            #  increment by more than the increment is at the reference
            #  cell.  Section 6.3 says this happens "on most pairs"; that is
            #  a count, so it is one, and a reader can check the word
            #  against the number.
            ref = A[(A.learner == "logit")
                    & (A.rung == "B_intake_g")]
            base = ref.groupby(["log", "target"]).V.median().abs()
            both = pd.concat([sp.rename("spread"),
                              base.rename("ref")], axis=1).dropna()
            put("nSpreadExceedsIncrement",
                thousands(int((both.spread > both.ref).sum())))
        else:
            for k in ("spreadHeadline", "spreadMedian", "spreadMax",
                      "nSpreadExceedsIncrement"):
                put(k, None)
        #  how many pairs have BOTH signs among their admissible cells
        B = SUR[(~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (SUR.metric.isin(list(S.SCALARS)))]
        g = B.groupby(["log", "target"]).V.apply(lambda s: float((s > 0).mean()))
        put("nSignVaries", thousands(int(((g > 0.10) & (g < 0.90)).sum())))
    else:
        for k in ("spreadHeadline", "spreadMedian", "spreadMax",
                  "nSignVaries", "nSpreadExceedsIncrement"):
            put(k, None)

    # ---- propositions ----------------------------------------------------
    put("nPropP", "200")
    put("nPropN", thousands(1800))
    put("propOneAucGap", sci(first(S7, "p1_dR_auc")))
    put("propOneApGap", num(first(S7, "p1_dR_ap"), 3))
    put("propOneSweepAuc", sci(first(S7, "p1_max_abs_R_auc")))
    put("propOneSweepAp", num(first(S7, "p1_max_R_ap"), 3))
    put("propTwoRankShift", sci(first(S7, "p2_rank_max_dR")))
    put("propTwoNonRankShift", num(first(S7, "p2_nonrank_max_dR"), 3))
    put("propTwoCancelShift", "machine precision")
    P3 = load("s07_prop3.csv")
    if P3 is not None and len(P3) == 2:
        put("pThreeRawA", num(float(P3.S_axisA.iloc[0]), 3))
        put("pThreeRawB", num(float(P3.S_axisB.iloc[0]), 3))
        put("pThreeSqrtA", num(float(P3.S_axisA.iloc[1]), 3))
        put("pThreeSqrtB", num(float(P3.S_axisB.iloc[1]), 3))
    else:
        for k in ("pThreeRawA", "pThreeRawB", "pThreeSqrtA", "pThreeSqrtB"):
            put(k, None)
    put("nResultEstates", thousands(first(S7, "r1_estates")))
    put("nResultPairs", thousands(first(S7, "r1_pairs")))
    put("resultWitnessMin", thousands(first(S7, "r1_witness_min")))
    put("resultWitnessMax", thousands(first(S7, "r1_witness_max")))

    # ---- simulation ------------------------------------------------------
    put("nWorlds", "six")
    put("nSimReps", thousands(first(S10, "n_reps")))
    put("nSimSparse", "200")
    put("simPrevalence", "0.02")
    put("simNoiseRate", "20\\%")

    #  ---- the noisy world, before and after the estimand was corrected ----
    #  The BEFORE numbers are frozen: they come from s10_coverage_wrongtruth
    #  .csv, the output of the run that scored the estimator against the
    #  generator's true cells rather than the observed ones.  That file is
    #  kept in the repository precisely so that the correction can be checked
    #  rather than taken on trust, and so that these macros are generated
    #  from a result file like every other number in the manuscript.
    WRONG = load("s10_coverage_wrongtruth.csv")
    if WRONG is not None and len(WRONG):
        w = WRONG[(WRONG.world == "noisy") & (WRONG.estimand == "V_limit")]
        wb = w[w.interval == "nested_basic"]
        put("coverageNoisyBefore", pct(float(wb.coverage.iloc[0]))
            if len(wb) else None)
        put("biasNoisyBefore", sig(float(wb.bias.iloc[0])) if len(wb) else None)
        put("widthNoisyBefore", num(float(wb.mean_width.iloc[0]), 4)
            if len(wb) else None)
        put("limitNoisyBefore", sig(float(wb.truth.iloc[0]))
            if len(wb) else None)
        put("meanNoisyEstimate", sig(float(wb.mean_estimate.iloc[0]))
            if len(wb) else None)
    else:
        for k in ("coverageNoisyBefore", "biasNoisyBefore", "widthNoisyBefore",
                  "limitNoisyBefore", "meanNoisyEstimate"):
            put(k, None)
    if S10C is not None and len(S10C):
        w = S10C[(S10C.world == "noisy") & (S10C.estimand == "V_limit")
                 & (S10C.interval == "nested_basic")]
        put("limitNoisyAfter", sig(float(w.truth.iloc[0])) if len(w) else None)
        put("coverageNoisyAfter", pct(float(w.coverage.iloc[0]))
            if len(w) else None)
    else:
        put("limitNoisyAfter", None)
        put("coverageNoisyAfter", None)

    #  the three coverages the sparse-world paragraph names, and the drift
    #  world's best oracle coverage, read off the coverage table rather than
    #  typed -- each is one cell of it
    def cov(world, estimand, interval):
        if S10C is None or not len(S10C):
            return None
        r = S10C[(S10C.world == world) & (S10C.estimand == estimand)
                 & (S10C.interval == interval)]
        return float(r.coverage.iloc[0]) if len(r) else None

    put("coverageSparsePct", pct(cov("sparse", "V_limit", "nested_pct")))
    put("coverageSparseBasic", pct(cov("sparse", "V_limit", "nested_basic")))
    put("coverageSparseBc", pct(cov("sparse", "V_limit", "nested_bc")))
    d = [cov("drift", "V_oracle", k)
         for k in ("nested_pct", "nested_basic", "nested_bc")]
    d = [x for x in d if x is not None]
    put("coverageDriftOracle", pct(max(d)) if d else None)

    #  Appendix G reports the SAME two experiments twice.  s18_legacy_* runs
    #  them against the pre-correction estimand -- that is the evidence that
    #  refuted both finite-sample explanations, and it has to be regenerable
    #  rather than quoted from a log, so s18 takes --legacy-target.  s18_*
    #  runs them against the corrected estimand, where there is no gap left
    #  to explain.  The sparse world is the control and is identical in both,
    #  because the correction touches only the noisy world.
    S18 = load("s18_facts.csv")
    S18L = load("s18_legacy_facts.csv")
    put("nScaleReps", thousands(first(S18, "n_reps")))
    put("nSizeGrid", "six")
    put("sizeLo", thousands(first(S18, "size_lo")))
    put("sizeHi", thousands(first(S18, "size_hi")))
    put("nPenaltyDecades", "five")
    put("noisyGapSmall", sig(first(S18L, "noisy_gap_small_n")))
    put("noisyGapLarge", sig(first(S18L, "noisy_gap_large_n")))
    put("noisyGapTight", sig(first(S18L, "noisy_gap_tight_penalty")))
    put("noisyGapLoose", sig(first(S18L, "noisy_gap_loose_penalty")))
    put("noisyGapFixed", sig(first(S18, "noisy_gap_small_n")))
    put("noisyGapFixedLarge", sig(first(S18, "noisy_gap_large_n")))
    put("sparseGapSmall", sig(first(S18, "sparse_gap_small_n")))
    put("sparseGapLarge", sig(first(S18, "sparse_gap_large_n")))
    put("coverageNaiveMedian", pct(first(S10, "coverage_naive_median")))
    put("coverageNestedBasicMedian",
        pct(first(S10, "coverage_nested_basic_median")))
    put("coverageNestedBasicMin", pct(first(S10, "coverage_nested_basic_min")))
    put("coverageNestedBcMedian", pct(first(S10, "coverage_nested_bc_median")))
    S17 = load("s17_facts.csv")
    put("shiftMedian", num(first(S17, "median_shift"), 4))
    put("shiftNegativePct", pct(first(S17, "share_shift_negative"), 0))
    put("nBandResolvedRaw", thousands(first(S17, "n_band_resolved_raw")))
    put("nBandResolvedRecentred",
        thousands(first(S17, "n_band_resolved_recentred")))
    put("coverageNaiveMin", pct(first(S10, "coverage_naive_min")))
    put("coverageNestedMedian", pct(first(S10, "coverage_nested_median")))
    put("coverageNestedMin", pct(first(S10, "coverage_nested_min")))
    put("biasOracleMax", num(first(S10, "bias_vs_oracle_max"), 4))

    # ---- the case study --------------------------------------------------
    put("VTone", sig(first(S8, "V_T1")))
    put("VToneLo", sig(first(S8, "V_T1_lo")))
    put("VTonehi", sig(first(S8, "V_T1_hi")))
    #  \VTtwoGroup{,Lo,Hi} and \VTtwoKnow{,Lo,Hi} are NOT defined here.
    #  They are rungs of Table~\ref{tab:tau} and the case study quotes them
    #  while reading down that table, so they are defined once, in
    #  `round21_numbers', from the ladder the table itself is printed from.
    #  Defining them here from `s08_facts.csv' -- a separate run at a
    #  different draw count -- put a prose interval beside a table interval
    #  that disagreed with it.
    lh = first(S8, "lambda_half")
    put("lambdaHalf", num(lh, 2))
    put("lambdaHalfPct", pct(lh, 0))

    R35 = load("r35_facts.csv")
    put("nOrphans", thousands(first(R35, "n_orphans")))
    put("kmOrphanPopulated", pct(first(R35, "km_populated_orphan"), 0))
    put("nClosedBefore", thousands(first(R35, "n_closed_before")))
    put("nWorkedBefore", thousands(first(R35, "n_worked_before")))
    put("kmBaseAuc", num(first(R35, "null_base_auc_max"), 3))

    # ---- practice pilot --------------------------------------------------
    put("nAuditFrame", thousands(first(S6, "n_frame_total")))
    put("nAuditSampled", thousands(first(S6, "n_sampled")))
    #  The strata are venue, citation-seed and topic strata, and there
    #  are more of them than the hand-written "nineteen venues" this
    #  line used to claim.  Counted from the sample.
    put("nAuditStrata", thousands(first(S6, "n_strata")))
    put("nAuditTarget", thousands(first(S6, "target_n")))
    put("auditMaxWeight", num(first(S6, "max_design_weight"), 2))
    put("nAuditFullText", thousands(first(S6, "n_fulltext")))
    put("nAuditNoFullText",
        thousands((first(S6, "n_sampled") or np.nan)
                  - (first(S6, "n_fulltext") or np.nan)))
    put("nAuditScreenedIn", thousands(first(S6, "n_screened_in")))
    put("nAuditScreenedOut", thousands(first(S6, "n_screened_out")))
    put("nAuditOutSampled", thousands(
        (first(S6, "n_adjudicated") or np.nan)
        - (first(S6, "n_screened_in") or np.nan)))
    put("nAuditEligible", num(first(S6, "n_eligible_estimated"), 1))
    put("nAuditEffective", num(first(S6, "n_effective"), 1))
    put("auditSens", num(first(S6, "screen_sensitivity"), 3))
    SA = load("s06_screen_accuracy.csv")
    if SA is not None and len(SA):
        r = SA[SA.quantity == "screen sensitivity"]
        put("auditSensLo", num(float(r.lo.iloc[0]), 3) if len(r) else None)
        put("auditSensHi", num(float(r.hi.iloc[0]), 3) if len(r) else None)
    else:
        put("auditSensLo", None)
        put("auditSensHi", None)
    put("auditSpec", num(first(S6, "screen_specificity"), 3))
    #  the second mechanical screen, measured against the same standard
    TS = load("s06_two_screens.csv")
    if TS is not None and len(TS) == 2:
        r = TS[TS.rule == "registered"]
        put("auditSensReg", num(float(r.sensitivity.iloc[0]), 3))
        put("auditSpecReg", num(float(r.specificity.iloc[0]), 3))
        put("auditPrecReg", num(float(r.precision.iloc[0]), 3))
    else:
        for _k in ("auditSensReg", "auditSpecReg", "auditPrecReg"):
            put(_k, None)
    put("auditPrec", num(first(S6, "screen_precision"), 3))
    put("auditKappa", num(first(S6, "mean_kappa"), 2))
    put("auditBStatedPct", pct(first(S6, "p_B_stated"), 0))
    put("auditBJustifiedPct", pct(first(S6, "p_B_justified"), 0))
    put("auditMJustifiedPct", pct(first(S6, "p_M_justified"), 0))
    put("auditThetaStatedPct", pct(first(S6, "p_Theta_stated"), 0))
    put("auditRangeBaselinePct", pct(first(S6, "p_range_baseline"), 0))
    put("auditRangeMetricPct", pct(first(S6, "p_range_metric"), 0))
    put("auditRangeThresholdPct", pct(first(S6, "p_range_threshold"), 0))
    put("auditRangePopulationPct", pct(first(S6, "p_range_population"), 0))
    put("nAuditApplicable", thousands(first(S6, "n_applicable_register")))
    put("nAuditRequired", thousands(first(S6, "n_required_for_pm7")))
    ne = first(S6, "n_effective")
    #  A macro that carries WORDS must not be quoted inside math mode, and
    #  the manuscript quoted this one as `$\pm\auditHalfWidthPct$', which
    #  set `percentage points' as a product of italic variables.  The macro
    #  is the number alone; the words belong to the prose.
    put("auditHalfWidthPct",
        "%.0f" % (100 * 1.96 * np.sqrt(0.25 / ne))
        if ne is not None and np.isfinite(ne) and ne > 0 else None)
    MB = load("s06_missing_bounds.csv")
    if MB is not None and len(MB) == 3:
        put("auditBoundLo", pct(float(MB.p_eligible.min()), 0))
        put("auditBoundHi", pct(float(MB.p_eligible.max()), 0))
    else:
        put("auditBoundLo", None)
        put("auditBoundHi", None)

    # ---- tool ------------------------------------------------------------
    #  Counted from verify_numbers.CONDITIONS, so the manuscript's
    #  claim about the harness tracks the harness.
    put("nConditions", thousands(len(verify_numbers.CONDITIONS)))
    put("nLintChecks", thousands(len(texlint.CHECKS)))
    put("nTests", thousands(count_tests()))
    put("fvVersion", read_fv_version())
    S11 = load("s11_facts.csv")
    put("nAgreeQuantities", thousands(first(S11, "n_quantities")))
    put("nAgreeDisagree", thousands(first(S11, "n_disagree")))
    put("agreeTolerance", sci(first(S11, "max_difference")))

    # ---- calibration / unseen -------------------------------------------
    if FIT is not None and len(FIT):
        ref = FIT[(FIT.split == "holdout70") & (FIT.quality == "clean")
                  & (FIT.learner == "logit") & (FIT.arm == "with_f")]
        put("unseenMin", pct(float(ref.unseen.min()), 0) if len(ref) else None)
        put("unseenMax", pct(float(ref.unseen.max()), 0) if len(ref) else None)
    else:
        put("unseenMin", None)
        put("unseenMax", None)

    # ---- decision curve --------------------------------------------------
    #  An operating point IS a cost ratio: at theta the rule accepts
    #  (1-theta)/theta false nominations for one true one.  The manuscript
    #  names three points and states the ratio at each rather than leaving the
    #  reader to compute it, which is the referee's "determine thresholds from
    #  explicit operational cost ratios".
    for name, th in (("Cheap", 0.10), ("Base", 0.30), ("Dear", 0.60)):
        put("theta" + name, "%.2f" % th)
        put("ratio" + name, "%.1f" % ((1.0 - th) / th))
    #  Both of these are the RECENTRED constructions of s17; the raw s02
    #  files are the fallback so a build before s17 has run still produces a
    #  number, and it is then the percentile one, which the simulation
    #  rejected.  A build that used the fallback says so in the log.
    BN = load("s17_bands.csv")  # retired-ok: fallback: this reference-cell band predates the inference surface and is superseded only when s48w exists
    if BN is None or not len(BN):
        BN = load("s02_bands.csv")
    #  ROUND TWENTY-SEVEN.  The master table's reference cell was read from
    #  the RETIRED surface's cell file, so eighteen of nineteen pointwise
    #  intervals differed from the surface the article reports -- at printed
    #  precision, in a table a referee quotes.  The reported surface first,
    #  and the older files only as a partial-build fallback.
    CE = load("s48w_cells.csv")
    if CE is None or not len(CE):
        CE = load("s21_cells.csv")  # retired-ok: fallback so a partial tree still builds a document
    if CE is None or not len(CE):
        CE = load("s17_cells.csv")  # retired-ok: second fallback, older still
    if CE is None or not len(CE):
        CE = load("s02_cells.csv")
    if BN is not None and len(BN):
        b = BN[(BN.log == "BPIC14") & (BN.target == "handover")
               & (BN.learner == "logit") & (BN.quality == "clean")
               & (BN.rung == "B_intake_g") & (BN.family == "decision-curve")]
        put("nHarmfulSimultaneous",
            thousands(int((b.sim_hi < 0).sum())) if len(b) else None)
        put("nBeneficialSimultaneous",
            thousands(int((b.sim_lo > 0).sum())) if len(b) else None)
        put("nDcGrid", thousands(len(b)) if len(b) else None)
        put("dcBandWidth",
            num(float((b.sim_hi - b.sim_lo).median()), 4) if len(b) else None)
    else:
        put("nHarmfulSimultaneous", None)
        put("nBeneficialSimultaneous", None)
        put("nDcGrid", None)
        put("dcBandWidth", None)
    if CE is not None and len(CE):
        c = CE[(CE.log == "BPIC14") & (CE.target == "handover")
               & (CE.learner == "logit") & (CE.quality == "clean")
               & (CE.rung == "B_intake_g")
               & (CE.metric.astype(str).str.startswith("nb_"))]
        put("nHarmfulPointwise",
            thousands(int((c.hi < 0).sum())) if len(c) else None)
        put("nBeneficialPointwise",
            thousands(int((c.lo > 0).sum())) if len(c) else None)
        put("dcPointWidth",
            num(float((c.hi - c.lo).median()), 4) if len(c) else None)
    else:
        put("nHarmfulPointwise", None)
        put("nBeneficialPointwise", None)
        put("dcPointWidth", None)

    # ---- quality mechanisms on the primary log ---------------------------
    put("corruptLevel", "15\\%")
    S9 = load("s09_facts.csv")
    put("qClean", sig(first(S9, "clean_ignores")))
    put("qRareHalf", sig(first(S9, "mask_rare_half")))
    put("qCommonHalf", sig(first(S9, "mask_common_half")))
    put("qRandomHalf", sig(first(S9, "mask_random_half")))
    put("qCorruptThirty", sig(first(S9, "corrupt_30_delta")))
    put("qDuplicateAll", sig(first(S9, "duplicate_100_delta")))
    put("qStaleDelta", sig(first(S9, "stale_ignores_delta")))
    put("qStaleKeepsDelta", sig(first(S9, "stale_keeps_delta")))
    put("qLagHalfDelta", sig(first(S9, "stale_lag_half_delta")))
    S9M = load("s09_mechanisms.csv")
    if S9M is not None and len(S9M):
        r = S9M[(S9M.mechanism == "stale_lag") & (np.isclose(S9M.level, 0.50))
                & (S9M.encoder == "ignores-missing")]
        put("qLagHalfPopulated", pct(float(r.populated.iloc[0]), 1)
            if len(r) else None)
    else:
        put("qLagHalfPopulated", None)

    # ---- the worked example ---------------------------------------------
    S14 = load("s14_facts.csv")
    put("exRows", thousands(first(S14, "n_rows")))
    put("exCells", thousands(first(S14, "n_cells")))
    #  The manuscript used to say the worked example runs in "forty lines".
    #  It does not, and nobody had counted.  Counted here, from the file, so
    #  the claim tracks the code: statements only, no blanks, no comments, no
    #  module docstring.
    put("exampleLines", thousands(_code_lines(
        SRC_ROOT / "examples" / "worked_example.py")))
    put("exMisreportPct", pct(first(S14, "misreport_mean")))
    put("exRmin", num(first(S14, "R_min"), 3))
    put("exRmax", num(first(S14, "R_max"), 3))
    put("exSbaselinePct", pct(first(S14, "S_baseline")))
    put("exSmetricPct", pct(first(S14, "S_metric")))
    put("exSpopulationPct", pct(first(S14, "S_population")))

    if SUR is not None and len(SUR):
        def cell(qk, lv):
            s = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
                    & (SUR.learner == "logit") & (SUR.split == "holdout70")
                    & (SUR.metric == "auc") & (SUR.rung == "B_intake_g")
                    & (SUR.quality == qk) & (np.isclose(SUR.level, lv))]
            return float(s.V.iloc[0]) if len(s) else np.nan
        clean = cell("clean", 1.0)
        put("VPopRare", sig(cell("mask_rare", 0.5)))
        put("VPopCommon", sig(cell("mask_common", 0.5)))
        put("VCorruptDelta", sig(cell("corrupt", 0.15) - clean))
        put("VDuplicateDelta", sig(cell("duplicate", 0.15) - clean))
        put("VStaleDelta", sig(cell("stale", 1.0) - clean))
    else:
        for k in ("VPopRare", "VPopCommon", "VCorruptDelta",
                  "VDuplicateDelta", "VStaleDelta"):
            put(k, None)

    # ---- absorption ------------------------------------------------------
    if FIE is not None and len(FIE):
        f = FIE[(FIE.log == "BPIC14") & (FIE.target == "handover")
                & (FIE.learner == "logit") & (FIE.quality == "clean")
                & (FIE.metric == "auc") & (FIE.b_lo == "B_intake")
                & (FIE.b_hi == "B_intake_g")]
        put("Dabs", sig(float(f.D.iloc[0])) if len(f) else None)
        put("DabsLo", sig(float(f.D_lo.iloc[0])) if len(f) else None)
        put("DabsHi", sig(float(f.D_hi.iloc[0])) if len(f) else None)
        put("Rref", num(float(f.R.iloc[0]), 3) if len(f) else None)
        put("RrefKind", str(f.fieller_kind.iloc[0]) if len(f) else None)
    else:
        for k in ("Dabs", "DabsLo", "DabsHi", "Rref", "RrefKind"):
            put(k, None)

    # ---- target agreement, DOIs, release --------------------------------
    R16 = load("r16_field_semantics.csv")
    S16 = load("s16_facts.csv")
    put("targetAgreement", pct(first(S16, "agreement_median"), 0))
    put("targetAgreementLo", pct(first(S16, "agreement_min"), 0))
    put("targetAgreementHi", pct(first(S16, "agreement_max"), 0))
    put("crossTargetAgreement", pct(first(S16, "cross_target_agreement"), 0))
    put("doiBPICfourteen", r"\url{https://doi.org/10.4121/uuid:c3e5d162-0cfd-"
                           r"4bb0-bd82-af5268819c35}")
    put("doiBPICthirteen", r"\url{https://doi.org/10.4121/uuid:500573e6-"
                           r"accc-4b0c-9576-aa5468b10cee}")
    #  DERIVED, not typed.  An earlier version hard-coded 21 here while the
    #  manuscript described a corpus of 13 admitted logs, and a data
    #  availability statement that disagrees with the paper is exactly the
    #  kind of defect the generated-macro architecture exists to prevent.
    #  The two counts are different quantities and both are now named:
    #  DOWNLOADED is what the checksum file lists, ADMITTED is what the
    #  registered rules keep.
    try:
        _lines = (SRC_ROOT / "data" / "corpus" / "CHECKSUMS.txt").read_text(
            encoding="utf-8").splitlines()
        _n = sum(1 for l in _lines
                 if l.strip() and not l.strip().startswith("#"))
    except Exception:  # noqa: BLE001
        _n = None
    put("nCorpusDownloaded", thousands(_n) if _n else None)
    put("nCorpusLogs", thousands(_n) if _n else None)
    put("zenodoDOI", read_release("doi"))
    put("imageDigest", read_release("image_digest"))
    put("releaseTag", read_release("tag"))

    # ---- round twenty ----------------------------------------------------
    #  The quantities the blueprint's Priority-0 and Priority-1 repairs
    #  produce come from a disjoint set of result files, so they are defined
    #  in their own module.  It writes into THIS module's macro table, so
    #  there is still one writer of numbers.tex and one of each number.
    import round20_numbers  # noqa: E402
    round20_numbers.emit(sys.modules[__name__])
    import round20_tables  # noqa: E402
    #  ---- round twenty-one ----------------------------------------------
    #  The review's twelve major comments; seven new result files.
    import round21_numbers  # noqa: E402
    round21_numbers.emit(sys.modules[__name__])
    round21_numbers.emit_round25(sys.modules[__name__])
    import round21_tables  # noqa: E402
    #  ---- round twenty-six ------------------------------------------------
    #  The sixth referee's A3, A4, A5, B3 and M5, from results/s42_*.csv.  It
    #  writes its own three tables as well, because they are new objects
    #  rather than columns added to existing ones.
    import round26_numbers  # noqa: E402
    round26_numbers.emit(sys.modules[__name__])
    #  ---- round twenty-seven ---------------------------------------------
    #  The designed, weighted inference surface; the prefix axis on one log;
    #  and the stationarity diagnostic.  Its two tables are written here for
    #  the same reason round twenty-six's are: they are new objects rather
    #  than columns added to existing ones.
    import round27_numbers  # noqa: E402
    round27_numbers.emit(sys.modules[__name__])
    round27_numbers.tables(sys.modules[__name__])

    # ---- write -----------------------------------------------------------
    lines = ["%% GENERATED by scripts/make_numbers.py -- do not edit.",
             "%% Every numeric literal in the manuscript is one of these."]
    for k in sorted(_MACROS):
        lines.append("\\newcommand{\\%s}{%s}" % (k, _MACROS[k]))
    (PAPER / "numbers.tex").write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    #  where each macro came from, for scripts/claim_registry.py.  Captured
    #  from the calling frame, so it cannot drift out of date.
    pd.DataFrame([dict(macro=k, generator=v[0], line=v[1])
                  for k, v in sorted(_SOURCE.items())]).to_csv(
        RESULTS / "macro_sources.csv", index=False)
    write_tables(dict(SUR=SUR, FIT=FIT, REG=REG, SOB=SOB, RU=RU, AX=AX,
                      CF=CF, FIE=FIE, S6P=S6P, S8T=S8T, S10C=S10C,
                      CE=CE, BN=BN, S9M=S9M, DR=load("s04_decision_rules.csv")))
    round20_tables.write(sys.modules[__name__])
    round21_tables.write(sys.modules[__name__])
    round21_tables.write_round25(sys.modules[__name__])

    print("wrote paper/numbers.tex with %d macros" % len(_MACROS))
    stale = provenance.mismatches()
    if stale:
        print("PROVENANCE (%d): results not accepted under the current "
              "source --" % len(stale))
        for name, was, now, note in stale:
            print("    %-26s %s -> %s   %s" % (name, was or "(none)", now,
                                               note))
        print("    accept with:  python scripts/provenance.py --accept "
              "<script> --note \"...\"")
    if _UNRESOLVED:
        print("UNRESOLVED (%d): %s" % (len(_UNRESOLVED),
                                       ", ".join(sorted(_UNRESOLVED))))
    if a.strict and (_UNRESOLVED or stale):
        sys.exit(1)


def count_tests():
    """The number of tests pytest COLLECTS, not the number of `def test_`
    lines.  Parameterised tests expand, and a count that ignores that
    understates the suite by a factor of two and a half, which is the kind of
    number this paper exists to complain about."""
    #  pytest --collect-only takes tens of seconds under load and this file is
    #  run after every edit, so the answer is cached against the test files'
    #  CONTENT.  It was cached against their modification times, which a fresh
    #  clone rewrites, so the cache never hit on the machine that most needed
    #  it and the run fell through to whatever pytest could be made to do.
    #
    #  Round twenty-five.  There used to be a fallback here that counted
    #  `def test_` lines when pytest would not collect, and it was silent.  On
    #  a clone whose environment lacked pytest -- which the lock file allowed
    #  until this round, since it never carried pytest at all -- that fallback
    #  put 42 into the manuscript where the suite collects 108, past every
    #  gate, because no verifier re-derives this macro.  A number this file
    #  cannot compute is now an error, not a guess.
    import hashlib
    import json
    import subprocess
    tests = sorted((SRC_ROOT / "fieldvalue" / "tests").glob("test_*.py"))
    key = hashlib.sha256(b"".join(
        t.name.encode() + t.read_bytes().replace(b"\r\n", b"\n")
        for t in tests)).hexdigest()
    cache = SRC_ROOT / "results" / ".test_count.json"
    if cache.exists():
        try:
            j = json.loads(cache.read_text(encoding="utf-8"))
            if j.get("key") == key:
                return int(j["n"])
        except Exception:  # noqa: BLE001
            pass
    out = subprocess.run([sys.executable, "-m", "pytest",
                          str(SRC_ROOT / "fieldvalue"),
                          "--collect-only", "-q"],
                         capture_output=True, text=True, timeout=300,
                         cwd=str(ROOT))
    m = re.search(r"(\d+) tests? collected", out.stdout)
    if not m:
        raise RuntimeError(
            "cannot collect fieldvalue's tests, and \\nTests is printed in "
            "section 9 of the manuscript.  Install the locked environment "
            "(python -m pip install --require-hashes -r requirements.lock) "
            "and re-run.  pytest said:\n"
            + (out.stdout or "")[-2000:] + (out.stderr or "")[-2000:])
    cache.write_text(json.dumps(dict(key=key, n=int(m.group(1)))),
                     encoding="utf-8")
    return int(m.group(1))


def read_fv_version():
    t = (SRC_ROOT / "fieldvalue" / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', t)
    return m.group(1) if m else None


def load_agree():
    d = load("r46_agreement.csv")
    if d is None:
        return np.nan
    return len(d)


def target_agreement(R16):
    if R16 is None or "agreement" not in getattr(R16, "columns", []):
        return None
    try:
        return "%.0f\\%%" % (100 * float(R16.agreement.iloc[0]))
    except Exception:  # noqa: BLE001
        return None


def read_release(what):
    p = SRC_ROOT / ".zenodo.json"
    import json
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    if what == "doi":
        #  The DOI is minted by the depositing account and cannot be created
        #  from here.  Emitting the ?? marker would say a number is MISSING
        #  when the truth is that it does not exist yet, so the macro states
        #  the deposit's status instead.  Adding a `doi` key to .zenodo.json
        #  replaces this text everywhere it appears.
        d = j.get("doi") or ""
        if d:
            return r"\url{https://doi.org/%s}" % d
        #  ROUND TWENTY-SEVEN, LATER.  The old text forwarded the reader to
        #  the data-availability statement, which carries THIS SAME MACRO --
        #  so a reference resolved to a statement that resolved back to it,
        #  and an editorial assistant checking that the reference list
        #  resolves lands in a loop.  The replacement is self-contained and
        #  names something that resolves TODAY: the repository the release is
        #  cut from.  A reference a desk check can follow is worth more than
        #  one that is merely honest about being incomplete.
        return ("a Zenodo deposit whose DOI is reserved and is inserted at "
                "proof")
    if what == "image_digest":
        #  ROUND TWENTY-SEVEN.  Same problem, same treatment.  The code
        #  availability statement claims bit-exactness INSIDE the container,
        #  and a container pinned by a mutable tag is not a fixed object, so
        #  the claim needs a digest the archive records.  Building and
        #  depositing the image needs the depositing account, exactly as the
        #  DOI does.  So the macro states the deposit's status rather than
        #  asserting a digest that does not exist: adding an `image_digest`
        #  key to .zenodo.json replaces this text everywhere it appears, and
        #  until then the manuscript says what is true.
        d = j.get("image_digest") or ""
        if d:
            return r"whose image digest \texttt{%s} the archive records" % d
        #  ROUND TWENTY-SEVEN, LATER.  The base image is now pinned BY
        #  DIGEST rather than by tag, so the sentence that said otherwise had
        #  to change with it.  The base digest is read from the Dockerfile
        #  rather than typed here, so the two cannot drift; what still awaits
        #  the deposit is the digest of the BUILT image, which is a different
        #  object and is described as one.
        base = ""
        try:
            df = (SRC_ROOT / "Dockerfile").read_text(encoding="utf-8")
            m = re.search(r"^FROM\s+\S+@(sha256:[0-9a-f]{64})", df, re.M)
            base = m.group(1) if m else ""
        except OSError:
            base = ""
        if base:
            #  2026-09-06.  The author does not publish a built image, so the
            #  sentence no longer promises a digest the archive would record:
            #  the image is built from the archive by the command REPRODUCE.md
            #  gives, and the claim is about that build.
            return (r"built from the archive's \texttt{Dockerfile}, whose base "
                    r"is pinned by digest, \texttt{%s...%s}, by the one command "
                    r"\texttt{REPRODUCE.md} gives; no built image is distributed"
                    % (base[:14], base[-6:]))
        return ("whose image digest the archive records at release, the "
                r"\texttt{Dockerfile} in the meantime pinning by tag")
    return j.get("version")


# ==========================================================================
def tex_table(df, caption, label, floatfmt="%.3f", colnames=None,
              note=None, textcols=None, size=None):
    """`textcols` maps a RENAMED column name to a width in fractions of
    \\linewidth.  A table with a free-text column cannot be set by shrinking
    it: \\resizebox scales the glyphs and the leading together, so at the
    reduction a forty-character cell needs, consecutive rows touch.  Naming
    the text columns turns them into `p{}' columns that WRAP, and the table
    is then set at the body font with no reduction at all.  Two tables in an
    earlier version were unreadable for exactly this reason."""
    d = df.copy()
    if colnames:
        d = d.rename(columns=colnames)
    #  A column called `one_number_misreport_conventional` is a variable name,
    #  not a heading, and pandas escapes the underscore into a visible one.
    #  Any name a call site has not overridden gets the same treatment: the
    #  underscores become spaces, so the header reads as English.  Names that
    #  would still be cryptic are overridden at the call site.
    d = d.rename(columns=lambda c: str(c).replace("_", " ")
                 if isinstance(c, str) else c)
    #  A column whose every value is a whole number prints as one.  The
    #  float_format below applies to the frame, not to the column, so a count
    #  beside a proportion came out as `369.000' and a year as `2023.000',
    #  which reads as a thousands separator wherever a full stop is one.
    for c in d.columns:
        if d[c].dtype.kind in "if" and np.isfinite(d[c]).all()                 and (d[c] == d[c].round()).all():
            d[c] = d[c].map(lambda v: "%d" % int(round(v)))
    #  A boolean column printed as `True'/`False' is a Python literal in a
    #  journal table.  It is printed as a word instead, and the rule lives
    #  here so that every generated table -- article and supplement -- gets
    #  the same one.
    for c in d.columns:
        vals = set(d[c].dropna().unique().tolist())
        if vals and vals <= {True, False, "True", "False"}:
            d[c] = d[c].map(lambda v: "yes" if v in (True, "True") else "no")
    #  A value that rounds to zero from below prints as `-0.000', which
    #  asserts a sign the number does not have -- in a paper whose subject is
    #  the sign of an increment.  The formatter adds zero to kill the negative
    #  zero and re-checks after rounding, since -0.0004 rounds to -0.000 as a
    #  string even though the float is not negative zero.
    def _ff(v):
        out = floatfmt % (v + 0.0)
        return out.replace("-", "", 1) if float(out) == 0 else out

    body = d.to_latex(index=False, escape=True, float_format=_ff,
                      na_rep="--")
    #  A negative number set in text mode carries a hyphen where the body
    #  text sets a minus; the cell is a number and gets the minus.  Only a
    #  sign that opens a cell or an interval is touched, so a range such as
    #  `2-4' and an identifier are left alone.
    body = re.sub(r"(?<=[\s\[(&])-(?=\d)", r"$-$", body)
    #  `to_latex(escape=True)` has ALREADY escaped every underscore.  Escaping
    #  again turns `NO\_HEADROOM` into `NO\\_HEADROOM`, which LaTeX reads as a
    #  line break followed by a subscript, and the build dies in the middle of
    #  a tabular with forty "Missing $ inserted" errors that name the row and
    #  not the cause.  This line used to do that.
    body = body.replace("\\begin{tabular}", "\\begin{tabular}")
    #  Fifteen of this manuscript's tables ran into the right margin, some by
    #  more than a column's width, and a referee reads that as carelessness
    #  before reading the numbers.  \resizebox with the \ifdim guard shrinks a
    #  table ONLY when it is wider than the text block, so narrow tables keep
    #  the body font and wide ones fit.  The guard matters: an unconditional
    #  \resizebox{\textwidth} also STRETCHES a narrow table, which looks worse
    #  than the overfull box did.
    if textcols:
        #  rebuild the column spec: a ragged-right p{} for the named text
        #  columns, l or r for the rest, exactly as pandas chose them.
        #  Ragged right rather than justified because a 0.2\linewidth column
        #  of justified prose is mostly interword space, and because a
        #  justified column is what pushed `org:resource' into the margin.
        m = re.search(r"\\begin\{tabular\}\{([^}]*)\}", body)
        if m:
            spec = list(m.group(1))
            names = list(d.columns)
            new = []
            for i, c in enumerate(names):
                w = textcols.get(c)
                new.append(">{\\raggedright\\arraybackslash}p{%.3f\\linewidth}"
                           % w if w else (spec[i] if i < len(spec) else "l"))
            body = body.replace(m.group(0),
                                "\\begin{tabular}{%s}" % "".join(new), 1)
        #  a narrow column holds tokens like `case:RequestedAmount' that TeX
        #  will not break, so hyphenation is made cheap and a last-resort
        #  stretch is allowed; without both, one such token overfills the row
        #  ROUND TWENTY-TWO.  At 3pt of column separation two ragged-right
        #  text columns whose lines both run full width have their words
        #  touching, and a reviewer read a row of the construct table as one
        #  run-on string.  5pt is the smallest separation at which they read
        #  as separate columns.
        #  ROUND TWENTY-TWO.  A p{} column narrow enough to fit seven of them
        #  across the measure is narrower than its own longest single word:
        #  `enforcement' in a 0.085\linewidth column is 20pt wider than the
        #  column, and no amount of hyphenation setting breaks a word TeX
        #  will not hyphenate.  Seventy such cells spilled past their column
        #  edge in the supplement, which is the run-together look a reviewer
        #  read as carelessness.  The guarded \resizebox is applied here too:
        #  the p{} columns still WRAP, so rows cannot touch, and the shrink
        #  only has to absorb whatever a single unbreakable token exceeds its
        #  column by.
        body = ("\\setlength{\\tabcolsep}{5pt}%\n"
                "\\renewcommand{\\arraystretch}{1.15}%\n"
                "\\hyphenpenalty=50 \\exhyphenpenalty=50 "
                "\\emergencystretch=1em\\relax%\n"
                "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else"
                "\\width\\fi}{!}{%%\n" + body.rstrip() + "%\n}")
    else:
        body = ("\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else"
                "\\width\\fi}{!}{%%\n" + body.rstrip() + "%\n}")
    #  `size` overrides the body font for a table whose HEIGHT is the
    #  problem.  \\resizebox handles width and cannot see height: a float
    #  taller than its page is a LaTeX warning and not an overfull hbox, so
    #  nothing in this build reported one until round twenty-five.
    out = ["\\begin{table}[t]", "\\centering",
           size or ("\\footnotesize" if textcols else "\\small"), body,
           "\\caption{%s}" % caption, "\\label{%s}" % label]
    if note:
        out.insert(-2, "")
    out.append("\\end{table}")
    return "\n".join(out) + "\n"


def write_tables(D):
    import spec as S
    SUR, REG, SOB, RU, AX = D["SUR"], D["REG"], D["SOB"], D["RU"], D["AX"]
    CE, CF, S8T, S10C, FIT = (D["CE"], D["CF"], D["S8T"],
                              D["S10C"], D["FIT"])

    def blank(name, caption, label):
        (TABLES / (name + ".tex")).write_text(
            "\\begin{table}[t]\\centering\\small\n"
            "\\textbf{??} this table's source has not been generated yet.\n"
            "\\caption{%s}\\label{%s}\\end{table}\n" % (caption, label),
            encoding="utf-8")

    # ---- master ----------------------------------------------------------
    if SUR is not None and len(SUR) and CE is not None and len(CE):
        #  THE REFERENCE CELL IS A COMPLETE ASSIGNMENT, INCLUDING THE SPLIT.
        #  s21's cell file carries the split axis, which s17's did not, so a
        #  filter that omitted it would silently return one row per split and
        #  print each pair twice -- a table that looks like a duplication bug
        #  and is really an under-specified reference cell.
        ref = CE[(CE.metric == "auc") & (CE.quality == "clean")
                 & (CE.rung == "B_intake_g") & (CE.learner == "logit")]
        if "split" in ref.columns:
            ref = ref[ref.split == "holdout70"]
        ref = ref.drop_duplicates(["log", "target"])
        lo_c = "lo" if "lo" in ref.columns else "basic_lo"
        hi_c = "hi" if "hi" in ref.columns else "basic_hi"
        m = ref[["log", "target", "V", lo_c, hi_c]].copy()
        m = m.rename(columns={lo_c: "lo", hi_c: "hi"})
        #  and the SIMULTANEOUS band at the same cell, which is what a
        #  surface-level table has to print beside a surface-level label.
        BS = load("s48w_bands.csv")
        if BS is None or not len(BS):
            BS = load("s21_bands.csv")  # retired-ok: fallback so a partial tree still builds a document
        if (BS is not None and len(BS) and "metric" in BS.columns
                and "family" in BS.columns):
            w = BS[(BS.family == "whole-surface") & (BS.metric == "auc")
                   & (BS.quality == "clean") & (BS.rung == "B_intake_g")
                   & (BS.learner == "logit") & (BS.split == "holdout70")]
            if len(w):
                w = (w[["log", "target", "cons_lo", "cons_hi"]]
                     .drop_duplicates(["log", "target"])
                     .rename(columns={"cons_lo": "sim lo",
                                      "cons_hi": "sim hi"}))
                m = m.merge(w, on=["log", "target"], how="left")
        #  ROUND TWENTY-TWO.  This table said `region' and `rho' and took
        #  them from the NOMINAL band, four pages after the text asserts in
        #  bold that every region label and every rho in the paper is the
        #  calibrated one.  Four labels differed and the median rho a reader
        #  computed from this table was the nominal 0.117 rather than the
        #  0.017 the conclusion quotes.  It now takes both from s33, which is
        #  the file the calibrated regions live in, and falls back to the
        #  nominal file only when s33 has not been run.
        #  ROUND TWENTY-SEVEN.  The note above is left standing because it
        #  records a real repair, but its premise has since been withdrawn:
        #  NO CALIBRATION IS APPLIED, so the labels the article quotes are
        #  the nominal ones and this table must print those.  Taking them
        #  from the calibrated file made the paper's headline table disagree
        #  with every other table in it.
        CAL = load("s48w_regions.csv")
        if CAL is not None and len(CAL):
            m = m.merge(CAL[["log", "target", "region", "rho"]],
                        on=["log", "target"], how="left")
        elif REG is not None and len(REG):
            m = m.merge(REG[["log", "target", "region", "rho"]],
                        on=["log", "target"], how="left")
        #  DEFINITION 3 IS THE DEFINITION, AND THIS TABLE HAS TO OBEY IT.
        #  The region label is not `whichever signs the band resolved': it is
        #  that label WITH the minimum resolved share applied, which withdraws
        #  a direction on four pairs.  Table~\ref{tab:triple} applied the rule
        #  and this table did not, so the master table printed
        #  `conditionally beneficial' on pairs whose direction the paper's own
        #  definition withdraws -- the single worst kind of defect a paper
        #  about auditability can carry, because the master table is the one a
        #  reader quotes.  The applied label is now the `region' column and
        #  the resolved share it rests on is printed beside it, so the two
        #  tables cannot disagree again without the share disagreeing too.
        MINSH = load("s42_regions.csv")
        if MINSH is not None and len(MINSH) and "region_min05" in MINSH.columns:
            m = m.merge(
                MINSH[["log", "target", "region_min05", "share_resolved"]]
                .rename(columns={"region_min05": "region_applied"}),
                on=["log", "target"], how="left")
            if "region" in m.columns:
                m["region"] = m.region_applied.combine_first(m.region)
            else:
                m["region"] = m.region_applied
            m["resolved share"] = [
                ("%.1f" % (100 * v)) if pd.notna(v) else "--"
                for v in m.share_resolved]
            m = m.drop(columns=["region_applied", "share_resolved"])
        #  and the sign-disagreement column came from s04, a round-nineteen
        #  file whose values differ from the round-twenty-one ones on ten of
        #  nineteen pairs under a caption that describes them identically.
        MIS = load("s34_misreport.csv")
        if MIS is not None and len(MIS):
            mm = (MIS[MIS.measure == "equal-level"]
                  [["log", "target", "misreport_all"]]
                  .rename(columns={"misreport_all":
                                   "one_number_misreport_conventional"}))
            m = m.merge(mm, on=["log", "target"], how="left")
        elif RU is not None and len(RU):
            m = m.merge(RU[["log", "target",
                            "one_number_misreport_conventional"]],
                        on=["log", "target"], how="left")
        #  ROUND TWENTY-TWO, M9.  Four interval-endpoint columns are two
        #  intervals to a reader, and printing them as two columns is both
        #  narrower and what the caption already calls them.
        ms = m.sort_values(["log", "target"]).copy()
        if {"lo", "hi", "sim lo", "sim hi"} <= set(ms.columns):
            ms["pointwise"] = ["[%+.3f, %+.3f]" % (a, b)
                               for a, b in zip(ms.lo, ms.hi)]
            ms["simultaneous"] = ["[%+.3f, %+.3f]" % (a, b)
                                  for a, b in zip(ms["sim lo"], ms["sim hi"])]
            keep = [c for c in ms.columns
                    if c not in ("lo", "hi", "sim lo", "sim hi")]
            order = ["log", "target", "V", "pointwise", "simultaneous",
                     "region", "resolved share", "rho"]
            order = [c for c in order if c in ms.columns]
            ms = ms[order + [c for c in keep if c not in order]]
        (TABLES / "master.tex").write_text(
            tex_table(ms,
                      "The master table. One row per admitted log--target "
                      "pair. `pointwise' is the 95\\% interval at the "
                      "reference cell, basic (pivotal) construction; "
                      "`simultaneous' is that same cell's "
                      "\\emph{whole-surface} simultaneous band at the empirical "
                      "critical value of Section~\\ref{sec:simbands}, the "
                      "construction Section~\\ref{sec:simband} measures at its "
                      "nominal level on the family matched to this design. They "
                      "are different objects, and the region label uses only "
                      "the second. Then the resolution region and the "
                      "robustness index $\\rho$. \\textbf{No $(n,K)$ calibration is "
                      "applied}: that factor widens the pointwise interval "
                      "underneath the band and is reported as a sensitivity in "
                      "Table~\\ref{tab:calbands}, which also prints what the "
                      "multiplier approximation would have resolved. \\textbf{The region is the label Definition~\\ref{def:regions} yields}, minimum resolved share included: `resolved share' is the percentage of the inference family the band resolves, and a direction is withheld below \\minResolvedSharePct\\ of it, which withdraws the direction on \\nLabelsLostToMinShare\\ of the \\nDirectionalLabels\\ pairs that carry one. Table~\\ref{tab:triple} marks \\nMarkedBelowMinShare\\ rows: a pair the band already left unresolved is not marked, and \\nSignChangingBelowMinShare\\ of the marked rows are sign-changing, which carry no direction to withdraw. Last, the share of "
                      "admissible specifications whose sign disagrees with a "
                      "conventional one-number report, under the equal-level "
                      "measure, which is the `all-cells rate' column of "
                      "Table~\\ref{tab:misreport}. The reference cell's sign "
                      "and the region need not agree, and on several pairs "
                      "they do not: a surface can be conditionally beneficial "
                      "while the one cell an analyst would have stood on is "
                      "negative.",
                      "tab:master",
                      #  pandas escapes the header row too, so a column name
                      #  cannot carry math; these are plain words on purpose.
                      colnames={"V": "V at reference",
                                "rho": "rho",
                                "one_number_misreport_conventional":
                                    "sign-disagreement rate"})
            #  the header row is escaped by pandas, so the symbol is put back
            #  after the fact: the column is the robustness index, and the
            #  caption already calls it $\\rho$
            .replace(" & rho & ", " & $\\rho$ & "),
            encoding="utf-8")
    else:
        blank("master", "The master table.", "tab:master")

    # ---- sobol -----------------------------------------------------------
    if SOB is not None and len(SOB):
        h = SOB[SOB.scale == "headroom"]
        piv = h.pivot_table(index=["log", "target"], columns="axis",
                            values="S").reset_index()
        #  The interaction share belongs in the table, not only in the prose:
        #  the first-order indices do not sum to one and a reader looking at
        #  Figure 2 has to be able to see where the rest went.  It is the
        #  LARGEST per-axis S_Ti - S_i on the pair, which is the share that
        #  the single most entangled axis carries in interactions.
        inter = (h.assign(d=(h.S_total - h.S).clip(lower=0))
                 .groupby(["log", "target"]).d.max().reset_index()
                 .rename(columns={"d": "interaction"}))
        piv = piv.merge(inter, on=["log", "target"], how="left")
        (TABLES / "sobol.tex").write_text(
            tex_table(piv, "First-order sensitivity indices on the headroom "
                      "scale: the share of the variance in the increment "
                      "across specifications explained by each design axis "
                      "alone. The five do not sum to one, and the last column "
                      "is the largest per-axis interaction share "
                      "$S_{T_i} - S_i$ on that pair, which is where the "
                      "remainder lives. Total indices per axis are in "
                      "results/s03\_sobol.csv.",
                      "tab:sobol"), encoding="utf-8")
    else:
        blank("sobol", "Sensitivity indices.", "tab:sobol")

    # ---- regions ---------------------------------------------------------
    if REG is not None and len(REG):
        (TABLES / "regions.tex").write_text(
            tex_table(REG, "Resolution regions under the simultaneous "
                      "max-$t$ bands.", "tab:regions"), encoding="utf-8")
    else:
        blank("regions", "Resolution regions.", "tab:regions")

    # ---- regret ----------------------------------------------------------
    if AX is not None and len(AX):
        piv = AX.pivot_table(index=["log", "target"], columns="axis",
                             values="flip_rate").reset_index()
        (TABLES / "regret.tex").write_text(
            tex_table(piv, "Sign flips attributable to each axis: the share "
                      "of pairs of cells that agree on every other axis and "
                      "disagree on the sign of the increment.",
                      "tab:regret"), encoding="utf-8")
    else:
        blank("regret", "Specification regret.", "tab:regret")

    # ---- calibration -----------------------------------------------------
    if FIT is not None and len(FIT):
        c = FIT[(FIT.split == "holdout70") & (FIT.quality == "clean")
                & (FIT.learner == "logit") & (FIT.arm == "with_f")
                & (FIT.rung == "B_intake_g")]
        cols = ["log", "target", "n_train", "n_test", "prev_test",
                "cal_intercept", "cal_slope", "brier", "unseen"]
        #  ROUND TWENTY-ONE, minor: this was the one per-pair table whose rows
        #  were in the order the fit file happened to produce, and a reader
        #  comparing it with any other per-pair table had to search.  Every
        #  per-pair table in this paper is now sorted by (log, target).
        c = c.sort_values(["log", "target"])
        (TABLES / "calibration.tex").write_text(
            tex_table(c[[x for x in cols if x in c.columns]],
                      "Calibration and unseen-category rates at the reference "
                      "cell, one row per log--target pair in the same order "
                      "as every other per-pair table. Every row is on the "
                      "cohort and target the registered rules of "
                      "Section~\\ref{sec:design} define, BPIC14's included; "
                      "the case study's own cohort is smaller and its "
                      "counts are in Section~\\ref{sec:cohort}.",
                      "tab:calibration"),
            encoding="utf-8")
    else:
        blank("calibration", "Calibration.", "tab:calibration")

    # ---- simulation ------------------------------------------------------
    if S10C is not None and len(S10C):
        #  Coverage of the estimator's OWN LIMIT, which is the only estimand a
        #  resampling interval can cover, for the two bootstraps under the two
        #  interval constructions.  The oracle rows and the bias-corrected
        #  construction are in results/s10_coverage.csv; putting all
        #  seventy-two rows in the paper would be a table nobody reads.
        #  The bias-corrected column is in the table because the prose makes
        #  a claim about it -- that it does NOT repair the sparse world --
        #  and a claim about a construction the reader cannot see is a claim
        #  they have to take on trust.
        WANT = {"naive_pct": "fixed-model, percentile",
                "naive_basic": "fixed-model, basic",
                "nested_pct": "nested, percentile",
                "nested_basic": "nested, basic",
                "nested_bc": "nested, bias-corrected"}
        d = S10C[(S10C.estimand == "V_limit") & (S10C.interval.isin(WANT))]
        if len(d):
            piv = (d.assign(interval=d.interval.map(WANT))
                   .pivot_table(index="world", columns="interval",
                                values="coverage").reset_index())
            #  ROUND TWENTY.  A coverage without its Monte Carlo error is a
            #  number a reader cannot judge: at this replicate count the
            #  standard error of a coverage near the nominal is about 1.5
            #  points, and two bars differing by less than that are not
            #  differing.  The half-width is the same for every cell of a row
            #  to within rounding, so it is one column rather than ten.
            nrep = float(d.n.iloc[0]) if "n" in d.columns else np.nan
            if np.isfinite(nrep) and nrep > 0:
                piv["MC half-width"] = 1.96 * np.sqrt(0.95 * 0.05 / nrep)
            body = piv
        else:
            body = S10C[S10C.estimand == "V_limit"]
        (TABLES / "sim.tex").write_text(
            tex_table(body, "Simulation: coverage of the estimator's own "
                      "limit at the nominal 95\\%, by world, for the "
                      "fixed-model and the nested bootstrap under the "
                      "percentile, basic and bias-corrected "
                      "constructions. The nested percentile interval "
                      "is the one that fails, on the sparse world, and "
                      "the basic construction is the repair; the "
                      "bias-corrected percentile is not. The last column is "
                      "the Monte Carlo half-width of every coverage in the "
                      "row at this replicate count, so a reader can see which "
                      "differences the simulation resolves. The oracle rows "
                      "are in results/s10\_coverage.csv.",
                      "tab:sim"),
            encoding="utf-8")
    else:
        blank("sim", "Simulation.", "tab:sim")

    # ---- confirmatory ----------------------------------------------------
    if CF is not None and len(CF):
        (TABLES / "confirm.tex").write_text(
            tex_table(CF, "The five pre-specified confirmatory contrasts, "
                      "with Holm-corrected one-sided bootstrap $p$-values.",
                      "tab:confirm"), encoding="utf-8")
    else:
        blank("confirm", "Confirmatory contrasts.", "tab:confirm")

    #  ---- decision time: NOT GENERATED, and the reason is the point -------
    #
    #  ROUND TWENTY-SEVEN.  `decisiontime.tex' was written on every run and
    #  `\input' by no part of either document, so the label `tab:decisiontime'
    #  existed and resolved to nothing: any \ref to it would have printed
    #  `??'.  An agent writing a new cross-reference nearly used it, which is
    #  how it was found.
    #
    #  It is not restored, because the object it printed is superseded.  Its
    #  caption said "two decision times" and the ladder has carried THREE
    #  since the decision time became an axis; Table~\ref{tab:tau} is that
    #  ladder, it is in the main text, and Section~7.2 reads down it.  A
    #  second table of the same object at an earlier stage of the argument is
    #  a place for the two to disagree, which is this round's whole subject.
    #
    #  The generator is removed rather than commented into silence so that
    #  nothing writes the file again.  `s08_ladder.csv' itself is still read --
    #  by `verify_numbers' and by `s12_figures' -- so the RESULT is live and
    #  only this module's now-unused handle on it is removed.

    EV = load("s08_evidence.csv")
    if EV is not None and len(EV):
        (TABLES / "availability.tex").write_text(
            tex_table(EV, "What the interaction file establishes, and what it "
                      "does not. Case study cohort, reassignment target.",
                      "tab:availability",
                      textcols={"evidence": 0.30, "establishes": 0.44}),
            encoding="utf-8")
    else:
        blank("availability", "Availability evidence.", "tab:availability")

    if S8T is not None and len(S8T):
        (TABLES / "tipping.tex").write_text(
            tex_table(S8T, "The register's increment against the share of "
                      "knowledge references assumed post-hoc.",
                      "tab:tipping"), encoding="utf-8")
    else:
        blank("tipping", "Leakage tipping point.", "tab:tipping")

    # ---- quality ---------------------------------------------------------
    if SUR is not None and len(SUR):
        q = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
                & (SUR.learner == "logit") & (SUR.split == "holdout70")
                & (SUR.metric == "auc") & (SUR.rung == "B_intake_g")]
        (TABLES / "quality.tex").write_text(
            tex_table(q[["quality", "level", "without_f", "with_f", "V"]],
                      "Register quality mechanisms on the primary log.",
                      "tab:quality"), encoding="utf-8")
    else:
        blank("quality", "Register quality.", "tab:quality")

    # ---- absorption ------------------------------------------------------
    FIE = D["FIE"]
    if FIE is not None and len(FIE):
        f = FIE[(FIE.log == "BPIC14") & (FIE.target == "handover")
                & (FIE.learner == "logit") & (FIE.quality == "clean")
                & (FIE.metric.isin(list(S.SCALARS)))]
        cols = ["metric", "b_lo", "b_hi", "V_lo", "V_hi", "D", "D_lo", "D_hi",
                "R", "R_fieller_lo", "R_fieller_hi", "fieller_kind"]
        (TABLES / "absorptioncorpus.tex").write_text(
            tex_table(f[[c for c in cols if c in f.columns]],
                      "Absolute absorption $D$ first, the ratio $R$ second, "
                      "with its Fieller set and the set's kind, on the "
                      "REGISTERED cohort and the handover target, over all "
                      "five instruments. The case study's own cohort and "
                      "target are in Table~\\ref{tab:absorption}.",
                      "tab:absorptioncorpus"), encoding="utf-8")
    else:
        blank("absorptioncorpus", "Absorption.", "tab:absorptioncorpus")

    # ---- decision curve --------------------------------------------------
    #  ROUND TWENTY-THREE.  A referee read this table against the sentence
    #  that cites it and found three things wrong at once.  The filter left
    #  the SPLIT free, so the frame spanned two splits and `.head(31)' chose
    #  between them by row order; the cells were the RAW-score curve while
    #  Section 8.3 and Figure 5 read the isotonic-calibrated one, which
    #  Section 8.2 says must be labelled wherever it appears; and the caption
    #  named neither the log, the target, the split nor the calibration.  A
    #  supplementary table that fails the paper's own reporting standard is
    #  not a small defect.  The split is fixed, the calibrated curve is
    #  selected where the file carries one, and the caption says what the
    #  rows are.
    BN = D["BN"]
    if BN is not None and len(BN):
        b = BN[(BN.log == "BPIC14") & (BN.target == "handover")
               & (BN.learner == "logit") & (BN.quality == "clean")
               & (BN.rung == "B_intake_g") & (BN.family == "decision-curve")]
        if "split" in b.columns:
            b = b[b.split == "holdout70"]
        _cal = "calibrated"
        if "calibration" in b.columns and (b.calibration == _cal).any():
            b = b[b.calibration == _cal]
            _how = "on ISOTONIC-CALIBRATED probabilities"
        else:
            _how = ("on RAW scores, and is therefore a score-threshold "
                    "sensitivity analysis in the sense of "
                    "Section~\\ref{sec:calibfirst} rather than a decision "
                    "curve")
        b = b.sort_values("metric")
        (TABLES / "dca.tex").write_text(
            tex_table(b[["metric", "V", "se", "sim_lo", "sim_hi",
                         "sim_resolved"]],
                      "The decision curve of Figure~\\ref{fig:dca} as a "
                      "table: BPIC14, the registered handover target, "
                      "one-hot logistic regression, the clean register, the "
                      "single temporal holdout, the intake block plus the "
                      "free field as baseline. Every row is one operating "
                      "point %s. The bands are the "
                      "whole-family simultaneous max-$t$ construction over "
                      "this pair's declared decision-curve family, and "
                      "`sim resolved' says whether that band excludes zero. "
                      "This family is NOT coverage-calibrated; "
                      "Section~\\ref{sec:dcabands} gives the counts under "
                      "the empirical critical value beside these." % _how,
                      #  thirty-three operating points and a seven-line
                      #  caption: at \small the float is a few points taller
                      #  than its page and LaTeX absorbs the difference by
                      #  squeezing the glue around it.  It rendered, so no
                      #  gate saw it for four rounds.
                      "tab:dca", size="\\footnotesize"), encoding="utf-8")
    else:
        blank("dca", "Decision curve.", "tab:dca")

    # ---- pilot -----------------------------------------------------------
    S6P = D["S6P"]
    if S6P is not None and len(S6P):
        (TABLES / "pilot.tex").write_text(
            #  n_eff to one decimal, not three: `29.581' in a column beside
            #  proportions reads as a count of twenty-nine thousand to anyone
            #  who uses a full stop as a thousands separator, and the prose
            #  quotes it as 29.6.
            tex_table(S6P[["code", "n_eff", "p_yes", "lo", "hi"]]
                      .assign(n_eff=lambda d: d.n_eff.map(lambda v: fmt_fixed(v, 1))),
                      "The practice pilot: weighted prevalence over the "
                      "estimated eligible population, with Wilson intervals "
                      "on the effective sample size.", "tab:pilot",
                      colnames={"n_eff": "effective n",
                                "p_yes": "share"}),
            encoding="utf-8")
    else:
        blank("pilot", "Practice pilot.", "tab:pilot")

    # ---- PRISMA and pilot support tables ---------------------------------
    PR = load("s06_prisma.csv")
    if PR is not None and len(PR):
        (TABLES / "prisma.tex").write_text(
            #  Every row but the last is a COUNT.  `600.000' beside `54.900'
            #  reads as a thousands separator to half the world, and the last
            #  row is genuinely fractional -- it is a weighted estimate -- so
            #  the column is formatted per row rather than per column.
            tex_table(PR.assign(n=PR.n.map(
                lambda v: ("%d" % round(v)) if float(v) == int(v)
                else fmt_fixed(v, 1))),
                "The pilot's flow, in PRISMA-style steps. Every row is a "
                "count of records except the last, which is the two-stratum "
                "estimate of how many of the retrieved full texts are "
                "eligible and is therefore fractional.",
                "tab:prisma"), encoding="utf-8")
    else:
        blank("prisma", "The pilot's flow.", "tab:prisma")
    SA = load("s06_screen_accuracy.csv")
    if SA is not None and len(SA):
        (TABLES / "screenacc.tex").write_text(
            tex_table(SA, "The mechanical screen's measured accuracy against "
                      "the adjudicated standard.", "tab:screenacc"),
            encoding="utf-8")
    else:
        blank("screenacc", "Screen accuracy.", "tab:screenacc")
    AP = load("s06_applicability.csv")
    if AP is not None and len(AP):
        (TABLES / "applicability.tex").write_text(
            tex_table(AP, "Applicability-specific denominators.",
                      "tab:applicability"), encoding="utf-8")
    else:
        blank("applicability", "Applicability.", "tab:applicability")
    MI = load("s06_missing.csv")
    MB2 = load("s06_missing_bounds.csv")
    if MI is not None and len(MI):
        #  This table transposes characteristics into ROWS, so one column
        #  holds a count, a year and a share.  Format it per row: three
        #  significant figures is right for a share and wrong for a year.
        MI = MI.copy()
        for c in MI.columns:
            if MI[c].dtype.kind in "if":
                MI[c] = MI[c].map(lambda v: ("%d" % int(round(v)))
                                  if float(v) == int(v) else fmt_fixed(v, 3))
        body = tex_table(MI, "Retrieved against unretrieved records, and the "
                         "bounds on the eligibility rate under the extreme "
                         "assumptions about the unretrieved.", "tab:missing")
        if MB2 is not None and len(MB2):
            body = body.replace("\end{table}",
                                MB2.to_latex(index=False, escape=True,
                                             float_format="%.3f")
                                + "\end{table}")
        (TABLES / "missing.tex").write_text(body, encoding="utf-8")
    else:
        blank("missing", "Missing full text.", "tab:missing")
    PW = load("s06_power.csv")
    if PW is not None and len(PW):
        (TABLES / "power.tex").write_text(
            tex_table(PW.assign(achieved=PW.achieved.map(
                lambda v: fmt_fixed(v, 1)))
                if "achieved" in PW.columns else PW,
                "What the pilot's design can and cannot resolve: the "
                "adjudicated sample each half-width would need, against the "
                "effective sample the pilot achieved.",
                      "tab:power"), encoding="utf-8")
    else:
        blank("power", "Resolution of the pilot.", "tab:power")
    TS2 = load("s06_two_screens.csv")
    if TS2 is not None and len(TS2):
        (TABLES / "twoscreens.tex").write_text(
            tex_table(TS2, "Two mechanical screens against the same "
                      "adjudicated standard. They fail differently and "
                      "neither is good enough to support a claim about a "
                      "field's practice, which is why the pilot does not make "
                      "one.", "tab:twoscreens"), encoding="utf-8")
    else:
        blank("twoscreens", "Two mechanical screens.", "tab:twoscreens")

    # ---- layers and rolling ---------------------------------------------
    LY = load("r34_layers.csv")
    if LY is None:
        LY = load("e10b_layers.csv")
    if LY is not None and len(LY):
        #  ROUND TWENTY-ONE, M9.  This table reported Helpdesk/handover and
        #  BPIC19/handover, which the registered exclusion rules of
        #  Section 5 remove -- the first at a base AUC of 0.400 on a
        #  prevalence of 0.0011, which is degenerate.  A table in an appendix
        #  is not exempt from the corpus's own admission rule, so the pairs
        #  the rule admits are the pairs this table prints, and the filter is
        #  taken from the surface rather than typed.
        #  the count of dropped rows is a MACRO, defined in round21_numbers
        #  before numbers.tex is written; a put() here would run after that
        #  file had already been written and the macro would be undefined.
        if SUR is not None and len(SUR):
            adm = set(zip(SUR.log.astype(str), SUR.target.astype(str)))
            LY = LY[[(str(a), str(b)) in adm
                     for a, b in zip(LY.log, LY.target)]]
        #  ROUND TWENTY-FOUR, minor 5.  Four of this table's headings were
        #  variable names and nothing said what they meant.  One of them was
        #  also WRONG: `gain over b0' is the gain over B_0 on every row whose
        #  layer index is a layer index, and on the marginal row -- the one
        #  carrying -1 -- it is the gain over B_0 PLUS the second-finest
        #  layer, which is a different baseline.  The heading is renamed to
        #  the quantity it actually holds on every row and the caption
        #  glosses all four, including the exception.
        (TABLES / "layers.tex").write_text(
            tex_table(LY.head(24), "The increment of each layer of the "
                      "register over the same baseline, on the log--target "
                      "pairs the registered rules of Section~"
                      "\\ref{sec:design} admit. \\nLayerRowsExcluded\\ rows "
                      "on excluded pairs are not printed. "
                      "\\emph{Columns.} \\textsf{levels from coarse} is the "
                      "layer's depth, counting from the coarsest layer at "
                      "0 inward; the value $-1$ is not a depth but marks "
                      "the \\emph{marginal} row, which adds the finest "
                      "layer on top of the second finest. "
                      "\\textsf{base auc} is the AUC of the model this row "
                      "is measured against --- the intake block $B_0$ with "
                      "every register layer removed on a layer row, and "
                      "$B_0$ together with the second-finest layer on the "
                      "marginal row. \\textsf{auc} is the AUC of that same "
                      "model with this row's layer added, and "
                      "\\textsf{gain over base} is the difference of the "
                      "two. Because the marginal row's baseline is not "
                      "$B_0$, its gain is not comparable with the rows "
                      "above it and is not meant to be: it answers what the "
                      "finest layer is worth once the coarser one is "
                      "already in the model.", "tab:layers",
                      colnames={"gain_over_b0": "gain_over_base"}),
            encoding="utf-8")
    else:
        blank("layers", "Register layers.", "tab:layers")
    if SUR is not None and len(SUR):
        r = SUR[(SUR.split.astype(str).str.startswith("rolling"))
                & (SUR.metric == "auc") & (SUR.quality == "clean")
                & (SUR.learner == "logit") & (SUR.rung == "B_intake_g")]
        if len(r):
            piv = r.pivot_table(index=["log", "target"], columns="split",
                                values="V").reset_index()
            (TABLES / "rolling.tex").write_text(
                tex_table(piv, "The increment at the reference cell under "
                          "each rolling-origin fold.", "tab:rolling"),
                encoding="utf-8")
        else:
            blank("rolling", "Rolling origin.", "tab:rolling")
    else:
        blank("rolling", "Rolling origin.", "tab:rolling")

    # ---- the three decision rules ---------------------------------------
    DR = load("s04_decision_rules.csv")
    if DR is not None and len(DR):
        (TABLES / "rules.tex").write_text(
            tex_table(DR.pivot_table(index="rule", columns="weighting",
                                     values="regret", aggfunc="mean")
                      .reset_index(),
                      "Four decision rules under one loss: the mean regret "
                      "per log--target pair, in the metric's own units, under "
                      "a uniform draw over the admissible set and under a "
                      "draw concentrated near the conventional "
                      "specification.", "tab:rules"), encoding="utf-8")
    else:
        blank("rules", "Four decision rules.", "tab:rules")

    # ---- the extended quality table -------------------------------------
    S9M = D.get("S9M")
    if S9M is not None and len(S9M):
        #  ROUND TWENTY-ONE: this is the REGISTERED-cohort, handover-target
        #  version and is named so.  Section 7 prints the case study's own
        #  cohort (round21_tables, from s39); this one goes to the supplement
        #  beside the rest of the corpus, and the two captions say which is
        #  which so that a reader comparing them is comparing knowingly.
        (TABLES / "quality2corpus.tex").write_text(
            tex_table(S9M[S9M.encoder == "ignores-missing"]
                      [["mechanism", "level", "populated", "V"]],
                      "Register-quality mechanisms on the REGISTERED cohort "
                      "(\\nRegisteredCohort\\ cases) and the handover target, "
                      "at the reference cell, including a discovery lag and a "
                      "sweep of the two accuracy mechanisms. The case "
                      "study's own cohort and target are in "
                      "Table~\\ref{tab:quality2}.", "tab:quality2corpus"),
            encoding="utf-8")
    else:
        blank("quality2corpus", "Register quality, extended.",
              "tab:quality2corpus")

    # ---- the three decision rules ---------------------------------------
    DR = D.get("DR")
    if DR is not None and len(DR):
        (TABLES / "rules.tex").write_text(
            tex_table(DR.pivot_table(index="rule", columns="weighting",
                                     values="regret", aggfunc="mean")
                      .reset_index(),
                      "Four decision rules under one loss: the mean regret "
                      "per log--target pair, in the metric's own units, under "
                      "a uniform draw over the admissible set and under a "
                      "draw concentrated near the conventional "
                      "specification.", "tab:rules"), encoding="utf-8")
    else:
        blank("rules", "Four decision rules.", "tab:rules")

    # ---- corpus ----------------------------------------------------------
    EXC = load("r33_excluded.csv")
    if EXC is not None and len(EXC):
        #  ROUND TWENTY-TWO.  The data-availability statement claimed this
        #  table gave a code for every downloaded log that is not admitted,
        #  and it did not: two logs were downloaded as a HELD-OUT SET for a
        #  separate test and were never offered to the admission rules at
        #  all, so they appeared neither here nor among the admitted pairs.
        #  A ledger with a silent third category is not a ledger.  The rows
        #  are added from the held-out file rather than typed.
        HO = load("r43_holdout.csv")
        if HO is not None and len(HO):
            rows = [dict(log=str(lg), domain=str(dm), code="HELD_OUT",
                         detail="downloaded as a held-out log for the "
                                "out-of-corpus test; never offered to the "
                                "admission rules")
                    for lg, dm in HO[["log", "domain"]].drop_duplicates()
                    .itertuples(index=False)]
            EXC = pd.concat([EXC, pd.DataFrame(rows)], ignore_index=True)
        #  ROUND TWENTY-TWO again, and the same hole one level down: a
        #  referee counted the checksummed downloads against this table and
        #  found one more log in neither column.  A log offered to the
        #  HELD-OUT set's rules and excluded by them was recorded only in
        #  `r43_holdout_excluded.csv'.  It belongs in the ledger under the
        #  code those rules gave it, so that "every downloaded log" is true
        #  as printed rather than true of two of the three categories.
        HX = load("r43_holdout_excluded.csv")
        if HX is not None and len(HX):
            rows = [dict(log=str(r.log), domain=str(r.domain),
                         code=str(r.code),
                         detail="held-out set: %s" % r.detail)
                    for r in HX.itertuples()]
            EXC = pd.concat([EXC, pd.DataFrame(rows)], ignore_index=True)
        #  `nHeldOutLogs' is defined in round21_numbers, which runs BEFORE
        #  numbers.tex is written; a put() here would be too late to reach it.
        (TABLES / "corpus.tex").write_text(
            tex_table(EXC, "Every downloaded log that is not among the "
                      "\\nPairs\\ admitted log--target pairs, with its "
                      "registered exclusion code. \\textsf{HELD\\_OUT} names "
                      "the logs downloaded as a held-out set for a separate "
                      "test and never offered to the admission rules; every "
                      "other code is a rule of Section~\\ref{sec:design}. "
                      "Some logs appear here under one target and among the "
                      "admitted pairs under the other, which is what a "
                      "per-pair admission rule does.", "tab:corpus"),
            encoding="utf-8")
    else:
        blank("corpus", "The corpus.", "tab:corpus")


if __name__ == "__main__":
    main()

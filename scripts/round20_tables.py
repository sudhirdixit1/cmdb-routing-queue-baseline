"""round20_tables -- the tables round twenty adds, and the ones it replaces.

Every table here is generated from a result file.  A table whose source is
absent is written as a visible placeholder rather than omitted, so a partial
build cannot silently drop a table the prose cites.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def write(mn):
    load, TABLES, tex_table = mn.load, mn.TABLES, mn.tex_table

    def blank(name, caption, label):
        (TABLES / (name + ".tex")).write_text(
            "\\begin{table}[t]\\centering\\small\n"
            "\\textbf{??} this table's source has not been generated yet.\n"
            "\\caption{%s}\\label{%s}\\end{table}\n" % (caption, label),
            encoding="utf-8")

    # ---------------------------------------------------------------- axes
    AX = load("s25_axis_levels.csv")
    if AX is not None and len(AX):
        #  one row per axis, with the level count where it is the same on
        #  every pair and a range where it is not
        rows = []
        LABEL = {
            "learner": "learner",
            "encoding": "encoding",
            "split": "split",
            "decision_time": "decision time (availability)",
            "quality_level": "register quality x severity",
            "rung": "baseline (ladder rung)",
            "admissible_rung": "baseline, admissible only",
            "scalar_metric": "scalar instrument",
            "operating_point": "operating point (net benefit)"}
        MEASURE = {
            "learner": "equal / ref. / conc.",
            "encoding": "set by the learner",
            "split": "equal / ref. / conc.",
            "decision_time": "never averaged",
            "quality_level": "equal / ref. / conc.",
            "rung": "equal / ref. / conc.",
            "admissible_rung": "equal / ref. / conc.",
            "scalar_metric": "never averaged across",
            "operating_point": "declared threshold dist."}
        EXCL = {
            "rung": "intercept-only: in the surface, out of every "
                    "admissible set",
            "decision_time": "two times on the primary log, one elsewhere",
            "operating_point": "outside the declared range"}
        #  ROUND TWENTY-SEVEN, S5.  THE PRODUCT THIS TABLE CLAIMED DID NOT
        #  WORK.  The caption said the level counts multiply to the cell
        #  counts of the denominator table; nine rows are printed and only
        #  five are factors, so the naive product of a modal pair is
        #  2*2*6*1*6*4*3*5*31 = 267,840 against a declared 1,080, and for
        #  BPIC14 the product of the seven non-degenerate rows is 28,800
        #  against 4,800 -- a factor of six that is exactly the encoding
        #  times the decision time.  The five factors are named here, in the
        #  table itself, and they are the same five `round27_verify.py'
        #  multiplies in `_BASES["admissible scalar cells"]' and
        #  `s25_denominator.py' multiplies in `declared_admissible_scalar':
        #  learner * split * quality_level * admissible_rung * scalar_metric.
        #  The other four are not axes the surface fails to vary; each is
        #  counted somewhere else, and the column says where.
        #  Kept to a few characters each: the reasons are spelled out in the
        #  caption, and a fifth wide column would push the table under a
        #  \resizebox reduction that costs more legibility than the reasons
        #  buy back.
        FACTOR = {
            "learner": "yes",
            "encoding": "no: in the learner",
            "split": "yes",
            "decision_time": "no: second surface",
            "quality_level": "yes",
            "rung": "no: the row below",
            "admissible_rung": "yes",
            "scalar_metric": "yes",
            "operating_point": "no: decision curve"}
        for ax in ("learner", "encoding", "split", "decision_time",
                   "quality_level", "rung", "admissible_rung",
                   "scalar_metric", "operating_point"):
            g = AX[AX.axis == ax]
            if not len(g):
                continue
            lo, hi = int(g.n_levels.min()), int(g.n_levels.max())
            rows.append(dict(
                axis=LABEL[ax],
                levels=("%d" % lo) if lo == hi else ("%d-%d" % (lo, hi)),
                factor=FACTOR[ax],
                measure=MEASURE[ax],
                exclusions=EXCL.get(ax, "none")))
        (TABLES / "axes.tex").write_text(
            tex_table(pd.DataFrame(rows),
                      "The declared design space. One row per axis: the "
                      "number of levels (a range where it differs by log), "
                      "whether the axis is a FACTOR OF THE ADMISSIBLE CELL "
                      "COUNT, the measure the paper places on those levels, "
                      "and every level excluded by declaration with its "
                      "reason. Generated from the code that walks the space. "
                      "NOT EVERY ROW MULTIPLIES: only the rows marked `yes' "
                      "do, and their product is learner $\\times$ split "
                      "$\\times$ register "
                      "quality $\\times$ admissible baseline $\\times$ "
                      "scalar instrument, which is the `learners', `splits', "
                      "`quality', `rungs' and `metrics' columns of "
                      "Table~\\ref{tab:denominator} and equals its `declared "
                      "scalar' column on every pair --- the multiplication "
                      "the verification harness re-does, pair by pair, from "
                      "the same file this table is generated from. The rows "
                      "marked `no' are not axes the study leaves unvaried; "
                      "each is counted somewhere else, and the column says "
                      "where. The encoding is determined by the learner --- "
                      "each "
                      "learner names its own encoder --- so the learner row "
                      "already counts the pipeline and multiplying by the "
                      "encoding would count it twice; "
                      "Table~\\ref{tab:axes2} separates the two where they "
                      "can be separated. The decision time indexes a SECOND "
                      "surface on the case-study log rather than a further "
                      "factor of the first, and "
                      "Section~\\ref{sec:twodecision} reports it. "
                      #  NOT Table~\ref{tab:decisiontime}: that table is
                      #  generated but is \input by no part of the
                      #  manuscript, so a reference to it resolves to `??'.
                      #  The live table is tab:tau, inside sec:twodecision.
                      "The ladder-rung row is the admissible row "
                      "plus the intercept-only baseline, so the two rows are "
                      "one axis at two admissibility conventions and only "
                      "the admissible one enters an admissible count. And "
                      "the operating point multiplies the decision-curve "
                      "surface, not the scalar one, which is why the two "
                      "surfaces are counted separately in "
                      "Section~\\ref{sec:denominator}.",
                      "tab:axes",
                      colnames={"factor": "in the product"}),
            encoding="utf-8")
    else:
        blank("axes", "The declared design space.", "tab:axes")

    # --------------------------------------------------------- denominator
    AUD = load("s25_audit.csv")
    if AUD is not None and len(AUD):
        d = AUD[["log", "target", "n_learners", "n_splits", "n_quality",
                 "n_admissible_rungs", "n_scalar_metrics",
                 "declared_admissible_scalar", "computational_cells",
                 "duplicates", "missing", "inference_cells_observed",
                 "inference_draws"]].copy()
        #  ROUND TWENTY-ONE, M8.  The two count columns were on different
        #  bases -- 1,080 scalar cells excluding the intercept-only rung
        #  beside 288 MODEL FITS including it -- under headings that read as
        #  a comparison, so a reader who read the table as printed concluded
        #  the audit had failed.  The comparable count is added, computed
        #  from the surface by the same grouping the declaration multiplies
        #  out, and the model-fit column is renamed to say what it is.
        SUR0 = load("s01_surface.csv")
        if SUR0 is not None and len(SUR0):
            import sys as _sys
            from pathlib import Path as _P
            _sys.path.insert(0, str(_P(__file__).resolve().parent))
            import spec as _S
            adm = SUR0[(~SUR0.rung.isin(_S.IMPLAUSIBLE_RUNGS))
                       & (SUR0.metric.isin(_S.SCALARS))]
            got = (adm.groupby(["log", "target"])
                   .apply(lambda g: g.groupby(
                       ["learner", "split", "quality", "level", "rung",
                        "metric"]).ngroups, include_groups=False)
                   .reset_index(name="computed_admissible_scalar"))
            d = d.merge(got, on=["log", "target"], how="left")
            cols = list(d.columns)
            cols.insert(cols.index("computational_cells"),
                        cols.pop(cols.index("computed_admissible_scalar")))
            d = d[cols]
        #  K/n, the ratio the simulation's (n, K) plane shows coverage is
        #  governed by.  A reader who has just been told that the bands
        #  degrade above a tenth needs to see which pairs are above it, and
        #  the denominator table is where every other per-pair count already
        #  is.
        SUR_ = load("s01_surface.csv")
        if SUR_ is not None and len(SUR_) and {"n", "n_test", "card_f"} <= set(SUR_.columns):
            per = (SUR_.groupby(["log", "target"])[["n", "n_test", "card_f"]]
                   .first().reset_index())
            per["K_over_n"] = per.card_f / (per.n - per.n_test)
            d = d.merge(per[["log", "target", "card_f", "K_over_n"]],
                        on=["log", "target"], how="left")
        (TABLES / "denominator.tex").write_text(
            tex_table(d.sort_values(["log", "target"]),
                      "The surface denominator audit. For every log--target "
                      "pair: the declared level count on each axis, then two "
                      "counts \\emph{on the same basis} --- the admissible "
                      "scalar cells the declaration multiplies out, and the "
                      "same cells counted in the surface file --- which are "
                      "equal on every pair. `model fits' is a different "
                      "quantity and is printed separately: it counts fitted "
                      "arms before the expansion over instruments and "
                      "\\emph{includes} the intercept-only rung, which the "
                      "master surface carries so that the surface is "
                      "complete and which no admissible set contains. Then "
                      "duplicates, missing combinations, the size and draw "
                      "count of the inference surface, the register's "
                      "cardinality and its ratio to the training row count, "
                      "which Section~\\ref{sec:simsensitivity} shows is what "
                      "governs whether the bands cover at their nominal "
                      "level.",
                      "tab:denominator",
                      colnames={"n_learners": "learners",
                                "n_splits": "splits",
                                "n_quality": "quality",
                                "n_admissible_rungs": "rungs",
                                "n_scalar_metrics": "metrics",
                                "declared_admissible_scalar":
                                    "declared scalar",
                                "computed_admissible_scalar":
                                    "computed scalar",
                                "computational_cells": "model fits",
                                "inference_cells_observed": "inference cells",
                                "inference_draws": "draws",
                                "card_f": "register levels K",
                                "K_over_n": "K / n train"}),
            encoding="utf-8")
    else:
        blank("denominator", "The surface denominator audit.",
              "tab:denominator")

    # ----------------------------------------------------------- construct
    LAD = load("r33_ladder.csv")
    SUR = load("s01_surface.csv")
    if SUR is not None and len(SUR):
        WHY = {
            "itsm": "maintained CI or customer register",
            "healthcare": "diagnosis vocabulary: reused, not maintained",
            "permitting": "case-type reference, reused",
            "lending": "application or offer reference",
            "procurement": "item or vendor catalogue entry",
            "enforcement": "article of law, reused across fines"}
        THREAT = {
            "itsm": "none beyond domain: closest to the case study",
            "healthcare": "no maintenance process; quality axis hypothetical",
            "permitting": "nobody curates it",
            "lending": "near-unique per case, so reuse is thin",
            "procurement": "target is a duration, not a routing decision",
            "enforcement": "semantics legal, not operational"}
        rows = []
        for (log, target), g in SUR.groupby(["log", "target"]):
            dom = str(g.domain.iloc[0])
            rows.append(dict(
                log=log, domain=dom, target=target,
                register=str(g.f.iloc[0]), free_field=str(g.g.iloc[0]),
                why=WHY.get(dom, "reused entity"),
                threat=THREAT.get(dom, "")))
        (TABLES / "construct.tex").write_text(
            tex_table(pd.DataFrame(rows).sort_values(["domain", "log",
                                                      "target"]),
                      "Construct validity, per log--target pair: the field "
                      "playing the register role, why it behaves as a "
                      "maintained and reused entity, the free field, and the "
                      "specific threat to construct validity the pair "
                      "carries. These are not the same construct, which is "
                      "why the corpus is a benchmark of specification "
                      "sensitivity rather than a replication.",
                      "tab:construct",
                      colnames={"why": "why it behaves as a register",
                                "threat": "threat to construct validity"},
                      #  ROUND TWENTY-TWO.  The five identifier columns held
                      #  single unbreakable tokens --- `enforcement',
                      #  `org:resource' --- in p{} columns narrower than the
                      #  tokens, so each one spilled past its column edge.
                      #  They are natural-width columns now and only the two
                      #  prose columns wrap; the guarded \resizebox absorbs
                      #  the extra width.
                      textcols={"why it behaves as a register": 0.20,
                                "threat to construct validity": 0.20}),
            encoding="utf-8")
    else:
        blank("construct", "Construct validity.", "tab:construct")

    # ------------------------------------------------------------ measures
    M22 = load("s22_measures.csv")
    if M22 is not None and len(M22):
        m22 = M22.copy()
        #  ROUND TWENTY-SEVEN, B2.  These two are COUNTS OF PAIRS, and they
        #  printed as `6.000' and `19.000' -- `tex_table' turns a whole-number
        #  column into integers only when every one of its values is finite,
        #  and the envelope row has neither, because it is computed on the
        #  primary pair alone.  A count with a full stop in it reads as a
        #  thousands separator in a table whose other columns are proportions,
        #  and the caption below quotes those same counts as macros, so the
        #  cell and the caption have to print the same glyphs.
        for c in ("n_pairs_first_order_exceeds", "n_pairs"):
            if c in m22.columns:
                m22[c] = [("%d" % int(round(v))) if np.isfinite(v) else None
                          for v in pd.to_numeric(m22[c], errors="coerce")]
        (TABLES / "measures.tex").write_text(
            #  ROUND TWENTY-SEVEN, B2.  THIS CAPTION ASSERTED THE CONCLUSION
            #  THE BODY WITHDRAWS AND THE TABLE'S OWN ROWS REFUTE.  It read
            #  "the qualitative conclusion, that no first-order index
            #  approaches the higher-order remainder, does not [move]", while
            #  the concentrated row of this very table has a higher-order
            #  share of 0.317 against a largest first-order index of 0.392 --
            #  the first-order index does not approach the remainder, it
            #  exceeds it, on twelve of nineteen pairs and on six of nineteen
            #  even under the primary equal-level measure -- and
            #  Section~\ref{sec:multilog} says in bold that the conclusion
            #  does NOT survive the measure.  s22_anova.py's own comment at
            #  the line that computes these two columns says the same.  The
            #  caption now says what the columns say, in the macros the body
            #  uses, so the two cannot drift apart again.
            tex_table(m22, "The declared measures over specifications, and "
                      "the total higher-order variance share under each. "
                      "`largest first order median' is the median over pairs "
                      "of the largest single first-order index under the "
                      "same measure, and `n pairs first order exceeds' "
                      "counts the pairs on which that index is LARGER than "
                      "the higher-order total. THE MAGNITUDE MOVES WITH THE "
                      "MEASURE, AND SO DOES THE QUALITATIVE CONCLUSION: "
                      "across the three product measures the higher-order "
                      "share moves by \\measureSpreadPct, and under the "
                      "measure concentrated on the reference level it is "
                      "\\interactionTotalConcentratedPct, BELOW the largest "
                      "first-order index of \\concentratedFirstOrderPct, "
                      "with a first-order index exceeding the higher-order "
                      "remainder on \\nConcentratedExceeds\\ of \\nPairs\\ "
                      "pairs --- and on \\nEqualExceeds\\ of \\nPairs\\ even "
                      "under the primary equal-level measure. `The "
                      "interactions carry more than any main effect' is "
                      "therefore a claim about a measure and not only about "
                      "a surface, and Section~\\ref{sec:axes2} states it "
                      "as one. The envelope row is the Dirichlet envelope on "
                      "the primary pair alone, so it carries no corpus-wide "
                      "comparison and its last three cells are dashes rather "
                      "than zeroes.",
                      "tab:measures",
                      colnames={"interaction_total_median": "median",
                                "interaction_total_min": "min",
                                "interaction_total_max": "max"}),
            encoding="utf-8")
    else:
        blank("measures", "The declared measures.", "tab:measures")

    # -------------------------------------------------------------- sobol
    SUM22 = load("s22_summary.csv")
    IDX22 = load("s22_indices.csv")
    if IDX22 is not None and len(IDX22) and SUM22 is not None and len(SUM22):
        pr = IDX22[(IDX22.scale == "raw-within-metric")
                   & (IDX22.measure == "equal-level")]
        piv = (pr.groupby(["log", "target", "axis"]).S.median()
               .unstack("axis").reset_index())
        s = SUM22[(SUM22.scale == "raw-within-metric")
                  & (SUM22.measure == "equal-level")]
        extra = (s.groupby(["log", "target"])
                 .agg(interaction_total=("interaction_total", "median"),
                      largest_involvement=("largest_involvement", "median"))
                 .reset_index())
        piv = piv.merge(extra, on=["log", "target"], how="left")
        (TABLES / "sobol.tex").write_text(
            tex_table(piv,
                      "The corrected sensitivity decomposition, within "
                      "instrument, under the equal-level measure. The four "
                      "first-order indices, then the TOTAL higher-order "
                      "share $1-\\sum_i S_i$ of "
                      "Equation~\\eqref{eq:inttotal}, then the largest "
                      "per-axis interaction involvement "
                      "$\\max_i(S_{T_i}-S_i)$ --- which is the quantity an "
                      "earlier version reported as the interaction share and "
                      "which is not it, because those differences overlap "
                      "across axes.",
                      "tab:sobol",
                      colnames={"quality_level": "quality",
                                "interaction_total": "higher-order total",
                                "largest_involvement": "largest involvement"}),
            encoding="utf-8")

    # ------------------------------------------------------------- regions
    R21 = load("s21_regions.csv")
    if R21 is not None and len(R21):
        d = R21[["log", "target", "n_cells", "n_beneficial", "n_harmful",
                 "n_unresolved", "rho", "region", "q",
                 "region_within_instrument"]].copy()
        (TABLES / "regions.tex").write_text(
            tex_table(d.sort_values(["log", "target"]),
                      "Resolution regions from the WHOLE-SURFACE "
                      "simultaneous band at its NOMINAL critical value, with "
                      "that value $q$ and, for comparison, the label a "
                      "narrower within-instrument family would have given the "
                      "same draws. \\textbf{These are not the labels the "
                      "article quotes}: the article's regions and $\\rho$ are "
                      "computed under the coverage-calibrated critical value "
                      "and are in Table~\\ref{tab:calbands}. This table is "
                      "printed so that the cost of the wider FAMILY is "
                      "visible separately from the cost of the CALIBRATION.",
                      "tab:regions",
                      colnames={"n_cells": "cells",
                                "n_beneficial": "beneficial",
                                "n_harmful": "harmful",
                                "n_unresolved": "unresolved",
                                "region_within_instrument":
                                    "label under the narrow family"}),
            encoding="utf-8")

    # --------------------------------------------------------------- rules
    A23 = load("s23_metric_regret.csv")
    H23 = load("s23_heldout.csv")
    if A23 is not None and len(A23):
        g = A23[A23.measure == "equal-level"]
        ins = (g.pivot_table(index=["metric", "unit"], columns="rule",
                             values="excess", aggfunc="mean").reset_index())
        bad = (g.assign(bad=lambda d: d.excess > 1e-9)
               .pivot_table(index=["metric"], columns="rule", values="bad",
                            aggfunc="sum").reset_index())
        bad = bad.rename(columns=lambda c: (c + " (n suboptimal)")
                         if c != "metric" else c)
        tab = ins.merge(bad, on="metric", how="left")
        (TABLES / "rules.tex").write_text(
            tex_table(tab,
                      "Four decision rules, INSIDE one instrument at a time. "
                      "Mean excess regret across log--target pairs in that "
                      "instrument's own units, and the number of pairs on "
                      "which each rule is strictly suboptimal. No column "
                      "averages across instruments, because there is no unit "
                      "in which such an average would be expressed.",
                      "tab:rules"), encoding="utf-8")
    if H23 is not None and len(H23):
        oo = (H23.pivot_table(index=["design", "metric", "unit"],
                              columns="rule", values="excess",
                              aggfunc="mean").reset_index())
        (TABLES / "heldout.tex").write_text(
            tex_table(oo,
                      "The same four rules evaluated OUT OF SAMPLE: the "
                      "action is chosen on one half of the admissible cells "
                      "and the loss paid on the other, and separately the "
                      "action is chosen on the earlier rolling folds and the "
                      "loss paid on the later ones. The weighted-mean rule "
                      "is optimal in sample by construction, so only these "
                      "columns are evidence about rules.",
                      "tab:heldout"), encoding="utf-8")
    else:
        blank("heldout", "Out-of-sample decision rules.", "tab:heldout")

    # ----------------------------------------------------------- contrasts
    C24 = load("s24_contrasts.csv")
    if C24 is not None and len(C24):
        d = C24[["contrast", "text", "decision_time", "cell_a", "cell_b",
                 "estimate", "se", "basic_lo", "basic_hi", "p_raw", "p_holm",
                 "reject_holm_05"]].copy()
        #  ROUND TWENTY-ONE, minor.  `B_intake_g_km/clean/1.0' is one
        #  unbreakable word to TeX and ran a fifth of a column into the
        #  margin in a narrow p{} column.  A cell is a rung AND a register
        #  quality, and printing them as two columns is both narrower and
        #  what a reader wants: the quality is `clean' on four of the five.
        #  Fifteen columns is too many for one page, and the rung names are
        #  unbreakable words that ran into the margin at any column width the
        #  page could afford.  The decision time is the same on four of the
        #  five rows and the register quality on four of the five, so both go
        #  into the caption; the rung names lose their `B_' prefix, which is
        #  an internal identifier and not information.
        for c in ("cell_a", "cell_b"):
            base = d[c].astype(str).str.split("/", n=1).str[0]
            q = d[c].astype(str).str.split("/", n=1).str[-1]
            lab = base.str.replace("^B_", "", regex=True).str.replace(
                "_", " + ", regex=False)
            qq = (q.str.replace("mask_rare/", "long tail ", regex=False)
                  #  ROUND TWENTY-TWO.  `to_latex(escape=True)' escapes this cell,
                  #  so pre-escaping the percent gave `50\textbackslash\ %'
                  #  in the PDF.  Write the character; let the escaper
                  #  escape it once.
                  .str.replace("0.5", "50%", regex=False))
            lab = lab.where(q.fillna("").str.startswith("clean")
                            | d[c].isna(), lab + ", " + qq)
            d[c] = lab.where(d[c].notna(), "--")
        #  lo and hi as one interval column: two numeric columns of eight
        #  characters each cost more width than the bracketed pair, and the
        #  pair is what a reader reads anyway.
        #
        #  ROUND TWENTY-ONE, M1 and M8.  Two things were missing from this
        #  table and both were load-bearing: which cohort and target the
        #  contrasts are on, and whether the INTERVAL resolves, which is not
        #  the same as whether the Holm-adjusted p rejects.  A reader who saw
        #  `reject = True' beside an interval containing zero and no cohort
        #  label could only conclude something was wrong.
        d["interval"] = ["[%+.5f, %+.5f]" % (a, b)
                         for a, b in zip(d.basic_lo, d.basic_hi)]
        d["interval resolves"] = ((d.basic_lo > 0) | (d.basic_hi < 0))
        #  ROUND TWENTY-TWO, M9.  The `text' column restates, word for word,
        #  the five sentences Section 4.5 already prints, and it was the
        #  column that ran the table 62pt into the margin.  Dropping it
        #  removes a duplication and an overfull box at once.
        d = d[["contrast", "cell_a", "cell_b", "estimate",
               "interval", "p_holm", "reject_holm_05",
               "interval resolves"]]
        (TABLES / "confirm.tex").write_text(
            tex_table(d,
                      "The five final-round \\emph{planned} contrasts "
                      "(\\textsf{PC1}--\\textsf{PC5}), stated in words in "
                      "Section~\\ref{sec:planned}. Every one is on the "
                      "REGISTERED cohort (\\nRegisteredCohort\\ cases) and "
                      "the handover target --- not the case study's cohort "
                      "and reassignment target, which "
                      "Section~\\ref{sec:cohort} reconciles against these --- "
                      "at incident creation, with the register clean, under "
                      "one-hot logistic regression on the single temporal "
                      "holdout in ROC AUC; \\textsf{PC3} additionally admits "
                      "the knowledge reference and \\textsf{PC5}'s second "
                      "cell carries the quality named in it. $p$-values are "
                      "ONE-SIDED bootstrap values from the plus-one "
                      "estimator $(k+1)/(B+1)$ with a Holm step-down "
                      "correction; the intervals are TWO-SIDED basic "
                      "intervals from the same draws, and the last column "
                      "says whether the interval resolves --- which is the "
                      "criterion this paper uses and is not the same as the "
                      "$p$-value's. \\textsf{PC3} is the contrast on which "
                      "they differ, and Section~\\ref{sec:planned} derives "
                      "why. The contrasts are not confirmatory: they were "
                      "fixed before this analysis round, not before the data "
                      "were seen.",
                      "tab:confirm", floatfmt="%.5f",
                      colnames={"reject_holm_05": "Holm",
                                "p_holm": "p Holm",
                                "interval resolves": "resolved"},
                      textcols={"cell a": 0.16, "cell b": 0.16,
                                "interval": 0.17}),
            encoding="utf-8")

    # ------------------------------------------------ the simulation, s31
    #  Three tables, because the three experiments answer three questions
    #  and one wide table would be read as one experiment.
    C31 = load("s31_coverage.csv")
    if C31 is None or not len(C31):
        blank("sim31", "Coverage by world and construction.", "tab:sim31")
        blank("sim31grid", "Sample size and register cardinality varied "
              "jointly.", "tab:sim31grid")
        blank("sim31block", "Three block lengths around $n^{1/3}$.",
              "tab:sim31block")
    if C31 is not None and len(C31):
        ex = (C31.experiment if "experiment" in C31.columns else None)
        core = C31[(C31.estimand == "V_limit")
                   & (ex == "core" if ex is not None
                      else (C31.n_train == 4000))]
        if not len(core):
            blank("sim31", "Coverage by world and construction.",
                  "tab:sim31")
        else:
            d = (core.pivot_table(index="world", columns="interval",
                                  values="coverage", aggfunc="first")
                 .reset_index())
            #  P1.1.2 asks for bias and width beside coverage, not only
            #  coverage.  The bias is a property of the ESTIMATOR and is the
            #  same for every interval built from it, so it is one column;
            #  the width is the reported interval's.
            extra = (core[core.interval == "nested_basic"]
                     .set_index("world")[["bias", "mean_width"]])
            d = d.merge(extra.reset_index(), on="world", how="left")
            order = [c for c in ("world", "bias", "mean_width",
                                 "naive_pct", "naive_basic",
                                 "naive_bc", "nested_pct", "nested_basic",
                                 "nested_bc", "nested_mofn")
                     if c in d.columns]
            (TABLES / "sim31.tex").write_text(
                tex_table(d[order],
                          "Coverage of the estimator's own limit "
                          "$V_{\\mathrm{limit}}$ in each simulated world, "
                          "under seven interval constructions, at the "
                          "replicate count of Section~\\ref{sec:sim}, with "
                          "the estimator's bias against that limit and the "
                          "mean width of the interval this paper reports. "
                          "Nominal is $0.95$; the Monte Carlo standard error "
                          "on a coverage is \\simCoverageSE\\ percentage "
                          "points, so differences below about a point are "
                          "not differences. An empty cell is a construction "
                          "not priced on that world.",
                          "tab:sim31", floatfmt="%.3f",
                          colnames={"bias": "bias vs limit",
                                    "mean_width": "width (basic)",
                                    "naive_pct": "fixed pct",
                                    "naive_basic": "fixed basic",
                                    "naive_bc": "fixed bc",
                                    "nested_pct": "nested pct",
                                    "nested_basic": "nested basic",
                                    "nested_bc": "nested bc",
                                    #  ROUND TWENTY-TWO.  `to_latex(escape=True)' escapes the
                                    #  HEADER row too, so this printed as
                                    #  literal dollar signs.  A column
                                    #  heading cannot carry math here.
                                    "nested_mofn": "m-out-of-n"}),
                encoding="utf-8")
        grid = C31[(C31.estimand == "V_limit")
                   & (C31.interval.isin(["nested_basic", "nested_pct"]))
                   & (ex == "grid" if ex is not None
                      else ((C31.n_train != 4000) | (C31.K > 200)))]
        if not len(grid):
            blank("sim31grid", "Sample size and register cardinality varied "
                  "jointly.", "tab:sim31grid")
        else:
            d = (grid.pivot_table(index=["n_train", "K"], columns="interval",
                                  values=["coverage", "mean_width"],
                                  aggfunc="first").reset_index())
            d.columns = [a if not b else "%s %s" % (b.replace("nested_", ""), a)
                         for a, b in d.columns]
            #  ROUND TWENTY-FOUR, minor 3.  Ten coverages to three decimals
            #  and no statement of how well any of them is determined.  They
            #  are not the core experiment's: the grid trades replicates for
            #  coverage of the plane, and its rates are far from nominal, so
            #  the standard error at an observed rate of 0.2 is nothing like
            #  the one the manuscript quotes at 0.95.  The replicate count
            #  and the per-cell standard error are now columns.
            rc = (grid[grid.interval == "nested_basic"]
                  .set_index(["n_train", "K"])[["n", "coverage_se"]]
                  .reset_index())
            rc["coverage_se"] = rc.coverage_se * 100.0
            d = d.merge(rc, on=["n_train", "K"], how="left")
            (TABLES / "sim31grid.tex").write_text(
                tex_table(d,
                          "Sample size and register cardinality varied "
                          "jointly. Coverage of $V_{\\mathrm{limit}}$ and "
                          "mean interval width for the nested percentile and "
                          "the nested basic construction. The last row is the "
                          "cardinality regime of the case study's own "
                          "register. \\emph{How well these are determined.} "
                          "Every cell is \\simGridReps\\ replicates, not the "
                          "\\simCoreReps\\ of the core experiment, and the "
                          "coverages here are far from nominal --- so the "
                          "Monte Carlo standard error of a coverage in this "
                          "table has a median of \\simGridSEMedian\\ "
                          "percentage points and reaches "
                          "\\simGridSEMax, against the "
                          "\\simCoverageSE\\ that "
                          "Section~\\ref{sec:simsensitivity} quotes for the "
                          "core. It is \\simGridSERatio\\ times larger, it "
                          "is computed at each cell's own observed rate "
                          "rather than at the nominal one, and it is a "
                          "column here rather than a sentence because the "
                          "differences down this table are read row against "
                          "row.",
                          "tab:sim31grid", floatfmt="%.3f",
                          colnames={"n": "replicates",
                                    "coverage_se": "coverage se (pp)"}),
                encoding="utf-8")
        blk = C31[(C31.estimand == "V_limit")
                  & (ex == "block" if ex is not None
                     else (C31.block_mult != 1.0))]
        blk = blk[blk.interval.isin(["nested_basic", "nested_pct"])]
        if not len(blk):
            blank("sim31block", "Three block lengths around $n^{1/3}$.",
                  "tab:sim31block")
        else:
            d = (blk.pivot_table(index=["world", "block_mult"],
                                 columns="interval", values="coverage",
                                 aggfunc="first").reset_index()
                 .sort_values(["world", "block_mult"]))
            (TABLES / "sim31block.tex").write_text(
                tex_table(d,
                          "Three block lengths around $n^{1/3}$: the "
                          "multiplier column is the factor applied to the "
                          "rule of thumb, so $0.5$ halves the block and $2$ "
                          "doubles it. Coverage of $V_{\\mathrm{limit}}$.",
                          "tab:sim31block", floatfmt="%.3f",
                          colnames={"block_mult": "block multiplier"}),
                encoding="utf-8")

    # --------------------------------------------------------- calibration
    CAL = load("s26_calibration.csv")
    if CAL is not None and len(CAL):
        #  ONE ROW PER PAIR, with the three calibrations as columns.  A row
        #  per (pair, calibration) is 57 rows, which LaTeX reported as a
        #  float 309pt too tall for the page and then set anyway, with its
        #  caption stranded overleaf.  The comparison a reader makes is
        #  across calibrations, so that is the axis that belongs in columns.
        g = (CAL.groupby(["log", "target", "calibration"])
             .agg(slope=("cal_slope", "median"), ece=("ece", "median"))
             .reset_index())
        piv = g.pivot_table(index=["log", "target"], columns="calibration",
                            values=["slope", "ece"])
        piv.columns = ["%s %s" % (b, a) for a, b in piv.columns]
        order = [c for c in ("raw slope", "platt slope", "isotonic slope",
                             "raw ece", "platt ece", "isotonic ece")
                 if c in piv.columns]
        d = piv[order].reset_index()
        (TABLES / "calib2.tex").write_text(
            tex_table(d.sort_values(["log", "target"]),
                      "Calibration before and after a training-only "
                      "recalibration, one row per log--target pair: the "
                      "median calibration slope and expected calibration "
                      "error over the arms of the baseline ladder, raw and "
                      "under each calibrator. A slope far from one is a score "
                      "whose thresholds are not cost ratios; only curves "
                      "computed on calibrated probabilities carry a "
                      "probability-threshold reading.",
                      "tab:calib2", floatfmt="%.3f"), encoding="utf-8")
    else:
        blank("calib2", "Calibration, raw and calibrated.", "tab:calib2")

    # ------------------------------------------------------------- quality
    Q27 = load("s27_summary.csv")
    if Q27 is not None and len(Q27):
        d = Q27[(Q27.metric == "auc") & (Q27.target == "handover")
                & (Q27.learner == "logit")][
            ["mechanism", "meaning", "n_levels", "n_seeds", "integral_fine",
             "grid_shift", "seed_sd_median", "V_at_clean", "V_at_empty"]]
        (TABLES / "quality3corpus.tex").write_text(
            tex_table(d,
                      "Register-quality mechanisms as severity CURVES rather "
                      "than points, on the primary log at the reference "
                      "cell. Each row gives the operational failure mode the "
                      "mechanism represents, the number of severities and "
                      "seeds, the integral of the increment against a "
                      "uniform measure on severity, how much coarsening the "
                      "severity grid by a factor of four moves that "
                      "integral, the spread across seeds, and the endpoints.",
                      "tab:quality3corpus",
                      colnames={"meaning": "operational failure mode",
                                "integral_fine": "integral",
                                "grid_shift": "grid shift",
                                "seed_sd_median": "seed s.d.",
                                "V_at_clean": "V complete",
                                "V_at_empty": "V empty"},
                      #  ROUND TWENTY-TWO.  `mask_common' is wider than a
                      #  0.115\linewidth column and spilled past its edge on
                      #  five rows; the mechanism names are a natural-width
                      #  column now and the guarded \resizebox takes up the
                      #  slack.
                      textcols={"operational failure mode": 0.26}),
            encoding="utf-8")
    else:
        blank("quality3corpus", "Register quality as severity curves.",
              "tab:quality3corpus")

    # --------------------------------------------------------------- pilot
    P30 = load("s30_proportions.csv")
    if P30 is not None and len(P30):
        d = P30[["code", "p", "boot_lo", "boot_hi", "design_lo", "design_hi",
                 "wilson_lo", "wilson_hi"]]
        (TABLES / "pilot.tex").write_text(
            tex_table(d,
                      "The pilot's proportions over the estimated eligible "
                      "population, with the stratified bootstrap interval "
                      "this paper reports, the design-based linearised "
                      "interval beside it, and the Wilson interval an "
                      "earlier version printed. None of the five Wilson "
                      "intervals is contained in its design-based "
                      "counterpart.",
                      "tab:pilot",
                      colnames={"p": "estimate",
                                "boot_lo": "boot lo", "boot_hi": "boot hi",
                                "design_lo": "design lo",
                                "design_hi": "design hi",
                                "wilson_lo": "Wilson lo",
                                "wilson_hi": "Wilson hi"}),
            encoding="utf-8")

"""round21_tables -- the tables round twenty-one adds, generated.

Seven new tables, one per major comment that needed one.  Every one is built
from a result file by `make_numbers.tex_table`, so none is typed by hand and
none can disagree with a macro.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_STEP_ORDER = ["the case study as published",
               "the case study, tie-break declared",
               "then the other tie-break rule",
               "then the registered cohort",
               "then the registered target"]

_TAU_LABEL = {"t0_first_touch_all": "T0 first touch, every call",
              "t1_first_touch_escalating": "T1 first touch, escalating only",
              "t2_matched": "T2 incident creation, T1's population",
              "t2_incident_creation": "T2 incident creation"}

_RUNG_LABEL = {"B_intake": "intake",
               "B_intake_g": "intake + group",
               "B_intake_g_km": "intake + group + knowledge"}



def _regions_as_calibrated(load):
    """The reported surface's regions, under the column names the calibrated
    file used.

    ROUND TWENTY-SEVEN.  `s33_regions' is the previous surface's
    coverage-calibrated labels.  The designed surface has no calibrated
    companion --- the factor was fitted for pointwise coverage on the old
    plane and the family-wise widening these families need is larger than it
    supplies --- so the operative labels are the nominal ones.  They are
    aliased here rather than renamed at every use, so the diff is one function
    and not fifty call sites, and so that a reader who greps for `_cal' finds
    this note.
    """
    G = load("s48w_regions.csv")
    if G is None or not len(G):
        return None
    G = G.copy()
    G["cells"] = G.n_cells
    G["beneficial"] = G.n_beneficial
    G["harmful"] = G.n_harmful
    G["unresolved"] = G.n_unresolved
    G["beneficial_cal"] = G.n_beneficial
    G["harmful_cal"] = G.n_harmful
    G["unresolved_cal"] = G.n_unresolved
    G["rho_calibrated"] = G.rho
    G["region_calibrated"] = G.region
    G["q_calibrated"] = G.q
    G["c"] = 1.0
    #  K/n is a property of the pair and not of the calibration, so it is
    #  carried over from the file that measures it rather than recomputed.
    K = load("s42_regions.csv")
    if K is not None and len(K) and "k_over_n" in K.columns:
        G = G.merge(K[["log", "target", "k_over_n"]], on=["log", "target"],
                    how="left")
    else:
        G["k_over_n"] = float("nan")
    return G


def write(mn):
    load, tex_table = mn.load, mn.tex_table
    TABLES = mn.TABLES

    def blank(name, caption, label):
        (TABLES / (name + ".tex")).write_text(
            "\\begin{table}[t]\\centering\\small\n"
            "\\textbf{??} result file absent\n"
            "\\caption{%s}\\label{%s}\\end{table}\n" % (caption, label),
            encoding="utf-8")

    # ---------------------------------------------------------- cohort
    P = load("s32_path.csv")
    if P is not None and len(P):
        d = P.copy()
        d["step"] = pd.Categorical(d.step, _STEP_ORDER, ordered=True)
        d = d.sort_values("step")
        d = d[["step", "cohort", "target", "V", "lo", "hi", "delta"]]
        (TABLES / "cohort.tex").write_text(
            tex_table(d, "The two published values of the register's "
                         "increment at the later decision time, reconciled "
                         "one factor at a time. Each row changes exactly one "
                         "thing from the row above; `delta' is what that "
                         "change is worth. The first row is the number "
                         "Section~\\ref{sec:cmdb} reported and the last is "
                         "the planned contrast \\textsf{PC3} of "
                         "Table~\\ref{tab:confirm}. Intervals are the "
                         "pointwise basic construction at "
                         "\\nCohortDraws\\ draws; the first row has none "
                         "because the ordering it was computed under is not "
                         "reproducible by a rule, which is the subject of "
                         "the second row.",
                      "tab:cohort", floatfmt="%.5f",
                      colnames={"V": "V at the knowledge rung"}),
            encoding="utf-8")
    else:
        blank("cohort", "The cohort reconciliation.", "tab:cohort")

    # ------------------------------------------------------- cohort ANOVA
    A = load("s32_anova.csv")
    if A is not None and len(A):
        d = A[A.effect != "grand mean"].copy()
        d = d.pivot_table(index="effect", columns="rung", values="share")
        d = d.reset_index()
        (TABLES / "cohortanova.tex").write_text(
            tex_table(d, "The exact two-factor decomposition of the "
                         "discrepancy. Share of the variance of $V$ over the "
                         "cohort $\\times$ target design, at each rung of the "
                         "ladder, at a declared tie-break. With two levels "
                         "per factor the decomposition is exact.",
                      "tab:cohortanova"),
            encoding="utf-8")
    else:
        blank("cohortanova", "The decomposition of the discrepancy.",
              "tab:cohortanova")

    # ----------------------------------------------------------- tau
    L = load("s38_ladder.csv")
    if L is not None and len(L):
        #  ROUND TWENTY-TWO, M9.  `lo' and `hi' are two numeric columns of
        #  six characters each and a reader reads them as one interval, so
        #  they are printed as one; that and a wrapping first column let the
        #  table be set at the body font instead of shrunk to fit.
        d = L.copy()
        d["decision time"] = d.decision_time.map(_TAU_LABEL)
        d["baseline"] = d.rung.map(_RUNG_LABEL)
        d["interval"] = ["[%+.3f, %+.3f]" % (a, b)
                         for a, b in zip(d.lo, d.hi)]
        d = d[["decision time", "baseline", "n", "prevalence",
               "card_register", "base_auc", "with_auc", "V", "interval",
               "resolved"]]
        #  THE CAPTION MUST NOT COUNT ROWS BY HAND.  It called the matched
        #  population "the fourth row" when the ladder had gained two rows and
        #  made it the sixth, and Section~\ref{sec:twodecision} repeated the
        #  wrong ordinal.  Both ordinals are computed from the frame the table
        #  is printed from, so a ladder that gains a rung renumbers its own
        #  prose.  \tauMatchedRow and \tauPlainRow carry the same two words
        #  into the body text.
        _ORD = ("first", "second", "third", "fourth", "fifth", "sixth",
                "seventh", "eighth", "ninth", "tenth")

        def _ordinal_of(mask):
            w = [i for i, v in enumerate(list(mask)) if v]
            return _ORD[w[0]] if w and w[0] < len(_ORD) else "??"

        _matched = _ordinal_of(L.decision_time == "t2_matched")
        _plain = _ordinal_of((L.decision_time == "t2_incident_creation")
                             & (L.rung == "B_intake"))
        (TABLES / "tau.tex").write_text(
            tex_table(d, "The decision time implemented as an axis. Each "
                         "moment carries its own population, its own "
                         "register and its own admissible set; the "
                         "PREDICTED TARGET is the same at all of them. "
                         "$\\tau_0$ and $\\tau_1$ differ only in which "
                         "cases are in scope. $\\tau_1$ and $\\tau_2$ "
                         "differ in what is known AND in which cases "
                         "are in scope, because \\nTauTwoUnmatched\\ incidents have no "
                         "interaction record; the %s row is "
                         "$\\tau_2$ restricted to $\\tau_1$'s own "
                         "population, and it is that row, not the "
                         "%s, that makes the "
                         "$\\tau_1$-to-$\\tau_2$ step an information "
                         "step alone. Every row is on the estate's own "
                         "cohort and the reassignment target, under a "
                         "declared tie-break, and every interval is "
                         "the pointwise basic construction at "
                         "\\nTauDraws\\ draws." % (_matched, _plain),
                      "tab:tau",
                      colnames={"card_register": "register levels",
                                "base_auc": "base auc",
                                "with_auc": "with auc"}),
            encoding="utf-8")
    else:
        blank("tau", "The decision time as an axis.", "tab:tau")

    # ------------------------------------------------------ misreport
    M = load("s34_misreport.csv")
    if M is not None and len(M):
        #  ROUND TWENTY-TWO, M9.  Two columns were called `resolved cells'
        #  and `resolved', one a count and one a rate, three columns apart.
        #  The count and the disagreeing count are the numerator and the
        #  denominator of the rate beside them, so they are printed as one
        #  `n / of which disagree' column and the rate is named as a rate.
        d = M[M.measure == "equal-level"].copy()
        d["resolved_cells"] = [
            "%d / %d" % (n, k) for n, k
            in zip(d.n_resolved_calibrated, d.n_disagree_calibrated)]
        d = d[["log", "target", "n_cells", "misreport_all",
               "resolved_cells",
               "misreport_resolved_calibrated", "misreport_magnitude"]]
        (TABLES / "misreport.tex").write_text(
            tex_table(d, "The sign-disagreement rate of a one-number report, "
                         "counted three ways, under the equal-level measure. "
                         "The all-cells rate counts every admissible cell, "
                         "most of whose signs the data do not determine; the "
                         "resolved rate is restricted to the cells whose "
                         "whole-surface band excludes "
                         "zero, and the column before it gives the two counts "
                         "it is computed from; the magnitude rate weights "
                         "every cell "
                         "by $|V|$ as well as by the measure. A pair with no "
                         "resolved cell has no resolved rate and is printed "
                         "with none rather than with zero.",
                      "tab:misreport",
                      colnames={
                          "n_cells": "cells",
                          "misreport_all": "all-cells rate",
                          "resolved_cells":
                              "resolved / of which disagree",
                          "misreport_resolved_calibrated": "resolved rate",
                          "misreport_magnitude": "magnitude rate"}),
            encoding="utf-8")
    else:
        blank("misreport", "The sign-disagreement rate, three ways.",
              "tab:misreport")

    # --------------------------------------------------------- family
    F = load("s34_family.csv")
    if F is not None and len(F):
        d = F.copy()
        #  the interval is printed WITH the statistic rather than in two more
        #  columns: three populations times three numbers is nine columns of
        #  numerals and nobody reads it
        for pop in ("all 19", "itsm 8", "other 11"):
            lo, hi = pop + " lo", pop + " hi"
            if lo in d.columns:
                d[pop] = [("%.3f [%.3f, %.3f]" % (v, a, b))
                          if pd.notna(v) and pd.notna(a) and pd.notna(b)
                          else ("%.3f" % v if pd.notna(v) else "--")
                          for v, a, b in zip(d[pop], d[lo], d[hi])]
        keep = ["statistic", "all 19", "itsm 8", "other 11"]
        d = d[[c for c in keep if c in d.columns]]
        (TABLES / "family.tex").write_text(
            tex_table(d, "Every headline corpus statistic on three "
                         "populations: all nineteen log--target pairs, the "
                         "eight from IT service management where the "
                         "register is a maintained configuration or customer "
                         "register, and the eleven where it is not. Each cell "
                         "is the statistic with a 95\\% percentile interval "
                         "from a cluster bootstrap that resamples LOGS, "
                         "because two targets on the same log share a cohort "
                         "and are not two independent observations. The "
                         "resolved-cell row is a pooled ratio --- "
                         "disagreeing cells over resolved cells, summed "
                         "across the population --- and not a median of "
                         "per-pair rates, which on a population where most "
                         "pairs resolve little prints zero and says nothing.",
                      "tab:family",
                      textcols={"statistic": 0.26, "all 19": 0.20,
                                "itsm 8": 0.20, "other 11": 0.20}),
            encoding="utf-8")
    else:
        blank("family", "Corpus statistics by family.", "tab:family")

    # ------------------------------------------------------- axis kinds
    K = load("s34_axiskind.csv")
    if K is not None and len(K):
        #  ROUND TWENTY-FIVE.  Stacking the two scales as rows doubled this
        #  table to thirty-eight and it ran off the bottom of its page -- a
        #  float taller than its page, which no overfull-hbox check sees.
        #  One row per pair, the two scales side by side, which is also the
        #  arrangement that shows the ordering reversing.
        SHORT = {"raw, within instrument": "raw",
                 "headroom, instrument as an axis": "hdrm"}
        wide = K.copy()
        wide["s"] = wide.scale.map(SHORT).fillna(wide.scale)
        parts = []
        for tag in ("raw", "hdrm"):
            sub = wide[wide.s == tag].set_index(["log", "target"])
            sub = sub[[c for c in ("analyst latitude", "resampling",
                                   "counterfactual", "higher-order")
                       if c in sub.columns]]
            #  ten columns of full words forced \resizebox to shrink this
            #  table to about half the body font, which is legible in a PDF
            #  viewer at 200% and not on paper.  The headings are abbreviated
            #  and the caption glosses them.
            ABBR = {"analyst latitude": "lat.", "resampling": "res.",
                    "counterfactual": "ctf.", "higher-order": "h.o."}
            parts.append(sub.rename(columns=lambda c: "%s %s"
                                    % (ABBR.get(c, c), tag)))
        K = parts[0].join(parts[1], how="outer").reset_index() \
            if len(parts) == 2 else parts[0].reset_index()
        cols = list(K.columns)
        (TABLES / "axiskind.tex").write_text(
            tex_table(K[cols], "The variance decomposition partitioned by "
                               "what KIND of choice each axis is, under both "
                               "declared scales. "
                               "\\emph{Analyst latitude} is the pipeline and "
                               "the baseline rung --- and, on the second "
                               "scale only, the instrument --- things an "
                               "analyst chooses and could have chosen "
                               "otherwise. \\emph{Resampling} is the split, "
                               "five of whose six levels are expanding-origin "
                               "folds on the same data and are therefore "
                               "different samples rather than different "
                               "analyses. \\emph{Counterfactual} is the "
                               "register-quality condition, which is a "
                               "different state of the world. The remainder "
                               "belongs to no single axis. "
                               "\\emph{Columns.} \\textsf{lat.} is analyst "
                               "latitude, \\textsf{res.} resampling, "
                               "\\textsf{ctf.} the counterfactual and "
                               "\\textsf{h.o.} the higher-order remainder; "
                               "\\textsf{raw} and \\textsf{hdrm} are the two "
                               "scales. "
                               "\\emph{Which scale, and why there are two.} "
                               "\\textsf{raw, within instrument} is the "
                               "paper's primary scale: the decomposition is "
                               "taken separately inside each of the five "
                               "instruments, on that instrument's own units, "
                               "and the median is reported --- so the "
                               "instrument is a stratum here and its own "
                               "contribution appears in no column. "
                               "\\textsf{headroom, instrument as an axis} is "
                               "the secondary scale of "
                               "Section~\\ref{sec:sobol}: raw AUC and raw "
                               "average precision do not share units, so "
                               "making the instrument a sixth axis requires "
                               "the headroom rescaling. Every row is the "
                               "equal-level measure. The two scales order "
                               "\\emph{analyst latitude} against "
                               "\\emph{resampling} oppositely, which is a "
                               "property of the scale and not of the corpus; "
                               "Section~\\ref{sec:family} says so rather "
                               "than choosing one.",
                      "tab:axiskind"),
            encoding="utf-8")
    else:
        blank("axiskind", "The decomposition by kind of axis.",
              "tab:axiskind")

    # --------------------------------------------------- calibrated bands
    G = _regions_as_calibrated(load)
    if G is not None and len(G):
        #  ROUND TWENTY-TWO, M9 and the review's table-legibility minor.
        #  Fifteen columns, two of them long region names, made this the one
        #  table \resizebox had to shrink hard enough to matter.  The three
        #  cell counts are one column each and read as a triple anyway, so
        #  they are printed as one `b / h / u' column per critical value;
        #  the total is the same on both, so `unresolved' need not be
        #  repeated.  Ten columns, set at the body font.
        d = G[["log", "target", "k_over_n", "q", "c", "q_calibrated",
               "beneficial", "harmful", "unresolved", "rho", "region",
               "beneficial_cal", "harmful_cal", "rho_calibrated",
               "region_calibrated"]].copy()
        n_cells = d.beneficial + d.harmful + d.unresolved
        d["cells_nominal"] = ["%d / %d / %d" % (b, h, u) for b, h, u
                              in zip(d.beneficial, d.harmful, d.unresolved)]
        d["cells_cal"] = ["%d / %d / %d" % (b, h, n - b - h) for b, h, n
                          in zip(d.beneficial_cal, d.harmful_cal, n_cells)]
        d = d[["log", "target", "k_over_n", "q", "c", "q_calibrated",
               "cells_nominal", "rho", "cells_cal", "rho_calibrated",
               "region_calibrated"]]
        (TABLES / "calbands.tex").write_text(
            tex_table(d, "Resolution regions under the nominal critical "
                         "value and under one calibrated for the register's "
                         "cardinality. $c$ is the inflation factor the "
                         "$(n, K)$ plane of "
                         "Section~\\ref{sec:simsensitivity} gives at that "
                         "pair's own $K/n$; the calibrated critical value is "
                         "$c$ times the nominal one. `q upper' is the "
                         "UPPER end of the critical value's Monte Carlo "
                         "interval, which is the value the bands use by "
                         "the rule of Section~\\ref{sec:simbands} that a "
                         "cell resolves only at the conservative end; the "
                         "point estimate whose corpus median the text "
                         "quotes is smaller. The cell columns are "
                         "beneficial / harmful / unresolved, and the "
                         "admissible count is the same under both critical "
                         "values. The calibrated columns are the ones the "
                         "article's counts use; the nominal ones are printed "
                         "beside them so that the size of the correction is "
                         "visible.",
                      "tab:calbands",
                      colnames={"k_over_n": "K / n",
                                "q_calibrated": "q calibrated",
                                #  ROUND TWENTY-TWO.  This column is the UPPER end of the
                                #  critical value's Monte Carlo interval --
                                #  which is the value the bands use, by the
                                #  rule that a cell resolves only at the
                                #  conservative end -- and it was headed `q',
                                #  which is the point estimate the text quotes.
                                "q": "q upper",
                                "cells_nominal": "cells (nominal)",
                                "cells_cal": "cells (cal)",
                                "rho_calibrated": "rho (cal)",
                                "region_calibrated": "region"}),
            encoding="utf-8")
    else:
        blank("calbands", "Regions under a calibrated critical value.",
              "tab:calbands")

    # ---------------------------------------------------- the plane itself
    C = load("s33_fit.csv")
    if C is not None and len(C):
        cols = ["world", "n_train", "K", "Kn", "n", "coverage_nominal",
                "coverage_nominal_se", "c", "c_lo", "c_hi", "c_applied",
                "c_loglinear"]
        d = C[[c for c in cols if c in C.columns]].copy()
        (TABLES / "plane.tex").write_text(
            tex_table(d, "The coverage calibration. For each cell of the "
                         "$(n, K)$ plane: the coverage the reported interval "
                         "actually attains, and the factor $c$ by which it "
                         "must be widened to attain the nominal level, with "
                         "the Monte Carlo interval of that factor. $c$ is the "
                         "$0.95$ quantile of the studentised error and is "
                         "computed, not searched for. `c applied' is the "
                         "monotone regression the corpus is calibrated with; "
                         "`c log-linear' is the parametric fit whose slope "
                         "Section~\\ref{sec:regions} quotes, printed beside "
                         "it because it sits below the measured factor at "
                         "small ratios and would under-correct there.",
                      "tab:plane",
                      colnames={"Kn": "K / n", "n": "replicates",
                                "coverage_nominal": "coverage at c = 1",
                                "coverage_nominal_se": "se",
                                "c_applied": "c applied",
                                "c_loglinear": "c log-linear"}),
            encoding="utf-8")
    else:
        blank("plane", "The coverage calibration.", "tab:plane")

    # ------------------------------------------------------------- sca
    V = load("s36_verdicts.csv")
    if V is not None and len(V):
        #  ROUND TWENTY-TWO.  `n_cases' and `capped' are printed because the
        #  case cap is a declared budget and a reader is entitled to see
        #  which pairs it bound on rather than to be told a count.  The
        #  per-cell columns the caption does not read are dropped so the
        #  table fits at the body font.
        cols = ["log", "target", "n_cases", "capped", "obs_median",
                "null_median_median", "p_median", "share_positive",
                "sca_verdict", "region_full_surface", "rho_full_surface"]
        d = V[[c for c in cols if c in V.columns]].copy()
        #  ROUND TWENTY-SEVEN, B4.  DEFINITION 3 IS THE DEFINITION, AND THIS
        #  TABLE HAS TO OBEY IT TOO.  `region_full_surface' in
        #  s36_verdicts.csv is the PRE-minimum-share label -- it is
        #  `region_calibrated' of s42_regions.csv, value for value on all
        #  nineteen pairs -- so this table printed `conditionally beneficial'
        #  on BPIC13_incidents/duration, BPIC15_1/duration and
        #  UCI498/handover and `conditionally harmful' on Helpdesk/duration,
        #  whose resolved shares are 1.7%, 1.1%, 4.4% and 1.1% against a
        #  declared minimum of 5%.  The master table was repaired for exactly
        #  this in an earlier round and this one was not, so the two tables
        #  disagreed about the same four cells under captions that both
        #  claimed to print the region of Section~\ref{sec:regions}.  The
        #  applied label is merged from the same file and the same column the
        #  master table reads, `region_min05', so they cannot part company
        #  again without that file disagreeing with itself.
        MINSH = load("s42_regions.csv")
        if (MINSH is not None and len(MINSH)
                and "region_min05" in MINSH.columns):
            d = d.merge(
                MINSH[["log", "target", "region_min05", "share_resolved"]],
                on=["log", "target"], how="left")
            if "region_full_surface" in d.columns:
                d["region_full_surface"] = (
                    d.region_min05.combine_first(d.region_full_surface))
            else:
                d["region_full_surface"] = d.region_min05
            d["resolved share"] = [
                (mn.fmt_fixed(100 * v, 1) if pd.notna(v) else "--")
                for v in d.share_resolved]
            d = d.drop(columns=["region_min05", "share_resolved"])
            #  the share the label rests on sits beside the label, not at the
            #  end of the row, so a reader can see why a direction was
            #  withheld without counting columns
            order = [c for c in d.columns if c != "resolved share"]
            i = order.index("region_full_surface") + 1
            d = d[order[:i] + ["resolved share"] + order[i:]]
        (TABLES / "sca.tex").write_text(
            tex_table(d, "Specification-curve analysis as practised, beside "
                         "this paper's region label. The permutation test "
                         "asks whether the surface as a whole differs from "
                         "one with no signal in it; the region asks, of each "
                         "cell, whether the sign of that cell's own "
                         "increment is determined. Where the two part "
                         "company is what the extra machinery is for. The "
                         #  ROUND TWENTY-SEVEN.  This clause read "BOTH
                         #  verdicts are computed on the declared sub-surface"
                         #  and then, four sentences later, that the region is
                         #  "computed on the full data".  Both cannot be true,
                         #  and the second is: `rho' beside the label is
                         #  0.422 on BPIC13_incidents/handover, which is
                         #  76/180, the full inference family -- not a share
                         #  of twenty-four cells.  Only the permutation test
                         #  runs on the sub-surface.
                         "permutation test runs on the declared "
                         "\\nScaCells-cell sub-surface at \\nScaPerms\\ "
                         "permutations, and `cases' is the number of cases "
                         "it ran on, which is the pair's own "
                         "count unless the declared cap of "
                         "\\nScaMaxCases\\ bound on it. THE REGION IS NOT "
                         "COMPUTED ON THAT SUB-SURFACE: it is the label "
                         "Definition~\\ref{def:regions} yields on the pair's "
                         "whole inference family, "
                         "minimum resolved share included, under the "
                         "operative critical "
                         "value of Section~\\ref{sec:regions}. `Resolved "
                         "share' is the percentage of the inference family "
                         "the band resolves, and a direction is withheld "
                         "below \\minResolvedSharePct\\ of it. THE TWO "
                         "UNRESOLVED LABELS ARE NOT THE SAME STATE: a plain "
                         "`unresolved' is a pair on which the band resolves "
                         "no cell at all, and `unresolved (below minimum "
                         "share)' one on which it resolves some but too few "
                         "to carry a direction --- which is why the count of "
                         "pairs where neither instrument resolves anything "
                         "is taken over the first label only. It is the "
                         "same label, from the same column of the same "
                         "file, as the `region' column of "
                         "Table~\\ref{tab:master}, and "
                         "Table~\\ref{tab:triple} prints the counts "
                         "underneath it.",
                      "tab:sca",
                      colnames={"n_cases": "cases",
                                "obs_median": "observed median",
                                "null_median_median": "null median",
                                "p_median": "p (median)",
                                "share_positive": "share positive",
                                "sca_verdict": "SCA verdict",
                                "region_full_surface": "region",
                                "rho_full_surface": "rho"}),
            encoding="utf-8")
    else:
        blank("sca", "Against specification-curve analysis.", "tab:sca")

    # ----------------------------------------------------------- axes2
    I = load("s37_indices.csv")
    if I is not None and len(I):
        first = I[I.order == 1]
        d = (first.pivot_table(index=["log", "target"], columns="term",
                               values="share", aggfunc="median")
             .reset_index())
        hi = (I[I.order > 1].groupby(["log", "target", "metric"]).share.sum()
              .groupby(level=[0, 1]).median().reset_index(name="higher-order"))
        d = d.merge(hi, on=["log", "target"], how="left")
        (TABLES / "axes2.tex").write_text(
            tex_table(d, "The decomposition with the model family and the "
                         "encoding as separate axes, on the case study's log "
                         "where all six pipelines run. First-order shares, "
                         "median over the five instruments, under the "
                         "equal-level measure, then the total higher-order "
                         "share. The `learner' axis of "
                         "Table~\\ref{tab:sobol} is the two of them "
                         "together.",
                      "tab:axes2"),
            encoding="utf-8")
    else:
        blank("axes2", "Family and encoding, separated.", "tab:axes2")

    # ------------------------------------------------ case-cohort quality
    #  These three file names were WRITTEN BY ANOTHER MODULE in the previous
    #  round, on a different cohort, and that module now writes them under
    #  `*corpus' names.  A file left on disk from before the rename would
    #  survive a build that never regenerated it -- a stale table beside a
    #  fresh macro, which is the defect this whole architecture exists to
    #  prevent -- so the placeholder is written FIRST and overwritten only if
    #  the source is there.
    for _n, _c, _l in (("quality2", "Register quality on the case study's "
                                    "cohort.", "tab:quality2"),
                       ("quality3", "Register quality as severity curves on "
                                    "the case study's cohort.",
                        "tab:quality3"),
                       ("absorption", "Absorption on the case study's "
                                      "cohort.", "tab:absorption")):
        blank(_n, _c, _l)

    Q = load("s39_quality.csv")
    if Q is not None and len(Q):
        d = Q[["mechanism", "level", "populated", "V", "V_sd",
               "n_seeds"]].copy()
        (TABLES / "quality2.tex").write_text(
            tex_table(d, "Register-quality mechanisms on the case study's "
                         "cohort (\\nCohort\\ incidents) and reassignment "
                         "target, at the reference cell. `level' is the "
                         "share populated for the population mechanisms, the "
                         "share corrupted for accuracy, the share of "
                         "identities split for reconciliation and the lag "
                         "for discovery. Stochastic mechanisms are averaged "
                         "over \\nQualitySeeds\\ seeds and the spread across "
                         "seeds is printed beside the mean, because "
                         "mechanism variability and sampling variability are "
                         "different quantities. The corpus-cohort version of "
                         "this table is in Supplement~\\ref{app:tables}.",
                      "tab:quality2",
                      colnames={"V_sd": "spread over seeds",
                                "n_seeds": "seeds"}),
            encoding="utf-8")

    A = load("s39_absorption.csv")
    if A is not None and len(A):
        d = A[A.metric == "auc"].drop(columns=["metric"])
        (TABLES / "absorption.tex").write_text(
            tex_table(d, "Absolute absorption $D = V(f \\mid B_0) - "
                         "V(f \\mid B_1)$ first, with its own interval, then "
                         "the ratio $R$ with its Fieller set and the set's "
                         "kind, on the case study's cohort and reassignment "
                         "target, in ROC AUC. \\nFiellerUnboundedCase\\ of "
                         "\\nFiellerCase\\ reductions across all five "
                         "instruments have a set that is not a bounded "
                         "interval; for those a percentile interval is not a "
                         "summary of anything.",
                      "tab:absorption", floatfmt="%.4f"),
            encoding="utf-8")

    I = load("s39_integrals.csv")
    if I is not None and len(I):
        (TABLES / "quality3.tex").write_text(
            tex_table(I, "Register-quality mechanisms as severity CURVES "
                         "rather than points, on the case study's cohort and "
                         "reassignment target. The integral is taken against "
                         "a uniform measure on severity over "
                         "\\nCaseSweepLevels\\ levels; `grid shift' is how "
                         "much coarsening that grid to five levels moves it, "
                         "which is the check that the summary is a property "
                         "of the curve and not of the grid.",
                      "tab:quality3",
                      colnames={"n_levels": "levels", "n_seeds": "seeds",
                                "integral_coarse": "coarse",
                                "grid_shift": "shift",
                                "seed_sd_median": "seed s.d.",
                                "V_at_clean": "V complete",
                                "V_at_empty": "V empty"}),
            encoding="utf-8")

    # -------------------------------------------------------- desk utility
    R = load("s35_rules.csv")
    if R is not None and len(R):
        d = (R[R.admitted]
             .pivot_table(index="threshold_measure", columns="rule",
                          values="excess_per_1000", aggfunc="median")
             .reset_index())
        n = (R[R.admitted].groupby("threshold_measure")
             .apply(lambda g: int((g.pivot_table(
                 index=["log", "target"], columns="rule",
                 values="excess_per_1000").max(axis=1)
                 - g.pivot_table(index=["log", "target"], columns="rule",
                                 values="excess_per_1000").min(axis=1)
                 > 1e-9).sum()), include_groups=False)
             .reset_index(name="pairs where the rules differ"))
        d = d.merge(n, on="threshold_measure", how="left")
        (TABLES / "desk.tex").write_text(
            tex_table(d, "Median excess regret of each decision rule, in net "
                         "benefit per thousand cases, on the models that "
                         "pass the registered calibration rule. The desk "
                         "distribution places its mass on the exchange rates "
                         "a service desk plausibly holds; the fixed rows "
                         "report single exchange rates so that a reader who "
                         "rejects the distribution still has a number. The "
                         "last column counts the pairs on which the four "
                         "rules do not all lose the same, out of the "
                         "\\nPairsDesk\\ pairs that carry a model the "
                         "calibration rule admits --- NOT out of "
                         "\\nPairs: the rule excludes "
                         "\\nPairsDcaExcluded\\ of them, and a count "
                         "taken over the admitted pairs and printed "
                         "against the corpus total is the defect this "
                         "caption exists to prevent.",
                      "tab:desk", floatfmt="%.4f",
                      colnames={"threshold_measure": "threshold measure"}),
            encoding="utf-8")
    else:
        blank("desk", "The decision rules in net benefit per thousand cases.",
              "tab:desk")


def write_round25(mn):
    """ROUND TWENTY-FIVE.  The band's family-wise coverage, from s41.

    Separated from `write` for the reason `emit_round25` is separated from
    `emit`: a reader tracing a round-25 table should land on a round-25 block.
    `make_numbers.write_tables` calls this once.
    """
    load, tex_table = mn.load, mn.tex_table
    TABLES = mn.TABLES
    import numpy as np
    import pandas as pd

    C = load("s41_coverage.csv")
    if C is None or not len(C):
        (TABLES / "bandcov.tex").write_text(
            "\\begin{table}[t]\\centering\\small\n"
            "\\textbf{??} result file absent\n"
            "\\caption{The band's family-wise coverage.}"
            "\\label{tab:bandcov}\\end{table}\n", encoding="utf-8")
        return

    #  the draw-count sensitivity rows share (family, K) with a grid cell and
    #  are reported in the prose, not here; the table is the matched cells.
    import s41_bandcoverage as S41
    grid = {(K, B) for (K, B, _f, _w) in S41.GRID}
    d = C[[(k, b) in grid for k, b in zip(C.K_nom, C.B)]].copy()
    #  ROUND TWENTY-FIVE.  As one row per (cell, candidate) this is ninety
    #  rows: it ran off the bottom of its page and the page number printed
    #  through it, which no hbox check sees because a float overflowing
    #  VERTICALLY is not an overfull hbox.  The candidates are columns.
    lab = {"q_mult": "multiplier", "q_mult_hi": "mult., MC upper",
           "q_emp": "empirical", "q_emp_hi": "emp., OS upper",
           "q_rad": "Rademacher"}
    d["cand"] = d.candidate.map(lab)
    piv = d.pivot_table(index=["family", "regime", "K_nom", "B"],
                        columns="cand", values="coverage").reset_index()
    ctl = (d[d.candidate == "q_mult"]
           .set_index(["family", "regime", "K_nom", "B"])
           [["coverage_percell_basic"]].reset_index())
    piv = piv.merge(ctl, on=["family", "regime", "K_nom", "B"], how="left")
    piv = piv.rename(columns={"K_nom": "K", "B": "draws",
                              "regime": "draws are",
                              "coverage_percell_basic": "per-cell"})
    order = ["family", "draws are", "K", "draws",
             "multiplier", "mult., MC upper", "empirical", "emp., OS upper",
             "Rademacher", "per-cell"]
    d = piv[[c for c in order if c in piv.columns]].sort_values(
        ["family", "draws are", "K"])
    (TABLES / "bandcov.tex").write_text(
        tex_table(d, "Family-wise coverage of the max-$t$ band against a "
                     "known answer, over synthetic families matched to this "
                     "corpus in size, draw count, cross-cell correlation and "
                     "per-cell excess kurtosis. Nominal is $0.95$; the five "
                     "middle columns are the five candidate critical values "
                     "and the last is the control. "
                     "\\emph{The bootstrap here is ideal} --- the draws come "
                     "from the sampling distribution itself --- so every "
                     "coverage in this table is an upper bound on what the "
                     "real procedure attains, and the control says why: "
                     "\\emph{per-cell} is the basic interval the band is "
                     "built from, on the same draws, and it is short of "
                     "nominal before any multiplicity correction is applied. "
                     "\\emph{Regimes.} \\textsf{gaussian} is the case the "
                     "multiplier bootstrap is derived for; \\textsf{heavy} "
                     "carries this corpus's measured tails; "
                     "\\textsf{degenerate} adds the cells whose net-benefit "
                     "difference is zero by arithmetic, which the corpus's "
                     "decision-curve families contain and its surface "
                     "families do not. Every cell is "
                     "\\nBandCoverageReps\\ replicates, so no coverage here "
                     "is determined worse than \\bandCoverageSEMax.",
                  "tab:bandcov", floatfmt="%.3f"),
        encoding="utf-8")

    # ------------------------------------------- reference sensitivity
    RS = load("s34_refsens.csv")
    if RS is not None and len(RS):
        #  ROUND TWENTY-FIVE.  `quality_level' and `mask_common/0.5' are
        #  internal identifiers, not headings or labels, and an unbreakable
        #  identifier in a p{} column narrower than itself does not wrap, it
        #  spills -- sixteen overfull boxes, which is rule five of the
        #  repository's own notes.  They are relabelled, and the columns go
        #  back to being ordinary ones.
        AXIS = {"declared": "the declared reference", "learner": "pipeline",
                "metric": "instrument", "rung": "baseline rung",
                "split": "split", "quality_level": "register quality"}
        LEVEL = {"hgb": "boosting, target-encoded",
                 "hgb_iso": "boosting, isotonic", "logit_fr": "logistic, "
                 "frequency-encoded", "B_half": "half the intake block",
                 "B_intake": "intake only",
                 "B_intake_g_km": "intake, group and knowledge",
                 "brier_skill": "Brier skill",
                 "logloss_skill": "log-loss skill", "ap": "average precision"}
        d = RS.copy()
        d["axis varied"] = d.axis.map(AXIS).fillna(d.axis)
        d["reference level"] = [
            LEVEL.get(v, str(v).replace("_", " ").replace("/", " at "))
            for v in d.level]
        d = d[["axis varied", "reference level", "n_pairs",
               "misreport_all_median", "misreport_all_min",
               "misreport_all_max"]].rename(columns={
                   "n_pairs": "pairs",
                   "misreport_all_median": "median rate",
                   "misreport_all_min": "min over pairs",
                   "misreport_all_max": "max over pairs"})
        (TABLES / "refsens.tex").write_text(
            tex_table(d, "The headline sign-disagreement rate under a "
                         "different declared reference specification. Each "
                         "row moves the reference ONE axis at a time and "
                         "holds the rest at the declared cell, then "
                         "recomputes the all-cells rate on every pair under "
                         "the equal-level measure; the first row is the "
                         "paper's own reference. The reference supplies the "
                         "sign the other cells are counted as agreeing or "
                         "disagreeing with, so moving it moves which cells "
                         "disagree and nothing else. The median column is "
                         "the corpus median the article quotes; the two "
                         "beside it are over pairs and show that the spread "
                         "within the corpus is far larger than the spread "
                         "across reference specifications.",
                      "tab:refsens", floatfmt="%.3f"),
            encoding="utf-8")
    else:
        (TABLES / "refsens.tex").write_text(
            "\\begin{table}[t]\\centering\\small\n"
            "\\textbf{??} result file absent\n"
            "\\caption{Reference sensitivity.}"
            "\\label{tab:refsens}\\end{table}\n", encoding="utf-8")

    # -------------------------------------------- the four objects, early
    #  ROUND TWENTY-FOUR.  The referees asked, three times, for one summary
    #  table near the front naming the four reporting objects: what each is
    #  for, where it is defined, which table reports it, and what it costs.
    #
    #  This one is EMITTED AS LATEX rather than through `tex_table`, and the
    #  reason is rule four of this repository's notes: `to_latex(escape=True)`
    #  escapes what you pre-escape, so a cell containing \ref{...} prints the
    #  control sequence and a cell containing $\rho$ prints the dollars.  The
    #  first version of this table did exactly that.  Every cell here is prose
    #  and a cross-reference and NOT ONE IS A NUMBER, so nothing can drift
    #  against a result file; the cross-references are LaTeX's own and go
    #  stale loudly.  The cost column is the one thing a reader cannot get
    #  from the text, and it is the property that decides affordability.
    OBJECTS = [
        ("Sensitivity decomposition",
         "how much of the disagreement each analysis choice explains, and "
         "how much belongs to no single one",
         r"\ref{sec:sobol}", r"\ref{tab:sobol}",
         r"exact; no refit. A M\"obius sum over the surface already "
         r"computed"),
        ("Simultaneous band",
         "an interval that holds over every cell a claim quantifies over, "
         "not one cell at a time",
         r"\ref{sec:simbands}", r"\ref{tab:calbands}",
         r"the whole cost: one draw refits every arm of every cell"),
        (r"Resolution region and $\rho$",
         "which way the surface points where the data settle it, and how "
         "much of it they settle",
         r"\ref{sec:regionsdef}", r"\ref{tab:triple}",
         r"a function of the band; no further refit"),
        #  ROUND TWENTY-SIX.  Regret is a robustness check and not a
        #  reporting object; the contribution list says so two pages earlier
        #  and this table contradicted it in its own caption.
        (r"Specification regret \emph{(a check, not an object)}",
         "what choosing one specification costs against the best one, on a "
         "scale a decision can use --- it returns a null on this corpus",
         r"\ref{sec:regretdef}", r"\ref{tab:regret}",
         r"exact; no refit, on the surface already computed"),
    ]
    body = "\n".join(
        r"%s & %s & %s & %s & %s \\" % (o, w, d, t, c)
        for (o, w, d, t, c) in OBJECTS)
    (TABLES / "objects.tex").write_text(
        "\\begin{table}[t]\n\\centering\n\\footnotesize\n"
        "\\setlength{\\tabcolsep}{4pt}%\n"
        "\\renewcommand{\\arraystretch}{1.2}%\n"
        "\\begin{tabular}{"
        #  the two reference columns are `Section~4.6' and `Table~3': narrow,
        #  but `l' lets them set at their natural width and the five columns
        #  then overran the text block by eleven points.  They are p{} too,
        #  so the widths sum to something that fits.
        #  `Section~4.6' is one unbreakable token: a p{} column narrower than
        #  it spills rather than wrapping.  The section and table numbers are
        #  therefore bare refs and the words live in the headings, which are
        #  allowed to wrap.
        ">{\\raggedright\\arraybackslash}p{0.17\\linewidth}"
        ">{\\raggedright\\arraybackslash}p{0.27\\linewidth}"
        "cc"
        ">{\\raggedright\\arraybackslash}p{0.26\\linewidth}}\n"
        "\\toprule\n"
        "object & what it is for & \\S & table & "
        "what it costs \\\\\n\\midrule\n"
        + body +
        "\n\\bottomrule\n\\end{tabular}\n"
        "\\caption{THE REPORTING OBJECTS. The three this paper supplies and "
        "the fourth it retains as a robustness check, what each "
        "is for, where it is defined, where it is reported on this corpus, "
        "and what it costs; the two middle columns are the section it is "
        "defined in and the table that reports it. Only the second costs "
        "model fits: a draw of the "
        "bootstrap refits every arm of every cell, which is why the surface "
        "an inference is taken over is smaller than the surface a point "
        "estimate is taken over (Section~\\ref{sec:threesurfaces}). The "
        "other three are functions of a surface that has already been "
        "computed, so an analyst who has done the sweep has already paid for "
        "them.}\n\\label{tab:objects}\n\\end{table}\n",
        encoding="utf-8")

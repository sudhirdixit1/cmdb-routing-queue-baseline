"""round21_verify -- independent re-derivations of the round-twenty-one
macros, and the consistency conditions the review's first comment requires.

THE CONDITION THAT WOULD HAVE CAUGHT M1.  The case study's headline number
appeared in the manuscript with two values and two signs, because two analyses
of the same log under different cohorts and different targets both produced a
quantity a reader would call "the register's increment at the later decision
time", and nothing required them to agree or to be distinguished.  A verifier
that checks each macro against its own source file cannot catch that: both
macros were right about their own source.

What catches it is a condition on the SET of macros: every macro that names
the same estimand must resolve to the same value, and macros that name
different estimands must not be described by the same words.  `ESTIMANDS`
below is that declaration -- one entry per named quantity, listing the macros
that may hold it -- and the check fails if two members of an entry differ.

The remaining checks are the usual kind: recompute from the row-level file
what make_numbers read from a summary.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

#: Each entry is a quantity a reader would name in one phrase, and the macros
#: that are allowed to hold it.  Two macros in the same entry must agree.  A
#: quantity that legitimately takes two values under two specifications gets
#: TWO entries with different names, and the manuscript must use those names.
ESTIMANDS = {
    #  ROUND TWENTY-SIX.  Round twenty-six computed the pooled decomposition's
    #  medians again, to compare them with the fold-averaged ones, and did it
    #  over a cell set that includes the demoted cross-instrument scale.  The
    #  paper then carried 28.7% and 29.1% for one quantity, and 56.0% and
    #  52.5% for another, four sections apart.  Same name, same idea, one
    #  value each.
    "the pooled higher-order share at the median pair": (
        "interactionTotalPct", "pooledInteractionMedianPct"),
    "the pooled largest first-order index at the median pair": (
        "largestFirstOrderPct", "pooledLargestFirstMedianPct"),
    #  the quantity Section 7 quotes: the estate's cohort and reassignment
    #  target, under the DECLARED tie-break.  s08 and s38 must agree.
    "the register's increment at tau2 against intake plus group plus "
    "knowledge, reassignment cohort, declared tie-break": (
        "VtauTwoKnowledge", "VTtwoKnow"),
    #  the value the case study PRINTED, under the unstable sort the original
    #  analysis used.  It is a different number on purpose -- it is the anchor
    #  of the reconciliation table -- and it is in an entry of its own so that
    #  nothing else may quietly take the same name.
    "the value the case study printed under an undeclared tie-break": (
        "VpublishedTauTwo",),
    "the register's increment at tau2 on the registered cohort and handover "
    "target": ("VregisteredTauTwo",),
    "the register's increment at tau2 against intake plus group, "
    "reassignment cohort": ("VTtwoGroup",),
    "the register's increment against the intake block at incident creation, "
    "reassignment cohort": ("VtauTwo", "VTone"),
    #  ROUND TWENTY-TWO.  Two macros described in the same words four pages
    #  apart -- "the cells the coverage-calibrated whole-surface band
    #  resolves" -- held 892 and 846, and the gap was a join failure nobody
    #  was checking.  They are the same quantity and must agree.
    #  ROUND TWENTY-SEVEN.  The `nResolvedCells*' half of each pair is retired.
    #  It came from the previous surface's calibration file, and the designed
    #  surface has no calibrated companion -- the calibration was fitted on the
    #  old plane and the family-wise widening the new families need is larger
    #  than it supplies, so it is not applied.  This check found the pair
    #  disagreeing across surfaces after the migration, which is what it is
    #  for; the fix is one macro per quantity and not two.
    "the number of cells the nominal band resolves across the corpus": (
        "nResolvedCorpusNominal",),
    #  and the headline sign-disagreement rate, which the abstract, the
    #  conclusion and the Highlights all state
    "the share of resolved cells whose sign disagrees with the reference": (
        "misreportPooledResolvedPct",),
    #  ROUND TWENTY-TWO, found by reading rather than by a check: the count
    #  of ITSM log--target pairs exists under two spellings, one used in
    #  Section 1 and the other in Section 5.  They agree today and nothing
    #  made them.  This is the entry that makes them.
    "the number of ITSM log--target pairs in the corpus": (
        "nITSMPairs", "nItsmPairs"),
}

#: ROUND TWENTY-TWO.  ESTIMANDS above covers POINT estimates, and a referee
#: found the hole that leaves: the same contrast and the same ladder rung
#: were printed with two different INTERVALS, from two runs at two draw
#: counts, in the article and in its own table.  An interval endpoint is a
#: quantity a reader names in one phrase just as a point estimate is, so the
#: endpoints are declared here too, by the macro that must hold them and the
#: result file that is allowed to be their source.
INTERVAL_SOURCES = {
    #  PC3: the planned-contrast run, which is what Table `confirm' prints
    ("pcThreeLo", "pcThreeHi"): ("s24_contrasts.csv", "contrast", "PC3",
                                 "basic_lo", "basic_hi"),
}

#: macros holding a value that must be identical to another macro's, because
#: they are the same number reached by two routes.  Empty at present: every
#: such pair is expressed as an ESTIMANDS entry instead, which carries the
#: quantity's NAME and is therefore the thing a reader can check the prose
#: against.
IDENTITIES = ()


def check(vn, M):
    eq, load = vn.eq, vn.load
    fmt_pct, fmt_num, fmt_thousands = vn.fmt_pct, vn.fmt_num, vn.fmt_thousands
    fmt_sig = vn.fmt_sig

    # ================================================================
    # THE CONDITION FROM M1
    # ================================================================
    for name, macros in ESTIMANDS.items():
        present = {m: M[m] for m in macros if m in M and M[m] != "\\textbf{??}"}
        vals = set(present.values())
        if len(vals) > 1:
            vn.FAILS.append(
                "M1 condition: the macros %s all name %r and hold %s"
                % (", ".join(sorted(present)), name,
                   ", ".join(sorted(vals))))
    for a, b, why in IDENTITIES:
        if a in M and b in M and M[a] != "\\textbf{??}" \
                and M[b] != "\\textbf{??}" and M[a] != M[b]:
            vn.FAILS.append("M1 condition: %s and %s differ (%s vs %s) -- %s"
                            % (a, b, M[a], M[b], why))

    #  ROUND TWENTY-TWO.  An interval endpoint must come from the run the
    #  manuscript says it comes from.  Re-derive each declared endpoint from
    #  its declared source, so that quoting one run's interval beside another
    #  run's p-value fails the build rather than the review.
    for (lo_m, hi_m), (src, key, val, lo_c, hi_c) in INTERVAL_SOURCES.items():
        F = load(src)
        if F is None or not len(F):
            continue
        r = F[F[key] == val]
        if not len(r):
            vn.FAILS.append("interval source: %s has no %s == %r"
                            % (src, key, val))
            continue
        eq(lo_m, fmt_sig(float(r[lo_c].iloc[0]), 5), M,
           "re-derived from %s" % src)
        eq(hi_m, fmt_sig(float(r[hi_c].iloc[0]), 5), M,
           "re-derived from %s" % src)

    # ================================================================
    # THE INFERENCE SURFACE MUST BE A SUBSET OF THE DECLARED SURFACE
    #
    # ROUND TWENTY-TWO.  It was not, on two of nineteen pairs: the bootstrap
    # grid gave the two largest logs the encoding pair of pipelines because
    # boosting refitted in every draw is unaffordable there, while the
    # declared surface gave every non-primary log the family pair.  Sixty of
    # each pair's hundred and twenty band cells therefore had no counterpart
    # in the declaration, and the region labels for those pairs quantified
    # over cells the design space says do not exist.
    #
    # The audit that existed checked level COUNTS.  This checks level
    # IDENTITY, cell for cell, which is the only version that would have
    # caught it.
    # ================================================================
    import spec as _S
    B21 = load("s21_bands.csv.gz")
    if B21 is None:
        B21 = load("s21_bands.csv")
    SUR0 = load("s01_surface.csv")
    if B21 is not None and len(B21) and SUR0 is not None and len(SUR0):
        W = B21[B21.family == "whole-surface"]
        key = ["log", "target", "learner", "split", "quality", "level",
               "rung", "metric"]
        key = [k for k in key if k in W.columns and k in SUR0.columns]
        have = set(map(tuple, SUR0[key].drop_duplicates().values))
        miss = [t for t in map(tuple, W[key].values) if t not in have]
        if miss:
            bad = sorted({(t[0], t[1]) for t in miss})
            vn.FAILS.append(
                "the inference surface is not a subset of the declared "
                "surface: %d band cells on %d pair(s) (%s) have no "
                "counterpart in s01_surface"
                % (len(miss), len(bad),
                   ", ".join("%s/%s" % b for b in bad[:4])))

    # ================================================================
    # the family-relative separation must be family-relative
    #
    # Corollary 1 claims a non-rank-based instrument whose reduction is
    # invariant WITHIN a declared family.  If the witness turned out to be
    # invariant outside it too the corollary would be understated; if the
    # affine shift were not negligible it would be false.  Both directions
    # are checked, because an earlier version stated the claim unrestricted
    # and this file's own evidence refutes that version.
    # ================================================================
    W = load("s29_wider.csv")
    if W is not None and len(W):
        aff = W[W.is_affine]
        non = W[~W.is_affine]
        if len(aff) and float(aff.R_shift.max()) > 1e-9:
            vn.FAILS.append(
                "s29: the corollary's witness is not invariant even inside "
                "the affine family (max shift %.2e)" % float(aff.R_shift.max()))
        if len(non) and float(non.R_shift.max()) < 1e-3:
            vn.FAILS.append(
                "s29: the corollary's witness IS invariant outside the affine "
                "family, so the family-relative statement understates it")
        eq("widerRShiftNonAffine", fmt_num(float(non.R_shift.max()), 3), M,
           "recomputed from s29_wider") if len(non) else None

    # ================================================================
    # s32 -- the cohort reconciliation, recomputed from the cell file
    # ================================================================
    C = load("s32_cells.csv")
    T = load("s32_tiebreak.csv")
    P = load("s32_path.csv")
    if C is not None and len(C):
        km = C[C.rung == "B_intake_g_km"]
        r = km[(km.ordering == "source_order") & (km.cohort == "registered")
               & (km.target == "handover")]
        if len(r):
            eq("VregisteredTauTwo", fmt_sig(float(r.V.iloc[0]), 5), M,
               "recomputed from s32_cells")
        eq("nCohortCells", fmt_thousands(len(C)), M, "counted from s32_cells")
        #  the two declared tie-break rules must agree exactly; if they ever
        #  stop agreeing the reconciliation's story changes and this says so
        a = km[km.ordering == "source_order"].sort_values(["cohort", "target"])
        b = km[km.ordering == "identifier"].sort_values(["cohort", "target"])
        if len(a) == len(b) and len(a):
            d = float(np.max(np.abs(a.V.values - b.V.values)))
            if d > 1e-12:
                vn.FAILS.append(
                    "s32: the two declared tie-break rules differ by %.2e; "
                    "the manuscript says they agree exactly" % d)
    if T is not None and len(T):
        eq("tiebreakRange", fmt_num(float(T.V.max() - T.V.min()), 5), M,
           "recomputed from s32_tiebreak")
        eq("nTiebreakPositive", fmt_thousands(int((T.V > 0).sum())), M)
    if P is not None and len(P):
        #  the path's deltas must telescope to the total difference
        tot = float(P.V.iloc[-1] - P.V.iloc[0])
        add = float(P.delta.dropna().sum())
        if abs(tot - add) > 1e-9:
            vn.FAILS.append("s32: the reconciliation's steps sum to %.6f but "
                            "the endpoints differ by %.6f" % (add, tot))

    # ================================================================
    # s33 -- the calibration, recomputed from the replicates
    # ================================================================
    R = load("s33_replicates.csv")
    F = load("s33_fit.csv")
    G = load("s33_regions.csv")
    if R is not None and len(R) and F is not None and len(F):
        #  the inflation factor is a quantile of the studentised error, so it
        #  is recomputable in three lines from the replicate file
        bad = 0
        for row in F.itertuples():
            sub = R[(R.world == row.world) & (R.n_train == row.n_train)
                    & (R.K == row.K)]
            if len(sub) < 30:
                continue
            L = (sub.V - sub.lo).values
            U = (sub.hi - sub.V).values
            ok = (L > 1e-12) & (U > 1e-12)
            rr = np.maximum((sub.V.values[ok] - row.truth) / L[ok],
                            (row.truth - sub.V.values[ok]) / U[ok])
            if abs(float(np.quantile(rr, 0.95)) - float(row.c)) > 1e-9:
                bad += 1
        if bad:
            vn.FAILS.append("s33: %d cells whose inflation factor is not the "
                            "0.95 quantile of the studentised error" % bad)
        eq("nPlaneCells", fmt_thousands(len(F)), M, "counted from s33_fit")
    if G is not None and len(G):
        #  a calibrated band is wider, so it cannot resolve more cells
        worse = int(((G.beneficial_cal + G.harmful_cal)
                     > (G.beneficial + G.harmful)).sum())
        if worse:
            vn.FAILS.append("s33: %d pairs resolve MORE cells under the "
                            "widened band, which is impossible" % worse)
        #  `nResolvedCellsCalibrated' retired with the calibration; see the
        #  note in the same-quantity table above.
        #  ROUND TWENTY-SEVEN: re-derived from the surface the manuscript
        #  reports, not the previous surface's calibration file.
        #  ROUND TWENTY-SEVEN, LATER THE SAME NIGHT.  This was re-pointed at
        #  the reported surface's NOMINAL rho while the macro's one use site
        #  quotes it as the CALIBRATED median -- what the widening would cost
        #  if it were applied.  Both numbers are wanted and they are two
        #  different numbers; the macro's name says which, so the check
        #  follows the name.
        G33b = load("s33_regions.csv")
        if G33b is not None and len(G33b) and "rho_calibrated" in G33b.columns:
            eq("rhoMedianCalibrated",
               fmt_num(float(G33b.rho_calibrated.median()), 3),
               M, "recomputed from s33_regions, which applies the factor")
        R48 = load("s48w_regions.csv")
        if R48 is not None and len(R48):
            eq("rhoMedian", fmt_num(float(R48.rho.median()), 3),
               M, "recomputed from s48w_regions")

    # ================================================================
    # s34 -- the three sign-disagreement rates
    # ================================================================
    MI = load("s34_misreport.csv")
    if MI is not None and len(MI):
        eq_ = MI[MI.measure == "equal-level"]
        eq("misreportPooledResolvedPct",
           fmt_pct(float(eq_.n_disagree_calibrated.sum()
                         / max(1, eq_.n_resolved_calibrated.sum()))), M,
           "recomputed as a ratio of counts from s34_misreport")
        eq("misreportPooledResolvedNominalPct",
           fmt_pct(float(eq_.n_disagree_nominal.sum()
                         / max(1, eq_.n_resolved_nominal.sum()))), M)
        eq("misreportMagnitudePct",
           fmt_pct(float(eq_.misreport_magnitude.median())), M)
        eq("misreportMedianPct",
           fmt_pct(float(eq_.misreport_all.median())), M,
           "recomputed from s34_misreport, which is where the macro now "
           "comes from")
        eq("misreportMaxPct", fmt_pct(float(eq_.misreport_all.max())), M)
        eq("misreportMinPct", fmt_pct(float(eq_.misreport_all.min())), M)
        eq("misreportLatitudePct",
           fmt_pct(float(eq_.misreport_latitude.median())), M,
           "the rate over the axes an analyst chooses")
        #  the latitude sub-space is a SUBSET, so its cell count cannot
        #  exceed the pair's
        if int((eq_.n_cells_latitude > eq_.n_cells).sum()):
            vn.FAILS.append("s34: the analyst-latitude sub-space has more "
                            "cells than the surface it is a subset of")
        eq("nResolvedCorpus",
           fmt_thousands(int(eq_.n_resolved_calibrated.sum())), M)
        #  the calibrated band is wider, so it cannot resolve more cells
        if int(eq_.n_resolved_calibrated.sum()) > int(
                eq_.n_resolved_nominal.sum()):
            vn.FAILS.append("s34: the calibrated band resolves more cells "
                            "than the nominal one, which is impossible")
        #  a disagreeing resolved cell is a resolved cell
        bad = int((eq_.n_disagree_nominal > eq_.n_resolved_nominal).sum())
        if bad:
            vn.FAILS.append("s34: %d pairs report more disagreeing cells than "
                            "resolved ones" % bad)

    # ================================================================
    # s35 -- the desk utility
    # ================================================================
    RU = load("s35_rules.csv")
    EX = load("s35_excluded.csv")
    if EX is not None and len(EX):
        eq("nModelsDcaAdmitted", fmt_thousands(int(EX.admitted.sum())), M,
           "recounted from s35_excluded")
        eq("nModelsDcaExcluded", fmt_thousands(int((~EX.admitted).sum())), M)
    if RU is not None and len(RU):
        #  excess regret is non-negative by construction
        if float(RU.excess_per_1000.min()) < -1e-12:
            vn.FAILS.append("s35: a negative excess regret, which the "
                            "definition forbids")

    # ================================================================
    # s36 -- the specification-curve comparison
    # ================================================================
    V = load("s36_verdicts.csv")
    N = load("s36_null.csv")
    if V is not None and len(V) and N is not None and len(N):
        bad = 0
        for row in V.itertuples():
            sub = N[(N.log == row.log) & (N.target == row.target)]
            nul = sub[sub.perm >= 0]
            obs = sub[sub.perm < 0]
            if not len(nul) or not len(obs):
                continue
            k = int((np.abs(nul["median"].values)
                     >= abs(float(obs["median"].iloc[0]))).sum())
            p = (k + 1) / (len(nul) + 1)
            if abs(p - float(row.p_median)) > 1e-12:
                bad += 1
        if bad:
            vn.FAILS.append("s36: %d permutation p-values do not match the "
                            "plus-one estimator on the null file" % bad)
        eq("nScaPairs", fmt_thousands(len(V)), M, "counted from s36_verdicts")
        #  ROUND TWENTY-TWO.  The two counts Section 6.7 quotes as the ways
        #  the two instruments part company are derived from the verdicts
        #  file by s36 itself; re-derive them here from the same file with
        #  independent code, which is the only reason to have this script.
        eq("nScaDisagree",
           fmt_thousands(int(((V.p_median <= 0.05)
                              & V.sub_surface_sign_varies).sum())),
           M, "re-derived from s36_verdicts")
        eq("nScaAgreeNull",
           fmt_thousands(int(((V.p_median > 0.05)
                              & (V.region_full_surface == "unresolved")).sum())),
           M, "re-derived from s36_verdicts")
        eq("nScaSubSurfaceDisagree",
           fmt_thousands(int(((~V.sub_surface_sign_varies)
                              & V.region_full_surface.isin(
                                  ["sign-changing",
                                   "conditionally harmful"])).sum())),
           M, "re-derived from s36_verdicts")

    # ================================================================
    # s37 -- the crossed axes
    # ================================================================
    I = load("s37_indices.csv")
    if I is not None and len(I):
        #  the disjoint components of an exact decomposition sum to one
        s = I.groupby(["log", "target", "metric"]).share.sum()
        bad = int(((s - 1.0).abs() > 1e-8).sum())
        if bad:
            vn.FAILS.append("s37: %d decompositions whose components do not "
                            "sum to one" % bad)
        f = I[I.order == 1]
        eq("sFamilyPct",
           fmt_pct(float(f[f.term == "family"].share.median())), M,
           "recomputed from s37_indices")
        eq("sEncodingPct",
           fmt_pct(float(f[f.term == "encoding"].share.median())), M)

    # ================================================================
    # s38 -- the decision-time ladder
    # ================================================================
    L = load("s38_ladder.csv")
    if L is not None and len(L):
        def v(tau, rung="B_intake"):
            m = L[(L.decision_time == tau) & (L.rung == rung)]
            return float(m.V.iloc[0]) if len(m) else np.nan

        v0, v1, v2 = (v("t0_first_touch_all"),
                      v("t1_first_touch_escalating"),
                      v("t2_incident_creation"))
        vm = v("t2_matched")
        eq("deltaCohortAtTau", fmt_sig(v1 - v0, 4), M,
           "recomputed from s38_ladder")
        #  ROUND TWENTY-TWO.  The information step is the one on the MATCHED
        #  population; the unadjusted difference mixes it with the 942
        #  incidents that have no interaction record, and the manuscript
        #  prints the three separately.  The identity that ties them is
        #  checked here rather than left to the reader.
        eq("deltaSnapshotAtTau", fmt_sig(vm - v1, 4), M,
           "the matched-population step, recomputed from s38_ladder")
        eq("deltaPopulationResidual", fmt_sig(v2 - vm, 4), M,
           "recomputed from s38_ladder")
        eq("deltaSnapshotUnmatched", fmt_sig(v2 - v1, 4), M,
           "recomputed from s38_ladder")
        if abs((vm - v1) + (v2 - vm) - (v2 - v1)) > 1e-12:
            vn.FAILS.append("s38: the matched and residual steps do not sum "
                            "to the unadjusted one")
        #  and the matched frame must actually be T1's population
        n1 = float(L[(L.decision_time == "t1_first_touch_escalating")].n.iloc[0])
        nm = float(L[(L.decision_time == "t2_matched")].n.iloc[0])
        if n1 != nm:
            vn.FAILS.append("s38: the matched cohort has %d cases and T1 has "
                            "%d; the information step is not on one "
                            "population" % (nm, n1))
        eq("VtauTwoKnowledge",
           fmt_sig(v("t2_incident_creation", "B_intake_g_km"), 4), M)
        #  the three decision times must differ; a decision-time axis whose
        #  levels agree to every digit is the defect this experiment answers
        if abs(v0 - v2) < 1e-9:
            vn.FAILS.append("s38: the decision-time axis is degenerate -- the "
                            "first and last levels agree exactly")

    # ================================================================
    # the highlights
    #
    # They are GENERATED from the macros now (make_highlights.py), because a
    # hand-written highlights file is the one part of the submission the
    # macro discipline never covered -- and a reviewer found a highlight
    # quoting the nominal sign-disagreement rate beside an abstract quoting
    # the calibrated one.  The check is therefore not only "are they the
    # right length" but "are they what the current macros render to".
    # ================================================================
    from pathlib import Path
    import sys
    HERE = Path(__file__).resolve().parent
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    try:
        txt = (HERE.parent / "submission" / "highlights.txt").read_text(
            encoding="utf-8")
        tail = txt.split("without the length prefixes --")[-1]
        items = [l.strip() for l in tail.splitlines() if l.strip()]
        if not (3 <= len(items) <= 5):
            vn.FAILS.append("highlights: %d bullets; Elsevier allows three "
                            "to five" % len(items))
        over = [i for i in items if len(i) > 85]
        if over:
            vn.FAILS.append("highlights: %d over 85 characters, the longest "
                            "at %d" % (len(over), max(len(i) for i in over)))
        eq("nHighlights", str(len(items)), M, "counted from highlights.txt")
        import make_highlights as MH
        want = MH.render()
        if want != items:
            vn.FAILS.append(
                "highlights: the file does not match what the current macros "
                "render to; run scripts/make_highlights.py")
    except Exception as e:  # noqa: BLE001
        vn.FAILS.append("highlights: could not be read (%s)" % e)

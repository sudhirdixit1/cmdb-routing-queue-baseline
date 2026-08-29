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
        #  THE LIKE-FOR-LIKE COUNTERFACTUAL.  The old count above is measured
        #  on a different design as well as a different scheme, so quoting it
        #  alone credits the resampling change with an improvement the design
        #  change may have supplied.  The multinomial arm was run on THIS
        #  design at THIS draw count, so it isolates the scheme, and it is the
        #  larger number -- reporting only the confounded pair would understate
        #  what weights actually bought.
        _m = mn.RESULTS / "s48m_bands.csv.gz"
        if _m.exists():
            _mw = pd.read_csv(_m)
            _mw = _mw[_mw.family == "whole-surface"]
            put("nUnbandableSameDesign",
                thousands(int(_mw.sim_lo.isna().sum())))
            put("nUnbandableSameDesignOf", thousands(int(len(_mw))))
        else:
            put("nUnbandableSameDesign", None)
            put("nUnbandableSameDesignOf", None)
    else:
        put("nUnbandableCells", None)
        put("nUnbandablePairs", None)
        put("nUnbandableOldCells", None)
        put("nUnbandableSameDesign", None)
        put("nUnbandableSameDesignOf", None)

    # ================================================================
    #  THE BAND'S COVERAGE, SEPARATED BY FAMILY AND BY DESIGN.
    #
    #  The manuscript quoted one median over ALL matched families, pooling
    #  the decision-curve ones with the surface ones -- two sets whose
    #  measured shortfalls it reports SEPARATELY, at 1.36-1.88 and 2.20-2.61,
    #  precisely because they are not the same object.  The pooled median
    #  also spanned draw counts from 33 to 1000 and family sizes from 120 to
    #  2966, while the reported corpus is 180 cells at 400 draws on every
    #  pair -- so the number offered as "this corpus's coverage" was measured
    #  mostly on designs this corpus does not have, and sat two sentences
    #  from the 400-draw figure, disagreeing with it.
    #
    #  Three quantities, because three different questions get asked: the
    #  cell MATCHED TO THE REPORTED DESIGN, the spread across the sensitivity
    #  in size and draw count, and the decision-curve families on their own.
    #  The correction RAISES the headline coverage, which is why it is
    #  reported with its neighbours rather than alone.
    #  THE OTHER ESTIMATOR, AT THE DESIGN THIS CORPUS RUNS.
    #
    #  Section 10 says "no estimator recovers the difference" and Section 4
    #  says the draw count is not the binding constraint.  Both are true of
    #  the MULTIPLIER band and both were checked on medians pooled across
    #  draw counts from 33 to 1000 -- and the empirical quantile behaves
    #  differently along that axis.  Its coverage RISES with the draw count
    #  where the multiplier's plateaus: 0.804 at 33 draws, 0.912 at 80,
    #  0.939 at 150 and 0.947 at 400, which is the count this corpus now runs
    #  on every pair and is within one Monte Carlo standard error of nominal.
    #  The pooled median hid it because half the families it averages over
    #  are at draw counts the corpus abandoned this round.
    CV = load("s41_coverage.csv")
    _cov = ("covHeavyWholeAtDesign", "covHeavyWholeMin", "covHeavyWholeMax",
            "covHeavyDcaMedian", "covHeavyDcaMin", "nBandCovWholeCells",
            "covHeavyWholeAtDesignSE")
    if CV is not None and len(CV) and {"regime", "candidate",
                                       "family"} <= set(CV.columns):
        H = CV[(CV.regime == "heavy") & (CV.candidate == "q_mult")]
        W = H[H.family == "whole-surface"]
        D = H[H.family == "decision-curve"]
        #  the reported design: the corpus's own family size and draw count
        _fam = int(pd.read_csv(mn.RESULTS / "s48w_bands.csv.gz")
                   .query("family == 'whole-surface'")
                   .groupby(["log", "target"]).size().median())
        _b = int(pd.read_csv(mn.RESULTS / "s44_grid.csv").draws.max())
        M180 = W[(W.K_nom == _fam) & (W.B == _b)]
        put("covHeavyWholeAtDesign",
            pct(float(M180.coverage.iloc[0]), 1) if len(M180) else None)
        put("covHeavyWholeAtDesignSE",
            pct(float(M180.coverage_se.iloc[0]), 1) if len(M180) else None)
        put("covHeavyWholeMin",
            pct(float(W.coverage.min()), 1) if len(W) else None)
        put("covHeavyWholeMax",
            pct(float(W.coverage.max()), 1) if len(W) else None)
        put("nBandCovWholeCells", int(len(W)))
        put("covHeavyDcaMedian",
            pct(float(D.coverage.median()), 1) if len(D) else None)
        put("covHeavyDcaMin",
            pct(float(D.coverage.min()), 1) if len(D) else None)
        #  the empirical quantile at the same matched cell, and its own
        #  conservative end, with the width each costs
        E = CV[(CV.regime == "heavy") & (CV.family == "whole-surface")
               & (CV.K_nom == _fam) & (CV.B == _b)]
        def _c(cand, col="coverage"):
            r = E[E.candidate == cand]
            return float(r[col].iloc[0]) if len(r) else None
        _ce, _cm = _c("q_emp"), _c("q_mult")
        put("covEmpWholeAtDesign", pct(_ce, 1) if _ce else None)
        put("covEmpWholeAtDesignSE",
            pct(_c("q_emp", "coverage_se"), 1) if _ce else None)
        put("covEmpHiWholeAtDesign",
            pct(_c("q_emp_hi"), 1) if _c("q_emp_hi") else None)
        _we, _wm = _c("q_emp", "mean_width"), _c("q_mult", "mean_width")
        put("widthEmpOverMultAtDesign",
            num(_we / _wm, 2) if _we and _wm else None)
    else:
        for k in _cov:
            put(k, None)

    # ================================================================
    #  THE REGION LABELS UNDER THE BAND THAT ATTAINS ITS LEVEL.
    #
    #  The empirical quantile covers 94.7% on the family matched to this
    #  corpus's design, against the reported multiplier band's 91.6%, and the
    #  bands file already carries both edges.  So the obvious question a
    #  reader has --- WHAT DO THE LABELS LOOK LIKE UNDER THE CONSTRUCTION
    #  THAT ACTUALLY COVERS? --- is answerable without a new run, and leaving
    #  it unanswered would be reporting the cheaper object because it is the
    #  one already tabulated.
    #
    #  It costs resolution, which is the honest trade and is why the article
    #  still reports the multiplier band.  What it BUYS is the strongest
    #  statement in the paper: the one uniformly beneficial surface survives
    #  it, so rho = 1 is not an artefact of a band that undercovers.
    _bw2 = mn.RESULTS / "s48w_bands.csv.gz"
    _emp = ("nResolvedEmpBand", "nUnifBenEmpBand", "rhoMedianEmpBand",
            "nCondBeneficialEmpBand", "nCondHarmfulEmpBand",
            "nSignChangingEmpBand", "nUnresolvedEmpBand")
    if _bw2.exists():
        import s21_bands as _S21
        _B = pd.read_csv(_bw2)
        _W = _B[_B.family == "whole-surface"].copy()
        _W = _W.assign(_lab=_W.apply(
            lambda r: _S21.label_of(r.emp_lo, r.emp_hi), axis=1))
        _rows = []
        for (_lg, _tg), _s in _W.groupby(["log", "target"]):
            _r, _nb, _nh, _nu = _S21.region_of(_s._lab)
            _rows.append((_r, _nb, _nh, len(_s)))
        _reg = [r for r, _, _, _ in _rows]
        put("nResolvedEmpBand", thousands(sum(b + h for _, b, h, _ in _rows)))
        put("nUnifBenEmpBand", int(_reg.count("uniformly beneficial")))
        put("nCondBeneficialEmpBand",
            int(_reg.count("conditionally beneficial")))
        put("nCondHarmfulEmpBand", int(_reg.count("conditionally harmful")))
        put("nSignChangingEmpBand", int(_reg.count("sign-changing")))
        put("nUnresolvedEmpBand", int(_reg.count("unresolved")))
        put("rhoMedianEmpBand",
            num(float(pd.Series([(b - h) / n for _, b, h, n in _rows])
                      .median()), 3))
    else:
        for _k in _emp:
            put(_k, None)

    # ================================================================
    #  THE DENOMINATOR OF THE ONE UNIFORMLY BENEFICIAL SURFACE.
    #
    #  Section 6.3 quotes the admissible cell count of the pair that attains
    #  rho = 1, and quoted it through a macro NAMED FOR A DIFFERENT PAIR --
    #  right number, wrong pair, because both BPIC14 targets happen to carry
    #  the same count.  A macro whose name is fixed cannot notice that the
    #  pair moved, which is this round's recurring defect.  So the pair is
    #  READ FROM THE REGION FILE rather than named here, and if the region
    #  that attains rho = 1 moves to another pair, these macros move with it.
    _reg = mn.RESULTS / "s48w_regions.csv"
    _ax = mn.RESULTS / "s42_axes.csv"
    if _reg.exists() and _ax.exists():
        _r = pd.read_csv(_reg)
        _u = _r[_r.region.astype(str).str.strip() == "uniformly beneficial"]
        _A = pd.read_csv(_ax)
        _A = _A.assign(_c=_A.n_pipeline * _A.n_split * _A.n_quality
                       * _A.n_rung * _A.n_instrument)
        if len(_u) == 1:
            _log = str(_u.log.iloc[0])
            _tgt = str(_u.target.iloc[0])
            _row = _A[(_A.log == _log) & (_A.target == _tgt)]
            if len(_row):
                _adm = int(_row._c.sum())
                #  the inference family is THE BANDED CELLS OF THAT PAIR --
                #  the same set the label is computed over, not a grid
                #  summary, whose rows are pairs rather than cells.
                _bw = pd.read_csv(mn.RESULTS / "s48w_bands.csv.gz")
                _bw = _bw[(_bw.family == "whole-surface")
                          & (_bw.log == _log) & (_bw.target == _tgt)]
                _fam = int(len(_bw))
                put("nCellsUniformPair", thousands(_adm))
                put("shareUniformFamilyPct",
                    "%.2f\\%%" % (100.0 * _fam / _adm))
                #  IS IT THE SMALLEST SHARE, OR A TIE?  The family size is
                #  constant across pairs by design, so the smallest share is
                #  the largest admissible count -- and two pairs carry it.
                #  "smaller than any other pair's" was therefore false.
                put("nPairsAtLargestGrid",
                    int((_A._c == _A._c.max()).sum()))
            else:
                put("nCellsUniformPair", None)
                put("shareUniformFamilyPct", None)
                put("nPairsAtLargestGrid", None)
        else:
            put("nCellsUniformPair", None)
            put("shareUniformFamilyPct", None)
            put("nPairsAtLargestGrid", None)

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
    #  the decomposition on the inference surface, which the balanced design
    #  makes possible -- Section 4.2 quotes the per-decomposition cell count and
    #  it is NOT the corpus total, which is that number times the pair count.
    F51 = load("s51_facts.csv")
    if F51 is not None and len(F51):
        put("nCellsPerDecomposition",
            thousands(int(first(F51, "n_cells_per_decomposition"))))
        put("nDecompositionsInference",
            thousands(int(first(F51, "n_decompositions"))))
    else:
        put("nCellsPerDecomposition", None)
        put("nDecompositionsInference", None)

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
    #  ROUND TWENTY-SEVEN, AGAIN.  These were read off a column of the
    #  PREVIOUS surface's region file, which no longer carries the labels the
    #  article prints and never carried a `uniformly beneficial' one -- so the
    #  enumeration the appendix printed summed to eighteen over a corpus of
    #  nineteen, and the missing pair was the one the round turns on.  The
    #  rule is short enough to apply here, to the reported surface, and an
    #  enumeration that must sum to the corpus is checked that it does.
    RW = load("s48w_regions.csv")
    R42 = load("s42_regions.csv")
    F42 = load("s42_facts.csv")
    _MS = ("nCondBeneficialMinShare", "nSignChangingMinShare",
           "nCondHarmfulMinShare", "nUniformlyBeneficialMinShare",
           "nUnresolvedMinShare", "nMarkedBelowMinShare",
           "nSignChangingBelowMinShare")
    if (RW is not None and len(RW) and F42 is not None and len(F42)
            and {"n_resolved_whole", "n_cells", "region"} <= set(RW.columns)):
        thr = float(first(F42, "min_resolved_declared"))
        share = RW.n_resolved_whole / RW.n_cells
        lab = RW.region.astype(str).where(share >= thr, "unresolved")
        put("nCondBeneficialMinShare",
            int((lab == "conditionally beneficial").sum()))
        put("nSignChangingMinShare", int((lab == "sign-changing").sum()))
        put("nCondHarmfulMinShare",
            int((lab == "conditionally harmful").sum()))
        put("nUniformlyBeneficialMinShare",
            int((lab == "uniformly beneficial").sum()))
        #  a withdrawn direction is unresolved, and the file spells the two
        #  states differently, so both count here
        put("nUnresolvedMinShare",
            int(lab.str.startswith("unresolved").sum()))
        #  HOW MANY ROWS THE TABLE MARKS, which is not how many directions
        #  the rule withdraws.  A reader counting the marked rows gets a
        #  larger number than the caption's, because a pair already
        #  unresolved is not marked and a SIGN-CHANGING pair is marked while
        #  carrying no direction to withdraw.  Both counts are printed so the
        #  arithmetic is visible instead of looking like a discrepancy.
        _below = share < thr
        put("nMarkedBelowMinShare",
            int((_below & (RW.region.astype(str) != "unresolved")).sum()))
        put("nSignChangingBelowMinShare",
            int((_below
                 & (RW.region.astype(str) == "sign-changing")).sum()))
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

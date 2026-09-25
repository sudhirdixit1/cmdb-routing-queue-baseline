"""round31_verify -- THE FORECAST-EVALUATION CHECKS, RE-DERIVED.

`s60_ijf_checks.py` computes the checks and `round31_numbers.py` turns them
into macros.  This file re-derives every one of those macros WITHOUT either of
them: from the row-level result files the checks were computed from (the
declared surface, the whole-surface band, the stored bootstrap draws, the
stratum and component files) and, for the reference-cell tests, from the
per-case predictions s60 stores -- with its own long-run variance, its own
labelling rule, its own reference-cell lookup and, for the pair-bootstrap
intervals, the EXACT bootstrap distribution of a median rather than a second
Monte Carlo run.  Nothing here imports s60.

It also enforces the conditions the new supplement section's prose rests on,
each a directional or structural claim that no single macro holds:

  1.  The same-metric comparison is made on Section 6.4's resolved cells, and
      read against the AUC reference it reproduces Section 6.4's numerator.
  2.  Every cell that changes status between the two references is a
      proper-score cell of BPIC19, and no cell enters.
  3.  BPIC19's pooled sign-changing label is across metrics only: no metric's
      own cells change sign, the rank metrics resolve only beneficial cells
      and the proper scores only harmful ones.
  4.  Each pair-bootstrap endpoint is a quantile of the exact bootstrap
      distribution of the median, at a level within Monte Carlo reach of the
      declared one, and the interval brackets its point.
  5.  The split's main effect and its interactions partition the
      split-involving stratum, component by component.
  6.  The refitted reference increments equal the reference cell of the
      master table on every pair, to machine precision.
  7.  The rejection counts do not change under the alternative lag the
      section says they survive.
  8.  Both fold-trend statistics lie above their exchangeable-fold null at
      the declared level, which is the direction the prose states.
  9.  The pairs the prose names by name are the pairs the data single out.
 10.  Every comparison the prose states in words holds in that direction.
 11.  The three new tables print, cell for cell, what is re-derived here.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

PAIR = ["log", "target"]
CELL = ["learner", "split", "quality", "level", "rung"]
SCALAR = ("auc", "ap", "brier_skill", "nagelkerke", "logloss_skill")
PROPER = ("brier_skill", "logloss_skill", "nagelkerke")
FOLD = ("rolling1", "rolling2", "rolling3", "rolling4", "rolling5")
MIN_SHARE = 0.05
LEVEL = 0.05
Z95 = 1.6448536269514722

#: the human-readable conditions, appended to verify_numbers.CONDITIONS
CONDITIONS = (
    "the same-metric disagreement count is taken over Section 6.4's resolved "
    "cells, and against the AUC reference reproduces Section 6.4's numerator",
    "every resolved cell that changes status between the AUC reference and "
    "its own metric's reference is a proper-score cell of BPIC19, and none "
    "enters",
    "BPIC19's sign-changing label is a disagreement between metrics: no "
    "metric's own cells change sign",
    "every pair-bootstrap interval endpoint is a quantile of the exact "
    "bootstrap distribution of the median within Monte Carlo reach of its "
    "level, and brackets its point",
    "the split's main effect and its interactions partition the "
    "split-involving stratum on every decomposition, in the order of size "
    "the prose states",
    "the refitted reference increments equal the master table's reference "
    "cell on every pair, and the declared surface's differ in no sign",
    "the reference-cell rejection counts are the same under the alternative "
    "lag",
    "both fold-trend statistics lie above their exchangeable-fold null at "
    "the declared level",
    "the pairs the section names -- the Clark-West reversals and the one "
    "pair that changes sign within a metric -- are the pairs the data "
    "single out",
    "every comparison the section states in words -- intervals that do not "
    "overlap, counts that exceed others, a critical value that falls and "
    "resolutions that rise -- holds in the direction stated",
    "every cell of the per-metric region, by-metric and reference-test "
    "tables is the value re-derived here",
)


def _read(results, name):
    for p in (Path(results) / name, Path(results) / (name + ".gz")):
        if p.exists():
            return pd.read_csv(p)
    return None


def _val(s):
    """A macro's number: math mode, separators and per cent stripped."""
    if s is None:
        return None
    t = re.sub(r"\{,\}", "", str(s)).replace("\\%", "").replace("$", "")
    t = t.strip()
    try:
        return float(t)
    except ValueError:
        return None


def _label(nb, nh, n):
    """Definition 3, written from the definition's text."""
    if nb + nh == 0:
        return "unresolved"
    if (nb + nh) < MIN_SHARE * n:
        return "unresolved (below minimum share)"
    if nb > 0 and nh > 0:
        return "sign-changing"
    if nh == 0:
        return "uniformly beneficial" if nb == n else "conditionally beneficial"
    return "uniformly harmful" if nh == n else "conditionally harmful"


def _hac_var(x, lag):
    """Bartlett long-run variance from the sample autocovariances."""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    gam = np.array([np.dot(x[: n - k], x[k:]) / n for k in range(lag + 1)])
    w = 1.0 - np.arange(lag + 1) / (lag + 1.0)
    return gam[0] + 2.0 * np.sum(w[1:] * gam[1:])


def _tstat(x, lag):
    return float(np.mean(x) / math.sqrt(_hac_var(x, lag) / len(x)))


def _auc(y, p):
    """Mann--Whitney AUC with midranks."""
    from scipy.stats import rankdata
    y = np.asarray(y).astype(int)
    r = rankdata(p)
    n1 = int(y.sum())
    n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def _exact_boot_quantiles(values, lo_level, hi_level):
    """Every value the inverted-CDF quantile of the bootstrap median can take
    for a level in [lo_level, hi_level], from the exact distribution: the
    median of n (odd) resampled values is at most x iff at least (n+1)/2 of
    them are, which is a binomial tail."""
    from scipy.stats import binom
    v = np.sort(np.asarray(values, float))
    n = len(v)
    k = (n + 1) // 2
    xs = np.unique(v)
    cdf = np.array([binom.sf(k - 1, n, np.mean(v <= x)) for x in xs])
    out = set()
    for i, x in enumerate(xs):
        below = cdf[i - 1] if i else 0.0
        #  x is the inverted-CDF quantile for levels in (below, cdf[i]]
        if cdf[i] >= lo_level and below < hi_level:
            out.add(float(x))
    return out


def check(vn, M):
    results = vn.RESULTS
    eq, pct, th = vn.eq, vn.fmt_pct, vn.fmt_thousands
    FAILS = vn.FAILS

    def num(x, d):
        s = vn.fmt_num(x, d)
        return "$-$" + s[1:] if s.startswith("-") else s

    def tol(name, want, tolerance):
        """A Monte Carlo quantity: agreement within `tolerance`, recorded as
        a re-derivation like any other."""
        vn.CHECKED += 1
        vn.VERIFIED.append(name)
        got = _val(M.get(name))
        if got is None:
            FAILS.append("%s: undefined or not a number in numbers.tex" % name)
        elif abs(got - want) > tolerance:
            FAILS.append("%s: numbers.tex has %s, an independent run gives "
                         "%.4f (tolerance %.3f)" % (name, M.get(name), want,
                                                    tolerance))

    SUR = _read(results, "s01_surface.csv")
    BND = _read(results, "s48w_bands.csv")
    REG = _read(results, "s42_regions.csv")
    if SUR is None or BND is None or REG is None:
        FAILS.append("round-31: a source file is missing")
        return
    SUR = SUR[(SUR.rung != "B_empty") & SUR.metric.isin(SCALAR)]
    W = BND[BND.family == "whole-surface"][PAIR + CELL + ["metric", "V",
                                                          "cons_lo",
                                                          "cons_hi"]]
    W = W.rename(columns={"V": "V_inf"})
    X = W.merge(SUR[PAIR + CELL + ["metric", "V"]], on=PAIR + CELL + ["metric"],
                how="left")
    X["res"] = (X.cons_lo > 0) | (X.cons_hi < 0)

    #  the reference cell, looked up directly on its five coordinates
    is_ref = ((SUR.learner == "logit") & (SUR["split"] == "holdout70")
              & (SUR.quality == "clean") & np.isclose(SUR.level, 1.0)
              & (SUR.rung == "B_intake_g"))
    REF = SUR[is_ref].set_index(PAIR + ["metric"]).V
    X["ref_own"] = [REF.get((a, b, m)) for a, b, m in
                    zip(X.log, X.target, X.metric)]
    X["ref_auc"] = [REF.get((a, b, "auc")) for a, b in zip(X.log, X.target)]

    def dis(v, r):
        return np.where(r > 0, v <= 0, v > 0)

    X["d_auc"] = dis(X.V.values, X.ref_auc.values) & X.res.values
    X["d_own"] = dis(X.V.values, X.ref_own.values) & X.res.values
    n_res = int(X.res.sum())

    # ---- T1 ---------------------------------------------------------------
    eq("nDisagreeOwnMetric", th(int(X.d_own.sum())), M)
    eq("misreportOwnMetricPct", pct(X.d_own.sum() / n_res), M)
    leave = X.d_auc & ~X.d_own
    enter = X.d_own & ~X.d_auc
    eq("nLeaveOwnMetric", th(int(leave.sum())), M)
    eq("nEnterOwnMetric", th(int(enter.sum())), M)
    eq("nLeaveBpicNineteenProper",
       th(int((leave & (X.log == "BPIC19") & X.metric.isin(PROPER)).sum())), M)
    eq("nPairsLeaveOwnMetric", th(X[leave].groupby(PAIR).ngroups), M)
    rb = REF.xs("brier_skill", level="metric")
    ra = REF.xs("auc", level="metric")
    differ = (np.sign(rb) != np.sign(ra.reindex(rb.index)))
    eq("nPairsRefSignDiffersBrier", th(int(differ.sum())), M)
    resb = X[X.metric == "brier_skill"].groupby(PAIR).res.sum()
    eq("nPairsRefSignDiffersBrierResolved",
       th(int((differ & (resb.reindex(differ.index) > 0)).sum())), M)
    #  the same counts with each cell's sign, and the reference, read off the
    #  inference surface's own point estimate
    ri = X[(X.learner == "logit") & (X["split"] == "holdout70")
           & (X.quality == "clean") & (X.rung == "B_intake_g")]
    ri = ri.set_index(PAIR + ["metric"]).V_inf
    rio = np.array([ri.get((a, b, m)) for a, b, m in
                    zip(X.log, X.target, X.metric)], float)
    ria = np.array([ri.get((a, b, "auc")) for a, b in zip(X.log, X.target)],
                   float)
    eq("nDisagreeAucRefInferencePoint",
       th(int((dis(X.V_inf.values, ria) & X.res.values).sum())), M)
    eq("nDisagreeOwnRefInferencePoint",
       th(int((dis(X.V_inf.values, rio) & X.res.values).sum())), M)
    #  condition 1
    if (th(n_res) != M.get("nResolvedCorpus")
            or th(int(X.d_auc.sum())) != M.get("nDisagreeResolved")):
        FAILS.append("round-31 condition: the same-metric comparison is not on "
                     "Section 6.4's cells (%d resolved, %d disagreeing with "
                     "the AUC reference; the article has %s and %s)"
                     % (n_res, int(X.d_auc.sum()), M.get("nResolvedCorpus"),
                        M.get("nDisagreeResolved")))
    #  condition 2
    stray = X[(leave & ~((X.log == "BPIC19") & X.metric.isin(PROPER)))
              | enter]
    if len(stray):
        FAILS.append("round-31 condition: %d cells change status outside "
                     "BPIC19's proper scores" % len(stray))

    # ---- T2 ---------------------------------------------------------------
    X["ben"], X["harm"] = X.cons_lo > 0, X.cons_hi < 0
    lab = {}
    for (lg, tg, m), g in X.groupby(PAIR + ["metric"]):
        lab[(lg, tg, m)] = (_label(int(g.ben.sum()), int(g.harm.sum()), len(g)),
                            int(g.ben.sum()), int(g.harm.sum()))
    pooled = REG.set_index(PAIR).region_min05
    stems = {"auc": "Auc", "ap": "Ap", "brier_skill": "Brier",
             "logloss_skill": "Logloss", "nagelkerke": "Nagelkerke"}
    diff_any = set()
    for m, stem in stems.items():
        d = {(a, b) for (a, b, mm), v in lab.items()
             if mm == m and v[0] != pooled.loc[(a, b)]}
        diff_any |= d
        eq("nPairsLabelDiffers" + stem, th(len(d)), M)
    eq("nPairsLabelDiffersAny", th(len(diff_any)), M)
    eq("nPairsAucLabelEqualsBrier",
       th(sum(1 for (a, b) in pooled.index
              if lab[(a, b, "auc")][0] == lab[(a, b, "brier_skill")][0])), M)
    sc_pairs = [p for p in pooled.index if pooled.loc[p] == "sign-changing"]
    eq("nSignChangingWithinMetric",
       th(sum(1 for (a, b) in sc_pairs
              if any(lab[(a, b, m)][0] == "sign-changing" for m in SCALAR))), M)
    eq("nBpicNineteenBenAuc", th(lab[("BPIC19", "duration", "auc")][1]), M)
    eq("nBpicNineteenBenAp", th(lab[("BPIC19", "duration", "ap")][1]), M)
    eq("nBpicNineteenHarmBrier",
       th(lab[("BPIC19", "duration", "brier_skill")][2]), M)
    eq("nBpicNineteenHarmLogloss",
       th(lab[("BPIC19", "duration", "logloss_skill")][2]), M)
    eq("nBpicNineteenHarmNagelkerke",
       th(lab[("BPIC19", "duration", "nagelkerke")][2]), M)
    #  condition 3
    b19 = {m: lab[("BPIC19", "duration", m)] for m in SCALAR}
    ok3 = (pooled.loc[("BPIC19", "duration")] == "sign-changing"
           and all(v[0] != "sign-changing" for v in b19.values())
           and all(b19[m][2] == 0 and b19[m][1] > 0 for m in ("auc", "ap"))
           and all(b19[m][1] == 0 and b19[m][2] > 0 for m in PROPER))
    if not ok3:
        FAILS.append("round-31 condition: BPIC19's label is not a pure "
                     "between-metric disagreement: %r" % b19)

    #  the within-metric families, from the stored draws: an empirical max-t
    #  over the metric's own cells, recentred as the band code recentres
    wdiff = {m: set() for m in SCALAR}
    wres = {}
    q_auc = []
    ddir = Path(results) / "s44_weighted"
    for fn in sorted(ddir.glob("draws_*.csv.gz")):
        D = pd.read_csv(fn)
        D = D[(D.rung != "B_empty") & D.metric.isin(SCALAR)]
        lg, tg = str(D.log.iloc[0]), str(D.target.iloc[0])
        for m in SCALAR:
            g = D[D.metric == m]
            piv = g.pivot_table(index="draw", columns=CELL, values="V")
            pt = piv.loc[-1]
            bt = piv.drop(index=-1)
            sd = bt.std(axis=0, ddof=1)
            keep = sd > 1e-15
            bt, pt, sd = bt.loc[:, keep], pt[keep], sd[keep]
            T = ((bt - bt.mean(axis=0)) / sd).abs().max(axis=1)
            q = float(np.quantile(T.values, 0.95))
            centre = 2 * pt - bt.median(axis=0)
            nb = int((centre - q * sd > 0).sum())
            nh = int((centre + q * sd < 0).sum())
            if _label(nb, nh, len(pt)) != pooled.loc[(lg, tg)]:
                wdiff[m].add((lg, tg))
            wres[m] = wres.get(m, 0) + nb + nh
            if m == "auc":
                q_auc.append(q)
    for m, stem in (("auc", "Auc"), ("brier_skill", "Brier"),
                    ("logloss_skill", "Logloss")):
        eq("nPairsLabelDiffersWithin" + stem, th(len(wdiff[m])), M)
    eq("nPairsLabelDiffersWithinAny",
       th(len(set().union(*wdiff.values()))), M)
    eq("qEmpWithinAucMedian", num(float(np.median(q_auc)), 2), M)
    #  condition 10 (part): with each metric its own family the critical
    #  value falls below the pooled family's and more cells resolve, in every
    #  metric -- the direction the prose states
    pooled_res = X.groupby("metric").res.sum()
    qw = _val(M.get("qEmpWholeMedian"))
    if (qw is None or not float(np.median(q_auc)) < qw
            or any(wres.get(m, 0) <= int(pooled_res[m]) for m in SCALAR)):
        FAILS.append("round-31 condition: the within-metric families do not "
                     "resolve more cells at a lower critical value: %r vs %r"
                     % (wres, pooled_res.to_dict()))

    # ---- T3/T4 ------------------------------------------------------------
    ST = _read(results, "s42_strata.csv")
    CO = _read(results, "s22_components.csv")
    BT = _read(results, "s60_share_boot.csv")
    if ST is None or CO is None or BT is None:
        FAILS.append("round-31: a stratum, component or bootstrap file is "
                     "missing")
        return
    ST = ST[ST.split_set == "all"]
    per_pair = {c: ST.groupby(PAIR)[c].median() for c in
                ("share_resampling", "share_analyst", "share_counterfactual",
                 "share_mixed")}
    CO = CO[(CO.measure == "equal-level") & (CO.scale == "raw-within-metric")
            & CO.metric.isin(SCALAR)].copy()
    CO["ax_set"] = CO.component.str.split("+").apply(frozenset)
    CO["wsplit"] = CO.ax_set.apply(lambda a: "split" in a)
    #  condition 5: main + interactions = involving = the s42 stratum
    inv = CO[CO.wsplit].groupby(PAIR + ["metric"]).share.sum()
    main = CO[CO.ax_set == frozenset({"split"})].set_index(
        PAIR + ["metric"]).share
    inter = CO[CO.wsplit & (CO.ax_set.apply(len) > 1)].groupby(
        PAIR + ["metric"]).share.sum()
    stratum = ST.set_index(PAIR + ["metric"]).share_resampling
    gap = max(float((inv - stratum.reindex(inv.index)).abs().max()),
              float((main.reindex(inv.index) + inter.reindex(inv.index)
                     - inv).abs().max()))
    if not gap < 1e-12:
        FAILS.append("round-31 condition: the split's main effect and "
                     "interactions do not partition the stratum (gap %.2e)"
                     % gap)

    def by_order(k):
        s = CO[CO.wsplit & (CO.ax_set.apply(len) == k)]
        return s.groupby(PAIR + ["metric"]).share.sum()

    def two(ax):
        s = CO[CO.ax_set == frozenset({"split", ax})].set_index(
            PAIR + ["metric"]).share
        return s

    comp = {"split_main": main, "split_interactions": inter,
            "split_two_way": by_order(2), "split_three_way": by_order(3),
            "split_four_way": by_order(4), "split_x_rung": two("rung"),
            "split_x_learner": two("learner"),
            "split_x_quality": two("quality_level")}
    for c, s in comp.items():
        per_pair[c] = s.groupby(level=[0, 1]).median()
    medmac = {"split_main": "splitMainPct",
              "split_interactions": "splitInteractionsPct",
              "split_two_way": "splitTwoWayPct",
              "split_three_way": "splitThreeWayPct",
              "split_four_way": "splitFourWayPct",
              "split_x_rung": "splitRungPct",
              "split_x_learner": "splitLearnerPct",
              "split_x_quality": "splitQualityPct"}
    for c, name in medmac.items():
        eq(name, pct(float(per_pair[c].median())), M)
    #  condition 5, continued: the directional statements the prose makes
    #  about these medians -- interactions more than twice the main effect,
    #  and the two-way terms in the order rung, pipeline, register quality
    md = {c: float(per_pair[c].median()) for c in medmac}
    if not (md["split_interactions"] > 2 * md["split_main"]
            and md["split_x_rung"] > md["split_x_learner"]
            > md["split_x_quality"]):
        FAILS.append("round-31 condition: the split components are not in "
                     "the order the prose states: %r" % md)
    intmac = {"share_resampling": "shareResamplingStratum",
              "share_analyst": "shareAnalystStratum",
              "share_counterfactual": "shareCounterfactualStratum",
              "share_mixed": "shareMixedStratum",
              "split_main": "splitMain",
              "split_interactions": "splitInteractions"}
    bt = BT.set_index("quantity")
    eq("nPairBoot", th(int(bt.n_boot.iloc[0])), M)
    for c, stem in intmac.items():
        vals = per_pair[c].values
        point = float(np.median(vals))
        lo_ok = _exact_boot_quantiles(vals, 0.02, 0.03)
        hi_ok = _exact_boot_quantiles(vals, 0.97, 0.98)
        lo, hi = float(bt.loc[c, "lo"]), float(bt.loc[c, "hi"])
        #  condition 4, and the macro is the file's value
        if (not any(abs(lo - x) < 1e-12 for x in lo_ok)
                or not any(abs(hi - x) < 1e-12 for x in hi_ok)
                or not lo <= point <= hi):
            FAILS.append("round-31 condition: the pair-bootstrap interval "
                         "for %s, [%.4f, %.4f], is not an exact bootstrap "
                         "quantile pair bracketing %.4f" % (c, lo, hi, point))
        eq(stem + "LoPct", pct(lo), M)
        eq(stem + "HiPct", pct(hi), M)
    #  condition 10 (part): the split-involving interval lies wholly above
    #  the other three
    if not float(bt.loc["share_resampling", "lo"]) > max(
            float(bt.loc[c, "hi"]) for c in
            ("share_analyst", "share_counterfactual", "share_mixed")):
        FAILS.append("round-31 condition: the split-involving interval "
                     "overlaps another stratum's")

    # ---- T5 ---------------------------------------------------------------
    for m, stem in (("auc", "Auc"), ("brier_skill", "Brier"),
                    ("logloss_skill", "Logloss")):
        s = ST[ST.metric == m]
        eq("splitShare" + stem + "Pct", pct(float(s.share_resampling.median())),
           M)
        others = s[["share_analyst", "share_counterfactual",
                    "share_mixed"]].max(axis=1)
        eq("nSplitLargest" + stem,
           th(int((s.share_resampling > others).sum())), M)
    for m, name in (("brier_skill", "madResolvedBrierMedian"),
                    ("logloss_skill", "madResolvedLoglossMedian")):
        g = X[(X.metric == m) & X.res].copy()
        g["dev"] = (g.V - g.ref_own).abs()
        eq(name, num(float(g.groupby(PAIR).dev.mean().median()), 4), M)
    #  the no-signal benchmark, by enumerating the components rather than
    #  by the closed form round31_numbers uses
    import itertools as _it
    STR = _read(results, "s42_strata.csv")
    if STR is None:
        FAILS.append("round-31: s42_strata.csv is missing")
    else:
        G = SUR.assign(ql=SUR.quality.astype(str) + "|"
                       + SUR.level.round(6).astype(str))
        lev = G.groupby(PAIR + ["metric"]).agg(
            learner=("learner", "nunique"), split=("split", "nunique"),
            quality=("ql", "nunique"), rung=("rung", "nunique"))
        rows = []
        for key, r in lev.iterrows():
            L = dict(r)
            df = {u: float(np.prod([L[a] - 1 for a in u]))
                  for k in range(1, 5) for u in _it.combinations(L, k)}
            tot = sum(df.values())
            rows.append(key + (sum(v for u, v in df.items() if "split" in u)
                               / tot,
                               sum(v for u, v in df.items()
                                   if set(u) <= {"learner", "rung"}) / tot))
        NL = (pd.DataFrame(rows, columns=PAIR + ["metric", "ns", "na"])
              .groupby(PAIR)[["ns", "na"]].median())
        OB = (STR[STR.split_set == "all"].groupby(PAIR)
              .share_resampling.median())
        NL = NL.join(OB, how="inner")
        eq("splitNullShareMinPct", pct(float(NL.ns.min())), M)
        eq("splitNullShareMaxPct", pct(float(NL.ns.max())), M)
        eq("nPairsSplitBelowNull",
           th(int((NL.share_resampling < NL.ns).sum())), M)
        eq("analystNullSharePct", pct(float(NL.na.median())), M)
    #  the pairs the AUC distance median is taken over (round 26 macro)
    eq("nPairsMadResolved",
       th(int(X[(X.metric == "auc") & X.res].groupby(PAIR).ngroups)), M)
    eq("nResolvedBrier", th(int(X[X.metric == "brier_skill"].res.sum())), M)
    eq("nDisagreeOwnBrier",
       th(int(X[X.metric == "brier_skill"].d_own.sum())), M)
    WV = SUR.pivot_table(index=PAIR + CELL, columns="metric", values="V")
    WV = WV.dropna()
    eq("nSpecsSignAgree", th(len(WV)), M)
    for m, name in (("brier_skill", "signAgreeAucBrierPct"),
                    ("logloss_skill", "signAgreeAucLoglossPct")):
        same = np.sign(WV[m]) == np.sign(WV["auc"])
        eq(name, pct(float(same.mean())), M)
        if m == "brier_skill":
            pp = same.groupby(level=[0, 1]).mean()
            eq("signAgreeAucBrierPairMinPct", pct(float(pp.min())), M)
            eq("signAgreeAucBrierPairMaxPct", pct(float(pp.max())), M)

    # ---- T6 ---------------------------------------------------------------
    PR = _read(results, "s60_reference_predictions.csv")
    CE = _read(results, "s48w_cells.csv")
    if PR is None or CE is None:
        FAILS.append("round-31: the reference predictions or the cell file "
                     "is missing")
        return
    CE = CE[(CE.metric == "auc") & (CE.learner == "logit")
            & (CE["split"] == "holdout70") & (CE.quality == "clean")
            & (CE.rung == "B_intake_g")].set_index(PAIR).V
    RA = REF.xs("auc", level="metric")
    rows = []
    for (lg, tg), g in PR.groupby(PAIR):
        g = g.sort_values("t")
        y, p0, p1 = g.y.values.astype(float), g.p0.values, g.p1.values
        n = len(y)
        lag = int(n ** (1.0 / 3.0))
        while (lag + 1) ** 3 <= n:
            lag += 1
        while lag ** 3 > n:
            lag -= 1
        lag_alt = max(10, int(round(n ** (1.0 / 3.0))))
        q0 = np.clip(p0, 1e-12, 1 - 1e-12)
        q1 = np.clip(p1, 1e-12, 1 - 1e-12)
        dB = (y - p0) ** 2 - (y - p1) ** 2
        dC = dB + (p1 - p0) ** 2
        dL = (y * np.log(q1) + (1 - y) * np.log(1 - q1)
              - y * np.log(q0) - (1 - y) * np.log(1 - q0))
        dauc = _auc(y, p1) - _auc(y, p0)
        rows.append(dict(
            pair=(lg, tg), lag=lag, dauc=dauc,
            tB=_tstat(dB, lag), tC=_tstat(dC, lag), tL=_tstat(dL, lag),
            tBa=_tstat(dB, lag_alt), tCa=_tstat(dC, lag_alt),
            tLa=_tstat(dL, lag_alt), mB=float(dB.mean()),
            mL=float(dL.mean()),
            d_table4=abs(dauc - float(CE.loc[(lg, tg)])),
            d_declared=abs(dauc - float(RA.loc[(lg, tg)]))))
    R6 = pd.DataFrame(rows)
    eq("nRejectDmBrier", th(int((R6.tB > Z95).sum())), M)
    eq("nRejectCw", th(int((R6.tC > Z95).sum())), M)
    eq("nRejectDmLogloss", th(int((R6.tL > Z95).sum())), M)
    eq("nRejectDmBrierAlt", th(int((R6.tBa > Z95).sum())), M)
    eq("nRejectCwAlt", th(int((R6.tCa > Z95).sum())), M)
    eq("nRejectDmLoglossAlt", th(int((R6.tLa > Z95).sum())), M)
    eq("nCwReverses", th(int(((R6.tB < 0) & (R6.tC > Z95)).sum())), M)
    eq("nBrierWorseReference", th(int((R6.mB < 0).sum())), M)
    eq("nAucLoglossSignDiffer",
       th(int((np.sign(R6.dauc) != np.sign(R6.mL)).sum())), M)
    eq("cwLagMin", th(int(R6.lag.min())), M)
    eq("cwLagMax", th(int(R6.lag.max())), M)
    eq("nExactDeclaredAuc", th(int((R6.d_declared < 1e-12).sum())), M)
    #  condition 6.  An independent AUC agrees with the stored one to
    #  rounding, not to the bit, so the macro prints the declared tolerance
    #  and is re-derived as that tolerance when this AUC also meets it.
    tol6 = 1e-12
    if not float(R6.d_table4.max()) < tol6:
        FAILS.append("round-31 condition: a refitted reference increment "
                     "differs from the master table's by %.2e"
                     % float(R6.d_table4.max()))
    else:
        eq("refitTolTableFour", "$10^{-12}$", M)
    #  and where the declared surface differs, it differs in no sign
    flip = [p for p, a in zip(R6.pair, R6.dauc)
            if np.sign(a) != np.sign(float(RA.loc[p]))]
    if flip:
        FAILS.append("round-31 condition: the declared surface's reference "
                     "increment differs in sign from the refit on %r" % flip)
    #  condition 9: the pairs the prose names are the pairs the data name
    named = {("BPIC19", "duration"), ("UCI498", "duration"),
             ("BPIC17", "duration")}
    rev = {p for p, b, c in zip(R6.pair, R6.tB, R6.tC) if b < 0 and c > Z95}
    if rev != named:
        FAILS.append("round-31 condition: the Clark-West reversals are on "
                     "%r, not the pairs the prose names" % sorted(rev))
    within_sc = {(a, b) for (a, b, m), v in lab.items()
                 if v[0] == "sign-changing"}
    if within_sc != {("RoadFines", "duration")} or any(
            lab[("RoadFines", "duration", m)][0] != "sign-changing"
            for m in PROPER) or any(
            lab[("RoadFines", "duration", m)][0] == "sign-changing"
            for m in ("auc", "ap")):
        FAILS.append("round-31 condition: the within-metric sign changes "
                     "are not RoadFines/duration's three proper scores "
                     "alone: %r" % sorted(within_sc))
    dmax = float(R6.d_declared.max())
    e = int(np.floor(np.log10(dmax)))
    eq("refitMaxDiffDeclared",
       "$%.1f \\times 10^{%d}$" % (dmax / 10.0 ** e, e), M)
    #  condition 10 (part): the comparisons of counts the prose makes
    for more, fewer in (("nRejectCw", "nRejectDmBrier"),
                        ("nSplitLargestBrier", "nSplitLargestAuc"),
                        ("nSplitLargestLogloss", "nSplitLargestAuc")):
        a, b = _val(M.get(more)), _val(M.get(fewer))
        if a is None or b is None or not a > b:
            FAILS.append("round-31 condition: %s (%s) is not larger than %s "
                         "(%s)" % (more, M.get(more), fewer, M.get(fewer)))
    #  condition 7
    for a, b in (("nRejectDmBrier", "nRejectDmBrierAlt"),
                 ("nRejectCw", "nRejectCwAlt"),
                 ("nRejectDmLogloss", "nRejectDmLoglossAlt")):
        if M.get(a) != M.get(b):
            FAILS.append("round-31 condition: %s (%s) changes under the "
                         "alternative lag (%s)" % (a, M.get(a), M.get(b)))

    # ---- T7 ---------------------------------------------------------------
    F = SUR[SUR["split"].isin(FOLD)].copy()
    F["k"] = F["split"].str[-1].astype(int)
    prof = {}
    for (lg, tg, m), g in F.groupby(PAIR + ["metric"]):
        P = g.pivot_table(index=["learner", "quality", "level", "rung"],
                          columns="k", values="V").dropna()
        if P.shape[1] != 5:
            continue
        prof.setdefault((lg, tg), {})[m] = P

    def r2(Y, order):
        """R^2 of a straight line in fold index, pooled over rows: the
        between-fold sum of squares a least-squares line removes."""
        Y = Y[:, order]
        k = np.arange(1, 6, dtype=float)
        kc = k - k.mean()
        Yc = Y - Y.mean(axis=1, keepdims=True)
        b = Yc @ kc / (kc @ kc)
        return float(np.sum(np.outer(b, kc) ** 2) / np.sum(Yc ** 2))

    ref_key = ("logit", "clean", 1.0, "B_intake_g")
    import itertools
    orders = [list(o) for o in itertools.permutations(range(5))]
    table = {}
    for pair, bym in prof.items():
        vals = []
        for o in orders:
            vr = [r2(P.loc[[ref_key]].values, o) for P in bym.values()]
            va = [r2(P.values, o) for P in bym.values()]
            vals.append((np.median(vr), np.median(va)))
        table[pair] = np.array(vals)
    ident = 0      # the identity permutation is the first
    obs_r = float(np.median([t[ident, 0] for t in table.values()]))
    obs_a = float(np.median([t[ident, 1] for t in table.values()]))
    eq("foldTrendRefMedian", num(obs_r, 2), M)
    eq("foldTrendAllMedian", num(obs_a, 2), M)
    eq("foldTrendExpected", num(1.0 / (5 - 1), 2), M)
    rng = np.random.default_rng(31)
    B = 20000
    pairs = list(table)
    pick = rng.integers(0, len(orders), size=(B, len(pairs)))
    stack = np.stack([table[p] for p in pairs])          # pairs x 120 x 2
    sims = stack[np.arange(len(pairs))[None, :], pick]   # B x pairs x 2
    null = np.median(sims, axis=1)                       # B x 2
    tol("foldTrendNullRef", float(null[:, 0].mean()), 0.01)
    tol("foldTrendNullAll", float(null[:, 1].mean()), 0.01)
    p_r = float((1 + (null[:, 0] >= obs_r).sum()) / (B + 1.0))
    p_a = float((1 + (null[:, 1] >= obs_a).sum()) / (B + 1.0))
    tol("foldTrendRefP", p_r, 0.005)
    tol("foldTrendAllP", p_a, 0.005)
    #  a declared constant: the macro must be the count the facts file
    #  records the run as having made
    FA = _read(results, "s60_facts.csv")
    eq("nFoldTrendPerm", th(int(FA.foldtrend_n_perm.iloc[0]))
       if FA is not None and len(FA) else None, M)
    #  condition 8
    for name, p in (("foldTrendRefP", p_r), ("foldTrendAllP", p_a)):
        got = _val(M.get(name))
        if got is None or not (got < LEVEL and p < LEVEL):
            FAILS.append("round-31 condition: %s is %s (independent run "
                         "%.4f), not below the declared level"
                         % (name, M.get(name), p))

    # ---- condition 11: the three tables print what is re-derived here ------
    tabdir = Path(vn.PAPER) / "tables"
    abbr = {"uniformly beneficial": "UB", "conditionally beneficial": "CB",
            "sign-changing": "SC", "conditionally harmful": "CH",
            "uniformly harmful": "UH", "unresolved": "U",
            "unresolved (below minimum share)": "U*"}
    bad = []
    rows = _rows(tabdir, "metricregions.tex")
    order = ("auc", "ap", "brier_skill", "logloss_skill", "nagelkerke")
    for r in rows:
        key = (r[0], r[1])
        if (key[0], key[1], "auc") not in lab:
            bad.append("metricregions: unknown pair %r" % (key,))
            continue
        want = [abbr[pooled.loc[key]]] + [
            "%s %d/%d" % (abbr[lab[(key[0], key[1], m)][0]],
                          lab[(key[0], key[1], m)][1],
                          lab[(key[0], key[1], m)][2]) for m in order]
        want.append(str(sum(1 for m in SCALAR if key in wdiff[m])))
        if r[2:] != want:
            bad.append("metricregions %s/%s: %r vs %r"
                       % (key[0], key[1], r[2:], want))
    if len(rows) != len(pooled):
        bad.append("metricregions has %d rows for %d pairs"
                   % (len(rows), len(pooled)))
    C4 = _read(results, "s48w_cells.csv")
    C4 = C4[(C4.learner == "logit") & (C4["split"] == "holdout70")
            & (C4.quality == "clean") & (C4.rung == "B_intake_g")]
    C4 = C4.set_index(PAIR + ["metric"]).V
    got6 = {tuple(r[:2]): r for r in _rows(tabdir, "cwtests.tex")}
    ntest = PR.groupby(PAIR).size()
    for rr in R6.itertuples():
        r = got6.get(rr.pair)
        want = [rr.pair[0], rr.pair[1], str(int(ntest.loc[rr.pair])),
                str(rr.lag), vn.fmt_num(rr.dauc, 4),
                vn.fmt_num(float(C4.loc[rr.pair + ("brier_skill",)]), 4),
                vn.fmt_num(rr.tB, 2), vn.fmt_num(rr.tC, 2),
                vn.fmt_num(rr.tL, 2)]
        if r is None or r != want:
            bad.append("cwtests %s/%s: %r vs %r"
                       % (rr.pair[0], rr.pair[1], r, want))
    if len(got6) != len(R6):
        bad.append("cwtests has %d rows for %d pairs" % (len(got6), len(R6)))
    label = {"AUC": "auc", "average precision": "ap",
             "Brier skill": "brier_skill", "log-loss skill": "logloss_skill",
             "Nagelkerke": "nagelkerke"}
    for r in _rows(tabdir, "bymetric.tex"):
        m = label.get(r[0])
        if m is None:
            bad.append("bymetric: unknown metric %r" % r[0])
            continue
        s = ST[ST.metric == m]
        g = X[(X.metric == m) & X.res]
        dev = (g.V - g.ref_own).abs().groupby([g.log, g.target]).mean()
        same = (np.sign(WV[m]) == np.sign(WV["auc"])).mean()
        big = s.share_resampling > s[["share_analyst", "share_counterfactual",
                                      "share_mixed"]].max(axis=1)
        want = [r[0], vn.fmt_num(100 * s.share_resampling.median(), 1),
                vn.fmt_num(100 * s.share_analyst.median(), 1),
                str(int(big.sum())), str(len(g)), str(int(g.d_auc.sum())),
                str(int(g.d_own.sum())), vn.fmt_num(float(dev.median()), 4),
                vn.fmt_num(100 * float(same), 1)]
        if r != want:
            bad.append("bymetric %s: %r vs %r" % (r[0], r, want))
    if bad:
        FAILS.append("round-31 condition: a new table does not print the "
                     "re-derived value: " + "; ".join(bad[:4]))


def _rows(tabdir, name):
    """Body rows of a generated table, cells stripped and unescaped."""
    p = Path(tabdir) / name
    if not p.exists():
        return []
    t = p.read_text(encoding="utf-8")
    i, j = t.find("\\midrule"), t.find("\\bottomrule")
    out = []
    for line in t[i + len("\\midrule"):j].split("\\\\"):
        line = line.strip()
        if not line:
            continue
        out.append([c.strip().replace("\\_", "_").replace("$-$", "-")
                    for c in line.split("&")])
    return out

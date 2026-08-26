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

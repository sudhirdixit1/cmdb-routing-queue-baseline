"""s03 -- THE SENSITIVITY DECOMPOSITION AND THE RESOLUTION REGIONS.

Round nineteen.  The referee's second major comment is that reporting a grid
of familiar dependencies is practical guidance, not a methodological
contribution, and names what would make it one: a complete specification
surface, a variance or sensitivity decomposition across axes, dominance or
robustness regions, and simultaneous uncertainty.  s01 builds the surface and
s02 supplies the simultaneous uncertainty.  This file builds the other two.

OBJECT 1 -- THE SENSITIVITY DECOMPOSITION.

The surface is a full factorial over the design axes, so the variance of
V_s(f) across specifications admits an exact functional-ANOVA (Sobol)
decomposition.  For axis i,

    S_i   = Var_{X_i}( E[V | X_i] ) / Var(V)            first order
    S_Ti  = 1 - Var_{X_~i}( E[V | X_~i] ) / Var(V)      total, with interactions

S_i answers "how much of the disagreement between analysts is explained by
their choice on axis i alone"; S_Ti - S_i is the part that lives in
interactions with the other axes.  Both are computed on two scales:

  raw      V in the metric's own units, one decomposition per metric, so no
           scale is mixed;
  headroom V / (1 - m(B)), the share of the REMAINING headroom the feature
           captures, which is comparable across the five scalar instruments
           and lets the metric itself enter as an axis.

OBJECT 2 -- THE RESOLUTION REGIONS.

Using s02's simultaneous bands, every admissible cell is labelled

    beneficial     the simultaneous lower band is above zero
    harmful        the simultaneous upper band is below zero
    unresolved     the band contains zero

and the surface as a whole is then

    UNIFORMLY BENEFICIAL      every admissible cell is beneficial
    CONDITIONALLY BENEFICIAL  some beneficial, none harmful
    UNIFORMLY HARMFUL         every admissible cell is harmful
    CONDITIONALLY HARMFUL     some harmful, none beneficial
    SIGN-CHANGING             at least one beneficial and at least one harmful
    UNRESOLVED                no cell resolved

with a scalar ROBUSTNESS INDEX

    rho = ( #beneficial - #harmful ) / #admissible   in [-1, 1].

rho = 1 is the only state in which a single positive number is a safe summary.
The whole point of the paper is that rho = 1 is rare.

    python s03_decompose.py

Outputs: results/s03_sobol.csv, s03_regions.csv, s03_cells.csv, s03_facts.csv
"""
from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

AXES = ("learner", "split", "quality_level", "rung")
SCALARS = list(S.SCALARS)


def _sobol(df, value="V", axes=AXES):
    """Exact first-order and total Sobol indices on a (possibly unbalanced)
    factorial.  Unbalanced cells are handled by taking conditional means over
    whatever levels are present, which is the standard estimator when the
    design is a complete crossing with occasional missing cells."""
    v = df[value].astype(float)
    tot = float(v.var(ddof=0))
    rows = []
    if not np.isfinite(tot) or tot <= 0:
        for a in axes:
            rows.append(dict(axis=a, S=np.nan, S_total=np.nan, levels=0))
        return pd.DataFrame(rows), tot
    for a in axes:
        if df[a].nunique() < 2:
            rows.append(dict(axis=a, S=0.0, S_total=0.0,
                             levels=int(df[a].nunique())))
            continue
        cond = df.groupby(a)[value].mean()
        w = df.groupby(a)[value].size() / float(len(df))
        mu = float((cond * w).sum())
        S_i = float((w * (cond - mu) ** 2).sum()) / tot
        others = [b for b in axes if b != a and df[b].nunique() > 1]
        if others:
            g = df.groupby(others)[value]
            cond2 = g.mean()
            w2 = g.size() / float(len(df))
            mu2 = float((cond2 * w2).sum())
            S_noti = float((w2 * (cond2 - mu2) ** 2).sum()) / tot
        else:
            S_noti = 0.0
        rows.append(dict(axis=a, S=S_i, S_total=max(0.0, 1.0 - S_noti),
                         levels=int(df[a].nunique())))
    return pd.DataFrame(rows), tot


def main():
    t0 = time.time()
    SUR = S.read_results("s01_surface.csv")
    SUR = SUR[~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS)].copy()
    SUR["quality_level"] = (SUR.quality.astype(str) + "@"
                            + SUR.level.map(lambda x: "%.2f" % x))
    SUR["headroom"] = SUR.V / (1.0 - SUR.without_f)

    print("=" * 92)
    print("s03  SENSITIVITY DECOMPOSITION AND RESOLUTION REGIONS")
    print("=" * 92)
    print("  %d surface rows over %d (log, target) pairs"
          % (len(SUR), SUR.groupby(["log", "target"]).ngroups))

    # ---- decomposition, per metric, in the metric's own units ------------
    rows = []
    for (log, target, metric), sub in SUR.groupby(["log", "target", "metric"]):
        if len(sub) < 8:
            continue
        tab, tot = _sobol(sub, "V", AXES)
        for _, r in tab.iterrows():
            rows.append(dict(log=log, target=target, metric=metric,
                             scale="raw", axis=r.axis, S=r.S,
                             S_total=r.S_total, levels=r.levels,
                             var_total=tot, n_cells=len(sub)))
    # ---- decomposition on the headroom scale, with metric as an axis -----
    SC = SUR[SUR.metric.isin(SCALARS)].copy()
    for (log, target), sub in SC.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        tab, tot = _sobol(sub, "headroom", tuple(list(AXES) + ["metric"]))
        for _, r in tab.iterrows():
            rows.append(dict(log=log, target=target, metric="ALL_SCALAR",
                             scale="headroom", axis=r.axis, S=r.S,
                             S_total=r.S_total, levels=r.levels,
                             var_total=tot, n_cells=len(sub)))
    #  and one with the threshold as an axis, over net benefit alone
    NB = SUR[SUR.metric.str.startswith("nb_")].copy()
    NB["threshold"] = NB.metric.str.slice(3).astype(float)
    for (log, target), sub in NB.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        tab, tot = _sobol(sub, "V", tuple(list(AXES) + ["threshold"]))
        for _, r in tab.iterrows():
            rows.append(dict(log=log, target=target, metric="NET_BENEFIT",
                             scale="raw", axis=r.axis, S=r.S,
                             S_total=r.S_total, levels=r.levels,
                             var_total=tot, n_cells=len(sub)))
    #  ---- with the TARGET as an axis, per log ---------------------------
    #  The manuscript lists the target among the axes of the estimand, and
    #  every decomposition above is computed WITHIN a (log, target) pair, so
    #  the target axis is nowhere measured.  It is measured here, over the
    #  logs that carry both registered targets.  The caveat is real and is
    #  stated in the manuscript: two targets are two questions -- they agree
    #  on about half of cases (s16) -- so this index answers "how much of the
    #  disagreement about this REGISTER, on this log, is disagreement about
    #  what to predict", which is a different question from the others and is
    #  labelled as one.
    for log, sub in SC.groupby("log"):
        if sub.target.nunique() < 2 or len(sub) < 32:
            continue
        tab, tot = _sobol(sub, "headroom",
                          tuple(list(AXES) + ["metric", "target"]))
        for _, r in tab.iterrows():
            rows.append(dict(log=log, target="BOTH", metric="ALL_SCALAR",
                             scale="headroom+target", axis=r.axis, S=r.S,
                             S_total=r.S_total, levels=r.levels,
                             var_total=tot, n_cells=len(sub)))

    SOB = pd.DataFrame(rows)
    SOB.to_csv(RESULTS / "s03_sobol.csv", index=False)

    print("\nFIRST-ORDER SOBOL INDICES, headroom scale, all scalar instruments")
    piv = (SOB[(SOB.scale == "headroom")]
           .pivot_table(index=["log", "target"], columns="axis", values="S"))
    print(piv.to_string(float_format=lambda x: "%.3f" % x))

    # ---- resolution regions ---------------------------------------------
    #  s17's bands are s02's, RECENTRED by the bootstrap shift; see s17 for
    #  why that matters with a high-cardinality register.  The raw bands are
    #  the fallback so this file still runs before s17 has, and the region
    #  labels then carry the defect s17 exists to remove.
    BND = pd.DataFrame()
    for name in ("s17_bands.csv", "s02_bands.csv"):
        try:
            BND = pd.read_csv(RESULTS / name)
            if len(BND):
                print("  regions from %s" % name)
                break
        except Exception:  # noqa: BLE001
            continue
    reg_rows, cell_rows = [], []
    if len(BND):
        #  The region is defined over the SCALAR family.  Mixing the
        #  decision-curve cells into it would let a single extreme threshold,
        #  where net benefit is near zero for every model, decide the label of
        #  a whole surface; the decision curve gets its own region, reported
        #  beside the first, and Section 8 reads that one.
        B = BND[(~BND.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (BND.family == "scalars")].copy()
        BD = BND[(~BND.rung.isin(S.IMPLAUSIBLE_RUNGS))
                 & (BND.family == "decision-curve")].copy()
        B["label"] = np.where(B.sim_lo > 0, "beneficial",
                              np.where(B.sim_hi < 0, "harmful", "unresolved"))
        cell_rows = B
        for (log, target), sub in B.groupby(["log", "target"]):
            nb_ = int((sub.label == "beneficial").sum())
            nh = int((sub.label == "harmful").sum())
            nu = int((sub.label == "unresolved").sum())
            n = len(sub)
            if nh and nb_:
                region = "sign-changing"
            elif nb_ and not nh and nu == 0:
                region = "uniformly beneficial"
            elif nb_ and not nh:
                region = "conditionally beneficial"
            elif nh and not nb_ and nu == 0:
                region = "uniformly harmful"
            elif nh and not nb_:
                region = "conditionally harmful"
            else:
                region = "unresolved"
            #  the same labels over the decision curve, reported beside
            dc = BD[(BD.log == log) & (BD.target == target)]
            dcb = int((dc.sim_lo > 0).sum()) if len(dc) else 0
            dch = int((dc.sim_hi < 0).sum()) if len(dc) else 0
            reg_rows.append(dict(log=log, target=target, n_cells=n,
                                 n_beneficial=nb_, n_harmful=nh,
                                 n_unresolved=nu,
                                 rho=(nb_ - nh) / float(n) if n else np.nan,
                                 share_positive=float((sub.V > 0).mean()),
                                 region=region,
                                 dc_cells=len(dc), dc_beneficial=dcb,
                                 dc_harmful=dch,
                                 dc_rho=(dcb - dch) / float(len(dc))
                                 if len(dc) else np.nan))
    REG = pd.DataFrame(reg_rows)
    REG.to_csv(RESULTS / "s03_regions.csv", index=False)
    if len(cell_rows):
        cell_rows.to_csv(RESULTS / "s03_cells.csv", index=False)
    if len(REG):
        print("\nRESOLUTION REGIONS")
        print(REG.to_string(index=False, float_format=lambda x: "%.3f" % x))

    hs = SOB[SOB.scale == "headroom"]
    facts = dict(
        n_surface_rows=len(SUR),
        n_pairs=int(SUR.groupby(["log", "target"]).ngroups),
        n_axes=len(AXES) + 1,
        sobol_rows=len(SOB),
        S_rung_median=float(hs[hs.axis == "rung"].S.median()),
        S_learner_median=float(hs[hs.axis == "learner"].S.median()),
        S_quality_median=float(hs[hs.axis == "quality_level"].S.median()),
        S_split_median=float(hs[hs.axis == "split"].S.median()),
        S_metric_median=float(hs[hs.axis == "metric"].S.median()),
        S_target_median=float(
            SOB[(SOB.scale == "headroom+target")
                & (SOB.axis == "target")].S.median())
        if (SOB.scale == "headroom+target").any() else np.nan,
        n_logs_both_targets=int(
            SOB[SOB.scale == "headroom+target"].log.nunique())
        if (SOB.scale == "headroom+target").any() else 0,
        S_rung_max=float(hs[hs.axis == "rung"].S.max()),
        interaction_share_median=float(
            (hs.S_total - hs.S).clip(lower=0).median()),
        n_regions=len(REG),
        n_uniformly_beneficial=int((REG.region == "uniformly beneficial").sum())
        if len(REG) else 0,
        n_conditionally_beneficial=int(
            (REG.region == "conditionally beneficial").sum())
        if len(REG) else 0,
        #  The mirror of `conditionally beneficial`: cells resolve, and the
        #  ones that resolve resolve to HARM.  One pair in this corpus lands
        #  here, and before it was named it was being counted as unresolved.
        n_conditionally_harmful=int(
            (REG.region == "conditionally harmful").sum())
        if len(REG) else 0,
        n_uniformly_harmful=int((REG.region == "uniformly harmful").sum())
        if len(REG) else 0,
        n_sign_changing=int((REG.region == "sign-changing").sum())
        if len(REG) else 0,
        n_unresolved=int((REG.region == "unresolved").sum()) if len(REG) else 0,
        rho_median=float(REG.rho.median()) if len(REG) else np.nan,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s03_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

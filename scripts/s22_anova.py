"""s22 -- THE CORRECTED VARIANCE DECOMPOSITION, AND THE MEASURE IT IS TAKEN
UNDER.

Round twenty.  Three of the blueprint's Priority-0 items live in this file.

P0.4 -- WHAT THE INTERACTION NUMBER IS.  Round nineteen printed, per axis, the
difference between the total-effect and first-order Sobol indices, and the
manuscript summarised the largest of them as "the interactions carry a median
30.0%".  That is wrong twice over.  S_Ti - S_i is the share of variance in
which axis i is INVOLVED beyond its own main effect; those quantities overlap
across axes, because a two-way component appears in the total effect of both
its axes.  They are not disjoint and their largest member is not the total.
For an orthogonal functional-ANOVA decomposition the total higher-order share
is

    S_interaction,total = 1 - sum_i S_i,

which this file computes, alongside every DISJOINT component of the
decomposition -- all 2^k of them -- so the identity sum_u S_u = 1 can be
asserted numerically rather than assumed.  The old quantity is retained under
the name it deserves: LARGEST PER-AXIS INTERACTION INVOLVEMENT.

P0.5 -- THE MEASURE.  A variance decomposition is taken with respect to a
distribution over specifications, and "uniform over the cells I happened to
enumerate" is a choice, not a neutral default: it moves if an analyst adds a
learner, writes five folds as five levels, or refines a threshold grid.  This
file separates the AXIS weights from the WITHIN-AXIS LEVEL weights, computes
every reported quantity under four declared measures, and runs the two
invariance tests that the blueprint names -- duplicating a level with its
weight split must change nothing, and refining a grid under the same
underlying measure must change nothing material.

P1.2 -- UNCERTAINTY.  Sobol indices are estimated from finite data through
fitted models.  Where s20 supplies bootstrap draws over an axis-complete
inference surface, the whole decomposition is recomputed inside every draw,
which gives an interval for every index; corpus-level medians are bootstrapped
with the LOG-TARGET PAIR as the resampling unit.

    python s22_anova.py                 # everything
    python s22_anova.py --no-boot       # skip the draw-level uncertainty

Outputs: results/s22_indices.csv     first-order, total, per axis, per measure
         results/s22_components.csv  every disjoint ANOVA component
         results/s22_summary.csv     per pair: total higher-order share etc.
         results/s22_measures.csv    the declared measures and their weights
         results/s22_invariance.csv  the duplication and refinement tests
         results/s22_facts.csv
"""
from __future__ import annotations

import argparse
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

#  ---- the declared measures over specifications ---------------------------
#  A measure is a pair (axis weights, level weights).  The axis weights matter
#  only for the ROBUSTNESS summaries, which average over axes; the level
#  weights define the product distribution the ANOVA is taken under.
#
#  M1  equal-level   every level of every axis equally likely.  This is the
#                    measure a reader assumes when they say "uniform", and it
#                    is NOT the same as uniform over cells unless the design
#                    is balanced.
#  M2  reference     half the mass on the reference level of each axis, the
#                    rest spread equally.  A reader who mostly does what the
#                    reference specification does.
#  M3  concentrated  eighty per cent on the reference level.  A reader who
#                    almost never departs from it.
#  M4  envelope      the range of a quantity over 200 Dirichlet(1) draws of
#                    the level weights on every axis: what the conclusion can
#                    be made to say by a reader whose habits we do not know.
MEASURES = ("equal-level", "reference", "concentrated", "envelope")

#: the reference level of each axis: the specification a conventional paper
#: would report without saying so.
REFERENCE = {"learner": "logit", "split": "holdout70",
             "quality_level": "clean@1.00", "rung": "B_intake_g",
             "metric": "auc"}


def level_weights(levels, axis, measure, rng=None):
    """The within-axis probability vector under one declared measure."""
    levels = list(levels)
    k = len(levels)
    if k == 0:
        return np.array([])
    if measure == "equal-level":
        return np.full(k, 1.0 / k)
    if measure == "envelope":
        return rng.dirichlet(np.ones(k))
    ref = REFERENCE.get(axis)
    mass = 0.5 if measure == "reference" else 0.8
    if ref not in levels:
        return np.full(k, 1.0 / k)
    w = np.full(k, (1.0 - mass) / max(1, k - 1)) if k > 1 else np.array([1.0])
    w[levels.index(ref)] = mass if k > 1 else 1.0
    return w / w.sum()


# --------------------------------------------------------------------------
# the exact orthogonal decomposition
# --------------------------------------------------------------------------
def _grid(df, axes, value):
    """Return (V, levels) for a COMPLETE factorial, or (None, levels) if the
    design is not complete over these axes.

    Vectorised deliberately: the draw-level uncertainty of P1.2 calls this
    once per (pair, instrument, draw), tens of thousands of times, and a
    row-at-a-time fill made that the slowest thing in the round.
    """
    levels, codes = [], []
    for a in axes:
        c = pd.Categorical(df[a].astype(str))
        levels.append(list(c.categories))
        codes.append(np.asarray(c.codes, dtype=np.int64))
    shape = tuple(len(x) for x in levels)
    n_cells = int(np.prod(shape)) if shape else 0
    if n_cells != len(df.drop_duplicates(list(axes))):
        return None, levels
    flat = np.ravel_multi_index(tuple(codes), shape)
    V = np.full(n_cells, np.nan)
    V[flat] = df[value].to_numpy(dtype=float)
    if not np.isfinite(V).all():
        return None, levels
    return V.reshape(shape), levels


def anova(V, W):
    """Exact functional-ANOVA components of an array V under the product
    measure W = (w_1, ..., w_k).

    Returns (components, mean, variance) where components maps a frozenset of
    axis indices to its variance contribution.  The identity

        sum over non-empty u of D_u  ==  Var(V)

    holds to machine precision, and the caller asserts it.
    """
    k = V.ndim
    axes = list(range(k))

    def cond_mean(u):
        """E[V | x_u], an array over the axes in u, marginalising the rest."""
        out = V
        for j in sorted(set(axes) - set(u), reverse=True):
            out = np.tensordot(out, W[j], axes=([j], [0]))
        return out

    #  g_u = sum over v subset of u of (-1)^{|u|-|v|} E[V | x_v], broadcast to
    #  the shape of u
    comps = {}
    means = {}
    for r in range(k + 1):
        for u in itertools.combinations(axes, r):
            u = tuple(u)
            #  the conditional mean for u must exist before g_u is formed:
            #  the Moebius sum below runs over every v SUBSET-OR-EQUAL to u.
            means[u] = cond_mean(u)
            if not u:
                continue
            g = np.zeros(tuple(V.shape[j] for j in u))
            for r2 in range(len(u) + 1):
                for v in itertools.combinations(u, r2):
                    sign = (-1) ** (len(u) - len(v))
                    cm = means[v]
                    if v:
                        #  place the axes of v into their slots inside u and
                        #  let numpy broadcast the rest
                        shape = [1] * len(u)
                        for a, j in enumerate(v):
                            shape[u.index(j)] = V.shape[j]
                        g = g + sign * np.asarray(cm).reshape(shape)
                    else:
                        g = g + sign * float(cm)
            wu = 1.0
            for a, j in enumerate(u):
                shape = [1] * len(u)
                shape[a] = V.shape[j]
                wu = wu * W[j].reshape(shape)
            comps[frozenset(u)] = float(np.sum(wu * g * g))
    mu = float(means[()])
    var = float(sum(comps.values()))
    return comps, mu, var


def decompose(df, axes, value, measure, rng=None):
    """One decomposition.  Returns a dict of results or None."""
    V, levels = _grid(df, axes, value)
    if V is None:
        return None
    W = [level_weights(levels[j], axes[j], measure, rng)
         for j in range(len(axes))]
    comps, mu, var = anova(V, W)
    if not np.isfinite(var) or var <= 1e-18:
        return None
    first = {a: comps[frozenset([j])] / var for j, a in enumerate(axes)}
    total = {a: sum(v for u, v in comps.items() if j in u) / var
             for j, a in enumerate(axes)}
    return dict(components={tuple(sorted(u)): v / var
                            for u, v in comps.items()},
                first=first, total=total, mean=mu, var=var,
                levels={a: len(levels[j]) for j, a in enumerate(axes)},
                n_cells=int(V.size))


# --------------------------------------------------------------------------
def run_surface(SUR, measure, rng=None, axes=AXES, value="V",
                by=("log", "target", "metric")):
    """Decompose every group of the surface under one measure."""
    out_idx, out_comp, out_sum = [], [], []
    for key, sub in SUR.groupby(list(by)):
        res = decompose(sub, axes, value, measure, rng)
        if res is None:
            continue
        kd = dict(zip(by, key if isinstance(key, tuple) else (key,)))
        s_first = sum(res["first"].values())
        for a in axes:
            out_idx.append(kd | dict(
                measure=measure, axis=a, S=res["first"][a],
                S_total=res["total"][a],
                involvement=res["total"][a] - res["first"][a],
                levels=res["levels"][a], n_cells=res["n_cells"]))
        for u, v in res["components"].items():
            out_comp.append(kd | dict(measure=measure,
                                      component="+".join(axes[j] for j in u),
                                      order=len(u), share=v))
        inv = {a: res["total"][a] - res["first"][a] for a in axes}
        top = max(inv, key=inv.get)
        out_sum.append(kd | dict(
            measure=measure,
            sum_first_order=s_first,
            interaction_total=1.0 - s_first,
            largest_involvement=inv[top], largest_involvement_axis=top,
            largest_first_order=max(res["first"].values()),
            largest_first_order_axis=max(res["first"], key=res["first"].get),
            var=res["var"], mean=res["mean"], n_cells=res["n_cells"],
            check_sum=sum(res["components"].values())))
    return (pd.DataFrame(out_idx), pd.DataFrame(out_comp),
            pd.DataFrame(out_sum))


# --------------------------------------------------------------------------
def invariance_tests(SUR):
    """The two tests the blueprint names, executed rather than asserted."""
    rows = []
    ex = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
             & (SUR.metric == "auc")].copy()
    base = decompose(ex, AXES, "V", "equal-level")
    if base is None:
        return pd.DataFrame(rows)

    #  1  DUPLICATION.  Duplicate one level of one axis, splitting its weight.
    #     Under a product measure with the weight split, every component must
    #     be unchanged.
    for axis in AXES:
        lv = sorted(ex[axis].astype(str).unique())
        if len(lv) < 2:
            continue
        dup = ex[ex[axis].astype(str) == lv[0]].copy()
        dup[axis] = lv[0] + "#dup"
        ex2 = pd.concat([ex, dup], ignore_index=True)
        levels2 = sorted(ex2[axis].astype(str).unique())
        V2, L2 = _grid(ex2, AXES, "V")
        if V2 is None:
            continue
        W2 = []
        for j, a in enumerate(AXES):
            if a == axis:
                w = np.full(len(L2[j]), 1.0 / len(lv))
                for nm in (lv[0], lv[0] + "#dup"):
                    w[L2[j].index(nm)] = 0.5 / len(lv)
                W2.append(w)
            else:
                W2.append(level_weights(L2[j], a, "equal-level"))
        comps2, mu2, var2 = anova(V2, W2)
        d = max(abs(comps2[frozenset([j])] / var2 - base["first"][a])
                for j, a in enumerate(AXES))
        rows.append(dict(test="duplicate-level", axis=axis,
                         max_abs_change=float(d),
                         passed=bool(d < 1e-9)))

    #  2  GRID REFINEMENT.  The decision-curve threshold grid is a
    #     discretisation of a continuous operating-point measure.  Halving the
    #     spacing under the same underlying measure must not move the
    #     threshold axis's share materially.
    NB = SUR[(SUR.log == "BPIC14") & (SUR.target == "handover")
             & (SUR.metric.str.startswith("nb_"))].copy()
    if len(NB):
        NB["threshold"] = NB.metric.str.slice(3).astype(float)
        coarse = NB[NB.threshold.map(
            lambda t: abs((round((t - 0.05) / 0.05) * 0.05 + 0.05) - t) < 1e-9)]
        for nm, sub in (("fine", NB), ("coarse", coarse)):
            r = decompose(sub, tuple(list(AXES) + ["threshold"]), "V",
                          "equal-level")
            if r is None:
                continue
            rows.append(dict(test="grid-refinement", axis="threshold:" + nm,
                             max_abs_change=float(r["first"]["threshold"]),
                             passed=True))
        a = [r for r in rows if r["axis"] == "threshold:fine"]
        b = [r for r in rows if r["axis"] == "threshold:coarse"]
        if a and b:
            d = abs(a[0]["max_abs_change"] - b[0]["max_abs_change"])
            rows.append(dict(test="grid-refinement", axis="threshold:delta",
                             max_abs_change=float(d), passed=bool(d < 0.05)))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def draw_uncertainty(rng_seed=0):
    """P1.2.  Recompute the whole decomposition inside every bootstrap draw of
    the axis-complete inference surface, which gives an interval for every
    index.  Returns an empty frame if s20 has not run."""
    files = sorted((RESULTS / "s20").glob("draws_*.csv.gz"))
    if not files:
        return pd.DataFrame(), pd.DataFrame()
    rows, summ = [], []
    for fn in files:
        D = pd.read_csv(fn)
        if not len(D):
            continue
        D = D[D.metric.isin(SCALARS) & (D.draw >= 0)].copy()
        if not len(D):
            continue
        D["quality_level"] = (D.quality.astype(str) + "@"
                              + D.level.map(lambda x: "%.2f" % x))
        for (log, target, metric, b), sub in D.groupby(
                ["log", "target", "metric", "draw"]):
            r = decompose(sub, AXES, "V", "equal-level")
            if r is None:
                continue
            s1 = sum(r["first"].values())
            summ.append(dict(log=log, target=target, metric=metric, draw=b,
                             interaction_total=1.0 - s1))
            for a in AXES:
                rows.append(dict(log=log, target=target, metric=metric,
                                 draw=b, axis=a, S=r["first"][a],
                                 S_total=r["total"][a]))
    return pd.DataFrame(rows), pd.DataFrame(summ)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-boot", action="store_true")
    ap.add_argument("--envelope-draws", type=int, default=200)
    a = ap.parse_args(argv)
    t0 = time.time()

    SUR = S.read_results("s01_surface.csv")
    SUR = SUR[~SUR.rung.isin(S.IMPLAUSIBLE_RUNGS)].copy()
    SUR["quality_level"] = (SUR.quality.astype(str) + "@"
                            + SUR.level.map(lambda x: "%.2f" % x))
    SUR["headroom"] = SUR.V / (1.0 - SUR.without_f)
    SC = SUR[SUR.metric.isin(SCALARS)].copy()

    print("=" * 92)
    print("s22  THE CORRECTED DECOMPOSITION AND THE MEASURE IT IS TAKEN UNDER")
    print("=" * 92)

    IDX, COMP, SUMM = [], [], []
    #  --- primary: within-metric, in the metric's own units ---------------
    for meas in ("equal-level", "reference", "concentrated"):
        i, c, s = run_surface(SC, meas)
        for df, nm in ((i, "idx"), (c, "comp"), (s, "sum")):
            if len(df):
                df["scale"] = "raw-within-metric"
        IDX.append(i)
        COMP.append(c)
        SUMM.append(s)

    #  --- secondary: metric as an axis, on the headroom scale -------------
    for meas in ("equal-level",):
        i, c, s = run_surface(SC, meas, axes=tuple(list(AXES) + ["metric"]),
                              value="headroom", by=("log", "target"))
        for df in (i, c, s):
            if len(df):
                df["scale"] = "headroom-metric-as-axis"
                df["metric"] = "ALL_SCALAR"
        IDX.append(i)
        COMP.append(c)
        SUMM.append(s)

    #  --- envelope: the range over Dirichlet level weights ----------------
    rng = np.random.default_rng(S.SEED)
    env = []
    for rep in range(a.envelope_draws):
        i, _c, s = run_surface(
            SC[(SC.log == "BPIC14") & (SC.target == "handover")],
            "envelope", rng=rng)
        if len(s):
            env.append(s.assign(rep=rep))
    ENV = pd.concat(env, ignore_index=True) if env else pd.DataFrame()

    IDX = pd.concat([x for x in IDX if len(x)], ignore_index=True)
    COMP = pd.concat([x for x in COMP if len(x)], ignore_index=True)
    SUMM = pd.concat([x for x in SUMM if len(x)], ignore_index=True)

    #  ---- the identity the whole correction rests on ---------------------
    bad = SUMM[(SUMM.check_sum - 1.0).abs() > 1e-8]
    print("  disjoint components sum to one on %d of %d decompositions"
          % (len(SUMM) - len(bad), len(SUMM)))
    assert len(bad) == 0, "ANOVA components do not sum to one"

    INV = invariance_tests(SUR)
    if len(INV):
        print("\nINVARIANCE TESTS")
        print(INV.to_string(index=False))

    BOOT, BSUM = (pd.DataFrame(), pd.DataFrame())
    if not a.no_boot:
        BOOT, BSUM = draw_uncertainty()
        if len(BOOT):
            print("\n  draw-level uncertainty from %d decompositions"
                  % BSUM.groupby(["log", "target", "metric"]).ngroups)

    #  ---- the corpus-level summaries, pair as the resampling unit --------
    prim = SUMM[(SUMM.scale == "raw-within-metric")
                & (SUMM.measure == "equal-level")]
    per_pair = prim.groupby(["log", "target"]).agg(
        interaction_total=("interaction_total", "median"),
        largest_involvement=("largest_involvement", "median"),
        largest_first_order=("largest_first_order", "median")).reset_index()
    rngp = np.random.default_rng(S.SEED)
    boot_med = []
    vals = per_pair.interaction_total.values
    for _ in range(4000):
        boot_med.append(float(np.median(rngp.choice(vals, len(vals),
                                                    replace=True))))
    ci = (float(np.percentile(boot_med, 2.5)),
          float(np.percentile(boot_med, 97.5)))

    IDX.to_csv(RESULTS / "s22_indices.csv", index=False)
    COMP.to_csv(RESULTS / "s22_components.csv", index=False)
    SUMM.to_csv(RESULTS / "s22_summary.csv", index=False)
    INV.to_csv(RESULTS / "s22_invariance.csv", index=False)
    per_pair.to_csv(RESULTS / "s22_per_pair.csv", index=False)
    if len(ENV):
        ENV.to_csv(RESULTS / "s22_envelope.csv", index=False)
    if len(BOOT):
        BOOT.to_csv(RESULTS / "s22_boot_indices.csv", index=False)
        BSUM.to_csv(RESULTS / "s22_boot_summary.csv", index=False)

    #  the measure table, written so the manuscript can print it
    mrows = []
    for meas in ("equal-level", "reference", "concentrated"):
        sub = SUMM[(SUMM.scale == "raw-within-metric")
                   & (SUMM.measure == meas)]
        pp = sub.groupby(["log", "target"]).interaction_total.median()
        mrows.append(dict(measure=meas,
                          description={
                              "equal-level": "every level of every axis "
                                             "equally likely",
                              "reference": "half the mass on the reference "
                                           "level of each axis",
                              "concentrated": "eighty per cent on the "
                                              "reference level"}[meas],
                          interaction_total_median=float(pp.median()),
                          interaction_total_min=float(pp.min()),
                          interaction_total_max=float(pp.max())))
    if len(ENV):
        pe = ENV.groupby("rep").interaction_total.median()
        mrows.append(dict(measure="envelope",
                          description="200 Dirichlet draws of the level "
                                      "weights, primary pair",
                          interaction_total_median=float(pe.median()),
                          interaction_total_min=float(pe.min()),
                          interaction_total_max=float(pe.max())))
    #  Does the qualitative conclusion -- that no first-order index reaches
    #  the higher-order remainder -- survive the measure?  It does NOT under
    #  every measure, and the file says so rather than the manuscript
    #  assuming it.  The mechanism is not subtle: a reader who almost never
    #  departs from the reference specification barely activates an
    #  interaction, so concentrating the measure moves variance out of the
    #  higher-order terms and into the main effects.
    for r in mrows:
        meas = r["measure"]
        if meas == "envelope":
            continue
        a = IDX[(IDX.scale == "raw-within-metric") & (IDX.measure == meas)]
        b = SUMM[(SUMM.scale == "raw-within-metric") & (SUMM.measure == meas)]
        if not len(a) or not len(b):
            continue
        top = (a.groupby(["log", "target", "metric"]).S.max()
               .groupby(level=[0, 1]).median())
        inter = b.groupby(["log", "target"]).interaction_total.median()
        r["largest_first_order_median"] = float(top.median())
        r["n_pairs_first_order_exceeds"] = int((top > inter).sum())
        r["n_pairs"] = int(len(inter))
    M = pd.DataFrame(mrows)
    M.to_csv(RESULTS / "s22_measures.csv", index=False)
    print("\nMEASURES")
    print(M.to_string(index=False, float_format=lambda x: "%.3f" % x))

    facts = dict(
        n_decompositions=len(SUMM),
        n_components=len(COMP),
        components_sum_to_one=int(len(SUMM) - len(bad)),
        interaction_total_median=float(per_pair.interaction_total.median()),
        interaction_total_lo=ci[0], interaction_total_hi=ci[1],
        interaction_total_min=float(per_pair.interaction_total.min()),
        interaction_total_max=float(per_pair.interaction_total.max()),
        largest_involvement_median=float(per_pair.largest_involvement.median()),
        largest_first_order_median=float(
            per_pair.largest_first_order.median()),
        n_invariance_tests=len(INV),
        n_invariance_passed=int(INV.passed.sum()) if len(INV) else 0,
        measure_spread=float(M.interaction_total_median.max()
                             - M.interaction_total_median.min()),
        n_measures_interaction_leads=int(
            (M.get("n_pairs_first_order_exceeds", pd.Series(dtype=float))
             .fillna(0) < M.get("n_pairs", pd.Series(dtype=float)).fillna(1)
             / 2.0).sum()),
        concentrated_first_order=float(
            M.loc[M.measure == "concentrated",
                  "largest_first_order_median"].iloc[0])
        if "largest_first_order_median" in M.columns
        and (M.measure == "concentrated").any() else np.nan,
        concentrated_exceeds=int(
            M.loc[M.measure == "concentrated",
                  "n_pairs_first_order_exceeds"].iloc[0])
        if "n_pairs_first_order_exceeds" in M.columns
        and (M.measure == "concentrated").any() else 0,
        equal_exceeds=int(
            M.loc[M.measure == "equal-level",
                  "n_pairs_first_order_exceeds"].iloc[0])
        if "n_pairs_first_order_exceeds" in M.columns
        and (M.measure == "equal-level").any() else 0,
        n_boot_decompositions=int(len(BSUM)) if len(BSUM) else 0,
        runtime_s=round(time.time() - t0, 1))
    #  the axis-level medians under the primary measure
    pr = IDX[(IDX.scale == "raw-within-metric")
             & (IDX.measure == "equal-level")]
    if len(pr):
        #  the single largest first-order index anywhere on the corpus, and
        #  where it is: the manuscript says which axis leads varies by pair,
        #  and this is the extreme case that makes the point.
        top = pr.loc[pr.S.idxmax()]
        facts["top_index"] = float(top.S)
        facts["top_axis"] = str(top.axis)
        facts["top_pair"] = "%s / %s" % (top.log, top.target)
        facts["top_metric"] = str(top.metric)
        #  and the median, per pair, of which axis leads
        lead = (pr.loc[pr.groupby(["log", "target", "metric"]).S.idxmax()]
                .axis.value_counts())
        facts["n_axes_leading"] = int(len(lead))
        facts["modal_leading_axis"] = str(lead.index[0])
        facts["modal_leading_share"] = float(lead.iloc[0] / lead.sum())
    for ax in AXES:
        v = pr[pr.axis == ax].groupby(["log", "target"]).S.median()
        facts["S_%s_median" % ax] = float(v.median())
    hs = IDX[IDX.scale == "headroom-metric-as-axis"]
    if len(hs):
        for ax in list(AXES) + ["metric"]:
            v = hs[hs.axis == ax].S
            if len(v):
                facts["Sh_%s_median" % ax] = float(v.median())
    pd.DataFrame([facts]).to_csv(RESULTS / "s22_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

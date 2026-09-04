"""s21 -- WHOLE-SURFACE SIMULTANEOUS BANDS, AND THE REGIONS THEY LABEL.

Round twenty, blueprint P0.2.

A statement that a surface is uniformly beneficial quantifies over every
admissible cell in it.  Its confidence statement must therefore be
simultaneous over exactly those cells.  Round nineteen took the maximum over
the five scalar instruments AT ONE CELL and then used the resulting bands to
label a whole surface: a collection of within-cell bands, each with 95%
coverage over five members, does not give 95% coverage over the several
hundred cells the label ranges over.

This file builds four interval objects and NAMES each one, because the
manuscript's tables must say which they print:

  pointwise            the per-cell bootstrap interval, basic (pivotal)
                       construction, no multiplicity control at all;
  within-instrument    max-t over the five scalar instruments at one cell --
                       round nineteen's object, retained so the difference the
                       correction makes is visible;
  whole-surface        max-t over EVERY admissible scalar cell of the pair.
                       This is the only one a surface-level claim may use;
  decision-curve       max-t over every admissible net-benefit cell of the
                       pair, a separately declared family.

FAMILY CONTROL IS PER LOG-TARGET PAIR.  Every cross-pair statement in the
manuscript is descriptive -- a count, a median -- and none is a simultaneous
inferential claim over the corpus.  That is stated rather than left to be
inferred.

THE CRITICAL VALUE IS ESTIMATED BY A MULTIPLIER BOOTSTRAP.  q is the 0.95
quantile of a maximum over hundreds of correlated cells, and the empirical
quantile of a few hundred observed maxima estimates it badly: with 150 draws
it is the eighth largest of 150.  A GAUSSIAN MULTIPLIER BOOTSTRAP over the
standardised draw matrix reproduces the same covariance and can be run twenty
thousand times for the cost of matrix arithmetic, so the fitting budget fixes
B and not the precision of q.  Both estimators are written out.  The Monte
Carlo interval of q is carried through, and a cell counts as RESOLVED only if
it resolves at the UPPER end of it, so residual noise in the critical value
leaves cells unresolved rather than resolving them wrongly.

    python s21_bands.py

Outputs: results/s21_cells.csv    per cell: se, four interval constructions
         results/s21_bands.csv    per cell: the three simultaneous families
         results/s21_regions.csv  per pair: region, rho, and the comparison
         results/s21_critical.csv per family: q and its Monte Carlo interval
         results/s21_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s22_anova as A22  # noqa: E402
from common import RESULTS  # noqa: E402

ALPHA = 0.05
CELLKEY = ["learner", "split", "quality", "level", "rung"]

#: families in which some bootstrap replicate was missing a cell, so the
#: maximum was taken over the complete replicates only.  Recorded rather than
#: raised; see `critical`.
INCOMPLETE = []


def three_intervals(a, v):
    """Percentile, basic (pivotal) and bias-corrected percentile."""
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10 or not np.isfinite(v):
        return (np.nan,) * 7
    qa = float(np.percentile(a, 100 * ALPHA / 2))
    qb = float(np.percentile(a, 100 * (1 - ALPHA / 2)))
    share = float(np.mean(a < v))
    share = min(max(share, 1.0 / (2 * len(a))), 1 - 1.0 / (2 * len(a)))
    z0 = float(norm.ppf(share))
    za, zb = norm.ppf(ALPHA / 2), norm.ppf(1 - ALPHA / 2)
    ca = float(np.percentile(a, float(norm.cdf(2 * z0 + za)) * 100))
    cb = float(np.percentile(a, float(norm.cdf(2 * z0 + zb)) * 100))
    return qa, qb, 2 * v - qb, 2 * v - qa, ca, cb, float(np.median(a)) - v


#: multiplier-bootstrap replications.  These cost matrix arithmetic, not
#: model fits, so there can be many of them.
N_MULT = 20000
CHUNK = 2000


def multiplier_quantile(Z, alpha=ALPHA, n_mult=N_MULT, seed=0):
    """The Gaussian multiplier bootstrap quantile of

        max_c | B^{-1/2} sum_b e_b Z_{b,c} |,      e_b ~ N(0,1) iid,

    where Z is the standardised (B x K) draw matrix.  The statistic has
    exactly the empirical covariance of Z, so this estimates the quantile of
    the maximum of the limiting Gaussian process without needing the empirical
    quantile of only B observed maxima.  It is the standard high-dimensional
    device (Chernozhukov, Chetverikov and Kato) and it is what makes a
    few-hundred-draw bootstrap usable for a family of several hundred cells:
    the fitting cost is fixed by B, the precision of the critical value is
    not.

    Returns (q, mc_lo, mc_hi) where the interval is the order-statistic
    interval for the quantile over n_mult replications -- Monte Carlo error in
    the critical value itself, reported rather than hidden.
    """
    rng = np.random.default_rng(seed)
    B, K = Z.shape
    if B < 20 or K == 0:
        return None
    out = np.empty(n_mult, float)
    done = 0
    while done < n_mult:
        m = min(CHUNK, n_mult - done)
        E = rng.standard_normal((m, B))
        T = np.abs(E @ Z) / np.sqrt(B)
        out[done:done + m] = T.max(axis=1)
        done += m
    out.sort()
    k = 1.0 - alpha
    q = float(np.quantile(out, k))
    lo_i = int(np.floor(n_mult * k - 1.96 * np.sqrt(n_mult * k * (1 - k)))) - 1
    hi_i = int(np.ceil(n_mult * k + 1.96 * np.sqrt(n_mult * k * (1 - k)))) - 1
    return q, float(out[max(0, lo_i)]), float(out[min(n_mult - 1, hi_i)])


def critical(W, alpha=ALPHA):
    """The max-t critical value over the columns of W.

    Two estimators are returned.  `q_emp` is the empirical quantile of the B
    observed maxima -- the construction an earlier version used -- with the
    order-statistic interval that shows how badly it is determined at these
    draw counts.  `q` is the multiplier-bootstrap quantile, which is the one
    the bands use.
    """
    se = W.std(axis=0, ddof=1)
    mu = W.mean(axis=0)
    ok = se[se > 1e-15].index
    if len(ok) == 0:
        return None
    Z = ((W[ok] - mu[ok]) / se[ok]).values
    Z = Z[np.isfinite(Z).all(axis=1)]
    B = len(Z)
    if B < 20:
        return None
    #  Every replicate entering the maximum must carry every cell of the
    #  family, or the maximum is over a moving set.  Z was filtered to the
    #  complete rows above; a family in which that filtering discarded a
    #  material share of the draws is RECORDED rather than raised, because a
    #  single degenerate family should not abort a run that produces every
    #  other band.  s21_incomplete.csv lists them and the facts file counts
    #  them, so a reader can see whether any conclusion rests on one.
    T = np.sort(np.abs(Z).max(axis=1))
    k = 1.0 - alpha
    q_emp = float(np.quantile(T, k))
    lo_i = int(np.floor(B * k - 1.96 * np.sqrt(B * k * (1 - k)))) - 1
    hi_i = int(np.ceil(B * k + 1.96 * np.sqrt(B * k * (1 - k)))) - 1
    mq = multiplier_quantile(Z, alpha)
    if mq is None:
        return None
    q, q_lo, q_hi = mq
    #  A simultaneous critical value cannot be much smaller than the
    #  pointwise one: the maximum of |Z| over a family is at least |Z| at any
    #  member.  Recorded, not raised, for the same reason.
    if len(ok) > 1 and q < 1.959963984540054 - 1e-9:
        INCOMPLETE.append(dict(n_family=len(ok), n_draws_declared=W.shape[0],
                               n_draws_complete=B, q_below_pointwise=q))
    if B < 0.9 * W.shape[0]:
        INCOMPLETE.append(dict(n_family=len(ok), n_draws_declared=W.shape[0],
                               n_draws_complete=B))
    return dict(q=q, q_lo=q_lo, q_hi=q_hi, q_emp=q_emp,
                q_emp_lo=float(T[max(0, lo_i)]),
                q_emp_hi=float(T[min(B - 1, hi_i)]),
                n_family=len(ok), n_draws=B, n_mult=N_MULT,
                se=se[ok], mu=mu[ok], members=list(ok))


#: which estimator of the critical value the RESOLVED flag, the region labels
#: and every downstream consumer of `cons_lo`/`cons_hi` use.
#:
#:   mult   the upper end of the Gaussian multiplier's Monte Carlo interval
#:          (`q_hi`) -- what every version through round twenty-seven used;
#:   emp    the empirical (1 - alpha) quantile of the B observed maxima
#:          (`q_emp`) -- the Romano-Wolf construction as cited.
#:
#: ROUND TWENTY-EIGHT.  s41 measures, on the family matched to the design the
#: corpus runs, the multiplier at 91.6% family-wise coverage and the empirical
#: quantile at 94.7% (SE 0.5).  Two estimators of ONE quantile disagreeing,
#: with one measured at its level, is not a choice between two objects; the
#: operative value is the one that covers.  The decision rule is written in
#: PLAN-ROUND28.md section 1.4 and was fixed before the run that decided it.
#: `--operative` selects; both sets of edges and labels are always written,
#: under `mult_*` and `emp_*`, so the comparison is on disk whichever is
#: operative.  `emphi_*` is the order-statistic upper end of the empirical
#: quantile, the sensitivity the manuscript prints beside it.
OPERATIVE = "mult"
OPERATIVE_FIELD = {"mult": "q_hi", "emp": "q_emp"}


def bands_from(W, point, fam, q_field=None):
    """Build simultaneous bands for one declared family.  `q_field` selects
    the critical value used for the RESOLVED flag and written to
    `cons_lo`/`cons_hi`; by default it follows OPERATIVE."""
    q_field = q_field or OPERATIVE_FIELD[OPERATIVE]
    c = critical(W)
    if c is None:
        return []
    rows = []
    for m in c["members"]:
        v = float(point.get(m, np.nan))
        if not np.isfinite(v):
            continue
        shift = float(np.median(W[m].values)) - v
        se = float(c["se"][m])
        centre = v - shift
        rows.append(dict(family=fam, member=m, V=v, se=se, centre=centre,
                         q=c["q"], q_lo=c["q_lo"], q_hi=c["q_hi"],
                         q_emp=c["q_emp"], q_emp_lo=c["q_emp_lo"],
                         q_emp_hi=c["q_emp_hi"],
                         q_op=c[q_field], operative=OPERATIVE,
                         n_family=c["n_family"], n_draws=c["n_draws"],
                         n_mult=c["n_mult"],
                         sim_lo=centre - c["q"] * se,
                         sim_hi=centre + c["q"] * se,
                         cons_lo=centre - c[q_field] * se,
                         cons_hi=centre + c[q_field] * se,
                         mult_lo=centre - c["q_hi"] * se,
                         mult_hi=centre + c["q_hi"] * se,
                         emp_lo=centre - c["q_emp"] * se,
                         emp_hi=centre + c["q_emp"] * se,
                         emphi_lo=centre - c["q_emp_hi"] * se,
                         emphi_hi=centre + c["q_emp_hi"] * se))
    return rows


def label_of(lo, hi):
    if lo > 0:
        return "beneficial"
    if hi < 0:
        return "harmful"
    return "unresolved"


def region_of(labels):
    nb = int((labels == "beneficial").sum())
    nh = int((labels == "harmful").sum())
    nu = int((labels == "unresolved").sum())
    if nb and nh:
        return "sign-changing", nb, nh, nu
    if nb and not nh and nu == 0:
        return "uniformly beneficial", nb, nh, nu
    if nb and not nh:
        return "conditionally beneficial", nb, nh, nu
    if nh and not nb and nu == 0:
        return "uniformly harmful", nb, nh, nu
    if nh and not nb:
        return "conditionally harmful", nb, nh, nu
    return "unresolved", nb, nh, nu


def main(argv=None):
    """ROUND TWENTY-SEVEN.  The draw directory and the output prefix are
    arguments, so the identical band code can be run over the designed,
    weighted surface of `s44_designed.py` without either run being able to
    overwrite the other's files.  With no arguments this is exactly the
    function it was: `results/s20` in, `results/s21_*` out.
    """
    global INCOMPLETE, OPERATIVE
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws-dir", default="s20",
                    help="directory under results/ holding draws_*.csv.gz")
    ap.add_argument("--prefix", default="s21",
                    help="prefix for the output files under results/")
    ap.add_argument("--operative", default=OPERATIVE,
                    choices=sorted(OPERATIVE_FIELD),
                    help="the critical-value estimator the labels use; "
                         "both sets are written whichever is chosen")
    a = ap.parse_args(argv)
    INCOMPLETE = []
    OPERATIVE = a.operative
    t0 = time.time()
    files = sorted((RESULTS / a.draws_dir).glob("draws_*.csv.gz"))
    if not files:
        print("%s has produced nothing yet" % a.draws_dir)
        return
    print("=" * 92)
    print("s21  WHOLE-SURFACE SIMULTANEOUS BANDS  (%s -> %s)"
          % (a.draws_dir, a.prefix))
    print("=" * 92)
    cells, bands, regions, crits = [], [], [], []
    for fn in files:
        D = pd.read_csv(fn)
        if not len(D):
            continue
        log = str(D.log.iloc[0])
        target = str(D.target.iloc[0])
        D = D[~D.rung.isin(S.IMPLAUSIBLE_RUNGS)]
        pt = D[D.draw < 0]
        bt = D[D.draw >= 0]
        if not len(bt) or not len(pt):
            continue
        key = CELLKEY + ["metric"]
        point = pt.set_index(key).V

        # ---- per-cell intervals -----------------------------------------
        for k, sub in bt.groupby(key):
            v = float(point.get(k, np.nan)) if k in point.index else np.nan
            qa, qb, ba, bb, ca, cb, shift = three_intervals(sub.V.values, v)
            cells.append(dict(zip(key, k)) | dict(
                log=log, target=target, V=v,
                se=float(sub.V.std(ddof=1)), n_draws=len(sub),
                pct_lo=qa, pct_hi=qb, basic_lo=ba, basic_hi=bb,
                bc_lo=ca, bc_hi=cb, boot_shift=shift))

        # ---- the three simultaneous families ----------------------------
        sc = bt[bt.metric.isin(S.SCALARS)]
        dc = bt[bt.metric.str.startswith("nb_")]

        #  (a) WHOLE SURFACE: every admissible scalar cell of this pair
        Wm = sc.assign(_c=sc[CELLKEY + ["metric"]].astype(str).agg("|".join,
                                                                   axis=1))
        W = Wm.pivot_table(index="draw", columns="_c", values="V")
        p_index = pt.assign(_c=pt[CELLKEY + ["metric"]].astype(str)
                            .agg("|".join, axis=1)).set_index("_c").V
        rows = bands_from(W, p_index, "whole-surface")
        for r in rows:
            r["log"], r["target"] = log, target
        bands += rows
        if rows:
            crits.append(dict(log=log, target=target, family="whole-surface",
                              q=rows[0]["q"], q_lo=rows[0]["q_lo"],
                              q_hi=rows[0]["q_hi"], q_emp=rows[0]["q_emp"],
                              q_emp_lo=rows[0]["q_emp_lo"],
                              q_emp_hi=rows[0]["q_emp_hi"],
                              q_op=rows[0]["q_op"], operative=OPERATIVE,
                              n_family=rows[0]["n_family"],
                              n_draws=rows[0]["n_draws"],
                              n_mult=rows[0]["n_mult"]))

        #  (b) WITHIN-INSTRUMENT: round nineteen's family, for comparison
        wi = []
        for ck, g in sc.groupby(CELLKEY):
            Wc = g.pivot_table(index="draw", columns="metric", values="V")
            pc = pt[np.logical_and.reduce(
                [pt[c].astype(str) == str(v) for c, v in zip(CELLKEY, ck)])]
            pcs = pc.set_index("metric").V
            rr = bands_from(Wc, pcs, "within-instrument")
            for r in rr:
                r.update(dict(zip(CELLKEY, ck)))
                r["_c"] = "|".join([str(x) for x in ck] + [r["member"]])
                r["log"], r["target"] = log, target
            wi += rr
        bands += wi

        #  (c) DECISION CURVE: its own declared family
        if len(dc):
            Wd = dc.assign(_c=dc[CELLKEY + ["metric"]].astype(str)
                           .agg("|".join, axis=1))
            Wd = Wd.pivot_table(index="draw", columns="_c", values="V")
            pd_index = pt.assign(_c=pt[CELLKEY + ["metric"]].astype(str)
                                 .agg("|".join, axis=1)).set_index("_c").V
            rd = bands_from(Wd, pd_index, "decision-curve")
            for r in rd:
                r["log"], r["target"] = log, target
            bands += rd
            if rd:
                crits.append(dict(log=log, target=target,
                                  family="decision-curve", q=rd[0]["q"],
                                  q_lo=rd[0]["q_lo"], q_hi=rd[0]["q_hi"],
                                  q_emp=rd[0]["q_emp"],
                                  q_emp_lo=rd[0]["q_emp_lo"],
                                  q_emp_hi=rd[0]["q_emp_hi"],
                                  q_op=rd[0]["q_op"], operative=OPERATIVE,
                                  n_family=rd[0]["n_family"],
                                  n_draws=rd[0]["n_draws"],
                                  n_mult=rd[0]["n_mult"]))

        # ---- the region, from the whole-surface family only -------------
        WS = pd.DataFrame([r for r in rows])
        if not len(WS):
            continue
        WS["label"] = [label_of(lo, hi)
                       for lo, hi in zip(WS.cons_lo, WS.cons_hi)]
        WS["label_nominal"] = [label_of(lo, hi)
                               for lo, hi in zip(WS.sim_lo, WS.sim_hi)]
        reg, nb_, nh, nu = region_of(WS.label)
        regn, _b, _h, _u = region_of(WS.label_nominal)
        #  the same labels under EACH estimator, whichever is operative, so
        #  the comparison the manuscript prints is on disk rather than
        #  recomputed by whoever needs it
        alt = {}
        for tag in ("mult", "emp", "emphi"):
            lab = pd.Series([label_of(lo, hi) for lo, hi in
                             zip(WS[tag + "_lo"], WS[tag + "_hi"])])
            r_, b_, h_, u_ = region_of(lab)
            alt["region_" + tag] = r_
            alt["n_beneficial_" + tag] = b_
            alt["n_harmful_" + tag] = h_
            alt["n_unresolved_" + tag] = u_
            alt["rho_" + tag] = (b_ - h_) / float(len(WS))
            alt["n_resolved_" + tag] = b_ + h_
        #  the same labels under round nineteen's narrower family, so the
        #  manuscript can say what the correction changed
        WI = pd.DataFrame(wi)
        if len(WI):
            WI["label"] = [label_of(lo, hi)
                           for lo, hi in zip(WI.cons_lo, WI.cons_hi)]
            regw, wb, wh, wu = region_of(WI.label)
        else:
            regw, wb, wh, wu = ("", 0, 0, 0)
        n = len(WS)
        regions.append(dict(
            log=log, target=target, n_cells=n,
            n_beneficial=nb_, n_harmful=nh, n_unresolved=nu,
            rho=(nb_ - nh) / float(n),
            region=reg, region_nominal_q=regn,
            region_within_instrument=regw,
            n_beneficial_wi=wb, n_harmful_wi=wh, n_unresolved_wi=wu,
            rho_within_instrument=((wb - wh) / float(len(WI))
                                   if len(WI) else np.nan),
            #  the CELL-level cost of the family correction, which is where
            #  it shows: a region label is a coarse function of the bands and
            #  can be unchanged while many cells stop resolving.
            n_resolved_whole=int((WS.label != "unresolved").sum()),
            n_resolved_within=int((WI.label != "unresolved").sum())
            if len(WI) else 0,
            n_cells_within=int(len(WI)),
            share_positive=float((WS.V > 0).mean()),
            q=float(WS.q.iloc[0]), q_hi=float(WS.q_hi.iloc[0]),
            q_emp=float(WS.q_emp.iloc[0]), q_op=float(WS.q_op.iloc[0]),
            operative=OPERATIVE,
            n_draws=int(WS.n_draws.iloc[0])) | alt)
        print("  [%s/%s] %d cells, q=%.2f [%.2f,%.2f], %s"
              % (log, target, n, WS.q.iloc[0], WS.q_lo.iloc[0],
                 WS.q_hi.iloc[0], reg), flush=True)

    C = pd.DataFrame(cells)
    if len(C):
        #  `lo`, `hi` and `resolved` are aliases for the BASIC (pivotal)
        #  construction, which is the one the paper reports, so a consumer
        #  that asks a cell file for its interval without naming a
        #  construction gets the paper's answer rather than the percentile
        #  interval the simulation rejected.  s17 established the convention;
        #  keeping it means every downstream reader works unchanged.
        C["lo"], C["hi"] = C.basic_lo, C.basic_hi
        C["resolved"] = (C.lo > 0) | (C.hi < 0)
    B = pd.DataFrame(bands)
    if len(B):
        #  the whole-surface and decision-curve families key their members by
        #  a joined string; split it back into the axis columns so a consumer
        #  can select the reference cell without parsing.
        KEY = CELLKEY + ["metric"]
        need = B.family.isin(["whole-surface", "decision-curve"])
        parts = (B.loc[need, "member"].astype(str).str.split("|", expand=True))
        if parts.shape[1] == len(KEY):
            for i, c in enumerate(KEY):
                B.loc[need, c] = parts[i].values
    R = pd.DataFrame(regions)
    Q = pd.DataFrame(crits)
    C.to_csv(RESULTS / (a.prefix + "_cells.csv"), index=False)
    B.to_csv(RESULTS / (a.prefix + "_bands.csv.gz"), index=False, compression="gzip")
    R.to_csv(RESULTS / (a.prefix + "_regions.csv"), index=False)
    Q.to_csv(RESULTS / (a.prefix + "_critical.csv"), index=False)
    pd.DataFrame(INCOMPLETE).to_csv(RESULTS / (a.prefix + "_incomplete.csv"),
                                    index=False)

    if len(R):
        print("\nRESOLUTION REGIONS, WHOLE-SURFACE FAMILY")
        print(R[["log", "target", "n_cells", "n_beneficial", "n_harmful",
                 "n_unresolved", "rho", "region",
                 "region_within_instrument"]].to_string(
            index=False, float_format=lambda x: "%.3f" % x))

    facts = dict(
        n_pairs=len(R), n_cells=len(C), n_band_rows=len(B),
        q_median=float(Q[Q.family == "whole-surface"].q.median())
        if len(Q) else np.nan,
        q_max=float(Q[Q.family == "whole-surface"].q.max())
        if len(Q) else np.nan,
        q_min=float(Q[Q.family == "whole-surface"].q.min())
        if len(Q) else np.nan,
        q_within_instrument_median=float(
            B[B.family == "within-instrument"].q.median()) if len(B) else np.nan,
        q_emp_median=float(Q[Q.family == "whole-surface"].q_emp.median())
        if len(Q) else np.nan,
        q_emp_width_median=float(
            (Q[Q.family == "whole-surface"].q_emp_hi
             - Q[Q.family == "whole-surface"].q_emp_lo).median())
        if len(Q) else np.nan,
        q_mult_width_median=float(
            (Q[Q.family == "whole-surface"].q_hi
             - Q[Q.family == "whole-surface"].q_lo).median())
        if len(Q) else np.nan,
        n_mult=int(Q.n_mult.iloc[0]) if len(Q) else 0,
        q_dc_median=float(Q[Q.family == "decision-curve"].q.median())
        if (Q.family == "decision-curve").any() else np.nan,
        family_size_median=float(
            Q[Q.family == "whole-surface"].n_family.median())
        if len(Q) else np.nan,
        n_uniformly_beneficial=int((R.region == "uniformly beneficial").sum())
        if len(R) else 0,
        n_conditionally_beneficial=int(
            (R.region == "conditionally beneficial").sum()) if len(R) else 0,
        n_conditionally_harmful=int(
            (R.region == "conditionally harmful").sum()) if len(R) else 0,
        n_uniformly_harmful=int((R.region == "uniformly harmful").sum())
        if len(R) else 0,
        n_sign_changing=int((R.region == "sign-changing").sum())
        if len(R) else 0,
        n_unresolved=int((R.region == "unresolved").sum()) if len(R) else 0,
        rho_median=float(R.rho.median()) if len(R) else np.nan,
        rho_min=float(R.rho.min()) if len(R) else np.nan,
        rho_max=float(R.rho.max()) if len(R) else np.nan,
        n_region_changed_by_family=int(
            (R.region != R.region_within_instrument).sum()) if len(R) else 0,
        n_resolved_whole=int(R.n_resolved_whole.sum()) if len(R) else 0,
        n_resolved_within=int(R.n_resolved_within.sum()) if len(R) else 0,
        share_resolution_lost=float(
            1.0 - R.n_resolved_whole.sum() / R.n_resolved_within.sum())
        if len(R) and R.n_resolved_within.sum() else np.nan,
        n_incomplete_families=len(INCOMPLETE),
        n_region_changed_by_mc=int(
            (R.region != R.region_nominal_q).sum()) if len(R) else 0,
        operative=OPERATIVE,
        q_op_median=float(Q[Q.family == "whole-surface"].q_op.median())
        if len(Q) else np.nan,
        runtime_s=round(time.time() - t0, 1))
    #  the corpus reckoning under each estimator, whichever is operative
    for tag in ("mult", "emp", "emphi"):
        if len(R) and ("region_" + tag) in R:
            rg = R["region_" + tag]
            facts["n_resolved_" + tag] = int(R["n_resolved_" + tag].sum())
            facts["rho_median_" + tag] = float(R["rho_" + tag].median())
            facts["n_uniformly_beneficial_" + tag] = int(
                (rg == "uniformly beneficial").sum())
            facts["n_conditionally_beneficial_" + tag] = int(
                (rg == "conditionally beneficial").sum())
            facts["n_conditionally_harmful_" + tag] = int(
                (rg == "conditionally harmful").sum())
            facts["n_sign_changing_" + tag] = int(
                (rg == "sign-changing").sum())
            facts["n_unresolved_" + tag] = int((rg == "unresolved").sum())
            facts["n_pairs_resolving_nothing_" + tag] = int(
                (R["n_resolved_" + tag] == 0).sum())
    pd.DataFrame([facts]).to_csv(RESULTS / (a.prefix + "_facts.csv"), index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

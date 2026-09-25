"""s60 -- FORECAST-EVALUATION CHECKS ON THE CORPUS'S HEADLINE OBJECTS.

Seven checks a reader from the forecast-evaluation literature will make of
Sections 6.2--6.4, each computed on files the analysis already wrote, except
the seventh group (T6), which refits ONE specification per pair -- the
reference cell -- with the repository's own pipeline code, because no per-case
prediction is stored anywhere else.

  T1  SAME-METRIC REFERENCE.  Section 6.4's resolved-cell disagreement rate
      compares every resolved cell with the reference cell read in AUC, the
      conventional report's metric.  Here each resolved cell is also compared
      with the reference cell OF ITS OWN METRIC (same pair, same pipeline,
      split, register and rung; only the metric is shared with the cell), and
      the cells that change status are attributed to pairs and metrics.
  T2  REGION LABELS WITHIN EACH METRIC.  Definition 3 applied to each
      metric's cells separately, under the pooled whole-surface band the
      article reports (primary), and -- as a sensitivity -- under a band whose
      max-t family is the metric's own cells, built by the band code itself
      (s21_bands.critical / bands_from) from the stored draws.  The same
      minimum resolved share applies, to the smaller family.
  T3  UNCERTAINTY FOR THE STRATUM SHARES.  A bootstrap over the pairs of the
      corpus medians of the four-way partition and of the split's main
      effect and interactions.  This interval is BETWEEN-PAIR: it says how
      much the median moves with which pairs are in the corpus, not how much
      a pair's own share moves with its sampling error.
  T4  THE SPLIT'S MAIN EFFECT AND ITS INTERACTIONS, separately, from
      s22_components (whose split-involving sum is s42's stratum exactly;
      checked below).
  T5  THE HEADLINES IN A PROPER SCORE.  Split-involving share, displacement
      of resolved cells from the same-metric reference and sign agreement
      with AUC, for Brier skill and log-loss skill beside AUC.
  T6  NESTED-MODEL ADJUSTMENT AT THE REFERENCE CELL.  The reference
      specification is refitted with and without the predictor; per-case
      test predictions give a Diebold--Mariano t on the Brier and log-loss
      differentials and a Clark--West adjusted t on the Brier differential,
      all with a Newey--West (Bartlett) long-run variance at lag
      floor(n_test^(1/3)).  The refitted AUC, Brier-skill and log-loss-skill
      increments are checked against the stored surface.
  T7  FOLD TREND.  The share of the fold-to-fold variation of the increment
      that a linear trend in the fold index explains, against the
      permutation null of exchangeable folds (expected share one quarter
      for five folds).

    python s60_ijf_checks.py

Outputs (results/):
    s60_samemetric.csv       T1, one row per pair x metric
    s60_metric_regions.csv   T2, one row per pair x metric
    s60_share_boot.csv       T3/T4, one row per quantity
    s60_split_components.csv T4, one row per pair (median over metrics)
    s60_by_metric.csv        T5, one row per metric
    s60_reference_tests.csv  T6, one row per pair
    s60_reference_predictions.csv.gz  T6, per-case test predictions
    s60_foldtrend.csv        T7, one row per pair x metric
    s60_facts.csv            every corpus-level number, one row
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import itertools  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import norm  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
import s21_bands as B21  # noqa: E402
import s23_regret as S23  # noqa: E402
import s42_round26 as S42  # noqa: E402
from common import RESULTS  # noqa: E402

KEY = ["learner", "split", "quality", "level", "rung"]
PAIR = ["log", "target"]
METRICS = list(S.SCALARS)
PROPER = ("brier_skill", "logloss_skill", "nagelkerke")
MIN_SHARE = S42.MIN_RESOLVED_DECLARED
ALPHA_ONE_SIDED = 0.05
Z_ONE_SIDED = float(norm.ppf(1 - ALPHA_ONE_SIDED))
N_BOOT = 10000
BOOT_SEED = S.SEED + 60
N_PERM = 10000
PERM_SEED = S.SEED + 61
FOLDS = ("rolling1", "rolling2", "rolling3", "rolling4", "rolling5")

#: the reference specification: the conventional report (one pipeline, the
#: register as recorded, the single temporal holdout, the full intake block)
REF_LEARNER, REF_SPLIT, REF_QUALITY, REF_RUNG = (
    "logit", "holdout70", "clean", "B_intake_g")


def region_label(nb, nh, n):
    """Definition 3, including the minimum resolved share, on a family of n
    cells of which nb are beneficial and nh harmful."""
    nu = n - nb - nh
    if nb and nh:
        r = "sign-changing"
    elif nb and nu == 0:
        r = "uniformly beneficial"
    elif nb:
        r = "conditionally beneficial"
    elif nh and nu == 0:
        r = "uniformly harmful"
    elif nh:
        r = "conditionally harmful"
    else:
        r = "unresolved"
    if r != "unresolved" and (nb + nh) / float(n) < MIN_SHARE:
        r = "unresolved (below minimum share)"
    return r


def disagrees(v, v_ref):
    """Section 6.4's rule, as s42_round26.mpid_rates writes it."""
    v = np.asarray(v, float)
    return (v > 0) if v_ref <= 0 else (v <= 0)


# ==========================================================================
# the inference surface, joined to the declared one
# ==========================================================================
def inference_cells(SC):
    B = S.read_results("s48w_bands.csv")
    W = B[B.family == "whole-surface"].copy()
    W["ben"] = W.cons_lo > 0
    W["harm"] = W.cons_hi < 0
    J = SC.merge(W[PAIR + KEY + ["metric", "V", "ben", "harm"]]
                 .rename(columns={"V": "V_band"}),
                 on=PAIR + KEY + ["metric"], how="inner")
    if len(J) != len(W):
        raise SystemExit("inference cells did not all join the surface: "
                         "%d of %d" % (len(J), len(W)))
    return J


def reference_values(SC):
    """{(log, target, metric): the reference cell's increment in that
    metric}, by the function Section 6.4's own rate uses."""
    out = {}
    for (log, target, metric), sub in SC.groupby(PAIR + ["metric"]):
        out[(log, target, metric)] = S23.reference_value(sub)
    return out


# ==========================================================================
# T1 -- the same-metric reference
# ==========================================================================
def t1_samemetric(J, REFV):
    rows = []
    for (log, target, metric), g in J.groupby(PAIR + ["metric"]):
        res = (g.ben | g.harm).values
        v = g.V.values
        v_auc = REFV[(log, target, "auc")]
        v_own = REFV[(log, target, metric)]
        d_auc = disagrees(v, v_auc) & res
        d_own = disagrees(v, v_own) & res
        rows.append(dict(
            log=log, target=target, metric=metric, n_cells=len(g),
            n_resolved=int(res.sum()), v_ref_auc=v_auc, v_ref_own=v_own,
            ref_signs_agree=bool((v_auc > 0) == (v_own > 0)),
            n_disagree_aucref=int(d_auc.sum()),
            n_disagree_ownref=int(d_own.sum()),
            n_leave=int((d_auc & ~d_own).sum()),
            n_enter=int((~d_auc & d_own).sum()),
            mad_resolved_own=(float(np.abs(v[res] - v_own).mean())
                              if res.any() else np.nan)))
    return pd.DataFrame(rows)


# ==========================================================================
# T2 -- region labels within each metric
# ==========================================================================
def t2_within_family(log, target):
    """Per metric: counts of beneficial and harmful cells under a max-t band
    whose family is that metric's own cells, from the stored draws, by the
    band code itself at the empirical critical value (the operative
    estimator).  Also returns the whole-surface q_emp recomputed from the
    same draws, as a check that the draws are the ones the article used."""
    fn = RESULTS / "s44_weighted" / ("draws_%s_%s.csv.gz" % (log, target))
    D = pd.read_csv(fn)
    D = D[~D.rung.isin(S.IMPLAUSIBLE_RUNGS) & D.metric.isin(METRICS)]
    D = D.assign(_c=D[KEY + ["metric"]].astype(str).agg("|".join, axis=1))
    pt, bt = D[D.draw < 0], D[D.draw >= 0]
    point = pt.set_index("_c").V
    W = bt.pivot_table(index="draw", columns="_c", values="V")
    whole = B21.critical(W)
    out = {}
    for m in METRICS:
        cols = [c for c in W.columns if c.endswith("|" + m)]
        rows = B21.bands_from(W[cols], point, "within-metric",
                              q_field="q_emp")
        nb = sum(1 for r in rows if r["cons_lo"] > 0)
        nh = sum(1 for r in rows if r["cons_hi"] < 0)
        out[m] = dict(nb=nb, nh=nh, n=len(rows),
                      q_emp=rows[0]["q_emp"] if rows else np.nan)
    return out, (whole["q_emp"] if whole else np.nan)


def t2_regions(J):
    REG = S.read_results("s42_regions.csv").set_index(PAIR)
    CRIT = S.read_results("s48w_critical.csv")
    CRIT = CRIT[CRIT.family == "whole-surface"].set_index(PAIR)
    rows, qcheck = [], []
    for (log, target), gp in J.groupby(PAIR):
        within, q_whole = t2_within_family(log, target)
        qcheck.append(abs(q_whole - float(CRIT.loc[(log, target), "q_emp"])))
        pooled = str(REG.loc[(log, target), "region_min05"])
        for metric, g in gp.groupby("metric"):
            nb, nh, n = int(g.ben.sum()), int(g.harm.sum()), len(g)
            w = within[metric]
            rows.append(dict(
                log=log, target=target, metric=metric, n_cells=n,
                n_beneficial=nb, n_harmful=nh,
                region=region_label(nb, nh, n),
                region_table4=pooled,
                n_beneficial_within=w["nb"], n_harmful_within=w["nh"],
                n_cells_within=w["n"], q_emp_within=w["q_emp"],
                region_within=region_label(w["nb"], w["nh"], w["n"])))
    R = pd.DataFrame(rows)
    R["differs"] = R.region != R.region_table4
    R["differs_within"] = R.region_within != R.region_table4
    return R, float(max(qcheck))


# ==========================================================================
# T3/T4 -- the pair bootstrap of the corpus medians
# ==========================================================================
def split_components():
    C = S.read_results("s22_components.csv")
    C = C[(C.measure == "equal-level") & (C.scale == "raw-within-metric")
          & C.metric.isin(METRICS)].copy()
    parts = C.component.str.split("+")
    C["has_split"] = parts.apply(lambda l: "split" in l)
    rows = []
    for (log, target, metric), g in C.groupby(PAIR + ["metric"]):
        s = g[g.has_split]
        comp = dict(zip(g.component, g.share))
        rows.append(dict(
            log=log, target=target, metric=metric,
            split_involving=float(s.share.sum()),
            split_main=float(comp.get("split", 0.0)),
            split_interactions=float(s[s.order >= 2].share.sum()),
            split_two_way=float(s[s.order == 2].share.sum()),
            split_three_way=float(s[s.order == 3].share.sum()),
            split_four_way=float(s[s.order == 4].share.sum()),
            split_x_rung=float(comp.get("split+rung", 0.0)),
            split_x_learner=float(comp.get("learner+split", 0.0)),
            split_x_quality=float(comp.get("split+quality_level", 0.0))))
    return pd.DataFrame(rows)


def pair_bootstrap(values, rng, n_boot=N_BOOT):
    """Percentile interval of the median over pairs, resampling pairs."""
    v = np.asarray(values, float)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    med = np.median(v[idx], axis=1)
    return (float(np.median(v)),
            float(np.quantile(med, 0.025, method="inverted_cdf")),
            float(np.quantile(med, 0.975, method="inverted_cdf")))


# ==========================================================================
# T6 -- the reference cell, refitted
# ==========================================================================
def nw_lrv(x, lag):
    """Newey--West long-run variance of x with Bartlett weights."""
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    v = float(x @ x) / n
    for l in range(1, lag + 1):
        v += 2.0 * (1.0 - l / (lag + 1.0)) * float(x[l:] @ x[:-l]) / n
    return v


def hac_t(x, lag):
    n = len(x)
    lrv = nw_lrv(x, lag)
    return float(np.mean(x) / np.sqrt(max(lrv, 1e-300) / n))


def t6_refit(log, target):
    """The reference specification refitted exactly as s01_surface.run_task
    fits it: the same preparation, the same split, the register degraded by
    the `clean' mechanism (which is the identity on its string form), the
    same learner, seed and columns."""
    d, ladder, f, meta = S01.prepare(log, target)
    if d is None:
        return None, None
    n = len(d)
    (_, tri, tei), = list(S.splits(n, REF_SPLIT))
    rng = np.random.default_rng(S.SEED + 1000 * 0)
    dd = d.copy()
    dd["_f"] = S.degrade(d[f], REF_QUALITY, 1.0, rng, tri)
    tr, te = dd.iloc[tri], dd.iloc[tei]
    cols = list(dict(ladder)[REF_RUNG])
    ytr, yte = tr["_y"].values, te["_y"].values.astype(int)
    prev_tr = float(ytr.mean())
    p0 = S.LEARNERS[REF_LEARNER](tr, te, cols, ytr, S.SEED)
    p1 = S.LEARNERS[REF_LEARNER](tr, te, cols + ["_f"], ytr, S.SEED)
    m0 = S.all_metrics(p0, yte, prev_tr)
    m1 = S.all_metrics(p1, yte, prev_tr)
    nte = len(yte)
    lag = int(np.floor(nte ** (1.0 / 3.0)))
    lag_alt = max(10, int(round(nte ** (1.0 / 3.0))))
    q0 = np.clip(p0, 1e-12, 1 - 1e-12)
    q1 = np.clip(p1, 1e-12, 1 - 1e-12)
    #  loss differentials, oriented so that POSITIVE means the predictor
    #  improves the forecast
    dB = (yte - p0) ** 2 - (yte - p1) ** 2
    cw = dB + (p0 - p1) ** 2
    ll0 = -(yte * np.log(q0) + (1 - yte) * np.log(1 - q0))
    ll1 = -(yte * np.log(q1) + (1 - yte) * np.log(1 - q1))
    dL = ll0 - ll1
    row = dict(
        log=log, target=target, n_train=len(tri), n_test=nte, lag=lag,
        lag_alt=lag_alt,
        auc_increment=m1["auc"] - m0["auc"],
        brier_skill_increment=m1["brier_skill"] - m0["brier_skill"],
        logloss_skill_increment=m1["logloss_skill"] - m0["logloss_skill"],
        brier_diff=float(dB.mean()), cw_adjusted=float(cw.mean()),
        logloss_diff=float(dL.mean()),
        dm_brier_t=hac_t(dB, lag), cw_t=hac_t(cw, lag),
        dm_logloss_t=hac_t(dL, lag),
        dm_brier_t_alt=hac_t(dB, lag_alt), cw_t_alt=hac_t(cw, lag_alt),
        dm_logloss_t_alt=hac_t(dL, lag_alt))
    for k in ("dm_brier", "cw", "dm_logloss"):
        row[k + "_reject"] = bool(row[k + "_t"] > Z_ONE_SIDED)
        row[k + "_reject_alt"] = bool(row[k + "_t_alt"] > Z_ONE_SIDED)
    row["cw_reverses"] = bool(row["dm_brier_t"] < 0 and row["cw_reject"])
    pred = pd.DataFrame(dict(log=log, target=target, t=np.arange(nte),
                             y=yte, p0=p0, p1=p1))
    return row, pred


# ==========================================================================
# T7 -- the fold trend
# ==========================================================================
LIN = (np.arange(5) - 2.0) / np.sqrt(10.0)   # orthonormal linear contrast


def trend_share(A):
    """A: (cells x 5) fold profiles.  The share of the within-cell
    fold-to-fold sum of squares on the linear contrast in fold index."""
    A = np.asarray(A, float)
    A = A - A.mean(axis=1, keepdims=True)
    tot = float((A ** 2).sum())
    return float(((A @ LIN) ** 2).sum()) / tot if tot > 0 else np.nan


def t7_profiles(SC):
    """{pair: {metric: (reference profile 1x5, all-cells profiles Cx5)}}"""
    F = SC[SC["split"].isin(FOLDS)].copy()
    out = {}
    for (log, target, metric), g in F.groupby(PAIR + ["metric"]):
        P = g.pivot_table(index=["learner", "quality_level", "rung"],
                          columns="split", values="V")
        if list(P.columns) != list(FOLDS):
            continue
        P = P.dropna()
        ref = (REF_LEARNER, "clean@1.00", REF_RUNG)
        if ref not in P.index:
            continue
        out.setdefault((log, target), {})[metric] = (
            P.loc[[ref]].values, P.values)
    return out


def t7_statistic(prof, perms=None):
    """Median over pairs of the median over metrics of the trend share, for
    the reference configuration and for all cells.  `perms` maps a pair to a
    permutation of the five folds (the null)."""
    ref_med, all_med = [], []
    for pair, bym in prof.items():
        o = perms[pair] if perms is not None else slice(None)
        ref_med.append(np.median([trend_share(r[:, o]) for r, _ in
                                  bym.values()]))
        all_med.append(np.median([trend_share(a[:, o]) for _, a in
                                  bym.values()]))
    return float(np.median(ref_med)), float(np.median(all_med))


def t7_foldtrend(SC):
    prof = t7_profiles(SC)
    rows = []
    for (log, target), bym in prof.items():
        for metric, (r, a) in bym.items():
            slope = float((r[0] - r[0].mean()) @ LIN)
            rows.append(dict(log=log, target=target, metric=metric,
                             trend_share_reference=trend_share(r),
                             trend_share_all_cells=trend_share(a),
                             reference_slope_positive=bool(slope > 0),
                             n_cells=int(a.shape[0])))
    obs_ref, obs_all = t7_statistic(prof)
    #  THE NULL: fold labels exchangeable within a pair.  One permutation per
    #  pair per replicate, shared by every metric and every cell of that pair,
    #  so the dependence across metrics and cells is kept and only the order
    #  of the folds is destroyed.
    rng = np.random.default_rng(PERM_SEED)
    allp = list(itertools.permutations(range(5)))
    pairs = list(prof)
    null_ref, null_all = np.empty(N_PERM), np.empty(N_PERM)
    #  precompute every pair's statistic under each of the 120 orders
    cache = {}
    for pair in pairs:
        bym = prof[pair]
        cache[pair] = np.array([
            (np.median([trend_share(r[:, list(o)]) for r, _ in bym.values()]),
             np.median([trend_share(a[:, list(o)]) for _, a in bym.values()]))
            for o in allp])
    pick = rng.integers(0, len(allp), size=(N_PERM, len(pairs)))
    for b in range(N_PERM):
        vals = np.array([cache[p][pick[b, i]] for i, p in enumerate(pairs)])
        null_ref[b] = np.median(vals[:, 0])
        null_all[b] = np.median(vals[:, 1])
    facts = dict(
        foldtrend_ref_median=obs_ref, foldtrend_all_median=obs_all,
        foldtrend_null_ref_mean=float(null_ref.mean()),
        foldtrend_null_all_mean=float(null_all.mean()),
        foldtrend_ref_p=float((1 + (null_ref >= obs_ref).sum())
                              / (N_PERM + 1.0)),
        foldtrend_all_p=float((1 + (null_all >= obs_all).sum())
                              / (N_PERM + 1.0)),
        foldtrend_n_pairs=len(pairs), foldtrend_n_perm=N_PERM,
        foldtrend_expected=0.25)
    return pd.DataFrame(rows), facts


# ==========================================================================
def main():
    t0 = time.time()
    print("=" * 92)
    print("s60  FORECAST-EVALUATION CHECKS")
    print("=" * 92)
    SC = S42.surface()
    REFV = reference_values(SC)
    J = inference_cells(SC)
    facts = dict(n_pairs=int(SC.groupby(PAIR).ngroups),
                 n_inference_cells=len(J),
                 max_abs_V_band_minus_surface=float(
                     (J.V - J.V_band).abs().max()))

    # ---- T1 ---------------------------------------------------------------
    T1 = t1_samemetric(J, REFV)
    T1.to_csv(RESULTS / "s60_samemetric.csv", index=False)
    n_res = int(T1.n_resolved.sum())
    n_auc, n_own = int(T1.n_disagree_aucref.sum()), int(T1.n_disagree_ownref.sum())
    bp = T1[(T1.log == "BPIC19") & T1.metric.isin(PROPER)]
    facts.update(
        n_resolved=n_res, n_disagree_aucref=n_auc, n_disagree_ownref=n_own,
        rate_aucref=n_auc / n_res, rate_ownref=n_own / n_res,
        n_leave=int(T1.n_leave.sum()), n_enter=int(T1.n_enter.sum()),
        n_leave_bpic19_proper=int(bp.n_leave.sum()),
        n_pairs_ref_sign_differs_bss=int(
            (~T1[T1.metric == "brier_skill"].ref_signs_agree).sum()),
        n_pairs_ref_sign_differs_bss_with_resolved=int(
            ((~T1[T1.metric == "brier_skill"].ref_signs_agree)
             & (T1[T1.metric == "brier_skill"].n_resolved > 0)).sum()),
        n_pairs_leave=int((T1.groupby(PAIR).n_leave.sum() > 0).sum()))
    #  SENSITIVITY: Section 6.4 reads each cell's sign off the declared
    #  surface and its resolution off the inference surface, whose point
    #  estimate differs on some cells.  The same two counts with the sign read
    #  off the inference surface instead, and its own reference cells.
    Jb = J.assign(V=J.V_band)
    REFB = {(lg, tg, m): float(g.V_band.iloc[0]) for (lg, tg, m), g in
            J[(J.learner == REF_LEARNER) & (J["split"] == REF_SPLIT)
              & (J.quality == REF_QUALITY) & (J.rung == REF_RUNG)]
            .groupby(PAIR + ["metric"])}
    T1b = t1_samemetric(Jb, REFB)
    facts.update(n_disagree_aucref_bandV=int(T1b.n_disagree_aucref.sum()),
                 n_disagree_ownref_bandV=int(T1b.n_disagree_ownref.sum()))
    print("\nT1  resolved %d; disagree with AUC reference %d (%.1f%%), with "
          "own-metric reference %d (%.1f%%); %d leave, %d enter, of which "
          "BPIC19 proper-score leave %d"
          % (n_res, n_auc, 100 * n_auc / n_res, n_own, 100 * n_own / n_res,
             facts["n_leave"], facts["n_enter"],
             facts["n_leave_bpic19_proper"]))
    print(T1[(T1.n_leave > 0) | (T1.n_enter > 0)].to_string(index=False))

    # ---- T2 ---------------------------------------------------------------
    T2, qdev = t2_regions(J)
    T2.to_csv(RESULTS / "s60_metric_regions.csv", index=False)
    facts["max_abs_q_emp_recomputed_minus_file"] = qdev
    by = T2.groupby(PAIR)
    for m in METRICS:
        sub = T2[T2.metric == m]
        facts["n_pairs_differs_" + m] = int(sub.differs.sum())
        facts["n_pairs_differs_within_" + m] = int(sub.differs_within.sum())
    facts["n_pairs_differs_any"] = int(by.differs.any().sum())
    facts["n_pairs_differs_within_any"] = int(by.differs_within.any().sum())
    wide = T2.pivot_table(index=PAIR, columns="metric", values="region",
                          aggfunc="first")
    facts["n_pairs_auc_equals_bss"] = int((wide.auc == wide.brier_skill).sum())
    sc = T2[T2.region_table4 == "sign-changing"]
    sc_within = sc.groupby(PAIR).region.apply(
        lambda s: bool((s == "sign-changing").any()))
    facts["n_pairs_sign_changing_table4"] = int(len(sc_within))
    facts["n_pairs_sign_changing_within_some_metric"] = int(sc_within.sum())
    b19 = T2[T2.log == "BPIC19"].set_index("metric")
    for m in METRICS:
        facts["bpic19_region_" + m] = str(b19.loc[m, "region"])
        facts["bpic19_nb_" + m] = int(b19.loc[m, "n_beneficial"])
        facts["bpic19_nh_" + m] = int(b19.loc[m, "n_harmful"])
    facts["bpic19_across_metric_only"] = bool(
        (b19.region != "sign-changing").all()
        and set(b19.region) >= {"conditionally beneficial"}
        and any(r.endswith("harmful") for r in b19.region))
    facts["q_emp_within_auc_median"] = float(
        T2[T2.metric == "auc"].q_emp_within.median())
    print("\nT2  labels differing from Table 4, by metric:",
          {m: facts["n_pairs_differs_" + m] for m in METRICS},
          "any", facts["n_pairs_differs_any"], "| within-metric families:",
          {m: facts["n_pairs_differs_within_" + m] for m in METRICS},
          "any", facts["n_pairs_differs_within_any"],
          "| whole-surface q_emp recomputed to %.1e" % qdev)
    print(wide.to_string())

    # ---- T3 / T4 ----------------------------------------------------------
    rng = np.random.default_rng(BOOT_SEED)
    ST = S.read_results("s42_strata.csv")
    ST = ST[ST.split_set == "all"]
    pp = ST.groupby(PAIR)[["share_resampling", "share_analyst",
                           "share_counterfactual", "share_mixed"]].median()
    SPC = split_components()
    chk = SPC.merge(ST, on=PAIR + ["metric"])
    facts["max_abs_split_involving_minus_stratum"] = float(
        (chk.split_involving - chk.share_resampling).abs().max())
    spp = SPC.groupby(PAIR).median(numeric_only=True)
    spp.reset_index().to_csv(RESULTS / "s60_split_components.csv",
                             index=False)
    brow = []
    for name, vals in list(pp.items()) + [(c, spp[c]) for c in (
            "split_main", "split_interactions", "split_two_way",
            "split_three_way", "split_four_way", "split_x_rung",
            "split_x_learner", "split_x_quality")]:
        m, lo, hi = pair_bootstrap(vals.values, rng)
        brow.append(dict(quantity=name, median=m, lo=lo, hi=hi,
                         n_pairs=len(vals), n_boot=N_BOOT, seed=BOOT_SEED))
    BT = pd.DataFrame(brow)
    BT.to_csv(RESULTS / "s60_share_boot.csv", index=False)
    print("\nT3/T4  corpus medians with pair-bootstrap intervals")
    print(BT.to_string(index=False, float_format=lambda x: "%.4f" % x))

    # ---- T5 ---------------------------------------------------------------
    PV = SC.pivot_table(index=PAIR + KEY, columns="metric", values="V")
    PV = PV.dropna()
    rows = []
    for m in METRICS:
        st = ST[ST.metric == m]
        sm = T1[T1.metric == m]
        agree = (np.sign(PV[m]) == np.sign(PV["auc"]))
        agree_pair = agree.groupby(level=[0, 1]).mean()
        rows.append(dict(
            metric=m,
            share_split_median=float(st.share_resampling.median()),
            share_analyst_median=float(st.share_analyst.median()),
            share_counterfactual_median=float(st.share_counterfactual.median()),
            share_mixed_median=float(st.share_mixed.median()),
            n_split_largest=int((st.share_resampling > st[[
                "share_analyst", "share_counterfactual",
                "share_mixed"]].max(axis=1)).sum()),
            n_resolved=int(sm.n_resolved.sum()),
            n_pairs_with_resolved=int((sm.n_resolved > 0).sum()),
            n_disagree_ownref=int(sm.n_disagree_ownref.sum()),
            n_disagree_aucref=int(sm.n_disagree_aucref.sum()),
            mad_resolved_own_median=float(sm.mad_resolved_own.median()),
            sign_agree_auc=float(agree.mean()),
            sign_agree_auc_pair_min=float(agree_pair.min()),
            sign_agree_auc_pair_max=float(agree_pair.max()),
            n_specifications=int(len(PV))))
    T5 = pd.DataFrame(rows)
    T5.to_csv(RESULTS / "s60_by_metric.csv", index=False)
    print("\nT5  headlines by metric")
    print(T5.to_string(index=False, float_format=lambda x: "%.4f" % x))
    #  the AUC displacement must reproduce Section 6.4's own figure
    MP = S.read_results("s42_mpid.csv")
    facts["max_abs_mad_auc_minus_s42"] = float(
        (T1[T1.metric == "auc"].set_index(PAIR).mad_resolved_own
         - MP.set_index(PAIR).mad_resolved).abs().max())

    # ---- T6 ---------------------------------------------------------------
    print("\nT6  the reference cell, refitted")
    rows, preds = [], []
    for log, target, _dom in S01.admitted_pairs():
        r, p = t6_refit(log, target)
        if r is None:
            continue
        rows.append(r)
        preds.append(p)
        print("  %-18s %-9s n_te=%6d dAUC=%+.4f  DM(B) %+6.2f  CW %+6.2f  "
              "DM(LL) %+6.2f" % (log, target, r["n_test"], r["auc_increment"],
                                 r["dm_brier_t"], r["cw_t"],
                                 r["dm_logloss_t"]), flush=True)
    T6 = pd.DataFrame(rows).sort_values(PAIR)
    ref = SC[(SC.learner == REF_LEARNER) & (SC["split"] == REF_SPLIT)
             & (SC.quality == REF_QUALITY) & (SC.rung == REF_RUNG)]
    ref = ref.pivot_table(index=PAIR, columns="metric", values="V")
    T6 = T6.join(ref[["auc", "brier_skill", "logloss_skill"]]
                 .rename(columns=lambda c: "surface_" + c), on=PAIR)
    #  and the inference surface's reference cell, which is the cell Table 4
    #  prints: the refit must reproduce THAT exactly.  The declared surface
    #  was run separately and is compared too, so a difference between the
    #  two stored surfaces is on disk rather than discovered by a reader.
    CE = S.read_results("s48w_cells.csv")
    CE = CE[(CE.learner == REF_LEARNER) & (CE["split"] == REF_SPLIT)
            & (CE.quality == REF_QUALITY) & (CE.rung == REF_RUNG)]
    CE = CE.pivot_table(index=PAIR, columns="metric", values="V")
    T6 = T6.join(CE[["auc", "brier_skill", "logloss_skill"]]
                 .rename(columns=lambda c: "table4_" + c), on=PAIR)
    for m in ("auc", "brier_skill", "logloss_skill"):
        T6["absdiff_" + m] = (T6[m + "_increment"] - T6["surface_" + m]).abs()
        T6["absdiff_table4_" + m] = (T6[m + "_increment"]
                                     - T6["table4_" + m]).abs()
    T6.to_csv(RESULTS / "s60_reference_tests.csv", index=False)
    #  mtime 0, so that an unchanged rerun writes an unchanged file
    pd.concat(preds).to_csv(RESULTS / "s60_reference_predictions.csv.gz",
                            index=False, float_format="%.17g",
                            compression={"method": "gzip", "mtime": 0})
    facts.update(
        t6_n_pairs=len(T6),
        t6_max_absdiff_auc=float(T6.absdiff_auc.max()),
        t6_max_absdiff_table4_auc=float(T6.absdiff_table4_auc.max()),
        t6_max_absdiff_table4_brier_skill=float(
            T6.absdiff_table4_brier_skill.max()),
        t6_max_absdiff_table4_logloss_skill=float(
            T6.absdiff_table4_logloss_skill.max()),
        t6_n_exact_surface_auc=int((T6.absdiff_auc < 1e-12).sum()),
        t6_max_absdiff_brier_skill=float(T6.absdiff_brier_skill.max()),
        t6_max_absdiff_logloss_skill=float(T6.absdiff_logloss_skill.max()),
        t6_n_reject_dm_brier=int(T6.dm_brier_reject.sum()),
        t6_n_reject_cw=int(T6.cw_reject.sum()),
        t6_n_reject_dm_logloss=int(T6.dm_logloss_reject.sum()),
        t6_n_reject_dm_brier_alt=int(T6.dm_brier_reject_alt.sum()),
        t6_n_reject_cw_alt=int(T6.cw_reject_alt.sum()),
        t6_n_reject_dm_logloss_alt=int(T6.dm_logloss_reject_alt.sum()),
        t6_n_cw_reverses=int(T6.cw_reverses.sum()),
        t6_n_brier_negative=int((T6.brier_diff < 0).sum()),
        t6_n_auc_positive=int((T6.auc_increment > 0).sum()),
        t6_n_auc_logloss_sign_differ=int(
            (np.sign(T6.auc_increment) != np.sign(T6.logloss_diff)).sum()),
        t6_lag_min=int(T6.lag.min()), t6_lag_max=int(T6.lag.max()),
        t6_z=Z_ONE_SIDED)
    print(T6[["log", "target", "n_test", "lag", "auc_increment",
              "absdiff_auc", "dm_brier_t", "cw_t", "dm_logloss_t",
              "cw_reverses"]].to_string(index=False,
                                        float_format=lambda x: "%.4g" % x))

    # ---- T7 ---------------------------------------------------------------
    T7, f7 = t7_foldtrend(SC)
    T7.to_csv(RESULTS / "s60_foldtrend.csv", index=False)
    facts.update(f7)
    print("\nT7  fold trend:", {k: round(v, 4) if isinstance(v, float) else v
                                for k, v in f7.items()})

    facts["runtime_s"] = round(time.time() - t0, 1)
    pd.DataFrame([facts]).to_csv(RESULTS / "s60_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())

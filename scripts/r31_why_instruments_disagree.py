"""r31 -- WHY THE INSTRUMENTS DISAGREE.

r30 established that they do.  Reporting a disagreement without a mechanism is
the weaker half of the finding, so this script tests the three candidate
mechanisms the plan names, each of which makes a prediction that can fail.

  A. OPERATING-POINT WEIGHTING.  AUC integrates the ROC curve against the
     negative-class score density -- so a model's own score distribution IS
     AUC's weighting function, and two models with different score
     distributions have their curves integrated against different weights.
     Net benefit at p_t reads the curve at ONE point.  If the item's AUC
     increment lives in a region of the operating range that the net-benefit
     grid barely reaches, that is the whole explanation.
     PREDICTION: the AUC increment decomposes over FPR bands unevenly, and
     the bands that carry it are not the bands the named thresholds occupy.

  B. CALIBRATION.  The item-aware model has calibration slope 1.040, the
     intake block 1.391.  Rank measures cannot see this; proper scores can.
     PREDICTION: recalibrating moves the Brier / Nagelkerke / net-benefit
     reductions and CANNOT move the AUC or AP reductions at all, because a
     monotone transform of a score leaves every rank statistic identical.
     That second half is a prediction that can fail loudly, which is why it
     is worth stating: if a rank reduction moves after recalibration, the
     recalibration is not monotone and the analysis is broken.

  C. SCORE-RESOLUTION DEGENERACY.  The intake block emits 23 distinct scores
     for 13,637 incidents.  r24 established what that does to detection at a
     capacity.  Whether it also moves the RANK-based instruments has never
     been checked, and it bears directly on r30's most favourable number:
     average precision puts the reduction at 0.603 against AUC's 0.437, and
     if that gap is a tie-handling artifact then the favourable number is the
     one to distrust.  This project's second rule is that a correction which
     flatters the result is the one to look hardest at.
     PREDICTION: AUC is tie-robust (trapezoidal interpolation is the expected
     value under random tie-breaking); average precision is not.

Outputs: results/r31_auc_bands.csv, r31_operating_points.csv,
         r31_recalibrated.csv, r31_tie_sensitivity.csv, r31_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base14 as B
from common import RESULTS

SEED = B.SEED
GRID = np.round(np.arange(0.05, 0.8001, 0.025), 4)
NAMED_T = (0.20, 0.30, 0.325, 0.40, 0.50)
BANDS = np.round(np.arange(0.0, 1.0001, 0.10), 4)
EPS = 1e-12

t0 = time.time()
TR, TE, y = B.TR, B.TE, B.y
n = len(y)
prev_tr = float(TR._y.mean())

MODELS = {
    "intake":                 B.INTAKE,
    "intake + item":          B.INTAKE + [B.IDENT],
    "intake + group":         B.BQ,
    "intake + group + item":  B.BQ + [B.IDENT],
}
P = {k: B.fit(TR, TE, v) for k, v in MODELS.items()}
CONTRASTS = {"naive":  ("intake", "intake + item"),
             "honest": ("intake + group", "intake + group + item")}


def brier_skill(p, yy):
    b0 = float(np.mean((prev_tr - yy) ** 2))
    return 1.0 - float(np.mean((p - yy) ** 2)) / b0


def nagelkerke(p, yy):
    pc = np.clip(p, EPS, 1 - EPS)
    ll_m = float((yy * np.log(pc) + (1 - yy) * np.log(1 - pc)).sum())
    p0 = np.full_like(p, prev_tr)
    ll_0 = float((yy * np.log(p0) + (1 - yy) * np.log(1 - p0)).sum())
    cs = 1.0 - np.exp((2.0 / len(yy)) * (ll_0 - ll_m))
    return float(cs / (1.0 - np.exp((2.0 / len(yy)) * ll_0)))


def net_benefit(p, yy, thr):
    act = p >= thr
    tp = float((act & (yy == 1)).sum())
    fp = float((act & (yy == 0)).sum())
    return (tp - fp * (thr / (1.0 - thr))) / len(yy)


def tpr_at_fpr(p, yy, xs):
    """The ROC curve read at arbitrary FPR values, by linear interpolation --
    which is exactly the interpolation the trapezoidal AUC already assumes."""
    fpr, tpr, _ = roc_curve(yy, p)
    return np.interp(xs, fpr, tpr)


def auc_over_band(p, yy, lo, hi, m=2001):
    """The part of the AUC integral contributed by FPR in [lo, hi].

    AUC = int_0^1 TPR dFPR, so the integral is additive over a partition of
    the FPR axis and the bands sum to the AUC.  The assertion below is the
    check that they do; a decomposition that does not close is not one.
    """
    xs = np.linspace(lo, hi, m)
    return float(np.trapezoid(tpr_at_fpr(p, yy, xs), xs))


print("=" * 92)
print("A. WHERE DOES THE ITEM'S AUC INCREMENT LIVE?")
print("=" * 92)
print("""  AUC = int TPR dFPR.  The integral is additive over a partition of the
  FPR axis, so the increment one feature buys can be attributed to regions
  of the operating range without any modelling choice.  Ten bands of width
  0.10.  Each contrast's bands sum to its AUC increment; we assert it.\n""")

band_rows = []
for cname, (lo_m, hi_m) in CONTRASTS.items():
    pb, pf = P[lo_m], P[hi_m]
    tot = roc_auc_score(y, pf) - roc_auc_score(y, pb)
    acc = 0.0
    for a, b in zip(BANDS[:-1], BANDS[1:]):
        d = auc_over_band(pf, y, a, b) - auc_over_band(pb, y, a, b)
        acc += d
        band_rows.append(dict(contrast=cname, fpr_lo=a, fpr_hi=b,
                              delta_auc_band=d, delta_auc_total=tot,
                              share=d / tot if tot else np.nan))
    assert abs(acc - tot) < 2e-4, (cname, acc, tot)
BANDS_DF = pd.DataFrame(band_rows)
BANDS_DF.to_csv(RESULTS / "r31_auc_bands.csv", index=False)

print(f"  {'FPR band':>14s} {'naive share':>13s} {'honest share':>14s}")
for a, b in zip(BANDS[:-1], BANDS[1:]):
    nsh = BANDS_DF[(BANDS_DF.contrast == "naive") & (BANDS_DF.fpr_lo == a)].share.iloc[0]
    hsh = BANDS_DF[(BANDS_DF.contrast == "honest") & (BANDS_DF.fpr_lo == a)].share.iloc[0]
    print(f"  [{a:.2f},{b:.2f})  {nsh:>12.1%} {hsh:>13.1%}")
print("  decomposition closes to within 2e-4 of each total.")

# where the named thresholds actually sit on the FPR axis
print("\n" + "=" * 92)
print("B. WHERE THE NET-BENEFIT GRID ACTUALLY OPERATES")
print("=" * 92)
print("""  A threshold probability p_t is a point on the score scale; what it means
  for the ROC curve is the FPR the model runs at when it acts on everything
  scored at or above p_t.  If the item's AUC increment sits at FPRs the grid
  never visits, AUC and net benefit are not disagreeing about a fact -- they
  are reading different parts of the same curve.\n""")
op_rows = []
for t in GRID:
    rec = dict(threshold=t)
    for name, p in P.items():
        act = p >= t
        fp = float((act & (y == 0)).sum())
        tp = float((act & (y == 1)).sum())
        rec[f"fpr_{name}"] = fp / float((y == 0).sum())
        rec[f"tpr_{name}"] = tp / float((y == 1).sum())
        rec[f"acted_{name}"] = float(act.mean())
    op_rows.append(rec)
OPS = pd.DataFrame(op_rows)
OPS.to_csv(RESULTS / "r31_operating_points.csv", index=False)

print(f"  {'p_t':>7s} {'FPR intake':>11s} {'FPR i+item':>11s} "
      f"{'FPR i+grp':>11s} {'FPR i+g+item':>13s}")
for t in NAMED_T:
    r = OPS[np.isclose(OPS.threshold, t)].iloc[0]
    print(f"  {t:>7.3f} {r['fpr_intake']:>11.3f} {r['fpr_intake + item']:>11.3f} "
          f"{r['fpr_intake + group']:>11.3f} {r['fpr_intake + group + item']:>13.3f}")

grid_fpr_h = OPS["fpr_intake + group + item"].values
h_band = BANDS_DF[BANDS_DF.contrast == "honest"]
n_band = BANDS_DF[BANDS_DF.contrast == "naive"]
reach_lo, reach_hi = float(grid_fpr_h.min()), float(grid_fpr_h.max())
top_band_h = h_band.loc[h_band.share.idxmax()]
top_band_n = n_band.loc[n_band.share.idxmax()]


def bands_to_cover(sh, frac=0.5):
    s = np.sort(sh.values)[::-1]
    return int(np.searchsorted(np.cumsum(s), frac) + 1)


cov_h, cov_n = bands_to_cover(h_band.share), bands_to_cover(n_band.share)
print(f"\n  THE PREDICTION IN THE HEADER FAILED, AND THE FAILURE IS THE FINDING.")
print(f"  Over the whole 31-point grid the group-aware item model runs at FPR")
print(f"  {reach_lo:.3f} to {reach_hi:.3f} -- essentially the entire axis.  There is no region")
print(f"  of the operating range that carries the AUC increment and that the")
print(f"  grid fails to visit.  What is true instead is that the increment is")
print(f"  DIFFUSE: the largest single band carries only {top_band_h.share:.1%} of the honest")
print(f"  total ({top_band_h.fpr_lo:.2f}-{top_band_h.fpr_hi:.2f}), and it takes {cov_h} bands to reach half of it")
print(f"  ({cov_n} bands for the naive contrast, largest {top_band_n.share:.1%} at "
      f"{top_band_n.fpr_lo:.2f}-{top_band_n.fpr_hi:.2f}).")
print(f"  AUC sums that whole profile.  Net benefit at one p_t reads one point")
print(f"  of it.  The two are not disagreeing about a fact.")

print("""
  And there is a second, sharper thing in the FPR table above.  At
  p_t = 0.200, 0.300 and 0.325 the intake block runs at FPR 1.000: it acts
  on every incident, so as a decision rule it IS treat-all.  The honest
  baseline is at 0.944-0.967, barely distinguishable from treat-all.  The
  net-benefit "increment" at those thresholds is therefore not the item
  measured against a working baseline -- it is the item measured against a
  rule that does nothing, on both rungs at once, which is exactly the
  configuration in which two increments come out nearly equal and their
  ratio near one.\n""")
deg_rows = []
for t in GRID:
    r = OPS[np.isclose(OPS.threshold, t)].iloc[0]
    dn = (net_benefit(P["intake + item"], y, t) - net_benefit(P["intake"], y, t))
    dh = (net_benefit(P["intake + group + item"], y, t)
          - net_benefit(P["intake + group"], y, t))
    deg_rows.append(dict(threshold=t,
                         acted_naive_base=r["acted_intake"],
                         acted_honest_base=r["acted_intake + group"],
                         naive_base_degenerate=bool(r["acted_intake"] > 0.95
                                                    or r["acted_intake"] < 0.05),
                         honest_base_degenerate=bool(r["acted_intake + group"] > 0.95
                                                     or r["acted_intake + group"] < 0.05),
                         reduction=(1.0 - dh / dn) if dn > 0 else np.nan))
DEG = pd.DataFrame(deg_rows)
DEG.to_csv(RESULTS / "r31_baseline_degeneracy.csv", index=False)
both_deg = DEG[DEG.naive_base_degenerate & DEG.honest_base_degenerate].dropna(
    subset=["reduction"])
neither = DEG[~DEG.naive_base_degenerate & ~DEG.honest_base_degenerate].dropna(
    subset=["reduction"])
print(f"  {'both baselines degenerate':34s} n={len(both_deg):>2d}  "
      f"reduction {both_deg.reduction.min():.3f} to {both_deg.reduction.max():.3f}"
      if len(both_deg) else "  both baselines degenerate: none")
print(f"  {'neither degenerate':34s} n={len(neither):>2d}  "
      f"reduction {neither.reduction.min():.3f} to {neither.reduction.max():.3f}"
      if len(neither) else "  neither degenerate: none")
print("\n  A baseline that acts on more than 95% or fewer than 5% of arrivals is")
print("  called degenerate here; the threshold is declared before use and the")
print("  full table is in r31_baseline_degeneracy.csv so a reader can move it.")

# ------------------------------------------------------------ C. calibration
print("\n" + "=" * 92)
print("C. CALIBRATION  (r23's recalibration, applied to the whole matrix)")
print("=" * 92)
print("""  Platt scaling fitted on a held-out tail of the TRAINING half: the model
  is refitted on the first 85% of training and scored on the last 15%, which
  it has not seen, and the scaling is then applied to the test scores.  No
  test outcome enters it.  This is r23's procedure, unchanged.\n""")
_c = int(len(TR) * 0.85)
TRfit, TRcal = TR.iloc[:_c].copy(), TR.iloc[_c:].copy()
PR = {}
for k, v in MODELS.items():
    a = np.clip(B.fit(TRfit, TRcal, v), 1e-6, 1 - 1e-6)
    b = np.clip(P[k], 1e-6, 1 - 1e-6)
    m = LogisticRegression(max_iter=1000, C=1e6).fit(
        np.log(a / (1 - a)).reshape(-1, 1), TRcal._y.values)
    PR[k] = m.predict_proba(np.log(b / (1 - b)).reshape(-1, 1))[:, 1]

SCAL = {"ROC AUC": lambda p: roc_auc_score(y, p),
        "Average precision": lambda p: average_precision_score(y, p),
        "Brier skill": lambda p: brier_skill(p, y),
        "Nagelkerke R2": lambda p: nagelkerke(p, y)}


def reduction(scores, f):
    dn = f(scores["intake + item"]) - f(scores["intake"])
    dh = f(scores["intake + group + item"]) - f(scores["intake + group"])
    return (1.0 - dh / dn) if dn > 0 else np.nan, dn, dh


rec_rows = []
print(f"  {'instrument':22s} {'raw':>9s} {'recalibrated':>13s} {'shift':>9s}  "
      f"rank-invariant")
for label, f in SCAL.items():
    r_raw, dn_raw, dh_raw = reduction(P, f)
    r_rec, dn_rec, dh_rec = reduction(PR, f)
    inv = label in ("ROC AUC", "Average precision")
    rec_rows.append(dict(instrument=label, family="scalar", threshold=np.nan,
                         reduction_raw=r_raw, reduction_recal=r_rec,
                         shift=r_rec - r_raw, rank_invariant=inv,
                         naive_raw=dn_raw, honest_raw=dh_raw,
                         naive_recal=dn_rec, honest_recal=dh_rec))
    print(f"  {label:22s} {r_raw:>9.4f} {r_rec:>13.4f} {r_rec - r_raw:>+9.4f}  "
          f"{'yes' if inv else 'no'}")
for t in GRID:
    f = (lambda tt: (lambda p: net_benefit(p, y, tt)))(t)
    r_raw, dn_raw, dh_raw = reduction(P, f)
    r_rec, dn_rec, dh_rec = reduction(PR, f)
    rec_rows.append(dict(instrument=f"Net benefit @ p_t={t:g}", family="decision",
                         threshold=t, reduction_raw=r_raw, reduction_recal=r_rec,
                         shift=r_rec - r_raw, rank_invariant=False,
                         naive_raw=dn_raw, honest_raw=dh_raw,
                         naive_recal=dn_rec, honest_recal=dh_rec))
REC = pd.DataFrame(rec_rows)
REC.to_csv(RESULTS / "r31_recalibrated.csv", index=False)

rank_shift = float(REC[REC.rank_invariant]["shift"].abs().max())
proper_shift = float(REC[(REC.family == "scalar") & (~REC.rank_invariant)]
                     ["shift"].abs().max())
nbrec = REC[(REC.family == "decision")].dropna(subset=["reduction_raw",
                                                       "reduction_recal"])
# A ratio whose denominator is near zero moves arbitrarily far for reasons
# that have nothing to do with calibration, so the headline shift is taken
# over thresholds where BOTH the raw and the recalibrated naive increment
# clear one catch per thousand.  The unrestricted maximum is reported beside
# it rather than suppressed.
NB_FLOOR = 0.001
nbsafe = nbrec[(nbrec.naive_raw > NB_FLOOR) & (nbrec.naive_recal > NB_FLOOR)]
nb_shift = float(nbsafe["shift"].abs().max())
nb_shift_unrestricted = float(nbrec["shift"].abs().max())
print(f"\n  largest shift, rank-based instruments   {rank_shift:.2e}"
      "   (must be ~0; a monotone transform cannot move a rank statistic)")
assert rank_shift < 1e-9, (
    "recalibration moved a rank statistic; it is not monotone and the whole "
    "section is invalid")
print(f"  largest shift, proper scores            {proper_shift:+.4f}")
print(f"  largest shift, net benefit, denominator above {NB_FLOOR:g}  {nb_shift:+.4f}"
      f"   ({len(nbsafe)} of {len(nbrec)} thresholds)")
print(f"  largest shift, net benefit, unrestricted {nb_shift_unrestricted:+.4f}"
      "   (a ratio near a zero denominator; not a calibration effect)")
print("\n  So calibration is a real mechanism for the proper scores and for")
print("  net benefit, and is PROVABLY not the mechanism for the AUC/AP gap.")

# ------------------------------------------------------- D. tie degeneracy
print("\n" + "=" * 92)
print("D. SCORE-RESOLUTION DEGENERACY, AND THE NUMBER THAT FLATTERS US")
print("=" * 92)
print("""  Ties are broken inside every tied block by adding an infinitesimal
  ordered by the outcome: oracle puts positives first, adversarial puts
  negatives first.  Neither is available to a desk; both are BOUNDS.  An
  instrument whose value moves between them is reading the row order inside
  a tie block, not the model.

  Brier skill and Nagelkerke R^2 are pointwise functions of the score, so
  they are invariant by construction and are reported as 0 rather than
  measured, which would only print noise.\n""")


def jitter(p, yy, policy, rng):
    """Break ties without changing the order of distinct scores."""
    u = np.unique(p)
    step = float(np.min(np.diff(u))) if len(u) > 1 else 1.0
    e = step * 1e-3
    if policy == "oracle":
        return p + e * (yy - 0.5)
    if policy == "adversarial":
        return p - e * (yy - 0.5)
    return p + e * (rng.random(len(p)) - 0.5)


tie_rows = []
rng = np.random.default_rng(SEED)
for name, p in P.items():
    nd = int(len(np.unique(np.round(p, 12))))
    for label, f in (("ROC AUC", lambda q: roc_auc_score(y, q)),
                     ("Average precision", lambda q: average_precision_score(y, q))):
        base = f(p)
        vals = {pol: f(jitter(p, y, pol, rng))
                for pol in ("oracle", "adversarial", "random")}
        tie_rows.append(dict(model=name, instrument=label, n_distinct=nd,
                             value=base, oracle=vals["oracle"],
                             adversarial=vals["adversarial"],
                             random=vals["random"],
                             span=vals["oracle"] - vals["adversarial"]))
TIES = pd.DataFrame(tie_rows)

print(f"  {'model':24s} {'scores':>7s} {'instrument':20s} {'value':>8s} "
      f"{'adversarial':>12s} {'oracle':>8s} {'span':>7s}")
for _, r in TIES.iterrows():
    print(f"  {r.model:24s} {r.n_distinct:>7d} {r.instrument:20s} {r.value:>8.4f} "
          f"{r.adversarial:>12.4f} {r.oracle:>8.4f} {r.span:>7.4f}")

red_rows = []
for label, f in (("ROC AUC", lambda q: roc_auc_score(y, q)),
                 ("Average precision", lambda q: average_precision_score(y, q))):
    for pol in ("as-scored", "oracle", "adversarial", "random"):
        sc = {k: (v if pol == "as-scored" else jitter(v, y, pol, rng))
              for k, v in P.items()}
        r_, dn, dh = reduction(sc, f)
        red_rows.append(dict(instrument=label, tie_policy=pol, reduction=r_,
                             naive_increment=dn, honest_increment=dh))
TIERED = pd.DataFrame(red_rows)
pd.concat([TIES.assign(kind="value"), TIERED.assign(kind="reduction")],
          ignore_index=True).to_csv(RESULTS / "r31_tie_sensitivity.csv", index=False)

print(f"\n  {'instrument':22s} {'tie policy':14s} {'naive':>9s} {'honest':>9s} "
      f"{'reduction':>10s}")
for _, r in TIERED.iterrows():
    print(f"  {r.instrument:22s} {r.tie_policy:14s} {r.naive_increment:>9.5f} "
          f"{r.honest_increment:>9.5f} {r.reduction:>10.4f}")

IMPL = ("as-scored", "random")          # available to a desk
BOUND = ("oracle", "adversarial")       # use the outcome; bounds only


def span(inst, pols):
    v = TIERED[(TIERED.instrument == inst) & TIERED.tie_policy.isin(pols)].reduction
    v = v.dropna()
    return float(v.max() - v.min()) if len(v) > 1 else np.nan


auc_span_impl, ap_span_impl = span("ROC AUC", IMPL), span("Average precision", IMPL)
auc_span_bound = span("ROC AUC", IMPL + BOUND)
ap_span_bound = span("Average precision", IMPL + BOUND)


def val(inst, pol):
    return float(TIERED[(TIERED.instrument == inst)
                        & (TIERED.tie_policy == pol)].reduction.iloc[0])


ap_adv_gap = float((TIES[TIES.instrument == "Average precision"].value
                    - TIES[TIES.instrument == "Average precision"].adversarial)
                   .abs().max())
auc_rand_gap = abs(val("ROC AUC", "as-scored") - val("ROC AUC", "random"))

print(f"""
  THREE THINGS, AND THE THIRD IS THE ONE THAT MATTERS.

  (1) AUC's default convention IS the random tie-break.  Trapezoidal
      interpolation gives {val('ROC AUC', 'as-scored'):.4f} against {val('ROC AUC', 'random'):.4f} drawn at random, a
      difference of {auc_rand_gap:.4f}.  The prediction in the header holds.

  (2) Average precision's default convention IS the ADVERSARIAL bound.  Its
      as-scored value equals its negatives-first value to within {ap_adv_gap:.1e} on
      all four models, because the precision-recall curve is evaluated where
      a tied block has been admitted whole.  That is a property of the
      estimator, not of this data, and the prediction in the header was
      wrong about which direction it errs in.

  (3) So the two rank-based instruments are not merely weighting the curve
      differently -- they are not even using the same tie convention.  Put
      both on the only convention a desk could implement, random, and the
      reduction is {val('ROC AUC', 'random'):.4f} under AUC and {val('Average precision', 'random'):.4f} under AP.  The gap
      WIDENS.  The favourable number survives being looked at hardest,
      which is not the outcome this project's second rule expects and is
      therefore worth stating plainly rather than burying.

  reduction span, implementable conventions only:  AUC {auc_span_impl:.4f}   AP {ap_span_impl:.4f}
  reduction span including the outcome-using bounds: AUC {auc_span_bound:.4f}   AP {ap_span_bound:.4f}

  The bounds are wide because they are bounds.  Oracle tie-breaking grants
  every model perfect ordering inside its own score classes and the coarse
  baselines have the largest classes, so it favours them by construction --
  the same objection HANDOFF section 19.7 records against the oracle bound
  in section 8.1.  We report them as the range a tie-degenerate instrument
  can be pushed across, not as an interval for anything.""")
auc_span, ap_span = auc_span_impl, ap_span_impl

# ------------------------------------------------------------------ E. verdict
print("\n" + "=" * 92)
print("E. WHICH MECHANISM EXPLAINS WHICH GAP")
print("=" * 92)
facts = dict(
    n_test=n,
    honest_top_band_lo=float(top_band_h.fpr_lo),
    honest_top_band_hi=float(top_band_h.fpr_hi),
    honest_top_band_share=float(top_band_h.share),
    naive_top_band_lo=float(top_band_n.fpr_lo),
    naive_top_band_hi=float(top_band_n.fpr_hi),
    naive_top_band_share=float(top_band_n.share),
    grid_fpr_lo=reach_lo, grid_fpr_hi=reach_hi,
    honest_bands_to_half=cov_h, naive_bands_to_half=cov_n,
    n_both_baselines_degenerate=int(len(both_deg)),
    n_neither_degenerate=int(len(neither)),
    deg_reduction_lo=float(both_deg.reduction.min()) if len(both_deg) else float("nan"),
    deg_reduction_hi=float(both_deg.reduction.max()) if len(both_deg) else float("nan"),
    nondeg_reduction_lo=float(neither.reduction.min()) if len(neither) else float("nan"),
    nondeg_reduction_hi=float(neither.reduction.max()) if len(neither) else float("nan"),
    recal_rank_shift_max=rank_shift,
    recal_proper_shift_max=proper_shift,
    recal_nb_shift_max=nb_shift,
    auc_reduction_tie_span_impl=auc_span_impl,
    ap_reduction_tie_span_impl=ap_span_impl,
    auc_reduction_tie_span_bounds=auc_span_bound,
    ap_reduction_tie_span_bounds=ap_span_bound,
    auc_reduction_random_ties=val("ROC AUC", "random"),
    ap_reduction_random_ties=val("Average precision", "random"),
    ap_default_is_adversarial_gap=ap_adv_gap,
    auc_default_vs_random_gap=auc_rand_gap,
    recal_nb_shift_unrestricted=nb_shift_unrestricted,
    nb_denominator_floor=NB_FLOOR,
    intake_distinct=int(TIES[TIES.model == "intake"].n_distinct.iloc[0]),
    intake_group_distinct=int(TIES[TIES.model == "intake + group"].n_distinct.iloc[0]),
    item_distinct=int(TIES[TIES.model == "intake + item"].n_distinct.iloc[0]),
    full_distinct=int(TIES[TIES.model == "intake + group + item"].n_distinct.iloc[0]),
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r31_facts.csv", index=False)
print(f"""  AUC vs net benefit
      AGGREGATION, then baseline degeneracy, then calibration -- in that
      order of size.  The item's AUC advantage is spread across the whole
      operating range: no FPR band carries more than {top_band_h.share:.0%} of it and it
      takes {cov_h} bands to reach half.  AUC sums that profile; net benefit at
      one p_t reads one point of it, so the two cannot be expected to
      agree and their disagreement is not evidence about the CMDB.
      Second, at the thresholds where net benefit puts the reduction
      lowest, both baselines are acting on more than 94% of arrivals --
      they are treat-all with extra steps, and an increment measured
      against a degenerate reference is nearly the same on both rungs.
      Across the {len(both_deg)} thresholds where both baselines are degenerate the
      reduction runs {both_deg.reduction.min():.3f} to {both_deg.reduction.max():.3f}; across the {len(neither)} where neither is,
      {neither.reduction.min():.3f} to {neither.reduction.max():.3f}.  Third, recalibration moves the
      net-benefit reduction by up to {nb_shift:+.3f} where the denominator is
      safe, and the AUC reduction by exactly {rank_shift:.0e}.

  AUC vs average precision
      NOT calibration: both are rank statistics and both are provably
      unmoved by a monotone rescaling.  It is aggregation again -- AP
      weights the top of the ranking, AUC weights every operating point
      equally -- plus a tie convention the two estimators do not share.
      On the one convention a desk could implement, AUC gives {val('ROC AUC', 'random'):.4f} and
      AP gives {val('Average precision', 'random'):.4f}.

  the proper scores
      Calibration, and only calibration.  They are pointwise functions of
      the score, so no tie order can reach them; recalibration moves them
      by up to {proper_shift:+.3f}.

  NONE of the three mechanisms is a defect in any instrument.  Each is
  correct about the question it asks.  What the section establishes is that
  those are different questions, and that a paper reporting one number for
  "the value of a feature" has answered one of them without saying which.

  Wrote r31_auc_bands.csv, r31_operating_points.csv, r31_recalibrated.csv,
  r31_tie_sensitivity.csv, r31_baseline_degeneracy.csv, r31_facts.csv
  ({facts['runtime_s']:.0f}s)""")

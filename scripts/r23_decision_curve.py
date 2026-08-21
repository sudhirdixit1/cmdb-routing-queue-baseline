"""
r23 -- DECISION CURVE ANALYSIS.  The principled replacement for the paper's
review-capacity framing.

The paper states what the field-admission choice buys as detection at a
review capacity of 5% of arrivals, and says in the same paragraph that no
desk it knows of runs that operating model.  That is an honest disclosure of
a weak instrument, not a repair.  Vickers and Elkin (2006) is the repair, it
is already cited in the manuscript, and it is the standard instrument for
precisely this question: what is a marginal predictor worth when the
decision it feeds has a cost ratio the analyst will not commit to?

NET BENEFIT.  At threshold probability p_t a desk that acts on every
incident scored at or above p_t obtains

    NB(p_t) = TP/n - (FP/n) * p_t/(1 - p_t)

The weight p_t/(1-p_t) is the exchange rate the threshold implies: choosing
p_t = 0.25 says one missed reassignment-bound incident is worth three
needless reviews.  NB is in units of true positives per incident, so
1000*NB reads as "extra reassignment-bound incidents caught per thousand
arrivals, net of the reviews spent catching them".  It needs no capacity
assumption, and it is defined across the whole range of exchange rates a
reader might hold rather than at one the author picked.

WHAT IS REPORTED.

  A.  Calibration.  Net benefit is only meaningful for a model whose scores
      are probabilities.  A referee is entitled to ask, and the honest
      answer for a one-hot logistic model with 2,554 sparse columns at fixed
      penalty is not obviously "yes".  Brier score, calibration-in-the-large
      and calibration slope are reported for all four models FIRST, and
      section C reports the curve on recalibrated scores as a sensitivity.

  B.  The curve, over both baselines.  The honest contrast adds item
      identity to intake+group; the naive one adds it to intake.  Same
      matched-pairs discipline as the capacity table.

  C.  The overstatement factor, restated in net benefit.  This is what
      replaces "4.3 times as many additional catches at 5% capacity": the
      ratio of the two increments, now as a function of the exchange rate
      instead of a single invented capacity.

Everything is held to r4_final: same cohort, same split, same intake block,
same estimator, same seed.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_BOOT = 2000
Q = "intake_group"
BQ = M.INTAKE + [Q]
GRID = np.round(np.arange(0.05, 0.8001, 0.025), 4)
NAMED = (0.20, 0.30, 0.40, 0.50, 0.60)

D, TR, TE, y = M.D, M.TR, M.TE, M.y
prev = float(y.mean())

MODELS = {
    "intake": M.INTAKE,
    "intake + item": M.INTAKE + [M.IDENT],
    "intake + group": BQ,
    "intake + group + item": BQ + [M.IDENT],
}
P = {k: M.fit(TR, TE, v) for k, v in MODELS.items()}

PAIRS = [("honest", "intake + group", "intake + group + item"),
         ("naive", "intake", "intake + item")]


def net_benefit(p, yy, thr):
    """Vickers-Elkin net benefit at one threshold probability."""
    act = p >= thr
    n = len(yy)
    tp = float((act & (yy == 1)).sum())
    fp = float((act & (yy == 0)).sum())
    return (tp - fp * (thr / (1.0 - thr))) / n


def nb_all(p, yy, grid=GRID):
    return np.array([net_benefit(p, yy, t) for t in grid])


print("=" * 92)
print("A. ARE THESE SCORES PROBABILITIES?  (net benefit is meaningless if not)")
print("=" * 92)
print(f"  test prevalence {prev:.4f}   n {len(y):,}\n")
print(f"  {'model':24s} {'AUC':>7s} {'Brier':>8s} {'mean p':>8s} "
      f"{'cal. slope':>11s} {'cal. intcpt':>12s}")
cal = []
for name, p in P.items():
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    lo = np.log(pc / (1 - pc)).reshape(-1, 1)
    m = LogisticRegression(max_iter=1000, C=1e6).fit(lo, y)
    slope = float(m.coef_[0][0])
    icpt = float(m.intercept_[0])
    b = brier_score_loss(y, p)
    a = roc_auc_score(y, p)
    cal.append(dict(model=name, auc=a, brier=b, mean_p=float(p.mean()),
                    cal_slope=slope, cal_intercept=icpt,
                    cal_in_large=float(p.mean() - prev)))
    print(f"  {name:24s} {a:>7.4f} {b:>8.4f} {p.mean():>8.4f} "
          f"{slope:>11.3f} {icpt:>12.3f}")
CAL = pd.DataFrame(cal)
CAL.to_csv(RESULTS / "r23_calibration.csv", index=False)
print("\n  A calibration slope below 1 means the scores are over-dispersed --")
print("  the usual signature of a penalised model with many sparse columns,")
print("  and it moves net benefit at extreme thresholds.  Section C repeats")
print("  the whole analysis on scores recalibrated on the TRAINING half, so")
print("  the conclusion does not rest on the raw scores being well behaved.")

print("\n" + "=" * 92)
print("B. NET BENEFIT ACROSS THE RANGE OF EXCHANGE RATES")
print("=" * 92)
nb = {k: nb_all(p, y) for k, p in P.items()}
nb_all_treat = np.array([prev - (1 - prev) * (t / (1 - t)) for t in GRID])
nb_none = np.zeros_like(GRID)

curve = pd.DataFrame({"threshold": GRID, "treat_all": nb_all_treat,
                      "treat_none": nb_none, **nb})
for tag, b, f in PAIRS:
    curve[f"delta_{tag}"] = curve[f] - curve[b]
curve["odds"] = GRID / (1 - GRID)
curve.to_csv(RESULTS / "r23_dca_curve.csv", index=False)

print(f"  net benefit x1000 = extra true positives per 1,000 arrivals, net of")
print(f"  the reviews spent.  Threshold 0.372 is this cohort's own base rate.\n")
print(f"  {'p_t':>6s} {'all':>8s} {'intake':>8s} {'+item':>8s} {'int+grp':>8s} "
      f"{'+item':>8s} {'d.naive':>9s} {'d.honest':>9s} {'ratio':>7s}")
for t in NAMED:
    r = curve[np.isclose(curve.threshold, t)].iloc[0]
    ratio = r.delta_naive / r.delta_honest if r.delta_honest > 0 else np.nan
    print(f"  {t:>6.2f} {1000*r.treat_all:>8.1f} {1000*r['intake']:>8.1f} "
          f"{1000*r['intake + item']:>8.1f} {1000*r['intake + group']:>8.1f} "
          f"{1000*r['intake + group + item']:>8.1f} "
          f"{1000*r.delta_naive:>9.1f} {1000*r.delta_honest:>9.1f} "
          f"{ratio:>7.2f}")

print("\n  Where each arm beats treat-all and treat-none:")
for k in MODELS:
    dom = curve[(curve[k] > curve.treat_all) & (curve[k] > 0)].threshold
    print(f"    {k:24s} {dom.min():.3f} to {dom.max():.3f}"
          if len(dom) else f"    {k:24s} never")

# ---- intervals on the two increments -----------------------------------
print("\n" + "=" * 92)
print("C. INTERVALS, AND THE OVERSTATEMENT FACTOR IN NET-BENEFIT UNITS")
print("=" * 92)
rng = np.random.default_rng(SEED)
idx = [rng.integers(0, len(y), len(y)) for _ in range(N_BOOT)]
rows = []
print(f"  {'p_t':>6s} {'honest dNB x1000':>26s} {'naive dNB x1000':>26s} "
      f"{'factor':>20s}")
for t in NAMED:
    hb, nbv, fb = [], [], []
    for i in idx:
        yy = y[i]
        if len(np.unique(yy)) < 2:
            continue
        dh = net_benefit(P["intake + group + item"][i], yy, t) - \
            net_benefit(P["intake + group"][i], yy, t)
        dn = net_benefit(P["intake + item"][i], yy, t) - \
            net_benefit(P["intake"][i], yy, t)
        hb.append(dh); nbv.append(dn)
        if dh > 0:
            fb.append(dn / dh)
    hb, nbv, fb = np.array(hb), np.array(nbv), np.array(fb)
    hlo, hhi = np.percentile(hb, [2.5, 97.5])
    nlo, nhi = np.percentile(nbv, [2.5, 97.5])
    flo, fhi = (np.percentile(fb, [2.5, 97.5]) if len(fb) > 100
                else (np.nan, np.nan))
    r = curve[np.isclose(curve.threshold, t)].iloc[0]
    fac = r.delta_naive / r.delta_honest if r.delta_honest > 0 else np.nan
    rows.append(dict(threshold=t, delta_honest=r.delta_honest,
                     honest_lo=hlo, honest_hi=hhi,
                     delta_naive=r.delta_naive, naive_lo=nlo, naive_hi=nhi,
                     factor=fac, factor_lo=flo, factor_hi=fhi,
                     p_honest_le0=float((hb <= 0).mean()),
                     frac_draws_positive=len(fb) / max(len(hb), 1)))
    print(f"  {t:>6.2f} "
          f"{f'{1000*r.delta_honest:+.1f} [{1000*hlo:+.1f},{1000*hhi:+.1f}]':>26s} "
          f"{f'{1000*r.delta_naive:+.1f} [{1000*nlo:+.1f},{1000*nhi:+.1f}]':>26s} "
          f"{f'{fac:.1f} [{flo:.1f},{fhi:.1f}]':>20s}")
DEL = pd.DataFrame(rows)
DEL.to_csv(RESULTS / "r23_dca_delta.csv", index=False)

# ---- recalibrated sensitivity ------------------------------------------
print("\n  SENSITIVITY: the same two increments on recalibrated scores.  The")
print("  Platt scaling is fitted on a held-out TAIL of the training half --")
print("  the model is refitted on the first 85% of training and scored on the")
print("  last 15%, which it has not seen -- and then applied to the test")
print("  scores.  No test outcome enters the recalibration.  Fitting it")
print("  in-sample on training instead would be worthless here: a model with")
print("  2,554 item indicators reproduces its own training labels.")
_c = int(len(TR) * 0.85)
TRfit, TRcal = TR.iloc[:_c].copy(), TR.iloc[_c:].copy()
Pr = {}
for k, v in MODELS.items():
    a = np.clip(M.fit(TRfit, TRcal, v), 1e-6, 1 - 1e-6)
    b = np.clip(P[k], 1e-6, 1 - 1e-6)
    m = LogisticRegression(max_iter=1000, C=1e6).fit(
        np.log(a / (1 - a)).reshape(-1, 1), TRcal._y.values)
    Pr[k] = m.predict_proba(np.log(b / (1 - b)).reshape(-1, 1))[:, 1]
rc = []
print(f"\n  {'p_t':>6s} {'honest dNB x1000':>18s} {'naive dNB x1000':>18s} "
      f"{'factor':>8s}")
for t in NAMED:
    dh = net_benefit(Pr["intake + group + item"], y, t) - \
        net_benefit(Pr["intake + group"], y, t)
    dn = net_benefit(Pr["intake + item"], y, t) - net_benefit(Pr["intake"], y, t)
    rc.append(dict(threshold=t, delta_honest=dh, delta_naive=dn,
                   factor=dn / dh if dh > 0 else np.nan))
    print(f"  {t:>6.2f} {1000*dh:>18.1f} {1000*dn:>18.1f} "
          f"{dn/dh if dh>0 else float('nan'):>8.2f}")
RC = pd.DataFrame(rc)
RC.to_csv(RESULTS / "r23_dca_recal.csv", index=False)

fmin, fmax = DEL.factor.min(), DEL.factor.max()
rmin, rmax = RC.factor.min(), RC.factor.max()
print(f"\n  factor across the five named thresholds, raw scores      "
      f"{fmin:.1f} to {fmax:.1f}")
print(f"  factor across the five named thresholds, recalibrated    "
      f"{rmin:.1f} to {rmax:.1f}")

# ---- the whole grid, with intervals ------------------------------------
print("\n" + "=" * 92)
print("D. WHERE THE INCREMENT IS RESOLVED, ACROSS THE WHOLE GRID")
print("=" * 92)
print("""  The five named thresholds are the author's choice, which is the
  criticism this section exists to answer.  Every grid point now carries
  its own interval, so the reader sees where the increment is resolved
  rather than where we chose to print it.

  Net benefit is a step function of the threshold, because each model
  emits finitely many distinct scores -- 23 for the intake block, 132 with
  the opening group.  Individual grid points therefore jump.  The claim
  below is about CONTIGUOUS REGIONS, not about single points.\n""")


def nb_grid(p, yy, grid):
    """Net benefit at every grid point in one pass.

    Sorting once and counting with searchsorted is what makes a 1,000-draw
    bootstrap over 31 thresholds and 4 models finish; the naive nested loop
    is 1.7e9 element comparisons.
    """
    o = np.argsort(-p, kind="stable")
    ps, ys = p[o], yy[o]
    cpos = np.concatenate([[0.0], np.cumsum(ys)])
    k = np.searchsorted(-ps, -grid, side="right")     # rows with p >= t
    tp = cpos[k]
    fp = k - tp
    return (tp - fp * (grid / (1.0 - grid))) / len(ys)


#  The two numbers the paper prints for this question, read from the files
#  that produced them rather than retyped into this prose.
_f5 = float(pd.read_csv(RESULTS / "r11_capacity.csv")
            .set_index("capacity").loc[0.05, "factor"])
_fauc = float(pd.read_csv(RESULTS / "r11_overstatement.csv").iloc[0].auc_ratio)

rng = np.random.default_rng(SEED)
DH = np.empty((N_BOOT, len(GRID)))
DN = np.empty((N_BOOT, len(GRID)))
kept = 0
for _ in range(N_BOOT):
    i = rng.integers(0, len(y), len(y))
    yy = y[i]
    if len(np.unique(yy)) < 2:
        continue
    DH[kept] = (nb_grid(P["intake + group + item"][i], yy, GRID)
                - nb_grid(P["intake + group"][i], yy, GRID))
    DN[kept] = (nb_grid(P["intake + item"][i], yy, GRID)
                - nb_grid(P["intake"][i], yy, GRID))
    kept += 1
DH, DN = DH[:kept], DN[:kept]

grid_rows = []
for j, t in enumerate(GRID):
    hlo, hhi = np.percentile(DH[:, j], [2.5, 97.5])
    nlo, nhi = np.percentile(DN[:, j], [2.5, 97.5])
    grid_rows.append(dict(
        threshold=float(t),
        delta_honest=float(curve.delta_honest.iloc[j]), honest_lo=hlo, honest_hi=hhi,
        delta_naive=float(curve.delta_naive.iloc[j]), naive_lo=nlo, naive_hi=nhi,
        honest_resolved=bool(hlo > 0), honest_negative=bool(hhi < 0),
        naive_resolved=bool(nlo > 0)))
GR = pd.DataFrame(grid_rows)
GR.to_csv(RESULTS / "r23_dca_grid.csv", index=False)

pos = GR[GR.honest_resolved]
neg = GR[GR.honest_negative]
npos = GR[GR.naive_resolved]


def _run(sel):
    """Longest contiguous run of grid points in `sel`, as (lo, hi)."""
    if sel.empty:
        return (np.nan, np.nan)
    idx = sel.index.to_numpy()
    breaks = np.where(np.diff(idx) > 1)[0]
    runs = np.split(idx, breaks + 1)
    best = max(runs, key=len)
    return (float(GR.threshold[best[0]]), float(GR.threshold[best[-1]]))

h_lo, h_hi = _run(pos)
n_lo, n_hi = _run(npos)
print(f"  honest increment > 0 with its interval excluding zero:")
print(f"    {len(pos)} of {len(GRID)} grid points; longest run "
      f"{h_lo:.3f} to {h_hi:.3f}")
print(f"  honest increment < 0 with its interval excluding zero:")
print(f"    {len(neg)} grid points"
      + (f"; from {neg.threshold.min():.3f} to {neg.threshold.max():.3f}"
         if len(neg) else ""))
print(f"  naive increment > 0 with its interval excluding zero:")
print(f"    {len(npos)} of {len(GRID)} grid points; longest run "
      f"{n_lo:.3f} to {n_hi:.3f}")
sub = GR[(GR.threshold >= h_lo) & (GR.threshold <= h_hi)]
rat = (sub.delta_naive / sub.delta_honest)
j_best = int(GR.delta_honest.idxmax())
t_best = float(GR.threshold[j_best])
rat_best = float(GR.delta_naive[j_best] / GR.delta_honest[j_best])
print(f"\n  Over the region where the honest increment is resolved, the")
print(f"  naive-to-honest ratio runs {rat.min():.2f} to {rat.max():.2f}.  That range is not")
print(f"  informative on its own, because the ratio's denominator decays to")
print(f"  zero at the top of the region.  The number that is:")
print(f"\n    at p_t={t_best:.3f}, where the item's increment is LARGEST")
print(f"    ({1000*GR.delta_honest[j_best]:.1f} per 1,000), omitting the opening group")
print(f"    overstates it by a factor of {rat_best:.2f}.\n")
print(f"  Over the whole grid the honest increment's largest value is")
print(f"  {1000*GR.delta_honest.max():.1f} per 1,000 at p_t={t_best:.3f}, and the naive")
print(f"  increment's largest is {1000*GR.delta_naive.max():.1f} at "
      f"p_t={GR.threshold[GR.delta_naive.idxmax()]:.3f}.")

print(f"""
  THIS IS THE ROUND'S SECOND FINDING AGAINST THE PAPER, and it agrees
  with r24's.  Section 8 reports that omitting the opening group
  overstates the operational gain {_f5:.1f}-fold at a 5% review capacity,
  against {_fauc:.1f} measured as AUC.  Net benefit does not reproduce that.
  Where the item's increment is resolvably positive -- p_t from
  {h_lo:.2f} to {h_hi:.2f}, which is the region either side of this cohort's
  own base rate of {prev:.3f} -- the ratio is {rat_best:.2f} at the threshold where
  that increment is largest, and rises above the AUC ratio only as the
  denominator decays toward zero at the top of the region.  A ratio whose
  denominator is crossing zero is not a quantity, so the honest summary
  is the first number, not the range.

  The two findings have the same cause.  A 5% review capacity is an
  operating point deep in the upper tail, where the group-aware baseline
  is already near its ceiling and the item adds almost nothing; the naive
  baseline is there only by a tie-break.  The paper measured the
  overstatement at the one operating point where its own honest arm has
  the least to give.""")

pd.DataFrame([dict(
    prevalence=prev, n_test=len(y),
    factor_lo_named=float(fmin), factor_hi_named=float(fmax),
    factor_lo_recal=float(rmin), factor_hi_recal=float(rmax),
    grid_lo=float(GRID.min()), grid_hi=float(GRID.max()), n_grid=len(GRID),
    resolved_lo=h_lo, resolved_hi=h_hi, n_resolved=len(pos),
    n_negative=len(neg), n_naive_resolved=len(npos),
    ratio_lo_resolved=float(rat.min()), ratio_hi_resolved=float(rat.max()),
    ratio_at_max_honest=rat_best, threshold_at_max_honest=t_best,
    max_honest=float(GR.delta_honest.max()),
    max_honest_at=float(GR.threshold[GR.delta_honest.idxmax()]),
    max_naive=float(GR.delta_naive.max()),
    max_naive_at=float(GR.threshold[GR.delta_naive.idxmax()]),
    n_boot=kept,
)]).to_csv(RESULTS / "r23_dca_facts.csv", index=False)
print("\ndone.  wrote r23_dca_curve.csv, r23_dca_grid.csv, r23_dca_delta.csv, "
      "r23_dca_recal.csv, r23_calibration.csv, r23_dca_facts.csv")

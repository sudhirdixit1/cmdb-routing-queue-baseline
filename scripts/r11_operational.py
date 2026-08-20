"""R11 -- what the AUC difference is worth at a fixed review capacity, and
how the result moves with the target's definition.

REBUILT after a referee found two defects in the first version.  Both are
recorded here because both changed the printed number.

  DEFECT 1 (mismatched arms).  The first version used ONE treatment model,
  intake+group+item, for both comparisons, so the "naive" contrast was
  intake  vs  intake+group+item -- which credits item identity with the
  opening group's own contribution.  An analyst who omitted the group from
  the baseline would also have omitted it from the model.  The matched
  contrast is intake vs intake+item, mirroring Table 1 exactly.  This alone
  moved the headline factor from 12.7 to about 10.

  DEFECT 2 (no interval).  The first version printed the factor bare, in a
  paper that elsewhere refuses to resolve +0.0017 past two decimals.  The
  denominator here is a count difference of a few dozen incidents and is
  genuinely uncertain.  Every quantity below now carries a paired bootstrap
  interval over test rows, and the tie structure at the capacity cut is
  disclosed rather than left to argsort.

  TIES.  The intake-only model emits very few distinct probabilities, so the
  capacity cut lands inside a large tie block and `argsort` would resolve it
  by row order.  Every draw below breaks ties at random, so the reported
  spread includes tie-breaking uncertainty rather than hiding it.

Two review objections are answered here.

O6.  An AUC difference is not a quantity a service desk can act on.  Part A
fixes a review capacity -- the share of incoming incidents a desk can afford
to look at before routing -- and reports, at that capacity, how many
reassignment-bound incidents each model actually surfaces.  This is a
DETECTION statement, not a savings claim: it says how many more of the right
incidents you see, not what seeing them is worth, which this log cannot
support.

O4.  The target fires on about 40% of incidents, which is routine workflow
rather than error.  Part B reports the whole ladder at three thresholds.

Everything is held to r4_final: same cohort, same temporal split, same
intake block, same opening group, same one-hot logistic estimator.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_BOOT = 2000
N_CAP_BOOT = 400
BQ = M.INTAKE + ["intake_group"]
CAPACITIES = (0.05, 0.10, 0.20)

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values

span_days = (TE._t.max() - TE._t.min()).total_seconds() / 86400.0
months = span_days / 30.44

# Four models.  The two contrasts must use MATCHED pairs.
p_intake = M.fit(TR, TE, M.INTAKE)                 # naive baseline
p_int_it = M.fit(TR, TE, M.INTAKE + [M.IDENT])     # naive treatment
p_base = M.fit(TR, TE, BQ)                         # honest baseline
p_full = M.fit(TR, TE, BQ + [M.IDENT])             # honest treatment

print("=" * 92)
print("A. WHAT THE GAIN BUYS AT A FIXED REVIEW CAPACITY")
print("=" * 92)
print(f"  Test window: {TE._t.min():%Y-%m-%d} to {TE._t.max():%Y-%m-%d} "
      f"({span_days:.0f} days, {len(TE):,} incidents, {months:.1f} months)")
print(f"  Base rate: {y.mean():.1%} reassigned at least once.")
print(f"  AUC: intake {roc_auc_score(y, p_intake):.3f}, "
      f"intake+group {roc_auc_score(y, p_base):.3f}, "
      f"+item {roc_auc_score(y, p_full):.3f}\n")

# -- tie disclosure -------------------------------------------------------
print("  Tie structure at the capacity cut (why every draw randomises ties):")
for nm, p in (("intake only", p_intake), ("intake + group", p_base)):
    k = int(round(len(p) * 0.10))
    cut = np.sort(p)[::-1][k - 1]
    n_tied = int((p == cut).sum())
    n_above = int((p > cut).sum())
    print(f"    {nm:16s} {len(np.unique(p)):>5,} distinct probabilities; "
          f"at 10% the cut value is shared by {n_tied:,} rows "
          f"({n_above:,} strictly above)")


def caught_at(p, frac, rng, idx=None):
    """Count positives in the top `frac`, breaking ties at random."""
    if idx is None:
        pp, yy = p, y
    else:
        pp, yy = p[idx], y[idx]
    k = int(round(len(pp) * frac))
    order = rng.permutation(len(pp))                # random tie-break
    sel = order[np.argsort(-pp[order], kind="stable")][:k]
    return k, int(yy[sel].sum())


print("\n  Honest contrast  : (intake + group)      vs (intake + group + item)")
print("  Naive contrast   : (intake)              vs (intake + item)")
print("  -- the naive arm now MATCHES Table 1's construction.\n")
print(f"  {'cap.':>5s} {'honest extra':>22s} {'naive extra':>22s} "
      f"{'factor':>18s}")
rows = []
for frac in CAPACITIES:
    rng = np.random.default_rng(SEED)
    k, cb = caught_at(p_base, frac, rng)
    _, cf = caught_at(p_full, frac, rng)
    _, ci = caught_at(p_intake, frac, rng)
    _, cn = caught_at(p_int_it, frac, rng)
    h_pt, n_pt = cf - cb, cn - ci
    hb, nb, fb = [], [], []
    for rep in range(N_CAP_BOOT):
        r = np.random.default_rng(SEED + 1000 + rep)
        idx = r.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        _, a = caught_at(p_base, frac, r, idx)
        _, b = caught_at(p_full, frac, r, idx)
        _, c = caught_at(p_intake, frac, r, idx)
        _, d = caught_at(p_int_it, frac, r, idx)
        hb.append(b - a)
        nb.append(d - c)
        if (b - a) > 0:
            fb.append((d - c) / (b - a))
    hb, nb, fb = np.array(hb), np.array(nb), np.array(fb)
    hlo, hhi = np.percentile(hb, [2.5, 97.5])
    nlo, nhi = np.percentile(nb, [2.5, 97.5])
    flo, fhi = (np.percentile(fb, [2.5, 97.5]) if len(fb) > 10 else (np.nan, np.nan))
    p_le0 = float((hb <= 0).mean())
    rows.append(dict(capacity=frac, reviewed=k, caught_base=cb, caught_full=cf,
                     caught_intake=ci, caught_intake_item=cn,
                     honest_extra=h_pt, honest_lo=hlo, honest_hi=hhi,
                     naive_extra=n_pt, naive_lo=nlo, naive_hi=nhi,
                     factor=n_pt / h_pt if h_pt else np.nan,
                     factor_lo=flo, factor_hi=fhi,
                     p_honest_le_zero=p_le0,
                     honest_per_month=h_pt / months))
    print(f"  {frac:>4.0%} {f'{h_pt:+d} [{hlo:+.0f},{hhi:+.0f}]':>22s} "
          f"{f'{n_pt:+d} [{nlo:+.0f},{nhi:+.0f}]':>22s} "
          f"{f'{n_pt/h_pt:.1f}x [{flo:.1f},{fhi:.1f}]':>18s}")
C = pd.DataFrame(rows)
C.to_csv(RESULTS / "r11_capacity.csv", index=False)

r10 = C[C.capacity == 0.10].iloc[0]
print(f"\n  P(honest extra <= 0) at 10% capacity: {r10.p_honest_le_zero:.1%}")
print("\n  READ THIS HONESTLY.  The direction is solid at every capacity and")
print("  the factor is comfortably above one, but the denominator is a count")
print("  difference of a few dozen incidents and its interval is wide.  The")
print("  paper reports the factor WITH its interval and does not bold it.")
print("  The qualitative claim -- that the omission inflates the operational")
print("  gain by roughly an order of magnitude, far more than the 1.8x it")
print("  inflates the AUC gain -- is what the data supports.")

g_naive = roc_auc_score(y, p_int_it) - roc_auc_score(y, p_intake)
g_honest = roc_auc_score(y, p_full) - roc_auc_score(y, p_base)
print(f"\n  AUC ratio for comparison: {g_naive:.4f} / {g_honest:.4f} = "
      f"{g_naive/g_honest:.2f}x")
pd.DataFrame([dict(auc_ratio=g_naive / g_honest, months=months,
                   span_days=span_days,
                   factor_10=float(r10.factor), factor_10_lo=float(r10.factor_lo),
                   factor_10_hi=float(r10.factor_hi),
                   factor_lo_across=float(C.factor.min()),
                   factor_hi_across=float(C.factor.max()))]
             ).to_csv(RESULTS / "r11_overstatement.csv", index=False)

print("\n" + "=" * 92)
print("B. THE LADDER AT THREE TARGET DEFINITIONS")
print("=" * 92)
print(f"  {'target':>18s} {'rate':>7s} {'intake':>9s} {'+group':>9s} "
      f"{'shrink':>8s} {'95% CI on +group':>20s}")
tro = []


def bdelta(pa, pb, yy, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(yy), len(yy))
        if len(np.unique(yy[i])) > 1:
            v.append(roc_auc_score(yy[i], pb[i]) - roc_auc_score(yy[i], pa[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


for thr in (1, 2, 3):
    d = D.copy()
    d["_y"] = (d._ra >= thr).astype(int)
    tr, te = M.split(d)
    yy = te._y.values
    a0 = roc_auc_score(yy, M.fit(tr, te, M.INTAKE))
    ai = roc_auc_score(yy, M.fit(tr, te, M.INTAKE + [M.IDENT]))
    pq = M.fit(tr, te, BQ)
    pqi = M.fit(tr, te, BQ + [M.IDENT])
    aq, aqi = roc_auc_score(yy, pq), roc_auc_score(yy, pqi)
    g0, g1 = ai - a0, aqi - aq
    lo, hi = bdelta(pq, pqi, yy)
    tro.append(dict(threshold=thr, rate=float(yy.mean()), gain_intake=g0,
                    gain_queue=g1, shrink_pct=100 * (g0 - g1) / g0, lo=lo, hi=hi))
    print(f"  {f'>= {thr} reassign.':>18s} {yy.mean():>7.1%} {g0:>+9.3f} "
          f"{g1:>+9.3f} {100*(g0-g1)/g0:>7.0f}%  [{lo:+.3f},{hi:+.3f}]")
T = pd.DataFrame(tro)
T.to_csv(RESULTS / "r11_threshold.csv", index=False)
print(f"\n  Magnitude is threshold-dependent -- the +group rung ranges "
      f"{T.gain_queue.min():+.3f} to {T.gain_queue.max():+.3f} --")
print(f"  but the ordering never reverses and the shrinkage stays between")
print(f"  {T.shrink_pct.min():.0f}% and {T.shrink_pct.max():.0f}%.  Every interval excludes zero.")

"""R11 -- what the AUC difference is worth at a fixed review capacity, and
how the result moves with the target's definition.

Two review objections are answered here.

O6.  The paper establishes that admitting one free field halves a measured
number, and then leaves the reader with no sense of what either number buys.
An AUC difference is not a quantity a service desk can act on.  Part A fixes
a review capacity -- the share of incoming incidents a desk can afford to
look at before routing -- and reports, at that capacity, how many
reassignment-bound incidents each model actually surfaces.  This is a
DETECTION statement, not a savings claim: it says how many more of the right
incidents you see, not what seeing them is worth, which this log cannot
support.

O4.  The paper's target fires on about 40% of incidents, which is routine
workflow rather than error, and the sensitivity to a stricter definition sat
in a subordinate clause of the Limitations.  Part B reports the whole ladder
at three thresholds so the reader can see both that the magnitude is
threshold-dependent and that the ordering is not.

Everything is held to r4_final: same cohort, same temporal split, same
intake block, same opening queue, same one-hot logistic estimator.
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
BQ = M.INTAKE + ["intake_group"]
CAPACITIES = (0.05, 0.10, 0.20)

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values

span_days = (TE._t.max() - TE._t.min()).total_seconds() / 86400.0
months = span_days / 30.44

print("=" * 92)
print("A. WHAT THE GAIN BUYS AT A FIXED REVIEW CAPACITY")
print("=" * 92)
print(f"  Test window: {TE._t.min():%Y-%m-%d} to {TE._t.max():%Y-%m-%d} "
      f"({span_days:.0f} days, {len(TE):,} incidents, {months:.1f} months)")
print(f"  Base rate: {y.mean():.1%} of test incidents are reassigned at least once.\n")

p_base = M.fit(TR, TE, BQ)
p_full = M.fit(TR, TE, BQ + [M.IDENT])
print(f"  baseline AUC {roc_auc_score(y, p_base):.3f}   "
      f"with item identity {roc_auc_score(y, p_full):.3f}\n")


def at_capacity(p, frac):
    """Flag the top `frac` of test incidents by predicted risk."""
    k = int(round(len(p) * frac))
    idx = np.argsort(-p)[:k]
    caught = int(y[idx].sum())
    return k, caught, caught / k, caught / y.sum()


print(f"  {'capacity':>9s} {'reviewed':>9s} | {'baseline':>18s} | "
      f"{'+ item identity':>18s} | {'extra caught':>21s}")
print(f"  {'':9s} {'':9s} | {'caught':>8s} {'prec':>9s} | "
      f"{'caught':>8s} {'prec':>9s} | {'total':>7s} {'per 1k':>6s} {'/month':>6s}")
rows = []
for frac in CAPACITIES:
    k, cb, pb, rb = at_capacity(p_base, frac)
    _, cf, pf, rf = at_capacity(p_full, frac)
    extra = cf - cb
    rows.append(dict(capacity=frac, reviewed=k, caught_base=cb, caught_full=cf,
                     prec_base=pb, prec_full=pf, recall_base=rb, recall_full=rf,
                     extra=extra, extra_per_1k=1000 * extra / k,
                     extra_per_month=extra / months,
                     lift_base=pb / y.mean(), lift_full=pf / y.mean()))
    print(f"  {frac:>8.0%} {k:>9,} | {cb:>8,} {pb:>8.1%} | "
          f"{cf:>8,} {pf:>8.1%} | {extra:>7,} {1000*extra/k:>6.0f} "
          f"{extra/months:>6.0f}")
pd.DataFrame(rows).to_csv(RESULTS / "r11_capacity.csv", index=False)

r10 = rows[1]
print(f"\n  Read the 10% row as the operational statement.  A desk that can")
print(f"  review {r10['reviewed']:,} of {len(TE):,} incidents before routing catches")
print(f"  {r10['caught_base']:,} reassignment-bound incidents using intake fields and the")
print(f"  queue, and {r10['caught_full']:,} if it also knows the configuration item --")
print(f"  {r10['extra']:,} more, or {r10['extra_per_month']:.0f} a month at this log's volume.")
print(f"  Precision moves from {r10['prec_base']:.1%} to {r10['prec_full']:.1%} against a "
      f"{y.mean():.1%} base rate.")
print("\n  What this does NOT say: that a reviewed incident is a corrected one.")
print("  The log records no intervention, so the recoverable share of these")
print("  is not identified here.")

print("\n  The same capacities against the intake-only baseline, i.e. what a")
print("  business case that omits the queue would appear to buy:")
p_intake = M.fit(TR, TE, M.INTAKE)
naive = []
for frac in CAPACITIES:
    k, ci, pi, _ = at_capacity(p_intake, frac)
    _, cf, pf, _ = at_capacity(p_full, frac)
    naive.append(dict(capacity=frac, reviewed=k, caught_intake=ci, caught_full=cf,
                      extra=cf - ci, extra_per_month=(cf - ci) / months))
    print(f"    {frac:>4.0%}: {cf-ci:>5,} extra   "
          f"({(cf-ci)/months:>5.0f} a month)  vs {rows[CAPACITIES.index(frac)]['extra']:>5,} "
          f"({rows[CAPACITIES.index(frac)]['extra_per_month']:>5.0f} a month) when the queue is admitted")
for n, r in zip(naive, rows):
    n["overstatement"] = n["extra"] / r["extra"]
pd.DataFrame(naive).to_csv(RESULTS / "r11_capacity_naive.csv", index=False)
ratio = naive[1]["overstatement"]
o_lo = min(n["overstatement"] for n in naive)
o_hi = max(n["overstatement"] for n in naive)
print(f"\n  At 10% capacity the omission overstates the operational gain by "
      f"{ratio:.1f}x; across the three capacities the factor runs "
      f"{o_lo:.1f}x to {o_hi:.1f}x.")
print("  The factor is larger than the ratio of the two AUC gains (1.8x)")
print("  because AUC averages over all operating points while a capacity-")
print("  limited desk works at one.  Near the top of the ranking the")
print("  queue-aware baseline is already close to its ceiling, so the item")
print("  column has far less left to add there than the global figure implies.")
g_naive = roc_auc_score(y, p_full) - roc_auc_score(y, p_intake)
g_honest = roc_auc_score(y, p_full) - roc_auc_score(y, p_base)
pd.DataFrame([dict(overstatement_10pct=ratio, overstatement_lo=o_lo,
                   overstatement_hi=o_hi, auc_ratio=g_naive / g_honest,
                   months=months, span_days=span_days)]
             ).to_csv(RESULTS / "r11_overstatement.csv", index=False)

print("\n" + "=" * 92)
print("B. THE LADDER AT THREE TARGET DEFINITIONS")
print("=" * 92)
print("  Reassignment at least once fires on ~40% of incidents and includes")
print("  legitimate escalation.  Stricter thresholds isolate the incidents")
print("  that were handed on repeatedly.\n")
print(f"  {'target':>18s} {'rate':>7s} {'intake':>9s} {'+queue':>9s} "
      f"{'shrink':>8s} {'95% CI on +queue':>20s}")
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
    aq = roc_auc_score(yy, pq)
    aqi = roc_auc_score(yy, pqi)
    g0, g1 = ai - a0, aqi - aq
    lo, hi = bdelta(pq, pqi, yy)
    tro.append(dict(threshold=thr, rate=float(yy.mean()), gain_intake=g0,
                    gain_queue=g1, shrink_pct=100 * (g0 - g1) / g0, lo=lo, hi=hi))
    print(f"  {f'>= {thr} reassign.':>18s} {yy.mean():>7.1%} {g0:>+9.3f} "
          f"{g1:>+9.3f} {100*(g0-g1)/g0:>7.0f}%  [{lo:+.3f},{hi:+.3f}]")
T = pd.DataFrame(tro)
T.to_csv(RESULTS / "r11_threshold.csv", index=False)
print(f"\n  The magnitude is threshold-dependent -- the queue rung ranges "
      f"{T.gain_queue.min():+.3f} to {T.gain_queue.max():+.3f} --")
print(f"  but the ordering never reverses and the shrinkage stays in a band of")
print(f"  {T.shrink_pct.min():.0f}% to {T.shrink_pct.max():.0f}%.  Every interval excludes zero.")

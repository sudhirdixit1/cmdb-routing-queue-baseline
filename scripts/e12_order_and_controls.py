"""E12 -- adversarial checks on the central claim.

Three threats to "the service layer carries the capability, CI adds little":

A. ORDER.  Service was always entered before CI.  A coarse feature entered
   first can absorb the structure a finer nested feature would otherwise
   supply.  Test the reverse order and the marginal contribution of each
   layer given the other (Shapley-style, both orders).

B. GRANULARITY.  Maybe the service field wins because ~259 groups is simply
   the right resolution for this task, and any partition at that resolution
   would do.  Control: replace the real service field with a RANDOM
   partition of CIs into the same number of groups.  If a random partition
   at matched cardinality performs comparably, the finding is about
   resolution, not about services.

C. NESTING.  Service Component is a coarsening of CI.  Test whether CI
   alone, with no service field at all, reaches the same performance.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14

SEED = 20260819
N_BOOT = 2000
BASE = ["Category", "Impact", "Urgency", "Priority"]
SVC = ["Service Component WBS (aff)"]
CI = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)"]

df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
TR, TE = df.iloc[:cut].copy(), df.iloc[cut:].copy()
y = TE._y.values


def enc(train, test, cols):
    Xtr = np.empty((len(train), len(cols))); Xte = np.empty((len(test), len(cols)))
    for j, c in enumerate(cols):
        tr = train[c].astype(str).where(~is_missing(train[c]), "__M__")
        te = test[c].astype(str).where(~is_missing(test[c]), "__M__")
        cats = pd.Index(tr.value_counts().index)
        a = pd.Categorical(tr, categories=cats).codes.astype(float)
        b = pd.Categorical(te, categories=cats).codes.astype(float)
        a[a < 0] = np.nan; b[b < 0] = np.nan
        Xtr[:, j], Xte[:, j] = a, b
    return Xtr, Xte


def auc(cols, train=None, test=None):
    train = TR if train is None else train
    test = TE if test is None else test
    Xtr, Xte = enc(train, test, cols)
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, m.predict_proba(Xte)[:, 1])


print("=" * 86)
print("E12  ADVERSARIAL CHECKS ON THE CENTRAL CLAIM")
print("=" * 86)

a_base = auc(BASE)
a_svc = auc(BASE + SVC)
a_ci = auc(BASE + CI)
a_both = auc(BASE + SVC + CI)

print("\nA. ORDER OF ENTRY")
print(f"  base                      {a_base:.3f}")
print(f"  base + service            {a_svc:.3f}   (service first: {a_svc-a_base:+.3f})")
print(f"  base + CI                 {a_ci:.3f}   (CI first:      {a_ci-a_base:+.3f})")
print(f"  base + service + CI       {a_both:.3f}")
print()
print(f"  CI added AFTER service    {a_both - a_svc:+.3f}")
print(f"  service added AFTER CI    {a_both - a_ci:+.3f}")
sh_svc = 0.5 * ((a_svc - a_base) + (a_both - a_ci))
sh_ci = 0.5 * ((a_ci - a_base) + (a_both - a_svc))
print(f"\n  order-independent (Shapley) attribution:")
print(f"    service {sh_svc:+.3f}   CI {sh_ci:+.3f}   "
      f"(service share {sh_svc/(sh_svc+sh_ci):.0%})")

print("\nB. GRANULARITY CONTROL  (random partition at matched cardinality)")
n_grp = TR[SVC[0]].nunique()
print(f"  real service field has {n_grp} groups; building random partitions "
      f"of CI into {n_grp} groups")
cis = pd.Index(pd.concat([TR, TE])["CI Name (aff)"].astype(str).unique())
rand_aucs = []
for rep in range(5):
    rng = np.random.default_rng(SEED + rep)
    lut = pd.Series(rng.integers(0, n_grp, len(cis)).astype(str), index=cis)
    tr, te = TR.copy(), TE.copy()
    tr["_rand"] = tr["CI Name (aff)"].astype(str).map(lut).fillna("__M__")
    te["_rand"] = te["CI Name (aff)"].astype(str).map(lut).fillna("__M__")
    rand_aucs.append(auc(BASE + ["_rand"], tr, te))
print(f"  base + RANDOM partition   {np.mean(rand_aucs):.3f} "
      f"(sd {np.std(rand_aucs):.4f})")
print(f"  base + REAL service       {a_svc:.3f}")
print(f"  -> real service beats a matched-cardinality random grouping by "
      f"{a_svc - np.mean(rand_aucs):+.3f}")

print("\nC. NESTING  (does CI alone reach the service ceiling?)")
print(f"  base + CI only            {a_ci:.3f}")
print(f"  base + service only       {a_svc:.3f}")
print(f"  difference                {a_ci - a_svc:+.3f}")

rows = [dict(check="base", auc=a_base), dict(check="base+service", auc=a_svc),
        dict(check="base+CI", auc=a_ci), dict(check="base+service+CI", auc=a_both),
        dict(check="base+random_partition", auc=float(np.mean(rand_aucs))),
        dict(check="shapley_service", auc=sh_svc),
        dict(check="shapley_ci", auc=sh_ci)]
pd.DataFrame(rows).to_csv(RESULTS / "e12_order_controls.csv", index=False)

print("\n" + "=" * 86)
print("INTERPRETATION")
print("=" * 86)
if a_ci - a_base > 0.8 * (a_svc - a_base):
    print("  CI ALONE is nearly as good as service alone.  The original claim")
    print("  that 'CI adds little' is ORDER-DEPENDENT and must be restated as")
    print("  'the two layers are largely redundant', not 'CI does not matter'.")
else:
    print("  CI alone falls well short of service alone.  The claim survives.")

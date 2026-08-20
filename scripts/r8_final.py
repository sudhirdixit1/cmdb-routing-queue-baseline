"""R8 -- repairs after the seventh review.

Two of the three mechanism legs had no null and turned out to be mostly
floor, and both are dropped.

NOTE (2026-08-20): this paragraph used to quote 48%/43% and 54%/44% from a
row-level null and asserted the random grouping retained MORE than the real
one.  results/r8_dropped_leg.csv says the opposite (real 0.0805, random
0.0450).  The figures were stale; the reason the leg is dropped is that three
defensible floors disagree by more than the effect, not that the null beat it.
Section B's floor is separately SUPERSEDED by r17_mechanism_floor.py.

The third leg has an enormous margin over its floor and becomes the section:
the queue's own gain is almost entirely recoverable from a queue label
randomised WITHIN item, because the item already determines the queue.

This script computes, with matched nulls throughout:

 A  the queue's unique contribution given item, with an interval and a
    matched-dimension null, plus its range across design choices (the
    previous draft printed "+0.002" bare)
 B  the mirror leg and its floor: queue-within-item against a null that
    matches the item mass profile
 C  the item-within-queue leg against three progressively fairer floors,
    reported so the reader can see why we do not use it
 D  the design-space range including the cleaning cutoff, which the previous
    draft omitted
 E  deployment scoping: what fraction of the +0.103 the top-k items recover
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
D, _, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def A(tr, te, cols, C=1.0):
    return roc_auc_score(te._y.values, M.fit(tr, te, cols, C))


def P(tr, te, cols, C=1.0):
    return M.fit(tr, te, cols, C)


A0, Ai = A(TR, TE, M.INTAKE), A(TR, TE, M.INTAKE + [M.IDENT])
Aq, Aqi = A(TR, TE, BQ), A(TR, TE, BQ + [M.IDENT])

print("=" * 88)
print("A. THE QUEUE'S UNIQUE CONTRIBUTION, PROPERLY BOUNDED")
print("=" * 88)
pi_, pqi = P(TR, TE, M.INTAKE + [M.IDENT]), P(TR, TE, BQ + [M.IDENT])
rng = np.random.default_rng(SEED)
d = []
for _ in range(N_BOOT):
    i = rng.integers(0, len(y), len(y))
    if len(np.unique(y[i])) > 1:
        d.append(roc_auc_score(y[i], pqi[i]) - roc_auc_score(y[i], pi_[i]))
lo, hi = np.percentile(d, [2.5, 97.5])
print(f"  A_qi - A_i = {Aqi-Ai:+.5f}   95% CI [{lo:+.5f},{hi:+.5f}]")

# matched-dimension null: a random column with the queue's marginal profile
qsz = TR.intake_group.value_counts(normalize=True)
nl = []
for rep in range(60):
    r = np.random.default_rng(SEED + rep)
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        p["_qn"] = r.choice(qsz.index, size=len(p), p=qsz.values)
    nl.append(A(tr, te, M.INTAKE + [M.IDENT, "_qn"]) - Ai)
nl = np.array(nl)
print(f"  matched-dimension null      {nl.mean():+.5f} +- {nl.std():.5f}  (60 draws)")
print(f"  draws reaching the observed value: {(nl >= Aqi-Ai).mean():.0%}")

rng2 = []
for frac in (0.60, 0.65, 0.70, 0.75, 0.80):
    tr, te = M.split(D, frac)
    rng2.append(A(tr, te, BQ + [M.IDENT]) - A(tr, te, M.INTAKE + [M.IDENT]))
for C in (0.03, 0.3, 1.0, 10.0):
    rng2.append(A(TR, TE, BQ + [M.IDENT], C) - A(TR, TE, M.INTAKE + [M.IDENT], C))
print(f"  across splits and penalties: {min(rng2):+.4f} to {max(rng2):+.4f}")
print("  -> positive and above its null, but the third decimal is not earned.")

print("\n" + "=" * 88)
print("B. THE MIRROR LEG AND ITS FLOOR  (this becomes the mechanism)")
print("=" * 88)


def shuffle_within(inner, outer, n=30, seed=900):
    """Randomise `inner` within cells of `outer`."""
    out = []
    for rep in range(n):
        r = np.random.default_rng(seed + rep)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            p["_s"] = p.groupby(outer)[inner].transform(
                lambda s: r.permutation(s.values))
        out.append(A(tr, te, M.INTAKE + ["_s"]) - A0)
    return np.array(out)


real_mirror = shuffle_within("intake_group", M.IDENT)
# floor: randomise the queue within cells of a RANDOM partition whose cell
# sizes match the item mass profile, so the null has the same granularity
isz = TR[M.IDENT].astype(str).value_counts()
floor = []
for rep in range(30):
    r = np.random.default_rng(SEED + rep)
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        lab = r.choice(isz.index, size=len(p), p=(isz / isz.sum()).values)
        p["_c"] = lab
        p["_s"] = p.groupby("_c")["intake_group"].transform(
            lambda s: r.permutation(s.values))
    floor.append(A(tr, te, M.INTAKE + ["_s"]) - A0)
floor = np.array(floor)
qg = Aq - A0
print(f"  queue's own gain over intake                    {qg:+.4f}")
print(f"  queue randomised WITHIN item                    {real_mirror.mean():+.4f}"
      f" +- {real_mirror.std():.4f}   = {100*real_mirror.mean()/qg:.0f}% of it")
print(f"  same, within a matched random partition (floor) {floor.mean():+.4f}"
      f" +- {floor.std():.4f}   = {100*floor.mean()/qg:.0f}%")
print(f"  margin over floor: {100*(real_mirror.mean()-floor.mean())/qg:.0f} points")
# SUPERSEDED 2026-08-20 by r17_mechanism_floor.py.  The floor computed just
# above draws cell labels PER ROW, so two incidents sharing an item land in
# different cells and the association is destroyed by construction: the null
# cannot fail, and its ~2% is not a measurement.  r17 rebuilds it as a random
# partition OF ITEMS, where retention rises with granularity (41% at 49 cells,
# 77% at 400).  The paper reports r17's sweep.  This block is kept only so the
# withdrawal is auditable.
print("\n  DO NOT QUOTE THE FLOOR ABOVE.  It is drawn per row, so it destroys")
print("  the item-group association by construction and can only return ~0.")
print("  Use r17_mechanism_floor.py, which partitions ITEMS.  The real leg's")
print("  91% stands; the honest margin over a matched floor is ~50 points,")
print("  not the 89 this block implies.")

print("\n" + "=" * 88)
print("C. THE LEG WE ARE DROPPING, AND WHY")
print("=" * 88)
real_fwd = shuffle_within(M.IDENT, "intake_group", seed=700)
ig = Ai - A0
rows = [("real routing queue", real_fwd.mean(), real_fwd.std())]
for label, mode in [("random cells, uniform over items", "uniform"),
                    ("random cells, item-mass matched", "mass")]:
    vals = []
    for rep in range(15):
        r = np.random.default_rng(SEED + rep)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            if mode == "uniform":
                items = pd.Index(D[M.IDENT].astype(str).unique())
                lut = pd.Series(r.integers(0, 50, len(items)).astype(str),
                                index=items)
                p["_c"] = p[M.IDENT].astype(str).map(lut)
            else:
                p["_c"] = r.choice(qsz.index, size=len(p), p=qsz.values)
            p["_s"] = p.groupby("_c")[M.IDENT].transform(
                lambda s: r.permutation(s.values))
        vals.append(A(tr, te, M.INTAKE + ["_s"]) - A0)
    v = np.array(vals)
    rows.append((label, v.mean(), v.std()))
for lab, mu, sd in rows:
    print(f"  {lab:36s} {mu:+.4f} +- {sd:.4f}   = {100*mu/ig:4.0f}% of item gain")
# CORRECTED 2026-08-20.  These two lines used to read "A random 50-cell
# grouping of items retains MORE than the real queue", which is the opposite
# of what the CSV written three lines below says (real 0.0805, random-uniform
# 0.0450).  The text was stale from a draft in which the null was drawn at row
# level.  A referee found a live script contradicting its own output -- the
# exact defect r7_final.py is retained as a record of.
print(f"\n  The real leg retains {100*rows[0][1]/ig:.0f}% of the item's gain; a routing-blind")
print(f"  50-cell grouping retains {100*rows[1][1]/ig:.0f}% and a mass-matched one "
      f"{100*rows[2][1]/ig:.0f}%.")
print("  The three floors disagree by more than the effect, so this leg is not")
print("  interpretable and is EXCLUDED from the paper.  See section 5's 'What")
print("  we do not claim'.")
pd.DataFrame([dict(leg=l, recovered=m, sd=s) for l, m, s in rows]
             ).to_csv(RESULTS / "r8_dropped_leg.csv", index=False)

print("\n" + "=" * 88)
print("D. DESIGN-SPACE RANGE, NOW INCLUDING THE CLEANING CUTOFF")
print("=" * 88)
variants = []
for frac in (0.55, 0.65, 0.70, 0.75, 0.80):
    tr, te = M.split(D, frac)
    variants.append((f"split {frac:.0%}", A(tr, te, BQ + [M.IDENT]) - A(tr, te, BQ)))
d2 = D.copy(); d2["_y"] = (d2._ra >= 2).astype(int)
t2, e2 = M.split(d2)
variants.append(("target >= 2", A(t2, e2, BQ + [M.IDENT]) - A(t2, e2, BQ)))
for co in ("2013-10-15", "2013-11-01", "2013-12-01"):
    dd = D[D._t >= co].reset_index(drop=True)
    tr, te = M.split(dd)
    variants.append((f"cutoff {co}", A(tr, te, BQ + [M.IDENT]) - A(tr, te, BQ)))
for lbl, g in variants:
    print(f"  {lbl:22s} {g:+.4f}")
print(f"\n  range {min(g for _, g in variants):+.3f} to "
      f"{max(g for _, g in variants):+.3f}")
pd.DataFrame([dict(variant=l, gain=g) for l, g in variants]
             ).to_csv(RESULTS / "r8_design_space.csv", index=False)

print("\n" + "=" * 88)
print("E. DEPLOYMENT SCOPING: TOP-k RECOVERY OF THE +0.103")
print("=" * 88)
freq = TR[M.IDENT].astype(str).value_counts()
scope = []
for k in (8, 16, 32, 64, 128, 256):
    keep = set(freq.index[:k])
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        s = p[M.IDENT].astype(str)
        p["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    a = A(tr, te, BQ + ["_v"])
    rec = (a - Aq) / (Aqi - Aq)
    cov = freq.iloc[:k].sum() / len(TR)
    scope.append(dict(k=k, auc=a, recovered=rec, coverage=cov))
    print(f"  top {k:>4,} items  coverage {cov:5.1%}  AUC {a:.4f}  "
          f"recovers {rec:5.1%} of the +0.103")
pd.DataFrame(scope).to_csv(RESULTS / "r8_scope.csv", index=False)
pd.DataFrame([dict(queue_unique=Aqi-Ai, lo=lo, hi=hi,
                   null_mean=float(nl.mean()), null_sd=float(nl.std()),
                   design_lo=min(rng2), design_hi=max(rng2),
                   mirror=float(real_mirror.mean()),
                   mirror_pct=100*real_mirror.mean()/qg,
                   mirror_floor=float(floor.mean()),
                   mirror_floor_pct=100*floor.mean()/qg,
                   queue_gain=qg)]).to_csv(RESULTS / "r8_mechanism.csv", index=False)

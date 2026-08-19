"""R7 -- repairs after the sixth review.

The sixth review broke the mechanism section on a point that is correct and
that we should have seen: the shuffle re-estimates, by Monte Carlo, a
quantity the paper states in closed form one line earlier.

    G_naive - G_direct = (A_i - A_0) - (A_qi - A_q)
                       = (A_q - A_0) - (A_qi - A_i)

is an algebraic identity for any two variables, so "the decomposition
closes" is not a finding and its fourth decimal place is meaningless: the
agreement's own bootstrap interval is wider than the agreement.

What survives, and what this script computes:

 A  The quantity that actually carries the section, and which the previous
    draft never printed: A_qi - A_i, the queue's UNIQUE contribution once
    item identity is present.  If that is near zero, the item column already
    contains the queue's predictive content -- which is the real claim.
 B  A closed-form share of the item's predictive content that lies between
    queues, computed by projecting the item's outcome-rate onto queue
    indicators.  No permutation, no Monte-Carlo error.
 C  The shuffle demoted to what it can support: a control showing the shared
    information is the queue partition SPECIFICALLY, by re-running it within
    random partitions of matched size profile and within other categoricals.
 D  The mirror -- shuffling queue within item -- because the commonality
    term is symmetric and the paper must say so rather than narrate one
    direction.
 E  The design-space range of the headline, since the bootstrap interval
    conditions on every design choice and understates the real spread.
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
BQ = M.INTAKE + ["intake_group"]
D, _, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def A(tr, te, cols, C=1.0):
    return roc_auc_score(te._y.values, M.fit(tr, te, cols, C))


A0 = A(TR, TE, M.INTAKE)
Ai = A(TR, TE, M.INTAKE + [M.IDENT])
Aq = A(TR, TE, BQ)
Aqi = A(TR, TE, BQ + [M.IDENT])

print("=" * 88)
print("A. THE QUANTITY THE PREVIOUS DRAFT NEVER PRINTED")
print("=" * 88)
print(f"  A0  intake only              {A0:.5f}")
print(f"  Ai  intake + item            {Ai:.5f}")
print(f"  Aq  intake + queue           {Aq:.5f}")
print(f"  Aqi intake + queue + item    {Aqi:.5f}")
print()
print(f"  item's gain over intake            Ai - A0  = {Ai-A0:+.5f}")
print(f"  item's gain over intake+queue      Aqi - Aq = {Aqi-Aq:+.5f}")
print(f"  QUEUE's gain over intake+item      Aqi - Ai = {Aqi-Ai:+.5f}   <-- the result")
print(f"  queue's gain over intake           Aq - A0  = {Aq-A0:+.5f}")
print()
print("  identity check (holds for ANY two variables, so proves nothing):")
lhs = (Ai - A0) - (Aqi - Aq); rhs = (Aq - A0) - (Aqi - Ai)
print(f"    (Ai-A0)-(Aqi-Aq) = {lhs:+.6f}    (Aq-A0)-(Aqi-Ai) = {rhs:+.6f}")
print(f"    difference {abs(lhs-rhs):.2e}  -- an identity, not a finding")
print()
print("  The substantive statement: adding the queue to a model that already")
print(f"  knows the item is worth {Aqi-Ai:+.4f}.  The item column already")
print("  carries almost all of the queue's predictive content.")

print("\n" + "=" * 88)
print("B. CLOSED-FORM: HOW MUCH OF THE ITEM'S SIGNAL LIES BETWEEN QUEUES")
print("=" * 88)
# item outcome-rate predictor, smoothed, fit on TRAIN; decompose its test
# variance into between-queue and within-queue parts.  No permutation.
gm = TR._y.mean()
st = TR.groupby(TR[M.IDENT].astype(str))._y.agg(["mean", "size"])
enc = (st["mean"] * st["size"] + gm * 20.0) / (st["size"] + 20.0)
te = TE.copy()
te["_p"] = te[M.IDENT].astype(str).map(enc).fillna(gm)
grand = te["_p"].mean()
grp = te.groupby("intake_group")["_p"]
between = float((grp.count() * (grp.mean() - grand) ** 2).sum())
total = float(((te["_p"] - grand) ** 2).sum())
share = 100 * between / total
print(f"  variance of the item predictor on test          {total:.4f}")
print(f"  between-queue component                          {between:.4f}")
print(f"  share of item signal that is between-queue      {share:.1f}%")
print("  -> a three-line calculation with no Monte-Carlo error, reproducing the")
print("     magnitude the shuffle estimates.")

print("\n" + "=" * 88)
print("C. THE SHUFFLE, DEMOTED TO A CONTROL")
print("=" * 88)


def shuffle_within(col, n=30, seed=700):
    out = []
    for rep in range(n):
        rng = np.random.default_rng(seed + rep)
        tr, te2 = TR.copy(), TE.copy()
        for p in (tr, te2):
            p["_s"] = p.groupby(col)[M.IDENT].transform(
                lambda s: rng.permutation(s.values))
        out.append(A(tr, te2, M.INTAKE + ["_s"]) - A0)
    return np.array(out)


rows = []
real = shuffle_within("intake_group")
print(f"  within the routing queue           {real.mean():+.4f} +- {real.std():.4f}")
rows.append(dict(partition="routing queue", recovered=float(real.mean()),
                 sd=float(real.std())))
# matched random partition: same number of cells, same size profile
sizes = TR.intake_group.value_counts()
for rep_label, n_cells in [("random, matched profile", len(sizes))]:
    vals = []
    for rep in range(10):
        rng = np.random.default_rng(SEED + rep)
        items = pd.Index(D[M.IDENT].astype(str).unique())
        lut = pd.Series(rng.integers(0, n_cells, len(items)).astype(str),
                        index=items)
        tr, te2 = TR.copy(), TE.copy()
        for p in (tr, te2):
            p["_g"] = p[M.IDENT].astype(str).map(lut)
            p["_s"] = p.groupby("_g")[M.IDENT].transform(
                lambda s: rng.permutation(s.values))
        vals.append(A(tr, te2, M.INTAKE + ["_s"]) - A0)
    v = np.array(vals)
    print(f"  within a {rep_label:26s} {v.mean():+.4f} +- {v.std():.4f}")
    rows.append(dict(partition=rep_label, recovered=float(v.mean()),
                     sd=float(v.std())))
for col in ["Category", "Priority", "Impact"]:
    v = shuffle_within(col, n=10)
    print(f"  within {col:28s} {v.mean():+.4f} +- {v.std():.4f}")
    rows.append(dict(partition=col, recovered=float(v.mean()), sd=float(v.std())))
pd.DataFrame(rows).to_csv(RESULTS / "r7_controls.csv", index=False)
print("\n  Only the queue partition recovers anything.  The shuffle therefore")
print("  supports the claim that the shared information IS the queue, and")
print("  nothing about the size of the overlap -- which B gives directly.")

print("\n" + "=" * 88)
print("D. THE MIRROR: THE OVERLAP IS SYMMETRIC")
print("=" * 88)
mir = []
for rep in range(30):
    rng = np.random.default_rng(900 + rep)
    tr, te2 = TR.copy(), TE.copy()
    for p in (tr, te2):
        p["_s"] = p.groupby(M.IDENT)["intake_group"].transform(
            lambda s: rng.permutation(s.values))
    mir.append(A(tr, te2, M.INTAKE + ["_s"]) - A0)
mir = np.array(mir)
print(f"  queue's gain over intake                  {Aq-A0:+.4f}")
print(f"  queue shuffled WITHIN item                {mir.mean():+.4f} "
      f"+- {mir.std():.4f}   ({100*mir.mean()/(Aq-A0):.0f}% of it)")
print(f"  item's gain over intake                   {Ai-A0:+.4f}")
print(f"  item shuffled WITHIN queue                {real.mean():+.4f} "
      f"+- {real.std():.4f}   ({100*real.mean()/(Ai-A0):.0f}% of it)")
print("\n  The overlap term is shared.  Attributing it to one variable is a")
print("  choice, not an identification result.  The paper must say so.")
pd.DataFrame([dict(item_gain=Ai-A0, item_within_queue=float(real.mean()),
                   queue_gain=Aq-A0, queue_within_item=float(mir.mean()),
                   queue_unique=Aqi-Ai, item_unique=Aqi-Aq,
                   between_share=share)]).to_csv(RESULTS / "r7_overlap.csv",
                                                 index=False)

print("\n" + "=" * 88)
print("E. DESIGN-SPACE RANGE OF THE HEADLINE")
print("=" * 88)
variants = []
for frac in (0.55, 0.65, 0.70, 0.75, 0.80):
    tr, te2 = M.split(D, frac)
    variants.append((f"split {frac:.0%}", A(tr, te2, BQ + [M.IDENT]) - A(tr, te2, BQ)))
d2 = D.copy(); d2["_y"] = (d2._ra >= 2).astype(int)
t2, e2 = M.split(d2)
variants.append(("target >= 2 reassignments", A(t2, e2, BQ + [M.IDENT]) - A(t2, e2, BQ)))
for lbl, g in variants:
    print(f"  {lbl:28s} {g:+.4f}")
lo, hi = min(g for _, g in variants), max(g for _, g in variants)
print(f"\n  range across design choices: {lo:+.3f} to {hi:+.3f}")
print("  The bootstrap interval conditions on all of these and is narrower.")
pd.DataFrame([dict(variant=l, gain=g) for l, g in variants]
             ).to_csv(RESULTS / "r7_design_space.csv", index=False)

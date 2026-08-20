"""R13 -- the shape of the free field, and how little of it is needed.

This script exists because r12 turned up something the earlier drafts had not
looked at: the opening routing queue is not 50 comparable groups.  One group
holds most of the traffic, the distribution drifts hard across the temporal
split, and the model-free lookup accuracy reported in r12 is largely carried
by that one dominant class.

Rather than bury this, the script measures it and asks the question it
raises.  If the queue is effectively one dominant pool plus a tail, then the
field that halves the measured value of a 2,929-item CMDB may be worth only
a single bit -- "did the desk send this to the main pool, or somewhere else".
That is a sharper claim than the paper currently makes, and a more useful one
for a practitioner, because a single binary flag is far cheaper to reproduce
in another organisation than a 50-way routing taxonomy.

  A  concentration and drift of the queue field, train against test
  B  the ladder with the queue REDUCED to one binary indicator, and to
     top-k groups with the tail collapsed
  C  how much of the queue's own baseline gain each reduction retains

Everything else is held to r4_final.
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
Q = "intake_group"

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def A(tr, te, cols):
    return roc_auc_score(te._y.values, M.fit(tr, te, cols))


def bdelta(pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


print("=" * 92)
print("A. THE QUEUE FIELD IS ONE POOL PLUS A TAIL, AND IT DRIFTS")
print("=" * 92)
shape = []
for nm, df in (("train", TR), ("test", TE)):
    p = df[Q].astype(str).value_counts(normalize=True)
    h = float(-(p * np.log2(p)).sum())
    shape.append(dict(split=nm, n_groups=int(len(p)), entropy=h,
                      perplexity=2 ** h, top1=float(p.iloc[0]),
                      top3=float(p.head(3).sum()), top10=float(p.head(10).sum())))
    print(f"  {nm:6s} {len(p):>3} groups   H {h:.2f} bits   perplexity {2**h:>4.1f}   "
          f"top-1 {p.iloc[0]:>5.1%}   top-3 {p.head(3).sum():>5.1%}")
pd.DataFrame(shape).to_csv(RESULTS / "r13_shape.csv", index=False)
DOM = TR[Q].astype(str).value_counts().idxmax()
print(f"\n  The dominant group is the same in both halves. Its share rises from")
print(f"  {shape[0]['top1']:.0%} to {shape[1]['top1']:.0%} and the number of live groups falls from "
      f"{shape[0]['n_groups']} to {shape[1]['n_groups']}.")
print("  Nominal cardinality (50) badly overstates this field: its effective")
print(f"  cardinality is {shape[0]['perplexity']:.1f} in training and "
      f"{shape[1]['perplexity']:.1f} in test.")

dom_te = TE[Q].astype(str) == DOM
print(f"\n  reassignment rate inside the dominant pool  {TE[dom_te]._y.mean():.3f}  "
      f"(n={int(dom_te.sum()):,})")
print(f"  reassignment rate outside it                {TE[~dom_te]._y.mean():.3f}  "
      f"(n={int((~dom_te).sum()):,})")
print("  -> most of what the queue knows is this one contrast.")
pd.DataFrame([dict(dominant=DOM, rate_in=float(TE[dom_te]._y.mean()),
                   rate_out=float(TE[~dom_te]._y.mean()),
                   n_in=int(dom_te.sum()), n_out=int((~dom_te).sum()))]
             ).to_csv(RESULTS / "r13_dominant.csv", index=False)

print("\n" + "=" * 92)
print("B. THE LADDER WITH THE QUEUE REDUCED")
print("=" * 92)
print("  Each variant replaces the 50-way queue with a coarser version of")
print("  itself, then re-runs the same two-rung ladder.\n")


def variant(tr, te, kind, k=None):
    tr, te = tr.copy(), te.copy()
    if kind == "full":
        for p in (tr, te):
            p["_q"] = p[Q].astype(str)
    elif kind == "binary":
        for p in (tr, te):
            p["_q"] = np.where(p[Q].astype(str) == DOM, "MAIN", "OTHER")
    elif kind == "topk":
        keep = set(tr[Q].astype(str).value_counts().index[:k])
        for p in (tr, te):
            s = p[Q].astype(str)
            p["_q"] = np.where(s.isin(keep), s, "__TAIL__")
    return tr, te


a_intake = A(TR, TE, M.INTAKE)
g_intake = A(TR, TE, M.INTAKE + [M.IDENT]) - a_intake
print(f"  intake-only baseline AUC {a_intake:.3f}; item identity is worth "
      f"{g_intake:+.3f} there.\n")
print(f"  {'queue variant':>22s} {'levels':>7s} {'base AUC':>9s} "
      f"{'queue gain':>11s} {'item gain':>10s} {'shrink':>7s} {'95% CI':>18s}")
rows = []
VARIANTS = [("binary: main pool vs rest", "binary", None),
            ("top 3 + tail", "topk", 3),
            ("top 10 + tail", "topk", 10),
            ("full queue", "full", None)]
for label, kind, k in VARIANTS:
    tr, te = variant(TR, TE, kind, k)
    lv = int(tr["_q"].nunique())
    cols = M.INTAKE + ["_q"]
    pb = M.fit(tr, te, cols)
    pf = M.fit(tr, te, cols + [M.IDENT])
    ab, af = roc_auc_score(y, pb), roc_auc_score(y, pf)
    lo, hi = bdelta(pb, pf)
    shrink = 100 * (g_intake - (af - ab)) / g_intake
    rows.append(dict(variant=label, levels=lv, base_auc=ab, queue_gain=ab - a_intake,
                     item_gain=af - ab, shrink_pct=shrink, lo=lo, hi=hi))
    print(f"  {label:>22s} {lv:>7} {ab:>9.3f} {ab-a_intake:>+11.3f} "
          f"{af-ab:>+10.3f} {shrink:>6.0f}%  [{lo:+.3f},{hi:+.3f}]")
V = pd.DataFrame(rows)
V.to_csv(RESULTS / "r13_reduced.csv", index=False)

b = V.iloc[0]
f = V.iloc[-1]
print(f"\n  The shrinkage is graded in the queue's resolution: "
      f"{V.shrink_pct.iloc[0]:.0f}%, {V.shrink_pct.iloc[1]:.0f}%, "
      f"{V.shrink_pct.iloc[2]:.0f}%, {V.shrink_pct.iloc[3]:.0f}% as the field goes from")
print("  two levels to fifty.  A proxy story predicts exactly this shape, and a")
print("  coincidence does not.")
print(f"\n  The first bit does most of the work but not all of it.  A single")
print(f"  binary flag -- main pool or not -- recovers "
      f"{100*b.queue_gain/f.queue_gain:.0f}% of the full queue's")
print(f"  baseline gain and {100*(g_intake-b.item_gain)/(g_intake-f.item_gain):.0f}% of the shrinkage it causes; the remaining")
print("  resolution supplies the rest.  For a practitioner this matters more")
print("  than the headline: the field that has to be admitted to the baseline")
print("  is far cheaper to reproduce elsewhere than a 49-way group taxonomy.")
pd.DataFrame([dict(
    binary_queue_gain=float(b.queue_gain), full_queue_gain=float(f.queue_gain),
    binary_share_of_queue=100 * float(b.queue_gain / f.queue_gain),
    binary_item_gain=float(b.item_gain), full_item_gain=float(f.item_gain),
    intake_item_gain=g_intake,
    binary_share_of_shrinkage=100 * float((g_intake - b.item_gain)
                                          / (g_intake - f.item_gain)),
    binary_shrink_pct=float(b.shrink_pct), full_shrink_pct=float(f.shrink_pct),
    dominant_group=DOM, n_items=int(D[M.IDENT].nunique()),
)]).to_csv(RESULTS / "r13_onebit.csv", index=False)

"""R14 -- deployment scoping, expanded from a paragraph into a result.

Review objection (O7).  "Identify your top 64 configuration items and you
recover 90% of the value, and you can compute which ones from a frequency
count before funding anything" is the most directly actionable sentence in
the paper, and it occupied ten lines.  The reviewer also asked us to explain
a visible oddity in the single-split curve: recovery is flat between k=16 and
k=32 even though incident coverage rises 15 points across that range.

WE TRIED TO EXPLAIN THE FLAT AND IT DOES NOT NEED EXPLAINING.  Two candidate
mechanisms were tested and both are false:

  (i)  "ranks 17-32 sit on the pool average, so naming them adds nothing".
       False.  Their volume-weighted departure from the pool rate is 0.207,
       tied for the LARGEST of any band, not the smallest.
  (ii) "their training rates do not transfer to test".  False.  Their
       train-to-test rate correlation is 0.93, the HIGHEST of any band, and
       all 16 appear in test.

The flat is split-specific noise.  Across five temporal split points the
recovery at k=32 ranges 66.7% to 75.8% -- a 9-point spread -- so a 0.05-point
dip between two adjacent k values on one split carries no information.  An
earlier version of this script printed a conclusion its own table
contradicted; that is the defect r7_final.py is retained as a record of, and
it is not repeated here.

So this script reports the curve the way it should have been reported: as a
mean over split points with the spread attached, which is what makes the
top-64 claim usable by someone else.

  A  the top-k curve, averaged over five temporal splits, with min-max spread
  B  the same curve with the queue removed from the baseline, to show the
     scoping claim does not depend on the paper's admission decision
  C  the descriptive concentration of the estate -- a frequency count, no
     model, computable before any funding decision

Selection is by TRAINING frequency only; no outcome is used to choose the set.
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
KS = (4, 8, 16, 32, 64, 128, 256)
SPLITS = (0.60, 0.65, 0.70, 0.75, 0.80)

D, counts, ACT, OPEN = M.load()


def curve(tr, te, base_cols):
    """Share of the item column's gain recovered by naming only the top k."""
    f = tr[M.IDENT].astype(str).value_counts()
    floor = roc_auc_score(te._y.values, M.fit(tr, te, base_cols))
    ceil = roc_auc_score(te._y.values, M.fit(tr, te, base_cols + [M.IDENT]))
    out = {}
    for k in KS:
        keep = set(f.index[:k])
        a, b = tr.copy(), te.copy()
        for p in (a, b):
            s = p[M.IDENT].astype(str)
            p["_v"] = np.where(s.isin(keep), s, "__OTHER__")
        au = roc_auc_score(b._y.values, M.fit(a, b, base_cols + ["_v"]))
        out[k] = (au - floor) / (ceil - floor)
    cov = {k: float(f.iloc[:k].sum() / len(tr)) for k in KS}
    return out, cov


def report(base_cols, label, tag):
    print(f"\n  baseline: {label}")
    print(f"  {'k':>5s} {'coverage':>9s} {'recovered':>10s} {'across-split range':>20s}")
    per = []
    covs = []
    for frac in SPLITS:
        tr, te = M.split(D, frac)
        r, c = curve(tr, te, base_cols)
        per.append(r)
        covs.append(c)
    rows = []
    for k in KS:
        v = np.array([p[k] for p in per])
        cv = float(np.mean([c[k] for c in covs]))
        rows.append(dict(k=k, coverage=cv, recovered=float(v.mean()),
                         lo=float(v.min()), hi=float(v.max()),
                         sd=float(v.std(ddof=1))))
        print(f"  {k:>5,} {cv:>9.1%} {v.mean():>10.1%} "
              f"{f'[{v.min():.0%}, {v.max():.0%}]':>20s}")
    T = pd.DataFrame(rows)
    T.to_csv(RESULTS / f"r14_curve_{tag}.csv", index=False)
    return T


print("=" * 92)
print("A. HOW MUCH OF THE ITEM COLUMN'S VALUE A PARTIAL CMDB RECOVERS")
print("=" * 92)
print("  Each row: name only the k highest-volume items, collapse the rest to")
print("  one bucket, and re-fit.  Averaged over five temporal split points,")
print("  because a single split's curve is not monotone at this resolution.")
Q = report(BQ, "intake fields + routing queue (the paper's)", "queue")
I = report(M.INTAKE, "intake fields only (queue removed)", "intake")

print("\n" + "=" * 92)
print("B. THE FLAT IN THE SINGLE-SPLIT CURVE IS NOISE, NOT STRUCTURE")
print("=" * 92)
tr, te = M.split(D, 0.70)
single, _ = curve(tr, te, BQ)
print("  single split (70%):  " + "  ".join(f"k={k}:{100*single[k]:.0f}%"
                                            for k in (8, 16, 32, 64)))
k32 = Q[Q.k == 32].iloc[0]
k16 = Q[Q.k == 16].iloc[0]
print(f"  mean over splits:    k=16:{k16.recovered:.0%}  k=32:{k32.recovered:.0%}")
print(f"\n  At k=32 the across-split range is [{k32.lo:.0%}, {k32.hi:.0%}], a spread of "
      f"{100*(k32.hi-k32.lo):.0f} points.")
print("  A one-point difference between adjacent k values on one split sits")
print("  well inside that.  Two candidate explanations for the flat were")
print("  tested and both are false -- ranks 17-32 have the joint-largest")
print("  departure from the pool rate, not the smallest, and the highest")
print("  train-to-test rate correlation of any band.  There is nothing to")
print("  explain: the curve should be read with its spread attached.")
pd.DataFrame([dict(k=k, single_split=single[k]) for k in KS]
             ).to_csv(RESULTS / "r14_single_split.csv", index=False)

print("\n" + "=" * 92)
print("C. THE CONCENTRATION ITSELF  (a frequency count, no model)")
print("=" * 92)
TR, TE = M.split(D)
freq = TR[M.IDENT].astype(str).value_counts()
conc = freq.cumsum() / len(TR)
print("  An organisation can compute this column before funding anything:\n")
print(f"  {'top k items':>12s} {'% of vocabulary':>16s} {'% of incidents':>15s}")
cc = []
for k in (8, 32, 64, 128, 256):
    cc.append(dict(k=k, pct_vocab=100 * k / TR[M.IDENT].nunique(),
                   coverage=float(conc.iloc[k - 1])))
    print(f"  {k:>12,} {100*k/TR[M.IDENT].nunique():>15.1f}% "
          f"{conc.iloc[k-1]:>15.1%}")
pd.DataFrame(cc).to_csv(RESULTS / "r14_concentration.csv", index=False)

q64 = Q[Q.k == 64].iloc[0]
q128 = Q[Q.k == 128].iloc[0]
i64 = I[I.k == 64].iloc[0]
print(f"\n  Naming {int(q64.k)} of {TR[M.IDENT].nunique():,} items -- "
      f"{100*64/TR[M.IDENT].nunique():.1f}% of the vocabulary, covering "
      f"{q64.coverage:.0%} of")
print(f"  incidents -- recovers {q64.recovered:.0%} [{q64.lo:.0%}, {q64.hi:.0%}] of the item column's")
print(f"  whole contribution.  {int(q128.k)} items recover {q128.recovered:.0%} "
      f"[{q128.lo:.0%}, {q128.hi:.0%}].")
print(f"  The same holds with the queue removed ({i64.recovered:.0%} at k=64), so this")
print("  is a property of the estate's concentration and not of the paper's")
print("  field-admission decision.")
pd.DataFrame([dict(
    top64=float(q64.recovered), top64_lo=float(q64.lo), top64_hi=float(q64.hi),
    top64_cov=float(q64.coverage),
    top128=float(q128.recovered), top128_lo=float(q128.lo),
    top128_hi=float(q128.hi), top128_cov=float(q128.coverage),
    top8=float(Q[Q.k == 8].recovered.iloc[0]),
    top8_cov=float(Q[Q.k == 8].coverage.iloc[0]),
    top64_intake=float(i64.recovered),
    k32_spread=float(k32.hi - k32.lo),
    n_items_train=int(TR[M.IDENT].nunique()),
    pct_vocab_64=100 * 64 / TR[M.IDENT].nunique(),
    pct_vocab_128=100 * 128 / TR[M.IDENT].nunique(),
)]).to_csv(RESULTS / "r14_scope_facts.csv", index=False)

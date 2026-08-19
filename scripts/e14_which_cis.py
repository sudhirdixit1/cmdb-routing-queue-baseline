"""E14 -- if you can only maintain k configuration items, which k?

Two objections to E13's random partitions:

1.  Real CMDB population is not random.  Organisations populate the assets
    they care about, typically the high-volume ones.  A random-ablation
    curve may therefore misstate what a partially populated CMDB achieves.
2.  E13 answers "how many groups", not "which ones" -- and the second is
    the question a practitioner actually faces.

This compares three strategies for spending a fixed budget of k identified
components, holding everything else constant:

  top-k       identify the k highest-volume CIs, everything else "other"
  random-k    identify k CIs drawn uniformly, everything else "other"
  partition-k partition ALL CIs into k random groups (E13's construction)

top-k and random-k model a partially populated CMDB.  partition-k models a
fully populated but coarsely classified one.  The gap between them is the
value of coverage versus the value of resolution.
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
N_REP = 5
KS = [8, 16, 32, 64, 128, 256, 512, 1024]
BASE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"

df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
TR, TE = df.iloc[:cut].copy(), df.iloc[cut:].copy()


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


def auc(train, test, cols):
    Xtr, Xte = enc(train, test, cols)
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, m.predict_proba(Xte)[:, 1])


base_auc = auc(TR, TE, BASE)
full_auc = auc(TR, TE, BASE + [IDENT])
# volume ranking computed on TRAIN only -- a real programme cannot see the future
freq = TR[IDENT].astype(str).value_counts()
all_cis = pd.Index(pd.concat([TR, TE])[IDENT].astype(str).unique())

print("=" * 88)
print("E14  WHICH CONFIGURATION ITEMS ARE WORTH IDENTIFYING?  (Rabobank)")
print("=" * 88)
print(f"  base, no component identity      AUC {base_auc:.3f}")
print(f"  full CI identity ({len(all_cis):,} CIs)     AUC {full_auc:.3f}\n")
print(f"  {'k':>6s} {'top-k':>18s} {'random-k':>18s} {'partition-k':>18s}")

rows = []
for k in KS:
    # top-k by training volume
    keep = set(freq.index[:k])
    tr, te = TR.copy(), TE.copy()
    for part in (tr, te):
        s = part[IDENT].astype(str)
        part["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    a_top = auc(tr, te, BASE + ["_v"])

    a_rand, a_part = [], []
    for rep in range(N_REP):
        rng = np.random.default_rng(SEED + rep)
        pick = set(rng.choice(all_cis, size=min(k, len(all_cis)), replace=False))
        tr, te = TR.copy(), TE.copy()
        for part in (tr, te):
            s = part[IDENT].astype(str)
            part["_v"] = np.where(s.isin(pick), s, "__OTHER__")
        a_rand.append(auc(tr, te, BASE + ["_v"]))

        lut = pd.Series(rng.integers(0, k, len(all_cis)).astype(str), index=all_cis)
        tr, te = TR.copy(), TE.copy()
        for part in (tr, te):
            part["_v"] = part[IDENT].astype(str).map(lut).fillna("__M__")
        a_part.append(auc(tr, te, BASE + ["_v"]))

    rows.append(dict(k=k, top_k=a_top, random_k=float(np.mean(a_rand)),
                     random_k_sd=float(np.std(a_rand)),
                     partition_k=float(np.mean(a_part)),
                     partition_k_sd=float(np.std(a_part)),
                     base=base_auc, full=full_auc))
    print(f"  {k:>6,} {a_top:>18.3f} {np.mean(a_rand):>13.3f}"
          f" (sd{np.std(a_rand):.3f}) {np.mean(a_part):>13.3f}"
          f" (sd{np.std(a_part):.3f})")

out = pd.DataFrame(rows)
out.to_csv(RESULTS / "e14_which_cis.csv", index=False)

print("\n" + "=" * 88)
print("COVERAGE OF INCIDENTS BY THE TOP-k CONFIGURATION ITEMS")
print("=" * 88)
tot = len(TR)
for k in KS:
    print(f"  top {k:>5,} CIs cover {freq.iloc[:k].sum()/tot:6.1%} of incidents")

print("\n" + "=" * 88)
print("INTERPRETATION")
print("=" * 88)
o = out.set_index("k")
for k in (64, 256):
    if k in o.index:
        r = o.loc[k]
        print(f"  at k={k}: top-k {r.top_k:.3f}  random-k {r.random_k:.3f}  "
              f"partition-k {r.partition_k:.3f}")
best = out.loc[out.top_k.idxmax()]
print(f"\n  top-k reaches {best.top_k:.3f} at k={int(best.k)}, against a full-CI "
      f"ceiling of {full_auc:.3f}")
gap = out.iloc[3]
print(f"  targeting high-volume CIs beats identifying the same number at random "
      f"by {gap.top_k - gap.random_k:+.3f} at k={int(gap.k)}")

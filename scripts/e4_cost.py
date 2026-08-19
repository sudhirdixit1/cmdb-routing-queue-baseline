"""E4 -- translate predictive gain into operational cost.

AUC is not a decision.  A triage team can review only a limited fraction of
incoming incidents.  Given a review capacity of k%, rank incidents by
predicted misrouting risk, and measure how many misroutes are caught and how
many handling hours that corresponds to.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14, load_uci

SEED = 20260818
CAPACITIES = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]


def encode(train, test, cols):
    Xtr = np.empty((len(train), len(cols)), dtype=float)
    Xte = np.empty((len(test), len(cols)), dtype=float)
    for j, c in enumerate(cols):
        tr = train[c].astype(str).where(~is_missing(train[c]), "__MISSING__")
        te = test[c].astype(str).where(~is_missing(test[c]), "__MISSING__")
        cats = pd.Index(tr.value_counts().index)
        Xtr[:, j] = pd.Categorical(tr, categories=cats).codes
        Xte[:, j] = pd.Categorical(te, categories=cats).codes
    Xtr[Xtr < 0] = np.nan
    Xte[Xte < 0] = np.nan
    return Xtr, Xte


def score(train, test, cols):
    Xtr, Xte = encode(train, test, cols)
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                         max_leaf_nodes=31, l2_regularization=1.0,
                                         random_state=SEED)
    clf.fit(Xtr, train._y.values)
    return clf.predict_proba(Xte)[:, 1]


# ---------------------------------------------------------------- Rabobank
df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df["_ht"] = pd.to_numeric(df["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                          errors="coerce")
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()

INTAKE = ["Category", "Impact", "Urgency", "Priority"]
CONFIG = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)",
          "Service Component WBS (aff)"]

p_intake = score(train, test, INTAKE)
p_full = score(train, test, INTAKE + CONFIG)
y = test._y.values
ht = test._ht.values

# median handling hours for routed-right vs routed-wrong, from TRAIN only
tr_ht = train._ht
h_ok = float(tr_ht[train._y == 0].median())
h_bad = float(tr_ht[train._y == 1].median())
excess = h_bad - h_ok

print("=" * 90)
print("E4  OPERATIONAL VALUE OF MISROUTING PREDICTION  (Rabobank)")
print("=" * 90)
print(f"  median handle time, routed correctly : {h_ok:6.1f} h")
print(f"  median handle time, later reassigned : {h_bad:6.1f} h")
print(f"  excess attributable to misrouting    : {excess:6.1f} h per incident\n")
print(f"  test set: {len(test):,} incidents, {y.mean():.1%} later reassigned")
print(f"  AUC intake-only {roc_auc_score(y, p_intake):.3f} | "
      f"with CMDB {roc_auc_score(y, p_full):.3f}\n")

print(f"  {'capacity':>9s} {'model':>14s} {'caught':>8s} {'precision':>10s} "
      f"{'lift':>6s} {'excess h flagged':>17s}")
rows = []
for cap in CAPACITIES:
    k = int(len(test) * cap)
    for label, p in [("intake-only", p_intake), ("intake+CMDB", p_full)]:
        idx = np.argsort(-p)[:k]
        caught = int(y[idx].sum())
        recall = caught / y.sum()
        prec = caught / k
        lift = prec / y.mean()
        hours = float(np.nansum(np.maximum(ht[idx] - h_ok, 0)[y[idx] == 1]))
        rows.append(dict(capacity=cap, model=label, k=k, caught=caught,
                         recall=recall, precision=prec, lift=lift,
                         excess_hours=hours))
        print(f"  {cap:>8.0%} {label:>14s} {recall:>7.1%} {prec:>10.1%} "
              f"{lift:>6.2f} {hours:>16,.0f}")
    print()

pd.DataFrame(rows).to_csv(RESULTS / "e4_cost.csv", index=False)

print("=" * 90)
print("WHAT THE CMDB IS WORTH, IN HOURS")
print("=" * 90)
r = pd.DataFrame(rows)
for cap in CAPACITIES:
    a = r[(r.capacity == cap) & (r.model == "intake-only")].iloc[0]
    b = r[(r.capacity == cap) & (r.model == "intake+CMDB")].iloc[0]
    print(f"  at {cap:.0%} review capacity: {b.caught - a.caught:>4,} more misroutes "
          f"caught ({b.recall - a.recall:+.1%} recall), "
          f"{b.excess_hours - a.excess_hours:>9,.0f} additional excess hours surfaced")

# ------------------------------------------------------- Volvo diagnostic
print("\n" + "=" * 90)
print("VOLVO IT DIAGNOSTIC  which creation-time field carries the signal?")
print("=" * 90)
from common import load_bpic13
v = load_bpic13("first").copy()
v["_y"] = (pd.to_numeric(v["reassignment_count"], errors="coerce") >= 1).astype(int)
v["_t"] = pd.to_datetime(v["opened_at"], errors="coerce", utc=True)
v = v.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
c = int(len(v) * 0.70)
vtr, vte = v.iloc[:c].copy(), v.iloc[c:].copy()
FEATS = ["impact", "product", "organization involved", "organization country",
         "resource country"]
for f in FEATS:
    p = score(vtr, vte, [f])
    print(f"  {f:26s} alone: AUC {roc_auc_score(vte._y.values, p):.3f}")
p = score(vtr, vte, FEATS)
print(f"  {'ALL':26s}      : AUC {roc_auc_score(vte._y.values, p):.3f}")
p = score(vtr, vte, ["impact", "product"])
print(f"  {'impact + product only':26s}: AUC {roc_auc_score(vte._y.values, p):.3f}")

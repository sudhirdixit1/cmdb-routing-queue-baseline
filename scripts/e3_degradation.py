"""E3 -- readiness thresholds.

Rabobank is the only instance with a mature CMDB.  Progressively blank its
configuration fields to simulate the same organisation at lower levels of
configuration-management maturity, and locate the population rate at which
the configuration-aware model stops beating the intake-only model.

Degradation is applied to BOTH train and test: a low-maturity organisation
has sparse CI data at training time and at inference time alike.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14

SEED = 20260818
CONFIG = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)",
          "Service Component WBS (aff)"]
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
RATES = [1.0, 0.90, 0.75, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10,
         0.05, 0.02, 0.01, 0.002, 0.0]
N_REPEAT = 5


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


def auc_for(train, test, cols):
    Xtr, Xte = encode(train, test, cols)
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                         max_leaf_nodes=31, l2_regularization=1.0,
                                         random_state=SEED)
    clf.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, clf.predict_proba(Xte)[:, 1])


df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
train_full, test_full = df.iloc[:cut].copy(), df.iloc[cut:].copy()

baseline = auc_for(train_full, test_full, INTAKE)
ceiling = auc_for(train_full, test_full, INTAKE + CONFIG)
print("=" * 88)
print("E3  CONFIGURATION READINESS THRESHOLD  (Rabobank, degraded in silico)")
print("=" * 88)
print(f"  intake-only baseline (no CMDB)      AUC {baseline:.3f}")
print(f"  full configuration ceiling (99.6%)  AUC {ceiling:.3f}")
print(f"  headroom attributable to the CMDB   {ceiling - baseline:+.3f}\n")
print(f"  {'CI population':>14s} {'AUC':>7s} {'vs baseline':>12s} "
      f"{'headroom kept':>14s}")

rows = []
for rate in RATES:
    aucs = []
    for rep in range(N_REPEAT if 0 < rate < 1 else 1):
        rng = np.random.default_rng(SEED + rep)
        tr, te = train_full.copy(), test_full.copy()
        for part in (tr, te):
            keep = rng.random(len(part)) < rate
            for c in CONFIG:
                part.loc[~keep, c] = "__MISSING__"
        aucs.append(auc_for(tr, te, INTAKE + CONFIG))
    a = float(np.mean(aucs))
    sd = float(np.std(aucs))
    kept = (a - baseline) / (ceiling - baseline)
    rows.append(dict(rate=rate, auc=a, sd=sd, delta=a - baseline,
                     headroom_kept=kept))
    print(f"  {rate:>13.1%} {a:>7.3f} {a - baseline:>+12.3f} {kept:>13.1%}"
          + (f"   (sd {sd:.4f})" if sd > 0 else ""))

out = pd.DataFrame(rows)
out.to_csv(RESULTS / "e3_degradation.csv", index=False)

# ---- interpolate thresholds ---------------------------------------------
print("\n" + "=" * 88)
print("READINESS THRESHOLDS  (interpolated)")
print("=" * 88)
o = out.sort_values("rate")
for frac, label in [(0.90, "90% of CMDB benefit retained"),
                    (0.75, "75% retained"),
                    (0.50, "half the benefit lost"),
                    (0.25, "75% of the benefit gone"),
                    (0.10, "capability effectively dead")]:
    thr = np.interp(frac, o.headroom_kept.values, o.rate.values)
    print(f"  {label:34s} requires CI population >= {thr:5.1%}")

sn_rate = 0.002
sn_auc = float(np.interp(sn_rate, o.rate.values, o.auc.values))
print("\n" + "=" * 88)
print("COUNTERFACTUAL  Rabobank held to the ServiceNow instance's CI population")
print("=" * 88)
print(f"  at 0.2% CI population, modelled AUC {sn_auc:.3f} "
      f"vs {ceiling:.3f} at full population")
print(f"  {(ceiling - sn_auc) / (ceiling - baseline):.1%} of the CMDB-attributable "
      f"advantage is lost")

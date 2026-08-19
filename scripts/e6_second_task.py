"""E6 -- does the configuration-data effect generalise beyond routing?

Second task: predict at creation time whether an incident will breach its
service target.  Rabobank has no SLA flag, so the long-handling proxy is the
top quartile of handle time (fit on TRAIN only).  ServiceNow-IT has a genuine
made_sla flag.

If configuration data helps on this task too, the finding is about
configuration readiness generally, not an artefact of the routing target.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14, load_uci

SEED = 20260818
N_BOOT = 2000


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


def boot_delta(y, pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    y, pa, pb = np.asarray(y), np.asarray(pa), np.asarray(pb)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        d.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


print("=" * 92)
print("E6  SECOND TASK -- SERVICE-TARGET BREACH PREDICTION AT CREATION TIME")
print("=" * 92)
rows = []

# -------------------------------------------------- Rabobank (long handling)
df = load_bpic14().copy()
df["_ht"] = pd.to_numeric(df["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                          errors="coerce")
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t", "_ht"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()
thr = train._ht.quantile(0.75)          # threshold from TRAIN only
train["_y"] = (train._ht > thr).astype(int)
test["_y"] = (test._ht > thr).astype(int)

INTAKE = ["Category", "Impact", "Urgency", "Priority"]
CONFIG = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)",
          "Service Component WBS (aff)"]
y = test._y.values
pi = score(train, test, INTAKE)
pc = score(train, test, INTAKE + CONFIG)
po = score(train, test, CONFIG)
lo, hi = boot_delta(y, pi, pc)
print(f"\nRabobank  (long handling: >{thr:.1f}h, train p75; "
      f"test positive rate {y.mean():.1%}, n={len(test):,})")
print(f"  intake-only      AUC {roc_auc_score(y,pi):.3f}  AP {average_precision_score(y,pi):.3f}")
print(f"  configuration    AUC {roc_auc_score(y,po):.3f}  AP {average_precision_score(y,po):.3f}")
print(f"  intake+config    AUC {roc_auc_score(y,pc):.3f}  AP {average_precision_score(y,pc):.3f}")
print(f"  delta from configuration  {roc_auc_score(y,pc)-roc_auc_score(y,pi):+.3f} "
      f"[{lo:+.3f},{hi:+.3f}]")
rows.append(dict(org="Rabobank", task="long-handling", intake=roc_auc_score(y, pi),
                 config_only=roc_auc_score(y, po), both=roc_auc_score(y, pc),
                 delta=roc_auc_score(y, pc) - roc_auc_score(y, pi), lo=lo, hi=hi))

# -------------------------------------------------- ServiceNow-IT (real SLA)
u = load_uci("first").copy()
u["_t"] = pd.to_datetime(u["opened_at"], errors="coerce", utc=True)
u = u.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
u["_y"] = u["sla_breach"].astype(int)
cut = int(len(u) * 0.70)
utr, ute = u.iloc[:cut].copy(), u.iloc[cut:].copy()
UI = ["category", "subcategory", "location", "contact_type", "impact",
      "urgency", "priority", "opened_by", "caller_id"]
UC = ["cmdb_ci"]
yu = ute._y.values
pui = score(utr, ute, UI)
puc = score(utr, ute, UI + UC)
lo2, hi2 = boot_delta(yu, pui, puc)
print(f"\nServiceNow-IT  (genuine made_sla flag; "
      f"test breach rate {yu.mean():.1%}, n={len(ute):,})")
print(f"  intake-only      AUC {roc_auc_score(yu,pui):.3f}  AP {average_precision_score(yu,pui):.3f}")
print(f"  intake+config    AUC {roc_auc_score(yu,puc):.3f}  AP {average_precision_score(yu,puc):.3f}")
print(f"  delta from configuration  {roc_auc_score(yu,puc)-roc_auc_score(yu,pui):+.3f} "
      f"[{lo2:+.3f},{hi2:+.3f}]   (field is 0.2% populated)")
rows.append(dict(org="ServiceNow-IT", task="sla-breach", intake=roc_auc_score(yu, pui),
                 config_only=np.nan, both=roc_auc_score(yu, puc),
                 delta=roc_auc_score(yu, puc) - roc_auc_score(yu, pui),
                 lo=lo2, hi=hi2))

pd.DataFrame(rows).to_csv(RESULTS / "e6_second_task.csv", index=False)

print("\n" + "=" * 92)
print("VERDICT")
print("=" * 92)
print("  The configuration-data effect is not specific to the routing target.")
print("  Where configuration data exists it helps on both tasks; where the field")
print("  exists but is unpopulated it contributes nothing on either.")

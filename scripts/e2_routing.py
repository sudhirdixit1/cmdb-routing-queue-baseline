"""E2 -- does configuration data improve misrouting prediction?

Task: at incident creation, predict whether the incident will later be
reassigned.  Comparable across all three organisations and tied directly to
the observed cost model.

Leakage controls:
  * features are taken from the FIRST observed state of each incident
  * the target is derived from the terminal state
  * fields recorded during handling (assignment group, assigned_to, knowledge
    article, closure code, causing-CI) are excluded outright
  * train/test split is temporal, never random
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic13, load_bpic14, load_uci

SEED = 20260818
N_BOOT = 2000

SPECS = {
    "ServiceNow-IT": dict(
        loader=lambda: load_uci("first"),
        intake=["category", "subcategory", "location", "contact_type",
                "impact", "urgency", "priority", "opened_by", "caller_id"],
        config=["cmdb_ci"],
    ),
    "VolvoIT": dict(
        loader=lambda: load_bpic13("first"),
        intake=["impact", "product", "organization involved",
                "organization country", "resource country"],
        config=[],
    ),
    "Rabobank": dict(
        loader=load_bpic14,
        intake=["Category", "Impact", "Urgency", "Priority"],
        config=["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)",
                "Service Component WBS (aff)"],
    ),
}


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


def fit_score(train, test, cols):
    Xtr, Xte = encode(train, test, cols)
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                         max_leaf_nodes=31, l2_regularization=1.0,
                                         random_state=SEED)
    clf.fit(Xtr, train._y.values)
    return clf.predict_proba(Xte)[:, 1]


def boot_auc(y, p, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    out = [roc_auc_score(y[i], p[i]) for i in
           (rng.integers(0, len(y), len(y)) for _ in range(n))
           if len(np.unique(y[i])) > 1]
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def boot_delta(y, pa, pb, n=N_BOOT, seed=SEED):
    """CI for AUC(pb) - AUC(pa) on paired bootstrap resamples."""
    rng = np.random.default_rng(seed)
    y, pa, pb = np.asarray(y), np.asarray(pa), np.asarray(pb)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        d.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def prep(org, spec):
    df = spec["loader"]().copy()
    df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
    df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
    cut = int(len(df) * 0.70)
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()


rows, preds = [], {}
for org, spec in SPECS.items():
    train, test = prep(org, spec)
    y = test._y.values
    conds = {"intake": spec["intake"]}
    if spec["config"]:
        conds["config-only"] = spec["config"]
        conds["intake+config"] = spec["intake"] + spec["config"]
    rows.append(dict(org=org, condition="trivial (majority)", n_feat=0, auc=0.500,
                     lo=np.nan, hi=np.nan, ap=float(y.mean()),
                     n_train=len(train), n_test=len(test), base=float(y.mean())))
    for name, cols in conds.items():
        cols = [c for c in cols if c in train.columns]
        if not cols:
            continue
        p = fit_score(train, test, cols)
        preds[(org, name)] = (y, p)
        lo, hi = boot_auc(y, p)
        rows.append(dict(org=org, condition=name, n_feat=len(cols),
                         auc=float(roc_auc_score(y, p)), lo=lo, hi=hi,
                         ap=float(average_precision_score(y, p)),
                         n_train=len(train), n_test=len(test), base=float(y.mean())))

res = pd.DataFrame(rows)
res.to_csv(RESULTS / "e2_routing.csv", index=False)

print("=" * 92)
print("E2  MISROUTING PREDICTION FROM CREATION-TIME STATE ONLY (temporal 70/30)")
print("=" * 92)
print(f"{'org':15s} {'condition':20s} {'feat':>5s} {'AUC':>7s} {'95% CI':>16s} "
      f"{'AP':>7s} {'base':>6s} {'n_test':>8s}")
for org in SPECS:
    for _, r in res[res.org == org].iterrows():
        ci = f"[{r.lo:.3f},{r.hi:.3f}]" if pd.notna(r.lo) else " " * 16
        print(f"{r.org:15s} {r.condition:20s} {r.n_feat:>5d} {r.auc:>7.3f} {ci:>16s} "
              f"{r.ap:>7.3f} {r.base:>6.3f} {r.n_test:>8,}")
    print()

print("=" * 92)
print("WHAT CONFIGURATION DATA ADDS  (paired bootstrap on the delta)")
print("=" * 92)
for org in SPECS:
    if (org, "intake+config") not in preds:
        s = res[(res.org == org) & (res.condition == "intake")].iloc[0]
        print(f"  {org:15s} intake {s.auc:.3f}  --  no configuration data captured")
        continue
    y, pi = preds[(org, "intake")]
    _, pc = preds[(org, "intake+config")]
    _, po = preds[(org, "config-only")]
    lo, hi = boot_delta(y, pi, pc)
    d = roc_auc_score(y, pc) - roc_auc_score(y, pi)
    print(f"  {org:15s} intake {roc_auc_score(y,pi):.3f} -> intake+config "
          f"{roc_auc_score(y,pc):.3f}   delta {d:+.3f} [{lo:+.3f},{hi:+.3f}]")
    print(f"  {'':15s} configuration alone: {roc_auc_score(y,po):.3f}")

# ---- Rabobank: which configuration field carries the signal? -------------
print("\n" + "=" * 92)
print("CONFIGURATION FIELD ABLATION  (Rabobank -- the only mature CMDB)")
print("=" * 92)
tr, te = prep("Rabobank", SPECS["Rabobank"])
y = te._y.values
for single in SPECS["Rabobank"]["config"]:
    p = fit_score(tr, te, [single])
    print(f"  {single:32s} alone: AUC {roc_auc_score(y, p):.3f}")
for drop in SPECS["Rabobank"]["config"]:
    cols = [c for c in SPECS["Rabobank"]["config"] if c != drop]
    p = fit_score(tr, te, cols)
    print(f"  without {drop:24s}       AUC {roc_auc_score(y, p):.3f}")

# ---- ServiceNow-IT: the 0.2% where cmdb_ci IS populated ------------------
print("\n" + "=" * 92)
print("ORACLE-CI SUBSET  (ServiceNow-IT incidents that DO carry a CI)")
print("=" * 92)
tr, te = prep("ServiceNow-IT", SPECS["ServiceNow-IT"])
full = pd.concat([tr, te])
has_ci = ~is_missing(full["cmdb_ci"])
print(f"  incidents with a populated cmdb_ci: {has_ci.sum()} of {len(full)} "
      f"({has_ci.mean():.2%})")
print(f"  reassignment rate  with CI: {full.loc[has_ci,'_y'].mean():.3f}   "
      f"without CI: {full.loc[~has_ci,'_y'].mean():.3f}")
print("  -> subset is far too small for a reliable within-organisation estimate;")
print("     reported as a descriptive check only, not as evidence.")

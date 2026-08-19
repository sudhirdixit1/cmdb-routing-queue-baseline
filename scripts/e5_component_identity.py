"""E5 -- the reframe.

Rabobank reaches AUC 0.742 with a mature CMDB.  Volvo reaches 0.744 with no
CMDB at all, using a mandatory intake field that names the affected product.
That suggests the binding constraint is not "do you operate a CMDB" but
"is the affected component identified at incident creation, by any mechanism,
at sufficient granularity".

This script tests that directly: for every creation-time field in every
organisation, measure single-field predictive power against the field's
effective granularity, and see whether granularity explains performance.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import (FIGURES, RESULTS, is_missing, load_bpic13, load_bpic14,
                    load_uci, population_rate)

SEED = 20260818

FIELDS = {
    "ServiceNow-IT": (lambda: load_uci("first"),
                      ["category", "subcategory", "location", "contact_type",
                       "impact", "urgency", "priority", "opened_by",
                       "caller_id", "cmdb_ci"],
                      {"cmdb_ci": "configuration", "subcategory": "component-ish"}),
    "VolvoIT": (lambda: load_bpic13("first"),
                ["impact", "product", "organization involved",
                 "organization country", "resource country"],
                {"product": "component-ish"}),
    "Rabobank": (load_bpic14,
                 ["Category", "Impact", "Urgency", "Priority", "CI Name (aff)",
                  "CI Type (aff)", "CI Subtype (aff)",
                  "Service Component WBS (aff)"],
                 {"CI Name (aff)": "configuration",
                  "Service Component WBS (aff)": "configuration"}),
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


def auc1(train, test, col):
    Xtr, Xte = encode(train, test, [col])
    clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08,
                                         max_leaf_nodes=31, l2_regularization=1.0,
                                         random_state=SEED)
    clf.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, clf.predict_proba(Xte)[:, 1])


def prep(loader):
    df = loader().copy()
    df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
    df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
    c = int(len(df) * 0.70)
    return df.iloc[:c].copy(), df.iloc[c:].copy()


rows = []
for org, (loader, fields, tags) in FIELDS.items():
    train, test = prep(loader)
    for f in fields:
        if f not in train.columns:
            continue
        pop = population_rate(pd.concat([train[f], test[f]]))
        nonmiss = train[f][~is_missing(train[f])]
        card = int(nonmiss.nunique())
        # effective granularity: population x log2(cardinality)
        eff = pop * np.log2(max(card, 2))
        rows.append(dict(org=org, field=f, tag=tags.get(f, "other"),
                         population=pop, cardinality=card,
                         eff_granularity=eff,
                         auc=auc1(train, test, f)))

d = pd.DataFrame(rows).sort_values("auc", ascending=False)
d.to_csv(RESULTS / "e5_component_identity.csv", index=False)

print("=" * 96)
print("E5  SINGLE-FIELD PREDICTIVE POWER vs EFFECTIVE GRANULARITY")
print("=" * 96)
print(f"{'org':15s} {'field':30s} {'tag':14s} {'pop':>6s} {'card':>7s} "
      f"{'effgran':>8s} {'AUC':>6s}")
for _, r in d.iterrows():
    print(f"{r.org:15s} {r.field:30s} {r.tag:14s} {r.population:>5.1%} "
          f"{r.cardinality:>7,} {r.eff_granularity:>8.2f} {r.auc:>6.3f}")

print("\n" + "=" * 96)
print("CORRELATION  effective granularity vs single-field AUC")
print("=" * 96)
sub = d[d.population > 0.05]
print(f"  Pearson  r = {np.corrcoef(sub.eff_granularity, sub.auc)[0,1]:.3f} "
      f"(n = {len(sub)}, fields with >5% population)")
print(f"  Spearman r = {sub.eff_granularity.corr(sub.auc, method='spearman'):.3f}")
print("\n  raw cardinality alone (ignoring population):")
print(f"  Pearson  r = {np.corrcoef(np.log2(sub.cardinality.clip(lower=2)), sub.auc)[0,1]:.3f}")

print("\n" + "=" * 96)
print("THE COMPONENT-IDENTITY FIELD IN EACH ORGANISATION")
print("=" * 96)
best = d[d.population > 0.5].sort_values("auc", ascending=False).groupby("org").head(1)
for _, r in best.iterrows():
    print(f"  {r.org:15s} {r.field:30s} card {r.cardinality:>6,}  "
          f"pop {r.population:>6.1%}  AUC {r.auc:.3f}")
print("\n  ServiceNow-IT's nominal configuration field, for contrast:")
sn = d[(d.org == 'ServiceNow-IT') & (d.field == 'cmdb_ci')].iloc[0]
print(f"  {'ServiceNow-IT':15s} {'cmdb_ci':30s} card {sn.cardinality:>6,}  "
      f"pop {sn.population:>6.1%}  AUC {sn.auc:.3f}")

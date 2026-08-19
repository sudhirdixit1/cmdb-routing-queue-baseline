"""E13 -- the capability-resolution curve.

E12 showed that a RANDOM partition of configuration items into 259 groups
performs as well as the real service hierarchy at the same cardinality.  So
the value of configuration data is not in its taxonomy but in how finely it
discriminates components.

That reframes the question from "which layer" to "how much resolution".
This builds the curve: coarsen component identity into k random groups for
k from 2 to full cardinality, and measure capability at each k.  Real
fields are then plotted at their own cardinality.  A real field sitting ON
the random curve carries no semantic value beyond its resolution; one
sitting ABOVE it does.

Random partitions are the control by construction, so this is immune to the
feature-ordering confound that invalidated the earlier decomposition.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic13, load_bpic14, load_uci

SEED = 20260819
N_REP = 5

SPECS = {
    "Rabobank": dict(
        loader=load_bpic14,
        base=["Category", "Impact", "Urgency", "Priority"],
        ident="CI Name (aff)",
        real={"CI Type (aff)": "CI Type", "CI Subtype (aff)": "CI Subtype",
              "Service Component WBS (aff)": "Service Component",
              "CI Name (aff)": "CI Name"},
    ),
    "VolvoIT": dict(
        loader=lambda: load_bpic13("first"),
        base=["impact", "organization involved", "organization country",
              "resource country"],
        ident="product",
        real={"product": "product"},
    ),
    "ServiceNow-IT": dict(
        loader=lambda: load_uci("first"),
        base=["location", "contact_type", "impact", "urgency", "priority",
              "opened_by", "caller_id"],
        ident="subcategory",
        real={"category": "category", "subcategory": "subcategory"},
    ),
}


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


def prep(loader):
    df = loader().copy()
    df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
    df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
    c = int(len(df) * 0.70)
    return df.iloc[:c].copy(), df.iloc[c:].copy()


rows, reals = [], []
for org, spec in SPECS.items():
    TR, TE = prep(spec["loader"])
    base_auc = auc(TR, TE, spec["base"])
    ident = spec["ident"]
    vals = pd.Index(pd.concat([TR, TE])[ident].astype(str).unique())
    full_k = len(vals)
    ks = [k for k in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
          if k < full_k] + [full_k]

    print("=" * 84)
    print(f"{org}   identity field '{ident}' has {full_k:,} distinct values")
    print(f"  base (no component identity): AUC {base_auc:.3f}")
    print(f"  {'k groups':>9s} {'AUC':>7s} {'sd':>7s} {'gain':>8s}")
    for k in ks:
        a = []
        for rep in range(1 if k == full_k else N_REP):
            rng = np.random.default_rng(SEED + rep)
            lut = pd.Series(rng.integers(0, k, len(vals)).astype(str), index=vals) \
                if k < full_k else pd.Series(vals, index=vals)
            tr, te = TR.copy(), TE.copy()
            tr["_k"] = tr[ident].astype(str).map(lut).fillna("__M__")
            te["_k"] = te[ident].astype(str).map(lut).fillna("__M__")
            a.append(auc(tr, te, spec["base"] + ["_k"]))
        rows.append(dict(org=org, k=k, auc=float(np.mean(a)),
                         sd=float(np.std(a)), base=base_auc,
                         gain=float(np.mean(a)) - base_auc))
        print(f"  {k:>9,} {np.mean(a):>7.3f} {np.std(a):>7.4f} "
              f"{np.mean(a)-base_auc:>+8.3f}")

    for col, label in spec["real"].items():
        if col not in TR.columns:
            continue
        card = int(TR[col][~is_missing(TR[col])].nunique())
        a = auc(TR, TE, spec["base"] + [col])
        reals.append(dict(org=org, field=label, cardinality=card, auc=a,
                          base=base_auc, gain=a - base_auc))
        print(f"  REAL  {label:22s} k={card:>6,}  AUC {a:.3f}")
    print()

curve = pd.DataFrame(rows); real = pd.DataFrame(reals)
curve.to_csv(RESULTS / "e13_resolution_curve.csv", index=False)
real.to_csv(RESULTS / "e13_real_fields.csv", index=False)

print("=" * 84)
print("SATURATION  -- k at which 90% / 95% of the full-resolution gain is reached")
print("=" * 84)
for org in SPECS:
    c = curve[curve.org == org].sort_values("k")
    full_gain = c.gain.iloc[-1]
    if full_gain <= 0:
        print(f"  {org:15s} no positive gain from component identity")
        continue
    for frac in (0.90, 0.95):
        hit = c[c.gain >= frac * full_gain]
        k = int(hit.k.iloc[0]) if len(hit) else None
        print(f"  {org:15s} {frac:.0%} of gain reached at k = {k}"
              f"   (full k = {int(c.k.iloc[-1]):,})")

print("\n" + "=" * 84)
print("DOES REAL TAXONOMY BEAT A RANDOM PARTITION OF THE SAME SIZE?")
print("=" * 84)
for _, r in real.iterrows():
    c = curve[curve.org == r.org].sort_values("k")
    interp = float(np.interp(np.log2(max(r.cardinality, 2)),
                             np.log2(c.k.clip(lower=2)), c.auc))
    delta = r.auc - interp
    verdict = "above curve" if delta > 0.01 else \
              ("below curve" if delta < -0.01 else "ON the curve")
    print(f"  {r.org:15s} {r.field:20s} k={r.cardinality:>6,}  "
          f"real {r.auc:.3f}  random {interp:.3f}  {delta:+.3f}  {verdict}")

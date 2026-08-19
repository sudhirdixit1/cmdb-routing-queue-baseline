"""E15 -- independently verify the two fatal findings from adversarial review.

F1: the taxonomy comparison matched real fields against random partitions at
    equal NOMINAL cardinality.  Real taxonomies are mass-imbalanced, so their
    EFFECTIVE resolution is far lower than their label count.  Claim: matching
    on effective cardinality reverses the sign.

M1: HistGradientBoostingClassifier bins ordinal features into at most 255
    bins by default.  With 2,633 CI codes fed as frequency-rank ordinals the
    model may not be able to resolve them all, which would make "top-128
    matches the full CMDB" partly tautological.

Both are checked here from scratch, not taken on trust.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14

SEED = 20260819
BASE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"
FIELDS = {"CI Type (aff)": "CI Type", "CI Subtype (aff)": "CI Subtype",
          "Service Component WBS (aff)": "Service Component",
          "CI Name (aff)": "CI Name"}

df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
cut = int(len(df) * 0.70)
TR, TE = df.iloc[:cut].copy(), df.iloc[cut:].copy()


def ords(train, test, cols):
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


def hgb(train, test, cols):
    Xtr, Xte = ords(train, test, cols)
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, m.predict_proba(Xte)[:, 1])


def ohe_lr(train, test, cols):
    tr = train[cols].astype(str); te = test[cols].astype(str)
    e = OneHotEncoder(handle_unknown="ignore", min_frequency=1)
    Xtr = e.fit_transform(tr); Xte = e.transform(te)
    m = LogisticRegression(max_iter=3000, C=1.0)
    m.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, m.predict_proba(Xte)[:, 1])


print("=" * 88)
print("F1  EFFECTIVE vs NOMINAL CARDINALITY")
print("=" * 88)
print(f"  {'field':22s} {'nominal k':>10s} {'perplexity':>11s} {'top class':>10s}")
eff = {}
for col, name in FIELDS.items():
    s = TR[col].astype(str).where(~is_missing(TR[col]), "__M__")
    p = s.value_counts(normalize=True)
    H = -(p * np.log2(p)).sum()
    eff[name] = 2 ** H
    print(f"  {name:22s} {s.nunique():>10,} {2**H:>11.1f} {p.iloc[0]:>9.1%}")

# --- mass-matched null: random partition reproducing the field's mass profile
print("\n" + "=" * 88)
print("MASS-MATCHED NULL  (random CI partition with the field's own mass profile)")
print("=" * 88)
cis = pd.Index(pd.concat([TR, TE])[IDENT].astype(str).unique())
ci_mass = TR[IDENT].astype(str).value_counts()
ci_mass = ci_mass.reindex(cis, fill_value=0)

rows = []
for col, name in FIELDS.items():
    real = hgb(TR, TE, BASE + [col])
    s = TR[col].astype(str).where(~is_missing(TR[col]), "__M__")
    target_shares = s.value_counts(normalize=True).values   # mass profile to mimic
    aucs = []
    for rep in range(5):
        rng = np.random.default_rng(SEED + rep)
        order = rng.permutation(len(cis))
        shuffled = ci_mass.iloc[order]
        cum = shuffled.cumsum() / shuffled.sum()
        edges = np.cumsum(target_shares)[:-1]
        grp = np.searchsorted(edges, cum.values, side="left")
        lut = pd.Series(grp.astype(str), index=shuffled.index)
        tr, te = TR.copy(), TE.copy()
        tr["_m"] = tr[IDENT].astype(str).map(lut).fillna("__M__")
        te["_m"] = te[IDENT].astype(str).map(lut).fillna("__M__")
        aucs.append(hgb(tr, te, BASE + ["_m"]))
    d = real - float(np.mean(aucs))
    rows.append(dict(field=name, real=real, mass_matched=float(np.mean(aucs)),
                     sd=float(np.std(aucs)), delta=d))
    print(f"  {name:22s} real {real:.3f}   mass-matched {np.mean(aucs):.3f} "
          f"(sd {np.std(aucs):.3f})   delta {d:+.3f}")

pd.DataFrame(rows).to_csv(RESULTS / "e15_mass_matched.csv", index=False)

# --- also re-interpolate the published curve at EFFECTIVE cardinality
print("\n  re-interpolating the PUBLISHED random curve at effective k:")
c = pd.read_csv(RESULTS / "e13_resolution_curve.csv")
c = c[c.org == "Rabobank"].sort_values("k")
real_tbl = pd.read_csv(RESULTS / "e13_real_fields.csv")
real_tbl = real_tbl[real_tbl.org == "Rabobank"]
for _, r in real_tbl.iterrows():
    nom = float(np.interp(np.log2(max(r.cardinality, 2)),
                          np.log2(c.k.clip(lower=2)), c.auc))
    e = eff.get(r.field)
    if e is None:
        continue
    ef = float(np.interp(np.log2(max(e, 2)), np.log2(c.k.clip(lower=2)), c.auc))
    print(f"    {r.field:22s} nominal-d {r.auc-nom:+.3f}   effective-d {r.auc-ef:+.3f}")

print("\n" + "=" * 88)
print("M1  CAN THE ESTIMATOR EVEN RESOLVE 2,633 CI VALUES?")
print("=" * 88)
Xtr, _ = ords(TR, TE, [IDENT])
bm = _BinMapper(n_bins=256, random_state=SEED).fit(Xtr)
binned = bm.transform(Xtr)
n_codes = int(np.nanmax(Xtr)) + 1
n_bins = len(np.unique(binned))
print(f"  distinct CI codes in TRAIN            {n_codes:,}")
print(f"  distinct BINNED values the model sees {n_bins:,}")
print(f"  -> the 'full CMDB' arm is effectively a top-~{n_bins} model")

print("\n  re-running the targeting comparison with a bin-free encoder:")
full_h = hgb(TR, TE, BASE + [IDENT])
full_l = ohe_lr(TR, TE, BASE + [IDENT])
freq = TR[IDENT].astype(str).value_counts()
out = []
for k in (128, 256, 1024):
    keep = set(freq.index[:k])
    tr, te = TR.copy(), TE.copy()
    for part in (tr, te):
        s = part[IDENT].astype(str)
        part["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    out.append((k, hgb(tr, te, BASE + ["_v"]), ohe_lr(tr, te, BASE + ["_v"])))
print(f"  {'condition':>14s} {'HGB(255 bins)':>15s} {'one-hot LR':>12s}")
print(f"  {'full CI':>14s} {full_h:>15.3f} {full_l:>12.3f}")
for k, h, l in out:
    print(f"  {'top-'+str(k):>14s} {h:>15.3f} {l:>12.3f}")
print(f"\n  top-128 recovers {100*(out[0][2]-0.566)/(full_l-0.566):.0f}% of the CI "
      f"gain under one-hot LR, vs {100*(out[0][1]-0.566)/(full_h-0.566):.0f}% under HGB")

# --- M2: what does random-k actually cover?
print("\n" + "=" * 88)
print("M2  IS 'k RANDOM CIs' A STRAWMAN?")
print("=" * 88)
tot = len(TR)
for k in (8, 128, 1024):
    rng = np.random.default_rng(SEED)
    cov = np.mean([freq.reindex(rng.choice(cis, size=k, replace=False))
                   .fillna(0).sum() / tot for _ in range(20)])
    topcov = freq.iloc[:k].sum() / tot
    print(f"  k={k:>5,}  random-k covers {cov:6.2%} of incidents   "
          f"top-k covers {topcov:6.2%}")

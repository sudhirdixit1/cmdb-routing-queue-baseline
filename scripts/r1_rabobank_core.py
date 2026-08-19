"""R1 -- definitive single-organisation analysis (Rabobank / BPIC 2014).

Rebuilt from scratch after adversarial review. Every fix applied:

  * warm-up window dropped (pre-2013-10 records are left-censored long-runners
    with 76-100% reassignment rates)
  * 203 blank incident IDs dropped
  * vocabulary and all encodings fit on TRAIN only -- no test values leak into
    the category set
  * TWO estimators reported: one-hot logistic regression (bin-free, exact) as
    primary, and histogram gradient boosting as secondary with its binning
    limit measured and stated
  * taxonomy compared against a MASS-MATCHED null, not a nominal-cardinality
    one -- the error that reversed the previous draft's headline
  * targeting compared against partition-k (full coverage, coarse labels),
    the honest comparator, not against k uniformly-drawn CIs
  * 25 repetitions on all random-partition curves
  * bootstrap CIs on every headline number, plus split and seed variance
    reported separately because the bootstrap cannot see them
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing

SEED = 20260819
N_BOOT = 2000
N_REP = 25
WARMUP_CUTOFF = "2013-10-01"
BASE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"
TAXO = {"CI Type (aff)": "CI Type", "CI Subtype (aff)": "CI Subtype",
        "Service Component WBS (aff)": "Service Component",
        "CI Name (aff)": "CI Name"}


# ------------------------------------------------------------------ data
def load():
    d = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                    encoding="latin-1")
    d = d.loc[:, [c for c in d.columns if not c.startswith("Unnamed")]]
    d.columns = [c.strip() for c in d.columns]
    n0 = len(d)
    d = d[~is_missing(d["Incident ID"])]
    n1 = len(d)
    d["_t"] = pd.to_datetime(d["Open Time"], format="%d/%m/%Y %H:%M:%S",
                             errors="coerce", dayfirst=True)
    d["_ra"] = pd.to_numeric(d["# Reassignments"], errors="coerce")
    d["_ht"] = pd.to_numeric(d["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                             errors="coerce")
    d = d.dropna(subset=["_t", "_ra"])
    n2 = len(d)
    d = d[d._t >= WARMUP_CUTOFF]
    d["_y"] = (d._ra >= 1).astype(int)
    print(f"  rows in file {n0:,} -> drop blank IDs {n0-n1:,} -> "
          f"drop unparseable {n1-n2:,} -> drop warm-up {n2-len(d):,}")
    return d.sort_values("_t").reset_index(drop=True)


def split(d, frac=0.70):
    c = int(len(d) * frac)
    return d.iloc[:c].copy(), d.iloc[c:].copy()


# -------------------------------------------------------------- encoders
def ohe_lr(tr, te, cols):
    """Primary estimator: bin-free, every level gets its own coefficient."""
    e = OneHotEncoder(handle_unknown="ignore")
    Xtr = e.fit_transform(tr[cols].astype(str))       # fit on TRAIN only
    Xte = e.transform(te[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=1.0)
    m.fit(Xtr, tr._y.values)
    return m.predict_proba(Xte)[:, 1]


def hgb(tr, te, cols):
    """Secondary estimator.  Ordinal codes are binned to <=255 values."""
    Xtr = np.empty((len(tr), len(cols))); Xte = np.empty((len(te), len(cols)))
    for j, c in enumerate(cols):
        a = tr[c].astype(str); b = te[c].astype(str)
        cats = pd.Index(a.value_counts().index)        # TRAIN only
        x = pd.Categorical(a, categories=cats).codes.astype(float)
        z = pd.Categorical(b, categories=cats).codes.astype(float)
        x[x < 0] = np.nan; z[z < 0] = np.nan
        Xtr[:, j], Xte[:, j] = x, z
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, tr._y.values)
    return m.predict_proba(Xte)[:, 1]


def boot_ci(y, p, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], p[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def boot_delta(y, pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


print("=" * 90)
print("R1  RABOBANK SINGLE-ORGANISATION ANALYSIS")
print("=" * 90)
D = load()
TR, TE = split(D)
y = TE._y.values
print(f"  usable {len(D):,} incidents | train {len(TR):,} test {len(TE):,}")
print(f"  window {D._t.min().date()} .. {D._t.max().date()}")
print(f"  positive rate: train {TR._y.mean():.3f}  test {y.mean():.3f}")

results = {}
print("\n" + "=" * 90)
print("A. DOES CONFIGURATION DATA HELP?")
print("=" * 90)
print(f"  {'condition':22s} {'one-hot LR':>22s} {'HGB':>22s}")
for name, cols in [("intake only", BASE),
                   ("+ CI identity", BASE + [IDENT]),
                   ("+ full config block", BASE + list(TAXO))]:
    pl = ohe_lr(TR, TE, cols); ph = hgb(TR, TE, cols)
    al, ah = roc_auc_score(y, pl), roc_auc_score(y, ph)
    lo, hi = boot_ci(y, pl)
    results[name] = (pl, al)
    print(f"  {name:22s} {al:>8.3f} [{lo:.3f},{hi:.3f}] {ah:>15.3f}")

pi, _ = results["intake only"]
pc, _ = results["+ CI identity"]
lo, hi = boot_delta(y, pi, pc)
gain = roc_auc_score(y, pc) - roc_auc_score(y, pi)
print(f"\n  CI identity contributes {gain:+.3f} [{lo:+.3f},{hi:+.3f}] (one-hot LR)")

print("\n  split and seed variance (what the bootstrap cannot see):")
for frac in (0.55, 0.65, 0.70, 0.80):
    tr, te = split(D, frac)
    a0 = roc_auc_score(te._y.values, ohe_lr(tr, te, BASE))
    a1 = roc_auc_score(te._y.values, ohe_lr(tr, te, BASE + [IDENT]))
    print(f"    cut {frac:.0%}: intake {a0:.3f}  +CI {a1:.3f}  gain {a1-a0:+.3f}")

print("\n" + "=" * 90)
print("B. TAXONOMY vs MASS-MATCHED NULL")
print("=" * 90)
cis = pd.Index(TR[IDENT].astype(str).unique())          # TRAIN vocabulary only
mass = TR[IDENT].astype(str).value_counts().reindex(cis, fill_value=0)
rows = []
print(f"  {'field':20s} {'nom k':>6s} {'perplex':>8s} {'real':>7s} "
      f"{'matched':>8s} {'delta':>8s} {'95% CI':>18s}")
for col, name in TAXO.items():
    s = TR[col].astype(str)
    p = s.value_counts(normalize=True)
    perplex = 2 ** (-(p * np.log2(p)).sum())
    p_real = ohe_lr(TR, TE, BASE + [col]); a_real = roc_auc_score(y, p_real)
    shares = p.values
    aucs, draws = [], []
    rng_b = np.random.default_rng(SEED)
    for rep in range(N_REP):
        rng = np.random.default_rng(SEED + rep)
        sh = mass.iloc[rng.permutation(len(cis))]
        cum = sh.cumsum() / sh.sum()
        grp = np.searchsorted(np.cumsum(shares)[:-1], cum.values, side="left")
        lut = pd.Series(grp.astype(str), index=sh.index)
        tr, te = TR.copy(), TE.copy()
        tr["_m"] = tr[IDENT].astype(str).map(lut).fillna("__M__")
        te["_m"] = te[IDENT].astype(str).map(lut).fillna("__M__")
        p_null = ohe_lr(tr, te, BASE + ["_m"])
        aucs.append(roc_auc_score(y, p_null))
        # pool bootstrap draws ACROSS reps so the interval carries both
        # test-set resampling and null-construction variance
        for _ in range(N_BOOT // N_REP):
            i = rng_b.integers(0, len(y), len(y))
            if len(np.unique(y[i])) > 1:
                draws.append(roc_auc_score(y[i], p_real[i])
                             - roc_auc_score(y[i], p_null[i]))
    lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    d = a_real - float(np.mean(aucs))
    rows.append(dict(field=name, nominal_k=int(s.nunique()), perplexity=perplex,
                     real=a_real, matched=float(np.mean(aucs)),
                     matched_sd=float(np.std(aucs)), delta=d, lo=lo, hi=hi))
    print(f"  {name:20s} {s.nunique():>6,} {perplex:>8.1f} {a_real:>7.3f} "
          f"{np.mean(aucs):>8.3f} {d:>+8.3f}  [{lo:+.3f},{hi:+.3f}]")
pd.DataFrame(rows).to_csv(RESULTS / "r1_taxonomy.csv", index=False)

print("\n" + "=" * 90)
print("C. TARGETING  (honest comparator: partition-k = full coverage, coarse labels)")
print("=" * 90)
a_base = roc_auc_score(y, ohe_lr(TR, TE, BASE))
p_full = ohe_lr(TR, TE, BASE + [IDENT]); a_full = roc_auc_score(y, p_full)
freq = TR[IDENT].astype(str).value_counts()
tot = len(TR)
print(f"  floor {a_base:.3f}   ceiling {a_full:.3f}   estate {len(cis):,} CIs\n")
print(f"  {'k':>6s} {'inc.cov':>8s} {'top-k':>18s} {'partition-k':>13s} {'recovered':>10s}")
rows = []
for k in (8, 16, 32, 64, 128, 256, 512, 1024):
    keep = set(freq.index[:k])
    tr, te = TR.copy(), TE.copy()
    for part in (tr, te):
        s = part[IDENT].astype(str)
        part["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    p_top = ohe_lr(tr, te, BASE + ["_v"]); a_top = roc_auc_score(y, p_top)
    tlo, thi = boot_ci(y, p_top)
    parts = []
    for rep in range(N_REP):
        rng = np.random.default_rng(SEED + rep)
        lut = pd.Series(rng.integers(0, k, len(cis)).astype(str), index=cis)
        tr2, te2 = TR.copy(), TE.copy()
        tr2["_v"] = tr2[IDENT].astype(str).map(lut).fillna("__M__")
        te2["_v"] = te2[IDENT].astype(str).map(lut).fillna("__M__")
        parts.append(roc_auc_score(y, ohe_lr(tr2, te2, BASE + ["_v"])))
    cov = freq.iloc[:k].sum() / tot
    rec = (a_top - a_base) / (a_full - a_base)
    rows.append(dict(k=k, coverage=cov, top_k=a_top, top_lo=tlo, top_hi=thi,
                     partition_k=float(np.mean(parts)),
                     partition_sd=float(np.std(parts)),
                     recovered=rec, base=a_base, full=a_full))
    print(f"  {k:>6,} {cov:>8.1%} {a_top:>7.3f} [{tlo:.3f},{thi:.3f}] "
          f"{np.mean(parts):>8.3f} {rec:>10.0%}")
pd.DataFrame(rows).to_csv(RESULTS / "r1_targeting.csv", index=False)

print("\n" + "=" * 90)
print("D. HGB BINNING LIMIT (why the previous draft overstated the ceiling)")
print("=" * 90)
from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper
a = TR[IDENT].astype(str)
codes = pd.Categorical(a, categories=pd.Index(a.value_counts().index)).codes.astype(float)
bm = _BinMapper(n_bins=256, random_state=SEED).fit(codes.reshape(-1, 1))
print(f"  distinct CI values in train: {a.nunique():,}")
print(f"  distinct values after binning: {len(np.unique(bm.transform(codes.reshape(-1,1)))):,}")
print("  -> gradient boosting on ordinal codes cannot separate the full estate;")
print("     one-hot logistic regression is used as the primary estimator.")

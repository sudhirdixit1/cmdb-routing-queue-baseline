"""E10b -- apply the practitioner's layer decomposition to BOTH tasks.

E2 reported +0.176 AUC for the configuration block on misrouting, and E6
reported +0.108 on service-target breach.  Both bundled Service Component
WBS (a service-layer attribute) with CI Name (a true CI-layer attribute),
and both used an intake baseline with no history.

The practitioner review argues service and history are the fundamental
layers and CI is an enhancer.  This tests that on both targets with the
same layered protocol, so the paper reports the decomposed number rather
than the bundled one.
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
N_BOOT = 2000

base = load_bpic14().copy()
base["_ht"] = pd.to_numeric(base["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                            errors="coerce")
base["_t"] = pd.to_datetime(base["opened_at"], errors="coerce", utc=True)
base["_ra"] = pd.to_numeric(base["reassignment_count"], errors="coerce")
base = base.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)
_o = base._t.values.astype("datetime64[ns]")
base["f_hour"] = base._t.dt.hour
base["f_dow"] = base._t.dt.dayofweek
base["f_arrivals24h"] = (np.arange(len(base))
                         - np.searchsorted(_o, _o - np.timedelta64(24, "h"),
                                           side="left"))

LAYERS = {
    "1 intake": ["Category", "Impact", "Urgency", "Priority"],
    "2 + time": ["f_hour", "f_dow", "f_arrivals24h"],
    "3 + service": ["Service Component WBS (aff)", "f_svc_hist"],
    "4 + CI": ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)", "f_ci_hist"],
}
NUMERIC = {"f_hour", "f_dow", "f_arrivals24h", "f_svc_hist", "f_ci_hist"}

TASKS = {
    "misrouting (reassigned >=1)": lambda d: (d._ra >= 1).astype(int),
    "service-target breach": None,          # threshold set per-split below
}


def encode(train, test, cols):
    Xtr = np.empty((len(train), len(cols))); Xte = np.empty((len(test), len(cols)))
    for j, c in enumerate(cols):
        if c in NUMERIC:
            Xtr[:, j] = pd.to_numeric(train[c], errors="coerce").values
            Xte[:, j] = pd.to_numeric(test[c], errors="coerce").values
        else:
            tr = train[c].astype(str).where(~is_missing(train[c]), "__M__")
            te = test[c].astype(str).where(~is_missing(test[c]), "__M__")
            cats = pd.Index(tr.value_counts().index)
            a = pd.Categorical(tr, categories=cats).codes.astype(float)
            b = pd.Categorical(te, categories=cats).codes.astype(float)
            a[a < 0] = np.nan; b[b < 0] = np.nan
            Xtr[:, j], Xte[:, j] = a, b
    return Xtr, Xte


def boot_delta(y, pa, pb, n=N_BOOT):
    rng = np.random.default_rng(SEED)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        d.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


print("=" * 92)
print("E10b  LAYER DECOMPOSITION, BOTH TASKS  (Rabobank)")
print("=" * 92)

rows = []
for task in TASKS:
    df = base.copy()
    if task.startswith("misrouting"):
        df = df.dropna(subset=["_ra"]).reset_index(drop=True)
        cut = int(len(df) * 0.70)
        train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()
        train["_y"] = (train._ra >= 1).astype(int)
        test["_y"] = (test._ra >= 1).astype(int)
    else:
        df = df.dropna(subset=["_ht"]).reset_index(drop=True)
        cut = int(len(df) * 0.70)
        train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()
        thr = train._ht.quantile(0.75)
        train["_y"] = (train._ht > thr).astype(int)
        test["_y"] = (test._ht > thr).astype(int)

    gm = train._y.mean()
    for col, name in [("Service Component WBS (aff)", "f_svc_hist"),
                      ("CI Name (aff)", "f_ci_hist")]:
        k_tr = train[col].astype(str).where(~is_missing(train[col]), "__M__")
        k_te = test[col].astype(str).where(~is_missing(test[col]), "__M__")
        st = pd.DataFrame({"k": k_tr, "y": train._y}).groupby("k").y.agg(["mean", "size"])
        enc = (st["mean"] * st["size"] + gm * 25.0) / (st["size"] + 25.0)
        train[name] = k_tr.map(enc).fillna(gm).values
        test[name] = k_te.map(enc).fillna(gm).values

    y = test._y.values
    print(f"\n{task}   (test n={len(test):,}, positive {y.mean():.1%})")
    print(f"  {'layer':16s} {'AUC':>7s} {'gain':>8s} {'95% CI':>19s}")
    cols, prev_p, prev_a = [], None, None
    for lname, add in LAYERS.items():
        cols += add
        Xtr, Xte = encode(train, test, cols)
        m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                           max_leaf_nodes=31, l2_regularization=1.0,
                                           random_state=SEED)
        m.fit(Xtr, train._y.values)
        p = m.predict_proba(Xte)[:, 1]
        a = roc_auc_score(y, p)
        if prev_p is None:
            print(f"  {lname:16s} {a:>7.3f} {'--':>8s}")
            rows.append(dict(task=task, layer=lname, auc=a, gain=np.nan))
        else:
            lo, hi = boot_delta(y, prev_p, p)
            print(f"  {lname:16s} {a:>7.3f} {a-prev_a:>+8.3f}   [{lo:+.3f},{hi:+.3f}]")
            rows.append(dict(task=task, layer=lname, auc=a, gain=a - prev_a,
                             lo=lo, hi=hi))
        prev_p, prev_a = p, a

out = pd.DataFrame(rows)
out.to_csv(RESULTS / "e10b_layers.csv", index=False)

print("\n" + "=" * 92)
print("REVISED HEADLINE")
print("=" * 92)
for task in TASKS:
    s = out[out.task == task].set_index("layer")
    svc = s.loc["3 + service", "gain"]
    ci = s.loc["4 + CI", "gain"]
    print(f"  {task}")
    print(f"    service layer contributes  {svc:+.3f}")
    print(f"    CI layer adds on top       {ci:+.3f}   "
          f"({ci/(svc+ci):.0%} of the configuration-attributable gain)")

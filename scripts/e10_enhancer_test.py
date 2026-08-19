"""E10 -- practitioner challenge: for service-target breach prediction, CI is
an enhancer rather than a prerequisite; SLA/OLA, service/offering, priority
and time history are more fundamental.

E6 measured +0.108 AUC from the configuration block, but that block bundled
CI Name with Service Component WBS, and the intake baseline had no temporal
or historical features at all.  This decomposes the gain into layers, added
in the order a practitioner would actually build them:

  1  intake            category, impact, urgency, priority
  2  + time            hour, weekday, month, live backlog at creation
  3  + service         Service Component WBS + its historical breach rate
  4  + CI              CI Name, Type, Subtype + CI historical breach rate

If layer 4 adds little once layers 2 and 3 are present, the practitioner is
right and the paper's claim must be narrowed.
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

df = load_bpic14().copy()
df["_ht"] = pd.to_numeric(df["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                          errors="coerce")
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t", "_ht"]).sort_values("_t").reset_index(drop=True)

# ---- time features (all knowable at creation) ---------------------------
df["f_hour"] = df._t.dt.hour
df["f_dow"] = df._t.dt.dayofweek
df["f_month"] = df._t.dt.month
# Arrival intensity: how many incidents opened in the preceding 24 hours.
# Uses only OPEN times, so it is knowable at creation.  A live-backlog
# feature was tried and discarded: reconstructing it offline requires close
# times, and close time = open + handle time, which is the target.
_o = df._t.values.astype("datetime64[ns]")
df["f_arrivals24h"] = (np.arange(len(df))
                       - np.searchsorted(_o, _o - np.timedelta64(24, "h"),
                                         side="left"))

cut = int(len(df) * 0.70)
train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()
thr = train._ht.quantile(0.75)
train["_y"] = (train._ht > thr).astype(int)
test["_y"] = (test._ht > thr).astype(int)

# ---- historical breach rates, smoothed, fit on TRAIN only ---------------
gm = train._y.mean()


def hist_rate(col, name, w=25.0):
    k_tr = train[col].astype(str).where(~is_missing(train[col]), "__M__")
    k_te = test[col].astype(str).where(~is_missing(test[col]), "__M__")
    st = pd.DataFrame({"k": k_tr, "y": train._y}).groupby("k").y.agg(["mean", "size"])
    enc = (st["mean"] * st["size"] + gm * w) / (st["size"] + w)
    train[name] = k_tr.map(enc).fillna(gm).values
    test[name] = k_te.map(enc).fillna(gm).values


hist_rate("Service Component WBS (aff)", "f_svc_hist")
hist_rate("CI Name (aff)", "f_ci_hist")

LAYERS = {
    "1 intake": ["Category", "Impact", "Urgency", "Priority"],
    # f_month is excluded: under a temporal split the test period covers
    # months absent from training, so it cannot generalise by construction.
    "2 + time": ["f_hour", "f_dow", "f_arrivals24h"],
    "3 + service": ["Service Component WBS (aff)", "f_svc_hist"],
    "4 + CI": ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)", "f_ci_hist"],
}
NUMERIC = {"f_hour", "f_dow", "f_month", "f_arrivals24h", "f_svc_hist", "f_ci_hist"}


def encode(cols):
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


def run(cols):
    Xtr, Xte = encode(cols)
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, train._y.values)
    return m.predict_proba(Xte)[:, 1]


def boot_delta(y, pa, pb, n=N_BOOT):
    rng = np.random.default_rng(SEED)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        d.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


print("=" * 90)
print("E10  IS CONFIGURATION DATA AN ENHANCER OR A PREREQUISITE?")
print("=" * 90)
print(f"  task: handling time > {thr:.1f}h (train p75)   "
      f"test n={len(test):,}, positive {test._y.mean():.1%}\n")
print(f"  {'layer':16s} {'feats':>5s} {'AUC':>7s} {'gain':>8s} {'95% CI':>18s}")

y = test._y.values
cols, prev_p, prev_auc = [], None, None
rows = []
for name, add in LAYERS.items():
    cols += add
    p = run(cols)
    a = roc_auc_score(y, p)
    if prev_p is None:
        print(f"  {name:16s} {len(cols):>5d} {a:>7.3f} {'--':>8s} {'':>18s}")
        rows.append(dict(layer=name, n_feat=len(cols), auc=a, gain=np.nan))
    else:
        lo, hi = boot_delta(y, prev_p, p)
        print(f"  {name:16s} {len(cols):>5d} {a:>7.3f} {a-prev_auc:>+8.3f} "
              f"  [{lo:+.3f},{hi:+.3f}]")
        rows.append(dict(layer=name, n_feat=len(cols), auc=a, gain=a - prev_auc,
                         lo=lo, hi=hi))
    prev_p, prev_auc = p, a

pd.DataFrame(rows).to_csv(RESULTS / "e10_enhancer.csv", index=False)

# counterfactual: everything EXCEPT the CI layer
no_ci = LAYERS["1 intake"] + LAYERS["2 + time"] + LAYERS["3 + service"]
p_no = run(no_ci); p_all = run(no_ci + LAYERS["4 + CI"])
lo, hi = boot_delta(y, p_no, p_all)
print("\n" + "=" * 90)
print("VERDICT")
print("=" * 90)
print(f"  without CI layer : AUC {roc_auc_score(y, p_no):.3f}")
print(f"  with CI layer    : AUC {roc_auc_score(y, p_all):.3f}")
print(f"  CI contribution  : {roc_auc_score(y,p_all)-roc_auc_score(y,p_no):+.3f} "
      f"[{lo:+.3f},{hi:+.3f}]")
print(f"\n  compare with E6, where the intake baseline carried no time or service")
print(f"  features and the whole configuration block appeared to add +0.108.")

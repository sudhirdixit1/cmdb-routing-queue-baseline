"""E3b -- separate readiness curves for the service layer and the CI layer.

E3 degraded every configuration field at once, so its curve conflated two
things that E10b has now shown are very different in value: service-level
identification (Service Component WBS) and CI-level identification (CI Name).

The practitioner anchored CSDM stages to a *CI population* rate, so the
matrix needs a curve that degrades the CI layer specifically, holding the
service layer at its observed maturity -- and, separately, a curve for the
service layer, since that is where most of the benefit lives.
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
RATES = [1.0, 0.90, 0.75, 0.65, 0.50, 0.35, 0.20, 0.10, 0.05, 0.02, 0.002, 0.0]
N_REP = 4

INTAKE = ["Category", "Impact", "Urgency", "Priority"]
TIME = ["f_hour", "f_dow", "f_arrivals24h"]
SERVICE = ["Service Component WBS (aff)"]
CI = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)"]
NUMERIC = set(TIME)

df = load_bpic14().copy()
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df["_ra"] = pd.to_numeric(df["reassignment_count"], errors="coerce")
df = df.dropna(subset=["_t", "_ra"]).sort_values("_t").reset_index(drop=True)
_o = df._t.values.astype("datetime64[ns]")
df["f_hour"] = df._t.dt.hour
df["f_dow"] = df._t.dt.dayofweek
df["f_arrivals24h"] = (np.arange(len(df))
                       - np.searchsorted(_o, _o - np.timedelta64(24, "h"), side="left"))
df["_y"] = (df._ra >= 1).astype(int)
cut = int(len(df) * 0.70)
TR, TE = df.iloc[:cut].copy(), df.iloc[cut:].copy()


def auc(train, test, cols):
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
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                       max_leaf_nodes=31, l2_regularization=1.0,
                                       random_state=SEED)
    m.fit(Xtr, train._y.values)
    return roc_auc_score(test._y.values, m.predict_proba(Xte)[:, 1])


ALL = INTAKE + TIME + SERVICE + CI
floor_no_cfg = auc(TR, TE, INTAKE + TIME)
ceiling = auc(TR, TE, ALL)
svc_only = auc(TR, TE, INTAKE + TIME + SERVICE)

print("=" * 90)
print("E3b  TWO-LAYER READINESS CURVES  (Rabobank, misrouting)")
print("=" * 90)
print(f"  intake+time only (no service, no CI)   AUC {floor_no_cfg:.3f}")
print(f"  + service layer                        AUC {svc_only:.3f}")
print(f"  + CI layer (full)                      AUC {ceiling:.3f}")


def curve(degrade_cols, hold_label, floor, ceil):
    rows = []
    print(f"\n  degrading {hold_label}")
    print(f"  {'population':>11s} {'AUC':>7s} {'retained':>10s}")
    for r in RATES:
        vals = []
        for rep in range(N_REP if 0 < r < 1 else 1):
            rng = np.random.default_rng(SEED + rep)
            tr, te = TR.copy(), TE.copy()
            for part in (tr, te):
                keep = rng.random(len(part)) < r
                for c in degrade_cols:
                    part.loc[~keep, c] = "__M__"
            vals.append(auc(tr, te, ALL))
        a = float(np.mean(vals))
        ret = (a - floor) / (ceil - floor)
        rows.append(dict(layer=hold_label, rate=r, auc=a, retained=ret))
        print(f"  {r:>10.1%} {a:>7.3f} {ret:>10.1%}")
    return rows


rows = []
rows += curve(CI, "CI layer (service held at 99.6%)", svc_only, ceiling)
rows += curve(SERVICE + CI, "service + CI together", floor_no_cfg, ceiling)
out = pd.DataFrame(rows)
out.to_csv(RESULTS / "e3b_two_layer.csv", index=False)

print("\n" + "=" * 90)
print("WHAT THIS MEANS FOR THE MATRIX ANCHOR")
print("=" * 90)
ci_curve = out[out.layer.str.startswith("CI layer")].sort_values("rate")
at65 = float(np.interp(0.65, ci_curve.rate, ci_curve.retained))
print(f"  practitioner anchored CSDM 'Walk' at 65% CI population.")
print(f"  On the CI-specific curve, 65% CI population retains {at65:.1%} of the")
print(f"  CI-attributable gain -- but the CI layer is only worth "
      f"{ceiling - svc_only:+.3f} AUC,")
print(f"  against {svc_only - floor_no_cfg:+.3f} for the service layer that sits beneath it.")
print(f"\n  So an organisation at Walk with service mapping in place already holds")
print(f"  AUC ~{svc_only:.3f} of a {ceiling:.3f} ceiling, before any CI work at all.")

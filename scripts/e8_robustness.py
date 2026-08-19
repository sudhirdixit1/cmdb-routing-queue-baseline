"""E8 -- is the configuration effect an artefact of the model or the split?

Repeats the headline Rabobank comparison across three learners and four
temporal split points.  If the effect survives all of them it is a property
of the data, not of the estimator.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))
from common import RESULTS, is_missing, load_bpic14

SEED = 20260818
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
CONFIG = ["CI Name (aff)", "CI Type (aff)", "CI Subtype (aff)",
          "Service Component WBS (aff)"]


def ordinal(train, test, cols):
    Xtr = np.empty((len(train), len(cols))); Xte = np.empty((len(test), len(cols)))
    for j, c in enumerate(cols):
        tr = train[c].astype(str).where(~is_missing(train[c]), "__M__")
        te = test[c].astype(str).where(~is_missing(test[c]), "__M__")
        cats = pd.Index(tr.value_counts().index)
        Xtr[:, j] = pd.Categorical(tr, categories=cats).codes
        Xte[:, j] = pd.Categorical(te, categories=cats).codes
    Xtr[Xtr < 0] = np.nan; Xte[Xte < 0] = np.nan
    return Xtr, Xte


def target_encode(train, test, cols, y, prior_w=20.0):
    """Smoothed target encoding fit on TRAIN only -- for the linear model."""
    Xtr = np.empty((len(train), len(cols))); Xte = np.empty((len(test), len(cols)))
    gm = y.mean()
    for j, c in enumerate(cols):
        tr = train[c].astype(str).where(~is_missing(train[c]), "__M__")
        te = test[c].astype(str).where(~is_missing(test[c]), "__M__")
        st = pd.DataFrame({"k": tr, "y": y}).groupby("k").y.agg(["mean", "size"])
        enc = (st["mean"] * st["size"] + gm * prior_w) / (st["size"] + prior_w)
        Xtr[:, j] = tr.map(enc).fillna(gm).values
        Xte[:, j] = te.map(enc).fillna(gm).values
    return Xtr, Xte


MODELS = {
    "HistGradientBoosting": lambda: HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.08, max_leaf_nodes=31,
        l2_regularization=1.0, random_state=SEED),
    "RandomForest": lambda: RandomForestClassifier(
        n_estimators=300, min_samples_leaf=5, n_jobs=-1, random_state=SEED),
    "LogisticRegression": lambda: LogisticRegression(max_iter=2000, C=1.0),
}

df = load_bpic14().copy()
df["_y"] = (pd.to_numeric(df["reassignment_count"], errors="coerce") >= 1).astype(int)
df["_t"] = pd.to_datetime(df["opened_at"], errors="coerce", utc=True)
df = df.dropna(subset=["_t"]).sort_values("_t").reset_index(drop=True)

print("=" * 94)
print("E8  ROBUSTNESS OF THE CONFIGURATION EFFECT (Rabobank)")
print("=" * 94)
print(f"{'split':>7s} {'model':22s} {'intake':>8s} {'+config':>9s} {'delta':>8s}")
rows = []
for split in (0.60, 0.70, 0.80, 0.90):
    cut = int(len(df) * split)
    train, test = df.iloc[:cut].copy(), df.iloc[cut:].copy()
    ytr, yte = train._y.values, test._y.values
    if len(np.unique(yte)) < 2:
        continue
    for mname, mk in MODELS.items():
        aucs = {}
        for cond, cols in [("intake", INTAKE), ("both", INTAKE + CONFIG)]:
            if mname == "LogisticRegression":
                Xtr, Xte = target_encode(train, test, cols, ytr)
            else:
                Xtr, Xte = ordinal(train, test, cols)
                if mname == "RandomForest":
                    Xtr = np.nan_to_num(Xtr, nan=-1); Xte = np.nan_to_num(Xte, nan=-1)
            m = mk(); m.fit(Xtr, ytr)
            aucs[cond] = roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
        d = aucs["both"] - aucs["intake"]
        rows.append(dict(split=split, model=mname, intake=aucs["intake"],
                         both=aucs["both"], delta=d))
        print(f"{split:>7.0%} {mname:22s} {aucs['intake']:>8.3f} "
              f"{aucs['both']:>9.3f} {d:>+8.3f}")
    print()

out = pd.DataFrame(rows)
out.to_csv(RESULTS / "e8_robustness.csv", index=False)
print("=" * 94)
print(f"  configuration delta across {len(out)} model x split combinations:")
print(f"    min {out.delta.min():+.3f}   median {out.delta.median():+.3f}   "
      f"max {out.delta.max():+.3f}")
print(f"    positive in {int((out.delta > 0).sum())}/{len(out)} combinations")

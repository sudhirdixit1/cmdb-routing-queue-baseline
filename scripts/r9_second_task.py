"""R9 -- does the baseline effect survive a change of prediction task?

HANDOFF section 8 names this as one of two defensible ways to add substance:
"measure a second prediction task on this log with the same baseline
discipline."  This is that measurement, and nothing more.

The claim under test is NOT "configuration data is valuable."  It is the
paper's actual thesis: that the measured value of item identity depends on
whether a free routing field is admitted to the baseline.  If that is a
property of the reassignment target alone, it is a curiosity.  If it
reproduces on an unrelated target, it is a property of the estate.

Two further targets, both available at closure and neither used as a
feature anywhere:

  reopened        the incident was reopened after resolution.  Correlation
                  with the reassignment target is +0.14, so this is close to
                  an independent failure mode.
  long-handling   handle time above the TRAINING third quartile.  Correlation
                  is +0.40 -- it partly re-measures the primary target, and
                  we report it with that caveat rather than as independent
                  evidence.

Everything else is held fixed to r4_final: same cohort, same temporal split,
same one-hot logistic estimator, same intake block, same opening queue.
Every gain is reported against the same matched-dimension null used in
r6_final -- the incident-to-item association shuffled, preserving column
count and mass profile while destroying the signal -- because adding item
identity adds thousands of indicator columns and that is not free.

CROSS-SCRIPT NOTE.  This script draws the null 50 times; r6_final draws it
100 times.  The two therefore disagree slightly on the pooled z of the ONE
row they share (reassigned, intake-only): r6 reports 28.1, this script
about 27.4.  The difference is Monte-Carlo dispersion in an estimate of the
null's mean and sd, not a disagreement about the data -- the gain itself
agrees to ten decimals.  The paper quotes r6 for that row and quotes this
script only for the two new targets, so no number appears twice with two
values.  Do not "fix" one to match the other; raise the draw count if the
agreement matters.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RAW, RESULTS, is_missing

SEED = 20260819
N_BOOT = 2000
N_NULL = 50
BQ = M.INTAKE + ["intake_group"]
LADDER = [("intake only", M.INTAKE), ("+ routing queue", BQ)]

D, counts, ACT, OPEN = M.load()

# ---------------------------------------------------------------- targets
raw = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                  encoding="latin-1")
raw = raw.loc[:, [c for c in raw.columns if not c.startswith("Unnamed")]]
raw.columns = [c.strip() for c in raw.columns]
# The blank-Incident-ID rows share one key, so the raw frame is not uniquely
# indexable.  Drop them first, then assert the join is 1:1 before relying on it.
side = raw[~is_missing(raw["Incident ID"])].drop_duplicates("Incident ID")
j = D[["Incident ID"]].merge(
    side[["Incident ID", "Reopen Time", "Handle Time (Hours)"]],
    on="Incident ID", how="left", validate="one_to_one")
assert len(j) == len(D), "join changed row count"

D["_reopen"] = (~is_missing(j["Reopen Time"])).astype(int)
_ht = pd.to_numeric(j["Handle Time (Hours)"].astype(str)
                    .str.replace(",", "."), errors="coerce")
TRn = int(len(D) * 0.70)
_q3 = _ht.iloc[:TRn].quantile(0.75)          # fit on training rows only
D["_longh"] = (_ht > _q3).astype(int)

TASKS = [("reassigned", "_y"), ("reopened", "_reopen"),
         ("long-handling", "_longh")]


def fit_pred(tr, te, cols, target, C=1.0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C).fit(X, tr[target].values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def auc(tr, te, cols, target, C=1.0):
    return roc_auc_score(te[target].values, fit_pred(tr, te, cols, target, C))


def boot(y, pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    v = np.array(v)
    return float(v.std()), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def null(tr, te, cols, target, n=N_NULL):
    """Matched-dimension null: same columns, same mass, zero information."""
    b = auc(tr, te, cols, target)
    out = []
    for rep in range(n):
        rng = np.random.default_rng(SEED + rep)
        t2, e2 = tr.copy(), te.copy()
        for p in (t2, e2):
            p["_n"] = rng.permutation(p[M.IDENT].astype(str).values)
        out.append(auc(t2, e2, cols + ["_n"], target) - b)
    return b, np.array(out)


TR, TE = M.split(D)

print("=" * 92)
print("A. TARGETS, AND HOW INDEPENDENT THEY ARE OF THE PRIMARY ONE")
print("=" * 92)
prof = []
y1 = D["_y"].values
for name, col in TASKS:
    v = D[col].values
    r = float(np.corrcoef(y1, v)[0, 1])
    prof.append(dict(task=name, n_pos=int(v.sum()), rate=float(v.mean()),
                     corr_with_reassigned=r))
    print(f"  {name:16s} positives {int(v.sum()):>7,}  rate {v.mean():.4f}  "
          f"corr with reassigned {r:+.3f}")
pd.DataFrame(prof).to_csv(RESULTS / "r9_targets.csv", index=False)
print("\n  'reopened' is close to independent; 'long-handling' is not, and is")
print("  reported below with that caveat rather than as separate evidence.")

print("\n" + "=" * 92)
print("B. THE LADDER, REPEATED ON EACH TARGET")
print("=" * 92)
rows = []
for tname, col in TASKS:
    print(f"\n  target: {tname}  (test positive rate {TE[col].mean():.3f})")
    print(f"    {'baseline':18s} {'AUC':>7s} {'+item':>7s} {'gain':>9s} "
          f"{'95% CI':>18s} {'null':>18s} {'z':>7s}")
    gains = {}
    for bname, cols in LADDER:
        b, nl = null(TR, TE, cols, col)
        pa = fit_pred(TR, TE, cols, col)
        pb = fit_pred(TR, TE, cols + [M.IDENT], col)
        af = roc_auc_score(TE[col].values, pb)
        g = af - b
        se, lo, hi = boot(TE[col].values, pa, pb)
        z = (g - nl.mean()) / np.hypot(se, nl.std())
        gains[bname] = g
        rows.append(dict(task=tname, baseline=bname, base_auc=b, with_ident=af,
                         gain=g, lo=lo, hi=hi, boot_se=se,
                         null_mean=float(nl.mean()), null_sd=float(nl.std()),
                         z_pooled=z))
        print(f"    {bname:18s} {b:>7.3f} {af:>7.3f} {g:>+9.4f}  "
              f"[{lo:+.3f},{hi:+.3f}]  {nl.mean():+.4f}+-{nl.std():.4f} "
              f"{z:>+7.1f}")
    shrink = 100 * (gains["intake only"] - gains["+ routing queue"]) / \
        gains["intake only"]
    rows[-1]["shrink_pct"] = shrink
    print(f"    -> admitting the queue removes {shrink:.0f}% of the measured "
          f"value of item identity")
R = pd.DataFrame(rows)
R.to_csv(RESULTS / "r9_ladder.csv", index=False)

print("\n" + "=" * 92)
print("C. IS THE SHRINKAGE STABLE ACROSS SPLIT POINTS?")
print("=" * 92)
stab = []
for tname, col in TASKS:
    for frac in (0.60, 0.65, 0.70, 0.75, 0.80):
        tr, te = M.split(D, frac)
        # LEAK, fixed 2026-08-20.  The long-handling threshold was the 75th
        # percentile of the FIRST 70% of rows, computed once above and reused
        # for every split.  At cuts of 0.60 and 0.65 that threshold had seen
        # rows in the split's own test half.  Refit the target definition on
        # each split's training rows before measuring that split.
        if col == "_longh":
            n_tr = int(len(D) * frac)
            q = _ht.iloc[:n_tr].quantile(0.75)
            tr = tr.copy(); te = te.copy()
            tr[col] = (_ht.iloc[:n_tr].values > q).astype(int)
            te[col] = (_ht.iloc[n_tr:].values > q).astype(int)
        g0 = auc(tr, te, M.INTAKE + [M.IDENT], col) - auc(tr, te, M.INTAKE, col)
        gq = auc(tr, te, BQ + [M.IDENT], col) - auc(tr, te, BQ, col)
        stab.append(dict(task=tname, cut=frac, gain_intake=g0, gain_queue=gq,
                         shrink_pct=100 * (g0 - gq) / g0))
    s = [r for r in stab if r["task"] == tname]
    print(f"  {tname:16s} shrinkage across splits: "
          f"{min(r['shrink_pct'] for r in s):.0f}%-"
          f"{max(r['shrink_pct'] for r in s):.0f}%")
pd.DataFrame(stab).to_csv(RESULTS / "r9_stability.csv", index=False)

print("\n" + "=" * 92)
print("D. VERDICT")
print("=" * 92)
for tname, _ in TASKS:
    sub = R[R.task == tname]
    res = (sub.z_pooled.abs() > 3).all()
    print(f"  {tname:16s} both rungs outside the null: {res}")
print("\n  The effect under test is the SHRINKAGE, not the gain.  A gain that")
print("  survives its null on a second target says configuration data helps")
print("  there too; the paper's claim is the narrower one that the measured")
print("  size of that help depends on admitting a field the desk already has.")

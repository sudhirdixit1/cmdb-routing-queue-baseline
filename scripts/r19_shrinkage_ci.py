"""R19 -- an interval on the SHRINKAGE, and a right-censoring sensitivity.

Two things a seventh referee found, both of which the paper needs.

A. THE PAPER'S TRANSFERABLE QUANTITY HAS NEVER CARRIED AN INTERVAL.
   Section 6 says "The transferable quantity is the shrinkage, not the gain",
   and section 7 says the shrinkage "reproduces on both" further targets.
   Every interval in the paper is on a GAIN.  Nobody had bootstrapped the
   shrinkage itself.  Doing so shows the replication claim outruns its
   evidence on the one target the paper argues is near-independent:
   reopening's shrinkage interval includes zero.

   That does not touch the primary result -- the reassignment shrinkage is
   comfortably resolved -- but "reproduces on both" is not what the data
   supports, and long handling correlates +0.40 with the primary target, so
   it cannot carry the replication on its own.

B. RIGHT-CENSORING AT THE EXTRACT BOUNDARY IS UNDISCUSSED.
   The paper removes 1,150 LEFT-censored incidents with an explicit
   justification and then says nothing about the mirror problem, while
   citing Weytjens and De Weerdt, whose subject it is.  Every close time in
   the file falls on or before the extract date, so incidents opened in the
   last weeks of the window cannot have long lives.  Truncating the cohort
   progressively tests whether that matters.  It does not -- which is worth
   two sentences, because a reader will ask.
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
BQ = M.INTAKE + ["intake_group"]

D, counts, ACT, OPEN = M.load()

raw = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                  encoding="latin-1")
raw = raw.loc[:, [c for c in raw.columns if not c.startswith("Unnamed")]]
raw.columns = [c.strip() for c in raw.columns]
side = raw[~is_missing(raw["Incident ID"])].drop_duplicates("Incident ID")
j = D[["Incident ID"]].merge(
    side[["Incident ID", "Reopen Time", "Handle Time (Hours)"]],
    on="Incident ID", how="left", validate="one_to_one")
D["_reopen"] = (~is_missing(j["Reopen Time"])).astype(int)
_ht = pd.to_numeric(j["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                    errors="coerce")
TRn = int(len(D) * 0.70)
D["_longh"] = (_ht > _ht.iloc[:TRn].quantile(0.75)).astype(int)

TASKS = [("reassigned", "_y"), ("reopened", "_reopen"),
         ("long-handling", "_longh")]

print("=" * 88)
print("A. A PAIRED BOOTSTRAP INTERVAL ON THE SHRINKAGE ITSELF")
print("=" * 88)
print("  Every interval in the paper is on a gain.  The quantity the paper")
print("  calls transferable is the SHRINKAGE, and it has never had one.\n")
print(f"  {'target':>16s} {'shrinkage':>10s} {'95% CI':>20s} {'P(<=0)':>8s}")
rows = []
for tname, col in TASKS:
    tr, te = M.split(D)
    yy = te[col].values

    def P(cols):
        return M.fit(tr.assign(_y=tr[col]), te.assign(_y=te[col]), cols)

    p0, pi = P(M.INTAKE), P(M.INTAKE + [M.IDENT])
    pq, pqi = P(BQ), P(BQ + [M.IDENT])
    g0 = roc_auc_score(yy, pi) - roc_auc_score(yy, p0)
    gq = roc_auc_score(yy, pqi) - roc_auc_score(yy, pq)
    shrink = 100 * (g0 - gq) / g0

    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(yy), len(yy))
        if len(np.unique(yy[i])) < 2:
            continue
        a0 = roc_auc_score(yy[i], pi[i]) - roc_auc_score(yy[i], p0[i])
        aq = roc_auc_score(yy[i], pqi[i]) - roc_auc_score(yy[i], pq[i])
        if a0 > 0:
            vals.append(100 * (a0 - aq) / a0)
    v = np.array(vals)
    lo, hi = np.percentile(v, [2.5, 97.5])
    ple = float((v <= 0).mean())
    rows.append(dict(task=tname, shrink_pct=shrink, lo=lo, hi=hi,
                     p_le_zero=ple, n_boot=len(v)))
    print(f"  {tname:>16s} {shrink:>9.1f}% {f'[{lo:.1f}, {hi:.1f}]':>20s} "
          f"{ple:>8.3f}")
S = pd.DataFrame(rows)
S.to_csv(RESULTS / "r19_shrinkage_ci.csv", index=False)

_re = S[S.task == "reopened"].iloc[0]
print(f"\n  Reopening -- the only near-independent target -- has a shrinkage")
print(f"  interval of [{_re.lo:.1f}, {_re.hi:.1f}] and P(shrinkage <= 0) = {_re.p_le_zero:.3f}.")
print("  It is NOT resolvably different from zero.  The paper must not say")
print("  the shrinkage 'reproduces' there; the honest statement is that it is")
print("  directionally consistent and unresolved, and that long handling --")
print("  which correlates +0.40 with the primary target -- cannot carry the")
print("  replication alone.")

print("\n" + "=" * 88)
print("B. RIGHT-CENSORING AT THE EXTRACT BOUNDARY")
print("=" * 88)
print("  Incidents opened near the extract date cannot have long lives, so")
print("  the target is mechanically depressed there.  Truncate and re-measure.\n")
print(f"  {'cohort ends':>14s} {'n':>8s} {'intake gain':>12s} {'+group gain':>12s} "
      f"{'shrinkage':>10s}")
cut_rows = []
for end in ("2014-03-31", "2014-03-24", "2014-03-17", "2014-03-10", "2014-03-01"):
    dd = D[D._t <= end].reset_index(drop=True)
    tr, te = M.split(dd)
    yy = te._y.values
    g0 = (roc_auc_score(yy, M.fit(tr, te, M.INTAKE + [M.IDENT]))
          - roc_auc_score(yy, M.fit(tr, te, M.INTAKE)))
    gq = (roc_auc_score(yy, M.fit(tr, te, BQ + [M.IDENT]))
          - roc_auc_score(yy, M.fit(tr, te, BQ)))
    cut_rows.append(dict(cohort_end=end, n=len(dd), gain_intake=g0,
                         gain_queue=gq, shrink_pct=100 * (g0 - gq) / g0))
    print(f"  {end:>14s} {len(dd):>8,} {g0:>+12.3f} {gq:>+12.3f} "
          f"{100*(g0-gq)/g0:>9.1f}%")
C = pd.DataFrame(cut_rows)
C.to_csv(RESULTS / "r19_right_censor.csv", index=False)
print(f"\n  Shrinkage over the truncations: {C.shrink_pct.min():.1f}% to "
      f"{C.shrink_pct.max():.1f}%.  The boundary does not")
print("  drive the result, which is worth stating rather than leaving for a")
print("  referee to ask about.")

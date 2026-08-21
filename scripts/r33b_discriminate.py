"""r33b -- CAN THE REDUCTION BE PREDICTED FROM LOG PROPERTIES?

PROTOCOL.md section 6.4.  The plan's section 3.3 says: if the reduction can be
predicted from properties measurable before any model is fitted, the paper is
a general finding rather than a list of case studies -- and says to try, and
to report the attempt even if it fails.

This is EXPLORATORY and is labelled so wherever it is reported.  There are
thirteen admitted logs.  Nothing fitted on thirteen points with five
predictors is evidence, and no in-sample R^2 from this script will be
presented as any.  What is reported is:

  A. The two-stage structure the corpus actually has.  Most logs never get as
     far as a reduction, because the entity is worth nothing to begin with:
     V(f | B_0) is at or below zero and there is nothing for the free field
     to absorb.  Stage 1 asks what distinguishes those logs.  Stage 2 asks,
     among the logs where the entity IS worth something, what predicts how
     much of it the free field takes.

  B. Per-discriminator Spearman correlations, each with a permutation test.

  C. A leave-one-out ridge fit on all discriminators at once, with its
     out-of-sample R^2 and a 2,000-shuffle permutation null.  A negative
     leave-one-out R^2 is the expected result and is reported as the result.

Outputs: results/r33b_table.csv, r33b_correlations.csv, r33b_predict.csv,
         r33b_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

t0 = time.time()
N_PERM = 2000
SEED = 20260819
DISC = ["n", "card_f", "card_g", "n_b0", "nmi_f_g", "entropy_f",
        "top1pct_share", "g_is_stamp", "events_mean", "coverage_f",
        "prevalence"]

LAD = pd.read_csv(RESULTS / "r33_ladder.csv")
DIS = pd.read_csv(RESULTS / "r33_discriminators.csv")
P = LAD[LAD.primary].copy()

T = P.merge(DIS.drop(columns=[c for c in ("domain", "n", "card_f", "card_g",
                                          "n_b0", "f", "g")
                             if c in DIS.columns]),
            on="log", how="left", suffixes=("", "_d"))
T["entity_pays"] = T.naive > 0
T["entity_pays_resolved"] = (T.get("naive_lo", pd.Series(np.nan, index=T.index))
                             > 0).fillna(False)
T["reduction_resolved"] = (T.get("reduction_lo",
                                 pd.Series(np.nan, index=T.index)) > 0).fillna(False)
T.to_csv(RESULTS / "r33b_table.csv", index=False)

print("=" * 100)
print("A. WHAT THE CORPUS ACTUALLY LOOKS LIKE")
print("=" * 100)
cols = ["log", "domain", "target", "n", "prevalence", "card_f", "card_g",
        "naive", "honest", "reduction"]
show = T[[c for c in cols if c in T.columns]].copy()
print(f"  {'log':18s} {'domain':12s} {'target':9s} {'n':>8s} {'prev':>6s} "
      f"{'card f':>7s} {'card g':>7s} {'V(f|B0)':>9s} {'V(f|B1)':>9s} "
      f"{'R':>8s}")
for _, r in show.iterrows():
    rr = f"{r.reduction:>8.3f}" if np.isfinite(r.reduction) else f"{'--':>8s}"
    print(f"  {r.log:18s} {r.domain:12s} {r.target:9s} {int(r.n):>8,} "
          f"{r.prevalence:>6.3f} {int(r.card_f):>7,} {int(r.card_g):>7,} "
          f"{r.naive:>+9.4f} {r.honest:>+9.4f} {rr}")

pays = T[T.entity_pays_resolved]
nopay = T[~T.entity_pays_resolved]
print(f"""
  {len(T)} log-target pairs from {T.log.nunique()} logs in {T.domain.nunique()} domains.
  The entity is worth something over the intake block, with its interval
  excluding zero, on {len(pays)} of them.  On the other {len(nopay)} there is nothing for
  the free field to absorb and no reduction exists to be measured.  Logs
  where that is the case: {', '.join(sorted(set(nopay.log)))}.
  The reduction's own interval excludes zero on {int(T.reduction_resolved.sum())}.""")

# ===================================================================== B
print("\n" + "=" * 100)
print("B. PER-DISCRIMINATOR CORRELATIONS  (EXPLORATORY)")
print("=" * 100)
rng = np.random.default_rng(SEED)
rows = []
for stage, sub, y, yname in (
        ("does the entity pay at all", T, T.entity_pays_resolved.astype(float),
         "V(f|B0) resolvably > 0"),
        ("how much the free field takes", pays.dropna(subset=["reduction"]),
         None, "reduction")):
    if stage.startswith("how"):
        y = sub.reduction
    if len(sub) < 4:
        print(f"\n  [{stage}] n={len(sub)}: too few points to correlate.")
        continue
    print(f"\n  [{stage}]  n={len(sub)}  outcome = {yname}")
    print(f"    {'discriminator':16s} {'rho':>7s} {'perm p':>8s}")
    for d in DISC:
        if d not in sub.columns:
            continue
        x = pd.to_numeric(sub[d], errors="coerce").astype(float)
        yy = pd.Series(np.asarray(y, dtype=float), index=sub.index)
        m = x.notna() & yy.notna()
        if m.sum() < 4 or x[m].nunique() < 2 or yy[m].nunique() < 2:
            continue
        rho = float(stats.spearmanr(x[m], yy[m]).statistic)
        null = np.array([abs(stats.spearmanr(
            rng.permutation(x[m].values), yy[m].values).statistic)
            for _ in range(500)])
        p = float((null >= abs(rho)).mean())
        rows.append(dict(stage=stage, discriminator=d, n=int(m.sum()),
                         spearman=rho, perm_p=p))
        print(f"    {d:16s} {rho:>+7.3f} {p:>8.3f}")
COR = pd.DataFrame(rows)
if len(COR):
    COR.to_csv(RESULTS / "r33b_correlations.csv", index=False)
    print(f"""
    {int((COR.perm_p < 0.05).sum())} of {len(COR)} correlations have a permutation p below 0.05.
    At {len(DISC)} discriminators over two stages that is roughly what chance
    produces, and no correction for multiplicity would leave any of them.""")

# ===================================================================== C
print("\n" + "=" * 100)
print("C. THE PREDICTION ATTEMPT  (EXPLORATORY; a negative is the expected "
      "result)")
print("=" * 100)
sub = pays.dropna(subset=["reduction"]).copy()
pred_rows = []
if len(sub) < 6:
    print(f"  n={len(sub)}: fewer than six points with a defined reduction.")
    print("  A leave-one-out fit on that is not an analysis and is not run.")
    loo_r2 = np.nan
    perm_p = np.nan
else:
    X = sub[[d for d in DISC if d in sub.columns]].apply(
        pd.to_numeric, errors="coerce").astype(float)
    X = X.loc[:, X.notna().all() & (X.nunique() > 1)]
    yv = sub.reduction.values.astype(float)

    def loo(Xa, ya):
        pred = np.empty(len(ya))
        for i in range(len(ya)):
            m = np.ones(len(ya), bool)
            m[i] = False
            sc = StandardScaler().fit(Xa[m])
            r = Ridge(alpha=1.0).fit(sc.transform(Xa[m]), ya[m])
            pred[i] = r.predict(sc.transform(Xa[~m]))[0]
        ss_res = float(((ya - pred) ** 2).sum())
        ss_tot = float(((ya - ya.mean()) ** 2).sum())
        return 1.0 - ss_res / ss_tot, pred

    loo_r2, pred = loo(X.values, yv)
    null = np.empty(N_PERM)
    for k in range(N_PERM):
        null[k] = loo(X.values, rng.permutation(yv))[0]
    perm_p = float((null >= loo_r2).mean())
    print(f"  predictors {list(X.columns)}")
    print(f"  n = {len(yv)}, p = {X.shape[1]}")
    print(f"  leave-one-out R^2 = {loo_r2:+.3f}")
    print(f"  permutation null over {N_PERM:,} shuffles: median "
          f"{np.median(null):+.3f}, 95th percentile "
          f"{np.percentile(null, 95):+.3f}")
    print(f"  p = {perm_p:.3f}")
    for lg, a, b in zip(sub.log, yv, pred):
        pred_rows.append(dict(log=lg, actual=float(a), predicted=float(b)))
    pd.DataFrame(pred_rows).to_csv(RESULTS / "r33b_predict.csv", index=False)
    print(f"\n  {'log':20s} {'actual':>8s} {'predicted':>10s}")
    for r in pred_rows:
        print(f"  {r['log']:20s} {r['actual']:>8.3f} {r['predicted']:>10.3f}")
    if loo_r2 <= 0:
        print("""
  The leave-one-out R^2 is at or below zero: the fitted model predicts the
  held-out reduction WORSE than its own mean does.  The reduction cannot be
  predicted from these log properties at this corpus size.  That is the
  result, it is reported as the result, and the paper does not present an
  in-sample fit in its place.""")
    else:
        print(f"""
  The leave-one-out R^2 is positive at {loo_r2:+.3f}, p = {perm_p:.3f}.  At n = {len(yv)} this is
  suggestive and nothing more; the paper reports it with the sample size in
  the same sentence.""")

facts = dict(
    n_pairs=len(T), n_logs=int(T.log.nunique()),
    n_domains=int(T.domain.nunique()),
    n_entity_pays=int(T.entity_pays_resolved.sum()),
    n_reduction_resolved=int(T.reduction_resolved.sum()),
    n_no_entity_value=int((~T.entity_pays_resolved).sum()),
    loo_r2=loo_r2, perm_p=perm_p,
    n_correlations=int(len(COR)),
    n_correlations_p05=int((COR.perm_p < 0.05).sum()) if len(COR) else 0,
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r33b_facts.csv", index=False)
print(f"\n  Wrote r33b_table.csv, r33b_correlations.csv, r33b_facts.csv"
      + (", r33b_predict.csv" if pred_rows else "")
      + f"  ({facts['runtime_s']:.0f}s)")

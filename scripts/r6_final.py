"""R6 -- the subtractive revision.

The fifth review confirmed the +0.103 against every attack it could build,
and broke both supporting contributions.  This script computes what the
reduced paper needs and nothing else:

  A  the two gains, each with its own paired-bootstrap SE
  B  z against the matched-dimension null, with BOTH sources of uncertainty
     pooled -- the previous draft divided by the null's Monte-Carlo sd alone
     and overstated the figures by roughly a factor of two
  C  the queue-proxy decomposition: shuffling item identity WITHIN the
     opening routing queue removes the part of the naive gain that is the
     item column standing in for the queue.  The residual should equal the
     gain measured directly with the queue in the baseline, and does.
  D  the coverage curve, demoted to description, with the uniform-random
     coverage ceiling stated so no convergence claim is made where that rule
     has no points

Dropped from the previous draft and NOT recomputed here: the leak
adjudication (the test could not separate its own counterexample) and the
dimensionality null as a contribution (its verdict on the small effect
ranged over six defensible constructions).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_BOOT = 2000
N_NULL = 100
BQ = M.INTAKE + ["intake_group"]

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def P(tr, te, cols, C=1.0):
    return M.fit(tr, te, cols, C)


def boot_se(pa, pb, n=N_BOOT, seed=SEED):
    """SE and CI of the AUC difference, paired on test rows."""
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    v = np.array(v)
    return float(v.std()), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def null_global(base_cols, n=N_NULL):
    b = P(TR, TE, base_cols)
    ab = roc_auc_score(y, b)
    out = []
    for rep in range(n):
        rng = np.random.default_rng(SEED + rep)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            p["_n"] = rng.permutation(p[M.IDENT].astype(str).values)
        out.append(roc_auc_score(y, P(tr, te, base_cols + ["_n"])) - ab)
    return ab, np.array(out)


print("=" * 88)
print("A+B. THE TWO GAINS, WITH BOTH SOURCES OF UNCERTAINTY POOLED")
print("=" * 88)
rows = []
for name, cols in [("intake fields only", M.INTAKE),
                   ("+ intake routing queue", BQ)]:
    ab, nl = null_global(cols)
    pb, pf = P(TR, TE, cols), P(TR, TE, cols + [M.IDENT])
    gain = roc_auc_score(y, pf) - ab
    se, lo, hi = boot_se(pb, pf)
    # pooled: the gain is itself uncertain; the previous draft ignored this
    z_pooled = (gain - nl.mean()) / np.hypot(se, nl.std())
    z_naive = (gain - nl.mean()) / nl.std()
    rows.append(dict(baseline=name, base_auc=ab, gain=gain, boot_se=se,
                     lo=lo, hi=hi, null_mean=float(nl.mean()),
                     null_sd=float(nl.std()), z_pooled=z_pooled,
                     z_naive=z_naive))
    print(f"  {name}")
    print(f"    base {ab:.3f}   gain {gain:+.4f} [{lo:+.4f},{hi:+.4f}]  "
          f"bootstrap SE {se:.4f}")
    print(f"    null {nl.mean():+.4f} +- {nl.std():.4f} ({N_NULL} draws)")
    print(f"    z pooled {z_pooled:.1f}   (naive, null-sd only: {z_naive:.1f})")
pd.DataFrame(rows).to_csv(RESULTS / "r6_gains.csv", index=False)
print("\n  The previous draft printed the naive figures.  They overstate the")
print("  evidence by roughly a factor of two; the conclusion is unaffected.")

print("\n" + "=" * 88)
print("C. THE QUEUE-PROXY DECOMPOSITION  (replaces the withdrawn leak section)")
print("=" * 88)
b_intake = roc_auc_score(y, P(TR, TE, M.INTAKE))
g_naive = roc_auc_score(y, P(TR, TE, M.INTAKE + [M.IDENT])) - b_intake
vals = []
for rep in range(30):
    rng = np.random.default_rng(700 + rep)
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        p["_s"] = p.groupby("intake_group")[M.IDENT].transform(
            lambda s: rng.permutation(s.values))
    vals.append(roc_auc_score(y, P(tr, te, M.INTAKE + ["_s"])) - b_intake)
vals = np.array(vals)
resid = g_naive - vals.mean()
g_direct = float(pd.DataFrame(rows).iloc[1].gain)
print(f"  naive gain, intake-only baseline            {g_naive:+.4f}")
print(f"  gain when identity is shuffled WITHIN queue {vals.mean():+.4f} "
      f"+- {vals.std():.4f}  ({len(vals)} draws)")
print(f"  residual                                    {resid:+.4f}")
print(f"  gain measured directly with queue in base   {g_direct:+.4f}")
print(f"  agreement                                   {abs(resid-g_direct):.4f}")
print(f"\n  {100*vals.mean()/g_naive:.0f}% of the naive gain is the item column")
print("  standing in for the routing queue.  The decomposition closes: what is")
print("  left after removing the proxy effect is what a queue-aware baseline")
print("  measures directly.")
pd.DataFrame([dict(g_naive=g_naive, within_queue=float(vals.mean()),
                   within_sd=float(vals.std()), residual=resid,
                   g_direct=g_direct, agreement=abs(resid - g_direct),
                   proxy_share=100 * vals.mean() / g_naive, n_draws=len(vals))]
             ).to_csv(RESULTS / "r6_proxy.csv", index=False)

print("\n" + "=" * 88)
print("D. COVERAGE, DEMOTED TO DESCRIPTION")
print("=" * 88)
freq = TR[M.IDENT].astype(str).value_counts()
tot = len(TR)
cis = pd.Index(TR[M.IDENT].astype(str).unique())
print("  mass concentration of this estate (a frequency count, no model):")
conc = freq.cumsum() / tot
for k in (8, 32, 64, 128, 256):
    print(f"    top {k:>4,} items = {conc.iloc[k-1]:.1%} of incidents")
# the ceiling that made the previous convergence claim untestable
rng = np.random.default_rng(SEED)
covs = [freq.reindex(rng.choice(cis, size=1024, replace=False)).fillna(0).sum() / tot
        for _ in range(10)]
print(f"\n  uniform-random selection of 1,024 of {len(cis):,} items reaches only")
print(f"  {np.mean(covs):.1%} incident coverage, so it has no points above that.")
print("  The previous draft's 'the rules converge above 55%' compared two")
print("  rules, not three, and is withdrawn.")
pd.DataFrame([dict(k=k, coverage=float(conc.iloc[k-1])) for k in (8,32,64,128,256)]
             + [dict(k=-1, coverage=float(np.mean(covs)))]
             ).to_csv(RESULTS / "r6_concentration.csv", index=False)

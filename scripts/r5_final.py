"""R5 -- repairs to the fifth draft after the fourth adversarial review.

Six repairs, none of which changes the surviving thesis:

 1. Every rung is now reported against a MATCHED-DIMENSION NOISE NULL: the
    incident-to-item association is shuffled, giving the same column count
    and the same mass profile with zero information.  A rung whose effect
    is inside that null is reported as not resolvable, not as an effect.
    (The previous draft's third row was inside it.)
 2. Each rung is also reported under PER-CONDITION penalty tuning, on an
    inner split of training only.
 3. The knowledge reference is examined.  NOTE (2026-08-20): this repair
    originally concluded the field was closure-valued and therefore a leak.
    That verdict is WITHDRAWN -- the identity test cannot separate its own
    counterexample, and the paper now makes no claim about the field.
 4. Field mutation counts are disclosed for every field used, including
    the paper's own intake fields, with a sensitivity analysis.
 5. Coverage comparison uses interpolation at matched coverage with 30
    draws per rule, replacing author-chosen bands.
 6. The estimator's binning limit is computed here rather than asserted.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RAW, RESULTS, is_missing

SEED = 20260819
N_NULL = 30
BQ = M.INTAKE + ["intake_group"]
BK = M.INTAKE + ["intake_group", "km_number"]
LADDER = [("intake fields only", M.INTAKE),
          ("+ intake routing queue", BQ),
          ("+ knowledge reference", BK)]

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def A(tr, te, cols, C=1.0):
    return roc_auc_score(te._y.values, M.fit(tr, te, cols, C))


def noise_null(base_cols, n=N_NULL):
    """Same columns, same mass profile, zero information."""
    b = A(TR, TE, base_cols)
    out = []
    for rep in range(n):
        rng = np.random.default_rng(SEED + rep)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            p["_n"] = rng.permutation(p[M.IDENT].astype(str).values)
        out.append(A(tr, te, base_cols + ["_n"]) - b)
    return b, np.array(out)


print("=" * 92)
print("REPAIR 1+2. EVERY RUNG AGAINST A NOISE NULL, AND UNDER TUNED PENALTY")
print("=" * 92)
print(f"  {'baseline':24s} {'gain':>8s} {'noise null':>18s} {'sd from null':>13s} "
      f"{'tuned':>8s}")
rows = []
itr, ite = M.split(TR, 0.80)
GRID = (0.1, 0.3, 1.0, 3.0, 10.0)
for name, cols in LADDER:
    b, nl = noise_null(cols)
    real = A(TR, TE, cols + [M.IDENT]) - b
    z = (real - nl.mean()) / nl.std()
    cb = max(GRID, key=lambda C: A(itr, ite, cols, C))
    cf = max(GRID, key=lambda C: A(itr, ite, cols + [M.IDENT], C))
    tuned = A(TR, TE, cols + [M.IDENT], cf) - A(TR, TE, cols, cb)
    verdict = "resolvable" if abs(z) > 3 else "NOT RESOLVABLE"
    rows.append(dict(baseline=name, base_auc=b, gain=real,
                     null_mean=float(nl.mean()), null_sd=float(nl.std()),
                     z=z, tuned_gain=tuned, C_base=cb, C_full=cf,
                     resolvable=abs(z) > 3))
    print(f"  {name:24s} {real:>+8.4f} {nl.mean():>+11.4f}+-{nl.std():.4f} "
          f"{z:>+13.1f} {tuned:>+8.4f}   {verdict}")
pd.DataFrame(rows).to_csv(RESULTS / "r5_rungs.csv", index=False)
print("\n  The first two rungs are far outside the dimensionality null.")
print("  The third is inside it: adding 2,554 columns at a fixed penalty costs")
print("  about what the measured 'effect' is, and tuning the penalty flips its")
print("  sign.  It is reported as not resolvable, not as a negative result.")

print("\n" + "=" * 92)
print("REPAIR 3. THE KNOWLEDGE REFERENCE -- WHY NEITHER TEST SETTLES IT")
print("=" * 92)
raw = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                  encoding="latin-1")
raw = raw.loc[:, [c for c in raw.columns if not c.startswith("Unnamed")]]
raw.columns = [c.strip() for c in raw.columns]
j = D[["Incident ID", "km_number"]].merge(raw[["Incident ID", "KM number"]],
                                          on="Incident ID")
ident = float((j.km_number.astype(str) == j["KM number"].astype(str)).mean())
n_int = OPEN.loc[OPEN.index.isin(D["Incident ID"]), "Interaction ID"].nunique()
print(f"  Open-row KM == closed-record KM : {ident:.6%}")
print(f"  Interaction IDs for {len(D):,} incidents : {n_int:,}  (near 1:1)")
print("\n  So the 'varies within an incident' test cannot separate these two:")
print("  it marks the knowledge reference and the interaction")
print("  key (creation-time, 1:1) identically.  Constancy is evidence of")
# CORRECTED 2026-08-20.  "The decisive test" was not decisive: section 7 of
# the paper shows the identity test cannot separate its own counterexample
# either (Interaction ID matches its closed-record column for 99.997628% of
# the single-interaction subset, against a 100.000000% pass mark).  The paper
# makes NO claim about this field, and in particular does not call it a leak.
print("  granularity, not of timing.  The identity test below is not decisive")
print("  either: Interaction ID, a creation-time key, matches its own")
print("  closed-record column for 99.997628% of the single-interaction subset.")
print("  NEITHER TEST SETTLES THE FIELD.  The paper makes no claim about it.")
pd.DataFrame([dict(km_identity=ident, n_interaction=n_int, n_incidents=len(D))]
             ).to_csv(RESULTS / "r5_leak.csv", index=False)

print("\n" + "=" * 92)
print("REPAIR 4. MUTATION DISCLOSURE FOR EVERY FIELD USED, AND SENSITIVITY")
print("=" * 92)
inwin = set(D["Incident ID"])
mut = []
for t in ["Impact Change", "Urgency Change", "Affected CI Change",
          "Service Change"]:
    s = ACT[ACT.IncidentActivity_Type == t]
    ids = set(s["Incident ID"]) & inwin
    touched = D[D["Incident ID"].isin(ids)]
    clean = D[~D["Incident ID"].isin(ids)]
    mut.append(dict(activity=t, incidents=len(ids), pct=len(ids) / len(D),
                    y_touched=touched._y.mean(), y_clean=clean._y.mean()))
    print(f"  {t:20s} {len(ids):>5,} incidents ({len(ids)/len(D):.2%})  "
          f"reassign rate {touched._y.mean():.3f} vs {clean._y.mean():.3f}")
pd.DataFrame(mut).to_csv(RESULTS / "r5_mutation.csv", index=False)

print("\n  Sensitivity of the surviving headline (+routing queue rung):")
sens = []
base_g = A(TR, TE, BQ + [M.IDENT]) - A(TR, TE, BQ)
sens.append(("as published", base_g, len(D)))
cat_only = ["Category", "intake_group"]
sens.append(("Category only (drop mutated Impact/Urgency/Priority)",
             A(TR, TE, cat_only + [M.IDENT]) - A(TR, TE, cat_only), len(D)))
mutated = set()
for t in ["Impact Change", "Urgency Change", "Affected CI Change"]:
    mutated |= set(ACT[ACT.IncidentActivity_Type == t]["Incident ID"])
clean_D = D[~D["Incident ID"].isin(mutated)].reset_index(drop=True)
ctr, cte = M.split(clean_D)
sens.append(("restricted to never-mutated incidents",
             A(ctr, cte, BQ + [M.IDENT]) - A(ctr, cte, BQ), len(clean_D)))
for label, g, n in sens:
    print(f"    {label:52s} {g:+.4f}   n={n:,}")
pd.DataFrame([dict(variant=l, gain=g, n=n) for l, g, n in sens]
             ).to_csv(RESULTS / "r5_sensitivity.csv", index=False)

print("\n" + "=" * 92)
print("REPAIR 5. MATCHED-COVERAGE COMPARISON (interpolated, 30 draws per rule)")
print("=" * 92)
a_base = A(TR, TE, BQ)
a_full = A(TR, TE, BQ + [M.IDENT])
freq = TR[M.IDENT].astype(str).value_counts()
cis = pd.Index(TR[M.IDENT].astype(str).unique())
tot = len(TR)


def subset(keep):
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        s = p[M.IDENT].astype(str)
        p["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    a = A(tr, te, BQ + ["_v"])
    return (a - a_base) / (a_full - a_base), freq.reindex(list(keep)).fillna(0).sum() / tot


curves = {}
KS = [8, 16, 32, 64, 128, 256, 512, 1024]
for rule in ["top-k", "volume-proportional", "uniform-random"]:
    pts = []
    for k in KS:
        if rule == "top-k":
            r, c = subset(set(freq.index[:k]))
            pts.append((c, r, 0.0))
        else:
            rs, cs = [], []
            p = (freq / freq.sum()).reindex(cis).fillna(0).values if rule == \
                "volume-proportional" else None
            for rep in range(N_NULL):
                rng = np.random.default_rng(SEED + rep)
                pick = (rng.choice(cis, size=min(k, len(cis)), replace=False,
                                   p=p / p.sum()) if p is not None
                        else rng.choice(cis, size=min(k, len(cis)), replace=False))
                rr, cc = subset(set(pick))
                rs.append(rr); cs.append(cc)
            pts.append((float(np.mean(cs)), float(np.mean(rs)), float(np.std(rs))))
    curves[rule] = pd.DataFrame(pts, columns=["coverage", "recovered", "sd"])
    curves[rule]["rule"] = rule
    curves[rule]["k"] = KS

allc = pd.concat(curves.values(), ignore_index=True)
allc.to_csv(RESULTS / "r5_curves.csv", index=False)

print(f"  {'coverage':>9s} " + " ".join(f"{r:>21s}" for r in curves) + "   spread")
comp = []
for cov in (0.35, 0.45, 0.55, 0.70, 0.85):
    vals = {}
    for rule, c in curves.items():
        cc = c.sort_values("coverage")
        if cov < cc.coverage.min() or cov > cc.coverage.max():
            continue
        vals[rule] = float(np.interp(cov, cc.coverage, cc.recovered))
    if len(vals) < 2:
        continue
    spread = max(vals.values()) - min(vals.values())
    comp.append(dict(coverage=cov, spread=spread, n_rules=len(vals), **vals))
    cells = " ".join(f"{vals.get(r, float('nan')):>21.3f}" for r in curves)
    print(f"  {cov:>8.0%} {cells}   {spread:>6.3f}")
C = pd.DataFrame(comp)
C.to_csv(RESULTS / "r5_matched.csv", index=False)
hi = C[C.coverage >= 0.55]
print(f"\n  max spread at coverage >= 55%: {hi.spread.max():.3f}")
print(f"  max spread below 55%:          {C[C.coverage < 0.55].spread.max():.3f}")
# WITHDRAWN 2026-08-20.  This compared TWO rules and reported it as three:
# uniform-random selection tops out near 40% coverage and has no points above
# it, so "converge above 55%" is not testable here.  r6 section D records the
# withdrawal.  The paper makes no convergence claim.
print("  -> WITHDRAWN.  Uniform-random selection reaches only ~40% coverage,")
print("     so above that this is a two-rule comparison reported as three.")
print("     The paper makes no claim that the rules converge.")
print("\n  within-rule Monte-Carlo sd (30 draws):")
for rule, c in curves.items():
    if c.sd.max() > 0:
        print(f"    {rule:22s} max sd {c.sd.max():.3f} at k={int(c.loc[c.sd.idxmax(),'k'])}")

print("\n" + "=" * 92)
print("REPAIR 6. ESTIMATOR BINNING, COMPUTED")
print("=" * 92)
s = TR[M.IDENT].astype(str)
codes = pd.Categorical(s, categories=pd.Index(s.value_counts().index)).codes
bm = _BinMapper(n_bins=256, random_state=SEED).fit(codes.reshape(-1, 1).astype(float))
nb = len(np.unique(bm.transform(codes.reshape(-1, 1).astype(float))))
print(f"  distinct items in training {s.nunique():,}; distinct bins {nb}")
pd.DataFrame([dict(n_items=int(s.nunique()), n_bins=int(nb))]
             ).to_csv(RESULTS / "r5_binning.csv", index=False)

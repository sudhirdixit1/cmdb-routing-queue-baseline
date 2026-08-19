"""E9b -- refine the CI-mediated join.

Two problems with the naive test in E9:

1. Only 559 CIs appear in both the incident and the change export, out of
   3,019 incident CIs and 8,778 change CIs.  Changes and incidents are being
   recorded against different parts of the CI namespace, which is itself a
   finding.
2. The permutation null spread mass over CIs that never receive changes,
   diluting the contrast.

This restricts the analysis to the CIs where the method would actually be
applied -- those carrying both incidents and changes -- and permutes within
that population.  It also tests the coarser Service Component grouping,
which the practitioner review suggested as the fallback when exact CI
matching is too sparse.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing, load_bpic14

SEED = 20260819
WINDOWS = [24, 72, 168]
N_PERM = 300

ch = pd.read_csv(RAW / "Detail_Change.csv", sep=";", low_memory=False,
                 encoding="latin-1")
ch = ch.loc[:, [c for c in ch.columns if not c.startswith("Unnamed")]]
ch.columns = [c.strip() for c in ch.columns]
ch["_end"] = pd.to_datetime(ch["Actual End"], errors="coerce", dayfirst=True)
ch = ch.dropna(subset=["_end"])

inc = load_bpic14().dropna(subset=["opened_at"]).copy()

print("=" * 88)
print("E9b  CI NAMESPACE ALIGNMENT AND CONDITIONAL CORRELATION")
print("=" * 88)


def analyse(key, label):
    c = ch[~is_missing(ch[key])].rename(columns={key: "k"})[["k", "_end"]]
    i = inc[~is_missing(inc[key])].rename(columns={key: "k"}).copy()
    both = set(i.k) & set(c.k)
    print(f"\n--- keyed on {label}")
    print(f"  distinct keys: incidents {i.k.nunique():,}  changes {c.k.nunique():,}"
          f"  overlap {len(both):,}")
    cov = i.k.isin(both).mean()
    print(f"  incidents whose key ever receives a change: {cov:.1%}")
    if not both:
        return []

    i = i[i.k.isin(both)].copy()
    c = c[c.k.isin(both)].sort_values("_end")
    by = {k: g["_end"].values for k, g in c.groupby("k")}
    t = i["opened_at"].values.astype("datetime64[ns]")

    def rec(keys):
        out = np.full(len(keys), np.inf)
        for n, (k, tt) in enumerate(zip(keys, t)):
            e = by.get(k)
            if e is None:
                continue
            j = np.searchsorted(e, tt)
            if j > 0:
                out[n] = (tt - e[j - 1]) / np.timedelta64(1, "h")
        return out

    obs = rec(i.k.values)
    rng = np.random.default_rng(SEED)
    null = {w: [] for w in WINDOWS}
    for _ in range(N_PERM):
        h = rec(rng.permutation(i.k.values))
        for w in WINDOWS:
            null[w].append(float((h <= w).mean()))

    print(f"  restricted to {len(i):,} incidents on {len(both):,} shared keys")
    print(f"  {'window':>8s} {'observed':>10s} {'null':>10s} {'lift':>6s} {'z':>7s}")
    out = []
    for w in WINDOWS:
        o = float((obs <= w).mean())
        nm, ns = float(np.mean(null[w])), float(np.std(null[w]))
        z = (o - nm) / ns if ns > 0 else np.nan
        out.append(dict(key=label, window_h=w, observed=o, null_mean=nm,
                        lift=o / nm if nm else np.nan, z=z, coverage=cov))
        print(f"  {w:>7d}h {o:>10.2%} {nm:>10.2%} {o/nm:>6.2f} {z:>7.1f}")
    return out


rows = []
rows += analyse("CI Name (aff)", "exact CI")
rows += analyse("Service Component WBS (aff)", "service component (coarser)")

res = pd.DataFrame(rows)
res.to_csv(RESULTS / "e9b_conditional.csv", index=False)

print("\n" + "=" * 88)
print("VERDICT")
print("=" * 88)
ex = (~is_missing(load_bpic14()["Related Change"])).mean()
best = res.sort_values("lift", ascending=False).iloc[0]
print(f"  explicit Related Change link covers            {ex:6.2%} of incidents")
for _, r in res[res.window_h == 168].iterrows():
    print(f"  CI-mediated join ({r.key:26s}) covers {r.observed:6.2%} "
          f"at 7 days, lift {r.lift:.2f}x")
print()
print("  The practitioner claim is half right: the CMDB-mediated join recovers")
print("  far more candidate pairs than the explicit link, but the elevation over")
print("  chance is small, so it is a RECALL mechanism and not a precision one.")
print("  It surfaces candidates for review; it does not identify causes.")

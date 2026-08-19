"""E9 -- practitioner challenge: the explicit incident-to-change link is not
required; correlate by time window plus affected CI instead.

E7 found that only 1.2% of Rabobank incidents carry a Related Change, and
concluded change-incident correlation is unsupported.  The practitioner
review rejects that conclusion: the sparsity is by design, and the CMDB
itself provides the join.  This tests whether that substitute path actually
recovers the signal.

Design: for each incident, find the most recent change on the SAME CI that
completed before the incident opened.  Compare the observed rate of
"recent change on this CI" against a permutation null in which incident CI
labels are shuffled, holding the incident timeline and the change history
fixed.  If changes really do induce incidents, the observed rate exceeds
the null.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing, load_bpic14

SEED = 20260819
WINDOWS = [24, 72, 168, 720]          # hours: 1 day, 3 days, 1 week, 30 days
N_PERM = 200

# ---------------------------------------------------------------- load
ch = pd.read_csv(RAW / "Detail_Change.csv", sep=";", low_memory=False,
                 encoding="latin-1")
ch = ch.loc[:, [c for c in ch.columns if not c.startswith("Unnamed")]]
ch.columns = [c.strip() for c in ch.columns]

print("=" * 88)
print("E9  CI-MEDIATED CHANGE-INCIDENT CORRELATION  (Rabobank)")
print("=" * 88)
print("\nchange timestamp availability:")
for c in ["Actual End", "Actual Start", "Change record Close Time", "Planned End"]:
    if c in ch.columns:
        t = pd.to_datetime(ch[c], errors="coerce", dayfirst=True)
        print(f"  {c:28s} parsed {t.notna().mean():6.1%}")

ch["_end"] = pd.to_datetime(ch["Actual End"], errors="coerce", dayfirst=True)
ch = ch.dropna(subset=["_end"])
ch = ch[~is_missing(ch["CI Name (aff)"])]
ch = ch.rename(columns={"CI Name (aff)": "ci"})[["ci", "_end", "Change ID"]]
print(f"\nusable changes: {len(ch):,} on {ch.ci.nunique():,} distinct CIs")

inc = load_bpic14()
inc = inc.dropna(subset=["opened_at"])
inc = inc[~is_missing(inc["CI Name (aff)"])].copy()
inc = inc.rename(columns={"CI Name (aff)": "ci"})
inc["_open"] = inc["opened_at"]
print(f"usable incidents: {len(inc):,} on {inc.ci.nunique():,} distinct CIs")
print(f"CIs appearing in both: "
      f"{len(set(inc.ci) & set(ch.ci)):,}")

# explicit link, for comparison
explicit = (~is_missing(inc["Related Change"])).mean()
print(f"\nexplicit Related Change link present on {explicit:.1%} of incidents")


# ------------------------------------------------- same-CI recency lookup
def recent_change_hours(inc_ci, inc_time, ch_by_ci):
    """Hours since the most recent completed change on this CI, or inf."""
    out = np.full(len(inc_ci), np.inf)
    for i, (ci, t) in enumerate(zip(inc_ci, inc_time)):
        ends = ch_by_ci.get(ci)
        if ends is None:
            continue
        j = np.searchsorted(ends, t)     # ends sorted; strictly before t
        if j > 0:
            out[i] = (t - ends[j - 1]) / np.timedelta64(1, "h")
    return out


ch_sorted = ch.sort_values("_end")
ch_by_ci = {ci: g["_end"].values for ci, g in ch_sorted.groupby("ci")}

inc_ci = inc.ci.values
inc_t = inc["_open"].values.astype("datetime64[ns]")
obs_h = recent_change_hours(inc_ci, inc_t, ch_by_ci)

print("\n" + "=" * 88)
print("OBSERVED vs PERMUTATION NULL  (CI labels shuffled, timeline fixed)")
print("=" * 88)
rng = np.random.default_rng(SEED)
perm_rates = {w: [] for w in WINDOWS}
for _ in range(N_PERM):
    shuffled = rng.permutation(inc_ci)
    h = recent_change_hours(shuffled, inc_t, ch_by_ci)
    for w in WINDOWS:
        perm_rates[w].append(float((h <= w).mean()))

rows = []
print(f"  {'window':>10s} {'observed':>10s} {'null mean':>10s} {'null sd':>9s} "
      f"{'lift':>7s} {'z':>8s}")
for w in WINDOWS:
    o = float((obs_h <= w).mean())
    nm, ns = float(np.mean(perm_rates[w])), float(np.std(perm_rates[w]))
    z = (o - nm) / ns if ns > 0 else np.nan
    rows.append(dict(window_h=w, observed=o, null_mean=nm, null_sd=ns,
                     lift=o / nm if nm else np.nan, z=z))
    print(f"  {w:>8d}h {o:>10.3%} {nm:>10.3%} {ns:>9.4%} {o/nm:>7.2f} {z:>8.1f}")

pd.DataFrame(rows).to_csv(RESULTS / "e9_ci_mediated_change.csv", index=False)

print("\n" + "=" * 88)
print("COVERAGE COMPARISON")
print("=" * 88)
for w in WINDOWS:
    print(f"  incidents with a same-CI change within {w:>4d}h: "
          f"{(obs_h <= w).mean():6.2%}")
print(f"  incidents with an explicit Related Change link : {explicit:6.2%}")
best = max(WINDOWS, key=lambda w: (obs_h <= w).mean())
print(f"\n  the CI-mediated join reaches "
      f"{(obs_h <= 168).mean() / explicit:.0f}x the coverage of the explicit "
      f"link at a 7-day window")

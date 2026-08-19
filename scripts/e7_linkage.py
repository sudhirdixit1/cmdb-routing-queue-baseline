"""E7 -- cross-process linkage is a separate readiness dimension from the CMDB.

Rabobank operates a mature CMDB (99.6% CI population) yet records a related
change on only 1.2% of incidents.  If that holds, then CMDB maturity and
cross-process linkage maturity are independent axes, and a whole class of
AIOps work -- change-incident correlation, problem clustering, causal RCA --
is unavailable even in the most mature instance available.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing, load_bpic14, load_uci

print("=" * 90)
print("E7  CROSS-PROCESS LINKAGE vs CMDB MATURITY")
print("=" * 90)

rows = []

# ------------------------------------------------------------- Rabobank
r = load_bpic14()
n = len(r)
ci_pop = 1 - is_missing(r["CI Name (aff)"]).mean()
chg = 1 - is_missing(r["Related Change"]).mean()
inter = 1 - is_missing(r["Related Interaction"]).mean()
n_inc = pd.to_numeric(r["# Related Incidents"], errors="coerce").fillna(0)
print(f"\nRabobank  ({n:,} incidents)")
print(f"  CI populated (affected)            {ci_pop:6.1%}")
print(f"  linked to an interaction           {inter:6.1%}")
print(f"  linked to a change                 {chg:6.1%}")
print(f"  linked to another incident         {(n_inc > 0).mean():6.1%}")
rows += [dict(org="Rabobank", link="configuration item", rate=ci_pop),
         dict(org="Rabobank", link="interaction (intake)", rate=inter),
         dict(org="Rabobank", link="change", rate=chg),
         dict(org="Rabobank", link="incident", rate=float((n_inc > 0).mean()))]

# how many changes exist that COULD be linked?
ch = pd.read_csv(RAW / "Detail_Change.csv", sep=";", low_memory=False,
                 encoding="latin-1")
ch = ch.loc[:, [c for c in ch.columns if not c.startswith("Unnamed")]]
print(f"  changes available in the same export: {len(ch):,}")
print(f"  -> the change records exist; the LINK is what is missing")

# ------------------------------------------------------------- ServiceNow
u = load_uci()
print(f"\nServiceNow-IT  ({len(u):,} incidents)")
for f, lbl in [("cmdb_ci", "configuration item"), ("rfc", "change"),
               ("problem_id", "problem"), ("caused_by", "causing incident")]:
    p = 1 - is_missing(u[f]).mean()
    print(f"  linked to a {lbl:22s} {p:6.1%}")
    rows.append(dict(org="ServiceNow-IT", link=lbl, rate=float(p)))

print(f"\nVolvoIT")
print(f"  no configuration, change, or problem reference in the export")
rows.append(dict(org="VolvoIT", link="configuration item", rate=0.0))

pd.DataFrame(rows).to_csv(RESULTS / "e7_linkage.csv", index=False)

print("\n" + "=" * 90)
print("READINESS IS TWO-DIMENSIONAL")
print("=" * 90)
print(f"  {'organisation':16s} {'CI population':>15s} {'change linkage':>16s}")
print(f"  {'VolvoIT':16s} {'absent':>15s} {'absent':>16s}")
print(f"  {'ServiceNow-IT':16s} {'0.2%':>15s} {'0.7%':>16s}")
print(f"  {'Rabobank':16s} {ci_pop:>14.1%} {chg:>15.1%}")
print()
print("  A mature CMDB does not imply usable cross-process linkage.  The most")
print("  configuration-mature instance in this study still cannot support")
print("  change-incident correlation: the change records exist in the same")
print("  export, but 98.8% of incidents carry no reference to them.")

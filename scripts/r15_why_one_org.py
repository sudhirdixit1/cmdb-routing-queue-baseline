"""R15 -- why this study is single-organisation.

"One organisation" is the paper's largest limitation and the first thing a
reviewer says.  HANDOFF section 8 names replication on a second
organisation's log as one of two defensible ways to add substance.  This
script is the answer to why that was not done, and it is a measurement
rather than an excuse.

The paper's quantity requires a log in which the AFFECTED CONFIGURATION ITEM
is recorded.  Of the three public ITSM incident logs in common use, only one
records it at any useful rate.  That is worth a sentence in the paper: the
reason a peer-reviewed measurement of the analytic value of a CMDB does not
already exist is partly that the public data to make it barely exists.

CAUTION -- this script deliberately does NOT reuse e1/e11.  Those are
withdrawn code and their cross-organisation MODELLING claims died for
reasons recorded in HANDOFF section 4.  What is recomputed here is only a
field-population rate: a descriptive statistic with no estimator, no
baseline and no null, which is not affected by any of those withdrawals.
Nothing here is a performance comparison across organisations, and none
should be added -- the three logs have different targets, different intake
schemas and different eras.
"""
import gzip
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing, population_rate

rows = []

print("=" * 88)
print("AFFECTED-ITEM POPULATION IN THE PUBLIC ITSM INCIDENT LOGS")
print("=" * 88)

# -- 1. Rabobank / BPIC 2014 (the log this paper uses) --------------------
inc = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                  encoding="latin-1")
inc.columns = [c.strip() for c in inc.columns]
inc = inc[~is_missing(inc["Incident ID"])]
rate = population_rate(inc["CI Name (aff)"])
rows.append(dict(log="BPIC 2014 (Rabobank)", system="HP Service Manager",
                 field="CI Name (aff)", incidents=len(inc), population=rate,
                 distinct=int(inc.loc[~is_missing(inc["CI Name (aff)"]),
                                      "CI Name (aff)"].nunique())))

# -- 2. UCI 498 / ServiceNow ---------------------------------------------
with zipfile.ZipFile(RAW / "incident_event_log.zip") as z:
    uci = pd.read_csv(z.open("incident_event_log.csv"), low_memory=False)
uci_inc = uci.groupby("number", as_index=False).last()
rate = population_rate(uci_inc["cmdb_ci"])
rows.append(dict(log="UCI 498 (anonymised)", system="ServiceNow",
                 field="cmdb_ci", incidents=len(uci_inc), population=rate,
                 distinct=int(uci_inc.loc[~is_missing(uci_inc["cmdb_ci"]),
                                          "cmdb_ci"].nunique())))

# -- 3. BPIC 2013 / Volvo IT ---------------------------------------------
raw = gzip.open(RAW / "BPI_Challenge_2013_incidents.xes.gz", "rt",
                encoding="utf-8", errors="replace").read()
# Take keys only from attribute elements, and only short ones: a first
# attempt matched every key="..." in the file and then tested for the
# substring "ci", which hits ordinary resource names like "Marcin" and
# "Fabricio".  Match whole words against an explicit vocabulary instead.
keys = set(re.findall(r'<[a-z]+\s+key="([^"]{1,40})"', raw))
n_traces = raw.count("<trace>")
CI_WORDS = {"ci", "cis", "config", "configuration", "asset", "component",
            "item", "cmdb"}
ci_keys = sorted(k for k in keys
                 if CI_WORDS & set(re.split(r"[^a-z]+", k.lower())))
rows.append(dict(log="BPIC 2013 (Volvo IT)", system="VINST",
                 field="; ".join(ci_keys) if ci_keys else "(no such field)",
                 incidents=n_traces, population=0.0 if not ci_keys else float("nan"),
                 distinct=0))

T = pd.DataFrame(rows)
print(f"\n  {'log':22s} {'system':18s} {'incidents':>10s} {'item field':>11s} "
      f"{'distinct':>9s}")
for _, r in T.iterrows():
    pop = "absent" if pd.isna(r.population) or r.population == 0 \
        else f"{r.population:.1%}"
    print(f"  {r.log:22s} {r.system:18s} {r.incidents:>10,} {pop:>11s} "
          f"{r.distinct if r.distinct else '-':>9}")

print(f"\n  BPIC 2013 attribute keys resembling a configuration reference: "
      f"{ci_keys if ci_keys else 'none'}")
print("\n  Only one of the three records the affected item at a rate that")
print("  supports the measurement this paper makes.  That is the reason the")
print("  study is single-organisation, and it is not a choice.")
T.to_csv(RESULTS / "r15_public_logs.csv", index=False)

u = T[T.log.str.startswith("UCI")].iloc[0]
b = T[T.log.str.startswith("BPIC 2014")].iloc[0]
print(f"\n  For the paper: {b.population:.0%} against {u.population:.2%}.")

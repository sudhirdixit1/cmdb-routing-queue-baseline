"""R16 -- what the Open-row Assignment Group actually is.

A referee challenged the paper's characterisation of its central free field.
The paper said the Open activity records "the queue the service desk routed
it to".  It does not, and this script is the evidence.

  A  the field's diversity against the other activity types
  B  agreement with the FIRST Assignment activity's group
  C  where incidents opened by the dominant group actually end up
  D  whether the real routing decision is available at creation

The finding is that the Open row's Assignment Group is the group that
RECORDED the incident -- the central service desk for two thirds of tickets
-- and not a routing destination.  The paper's language is corrected
accordingly.

This does NOT weaken the result and it does not touch a single measured
number.  The field is still on the Open row, still 100% populated, still
free, still creation-time, and still absorbs 44% of the item column's
measured value.  What changes is what it is called, which matters because
the paper's practitioner-facing sentence was built on the wrong reading.

Section D is the part that makes this a contribution rather than an
erratum: the actual routing decision happens strictly AFTER creation on
every incident that has one, so it is inadmissible as a baseline feature
under the paper's own criterion.  A reviewer's natural suggestion -- "use
the real routing field instead" -- would introduce exactly the leakage the
paper's admissibility rule exists to prevent.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

D, counts, ACT, OPEN = M.load()
A = ACT[ACT["Incident ID"].isin(set(D["Incident ID"]))].copy()
G = "Assignment Group"

print("=" * 88)
print("A. THE OPEN ROW'S GROUP IS FAR LESS DIVERSE THAN THE WORK ROWS")
print("=" * 88)
rows = []
for t in ["Open", "Assignment", "Reassignment", "Closed"]:
    s = A[A.IncidentActivity_Type == t]
    rows.append(dict(activity=t, rows=len(s), groups=int(s[G].nunique())))
    print(f"  {t:14s} {len(s):>8,} rows   {s[G].nunique():>4} distinct groups")
n_all = int(A[G].nunique())
print(f"  {'(all rows)':14s} {len(A):>8,} rows   {n_all:>4} distinct groups")
print("\n  A routing DESTINATION cannot be less diverse than the teams that")
print("  then do the work.  The Open row carries a fifth of the vocabulary.")

DOM = A[A.IncidentActivity_Type == "Open"][G].value_counts().idxmax()
op = A[A.IncidentActivity_Type == "Open"]
share_open = float((op[G] == DOM).mean())
share_all = float((A[G] == DOM).mean())
print(f"\n  {DOM} is {share_open:.1%} of Open rows but only {share_all:.1%} of all rows.")
print(f"  It looks like a desk that logs tickets, not a team that owns them.")

print("\n" + "=" * 88)
print("B. IT DISAGREES WITH THE FIRST ASSIGNMENT")
print("=" * 88)
first_open = op.sort_values("ts").groupby("Incident ID")[G].first()
asg = A[A.IncidentActivity_Type == "Assignment"].sort_values("ts")
first_asg = asg.groupby("Incident ID")[G].first()
both = first_open.index.intersection(first_asg.index)
agree = float((first_open[both] == first_asg[both]).mean())
print(f"  incidents with both an Open and an Assignment: {len(both):,}")
print(f"  Open group == first Assignment group:          {agree:.2%}")
print("\n  If the Open row recorded a routing decision, these would largely")
print("  agree.  They agree about one time in seven.")

print("\n" + "=" * 88)
print("C. WHERE THE DOMINANT GROUP'S TICKETS ACTUALLY GO")
print("=" * 88)
t8 = both[first_open[both] == DOM]
dest = first_asg[t8].value_counts(normalize=True)
print(f"  of {len(t8):,} incidents opened under {DOM}, the first assignment is:")
for g, s in dest.head(5).items():
    print(f"    {g:12s} {s:>6.1%}")
print(f"    (self: {dest.get(DOM, 0.0):.1%})")

print("\n" + "=" * 88)
print("C2. ADMISSIBILITY, RESTRICTED TO THE COHORT")
print("=" * 88)
# r4_final computes "varies within incident" over the WHOLE activity log and
# writes 92.66% to r4_admissibility.csv.  The paper quotes the COHORT figure,
# 92.56%, which until now was produced only inside verify_paper.py.  A number
# whose sole producer is the checker is not a checked number, and the results
# file a reader is pointed to showed a differently-valued twin.  Produce it
# here, next to the other facts about this field.
_v = A.groupby("Incident ID")[G].nunique()
cohort_varies = float((_v > 1).mean())
print(f"  varies within incident, cohort only  {cohort_varies:.2%}")
# The paper's companion figure, 21.35%, had the same defect: its only
# producer was verify_paper.py.  Compute it here too.
_last = A.sort_values("ts").groupby("Incident ID")[G].last()
_shared = first_open.index.intersection(_last.index)
open_is_last = float((first_open[_shared] == _last[_shared]).mean())
print(f"  Open group == last observed group    {open_is_last:.2%}")
print(f"  (r4_admissibility.csv reports 92.66% over the whole activity log;")
print("   the difference is the 1,150 left-censored incidents.)")

print("\n" + "=" * 88)
print("D. THE REAL ROUTING DECISION IS NOT AVAILABLE AT CREATION")
print("=" * 88)
o1 = op.sort_values("ts").groupby("Incident ID")["ts"].first()
a1 = asg.groupby("Incident ID")["ts"].first()
b2 = o1.index.intersection(a1.index)
delta = (a1[b2] - o1[b2]).dt.total_seconds()
after = float((delta > 0).mean())
med_min = float(delta.median() / 60.0)
no_asg = int(len(set(D["Incident ID"]) - set(first_asg.index)))
print(f"  first Assignment occurs strictly after Open: {after:.1%} of incidents")
print(f"  median delay: {med_min:,.0f} minutes")
print(f"  incidents with no Assignment activity at all: {no_asg:,} of {len(D):,}")
print("\n  So the first Assignment group fails the paper's own admissibility")
print("  criterion as a BASELINE feature: it is not observable at creation.")
print("  Substituting it would introduce the leakage the criterion prevents.")
print("  The opening group is admissible precisely because it is a property")
print("  of the intake event itself.")

pd.DataFrame([dict(
    dominant=DOM, groups_open=int(op[G].nunique()),
    groups_assignment=int(asg[G].nunique()), groups_all=n_all,
    dom_share_open=share_open, dom_share_all=share_all,
    agree_first_assignment=agree, n_both=len(both),
    cohort_varies=cohort_varies, open_is_last=open_is_last,
    first_asg_after_open=after, median_delay_min=med_min,
    n_no_assignment=no_asg, n_incidents=len(D),
)]).to_csv(RESULTS / "r16_field_semantics.csv", index=False)
pd.DataFrame(rows).to_csv(RESULTS / "r16_activity_groups.csv", index=False)

"""E1 -- configuration readiness audit across three ITSM instances."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import LOADERS, RESULTS, entropy, is_missing, population_rate

CLASS_ORDER = ["intake", "descriptive", "workflow", "configuration",
               "relational", "outcome"]

rows = []
counts = {}
for org, (loader, classmap) in LOADERS.items():
    df = loader()
    counts[org] = len(df)
    for field, cls in classmap.items():
        if field not in df.columns:
            rows.append(dict(org=org, field=field, field_class=cls,
                             present_in_export=False, population=0.0,
                             distinct=0, entropy=0.0, top1_share=float("nan")))
            continue
        s = df[field]
        nonmiss = s[~is_missing(s)]
        top1 = (nonmiss.value_counts(normalize=True).iloc[0]
                if len(nonmiss) else float("nan"))
        rows.append(dict(
            org=org, field=field, field_class=cls, present_in_export=True,
            population=population_rate(s), distinct=int(nonmiss.nunique()),
            entropy=entropy(s), top1_share=float(top1),
        ))

audit = pd.DataFrame(rows)
audit.to_csv(RESULTS / "e1_field_audit.csv", index=False)

print("=" * 78)
print("E1  CONFIGURATION READINESS AUDIT")
print("=" * 78)
for org, n in counts.items():
    print(f"  {org:15s} {n:>7,} incidents")

print("\n--- per-field detail ---")
for org in LOADERS:
    sub = audit[audit.org == org]
    print(f"\n{org}")
    print(f"  {'field':32s} {'class':14s} {'pop':>7s} {'distinct':>9s} {'H':>7s}")
    for cls in CLASS_ORDER:
        for _, r in sub[sub.field_class == cls].iterrows():
            if not r.present_in_export:
                print(f"  {r.field:32s} {cls:14s} {'ABSENT':>7s} "
                      f"{'-':>9s} {'-':>7s}")
            else:
                print(f"  {r.field:32s} {cls:14s} {r.population:>6.1%} "
                      f"{r.distinct:>9,} {r.entropy:>7.2f}")

print("\n" + "=" * 78)
print("HEADLINE  mean population rate by field class and organisation")
print("=" * 78)
piv = (audit[audit.present_in_export]
       .pivot_table(index="field_class", columns="org", values="population",
                    aggfunc="mean")
       .reindex(CLASS_ORDER))
absent = (audit[~audit.present_in_export]
          .groupby(["field_class", "org"]).size().unstack(fill_value=0))
print((piv * 100).round(1).to_string(na_rep="  -- "))
if len(absent):
    print("\nfields absent from export entirely:")
    print(absent.to_string())
piv.to_csv(RESULTS / "e1_class_by_org.csv")

print("\n" + "=" * 78)
print("GATE 1  does the configuration gap replicate across organisations?")
print("=" * 78)
for org in LOADERS:
    sub = audit[(audit.org == org) & (audit.field_class == "configuration")]
    if sub.empty or not sub.present_in_export.any():
        print(f"  {org:15s} NO CONFIGURATION FIELD IN EXPORT")
        continue
    for _, r in sub.iterrows():
        flag = ("EMPTY" if r.population < 0.10
                else "PARTIAL" if r.population < 0.90 else "POPULATED")
        print(f"  {org:15s} {r.field:28s} {r.population:>6.1%}  {flag}")

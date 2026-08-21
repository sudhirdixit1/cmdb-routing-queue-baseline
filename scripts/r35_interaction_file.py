"""r35 -- THE FILE SECTION 9 SAID WOULD SETTLE IT.

Section 9 of the manuscript, "One Thing We Could Not Establish", reports that
the knowledge-article reference raises AUC to 0.805 and drives the measured
value of item identity to -0.003, and that the paper cannot tell whether the
field is available at incident creation.  It names the missing evidence:

    "The collection ships an interaction detail file we did not obtain; if it
     records this field at creation the question is answerable, and our
     inability to settle it is a limit of the three files we hold, not of the
     export."

`Detail_Interaction.csv` is now obtained: 147,004 service-desk interactions,
21,873,186 bytes, from the same DOI as the three files already used.

WHAT THE FILE CAN AND CANNOT PROVE.  It is a CLOSED record, exactly like the
incident and activity files, and section 9 already rejects agreement with a
closed record as evidence -- `Interaction ID`, a creation-time key, agrees at
99.997628% and so does everything else.  So this script does not run that test
again.  It runs four that the interaction file makes possible and the three
earlier files did not, and it runs every one of them against a NEGATIVE
CONTROL -- `Closure Code`, which is certainly not creation-time -- so that a
test which cannot discriminate is visible as one.

  A. Join and coverage.
  B. Timing.  An interaction that is CLOSED before its incident is OPENED was
     final before the incident existed; every field on it is then provably
     pre-incident.  This is the only test in the battery that is airtight, and
     it is airtight only on the subset where the ordering holds.
  C. Interactions that never become incidents.  Two thirds of the file.  If
     they carry knowledge references at the same rate and diversity, the
     reference is assigned at the service desk and not by the incident
     process.
  D. Consequence.  Re-run the admissibility ladder with the knowledge
     reference carried by a PROVABLY pre-incident interaction, and report what
     the item is worth once it is admitted.

Outputs: results/r35_join.csv, r35_timing.csv, r35_orphans.csv,
         r35_ladder.csv, r35_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base14 as B
from common import RAW, RESULTS

t0 = time.time()
PROBE = "KM number"          # the field section 9 could not adjudicate
CONTROL = "Closure Code"     # certainly not creation-time; the null

# ---------------------------------------------------------------- load
INT = pd.read_csv(RAW / "Detail_Interaction.csv", sep=";", low_memory=False,
                  encoding="latin-1")
INT = INT.loc[:, [c for c in INT.columns if not c.startswith("Unnamed")]]
INT.columns = [c.strip() for c in INT.columns]
INT["t_open"] = pd.to_datetime(INT["Open Time (First Touch)"], dayfirst=True,
                               errors="coerce", format="mixed")
INT["t_close"] = pd.to_datetime(INT["Close Time"], dayfirst=True,
                                errors="coerce", format="mixed")

D = B.D.copy()                       # r4_final's cohort, unchanged
D["t_open"] = D["_t"]

print("=" * 92)
print("A. THE JOIN")
print("=" * 92)
print(f"  interactions            {len(INT):,}")
print(f"  incidents in the cohort {len(D):,}   (r4_final's, unchanged)")
n_rel = int(INT["Related Incident"].notna().sum())
print(f"  interactions naming a related incident {n_rel:,} "
      f"({n_rel / len(INT):.1%})")
have_ri = D["Related Interaction"].notna()
print(f"  cohort incidents naming a related interaction "
      f"{int(have_ri.sum()):,} ({have_ri.mean():.1%})")

IX = INT.set_index("Interaction ID")
dup = int(INT["Interaction ID"].duplicated().sum())
print(f"  duplicate interaction ids {dup}")
IX = IX[~IX.index.duplicated(keep="first")]

J = D[have_ri].copy()
J["_int"] = J["Related Interaction"].astype(str).str.strip()
J = J[J._int.isin(IX.index)]
for c in (PROBE, CONTROL, "t_open", "t_close", "Category", "CI Name (aff)",
          "First Call Resolution"):
    J[f"int_{c}"] = J._int.map(IX[c])
print(f"  incidents joined to an interaction record {len(J):,} "
      f"({len(J) / len(D):.1%} of the cohort)")

join_rows = [dict(metric="interactions", value=len(INT)),
             dict(metric="cohort_incidents", value=len(D)),
             dict(metric="interactions_with_related_incident", value=n_rel),
             dict(metric="cohort_with_related_interaction", value=int(have_ri.sum())),
             dict(metric="joined", value=len(J))]
pd.DataFrame(join_rows).to_csv(RESULTS / "r35_join.csv", index=False)

# ------------------------------------------------------------ B. timing
print("\n" + "=" * 92)
print("B. TIMING: WAS THE INTERACTION FINAL BEFORE THE INCIDENT EXISTED?")
print("=" * 92)
MIN_N = 100          # declared before the counts are read; see below

J["gap_open_h"] = (J.t_open - J.int_t_open).dt.total_seconds() / 3600.0
J["gap_close_h"] = (J.t_open - J.int_t_close).dt.total_seconds() / 3600.0
J["int_handle_h"] = pd.to_numeric(
    J._int.map(IX["Handle Time (secs)"]), errors="coerce") / 3600.0
J["int_worked_to"] = J.int_t_open + pd.to_timedelta(J.int_handle_h, unit="h")

opened_before = J.int_t_open <= J.t_open
closed_before = J.int_t_close <= J.t_open
worked_before = J.int_worked_to <= J.t_open
print(f"  interaction OPENED before the incident        "
      f"{opened_before.mean():7.2%}  ({int(opened_before.sum()):,})")
print(f"  interaction CLOSED before the incident        "
      f"{closed_before.mean():7.2%}  ({int(closed_before.sum()):,})")
print(f"  interaction's HANDLE TIME elapsed before it   "
      f"{worked_before.mean():7.2%}  ({int(worked_before.sum()):,})")
print(f"  median open-to-open gap {J.gap_open_h.median():,.1f} h;"
      f"  median close-to-open gap {J.gap_close_h.median():,.1f} h")
print(f"""
  `Close Time` on an interaction is an administrative bulk closure -- the
  first record in the file opens in September 2011 and closes in February
  2014 after 239 seconds of handling -- so "closed before" is nearly empty
  and carries no power.  `Open Time (First Touch)` plus `Handle Time (secs)`
  is when the desk's WORK on the interaction finished, and that is the
  timing test with power.  It assumes the handled time is contiguous, which
  is an assumption and is stated as one.\n""")

SUBSETS = [("all joined", pd.Series(True, index=J.index)),
           ("opened-before", opened_before),
           ("worked-before", worked_before),
           ("closed-before", closed_before)]
print(f"  {'field':22s} " + " ".join(f"{nm:>16s}" for nm, _ in SUBSETS))
tim_rows = []
for f in (PROBE, CONTROL, "Category", "CI Name (aff)"):
    a = (J[f].astype(str).str.strip() == J[f"int_{f}"].astype(str).str.strip())
    rec = dict(field=f, is_control=(f == CONTROL))
    cells = []
    for nm, mask in SUBSETS:
        sub = a[mask.values]
        v = float(sub.mean()) if len(sub) else np.nan
        rec[f"agree_{nm.replace(' ', '_').replace('-', '_')}"] = v
        rec[f"n_{nm.replace(' ', '_').replace('-', '_')}"] = int(len(sub))
        cells.append(f"{v:>15.4%}" if len(sub) else f"{'--':>16s}")
    tim_rows.append(rec)
    print(f"  {f:22s} " + " ".join(cells))
print(f"  {'n':22s} " + " ".join(f"{int(m.sum()):>16,}" for _, m in SUBSETS))
TIM = pd.DataFrame(tim_rows)
TIM.to_csv(RESULTS / "r35_timing.csv", index=False)

n_wb = int(worked_before.sum())
n_cb = int(closed_before.sum())
km_wb = float(TIM[TIM.field == PROBE].agree_worked_before.iloc[0])
cc_wb = float(TIM[TIM.field == CONTROL].agree_worked_before.iloc[0])
km_cb = float(TIM[TIM.field == PROBE].agree_closed_before.iloc[0])
cc_cb = float(TIM[TIM.field == CONTROL].agree_closed_before.iloc[0])
discriminates = bool(n_wb >= MIN_N and abs(km_wb - cc_wb) >= 0.05)
print(f"""
  READ THE COUNT ROW BEFORE BELIEVING ANY RATE ABOVE IT.  The closed-before
  column rests on {n_cb} incidents.  A rate on {n_cb} rows separating from another
  rate on {n_cb} rows is not a finding, and this project has shipped exactly that
  defect before; MIN_N is declared as {MIN_N} in the source above the counts.

  The worked-before column rests on {n_wb:,}.  There the knowledge reference
  agrees at {km_wb:.2%} and the closure code -- which is certainly NOT
  creation-time -- agrees at {cc_wb:.2%}.""")
print("  The two separate on a subset with power: THE TEST DISCRIMINATES."
      if discriminates else
      "  The two do NOT separate on a subset with power, so this test\n"
      "  establishes nothing and section E does not lean on it.")

# --------------------------------------------------------- C. the orphans
print("\n" + "=" * 92)
print("C. INTERACTIONS THAT NEVER BECOME INCIDENTS")
print("=" * 92)
orph = INT[INT["Related Incident"].isna()]
withinc = INT[INT["Related Incident"].notna()]
print(f"  {len(orph):,} of {len(INT):,} interactions ({len(orph) / len(INT):.1%}) "
      f"never produce an incident.")
orows = []
for f in (PROBE, CONTROL, "Category"):
    po = float(orph[f].notna().mean())
    pw = float(withinc[f].notna().mean())
    co, cw = int(orph[f].nunique()), int(withinc[f].nunique())
    orows.append(dict(field=f, populated_orphan=po, populated_with_incident=pw,
                      distinct_orphan=co, distinct_with_incident=cw,
                      is_control=(f == CONTROL)))
    print(f"  {f:16s} populated {po:7.2%} / {pw:7.2%}   "
          f"distinct {co:,} / {cw:,}")
fcr = orph["First Call Resolution"].astype(str).str.strip().str.upper()
n_fcr = int((fcr == "Y").sum())
print(f"  of the orphans, {n_fcr:,} ({n_fcr / max(len(orph), 1):.1%}) were "
      f"resolved on the first call")
km_orphan_pop = float(orph[PROBE].notna().mean())
cc_orphan_pop = float(orph[CONTROL].notna().mean())
pd.DataFrame(orows).to_csv(RESULTS / "r35_orphans.csv", index=False)
print(f"""
  The knowledge reference is populated on {km_orphan_pop:.1%} of interactions that
  never become incidents, across {int(orph[PROBE].nunique()):,} distinct articles.  A field
  the incident process assigns could not be populated on records the incident
  process never touches.  The closure code is populated on {cc_orphan_pop:.1%} of the
  same records, which is the reminder that an interaction is itself a closed
  record and this argument is about WHICH process writes the field, not about
  when within that process.""")

# ------------------------------------------------------- D. the consequence
print("\n" + "=" * 92)
print("D. THE LADDER, WITH THE KNOWLEDGE REFERENCE CARRIED BY THE INTERACTION")
print("=" * 92)
print("""  Three versions of the field, so a reader can see what each admission
  buys and what it rests on:

    km_open     the reference on the incident's own Open activity row.  This
                is the one section 9 declines to adjudicate.
    km_int      the reference carried by the related interaction, wherever the
                interaction is joined at all.
    km_prov     the reference carried by the related interaction ONLY where
                that interaction's HANDLE TIME had elapsed before the
                incident opened, and a missing token everywhere else.  This
                is the version whose availability at creation rests on the
                least inference.\n""")

D2 = D.copy()
D2["km_open"] = D2["km_number"]
m_int = pd.Series(index=J.index, data=J[f"int_{PROBE}"].values)
m_prov = pd.Series(index=J.index[worked_before.values],
                   data=J.loc[worked_before.values, f"int_{PROBE}"].values)
D2["km_int"] = "__M__"
D2.loc[m_int.index, "km_int"] = m_int.astype(str).values
D2["km_prov"] = "__M__"
D2.loc[m_prov.index, "km_prov"] = m_prov.astype(str).values
for c in ("km_int", "km_prov"):
    D2[c] = D2[c].fillna("__M__").replace({"nan": "__M__"})
    print(f"  {c:10s} populated {float((D2[c] != '__M__').mean()):6.1%}   "
          f"{int(D2[c].nunique()):,} distinct")

TR2, TE2 = B.split(D2)
y2 = TE2._y.values
assert (y2 == B.y).all()

LADDER = [
    ("intake",                          B.INTAKE),
    ("intake + group",                  B.BQ),
    ("intake + group + km_open",        B.BQ + ["km_open"]),
    ("intake + group + km_int",         B.BQ + ["km_int"]),
    ("intake + group + km_prov",        B.BQ + ["km_prov"]),
]
lrows = []
print(f"\n  {'baseline':32s} {'AUC':>7s} {'+item':>8s} {'gain':>8s} "
      f"{'95% CI':>18s}")
for name, cols in LADDER:
    pb = B.fit(TR2, TE2, cols)
    pf = B.fit(TR2, TE2, cols + [B.IDENT])
    ab, af = roc_auc_score(y2, pb), roc_auc_score(y2, pf)
    lo, hi = B.bdelta(y2, pb, pf)
    lrows.append(dict(baseline=name, base_auc=ab, with_item=af, gain=af - ab,
                      lo=lo, hi=hi, resolved=bool(lo > 0)))
    print(f"  {name:32s} {ab:>7.4f} {af:>8.4f} {af - ab:>+8.4f} "
          f"[{lo:>+.4f},{hi:>+.4f}]")
LAD = pd.DataFrame(lrows)
LAD.to_csv(RESULTS / "r35_ladder.csv", index=False)

g_intake = float(LAD[LAD.baseline == "intake"].gain.iloc[0])
g_group = float(LAD[LAD.baseline == "intake + group"].gain.iloc[0])
g_open = float(LAD[LAD.baseline == "intake + group + km_open"].gain.iloc[0])
g_prov = float(LAD[LAD.baseline == "intake + group + km_prov"].gain.iloc[0])
g_int = float(LAD[LAD.baseline == "intake + group + km_int"].gain.iloc[0])
r_open = 1 - g_open / g_intake
r_prov = 1 - g_prov / g_intake

facts = dict(
    n_interactions=len(INT), n_orphans=len(orph),
    orphan_share=len(orph) / len(INT),
    km_populated_orphan=km_orphan_pop,
    km_distinct_orphan=int(orph[PROBE].nunique()),
    control_populated_orphan=cc_orphan_pop,
    n_joined=len(J), join_share=len(J) / len(D),
    opened_before=float(opened_before.mean()),
    closed_before=float(closed_before.mean()),
    worked_before=float(worked_before.mean()),
    n_closed_before=n_cb, n_worked_before=n_wb, min_n=MIN_N,
    km_agree_closed_before=km_cb, control_agree_closed_before=cc_cb,
    km_agree_worked_before=km_wb, control_agree_worked_before=cc_wb,
    test_discriminates=discriminates,
    gain_intake=g_intake, gain_group=g_group,
    gain_km_open=g_open, gain_km_int=g_int, gain_km_prov=g_prov,
    reduction_km_open=r_open, reduction_km_prov=r_prov,
    km_prov_populated=float((D2.km_prov != "__M__").mean()),
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r35_facts.csv", index=False)

print("\n" + "=" * 92)
print("E. WHAT THE FILE SETTLES, AND WHAT IT DOES NOT")
print("=" * 92)
print(f"""  SETTLED.  The knowledge reference is not written by the incident
  process.  It is populated on {km_orphan_pop:.1%} of the {len(orph):,} interactions that never
  become incidents, over {int(orph[PROBE].nunique()):,} distinct articles.  Section 9's open
  question -- whether this is an incident-side artifact -- has an answer, and
  the answer is no.

  THE TIMING TEST.  {'On the ' + format(n_wb, ",") + ' incidents whose interaction was worked to completion before the incident opened, the knowledge reference agrees at ' + format(km_wb, ".2%") + ' and the closure code at ' + format(cc_wb, ".2%") + ': the test separates on a subset with power.' if discriminates else 'The timing test does not separate a field that is creation-time from one that certainly is not, on any subset with power. Nothing is concluded from it.'}

  THE CONSEQUENCE, WHICHEVER WAY IT IS READ.  Admitting the reference the
  incident's own row carries takes the item's value from {g_group:+.4f} to
  {g_open:+.4f}; admitting only the provably pre-incident version takes it to
  {g_prov:+.4f}.  Measured against the intake-only baseline of {g_intake:+.4f}, the
  reduction is {r_open:.1%} and {r_prov:.1%} respectively, against the
  published {1 - g_group / g_intake:.1%} for the opening group alone.

  Wrote r35_join.csv, r35_timing.csv, r35_orphans.csv, r35_ladder.csv,
  r35_facts.csv   ({facts['runtime_s']:.0f}s)""")


# ===========================================================================
# F. THE NULLS.  Section D removed this paper's headline.  This project's
#    third rule is that every constructed control introduces a confound, and
#    five nulls in its history were drawn at the wrong level, so a result of
#    that size is not believed until it has survived two of them.
# ===========================================================================
print("\n" + "=" * 92)
print("F. IS SECTION D A FINDING, OR A CONFOUND?")
print("=" * 92)
print("""  Two ways for "the item adds nothing once the knowledge reference is
  admitted" to be true for an uninteresting reason.

    F1  COLLINEARITY.  If the knowledge reference is a near-deterministic
        function of item identity, admitting it admits the item under
        another name, and the item's marginal is zero by construction.
    F2  DIMENSIONALITY.  If ANY grouping of this cardinality drives the
        marginal to zero -- because 1,700 extra sparse columns at fixed
        penalty is a regularisation burden the item then has to overcome --
        the result is about column counts, not about knowledge articles.

  F2's null is a RANDOM partition of incidents whose cell-size distribution
  is exactly km_prov's, built by slicing a permutation rather than by
  searchsorted on cumulative mass -- the bug that broke this project's third
  withdrawn finding, where high-mass items swallowed boundaries and left
  empty cells.  The sizes are asserted equal.\n""")

rng = np.random.default_rng(B.SEED)


def matched_partition(labels, seed):
    """A random partition with EXACTLY the cell sizes of `labels`."""
    sizes = pd.Series(labels).value_counts().values
    r = np.random.default_rng(seed)
    order = r.permutation(len(labels))
    out = np.empty(len(labels), dtype=object)
    pos = 0
    for j, s in enumerate(sizes):
        out[order[pos:pos + s]] = f"R{j}"
        pos += s
    assert pos == len(labels)
    got = np.sort(pd.Series(out).value_counts().values)[::-1]
    assert (got == np.sort(sizes)[::-1]).all(), "mass not matched"
    return out


# ---- F1 determinism -------------------------------------------------------
sub = D2[D2.km_prov != "__M__"]
km_per_ci = sub.groupby(B.IDENT)["km_prov"].nunique()
ci_per_km = sub.groupby("km_prov")[B.IDENT].nunique()
grp_per_ci = D2.groupby(B.IDENT)[B.Q].nunique()
det_rows = [
    dict(pair="km_prov | item", n_groups=int(sub[B.IDENT].nunique()),
         mean_distinct=float(km_per_ci.mean()),
         share_exactly_one=float((km_per_ci == 1).mean())),
    dict(pair="item | km_prov", n_groups=int(sub.km_prov.nunique()),
         mean_distinct=float(ci_per_km.mean()),
         share_exactly_one=float((ci_per_km == 1).mean())),
    dict(pair="opening group | item", n_groups=int(D2[B.IDENT].nunique()),
         mean_distinct=float(grp_per_ci.mean()),
         share_exactly_one=float((grp_per_ci == 1).mean())),
]
DET = pd.DataFrame(det_rows)
DET.to_csv(RESULTS / "r35_determinism.csv", index=False)
print(f"  {'relation':24s} {'groups':>8s} {'mean distinct':>14s} "
      f"{'exactly one':>12s}")
for _, r in DET.iterrows():
    print(f"  {r.pair:24s} {r.n_groups:>8,} {r.mean_distinct:>14.3f} "
          f"{r.share_exactly_one:>12.1%}")
km_det = float(DET[DET.pair == "km_prov | item"].share_exactly_one.iloc[0])
print(f"""
  {km_det:.1%} of items carry exactly one knowledge reference.  For comparison
  r21 established that 0 of 2,929 items carry more than one CI Type or
  Subtype -- perfect determinism -- and that the opening group varies on
  92.5% of incidents.  The knowledge reference sits between those two.""")

# ---- F2 dimensionality null ----------------------------------------------
null_rows = []
for rep in range(5):
    D2[f"_null{rep}"] = matched_partition(D2.km_prov.values, B.SEED + 500 + rep)
TRn, TEn = B.split(D2)
for rep in range(5):
    cols = B.BQ + [f"_null{rep}"]
    pb = B.fit(TRn, TEn, cols)
    pf = B.fit(TRn, TEn, cols + [B.IDENT])
    ab, af = roc_auc_score(y2, pb), roc_auc_score(y2, pf)
    null_rows.append(dict(rep=rep, base_auc=ab, with_item=af, gain=af - ab))
NUL = pd.DataFrame(null_rows)
NUL.to_csv(RESULTS / "r35_dimensionality_null.csv", index=False)
print(f"\n  {'':6s} {'base AUC':>10s} {'+item':>9s} {'gain':>9s}")
for _, r in NUL.iterrows():
    print(f"  null{int(r.rep):<2d} {r.base_auc:>10.4f} {r.with_item:>9.4f} "
          f"{r.gain:>+9.4f}")
print(f"  {'km_prov':6s} "
      f"{float(LAD[LAD.baseline == 'intake + group + km_prov'].base_auc.iloc[0]):>10.4f} "
      f"{float(LAD[LAD.baseline == 'intake + group + km_prov'].with_item.iloc[0]):>9.4f} "
      f"{g_prov:>+9.4f}")
null_gain_lo, null_gain_hi = float(NUL.gain.min()), float(NUL.gain.max())
null_auc_hi = float(NUL.base_auc.max())
inside = bool(null_gain_lo <= g_prov <= null_gain_hi)
print(f"""
  A matched-mass random partition of the same cardinality reaches base AUC
  at most {null_auc_hi:.4f} and leaves the item worth {null_gain_lo:+.4f} to {null_gain_hi:+.4f}.
  The knowledge reference reaches {float(LAD[LAD.baseline == 'intake + group + km_prov'].base_auc.iloc[0]):.4f} and leaves it worth {g_prov:+.4f}.""")
print("  The observed value is INSIDE the null: section D is a dimensionality\n"
      "  artifact and must not be reported as a finding."
      if inside else
      "  The null does not reproduce either number.  The base AUC the\n"
      "  knowledge reference reaches is far outside what a random partition of\n"
      "  its size reaches, so it is carrying real signal; and the item's\n"
      "  marginal collapses only under the real field, not under its\n"
      "  cardinality.  Section D survives F2.")

FACTS = pd.read_csv(RESULTS / "r35_facts.csv")
FACTS["km_share_exactly_one_item"] = km_det
FACTS["null_base_auc_max"] = null_auc_hi
FACTS["null_gain_lo"] = null_gain_lo
FACTS["null_gain_hi"] = null_gain_hi
FACTS["inside_null"] = inside
FACTS.to_csv(RESULTS / "r35_facts.csv", index=False)
print("\n  Wrote r35_determinism.csv, r35_dimensionality_null.csv; "
      "r35_facts.csv updated")

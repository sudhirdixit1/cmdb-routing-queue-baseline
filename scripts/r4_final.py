"""R4 -- final analysis.  Fifth rebuild, after three adversarial reviews.

The thesis is now the thing that kept breaking the previous drafts: the
measured value of a CMDB is a function of which fields the analyst admits to
the baseline, and the field-admission decision needs a criterion stated in
advance.

Method note.  Four prior claims died as artifacts of controls: feature entry
order, nominal-cardinality matching, a mass-matched null that did not match
mass, and a within-table comparison confounded by regularisation burden.  The
lesson is NOT "avoid constructed comparisons" -- that rule is what let the
fourth one through, since the control that exposes it is itself constructed.
The lesson is that every comparison, in-design or constructed, must be
checked for the confound it introduces.  So this script states its
admissibility criterion first, applies it uniformly to every candidate
field, and reports the headline under every admissible baseline.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).parent))
from common import RAW, RESULTS, is_missing

SEED = 20260819
N_BOOT = 2000
CUTOFF = "2013-10-01"
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
IDENT = "CI Name (aff)"
CLASSES = ["CI Type (aff)", "CI Subtype (aff)", "Service Component WBS (aff)"]


def load():
    d = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                    encoding="latin-1")
    d = d.loc[:, [c for c in d.columns if not c.startswith("Unnamed")]]
    d.columns = [c.strip() for c in d.columns]
    n_file = len(d)
    d = d[~is_missing(d["Incident ID"])]
    n_id = len(d)
    d["_t"] = pd.to_datetime(d["Open Time"], format="%d/%m/%Y %H:%M:%S",
                             errors="coerce", dayfirst=True)
    d["_ra"] = pd.to_numeric(d["# Reassignments"], errors="coerce")
    d["_ht"] = pd.to_numeric(d["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                             errors="coerce")
    d = d.dropna(subset=["_t", "_ra"])
    n_parse = len(d)

    a = pd.read_csv(RAW / "Detail_Incident_Activity.csv", sep=";",
                    low_memory=False, encoding="latin-1")
    a.columns = [c.strip() for c in a.columns]
    a["ts"] = pd.to_datetime(a["DateStamp"], format="%d-%m-%Y %H:%M:%S",
                             errors="coerce", dayfirst=True)
    op = (a[a.IncidentActivity_Type == "Open"].sort_values("ts")
          .groupby("Incident ID").first())
    d["intake_group"] = d["Incident ID"].map(op["Assignment Group"]).fillna("__M__")
    d["km_number"] = d["Incident ID"].map(op["KM number"]).fillna("__M__")

    d = d[d._t >= CUTOFF]
    d["_y"] = (d._ra >= 1).astype(int)
    return d.sort_values("_t").reset_index(drop=True), (n_file, n_id, n_parse), a, op


def split(d, frac=0.70):
    c = int(len(d) * frac)
    return d.iloc[:c].copy(), d.iloc[c:].copy()


def fit(tr, te, cols, C=1.0):
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C).fit(X, tr._y.values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def bdelta(y, pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


D, counts, ACT, OPEN = load()
TR, TE = split(D)
y = TE._y.values
n_file, n_id, n_parse = counts

print("=" * 92)
print("A. WHICH FIELDS MAY ENTER THE BASELINE?  (criterion stated before use)")
print("=" * 92)
print("""  Criterion.  A field carried on the Open activity row is admissible as a
  creation-time feature only if its value is a PER-EVENT observation.  The
  test is whether the field varies across the activity rows of a single
  incident.  A field constant on every activity row of every incident is
  denormalised from the incident record onto the log; its appearance on the
  Open row is an artifact of the export and carries no timing information.
  This is a property of the export, decidable without reference to any
  outcome, and we state it before applying it.\n""")
rows = []
for col in ["Assignment Group", "KM number", "Interaction ID"]:
    v = ACT.groupby("Incident ID")[col].nunique()
    varies = float((v > 1).mean())
    rows.append(dict(field=col, varies_within=varies, max_distinct=int(v.max()),
                     admissible=varies > 0))
    verdict = "ADMISSIBLE (per-event)" if varies > 0 else "denormalised -- excluded"
    print(f"  {col:20s} varies within incident {varies:7.2%}  "
          f"max {int(v.max()):>2}   {verdict}")
pd.DataFrame(rows).to_csv(RESULTS / "r4_admissibility.csv", index=False)
# CORRECTED 2026-08-20.  "Excludes" overstates what this test can do.  The
# paper (section 7) reports that the criterion CANNOT adjudicate the knowledge
# reference: constancy is evidence of granularity, not of timing, and
# Interaction ID -- a creation-time key -- is constant too.  Section B reports
# the headline under both so the reader can price the decision.
print("\n  The criterion admits the opening group.  It does NOT settle the")
print("  knowledge-article reference: constancy is evidence of granularity,")
print("  not of timing, and Interaction ID is constant for the same reason.")
print("  The paper makes no claim about that field.  Section B reports the")
print("  headline under both so the reader can price the decision.")

print("\n" + "=" * 92)
print("B. THE HEADLINE UNDER EVERY BASELINE  (this is the paper's thesis)")
print("=" * 92)
LADDER = [
    ("intake fields only", INTAKE),
    ("+ intake routing queue", INTAKE + ["intake_group"]),
    ("+ knowledge reference", INTAKE + ["intake_group", "km_number"]),
]
main = []
print(f"  {'baseline':30s} {'AUC':>7s} {'+item identity':>15s} {'gain':>9s} {'95% CI':>18s}")
for name, cols in LADDER:
    pb = fit(TR, TE, cols)
    pf = fit(TR, TE, cols + [IDENT])
    ab, af = roc_auc_score(y, pb), roc_auc_score(y, pf)
    lo, hi = bdelta(y, pb, pf)
    main.append(dict(baseline=name, base_auc=ab, with_ident=af,
                     gain=af - ab, lo=lo, hi=hi))
    print(f"  {name:30s} {ab:>7.3f} {af:>15.3f} {af-ab:>+9.3f}  [{lo:+.3f},{hi:+.3f}]")
M = pd.DataFrame(main)
M.to_csv(RESULTS / "r4_baselines.csv", index=False)

g_intake = M.iloc[0].gain; g_queue = M.iloc[1].gain; g_km = M.iloc[2].gain
print(f"\n  omitting the routing queue inflates the gain by "
      f"{100*(g_intake-g_queue)/g_queue:.0f}%")
print(f"  admitting the knowledge reference would take it to {g_km:+.3f}")
# CORRECTED 2026-08-20.  "That is the finding" pointed at a claim the paper
# disowns: the third rung is NOT resolvable (r5 REPAIR 1), so the "+0.19 to ~0"
# span is not something the paper asserts.  The paper's finding is the halving
# between the first two rungs.
print("  -> THE PAPER'S FINDING IS THE FIRST TWO RUNGS: admitting one free")
print("     field halves the measured value of item identity.  The third rung")
print("     is inside the dimensionality null and is reported as not")
print("     resolvable, not as a result.  Do not quote the +0.19-to-zero span.")

print("\n  stability of each rung across temporal splits:")
stab = []
for frac in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
    tr, te = split(D, frac)
    row = {"cut": frac}
    for name, cols in LADDER:
        pb = fit(tr, te, cols); pf = fit(tr, te, cols + [IDENT])
        row[name] = roc_auc_score(te._y.values, pf) - roc_auc_score(te._y.values, pb)
    stab.append(row)
    print(f"    cut {frac:.0%}: " + "  ".join(
        f"{k.split('+')[-1].strip()[:14]} {v:+.3f}" for k, v in row.items() if k != "cut"))
pd.DataFrame(stab).to_csv(RESULTS / "r4_stability.csv", index=False)

print("\n" + "=" * 92)
print("C. THE CLASS HIERARCHY IS STRUCTURALLY REDUNDANT  (no model involved)")
print("=" * 92)
red = []
for col in CLASSES:
    v = D.groupby(IDENT)[col].nunique()
    red.append(dict(field=col, items_with_multiple=int((v > 1).sum()),
                    n_items=int(len(v))))
    print(f"  {col:32s} items with >1 value: {int((v>1).sum()):>3} of {len(v):,}")
pd.DataFrame(red).to_csv(RESULTS / "r4_redundancy.csv", index=False)
print("\n  CI Type and CI Subtype are deterministic functions of item identity:")
print("  their indicator columns are exact sums of columns already present, so")
print("  they cannot carry information.  A previous draft measured a small")
print("  negative effect from adding them and reported it; that was the")
print("  regularisation cost of 330 collinear columns, not a property of the")
print("  taxonomy.  No measurement is needed and none is reported.")

print("\n" + "=" * 92)
print("D. RECOVERY AT MATCHED COVERAGE  (replaces an R^2 that was misspecified)")
print("=" * 92)
base_cols = INTAKE + ["intake_group"]
pb = fit(TR, TE, base_cols); a_base = roc_auc_score(y, pb)
pf = fit(TR, TE, base_cols + [IDENT]); a_full = roc_auc_score(y, pf)
freq = TR[IDENT].astype(str).value_counts()
cis = pd.Index(TR[IDENT].astype(str).unique())
tot = len(TR)


def subset_auc(keep):
    tr, te = TR.copy(), TE.copy()
    for part in (tr, te):
        s = part[IDENT].astype(str)
        part["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    a = roc_auc_score(y, fit(tr, te, base_cols + ["_v"]))
    cov_tr = freq.reindex(list(keep)).fillna(0).sum() / tot
    s_te = TE[IDENT].astype(str)
    cov_te = s_te.isin(keep).mean()
    return a, cov_tr, cov_te


pts = []
for k in (8, 16, 32, 64, 128, 256, 512, 1024):
    a, ctr, cte = subset_auc(set(freq.index[:k]))
    pts.append(dict(rule="top-k", k=k, auc=a, cov_train=ctr, cov_test=cte,
                    recovered=(a - a_base) / (a_full - a_base)))
    for rule, p in [("volume-proportional", (freq / freq.sum()).reindex(cis).fillna(0).values),
                    ("uniform-random", None)]:
        accs, covs = [], []
        for rep in range(5):
            rng = np.random.default_rng(SEED + rep)
            pick = (rng.choice(cis, size=min(k, len(cis)), replace=False,
                               p=p / p.sum()) if p is not None
                    else rng.choice(cis, size=min(k, len(cis)), replace=False))
            aa, cc, _ = subset_auc(set(pick))
            accs.append(aa); covs.append(cc)
        pts.append(dict(rule=rule, k=k, auc=float(np.mean(accs)),
                        cov_train=float(np.mean(covs)), cov_test=np.nan,
                        recovered=(float(np.mean(accs)) - a_base) / (a_full - a_base)))
P = pd.DataFrame(pts)
P.to_csv(RESULTS / "r4_coverage.csv", index=False)

print(f"  floor {a_base:.3f}   ceiling {a_full:.3f}\n")
print("  Recovery at comparable incident coverage, across three rules that each")
print("  identify a subset of items exactly:")
print(f"  {'coverage band':>16s}   {'rule':>22s} {'coverage':>9s} {'recovered':>10s}")
BANDS = [(0.28, 0.42), (0.42, 0.60), (0.65, 0.78), (0.82, 0.92)]
match = []
for lo_b, hi_b in BANDS:
    sel = P[(P.cov_train >= lo_b) & (P.cov_train < hi_b)].sort_values("cov_train")
    if sel.empty:
        continue
    spread = sel.recovered.max() - sel.recovered.min()
    for _, r in sel.iterrows():
        print(f"  {f'{lo_b:.0%}-{hi_b:.0%}':>16s}   {r.rule:>22s} "
              f"{r.cov_train:>9.1%} {r.recovered:>10.1%}")
    print(f"  {'':16s}   {'spread within band:':>22s} {'':9s} {spread:>10.1%}")
    match.append(dict(band=f"{lo_b:.0%}-{hi_b:.0%}", n=len(sel), spread=spread))
pd.DataFrame(match).to_csv(RESULTS / "r4_matched.csv", index=False)
print(f"\n  max spread across all bands: "
      f"{max(m['spread'] for m in match):.1%}")
# WITHDRAWN 2026-08-20.  This conclusion was drawn from author-chosen bands
# and did not survive r5 REPAIR 5 or r6 section D: uniform-random selection
# tops out near 40% coverage, so it has no observations where the claim was
# made.  The paper makes no convergence claim.
print("  -> WITHDRAWN.  This comparison used author-chosen bands and one of")
print("     the three rules has no observations above ~40% coverage.  The")
print("     paper makes no claim that the rules agree at matched coverage.")

print("\n  coverage drift, train -> test (top-k):")
for _, r in P[P.rule == "top-k"].iterrows():
    print(f"    k={int(r.k):>5,}  train {r.cov_train:.1%}  test {r.cov_test:.1%}  "
          f"drift {100*(r.cov_test-r.cov_train):+.1f}pp")

print("\n" + "=" * 92)
print("E. FACTS")
print("=" * 92)
n_items_train = TR[IDENT].nunique()
n_items_all = D[IDENT].nunique()
print(f"  rows {n_file:,} -> blank {n_file-n_id:,} -> unparseable {n_id-n_parse:,}"
      f" -> warm-up {n_parse-len(D):,} -> analysed {len(D):,}")
print(f"  train {len(TR):,} / test {len(TE):,}  positive {TR._y.mean():.3f}/{TE._y.mean():.3f}")
print(f"  items: {n_items_all:,} in window, {n_items_train:,} in training")
print(f"  128 items = {100*128/n_items_train:.1f}% of the training vocabulary "
      f"(the set selection is made from)")
pd.DataFrame([dict(
    n_file=n_file, n_blank=n_file-n_id, n_unparseable=n_id-n_parse,
    n_warmup=n_parse-len(D), n_analysed=len(D), n_train=len(TR), n_test=len(TE),
    pos_train=TR._y.mean(), pos_test=TE._y.mean(),
    n_items_all=n_items_all, n_items_train=n_items_train,
    pct_128=100*128/n_items_train, a_base=a_base, a_full=a_full,
)]).to_csv(RESULTS / "r4_facts.csv", index=False)

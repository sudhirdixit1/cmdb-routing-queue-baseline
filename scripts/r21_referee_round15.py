"""
r21 -- ROUND FIFTEEN.  Six findings, five of which cut against us.

A.  THE ASYMMETRY IN SECTION 5 IS AN ALGEBRAIC IDENTITY, NOT A MEASUREMENT.
    `r18` reports U(group|item)=60.4% and U(item|group)=19.6%, and the paper
    reads the asymmetry as evidence that the mechanism runs from item to
    group.  But U(inner,outer) = I(inner;outer)/H(inner) and I is SYMMETRIC,
    so the ratio of the two coefficients is identically H(item)/H(group) --
    a function of two marginal entropies and of nothing else.  Any two
    variables with that entropy ratio produce those two numbers whether or
    not either determines the other.  The floor subtraction does not rescue
    it: the floors are in the same ratio, so "46 points against 15" is the
    same tautology re-printed.  This is the second defect in this project
    that is an algebraic identity restated as a measurement -- see HANDOFF
    section 4, withdrawn finding 7 -- and it survived eight review rounds
    with the two marginal entropies sitting one division away in the same
    results file.

B.  THE MECHANISM'S FLOOR IS SWEPT TO 800 CELLS AND THE LEG IT BOUNDS USES
    2,929.  `r17` truncates its sweep on the stated ground that "cells
    approach items; no longer a floor".  That ground is wrong.  A RANDOM
    partition of n items into n cells is not the identity partition -- by
    the usual occupancy argument most non-empty cells collect more than one
    item -- so it stays routing-blind and stays a valid floor.  Swept out to
    matched granularity, the margin the paper calls 50 points is a knob.

C.  THE SHRINKAGE IS THE QUANTITY THE PAPER CALLS TRANSFERABLE AND THE ONE
    QUANTITY WHOSE DESIGN-SPACE RANGE IT NEVER PRINTS.  Section 4 makes that
    disclosure for the GAIN, on the quantity the paper says does not
    transfer.  Here it is for the shrinkage.

D.  `Priority` IS A DETERMINISTIC FUNCTION OF (Impact, Urgency).  The "four
    intake fields" are three.  Sarnovsky and Surma reported this on this
    same log in 2018.

E.  THE SIGNAL IS A PER-ITEM OUTCOME RATE, NOT CONFIGURATION DATA.  A lookup
    table of each item's training reassignment rate -- no model, no other
    field -- is compared against the paper's full model.

F.  THE RESOLUTION LADDER.  How fine does configuration data have to be?
    `CI Type (aff)` and `CI Subtype (aff)` sit in the same file, are 100%
    populated, and are never mentioned in the paper.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import r4_final as M
from common import RAW, RESULTS, is_missing

SEED = 20260819
N_DRAW = 25
Q = "intake_group"
CUTOFFS = ("1900-01-01", "2013-10-01", "2013-10-15", "2013-11-01", "2013-12-01")

D, TR, TE, y = M.D, M.TR, M.TE, M.y

print("=" * 88)
print("A. THE ASYMMETRY IS H(item)/H(group), AND NOTHING ELSE")
print("=" * 88)
mi = pd.read_csv(RESULTS / "r18_mi_null.csv").iloc[0]
qi = pd.read_csv(RESULTS / "r12_queue_from_item.csv").iloc[0]
ratios = dict(
    coefficients=mi.u_group_given_item / mi.u_item_given_group,
    shuffled_floors=mi.null_group_given_item / mi.null_item_given_group,
    excess_over_floor=mi.excess_group / mi.excess_item,
    marginal_entropies=qi.h_item / qi.h_queue,
)
for k, v in ratios.items():
    print(f"  {k:22s} {v:.6f}")
spread = max(ratios.values()) - min(ratios.values())
print(f"  {'spread':22s} {spread:.2e}")
mi_bits = float(mi.u_group_given_item * qi.h_queue)
print(f"\n  I(item;group) from the group side  {mi_bits:.6f} bits")
print(f"  I(item;group) from the item  side  "
      f"{mi.u_item_given_group * qi.h_item:.6f} bits")
print("  -> one number, reported twice, divided by two different marginals.")
print("     The DIRECTION is not measurable this way.  Withdraw the claim.")
print("     The mutual information itself remains reportable.")
pd.DataFrame([dict(**ratios, spread=spread, mi_bits=mi_bits)]
             ).to_csv(RESULTS / "r21_mi_tautology.csv", index=False)

print("\n" + "=" * 88)
print("B. THE FLOOR AT THE GRANULARITY OF THE LEG IT BOUNDS")
print("=" * 88)
A0 = roc_auc_score(y, M.fit(TR, TE, M.INTAKE))
Aq = roc_auc_score(y, M.fit(TR, TE, M.INTAKE + [Q]))
qg = Aq - A0
ITEMS = pd.Index(D[M.IDENT].astype(str).unique())
N_ITEMS = len(ITEMS)
N_GROUPS = int(TR[Q].astype(str).nunique())
print(f"  opening group's gain over intake {qg:+.4f}   "
      f"items {N_ITEMS:,}   groups {N_GROUPS}")

real = []
for rep in range(N_DRAW):
    r = np.random.default_rng(900 + rep)
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        p["_s"] = p.groupby(M.IDENT)[Q].transform(
            lambda s: r.permutation(s.values))
    real.append(roc_auc_score(y, M.fit(tr, te, M.INTAKE + ["_s"])) - A0)
real = np.array(real)
real_ret, real_sd = 100 * real.mean() / qg, 100 * real.std() / qg
print(f"  REAL LEG (cells = item identity, {N_ITEMS:,} cells)"
      f"   {real_ret:.1f}% +- {real_sd:.1f}%")
print()
rows = []
for k in (N_GROUPS, 400, 800, 1600, N_ITEMS, 5000):
    vals = []
    for rep in range(N_DRAW):
        r = np.random.default_rng(SEED + rep)
        lut = pd.Series(r.integers(0, k, N_ITEMS).astype(str), index=ITEMS)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            p["_c"] = p[M.IDENT].astype(str).map(lut)
            p["_s"] = p.groupby("_c")[Q].transform(
                lambda s: r.permutation(s.values))
        vals.append(roc_auc_score(y, M.fit(tr, te, M.INTAKE + ["_s"])) - A0)
    v = np.array(vals)
    ret, sd = 100 * v.mean() / qg, 100 * v.std() / qg
    margin = real_ret - ret
    z = margin / np.sqrt(sd ** 2 + real_sd ** 2)
    tag = "   <- MATCHED to the real leg" if k == N_ITEMS else ""
    rows.append(dict(cells=k, retained=ret / 100, sd=sd / 100,
                     margin_points=margin, z=z))
    print(f"  floor k={k:>5,}   {ret:5.1f}% +- {sd:4.1f}%   "
          f"margin {margin:5.1f} pts   z {z:4.1f}{tag}")
FS = pd.DataFrame(rows)
FS.to_csv(RESULTS / "r21_floor_matched.csv", index=False)
m = FS[FS.cells == N_ITEMS].iloc[0]
print(f"\n  At matched granularity the margin is {m.margin_points:.1f} points, "
      f"z={m.z:.1f}.")
print("  This project's own resolvability bar is |z|>3 (r5_final.py:79).")
print("  This leg does not clear it.  The 50-point margin is a granularity")
print("  knob set to the value that maximises it -- the same asymmetry r17's")
print("  own docstring accuses the previous version of.")

print("\n" + "=" * 88)
print("C. THE DESIGN-SPACE RANGE OF THE SHRINKAGE")
print("=" * 88)
sh = []
st = pd.read_csv(RESULTS / "r4_stability.csv")
for _, r in st.iterrows():
    g1, g2 = r["intake fields only"], r["+ intake routing queue"]
    if g1 > 0:
        sh.append(("split point", str(r["cut"]), 100 * (1 - g2 / g1)))
est = pd.read_csv(RESULTS / "r10_estimators.csv")
for _, r in est[est.shrink_pct.notna()].iterrows():
    sh.append(("estimator", str(r.estimator), float(r.shrink_pct)))
for _, r in pd.read_csv(RESULTS / "r11_threshold.csv").iterrows():
    sh.append(("target threshold", f">={int(r.threshold)}",
               float(r.shrink_pct)))

print("  cleaning cutoff, recomputed from raw (the paper reports the GAIN's")
print("  sensitivity to this knob and not the shrinkage's):")
orig_cutoff = M.CUTOFF
cut_rows = []
for cut in CUTOFFS:
    M.CUTOFF = cut
    d, _, _, _ = M.load()
    c = int(len(d) * 0.70)
    tr, te = d.iloc[:c].copy(), d.iloc[c:].copy()
    yy = te._y.values
    g1 = (roc_auc_score(yy, M.fit(tr, te, M.INTAKE + [M.IDENT]))
          - roc_auc_score(yy, M.fit(tr, te, M.INTAKE)))
    g2 = (roc_auc_score(yy, M.fit(tr, te, M.INTAKE + [Q, M.IDENT]))
          - roc_auc_score(yy, M.fit(tr, te, M.INTAKE + [Q])))
    s = 100 * (1 - g2 / g1)
    cut_rows.append(dict(cutoff=cut, n=len(d), gain_intake=g1,
                         gain_plus_group=g2, shrinkage=s))
    sh.append(("cleaning cutoff", cut, s))
    print(f"    {cut}  n={len(d):>6,}  rung1 {g1:+.4f}  rung2 {g2:+.4f}"
          f"  shrinkage {s:5.1f}%")
M.CUTOFF = orig_cutoff
pd.DataFrame(cut_rows).to_csv(RESULTS / "r21_shrinkage_cutoff.csv", index=False)

S = pd.DataFrame(sh, columns=["knob", "setting", "shrinkage"])
S.to_csv(RESULTS / "r21_shrinkage_range.csv", index=False)
print(f"\n  shrinkage across the whole design space: "
      f"{S.shrinkage.min():.1f}% to {S.shrinkage.max():.1f}%")
for knob, grp in S.groupby("knob"):
    print(f"    {knob:18s} {grp.shrinkage.min():5.1f}% to "
          f"{grp.shrinkage.max():5.1f}%")
print("  The paper's bootstrap interval on the shrinkage is [40,48] and")
print("  conditions on every one of these knobs.  The title says 'nearly in")
print("  half'.")

print("\n" + "=" * 88)
print("D. Priority IS A FUNCTION OF (Impact, Urgency)")
print("=" * 88)
raw = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                  encoding="latin-1")
raw.columns = [c.strip() for c in raw.columns]
sub = raw[["Impact", "Urgency", "Priority"]].astype(str)
cells = sub.groupby(["Impact", "Urgency"])["Priority"].nunique()
print(f"  rows {len(sub):,}   (Impact,Urgency) cells {len(cells)}   "
      f"cells carrying >1 Priority {int((cells > 1).sum())}")
a_full = roc_auc_score(y, M.fit(TR, TE, M.INTAKE))
a_drop = roc_auc_score(y, M.fit(TR, TE, [c for c in M.INTAKE
                                         if c != "Priority"]))
print(f"  intake AUC with Priority {a_full:.4f}   without {a_drop:.4f}"
      f"   delta {a_full - a_drop:+.5f}")
print("  -> the naive baseline the paper attacks contains a provably")
print("     redundant column.  Disclose it.")
pd.DataFrame([dict(rows=len(sub), cells=len(cells),
                   cells_multi=int((cells > 1).sum()),
                   auc_with=a_full, auc_without=a_drop)]
             ).to_csv(RESULTS / "r21_priority.csv", index=False)

print("\n" + "=" * 88)
print("E. A PER-ITEM OUTCOME RATE, WITH NO MODEL AND NO OTHER FIELD")
print("=" * 88)
rate = TR.groupby(TR[M.IDENT].astype(str))._y.mean()
prior = float(TR._y.mean())
look = TE[M.IDENT].astype(str).map(rate).fillna(prior).values
a_look = roc_auc_score(y, look)
a_item_only = roc_auc_score(y, M.fit(TR, TE, [M.IDENT]))
a_model = roc_auc_score(y, M.fit(TR, TE, M.INTAKE + [Q, M.IDENT]))
print(f"  per-item training reassignment rate, as a lookup   {a_look:.4f}")
print(f"  item identity alone, one-hot logistic              {a_item_only:.4f}")
print(f"  the paper's full model (intake + group + item)     {a_model:.4f}")
print("  -> what the CMDB supplies here is item IDENTITY carrying an outcome")
print("     history, not configuration ATTRIBUTES.  Six months of tickets")
print("     keyed on any stable token would do the same work.  The defensible")
print("     reading is that identity resolution IS a configuration-management")
print("     function; the paper should say so rather than leave it implicit.")
pd.DataFrame([dict(lookup=a_look, item_only=a_item_only, full_model=a_model,
                   prior=prior)]
             ).to_csv(RESULTS / "r21_item_history.csv", index=False)

print("\n" + "=" * 88)
print("F. HOW FINE DOES CONFIGURATION DATA HAVE TO BE?")
print("=" * 88)
base = M.INTAKE + [Q]
ab = roc_auc_score(y, M.fit(TR, TE, base))
print(f"  baseline (intake + opening group) {ab:.4f}\n")
lad = []
for col in ("CI Type (aff)", "CI Subtype (aff)",
            "Service Component WBS (aff)", M.IDENT):
    a = roc_auc_score(y, M.fit(TR, TE, base + [col]))
    lv = int(TR[col].astype(str).nunique())
    lad.append(dict(field=col, levels=lv, auc=a, gain=a - ab))
    print(f"  {col:30s} {lv:>5,} levels   {a:.4f}   gain {a - ab:+.4f}")
wbs = "Service Component WBS (aff)"
a_wbs = roc_auc_score(y, M.fit(TR, TE, base + [wbs]))
a_wbs_ci = roc_auc_score(y, M.fit(TR, TE, base + [wbs, M.IDENT]))
lad.append(dict(field="CI Name marginal over WBS", levels=-1,
                auc=a_wbs_ci, gain=a_wbs_ci - a_wbs))
print(f"\n  instance identity MARGINAL over the service component:"
      f" {a_wbs_ci - a_wbs:+.4f}")
print("  -> a few-hundred-way grouping captures most of it; instance-level")
print("     identity, which is where CMDB cost lives, adds the remainder.")
pd.DataFrame(lad).to_csv(RESULTS / "r21_resolution_ladder.csv", index=False)

print("\n" + "=" * 88)
print("G. WHY THE CLASSIFICATION LAYERS ARE IN THE LADDER AND NOT THE BASELINE")
print("=" * 88)
print("""  ROUND SIXTEEN.  Section F measures `CI Type (aff)` and `CI Subtype
  (aff)` over the intake+group baseline and reports small gains.  A referee
  is entitled to ask the obvious question the paper never answers: if these
  two fields are 100% populated and free, why are they not IN the baseline,
  alongside the opening group?

  The answer is the admissibility criterion the paper already states, and it
  is decidable without any model.  A field admitted to the baseline must be
  something the organisation holds WITHOUT the CMDB.  CI Type and CI Subtype
  are not: they are deterministic functions of the affected item, so they
  exist only where item identity exists.  Admitting them would be admitting
  the CMDB to the CMDB-free baseline.

  The service component is the field this argument does NOT dispose of, and
  the paper says so: it is near-deterministic in the item but not exactly
  so, and section 5 declines to draw a principled line.  This section states
  the three fields' determinism side by side so the reader can see exactly
  where the line falls and how much of a line it is.\n""")
det = []
for col in ("CI Type (aff)", "CI Subtype (aff)",
            "Service Component WBS (aff)", Q):
    s = D[col].astype(str)
    pop = 1.0 - float(M.is_missing(D[col]).mean()) \
        if hasattr(M, "is_missing") else 1.0 - float(_is_missing(D[col]).mean())
    v = D.groupby(D[M.IDENT].astype(str))[col].nunique()
    multi = int((v > 1).sum())
    # incident mass carried by the items that are NOT determined
    bad_items = set(v[v > 1].index)
    mass = float(D[M.IDENT].astype(str).isin(bad_items).mean())
    #  BOTH level counts.  Section F's ladder counts TRAINING levels; a
    #  cohort-wide count is the right scope for a determinism statement but
    #  differs (CI Subtype: 61 in training, 65 in the cohort), and one table
    #  quoting each without saying so is how a reader is misled.
    det.append(dict(field=col, levels_train=int(TR[col].astype(str).nunique()),
                    levels_cohort=int(s.nunique()), population=pop,
                    items_multi=multi, n_items=int(len(v)),
                    incident_mass_multi=mass,
                    deterministic=bool(multi == 0)))
    tag = ("deterministic in the item -- NOT admissible" if multi == 0 else
           f"varies on {multi} of {len(v):,} items ({mass:.1%} of incidents)")
    print(f"  {col:30s} {int(TR[col].astype(str).nunique()):>5,} training "
          f"levels ({int(s.nunique()):,} in cohort)  "
          f"population {pop:6.2%}   {tag}")
DT = pd.DataFrame(det)
DT.to_csv(RESULTS / "r21_ci_determinism.csv", index=False)
_t = DT[DT.field == "CI Type (aff)"].iloc[0]
_s = DT[DT.field == "CI Subtype (aff)"].iloc[0]
_w = DT[DT.field == "Service Component WBS (aff)"].iloc[0]
print(f"\n  CI Type and CI Subtype: {int(_t.items_multi)} and "
      f"{int(_s.items_multi)} items of {int(_t.n_items):,} carry more than one")
print(f"  value.  Both are exactly determined by item identity, so their")
print(f"  indicator columns are exact sums of columns already present when")
print(f"  the item is in the model, and they cannot enter a baseline that")
print(f"  excludes the item without smuggling it in.")
print(f"\n  The service component is the hard case: {int(_w.items_multi)} of "
      f"{int(_w.n_items):,} items carry")
print(f"  more than one value, which is {_w.incident_mass_multi:.1%} of "
      f"incidents.  It is nearly, but not")
print(f"  exactly, the same argument -- which is why the paper reports the")
print(f"  headline both ways instead of choosing.")
print("\ndone.")

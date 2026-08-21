"""r38 -- THE ERA LIMITATION, DECOMPOSED INTO FOUR MEASURABLE AXES.

The manuscript's Limitations concede that practice has moved since 2014 and
then stop.  That is an apology.  2026 data cannot be obtained, but "practice
has moved" is not one claim -- it is four, and each one has a proxy in the
data already held.  PLAN-STRONG-ACCEPT.md section 5.4 names them; this script
measures them.

  A  discovery tooling auto-populates a large fraction of a modern estate
     -> read r36's population curve from the top instead of the bottom.
  B  event-driven incidents arrive with the item already stamped
     -> the interaction file records whether the item was on the originating
        service-desk record.  It is a direct measurement of "arrives
        pre-stamped", in 2014.
  C  service mapping, not item identity, is where the spend goes
     -> the resolution ladder is exactly that measurement.
  D  more intake channels, fewer central desks
     -> 66% of this cohort opens at one desk.  Vary that share by
        subsampling and re-measure the ladder at each.

Every axis is reported whether or not it helps.

Outputs: results/r38_axisA.csv, r38_axisB.csv, r38_axisC.csv, r38_axisD.csv,
         r38_facts.csv
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
D = B.D.copy()
TR, TE = B.split(D)
y = B.y
CENTRAL_SHARES = (0.00, 0.20, 0.40, 0.66, 0.80, 0.95)
N_SEEDS = 3
facts = {}


def ladder(d, label=""):
    """The two-rung ladder on an arbitrary cohort, split 70/30 in time."""
    tr, te = B.split(d)
    yy = te._y.values
    if len(np.unique(yy)) < 2 or len(te) < 200:
        return None
    a_b0 = roc_auc_score(yy, B.fit(tr, te, B.INTAKE))
    a_b0f = roc_auc_score(yy, B.fit(tr, te, B.INTAKE + [B.IDENT]))
    a_bg = roc_auc_score(yy, B.fit(tr, te, B.BQ))
    a_bgf = roc_auc_score(yy, B.fit(tr, te, B.BQ + [B.IDENT]))
    vn, vh = a_b0f - a_b0, a_bgf - a_bg
    return dict(label=label, n=len(d), n_test=len(te),
                prevalence=float(yy.mean()),
                auc_b0=a_b0, auc_b0f=a_b0f, auc_b0g=a_bg, auc_b0gf=a_bgf,
                naive=vn, honest=vh,
                reduction=(1 - vh / vn) if vn > 0 else np.nan)


# ============================================================= A
print("=" * 92)
print("A. DISCOVERY AUTO-POPULATES THE ESTATE")
print("=" * 92)
cur_p = RESULTS / "r36_curve.csv"
if not cur_p.exists():
    print("  r36_curve.csv not present; run r36_population_ablation.py first.")
    AX_A = pd.DataFrame()
else:
    CUR = pd.read_csv(cur_p)
    full = CUR[CUR.regime == "full"].iloc[0]
    rows = []
    for regime in ("random", "rare-first", "common-first"):
        s = CUR[CUR.regime == regime].sort_values("level")
        top = s[s.level >= 0.75]
        if len(top) < 1:
            continue
        # slope of the group-aware increment per 10 points of population,
        # measured between 75% and 100%
        x = np.append(top.actual_population.values, full.actual_population)
        z = np.append(top.honest.values, full.honest)
        slope = float(np.polyfit(x, z, 1)[0]) / 10.0
        rows.append(dict(regime=regime, slope_per_10pts=slope,
                         honest_at_75=float(s[s.level == 0.75].honest.iloc[0]),
                         honest_at_100=float(full.honest)))
        print(f"  {regime:14s} increment at 75% population "
              f"{float(s[s.level == 0.75].honest.iloc[0]):+.4f}, at 100% "
              f"{float(full.honest):+.4f};  "
              f"{slope:+.5f} AUC per 10 points of population")
    AX_A = pd.DataFrame(rows)
    AX_A.to_csv(RESULTS / "r38_axisA.csv", index=False)
    print(f"""
  This cohort's register is ALREADY 100% populated.  Discovery tooling
  cannot move a measurement taken at the top of its own curve, so on this
  axis {full.honest:+.4f} is an upper bound and not a lower one -- which is the
  opposite of what the Limitations section currently implies by calling the
  full population unrepresentative.  What a modern estate changes is the
  MIX of what is populated, and that is regime, not level: at half
  population the increment is {float(CUR[(CUR.regime == 'rare-first') & (CUR.level == 0.5)].honest.iloc[0]):+.4f} if the tail is missing and
  {float(CUR[(CUR.regime == 'common-first') & (CUR.level == 0.5)].honest.iloc[0]):+.4f} if the core is.""")

# ============================================================= B
print("\n" + "=" * 92)
print("B. INCIDENTS ARRIVE WITH THE ITEM ALREADY STAMPED")
print("=" * 92)
INT = pd.read_csv(RAW / "Detail_Interaction.csv", sep=";", low_memory=False,
                  encoding="latin-1")
INT = INT.loc[:, [c for c in INT.columns if not c.startswith("Unnamed")]]
INT.columns = [c.strip() for c in INT.columns]
IX = INT.set_index("Interaction ID")
IX = IX[~IX.index.duplicated(keep="first")]

d = D.copy()
d["_int"] = d["Related Interaction"].astype(str).str.strip()
d["_int_ci"] = d._int.map(IX["CI Name (aff)"])
joined = d._int.isin(IX.index)
same = (d[B.IDENT].astype(str).str.strip()
        == d._int_ci.astype(str).str.strip()) & joined
no_int = ~joined
print(f"  cohort {len(d):,}")
print(f"  joined to a service-desk interaction        {int(joined.sum()):,} "
      f"({joined.mean():.2%})")
print(f"  item ALREADY on that interaction            {int(same.sum()):,} "
      f"({same.mean():.2%} of the cohort, "
      f"{same.sum() / max(int(joined.sum()), 1):.2%} of joins)")
print(f"  no interaction at all (raised elsewhere)    {int(no_int.sum()):,} "
      f"({no_int.mean():.2%})")

rows = []
for label, mask in (("item pre-stamped on the interaction", same.values),
                    ("item differs from the interaction", (joined & ~same).values),
                    ("no originating interaction", no_int.values)):
    sub = d[mask]
    r = ladder(sub, label) if len(sub) >= 500 else None
    if r is None:
        print(f"  [{label}] n={len(sub):,}: too small for a ladder; "
              f"target rate {float(sub._y.mean()) if len(sub) else float('nan'):.3f}")
        rows.append(dict(label=label, n=len(sub),
                         prevalence=float(sub._y.mean()) if len(sub) else np.nan,
                         naive=np.nan, honest=np.nan, reduction=np.nan,
                         too_small=True))
    else:
        r["too_small"] = False
        rows.append(r)
        print(f"  [{label}] n={r['n']:,}  naive {r['naive']:+.4f}  "
              f"honest {r['honest']:+.4f}  reduction {r['reduction']:.3f}")
AX_B = pd.DataFrame(rows)
AX_B.to_csv(RESULTS / "r38_axisB.csv", index=False)
print(f"""
  In 2014, on this estate, {same.sum() / max(int(joined.sum()), 1):.1%} of incidents that came through the
  service desk ALREADY carried the item their originating call carried.  A
  2026 change that pre-stamps arrivals is a change from {same.sum() / max(int(joined.sum()), 1):.1%} to at most
  100%, not from nothing to everything.

  The one public log with an intake-channel field, UCI 498, records
  contact_type as `Phone` for 99.1% of its incidents, so the channel-mix
  question cannot be measured there either.  That is a documented negative
  and not an omission.""")

# ============================================================= C
print("\n" + "=" * 92)
print("C. SERVICE MAPPING RATHER THAN ITEM IDENTITY")
print("=" * 92)
tr, te = TR, TE
a_bg = roc_auc_score(y, B.fit(tr, te, B.BQ))
rows = []
for col in ["CI Type (aff)", "CI Subtype (aff)", "Service Component WBS (aff)",
            B.IDENT]:
    a = roc_auc_score(y, B.fit(tr, te, B.BQ + [col]))
    rows.append(dict(level=col, cardinality=int(D[col].nunique()),
                     auc=a, gain_over_group=a - a_bg))
    print(f"  {col:32s} card {int(D[col].nunique()):>6,}  AUC {a:.4f}  "
          f"over intake+group {a - a_bg:+.4f}")
wbs = [r for r in rows if r["level"] == "Service Component WBS (aff)"][0]
item = [r for r in rows if r["level"] == B.IDENT][0]
a_both = roc_auc_score(y, B.fit(tr, te, B.BQ + ["Service Component WBS (aff)",
                                                B.IDENT]))
marg = a_both - wbs["auc"]
rows.append(dict(level="item marginal over service component", cardinality=-1,
                 auc=a_both, gain_over_group=marg))
AX_C = pd.DataFrame(rows)
AX_C.to_csv(RESULTS / "r38_axisC.csv", index=False)
# r21 counts TRAINING levels (256 and 2,554); the table above counts levels
# in the whole cohort (272 and 2,929).  Both are correct counts of different
# things and r21's own source records that it reports both.  The sentence
# below therefore reads its numbers from the table rather than restating a
# figure computed elsewhere on a different set of rows.
n_wbs = int(D["Service Component WBS (aff)"].nunique())
n_item = int(D[B.IDENT].nunique())
n_wbs_tr = int(TR["Service Component WBS (aff)"].astype(str).nunique())
n_item_tr = int(TR[B.IDENT].astype(str).nunique())
print(f"""
  The service component -- {n_wbs} values in this cohort, {n_wbs_tr} of them present in
  training -- reaches {wbs['gain_over_group']:+.4f} over intake + group; the item, at {n_item:,} and
  {n_item_tr:,}, reaches {item['gain_over_group']:+.4f}, so the service component captures
  {wbs['gain_over_group'] / item['gain_over_group']:.1%} of it.  The item's marginal over the service component
  is {marg:+.4f}.  A 2026 organisation that spends on service mapping rather
  than item-level curation is buying the larger share of the two, and this
  is the measurement that says so.

  READ THE LADDER FILE, NOT THE CHART.  The model holding BOTH the service
  component and the item scores {a_both:.4f}, BELOW the model holding only the
  item at {item['auc']:.4f}.  Subtracting two points off an axis gives a different
  quantity from the marginal, and round sixteen shipped a figure that did.""")

# ============================================================= D
print("\n" + "=" * 92)
print("D. THE INTAKE MIX: HOW MUCH OF THIS IS ONE CENTRAL DESK?")
print("=" * 92)
vc = D[B.Q].astype(str).value_counts()
central = vc.index[0]
nat = float(vc.iloc[0] / len(D))
print(f"  {len(vc)} opening groups; the largest, {central}, holds "
      f"{nat:.1%} of the cohort.\n")
rows = []
idx_c = np.flatnonzero((D[B.Q].astype(str) == central).values)
idx_o = np.flatnonzero((D[B.Q].astype(str) != central).values)
print(f"  {'central share':>14s} {'n':>8s} {'naive':>9s} {'honest':>9s} "
      f"{'reduction':>10s}")
for s in CENTRAL_SHARES:
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(B.SEED + 900 + seed)
        # largest cohort with the requested central share
        if s <= 0:
            take_c, take_o = 0, len(idx_o)
        elif s >= 1:
            take_c, take_o = len(idx_c), 0
        else:
            take_c = int(min(len(idx_c), len(idx_o) * s / (1 - s)))
            take_o = int(min(len(idx_o), take_c * (1 - s) / s))
        sel = np.concatenate([rng.choice(idx_c, take_c, replace=False),
                              rng.choice(idx_o, take_o, replace=False)])
        sel.sort()                       # keeps temporal order
        sub = D.iloc[sel]
        r = ladder(sub, f"central={s:.2f}")
        if r is None:
            continue
        r.update(central_share=s, seed=seed,
                 actual_central=float((sub[B.Q].astype(str) == central).mean()))
        rows.append(r)
        if seed == 0:
            print(f"  {s:>14.0%} {r['n']:>8,} {r['naive']:>+9.4f} "
                  f"{r['honest']:>+9.4f} {r['reduction']:>10.4f}")
AX_D = pd.DataFrame(rows)
AX_D.to_csv(RESULTS / "r38_axisD.csv", index=False)
agg = AX_D.groupby("central_share").agg(
    naive=("naive", "mean"), honest=("honest", "mean"),
    reduction=("reduction", "mean"), n=("n", "mean")).reset_index()
print(f"\n  averaged over {N_SEEDS} draws:")
for _, r in agg.iterrows():
    print(f"  {r.central_share:>14.0%} {int(r.n):>8,} {r.naive:>+9.4f} "
          f"{r.honest:>+9.4f} {r.reduction:>10.4f}")
red_lo, red_hi = float(agg.reduction.min()), float(agg.reduction.max())
print(f"""
  Across intake mixes from no central desk to 95% central desk the reduction
  runs {red_lo:.3f} to {red_hi:.3f}.  A 2026 organisation with more channels and a
  smaller central desk sits at the LEFT of that sweep.""")

facts.update(
    n=len(D), central_group=str(central), central_share_natural=nat,
    n_groups=int(len(vc)),
    prestamped_share_of_joins=float(same.sum() / max(int(joined.sum()), 1)),
    prestamped_share_of_cohort=float(same.mean()),
    n_no_interaction=int(no_int.sum()),
    uci_phone_share=0.991,
    wbs_gain=float(wbs["gain_over_group"]), item_gain=float(item["gain_over_group"]),
    n_wbs_cohort=n_wbs, n_wbs_train=n_wbs_tr,
    n_item_cohort=n_item, n_item_train=n_item_tr,
    wbs_share_of_item=float(wbs["gain_over_group"] / item["gain_over_group"]),
    item_marginal_over_wbs=float(marg),
    auc_both_layers=float(a_both), auc_item_only=float(item["auc"]),
    reduction_lo_intake_mix=red_lo, reduction_hi_intake_mix=red_hi,
    n_axisD_rows=len(AX_D), runtime_s=round(time.time() - t0, 1))
pd.DataFrame([facts]).to_csv(RESULTS / "r38_facts.csv", index=False)
print(f"\n  Wrote r38_axisA.csv, r38_axisB.csv, r38_axisC.csv, r38_axisD.csv, "
      f"r38_facts.csv  ({facts['runtime_s']:.0f}s)")

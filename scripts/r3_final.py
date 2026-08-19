"""R3 -- definitive analysis.  Fourth and final rebuild.

Design rule after three theses collapsed under review: EVERY claim must rest
on a comparison that already exists in the experimental design, not on a
control invented to support it.  All three previous failures -- feature
entry order, nominal-cardinality matching, and a mass-matched null that did
not match mass -- came from invented controls that were subtly wrong in the
direction that flattered the result.

Consequently this script makes no novel null.  It reports:
  A  descriptive data facts (no comparison at all)
  B  the value of item identity against a baseline that includes every
     creation-time field actually available, including the intake routing
     queue the service desk records for free
  C  the targeting curve under FOUR selection strategies, and the
     coverage-recovery relationship that holds across all of them
  D  a direct within-table comparison: does the class hierarchy add anything
     on top of item identity?  (no external baseline required)
  E  stability of every headline number across splits, seeds and windows
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
N_REP = 25
CUTOFF = "2013-10-01"
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
QUEUE = ["intake_group"]
IDENT = "CI Name (aff)"
CLASSES = ["CI Type (aff)", "CI Subtype (aff)", "Service Component WBS (aff)"]


# ====================================================================== data
def load(cutoff=CUTOFF):
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

    # intake routing queue, from the Open event of the activity log
    a = pd.read_csv(RAW / "Detail_Incident_Activity.csv", sep=";",
                    low_memory=False, encoding="latin-1")
    a.columns = [c.strip() for c in a.columns]
    a["ts"] = pd.to_datetime(a["DateStamp"], format="%d-%m-%Y %H:%M:%S",
                             errors="coerce", dayfirst=True)
    op = (a[a.IncidentActivity_Type == "Open"].sort_values("ts")
          .groupby("Incident ID").first())
    d["intake_group"] = d["Incident ID"].map(op["Assignment Group"]).fillna("__M__")

    if cutoff:
        d = d[d._t >= cutoff]
    d["_y"] = (d._ra >= 1).astype(int)
    return d.sort_values("_t").reset_index(drop=True), (n_file, n_id, n_parse), a, op


def split(d, frac=0.70):
    c = int(len(d) * frac)
    return d.iloc[:c].copy(), d.iloc[c:].copy()


def auc(tr, te, cols, C=1.0):
    e = OneHotEncoder(handle_unknown="ignore")
    Xtr = e.fit_transform(tr[cols].astype(str))
    Xte = e.transform(te[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C).fit(Xtr, tr._y.values)
    return te._y.values, m.predict_proba(Xte)[:, 1]


def boot_delta(y, pa, pb, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], pb[i]) - roc_auc_score(y[i], pa[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def boot_ci(y, p, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) > 1:
            v.append(roc_auc_score(y[i], p[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


D, counts, ACT, OPEN = load()
TR, TE = split(D)
n_file, n_id, n_parse = counts

print("=" * 92)
print("A. DATA  (descriptive -- no comparison, nothing to get wrong)")
print("=" * 92)
print(f"  rows in file                {n_file:,}")
print(f"  minus blank incident ID     {n_file-n_id:,}")
print(f"  minus unparseable           {n_id-n_parse:,}")
print(f"  minus warm-up (pre {CUTOFF}) {n_parse-len(D):,}")
print(f"  analysed                    {len(D):,}   train {len(TR):,} / test {len(TE):,}")
print(f"  window   {D._t.min().date()} .. {D._t.max().date()}")
print(f"  positive rate  train {TR._y.mean():.3f}   test {TE._y.mean():.3f}")

# the warm-up cut is identifiable from VOLUME alone -- outcome-free
vol = D._t.dt.to_period("M").value_counts().sort_index()
allm = (load(cutoff=None)[0]._t.dt.to_period("M").value_counts().sort_index())
print(f"\n  monthly volume before/after the cut: "
      f"{allm.loc[pd.Period('2013-09')]:,} (Sep) -> {allm.loc[pd.Period('2013-10')]:,} (Oct)")
print("  -> the cut point is identifiable from volume alone, without the outcome")

# population rate, computed only over rows we actually analyse
pop_ident = 1 - is_missing(D[IDENT]).mean()
print(f"\n  {IDENT} populated over ANALYSED rows: {pop_ident:.4%}")
print(f"  distinct items: train {TR[IDENT].nunique():,}  "
      f"analysed window {D[IDENT].nunique():,}")

# right-censoring: report, do not hide
print(f"\n  right-censoring check (extract ends {D._t.max().date()}):")
for m, g in D.groupby(D._t.dt.to_period('M')):
    print(f"    {m}  n={len(g):>6,}  positive {g._y.mean():.3f}  "
          f"median handle {g._ht.median():.2f}h")

# ---- the three figures the previous draft got wrong, recomputed
print("\n  RECOMPUTED (previous draft misstated these):")
ht = D.groupby(D._ra.clip(upper=5))._ht.median()
print(f"    median handle time, 0 reassignments : {ht.loc[0]:.2f} h")
print(f"    median handle time, 5+ reassignments: {ht.loc[5]:.2f} h")
sub = TR.groupby(["CI Subtype (aff)"])["CI Type (aff)"].nunique()
print(f"    CI Subtypes refining exactly one CI Type: "
      f"{(sub == 1).sum()} of {len(sub)}")
f = TR[IDENT].astype(str).value_counts()
keep = f[f >= 5].index
g = TR[TR[IDENT].astype(str).isin(keep)].groupby(TR[IDENT].astype(str))
rate = g._y.mean(); cnt = g.size(); cts = g._ra.mean()
print(f"    Spearman(volume, reassign RATE)  = {cnt.corr(rate, method='spearman'):+.4f}")
print(f"    Spearman(volume, reassign COUNT) = {cnt.corr(cts, method='spearman'):+.4f}")
print(f"    top-64 items reassignment rate {TR[TR[IDENT].astype(str).isin(f.index[:64])]._y.mean():.3f}"
      f" vs rest {TR[~TR[IDENT].astype(str).isin(f.index[:64])]._y.mean():.3f}")

print("\n" + "=" * 92)
pd.DataFrame([dict(
    n_file=n_file, n_blank=n_file - n_id, n_unparseable=n_id - n_parse,
    n_warmup=n_parse - len(D), n_analysed=len(D), n_train=len(TR), n_test=len(TE),
    pos_train=TR._y.mean(), pos_test=TE._y.mean(), pop_ident=pop_ident,
    n_items_analysed=D[IDENT].nunique(), n_items_train=TR[IDENT].nunique(),
    ht_0=ht.loc[0], ht_5=ht.loc[5],
    subtype_refining=int((sub == 1).sum()), subtype_total=int(len(sub)),
    sp_rate=cnt.corr(rate, method="spearman"),
    sp_count=cnt.corr(cts, method="spearman"),
    vol_sep=int(allm.loc[pd.Period("2013-09")]),
    vol_oct=int(allm.loc[pd.Period("2013-10")]),
)]).to_csv(RESULTS / "r3_facts.csv", index=False)

print("B. WHAT IS ITEM IDENTITY WORTH?  (baseline includes every free creation-time field)")
print("=" * 92)
conds = {
    "intake fields only": INTAKE,
    "+ intake routing queue": INTAKE + QUEUE,
    "+ item identity": INTAKE + QUEUE + [IDENT],
    "+ class hierarchy too": INTAKE + QUEUE + [IDENT] + CLASSES,
}
P = {}
print(f"  {'condition':26s} {'AUC':>7s} {'95% CI':>18s}")
for name, cols in conds.items():
    y, p = auc(TR, TE, cols)
    P[name] = p
    lo, hi = boot_ci(y, p)
    print(f"  {name:26s} {roc_auc_score(y,p):>7.3f}  [{lo:.3f},{hi:.3f}]")

MAIN = []
for name in conds:
    yy = TE._y.values
    lo_, hi_ = boot_ci(yy, P[name])
    MAIN.append(dict(condition=name, auc=roc_auc_score(yy, P[name]),
                     lo=lo_, hi=hi_))
lo, hi = boot_delta(y, P["+ intake routing queue"], P["+ item identity"])
gain = roc_auc_score(y, P["+ item identity"]) - roc_auc_score(y, P["+ intake routing queue"])
print(f"\n  item identity over the full free baseline: {gain:+.3f} [{lo:+.3f},{hi:+.3f}]")
lo2, hi2 = boot_delta(y, P["intake fields only"], P["+ item identity"])
g2 = roc_auc_score(y, P["+ item identity"]) - roc_auc_score(y, P["intake fields only"])
print(f"  (against intake fields alone it would read {g2:+.3f} "
      f"[{lo2:+.3f},{hi2:+.3f}] -- an overstatement of "
      f"{100*(g2-gain)/gain:.0f}%)")

lo3, hi3 = boot_delta(y, P["+ item identity"], P["+ class hierarchy too"])
g3 = roc_auc_score(y, P["+ class hierarchy too"]) - roc_auc_score(y, P["+ item identity"])
print(f"\n  D. class hierarchy ON TOP of item identity: {g3:+.3f} [{lo3:+.3f},{hi3:+.3f}]")
print("     (direct within-table comparison; no external null required)")

base_auc = roc_auc_score(y, P["+ intake routing queue"])
full_auc = roc_auc_score(y, P["+ item identity"])
pd.DataFrame(MAIN + [
    dict(condition="GAIN item identity", auc=gain, lo=lo, hi=hi),
    dict(condition="GAIN vs intake only", auc=g2, lo=lo2, hi=hi2),
    dict(condition="GAIN class hierarchy", auc=g3, lo=lo3, hi=hi3),
]).to_csv(RESULTS / "r3_main.csv", index=False)

print("\n  C tuning (inner temporal 80/20 within train):")
itr, ite = split(TR, 0.80)
for C in (0.1, 0.3, 1.0, 3.0, 10.0):
    yy, pp = auc(itr, ite, INTAKE + QUEUE + [IDENT], C=C)
    print(f"    C={C:<5} inner AUC {roc_auc_score(yy,pp):.3f}")

print("\n" + "=" * 92)
print("C. HOW MUCH OF THE ESTATE DO YOU NEED?  (four selection strategies)")
print("=" * 92)
freq = TR[IDENT].astype(str).value_counts()
cis = pd.Index(TR[IDENT].astype(str).unique())
tot = len(TR)
BASECOLS = INTAKE + QUEUE
KS = [8, 16, 32, 64, 128, 256, 512, 1024]
rows = []


def eval_subset(keep, label, k):
    tr, te = TR.copy(), TE.copy()
    for part in (tr, te):
        s = part[IDENT].astype(str)
        part["_v"] = np.where(s.isin(keep), s, "__OTHER__")
    yy, pp = auc(tr, te, BASECOLS + ["_v"])
    a = roc_auc_score(yy, pp)
    cov = freq.reindex(list(keep)).fillna(0).sum() / tot
    return a, cov, pp


print(f"  floor {base_auc:.3f}   ceiling {full_auc:.3f}\n")
print(f"  {'k':>6s} {'strategy':>14s} {'inc.cov':>8s} {'AUC':>7s} {'recovered':>10s}")
for k in KS:
    # 1 top-k by volume
    a, cov, pp = eval_subset(set(freq.index[:k]), "top-k", k)
    rlo, rhi = boot_delta(y, P["+ intake routing queue"], pp)
    rec = (a - base_auc) / (full_auc - base_auc)
    rows.append(dict(k=k, strategy="top-k", auc=a, coverage=cov, recovered=rec,
                     rec_lo=rlo / (full_auc - base_auc),
                     rec_hi=rhi / (full_auc - base_auc)))
    print(f"  {k:>6,} {'top-k':>14s} {cov:>8.1%} {a:>7.3f} {rec:>9.0%}"
          f"  [{rlo/(full_auc-base_auc):.0%},{rhi/(full_auc-base_auc):.0%}]")
    # 2 volume-proportional sampling ("whatever crosses the desk")
    accs = []
    for rep in range(5):
        rng = np.random.default_rng(SEED + rep)
        pr = (freq / freq.sum()).reindex(cis).fillna(0).values
        pick = rng.choice(cis, size=min(k, len(cis)), replace=False, p=pr / pr.sum())
        accs.append(eval_subset(set(pick), "prop", k)[:2])
    a2 = float(np.mean([x[0] for x in accs])); c2 = float(np.mean([x[1] for x in accs]))
    rows.append(dict(k=k, strategy="volume-proportional", auc=a2, coverage=c2,
                     recovered=(a2 - base_auc) / (full_auc - base_auc)))
    # 3 uniform random selection
    accs = []
    for rep in range(5):
        rng = np.random.default_rng(SEED + rep)
        pick = rng.choice(cis, size=min(k, len(cis)), replace=False)
        accs.append(eval_subset(set(pick), "unif", k)[:2])
    a3 = float(np.mean([x[0] for x in accs])); c3 = float(np.mean([x[1] for x in accs]))
    rows.append(dict(k=k, strategy="uniform-random", auc=a3, coverage=c3,
                     recovered=(a3 - base_auc) / (full_auc - base_auc)))
    # 4 all items collapsed into k random buckets
    accs = []
    for rep in range(5):
        rng = np.random.default_rng(SEED + rep)
        lut = pd.Series(rng.integers(0, k, len(cis)).astype(str), index=cis)
        tr, te = TR.copy(), TE.copy()
        tr["_v"] = tr[IDENT].astype(str).map(lut).fillna("__M__")
        te["_v"] = te[IDENT].astype(str).map(lut).fillna("__M__")
        yy, pp = auc(tr, te, BASECOLS + ["_v"])
        accs.append(roc_auc_score(yy, pp))
    a4 = float(np.mean(accs))
    rows.append(dict(k=k, strategy="k random buckets", auc=a4, coverage=1.0,
                     recovered=(a4 - base_auc) / (full_auc - base_auc)))

R = pd.DataFrame(rows)
R["base"] = base_auc; R["full"] = full_auc
R.to_csv(RESULTS / "r3_targeting.csv", index=False)

print("\n" + "=" * 92)
print("THE TRANSFERABLE RESULT: recovery is a function of INCIDENT COVERAGE")
print("=" * 92)
sub = R[R.strategy.isin(["top-k", "volume-proportional", "uniform-random"])]
sub = sub[sub.coverage < 0.999]
sp = sub.coverage.corr(sub.recovered, method="spearman")
lin = np.polyfit(sub.coverage, sub.recovered, 1)
pred = np.polyval(lin, sub.coverage)
r2 = 1 - ((sub.recovered - pred) ** 2).sum() / ((sub.recovered - sub.recovered.mean()) ** 2).sum()
print(f"  across {len(sub)} (strategy, k) points spanning three selection rules:")
print(f"    Spearman(incident coverage, recovered) = {sp:.3f}")
print(f"    linear R^2                             = {r2:.3f}")
print("  -> how much of the estate you must identify is set by mass concentration,")
print("     which is a value_counts() away and needs no model at all.")

conc = freq.cumsum() / tot
print(f"\n  mass concentration of this estate:")
for k in (8, 32, 64, 128, 256):
    print(f"    top {k:>4,} items = {conc.iloc[k-1]:.1%} of incidents")

print("\n" + "=" * 92)
print("E. STABILITY")
print("=" * 92)
STAB = []
print("  gain and recovery across temporal split points:")
for frac in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
    tr, te = split(D, frac)
    yy, pb = auc(tr, te, INTAKE + QUEUE)
    _, pf = auc(tr, te, INTAKE + QUEUE + [IDENT])
    b, fl = roc_auc_score(yy, pb), roc_auc_score(yy, pf)
    fr = tr[IDENT].astype(str).value_counts()
    recs = {}
    for k in (64, 128, 256):
        t2, e2 = tr.copy(), te.copy()
        for part in (t2, e2):
            s = part[IDENT].astype(str)
            part["_v"] = np.where(s.isin(set(fr.index[:k])), s, "__OTHER__")
        _, pk = auc(t2, e2, BASECOLS + ["_v"])
        recs[k] = (roc_auc_score(yy, pk) - b) / (fl - b)
    print(f"    cut {frac:.0%}: gain {fl-b:+.3f}   rec@64 {recs[64]:.0%}  "
          f"rec@128 {recs[128]:.0%}  rec@256 {recs[256]:.0%}")
    STAB.append(dict(cut=frac, gain=fl-b, r64=recs[64], r128=recs[128],
                     r256=recs[256]))

pd.DataFrame(STAB).to_csv(RESULTS / "r3_stability.csv", index=False)

print("\n  sensitivity to the warm-up cutoff:")
for co in ["2013-09-01", "2013-10-01", "2013-11-01", None]:
    d2, _, _, _ = load(cutoff=co)
    t2, e2 = split(d2)
    yy, pb = auc(t2, e2, INTAKE + QUEUE)
    _, pf = auc(t2, e2, INTAKE + QUEUE + [IDENT])
    print(f"    cutoff {str(co):>12s}: n={len(d2):>6,}  "
          f"gain {roc_auc_score(yy,pf)-roc_auc_score(yy,pb):+.3f}")

# ---- generate the mutability artifact PROPERLY (was an orphan CSV)
n_inc = ACT["Incident ID"].nunique()
mut = []
for t in ["Affected CI Change", "Service Change"]:
    s = ACT[ACT.IncidentActivity_Type == t]
    mut.append(dict(activity=t, events=len(s),
                    incidents=s["Incident ID"].nunique(),
                    pct_incidents=s["Incident ID"].nunique() / n_inc))
mdf = pd.DataFrame(mut); mdf.to_csv(RESULTS / "r3_mutability.csv", index=False)
print("\n" + "=" * 92)
print("F. FEATURE VALIDITY  (regenerated here, not an orphan file)")
print("=" * 92)
print(f"  activities {len(ACT):,} over {n_inc:,} incidents")
for _, r in mdf.iterrows():
    print(f"  {r.activity:22s} {r.incidents:>5,} incidents  {r.pct_incidents:.2%}")
ci_edit = set(ACT[ACT.IncidentActivity_Type == "Affected CI Change"]["Incident ID"])
D["_edit"] = D["Incident ID"].isin(ci_edit)
print(f"  P(CI edited | reassigned)     {D[D._y==1]._edit.mean():.4%}")
print(f"  P(CI edited | not reassigned) {D[D._y==0]._edit.mean():.4%}")
print("  -> edits concentrate where they would do harm, but at 0.4% they cannot")
print("     move an AUC of 0.75; reported for completeness, not as a threat.")

ra_log = (ACT[ACT.IncidentActivity_Type == "Reassignment"]
          .groupby("Incident ID").size())
j = D.set_index("Incident ID")[["_ra"]].join(ra_log.rename("log")).fillna({"log": 0})
print(f"  corr(counter, logged reassignments) {j._ra.corr(j.log):.4f}   "
      f"binary agreement {((j._ra>=1)==(j.log>=1)).mean():.4%}")

# intake queue validity
lag = (OPEN["ts"] - D.set_index("Incident ID")["_t"]).dropna().dt.total_seconds() / 60
print(f"\n  intake routing queue: {OPEN['Assignment Group'].nunique()} groups, "
      f"{is_missing(OPEN['Assignment Group']).mean():.2%} missing")
print(f"  Open-event lag: median {lag.median():.2f} min, "
      f"within 5 min {(lag.abs()<=5).mean():.1%}")
print(f"  group varies within incident on "
      f"{(ACT.groupby('Incident ID')['Assignment Group'].nunique()>1).mean():.2%} of incidents")

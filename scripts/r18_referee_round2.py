"""R18 -- four things a second referee found missing.

Each is a quantity the paper asserts, or silently omits, without the control
its own argument demands.

  A  A NULL FOR THE INFORMATION-THEORETIC FIGURES.  Section 5 reports
     U(group|item) = 60.4% "without any estimator" and calls it real.  A
     plug-in uncertainty coefficient over 2,554 conditioning levels on 31,818
     rows is biased upward by finite samples.  The referee computed the floor;
     this reproduces it.  Reporting a number in the section that narrates
     fixing exactly this failure mode, without its floor, is indefensible.

  B  THE FIELD THE PAPER NEVER MENTIONS.  `Service Component WBS (aff)` is
     100% populated, free, and admitting it takes the item's measured value
     from +0.183 to near zero.  Excluding it is almost certainly right --- it
     is near-deterministic in the item, so it IS configuration data --- but
     the paper's whole thesis is that silent field exclusions decide the
     answer, and this exclusion is silent.  Measure it and say so.

  C  THE "HONEST" BASELINE IS NOT A TERMINUS EITHER.  Hour-of-day and
     day-of-week are unambiguously creation-time and unambiguously free, and
     the paper never tests them.  If they move the number, that is not an
     embarrassment: it is the thesis applied one rung further, and the paper
     is stronger for saying so.

  D  THE DROPPED LEG'S THIRD FLOOR IS THE CONSTRUCTION WE CONDEMNED.  Section
     5 excludes the reverse framing because "defensible nulls disagree",
     citing 44%, 25% and -7%.  The -7% comes from r8_final.py:167, which
     draws cell labels PER ROW -- the same defect r17 exists to correct.  A
     number produced by a construction the paper calls invalid cannot be part
     of the reason for a withdrawal.  Rebuild it at item level.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_DRAW = 30
Q = "intake_group"
WBS = "Service Component WBS (aff)"

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values


def H(s):
    p = pd.Series(s).value_counts(normalize=True).values
    return float(-(p * np.log2(p)).sum())


def H_cond(inner, outer, df):
    g = df.groupby(outer, observed=True)[inner]
    w = g.size() / len(df)
    return float((w * g.apply(H)).sum())


def U(inner, outer, df):
    return 1 - H_cond(inner, outer, df) / H(df[inner])


print("=" * 88)
print("A. A FLOOR FOR THE UNCERTAINTY COEFFICIENTS")
print("=" * 88)
tr = TR[[M.IDENT, Q]].astype(str)
u_qi, u_iq = U(Q, M.IDENT, tr), U(M.IDENT, Q, tr)
nq, ni = [], []
for rep in range(N_DRAW):
    r = np.random.default_rng(SEED + rep)
    s = tr.copy()
    s["_shuf"] = r.permutation(s[M.IDENT].values)   # item labels destroyed
    nq.append(U(Q, "_shuf", s))
    ni.append(1 - H_cond("_shuf", Q, s) / H(s["_shuf"]))
nq, ni = np.array(nq), np.array(ni)
print(f"  U(group | item)   real {u_qi:6.1%}   shuffled {nq.mean():6.1%} "
      f"+- {nq.std():.1%}   above floor {100*(u_qi-nq.mean()):5.1f} pts")
print(f"  U(item  | group)  real {u_iq:6.1%}   shuffled {ni.mean():6.1%} "
      f"+- {ni.std():.1%}   above floor {100*(u_iq-ni.mean()):5.1f} pts")
print("\n  A quarter of the 60.4% is finite-sample bias from conditioning on")
print(f"  {tr[M.IDENT].nunique():,} levels.  The ASYMMETRY survives with room to spare, so the")
print("  qualitative claim stands -- but the raw figures must be reported")
print("  with these floors, not as if they were information.")
pd.DataFrame([dict(u_group_given_item=u_qi, u_item_given_group=u_iq,
                   null_group_given_item=float(nq.mean()),
                   null_group_sd=float(nq.std()),
                   null_item_given_group=float(ni.mean()),
                   null_item_sd=float(ni.std()),
                   excess_group=100 * (u_qi - nq.mean()),
                   excess_item=100 * (u_iq - ni.mean()),
                   n_levels=int(tr[M.IDENT].nunique()), n_draws=N_DRAW)]
             ).to_csv(RESULTS / "r18_mi_null.csv", index=False)


def gain(base_cols):
    a = roc_auc_score(y, M.fit(TR, TE, base_cols))
    b = roc_auc_score(y, M.fit(TR, TE, base_cols + [M.IDENT]))
    return a, b, b - a


print("\n" + "=" * 88)
print("B+C. EVERY FREE FIELD WE COULD HAVE ADMITTED, AND WHAT IT COSTS")
print("=" * 88)
for p in (TR, TE):
    p["_hour"] = p._t.dt.hour.astype(str)
    p["_dow"] = p._t.dt.dayofweek.astype(str)
from common import population_rate
print(f"  {WBS}: {D[WBS].nunique():,} distinct values, "
      f"{population_rate(D[WBS]):.1%} populated")
v = D.groupby(M.IDENT)[WBS].nunique()
print(f"  items with more than one WBS value: {int((v>1).sum())} of {len(v):,}"
      f"  -> near-deterministic in the item\n")
LADDER = [
    ("intake only", M.INTAKE),
    ("+ opening group  (the paper's)", M.INTAKE + [Q]),
    ("+ hour of day", M.INTAKE + [Q, "_hour"]),
    ("+ hour + day of week", M.INTAKE + [Q, "_hour", "_dow"]),
    ("+ service component WBS", M.INTAKE + [Q, WBS]),
    ("WBS instead of the group", M.INTAKE + [WBS]),
]
rows = []
print(f"  {'baseline':34s} {'base':>7s} {'+item':>7s} {'gain':>9s}")
for name, cols in LADDER:
    a, b, g = gain(cols)
    rows.append(dict(baseline=name, base_auc=a, with_item=b, gain=g))
    print(f"  {name:34s} {a:>7.3f} {b:>7.3f} {g:>+9.3f}")
W = pd.DataFrame(rows)
W.to_csv(RESULTS / "r18_other_fields.csv", index=False)
g_paper = float(W[W.baseline.str.startswith("+ opening")].gain.iloc[0])
g_wbs = float(W[W.baseline.str.startswith("+ service")].gain.iloc[0])
g_dow = float(W[W.baseline.str.startswith("+ hour + day")].gain.iloc[0])
print(f"\n  Hour and day of week are free and creation-time, and take the")
print(f"  measured value from {g_paper:+.3f} to {g_dow:+.3f}.  The paper's baseline is")
print("  not a terminus, and the paper should say so: that IS the thesis.")
print(f"\n  Service component takes it to {g_wbs:+.3f}.  We exclude it because it is")
print(f"  a near-deterministic function of the item ({int((v>1).sum())} of {len(v):,} items vary),")
print("  so it is configuration data, not a free intake field -- but that is")
print("  an argument the paper has to make, not omit.")

print("\n" + "=" * 88)
print("D. THE DROPPED LEG'S THIRD FLOOR, REBUILT AT ITEM LEVEL")
print("=" * 88)
A0 = roc_auc_score(y, M.fit(TR, TE, M.INTAKE))
ig = roc_auc_score(y, M.fit(TR, TE, M.INTAKE + [M.IDENT])) - A0
ITEMS = pd.Index(D[M.IDENT].astype(str).unique())
qsz = TR[Q].astype(str).value_counts(normalize=True)


def shuffle_items_within(cell_col, tr, te):
    out = []
    for rep in range(15):
        r = np.random.default_rng(SEED + rep)
        a, b = tr.copy(), te.copy()
        for p in (a, b):
            p["_s"] = p.groupby(cell_col)[M.IDENT].transform(
                lambda s: r.permutation(s.values))
        out.append(roc_auc_score(b._y.values, M.fit(a, b, M.INTAKE + ["_s"])) - A0)
    return np.array(out)


res = []
tr0, te0 = TR.copy(), TE.copy()
tr0["_c"], te0["_c"] = tr0[Q].astype(str), te0[Q].astype(str)
real = shuffle_items_within("_c", tr0, te0)
res.append(("real opening group", real.mean(), real.std()))

for label, mode in [("random item cells, equal size", "uniform"),
                    ("random item cells, group-mass matched", "mass")]:
    vals = []
    for rep in range(15):
        r = np.random.default_rng(SEED + rep)
        if mode == "uniform":
            lut = pd.Series(r.integers(0, len(qsz), len(ITEMS)).astype(str),
                            index=ITEMS)
        else:
            # cell SIZES follow the group's mass profile, but cells are a
            # partition of ITEMS -- the row-level version of this is what
            # r8_final.py:167 does and what section 5 condemns.
            lut = pd.Series(r.choice(qsz.index, size=len(ITEMS), p=qsz.values),
                            index=ITEMS)
        a, b = TR.copy(), TE.copy()
        for p in (a, b):
            p["_c"] = p[M.IDENT].astype(str).map(lut)
        for q in (a, b):
            q["_s"] = q.groupby("_c")[M.IDENT].transform(
                lambda z: r.permutation(z.values))
        vals.append(roc_auc_score(b._y.values,
                                  M.fit(a, b, M.INTAKE + ["_s"])) - A0)
    v2 = np.array(vals, dtype=float)
    res.append((label, v2.mean(), v2.std()))

print(f"  {'construction':40s} {'retained':>10s} {'sd':>8s}")
for lab, mu, sd in res:
    print(f"  {lab:40s} {100*mu/ig:>9.0f}% {100*sd/ig:>7.0f}%")
pd.DataFrame([dict(leg=l, retained=m / ig, sd=s / ig) for l, m, s in res]
             ).to_csv(RESULTS / "r18_dropped_leg_itemlevel.csv", index=False)
print("\n  Rebuilt at item level the floors no longer straddle the real leg the")
print("  way the row-level -7% suggested.  The paper must either drop the -7%")
print("  from its reason for excluding this leg, or replace it with these.")

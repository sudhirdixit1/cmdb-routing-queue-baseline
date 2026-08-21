"""
r20 -- THE SECOND ORGANISATION.

Round fifteen found that the Background's claim about the third public log
--- "has no such field at all" --- is FALSE.  BPI Challenge 2013 (Volvo IT,
VINST) carries `product`: 704 distinct values, exactly one per trace, on all
7,554 traces, none missing.  The claim was the sole support for the paper's
largest limitation, and this repository already knew better: see
`scripts/e11_cross_org_layers.py`, which defines VolvoIT with service=
["product"], and `results/e13_real_fields.csv`, which records a gain for it.

So the study is no longer single-organisation.  This script runs the paper's
ladder on Volvo IT and reports what does and does not carry across.

WHAT CARRIES:      the ordering and the existence of the gap.
WHAT DOES NOT:     the magnitude.

AND ONE CAVEAT WE MUST STATE OURSELVES, because it cuts against us:
on BPIC 2014 the opening group matches the incident's first Assignment
group only 15.1% of the time --- it is the desk that LOGGED the ticket, a
different object from the routing sequence that defines the target.  On
BPIC 2013 the opening group IS the first term of the org:group sequence
whose variation defines ping-pong.  The coupling is therefore strictly
tighter here, the free field is correspondingly worth more (+0.19 against
+0.08), and the Volvo shrinkage should be read as an UPPER bound rather
than as a second draw from the same distribution.
"""
import gzip
import re

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

from common import RAW, RESULTS

SEED = 20260819
N_BOOT = 2000
SPLITS = (0.55, 0.60, 0.65, 0.70, 0.75, 0.80)
INTAKE = ["impact"]          # the one intake-form field BPIC 2013 shares
IDENT = "product"            # the configuration-item analogue
FREE = "open_group"          # the group on the first event


def load():
    with gzip.open(RAW / "BPI_Challenge_2013_incidents.xes.gz",
                   "rt", encoding="utf-8") as f:
        xes = f.read()
    rows = []
    for t in re.findall(r"<trace>(.*?)</trace>", xes, re.S):
        evs = re.findall(r"<event>(.*?)</event>", t, re.S)

        def g(ev, k):
            m = re.search(r'key="%s" value="([^"]*)"' % re.escape(k), ev)
            return m.group(1) if m else "__M__"

        gr = [g(e, "org:group") for e in evs]
        rows.append(dict(
            t0=g(evs[0], "time:timestamp"),
            product=g(evs[0], "product"),
            impact=g(evs[0], "impact"),
            open_group=gr[0],
            n_prod=len({g(e, "product") for e in evs}),
            changes=sum(1 for a, b in zip(gr, gr[1:]) if a != b),
        ))
    d = pd.DataFrame(rows)
    d["_t"] = pd.to_datetime(d.t0, utc=True, format="ISO8601", errors="coerce")
    d = d.dropna(subset=["_t"]).sort_values(
        ["_t", "product"], kind="stable").reset_index(drop=True)
    return d


def fit(tr, te, cols, C=1.0):
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C).fit(X, tr._y.values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def ladder(d, frac):
    c = int(len(d) * frac)
    tr, te = d.iloc[:c].copy(), d.iloc[c:].copy()
    y = te._y.values
    p = {}
    for tag, base in (("a", INTAKE), ("b", INTAKE + [FREE])):
        p[tag + "0"] = fit(tr, te, base)
        p[tag + "1"] = fit(tr, te, base + [IDENT])
    g1 = roc_auc_score(y, p["a1"]) - roc_auc_score(y, p["a0"])
    g2 = roc_auc_score(y, p["b1"]) - roc_auc_score(y, p["b0"])
    return g1, g2, y, p, tr, te


def boot_shrinkage(y, p, n=N_BOOT, seed=SEED):
    """Paired bootstrap on the SHRINKAGE itself, not on either gain.

    Round fourteen's lesson: for eight rounds every interval was on a gain
    while every transferability claim was about the shrinkage.
    """
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if len(np.unique(y[i])) < 2:
            continue
        g1 = roc_auc_score(y[i], p["a1"][i]) - roc_auc_score(y[i], p["a0"][i])
        g2 = roc_auc_score(y[i], p["b1"][i]) - roc_auc_score(y[i], p["b0"][i])
        if g1 > 0:
            v.append(100 * (1 - g2 / g1))
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)),
            float(np.mean(np.array(v) <= 0)), len(v))


D = load()

print("=" * 88)
print("A. THE FIELD THE PAPER SAID DID NOT EXIST")
print("=" * 88)
print(f"  traces                       {len(D)}")
print(f"  distinct `product` values    {D['product'].nunique()}")
print(f"  traces with exactly one      {int((D.n_prod == 1).sum())}")
print(f"  traces with none             {int((D.n_prod == 0).sum())}")
print(f"  population                   "
      f"{100 * (D.n_prod >= 1).mean():.1f}%")
print(f"  distinct opening org:group   {D[FREE].nunique()}")
print("  -> the claim that this log has no such field is false.")
pd.DataFrame([dict(n_traces=len(D),
                   n_products=int(D["product"].nunique()),
                   n_single_product=int((D.n_prod == 1).sum()),
                   n_missing=int((D.n_prod == 0).sum()),
                   population=float((D.n_prod >= 1).mean()),
                   n_open_groups=int(D[FREE].nunique()))]
             ).to_csv(RESULTS / "r20_facts.csv", index=False)

rows = []
print()
print("=" * 88)
print("B. THE LADDER ON VOLVO IT, TWO THRESHOLDS x SIX SPLITS")
print("=" * 88)
for thr in (1, 2):
    D["_y"] = (D.changes >= thr).astype(int)
    print(f"\n  ping-pong >= {thr} group change(s)   "
          f"positive rate {D._y.mean():.3f}")
    for frac in SPLITS:
        g1, g2, y, p, tr, te = ladder(D, frac)
        sh = 100 * (1 - g2 / g1)
        rows.append(dict(threshold=thr, split=frac, n=len(D),
                         pos_rate=float(D._y.mean()),
                         n_train=len(tr), n_test=len(te),
                         gain_intake=g1, gain_plus_group=g2, shrinkage=sh))
        print(f"    split {frac:.2f}   rung1 {g1:+.4f}   rung2 {g2:+.4f}"
              f"   shrinkage {sh:5.1f}%")

pd.DataFrame(rows).to_csv(RESULTS / "r20_second_org.csv", index=False)

print()
print("=" * 88)
print("C. AN INTERVAL ON THE SHRINKAGE, AT THE PUBLISHED SPLIT")
print("=" * 88)
ci = []
for thr in (1, 2):
    D["_y"] = (D.changes >= thr).astype(int)
    g1, g2, y, p, tr, te = ladder(D, 0.70)
    lo, hi, p0, nb = boot_shrinkage(y, p)
    ci.append(dict(threshold=thr, gain_intake=g1, gain_plus_group=g2,
                   shrinkage=100 * (1 - g2 / g1), lo=lo, hi=hi,
                   p_le_0=p0, n_draws=nb))
    print(f"  >= {thr}   shrinkage {100 * (1 - g2 / g1):5.1f}%"
          f"   95% CI [{lo:.0f}, {hi:.0f}]   P(<=0) {p0:.3f}"
          f"   ({nb} draws)")
pd.DataFrame(ci).to_csv(RESULTS / "r20_second_org_ci.csv", index=False)

print()
print("=" * 88)
print("D. THE CAVEAT THAT CUTS AGAINST US")
print("=" * 88)
D["_y"] = (D.changes >= 1).astype(int)
c = int(len(D) * 0.70)
tr, te = D.iloc[:c].copy(), D.iloc[c:].copy()
y = te._y.values
a0 = roc_auc_score(y, fit(tr, te, INTAKE))
aq = roc_auc_score(y, fit(tr, te, INTAKE + [FREE]))
print(f"  the free field is worth {aq - a0:+.4f} over intake here,")
print(f"  against +0.082 on BPIC 2014.  On BPIC 2014 the opening group")
print(f"  matches the first Assignment group 15.1% of the time; here it IS")
print(f"  the first term of the sequence whose variation defines the target.")
print(f"  Read the Volvo shrinkage as an upper bound, not a second draw.")
pd.DataFrame([dict(auc_intake=a0, auc_intake_group=aq, free_gain=aq - a0)]
             ).to_csv(RESULTS / "r20_coupling.csv", index=False)
print()
print("wrote r20_second_org.csv, r20_second_org_ci.csv, r20_coupling.csv")

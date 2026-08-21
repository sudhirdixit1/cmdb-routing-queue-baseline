"""r34 -- DOES THE LEAD CONTRIBUTION REPLICATE?

The published paper leads with "identity, not attributes": a resolution ladder
on Rabobank's estate in which a 256-way grouping captures three quarters of
what the 2,554-way item identity is worth.  That finding is ONE LOG.  Plan
section 4 says: replicate it on at least two more, or demote it out of the
lead.  This script is that test, and it is written so that it can fail.

  A. THE LAYER LADDERS.  The candidate hierarchies are the ones named in
     PLAN-STRONG-ACCEPT.md section 4.1, which was written before any of them
     was run:

         UCI 498     cmdb_ci  <  subcategory  <  category
         Helpdesk    product  <  support_section  <  service_type
         BPIC 2019   case:Item  <  case:Item Category  <  case:Vendor
                                <  case:Spend area text
         BPIC 2013   does `product` decompose?  If the strings carry no
                     structure, say so.  A hierarchy invented by clustering
                     is a grouping chosen after seeing the outcome and is
                     not admissible.

     Every level is tested for determinism against the level below it and
     the test is reported, because a "hierarchy" whose levels cross is not
     one.  Where a level is sparsely populated the ladder runs on the
     populated subset and the cohort size is printed beside it: a small-n
     replication that is LABELLED small is worth more than none.

  B. THE OUTCOME-HISTORY CONTROL, ON EVERY ADMITTED LOG.  The strongest
     single number in the published paper is that a per-item historical
     outcome rate -- no model, no attribute, one number per entity -- reaches
     AUC 0.744 against the fitted model's 0.748.  If entity identity is a
     carrier of outcome history rather than of attributes, that is where it
     shows, and it should show on every log or on none.

Outputs: results/r34_layers.csv, r34_layer_determinism.csv,
         r34_history.csv, r34_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
import r33_generic_ladder as L
from common import RESULTS

t0 = time.time()
TRAIN_FRAC = L.TRAIN_FRAC

# Declared in PLAN-STRONG-ACCEPT.md section 4.1, before any was run.
HIERARCHIES = {
    "UCI498":   ["cmdb_ci", "subcategory", "category"],
    "Helpdesk": ["product", "support_section", "service_type"],
    "BPIC19":   ["case:Item", "case:Item Category", "case:Vendor",
                 "case:Spend area text"],
    "BPIC14":   ["CI Name (aff)", "CI Subtype (aff)", "CI Type (aff)"],
}
DECOMPOSE = {"BPIC13_incidents": "product", "BPIC13_closed": "product"}

ROLES = pd.read_csv(RESULTS / "r33_roles.csv")
EXC = (pd.read_csv(RESULTS / "r33_excluded.csv")
       if (RESULTS / "r33_excluded.csv").exists() else pd.DataFrame())
ADMITTED = sorted(ROLES.log.unique())


def roles_for(key):
    r = ROLES[ROLES.log == key]
    f = r[r.role.isin(["f_amended"])].attribute.tolist() or \
        r[r.role == "f_registered"].attribute.tolist()
    g = r[r.role == "g"].attribute.tolist()
    b0 = r[r.role == "B0"].attribute.tolist()
    return (f[0] if f else None), (g[0] if g else None), b0


def prepared(key):
    """The log, ordered and split exactly as r33 orders and splits it, with
    both registered targets attached."""
    d = C.load(key)
    d, has_time = L.temporal_order(d)
    n = len(d)
    cut = int(n * TRAIN_FRAC)
    _, g, _ = roles_for(key)
    seq = next((c for c in d.columns
                if c.startswith("_seq_") and c[5:].lower() == str(g).lower()),
               None)
    if seq is None:
        return None
    y_h, y_d, _ = L.targets(d, seq, cut)
    return d, cut, y_h, y_d


# ===================================================================== A
print("=" * 92)
print("A. THE LAYER LADDERS")
print("=" * 92)
lay_rows, det_rows = [], []
for key, levels in HIERARCHIES.items():
    if key not in ADMITTED:
        print(f"\n{key}: not admitted by the protocol; skipped")
        continue
    prep = prepared(key)
    if prep is None:
        print(f"\n{key}: no resource sequence; skipped")
        continue
    d, cut, y_h, y_d = prep
    f, g, b0 = roles_for(key)
    have = [c for c in levels if c in d.columns]
    missing = [c for c in levels if c not in d.columns]
    print(f"\n{key}   levels present {have}" +
          (f"   MISSING {missing}" if missing else ""))
    if len(have) < 2:
        print("  fewer than two levels present; no ladder")
        continue

    # populated subset: every level non-missing
    ok = np.ones(len(d), dtype=bool)
    for c in have:
        ok &= ~C.is_missing(d[c]).values
    print(f"  populated on all levels: {int(ok.sum()):,} of {len(d):,} "
          f"({ok.mean():.2%})")

    # determinism between adjacent levels, on the populated subset
    sub = d[ok]
    for a, b in zip(have[:-1], have[1:]):
        t = pd.DataFrame({"fine": sub[a].astype(str).values,
                          "coarse": sub[b].astype(str).values})
        nu = t.groupby("fine")["coarse"].nunique()
        det_rows.append(dict(log=key, fine=a, coarse=b,
                             card_fine=int(sub[a].nunique()),
                             card_coarse=int(sub[b].nunique()),
                             share_exactly_one=float((nu == 1).mean()),
                             max_distinct=int(nu.max()),
                             deterministic=bool((nu == 1).all()),
                             n=int(len(sub))))
        print(f"    {a:22s} -> {b:22s} "
              f"{int(sub[a].nunique()):>6,} -> {int(sub[b].nunique()):>5,}  "
              f"deterministic {(nu == 1).mean():.2%}"
              + ("" if (nu == 1).all() else f"  (max {int(nu.max())})"))

    for tname, yv in (("handover", y_h), ("duration", y_d)):
        if yv is None:
            continue
        dd = d.copy()
        dd["_y"] = yv
        s = dd[ok]
        c2 = int(len(s) * TRAIN_FRAC)
        tr, te = s.iloc[:c2], s.iloc[c2:]
        yte = te["_y"].values
        if len(np.unique(yte)) < 2 or len(te) < 100:
            print(f"    [{tname}] too little test variation; skipped")
            continue
        b0_here = [c for c in b0 if c not in have]
        if not b0_here:
            b0_here = [c for c in b0] or have[-1:]
        try:
            base = roc_auc_score(yte, L.fit(tr, te, b0_here))
        except Exception as e:                              # noqa: BLE001
            print(f"    [{tname}] base fit failed: {e}")
            continue
        print(f"    [{tname}] n={len(s):,} prev={yv[ok].mean():.3f}  "
              f"B0 AUC {base:.4f}")
        prev_auc = base
        for c in reversed(have):          # coarsest first
            try:
                a = roc_auc_score(yte, L.fit(tr, te, b0_here + [c]))
            except Exception as e:                          # noqa: BLE001
                print(f"      {c}: fit failed {e}")
                continue
            lay_rows.append(dict(log=key, target=tname, level=c,
                                 levels_from_coarse=list(reversed(have)).index(c),
                                 cardinality=int(s[c].nunique()),
                                 n=int(len(s)), n_test=int(len(te)),
                                 base_auc=base, auc=a, gain_over_b0=a - base))
            print(f"      + {c:24s} card {int(s[c].nunique()):>6,}  "
                  f"AUC {a:.4f}  over B0 {a - base:+.4f}")
            prev_auc = a
        # the marginal of the finest level over the second finest
        if len(have) >= 2:
            fine, nxt = have[0], have[1]
            try:
                a_next = roc_auc_score(yte, L.fit(tr, te, b0_here + [nxt]))
                a_both = roc_auc_score(yte, L.fit(tr, te, b0_here + [nxt, fine]))
                lay_rows.append(dict(log=key, target=tname,
                                     level=f"{fine} marginal over {nxt}",
                                     levels_from_coarse=-1,
                                     cardinality=int(s[fine].nunique()),
                                     n=int(len(s)), n_test=int(len(te)),
                                     base_auc=a_next, auc=a_both,
                                     gain_over_b0=a_both - a_next))
                print(f"      {fine} marginal over {nxt}: {a_both - a_next:+.4f}")
            except Exception as e:                          # noqa: BLE001
                print(f"      marginal failed: {e}")

# --- does BPIC 2013's product string decompose? ---------------------------
print("\n" + "-" * 92)
print("Does BPI Challenge 2013's `product` carry structure?")
for key, col in DECOMPOSE.items():
    if key not in ADMITTED:
        continue
    d = C.load(key)
    v = d[col].astype(str)
    v = v[~C.is_missing(d[col]).values]
    sample = sorted(v.unique())[:6]
    seps = {s: float(v.str.contains(s, regex=False).mean())
            for s in ("_", "-", " ", ".", "/")}
    print(f"  {key}: {v.nunique():,} distinct, examples {sample}")
    print(f"    separator frequency: " +
          ", ".join(f"{k!r} {p:.1%}" for k, p in seps.items()))
    best = max(seps, key=seps.get)
    if seps[best] > 0.90:
        pref = v.str.split(best, regex=False).str[0]
        print(f"    prefix before {best!r}: {pref.nunique():,} distinct "
              f"(a candidate coarser level)")
        det_rows.append(dict(log=key, fine=col, coarse=f"prefix({best})",
                             card_fine=int(v.nunique()),
                             card_coarse=int(pref.nunique()),
                             share_exactly_one=1.0, max_distinct=1,
                             deterministic=True, n=int(len(v))))
    else:
        print(f"    no separator appears in more than 90% of values, so the "
              f"strings carry no\n    decomposable structure.  We do not "
              f"invent one by clustering: a grouping\n    chosen after seeing "
              f"the outcome is not a hierarchy.")
        det_rows.append(dict(log=key, fine=col, coarse="NONE FOUND",
                             card_fine=int(v.nunique()), card_coarse=np.nan,
                             share_exactly_one=np.nan, max_distinct=np.nan,
                             deterministic=False, n=int(len(v))))

if lay_rows:
    pd.DataFrame(lay_rows).to_csv(RESULTS / "r34_layers.csv", index=False)
pd.DataFrame(det_rows).to_csv(RESULTS / "r34_layer_determinism.csv", index=False)

# ===================================================================== B
print("\n" + "=" * 92)
print("B. THE OUTCOME-HISTORY CONTROL, ON EVERY ADMITTED LOG")
print("=" * 92)
print("""  The score is one number per entity: the target rate among the TRAINING
  traces carrying that value of f.  Values unseen in training take the
  training prior.  No model, no attribute, no interaction.  If it reaches
  the fitted model's AUC, entity identity is carrying outcome history and
  not attributes.\n""")
hist_rows = []
print(f"  {'log':18s} {'target':9s} {'n_test':>8s} {'history':>8s} "
      f"{'B0+f model':>11s} {'B0':>7s} {'unseen':>7s}")
for key in ADMITTED:
    prep = prepared(key)
    if prep is None:
        continue
    d, cut, y_h, y_d = prep
    f, g, b0 = roles_for(key)
    if f is None or not b0:
        continue
    for tname, yv in (("handover", y_h), ("duration", y_d)):
        if yv is None:
            continue
        prev = float(yv.mean())
        if not (L.PREV_LO <= prev <= L.PREV_HI):
            continue
        dd = d.copy()
        dd["_y"] = yv
        tr, te = dd.iloc[:cut], dd.iloc[cut:]
        yte = te["_y"].values
        if len(np.unique(yte)) < 2:
            continue
        rate = tr.groupby(tr[f].astype(str))["_y"].mean()
        prior = float(tr["_y"].mean())
        key_te = te[f].astype(str)
        score = key_te.map(rate).fillna(prior).values
        unseen = (float((~key_te.isin(rate.index)).mean())
                  if len(key_te) else np.nan)
        try:
            a_hist = roc_auc_score(yte, score)
            a_model = roc_auc_score(yte, L.fit(tr, te, b0 + [f]))
            a_b0 = roc_auc_score(yte, L.fit(tr, te, b0))
        except Exception as e:                              # noqa: BLE001
            print(f"  {key:18s} {tname:9s} failed {e}")
            continue
        hist_rows.append(dict(log=key, domain=C.LOGS[key][0], target=tname,
                              f=f, n_test=len(te), prevalence=prev,
                              auc_history=a_hist, auc_model=a_model,
                              auc_b0=a_b0,
                              share_of_model=(a_hist - 0.5) / (a_model - 0.5)
                              if a_model > 0.5 else np.nan,
                              unseen_share=unseen))
        print(f"  {key:18s} {tname:9s} {len(te):>8,} {a_hist:>8.4f} "
              f"{a_model:>11.4f} {a_b0:>7.4f} {unseen:>7.1%}")
HIS = pd.DataFrame(hist_rows)
HIS.to_csv(RESULTS / "r34_history.csv", index=False)

# ===================================================================== facts
det = pd.DataFrame(det_rows)
lay = pd.DataFrame(lay_rows) if lay_rows else pd.DataFrame()
facts = dict(
    n_hierarchies_attempted=len(HIERARCHIES),
    n_hierarchies_with_two_levels=int(lay.log.nunique()) if len(lay) else 0,
    n_deterministic_pairs=int(det.deterministic.sum()) if len(det) else 0,
    n_pairs_tested=int(len(det)),
    n_history_rows=len(HIS),
    history_auc_min=float(HIS.auc_history.min()) if len(HIS) else np.nan,
    history_auc_max=float(HIS.auc_history.max()) if len(HIS) else np.nan,
    history_share_min=float(HIS.share_of_model.min()) if len(HIS) else np.nan,
    history_share_max=float(HIS.share_of_model.max()) if len(HIS) else np.nan,
    n_history_beats_model=int((HIS.auc_history >= HIS.auc_model).sum())
    if len(HIS) else 0,
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r34_facts.csv", index=False)
if len(HIS):
    print(f"""
  Across {len(HIS)} log-target pairs the history score reaches AUC
  {HIS.auc_history.min():.4f} to {HIS.auc_history.max():.4f}, which is {HIS.share_of_model.min():.1%} to {HIS.share_of_model.max():.1%} of what the
  fitted B0+f model reaches above chance.  It matches or beats the model on
  {int((HIS.auc_history >= HIS.auc_model).sum())} of them.""")
print(f"\n  Wrote r34_layers.csv, r34_layer_determinism.csv, r34_history.csv, "
      f"r34_facts.csv  ({facts['runtime_s']:.0f}s)")

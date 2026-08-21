"""r37 -- FREE TEXT: A SEARCH, AND WHATEVER IT FINDS.

HANDOFF section 19.7 names free text as the largest untested threat to this
paper: Kapel et al. rank two free-text fields above the configuration item for
a related target, and if free text absorbs the item's value then the paper's
conclusion gets stronger and the register's measured value gets smaller.  The
published paper has no evidence either way, and neither of its two logs has a
description field.

This is therefore a SEARCH before it is an analysis, and PROTOCOL.md section 7
declares the criterion before the search runs.  An attribute is free text if,
on the training half:

    (i)   more than 40% of its non-missing values are unique;
    (ii)  its mean value length exceeds 20 characters;
    (iii) more than half of its values contain a space;

and, by amendment 7 (PROTOCOL.md section 10), which was added because the
three registered conditions admit a FORMATTED IDENTIFIER rather than prose:

    (iv)  more than half of its distinct forms survive having their digits
          stripped -- "request for payment 148214" collapses to one form and
          is not a description;
    (v)   it is populated on at least 50 training rows -- a column populated
          on one row is trivially 100% unique;
    (vi)  it survives the structural exclusions of section 3.1, which the
          first version of this search did not apply, and which is why it
          offered `Complete Timestamp` as a text field.

Every attribute of every log in the corpus is tested and the result is
recorded field by field, including the fields that fail and which condition
they fail.  A documented negative closes the question; an undocumented gap
invites a referee to assume nobody looked.

Where a field passes, the ladder is re-run with it admitted through a hashed
character n-gram encoder -- deliberately the dullest possible text model,
because the question is whether free text carries the item's value at all, not
how well a good text model does.

Outputs: results/r37_free_text.csv, r37_ladder.csv, r37_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
import r33_generic_ladder as L
from common import RESULTS

t0 = time.time()
MIN_UNIQUE = 0.40
MIN_MEAN_LEN = 20.0
MIN_SPACE = 0.50
N_FEATURES = 2 ** 16

# --- PROTOCOL.md section 10, amendment 7 (declared 2026-08-21) ------------
# The three registered conditions admit a FORMATTED IDENTIFIER.  Every BPI
# Challenge 2020 case carries `case:Rfp_id` = "request for payment 148214":
# 100% unique, 26 characters, always contains a space, and not prose -- all
# of its variation is one number.  A fourth condition, computed from feature
# values only: strip the digits, and a genuine description still varies.
# Expressed as a RATIO of distinct forms before and after stripping, because
# a share of rows is n-dependent -- the first version of this condition let
# `case:Rfp_id_4` through on 15 populated rows, where one surviving form out
# of fifteen values clears any small share threshold.
# The search also now applies the same structural exclusions section 3.1
# applies, which is why the first run offered `Complete Timestamp` as a text
# field.
MIN_DIGITSTRIP_RATIO = 0.50
# A column populated on one row cannot be assessed: one value is trivially
# 100% unique and its single digit-stripped form is 100% of the distinct
# forms.  BPI Challenge 2020's travel-permit log carries `case:Rfp_id_14`
# on a handful of rows and it cleared every other condition.
MIN_POPULATED = 50

ROLES = pd.read_csv(RESULTS / "r33_roles.csv")
ADMITTED = sorted(ROLES.log.unique())
ALL_LOGS = list(C.LOGS)


def roles_for(key):
    r = ROLES[ROLES.log == key]
    f = (r[r.role == "f_amended"].attribute.tolist()
         or r[r.role == "f_registered"].attribute.tolist())
    g = r[r.role == "g"].attribute.tolist()
    b0 = r[r.role == "B0"].attribute.tolist()
    return (f[0] if f else None), (g[0] if g else None), b0


print("=" * 92)
print("A. THE SEARCH  (every attribute of every log in the corpus)")
print("=" * 92)
print(f"  free text := unique > {MIN_UNIQUE:.0%}  AND  mean length > "
      f"{MIN_MEAN_LEN:.0f}  AND  contains a space > {MIN_SPACE:.0%}\n")

rows = []
for key in ALL_LOGS:
    try:
        d = C.load(key)
    except Exception as e:                                  # noqa: BLE001
        rows.append(dict(log=key, attribute="<load failed>",
                         detail=f"{type(e).__name__}: {e}"))
        continue
    d, _ = L.temporal_order(d)
    cut = int(len(d) * L.TRAIN_FRAC)
    tr = d.iloc[:cut]
    act = d["concept:name"] if "concept:name" in d.columns else None
    for c in d.columns:
        if c.startswith(("_seq_", "_t_")) or c in ("n_events", "duration_h"):
            continue
        col = tr[c]
        v = col[~C.is_missing(col)].astype(str)
        if len(v) == 0:
            continue
        # the structural exclusions of section 3.1 apply to the search too
        excluded = ""
        if L.base_name(c) in C.OUTCOME_FIELDS:
            excluded = "outcome-field"
        elif C.looks_like_timestamp(c, col):
            excluded = "timestamp"
        elif act is not None and C.is_activity_alias(d[c], act):
            excluded = "activity-alias"
        uniq = float(v.nunique() / len(v))
        mlen = float(v.str.len().mean())
        space = float(v.str.contains(" ", regex=False).mean())
        nod = v.str.replace(r"\d", "", regex=True).str.strip()
        uniq_nod = float(nod.nunique() / max(v.nunique(), 1))
        passes = [uniq > MIN_UNIQUE, mlen > MIN_MEAN_LEN, space > MIN_SPACE,
                  uniq_nod > MIN_DIGITSTRIP_RATIO, len(v) >= MIN_POPULATED]
        why = ", ".join(nm for nm, ok in
                        zip(("unique", "length", "space", "not-an-id",
                             "too-few-rows"), passes)
                        if not ok)
        if excluded:
            why = (why + ", " if why else "") + excluded
        rows.append(dict(log=key, attribute=c, n=len(v), unique_share=uniq,
                         mean_length=mlen, space_share=space,
                         digitstrip_ratio=uniq_nod,
                         structurally_excluded=excluded or "-",
                         is_free_text=bool(all(passes) and not excluded),
                         fails=why or "-",
                         example=str(v.iloc[0])[:60]))
FT = pd.DataFrame(rows)
FT.to_csv(RESULTS / "r37_free_text.csv", index=False)

hits = FT[FT.is_free_text.fillna(False)]
print(f"  {len(FT):,} attributes tested over {FT.log.nunique()} logs.")
print(f"  {len(hits)} pass all three conditions.\n")
if len(hits):
    print(f"  {'log':18s} {'attribute':26s} {'uniq':>6s} {'len':>7s} "
          f"{'space':>6s}  example")
    for _, r in hits.iterrows():
        print(f"  {r.log:18s} {r.attribute:26s} {r.unique_share:>6.1%} "
              f"{r.mean_length:>7.1f} {r.space_share:>6.1%}  {r.example[:34]}")

near = FT[(~FT.is_free_text.fillna(False)) & (FT.space_share > MIN_SPACE)
          & (FT.mean_length > MIN_MEAN_LEN)]
print(f"\n  Near misses -- prose-shaped but not unique enough to be free text: "
      f"{len(near)}")
for _, r in near.head(12).iterrows():
    print(f"    {r.log:18s} {r.attribute:26s} unique {r.unique_share:>6.1%} "
          f"(fails: {r.fails})   {r.example[:32]}")

# what the closest candidates in the ITSM logs actually are
print("\n  The fields a referee will ask about, by name:")
for lg, at in (("UCI498", "u_symptom"), ("UCI498", "cmdb_ci"),
               ("BPIC14", "KM number"), ("Helpdesk", "product"),
               ("Sepsis", "Diagnose"), ("BPIC19", "case:Name")):
    r = FT[(FT.log == lg) & (FT.attribute == at)]
    if r.empty:
        print(f"    {lg:10s} {at:14s} not present in the parsed log")
    else:
        r = r.iloc[0]
        print(f"    {lg:10s} {at:14s} unique {r.unique_share:>6.1%}  "
              f"len {r.mean_length:>5.1f}  space {r.space_share:>6.1%}  "
              f"free text: {'YES' if r.is_free_text else 'no (' + r.fails + ')'}")

# ===================================================================== B
print("\n" + "=" * 92)
print("B. THE LADDER WITH TEXT ADMITTED")
print("=" * 92)
lad_rows = []
targets_done = 0
if hits.empty:
    print("""  No attribute in any of the 22 logs in the corpus satisfies the
  declared criterion.  That is the finding, and it is recorded as one: the
  public process-mining corpus does not contain a free-text description
  field on a log that also carries a reusable high-cost entity and a free
  per-event resource stamp.  The threat HANDOFF section 19.7 names as the
  largest remaining one CANNOT be tested on public data, and the paper says
  so with this search attached rather than with a sentence of regret.""")
else:
    def fit_mixed(tr, te, oh_cols, text_col):
        e = OneHotEncoder(handle_unknown="ignore")
        Xa = e.fit_transform(tr[oh_cols].astype(str))
        Xb = e.transform(te[oh_cols].astype(str))
        if text_col is not None:
            h = HashingVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                  n_features=N_FEATURES, alternate_sign=False,
                                  norm="l2")
            Ta = h.transform(tr[text_col].astype(str))
            Tb = h.transform(te[text_col].astype(str))
            Xa, Xb = sparse.hstack([Xa, Ta]).tocsr(), sparse.hstack([Xb, Tb]).tocsr()
        m = LogisticRegression(max_iter=3000, C=1.0).fit(Xa, tr["_y"].values)
        return m.predict_proba(Xb)[:, 1]

    for lg in sorted(hits.log.unique()):
        if lg not in ADMITTED:
            print(f"\n  {lg}: has free text but is not admitted by the "
                  f"protocol ladder; text reported, no ladder")
            continue
        f, g, b0 = roles_for(lg)
        d = C.load(lg)
        d, _ = L.temporal_order(d)
        cut = int(len(d) * L.TRAIN_FRAC)
        seq = next((c for c in d.columns if c.startswith("_seq_")
                    and c[5:].lower() == str(g).lower()), None)
        if seq is None:
            continue
        y_h, y_d, _ = L.targets(d, seq, cut)
        for tname, yv in (("handover", y_h), ("duration", y_d)):
            if yv is None or not (L.PREV_LO <= yv.mean() <= L.PREV_HI):
                continue
            dd = d.copy()
            dd["_y"] = yv
            tr, te = dd.iloc[:cut], dd.iloc[cut:]
            yte = te["_y"].values
            if len(np.unique(yte)) < 2:
                continue
            for txt in hits[hits.log == lg].attribute:
                if txt in (f, g) or txt in b0:
                    continue
                a_b0 = roc_auc_score(yte, fit_mixed(tr, te, b0, None))
                a_b0f = roc_auc_score(yte, fit_mixed(tr, te, b0 + [f], None))
                a_bt = roc_auc_score(yte, fit_mixed(tr, te, b0, txt))
                a_btf = roc_auc_score(yte, fit_mixed(tr, te, b0 + [f], txt))
                a_bg = roc_auc_score(yte, fit_mixed(tr, te, b0 + [g], None))
                a_bgf = roc_auc_score(yte, fit_mixed(tr, te, b0 + [g, f], None))
                a_bgt = roc_auc_score(yte, fit_mixed(tr, te, b0 + [g], txt))
                a_bgtf = roc_auc_score(yte, fit_mixed(tr, te, b0 + [g, f], txt))
                lad_rows.append(dict(
                    log=lg, target=tname, text_field=txt, f=f, g=g,
                    n_test=len(te),
                    auc_b0=a_b0, auc_b0f=a_b0f, auc_b0t=a_bt, auc_b0tf=a_btf,
                    auc_b0g=a_bg, auc_b0gf=a_bgf, auc_b0gt=a_bgt,
                    auc_b0gtf=a_bgtf,
                    v_no_text=a_bgf - a_bg, v_with_text=a_bgtf - a_bgt,
                    reduction_from_text=(1 - (a_bgtf - a_bgt) / (a_bgf - a_bg))
                    if (a_bgf - a_bg) > 0 else np.nan))
                targets_done += 1
                print(f"  {lg} [{tname}] text={txt}")
                print(f"    item over intake+group, text OMITTED   "
                      f"{a_bgf - a_bg:+.4f}")
                print(f"    item over intake+group, text ADMITTED  "
                      f"{a_bgtf - a_bgt:+.4f}")
                print(f"    reduction from admitting the text     "
                      f"{lad_rows[-1]['reduction_from_text']:.3f}")
if lad_rows:
    pd.DataFrame(lad_rows).to_csv(RESULTS / "r37_ladder.csv", index=False)

facts = dict(
    n_attributes_tested=len(FT), n_logs=int(FT.log.nunique()),
    n_free_text=int(len(hits)),
    n_free_text_logs=int(hits.log.nunique()) if len(hits) else 0,
    n_near_miss=int(len(near)),
    min_unique=MIN_UNIQUE, min_mean_len=MIN_MEAN_LEN, min_space=MIN_SPACE,
    min_digitstrip_ratio=MIN_DIGITSTRIP_RATIO,
    min_populated=MIN_POPULATED,
    n_structurally_excluded=int((FT.structurally_excluded != "-").sum()),
    n_ladders=len(lad_rows),
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r37_facts.csv", index=False)
print(f"\n  Wrote r37_free_text.csv ({len(FT):,} rows), r37_facts.csv"
      + (", r37_ladder.csv" if lad_rows else "")
      + f"  ({facts['runtime_s']:.0f}s)")

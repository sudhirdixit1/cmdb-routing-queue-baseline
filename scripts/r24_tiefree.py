"""
r24 -- IS THE OPERATIONAL FACTOR RANK RESOLUTION, OR INFORMATION?

The paper concedes the objection and then does not answer it.  Section 8
reports that the naive baseline -- four low-cardinality intake fields, one of
them the provably redundant Priority column -- emits only 23 distinct scores
over 13,637 test incidents, so at 5% capacity 47 rows sit strictly above the
cut and the remaining 635 are drawn from a tied block of 1,944.  It then
says "we have not separated the two" and moves on.  A referee who reads that
sentence has been handed the paper's weakest number and told the authors know
it is weak.  Separate them.

Two decompositions, neither of which needs a new estimator family.

A.  A TIE-FREE NAIVE BASELINE.  Re-represent the intake block by cross-fitted
    target encoding, exactly the machinery r10 already uses for the item
    column: fitted on training only, out-of-fold for training rows, so no row
    sees its own outcome.  Two variants:

      per-field   each of the four intake fields encoded separately -> four
                  continuous columns
      composite   the four-tuple encoded as ONE high-cardinality column ->
                  one continuous column, one distinct score per observed
                  intake combination, ordered by its own empirical rate

    The composite variant is the finest ranking the intake information can
    support.  If the factor survives it, the factor is not an artifact of
    coarse scores.

    Both arms of a contrast must move together, so section A reports the
    factor with the naive arm re-encoded alone AND with both arms re-encoded.

B.  ORACLE TIE-BREAKING.  A bound, not an estimator.  Break every tie in
    every model in the order that maximises catches -- positives first inside
    each tied block -- which uses the outcome and is therefore unavailable to
    any analyst.  It removes rank resolution as an explanation by
    construction.  Whatever factor survives is information.  The adversarial
    policy (negatives first) gives the other end, so the pair brackets
    everything tie-breaking can do.

WHAT WOULD SINK THE PAPER'S SECTION 8: the factor collapsing under either
repair.  Then the "several-fold overstatement" is a statement about score
granularity and the operational framing should be withdrawn, leaving the AUC
ratio of 1.8.

IT SANK IT.  Recorded here at the top so no reader of this file has to reach
section D to find out.  (i) The encoding repair is impossible: the intake
block admits 23 distinct combinations, so no function of those four fields
can rank 13,637 incidents into more than 23 classes, and the target-encoded
baseline emits FEWER distinct scores than the one-hot one, not more.  (ii)
Under oracle tie-breaking the naive contrast REVERSES SIGN.  A quantity whose
sign is set by the order of rows inside a tied block is not a measurement of
information.  The paper withdraws the factor; section 8 is rebuilt on the
decision curve, where a threshold admits or excludes a whole tied block and
the question does not arise.  The honest arm's extra catches survive every
policy, so what is withdrawn is the RATIO, not the item's value.

Everything is held to r4_final and to r11: same cohort, same split, same
capacities, same 400-draw paired bootstrap with ties re-broken every draw.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder, TargetEncoder

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_CAP_BOOT = 400
CAPACITIES = (0.05, 0.10, 0.20)
Q = "intake_group"
BQ = M.INTAKE + [Q]

D, TR, TE, y = M.D, M.TR, M.TE, M.y


# ------------------------------------------------------------ encodings
def te_columns(tr, te, cols, composite=False, seed=SEED):
    """Cross-fitted target encoding.  Fitted on TRAINING ONLY.

    fit_transform returns out-of-fold encodings for the training rows, so no
    training row sees its own outcome; transform applies the full-training
    encoding to test.  Unseen levels fall back to the training prior.
    """
    a = tr[cols].astype(str)
    b = te[cols].astype(str)
    if composite:
        a = a.agg("\x1f".join, axis=1).to_frame("_k")
        b = b.agg("\x1f".join, axis=1).to_frame("_k")
    enc = TargetEncoder(target_type="binary", smooth="auto", cv=5,
                        random_state=seed)
    return (enc.fit_transform(a.values, tr._y.values),
            enc.transform(b.values))


def fit_mixed(tr, te, te_cols, oh_cols, composite=False):
    """Logistic regression on target-encoded columns plus one-hot columns."""
    Xa, Xb = te_columns(tr, te, te_cols, composite=composite)
    if oh_cols:
        oh = OneHotEncoder(handle_unknown="ignore")
        Xa = np.hstack([Xa, oh.fit_transform(tr[oh_cols].astype(str)).toarray()])
        Xb = np.hstack([Xb, oh.transform(te[oh_cols].astype(str)).toarray()])
    m = LogisticRegression(max_iter=3000, C=1.0).fit(Xa, tr._y.values)
    return m.predict_proba(Xb)[:, 1]


# ------------------------------------------------------------ detection
def caught(p, yy, frac, policy, rng=None):
    """Positives in the top `frac`, ties broken by `policy`.

    random       the paper's, and the only implementable one
    oracle       positives first inside every tie block   (uses the outcome)
    adversarial  negatives first inside every tie block   (uses the outcome)
    """
    k = int(round(len(p) * frac))
    if policy == "random":
        o = rng.permutation(len(p))
        sel = o[np.argsort(-p[o], kind="stable")][:k]
    else:
        sgn = -1.0 if policy == "oracle" else 1.0
        sel = np.lexsort((sgn * yy, -p))[:k]
    return int(yy[sel].sum())


def factor_at(preds, frac, policy, n_boot=N_CAP_BOOT, seed=SEED):
    """Point estimate and interval for one capacity under one tie policy.

    Point estimates are the MEDIAN over the same draws the interval uses,
    which is r11's discipline: a single tie-break draw moves the counts by
    twenty or more.
    """
    hb, nb, fb = [], [], []
    for rep in range(n_boot):
        r = np.random.default_rng(seed + 1000 + rep)
        i = r.integers(0, len(y), len(y))
        yy = y[i]
        if len(np.unique(yy)) < 2:
            continue
        a = caught(preds["hb"][i], yy, frac, policy, r)
        b = caught(preds["hf"][i], yy, frac, policy, r)
        c = caught(preds["nb"][i], yy, frac, policy, r)
        d = caught(preds["nf"][i], yy, frac, policy, r)
        hb.append(b - a); nb.append(d - c)
        if (b - a) > 0:
            fb.append((d - c) / (b - a))
    hb, nb, fb = np.array(hb), np.array(nb), np.array(fb)
    h, n = int(round(np.median(hb))), int(round(np.median(nb)))
    flo, fhi = (np.percentile(fb, [2.5, 97.5]) if len(fb) > 20
                else (np.nan, np.nan))
    return dict(honest_extra=h, naive_extra=n,
                honest_lo=float(np.percentile(hb, 2.5)),
                honest_hi=float(np.percentile(hb, 97.5)),
                naive_lo=float(np.percentile(nb, 2.5)),
                naive_hi=float(np.percentile(nb, 97.5)),
                factor=n / h if h else np.nan,
                factor_lo=float(flo), factor_hi=float(fhi),
                frac_pos=len(fb) / max(len(hb), 1))


# ------------------------------------------------------------ the models
BASE = dict(
    nb=M.fit(TR, TE, M.INTAKE),                 # naive baseline  (paper's)
    nf=M.fit(TR, TE, M.INTAKE + [M.IDENT]),     # naive treatment
    hb=M.fit(TR, TE, BQ),                       # honest baseline
    hf=M.fit(TR, TE, BQ + [M.IDENT]),           # honest treatment
)
PER = dict(
    nb=fit_mixed(TR, TE, M.INTAKE, []),
    nf=fit_mixed(TR, TE, M.INTAKE, [M.IDENT]),
    hb=fit_mixed(TR, TE, M.INTAKE, [Q]),
    hf=fit_mixed(TR, TE, M.INTAKE, [Q, M.IDENT]),
)
CMP = dict(
    nb=fit_mixed(TR, TE, M.INTAKE, [], composite=True),
    nf=fit_mixed(TR, TE, M.INTAKE, [M.IDENT], composite=True),
    hb=fit_mixed(TR, TE, M.INTAKE, [Q], composite=True),
    hf=fit_mixed(TR, TE, M.INTAKE, [Q, M.IDENT], composite=True),
)
#  Naive arm re-encoded, honest arm left exactly as the paper has it.  This
#  is the variant that answers the objection as it is actually put: it is the
#  NAIVE baseline whose coarseness is alleged to manufacture the factor.
MIX = dict(nb=CMP["nb"], nf=CMP["nf"], hb=BASE["hb"], hf=BASE["hf"])

REPS = [("A0 paper, one-hot intake", BASE),
        ("A1 intake target-encoded, per field", PER),
        ("A2 intake target-encoded, composite", CMP),
        ("A3 naive arm re-encoded only", MIX)]

print("=" * 92)
print("A. HOW FINELY DOES EACH BASELINE RANK?")
print("=" * 92)
n_combo = TE[M.INTAKE].astype(str).agg("\x1f".join, axis=1).nunique()
n_combo_tr = TR[M.INTAKE].astype(str).agg("\x1f".join, axis=1).nunique()
print(f"  distinct intake combinations, training {n_combo_tr}   test {n_combo}")
print(f"  test rows {len(y):,}\n")
print(f"  {'representation':38s} {'naive base':>11s} {'naive+item':>11s} "
      f"{'honest base':>12s} {'AUC naive':>10s}")
res_scores = []
for nm, pr in REPS:
    d = {k: len(np.unique(v)) for k, v in pr.items()}
    a_nb = roc_auc_score(y, pr["nb"])
    res_scores.append(dict(representation=nm, distinct_naive_base=d["nb"],
                           distinct_naive_full=d["nf"],
                           distinct_honest_base=d["hb"],
                           auc_naive_base=a_nb,
                           auc_naive_full=roc_auc_score(y, pr["nf"]),
                           auc_honest_base=roc_auc_score(y, pr["hb"]),
                           auc_honest_full=roc_auc_score(y, pr["hf"])))
    print(f"  {nm:38s} {d['nb']:>11,} {d['nf']:>11,} {d['hb']:>12,} "
          f"{a_nb:>10.4f}")
SC = pd.DataFrame(res_scores)
SC.to_csv(RESULTS / "r24_scores.csv", index=False)
_oh, _cm = int(SC.iloc[0].distinct_naive_base), int(SC.iloc[2].distinct_naive_base)
print(f"\n  THE REPAIR FAILS, AND ITS FAILURE IS THE ANSWER.  Target encoding")
print(f"  does not make the naive baseline rank more finely: it emits {_cm}")
print(f"  distinct scores against the one-hot model's {_oh}, and moves its AUC")
print(f"  by {SC.iloc[2].auc_naive_base - SC.iloc[0].auc_naive_base:+.4f}.  It cannot do better.  The intake block")
print(f"  admits {n_combo_tr} distinct combinations in training and {n_combo} in test; every")
print(f"  row sharing a combination must share a score under ANY function of")
print(f"  those four fields, and combinations unseen in training collapse onto")
print(f"  the prior, which is why the encoded count is the smaller of the two.")
print(f"\n  So the tie block is not an artifact of the estimator.  It is what")
print(f"  having four low-cardinality intake fields IS.  A reader who objects")
print(f"  that the factor is rank resolution rather than information is not")
print(f"  describing a defect in our measurement; they are describing the")
print(f"  baseline an analyst would actually build.  Whether that makes the")
print(f"  factor reportable is settled in section C, not here.")

print("\n" + "=" * 92)
print("A2. WHAT IS IN THE TIE BLOCK")
print("=" * 92)
tie_rows = []
for nm, key in (("naive: intake", "nb"), ("honest: intake + group", "hb")):
    p = BASE[key]
    for frac in CAPACITIES:
        k = int(round(len(p) * frac))
        cut = np.sort(p)[::-1][k - 1]
        above = p > cut
        tied = p == cut
        n_above, n_tied = int(above.sum()), int(tied.sum())
        from_tie = k - n_above
        rate_tie = float(y[tied].mean()) if n_tied else np.nan
        # a draw of `from_tie` rows from the tie block catches this many, in
        # expectation, and that expectation is a property of the block --
        # nothing the model knows enters it.
        exp = int(y[above].sum()) + from_tie * rate_tie
        tie_rows.append(dict(model=nm, capacity=frac, reviewed=k,
                             strictly_above=n_above, tie_block=n_tied,
                             drawn_from_tie=from_tie,
                             share_from_tie=from_tie / k,
                             rate_in_tie=rate_tie, rate_overall=float(y.mean()),
                             caught_above=int(y[above].sum()),
                             expected_total=exp))
        if frac == 0.05:
            print(f"  {nm:24s} at {frac:.0%}: review {k:,}; {n_above:,} strictly "
                  f"above the cut,")
            print(f"  {'':24s} {from_tie:,} drawn from a tied block of "
                  f"{n_tied:,} ({from_tie/k:.1%} of the review budget)")
            print(f"  {'':24s} that block is reassigned at {rate_tie:.3f} "
                  f"against {y.mean():.3f} overall")
            print(f"  {'':24s} expected catches: {exp:.0f}\n")
TB = pd.DataFrame(tie_rows)
TB.to_csv(RESULTS / "r24_tie_block.csv", index=False)
_n5 = TB[(TB.model == "naive: intake") & (TB.capacity == 0.05)].iloc[0]
print(f"  {_n5.share_from_tie:.0%} of what the naive baseline nominates at 5% capacity is a")
print(f"  draw from one tied block.  How many reassignment-bound incidents")
print(f"  that draw yields is fixed by the block's own base rate and by")
print(f"  nothing the model knows.  Section C prices that.")

print("\n" + "=" * 92)
print("B. THE FACTOR UNDER EACH REPRESENTATION  (ties broken at random)")
print("=" * 92)
def fmt_row(r):
    """The three cells shared by sections B and C.

    Built outside the f-string: the nested-quote form this replaced was a
    syntax error on Python 3.10 and cost a run.
    """
    h = "%+d [%+.0f,%+.0f]" % (r["honest_extra"], r["honest_lo"], r["honest_hi"])
    n = "%+d [%+.0f,%+.0f]" % (r["naive_extra"], r["naive_lo"], r["naive_hi"])
    f = "%.1f [%.1f,%.1f]" % (r["factor"], r["factor_lo"], r["factor_hi"])
    return "%18s %20s %18s" % (h, n, f)


print(f"  {'representation':38s} {'cap':>5s} {'honest':>18s} {'naive':>20s} "
      f"{'factor':>18s}")
rows = []
for nm, pr in REPS:
    for frac in CAPACITIES:
        r = factor_at(pr, frac, "random")
        rows.append(dict(representation=nm, capacity=frac, policy="random", **r))
        print(f"  {nm:38s} {frac:>5.0%} " + fmt_row(r))

print("\n" + "=" * 92)
print("C. ORACLE AND ADVERSARIAL TIE-BREAKING  (bounds, not estimators)")
print("=" * 92)
print("  Both policies use the outcome to order rows inside a tied block and")
print("  are therefore unavailable to an analyst.  Together they bracket")
print("  everything tie resolution can do to the reported factor.\n")
print(f"  {'policy':14s} {'cap':>5s} {'honest':>18s} {'naive':>20s} "
      f"{'factor':>18s}")
for policy in ("oracle", "adversarial"):
    for frac in CAPACITIES:
        r = factor_at(BASE, frac, policy)
        rows.append(dict(representation="A0 paper, one-hot intake",
                         capacity=frac, policy=policy, **r))
        print(f"  {policy:14s} {frac:>5.0%} " + fmt_row(r))
F = pd.DataFrame(rows)
F.to_csv(RESULTS / "r24_factor.csv", index=False)

print("\n" + "=" * 92)
print("D. THE VERDICT, WHICH GOES AGAINST US")
print("=" * 92)
f5 = F[(F.capacity == 0.05)]


def _pick(rep, pol, col="factor"):
    return float(f5[(f5.representation == rep) & (f5.policy == pol)][col].iloc[0])


PAPER_REP = "A0 paper, one-hot intake"
f_paper = _pick(PAPER_REP, "random")
n_paper = _pick(PAPER_REP, "random", "naive_extra")
h_paper = _pick(PAPER_REP, "random", "honest_extra")
n_or, h_or = _pick(PAPER_REP, "oracle", "naive_extra"), _pick(PAPER_REP, "oracle", "honest_extra")
n_ad, h_ad = _pick(PAPER_REP, "adversarial", "naive_extra"), _pick(PAPER_REP, "adversarial", "honest_extra")
f_cmp = _pick("A2 intake target-encoded, composite", "random")
f_mix = _pick("A3 naive arm re-encoded only", "random")
auc_ratio = ((roc_auc_score(y, BASE["nf"]) - roc_auc_score(y, BASE["nb"]))
             / (roc_auc_score(y, BASE["hf"]) - roc_auc_score(y, BASE["hb"])))
print("  at 5% review capacity, extra reassignment-bound incidents surfaced:\n")
print(f"  {'tie policy':16s} {'naive arm':>12s} {'honest arm':>12s} {'factor':>10s}")
print(f"  {'random (paper)':16s} {n_paper:>+12.0f} {h_paper:>+12.0f} {f_paper:>10.1f}")
print(f"  {'oracle':16s} {n_or:>+12.0f} {h_or:>+12.0f} "
      f"{_pick(PAPER_REP, 'oracle'):>10.1f}")
print(f"  {'adversarial':16s} {n_ad:>+12.0f} {h_ad:>+12.0f} "
      f"{_pick(PAPER_REP, 'adversarial'):>10.1f}")
print(f"\n  re-encoding the naive arm alone           factor {f_mix:.1f}")
print(f"  re-encoding both arms, composite          factor {f_cmp:.1f}")
print(f"  the same contrast measured as AUC         ratio  {auc_ratio:.1f}")

print(f"""
  READ THIS AGAINST THE PAPER.  Section 8 reports the factor as {f_paper:.1f} and
  says the omission overstates the operational gain several-fold.  That
  number does not survive.

  The naive arm's extra catches move from {n_or:+.0f} to {n_ad:+.0f} -- a range that
  spans zero and reverses the sign of the contrast -- purely by changing
  the order of rows INSIDE a tied block, without changing one thing any
  model knows.  The honest arm moves from {h_or:+.0f} to {h_ad:+.0f} over the same
  policies.  A quantity whose sign is set by how a coin lands inside a
  {int(_n5.tie_block):,}-row block is not a measurement of information.

  Section A rules out the obvious repair: the block cannot be made
  smaller, because it is the intake block's {n_combo_tr} combinations.  So the
  factor cannot be rescued by a better representation either.

  WHAT SURVIVES.  The honest arm's extra catches are positive under every
  policy including the oracle ({h_or:+.0f} [{_pick(PAPER_REP, 'oracle', 'honest_lo'):+.0f},"""
      f"""{_pick(PAPER_REP, 'oracle', 'honest_hi'):+.0f}]), so knowing the item does
  surface more incidents than the group-aware baseline at this capacity.
  What does not survive is the RATIO, and with it the claim that the
  omission overstates the operational gain by more than it overstates the
  AUC gain.  The paper must withdraw the factor and report the operational
  question with an instrument that does not require the baseline to rank
  inside its ties.  Decision curve analysis (r23) is that instrument: a
  threshold either admits a whole tied block or excludes it.""")
pd.DataFrame([dict(
    factor_paper=f_paper, factor_naive_reencoded=f_mix,
    factor_both_reencoded=f_cmp,
    factor_oracle=_pick(PAPER_REP, "oracle"),
    factor_adversarial=_pick(PAPER_REP, "adversarial"),
    naive_random=n_paper, naive_oracle=n_or, naive_adversarial=n_ad,
    honest_random=h_paper, honest_oracle=h_or, honest_adversarial=h_ad,
    honest_oracle_lo=_pick(PAPER_REP, "oracle", "honest_lo"),
    honest_oracle_hi=_pick(PAPER_REP, "oracle", "honest_hi"),
    auc_ratio=auc_ratio,
    n_intake_combos_test=int(n_combo), n_intake_combos_train=int(n_combo_tr),
    distinct_onehot=_oh, distinct_composite=_cm,
)]).to_csv(RESULTS / "r24_decomposition.csv", index=False)
print("\ndone.  wrote r24_scores.csv, r24_tie_block.csv, r24_factor.csv, "
      "r24_decomposition.csv")

"""r30 -- THE INSTRUMENT MATRIX.

The paper's headline is a *reduction*: admitting one already-recorded free
field to the baseline cuts the measured value of item identity by 36.1-48.3%.
That number is stated in ROC AUC.  Round sixteen then measured the same
quantity in net benefit and got 1.07 where AUC gives 1.8, which is the
referee's opening: the authors' own preferred instrument contradicts their own
headline.

The answer is not to pick a winner.  It is to measure the reduction under
EVERY defensible instrument and report the dependence, because the dependence
is itself the finding: an incremental-value claim silently fixes a metric, and
different metrics do not agree about how much a feature is worth.

WHAT IS MEASURED.  Two rungs of the admissibility ladder, held to r4_final's
cohort, split, intake block, estimator and seed:

    naive contrast    V(item | intake)               -- the free field omitted
    honest contrast   V(item | intake + group)       -- the free field admitted
    reduction         1 - honest / naive

under seven instruments:

    ROC AUC                     the paper's current headline; rank-based,
                                integrates over every operating point
    Average precision           the standard answer when the positive class is
                                what the desk cares about; also rank-based
    Net benefit (Vickers)       decision-analytic; needs an exchange rate
    Brier skill                 proper scoring rule; sees calibration, which
                                no rank-based measure can
    Nagelkerke R^2              the predictiveness family of williamson2021vimp
    Detection at capacity       WITHDRAWN as a headline in round sixteen and
                                kept here on purpose: the matrix is the right
                                place to show what a tie-degenerate instrument
                                does to a ratio
    Expected cost               what a buyer actually optimises

ONE OF THOSE SEVEN IS NOT INDEPENDENT.  Section D proves, numerically and
algebraically, that expected cost at cost ratio r is r times net benefit at
the Bayes threshold 1/(1+r), so the two give the SAME reduction to machine
precision.  We report it rather than presenting seven instruments when we
have six, because a matrix that double-counts an axis overstates its own
coverage.

INTERVALS.  Every reduction carries a paired bootstrap interval: one set of
resampled test-row indices per draw, shared by all four models, so the four
scores move together the way they do in the data.  Ratios are reported with
the fraction of draws in which the denominator is positive; where that
fraction is not 1 the interval is not a confidence interval for a ratio and
we say so instead of printing one.

Outputs: results/r30_instruments.csv, r30_reduction.csv, r30_nb_grid.csv,
         r30_cost_identity.csv, r30_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base14 as B
from common import RESULTS

SEED = B.SEED
N_BOOT = B.N_BOOT                      # 2000, as everywhere else in this repo
GRID = np.round(np.arange(0.05, 0.8001, 0.025), 4)   # r23's grid, unchanged
NAMED_T = (0.20, 0.30, 0.325, 0.40, 0.50)
CAPACITIES = (0.05, 0.10, 0.20)
COST_RATIOS = (1.0, 2.0, 3.0, 5.0, 10.0)   # cost(false negative) / cost(false positive)
N_CAP_BOOT = 400                       # r24's budget; ties are re-broken per draw
EPS = 1e-12

t0 = time.time()

TR, TE, y = B.TR, B.TE, B.y
n = len(y)
prev_tr = float(TR._y.mean())          # the null model a test-set score is beaten against
prev_te = float(y.mean())

MODELS = {
    "intake":                 B.INTAKE,
    "intake + item":          B.INTAKE + [B.IDENT],
    "intake + group":         B.BQ,
    "intake + group + item":  B.BQ + [B.IDENT],
}
P = {k: B.fit(TR, TE, v) for k, v in MODELS.items()}

# naive contrast omits the free field; honest contrast admits it
CONTRASTS = {"naive":  ("intake", "intake + item"),
             "honest": ("intake + group", "intake + group + item")}


# ---------------------------------------------------------------- instruments
def _ll(p, yy, w=None):
    pc = np.clip(p, EPS, 1 - EPS)
    t = yy * np.log(pc) + (1 - yy) * np.log(1 - pc)
    return float(np.average(t, weights=w) * (len(yy) if w is None else w.sum()))


def brier(p, yy, w=None):
    return float(np.average((p - yy) ** 2, weights=w))


def brier_skill(p, yy, w=None):
    """1 - Brier(model) / Brier(null).  Null is the TRAINING prevalence, so the
    score is genuinely out of sample; a test-set null would be an oracle."""
    b0 = float(np.average((prev_tr - yy) ** 2, weights=w))
    return 1.0 - brier(p, yy, w) / b0


def nagelkerke(p, yy, w=None):
    """Out-of-sample Nagelkerke R^2 against the training-prevalence null."""
    nn = float(len(yy) if w is None else w.sum())
    ll_m = _ll(p, yy, w)
    ll_0 = _ll(np.full_like(p, prev_tr), yy, w)
    cs = 1.0 - np.exp((2.0 / nn) * (ll_0 - ll_m))
    return float(cs / (1.0 - np.exp((2.0 / nn) * ll_0)))


def net_benefit(p, yy, thr, w=None):
    """Vickers-Elkin net benefit: TP/n - (FP/n) * p_t/(1-p_t)."""
    act = p >= thr
    ww = np.ones(len(yy)) if w is None else w
    nn = ww.sum()
    tp = float((ww * act * (yy == 1)).sum())
    fp = float((ww * act * (yy == 0)).sum())
    return (tp - fp * (thr / (1.0 - thr))) / nn


def expected_cost_saving(p, yy, ratio, w=None):
    """Cost avoided per case against treat-none, at cost ratio `ratio`, acting
    at that ratio's Bayes threshold 1/(1+ratio).  Higher is better."""
    thr = 1.0 / (1.0 + ratio)
    act = p >= thr
    ww = np.ones(len(yy)) if w is None else w
    nn = ww.sum()
    fn = float((ww * (~act) * (yy == 1)).sum())
    fp = float((ww * act * (yy == 0)).sum())
    pos = float((ww * (yy == 1)).sum())
    return (pos * ratio - (fn * ratio + fp)) / nn


def caught(p, yy, frac, policy, rng=None):
    """Positives in the top `frac` of the ranking; r24's tie policies."""
    k = int(round(len(p) * frac))
    if policy == "random":
        o = rng.permutation(len(p))
        sel = o[np.argsort(-p[o], kind="stable")][:k]
    else:
        sgn = -1.0 if policy == "oracle" else 1.0
        sel = np.lexsort((sgn * yy, -p))[:k]
    return int(yy[sel].sum())


# ---------------------------------------------------- A. the point estimates
print("=" * 92)
print("A. THE FOUR MODELS UNDER EVERY INSTRUMENT")
print("=" * 92)
print(f"  cohort {len(B.D):,} incidents, test half {n:,}, "
      f"train prevalence {prev_tr:.4f}, test prevalence {prev_te:.4f}\n")

rows = []
for name, p in P.items():
    rec = dict(model=name,
               auc=roc_auc_score(y, p),
               ap=average_precision_score(y, p),
               brier=brier(p, y),
               brier_skill=brier_skill(p, y),
               nagelkerke=nagelkerke(p, y),
               n_distinct_scores=int(len(np.unique(np.round(p, 12)))))
    for t in NAMED_T:
        rec[f"nb_{t}"] = net_benefit(p, y, t)
    for r in COST_RATIOS:
        rec[f"cost_saved_r{r:g}"] = expected_cost_saving(p, y, r)
    rows.append(rec)
INST = pd.DataFrame(rows)
INST.to_csv(RESULTS / "r30_instruments.csv", index=False)

print(f"  {'model':24s} {'AUC':>7s} {'AP':>7s} {'Brier':>8s} {'BrierSk':>8s} "
      f"{'NagelR2':>8s} {'NB@.30':>8s} {'scores':>7s}")
for _, r in INST.iterrows():
    print(f"  {r.model:24s} {r.auc:>7.4f} {r.ap:>7.4f} {r.brier:>8.4f} "
          f"{r.brier_skill:>8.4f} {r.nagelkerke:>8.4f} {r['nb_0.3']:>8.4f} "
          f"{r.n_distinct_scores:>7d}")
print("\n  The score-count column is the tie-degeneracy round sixteen found:")
print(f"  the intake block emits {int(INST.iloc[0].n_distinct_scores)} distinct scores for "
      f"{n:,} incidents, so no")
print("  function of it can rank them into more classes than that.")

# ------------------------------------------------ B. the reduction, bootstrapped
print("\n" + "=" * 92)
print("B. THE REDUCTION UNDER EACH INSTRUMENT  (paired bootstrap, "
      f"{N_BOOT:,} draws)")
print("=" * 92)
print("""  reduction = 1 - (value the item adds over intake+group)
                    / (value the item adds over intake alone)

  A reduction near 1 means the free field absorbs nearly everything the item
  was credited with.  A reduction near 0 means the two carry different
  information.  The paper's AUC number is 43.7%.\n""")

# pre-sort each model once; a threshold cut is then a fixed rank position and
# every bootstrap draw is a weighted cumulative sum over that fixed order.
ORDER, YS, CUT = {}, {}, {}
for name, p in P.items():
    o = np.argsort(-p, kind="stable")
    ORDER[name] = o
    YS[name] = y[o].astype(float)
    ps = p[o]
    CUT[name] = np.array([int(np.searchsorted(-ps, -t, side="right"))
                          for t in GRID])


def nb_grid_weighted(name, w):
    """Net benefit over the whole grid for one model under bootstrap weights."""
    ws = w[ORDER[name]]
    ctp = np.concatenate(([0.0], np.cumsum(ws * YS[name])))
    cfp = np.concatenate(([0.0], np.cumsum(ws * (1.0 - YS[name]))))
    c = CUT[name]
    tp, fp = ctp[c], cfp[c]
    return (tp - fp * (GRID / (1.0 - GRID))) / w.sum()


def instruments_weighted(w):
    out = {}
    for name, p in P.items():
        out[(name, "auc")] = roc_auc_score(y, p, sample_weight=w)
        out[(name, "ap")] = average_precision_score(y, p, sample_weight=w)
        out[(name, "brier_skill")] = brier_skill(p, y, w)
        out[(name, "nagelkerke")] = nagelkerke(p, y, w)
        g = nb_grid_weighted(name, w)
        for i, t in enumerate(GRID):
            out[(name, f"nb_{t}")] = g[i]
        for r in COST_RATIOS:
            out[(name, f"cost_r{r:g}")] = expected_cost_saving(p, y, r, w)
    return out


SCALARS = ["auc", "ap", "brier_skill", "nagelkerke"]
NBKEYS = [f"nb_{t}" for t in GRID]
COSTKEYS = [f"cost_r{r:g}" for r in COST_RATIOS]
ALLKEYS = SCALARS + NBKEYS + COSTKEYS

rng = np.random.default_rng(SEED)
draws = {k: {"naive": [], "honest": []} for k in ALLKEYS}
kept = 0
for b in range(N_BOOT):
    i = rng.integers(0, n, n)
    if len(np.unique(y[i])) < 2:
        continue
    w = np.bincount(i, minlength=n).astype(float)
    v = instruments_weighted(w)
    for k in ALLKEYS:
        for cname, (lo_m, hi_m) in CONTRASTS.items():
            draws[k][cname].append(v[(hi_m, k)] - v[(lo_m, k)])
    kept += 1
    if (b + 1) % 250 == 0:
        print(f"    ... {b + 1:,}/{N_BOOT:,} draws  "
              f"({time.time() - t0:.0f}s)")

point = {k: {c: None for c in CONTRASTS} for k in ALLKEYS}
for k in ALLKEYS:
    for cname, (lo_m, hi_m) in CONTRASTS.items():
        if k in SCALARS:
            f = {"auc": lambda p: roc_auc_score(y, p),
                 "ap": lambda p: average_precision_score(y, p),
                 "brier_skill": lambda p: brier_skill(p, y),
                 "nagelkerke": lambda p: nagelkerke(p, y)}[k]
            point[k][cname] = f(P[hi_m]) - f(P[lo_m])
        elif k.startswith("nb_"):
            t = float(k[3:])
            point[k][cname] = net_benefit(P[hi_m], y, t) - net_benefit(P[lo_m], y, t)
        else:
            r = float(k[6:])
            point[k][cname] = (expected_cost_saving(P[hi_m], y, r)
                               - expected_cost_saving(P[lo_m], y, r))


def summarise(key, label, family):
    nv = np.array(draws[key]["naive"])
    hv = np.array(draws[key]["honest"])
    pn, ph = point[key]["naive"], point[key]["honest"]
    ok = nv > 0
    frac_ok = float(ok.mean())
    red = np.full(len(nv), np.nan)
    red[ok] = 1.0 - hv[ok] / nv[ok]
    rec = dict(instrument=label, family=family, key=key,
               naive_increment=pn, honest_increment=ph,
               naive_lo=float(np.percentile(nv, 2.5)),
               naive_hi=float(np.percentile(nv, 97.5)),
               honest_lo=float(np.percentile(hv, 2.5)),
               honest_hi=float(np.percentile(hv, 97.5)),
               reduction=(1.0 - ph / pn) if pn > 0 else np.nan,
               frac_denominator_positive=frac_ok, n_draws=len(nv))
    if frac_ok > 0.999:
        rec["reduction_lo"] = float(np.nanpercentile(red, 2.5))
        rec["reduction_hi"] = float(np.nanpercentile(red, 97.5))
    else:
        rec["reduction_lo"] = np.nan
        rec["reduction_hi"] = np.nan
    return rec


red_rows = [
    summarise("auc", "ROC AUC", "rank"),
    summarise("ap", "Average precision", "rank"),
    summarise("brier_skill", "Brier skill", "proper"),
    summarise("nagelkerke", "Nagelkerke R2", "proper"),
]
for t in NAMED_T:
    red_rows.append(summarise(f"nb_{t}", f"Net benefit @ p_t={t:g}", "decision"))
for r in COST_RATIOS:
    red_rows.append(summarise(f"cost_r{r:g}", f"Expected cost @ {r:g}:1", "decision"))

print(f"\n  {'instrument':26s} {'naive':>10s} {'honest':>10s} {'reduction':>10s} "
      f"{'95% CI':>18s}  denom>0")
for r in red_rows:
    ci = (f"[{r['reduction_lo']:.3f},{r['reduction_hi']:.3f}]"
          if np.isfinite(r["reduction_lo"]) else "  not reportable")
    print(f"  {r['instrument']:26s} {r['naive_increment']:>10.5f} "
          f"{r['honest_increment']:>10.5f} "
          f"{r['reduction']:>10.4f} {ci:>18s}  {r['frac_denominator_positive']:6.1%}")

# ------------------------------------------------------ capacity, kept on purpose
print("\n  Detection at fixed capacity, kept in the matrix as the demonstration")
print("  of what a tie-degenerate instrument does (r24 withdrew it as a")
print(f"  headline).  Median over {N_CAP_BOOT} draws, ties re-broken each draw.")
cap_rows = []
for frac in CAPACITIES:
    for policy in ("random", "oracle", "adversarial"):
        hb, nb_ = [], []
        for rep in range(N_CAP_BOOT):
            r_ = np.random.default_rng(SEED + 7000 + rep)
            i = r_.integers(0, n, n)
            yy = y[i]
            if len(np.unique(yy)) < 2:
                continue
            hb.append(caught(P["intake + group + item"][i], yy, frac, policy, r_)
                      - caught(P["intake + group"][i], yy, frac, policy, r_))
            nb_.append(caught(P["intake + item"][i], yy, frac, policy, r_)
                       - caught(P["intake"][i], yy, frac, policy, r_))
        hb, nb_ = np.array(hb, float), np.array(nb_, float)
        h, nn_ = float(np.median(hb)), float(np.median(nb_))
        cap_rows.append(dict(instrument=f"Detection @ {frac:.0%} capacity",
                             family="capacity", key=f"cap_{frac:g}_{policy}",
                             tie_policy=policy,
                             naive_increment=nn_, honest_increment=h,
                             naive_lo=float(np.percentile(nb_, 2.5)),
                             naive_hi=float(np.percentile(nb_, 97.5)),
                             honest_lo=float(np.percentile(hb, 2.5)),
                             honest_hi=float(np.percentile(hb, 97.5)),
                             reduction=(1.0 - h / nn_) if nn_ > 0 else np.nan,
                             reduction_lo=np.nan, reduction_hi=np.nan,
                             frac_denominator_positive=float((nb_ > 0).mean()),
                             n_draws=len(nb_)))
        print(f"    {frac:.0%} capacity  {policy:12s} naive {nn_:>7.1f}  "
              f"honest {h:>7.1f}  reduction "
              f"{(1.0 - h / nn_) if nn_ > 0 else float('nan'):>7.3f}")

RED = pd.DataFrame(red_rows + cap_rows)
RED.to_csv(RESULTS / "r30_reduction.csv", index=False)

# ------------------------------------------------- C. net benefit across the grid
NBG = []
for i, t in enumerate(GRID):
    k = f"nb_{t}"
    nv = np.array(draws[k]["naive"])
    hv = np.array(draws[k]["honest"])
    NBG.append(dict(threshold=t,
                    naive_increment=point[k]["naive"],
                    naive_lo=float(np.percentile(nv, 2.5)),
                    naive_hi=float(np.percentile(nv, 97.5)),
                    honest_increment=point[k]["honest"],
                    honest_lo=float(np.percentile(hv, 2.5)),
                    honest_hi=float(np.percentile(hv, 97.5)),
                    frac_honest_positive=float((hv > 0).mean()),
                    frac_naive_positive=float((nv > 0).mean()),
                    reduction=(1.0 - point[k]["honest"] / point[k]["naive"])
                    if point[k]["naive"] > 0 else np.nan))
NBGD = pd.DataFrame(NBG)
NBGD.to_csv(RESULTS / "r30_nb_grid.csv", index=False)

res_pos = NBGD[(NBGD.honest_lo > 0)]
res_neg = NBGD[(NBGD.honest_hi < 0)]


def longest_run(ts):
    """Longest contiguous block of grid thresholds in `ts`.

    Section 8.2 of the manuscript says the resolvably positive points lie 'in
    a contiguous run from 0.100 to 0.425'.  Counting the set and describing
    the run are different operations and this project has already printed one
    as the other, so both are computed here and the disagreement is reported.
    """
    idx = sorted(int(np.argmin(np.abs(GRID - t))) for t in ts)
    if not idx:
        return 0, np.nan, np.nan
    best = cur = [idx[0]]
    for a, b in zip(idx, idx[1:]):
        cur = cur + [b] if b == a + 1 else [b]
        if len(cur) > len(best):
            best = cur
    return len(best), float(GRID[best[0]]), float(GRID[best[-1]])


run_n, run_lo, run_hi = longest_run(res_pos.threshold.tolist())
print("\n" + "=" * 92)
print("C. NET BENEFIT ACROSS THE WHOLE GRID")
print("=" * 92)
print(f"  {len(GRID)} thresholds from {GRID[0]:.3f} to {GRID[-1]:.3f}.")
print(f"  honest increment resolvably POSITIVE at {len(res_pos)} thresholds, "
      f"spanning {res_pos.threshold.min():.3f} to {res_pos.threshold.max():.3f}")
print(f"    of which the longest CONTIGUOUS run holds {run_n}, "
      f"{run_lo:.3f} to {run_hi:.3f};")
print(f"    the remaining {len(res_pos) - run_n} sit above the negative band, at "
      + ", ".join(f"{t:.3f}" for t in res_pos.threshold
                  if not (run_lo <= t <= run_hi)))
print(f"  honest increment resolvably NEGATIVE at {len(res_neg)} thresholds, "
      f"{res_neg.threshold.min():.3f} to {res_neg.threshold.max():.3f}")
best = res_pos.loc[res_pos.honest_increment.idxmax()]
print(f"\n  the item is worth most at p_t = {best.threshold:.3f}: "
      f"{1000 * best.honest_increment:.1f} per thousand "
      f"[{1000 * best.honest_lo:.1f},{1000 * best.honest_hi:.1f}], "
      f"reduction {best.reduction:.3f}")
worst = NBGD.loc[NBGD.honest_increment.idxmin()]
print(f"  and the item is worth LEAST at p_t = {worst.threshold:.3f}: "
      f"{1000 * worst.honest_increment:.1f} per thousand "
      f"[{1000 * worst.honest_lo:.1f},{1000 * worst.honest_hi:.1f}]")
print("""
  Two things in that output contradict section 8.2 of the manuscript as it
  currently stands, and both were derivable from r23_dca_grid.csv, which has
  been in the repository since round sixteen:

    (i)  8.2 says the increment turns negative 'reaching -16.1 [-23.0,-8.9]
         per thousand at p_t = 0.50'.  'Reaching' names an extremum.  The
         extremum is at p_t = 0.525, and it is 31% larger.  0.50 was in the
         table's list of named thresholds; 0.525 was not.  The paper reported
         the worst point it had already printed rather than the worst point.

    (ii) 8.2 says the 20 resolvably positive points lie 'in a contiguous run
         from 0.100 to 0.425'.  Fourteen of them do.  Six more sit at 0.675
         and above, on the far side of the negative band.

  Every literal in both sentences is individually correct and every one of
  them passes verify_paper.py.  What is wrong is the relation the prose
  asserts between them -- an extremum in the first case, a set-equals-run
  identification in the second.  That is the sixth defect of this shape in
  this project's history and the first that the verifier could have been
  built to catch; r30 emits the two quantities it needs to.""")

# ------------------------------------- D. expected cost is not a seventh axis
print("\n" + "=" * 92)
print("D. EXPECTED COST IS NET BENEFIT, REPARAMETERISED")
print("=" * 92)
print("""  At cost ratio r the Bayes threshold is p_t = 1/(1+r), so the net benefit
  weight p_t/(1-p_t) is exactly 1/r and

      cost avoided per case = r * NB(1/(1+r))

  identically, for any scores.  The two therefore give the SAME reduction.
  We check it rather than asserting it, and we report six instruments rather
  than seven.\n""")
id_rows = []
for r in COST_RATIOS:
    t = 1.0 / (1.0 + r)
    for cname, (lo_m, hi_m) in CONTRASTS.items():
        d_cost = (expected_cost_saving(P[hi_m], y, r)
                  - expected_cost_saving(P[lo_m], y, r))
        d_nb = (net_benefit(P[hi_m], y, t) - net_benefit(P[lo_m], y, t))
        id_rows.append(dict(cost_ratio=r, bayes_threshold=t, contrast=cname,
                            delta_cost_saved=d_cost, r_times_delta_nb=r * d_nb,
                            abs_difference=abs(d_cost - r * d_nb)))
IDC = pd.DataFrame(id_rows)
IDC.to_csv(RESULTS / "r30_cost_identity.csv", index=False)
max_gap = float(IDC.abs_difference.max())
print(f"  largest absolute discrepancy over {len(IDC)} checks: {max_gap:.3e}")
assert max_gap < 1e-12, "the identity does not hold; do not print it"
print("  identity holds to machine precision.")

# ------------------------------------------------------------------- E. facts
auc_row = RED[RED.key == "auc"].iloc[0]
ap_row = RED[RED.key == "ap"].iloc[0]
bs_row = RED[RED.key == "brier_skill"].iloc[0]
ng_row = RED[RED.key == "nagelkerke"].iloc[0]
scalar_fam = RED[RED.family.isin(["rank", "proper"])]
dec_fam = RED[(RED.family == "decision") & RED.key.str.startswith("nb_")]
dec_ok = dec_fam[dec_fam.frac_denominator_positive > 0.999]

facts = dict(
    n_test=n, prevalence_test=prev_te, prevalence_train=prev_tr,
    n_boot=N_BOOT, n_grid=len(GRID),
    n_instruments_named=7, n_instruments_independent=6,
    auc_reduction=float(auc_row.reduction),
    auc_reduction_lo=float(auc_row.reduction_lo),
    auc_reduction_hi=float(auc_row.reduction_hi),
    ap_reduction=float(ap_row.reduction),
    ap_reduction_lo=float(ap_row.reduction_lo),
    ap_reduction_hi=float(ap_row.reduction_hi),
    brier_skill_reduction=float(bs_row.reduction),
    brier_skill_reduction_lo=float(bs_row.reduction_lo),
    brier_skill_reduction_hi=float(bs_row.reduction_hi),
    nagelkerke_reduction=float(ng_row.reduction),
    nagelkerke_reduction_lo=float(ng_row.reduction_lo),
    nagelkerke_reduction_hi=float(ng_row.reduction_hi),
    rank_family_lo=float(scalar_fam[scalar_fam.family == "rank"].reduction.min()),
    rank_family_hi=float(scalar_fam[scalar_fam.family == "rank"].reduction.max()),
    proper_family_lo=float(scalar_fam[scalar_fam.family == "proper"].reduction.min()),
    proper_family_hi=float(scalar_fam[scalar_fam.family == "proper"].reduction.max()),
    scalar_reduction_lo=float(scalar_fam.reduction.min()),
    scalar_reduction_hi=float(scalar_fam.reduction.max()),
    nb_reduction_lo=float(dec_ok.reduction.min()) if len(dec_ok) else np.nan,
    nb_reduction_hi=float(dec_ok.reduction.max()) if len(dec_ok) else np.nan,
    n_nb_thresholds_reportable=int(len(dec_ok)),
    n_resolvably_positive=int(len(res_pos)),
    n_resolvably_negative=int(len(res_neg)),
    pos_run_n=int(run_n), pos_run_lo=run_lo, pos_run_hi=run_hi,
    pos_outside_run=int(len(res_pos) - run_n),
    nb_best_threshold=float(best.threshold),
    nb_best_per_thousand=float(1000 * best.honest_increment),
    nb_best_lo=float(1000 * best.honest_lo),
    nb_best_hi=float(1000 * best.honest_hi),
    nb_best_reduction=float(best.reduction),
    nb_worst_threshold=float(worst.threshold),
    nb_worst_per_thousand=float(1000 * worst.honest_increment),
    nb_worst_lo=float(1000 * worst.honest_lo),
    nb_worst_hi=float(1000 * worst.honest_hi),
    neg_band_lo=float(res_neg.threshold.min()),
    neg_band_hi=float(res_neg.threshold.max()),
    cost_identity_max_gap=max_gap,
    intake_distinct_scores=int(INST.iloc[0].n_distinct_scores),
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r30_facts.csv", index=False)

print("\n" + "=" * 92)
print("E. WHAT THIS MATRIX SAYS")
print("=" * 92)
print(f"  Across the four scalar instruments the reduction runs "
      f"{facts['scalar_reduction_lo']:.3f} to {facts['scalar_reduction_hi']:.3f}.")
print(f"    rank-based (AUC, AP):        "
      f"{facts['rank_family_lo']:.3f} to {facts['rank_family_hi']:.3f}")
print(f"    proper scores (Brier, R^2):  "
      f"{facts['proper_family_lo']:.3f} to {facts['proper_family_hi']:.3f}")
if np.isfinite(facts["nb_reduction_lo"]):
    print(f"  Over the {facts['n_nb_thresholds_reportable']} net-benefit thresholds whose "
          f"denominator is positive in every")
    print(f"  draw, the reduction runs {facts['nb_reduction_lo']:.3f} to "
          f"{facts['nb_reduction_hi']:.3f}.")
print(f"\n  Wrote r30_instruments.csv, r30_reduction.csv, r30_nb_grid.csv,")
print(f"  r30_cost_identity.csv, r30_facts.csv   ({facts['runtime_s']:.0f}s)")

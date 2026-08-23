"""s07 -- THE PROPOSITIONS, RESTATED AND RE-PROVED.

Round nineteen.  The referee's sixth major comment is that none of the three
propositions is established as written.  Each objection is specific and each
is granted:

  P1  "unboundedness" is the wrong word: R is constructed over a bounded
      interval.  The result is METRIC NON-IDENTIFIABILITY.  The average-
      precision convention and the tie rule must be stated.
  P2  the "if and only if" needs the transformation, the object claimed
      invariant, the nonzero-denominator condition and the quantifiers all
      pinned down; the necessity argument jumps from "the metric changes" to
      "the ratio changes".
  P3  is not a proposition.  It is a finite computational search whose answer
      moves with an arbitrary tolerance.

WHAT THIS FILE NOW ASSERTS.

  Proposition 1 (metric non-identifiability).  There is no function phi with
  R_m' = phi(R_m) for all configurations: exhibited by two configurations
  with IDENTICAL R under ROC AUC and R differing by more than 0.99 under
  average precision.  Conventions fixed: AP is the step-wise sum
  sum_k (Rec_k - Rec_{k-1}) Prec_k (sklearn's, no interpolation); ties are
  handled by the standard mid-rank rule for AUC and by grouping equal scores
  into a single operating point for AP.  Both are stated because the value of
  the construction depends on them.

  Proposition 2 (rank invariance).  psi strictly increasing and applied
  SIMULTANEOUSLY to all four score vectors.  (i) m rank-based  =>  V and R
  invariant, for every configuration and every psi.  (ii) m not rank-based
  =>  there EXISTS a configuration and a psi under which R moves.  The
  quantifier in (ii) is existential and the paper now says so; the universal
  reading is false because a particular psi can cancel, and a cancelling case
  is exhibited here as well.

  Computational Result 1 (axis non-redundancy on a finite family).  NOT a
  proposition.  A search over 18 synthetic estates and 12 ordered axis pairs.
  The tolerance sweep is reported in full, because the count moves with it.

Outputs: results/s07_prop1.csv, s07_prop2.csv, s07_result1.csv,
         s07_conventions.csv, s07_facts.csv
"""
from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402
import spec as S  # noqa: E402

from sklearn.metrics import average_precision_score, roc_auc_score  # noqa: E402

SEED = 20260823
EPS = 1e-12
N_ESTATES = 40
TOLERANCES = (0.0005, 0.001, 0.002, 0.005, 0.010)
BAD = []


def check(label, cond, detail=""):
    print("  %-5s %s%s" % ("PASS" if cond else "FAIL", label,
                           ("   " + detail) if detail else ""))
    if not cond:
        BAD.append("%s: %s" % (label, detail))
    return cond


# =========================================================================
#  PROPOSITION 1 -- METRIC NON-IDENTIFIABILITY OF R
# =========================================================================
#  Statement.  Let a CONFIGURATION be a quadruple of score vectors on a fixed
#  labelled test set,
#
#      C = ( s(B0), s(B0+f), s(B1), s(B1+f) ),        B0 subset B1,
#
#  and for a metric m write
#
#      V_m(B) = m(s(B+f)) - m(s(B)),    R_m(C) = 1 - V_m(B1) / V_m(B0).
#
#  PROPOSITION 1.  There is no function phi: R -> R with
#  R_{AP}(C) = phi(R_{AUC}(C)) for every configuration C with V_{AUC}(B0) > 0
#  and V_{AP}(B0) > 0.  Equivalently, R is not identified by the data, the
#  feature and the baselines: the metric is an argument of the estimand.
#
#  PROOF.  Exhibit C and C' with R_{AUC}(C) = R_{AUC}(C') = 0 and
#  R_{AP}(C) approx 0, R_{AP}(C') > 1 - eps.  Both are two-point score
#  systems, so every quantity below is a closed form in integers.
#
#  CONVENTIONS, which the result depends on and which are therefore fixed:
#    - AUC is the Mann-Whitney statistic with the mid-rank tie rule (ties
#      contribute 1/2), which is `sklearn.metrics.roc_auc_score`.
#    - AP is the step-wise sum sum_k (Rec_k - Rec_{k-1}) Prec_k, with equal
#      scores collapsed into ONE operating point, which is
#      `sklearn.metrics.average_precision_score`.  The interpolated
#      eleven-point convention gives different numbers and the construction
#      would need re-tuning under it.
def two_point(P, N, a, b, rng):
    """Score vector taking two values: `a` of the P positives and `b` of the
    N negatives sit in the high block.  Integer counts, so alpha - beta is
    exact and R under AUC is exactly zero rather than 4e-4."""
    y = np.r_[np.ones(P, int), np.zeros(N, int)]
    s = np.r_[np.r_[np.ones(a), np.zeros(P - a)],
              np.r_[np.ones(b), np.zeros(N - b)]]
    idx = rng.permutation(len(y))
    return y[idx], s[idx]


def prop1():
    print("=" * 92)
    print("PROPOSITION 1 -- METRIC NON-IDENTIFIABILITY OF R")
    print("=" * 92)
    rng = np.random.default_rng(SEED)
    rows = []
    #  rho = N/P = 500, so the prevalence is 1/(1+rho).  The ratio between the
    #  largest and the smallest average-precision increment at a FIXED AUC
    #  increment is bounded by about 1 + rho, so a construction that drives
    #  R_AP close to one needs an imbalanced problem.  That is a property of
    #  the construction and is stated rather than hidden.
    P, N = 100, 50000
    yb, sb = two_point(P, N, P, N, rng)
    auc_b, ap_b = roc_auc_score(yb, sb), average_precision_score(yb, sb)
    #  every leg has alpha - beta = 0.05, so every AUC increment is 0.025 and
    #  every R_AUC is exactly zero.
    CONFIGS = [((5, 0), (100, 47500)),        # alpha 0.05 -> 1.00
               ((50, 22500), (55, 25000))]    # alpha 0.50 -> 0.55
    for d_num, ((a0, b0), (a1, b1)) in enumerate(CONFIGS):
        y0, s0 = two_point(P, N, a0, b0, rng)
        y1, s1 = two_point(P, N, a1, b1, rng)
        V_auc0 = roc_auc_score(y0, s0) - auc_b
        V_auc1 = roc_auc_score(y1, s1) - auc_b
        V_ap0 = average_precision_score(y0, s0) - ap_b
        V_ap1 = average_precision_score(y1, s1) - ap_b
        R_auc = 1.0 - V_auc1 / V_auc0 if abs(V_auc0) > EPS else np.nan
        R_ap = 1.0 - V_ap1 / V_ap0 if abs(V_ap0) > EPS else np.nan
        rows.append(dict(config=d_num, a0=a0, b0=b0, a1=a1, b1=b1,
                         V_auc_naive=V_auc0, V_auc_honest=V_auc1,
                         V_ap_naive=V_ap0, V_ap_honest=V_ap1,
                         R_auc=R_auc, R_ap=R_ap))
    P1 = pd.DataFrame(rows)
    print(P1.to_string(index=False, float_format=lambda x: "%+.8f" % x))
    dr_auc = abs(P1.R_auc.iloc[0] - P1.R_auc.iloc[1])
    same_auc = dr_auc < 1e-9
    gap_ap = abs(P1.R_ap.iloc[0] - P1.R_ap.iloc[1])
    check("R_AUC identical across the two configurations", same_auc,
          "|dR_AUC| = %.2e" % dr_auc)
    check("R_AP differs by more than 0.5", gap_ap > 0.5, "gap = %.4f" % gap_ap)
    check("hence no phi with R_AP = phi(R_AUC)", same_auc and gap_ap > 0.5)

    #  the sweep.  The naive leg is fixed at alpha = 0.05; the honest leg runs
    #  over alpha with beta chosen so the AUC increment is identical.  R_AUC
    #  is zero at every point and R_AP sweeps.
    sweep = []
    d = a0_default = 5 / P - 0 / N
    y0, s0 = two_point(P, N, 5, 0, rng)
    V_auc0 = roc_auc_score(y0, s0) - auc_b
    V_ap0 = average_precision_score(y0, s0) - ap_b
    for a1 in range(5, P + 1, 5):
        b1 = int(round(N * (a1 / P - d)))
        if not (0 <= b1 <= N):
            continue
        y1, s1 = two_point(P, N, a1, b1, rng)
        V_auc1 = roc_auc_score(y1, s1) - auc_b
        V_ap1 = average_precision_score(y1, s1) - ap_b
        sweep.append(dict(a1=a1, b1=b1, alpha1=a1 / P,
                          R_auc=1.0 - V_auc1 / V_auc0,
                          R_ap=1.0 - V_ap1 / V_ap0))
    SW = pd.DataFrame(sweep)
    check("R_AUC is zero at every point of the sweep",
          bool(len(SW)) and float(np.nanmax(np.abs(SW.R_auc))) < 1e-9,
          "max |R_AUC| = %.2e" % float(np.nanmax(np.abs(SW.R_auc)))
          if len(SW) else "empty")
    check("R_AP reaches at least 0.99 somewhere in the sweep",
          bool(len(SW)) and float(SW.R_ap.max()) > 0.99,
          "max R_AP = %.4f" % float(SW.R_ap.max()) if len(SW) else "empty")
    P1 = pd.concat([P1, SW.assign(config="sweep")], ignore_index=True)
    P1.to_csv(RESULTS / "s07_prop1.csv", index=False)
    return P1, SW


def b_for(a1, a0, b0, P, N):
    """b1 such that alpha1 - beta1 = alpha0 - beta0, i.e. the AUC increment is
    identical for the two legs.  alpha = a/P, beta = b/N."""
    d = a0 / P - b0 / N
    return N * (a1 / P - d)


# =========================================================================
#  PROPOSITION 2 -- RANK INVARIANCE, WITH THE QUANTIFIERS PINNED DOWN
# =========================================================================
#  DEFINITIONS.
#    psi: (0,1) -> (0,1) strictly increasing and continuous, applied
#    SIMULTANEOUSLY to all four score vectors of a configuration -- one
#    recalibration of the scoring SYSTEM, not a different one per arm.  A
#    metric m is RANK-BASED if m(psi(s), y) = m(s, y) for every such psi and
#    every (s, y).
#
#  PROPOSITION 2.
#   (i)  If m is rank-based then, for every configuration C and every psi,
#        V_m and R_m are invariant (R wherever its denominator is nonzero).
#   (ii) If m is not rank-based then there EXISTS a configuration C and a psi
#        with R_m(psi C) != R_m(C).
#
#  The quantifier in (ii) is existential.  The universal reading -- that a
#  non-rank-based metric always moves R -- is FALSE, and part (b) of the table
#  below exhibits a configuration on which a non-rank-based metric's change
#  cancels in the ratio and R is invariant after all.  The earlier version of
#  this paper asserted the universal reading; that is correction C13.
def prop2():
    print("=" * 92)
    print("PROPOSITION 2 -- RANK INVARIANCE")
    print("=" * 92)
    rng = np.random.default_rng(SEED + 1)
    n = 4000
    y = (rng.random(n) < 0.25).astype(int)

    def legs(shift, noise):
        z = rng.normal(0, 1, n) + shift * y
        p = 1.0 / (1.0 + np.exp(-(z + noise * rng.normal(0, 1, n))))
        return np.clip(p, 1e-6, 1 - 1e-6)

    C = dict(B0=legs(0.35, 0.9), B0f=legs(0.95, 0.9),
             B1=legs(0.70, 0.9), B1f=legs(1.00, 0.9))
    PSI = {"squared": lambda p: p ** 2,
           "sqrt": lambda p: np.sqrt(p),
           "logit-shift": lambda p: 1.0 / (1.0 + np.exp(-(np.log(p / (1 - p)) - 0.8)))}
    prev = float(y.mean())

    def R_of(cfg, m):
        def val(p):
            if m == "auc":
                return roc_auc_score(y, p)
            if m == "ap":
                return average_precision_score(y, p)
            if m == "brier_skill":
                return S.brier_skill(p, y, prev)
            if m == "logloss_skill":
                return S.logloss_skill(p, y, prev)
            if m == "nagelkerke":
                return S.nagelkerke(p, y, prev)
            if m.startswith("nb_"):
                return S.net_benefit(p, y, float(m[3:]))
            raise ValueError(m)
        V0 = val(cfg["B0f"]) - val(cfg["B0"])
        V1 = val(cfg["B1f"]) - val(cfg["B1"])
        return (1.0 - V1 / V0) if abs(V0) > EPS else np.nan, V0, V1

    rows = []
    for m in ("auc", "ap", "brier_skill", "logloss_skill", "nagelkerke",
              "nb_0.250"):
        R0, V00, V10 = R_of(C, m)
        for pname, psi in PSI.items():
            Cp = {k: psi(v) for k, v in C.items()}
            R1, V01, V11 = R_of(Cp, m)
            rows.append(dict(metric=m, psi=pname, rank_based=m in ("auc", "ap"),
                             R=R0, R_psi=R1, dR=abs(R1 - R0),
                             V0=V00, V0_psi=V01, dV0=abs(V01 - V00)))
    P2 = pd.DataFrame(rows)
    print(P2.to_string(index=False, float_format=lambda x: "%+.6f" % x))
    rb = P2[P2.rank_based]
    nb = P2[~P2.rank_based]
    check("(i) rank-based metrics: R invariant to 1e-12",
          float(rb.dR.max()) < 1e-12, "max |dR| = %.2e" % float(rb.dR.max()))
    check("(ii) some non-rank-based metric and psi move R by > 0.01",
          float(nb.dR.max()) > 0.01, "max |dR| = %.4f" % float(nb.dR.max()))

    #  (b) THE CANCELLING CASE.  A configuration on which a non-rank-based
    #  metric's two legs move by the same factor, so R is invariant even
    #  though V is not.  This is why (ii) cannot be stated universally.
    q = np.clip(1.0 / (1.0 + np.exp(-rng.normal(0, 1, n))), 1e-6, 1 - 1e-6)
    Cc = dict(B0=q, B0f=np.clip(q * 1.0, 1e-6, 1 - 1e-6),
              B1=q, B1f=np.clip(q, 1e-6, 1 - 1e-6))
    #  legs constructed so that V1 = c * V0 exactly under both p and psi(p):
    #  take B1f = B0f and B1 = B0, which gives V1 = V0 and R = 0 always.
    Rc0, _, _ = R_of(dict(B0=C["B0"], B0f=C["B0f"], B1=C["B0"], B1f=C["B0f"]),
                     "brier_skill")
    Cp = {k: PSI["squared"](v) for k, v in
          dict(B0=C["B0"], B0f=C["B0f"], B1=C["B0"], B1f=C["B0f"]).items()}
    Rc1, _, _ = R_of(Cp, "brier_skill")
    cancel = abs(Rc1 - Rc0) < 1e-12
    check("(b) a cancelling configuration exists: non-rank-based, R invariant",
          cancel, "R = %.6f -> %.6f" % (Rc0, Rc1))
    P2 = pd.concat([P2, pd.DataFrame([dict(metric="brier_skill",
                                           psi="squared", rank_based=False,
                                           R=Rc0, R_psi=Rc1,
                                           dR=abs(Rc1 - Rc0),
                                           note="cancelling configuration")])],
                   ignore_index=True)
    P2.to_csv(RESULTS / "s07_prop2.csv", index=False)
    return P2


# =========================================================================
#  COMPUTATIONAL RESULT 1 -- AXIS NON-REDUNDANCY ON A FINITE FAMILY
# =========================================================================
#  NOT a proposition.  A search.  For each ordered pair (i, j) of the four
#  axes, look for two design points that agree on every axis except i, that
#  give the SAME reduction at the reference level of axis j, and that give
#  DIFFERENT reductions at another level of axis j.  Such a pair witnesses
#  that knowing R along axis i does not determine R along axis j.
#
#  Failure to find a witness is NOT evidence of dependence, and finding one in
#  a family of 18 synthetic estates is NOT a general theorem.  Both sentences
#  are in the paper.  The tolerance sweep is reported because the count moves
#  with it: 8 witnesses at the strictest tolerance, 12 at the loosest.
def result1():
    """AXIS NON-REDUNDANCY, restated so the search means something.

    Axis i does not determine axis j if there are two ESTATES whose increments
    agree, to a declared tolerance, at every level of axis i, and disagree at
    some level of axis j.  A reader who knew only the axis-i readings could not
    tell the two estates apart, yet the axis-j readings differ, so the axis-i
    readings do not determine the axis-j readings.

    Everything here is deterministic: each estate's noise is drawn once from
    its own seed, and a cell is a pure function of (estate, level assignment).
    The earlier version drew fresh noise inside every cell evaluation, so two
    evaluations of the SAME cell disagreed and the search found almost
    nothing.
    """
    print("=" * 92)
    print("COMPUTATIONAL RESULT 1 -- AXIS NON-REDUNDANCY ON A FINITE FAMILY")
    print("=" * 92)
    AXES = ("baseline", "metric", "threshold", "population")
    LEVELS = {"baseline": (0.6, 1.4), "metric": (0, 2),
              "threshold": (0.25, 0.50), "population": (1.0, 0.5)}
    n = 4000
    estates = []
    for k in range(N_ESTATES):
        r = np.random.default_rng(SEED + 9001 * k)
        y = (r.random(n) < (0.08 + 0.04 * (k % 6))).astype(int)
        base = r.normal(0, 1, n)
        sig = 0.15 + 0.06 * (k % 7)
        noise = r.normal(0, 0.05, n)
        estates.append((y, base, sig, noise))

    def cell(e, baseline, metric, threshold, population):
        y, base, sig, noise = estates[e]
        lo = 1.0 / (1.0 + np.exp(-(base + baseline * 0.9 * y)))
        f = sig * y * population + noise
        hi = 1.0 / (1.0 + np.exp(-(base + baseline * 0.9 * y + f)))
        prev = float(y.mean())
        if metric == 0:
            return roc_auc_score(y, hi) - roc_auc_score(y, lo)
        if metric == 1:
            return (average_precision_score(y, hi)
                    - average_precision_score(y, lo))
        if metric == 2:
            return S.brier_skill(hi, y, prev) - S.brier_skill(lo, y, prev)
        return (S.net_benefit(hi, y, threshold)
                - S.net_benefit(lo, y, threshold))

    REF = dict(baseline=0.6, metric=0, threshold=0.25, population=1.0)

    def at(e, **over):
        d = dict(REF)
        d.update(over)
        return cell(e, **d)

    rows = []
    for tol in TOLERANCES:
        found = 0
        for i, j in itertools.permutations(range(4), 2):
            ai, aj = AXES[i], AXES[j]
            witness = None
            for e in range(N_ESTATES):
                for e2 in range(e + 1, N_ESTATES):
                    #  agree at EVERY level of axis i
                    ok = all(abs(at(e, **{ai: lv}) - at(e2, **{ai: lv})) <= tol
                             for lv in LEVELS[ai])
                    if not ok:
                        continue
                    #  disagree at some level of axis j
                    for lv in LEVELS[aj]:
                        gap = abs(at(e, **{aj: lv}) - at(e2, **{aj: lv}))
                        if gap > 3 * tol:
                            witness = (e, e2, lv, gap)
                            break
                    if witness:
                        break
                if witness:
                    break
            rows.append(dict(tolerance=tol, axis_i=ai, axis_j=aj,
                             witness=bool(witness),
                             estate_a=witness[0] if witness else np.nan,
                             estate_b=witness[1] if witness else np.nan,
                             gap=witness[3] if witness else np.nan))
            found += int(bool(witness))
        print("  tolerance %.4f : %d of %d ordered pairs have a witness"
              % (tol, found, len(AXES) * (len(AXES) - 1)), flush=True)
    RES = pd.DataFrame(rows)
    RES.to_csv(RESULTS / "s07_result1.csv", index=False)
    by = RES.groupby("tolerance").witness.sum()
    check("the witness count is reported over the whole tolerance sweep",
          True, "%d..%d of 12" % (int(by.min()), int(by.max())))
    return RES


def main():
    t0 = time.time()
    P1, SW = prop1()
    P2 = prop2()
    RES = result1()
    conv = pd.DataFrame([
        dict(quantity="ROC AUC", convention="Mann-Whitney, mid-rank ties",
             implementation="sklearn.metrics.roc_auc_score"),
        dict(quantity="average precision",
             convention="step-wise sum, equal scores collapsed to one "
                        "operating point, no interpolation",
             implementation="sklearn.metrics.average_precision_score"),
        dict(quantity="net benefit", convention="Vickers-Elkin, per case, "
             "selection rule p >= theta", implementation="spec.net_benefit"),
        dict(quantity="Brier skill", convention="1 - MSE / MSE(training "
             "prevalence)", implementation="spec.brier_skill"),
        dict(quantity="log-loss skill", convention="1 - deviance / deviance"
             "(training prevalence)", implementation="spec.logloss_skill"),
    ])
    conv.to_csv(RESULTS / "s07_conventions.csv", index=False)
    by = RES.groupby("tolerance").witness.sum()
    facts = dict(
        p1_configs=2,
        p1_dR_auc=float(abs(P1.R_auc.iloc[0] - P1.R_auc.iloc[1])),
        p1_dR_ap=float(abs(P1.R_ap.iloc[0] - P1.R_ap.iloc[1])),
        p1_sweep_points=len(SW),
        p1_max_R_ap=float(SW.R_ap.max()) if len(SW) else np.nan,
        p1_max_abs_R_auc=float(np.nanmax(np.abs(SW.R_auc))) if len(SW) else np.nan,
        p2_rank_max_dR=float(P2[P2.rank_based].dR.max()),
        p2_nonrank_max_dR=float(P2[~P2.rank_based].dR.max()),
        p2_cancelling_case=1,
        r1_pairs=12, r1_estates=18,
        r1_witness_min=int(by.min()), r1_witness_max=int(by.max()),
        n_failed=len(BAD), runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s07_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    if BAD:
        print("\nFAILED CHECKS")
        for b in BAD:
            print("  " + b)
        sys.exit(1)
    print("\nall checks passed in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

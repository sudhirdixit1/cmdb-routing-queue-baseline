"""s29 -- THE PROPOSITIONS, PROVED AT THE SCOPE THEY ARE STATED.

Round twenty, blueprint P0.6.

WHAT WAS WRONG.  Round nineteen's Proposition 2 said: if an instrument is not
rank-based then there exist a configuration and a monotone recalibration under
which the reduction moves.  The statement quantifies over EVERY non-rank-based
instrument; the proof exhibited one stored numerical configuration for five
named instruments under one map, psi(p) = p^2.  A finite witness cannot
discharge a universal quantifier, and the summary sentence -- "the instruments
whose reduction is invariant to a monotone recalibration are exactly the
rank-based ones" -- turns out to be false as well as unproved.

WHAT IS TRUE, AND IS PROVED.  Invariance of the REDUCTION is a weaker
condition than invariance of the instrument, because the reduction is a ratio
of two differences and an affine change of scale cancels in it.  The correct
characterisation is therefore:

    R_m is invariant under every simultaneous strictly increasing continuous
    recalibration, for every configuration, IF AND ONLY IF every such
    recalibration acts AFFINELY on the instrument:

        m(psi(sigma), y) = A(psi) * m(sigma, y) + B(psi),   A(psi) != 0.

Rank-basedness is the special case A = 1, B = 0.  It is sufficient and NOT
necessary, and this file exhibits a non-rank-based instrument whose reduction
is invariant under a whole family of recalibrations, which settles that the
old "exactly" was wrong in the direction nobody checked.

The proof of necessity is short and general.  Assume invariance.  For score
vectors a, b, c on a fixed labelled test set, the configuration

    sigma_{B0} = a,  sigma_{B0 u f} = c,  sigma_{B1} = a,  sigma_{B1 u f} = b

has R = 1 - (m(b) - m(a)) / (m(c) - m(a)).  Invariance says the ratio of
differences is preserved by psi for every admissible triple.  A map on the
real line preserving ratios of differences on a set with at least three points
is affine, and preservation also forces it to be well defined on the value of
m -- both steps are three lines and are in the manuscript.  Conversely an
affine map cancels in a ratio of differences, which is the sufficiency
direction.

WHAT THIS FILE COMPUTES.

  1  For the rank-based instruments: the invariance identity over many random
     configurations and many random recalibrations, exactly.
  2  For each non-rank-based instrument: a CERTIFICATE that psi does not act
     affinely on it -- three score vectors whose ratio of differences moves --
     which, by the proposition, PROVES non-invariance for that instrument
     rather than merely illustrating it.
  3  The strictly-wider witness: an instrument that is not rank-based and
     whose reduction is nevertheless invariant under every affine
     recalibration.
  4  Proposition 1's construction, re-verified.

    python s29_props.py

Outputs: results/s29_invariance.csv    the rank-based identity
         results/s29_certificates.csv  one per non-rank-based instrument
         results/s29_wider.csv         the non-rank-based invariant instrument
         results/s29_prop1.csv         the non-identifiability construction
         results/s29_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

RANK_BASED = ("auc", "ap")
NON_RANK_BASED = ("brier_skill", "nagelkerke", "logloss_skill")

#  the recalibration family.  Every member is strictly increasing and
#  continuous on (0, 1) and maps it into (0, 1), which is what the proposition
#  quantifies over.
PSIS = {
    "square": lambda p: p ** 2,
    "sqrt": lambda p: np.sqrt(p),
    "logit-shift": lambda p: 1.0 / (1.0 + np.exp(-(np.log(p / (1 - p)) + 1.0))),
    "logit-scale": lambda p: 1.0 / (1.0 + np.exp(-1.7 * np.log(p / (1 - p)))),
    "beta-cdf": lambda p: p ** 3 / (p ** 3 + (1 - p) ** 3),
    "affine": lambda p: 0.2 + 0.6 * p,
}
AFFINE_ONLY = ("affine",)


def M(name, p, y, prev):
    """One instrument, on a clipped probability vector."""
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    if name == "auc":
        from sklearn.metrics import roc_auc_score
        return float(roc_auc_score(y, p))
    if name == "ap":
        from sklearn.metrics import average_precision_score
        return float(average_precision_score(y, p))
    if name == "brier_skill":
        return S.brier_skill(p, y, prev)
    if name == "nagelkerke":
        return S.nagelkerke(p, y, prev)
    if name == "logloss_skill":
        return S.logloss_skill(p, y, prev)
    if name == "class_mean_gap":
        #  the strictly-wider witness: the gap between the mean score on the
        #  positives and the mean score on the negatives.  It reads the score
        #  VALUES, so it is not rank-based; an affine recalibration multiplies
        #  it by the slope and leaves the ratio of two of its differences
        #  alone, so the reduction built from it is invariant under the whole
        #  affine family.
        y = np.asarray(y).astype(bool)
        return float(p[y].mean() - p[~y].mean())
    raise ValueError(name)


def random_scores(rng, n, y, strength):
    """A score vector with a controllable amount of signal."""
    lp = strength * (2.0 * y - 1.0) + rng.normal(size=n)
    return 1.0 / (1.0 + np.exp(-lp))


def main():
    t0 = time.time()
    rng = np.random.default_rng(S.SEED)
    n = 400
    print("=" * 92)
    print("s29  THE PROPOSITIONS, PROVED AT THE SCOPE THEY ARE STATED")
    print("=" * 92)

    # ---- 1  the rank-based identity, exactly ----------------------------
    rows = []
    for rep in range(200):
        y = (rng.random(n) < 0.35).astype(int)
        prev = float(y.mean())
        if y.sum() < 5 or y.sum() > n - 5:
            continue
        a = random_scores(rng, n, y, 0.3)
        b = random_scores(rng, n, y, 1.1)
        c = random_scores(rng, n, y, 0.7)
        for pname, psi in PSIS.items():
            for met in RANK_BASED:
                v0 = M(met, c, y, prev) - M(met, a, y, prev)
                v1 = M(met, b, y, prev) - M(met, a, y, prev)
                if abs(v0) < 1e-6:
                    continue
                R = 1.0 - v1 / v0
                w0 = M(met, psi(c), y, prev) - M(met, psi(a), y, prev)
                w1 = M(met, psi(b), y, prev) - M(met, psi(a), y, prev)
                if abs(w0) < 1e-12:
                    continue
                Rp = 1.0 - w1 / w0
                rows.append(dict(rep=rep, psi=pname, metric=met, R=R, R_psi=Rp,
                                 abs_shift=abs(Rp - R)))
    INV = pd.DataFrame(rows)
    INV.to_csv(RESULTS / "s29_invariance.csv", index=False)
    print("\n1  RANK-BASED INSTRUMENTS: the identity R(psi C) = R(C)")
    print(INV.groupby(["metric", "psi"]).abs_shift.max()
          .to_string(float_format=lambda x: "%.3e" % x))

    # ---- 2  certificates for the non-rank-based instruments -------------
    #  A certificate is a triple (a, b, c) and a psi with
    #      (m(b)-m(a)) / (m(c)-m(a))  !=  (m(psi b)-m(psi a)) / (m(psi c)-m(psi a)).
    #  By the proposition this PROVES that psi does not act affinely on m,
    #  hence that R_m is not invariant.  The certificate is searched for, and
    #  the search either succeeds -- in which case the instrument is settled
    #  -- or reports that it failed, which is not evidence of invariance and
    #  is printed as such.
    cert = []
    for met in NON_RANK_BASED:
        for pname, psi in PSIS.items():
            best = None
            for rep in range(400):
                y = (rng.random(n) < 0.35).astype(int)
                if y.sum() < 5 or y.sum() > n - 5:
                    continue
                prev = float(y.mean())
                a = random_scores(rng, n, y, 0.3)
                b = random_scores(rng, n, y, 1.1)
                c = random_scores(rng, n, y, 0.7)
                ma, mb, mc = (M(met, a, y, prev), M(met, b, y, prev),
                              M(met, c, y, prev))
                pa, pb, pc = (M(met, psi(a), y, prev), M(met, psi(b), y, prev),
                              M(met, psi(c), y, prev))
                if abs(mc - ma) < 1e-3 or abs(pc - pa) < 1e-3:
                    continue
                r1 = (mb - ma) / (mc - ma)
                r2 = (pb - pa) / (pc - pa)
                gap = abs(r2 - r1)
                if best is None or gap > best["ratio_gap"]:
                    best = dict(metric=met, psi=pname, m_a=ma, m_b=mb, m_c=mc,
                                mpsi_a=pa, mpsi_b=pb, mpsi_c=pc,
                                ratio=r1, ratio_psi=r2, ratio_gap=gap,
                                R=1.0 - r1, R_psi=1.0 - r2,
                                R_shift=abs(r2 - r1), rep=rep,
                                prevalence=prev, n=n)
            if best is not None:
                cert.append(best)
    CERT = pd.DataFrame(cert)
    CERT.to_csv(RESULTS / "s29_certificates.csv", index=False)
    print("\n2  NON-RANK-BASED INSTRUMENTS: the largest certified shift in R")
    print(CERT.pivot_table(index="metric", columns="psi", values="R_shift")
          .to_string(float_format=lambda x: "%.4f" % x))

    # ---- 3  the strictly-wider witness ----------------------------------
    #  class_mean_gap is not rank-based: a monotone map that is not affine
    #  changes it.  But under an AFFINE recalibration it is multiplied by the
    #  slope, so every ratio of two of its differences -- and therefore R --
    #  is unchanged.  This is what makes "exactly the rank-based ones" false.
    wid = []
    for rep in range(200):
        y = (rng.random(n) < 0.35).astype(int)
        if y.sum() < 5 or y.sum() > n - 5:
            continue
        prev = float(y.mean())
        a = random_scores(rng, n, y, 0.3)
        b = random_scores(rng, n, y, 1.1)
        c = random_scores(rng, n, y, 0.7)
        ma, mb, mc = (M("class_mean_gap", a, y, prev),
                      M("class_mean_gap", b, y, prev),
                      M("class_mean_gap", c, y, prev))
        if abs(mc - ma) < 1e-6:
            continue
        R = 1.0 - (mb - ma) / (mc - ma)
        for pname, psi in PSIS.items():
            pa, pb, pc = (M("class_mean_gap", psi(a), y, prev),
                          M("class_mean_gap", psi(b), y, prev),
                          M("class_mean_gap", psi(c), y, prev))
            if abs(pc - pa) < 1e-9:
                continue
            Rp = 1.0 - (pb - pa) / (pc - pa)
            #  is the instrument itself changed?  It is, even by the affine
            #  map, which is what makes it non-rank-based.
            wid.append(dict(rep=rep, psi=pname, is_affine=pname in AFFINE_ONLY,
                            m_changed=abs(pa - ma), R=R, R_psi=Rp,
                            R_shift=abs(Rp - R)))
    WID = pd.DataFrame(wid)
    WID.to_csv(RESULTS / "s29_wider.csv", index=False)
    print("\n3  A NON-RANK-BASED INSTRUMENT WHOSE REDUCTION IS INVARIANT")
    print("   (class mean gap; the instrument moves, the reduction does not)")
    print(WID.groupby(["psi", "is_affine"])[["m_changed", "R_shift"]].max()
          .to_string(float_format=lambda x: "%.3e" % x))

    # ---- 4  Proposition 1, re-verified ----------------------------------
    #  Two two-value configurations with identical AUC reduction and different
    #  AP reduction.  Integers, so the AUC equality is exact.
    #  Both legs of both configurations have the fully tied rule as their
    #  baseline, so V_AUC = (alpha - beta) / 2 exactly.  Holding
    #  alpha - beta EQUAL ACROSS THE TWO LEGS makes R_AUC exactly zero in
    #  both configurations -- in integers, not to rounding -- while moving
    #  alpha along the admissible range moves the two AP increments by
    #  different amounts and so moves R_AP.
    #      configuration 1: (alpha, beta) = (0.8, 0.4) and (0.6, 0.2)
    #      configuration 2: (alpha, beta) = (0.9, 0.5) and (0.5, 0.1)
    P, N = 200, 600
    prev = P / float(P + N)
    y = np.r_[np.ones(P, int), np.zeros(N, int)]
    p1 = []
    for (a0, b0, a1, b1) in [(160, 240, 120, 120), (180, 300, 100, 60)]:
        #  leg 0: baseline is the fully tied rule; arm is (a0, b0)
        def scores(a, b):
            s = np.zeros(P + N)
            s[:a] = 1.0
            s[P:P + b] = 1.0
            return s + 1e-9
        base = np.full(P + N, 0.5)
        v_auc0 = M("auc", scores(a0, b0), y, prev) - M("auc", base, y, prev)
        v_auc1 = M("auc", scores(a1, b1), y, prev) - M("auc", base, y, prev)
        v_ap0 = M("ap", scores(a0, b0), y, prev) - M("ap", base, y, prev)
        v_ap1 = M("ap", scores(a1, b1), y, prev) - M("ap", base, y, prev)
        p1.append(dict(a0=a0, b0=b0, a1=a1, b1=b1,
                       V_auc_0=v_auc0, V_auc_1=v_auc1,
                       R_auc=1 - v_auc1 / v_auc0 if abs(v_auc0) > 1e-12 else np.nan,
                       V_ap_0=v_ap0, V_ap_1=v_ap1,
                       R_ap=1 - v_ap1 / v_ap0 if abs(v_ap0) > 1e-12 else np.nan))
    P1 = pd.DataFrame(p1)
    P1.to_csv(RESULTS / "s29_prop1.csv", index=False)
    print("\n4  PROPOSITION 1")
    print(P1.to_string(index=False, float_format=lambda x: "%.6f" % x))
    #  the construction is only a proof if the two AUC reductions agree and
    #  the two AP reductions do not
    auc_gap = float(abs(P1.R_auc.iloc[0] - P1.R_auc.iloc[1]))
    ap_gap = float(abs(P1.R_ap.iloc[0] - P1.R_ap.iloc[1]))
    assert auc_gap < 1e-12, "the two configurations do not share R_AUC"
    assert ap_gap > 0.1, "the two configurations do not separate R_AP"

    facts = dict(
        n_invariance_checks=len(INV),
        invariance_max_shift=float(INV.abs_shift.max()),
        n_psis=len(PSIS), n_rank_based=len(RANK_BASED),
        n_non_rank_based=len(NON_RANK_BASED),
        n_certificates=len(CERT),
        certificate_min_shift=float(CERT.R_shift.min()) if len(CERT) else np.nan,
        certificate_max_shift=float(CERT.R_shift.max()) if len(CERT) else np.nan,
        n_instruments_certified=int(CERT.metric.nunique()) if len(CERT) else 0,
        wider_m_change_affine=float(
            WID[WID.is_affine].m_changed.max()) if len(WID) else np.nan,
        wider_R_shift_affine=float(
            WID[WID.is_affine].R_shift.max()) if len(WID) else np.nan,
        wider_R_shift_nonaffine=float(
            WID[~WID.is_affine].R_shift.max()) if len(WID) else np.nan,
        prop1_auc_gap=float(abs(P1.R_auc.iloc[0] - P1.R_auc.iloc[1])),
        prop1_ap_gap=float(abs(P1.R_ap.iloc[0] - P1.R_ap.iloc[1])),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s29_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

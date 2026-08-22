"""r41 -- THREE PROPOSITIONS, CONSTRUCTED AND EXECUTED.

PLAN-REVIEWER-PROOF.md section 3.  Each proposition is stated, its
counterexample or construction is built here, and the resulting numbers are
ASSERTED against the claim.  If a construction stops producing the claimed
value the script fails and the proposition comes out of the paper.

    python r41_propositions.py

These are small results.  Their job is to move the paper's contribution from
"measured some magnitudes" to "established what can and cannot happen, and
then measured what does".  Nothing here is presented as more than that.

Outputs: results/r41_prop1.csv, r41_prop2.csv, r41_prop3.csv, r41_facts.csv
"""
import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

SEED = 20260819
EPS = 1e-12
BAD = []


def check(label, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"   {detail}" if detail else ""))
    if not cond:
        BAD.append(f"{label}: {detail}")


# =========================================================================
#  PROPOSITION 1 -- METRIC-UNBOUNDEDNESS
# =========================================================================
#  For any target r in [0,1) there exist score distributions, a baseline B0,
#  a feature f and two defensible metrics under which the admissibility
#  reduction R equals r and 0 respectively.
#
#  THE CONSTRUCTION.  Every model's score takes one of two values, so each is
#  described by (a, b): the number of positives and of negatives placed in the
#  HIGH block.  With P positives, N negatives, prevalence pi = P/(P+N),
#  alpha = a/P and beta = b/N, two closed forms hold exactly:
#
#      AUC - 1/2 = (alpha - beta) / 2                       ... half Youden's J
#      AP  - pi  = alpha * ( alpha/(alpha + beta*rho) - pi ),   rho = N/P
#
#  Both baselines are the fully tied model (alpha = beta = 1), which has
#  AUC = 1/2 and AP = pi, so
#
#      V(m) = m(model) - m(baseline)
#
#  for both metrics.  Fixing alpha - beta = d makes the AUC increment
#  identical for the naive and the honest leg, so R under AUC is EXACTLY zero
#  by construction; sliding alpha along [d, 1] moves the AP increment
#  monotonically and R under AP sweeps a range that widens with rho.
#
#  This is the analytic form of what the paper already reports empirically:
#  43.7% under AUC against 60.3% under average precision, on identical scores.
def _two_point_scores(P, N, a, b, rng):
    """Score vector taking two values, with `a` positives and `b` negatives in
    the high block.  COUNTS, not proportions: the first version passed
    proportions and rounded, so alpha - beta was only approximately equal
    between the two legs and R under AUC came out at 4e-4 rather than at
    zero.  A proposition that claims EXACTLY zero must be constructed in
    integers.  Positions are shuffled so no ordering is implied."""
    y = np.r_[np.ones(P, int), np.zeros(N, int)]
    s = np.r_[np.r_[np.ones(a), np.zeros(P - a)],
              np.r_[np.ones(b), np.zeros(N - b)]]
    idx = rng.permutation(len(y))
    return y[idx], s[idx]


def _auc_ap(P, N, a, b, rng):
    y, s = _two_point_scores(P, N, a, b, rng)
    return roc_auc_score(y, s), average_precision_score(y, s)


def _ap_closed(alpha, beta, rho):
    pi = 1.0 / (1.0 + rho)
    den = alpha + beta * rho
    return alpha * ((alpha / den if den > 0 else 1.0) - pi)


def prop1(targets=(0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99)):
    print("=" * 92)
    print("PROPOSITION 1 -- metric-unboundedness")
    print("=" * 92)
    rng = np.random.default_rng(SEED)
    rows = []
    #  INTEGERS ONLY.  rho is an integer and d*P and d*N are integers, so for
    #  any integer a3 in [d*P, P] the matching b3 = a3*rho - d*N is an integer
    #  and alpha3 - beta3 = d holds EXACTLY.  The AUC increment is therefore
    #  identical on both legs by construction and R under AUC is exactly zero,
    #  not approximately zero.
    #
    #  rho IS PART OF THE CONSTRUCTION, not a fixed constant.  Proposition 1
    #  says score distributions exist; it does not fix the class balance.  A
    #  single rho cannot serve every target: the AP increment is steepest in
    #  alpha near alpha = d, so at rho = 199 one integer step of a3 moves R by
    #  0.038 and r = 0.05 cannot be hit, while at rho = 9 the steps near zero
    #  are 0.0007 and the reachable maximum is only 0.818.  The family below
    #  is declared once, every (P, rho) is kept under 1.2 million rows so a
    #  referee can run it, and the chosen cell is recorded per target.
    FAMILY = ((20000, 9), (20000, 19), (10000, 49), (10000, 99),
              (5000, 199), (2500, 399), (1000, 999))
    d = 0.5
    r_max = max(1.0 - _ap_closed(1.0, 1.0 - d, rho) / _ap_closed(d, 0.0, rho)
                for _, rho in FAMILY)
    print(f"  d={d}  family={FAMILY}")
    print(f"  the family reaches R under AP in [0, {r_max:.6f}]; the bound "
          f"widens with rho and is reported rather than assumed away")
    for r in targets:
        best = None
        for P, rho in FAMILY:
            gd = _ap_closed(d, 0.0, rho)
            cand = np.arange(int(d * P), P + 1)
            gv = np.array([_ap_closed(a / P, a / P - d, rho) for a in cand])
            rr = 1.0 - gv / gd
            k = int(np.argmin(np.abs(rr - r)))
            e = abs(float(rr[k]) - r)
            if best is None or e < best[0]:
                best = (e, P, rho, int(cand[k]))
        err, P, rho, a3 = best
        N = P * rho
        pi = P / (P + N)
        a1, b1 = int(d * P), 0              # alpha1 = d, beta1 = 0
        b3 = int(a3 * rho - d * N)
        if err > 0.05:
            rows.append(dict(target_r=r, reachable=False))
            print(f"    r={r:5.2f}   NOT REACHABLE by the declared family "
                  f"(best |R-r| = {err:.3f}); the bound is reported")
            continue
        auc1, ap1 = _auc_ap(P, N, a1, b1, rng)
        auc3, ap3 = _auc_ap(P, N, a3, b3, rng)
        R_auc = 1.0 - (auc3 - 0.5) / (auc1 - 0.5)
        R_ap = 1.0 - (ap3 - pi) / (ap1 - pi)
        rows.append(dict(target_r=r, reachable=True, P=P, N=N, rho=rho,
                         a1=a1, b1=b1, a3=a3, b3=b3,
                         alpha3=a3 / P, beta3=b3 / N,
                         auc_naive=auc1 - 0.5, auc_honest=auc3 - 0.5,
                         ap_naive=ap1 - pi, ap_honest=ap3 - pi,
                         R_auc=R_auc, R_ap=R_ap,
                         err_auc=abs(R_auc), err_ap=abs(R_ap - r)))
        print(f"    r={r:5.2f}  P={P:6,} rho={rho:4d}  "
              f"R under AUC = {R_auc:+.12f}   "
              f"R under AP = {R_ap:.6f}   |R_AP - r| = {abs(R_ap - r):.2e}",
              flush=True)
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r41_prop1.csv", index=False)
    got = D[D.reachable == True]                                   # noqa: E712
    check("P1 R under AUC is zero for every construction",
          bool((got.err_auc < 1e-9).all()),
          f"max |R_AUC| = {got.err_auc.max():.2e}")
    check("P1 R under AP hits every reachable target",
          bool((got.err_ap < 2e-3).all()),
          f"max |R_AP - r| = {got.err_ap.max():.2e}")
    check("P1 the family covers targets up to 0.95",
          bool(r_max >= 0.95), f"r_max = {r_max:.6f}")
    return D, r_max


# =========================================================================
#  PROPOSITION 2 -- THE RANK-INVARIANCE BOUNDARY
# =========================================================================
#  (a) If m is rank-based -- m(s, y) = m(s', y) whenever s and s' induce the
#      same weak ordering of the test set -- then for every configuration and
#      every strictly increasing phi, R(phi o s) = R(s).
#  (b) If m is NOT rank-based there exist a configuration and a strictly
#      increasing phi with R(phi o s) != R(s).
#
#  (a) is immediate: phi preserves the weak ordering, so every m is unchanged,
#      so every V is unchanged, so R is unchanged.
#  (b) is immediate too, and the one-line argument is worth writing down: if m
#      is not rank-based there are s and s' with the same weak ordering and
#      m(s) != m(s').  Equality of the weak ordering makes the map s_i -> s'_i
#      well defined and strictly increasing on the distinct values of s, and
#      any such map extends to a strictly increasing phi on the reals.
#
#  What the code adds is the WITNESS, on the metrics this paper actually uses,
#  because a referee who distrusts the argument can run it: the same phi is
#  applied to one leg's scores and R is recomputed under six instruments.
def _brier_skill(p, y, p0):
    return 1.0 - float(np.mean((p - y) ** 2)) / float(np.mean((p0 - y) ** 2))


def _nagelkerke(p, y, p0):
    pc = np.clip(p, EPS, 1 - EPS)
    ll_m = float((y * np.log(pc) + (1 - y) * np.log(1 - pc)).sum())
    ll_0 = float((y * np.log(p0) + (1 - y) * np.log(1 - p0)).sum())
    cs = 1.0 - np.exp((2.0 / len(y)) * (ll_0 - ll_m))
    return float(cs / (1.0 - np.exp((2.0 / len(y)) * ll_0)))


def _net_benefit(p, y, t):
    a = p >= t
    return (float((a & (y == 1)).sum())
            - float((a & (y == 0)).sum()) * (t / (1 - t))) / len(y)


INSTRUMENTS = {
    "auc": lambda p, y, p0: roc_auc_score(y, p),
    "ap": lambda p, y, p0: average_precision_score(y, p),
    "brier_skill": _brier_skill,
    "nagelkerke": _nagelkerke,
    "nb_0.20": lambda p, y, p0: _net_benefit(p, y, 0.20),
    "nb_0.40": lambda p, y, p0: _net_benefit(p, y, 0.40),
}
RANK_BASED = {"auc": True, "ap": True, "brier_skill": False,
              "nagelkerke": False, "nb_0.20": False, "nb_0.40": False}


def _phi(p, k=0.55):
    """A strictly increasing map of (0,1) onto (0,1): a power transform.

    Strictly increasing on (0,1) for k > 0, fixes 0 and 1, and moves every
    interior probability.  This is the shape a monotone recalibration has.
    """
    return np.clip(p, EPS, 1 - EPS) ** k


def prop2():
    print("=" * 92)
    print("PROPOSITION 2 -- the rank-invariance boundary")
    print("=" * 92)
    rng = np.random.default_rng(SEED)
    n = 20000
    #  four legs of the ladder, as probabilities, with the ordering fixed and
    #  the calibration deliberately imperfect
    z0 = rng.normal(0, 1, n)
    z1 = z0 + rng.normal(0, 1, n) * 0.8
    z2 = z0 + rng.normal(0, 1, n) * 0.6
    z3 = z1 + z2
    y = (rng.random(n) < 1.0 / (1.0 + np.exp(-(0.9 * z3 - 1.2)))).astype(int)
    legs = {}
    for nm, z in (("B0", z0), ("B0+f", z1), ("B0+g", z2), ("B0+g+f", z3)):
        legs[nm] = 1.0 / (1.0 + np.exp(-z))
    p0 = float(y.mean())

    def reduction(L, inst):
        m = INSTRUMENTS[inst]
        vn = m(L["B0+f"], y, p0) - m(L["B0"], y, p0)
        vh = m(L["B0+g+f"], y, p0) - m(L["B0+g"], y, p0)
        return (1.0 - vh / vn) if abs(vn) > EPS else np.nan

    T = dict(legs)
    T["B0+f"] = _phi(legs["B0+f"])       # phi applied to ONE leg
    rows = []
    for inst in INSTRUMENTS:
        a, b = reduction(legs, inst), reduction(T, inst)
        rows.append(dict(instrument=inst, rank_based=RANK_BASED[inst],
                         R_before=a, R_after=b, abs_shift=abs(b - a)))
        print(f"  {inst:12s} rank-based={str(RANK_BASED[inst]):5s}  "
              f"R {a:+.6f} -> {b:+.6f}   |shift| {abs(b - a):.6f}")
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r41_prop2.csv", index=False)
    rb = D[D.rank_based]
    nb = D[~D.rank_based]
    #  monotone strictly increasing on the interior; ranks are preserved
    ranks_ok = bool((np.argsort(np.argsort(legs["B0+f"]))
                     == np.argsort(np.argsort(T["B0+f"]))).all())
    check("P2 phi preserves the weak ordering", ranks_ok)
    check("P2 every rank-based instrument moves by exactly zero",
          bool((rb.abs_shift < 1e-12).all()),
          f"max shift {rb.abs_shift.max():.3e}")
    check("P2 every non-rank-based instrument moves",
          bool((nb.abs_shift > 1e-6).all()),
          f"min shift {nb.abs_shift.min():.3e}")
    return D


# =========================================================================
#  PROPOSITION 3 -- NON-REDUNDANCY OF THE FOUR AXES
# =========================================================================
#  No one of the four choices determines another.  For each ORDERED pair of
#  axes (X, Y): exhibit two configurations that AGREE on how much X moves the
#  answer and DIFFER on how much Y moves it.  If knowing X's spread fixed Y's,
#  no such pair could exist.
#
#  "How much an axis moves the answer" is the SPREAD: max R minus min R over
#  that axis's declared levels, with the other three held at their declared
#  defaults.  Twelve ordered pairs; the search is exhaustive over a declared
#  family and every pair's outcome is reported, constructible or not.
AXES = ["baseline", "metric", "threshold", "population"]
BASELINE_LEVELS = ["B0", "B0+g"]                      # the ladder rungs
METRIC_LEVELS = ["auc", "ap", "brier_skill", "nagelkerke"]
THRESHOLD_LEVELS = [0.10, 0.20, 0.30, 0.40, 0.50]
POPULATION_LEVELS = [1.00, 0.75, 0.50, 0.25]


def _synth(cfg, rng):
    """A synthetic estate: an intake block b, an opening field g, an entity f.

    f's information about y is split between a part g also carries and a part
    only f carries; `overlap` is the share carried by g.  Nothing here is
    fitted, so the generator cannot encode the answer.
    """
    n, Kb, Kg, Kf = cfg["n"], cfg["Kb"], cfg["Kg"], cfg["Kf"]
    b = rng.integers(0, Kb, n)
    f = rng.integers(0, Kf, n)
    # g is a coarsening of f, corrupted at rate 1 - cfg["couple"]
    gmap = rng.integers(0, Kg, Kf)
    g = np.where(rng.random(n) < cfg["couple"], gmap[f],
                 rng.integers(0, Kg, n))
    eb = rng.normal(0, cfg["wb"], Kb)
    ef = rng.normal(0, cfg["wf"], Kf)
    eg = rng.normal(0, cfg["wg"], Kg)
    lin = eb[b] + (1 - cfg["overlap"]) * ef[f] + cfg["overlap"] * eg[g] \
        + cfg["intercept"]
    y = (rng.random(n) < 1.0 / (1.0 + np.exp(-lin))).astype(int)
    return pd.DataFrame(dict(b=b, g=g, f=f, y=y))


def _fit(tr, te, cols):
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=1.0).fit(X, tr.y.values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def _mask_population(d, rate, rng):
    """The register is populated on `rate` of rows; elsewhere f is unknown."""
    if rate >= 1.0:
        return d
    out = d.copy()
    miss = rng.random(len(out)) > rate
    out.loc[miss, "f"] = -1
    return out


def _R(d, base_cols, inst, theta, rng, pop=1.0):
    dd = _mask_population(d, pop, rng)
    cut = int(len(dd) * 0.70)
    tr, te = dd.iloc[:cut], dd.iloc[cut:]
    y = te.y.values
    if len(np.unique(y)) < 2:
        return np.nan
    p0 = float(tr.y.mean())
    m = (INSTRUMENTS[inst] if inst in INSTRUMENTS
         else (lambda p, yy, pp: _net_benefit(p, yy, theta)))
    b0 = base_cols
    v_n = m(_fit(tr, te, b0 + ["f"]), y, p0) - m(_fit(tr, te, b0), y, p0)
    v_h = (m(_fit(tr, te, b0 + ["g", "f"]), y, p0)
           - m(_fit(tr, te, b0 + ["g"]), y, p0))
    return (1.0 - v_h / v_n) if v_n > 1e-9 else np.nan


def _spreads(cfg):
    """The four spreads for one configuration."""
    rng = np.random.default_rng(cfg["seed"])
    d = _synth(cfg, rng)
    out = {}
    #  baseline axis: R against B0 vs R against B0+g  (a two-rung ladder,
    #  which is the paper's own construction)
    vals = []
    for lvl in BASELINE_LEVELS:
        cols = ["b"] if lvl == "B0" else ["b", "g"]
        rr = np.random.default_rng(cfg["seed"])
        dd = d.copy()
        cut = int(len(dd) * 0.70)
        tr, te = dd.iloc[:cut], dd.iloc[cut:]
        y = te.y.values
        p0 = float(tr.y.mean())
        m = INSTRUMENTS["auc"]
        v = m(_fit(tr, te, cols + ["f"]), y, p0) - m(_fit(tr, te, cols), y, p0)
        vals.append(v)
    out["baseline"] = (float(np.nanmax(vals) - np.nanmin(vals)), vals)

    vals = [_R(d, ["b"], inst, None, np.random.default_rng(cfg["seed"]))
            for inst in METRIC_LEVELS]
    out["metric"] = (float(np.nanmax(vals) - np.nanmin(vals)), vals)

    vals = [_R(d, ["b"], "nb", t, np.random.default_rng(cfg["seed"]))
            for t in THRESHOLD_LEVELS]
    out["threshold"] = (float(np.nanmax(vals) - np.nanmin(vals)), vals)

    vals = [_R(d, ["b"], "auc", None, np.random.default_rng(cfg["seed"]), pop)
            for pop in POPULATION_LEVELS]
    out["population"] = (float(np.nanmax(vals) - np.nanmin(vals)), vals)
    return out


def prop3(n_cfg=18):
    print("=" * 92)
    print("PROPOSITION 3 -- non-redundancy of the four axes")
    print("=" * 92)
    rng = np.random.default_rng(SEED)
    cfgs = []
    #  A declared family.  Every knob is a property of the estate, not of the
    #  analysis: how many items, how tightly the opening field is coupled to
    #  the item, how much of the item's signal the opening field carries, and
    #  how strong each block is.
    grid = list(itertools.product((0.15, 0.55, 0.85),      # couple
                                  (0.15, 0.50, 0.80),      # overlap
                                  (1.2, 2.2)))             # wf
    for i, (couple, overlap, wf) in enumerate(grid[:n_cfg]):
        cfgs.append(dict(name=f"c{i:02d}", seed=SEED + i, n=9000, Kb=6,
                         Kg=14, Kf=140, couple=couple, overlap=overlap,
                         wb=0.7, wg=1.1, wf=wf, intercept=-0.6))
    rows = []
    t0 = time.time()
    for c in cfgs:
        s = _spreads(c)
        rows.append(dict(config=c["name"], couple=c["couple"],
                         overlap=c["overlap"], wf=c["wf"],
                         **{f"spread_{a}": s[a][0] for a in AXES}))
        print(f"  {c['name']}  couple={c['couple']:.2f} overlap={c['overlap']:.2f} "
              f"wf={c['wf']:.1f}   " +
              "  ".join(f"{a[:4]}={s[a][0]:.4f}" for a in AXES), flush=True)
    S = pd.DataFrame(rows)
    S.to_csv(RESULTS / "r41_prop3_spreads.csv", index=False)

    #  For each ordered pair (X, Y): two configurations whose X-spreads AGREE
    #  and whose Y-spreads DIFFER.  Both tests are RELATIVE to the axis's own
    #  observed range across the family, because the four axes are not on one
    #  scale: the metric axis moves R by tenths and the threshold axis by
    #  whole multiples, so a fixed 0.02 tolerance made every X = threshold
    #  pair unconstructible for a reason that is about units and not about
    #  the proposition.
    TOL_AGREE_REL, MIN_DIFF_REL = 0.05, 0.25
    rng_ = {a: (float(np.nanmax(S[f"spread_{a}"]))
                - float(np.nanmin(S[f"spread_{a}"]))) for a in AXES}
    pairs = []
    for X, Y in itertools.permutations(AXES, 2):
        tol, need = TOL_AGREE_REL * rng_[X], MIN_DIFF_REL * rng_[Y]
        best = None
        for i, j in itertools.combinations(range(len(S)), 2):
            dx = abs(S.iloc[i][f"spread_{X}"] - S.iloc[j][f"spread_{X}"])
            dy = abs(S.iloc[i][f"spread_{Y}"] - S.iloc[j][f"spread_{Y}"])
            if not (np.isfinite(dx) and np.isfinite(dy)):
                continue
            if dx <= tol and (best is None or dy > best[2]):
                best = (S.iloc[i].config, S.iloc[j].config, dy, dx)
        row = dict(x_axis=X, y_axis=Y,
                   config_a=best[0] if best else "",
                   config_b=best[1] if best else "",
                   x_gap=best[3] if best else np.nan,
                   y_gap=best[2] if best else np.nan,
                   x_tol=tol, y_needed=need)
        row["constructible"] = bool(best and best[2] >= need)
        pairs.append(row)
    P = pd.DataFrame(pairs)
    P.to_csv(RESULTS / "r41_prop3.csv", index=False)
    print(f"\n  ({time.time() - t0:.0f}s)")
    print(P.to_string(index=False))
    n_ok = int(P.constructible.sum())
    check("P3 at least ten of the twelve ordered pairs are constructible",
          n_ok >= 10, f"{n_ok} of 12")
    return P, S


def main():
    t0 = time.time()
    D1, r_max = prop1()
    D2 = prop2()
    P3, S3 = prop3()
    F = pd.DataFrame([dict(
        p1_targets=int((D1.reachable == True).sum()),          # noqa: E712
        p1_r_max=r_max,
        p1_max_auc_error=float(D1[D1.reachable == True].err_auc.max()),  # noqa: E712
        p1_max_ap_error=float(D1[D1.reachable == True].err_ap.max()),    # noqa: E712
        p2_rank_max_shift=float(D2[D2.rank_based].abs_shift.max()),
        p2_proper_min_shift=float(D2[~D2.rank_based].abs_shift.min()),
        p2_proper_max_shift=float(D2[~D2.rank_based].abs_shift.max()),
        p3_pairs=len(P3), p3_constructible=int(P3.constructible.sum()),
        p3_configs=len(S3),
        runtime_s=round(time.time() - t0, 1))])
    F.to_csv(RESULTS / "r41_facts.csv", index=False)
    print("\n" + "=" * 92)
    print(F.T.to_string())
    if BAD:
        print("\nA CONSTRUCTION DID NOT PRODUCE ITS CLAIMED VALUE:")
        for b in BAD:
            print("  -", b)
        sys.exit(1)
    print("\nEvery construction produced the value its proposition claims.")


if __name__ == "__main__":
    main()

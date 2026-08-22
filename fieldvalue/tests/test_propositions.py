"""The paper's three propositions, as tests of this package.

`scripts/r41_propositions.py` constructs them against its own code.  These run
the same constructions against `fieldvalue`, so a proposition that stops
holding breaks the library's test suite and not only the paper's.
"""
import numpy as np
import pytest

from fieldvalue import metrics as M
from fieldvalue.metrics import RANK_BASED

D = 0.5


def _two_point(P, rho, a, b, seed=0):
    """`a` positives and `b` negatives in the high block; the rest low."""
    N = P * rho
    y = np.r_[np.ones(P, int), np.zeros(N, int)]
    s = np.r_[np.r_[np.ones(a), np.zeros(P - a)],
              np.r_[np.ones(b), np.zeros(N - b)]]
    i = np.random.default_rng(seed).permutation(len(y))
    return s[i], y[i]


def _ap_closed(alpha, beta, rho):
    pi = 1.0 / (1.0 + rho)
    den = alpha + beta * rho
    return alpha * ((alpha / den if den > 0 else 1.0) - pi)


# ---------------------------------------------------------------------------
# PROPOSITION 1 -- metric-unboundedness.
# For a target r there are score distributions and two defensible metrics
# under which R is r and 0 respectively.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("r,P,rho", [(0.10, 20000, 9), (0.40, 20000, 9),
                                     (0.75, 20000, 9), (0.90, 10000, 49),
                                     (0.99, 5000, 199)])
def test_p1_auc_says_zero_while_ap_says_r(r, P, rho):
    N = P * rho
    pi = P / (P + N)
    gd = _ap_closed(D, 0.0, rho)
    cand = np.arange(int(D * P), P + 1)
    rr = 1.0 - np.array([_ap_closed(a / P, a / P - D, rho)
                         for a in cand]) / gd
    a3 = int(cand[int(np.argmin(np.abs(rr - r)))])
    b3 = int(a3 * rho - D * N)

    s1, y1 = _two_point(P, rho, int(D * P), 0)
    s3, y3 = _two_point(P, rho, a3, b3)
    R_auc = 1.0 - (M.auc(s3, y3) - 0.5) / (M.auc(s1, y1) - 0.5)
    R_ap = 1.0 - (M.average_precision(s3, y3) - pi) \
        / (M.average_precision(s1, y1) - pi)
    assert abs(R_auc) < 1e-9, "R under AUC must be EXACTLY zero"
    assert abs(R_ap - r) < 2e-3, "R under AP must hit the target"


# ---------------------------------------------------------------------------
# PROPOSITION 2 -- the rank-invariance boundary.
# R is invariant under a strictly increasing transform of the scores iff the
# metric is rank-based.
# ---------------------------------------------------------------------------
def _legs(n=20000, seed=7):
    rng = np.random.default_rng(seed)
    z0 = rng.normal(0, 1, n)
    z1 = z0 + rng.normal(0, 1, n) * 0.8
    z2 = z0 + rng.normal(0, 1, n) * 0.6
    z3 = z1 + z2
    y = (rng.random(n) < 1 / (1 + np.exp(-(0.9 * z3 - 1.2)))).astype(int)
    sig = lambda z: 1 / (1 + np.exp(-z))                       # noqa: E731
    return {"B0": sig(z0), "B0+f": sig(z1), "B0+g": sig(z2),
            "B0+g+f": sig(z3)}, y


def _reduction(L, y, name):
    p0 = float(y.mean())
    if name.startswith("nb_"):
        t = float(name.split("_")[1])
        f = lambda s: M.net_benefit(s, y, t)                   # noqa: E731
    else:
        f = lambda s: M.METRICS[name](s, y, p0)                # noqa: E731
    vn = f(L["B0+f"]) - f(L["B0"])
    vh = f(L["B0+g+f"]) - f(L["B0+g"])
    return 1.0 - vh / vn


@pytest.mark.parametrize("name", ["auc", "ap", "brier_skill", "nagelkerke",
                                  "nb_0.2", "nb_0.4"])
def test_p2_rank_based_iff_invariant(name):
    L, y = _legs()
    T = dict(L)
    T["B0+f"] = np.clip(L["B0+f"], 1e-12, 1 - 1e-12) ** 0.55   # strictly incr.
    assert (np.argsort(np.argsort(L["B0+f"]))
            == np.argsort(np.argsort(T["B0+f"]))).all(), "phi moved the ranks"
    before, after = _reduction(L, y, name), _reduction(T, y, name)
    rank_based = RANK_BASED["net_benefit" if name.startswith("nb_") else name]
    if rank_based:
        assert abs(after - before) < 1e-12
    else:
        assert abs(after - before) > 1e-6


# ---------------------------------------------------------------------------
# PROPOSITION 3 -- non-redundancy.  Here in its weakest checkable form: the
# four axes do not move together, so no one of them determines another.
# The full twelve-pair construction is in scripts/r41_propositions.py.
# ---------------------------------------------------------------------------
def test_p3_the_axes_do_not_move_together():
    import pandas as pd

    from fieldvalue import surface
    rng = np.random.default_rng(11)
    n, Kb, Kg, Kf = 6000, 5, 8, 60
    b = rng.integers(0, Kb, n)
    f = rng.integers(0, Kf, n)
    gmap = rng.integers(0, Kg, Kf)
    g = np.where(rng.random(n) < 0.7, gmap[f], rng.integers(0, Kg, n))
    eb, ef, eg = (rng.normal(0, 0.7, Kb), rng.normal(0, 1.6, Kf),
                  rng.normal(0, 1.2, Kg))
    y = (rng.random(n) < 1 / (1 + np.exp(-(eb[b] + 0.6 * ef[f]
                                           + 0.6 * eg[g] - 0.4)))).astype(int)
    X = pd.DataFrame(dict(b=b.astype(str), g=g.astype(str), f=f.astype(str)))
    s = surface(X, y, feature="f",
                baselines={"B0": ["b"], "B0+g": ["b", "g"]},
                thresholds=(0.2, 0.3, 0.4, 0.5), population=(1.0, 0.5),
                seed=3)
    sp = s.spread().set_index("axis")
    assert sp.loc["metric", "spread"] > 1e-6
    assert sp.loc["threshold", "spread"] > 1e-6
    assert sp.loc["population", "spread"] > 1e-6
    #  and no two axes agree on how much they move it
    vals = [sp.loc[a, "spread"] for a in ("metric", "threshold", "population")]
    assert len(set(round(v, 6) for v in vals)) == 3

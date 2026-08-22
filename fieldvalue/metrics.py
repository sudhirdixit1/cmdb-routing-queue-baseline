"""Metrics, implemented from scratch in numpy.

WHY NOT CALL SCIKIT-LEARN.  `scripts/r46_tool_agreement.py` re-derives the
paper's headline surface through this package and asserts it matches the
analysis scripts.  That check is only worth something if the two paths are
actually different, so every metric here is implemented directly rather than
delegated.  `tests/test_metrics.py` asserts agreement with scikit-learn to
1e-12 on random inputs, so the independence costs no correctness.

Every function takes (scores, y) with y in {0, 1} and returns a float.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-12

__all__ = ["auc", "average_precision", "brier", "brier_skill", "nagelkerke",
           "net_benefit", "expected_cost_saving", "METRICS", "RANK_BASED"]


def _check(s, y):
    s = np.asarray(s, dtype=float).ravel()
    y = np.asarray(y).ravel().astype(int)
    if s.shape != y.shape:
        raise ValueError(f"scores {s.shape} and labels {y.shape} differ")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("labels must be 0/1")
    return s, y


def auc(s, y):
    """ROC AUC as the Mann-Whitney statistic, with ties taking half credit.

    Computed from midranks, which is the definition, and which makes the tie
    convention explicit rather than inherited from a library's sort.
    """
    s, y = _check(s, y)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    ss = s[order]
    ranks = np.empty(len(s), dtype=float)
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0      # midrank, 1-based
        i = j + 1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def average_precision(s, y):
    """AP as the step-wise sum used by scikit-learn: sum_k (R_k - R_{k-1}) P_k.

    Thresholds are the distinct score values in descending order; a tied block
    is admitted whole, which is the convention the paper's section on tie
    handling discusses.
    """
    s, y = _check(s, y)
    n1 = int(y.sum())
    if n1 == 0:
        return float("nan")
    order = np.argsort(-s, kind="mergesort")
    ys = y[order]
    ss = s[order]
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    #  keep only the last index of each tied block: that is where a threshold
    #  can actually be placed
    last = np.r_[np.flatnonzero(np.diff(ss) != 0), len(ss) - 1]
    tp, fp = tp[last], fp[last]
    prec = tp / np.maximum(tp + fp, EPS)
    rec = tp / n1
    d_rec = np.diff(np.r_[0.0, rec])
    return float((d_rec * prec).sum())


def brier(s, y):
    s, y = _check(s, y)
    return float(np.mean((s - y) ** 2))


def brier_skill(s, y, p0=None):
    """1 - Brier(model) / Brier(reference).  `p0` defaults to the test-set
    base rate; the paper passes the TRAINING base rate, which is the honest
    reference and is why it is a parameter."""
    s, y = _check(s, y)
    p0 = float(np.mean(y)) if p0 is None else float(p0)
    den = float(np.mean((p0 - y) ** 2))
    return float("nan") if den <= EPS else float(1.0 - brier(s, y) / den)


def nagelkerke(s, y, p0=None):
    s, y = _check(s, y)
    p0 = float(np.mean(y)) if p0 is None else float(p0)
    pc = np.clip(s, EPS, 1 - EPS)
    ll_m = float((y * np.log(pc) + (1 - y) * np.log(1 - pc)).sum())
    ll_0 = float((y * np.log(p0) + (1 - y) * np.log(1 - p0)).sum())
    n = len(y)
    cs = 1.0 - np.exp((2.0 / n) * (ll_0 - ll_m))
    denom = 1.0 - np.exp((2.0 / n) * ll_0)
    return float("nan") if abs(denom) <= EPS else float(cs / denom)


def net_benefit(s, y, threshold):
    """Vickers' net benefit at one operating point.

    NB(t) = TP/n - (FP/n) * t/(1-t).  Requires a threshold: that is the point.
    """
    s, y = _check(s, y)
    t = float(threshold)
    if not (0.0 < t < 1.0):
        raise ValueError("threshold must lie strictly inside (0, 1)")
    act = s >= t
    tp = float((act & (y == 1)).sum())
    fp = float((act & (y == 0)).sum())
    return float((tp - fp * (t / (1.0 - t))) / len(y))


def expected_cost_saving(s, y, ratio):
    """Cost saved against treat-none at cost(FN)/cost(FP) = `ratio`.

    Identical to `ratio * net_benefit(s, y, 1/(1+ratio))`; the paper's section
    on the instrument matrix proves the identity and reports it rather than
    presenting the two as independent instruments.
    """
    r = float(ratio)
    return float(r * net_benefit(s, y, 1.0 / (1.0 + r)))


#  Name -> callable(scores, y, p0).  Net benefit is not here because it takes
#  an operating point; the surface treats the operating point as its own axis.
METRICS = {
    "auc": lambda s, y, p0: auc(s, y),
    "ap": lambda s, y, p0: average_precision(s, y),
    "brier_skill": lambda s, y, p0: brier_skill(s, y, p0),
    "nagelkerke": lambda s, y, p0: nagelkerke(s, y, p0),
}

#  Which metrics see only the ORDER of the scores.  Proposition 2 in the
#  paper: R is invariant under a strictly monotone transform of the scores if
#  and only if the metric is rank-based.  `tests/test_propositions.py` asserts
#  this table against the implementations above rather than trusting it.
RANK_BASED = {"auc": True, "ap": True, "brier_skill": False,
              "nagelkerke": False, "net_benefit": False}

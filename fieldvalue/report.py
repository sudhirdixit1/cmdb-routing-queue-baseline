"""The four objects the reporting standard requires, as functions of a
Surface.

Round nineteen.  Version 0.1 of this package computed the surface and refused
to collapse it, which is a position rather than a method.  A referee for
*Information Systems* asked what the methodological object actually is, and
the answer is these four:

    decompose(frame)   an exact functional-ANOVA (Sobol) decomposition of the
                       variance of V across the design axes -- which choice
                       moves the answer, and how much of the movement belongs
                       to no single choice
    regions(frame)     each cell labelled beneficial / harmful / unresolved
                       under an interval, and the surface labelled uniformly
                       beneficial / conditionally beneficial / sign-changing /
                       conditionally harmful / uniformly harmful / unresolved
    robustness(frame)  rho in [-1, 1]: the only state in which a scalar is a
                       safe summary of a surface is rho = 1
    regret(frame)      what a one-number report costs: the share of admissible
                       specifications whose sign disagrees with it, and the
                       performance forgone or destroyed by acting on it

Each takes the tidy frame a Surface yields and returns a DataFrame, so they
compose with anything that can produce that frame -- including a pipeline that
is not this package's.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_AXES = ("baseline_pair", "metric", "population", "regime")


def _axis_columns(frame, axes):
    return [a for a in axes if a in frame.columns and frame[a].nunique() > 1]


def decompose(frame, value="V", axes=DEFAULT_AXES):
    """First-order and total Sobol indices for `value` over `axes`.

    S_i     = Var( E[V | X_i] ) / Var(V)
    S_Ti    = 1 - Var( E[V | X_~i] ) / Var(V)

    The design need not be balanced: conditional means are taken over whatever
    levels are present and weighted by their share, which is the standard
    estimator when a complete crossing has occasional missing cells.  The
    difference S_Ti - S_i is the share that lives in interactions, and on real
    surfaces it is usually the largest single term.
    """
    d = pd.DataFrame(frame).dropna(subset=[value])
    use = _axis_columns(d, axes)
    tot = float(d[value].var(ddof=0))
    rows = []
    if not np.isfinite(tot) or tot <= 0 or not use:
        for a in axes:
            rows.append(dict(axis=a, S=np.nan, S_total=np.nan, levels=0))
        return pd.DataFrame(rows)
    for a in use:
        cond = d.groupby(a)[value].mean()
        w = d.groupby(a)[value].size() / float(len(d))
        mu = float((cond * w).sum())
        S_i = float((w * (cond - mu) ** 2).sum()) / tot
        others = [b for b in use if b != a]
        if others:
            g = d.groupby(others)[value]
            c2, w2 = g.mean(), g.size() / float(len(d))
            mu2 = float((c2 * w2).sum())
            S_noti = float((w2 * (c2 - mu2) ** 2).sum()) / tot
        else:
            S_noti = 0.0
        rows.append(dict(axis=a, S=S_i, S_total=max(0.0, 1.0 - S_noti),
                         levels=int(d[a].nunique())))
    out = pd.DataFrame(rows)
    out["interaction"] = (out.S_total - out.S).clip(lower=0)
    return out.sort_values("S", ascending=False).reset_index(drop=True)


def regions(frame, value="V", lo="lo", hi="hi", exclude=()):
    """Label every cell, and the surface.

    A cell is BENEFICIAL if its lower bound is above zero, HARMFUL if its
    upper bound is below zero, UNRESOLVED otherwise.  Without bounds the
    labels fall back to the sign of the point estimate and the surface is
    reported as unresolved-by-construction, because a sign without an interval
    is not a resolution.
    """
    d = pd.DataFrame(frame).copy()
    if exclude:
        for col in ("baseline", "baseline_pair", "rung"):
            if col in d.columns:
                d = d[~d[col].astype(str).isin(set(exclude))]
    have = lo in d.columns and hi in d.columns
    if have:
        d["label"] = np.where(d[lo] > 0, "beneficial",
                              np.where(d[hi] < 0, "harmful", "unresolved"))
    else:
        d["label"] = np.where(d[value] > 0, "positive-point-estimate",
                              "non-positive-point-estimate")
    return d


def robustness(frame, value="V", lo="lo", hi="hi", exclude=()):
    """rho and the surface's region, as a one-row frame."""
    d = regions(frame, value=value, lo=lo, hi=hi, exclude=exclude)
    n = len(d)
    if n == 0:
        return pd.DataFrame([dict(n_cells=0, region="empty", rho=np.nan)])
    nb = int((d.label == "beneficial").sum())
    nh = int((d.label == "harmful").sum())
    nu = int((d.label == "unresolved").sum())
    #  "no intervals supplied" is a property of the INPUT, not of the labels.
    #  Testing it by asking whether any cell resolved conflates it with the
    #  genuine unresolved region -- a surface where bounds were given and
    #  every one of them straddles zero -- and that conflation made the
    #  package disagree with the pipeline on two pairs of this paper's corpus,
    #  both of them honestly unresolved.  The fallback labels are unambiguous,
    #  so read the answer off them.
    if not len(set(d.label) & {"beneficial", "harmful", "unresolved"}):
        region = "unresolved (no intervals supplied)"
    elif nh and nb:
        region = "sign-changing"
    elif nb and not nh and nu == 0:
        region = "uniformly beneficial"
    elif nb and not nh:
        region = "conditionally beneficial"
    elif nh and not nb and nu == 0:
        region = "uniformly harmful"
    elif nh and not nb:
        region = "conditionally harmful"
    else:
        region = "unresolved"
    return pd.DataFrame([dict(n_cells=n, n_beneficial=nb, n_harmful=nh,
                              n_unresolved=nu, region=region,
                              rho=(nb - nh) / float(n),
                              share_positive=float((d[value] > 0).mean()))])


def regret(frame, value="V", exclude=()):
    """What a one-number report costs, per cell.

    misreport(s) = P_{s'}[ sign V_{s'} != sign V_s ]
    regret(s)    = E[max(0, -V)] if V_s > 0 else E[max(0, V)]

    The first is what share of the admissible set a reader who acts on cell s
    would be misled about; the second is the performance destroyed by adopting
    when the reader's own cell is harmful, or forgone by declining when it is
    beneficial.
    """
    d = pd.DataFrame(frame).dropna(subset=[value]).copy()
    if exclude:
        for col in ("baseline", "baseline_pair", "rung"):
            if col in d.columns:
                d = d[~d[col].astype(str).isin(set(exclude))]
    if d.empty:
        return d.assign(misreport=[], regret=[])
    v = d[value].values
    pos = v > 0
    p = float(pos.mean())
    d["misreport"] = np.where(pos, 1.0 - p, p)
    d["regret"] = np.where(pos, float(np.mean(np.maximum(0.0, -v))),
                           float(np.mean(np.maximum(0.0, v))))
    return d


def summary(frame, value="V", lo="lo", hi="hi", axes=DEFAULT_AXES,
            exclude=()):
    """The minimum reportable form, as three frames rather than one number."""
    return dict(decomposition=decompose(frame, value=value, axes=axes),
                robustness=robustness(frame, value=value, lo=lo, hi=hi,
                                      exclude=exclude),
                regret=regret(frame, value=value, exclude=exclude)
                [["misreport", "regret"]].describe())

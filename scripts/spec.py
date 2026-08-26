"""spec -- THE DESIGN SPACE, AND THE ESTIMATOR THAT WALKS IT.

Round nineteen.  The referee's third major comment is that the estimand
V(f | B, m, theta) omits choices the manuscript itself admits matter.  This
module answers it by making the design space explicit and enumerable.

    A SPECIFICATION s is a complete assignment to every axis below.
    The estimand is

        V_s(f) = m_theta( A_s(D_train, B + {f_q}), D_test )
               - m_theta( A_s(D_train, B),         D_test )

    where s names the learner A, the encoding, the target, the split, the
    feature-availability rule (which decision time), the register quality
    mechanism q, the baseline B, the metric m and the operating point theta.

Ten axes, every one of them a choice an analyst makes and usually does not
report:

  1  learner        logit | logit_fr | hgb | hgb_iso
  2  encoding       onehot | frequency | cross-fitted target
  3  target         handover | duration
  4  split          holdout70 | rolling-origin fold k
  5  availability   t_interaction | t_incident   (BPIC14 only; see s08)
  6  quality        clean | mask_* | corrupt | duplicate | stale
  7  baseline       a nested ladder, every ordered pair
  8  metric         auc | ap | brier_skill | nagelkerke | logloss_skill | net_benefit
  9  operating pt   the net-benefit grid
 10  seed           for the stochastic quality mechanisms

Nothing in this module reads a test outcome to make a choice.  Every quality
mechanism, every encoder and every frequency ranking is fitted on the training
half alone; `assert_train_only` is the check, and s01 executes it.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

SEED = 20260819
EMPTY = "__EMPTY__"
EPS = 1e-12
TRAIN_FRAC = 0.70
NB_GRID = tuple(np.round(np.arange(0.05, 0.8001, 0.025), 4))
SCALARS = ("auc", "ap", "brier_skill", "nagelkerke", "logloss_skill")

# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
from sklearn.metrics import average_precision_score, roc_auc_score


#  EVERY INSTRUMENT TAKES A WEIGHT, BECAUSE THE RESAMPLING SCHEME DOES.
#  Under the weighted block bootstrap of `block_weights` a draw is a weight
#  vector rather than an index multiset, so a metric computed by counting rows
#  would silently evaluate the point estimate in every draw.  `w=None` is the
#  unweighted case and reduces to the arithmetic that was here before, exactly:
#  `_wmean(x, None)` is `x.mean()`.
def _wmean(x, w=None):
    x = np.asarray(x, float)
    if w is None:
        return float(np.mean(x))
    w = np.asarray(w, float)
    s = float(np.sum(w))
    return float(np.dot(x, w) / s) if s > EPS else np.nan


def brier_skill(p, y, p0, w=None):
    ref = _wmean((p0 - y) ** 2, w)
    return float(1.0 - _wmean((p - y) ** 2, w) / ref) if ref > EPS else np.nan


def _ll(p, y, w=None):
    p = np.clip(np.asarray(p, float), 1e-12, 1 - 1e-12)
    y = np.asarray(y, float)
    return _wmean(y * np.log(p) + (1 - y) * np.log(1 - p), w)


def logloss_skill(p, y, p0, w=None):
    """1 - deviance(p) / deviance(intercept).  A proper scoring rule on the
    log scale, and the one instrument here that is neither rank-based nor a
    squared error."""
    ref = _ll(np.full(len(np.asarray(y)), float(p0)), y, w)
    return float(1.0 - _ll(p, y, w) / ref) if abs(ref) > EPS else np.nan


def nagelkerke(p, y, p0, w=None):
    #  the effective sample size, which is the row count when w is None and
    #  Kish's when it is not: the Cox-Snell exponent is per-observation, so a
    #  weighted fit must divide by the weight it actually carries.
    n = _eff_n(len(y), w)
    ll1, ll0 = _ll(p, y, w) * n, _ll(np.full(len(y), float(p0)), y, w) * n
    cox = 1.0 - np.exp(2.0 * (ll0 - ll1) / n)
    mx = 1.0 - np.exp(2.0 * ll0 / n)
    return float(cox / mx) if mx > EPS else np.nan


def _eff_n(n, w=None):
    if w is None:
        return float(n)
    w = np.asarray(w, float)
    s2 = float(np.sum(w ** 2))
    return float(np.sum(w) ** 2 / s2) if s2 > EPS else float(n)


def net_benefit(p, y, t, w=None):
    """Vickers-Elkin net benefit per case, at exchange rate t/(1-t)."""
    y = np.asarray(y).astype(int)
    sel = np.asarray(p) >= t
    if len(y) == 0:
        return np.nan
    tp = _wmean(sel & (y == 1), w)
    fp = _wmean(sel & (y == 0), w)
    return float(tp - fp * (t / (1.0 - t)))


def all_metrics(p, y, prev_tr, grid=NB_GRID, w=None):
    y = np.asarray(y).astype(int)
    two = len(np.unique(y)) > 1
    kw = {} if w is None else {"sample_weight": np.asarray(w, float)}
    out = {"auc": roc_auc_score(y, p, **kw) if two else np.nan,
           "ap": average_precision_score(y, p, **kw) if two else np.nan,
           "brier_skill": brier_skill(p, y, prev_tr, w),
           "nagelkerke": nagelkerke(p, y, prev_tr, w),
           "logloss_skill": logloss_skill(p, y, prev_tr, w)}
    for t in grid:
        out["nb_%.3f" % t] = net_benefit(p, y, float(t), w)
    return out


# --------------------------------------------------------------------------
# calibration diagnostics (referee comment 8, phase 4)
# --------------------------------------------------------------------------
def calibration(p, y):
    """Cox calibration slope and intercept, plus the Brier score.  The slope
    is the coefficient of the linear predictor in a logistic recalibration;
    the intercept is the offset that makes the mean predicted risk match the
    observed rate with the slope held at one."""
    from scipy.optimize import brentq
    from sklearn.linear_model import LogisticRegression
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    lp = np.log(p / (1 - p))
    out = {"brier": float(np.mean((p - y) ** 2))}
    if len(np.unique(y)) < 2 or float(np.std(lp)) < 1e-9:
        out["cal_slope"] = np.nan
        out["cal_intercept"] = np.nan
        return out
    m = LogisticRegression(max_iter=2000, C=1e6).fit(lp.reshape(-1, 1), y)
    out["cal_slope"] = float(m.coef_[0][0])

    def g(a):
        q = 1.0 / (1.0 + np.exp(-(a + lp)))
        return float(np.mean(q - y))

    try:
        out["cal_intercept"] = float(brentq(g, -25, 25))
    except Exception:
        out["cal_intercept"] = np.nan
    return out


def unseen_rate(tr, te, cols):
    """Share of test rows carrying at least one level unseen in training.
    Referee phase 4: report unseen-category rates."""
    if not cols:
        return 0.0
    bad = np.zeros(len(te), dtype=bool)
    for c in cols:
        seen = set(tr[c].astype(str).unique())
        bad |= ~te[c].astype(str).isin(seen).values
    return float(bad.mean())


# --------------------------------------------------------------------------
# learners.  Each returns test-set probabilities; each is fitted on train only.
# --------------------------------------------------------------------------
def _onehot_logit(tr, te, cols, y, seed, C_=1.0, w=None):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C_, random_state=seed)
    #  `handle_unknown="ignore"` still encodes every level PRESENT in tr, and
    #  under the weighted scheme every level of the register is present in
    #  every draw, which is the whole point of it.
    m.fit(X, y, sample_weight=None if w is None else np.asarray(w, float))
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def _freq_logit(tr, te, cols, y, seed, w=None):
    """Frequency (count) encoding fitted on the training half only, then
    logistic regression on the log counts.  A second, target-free encoding of
    the same columns, so the encoding axis can be measured rather than
    asserted."""
    from sklearn.linear_model import LogisticRegression
    Xtr, Xte = [], []
    ww = None if w is None else np.asarray(w, float)
    for c in cols:
        a = tr[c].astype(str)
        #  THE COUNT IS THE DRAW'S COUNT.  A frequency encoding is a statistic
        #  of the resample, so under weights it is the WEIGHTED count; using
        #  the unweighted one would encode the point estimate's frequencies
        #  into every draw and understate the encoding's own variability.
        vc = (a.value_counts() if ww is None
              else pd.Series(ww, index=a.values).groupby(level=0).sum())
        Xtr.append(np.log1p(a.map(vc).fillna(0.0).values.astype(float)))
        Xte.append(np.log1p(te[c].astype(str).map(vc).fillna(0.0)
                            .values.astype(float)))
    Xtr, Xte = np.column_stack(Xtr), np.column_stack(Xte)
    if ww is None:
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    else:
        mu = np.average(Xtr, axis=0, weights=ww)
        sd = np.sqrt(np.average((Xtr - mu) ** 2, axis=0, weights=ww)) + 1e-9
    m = LogisticRegression(max_iter=3000, random_state=seed)
    m.fit((Xtr - mu) / sd, y, sample_weight=ww)
    return m.predict_proba((Xte - mu) / sd)[:, 1]


def _wtarget_encode(Xtr, y, Xte, w, seed, cv=5, smooth=20.0):
    """A CROSS-FITTED TARGET ENCODER THAT TAKES A WEIGHT.

    `sklearn.preprocessing.TargetEncoder` has no `sample_weight`, and a target
    encoding is a statistic of the training data: under the weighted scheme an
    unweighted encoder would put the point estimate's category means inside
    every draw, so the draw would understate exactly the variability the
    encoding contributes.  This is the same estimator with the weights carried
    through -- a cross-fitted, m-smoothed category mean:

        mhat(c) = (sum_i w_i y_i [x_i = c] + smooth * ybar) /
                  (sum_i w_i [x_i = c] + smooth)

    computed on the folds a row is NOT in, so no training row sees its own
    outcome in its own encoding, and with the full training half for the test
    rows.  A category unseen in a fold falls back to the weighted prior.

    It is used only when `w is not None`.  With no weights the learner keeps
    sklearn's encoder, so every unweighted number this repository has ever
    produced is unchanged by this function's existence.
    """
    from sklearn.model_selection import KFold
    Xtr = np.asarray(Xtr, dtype=object)
    Xte = np.asarray(Xte, dtype=object)
    y = np.asarray(y, float)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    n, k = Xtr.shape
    Etr = np.zeros((n, k), float)
    Ete = np.zeros((len(Xte), k), float)

    def _means(idx, col):
        a = Xtr[idx, col]
        ser = pd.DataFrame({"c": a, "w": w[idx], "wy": w[idx] * y[idx]})
        g = ser.groupby("c", sort=False)[["w", "wy"]].sum()
        prior = float(ser.wy.sum() / ser.w.sum()) if ser.w.sum() > 0 else 0.5
        m = (g.wy + smooth * prior) / (g.w + smooth)
        return m, prior

    for col in range(k):
        #  the test half is encoded with the whole training half
        m, prior = _means(np.arange(n), col)
        Ete[:, col] = pd.Series(Xte[:, col]).map(m).fillna(prior).values
        #  and each training fold with the folds it is not in
        kf = KFold(n_splits=min(cv, max(2, n // 2)), shuffle=True,
                   random_state=seed)
        for fit_idx, out_idx in kf.split(np.arange(n)):
            mm, pp = _means(fit_idx, col)
            Etr[out_idx, col] = (pd.Series(Xtr[out_idx, col]).map(mm)
                                 .fillna(pp).values)
    return Etr, Ete


def _hgb(tr, te, cols, y, seed, calibrate=None, w=None):
    """Cross-fitted target encoding plus histogram gradient boosting.  The
    encoder is cross-fitted inside the training half, so no training row sees
    its own outcome in its own encoding; the test half is encoded with the
    full-train statistics.  Native categorical support in
    HistGradientBoosting caps cardinality at 255 and the registers here run to
    3,019 levels, which is why the encoding is target-based and cross-fitted
    rather than one-hot."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    if w is None:
        from sklearn.preprocessing import TargetEncoder
        e = TargetEncoder(target_type="binary", cv=5, random_state=seed)
        X = e.fit_transform(tr[cols].astype(str).values, y)
        Xt = e.transform(te[cols].astype(str).values)
    else:
        X, Xt = _wtarget_encode(tr[cols].astype(str).values, y,
                                te[cols].astype(str).values, w, seed)
    base = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                          random_state=seed)
    if calibrate:
        from sklearn.calibration import CalibratedClassifierCV
        base = CalibratedClassifierCV(base, method=calibrate, cv=3)
    ww = None if w is None else np.asarray(w, float)
    return base.fit(X, y, sample_weight=ww).predict_proba(Xt)[:, 1]


#  Every learner takes an optional training weight as its sixth argument.
#  Passing none is the scheme this repository ran until round twenty-seven and
#  reproduces its numbers exactly; passing one is the weighted block bootstrap.
LEARNERS = {
    "logit": lambda tr, te, c, y, s, w=None: _onehot_logit(tr, te, c, y, s, w=w),
    "logit_fr": lambda tr, te, c, y, s, w=None: _freq_logit(tr, te, c, y, s, w=w),
    "hgb": lambda tr, te, c, y, s, w=None: _hgb(tr, te, c, y, s, w=w),
    "hgb_iso": lambda tr, te, c, y, s, w=None: _hgb(tr, te, c, y, s,
                                                    calibrate="isotonic", w=w),
}
LEARNER_ENCODING = {"logit": "onehot", "logit_fr": "frequency",
                    "hgb": "target-xfit", "hgb_iso": "target-xfit"}
LEARNER_LABEL = {"logit": "logistic (one-hot)",
                 "logit_fr": "logistic (frequency)",
                 "hgb": "gradient boosting",
                 "hgb_iso": "gradient boosting, isotonic"}


# --------------------------------------------------------------------------
# register quality mechanisms.  Referee comment 10.
#
# Each is a map from the register-valued column to a degraded column, and each
# is parameterised by the TRAINING half alone: the frequency ranking that
# decides which identities vanish first, the set of identities known by the
# split point, and the alphabet a corruption draws from.  `train_index` is
# passed explicitly so this cannot be got wrong silently.
# --------------------------------------------------------------------------
QUALITY_KINDS = ("clean", "mask_rare", "mask_random", "mask_common",
                 "corrupt", "duplicate", "stale")

#: the mechanisms that draw randomness and must therefore be averaged over
#: seeds.  Named here rather than in each caller so a caller cannot forget one.
STOCHASTIC_KINDS = frozenset({"mask_random", "corrupt", "duplicate"})

QUALITY_LABEL = {
    "clean": "as recorded",
    "mask_rare": "population: the long tail is absent",
    "mask_common": "population: the core is absent",
    "mask_random": "population: absent at random",
    "corrupt": "accuracy: a share of rows carry the wrong identity",
    "duplicate": "reconciliation: a share of identities exist twice",
    "stale": "discovery: identities first seen after the split are absent",
}


def degrade(col, kind, level, rng, train_index):
    """Return a degraded copy of `col`.

    `level` is the share POPULATED for mask_*, the share CORRUPTED for
    corrupt, the share of identities SPLIT for duplicate, and is ignored for
    clean and stale.
    """
    s = col.astype(str).copy()
    tr = s.iloc[train_index]
    if kind == "clean":
        return s
    if kind == "stale":
        known = set(tr.unique())
        return s.where(s.isin(known), EMPTY)
    if kind == "mask_random":
        return s.where(rng.random(len(s)) < level, EMPTY)
    if kind in ("mask_rare", "mask_common"):
        vc = tr.value_counts()
        order = vc.index[::-1] if kind == "mask_rare" else vc.index
        cum = vc.loc[order].cumsum() / max(1, len(tr))
        drop = set(order[cum <= (1.0 - level)])
        return s.where(~s.isin(drop), EMPTY)
    if kind == "corrupt":
        alpha = tr.value_counts(normalize=True)
        if len(alpha) < 2:
            return s
        hit = rng.random(len(s)) < level
        k = int(hit.sum())
        if k == 0:
            return s
        draw = rng.choice(alpha.index.values, size=k, p=alpha.values)
        out = s.values.astype(object).copy()
        out[hit] = draw
        return pd.Series(out, index=s.index).astype(str)
    if kind == "duplicate":
        ids = tr.unique()
        k = max(1, int(round(level * len(ids))))
        dup = set(rng.choice(ids, size=min(k, len(ids)), replace=False))
        flip = rng.random(len(s)) < 0.5
        out = np.where(s.isin(dup).values & flip, s.values.astype(str) + "#2",
                       s.values.astype(str))
        return pd.Series(out, index=s.index)
    raise ValueError("unknown quality mechanism %r" % kind)


def assert_train_only(col, kind, level, seed, train_index):
    """The degradation must not change when the TEST half changes.  Perturb
    the test half, re-degrade, and require the training half's degraded values
    to be identical.  Executed by s01, not merely asserted in prose."""
    a = degrade(col, kind, level, np.random.default_rng(seed), train_index)
    c2 = col.astype(str).copy()
    tail = np.arange(len(col)) > int(np.max(train_index))
    c2.iloc[tail] = "__PERTURBED__"
    b = degrade(c2, kind, level, np.random.default_rng(seed), train_index)
    return bool((a.iloc[train_index].values == b.iloc[train_index].values).all())


# --------------------------------------------------------------------------
# splits.  Referee comment 8: rolling origin, not one holdout.
# --------------------------------------------------------------------------
def splits(n, kind="holdout70", n_folds=5, min_train=0.40):
    """Yield (name, train_idx, test_idx) in TIME ORDER.  `rolling` is an
    expanding-origin scheme: fold k trains on everything before the k-th
    boundary and tests on the block that follows it."""
    idx = np.arange(n)
    if kind == "holdout70":
        cut = int(n * TRAIN_FRAC)
        yield ("holdout70", idx[:cut], idx[cut:])
        return
    if kind == "rolling":
        first = int(n * min_train)
        step = max(1, (n - first) // n_folds)
        for k in range(n_folds):
            a = first + k * step
            b = n if k == n_folds - 1 else min(n, first + (k + 1) * step)
            if b - a < 50 or a < 50:
                continue
            yield ("rolling%d" % (k + 1), idx[:a], idx[a:b])
        return
    raise ValueError(kind)


# --------------------------------------------------------------------------
# the moving-block bootstrap.  Referee comment 8: the pipeline is refitted
# inside every draw, and the blocks carry the temporal dependence.
# --------------------------------------------------------------------------
def block_indices(n, rng, ell=None):
    if ell is None:
        ell = max(10, int(round(n ** (1.0 / 3.0))))
    k = int(np.ceil(n / float(ell)))
    starts = rng.integers(0, max(1, n - ell + 1), size=k)
    out = np.concatenate([np.arange(s, s + ell) for s in starts])[:n]
    return np.clip(out, 0, n - 1)


def block_length(n, ell=None):
    """The block length the two schemes share, so a comparison between them
    is a comparison of schemes and not of bandwidths."""
    return int(ell) if ell is not None else max(10, int(round(n ** (1.0 / 3.0))))


def block_weights(n, rng, ell=None):
    """THE WEIGHTED BLOCK BOOTSTRAP: a draw is a weight vector, not a subset.

    `block_indices` resamples blocks with replacement, so about $1 - e^{-1}$ of
    the rows appear in any one draw and the rest do not appear at all.  On a
    high-cardinality register that is not a nuisance, it is a bias: a register
    level absent from a draw cannot be fitted in it, so the refit is of a
    smaller register than the one the estimand is about, and the bootstrap
    distribution is displaced.  The displacement does not shrink with $n$ while
    the interval's half-width does, so the interval becomes a correct interval
    for the wrong quantity, and the pivotal interval built from it can exclude
    its own point estimate.

    The repair is to give every row a positive weight in every draw.  The
    blocks are a circular tiling of the row order at a RANDOM OFFSET, so a
    block boundary is not fixed across draws and the temporal dependence
    survives at the same length scale `block_indices` uses; each block gets one
    weight, and the block weights are $k$ times a Dirichlet$(1,\dots,1)$ --
    equivalently, i.i.d. exponentials normalised to sum to $k$.  Every row
    therefore carries the weight of exactly one block, the weights are strictly
    positive with probability one, they average to one, and their variance is
    one, which is the variance of a block's multiplicity under
    `block_indices`.  The two schemes differ in whether a row can be dropped
    and in nothing else that is declared.

    Returns a float array of length `n` with mean 1.
    """
    ell = block_length(n, ell)
    k = int(np.ceil(n / float(ell)))
    #  one exponential per block, normalised: (w_1..w_k) ~ k * Dirichlet(1^k)
    xi = rng.exponential(1.0, size=k)
    s = float(xi.sum())
    if s <= 0:
        return np.ones(n, float)
    xi = xi * (k / s)
    off = int(rng.integers(0, ell)) if ell > 1 else 0
    #  the circular tiling: row i belongs to block ((i - off) mod n) // ell
    idx = ((np.arange(n) - off) % n) // ell
    w = xi[np.clip(idx, 0, k - 1)]
    #  a tiling of n rows into blocks of length ell leaves a short last block;
    #  renormalising to mean one keeps the weight budget exactly n whatever
    #  the remainder is
    return w * (n / float(w.sum()))


# --------------------------------------------------------------------------
# the nested baseline ladder
# --------------------------------------------------------------------------
def ladder_for(d, b0, g, extra=()):
    """The nested ladder.  B_half is the first half of B0 under a
    deterministic order -- by cardinality then name -- so no rung is chosen
    after an outcome has been seen.  `extra` appends further admitted fields,
    each as its own rung, in the order given."""
    def card(c):
        return int(d[c].astype(str).nunique())
    order = sorted(list(b0), key=lambda c: (card(c), str(c)))
    half = order[:max(1, len(order) // 2)]
    L = [("B_empty", []), ("B_half", half), ("B_intake", list(b0)),
         ("B_intake_g", list(b0) + [g])]
    cols = list(b0) + [g]
    for name, add in extra:
        cols = cols + list(add)
        L.append(("B_" + name, list(cols)))
    return L


#: The rungs an ANALYST could actually build.  The intercept-only rung exists
#: so the surface is complete, but the referee is right that no analyst builds
#: it, so it is excluded from every headline comparison and marked here once.
IMPLAUSIBLE_RUNGS = ("B_empty",)


def fingerprint(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode())
    return h.hexdigest()[:16]


# --------------------------------------------------------------------------
# result files
# --------------------------------------------------------------------------
def result_path(name):
    """Resolve a result file that may be stored compressed.

    `results/s01_surface.csv` is 52 MB uncompressed and 4 MB gzipped, and a
    repository that carries the uncompressed one is a repository nobody
    clones.  Writers gzip anything over a few megabytes; readers call this and
    do not care, because pandas reads `.gz` by extension.
    """
    from pathlib import Path
    from common import RESULTS
    p = Path(RESULTS) / name
    if p.exists():
        return p
    q = Path(RESULTS) / (name + ".gz")
    if q.exists():
        return q
    return p


def read_results(name, **kw):
    import pandas as pd
    return pd.read_csv(result_path(name), **kw)

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


def brier_skill(p, y, p0):
    ref = float(np.mean((p0 - y) ** 2))
    return float(1.0 - np.mean((p - y) ** 2) / ref) if ref > EPS else np.nan


def _ll(p, y):
    p = np.clip(np.asarray(p, float), 1e-12, 1 - 1e-12)
    y = np.asarray(y, float)
    return float(np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def logloss_skill(p, y, p0):
    """1 - deviance(p) / deviance(intercept).  A proper scoring rule on the
    log scale, and the one instrument here that is neither rank-based nor a
    squared error."""
    ref = _ll(np.full(len(np.asarray(y)), float(p0)), y)
    return float(1.0 - _ll(p, y) / ref) if abs(ref) > EPS else np.nan


def nagelkerke(p, y, p0):
    n = len(y)
    ll1, ll0 = _ll(p, y) * n, _ll(np.full(n, float(p0)), y) * n
    cox = 1.0 - np.exp(2.0 * (ll0 - ll1) / n)
    mx = 1.0 - np.exp(2.0 * ll0 / n)
    return float(cox / mx) if mx > EPS else np.nan


def net_benefit(p, y, t):
    """Vickers-Elkin net benefit per case, at exchange rate t/(1-t)."""
    y = np.asarray(y).astype(int)
    sel = np.asarray(p) >= t
    n = len(y)
    if n == 0:
        return np.nan
    tp = float(np.sum(sel & (y == 1))) / n
    fp = float(np.sum(sel & (y == 0))) / n
    return float(tp - fp * (t / (1.0 - t)))


def all_metrics(p, y, prev_tr, grid=NB_GRID):
    y = np.asarray(y).astype(int)
    two = len(np.unique(y)) > 1
    out = {"auc": roc_auc_score(y, p) if two else np.nan,
           "ap": average_precision_score(y, p) if two else np.nan,
           "brier_skill": brier_skill(p, y, prev_tr),
           "nagelkerke": nagelkerke(p, y, prev_tr),
           "logloss_skill": logloss_skill(p, y, prev_tr)}
    for t in grid:
        out["nb_%.3f" % t] = net_benefit(p, y, float(t))
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
def _onehot_logit(tr, te, cols, y, seed, C_=1.0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C_, random_state=seed).fit(X, y)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def _freq_logit(tr, te, cols, y, seed):
    """Frequency (count) encoding fitted on the training half only, then
    logistic regression on the log counts.  A second, target-free encoding of
    the same columns, so the encoding axis can be measured rather than
    asserted."""
    from sklearn.linear_model import LogisticRegression
    Xtr, Xte = [], []
    for c in cols:
        a = tr[c].astype(str)
        vc = a.value_counts()
        Xtr.append(np.log1p(a.map(vc).fillna(0.0).values.astype(float)))
        Xte.append(np.log1p(te[c].astype(str).map(vc).fillna(0.0)
                            .values.astype(float)))
    Xtr, Xte = np.column_stack(Xtr), np.column_stack(Xte)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    m = LogisticRegression(max_iter=3000, random_state=seed)
    m.fit((Xtr - mu) / sd, y)
    return m.predict_proba((Xte - mu) / sd)[:, 1]


def _hgb(tr, te, cols, y, seed, calibrate=None):
    """Cross-fitted target encoding plus histogram gradient boosting.  The
    encoder is cross-fitted inside the training half, so no training row sees
    its own outcome in its own encoding; the test half is encoded with the
    full-train statistics.  Native categorical support in
    HistGradientBoosting caps cardinality at 255 and the registers here run to
    3,019 levels, which is why the encoding is target-based and cross-fitted
    rather than one-hot."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.preprocessing import TargetEncoder
    e = TargetEncoder(target_type="binary", cv=5, random_state=seed)
    X = e.fit_transform(tr[cols].astype(str).values, y)
    Xt = e.transform(te[cols].astype(str).values)
    base = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                          random_state=seed)
    if calibrate:
        from sklearn.calibration import CalibratedClassifierCV
        base = CalibratedClassifierCV(base, method=calibrate, cv=3)
    return base.fit(X, y).predict_proba(Xt)[:, 1]


LEARNERS = {
    "logit": lambda tr, te, c, y, s: _onehot_logit(tr, te, c, y, s),
    "logit_fr": lambda tr, te, c, y, s: _freq_logit(tr, te, c, y, s),
    "hgb": lambda tr, te, c, y, s: _hgb(tr, te, c, y, s),
    "hgb_iso": lambda tr, te, c, y, s: _hgb(tr, te, c, y, s, calibrate="isotonic"),
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

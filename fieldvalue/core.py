"""The estimand, the estimator, and the surface.

    V(f | B, m, theta)  =  m(B + {f}, theta) - m(B, theta)
    R(f | B0, B1, m, theta) = 1 - V(f | B1, m, theta) / V(f | B0, m, theta)

`surface()` computes V and R over the CROSS PRODUCT of four axes -- baseline,
metric, operating point, register population -- and returns a `Surface`, which
refuses to collapse itself to one number.  That refusal is the standard this
package exists to encode; see `Surface.headline`.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .metrics import METRICS, RANK_BASED, net_benefit

EPS = 1e-12
EMPTY = "__EMPTY__"
DEFAULT_METRICS = ("auc", "ap", "brier_skill", "nagelkerke")
DEFAULT_THRESHOLDS = tuple(np.round(np.arange(0.05, 0.8001, 0.025), 4))
DEFAULT_POPULATION = (1.00, 0.75, 0.50, 0.25)


class SingleNumberRefused(RuntimeError):
    """Raised when a caller asks the surface for one number.

    Not a defensive check.  The whole argument of the paper this package
    accompanies is that a feature-value claim is a function of four arguments
    and that collapsing it to a scalar hides the arguments.  A library that
    offered `float(surface)` would be arguing the opposite.
    """


def _fit_predict(train, test, cols, target, seed):
    """One-hot + logistic regression, the estimator every number in the
    accompanying paper uses.  `handle_unknown='ignore'` so a level unseen in
    training does not blow up; C=1.0 and max_iter=3000 are the paper's."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    enc = OneHotEncoder(handle_unknown="ignore")
    Xtr = enc.fit_transform(train[list(cols)].astype(str))
    model = LogisticRegression(max_iter=3000, C=1.0, random_state=seed)
    model.fit(Xtr, train[target].values)
    Xte = enc.transform(test[list(cols)].astype(str))
    return model.predict_proba(Xte)[:, 1]


def _mask(col, level, regime, rng):
    """Degrade a register to `level` populated.  A masked value becomes an
    explicit EMPTY level, not a dropped row: a desk with a half-populated
    register still has the cases."""
    s = col.astype(str)
    if level >= 1.0:
        return s
    if regime == "random":
        return s.where(rng.random(len(s)) < level, EMPTY)
    if regime == "rare-first":
        vc = s.value_counts()
        order = vc.index[::-1]
        cum = vc.loc[order].cumsum() / len(s)
        return s.where(~s.isin(set(order[cum <= (1.0 - level)])), EMPTY)
    if regime == "common-first":
        vc = s.value_counts()
        cum = vc.cumsum() / len(s)
        return s.where(~s.isin(set(vc.index[cum <= (1.0 - level)])), EMPTY)
    raise ValueError(f"unknown regime {regime!r}")


@dataclass
class Surface:
    """V and R over the four axes.  Deliberately not a number."""
    frame: pd.DataFrame
    feature: str
    baselines: dict
    metrics: tuple
    thresholds: tuple
    population: tuple
    n_boot: int
    seed: int
    n_train: int = 0
    n_test: int = 0
    prevalence: float = float("nan")
    notes: list = field(default_factory=list)

    # -- the refusal -----------------------------------------------------
    def __float__(self):
        raise SingleNumberRefused(self._why())

    def headline(self):
        raise SingleNumberRefused(self._why())

    def _why(self):
        r = self.frame.R.dropna()
        span = (f"{r.min():+.3f} to {r.max():+.3f} over {len(r)} cells"
                if len(r) else "undefined: no cell has a positive denominator")
        return (
            "fieldvalue does not emit a single number for a feature's value, "
            "by design.\n"
            f"  On this data the admissibility reduction R runs {span}.\n"
            "  R is a function of four arguments -- the baseline, the metric, "
            "the operating\n"
            "  point and the register's population -- and a scalar hides all "
            "four.  Use\n"
            "  .report() for the minimum reportable form, .to_frame() for the "
            "surface, or\n"
            "  .at(baseline=..., metric=..., threshold=..., population=...) "
            "for one cell,\n"
            "  which forces you to say which cell you are standing in.")

    # -- the accessors ---------------------------------------------------
    def at(self, baseline=None, metric="auc", threshold=None, population=1.0,
           regime="rare-first"):
        f = self.frame
        if baseline is not None:
            f = f[f.baseline_pair == baseline]
        f = f[(f.metric == metric) & (f.population == population)]
        f = f[(f.regime == regime) | (f.population == 1.0)]
        if threshold is not None:
            f = f[np.isclose(f.threshold.astype(float), float(threshold))]
        else:
            f = f[f.threshold.isna()]
        if len(f) != 1:
            raise KeyError(f"{len(f)} cells match; name the cell exactly")
        return f.iloc[0]

    def to_frame(self):
        return self.frame.copy()

    def spread(self):
        """How much each axis moves R with the others held at the reference."""
        f = self.frame
        ref = f[(f.population == 1.0)]
        rows = []
        base = ref[(ref.metric == "auc") & (ref.threshold.isna())]
        rows.append(("baseline", base.R.min(), base.R.max(), len(base)))
        m = ref[(ref.baseline_pair == self._ref_pair())
                & (ref.threshold.isna())]
        rows.append(("metric", m.R.min(), m.R.max(), len(m)))
        t = ref[(ref.baseline_pair == self._ref_pair())
                & (ref.threshold.notna())]
        rows.append(("threshold", t.R.min(), t.R.max(), len(t)))
        p = f[(f.baseline_pair == self._ref_pair()) & (f.metric == "auc")
              & (f.threshold.isna())]
        rows.append(("population", p.R.min(), p.R.max(), len(p)))
        out = pd.DataFrame(rows, columns=["axis", "lo", "hi", "cells"])
        out["spread"] = out.hi - out.lo
        return out

    def _ref_pair(self):
        names = list(self.baselines)
        return f"{names[0]} -> {names[-1]}" if len(names) > 1 else names[0]

    # -- the reportable form --------------------------------------------
    def report(self, stream=None):
        import sys
        out = stream or sys.stdout
        w = out.write
        w("=" * 78 + "\n")
        w(f"INCREMENTAL VALUE OF {self.feature!r}, AS A SURFACE\n")
        w("=" * 78 + "\n")
        w(f"  train {self.n_train:,} rows   test {self.n_test:,} rows   "
          f"prevalence {self.prevalence:.4f}\n")
        w(f"  baselines: " + ", ".join(f"{k} ({len(v)} fields)"
                                       for k, v in self.baselines.items()) + "\n")
        w(f"  metrics:   {', '.join(self.metrics)}\n")
        w(f"  operating points: {len(self.thresholds)} in "
          f"[{min(self.thresholds):.3f}, {max(self.thresholds):.3f}]\n"
          if self.thresholds else "  operating points: none requested\n")
        w(f"  population levels: {', '.join(f'{p:.2f}' for p in self.population)}\n")
        w(f"  bootstrap: {self.n_boot} draws, seed {self.seed}\n\n")
        w("  V(f | B, m) at full population\n")
        f = self.frame
        sub = f[(f.population == 1.0) & (f.threshold.isna())]
        #  every baseline appears as the low leg of some pair and, for the
        #  topmost rung, only as the high leg; take both so no rung is missing
        v = pd.concat([
            sub[["baseline", "metric", "V_lo"]].rename(columns={"V_lo": "V"}),
            sub[["baseline_hi", "metric", "V_hi"]]
            .rename(columns={"baseline_hi": "baseline", "V_hi": "V"}),
        ]).drop_duplicates(subset=["baseline", "metric"])
        v = v.pivot_table(index="baseline", columns="metric", values="V")
        w(v.to_string(float_format=lambda x: f"{x:+.4f}") + "\n\n")
        w("  R over each axis, others held at the reference cell\n")
        w(self.spread().to_string(index=False,
                                  float_format=lambda x: f"{x:+.4f}") + "\n")
        if self.notes:
            w("\n  NOTES\n")
            for n in self.notes:
                w(f"   - {n}\n")
        w("\n  This is the minimum reportable form.  A single number for the\n")
        w("  value of this field would be a choice of one cell above, and\n")
        w("  fieldvalue will not make that choice for you.\n")
        return None

    # -- the signature figure -------------------------------------------
    def plot(self, path=None, ax=None):
        """Baseline against metric, each cell coloured by R.

        Readable in greyscale and at half width; every value comes from
        `self.frame`.
        """
        import matplotlib
        if path is not None:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        f = self.frame
        g = (f[(f.population == 1.0) & (f.threshold.isna())]
             .pivot_table(index="baseline_pair", columns="metric", values="R"))
        if ax is None:
            _, ax = plt.subplots(figsize=(1.6 + 1.1 * g.shape[1],
                                          1.2 + 0.5 * g.shape[0]))
        im = ax.imshow(g.values, cmap="Greys", aspect="auto")
        ax.set_xticks(range(g.shape[1]))
        ax.set_xticklabels(g.columns, rotation=30, ha="right", fontsize=8)
        ax.set_yticks(range(g.shape[0]))
        ax.set_yticklabels(g.index, fontsize=8)
        for i in range(g.shape[0]):
            for j in range(g.shape[1]):
                val = g.values[i, j]
                if np.isfinite(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            fontsize=8,
                            color=("white" if val > np.nanmedian(g.values)
                                   else "black"))
        ax.set_title(f"R for {self.feature!r}: the same data, different cells",
                     fontsize=9)
        ax.figure.colorbar(im, ax=ax, label="admissibility reduction R")
        ax.figure.tight_layout()
        if path:
            ax.figure.savefig(path, dpi=200)
        return ax


def surface(X, y, feature, baselines, metrics=DEFAULT_METRICS,
            thresholds=DEFAULT_THRESHOLDS, population=DEFAULT_POPULATION,
            regimes=("rare-first",), n_boot=0, seed=20260819,
            train_frac=0.70, order=None):
    """Compute the four-axis surface for `feature`.

    X            a DataFrame of categorical columns
    y            the binary target, array-like or a column name in X
    feature      the column whose incremental value is being claimed
    baselines    {name: [columns]}, given LOWEST FIRST.  R is computed for
                 every ordered pair, so a two-entry dict gives one reduction
                 and a four-entry dict gives six.
    metrics      names from fieldvalue.metrics.METRICS
    thresholds   operating points for net benefit; the third axis
    population   register population levels; the fourth axis
    regimes      how the register empties: 'rare-first', 'random',
                 'common-first'
    n_boot       paired bootstrap draws for R at the reference cell (0 = none)
    order        optional column name to sort by before the split; use the
                 timestamp, because a random split on a process log leaks the
                 future.  Without it the existing row order is the order.
    """
    X = pd.DataFrame(X).copy()
    if isinstance(y, str):
        ycol, y = y, X[y].values
        X = X.drop(columns=[ycol])
    y = np.asarray(y).astype(int)
    if len(y) != len(X):
        raise ValueError("X and y differ in length")
    if feature not in X.columns:
        raise KeyError(f"{feature!r} is not a column of X")
    if not baselines:
        raise ValueError("at least one baseline is required")
    for nm, cols in baselines.items():
        missing = [c for c in cols if c not in X.columns]
        if missing:
            raise KeyError(f"baseline {nm!r} names missing columns {missing}")
        if feature in cols:
            raise ValueError(f"baseline {nm!r} already contains {feature!r}; "
                             "a feature cannot be incremental over itself")
    notes = []
    if order is not None:
        X = X.assign(_y=y).sort_values(order, kind="stable")
        y = X.pop("_y").values
        X = X.drop(columns=[order])
    else:
        notes.append("No `order` column was given, so the split follows the "
                     "existing row order.  On a process log that must be the "
                     "timestamp: a random split leaks the future.")
        X = X.assign(_y=y)
        y = X.pop("_y").values

    cut = int(len(X) * train_frac)
    names = list(baselines)
    rng_master = np.random.default_rng(seed)
    rows = []
    prev_tr = float(y[:cut].mean())
    for level in population:
        for regime in (regimes if level < 1.0 else ("full",)):
            d = X.copy()
            d["_y"] = y
            d["_f"] = _mask(d[feature], level, regime,
                            np.random.default_rng(seed))
            tr, te = d.iloc[:cut], d.iloc[cut:]
            yte = te["_y"].values
            if len(np.unique(yte)) < 2:
                notes.append(f"population {level} regime {regime}: the test "
                             "half has one class; skipped")
                continue
            P = {}
            for nm in names:
                cols = list(baselines[nm]) or ["_const"]
                if not baselines[nm]:
                    tr, te = tr.assign(_const="c"), te.assign(_const="c")
                P[(nm, 0)] = _fit_predict(tr, te, cols, "_y", seed)
                P[(nm, 1)] = _fit_predict(tr, te, list(cols) + ["_f"], "_y",
                                          seed)
            for nm in names:
                for m in metrics:
                    fn = METRICS[m]
                    v = fn(P[(nm, 1)], yte, prev_tr) - fn(P[(nm, 0)], yte,
                                                          prev_tr)
                    rows.append(dict(baseline=nm, metric=m, threshold=np.nan,
                                     population=level, regime=regime,
                                     populated=float((d["_f"] != EMPTY).mean()),
                                     V=v))
                for t in thresholds:
                    v = (net_benefit(P[(nm, 1)], yte, t)
                         - net_benefit(P[(nm, 0)], yte, t))
                    rows.append(dict(baseline=nm, metric="net_benefit",
                                     threshold=float(t), population=level,
                                     regime=regime,
                                     populated=float((d["_f"] != EMPTY).mean()),
                                     V=v))
    V = pd.DataFrame(rows)

    #  R for every ORDERED pair of baselines, lower first
    out = []
    key = ["metric", "threshold", "population", "regime"]
    for _, sub in V.groupby(key, dropna=False):
        d = {r.baseline: r.V for r in sub.itertuples()}
        head = sub.iloc[0]
        for i, j in itertools.combinations(range(len(names)), 2):
            lo_, hi_ = names[i], names[j]
            if lo_ not in d or hi_ not in d:
                continue
            R = (1.0 - d[hi_] / d[lo_]) if d[lo_] > EPS else np.nan
            out.append(dict(baseline_pair=f"{lo_} -> {hi_}", baseline=lo_,
                            baseline_hi=hi_, metric=head.metric,
                            threshold=head.threshold,
                            population=head.population, regime=head.regime,
                            populated=head.populated,
                            V_lo=d[lo_], V_hi=d[hi_], R=R))
    F = pd.DataFrame(out)
    if (F.R.isna()).any():
        notes.append(f"{int(F.R.isna().sum())} of {len(F)} cells have no "
                     "reduction because the lower baseline's increment is not "
                     "positive there.  A ratio whose denominator crosses zero "
                     "is not a quantity and is left blank rather than printed.")
    return Surface(frame=F, feature=feature, baselines=baselines,
                   metrics=tuple(metrics), thresholds=tuple(thresholds),
                   population=tuple(population), n_boot=n_boot, seed=seed,
                   n_train=cut, n_test=len(X) - cut,
                   prevalence=float(y[cut:].mean()), notes=notes)

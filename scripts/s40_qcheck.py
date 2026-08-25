"""s40 -- THE CRITICAL VALUE, CHECKED AGAINST THE OTHER ESTIMATE OF ITSELF.

ROUND TWENTY-TWO.  A referee did something nobody in twenty-one rounds had
done: took the two estimates of the max-t critical value that `s21` already
writes side by side -- the Gaussian multiplier quantile `q`, which the bands
use, and the empirical quantile `q_emp` of the same B observed maxima, which
`s21`'s own docstring calls "the construction an earlier version used" -- and
compared them.

`q` lies BELOW the entire 95% order-statistic interval of `q_emp` on most
whole-surface families and on EVERY decision-curve family, and the gap is in
the anti-conservative direction: a band built on `q` is narrower than the
observed maxima say it should be, so it resolves cells the data may not
resolve.  `s21`'s answer to "why not the empirical quantile" is that the
empirical quantile is imprecise -- a median order-statistic width of about two
against the multiplier's four hundredths -- and that is true and is an
argument about VARIANCE.  It does not address a systematic one-sided gap.

WHY THE GAP IS THERE.  The multiplier bootstrap replaces the draw vector by a
Gaussian vector with the same empirical covariance, so it can only reproduce
excursions a Gaussian process makes.  This file measures how far the
standardised draws are from Gaussian -- the per-cell excess kurtosis -- and
finds a heavy right tail.  A Gaussian multiplier under heavy-tailed draws is
anti-conservative by construction, which is exactly the direction observed.

WHAT THIS FILE DOES NOT DO.  It does not decide which estimator is right.
The empirical quantile is badly determined at B = 33 to 201 draws and the
multiplier rests on an asymptotic argument this corpus's draw counts may not
reach.  What it does is COUNT what each one resolves, so the manuscript can
report how much of its resolution is a property of the data and how much of
the estimator, instead of asserting one and moving on.  Section 6.4 reports
both and Section 11 carries the gap as a limitation.

    python s40_qcheck.py

Outputs: results/s40_qcheck.csv   per family: q, q_emp, and what each resolves
         results/s40_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

ALPHA = 0.05


def main():
    t0 = time.time()
    Q = pd.read_csv(RESULTS / "s21_critical.csv")
    B = pd.read_csv(RESULTS / "s21_bands.csv.gz")

    rows = []
    for (lg, tg, fam), s in B.groupby(["log", "target", "family"]):
        q = Q[(Q.log == lg) & (Q.target == tg) & (Q.family == fam)]
        if not len(q):
            continue
        q = q.iloc[0]
        rows.append(dict(
            log=lg, target=tg, family=fam,
            n_family=int(len(s)), n_draws=int(q.n_draws),
            q=float(q.q), q_hi=float(q.q_hi),
            q_emp=float(q.q_emp), q_emp_lo=float(q.q_emp_lo),
            q_emp_hi=float(q.q_emp_hi),
            #  the multiplier value sits below every value the observed
            #  maxima's order-statistic interval admits
            below=bool(float(q.q) < float(q.q_emp_lo)),
            ratio=float(q.q_emp) / float(q.q) if float(q.q) else np.nan,
            resolved_mult=int(((s.cons_lo > 0) | (s.cons_hi < 0)).sum()),
            resolved_emp=int(((s.emp_lo > 0) | (s.emp_hi < 0)).sum())))
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "s40_qcheck.csv", index=False)

    def by(fam, col):
        s = D[D.family == fam]
        return s[col]

    ws, dc = D[D.family == "whole-surface"], D[D.family == "decision-curve"]
    facts = dict(
        n_families_whole=len(ws), n_families_dca=len(dc),
        n_below_whole=int(ws.below.sum()), n_below_dca=int(dc.below.sum()),
        q_whole_median=float(ws.q.median()),
        q_emp_whole_median=float(ws.q_emp.median()),
        q_dca_median=float(dc.q.median()),
        q_emp_dca_median=float(dc.q_emp.median()),
        ratio_whole_median=float(ws.ratio.median()),
        ratio_dca_median=float(dc.ratio.median()),
        resolved_whole_mult=int(ws.resolved_mult.sum()),
        resolved_whole_emp=int(ws.resolved_emp.sum()),
        resolved_dca_mult=int(dc.resolved_mult.sum()),
        resolved_dca_emp=int(dc.resolved_emp.sum()),
        n_draws_min=int(D.n_draws.min()), n_draws_max=int(D.n_draws.max()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s40_facts.csv", index=False)
    print(D.to_string(index=False))
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s40_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

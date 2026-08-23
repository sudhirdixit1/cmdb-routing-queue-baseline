"""s11 -- THE PACKAGE AGAINST THE PIPELINE.

The analysis scripts and the `fieldvalue` package implement the same four
objects twice, from the same definitions, in different code.  Neither was
written against the other: `scripts/s03_decompose.py` and
`scripts/s04_regret.py` compute the decomposition, the regions, the robustness
index and the regret over the whole corpus in one pass, and
`fieldvalue.report` computes them from a tidy frame with no knowledge of this
corpus at all.

This file runs both on the same input and prints every disagreement.  It is
the reason the manuscript can say the package is an independent
implementation: twice in this project's history the two have disagreed, and
both times the paper was wrong and the package was right.

    python s11_tool_agreement.py

Outputs: results/s11_agreement.csv, s11_facts.csv
Exit status is non-zero if any quantity disagrees beyond the stated tolerance.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

import fieldvalue as FV  # noqa: E402

TOL = 1e-12
ROWS = []


def cmp(name, a, b, tol=TOL):
    ok = (a is None and b is None) or (
        np.isfinite(a) and np.isfinite(b) and abs(a - b) <= tol)
    ROWS.append(dict(quantity=name, pipeline=a, package=b,
                     difference=(abs(a - b) if np.isfinite(a)
                                 and np.isfinite(b) else np.nan),
                     agrees=bool(ok), tolerance=tol))
    return ok


def main():
    t0 = time.time()
    SUR = S.read_results("s01_surface.csv")
    print("=" * 92)
    print("s11  fieldvalue AGAINST THE ANALYSIS PIPELINE")
    print("=" * 92)

    #  ---- the decomposition ----------------------------------------------
    SOB = S.read_results("s03_sobol.csv")
    checked = 0
    for (log, target), sub in SUR.groupby(["log", "target"]):
        d = sub[(~sub.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (sub.metric.isin(list(S.SCALARS)))].copy()
        if len(d) < 16:
            continue
        d["quality_level"] = (d.quality.astype(str) + "@"
                              + d.level.map(lambda x: "%.2f" % x))
        d["headroom"] = d.V / (1.0 - d.without_f)
        pkg = FV.decompose(d, value="headroom",
                           axes=("learner", "split", "quality_level", "rung",
                                 "metric")).set_index("axis")
        pipe = SOB[(SOB.log == log) & (SOB.target == target)
                   & (SOB.scale == "headroom")].set_index("axis")
        for ax in pkg.index:
            if ax in pipe.index:
                cmp("S[%s/%s/%s]" % (log, target, ax),
                    float(pipe.loc[ax, "S"]), float(pkg.loc[ax, "S"]))
                cmp("S_total[%s/%s/%s]" % (log, target, ax),
                    float(pipe.loc[ax, "S_total"]),
                    float(pkg.loc[ax, "S_total"]))
                checked += 2

    #  ---- the regret ------------------------------------------------------
    RG = S.read_results("s04_regret.csv")
    for (log, target), sub in SUR.groupby(["log", "target"]):
        d = sub[(~sub.rung.isin(S.IMPLAUSIBLE_RUNGS))
                & (sub.metric.isin(list(S.SCALARS)))]
        if len(d) < 8:
            continue
        pkg = FV.regret(d, value="V")
        pipe = RG[(RG.log == log) & (RG.target == target)]
        if not len(pipe):
            continue
        cmp("misreport_mean[%s/%s]" % (log, target),
            float(pipe.misreport.mean()), float(pkg.misreport.mean()))
        cmp("regret_mean[%s/%s]" % (log, target),
            float(pipe.regret.mean()), float(pkg.regret.mean()))

    #  ---- the regions -----------------------------------------------------
    bands = RESULTS / "s02_bands.csv"
    regions = RESULTS / "s03_regions.csv"
    if bands.exists() and regions.exists():
        BN = pd.read_csv(bands)
        RE = pd.read_csv(regions)
        if len(BN) and len(RE):
            BN = BN.rename(columns={"sim_lo": "lo", "sim_hi": "hi"})
            for (log, target), sub in BN.groupby(["log", "target"]):
                pkg = FV.robustness(sub, value="V", lo="lo", hi="hi",
                                    exclude=S.IMPLAUSIBLE_RUNGS)
                pipe = RE[(RE.log == log) & (RE.target == target)]
                if not len(pipe):
                    continue
                cmp("rho[%s/%s]" % (log, target), float(pipe.rho.iloc[0]),
                    float(pkg.rho.iloc[0]))
                ROWS.append(dict(
                    quantity="region[%s/%s]" % (log, target),
                    pipeline=pipe.region.iloc[0], package=pkg.region.iloc[0],
                    difference=np.nan,
                    agrees=bool(pipe.region.iloc[0] == pkg.region.iloc[0]),
                    tolerance=np.nan))
    else:
        print("  (regions skipped: s02_bands.csv or s03_regions.csv missing)")

    A = pd.DataFrame(ROWS)
    A.to_csv(RESULTS / "s11_agreement.csv", index=False)
    bad = A[~A.agrees]
    print("  %d quantities compared, %d disagree" % (len(A), len(bad)))
    if len(bad):
        print(bad.to_string(index=False)[:3000])
    worst = float(A.difference.max()) if A.difference.notna().any() else 0.0
    print("  largest numeric difference: %.3g" % worst)
    pd.DataFrame([dict(n_quantities=len(A), n_disagree=len(bad),
                       max_difference=worst, tolerance=TOL,
                       runtime_s=round(time.time() - t0, 1))]).to_csv(
        RESULTS / "s11_facts.csv", index=False)
    sys.exit(1 if len(bad) else 0)


if __name__ == "__main__":
    main()

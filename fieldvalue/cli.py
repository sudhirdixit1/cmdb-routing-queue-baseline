"""fieldvalue's command line.

    python -m fieldvalue --data incidents.csv --target reassigned \
        --feature ci_name --baseline intake:category,impact,urgency \
        --baseline "intake+group:category,impact,urgency,group" \
        --order opened_at --out surface.csv --figure surface.png

Every argument that fixes one of the four axes is named on the command line,
because a tool that defaulted them silently would be the practice this
package exists to argue against.  `--baseline` may be given more than once and
is ordered LOWEST FIRST; with fewer than two the tool computes V and says why
it cannot compute R.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

from .core import (DEFAULT_METRICS, DEFAULT_POPULATION, SingleNumberRefused,
                   surface)


def _parse_baseline(spec):
    if ":" not in spec:
        raise argparse.ArgumentTypeError(
            f"--baseline must be NAME:col1,col2 (got {spec!r})")
    name, cols = spec.split(":", 1)
    return name.strip(), [c.strip() for c in cols.split(",") if c.strip()]


def build_parser():
    p = argparse.ArgumentParser(
        prog="python -m fieldvalue",
        description="Report a recorded field's incremental value as a surface.")
    p.add_argument("--data", required=True, help="CSV of categorical columns")
    p.add_argument("--target", required=True, help="binary outcome column")
    p.add_argument("--feature", required=True, help="the field being valued")
    p.add_argument("--baseline", action="append", required=True,
                   type=_parse_baseline, metavar="NAME:c1,c2",
                   help="repeatable, lowest first")
    p.add_argument("--metrics", default=",".join(DEFAULT_METRICS))
    p.add_argument("--thresholds", default="0.05:0.80:0.025",
                   help="lo:hi:step, or 'none'")
    p.add_argument("--population", default=",".join(
        f"{x:g}" for x in DEFAULT_POPULATION))
    p.add_argument("--regime", default="rare-first",
                   choices=["rare-first", "random", "common-first"])
    p.add_argument("--order", default=None,
                   help="column to sort by before the split; use the timestamp")
    p.add_argument("--seed", type=int, default=20260819)
    p.add_argument("--out", default=None, help="write the surface as CSV")
    p.add_argument("--figure", default=None, help="write the signature figure")
    p.add_argument("--headline", action="store_true",
                   help="ask for one number; the tool will refuse and say why")
    return p


def main(argv=None):
    a = build_parser().parse_args(argv)
    df = pd.read_csv(a.data, low_memory=False)
    if a.target not in df.columns:
        sys.exit(f"--target {a.target!r} is not a column of {a.data}")
    if a.thresholds.lower() == "none":
        th = ()
    else:
        lo, hi, st = (float(x) for x in a.thresholds.split(":"))
        th = tuple(np.round(np.arange(lo, hi + 1e-9, st), 6))
    s = surface(df.drop(columns=[a.target]), df[a.target].values,
                feature=a.feature, baselines=dict(a.baseline),
                metrics=[m.strip() for m in a.metrics.split(",") if m.strip()],
                thresholds=th,
                population=[float(x) for x in a.population.split(",")],
                regimes=(a.regime,), seed=a.seed, order=a.order)
    s.report()
    if a.out:
        s.to_frame().to_csv(a.out, index=False)
        print(f"\n  surface written to {a.out}")
    if a.figure:
        s.plot(path=a.figure)
        print(f"  figure written to {a.figure}")
    if a.headline:
        try:
            float(s)
        except SingleNumberRefused as e:
            print("\n" + "=" * 78)
            print(e)
            return 2
    return 0

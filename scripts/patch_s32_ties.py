"""Add the tied-timestamp count to s32's facts file.

s32 printed the count and never stored it, so `nTiedTimestamps` was
unresolved.  Rather than re-run forty minutes of bootstrap for one integer,
this recomputes the frame -- which is deterministic and cheap -- and writes
the column.  The next full run of s32 writes it directly and this file becomes
a no-op; it is kept so that the archived results and the source agree about
where the number came from.

    python patch_s32_ties.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402
import s32_cohort as S32  # noqa: E402


def main():
    d = S32.base_frame()
    p = RESULTS / "s32_facts.csv"
    F = pd.read_csv(p)
    F["n_ties"] = int(d.attrs["n_ties"])
    cols = list(F.columns)
    cols.insert(cols.index("n_extra") + 1, cols.pop(cols.index("n_ties")))
    F[cols].to_csv(p, index=False)
    print("n_ties =", int(d.attrs["n_ties"]))


if __name__ == "__main__":
    main()

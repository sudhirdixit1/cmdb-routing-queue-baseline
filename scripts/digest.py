"""Print every *_facts.csv in results/ as a flat name = value list.

Not part of the pipeline.  It exists so that a number written into the
manuscript can be copied from a result file rather than remembered, which is
how three of this project's corrections got in.

    python scripts/digest.py            # everything
    python scripts/digest.py r30 r35    # only those prefixes
"""
import sys
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parent.parent / "results"


def main(argv):
    want = [a for a in argv if not a.startswith("-")]
    for p in sorted(R.glob("*_facts.csv")):
        if want and not any(p.name.startswith(w) for w in want):
            continue
        try:
            d = pd.read_csv(p)
        except Exception as e:                              # noqa: BLE001
            print(f"# {p.name}: {e}")
            continue
        if len(d) != 1:
            print(f"\n### {p.name}  ({len(d)} rows)")
            print(d.to_string(index=False))
            continue
        print(f"\n### {p.name}")
        for k, v in d.iloc[0].items():
            if isinstance(v, float):
                print(f"  {k:34s} {v:.6g}")
            else:
                print(f"  {k:34s} {v}")


if __name__ == "__main__":
    main(sys.argv[1:])

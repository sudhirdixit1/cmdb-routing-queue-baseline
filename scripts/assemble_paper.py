"""assemble_paper -- concatenate paper/parts/*.tex into the submission file.

The manuscript is written in parts so that a section can be edited without
rewriting the whole file, and is SHIPPED as one .tex because that is what a
submission system wants.  This script does the concatenation, in a declared
order, and refuses to run if a part named in the order is missing.

    python assemble_paper.py            # writes paper/specification_surfaces.tex
    python assemble_paper.py --check    # verify the assembled file is current
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "paper" / "parts"
OUT = ROOT / "paper" / "specification_surfaces.tex"

ORDER = [
    "00_front_intro_related.tex",
    "10_surface.tex",
    "20_inference.tex",
    "30_design.tex",
    "40_multilog.tex",
    "50_cmdb.tex",
    "60_dca.tex",
    "70_standard.tex",
    "80_limits.tex",
    "90_backmatter.tex",
]


def build():
    missing = [p for p in ORDER if not (PARTS / p).exists()]
    if missing:
        sys.exit("missing parts: %s" % ", ".join(missing))
    chunks = []
    for p in ORDER:
        chunks.append("%% ---- paper/parts/%s ----\n" % p)
        chunks.append((PARTS / p).read_text(encoding="utf-8"))
    return "".join(chunks)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    text = build()
    if a.check:
        cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur != text:
            sys.exit("paper/specification_surfaces.tex is stale; "
                     "run scripts/assemble_paper.py")
        print("assembled manuscript is current")
        return
    OUT.write_text(text, encoding="utf-8")
    words = len(text.split())
    print("wrote %s (%d parts, ~%d tokens of source)" % (OUT.name, len(ORDER),
                                                         words))


if __name__ == "__main__":
    main()

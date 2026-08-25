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
OUT_SUPP = ROOT / "paper" / "supplement.tex"

ORDER = [
    "00_front_intro_related.tex",
    "10_surface.tex",
    "20_inference.tex",
    "30_design.tex",
    "40_multilog.tex",
    "50_cmdb.tex",
    "60_dca.tex",
    "70_standard.tex",
    "75_simulation.tex",
    "80_limits.tex",
    "90_backmatter.tex",
]

#  ROUND TWENTY-ONE.  The review's twelfth comment: the article is
#  ninety-seven pages and nobody finishes it.  The appendices are now a
#  SEPARATE DOCUMENT with its own numbering, built from the same parts and
#  the same generated macros.  Cross-references between the two resolve
#  through `xr', which is why build_journal.py runs both twice.
ORDER_SUPP = [
    "S0_supplement_front.tex",
    "S9_supplement_back.tex",
]

DOCS = {OUT: ORDER, OUT_SUPP: ORDER_SUPP}


def build(order):
    missing = [p for p in order if not (PARTS / p).exists()]
    if missing:
        sys.exit("missing parts: %s" % ", ".join(missing))
    chunks = []
    for p in order:
        chunks.append("%% ---- paper/parts/%s ----\n" % p)
        chunks.append((PARTS / p).read_text(encoding="utf-8"))
    return "".join(chunks)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    for out, order in DOCS.items():
        text = build(order)
        if a.check:
            cur = out.read_text(encoding="utf-8") if out.exists() else ""
            if cur != text:
                sys.exit("paper/%s is stale; run scripts/assemble_paper.py"
                         % out.name)
            print("assembled %s is current" % out.name)
            continue
        out.write_text(text, encoding="utf-8")
        print("wrote %s (%d parts, ~%d tokens of source)"
              % (out.name, len(order), len(text.split())))


if __name__ == "__main__":
    main()

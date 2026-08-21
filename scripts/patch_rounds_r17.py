"""Remove "this round" from the manuscript where it no longer means what it
used to, and where a reader could not know what it means at all.

The phrase accumulated across seventeen rounds and now points at three
different rounds in one document: §5's "until this round" is round fifteen's
correction, §9's "the second of this round's two corrections" is round
sixteen's, and §15's "two of the three found this round" is round
seventeen's. A published paper has no rounds; a correction has a number.

    python scripts/patch_rounds_r17.py --check
    python scripts/patch_rounds_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

EDITS = [
    ("secondorg",
     "Until this round we described this study as single-organisation of necessity,",
     "An earlier version described this study as single-organisation of necessity,"),
    ("capacity-withdrawal",
     """That framing is withdrawn here, and the reason is the second of this round's
two corrections.""",
     """That framing is withdrawn here, and the reason is correction seven in
Section~\\ref{sec:corrections}."""),
    ("correction-seven",
     """four gave that factor an interval; this round asked what it measured.""",
     """four gave that factor an interval; this one asked what it measured."""),
    ("corrections-lead",
     """Two of the three found this round are worth separating out, because they are a
kind the apparatus was built to catch and could not.""",
     """Two of the three most recent are worth separating out, because they are a
kind the apparatus was built to catch and could not."""),
    ("plan-round",
     """We attempted the prediction the plan for this round asked for: regress the""",
     """We attempted the prediction we set ourselves in advance: regress the"""),
]


def main(argv):
    s = TEX.read_text(encoding="utf-8")
    missing = [f"{n}: anchor appears {s.count(o)} times"
               for n, o, _ in EDITS if s.count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for n, o, w in EDITS:
        s = s.replace(o, w, 1)
        print(f"  applied {n}")
    TEX.write_text(s, encoding="utf-8")
    print(f"wrote {TEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

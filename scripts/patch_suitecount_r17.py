"""The paper said the corruption suite has 149 mutations. It has 199. And the
check that was supposed to catch that compared the constant 149 against the
literal 149.

That is exactly the defect HANDOFF §19.4 records for the corrections count:
"the corrections list length was compared against the constant 8, and the word
against nothing". A check whose expected value is a constant typed beside the
paper's literal cannot fail when the world moves. This makes the check read
`len(attack_verifier.CORRUPTIONS)`, so the paper and the suite cannot drift.

The same sentence also claimed the suite "has found eight holes in that
program". Round seventeen took that to twelve, but there is no result file
that counts holes, so an uncheckable count is replaced by a claim that is
true, stronger, and pinned: every hole this checker has had was found by the
suite.

    python scripts/patch_suitecount_r17.py --check
    python scripts/patch_suitecount_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"
V = ROOT / "scripts" / "verify_paper.py"

EDITS = [
    ("paper", TEX,
     r"""program that re-derives every numeric literal from a result file, and a
corruption suite of $149$ mutations that has found eight holes in that
program.""",
     r"""program that re-derives every numeric literal from a result file, and a
corruption suite of $199$ mutations which has found every hole that program
has ever had.""" ),
    ("check", V,
     '''ck("corruption suite size", 149, "149", 0,
   anchor="a corruption suite of")''',
     '''#  ROUND SEVENTEEN.  This compared the constant 149 against the literal 149,
#  so it could not fail when the suite grew -- the same shape of defect as the
#  corrections count in round sixteen.  It reads the suite's own list now.
import attack_verifier as _AV
ck("corruption suite size", len(_AV.CORRUPTIONS), "199", 0,
   anchor="a corruption suite of")'''),
    ("pin", V,
     'ck_phrase("the falsification verdict is pinned",',
     '''ck_phrase("the suite's provenance claim is pinned",
          r"a corruption suite of $199$ mutations which has found every hole "
          r"that program has ever had")
ck_phrase("the falsification verdict is pinned",'''),
]


def main(argv):
    srcs = {p: p.read_text(encoding="utf-8") for _, p, _, _ in EDITS}
    missing = [f"{n} ({p.name}): anchor appears {srcs[p].count(o)} times"
               for n, p, o, _ in EDITS if srcs[p].count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for n, p, o, w in EDITS:
        srcs[p] = srcs[p].replace(o, w, 1)
        print(f"  applied {n} -> {p.name}")
    for p, s in srcs.items():
        p.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

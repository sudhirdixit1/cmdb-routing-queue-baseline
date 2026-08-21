"""Close the prose holes the round-seventeen corruption suite found.

The enlarged suite landed three corruptions on its first run and all three
are prose, not arithmetic:

  * "It is falsified" softened to "It is largely supported";
  * "the headline does not survive our own admissibility criterion"
    reversed to "the headline survives";
  * the two ends of a three-way population comparison swapped, where both
    values stay checked and only their attribution moves.

The first two are directional constructions the guard list did not contain.
The third is the ordered-pair hole `ck_phrase` exists for, on a triple this
round added and did not pin.

Nothing here weakens a check.  RISKY grows, which makes MORE sentences
require a pin, and three sentences get verbatim pins.

    python scripts/patch_guards_r17.py --check
    python scripts/patch_guards_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "scripts" / "verify_paper.py"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ---------------------------------------------------- the guard list grows
edit("risky", '''    "we withdraw", "not error", "not as a recoverable",
)''',
     '''    "we withdraw", "not error", "not as a recoverable",
    #  ROUND SEVENTEEN.  Every one of these carried a corruption the suite
    #  landed, or is the same construction as one that did.  A list is not a
    #  theory: these were added one defect at a time and nothing on the list
    #  was foreseen before the corruption that put it there.
    "falsified", "does not survive", "resolvably harmful",
    "cannot be tested", "is not proved", "the gap widens",
    "nothing to reduce", "not resolvably", "removes the headline",
)''')

# ------------------------------------------------------- the three pins
edit("pins", '''ck_phrase("no ratio is quoted across a zero denominator",''',
     '''#  ROUND SEVENTEEN, three corruptions that landed on the suite's first run.
#  Each is now pinned verbatim; the numbers inside each are separately
#  checked above, because ck_phrase pins POSITION and not value.
ck_phrase("the falsification verdict is pinned",
          r"It is falsified. We report that rather than reframing the claim "
          r"to fit")
ck_phrase("the abstract's non-survival is pinned",
          r"the headline does not survive our own admissibility criterion "
          r"once the evidence to apply it is in hand")
ck_phrase("the population regimes are pinned to their values",
          r"the group-aware increment is $+0.082$ when the long tail is "
          r"missing, $+0.067$ at random, and $+0.064$ when the core is")
ck_phrase("the harmful band is pinned",
          r"the item is resolvably harmful in a band above the base rate")
ck_phrase("the free-text negative is pinned",
          r"Of $596$ attributes, zero satisfy it")
ck_phrase("the corpus precondition is pinned",
          r"the entity is not resolvably worth anything over the intake "
          r"block at all, so there is nothing for a free field to absorb")
ck_phrase("the tie-convention direction is pinned",
          r"The gap widens rather than closes, which is the outcome we did "
          r"not expect and report because we did not")
ck_phrase("the null verdict is pinned",
          r"The real field reaches $0.8041$ and leaves it worth $+0.001$")

ck_phrase("no ratio is quoted across a zero denominator",''')


def main(argv):
    src = V.read_text(encoding="utf-8")
    check = "--check" in argv
    missing = [f"{name}: anchor appears {src.count(old)} times"
               for name, old, _new in EDITS if src.count(old) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if check:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for name, old, new in EDITS:
        src = src.replace(old, new, 1)
        print(f"  applied {name}")
    V.write_text(src, encoding="utf-8")
    print(f"wrote {V}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

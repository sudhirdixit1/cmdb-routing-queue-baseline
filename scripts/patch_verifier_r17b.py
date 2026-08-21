"""Round seventeen's edits to verify_paper.py, part 2: the corrections list,
the title test, the guard list, and the round-seventeen check block.

    python scripts/patch_verifier_r17b.py --check
    python scripts/patch_verifier_r17b.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "scripts" / "verify_paper.py"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ------------------------------------------------- the three new corrections
edit("correction-anchors", '''    "8 (a control run on one of two rungs)":
        r"the correction moves the boosting reduction by $3.4$ percentage "
        r"points, and upward",
}''',
     '''    "8 (a control run on one of two rungs)":
        r"the correction moves the boosting reduction by $3.4$ percentage "
        r"points, and upward",
    #  ROUND SEVENTEEN.  Nine and ten are the first two corrections in this
    #  project's history in which every literal was right and the sentence
    #  was wrong, so each is pinned on the WORD that made it wrong --
    #  "reaching", which names an extremum, and the identification of a
    #  count with an interval.
    "9 (an extremum that was the worst named point)":
        r"The word \\emph{reaching} names an extremum",
    "10 (a count and a run reported as one set)":
        r"Counting a set and describing an interval are different operations",
    "11 (an open question left open with the evidence one download away)":
        r"named the file that would settle where the field comes from, and "
        r"did not obtain it",
}''')

# ------------------------------------------------------------- the title
edit("title-subject", '''    if "Configuration Data" not in _title_txt:
        bad.append(f"title no longer names the paper's subject: {_title_txt!r}")
    else:
        ok += 1
    #  ... and it must not promise attributes, which is the thing the paper
    #  spends section 5 showing the data does NOT supply.
    if "Attributes" not in _title_txt:
        bad.append(f"title drops the claim section 5 makes: {_title_txt!r}")
    else:
        ok += 1''',
     '''    #  ROUND SEVENTEEN.  The lead contribution moved again, from which layer
    #  of configuration data pays -- a finding section 9 shows does not
    #  replicate outside the primary log -- to the estimand itself.  The
    #  title must name that subject.
    if "Incremental Value" not in _title_txt:
        bad.append(f"title no longer names the paper's subject: {_title_txt!r}")
    else:
        ok += 1
    #  ... and it must not still assert the demoted lead.  "Identity, Not
    #  Attributes" is a claim the corpus does not support and the title may
    #  not carry it.
    if "Identity, Not Attributes" in _title_txt:
        bad.append(f"title asserts the demoted lead: {_title_txt!r}")
    else:
        ok += 1''')

# ------------------------------------------------------------ the guard list
edit("unguarded-ok", '''    "If the group is independent, a CMDB is worth half":
        "the first horn of the ambiguity; the second horn carries the "
        "'lower bound' claim and IS pinned",
}''',
     '''    "If the group is independent, a CMDB is worth half":
        "the first horn of the ambiguity; the second horn carries the "
        "'lower bound' claim and IS pinned",
    #  ROUND SEVENTEEN.  This sentence RETRACTS an upper-bound claim rather
    #  than making one; the measurement that replaces it is section 10's
    #  population curve, every point of which is checked.
    "The usual caveat":
        "a retraction of the upper-bound caveat, not an assertion of one; "
        "the curve that replaces it is checked point by point",
}''')

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

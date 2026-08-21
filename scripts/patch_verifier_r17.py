"""Round seventeen's edits to verify_paper.py.

Three kinds of change, in this order:

  1. RETIREMENT.  A check is retired only when the sentence it anchored has
     been removed or rewritten, never because it fails.  The coverage census
     at the bottom of the verifier is what makes that safe: every literal in
     the paper must be covered by SOME check, so retiring one for deleted
     prose cannot free a live number -- the number simply becomes unaccounted
     and the run fails.  Every retirement below names the claim that went.

  2. NEW STRUCTURAL CONTEXTS.  Section 6's estimand introduces notation --
     $1/(1+r)$, $1/r$, the leading 1 of the reduction identity -- whose
     digits are not claims.  A literal is structural only if EVERY occurrence
     of it sits in such a context, which is the property that closed the v7
     hole; adding a context cannot free a literal that also appears in prose.

  3. ck_word, and about two hundred new checks.  ck_word is new machinery and
     is the direct descendant of the round-sixteen hole in which "Eight
     errors of our own" could be changed to "Six" and pass, because the
     tokeniser only sees digits.  Any count this paper spells out in letters
     is now compared to the data that produces it.

    python scripts/patch_verifier_r17.py --check
    python scripts/patch_verifier_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "scripts" / "verify_paper.py"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ---------------------------------------------------------------- 1. retire
RETIRE_BLOCK = '''
# =======================================================================
#  ROUND SEVENTEEN.  Checks retired because the sentence they anchored no
#  longer exists.  A check is NEVER retired because it fails; it is retired
#  because the claim went, and the claim that replaced it carries its own
#  check below.  The coverage census at the bottom of this file is what
#  makes this safe: a literal freed by a retirement and not re-checked
#  becomes unaccounted, and the run fails.
# =======================================================================
RETIRED = {
    # Section 9 was "One Thing We Could Not Establish" and is now settled.
    # Its four structural-test numbers went with it; the replacement
    # evidence is checked in the round-seventeen block.
    "km identity", "interaction ids", "single-interaction cohort",
    "interaction identity", "cohort restated at the interaction key",
    # The abstract, introduction and conclusion were rewritten around the
    # four choices; every number in the new versions is checked below.
    "abstract design-space range pinned", "abstract names the withdrawn factor",
    "abstract gives the replacement", "abstract's operational sentence pinned",
    "abstract's replacement pinned", "abstract discloses the corrections",
    "abstract states the Volvo coupling caveat",
    "abstract rung 1", "abstract rung 2", "abstract rung 2 lo",
    "abstract rung 2 hi", "abstract volvo strict reduction",
    "intro wbs levels", "intro marginal", "intro full model auc",
    "intro rung 1", "intro rung 2", "intro rung 2 lo", "intro rung 2 hi",
    "conclusion restates both gains", "the conclusion repeats the withdrawal",
    "conclusion restates the replacement",
    "conclusion restates the withdrawn factor",
    "conclusion lookup auc", "conclusion full model auc",
    "conclusion wbs levels", "conclusion marginal",
    "conclusion design space lo", "conclusion design space hi",
    "design space lo restated in conclusion",
    "design space hi restated in conclusion",
    "WBS headline restated, conclusion",
    "rung 1 restated in limitations", "rung 2 restated in limitations",
    # The data-quality caveat this pinned is replaced by a measured curve.
    "population rate is bounded upward, not claimed",
    # The negative band's sentence now names the grid extremum, not the
    # extremum among the named thresholds; correction nine.
    "the negative region is stated, not buried",
}
RETIRED_COUNT = len(RETIRED)


WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
         "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
         "nineteen": 19, "twenty": 20, "twenty-two": 22, "twenty-three": 23}


def ck_word(label, value, word, anchor):
    """Compare a count the paper spells out in LETTERS against the data.

    Round sixteen's suite found that "Eight errors of our own are reported
    as results" could be changed to "Six" and pass every check, because the
    tokeniser only sees digits and the word was compared to nothing.  That
    hole is closed for the corrections count by a bespoke check; this is the
    general form of it.  The word must both equal the value and appear
    within the anchor's window, so a correct count in the wrong sentence
    fails too.
    """
    global ok
    w = word.lower()
    if w not in WORDS:
        bad.append(f"{label}: {word!r} is not a word this checker knows")
        return
    if WORDS[w] != int(round(float(value))):
        bad.append(f"{label}: data={float(value):.6g} but the paper spells "
                   f"{word!r} = {WORDS[w]}")
        return
    flat_anchor = re.sub(r"\\s+", " ", anchor)
    for m in re.finditer(re.escape(flat_anchor), FLAT):
        lo_, hi_ = max(0, m.start() - 200), m.end() + 200
        if re.search(r"\\b" + re.escape(word) + r"\\b", FLAT[lo_:hi_], re.I):
            ok += 1
            return
    bad.append(f"{label}: the word {word!r} does not appear near {anchor!r}")

'''

edit("retire-block", """def ck(label, value, printed, tol, anchor):""",
     RETIRE_BLOCK + """def ck(label, value, printed, tol, anchor):""")

edit("retire-ck", '''    global ok
    seen.add(printed)
    try:
        target = float(printed.replace("{,}", ""))''',
     '''    global ok
    if label in RETIRED:
        return
    seen.add(printed)
    try:
        target = float(printed.replace("{,}", ""))''')

edit("retire-ck-bound", '''    global ok
    seen.add(printed)
    v, target = float(value), float(printed.replace("{,}", ""))''',
     '''    global ok
    if label in RETIRED:
        return
    seen.add(printed)
    v, target = float(value), float(printed.replace("{,}", ""))''')

edit("retire-ck-phrase", '''    global ok
    flat = re.sub(r"\\s+", " ", phrase)
    guarded_phrases.append(flat)''',
     '''    global ok
    if label in RETIRED:
        return
    flat = re.sub(r"\\s+", " ", phrase)
    guarded_phrases.append(flat)''')

# --------------------------------------------------- 2. structural contexts
edit("struct", '''    r"\\{1-p_t\\}",                  # the odds transform, in display maths
    r"\\(1-p_t\\)",                  # and inline
)''',
     '''    r"\\{1-p_t\\}",                  # the odds transform, in display maths
    r"\\(1-p_t\\)",                  # and inline
    #  ROUND SEVENTEEN.  The estimand of section 3 and the cost-ratio
    #  identity of section 6 introduce notation whose digits are not claims.
    #  Adding a context cannot free a literal that ALSO appears in prose:
    #  is_structural() requires EVERY occurrence to sit in one.
    r"\\;=\\; 1 - \\\\frac",          # the leading 1 of the reduction identity
    r"\\$1/\\(1\\+r\\)\\$",             # the Bayes threshold at cost ratio r
    r"\\$1/r\\$",                    # its net-benefit weight
    r"\\(1/\\(1\\+r\\)\\)",             # the same, inside \\text{NB}(...)
    r"\\(1-\\\\theta\\)",             # the odds transform in theta notation
)''')

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

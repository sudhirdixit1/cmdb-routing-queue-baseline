"""check_claims -- A WITHDRAWN CLAIM MAY NOT SURVIVE IN THE PACKAGE'S PROSE.

WHY THIS FILE EXISTS.  The manuscript cannot contradict itself about a number:
there is one of each, generated, and `verify_numbers` re-derives it.  The
SUBMISSION PACKAGE has no such discipline, because it is prose with typed
numbers and typed claims by design -- and in round twenty-seven the cover
letter, the document an editor reads first, said

    "every region label and every robustness index in the article is the
     calibrated one"

for as long as it took a human to read it.  The article applies no
calibration.  It derives one, measures that the widening its families need is
larger than the factor supplies, and reports NOMINAL labels while saying by
how much they are anti-conservative.  The letter asserted the negation of the
paper's central caveat, in a bullet summarising the contribution.

`texlint` guards the manuscript's prose.  `check_response_refs` validates the
package's section and table references -- which is why the letter's stale
SECTION NUMBERS were caught by a gate and its stale CLAIM was not.  This file
closes that gap for the one thing a gate can actually check: a phrase the
project has withdrawn, appearing anywhere it would be read as current.

WHAT IT IS NOT.  It cannot decide whether a sentence is true.  It checks a
DECLARED LIST of retired phrasings, each with the reason it was retired and
the round that retired it, so adding a withdrawal is one entry rather than a
memory.  A claim nobody lists is a claim nobody checks; the list is the
maintenance burden and it is meant to be.

HISTORICAL DOCUMENTS ARE EXEMPT.  A letter answering an old report describes
the version it answered, and rewriting it would falsify the record.  Only the
documents that speak for the CURRENT version are checked.

    python check_claims.py

Exit status is non-zero on any hit, so this is usable as a gate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "submission"
PARTS = ROOT / "paper" / "parts"

#: Documents that speak for the CURRENT version.  Everything else under
#: submission/ is correspondence about a previous one and is left alone.
CURRENT = (
    "cover_letter.md",
    "summary_of_changes.md",
    "response_to_review28.md",
    "README.md",
    "OWNER-ACTIONS.md",
    "data_availability.md",
    "credit_statement.md",
    "declaration_of_interests.md",
    "highlights.txt",
)

#: (compiled pattern, what the project now holds, the round that retired it).
#: Write the pattern so it matches the ASSERTION and not a denial of it --
#: "not applied" must not trip a rule about "applied".
RETIRED = [
    (re.compile(r"every region label and every (robustness index|\$?\\?rho\$?)"
                r"[^.]{0,60}\bis the calibrated one", re.I),
     "no coverage calibration is applied; the labels are nominal and the "
     "manuscript states by how much they are anti-conservative",
     27),
    (re.compile(r"\bthe corpus is (therefore )?calibrated with\b", re.I),
     "the calibration is derived and reported, not applied",
     27),
    (re.compile(r"\bcalibration (that|which)? ?(this paper|we) appl(y|ies)\b",
                re.I),
     "the calibration is not applied",
     27),
    (re.compile(r"\bpinn?(ing|ed|s) (its base )?by \*?tag\*?\b", re.I),
     "the Dockerfile pins its base by digest",
     27),
    (re.compile(r"\bDOI reserved, inserted at proof\b", re.I),
     "the software reference carries a resolvable URL and states the DOI's "
     "status in one clause, rather than forwarding to a statement that "
     "forwarded back",
     27),
    (re.compile(r"\bno widening is applied to either\b", re.I),
     "the decision-curve families ARE widened by the measured shortfall "
     "(Section 8.3 applies a factor of 2.61 and costs 13 of 31 operating "
     "points); what is applied to neither family is the (n,K) CALIBRATION. "
     "Two different widenings, and a sentence that conflates them "
     "contradicts Section 8.3 inside the same PDF",
     27),
    #  ROUND TWENTY-EIGHT.  The operative critical value is the empirical
    #  quantile, measured at its level on the family matched to the design;
    #  the sentences that described the reported band as a diagnostic that
    #  does not attain its level are retired as statements about the
    #  CURRENT version.  The multiplier still undercovers, and saying so is
    #  not a hit: these patterns name the labels or the reported band.
    (re.compile(r"\b(?:reported|treated|read) as descriptive diagnostics?"
                r"(?: and not (?:as )?guarantees?)?\b", re.I),
     "the region labels and rho rest on a critical value measured at its "
     "nominal level on the family matched to this design (the empirical "
     "quantile); the multiplier approximation is printed beside it",
     28),
    (re.compile(r"\b(?:every|each) (?:band, )?region label and (?:every )?"
                r"\$?\\?rho\$?[^.]{0,40}\bis (?:therefore )?(?:an? )?"
                r"(?:anti-conservative|descriptive diagnostic)", re.I),
     "the labels rest on the empirical critical value, which attains its "
     "level on the matched family",
     28),
    (re.compile(r"\bno (?:construction|estimator) here attains its level\b",
                re.I),
     "the empirical quantile attains its level on the matched family and "
     "is the operative critical value",
     28),
    (re.compile(r"\b84\.3\s?(?:%|per cent|percent)\b"),
     "84.3% was a median over six synthetic families matched to the "
     "previous surface; the matched non-zero-truth coverage is "
     "\\covMultNonzeroWholeAtDesign / \\covEmpNonzeroWholeAtDesign",
     28),
    #  ROUND TWENTY-SIX'S TWO WITHDRAWALS ARE DELIBERATELY ABSENT.  "the
    #  sign-disagreement rate" is the NAME OF A QUANTITY the paper still
    #  computes and still prints in a table; what was withdrawn is its use as
    #  a HEADLINE, which is a fact about prominence and not about wording.
    #  "most of the variance belongs to no single axis" appears in the very
    #  sentences that withdraw it.  A pattern that fires on both a claim and
    #  its retraction reports noise, and a noisy gate is skipped.  Only
    #  claims a regex can separate from their denial belong in this list.
]


def scan(path: Path) -> list[tuple[int, str, str, int]]:
    out = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return out
    #  A CLAIM INSIDE QUOTATION MARKS IS REPORTED, NOT ASSERTED.  Every
    #  letter that explains a withdrawal quotes the sentence it withdrew, and
    #  a gate that cannot tell those apart fires on the very documents doing
    #  the right thing.  Quoted spans are blanked to spaces so that line
    #  numbers and offsets survive.  A quotation may wrap one line.
    text = re.sub(r'[\u201c"][^\u201d"\n]{0,200}(\n[^\u201d"\n]{0,200})?'
                  r'[\u201d"]',
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    lines = text.splitlines()
    #  join wrapped prose so a claim split across two lines is still seen,
    #  keeping a line number for the report
    for i, line in enumerate(lines, 1):
        window = " ".join(lines[i - 1:i + 2])
        for pat, holds, rnd in RETIRED:
            m = pat.search(window)
            if m and m.start() < len(line) + 1:
                out.append((i, m.group(0)[:78], holds, rnd))
    return out


def main(argv=None):
    print("=" * 78)
    print("check_claims  A WITHDRAWN CLAIM MAY NOT SURVIVE IN THE PACKAGE")
    print("=" * 78)
    print("  %d retired claim(s) declared; historical correspondence exempt"
          % len(RETIRED))

    targets = [SUB / n for n in CURRENT if (SUB / n).exists()]
    targets += sorted(PARTS.glob("*.tex"))
    fails = []
    for f in targets:
        for ln, hit, holds, rnd in scan(f):
            fails.append((f, ln, hit, holds, rnd))

    print("  %d document(s) checked" % len(targets))
    for f, ln, hit, holds, rnd in fails:
        try:
            rel = f.relative_to(ROOT)
        except ValueError:
            rel = f
        print("  FAIL  %s:%d" % (rel, ln))
        print("        says: %s" % hit)
        print("        round %d retired this; the project now holds: %s"
              % (rnd, holds))
    print("check_claims: %d withdrawn claim(s) still asserted" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

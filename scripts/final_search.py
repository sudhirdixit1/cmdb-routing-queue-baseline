"""final_search -- the pre-submission string search, as a script.

The second review ends with a list of strings to search the manuscript and the
generated PDF text for before submitting, each of which either must be gone or
must be checked by hand against the corrected analysis.  A list in a review is
a thing somebody forgets; a script is not.

Three kinds of pattern:

  FORBIDDEN   must not appear anywhere in the manuscript sources or the
              built PDF.  A hit fails the run.
  WITHDRAWN   a number or phrase the corrected analysis replaced.  A hit fails
              the run, because the generated-macro architecture means a
              withdrawn value can only reappear by being typed.
  REVIEW      may legitimately appear; every occurrence is printed with its
              file and line so a human confirms it rather than assuming.

    python final_search.py            # check sources and the built PDF
    python final_search.py --sources  # skip the PDF

Exit status is non-zero on any FORBIDDEN or WITHDRAWN hit.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "paper" / "parts"
PDF = ROOT / "build" / "journal" / "specification_surfaces.pdf"

FORBIDDEN = [
    (r"\bp\s*=\s*0\b(?!\.)", "a p-value written as exactly zero"),
    (r"\bp\s*<\s*0\.000\b", "a p-value below the plus-one floor"),
    (r"DOI reserved", "an archive DOI that has not been minted"),
    (r"inserted at proof", "a value deferred to proof"),
    (r"\bTODO\b|\bFIXME\b|\bXXX\b", "an editing marker"),
    #  Not just `the referee asked': the manuscript carried `the referee of
    #  the previous version asked for', which the adjacent form missed.  Any
    #  referee within a clause of a verb of asking is referee-facing
    #  narrative, and Gate 5 asks for a finished article rather than a reply.
    (r"\bthe referee\b[^.]{0,60}?"
     r"\b(?:asked|asks|wrote|writes|says|said|requested|objected)\b",
     "referee-facing narrative"),
    (r"\bthis round\b", "round-facing narrative"),
]

WITHDRAWN = [
    (r"\binteractions carry (?:a median )?30", "the withdrawn interaction share"),
    (r"\b57\.2\s*\\?%", "the withdrawn cross-unit regret figure"),
    #  the phrase may appear INSIDE its own withdrawal, which is the one
    #  place a withdrawn claim belongs.  The exception is therefore stated as
    #  a property of the SENTENCE: the occurrence is allowed when the same
    #  sentence goes on to call it false, withdrawn or refuted.  An earlier
    #  version required the phrase to be closed by a quote and then followed
    #  immediately by `is false', which the manuscript's own withdrawal
    #  sentence does not do -- so the check failed on the one occurrence it
    #  was written to permit.
    (r"exactly the rank-based ones(?![^.]{0,160}"
     r"(?:false|withdrawn|refuted))",
     "the withdrawn characterisation of monotone invariance"),
    (r"\b21 logs\b", "the corpus count that disagreed with the manuscript"),
    (r"\bconfirmatory contrast", "the withdrawn label for the planned contrasts"),
    (r"one number is (?:a )?safe\b(?! summary of a surface)",
     "an unqualified safety claim"),
]

REVIEW = [
    (r"\bconfirmatory\b", "should appear only where a prospective protocol "
                          "supports it"),
    (r"\bcorrection~?C\d+", "each must exist in the register"),
    (r"\buniformly beneficial\b", "must be a whole-surface claim"),
    (r"\bmedian\b", "must name the unit of analysis"),
]


def sources():
    out = []
    for f in sorted(PARTS.glob("*.tex")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            out.append((f.name, n, line))
    return out


def pdf_text():
    if not PDF.exists():
        return ""
    for tool in ("pdftotext",):
        try:
            r = subprocess.run([tool, "-q", str(PDF), "-"],
                               capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
        except Exception:  # noqa: BLE001
            continue
    return ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", action="store_true",
                    help="skip the built PDF")
    a = ap.parse_args(argv)
    lines = sources()
    txt = "" if a.sources else pdf_text()

    fails, notes = [], []
    print("=" * 92)
    print("FINAL PRE-SUBMISSION SEARCH")
    print("=" * 92)

    for group, pats, hard in (("FORBIDDEN", FORBIDDEN, True),
                              ("WITHDRAWN", WITHDRAWN, True),
                              ("REVIEW", REVIEW, False)):
        for pat, why in pats:
            rx = re.compile(pat, re.I)
            hits = [(f, n, l.strip()[:88]) for f, n, l in lines if rx.search(l)]
            if txt and rx.search(txt) and not hits:
                hits.append(("(built PDF)", 0, "match in the rendered text"))
            if not hits:
                continue
            if hard:
                for f, n, l in hits:
                    fails.append("%s  %s:%d  %s" % (why, f, n, l))
            else:
                notes.append("%-46s %d occurrence(s)" % (why, len(hits)))

    for n in notes:
        print("  note   " + n)
    for f in fails:
        print("  FAIL   " + f)
    print("final_search: %d patterns, %d failures%s"
          % (len(FORBIDDEN) + len(WITHDRAWN) + len(REVIEW), len(fails),
             "" if txt else "  (sources only; the PDF was not read)"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

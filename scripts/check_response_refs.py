"""check_response_refs -- EVERY SECTION NUMBER IN THE COVER MATERIAL EXISTS.

Round nineteen.  The response to the referee is a map from the report's ten
major comments to the places in the manuscript that answer them, and its whole
value is that a referee can follow it.  A reference to a section that does not
exist, or that exists and discusses something else, is worse than no reference:
it costs the referee the trip and it reads as carelessness about the very
comment being answered.

Eight of the letter's references were stale after this round renumbered the
manuscript, and they were found by hand.  This file exists so the next round
does not have to.

It reads the ASSEMBLED manuscript, counts \\section and \\subsection exactly as
LaTeX does -- starred headings take no number, and \\appendix restarts the
counter in letters -- and then checks every "S<n>" reference in the submission
material against that map.  It prints the heading each reference lands on, so a
reference that resolves to the wrong section is visible even though it is not
an error.

    python check_response_refs.py            # check
    python check_response_refs.py --map      # print the numbering and stop

Exit status is non-zero if any reference names a heading that does not exist.
"""
from __future__ import annotations

import argparse
import re
import string
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANUSCRIPT = ROOT / "paper" / "specification_surfaces.tex"
DOCS = [ROOT / "submission" / "response_to_referee.md",
        ROOT / "submission" / "cover_letter.md"]

HEADING = re.compile(r"\\(appendix|section|subsection)(\*?)(?:\{([^}]*)\})?")
#  A reference is a section sign followed by a number, or the word Appendix
#  followed by a letter.  `SS1.2` and `SS1` are both references; `SS` alone is
#  not, and a number in ordinary prose is not.
REF = re.compile(r"\u00a7\s?([0-9]+(?:\.[0-9]+)?|[A-G](?:\.[0-9]+)?)")
APPREF = re.compile(r"Appendix\s+([A-G])\b")


def numbering(text):
    """Map every numbered heading to its printed number, LaTeX's way."""
    body = text.split("\\begin{document}", 1)[-1]
    out, sec, sub, app = {}, 0, 0, False
    for m in HEADING.finditer(body):
        kind, star, title = m.group(1), m.group(2), m.group(3)
        if kind == "appendix":
            app, sec = True, 0
            continue
        if star:                       # \section*{} takes no number
            continue
        if kind == "section":
            sec, sub = sec + 1, 0
            n = string.ascii_uppercase[sec - 1] if app else str(sec)
        else:
            sub += 1
            base = string.ascii_uppercase[sec - 1] if app else str(sec)
            n = "%s.%d" % (base, sub)
        #  A heading like \subsection{\texttt{fieldvalue}} has a nested brace,
        #  so the regex's group stops early.  Re-read the argument by counting
        #  braces from the opening one, then strip the markup, so the title
        #  printed beside a reference is the title a reader would see.
        j = body.find("{", m.start())
        if j != -1:
            depth, k = 0, j
            while k < len(body):
                depth += (body[k] == "{") - (body[k] == "}")
                if depth == 0:
                    break
                k += 1
            title = body[j + 1:k]
        title = re.sub(r"\\[a-zA-Z]+\s*", "", title or "")
        out[n] = title.replace("{", "").replace("}", "").strip()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", action="store_true")
    a = ap.parse_args(argv)

    if not MANUSCRIPT.exists():
        sys.exit("assemble the manuscript first: python assemble_paper.py")
    N = numbering(MANUSCRIPT.read_text(encoding="utf-8"))
    if a.map:
        for k in sorted(N, key=lambda s: (len(s.split(".")), s)):
            print("  %-7s %s" % (k, N[k]))
        return 0

    bad, checked = [], 0
    for doc in DOCS:
        if not doc.exists():
            continue
        for i, line in enumerate(doc.read_text(encoding="utf-8").splitlines(),
                                 1):
            for m in list(REF.finditer(line)) + list(APPREF.finditer(line)):
                ref = m.group(1)
                checked += 1
                if ref in N:
                    print("  %-28s %-7s %s"
                          % (doc.name + ":" + str(i), ref, N[ref][:52]))
                else:
                    bad.append("%s:%d  %s names no heading in the manuscript"
                               % (doc.name, i, ref))

    print()
    print("check_response_refs: %d references checked, %d unresolved"
          % (checked, len(bad)))
    for b in bad:
        print("  FAIL  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

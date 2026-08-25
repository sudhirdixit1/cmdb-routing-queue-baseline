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
SUPPLEMENT = ROOT / "paper" / "supplement.tex"
DOCS = [ROOT / "submission" / "response_to_referee.md",
        ROOT / "submission" / "response_to_blueprint.md",
        ROOT / "submission" / "response_to_review21.md",
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
    ap.add_argument("--sync", action="store_true",
                    help="rewrite the structure table's word counts from "
                         "results/section_words.csv instead of failing on "
                         "them.  Every edit to the manuscript moves those "
                         "numbers, and a human retyping them is how they go "
                         "wrong.")
    a = ap.parse_args(argv)

    if not MANUSCRIPT.exists():
        sys.exit("assemble the manuscript first: python assemble_paper.py")
    N = numbering(MANUSCRIPT.read_text(encoding="utf-8"))
    #  ROUND TWENTY-ONE.  The appendices are a separate document now, and the
    #  earlier response letters refer to them by the letters they had inside
    #  the article.  Those letters still name real headings, in the
    #  supplement, in the same order -- so the map is positional and is built
    #  here rather than leaving twelve stale references in two historical
    #  documents that answered earlier reviews correctly at the time.
    if SUPPLEMENT.exists():
        S = numbering(SUPPLEMENT.read_text(encoding="utf-8"))
        tops = [k for k in S if "." not in k]
        tops.sort(key=int)
        for i, k in enumerate(tops):
            letter = string.ascii_uppercase[i]
            N.setdefault(letter, "Supplement S%s: %s" % (k, S[k]))
            for sub in sorted(x for x in S if x.startswith(k + ".")):
                N.setdefault("%s.%s" % (letter, sub.split(".", 1)[1]),
                             "Supplement S%s: %s" % (sub, S[sub]))
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

    #  The response's structure table quotes a word count per section.  Those
    #  are the only numbers in the submission package that are not macros, so
    #  they are the only ones that can go stale silently -- and they will,
    #  because every edit to the manuscript moves them.  texlint writes
    #  results/section_words.csv on every run; this checks the table against
    #  it.
    n_words = 0
    sw = ROOT / "results" / "section_words.csv"
    resp = ROOT / "submission" / "response_to_blueprint.md"
    if sw.exists() and resp.exists():
        want = {}
        for line in sw.read_text(encoding="utf-8").splitlines()[1:]:
            name, _, n = line.rpartition(",")
            want[name.strip('"').lower()] = int(n)
        row = re.compile(r"^(\|\s*\d+\s*\|\s*)([^|]+?)(\s*\|\s*)([\d,]+)(\s*\|)")
        lines = resp.read_text(encoding="utf-8").splitlines()
        changed = 0
        for i, line in enumerate(lines, 1):
            m = row.match(line)
            if not m:
                continue
            label, quoted = m.group(2).strip(), int(m.group(4).replace(",", ""))
            key = next((k for k in want
                        if k.startswith(label.lower()[:18])), None)
            if key is None:
                bad.append("%s:%d  the structure table names a section "
                           "%r that the manuscript does not have"
                           % (resp.name, i, label))
                continue
            n_words += 1
            if want[key] == quoted:
                continue
            if a.sync:
                lines[i - 1] = "%s%s%s%s%s" % (
                    m.group(1), m.group(2), m.group(3),
                    "{:,}".format(want[key]), m.group(5)) \
                    + line[m.end():]
                changed += 1
            else:
                bad.append("%s:%d  the structure table says %s is %d words; "
                           "texlint counts %d"
                           % (resp.name, i, label, quoted, want[key]))
        if a.sync and changed:
            resp.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print("  synced %d word counts in %s" % (changed, resp.name))

    print()
    print("check_response_refs: %d references checked, %d section word counts "
          "checked, %d unresolved" % (checked, n_words, len(bad)))
    for b in bad:
        print("  FAIL  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

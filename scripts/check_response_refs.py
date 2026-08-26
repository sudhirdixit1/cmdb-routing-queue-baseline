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
PAPER = ROOT / "paper"
MANUSCRIPT = ROOT / "paper" / "specification_surfaces.tex"
SUPPLEMENT = ROOT / "paper" / "supplement.tex"
DOCS = [ROOT / "submission" / "response_to_referee.md",
        ROOT / "submission" / "response_to_blueprint.md",
        ROOT / "submission" / "response_to_review21.md",
        ROOT / "submission" / "cover_letter.md",
        #  ROUND TWENTY-FIVE.  These four are the documents Elsevier
        #  publishes or the editor reads, and none of them was checked.  The
        #  data availability statement sent a reader to the design-space
        #  table for the list of exclusions.
        ROOT / "submission" / "data_availability.md",
        ROOT / "submission" / "credit_statement.md",
        ROOT / "submission" / "declaration_of_interests.md",
        ROOT / "submission" / "response_to_review23.md"]

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


TABLE_REF = re.compile(r"\bTable~?\s?(S?)([0-9]+)\b")


def table_numbering(text, prefix=""):
    """Map every table's printed number to its label, LaTeX's way: floats are
    numbered in the order their environments OPEN.

    ROUND TWENTY-FIVE.  This file checked section references and not table
    ones, and the difference showed the moment a table was added near the
    front: every article table's number moved by one and four references in
    the submission material silently came to name a different table.  Two of
    them had been wrong before that as well --- the data availability
    statement, which is published, sent a reader to the design-space table
    for the list of exclusions --- so nothing had ever checked these.
    """
    body = text.split("\\begin{document}", 1)[-1]
    #  the assembled document keeps \input{tables/...}, so the float
    #  environments are in the included files and counting them here found
    #  nothing.  They are expanded in place, once, in document order.
    #  the supplement inputs its section files, which in turn input the
    #  table files, so one pass of expansion finds no supplement table at all
    def _expand(mm):
        f = PAPER / (mm.group(1) + ".tex")
        return f.read_text(encoding="utf-8") if f.exists() else ""
    for _ in range(4):
        body, n_sub = re.subn(r"\\input\{([^}]*)\}", _expand, body)
        if not n_sub:
            break
    out, n = {}, 0
    for m in re.finditer(r"\\begin\{table\*?\}", body):
        n += 1
        chunk = body[m.end():m.end() + 4000]
        lab = re.search(r"\\label\{(tab:[^}]+)\}", chunk)
        out[prefix + str(n)] = lab.group(1) if lab else "(no label)"
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

    #  the float numbering of both documents, for the table check below
    T = table_numbering(MANUSCRIPT.read_text(encoding="utf-8"))
    if SUPPLEMENT.exists():
        T.update(table_numbering(SUPPLEMENT.read_text(encoding="utf-8"), "S"))

    bad, checked = [], 0
    n_tables = 0

    #  ROUND TWENTY-FIVE.  `.zenodo.json` is the archive's public metadata ---
    #  the first thing a reader of the DOI sees --- and its description
    #  carried NINE hand-typed numbers, outside the macro discipline
    #  entirely.  Seven of them had gone stale: 107 tests where the suite
    #  collects 108, a median baseline spread of 0.091 where the manuscript
    #  says 0.073, a largest first-order index of 10.1% against 28.7%, an
    #  interaction share of 30.0% against 56.0%, a sign-disagreement rate of
    #  35.3% against 32.8%, and two linter limits the linter had since
    #  tightened.  A paper whose subject is that one number cannot be trusted
    #  should not contradict itself in its own archive record.
    zen = ROOT / ".zenodo.json"
    n_zen = 0
    if zen.exists():
        import json
        zt = json.loads(zen.read_text(encoding="utf-8")).get("description", "")
        macros = dict(re.findall(
            r"\\newcommand\{\\([a-zA-Z]+)\}\{(.*)\}\s*$",
            (PAPER / "numbers.tex").read_text(encoding="utf-8"), re.M))

        def mac(k):
            return (macros.get(k, "\u0000")
                    .replace("{,}", ",").replace("\\%", "%")
                    .replace("$", "").strip())

        #  each entry: the phrase that must appear, built from the macro it
        #  is governed by.  Adding a number to the description means adding
        #  it here, which is the point.
        #  ROUND TWENTY-SIX rewrote the description's evidence paragraph,
        #  because round twenty-six withdrew two of the claims that were in
        #  it: the pooled decomposition's headline and the sign-disagreement
        #  rate.  An archive record that contradicts the manuscript on a
        #  withdrawn claim is worse than one that contradicts it on a stale
        #  number, because a reader cannot tell which document is the later
        #  one.  The claim list moves with the description, which is the
        #  point of its being a list.
        CLAIMS = [
            ("the split carry a median %s of the variance" %
             mac("shareResamplingStratumPct"), "shareResamplingStratumPct"),
            ("moves that to %s" % mac("shareResamplingRollingPct"),
             "shareResamplingRollingPct"),
            ("index at the median pair is %s" %
             mac("foldLargestFirstOrderPct"), "foldLargestFirstOrderPct"),
            ("the higher-order share %s" % mac("foldInteractionTotalPct"),
             "foldInteractionTotalPct"),
            ("against %s and %s on the pooled surface"
             % (mac("pooledLargestFirstMedianPct"),
                mac("pooledInteractionMedianPct")),
             "pooledLargestFirstMedianPct"),
            ("difference of %s AUC is declared" % mac("mpidAuc"), "mpidAuc"),
            ("%s of %s admissible AUC cells"
             % (mac("nDisagreeFullyRestricted"),
                mac("nCellsFullyRestricted")), "nCellsFullyRestricted"),
            ("a median %s AUC from the conventional report" %
             mac("madResolvedMedian"), "madResolvedMedian"),
            ("on %s of %s pairs the data do not determine"
             % (mac("nRefUnresolvedCell"), mac("nPairs")),
             "nRefUnresolvedCell"),
            ("%s tests." % mac("nTests"), "nTests"),
            ("%s log-target pairs" % mac("nPairs"), "nPairs"),
            ("from %s public event logs" % mac("nLogs"), "nLogs"),
        ]
        for phrase, macname in CLAIMS:
            n_zen += 1
            if phrase in zt:
                print("  %-28s %s" % (".zenodo.json", phrase[:56]))
            else:
                bad.append(".zenodo.json  the description does not carry "
                           "%r, which is what \\%s renders to"
                           % (phrase, macname))

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
            for m in TABLE_REF.finditer(line):
                ref = m.group(1) + m.group(2)
                n_tables += 1
                if ref in T:
                    print("  %-28s Table %-4s %s"
                          % (doc.name + ":" + str(i), ref, T[ref]))
                else:
                    bad.append("%s:%d  Table %s is not a table in either "
                               "document" % (doc.name, i, ref))

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
    print("check_response_refs: %d section and %d table references checked, "
          "%d archive-metadata claims, %d section word counts checked, "
          "%d unresolved" % (checked, n_tables, n_zen, n_words, len(bad)))
    for b in bad:
        print("  FAIL  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

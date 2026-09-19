"""check_blind -- THE BLIND PDFS CARRY NOTHING THAT NAMES THE AUTHOR.

IJF RETARGET.  The International Journal of Forecasting reviews
double-blind.  The manuscript and the supplement are built with a switch
(\\ifblind, set by build_journal.py --target ijf) that removes the author
block, the five statements and the archive pointers, and rewrites the
software self-citation as Anonymous.  The switch is a claim; the PDF is
the fact.  This reads what was BUILT -- the text and the metadata of both
blind documents -- and fails on any string that names the author, the
address, the repository or the archive.  File names are checked too.

    python check_blind.py             # check build/journal/{manuscript,supplement}.pdf
    python check_blind.py --selftest  # prove the scanner fires on planted text

WHY A SELFTEST.  Rule 5 of PLAN-STRONG-ACCEPT.md: write the corruption
before you believe the check.  The selftest plants the author's name, a
repository URL and the city in a string and asserts three hits, and
asserts zero on a sentence that should pass.

Exit status is non-zero on any hit.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "journal"
BLIND = [OUT / "manuscript.pdf", OUT / "supplement.pdf"]


def _macro(name):
    m = re.search(r"newcommand\{\\%s\}\{([^}]*)\}" % name,
                  (ROOT / "paper" / "numbers.tex").read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def patterns():
    p = ["Dixit", "sudhir", "sudhirdixit1", r"github\.com", "zenodo",
         r"10\.5281", "Independent Researcher", "ORCID", "Anthropic",
         "Claude",
         #  the package's name: a search for it beside the paper's title
         #  returns the author's repository first.  The blind documents
         #  print \pkgname (paper/parts/blindnames.tex) instead; a \citep
         #  key is not printed text, and the .bbl entry is anonymised.
         "fieldvalue"]
    #  the street and the city are the author's; they live only in
    #  numbers.tex, so they are read from there rather than typed here
    for k in ("affiliationStreet", "affiliationCity"):
        v = _macro(k)
        if v:
            p.append(re.escape(v))
    return [re.compile(x, re.I) for x in p]


def scan(text, pats):
    return [(m.group(0),
             text[max(0, m.start() - 40):m.end() + 40].replace("\n", " "))
            for pat in pats for m in pat.finditer(text)]


def pdf_text(pdf):
    return subprocess.run(["pdftotext", "-q", str(pdf), "-"],
                          capture_output=True, text=True, timeout=180).stdout


def pdf_meta(pdf):
    return subprocess.run(["pdfinfo", str(pdf)],
                          capture_output=True, text=True).stdout


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pats = patterns()
    if argv and argv[0] == "--selftest":
        hits = scan("draft by Sudhir Dixit, github.com/x, Apex", pats)
        assert len(hits) >= 3, hits
        assert not scan("a register is a predictor", pats)
        print("check_blind selftest OK: %d hits on the planted text"
              % len(hits))
        return 0
    fails = []
    for pdf in BLIND:
        if not pdf.exists():
            fails.append("%s missing (run build_journal.py --target ijf)"
                         % pdf.name)
            continue
        for what, ctx in scan(pdf_text(pdf), pats) + scan(pdf_meta(pdf), pats):
            fails.append("%s: '%s' in ...%s..." % (pdf.name, what, ctx))
    for f in OUT.glob("*.pdf"):
        if "dixit" in f.name.lower():
            fails.append("file name names the author: %s" % f.name)
    for f in fails:
        print("FAIL  " + f)
    print("check_blind: %d failures" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

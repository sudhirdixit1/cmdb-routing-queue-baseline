"""fill_response21 -- substitute the built page and table counts into the
round-twenty-one response letter.

The letter quotes the article's page count, the supplement's, the number of
tables in each and the misreport headline.  Those are the only numbers in the
submission package that are not macros, because the response is Markdown and
does not pass through LaTeX -- so they are the only ones that can go stale
silently, which is what happened to the previous round's structure table.

Every placeholder has the form `@NAME@` and is replaced from the BUILT PDFs
and the assembled sources, so the letter cannot quote a page count for a
document that was not built.

    python fill_response21.py             # substitute
    python fill_response21.py --check     # fail if any placeholder remains
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = ROOT / "build" / "journal"
PAPER = ROOT / "paper"
DOCS = [ROOT / "submission" / "response_to_review21.md",
        ROOT / "submission" / "cover_letter.md"]


def pages(stem):
    """The page count LaTeX wrote, read from the build log rather than from
    the PDF, so it is the count the build actually produced."""
    for name in ("p3.log", "s3.log"):
        p = BUILD / name
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if ("%s.tex" % stem) not in txt and ("%s.pdf" % stem) not in txt:
            continue
        m = re.search(r"Output written on %s\.pdf \((\d+) pages" % re.escape(stem),
                      txt)
        if m:
            return int(m.group(1))
    return None


def n_tables(tex):
    if not tex.exists():
        return None
    return len(re.findall(r"\\input\{tables/", tex.read_text(encoding="utf-8")))


def prose_words():
    total = 0
    for f in sorted((PAPER / "parts").glob("[0-9]*.tex")):
        total += len(f.read_text(encoding="utf-8").split())
    return total


def misreport():
    n = PAPER / "numbers.tex"
    if not n.exists():
        return None
    m = re.search(r"\\newcommand\{\\misreportPooledResolvedPct\}\{([^}]*)\}",
                  n.read_text(encoding="utf-8"))
    return m.group(1).replace("\\%", "%") if m else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    missing_docs = [d for d in DOCS if not d.exists()]
    if missing_docs:
        sys.exit("no %s" % ", ".join(str(d) for d in missing_docs))

    pm, ps = pages("specification_surfaces"), pages("supplement")
    nt = n_tables(PAPER / "specification_surfaces.tex")
    pw = prose_words()
    vals = {
        "PAGES_MAIN": ("%d pages" % pm) if pm else None,
        "PAGES_SUPP": ("%d pages" % ps) if ps else None,
        "N_TABLES_MAIN": ("%d" % nt) if nt else None,
        "PROSE_WORDS": "{:,}".format(pw),
        "PROSE_PAGES": ("%d" % (pm - 20)) if pm else None,
        "MISREPORT_RESOLVED": misreport(),
    }
    missing = [k for k, v in vals.items() if v is None]
    if missing:
        sys.exit("cannot resolve %s -- build the PDFs first"
                 % ", ".join(missing))

    if a.check:
        bad = {}
        for d in DOCS:
            left = re.findall(r"@([A-Z_]+)@", d.read_text(encoding="utf-8"))
            if left:
                bad[d.name] = sorted(set(left))
        if bad:
            sys.exit("unsubstituted placeholders: %s"
                     % "; ".join("%s: %s" % (k, ", ".join(v))
                                 for k, v in bad.items()))
        print("%s: no unsubstituted placeholders"
              % ", ".join(d.name for d in DOCS))
        return 0

    for k, v in vals.items():
        print("  %-20s %s" % (k, v))
    rc = 0
    for d in DOCS:
        text = d.read_text(encoding="utf-8")
        for k, v in vals.items():
            text = text.replace("@%s@" % k, v)
        d.write_text(text, encoding="utf-8")
        left = re.findall(r"@([A-Z_]+)@", text)
        if left:
            print("  %s STILL UNSUBSTITUTED: %s"
                  % (d.name, ", ".join(sorted(set(left)))))
            rc = 1
        else:
            print("wrote %s" % d.name)
    return rc


if __name__ == "__main__":
    sys.exit(main())

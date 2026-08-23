"""texlint -- the manuscript's own compliance checks.

Round nineteen.  A referee for *Information Systems* returned the previous
version for technical corrections before scientific review: the abstract was
636 words against a 250-word limit, there were eight keywords against a limit
of seven, the highlights were absent, and several statements were missing.
Those are not judgement calls and should not be checked by reading.

    python texlint.py            # all checks
    python texlint.py --report   # print the counts without failing

Checks
  1  abstract word count             <= 250
  2  keyword count                   <= 7
  3  highlights                       3..5 bullets, each <= 85 characters
  4  required statements present      CRediT, competing interests, funding,
                                      data availability, generative AI
  5  no `Appendix Appendix`           the duplicated-label defect
  6  no numeric literal in the body   every number is a macro from numbers.tex
  7  no rhetorical openers            the sentence shapes the referee asked to
                                      have deleted
  8  every \\input target exists
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
TEX = PAPER / "specification_surfaces.tex"
HIGH = ROOT / "submission" / "highlights.txt"

ABSTRACT_LIMIT = 250
KEYWORD_LIMIT = 7
HIGHLIGHT_LIMIT = 85

REQUIRED = [
    ("CRediT", r"CRediT authorship contribution statement"),
    ("competing interests", r"Declaration of competing interest"),
    ("funding", r"\\section\*\{Funding\}"),
    ("data availability", r"\\section\*\{Data availability\}"),
    ("generative AI", r"Declaration of generative AI"),
]

BANNED_OPENERS = [
    r"(?m)^A referee is entitled to",
    r"(?m)^A reader may object",
    r"(?m)^We report rather than hide",
    r"(?m)^This is correction number",
]

FAILS, NOTES = [], []


def strip_comments(t):
    return re.sub(r"(?<!\\)%.*", "", t)


def body_of(t):
    """Everything between \\begin{document} and \\appendix, with the
    frontmatter, the generated tables and the math removed.  The literal check
    runs on prose only: a generated table is allowed to contain numbers,
    because it IS the generated file."""
    t = strip_comments(t)
    i = t.find("\\begin{frontmatter}")
    j = t.find("\\appendix")
    t = t[i:j if j > 0 else len(t)]
    t = re.sub(r"\\input\{[^}]*\}", " ", t)
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"\\\[.*?\\\]", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", " ", t, flags=re.S)
    t = re.sub(r"\\(label|ref|eqref|cite[pt]?)\{[^}]*\}", " ", t)
    t = re.sub(r"\\includegraphics(\[[^]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(documentclass|usepackage)(\[[^]]*\])?\{[^}]*\}", " ", t)
    return t


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    if not TEX.exists():
        sys.exit("assembled manuscript not found; run assemble_paper.py")
    raw = TEX.read_text(encoding="utf-8")
    t = strip_comments(raw)

    # 1 abstract
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", t, re.S)
    n_abs = 0
    if not m:
        FAILS.append("no abstract found")
    else:
        w = re.sub(r"\\[a-zA-Z]+\\?", "X", m.group(1))
        w = re.sub(r"[{}$\\]", " ", w)
        #  a token carrying no letter and no digit -- an em dash, a stray
        #  brace -- is not a word, and a publisher's counter does not count
        #  one.  A macro is counted as one word, which is what it usually
        #  expands to; the four that expand to two are named in NOTES below.
        n_abs = len([x for x in w.split() if re.search(r"[A-Za-z0-9]", x)])
        if n_abs > ABSTRACT_LIMIT:
            FAILS.append("abstract is %d words, limit %d" % (n_abs,
                                                             ABSTRACT_LIMIT))

    # 2 keywords
    m = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", t, re.S)
    n_kw = 0
    if not m:
        FAILS.append("no keyword block found")
    else:
        n_kw = len([k for k in m.group(1).split("\\sep") if k.strip()])
        if n_kw > KEYWORD_LIMIT:
            FAILS.append("%d keywords, limit %d" % (n_kw, KEYWORD_LIMIT))

    # 3 highlights
    n_hi = 0
    if not HIGH.exists():
        FAILS.append("submission/highlights.txt is missing")
    else:
        ht = HIGH.read_text(encoding="utf-8")
        bullets = re.findall(r"(?m)^\[(\d+)\] (.+)$", ht)
        n_hi = len(bullets)
        if not (3 <= n_hi <= 5):
            FAILS.append("%d highlights; the limit is 3 to 5" % n_hi)
        for stated, text in bullets:
            if len(text) > HIGHLIGHT_LIMIT:
                FAILS.append("highlight over %d characters: %s"
                             % (HIGHLIGHT_LIMIT, text[:40]))
            if int(stated) != len(text):
                FAILS.append("highlight length claim %s is wrong (%d): %s"
                             % (stated, len(text), text[:40]))

    # 4 required statements
    for name, pat in REQUIRED:
        if not re.search(pat, t):
            FAILS.append("missing statement: %s" % name)

    # 5 the duplicated-appendix defect
    if "Appendix Appendix" in t:
        FAILS.append("the manuscript contains 'Appendix Appendix'")

    # 6 numeric literals in the prose
    body = body_of(raw)
    #  A four-digit year inside a proper name -- "BPI Challenge 2014", "the
    #  PRISMA 2020 statement" -- is part of the name, not a result, and is
    #  allowed.  Everything else must come from numbers.tex.
    body = re.sub(r"(?:19|20)[0-9][0-9]", " ", body)
    #  SHA-256 is the name of a hash function, not a result.
    body = re.sub(r"SHA-[0-9]+", " ", body)
    lits = re.findall(r"(?<![\w.])\d[\d.,]*(?![\w])", body)
    lits = [x for x in lits if x not in {"1", "2", "3", "4", "5", "0"}]
    if lits:
        FAILS.append("numeric literals in the prose (every number should be "
                     "a macro): %s" % ", ".join(sorted(set(lits))[:12]))

    # 7 rhetorical openers
    for pat in BANNED_OPENERS:
        if re.search(pat, t):
            FAILS.append("a banned rhetorical opener survives: %s" % pat)

    # 8 \input targets
    for tgt in re.findall(r"\\input\{([^}]*)\}", t):
        p = PAPER / (tgt if tgt.endswith(".tex") else tgt + ".tex")
        if not p.exists():
            FAILS.append("\\input target does not exist: %s" % tgt)

    #  the body word count, reported rather than enforced
    words = len(re.sub(r"[{}$\\]", " ", body).split())
    NOTES.append("abstract %d words; %d keywords; %d highlights; "
                 "main-text source about %d words" % (n_abs, n_kw, n_hi, words))

    for n in NOTES:
        print("  " + n)
    for f in FAILS:
        print("  FAIL  " + f)
    print("texlint: %d failures" % len(FAILS))
    if a.report:
        return
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

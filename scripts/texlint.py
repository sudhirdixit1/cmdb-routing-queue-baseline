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
  9  no stray control character       a here-document turning \\b into 0x08
 10  a spelled-out count matches      the list of identifiers it introduces
 11  no `Appendix' before a \\ref      that already supplies the word
 12  no macro swallowing its space    a control word eats the space after it
 13  no wordy macro inside math       $...$ sets its words as italic variables
 14  no phrase repeated immediately   a scripted edit leaving its own tail

Checks 10 to 14 exist because each caught a defect that had already reached a
compiled PDF: `forty lines' for a file of 121 statements, `Appendix Appendix
G' on fourteen references, `42.0%--- and', `18percentagepoints', and a
sentence's tail printed twice.  Every one of them was found by READING the
rendered pages, which is the check this file cannot replace.
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

#  ROUND TWENTY-ONE.  The review's front-matter items: the Elsevier template
#  caps keywords at SIX, not seven, and asks for an abstract that a reader
#  finishes -- the limit here is the one the review set, 200 words, which is
#  stricter than the journal's and is the point.
ABSTRACT_LIMIT = 200
KEYWORD_LIMIT = 6
HIGHLIGHT_LIMIT = 85

#  the changelog belongs in the repository, not in the article.  These are the
#  two phrases the review named; each is a failure wherever it appears in the
#  MAIN TEXT, and the supplement is exempt because that is where the
#  correction register lives.
BANNED_IN_MAIN = [
    ("self-reference", r"an earlier version of this work|"
                       r"an earlier version of this paper|"
                       r"the previous version of this work|"
                       r"an earlier draft of this section|"
                       r"an earlier round"),
    ("correction reference", r"correction~?C\d+"),
]

#  ---- THE REVISION NARRATIVE, WHICH BELONGS IN THE RESPONSE LETTER --------
#  An archival article is read by people who never saw its referee reports.
#  A manuscript that says "round twenty-six adds", "a defect a referee named"
#  or "it is not in this version" is telling those readers about a
#  conversation they were not part of, and it dates the article to a moment in
#  a review process rather than to a state of knowledge.  Every one of these
#  sentences has a home -- `submission/response_to_review*.md' -- and this
#  check is what keeps them there.  It runs over the article AND the
#  supplement, because both are archived.
#
#  It is deliberately blunt: a phrase that trips it can almost always be said
#  without the history, and where it genuinely cannot -- the pre-registration
#  paragraph has to say what was fixed BEFORE the results -- the sentence is
#  written about the protocol rather than about the round.
REVISION_NARRATIVE = [
    ("a numbered revision round",
     r"\bround (?:nineteen|twenty|twenty-\w+|twenty\s+\w+|\d+)\b"),
    ("a reference to the referees",
     r"\b(?:a|the|this|our|its) referees?\b|\breferees\b|"
     r"\bthe (?:report|review)(?:'s)? (?:asks|asked|names|named|"
     r"wants|wanted|requires|required)\b"),
    ("a sentence about the manuscript's own editing",
     r"\bthe earlier wording\b|\bthis (?:paragraph|section|sentence) "
     r"(?:used to|previously|formerly|originally)\b|"
     #  NOT "as it stands", which is ordinarily said of an equation or a
     #  definition and was a false positive on Section 3.2's first line.
     r"\bdid not make clear which\b|"
     r"\bthe wording (?:above|below|here) (?:was|has been)\b"),
    ("a reference to this draft as one of several",
     r"\bthis version of the (?:paper|manuscript|article)\b|"
     r"\b(?:not|absent) in this version\b|\bin this version\b|"
     r"\bthis (?:round|revision|resubmission)\b|"
     r"\bearlier (?:versions?|drafts?) of this (?:paper|work|manuscript)\b|"
     r"\bthe previous (?:version|draft|round)\b|"
     r"\bin (?:this|the current) revision\b"),
]

REQUIRED = [
    ("CRediT", r"CRediT authorship contribution statement"),
    ("competing interests", r"Declaration of competing interest"),
    ("funding", r"\\section\*\{Funding\}"),
    ("data availability", r"\\section\*\{Data availability\}"),
    #  ROUND TWENTY-SEVEN.  Capital G, and the check is case-sensitive on it
    #  deliberately.  Elsevier's policy page gives the section title verbatim
    #  as "Declaration of Generative AI and AI-assisted technologies in the
    #  writing process", and this is a REQUIRED section whose title an
    #  editorial check reads literally.  This pattern held the lower-case
    #  form for ten rounds and would have failed the build the moment the
    #  title was corrected, so the wrong spelling was being enforced.
    ("generative AI", r"Declaration of Generative AI"),
]

BANNED_OPENERS = [
    r"(?m)^A referee is entitled to",
    r"(?m)^A reader may object",
    r"(?m)^We report rather than hide",
    r"(?m)^This is correction number",
]

#  The referee named FIVE sentence-openers to delete and this file banned
#  four; `An earlier version...' opened six sentences, five of them in the
#  main text.  The objection was that transparency should be visible in the
#  design and the supplement rather than repeatedly asserted, so the opener is
#  banned in the MAIN TEXT and allowed in the correction register, which is
#  the supplement whose whole job is to say what an earlier version claimed.
MAIN_TEXT_BANNED = [r"(?m)(^|\.\s+)An earlier version"]
CORRECTION_APPENDIX = "app_corrections.tex"

#  ROUND TWENTY-FIVE.  Check 6 reads `body_of`, and `body_of` strips inline
#  math before it looks -- so `$0.780$` was invisible to the rule that no
#  number is typed into the prose, and three coverages of the (n, K) plane sat
#  in Section 10.3 as literals for four rounds.  The hole cannot be closed by
#  banning digits inside math: a level, a nominal rate, a declared split and
#  the standard normal quantile all belong there and are not results.
#
#  So the rule is an ALLOWLIST.  Every inline-math span in the body that
#  carries a numeric literal must appear here with a reason, and anything else
#  is a failure.  The cost of adding an entry is having to justify it, which
#  is the point: a result cannot be justified, so it becomes a macro.
MATH_LITERALS_ALLOWED = {
    r"$[0,1]$": "the unit interval, a definition",
    r"$\rho \in [-1,1]$": "the range of the robustness index, a definition",
    r"$95\%$": "the nominal confidence level, a convention not a result",
    r"$1.96$": "the standard normal quantile",
    r"$\alpha = 0.05$": "the declared test level",
    r"$\max(0,-V_s)$": "an argument of a maximum, not a number",
    r"$70/30$": "the registered split proportion",
    r"$[0.5, 2]$": "the declared calibration-slope window",
    r"$0.05$": "the lower end of the declared threshold range for the desk",
    r"$0.80$": "the upper end of the declared threshold range for the desk",
    r"$63\%$": "1 - 1/e, the share of distinct levels a resample holds",
}

#  ROUND TWENTY-FIVE, the same hole one step further out.  Check 6 reads
#  DIGITS, so a result written as a word is invisible to it too: "moves
#  coverage by sixteen points" sat in Section 10.3 beside the three coverages
#  that were hiding inside math.  As with those, a blanket ban is wrong --- a
#  nominal level, a declared split proportion and a count of things listed are
#  all legitimately words --- so this is an allowlist of the phrases that are
#  not results, each with its reason.
WORD_MAGNITUDES_ALLOWED = {
    "ninety-five per cent": "the nominal confidence level, a convention",
    "seventy per cent": "the registered split proportion",
    "five folds": "an illustration of re-describing an axis, not a result",
    "five levels": "the same illustration",
    "one level": "the same illustration -- five folds written as five levels "
                 "rather than one",
    "two levels": "the axis-completeness rule, a declaration of the design",
    "six levels": "the split axis's declared level count",
    "four levels": "the pipeline axis's declared level count on the case "
                   "study's log",
    "three points": "a count of the operating points named next, not a "
                    "magnitude",
}
#  the tens must come first and carry an optional hyphenated unit, or
#  "ninety-five per cent" is matched as "five per cent" and an allowlist
#  entry for the whole phrase never fires
_UNITS_W = (r"one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
            r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen")
_TENS_W = r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
_WORD_NUM = r"(?:(?:%s)(?:-(?:%s))?|%s|hundred)" % (_TENS_W, _UNITS_W,
                                                    _UNITS_W)
#  longest alternative first, or "folds" matches as "fold" and the allowlist
#  entry for the whole phrase never fires
_WORD_UNIT = (r"(?:percentage points?|points?|per cent|percent|times|folds?|"
              r"orders? of magnitude|levels?)")

#  The checks this file performs, as a list rather than as a number in a
#  sentence.  The manuscript quotes the count (Appendix H), so the list is
#  where that number comes from and adding a check updates the paper.
CHECKS = (
    "the abstract's word count",
    "the keyword count",
    "the highlight count and each highlight's length against its own claim",
    "the presence of all five required statements",
    "the absence of `Appendix Appendix'",
    "the absence of any numeric literal in the prose",
    "the absence of the rhetorical openers a referee asked to have deleted",
    "that every input target exists",
    "that no source file carries a stray control character",
    "that a spelled-out count matches the list of identifiers it introduces",
    "that no reference writes `Appendix' before a ref that supplies it",
    "that no macro swallows the space after it",
    "that no macro carrying words or math is used inside math mode",
    "that no phrase is repeated immediately",
    "that no backslash escape was interpreted by a scripted edit",
    "that neither document narrates its own revision history",
)

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
    ap.add_argument("--sections", action="store_true",
                    help="also print the word count of every section, "
                         "which is what a length request is really "
                         "about")
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
    #  ...and the form that PRODUCES it, which the literal check cannot see.
    #  elsarticle's \ref for an appendix section already expands to
    #  `Appendix A', so `Appendix~\ref{app:x}' prints `Appendix Appendix A'.
    #  All fourteen of this manuscript's appendix references were written that
    #  way and the literal check above passed every build, because the source
    #  never contains the doubled word -- only the PDF does.
    dup = re.findall(r"(?i)appendix~?\\ref\{app:[^}]*\}", t)
    for f in sorted((PAPER / "parts").glob("*.tex")):
        dup += re.findall(r"(?i)appendix~?\\ref\{app:[^}]*\}",
                          strip_comments(f.read_text(encoding="utf-8")))
    if dup:
        FAILS.append("%d appendix references write the word Appendix before "
                     "a ref that already supplies it, e.g. %s"
                     % (len(dup), dup[0]))

    #  A control word swallows the whitespace after it, so `\foo bar' prints
    #  `FOObar'.  Every one of the 245 generated macros is a control word, and
    #  the manuscript quotes them mid-sentence constantly.  One had eaten the
    #  space before an em dash and printed `42.0%--- and'.  A space that ends
    #  up before `&' or `\\' inside a tabular is harmless, because LaTeX
    #  discards it there anyway, so those are exempt.
    names = set(re.findall(r"\\newcommand\{\\(\w+)\}",
                           (PAPER / "numbers.tex").read_text(encoding="utf-8"))
                ) if (PAPER / "numbers.tex").exists() else set()
    eaten = []
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        for m in re.finditer(r"\\(\w+)", src):
            if m.group(1) not in names:
                continue
            if src[m.end():m.end() + 1] not in (" ", chr(10), chr(9)):
                continue
            after = src[m.end():m.end() + 6].lstrip()
            if after.startswith("&") or after.startswith(chr(92) * 2):
                continue                      # a tabular cell or row break
            eaten.append("%s: %s%s" % (f.name, chr(92), m.group(1)))
    if eaten:
        FAILS.append("%d macros swallow the space after them (write "
                     "`%smacro%s ' or follow it with punctuation): %s"
                     % (len(eaten), chr(92), chr(92), ", ".join(eaten[:6])))

    #  A macro whose VALUE contains a word must not be quoted inside math
    #  mode: `$\\pm\\auditHalfWidthPct$' set `percentage points' as a
    #  product of six italic variables and printed `18percentagepoints'.
    #  The macro definitions are the source of truth for which ones carry
    #  words, so this needs no list to maintain.
    wordy = set()
    if (PAPER / "numbers.tex").exists():
        for nm, val in re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}",
                                  (PAPER / "numbers.tex").read_text(
                                      encoding="utf-8")):
            #  Two kinds of macro must stay out of math mode.  A macro
            #  carrying WORDS sets them as a product of italic variables.  A
            #  macro carrying its own `$' closes the enclosing math and opens
            #  display math -- `$D = \Dabs$' where \Dabs is `$+0.0899$' failed
            #  the build with "Display math should end with $$", which is at
            #  least loud; the words case is silent and ships.
            if "$" in val:
                wordy.add(nm)
                continue
            #  strip the macros inside the value first: `\times' and `\%' are
            #  markup, not words
            v = re.sub(r"\\[a-zA-Z]+", " ", val)
            if re.search(r"[A-Za-z]{3,}", v):
                wordy.add(nm)
    inmath = []
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        for seg in re.findall(r"\$[^$]*\$", src):
            for nm in re.findall(r"\\(\w+)", seg):
                if nm in wordy:
                    inmath.append("%s: %s%s" % (f.name, chr(92), nm))
    if inmath:
        FAILS.append("%d macros that carry words or their own math are used "
                     "inside math mode: "
                     "%s" % (len(inmath), ", ".join(inmath[:6])))

    #  A scripted edit that replaces a sentence can leave its tail behind:
    #  `That is the pilot's central finding about itself. / central finding
    #  about itself.' shipped in a compiled PDF for a round.  Any run of five
    #  or more words that repeats immediately, ignoring line breaks, is
    #  almost always that rather than deliberate anaphora.
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        #  Math first: `V_s(f \mid B_0) - V_s(f \mid B_1)' is a legitimate
        #  repetition of five tokens once the symbols are read as words, and
        #  a check that flags it is a check nobody will keep running.
        src = re.sub(r"\$[^$]*\$", " ", src)
        src = re.sub(r"\\\[.*?\\\]", " ", src, flags=re.S)
        src = re.sub(r"\\begin\{(equation|aligned|align)\*?\}.*?"
                     r"\\end\{\1\*?\}", " ", src, flags=re.S)
        words = re.findall(r"[A-Za-z']+", src)
        for i in range(len(words) - 10):
            #  not `a' -- that is the argparse namespace, and shadowing it
            #  here made --report raise instead of report
            head = [w.lower() for w in words[i:i + 5]]
            tail = [w.lower() for w in words[i + 5:i + 10]]
            if head == tail:
                FAILS.append("%s repeats a phrase immediately: %r"
                             % (f.name, " ".join(words[i:i + 5])))
                break

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

    # 6b the same rule, INSIDE inline math, against the allowlist
    mathbody = strip_comments(raw)
    i0 = mathbody.find("\\begin{frontmatter}")
    j0 = mathbody.find("\\appendix")
    mathbody = mathbody[i0:j0 if j0 > 0 else len(mathbody)]
    mathbody = re.sub(r"\\input\{[^}]*\}", " ", mathbody)
    bad_math = []
    for m in re.finditer(r"\$[^$]*\$", mathbody):
        span = m.group(0)
        if span in MATH_LITERALS_ALLOWED:
            continue
        #  a digit that is part of an identifier, an exponent or a brace
        #  group -- n^{1/3}, V_0, \tau_2 -- is notation, not a quantity
        #  strip trailing punctuation before the exemption test: a lone `0'
        #  inside \max(0,-V_s) is matched as "0," and is not a quantity
        found = [x for x in
                 (y.rstrip(".,") for y in
                  re.findall(r"(?<![\w.^{_])\d[\d.,]*(?![\w}])", span))
                 if x not in {"", "0", "1", "2", "3", "4", "5"}]
        if found:
            bad_math.append(span if len(span) < 46 else span[:43] + "...")
    if bad_math:
        FAILS.append("numeric literals inside inline math, which check 6 "
                     "cannot see (make each a macro, or add it to "
                     "MATH_LITERALS_ALLOWED with a reason): %s"
                     % ", ".join(sorted(set(bad_math))[:8]))

    # 6c the same rule for a magnitude written as a WORD
    bad_words = []
    for m in re.finditer(_WORD_NUM + r"[- ]" + _WORD_UNIT, body, re.I):
        phrase = m.group(0).lower()
        if phrase not in WORD_MAGNITUDES_ALLOWED:
            bad_words.append(phrase)
    if bad_words:
        FAILS.append("magnitudes spelled as words, which check 6 cannot see "
                     "(make each a macro, or add it to "
                     "WORD_MAGNITUDES_ALLOWED with a reason): %s"
                     % ", ".join(sorted(set(bad_words))[:8]))

    # 6d every macro that LOOKS like one of numbers.tex's is one
    #
    #  ROUND TWENTY-FIVE.  Compressing a section means writing a summary, and
    #  a summary needs the numbers the passage carried.  Twice while doing
    #  that I wrote a macro name that does not exist --- \nDcaResolvedSim,
    #  \tippingPoint --- and every check here passed, because none of them
    #  reads numbers.tex.  The build then died on an undefined control
    #  sequence several files away from the mistake.
    #
    #  numbers.tex's macros are the only control words in this manuscript
    #  that start lowercase and contain a capital, which makes them
    #  recognisable without a list.  The handful of package commands sharing
    #  that shape are named here.
    NOT_NUMBERS = {"externalDocument", "arraybackslash", "raggedright"}
    defined = set(re.findall(r"\\newcommand\{\\([a-zA-Z]+)\}",
                             (PAPER / "numbers.tex").read_text(
                                 encoding="utf-8")))
    unknown = {}
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        for name in set(re.findall(r"\\([a-z][a-zA-Z]*[A-Z][a-zA-Z]*)", src)):
            if name in defined or name in NOT_NUMBERS:
                continue
            unknown.setdefault(name, f.name)
    if unknown:
        FAILS.append("macros used in the manuscript that numbers.tex does "
                     "not define: %s"
                     % ", ".join("\\%s (%s)" % (k, v)
                                 for k, v in sorted(unknown.items())[:8]))

    # 7 rhetorical openers
    for pat in BANNED_OPENERS:
        if re.search(pat, t):
            FAILS.append("a banned rhetorical opener survives: %s" % pat)

    #  7c  ROUND TWENTY-TWO.  A macro whose VALUE carries an unescaped LaTeX
    #  special is a live grenade: an unescaped `%' comments out the rest of
    #  the line, including the macro's own closing brace, and the build dies
    #  on a runaway argument several files later.  That happened the first
    #  time a generated highlight quoted a rate.  Every value in the
    #  generated macro file is checked here, once, where it is cheap.
    nums = PAPER / "numbers.tex"
    if nums.exists():
        bad_macros = []
        for line in nums.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}\s*$", line)
            if not m:
                continue
            val = m.group(2)
            #  a lone % or & or # that is not already escaped
            if re.search(r"(?<!\\)[%&#]", val):
                bad_macros.append(m.group(1))
        if bad_macros:
            FAILS.append("%d generated macros carry an unescaped LaTeX "
                         "special in their value: %s"
                         % (len(bad_macros), ", ".join(bad_macros[:8])))

    #  7b  ROUND TWENTY-ONE.  The changelog is out of the article.  `t' is the
    #  assembled MAIN document only; the supplement is a separate file and is
    #  where the correction register lives, so it is not scanned here.
    for name, pat in BANNED_IN_MAIN:
        hits = re.findall(pat, t, flags=re.IGNORECASE)
        if hits:
            FAILS.append("%d %s(s) survive in the article, which the review "
                         "asked to have moved to the archive: %s"
                         % (len(hits), name, ", ".join(sorted(set(hits))[:6])))
    #  16  THE REVISION NARRATIVE.  Over every part that reaches either
    #  archived document, comments stripped, so a source annotation is free
    #  and a sentence a reader sees is not.
    _narr = []
    for f in sorted((PAPER / "parts").glob("*.tex")):
        if f.name in (CORRECTION_APPENDIX, "app_pilot.tex",
                      "_appendix_block.tex"):
            continue
        src = strip_comments(f.read_text(encoding="utf-8"))
        for name, pat in REVISION_NARRATIVE:
            for m in re.finditer(pat, src, flags=re.IGNORECASE):
                line = src[:m.start()].count("\n") + 1
                _narr.append("%s:%d %s (%r)"
                             % (f.name, line, name, m.group(0)[:48]))
    if _narr:
        FAILS.append(
            "%d passage(s) narrate the manuscript's own revision history, "
            "which belongs in the response letter and not in an archival "
            "article: %s" % (len(_narr), "; ".join(_narr[:8])))

    for f in sorted((PAPER / "parts").glob("*.tex")):
        if f.name == CORRECTION_APPENDIX:
            continue
        src = strip_comments(f.read_text(encoding="utf-8"))
        for pat in MAIN_TEXT_BANNED:
            n = len(re.findall(pat, src))
            if n:
                FAILS.append("%s opens %d sentence(s) with a correction "
                             "narrative that belongs in %s: %s"
                             % (f.name, n, CORRECTION_APPENDIX, pat))

    # 8 stray control characters
    #  Several rounds of scripted editing have written a literal backspace or
    #  form feed into a source file, because a shell here-document turned
    #  "\b" into 0x08 and "\f" into 0x0c on the way to Python.  The damage is
    #  invisible in most editors and fatal in LaTeX, so it is checked rather
    #  than watched for.
    import glob
    #  EVERY C0 control character except tab, newline and carriage return.
    #  The named list was six characters long and a here-document turning a
    #  regex backreference `\1' into 0x01 walked straight through it -- the
    #  check knew about \b, \f, \v, \a, NUL and ESC because those are the ones
    #  it had already been bitten by, which is not a reason to stop there.
    CTRL = {c: "control character 0x%02x" % c
            for c in range(32) if c not in (9, 10, 13)}
    CTRL[127] = "delete"
    CTRL.update({8: "backspace", 11: "vertical tab", 12: "form feed",
                 7: "bell", 0: "NUL", 27: "escape"})
    for pat in ("paper/parts/*.tex", "paper/*.tex", "scripts/*.py",
                "fieldvalue/*.py", "fieldvalue/tests/*.py", "examples/*.py",
                "submission/*.md", "*.md"):
        for f in glob.glob(str(ROOT / pat)):
            try:
                txt = open(f, encoding="utf-8").read()
            except Exception:  # noqa: BLE001
                continue
            for i, ch in enumerate(txt):
                if ord(ch) in CTRL:
                    FAILS.append("%s carries a stray %s at line %d"
                                 % (Path(f).name, CTRL[ord(ch)],
                                    txt[:i].count(chr(10)) + 1))
                    break

    # 9 \input targets
    for tgt in re.findall(r"\\input\{([^}]*)\}", t):
        p = PAPER / (tgt if tgt.endswith(".tex") else tgt + ".tex")
        if not p.exists():
            FAILS.append("\\input target does not exist: %s" % tgt)

    # 10 a spelled-out count must match the list it introduces
    #
    #  The no-numeric-literals rule reads digits and says nothing about words,
    #  which is how "produces all of it in forty lines" survived for a file of
    #  121 statements and "eighteen other public logs" survived for a corpus
    #  of thirteen.  A general check on spelled-out numbers is too noisy to be
    #  useful --- "four objects", "five contrasts" and "nine tenths" are all
    #  fine --- but the sub-case where the number introduces an explicit list
    #  is exact, and it is the form the correction register uses throughout.
    WORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
            "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
            "twenty": 20}
    pat = re.compile(r"\b(%s)\b[^.(]{0,40}?\(((?:[A-Z]\d+[,;]\s*)+[A-Z]\d+)\)"
                     % "|".join(WORD), re.I)
    #  over the PARTS, not over `t`: `t` has had every \input replaced by a
    #  space, so the appendices -- where the correction register lives, and
    #  where this form is used most -- are invisible in it.
    n_enum = 0
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        for m in pat.finditer(src):
            said = WORD[m.group(1).lower()]
            items = [x for x in re.split(r"[,;]\s*", m.group(2)) if x.strip()]
            n_enum += 1
            if said != len(items):
                FAILS.append("%s: \"%s\" introduces %d items: %s"
                             % (f.name, m.group(0)[:46].replace(chr(10), " "),
                                len(items), ", ".join(items)))
    #  The same check where the list is a `description' environment rather
    #  than a parenthesised run of identifiers.  Appendix J said "the
    #  architecture comes with five controls" and then listed SIX, which the
    #  identifier form above cannot see because the items are \item[...]
    #  labels.  A spelled-out count in the sentence immediately before a
    #  description environment is compared with the number of \item's in it.
    LIST = re.compile(
        r"\b(%s)\b[^.]{0,60}\.\s*\n+\\begin\{(description|enumerate|itemize)\}"
        r"(.*?)\\end\{\2\}" % "|".join(WORD), re.I | re.S)
    for f in sorted((PAPER / "parts").glob("*.tex")):
        src = strip_comments(f.read_text(encoding="utf-8"))
        for m in LIST.finditer(src):
            said = WORD[m.group(1).lower()]
            n_items = len(re.findall(r"(?m)^\s*\\item\b", m.group(3)))
            if n_items == 0:
                continue
            n_enum += 1
            if said != n_items:
                head = re.sub(r"\s+", " ", m.group(0)[:60])
                FAILS.append("%s: \"%s\" introduces a list of %d items"
                             % (f.name, head, n_items))
    NOTES.append("%d spelled-out counts checked against the list each "
                 "introduces" % n_enum)

    # 15 a backslash escape interpreted by a scripted edit
    #
    #  A Python edit that writes "\\ref{x}" as "\ref{x}" puts a CARRIAGE
    #  RETURN in the file followed by `ef{x}`, and one that writes "\\nMacro"
    #  puts a NEWLINE followed by `nMacro`.  Both print as garbage; neither is
    #  a wrong NUMBER, so the generated-macro discipline cannot see them; and
    #  both survived into a committed manuscript in an earlier round.  The
    #  signature is exact: a CR that is not part of a CRLF pair, or a line
    #  that begins with the tail of a common control word.
    #  The TAB case is the one that reached a generated TABLE rather than a
    #  hand-written part: "\\textsf" written as "\textsf" inside a Python
    #  caption is a TAB followed by `extsf`, and Python raises no warning for
    #  it because \t is a VALID escape.  So the scan covers paper/tables as
    #  well, and any control character other than newline is a failure --
    #  nothing in this manuscript legitimately contains one.
    TAILS = ("ef{", "ef ", "aisebox", "ightarrow", "esizebox", "ewcommand",
             "oindent", "ewline", "extbf", "extit", "exttt", "extsf",
             "extsc", "extsuperscript", "imes", "op{", "mph{", "ilde",
             "ar{", "egin{", "f{")
    CTRL = {9: "tab", 11: "vertical tab", 12: "form feed", 8: "backspace",
            7: "bell", 0: "NUL", 27: "escape"}
    n_esc = 0
    for f in sorted(list((PAPER / "parts").glob("*.tex"))
                    + list((PAPER / "tables").glob("*.tex"))):
        raw = f.read_bytes().decode("utf-8")
        n_esc += 1
        for i, ch in enumerate(raw):
            if ch == chr(13) and (i + 1 >= len(raw) or raw[i + 1] != chr(10)):
                FAILS.append("%s: a carriage return that is not a line "
                             "ending at line %d -- a backslash escape was "
                             "interpreted by a scripted edit"
                             % (f.name, raw[:i].count(chr(10)) + 1))
                break
        for i, ch in enumerate(raw):
            if ord(ch) in CTRL:
                FAILS.append("%s: a %s character at line %d -- a backslash "
                             "escape was interpreted by a scripted edit"
                             % (f.name, CTRL[ord(ch)],
                                raw[:i].count(chr(10)) + 1))
                break
        for ln, line in enumerate(raw.split(chr(10)), 1):
            for t in TAILS:
                #  at the head of a line, or straight after a control char
                if line.lstrip(chr(13)).startswith(t):
                    FAILS.append("%s:%d begins with %r, which is the tail of "
                                 "a control word whose backslash was eaten"
                                 % (f.name, ln, line[:12]))
                    break
    #  And the SCRIPTS, because the tables and the macros are written by them
    #  and a control character in a Python string lands in the PDF.  This
    #  round it happened three times in one session: a caption written as
    #  "\textsf" (a TAB), a line continuation eaten out of a regex, and a
    #  "\b" in a search pattern that became a BACKSPACE and silently turned a
    #  word-boundary assertion into a match against a character no file
    #  contains.  Python warns about none of them, because \t and \b are
    #  VALID escapes.  Nothing in this repository's Python legitimately holds
    #  a control character other than newline.
    n_py = 0
    for f in sorted((ROOT / "scripts").glob("*.py")):
        raw = f.read_bytes()
        n_py += 1
        bad = [(i, c) for i, c in enumerate(raw)
               if c in CTRL and c != 10]
        if bad:
            i, c = bad[0]
            FAILS.append("scripts/%s: a %s character at line %d -- a "
                         "backslash escape was interpreted where a literal "
                         "was meant" % (f.name, CTRL[c],
                                        raw[:i].count(b"\n") + 1))
    NOTES.append("%d manuscript parts and generated tables, and %d scripts, "
                 "checked for interpreted escapes" % (n_esc, n_py))

    #  the body word count, reported rather than enforced
    words = len(re.sub(r"[{}$\\]", " ", body).split())
    NOTES.append("abstract %d words; %d keywords; %d highlights; "
                 "main-text source about %d words" % (n_abs, n_kw, n_hi, words))

    #  and the same count PER SECTION, because a reviewer who asks for a
    #  length asks for a shape.  Reported, never enforced: a section that is
    #  over its budget is an editorial judgement, not a defect a script can
    #  adjudicate.  submission/response_to_blueprint.md quotes this list.
    cuts = [(m.start(), re.sub(r"\\[a-zA-Z]+|[{}$\\]", "", m.group(1)).strip())
            for m in re.finditer(r"\n\\section\*?\{([^}]*)\}", body)]
    cuts.append((len(body), "(end)"))
    rows = []
    for i in range(len(cuts) - 1):
        seg = body[cuts[i][0]:cuts[i + 1][0]]
        rows.append((cuts[i][1], len(re.sub(r"[{}$\\]", " ", seg).split())))
    #  written every run, so submission/response_to_blueprint.md's structure
    #  table has a file to be checked against and cannot go stale silently.
    out = ROOT / "results" / "section_words.csv"
    if out.parent.exists():
        #  A section title wrapped across two source lines carries a newline
        #  into the field, which makes this file no longer a CSV and killed
        #  check_response_refs with a ValueError rather than a diagnosis.
        #  Whitespace is collapsed here so a title's line breaks cannot reach
        #  a reader of this file.
        out.write_text("section,words\n" + "".join(
            '"%s",%d\n' % (" ".join(s.replace('"', "'").split()), n)
            for s, n in rows), encoding="utf-8")
    if a.sections:
        print("  -- words per section --")
        for s, n in rows:
            print("     %5d  %s" % (n, s))

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

"""retarget_ijf -- THE VOCABULARY MAP OF THE IJF RETARGET, AS A SCRIPT.

PLAN-IJF.md §2.4.  The manuscript was written for an information-systems
readership and is being submitted to a forecasting journal.  The object it
studies does not change; the words for it do.  A rename applied by hand
across nine parts is a rename applied inconsistently, so the map is here,
ordered, and every hit is printed with its context before anything is
written.

    python retarget_ijf.py            # dry run: print every hit
    python retarget_ijf.py --apply    # write

WHAT IT NEVER TOUCHES.  paper/numbers.tex and paper/tables/*.tex are
generated; a \\newcommand line is a macro definition; a match preceded by a
backslash is a macro name; a match inside a \\label{} or a \\ref{} is a key.
EXCLUDE lists (file, line) pairs a human read and kept, with the reason.

Rule 6 of PLAN-STRONG-ACCEPT.md: a directional word is a claim.  Nothing in
MAP is directional; each entry renames a noun phrase for the same referent.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "paper" / "parts"

#  (pattern, replacement, note).  Applied in order, once each, to every part
#  except the generated tables.  Case of a leading capital is preserved.
MAP = [
    #  NOT `forecast value'.  The plan first wrote that; the introduction says
    #  in so many words that the paper reports PERFORMANCE and not VALUE,
    #  because value is what a decision earns and Section 8 is the only place
    #  that computes one.  In the forecasting literature `forecast value' is
    #  exactly that decision-based quantity (Murphy 1993), so the name would
    #  have asserted what the construct paragraph disclaims.
    (r"incremental predictive performance", "incremental forecast performance",
     "the object, everywhere including the title"),
    (r"predictive performance", "forecast performance",
     "the remaining uses, after the phrase above is gone"),
    (r"decision times", "forecast origins", "the axis, plural"),
    (r"decision time", "forecast origin",
     "the axis; the first use in the introduction carries the definition"),
    (r"the outcome predicted", "the forecast target", "one hit, the abstract"),
]

#  (file, line): hits a human read and kept as they were, with the reason.
EXCLUDE = {
}


#  The table captions are not in the parts: round20_tables.py and
#  round21_tables.py write paper/tables/*.tex from string literals, and the
#  highlight templates live in make_highlights.py.  The map runs over those
#  generators too, and make_numbers.py --strict regenerates the tables.
GENERATORS = ["round20_tables.py", "round21_tables.py", "make_highlights.py"]


def files():
    return sorted(p for p in PARTS.glob("*.tex")) + \
        [ROOT / "scripts" / g for g in GENERATORS]


def apply_line(line, pat, rep):
    out, n = [], 0
    pos = 0
    for m in re.finditer(pat, line, flags=re.I):
        s = m.start()
        #  a macro name, a label or a ref key: not prose
        if s > 0 and line[s - 1] == "\\":
            continue
        pre = line[:s]
        if re.search(r"\\(?:label|ref|eqref|cite[a-z]*)\{[^}]*$", pre):
            continue
        r = rep
        if m.group(0)[0].isupper():
            r = rep[0].upper() + rep[1:]
        out.append(line[pos:s]); out.append(r); pos = m.end(); n += 1
    out.append(line[pos:])
    return "".join(out), n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    total, excluded = 0, 0
    for f in files():
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        changed = False
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith(("%", "#")) or "\\newcommand" in line:
                continue
            new = line
            for pat, rep, _ in MAP:
                if (f.name, i) in EXCLUDE:
                    if re.search(pat, new, re.I):
                        excluded += 1
                        print("KEEP  %-28s %4d  %s  [%s]" % (
                            f.name, i, new.strip()[:70], EXCLUDE[(f.name, i)]))
                    continue
                new2, n = apply_line(new, pat, rep)
                if n:
                    total += n
                    print("%s  %-28s %4d  %s" % (
                        "WRITE" if a.apply else "HIT  ", f.name, i,
                        new.strip()[:90]))
                    new = new2
            if new != line:
                lines[i - 1] = new
                changed = True
        if changed and a.apply:
            f.write_text("".join(lines), encoding="utf-8")
    print("retarget_ijf: %d replacement(s) %s, %d kept by EXCLUDE"
          % (total, "written" if a.apply else "pending (dry run)", excluded))
    return 0


if __name__ == "__main__":
    sys.exit(main())

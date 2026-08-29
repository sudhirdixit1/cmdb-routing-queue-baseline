"""check_sources -- NO GENERATOR MAY READ A RETIRED SURFACE BY NAME.

WHY THIS FILE EXISTS.  Round twenty-seven replaced the inference surface.
The manuscript was migrated, and then six separate audits found the same
defect fourteen more times, in fourteen different files:

    A CHECK THAT READS A FIXED FILENAME CANNOT NOTICE THAT THE ANALYSIS MOVED.

The macro generators went on reading it; the coverage matcher did; the region
figure did; the estimator comparison did, and printed a band resolving MORE
cells than the band it was comparing; the calibration sensitivity ladder did,
and its "no widening applied" rung -- which is by construction the article's
own reported band -- disagreed with the article's own resolved count; and the
VERIFIERS did, so the thing built to catch this failed on eleven macros by
disagreeing with the files it was checking.

Every one of those was found by a human-equivalent reading a table and
noticing an impossible number.  None was found by a gate, because no gate
asked the only question that generalises: DOES ANY GENERATOR STILL NAME THE
OLD SURFACE?  That question is cheap, and this file asks it.

WHAT COUNTS AS RETIRED is declared in RETIRED below, prefix by prefix, each
with the prefix that replaces it and one line saying why.  A prefix is
retired when a NEWER FILE MEASURES THE SAME QUANTITY: `s21_bands' and
`s48w_bands' are both whole-surface simultaneous bands, and only one of them
is the article's.

THE ESCAPE HATCH, and why it is narrow.  A retired file is legitimately read
in exactly two situations: as a FALLBACK, so that a partial tree still builds
a document, and as the OLD SIDE of a deliberate comparison, which is how the
manuscript quotes what the previous surface carried.  Both are marked in the
source with a trailing

    # retired-ok: <reason>

and the reason is required, because a bare marker is a way of turning this
file off one line at a time.  Anything else fails.

    python check_sources.py

Exit status is non-zero on any unmarked read, so this is usable as a gate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: prefix -> (replacement, why it is retired).  Add a row here the moment a
#: surface is replaced; that is the whole maintenance burden.
RETIRED = {
    "s21": ("s48w", "the previous inference surface: multinomial resampling "
                    "on a surface chosen by row count, replaced in round "
                    "twenty-seven by a balanced full factorial under weights"),
    "s17": ("s48w", "an inference surface two rounds older still"),
}

#: files that are ABOUT the retired surface and may name it freely.  Each
#: needs a reason, for the same reason the inline marker does.
EXEMPT = {
    "check_sources.py": "declares the retired list",
    "s21_bands.py": "is the generator of the retired surface itself",
    "provenance.py": "records hashes of every script including retired ones",
}

#: THE SURFACE-SHAPED KINDS, and nothing else.  A retired prefix does not
#: retire every file that carries it: `s17_facts' holds a shift diagnostic
#: that no later file recomputes, while `s17_bands' is a superseded band.
#: Flagging the prefix rather than the OBJECT would make this gate noisy,
#: and a noisy gate is one people learn to skip.
SURFACE_KINDS = ("bands", "cells", "regions", "critical", "incomplete")

#: a read of a results file, in either of the two forms the codebase uses
PAT = re.compile(r"""(?:load|read_csv)\s*\(\s*[^)]*?
                     ["'](?P<f>(?P<p>s\d+[a-z]*)_(?P<k>[a-z0-9_]+)\.csv(?:\.gz)?)["']""",
                 re.VERBOSE)
MARK = re.compile(r"#\s*retired-ok:\s*\S")


def scan(path: Path) -> list[tuple[int, str, str]]:
    """Return (line number, filename read, the line) for each unmarked read."""
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return out
    for i, line in enumerate(lines, 1):
        for m in PAT.finditer(line):
            if m.group("p") not in RETIRED:
                continue
            if m.group("k") not in SURFACE_KINDS:
                continue
            #  the marker may sit on this line or the one above it, because a
            #  wrapped call puts the filename on a line of its own
            here = line
            above = lines[i - 2] if i >= 2 else ""
            if MARK.search(here) or MARK.search(above):
                continue
            out.append((i, m.group("f"), line.strip()))
    return out


def main(argv=None):
    print("=" * 78)
    print("check_sources  NO GENERATOR MAY READ A RETIRED SURFACE BY NAME")
    print("=" * 78)
    for p, (rep, why) in sorted(RETIRED.items()):
        print("  %-5s retired in favour of %-5s -- %s" % (p, rep, why))
    print()

    fails = []
    n_files = n_marked = 0
    for f in sorted(HERE.glob("*.py")):
        if f.name in EXEMPT:
            continue
        n_files += 1
        for ln, fn, src in scan(f):
            fails.append((f.name, ln, fn, src))
    #  count the marked ones too, so the output says how much is deliberate
    for f in sorted(HERE.glob("*.py")):
        if f.name in EXEMPT:
            continue
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if MARK.search(line):
                    n_marked += 1
        except (OSError, UnicodeDecodeError):
            pass

    print("  %d generator(s) scanned; %d deliberate read(s) of a retired "
          "surface, each with a stated reason" % (n_files, n_marked))
    for name, ln, fn, src in fails:
        rep = RETIRED[fn.split("_")[0]][0]
        print("  FAIL  %s:%d reads %s" % (name, ln, fn))
        print("        %s" % src[:96])
        print("        use %s_... , or mark the line "
              "`# retired-ok: <reason>' if it is a fallback or a deliberate "
              "comparison with the old surface." % rep)
    print("check_sources: %d unmarked read(s) of a retired surface"
          % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

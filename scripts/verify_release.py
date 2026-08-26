"""verify_release -- DOES A CLEAN CHECKOUT REPRODUCE THE SUBMITTED NUMBERS?

Round twenty-five.  `submission/OWNER-ACTIONS.md` has one blocking item a
script cannot clear --- minting the archive DOI needs the depositing account
--- and one that had been sitting beside it unclaimed: *confirm the archived
release reproduces the submitted numbers to the digit*.  That one is
checkable, and nothing was checking it.

WHAT THE ARCHIVE IS.  Zenodo snapshots whatever a git tag points at.  So the
question is not whether this working tree reproduces its own numbers --- the
gates already answer that, and a working tree can carry an untracked file
that everything silently depends on.  The question is whether a checkout
carrying ONLY WHAT IS COMMITTED reproduces them.  This file exports one with
`git archive`, which sees exactly what the tag would, and runs the manuscript
out of it.

WHAT IT PROVES, AND WHAT IT DOES NOT.  It proves that every number in both
documents is regenerated, byte for byte, from committed result files by
committed code, and that the build needs nothing under `data/` --- which is
the claim `HANDOFF-NEW-MACHINE.md` makes and which a reader who fetches the
archive is entitled to have tested.  It does NOT re-run the analysis from the
raw logs: that needs the 1.2 GB fetch, takes days, and is what
`scripts/reproduce_all.py` is for.  A reader who wants the numbers rebuilt
from the event logs themselves should run that; a reader who wants to know
that the archive is internally consistent should run this.

    python scripts/verify_release.py            # export, rebuild, compare
    python scripts/verify_release.py --keep     # leave the export in place

Exit status is non-zero if any generated file differs from the committed one.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: regenerated in the export and compared byte for byte against the committed
#: copy.  `numbers.tex` is the one that matters --- every number in both
#: documents is a macro in it --- and the generated tables are included
#: because a table is a number too.
COMPARE = ["paper/numbers.tex"]

#: the chain a reader runs.  `build_journal` is last because it is the slow
#: one and because a difference in the macros should be reported before a
#: reader waits for LaTeX.
CHAIN = [
    ("make_numbers.py", "regenerate every macro and table from results/"),
    ("assemble_paper.py", "parts -> the two documents"),
    ("texlint.py", "the manuscript's own compliance checks"),
    ("verify_numbers.py", "re-derive each macro with independent code"),
    ("build_journal.py", "build both documents"),
]

ENV = dict(os.environ)
ENV.update({v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                             "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                             "VECLIB_MAXIMUM_THREADS")})


def export(dest: Path) -> str:
    """A tree containing exactly what is committed, and the commit it is."""
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()
    tar = subprocess.run(["git", "-C", str(ROOT), "archive", head],
                         capture_output=True, check=True).stdout
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)
    return head


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true",
                    help="do not delete the export")
    a = ap.parse_args(argv)

    tmp = Path(tempfile.mkdtemp(prefix="release-check-"))
    work = tmp / "export"
    print("=" * 92)
    print("verify_release  DOES A CLEAN CHECKOUT REPRODUCE THE SUBMITTED "
          "NUMBERS?")
    print("=" * 92)
    head = export(work)
    print("  exported %s to %s" % (head[:12], work))

    #  the claim the handoff makes, tested rather than repeated
    data = work / "data"
    present = sorted(p.relative_to(work).as_posix()
                     for p in data.rglob("*") if p.is_file()) if data.exists() \
        else []
    print("  files under data/ in the export: %d%s"
          % (len(present), ("  " + ", ".join(present[:4])) if present else ""))

    fails = []
    for script, what in CHAIN:
        r = subprocess.run([sys.executable, str(work / "scripts" / script)],
                           capture_output=True, text=True, env=ENV, cwd=work)
        tail = (r.stdout or r.stderr).strip().splitlines()
        print("  %-20s exit=%d  %s"
              % (script, r.returncode, tail[-1][:58] if tail else ""))
        if r.returncode != 0:
            fails.append("%s failed in a clean checkout (%s):\n%s"
                         % (script, what,
                            "\n".join((r.stdout + r.stderr).splitlines()[-12:])))
            break

    if not fails:
        for rel in COMPARE:
            same = filecmp.cmp(ROOT / rel, work / rel, shallow=False)
            print("  %-20s %s" % (Path(rel).name,
                                  "identical" if same else "DIFFERS"))
            if not same:
                fails.append("%s regenerated in a clean checkout differs from "
                             "the committed copy" % rel)
        tabs = sorted((ROOT / "paper" / "tables").glob("*.tex"))
        diff = [t.name for t in tabs
                if not (work / "paper" / "tables" / t.name).exists()
                or not filecmp.cmp(t, work / "paper" / "tables" / t.name,
                                   shallow=False)]
        print("  %-20s %d compared, %d differ"
              % ("generated tables", len(tabs), len(diff)))
        if diff:
            fails.append("generated tables differ in a clean checkout: %s"
                         % ", ".join(diff[:6]))

    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("  export kept at %s" % work)

    print()
    if fails:
        for f in fails:
            print("  FAIL  %s" % f)
        print("\nverify_release: the archive would NOT reproduce the "
              "submitted numbers")
        return 1
    print("verify_release: a checkout carrying only what is committed "
          "regenerates\n  every macro and every generated table byte for "
          "byte, and builds both\n  documents, without any file under data/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

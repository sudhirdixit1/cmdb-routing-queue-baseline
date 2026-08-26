"""check_package -- IS THE THING THE ARTICLE POINTS AT ACTUALLY IN THE PACKAGE?

Round twenty-seven.  A reviewer with the submission package in hand could not
walk the evidence chain, and the reason was not that any evidence was missing
from the repository: it was that the package's own manifest did not list the
supplement.  The article makes thirty-five references to twenty-nine distinct
appendices, all of which live in `paper/supplement.pdf`, and the table in
`submission/README.md` named the article and not it.  Every gate in this
repository passed, because no gate had ever read the manifest.

This one does.  It asserts four things:

  1.  every file the manifest names exists;
  2.  every document the article REFERENCES is named in the manifest -- if
      the article resolves an `\\ref{app:...}`, the supplement is required;
  3.  the two built documents are no older than the assembled sources they
      are built from, so the package cannot ship a stale PDF;
  4.  the repository carries a licence file, and it is the licence
      `.zenodo.json` declares.

    python check_package.py          # check
    python check_package.py --list   # print the manifest as parsed

Exit status is non-zero on any failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "submission"
PAPER = ROOT / "paper"
MANIFEST = SUB / "README.md"

FAILS = []


def manifest_paths():
    """Every repository path the manifest names in a table cell, resolved
    against `submission/`.  A path is a backticked token containing a slash or
    a dot, which is how every row of those tables writes one."""
    if not MANIFEST.exists():
        FAILS.append("submission/README.md is missing; the package has no "
                     "manifest")
        return []
    out = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        for tok in re.findall(r"`([^`]+)`", line.split("|")[1]):
            tok = tok.strip()
            if "/" in tok or tok.endswith((".md", ".txt", ".pdf")):
                out.append(tok)
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)

    paths = manifest_paths()
    if a.list:
        for p in paths:
            print("  %-58s %s" % (p, "ok" if (SUB / p).exists() else "MISSING"))

    # 1.  every named file exists
    missing = [p for p in paths if not (SUB / p).exists()]
    #  the two built PDFs are produced by build_journal into build/journal and
    #  copied to paper/; either location satisfies the manifest
    still = []
    for p in missing:
        alt = PAPER / Path(p).name
        if not alt.exists():
            still.append(p)
    if still:
        FAILS.append("the package manifest names %d file(s) that do not "
                     "exist: %s" % (len(still), ", ".join(still)))

    # 2.  a referenced document must be in the manifest
    art = PAPER / "specification_surfaces.tex"
    if art.exists():
        n_app = len(re.findall(r"\\ref\{app:[^}]*\}", art.read_text(encoding="utf-8")))
        listed = any("supplement.pdf" in p for p in paths)
        if n_app and not listed:
            FAILS.append(
                "the article makes %d reference(s) to the supplement and the "
                "package manifest does not name supplement.pdf, so a reader "
                "who receives the package cannot follow any of them" % n_app)

    # 3.  a built PDF may not be older than the source it is built from
    for stem in ("specification_surfaces", "supplement"):
        src, pdf = PAPER / (stem + ".tex"), PAPER / (stem + ".pdf")
        if src.exists() and pdf.exists() and pdf.stat().st_mtime < src.stat().st_mtime:
            FAILS.append("%s.pdf is older than %s.tex; the package would ship "
                         "a stale document" % (stem, stem))

    # 4.  the licence exists and agrees with the archive metadata
    lic = ROOT / "LICENSE"
    if not lic.exists():
        FAILS.append("there is no LICENSE file; a reader cannot tell what "
                     "they may do with the code the paper rests on")
    else:
        zp = ROOT / ".zenodo.json"
        if zp.exists():
            declared = str(json.loads(zp.read_text(encoding="utf-8"))
                           .get("license", "")).upper()
            body = lic.read_text(encoding="utf-8").upper()
            if declared and declared.split("-")[0] not in body:
                FAILS.append(
                    "the archive metadata declares the %s licence and LICENSE "
                    "does not appear to be it" % declared)

    print("check_package: %d manifest entries, %d failures"
          % (len(paths), len(FAILS)))
    for f in FAILS:
        print("  FAIL  " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

"""Build the Information Systems (Elsevier) submission PDF.

The document was retargeted from IAAI-27 to Information Systems in round
fifteen; `scripts/build_paper.py` builds the superseded AAAI version and is
kept only so that version stays reproducible.  This script is the current
one.

DIFFERENCES FROM THE AAAI BUILD, each of which cost a failed run:

  1. `elsarticle` is a CTAN class, not a downloaded author kit.  Nothing is
     fetched; a TeX distribution supplies it.  MiKTeX installs it on first
     use if `--enable-installer` is passed, which it is.
  2. The bibliography style is `elsarticle-harv`, set by the DOCUMENT, not
     by the class.  The AAAI class set its own and a second
     \\bibliographystyle was an error there; here its absence is the error.
  3. `elsarticle` does not load `amsmath`, and \\text inside math needs it.
  4. Elsevier wants the preprint option for a submission PDF; the journal's
     own production run uses a different option and is not our business.

Usage:  python scripts/build_journal.py [--outdir DIR]

Exit status is non-zero on any LaTeX error, any undefined reference, or a
missing PDF, so this is usable as a gate in a reproduction script.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
STEM = "iaai27_empty_cmdb"


def find(prog):
    exe = shutil.which(prog)
    if exe:
        return exe
    for c in (Path.home() / f"AppData/Local/Programs/MiKTeX/miktex/bin/x64/{prog}.exe",
              Path(f"C:/Program Files/MiKTeX/miktex/bin/x64/{prog}.exe"),
              Path(f"/usr/bin/{prog}")):
        if c.exists():
            return str(c)
    sys.exit(f"{prog} not found.  Install MiKTeX or TeX Live and retry.")


def run(cmd, cwd, log):
    with open(cwd / log, "w", encoding="utf-8", errors="replace") as fh:
        subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    return (cwd / log).read_text(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "build" / "journal"))
    a = ap.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    pdflatex, bibtex = find("pdflatex"), find("bibtex")

    for f in [f"{STEM}.tex", "references.bib"] + \
             [p.name for p in sorted(PAPER.glob("*.png"))]:
        shutil.copy2(PAPER / f, out / f)
    for f in out.glob(f"{STEM}.*"):
        if f.suffix in (".aux", ".bbl", ".blg", ".pdf", ".log"):
            f.unlink()

    tex = [pdflatex, "-interaction=nonstopmode", "--enable-installer",
           f"{STEM}.tex"]
    run(tex, out, "p1.log")
    blog = run([bibtex, STEM], out, "b1.log")
    if "I couldn't open" in blog or "Illegal" in blog:
        print(blog)
        sys.exit("bibtex failed")
    run(tex, out, "p2.log")
    log = run(tex, out, "p3.log")

    errs = [l for l in log.splitlines() if l.startswith("!")]
    undef = [l for l in log.splitlines()
             if "Warning" in l and "undefined" in l.lower()]
    over = [l for l in log.splitlines() if l.startswith("Overfull \\hbox")]
    pdf = out / f"{STEM}.pdf"
    if errs or not pdf.exists():
        print("\n".join(errs) or "no PDF produced")
        sys.exit("BUILD FAILED")

    pages = next((l for l in log.splitlines() if "Output written" in l), "")
    m = re.search(r"\((\d+) pages", pages)
    print(f"OK  {pdf}")
    print(f"    {pages.strip()}")
    print(f"    {len(over)} overfull hboxes")
    shutil.copy2(pdf, PAPER / f"{STEM}.pdf")
    print(f"    copied to {PAPER / f'{STEM}.pdf'}")
    if undef:
        print(f"    {len(undef)} UNDEFINED reference/citation warnings:")
        for u in undef[:10]:
            print(f"      {u.strip()}")
        sys.exit("undefined references -- fix before submitting")
    print(f"    0 errors, 0 undefined references"
          + (f", {m.group(1)} pages" if m else ""))


if __name__ == "__main__":
    main()

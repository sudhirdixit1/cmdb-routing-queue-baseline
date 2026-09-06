"""Build the Information Systems (Elsevier) submission PDF.

The document was retargeted from IAAI-27 to Information Systems in round
fifteen; `scripts/build_paper.py` builds the superseded AAAI version and is
kept only so that version stays reproducible.  This script is the current
one.

DIFFERENCES FROM THE AAAI BUILD, each of which cost a failed run:

  1. `elsarticle` is a CTAN class, not a downloaded author kit.  Nothing is
     fetched; a TeX distribution supplies it.  MiKTeX installs it on first
     use if `--enable-installer` is passed, which it is.
  2. The bibliography style is `elsarticle-num`, set by the DOCUMENT, not
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

#  ROUND SEVENTEEN.  attack_verifier.py rewrites the manuscript once per
#  corruption and restores it in a finally block.  Anything that reads the
#  manuscript while that is happening is reading a CORRUPTED file.  Round
#  sixteen had a build and a verification do it; round seventeen had a
#  `git add -A` commit one.  A docstring is not a control, so this is:
_SUITE_LOCK = Path(__file__).resolve().parent.parent / "paper" / ".tex.bak"
if _SUITE_LOCK.exists():
    sys.exit(
        f"REFUSING TO RUN: {_SUITE_LOCK} exists, which means attack_verifier.py\n"
        "is running or was killed mid-flight.  If it is running, wait.  If it\n"
        "was killed, the manuscript on disk is CORRUPTED -- restore it first:\n"
        f"    cp {_SUITE_LOCK} {_SUITE_LOCK.with_name('iaai27_empty_cmdb.tex')}\n"
        f"    rm {_SUITE_LOCK}")
PAPER = ROOT / "paper"
STEM = "specification_surfaces"


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
    global STEM
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "build" / "journal"))
    ap.add_argument("--paper", default=None,
                    help="stem of the .tex to build; default is the "
                         "round-nineteen manuscript")
    a = ap.parse_args()
    if a.paper:
        STEM = a.paper
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    pdflatex, bibtex = find("pdflatex"), find("bibtex")

    #  ROUND TWENTY-ONE.  Two documents now: the article and its supplement,
    #  which reference each other through `xr'.  Both are copied, both are
    #  built, and the article is built again afterwards so that a reference
    #  to a supplement section resolves to the number the supplement settled
    #  on rather than to the one it had on the first pass.
    supp = "supplement" if (PAPER / "supplement.tex").exists() else None
    for f in [f"{STEM}.tex", "references.bib"] + \
             ([f"{supp}.tex"] if supp else []) + \
             [p.name for p in sorted(PAPER.glob("*.png"))]:
        shutil.copy2(PAPER / f, out / f)
    #  ROUND NINETEEN.  The manuscript \input's a GENERATED macro file and a
    #  directory of GENERATED tables, and the appendices \input the section
    #  parts.  A build that copies only the .tex and the images fails on the
    #  first \input, which is what happened the first time this ran.
    if (PAPER / "numbers.tex").exists():
        shutil.copy2(PAPER / "numbers.tex", out / "numbers.tex")
    for sub in ("tables", "parts"):
        if (PAPER / sub).exists():
            (out / sub).mkdir(exist_ok=True)
            for f in (PAPER / sub).glob("*.tex"):
                shutil.copy2(f, out / sub / f.name)
    for stem in [STEM] + ([supp] if supp else []):
        for f in out.glob(f"{stem}.*"):
            if f.suffix in (".aux", ".bbl", ".blg", ".pdf", ".log"):
                f.unlink()

    def tex_for(stem):
        return [pdflatex, "-interaction=nonstopmode", "--enable-installer",
                f"{stem}.tex"]

    def build_one(stem, tag):
        run(tex_for(stem), out, f"{tag}1.log")
        blog = run([bibtex, stem], out, f"{tag}b.log")
        if "I couldn't open" in blog or "Illegal" in blog:
            print(blog)
            sys.exit(f"bibtex failed on {stem}")
        #  `elsarticle-num' writes every DOI as \href{URL}{\path{doi:...}},
        #  which needs hyperref; neither document loads it, and a fallback
        #  that takes two arguments hands \path a DOI whose underscore has
        #  already been read as a subscript, which is a LaTeX error in the
        #  reference list.  The DOI is kept and the link wrapper removed, so
        #  \path reads the DOI itself, as it does under `elsarticle-harv'.
        bbl = out / f"{stem}.bbl"
        if bbl.exists():
            t = bbl.read_text(encoding="utf-8")
            t2 = re.sub(r"\\href\s*\{[^{}]*\}\s*\{(\\path\{[^{}]*\})\}", r"\1", t)
            #  the same .bbl replaces \path by an identity macro whenever
            #  \href is undefined, which is what typesets the underscore as a
            #  subscript; the url package's \path is kept instead
            t2 = t2.replace("\\def\\path#1{#1}", "")
            if t2 != t:
                bbl.write_text(t2, encoding="utf-8")
        run(tex_for(stem), out, f"{tag}2.log")
        return run(tex_for(stem), out, f"{tag}3.log")

    log = build_one(STEM, "p")
    if supp:
        slog = build_one(supp, "s")
        #  the article again, now that the supplement's numbers exist, and
        #  the supplement again, now that the article's do
        log = build_one(STEM, "p")
        slog = build_one(supp, "s")
        serrs = [l for l in slog.splitlines() if l.startswith("!")]
        sundef = [l for l in slog.splitlines()
                  if "Warning" in l and "undefined" in l.lower()
                  and "Font" not in l]
        spdf = out / f"{supp}.pdf"
        if serrs or not spdf.exists():
            print("\n".join(serrs) or "no supplement PDF produced")
            sys.exit("SUPPLEMENT BUILD FAILED")
        spages = next((l for l in slog.splitlines()
                       if "Output written" in l), "")
        shutil.copy2(spdf, PAPER / f"{supp}.pdf")
        print(f"OK  {spdf}")
        print(f"    {spages.strip()}")
        #  ROUND TWENTY-TWO.  This line reported the ARTICLE's overfull boxes
        #  and nothing else, so seventy cells spilling past their column edge
        #  in the supplement sat unreported through four rounds.  A build
        #  summary that checks one of two documents is worse than none.
        sover = [l for l in slog.splitlines()
                 if l.startswith("Overfull \\hbox")]
        print(f"    {len(sover)} overfull hboxes in the supplement")
        #  ROUND TWENTY-FIVE.  A float TALLER than its page is not an
        #  overfull hbox, so the check above cannot see one.  A table that
        #  grew from nineteen rows to thirty-eight ran off the bottom of its
        #  page with the page number printed through it, and this summary
        #  said `0 overfull hboxes' about it.  Both documents are scanned.
        sbig = [l for l in slog.splitlines() if "Float too large" in l]
        print(f"    {len(sbig)} floats too large for their page "
              f"in the supplement")
        for u in sbig[:6]:
            print(f"      {u.strip()}")
        if sundef:
            print(f"    {len(sundef)} UNDEFINED in supplement:")
            for u in sundef[:10]:
                print(f"      {u.strip()}")
            sys.exit("undefined references in the supplement")

    errs = [l for l in log.splitlines() if l.startswith("!")]
    #  A `Font shape ... undefined' warning is a substitution, not a broken
    #  cross-reference, and treating it as one made the gate fire on a build
    #  whose references were all resolved.  Font problems are still reported,
    #  separately, because they are worth fixing -- they just are not this
    #  gate's business.
    warn = [l for l in log.splitlines() if "Warning" in l]
    undef = [l for l in warn
             if "undefined" in l.lower() and "Font" not in l]
    fonts = [l for l in warn if "Font" in l and "undefined" in l.lower()]
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
    big = [l for l in log.splitlines() if "Float too large" in l]
    print(f"    {len(big)} floats too large for their page")
    for u in big[:6]:
        print(f"      {u.strip()}")
    if fonts:
        print(f"    {len(fonts)} font-shape substitutions (not references):")
        for u in fonts[:4]:
            print(f"      {u.strip()}")
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

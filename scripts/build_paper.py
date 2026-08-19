"""Build the submission PDF.

The AAAI style files are NOT redistributed in this repository.  This script
fetches the official AAAI-27 author kit into a scratch build directory,
copies aaai2027.sty and aaai2027.bst next to the sources, and runs the
pdflatex -> bibtex -> pdflatex -> pdflatex sequence AAAI requires.

Three things this build caught that a structural lint cannot, recorded here
so they are not reintroduced:

  1. The kit ships aaai2027.sty / aaai2027.bst, not aaai27.*  An earlier
     preamble named the short form and would not have resolved.
  2. aaai2027.sty issues its own \\bibliographystyle.  A second one in the
     document makes bibtex fail with "Illegal, another \\bibstyle command"
     and silently leaves the references unresolved.
  3. aaai2027.sty loads newtxtext, helvet and courier itself and sets the
     PDF page size itself.  It explicitly forbids \\usepackage{times}.

Usage:  python scripts/build_paper.py [--outdir DIR]
"""
import argparse
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
STEM = "iaai27_empty_cmdb"
KIT_URL = "https://aaai.org/authorkit27/"
NEEDED = ("aaai2027.sty", "aaai2027.bst")


def find_pdflatex():
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    for c in (Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe",
              Path("C:/Program Files/MiKTeX/miktex/bin/x64/pdflatex.exe")):
        if c.exists():
            return str(c)
    sys.exit("pdflatex not found.  Install MiKTeX or TeX Live and retry.\n"
             "AAAI requires pdflatex: the mandated \\pdfinfo block is a "
             "pdfTeX primitive, so xelatex/tectonic will not do.")


def fetch_kit(dest: Path):
    """Download and unpack the author kit, unless the style files are present."""
    if all((dest / n).exists() for n in NEEDED):
        return
    zp = dest / "AuthorKit27.zip"
    print(f"fetching author kit from {KIT_URL}")
    # aaai.org's WAF rejects urllib's default user-agent, and also rejects a
    # spoofed "Mozilla/5.0".  It accepts an honest command-line client string.
    req = urllib.request.Request(KIT_URL, headers={"User-Agent": "curl/8.0.1"})
    with urllib.request.urlopen(req, timeout=120) as r, open(zp, "wb") as fh:
        shutil.copyfileobj(r, fh)
    with zipfile.ZipFile(zp) as z:
        for member in z.namelist():
            name = Path(member).name
            if name in NEEDED:
                with z.open(member) as src, open(dest / name, "wb") as out:
                    shutil.copyfileobj(src, out)
                print(f"  extracted {name}")
    missing = [n for n in NEEDED if not (dest / n).exists()]
    if missing:
        sys.exit(f"author kit did not contain: {', '.join(missing)}")


def run(cmd, cwd, log):
    with open(cwd / log, "w", encoding="utf-8", errors="replace") as fh:
        subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    return (cwd / log).read_text(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "build"))
    a = ap.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    pdflatex = find_pdflatex()
    bibtex = str(Path(pdflatex).with_name("bibtex.exe")) \
        if Path(pdflatex).with_name("bibtex.exe").exists() else "bibtex"

    for f in (f"{STEM}.tex", "references.bib", "figG1_baselines.png"):
        shutil.copy2(PAPER / f, out / f)
    fetch_kit(out)

    for f in out.glob(f"{STEM}.*"):
        if f.suffix in (".aux", ".bbl", ".blg", ".pdf", ".log"):
            f.unlink()

    tex = [pdflatex, "-interaction=nonstopmode", "--enable-installer", f"{STEM}.tex"]
    run(tex, out, "pass1.log")
    blog = run([bibtex, STEM], out, "bibtex.log")
    if "Illegal" in blog or "I couldn't open" in blog:
        print(blog)
        sys.exit("bibtex failed -- see the header of this file for the "
                 "\\bibliographystyle trap.")
    run(tex, out, "pass2.log")
    log = run(tex, out, "pass3.log")

    errs = [l for l in log.splitlines() if l.startswith("!")]
    undef = [l for l in log.splitlines()
             if "Warning" in l and "undefined" in l.lower()]
    pdf = out / f"{STEM}.pdf"
    if errs or not pdf.exists():
        print("\n".join(errs) or "no PDF produced")
        sys.exit("BUILD FAILED")

    pages = next((l for l in log.splitlines() if "Output written" in l), "")
    print(f"OK  {pdf}")
    print(f"    {pages.strip()}")
    if undef:
        print(f"    {len(undef)} undefined reference/citation warnings:")
        for u in undef[:5]:
            print(f"      {u.strip()}")
    shutil.copy2(pdf, PAPER / f"{STEM}.pdf")
    print(f"    copied to {PAPER / f'{STEM}.pdf'}")


if __name__ == "__main__":
    main()

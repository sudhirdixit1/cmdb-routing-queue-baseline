"""make_cover_pdf -- typeset submission/cover_letter.md as a PDF for upload.

    python scripts/make_cover_pdf.py

Editorial Manager takes the cover letter as a file or pasted text; a .md file
would show its asterisks and backticks to the editor.  This converts the few
Markdown constructs the letter uses (headings are not used; **bold**,
*italic*, `code`, --- dashes, a horizontal rule, the header lines) to LaTeX
and builds build/journal/cover_letter.pdf.  The letter itself stays the one
source; this file is a typesetter, not a second copy.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "submission" / "cover_letter.md"
OUT = ROOT / "build" / "journal"


def esc(t):
    t = t.replace("\\", r"\textbackslash{}")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("$", r"\$"), ("{", r"\{"), ("}", r"\}"), ("~", r"\~{}"),
                 ("^", r"\^{}")):
        t = t.replace(a, b)
    return t


def inline(t):
    codes = []
    t = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or
               "\x00%d\x00" % (len(codes) - 1), t)
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"\*(.+?)\*", r"\\emph{\1}", t)
    t = t.replace("---", "---")
    t = re.sub(r"\x00(\d+)\x00",
               lambda m: r"\texttt{%s}" % esc(codes[int(m.group(1))])
               .replace("/", r"/\allowbreak{}"), t)
    t = re.sub(r'"(.+?)"', r"``\1''", t)
    return t


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    body, para = [], []

    def flush():
        if para:
            body.append(inline(" ".join(para)) + "\n")
            para.clear()
    for ln in lines:
        if ln.startswith("# "):
            continue
        if ln.strip() == "---":
            flush()
            body.append(r"\medskip\hrule\medskip" + "\n")
        elif not ln.strip():
            flush()
        elif ln.startswith("**To:**") or ln.startswith("**Manuscript:**") \
                or ln.startswith("**Author:**"):
            flush()
            para.append(ln)
            body.append("")
        else:
            para.append(ln.strip())
    flush()
    tex = (r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage[utf8]{inputenc}
\usepackage[margin=2.5cm]{geometry}\usepackage{microtype}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.6em}
\pagestyle{plain}
\begin{document}
""" + "\n".join(body) + "\n\\end{document}\n")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cover_letter.tex").write_text(tex, encoding="utf-8")
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode",
                            "cover_letter.tex"], cwd=OUT,
                           capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout[-2000:])
    print("OK  %s" % (OUT / "cover_letter.pdf"))


if __name__ == "__main__":
    main()

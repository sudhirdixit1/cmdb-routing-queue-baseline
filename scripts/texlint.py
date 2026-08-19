"""Structural lint for the LaTeX source, and a repair for row terminators.

The seventh draft shipped with Table 2's rows terminated by a single
backslash instead of a double.  In a two-column tabular that raises "Extra
alignment tab has been changed to \\cr" and the document does not build --
while verify_paper.py reported "92 checks passed, 0 failed" on it.  A
checker that certifies an unbuildable file is checking the wrong artifact.

Run with --fix to repair, without to lint.
"""
import re
import sys
from pathlib import Path

TEX = Path(__file__).resolve().parent.parent / "paper" / "iaai27_empty_cmdb.tex"
ROW_END = "\\" + "\\"          # a LaTeX row terminator, written defensively


def tabular_blocks(src):
    return list(re.finditer(r"\\begin\{tabular\}(.*?)\\end\{tabular\}", src, re.S))


def bad_rows(src):
    out = []
    for m in tabular_blocks(src):
        start = src[:m.start()].count("\n") + 1
        for i, ln in enumerate(m.group(1).split("\n")):
            t = ln.rstrip()
            if "&" not in t or "multicolumn" in t:
                continue
            if not t.endswith(ROW_END):
                out.append((start + i + 1, t[:64]))
    return out


def continuation_rows(src):
    """A row wrapped across two lines: the second line carries the &."""
    return None


def fix(src):
    def repair(m):
        body = m.group(1)
        lines = body.split("\n")
        for i, ln in enumerate(lines):
            t = ln.rstrip()
            if not t or "multicolumn" in t:
                continue
            if t.endswith(ROW_END) or t.endswith("{"):
                continue
            # a data row ends with a single backslash where it needs two
            if t.endswith("\\") and not t.endswith(ROW_END):
                lines[i] = t + "\\"
        return "\\begin{tabular}" + "\n".join(lines) + "\\end{tabular}"
    return re.sub(r"\\begin\{tabular\}(.*?)\\end\{tabular\}", repair, src, flags=re.S)


def check_other(src):
    problems = []
    for env in ("table", "figure", "tabular", "itemize", "enumerate", "abstract"):
        o = len(re.findall(r"\\begin\{" + env + r"\}", src))
        c = len(re.findall(r"\\end\{" + env + r"\}", src))
        if o != c:
            problems.append(f"unbalanced {env}: {o} begin, {c} end")
    if src.count("$") % 2:
        problems.append(f"odd number of $ delimiters ({src.count('$')})")
    for cmd in ("\\label", "\\ref", "\\cite"):
        for m in re.finditer(re.escape(cmd) + r"\{([^}]*)\}", src):
            if not m.group(1).strip():
                problems.append(f"empty {cmd}{{}}")
    labels = set(re.findall(r"\\label\{([^}]*)\}", src))
    refs = set(re.findall(r"\\ref\{([^}]*)\}", src))
    for r in refs - labels:
        problems.append(f"\\ref to undefined label: {r}")
    return problems


if __name__ == "__main__":
    src = TEX.read_text(encoding="utf-8")
    if "--fix" in sys.argv:
        TEX.write_text(fix(src), encoding="utf-8")
        src = TEX.read_text(encoding="utf-8")
        print("repaired")
    br = bad_rows(src)
    other = check_other(src)
    print(f"tabular rows not ending in a row terminator: {len(br)}")
    for ln, t in br:
        print(f"   line {ln}: {t}")
    print(f"other structural problems: {len(other)}")
    for o in other:
        print("   ", o)
    sys.exit(1 if (br or other) else 0)

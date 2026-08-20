"""Corruption suite for verify_paper.py.

Run as a regression test.  Each entry perturbs the paper in a way an earlier
version of the verifier failed to catch, then asserts the verifier now fails.
Whitespace in the search strings is normalised, because LaTeX wraps lines and
a naive replace silently no-ops -- which produced a false "PASSED" in an
earlier run of this suite and briefly looked like a verifier hole.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"
BAK = ROOT / "paper" / ".tex.bak"

CORRUPTIONS = [
    ("sign flip, headline gain", "& $+0.183$ [", "& $-0.183$ ["),
    ("sign flip, queue-unique", r"$\mathbf{+0.002}$", r"$\mathbf{-0.002}$"),
    ("swap table-1 AUCs", "intake only & 0.562 & 0.746", "intake only & 0.644 & 0.746"),
    ("swap train/test n", "$31{,}818$ training and", "$13{,}637$ training and"),
    ("swap mirror pair", "retains $91\\%$ of the queue's", "retains $2\\%$ of the queue's"),
    ("corrupt mirror floor", "retains $2\\%$. The margin", "retains $9\\%$. The margin"),
    ("corrupt scope top-64", "$64$ recover $90.0\\%$", "$64$ recover $70.0\\%$"),
    ("corrupt scope top-8", "top $8$ recover $57.9\\%$", "top $8$ recover $27.9\\%$"),
    ("corrupt design range", "ranges $+0.068$ to", "ranges $+0.088$ to"),
    ("corrupt queue-unique CI", "$[+0.0001,+0.0034]$", "$[+0.0010,+0.0034]$"),
    ("corrupt null", "$-0.0009 \\pm 0.0006$", "$-0.0019 \\pm 0.0006$"),
    ("corrupt cohort figure", "$92.56\\%$", "$95.56\\%$"),
    ("break a tabular row", "& $+0.082$ \\\\", "& $+0.082$ \\"),
    ("fabricated literal", "before funding anything.",
     "before funding anything, across $737$ sites."),
    # -- second task (r9).  A new claim gets the same treatment as an old one.
    ("swap the reopen gain pair",
     "worth $+0.083$ against the intake block and $+0.055$",
     "worth $+0.055$ against the intake block and $+0.083$"),
    ("inflate reopen shrinkage", "a reduction of $33\\%$", "a reduction of $53\\%$"),
    ("corrupt long-handling gain", "figures are $+0.118$ and $+0.078$",
     "figures are $+0.148$ and $+0.078$"),
    ("corrupt reopen positives", "fires on $2{,}096$ incidents",
     "fires on $3{,}096$ incidents"),
    ("overstate target independence",
     "correlates with reassignment at $+0.14$",
     "correlates with reassignment at $+0.04$"),
    ("overstate reopen evidence", "stand $5.5$ and $4.2$ pooled",
     "stand $25.5$ and $4.2$ pooled"),
    ("widen the shrinkage range", "ranges from $30\\%$ to $46\\%$",
     "ranges from $40\\%$ to $46\\%$"),
]


def flat(s):
    return re.sub(r"\s+", " ", s)


def apply(src, old, new):
    """Replace ignoring how LaTeX happened to wrap the line."""
    f_src, f_old = flat(src), flat(old)
    i = f_src.find(f_old)
    if i < 0:
        return None
    # walk the original string counting non-space characters to find the span
    def span(target_idx):
        seen = j = 0
        while j < len(src):
            if not src[j].isspace():
                if seen == target_idx:
                    return j
                seen += 1
            elif j and not src[j - 1].isspace():
                seen += 1
            j += 1
        return len(src)
    nonspace_before = len(flat(f_src[:i]).replace(" ", ""))
    # simpler: rebuild by regex allowing arbitrary whitespace between tokens
    pat = r"\s+".join(re.escape(t) for t in old.split())
    m = re.search(pat, src)
    if not m:
        return None
    return src[:m.start()] + new + src[m.end():]


def run():
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_paper.py")],
                          capture_output=True, text=True).returncode


shutil.copy(TEX, BAK)
caught = missed = skipped = 0
try:
    for name, old, new in CORRUPTIONS:
        src = BAK.read_text(encoding="utf-8")
        out = apply(src, old, new)
        if out is None or out == src:
            print(f"  SKIP     {name}  (pattern not found -- test is stale)")
            skipped += 1
            continue
        TEX.write_text(out, encoding="utf-8")
        if run() != 0:
            print(f"  caught   {name}")
            caught += 1
        else:
            print(f"  MISSED   {name}")
            missed += 1
finally:
    shutil.copy(BAK, TEX)
    BAK.unlink()

print(f"\n{caught} caught, {missed} missed, {skipped} skipped "
      f"of {len(CORRUPTIONS)}")
sys.exit(1 if (missed or skipped) else 0)

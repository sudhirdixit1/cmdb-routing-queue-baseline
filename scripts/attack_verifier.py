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
    ("corrupt scope top-64", "$64$ recover $88\\%$", "$64$ recover $68\\%$"),
    ("corrupt scope top-8", "top $8$ recover $56\\%$", "top $8$ recover $26\\%$"),
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

    # -- r10, estimator families.  The point of these rows is that the effect
    #    is not an artifact of one estimator, so an inflated range or a hidden
    #    encoder null is exactly the corruption that would matter.
    ("swap the estimator range endpoints",
     "the first rung ranges $+0.173$ to $+0.183$",
     "the first rung ranges $+0.183$ to $+0.173$"),
    ("narrow the estimator shrinkage",
     "the shrinkage $43\\%$ to $47\\%$", "the shrinkage $43\\%$ to $44\\%$"),
    ("hide the boosting encoder null",
     "$+0.0042 \\pm 0.0020$", "$+0.0002 \\pm 0.0020$"),
    # This one is a real defect that shipped: HANDOFF quoted the max_bins
    # PARAMETER (256) where r5_binning computes 137 distinct bins.
    ("restore the wrong bin count", "into $137$ bins", "into $256$ bins"),

    # -- r11, the operational translation.
    ("swap a capacity row's caught counts",
     "$1{,}119$ & $1{,}153$", "$1{,}153$ & $1{,}119$"),
    ("corrupt the naive catch count",
     "with $303$, $432$ and $501$ instead", "with $303$, $832$ and $501$ instead"),
    ("swap the precision pair",
     "precision from $82.0\\%$ to $84.5\\%$", "precision from $84.5\\%$ to $82.0\\%$"),
    ("inflate the overstatement factor",
     "by a factor of $12.7$", "by a factor of $22.7$"),
    ("corrupt the abstract's detection factor",
     "baseline attributes $12.7$ times", "baseline attributes $19.7$ times"),
    ("understate the AUC ratio it is contrasted with",
     "gains, which is $1.8$", "gains, which is $1.2$"),
    ("swap the threshold ladder pair",
     "gives $+0.131$ and $+0.068$", "gives $+0.068$ and $+0.131$"),
    ("narrow the threshold shrinkage band",
     "between $44\\%$ and $48\\%$", "between $44\\%$ and $45\\%$"),

    # -- r12/r13, the queue's shape and the model-free mechanism.  The
    #    balanced-accuracy figure is the one that keeps the mechanism claim
    #    honest, so removing it is the most damaging single edit available.
    ("hide the class-balanced lookup accuracy",
     "class-balanced it reaches only $34.1\\%$",
     "class-balanced it reaches only $74.1\\%$"),
    ("overstate what the item tells you about the queue",
     "carries $60.4\\%$ of the queue's information",
     "carries $90.4\\%$ of the queue's information"),
    ("swap the asymmetry direction",
     "carries $60.4\\%$ of the queue's information and the queue carries "
     "$19.6\\%$",
     "carries $19.6\\%$ of the queue's information and the queue carries "
     "$60.4\\%$"),
    ("understate the queue's concentration",
     "largest group holding $62.1\\%$", "largest group holding $22.1\\%$"),
    ("swap the dominant-pool reassignment rates",
     "$0.309$ inside the dominant pool and $0.603$ outside",
     "$0.603$ inside the dominant pool and $0.309$ outside"),
    ("flatten the dose-response",
     "shrinkages of $27\\%$, $28\\%$, $36\\%$ and $44\\%$",
     "shrinkages of $41\\%$, $28\\%$, $36\\%$ and $44\\%$"),
    ("corrupt the abstract's dose-response floor",
     "rising from $27\\%$ when the queue", "rising from $17\\%$ when the queue"),
    ("overstate what one bit recovers",
     "recovers $61\\%$ of the queue's baseline gain",
     "recovers $91\\%$ of the queue's baseline gain"),

    # -- r14, scoping.  The across-split band is what stops a single split's
    #    curve being read as an estimate, so shrinking it is the attack.
    ("shrink the scoping band", "$88\\%$ $[82,92]$", "$88\\%$ $[87,89]$"),
    ("corrupt the across-split spread",
     "across-split spread is $9$ points", "across-split spread is $2$ points"),
    ("corrupt scoping without the queue", "--- $89\\%$ at $k=64$",
     "--- $69\\%$ at $k=64$"),

    # -- r15.  The single-organisation justification rests on this rate: if it
    #    were 20% rather than 0.2%, a second organisation would be available
    #    and "constraint rather than choice" would be false.
    ("overstate the second log's item population",
     "the second records it on $0.2\\%$", "the second records it on $20\\%$"),
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

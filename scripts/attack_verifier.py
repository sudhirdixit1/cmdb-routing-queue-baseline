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
    ("sign flip, group-unique",
     "and $+0.002$ once the item is present",
     "and $-0.002$ once the item is present"),
    ("swap table-1 AUCs", "intake only & 0.562 & 0.746", "intake only & 0.644 & 0.746"),
    ("swap train/test n", "$31{,}818$ training and", "$13{,}637$ training and"),
    ("swap mirror pair", "retains $91\\%$ of the group's", "retains $41\\%$ of the group's"),
    ("corrupt the withdrawn floor we quote as history",
     "against a floor of $2\\%$", "against a floor of $9\\%$"),
    ("corrupt scope top-64", "$64$ recover $88\\%$", "$64$ recover $68\\%$"),
    ("corrupt scope top-8", "top $8$ recover $56\\%$", "top $8$ recover $26\\%$"),
    ("corrupt design range", "ranges $+0.068$ to", "ranges $+0.088$ to"),
    ("corrupt queue-unique CI", "$[+0.0001,+0.0034]$", "$[+0.0010,+0.0034]$"),
    ("corrupt null", "$-0.0009 \\pm 0.0005$", "$-0.0019 \\pm 0.0005$"),
    ("corrupt cohort figure", "$92.56\\%$", "$95.56\\%$"),
    ("break a tabular row",
     "& $+262$ [$242,300$] & $3.9$ [$3.2,6.4$] \\\\",
     "& $+262$ [$242,300$] & $3.9$ [$3.2,6.4$] \\"),
    ("fabricated literal", "before funding anything.",
     "before funding anything, across $737$ sites."),
    # -- second task (r9).  A new claim gets the same treatment as an old one.
    ("swap the reopen gain pair",
     "worth $+0.083$ against the intake block and $+0.055$",
     "worth $+0.055$ against the intake block and $+0.083$"),
    ("inflate reopen shrinkage", "a reduction of $33\\%$", "a reduction of $53\\%$"),
    ("corrupt long-handling gain", "on long handling, $+0.118$ and $+0.078$",
     "on long handling, $+0.148$ and $+0.078$"),
    ("corrupt reopen positives", "fires on $2{,}096$ incidents",
     "fires on $3{,}096$ incidents"),
    ("overstate target independence",
     "correlates with reassignment at $+0.14$",
     "correlates with reassignment at $+0.04$"),
    ("overstate reopen evidence", "stand only $5.5$ and $4.2$ pooled",
     "stand only $25.5$ and $4.2$ pooled"),
    ("widen the second-task shrinkage range",
     "ranges from $30\\%$ to $39\\%$ on these two targets",
     "ranges from $40\\%$ to $39\\%$ on these two targets"),

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
    ("swap a capacity row's two arms",
     "$+67$ [$43,84$] & $+262$", "$+262$ [$43,84$] & $+67$"),
    ("corrupt a naive catch count",
     "$+353$ [$304,404$]", "$+853$ [$304,404$]"),
    ("inflate the honest detection gain",
     "surfaces $67$ $[43,84]$ more", "surfaces $167$ $[43,84]$ more"),
    ("inflate the overstatement factor",
     "by a factor of $3.9$ $[3.2,6.4]$", "by a factor of $9.3$ $[3.2,6.4]$"),
    ("corrupt the abstract's detection factor",
     "credits the CMDB with $3.9$", "credits the CMDB with $13.9$"),
    ("understate the AUC ratio it is contrasted with",
     "against a ratio of only $1.8$", "against a ratio of only $1.1$"),
    ("swap the threshold ladder pair",
     "gives $+0.131$ and $+0.068$", "gives $+0.068$ and $+0.131$"),
    # Range endpoints floor and ceil; narrowing either makes the stated
    # range untrue, which ck_bound now catches.
    ("narrow the threshold shrinkage band",
     "between $43\\%$ and $49\\%$", "between $44\\%$ and $48\\%$"),

    # -- r12/r13, the queue's shape and the model-free mechanism.  The
    #    balanced-accuracy figure is the one that keeps the mechanism claim
    #    honest, so removing it is the most damaging single edit available.
    ("hide the class-balanced lookup accuracy",
     "class-balanced reaches only $34.1\\%$",
     "class-balanced reaches only $74.1\\%$"),
    ("overstate what the item tells you about the group",
     "carries $60.4\\%$ of the opening group's",
     "carries $90.4\\%$ of the opening group's"),
    ("swap the asymmetry direction",
     "carries $60.4\\%$ of the opening group's information and the group "
     "carries $19.6\\%$",
     "carries $19.6\\%$ of the opening group's information and the group "
     "carries $60.4\\%$"),
    ("understate the field's concentration",
     "largest group holds $62.1\\%$", "largest group holds $22.1\\%$"),
    ("swap the two shares that show the field is an actor stamp",
     "$67.0\\%$ of \\texttt{Open} rows but only $18.4\\%$",
     "$18.4\\%$ of \\texttt{Open} rows but only $67.0\\%$"),
    ("flatten the dose-response",
     "shrinkages of $27\\%$, $28\\%$, $36\\%$ and $44\\%$",
     "shrinkages of $41\\%$, $28\\%$, $36\\%$ and $44\\%$"),
    ("corrupt the abstract's dose-response floor",
     "running $27\\%$ to $44\\%$", "running $7\\%$ to $44\\%$"),
    ("overstate what one bit recovers",
     "recovers $61\\%$ of the group's baseline gain",
     "recovers $91\\%$ of the group's baseline gain"),

    # -- r14, scoping.  The across-split band is what stops a single split's
    #    curve being read as an estimate, so shrinking it is the attack.
    ("shrink the scoping band",
     "range over $53$--$58$, $82$--$92$", "range over $55$--$57$, $87$--$89$"),
    ("corrupt the across-split spread",
     "across-split spread is $9$ points", "across-split spread is $2$ points"),
    ("corrupt scoping without the group", "--- $89\\%$ at $k=64$",
     "--- $69\\%$ at $k=64$"),

    # -- r15.  The single-organisation justification rests on this rate: if it
    #    were 20% rather than 0.2%, a second organisation would be available
    #    and "constraint rather than choice" would be false.
    ("overstate the second log's item population",
     "the second records it on $0.2\\%$", "the second records it on $20\\%$"),
    # -- r16.  The field re-characterisation is the correction that cost the
    #    paper its title.  Each of the three structural facts is attacked,
    #    because reversing any one of them restores the wrong reading.
    ("hide that Open rows are less diverse than Assignment rows",
     "rows carry $218$", "rows carry $18$"),
    ("reverse the agreement with the first Assignment",
     "activity for just $15.1\\%$", "activity for just $85.1\\%$"),
    ("shrink the delay that makes real routing inadmissible",
     "a median of $46$ minutes later", "a median of $4$ minutes later"),
    ("corrupt the count of incidents with no Assignment at all",
     "$7{,}878$ of $45{,}455$", "$1{,}878$ of $45{,}455$"),
    ("understate the drift in the free field",
     "falls from $49$ to $32$", "falls from $49$ to $42$"),

    # -- r17.  The rebuilt floor corrects a null that could not fail;
    #    understating it would restore the withdrawn 89-point margin.
    ("understate the rebuilt floor",
     "$41\\%$ at $49$ cells", "$11\\%$ at $49$ cells"),
    ("understate the floor at fine granularity",
     "$77\\%$ at $400$", "$47\\%$ at $400$"),
    ("inflate the honest margin",
     "a margin of $50$ points", "a margin of $80$ points"),

    # -- the widest capacity's interval includes zero, which is why the paper
    #    quotes the 5% figure instead.  Hiding that is the attack.
    ("hide that the widest capacity's interval includes zero",
     "$+18$ [$-28,82$]", "$+18$ [$8,82$]"),
    # -- round three.  Each of these is a control a referee had to compute
    #    because the paper had not, so each gets its own corruption.
    ("hide the finite-sample floor under the MI figures",
     "leaves floors of $14.0\\%$ and $4.5\\%$",
     "leaves floors of $1.0\\%$ and $4.5\\%$"),
    ("swap the MI excesses",
     "survives with $46$ points against $15$",
     "survives with $15$ points against $46$"),
    ("understate what admitting the service component costs",
     "takes the measured value to $+0.023$",
     "takes the measured value to $+0.093$"),
    ("overstate how much hour and day of week move it",
     "from $+0.103$ to $+0.099$", "from $+0.103$ to $+0.049$"),
    ("hide that the routing-blind floor beats the real leg",
     "partition of items retains \\emph{more}, $55\\%$",
     "partition of items retains less, $15\\%$"),
    # Deleting this caveat would restore an ordering that holds by
    # construction: at one cell per item the null IS the real leg.
    ("delete the caveat that the ordering is structural",
     "at one cell\nper item the null \\emph{is} the real leg",
     "at one cell\nper item the null is unrelated to the real leg"),
    ("misstate the capacity table's bootstrap draws",
     "re-ranked in each draw and use $400$",
     "re-ranked in each draw and use $4000$"),
    # -- round four.
    ("delete the engagement with the free-field objection",
     "The opening group may be free only because a human at the desk",
     "The opening group is free because nobody at the desk"),
    ("reuse bootstrap notation for the across-split spread",
     "These are min--max spreads over a design choice, not bootstrap",
     "These are 95% bootstrap intervals, like every other"),
    ("restore over-precise z statistics",
     "roughly $28$ and\n$17$ standard deviations",
     "roughly $28.1$ and\n$17.4$ standard deviations"),
    ("narrow the primary-target shrinkage range",
     "from $38\\%$ to $47\\%$ on the primary one",
     "from $39\\%$ to $46\\%$ on the primary one"),
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

"""Round seventeen's edits to the manuscript, as one auditable script.

Every replacement is an exact string match against the current file and fails
loudly if the anchor has moved, so a half-applied edit is impossible.  The
numbers below are typed by hand from `python scripts/digest.py`; they are NOT
generated from the result files, because `verify_paper.py` re-derives each one
from those files and a paper generated from the same CSVs it is checked
against would make the checker circular.

    python scripts/patch_paper_r17.py            # apply
    python scripts/patch_paper_r17.py --check    # verify anchors only
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ===================================================================== title
edit("title", r"""\title{Identity, Not Attributes: What Configuration Data Contributes to
Incident Prediction in Two Organisations}""",
     r"""\title{Four Choices Behind One Number: Reporting the Incremental Value
of a Recorded Field}""")

# ================================================================== abstract
edit("abstract", r"""\begin{abstract}
A configuration management database (CMDB) programme is justified by the
analytics it enables, and that justification is a comparison against a
baseline the analyst chooses. We measure what configuration data contributes
on a named operational task in two organisations, and find the answer set
less by the data than by two decisions that are rarely written down: which
layer of the configuration hierarchy is being bought, and which
already-recorded fields the comparison baseline is allowed to contain.

On a public event log of $45{,}455$ incidents from a bank's IT operation,
predicting at intake whether an incident will be reassigned, a $256$-way
service-component grouping captures three quarters of what instance-level
identity is worth, and instance identity adds $+0.023$ AUC over it. A
per-item outcome rate --- no model, and no configuration attribute of any
kind --- scores $0.744$ against the full model's $0.748$. What the CMDB
supplies on this task is a stable identifier under which outcome history
accumulates, not the configuration attributes it is bought for.

The second decision explains why the headline number moves. Knowing the
affected item is worth $+0.183$ AUC against four intake fields and $+0.103$
$[+0.094,+0.113]$ once one further field the organisation already records is
admitted: which group logged the incident. Across every design choice we
varied --- split point, target threshold, cleaning cutoff and estimator
family --- the reduction ranges $36.1\%$ to $48.3\%$, and the ordering never
reverses. Four free creation-time congestion features leave it there. The
pattern replicates on a second organisation, tool and country: on the BPI
Challenge 2013 log the same ladder gives a reduction of $61.3\%$ $[54,68]$ on
that challenge's own ping-pong target and $43.9\%$ $[31,55]$ at a stricter
threshold, though the free field is more tightly coupled to the target
there, so we read it as an upper bound.

We report what the measurement does not support in the same detail. Eight
errors of our own are reported as results rather than edited away, two of
them found in the round that produced this version. The larger of the two is
this paper's own: an operational overstatement we had reported as a factor of
$4.3$ at a fixed review capacity does not survive, because its sign reverses
when ties inside the naive baseline's scores are broken differently. Restated
as net benefit across the whole range of decision thresholds, omitting the
free field overstates the item's value by $1.07$ at the threshold where that
value is largest.
\end{abstract}""",
     r"""\begin{abstract}
Papers, business cases and tool evaluations routinely report what a recorded
field is worth as a single number. We argue, and then measure, that the
number is a function of four choices which are almost never stated: the
\emph{baseline} of already-recorded fields the comparison is allowed to
contain, the \emph{metric}, the \emph{operating point}, and the
\emph{population} of the register itself. We write the quantity as
$V(f \mid B, m, \theta)$ and propose that a feature-value claim be reported
as a surface over these arguments rather than as a point.

The demonstration is a configuration management database (CMDB) on a public
event log of $45{,}455$ incidents from a bank's IT operation, predicting at
intake whether an incident will be reassigned. Each of the four choices moves
the answer by more than the effect the previous version of this paper
reported. Admitting one further field the organisation already records ---
which group logged the incident --- takes the item's value from $+0.183$ AUC
to $+0.103$. Admitting a second such field, which a file we had not obtained
now shows is written by the service desk before the incident exists, takes it
to $+0.001$ $[-0.002,+0.003]$: the headline does not survive our own
admissibility criterion once the evidence to apply it is in hand. Under six
defensible instruments on the same scores the reduction runs $43.7\%$ to
$60.3\%$; under net benefit it runs $6.3\%$ to $119.2\%$ across the operating
range, and the item is resolvably harmful in a band above the base rate. At
half population the item is worth $+0.082$ if the long tail of the register
is missing and $+0.062$ if the core is.

We pre-registered a generic protocol and applied it to $22$ public event
logs across seven domains. It admits $13$; the reduction is resolvably
positive on three of them. The generality claim we registered is therefore
\emph{falsified}, and we report the negative, the exclusions and the
condition that actually governs: on most logs the entity is worth nothing to
the intake baseline in the first place, so there is no value for a free field
to absorb.

Eleven errors of our own are reported as results rather than edited away,
three of them found in the round that produced this version. Two are claims
whose every individual number was correct and whose relation between them was
not.
\end{abstract}""")

# =================================================================== keywords
edit("keywords", r"""\begin{keyword}
configuration management database \sep predictive process monitoring \sep
baseline specification \sep variable importance \sep IT service management
\sep incident management \sep decision curve analysis
\end{keyword}""",
     r"""\begin{keyword}
incremental value \sep baseline specification \sep evaluation metrics \sep
predictive process monitoring \sep configuration management database \sep
variable importance \sep decision curve analysis \sep pre-registration
\end{keyword}""")


def main(argv):
    src = TEX.read_text(encoding="utf-8")
    check = "--check" in argv
    missing = []
    for name, old, _new in EDITS:
        if src.count(old) != 1:
            missing.append(f"{name}: anchor appears {src.count(old)} times")
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if check:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for name, old, new in EDITS:
        src = src.replace(old, new, 1)
        print(f"  applied {name}")
    TEX.write_text(src, encoding="utf-8")
    print(f"wrote {TEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

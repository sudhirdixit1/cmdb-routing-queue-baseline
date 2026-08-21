"""Round seventeen's edits to the manuscript, part 4: everything the four
adversarial passes produced.

Every edit below is traceable to an objection in `REFEREE-LOG.md` and names
it. Three add a measurement that did not previously exist (M4, M5, P4);
the rest add a sentence the paper did not contain.

    python scripts/patch_paper_r17d.py --check
    python scripts/patch_paper_r17d.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ------------------------------- M1, M2, H1: what the estimand does not claim
edit("estimand-caveats", r"""Four independent choices therefore sit inside any single-number claim: which
already-recorded fields $B$ contains, which $m$, which $\theta$, and --- for a
feature that is a lookup into a register --- how completely that register is
populated.""",
     r"""Three properties of $R$ should be stated before it is used, because each is a
limit a reader would otherwise have to infer.

First, $R$ is metric-relative \emph{by construction}. It divides two
increments of $m$, and an increment of AUC has no natural zero of the kind a
ratio needs, so ``$43.7\%$ of the value is absorbed'' under AUC and
``$60.3\%$'' under Brier skill are not one quantity measured twice. We do not
claim $R$ is comparable across $m$; Section~\ref{sec:metric} reports the
spread across $m$ as the finding.

Second, every interval in this paper comes from a paired bootstrap that
resamples test rows and holds the fitted models fixed. It therefore quantifies
test-set sampling error and not model-fitting variability, and is narrower
than a full resampling would give. The substitute is the design-space sweep
this paper already carries --- split point, target threshold, cleaning cutoff
and three estimator families --- across which the AUC reduction runs $36.1\%$
to $48.3\%$. A reader should treat that range, not a bootstrap interval, as
the honest width.

Third, four is a claim about how many choices are usually left \emph{implicit},
not about how many exist. The estimator family is a fifth and the cohort a
sixth; the literature already treats the estimator as a choice, and this paper
varies it over three families and reports the range. The four below are the
ones a feature-value claim routinely fixes without saying so.

Four independent choices therefore sit inside any single-number claim: which
already-recorded fields $B$ contains, which $m$, which $\theta$, and --- for a
feature that is a lookup into a register --- how completely that register is
populated.""")

# ---------------------------------------- R4: where the harmful band actually is
edit("harmful-band-operating", r"""off on this task. We have no mechanism to offer for that beyond the obvious one ---
a model with $2{,}554$ item indicators can be confidently wrong where a
coarse model abstains --- and we report it because it is the operating region
in which a desk that reviews a small share of arrivals is working, and
because it is the honest reason the capacity framing produced the number it
did.""",
     r"""off on this task. Locating that band operationally matters, and the direction
is the uncomfortable one: a \emph{higher} threshold means acting on
\emph{fewer} arrivals, so the harmful band is where a capacity-constrained
desk sits, not where an unconstrained one does. Across the four thresholds the
group-aware item model acts on $17\%$ to $36\%$ of arrivals. We have no
mechanism to offer for the sign beyond the obvious one --- a model with
$2{,}554$ item indicators can be confidently wrong where a coarse model
abstains --- and we report it because it is the honest reason the capacity
framing produced the number it did.""")

# ------------------------- M5, P1, P4, P5, H2: the corpus section, strengthened
edit("corpus-falsified", r"""Eight of the $13$ admitted logs are outside ITSM, and the reduction is
resolvable on one of them. \texttt{PROTOCOL.md} \S8 states that the claim is
falsified if the effect appears on the two published ITSM logs and not on a
majority of the admitted non-ITSM logs. It is falsified. We report that rather
than reframing the claim to fit, and the paper's scope is bounded accordingly:
what generalises is the \emph{estimand} and the practice of reporting it as a
surface, not the magnitude of any particular reduction.""",
     r"""Eight of the $13$ admitted logs are outside ITSM, and the reduction is
resolvable on one of them. \texttt{PROTOCOL.md} \S8 states that the claim is
falsified if the effect appears on the two published ITSM logs and not on a
majority of the admitted non-ITSM logs. It is falsified. We report that rather
than reframing the claim to fit, and the paper's scope is bounded accordingly:
what generalises is the \emph{estimand} and the practice of reporting it as a
surface, not the magnitude of any particular reduction.

\paragraph{What ``falsified'' does and does not mean here.}
A referee is entitled to object that we did not fail to find the effect so
much as fail to have a test: on $10$ of the $19$ pairs the reduction has no
denominator, so it could not have been detected had it been there. The
objection is correct and the two statements are separated rather than
conflated. The claim registered in \texttt{PROTOCOL.md} \S8 is falsified
\emph{by its own registered criterion}, which we report because
pre-registration is worth nothing if the verdict is renegotiated once the
answer is known. Beside it: on the nine pairs where a reduction exists to be
measured, four are resolvably positive; on the other ten there was nothing to
measure. A narrower claim --- that where a high-cost entity predicts the
outcome at all, a free opening stamp absorbs a large share of what it is
credited with --- is neither refuted by this corpus nor asserted by it.

\paragraph{Which target carries this.}
Both registered targets are reported for every log, and the four resolvable
results are carried by the \emph{duration} target, which is the standard
outcome in this literature. The handover target is a generalisation of this
paper's own task rather than a standard one, and Section~\ref{sec:corpus}'s
validity check below is why we do not lean on it.

\paragraph{Two things the protocol does not do, stated rather than left to be
found.}
It admits no inter-case features, although Section~\ref{sec:admission} shows
four free creation-time congestion features move the primary log's reduction
from $43.7\%$ to $45.7\%$; that is one log's evidence and the corpus does not
extend it. And its \texttt{NO\_HEADROOM} rule reads the target's prevalence on
the full log, which includes the test half. Recomputing that rule on the
training half only changes \textbf{no} admission decision on any of the $26$
log-target pairs it applies to, so the peek exists in the registered text and
changes nothing in the result.""")

# --------------------------------------- P4: the exclusions predicted in advance
edit("corpus-condition", r"""\paragraph{A precondition, not a moderator.}""",
     r"""\paragraph{The condition that governs, and it is measured on the primary log.}
The exclusions are not bookkeeping; they are the answer. BPI Challenge 2015's
five municipalities are the closest thing the public corpus has to a
controlled replication --- one process, five organisations --- four are
admitted, and none shows a resolvable reduction. Their opening resource stamp
has cardinality $7$ to $18$. BPI Challenge 2012 and all five BPI Challenge
2020 sub-logs have cardinality \emph{one}, which is why the protocol excludes
them. A nearly constant opening field cannot absorb anything, and
Section~\ref{sec:limits}'s intake-mix sweep measures precisely that dependence
on the primary log: as the largest opening group's share of arrivals goes from
$0\%$ to $95\%$, the reduction falls from $95.3\%$ to $6.3\%$. A sweep run on
one organisation predicts which logs in the corpus will show the effect and
which will not, and that is the strongest thing the corpus produced.

\paragraph{A precondition, not a moderator.}""")

# ----------------------------------------- M3 and M4: the nulls in section 12
edit("nulls", r"""\paragraph{Two nulls, because a result of that size is not believed on sight.}
A collapse to zero could be collinearity --- the reference being item identity
relabelled --- or dimensionality, $1{,}700$ extra sparse columns at fixed
penalty being a burden the item must then overcome. Neither survives.
$78.8\%$ of knowledge articles map to exactly one item, against $80.7\%$ for
the opening group, which absorbs less than half of the item's value rather
than all of it; so determinism at that level does not collapse a marginal. And
five matched-mass random partitions of the same cardinality --- built by
slicing a permutation rather than by \texttt{searchsorted} on cumulative mass,
which is the bug that killed correction three --- reach base AUC at most
$0.6479$ and leave the item worth $+0.094$ to $+0.099$. The real field reaches
$0.8041$ and leaves it worth $+0.001$.""",
     r"""\paragraph{Three nulls, because a result of that size is not believed on
sight.}
A collapse to zero could be collinearity --- the reference being item identity
relabelled --- or dimensionality, $1{,}700$ extra sparse columns at fixed
penalty being a burden the item must then overcome, or temporal coherence,
since a knowledge article is used in bursts and a random grouping is not. None
survives.

\emph{Collinearity.} $78.8\%$ of knowledge articles map to exactly one item,
against $80.7\%$ for the opening group, which absorbs less than half of the
item's value rather than all of it. Determinism at that level does not
collapse a marginal.

\emph{Dimensionality.} Five matched-mass random partitions of the same
cardinality --- built by slicing a permutation rather than by
\texttt{searchsorted} on cumulative mass, which is the bug that killed
correction three --- reach base AUC at most $0.6479$ and leave the item worth
$+0.094$ to $+0.099$. The real field reaches $0.8041$ and leaves it worth
$+0.001$.

\emph{Temporal coherence.} Five further partitions matched on cell size
\emph{and} on each cell's distribution over twenty equal-count time strata,
so that every synthetic cell has the same size and the same profile through
time as the real one it copies. They reach base AUC at most $0.6483$ --- the
real field is $0.1558$ above that --- and leave the item worth $+0.093$ to
$+0.100$. We did not build cells from contiguous blocks of the time-ordered
cohort, which would give perfect temporal coherence and would be useless: the
split is temporal, so every test cell would be unseen in training and the null
could not fail. A null that cannot fail is this project's most-repeated defect
and we did not add a sixth.

One thing this ladder does \emph{not} do is condition on a subset. The
knowledge reference enters as a feature column on the unchanged cohort:
incidents whose interaction does not qualify carry an explicit missing token
and stay in the model, the split and the test set, so every rung is measured
on the same $13{,}637$ test incidents.""")

# ------------------------------------------------ R3: axis D is a subsample
edit("axisd-subsample", r"""A 2026 organisation with more
channels sits at the end of that sweep where the free field matters
\emph{more}, not less.""",
     r"""A 2026 organisation with more
channels sits at the end of that sweep where the free field matters
\emph{more}, not less. Two honest qualifications. Subsampling one estate's
opening groups varies the intake mix \emph{within} one organisation, one tool
and one period; it is a sensitivity, not a replication. What supports reading
it as more than that is Section~\ref{sec:corpus}: the logs in the corpus whose
opening field is nearly constant are exactly the ones that show no effect, so
the sweep's prediction is confirmed on data it was not fitted to.""")

# ------------------------------------------------ R1: what a buyer should do
edit("buyer", r"""None of those variations is a defect in any instrument or an error in any
measurement. Each is correct about the question it asks. The point is that a
single number answers one of those questions without saying which, and that
the person writing the business case is the person choosing.""",
     r"""None of those variations is a defect in any instrument or an error in any
measurement. Each is correct about the question it asks. The point is that a
single number answers one of those questions without saying which, and that
the person writing the business case is the person choosing.

We are asked what a buyer should conclude, and on the scope this paper can
speak to the answer is plain. On this task, this estate and this target, a
register that costs money to build and maintain adds nothing measurable over
two fields the organisation already records, and a business case built on
$+0.183$ is pricing that register together with both of them. We do not say
that about registers in general; Section~\ref{sec:corpus} is why we cannot,
and Section~\ref{sec:limits} lists what would have to be true for the sentence
to travel.""")


def main(argv):
    src = TEX.read_text(encoding="utf-8")
    check = "--check" in argv
    missing = [f"{name}: anchor appears {src.count(old)} times"
               for name, old, _new in EDITS if src.count(old) != 1]
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

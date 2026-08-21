"""Round seventeen's edits to the manuscript, part 1: front matter, the
introduction, and the estimand.

Every replacement is an exact string match against the current file and the
script refuses to write anything unless every anchor is found exactly once,
so a half-applied edit is impossible.  The numbers below are typed by hand
from `python scripts/digest.py`; they are NOT generated from the result
files, because `verify_paper.py` re-derives each one from those files and a
paper generated from the same CSVs it is checked against would make the
checker circular.

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
Papers, business cases and tool evaluations report what a recorded field is
worth as a single number. That number is a function of four choices which are
almost never stated: the \emph{baseline} of already-recorded fields the
comparison is allowed to contain, the \emph{metric}, the \emph{operating
point}, and the \emph{population} of the register the field reads from. We
write the quantity as $V(f \mid B, m, \theta)$ and propose that a
feature-value claim be reported as a surface over those arguments rather than
as a point.

The demonstration is a configuration management database (CMDB) on a public
event log of $45{,}455$ incidents from a bank's IT operation, predicting at
intake whether an incident will be reassigned. Each choice moves the answer by
more than the effect the previous version of this paper reported. Admitting
one further field the organisation already records --- which group logged the
incident --- takes the item's value from $+0.183$ AUC to $+0.103$. Admitting a
second, which a file we had not obtained now shows is written by the service
desk before the incident exists, takes it to $+0.001$ $[-0.002,+0.003]$: the
headline does not survive our own admissibility criterion once the evidence to
apply it is in hand. Under six defensible instruments on the same scores the
reduction runs $43.7\%$ to $60.3\%$, and the AUC figure we published is the
smallest of them; under net benefit it runs $6.3\%$ to $119.2\%$ across the
operating range, and the item is resolvably harmful in a band above the base
rate. At half population the item is worth $+0.082$ if the register's long
tail is missing and $+0.064$ if its core is.

We pre-registered a generic protocol and applied it to $22$ public event logs
across seven domains. It admits $13$; the reduction is resolvably positive on
three. The generality claim we registered is therefore falsified, and we
report the negative, the exclusions and the condition that does govern: on
most logs the entity is worth nothing to the intake baseline, so there is no
value for a free field to absorb.

Eleven errors of our own are reported as results rather than edited away,
three of them found in the round that produced this version. Two are claims
whose every individual number was correct and whose asserted relation between
them was not.
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

# ============================================================== introduction
edit("intro-opening", r"""A CMDB programme is expensive and is justified by what it will enable. That
justification rests on a comparison whose second arm --- performance without
configuration data --- is a choice the analyst makes, usually silently, by
deciding which already-available fields to include. It also rests on a
quantity that is almost never separated out: which \emph{layer} of the
configuration hierarchy the benefit comes from, given that an instance-level
register costs far more to build and maintain than a service register.

This paper measures both, on two organisations' incident logs, and reports
three things.""",
     r"""A business case for a data programme is a comparison, and the second arm of
that comparison --- performance \emph{without} the data --- is a choice the
analyst makes, usually silently. So is the metric the comparison is stated
in, so is the operating point at which that metric is read, and so is the
assumed completeness of the register being bought. Each of those choices is
routinely left implicit, and the result is reported as one number.

We write the quantity such a claim actually names as
\begin{equation}
V(f \mid B, m, \theta),
\label{eq:estimand}
\end{equation}
the incremental value of a feature $f$ over a baseline feature set $B$, under
metric $m$, at operating point $\theta$; and for a feature that is a lookup
into a register we treat that register's population as a fourth choice, one
that acts on $f$ rather than on the comparison. The claim of this paper is not
that $V$ depends on those arguments --- that is a theorem, and
Section~\ref{sec:notvimp} says whose --- but that on a real decision, with
every choice held to a defensible range, the dependence is larger than the
effect being reported. We demonstrate it by taking our own previously
published headline apart along each argument in turn. One of those
demonstrations removes the headline.

The demonstration runs on a configuration management database (CMDB): the
register of items an IT estate contains, bought to make operational analytics
possible, evaluated here on a named task --- predicting at intake whether an
incident will be reassigned --- on a public log of $45{,}455$ incidents from a
bank's IT operation.

This paper reports four things.""")

edit("intro-contributions", r"""\begin{enumerate}
\item \textbf{Identity, not attributes, and not at instance level.} A
$256$-way service-component grouping of the same estate captures three
quarters of what instance-level identity is worth on this task, and instance
identity adds $+0.023$ over it. Below that, a per-item outcome rate applied
as a lookup table --- no model, no other field, no configuration attribute
--- reaches $0.744$ against the full model's $0.748$. What the configuration
data supplies here is a stable key under which six months of outcomes
accumulate (Section~\ref{sec:layer}).

\item \textbf{The measured value turns on a field-admission choice.}
Against four intake fields, item identity is worth $+0.183$ AUC; against
those fields plus one the organisation already records for nothing, $+0.103$
$[+0.094,+0.113]$. The reduction runs $36.1\%$ to $48.3\%$ across the design
space and replicates on a second organisation, tool and country
(Section~\ref{sec:admission}).

\item \textbf{Eight corrections, reported as results.} Six were found in
earlier rounds; two in the round that produced this version. Both of the
new ones removed a claim the previous version made, and one of them is the
paper's own operational headline (Section~\ref{sec:corrections}).
\end{enumerate}""",
     r"""\begin{enumerate}
\item \textbf{Every choice moves the answer, and the baseline choice removes
it.} Admitting one further field the organisation already records --- which
group logged the incident --- takes the item's value from $+0.183$ to
$+0.103$ $[+0.094,+0.113]$ AUC. Admitting a second, the knowledge-article
reference, takes it to $+0.001$ $[-0.002,+0.003]$. The previous version
declined to admit that second field because it could not establish when the
value was written; a file from the same public collection, which we had not
obtained, settles where it comes from (Sections~\ref{sec:admission}
and~\ref{sec:failed}).

\item \textbf{The metric and the operating point are choices of the same
kind.} On identical scores, six defensible instruments put the reduction
between $43.7\%$ and $60.3\%$, and ROC AUC --- the number the previous
version printed --- is the \emph{smallest} of them. Net benefit, read at a
single operating point as decision-analytic practice requires, puts it
between $6.3\%$ and $119.2\%$ depending on which point, and the item is
resolvably harmful in a band above the base rate. We identify which mechanism
produces which disagreement (Sections~\ref{sec:metric} and~\ref{sec:opp}).

\item \textbf{A pre-registered protocol over $22$ public logs, and a
falsified generality claim.} We registered a generic procedure, a corpus and
an exclusion rule before running any of them. The rules admit $13$ logs
across six domains; the reduction is resolvably positive on three. The
registered claim that the effect is a property of process event logs rather
than of ITSM data is therefore \emph{falsified}, and
Section~\ref{sec:corpus} reports the negative together with the condition
that does govern: on most logs the entity is worth nothing to the intake
baseline, so there is no value for a free field to absorb.

\item \textbf{Eleven corrections, reported as results.} Eight were found in
earlier rounds; three in the round that produced this version. Two of the
three are claims in which every individual number was correct and the
relation the prose asserted between them was not
(Section~\ref{sec:corrections}).
\end{enumerate}""")

# =============================================== the estimand (was notvimp)
edit("notvimp-head", r"""\label{sec:notvimp}

The objection we expect first, and the one this paper would deserve if it
stopped at Section~\ref{sec:admission}, is that measured importance is
baseline-relative, that \citet{williamson2023vimp} and \citet{covert2020sage}
formalise exactly that, and that a study reporting it on one log is reporting
a known fact with a new number attached. The objection is correct about the
formal content and we concede it in those terms. Four things are added here
that no formal framework supplies.""",
     r"""\label{sec:notvimp}

\subsection{The estimand}
Equation~\ref{eq:estimand} names
$V(f \mid B, m, \theta) = m(B \cup \{f\}, \theta) - m(B, \theta)$. For two
nested baselines $B_0 \subset B_1$ we report the \emph{admissibility
reduction}
\begin{equation}
R(f \mid B_0, B_1, m, \theta) \;=\; 1 - \frac{V(f \mid B_1, m, \theta)}
{V(f \mid B_0, m, \theta)},
\label{eq:reduction}
\end{equation}
the share of a feature's apparent value already carried by fields the
organisation records for nothing. $\theta$ is absent for metrics that
integrate over the operating range; Section~\ref{sec:metric} says which those
are. We report $R$ only where $V(f \mid B_0, m, \theta)$ is positive in every
bootstrap draw. A ratio whose denominator crosses zero is not a quantity, and
this paper has previously printed one that did.

Four independent choices therefore sit inside any single-number claim: which
already-recorded fields $B$ contains, which $m$, which $\theta$, and --- for a
feature that is a lookup into a register --- how completely that register is
populated. Sections~\ref{sec:admission}, \ref{sec:metric}, \ref{sec:opp}
and~\ref{sec:population} vary one at a time on one dataset, holding the cohort,
the split, the estimator and the seed fixed throughout, so that any movement
is attributable to the choice and to nothing else.
Section~\ref{sec:standard} states what we propose be reported in place of a
point.

\subsection{What is and is not new here}
The objection we expect first is that measured importance is baseline-relative,
that \citet{williamson2023vimp} and \citet{covert2020sage} formalise exactly
that, and that a study reporting it on one log is reporting a known fact with
a new number attached. The objection is correct about the formal content and
we concede it in those terms. Four things are added here that no formal
framework supplies.""")

edit("notvimp-tail", r"""\paragraph{It replicates across organisations, and no framework predicts that.}
Baseline-relativity is a theorem; whether a particular pair of fields overlaps
in a particular estate is an empirical question with no general answer. That
the same ladder produces the same ordering and a reduction of the same order
on a second organisation, a second tool and a second country
(Section~\ref{sec:admission}) is evidence about how ITSM data is
generated, not about the definition of variable importance.

\paragraph{What we do not claim.}
We do not claim a new estimator, a new importance measure, or priority over
\citet{cook2007roc}, who stated the underlying point for AUC in 2007. The
contribution is measurement and evaluation practice, and
Section~\ref{sec:layer} rather than Section~\ref{sec:admission} is where the
paper's novel finding sits.""",
     r"""\paragraph{The metric argument is not in those frameworks at all.}
\citet{williamson2023vimp} and \citet{covert2020sage} are stated for a fixed
predictiveness measure. Nothing in them says that two defensible measures
applied to the \emph{same scores} disagree about how much of a feature's value
a second feature absorbs, still less by how much. That is an empirical
question, Section~\ref{sec:metric} answers it here, and the answer is that on
this decision the metric choice moves the reduction by more than the free
field does.

\paragraph{Where it appears and where it does not, measured rather than
assumed.}
Baseline-relativity is a theorem; whether a particular pair of fields overlaps
in a particular estate is an empirical question with no general answer. We
pre-registered a protocol and applied it to $22$ public logs
(Section~\ref{sec:corpus}) rather than generalising from one. The answer is
mostly negative and is reported as such.

\paragraph{What we do not claim.}
We do not claim a new estimator, a new importance measure, or priority over
\citet{cook2007roc}, who stated the underlying point for AUC in 2007. Nor do
we claim any of the four choices is illegitimate: each is correct about the
question it asks. The contribution is that those are different questions,
that a single number answers one of them without saying which, and that on
this decision the spread between them is larger than the effect.""")


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

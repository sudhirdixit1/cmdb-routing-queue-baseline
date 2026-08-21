"""Round seventeen's edits to the manuscript, part 2: the metric axis, the
operating-point fixes, the population axis, the corpus, the reporting
standard, the settled Section 9, the limitations, the corrections list and
the conclusion.

Same discipline as part 1: exact-match anchors, nothing written unless every
one is found exactly once, numbers typed by hand from
`python scripts/digest.py` so that `verify_paper.py` remains an independent
check rather than a restatement.

    python scripts/patch_paper_r17b.py --check
    python scripts/patch_paper_r17b.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# =========================================================== the metric axis
METRIC = r"""\section{The Metric Axis}
\label{sec:metric}

Section~\ref{sec:admission} varied $B$ and held $m$ at ROC AUC. This section
holds $B$ and the scores fixed and varies $m$. Same cohort, same split, same
four fitted models, same seed: the only thing that changes is what is
computed from the scores.

\subsection{Seven instruments, six of them independent}
Table~\ref{tab:instruments} reports the reduction of Equation~\ref{eq:reduction}
under every instrument we can defend for this question. Detection at a fixed
review capacity is kept in the table although Section~\ref{sec:withdrawn}
withdrew it as a headline, because a matrix of instruments is the right place
to show what a tie-degenerate instrument does to a ratio.

Expected cost at a stated cost ratio is \emph{not} a seventh axis. At cost
ratio $r$ the Bayes threshold is $1/(1+r)$, so the net-benefit weight
$\theta/(1-\theta)$ is exactly $1/r$ and the cost avoided per case is
$r \cdot \text{NB}(1/(1+r))$ identically. The two therefore give the same
reduction; we verified it over ten contrasts, where the largest discrepancy
is $3\times 10^{-16}$, and report six instruments rather than seven.

\begin{table}[t]
\centering
\small
\begin{tabular}{lrrr}
\toprule
instrument & $V(f \mid B_0)$ & $V(f \mid B_1)$ & reduction \\
\midrule
ROC AUC              & $+0.183$ & $+0.103$ & $43.7\%$ $[40.2,47.1]$ \\
Average precision    & $+0.226$ & $+0.090$ & $60.3\%$ $[57.3,63.4]$ \\
Brier skill          & $+0.168$ & $+0.070$ & $58.4\%$ $[54.4,62.3]$ \\
Nagelkerke $R^2$     & $+0.223$ & $+0.097$ & $56.6\%$ $[52.9,60.3]$ \\
\midrule
Net benefit, $\theta=0.325$ & $+0.093$ & $+0.087$ & $6.3\%$ \\
Net benefit, $\theta=0.500$ & $+0.084$ & $-0.016$ & $119.2\%$ \\
\bottomrule
\end{tabular}
\caption{The same reduction under four instruments that integrate over the
operating range and two readings of one that does not. $B_0$ is the four
intake fields; $B_1$ adds the opening group. Intervals are paired bootstrap,
$2{,}000$ draws, one resampled index set per draw shared by all four models.
The net-benefit rows carry no interval on the ratio because the whole point of
the row pair is that the ratio is not one number.}
\label{tab:instruments}
\end{table}

\paragraph{The number we published is the smallest of them.}
Across the four instruments that integrate over the operating range the
reduction runs $43.7\%$ to $60.3\%$, and ROC AUC sits at the bottom of that
range. The previous version of this paper reported the AUC figure and treated
the more principled instruments as a threat to it; on this data they are not,
and a referee reading only Section~\ref{sec:withdrawn} would have drawn the
opposite conclusion. This is the second correction in this project's history
that goes against the direction its errors usually take, and we record it as
such rather than quietly banking it.

\subsection{Why the instruments disagree}
Three mechanisms are testable and we test all three. Each makes a prediction
that can fail, and the first one did.

\paragraph{Aggregation, which is the largest.}
AUC is $\int \text{TPR}\,d\text{FPR}$, so the increment a feature buys can be
attributed to regions of the operating range without any modelling choice: the
integral is additive over a partition of the FPR axis and the parts sum to the
whole, which we assert rather than assume. We predicted the increment would be
concentrated somewhere the net-benefit grid does not reach. It is not. Over the
$31$-point grid the group-aware model runs at every false-positive rate from
$0.009$ to $0.997$, and the item's advantage is \emph{diffuse}: the largest of
ten equal FPR bands carries $18.2\%$ of it and three bands are needed to reach
half. AUC sums that whole profile; net benefit at one $\theta$ reads one point
of it. The two are not disagreeing about a fact.

\paragraph{Baseline degeneracy, which explains where net benefit is lowest.}
At $\theta = 0.200$, $0.300$ and $0.325$ the intake block acts on every
incident in the test half: as a decision rule it \emph{is} treat-all, and the
group-aware baseline is at $0.944$ to $0.967$, barely distinguishable from it.
An increment measured against a rule that does nothing comes out nearly the
same on both rungs, and their ratio near one. Calling a baseline degenerate
when it acts on more than $95\%$ or fewer than $5\%$ of arrivals --- a
threshold we declare before applying it --- the reduction runs $0.047$ to
$0.435$ across the $11$ grid points where both baselines are degenerate and
$0.581$ to $1.168$ across the $5$ where neither is.

\paragraph{Calibration, which is real and provably not the whole story.}
The item-aware model has calibration slope $1.040$ and the intake block
$1.391$. Recalibrating on a held-out tail of the training half moves the
net-benefit reduction by up to $0.253$ where the denominator is safe and the
proper-score reductions by up to $0.014$. It moves the AUC and average
precision reductions by exactly zero, because a monotone rescaling cannot
change a rank statistic --- a prediction that would have failed loudly had the
recalibration not been monotone, and did not.

\paragraph{And a tie convention the two rank statistics do not share.}
The intake block emits $23$ distinct scores for $13{,}637$ incidents.
Average precision's default value equals its \emph{negatives-first} bound to
within $10^{-16}$ on all four models, because the precision-recall curve is
evaluated where a tied block has been admitted whole; AUC's default equals a
random tie-break to within $0.0004$. Put both on the only convention a desk
could implement, the reduction is $43.6\%$ under AUC and $71.2\%$ under
average precision. The gap widens rather than closes, which is the outcome we
did not expect and report because we did not.

"""

edit("insert-metric", r"""\section{What the Difference Buys}
\label{sec:buys}""", METRIC + r"""\section{What the Difference Buys: the Operating-Point Axis}
\label{sec:buys}""")

# ======================================== section 8.2, two defects repaired
edit("dca-run", r"""Over a grid of $31$ thresholds from $0.05$ to $0.80$, the group-aware
increment is positive with its interval excluding zero at $20$ points, in a
contiguous run from $0.100$ to $0.425$ --- the region either side of this
cohort's base rate. The naive increment is positive and resolved at $29$ of
the $31$.""",
     r"""Over a grid of $31$ thresholds from $0.05$ to $0.80$, the group-aware
increment is positive with its interval excluding zero at $20$ points. Those
$20$ are not one run: $14$ of them form a contiguous block from $0.100$ to
$0.425$, the region either side of this cohort's base rate, and the remaining
$6$ sit at $0.675$ and above, on the far side of the negative band described
below. An earlier version of this sentence said all $20$ lay in the run; every
number in it was correct and the relation asserted between them was not
(Section~\ref{sec:corrections}). The naive increment is positive and resolved
at $29$ of the $31$.""")

edit("dca-negative", r"""Above the resolved region the increment decays and then turns negative: at
four grid points between $0.475$ and $0.575$ the group-aware increment's
interval lies entirely below zero, reaching $-16.1$ $[-23.0,-8.9]$ per
thousand at $p_t=0.50$. At a one-for-one exchange rate, adding item identity
to a model that already knows the opening group makes the desk worse off on
this task.""",
     r"""Above the contiguous region the increment decays and then turns negative: at
four grid points between $0.475$ and $0.575$ the group-aware increment's
interval lies entirely below zero, and its minimum over the whole grid is
$-21.1$ $[-27.7,-14.4]$ per thousand at $\theta=0.525$. An earlier version
gave the minimum as $-16.1$ $[-23.0,-8.9]$ at $\theta=0.50$, which is the
worst point among the five this paper had chosen to name rather than the worst
point on the grid; the understatement was $31\%$ and it flattered us
(Section~\ref{sec:corrections}). At a one-for-one exchange rate, adding item
identity to a model that already knows the opening group makes the desk worse
off on this task.""")

# ======================================================= population + corpus
TAIL = r"""\section{The Population Axis}
\label{sec:population}

Our item field is $100\%$ populated. Real registers are not, and every
practitioner who has read a draft of this paper has said so. That is a
measurement, not a caveat, so we make it one: we mask the item column to a
declared population level and re-measure the whole ladder, leaving both
baselines untouched, so the curve is the value of a partially populated
register rather than the value of a smaller dataset. A masked item becomes an
explicit empty level rather than a dropped row, because a desk with a
half-empty register still has the incidents.

How an estate empties turns out to matter more than how empty it is, so we
report three regimes: items masked independently at random; the least frequent
items dropped whole, which is how a real estate degrades because discovery and
manual curation cover the big central things first; and the most frequent
dropped whole, which is not realistic and is reported as the other end of the
range. At half population the group-aware increment is $+0.082$ when the long
tail is missing, $+0.067$ at random, and $+0.064$ when the core is; the
reduction at the same three points is $39.3\%$, $36.1\%$ and $14.2\%$. Over
the whole surface the reduction runs $-0.6\%$ to $47.0\%$, and its interval
excludes zero at $19$ of the $19$ points measured. Figure~\ref{fig:population}
draws it.

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figK3_population.png}
\caption{What a partially populated register is worth. Left: the item's value
over intake plus the opening group, against the share of incidents whose item
is recorded, under three degradation regimes. Right: the reduction of
Equation~\ref{eq:reduction} on the same axis. The estate is concentrated
enough that $246$ of $2{,}929$ items carry $90\%$ of the incidents, which is
why dropping the tail costs so little.}
\label{fig:population}
\end{figure}

The practical reading is that a buyer who prices a half-populated register
from the random curve will be wrong in whichever direction their estate
actually degrades, and by roughly a factor of three in the reduction. The
usual caveat --- ``our figure is an upper bound because real data is worse''
--- is not supported on this axis either: at full population the measurement
sits at the top of its own curve, so better discovery tooling cannot raise it.

\section{The Corpus: Where the Effect Appears, and Where It Does Not}
\label{sec:corpus}

Everything above is one log. This section asks whether the admissibility
effect is a property of process event logs in general or of ITSM data in
particular, under a protocol registered before any of it was run.

\subsection{Pre-registration}
\texttt{PROTOCOL.md}, supplied as supplementary material and committed to the
repository in a commit that adds no result file, fixes in advance: the two
targets, both reported for every log; the rules that assign every attribute to
exactly one of the high-cost entity $f$, the free per-event field $g$, the
intake block $B_0$, a layer, or excluded; six exclusion codes; the estimator,
split, seed and instruments; the log-level discriminators, computed before any
model is fitted; and the outcome that would falsify the claim. Eight
amendments were made after running the role assignment, which reads no
outcome, and before fitting any model; each is recorded in that file with its
reason, and every one is the registered text failing to implement its own
stated intent. The check that they stop there is that after them the generic
rules assign the primary log exactly the roles this paper assigns by hand ---
$f$ the configuration item, $g$ the opening group, $B_0$ the four intake
fields, and the CI type and subtype as layers --- although nothing in the
rules names that log or those fields.

\subsection{The corpus, and what the rules exclude}
Twenty-three files across seven domains, fetched by DOI with a recorded
SHA-256 for each; $22$ logs parse. The registered rules admit $13$ across six
domains and exclude nine with a code. Two exclusions are worth stating as
findings rather than as bookkeeping. In BPI Challenge 2012 and in all five BPI
Challenge 2020 sub-logs, \emph{every case is opened by the same actor}: the
opening resource stamp has cardinality one, there is no free opening field to
admit, and the question this paper asks cannot arise. In the Hospital Billing
log the only reusable entity, \texttt{diagnosis}, is missing on $65\%$ of first
events and no other attribute reaches the registered cardinality floor.

\subsection{The result, which is mostly negative}
Nineteen log-target pairs survive the exclusion rules.
Figure~\ref{fig:corpus} shows every one where a reduction exists to be
measured. On $10$ of the $19$ the entity is not resolvably worth anything over
the intake block at all, so there is nothing for a free field to absorb and
$R$ is undefined rather than small. On the remaining nine the reduction's own
interval excludes zero on four, drawn from three logs: the primary log on both
targets, BPI Challenge 2013's incident log on the duration target
($37.8\%$ $[12.9,62.8]$), and BPI Challenge 2019's procurement log on the
duration target ($47.1\%$ $[40.8,53.4]$ on $251{,}734$ traces).

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figK4_corpus.png}
\caption{Every log-target pair where the entity is resolvably worth something
over the intake block, so that a reduction exists. A hollow ring marks a pair
whose reduction has no reportable interval because the denominator is not
positive in every draw.}
\label{fig:corpus}
\end{figure}

Eight of the $13$ admitted logs are outside ITSM, and the reduction is
resolvable on one of them. \texttt{PROTOCOL.md} \S8 states that the claim is
falsified if the effect appears on the two published ITSM logs and not on a
majority of the admitted non-ITSM logs. It is falsified. We report that rather
than reframing the claim to fit, and the paper's scope is bounded accordingly:
what generalises is the \emph{estimand} and the practice of reporting it as a
surface, not the magnitude of any particular reduction.

\subsection{Two things the corpus does establish}
\paragraph{A precondition, not a moderator.}
We attempted the prediction the plan for this round asked for: regress the
reduction on log properties measurable before any model is fitted --- entity
cardinality, its concentration, the mutual information between $f$ and $g$,
trace length, whether $g$ is a person or a team, and four more. On nine points
with eleven predictors the leave-one-out $R^2$ is $-1.323$ against a
permutation null of $2{,}000$ shuffles at $p = 0.448$: the fit predicts a
held-out reduction worse than its own mean does. We report that and show no
in-sample fit in its place. What the corpus does show is coarser and more
useful: the effect requires an entity that predicts the outcome at all, and on
most public logs it does not.

\paragraph{A generic target is not the published target, and we checked.}
The protocol's handover target counts distinct opening groups in a trace. The
primary log ships its own reassignment count, which is what this paper's other
sections use. They are not the same construction and they do not agree: the
generic target fires on $92.7\%$ of incidents against the published target's
$41.1\%$, and the two agree on $46.0\%$ of them, barely above what
independence between two marginals of that size would give. The tautology
control of \texttt{PROTOCOL.md} \S4.3 splits with them --- under the generic
target the largest opening group has the higher rate, under the published
target the lower. The corpus measures a generic workflow outcome; it does not
measure this paper's task on twelve further organisations, and it would have
been easy to write as though it did.

\section{A Reporting Standard}
\label{sec:standard}

We propose that a feature-value claim be reported as a surface over the
arguments of Equation~\ref{eq:estimand} rather than as a point, and that the
minimum reportable form is:

\begin{enumerate}
\item \textbf{The baseline ladder.} Every already-recorded field admitted to
$B$, named, with the admissibility criterion stated before it is applied, and
$V$ at each rung. A field the organisation already holds and does not admit is
a decision, and its cost is the difference between two rungs.
\item \textbf{At least one integrating and one operating-point instrument.}
On this data the two families differ by more than the effect. Reporting only
one is reporting one of two answers without saying which question was asked.
\item \textbf{The operating range, not a chosen point.} If the claim is
decision-analytic, the whole curve with intervals, and explicitly the region
where the increment is not resolvable or is negative.
\item \textbf{The register's population, if the feature is a lookup.} With the
degradation regime named, because the regime moves the answer by more than the
level does.
\end{enumerate}

Figure~\ref{fig:surface} is that report for one instrument on this data, and
Figure~\ref{fig:instruments} is the same claim across instruments. Neither
figure contains a number that is not in a result file, and every number in
both is re-derived from those files by the checker described in
Section~\ref{sec:corrections}.

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figK1_instruments.png}
\caption{Left: the reduction under six instruments, paired bootstrap
intervals, the published AUC figure dashed. Right: the same reduction under
one instrument across the operating range. The shaded band is where the item's
increment over a group-aware baseline is resolvably negative.}
\label{fig:instruments}
\end{figure}

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figK2_surface.png}
\caption{$V(f \mid B, m, \theta)$ at $m$ = net benefit, both baselines, every
operating point, with paired bootstrap bands. A single number for ``what the
item is worth'' is a choice of one $x$-coordinate and one of these two
curves.}
\label{fig:surface}
\end{figure}

"""

edit("insert-tail", r"""\section{One Thing We Could Not Establish}
\label{sec:failed}""", TAIL + r"""\section{The Question We Could Not Answer, Answered}
\label{sec:failed}""")

# ==================================================== section 9, rewritten
edit("failed-body", r"""A third field, the knowledge-article reference, sits on the same
\texttt{Open} row, is $100\%$ populated, and costs nothing. Adding it to the
baseline raises AUC to $0.805$ and drives the measured value of item
identity to $-0.003$. Whether that figure belongs in Table~\ref{tab:headline}
depends on whether the field is available at creation, and we could not
determine this.

Two structural tests both fail. A field that varies within an incident is
certainly a per-event observation; the knowledge reference never varies ---
but neither does \texttt{Interaction ID}, which has $45{,}426$ distinct
values for $45{,}455$ incidents and is plainly a creation-time key, so
constancy is evidence of granularity, not timing. Exact identity with the
closed record fares no better: the knowledge reference matches its
closed-record column for $100.000000\%$ of incidents, but so does
\texttt{Interaction ID} for $99.997628\%$ of the $42{,}151$ single-interaction
incidents --- one mismatch against a pass mark of $100.000000\%$.

We therefore make no claim about this field. The $-0.003$ is also inside the
dimensionality null of Section~\ref{sec:admission} and changes sign under
penalty tuning, so it is not resolvable on either ground. This is the paper's
thesis turned on itself, and that reading is correct: our headline is
contingent on a field-admission decision we cannot adjudicate. The
transferable part is the negative --- a field being free, populated and
present on an opening record does not make it creation-time. The collection
ships an interaction detail file we did not obtain; if it records this field
at creation the question is answerable, and our inability to settle it is a
limit of the three files we hold, not of the export.""",
     r"""The previous version of this paper had a section here titled ``One Thing We
Could Not Establish''. A third field, the knowledge-article reference, sits on
the same \texttt{Open} row, is $100\%$ populated, and costs nothing. Adding it
to the baseline raises AUC to $0.805$ and drives the measured value of item
identity to $-0.003$. Whether that figure belonged in the headline depended on
whether the field is available at creation, and we could not determine it from
the three files we held. That section named the missing evidence: an
interaction detail file shipped in the same public collection, which we had not
obtained.

We obtained it. \texttt{Detail\_Interaction.csv} records $147{,}004$
service-desk interactions.

\paragraph{What it settles.}
$94{,}250$ of those interactions --- $64.1\%$ of the file --- never produce an
incident at all, and $99.7\%$ of those were resolved on the first call. Every
one of them carries a knowledge reference, across $1{,}978$ distinct articles.
A field the incident process assigns cannot be populated on records the
incident process never touches, so the reference is written by the service desk
during the call. Of the incidents that do join an interaction, $92.4\%$ of the
cohort, the interaction opened before the incident in $100.00\%$ of cases with
a median gap of six minutes, and the desk's recorded handling time on it had
elapsed before the incident opened in $98.6\%$.

\paragraph{What it does not settle, and we say so.}
Agreement with the closed record still cannot discriminate. On the $41{,}413$
incidents whose interaction was worked to completion first, the knowledge
reference agrees with its interaction's value on $100.00\%$ and the closure
code --- which is certainly not creation-time --- on $98.97\%$. The reasoning
of the previous version stands: an interaction is itself a closed record. The
subset whose interaction had formally \emph{closed} before the incident opened
contains five incidents, and nothing is concluded from five.

\paragraph{The consequence, which removes our headline.}
Admitting the reference carried by an interaction that was worked to
completion before the incident opened --- populated on $91.1\%$ of the
cohort --- takes the item's measured value from $+0.103$ to $+0.001$
$[-0.002,+0.003]$, a reduction of $99.7\%$ against the intake-only baseline
rather than $43.7\%$. Figure~\ref{fig:knowledge} draws the ladder.

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figK5_knowledge.png}
\caption{What item identity is worth as the baseline admits more of what the
organisation already recorded. The shaded band is the range left by five
matched-mass random partitions of the same cardinality as the knowledge
reference.}
\label{fig:knowledge}
\end{figure}

\paragraph{Two nulls, because a result of that size is not believed on sight.}
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
$0.8041$ and leaves it worth $+0.001$.

\paragraph{What this does to the paper.}
Our thesis is that the measured value of a field is set by an admission
decision the analyst makes silently. The strongest available demonstration of
that thesis is that it removes our own headline, and this is that
demonstration. We do not claim the knowledge reference is \emph{proved}
creation-time; we claim the balance of evidence has moved decisively, that a
paper whose headline is contingent on excluding a field must report what
admitting it does, and that $+0.103$ should be read as the value of item
identity \emph{given that one particular free field is admitted and another is
not}. Section~\ref{sec:standard} is the general form of that sentence.""")


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

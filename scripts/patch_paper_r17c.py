"""Round seventeen's edits to the manuscript, part 3: limitations, the
corrections list, the conclusion and the acknowledgement.

    python scripts/patch_paper_r17c.py --check
    python scripts/patch_paper_r17c.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

EDITS = []


def edit(name, old, new):
    EDITS.append((name, old, new))


# ================================================================ limitations
edit("limits-era", r"""\paragraph{Estate and era.}
Two organisations, two platforms, both on-premises products, and six months
of 2013 and 2014 data in the primary case. The values $+0.183$ and $+0.103$ are
properties of one estate; what we argue transfers is that the gap exists and
is large. Practice has moved since: discovery tooling auto-populates a large
fraction of a modern estate, event-driven incidents arrive with the item
already stamped by the monitoring source, and service mapping rather than
item identity is where much current CMDB spend goes. The counterfactual we
model --- an organisation with no item field at all --- is not the
counterfactual a 2026 buyer faces, which is about relationship depth and data
health rather than existence. Section~\ref{sec:layer} is the part of this
paper that speaks to that buyer, and it says the service layer carries most
of the measured value.

\paragraph{Data quality.}
Our item field is $100\%$ populated because the tool copies it from the
originating interaction record. Real CMDBs are not this clean, and a lower
population or accuracy rate would reduce the item's measured value. Our
$+0.103$ should be read as an upper bound for an estate whose configuration
data is worse than this one's, which is most of them.

\paragraph{Intake channel.}
The free field's informativeness depends on an intake mix in which two thirds
of tickets pass a central desk. Where tickets are opened by end users through
a portal or by an integration account, the field may carry far less, or may
not exist in a comparable form. The one-bit result implies the contrast that
matters is central desk against everything else, and that contrast is a
property of how the organisation takes work in.

\paragraph{Free text.}
Neither log carries a usable short description, and every real deployment
has one. \citet{kapel2026change} rank two free-text fields above CI Name for
a related target. If free text absorbs much of the item's value, the
field-admission argument becomes stronger and the CMDB's measured value
smaller; we cannot test it here, and it is the most important open question
this study leaves.""",
     r"""\paragraph{Era, decomposed into four measurements.}
The primary log is six months of 2013 and 2014 from one estate, and practice
has moved. ``Practice has moved'' is not one claim, however, and each of its
four usual components has a proxy in data we hold.
\emph{(i)~Discovery auto-populates the estate.} Ours is already $100\%$
populated, so the measurement sits at the top of its own curve and better
tooling cannot raise it; what a modern estate changes is which part of the
register is populated, and Section~\ref{sec:population} measures that.
\emph{(ii)~Incidents arrive pre-stamped.} In 2014, $97.7\%$ of incidents that
came through the service desk already carried the item their originating call
carried. A change that pre-stamps arrivals is a change from $97.7\%$ to at
most $100\%$.
\emph{(iii)~Service mapping rather than item identity.} The service component
--- $272$ values in this cohort --- reaches $+0.078$ over intake plus group
against the item's $+0.103$, so it captures $75.3\%$ of it, and the item's
marginal over it is $+0.023$.
\emph{(iv)~More intake channels, fewer central desks.} This is the largest
sensitivity in the paper. Subsampling the cohort so that the largest opening
group holds between $0\%$ and $95\%$ of it moves the reduction from $95.3\%$
to $6.3\%$: when one desk opens everything the opening group carries almost no
information and absorbs almost nothing, and when opening is distributed it
absorbs nearly all of the item's apparent value. A 2026 organisation with more
channels sits at the end of that sweep where the free field matters
\emph{more}, not less.

\paragraph{Data quality.}
Section~\ref{sec:population} replaces the caveat this paragraph used to make.
What remains is that we measure population and not \emph{accuracy}: a register
that is fully populated with wrong values is not modelled here, and we have no
way to detect one in a public export.

\paragraph{Free text, and a search rather than a regret.}
Neither of the published logs carries a usable short description, and every
real deployment has one. \citet{kapel2026change} rank two free-text fields
above CI Name for a related target. We therefore searched: every attribute of
every one of the $22$ parsed logs, against a criterion declared in
\texttt{PROTOCOL.md} \S7 before the search ran. Of $596$ attributes, zero
satisfy it. The field a referee will name, UCI 498's \texttt{u\_symptom}, is
$3.4\%$ unique with a mean length of $10.9$ characters: a coded symptom, not a
description. Two amendments were needed to stop the criterion admitting
formatted identifiers, and they are recorded. The threat is real, it is the
most important open question this study leaves, and it cannot be tested on
public process-mining data. We report the search rather than the regret.""")

edit("limits-construct", r"""\paragraph{Construct and mechanism.}
Reassignment is a proxy for misrouting and also fires on legitimate
escalation; the within-item shuffle preserves item membership but not other
correlates of identity, so it bounds the proxy share rather than isolating
it; and the opening group's distribution drifts between our halves. After
this round's withdrawals, we do not claim a measured direction for the
mechanism.""",
     r"""\paragraph{Construct and mechanism.}
Reassignment is a proxy for misrouting and also fires on legitimate
escalation; the within-item shuffle preserves item membership but not other
correlates of identity, so it bounds the proxy share rather than isolating
it; and the opening group's distribution drifts between our halves. After
round sixteen's withdrawals, we do not claim a measured direction for the
mechanism.

\paragraph{The corpus measures a different target from the rest of the paper.}
Section~\ref{sec:corpus} applies a generic handover target so that one rule
can run on twenty-two logs. On the primary log that target and the log's own
reassignment count agree on $46.0\%$ of incidents. The corpus therefore bounds
the generality of the \emph{estimand and the practice}, not of this paper's
particular magnitude, and we say so there rather than letting thirteen log
names imply thirteen replications.

\paragraph{What is still outside reach.}
No deployment, no organisational partner and no practitioner validation; a
single author with no institutional affiliation; public benchmark data whose
newest log is from 2019. None of the four is fixable by further analysis and
we would rather state them than have them inferred.""")

# ================================================================ corrections
edit("corrections-head", r"""Eight errors of our own are reported as results rather than
edited away, because each is an
instance of the failure this paper is about --- a control, a claim or a
baseline asserted rather than checked --- and because the pattern across them
is more informative than any one.""",
     r"""Eleven errors of our own are reported as results rather than
edited away, because each is an
instance of the failure this paper is about --- a control, a claim or a
baseline asserted rather than checked --- and because the pattern across them
is more informative than any one.""")

edit("corrections-add", r"""\item \textbf{A control run on one of the two rungs it bounds.} The
shuffled-item encoder null was run on the group-aware rung only, while the
reduction it is meant to bound is computed from two rungs, and its residual
under boosting is eleven standard errors from zero rather than noise. Run on
both rungs, the correction moves the boosting reduction by $3.4$ percentage
points, and upward (Section~\ref{sec:admission}).
\end{enumerate}

Six of the eight flattered the result, one --- the dataset claim ---
excused its principal limitation, and one, the eighth, would have made the
result larger had we noticed it earlier. We draw the obvious inference about
the direction in which unchecked assertions travel, and note that the paper's
verification apparatus, which recomputes every number it prints, would not
have caught any of them: all eight are claims about what a number
\emph{means}.""",
     r"""\item \textbf{A control run on one of the two rungs it bounds.} The
shuffled-item encoder null was run on the group-aware rung only, while the
reduction it is meant to bound is computed from two rungs, and its residual
under boosting is eleven standard errors from zero rather than noise. Run on
both rungs, the correction moves the boosting reduction by $3.4$ percentage
points, and upward (Section~\ref{sec:admission}).

\item \textbf{An extremum that was the worst of the points we had named.} We
wrote that the group-aware increment turns negative, ``reaching $-16.1$
$[-23.0,-8.9]$ per thousand at $p_t=0.50$''. The word \emph{reaching} names an
extremum. The extremum is $-21.1$ $[-27.7,-14.4]$ at $\theta=0.525$, which is
$31\%$ larger; $0.50$ was in the list of five thresholds our own table
happened to name and $0.525$ was not. Every literal in that sentence was
correct and was computed from a file already in the repository
(Section~\ref{sec:dca}).

\item \textbf{A count and a run reported as the same set.} We wrote that the
increment is resolvably positive ``at $20$ points, in a contiguous run from
$0.100$ to $0.425$''. Fourteen are in that run; six sit at $0.675$ and above.
Counting a set and describing an interval are different operations and this
sentence performed one and reported the other (Section~\ref{sec:dca}).

\item \textbf{An open question we left open with the evidence one download
away.} The previous version reported that it could not establish whether the
knowledge-article reference is available at incident creation, named the file
that would settle where the field comes from, and did not obtain it. The file
is in the same public collection as the three we used. Obtaining it shows the
reference is written by the service desk on calls that never become incidents
at all, and admitting it takes our headline from $+0.103$ to $+0.001$
(Section~\ref{sec:failed}). We record this as a correction rather than as
progress because the paper's own thesis is that an unexamined admission
decision sets the answer, and we left ours unexamined for a round.
\end{enumerate}

Eight of the eleven flattered the result, one --- the dataset claim ---
excused its principal limitation, one would have made the result larger had we
noticed it earlier, and one removed the result altogether. We draw the obvious
inference about the direction in which unchecked assertions travel.

Two of the three found this round are worth separating out, because they are a
kind the apparatus was built to catch and could not. The paper is checked by a
program that re-derives every numeric literal from a result file, and a
corruption suite of $149$ mutations that has found eight holes in that
program. Every literal in corrections nine and ten passed: $-16.1$, $-23.0$,
$-8.9$, $0.50$, $20$, $0.100$ and $0.425$ are all correct values sitting in
correct places. What was wrong was the relation the prose asserted between
them --- an extremum in the first case, a set-equals-interval identification in
the second. A checker that verifies numbers and not the words joining them
will certify both. The checker now compares the named extremum against the
extremum and the stated count against the run length, and the general lesson
--- that a directional word is a claim and needs a check of its own --- is the
one this project keeps relearning.""")

# ================================================================= conclusion
edit("conclusion", r"""What configuration data contributes to this task is a stable identifier under
which outcome history accumulates, not the configuration attributes a CMDB is
usually bought for: a per-item outcome rate with no model reaches $0.744$
against the full model's $0.748$, and a $256$-way service-component grouping
captures three quarters of what instance-level identity is worth, with
instance identity adding $+0.023$ over it. The layer an organisation is
buying, and not the fact of buying, is what the measured value turns on.

The size of that measured value is set by a second choice. Knowing which
configuration item an incident concerns is worth $+0.183$ or
$+0.103$ AUC for predicting reassignment, depending on whether the baseline
includes one field the organisation already records: which group logged the
ticket. The reduction runs $36.1\%$ to $48.3\%$ across the design space, it
survives the admission of free congestion features, and the
pattern replicates on a second organisation. The
difference is an overlap --- a model given the item has already been told
most of what the group would say --- so a business case built on the first
figure is measuring a CMDB plus a field the organisation was already
recording for nothing.

Three qualifications belong in the same breath. Which figure is right depends
on an admission line we cannot draw principledly: admit the service component
instead and the number is $+0.023$. Stated operationally rather than as AUC,
the overstatement is far smaller than we previously reported --- $1.07$ at
the threshold where the item is worth most --- and we withdraw the factor of
$4.3$ that an earlier version printed. And in a band of thresholds above the
base rate, the item is worth nothing at all over a group-aware baseline. The
transferable claim is not a number. It is that the number is chosen, and that
whoever writes the business case is choosing it.""",
     r"""What a recorded field is worth is not a number. It is
$V(f \mid B, m, \theta)$, and on this decision every one of those arguments
moves the answer by more than the effect we set out to report.

Vary the baseline: knowing which configuration item an incident concerns is
worth $+0.183$ AUC against four intake fields, $+0.103$ once one further field
the organisation already records is admitted, and $+0.001$
$[-0.002,+0.003]$ once a second is. Vary the metric on those same scores: the
reduction runs $43.7\%$ to $60.3\%$ over six instruments, and the figure we
previously published is the smallest of them. Vary the operating point: it
runs $6.3\%$ to $119.2\%$, and in a band above the base rate the item is
resolvably harmful. Vary the register's population and the regime by which it
empties: at half population the item is worth $+0.082$ or $+0.064$ depending
on whether the tail or the core is missing. Vary how the organisation takes
work in: across intake mixes the reduction runs $6.3\%$ to $95.3\%$.

None of those variations is a defect in any instrument or an error in any
measurement. Each is correct about the question it asks. The point is that a
single number answers one of those questions without saying which, and that
the person writing the business case is the person choosing.

We tried to make the finding general and it did not go. A pre-registered
protocol over $22$ public logs admits $13$ and finds a resolvable reduction on
three; the registered generality claim is falsified and Section~\ref{sec:corpus}
reports it. What the corpus does establish is the precondition: the effect
needs an entity that predicts the outcome at all, and on most public process
logs there is not one. What we offer in its place is
Section~\ref{sec:standard}: a minimum reportable form for an incremental-value
claim, demonstrated on data where following it removes the paper's own
headline. That is the strongest evidence we can give that it is worth
following.""")

edit("ack", r"""The manuscript was subjected to sixteen rounds of adversarial review, the
later rounds machine-assisted, in which each round was asked to break the
previous version's claims; the corrections in Section~\ref{sec:corrections}
came from that process.""",
     r"""The manuscript was subjected to seventeen rounds of adversarial review, the
later rounds machine-assisted, in which each round was asked to break the
previous version's claims; the corrections in Section~\ref{sec:corrections}
came from that process. The protocol of Section~\ref{sec:corpus} was
registered in the repository before the analyses it governs were run, in a
commit that adds no result file.""")


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

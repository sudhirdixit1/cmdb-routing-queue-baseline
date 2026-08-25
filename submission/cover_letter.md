# Cover letter

**To:** the Editors, *Information Systems* (Elsevier)
**Manuscript:** *Specification Surfaces for Incremental Predictive
Performance: Estimation, Uncertainty, and Multi-Log Evaluation*
**Author:** Sudhir Dixit, Independent Researcher

---

Dear Editors,

I am submitting a manuscript that replaces an earlier one, *Four Choices
Behind One Number: Reporting the Incremental Value of a Recorded Field*, which
a referee for this journal recommended rejecting as submitted. The report was
unusually specific and I treated it as a design document rather than a list of
revisions; `response_to_referee.md` answers its ten major comments one by one.

The manuscript has since had **two further developmental reviews**. The first
recommended reject-and-resubmit and listed eight submission-blocking problems;
`response_to_blueprint.md` answers those. The second read the resulting
ninety-seven-page manuscript, recommended **major revision**, and noted that a
strict reviewer would recommend reject-and-resubmit on two of its comments
alone. `response_to_review21.md` answers its twelve major comments and its
eleven minor ones. Three of the twelve mattered more than the rest and I want
to say what they were before saying what the paper contributes.

- **The case study's headline number appeared twice with two values and two
  signs**, one of them Holm-rejected. It is the class of error the
  repository's whole verification apparatus exists to prevent, and the
  apparatus could not have caught it: each number was right about its own
  source file, and what was wrong was that two of them answered to the same
  English sentence. Section 7.1 now reconciles them one factor at a time from
  a purpose-built experiment, and the answer is a finding rather than an
  erratum: over the cohort-by-target design the **target** carries 99.3% of
  the difference and the cohort 0.008%. Two other candidate explanations were
  ruled out by computation rather than by argument. A new verifier condition
  now declares, for each quantity a reader would name in one phrase, which
  macros may hold it, and fails when two of them disagree.
- **Two of the paper's four reporting objects rested on bands the paper itself
  declared undercovering on its own corpus.** They are now computed under a
  critical value calibrated at each pair's own register cardinality, from a
  denser simulated plane, by a factor that is a quantile of the studentised
  error rather than a fitted fudge. The correction costs resolution and the
  manuscript prints both sets of labels so the cost is visible.
- **Ninety-seven pages, thirty of them about the project's own history of
  errors.** The appendices are now a separate supplementary document; the
  correction register, the literature pilot and the verification harness are
  in it; and the phrases "an earlier version of this work" and "correction
  Cnn" appear zero times in the article, which a linter now enforces.

The first developmental review's eight problems were not cosmetic either, and
four of them were the same kind of error, in which an *inferential object did
not match the sentence it was used to license*.

- A region label ranging over a whole surface was supported by a confidence
  band whose family was five instruments at **one cell**, and by a bootstrap
  grid that held fixed the design axis with the second-largest sensitivity
  index. The manuscript now distinguishes three surfaces by name, audits the
  denominator of each cell-for-cell, and takes the band over the family the
  claim ranges over.
- The reported "interaction share" was the largest per-axis *involvement*
  $\max_i(S_{T_i}-S_i)$. Those quantities overlap across axes and their
  maximum is not their union; the total higher-order share is $1-\sum_i S_i$,
  and on this corpus it is 56.0% against the 43.7% the old statistic gives —
  and against the 30.0% the earlier manuscript printed.
- Expected regret was averaged across five instruments whose units do not add,
  and reported as a single percentage. It is now computed inside one
  instrument at a time, with a common-utility version on calibrated net
  benefit, and evaluated out of sample rather than on the surface the loss
  averages over.
- The rank-invariance proposition was stated more widely than its proof
  reached. Proving it generally showed the statement was also **false**: what
  invariance of the reduction requires is that a recalibration act *affinely*
  on the instrument, and the manuscript now exhibits a non-rank-based
  instrument whose reduction is invariant.

Each of those changed a number in the abstract. All four are in the correction
register, grouped by the class of mistake they belong to, because the classes
are more useful to a reader than the incidents.

**What the paper contributes.** A claim about what a recorded field is worth
to a prediction is a claim about one cell of a surface: the answer is a
functional of the baseline, the learner, the encoding, the target, the
temporal split, the field's availability at the decision time, the register's
quality, the metric and the operating point. The paper defines that surface,
and supplies four things that make it an object a reader can act on rather
than a grid to look at:

1. an exact functional-ANOVA decomposition of the surface's variance across
   design axes, so *which choice matters* becomes a measurement;
2. simultaneous max-$t$ confidence bands from a moving-block bootstrap that
   refits the entire pipeline inside every draw, so a statement about a whole
   decision curve has family-wise coverage and the interval contains the
   model, not only the test rows;
3. *resolution regions* --- uniformly or conditionally beneficial, uniformly
   or conditionally harmful, sign-changing, unresolved --- with a scalar
   robustness index, which name the one state in which a single number is a
   safe summary;
4. *specification regret*, which measures what conventional one-number
   reporting gets wrong, on every eligible log rather than on the ones where
   the answer resolved.

**Why it is in scope.** *Information Systems* publishes evaluation
methodology for data-intensive systems, and this is an evaluation methodology
with a formal object, an estimator, inference, a benchmark and a software
implementation. The configuration management database that motivated the study
is now one case among nineteen log--target pairs, and is reported at greater
length only because it is the case in which the field's *availability at the
decision time* decides the answer.

**What the evidence says, and what it does not.** Over nineteen log--target
pairs from thirteen public event logs, across a design space whose denominator
is audited cell by cell, a conventional one-number report misstates the *sign*
of the increment for a large minority of the other admissible specifications.
No single design axis dominates the disagreement. Under a measure that lets a
reader roam the design space, the variance belonging to no single axis exceeds
every main effect; under one that keeps them at the reference specification it
does not, because a reader who never departs from the reference barely
activates an interaction. The paper reports that quantity correctly computed
and under four declared measures, and says which conclusions survive which ---
which is the point of declaring a measure at all. The paper does not claim to measure the
economic value of a register: it measures incremental predictive performance,
says so in the title of the quantity, and converts it into decision-analytic
units at a declared exchange rate rather than into money.

**Reproducibility.** Every number in the manuscript is a macro generated from
a result file, so a number cannot disagree between the abstract, a table and
the conclusion: there is one of it, and a linter fails the build if a numeric
literal appears in the prose. A separate checker re-derives each macro from its
source with independent code. The whole study --- fetch, analysis, numbers,
figures, verification, PDF --- runs from one command against a lockfile and a
container. The archive carries the pre-registrations, the amendment log, the
practice pilot's adjudications with a free-text reason for every judgement, and
a correction register grouping the author's own errors by class.

**What the apparatus found in itself.** After every one of the referee's ten
comments had been answered, four defects were found in this round's own work
by this round's own controls, and the manuscript reports all four rather than
quietly fixing them. The most serious is in Appendix H: the simulation
reported that every interval construction fails in one of its six worlds, and
the failure was in the *estimand*, not the estimator --- the simulation scored
the estimator against a population it does not sample from. It was found by
testing the two finite-sample explanations that an apparent bias implies, with
a control world that a genuine finite-sample gap does close, and having both
arms refuse. The others: a pilot frame size aggregated over the wrong index
set, which turned out to change what the pilot *is*; a strict mode that
certified a manuscript built from a superseded run; and a corruption in the
verifier's own regression suite that had been passing because nothing
regenerated between the corruption and the check. The correction register
groups the project's errors by class, and Appendix H's class is the one no
checker in the repository could have caught.

**The bootstrap validation.** The second review asked for the simulation to be
rebuilt at a size a methods claim can rest on, and it has been: a thousand
replicates in each of six worlds, sample size and register cardinality varied
jointly up to the 3,019-level regime the case study's own register occupies,
three block lengths around the rule of thumb, and seven interval constructions
compared including *m*-out-of-*n* subsampling in the sparse regime, which is
the standard alternative to the construction this paper uses. It is priced
against that construction in the regime that motivates it, and it loses: on
the sparse world the basic interval covers 89.9% and subsampling 72.8%, with
the percentile interval at 37.2%. That is a negative result about an
alternative we had reason to prefer, and the manuscript reports it as one.

**The same experiment produced a result against the paper, and the second
review was right that stating it was not enough.** Coverage of the interval
this paper reports is governed by the ratio of the register's cardinality to
the training row count, and this corpus lives where that coverage is below
nominal: the median pair sits at 0.106. The previous version reported that as
a limitation and left the region labels at their nominal critical value, which
means it published two objects it had just declared unreliable. This version
calibrates instead. The plane is estimated at twenty cells and five hundred
replicates over the range the corpus actually occupies; the factor by which an
interval must be widened to reach nominal coverage is derived in closed form
as a quantile of the studentised error, so it is computed rather than tuned;
and every region label and every robustness index in the article is the
calibrated one, with the nominal one printed beside it so the size of the
correction is visible. What the repair does not buy is stated in three clauses
in section 10, because a calibration estimated in a simulation and applied to
real logs is an assumption and should be labelled as one.

**Length and structure.** The article and its supplementary material are now
two documents. The supplement carries the protocol and its amendments, the
proofs, the constructions, the correction register, the per-layer and per-fold
results, the literature pilot, the diagnosis of the one simulated world where
the bootstrap misbehaves, the worked example, the verification harness, the
derivation of the coverage calibration, three results the article summarises
in a paragraph each, and the tables the article does not print.
Cross-references between the two resolve automatically, so neither document
guesses at the other's numbering. The article is self-contained without the
supplement.

The article was ninety-seven pages two rounds ago and seventy-one when the
second developmental review read it. It is now 58 pages, with
7 tables and five figures against twenty-three tables and seven
figures, and no line overruns its margin. About ten of those pages moved to
the supplement and about seven were restatement that came out: four sections
were describing the coverage calibration and one does now. The review asked
for thirty-five to forty pages, and the response letter sets out under M12 the
arithmetic that leaves the article above that — the same review asked, in its
first two phases, for eight new measurements, and those are about eight pages
of article — together with an ordered list of what the editor could cut next
and what each would cost.

**A pre-submission review.** Before submitting, the revised manuscript was
given to an independent reader with this journal's brief, no knowledge of what
had changed, and access to the repository to check any number they doubted. It
returned major revision with nine major comments, six of which were defects
rather than differences of opinion. All six are fixed and each is recorded in
`REFEREE-LOG.md` with the file and the number that establishes it. The worst
of them is worth naming here: on two log--target pairs the simultaneous band
quantified over pipeline levels the design declaration did not contain, so a
region label ranged over cells the design space says do not exist. The
declared surface was widened to match, the whole surface was recomputed, and
the verifier now asserts the subset relation *cell for cell* rather than by
level count, which is the only version of the check that would have caught
it.

The prose has been rewritten in a plainer register. The second review's
twelfth comment was that the manuscript reads as a running commentary on its
own previous versions and that this would strike a reader as combative rather
than transparent. It was right. The changelog is in the archive, the article
says so once, and a linter fails the build if either of the two phrases the
review named reappears in the main text.

**Where the argument is weaker than the apparatus, said plainly.** The second
review's fifth comment was that the practical stakes of "what one number
costs" are thin, and having tried the remedy it offered I agree with the
premise. The decision-analytic comparison now runs on a service desk's own
exchange rate, in net benefit per thousand cases, on models that pass a
registered calibration screen --- and the four collapse rules still mostly
tie. The article says so in a paragraph of its own and no longer describes the
regret comparison as the result a reader should carry away. What the section
does establish is sharper: a third of the models a published evaluation would
fit here cannot carry a threshold read as a cost ratio at all, and a desk that
adopted this register on its first-touch number and deployed it at incident
creation would be promised 1.71 true positives per thousand cases and receive
0.003. That difference is larger than every difference between the four rules
put together, and it is a difference about the *decision time*, which is the
axis this paper adds.

**What I did not manage.** Stated here rather than left to be found. The
surface on which bands are computed is smaller than the surface on which point
estimates are computed. The coverage calibration is estimated on a pointwise
interval in a simulation and applied to a simultaneous band on real logs. The
model family and the encoding are crossed on one log only, where the result is
that the encoding matters about twice as much as the family and their
interaction is the largest two-way term --- which is a reason to want the
crossing everywhere and not evidence that it transfers. The stationarity and
mixing the moving-block bootstrap needs are assumed rather than tested, and
the split point is fixed within a draw. The practice pilot still has one
machine-assisted adjudicator and is now in supplementary material with no
claim resting on it. And there is still no organisational partner with
timestamped field histories, so the configuration-management case remains a
benchmark case.

I confirm that this work is original, is not under consideration elsewhere,
has no funding to declare and no competing interests. The use of a
large-language-model assistant --- in the software, in the pilot's
adjudication, and in drafting and editing prose --- is declared in the
manuscript with the model identifier and dates, and `AI-USE.md` in the archive
is the register the declaration points at. It records that the identifier used
for the pilot's adjudication was not captured at the time, which is a
reproducibility defect in the pilot and is stated as one rather than filled in
from memory.

Thank you for considering it.

Sudhir Dixit

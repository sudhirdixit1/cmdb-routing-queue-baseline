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
unusually specific and I have treated it as a design document rather than a
list of revisions. The referee's own summary was that a strong version would
require a redesigned study and a substantially new manuscript. That is what
this is, and `response_to_referee.md` answers the ten major comments one by
one.

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
pairs from thirteen public event logs, a conventional one-number report
misstates the *sign* of the increment for a median 35% of the other admissible
specifications, and the rate is above 10% on eighteen of the nineteen. No
single design axis dominates the disagreement; the interactions between axes
carry more than any main effect. The paper does not claim to measure the
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
quietly fixing them. The most serious is in Appendix G: the simulation
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
groups the project's errors by class, and Appendix G's class is the one no
checker in the repository could have caught.

**Length and structure.** The manuscript follows the structure the referee
recommended and is within the length they asked for. The literature component
is now a clearly labelled pilot in one subsection, with its own measured error
rate, and no claim in the paper depends on it.

I confirm that this work is original, is not under consideration elsewhere,
has no funding to declare and no competing interests, and that the use of a
large-language-model assistant --- in the software, in the pilot's
adjudication, and in drafting --- is declared explicitly in the manuscript
rather than as the phrase "machine-assisted".

Thank you for considering it.

Sudhir Dixit

# Cover letter

**To:** the Editors, *Information Systems* (Elsevier)
**Manuscript:** *Specification Surfaces for Incremental Predictive
Performance: Estimation, Uncertainty, and Multi-Log Evaluation*
**Author:** Sudhir Dixit, Independent Researcher

---

Dear Editors,

I am submitting a methods paper on how the incremental predictive
performance of a recorded field --- what a register is worth to a prediction
--- should be reported. The claim is that such a number is a functional of
choices a report rarely states (the baseline, the pipeline, the target, the
split, the decision time, the register's population and the metric), that the
right object is therefore a *surface* over a declared design space, and that
a surface admits estimation and inference of its own. The paper supplies
three reporting objects for one: an exact functional-ANOVA decomposition of
the surface's variance that separates analyst choices from the resampling a
design contains; simultaneous max-*t* bands from a pipeline-refitting
bootstrap, at a critical value whose family-wise coverage is measured against
a known answer; and resolution regions with a robustness index, which say
where a sign is determined and withhold a direction where too little of the
surface resolves to support one.

**What the evidence says.** On 19 log--target pairs from 13 public event
logs, a median 71.7% of a pooled specification surface's variance is
resampling rather than analyst latitude, and net of it which analyst choice
leads is a property of the pair. A conventional one-number report is usually
right about the sign and usually silent about the size: where the data
determine a sign, admissible specifications sit a median 0.0600 AUC from the
conventional report. In a case study on a bank's configuration management
database, the register's worth turns on the decision time and its sign on the
target, and a desk that adopted the register on its first-touch number and
deployed it at incident creation would be promised 1.71 true positives
per thousand cases and receive 0.003.

**Why this journal.** *Information Systems* publishes evaluation methodology
for data-intensive systems, and this is one: a formal object, an estimator,
inference, a registered multi-log benchmark on public event logs, and a
software implementation. The configuration management database that motivated
the study is one case among nineteen and is reported at length because it is
the case in which the field's availability at the decision time decides the
answer, which is the axis the paper adds.

**History, and how this manuscript was reviewed.** An earlier manuscript,
*Four Choices Behind One Number*, was reviewed for this journal and the
referee recommended rejecting it as submitted; the report was specific and
`response_to_referee.md` answers its ten major comments one by one, and
`summary_of_changes.md` says by section what has changed since. Between that
report and this submission the manuscript was revised through internal
adversarial reviews that I conducted with a large-language-model assistant
reading each built PDF against the repository in the role of a referee. I say
so plainly because the archive carries those reviews and the letters that
answer them, and an editor who opens it should know what they are: they are
my own reviews, made with a tool, not reports from this journal's referees.
The manuscript's generative-AI declaration names that use beside the two
others (drafting and editing prose; writing the analysis and verification
code), with the model identifiers and dates in `AI-USE.md`.

**Reproducibility.** Every number in the manuscript is a macro generated from
a result file, so a number cannot disagree between the abstract, a table and
the conclusion, and a linter fails the build if a numeric literal appears in
the prose. A separate checker re-derives each macro from its source with
independent code and enforces the manuscript's own directional claims as
conditions. The whole study runs from one command against a lockfile and a
container whose base is pinned by digest; the archive records the measured
tolerance outside that container, because the results are not bit-reproducible
across processor architectures and a reproduction claim that holds only on
the author's machine is not one.

**Length.** The article is 56 pages with 8 tables and
3 figures; the appendices are a separate supplementary document.
The body's length is measured rather than defended: `summary_of_changes.md`
gives the per-section word counts and names, in order, what the editor could
cut next and what each cut would cost.

**Where the argument is weaker than the apparatus.** The coverage measurement
uses an ideal bootstrap, so it bounds the critical value's contribution and
not the resampling's; the pointwise interval underneath is governed by the
register's cardinality over the training size and undercovers where this
corpus lives, and the calibration that would widen it is reported as a
sensitivity rather than applied. Stationarity is measured and does not hold on
every pair; mixing is not tested. The model family and the encoding are
crossed on the eight IT-service-management pairs and not everywhere. The
case study is one bank's estate on one public log, with the availability
question at its centre settled by probability rather than by a timestamped
field history. And there is no organisational partner, so the configuration
management case remains a benchmark case.

I confirm that this work is original, is not under consideration elsewhere,
has no funding to declare and no competing interests.

Thank you for considering it.

Sudhir Dixit

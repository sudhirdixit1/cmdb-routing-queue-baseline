# Cover letter

**To:** the Editors, *International Journal of Forecasting*
**Manuscript:** *Specification Surfaces for Incremental Forecast
Performance: Estimation, Uncertainty, and Multi-Log Evaluation*
**Author:** Sudhir Dixit, Independent Researcher (title page; the
manuscript and the supplement are blinded)

---

Dear Editors,

I am submitting a methods paper on how the incremental forecast performance
of a candidate predictor --- what a recorded field adds to a forecast ---
should be reported. The claim is that such a number is a functional of
choices a report rarely states (the baseline, the pipeline, the forecast
target, the split, the forecast origin, the predictor's population and the
score), that the right object is therefore a *surface* over a declared
design space, and that a surface admits estimation and inference of its own.
The paper supplies three reporting objects for one: an exact
functional-ANOVA decomposition of the surface's variance that separates
analyst choices from the resampling a design contains; simultaneous max-*t*
bands from a pipeline-refitting bootstrap, at a critical value whose
family-wise coverage is measured against a known answer; and resolution
regions with a robustness index, which say where a sign is determined and
withhold a direction where too little of the surface resolves to support
one.

**What the evidence says.** On 19 log--target pairs from 13 public event
logs, a median 71.7% of a pooled specification surface's variance is
resampling rather than analyst latitude, and net of it which analyst choice
leads is a property of the pair. A conventional one-number report is usually
right about the sign and usually silent about the size: where the data
determine a sign, admissible specifications sit a median 0.0600 AUC from the
conventional report. In a case study on a bank's configuration management
database, the register's worth turns on the forecast origin and the sign of its
point estimate on the target, and a desk that adopted the register on its first-touch number
and deployed it at incident creation would be promised 1.71 true positives
per thousand cases and receive 0.003.

**Why this journal.** The question is one the forecasting literature has
asked of a single specification at a time --- whether a predictor adds
accuracy to a model that nests the one without it --- and of a family of
specifications through the reality check, the test for superior predictive
ability and the model confidence set. This paper takes a different object
from those tests: not whether the family contains a member that beats a
benchmark, nor which members survive, but the shape of the family's
increment, with its uncertainty, and what the conventional report costs
against it. Evaluation of forecasts, forecast uncertainty and its effect on
decisions are on the journal's list of topics, and the decision-analytic
section reads the same surface in net benefit, the decision-based value of a
forecast. The forecasts are probability forecasts of a binary event at a
declared origin, scored on a held-out later period; they are not time
series, and the paper says so where it defines them.

**History.** An earlier manuscript on this question, *Four Choices Behind
One Number*, was reviewed for *Information Systems* (Elsevier) and the
referee recommended rejecting it as submitted; the ten major comments were
answered in a revision, which became the present paper. The present paper
was then declined by that journal's Editor-in-Chief at the editorial stage
on 10 September 2026 without referee comments, with the sentence: "Your very
nice paper should be sent to a forecasting journal where your treatment of
the value of a feature may give new insight." The referee's ten major comments, as
summarised, and the answers to each are in the archive. Between those two decisions the
manuscript was revised through internal adversarial reviews that I conducted
with a large-language-model assistant reading each built PDF against the
repository in the role of a referee; the archive carries those reviews and
the letters that answer them, and they are my own reviews made with a tool,
not reports from any journal's referees. The generative-AI declaration on
the title page names that use beside the others (drafting and editing
prose; writing the analysis and verification code; the literature pilot's
adjudication, which the supplement declares where it is described), with
model identifiers and dates in `AI-USE.md`.

**Related manuscripts.** No other manuscript based on these methods or data
is published or under review. An earlier conference-format draft, kept in
the repository's history, was never submitted.

**Data and code.** Every event log is public and obtained by DOI. Code,
derived results, the registered protocols, the amendment log and the
verification harness are archived at Zenodo, DOI 10.5281/zenodo.22557927
(release v28.0), and developed at
`https://github.com/sudhirdixit1/cmdb-routing-queue-baseline`. The archive holds
every analysis result file byte for byte (its harness's bookkeeping files
post-date it), and its own script
`scripts/verify_release.py` demonstrates that a clean checkout regenerates
every analysis number from those results; the manuscript source, the figures
and the generators as submitted are at the repository's head, which
post-dates the archive with the retargeting edits and with the corrections
to how a summary is computed (a rate's minimum, two layer values, a seed
count) that the supplement's correction register records. The reproducibility
check the journal runs at acceptance can be run from `REPRODUCE.md` with one
command against a lockfile and a container whose base is pinned by digest;
the archive records the measured tolerance outside that container, because
the results are not bit-reproducible across processor architectures.

**Reproducibility inside the manuscript.** Every number is a macro generated
from a result file, so a number cannot disagree between the abstract, a
table and the conclusion, and a linter fails the build if a numeric literal
appears in the prose. A separate checker re-derives each macro from its
source with independent code and enforces the manuscript's own directional
claims as conditions.

**Length.** The article is 54 pages in the journal template's setting
(11-point, 1.5 line spacing), with 8 tables and 3 figures; the appendices
are a separate supplementary document, and nine passages were moved there
for this submission. All three figures in the article are greyscale and
are supplied as vector PDF; online colour is not needed.

**Where the argument is weaker than the apparatus.** The coverage
measurement uses an ideal bootstrap, so it bounds the critical value's
contribution and not the resampling's; the pointwise interval underneath is
governed by the register's cardinality over the training size and
undercovers where this corpus lives, and the calibration that would widen it
is reported as a sensitivity rather than applied. Stationarity is measured
and does not hold on every pair; mixing is not tested. The model family and
the encoding are crossed on the eight IT-service-management pairs and not
everywhere. The case study is one bank's estate on one public log, with the
availability question at its centre settled by probability rather than by a
timestamped field history.

**Suggested referees** are listed in the separate file, with the reason for
each.

I confirm that this work is original, is not under consideration elsewhere,
has no funding to declare and no competing interests.

Thank you for considering it.

Sudhir Dixit

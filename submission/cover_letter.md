# Cover letter

**To:** the Editors, *International Journal of Forecasting*
**Manuscript:** *Specification Surfaces for Incremental Forecast
Performance: Decomposition and Simultaneous Inference for Nested Probability
Forecasts*
**Author:** Sudhir Dixit, Independent Researcher (title page; the
manuscript and the supplement are blinded)

---

Dear Editors,

I am submitting a paper on forecast evaluation: how to report whether a
candidate predictor improves out-of-sample probability forecasts over a
nested benchmark. The usual report is one score difference, yet that
difference depends on choices the forecaster rarely states --- the
benchmark, the model class, the sample split, the forecast origin, the
predictor's completeness and the scoring rule. The paper treats the
incremental performance as a surface over a declared design space and
supplies three reporting objects for it: an exact variance decomposition
that separates the evaluation split, with its sampling variability and
fold-to-fold instability, from the forecaster's other choices; simultaneous
bootstrap bands over a declared family of specifications, with family-wise
coverage measured by simulation; and resolution
regions that state where the sign of the improvement is determined.

**What the evidence says.** On 19 pre-specified binary forecasting tasks
from 13 public business-process event logs, most of them from IT service
desks and public administration, a median 71.7% of a pooled surface's
variance comes from the evaluation split and its interactions rather than
from the forecaster's other choices. A conventional one-number report
usually has the right sign but does not show how far other defensible
specifications lie from it: where the data determine a sign, resolved
specifications lie a median 0.0600 AUC from it. In a case study of incident
reassignment at a bank's IT service desk, the predictor's value depends on
what the forecast origin makes known: a desk that adopted it on its
performance against the arrival attributes alone, and deployed it where the
assignment group and the knowledge reference are already recorded, would be
promised 1.71 net true positives per thousand cases on the pre-specified
handover target and receive 0.003.

**Why this journal.** The paper extends forecast-evaluation work this
journal publishes. Its question --- does adding a predictor improve
out-of-sample forecasts over a nested benchmark --- is Clark and
McCracken's, asked for many candidate predictors at once by Gonzalo and
Pitarakis (IJF, 2024) and as marginal predictive content by Liu and Swanson
(IJF, 2024). Its concern, that the answer depends on the evaluation design,
is the one Rossi and Inoue and Hansen and Timmermann raised for the window
and the split, and that Bańbura and Bobeica (IJF, 2023) met for the Phillips
curve. Where the reality check and the model confidence set control a search
for the best model, this paper reports how a fixed predictor's increment
varies across the design, with inference over a declared family. The
forecasts are case-level probability forecasts of binary events, evaluated
with proper scores and ROC measures, as in Dimitriadis et al.
(IJF, 2024), and with net benefit; the application sits beside the call-centre and
emergency-department forecasting the journal publishes (Ibrahim et al., IJF,
2016; Rostami-Tabar and Ziel, IJF, 2022).

**History.** An earlier version of this work was submitted to *Information
Systems* (Elsevier), reviewed, and revised in response to the referee's
comments; the revised manuscript was declined by that journal's
Editor-in-Chief on 10 September 2026 as better suited to a forecasting
journal. It has since been rewritten for this readership.

**Related manuscripts.** No other manuscript based on these methods or data
is published or under review. An earlier conference-format draft, kept in
the repository's history, was never submitted.

**Data and code.** Every event log is public and cited by DOI. Code, derived
results, the pre-specified protocol and its amendment log are archived at
Zenodo (DOI DOI-PENDING, release v29.0), with the development
repository named on the title page. The journal's
reproducibility check (Pinson et al., IJF, 2026) can be run from
`REPRODUCE.md` with one command, in a container whose base image is pinned
by digest.

**Format.** Proofs, the protocol and secondary results are in a separate
supplementary document; the article is self-contained and the supplement
is reference material. The article's figures are greyscale. Generative-AI
use is declared in the manuscript.

**Suggested referees** are listed in the separate file, with the reason for
each.

I confirm that this work is original, is not under consideration elsewhere,
has no funding to declare and no competing interests.

Thank you for considering it.

Sudhir Dixit

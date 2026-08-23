# AUDIT-PROTOCOL-2 — the practice pilot, registered

**Status:** registered. Committed before any paper in the round-nineteen frame
was screened. The commit that adds this file adds no result file; `git log
--stat` is the check.

**What this is.** A *machine-assisted prevalence pilot*, not a systematic
review. Its purpose is to put a size and an error bar on a question the
manuscript raises — are the axes the manuscript varies varied in published
work? — and to be honest enough about its own accuracy that no claim in the
manuscript needs to rest on it.

A referee for *Information Systems* listed eighteen defects in the
round-eighteen version of this audit and offered two dispositions: rebuild it
as a proper systematic empirical study, or reduce it to a clearly labelled
exploratory pilot that does not support a field-wide claim. This protocol does
as much of the first as one author can honestly do and the manuscript takes
the second.

---

## 1. The estimand

Over the population of published articles that **report the incremental
predictive performance of a named feature or feature group against a stated
comparison model, on a quantitative performance metric**, the share that

* `B_stated` — state the composition of the comparison model's feature set;
* `B_justified` — argue for what the comparison model excludes;
* `M_justified` — argue for the metric;
* `Theta_stated` — state an operating point, or integrate over one explicitly;
* `Range_reported` — report the increment across a *range* of a design choice,
  and separately for each of the four axes: baseline, metric, operating point,
  register population.

A confidence interval is **not** a range over a choice, and a code is not
assigned for one.

## 2. The frame and the sample

**2.1 Strata.** Nineteen venue strata (the four of round eighteen plus fifteen
information-systems, software-engineering, decision-support, applied-machine-
learning and clinical-informatics venues in which a paper of this kind would
plausibly appear); two citation strata seeded on predictive-process-monitoring
benchmarks; three topic strata. Publication years 2015–2026, type `article`,
open access, with a declared topical keyword filter on title and abstract for
the venue strata.

**2.2 Enumeration.** Every stratum is enumerated in full by cursor and cached
to disk, keyed by stratum and filter string, so an interruption costs one
stratum rather than all of them.

**2.3 Allocation.** `n_h = max(25, round(2400 * N_h / N))`, capped at `N_h`,
scaled down proportionally if the total exceeds the budget of 2,400. Declared
before the enumeration finished. The design weight is `N_h / n_h` and every
estimate uses it.

**2.4 Deduplication.** On DOI where present, else on the index identifier,
before sampling.

## 3. Retrieval

Full text is retrieved as PDF from the open-access locations the index
records, extracted to text, and cached. A record is retained if the extraction
yields at least 6,000 characters over at least 4 pages. Records already
retrieved for the round-eighteen frame are reused rather than re-downloaded:
the retrieval is the same operation on the same DOI.

## 4. Screening

A mechanical screen, whose patterns were fixed in `scripts/r40_audit.py`
before the first paper of round eighteen was read and are **not modified for
round nineteen**, admits a record if

* (M) some sentence carries a performance-metric term beside a number that is
  not inside a citation marker; and
* (A) some sentence states an incremental or ablation comparison of a feature
  or feature set, and that sentence is about performance rather than about the
  literature.

## 5. Adjudication — the two-stratum design

This is the part that is new, and it is the part that makes the estimates
usable.

**5.1 Stratum 1 (census).** Every record the screen admits is adjudicated
against its full text.

**5.2 Stratum 2 (probability sample).** A random sample of the records the
screen *rejects* is adjudicated too, so that the screen's **misses** are
counted rather than assumed away. Round nineteen draws 120 of them.

**5.3 The evidence dossier.** Each adjudication is made from a dossier
extracted from the full text: the paper's identity, the head of the text, the
sentences carrying a performance metric beside a number, the sentences the
screen fired on, and the neighbourhood of every mention of each coded concept.
Dossiers are committed to `data/audit2/dossiers/`.

**5.4 The judgement.** Eligibility first; then, for eligible records, the five
codes and the applicability code. Every judgement carries a free-text reason.
`unclear` is a value the adjudicator assigns when the dossier does not settle
the question; it is reported separately from `no`.

**5.5 The applicability code.** `applic_register` is `yes` when the
incremental feature is a lookup into an external register or reference source,
distinct from the transactional record itself, whose per-case coverage can be
incomplete. The `Range_reported` code for the register-population axis is
reported over that denominator and not over all eligible records.

**5.6 What this is not.** One adjudicator, machine-assisted. Not two
independent human raters. The dossiers are committed so the judgements can be
re-examined against exactly what they were made from; that is transparency,
not independence, and the manuscript says so.

## 6. Estimation

**6.1 Screen accuracy.** With `tp` confirmed eligible in stratum 1, `fp` the
rest of stratum 1, and stratum 2 weighted up by the reciprocal of its sampling
fraction to `fn_hat` and `tn_hat`:

    sensitivity = tp / (tp + fn_hat)
    specificity = tn_hat / (tn_hat + fp)
    precision   = tp / (tp + fp)

with Wilson intervals on the implied counts.

**6.2 Prevalence.** Each code's prevalence is a weighted proportion over the
union of the eligible records in both strata, with stratum-2 records carrying
their sampling weight. Intervals are Wilson intervals on Kish's effective
sample size, so a weighted estimate is not reported as though it carried the
information of an unweighted one.

**6.3 Why not Rogan–Gladen.** A classifier-error correction of the
Rogan–Gladen kind repairs a point estimate observed through an imperfect
screen. The two-stratum design here observes the truth directly in both
strata, which is strictly more informative, so the correction is not needed
for the point estimate and its interval would be wider than necessary.
`scripts/s06_audit2.py` retains the correction as a documented function for
comparison.

**6.4 Missing full text.** Retrieved and unretrieved records are compared on
every characteristic the metadata carries, and the eligibility rate is bounded
under the extreme assumptions that none and that all of the unretrieved are
eligible.

**6.5 Resolution.** The sample size required for a half-width of 5, 7, 10, 15
and 20 percentage points on a proportion near one half is reported beside the
achieved effective sample size. This is the pilot's binding limitation.

## 7. Reporting

PRISMA-style flow with every exclusion reason; screen accuracy; weighted
prevalence per code with intervals; applicability-specific denominators;
missing-data comparison and bounds; the resolution table. All in
`results/s06_*.csv` and reproduced by

    python scripts/s06_audit2.py --frame --fetch --screen --dossiers --report

## 8. Amendments

Any change to sections 1–7 after the first screening run is recorded here with
its date, its cause and the result it moved.

*(No amendments to date.)*

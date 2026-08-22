# Pre-registered protocol: how the field reports the incremental value of a field

**Registered:** 2026-08-22, round eighteen
**Registered by:** committed to `round-eighteen-reviewer-proof` **before** a
single paper was screened or coded. The commit that adds this file adds no
row of `results/r40_*.csv` and no downloaded full text, and the commit message
says so. A reader who does not believe that can check: `git log --stat` shows
this file arriving alone.

**Why this exists.** The paper's central premise is that four choices behind a
feature-value number are almost never stated. That premise has been argued
from examples. An argument from examples is what a referee calls *assembling
known critiques*. This document fixes, in advance, a frame, an inclusion rule
and five mechanical codes, so that the premise is either **measured** or
**refuted** — and the refutation is the outcome this project would find most
important, because it would mean the paper is wrong about the field.

---

## 1. The claim to be tested

> Among published papers that report the incremental value of a feature, a
> field, a feature group or a data source, a large majority state **none** of
> the four choices, and almost none report a range over any of them.

**Operationalised.** Over the included set, the proportion coding `yes` on each
of `B_stated`, `B_justified`, `M_justified`, `Theta_stated`, `Range_reported`,
and the proportion coding `yes` on **zero** of the four choice-related codes.

**What would refute it, stated now.** If a majority of included papers code
`yes` on `B_stated` *and* a majority code `yes` on `M_justified`, the premise
is wrong as stated and the paper must say so in those words, reframe around
the CMDB null, and report this audit as the finding that forced it.

---

## 2. The sampling frame

Enumerated through the **OpenAlex** API, which is open, free and
machine-enumerable; every query below is executed verbatim by
`scripts/r40_audit.py` and its raw response counts are written to
`results/r40_frame.csv`.

### 2.1 Frame A — a fixed venue set

Works with `type:article`, `publication_year:2019-2026`,
`open_access.is_oa:true`, whose `primary_location.source.id` is one of:

| venue | OpenAlex source |
|---|---|
| *Information Systems* (Elsevier) | `S193006928` |
| *Decision Support Systems* | `S11479521` |
| *Information & Management* | `S38883057` |
| *Empirical Software Engineering* | `S109852484` |

and which pass the **declared topical pre-filter**, applied by OpenAlex to
title and abstract:

    (predict OR prediction OR predictive OR classifier OR classification
     OR "machine learning" OR AUC OR forecasting)

The pre-filter is part of the frame, not a screening step. It is declared
here, applied by the index rather than by us, and its effect is reported: the
frame table carries the count before and after it for every venue.

### 2.2 Frame B — everyone citing the benchmark

Works with `publication_year:2019-2026`, `open_access.is_oa:true`, citing
either OpenAlex record of Teinemaa et al.'s outcome-oriented predictive
process monitoring benchmark: `W2964066696` (TKDD 2019) or `W2737745668`
(the 2017 preprint of the same work).

### 2.3 The conference venues, and why they are not enumerated directly

`PLAN-REVIEWER-PROOF.md` §2.2 names BPM, ICPM and CAiSE in the venue set.
**They are not machine-enumerable in OpenAlex and this protocol does not
pretend otherwise.** Measured on 2026-08-22, before any screening:

- BPM (`S4306417875`): 69 works 2019–2026, **0** flagged open access.
- CAiSE (`S4306418014`): 1 work 2019–2026, 0 open access.
- ICPM: no source record; a `sources?search=ICPM` query returns an unrelated
  mechanical-engineering serial.

Most BPM/ICPM/CAiSE papers are indexed under the umbrella LNCS source
(`S106296714`, 607,806 works), which cannot be filtered to a conference. A
frame that cannot be reproduced is not a frame. **These venues are therefore
covered through Frame B**, which is dominated by the same community, and the
venue mix of the included set is reported *whatever it turns out to be*,
including the possibility that the conference literature is under-represented.
That is a limitation of the frame and is reported as one.

### 2.4 The cap, and the sample

The two frames are unioned and deduplicated on DOI (lowercased, with any
`https://doi.org/` prefix stripped); where a work has no DOI, on its OpenAlex
id.

**Cap: N = 600.** If the deduplicated frame exceeds 600, a simple random
sample of 600 is drawn with `numpy.random.default_rng(20260819)` — the seed
every script in this repository uses — after sorting the frame by OpenAlex id
so the draw does not depend on the order the API happened to return. Never by
convenience, never by relevance rank, never by citation count.

---

## 3. Full text, and the stage that will lose the most papers

A code without a quote is not evidence, so **a paper that cannot be read in
full is not coded**. Retrieval is attempted, in this order, and the first
success wins:

1. `best_oa_location.pdf_url`
2. every other `locations[].pdf_url`
3. for a `10.1007/…` DOI, `https://link.springer.com/content/pdf/<doi>.pdf`
4. for a work with an arXiv id in `locations`, the arXiv PDF
5. `best_oa_location.landing_page_url`, accepted only if it returns a PDF

Each attempt gets one try and a 45-second timeout. A response is a full text
iff it is `application/pdf`, parses under PyMuPDF, and yields **at least 6,000
characters of extracted text over at least 4 pages** — a scanned page image
that yields no text is not a full text and is recorded as `NO_FULLTEXT`, not
silently coded `no`.

**This stage is expected to lose a large share of the frame and its size is a
reported number, not a footnote.** Papers lost here are lost for a reason
nobody can show is correlated with the codes; the argument that it might be is
written into the Limitations rather than assumed away.

---

## 4. The inclusion rule

> A paper is **included** iff it reports, anywhere, a quantitative comparison
> of predictive performance *with* and *without* a named feature, field,
> feature group or data source.

Implemented as two conditions on the extracted full text, **both** required:

- **(M) a performance metric is reported**: the text contains at least one of
  a declared metric lexicon (`AUC`, `AUROC`, `ROC`, `F1`, `F-measure`,
  `precision`, `recall`, `accuracy`, `MCC`, `Brier`, `average precision`,
  `AUPRC`, `MAE`, `RMSE`, `R2`) **and** at least one numeric result in a
  results-like context.
- **(A) an ablation-like construction is present**: at least one sentence
  matching the declared pattern set in `r40_audit.py`'s `ABLATION_PATTERNS`,
  which is fixed in that file before the first paper is screened. The classes
  are: *with/without*, *adding/removing a feature*, *ablation*, *feature set
  comparison*, *with the X feature the model improves by*, *inclusion of X
  increases/decreases*, *excluding X*, *contribution of the X feature*.

**Exclusions are recorded with a reason**, one of `NO_FULLTEXT`, `NO_METRIC`,
`NO_ABLATION`, `PARSE_FAILED`, in `results/r40_screening.csv`. Every included
paper's record carries the **matching sentence** that admitted it, so the
inclusion decision is as auditable as the codes.

---

## 5. The coding sheet

Five items per included paper. Each is `yes`, `no` or `unclear`; `unclear` is a
legitimate value, is reported separately from `no`, and is **never** folded
into `no` in any proportion this paper prints.

| code | question | mechanical rule |
|---|---|---|
| `B_stated` | Is the baseline's feature set enumerated? | The text names the baseline's features — an enumeration, a named feature table, or a declared feature-set list — in the ablation's neighbourhood or in a features section. |
| `B_justified` | Is the choice of which already-available fields to *exclude* from the baseline argued? | An explicit sentence giving a reason for leaving an available field out; an implication does not count. |
| `M_justified` | Is the metric argued for, rather than only named? | A reason is given for the reported metric over others: class imbalance, cost, comparability, or prior work's choice argued rather than inherited. |
| `Theta_stated` | Is an operating point or a cost ratio stated? | A threshold, a capacity, a cost or utility ratio, or an explicit statement that the metric integrates over the operating range. |
| `Range_reported` | Is the incremental value reported as a range or a surface over any of the four choices? | An interval over a **choice** — several baselines, several metrics, several thresholds, several population levels — reported *for the increment*. A confidence interval is **not** a range over a choice and codes `no`. |

**Every `yes` carries a verbatim quote and a page number, or it is `unclear`.**
The quote is the sentence that matched, truncated at 300 characters, stored
with the 1-based **PDF page index** it was found on. The PDF page index is not
always the printed journal page; the coding sheet's column is named
`pdf_page` and the paper says so.

The patterns implementing each rule are in `r40_audit.py` as `CODE_RULES`,
are fixed before the first paper is coded, and are published with the paper.

**Where a rule has to be interpreted, the case is recorded.** Any paper whose
code changes between the two implementations of §7 is listed with both codes.

---

## 6. What is reported

1. The frame, per venue, before and after the topical pre-filter.
2. The **screening funnel**, PRISMA-style: enumerated → deduplicated →
   sampled → full text retrieved → included, with every exclusion reason
   counted.
3. Each of the five codes as a proportion of the included set, with a Wilson
   binomial 95% interval, and the `unclear` share reported beside it.
4. The **joint distribution**: how many included papers state zero, one, two,
   three or four of the four choice-related codes (`B_stated`, `M_justified`,
   `Theta_stated`, `Range_reported`; `B_justified` is a strictly harder form
   of `B_stated` and is reported separately, not double-counted).
5. The venue and year distribution of the included set.
6. **A worked example of the consequence**, on one included paper whose data
   is public, showing what its reported increment would look like as a
   surface. The point is that the practice is universal; **the example names
   no defect in that paper and does not impugn its authors**, and the sentence
   saying so goes in the paper next to the example.

---

## 7. Reliability, with one author

One author cannot compute inter-rater reliability and a referee will say so.
Four things are done instead, all fixed here in advance.

1. **Every code ships with its quote and page**, so the coding is auditable
   rather than trusted. `results/r40_coding.csv` is supplementary material.
2. **A second, independently written implementation of the same five rules**
   (`CODE_RULES_B` in `r40_audit.py`, written against the §5 prose rather than
   against `CODE_RULES`) is run on a random 20% of the included set, drawn
   with the same seed. Agreement is reported as Cohen's kappa per code, with
   every disagreeing paper listed. This measures what inter-rater reliability
   measures — whether the rule survives a change of operationalisation — and it
   is obtainable by one author. It is **not** inter-rater reliability and the
   paper will not call it that.
3. **A validation subsample.** Twenty included papers, drawn with the same
   seed, have every code checked against the paper's own text by reading the
   surrounding context; agreement with the mechanical coder is reported as a
   confusion count per code. Disagreements are reported and **the mechanical
   code is not silently overwritten**: the sheet carries both.
4. **The seven-day blind re-code by the author is an owner action**, because
   it needs elapsed time and a human coder. It is written into
   `submission/OWNER-ACTIONS.md` with the exact procedure and the random 20%
   already drawn and recorded, so it can be executed without re-deciding
   anything.

The limitation is stated in the paper's Limitations section in the referee's
own terms: *a single author coded every paper, by machine, and the
reproducibility evidence is agreement between two implementations of one
person's rules, not agreement between two people.*

---

## 8. What this protocol does not fix

- It does not fix the **frame**. A different frame is a different audit. What
  it fixes is that this frame is enumerable, and that the enumeration is in a
  script rather than in a description.
- It does not remove the **open-access bias**. Only OA papers can be read in
  full without institutional credentials, and the frame says so up front
  rather than discovering it later.
- It does not make a mechanical coder a careful reader. It makes a mechanical
  coder a *published* one, which is a different and checkable property.
- It does not claim the sample is representative of all published claims about
  feature value. It is representative of the two frames in §2, and every
  proportion in the paper is scoped to them in the sentence that states it.

---

## 9. Changes to this document after registration

Any change is appended below with its date and reason, and the original text
stays. Nothing is edited in place.

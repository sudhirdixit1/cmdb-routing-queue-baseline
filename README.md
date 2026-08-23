# Specification surfaces for incremental predictive performance

Code, derived results, pre-registered protocols, a verification harness and a
Python package for a study of what a recorded field is worth to a prediction,
and of how much that answer depends on choices the analyst usually leaves
implicit.

**Paper:** `paper/specification_surfaces.tex` — *Specification Surfaces for
Incremental Predictive Performance: Estimation, Uncertainty, and Multi-Log
Evaluation*. Targeted at *Information Systems* (Elsevier).

**The previous version** — *Four Choices Behind One Number* — is retained at
`paper/iaai27_empty_cmdb.tex`. A referee for this journal recommended
rejecting it as submitted; `submission/response_to_referee.md` answers the ten
major comments one by one, and every claim of that version which this one
withdraws is a correction in Appendix C of the new manuscript.

**Pre-registrations:** `PROTOCOL.md` (the corpus), `AUDIT-PROTOCOL-2.md` (the
practice pilot), `PREDICTION.md` (a frozen rule tested on unseen logs). Each
was committed before any result it governs; `git log --stat` shows the
registering commit adding one file and no result file.

**Reproduction:** `REPRODUCE.md`. One command, which fetches every dataset by
DOI and checksums it:

```bash
python scripts/reproduce_all.py
```

---

## What the paper claims

1. **A feature's incremental predictive performance is a surface, not a
   number.** The estimand carries the learner, the encoding, the target, the
   split, the field's availability at the decision time, the register's
   quality, the baseline, the metric and the operating point. A claim is well
   posed only against a declared design space.

2. **Four objects make a surface reportable.** An exact functional-ANOVA
   decomposition of its variance across axes; simultaneous max-$t$ bands from
   a moving-block bootstrap that refits the entire pipeline inside every draw;
   *resolution regions* — uniformly beneficial, conditionally beneficial,
   sign-changing, unresolved — with a scalar robustness index $\rho$; and
   *specification regret*, which measures what one-number reporting gets
   wrong.

3. **On this corpus the choices dominate.** Over 19 log–target pairs from 13
   public event logs, varying the baseline alone moves the increment by 0.091
   AUC at the median pair and 0.298 at the widest. No single axis dominates
   the disagreement: the largest median first-order index is 10.1%, and the
   interactions between axes carry a median 30.0%. A conventional one-number
   report misstates the **sign** of the increment for a median 35.3% of the
   other admissible specifications; the rate is above 10% on 18 of 19 pairs.

4. **The case study's answer turns on a question the data cannot settle.** A
   configuration management database on 45,455 bank incidents is worth one
   thing if the prediction is made when the service desk picks up the call and
   another if it is made when the incident is created, because a
   knowledge-article reference is written in between. The paper reports both
   decision times and a curve of the increment against the share of references
   assumed to be post-hoc, rather than choosing.

## What this round withdrew

Recorded here as prominently as the claims.

- **The headline spread was inflated by a baseline no analyst would build.**
  The previous version's abstract said the baseline choice alone moves the
  reduction by more than the reduction itself; a later section of the same
  manuscript said the comparison included an intercept-only model and was
  therefore inflated, and the abstract was never corrected. The intercept-only
  rung is now excluded from every admissible set by definition, and the
  headline is recomputed without it.

- **"Not one of twenty papers reports the increment across operating points"
  is withdrawn.** The rebuilt pilot adjudicates the papers the mechanical
  screen *rejected* as well as the ones it accepted, measures the screen's
  sensitivity at 0.47, and finds eligible papers that do report the increment
  across a range of operating points. The earlier claim was a property of a
  coder that finds fewer than half of the eligible papers.

- **A universal "if and only if" that is only existential.** Rank-basedness is
  necessary and sufficient for the reduction to be invariant to a monotone
  recalibration *for every configuration*; the previous version's necessity
  direction was stated as though it held configuration by configuration, and a
  cancelling configuration is now exhibited.

- **A finite search reported as a proposition.** The axis non-redundancy claim
  is a computational result over a synthetic family, its tolerance sweep is
  printed in full, and the search itself had a defect: it drew fresh noise
  inside each cell evaluation, so two evaluations of the same cell disagreed.

The withdrawals from earlier rounds — an operational factor whose sign was set
by a tie-break, an asymmetry that was an algebraic identity, a margin that was
a granularity knob — stand.

---

## Layout

| path | what it is |
|---|---|
| `paper/` | the manuscript, its parts, the generated macro file and the generated tables |
| `paper/parts/` | the manuscript's sections; `scripts/assemble_paper.py` concatenates them |
| `paper/numbers.tex` | **generated.** Every number in the manuscript is a macro defined here |
| `paper/tables/` | **generated.** Every data table |
| `scripts/s*.py` | round nineteen: the surface, the bootstrap, the decomposition, the regret benchmark, the pilot, the propositions, the decision times, the simulation, the figures |
| `scripts/r*.py`, `e*.py` | earlier rounds, retained so their results stay reproducible |
| `fieldvalue/` | the package that computes a surface and refuses to emit one number |
| `results/` | every derived `.csv`; nothing here is hand-edited |
| `data/` | fetched by DOI, not redistributed; `CHECKSUMS.txt` and the pilot's adjudications are tracked |
| `submission/` | highlights, statements, the response to the referee, the cover letter |

## The controls

Every number in the manuscript is a macro generated from a result file, so a
number cannot disagree between the abstract, a table and the conclusion: there
is one of it.

| control | what it does |
|---|---|
| `scripts/make_numbers.py` | generates `paper/numbers.tex` and `paper/tables/*.tex` from `results/*.csv` |
| `scripts/verify_numbers.py` | re-derives each macro from its source with independent code and compares |
| `scripts/texlint.py` | abstract length, keyword count, highlight lengths, required statements, and **no numeric literal anywhere in the prose** |
| `scripts/attack_verifier.py` | injects corruptions and requires the verifier to catch every one |
| `scripts/test_checker_purity.py` | asserts the verifier does not modify what it checks |
| `scripts/check_highlights.py` | derives the highlight character counts rather than trusting them |

## Data

All public. BPI Challenge 2014 (`10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35`),
BPI Challenge 2013 incidents
(`10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee`), the UCI incident
management log (`10.24432/C57S4H`), and twenty further public event logs whose
DOIs and SHA-256 checksums are in `data/corpus/CHECKSUMS.txt`. No row of any
dataset is redistributed here; `scripts/fetch_corpus.py` resolves every DOI and
checksums what it downloads.

The practice pilot's frame, sample, mechanical codes and **adjudications** are
in the archive. The full texts are other publishers' PDFs and are not
redistributed; neither are the evidence dossiers built from them, which
`python scripts/s06_audit2.py --dossiers` regenerates deterministically from
the re-fetched texts.

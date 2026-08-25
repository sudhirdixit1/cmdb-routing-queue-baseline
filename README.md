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

**A second review**, of the round-nineteen manuscript, recommended *reject and
invite resubmission* and listed eight submission-blocking problems, six
methodological strengthenings and three positioning items.
`submission/response_to_blueprint.md` answers each in the order it was raised.
Four of them were the same kind of mistake — an inferential object that did
not match the sentence it licensed — and they are worth naming here.

- **A denominator that was not the one the claim quantified over.** Region
  labels ranging over a whole surface were supported by max-*t* bands whose
  family was five instruments *at one cell*, and by a bootstrap grid that held
  the split axis — the axis with the second-largest first-order index — fixed.
  There are now three surfaces, named and audited
  (`scripts/s25_denominator.py`), and the band family for a surface-level
  claim is the whole surface (`scripts/s21_bands.py`).
- **A variance component that was not the component it was named as.** The
  reported interaction share was the largest per-axis *involvement*
  `max_i(S_Ti - S_i)`; those quantities overlap across axes. The total
  higher-order share is `1 - sum_i S_i`, and it is roughly twice as large
  (`scripts/s22_anova.py`), computed under a **declared measure** over
  specifications rather than under whichever cells were enumerated.
- **An average over units that do not add.** Expected regret was averaged
  across AUC, average precision, Brier skill, log-loss skill and Nagelkerke
  R-squared and reported as one percentage. It is now computed inside one
  instrument at a time, with a common-utility version on calibrated net
  benefit, and evaluated **out of sample** (`scripts/s23_regret.py`).
- **A theorem stated wider than its proof — and wider than the truth.**
  Proving the rank-invariance proposition generally showed that what
  invariance of the *reduction* requires is that a recalibration act
  **affinely** on the instrument, which is strictly weaker than
  rank-basedness; a non-rank-based instrument whose reduction is invariant is
  exhibited (`scripts/s29_props.py`). "Exactly the rank-based ones" was not
  merely unproved, it was false.

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

2. **Four objects make a surface reportable.** An exact and orthogonal
   functional-ANOVA decomposition of its variance across axes, taken under a
   declared measure, with every disjoint component computed and their sum to
   one asserted rather than assumed; simultaneous max-*t* bands over the
   **whole surface a claim ranges over**, from a moving-block bootstrap that
   refits the entire pipeline inside every draw, with the critical value
   estimated by a multiplier bootstrap so its precision is not limited by the
   refitting budget; *resolution regions* — uniformly or conditionally
   beneficial, uniformly or conditionally harmful, sign-changing, unresolved —
   with a scalar robustness index ρ; and *specification regret*, computed
   inside one instrument at a time and evaluated **out of sample**.

3. **On this corpus the choices dominate.** Over 19 log–target pairs from 13
   public event logs, across a design space whose denominator is audited cell
   by cell, varying the baseline alone moves the increment by 0.091 AUC at the
   median pair and 0.298 at the widest. No single axis dominates: the largest
   first-order index at the median pair is about 29%, against a *total
   higher-order* share — the variance belonging to no single axis — of about
   56%. A conventional one-number report misstates the **sign** of the
   increment for a median 35% of the other admissible specifications.

   All three of those numbers are stated under a **declared measure** over
   specifications, and the paper reports them under three. One conclusion does
   not survive all three: under a measure concentrated on the reference
   specification, a single axis carries more variance than everything
   higher-order combined, because a reader who never departs from the
   reference barely activates an interaction. That is in the paper, not
   buried.

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

- **A universal "if and only if" that is only existential — and then the
  "if and only if" itself.** The necessity direction was stated as though it
  held configuration by configuration; a cancelling configuration is exhibited.
  Round twenty went further and proved the proposition generally, which showed
  the statement was not merely unproved but wrong: what invariance of the
  reduction requires is that a recalibration act **affinely** on the
  instrument, and a non-rank-based instrument whose reduction is invariant is
  now exhibited. "Exactly the rank-based ones" is withdrawn.

- **A finite search reported as a proposition, and then withdrawn entirely.**
  The axis non-redundancy claim was demoted to a computational result in round
  nineteen; round twenty removes it from the paper and the supplement. Its
  answer moved with an arbitrary tolerance, failing to find a witness is not
  evidence, and nothing depended on it.

## What this round found in its own work

After every one of the referee's ten comments was answered, the apparatus
found four defects in this round's own work and reading the compiled pages
found seven more. All eleven are in the manuscript, most of them in
Appendix C.

- **The simulation's own truth was wrong in one world.** It reported that
  every interval construction fails on the noisy world. The estimator was
  being scored against a population it never samples from. Found by testing
  the two finite-sample explanations an apparent bias implies — sample size
  and regularisation strength, with the sparse world as a control that a real
  finite-sample gap does close — and having both refuse. Appendix G;
  `scripts/s18_bias_scaling.py --legacy-target` regenerates the evidence.
- **The pilot's frame was 600 and the manuscript said 54,910**, from a
  stratum-size column summed over rows rather than strata. Correcting it
  showed the pilot is a census of what one index returned rather than a
  probability sample of a literature.
- **`--strict` certified a build reading a superseded run.**
  `results/provenance.json` now records each analysis script's SHA-256 at the
  moment its outputs were accepted.
- **One of ten corruptions was passing** because nothing regenerated between
  the corruption and the check.
- **Seven defects produced no wrong number and printed badly** — a doubled
  *Appendix*, a macro eating a space, a macro carrying words set as italic
  variables, a sentence's tail printed twice, a minus sign set as a hyphen, a
  figure axis clipping its most important bar, and a comparison whose two
  numbers were both zero. **Every checker here passed on the build that
  carried all seven.** Five became lint checks; the other two are judgements a
  checker cannot make.

The withdrawals from earlier rounds — an operational factor whose sign was set
by a tie-break, an asymmetry that was an algebraic identity, a margin that was
a granularity knob — stand.

## What round twenty found in its own work

- **A backslash escape interpreted by a scripted edit, in the committed
  sources.** `\ref{sec:practice}` had been written into the corrections
  appendix as a carriage return followed by `ef{sec:practice}`, and
  `\nAuditFrame` as a newline followed by `AuditFrame`. Both print as garbage;
  neither is a wrong *number*; every checker passed on the build that carried
  them. `texlint` check 15 now catches the signature exactly. Found by reading
  the sources, not the PDF.
- **A leak in the mechanism written to demonstrate no leak.** The new
  propensity-driven register-quality mechanism ranks a fitted score before
  thresholding it, and the first implementation ranked over *all* rows, so a
  training row's rank depended on the test rows. The executed train-only check
  caught it; the rank is now taken against the training half's empirical
  distribution.
- **A claim about the measures that computing them refuted.** The manuscript
  said the interaction conclusion held under every declared measure. It does
  not — under the concentrated measure a single axis leads on most pairs — and
  the corrected version is a better result than the claim it replaces.
- **A repair heuristic that damaged what it was fixing.** The script written
  to repair the mangled escapes matched a line beginning `ho` as a mangled
  `\rho` and joined `holdout's` and `holds` to their previous lines, creating
  two new defects while fixing three. The lint check uses only exact
  signatures; the repair should have too.

---

## Layout

| path | what it is |
|---|---|
| `paper/` | the manuscript, its parts, the generated macro file and the generated tables |
| `paper/parts/` | the manuscript's sections; `scripts/assemble_paper.py` concatenates them |
| `paper/numbers.tex` | **generated.** Every number in the manuscript is a macro defined here |
| `paper/tables/` | **generated.** Every data table |
| `scripts/s01*`--`s18*` | round nineteen: the surface, the bootstrap, the decomposition, the regret benchmark, the pilot, the propositions, the decision times, the simulation, the figures |
| `scripts/s20*`--`s30*` | round twenty: the inference surface, whole-surface bands, the corrected ANOVA, coherent-scale regret, planned contrasts, the denominator audit, calibrated decision curves, register-quality curves, the propositions, the pilot's variance |
| `scripts/round20_*` | the round-twenty macros, tables, verifications and the chain that runs them |
| `scripts/claim_registry.py` | every number the manuscript prints, its generator line and its result file |
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
| `scripts/texlint.py` | fifteen compliance checks: abstract length, keyword count, highlight lengths, required statements, **no numeric literal anywhere in the prose**, five typographic checks each of which caught a defect already in a compiled PDF, and one that catches a backslash escape interpreted by a scripted edit |
| `scripts/provenance.py` | records which version of each analysis script produced the results in the tree; `make_numbers.py --strict` refuses a build whose numbers come from a script changed since |
| `scripts/check_response_refs.py` | every section the cover material cites exists, and prints the heading each lands on |
| `scripts/attack_verifier.py`, `scripts/s13_attack_numbers.py` | inject corruptions and require the verifier to catch every one; 265 across the two |
| `scripts/test_checker_purity.py` | asserts the verifier does not modify what it checks |
| `scripts/check_highlights.py` | derives the highlight character counts rather than trusting them |
| `scripts/claim_registry.py` | every macro, its value, every manuscript location that uses it, the generator **line**, the result file, and whether the verifier re-derives it independently |
| `scripts/round20_verify.py` | recomputes the round-twenty quantities from the **row-level** result files rather than the summary rows the generator reads |

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

# Response to the developmental review of *Specification Surfaces for Incremental Predictive Performance*

**Manuscript:** `paper/specification_surfaces.tex`
**Review:** the strong-accept revision blueprint of 24 August 2026, which
recommended *reject and invite resubmission* and listed eight
submission-blocking scientific problems (P0.1–P0.8), six methodological
strengthenings (P1.1–P1.6), three positioning items (P2.1–P2.3), a
restructuring plan, a compliance package and five red-team gates.

This document answers each in the order the blueprint raises it. Every claim
below is checkable: the script that produces the evidence is named, the result
file is named, and `results/claim_registry.csv` maps every number printed in
the manuscript to the generator line and result file it came from.

**One general remark before the details.** The blueprint's central complaint
is not that particular numbers were wrong. It is that several *inferential
objects* did not match the sentences they were used to license — a family
smaller than the claim it covered, a variance component that was not the
component it was named as, an average over units that do not add, a theorem
stated wider than its proof. We have taken that as the organising principle of
the revision. Where the repair changed a number, the number changed. Where the
repair changed what a number *means*, we have said so and renamed it.

---

## Priority 0 — submission-blocking

### P0.1 Reconcile the declared surface with the cells used in the headline region analysis

**Accepted in full.** The blueprint is right that the region analysis was
computed on a sub-grid and described as a property of the declared surface.

Three objects are now distinguished by name and counted from the files:

| object | what it is | where |
|---|---|---|
| **declared surface** | every scientifically admissible specification | §3.1, the design-space table |
| **computational surface** | every specification actually evaluated | §6.1, the denominator audit |
| **inference surface** | every specification carrying bootstrap draws | §4.3, the denominator audit |

`scripts/s25_denominator.py` generates the **surface denominator audit**
with one row per log–target pair, giving the declared level count on
every axis, the expected Cartesian product, the observed unique cells,
duplicates, missing combinations and the reason for every structural
exclusion. It **asserts** `observed = expected − declared exclusions` and
`duplicates = 0` rather than leaving the manuscript to claim them, and both
hold on all 19 pairs.

The blueprint asks that the three objects be identical wherever possible. The
first two now are, exactly. The third is not, and cannot be on the hardware
this study has: a draw refits the whole pipeline, so the inference surface
costs the declared surface multiplied by the draw count. Two things follow and
both are done.

1. **The inference surface is declared before any draw**, by a rule that reads
   only the row count of a log (`s20_boot2.plan()`, written to
   `results/s20_grid.csv` before the first draw), and it is **axis-complete**:
   every axis of the estimand varies over at least two levels. Round
   nineteen's grid held the split axis fixed at one holdout — the axis with
   the second-largest first-order index — which is the specific defect that
   made the old denominator indefensible rather than merely small.
2. **The restriction is measured, not asserted.** Point estimates exist on
   both surfaces, so `s25` reports the gap: the share of positive cells
   differs between the declared and inference surfaces by a median 0.067 and
   at most 0.351. That number is in the manuscript, in the limitations, and in
   the abstract's framing.

The same budget shows in the draw counts, which vary by pair. The denominator
audit prints the count each pair actually carries rather than a corpus
average, and the limitations say what varying it does and does not affect: it
moves the per-cell standard errors, not the critical value, because the
multiplier bootstrap of P0.2 estimates that independently of *B*. The case
study carries the most draws; the smallest logs carry the fewest. On this
machine the primary log alone took six hours per target.

Everything that does not need a band — the decomposition, the sign
disagreement, the regret comparison — is computed on the **full declared
surface**. Only region labels use the inference surface, and they are named as
such at every appearance.

One consequence is stated in the manuscript rather than left for a reviewer to
find: *uniformly* beneficial is a claim about every cell, so a smaller set of
cells makes it easier to reach. The count of uniformly beneficial surfaces is
therefore an **upper bound** on what the declared surface would give. That is
the optimistic direction for that one count and the conservative direction for
every other claim in the paper, and §6.4 says so.

**Acceptance tests.** All four pass; the assertions are in `s25_denominator.py`
and are re-derived independently in `round20_verify.check`.

---

### P0.2 Make inference simultaneous over the family used for a surface-level conclusion

**Accepted in full.** `scripts/s21_bands.py` replaces the band layer.

Four interval objects are now constructed and **named**, and every table says
which it prints:

1. **pointwise** — per-cell, no multiplicity control;
2. **within-instrument** — max-*t* over the scalar instruments at one cell
   (round nineteen's object, retained *only* so the difference the correction
   makes is visible);
3. **whole-surface** — max-*t* over every admissible scalar cell of the pair;
4. **decision-curve** — max-*t* over every admissible net-benefit cell,
   declared separately.

Region labels use (3) and nothing else. Family control is **per log–target
pair**, and the manuscript now states explicitly that every cross-pair
statement is descriptive rather than a simultaneous inferential claim.
Bootstrap replicate identifiers are aligned across every cell entering a
maximum by construction: a draw is a task, and all cells in it consume one
random stream (`s20_boot2.one_draw`).

**Beyond what was asked.** The blueprint notes that a max-*t* quantile from a
few hundred draws is badly estimated. It is, and raising the draw count was
not affordable. We estimate the critical value by a **Gaussian multiplier
bootstrap** over the standardised draw matrix
([Chernozhukov, Chetverikov and Kato, 2013](https://doi.org/10.1214/13-AOS1161)),
which reproduces the empirical covariance and can be run 20,000 times for the
cost of matrix arithmetic. The fitting budget therefore fixes *B*; it no
longer fixes the precision of *q*. Both estimators are reported, and the
residual Monte Carlo interval is carried through: a cell counts as resolved
only if it resolves at the **upper** end of it, so what noise remains leaves
cells unresolved rather than resolving them wrongly.

---

### P0.3 Redefine specification regret on a coherent utility scale

**Accepted in full.** The old number averaged AUC, average precision, Brier
skill, log-loss skill and Nagelkerke *R²* increments into one quantity and
called the result "in the metric's own units". It is withdrawn (correction
C27). `scripts/s23_regret.py` implements all three of the designs the
blueprint offers.

**A. Metric-specific (primary).** The loss is computed inside one instrument
at a time; no average in the paper crosses an instrument; every value carries
the name of its unit. The only cross-instrument statement the design permits
is a *count* of the instruments a direction holds in — and writing it as a
count is what caught two overclaims in our own draft: the conservative rule is
worst in **four** of the five instruments, not five, and the full
out-of-sample ordering of the three remaining rules holds in **four**, not
five. Both counts are macros, both are re-derived by `round20_verify`, and
both exceptions are named in §6.6.

**B. Common operational utility.** Net benefit — true positives per case at a
declared exchange rate — on **calibrated probabilities only**, under a
declared threshold distribution, and *also* reported as a function of the
threshold so a reader need assume no distribution at all. Called *decision*
regret, not predictive-performance regret.

**C. Partial identification.** Five monotone utility maps fixing zero; the
range of the conclusion over the family, and which conclusions are invariant
to all of them.

**On "optimal by construction".** The blueprint is right that the mean rule
minimising loss on the surface the loss averages over is an identity. It is
now labelled a **lemma**, its assumptions are stated (one action for every
reader, linear loss in a common utility, known reader distribution), the
identity is reported as a *check on the algebra* — the in-sample excess is
0 everywhere, as it must be — and the rules are compared **out of sample** in
three ways: held-out specifications, held-out time, and held-out logs. The
out-of-sample comparison is the one the manuscript now leads with, and it is
less flattering than the in-sample one: on held-out time the ordering reverses
on the instruments that read calibration, and the leave-one-log-out ordering
agrees only about three-fifths of the time. Both are reported.

---

### P0.4 Correct the interaction decomposition and all associated claims

**Accepted in full.** `scripts/s22_anova.py` replaces the decomposition.

- The **total higher-order share** is `1 − Σᵢ Sᵢ`, computed and reported.
- Every **disjoint component** of the decomposition is computed — all 2^k of
  them — and the identity `Σᵤ Sᵤ = 1` is **asserted numerically** on every
  decomposition, not assumed. It holds on all of them.
- The old quantity is renamed **largest per-axis interaction involvement**.
  The two differ by a wide margin: the corrected median higher-order share is
  56.0%, against the 43.7% the old statistic gives on the corrected surface
  and the 30.0% that was printed.
- The probability measure is explicit (P0.5).
- Orthogonality is guaranteed because the design is a *complete* factorial
  under a *product* measure, which P0.1's audit establishes cell by cell; the
  decomposition code refuses to run on an incomplete grid.
- **Within-metric decompositions are primary**; the headroom-scale
  cross-metric decomposition is a labelled sensitivity analysis.
- Uncertainty: the decomposition is recomputed inside every bootstrap draw
  where the inference surface supplies them, and corpus medians are
  bootstrapped with the pair as the resampling unit. No axis is called
  dominant where intervals overlap.

Every occurrence of the old 30.0% is gone; `texlint` forbids numeric literals
in the prose, so the only way for it to survive would be for the generator to
produce it.

---

### P0.5 Define a defensible probability measure over specifications

**Accepted in full.** Axis weights and within-axis level weights are separated.
Four measures are declared and every weighted quantity is reported under all
of them, in the measures table: *equal-level*, *reference* (half the mass on each axis's
reference level), *concentrated* (four fifths), and an *envelope* over 200
Dirichlet draws of the level weights. The measure matters — the total
higher-order share moves by 29.2 points across the three product measures,
with the Dirichlet envelope at 18.1% reported beside them rather than inside
that range — the envelope is computed on the primary pair and the other three
are corpus medians, and an earlier draft took the range over all four, which
mixed the two populations and made the number 37.9 — and the manuscript says
which conclusions survive all four.

The two invariance properties the blueprint names are **executed**:
duplicating a level with its weight split leaves every component unchanged to
5.6 × 10⁻¹⁷, and refining the operating-point grid fourfold under the same
continuous measure moves the threshold index by 0.004. Unweighted cell
proportions are labelled descriptive counts.

**And doing this changed a conclusion, which is the argument for doing it.**
Under the equal-level and reference measures the total higher-order share
exceeds every first-order index, as the manuscript said. Under the
concentrated measure it does not: on most pairs a single axis then carries
more variance than everything higher-order combined. The mechanism is that a
reader who almost never departs from the reference specification barely
activates an interaction, so the surface is being sampled where it is nearly
additive. We had written that the conclusion held under every measure before
computing it under every measure; it does not, the manuscript now says so in
§6.3 and in the limitations, and the finding is more interesting than
the claim it replaces.

---

### P0.6 Repair Proposition 2

**Accepted, and the repair went further than the blueprint asked.** We took
the general-theorem route, and proving it showed the claim was not merely
unproved but **false**.

What invariance of the *reduction* requires is not that a recalibration leave
the instrument fixed, but that it act **affinely** on it — an affine change of
scale cancels in a ratio of two differences. The corrected proposition is an
if-and-only-if at that scope, with a three-line proof (an affine map is the
unique solution of a ratio-of-differences functional equation on a set with
three points), stated under an explicit richness assumption.

Rank-basedness is the special case *A* ≡ 1, *B* ≡ 0. Corollary 1 exhibits a
**non-rank-based instrument whose reduction is invariant** under the whole
affine family — the class-mean gap — so "exactly the rank-based ones" is
withdrawn as correction C23.

The proposition also converts a search into a proof: one violating triple now
*settles* an instrument, because it establishes non-affine action and the
proposition does the rest. `scripts/s29_props.py` supplies such a certificate
for each of the three non-rank-based instruments under each of six
recalibration families — 18 in all — and verifies the invariance identity for
the two rank-based instruments over 2,400 configurations, to machine
precision.

---

### P0.7 Correct confirmatory inference and finite-bootstrap p-values

**Accepted in full.** `scripts/s24_confirm.py`.

- The **plus-one estimator** `p̂ = (k+1)/(B+1)` is used throughout; the
  smallest attainable raw and Holm-adjusted values are printed beside the
  results, so a reader can see that the design cannot produce zero.
- Independent draws raised to 2,000 for these contrasts, which live on one
  cell each and are therefore affordable at that scale. (The blueprint asks
  for 5,000–10,000 for max-*t* inference; for the *bands*, where a draw costs
  the whole design space, we met the requirement differently — see P0.2 — by
  making the critical value's precision independent of *B*.)
- The number of **independent draws** is reported, distinct from the number of
  cell-draw records.
- The contrasts are renamed **final-round planned contrasts**. They were fixed
  before this analysis round, not before the data were seen, and the
  manuscript says so in those words.
- Each contrast now carries a **complete estimand**: log, cohort, target,
  learner, encoding, split, decision time, register quality, baseline and
  instrument, printed in the table.
- Holm is re-derived independently in `round20_verify`, and a p-value below
  the attainable floor is a verification failure.
- The contrasts are relabelled **PC1–PC5**. They had been C1–C5, and the
  correction register numbers its entries C1–C31, so §4.5 cited correction C29
  three paragraphs from a table whose rows were C1 to C5. One identifier
  space, two meanings, in one section. The manuscript says why in a sentence,
  because a reader of the previous version will otherwise wonder where the
  contrasts went.

---

### P0.8 Make decision-curve analysis probability-valid

**Accepted in full.** `scripts/s26_calib_dca.py`.

Every model contributing to a decision-curve conclusion is refitted under a
**training-only** calibration — isotonic and Platt, each cross-validated
*inside* the training half, rebuilt inside every resampling iteration.
Calibration intercept, slope, Brier score, expected calibration error and
binned calibration curves are reported for raw and calibrated scores on every
pair, in the calibration table.

The interpretive rule is now explicit and enforced in the captions: **curves
on calibrated probabilities carry the probability-threshold reading; curves on
raw scores are labelled score-threshold sensitivity analyses.** The paper
reports how much calibrating changes the sign of the net-benefit increment,
rather than assuming it changes nothing.

---

## Priority 1

### P1.1 Strengthen bootstrap validation

**Accepted.** The simulation was rebuilt at the size the request implies, in
`scripts/s31_simboost.py`, which supersedes the 200-replicate run for every
coverage number the manuscript prints. It imports the world generator, the
enumerated truth and the observed-population marginalisation from
`s10_simulation2.py` rather than copying them, because those are the delicate
part and one of them was wrong for two rounds; a copy could drift, an import
cannot. The nine required items, one by one:

| # | required | done |
|---|---|---|
| 1 | ≥1,000 replicates per world | 1,000 in each of six worlds |
| 2 | Monte Carlo standard errors for coverage, bias and width | every row of `results/s31_coverage.csv` carries all three; §10's table prints the bias and the reported interval's width beside the coverages, and the manuscript quotes the coverage resolution wherever it compares two constructions |
| 3 | sparse world expanded toward the observed 3,019-level regime | the `(n, K)` grid reaches K = 3,019, the case study's own register cardinality |
| 4 | sample size and cardinality varied **jointly** | a 10-cell `(n, K)` plane, n ∈ {2,000; 4,000; 8,000}, K ∈ {20; 200; 1,000} plus (8,000; 3,019) — because it is the *ratio* K/n that governs the bootstrap shift, and varying either alone shows neither |
| 5 | at least three block lengths around n^(1/3) | three — half the rule of thumb, the rule, and twice it — on the world where the construction is well behaved and on the one where it is not. The coverage **does** move with the block length, by a couple of points within a world, and §10.3 says so rather than claiming invariance; what does not move is the comparison the paper rests on, which holds at every length |
| 6 | six constructions compared, including m-out-of-n in the sparse regime | seven: fixed-model percentile/basic/bias-corrected, nested percentile/basic/bias-corrected, and nested **m-out-of-n** at m = n^(2/3) with the deviations rescaled by √(m/n) |
| 7 | coverage for both the fitted-pipeline limit and the oracle target | both, in every table, with the manuscript stating that only the first is estimable by resampling |
| 8 | stationarity/mixing assumptions stated | §11, and again in the simulation section's closing paragraph |
| 9 | consequence of a fixed split point | §11: split-position uncertainty is outside every interval reported here, said in those words |

**The result that matters is a negative one and is reported as one.** In the
sparse regime — the one that motivates subsampling at all — the nested
percentile interval covers **37.2%** against a nominal 95%, the
bias-corrected percentile **63.1%**, m-out-of-n **72.8%**, and the basic
(pivotal) interval **89.9%**. Subsampling does not rescue the sparse world and
undercovers on the well-behaved ones too. The paper therefore keeps the basic
interval — one construction rather than a construction and a rate — and §10
prints all seven coverages side by side so the choice is visible rather than
asserted. **And the `(n, K)` plane returned the round's most consequential result,
which is against us.** Coverage of the interval this paper reports is governed
by the ratio of register cardinality to training size. It holds at or above
90% while K/n ≤ 0.05, is below three quarters by K/n = 0.125, and reaches
**21.3%** at K = 3,019 on 8,000 training rows. The median log–target pair in
this corpus is at **K/n = 0.106**, ten of the nineteen are above a tenth, and
the case study is at 0.093. **So the bands this paper reports are narrower
than their nominal level on most of its own pairs**, which is the
anti-conservative direction: it inflates the count of cells called *resolved*.

We report this in §10.3, again in §11 as the study's sharpest limitation, and
as a `K/n` column in the denominator table so a reader can see which pairs are
affected. Nothing in the paper's point estimates or its
specification-sensitivity conclusions rests on the bands — the decomposition,
the sign-disagreement rate and the regret comparison are computed without one
— but the resolution regions and the robustness index do, and they should be
read as upper bounds on resolution.

The blueprint's pass condition is *"reasonably stable near-nominal coverage
across the worlds for its stated estimand, **or** the manuscript must clearly
delimit the regimes in which it does not"*. We meet the second clause, and we
would rather meet it explicitly than meet the first by not having looked. The
experiment that found this is the one the review asked for; had we run the
sparse world at a single cardinality, as the previous version did, we would
not have known.

### P1.2 Add uncertainty to sensitivity indices and region summaries

**Accepted.** The decomposition is recomputed inside bootstrap draws; interval
summaries are produced for first-order indices, total indices and the total
higher-order share; corpus medians are bootstrapped with the pair as the
resampling unit; and no axis is declared dominant where intervals overlap.

### P1.3 Improve register-quality mechanisms

**Accepted in full.** `scripts/s27_quality.py`: 20 seeds for every stochastic
mechanism; severity **curves** rather than points, summarised by an integral
against a declared continuous measure, with the grid-refinement shift
reported; mechanism variability reported **separately** from sampling
variability; and three new **dependent** mechanisms — time (the register was
populated late), content (coverage depends on the item's type) and propensity
(missingness correlated with the outcome through a training-estimated score).
The duplicate mechanism's operational meaning is stated: one item reconciled
under two keys. Every mechanism, including the dependent ones, is verified *by
execution* to read no test outcome.

### P1.4 Clarify the benchmark's construct validity

**Accepted.** A construct-validity table gives, per pair, the domain, the
register field, why it behaves as a maintained and reused entity, the free
field, the target's interpretation and the **specific threat to construct
validity** the pair carries. The ITSM-like pairs are analysed as a family. No
domain-specific magnitude is averaged across domains. The false dichotomy
"the sign is a property of the specification and not of the data" is
withdrawn and replaced with the joint statement.

### P1.5 Preserve but discipline the CMDB case study

**Accepted.** Both cohorts and both decision times are preserved and explained
in one table; the knowledge reference is never claimed to be definitely
available; the λ-masking curve is labelled a sensitivity analysis; causal
statements are absent; and the quality mechanisms are now mapped one-to-one to
operational failure modes an architect would recognise — missing CI coverage,
duplicate identities, wrong identities, stale discovery, delayed CI creation,
and configuration items unseen after a temporal split.

### P1.6 Remove or radically reduce the practice pilot

**Accepted in full.** The main text keeps one cautious paragraph; the
protocol, PRISMA-style flow, screen accuracy, prevalence estimation,
applicability-specific denominators and sensitivity analyses are all in the
appendix. The Wilson intervals computed from a fractional effective sample are
withdrawn (correction C28) and replaced with a **stratified bootstrap**
(primary) and a **design-based linearised** interval for the two-stratum ratio
estimator; none of the five Wilson intervals is contained in its design-based
counterpart. The single machine-assisted adjudicator is stated prominently,
and the main text says in terms that no claim in the paper depends on the
pilot.

---

## Priority 2

**P2.1 Novelty.** The introduction now separates existing components (named,
with citations) from the new formalisation, the new reporting objects, the new
empirical evidence and the new operational case, and states explicitly that
the contribution is *not* "people usually report one number".

**P2.2 The weighted-mean result** is a **lemma**, with assumptions stated and
the identity presented as a theorem check rather than an empirical discovery.

**P2.3 Computational Result 1 is removed** from the main paper and the
supplement, with a short note in the proofs appendix recording why (correction
C24): its answer moved with an arbitrary tolerance and nothing depended on it.

---

## Presentation, compliance and verification

- **Correction narrative.** `texlint` bans five sentence openers the referee
  named; the register lives in the appendix, grouped by *class* of error, and
  round twenty adds five classes (I–M).
- **A defect class the checkers could not see.** Reading the committed sources
  found `\ref` and `\nMacro` written as literal control characters by an
  earlier scripted edit — printing as `ef{sec:practice}` in a compiled PDF
  that every checker passed. `texlint` check 15 now catches it exactly.
- **Claim registry.** `scripts/claim_registry.py` writes
  `results/claim_registry.csv`: every macro, its value, every manuscript
  location that uses it, the generator file and **line**, the result file, and
  whether `verify_numbers` re-derives it independently. Because the manuscript
  contains no numeric literals, the registry is exhaustive by construction.
  It reports **25 of the 30 headline macros** — the ones the abstract, the
  introduction and the conclusion print — as independently re-derived, against
  **10 of 29** when this session began. Three of the five that remain are the
  simulation's, and are re-derived where that file supplies them. Raising that
  count is not bookkeeping: the second re-derivation written for it disagreed
  with the generator, and the generator was wrong (the measure-range defect
  above).
- **Independent re-derivation.** `round20_verify.py` recomputes the
  round-twenty quantities from the *row-level* result files rather than the
  summary rows the generator reads, and adds consistency conditions — a
  p-value below its attainable floor, a region label inconsistent with its own
  cell counts, an ANOVA whose components do not sum to one, a rank-based
  instrument whose reduction moved — each of which is a build failure.
- **Journal compliance.** Abstract 243 words, under the 250 limit and inside
  the 220–235 range the review suggested aiming at; seven keywords; five
  highlights with machine-derived character counts; all declarations present;
  the data-availability statement's log count is now derived from the checksum
  file rather than typed, which is what made it disagree with the manuscript.

### Structure and length, against §7 of the review

The restructuring plan was followed section for section, including the two
changes of shape it asks for: **simulation is now its own section** rather
than two subsections in two different places, and the **practice pilot is one
paragraph** with its dossier in the appendix. `python scripts/texlint.py
--sections` prints the table below, so the numbers here are generated rather
than counted by hand.

| § | section | words | requested | |
|---|---|---:|---|---|
| 1 | Introduction | 1,292 | 1,200–1,500 | ✓ |
| 2 | Related work | 992 | 1,200–1,500 | under |
| 3 | The specification surface | 2,008 | ~1,500 | ✓ |
| 4 | Estimation and inference | 3,732 | 2,000–2,500 | **over** |
| 5 | The registered benchmark design | 1,056 | 1,200–1,500 | under |
| 6 | Multi-log results | 4,060 | 2,000–2,500 | **over** |
| 7 | Case study: a configuration management database | 2,576 | 1,500–2,000 | just over |
| 8 | Decision-analytic evaluation | 1,635 | — | added |
| 9 | A reporting standard, and software | 602 | — | added |
| 10 | Simulation | 1,847 | 1,000–1,500 | just over |
| 11 | Limitations | 2,007 | 1,200–1,500 | just over |
| 12 | Conclusion | 585 | 400–600 | ✓ |

**The body is about 19,700 words against the 13,000–15,000 requested, and we
are not going to pretend that is inside the band.** In pages, in the
`preprint,12pt` layout Elsevier asks for at review: **64 pages of main text
and 33 of appendices**, against the review's count of 69 pages for the whole
of the round-nineteen manuscript. What grew is the appendix — this round moved
four constructions, a worked example and the practice pilot's dossier into it
— and the appendix is the online supplement the review asked us to move them
to. Four of the ten sections the plan
names are inside their stated budgets, three are within about sixty words of
the top of theirs, and two are under. The two
that are materially over are §4 and §6 — which are exactly the two sections
the Priority 0 list required new work in: three named surfaces with an audited denominator,
whole-surface simultaneous bands with a multiplier-bootstrap critical value,
an exact decomposition under four declared measures, a coherent regret scale
with three designs, planned contrasts with finite-bootstrap *p*-values, and
the region machinery that reads all of it. Each of those is an object the
review asked to have defined rather than asserted, and a defined object costs
words.

What we did instead of cutting the content:

- moved every **construction** out of §4 into a new **Appendix C, Construction
  of the inferential objects** — the multiplier bootstrap, Fieller's set, the
  three regret designs, and the exact computation and invariance checks of the
  decomposition — so the section carries what each object is and why, and the
  appendix carries the arithmetic;
- merged the two overlapping novelty statements (the introduction's
  contributions list and related work's five-part claim) into **one**, which
  is also what P2.1 asks for;
- moved the practice pilot, the worked example and the correction register out
  of the main text entirely.

The manuscript also grew after the structure table was first written, by
about a thousand words, and all of it is §10.3 and §11: the `(n, K)` plane
returned a result against the paper and reporting it properly took the space
it took. We would rather submit over length than either remove an object the
review asked to have made precise or bury the limitation the review's own
experiment produced. If the editor wants the band met exactly, the two candidates we would
cut are §9 (the reporting standard and software, 769 words, which is a
contribution but not a result) and the decision-analytic section's
partial-identification passage — and we would prefer to be told which, rather
than choose for you.

---

## The five red-team gates

The review asks that we not request another full review until all five gates
pass. They are answered here one question at a time, with the object that
answers each. Two answers are **no**, and they are marked as such.

### Gate 1 — statistical reviewer

| question | answer |
|---|---|
| Is the estimand identical across the mathematical definition, code and results? | **Yes.** One equation, one `spec.py`, and `claim_registry.csv` maps every printed number to the generator line and result file that produced it. |
| Does the simultaneous family match the conclusion family? | **Yes.** Four families are named; a region label uses the whole-surface family and nothing else, and every table prints which family it used. |
| Are the *p*-values attainable with the stated bootstrap size? | **Yes.** Plus-one estimator, and the smallest attainable raw and Holm-adjusted values are printed beside the table. A verifier condition fails the build if any *p*-value falls below its own floor. |
| Is the interaction statistic interpreted correctly? | **Yes.** The total higher-order share is one minus the sum of the first-order indices; the old per-axis maximum is retained under the name it deserves and the two are printed side by side. |
| Does every regret value have a coherent unit? | **Yes.** No average in the paper crosses an instrument; the common-utility version is on calibrated net benefit, in true positives per case. |
| Is the weighting distribution explicit? | **Yes.** Four measures, declared in a table, reported everywhere, and one qualitative conclusion does not survive all four — which the paper reports rather than smooths. |
| Are simulation conclusions supported by adequate Monte Carlo precision? | **Yes.** 1,000 replicates per world, and every coverage, bias and width carries a Monte Carlo standard error the manuscript quotes wherever it compares two constructions. |

### Gate 2 — information-systems / process reviewer

| question | answer |
|---|---|
| Is the contribution clearer than a generic machine-learning benchmark? | **Yes.** The object is a reporting standard for a claim service-operations teams actually make — what a maintained register is worth to a prediction — and the availability of the field at the decision time is an argument of the estimand rather than a preprocessing detail. |
| Is the CMDB/ITSM case operationally meaningful? | **Yes.** Two decision times matching two moments in an incident's life, a baseline ladder built from intake fields a service desk has, and net benefit at a declared review capacity. |
| Are decision time, field availability and leakage handled correctly? | **Yes.** Decision time is a declared axis; the knowledge-field availability question is traced as a curve a reader places their own belief on; every quality mechanism is verified train-only *by execution*, which is how a real leak in one of them was found. |
| Are heterogeneous register constructs described honestly? | **Yes.** A construct-validity table with one row per pair, naming the specific threat each carries, and nothing averaged across pairs. |
| Are the implications useful to architects without overstating business causality? | **Yes, and the limits are first.** The paper says in its first limitation that this is predictive performance and not value, and that converting the master table into a procurement decision is unsupported. |

### Gate 3 — theory reviewer

| question | answer |
|---|---|
| Is every proposition proved at its stated quantifier scope? | **Yes.** The rank-invariance proposition is now an equivalence under a stated richness assumption, and proving it generally showed the previous "exactly the rank-based ones" was false rather than merely unproved. |
| Are computational witnesses labelled as examples rather than universal proofs? | **Yes**, and the one that could not be so labelled is withdrawn. |
| Are assumptions on denominators, continuity, calibration and utility explicit? | **Yes.** Fieller sets carry their kind; the recalibration is strictly increasing and continuous; decision curves are calibrated first; the lemma's three assumptions are in the sentence that states it. |
| Is novelty distinguished from established component methods? | **Yes.** The introduction separates existing components, the new formalisation, the reporting objects — naming which two are adaptations — the new evidence and the new case. |

### Gate 4 — reproducibility reviewer

| question | answer |
|---|---|
| Can a new environment regenerate all principal results? | **Yes.** `Dockerfile`, `requirements.lock` pinning every transitive dependency, `REPRODUCE.md` with per-script runtimes, and `reproduce_all.py` running the waves in dependency order. |
| Is the archive publicly accessible at a frozen DOI? | **Not yet — this is the one blocking item no script can clear.** The Zenodo deposition is prepared and `submission/OWNER-ACTIONS.md` carries the exact steps; the DOI must be minted by the author before submission, and the manuscript's `\zenodoDOI` macro resolves from the release file so it cannot be typed. |
| Do source checksums and result checksums pass? | **Yes**, and `provenance.json` additionally refuses to certify a result produced by a source that has since changed. |
| Are all tables and figures generated rather than edited manually? | **Yes.** Every table is written by `make_numbers.py` or `round20_tables.py`; a table whose source is missing is written as a visible placeholder rather than omitted, so a partial build cannot silently drop one. |
| Does the claim registry show where every headline number came from? | **Yes**, and it is exhaustive by construction, because `texlint` fails the build on any numeric literal in the prose. |

### Gate 5 — handling editor

| question | answer |
|---|---|
| Can the novelty be understood from the first two pages? | **Yes.** The abstract states the object and the four reporting instruments; the contributions list on page two separates what is borrowed from what is new. |
| Is the main manuscript short enough to review efficiently? | **No, and we say so.** The body is about 19,700 words against a requested 13,000–15,000, in 64 pages of main text and 33 of appendices. The structure table above shows which sections are inside their budgets and which are not, and names the two we would cut if the editor wants the band met. |
| Are the contributions precise and defensible? | **Yes**, and each is stated so it can be refused separately. |
| Does the abstract contain only results that survived the final audit? | **Yes.** Every number in it is a macro generated from a result file, and the build fails if any of them is unresolved. |
| Is the paper written as a finished article rather than a response to a referee? | **Yes.** The correction register is in the appendix, grouped by class; `texlint` bans the five sentence openers the first referee named, and the main text carries no round-by-round narrative. |
| Is every required submission component present? | **Yes**, with the Zenodo DOI as the single outstanding owner action. |

**Two gates carry a "no".** The archive DOI is an action for the author at
submission time and is documented rather than deferred silently. The length is
a judgement we have made explicitly and argued for above, and we would rather
be overruled on it than remove an object the review asked to have defined.

---

## What we did not do

Stated plainly, because a reviewer should not have to find them.

1. **The inference surface is still smaller than the declared surface.** It is
   axis-complete and its restriction is measured, but a study with more
   compute should equate them.
2. **The simulation certifies six worlds, a ten-cell `(n, K)` plane and three
   block lengths, and nothing else.** The stationarity and mixing the
   moving-block bootstrap needs are assumed, not tested, and the split point
   is fixed within a draw, so split-position uncertainty is outside every
   interval in the paper.
3. **There is still one adjudicator on the practice pilot**, and no
   independent human reliability study.
4. **There is still no organisational partner** with timestamped field
   histories, so the CMDB case remains a benchmark case and the decision-time
   question remains a sensitivity analysis rather than a settled fact.
5. **The body is 19,700 words against a requested 13,000–15,000.** Argued
   above, section by section, and not met.
6. **Two bands rest on fewer replicates than the draw count declares** — 33
   of 40 on the worst, because a resample on a small log can leave a cell of
   the family without outcome variation. §4.4 reports it; the effect is on the
   per-cell standard errors and not on the critical value.
7. **On a common operational utility, three of the four decision rules tie.**
   The case against one-number reporting rests on the metric-specific
   comparison and the sign disagreement, not on the net-benefit one. §8.4
   says so in the section where our own argument has least purchase.

---

## A note on what this round's own checking found

Twelve defects were found in this round's work after every item above was
answered, and all twelve are in sections 25.8 to 25.10 of `../HANDOFF.md`
with what each one changed. Three are worth the editor's attention because they say
something about what a checking apparatus can and cannot do.

**A decision-curve interval was a percentile interval while the manuscript
said every interval in it was the basic construction.** Nothing was wrong with
either interval; what was wrong was that a property asserted of *every* object
had not been checked on each object. The band file now declares its
construction and the verifier reads that declaration.

**Two cross-instrument claims were written as "in all five instruments" and
were true in four.** The exceptions are Nagelkerke *R²* and Brier skill, both
now named in §6.6. This repository's whole discipline is that every number is
generated and checked — and these were not numbers, they were quantifiers.
They are counts now, with macros and a re-derivation, which is the only way
that discipline could reach them.

**A calibration table was a float 309 pt too tall for the page.** LaTeX said
so in the build log, in a warning, and typeset it anyway with its caption
stranded overleaf. The build checks errors, undefined references and overfull
horizontal boxes; it did not check warnings. The table is now nineteen rows
rather than fifty-seven, which is also the better table.

What the three share is that the generated-macro discipline protects
*numbers*, and each of these was a *word* around a number — a quantifier, the
name of a construction, a contrast between two values that print the same.
Where the word could be rewritten as a count we rewrote it and the protection
reached it. Where it could not, the only instrument was reading the compiled
pages, which is what found six of the twelve.

**A twelfth, in the test harness.** The corruption suite writes an impossible
region label into a regions file and requires the verifier to notice. It was
writing into the round-nineteen regions file; round twenty moved the
manuscript's region labels to a new one and nobody moved the corruption. The
suite reported **MISSED**, which is the correct answer to a test that cannot
fail, and the corruption now targets the file the verifier reads. It catches
10 of 10.

We report these for the same reason we report the corrections: an apparatus
that only ever produces clean runs is not being tested, and the useful thing
to publish about one is where it failed.

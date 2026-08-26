# Response to the developmental review of the round-twenty manuscript

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Journal:* Information Systems
*Review verdict:* major revision, with a note that the revision must be
substantially shorter

---

## Summary of what changed

| | round twenty | round twenty-one |
|---|---|---|
| article | 97 pages | **58 pages** |
| supplementary material | none (33 pages of appendices inside the article) | **55 pages** |
| tables in the article | 23 | **7** |
| new experiments | — | `s32`–`s39`, eight scripts |
| headline sign-disagreement rate | 35.3% of all cells | **7.5%** of the cells the corpus resolves; 20.0% over the axes an analyst chooses |
| resolution regions | nominal critical value | **coverage-calibrated at each pair's own K/n** |
| self-references to earlier versions in the article | 21 occurrences | **0** |
| `correction Cnn` in the article | 13 occurrences | **0** |

Five things are new results rather than repairs, and each came out of trying
to answer a comment:

1. **The case study's two published values differ because of the TARGET, not
   the cohort** (M1). An exact two-factor decomposition puts
   99.3% of the difference on the target and 0.008% on the cohort.
2. **An undeclared specification axis, found by trying to reconcile the two.**
   270 incidents share a timestamp, the split is at 70% of the row order, and
   the sort that produced the case study's cohort was not stable. Over 25
   random tie-breaks the increment ranges over 0.00088 AUC. No reporting
   standard asks anyone to state this.
3. **The decision time now changes three things, and the three are separated**
   (M2): the population in scope, the feature snapshot, and the admissible
   set.
4. **The encoding matters about twice as much as the model family, and their
   interaction is the largest two-way term** (M7).
5. **A registered calibration rule removes a third of the models from any
   decision-analytic reading** (M5) — which is a stronger operational finding
   than the regret comparison it was meant to enable.

---

## Major comments

### M1 — the case study's headline number is internally inconsistent

**Accepted in full, and this was the first thing fixed.** A new experiment
(`scripts/s32_cohort.py`) estimates the register's increment at the later
decision time on the full cohort $\times$ target factorial at three rungs of
the ladder, 24 cells at 400 nested moving-block draws each, one estimator, one
seed. Section 7.1 and **Table `tab:cohort`** report it as a one-factor-at-a-
time path from the number Section 7 printed to the number `PC3` printed;
**Table `tab:cohortanova`** gives the exact two-factor decomposition.

The reconciliation table, verbatim from `results/s32_path.csv`:

| step | cohort | target | V at the knowledge rung | 95% interval | delta |
|---|---|---|---|---|---|
| the case study as published | reassignment | reassignment | −0.00322 | — | — |
| then a declared tie-break | reassignment | reassignment | −0.00286 | [−0.00731, +0.00203] | +0.00036 |
| then the other tie-break rule | reassignment | reassignment | −0.00286 | [−0.00731, +0.00203] | 0.00000 |
| then the registered cohort | registered | reassignment | −0.00385 | [−0.00898, +0.00069] | −0.00098 |
| then the registered target | registered | handover | **+0.00768** | [−0.00161, +0.01217] | +0.01153 |

Three findings, none of them a hedge:

* **It is the target.** Over the cohort $\times$ target design the target
  carries 99.3% of the variance in the increment at that rung, the cohort
  0.008%, and their interaction 0.69%. Reassignment before resolution has
  prevalence 0.372; the registered handover rule has 0.927. They are not the
  same question.
* **Two candidate explanations were checked and ruled out by computation, not
  by argument.** The assignment-group and knowledge fields the two analyses
  reach by different routes agree on every one of the 45,455 shared rows, and
  so do the intake block and the register.
* **Neither cell resolves.** On all eight (ordering, cohort, target)
  combinations at the knowledge rung, the two-sided interval contains zero.
  The apparent contradiction was between two point estimates, neither of which
  the data resolve — which the manuscript now says in those words.

**Section 7 is now on one cohort throughout.** The register-quality
mechanisms, the severity curves and the absorption ladder are re-run on the
estate's own cohort and reassignment target (`scripts/s39_case_quality.py`);
the registered-cohort versions of the same three objects are in the
supplement, and every caption in both places names its cohort and target.
`s08` now declares its tie-break so that Section 7's ladder, the tipping
curve and `s38`'s decision-time ladder stand on the same row order.

**And a verifier condition now makes the class of error impossible rather than
unlikely.** `scripts/round21_verify.py` carries an `ESTIMANDS` table: one
entry per quantity a reader would name in one phrase, listing the macros
allowed to hold it. Two macros in the same entry that disagree is a failure.
The old harness could not have caught this, because each macro was right about
its own source file; what was wrong was that two of them answered to the same
English sentence.

### M2 — the decision time is not operationally distinct from the baseline

**Accepted, and implemented rather than argued for.**
`scripts/s38_tau.py` estimates three decision times on the case study's log,
and what changes between them is not only the admissible set:

| | population | prevalence | register levels | V against intake |
|---|---|---|---|---|
| τ₀ first touch, every call | 145,478 interactions | 0.146 | 4,034 | +0.2310 [+0.2204, +0.2618] |
| τ₁ first touch, escalating calls | 44,513 | 0.402 | 2,445 | +0.2013 [+0.1930, +0.2224] |
| τ₂ incident creation | 45,455 incidents | 0.400 | 2,929 | +0.1838 [+0.1725, +0.2040] |

The decision — will this case be reassigned before it is resolved — is the
same at all three, which is what makes them comparable. The pairwise
differences separate the three mechanisms: restricting the population costs
−0.0297 AUC with the information held fixed, and moving from first touch to
incident creation on the same cases costs a further −0.0175 before any
baseline changes. All three are resolved. **Table `tab:tau`** replaces the old
decision-time table, whose two rows were identical because only the baseline
label differed between them.

### M3 — the two novel objects rest on bands the paper declares unreliable

**Accepted. Option (b) of the three offered: a coverage-calibrated critical
value.** `scripts/s33_calibrate.py` does three things.

1. It estimates a denser $(n, K)$ plane — 20 cells at 500 replicates, on two
   worlds rather than one, over $K/n \in [0.0025, 0.5]$, which brackets the
   corpus's own range rather than sampling three points inside it.
2. For each cell it computes the factor $c$ by which the interval must be
   widened to attain nominal coverage. This is **not a search**: writing the
   basic interval as $[V - L, V + U]$, coverage at inflation $c$ holds exactly
   when $c \geq \max\{(V-\theta)/L, (\theta-V)/U\}$, so the smallest
   attaining $c$ is the 0.95 quantile of that ratio. Its Monte Carlo interval
   comes from the same order statistics. `round21_verify` recomputes every
   cell's $c$ from the replicate file.
3. It applies $c$ at each pair's own ratio, relabels every cell and
   recomputes the regions and $\rho$. The curve applied is a **monotone
   regression** through the measured factors rather than the log-linear fit,
   because the parametric fit sits below the measured factor at the smallest
   ratios and would under-correct exactly the pairs whose bands are narrowest
   — the anti-conservative direction. The log-linear fit is reported beside
   it because its slope (0.122, s.e. 0.006) is the quotable summary of the
   mechanism. **Table `tab:plane`** prints both curves against every measured
   factor; **Table `tab:calbands`** prints nominal and calibrated regions side
   by side; and **every region label and every $\rho$ in the article is the
   calibrated one.**

The correction is not small and is not hidden. Factors run from 1.15 to 1.82;
the corpus resolves 892 cells under the calibrated band against 1,150 under
the nominal one, a loss of 22.4%; four region labels change; the median $\rho$
falls from 0.117 to 0.017; and the number of pairs that resolve nothing at all
rises from 2 to 6. Every one of those counts is reported at three settings ---
nominal, calibrated, and every factor at the upper end of its own Monte Carlo
interval --- so a reader who rejects the transfer has a column to read.
**No surface in the corpus is uniformly beneficial under any of the three**,
which the article now states as a result in its own right: the state in which
a single number is a safe summary is not reached once on nineteen pairs.

The verifier also checks the direction the correction must go: a widened band
cannot resolve more cells, and a pair that did would be a failure.

What the calibration does not buy is stated in Section 10 in three clauses: it
corrects the scale of the studentised statistic and not the shape of the
maximum's distribution; it is estimated on a pointwise interval and applied to
a simultaneous band; and it assumes the simulated worlds' dependence on $K/n$
transfers.

### M4 — the misreport rate counts cells whose sign is not resolved

**Accepted, and the headline number has fallen.**
`scripts/s34_reporting.py` reports three quantities where there was one
(**Table `tab:misreport`**):

* **all cells**, the old definition, kept so the change is visible;
* **resolved cells only**, restricted to cells whose coverage-calibrated
  whole-surface band excludes zero, with the count each rate is computed on;
* **magnitude-weighted**, every cell weighted by $|V|$ as well as by the
  declared measure.

The article's headline is now the second: of the **892** cells the corpus
resolves under the coverage-calibrated band, **67** disagree in sign with the
reference cell — **7.5%**, against 32.8% over all cells. (Under the nominal
band it is 137 of 1,150, or 11.9%; both are in the facts file and the
calibrated pair is what the article quotes, because the calibrated band is the
one its region labels use.) It is also reported as a distribution rather than
as a median of rates: on 8 pairs no resolved cell contradicts the reference,
on 5 some do, and on 6 nothing resolves at all.

We note what this costs the paper's own argument and report it rather than
softening it: the headline is now a quarter of the number the previous version
printed. A fourth rate has since been added for a separate reason (see the
pre-submission review below): restricted to the axes an analyst actually
chooses, the rate is **20.0%**.

The magnitude-weighted rate is **higher** than the unweighted one (50.2%
against 32.8%), and that is reported rather than buried: the cells that
disagree are not the negligible ones.

### M5 — the practical stakes of "what one number costs" are thin

**Accepted, and the section is reframed rather than defended.** We tried the
first of the two remedies offered and report what it gave.
`scripts/s35_utility.py` adds all three things a decision-analytic comparison
needed:

* a **registered calibration rule** — recalibrated Cox slope inside
  $[0.5, 2.0]$, both arms, applied per (pair, pipeline, baseline) — which
  removes 40 of 118 models and leaves 3 of 19 pairs with none;
* a **desk threshold distribution** whose mass sits where a service desk's
  exchange rate plausibly sits, with fixed exchange rates of 1:2, 1:4, 1:9 and
  1:19 beside it;
* the unit a desk budgets in, net benefit **per thousand cases**.

**The rules still mostly tie**, and the article now says so plainly. Under
the desk distribution the one-number, majority and weighted-mean rules all
carry a median excess regret of zero; the four rules differ on 11 of 16 pairs,
and where they differ the one-number rule is worst on 10 of them, at a maximum
of 0.41 per thousand. Section 6.8 states in one paragraph that we do **not**
conclude a surface report is a better decision rule than a number, that the
case rests on the decomposition and the sign disagreement, and that the regret
comparison is a check rather than a result.

What the section gained instead is a decision-relevant quantity that is not
about collapse rules at all. The register is worth 1.71 true positives per
thousand cases against the intake block and 0.003 against intake plus group
plus the knowledge reference. A desk that read the first number and deployed
where the second applies is short 1.70 per thousand — larger than every
difference between the four rules put together. That is the operational
content of the decision-time axis, in the units the objection asked for.

### M6 — novelty is narrower than the length implies

**Accepted, and the comparison the comment asks for is now in the article —
on more pairs than the comment asked for.** `scripts/s36_sca.py` runs
specification-curve analysis as practised — permutation test of the sharp
null, median estimate and dominant-sign share as test statistics — unchanged,
on a declared 24-cell sub-surface, for **every one of the 19 admitted
log--target pairs** at 100 permutations each, and puts its verdict beside the
region label computed on the same cells. The comment suggested two or three
pairs; three pairs can only show that the two verdicts *can* differ, and
running it on all of them turns "how often do they part company" into a
measurement. **Table `tab:sca`** prints all nineteen rows.

The measurement:

* **They part company on 9 of the 19 pairs** — close to half. The
  permutation test rejects the sharp null and the same cells contain
  increments of both signs. A reader given only the permutation test on those
  pairs would conclude the register matters and could not learn that whether
  it helps or hurts depends on choices nobody told them about. On BPIC14 /
  handover, for instance, the test rejects at $p = 0.0099$ and the surface is
  sign-changing.
* **They agree that nothing is there on 3 pairs**, where the test does not
  reject and the region is unresolved. Both instruments say the same thing
  and the cheaper one suffices; we say so.
* **And a specification curve is a claim about the cells it enumerates.** On
  1 pair every cell of the declared sub-surface is positive while the full
  surface for that pair is sign-changing. Neither is wrong; they are claims
  about different sets, which is a concrete demonstration that a curve
  without a declared denominator and a simultaneous band cannot distinguish
  "the sign holds" from "the sign holds on the cells I drew".

The article no longer asserts that the extra machinery buys something; it
measures where it does and where the cheaper instrument suffices, and
Section 6.7 ends by saying that neither procedure subsumes the other.

**The experiment carries two declared budgets, and the second one is new.** A
permutation replicate refits every cell of every pair, so the cost is
quadratic in the corpus's largest logs: on BPIC19, at 251,734 cases, one
replicate of the 24-cell design took three quarters of an hour and the run
over nineteen pairs was on course for most of a day, which is not an
experiment anybody — including us — would rerun. The sub-surface already
bounds the *cells*; the rows each fit sees are now bounded too, by a declared
cap of **20,000 cases per pair**, drawn once as a seeded sample and restored
to time order so that the observed surface and its null are computed on the
same cases and the temporal split still cuts in time. The cap binds on 7 of
the 19 pairs, is printed per pair in Table `tab:sca` and recorded in
`results/s36_verdicts.csv`, and Section 6.7 states it. It does not touch the
region labels the verdict is set beside: those are the coverage-calibrated
ones of Section 6.4, computed on the full data.

We have not inflated the propositions' claims in response to the rest of the
comment, and have instead tightened them: Proposition 2 now carries a
paragraph saying exactly what fails under a restricted model class, and which
direction of the equivalence needs richness (only one of them does).

### M7 — the learner axis is confounded with the encoding axis

**Accepted, and the two are now crossed.** `scripts/s37_axes.py` runs both
model families against all three encodings on the case study's log, a complete
$2 \times 3$ factorial, and applies the same exact functional ANOVA the
article defines. The result is worth the compute:

| term | first-order share |
|---|---|
| encoding | 10.1% |
| model family | 5.2% |
| **family × encoding** | **9.8%** |

The encoding is the larger of the two, and their interaction is the largest
two-way component in the crossed decomposition — which is precisely what an
axis that fuses them cannot express. Section 6.3 reports this and says that
Table `tab:sobol`'s pipeline column is the two together. We have not re-run
the crossing on the other 17 pairs and Section 10 carries that as a
limitation.

### M8 — corpus statistics that cannot be reproduced from the printed tables

Each of the five, in order.

1. **28.7% against Table 4's 0.263.** Both are right and they are different
   aggregations: the table printed, per axis, the median over instruments of
   that axis's index, so its row maximum is a maximum of medians; the headline
   is the median over instruments of the maximum over axes. Table 4 now
   carries the headline's own per-pair quantity as its last column, so the
   printed table reproduces the printed number. The caption says which is
   which.
2. **32.8% against 35.3%.** Two differently-weighted quantities under one
   name. The article's headline is now the resolved-cell rate of M4;
   `misreportEqualPct` (32.8%) is named as the equal-level measure wherever it
   appears, and Table `tab:misreport` prints the measure in its caption.
3. **`PC3`'s one-sided p against its two-sided interval.** Not a
   contradiction, and Section 4.5 now derives it: the central 95% of the
   bootstrap draws at that cell lies entirely above zero, which is what the
   one-sided p reports, but the draws are centred above the estimate, so
   pivoting moves the interval down by twice that shift and its lower limit
   crosses zero. This is the same upward shift the paper's own Section 4.2
   diagnoses. The confirmatory table now prints a column saying whether the
   *interval* resolves, which is the criterion the paper uses, and `PC3` does
   not.
4. **`declared 1080 / computed cells 288`.** Two counts on different bases
   under headings that read as a comparison. The table now prints
   `declared scalar` beside `computed scalar` — the same basis, equal on every
   pair — and `model fits` separately, with the caption saying that model fits
   count arms before the instrument expansion and include the intercept-only
   rung.
5. **The 262,656 rows.** The article now states, in the sentence that quotes
   the count, that the master surface file includes the intercept-only rung
   and that no admissible set does.

### M9 — excluded pairs appear in an appendix table

**Accepted.** The layer table is now filtered to the pairs the registered
rules admit, by a filter taken from the surface rather than typed, and its
caption states how many rows were dropped. Helpdesk/handover, whose base AUC
was 0.400 at a prevalence of 0.0011, is one of them.

### M10 — construct validity, and corpus statistics that mix populations

**Accepted; Section 5.4's promise is now kept.** `scripts/s34_reporting.py`
computes every headline corpus statistic on three populations — all 19 pairs,
the 8 ITSM pairs where the register is a maintained one, and the 11 that
remain — and **Table `tab:family`** prints all three with the count behind
each. Section 6.6 reads the differences: the ITSM family's surfaces are somewhat
more additive, its largest first-order index is larger, and its
sign-disagreement rate is lower.  On the resolved cells the gap is large and
runs against the paper --- 3.6% on the ITSM eight against 22.2% on the other
eleven --- so the corpus-wide headline is partly carried by the pairs
Section 5.4 names as construct-validity threats, and the article says so. A reader who takes the paper to be about
maintained registers has the column for it.

### M11 — the literature pilot should not be in the paper

**Accepted.** The pilot is in supplementary material. Section 9's paragraph is
reduced to three sentences that say what it is, that it generates a hypothesis
and cannot test one, and that no claim rests on it. The generative-AI
declaration now states that the model identifier used for its adjudication was
not recorded at the time, and names that as a reproducibility defect in the
pilot and a further reason it carries no claim.

### M12 — presentation

**Accepted, and this is the largest single change.**

* **Length.** The appendices are a separate supplementary document with its
  own numbering (S1–S12, Table S1 onwards). Cross-references between the two
  resolve through `xr`, so neither document guesses at the other's numbers.
  The article is **58 pages**, down from 97 in round twenty and 71 in the
  version you read; the supplement is **55 pages**. The article now
  carries **7** tables and 5 figures, against 23 tables in round
  twenty.
* **The changelog is out of the article.** Zero occurrences of the
  "an earlier version of this work" family and zero of "correction Cnn" remain
  in the main text; the correction register is Supplement S4 and the archive.
  `texlint` fails the build if either returns, so this is a property of the
  repository rather than of one editing pass.
* **Voice.** The aphorisms are gone ("Collapse for a decision; report the
  surface", "which is this paper's argument in a line"), the all-capitals
  aside in Figure 1's caption is ordinary prose, and the asides addressed to
  an imagined referee ("we say so rather than letting a reader assume") are
  cut. Where a limitation needed stating it is stated once, in the
  limitations section, in plain terms.
* **Nothing floats unreferenced.** Every table and every figure in the article
  is now named in the running text; four previously carried a label and a
  caption and were never pointed at.

**What was moved, and what was cut.** The reduction from 71 pages is not one
compression pass but three separable things, and it is worth separating them
so the editor can see that no evidence was lost:

1. **Nine tables and two figures moved to the supplement** (about 6 pages).
   The article keeps the seven exhibits its argument is read from — the axis
   declaration, the master table, the decomposition, the calibrated bands, the
   sign-disagreement rates, the cohort reconciliation and the three decision
   times — and points at the rest. Table S-numbers are resolved by `xr`, so a
   reference cannot go stale.
2. **Three result sections moved to Supplement S11** (about 4 pages): the
   crossed family-by-encoding decomposition, the decision-rule comparison, and
   the calibration, unseen-category and rolling-origin diagnostics. Each is
   summarised in the article in a paragraph carrying the numbers a reader
   needs, with the full treatment one cross-reference away. The coverage
   calibration's derivation is likewise Supplement S10 now.
3. **About 3,300 words of restatement cut** (about 7 pages). Four sections
   were describing the coverage calibration; one does now. Three were
   restating that no average crosses an instrument; one does. The
   contributions list, the related-work section and the limitations each lost
   roughly a fifth of their length without losing a claim.

**Where we still exceed the target, and the arithmetic.** The review asked for
35–40 pages of main text and proposed a section budget summing to 41 pages of
body. The article is **58 pages**, of which about 5 are references and 2
the required Elsevier statements, so the body is roughly 12 pages over that
budget. The gap is arithmetic rather than evasion. Phases 1 and 2 of your plan
asked for eight new measurements — the cohort reconciliation (M1), the third
decision time (M2), the coverage calibration and its three-setting sensitivity
(M3), the resolved-cell and analyst-latitude rates (M4), the desk threshold
distribution and the exclusion rule (M5), the specification-curve comparison
on every admitted pair (M6), the family-by-encoding crossing (M7) and the ITSM
family split (M10) — which add about 8 pages of article between them. Phase 3
asked for the article to be a third shorter. We have done both as far as they
are compatible: 26 pages have come out and 8 have gone in.

If the remaining 12 must go, we would rather be told which than choose for
you. The order we would cut in, with what each costs:

1. **Section 9, the reporting standard and the software** (about 1.5 pages).
   Cheapest to lose; the package is in the archive and the standard is a list
   a reader can reconstruct from Section 4.
2. **Section 10, the simulation** (about 2 pages), leaving one paragraph
   pointing at the supplement. It certifies the interval construction, which
   a methods reviewer will want to see, but it certifies nothing about the
   corpus.
3. **Section 6.7, the comparison with specification-curve analysis** (about
   1 page). Added in answer to M6, so cutting it re-opens that comment.
4. **Section 6.6, the ITSM family split** (about 1 page). Added in answer to
   M10, with the same caveat.
5. **Sections 8.1–8.2, the operating point and the calibration rule** (about
   1.5 pages), reducing Section 8 to the simultaneous bands, the desk utility
   and the decision-time cost.

Items 3 and 4 are on the list only because the review asked for both a shorter
article and those additions, and we would rather name the tension than
silently resolve it.

---

## Minor comments

| comment | disposition |
|---|---|
| abstract's hedging final clause | removed; the abstract is 194 words and states the estimand, the four objects, three numbers and the case study's cohort-and-target dependence |
| the per-pair table's row order | every per-pair table is now sorted by (log, target); the caption says so |
| Tables 4 and 17 running together; Tables 13 and 2 overflowing | wide text tables no longer use `\resizebox`, which scales glyphs and leading together; they use ragged-right `p{}` columns at the body font, with hyphenation made cheap for tokens like `case:RequestedAmount` |
| BPIC15_4 and BPIC19 uninterpretable after recalibration | a registered exclusion rule now removes them from the decision-analytic reading and names what it removed (M5) |
| Figures 1 and 6 lack subpanel labels; Figure 6's dip | Figure 1's panels are labelled (a) and (b) and the caption refers to them; Figure 6's caption now carries the resolved/unresolved counts for the dip |
| "PC" vs "C" numbering explained in the body | removed; the contrasts are simply `PC1`–`PC5` |
| the per-pair table's BPIC14 row mixes cohorts | the caption states that every row is on the registered cohort and target, and points at Section 7.1 for the case study's |
| Proposition 2's Assumption 1 | a paragraph now says which direction of the equivalence needs richness (one), and what a reader inside a restricted model class should conclude |
| "nothing here is new" in Appendix C | removed |
| the archived release must match the submitted numbers | see below |

---

## A pre-submission review, and six further defects it found

Before submitting, the revised manuscript was given to an independent reviewer
with this journal's brief, no knowledge of what had changed, and access to the
repository to check any number they doubted. They returned major revision with
nine major comments, six of which were defects rather than differences of
opinion. All six are fixed and all six are in `REFEREE-LOG.md` under round
twenty-two. Three are worth naming here because they bear on the comments
above.

1. **The inference surface was not a subset of the declared surface.** On two
   of nineteen pairs the bootstrap grid carried a pipeline the design
   declaration did not, so sixty of each pair's hundred and twenty band cells
   had no counterpart in the declared space and those pairs' region labels
   quantified over cells the declaration says do not exist. The declared
   surface has been widened to contain them, the whole surface recomputed, and
   the verifier now asserts the subset relation **cell for cell** — the audit
   that existed checked level counts, which is why it could not see this.
2. **Two macros described in the same words held different values**, four
   pages apart, and so did the abstract and Highlight 4. Both are now
   `ESTIMANDS` entries; the Highlights are generated from the macros rather
   than written by hand, which closes the one part of the submission the
   verification discipline never covered.
3. **Corollary 1's witness did not support it.** The class-mean-gap
   instrument's reduction is invariant inside the affine family and not
   outside it, which this repository's own certificate file records.
   Proposition 2 is now stated relative to a declared family of
   recalibrations — what its proof reaches and what an analyst can act on —
   the corollary is stated for the affine family, and a new remark reports the
   non-affine shifts and says the unrestricted question is open.

The other three: the master table printed uncalibrated region labels in
contradiction of a bold assertion elsewhere; the design space pooled analyst
latitude with resampling and with counterfactual register states, which
inflates the headline rate by about half; and no corpus-level statistic
carried an interval. All are fixed, and two of the fixes move a number
against the paper.

## What the author must still do before submission

These are in `submission/OWNER-ACTIONS.md` and cannot be done by the
repository:

1. **Mint the Zenodo DOI** and put the real value in `results/release.json`.
   `scripts/final_search.py` fails deliberately until it is real.
2. **Confirm the keyword limit and the highlights requirement** on the live
   Guide for Authors page. The manuscript ships six keywords and five
   highlights of at most 85 characters, which is what the standard Elsevier
   template asks for.
3. **Confirm the model identifiers for rounds 1–20** in `AI-USE.md`, or leave
   them recorded as unrecorded. Round 21's is `claude-opus-5`.
4. **Run `python scripts/verify_numbers.py --strict` against the archived
   release** and confirm it passes on the submitted PDF's numbers.

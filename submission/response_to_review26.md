# Response to the sixth referee report

> **HISTORICAL — read with the round-27 letter beside it.** This letter was
> accurate when it was written and two of its framings did not survive the
> next round. It says "most of the variance belongs to no single axis" net of
> resampling; round 27 found that holds on 7 of 19 pairs and the article now
> withdraws it, carrying instead the claim that *which* axis leads is a
> property of the pair. And it says the nested interval "beats" the
> fixed-model interval by 1.3 Monte Carlo standard errors; the article's own
> Section 4.1 calls that gap one this evidence cannot resolve, and Section 11
> now says so too. Both corrections are in `response_to_review27.md`. The
> letter is kept unedited below, because a response letter is a dated record
> of what was claimed when, and editing one to match a later manuscript is
> the thing this project's correction register exists to prevent.


*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Recommendation received:* major revision

Thank you for a report that is more useful than most published papers. Every
finding in it was reproduced from the deposited result files before it was
acted on, and two of them changed headline claims this paper had been making
for six rounds. Those two are answered first, because a reader is entitled to
see a withdrawal stated rather than discovered.

**One thing is said at the top so that nothing below implies otherwise.** Four
of the Phase-A items — **A1** (the weighted bootstrap), **A2** (≥400 draws on
a designed inference surface), **A6** (degradation on both halves as a new
run) and **A7** (a prefix axis, and the crossed pipeline decomposition on the
ITSM pairs) — require the corpus refetched and every arm refitted, and **this
revision does not run them**. Section 11 names each as the change we would
make first, in order, with the reason. Where a claim depended on them, the
claim has been weakened rather than the work implied. A6 turns out to need no
run at all, for the reason given under M9.

---

## The two headlines this report retired

### M3 — the split axis conflates sampling noise with specification sensitivity

**Conceded, and the correction is larger than the report anticipated.**

You are right that five of the split axis's six levels are expanding-origin
folds on the same data, and that a decomposition pooling them reports sampling
variability as specification sensitivity. Because the decomposition is exact
and orthogonal over a complete factorial, the repair is a partition rather
than a model: every component either involves the split or does not, so

> analyst choice + counterfactual + mixed + resampling = 1

exactly. `scripts/s42_round26.py` computes it; the identity holds to 4.4×10⁻¹⁶
and is now a verifier condition.

Taking each column's median across the corpus — four medians, which do not
add — **the components involving the split carry 71.7% of the variance**,
against 13.3% for the choices an analyst makes, 4.2% for the register-quality
counterfactual and 4.5% for the components joining them.
Resampling is the largest of the four on **17 of 19 pairs**. We also ran a
check you did not ask for, because "the split is resampling" could have been
an artefact of the axis mixing one rule-choice with five folds of it: dropping
the single temporal holdout so that the axis is folds and nothing else moves
the share from **71.7% to 71.0%**.

**The headline reverses.** On the fold-averaged surface — which carries 28.3%
of the pooled variance — the higher-order share is **26.3%** against the
pooled **56.0%**, and it **no longer exceeds the largest first-order index**
(38.8% against the pooled 28.7%). Pooled, the interactions carry more than any
main effect on 13 of 19 pairs; net of resampling, on 7 of 19.

*Most of the variance belongs to no single axis* is therefore a property of a
surface that counts five folds as five specifications, and it is withdrawn.
What survives, and is what §6.2 now argues, is weaker and still sufficient:
**which** axis leads is a property of the pair — the rung on some, the
register-quality condition on others, the pipeline on others — so an analyst
cannot learn from somebody else's paper which of their own choices their
answer turns on.

*Where:* new §4.5 paragraph and equation (7); §6.2 rewritten with the
fold-averaged decomposition primary and the pooled one beside it; new Table 5;
abstract; §11; §12.

### M4 and M5 — sign disagreement ignores magnitude, and two headlines disagreed

**Conceded. The sign-disagreement rate is withdrawn as a headline.**

Your arithmetic reproduces exactly: **8 of 19** reference increments lie
inside ±0.01 AUC. We also found that only **5 of 19** pairs resolve the sign
of their *own* reference cell, which is stronger than the six you inferred
from Table 3.

A minimal practically important difference of **0.01 AUC** is now declared in
one place in the code and applied on the AUC sub-surface — Remark 1 (formerly
Proposition 1) forbids carrying a threshold in AUC units to another
instrument, so declaring one MPID per instrument would have been five
arbitrary conventions rather than one. On that sub-surface:

| restriction | cells | disagree | rate |
|---|---|---|---|
| every admissible AUC cell | 5,808 | 1,538 | 26.5% |
| both increments above the MPID | 3,291 | 434 | 13.2% |
| the band resolves the cell | 197 | 5 | 2.5% |
| resolved **and** above the MPID | 185 | 1 | 0.5% |
| **all three restrictions §6.4's argument implies** | **42** | **1** | **2.4%** |

M5 asked us to state one headline and defend it — 7.5% or the 12.9% §6.4
itself said the argument asked for. The answer is neither: with the third
restriction the same argument also implies, the corpus retains 42 cells and
one of them disagrees. A rate over 42 cells is not a rate, which is an
argument this paper makes about other people's denominators and now makes
about its own.

**Two things came out of the withdrawal that are worth more than what went.**

*The 7.5% was never an AUC statement.* Split by instrument, the resolved-cell
disagreement runs **2.5% on ROC AUC to 11.2% on Nagelkerke R²**. That is
Remark 1 appearing in the corpus, not a claim about specifications, and the
manuscript now says so where the rate is quoted.

*The magnitude survives every restriction the rate does not.* Over the cells
the band resolves, admissible specifications sit a median **0.0430 AUC** from
the reference cell, and **0.0534** under the full restriction — four to five
times the MPID. So the corrected claim, which is what the abstract and §12 now
make, is that **a one-number report is usually right about the sign and
usually silent about the size**, and that on 14 of 19 pairs the data do not
determine the sign of the cell it stands on.

*Where:* §6.4 rewritten; new Table 6; abstract; highlight 4; §11; §12; the
MPID added to the reporting standard in §9.1.

---

## The rest of the major comments

### M1 — the inferential claims in the front matter are not supported by the body

**Conceded; option (b), as you expected, since (a) needs A2.**

"Coverage-calibrated" is gone from the highlights. The abstract now says the
bands' coverage is *measured against a known answer and found short of
nominal*. Contribution 2 says the same and adds that the labels are therefore
**descriptive diagnostics and not guarantees**. §4.3's three-paragraph
coverage discussion is one paragraph and a forward reference, as you asked;
the detail stays in §10.4 where it is computed. §11 leads with it.

### M2 — the nested refitting bootstrap is under-justified and is the source of the bias

**Conceded on the justification; the repair is named and not run.**

Your measurement of the gap is right and is now in §4.1 as a macro: the nested
interval beats the fixed-model interval by **1.3 Monte Carlo standard errors**
at the 0.7-point standard error §10.2 states. §4.1 no longer offers that as
the reason for the design. The reason it now gives is that the variability the
nested scheme admits is variability the estimand contains and the fixed-model
interval excludes by construction — which is an argument about the estimand
and not about this comparison.

Your proposed repair is right and §11 adopts it as the first change we would
make: **drawing weights (Dirichlet or i.i.d. exponential) per moving block
rather than resampling rows**, so every row has positive weight in every draw,
every register level is present in every refit, and the displacement
disappears at source rather than being pivoted around. It is a change to one
function and a re-run of the whole inference surface. We have not run it, we
do not report the construction comparison across the (n,K) plane, and §11 says
that no conclusion in the paper should be read as evidence that the refit's
cost was worth paying.

### M6 — the design-space declaration is inconsistent

**Conceded. New Table 4, in the main text.**

It gives, per pair: which attribute plays the register and which the free
field, whether the pair is ITSM, the number of levels on each of pipeline,
split, register quality and baseline rung, the case count and the register's
cardinality. §3.1 now states that the **target indexes surfaces rather than
being an axis of one**, and that the decision time, the operating point and
the cohort vary on the case study's log alone; §5.2 states the pipeline
admission rule in full (a function of the log's row count and nothing else);
§11 carries the gap between Definition 1's nine axes and the five the per-pair
factorial varies. "Nine axes" no longer appears as a description of what was
varied.

### M7 — the main text is not self-contained

**Partly conceded, and it collides with C6. See the note on length below.**

Moved in: the roles-and-levels table (was S11), **the decision-time ladder
(was S9)**, the resolution triple, the MPID table, the register-layer result
(in §7.4's prose, with the supplement carrying the full layer ladder), and a
glossary. Not moved in: the region figure, the decision curve, the leakage
tipping-point figure and the coverage table, because each is a page and the
same report asks for a body of ~30 pages. We would rather be told which of
those you want than guess.

*(Checking this claim against the rendered pages found that the decision-time
ladder had been moved to the supplement in an earlier round's length
reduction, while §7.2 still discussed it as though a reader had it. That is
what C3's first item was about, and it is now back in §7.2.)*

The supplement is supplied with this revision, and the self-containment claim
in §1 has been replaced by a specific list of what the article prints and what
the supplement is for.

### M8 — the payoff for the journal's readers is deferred to the supplement

**Conceded. §7.4 is now a real subsection.** It carries: the field-to-role map
for BPIC14 in the estate's vocabulary (affected configuration item; its type
and subtype; the assignment group; category, impact, urgency, priority; the
knowledge reference); **τ₀/τ₁/τ₂ in service-desk terms** (an interaction is
logged / the same moment restricted to escalating calls / an incident record
is created), with the population of each; the ladder read down; **the
register-layer result** — over the intake baseline on the reassignment
question, the item's type is worth 0.134 AUC, its subtype 0.163, the item
itself 0.257, and the item still adds 0.109 with the subtype already in the
model; and three named conditions under which the answer would move
(timestamped field history, population completeness at the decision time, a
target the desk acts on).

The layer finding is framed for a layered service model — the layers are not
substitutes and **which one pays is a property of the question, not of the
estate** — and is explicitly not a procurement claim, since nothing here
prices what a layer costs to populate or keep accurate.

### M9 — is the register degraded in the training half only?

**Not conceded — but the manuscript could not have told you, and that is our
defect.**

`spec.degrade` returns a degraded copy of the **whole column**: both halves
are degraded, so the increment measures a model built on a degraded register
and deployed against one, which is the operational counterfactual you are
asking for. What is estimated from the training half alone is the mechanism's
**parameters** — which values are in the long tail, the frequency table a
corruption draws from, the identities a reconciliation failure splits — and
`spec.assert_train_only` executes that claim by perturbing the test half,
re-degrading, and requiring the training half's degraded values to be
identical.

§11's phrase "constructed from the training half" was ambiguous in exactly the
direction that mattered. §7.3 now states which halves are degraded, which half
the parameters come from, and why the distinction changes what the increment
measures. No new run is needed because the both-halves variant is what the
paper already runs.

### M10 — specification regret is undermined by the paper's own results

**Conceded; dropped from the contribution list, as you recommend.** It is a
robustness check on the other two arguments, said so in §4.7's title and first
paragraph, in the contribution list (now three items, with a paragraph
explaining the demotion), and in §11. The results are unchanged and still
reported in full.

### M11 — Propositions 1 and 2 are elementary

**Conceded.** They are Remarks 1 and 2, about a page shorter. The Richness
assumption and both constructions are in Supplement B, where the proofs were
already. The three repository file paths are out of the body.

### M12 — presentation

**Partly done.** A glossary table with the case study's own value for every
term; an overview figure of the method (roles → design space → surface →
three denominators → the objects); §11 rewritten as threats to validity
grouped construct / internal / conclusion / external, at 1,468 words against
the 1,794 you read, with the re-derivations of §4.1, §6.3 and §10.3–10.4 removed. The
first-person plural is unchanged in this revision — the manuscript is
consistent in it and changing voice throughout is a mechanical pass we would
rather do once, at the editor's preference, than half-do now.

### M13 — registration and reproducibility asserted, not verifiable

**Partly done, and the remainder is owner-only.** `scripts/verify_release.py`
already establishes that a `git archive` export carrying only what is
committed regenerates `paper/numbers.tex` byte for byte and all 52 generated
tables, and builds both documents with no file under `data/`. The datasets now
carry the `[dataset]` tag and the package is cited as software with its
version. **Minting the archive DOI needs the depositing account**; it is the
one item on `submission/OWNER-ACTIONS.md` that cannot be done from the
repository, and `scripts/insert_doi.py` inserts it and re-runs the gates in
one command once it exists. The repository name does reflect an earlier,
narrower scope; renaming it would break the DOIs and links already recorded,
so it stays and the cover letter says why.

### M14 — the paper positions itself in PPM but does not do prefix-based prediction

**Conceded; repositioned, since A7 is not run.** §11 now states plainly that
**we claim no result about predictive process monitoring's own benchmark**:
what is reported is case-level outcome prediction from event-log attributes,
the corpus measures sensitivity in a simpler adjacent setting on the same
data, and adding a prefix axis is the clearest next study. The keyword is
retained because the related-work discussion is genuinely about that
literature; if you would prefer it dropped, say so and it goes.

### M15 — related-work gaps

**Conceded; six references added**, each with the sentence that says what this
paper takes from it: many-analysts studies (Silberzahn et al. 2018; Breznau et
al. 2022), predictive multiplicity and Rashomon sets (Marx, Calmon & Ustun
2020; Semenova, Rudin & Parr 2022), the deep-learning PPM benchmark
(Rama-Maneiro, Vidal & Lama 2023), and the E-value / unmeasured-confounding
sensitivity tradition (VanderWeele & Ding 2017), which is named as the form
§7.3's leakage tipping point takes. The CMDB-quality and layered-service
strands are cited where §7.4 uses them.

We also acted on your §2 note: the manuscript no longer claims ρ as new.
§2 now says that **counting the share of specifications with an effect in a
declared direction is standard specification-curve practice**, and that what
is new is what the count is taken over and under — a simultaneous band, an
audited denominator, and a minimum resolved share.

### M16 — the registered handover target is near-degenerate

**Conceded and discussed, not fixed.** §5.3 states the prevalence, states that
the pair carries 9,600 of 29,040 admissible cells, and points at the ITSM-only
statistics. §11 raises both questions you ask — whether a generic handover
rule is meaningful on ITSM logs where reassignment is what a desk acts on, and
whether the window should close below 0.95 — and says we did **not** narrow
the rule, because narrowing an admission rule after seeing which pair it
admits is the thing a registered protocol exists to prevent. We would take the
decision differently in a new protocol and say so.

---

## The section-by-section list

Every item is done except where noted.

- **Title, abstract, highlights** — abstract rewritten as prose in the order
  you set, 200 words; highlights 2, 3 and 4 replaced (bullet 3 no longer says
  "coverage-calibrated"; bullet 4 now quotes the magnitude).
- **§1** — contribution 2 was a validation and is gone; the list is three
  items; the self-containment sentence is replaced by a specific list.
- **Figure 1** — the caption states the cell count and the product that gives
  it. *(Writing that sentence, we printed the wrong pipeline count and a
  product that missed its own total threefold. A verifier condition now
  multiplies a caption's stated factors and compares. See R26.8 in
  `REFEREE-LOG.md`.)* Faceting panel (a) by instrument is not done — it is a
  figure rewrite and the caption already carries the warning.
- **§2** — the novelty claim is narrowed, precisely, as above.
- **§3.1 / Table 2** — the three product measures are now defined in the main
  text; the target and the fixed axes are reconciled with Table 4.
- **§3.2** — the stationarity and mixing assumption is stated where the
  population limit is defined, not only in §10.4/§11.
- **§3.4** — the dangling clause is gone; the sentence now says the case
  study's ladder is the favourable case and gives the corpus figure beside it.
- **§3.5** — Remarks; "class-mean gap" defined where it is used; file paths
  removed.
- **§4.1** — the Monte Carlo standard error is beside the coverages; **K** is
  defined at first use, with the corpus's median and maximum.
- **§4.2** — the inference-surface rule is stated in full, and the resolution-IV
  fractional factorial you suggest is named in §11 as the change it should be
  replaced by.
- **§4.3** — one paragraph and a forward reference.
- **§4.4** — presented as **not confirmatory**, at a third the length; the
  "5 of the five" construction is fixed.
- **§4.5** — the split stratum, as above. *(The count "304 decompositions" is
  19 pairs × 4 measures × 4 axes; it is stated where it appears.)*
- **§4.6** — the minimum resolved share, and the triple in Table 7.
- **§5.1** — kept, shortened.
- **§5.2** — confirmed: only the first value of the group is used as a
  feature, and §5.2 now says so.
- **§5.3** — BPIC15\_2's exclusion code and case count are in the main text,
  with the prevalence-window discussion; the ITSM pairs are flagged in Table 4.
- **§6.1 / Table 3** — |F|, the beneficial/harmful/unresolved triple and the
  resolved share are in the adjacent Table 7, and the register field and ITSM
  flag in Table 4, because putting all five in Table 3 would have made it
  thirteen columns wide. The caption's admission is now a sentence in the text.
- **§6.2** — the baseline spread is restated over the realistic rungs; the
  pipeline-admission rule is stated. The crossed decomposition on the eight
  ITSM pairs is **not run** (it needs refits).
- **§6.4** — the MPID, as above; the unresolved-cell rate is no longer in the
  abstract.
- **§6.5** — the grammar is fixed; the permutation budget's p-value floor of
  0.010 is stated with why it is adequate here. The figure you suggest is not
  added, for length.
- **§6.6** — which rule is which is named, with the difference.
- **§7.1** — both candidate explanations are now given; the tie-break rule is
  in the reporting standard.
- **§7.2** — the τ₀ population is explained in the text.
- **§7.3** — the tipping point is cited to the sensitivity-analysis tradition;
  which halves are degraded is stated.
- **§7.4** — as above.
- **§8.2** — the calibration-slope window is justified, and **why isotonic
  recalibration is not applied before exclusion** is stated: it is a *level of
  the pipeline axis*, so applying it to a failing arm would substitute one
  specification for another and report it under the first one's name.
- **§8.4** — the promised/delivered per-thousand result is now in §12's fourth
  paragraph. It is not in the abstract, which had no room after the rewrite.
- **§9.1** — the tie-break rule, the halves the degradation applies to, the
  MPID, and the draw and effective-draw counts are all added, with a six-step
  recipe for applying the standard to a field of one's own.
- **§9.2** — `fieldvalue` is cited as software with its version.
- **§9.3** — the two indices are a coincidence, not a copy error: 25.94%
  against 25.90%, and the fourth figure is now printed. The prevalence-pilot
  paragraph is one sentence.
- **§10** — the fixed-model interval on every world, and a non-zero-truth
  family-wise coverage design, are **not run**: both need the simulation
  re-run.
- **§11** — rewritten as threats to validity, 1,468 words against 1,794.
- **§12** — restated on the analyst-latitude sub-space with the MPID; "only
  one of the three arguments is conventionally reported" is gone.
- **Declarations** — the AI declaration uses the journal's section title and
  template wording and no longer discusses the pilot; the funding statement
  already used Elsevier's wording. **The affiliation city and country are not
  supplied** — see below.
- **References** — `[dataset]` on the three data references; `fieldvalue`
  cited as software; reference [3] (Çarka et al.) moved from the encoding
  strand, where it did not belong, to the metric-choice strand, where its
  argument is the same as this paper's.

---

## Your arithmetic-consistency pass

Every check reproduces. Three are worth answering directly:

- **"Nested vs fixed-model coverage 93.0 vs 92.1 against MC SE 0.7 — gap ≈ 1.3
  SE — not a justification."** Agreed, and it is now printed as 1.3 SE.
- **"Median pair resolves 8/180 cells but corpus resolves 896/3,900 —
  resolution concentrated on few pairs."** Agreed; Table 7 now prints the
  resolved share per pair and the minimum-share condition acts on exactly the
  pairs this check identifies.
- **"Highlights ≤ 85 chars each."** Still true after the rewrite; the longest
  is 73.

---

## Two things we are asking the editor to decide

**Length.** The report asks for both C3 (six more tables and figures into the
main text) and C6 (a target of ~30 pages). The article was 48 pages before
this revision and is 59 after — body 49, declarations 4, references 6 — and
everything added is something the report asked for: the roles table, the
partition table, the triple table, the MPID table, the glossary, the overview
figure and §7.4. We have cut where the report sanctioned cutting (§4.3, §4.4,
§11, the propositions) and that recovered about five pages.

If the journal wants ~30 pages of body, these move to the supplement without
loss, in the order we would move them: §6.5 (specification-curve comparison,
~1.5 pp), §6.6 (decision rules, ~1 pp), the MPID table (~0.6 pp), the strata
table (~0.5 pp), §8.3 (~1 pp), and §10's grid and block-length sensitivity
(~2 pp). That is about seven pages and it is a decision about what an
*Information Systems* reader should be able to check without a second
document, which is the editor's to take rather than ours.

**The four refitting items.** A1 and A2 together are what would let the bands
carry a coverage claim in a headline. They are six to twenty hours of compute
on a workstation and a re-run of every downstream table. If the editor would
like them in the next revision rather than the one after, we will run them and
say so.

---

## Nine corrections we made to ourselves

Every gate was green and this letter was written when we read the sixty
rendered pages end to end, which this repository's history says is the only
thing that finds a certain class of defect. It found nine more, four of them
false statements, in a revision written the same week.

The one that matters to you: **we had two macros for one quantity**. Computing
the pooled decomposition's medians again, to compare them with the
fold-averaged ones, we grouped over a cell set that includes the demoted
cross-instrument scale. The manuscript then carried 28.7% *and* 29.1% for the
pooled largest first-order index, and 56.0% *and* 52.5% for the pooled
higher-order share, four sections apart. On the canonical basis the count of
pairs where the interactions exceed the largest main effect is **13 of 19, not
the 16 an earlier draft of this letter said**. The registry this repository
keeps for exactly this failure had no entry for the new macros; it does now.

The others: the crossed-pipeline macro used twice more where the case study's
four pipeline levels were meant; §6.4 still saying "two things are wrong ...
and both are corrected" while making three corrections, which is round
twenty-four's minor 4 recurring; a claim in §7.4 that the coarse register
layers are "nearly free" on the duration target when they are worth about a
third of the item; Table 1, §4.5, §10.4 and the supplement's abstract still
calling regret one of "four reporting objects" after the contribution list
demoted it; a contribution citing §6.4 for results that are in §6.6; §9.3's
correction of the UCI Adult coincidence, **claimed in an earlier draft of this
letter**, which had silently not applied; and §12 quoting a rate without its
AUC denominator in a paper about denominator discipline.

We report this rather than quietly fixing it because the report's C6 is about
density, and nine defects found by reading rather than by gating is evidence
for the referee's position and against ours.

## One correction we made to ourselves

Rewriting Figure 1's caption to state its own arithmetic, we used the macro
for the *crossed* pipeline factorial (12) where the figure's pair runs four
pipeline levels, and printed a product that missed its stated total by a
factor of three. Every macro in the sentence was correct and the sentence was
not — which is the one failure mode this repository's no-typed-numbers
discipline does not catch. `scripts/round26_verify.py` now multiplies a
caption's stated factors and compares them with its stated total, checks that
the four-way partition's residual is machine epsilon, and checks that the
MPID, resolved and fully-restricted cell counts are nested. All three were
exercised against injected errors before being accepted; the verifier reports
28 conditions and 0 failures.

## One thing that is not fixed and is one line

The Guide for Authors asks for a city and a country in the affiliation, and
you found neither. They are not derivable from any file in this repository, so
the two macros are undefined and the title block prints the visible `??`
marker — the same marker a missing result gets, so the omission is on the page
rather than in a checklist. It is the only unresolved macro in the build and
`submission/OWNER-ACTIONS.md` carries it.

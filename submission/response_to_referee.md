# Response to the referee — *Information Systems*

**Manuscript (previous):** *Four Choices Behind One Number: Reporting the
Incremental Value of a Recorded Field*
**Recommendation received:** reject as submitted
**Manuscript (this submission):** *Specification Surfaces for Incremental
Predictive Performance: Estimation, Uncertainty, and Multi-Log Evaluation*

---

## Summary of what changed

The referee's report was not a request for revisions. It said, in substance,
that several of the weaknesses touched the central evidence rather than the
presentation, and that a strong version would require a redesigned study and a
substantially new manuscript. We agree, and that is what this is: a new
manuscript, a new estimand, four new methodological objects, a rebuilt
inference layer, a rebuilt empirical design over every eligible log rather
than the ones where the answer resolved, and a literature component demoted to
a measured pilot with its own error rate.

The previous manuscript is retained in the archive as
`paper/iaai27_empty_cmdb.tex` so the version history stays legible, and every
claim of it that this version withdraws is recorded as a correction in
Appendix C.

Six of the referee's own **minimum resubmission gates** are addressed as
follows.

| Gate | Where |
|---|---|
| 1. The abstract and the later section make the same claim | Every number in the manuscript is a macro generated from a result file (Appendix G). There is one of each number; disagreement is structurally impossible. |
| 2. A complete admissible baseline does not depend on unresolved timestamp assumptions | §7.1 defines **two decision times** and estimates a surface for each; §7.3 gives a leakage tipping-point curve so a reader can place their own belief. Neither surface is "the" headline. |
| 3. The audit is rebuilt or no longer supports field-wide claims | §9.3 reports it as a **machine-assisted prevalence pilot** with measured screen sensitivity, an adjudicated sample of the papers the screen *rejected*, applicability-specific denominators, missing-data bounds, and an explicit statement of what its resolution is. **No claim in the paper depends on it.** |
| 4. Uncertainty includes model refitting and temporal validation | §4.2: a nested moving-block bootstrap that refits the entire pipeline inside every draw, plus rolling-origin validation as an axis of the design. §4.3: simultaneous max-$t$ bands. §4.8 measures both against a known truth in six worlds. |
| 5. Methodological novelty can be stated without "people usually report one number" | §3–§4 introduce the specification surface, an exact functional-ANOVA decomposition of its variance, resolution regions with a robustness index, simultaneous bands over the surface, Fieller sets for the ratio, and specification regret. The pilot is now a small subsection of §9. |
| 6. The central contribution is identifiable within the first four pages | The abstract, the contribution list in §1 and Figure 1 are all on pages 1–3. |

---

## Major comment 1 — the main conclusion contradicts the paper's own results

**Granted in full.** The abstract claimed the baseline choice moves the
reduction by more than the reduction itself; §10 of that manuscript said the
comparison was inflated by an intercept-only baseline "no analyst would
build"; and the abstract, introduction, threat section and conclusion retained
the strong form.

What is done:

1. **The intercept-only rung is excluded from every admissible set, by
   definition** (§4.7). It remains a point of the surface and is never a
   comparator.
2. **One master table** (Table 1) is computed from one frozen specification by
   one pass of one pipeline, and every claim in the abstract, the introduction
   and the conclusion is read off it.
3. **Every number in the manuscript is a generated macro.**
   `scripts/make_numbers.py` writes `paper/numbers.tex` from `results/*.csv`;
   the manuscript contains no numeric literal outside that file and the
   generated tables. A number cannot differ between the abstract and a table
   because there is one of it.
4. The specific inconsistencies the referee listed — the instrument count that
   treated two thresholds as two instruments, the $43.7\%$ / $35.0\%$
   mismatch, the section that said a withdrawn instrument was retained in a
   table that did not contain it — are recorded as corrections C17–C19 in
   Appendix C and cannot recur under (3).
5. The strong claim itself is **not restated**. §6 reports what the surface
   actually does, per pair, with a region label.

## Major comment 2 — the contribution is not sufficiently novel

**Granted, and this is the largest change.** The previous version's
contribution reduced to "these familiar dependencies are large here, so report
a grid". The new manuscript introduces four objects, each with a definition,
an estimator and a use:

1. **The specification surface** over a declared, enumerable design space
   (§3.1–§3.2), with the estimand $V_s(f)$ carrying learner, encoding, target,
   split, decision time, register quality, baseline, metric and operating
   point.
2. **An exact functional-ANOVA (Sobol) decomposition** of
   $\operatorname{Var}_s[V_s(f)]$ into first-order and total sensitivity
   indices per axis (§4.6), on two scales, so "which choice matters" is a
   measurement rather than a claim.
3. **Resolution regions and the robustness index $\rho$** (§4.7): a surface is
   uniformly beneficial, conditionally beneficial, sign-changing or
   unresolved, under *simultaneous* bands. $\rho = 1$ is named as the only
   state in which a scalar is a safe summary — which concedes the referee's
   point that a grid is not always necessary, and makes the concession
   measurable.
4. **Specification regret** (§4.9, §6.5): a decision-theoretic benchmark of
   one-number reporting against the surface, over every eligible log--target
   pair. This is the benchmark the referee asked for and the previous version
   did not attempt.

Two of the four turned out to have properties worth proving, and one of the
proofs changed the paper's advice.

* **Proposition 3** shows the sensitivity decomposition inherits the metric's
  scale: the indices of $V$ and of $\phi(V)$ need not agree, and there is a
  three-by-three design on which the leading axis changes under a square root.
  So the manuscript reports the decomposition on two scales and never names a
  dominant axis without naming the scale. (Two levels per axis will not do,
  and the first attempt at this proposition used a two-by-two design and was
  false; the reason is in Appendix B.)
* **Proposition 4** identifies the decision-optimal collapse of a surface. The
  difference between the expected loss of declining and of adopting is exactly
  the weighted mean increment, so the optimal single-action rule is *adopt iff
  the weighted mean is positive* — not the sign at any one cell, and not the
  count of positive cells. Measured over the corpus, that rule attains its
  bound on 19 of 19 pairs; the conventional one-number report attains it on 9
  and costs 57.2% more expected regret; and the cautious rule of adopting only
  where the whole surface agrees is the worst of the four, because it declines
  when the harm it avoids is smaller than the benefit it forgoes.

  This also resolves a tension a referee would be right to press on. There
  **is** a defensible collapse of a surface to one number. It depends on which
  specifications the reader's own practice makes likely, and the analyst does
  not know that. So the analyst reports the surface and the reader collapses
  it: *collapse for a decision, report the surface*.

The `fieldvalue` package is now presented as the software realisation of the
standard (§9.2) and not as a contribution in itself.

## Major comment 3 — the estimand is incomplete and "value" is overstated

**Granted.** The quantity is renamed **incremental predictive performance**
throughout, and the manuscript says in §1 and again in §11 that it does not
measure acquisition cost, maintenance cost, intervention effectiveness,
downstream routing improvement, or organisational review costs.

The estimand of Equation (1) is the one the referee wrote, with $s$ naming
learner, encoding, target, split, availability, quality mechanism, baseline,
metric and operating point. The register population is no longer hidden inside
$f$: it is one level of the quality axis $q$, which also carries accuracy,
reconciliation and discovery mechanisms.

## Major comment 4 — the literature audit cannot support the field-wide claim

**Granted, on every one of the eighteen points.** The referee offered two
dispositions and we take the second while doing as much of the first as one
author honestly can.

The audit is now a **pilot** (§9.3, Appendix F), and:

* the frame is larger and stratified, with declared allocation and design
  weights, and the enumeration is cached and reproducible;
* **a random sample of the papers the screen rejected was adjudicated**, so
  the screen's misses are counted rather than assumed away. This is the single
  most important change: it converts "we found none" into a measurable
  sensitivity;
* the screen's measured sensitivity is reported, and it is poor. The
  "not one of twenty" claim of the previous version is **withdrawn** (C15):
  it was a property of a coder that finds fewer than half of the eligible
  papers, and the pilot now finds eligible papers that do report the increment
  across a range of operating points;
* denominators are applicability-specific: the register-population code is
  reported over the papers whose incremental feature is a register lookup;
* missing full text is bounded rather than ignored;
* the flow is PRISMA-style, with every exclusion reason;
* a sample-size calculation states what the design can resolve, and it is
  the pilot's binding limitation;
* the adjudication is machine-assisted with one adjudicator, every judgement
  is made from a committed evidence dossier, and the manuscript says plainly
  that this is transparency and not independence.

**No claim in the manuscript depends on the pilot.** The paper's argument is
carried by the surface, the decomposition and the regret benchmark.

## Major comment 5 — the ratio $R$ is unstable and read as a proportion

**Granted.** Three changes:

1. The **absolute increments and the absolute absorption
   $D = V(f\mid B_0) - V(f\mid B_1)$ are primary** everywhere (§3.3, Table 8).
2. $R$ is secondary, is reported only where the denominator is resolvably
   positive *under the simultaneous band*, and carries a **Fieller set** whose
   *kind* — bounded, unbounded, or the complement of an interval — is printed
   beside it (§4.5). The manuscript reports how many of its reductions have a
   non-bounded set; a percentile interval reports a bounded interval for every
   one of them, which is the referee's objection made concrete.
3. The magnitude of $R$ is nowhere compared with the spread of $R$ across
   metrics.

## Major comment 6 — the formal propositions are not established as written

**Granted on all three.**

* **Proposition 1** is restated as **metric non-identifiability**, not
  unboundedness; the average-precision convention and the tie rule are stated
  and the construction's dependence on them is acknowledged; the construction
  is exhibited in integers so the AUC reduction is exactly zero rather than
  approximately so.
* **Proposition 2** now pins down the transformation (common to all four score
  vectors), the object claimed invariant, the nonzero-denominator condition,
  and the quantifiers. The necessity direction is **existential**, and
  Remark 2 exhibits a cancelling configuration on which a non-rank-based
  metric leaves $R$ invariant — which is why the universal reading is false.
  The previous version asserted it; that is correction C13.
* **Proposition 3 is no longer a proposition.** It is Computational Result 1,
  its tolerance sweep is printed in full, and the manuscript states that
  failing to find a witness is not evidence of dependence and that finding one
  in a finite family is not a theorem. The search itself had a defect — it
  drew fresh noise inside each cell evaluation — and that is correction C16.

## Major comment 7 — the knowledge reference may be post-decision information

**Granted, and this is the change we think most improves the paper.** We do
not have a timestamped field-value history and cannot obtain one. So the
manuscript takes the referee's third option:

* **two decision times** are defined, $\tau_1$ at interaction opening and
  $\tau_2$ at incident creation, and a surface is estimated for each (§7.1);
* what the interaction file establishes and what it does not is tabulated
  item by item (§7.2), including that only five interactions were formally
  closed before their incident was opened, that elapsed handling time is not a
  field-value history, and that a base AUC of 0.8 from one field is a reason
  for suspicion;
* a **leakage tipping-point curve** (§7.3) reports the increment as a function
  of the share $\lambda$ of references assumed post-hoc, so a reader can place
  their own belief on it rather than accepting ours;
* the availability rule is an **axis of the estimand**, not a preliminary
  decision.

Neither surface is used to retire a claim the other supports.

## Major comment 8 — statistical inference is inadequate

**Granted.** Every interval in the manuscript is new:

* a **nested moving-block bootstrap** that resamples the training half in
  blocks, **refits the entire pipeline** — encoders, frequency tables, target
  encodings, register rankings, calibrators — and evaluates on a moving-block
  resample of the test half (§4.2);
* **rolling-origin validation** as an axis, reported per fold (Appendix E);
* **simultaneous max-$t$ bands** over two declared families, so the harmful
  band of §8.2 is a family statement with family-wise coverage (§4.3);
* **five pre-specified confirmatory contrasts** with Holm correction, and
  everything else labelled exploratory (§4.4);
* a **rebuilt simulation** (§4.9, §6.6): six worlds including misspecified,
  drifting, sparse, imbalanced and noisy, with an exactly enumerated truth,
  and many more replicates. The 85% coverage the previous version dismissed is
  now decomposed: the manuscript separates the estimator's own limit from the
  oracle quantity, reports coverage of each, and states that under
  misspecification no amount of resampling makes an interval around the first
  an interval around the second.

## Major comment 9 — external validation is selected and heterogeneous

**Granted.** The surface is computed on **every log--target pair the
pre-registered rules admit**, not on the ones whose reduction resolves.
Selected reporting was the defect and it is removed at the source: the pair
list is read from the registered ladder's own admission output.

The manuscript also **reframes** the multi-log analysis, exactly as the
referee suggested: it is a *benchmark of specification sensitivity across
heterogeneous prediction problems*, not a replication of one finding on three
organisations. §5.4 states plainly that the registers, free fields and targets
mean different things across the corpus, and the results are not averaged
across pairs.

The prospective-prediction exercise of the previous version, whose positive
half was untested, is not part of this manuscript's argument.

## Major comment 10 — the population axis does not model register quality

**Granted.** The population axis is replaced by a **register-quality axis**
with six mechanisms besides the clean field: coverage loss with the long tail
absent, with the core absent, and at random; identity error; reconciliation
failure (one identity existing as two); and staleness (an identity present
only if the register had seen it before the split). Frequency rankings and
corruption alphabets are computed from the training half alone, stochastic
mechanisms are averaged over seeds, and the train-only property is **verified
by execution**: perturbing the test half and re-degrading must leave the
training half's degraded values identical.

We agree that this is still synthetic and that a register degrades in ways
correlated with the outcome. §11 says so and names validation against a
genuinely incomplete register as the next study.

---

## Presentation, structure and compliance

* **Structure** follows the referee's recommended outline. The literature
  pilot, the correction history, protocol amendments, extended results, all
  threshold tables, the checker architecture and the proof details are in
  supplements.
* **Length**: the main text is within the range the referee asked for; the
  previous version's 26,755 words and twelve correction narratives are not
  carried forward.
* **Deleted**: sentences beginning "A referee is entitled to…", "A reader may
  object…", "We report rather than hide…", "This is correction number…". The
  correction register survives in Appendix C, grouped by class.
* **Abstract** 250 words or fewer; **keywords** seven; **highlights** five,
  each within 85 characters, checked by a script rather than by hand.
* **Statements**: CRediT, competing interests, funding, data availability,
  code availability, and a **generative-AI declaration that says precisely
  what was machine-assisted** — the software, the pilot's adjudication, and
  the drafting — rather than the word "machine-assisted" alone.
* **Bibliography** carries no commentary; the annotations the referee quoted
  are gone.
* **Figure 1** is replaced. It is now a specification curve: one point per
  admissible cell, sorted, with a panel showing which axis level each cell
  occupies. It is readable at print size, which the previous Figure 1 was not.
* **Archive**: a frozen release with a DOI, a lockfile and a container, and a
  one-command reproduction.

---

## What we did not do, and why

* **We did not obtain an organisational partner** with timestamped field
  histories, historical register population and accuracy, and operational
  review costs. That study would be better and we cannot run it. The
  manuscript is framed as a benchmark case in consequence, and says so in §1,
  §7 and §11.
* **We did not rebuild the audit as a systematic review** with two independent
  human raters and 150–200 manually confirmed in-scope papers. One author
  cannot supply a second independent human rater. We took the referee's
  alternative — a clearly labelled pilot — and spent the effort instead on
  measuring the coder's error rate, which is what makes the pilot's numbers
  interpretable at all.
* **We did not remove the CMDB case study.** It is now one case among the
  admitted pairs, reported at greater length because it is where the
  availability axis decides the answer, and it no longer leads the paper.

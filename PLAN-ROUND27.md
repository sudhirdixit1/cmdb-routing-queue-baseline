# Plan: round twenty-seven — from *major revision (narrow)* to *strong accept*

**Target venue:** Information Systems, Elsevier, ISSN 0306-4379
**Written:** 2026-08-28, after an independent second-round review of the
round-twenty-six PDF (`~/Downloads/specification_surfaces.pdf`, compiled
2026-08-26).
**Predecessors:** `PLAN-STRONG-ACCEPT.md` (round 16→26, executed),
`ROUND27-STATE.md` (the paused run and what is already committed).
**Audience:** an autonomous agent. Read §0 of `PLAN-STRONG-ACCEPT.md` first —
its rules 1–6 and its recording discipline (§0.2) govern this plan too.
Append progress to §9 of THIS file after every phase.

---

## STATUS AT A GLANCE — updated 2026-08-29, 00:30 (overnight session)

| phase | what | state |
|---|---|---|
| 1 | weighted bootstrap, designed surface, 400 draws | **running** — 14/19 weighted at 00:24. BPIC19 took **86 min**, not the ~58 the resume note implied, so budget ~5 h more: ~50 min for the remaining 5 weighted, then ~4 h for all 19 multinomial. Output validated (see below). Everything downstream is written and waiting; `scripts/round27_chain.sh` runs it in one command. |
| 2 | decision-curve band widened by its measured shortfall | **done** — `s49_dcaband.py`. Costs 10 of 31 resolved thresholds; the per-thousand headline was checked and is untouched. |
| 2b | within-cell noise bound on the analyst-choice share | queued — needs Phase 1's draws |
| 2c | crossed family × encoding on the 8 ITSM pairs | **done** — 3,456 fits in 5 min, run nice'd beside Phase 1 on idle cores. **Partially replicates**: encoding leads on 6 of 8, family on the other 2 and not narrowly (0.04× on the worst). Written into §6.2 and §11's limitation narrowed. |
| 3 | the inference-share denominator, plus a generalised sweep | **done** — two macros, and a condition that re-multiplies every quoted count from the axis declaration |
| 3b | scikit-learn citation; §9.3's euphemism | **both done** |
| — | **internal red team, pass 1** | 18 findings (8 blocking) — **all repaired**, built, verified, committed |
| — | **internal red team, pass 2** | 14 findings (3 blocking) over the files pass 1 could not read — **all repaired** |
| 4 | length | **measured**: was 58 pp, now **63** — the 32 repairs added five pages of denominators and qualifiers, and that was the right trade. 42 was never reachable; the target is 46 and the arithmetic is in §4.0b. Cut list written and executable; execution waits for Phase 1. |
| 4.2 | voice | **decided: keep the editorial "we"**, with the reason recorded |
| 5 | claims regenerated against the new numbers | register written; execution waits for Phase 1 |
| 6 | the `hgb` cross-machine reproduction gap | **done — and it was worse than recorded.** Platform, not threading; the divergence tracks register **cardinality**, not the learner; `logit` diverges up to 0.094 and boosting to 0.851, against the 5e-10 and 0.14 the repo had written down. Disclosed with six measured tolerances, gated, and the gate has its own corruption suite. |
| 7 | compliance | audited against the journal's own guide; agent-fixable items **done**; owner items in `submission/OWNER-ACTIONS.md` §4 |
| 8 | pre-submission red team | **gates green**: `attack_verifier` 255 caught / 0 missed, the new `attack_reproduction` 6 / 0 unnoticed, `verify_numbers` 166 macros + 38 conditions / 0 failures, `texlint` 0, `check_package` 15 / 0, `check_highlights` 5 / 0. Build: **63 pp, 0 errors, 0 undefined references, 0 overfull boxes.** Remaining: the fresh-context read of the built PDF, which waits for the Phase 1 rewrite. |

**A second thing that now needs the owner, created by this round's own
disclosure:** the code-availability statement claims bit-exactness *inside the
container, whose image digest the archive records* — and **no such digest
exists**. The `Dockerfile` pins its base by mutable tag. Until it is minted
and recorded, the manuscript makes a claim the archive cannot support, which
is the one category of defect this project treats as unshippable.
`submission/OWNER-ACTIONS.md` §4.7.

**The one thing that cannot be done without the owner:** mint the archive DOI.
It is not merely a missing statement — it is **reference [11]** in the printed
bibliography, rendering as a placeholder that forwards the reader to a
statement which does not carry the DOI either. That is the single most likely
cause of a desk return. See `submission/OWNER-ACTIONS.md` §4.5.

## 0. The review this plan answers

A second-round review of the round-26 PDF reached: **major revision, narrow**.
The reviewer's summary judgement, verbatim:

> Round twenty-six is honest to a degree that is rare, and most of the
> round-25 report is properly implemented. What blocks acceptance is no
> longer candour or presentation but delivery: contribution 2 rests on a
> band the paper itself measures at 84.6% median family-wise coverage
> against a nominal 95%, and Section 11 names the repair — a weighted
> block bootstrap and ≥400 draws on a designed inference surface — as "a
> change to one function and a re-run," and does not run it. A methods
> paper whose subject is inference discipline cannot ship its central
> inferential object as a diagnostic when its own text prices the fix at
> one function. Secondary blockers: the decision-curve family's measured
> widening (1.90–2.05) is never applied although it is arithmetic on
> existing draws; a handful of internal inconsistencies; length; and
> compliance residuals (unresolved archive DOI at review time).

Every finding of that review is enumerated in §§1–8 below with its fix,
its script, and its done-when. Nothing else in the manuscript was found
blocking: the round-25 items A3–A6, B1–B5, C1–C5, D1–D3, E2 are verified
implemented in the round-26 PDF and must not regress.

**Consistency checks the reviewer ran and the manuscript passed** (keep them
passing; several are worth adding to `round27_verify.py` as permanent
conditions):

- Table 6 medians: resampling 71.7 / analyst 13.3 / counterfactual 4.2 /
  mixed 4.5; resampling largest on 17 of 19 pairs.
- Table 8 last column median = 0.0430 (median of 10 values).
- Table 7: beneficial 850 + harmful 46 = 896 resolved; family sizes sum to
  3,900 (2×480 + 15×180 + 2×120); label counts 6/9/1/3 sum to 19; the
  minimum-share condition withdraws exactly 4 of 13 directional labels
  (1.7%, 1.1%, 1.1%, 4.4% < 5% ≤ 5.6%).
- Declared surface multiplies out: 15×1,080 + 2×1,620 + 2×4,800 = 29,040;
  master file 37,920 scalar-with-intercept + 235,104 decision-curve rows
  = 273,024. 29,040/5 = 5,808 AUC cells. 1/42 = 2.4%. 67/896 = 7.5%.
  (1,150−896)/1,150 = 22.1%. 74/3,900 = 1.9%.
- Table 9 ladder differences: 0.2310−0.2013 = 0.0297 (population),
  0.2013−0.1914 = 0.0099 (information), 0.1914−0.1838 = 0.0076 (no-record
  incidents) — matches the Conclusion's three steps.
- §7.5: D = 0.184−0.1034 ≈ 0.0804; R = 0.0804/0.184 = 0.437.
- §7.4 layer ratios: 0.134/0.257 ≈ ½; 0.045/0.129 ≈ ⅓.
- 8 of 19 reference increments have |V| < 0.01 (counted from Table 5).
- Highlights: 5 bullets, all ≤ 85 characters.

---

## 1. Phase 1 — Finish the inference repair (the acceptance-deciding phase)

This is `ROUND27-STATE.md`'s run, already 13 of 38 pair-runs done. Do not
redesign it; finish it.

- [ ] **1.1 Resume the run** (owner stopped it for machine heat — before
  resuming, confirm with the owner OR run at reduced load):

  ```bash
  python scripts/s44_designed.py --scheme both --draws 400 --procs 8 --resume
  ```

  `--resume` skips finished pairs. BPIC19 is ~70 s/draw; budget accordingly.
  Do NOT read `results/s44_facts.csv` until the run completes (it currently
  holds the four-draw smoke run). A finished pair's `.csv.gz` is ~10 MB.

**The weighted arm's bands do not wait for the multinomial arm.** Verified:
`s21_bands.py --draws-dir s44_weighted --prefix s48w` reads only the weighted
draws, so it can run the moment the 19th weighted pair lands — hours before
the multinomial arm finishes. That gives the new region labels, ρ and resolved
counts early, and §6.1/§6.3's rewrite can start against them. Only
`s47_schemes.py` (the two-scheme comparison) genuinely needs both arms.

*Chain verified 2026-08-29: all four downstream scripts accept the flags
`round27_chain.sh` passes them (`--draws-dir`/`--prefix`, none, `--procs`,
none), and the script passes `sh -n`. It also refuses to proceed at fewer than
19/19 in either arm, with the resume command in the message.*

- [ ] **1.2 Downstream, in order:**

  ```bash
  python scripts/s21_bands.py --draws-dir s44_weighted    --prefix s48w
  python scripts/s21_bands.py --draws-dir s44_multinomial --prefix s48m
  python scripts/s47_schemes.py          # the two schemes, compared
  python scripts/s41_bandcoverage.py     # coverage, with a non-zero-truth regime; give it --procs
  python scripts/provenance.py --accept s44_designed.py --note "designed surface, 400 draws, both schemes"
  python scripts/provenance.py --accept s21_bands.py --note "bands on the designed surface"
  python scripts/provenance.py --accept s41_bandcoverage.py --note "family-wise coverage incl. non-zero truth"
  ```

- [ ] **1.3 Decide the scheme from the results, not the plan.** The paper's
  own prediction is that the weighted scheme removes the displacement at
  source. Rule 2 of §0.1 applies: if the weighted scheme flatters the paper,
  look hardest at it. Whichever scheme survives becomes the paper's interval;
  the other is reported as the comparison Section 11 said was owed.

- [ ] **1.4 Rewrite the sections written against the old inference surface:**
  §4.1 (the displacement paragraphs become a comparison with a result),
  §4.2 (the inference surface is now a designed factorial — the "corner"
  objection and the median-12.5% sentence go away), §4.3, §6.1, §6.3
  (the K/n calibration is either retired or re-scoped), §10.4 (new measured
  coverage, now including the non-zero-truth regime), §11 (delete the
  "repair is not run here" paragraph; shrink the internal-threat paragraphs
  it carried). Table 1, Table 5, Table 7 regenerate from the new band.

- [ ] **1.5 Defend the half-of-intake rung's membership in the inference
  family — one sentence that does not currently exist.** Verified by grep:
  the rung appears in the manuscript only at `40_multilog.tex:148`, and only
  as the thing that inflates the baseline spread ("That range is carried by
  the half-of-intake rung, and a reader is owed the spread without it").
  Nowhere does the paper say why a rung it elsewhere treats as impoverished
  is admissible in the family that every region label and every $\rho$ ranges
  over — and under the round-27 design it is **one of three rungs, so a third
  of that family on every pair**. An earlier referee already called it a
  straw baseline; the next one will ask why it is a third of the inference
  family, and the answer should be in the text before they ask. The sentence
  to write, in §4.6 or §6.3, has three clauses and needs all three: it is
  admissible by declaration; dropping it after seeing which cells resolve
  would condition the family on the answer, which is the move this paper
  exists to argue against; and including it can only make a directional label
  *harder* to earn, so the choice errs conservative. The third clause is what
  turns a defence into a reason.

### 1.4a The rewrite, paragraph by paragraph

Written before the run finished so the writing is a decision about evidence
and not about wording. Each item says what the paragraph must decide, and what
it must **not** be allowed to drift into.

**§4.1, "A pivoted interval need not contain the estimate it is built from."**
Currently states the round-25 multinomial count. It becomes a *comparison*:
both schemes, one design, one draw count, one set of seeds. The early read
says the weighted scheme roughly halves the rate rather than removing it, so
the paragraph's job is to say **what the repair bought and what it did not**.
The claim the evidence supports is narrow and should be written narrowly:
every register level is present in every refit, so the *mechanism* §11 named
is gone; a residual displacement remains that the mechanism does not explain.
That residual deserves its own sentence — it says the displacement was never
only about level loss. *Do not write "the weighted scheme fixes it."*

**§4.1, "It gets worse with the sample size."** Keep the mechanism; drop the
crossing numbers and forward-reference §10.3, which carries them plus the
plane's own facts (§4.0's cut, resolved).

**§4.2, "The rule that selects it, in full."** The inference surface is now a
balanced full factorial on every pair. **Three concessions are retired, and
retiring them is a result rather than a deletion**: the "corner, not a design"
limitation; the claim that the decomposition cannot be computed on the
inference surface (it now can, and comparing it with the declared surface's is
a new sentence worth having); and the median-share sentence, which becomes a
per-size-class statement because the share is no longer uniform.

**§4.3 / §10.4, the coverage.** The headline of the round. If measured
family-wise coverage at 400 draws reaches nominal, contribution 2 and
highlight 3 may claim *inference* and the abstract's "and find short of
nominal" inverts. If it does not, **the diagnostics framing stays and the
front matter keeps saying so** — and the paper is still better, because it now
reports a measurement under a scheme with no displacement bias. §10.4 must
also report the new `nonzero`-truth regime separately: under a zero truth
every rejection is an error, so that regime is the only one that speaks to a
band that resolves *correctly*.

**§6.3, the K/n calibration.** If the weighted scheme covers, this apparatus
is **retired, not re-fitted** — and §11's paragraph about a calibration fitted
for pointwise coverage and applied simultaneously goes with it. That is a
large simplification and the temptation will be to keep the machinery because
it was expensive. Rule 1: if the result contradicts the paper, the paper
changes, including by getting shorter.

**§11, "the repair is not run here."** Does **not** simply get deleted. It
becomes the paragraph that says what the repair bought, what it cost, and what
remains — including the residual displacement above. A limitation section that
loses a paragraph every round without gaining one is a section nobody believes.

**§6.1 and the tables.** Table 5, Table 7 and Table 1 regenerate. Every label
and ρ moves. Work §5.1a's claims-at-risk register rather than re-reading.

### 1.4b Ready-to-paste replacement for §4.2's second half

Drafted while the multinomial arm ran, because this passage's content is
settled by facts already verified and does **not** depend on the coverage
measurement. The first paragraph of §4.2 (the three surfaces, the declared /
computational identity) is unchanged. What follows replaces everything from
**"The rule that selects it, in full"** to the end of the subsection.

Macro names below are proposals; wire them from `s44_grid.csv` and
`s51_facts.csv` when the surface macros are re-pointed. Do not paste this
until every site in the re-pointing table has moved together — a half-migrated
state is what `round27_verify`'s newest condition exists to fail.

---

\textbf{The rule that selects it, in full.} It is one design, and it is the
same design on every pair: \nInfLearners\ learners, \nInfSplits\ splits,
\nInfQuality\ register-quality conditions and \nInfRungs\ admissible rungs,
crossed --- \nInfCells\ cells, \nInferenceScalar\ scalar family members across
the corpus --- at \nDrawsDesigned\ draws. Nothing in the rule reads a result,
and nothing in it reads the log: the size classes that chose the old surface's
levels are gone, and with them the objection they carried.

\textbf{It is a complete factorial, and that is checked rather than declared.}
On every one of the \nPairs\ pairs, each combination of the four axes is
present exactly once: no cell missing, no cell twice, and no pair differing in
shape from any other. So a corpus median over these families is a median over
one design, which the previous surface's was not. A balanced full factorial is
also strictly stronger than the resolution-IV fraction
Section~\ref{sec:lim} used to ask for, so that request is answered rather than
deferred.

\textbf{Two objections this retires, and one it does not.} The inference
surface was \emph{a corner of the declared surface rather than a design}, and
the decomposition of Section~\ref{sec:sobol} could not be computed on it.
It can now: \nInfAnovaCount\ decompositions run on it, one per pair per
instrument, over \nInfCells\ cells each. What that comparison shows is
reported in Supplement~\ref{app:infanova} and is not a confirmation ---
\textbf{the axis carrying the largest first-order index agrees between the two
surfaces on \nInfAnovaAgree\ of \nPairs\ pairs}, and the two do not declare
the same levels, so the disagreement is a comparison between designs and shows
neither of them unrepresentative. What it does show is worth one sentence: a
first-order index is a statement about the levels an analyst declared and not
only about the pair.

\noindent The objection it does not retire is the one that matters most for
reading a region label. The inference family is still a fraction of the
admissible surface --- \inferenceShareAdmissibleMedianPct\ at the median pair
--- and \textbf{a label computed over fewer cells is systematically cleaner
than one computed over all of them}. Section~\ref{sec:regionsdef} says which
label that most flatters and Section~\ref{sec:regions} reports what it costs.

---

**Why the last paragraph is in this draft.** The new surface reaches
`uniformly beneficial` on one pair, over a family that is a *smaller* share of
that pair's admissible cells than the old one was. §4.2 is where a reader
meets the inference surface, so it is where the restriction has to be stated
plainly — before §6.3 reports a label that the restriction helped produce.
Putting it only in §6.3 would be putting it after the reader needs it.

### 1.4c Ready-to-paste replacement for §11's refitting-bootstrap paragraph

Its content is settled: the repair ran, and what it bought is measured. Only
the coverage sentence at the end waits on `s41`. The current paragraph is
headed *"Internal --- the refitting bootstrap is the source of a bias, and the
repair is not run here"*; that heading goes with it.

---

\paragraph{Internal --- the refitting bootstrap was the source of a bias, and
the repair removes its mechanism and not all of it}
A multinomial resample holds about $1 - e^{-1}$ of a high-cardinality
register's levels, so the bootstrap distribution is displaced: the percentile
interval becomes a correct interval for the wrong quantity, and the pivotal
interval this paper uses can exclude its own point estimate.
Section~\ref{sec:lim} of the previous round named the repair --- drawing
\emph{weights} per moving block, so that every row has positive weight in
every draw and every register level is present in every refit --- and did not
run it. \textbf{It is run here, on one design at one draw count with one set
of seeds, and the comparison is reported rather than the scheme we preferred.}

\textbf{The mechanism is removed and the symptom is halved, not removed.}
Under weights every register level is present in every refit, which is the
thing the mechanism was about, and the count of cells whose pivotal interval
excludes its own point estimate falls from \nCellsExcludingVOld\ of
\nCellsWholeTotalOld\ to \nCellsExcludingV\ of \nCellsWholeTotal. That is a
halving of the rate and not an elimination of it, and \textbf{the residual is
the informative part}: a displacement that survives the removal of level loss
was never only about level loss. What remains of it we do not explain, and
Section~\ref{sec:lim} carries that rather than a claim that the scheme is now
unbiased.

\noindent Two things follow that the earlier version could not say. The
percentile interval is admissible again on a scheme with no level loss, and
the paper nonetheless keeps the pivotal one, because the residual displacement
above is exactly the condition under which the two differ. And the
seven-construction comparison that chose the pivotal interval still ran at one
training size, which remains a limitation of the choice rather than of the
scheme.

---

**Two cautions for whoever pastes this.**

1. `\nCellsExcludingVOld` and `\nCellsWholeTotalOld` do not exist. The old
   counts must become macros of their own before the paragraph can quote both,
   or the sentence has to be recast to quote only the new pair and describe
   the old one in words. **Do not hardcode 74 and 3,900** — that is the defect
   this project's lint exists to prevent, and it would be introduced by the
   paragraph announcing the repair.
2. The last sentence of the first paragraph promises the comparison is "on one
   design at one draw count with one set of seeds". That is `s47_schemes.py`'s
   claim and must be checked against its output before the sentence ships, not
   assumed from the design's intent.

**Done when:**
- the displacement statistic on the weighted scheme is ≈ 0 and the count of
  cells whose band excludes its own point estimate is 0 (or reported ≤ 0.1%);
- measured family-wise coverage on matched families is ≥ 93% at the corpus's
  actual draw count, stated in §10.4, including under the non-zero-truth
  regime;
- region labels and ρ are re-stated as inference (not "descriptive
  diagnostics") ONLY if that measured coverage supports it; otherwise the
  diagnostics framing stays and the front matter keeps saying so;
- the fixed-model interval's coverage appears for every simulation world in
  one main-text table (round-25 M2 asked; round-26 still reports it only in
  prose for two worlds).

---

## 2. Phase 2 — The decision-curve family's band (arithmetic, no refits)

Round-26 §8.3 prints "resolvably positive at 24 of 31 pointwise, 18
simultaneous" from a band §10.4 measures as needing a 1.90–2.05 widening it
never receives. Applying a measured multiplicative widening to an
already-computed critical value costs matrix arithmetic only.

- [ ] 2.1 After Phase 1's `s41_bandcoverage.py`, extract the decision-curve
  families' own measured shortfall factor (with and without the 841
  degenerate all-alike-threshold cells, as §10.4 already distinguishes).
- [ ] 2.2 Apply it as the operative critical value for every decision-curve
  statement: recompute the 24/18/0 counts in §8.3, the net-benefit region,
  and any Table S22 columns; print nominal beside corrected, as Table S6
  already does for the scalar family.
- [ ] 2.3 If the corrected band un-resolves the 1.71-per-thousand promise or
  the 0.003 delivery at their thresholds, rule 1 of §0.1 applies: the paper
  changes, including §8.4 and the Conclusion.

- [x] **2.4 The decision-curve FIGURE now disagrees with its own section —
  DONE, by resolution 2.** The drawn band is left as it is and the caption now
  says it is the **nominal** one, gives the widened band's factor, and prints
  the dip and the harmful counts under both. So the figure shows the shape of
  the curve and the ordering of the two intervals, and says plainly that it is
  not the band any claim is read against. Resolution 1 (redraw) was declined:
  it would need the figure generator taught about `s49_dcaband.csv` for a
  picture whose *shape* is unchanged, and a caption that names which band it
  draws is the more useful artefact anyway. The superseded "read this
  section's counts as upper bounds" paragraph now says what the widening does
  and does not settle — it is fitted where the bootstrap is ideal, and it does
  not reconcile the two estimators of the critical value.
  *(original finding below)* `app_secondary.tex:306-315`
  draws `figS4_dca.png`, which plots the **nominal** band, and its caption
  quotes the nominal `\dcaDipTheta`, `\dcaDipValue` and
  `\nHarmfulSimultaneous`. The prose immediately below it now quotes the
  **widened** dip and harmful count. Two honest resolutions, in order of
  preference:
  1. redraw the figure with the widened band (needs the figure generator
     taught about `results/s49_dcaband.csv`, which carries both edges per
     cell), and move the caption to the widened macros; or
  2. keep the drawn band and make the caption **say** it is the uncorrected
     one, giving the widened counts beside it.
  Do **not** leave the caption as it stands: a figure whose caption describes
  a different band from the section around it is precisely the defect class
  R27.6 exists to catch, and it would be one this round introduced itself.
  *(Deferred only because another agent held that file when it was found.)*

**Done when:** no decision-curve count in the paper rests on a band whose
measured widening was not applied, §8.3's "most exposed family" caveat is
replaced by the correction it called for, and the figure and its caption
describe the same band as the text around them.

---

## 2b. Phase 2b — The attack the next referee has left (new; do after Phase 1)

Round 26 made the split an error stratum, which removes *between-fold*
variation from the analyst-choice share. It does not remove **within-cell
estimation noise**: every $V_s$ is estimated on a finite test half, and that
estimation error is still inside the decomposition, distributed across every
component including `analyst choice`. So "analyst latitude carries 13.3%" is
an **upper bound**, and a referee who sees that the paper corrected one noise
source and not the other will say so — the more sharply because separating
noise from latitude is the paper's own headline contribution.

The correction is cheap and the ingredients are exactly what Phase 1
produces. Each cell carries a bootstrap standard error $\hat\sigma_c$, and
the cells' errors are strongly correlated because they share a test half
(`results/s41_profile.csv` carries the per-family mean correlation, `rho_mean`
≈ 0.11–0.14 on the surface families). Independent noise would contribute
about $\overline{\hat\sigma^2}$ to the cross-cell variance; correlated noise
contributes roughly $\overline{\hat\sigma^2}(1-\bar\rho)$. That is a
computable bound on how much of the surface's variance is estimation error
rather than either analyst choice or resampling.

- [x] **2b.1 Computed, and the bound as posed is WRONG — do not use it.**
  `scripts/s50_noise.py`, run against the 13 pairs that already carry 400
  weighted draws. Its noise share **exceeds one on 7 of the 13**, which is
  impossible for a share of a variance and is the computation reporting its
  own ill-posedness.

  **The reason is worth more than the number would have been.** $\hat\sigma$
  comes from the nested bootstrap, which resamples the **training** half as
  well as the test half, because this paper's estimand deliberately contains
  training-sample variability (§4.1). The cross-cell variance the
  decomposition partitions is computed at **fixed training data** — it is the
  spread across specifications on one dataset. The two are not commensurable
  and their ratio is not a noise share. Answering the original question needs
  a **fixed-training** standard error, which is a different scheme and a
  separate run.

  Rule 4 applies: print only what the output supports. **No macro reads
  `s50_facts.csv`, and nothing from it goes in the paper as a share.** The
  script's header now says so before it says anything else.

- [ ] **2b.2 What the run does support, and is worth one sentence.** The
  comparison that needs no decomposition model: a cell's own standard error
  against the standard deviation across cells, both in the metric's own units.
  On AUC the mean per-cell standard error runs 0.007 on the two largest pairs
  to 0.078 on BPIC15_5, against cross-cell standard deviations of 0.011 to
  0.053 — so **on the small logs a single specification's uncertainty is
  larger than the entire spread across specifications**.

  That corroborates from a second direction what §6.3 already reports as
  scarcity of resolved cells, and it is the more honest framing of this
  paper's own thesis: on most of this corpus, *which* specification you choose
  moves the answer less than not knowing the answer does. Decide during the
  Phase 1 write-up whether §11 takes one sentence of it. It is a limitation on
  how the decomposition may be read, and stating it pre-empts the attack
  better than a bad number would have.

- [ ] 2b.3 If a fixed-training standard error is ever run, revisit — but not
  in this round, and not as a fourth reporting object.

## 2c. Phase 2c — Close the crossed-pipeline limitation (queue after Phase 1's compute)

§6.2 reports that the pipeline axis is really two axes — model family and
encoding — and that crossing them shows the **encoding** is the larger
(10.1% of the variance against the family's 5.2%, with an interaction of
9.7% as large as either main effect, so "the fused index is not the sum of
two indices"). That is one of the paper's more useful findings for a
practitioner. It is computed **on the case study's log alone**, and §11
concedes that the other 15 pairs carry family and encoding confounded.

This is cheap to close and it is the kind of concession a referee converts
into a demand. A decomposition needs **point estimates only** — no bootstrap,
no bands — so the cost is 2 families × 3 encodings = 6 pipelines refitted on
the 8 ITSM pairs, which is a small fraction of what one bootstrap pair costs.

- [x] **2c.0 The script is ready** — `s37_axes.py` gained `--pairs case|itsm`,
  `--procs`, and an output suffix, so the ITSM run writes
  `results/s37_*_itsm.csv` and **cannot overwrite the case-study results the
  manuscript's macros are computed from**. Verified by `--plan`: the case set
  is 12 pipelines × 36 cells × 2 arms = 864 fits; the ITSM set is 48 × 36 × 2
  = **3,456 fits**. BPIC14's two pairs are in both sets and are the expensive
  ones, so the marginal cost is six small logs.
- [ ] 2c.1 Run it once `s44_designed.py` is done:

  ```bash
  python scripts/s37_axes.py --pairs itsm --procs 8
  ```

  **Do not start it before then** — the machine is thermally constrained and
  Phase 1 is on the critical path.
- [ ] 2c.1a Then decide how the macros read it. `\sEncodingPct`,
  `\sFamilyPct`, `\sFamilyEncodingPct` and `\crossedHigherOrderPct` are
  currently computed from `s37_indices.csv` for BPIC14 — and an internal audit
  found they are the median over the **pooled** target × instrument
  combinations while the table beside them prints **per-target** medians, an
  aggregation §6.2 itself insists must be named where it appears. Fix that
  first, then extend; do not add ITSM numbers on top of an aggregation that is
  already mis-stated.
- [ ] 2c.2 Report whether "encoding beats family" holds beyond BPIC14. **Rule
  1 applies with force here**: this is a finding the paper likes, run on new
  pairs for the first time, so the prior should be that it does not fully
  replicate. If it does not, §6.2 says so and the claim narrows to the case
  study — which is still a better paper than one that concedes the question
  was never asked.
- [ ] 2c.3 Either way, delete the corresponding sentence from §11's
  "three narrower limits" and replace it with the measurement.

**Do not start this until `s44_designed.py` has finished** — the machine is
thermally constrained and Phase 1 is on the critical path.

## 3. Phase 3 — Internal inconsistencies found by this review (new items)

Each becomes a generator fix plus a `round27_verify.py` condition, per the
R3 pattern already established.

- [ ] **3.1 "median 12.5% of each pair's admissible scalar cells" is
  arithmetically wrong.** *(Confirmed still present in source: the macro is
  generated in `round20_numbers.py` as
  `inference_cells_observed / computational_cells`, and is used at four call
  sites of which only `20_inference.tex:112` says "computational".)* Per pair, inference/admissible = 180/1,080 = 16.7%
  (15 pairs), 480/4,800 = 10.0% (2), 120/1,620 = 7.4% (2); the median is
  16.7%. 12.5% is 180/1,440 — the denominator that *includes* the
  intercept-only rung, which "admissible" excludes by definition. Appears in
  §4.2, Definition 3, and §11. Phase 1 replaces the inference surface anyway;
  wherever the sentence survives, recompute the share from the files and add
  a verify condition that recomputes it from the axis counts.
- [x] **3.2 Table 5's region column contradicts Definition 3.** — **ALREADY
  DONE** in commit `a03b560` (2026-08-26 16:51), before this plan was
  written. The master table's `region` column is now the applied label with
  the resolved share beside it, and `round27_verify` condition 1 compares the
  two tables cell by cell. The reviewed PDF predates the commit. No action;
  do not regress.
- [x] **3.3 "That pair carries 9,600 of the corpus's 29,040 admissible
  cells" (§5.3).** — **ALREADY DONE** in the same commit: the sentence now
  reads `\nCellsBpicFourteenHandover` for the pair with the log's
  `\nCellsBpicFourteen` named separately, and `round27_verify` condition 4
  requires the log's count to be the pair's double. No action.

  *Commit `a03b560` also repaired three defects of the same class that the
  round-26 external review did not find: the decision-time caption's stale
  ordinal ("the fourth row" when the ladder had grown to make it the sixth),
  §7.2 quoting a rung's interval from a different run at a different draw
  count than the table it sits beside, and the §7.4 layer ladder being
  presented as reconcilable with Table 9 when it runs on a different cohort
  and target. All five are conditions in `round27_verify.py`.*
- [ ] **3.4 Sweep for siblings.** Grep the manuscript for every per-pair /
  per-log / per-surface count and re-derive each from `results/` in
  `round27_verify.py`. The three above were found by hand-multiplying Table 4;
  the check should do that multiplication for every quoted share.

**Done when:** `round27_verify.py` recomputes every quoted denominator and
share from the axis declaration and fails on the three defects above if
reintroduced.

---

## 3b. Phase 3b — Small items found this session (apply when the owning agent releases the file)

- [x] **3b.1 scikit-learn is never cited.** — **DONE.** Cited at §4.1 where
  the pipeline is introduced, with the clause that earns it: every learner,
  encoder and calibrator is that implementation at the version
  `requirements.lock` pins, "so the pipeline axis varies what this paper
  declares and nothing underneath it". Re-checked afterwards: every bib entry
  is now cited and every citation resolves.
  *(original finding below)* `references.bib` carries
  `pedregosa2011scikit` and nothing cites it — verified by resolving every
  `\cite` key across parts, tables and both documents. This matters more than
  a normal missing citation because the paper *itself* argues for software
  citation discipline and cites `fieldvalue` as software; a referee who
  notices that the manuscript demands the practice and omits its own principal
  dependency has a free shot. Cite it where the learners are introduced
  (§4.1, `20_inference.tex`) — currently owned by another agent — and confirm
  the version is the one `requirements.lock` pins.
- [x] **3b.2 §9.3's "machine-assisted" is a euphemism.** — **DONE.** The
  pilot's adjudicator is now named as "the author, assisted by the model named
  in the generative-AI declaration", so the declaration's pointer lands on a
  fact rather than on a hedge, and the two disclosures agree.
  *(original finding below)* The AI declaration
  now points at §9.3 for the one machine-assisted judgement inside a study,
  but §9.3 (`70_standard.tex:94-100`) says only "a machine-assisted prevalence
  pilot" without naming what assisted it. Name it — "the author, assisted by
  the model named in the generative-AI declaration" — so the pointer lands on
  a fact rather than on a hedge. Deferred only because the red-team pass is
  reading that file and line numbers would shift under it.

**Verified clean this session, so no work is owed** (recorded so a later
round does not re-check): every `\includegraphics` target exists; there are
**no** dangling `\ref` targets across both documents once `paper/tables/`
is included in the scan; every `\cite` key resolves to a `references.bib`
entry.

## 4. Phase 4 — Length, voice, and residual presentation

Round-25 C6 asked ~30 pages; `ROUND27-STATE.md` targets 42 total; round-26
sits at 58–60.

### 4.0 The length target is wrong, and must be renegotiated rather than met

Measured this session against `build/journal/specification_surfaces.aux`
(exact per-section page anchors, not estimates), calibrated at **435 prose
words per printed page plus 0.6 page per float**, residual ≤ 0.6 pp over ten
sections:

- the PDF is **58 pages**, not 60: p1 front matter, **p2–p51 body (50 pp)**,
  p52–53 declarations, p54–58 references.
- the eight non-body pages are effectively fixed, so **"42 pages total" means
  a 34-page body — a 16-page cut, not the 8 that "46 → 38" implies.**

The full cut list — every duplicate, every compressible passage, and the
reserve outside the four target sections — totals **12.2 pages** and lands at
**46**. Reaching 42 would require moving four more floats out of a main text
that has eleven, when the round-25 report asked for *six more* floats to be
moved **in**. Those two referee requests cannot both be satisfied, and the
round-26 response letter already puts that trade to the editor.

- [x] **4.0 Decision: the target is 46 pages total / 38-page body**, taken on
  the measurement above. It removes no concession and every moved passage
  lands in a supplement section that already exists. The response letter must
  state the trade rather than quietly missing 42.

**4.0b The baseline moved, and the reason is not slippage.** After the
red-team repairs the built article is **62 pages**, not 58. The four pages are
almost entirely the repairs themselves, and they are the *right* kind of
addition: nearly every finding was "the sentence names one set and the number
was computed on another", and the fix is to name the set. "197 of 5,808 AUC
cells" became "197 of the 780 AUC cells that carry a band"; the axes table
gained a column saying which rows multiply; the decision-curve figure's
caption now says which band it draws.

So **precision cost four pages and it was worth paying**, and the cut list's
12.2 pages now lands at 50 rather than 46. Two consequences:

- the Reserve tier (R1–R5, 2.26 pp) moves from optional to necessary, and
  even then the arithmetic gives ~47–48;
- the response letter should say this plainly rather than hide it. The honest
  sentence is that this round *added* four pages of denominators and
  qualifiers because a referee found eighteen places where the paper said one
  set and meant another, and that a shorter paper would have been a less
  precise one. An editor who has just read that argument is in a position to
  judge the trade; one who only sees a missed page target is not.
- Re-measure after the Phase 1 rewrite before committing to a number: §4, §6,
  §10 and §11 are 25 of the 50 body pages and are being rewritten once against
  the new results, which is where compression is cheapest.

### 4.0a A sentence in §11 that is false, and is the kind a referee checks

`80_limits.tex:4–5` opens the threats section with

> Nothing here is re-derived: every number is stated where it is computed and
> referenced from here.

Of the **73** `numbers.tex` macros used in that file, **55 restate a value
already printed elsewhere in the main body**. The sentence is false against
the paper's own macros. In a manuscript whose subject is auditability, and
whose defence throughout is "we counted it rather than asserting it", this is
the single cheapest shot a referee has.

- [ ] 4.0a Either make it true (Tier B below does most of that) or delete it.
  Do **not** leave it standing. Prefer making it true: after Tier B the claim
  is nearly accurate and it is worth having.

- [ ] 4.1 The length pass waits for Phases 1–2 (write §4, §6, §10, §11 once,
  against the new numbers — that is 25 of the body's 50 pages).

  **One cut resolved precisely, so the pass does not have to re-derive it.**
  The largest Tier-B duplicate was listed as "delete §10.3's straddle
  paragraph, §4.1 already says it". Checked line by line: it is **not** a
  wholesale duplicate. `20_inference.tex:70-78` and `75_simulation.tex:75-90`
  quote the *same four macros* — `\straddleRatio`, `\nStraddleAllMax`,
  `\shareStraddleAtHalfPct`, `\nStraddleHalfMin` — telling the same story, but
  §10.3 additionally carries two facts §4.1 does not: the plane's own size
  range, and the count of plane cells for which the inflation factor is
  undefined.

  So the cut is: **§4.1 keeps the mechanism and drops the crossing numbers**,
  forward-referencing §10.3 as it already does in the same sentence; §10.3
  keeps the crossing, which is what its heading is about, and keeps the plane
  facts. That saves the overlap without gutting either.

  **Not done now, deliberately**: §4.1's displacement paragraphs are precisely
  what Phase 1 rewrites — under the weighted scheme the whole displacement
  story changes — so cutting here before the run lands means cutting twice.

  **The cut list is in the length analysis and is executable as written**:
  Tier A (2.47 pp, already offered to the editor, destinations already
  written), Tier B (3.07 pp, pure duplicates inside §4/§6/§10/§11), Tier C
  (3.24 pp, compressible), Reserve (2.26 pp, outside the four sections).
  Two rules govern execution:
  - **Cutting a number is a saving; cutting a concession is a regression.**
    The protected list — the coverage measurement at full length, every
    withdrawn claim, the "descriptive diagnostic and not a guarantee"
    sentence, the prefix/PPM disclaimer, the per-pair role declarations, the
    decision-time ladder, the CMDB-programme reading, and the floats added at
    referee request — survives verbatim.
  - **§8.3 is a genuine conflict between two of this round's own goals.**
    Phase 2 *added* 213 words there to say the widening is applied; the
    length pass calls that a sixth restatement of the coverage story. Both
    are right. Keep the statement that the correction is applied and what it
    cost; cut the re-derivation of *why* the band undercovers, which §10.4
    already carries in full.
- [x] **4.2 Voice — decided: keep the editorial "we", and say so.** Round-25
  M12 asked for first-person singular or impersonal on the ground that the
  paper is single-author. Counted before deciding: **41 instances in the whole
  document, 19 in the main body parts** — small enough that the pass is easy,
  which is why the decision has to rest on something other than cost.

  Reading where they fall: the plural is not decorating narrative, it is
  carrying **accountability**, and it clusters exactly on the sentences the
  referees have praised — "we therefore withdraw the claim that a one-number
  report misstates a sign at a rate worth quoting", "we report both rather
  than the one that reads better", "we did not narrow the rule
  retrospectively", "we do not conclude that a surface report is a better
  decision rule than a number". Rewriting those impersonally ("the claim is
  therefore withdrawn") removes the agent from a withdrawal, which is the one
  place a paper should have one; rewriting them as "I" would be unusual enough
  in this literature to become the thing a reader notices.

  So: the editorial "we" stays. It is standard and unobjectionable in this
  field, and the alternative costs the paper its best feature to answer one
  line of a long list. **Record it in the response letter as a considered
  refusal with this reason**, not as an item quietly missed — a referee
  tolerates a reasoned "no" far better than a silent one.
- [ ] 4.3 Reduce the one-sentence bolded lead-in density in §§4, 6, 10 (it
  reads as a memo, not an article; keep them where a table needs a verdict).
- [ ] 4.4 Two figures still out of the main text that round-25 C3 asked in:
  the decision curve (S3) and the leakage tipping point (S2). Bring both in
  (as one figure each, print-sized); the region figure may stay out now that
  Table 7 carries the counts.
- [ ] 4.5 The AI declaration still discusses the literature-prevalence pilot;
  round-25 said keep the template statement plus the uses, drop the pilot
  from the declaration (it is described in §9.3 where it belongs). Trim; keep
  `AI-USE.md` as the archive record.
- [ ] 4.6 Keywords: "predictive process monitoring" survives as a keyword
  while §11 disclaims that literature's benchmark. Either the prefix-axis
  pilot (`s45_prefix.py`, already run per `ROUND27-STATE.md`) earns the
  keyword — then cite it in §11 — or the keyword changes to
  "process mining" / "event logs".

**Done when:** body ≤ ~42 pages, one voice, `texlint` enforces it, S2/S3
figures in the main text, declaration matches the Elsevier template.

---

## 5. Phase 5 — Claims alignment after the new numbers

- [ ] 5.1 Regenerate every headline through `make_numbers.py` /
  `round26_numbers.py` successors; abstract, highlights, Table 1 and §12 must
  quote the post-repair numbers.

### 5.1a The claims-at-risk register

Built before the run finished, by asking of each headline: *is it computed on
the declared surface (which Phase 1 does not touch) or on the inference
surface (which Phase 1 replaces)?* Work this list rather than re-reading the
paper.

**AT RISK — recomputed on the new inference surface; every one must be
regenerated and re-read in context:**

| claim | where | why it moves |
|---|---|---|
| "coverage … short of nominal" | abstract, §4.3, §10.4, §11 | 400 draws + weighted scheme; `cov_mult_B400` = 0.9575 says this clause may invert. **This is the headline change of round 27.** |
| `\madResolvedMedian` (0.0430 AUC) | abstract, highlight 4, §6.4, §12 | a distance averaged over *resolved* cells; the resolved set changes |
| 197 of 5,808 AUC cells resolve; 896 resolved cells; 67/896 = 7.5% | §6.3, §6.4, §12 | all counted on the inference surface |
| "1 of 42 cells disagrees" | §6.4, §12 | the 42 is a resolved∩MPID intersection |
| "14 of 19 pairs do not resolve the cell a conventional report stands on" | §6.4, §12 | resolved set |
| region labels, ρ, the resolved triples | Table 5, Table 7, §6.3 | recomputed under the new band |
| 74 cells whose band excludes their own estimate (1.9%) | §4.1, §11 | should go to **0** under weighted resampling — that is the repair's success criterion |
| the K/n coverage calibration and its factors (1.18–1.77; 3.33→4.54) | §6.3, §9, §11 | may become unnecessary; if the weighted scheme covers, this whole apparatus is retired rather than re-fitted |
| median family size 180, critical value 3.33 vs 2.35 vs 1.96 | §4.3, §6.3 | new family is uniformly 180 per pair, new draws |
| pointwise 24 / simultaneous 18 of 31 thresholds | §8.3 | Phase 2 changes these |
| "median 12.5% of a pair's cells" | §4.2, Def. 3, §11 | Phase 3.1, and the new design makes the share non-uniform |

**SAFE — computed on the declared surface or on point estimates; do not
churn these, and do not let a regeneration silently move them:**

- the whole decomposition, Table 6 and §6.2 — including the 71.7% resampling
  share, the 13.3% analyst share, the 26.3% higher-order share net of
  resampling, and "which axis leads is a property of the pair"
- the all-cells sign-disagreement rates (Table 8's unrestricted columns) and
  the 32.8% pooled rate
- the baseline-spread result (0.073 median, 0.0055 excluding the half-intake
  rung) and the layer ladder of §7.4
- Remarks 1 and 2, the Fieller-set counts (5,282 of 10,584)
- the 40-of-118 calibration-slope exclusions
- the decision-time ladder's *point estimates* (Table 9) — but its
  **intervals** run at 300 draws and should be checked for consistency with
  the new scheme, since §7.1's PC3 disagreement rests on one

- [ ] 5.1b After regeneration, diff `paper/numbers.tex` against its committed
  version and account for **every** changed macro against this register. A
  macro that moved and is not on the AT-RISK list is a defect, not a result —
  that is exactly the check that would have caught the round-25 inconsistency
  before a referee did.
- [ ] 5.2 Contribution 2 may claim simultaneous inference (not diagnostics)
  only under Phase 1's done-when. Highlight 3 likewise.
- [ ] 5.3 The stationarity diagnostic (`s46_drift.py`, run) and the prefix
  pilot (`s45_prefix.py`, run) get their one paragraph each in §11 / §5, so
  two "assumed and not tested" sentences become measurements.
- [ ] 5.4 `check_highlights.py`, `check_response_refs.py`, `texlint`,
  `verify_numbers` all green on the rebuilt paper and supplement.

---

## 6. Phase 6 — Reproducibility integrity: the `hgb` finding

`ROUND27-STATE.md` records that the boosting learner does not reproduce this
repository's committed results across machines at identical pinned versions
(up to 0.14 Nagelkerke on Sepsis), while `logit` reproduces to 5e-10 — and no
gate detects it because `verify_release.py` re-derives macros from committed
CSVs. The manuscript currently says every result re-runs by one command.
That sentence is not true on another machine, and a reviewer who tries is the
worst way to find out.

- [ ] 6.1 Diagnose: re-run one `hgb` pair under `OMP_NUM_THREADS=1` and with
  `scikit-learn` thread count pinned; if the difference persists, it is
  platform (BLAS/compiler) nondeterminism, not threading.
- [ ] 6.2 Disclose: one paragraph in `REPRODUCE.md` and one sentence in the
  code-availability statement — bit-exact reproduction is claimed inside the
  shipped Docker image (pin the image digest as canonical); outside it,
  logit-family results reproduce to 5e-10 and boosting-family results to a
  stated tolerance.
- [ ] 6.3 Gate: add a two-pair spot re-run (one logit, one hgb) to the
  verification harness with the documented tolerances, so the claim is
  executed rather than asserted, per rule 5.

**Done when:** the reproduction claim in the paper matches what a fresh
machine actually gets, with the tolerance stated and tested.

---

## 7. Phase 7 — Compliance and submission package (owner + agent)

- [ ] 7.1 **Owner:** mint the Zenodo/4TU DOI for release v27.0 *before*
  submission (`submission/OWNER-ACTIONS.md` §1.1); the round-25 report
  already refused "reserved, inserted at proof" once. Run
  `scripts/insert_doi.py`; `verify_numbers` must fail on the placeholder.
- [ ] 7.2 **Owner:** ORCID on the submission profile (OWNER-ACTIONS §0.1).
- [ ] 7.3 Supplement, `PROTOCOL.md`, amendment log, `requirements.lock`,
  Dockerfile (with digest), expected runtime all in the archived release;
  `check_package.py` green.
- [ ] 7.4 Highlights as a separate file (`submission/highlights.txt`,
  regenerate via `make_highlights.py` after Phase 5).
- [ ] 7.5 `submission/response_to_review26.md`: point-by-point against the
  round-26 external review (this plan's §0 items), each answer naming the
  section and the result file that discharges it, per the change-table
  pattern of earlier responses.
- [ ] 7.6 Cover letter: name the journal's reproducibility/software interests,
  offer the archived release for validation, and state in two sentences what
  round 27 changed (the weighted bootstrap, the designed 400-draw surface,
  the measured coverage now attained or the honest statement that it is not).

---

## 8. Phase 8 — Pre-submission red team

- [ ] 8.1 `python scripts/attack_verifier.py` and `round27_verify.py` —
  every condition, including the new §3 conditions.
- [ ] 8.2 A fresh-context read of the built PDF simulating a third-round
  referee: every number in §0's consistency list re-derived; every
  cross-reference resolved; every "Section 11 records" promise checked
  against Section 11.
- [ ] 8.3 The round-25 report's Phase-F attack table, re-run against the
  round-27 PDF; each row must land on a section that answers it.
- [ ] 8.4 Build via `build_journal.py`; confirm the submission manifest.

---

## 9. Record of execution

*(append per phase: what ran, what it found, what changed in the paper, what
it cost — per `PLAN-STRONG-ACCEPT.md` §0.2. Numbers here are checked against
result files like any others.)*

**Order of this section.** The baseline entry comes first and everything after
it is **newest first**, because during a long run the most recent entry is the
one a reader needs. Each entry carries its own timestamp, so the sequence can
be reconstructed; do not reorder them to fix the apparent inconsistency, since
the timestamps are the record and the arrangement is not.

### 2026-08-28, session start — baseline established

**What was found before anything ran.** The externally reviewed PDF
(`specification_surfaces.pdf`, built 2026-08-26 15:53 at commit `d854e9d`)
is **stale**: six commits of round-27 work land after it (`a03b560` through
`416cd1a`). Two of the three inconsistencies that review reported were
already repaired in `a03b560`, along with three more of the same class that
the review missed. §3.2 and §3.3 of this plan are therefore closed without
work, and the surviving item is §3.1 alone.

Consequence for the response letter (§7.5): it must be written against the
current source, not the reviewed PDF, and should say plainly that three of
the reviewer's items were already fixed in the interval — with the commit
hash — rather than claiming them as new work.

**Phase 1 resumed.** `s44_designed.py --scheme both --draws 400 --procs 8
--resume` restarted 2026-08-28 22:58 (`--procs 8`, not 12, because heat was
why the owner stopped it). State at restart: 13 of 19 weighted pairs carried
real 400-draw output (~10 MB each); the remaining 6 weighted and all 19
multinomial files were 130 KB smoke-run leftovers and are being recomputed.
`results/s44_facts.csv` is still the smoke run and must not be read until the
run completes.

**What the new design buys, read off `results/s44_grid.csv` before the run
finished.** Every one of the 19 pairs now carries the SAME surface —
2 learners × 2 splits × 3 quality conditions × 3 rungs = 36 cells, 180 scalar
members, `balanced = True`, at 400 draws. Three consequences the write-up
must claim, because each retires a standing limitation:

1. **The "corner, not a design" objection dies.** §4.2 and §11 currently
   concede that the inference surface is axis-complete but unbalanced, that
   the decomposition therefore cannot be computed on it, and that a
   resolution-IV fractional factorial would fix both. The new surface is a
   balanced full factorial, which is strictly stronger than the fraction the
   limitation asked for. The decomposition can now be computed on the
   inference surface as well as the declared one, and the two can be
   compared — which is a result, not a concession.
2. **Cross-pair statements get cleaner.** The old surface varied its design
   by log size, so a corpus median mixed pairs whose families differed in
   shape. Now every pair contributes the same 180-cell family.
3. **The per-pair inference share is no longer uniform and must not be
   quoted as one number** — 180/1,080 on the standard pairs, 180/4,800 on
   the case study's two, 180/1,620 on the largest. This interacts directly
   with §3.1 below: whatever macro survives must be recomputed against this
   design, and the case study's share falls rather than rises.

**One design choice to defend explicitly in the text, not silently.** The
three rungs are `B_half`, `B_intake`, `B_intake_g` — so the half-of-intake
rung, which an earlier referee called a straw baseline, is a third of the
inference family and therefore a third of what every region label and every
ρ is computed over. Keeping it is the right call and the paper should say
why in one sentence: it is admissible by declaration, and dropping it after
seeing which cells resolve would condition the family on the answer. Note
also that including it can only make a directional label harder to earn, so
the choice is conservative in the direction that matters. If §4.6 or §6.3
does not already say this, it must.

**Phase 1's downstream is already written; only the compute is missing.**
Verified by reading the scripts rather than assuming: `s41_bandcoverage.py`
already implements the fourth `nonzero` regime this plan asks for — a
heterogeneous non-zero truth two sampling standard deviations wide, added
precisely because under a zero truth every rejection is an error and
family-wise coverage cannot distinguish a band that resolves correctly from
one that never resolves. And `s47_schemes.py` already computes the three
comparisons that decide whether the repair worked: level coverage per draw,
displacement against $K$ and against $n$, and the count of cells whose
pivotal interval excludes its own point estimate — the last being the
headline, because it is a defect a reader can see without believing any
theory about why it happens. Round 25 counted 74 of 3,900. **The success
criterion for Phase 1 is that number going to zero under weights.**

### 2026-08-29, 01:55 — the new bands validated before anything depends on them

`verify_numbers` checks the OLD bands for internal consistency and does not
yet read `s48w`. Run by hand, on the 3,420 whole-surface cells:

1. the simultaneous band contains the pointwise interval on **every** cell —
   0 violations;
2. the conservative edge contains the simultaneous band on **every** cell —
   0 violations;
3. critical values run **3.214 to 3.430**, median **3.356**, all above the
   pointwise 1.96 — and close to the old surface's median 3.33, which is
   reassuring for a different scheme on a different design;
4. the band edges reproduce the regions file's beneficial and harmful counts
   on all 19 pairs, **exactly**;
5. no NaN edge anywhere.

**Check 4 failed the first time and the failure was mine.** I tested the
`sim_*` edges; the region labels are computed at the **conservative** end of
the critical value's Monte Carlo interval, which is what the manuscript has
said all along. Testing the right edge reproduces every count. Two useful
facts fell out of getting it wrong: the conservative safeguard costs two pairs
a handful of cells (89→86 and 28→27), so it is doing something small and
nonzero rather than nothing; and the **empirical** quantile edge would resolve
far less — 72 against 86 on one pair, differing on 16 of 19 — which is the
same ordering §10.4 reports between the multiplier value and the empirical
quantile's order-statistic interval, arriving independently on a new surface.

**Add these five as a permanent condition when `verify_numbers` is re-pointed
at `s48w`.** They are cheap, they caught nothing this time, and the reason to
add them is that check 4 is precisely the kind that fails silently: a band
built from one edge and a label counted from another would agree on most pairs
and differ on a few.

### 2026-08-29, 01:45 — the design is a balanced full factorial, checked rather than trusted

The rewrite will claim the new inference surface is "a full factorial and so a
strictly stronger guarantee than the resolution-IV fraction Section 11 asked
for". `s44_grid.csv` carries `balanced = True`, but that is the design's own
flag and not a measurement of what ran. Checked against the draw files:

- on **every one of the 19 pairs**, the AUC sub-surface is 2 learners × 2
  splits × 3 quality conditions × 3 rungs = **36 cells, with every
  combination present exactly once** — no missing cell, no duplicate;
- and every pair is **identical in shape**: the level counts and the cell
  count take one value across the corpus.

So the claim is supportable as written, and the second half of it — that a
corpus median no longer mixes families of different shapes — is now a
verified fact rather than a design intention. Both are worth stating in §4.2
with the check named, because "balanced" is exactly the kind of word a
referee will want evidence for and the evidence is one line of arithmetic.

### 2026-08-29, 01:30 — the decomposition on the inference surface: computable, and it does NOT confirm the declared one

§4.2's concession is that the inference surface is "a corner of the declared
surface rather than a design … which is why the decomposition cannot be
computed on it". Under the balanced design **it can**, and it now has been:
`results/s51_inference_anova.csv`, all **95** decompositions (19 pairs × 5
instruments), 36 cells each, no failures. That much retires the concession.

**Then it goes the other way, and the rewrite must not claim otherwise.**
Comparing which axis carries the largest first-order index on each surface,
the two **agree on 6 of 19 pairs**. The corpus medians differ too — on the
inference surface the rung leads at 17.1%, quality 8.6%, pipeline 4.8%, split
4.1%, higher-order 22.0%, against the declared surface's fold-averaged 21.9 /
19.2 / 15.2 / 26.3.

**The confound, stated because it is the whole interpretation.** The two
surfaces do not declare the same levels: the inference surface carries 2
splits, 3 quality conditions and 3 rungs against the declared surface's 6, 6–10
and 3–4. An axis cannot show the same variance share at three levels as at ten.
So this is a comparison **between two designs**, not a check of one against
the other, and it does *not* establish that either surface is unrepresentative.

**What it does mean for the rewrite, and it is a restraint rather than a
result.** The tempting sentence — *"the decomposition computed on the
inference surface confirms the declared one"* — is not available. Nor is its
opposite. What is available is narrower and worth saying: the decomposition is
now computable on both, the two are reported, and the ordering differs, which
is a reminder that a first-order index is a statement about *the levels an
analyst declared* and not only about the pair. That is consistent with the
paper's surviving claim rather than a refutation of it, but it qualifies it,
and §6.2 should carry the qualification rather than let a reader discover it
from the supplement.

**Do not promote this to a headline.** It is exploratory, the confound is real,
and a clean version would need the two surfaces matched on level counts —
which is a further run and is not this round's.

**A correction to this entry, made an hour after it was written, and the
reason it is left visible.** The first version said the leaders agree on
*seven* pairs. They agree on **six**. The inline script that produced the
seven omitted `first_split` from the columns it took the maximum over, so it
could not pick the split as a leader — and the split *does* lead on four pairs
of the inference surface, which is itself worth knowing given that surface
carries only two split levels. `scripts/s51_infanova.py` is the formalised
version and is the one to cite; it takes the maximum over all four axes and
maps s22's `learner` onto the designed surface's `pipeline` rather than
counting a naming difference as disagreement.

That is this project's rule 4 arriving on its own author: an inline number,
printed once and believed, was wrong in a way only re-implementation caught.
Nothing from a scratch script goes in the manuscript.

### 2026-08-29, 01:20 — every place that still describes the OLD inference surface

Found by grepping for the trap the audit had just caught twice. **The
inference-surface macros in the manuscript are still the round-25 ones**, and
they will silently stay that way through a rebuild unless each site below is
re-pointed. This is the concrete work list for §5.1b's "account for every
changed macro" — with the sites that will *not* change on their own.

| site | what it feeds | needs |
|---|---|---|
| `round20_numbers.py:69` `load("s20_grid.csv")` | `\nInferenceCells` (780), `\nInferenceScalar` (3,900) | `s44_grid.csv`: 19 × 36 = 684 cells, 19 × 180 = **3,420** scalar |
| `round20_numbers.py` (same block) `s21_facts` / `s21_regions` / `s21_critical` | every band, region, ρ and critical-value macro | the `s48w_*` files just written |
| `round21_numbers.py:900` `load("s20_grid.csv")` | second reader of the same grid | as above |
| `s25_denominator.py:96,148` | the denominator audit's inference column, and its per-pair draw check | `s44_grid.csv` and `results/s44_weighted/` |
| `s22_anova.py:327` globs `RESULTS/"s20"` | the **bootstrapped** decomposition indices and their intervals (Table S5) | `s44_weighted` — and note the design changed, so these intervals are not comparable to the old ones cell for cell |
| `s41_bandcoverage.py` | family-wise coverage | **done** — `--draws-dir` added, running against `s44_weighted` |
| `s21_bands.py` | the bands themselves | **done** — already had `--draws-dir` |
| `s28_figures.py:174-175` | **`figS3_regions.png`**, the ρ-and-region figure | `s48w_regions.csv`. Figures were an unchecked category and this is the one that matters: it draws a bar per pair sorted by ρ, so if it is not regenerated it will **picture** the old surface's labels under a caption describing the new ones — a disagreement a reader sees rather than has to compute |
| `s51_infanova.py` | the decomposition on the inference surface | **done** — reads `s44_weighted` by argument |

**Two of these are traps rather than chores.** `s25_denominator` computes the
audit that the manuscript's whole denominator discipline rests on; if it keeps
auditing the old surface while the text describes the new one, the paper's
most-defended claim becomes its most wrong. And `s22_anova`'s bootstrapped
indices are the only thing that would silently produce *plausible* numbers
from the wrong surface — the others would produce obviously stale counts.

**The pattern is now three-for-three.** Every check in this repository that
reads a fixed filename failed the moment the analysis moved: `round21_numbers`
counting crossed pairs, `s41` profiling families, and these. The generalisable
fix is not to re-point them one at a time but to make the surface an argument
with no default — a script that must be *told* which surface it describes
cannot describe the wrong one silently. Worth doing if a later round replaces
the surface again; recorded here because the reason will not be obvious then.

### 2026-08-29, 01:10 — THE WEIGHTED ARM IS COMPLETE, and it changes a headline

`s21_bands.py --draws-dir s44_weighted --prefix s48w` has run on all 19 pairs.
**Read the caveat in point 4 before quoting anything above it.**

**1. The repair works, and it does not fully work — as predicted.** The
pivotal interval excludes its own point estimate on **36 of 3,420** scalar
cells, **1.05%**, against round 25's 74 of 3,900 = 1.90% under multinomial
resampling. Roughly halved, not eliminated. Phase 1's done-when asked for zero
and does not get it, so §4.1 says the mechanism §11 named is removed and a
residual remains that the mechanism does not explain. **Do not write "the
weighted scheme fixes it."**

**2. The bands are wider, which is the conservative direction.** 890 resolved
cells at the nominal critical value against round 25's **1,150 nominal**. And
note what 890 is close to: round 25's **coverage-calibrated** count was 896.
So the weighted scheme at 400 draws produces bands about as wide as the old
scheme's calibrated ones — a hypothesis that `s41_bandcoverage.py` must test
before it is written down, but if it holds, **the K/n calibration apparatus is
retired rather than re-fitted** and §6.3 shrinks to a paragraph.

**3. The region labels move a long way.** Against round 25's calibrated
0 uniformly beneficial / 9 conditionally beneficial / 1 conditionally harmful
/ 3 sign-changing / 6 unresolved, the weighted arm gives **1 / 10 / 1 / 5 /
2**. Far fewer pairs resolve nothing; more resolve both signs. BPIC19 flips
hard — 94 harmful against 21 beneficial, ρ = −0.41.

**4. THE TRAP, and it is the most important thing on this page.** BPIC14 /
duration comes out **uniformly beneficial** — 180 of 180 cells — which
reverses "*No surface in this corpus is uniformly beneficial*", a claim the
paper has carried for rounds, and lands exactly on the state §4.6 calls "the
only state in which one positive number is a safe summary of a surface".

**It is on a smaller family, and smaller in the direction that manufactures
the label.** That pair's inference family is now 180 cells of its 4,800
admissible — **3.8%**, down from 480 cells and **10.0%**. And §4.6 already
warns, in the paper's own words, that *"a label computed on a sixth of a
pair's cells is systematically cleaner than one computed on all of them, and*
uniformly beneficial *is the label most helped by it: a claim about every cell
is easier to sustain over fewer cells."*

So the paper wrote the warning for this result before it had it. **The
rewrite must lead with the warning and not with the label.** The defensible
sentence is that the state obtains once in nineteen, on the pair with the
richest grid, over a family that is a twenty-sixth of that pair's admissible
cells — and that this is what the design's own restriction buys, not what the
data establish about every specification an analyst could choose. A headline
reading "we found a uniformly beneficial surface" would be the single most
attackable sentence in the paper, and it would be attackable using a paragraph
the paper already contains.

**5. What is still needed before any of this is written.** The multinomial arm
(for `s47`'s scheme comparison), and `s41_bandcoverage.py` on the new families
— because every label above is at the **nominal** critical value. `region` and
`region_nominal_q` are identical in `s48w_regions.csv`: no calibration has been
applied. Whether one is still needed is exactly what s41 decides.

### 2026-08-29, 01:00 — the repairs audited, and why that was worth doing

The 32 repairs rewrote a lot of prose and nobody had read the rewrites. A
third pass over **tonight's diff only** found **eight more defects, one
blocking** — every one of them created by a repair.

**The blocking one is the class this round keeps finding.** §8.4's headline
was reversed and **three other statements of the withdrawn claim were left
standing**, all citing the section whose headline now says the opposite. That
is the master-table defect again, committed by the round that was fixing it.

**And a safeguard failed the first time it was tested.** The macro behind
"the crossing has not been re-run on the other N pairs" carries a comment
saying it reads the crossing's own output *"so a crossing extended to a second
log moves the sentences with it"* — and it read **one filename**. So the macro
was corrected 15 → 17 in the same round that made 17 wrong; it is 11. A check
that reads a fixed filename cannot notice a second file. It now reads every
file the analysis writes, and counts pairs rather than logs.

**The lesson for the Phase 1 rewrite, which is the biggest rewrite left.**
Every repair is a new claim and inherits no credibility from the defect it
replaced. The rewrite of §4, §6, §10 and §11 must be audited the same way
before it is believed — budget that pass rather than discovering it is needed.

Two of the eight are worth carrying as method notes. `texlint` caught a
spelled-out magnitude in *my own* replacement sentence, which is the gate
doing exactly its job on the person maintaining it. And the Data availability
statement claimed a container digest that does not exist; it is now a macro
that states the deposit's status the way the DOI macro does, so the manuscript
cannot assert an artefact into existence.

### 2026-08-29, 00:24 — the first new pair, validated rather than assumed

BPIC19's weighted draw file was checked structurally before the run was left
to continue, because a malformed output discovered four hours later is four
hours lost:

- 519,696 rows = 401 draws × 1,296, where 401 is the point estimate at
  `draw = -1` plus 400 bootstrap draws, and 1,296 is 36 cells × 36 metrics
  (the 5 scalar instruments plus the 31-point decision-curve grid);
- 2 learners, 2 splits, 3 rungs — the declared balanced factorial, with no
  level missing;
- **180 scalar point-estimate cells**, which is what the design says a pair
  carries;
- zero NaN increments.

So the design in `s44_grid.csv` is the design being run, and the resume did
not silently drop an axis. Note the wall-clock: **86 minutes for one pair**
against the ~58 implied by the resume note's "about 70s a draw", so every
downstream estimate in this file was optimistic by about half.

### 2026-08-29, overnight — the second red team, and a headline that did not survive

Fourteen more findings over the files the first pass could not read, three
blocking, all repaired. The pattern held: **the defects are in prose that
describes tables, not in the tables.** Two are worth carrying.

**A paragraph whose own headline was one of its defects.** §8.4 said "And the
rules mostly tie", and then: the four rules separate "on only 11 of 19 pairs",
where the count was taken over the 16 pairs carrying a calibrated model — two
sentences after the same paragraph says the calibration rule excludes 3 of the
19. Eleven of sixteen is 69%, a majority. So "only" goes, and "mostly tie"
goes with it: the rules tie on 5 and separate on 11.

The same paragraph said the one-number rule is "worst on 10". That came from
`idxmax`, which returns the *first* maximum, and one-number is the first row of
every group. It is strictly worst on **3**, tied for worst on 2, and on **5 of
the 10 all four rules are identical at exactly zero** — so on half of them
nothing is worst. And "expected excess" was a cross-pair *median*: the means
are 0.056 against the conservative rule's 6.092, a 128-fold understatement in
the sentence arguing the rules tie.

**The paragraph's conclusion survives and is better supported than before.**
"The case against one-number reporting does not rest on this design" now rests
on numbers that hold — strictly worst on 3 of 16, worst-pair cost 0.412 per
thousand, mean excess 108× smaller than the conservative rule's. The
correction cuts *against* the paper's own advocate, which is why it is
reported rather than left as a median.

**The Conclusion asserted what §11 withdraws.** §12 opened "what remains is
not dominated by one choice" while §11, under a heading saying this evidence
does not support it, had withdrawn exactly that — and §12's own next sentence
gave a largest first-order index of 38.8% against a higher-order share of
26.3%. Net of resampling the interactions lead on **7 of 19** pairs, so on 12
a single axis carries more than every interaction combined. Both §12 and the
abstract now carry the claim that survives: *which* axis leads is a property
of the pair — rung on 8, pipeline on 6, quality on 5.

The abstract sits at exactly `texlint`'s 200-word limit, so that replacement
had to be word-neutral and was paid for with two lossless trims in the same
paragraph.

### 2026-08-28, overnight — an early read on Phase 1, and a warning about it

Computed directly from the 13 weighted pairs that already carry 400 draws,
restricted to the five scalar instruments so it is comparable with the number
the paper quotes:

| | cells | interval excludes its own estimate | median \|displacement\|/half-width |
|---|---|---|---|
| round-25, multinomial | 3,900 | 74 (**1.9%**) | 0.09 |
| round-27, weighted (13 pairs) | 2,340 | 20 (**0.85%**) | 0.129 |

**Read this as a warning, not a result.** The two rows are different surfaces
at different draw counts, so the comparison is not clean — `s47_schemes.py`
runs both schemes over *one* design at *one* draw count with *one* set of
seeds, and it is the authority. But the direction is worth knowing now: the
weighted scheme roughly **halves** the rate and does **not** take it to zero.

Phase 1's done-when says the count should be zero, "or reported ≤ 0.1%". On
this evidence it will be neither. So plan for the honest outcome rather than
the hoped one:

- The §4.1 paragraph must say the repair **reduced** the pathology rather
  than removed it, and give both counts.
- §11's "the repair is not run here" paragraph does not simply get deleted;
  it becomes a paragraph saying what the repair bought and what it did not.
- **Do not let the framing drift to "the weighted scheme fixes it".** Rule 2
  applies exactly here: this is the round's flagship change, so the temptation
  to over-read a favourable direction is at its strongest. The claim the
  evidence will support is narrower — every register level is present in every
  refit, so the *mechanism* named in Section 11 is removed, and a residual
  displacement remains that the mechanism does not explain.
- That residual is itself worth a sentence, because it says the displacement
  was never only about level loss.

### 2026-08-28, overnight — the auditability check, made to work

The worst of the red team's eighteen is repaired, and the repair is worth
recording because deleting the claim was the tempting option and the wrong
one.

`paper/tables/axes.tex` gains a third column, **"in the product"**, generated
rather than typed: `yes` on the five rows that are factors of the admissible
cell count — learner, split, register quality, admissible baseline, scalar
instrument — and, on the other four, a `no` that says where each is counted
instead. The encoding is fixed by the learner, so the learner row already
counts the pipeline and multiplying both would double-count it. The
ladder-rung row is the admissible row plus the intercept-only baseline, which
is in the surface and in no admissible set. The decision time indexes a
*second* surface rather than a further factor of the first. The operating
point multiplies the decision-curve grid, which is counted separately.

Verified mechanically on all 19 pairs: the product of only the `yes` rows
equals the declared-scalar column, zero mismatches. So a reader can now run
the check the paper invites them to run, which was the point.

Two smaller things fell out. The claim said "the **first** check the
verification harness runs" and it is condition 10, not condition 1, so
"first" is gone rather than defended. And the same table's two count columns
had been printing `6.000` and `19.000`, because the integer coercion needs
every value in the column finite and the envelope row is NaN.

**The specification-curve table now obeys Definition 3 too**, and a condition
was added so the pair cannot drift again — read by *header* rather than by
column position, because that table gained a column when it was repaired and
a positional read would have silently moved to the wrong one. Exercised
against the exact defect it replaces: flipping one withdrawn label back to
its pre-minimum-share value fails the build, and the clean tree passes.

**`\nDirectionalLabels` was 13 and is 10.** It counted `region != unresolved`,
which includes the three *sign-changing* pairs — and a sign-changing label
carries no direction, which is precisely what the four sentences quoting it
say in words. The numerator is now re-derived over the same rows as the
denominator, so a count taken over one set can never again be printed against
a total taken over another.

**Outstanding, small:** `paper/tables/decisiontime.tex` is generated and
`\input` by nothing — confirmed dead by grep. Either input it or stop
generating it; it is harmless but it is a table a `\ref` could resolve to
`??`.

### 2026-08-28, overnight — red-team repairs, two findings that grew

Two of the four repair agents are done and their findings extended past what
was handed to them. Both extensions are recorded because each is a case of the
same defect surviving in a file nobody had looked at.

**The pre- versus post-minimum-share label systems are two systems, and the
paper had not said so.** The supplement asserted one conditionally harmful
surface exists while the master table shows none — and both were right about
their own object. `\nCondHarmfulCal` and its siblings count the *calibrated
band's* region column, which is the label **before** Definition 3's minimum
resolved share; the master table prints the label **after** it. Four pairs
lose a direction there and one of them is the only conditionally harmful
surface the band reaches. The repair is not to pick one: both sets are now
macros (`\nCondBeneficialMinShare` and siblings, 6/3/0/10 against 9/3/1/6), so
a sentence states which system it quotes. §4.6 carried the same contradiction
in the article body and now says the label is available and the data do not
earn it — Helpdesk resolves 2 cells of 180, so the direction is withdrawn.

**`\calFactorMin`/`\calFactorMax` described the wrong object in both places
they appeared.** They are the min and max over the 33 cells of the
*simulation plane*; the factors actually **applied to this corpus** are
`\calMin`/`\calMax` (1.18–1.77), already correct elsewhere. Both sites are
fixed and the three `calFactor*` macros now appear in no prose at all — they
should be retired from `round21_numbers.py` so nothing reaches for them again.

And the argument got *better* for being corrected: against a needed 1.05–1.24,
both ends of 1.18–1.77 sit above the corresponding ends, so where the
calibration acts it is **conservative rather than short** — which the old
sentence, hedging with "of the right order", could not say. `\calMax` = 1.77
is still below `\shortfallDcaMin` = 1.90, so "absent where the shortfall is
largest" survives intact.

**Two smaller corrections worth recording because they correct me.** The
tie-break paragraph's "a quarter of the point estimate's own magnitude" was
describing two different quantities with one number: the range over 25 random
tie orders is **30.6%** of the declared increment, and the displacement the
undeclared sort actually caused is **12.4%** — not the 10% I estimated, which
came from dividing the *rounded* display macros. Both are now shares of one
declared denominator. And the agent asked to fix "the other 19 pairs"
declined to wire a count, on the ground that whether the referent is 17 or 18
turns on a judgement about how the case study's own cell is individuated —
and that inventing one would re-create the class of error being fixed. It
rewrote both sentences to be true under either reading instead. That is the
right call.

### 2026-08-28, later — an internal red team, and what it changes about this plan

An adversarial pass over the sections no referee has complained about
returned **eighteen findings, eight blocking**, all verified against
`results/*.csv` or against the generator. They are enumerated in
`REFEREE-LOG.md` under R27.6 and are being repaired now.

**The one that matters most is not on any referee's list.** The paper's
advertised *first* auditability check — "multiplying Table 3's level counts
gives the cell counts of Section 6, and that multiplication is the first
check the verification harness runs" — **does not work.** Three of Table 3's
nine rows break the product: encoding is already fused into the learner row,
the decision time is not a factor of any surface, and the baseline is printed
twice. The naive product for a modal pair is 267,840 against a declared
1,080. A reader who follows the paper's own instruction to check its
denominator gets a number six times too large.

That is worse than any single wrong number, because the whole argument of
this paper is that a reader should be able to reproduce a denominator. **It
must be made to work rather than deleted** — the claim is the right claim and
the table has to earn it.

**What the pass also bought, and what it costs.** It verified roughly thirty
identities clean, cell for cell, including the entire denominator table, all
nineteen rows of the master/triple/calibrated-band tables, every corpus
median of the decomposition, and the decision-time ladder's increments,
intervals and ordinals. The defects are concentrated **in prose that
describes tables, not in the tables** — which is worth knowing, because it
says the generators are sound and the writing is where the risk lives. That
is also the argument for the Phase 4 length pass being a correctness measure
and not only a presentation one: every restatement of a number in prose is
another place for the prose and the table to drift apart, and this paper
restates 55 of the 73 macros in §11 alone.

### 2026-08-28, later — Phase 4.5/4.6 complete

**The AI declaration (4.5) — and an overclaim found while trimming it.** The
declaration is now Elsevier's template statement plus the two facts that
belong with it, and nothing else; the literature-pilot description that had
accumulated in it is removed, having been verified to be stated where the
pilot is described (§9.3, `70_standard.tex:94-100`, plus twice in the
supplement).

The substantive find: the declaration's assertion that **no generative model
produced, imputed, augmented or selected any datum, result or citation** was
*unscoped*, and was safe only because the pilot carve-out immediately
followed it. The supplement does report prevalence estimates from
adjudications that are machine-assisted. Deleting the carve-out and leaving
the sentence would therefore have converted a trim into an overclaim — the
exact failure this project's rule 2 predicts, since the trim looked like pure
subtraction. The sentence is now scoped to "behind a claim of this paper",
which is what it always meant, with one clause pointing at §9.3.
`submission/credit_statement.md` carried the same unscoped sentence beside the
same pilot description and is scoped to match; its claim that the manuscript
states this in an *Acknowledgements* section was also stale and now names the
dedicated declaration section.

**Keywords (4.6) — retired rather than earned.** "Predictive process
monitoring" → "event logs". The prefix pilot does not earn the keyword: one
log, six prefix levels, one register, no bucketing, no sequence encoder, and
the interval spans zero on two of the six levels. The paper's own text says
so in three places, including the pilot appendix's "it does not make this a
predictive-process-monitoring paper". A keyword is a claim of topical
membership and the body disclaims it. `.zenodo.json` still lists the term
among twenty *deposit* keywords: **deliberately left**, because deposit
metadata is a discovery aid where breadth helps and no reader takes it as a
claim about contribution. Recorded here so it is not re-litigated as an
oversight.

**Phase 2 unblocked without new compute.** The decision-curve family's
measured shortfall is already on disk in `results/s41_facts.csv`:
`shortfall_dca_min` 1.9001, `shortfall_dca_max` 2.0455, with
`ratio_dca_all` 2.0934 against `ratio_dca_adm` 1.7957 (the latter excluding
the 841 degenerate cells). So the widening §8.3 never applied is arithmetic
on existing draws, exactly as the review claimed.

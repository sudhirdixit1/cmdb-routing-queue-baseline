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

## STATUS AT A GLANCE — updated 2026-08-28, overnight session

| phase | what | state |
|---|---|---|
| 1 | weighted bootstrap, designed surface, 400 draws | **running** — `s44_designed.py`, 13/19 weighted done at restart, on BPIC19 (the ~1 h pair); multinomial arm after it. Everything downstream is written and waiting. |
| 2 | decision-curve band widened by its measured shortfall | **done** — `s49_dcaband.py`. Costs 10 of 31 resolved thresholds; the per-thousand headline was checked and is untouched. |
| 2b | within-cell noise bound on the analyst-choice share | queued — needs Phase 1's draws |
| 2c | crossed family × encoding on the 8 ITSM pairs | **script ready**, run queued behind Phase 1 |
| 3 | the inference-share denominator, plus a generalised sweep | **done** — two macros, and a condition that re-multiplies every quoted count from the axis declaration |
| 3b | scikit-learn citation; §9.3's euphemism | 3b.1 **done**; 3b.2 queued |
| — | **internal red team, pass 1** | 18 findings (8 blocking) — **4 agents repairing** |
| — | **internal red team, pass 2** | running, over the files pass 1 could not read |
| 4 | length | **measured**: 58 pp, and 42 is *not* reachable — target renegotiated to 46. Cut list written and executable. Execution waits for Phase 1. |
| 4.2 | voice | **decided: keep the editorial "we"**, with the reason recorded |
| 5 | claims regenerated against the new numbers | register written; execution waits for Phase 1 |
| 6 | the `hgb` cross-machine reproduction gap | agent working |
| 7 | compliance | audited against the journal's own guide; agent-fixable items **done**; owner items in `submission/OWNER-ACTIONS.md` §4 |
| 8 | pre-submission red team | partly done by the two passes above |

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

- [ ] **2.4 The decision-curve FIGURE now disagrees with its own section —
  fix introduced by this round's own correction.** `app_secondary.tex:306-315`
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

- [ ] 2b.1 Compute it per pair from the Phase-1 draw files; report the
  implied ceiling on the noise share of `analyst choice`.
- [ ] 2b.2 One sentence in §6.2 and one paragraph in the supplement. Do NOT
  promote it to a fourth reporting object — the project's own rule is that a
  check is not a contribution. It is a bound that makes an existing number
  honest, and it should read that way.
- [ ] 2b.3 If the bound turns out to be large enough that `analyst choice`
  is mostly noise, rule 1 applies and §6.2's claim changes.

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
- [ ] **3b.2 §9.3's "machine-assisted" is a euphemism.** The AI declaration
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

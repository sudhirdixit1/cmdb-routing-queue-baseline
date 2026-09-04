# Plan: round twenty-eight — from *major revision (narrow)* to *accept*

**Target venue:** Information Systems, Elsevier, ISSN 0306-4379
**Written:** 2026-09-03, after reading the round-27 PDF (`250e8e8`, 63 pp)
as an eighth referee. The report is `submission/review_round28.md`; read it
first. **Predecessor:** `PLAN-ROUND27.md`, executed; its §9 is the record.
**Audience:** an autonomous agent. `PLAN-STRONG-ACCEPT.md` §0 still governs
how to work; three rules round twenty-seven added are in §0 below.

---

## STATUS AT A GLANCE — updated 2026-09-04, 00:30

| phase | state |
|---|---|
| 1 · coverage grid re-matched to the balanced design (`s41`) | **done** — two runs; the second calibrated to the corpus's estimator ratio; empirical quantile adopted by the rule (§10 record) |
| 2 · operative critical value → empirical quantile, every band-dependent number regenerated | **done** — `s21 --operative emp`, `s49` on the admissible family, chain re-run, 168 macros / 41 conditions / 0 failures |
| 3 · the rewrite: §4.3, §6.3, §8.3, §9.4, §10, contribution 2, abstract, highlights | **done**, and audited against the built PDF (§8.2) |
| 4 · revision narrative out of the article; voice | **done** — texlint check 16 widened; §6 bold lead-ins 36 → 10 |
| 5 · length | **done, short of target** — 63 → 57 pp; body 21,400 → 18,300 words with ~600 added; the 52-page target is not reachable without a protected float or a concession; next cuts and costs in `submission/summary_of_changes.md` §4 |
| 6 · the package: cover letter, uploads, AI declaration | **done** |
| 7 · ten small items (R28.6) | **done** (item 9 is the owner's DOI) |
| 8 · gates, red-team of every rewrite, build | **done** — all gates clean except the DOI placeholder `final_search` reports; attack suite 11 of 11 caught after two cases were re-pointed and one independent re-derivation added (§10) |
| 9 · owner items (DOI, image digest, e-mails, address, push/tag) | owner — `python scripts/finalise.py` |

---|---|
| 1 · coverage grid re-matched to the balanced design (`s41`) | **done** — two runs; the second calibrated to the corpus's estimator ratio; empirical quantile adopted by the rule |
| 2 · operative critical value → empirical quantile, every band-dependent number regenerated | not started — waits on 1 |
| 3 · the rewrite: §4.3, §6.3, §8.3, §9.4, §10, contribution 2, abstract, highlights | not started — waits on 2 |
| 4 · revision narrative out of the article; voice | not started |
| 5 · length, to ≤ 52 pp article / ≤ 46 pp body | not started — waits on 3 |
| 6 · the package: cover letter, uploads, AI declaration | not started |
| 7 · ten small items (R28.6) | not started |
| 8 · gates, red-team of every rewrite, build | not started |
| 9 · owner items (DOI, image digest, e-mails, address, push/tag) | owner |

---

## 0. How to work — three rules round twenty-seven earned

The rules in `PLAN-STRONG-ACCEPT.md` §0 apply unchanged: numbers reach the
manuscript only as macros from `paper/numbers.tex`; every gate runs before a
commit; progress is recorded in §10 of this file, newest first, with numbers
checked against result files. Three more, each learned the hard way last
round (`REFEREE-LOG.md` R27.17, R27.19, R27.21):

1. **A pooled median is not a corpus statement.** Before quoting any
   simulation number as being about "this corpus" or "the reported design",
   name the row it comes from and check that row's family size and draw
   count equal the corpus's. Three headlines were wrong last round for this
   reason, and R28.2 is a fourth. Phase 1 adds a gate for it.
2. **Every rewrite is audited by a separate pass before it is trusted.**
   Each rewrite pass last round introduced 10–18 defects, three of them
   blocking, one of them the deletion of a concession. Phase 8.2 is that
   audit and it is not optional.
3. **Decide the rule before the number exists.** Phase 1 ends with a
   decision that changes every band-dependent number in the paper. §1.4
   writes the decision rule now, so the result cannot choose its own
   framing.

Build with `python scripts/build_journal.py` (latexmk is not on this
machine; a redirected shell reports its absence as success).

---

## 1. Phase 1 — Re-match the coverage grid to the design the corpus runs

**Why this is first.** `results/s41_coverage.csv` measures family-wise
coverage on a grid matched to the *previous* inference surface: whole-surface
cells of 120/33, 180/80 and 480/150 (cells/draws) and decision-curve cells of
534/40, 1,100/80 and 2,966/150. Since round twenty-seven every pair carries
180 scalar cells at 400 draws and about 1,100 decision-curve cells at 400
draws (`results/s48w_critical.csv`, `n_family` 1,058–1,116). The only cell
matched to the current design is the heavy-regime draw-count ladder's 400
point, and the non-zero-truth regime was never run there. `\covMultNonzeroMedian`
(84.3%) is the median over six unmatched families and §10 quotes it beside
the matched 91.6%.

- [ ] **1.1 Re-declare `GRID` in `scripts/s41_bandcoverage.py`.** Replace the
  six cells with cells matched to `s48w`: `(180, 400, "whole-surface")`,
  `(1100, 400, "decision-curve")`, and the case study's own curve family
  (248 cells; read its draw count from `s26_calib_dca.py`'s output rather
  than assuming). Keep the old six as a *legacy* tuple so S9's history can
  still be described, but nothing in the article quotes them. Re-profile
  the matching (`--only profile,calibrate`) against `s44_weighted`'s draw
  files, since the tail and correlation targets were fitted on the old
  surface. Fix the stale comment that says 400 draws is unaffordable.
- [ ] **1.2 Run it**: all four regimes (`gaussian`, `heavy`, `degenerate`,
  `nonzero`) × all five candidates (`q_mult`, `q_mult_hi`, `q_emp`,
  `q_emp_hi`, `q_rad`) × 2,000 replicates on every matched cell, plus the
  draw-count ladder `BSENS` at (180, ·) under `heavy` **and** `nonzero`.
  Matrix arithmetic only; give it `--procs`. Accept with
  `provenance.py --accept s41_bandcoverage.py`.
- [ ] **1.3 Macros.** In `scripts/round27_numbers.py` (or a new
  `round28_numbers.py` that the runner calls — check `check_sources.py`
  lists it): every coverage macro quoted as matched to the reported design
  reads the `(whole-surface, 180, 400)` row of the named regime.
  `\covMultNonzeroMedian` is retired; replace with
  `\covMultNonzeroAtDesign`, `\covEmpNonzeroAtDesign`, and their SEs. Any
  macro that is a pooled median keeps the word `Pooled` in its name and is
  used only in a sentence that says "pooled".
- [ ] **1.4 The decision rule, fixed before 1.2 finishes.** Let $c_h$ and
  $c_z$ be the empirical quantile's coverage at (180, 400) under `heavy`
  and `nonzero`, with Monte Carlo SEs $s_h$, $s_z$ (about 0.5 points).
  - **Adopt** the empirical quantile as the operative critical value
    (Phase 2 as written) if $c_h \ge 0.95 - 2s_h$ **and** $c_z \ge 0.95 - 2s_z$.
  - **Do not adopt** it if either fails by more than two SEs; Phase 2 then
    becomes "print both, state that neither attains the level, and say by
    how much each is short" — the paper's current position, with the
    numbers corrected. The framing for both outcomes is in §1.5 so neither
    is written after the fact.
  - The decision-curve families are decided separately by the same rule on
    the (1,100, 400) cell, on the *admissible* family (degenerate cells
    excluded, §2.3).
- [x] **1.4a Amendment, 2026-09-03 22:40, written before the second run.**
  The first re-matched run (calibration at 180 × 400, kurtosis targets
  only) gave multiplier 94.5% and empirical 94.5% under `heavy` on the
  surface family — both at level — and its synthetic family had
  $q_{\mathrm{emp}}/q \approx 1.0$, where the corpus's own families have a
  median 1.50 (surface) and 2.24 (admissible curve cells). The kurtosis
  match had chosen a contamination share of 2% against round 27's 5%, and a
  95% quantile of 400 maxima sees a 2% contamination and not a 5% one, so
  the verdict was riding on a grid choice the corpus does not constrain.
  **A synthetic family counts as matched only if it reproduces the corpus's
  observable ratio $q_{\mathrm{emp}}/q$** (within the corpus's interquartile
  range) as well as its kurtosis; the calibration gains that target and a
  finer contamination grid, and the run is repeated. Decision rule, extended
  for the case the first run raised: if both estimators pass the level test
  on the matched family, the multiplier stays operative (the narrower band,
  at level) and the empirical is printed; if the empirical passes and the
  multiplier fails, the empirical is adopted; if neither passes, both are
  printed and neither is described as attaining its level. The first run's
  coverage table is kept as `results/s41_r28a_coverage.csv` for the record.
- [ ] **1.5 Both framings, written now.**
  - *Adopted:* "The critical value this paper reports is the empirical
    $(1-\alpha)$ quantile of the observed bootstrap maxima — the Romano–Wolf
    construction — which on the family matched to this design covers
    \covEmpWholeAtDesign\ under the corpus's tails and \covEmpNonzeroAtDesign\
    under a non-zero truth, against a nominal 95%, under an ideal bootstrap
    that makes both an upper bound. The Gaussian multiplier approximation
    used previously covers \covMultWholeAtDesign; every table prints both.
    What remains uncorrected is the pointwise interval underneath, whose
    $K/n$-governed shortfall Section 9.3 measures."
  - *Not adopted:* "Neither estimator of the critical value attains its
    level on the family matched to this design: the multiplier covers X and
    the empirical quantile Y under a non-zero truth. Labels are nominal;
    both are printed; the shortfall is stated in the factor a widening
    would need." (Keep the current §9.4 apparatus in that case.)
- [ ] **1.6 Gate.** A `round28_verify.py` condition: for every macro whose
  name ends in `AtDesign`, the row it derives from has `K_nom = 180` and
  `B = 400` (or the decision-curve equivalents), and the `nonzero` row
  exists. Prove it by deleting the row and watching the gate fail.

## 2. Phase 2 — The operative critical value (if §1.4 adopts)

Everything here is arithmetic on `results/s48w_bands.csv.gz`, which already
carries `q_emp`, `q_emp_lo`, `q_emp_hi`, `emp_lo`, `emp_hi` per cell. No
refit, no draw.

- [ ] **2.1 `scripts/s21_bands.py`**: add `--operative {mult,emp}` (default
  `emp` once adopted). `regions.csv` gains a full second label set —
  `n_beneficial_emp`, `n_harmful_emp`, `n_unresolved_emp`, `rho_emp`,
  `region_emp`, `region_emp_minshare` — computed with `label_of(emp_lo,
  emp_hi)` and `region_of`, and keeps the multiplier set under `_mult`
  names. The operative set is a *copy* named without suffix, so every
  downstream generator reads one column and the choice is one flag.
  Operative edge: the point estimate `q_emp` (94.7% at design), with the
  order-statistic upper end `q_emp_hi` printed as the sensitivity, mirroring
  what the multiplier band did with its MC upper end. Record that choice in
  `submission/DECISIONS.md` with the alternative (upper end operative:
  96.6% coverage, ~0.12 resolved cells per family in the zero-truth
  simulation — over-covers and resolves almost nothing).
- [ ] **2.2 Every band-dependent macro** in `round27_numbers.py` derives from
  the operative set, with a `Mult` twin kept for the comparison. The
  claims-at-risk register is §2.5; each row gets its old value, its new
  value and the sentence that quotes it.
- [ ] **2.3 Decision-curve families.** Replace `s49_dcaband.py`'s widening
  (`f · q_mult`, f = 2.61) with `q_emp` on the *admissible* family, where a
  cell is inadmissible if its net-benefit difference is exactly zero in at
  least nine draws of ten (S9.6's own criterion: such a cell is arithmetic,
  not a statement). Declare the rule in S3.3 beside the four interval
  objects. Report the operating points resolved under (a) `q_emp` on the
  admissible family — operative; (b) `q_emp` on all cells; (c) the previous
  2.61 widening — for comparison, in S14.7. If (a) and (c) disagree on the
  count, the paper says which is operative and why (the rule, not the
  count).
- [ ] **2.4 Tables**: `master.tex` (Table 4) prints the operative band in the
  `simultaneous` column and the multiplier band in a new column or Table S9;
  `triple.tex` / `regions.tex` (Table 6) print the operative triple, with the
  multiplier triple in S16; `misreport.tex` (Table 7) recomputes its
  `resolved` columns on the operative set; `calbands.tex` (S9) becomes a
  three-way comparison — multiplier, empirical, empirical × $c(K/n)$ — and
  S9.7's ladder gains the empirical rung as the *first* one rather than a
  footnote.
- [ ] **2.5 Claims-at-risk register** (fill the new column from
  `numbers.tex` after 2.2; every row must be accounted for in §10's record):

| macro / statement | old | where quoted | new |
|---|---|---|---|
| `\nResolvedCorpus` / `\nResolvedWhole` | 890 | §4.3, §6.3, §6.4, §10, S3.5, S9.7 | (698 expected) |
| `\rhoMedian…` | 0.039 | §6.3, S9.7 | (0.000 expected) |
| pairs resolving nothing | 2 | §6.3 | (8 expected) |
| "17 pairs resolve anything; 12 one sign only (11 + 1); 5 both" | 17/12/5 | §6.3 | ? |
| directions withdrawn under minimum share | 5 of 12 (7 rows marked) | Def. 3, Table 4 caption, Table 6, §10 | ? |
| uniformly beneficial count | 1 (BPIC14/duration) | §6.3, S14.18, S9.7 | 1 — already shown to survive |
| conditionally harmful before/after min. share | 1 / 0 | §4.6, S9.4 | ? |
| median cells resolved per pair | 19 of 180 | §6.4 | ? |
| `\madResolvedMedian` | 0.0556 AUC | **abstract, highlights**, §6.4, §11 | ? |
| `\madFullyRestrictedMedian` | 0.0600 | §6.4 | ? |
| `\misreportPooledResolvedPct`; per-instrument 7.2–24.8% | 16.4% | §6.4 | ? |
| resolved AUC cells 217 of 684 (31.7%) | | §6.4 | ? |
| `\nCellsFullyRestricted` and its disagreement count | 38 → 0 | §6.4, §11 | ? — if the count is no longer 0, the withdrawal in §11 is re-examined, not softened |
| "14 of 19 pairs do not resolve the reference cell" | 14 | §6.4, §11 | ? |
| §6.5 verdicts part company / neither resolves / one-sign sub-surface | 9 / 1 / 1 of 19 | §6.5, S15 | ? |
| §8.3 operating points resolved: pointwise / band / before widening | 24 / 5 / 18 | §8.3, §10, S14.7 | ? |
| §7.5 "0 of 30 reductions with a non-bounded Fieller set" | 0 | §7.5 | recheck — Fieller kind depends on the band |
| §3.4 "5,282 of 10,584 reductions non-bounded" | 5,282 | §3.4 | recheck |
| within-instrument vs whole-surface: "different label on 8 of 19"; 1,135 vs 890 | 8; 1,135/890 | §6.3 | ? |
| contribution 2 wording ("descriptive diagnostics, not guarantees") | | §1, §4.3, §6.3, §10, abstract | rewritten per §1.5 |

  Untouched by the switch and to be left alone: the decomposition (§4.5,
  §6.2, Table 5), the 71.7% / 13.3% / 26.3% / 56.0% figures, the
  decision-time ladder (§7.2, pointwise), the layer ladder (§7.4), the
  cohort × target 99.3%, the planned contrasts (§4.4), the calibration
  screen 40 of 118, the 1.71 vs 0.003 promise, the stationarity and prefix
  results. `verify_numbers` must show these macros byte-identical before
  and after.

- [ ] **2.6 `check_bands.py`** extends to the empirical edges: `emp_lo ≤
  cons_lo` on every cell (the empirical band is never narrower than the
  multiplier's conservative end — S3.5 says it holds on 19 of 19; make it a
  condition), and the operative label set equals a recomputation from the
  edges.

## 3. Phase 3 — The rewrite against the covering band

Write each section once, after Phase 2's numbers exist. Ready-to-paste
paragraphs are deliberately not supplied here: §1.5 fixes the framing, the
numbers are macros, and the round-27 lesson is that pasted prose drifts.

- [ ] **3.1 Contribution 2** (`00_front_intro_related.tex`): "Simultaneous
  inference whose coverage is measured" and — if adopted — *attains its
  nominal level on the family matched to this design under an ideal
  bootstrap*, with the pointwise $K/n$ caveat in the same sentence. Drop
  "reported as descriptive diagnostics" wherever the operative band covers.
- [ ] **3.2 §4.3**: the critical value is the Romano–Wolf empirical quantile;
  the Gaussian multiplier is an approximation adopted for Monte Carlo
  precision that undercovers under heavy tails (S3.5); one sentence on why
  400 draws is where the order statistic becomes usable (R27.19's table).
  Disambiguate the two "1.35"s (R28.6.6).
- [ ] **3.3 §6.3**: labels under the operative band; the multiplier's beside
  them as "what the previous approximation would have resolved"; the (n, K)
  calibration paragraph shrinks to a pointer, because its role is now the
  pointwise channel only (S9).
- [ ] **3.4 §8.3**: the admissible decision-curve family and its empirical
  quantile; the 2.61 machinery leaves the body.
- [ ] **3.5 §9.4**: reorganise around the matched cell — one table (make it
  `bandcov.tex`) with the five candidates × four regimes at (180, 400) and
  (1,100, 400); the draw-count ladder as the sensitivity; the degenerate-cell
  mechanism in one paragraph. Target ≤ 900 words from 1,945 for §9.
- [ ] **3.6 §10**: the "Internal — the band does not attain its nominal
  level" paragraph is rewritten to the new shape (the reported band attains
  it under an ideal bootstrap; the pointwise channel and the transfer are
  what remain); the "two repairs … neither did what it was named for"
  paragraph is cut to its two findings without the history (Phase 4).
- [ ] **3.7 Abstract and highlights**: "whose coverage we measure against a
  known answer and find short of nominal" → the adopted framing; the
  0.0556 highlight regenerates from its macro via `make_highlights.py`.
- [ ] **3.8 `check_claims.py`**: add the retired phrasings — "descriptive
  diagnostics and not as guarantees" (if adopted), "not applied … larger
  than it supplies" as a statement about the operative band — with round
  28 as the retiring round. Test each by reinstating the sentence.

## 4. Phase 4 — Revision narrative out of the article; voice

- [ ] **4.1 Rewrite** without history, keeping every finding:
  `20_inference.tex:56–124` ("A previous version of this paper named the
  repair", "which this paper had never reported", "the diagnosis this paper
  offered was wrong"); `80_limits.tex:62` ff ("two repairs this paper named,
  both run, and neither did what it was named for", "Two changes this
  paper's own analysis identified as the first to make are run here"). The
  finding is *level loss does not explain the displacement; the draw count
  is not the binding constraint* — state it as a result of the comparison.
- [ ] **4.2 `texlint.py` check 16**: add `previous version of this paper`,
  `this paper had never reported`, `repairs? this paper named`, `this paper
  offered was wrong`, `this paper's own analysis identified` to the main-
  text banned list; keep the supplement's correction register exempt.
  Prove on the current source (it must fail) before the rewrite.
- [ ] **4.3 Voice**: at most one instance in the article of each of "which
  is the paper's own thesis", "we say so plainly / stated rather than
  implied / rather than argued away", "the honest shape / the honest
  reading"; bolded lead-ins at most one per page in §§4, 6, 9, 10 (count
  with a grep on `\textbf{` per part and print it in the record).

## 5. Phase 5 — Length

Target **≤ 52 pages article, ≤ 46 body** (from 63 / 57). The referee's rule
stands: a cut that removes a number is a saving; a cut that removes a
concession is a regression. Moves, in order, with the words they free
(`results/section_words.csv`):

- [ ] 5.1 §4.1's scheme comparison (`20_inference.tex:56–124`, ≈1,000 words)
  → new S3.8; the body keeps ≤ 150 words: the scheme adopted, the two
  findings, the pointer. (−2 pp)
- [ ] 5.2 §6.6 (≈220 words) → S14.3, with a two-sentence pointer in §4.7.
  (−0.5 pp)
- [ ] 5.3 §9 after Phase 3.5 (1,945 → ≤ 1,100 words). (−2 pp)
- [ ] 5.4 §10 (2,244 → ≤ 1,300 words): delete every paragraph that re-argues
  a section rather than naming its threat; the rule is that §10 may state a
  limitation and point, not re-derive. (−2 pp)
- [ ] 5.5 §6.4 (≈1,100 words): the three restrictions in one paragraph each,
  Table 7 carrying the numbers. (−1 pp)
- [ ] 5.6 §7.4 "What would have to change" duplicates S14.14; keep the
  three-item list in the body at one sentence each. (−0.5 pp)
- [ ] 5.7 Re-measure with `texlint.py --sections` and the built `.aux`; put
  the arithmetic in the response letter as R27.21 did. If the count is
  still above target, the next two cuts are the ones `OWNER-ACTIONS.md`
  §1.7 already names (the partial-identification passage of §8; §6.5), in
  that order, and the letter says what each costs.

## 6. Phase 6 — The package: what the editor reads

- [ ] **6.1 Cover letter, rewritten, ≤ 2 pages.** Opens with what the paper
  contributes (three objects, one sentence each) and the case-study finding
  a service-management reader cares about. Then, in one paragraph: the
  earlier manuscript this journal's referee recommended rejecting; that the
  present manuscript answers that report in `response_to_referee.md`; and
  that **the manuscript was then revised through internal adversarial
  reviews conducted with a large-language-model assistant against the
  repository, all of them recorded in `REFEREE-LOG.md` in the archive** —
  said plainly, once. No narration of six reviews, no "independent reader
  with this journal's brief". The length argument stays as a measured table.
  The limitations paragraph stays.
- [ ] **6.2 Uploads** (`OWNER-ACTIONS.md` §1.4 and `submission/README.md`):
  manuscript, supplement, `upload/Highlights.txt`, cover letter,
  `response_to_referee.md` (the journal's real report) and a new
  `summary_of_changes.md` (two pages: what changed since that report, by
  section). `response_to_blueprint.md`, `_review21`, `_review23`,
  `_review26`, `_review27` stay in the archive and are not uploaded;
  `check_package.py`'s manifest changes accordingly and `check_claims`
  still scans them.
- [ ] **6.3 AI declaration** (`S9_supplement_back.tex` / back matter macros
  in `round26_numbers.py`): the span is the register's first date
  (2026-08-18) to round 28's last; identifiers named where recorded and
  "not recorded" where not; the three uses named — code, prose, and
  **internal review of the manuscript** — with the model for round 28
  (`claude-fable-5-1`). `AI-USE.md` gains the round-28 row and a row for the
  review use; the declaration reads both from the same macros as now.
- [ ] **6.4 `response_to_review28.md`**: point-by-point against
  `review_round28.md`, in the archive (not uploaded). `check_response_refs`
  covers it.

## 7. Phase 7 — The ten small items (R28.6)

- [ ] 7.1 Table 4 header "misreport rate" → "sign-disagreement rate"
  (`round26_numbers.py` / `master.tex` generator; keep the label
  `tab:misreport` and the macro names).
- [ ] 7.2 `40_multilog.tex:433` "sign-changing or conditionally harmful" →
  the pair and its Definition-3 label, from a macro.
- [ ] 7.3 Response letter (round 27, archived; and the summary of changes):
  the excludes-own-estimate count on the *scalar* family under both schemes,
  beside 74 of 3,900.
- [ ] 7.4 Table 3 header: `axes: pipe/split/qual/adm. rungs`; caption says
  the intercept-only rung is not counted.
- [ ] 7.5 §9.4 replicate/cell counts from macros (`\nCoverageCells`).
- [ ] 7.6 The two 1.35s (Phase 3.2).
- [ ] 7.7 Contribution 2 (Phase 3.1).
- [ ] 7.8 `OWNER-ACTIONS.md` §3 "seven keywords" → six; sweep that file for
  other stale counts against `texlint --report`.
- [ ] 7.9 Reference [11] — owner (Phase 9).
- [ ] 7.10 §4.3 sentence on multiplier vs Romano–Wolf (Phase 3.2).

## 8. Phase 8 — Gates, audit, build

- [ ] 8.1 `make_numbers.py --strict`, `verify_numbers.py`, `round27_verify.py`
  plus the round-28 conditions (1.6, 2.6), `texlint.py`, `check_bands.py`,
  `check_claims.py`, `check_highlights.py`, `check_response_refs.py`,
  `check_sources.py`, `check_package.py`, `build_journal.py` (0 errors, 0
  undefined, 0 overfull), `final_search.py`, `verify_release.py`,
  `s13_attack_numbers.py`, `attack_verifier.py`.
- [ ] 8.2 **The audit pass.** A fresh-context read of the built PDF for
  Sections 4.3, 6.3, 6.4, 8.3, 9.4, 10 and the abstract, looking for the
  three classes that recur: a moved block that points at itself or loses
  its antecedent; a number restated in prose that the table beside it
  contradicts; a concession that the cut removed. Record the count in §10
  whatever it is.
- [ ] 8.3 `check_reproduction.py` once (the container claim is unchanged,
  but the gate must still pass on the rebuilt tree).
- [ ] 8.4 Diff `paper/numbers.tex` against `250e8e8`'s; every changed macro
  appears in §2.5 or is explained in §10's record.

## 9. Phase 9 — Owner items (unchanged from `finalise.py`)

`python scripts/finalise.py` lists them and exits non-zero while any is
open: the Zenodo DOI (`--doi`), the built image's digest
(`--image-digest`), institutional e-mail addresses for the suggested
reviewers, the full postal address, and the push and tag (`v28.0`, not
`v27.0`, once this round is merged). Also: ORCID on the Editorial Manager
profile; Elsevier's `.docx` competing-interest form. The manuscript must not
be submitted with "DOI reserved" in reference [11].

---

## 10. Record of execution

*(newest first after the baseline; per phase: what ran, what it found, what
changed in the paper, what it cost; numbers checked against result files.)*

### 2026-09-04, 01:30 — the length pass, measured

Three passes. Section 9's pointwise simulation is one subsection (its plane
and worlds already live in S9.5 and S6, so nothing was duplicated); §8.1 and
§8.2 merged; §§1, 2, 3, 4, 5, 6, 7 and 10 compressed paragraph by paragraph
with every macro kept; §6.6 a paragraph; §4.1's comparison and §3.4's rules in
the supplement. Article **63 → 57 pages** (body to page 51), source
**21,400 → 18,300 words** with about 600 added for the round's substance.
Gates after the pass: texlint 0, verify_numbers 168 / 41 / 0, build 0 errors.
The 52-page target is not reachable without a protected float or a
concession; `submission/summary_of_changes.md` §4 gives the editor the next
three cuts and their costs. Section renumbering (9.4 → 9.2, 8.3 → 8.2) is
followed in the current package documents; the historical letters keep the
numbers of the versions they answered and are exempt in
`check_response_refs`.

### 2026-09-04, 00:30 — Phases 2 to 8 executed on the second run's decision

`s21_bands.py --operative emp` on `s44_weighted` and `s44_multinomial`;
`check_bands` (eight conditions) clean on `s48w`; `s40`, `s33 --reuse`, `s34`,
`s36 --reuse`, `s42`, `s49` (now computing the empirical quantile on the
admissible curve family: 6.64 [5.73, 9.08] over 246 cells, 2 degenerate
excluded, against the multiplier's 3.57 and the retired widening's 9.33),
`s28`; provenance accepted for each. Six provenance entries were stale or
never accepted before this round (`s22`, `s25`, `s35`, `s44`, `s47`, `s50`);
each was checked against its output's timestamp, and `s35` re-run. Macros
regenerated: 1,415; `texlint` 0 failures; `verify_numbers` 168 macros, 41
conditions (three new round-28 ones), 0 failures after three stale round-27
conditions whose sentences left the article were retired and the operative
critical value's re-derivation was pointed at `q_op`. Build: article 61 pp,
supplement 110 pp, 0 errors, 0 undefined references. Package gates clean;
`final_search` fails only on the DOI placeholder, as it must. The attack
suite reported two cases MISSED because both corrupted files nothing reads
(`s21_regions`, `s04_rules`); re-pointed at `s48w_regions` and
`s34_misreport`, the region case is caught; the rate case needed more, because the
suite regenerates the macros in its copy before verifying, so a corrupted
summary file reproduces itself --- `round21_verify` now re-derives the
all-cells rate from the master surface on every pair (it matches the summary
to 1e-16), and the suite reports 11 of 11 caught.

**Claims-at-risk register, resolved** (multiplier → empirical): resolved
cells 890 → 698; median ρ 0.039 → 0.000; pairs resolving nothing 2 → 8;
resolving anything 17 → 11 (one sign 12 → 9 = 7 + 2; both 5 → 2);
directions withdrawn 5 of 12 → 3 of 9; median resolved per pair 19 → 2;
`madResolvedMedian` 0.0556 → 0.0600 (abstract, highlights);
`misreportPooledResolvedPct` 16.4% → 13.0%; fully restricted cells 38 → 31,
0 disagreeing under both; reference cell unresolved on 14 of 19 (unchanged);
uniformly beneficial 1 → 1, same pair; §6.5 verdicts part company 9 of 19
(unchanged), sub-surface disagreement 1 pair (BPIC19/duration); §8.3 resolved
operating points 18 → 8 (pointwise 24); conditionally harmful before the
minimum share 1 → 2, both withdrawn (0 after). Decomposition, decision-time
ladder, layer ladder, cohort × target, planned contrasts and calibration
screen: unchanged, verified.

**The audit pass** (§8.2) read the built §4.3, §6.3, §8.3, §9.4, §10 and §11
against the files: no number or directional word out of step; two sentences
had been falsified by the new counts before the audit and were caught by the
verifier and by the read (the "one conditionally harmful label" sentence of
§4.6 and S9.4; the master caption's "which is the larger number"), and are
fixed.

### 2026-09-03, 23:55 — the second run decides it: the empirical quantile is operative

Runtime 2,679 s. Calibration with the ratio target: surface family
eps = 0.050, lam = 3.0, fitted ratio **1.25** against the corpus's 1.50
[IQR 1.24, 1.67] — inside, at the edge; curve family eps = 0.050, lam = 4.0,
fitted ratio **1.49** against 2.24 [2.07, 2.55] — **outside**, so the curve
family's numbers carry a transfer caveat. On the matched surface family
(180 × 400): empirical **94.7%** (SE 0.50) under the corpus's tails and
**94.6%** under a non-zero truth; multiplier **91.5%** and **92.6%**;
Gaussian draws 93.7% and 94.3% (the multiplier is the better estimator where
it is derived to be). Rule §1.4: the empirical passes both tests
(thresholds 94.0% and 94.0%), the multiplier fails both → **adopt the
empirical quantile**. Ladder (heavy): multiplier 80.6 / 88.1 / 90.9 / 91.5 /
91.2 at 33 / 80 / 150 / 400 / 1,000 draws — plateaus; empirical 77.8 / 90.8
/ 93.8 / 94.7 / 94.4. Curve families: modal (1,100 × 400) empirical 93.8%
(tails) and 94.3% (non-zero), multiplier 91.3% and 92.1%; case study
(248 × 200) empirical 93.6% and 93.3%, multiplier 91.2% and 90.3%. The
empirical fails the heavy test on the modal curve family by 0.2 points; it
is operative there for consistency and because it is the better of the two,
and the article says it is about a point short on a family whose estimator
ratio under-reproduces the corpus's. Every number above is read from
`results/s41_coverage.csv` and `results/s41_calibration.csv`.

### 2026-09-03, 22:40 — the first re-matched run, and why it is not the one the paper will quote

`s41_bandcoverage.py` re-run with the grid matched to the balanced design
(180 × 400 surface; 1,100 × 400 and 248 × 200 curve families; four regimes;
tails calibrated at 180 × 400 instead of 180 × 80). Runtime 2,446 s. On the
surface family under the corpus's tails: multiplier **94.5%** (SE 0.5),
empirical **94.5%**; under a non-zero truth 94.7% and 94.0%; Gaussian 94.3%
and 93.7%. So the round-27 figure of 91.6% for the multiplier — the paper's
"sharpest limitation", five standard errors short — does not survive
re-matching the calibration to the draw count the corpus runs. **That
flatters the paper, so it was examined rather than adopted**, and it does
not hold up either: in that synthetic family the two estimators coincide
($q_{\mathrm{emp}}/q \approx 1.0$; mean band widths 7.15 against 7.16) where
the corpus's own families disagree by a median 1.50 (surface) and 2.24
(admissible curve cells). The kurtosis fit had chosen a contamination share
of 2% against round 27's 5%, and a 95% quantile of 400 maxima sees a 5%
contamination and not a 2% one — so both the round-27 verdict (undercovers)
and the first round-28 verdict (covers) were decided by a grid choice of the
tail model that the corpus's kurtosis does not constrain. The corpus does
constrain the ratio, directly. The calibration now targets it alongside the
kurtosis (§1.4a), the contamination grid is finer, and the run is repeated.
The first run's files are kept as `results/s41_r28a_*`. Whatever the second
run says, the manuscript must state that its matched families reproduce the
corpus's estimator ratio, or say by how much they miss it.

### 2026-09-03 — baseline

Round-27 tree at `250e8e8`, branch `round27-inference` (= local `main`, 201
commits ahead of `origin/main`, nothing pushed). All gates clean:
`verify_numbers` 166 macros / 38 conditions / 0 failures; `texlint` 0;
`check_package` 19 entries / 0; `check_claims` 6 retired / 0 asserted;
`check_bands` 0 failed; `round27_verify` exit 0; `finalise` 5 owner items.
Article 63 pp, supplement 108 pp. Findings that seeded this plan:
`s41_coverage.csv` has 28 grid cells, none of them (180, 400) under
`nonzero`; `\covMultNonzeroMedian` = 84.3% is the median of the six
`nonzero` `q_mult` rows (0.744, 0.8195, 0.831, 0.8545, 0.8835, 0.905);
`s48w_bands.csv.gz` carries `emp_lo`/`emp_hi` per cell and
`round27_numbers.py` already derives the 698-cell empirical count from
them, so Phase 2 is arithmetic.

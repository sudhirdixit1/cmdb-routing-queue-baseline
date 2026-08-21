# Four choices behind one number — analysis repository

Code, derived results, figures, a pre-registered protocol and a verification
harness for a study of what a recorded field is worth, and of how much that
answer depends on choices the analyst usually leaves implicit.

**Paper:** `paper/iaai27_empty_cmdb.tex` — *Four Choices Behind One Number:
Reporting the Incremental Value of a Recorded Field*. Targeted at *Information
Systems* (Elsevier). The file name is a fossil of the IAAI-27 draft this was
retargeted from and is retained so the version history stays legible.

**Pre-registration:** `PROTOCOL.md`, committed before any corpus result file
existed. `git log --stat` shows that commit adding one file.

**Referee log:** `REFEREE-LOG.md` — twenty-two objections from four
adversarial passes, each with its disposition, including the six dismissed.

**Reproduction:** `REPRODUCE.md`. One command, which now fetches all 23
datasets by DOI and checksums them:

```bash
python scripts/reproduce_all.py
```

---

## What the paper claims

Four things, in the order the paper makes them.

1. **Every choice moves the answer, and the baseline choice removes it.** On
   the BPI Challenge 2014 incident log, item identity is worth **+0.183 AUC**
   against four intake fields, **+0.103 [+0.094, +0.113]** once the group that
   logged the incident is admitted, and **+0.001 [−0.002, +0.003]** once the
   knowledge-article reference is. The previous version declined to admit that
   second field because it could not establish when the value was written; the
   interaction detail file, which we had not obtained, settles where it comes
   from.

2. **The metric and the operating point are choices of the same kind.** On
   identical scores, six defensible instruments put the reduction between
   **43.7% and 60.3%**, and ROC AUC — the number the previous version printed
   — is the smallest of them. Net benefit, read at one operating point, puts
   it between **6.3% and 119.2%** depending on which point, and the item is
   resolvably harmful in a band above the base rate.

3. **A pre-registered protocol over 22 public logs, and a falsified
   generality claim.** The registered rules admit **13** logs across six
   domains; the reduction is resolvably positive on **three**. The claim we
   registered is falsified by its own criterion, and we report the negative
   with the condition that does govern: on 10 of 19 log-target pairs the
   entity is worth nothing to the intake baseline, so there is no value for a
   free field to absorb.

4. **Eleven corrections, reported as results rather than edited away.** Eight
   from earlier rounds; three from the round that produced this version. Two
   of the three are sentences in which every literal was correct and the
   relation asserted between them was not.

---

## What this round withdrew

Recorded here as prominently as the claims, because a repository that
advertises its findings and buries its retractions is doing the thing this
paper is about.

- **The operational factor of 4.3 is gone.** The paper used to report that
  omitting the free field overstates the CMDB's operational value by 4.3×
  at a 5% review capacity. At that capacity 93.1% of what the naive baseline
  nominates comes from a single tied block of 1,944 rows, and reordering rows
  *inside* that block — which changes nothing any model knows — moves the
  naive arm from −26 to +608. A quantity whose sign is set by a tie-break is
  not a measurement. Section 8 is rebuilt on decision curve analysis, where a
  threshold admits or excludes a whole tied block. The replacement figure is
  **1.07** at the threshold where the item is worth most (`r24`, `r23`).

- **A band of thresholds where the item is worth nothing.** Net benefit is
  resolvably *negative* at four grid points between 0.475 and 0.575, reaching
  −16.1 [−23.0, −8.9] per thousand arrivals at p_t = 0.50. Reported in the
  paper and in the limitations (`r23`).

- **A control that bounded one of the two rungs it was for.** The
  shuffled-item encoder null ran on the group-aware rung only; its boosting
  residual is eleven standard errors from zero. Run on both rungs it moves
  the boosting reduction from 47.1% to 50.5% — upward (`r10`).

The mechanism withdrawals from round fifteen — an asymmetry that was an
algebraic identity, and a margin that was a granularity knob — stand.

**Round seventeen withdrew three more, and two of them are a new kind.**

- **An extremum that was the worst of the points we had named.** The paper
  said the group-aware increment turns negative, "reaching −16.1
  [−23.0, −8.9] per thousand at p_t = 0.50". *Reaching* names an extremum.
  The extremum is **−21.1 [−27.7, −14.4] at θ = 0.525**, 31% larger; 0.50 was
  in the list of five thresholds our own table happened to name.

- **A count reported as an interval.** "Resolvably positive at 20 points, in
  a contiguous run from 0.100 to 0.425." Fourteen are in that run; six sit at
  0.675 and above.

  Every literal in both sentences was correct and every one passed the
  checker. What was wrong was the relation the prose asserted between them.
  No check that compares numbers to data can see that class of defect, and
  the suite now carries five corruptions that mutate a relation rather than a
  value.

- **"One Thing We Could Not Establish" is established, and it removes the
  headline.** The previous version could not tell whether the
  knowledge-article reference is available at incident creation, named the
  file that would settle it, and did not obtain it. `Detail_Interaction.csv`
  is in the same public collection: 94,250 of its 147,004 interactions never
  become an incident at all and every one of them carries a knowledge
  reference, so the field is written by the service desk and not by the
  incident process. Admitting it takes item identity from **+0.103 to +0.001
  [−0.002, +0.003]** (`r35`). Two nulls — one matched on cell mass, one
  additionally matched on each cell's distribution over twenty time strata —
  reproduce neither the base AUC nor the collapse (`r35`, `r35b`).

---

## Layout

```
paper/          the manuscript, its figures and its bibliography
scripts/        every analysis, the figure generator, the checker
results/        every derived CSV the scripts produce
figures/        every figure, including ones not in the paper
submission/     highlights, cover letter, CRediT, data availability
data/raw/       the five files the primary analysis reads.  NOT in git.
data/corpus/    the other eighteen, fetched by DOI.  NOT in git; its
                CHECKSUMS.txt IS.
data/normalized/  one parquet per parsed log, so a 728 MB XES is read once
PROTOCOL.md     the pre-registration
REFEREE-LOG.md  four adversarial passes, 22 objections, every disposition
Dockerfile      a pinned environment, including BLAS thread counts
requirements.lock  every dependency by version AND artefact hash
```

### Scripts that matter

| file | role |
|---|---|
| `common.py` | loaders for the three logs, missing-token handling, paths |
| `r4_final.py` | **the canonical loader.** Cohort, split, estimator, baselines. Everything else does `import r4_final as M` |
| `r10_estimators.py` | three estimator families; the encoder null, on both rungs |
| `r11_operational.py` | target thresholds; the tie census |
| `r20_second_org.py` | the second organisation |
| `r21_referee_round15.py` | round-15 findings; the resolution ladder; field determinism |
| `r22_intercase.py` | congestion features; the central-desk contrast |
| `r23_decision_curve.py` | net benefit — the instrument section 8 now uses |
| `r24_tiefree.py` | the tie decomposition that withdrew the capacity factor |
| `r25_figures.py`, `r39_figures.py` | the ten journal figures |
| `base14.py` | `r4_final`'s cohort in 5 s rather than 90, by executing that file's own source up to the line that builds it |
| `fetch_corpus.py` | 23 files, 7 domains, by DOI, with checksums |
| `r30_instrument_matrix.py` | six instruments; the cost-ratio identity |
| `r31_why_instruments_disagree.py` | aggregation, degeneracy, calibration, tie conventions |
| `r32_corpus.py` | streaming XES parser; the attribute inventory |
| `r33_generic_ladder.py` | the pre-registered ladder over 13 logs |
| `r34_layers_and_history.py` | layer hierarchies; the outcome-history control |
| `r35_interaction_file.py` | the file section 12 said would settle it |
| `r36_population_ablation.py` | the population curve, three regimes |
| `r37_free_text.py` | the free-text search: 596 attributes, zero hits |
| `r38_era_sensitivity.py` | the era limitation as four measurements |
| `verify_paper.py` | recomputes every number in the paper |
| `attack_verifier.py` | the checker's own regression suite |
| `reproduce_all.py` | all of the above, in order, one command |
| `build_journal.py` | the elsarticle build |
| `texlint.py` | structural LaTeX lint; `--fix` repairs row terminators |

### Scripts that are dead weight, named exactly

Nothing in the paper depends on any of these, and none of them is run by
`reproduce_all.py`. They are listed rather than deleted so the withdrawals
stay auditable — and listed by name, because "some of the older scripts" is
the kind of vagueness this project is about.

- **Withdrawn analyses:** `e1`–`e16`, `r1_rabobank_core.py`, `r3_final.py`,
  `r7_final.py`. `r7_final.py:124-148` prints a conclusion its own output CSV
  contradicts; it is kept deliberately as the record of a control that
  failed.
- **Superseded figure scripts:** `figures.py`, `figures2.py`,
  `r2_figures.py`, `r3_figures.py`, `r5_figures.py`, `r9_figures.py`,
  `r14_figures.py`. `r4_figures.py` and `r9_figures.py` still generate the
  conference-era `figG*` artwork into `figures/`; the journal manuscript
  uses `figJ*` from `r25_figures.py` and nothing else.
- **One-shot patch scripts from earlier rounds:** `patch_paper.py`,
  `patch_refs.py`, `patch_verifier.py`, `patch_verifier2.py`. They edited
  files that have since been rewritten; running one now would do damage.
- **A withdrawn side analysis:** `build_matrix.py`, `verify_matrix.py`, and
  the two `capability_readiness_matrix*.xlsx` workbooks they read. Kept on
  disk, out of version control.

`common.py`, `texnum.py` and `texlint.py` are **not** dead weight despite
their age; the verifier imports all three.

An early draft of `r14_scope.py` repeated `r7`'s defect — it printed an
explanation for a curve feature that its own table refuted — and was
rewritten. If you are adding a script, print only what your output supports.

---

## Verification

Current state:

```
934 checks passed, 0 failed
417 literals in body; 0 unaccounted; 405 compared against data
198 caught, 0 missed, 0 skipped of 198
```

`verify_paper.py` compares every numeric literal in the paper against a value
computed from a result file or recomputed from the raw data, requires each to
appear within an anchor phrase, and fails if any literal in the body is
unaccounted for. `attack_verifier.py` is its regression suite: 198
corruptions.

### Be precise about what that buys

It guards **numbers** thoroughly and **prose** only where a guard was written
by hand. There is no general coverage of non-numeric assertions and this file
will not imply otherwise. All eleven corrections the paper reports are claims
about what a number *means*, and the checker would have caught none of them.

Round seventeen's suite made that concrete. Three corruptions landed on the
first run of the enlarged suite and all three were prose: softening "It is
falsified" to "It is largely supported"; reversing "the headline does not
survive our own admissibility criterion"; and swapping the two ends of a
three-way population comparison, where both values stay checked and only
their attribution moves. Each is now guarded, and the general point is that
the guard list is a list — it grows one defect at a time and nothing on it
was foreseen.

### Rules, all learned the hard way

- `ck()` tests rounding **equality** at the paper's printed precision, not a
  tolerance. A `6e-4` tolerance on three-decimal literals let three wrong
  last digits through while the suite reported "0 failed".
- A range endpoint **floors or ceils**; it does not round. Use `ck_bound()`.
  Three ranges shipped rounded inward, each narrower than the data supports.
- Anchoring alone cannot separate two values that share a sentence. Any
  ordered pair needs a `ck_phrase(...)` pin, or a reviewer can swap them
  undetected.
- `ck_phrase(...)` pins **position**, not value. Every literal it names must
  also have its own `ck(...)`. A literal accounted for by a phrase alone is a
  failure — that gap put a discredited figure in the abstract, contradicting
  the paper's own table, for a full revision cycle.
- Load-bearing caveats are checked with `ck_phrase(...)` too. Deleting one
  leaves every number correct and the claim wrong. `RISKY` is a hand-curated
  list of about twenty constructions; anything not on it stays unguarded, and
  a reversal of one of those will still pass.
- **Coverage is literal-level, not window-level** (round sixteen). A check
  vouches for the number it compared, at the positions where that number
  appears in its window, and for nothing else. It used to vouch for the whole
  400-character window, which let an audit append `confirmed on $10$
  independent extracts` to a checked sentence and pass. That was the one
  corruption in the suite that had never been caught; it is caught now.
- **A number spelled out in letters is still a number** (round sixteen). The
  corrections section says "Eight errors of our own"; the tokeniser only sees
  digits, so "Six" passed. The word is now parsed and compared against the
  length of the list it describes.
- **The `RISKY` match is case-insensitive** (round sixteen). It was not, so
  every load-bearing construction that begins a sentence — "We withdraw…",
  "We exclude…" — escaped the guard. Making it case-insensitive immediately
  surfaced a sentence that had been unguarded for eight rounds.
- **A count the paper spells out is compared to the data** (round seventeen).
  `ck_word()` generalises the bespoke fix round sixteen put on the corrections
  count. "Six instruments rather than seven", "three bands", "five incidents"
  — each is now compared to the number the result file produces.
- **The census runs last, and the file lints itself to keep it there** (round
  seventeen). This is the *second* time the coverage census has been outrun by
  checks written below it. Moving the block is not a fix for a hole whose
  cause is order: `_lint_check_order()` reads `verify_paper.py`'s own source
  and fails if any check **call** appears after the census call site.
- **Retiring a check is explicit and safe only because of coverage** (round
  seventeen). Forty-two checks whose anchoring sentence no longer exists sit
  in a `RETIRED` set naming the claim that went. That is safe only because a
  literal freed by a retirement and not re-checked becomes unaccounted and the
  run fails. Never retire a check because it fails — and note that a
  retirement can unguard PROSE it was not retired for, which is how the suite
  caught one this round.
- If you add a claim, add a `ck(...)` with an anchor **and** a corruption to
  `attack_verifier.py`. The suite is what found every hole the verifier has
  had — three in round sixteen and three more in round seventeen, all six
  written *after* a fix looked complete. Write the corruption before you
  believe the check.

---

## The datasets

Twenty-three files across seven domains, all public, none redistributed here.
`python scripts/fetch_corpus.py` resolves every DOI, downloads every file and
records a SHA-256 for each in `data/corpus/CHECKSUMS.txt`, which is tracked.
`REPRODUCE.md` §2 gives the identifiers, the filenames, and the two
file-format traps that have each cost a debugging session.

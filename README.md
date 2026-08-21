# Identity, not attributes — analysis repository

Code, derived results, figures and a verification harness for a study of
what configuration data contributes to incident prediction, on two public
ITSM event logs.

**Paper:** `paper/iaai27_empty_cmdb.tex` — *Identity, Not Attributes: What
Configuration Data Contributes to Incident Prediction in Two Organisations*.
Targeted at *Information Systems* (Elsevier). The file name is a fossil of
the IAAI-27 draft this was retargeted from and is retained so the version
history stays legible.

**Reproduction:** `REPRODUCE.md`. One command:

```bash
python scripts/reproduce_all.py
```

---

## What the paper claims

Three things, in the order the paper makes them.

1. **Identity, not attributes, and not at instance level.** On the BPI
   Challenge 2014 incident log, a 256-way service-component grouping captures
   three quarters of what instance-level configuration-item identity is worth
   for predicting reassignment, and instance identity adds **+0.023 AUC**
   over it. A per-item outcome rate applied as a lookup — no model, no
   configuration attribute of any kind — reaches **0.744** against the full
   model's **0.748**. What the CMDB supplies on this task is a stable key
   under which outcome history accumulates.

2. **The measured value is set by a field-admission decision.** Item identity
   is worth **+0.183 AUC** against four intake fields and **+0.103
   [+0.094, +0.113]** once one further field the organisation already records
   is admitted — the group that logged the incident. The reduction runs
   **36.1% to 48.3%** across the design space, survives the admission of four
   free creation-time congestion features, and replicates on a second
   organisation, tool and country (BPI Challenge 2013, Volvo IT).

3. **Eight corrections, reported as results rather than edited away.** Six
   from earlier rounds; two from the round that produced this version. Both
   of the new ones removed a claim the previous version made.

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

---

## Layout

```
paper/          the manuscript, its figures and its bibliography
scripts/        every analysis, the figure generator, the checker
results/        every derived CSV the scripts produce
figures/        every figure, including ones not in the paper
submission/     highlights, cover letter, CRediT, data availability
data/raw/       the three public logs.  NOT in version control.
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
| `r25_figures.py` | the five journal figures |
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
674 checks passed, 0 failed
325 literals in body; 0 unaccounted; 313 compared against data
149 caught, 0 missed, 0 skipped of 149
```

`verify_paper.py` compares every numeric literal in the paper against a value
computed from a result file or recomputed from the raw data, requires each to
appear within an anchor phrase, and fails if any literal in the body is
unaccounted for. `attack_verifier.py` is its regression suite: 149 corruptions.

### Be precise about what that buys

It guards **numbers** thoroughly and **prose** only where a guard was written
by hand. There is no general coverage of non-numeric assertions and this file
will not imply otherwise. All eight corrections the paper reports are claims
about what a number *means*, and the checker would have caught none of them.

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
- If you add a claim, add a `ck(...)` with an anchor **and** a corruption to
  `attack_verifier.py`. The suite is what found every hole the verifier has
  had — three of them in round sixteen alone, two of those written *after*
  the first fix looked complete. Write the corruption before you believe the
  check.

---

## The datasets

All three are public; none is redistributed here. `REPRODUCE.md` §2 gives the
identifiers, the filenames, and the two file-format traps that have each cost
a debugging session.

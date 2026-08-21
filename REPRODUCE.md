# Reproducing every number in the paper

One command reproduces the whole result set from the raw logs. Everything
else in this file exists so that when it fails, you can tell why.

```
python scripts/reproduce_all.py
```

That runs every analysis in dependency order, regenerates every
`results/*.csv` and every figure, rebuilds the PDF, verifies each numeric
literal in the manuscript against a value computed from data, and runs the
verifier's own corruption suite. It exits non-zero on the first failure.

Expected end state, on the environment pinned in `requirements.txt`:

```
674 checks passed, 0 failed
325 literals in body; 0 unaccounted; 313 compared against data
149 caught, 0 missed, 0 skipped of 149
0 errors, 0 undefined references, 33 pages
```

---

## 1. What you need

**Python 3.10.0** and the exact versions in `requirements.txt`. The pins are
not decoration: `scikit-learn` 1.7.2's `TargetEncoder` and
`HistGradientBoostingClassifier` defaults both moved in the release series
around it, and the figures were computed on `matplotlib` 3.10.5.

```
python -m venv .venv
.venv\Scripts\activate          # Windows;  source .venv/bin/activate elsewhere
pip install -r requirements.txt
```

**A TeX distribution providing `pdflatex` and `bibtex`**, only if you want
the PDF. `scripts/build_journal.py` looks on `PATH` and then in the usual
MiKTeX locations on Windows. The document uses `elsarticle`, which is on
CTAN; MiKTeX installs it on first use.

**Roughly 20 GB of RAM is not required.** The heaviest step fits one-hot
logistic regressions over 31,818 rows and about 2,600 sparse columns.

---

## 2. The three datasets

None is redistributed here. Fetch each from its persistent identifier and
put the named files in `data/raw/`.

| File | Collection | Identifier |
|---|---|---|
| `Detail_Incident.csv` | BPI Challenge 2014 | `doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35` |
| `Detail_Incident_Activity.csv` | BPI Challenge 2014 | same |
| `Detail_Change.csv` | BPI Challenge 2014 | same |
| `BPI_Challenge_2013_incidents.xes.gz` | BPI Challenge 2013 | `doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee` |
| `incident_event_log.zip` | UCI 498 | `doi:10.24432/C57S4H` |

`data/` is gitignored. Nothing in this repository contains a row of any of
them.

**Two file-format traps**, both of which have cost a debugging session:

- The BPIC 2014 CSVs are semicolon-delimited and **latin-1** encoded, not
  UTF-8. `common.py` and `r4_final.py` open them that way. A UTF-8 read
  fails on the accented characters in a handful of free-text fields.
- `Detail_Incident.csv` timestamps are `%d/%m/%Y %H:%M:%S` and the activity
  file's are `%d-%m-%Y %H:%M:%S`. Different separators, same collection.
  Both loaders pass `dayfirst=True`; without it pandas silently reads
  `03/04/2014` as March.

---

## 3. Runtimes

Measured on a 14-core Windows laptop, Python 3.10.0, one script at a time.
`r4_final.py` executes its whole analysis at import, so every script that
does `import r4_final as M` re-runs it; that import is most of the fixed
cost below.

| Step | Approximate wall clock |
|---|---|
| `r4_final.py` | 4 min |
| `r5_final.py`, `r6_final.py`, `r8_final.py` | 4–6 min each |
| `r9_second_task.py`, `r10_estimators.py` | 8–12 min each |
| `r11`, `r12`, `r13`, `r14`, `r16`, `r17`, `r18`, `r19` | 4–8 min each |
| `r20_second_org.py` | under 1 min (no `r4` import) |
| `r21_referee_round15.py` | 15–20 min (150 model fits in section B) |
| `r22`, `r23`, `r24` | 6–10 min each |
| `r25_figures.py` | seconds (reads result files only) |
| `verify_paper.py` | 1–2 min |
| `attack_verifier.py` | **40–70 min** (one full verifier run per corruption) |
| `build_journal.py` | under 1 min |

`reproduce_all.py` runs the independent scripts in parallel and takes about
45 minutes to reach the verifier, plus the corruption suite.

---

## 4. Determinism

Every sampling script seeds from a single constant, `SEED = 20260819`, and
every bootstrap, permutation null and Monte-Carlo draw derives its generator
from it. Re-running produces the same figures to the last printed digit, on
the same library versions.

Three things will change the numbers, and all three are the environment
rather than the analysis:

- **A different `scikit-learn`.** `TargetEncoder`'s smoothing and
  `HistGradientBoostingClassifier`'s early-stopping split are both version
  sensitive.
- **A different BLAS, or the same BLAS with a different thread count.**
  `lbfgs` converges to the same optimum but not to the same last bit, and the
  reduction order in a threaded matrix product is not fixed. Observed
  directly while preparing this version: running `r10_estimators.py` with
  `OMP_NUM_THREADS=2` and again with `OMP_NUM_THREADS=3` moved one bootstrap
  percentile from `+0.0937` to `+0.0938`. Nothing the paper prints changed,
  because those two round to the same three-decimal literal — but a value
  sitting on a rounding boundary would have. If you need bit-identical
  output, set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS`
  to the same value on every run.
- **A different pandas.** Grouped-transform ordering affects which row a
  permutation lands on inside `r21`'s within-item shuffles.

If your figures differ in the third decimal, check the versions before
suspecting the analysis. If they differ in the second, do not.

---

## 5. What the checker does, and what it does not

`scripts/verify_paper.py` is the artifact this repository is really about.

**What it does.** It tokenises the manuscript once into numeric literals,
compares each against a value computed from a result file or recomputed from
the raw data, requires each to appear within an anchor phrase that ties it to
the sentence making the claim, and fails if any literal in the body is
unaccounted for. Membership is exact set membership, never substring.
Comparison is rounding equality at the paper's own printed precision, not a
tolerance. Range endpoints floor or ceil rather than round. Coverage is
**occurrence-level and literal-level**: a check vouches for the number it
compared, at the positions where that number appears in its window, and for
nothing else — so a fabricated figure inserted next to a checked one is
uncovered and fails.

**What it does not do.** It guards numbers thoroughly and prose only where a
guard was written by hand. `RISKY` in that file is a curated list of about
twenty directional and modal constructions — "lower bound", "we exclude",
"only the trend" — and a sentence containing one must be pinned verbatim by
a `ck_phrase` or declared with a reason. **There is no general coverage of
non-numeric assertions.** A referee once wrote twenty corruptions of
*unguarded* qualifications and fifteen passed, including flipping "a lower
bound" to "an upper bound", which reverses the paper's central interpretive
claim. When you add a qualification the argument leans on, add its guard by
hand; nothing will remind you.

It also cannot tell you that an interpretation is sound. The paper reports
eight corrections; **all eight are claims about what a number means, and the
checker would have caught none of them.**

`scripts/attack_verifier.py` is the checker's regression suite: 149
corruptions drawn from defects found in earlier versions of this work. Run it
after any change to the verifier. If you add a claim, add a `ck(...)` with an
anchor **and** a corruption; the suite is what found every hole the verifier
has had.

---

## 6. Dependency order

`reproduce_all.py` encodes this; it is written out here so a partial re-run
is possible.

```
common.py
└── r4_final.py                    the canonical loader: cohort, split, fit
    ├── r5_final.py                nulls, mutation sensitivity
    ├── r6_final.py                gains with pooled uncertainty
    ├── r8_final.py                mechanism, design space, scoping
    ├── r9_second_task.py          the ladder on two further targets
    ├── r10_estimators.py          three estimator families; encoder nulls
    ├── r11_operational.py         target thresholds, tie census
    ├── r12_queue_from_item.py     model-free queue/item relationship
    ├── r13_queue_shape.py         concentration, the one-bit contrast
    ├── r14_scope.py               split-averaged scoping curve
    ├── r16_field_semantics.py     what the Open-row group actually is
    ├── r17_mechanism_floor.py     the floor, at item level
    ├── r18_referee_round2.py      MI nulls, other free fields
    ├── r19_shrinkage_ci.py        intervals on the REDUCTION
    ├── r22_intercase.py           congestion; the central-desk contrast
    ├── r23_decision_curve.py      net benefit                    [needs r11]
    ├── r24_tiefree.py             the tie decomposition
    └── r21_referee_round15.py     round-15 findings   [needs r10, r11, r12,
                                                        r14, r18]
r15_why_one_org.py                 three public logs   [needs all three files]
r20_second_org.py                  the second organisation   [BPIC 2013 only]
r25_figures.py                     the journal figures  [reads results only]
verify_paper.py                    [needs every result file above]
attack_verifier.py                 [needs verify_paper.py to pass first]
build_journal.py                   [needs paper/ and a TeX distribution]
```

Scripts `e1`–`e16`, `r1`–`r3` and `r7` are superseded. They implement
analyses withdrawn during review and are retained only so the withdrawals
are auditable. Nothing in the paper depends on them. `r7_final.py:124-148`
prints a conclusion its own output contradicts; it is kept deliberately as
the record of a control that failed.

---

## 7. If a number does not match

In order of likelihood:

1. **Check the library versions first.** See §4.
2. **Check that all five raw files are present**, including
   `Detail_Change.csv`, which nothing in the paper uses but `common.py`
   references, and the two logs needed by `r15`.
3. **Check the cutoff.** `r4_final.CUTOFF` is `2013-10-01`.
   `r21_referee_round15.py` mutates it to sweep cleaning cutoffs and restores
   it; if you interrupt that script mid-sweep in an interactive session, the
   module global is left at the wrong value.
4. **Re-run the producing script, not the verifier.** The verifier reads
   `results/*.csv`; a stale CSV from an interrupted run will make it fail
   against a paper that is correct.

If a number in the paper and a number in a result file disagree and you
cannot tell which is right, the result file is right and the paper is wrong.
That has been true six of the eight times it has come up here.

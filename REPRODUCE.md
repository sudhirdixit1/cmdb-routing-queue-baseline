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
pip install --require-hashes -r requirements.lock
```

`requirements.lock` pins every dependency by version **and** by the SHA-256 of
every artefact PyPI serves for it, so `--require-hashes` refuses a different
build of the same version. `requirements.txt` still lists the five direct
dependencies for a reader who only wants to look. Regenerate the lockfile with
`python scripts/make_lockfile.py`.

**Or run the container**, which additionally pins the thread counts §4 says
move a bootstrap percentile:

```
docker build -t emptycmdb .
docker run --rm -v "$PWD/data:/work/data" -v "$PWD/results:/work/results" \
           -v "$PWD/figures:/work/figures" emptycmdb
```

The data directory is mounted rather than baked in: nothing in this repository
redistributes anybody's data.

**A TeX distribution providing `pdflatex` and `bibtex`**, only if you want
the PDF. `scripts/build_journal.py` looks on `PATH` and then in the usual
MiKTeX locations on Windows. The document uses `elsarticle`, which is on
CTAN; MiKTeX installs it on first use.

**Roughly 20 GB of RAM is not required.** The heaviest step fits one-hot
logistic regressions over 31,818 rows and about 2,600 sparse columns.

---

## 2. The datasets

None is redistributed here, and none has to be fetched by hand:

```
python scripts/fetch_corpus.py          # 24 files, 7 domains, by DOI
python scripts/fetch_corpus.py --list   # the manifest, no network
```

`fetch_corpus.py` resolves each dataset's DOI through the 4TU.ResearchData API,
downloads the named file, and records its SHA-256 in
`data/corpus/CHECKSUMS.txt`, which **is** tracked in git. On every later run the
checksum is verified and an unchanged file is skipped, so a reader can assert
that the corpus they have is the corpus the paper was written against.

The checksums cannot be pinned in advance: they are recorded on first download
and verified from then on. A checksum a reader cannot independently obtain
proves nothing, and the DOI is the citable identifier.

The five files below are the ones the primary analysis needs and are read from
`data/raw/`; the other eighteen land in `data/corpus/` and are used only by the
corpus sections.

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
| `r25_figures.py`, `r39_figures.py` | seconds each (read result files only) |
| `verify_paper.py` | 1–2 min |
| `attack_verifier.py` | **40–90 min** (one full verifier run per corruption) |
| `build_journal.py` | under 1 min |

Round seventeen's scripts, which do not import `r4_final` and therefore skip
its fixed cost — `base14.py` executes `r4_final`'s source up to the line that
builds the cohort and stops, which is 5 seconds rather than 90:

| Step | Approximate wall clock |
|---|---|
| `fetch_corpus.py` | 2–4 min for 1.0 GB, network permitting |
| `r30_instrument_matrix.py` | 1–2 min |
| `r31_why_instruments_disagree.py` | seconds |
| `r32_corpus.py` | 3–5 min (parses a 728 MB XES once and caches it) |
| `r33_generic_ladder.py` | **9–12 min** (13 logs, both targets, every g) |
| `r33b`, `r33c` | under 1 min each |
| `r34_layers_and_history.py` | under 1 min |
| `r35_interaction_file.py` | 1–2 min |
| `r35b_temporal_null.py` | 1–2 min |
| `r36_population_ablation.py` | **9–10 min** (19 ladders, each bootstrapped) |
| `r37_free_text.py` | under 1 min |
| `r38_era_sensitivity.py` | under 1 min |

`reproduce_all.py` writes a per-script table to `logs/runtimes.csv` and prints
the six slowest. **A measured full run: 43 minutes** on a 14-core Windows
laptop with `--jobs 4`, from a populated `data/`, through nine waves, the
figures, the verifier and the build. Add two to four minutes for the fetch
stage from cold, and 60 to 100 minutes for the corruption suite. The slowest
six on that run were `r5_final` (8.3), `r36_population_ablation` (8.2),
`r33_generic_ladder` (7.9), `r9_second_task` (7.6), `r8_final` (5.5) and
`r10_estimators` (5.2).

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

It also cannot tell you that an interpretation is sound. **Three of the
twelve corrections this paper reports are sentences in which every literal was
correct** — the extremum that was the worst of the points we had named, the
count identified with an interval, and the range across the operating range
that was the range across five named thresholds — and no check that compares
numbers to data can see any of them. The checker now compares each named
extremum against the extremum and each stated count against the run length,
which closes those three instances and not the class.

**The third was found by something outside the checker.** `r46_tool_agreement.py`
re-derives the paper's headline surface through `fieldvalue`, the package
shipped with the paper, and on its first run it printed a range the paper's
own prose contradicted. That is worth stating plainly: after eighteen rounds
and 1,358 checks, the defect was found by computing the same quantity a second
way, not by checking the first way harder.

`ck_word` is new in this version: a count the paper spells out in letters is
compared to the data that produces it. Round sixteen's suite showed that
"Eight errors of our own" could be changed to "Six" and pass, because the
tokeniser only sees digits.

**Two more holes, both opened by adding material rather than by editing
code.** `texnum.body_of` used to cut the paper at `\bibliographystyle`, which
was a convenient end-marker in a document with no appendix. The moment round
eighteen moved five subsections and added five more into an `\appendix` —
which in this document sits after the bibliography commands — **every number
in ten appendices became invisible to the checker**, and 870 checks failed
against text sitting in the file. The body now runs to `\end{document}` and
the two bibliography commands are removed individually. Separately, `ck_word`
was the one check family that never consulted the `RETIRED` set, so a retired
word-count went on failing after its sentence had gone; a retirement that does
not retire is worse than none, because the failure looks like a real defect
and invites someone to change the paper.

**The census runs last, and this file lints itself to keep it there.** The
unaccounted-and-coverage census was outrun twice: round sixteen found it
sitting halfway down the file, invisible to the checks below it, and moved it;
round seventeen appended two hundred checks below where it had been moved to
and the coverage half silently stopped seeing them. Moving a block does not
fix a hole whose cause is order. It is now a function called once at the end,
and `_lint_check_order()` reads `verify_paper.py`'s own source and fails if any
`ck`/`ck_bound`/`ck_phrase`/`ck_word` **call** appears after that call site.
The guard-or-declare lint turned out to have the same bug for the same reason
and is now called from the same block; the self-lint names both call sites.

`scripts/attack_verifier.py` is the checker's regression suite: 243
corruptions drawn from defects found in earlier versions of this work,
including fourteen that mutate a *relation* rather than a value — nine of them
added in round eighteen — because that is the class three of the corrections
belong to. A relation corruption leaves every literal in the paper correct and
sitting in a correct place, and changes only the word joining two of them: the
suite reorders the three logs' spreads, swaps the simulation's bias and
standard deviation columns, exchanges the two axes the audit reports, and
restates the corrected operating range as the two named thresholds it used to
be. Run it after any change to the
verifier. If you add a claim, add a `ck(...)` with an anchor **and** a
corruption; the suite is what found every hole the verifier has had.

---

## 5b. What round eighteen added, and what each stage needs

| stage | what it needs | what it writes |
|---|---|---|
| `r40_audit.py` | the network, once; then `data/audit/` | the frame, the funnel, the coding sheet, the proportions |
| `r41_propositions.py` | nothing at all | the three constructions, executed and asserted |
| `r42_holdout_fetch.py` | the network; two DOIs | the held-out logs, with checksums, and the 4TU census |
| `r43_holdout_test.py --fit` | `r33b_table.csv` and the r32 caches | the two frozen thresholds |
| `r43_holdout_test.py` | the held-out logs | the prospective test's confusion matrix |
| `r44_axes_multilog.py` | the r32 caches | the four-axis surface on three logs |
| `r45_simulation.py` | nothing at all | the estimator against a known answer |
| `r46_tool_agreement.py` | `r30_instruments.csv`, `fieldvalue` | 20 quantities, two code paths |
| `r47_signature_figure.py` | `r44_surface.csv` | the signature figure and its caption |
| `r48_venue.py` | the network | the venue counts |
| `python -m pytest fieldvalue` | nothing | 91 tests |
| `examples/worked_example.py` | the network, once | the surface on UCI Adult |

**The order between `r43 --fit` and `r43` is the claim, not a convenience.**
`--fit` reads only round-seventeen results; the second call opens the held-out
logs. `reproduce_all.py` runs them in that order in a stage of its own.

**Three stages need the network and cache what they fetch**, so a second run
is offline: the audit's full texts, the held-out logs, and the venue counts.
Nothing is redistributed here.

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

base14.py                          r4_final's cohort in 5 s, not 90
├── r30_instrument_matrix.py       the six instruments
├── r31_why_instruments_disagree.py    the three mechanisms  [needs r30's grid]
├── r35_interaction_file.py        the settled section 12
├── r35b_temporal_null.py          the time-profile-matched null   [needs r35]
├── r36_population_ablation.py     the population curve
└── r38_era_sensitivity.py         the four era axes    [needs r36's curve]

r32_corpus.py                      parses 22 logs once, caches parquet
└── r33_generic_ladder.py          the pre-registered corpus ladder
    ├── r33b_discriminate.py       the prediction attempt
    ├── r33c_headroom.py           the exclusion-rule sensitivity
    ├── r34_layers_and_history.py  layers; the outcome-history control
    └── r37_free_text.py           the free-text search
r25_figures.py, r39_figures.py     the journal figures  [read results only]
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

## 6b. If a script does not run

`reproduce_all.py`'s preflight `ast.parse`s every file in `scripts/` and
refuses to start if any fails. That check exists because
`r6_final.py` did not parse for thirteen rounds and the failure only surfaced
thirty minutes into wave 2 of a full run --- an f-string expression split
across four adjacent string literals, each of which is parsed on its own.

The three things that made it survive thirteen rounds are worth knowing before
you trust any part of this apparatus:

- **A checker that reads a pipeline's output cannot see a pipeline script that
  never runs.** `verify_paper.py` passed 936 checks against `r6_gains.csv`
  while the script that writes it could not be parsed.
- **Cached result files hide it.** `results/r6_*.csv` were an hour older than
  the break and were still correct, so nothing downstream complained.
  Re-running the repaired script produced byte-identical files.
- **Writing a reproduction script is not reproducing.** The round that wrote
  `reproduce_all.py` documented it and cited it in the manuscript without
  running it to completion.

If you change a script, run `python scripts/reproduce_all.py --only analysis`
before you trust anything downstream of it.

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

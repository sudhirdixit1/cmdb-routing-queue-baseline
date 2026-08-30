# Reproducing this paper

One command:

```bash
python scripts/reproduce_all.py
```

It fetches every dataset by DOI, checksums what it downloaded, runs every
analysis in dependency order, regenerates every number and every table in the
manuscript from the results, rebuilds the figures, runs the verification
harness and its corruption suite, and builds the PDF. Nothing in
`results/`, `paper/numbers.tex` or `paper/tables/` is hand-edited; if a number
in the manuscript disagrees with a result file the build fails.

---

## 1. Environment

Python 3.10. Two ways to get the exact environment the results were produced
in.

```bash
# a) the lockfile: every transitive dependency pinned by artefact hash
python -m pip install --require-hashes -r requirements.lock

# b) the container: also pins the BLAS thread count, which changes the last
#    digit of a bootstrap quantile if it is left free
docker build -t specsurface .
docker run --rm -v "$PWD:/work" specsurface python scripts/reproduce_all.py
```

`requirements.txt` is the human-readable list; `requirements.lock` is what a
reproduction should install.

**Thread counts matter.** Every script that runs a process pool sets
`OMP_NUM_THREADS=1` and its four siblings before importing numpy, because the
pool parallelises over tasks and the gradient-boosting learner parallelises
over threads. With both free, a fit that takes 3 seconds alone took 8 in the
pool, and a run that should take 35 minutes took four hours. The container
pins the same variables.

## 2. Data

Nothing is redistributed. Every dataset is public and is fetched from its DOI:

| dataset | DOI | used for |
|---|---|---|
| BPI Challenge 2014 | `10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35` | the case study, and one corpus log |
| BPI Challenge 2013, incidents | `10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee` | a corpus log |
| Incident management process enriched event log | `10.24432/C57S4H` | a corpus log |
| the further public event logs | see `data/corpus/CHECKSUMS.txt`, which lists every file with its SHA-256 | the corpus, the held-out set, and the logs the registered rules exclude |

```bash
python scripts/fetch_corpus.py       # resolves each DOI, downloads, checksums
```

The checksums are compared against `data/corpus/CHECKSUMS.txt`, which is
tracked. A mismatch stops the run: an analysis on a file that is not the file
the paper was written against is not a reproduction.

The practice pilot's full texts are other publishers' PDFs. They are not in
the archive. `python scripts/s06_audit2.py --fetch` re-retrieves them from the
open-access locations recorded for each DOI in `results/s06_sample.csv`, and
`--dossiers` rebuilds the evidence packets each adjudication was made from,
deterministically.

## 3. The stages, and what each costs

| stage | scripts | wall clock |
|---|---|---|
| fetch | `fetch_corpus.py` | 10–40 min, once, network-bound |
| analysis, earlier rounds | `e*.py`, `r*.py` | ~45 min |
| the master surface | `s01_surface.py` | ~35 min on 12 cores |
| the nested bootstrap | `s02_boot.py` | ~2 h on 12 cores |
| the propositions | `s07_props.py` | ~5 min |
| the simulation | `s10_simulation2.py` | ~25 min on 12 cores |
| decision times | `s08_decision_time.py` | ~30 min |
| the intervals, recentred | `s17_intervals.py` | ~20 s, reads s02's draws |
| decomposition, regret | `s03_decompose.py`, `s04_regret.py` | ~2 min |
| the pilot | `s06_audit2.py` | ~20 min, network-bound, cached |
| the noisy-world arms | `s18_bias_scaling.py` | ~1 min on 10 cores |
| **the inference surface** | `s20_boot2.py` | **4-6 h**, see below |
| **whole-surface bands** | `s21_bands.py` | ~3 min, reads s20's draws |
| **the corrected ANOVA** | `s22_anova.py` | ~5 min |
| **regret on a coherent scale** | `s23_regret.py` | ~1 min |
| **the planned contrasts** | `s24_confirm.py` | ~40 min on 12 cores |
| **the denominator audit** | `s25_denominator.py` | ~2 min |
| **calibration and decision curves** | `s26_calib_dca.py` | ~50 min |
| **register-quality curves** | `s27_quality.py` | ~30 min |
| **the propositions, round twenty** | `s29_props.py` | ~4 min |
| **the pilot's design-based variance** | `s30_pilot_var.py` | ~20 s |
| **the simulation at full size** | `s31_simboost.py` | **5-7 h**, see below |
| numbers, tables, claim registry | `make_numbers.py`, `assemble_paper.py`, `claim_registry.py` | seconds |
| figures | `s12_figures.py`, `s28_figures.py` | ~2 min |
| verification | `verify_numbers.py`, `verify_paper.py` | ~2 min |
| corruption suite | `s13_attack_numbers.py` | ~1 min |
| PDF | `build_journal.py` | ~1 min |

`s17_intervals.py` must run **after** `s02_boot.py` and **before**
`s03_decompose.py`: it recomputes every interval and band from s02's stored
draws using the basic (pivotal) construction, and s03 labels the resolution
regions from those bands. `reproduce_all.py` already orders them this way.

### The round-twenty chain, and why `s20_boot2.py` dominates it

`s20_boot2.py` computes the **inference surface**: a nested moving-block
bootstrap in which every draw refits the entire pipeline over an
axis-complete sub-grid of the declared design space. Its cost is therefore the
cost of the declared surface multiplied by the draw count, and on the machine
these results were produced on --- an Intel Core Ultra 7 155U, twelve cores of
which two are performance cores, delivering under three cores of *sustained*
throughput under a 15 W envelope --- it takes four to six hours. On a
workstation it is proportionally faster.

It is **resumable**: a pair whose draw file already carries the declared
number of draws is skipped, so an interrupted run continues rather than
restarting. `python scripts/s20_boot2.py --plan` prints the grid and the draw
allocation without taking a draw, and `--no-resume` forces a rebuild.

`bash scripts/round20_chain.sh` waits for it and then runs everything
downstream in dependency order, through the checks and the PDF.

### The round-twenty-seven chain, which produces the surface the article reports

**`s20_boot2.py` is no longer the surface the manuscript's bands come from.**
Round twenty-seven replaced it with a *balanced full factorial* --- two
learners, two splits, three register-quality conditions and three rungs,
crossed, at four hundred draws on every pair --- resampled by **weights per
moving block** rather than multinomially. Every band, region, robustness index
and coverage figure in the article is computed on that surface
(`results/s44_*`, `results/s48w_*`), and `s20_boot2.py`'s output is retained
only as the comparison the article makes against it.

```bash
bash scripts/round27_chain.sh
```

runs it: the designed surface under both resampling schemes, the bands and
their internal checks after each, the scheme comparison, the family-wise
coverage, the decision-curve widening, and the estimator comparison. It is the
long job now --- two schemes over nineteen pairs --- and like `s20_boot2.py` it
is resumable per pair.

`reproduce_all.py` invokes it as its own stage, between the analysis waves and
the held-out test, so the default path rebuilds it:

```bash
python scripts/reproduce_all.py --only round27
```

**This was missing until round twenty-seven's last audit.** The wave list in
`reproduce_all.py` ended at `s39`, so a reader who followed this file
regenerated the *retired* surface and got numbers that do not match the paper.
`scripts/check_sources.py` now fails any generator that reads a retired
surface by name, and the stage above closes the other half.

### The other long job: `s31_simboost.py`

`s31_simboost.py` is the simulation at the size a methods claim needs: a
thousand replicates in each of six worlds with a hundred pipeline refits
inside each replicate, plus an `(n, K)` plane up to a 3,019-level register and
three block lengths around *n*^(1/3). It is five to seven hours on the machine
above and is **independent of everything else** — nothing reads its output but
`make_numbers.py` — so it can run beside the chain, and
`python scripts/s31_simboost.py --plan` prices it before it starts. Its three
experiments are written as they finish and `--resume` keeps the ones already
on disk, so `--only core` alone reproduces every coverage number the
manuscript prints; `block` and `grid` add the two sensitivity tables.

When `results/s31_*.csv` is absent, `make_numbers.py` falls back to the
200-replicate `s10_simulation2.py` run for the same macros and
`verify_numbers.py` checks them against that file instead, so a partial
reproduction is consistent rather than broken. Where `s31` *has* run,
`verify_numbers.py` additionally fails if it ran fewer than a thousand
replicates per world, because that is the count the manuscript claims and the
review requires. A reproduction that stops before `s31` therefore reproduces a
manuscript whose `\nSimReps` reads 200; the submitted one reads the full
count, and `results/s31_facts.csv` in the archive carries it.

Two things about the draw count are worth stating because a reader will ask.
First, the critical value of a max-*t* band is **not** taken as the empirical
quantile of those few hundred maxima: `s21_bands.py` estimates it by a
Gaussian multiplier bootstrap over the standardised draw matrix, 20,000 times,
so the fitting budget fixes *B* and not the precision of *q*. Second, the five
planned contrasts of `s24_confirm.py` live on one cell each and are therefore
affordable at 2,000 draws, which is where the plus-one *p*-values come from.

`s18_bias_scaling.py --legacy-target` regenerates Appendix G's
pre-correction figures. It is not needed for the manuscript's numbers; it is
needed if you want to check the correction rather than take it on trust.

To run one stage:

```bash
python scripts/reproduce_all.py --only analysis
python scripts/reproduce_all.py --only numbers
python scripts/reproduce_all.py --only verify
```

## 4. What the controls check

```bash
python scripts/make_numbers.py --strict   # fails if any macro is unresolved
python scripts/verify_numbers.py          # re-derives each macro independently
python scripts/texlint.py                 # abstract, keywords, highlights,
                                          # statements, no numeric literals
python scripts/check_highlights.py        # the highlight character counts
python scripts/finalise.py                # what is still owed before upload,
                                          # and the command that discharges
                                          # each; non-zero while any remains
python scripts/check_claims.py            # no document that speaks for this
                                          # version still asserts a claim the
                                          # project has withdrawn
python scripts/check_sources.py           # no generator reads a RETIRED
                                          # surface by name -- round 27's
                                          # recurring defect, now a gate
python scripts/check_bands.py --prefix s48w   # the bands file's own five
                                          # internal consistency conditions
python scripts/check_response_refs.py     # every section the cover letter
                                          # cites exists, and what it lands on
python scripts/provenance.py              # which script version produced
                                          # each result file
python scripts/s13_attack_numbers.py      # the verifier's own regression suite
python scripts/assemble_paper.py --check  # the shipped .tex is current
python scripts/claim_registry.py --check  # every macro the manuscript uses
                                          # resolves, and every headline
                                          # number is re-derived independently
python scripts/check_reproduction.py      # RE-RUNS one pair of the surface
                                          # for both learner families and
                                          # diffs it against the committed
                                          # CSV at the documented tolerances
python -m pytest fieldvalue -q            # the package
```

**Only one of those controls re-runs an analysis.** Every other check in the
list re-derives the manuscript's macros from the committed CSVs, which means
they verify that the paper agrees with the result files and cannot see a
result file the code no longer produces. That gap is how the cross-machine
discrepancy in §5.1 sat undetected: nothing had ever re-run a cell and
compared it. `check_reproduction.py` does, for one pair and both learner
families, in about fifty seconds.

**`--strict` is not a freshness guarantee.** It certifies that every macro
resolved, not that the file it resolved from is current — this round left a
two-replicate smoke test behind and every macro reading it resolved cleanly to
a wrong number. `results/provenance.json` records each analysis script's
SHA-256 at the moment its outputs were accepted, with a note saying why, and
`make_numbers.py --strict` refuses a manuscript whose numbers come from a
script that has changed since. After re-running a stage:

```bash
python scripts/provenance.py --accept s10_simulation2.py --note "why"
```

**Every number in the manuscript is a macro** defined in `paper/numbers.tex`,
which `make_numbers.py` generates from `results/*.csv`. The manuscript
contains no numeric literal outside that file and the generated tables, and
`texlint.py` fails if one appears. This is why the abstract and a table cannot
disagree: there is one of each number.

`verify_numbers.py` re-derives each checked macro from its result file with
code written against the definition rather than against `make_numbers.py`, so
a bug in the generator is caught rather than propagated consistently.

## 5. Determinism

Every script takes a seed from one constant (`spec.SEED = 20260819`, and
`20260823` for the round-nineteen additions) and derives every stream from it.
Reruns on the same data and the same lockfile reproduce every result file
byte-for-byte **on the same machine**, with two documented exceptions:

- **The pilot's frame** depends on the public index's contents at fetch time.
  The enumeration is cached per stratum under `data/audit2/frame_cache/`, so a
  rerun uses the cache; deleting it re-queries and may return a slightly
  different frame.
- **Full-text retrieval** depends on which open-access locations are reachable.
  `results/s06_fetch.csv` records what was retrieved and from where.

### 5.1 Across machines, byte-for-byte is not true, and here is what is

The committed result files were produced on x86-64. Re-running the analysis on
arm64, at the pinned versions, reproduces some of the surface exactly and some
of it only to a tolerance — and the reader is owed the measurement rather than
the claim. **Bit-exact reproduction is claimed only inside the container**,
which fixes the interpreter, the artefact hashes and the thread counts, and
and whose base image is pinned **by digest**:
`python:3.10.0-slim-bullseye@sha256:ad540a47...88f0d8`. That digest is the
multi-architecture manifest list, so a build still selects the host's
platform while the content is fixed; the canonical environment for a check
against a printed digit is its `linux/amd64` variant. A tag is mutable and a
digest is not, so an image built from this `Dockerfile` today and one built
from it next year are the same image. What remains outstanding is the second
half: the digest of the **built** image, published alongside the release, is
what closes the loop from this file to a specific artefact, and it is recorded
in `submission/OWNER-ACTIONS.md` §4.7 and in the archived release at deposit. Outside that image, this is what a reader should
expect.

Four candidate causes were eliminated by measurement, not by argument. Thread
count is not it: one thread and four give bit-identical answers, and every
script already pins the five variables above. Library version is not it:
scikit-learn 1.7.2 and 1.9.0, pandas 2.2.3 and 2.3.1, and CPython 3.11 and
3.13 all give bit-identical answers to each other. Source drift is not it: the
`spec.py` of the commit that wrote the surface gives bit-identical answers to
the current one. Run-to-run nondeterminism is not it: there is none, and
`check_reproduction.py` condition 4 executes that claim rather than repeating
it. What is left is the machine, and the mechanism is amplification, not
noise. Nudging the boosting learner's encoding matrix by **one ULP** — a
relative change of 2.2e-16 — moves a predicted probability by 0.37 and
Nagelkerke by 0.038, because histogram binning and split-gain ties resolve the
other way and the fitted trees then differ. The logistic learner is not
chaotic in that sense: its predicted probabilities agree to 1.4e-15. What
moves there is the *summary*: a one-hot design over a register gives many test
rows exactly equal predictions, and AUC, average precision and net benefit are
step functions that jump a whole step when a 1e-15 difference unties them.
Fitting one cell through the sparse and the dense code path on a single
machine reproduces the committed AUC discrepancy exactly — identical
probabilities, AUC apart by 1.3e-4.

The discrepancy tracks **cardinality**, not the learner and not the arm:

| what | max abs. difference | where |
|---|---|---|
| the `B_empty` and `B_half` rungs, `without_f`, either family | 2.3e-12 | 4.4e-16 for boosting alone, i.e. machine epsilon |
| logistic, `without_f`, every rung | 2.0e-8 | on a smooth metric |
| logistic, `with_f`, undegraded cells, smooth metrics | 6.9e-9 | Nagelkerke, scaled Brier, log-loss skill |
| logistic, `with_f`, undegraded cells, AUC and average precision | 9.4e-4 | one tie unties |
| boosting, `without_f`, the `B_intake` rungs | 9.9e-2 | the rung is itself high-cardinality |

Once a degradation mechanism runs, a second and larger source is added for
both families: `mask_rare` cuts the cumulative-count curve *inside* a group of
identities that share a count, and `corrupt` maps its draws onto a tie-ordered
index, so which identities are masked or corrupted is decided by a tie order
that nothing in the code pins. This is a defect rather than a fact of
floating-point arithmetic, and it is the one part of this that is repairable;
it is not repaired here because doing so changes every committed number and
the repair belongs with the run that regenerates them.

Taking the whole surface together — 41,472 values, four logs, both families,
every cell of the quality and split axes — these are the **documented
tolerances**, and `scripts/check_reproduction.py` enforces them:

| family | metric class | measured max | documented tolerance |
|---|---|---|---|
| logistic | smooth (Nagelkerke, scaled Brier, log-loss skill) | 0.093934 | 0.10 |
| logistic | rank (AUC, average precision) | 0.038693 | 0.05 |
| logistic | threshold (net benefit) | 0.128427 | 0.15 |
| boosting | smooth (Nagelkerke, scaled Brier, log-loss skill) | 0.851086 | 0.90 |
| boosting | rank (AUC, average precision) | 0.108966 | 0.15 |
| boosting | threshold (net benefit) | 0.354167 | 0.40 |

78.1% of the logistic family's `with_f` values and 59.2% of the boosting
family's come back within 1e-12; the tolerances above bound the rest. They are
ceilings, not typical errors, and they are worst-case over a deliberately
adversarial slice — the smallest rolling block of the smallest logs, under the
heaviest masking, which is where a step of one test row is worth the most.

Two things follow, and both are stated in the manuscript rather than left
here. The affected quantity is the paper's own object of study: the increment
`V = with_f - without_f` over a high-cardinality register is exactly the arm
that does not reproduce across machines. And a reader who wants to check a
printed digit must use the container; a reader who wants to check a
*conclusion* can use anything, because the conclusions rest on comparisons
within one run, and every run is internally consistent.

```bash
python scripts/check_reproduction.py           # the gate, ~50 s
python scripts/check_reproduction.py --wide    # re-derive the table above
python scripts/check_reproduction.py --table   # print it without judging
```

## 6. If something fails

- `refusing to run: paper/.tex.bak exists` — the corruption suite was killed
  mid-flight and the manuscript on disk is corrupted. Restore it from the
  backup named in the message before doing anything else.
- `numeric literals in the prose` — a number was typed into the manuscript
  instead of being added to `make_numbers.py`. Add the macro.
- `N macros are unresolved` — a result file has not been generated. Run the
  stage that writes it; the macro names say which.
- `checksum mismatch` — the dataset you hold is not the dataset the paper was
  written against. Re-fetch.

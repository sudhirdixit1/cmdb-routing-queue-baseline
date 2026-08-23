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
| twenty further public event logs | see `data/corpus/CHECKSUMS.txt` | the corpus |

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
| decomposition, regret | `s03_decompose.py`, `s04_regret.py` | ~2 min |
| the pilot | `s06_audit2.py` | ~20 min, network-bound, cached |
| numbers and tables | `make_numbers.py`, `assemble_paper.py` | seconds |
| figures | `s12_figures.py` | ~1 min |
| verification | `verify_numbers.py`, `verify_paper.py` | ~2 min |
| corruption suite | `attack_verifier.py` | ~20 min |
| PDF | `build_journal.py` | ~1 min |

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
python scripts/assemble_paper.py --check  # the shipped .tex is current
python -m pytest fieldvalue -q            # the package
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
byte-for-byte, with two documented exceptions:

- **The pilot's frame** depends on the public index's contents at fetch time.
  The enumeration is cached per stratum under `data/audit2/frame_cache/`, so a
  rerun uses the cache; deleting it re-queries and may return a slightly
  different frame.
- **Full-text retrieval** depends on which open-access locations are reachable.
  `results/s06_fetch.csv` records what was retrieved and from where.

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

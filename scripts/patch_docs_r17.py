"""Round seventeen's documentation edits: REPRODUCE.md and README.md.

Same exact-anchor discipline as the manuscript patches.

    python scripts/patch_docs_r17.py --check
    python scripts/patch_docs_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDITS = []


def edit(name, path, old, new):
    EDITS.append((name, ROOT / path, old, new))


# ============================================================ REPRODUCE.md
edit("repro-need", "REPRODUCE.md",
     """**Python 3.10.0** and the exact versions in `requirements.txt`. The pins are
not decoration: `scikit-learn` 1.7.2's `TargetEncoder` and
`HistGradientBoostingClassifier` defaults both moved in the release series
around it, and the figures were computed on `matplotlib` 3.10.5.

```
python -m venv .venv
.venv\\Scripts\\activate          # Windows;  source .venv/bin/activate elsewhere
pip install -r requirements.txt
```""",
     """**Python 3.10.0** and the exact versions in `requirements.txt`. The pins are
not decoration: `scikit-learn` 1.7.2's `TargetEncoder` and
`HistGradientBoostingClassifier` defaults both moved in the release series
around it, and the figures were computed on `matplotlib` 3.10.5.

```
python -m venv .venv
.venv\\Scripts\\activate          # Windows;  source .venv/bin/activate elsewhere
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
docker run --rm -v "$PWD/data:/work/data" -v "$PWD/results:/work/results" \\
           -v "$PWD/figures:/work/figures" emptycmdb
```

The data directory is mounted rather than baked in: nothing in this repository
redistributes anybody's data.""")

edit("repro-data", "REPRODUCE.md",
     """## 2. The three datasets

None is redistributed here. Fetch each from its persistent identifier and
put the named files in `data/raw/`.""",
     """## 2. The datasets

None is redistributed here, and none has to be fetched by hand:

```
python scripts/fetch_corpus.py          # 23 files, 7 domains, by DOI
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
corpus sections.""")

edit("repro-runtimes", "REPRODUCE.md",
     """| `r25_figures.py` | seconds (reads result files only) |
| `verify_paper.py` | 1–2 min |
| `attack_verifier.py` | **40–70 min** (one full verifier run per corruption) |
| `build_journal.py` | under 1 min |

`reproduce_all.py` runs the independent scripts in parallel and takes about
45 minutes to reach the verifier, plus the corruption suite.""",
     """| `r25_figures.py`, `r39_figures.py` | seconds each (read result files only) |
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
the six slowest. Allow about 70 minutes to reach the verifier from a cold
`data/`, plus the corruption suite.""")

edit("repro-checker", "REPRODUCE.md",
     """`scripts/attack_verifier.py` is the checker's regression suite: 149
corruptions drawn from defects found in earlier versions of this work. Run it
after any change to the verifier. If you add a claim, add a `ck(...)` with an
anchor **and** a corruption; the suite is what found every hole the verifier
has had.""",
     """It also cannot tell you that an interpretation is sound. **Two of the eleven
corrections this paper reports are sentences in which every literal was
correct** — the extremum that was the worst of the points we had named, and
the count identified with an interval — and no check that compares numbers to
data can see either. The checker now compares the named extremum against the
extremum and the stated count against the run length, which closes those two
instances and not the class.

`ck_word` is new in this version: a count the paper spells out in letters is
compared to the data that produces it. Round sixteen's suite showed that
"Eight errors of our own" could be changed to "Six" and pass, because the
tokeniser only sees digits.

**The census runs last, and this file lints itself to keep it there.** The
unaccounted-and-coverage census was outrun twice: round sixteen found it
sitting halfway down the file, invisible to the checks below it, and moved it;
round seventeen appended two hundred checks below where it had been moved to
and the coverage half silently stopped seeing them. Moving a block does not
fix a hole whose cause is order. It is now a function called once at the end,
and `_lint_check_order()` reads `verify_paper.py`'s own source and fails if any
`ck`/`ck_bound`/`ck_phrase`/`ck_word` **call** appears after that call site.

`scripts/attack_verifier.py` is the checker's regression suite: 183
corruptions drawn from defects found in earlier versions of this work,
including five that mutate a *relation* rather than a value, because that is
the class the two new corrections belong to. Run it after any change to the
verifier. If you add a claim, add a `ck(...)` with an anchor **and** a
corruption; the suite is what found every hole the verifier has had.""")

edit("repro-deporder", "REPRODUCE.md",
     """r15_why_one_org.py                 three public logs   [needs all three files]
r20_second_org.py                  the second organisation   [BPIC 2013 only]
r25_figures.py                     the journal figures  [reads results only]
verify_paper.py                    [needs every result file above]""",
     """r15_why_one_org.py                 three public logs   [needs all three files]
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
verify_paper.py                    [needs every result file above]""")

# ================================================================ README.md
edit("readme-head", "README.md",
     """# Identity, not attributes — analysis repository

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
```""",
     """# Four choices behind one number — analysis repository

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
```""")

edit("readme-claims", "README.md",
     """## What the paper claims

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
   of the new ones removed a claim the previous version made.""",
     """## What the paper claims

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
   relation asserted between them was not.""")


def main(argv):
    check = "--check" in argv
    problems = []
    for name, path, old, _new in EDITS:
        if not path.exists():
            problems.append(f"{name}: {path} missing")
            continue
        if path.read_text(encoding="utf-8").count(old) != 1:
            problems.append(f"{name}: anchor appears "
                            f"{path.read_text(encoding='utf-8').count(old)} times")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if check:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for name, path, old, new in EDITS:
        s = path.read_text(encoding="utf-8")
        path.write_text(s.replace(old, new, 1), encoding="utf-8")
        print(f"  applied {name} -> {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

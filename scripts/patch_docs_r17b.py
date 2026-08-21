"""Round seventeen's documentation edits, part 2: the rest of README.md.

    python scripts/patch_docs_r17b.py --check
    python scripts/patch_docs_r17b.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDITS = []


def edit(name, path, old, new):
    EDITS.append((name, ROOT / path, old, new))


edit("readme-withdrew", "README.md",
     """The mechanism withdrawals from round fifteen — an asymmetry that was an
algebraic identity, and a margin that was a granularity knob — stand.""",
     """The mechanism withdrawals from round fifteen — an asymmetry that was an
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
  reproduce neither the base AUC nor the collapse (`r35`, `r35b`).""")

edit("readme-layout", "README.md",
     """submission/     highlights, cover letter, CRediT, data availability
data/raw/       the three public logs.  NOT in version control.
```""",
     """submission/     highlights, cover letter, CRediT, data availability
data/raw/       the five files the primary analysis reads.  NOT in git.
data/corpus/    the other eighteen, fetched by DOI.  NOT in git; its
                CHECKSUMS.txt IS.
data/normalized/  one parquet per parsed log, so a 728 MB XES is read once
PROTOCOL.md     the pre-registration
REFEREE-LOG.md  four adversarial passes, 22 objections, every disposition
Dockerfile      a pinned environment, including BLAS thread counts
requirements.lock  every dependency by version AND artefact hash
```""")

edit("readme-scripts", "README.md",
     """| `r25_figures.py` | the five journal figures |
| `verify_paper.py` | recomputes every number in the paper |""",
     """| `r25_figures.py`, `r39_figures.py` | the ten journal figures |
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
| `verify_paper.py` | recomputes every number in the paper |""")

edit("readme-verif", "README.md",
     """```
674 checks passed, 0 failed
325 literals in body; 0 unaccounted; 313 compared against data
149 caught, 0 missed, 0 skipped of 149
```

`verify_paper.py` compares every numeric literal in the paper against a value
computed from a result file or recomputed from the raw data, requires each to
appear within an anchor phrase, and fails if any literal in the body is
unaccounted for. `attack_verifier.py` is its regression suite: 149 corruptions.""",
     """```
890 checks passed, 0 failed
410 literals in body; 0 unaccounted; 401 compared against data
183 caught, 0 missed, 0 skipped of 183
```

`verify_paper.py` compares every numeric literal in the paper against a value
computed from a result file or recomputed from the raw data, requires each to
appear within an anchor phrase, and fails if any literal in the body is
unaccounted for. `attack_verifier.py` is its regression suite: 183
corruptions.""")

edit("readme-buys", "README.md",
     """It guards **numbers** thoroughly and **prose** only where a guard was written
by hand. There is no general coverage of non-numeric assertions and this file
will not imply otherwise. All eight corrections the paper reports are claims
about what a number *means*, and the checker would have caught none of them.""",
     """It guards **numbers** thoroughly and **prose** only where a guard was written
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
was foreseen.""")

edit("readme-rules", "README.md",
     """- If you add a claim, add a `ck(...)` with an anchor **and** a corruption to
  `attack_verifier.py`. The suite is what found every hole the verifier has
  had — three of them in round sixteen alone, two of those written *after*
  the first fix looked complete. Write the corruption before you believe the
  check.""",
     """- **A count the paper spells out is compared to the data** (round seventeen).
  `ck_word()` generalises the bespoke fix round sixteen put on the corrections
  count. "Six instruments rather than seven", "three bands", "five incidents"
  — each is now compared to the number the result file produces.
- **The census runs last, and the file lints itself to keep it there** (round
  seventeen). This is the *second* time the coverage census has been outrun by
  checks written below it. Moving the block is not a fix for a hole whose
  cause is order: `_lint_check_order()` reads `verify_paper.py`'s own source
  and fails if any check **call** appears after the census call site.
- **Retiring a check is explicit and safe only because of coverage** (round
  seventeen). Thirty-nine checks whose anchoring sentence no longer exists sit
  in a `RETIRED` set naming the claim that went. That is safe only because a
  literal freed by a retirement and not re-checked becomes unaccounted and the
  run fails. Never retire a check because it fails.
- If you add a claim, add a `ck(...)` with an anchor **and** a corruption to
  `attack_verifier.py`. The suite is what found every hole the verifier has
  had — three in round sixteen and three more in round seventeen, all six
  written *after* a fix looked complete. Write the corruption before you
  believe the check.""")

edit("readme-datasets", "README.md",
     """## The datasets

All three are public; none is redistributed here. `REPRODUCE.md` §2 gives the
identifiers, the filenames, and the two file-format traps that have each cost
a debugging session.""",
     """## The datasets

Twenty-three files across seven domains, all public, none redistributed here.
`python scripts/fetch_corpus.py` resolves every DOI, downloads every file and
records a SHA-256 for each in `data/corpus/CHECKSUMS.txt`, which is tracked.
`REPRODUCE.md` §2 gives the identifiers, the filenames, and the two
file-format traps that have each cost a debugging session.""")


def main(argv):
    check = "--check" in argv
    problems = []
    for name, path, old, _new in EDITS:
        n = path.read_text(encoding="utf-8").count(old) if path.exists() else -1
        if n != 1:
            problems.append(f"{name}: anchor appears {n} times")
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

# The routing-queue baseline effect — analysis repository

Single-organisation study on the BPI Challenge 2014 incident log
(Rabobank Group ICT). Paper: `paper/iaai27_empty_cmdb.tex`.

## Reproducing

    python scripts/r4_final.py    # cohort, baselines, stability, disclosure
    python scripts/r5_final.py    # nulls, mutation sensitivity
    python scripts/r6_final.py    # pooled-uncertainty gains
    python scripts/r8_final.py    # mechanism, design space, scoping
    python scripts/r9_second_task.py  # the ladder on two further targets
    python scripts/r4_figures.py  # baseline + coverage figures
    python scripts/r9_figures.py  # overlap diagram, second task, scoping
    python scripts/verify_paper.py    # every claim vs the result files
    python scripts/attack_verifier.py # regression suite for the verifier
    python scripts/texlint.py         # structural lint of the LaTeX

`data/raw/` must contain Detail_Incident.csv, Detail_Change.csv and
Detail_Incident_Activity.csv from the BPIC 2014 collection
(doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35). The raw data is not
redistributed here.

## Building the paper

    python scripts/build_paper.py

Fetches the official AAAI-27 author kit (the style files are AAAI's and are
not vendored here), then runs pdflatex, bibtex, pdflatex, pdflatex. Requires
a TeX distribution providing `pdflatex` — AAAI mandates a `\pdfinfo` block,
which is a pdfTeX primitive, so xelatex and tectonic will not work.

Current state: 6 pages, 0 errors, 0 undefined references. The body ends on
page 5 and the references run to page 6; IAAI-27 allows 6 pages with
references unlimited.

## Scripts e1-e16 and r1-r3, r7

Superseded. They implement analyses that were withdrawn during review and
are retained only so the withdrawals are auditable. Nothing in the paper
depends on them. `r7_final.py:124-148` in particular prints a conclusion its
own output contradicts; it is kept as the record of a control that failed.

## Verification

`verify_paper.py` compares every numeric literal in the paper against a
value computed from a result file or recomputed from the raw data, requires
each to appear within an anchor phrase, and fails if any literal in the
paper is unaccounted for. `attack_verifier.py` is its regression suite: 14
corruption classes drawn from defects found in earlier versions.

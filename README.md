# The routing-queue baseline effect — analysis repository

Single-organisation study on the BPI Challenge 2014 incident log
(Rabobank Group ICT). Paper: `paper/iaai27_empty_cmdb.tex`.

## Reproducing

    python scripts/r4_final.py      # cohort, baselines, stability, disclosure
    python scripts/r5_final.py      # nulls, mutation sensitivity
    python scripts/r6_final.py      # pooled-uncertainty gains
    python scripts/r8_final.py      # mechanism, design space, scoping
    python scripts/r9_second_task.py   # the ladder on two further targets
    python scripts/r10_estimators.py   # three estimator families
    python scripts/r11_operational.py  # detection framing, target thresholds
    python scripts/r12_queue_from_item.py  # model-free queue/item relationship
    python scripts/r13_queue_shape.py  # queue concentration, reduced-queue ladder
    python scripts/r14_scope.py        # split-averaged scoping curve
    python scripts/r15_why_one_org.py  # affected-item population, 3 public logs
    python scripts/r16_field_semantics.py  # what the Open-row group actually is
    python scripts/r17_mechanism_floor.py  # the floor, rebuilt at item level
    python scripts/r4_figures.py    # baseline + coverage figures
    python scripts/r9_figures.py    # overlap diagram, second task
    python scripts/r14_figures.py   # dose-response + scoping (figG5)
    python scripts/verify_paper.py     # every claim vs the result files
    python scripts/attack_verifier.py  # regression suite for the verifier
    python scripts/texlint.py          # structural lint of the LaTeX

`data/raw/` must contain Detail_Incident.csv, Detail_Change.csv and
Detail_Incident_Activity.csv from the BPIC 2014 collection
(doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35). `r15_why_one_org.py`
additionally needs incident_event_log.zip (UCI 498,
doi:10.24432/C57S4H) and BPI_Challenge_2013_incidents.xes.gz
(doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee). All three are
public; none is redistributed here.

Note that `r4_final.py` executes its whole analysis at import, so every
script that does `import r4_final as M` re-runs it. Expect a few minutes per
script.

## Building the paper

    python scripts/build_paper.py

Fetches the official AAAI-27 author kit (the style files are AAAI's and are
not vendored here), then runs pdflatex, bibtex, pdflatex, pdflatex. Requires
a TeX distribution providing `pdflatex` — AAAI mandates a `\pdfinfo` block,
which is a pdfTeX primitive, so xelatex and tectonic will not work.

Current state: 7 pages, 0 errors, 0 undefined references. The body ends on
page 6 and the references run to page 7; IAAI-27 allows 6 body pages with
references unlimited. If you add text, re-check this: the body has spilled
onto page 7 twice and both times it was the closing sections, not the body,
that had to give.

## What the paper claims

See `FINDINGS-R10-R14.md` for the evidence added in the latest round and,
importantly, for the two claims it forced us to weaken.

## Scripts e1-e16 and r1-r3, r7

Superseded. They implement analyses that were withdrawn during review and
are retained only so the withdrawals are auditable. Nothing in the paper
depends on them. `r7_final.py:124-148` in particular prints a conclusion its
own output contradicts; it is kept as the record of a control that failed.

An early draft of `r14_scope.py` repeated that same defect — it printed an
explanation for a curve feature that its own table refuted — and was
rewritten. If you are adding a script, print only what your output supports.

## Verification

`verify_paper.py` compares every numeric literal in the paper against a
value computed from a result file or recomputed from the raw data, requires
each to appear within an anchor phrase, and fails if any literal in the
paper is unaccounted for. `attack_verifier.py` is its regression suite: 54
corruption classes drawn from defects found in earlier versions.

Currently **252 checks, 0 failed, 0 unaccounted; 54 corruptions caught, 0
missed.**

Three rules, all learned the hard way:

- `ck()` tests rounding EQUALITY at the paper's printed precision, not a
  tolerance. A `6e-4` tolerance on three-decimal literals let three wrong
  last digits through while the suite reported "0 failed".

- If you add a claim, add a `ck(...)` with an anchor AND a corruption to
  `attack_verifier.py`. The suite is what found the last two holes.
- Anchoring alone cannot separate two values that share a sentence. Any
  ordered pair needs a `ck_phrase(...)` pin, or a reviewer can swap them
  undetected.

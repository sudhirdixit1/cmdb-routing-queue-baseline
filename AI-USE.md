# Use of a large-language-model assistant

Elsevier requires a disclosure of generative-AI use; where the use is in the
research method rather than in the writing, it requires the model name and
version, described reproducibly. A disclosure that names a product and not a
version is not reproducible, so this file is the register the manuscript's
declaration points at.

## What the assistant was used for

| purpose | where it appears | reproducible without the model? |
|---|---|---|
| writing the analysis code, the package and the verification harness | every result | yes — the code is in the archive and `REPRODUCE.md` regenerates every number from the raw data |
| adjudicating the literature pilot | Supplement S7 only | **no** — see below |
| drafting and editing prose | the manuscript | not applicable |
| **internal adversarial review** of each revision, in the role of a referee, against the repository | `REFEREE-LOG.md`, `submission/review_round*.md`, the `response_to_*.md` letters other than `response_to_referee.md` | not applicable — these are the author's own reviews, conducted with the tool, and are **not** reports from the journal's referees; the one journal report is answered in `response_to_referee.md` |

No generative model produced, imputed, augmented or selected any datum, any
result or any citation.

## The version register

| round | dates | model identifier | use |
|---|---|---|---|
| 1–18 | 2026-08-18 to 2026-08-22 | **not recorded** | code, prose |
| 19 (literature pilot adjudication) | 2026-08-22 | **not recorded** | code, prose, **pilot adjudication** |
| 20 | 2026-08-23 to 2026-08-24 | **not recorded** | code, prose |
| 21 | 2026-08-24 | `claude-opus-5` | code, prose |
| 22–26 | 2026-08-25 to 2026-08-26 | **not recorded** | code, prose |
| 27 | 2026-08-28 to 2026-08-29 | `claude-opus-5`, then `claude-fable-5` | code, prose, review |
| 28 (this revision) | 2026-09-03 to 2026-09-06 | `claude-fable-5-1` | code, prose, **review** (`submission/review_round28.md`); final pre-submission read on 2026-09-06 |

**The gap is stated rather than filled.** The identifiers for rounds 1–20 and
22–26 were not recorded at the time and are not reconstructible from the
repository; the dates are, and are given. Round twenty-seven ran under two
models in one session --- it began under `claude-opus-5` and continued under
`claude-fable-5` --- and both are listed rather than only the later one,
because a register that names the model that finished the work and not the one
that started it is not a register. For
the code and the prose this does not affect reproducibility: the code is in
the archive and produces the numbers without any model. For the literature
pilot it does, because there the model was part of the measuring instrument.
That is one of the reasons the pilot is reported as a pilot, is confined to
supplementary material, and carries no claim in the article.

## What a reader can check without the model

* `REPRODUCE.md` — every table and figure from the raw logs, one command.
* `scripts/verify_numbers.py --strict` — every macro in the manuscript
  re-derived from the result files by code that does not generate them.
* `scripts/attack_verifier.py` — the corruption suite, which alters a result
  file and requires the verifier to notice.
* `results/provenance.json` — the hash of every script beside the results it
  produced.

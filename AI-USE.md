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
| adjudicating the literature pilot | Supplement S23 only (S21.3 states what it is) | **no** — see below |
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
| 28 | 2026-09-03 to 2026-09-06 | `claude-fable-5-1` | code, prose, **review** (`submission/review_round28.md`); final pre-submission read on 2026-09-06 |
| IJF retarget | 2026-09-11 to 2026-09-12 | `claude-opus-5` | code (blind build, `check_blind`, `retarget_ijf`), prose (abstract, introduction, related work, section openings, cover letter), **review** (`submission/review_round29.md`); after the *Information Systems* desk decision of 2026-09-10 |
| 30, pre-upload review | 2026-09-18 | `claude-fable-5-1`, then `claude-opus-5` | **review** of the built IJF package in the role of a referee (`submission/review_round30.md`) under `claude-fable-5-1`; then the revision that read prompted, under `claude-opus-5`: code (build script, table and figure generators), prose (statements, front matter, section relocations, cover material) |
| 30, verification and corrections | 2026-09-19 | `claude-opus-5` | **review** (seven rounds of independent adversarial reads of the revised build, in the role of referees and a technical editor) and the corrections they prompted (prose, generators, records); no analysis result changed |

**The gap is stated rather than filled.** The identifiers for rounds 1–20 and
22–26 were not recorded at the time and are not reconstructible from the
repository; the dates are, and are given. Round twenty-seven ran under two
models in one session --- it began under `claude-opus-5` and continued under
`claude-fable-5` --- and both are listed rather than only the later one,
because a register that names the model that finished the work and not the one
that started it is not a register. The pre-upload session of 2026-09-18
likewise ran under two models --- the referee read under `claude-fable-5-1`,
the revision under `claude-opus-5` --- and both are listed. For
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

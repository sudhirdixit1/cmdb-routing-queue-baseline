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

No generative model produced, imputed, augmented or selected any datum, any
result or any citation.

## The version register

| round | dates | model identifier | use |
|---|---|---|---|
| 1–18 | 2026-08-18 to 2026-08-22 | **not recorded** | code, prose |
| 19 (literature pilot adjudication) | 2026-08-22 | **not recorded** | code, prose, **pilot adjudication** |
| 20 | 2026-08-23 to 2026-08-24 | **not recorded** | code, prose |
| 21 (this revision) | 2026-08-24 | `claude-opus-5` | code, prose |

**The gap is stated rather than filled.** The identifiers for rounds 1–20 were
not recorded at the time and are not reconstructible from the repository. For
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

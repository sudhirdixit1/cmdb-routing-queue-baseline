---
name: submitting-to-ijf
description: Use when the author is about to upload the Specification Surfaces manuscript to the International Journal of Forecasting (Elsevier/IIF), asks what is still owed before uploading, is diffing the IJF LaTeX template, or is filling in the Editorial Manager forms. Replaces submitting-to-information-systems after the 2026-09-10 desk decision.
---

# Submitting to the International Journal of Forecasting

## Overview

The manuscript was retargeted from *Information Systems* (desk decision,
2026-09-10, `REFEREE-LOG.md`) to the *International Journal of Forecasting*
under `PLAN-IJF.md`, executed 2026-09-12, and read against the journal's
guide and template on 2026-09-18 (`submission/review_round30.md`,
`response_to_review30.md`). Everything the repository can do is done and
gated. What remains are the steps only the author can take. The one
command that says what is still owed, and exits non-zero while anything is:

```bash
python scripts/finalise.py
```

Run it first and last: exit 0 means nothing is owed and the package may be
uploaded.

## What the journal asks (Guide for Authors, April 2020; IIF page and template read 2026-09-18)

- **Double-blind.** The main manuscript and the supplement carry nothing
  that names the author; the title page is a **separate file**, not for
  review. `python scripts/build_journal.py --target ijf` builds all three;
  `python scripts/check_blind.py` reads the two blind PDFs and fails on any
  identifying string.
- The journal's template: `\documentclass[11pt,3p,review,authoryear]{elsarticle}`
  with `model5-names` and `\biboptions{longnamesfirst}` — applied to the
  article; the supplement keeps `preprint,12pt` by decision
  (`submission/IJF-TEMPLATE-CHECKED.md`, `DECISIONS.md` §IJF.5). Abstract
  100–150 words with no notation, at least five keywords from the IIF list
  (`texlint.py` enforces the counts). Figures as vector PDF, no title above
  a plot.
- 4–6 suggested referees outside the author's institution
  (`submission/suggested_reviewers.md`, five, addresses sourced).
- Code and data mandatory; a reproducibility check at acceptance. The
  archive is `10.5281/zenodo.22557927` (release `v28.0`), by decision not
  re-cut (`submission/DECISIONS.md` §IJF.3); `scripts/verify_release.py`
  proves a clean checkout reproduces every number.
- Submit the PDF; sources are requested at acceptance.
- Submission system: `https://www.editorialmanager.com/ijf`.

## The steps only the author can take

| # | step | how | done when |
|---|---|---|---|
| 1 | ~~Diff the IJF LaTeX template~~ | done 2026-09-18: `submission/IJF-TEMPLATE-CHECKED.md` | — |
| 2 | ~~Postcode~~ | done 2026-09-18: Apex, NC 27523 on `title_page.pdf` | — |
| 3 | Editorial Manager profile | create the IJF account; enter the ORCID there (it is not printed on the title page by decision — the system collects it) | profile complete |
| 4 | Elsevier's declaration-of-interests `.docx` | fill from `submission/declaration_of_interests.md`; do not convert the markdown | attached |
| 5 | Related-manuscript sentence | `cover_letter.md` says no other manuscript on these methods or data is under review and the conference-format draft was never submitted; confirm both are true | you agree |
| 6 | Read the title-page statements | CRediT, competing interest, funding, code availability, generative-AI declaration — `build/journal/title_page.pdf` — they are claims about you | you agree with every sentence |
| 7 | Push | `git push origin main ijf-retarget` — **no tag**: `v28.0` stays where the published release points | `origin/main` = `main` |
| 8 | Upload | the table below | submission confirmed |

## Rebuild and gate before upload

```bash
python scripts/make_numbers.py --strict && python scripts/assemble_paper.py && python scripts/build_journal.py --target ijf
```

```bash
for s in texlint verify_numbers check_package check_highlights check_claims check_response_refs check_sources final_search check_blind; do python scripts/$s.py | tail -1; done
```

Every line must end in `0 failures` (or `0 unresolved` / `0 withdrawn`).

## What to upload

| file | where |
|---|---|
| `build/journal/manuscript.pdf` | manuscript (blind) |
| `build/journal/title_page.pdf` | title page (separate file, not for review) |
| `build/journal/supplement.pdf` | supplementary material (blind; the article points into it 75 times) |
| `submission/upload/Highlights.txt` (pasted into Word if asked) | highlights. **Capital H, in `upload/`**; the lower-case `submission/highlights.txt` is the working copy and must not go |
| `submission/cover_letter.md` | cover letter |
| Elsevier's declaration `.docx` | declaration of interests |
| `submission/credit_statement.md`, `submission/data_availability.md` | as the forms ask |
| `submission/suggested_reviewers.md` | referee suggestions |

Do **not** upload `submission/summary_of_changes.md` or
`submission/response_to_referee.md` (they answered the *Information Systems*
referee and are marked superseded), any `review_round*.md` or
`response_to_review*.md` (internal, machine-assisted reviews the AI
declaration names), or `paper/*.pdf` by those names (they are the same blind
builds; the upload names are in `build/journal/`).

## Common mistakes

| mistake | consequence |
|---|---|
| Uploading `paper/specification_surfaces.pdf` from a build without `--target ijf` | an unblinded manuscript goes to double-blind review |
| Editing `paper/tables/*.tex` or `paper/numbers.tex` by hand | `verify_release.py` fails; numbers reach the paper only through macros |
| Moving the `v28.0` tag | the published Zenodo record no longer points at what it archived |
| Converting the declaration `.docx` to another format | the guide forbids it |
| Printing a placeholder ORCID on the title page | a non-fact on the one page that names you |

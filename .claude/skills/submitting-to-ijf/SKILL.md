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
  submission cites the GitHub release `v29.0` (published 2026-09-28), not a
  Zenodo DOI (`DECISIONS.md` §IJF.16).
  `v28.0` (`10.5281/zenodo.22557927`) is the *Information Systems*
  version and its tag never moves. `scripts/verify_release.py` proves a clean
  checkout regenerates every analysis number from the committed results.
- Submit the PDF; sources are requested at acceptance.
- Submission system: `https://www.editorialmanager.com/ijf`.
- Generative-AI declaration (Elsevier policy, updated June 2026): in the
  manuscript **immediately before the references**, and AI-written code
  described in the Methods section. Since 2026-09-24 it is
  `paper/parts/aideclaration.tex`, carried by the blind article (§4.1 has
  the Methods sentence) and the title page. Any further session with an AI
  tool extends the span: update `aiModelId`/`aiModelDate` in
  `scripts/round21_numbers.py` and the table in `AI-USE.md`.
- Review on 2026-09-24 (`DECISIONS.md` §IJF.13): Tiers 1–2 done; the Tier 3
  items listed there are the likeliest referee requests.
- Second review on 2026-09-25 (§IJF.14): five-lens multi-agent review, four
  implementation passes, three verification reads. Article 47 pp,
  supplement 133 pp. New analyses in `scripts/s60_ijf_checks.py` →
  Supplement S14, re-derived by `round31_verify.py`. Hand-typed supplement
  numbers live in `scripts/s43_overview.py` POINTERS (Figure 2) and in
  `submission/data_availability.md` / `credit_statement.md`: re-check them
  against `build/journal/*.aux` after any change to the supplement's order.
  `provenance.py --accept <script> --note "..."` after editing a figure or
  analysis script.
- Final review on 2026-09-25 (§IJF.15): compliance, referee, copy-edit and
  package reads plus a Crossref check of every DOI. Article 48 pp,
  supplement 134 pp. The no-signal benchmark for the split stratum (83.4–83.7%
  of the degrees of freedom) now sits beside the 71.7% in §6.2 and §11;
  `s60_ijf_checks.py` runs in `round27_chain.sh`. Untouched by choice: the
  ~35-page cut, vocabulary renaming, table sizes (Tier 3 / referee asks).

## The steps only the author can take

| # | step | how | done when |
|---|---|---|---|
| 1 | ~~Diff the IJF LaTeX template~~ | done 2026-09-18: `submission/IJF-TEMPLATE-CHECKED.md` | — |
| 2 | ~~Postcode~~ | done 2026-09-18: Apex, NC 27523 on `title_page.pdf` | — |
| 3 | Editorial Manager profile | create the IJF account; enter the ORCID there (it is not printed on the title page by decision — the system collects it) | profile complete |
| 4 | Elsevier's declaration-of-interests `.docx` | fill from `submission/declaration_of_interests.md`; do not convert the markdown | attached |
| 5 | Related-manuscript sentence | `cover_letter.md` says no other manuscript on these methods or data is under review and the conference-format draft was never submitted; confirm both are true | you agree |
| 6 | Read the title-page statements | CRediT, competing interest, funding, code availability, generative-AI declaration — `build/journal/title_page.pdf` — they are claims about you | you agree with every sentence |
| 7 | Push | `git push origin main ijf-retarget` — **do not move `v28.0`**: it stays where the published release points | `origin/main` = `main` |
| 7a | ~~Cut v29.0~~ done 2026-09-28: pushed, release v29.0 published; the submission cites the GitHub release, not a DOI (§IJF.16). Old instructions: | the tree already says v29.0 (`.zenodo.json` has no `doi` key; cover letter reads `DOI-PENDING`). From the **sudhirdixit1** account: GitHub release, new tag `v29.0` on the pushed `main`; Zenodo mints the DOI; `python scripts/insert_doi.py <DOI>`; put the DOI in `submission/cover_letter.md`; `python scripts/make_cover_pdf.py`; gates; commit; push | `finalise.py` exit 0 |
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
| `build/journal/cover_letter.pdf` (`python scripts/make_cover_pdf.py` after any edit to `submission/cover_letter.md`) | cover letter |
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

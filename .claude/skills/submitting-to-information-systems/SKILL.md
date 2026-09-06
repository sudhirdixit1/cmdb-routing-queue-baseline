---
name: submitting-to-information-systems
description: Use when the author is about to upload the Specification Surfaces manuscript to Information Systems (Elsevier), asks what is still owed before uploading, has just received the Zenodo DOI or the Docker image digest, or is filling in the Editorial Manager forms.
---

# Submitting to Information Systems

## Overview

Everything the repository can do is done and gated. What remains needs the
author's accounts or the author's own facts. The one command that says what
is still owed, and exits non-zero while anything is:

```bash
python scripts/finalise.py
```

Run it first and last: exit 0 means nothing is owed and the package may be
uploaded; non-zero lists what is. Do the steps below **in this order**: the archive
snapshots whatever the release tag points at, and Zenodo only archives
releases made *after* its integration is switched on.

## The steps only the author can take

| # | step | how | done when |
|---|---|---|---|
| 1 | Push main, the branch and the tag | **Done 2026-09-06**: `Ardbiu` was added as a collaborator and `main`, `round28-band` and `v28.0` are on the remote at one commit. If the tag is ever moved (step 10), push again with `git push origin main round28-band v28.0` | `git ls-remote --tags origin` lists `v28.0` at the intended commit |
| 2 | Switch on Zenodo's GitHub integration | **Done 2026-09-06**: the repository shows ON under Enabled Repositories at zenodo.org/account/settings/github/ | the repository shows as enabled |
| 3 | Publish the GitHub release | **Done 2026-09-06**: github.com/sudhirdixit1/cmdb-routing-queue-baseline/releases/tag/v28.0, published after the toggle | Zenodo shows a record within minutes |
| 4 | Insert the DOI | **Done 2026-09-06**: `10.5281/zenodo.22557927` (version DOI of release v28.0; concept DOI `10.5281/zenodo.22557926`) is in `.zenodo.json`, the code-availability statement and reference [46]; `final_search.py` passes. If a new release is ever cut, run `python scripts/insert_doi.py <new DOI>` again | `final_search.py` reports 0 failures |
| 5 | Record the built image's digest | build and push the image per `submission/OWNER-ACTIONS.md` §4.7, then `python scripts/finalise.py --image-digest sha256:<64 hex>` | `finalise.py` no longer lists it |
| 6 | Reviewer e-mails | add each suggested reviewer's institutional e-mail in `submission/suggested_reviewers.md` | six addresses present |
| 7 | Postal address | set the full address beside `AFFILIATION_CITY` in `scripts/round26_numbers.py`, then `python scripts/make_numbers.py --strict` and rebuild | title page shows it |
| 8 | Elsevier's forms | competing-interest declaration as Elsevier's **.docx** (do not convert `declaration_of_interests.md`); Highlights pasted unchanged from `submission/upload/Highlights.txt` into the Word file the system asks for; ORCID in the Editorial Manager profile | attached in the system |
| 9 | Read the three statements | CRediT, competing interest and the generative-AI declaration (end of the article, before the references) make factual claims about you; correct them before the upload, not after | you agree with every sentence |
| 10 | Commit and push, but do not move the tag | after 4, 5 and 7: commit on `round28-band`, fast-forward `main`, `git push origin main round28-band`. The DOI, the digest and the address are inserted **after** the archive is cut by design (the archive cannot contain its own DOI), so the DOI-bearing commits sit after `v28.0` on `main` and the tag stays where the published release points. Cut `v28.1` only if a result file or a number-producing script changes; that means a new GitHub release, a new version DOI from Zenodo, and `insert_doi.py` again | `verify_release.py` passes on HEAD |

## Rebuild and gate before upload

Needed after steps 5 and 7, which edit files by hand; step 4 runs this
itself. Always run it once more as the last thing before uploading:

```bash
python scripts/make_numbers.py --strict && python scripts/assemble_paper.py && python scripts/build_journal.py
```

Then every gate; each must end in 0 failures except `final_search.py`, which
must now pass too because the DOI is in:

```bash
for s in texlint verify_numbers check_package check_highlights check_claims check_response_refs check_sources final_search; do python scripts/$s.py | tail -1; done
```

## What to upload

| file | where |
|---|---|
| `build/journal/specification_surfaces.pdf` | manuscript |
| `build/journal/supplement.pdf` | supplementary material (the article points into it 35 times) |
| `submission/upload/Highlights.txt` (pasted into Word) | highlights. **Capital H, in `upload/`**: the lower-case `submission/highlights.txt` is the working copy with build commentary and must not go |
| `submission/cover_letter.md` | cover letter |
| `submission/summary_of_changes.md`, `submission/response_to_referee.md` | response to the journal's referee, the only correspondence uploaded |
| Elsevier's competing-interest .docx | declaration |
| `submission/credit_statement.md`, `submission/data_availability.md` | as the forms ask |
| `submission/suggested_reviewers.md` | reviewer suggestions |

Do not upload `submission/highlights.txt`, any `review_round*.md` or
`response_to_review*.md`: those are the internal, machine-assisted reviews the
AI declaration names, archived and not correspondence.

## Common mistakes

| mistake | consequence |
|---|---|
| Tagging or releasing before step 2 | Zenodo archives nothing; no DOI |
| Uploading with the DOI placeholder | reference [46] and Code availability read "reserved and inserted at proof"; the second internal review says do not submit like that |
| Pushing the image after recording a digest | the digest names an image that does not exist |
| Hand-editing `paper/numbers.tex` or `paper/tables/*.tex` | `verify_release.py` fails; numbers reach the paper only through macros |
| Converting the declaration .docx to another format | the guide forbids it explicitly |

# Submission package — *International Journal of Forecasting* (Elsevier / IIF)

The manuscript is **Specification Surfaces for Incremental Forecast
Performance: Estimation, Uncertainty, and Multi-Log Evaluation**. It was
retargeted from *Information Systems* after that journal's Editor-in-Chief
declined it at the editorial stage on 2026-09-10 with the sentence that it
"should be sent to a forecasting journal" (`../REFEREE-LOG.md`,
`../PLAN-IJF.md`). The journal reviews **double-blind**: the manuscript and
the supplement are built blind, and everything that names the author is on a
separate title page.

**What the letters in this directory are.** `response_to_referee.md` and
`summary_of_changes.md` answered an *Information Systems* referee's report on
an earlier manuscript, *Four Choices Behind One Number*; they are superseded
and are not uploaded. Between that report and this submission the manuscript
went through internal adversarial reviews, conducted by the author with a
large-language-model assistant reading the built PDF against the repository
in the role of a referee. Every objection those reviews raised and its
disposition is in `REFEREE-LOG.md`; the `review_round*.md` files are the
reviews and the `response_to_review*.md` and `response_to_blueprint.md`
files answer them. **None is a report from a journal's referees and none is
uploaded as correspondence**; they are archived so that a reader can see how
each number came to be what it is. The generative-AI declaration on the
title page names this use.

## Read these first

| file | what it is |
|---|---|
| **`OWNER-ACTIONS.md`** | The things only a person can do: the IJF template diff, the postcode, the ORCID and the Editorial Manager profile, the declaration form, the confirmation that the statements are true of you, and the upload. |
| **`cover_letter.md`** | Why this journal, the review history, the related-manuscript disclosure, the archive. |

Every section and appendix reference in the package is checked against the
built manuscript by `scripts/check_response_refs.py`, which resolves letters
and numbers from the manuscript itself rather than from memory.

## What the submission system will ask for

| file | where it goes |
|---|---|
| `../build/journal/manuscript.pdf` | **The manuscript, blind.** Built by `python scripts/build_journal.py --target ijf`; no author block, no statements, the archive pointed at from the title page, the software self-citation printed as Anonymous. `scripts/check_blind.py` reads it and fails on anything identifying. |
| `../build/journal/title_page.pdf` | **The title page, separate file, not for review.** Title, author, affiliation with full postal address, e-mail, abstract, keywords, and the five statements: CRediT, competing interest, funding, code availability with the archive DOI and repository, and the generative-AI declaration. |
| `../build/journal/supplement.pdf` | **The supplement, blind.** The article makes 75 references to it across 46 distinct appendices and subsections, so a reader who receives the article alone cannot follow them. Built by the same command and uploaded as supplementary material. `scripts/check_package.py` fails if the article references an appendix and the package does not list the document that contains it. |
| `upload/Highlights.txt` | **The highlights file to upload, and the only one to upload.** Five bullets, nothing else in the file. **Capital H, in `upload/`**: the lower-case `submission/highlights.txt` is the working copy with build commentary and must not go. If the system asks for a Word file, paste these five lines into it unchanged. |
| `highlights.txt` | The **working copy** of the same five bullets, carrying each bullet's character count and the note on why they are generated. Do **not** upload this one. Both files are written from one `render()` in `scripts/make_highlights.py`, so they cannot disagree; lengths are **derived** by `scripts/check_highlights.py` rather than counted. |
| `cover_letter.md` | Cover letter. |
| `declaration_of_interests.md` | Declaration of interests; the system asks for Elsevier's own `.docx`, which is filled from this. |
| `credit_statement.md` | CRediT roles. |
| `data_availability.md` | Data availability statement, with every dataset DOI. |
| `suggested_reviewers.md` | Suggested reviewers, with the reason for each. |

## What the package records rather than sends

| file | what it is |
|---|---|
| `summary_of_changes.md`, `response_to_referee.md` | **Superseded.** The answer to the *Information Systems* referee's report on *Four Choices Behind One Number*, and the summary of what changed after it. Marked as such at the top of each file; the section numbers belong to the round-28 manuscript. Not uploaded. |
| `review_round21.md`, `review_round28.md`, `review_round29.md` | The internal reviews that are kept verbatim; the others are summarised in `REFEREE-LOG.md`. **Internal, machine-assisted; not the journal's.** |
| `response_to_blueprint.md`, `response_to_review21.md`, `response_to_review23.md`, `response_to_review26.md`, `response_to_review27.md`, `response_to_review28.md`, `response_to_review29.md` | The point-by-point answers to the internal reviews. Archived, not uploaded. |
| `DECISIONS.md` | Decisions the plans left open, how each was settled, and the rejected alternatives. **Round sixteen, and marked superseded at the top of the file**: its title, its section numbers and several of its numbers belong to a manuscript that no longer exists. Kept for the reasoning, and because a decision recorded and later reversed is more useful than one never written down. |
| `reviewer_map.md` | **Superseded.** Maps objections to sections of the round-eighteen manuscript, which is not the one being submitted. Marked as such at the top of the file. |
| `../REFEREE-LOG.md` | Every objection this project has received, with its disposition, including the four defects this round found in its own work after the referee's ten were answered. |

## Before sending

```bash
python scripts/make_numbers.py --strict     # every macro resolved, from an accepted script
python scripts/verify_numbers.py            # macros re-derived from the row-level files, plus consistency conditions
python scripts/texlint.py                   # the compliance checks; --sections adds the per-section word counts
python scripts/check_response_refs.py       # every section this package cites exists, and the word counts it quotes
python scripts/check_highlights.py          # the highlight lengths
python scripts/provenance.py                # which script version produced each result
python scripts/s13_attack_numbers.py        # the verifier's own regression suite
python scripts/build_journal.py             # 0 errors, 0 undefined references, BOTH documents
python scripts/final_search.py              # the patterns that must not appear in the built PDF
python scripts/check_package.py             # every file this table names exists, and every
                                            # document the article references is in the table
```

`final_search.py` reads the **built PDF**, not the sources, and its two
standing failures are the archive DOI: it fails while `\zenodoDOI` still
renders as "a Zenodo deposit whose DOI is reserved and is inserted at proof",
and passes once the DOI in `.zenodo.json` is real. That is the check that stops the manuscript
being submitted with a placeholder where a citation should be.

`--strict` refuses a build whose numbers come from a script that has changed
since its outputs were accepted. If you re-run an analysis stage, accept it
again — `python scripts/provenance.py --accept <script> --note "why"` — or the
build will refuse, which is the point of it.

**And read the compiled PDF end to end afterwards.** On the previous round
that pass found seven defects that produced no wrong number and that every
checker above passed on; section 24 of `../HANDOFF.md` lists
them. On this one it found twelve more, of which five could not have been
caught by any checker that existed at the time: a 57-row table that LaTeX
reported as a float 309 pt too tall and then set anyway with its caption
stranded overleaf; a decision-curve interval that was a percentile interval
while the manuscript said every interval in it was the basic construction; two
cross-instrument claims written as "in all five instruments" that were true in
four; and a sentence contrasting two numbers that print the same. Sections 25.8 to 25.10
of `../HANDOFF.md` have all twelve. The lesson they share: **the generated-macro
discipline protects numbers, and these were the words around them — a
quantifier, a construction name, a contrast. Rewrite the word as a count and
the protection reaches it; otherwise the only instrument is reading.**

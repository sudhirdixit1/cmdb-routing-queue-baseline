# Submission package — *Information Systems* (Elsevier)

The manuscript is **Specification Surfaces for Incremental Predictive
Performance: Estimation, Uncertainty, and Multi-Log Evaluation**. It replaces
*Four Choices Behind One Number*, which a referee for this journal
recommended rejecting as submitted; `response_to_referee.md` answers that
report's ten major comments one by one.

The manuscript then had a **second, developmental review**, which recommended
reject-and-resubmit and listed eight submission-blocking problems, six
methodological strengthenings and three positioning items.
`response_to_blueprint.md` answers those, in the order they were raised, and
is the document to read first if you are the handling editor.

## Read these three first

| file | what it is |
|---|---|
| **`OWNER-ACTIONS.md`** | The things only a person can do: mint the Zenodo DOI, decide what to do with the branch, confirm the three statements are true of you, and upload the separate files the editorial system asks for. It also records what is already done, so you do not redo it. **The DOI is the one blocking item a script cannot clear.** |
| **`response_to_blueprint.md`** | The point-by-point reply to the second review, including a closing section on what was *not* achieved. |
| **`response_to_referee.md`** | The point-by-point reply to the first. |

Every section and appendix reference in all three is checked against the
built manuscript by `scripts/check_response_refs.py`, which resolves letters
and numbers from the manuscript itself rather than from memory. It also checks
the per-section word counts quoted in `response_to_blueprint.md` against
`results/section_words.csv`, and `--sync` rewrites them, because those are the
only numbers in this package that are not macros.

## What the submission system will ask for

| file | where it goes |
|---|---|
| `../build/journal/specification_surfaces.pdf` | The manuscript. |
| `../build/journal/supplement.pdf` | **The supplement.** The article makes 35 references to it across 29 distinct appendices, so a reader who receives the article alone cannot follow 29 of its pointers. Elsevier takes it as a *supplementary file*; it is built by the same command as the article and must be uploaded with it. `scripts/verify_release.py` fails if the article references an appendix and the package does not list the document that contains it. |
| `highlights.txt` | Highlights. Five bullets, each within Elsevier's 85-character limit, with lengths **derived** by `scripts/check_highlights.py` rather than counted — the counts have shipped wrong twice. |
| `cover_letter.md` | Cover letter. |
| `response_to_blueprint.md` | Response to the second review. Upload this one if the system takes a single response document. |
| `response_to_referee.md` | Response to the first report, kept because the correction register cites it. |
| `declaration_of_interests.md` | Declaration of interests. |
| `credit_statement.md` | CRediT roles. |
| `data_availability.md` | Data availability statement, with every dataset DOI. |
| `suggested_reviewers.md` | Suggested reviewers, with the reason for each. |

## What the package records rather than sends

| file | what it is |
|---|---|
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
renders as "DOI reserved, inserted at proof", and passes once the DOI in
`results/release.json` is real. That is the check that stops the manuscript
being submitted with a placeholder where a citation should be.

`--strict` refuses a build whose numbers come from a script that has changed
since its outputs were accepted. If you re-run an analysis stage, accept it
again — `python scripts/provenance.py --accept <script> --note "why"` — or the
build will refuse, which is the point of it.

**And read the compiled PDF end to end afterwards.** On the previous round
that pass found seven defects that produced no wrong number and that every
checker above passed on; Appendix D and section 24 of `../HANDOFF.md` list
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

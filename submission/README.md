# Submission package — *Information Systems* (Elsevier), round nineteen

The manuscript is **Specification Surfaces for Incremental Predictive
Performance: Estimation, Uncertainty, and Multi-Log Evaluation**. It replaces
*Four Choices Behind One Number*, which a referee for this journal
recommended rejecting as submitted; that report is the input to this round and
`response_to_referee.md` answers its ten major comments one by one.

## Read these two first

| file | what it is |
|---|---|
| **`OWNER-ACTIONS.md`** | The things only a person can do: mint the Zenodo DOI, decide what to do with the branch, confirm the three statements are true of you, and upload the separate files the editorial system asks for. It also records what is already done, so you do not redo it. |
| **`response_to_referee.md`** | The point-by-point reply. Every section reference in it is checked against the built manuscript by `scripts/check_response_refs.py`, which currently resolves 54 of 54. |

## What the submission system will ask for

| file | where it goes |
|---|---|
| `../build/journal/specification_surfaces.pdf` | The manuscript. |
| `highlights.txt` | Highlights. Five bullets, each within Elsevier's 85-character limit, with lengths **derived** by `scripts/check_highlights.py` rather than counted — the counts have shipped wrong twice. |
| `cover_letter.md` | Cover letter. |
| `response_to_referee.md` | Response to the previous report. |
| `declaration_of_interests.md` | Declaration of interests. |
| `credit_statement.md` | CRediT roles. |
| `data_availability.md` | Data availability statement, with every dataset DOI. |
| `suggested_reviewers.md` | Suggested reviewers, with the reason for each. |

## What the package records rather than sends

| file | what it is |
|---|---|
| `DECISIONS.md` | Decisions the plans left open, how each was settled, and the rejected alternatives. Round sixteen and seventeen; kept for the reasoning, not for the section numbers. |
| `reviewer_map.md` | **Superseded.** Maps objections to sections of the round-eighteen manuscript, which is not the one being submitted. Marked as such at the top of the file. |
| `../REFEREE-LOG.md` | Every objection this project has received, with its disposition, including the four defects this round found in its own work after the referee's ten were answered. |

## Before sending

```bash
python scripts/make_numbers.py --strict     # every macro resolved, from an accepted script
python scripts/verify_numbers.py            # 61 macros re-derived, 10 consistency conditions
python scripts/texlint.py                   # 14 compliance checks
python scripts/check_response_refs.py       # every section this package cites exists
python scripts/check_highlights.py          # the highlight lengths
python scripts/provenance.py                # which script version produced each result
python scripts/s13_attack_numbers.py        # the verifier's own regression suite
python scripts/build_journal.py             # 0 errors, 0 undefined references
```

`--strict` refuses a build whose numbers come from a script that has changed
since its outputs were accepted. If you re-run an analysis stage, accept it
again — `python scripts/provenance.py --accept <script> --note "why"` — or the
build will refuse, which is the point of it.

**And read the compiled PDF end to end afterwards.** On this round that pass
found seven defects that produced no wrong number and that every checker above
passed on; Appendix C and section 24 of `../HANDOFF.md` list them.

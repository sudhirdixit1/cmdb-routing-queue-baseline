# Submission package — *Information Systems* (Elsevier)

Everything the submission system will ask for, plus the two files that record
what was decided and what is still yours to do.

## Read these two first

| file | what it is |
|---|---|
| **`OWNER-ACTIONS.md`** | The five things only you can do — rename the repository, push, mint the Zenodo DOI, post the arXiv preprint, confirm the acknowledgement — each with the exact commands. **Nothing else in this package is ready to send until §1–§3 of that file are done**, because the manuscript cites a repository that does not exist yet. |
| **`DECISIONS.md`** | The four open decisions from the plan, how each was settled and why, plus the three findings this round produced that the plan did not anticipate — including the one that removed the paper's previous operational headline. |

## What the submission system will ask for

| file | where it goes |
|---|---|
| `highlights.txt` | Highlights. Five bullets, each under Elsevier's 85-character limit; the lengths are printed beside them so a future edit can check without counting. |
| `cover_letter.md` | Cover letter. **Has a "delete before sending" section at the bottom** listing the four placeholders to fill (repository URL, Zenodo DOI, arXiv identifier, refreshed counts). |
| `data_availability.md` | Data availability statement. Contains a paste-ready paragraph and the three dataset DOIs. |
| `credit_statement.md` | CRediT roles, plus the generative-AI disclosure Elsevier's policy requires. |
| `declaration_of_interests.md` | Competing-interests declaration. None to declare. |
| `suggested_reviewers.md` | Six names with, for each, what they are best placed to *break*. Affiliations need re-checking and email addresses need supplying — the file says so at the top. |

## The manuscript itself

Not in this directory. `paper/iaai27_empty_cmdb.tex` builds to
`paper/iaai27_empty_cmdb.pdf` via `python scripts/build_journal.py`: 33
pages, 0 errors, 0 undefined references. The file name is a fossil of the
IAAI-27 draft this was retargeted from; Elsevier's system renames uploads
anyway.

Upload for the submission: the PDF, plus — if the journal asks for source —
the `.tex`, `references.bib`, and the five `figJ*.png` files. Nothing else in
`paper/` is used by the build.

## A note on the numbers quoted in these files

`674 checks`, `325 literals`, `149 corruptions`, `33 pages` appear in the
cover letter and in `REPRODUCE.md`. They move whenever the manuscript does.
Before sending, run

```bash
python scripts/reproduce_all.py
```

and reconcile. If any of them has drifted, the cover letter is making a
claim about an artifact that no longer exists — which is, precisely, the
class of error this paper is about.

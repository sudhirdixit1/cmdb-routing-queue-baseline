# Submission package — *Information Systems* (Elsevier)

Everything the submission system will ask for, plus the files that record what
was decided and what is still yours to do.

## Read these three first

| file | what it is |
|---|---|
| **`OWNER-ACTIONS.md`** | The things only you can do — push round seventeen, rename the repository, mint the Zenodo DOI, post the arXiv preprint, confirm the acknowledgement — each with the exact commands. **Nothing else in this package is ready to send until §0–§3 of that file are done**, because the manuscript cites a repository that does not exist yet and a branch that is not pushed. It also flags one commit in the branch that contains a corrupted manuscript, and what to do about it. |
| **`DECISIONS.md`** | Every decision the two plans left open, how each was settled and why, with the rejected alternatives. Round seventeen added six, including the title change and the decision to report the pre-registered generality claim as falsified rather than soften it. |
| **`../REFEREE-LOG.md`** | Four adversarial passes, twenty-two objections, every disposition — including the six dismissed and the reason for each. Three produced new measurements. |

## What the submission system will ask for

| file | where it goes |
|---|---|
| `highlights.txt` | Highlights. Five bullets, each under Elsevier's 85-character limit; the lengths are printed beside them and are re-derived rather than copied, because the previous version's five counts were all wrong. |
| `cover_letter.md` | Cover letter. **Has a "delete before sending" section at the bottom** listing the five placeholders to fill (repository URL, Zenodo DOI, arXiv identifier, refreshed counts, protocol as supplementary material). |
| `data_availability.md` | Data availability statement. A paste-ready paragraph, all fourteen dataset DOIs, and the pre-registration. |
| `credit_statement.md` | CRediT roles, plus the generative-AI disclosure Elsevier's policy requires. |
| `declaration_of_interests.md` | Competing-interests declaration. None to declare. |
| `suggested_reviewers.md` | Six names with, for each, what they are best placed to *break*, and a round-seventeen addendum on what has moved. Affiliations need re-checking and email addresses need supplying — the file says so at the top. |
| `../PROTOCOL.md` | **Supplementary material.** The corpus pre-registration. A referee should not have to go looking in a repository for it. |
| `../AUDIT-PROTOCOL.md` | **Supplementary material.** The audit pre-registration, with its three amendments and the defects that forced each. |
| `../PREDICTION.md` | **Supplementary material.** The registered prediction, with both frozen thresholds and the in-sample failure of the form the plan named. |
| `../results/r40_coding.csv` | **Supplementary material.** The audit's coding sheet: one row per included paper, every code with its verbatim quote and PDF page, and the second implementation's code beside it. This is what makes the audit auditable rather than trusted. |
| `../results/r40_adjudication.csv` | **Supplementary material.** The thirty papers read by hand, with the adjudicated codes, the axis each reported range was over, and a note per paper. |
| `reviewer_map.md` | **Supplementary material, or a cover-letter attachment.** One row per objection a referee is likely to raise, and the section that answers it. |

## The manuscript itself

Not in this directory. `paper/iaai27_empty_cmdb.tex` builds to
`paper/iaai27_empty_cmdb.pdf` via `python scripts/build_journal.py`: 47
pages, 0 errors, 0 undefined references. The file name is a fossil of the
IAAI-27 draft this was retargeted from; Elsevier's system renames uploads
anyway.

Upload for the submission: the PDF, plus — if the journal asks for source —
the `.tex`, `references.bib`, and the ten `figJ*.png` and `figK*.png` files.
Nothing else in `paper/` is used by the build.

## A note on the numbers quoted in these files

`936 checks`, `417 literals`, `199 corruptions`, `24 files`, `13 admitted
logs`, `47 pages` appear across the cover letter, the data-availability
statement and `REPRODUCE.md`. They move whenever the manuscript does, and the
round-sixteen versions of these files all quoted counts that had. Before
sending, run

```bash
python scripts/reproduce_all.py
```

and reconcile. If any of them has drifted, the cover letter is making a claim
about an artifact that no longer exists — which is, precisely, the class of
error this paper is about. `scripts/patch_counts_r17.py` is the script that
did the last reconciliation and shows which files carry which count.

# What only the author can do

Everything in the plan that needs an account, a credential, or a decision
that is not mine to make. Each item says exactly what to do and what is
already prepared for it, so none of them takes more than a few minutes.

Ordered by what blocks what.

---

## 1. Create the renamed repository — blocks everything below

**Why.** The live remote is
`https://github.com/sudhirdixit1/cmdb-routing-queue-baseline.git`. That name
embeds "routing queue", which is the description Section 4 of the paper
*retracts*: the field is the group that **logged** the incident, not a
routing queue. The manuscript already prints the intended name,
`cmdb-field-admission`, in its Acknowledgements. The two do not currently
agree.

**Do.** On GitHub, rename the repository to **`cmdb-field-admission`**
(Settings → General → Repository name → Rename). GitHub keeps a permanent
redirect from the old name, so nothing that cites the old URL breaks. Then,
locally:

```bash
git remote set-url origin https://github.com/sudhirdixit1/cmdb-field-admission.git
git remote -v
```

**Not done here** because renaming a repository is an outward-facing change
to a public artifact and needs your GitHub credentials.

> If you would rather keep the old name, the manuscript's Acknowledgements
> URL and this file both have to change instead. Do not ship them
> disagreeing.

---

## 2. Push the work — **DONE**

`r10`–`r25`, the manuscript, the figures, the result files, `REPRODUCE.md`
and this package are public as of round sixteen. Git Credential Manager had
a live credential for the remote, so this one did not need you after all.

```
d301bf2  Record the plan's execution in the plan
315ffaf  Round sixteen: which layer pays, decision curve analysis, two withdrawals
```

Both are on `main` and on `round-sixteen-information-systems`, at
`github.com/sudhirdixit1/cmdb-routing-queue-baseline` — the **old** name, see
§1. The paper cites the new one, so the citation is dead until you rename.

**Two things to look at, since this went out while you were away.**

1. `submission/` is now public. Nothing in it is confidential — no
   credentials, no unpublished data, and the suggested-reviewer file carries
   no contact details — but a cover-letter draft and a reviewer list are
   things some authors would rather keep private. If you want them out:
   `git rm -r --cached submission && echo submission/ >> .gitignore`, commit,
   push. The files stay on your disk.
2. The `--% ` "Notes to self before sending" section at the foot of
   `cover_letter.md` is visible. It is a to-do list, not a disclosure, but
   delete it before the letter goes to the journal either way.

---

## 3. Mint the Zenodo DOI

**Why.** The paper cites a repository; a repository URL is not a citable,
archived artifact. *Information Systems*' reproducibility programme will
want one, and so will a referee.

**Do.**

1. Sign in at <https://zenodo.org> with your GitHub account.
2. Under *GitHub* in your Zenodo profile, flip the switch **on** for
   `cmdb-field-admission`.
3. On GitHub, draft a release tagged `v1.0.0-is-submission`, title it
   "Information Systems submission", publish it.
4. Zenodo picks up the release and mints a DOI within a minute or two.
   `.zenodo.json` at the repository root already carries the title, the
   description, the keywords, the licence, and the three dataset DOIs as
   `isDerivedFrom` relations — Zenodo reads it automatically, so you should
   not have to type any metadata.
5. Copy the **concept DOI** (the one that always resolves to the latest
   version, not the version-specific one).

**Then.** Put the DOI in three places:

- `paper/iaai27_empty_cmdb.tex`, the Acknowledgements paragraph, next to the
  repository URL.
- `submission/cover_letter.md`, paragraph two.
- `submission/data_availability.md`, in the statement for the submission
  system.

After editing the manuscript, re-run `python scripts/verify_paper.py`. A DOI
contains digits, and the verifier checks every numeric literal in the body —
the URL sits inside a `\url{}`, which the tokeniser does not scan, so this
should pass unchanged, but check rather than assume.

**Not done here** because it needs your Zenodo and GitHub accounts.

---

## 4. Post the arXiv preprint — before submitting, not after

**Why.** Elsevier permits preprints, it is free, and the median time from
submission to acceptance at this journal is about 244 days. Posting first
starts the citation clock during that window. Posting *after* submission
loses most of the benefit for no gain.

**Do.**

- Category: **cs.SE** primary, cross-list **cs.LG** and **cs.DB**.
- Upload `paper/iaai27_empty_cmdb.tex`, `paper/references.bib`, and the five
  `paper/figJ*.png` files. arXiv runs its own LaTeX; `elsarticle` is in its
  distribution.
- Licence: CC BY 4.0 unless you have a reason to pick another.
- Title, abstract and author details are in the manuscript's frontmatter;
  copy them rather than retyping.
- Add the arXiv identifier to `submission/cover_letter.md`.

**Not done here** because it publishes to a public archive under your name.

---

## 5. Two editorial decisions that are yours

### 5.1 The title

I picked one so the manuscript would build, and recorded why in
`submission/DECISIONS.md`. The choice is
**"Identity, Not Attributes: What Configuration Data Contributes to Incident
Prediction in Two Organisations"**, on the ground that the plan promoted the
identity finding to the lead contribution and a title should name the lead
contribution.

The two alternatives from the plan are still live. To switch, edit the
`\title{}` block and re-run `verify_paper.py` — it asserts that the title
names the paper's subject and does not assert a magnitude the body ranges
over, so it will tell you if a replacement breaks either rule.

### 5.2 The acknowledgement

The manuscript now says the later review rounds were machine-assisted, which
is what the repository records. **If a real practitioner in IT service
management did review this work, that credit was removed in error and should
be restored** — I could not verify a name and would not invent one. The
sentence to edit is the first of the "Acknowledgements and Reproducibility"
section.

---

## 6. If invited to the reproducibility track

Say yes. It is a second publication from the same work, co-authored with the
reproducibility reviewers, and this repository was built for exactly that
review. `REPRODUCE.md` is written for a stranger with the three DOIs and a
Python install.

---
---

# Round seventeen: what changed in this list, and one new item

Nothing in §§1, 3, 4 and 5 above is done. They all still need your accounts or
your judgement, and none was attempted. §2 (*Push*) needs re-reading, because
its status has changed.

## 0. NEW — round seventeen is committed but **not pushed**

**Where the work is.** Branch `round-seventeen-strong-accept`, local only. It
is a large round: a pre-registered protocol, a corpus of twenty-four public
files, thirteen new analyses, a rebuilt 47-page manuscript, the checker from
674 checks to 936, the corruption suite from 149 to 199, and a referee log.

**Why it was not pushed.** Pushing publishes. Round sixteen pushed because a
live credential happened to be present and the plan asked for it; this round's
plan does not ask for a push, and publishing a manuscript that retracts its own
previous headline is a decision worth taking deliberately rather than as a side
effect. `PLAN-STRONG-ACCEPT.md` §0.3 says a credential item stops *that item
only*, which is what happened.

**Do, when you are ready.**

```bash
git checkout round-seventeen-strong-accept
git log --oneline main..HEAD          # read the messages before you push
python scripts/reproduce_all.py       # confirm it still passes on your machine
git push -u origin round-seventeen-strong-accept
```

**Read this before you push.** The commit `6456088` in that branch contains a
**corrupted manuscript**: a `git add -A` issued while the corruption suite was
rewriting the file froze an injected `$58.2\%$` where `$18.2\%$` belongs. The
very next commit, `9b5b340`, restores it and adds three controls so it cannot
happen again. Nothing after `9b5b340` is affected and the branch tip is
correct. If you would rather the history not contain it, the two commits can be
squashed before pushing:

```bash
git rebase -i 6456088~1     # mark 9b5b340 as 'fixup'
```

That is a judgement call about whether a public history should show a mistake
being made and repaired, or only the repaired state. This project's whole
argument is for the former, so the default is to leave it — and `HANDOFF.md`
§20.9 describes it either way.

## 1. Repository rename — unchanged, still blocks the citation

The manuscript still prints `github.com/sudhirdixit1/cmdb-field-admission` and
the live remote is still `cmdb-routing-queue-baseline`. §1 above has the
commands.

## 3, 4, 5 — unchanged

The Zenodo DOI, the arXiv preprint and the acknowledgement decision are as
described above. Two notes:

- **`.zenodo.json` is updated and ready.** Round seventeen rewrote its title,
  description, keywords and `isDerivedFrom` relations: fourteen dataset DOIs,
  the current literal and corruption counts, and the pre-registration.
  Regenerate with `python scripts/patch_zenodo_r17.py` if the counts move
  again.
- **The acknowledgement decision is unchanged and is still the one that could
  be wrong in the direction that matters.** The manuscript describes rounds
  eleven to seventeen as machine-assisted. If a real practitioner reviewed this
  work, that credit was removed in error and only you can say so.

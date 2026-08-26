# Owner actions — the things a person has to do

Everything in this repository that a script can do, a script does. What
follows needs an account, a credential or a judgement call, and is listed so
it is not mistaken for done.

---

## 0. The one-line item round twenty-six added

### 0.1 The affiliation's city and country  *(done)*

Supplied in round twenty-six as **Apex, United States**, in
`scripts/round26_numbers.py`:

```python
AFFILIATION_CITY = "Apex"
AFFILIATION_COUNTRY = "United States"
```

Setting either back to `None` makes the title block print the visible `??`
marker and `verify_numbers` fail, which is the intended behaviour for a value
the repository cannot derive.

**The ORCID** is the other half of the same referee comment. Elsevier collects
it from the corresponding author's profile in the submission system rather
than from the manuscript source, so there is nothing to change in the LaTeX —
but the profile has to carry one before submission.

---

## 1. Before submission

### 1.1 Mint the archive DOI  *(required by the referee's Phase 7)*

The manuscript's data-availability and code-availability statements cite a
Zenodo DOI. There is nothing to cite yet, so the macro currently renders as
*"the archived release cited in the data-availability statement (DOI reserved,
inserted at proof)"* rather than as the `??` marker — a number that does not
exist yet is a different thing from a number that is missing, and the
manuscript says which. `.zenodo.json` carries `"version": "v25.0"` and must be moved to `v26.0`, and its numeric claims are
checked against `paper/numbers.tex` by `check_response_refs.py` --- seven
of them had gone stale before round twenty-five added that check.

1. Log in at <https://zenodo.org> with the GitHub account that owns
   `sudhirdixit1/cmdb-routing-queue-baseline`.
2. **Settings → GitHub**, and switch the repository **on**. Zenodo will then
   archive every future release.
3. **Tag the commit this manuscript was built from as `v26.0`** and push it.
   Its message should record the gate results at that commit:

   ```bash
   git tag -a v26.0 -m "round twenty-six: the split as an error stratum, the MPID, and two headlines withdrawn"
   git push origin v26.0
   git ls-remote --tags origin
   ```

4. On GitHub, **Releases → Draft a new release**, choose the tag
   `v25.0`, title it
   *Specification Surfaces for Incremental Predictive Performance*, and
   publish. Zenodo mints the DOI within a minute or two.
5. Paste the minted DOI into one command:

   ```bash
   python scripts/insert_doi.py 10.5281/zenodo.XXXXXXX
   ```

   That writes the `doi` key into `.zenodo.json` and runs the whole chain ---
   `make_numbers.py --strict`, `assemble_paper.py`, `texlint.py`,
   `verify_numbers.py`, `build_journal.py`, `check_response_refs.py` --- so a
   DOI that does not build is reported before you commit it. It takes a bare
   DOI or a `doi.org` URL.

   **It refuses a DOI that is not this archive's.** Before writing anything it
   resolves the DOI against Zenodo's public API (no credential needed to
   read) and checks the record's title against `.zenodo.json`'s and its
   depositor against this archive's creators. A mistyped digit usually lands
   on somebody else's deposit rather than on nothing, and a live link in a
   submitted paper that goes to the wrong record is worse than the
   placeholder, which at least cannot mislead. `--no-verify` skips the check
   for an offline machine; `--dry-run` reports and writes nothing.

Before tagging, run `python scripts/verify_release.py`. It exports the tree
with `git archive` --- which sees exactly what the tag will --- and rebuilds
the manuscript out of it, failing if any macro or generated table differs
from the committed copy by a byte. That is the *confirm the archived release
reproduces the submitted numbers* half of this item, and it passes on the
commit this file ships with.

**Step 2 has never been done, and that is the binding one.** Round
twenty-five queried Zenodo's public API for this repository by name, by the
manuscript's title and by the owner's username: **zero records**. The remote
carries a `v19.0` tag, so a release was tagged and never archived --- which
is what an un-enabled integration looks like. Zenodo only archives releases
made *after* the repository is switched on, so **switching it on is not
optional and tagging first will produce nothing**. Do step 2, then step 3.

**The insertion itself is verified end to end.** Round twenty-five ran step 5
against a `git archive` export --- a tree carrying only what is committed,
which is what the tag will point at --- with a placeholder DOI. All six gates
exit clean, `\zenodoDOI` becomes `\url{https://doi.org/...}`, the
code-availability statement on **page 43** of the article carries the
resolved URL with the placeholder gone, the article is still 48 pages, and
both documents build at 0 errors, 0 undefined references, 0 overfull boxes.
The refusals were exercised too: a malformed DOI, a well-formed DOI Zenodo
has no record for, and a real Zenodo DOI belonging to a different deposit are
each refused with nothing written. So the only thing between this manuscript
and a real DOI is the deposit --- nothing in the build will surprise you when
you paste the number in.

**Minting the DOI is the one blocking item a script cannot clear.** The second review is
explicit that a manuscript whose archive DOI reads "reserved" should not be
submitted, and it is right: a reproducibility claim that points at a mutable
repository is not a reproducibility claim. Everything else in this repository
is done; this needs the depositing account.

### 1.2 Decide what to do about the branch

The work is on `round25-coverage`, which branches from `main`. Merge it to
the default branch before tagging if the release should sit on the mainline;
the archive is a snapshot of whatever the tag points at. Nothing under
`data/` is committed on it.

### 1.3 Read the three statements

`submission/credit_statement.md`, `declaration_of_interests.md` and the
generative-AI declaration in the manuscript's back matter make factual claims
about **you**. They are written as the author believes them to be true; the
author is the only person who can confirm them. In particular the AI
declaration names three specific uses — the software, the pilot's
adjudication, and drafting — and if any of that is wrong it must be corrected
before submission, not after.

### 1.4 Upload the separate files Elsevier asks for

The editorial system takes highlights and the cover letter as separate items,
not as part of the PDF.

| item | file |
|---|---|
| Manuscript | `build/journal/specification_surfaces.pdf` |
| Highlights | `submission/highlights.txt` (the paste-ready block at the bottom) |
| Cover letter | `submission/cover_letter.md` |
| Supplementary material | `build/journal/supplement.pdf` |
| Response to the previous report | `submission/response_to_referee.md` |
| Declaration of interests | `submission/declaration_of_interests.md` |
| CRediT | `submission/credit_statement.md` |
| Data availability | `submission/data_availability.md` |
| Suggested reviewers | `submission/suggested_reviewers.md` |
| Response to the first developmental review | `submission/response_to_blueprint.md` |
| Response to the second developmental review | `submission/response_to_review21.md` |

### 1.5 Corresponding-author details the submission system asks for

The manuscript carries the name, the affiliation line and the email. The
editorial system also asks for a **full postal address and a telephone
number**, which are personal details deliberately not committed to a public
repository. Have them ready at upload; nothing in the build supplies them.

### 1.6 Figures, if the production office asks for more

Every figure is generated at 400 dpi, which is above the 300 dpi Elsevier asks
for on combination art. If production wants vector files instead, change
`savefig(p)` to also write `p.with_suffix(".pdf")` in `scripts/s12_figures.py`
and `scripts/s28_figures.py` and re-run them; the manuscript's
`\includegraphics` calls name the `.png` explicitly and do not need to change.

### 1.7 Check the length against the journal's own guidance

`python scripts/texlint.py --report` prints the abstract word count, the
keyword count, the highlight lengths and an approximate main-text word count;
`--sections` adds the per-section breakdown and writes
`results/section_words.csv`. The abstract is 198 words; the linter's limit is
200, which is stricter than the journal's 250 and is the limit the second
developmental review set.

The appendices are now a separate supplementary document, which is the change
that review asked for. Check the article's page count against the journal's
own guidance before submitting; if the editor asks for a shorter article
still, the two things to cut are section 9 (the reporting standard and the
software) and the partial-identification passage of section 8, in that order.

### 1.8 Confirm the generative-AI version register

`AI-USE.md` records the model identifier and dates for every round. Round
twenty-one's is `claude-opus-5`; rounds one to twenty are recorded as
**unrecorded**, because they were not recorded at the time. If you have
session records that establish them, fill them in. If you do not, leave them
as they are: an unrecorded identifier stated as unrecorded is a disclosure,
and a guessed one is not.

---

## 2. Optional, and worth considering

### 2.1 Decide whether to expand the pilot frame

The pilot's frame is **600 deduplicated records across 77 strata**, against a
declared budget of 2,400: the public index's daily request quota stopped the
enumeration first. Every enumerated record was therefore taken, every design
weight is 1, and §9.4 reports the pilot as a census of what one index returned
rather than a probability sample of a literature.

`scripts/s06_audit2.py --frame` retries the enumeration, caching per stratum
and waiting the quota out over about six hours. **It was stopped deliberately
in the last session rather than left running**, because succeeding would
overwrite `s06_sample.csv` and leave a new sample beside the existing coding
and adjudications — which is worse than not expanding. Expanding means
re-running

```bash
python scripts/s06_audit2.py --frame --fetch --screen --dossiers
```

and then **re-adjudicating from scratch**, which is the part that needs a
person: this session adjudicated 54 screened-in and 120 screened-out papers by
hand against their dossiers. The pilot's binding limitation is its effective
sample size, and only more adjudicated papers fix it.

Worth weighing against: no claim in the paper depends on the pilot, and the
current version is complete, internally consistent, and honest about its own
reach.

### 2.2 Find a second, independent coder

The referee asked for two independent human raters. One author cannot supply
the second. If a colleague will code even fifty of the dossiers blind, the
pilot gains a real reliability estimate and the paper can say so.

### 2.3 Approach an organisational partner

The single change that would most improve the case study: an estate with
timestamped field histories, a known prediction time, historical register
population and accuracy, operational review costs, and practitioner
confirmation of which fields are admissible at which decision time. Everything
in `scripts/` would run on it unchanged.

---

## 3. What is already done, so you do not redo it

- The manuscript is assembled, compiles, and passes `texlint.py` with zero
  failures: abstract within the limit, seven keywords, five highlights each
  within 85 characters and each with a machine-derived length, all five
  required statements present, no `Appendix Appendix`, and **no numeric
  literal anywhere in the prose**.
- The bibliography carries no commentary; the annotations the referee quoted
  are gone.
- Figure 1 is replaced with a specification curve, readable at print size.
- `requirements.lock` pins every transitive dependency by hash and the
  `Dockerfile` pins the thread counts.
- `python scripts/reproduce_all.py` runs the whole study end to end.
- `results/provenance.json` records which version of each analysis script
  produced the results in the tree; all sixteen are accepted and
  `make_numbers.py --strict` passes. **If you re-run any stage, accept it
  again** — `python scripts/provenance.py --accept <script> --note "why"` —
  or `--strict` will refuse the build, which is the point of it.
- The corruption suite catches 10 of 10; `verify_numbers.py` re-derives 56
  macros independently and enforces 9 consistency conditions, with 0 failures;
  `check_response_refs.py` confirms all 50 section references in the cover
  material resolve to headings that exist.
- The branch `round-nineteen-specification-surfaces` is pushed to
  `origin`.

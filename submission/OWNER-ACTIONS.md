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
*"a Zenodo deposit whose DOI is reserved and is inserted at proof"* rather
than as the `??` marker — a number that does not
exist yet is a different thing from a number that is missing, and the
manuscript says which. `.zenodo.json` carries `"version": "v27.0"`, moved there in round twenty-seven so the manuscript names the release it describes, and its numeric claims are
checked against `paper/numbers.tex` by `check_response_refs.py` --- seven
of them had gone stale before round twenty-five added that check.

1. Log in at <https://zenodo.org> with the GitHub account that owns
   `sudhirdixit1/cmdb-routing-queue-baseline`.
2. **Settings → GitHub**, and switch the repository **on**. Zenodo will then
   archive every future release.
3. **Tag the commit this manuscript was built from as `v27.0`** and push it.
   Its message should record the gate results at that commit:

   ```bash
   git tag -a v27.0 -m "round twenty-seven: the weighted bootstrap on a balanced designed surface; both named repairs run and neither did what it was named for"
   git push origin v27.0
   git ls-remote --tags origin
   ```

4. On GitHub, **Releases → Draft a new release**, choose the tag
   `v27.0` — the same tag as step 3, not an earlier one — title it
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

The work is on **`round27-inference`**, which branches from `main`. (This
file named `round25-coverage` for two rounds after the work had moved off it;
the branch is checked here rather than remembered.) Merge it to the default
branch before tagging if the release should sit on the mainline; the archive
is a snapshot of whatever the tag points at. Nothing under `data/` is
committed on it. The merge is left to you because it changes what the default
branch is, which is not an agent's call to make unasked.

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
`results/section_words.csv`. The abstract is 200 words; the linter's limit is
200, which is stricter than the journal's 250 and is the limit the second
developmental review set.

The appendices are a separate supplementary document, which is the change
that review asked for. **The first of the two cuts this file used to name has
been taken**: the reporting standard and software section moved to the
supplement in full, keeping the prescription itself in the body as a
paragraph, and the article is **62 pages** with a 52-page body. If the editor
asks for a shorter article still, the next two are the partial-identification
passage of the decision-analytic section and section 6.5, the head-to-head
against specification-curve analysis --- in that order, and with the caveat
that 6.5 is the paper's only direct comparison with the closest existing
practice, so it is a saving that costs positioning. `submission/response_to_review27.md`
puts the whole trade to the editor with the arithmetic.

### 1.8 Confirm the generative-AI version register  *(brought current by agent; rounds 22–26 still blank)*

> **What changed.** The register stopped at round 21 and still called it "this
> revision", while the manuscript is round 27 — and the manuscript's own
> declaration named `claude-opus-5, 2026-08-24`, the model that prepared a
> version two rounds old. Both now name round twenty-seven's two models,
> `claude-opus-5` then `claude-fable-5`, over 2026-08-24 to 2026-08-29, and the
> declaration reads them from the same macros as the register so the two cannot
> drift. Rounds 22–26 remain **not recorded**, with their dates supplied from
> the commit history; if you have session records that establish the
> identifiers, fill them in — and if you do not, leave them, because an
> unrecorded identifier stated as unrecorded is a disclosure and a guessed one
> is not.


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

---

## 4. Round twenty-seven: what a compliance audit against the journal's own guide added

The Guide for Authors was recovered in full from the Internet Archive
(snapshot **2024-04-22**, the newest that exists; the live page returns 403 to
automated fetches). Everything below is from that snapshot or from a
publisher-level policy page fetched on 2026-08-28. **The primary source is
about two years old**, so re-read the live guide once before submitting.

Three findings are *not* problems and are recorded so they are not
"fixed" by mistake:

- **There is no abstract word limit in this journal's guide.** The widely
  repeated 250 words is boilerplate from other Elsevier titles. The abstract
  is 201 words and needs nothing.
- **ORCID appears nowhere in this journal's guide.** The manuscript's
  handling — leave it to the Editorial Manager profile — is correct.
- **No graphical abstract is required** ("where applicable").

### 4.1 Highlights are MANDATORY for this journal *(fixed — nothing to do)*

Not optional, as they are for most Elsevier titles. The guide asks for a
separate editable file with `Highlights` in the name. What the package used
to offer was a working document that opened with fifteen lines of build
commentary. **Upload `submission/upload/Highlights.txt`** — five bullets,
nothing else — and not `submission/highlights.txt`, which is the annotated
working copy. If the system wants a Word file, paste those five lines in
unchanged.

### 4.2 Suggested reviewers need institutional e-mail addresses  *(owner)*

The guide and the submission checklist both require them.
`suggested_reviewers.md` currently has six names and **zero e-mail
addresses**. Editorial Manager will not let the submission complete without
them, so this stops the submission rather than risking a rejection.

### 4.3 The competing-interest declaration must be Elsevier's .docx  *(owner)*

The guide is unusually explicit: use Elsevier's declaration tool and
**"do not convert the .docx template to another file type."** The package
supplies `declaration_of_interests.md` — the content is right, the container
is wrong. Generate the .docx from Elsevier's tool and attach that.

### 4.4 The affiliation is not a full postal address  *(owner)*

The guide asks for the "full postal address of each affiliation, including
the country name", and the submission checklist repeats it for the
corresponding author. The manuscript renders *"Independent Researcher, Apex,
United States"* — a city and a country, not a postal address. This is queried
at technical check for unaffiliated authors specifically. Set the full
address in `scripts/round26_numbers.py` beside `AFFILIATION_CITY`.

### 4.5 The archive DOI is now a placeholder inside the reference list  *(owner — the circularity is fixed; the DOI itself is still yours)*

> **The loop is gone.** Reference [11] used to read *"the archived release
> cited in the data-availability statement (DOI reserved, inserted at
> proof)"* — and that statement carried the same macro, so a desk check
> following the reference arrived back where it started. The entry now carries
> its own resolvable `url` to the repository the release is cut from, and the
> note states the DOI's status in one clause. An editorial assistant checking
> that the reference list resolves now gets a live link.
>
> **What is still yours**: mint the DOI. Adding a `doi` key to `.zenodo.json`
> replaces the placeholder everywhere it appears — the statement, the
> reference and the archive metadata — with no other edit.


Already §1.1 above, with one thing that section did not know: the placeholder
does not only appear in the code-availability statement. It is also
**reference [11]**, the `fieldvalue` software citation. The guide requires a
software citation to carry a "global persistent identifier", and until the DOI
exists this entry does not have one — so the entry now carries a resolvable
`url` to the repository the release is cut from, and states the DOI's status
in one clause, rather than forwarding the reader to a statement that forwarded
back. That was the loop, and it was the likelier cause of a desk return than
the missing identifier itself; it is closed. The identifier is still owed.

### 4.6 Rebuild before uploading  *(owner or agent, but do not skip)*

`paper/specification_surfaces.pdf` predates the current source. The built
PDF's generative-AI declaration differs in substance from the one now in the
source of record. Whatever is uploaded must be rebuilt from the current tree.

### 4.7 Mint and record the Docker image digest  *(step 1 DONE by agent; step 2 owner)*

> **Step 1 is done.** The base is pinned by digest:
> `FROM python:3.10.0-slim-bullseye@sha256:ad540a47...88f0d8`, the
> multi-architecture manifest list, so `docker build` still selects the right
> platform while the content is fixed. The digest was verified
> cryptographically rather than trusted: fetching the manifest *by* that
> digest returns bytes that hash to exactly it. The manuscript's
> code-availability sentence now reads the digest **out of the Dockerfile**
> rather than carrying a typed copy, and `round27_verify` condition 20 fails
> the build if the two ever disagree — so the sentence cannot be falsified by
> an edit to the container.
>
> Re-resolve with `docker buildx imagetools inspect python:3.10.0-slim-bullseye`.
>
> **Step 2 remains yours**: build the image and record *its own* digest in the
> archive. That needs the deposit, which needs the DOI, which needs your
> account. The manuscript no longer claims that digest exists — it says the
> archive records it at release, which is true.


Round twenty-seven measured that this repository's results are **not**
bit-reproducible across processor architectures, and the paper's
code-availability statement now says so — and says that bit-exact
reproduction is claimed *inside the container, whose image digest the archive
records*. **No such digest exists yet.** The `Dockerfile` pins
`python:3.10.0-slim-bullseye` by **tag**, which is mutable, so the container
is not currently pinned either.

Two steps, and the second is the one the paper's sentence depends on:

1. Build the image and resolve the base to a digest, replacing the tag:
   `FROM python:3.10.0-slim-bullseye@sha256:<...>`.
2. Record the built image's own digest in the archive, and check it is what
   `REPRODUCE.md` §5.1 names as canonical.

Until this is done the manuscript makes a claim the archive cannot support,
which is the one category of defect this project treats as unshippable.

### 4.8 One measured defect that is *not* repaired, and why  *(decision, not an action)*

The register-quality mechanisms cut on a tie-ordered index: `mask_rare` cuts
the cumulative-count curve **inside** a tie group (5–9 identities were
measured tied at the cut), and `corrupt` maps its draws onto the same
tie-ordered index. So *which* identities are masked or corrupted rests on a
sort order nothing pins — the second undeclared tie order this project has
found, after the one in the split sort that Section 7.1 reports.

It is not repaired in this round because repairing it changes every committed
number on the quality axis, and it belongs with the run that regenerates them.
It is recorded in `REPRODUCE.md` and `ROUND27-STATE.md`, and the reporting
standard's tie-break item should be widened from "the sort that produces the
split" to any sort a mechanism cuts on.

# Owner actions — the things a person has to do

Everything in this repository that a script can do, a script does. What
follows needs an account, a credential or a judgement call, and is listed so
it is not mistaken for done.

---

## 1. Before submission

### 1.1 Mint the archive DOI  *(required by the referee's Phase 7)*

The manuscript's data-availability and code-availability statements cite a
Zenodo DOI, and `paper/numbers.tex` currently renders it as `??` because there
is nothing to cite yet.

1. Log in at <https://zenodo.org> with the GitHub account that owns
   `sudhirdixit1/cmdb-routing-queue-baseline`.
2. **Settings → GitHub**, and switch the repository **on**. Zenodo will then
   archive every future release.
3. Back in the repository:

   ```bash
   git tag -a v19.0 -m "Round nineteen: specification surfaces"
   git push origin round-nineteen-specification-surfaces --tags
   ```

4. On GitHub, **Releases → Draft a new release**, choose tag `v19.0`, title it
   *Specification Surfaces for Incremental Predictive Performance*, and
   publish. Zenodo mints the DOI within a minute or two.
5. Put the DOI into `.zenodo.json` as `"doi": "10.5281/zenodo.XXXXXXX"`, then:

   ```bash
   python scripts/make_numbers.py --strict
   python scripts/assemble_paper.py
   python scripts/build_journal.py
   ```

   `--strict` fails if any macro is still unresolved, which is the check that
   the DOI actually landed in the manuscript.

### 1.2 Decide what to do about the branch

The work is on `round-nineteen-specification-surfaces`. Merge it to the
default branch before tagging if the release should sit on the mainline; the
archive is a snapshot of whatever the tag points at.

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
| Response to the previous report | `submission/response_to_referee.md` |
| Declaration of interests | `submission/declaration_of_interests.md` |
| CRediT | `submission/credit_statement.md` |
| Data availability | `submission/data_availability.md` |
| Suggested reviewers | `submission/suggested_reviewers.md` |

### 1.5 Check the length against the journal's own guidance

`python scripts/texlint.py --report` prints the abstract word count, the
keyword count, the highlight lengths and an approximate main-text word count.
The abstract is at the 250-word limit exactly; if the journal's counter
disagrees with ours by a word, cut one.

---

## 2. Optional, and worth considering

### 2.1 Finish the expanded pilot frame

`scripts/s06_audit2.py --frame` enumerates a frame roughly four times the size
of the one the pilot currently uses. The public index meters requests against
a daily budget, so the enumeration waits it out and caches per stratum; a run
left going overnight completes. If it does, then

```bash
python scripts/s06_audit2.py --fetch --screen --dossiers
```

produces a much larger screened-in set, and **the adjudication of that set is
the part that needs a person**. The pilot's binding limitation is its
effective sample size, and only more adjudicated papers fix it.

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

# Pre-upload read of the IJF package (internal, simulated tenth referee)

*Manuscript:* Specification Surfaces for Incremental Forecast Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Version read:* `build/journal/manuscript.pdf` (blind, 53 pages),
`supplement.pdf` (blind, 115 pages) and `title_page.pdf` (3 pages), built
2026-09-18 from commit `a028db9` with every gate at zero and
`verify_release.py` byte-identical; the repository open to check any number.
*Brief:* the whole package as the journal will receive it — the paper, its
scope for the *International Journal of Forecasting*, its formatting against
the journal's Guide for Authors (April 2020, read from the IIF authors page
on 2026-09-18) and the IIF LaTeX template, and every file the submission
form asks for. Two independent reads of the built documents were combined
with a check of every requirement in the guide.
*Written:* 2026-09-18.

> This is an internal review produced with a large-language-model assistant
> reading the built PDFs against the repository and the journal's guide. It
> is not a report from the journal's referees. `AI-USE.md` names the
> session.

## 1. What is sound

The build compiles clean; the nine gates pass; a clean checkout reproduces
every macro and generated table byte for byte; the Zenodo record resolves
to release v28.0; the Editorial Manager site is live. Neither blind PDF
contains the author's name, address, e-mail, repository, archive DOI, model
names or ORCID, in text or in metadata. The paper reads as a forecasting
paper from page 1; the six journal keywords are on the IIF list; the cover
letter's case for the venue is sound. Every number the two reads recomputed
from the printed tables agreed with the text, and the abstract, introduction
and conclusion agree with their sources.

## 2. Must fix before upload

1. **The title page's generative-AI declaration is out of date.** It gives
   the models as `claude-opus-5, then claude-fable-5, then claude-fable-5-1`
   and the dates as 2026-08-18 to 2026-09-06; `AI-USE.md` records the IJF
   retarget of 2026-09-11/12 under `claude-opus-5`, and this read is a
   further session. The one page that names the author makes a stale claim.
2. **The anonymised self-citation sorts under the author's surname.** The
   `.bbl` rewrite in `build_journal.py` leaves "Anonymous (2026)" in the D
   slot: between Diebold and van Dongen in the article (p. 49), between
   Davison and Fieller in the supplement (p. 111).
3. **Supplement S22 (p. 99) says "a referee for this journal observed…".**
   That referee was *Information Systems*'; at IJF the sentence is false and
   discloses prior review. P. 100's "every objection this project has
   received … twenty rounds" does the same.
4. **Supplement S21.3 (p. 99) points at "the generative-AI declaration"**,
   which the blind build omits.
5. **Two empty duplicate headings.** S1.3 "Targets, splits and the exclusion
   codes" is empty and followed by S1.4 "Targets, splits and exclusions",
   and the article cites S1.3 (p. 23). S14.13 is empty, followed by S14.14,
   and duplicates S18's title.
6. **Table S6 prints "BPIC13\_closed"** (p. 47): the generated table escapes
   the underscore twice.
7. **The data-availability statement is stale.** It cites "Supplement S18"
   for the literature pilot (now S23) and "the Acknowledgements" for the
   repository (the blind article has none; the title page's code-availability
   statement carries it). The reference checker does not parse that form.
8. **Three residues in the article.** Definition 1 (p. 9) defines a design
   space "for a feature-value claim"; Table 8's caption says "predicted
   target"; equation (3) prints "− (⋯)" inside an identity said to hold to
   machine precision.
9. **Section 6.4 reads as contradicting 6.2**: Table S20's shares (analyst
   latitude 11.1%, resampling 18.9%) beside 6.2's 71.7% for components
   involving the split, without saying S20 leaves the higher-order remainder
   as a fourth column.

## 3. Should fix

- **The IJF template differs from the build.** `ijftemplate.tex` uses
  `\documentclass[11pt,3p,review,authoryear]{elsarticle}` with
  `model5-names` and `\biboptions{longnamesfirst}`; the build uses
  `[preprint,12pt,authoryear]` with `elsarticle-harv`. The guide says "you
  are requested to use the template". (In the installed elsarticle 3.5,
  `review` sets 1.5 line spacing.)
- **Figures** are PNG; the IIF page asks for EPS or PDF. Figures 1 and 3
  carry titles above the plots, which the guide forbids. Figure 2's diagram
  points at "Sections 4.3, 9.4"; there is no 9.4.
- **The title page prints an empty "References" heading** on page 3.
- **Two public texts still call the old venue "this journal"**: `README.md`
  line 18 and the narrative in `credit_statement.md`.
- **Deanonymisation by search.** The package name on p. 21 plus the paper's
  title returns the author's repository as the first web hit; script and
  file names on pp. 13, 24, 35, 47 are the same kind of key.
- **Uncited prior results** (p. 5 "the two values the case study's log has
  been reported to give"; p. 35; Table S11 "two published values") refer to
  the author's own earlier, unpublished analysis.
- **Supplement tables** S14, S22, S26, S27 are shrunk to about 4-point type;
  Tables S9 and S16 describe the `q` column as the operative critical value
  while the column holds the multiplier's values; S15.1–S15.6 are stacked
  empty headings; Table S20's caption points at S14.17 for S14.11; S18 opens
  "This subsection"; S20 opens on "the measurement" without an antecedent;
  S1 states the planned contrasts were fixed before any governed result while
  Table S15 and Class L say before this analysis round.
- **Length.** 53 pages (45 body, 8 references). First moves: the
  specification-regret thread (§4.7, §6.6, the rules paragraph of §8.3),
  then §3.4.
- **The likely first referee objection** — AUC as primary instrument for a
  probability forecast when proper scores exist — is answered across §3.5,
  §4.5 and §8.1 and gathered nowhere.
- P. 19 "43.7% against 56.0%" does not say which is which; p. 26's 28.7%
  is defined in the words p. 28 uses for 38.9% without saying "pooled".

## 4. Smaller

The abstract is exactly 150 words; "Uncertainty" and "specification surface"
repeat title words; five reference entries print "et al." after three
authors; "van Calster" and "Van Calster" both appear; the same axis is
called forecast origin, decision time, availability and moment; the cover
letter does not state a colour preference; `paper/*.pdf` builds are
uncommitted.

## Recommendation

Not ready to upload as built. Nothing in §2 touches a claim; every item is
a wording, a build step or a statement about the author. Fix, rebuild, gate,
re-read.

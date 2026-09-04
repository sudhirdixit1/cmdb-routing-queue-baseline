# Response to the eighth review (internal, machine-assisted)

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Review:* `submission/review_round28.md` (2026-09-03), an internal review
conducted with a language-model assistant reading the round-27 PDF against
the repository. Not a journal report; archived, not uploaded.
*Recommendation received:* major revision (narrow)

> Every number in this letter is a macro re-derived from a result file, or
> a count read from the file it names. Where the round's own measurements
> contradicted the plan that was written before them, the letter says so.

---

## R28.1 and R28.2 The operative critical value, and the coverage grid

**Both conceded, and the two turned out to be one problem.** The report
asked for the coverage grid to be re-matched to the design the corpus runs
(R28.2) and for the estimator that attains its level on that design to be
made operative (R28.1). The grid was re-declared to the balanced design ---
every pair's surface family of 180 cells at 400 draws, the modal decision-
curve family of about 1,100 cells at 400, and the case study's own curve
family of 248 at 200 --- under all four regimes, with the tails calibrated at
that design rather than at the 80-draw cell of the previous surface, and the
non-zero-truth regime run on it for the first time.

**What the first re-matched run found, and why it is not the run the paper
quotes.** With the tails matched on per-cell kurtosis alone, the multiplier
and the empirical quantile both covered about 94.5% on the surface family.
That would have retired the paper's sharpest limitation, so it was examined
rather than adopted, and it did not hold: in that synthetic family the two
estimators coincided, where on the corpus's own families the empirical
quantile exceeds the multiplier by a median factor of 1.50 (2.24 on the
admissible curve cells). The kurtosis fit had chosen a 2% contamination share
against the previous 5%, and a 95% quantile of 400 maxima sees a 5%
contamination and not a 2% one, so both the round-27 verdict and the first
round-28 verdict were decided by a grid choice of the tail model that the
corpus's kurtosis does not constrain. The corpus does constrain the ratio,
directly. The calibration now targets it, a synthetic family counts as
matched only if it reproduces the corpus's ratio within its interquartile
range, and the decision rule was extended --- before the second run --- for
the case the first run raised (`PLAN-ROUND28.md` §1.4a). The first run's
files are kept in the archive as `results/s41_r28a_*`.

**What the second run measured, and what the paper now does.** With the
ratio target the surface family's synthetic tails reproduce the corpus's
estimator ratio at 1.25 against a median 1.50 (interquartile range 1.24 to
1.67) --- inside the range --- and the curve family reaches 1.49 against 2.24,
outside it. On the matched surface family (180 cells, 400 draws) the
empirical quantile covers **94.7%** under the corpus's tails and **94.6%**
under a non-zero truth, at a Monte Carlo standard error of 0.5%, against a
nominal 95%; the multiplier covers **91.5%** and **92.6%**. Along the
draw-count ladder the multiplier plateaus (90.9% at 150, 91.5% at 400, 91.2%
at 1,000) while the empirical quantile rises to its level by 400 (77.8% at
33, 93.8% at 150, 94.7% at 400). Under Gaussian draws the two change places
(94.3% against 93.7%), which is what the theory says and what the corpus's
draws are not. The rule adopts the empirical quantile: it passes both tests
and the multiplier fails both. On the curve families the empirical quantile
is about a point short (93.8% and 94.3% on the modal family; 93.6% on the
case study's own) and the multiplier two to four points (91.3%, 92.1%,
91.2%), on a synthetic family that under-reproduces the corpus's ratio; the
article says so where the counts are printed and reports the empirical
quantile as the better of the two rather than as one measured at nominal.

**What changed in the paper.** The empirical quantile is the operative
critical value on every family (`s21_bands.py --operative emp`); both
estimators' edges and labels are written whichever is operative, and every
table prints what the multiplier would have resolved beside the reported
band. The decision-curve family excludes cells that are exactly zero in at
least nine draws of ten by a declared rule before the quantile is taken (2 of
248 on the case study), and the measured widening of the multiplier that
Section 8.2 previously applied becomes the supplement's comparison. The
numbers that moved, multiplier → empirical: resolved cells 890 → 698; median
ρ 0.039 → 0.000; pairs resolving nothing 2 → 8; pairs resolving anything
17 → 11, of which one sign only 12 → 9 (7 beneficial, 2 harmful) and both
signs 5 → 2; directions withdrawn by the minimum resolved share 5 of 12 → 3
of 9; median resolved cells per pair 19 → 2; the mean distance of resolved
cells from the conventional report 0.0556 → 0.0600 AUC (abstract and
highlights); the resolved-cell sign-disagreement rate 16.4% → 13.0%; cells
surviving all three restrictions 38 → 31, with 0 disagreeing under both, so
the withdrawal of the sign-disagreement rate as a headline stands; 14 of 19
pairs still do not resolve the conventional report's own cell; the case
study's decision curve resolves 8 of 31 operating points against the
multiplier's 18 and the pointwise 24. The one uniformly beneficial surface
holds under both estimators, under the empirical quantile's order-statistic
upper end and under every widening the (n, K) calibration could ask for. The
decomposition, the decision-time ladder, the layer ladder, the cohort ×
target reconciliation, the planned contrasts and the calibration screen did
not move, and the verifier shows their macros unchanged.

**What the coverage measurement still does not establish**, said in Sections
4.3, 6.3 and 10: its bootstrap is ideal, so it bounds the critical value's
contribution and not the resampling's; the pointwise interval underneath is
governed by K/n and undercovers where this corpus lives; and the (n, K)
calibration that would widen it is a sensitivity ladder (Supplement S9), not
applied.

The pooled figure of 84.3% is retired. `\covMultNonzeroMedian` is gone from
the macros; a sentence about "the reported design" can only read a macro
derived from the row whose family size and draw count are the corpus's own,
and a verifier condition fails the build if such a macro is quoted without
that row existing under the regime the sentence names.

## R28.3 Revision history in the article

**Conceded.** The scheme comparison of Section 4.1 is stated as a
comparison --- two schemes, one design, two findings --- with the full
treatment moved to Supplement S3.8 and the history removed from both;
Section 10's "two repairs this paper named" is now "two mechanisms this
evidence retires"; Section 4.2's "objection this retires" is "a design, not a
corner". The linter's revision-narrative check gained the phrasings the
report found ("a previous version of this paper", "this paper had never
reported", "repairs this paper named", and their siblings), fails on the
round-27 source, and passes on this one.

## R28.4 Length

**Conceded in part; the yield is measured, and the target is not met.** The
article is 57 pages from 63, and the body's source about 18,300 words from
about 21,400, while the round's own substance --- the re-matched coverage
measurement and the two estimators --- added about 600 words. Out: the
scheme comparison of Section 4.1 and the reduction's rules of Section 3.4 to
the supplement; Section 6.6 to a paragraph; the pointwise simulation of Section 9 to one
subsection; Sections 8.1 and 8.2 merged; Sections 1 to 7 and 10 compressed
paragraph by paragraph; 26 bold lead-ins removed from Section 6
alone and the meta-commentary the report quoted removed. The eleven floats
stay. `summary_of_changes.md` §4 names the next three cuts in order and what
each costs, for the editor to take if the count is binding.

## R28.5 The package and the disclosure

**Conceded in full.** The cover letter is rewritten to two pages and says in
one paragraph that the manuscript was revised through internal adversarial
reviews conducted with a language-model assistant, and that the archive's
review and response files are those reviews and not the journal's. The
upload list carries the manuscript, the supplement, the highlights, the cover
letter, the response to the journal's actual referee report, and a
`summary_of_changes.md`; the letters answering internal reviews stay in the
archive and are described as such in `README.md`. The generative-AI
declaration gives the full span of use from the register's first date, names
every identifier that was recorded, and names the review use beside code and
prose; `AI-USE.md` gains the review row and the round-28 row.

## R28.6 The ten small items

1. Table 4's last column is headed "sign-disagreement rate". **Done.**
2. Section 6.5 names the pair --- BPIC19/duration, sign-changing --- from a
   macro the comparison script now writes. **Done.**
3. The excludes-own-estimate criterion: the round-27 letter is historical
   and is left as written; the comparison the article reports is on 24,624
   cells of both schemes over one design (3.9% → 1.3%), and the scalar-only
   count is in `results/s40_qcheck.csv` per pair under both estimators. **The
   letter's "74 of 3,900" was the retired surface's count and is not
   comparable; this letter says so rather than restating it.**
4. Table 3's header reads "adm. rungs" and its caption says the intercept-
   only rung is not counted; the caption's own revision history ("this table
   was Supplement Table S11 through round twenty-five") is gone. **Done.**
5. Section 9.2's cell and replicate counts are macros, and the article
   distinguishes grid cells from the draw-count ladder. **Done.**
6. The two quantities that were both "1.35" are in separate sentences with
   their own names. **Done.**
7. Contribution 2 is rewritten with the switch. **Done.**
8. `OWNER-ACTIONS.md` says six keywords. **Done.**
9. Reference [11]: owner item, unchanged; `finalise.py` lists it.
10. Section 4.3 says the multiplier is an approximation to the bootstrap
    quantile adopted for Monte Carlo precision and not the Romano--Wolf
    construction as cited. **Done.**

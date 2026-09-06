# Summary of changes since the referee report

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Answers:* the report on the earlier manuscript *Four Choices Behind One
Number*, whose ten major comments `response_to_referee.md` addresses point by
point. Everything below happened after that report, through internal reviews
the author conducted with a language-model assistant (declared in the
manuscript's generative-AI statement and in `AI-USE.md`); every objection
those reviews raised and its disposition is in `REFEREE-LOG.md` in the
archive.

> Every number below is a macro from `paper/numbers.tex`, regenerated from
> the result files, or a count read from the file it names;
> `scripts/check_response_refs.py` checks the section references and the
> word counts against the built manuscript.

---

## 1. What the paper now is

A methods paper. The incremental predictive performance of a recorded field
is defined as a *specification surface* over a design space the analyst
declares --- baseline, pipeline, target, split, decision time, register
quality, metric, operating point --- and three objects are supplied for
reporting one: an exact functional-ANOVA decomposition whose split axis is an
error stratum, so analyst latitude is separated from resampling; simultaneous
max-*t* bands from a pipeline-refitting moving-block bootstrap, at a critical
value whose family-wise coverage is measured against a known answer; and
resolution regions with a robustness index, under a declared minimum resolved
share. The surface is computed through one frozen pipeline on 19 log--target
pairs from 13 public event logs under a registered protocol, and a
configuration management database is evaluated at three decision times on a
public bank log.

## 2. The inference: what changed in this revision, and why

**The critical value.** Two estimators of the max-*t* critical value are
computed on every family: the empirical quantile of the observed bootstrap
maxima (the Romano--Wolf construction) and a Gaussian-multiplier
approximation adopted for Monte Carlo precision. Earlier versions reported the
multiplier. Section 9.2 now measures both on synthetic families matched to
the design the corpus runs --- 180 cells at 400 draws on every pair --- under
four regimes, with the tails calibrated to the corpus's kurtosis *and* to its
own observed ratio of the two estimators (median 1.50 on the surface
families). On that matched family the empirical quantile covers 94.7% under
the corpus's tails and 94.6% under a non-zero truth (Monte Carlo standard
error 0.5), against a nominal 95%; the multiplier covers 91.5% and 92.6%,
and its coverage plateaus from 150 draws on while the empirical quantile's
rises to its level by 400. **The empirical quantile is therefore the
operative critical value**, by a rule written down before the run
(`PLAN-ROUND28.md` §1.4), and the multiplier's labels are printed beside it
in every table.

**What that costs and what it buys.** The reported band is 1.5 times as wide
as the multiplier's on the corpus's own families. It resolves 698 cells
corpus-wide against the multiplier's 890; 8 pairs resolve nothing against 2;
the median robustness index is 0.000 against 0.039. The one uniformly
beneficial surface (BPIC14/duration, all 180 cells) holds under both
estimators, under the empirical quantile's order-statistic upper end, and
under every widening the (n, K) calibration could ask for. On the curve
families the empirical quantile is about a point short of nominal (93.8% and
94.3% on the modal family; 93.6% on the case study's own), on a synthetic
family that reproduces a ratio of 1.49 against the corpus's 2.24, and the
paper says so where the counts are printed; cells that are zero by arithmetic
are excluded from a curve family by a declared rule before the quantile is
taken (2 of 248 on the case study). The case study's decision curve resolves
8 of 31 operating points under the operative band, against 18 under the
multiplier and 24 pointwise.

**What the coverage measurement does not establish.** Its bootstrap is
ideal, so it bounds the critical value's contribution and not the
resampling's; the pointwise interval underneath is governed by the register's
cardinality over the training size and undercovers where this corpus lives;
the (n, K) calibration that would widen it is reported as a sensitivity
ladder (Supplement S9) and not applied. Section 10 carries all three.

**Numbers that moved with the operative band** (multiplier → empirical):
resolved cells 890 → 698; median ρ 0.039 → 0.000; pairs resolving nothing
2 → 8; pairs resolving anything 17 → 11, of which one sign only 12 → 9 (7
beneficial, 2 harmful) and both signs 5 → 2; directions withdrawn by the
minimum resolved share 5 of 12 → 3 of 9; median resolved cells per pair
19 → 2; the mean distance of resolved cells from the conventional report
0.0556 → 0.0600 AUC (abstract and highlights); the resolved-cell
sign-disagreement rate 16.4% → 13.0%; cells surviving all three restrictions
38 → 31, with 0 disagreeing under both, so the withdrawal of the
sign-disagreement rate as a headline stands; 14 of 19 pairs still do not
resolve the conventional report's own cell. The decomposition, the
decision-time ladder, the layer ladder, the cohort × target reconciliation,
the planned contrasts and the calibration screen are untouched, and the
verifier shows their macros unchanged.

**A pooled figure retired.** "84.3% under a non-zero truth" was a median over
six synthetic families matched to the previous surface, none of them the
design the corpus runs; it is gone, and a verifier condition now fails the
build if a coverage macro is quoted as the design's without the matched row
existing under the regime named.

## 3. What changed since the referee's report, by section

| section | change |
|---|---|
| Abstract, highlights, contribution 2 | the bands are described by the critical value's measured coverage; the "short of nominal" wording is replaced by the measurement |
| §4.1 | the two resampling schemes are compared in the supplement (S3.8); the body keeps the two findings without the project's history |
| §4.3 | two estimators of the critical value, which is operative and why; the coverage paragraph reads the matched rows only |
| §6.3 | labels under the operative band; what the multiplier would have resolved; the two shortfalls that remain |
| §6.5 | the pair on which the sub-surface and the full surface disagree is named |
| §8.2 | the decision curve under the empirical quantile of the admissible family; the measured widening becomes the supplement's comparison |
| §9.2 | rewritten around the re-matched grid, the ratio match, the four regimes and the draw-count ladder for both estimators |
| §10 | the band paragraph states what the coverage measurement does and does not establish; the "two repairs" paragraph is two retired mechanisms |
| Tables 3, 4 | the rungs column is labelled as admissible rungs; the last column of the master table is the sign-disagreement rate; captions describe the operative band |
| Supplement S3.5, S3.8, S9, S14.7, S14.18 | the estimator comparison, the moved scheme comparison, the calibration as a sensitivity for the pointwise channel, the curve family's ladder |
| Back matter | the generative-AI declaration gives the full span of use and names the internal-review use |

## 4. Length

The article is 56 pages, from 63: the conclusion ends on page 48, the
declarations and availability statements run to page 49, and the references
occupy pages 50 to 56; the body's source is about 17,900 words, from about
21,400. What came out: the scheme comparison of §4.1 and the rules
for the reduction of §3.4 to the supplement; §6.6 to a paragraph; the pointwise
simulation of §9 to one subsection, its plane and worlds living in the
supplement; §8.1 and §8.2 merged; §§1, 2, 3, 4, 5, 6, 7 and 10 compressed
paragraph by paragraph; 26 bold lead-ins removed from §6 alone. What came in: the coverage measurement's re-matched design and
the two estimators, which is the round's substance. The eleven floats stay.
If the editor needs the article shorter, the next cuts in order, with what
each costs: §6.5's comparison against specification-curve analysis to the
supplement (about a page; it is the paper's only direct comparison with the
closest existing practice); §7.4's reading for a configuration-management
programme to a paragraph (about a page; it is the part a service-management
reader uses); §9.3's plane to a pointer (half a page; the pointwise
shortfall's mechanism then lives only in the supplement).

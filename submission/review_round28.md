# Referee report on the round-27 manuscript (internal, simulated eighth referee)

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Version read:* `paper/specification_surfaces.pdf` built 2026-08-30 07:42 at
commit `250e8e8` (63 pages; supplement 108 pages), plus the submission
package in `submission/` and the result files under `results/`.
*Brief:* a referee for *Information Systems* (Elsevier) reading a
resubmission, with the repository open to check any number.
*Written:* 2026-09-03.

> This is an internal review produced with a large-language-model assistant
> against the repository, in the same way as rounds 19–27. It is not a
> journal referee report and must not be presented as one (see R28.5).

---

## Recommendation

**Major revision, narrow.** Not acceptable as it stands, and closer to
acceptance than any previous version. Two items block, one is an editor-level
trust issue, and the rest are minor. The blocking items are cheap: one is an
arithmetic switch on data already on disk, the other a small simulation.

**Where it stands.** The internal consistency that three earlier reports
attacked is now good: I re-derived about twenty-five identities from the
tables and files (cell counts 4,800 / 9,600 / 29,040 / 273,024; the 890
resolved cells; the median of 19 resolved cells; 14 of 19 reference cells
unresolved; the 12-of-17 one-sign split; 7 marked rows and 5 withdrawn
directions; the 16.7% / 12.5% / 3.75% shares; the decision-time ladder's
three differences; the 52% and 35% layer shares; the decision-curve counts
24 / 18 / 5 / 13) and every one reconciles. The inference surface is a
balanced full factorial; the coverage measurement is honest; the case study
is the part of the paper this journal's readers will use and it is strong.
The paper's best single result — that the one uniformly beneficial surface
survives the band that attains its level — is new this round and is the kind
of result that carries a methods paper.

**Why it is not yet acceptable.** The paper now *has* a simultaneous band
whose coverage it measures at the nominal level, and reports a different one
it measures short of it. For a methods paper whose subject is inference
discipline, that is the round-27 objection moved one step along: last time
the repair was named and not run; this time it is run, measured to work, and
not adopted. Everything else in this report is secondary to that.

---

## R28.1 The operative critical value is the one that undercovers. **BLOCKING**

Section 9.4 measures, on the family matched to the design this paper runs
(180 cells, 400 draws, the corpus's tails), the multiplier critical value at
**91.6%** family-wise coverage (SE 0.6) and the empirical quantile of the
observed bootstrap maxima at **94.7%** (SE 0.5; conservative end 96.6%). The
article then reports every band, region label and ρ under the multiplier,
and calls them "descriptive diagnostics, not guarantees".

The stated reason — "a band that attains its level by being wider is a
different object rather than a correction to this one" — is not a
statistical argument. Both quantities estimate the same $(1-\alpha)$ quantile
of the max-$t$ statistic. The multiplier is an approximation adopted for
Monte Carlo precision (Section 4.3 says so), and Supplement S3.5 shows it
lies *below the entire order-statistic interval* of the empirical quantile on
19 of 19 surface families and 19 of 19 decision-curve families. Where two
estimators of one quantile disagree and one is measured at its level, the
paper reports the wrong one. The empirical quantile is, moreover, the
Romano–Wolf construction the paper already cites for max-$t$ [31]; the
Gaussian multiplier over standardised bootstrap draws is a bootstrap of a
bootstrap and is the source of the shortfall under heavy tails.

**What I ask for.** Adopt the empirical quantile as the operative critical
value for every family, and print the multiplier band beside it as the
narrower one that undercovers. Contribution 2 can then claim what it
currently disclaims. The consequences are large and the paper must carry
every one of them: 698 resolved cells against 890; a median ρ of 0.000
against 0.039; 8 pairs resolving nothing against 2; the 0.0556 AUC figure in
the abstract and highlights; the 16.4% and 38-cell figures of Section 6.4;
the 14-of-19 and 12-of-17 statements of Sections 6.3–6.4; Section 6.5's
9-of-19; Table 4, Table 6, Table 7, Tables S9 and S16; and Section 8.3's
5-of-31, where the empirical quantile on the admissible decision-curve family
should replace the measured 2.61 factor (the factor is itself a calibration
of the kind Section 6.3 declines for the surface families). The paper has
already shown the headline survives: BPIC14/duration is uniformly beneficial
under the empirical band, all 180 cells. Report the rest.

Two things to say in the same breath, so that the switch is not oversold.
The coverage measurement uses an ideal bootstrap and is an upper bound; the
pointwise interval underneath still carries the $K/n$-governed shortfall of
Section 9.3, which the empirical quantile does not repair. And the decision-
curve families' empirical quantile is inflated by cells that are zero by
arithmetic (S9.6); exclude those from the family by a declared admission
rule rather than widening around them.

## R28.2 "84.3% under a non-zero truth" is pooled over designs the corpus does not run. **BLOCKING — the R27.19 class, again**

Section 10 says: "91.6% on the family matched to that design under this
corpus's tails, and 84.3% under a non-zero truth, against a nominal 95%".
The response letter says the same. In `results/s41_coverage.csv` the
non-zero regime was run on six families — three decision-curve families of
534, 1,100 and 2,966 cells at 40, 80 and 150 draws, and three surface
families of 120, 180 and 480 cells at 33, 80 and 150 draws — and **84.3% is
the median over those six**. The family matched to the reported design (180
cells, 400 draws) does not exist under the non-zero regime; the only cell at
400 draws is the heavy-regime draw-count ladder. So the sentence places a
matched number beside a pooled one as if they were the same kind of thing,
which is exactly the defect R27.19 records the paper making three times
last round.

Worse for the grid than for the sentence: every cell of the coverage grid
except the ladder's 400-draw point is matched to the *previous* surface.
No current pair has 120 or 480 cells; none runs 33, 80 or 150 draws; the
"largest family of all" (2,966 cells) no longer exists, and the modal
decision-curve family is now about 1,100 cells at 400 draws. Section 9.4's
"7 surface families" are one matched cell and six that match nothing. The
script's own comment still says 400 draws "is not affordable on the corpus".

**What I ask for.** Re-declare the grid to the balanced design — whole-
surface 180 × 400 and decision-curve ≈1,100 × 400, plus the case study's own
curve family — under all four regimes and all five candidates; quote
matched numbers only; keep the draw-count ladder as the sensitivity it is;
and add a verifier condition that any coverage macro quoted as "matched to
the reported design" is read from the matched row. Decide the R28.1 switch on
that run's result, by a rule written before it runs.

## R28.3 Revision history in the article. **MAJOR**

Section 4.1: "A previous version of this paper named the repair … and did
not run it"; "which this paper had never reported". Section 10: "two repairs
this paper named, both run, and neither did what it was named for". The
paper's own linter bans "an earlier version of this work"; these are the same
sentence in other words. A journal reader has no previous version. State
the comparison, the result, and the retired mechanism; the history belongs
in the response letter. (The round-21 review made this point and the paper
agreed with it.)

## R28.4 Length and repetition. **MAJOR**

Sixty-three pages, fifty-seven of body. Section 10 (2,244 words) restates
Sections 4.1, 6.3 and 9.4 almost in full; Section 4.1's scheme comparison
(about 1,000 words) is a supplement item with a two-sentence summary in the
body; Section 6.6 is a null check; and once R28.1 is adopted, Section 9.4
and Supplement S9 shrink, because the story becomes "the multiplier
undercovers, the empirical quantile does not, and here is what the level
costs" rather than a calibration derived and not applied. The prose is also
mannered in places — "which is the paper's own thesis arriving at the
paper", "we say so plainly", and a density of bolded lead-ins that a reader
registers as emphasis on everything. Say each of those once. A target of
about 50 pages is reachable without cutting a concession.

## R28.5 The submission package describes internal reviews as if they were referees. **MAJOR — editor-facing**

The cover letter narrates "six further developmental reviews", "an
independent reader with this journal's brief, no knowledge of what had
changed", and `OWNER-ACTIONS.md` instructs uploading six response letters to
those reviews as prior correspondence. Nothing in the package says these
reviews were internal, produced with a language-model assistant against the
repository, which is what `REFEREE-LOG.md`, `DECISIONS.md` and the plan
files record. An editor will ask who the reviewers were, and the honest
answer is not the one the letter implies. Elsevier's policy asks for
disclosure of AI use in the research process; a simulated referee is a use.

**What I ask for.** A cover letter of at most two pages that says the
manuscript was revised through internal, machine-assisted adversarial
reviews recorded in the archive; that answers the journal's actual referee
report (the one real review) in a separate document; and that uploads
nothing else as correspondence. The generative-AI declaration should give
the full span of use (the register starts on 2026-08-18, the declaration
says 2026-08-24) and name the review use alongside code and prose.

## R28.6 Smaller items, each checked

1. Table 4's last column is headed "misreport rate" while Section 6.4
   withdraws the claim that a sign disagreement is a misstatement. Head it
   "sign-disagreement rate".
2. Section 6.5: "the full surface is sign-changing or conditionally harmful"
   — under Definition 3 the corpus carries no conditionally harmful surface.
   Name the pair and its label.
3. Response letter §1: the success criterion is "74 of 3,900 cells" (the old
   scalar surface); the result reported is "3.9% to 1.3%" on 24,624 cells
   that include the 31 decision-curve instruments. Give the count on the
   scalar family under both schemes so the criterion can be checked.
4. Table 3's "rung" column counts *admissible* rungs (4 on BPIC14, where
   Table 2's ladder has 5). Say so in the header; a reader multiplying
   Table 3 reaches 4,800 only if they know it.
5. Section 9.4: "2,000 replicates in each of 24 cells" — the coverage file
   carries 28 grid cells; print the count from a macro.
6. Section 4.3 uses "1.35" twice for two different quantities (the order-
   statistic interval width of the empirical quantile; the width ratio of
   the empirical band). Distinguish them.
7. Contribution 2 says coverage is "short of nominal everywhere in this
   corpus's configuration"; Section 9.4 reports an estimator at 94.7%.
   R28.1 dissolves this; otherwise the contribution must say "the reported
   band".
8. `OWNER-ACTIONS.md` §3 says seven keywords; the manuscript has six.
9. The reference list carries "DOI reserved" for the archive [11]; the
   round-21 review said a manuscript should not be submitted in that state
   and the project agrees. Owner item.
10. Section 4.3 should say in one sentence that the multiplier is an
    approximation to the bootstrap quantile adopted for Monte Carlo
    precision, and that it is not the Romano–Wolf construction as cited.

## What I did not find

No numeric inconsistency between a table and the prose describing it in
Sections 5–8, which is where the last three reports found theirs. The
decomposition, the decision-time ladder, the layer ladder, the cohort ×
target reconciliation and the calibration-screen counts all reproduce from
the files. The stationarity diagnostic and the prefix pilot are reported at
the strength the evidence supports. The reproducibility disclosure is more
candid than most published work.

## Predicted decision on this version, and on the revised one

As submitted: **major revision (narrow)**. With R28.1–R28.2 done by the
rule the plan states in advance, R28.3–R28.5 done, and the DOI minted:
**accept with minor revision** is the realistic ceiling, and the paper would
deserve it.

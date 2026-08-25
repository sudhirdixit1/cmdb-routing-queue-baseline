# Round twenty-one — the developmental review's twelve major comments

The report answered here is `submission/review_round21.md` (the full text as
received). Its verdict is **major revision**, with a note that a strict
reviewer would say reject-and-resubmit on M1 and M12 alone. Its own plan is in
five phases and this file follows it.

The three findings that decide the outcome:

* **M1** the case study's headline number appears with two values and two
  signs, one of them Holm-rejected. The paper's own harness exists to make
  that impossible and did not.
* **M3** two of the four new reporting objects (resolution regions, the
  robustness index) rest on bands the paper itself declares undercovering on
  its own corpus.
* **M12** ninety-seven pages written as a running commentary on the project's
  own errors. Nobody finishes it.

## Phase 1 — correctness

| id | comment | action | artefact |
|---|---|---|---|
| P1.1 | M1 | run the τ ladder on **both** cohorts, print the reconciliation, name the cohort in every §7 caption, rewrite PC3's estimand text | `s32_cohort.py` → `s32_reconcile.csv`, `tab:cohort` |
| P1.2 | M8c | PC3's one-sided p vs two-sided basic interval | `s32` re-derives both from `s24_draws` |
| P1.3 | M8a,b | label the aggregation behind 28.7 / 32.8 / 35.3 | new column in `tab:sobol`; `tab:misreport` names its measure |
| P1.4 | M8d,e | Table 5 on one basis; state the master file carries the intercept-only rung | `s25` re-emit, `tab:denominator` |
| P1.5 | M9 | excluded pairs out of Table E.24 | `s09`/held-out table filter |
| P1.6 | M10 | every corpus statistic twice: 19 pairs and the 8 ITSM pairs | `s34_family.py` → `tab:family` |
| P1.7 | M1 | verifier condition: one value per named quantity per cohort | `round21_verify.py` |

## Phase 2 — the two weak objects, and the four axis complaints

| id | comment | action | artefact |
|---|---|---|---|
| P2.1 | M3 | coverage-calibrated critical value from a denser (n,K) plane; regions and ρ recomputed under it | `s33_calibrate.py` → `s33_lambda.csv`, `s33_regions.csv` |
| P2.2 | M4 | misreport restricted to resolved cells, and magnitude-weighted | `s34_misreport.py` |
| P2.3 | M5 | cost-asymmetric utility and a desk threshold distribution; regret demoted to a check | `s35_utility.py` |
| P2.4 | M2 | τ as a genuine axis: cohort-at-τ and feature snapshot at τ, not only the admissible set | `s38_tau.py` |
| P2.5 | M6 | head-to-head against specification-curve analysis as practised | `s36_sca.py` |
| P2.6 | M7 | learner and encoding crossed rather than confounded | `s37_axes.py` |

## Phase 3 — restructure and cut

Target: **35–40 pages of main text.** Main text sections and page budgets are
the review's. Everything else moves to `paper/supplement.tex`, built as a
separate PDF with its own numbering (S1, S2, Table S1…).

To the supplement: Appendix D (corrections), G (literature pilot), H (noisy
world), J (harness), Tables 17–18, 21–23, Appendix E, Appendix F.

Out of the main text entirely: every "an earlier version of this work", every
"correction Cnn", every aphorism, every aside addressed to a referee. One
paragraph in §1 says the archive carries the correction register.

Abstract under 200 words. Six keywords. Five highlights at ≤85 characters.
Model name, version and date in the AI declaration.

## Phase 4 — make the case study land

One subsection relating the register layers to CSDM-style CI-class layering,
and the quality mechanisms to how CMDB decay actually arises (discovery lag,
unreconciled duplicates, desk-populated affected-CI).

## Phase 5 — response

`submission/response_to_review21.md`, one paragraph per M-number, each naming
the table or figure the change lives in, plus the M1 reconciliation table
inline and a diff summary of what moved.

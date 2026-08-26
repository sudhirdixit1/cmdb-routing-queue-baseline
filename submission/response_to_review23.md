# Response to the two pre-submission referee reports

Before submitting, the manuscript was sent to two independent readers with
this journal's brief, no knowledge of its revision history, and access to the
repository to check any number they doubted. One read as a methodologist, one
as an information-systems and process-mining referee. Both returned **major
revision**. This document answers both, and it is included in the submission
because two of their findings changed numbers the paper had already published
and a reader is entitled to see that stated rather than discovered.

Every finding was reproduced from the deposited files before it was acted on.
The two reports agreed on four points and each found something the other did
not; the four shared points are answered first.

---

## The four both referees raised

### A. The simultaneous band's critical value is contradicted by the paper's own second estimate of it

**Conceded, and it is the most consequential thing either report found.**

`results/s21_critical.csv` has always written two estimates of the same
max-$t$ critical value side by side: the Gaussian multiplier quantile `q`,
which the bands use, and the empirical quantile `q_emp` of the same $B$
observed maxima. In twenty-two rounds nobody compared them. **`q` lies below
the entire order-statistic interval of `q_emp` on 15 of 19 whole-surface
families and on all 19 decision-curve families**, in the anti-conservative
direction — median ratio 1.29 and 2.09 respectively.

The manuscript's defence of the multiplier was that the empirical quantile is
imprecise (median order-statistic width 2.0 against 0.04). That is true, it is
an argument about variance, and it does not touch a systematic one-sided gap.
The mechanism is not the draw count: a Gaussian multiplier reproduces the
empirical *covariance* of the standardised draws and hence only the excursions
a Gaussian process makes, and these draws are heavy-tailed.

What it costs, from the deposited bands file:

| | multiplier | empirical |
|---|---|---|
| resolved whole-surface cells | 1,150 | **995** |
| resolved decision-curve cells | 3,066 | **613** |

**What we did.** `scripts/s40_qcheck.py` computes both, per family and pooled.
Section 4.3 has a new paragraph stating the disagreement, its direction and
its mechanism. Section 6.4 reports the empirical count as a fourth setting
beside the three calibration settings, and notes that it moves the resolution
by more than the calibration does. Section 8.3 now states that the
decision-curve family is **not** coverage-calibrated — which the manuscript
had never said — and that its counts are upper bounds under the empirical
value. Section 11 carries it as the sharpest limitation in the paper.

**What we did not do, and why we say so.** Nothing here measures the band's
*family-wise* coverage against a known answer; the simulation validates the
pointwise interval only. The methods referee names this as the single most
important fix and is right. It is a new experiment — family-wise coverage over
synthetic families matching the corpus's sizes, draw counts and tail behaviour
— not an edit, and it is not in this revision. What we have done instead is
report both estimators and what each resolves, so that a reader who prefers
the conservative one has the numbers, and name the experiment that would close
the gap.

### B. "No surface is uniformly beneficial" is unreachable by construction

**Conceded.** A cell whose *point estimate* is negative can never be
beneficial at any critical value, and all 19 pairs have one, so the label was
ruled out before any band was computed. Reporting "zero at every setting" as
robustness presented invariance to something the label does not depend on. For
the same reason $\rho = 1$ is not attainable for any pair in this design.

Section 6.4 now leads with the informative reading — of the 13 pairs that
resolve any sign, 9 have no harmful cell and 4 resolve both — and says the
uniform-beneficence count needs none of the apparatus. The Conclusion's
first bullet states what is true of the point estimates instead.

### C. The headline is quoted on the population the paper concedes is the wrong one

**Conceded.** The pooled resolved-cell misreport rate is 7.5%; on the eight
ITSM pairs it is 3.6% and on the other eleven 22.2%, and Section 6.6 already
said the corpus figure is driven by the pairs Section 5.4 names as
construct-validity threats. The abstract, the Highlights and the Conclusion
printed only the pooled figure. All three now carry both, and the abstract
also carries the 13-and-4 split. The Highlights are generated from the macros,
so the first line an editor reads cannot drift from this again.

### D. Length

**Conceded.** The practice pilot and the correction register are out of the
submission entirely — removed to the archive rather than compressed or moved
to the supplement, which is what both referees asked for and what the previous
review's eleventh comment had asked for before them. Section 9.3 states in
four sentences that the prevalence of one-number reporting is not established
here and that the paper's argument does not need it.

---

## What the methodological referee found alone

### E. The estimand was never defined as a population quantity

**Conceded.** Equation (1) is written on a fixed train/test split, so as
printed $V_s(f)$ is a deterministic functional of the log and an interval for
it covers with probability 0 or 1 — while Section 4.1 resamples the training
half precisely because the analyst does not want to condition on it. The two
were inconsistent and the paper never reconciled them.

Definition 2 (Section 3.2) now gives the population estimand
$\vartheta_s(f)$, states that the split rule and the pipeline are *part of*
the estimand rather than nuisances to be averaged away, and says that every
printed cell is an estimate of it and that "resolved" is a statement about it.

### F. Percentile intervals were printed where the paper says every interval is basic

**Conceded**, and it is the same class as the `PC3` discrepancy below: `s08`
computes `np.nanpercentile` and `s38` the basic construction, and the two were
printed three lines apart with identical point estimates. Section 7.2 now
takes its ladder numbers from one run under the basic construction, and the
`ESTIMANDS` guard has been extended to interval endpoints (`INTERVAL_SOURCES`)
so that an endpoint must re-derive from the run the manuscript says it comes
from.

### G. "Coverage is governed by $K/n$" is stronger than the grid supports

**Conceded.** Two cells at nearly the same ratio cover 0.780 and 0.613, and
holding $K$ fixed at 1,000 while moving $n$ from 2,000 to 8,000 moves coverage
from 0.453 to 0.613. Section 10.3 now says the ratio captures most of the
dependence and not all of it, gives both counterexamples, and states that the
calibration — a function of the ratio alone — inherits the residual.

### H. Figure 2's caption promised intervals the figure does not contain

**Conceded**, and there was a second defect underneath it: `set_xlim(0, 1.02)`
clipped exactly the bars that exceed one, which several do, because each
segment is a median over instruments and medians do not add. The limit is
taken from the data now, a dotted rule marks one, and the caption explains
both the absence of intervals and the sums.

---

## What the information-systems referee found alone

### I. $\tau_1$ and $\tau_2$ are not the same cases

**Conceded, and this changed a headline number.** Table 8's caption said the
two differ "only in what is known about the same cases"; its own columns said
44,513 against 45,455, because 942 incidents have no interaction record. The
clean population/information separation is the operational contribution of
Section 7.2 and was quoted again in the Conclusion.

`s38` now also runs $\tau_2$ restricted to $\tau_1$'s population — same 44,513
cases, same prevalence. The corrected decomposition:

| step | what changes | value |
|---|---|---|
| $\tau_0 \to \tau_1$ | population | $-0.0297$ |
| $\tau_1 \to \tau_2$ matched | **information alone** | $-0.0099$ |
| $\tau_2$ matched $\to \tau_2$ | the 942 unmatched incidents | $-0.0076$ |

The information channel is $-0.0099$, not the $-0.0175$ the paper reported:
**it had been overstated by three quarters.** The verifier checks that the two
steps sum to the unadjusted one and that the matched cohort really carries
$\tau_1$'s case count.

### J. The same contrast was printed with two intervals

**Conceded.** `PC3` appeared as $[-0.00161, +0.01217]$ in Section 4.4 and
$[-0.00059, +0.01210]$ in Table S8. Both were right about their own file —
400 draws and 2,000 draws — and the point estimate agrees to seven figures.
What was wrong is that the article quoted the 400-draw interval in the same
paragraph as the 2,000-draw budget, beside a table printing the other, under a
supplement abstract promising that a quantity cannot differ between the two
documents. Every `PC3` macro now comes from the planned-contrast run.

### K. Two prevalences for one cohort

**Conceded.** `s08` records the test half's prevalence and `s38` the whole
cohort's; Section 7.1 attached the first to the 45,455-case cohort and then
set it against a whole-cohort figure for the other target. The cohort's
prevalence is the cohort's now and the test half's is a separate macro, named
as the test half where it appears.

### L. The layer conclusion overstates its table

**Conceded.** "The coarse layers are close to free" is not what Table S1
shows: on handover the item's type alone is worth $+0.134$ against the item's
$+0.257$, and on duration $+0.045$ against $+0.129$. Section 7.6 now gives
the layer figures per target and makes the claim that survives — about the
item's *marginal* contribution over the subtype, $+0.109$ on handover — and
says these are on the registered targets rather than the section's own.

### M. The exclusion ledger is still not complete

**Conceded.** A log offered to the held-out set's rules and excluded by them
appeared in neither the admitted pairs nor the ledger. The ledger takes a
third source now, so "every downloaded log" is true as printed.

---

## The two typesetting defects worth naming

`to_latex(escape=True)` escapes what you pre-escape: `50\%` reached the PDF as
`50\textbackslash %`, and a math column heading as literal dollar signs. Both
are fixed at the generator. Both documents now build with **zero overfull
boxes**, and `build_journal.py` reports the supplement's count as well as the
article's — it had been reporting only the article's, which is why seventy
overfull boxes in the supplement had gone unnoticed for four rounds.

---

## Where this leaves the manuscript

Two independent referees, blind to its history, returned major revision rather
than reject, and between them found one defect that changes a published number
(I), one that changes what an inferential object supports (A), and four that
change how a result must be described (B, C, E, G). All are fixed or, in the
one case where the fix is a new experiment rather than an edit, stated as an
open limitation with the numbers a reader needs to take the conservative
reading.

`verify_numbers` re-derives 165 macros independently under 25 consistency
conditions with zero failures; `texlint`, `claim_registry` and
`check_response_refs` pass; provenance is accepted for all 38 analysis
scripts; and both documents build with zero errors, zero undefined references
and zero overfull boxes.

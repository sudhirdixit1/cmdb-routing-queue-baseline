# Response to the seventh referee report

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Recommendation received:* major revision (narrow)

> **STATUS: DRAFT — round 27 in progress.** Passages marked `⟨PENDING⟩` await
> the run this round is built on. Every number that reaches the final version
> is a macro re-derived from a deposited result file; nothing below is typed
> from memory. Delete this block before submission.

---

Thank you for a report that concedes the paper's honesty and then declines to
accept honesty as a substitute for the work. That is the right judgement and
we have not argued with it.

**The report's central charge, in its own words:** the paper ships its
central inferential object as a diagnostic while its own Section 11 prices
the repair at "a change to one function and a re-run" — and a methods paper
whose subject is inference discipline cannot do that. We agree. Round
twenty-seven runs it.

---

## 0. One thing said at the top

Three of the report's findings were **already repaired before the report was
written**, in commit `a03b560` of 2026-08-26, and the reviewed PDF predates
that commit. We record this rather than claiming the repairs as new work:

| the report's finding | disposition |
|---|---|
| the master table prints directional labels that Definition 3 withdraws | repaired in `a03b560`; the applied label is now the `region` column with its resolved share beside it, and `round27_verify` condition 1 compares the two tables cell by cell |
| "that pair carries 9,600 cells" is the log's count, not the pair's | repaired in `a03b560`; the pair and the log now carry separate macros, and condition 4 requires the log's to be the pair's double |
| the inference share is quoted against the wrong denominator | **not** previously found; repaired this round, see §3 below |

The same commit repaired three further defects of the identical class that
the report did not find — a caption ordinal that had gone stale as the ladder
grew, a rung interval quoted from a different run at a different draw count
than the table beside it, and a layer ladder presented as reconcilable with a
table computed on a different cohort and target. All six are now conditions
in `round27_verify.py`, exercised against the exact defect each replaces.

We mention the three the report missed not to score a point but because it
bears on the report's own diagnosis: this class of defect — *a macro is
right, a table is right, and the pair contradicts* — is the failure mode a
paper about auditability can least afford, and finding six of them says the
class needed a gate rather than a proofread. It now has one.

---

## 1. The blocking finding — the band is delivered as a diagnostic

**Conceded in full, and run.** ⟨PENDING: the outcome of `s44_designed.py`⟩

The report is right that Section 11 named the repair and did not run it, and
right that the excuse — cost — is not available to us when our own text
prices the fix at one function. Two things were wrong and both are now
changed rather than described.

**The resampling scheme.** A moving-block resample holds about $1-e^{-1}$ of
the rows of a draw, so a register level present in few rows is absent from
many draws, and a refit that cannot see a level is a refit of a smaller
register than the estimand is about. The bootstrap distribution is displaced;
the displacement is a bias, not a variance, so it does not shrink with $n$
while the interval's half-width does. `spec.block_weights` replaces the
subset with a weight vector — Dirichlet weights drawn per moving block, so
the temporal dependence survives and every row, hence every register level,
is present in every refit.

The visible symptom was a pivotal interval excluding its own point estimate
on 74 of 3,900 cells. That count is the success criterion, because it is a
defect a reader can see without believing any theory about why it happens.
⟨PENDING: the count under weights; the target is zero.⟩

**The surface, and the draws.** The old inference surface was chosen by row
count — four learners on the case study and two elsewhere, three quality
conditions except on the largest logs. It was axis-complete and it was
*unbalanced*, which is why the decomposition could not be computed on it and
why its cell mix differed from the declared surface's. Section 11 asked for a
resolution-IV fraction. What round twenty-seven runs is stronger: one design
on every pair — 2 learners × 2 splits × 3 quality conditions × 3 rungs, 36
cells, 180 scalar members, balanced and orthogonal, which is a full factorial
and not a fraction of one. It costs less per draw than the old surface did,
and that is what pays for the third change: **400 draws on every pair**,
against 40 to 150 before, which is the count at which our own coverage
measurement says the band attains its level.

Three consequences we now claim rather than concede:

1. The "corner, not a design" limitation is retired. The decomposition can be
   computed on the inference surface as well as the declared one.
2. Every pair contributes the same 180-cell family, so a corpus median no
   longer mixes families that differ in shape.
3. ⟨PENDING: measured family-wise coverage, including under the non-zero-truth
   regime `s41_bandcoverage.py` adds this round.⟩

**On the labels.** If the measured coverage supports it, region labels and
$\rho$ become inference and the front matter says so. If it does not, they
stay descriptive diagnostics and the front matter keeps saying *that* — we
will not describe a band as covering because we would like it to.
⟨PENDING: which.⟩

**One design choice we state rather than leave to be found.** The three rungs
are half-of-intake, intake, and intake-plus-the-free-field, so the
half-of-intake rung an earlier report called a straw baseline is a third of
the family every label is computed over. We keep it. It is admissible by
declaration, and dropping it after seeing which cells resolve would condition
the family on the answer — the precise move this paper exists to argue
against. Note also that including an impoverished rung can only make a
directional label *harder* to earn, so the choice errs conservative.

---

## 2. The decision-curve band's measured widening was never applied

**Conceded; it was arithmetic and it is now applied.** ⟨PENDING: `s49_dcaband.py`⟩

The report is right that this one had no excuse at all: Section 10.4 measures
that the decision-curve families need a multiplicative widening of 1.90 to
2.05, Section 8.3 printed counts from the uncorrected band, and Section 11
told the reader to distrust them. Widening an already-computed critical value
costs matrix arithmetic and no refits.

⟨PENDING: which factor was applied and why (the all-cells factor against the
one excluding the 841 degenerate cells where both arms treat every case alike
and the net-benefit difference is zero by arithmetic); the corrected counts
against the uncorrected 24 pointwise / 18 simultaneous; and whether any
conclusion did not survive it.⟩

If the correction removes a finding, the finding goes. We checked the one
that would have mattered most and it is not exposed: the promise-versus-
delivery figure — 1.71 true positives per thousand at the earlier decision
time against 0.003 at the later one — is a net-benefit comparison over a
declared distribution of exchange rates, computed in `s35_facts.csv`, and
does not rest on the simultaneous band's resolved-threshold count. It stands
unchanged.

What the correction does move is the band claim itself, and it moves it a
long way: the thresholds the whole-curve band resolves fall from 18 of 31 to
8, and the surviving 8 are **not contiguous**. We report that rather than
soften it. The honest reading is the one the paper has been making about
everyone else's work and must now make about its own — a decision curve read
across its range while priced pointwise has claimed something it did not pay
for, and once it does pay for it, most of the range stops being sayable. The
paper's operational conclusion about the decision time survives because it
never depended on that band; its inferential conclusion about the curve does
not, and Section 8.3 now says which is which. ⟨PENDING: final wording once
the factor choice is settled.⟩

---

## 3. The inference share was quoted against the wrong denominator

**Conceded.** The macro was computed as observed inference cells over
*computational* cells — a denominator that includes the intercept-only rung —
and then used at four call sites, three of which describe it as a share of
*admissible* cells, which by the paper's own definition excludes that rung.
One macro was serving two denominators, so at least one call site was wrong
wherever the two differed.

The repair is two macros, each derived from the axis declaration rather than
typed, used at the call sites whose sentences name their denominator; plus a
condition that recomputes both from the files and fails if they agree.
Because round twenty-seven's design also makes the share non-uniform across
pairs — the case study's family is now a smaller fraction of its much larger
admissible set — the quantity is reported per size class rather than as a
single median. ⟨PENDING: the values.⟩

The report is also right that this defect is the same species as the six in
§0. The generalisable repair is the sweep now in `round27_verify.py`: every
macro naming a per-pair or per-surface count or share is recomputed from the
axis-level declaration, so the next one of these fails the build rather than
reaching a referee.

---

## 4. Reproducibility: a discrepancy we found ourselves and are disclosing

⟨PENDING: the `hgb` cross-machine finding and its disposition.⟩

The short of it: the boosting learner does not reproduce this repository's
committed results across machines at identical pinned dependency versions,
while the logistic learner reproduces to 5e-10. No gate caught it, because
the release check re-derives macros from committed result files and never
re-runs an analysis. The manuscript claimed one-command reproduction without
qualification. A referee who tried it on their own machine would have found
this before we told them, which is the worst possible order.

We would rather be the ones who found it. ⟨PENDING: whether it is thread
nondeterminism and therefore fixable by pinning, or platform nondeterminism
and therefore a disclosed tolerance; the gate that now executes the claim
rather than asserting it; and the corrected wording of the code-availability
statement.⟩

---

## 5. Presentation, compliance, and the smaller items

**The generative-AI declaration** now carries Elsevier's template statement
and the two facts that belong with it, and nothing else; the
literature-pilot description that had accumulated in it is where the pilot
is, in Section 9.3. One substantive change came out of the edit and is worth
flagging: the declaration's assertion that no generative model produced,
imputed, augmented or selected any datum, result or citation was
*unscoped*, and was safe only because the pilot carve-out followed it. The
supplement does report prevalence estimates from adjudications that are
machine-assisted. The sentence is now scoped — "behind a claim of this
paper" — which is what it always meant and now says. `credit_statement.md`
is scoped to match.

**The keyword "predictive process monitoring" is retired**, replaced by
"event logs". Section 11 states that prefix length, prefix bucketing and
sequence encoding are not axes of this design space and cannot be, and that
no result about that literature's benchmark is claimed; the prefix pilot is
one log, one register, no bucketing and no sequence encoder, and says of
itself that it does not make this a predictive-process-monitoring paper. A
keyword is a claim of topical membership, and we should not make one the body
disclaims.

**Length.** ⟨PENDING: the measured cut. Target 42 pages of body; the
reduction is taken in Sections 4, 6, 10 and 11, which are being rewritten
against the new numbers anyway, and the largest single saving is Section 11's
re-derivation of material already stated where it was computed.⟩

**The archive DOI.** ⟨PENDING — owner action. The report declined "reserved,
inserted at proof" and it was right to: a paper whose strongest claim is
reproducibility cannot ask a referee to take the artefact on trust.⟩

---

## 6. What round twenty-seven does not do

Stated here so that nothing above implies otherwise.

- ⟨PENDING: the crossed family × encoding decomposition beyond the case
  study's log, if Phase 2c does not run.⟩
- The corpus is still a family of related prediction problems rather than
  replications of one finding, and every corpus statistic is still about
  sensitivity rather than about a universal register value.
- The stationarity and mixing the moving-block construction needs are
  diagnosed this round but not tested in the sense a formal test would mean.
- The case study is still one bank's estate on one public log, with the
  admissibility question at its centre settled by probability rather than by
  a timestamped field-value history.

# Response to the seventh referee report

*Manuscript:* Specification Surfaces for Incremental Predictive Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Recommendation received:* major revision (narrow)

> **One item is still open and it is the author's, not the analysis's:** the
> archive DOI and the container image digest, both noted below. Every number in
> this letter is a macro re-derived from a deposited result file; none is typed
> from memory.

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

**Conceded in full, and run — and the run did not vindicate the repair.** We
report that first because it is the finding.

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

**We ran the comparison, and it did not go the way Section 11 predicted.**

The mechanism is removed completely. Register levels present in a draw go from
**80.8%** — 60.2% at worst — to **100% by construction**. The starkest
consequence goes with it: on the old surface **150 cells of 3,900 could not be
given a band at all**, because a resample dropped the arm from enough draws
that the median down its column was undefined. Under weights that count is
**zero**. That pair changes the design as well as the scheme, so we also ran
the multinomial arm on *this* design at the same draw count, which isolates
the scheme: **270 of 3,420**, against zero. The clean comparison is the larger
one, and Section 4.1 now prints both rather than only the flattering pair.
We had never reported these cells at all: they were not resolved, so they
were counted as *unresolved*, beside cells that were banded and straddled zero.
Section 4.1 now reports them, and a verifier condition requires the count to be
printed whatever it is.

**And the symptom survives the removal of its supposed cause.** The interval
that excludes its own point estimate falls from 3.9% to 1.3% — better, not
fixed. The displacement's median barely moves, 0.0050 to 0.0041, and its
maximum is slightly *worse* under weights.

So level loss was offered as the explanation of the displacement, and removing
level loss entirely leaves most of the displacement standing. **It was not the
main cause, and we do not know what is.** We think this is the more valuable
outcome: the round retires a mechanism the manuscript asserted, on evidence the
manuscript generated, and no amount of reasoning about $1-e^{-1}$ would have
shown it. The weighted scheme is adopted anyway — it removes a real defect and
is slightly more conservative — but not on the grounds we gave for wanting it.

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

1. The "corner, not a design" limitation is retired, and not by assertion: the
   exact functional ANOVA now runs on the inference surface — 95
   decompositions, 19 pairs by 5 instruments, 36 cells each, no failures. We
   report alongside it that its leading axis agrees with the declared
   surface's on a minority of pairs, and that this compares two designs which
   do not declare the same levels rather than showing either
   unrepresentative. The tempting sentence — that one confirms the other — is
   not available, and we do not use it.
2. Every pair contributes the same 180-cell family, so a corpus median no
   longer mixes families that differ in shape. Checked rather than trusted: on
   every one of the 19 pairs the design is 2 learners × 2 splits × 3 quality
   conditions × 3 rungs, with **every combination present exactly once**, and
   no pair differs in shape from any other.
3. Measured family-wise coverage, on the family matched to **this** design
   rather than the one it replaced: **91.6%** under the corpus's own tails, at
   a Monte Carlo standard error of 0.6%, and **84.3%** under the
   non-zero-truth regime this round adds, against a nominal 95%. That regime
   matters and is new: under a zero truth every rejection is an error, so
   coverage cannot distinguish a band that resolves *correctly* from one that
   never resolves at all.

   *A correction we make against ourselves, because it flatters us.* An
   earlier draft of this letter and of Section 10 quoted a median of 83.7%
   here. That figure pooled the decision-curve families with the surface ones
   — two sets whose required widenings we report separately, at 1.36–1.88 and
   2.20–2.61, precisely because they are not the same object — across draw
   counts from 33 to 1,000 and family sizes from 120 to 2,966, while every
   pair we report carries 180 cells at 400 draws. The number matched to what
   we actually run is 91.6%, and the table of "families matched to this
   corpus" did not contain that row until this revision. The correction raises
   our coverage, so we state it plainly: 91.6% against a nominal 95% is short
   by more than five Monte Carlo standard errors, the limitation is unchanged
   in kind, and the number that carries it is now the right one.

**On the labels: it does not, so they stay diagnostics.** We said we would not
describe a band as covering because we would like it to, and we have not.
Region labels and $\rho$ remain descriptive diagnostics, contribution 2 does
not claim inference, and the abstract's *"whose coverage we measure against a
known answer and find short of nominal"* stands as written.

**And the reason it does not is the second finding.** The draw count was named
as the binding constraint. It is not: coverage is 91.2% at 150 draws, 91.6% at
400 and 91.3% at 1,000 — it **plateaus**. This corpus now runs at 400
throughout, on the plateau rather than below it. The widening that would close
the gap is 1.36–1.88 on the surface families, *larger* than the 1.18–1.77 the
only calibration we have fitted would supply. **So we do not apply it.** A
widening smaller than the measurement asks for would spend resolution and
present the labels as corrected without earning the level, which is a worse
position than reporting them nominal and saying by how much they are
anti-conservative. Section 11 says so, and Supplement F derives the
calibration in full so that the measurement retiring it is legible beside it.
We do not claim to know *why* the shortfall exceeds it; that would need a
counterfactual we have not run.

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

**Conceded; it was arithmetic and it is now applied** (`s49_dcaband.py`, 0.07 s, no refits).

The report is right that this one had no excuse at all: Section 10.4 measures
that the decision-curve families need a multiplicative widening of 1.90 to
2.05, Section 8.3 printed counts from the uncorrected band, and Section 11
told the reader to distrust them. Widening an already-computed critical value
costs matrix arithmetic and no refits.

**Which factor, and why it is measured rather than chosen.** The candidates
are not the two you might expect. The ratio of two marginal quantiles is *not*
a widening — our own simulation file carries a comment recording that an
earlier version applied one and was wrong, because the critical value and the
statistic are estimated from the same draws and move together. The factor that
attains the level is the within-replicate quantile of their ratio. So the
choice is between simulation *regimes*, and this family is measured into one
rather than assigned to it: 2 of its 248 cells are degenerate against a corpus
maximum of 17.2%, and its excess kurtosis matches the heavy regime and not the
degenerate one. We apply the heavy regime's factor at its conservative end,
2.05, and print the degenerate regime's 2.09 beside every count.

**What it costs.** The thresholds the whole-curve band resolves fall from 18
of 31 to **8**, and the surviving 8 are **not contiguous** — a fact the
results file records so that no generator can accidentally describe them as a
range. Over the whole 248-cell family the beneficial count falls from 110 to
36, and the single cell that resolved as *harmful* no longer resolves, so the
correction removes a claim rather than adding one. The count is 8 at every
candidate factor from 1.80 to 2.05 and 7 only at the top, so the choice of
factor moves one point in thirty-one.

We state the consequence plainly: a decision curve read across its range while
priced pointwise has claimed something it did not pay for, and once it pays,
most of the range stops being sayable. That is the argument this paper makes
about other people's work, and it costs us more than it costs them.

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
not, and Section 8.3 now says which is which. The factor is settled: the
heavy-regime shortfall at its conservative end, measured on this family rather
than assigned to it, with the degenerate-regime alternative printed beside
every count.

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
single median. The values: the inference family is a median **16.7%** of a
pair's admissible cells and **12.5%** of the master surface file, which carries
the intercept-only rung that no admissible set contains. Those are two numbers
because they are two denominators, and the sentence quoting each now names
which.

The report is also right that this defect is the same species as the six in
§0. The generalisable repair is the sweep now in `round27_verify.py`: every
macro naming a per-pair or per-surface count or share is recomputed from the
axis-level declaration, so the next one of these fails the build rather than
reaching a referee.

---

## 3a. What we went looking for once you had named the class

Your three findings were instances of one thing: *a macro is right, a table is
right, and the pair contradicts when a reader holds them together*. Six of
that class had already been repaired in `a03b560`; yours was a seventh. That
is enough instances to stop treating them as a proofreading problem.

So we hunted the class deliberately, in the sections no referee has yet
complained about, and found **eighteen more — eight of them blocking**. All
are repaired and enumerated in `REFEREE-LOG.md` under R27.6. A sample, so the
severity is not taken on trust: the two cohorts' subset relation was stated
backwards, in a paragraph whose own next clause proves the direction; a
resolution rate was quoted as "197 of 5,808 cells" where 5,028 of those cells
carry no bootstrap draws and are therefore neither resolved nor unresolved,
understating the corpus's resolution sevenfold *in the sentence claiming the
data resolve little*; a table printed region labels that Definition 3
retracts — the same defect repaired in the master table a week earlier and
left standing in a second table; and the supplement asserted that one
conditionally harmful surface exists while the article's master table shows
none.

**One of the eighteen deserves its own paragraph, because it is worse than a
wrong number.** Section 3 tells the reader that multiplying Table 3's level
counts reproduces the cell counts of Section 6, and calls that "the first
check the verification harness runs". Three of Table 3's nine rows are not
factors of that product: the encoding is already fused into the learner row,
the decision time is not a factor of any surface, and the baseline appears
twice. A reader who follows our own instruction to audit our denominator gets
267,840 where the declaration says 1,080. The check the harness runs is the
right one; the table a reader was pointed at could not reproduce it. We have
made the table earn the claim rather than deleting the claim, because a reader
reproducing a denominator is the argument of this paper.

Two things are worth saying about the eighteen as a set. The pass also
verified about thirty identities **clean** — the whole denominator table cell
for cell, all nineteen rows of the master, triple and calibrated-band tables,
every corpus median of the decomposition, the decision-time ladder's
increments and intervals and ordinals. And the defects are concentrated in
*prose that describes tables*, not in the tables: the generators are sound and
the writing is where the risk lives. That is the strongest argument we have
for the length reduction below being a correctness measure rather than a
cosmetic one. Every restatement of a number in prose is another place for the
prose and the table to drift, and Section 11 alone restates 55 of the 73
macros it uses.

## 4. Reproducibility: a discrepancy we found ourselves and are disclosing

This is not in your report. We are raising it because it would have been in
the next one, and because a referee who ran our archive before we said this
would have been entitled to disbelieve everything else in it.

**The manuscript claimed one-command reproduction without qualification, and
that claim was false on any machine but ours.** No gate caught it: the
release check re-derives macros from committed result files and never re-runs
an analysis, so it could not see the thing it certified.

We diagnosed it by elimination rather than by argument, and **four candidate
causes are ruled out by measurement**: thread count (pinned to one against
four — bit-identical), library versions (the pinned set against a newer one —
bit-identical), source drift (the analysis module at the commit that produced
the surface against the current one — bit-identical), and run-to-run
nondeterminism (exactly deterministic). What remains is the processor
architecture. Thread pinning does not repair it, because the pins were
already there.

**The mechanism is amplification and we measured it.** A one-unit-in-the-
last-place nudge to the boosting encoding matrix — a relative 2.2e-16 — moves
a predicted probability by 0.37. The logistic learner is not chaotic at all:
its probabilities agree to 1.4e-15. But a rank-based metric is a step
function, and a high-cardinality register ties test rows to equal predictions
that a difference in the last bit unties.

**Two things we had written down about this were wrong, and both were wrong
in our favour.** Our own notes said the logistic learner reproduced to 5e-10;
it diverges by up to 0.094 in Nagelkerke. They said the discrepancy reached
0.14; it reaches 0.851. And the right characterisation is not a learner at
all — **the divergence tracks the register's cardinality**, and the
low-cardinality rungs of both families reproduce to 2.3e-12.

The disposition is a measured tolerance, not a promise. `REPRODUCE.md` now
carries the eliminations, the mechanism and six documented tolerances; the
code-availability statement claims bit-exactness inside the container and
states what holds outside it, with the distinction that matters — **checking
a digit requires the container, checking a conclusion does not**. Two new
scripts execute the claim instead of asserting it: a gate that re-runs part of
the surface against those tolerances, and its own corruption suite, which
caught a labelling bug in the gate before we trusted the gate.

**A second undeclared tie order, found on the way, and not repaired.** The
register-quality mechanisms cut a cumulative-count curve *inside* a group of
tied identities, so which identities a degradation removes rests on a sort
nothing pins. This is the second instance of the defect Section 7.1 already
reports about the split sort — which is why the reporting standard's
tie-break item is now stated over *every* sort a procedure cuts on, rather
than over the one place we happened to find it first. We have not repaired it:
doing so moves every number on the quality axis, and it belongs with the run
that regenerates them. It is recorded where a reader will meet it.

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

**One request we are declining, with the reason.** An earlier report asked
that the single-author paper drop the editorial "we" for first-person
singular or an impersonal voice. We counted before deciding: 41 instances in
the whole document, 19 in the main body — so this is not a cost objection.
It is that the plural is not decorating narrative here, it is carrying
accountability, and it falls almost entirely on the sentences that own a
withdrawal or a refusal: *we therefore withdraw the claim*, *we report both
rather than the one that reads better*, *we did not narrow the rule
retrospectively*, *we do not conclude that a surface report is a better
decision rule than a number*. An impersonal rewrite takes the agent out of a
withdrawal, which is the last place a paper should be agentless. We would
rather answer the request with a reason than with a passive voice.

**Length, and a trade we want the editor to judge rather than discover.**
This round *added* four pages before it cut any, and we would make the same
choice again. Nearly every one of the eighteen defects above was of one shape
— the sentence named one set and the number was computed on another — and the
repair for that shape is to name the set. "197 of 5,808 AUC cells" became
"197 of the 780 AUC cells that carry a band". The design-space table gained a
column stating which of its rows are factors of the cell count. The
decision-curve figure's caption now says which band it draws. Precision is not
free in pages, and a shorter version of this paper would have been a less
precise one.

**Then we cut, and we report what the cut actually yielded.** The reporting
standard and software section moved to the supplement in full, keeping the
prescription itself in the body as a paragraph, because the standard is the
contribution and the recipe, the package and the worked example are the
apparatus. The case study's two side experiments, four detail blocks in
Section 6, the design rule's full statement and two constructions the
supplement already gives verbatim moved with it. Ten passages that restated a
number where it was not computed were compressed to a pointer. **The article
went from 66 pages to 62 and the body from 22,100 words to 19,900.**

**That is four pages, and the target asks for twenty. We are not going to
close that gap and we will say exactly why rather than let you discover it.**
We measured the whole body, section by section, against the constraint that a
cut which removes a number is a saving and a cut which removes a concession is
a regression. Of the body's prose, roughly a quarter is protected under that
rule: the coverage measurement at full length, every withdrawn claim, the
"descriptive diagnostic and not a guarantee" sentence, the prefix disclaimer,
the per-pair role declarations, the decision-time ladder and the configuration
management programme reading. **All eleven floats are protected too, and by
your own earlier report** — the four-way partition table, the resolution-triple
table, the MPID table and the overview figure were each moved into the body or
written new to answer comment C3, which asked for six more floats in, not
fewer. Eleven floats are 6.6 of the body's 53 pages and none of them is
available. Reaching 38 body pages from here means removing about 43 per cent
of everything not explicitly protected, from sections that have had material
moved to the supplement in four consecutive rounds. At that density it stops
being a move-and-compress pass and becomes the kind of rewrite that this
project's own log records as the reliable way to introduce a defect — and this
round found eighteen of them created by exactly that.

**One thing we kept that we could have cut.** Section 6.5 runs
specification-curve analysis unchanged against our own region labels and
reports where the two part company. It is 0.85 pages and the single largest
saving still on the table. It is also the paper's only head-to-head with the
closest existing practice, and a reader assessing what is new here will look
precisely there. We kept it, and we would rather be told to cut it than cut it
and be asked where the comparison went.

**So: 62 pages, and the trade is yours to make.** We would rather submit 62
pages in which every number states the set it was computed over than 46 in
which some of them do not, and we have put the arithmetic above so that the
judgement is yours to overrule rather than ours to hide. If the page count is
binding, tell us so and Section 6.5 and the simulation's first three
subsections are the next 2.4 pages we would take.⟩

**The archive DOI, and one more the round created.** Both are the author's to
mint, and we have taken each as far as it goes without the depositing account.

**The container is now a fixed object.** This round measured that the results
are not bit-reproducible across processor architectures, and the
code-availability statement claims bit-exactness *inside the shipped
container* — which a container pinned by a mutable tag cannot support, because
the same `Dockerfile` would build a different image next year. The base is now
pinned **by digest**, the multi-architecture manifest list, so a build still
selects the host platform while the content is fixed. We verified the digest
rather than trusting the registry's reply: fetching the manifest *by* that
digest returns bytes that hash to exactly it. The manuscript's sentence reads
the digest out of the `Dockerfile` rather than carrying a typed copy, and a
verifier condition fails the build if the two ever disagree, so an edit to the
container cannot silently falsify the paper. What still awaits the deposit is
the digest of the **built** image; the statement says the archive records it at
release, which is true.

**The DOI is still ours to mint, and the loop around it is closed.** Reference
[11] read *"the archived release cited in the data-availability statement (DOI
reserved, inserted at proof)"* — and that statement carried the same text, so
an editorial assistant following the reference arrived back where they
started. The entry now carries its own resolvable URL to the repository the
release is cut from, and the note states the DOI's status in one clause.
Adding a `doi` key to `.zenodo.json` replaces the placeholder in the
statement, the reference and the archive metadata at once. We would rather you
saw this listed than discovered it.

---

## 6. What round twenty-seven does not do

Stated here so that nothing above implies otherwise.

- The crossed family × encoding decomposition now runs on the eight ITSM
  pairs rather than the case study's log alone, so that limitation is
  narrowed — but the pairs outside that family are still confounded, and we
  do not claim otherwise.

  We report the outcome here because it is not the one we wanted. **The
  finding partially replicates**: the encoding is the larger first-order axis
  on six of the eight pairs, and on the other two the family is, decisively —
  on the more extreme, the encoding carries four hundredths of what the family
  does. So the case study's ordering is the common case and not a corpus fact,
  and Section 6.2 says so.

  We think this is a better result than a clean replication would have been.
  The crossing exists to separate two axes that a fused index confounds, and
  what it finds on new pairs is this paper's own central claim arriving where
  it was not sent: which axis leads is a property of the pair. A finding that
  survives its generalisation test by turning into the thesis is worth more
  than one that survives by repeating.
- The corpus is still a family of related prediction problems rather than
  replications of one finding, and every corpus statistic is still about
  sensitivity rather than about a universal register value.
- The stationarity and mixing the moving-block construction needs are
  diagnosed this round but not tested in the sense a formal test would mean.
- The case study is still one bank's estate on one public log, with the
  admissibility question at its centre settled by probability rather than by
  a timestamped field-value history.

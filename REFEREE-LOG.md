# Referee log

Every objection this project has received, with its disposition. An objection
is dispositioned in exactly one of four ways:

| code | meaning |
|---|---|
| **MEASURED** | a new measurement was run and the paper reports it |
| **CONCEDED** | the paper now states the limitation in the referee's terms |
| **NEGATIVE** | we looked, found nothing, and the search is recorded |
| **DISMISSED** | the objection does not hold, with the reason |

Nothing here is left as "noted".

---

# Round nineteen — the *Information Systems* referee

An external referee for *Information Systems* recommended **rejecting the
round-eighteen manuscript as submitted**, on the ground that several
weaknesses affected the central evidence rather than the presentation. The
full report is the input to this round. Ten major comments; every one is
conceded, and eight of them changed the study rather than the prose.
`submission/response_to_referee.md` is the point-by-point reply.

### IS1. The main conclusion contradicts the paper's own later analysis. **CONCEDED — and structurally prevented**

The abstract said the baseline choice moves the reduction by more than the
reduction itself; §10 of the same manuscript said the comparison was inflated
by an intercept-only baseline "no analyst would build"; the abstract was never
corrected. Six further internal inconsistencies were listed and all six hold.

**Disposition.** The intercept-only rung is excluded from every admissible set
by definition. Every number in the manuscript is now a macro generated from a
result file, and `scripts/texlint.py` fails the build if a numeric literal
appears anywhere in the prose. The abstract and a table cannot disagree
because there is one of each number. Corrections C14 and C17–C19.

### IS2. The contribution is not sufficiently novel. **CONCEDED — four new objects**

The previous version's contribution reduced to "these familiar dependencies
are large here, so report a grid".

**Disposition.** The specification surface, an exact functional-ANOVA
decomposition of its variance, resolution regions with a robustness index, and
specification regret — the last being the benchmark against one-number
reporting that the referee asked for and the previous version did not attempt.
`fieldvalue` 0.2 implements all four.

### IS3. The estimand is incomplete and "value" is overstated. **CONCEDED**

**Disposition.** Renamed *incremental predictive performance* throughout. The
estimand carries learner, encoding, target, split, availability, quality
mechanism, baseline, metric and operating point. Register population is no
longer hidden inside $f$: it is one level of the quality axis.

### IS4. The literature audit cannot support a field-wide claim. **CONCEDED — and the claim is withdrawn**

Eighteen specific defects, all of which hold.

**Disposition.** Demoted to a machine-assisted prevalence pilot. A random
sample of the papers the mechanical screen *rejected* is now adjudicated, so
its misses are counted; its measured sensitivity is under one half. The
round-eighteen claim that not one of twenty papers reports the increment
across operating points is **withdrawn** (C15): it was a property of the
coder. Applicability-specific denominators, missing-data bounds, a PRISMA-style
flow and a sample-size calculation are added, and **no claim in the paper
depends on the pilot**.

### IS5. The ratio $R$ is unstable and is read as a proportion. **CONCEDED**

**Disposition.** Absolute increments and the absolute absorption $D$ are
primary. $R$ is secondary, reported only where its denominator is resolvably
positive under the simultaneous band, with a Fieller set whose *kind* is
printed beside it.

### IS6. The formal propositions are not established as written. **CONCEDED on all three**

**Disposition.** Proposition 1 restated as metric non-identifiability, with
the average-precision convention and the tie rule stated and the construction
done in integers. Proposition 2's quantifiers pinned down, its necessity
direction stated as existential, and a cancelling configuration exhibited
(C13). Proposition 3 relabelled a computational result, with its tolerance
sweep printed and a defect in the search itself recorded (C16).

### IS7. The knowledge reference may be post-decision information. **CONCEDED — and it improved the paper**

Only five interactions were formally closed before their incident was opened;
agreement with a closed record cannot establish creation-time availability;
and a base AUC near 0.8 from one field is itself a reason for suspicion.

**Disposition.** Two decision times, two surfaces, and a leakage tipping-point
curve so a reader can place their own belief about how many references are
post-hoc. Neither surface is used to retire a claim the other supports. What
the interaction file establishes and what it does not is tabulated item by
item.

### IS8. Statistical inference is inadequate. **CONCEDED**

**Disposition.** A nested moving-block bootstrap that refits the whole
pipeline inside every draw; rolling-origin validation as an axis; simultaneous
max-$t$ bands; five pre-specified confirmatory contrasts with Holm and
everything else labelled exploratory; and a rebuilt simulation over six
worlds — misspecified, drifting, sparse, imbalanced, noisy — with an exactly
enumerated truth, separating the estimator's own limit from the oracle
quantity. The 85% coverage the previous version dismissed as boundary
behaviour is now decomposed rather than explained away.

### IS9. External validation is selected and heterogeneous. **CONCEDED**

The previous version ran the full surface only on the logs whose reduction was
resolvable, which conditions the analysis on the outcome.

**Disposition.** Every log--target pair the pre-registered rules admit is
analysed and reported, and the pair list is read from the registered ladder's
own admission output rather than chosen. The multi-log analysis is reframed as
a benchmark of specification sensitivity across heterogeneous problems, and
results are not averaged across pairs.

### IS10. The population axis does not model register quality. **CONCEDED**

**Disposition.** Six mechanisms besides the clean field — coverage loss three
ways, identity error, reconciliation failure, staleness — each parameterised
from the training half alone, stochastic ones averaged over seeds, and the
train-only property verified by execution rather than asserted.

### What we found in our own work while answering them

Four defects were found in this round's own apparatus, by this round's own
apparatus, after every one of the referee's ten comments had been answered.
They are recorded here because a referee is entitled to know what the process
catches when nobody is looking at it.

**The simulation's truth was wrong in one world.** `s10` reported that every
interval construction fails on the noisy world — coverage 0.035, an apparent
bias of −0.035 against an interval half-width of 0.037. The comfortable
reading was that the estimator is biased there. `s18` tested the two
finite-sample explanations that reading implies: growing *n* from 4,000 to
64,000 (the sparse world's gap closes from +0.0118 to +0.0006, the noisy
world's from +0.0361 to +0.0329) and weakening the L2 penalty by five decades
(the noisy world's gap moves by 0.0000). Both refuted. What was wrong was the
target: the simulation enumerated the generator's *true* register values while
the estimator only ever sees a value replaced by a uniform draw 20% of the
time. With the noise marginalised exactly, V_limit moves from +0.1135 to
+0.0804, the estimator's mean was +0.0781 throughout, and coverage is 0.920.
Appendix G. This is the round's most serious finding and no checker in the
repository could have caught it.

**The pilot's frame was 600 and the manuscript said 54,910.** `n_frame_total`
summed a stratum-size column over the *rows* of the sample instead of over its
distinct strata. Correcting it showed that every design weight is 1 and that
the enumeration had stopped short of its declared 2,400-record budget, so the
pilot is a census of what one index returned rather than a probability sample
of a literature. §9.4 and Appendix F now say so, with a fourth stated limit.
Correction C21, Class H.

**`--strict` certified a manuscript built from a superseded run.** A
two-replicate smoke test of `s18`, run under the wrong seed and against the
estimand that was corrected an hour later, left result files behind; every
macro reading them resolved cleanly, to a wrong number. `results/provenance
.json` now records the SHA-256 of each analysis script at the moment its
outputs were accepted, with a note saying why, and `--strict` refuses a
manuscript whose numbers come from a script that has changed since.

**One of the ten corruptions was passing because nothing regenerated.** The
suite corrupted a result file and then asked the verifier about a
`numbers.tex` built from the clean results, so a quantity the verifier
re-derives from a different file than the generator reads was untouched. The
suite now regenerates from the corrupted copy first: 10 caught, 0 missed.

Two prose claims were also counted for the first time and were wrong — the
worked example runs in 121 statements and not "forty lines", and the corpus is
13 logs and not "the two ITSM ones and eighteen others". `texlint` forbids
numeric *literals* and said nothing about spelled-out ones; it now checks that
a spelled-out count matches the list it introduces.

### What the referee asked for and we could not do

- **An organisational partner** with timestamped field histories, historical
  register population and accuracy, and operational review costs. We do not
  have one. The case study is framed as a benchmark case in consequence.
- **A systematic review with two independent human raters and 150–200
  manually confirmed in-scope papers.** One author cannot supply a second
  independent human rater. We took the referee's stated alternative and spent
  the effort on measuring the coder's error rate instead, which is what makes
  the pilot's numbers interpretable at all.

---

# Referee log, rounds fourteen to eighteen

Four independent passes, each with a different brief, each instructed to
reject. Every objection is recorded with its disposition, **including the ones
dismissed and why**. An objection is dispositioned in exactly one of four
ways:

| code | meaning |
|---|---|
| **MEASURED** | a new measurement was run and the paper reports it |
| **CONCEDED** | the paper now states the limitation in the referee's terms |
| **NEGATIVE** | we looked, found nothing, and the search is recorded |
| **DISMISSED** | the objection does not hold, with the reason |

Objections that produced a paper edit name the section. Nothing here is left
as "noted".

---

## Pass 1 — the methodologist

*Brief: is the estimand well defined? Are the nulls matched? Does any control
destroy more than it means to?*

### M1. The reduction is a ratio of two differences on a scale that has no ratio structure. **CONCEDED — and promoted**

$R = 1 - V(f \mid B_1)/V(f \mid B_0)$ divides two AUC increments. An AUC
increment has no natural zero of the kind a ratio needs, so "$43.7\%$ of the
value is absorbed" under AUC and "$60.3\%$" under average precision are not
the same quantity measured twice. (The first draft of that sentence in the
paper attributed $60.3\%$ to Brier skill, which is $58.4\%$; the checker
caught it, because the value and the instrument named beside it disagreed.) The referee is right, and the objection is the paper's own
thesis stated formally: $R$ is metric-relative *by construction*, not merely
empirically.

**Disposition.** §3 now says so explicitly rather than leaving it to be
inferred from §7's table. The paper does not claim $R$ is comparable across
$m$; it claims the opposite, and reports the spread as the finding.

### M2. The paired bootstrap resamples test rows and holds the fitted models fixed. **CONCEDED**

It therefore quantifies test-set sampling error and not model-fitting
variability, so every interval in the paper is narrower than a full
resampling would give.

**Disposition.** Stated in §5. The substitute is the design-space sweep the
paper already carries — split point, target threshold, cleaning cutoff and
three estimator families — which moves the AUC reduction over $36.1\%$ to
$48.3\%$, a range far wider than any bootstrap interval in the paper. A
reader should treat that range, not the bootstrap interval, as the honest
width.

### M3. `km_prov` conditions on a data-derived subset, so section 13 may be selecting on the outcome. **DISMISSED, with the reason**

The objection would hold if the analysis were run on the incidents whose
interaction was worked to completion first. It is not. `km_prov` is a
**feature column** on the unchanged cohort: incidents that do not qualify
carry an explicit missing token and stay in the model, the split and the test
set. `r35_interaction_file.py` constructs it that way and the cohort size is
identical on every rung of that ladder.

### M4. The matched-mass null matches cell sizes but not temporal coherence. **MEASURED**

A random partition of incidents has no temporal structure; a real field does,
because a knowledge article is used in bursts. So the null shows the collapse
is not a dimensionality artifact, but it does not show it is not "any
temporally coherent grouping of this size".

**Disposition.** A third null was added, and the obvious construction was
rejected first. Building cells from contiguous blocks of the time-ordered
cohort gives *perfect* temporal coherence and is useless here: the split is
temporal, so every test cell would be unseen in training, the model could not
use any of them, and the null would collapse to the baseline for a reason
unrelated to the question. A null that cannot fail is this project's
most-repeated defect.

What `r35b_temporal_null.py` runs instead is a permutation that preserves each
cell's **temporal profile exactly**: the time-ordered cohort is cut into twenty
equal-count strata, and labels are reassigned at random *within* each stratum,
so every synthetic cell has the same size and the same distribution through
time as the real one it copies. Both properties are asserted rather than
assumed. Result: base AUC at most $0.6483$ against the real field's $0.8041$ —
a gap of $0.1558$ — and the item left worth $+0.092$ to $+0.101$ against
$+0.001$. Temporal coherence reproduces neither number. §13 reports all three
nulls.

### M5. `NO_HEADROOM` reads the target's prevalence on the full log, including the test half. **MEASURED**

That is a use of test-set information to decide inclusion. It selects on class
balance rather than on effect, so it is mild, but it is not nothing.

**Disposition.** Re-run with the rule applied to the **training half only**.
`r33c_headroom.py` fits no model — the prevalence and the split point are all
it needs — and **0 of 26 admission decisions change**. The peek exists in the
registered text and changes nothing in the result. §11 says so in one
sentence.

### M6. Flooring a bootstrap percentile is not conservative in any distributional sense. **DISMISSED, with the reason**

`ck_bound`'s floor/ceil discipline is about printing: an interval a paper
states must contain the interval it computed, so a lower endpoint may not be
rounded up. It makes no claim about coverage. The check caught six real
defects in this round's new tables on its first run, which is the argument for
keeping it.

---

## Pass 2 — the process-mining referee

*Brief: is the protocol faithful to how these logs are generated? Are the
targets defensible? Is the inter-case perspective handled?*

### P1. "More than one distinct resource touched the case" is not a target anyone predicts. **CONCEDED, and the ordering changed**

Predictive process monitoring predicts next activity, remaining time, or a
case outcome. The handover target is a generalisation of *this paper's* task,
not a standard one; the duration target is standard.

**Disposition.** §11 now leads with the duration target, says the handover
target is this paper's own construction generalised, and reports both for
every log as the protocol requires. The corpus's three resolvable logs are
carried by the duration target.

### P2. Using only the first event discards the prefix, which is the point of the field. **DISMISSED, with the reason**

Deliberate and already stated: the decision this paper is about is taken at
intake, before any prefix exists, so a prefix-length-indexed evaluation would
answer a different question. §4 says the paper predicts at $t=0$ with no
prefix.

### P3. `C=1.0` was never tuned, and the paper says elsewhere that penalty tuning changes a sign. **CONCEDED**

**Disposition.** §5 points at the penalty sweep the paper already carries, and
repeats that the one quantity whose sign moves under tuning --- the knowledge
reference's $-0.003$ --- is reported as unresolvable on that ground and not
used.

### P4. The permitting logs are the natural replication set and none of them shows the effect. Say what that means. **MEASURED — and it produced the paper's condition**

BPI Challenge 2015's five municipalities are the closest thing the public
corpus has to a controlled replication: one process, five organisations. Four
are admitted and none shows a resolvable reduction. The referee is right that
a paper should explain that rather than list it.

**Disposition.** It has the same cause as the exclusions. Those logs' opening
resource stamp has cardinality $7$ to $18$; BPI Challenge 2012 and all five
BPI Challenge 2020 sub-logs have cardinality **one**, which is why the
protocol excludes them as `NO_G`. A nearly constant opening field cannot
absorb anything, and §13's intake-mix sweep measures exactly that on the
primary log: as the largest opening group's share goes from $0\%$ to $95\%$
the reduction falls from $95.3\%$ to $6.3\%$. **The sweep on one log predicts
the corpus.** §11 now makes that link, which is the strongest thing the corpus
produced.

### P5. The corpus protocol has no inter-case features although the primary log's analysis does. **CONCEDED**

**Disposition.** Stated in §11 as a scope limit. `r22` shows four free
creation-time congestion features move the primary log's reduction from
$43.7\%$ to $45.7\%$, so the omission is unlikely to be large, and that is
one log's evidence rather than the corpus's.

---

## Pass 3 — the practitioner

*Brief: would any of this change a funding decision? Is the population curve
credible? Is the era argument honest?*

### R1. You never say what a buyer should do. **CONCEDED**

The paper reports that the item is worth $+0.001$ once every free field is
admitted and then declines to draw the conclusion.

**Disposition.** §15 now says it in one sentence, scoped exactly: on this
task, this estate and this target, a register that costs money adds nothing
measurable over fields the organisation already records, and a business case
built on $+0.183$ is pricing a register plus two free fields. It does not say
that about registers in general, and §11 is why it cannot.

### R2. Real registers are wrong, not empty. **CONCEDED**

A confidently wrong configuration item is worse than a blank one, and the
population curve models blanks.

**Disposition.** §13 states that the curve measures population and not
accuracy, and that we have no way to detect a wrong value in a public export.

### R3. Subsampling one organisation's opening groups does not make a second organisation. **CONCEDED**

§13's intake-mix sweep varies the mix within one estate, one tool and one
period. It is a sensitivity, not a replication.

**Disposition.** §13 says so in those words. What supports the reading is that
the sweep's prediction --- a nearly constant opening field absorbs almost
nothing --- is what the corpus independently shows on the logs where the
opening field is nearly constant (P4).

### R4. Nobody runs a desk at $\theta = 0.525$. **PARTLY DISMISSED, and the honest reading is worse for us**

The referee has the direction backwards, and correcting it makes the finding
more relevant rather than less. A high threshold means acting on *fewer*
arrivals, which is the capacity-constrained desk. At the thresholds where the
item is resolvably harmful the group-aware item model acts on $17\%$ to
$36\%$ of arrivals, which is squarely the operating region of a desk that
reviews a minority of its intake.

**Disposition.** §8.2 now states the acted-on share alongside the threshold,
so a reader can locate their own desk on the curve, and says plainly that the
harmful band is where a capacity-constrained desk operates.

### R5. A "free" field is not free; the desk structure that makes it informative costs money. **CONCEDED, already in the paper**

**Disposition.** Unchanged. §7 already engages this: the opening group may be
informative only because a human at the desk already knew what the ticket was
about, and that human is not free. What the paper claims is narrower --- the
field costs no *incremental* data-programme spend, because it is already
recorded.

---

## Pass 4 — the hostile generalist

*Brief: where does the paper overclaim by one word? Which sentence would you
quote in a rejection?*

### H1. Why exactly four choices? The estimator is a fifth. **CONCEDED**

Nothing makes four the right number. The estimator family is a sixth axis and
the cohort a seventh.

**Disposition.** §3 now says the four are the choices that are usually left
*implicit*, names the estimator as one the literature already treats as a
choice, and points at the three estimator families this paper varies. The
title's "four" is a claim about what is usually unstated, not about what
exists, and §3 says that.

### H2. "Falsified" is too strong for a corpus with no power. **CONCEDED — this is the sharpest objection in the log**

On $10$ of $19$ log-target pairs the entity is not resolvably worth anything
over the intake block, so $R$ has no denominator and the test could not have
detected the effect if it were there. Reporting that as a falsification
conflates *absent* with *untestable*.

**Disposition.** §11 now separates the two. The claim registered in
`PROTOCOL.md` §8 is falsified **by its own registered criterion**, which is
reported because pre-registration means reporting the verdict you registered.
Beside it the paper states what the corpus can and cannot support: on the nine
pairs where a reduction exists to measure, four are resolvably positive; on
the other ten there was nothing to measure. A narrower claim --- that where a
high-cost entity predicts at all, a free opening stamp absorbs a large share
of it --- is **not** refuted by this corpus and is not asserted by it either.

### H3. "The headline does not survive our own admissibility criterion" — so why is the paper still built on $+0.103$? **CONCEDED**

**Disposition.** The abstract, §3 and §15 now present $+0.183$, $+0.103$ and
$+0.001$ as three points on one surface, never as a result and a caveat. Where
the paper uses $+0.103$ for a downstream measurement --- the population curve,
the intake-mix sweep --- it says which baseline that number is conditioned on
in the same sentence.

### H4. Eleven self-reported errors read as eleven reasons to distrust the paper. **EXPLICIT DECISION, recorded rather than fixed**

Some referees will score the paper down for the Corrections section. That is
priced in: `PLAN-STRONG-ACCEPT.md` §11 records the decision to keep it, and
the reason is that a paper whose thesis is that unexamined choices set the
answer cannot suppress its own. Two of the eleven are a defect class the
verification apparatus could not see, and that is a contribution rather than
an embarrassment.

### H5. Forty-five pages. **ACCEPTED AS A RISK**

*Information Systems* enforces no hard limit. Every section added this round
carries a measurement; nothing was added as discussion. If an editor asks for
a cut, §9's mechanism material and §13's per-axis detail are the two places
that can move to supplementary material without removing a claim.

### H6. The paper cites its own repository as evidence about itself. **DISMISSED, with the reason**

The claim the repository supports is checkable: `PROTOCOL.md` was committed
before any corpus result file existed, and `git log --stat` shows that commit
adding one file. A reader who does not believe it can check it in one command.
That is a stronger form of evidence than the assertion it replaces, not a
weaker one.

---

## Summary

| pass | objections | measured | conceded | negative | dismissed |
|---|---|---|---|---|---|
| methodologist | 6 | 2 | 2 | 0 | 2 |
| process-mining | 5 | 1 | 3 | 0 | 1 |
| practitioner | 5 | 0 | 4 | 0 | 1 |
| hostile generalist | 6 | 0 | 4 | 0 | 2 |
| **total** | **22** | **3** | **13** | **0** | **6** |

**And then the corruption suite found three more, all of them prose.** The
enlarged suite's first run landed "It is falsified" softened to "It is largely
supported", the abstract's "does not survive" reversed, and the two ends of a
three-way population comparison swapped. Each is now guarded. Repairing them
exposed a fourth: retiring a check for a rewritten sentence had silently
unguarded the admission that item identity can make a desk *worse* off, and a
corruption that had been caught for a round started passing. **A retirement can
unguard prose it was not retired for, and only the suite can see that.**

Repairing *those* exposed a fifth, in the checker rather than the paper: the
guard-or-declare lint consumes `guarded_phrases` and sat above the pins added
in this pass, so it reported as unguarded two sentences that were pinned. That
is the third instance in two rounds of one bug — a consumer placed above its
producers — and it is fixed the same way the census was, by moving it into a
function called from one late block that `_lint_check_order()` polices.

**And running the suite exposed a sixth and a seventh.** The seventh is the
worst thing this round did. A check added to compare the corruption suite's
size against the number the paper prints read it with `import
attack_verifier` — which, `attack_verifier.py` being a script, *ran* the
suite. Every invocation of the checker became a 199-corruption run in which
every corruption reported *caught*, because the nested checker hit the
lock-file guard and refused to start. **A clean 199/199 produced by an
apparatus that had checked nothing.** The size is parsed now rather than
imported, and `verify_paper.py` additionally asserts that the manuscript's
SHA-256 is unchanged from before it read anything;
`scripts/test_checker_purity.py` proves that guard fires. The general lesson
is that a harness which can modify its subject can report success by
construction.

**An eighth surfaced only because the one-command reproduction was run end to
end, apparently for the first time.** `r6_final.py` has not parsed since round
four: an f-string expression split across four adjacent string literals. Every
round since has read `results/r6_*.csv` and none could have regenerated them.
Re-running the repaired script produced byte-identical files, so the numbers
were right and the reproducibility claim was not. `HANDOFF.md` §20.11 has the
account; `reproduce_all.py` now parses every script in preflight.

The sixth is a process defect rather than a code one. A commit issued while the suite was rewriting the manuscript
captured a *corrupted* manuscript. The suite's own docstring has warned about
exactly that since round sixteen; a warning addressed to a reader is not a
control. `paper/.tex.bak` is now gitignored, and the verifier, the build and
the suite itself all refuse to start while it exists. `HANDOFF.md` §20.9 has
the full account.

Three objections produced new measurements (M4, M5, P4). Thirteen produced a
sentence the paper did not previously contain. Six were dismissed and the
reason is recorded above in each case.

**The rejection letter we could still write.** Following `PLAN-STRONG-ACCEPT.md`
§10's honest test, the strongest rejection remaining is: *the paper's general
claim is a reporting standard demonstrated on a single organisation's log; its
attempt to generalise returned a negative; and its most striking result --- that
the register adds nothing once two free fields are admitted --- rests on a
field-admission judgement the authors themselves say is not proved.* That
letter is writable, and every clause of it is a sentence the paper already
contains. What we do not think is writable is a rejection that names a claim
the paper makes and the data does not support.

---
---

# Referee log, round eighteen

**Six** independent passes this round, not four: the four briefs of
`PLAN-STRONG-ACCEPT.md` §8 plus the two `PLAN-REVIEWER-PROOF.md` §10 adds —
the literature-audit referee, and the editor. Same four dispositions, same
rule: nothing is left as "noted".

The measurements every objection below demanded are in
`scripts/r49_referee_round18.py`, and each prints its result whatever the
result is.

**The headline of this round's passes: the strongest objection landed, and it
weakened the paper's central claim.** M2 is worth reading before anything
else.

---

## Pass 1 — the methodologist

### M1. The audit's `Range_reported` counts two metrics as a range. **CONCEDED, and the rule is now stated before the number**

Reporting the with-and-without difference under AUC and F1 is not reporting a
surface, and crediting it inflates how compliant the field looks.

**Disposition.** §4.4 now states the rule *before* the proportions, says the
generosity is deliberate, and says why: a stricter reading would score the
field against a standard nobody has adopted. It also notes that on the two
axes where the count is zero no softer reading was available to give — the
generosity cannot have manufactured those zeros.

### M2. The three-log baseline spread is inflated by a rung no analyst would build. **MEASURED — and the paper's central claim is weakened**

The ladder's bottom rung is the intercept-only model. V(f | ∅) is large for
reasons that have nothing to do with this paper, so every ordered pair that
uses it exaggerates the baseline axis.

**Measured** (`r49_baseline_spread.csv`): dropping every pair that uses the
empty rung leaves three real baselines and three pairs, and the spread falls.

| log | all six pairs | real baselines only | reference *R* |
|---|---|---|---|
| BPIC 2014 | 0.565 | **0.346** | 0.350 |
| BPIC 2013 incidents | 0.467 | **0.347** | 0.378 |
| BPIC 2019 | 0.654 | **0.382** | 0.471 |

**Disposition.** The sentence "on every one of the three logs the baseline
choice alone moves *R* by more than *R* itself" **was true only of the
unrestricted ladder and is gone.** §10 now states both versions, says the
restricted one is the honest one, and scopes the "exceeds the effect" claim to
BPI Challenge 2014, where 0.346 against 0.350 is within a hundredth. On the
other two the axis moves the answer by *less* than the effect — still between
six and nine tenths of it, on three organisations, which is what the corpus
buys and is a smaller claim than the one we first wrote.

This is the objection of the round. It did not ship; it was found here.

### M3. The simulation validates the estimator on a correctly specified model. **CONCEDED — it was already**

§11's last paragraph says so in those words and calls the reported bias a
lower bound on the bias against a misspecified truth.

### M4. Proposition 3's constructibility thresholds are arbitrary. **MEASURED**

**Measured** (`r49_prop3_tol.csv`): across a grid of 16 tolerance pairs the
number of constructible ordered axis pairs runs from **8 to 12**. The paper
reports the cell at (agree within 5% of the axis's range, differ by 25%).

**Disposition.** Appendix A now prints the range and names the cell it
reports, so a reader can see how much of "ten of twelve" is the tolerance.

---

## Pass 2 — the process-mining referee

### P1. "`NO_HEADROOM` at prevalence 1.0000" is a code, not an explanation. **MEASURED**

**Measured** (`r49_holdout_roles.csv`): on BPI Challenge 2018 the opening
field is `org:resource`, cardinality 7, with a mean of **10.14 distinct values
per case** — and **99.9% of cases open with the literal value `0;n/a`**.

**Disposition.** §12.5 now says that. The exclusion is this paper's own
mechanism in a new form: the opening field carries essentially nothing at
intake, exactly as in BPI Challenge 2012 and every BPI Challenge 2020 sub-log,
except that here it passes the cardinality rule and fails the target instead.

### P2. The registered rules picked a classification as the "high-cost entity" on the held-out log. **CONCEDED**

**Measured**: BPI Challenge 2011's *f* is `case:Diagnosis`, 102 distinct
values, reuse 11.2. A diagnosis is not a maintained register that costs money
to keep.

**Disposition.** §12.5 says so, and says what follows: the prospective test is
a test of the registered *rules* on a log they had never seen — which is what
was registered — and not a test of this paper's question on a hospital.

### P3. "Three organisations, two domains" is thin for a generality claim. **CONCEDED**

Two of the three are ITSM. §10 says three organisations, three information
systems and two domains, and claims nothing about domains beyond that; §12
reports the registered generality claim as falsified.

### P4. The generic handover target is not the paper's published target. **DISMISSED — it is already reported, and prominently**

§15 gives the agreement: prevalence 0.927 against 0.411, agreeing on 46.0% of
incidents, and says the corpus measures a generic workflow outcome and not
this paper's task on twelve further organisations.

---

## Pass 3 — the practitioner

### Pr1. "No paper reports a range over operating points" is unsurprising in a field that reports rank metrics. **CONCEDED — and it is the point**

**Disposition.** The finding is not that the field is careless but that it
varies the two choices that are cheap to vary and not the two that decide the
answer. §4.4 says exactly that, and its new paragraph makes the generosity of
the counting rule explicit so the zero cannot be read as an artifact of a
strict one.

### Pr2. A business case needs a number, and the tool refuses to give one. **CONCEDED — and the paper now says what the number is**

**Disposition.** §13.1 adds the sentence a practitioner should write: the
value at one named cell, with its four coordinates, beside the range the other
cells occupy. `s.report()` prints it. Refusing a *bare* number is not refusing
a number.

### Pr3. The population curve is measured on one estate and generalised. **MEASURED, and it does not generalise**

**Disposition.** §10 reports that the population axis moves *R* by 0.085 on
one log and 1.293 on another — a fifteen-fold difference across three logs —
and says the honest reading is that how much register completeness matters is
a property of the estate, not of the method.

---

## Pass 4 — the hostile generalist

### H1. "Not one paper reports..." reads as a claim about the field; n = 20. **DISMISSED — the sentence already carries its n**

Both the abstract and §4.4 name the twenty, and §4.4 prints the Wilson upper
bound of 16.2%. A reader cannot take the sentence for a population claim
without ignoring the number in it.

### H2. The audit's effective n is 20, after 600 were enumerated. **CONCEDED**

That is what the funnel says, and the funnel is printed rather than
summarised: 600 sampled, 369 full texts, 54 mechanically included, 30 read, 20
confirmed.

### H3. "20 of 20 quantities agree to 2.2 × 10⁻¹⁶" oversells. **CONCEDED — the bound is in the same paragraph**

§13.1 states what is *not* independent — scikit-learn's estimator and the
shared cohort loader — and says an error in either would agree with itself.

### H4. Which sentence would you quote in a rejection? **CONCEDED, and it is the paper's own**

"Both scored pairs are negatives, so the rules' positive half was never tested
at all." It stays. A rejection built on a sentence the paper wrote about
itself is a rejection of a paper that told you where it was weak.

---

## Pass 5 — the literature-audit referee

### A1. Check three coded rows against the actual papers. **MEASURED**

**Measured** (`r49_audit_spotcheck.csv`): 9 quoted codes across 5 papers drawn
with the registered seed. The stated PDF page exists in 9 of 9, and the quoted
sentence is **on that page in 9 of 9**.

### A2. Would you accept this audit if your own paper were in the sample? **CONCEDED — with the number that makes it fair to ask**

The mechanical screen's precision is 66.7%: a third of the papers it admitted
are, on a read, not reporting a with-and-without comparison at all.

**Disposition.** The paper's primary proportions use only the 20 a read
confirms; `results/r40_coding.csv` ships the mechanical sheet and
`results/r40_adjudication.csv` ships the read, with a note per paper saying
what it actually does. An author whose paper is in the sample can see, in one
row, both what the machine said and what a person said.

### A3. The frame excludes the conference literature this paper's own community publishes in. **CONCEDED, with the counts**

**Disposition.** §4.1 gives the measurement that forced it: the BPM source
record carries 69 works for 2019–2026 and *none* flagged open access; CAiSE
carries one; ICPM has no source record. The venues are covered through the
citation frame and the venue mix of the included set is reported.

### A5. The topical pre-filter is a constructed control. Null it. **MEASURED — and it runs the conservative way**

Frame A filters titles and abstracts by keyword; frame B does not. If the
filter selected papers that are unusually careful, the audit understates the
practice failure.

**Measured** (`r49_frame_null.csv`): on the four codes where the two frames can
be compared, the filtered frame's papers are **more** careful on every one, by
up to 23.3 percentage points on `M_justified`; on `Range_reported` both frames
are at zero. The unfiltered arm is 11 papers, so this is a direction and not an
estimate — and the direction is the one that makes the reported failure a lower
bound.

**Disposition.** §4.4 reports it, with the small-n caveat in the same sentence.

### A4. `unclear` on `Theta_stated` is larger than `yes`. **DISMISSED — that is what `unclear` is for**

23 of 54 under the mechanical coder. The protocol registers `unclear` as a
value the rule *assigns*, reported separately from `no` and never folded into
it, and the adjudication resolves it on the subsample.

---

## Pass 6 — the editor

*Brief: is this one paper or three? Would you send it out? What would you say
in a desk-reject letter?*

### E1. This is a literature audit, a theory note and an empirical study. **CONCEDED — and answered in §1**

**Disposition.** §1 now carries a paragraph titled *Is this one paper or
three?* whose answer is that each of the three is the reply to an objection
the other two provoke: the empirical study alone is a null on one estate, the
propositions alone say nothing about what happens, the audit alone shows a
practice without a cost. Split it and each piece loses its own defence. It is
in the introduction rather than the cover letter because a reader deserves the
reason where they first wonder.

### E2. Forty-two pages of main text and seventy-one in total. **CONCEDED, and recorded**

`submission/DECISIONS.md` records the target (36), the plan's own per-section
budget (41), what landed (42), and what moved to appendices to get there —
five subsections, one figure and three nulls, none of which carries a claim
the main text does not still state.

### E3. What would the desk-reject letter say? **CONCEDED — it is quoted, and answered where it can be**

It would say: *single unaffiliated author, no deployment, no organisational
partner, a methodological argument illustrated on a public benchmark.* Three
of those four are in §17 in exactly those words, and the fourth — the author
profile — is now **counted rather than excused**: of 3,360 research articles
published 2024–2026 across eight candidate venues, five are single-author and
unaffiliated (`r48_venue.csv`). The cover letter says so rather than hoping
nobody checks.

### E4. Would you send it out? **The honest answer, recorded**

On the technical work, yes. On fit, that is what `submission/DECISIONS.md` §15
re-took against six criteria fixed in advance, and it changed the venue.

---

# Round twenty — the developmental review

A second, developmental review of the round-nineteen manuscript recommended
**reject and invite resubmission** and listed eight submission-blocking
scientific problems (P0.1–P0.8), six methodological strengthenings
(P1.1–P1.6), three positioning items (P2.1–P2.3), a restructuring plan and
five red-team gates. `submission/response_to_blueprint.md` is the
point-by-point reply. Every item is dispositioned below, and the corrections
each one produced are named so that the register in Appendix D can be read
backwards from the objection.

The organising observation, because it explains why the repairs cluster: four
of the eight blocking problems are the same mistake in different places — **an
inferential object that did not match the sentence it licensed**. A family
smaller than the claim it covered; a variance component that was not the
component it was named as; an average over units that do not add; a theorem
stated wider than its proof.

### B1. The region analysis was computed on a sub-grid and described as a property of the declared surface (P0.1). **CONCEDED — and the denominator is now an audited object**

Three surfaces are named and counted from the files: **declared**,
**computational** and **inference**. `s25_denominator.py` asserts
`observed = expected − declared exclusions` and `duplicates = 0` per pair
rather than leaving the manuscript to claim them. The inference surface is
declared before any draw by a rule reading only a log's row count, and is
**axis-complete** — round nineteen's grid held the split axis fixed, which is
the specific defect that made the old denominator indefensible rather than
merely small. The restriction is measured: the share of positive cells differs
between the declared and inference surfaces by a median 0.064.

One consequence is stated rather than left to be found: *uniformly* beneficial
is easier to reach on a smaller cell set, so that one count is an **upper
bound** on what the declared surface would give.

### B2. Simultaneous inference was taken over a family smaller than the claim (P0.2). **CONCEDED — correction C26**

Four interval objects are constructed and named — pointwise,
within-instrument, whole-surface and decision-curve — and every table says
which it prints. Region labels use the whole-surface family and nothing else.
The critical value is estimated by a **Gaussian multiplier bootstrap** over
the standardised draw matrix, which decouples the precision of the critical
value from the refitting budget; this was not asked for and is the round's one
methodological addition beyond the list.

### B3. Specification regret averaged incommensurable units (P0.3). **CONCEDED — correction C27**

All three designs the review offers are implemented: metric-specific
(primary), common operational utility on calibrated net benefit, and partial
identification over a declared family of five monotone utility maps. No
average in the paper crosses an instrument.

### B4. The interaction share was the largest per-axis difference (P0.4). **CONCEDED — correction C25**

The per-axis differences overlap across axes and their maximum is neither the
sum nor the union of the higher-order components. The total higher-order share
is one minus the sum of the first-order indices, every disjoint component is
computed, and the identity that the components sum to one is asserted
numerically on every decomposition.

### B5. The measure over specifications was implicit (P0.5). **CONCEDED — and one conclusion did not survive it**

Four measures are declared and reported. Under the **concentrated** measure —
a reader who rarely departs from the reference specification — a single axis
carries more variance than everything higher-order combined on most pairs, so
"the interactions dominate" is a claim about a measure and not only about a
surface. This is reported as a substantive finding in the results and in the
limitations rather than as a caveat, because it is one: how much interactions
matter is a fact about how far a reader roams.

### B6. Proposition 2 was stated wider than its proof (P0.6). **CONCEDED — corrections C23 and C24**

Proving it generally showed the claim was **false**, not merely unproved: what
invariance of the reduction requires is that the recalibration act *affinely*
on the instrument, which is strictly weaker than rank-basedness, and a
non-rank-based instrument with an invariant reduction is exhibited. The axis
non-redundancy search is withdrawn entirely.

### B7. Bootstrap p-values of zero, and the word "confirmatory" (P0.7). **CONCEDED — corrections C29 and C30**

The plus-one estimator at 2,000 independent draws, with the smallest
attainable raw and Holm-adjusted values printed beside the table. The
contrasts are **final-round planned contrasts**, not confirmatory, and were
relabelled **PC1–PC5** in the second session because C1–C5 collided with the
correction register's own identifiers in the same section.

### B8. Decision curves read thresholds as cost ratios on uncalibrated scores (P0.8). **CONCEDED — correction C31**

Calibration is fitted inside the training half, repeated inside every
bootstrap refit, and raw-score curves are labelled score-threshold sensitivity
analyses. The decision-curve conclusions are qualitatively stable after
calibration, which is reported rather than assumed.

### B9. The bootstrap validation was too limited for a methods paper (P1.1). **MEASURED — `s31_simboost.py`**

Nine demands; `s10_simulation2.py` met four. `s31` meets the rest: 1,000
replicates in each of six worlds, Monte Carlo standard errors on every
coverage, bias and width, sample size and register cardinality varied
**jointly** over ten cells to a 3,019-level register, three block lengths
around the rule of thumb, and seven interval constructions including
m-out-of-n subsampling in the sparse regime.

The result is a **NEGATIVE** one and is reported as such. In the sparse
regime — the one that motivates subsampling — the nested percentile interval
covers 37.2% against a nominal 95%, the bias-corrected percentile 63.1%,
m-out-of-n 72.8%, and the basic (pivotal) interval 89.9%. Subsampling does not
rescue the sparse world and undercovers on the well-behaved worlds too, so the
paper keeps the basic interval and prints all seven coverages side by side.

### B10. Sensitivity indices and region summaries had no uncertainty (P1.2). **MEASURED**

The decomposition is recomputed inside every bootstrap draw; corpus medians
are bootstrapped with the log–target pair as the resampling unit; no axis is
called dominant where intervals overlap.

### B11. The quality mechanisms were independent coin flips (P1.3). **MEASURED**

Three dependent mechanisms added — on time, on the item's recorded type, and
on a training-estimated propensity that correlates missingness with the
outcome — plus severity curves over several levels and repeats over seeds. All
are verified train-only **by execution**, and the check caught a real leak in
the propensity mechanism itself (section 25.6 of `HANDOFF.md`).

### B12. Construct validity across a heterogeneous corpus (P1.4). **CONCEDED, with a table**

One row per pair: the field playing the register role, why it behaves as a
maintained and reused entity, and the specific threat to construct validity
that pair carries. The corpus is a benchmark of specification sensitivity
across heterogeneous problems, not a replication, and nothing is averaged
across pairs.

### B13. Discipline the CMDB case study (P1.5). **CONCEDED**

Two decision times, a knowledge-field availability curve a reader can place
their own belief on, and decision curves only after calibration.

### B14. Remove or radically reduce the practice pilot (P1.6). **CONCEDED — correction C28**

One paragraph in the main text; protocol, screen accuracy, PRISMA-style flow
and prevalence estimation in Appendix G. The Wilson intervals built on a
fractional effective sample are withdrawn and replaced with a stratified
bootstrap and a design-based linearised interval; none of the five Wilson
intervals contains its design-based counterpart. One machine-assisted
adjudicator and no independent human reliability study is stated prominently,
and no claim in the paper depends on the pilot.

### B15. State the novelty narrowly (P2.1). **CONCEDED**

The introduction now distinguishes existing components, the new formalisation,
the new reporting objects — naming which two are adaptations and which two are
new — the new empirical evidence and the new operational case. The second,
overlapping novelty statement in related work was merged into a single
paragraph naming the gap in four places.

### B16. Proposition 4 is interpretive, not difficult (P2.2). **CONCEDED**

It is a **lemma**, its three strong assumptions are named in the sentence that
states it, and the manuscript says in terms that the scientifically difficult
part is specifying the utility and the weighting rather than proving the
identity. The in-sample check is reported as an algebraic check and the rules
are compared out of sample.

### B17. Remove Computational Result 1 (P2.3). **CONCEDED — correction C24**

Withdrawn. Its answer moved between zero and five of twelve ordered pairs as
an arbitrary tolerance was swept; nothing depended on it.

### B18. The manuscript is too long (the restructuring plan). **CONCEDED IN PART, and the shortfall is stated**

The structure is now the recommended one, section for section, with simulation
promoted to its own section and the pilot demoted to a paragraph. A new
Appendix C carries the constructions moved out of the inference section. The
body is nevertheless about 19,700 words against a requested 13,000–15,000, in
64 pages of main text and 33 of appendices: six
of the ten recommended sections are inside their budgets, two are under, and
the two over are the two in which the Priority 0 list required new objects to
be defined. The response names the two sections we would cut if the editor
insists rather than choosing for them. `python scripts/texlint.py --sections`
prints the table and `check_response_refs.py` checks the response against it.

---

# Round twenty-one — the second developmental review

A second developmental review read the round-twenty manuscript, recommended
**major revision**, and noted that a strict reviewer would recommend
reject-and-resubmit on M1 and M12 alone. Twelve major comments and eleven
minor ones. `submission/review_round21.md` is the report as received;
`submission/response_to_review21.md` is the reply.

### M1. The case study's headline number appears with two values and two signs. **MEASURED**

The most serious objection this project has received, because it is the class
of error the whole verification apparatus exists to prevent. `s32_cohort.py`
estimates the increment at the later decision time over the full cohort x
target factorial at three rungs, 24 cells at 400 nested draws. The
reconciliation is a one-factor-at-a-time path and the answer is a finding: the
target carries 99.3% of the difference, the cohort 0.008%. Two candidate
explanations were ruled out by computation. Section 7 is now on one cohort
throughout (`s39_case_quality.py`, and `s08` re-run under a declared
tie-break). `round21_verify.py` adds an `ESTIMANDS` table that fails when two
macros naming the same quantity disagree.

**Why the old harness could not have caught it.** Every check in this
repository verifies a macro against its own source file, and both macros were
right about theirs. What was wrong was that two of them answered to the same
English sentence. A check on a single number cannot see that; a check on the
SET of numbers can, and is what the ESTIMANDS table is.

### M2. The decision time is a relabelling of the baseline. **MEASURED**

`s38_tau.py`. Three decision times, each with its own population, its own
register and its own admissible set, one decision. The population costs
-0.0297 AUC with the information held fixed; the feature snapshot a further
-0.0175 before any baseline changes. All three resolve.

### M3. Two of the four objects rest on bands the paper declares unreliable. **MEASURED**

`s33_calibrate.py`. A denser (n, K) plane; a widening factor that is the 0.95
quantile of the studentised error, so it is computed rather than searched for;
a fitted curve in log(K/n); and every region label and rho in the article
computed under the calibrated critical value, with the nominal one printed
beside it.

### M4. The misreport rate counts cells whose sign is not resolved. **MEASURED, and the headline fell**

`s34_reporting.py`. Three rates: all cells, resolved cells, magnitude-weighted.
The article's headline is the second and is smaller than the number it
replaces. The magnitude-weighted rate is HIGHER than the unweighted one and is
reported as such.

### M5. The practical stakes are thin. **CONCEDED after measuring**

`s35_utility.py` adds a registered calibration screen, a desk threshold
distribution and a per-thousand-cases unit. The rules still mostly tie and the
article says so in a paragraph of its own; the regret comparison is demoted to
a check. What the section gained instead is the cost of deploying at the wrong
decision time, which is larger than every difference between the rules.

### M6. Novelty is narrower than the length implies. **MEASURED**

`s36_sca.py` runs specification-curve analysis as practised, unchanged, on the
same declared sub-surface, and the article reports where the two verdicts part
company.

### M7. The learner axis is confounded with the encoding axis. **MEASURED**

`s37_axes.py`. Crossed on the case study's log: encoding 10.1%, family 5.2%,
their interaction 9.8% -- the largest two-way term. The axis is called a
pipeline throughout and the confound is named.

### M8. Five corpus statistics that cannot be reproduced from the printed tables. **CONCEDED, all five**

Aggregations labelled; PC3's one-sided p derived against its two-sided
interval; the denominator table put on one basis with the model-fit column
named; the master surface's intercept-only rung stated.

### M9. Excluded pairs appear in an appendix table. **CONCEDED**

The layer table is filtered by the surface's own admission list and its
caption states the count dropped.

### M10. Corpus statistics mix two populations. **MEASURED**

Every headline statistic on all 19 pairs, the 8 ITSM pairs and the 11 others.

### M11. The literature pilot should not be in the paper. **CONCEDED**

Supplementary material; three sentences in the article; and the declaration
now records that the model identifier for its adjudication was not captured.

### M12. Ninety-seven pages written as a commentary on its own errors. **CONCEDED IN PART**

The appendices are a separate document. Zero occurrences of "an earlier
version of this work" and zero of "correction Cnn" remain in the article, and
`texlint` fails the build if either returns. The prose is in a plainer
register. The article is nevertheless longer than the 35-40 pages the review
asked for, and the response says by how much and what would have to go.

---

# Round twenty-two — an independent pre-submission review

Before submitting, the round-twenty-one manuscript was given to an independent
reviewer with the journal's own brief, no knowledge of what had changed, and
access to the repository to check any number it doubted. It returned **major
revision** with nine major comments and twenty minor ones, and six of the nine
were defects rather than differences of opinion. Every one of the six was
verified against the result files before it was acted on.

### R1. The inference surface is not a subset of the declared surface. **CONCEDED — the worst finding of the round**

On `BPIC19/duration` and `RoadFines/duration` the whole-surface band carries
the pipelines `{logit, logit_fr}` while the declared surface carries
`{logit, hgb}`: sixty of each pair's hundred and twenty band cells had **no
counterpart in the design declaration**. The region label and rho for those
two pairs therefore quantified over cells the design space says do not exist.

The cause is a deliberate choice in the right place and a missing one in the
other: `s20` gives the two largest logs the ENCODING pair because a boosting
fit refitted inside every draw is unaffordable there, and `s01` gave every
non-primary log the FAMILY pair. Neither file was wrong about itself.

**The declared surface is what widened** — one logistic fit per cell is cheap,
and narrowing the inference surface is not — so the two largest logs now carry
three pipelines in the declaration and the two `s20` can afford in the bands.
The whole surface was recomputed and everything that reads it with it.

**Why the audit missed it: it checked level COUNTS and not level IDENTITY.**
`round21_verify` now asserts the subset relation cell for cell, which is the
only version of the check that would have caught this.

### R2. Two macros described in the same words held 892 and 846. **CONCEDED**

The same gap, arriving four pages apart in the prose. Both are now
`ESTIMANDS` entries and must agree. So is the headline rate, which was
5.6% in the abstract and "a tenth" in Highlight 4 — the nominal figure. **The
Highlights were the one part of the submission the macro discipline never
covered**, and they are the first thing an editor reads.
`scripts/make_highlights.py` generates them from the macros now, and the
verifier fails if the file does not match what the current macros render to.

### R3. The master table printed uncalibrated labels and a superseded column. **CONCEDED**

Section 6.4 says in bold that every region and rho in the paper is the
calibrated one; Table 3 took both from the nominal file, four labels differed,
and the median rho a reader computed from it was 0.117 against the 0.017 the
conclusion quotes. Its sign-disagreement column came from a round-nineteen
file that disagrees with the round-twenty-one one on ten of nineteen pairs and
still carries a "uniformly beneficial" label the paper's headline denies. Both
columns now come from the current files, and the captions name them.

### R4. The design space pools three kinds of axis. **CONCEDED, and it costs the headline a third**

Analyst latitude (pipeline, rung, instrument), resampling (the split, five of
whose six levels are folds on the same data) and counterfactual states of the
world (register quality) were averaged into one rate. Restricted to the axes
an analyst actually chooses, the sign-disagreement rate falls from 32.8% to
about 20%. Both are now reported, the decomposition is partitioned by kind,
and Section 11 says that the region labels are conditional on the quality axis
being averaged over.

### R5. No corpus-level headline carried any uncertainty. **CONCEDED**

Every cell of the family table now carries a percentile interval from a
cluster bootstrap with the LOG as the resampling unit, because two targets on
one log share a cohort. The resolved-cell row was a median of per-pair rates
and printed 0.000; it is a pooled ratio now. **And the pooled rate is lower on
the ITSM family than on the rest**, which is the population the paper's
argument is about, so the corpus-wide headline is partly carried by the pairs
the paper itself names as construct-validity threats. That is now in the text.

### R6. Corollary 1's witness does not support it. **CONCEDED — the proposition is restated**

Proposition 2 quantified over every strictly increasing continuous map;
Corollary 1's witness, the class-mean gap, is invariant only inside the AFFINE
family, and this repository's own `s29_wider.csv` records shifts up to 0.638
outside it. The corollary therefore did not establish the separation at the
proposition's scope.

The proposition is now stated **relative to a declared family** $\Psi$, which
is both what the proof reaches and what an analyst can act on; the corollary
is stated for the affine family; and a new remark reports the non-affine
shifts and says plainly that the separation is family-relative and that the
unrestricted question is open. `round21_verify` checks both directions.

### R7. The design space omits the axis predictive process monitoring varies. **CONCEDED**

Prefix length, prefix bucketing and sequence encoding cannot be axes here
because this study predicts at one prediction point. Sections 2 and 11 now say
so and say that the corpus result therefore does not measure the sensitivity
of that literature's benchmark conclusions.

### R8. Two pieces of load-bearing evidence rest on thin designs. **MEASURED**

The calibration's counts are now reported at three settings --- nominal,
calibrated, and every factor pushed to the upper end of its own Monte Carlo
interval --- so a reader who rejects the transfer can read the nominal column.
The specification-curve comparison now runs on **every** admitted pair rather
than on three chosen to illustrate three outcomes.

**What that cost, and the second budget it forced.** A permutation replicate
refits every cell of every pair, so the experiment is quadratic in the
corpus's largest logs: on BPIC19, at 251,734 cases, one replicate of the
twenty-four-cell design took three quarters of an hour, and the run over
nineteen pairs was on course for most of a day. The sub-surface already
bounds the *cells*; the rows each fit sees are now bounded too, by a declared
cap of twenty thousand cases per pair — a seeded sample drawn once and
restored to time order, so the observed surface and its null are computed on
the same cases. It binds on four logs, is recorded per pair in
`s36_verdicts.csv`, and Section 6.7 states it. It does not touch the region
labels the verdict is set beside, which are computed on the full data by
`s33`.

**And the run would have crashed at the end.** `s36` renames the calibrated
region columns of `s33_regions.csv` onto `region` and `rho` — names that file
*also* carries for the nominal ones — so `g.rho` was a two-column frame and
`float()` of it raised. The failure is in the last twenty lines of the
script, after every fit, so it would have surfaced only after the whole run
had been paid for. The nominal columns are dropped before the rename now.

### R9. Length, legibility, and an incomplete exclusion ledger. **CONCEDED IN PART**

The construct table's columns were touching at 3pt of separation and are set
at 5pt; Figure 1's panel labels sat on the tick labels and are inside the top
right now; its axis-level legend is larger and its levels are spelled out. The
ledger was incomplete in the direction that matters: two logs were downloaded
as a **held-out set** for a separate test and were never offered to the
admission rules, so they appeared neither among the admitted pairs nor among
the exclusions. They are in the ledger now under `HELD_OUT`, and the
data-availability statement no longer claims more than the table delivers.

**Length.** The reduction was done in three separable moves, so that no
evidence was lost to it. Nine tables and two figures moved to the supplement;
three result subsections — the family-by-encoding crossing, the decision-rule
comparison, and the calibration, unseen-category and rolling-origin
diagnostics — moved to Supplement S11 with a paragraph of numbers left in the
article; and the coverage calibration's derivation moved to Supplement S10.
Then about 3,300 words of restatement came out. **Four sections were
describing the coverage calibration and one does now.** The article carries
seven tables and five figures against sixteen and seven, every one of them now
named in the running text. The remaining gap to the review's 35–40 pages is
stated in the response with the arithmetic that produces it: the same review
asked for eight new measurements, which are about eight pages of article, and
they were added.

**And the build summary was checking one document of two.** It reported the
article's overfull boxes and said nothing about the supplement's, which had
**seventy** — sixty-two of them in the construct table alone, where five
columns held single unbreakable tokens (`enforcement`, `org:resource`) in
`p{}` columns narrower than the tokens, so every one of them printed past its
column edge. That is the run-together look the review's twentieth minor
comment described, and it had survived four rounds because nothing looked.
Those columns are natural-width now and the guarded `\resizebox` takes up the
slack; the same defect in the corpus severity table is fixed the same way;
and `build_journal.py` prints both documents' counts. Four wide tables were
also rebuilt with fewer columns — the planned contrasts lost a column that
restated Section 4.4 word for word, the master table and the decision-time
table print an interval as one column instead of two endpoints as two, and
the region table prints its three cell counts as one triple per critical
value, dropping it from fifteen columns to eleven. **Both documents now build
with zero overfull boxes.**

---

# Round twenty-three — two blind referees, and the object they broke

The round-twenty-two manuscript was sent to two independent readers with this
journal's brief, no knowledge of its history, and access to the repository to
check any number they doubted. One was asked to read as a methodologist, one
as an information-systems and process-mining referee. **Both returned major
revision.** Neither recommended reject; neither recommended accept.

They agreed on four things and each found something the other did not. Every
finding below was reproduced from the deposited files before it was acted on.

## R23.1 The simultaneous band's critical value is contradicted by the paper's own second estimate. **CONCEDED — the worst finding in three rounds**

`s21` writes two estimates of the same max-$t$ critical value side by side:
the Gaussian multiplier quantile `q`, which the bands use, and the empirical
quantile `q_emp` of the same $B$ observed maxima, with its order-statistic
interval. Nobody had compared them.

**`q` lies below the *entire* order-statistic interval of `q_emp` on 15 of 19
whole-surface families and on all 19 decision-curve families**, in the
anti-conservative direction. Median ratio: 1.29 on the surface families, 2.09
on the decision-curve ones (3.87 against 8.10). The manuscript's only defence
was that the empirical quantile is imprecise — a median order-statistic width
of 2.0 against the multiplier's 0.04 — which is an argument about *variance*
and says nothing about a systematic one-sided gap.

The cause is not the draw count. A Gaussian multiplier reproduces the
empirical *covariance* of the standardised draws and therefore only the
excursions a Gaussian process makes; these draws are heavy-tailed. The
referee's synthetic check makes the direction unambiguous: at the corpus's
family sizes and draw counts the multiplier is accurate under Gaussian draws
and badly anti-conservative under $t_3$ draws.

What it costs, computed from the deposited bands file:

| | multiplier | empirical |
|---|---|---|
| resolved whole-surface cells | 1,150 | **995** |
| resolved decision-curve cells | 3,066 | **613** |

The decision-curve exposure is fivefold and undisguised, because the coverage
calibration of Section 6.4 is estimated for the scalar instruments and is
**not** applied to that family — which the manuscript had also never said.

**What was done.** `s40_qcheck.py` computes both counts and the per-family
comparison. Section 4.3 carries a new paragraph stating the disagreement, its
direction, its mechanism and what each estimator resolves. Section 6.4 reports
the empirical count as a fourth setting beside the three calibration settings
— and it moves the resolution by more than the calibration does. Section 8.3
states that its family is uncalibrated and that its counts are upper bounds
under the empirical value. Section 11 carries it as the sharpest limitation
and says plainly what neither estimator settles: **nothing in this paper
measures the band's family-wise coverage against a known answer.** The
simulation validates the *pointwise* interval only. Extending it to
family-wise coverage, at the corpus's family sizes, draw counts and tail
behaviour, is named as the first thing to do with more compute. It is not done
here and the paper does not pretend otherwise.

## R23.2 $\tau_1$ and $\tau_2$ are not the same cases, so the information step was overstated by three quarters. **CONCEDED**

Table 7's caption said "$\tau_1$ and $\tau_2$ only in what is known about the
same cases" and Section 7.2 attributed the whole $-0.0175$ step to
information. The table's own columns said otherwise: $\tau_1$ carries 44,513
cases and $\tau_2$ carries 45,455, because 942 incidents have no interaction
record. The clean population/information separation is the operational
contribution of Section 7.2 and it was quoted again in the Conclusion.

`s38` now also runs $\tau_2$ **restricted to $\tau_1$'s population** — same
44,513 cases, same prevalence 0.4016. The decomposition is therefore:

| step | what changes | value |
|---|---|---|
| $\tau_0 \to \tau_1$ | population | $-0.0297$ |
| $\tau_1 \to \tau_2$ matched | **information alone** | $-0.0099$ |
| $\tau_2$ matched $\to \tau_2$ | the 942 unmatched incidents | $-0.0076$ |

The information channel was **$-0.0099$, not $-0.0175$**. The verifier now
checks that the two steps sum to the unadjusted one and that the matched
cohort really has $\tau_1$'s case count.

## R23.3 The same contrast was printed with two intervals, and the same ladder rung with two constructions. **CONCEDED**

`PC3` appeared as $[-0.00161, +0.01217]$ in Section 4.4 and
$[-0.00059, +0.01210]$ in Table S15. Both were right about their own file —
`s32` runs the cohort experiment at 400 draws, `s24` the planned contrasts at
2,000 — and the point estimate agrees to seven figures. What was wrong is that
the article quoted the 400-draw interval in the same paragraph as the
2,000-draw budget, beside a table printing the 2,000-draw interval, under a
supplement abstract promising that a quantity cannot differ between the two
documents. Every `PC3` macro now comes from `s24`.

**The ESTIMANDS guard could not have caught this, and now can.** It covered
point estimates only. `INTERVAL_SOURCES` declares, per interval macro, the
result file and row its endpoints must be re-derived from.

## R23.4 "No surface is uniformly beneficial" is unreachable by construction. **CONCEDED — both referees, independently**

A cell whose *point estimate* is negative can never be beneficial at any
critical value, and every one of the 19 pairs has one. The label was therefore
ruled out before any band, bootstrap or calibration was applied, and reporting
"zero at every setting" as robustness presented invariance to something the
label does not depend on. For the same reason $\rho = 1$ is not an attainable
state for any pair in this design.

Section 6.4 now leads with the informative reading — of the 13 pairs that
resolve any sign, 9 have no harmful cell and 4 resolve both signs — and states
that the uniform-beneficence count needs none of the apparatus. The
Conclusion's first bullet says the thing that is actually true of point
estimates.

## R23.5 The headline was quoted on the population the paper concedes is the wrong one. **CONCEDED**

The pooled resolved-cell misreport rate is 7.5%; on the eight ITSM pairs — the
population the paper says it is about — it is 3.6%, and 22.2% on the other
eleven. Section 6.6 said so; the abstract, the Highlights and the Conclusion
printed only the pooled figure. All three carry both now, and the abstract
also carries the 13-and-4 split. The Highlights are generated, so the first
line an editor reads cannot drift from this again.

## R23.6 The estimand was never defined as a population quantity. **CONCEDED**

Equation (1) is written on a fixed train/test split, so as printed $V_s(f)$ is
a deterministic functional of the log and an interval for it covers with
probability 0 or 1 — while Section 4.1 resamples the training half precisely
because the analyst does not want to condition on it. Definition 2 now gives
the population estimand $\vartheta_s(f)$, states that the split rule and the
pipeline are *part of* it rather than nuisances, and says that every printed
cell is an estimate of it and that "resolved" is a statement about it.

## R23.7 Six smaller things, each verified

- **The layer conclusion overstated its table.** "Coarse layers are close to
  free" against CI Type at $+0.134$ and the item at $+0.257$ on handover. The
  claim that survives is about the item's *marginal* contribution over the
  subtype, $+0.109$, and Section 7.6 states the layer figures per target.
- **Two prevalences for one cohort.** `s08` records the test half's and `s38`
  the whole cohort's; Section 7.1 attached the first to the 45,455-case cohort
  and then compared it against a whole-cohort figure for the other target.
  The cohort's prevalence is the cohort's now, and the test half's is a
  separate macro named as such.
- **The exclusion ledger was still incomplete.** A log offered to the
  held-out set's rules and excluded by them appeared in neither column. The
  ledger has a third source now, so "every downloaded log" is true as printed.
- **Figure 2's caption promised bootstrap intervals the figure has none of**,
  and called the hatched segment a remainder when it is one of the plotted
  segments. Worse, `set_xlim(0, 1.02)` clipped exactly the bars that exceed
  one — which they do, because each segment is a median over instruments and
  medians do not add. The limit comes from the data now and the caption says
  why.
- **`to_latex(escape=True)` escapes what you pre-escape.** `50\%` printed as
  `50\textbackslash %` and a math column heading as literal dollar signs.
- **"Coverage is governed by $K/n$" was stronger than the grid supports.**
  Two cells at nearly the same ratio cover 0.780 and 0.613, and holding $K$
  fixed while moving $n$ moves coverage by 16 points. Section 10.3 now says
  the ratio captures most of the dependence and not all of it, and that the
  calibration inherits the residual.

## R23.8 Length, again

Both referees said the article is about twice the length its content supports.
The practice pilot and the correction register are **out of the submission
entirely** — not compressed, not moved to the supplement, removed to the
archive — which is what both asked for and what the round-twenty-one review's
eleventh comment had asked for before them. Section 9.3 now states in four
sentences that the prevalence of one-number reporting is not established here
and that the paper's argument does not need it.

## R23.9 What this round did not do

The band's family-wise coverage is still not validated against a known answer.
That is the methods referee's "single most important thing", it is correctly
identified, and it is a new experiment rather than an edit. The paper now
reports both critical-value estimates and what each resolves, states the gap
as its sharpest limitation, and names the experiment that would close it. A
reader who wants the conservative reading has the numbers to take it.

---

# Round twenty-four — a third blind referee, and a sentence that was simply false

The round-twenty-three manuscript was sent to a third independent reader under
the same conditions as the two before it: this journal's brief, no knowledge
of the paper's history, repository access to check any number. It returned
**major revision**. It reproduced about thirty printed quantities from
`results/` — the denominator, the baseline spread, the 892/67/7.5% chain, the
ITSM split, every first-order median of Table 3, the critical-value
comparison, the calibration factors and the case-study ladder — and found
every one correct. Then it found seven things that were not.

## R24.1 A sentence about simulated coverage is false against the paper's own grid. **CONCEDED**

Section 10.3 said coverage "holds at or above 90.0% while $K/n$ is at most
0.050". In `results/s31_coverage.csv` the cells at or below that ratio cover
**0.887, 0.893, 0.893, 0.900 and 0.907** — the minimum is 88.7%.

The macro was the trap. `simGridCoverageSafe` was defined as the minimum
coverage *among the cells that attain 0.90*, and `simGridRatioSafe` as the
largest ratio at which some cell attains it. Both are extrema over a selected
subset; the manuscript read them as a guarantee over a range. **A macro is
only as safe as its definition, and the verifier could not catch this because
the macro matched its source exactly.** The pair is replaced by
`coverageGridSafeMin`/`coverageGridSafeMax` — the honest range over every cell
in the band — and the old macros are no longer emitted, so the sentence cannot
be rebuilt from them.

## R24.2 The coverage calibration is an extrapolation in $n$ over most of the corpus. **CONCEDED — the referee's single most important item**

The plane that identifies the inflation factor is estimated at training sizes
**2,000, 4,000 and 8,000**. This corpus runs **735 to 176,213** training rows,
so **3 of 19 pairs** lie inside the range the factor was fitted on: nine below
it and seven above. Section 10.3 proves in the same document that $K/n$ does
not determine coverage — holding $K$ at 1,000 and moving $n$ from 2,000 to
8,000 moves coverage from 0.453 to 0.613 — so a factor that is a function of
the ratio alone is being read outside the region that identifies it on most of
the corpus. Section 11 stated the transfer as an assumption in general terms
and never told the reader how far it reaches.

Section 6.4 now states the reach where the factor is applied, and Section 11
carries it as a limitation of its own with the arithmetic. Widening the plane
in $n$ is named as the cheapest outstanding improvement.

## R24.3 The headline was quoted at one band setting when the file held another. **CONCEDED**

`\misreportPooledResolvedNominalPct` (11.9%) existed in `numbers.tex`, was
computed correctly, and was used **zero times** in either document, while the
calibrated 7.5% was used four times including the abstract. Section 6.4 makes
a virtue of reporting region counts at several settings; the headline deserved
the same. Section 6.5 now prints both and says the calibrated figure is the
smaller — the conservative choice, but a choice.

**And one number was withdrawn rather than printed.** A rate under the
empirical critical value was drafted for the same sentence and computed 4.7%
where the correct value is near 11%: the quick version took each pair's
reference sign from the first row of a group rather than from the reference
cell. It is not in the manuscript. What is printed instead is the empirical
band's resolution *count*, which `s40` computes correctly.

## R24.4 The section names two defects in its own rate and corrects them one at a time. **CONCEDED**

Restricting to analyst-latitude cells gives 20.0%; restricting to resolved
cells gives 7.5%; the two were never imposed together although the argument
asks for it. Jointly: **27 of 210 cells, 12.9%** over the corpus, and 7.5% on
the ITSM eight. `s34` computes it now and Section 6.5 prints it as the rate
that answers "how often would a one-number report be wrong about a sign the
data determine, on a cell an analyst might actually have stood on".

## R24.5 The headline's denominator is concentrated in three logs. **CONCEDED**

Of the 67 disagreeing cells, **65 come from three logs** and only **4 of 13
logs** contribute any at all. Two of the three also carry the smallest
bootstrap budgets — 33 complete draws of 40 — so the largest contributors to
the headline are also its noisiest. Both facts are in Section 6.5 and Section
11 now.

## R24.6 A supplementary table was the wrong object, chosen by row order. **CONCEDED**

The decision-curve table filtered on log, target, learner, quality and rung
but **not on split**, so the frame spanned two splits and a `.head(31)` chose
between them by row order. The rows were the raw-score curve while the text
and figure beside it read the isotonic-calibrated one — which Section 8.2
states must be labelled wherever it appears — and the caption named neither
the log, the target, the split nor the calibration. The sentence citing it
quoted two numbers the table does not contain. **A supplementary table that
fails the paper's own reporting standard is not a small defect.** The split is
fixed, the calibrated curve is selected where the file carries one, the
caption names the cell, and the citing sentence points at what the table
actually shows.

## R24.7 Definition 3 defines a label over a set the paper does not compute on. **CONCEDED**

"Uniformly beneficial if every admissible cell is beneficial" — but the labels
are computed on the inference family, a median 16.7% of a pair's admissible
scalar cells. The direction is not neutral: a claim about every cell is easier
to sustain over fewer cells, and *uniformly beneficial* is the label most
helped. The definition is now stated relative to the declared family
$\mathcal{F}$, $\rho$'s denominator is $|\mathcal{F}|$, and the asymmetry is
spelled out underneath it.

## R24.8 What three blind referees have now agreed on

All three returned **major revision**; none returned reject and none returned
accept. Two of the three independently found that "no surface is uniformly
beneficial" is unreachable by construction, and two independently found that
the headline was quoted on the population the paper itself calls the wrong
one. Both are fixed. The one thing none of them could check, and that all
three would want, is still outstanding and still stated: **nothing in this
paper measures the simultaneous band's family-wise coverage against a known
answer.**

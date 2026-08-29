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

# Round twenty-five — the outstanding item closed, and four defects found closing it

This round works the handoff's priority list: item A (the band's family-wise
coverage), item B (the coverage calibration's reach in $n$), item C (length)
and item D (round twenty-four's undone minor comments). It found four things
nobody had asked about, three of them because a gate could not see them.

## R25.0 The environment the reader is told to build did not build

Three defects in the setup, all of which only a second machine could find.

`requirements.lock` never carried **jinja2**. pandas routes
`DataFrame.to_latex` through its Styler, which imports it, so a reader who
followed `REPRODUCE.md` exactly got an `ImportError` out of the first gate and
no table at all. It never carried **pytest**, **requests** or **pymupdf**
either, though `requirements.txt` has pinned all three since round eighteen.

pytest's absence was not loud. `make_numbers.count_tests` fell back to
counting `def test_` lines when pytest would not collect, and wrote **42**
into section 9 where the suite collects **108** — past every gate, because no
verifier re-derives that macro. Its own docstring called that fallback "the
kind of number this paper exists to complain about". The fallback is gone; a
number this file cannot compute is now an error. Its cache is keyed on the
test files' content rather than their modification times, which a fresh clone
rewrites.

`provenance.py` hashed raw bytes, so a checkout whose line endings differed
from the accepting machine's reported every script as stale: a fresh clone on
Unix reported **twenty of thirty-seven** out of date and not one had changed
by a character. A guard that fires on a checkout artefact teaches its reader
to ignore it. The hash is now taken over content with line endings
normalised, and `--renormalise` migrated the twenty entries one at a time.

## R25.1 The band's family-wise coverage, measured. **ITEM A — CLOSED**

Section 4.3 ended by saying nothing in this paper measured it.
`scripts/s41_bandcoverage.py` measures it, and the band does not attain its
nominal level anywhere in this corpus's configuration.

The design is deliberately the most favourable case the band can be given: the
truth is zero at every cell, and the point estimate and the bootstrap draws
come from the *same* distribution, so the bootstrap is not an approximation of
the sampling distribution but is it. Every way a resampling scheme can be
wrong is switched off. What remains is the object under test — a standard
error and a critical value estimated from the same handful of draws — so every
coverage below is an **upper bound** on what the real procedure attains.

| | multiplier (what the bands use) | best of five | control: per-cell |
|---|---|---|---|
| Gaussian draws | 87.3% median, 74.8% min | 92.1% | 90–94% |
| the corpus's tails | 84.6% median, 76.1% min | 92.2% | 90–94% |

Three things follow that the paper did not know.

**The safeguard is not one.** Resolving a cell only at the upper end of the
critical value's Monte Carlo interval — which section 4.3 describes as the
conservative choice — moves coverage by less than a point. It controls the
Monte Carlo error in $q$ and not the error in what $q$ estimates.

**The binding constraint is the draw count, not the estimator.** 82.0% at 33
draws, 95.8% at 400. And the per-cell interval underneath the band is itself
only 90.3% at 33 draws: part of what the band loses it loses before any
critical value is chosen, and section 10.2 validated that construction at a
refit count this corpus does not reach on most pairs.

**A Rademacher wild multiplier, which preserves the observed draws'
magnitudes instead of replacing them by Gaussians and is the natural repair
for a tail problem, is worse than the Gaussian one.** Reported as the
negative result it is.

We did not switch the reported bands to a wider estimator. The one that helps
is the empirical quantile at the upper end of its order-statistic interval,
not the Monte Carlo upper end the paper already calls conservative — and it
reaches 92.2% at 1.52 times the width and still falls to 86.5% on the
smallest family. Substituting an estimator that is also wrong, and less
visibly so, is worse than reporting the bands as computed and saying what
they are worth. Section 11 says what they are worth.

## R25.2 "These draws are heavy-tailed" was two different things under one word

Section 4.3 asserted it with no number behind it. The draws are in the
repository, so the sentence is checkable.

On the **surface** families the tail is real and statistical: a Nagelkerke
cell whose eighty draws run between $-2.5$ and $1.4$ with one draw at $-24$,
which is one refit that came apart on an instrument unbounded below. No
instrument dominates the family maximum.

On the **decision-curve** families it is largely **degenerate cells**. At a
threshold where both arms treat every case alike the net-benefit difference is
zero *by arithmetic*, and **841** cells of the corpus's curve families are
exactly `0.0` in at least nine draws of ten — 276 of BPIC14/handover's 2,853,
up to 17.2% of a single family, against **zero** such cells anywhere in the
surface families. `s21.critical` admits any cell whose spread exceeds a floor
stated in absolute units, so such a cell survives, and standardising it by
that spread sends its studentised value to the algebraic ceiling.

Excluding them moves the median $q_{\mathrm{emp}}/q$ on those families from
2.09 to 1.80 — and does **not** overturn R23's finding: $q$ still lies below
the empirical interval on 19 of 19 curve families and 15 of 19 surface ones.
Section 6.4's count of what $q_{\mathrm{emp}}$ resolves is, on those families,
partly a count of arithmetic, and the paper now says so.

## R25.3 Table S13 did not contain the axis its caption claimed. **FOUND WHILE ANSWERING R24's MINOR 4**

The minor comment asked which scale the axis-kind partition is taken under.
Answering it found the caption wrong and the sentence resting on it
reversible.

`s34` computes the partition on the primary scale, `raw-within-metric`, which
decomposes separately *inside* each of the five instruments and takes the
median across them. The instrument is a stratum there and cannot be an axis,
so the `analyst latitude` column held the pipeline and the baseline rung
alone — while `s34`'s own docstring, the table's caption and section 6.5 each
described it as "the pipeline, the baseline rung **and the instrument**". The
instrument's contribution was in no column of the table that claimed it.

It is not a labelling slip. The only scale on which the instrument *is* an
axis is the headroom rescaling, and on that scale the ordering reverses:
analyst latitude 19.2% against resampling 9.4%, where the primary scale gives
11.1% against 18.9%. Section 6.5 stated **in bold** that the split moves the
increment more than all three analytic axes together. Under the definition of
the column that its own paragraph gave, that is false.

Both scales are now computed, both are in Table S13, the caption says what
each is and why there are two, and section 6.5 reports both orderings with the
count of pairs each holds on — 10 of 19 and 7 of 19 — instead of the one that
read better.

## R25.4 The no-typed-numbers rule had a hole, and three results were in it

`texlint`'s check that every number in the prose is a macro reads `body_of`,
and `body_of` strips inline math before it looks. `$0.780$` was therefore
invisible to it, and section 10.3's argument that $K/n$ is not sufficient
quoted three coverages of the $(n,K)$ plane as literals — 0.780, 0.613 and
0.453 — along with four grid coordinates and a gap stated as "about three and
a half" standard errors, which is 3.2.

The hole is closed by an allowlist rather than a ban: a level, a nominal rate,
the standard normal quantile and the registered split all belong inside math
and are not results, so each is listed with its reason and anything else
fails. The new check caught a space-swallowing macro in the same edit that
added it. The two cells section 10.3 compares are now selected *by rule*, so
re-running `s31` on a different grid moves the sentence with it.

## R25.5 A float taller than its page is not an overfull hbox

`build_journal` reported both documents' overfull boxes — round twenty-two's
fix — and could not see a table running off the bottom of its page, because
that is a different LaTeX warning. Making Table S13 carry both scales doubled
it to 38 rows and it ran **650pt** off the bottom of its page with the page
number printed through it, and the build said "0 overfull hboxes".

Both documents are now scanned for oversized floats as well, which
immediately found a **pre-existing** one: Table S18's 33 operating points have
been 3.9pt taller than their page since before this round, with LaTeX
absorbing the difference by squeezing glue. Both documents are back to zero on
both counts.

## R25.6 Round twenty-four's minor comments, all eight

1. **Two missing citations.** Hutter, Hoos and Leyton-Brown decompose an
   algorithm's performance over its configuration space by the same device
   section 4.6 uses and were uncited; the paragraph now says what differs.
   Davison and Hinkley carry the pivotal interval in section 4.1.
2. **Reference-specification sensitivity.** The referee's arithmetic
   reproduces exactly: the corpus median moves 0.328 to 0.353 if the
   reference pipeline becomes target-encoded boosting, and runs 0.328 to
   0.382 across the five instruments; over all 26 one-axis variants, 0.328 to
   0.384. Table S14, and the headline is not an artefact of which cell we
   called conventional.
3. **Table S30's replicate count.** Added, with a per-cell Monte Carlo
   standard error: its cells run at 150 replicates against the core's 1,000
   and their coverages are nowhere near nominal, so the error is a median 3.0
   percentage points and reaches 4.1 — 3.7 times the 0.7 the manuscript
   quotes for the core, and computed at each cell's own observed rate.
4. **Table S13's scale and measure.** See R25.3.
5. **Table S1's unglossed columns.** Glossed, and `gain over b0` renamed
   `gain over base`, because on the marginal row it was the gain over $B_0$
   plus the second-finest layer, which is a different baseline.
6. **Section 5.1's "pre-registration".** It now says plainly that this is a
   file in a repository the authors control and not a timestamped
   third-party registration, and that any claim of prior commitment is no
   stronger than the repository.
7. **Section 5.4's admission margin.** BPIC14/handover has the highest
   prevalence of any admitted pair, 0.927 against a bound of 0.95, while the
   nearest pair excluded above the bound is at 0.959 — and it is the largest
   single contributor to the corpus, 4,800 of the 29,040 admissible scalar
   cells.
8. **Figure 2.** It was a stacked bar per pair whose segments were medians
   over five instruments. Medians do not add, so the bars did not sum to one
   and the caption had to forbid the addition a stacked bar promises. It is
   now one pair's exact decomposition beside the corpus as a median, a middle
   half and a full range, with nothing stacked.

## R25.7 The calibration plane, widened in $n$. **ITEM B — CLOSED, AND IT FOUND MORE**

The plane ran at 2,000, 4,000 and 8,000 training rows against a corpus
running 735 to 176,213, so 3 of 19 pairs were inside it. It now runs 500 to
180,000 across 33 cells, including three **constant-ratio ladders** --- $K/n$
held fixed while $n$ moves over two orders of magnitude, which is the design
that isolates $n$ and which the old plane, where the two moved together,
could not be. All 19 pairs are inside it.

**$K/n$ is not sufficient, and now it is measured.** $\log n$ enters the fit
at $t = 8.3$, and at $t = 5.2$ excluding every cell above 8,000 rows, so it
is not one point. The old plane gave $t = 1.45$: it had no leverage in $n$.
Along a ladder the measured factor moves by 0.22, which is 2.8 combined Monte
Carlo standard errors, and coverage itself by 21.7 points. The applied curve
is a function of the ratio alone and carries that as a residual; adding
$\log n$ to a parametric curve does not repair it and is worse than the
monotone curve on the criterion the monotone curve was adopted under, so the
residual is reported rather than fitted away.

**And past a crossing in $n$ the estimator stops existing.** The factor
widens an interval *about its point estimate*, and the basic interval does
not always contain its point estimate: pivoting moves it by twice the
bootstrap displacement, and where the displacement exceeds the half-width
both endpoints land on the same side. The displacement is a **bias that does
not shrink with $n$** --- a resample holds about $1 - e^{-1}$ of the distinct
levels however many rows it has --- while the half-width shrinks like
$n^{-1/2}$, so the ratio grows with $n$: at $K/n = 0.05$ it runs 0.17, 0.31,
0.53, 1.26, 1.76 across $n = 750$ to 120,000. Four of the plane's 33 cells
have no factor for this reason, all at 50,000 rows or more.

**It is not confined to the simulation.** 74 of the corpus's 3,900
whole-surface cells have a band that excludes their own point estimate, on
the three pairs nearest the crossing --- 21% of UCI498/duration's cells.
Section 4.1 reports it, and Section 11 says that the interval construction
was chosen on evidence from one sample size, 4,000, below the regime in which
it develops the defect.

**No region label changed** under the re-estimated plane and the
resolved-cell count moved 892 to 896, so the headline survives a calibration
re-fitted on a plane six times wider in $n$.

## R25.8 Two guards, both earned during the round

The plane's admission rule was a replicate **count** --- at least thirty
usable. Two cells passed it on 34 and 39 **selected** replicates, the ones
whose displacement happened to be small, and returned $c = 3074.7$ and
$c = 0.86$; both would have entered the fit. It is now a **share**, and the
shares are bimodal --- rejected cells reach 0.078 and admitted ones start at
0.976 --- so the threshold decides nothing and the file prints that.

`s36`'s permutation task catches its own exceptions and returns an error row,
so a run with no data under it completes "successfully" and overwrote a good
permutation null with 1,919 error rows. It did, during this round, and the
file came back out of git. A run that produces no usable replicate now
refuses to write.

## R25.9 What this round did not do

**Length.** The five cuts the referees named --- halve S9.1--9.2, compress
S4.4's $p$-versus-interval passage, fold Remarks 1--3 and Corollary 1 into
the text, halve S6.8, consolidate the relative-reduction material --- are all
done, and the summary table of the four reporting objects they asked for
three times is Table 1. They are worth about 170 words against a main text of
23,000, and the article is 70 pages. The body would have to go from 58 pages
to about 32, and every remaining candidate --- the case study, the
limitations, the article's eight tables, Section 6's per-pair detail --- is
something a referee also asked for. That decision is the author's and is not
made here.

**The real Zenodo DOI** is still reserved, and the archived release has not
been confirmed to reproduce the submitted numbers. Both are in
`submission/OWNER-ACTIONS.md` and neither can be done from here.

---

# Round twenty-six — a sixth referee, and two headlines withdrawn

A sixth blind referee returned **major revision** with sixteen major comments,
a section-by-section list, an arithmetic-consistency pass and a seven-phase
revision plan. Like the three before it, the report is right about more than
it claims. Two of this paper's headline findings do not survive it and are
withdrawn; a third turns out to be a wording defect rather than a design
defect; and one of the referee's own arithmetic checks reproduces exactly.

**What this round did not do, and why.** Four of the report's Phase-A items —
A1 the weighted bootstrap, A2 four hundred draws on a designed inference
surface, A6 degradation applied to both halves as a *new run*, A7 a prefix
axis — need the corpus refetched and every arm refitted. That is six to
twenty hours of compute and it is not run here. Section 11 names each as the
change it would make first, in order, and the response letter says so plainly
rather than implying the version submitted has them.

## R26.1 The split axis is an error stratum, and the decomposition's headline reverses. **CONCEDED — the most consequential finding of the round**

Five of the split axis's six levels are expanding-origin folds on the same
data. They are different *samples*, not different analyses, and a functional
ANOVA that pools them reports sampling variability as specification
sensitivity. The referee said the "56.0% higher-order" and "no single axis
dominates" headlines are "inflated by construction". They are, and by more
than the report guessed.

Because the decomposition is exact and orthogonal, the repair is a partition
rather than a model: every component either involves the split or does not.
`scripts/s42_round26.py` computes the four-way partition of equation (7) and
it sums to one to 4.4e-16. **At the median pair the components involving the
split carry 71.7% of the variance**, against 13.3% for the choices an analyst
makes, 4.2% for the register-quality counterfactual and 4.5% for the
components that join them. Resampling is the largest of the four on **17 of
19 pairs**; the two exceptions are the case study's own, which carry the
richest analyst grids in the corpus (4 pipelines and 10 quality conditions
against two and six elsewhere).

Dropping the one split level that *is* an analyst choice — the single
temporal holdout, leaving five folds of one rule — moves the share from
**71.7% to 71.0%**, so the stratum is not an artefact of mixing a rule with
its folds. That check was not asked for; it exists because "the split axis is
resampling" is a claim that could have been an artefact of the axis's
composition, and it is not.

**The headline reverses.** On the fold-averaged surface — 28.3% of the pooled
variance — the higher-order share is **26.3% against the pooled 56.0%**, and
it no longer exceeds the largest first-order index (**38.8%** against the
pooled **28.7%**). Pooled, the interactions carry more than any main effect on
**13 of 19** pairs; net of resampling, on **7 of 19**. *Most of the variance belongs to no single axis*
is a property of a surface that counts five folds as five specifications.
Section 6.2 now reports the fold-averaged decomposition as primary, the
pooled one beside it, and says which claim survives: **which** axis leads is a
property of the pair.

## R26.2 A sign flip between two increments that both round to zero is not a misstatement. **CONCEDED — the sign-disagreement headline is withdrawn**

The referee's objection: the rate counts a disagreement at any magnitude, 8
of 19 reference increments are inside ±0.01 AUC, and the paper's own decision
analysis says the cost of one number is tiny. Every part of that reproduces.
**8 of 19** reference increments are below a hundredth of an AUC point — the
referee computed that from Table 3 and it is exact — and only **5 of 19**
pairs resolve the sign of their own reference cell at all.

A minimal practically important difference of **0.01 AUC** is now declared,
in one place in the code, and applied on the AUC sub-surface because Remark 1
forbids carrying it to another instrument. The rates, all on that
sub-surface: **26.5%** over every admissible AUC cell; **13.2%** once both
increments must clear the MPID; **2.5%** over the cells the band resolves;
**0.5%** over cells that satisfy both. Imposing every restriction the paper's
own §6.4 argument implies — analyst-latitude axes, resolved cells, both
increments above the MPID — leaves **42 cells, of which 1 disagrees**.

**We withdraw the claim that a one-number report misstates a sign at a rate
worth quoting as a headline.** The abstract, the highlights, §6.4 and §12 all
said it and none of them says it now.

Two things emerged from the withdrawal that are worth more than what was
withdrawn. First, **the 7.5% pooled rate is not an AUC statement**: split by
instrument it runs 2.5% on ROC AUC to 11.2% on Nagelkerke $R^2$, which is
Remark 1 showing up in the corpus rather than a claim about specifications.
Second, **the magnitude survives every restriction the rate does not**: over
the cells the band resolves, admissible specifications sit a median 0.0430
AUC from the reference cell, and 0.0534 under the full restriction — four to
five times the MPID. The corrected claim is that a one-number report is
usually right about the sign and usually silent about the size, and that on
14 of 19 pairs the data do not determine the sign of the cell it stands on.

## R26.3 "Is the register degraded in training only?" **NOT CONCEDED — but the manuscript could not have told the referee so**

The referee read §11's "constructed from the training half, not observed" as
saying the degradation is applied to the training half alone, which would
make the increment a train/test mismatch rather than an operational
counterfactual. Reading `spec.degrade` settles it: every mechanism returns a
degraded copy of the **whole column** — both halves — and what is estimated
from the training half alone is the mechanism's *parameters* (which values
are in the long tail, the frequency table a corruption draws from, the
identities a reconciliation failure splits). `spec.assert_train_only`
executes that: it perturbs the test half, re-degrades, and requires the
training half's degraded values to be identical.

So the design is the one the referee wanted and the sentence describing it
was ambiguous in the direction that mattered. §7.3 now states which halves
are degraded, which half the parameters come from, and why the distinction
changes what the increment measures. The both-halves *variant* the referee
asks for is what the paper already runs; there is nothing to add but the
sentence.

## R26.4 The baseline spread is carried by the half-of-intake rung. **CONCEDED**

The abstract's "the baseline alone moves the increment by 0.073 AUC at the
median pair" ranges over a rung that is half an intake block taken in
cardinality order. The referee: that is the same argument used to exclude the
intercept-only rung. It is. **Excluding it too, the median spread is 0.0055
AUC** and it exceeds the reference increment on 7 of 19 pairs rather than 15.

The fall has a plain explanation that makes the smaller number legible rather
than embarrassing: on 17 of 19 pairs only two rungs remain, so the spread over
them **is** the absorption $D$ of the free field, which the paper already
reports as an object with its own interval. Only the case study's log carries
a third, and there the realistic-rung spread is 0.2495. §6.2 reports both
numbers and says which is which; the abstract no longer quotes either as a
headline.

## R26.5 Two headline numbers contradicted each other. **CONCEDED**

Abstract and conclusion said 7.5%; §6.4 said "applying both corrections at
once gives 12.9%, which is the number this section's own argument asks for".
The referee is right that a paper states one headline. R26.2 settles it in a
direction neither number anticipated: with the third restriction the argument
also implies, the answer is 1 cell in 42, and the headline is withdrawn
instead of chosen.

## R26.6 The refit's justification is 1.3 Monte Carlo standard errors. **CONCEDED**

§4.1 justified the nested bootstrap by 93.0% against 92.1% coverage. The
referee measured that gap against the 0.7-point Monte Carlo standard error
§10.2 states and got ~1.3 SE. The macro `nestedGainInSe` now computes it from
the same file as both coverages, prints it in §4.1, and the sentence around
it says the nested construction is retained because the variability it admits
is variability the estimand contains — not because it measures better here.

## R26.7 Five smaller things the referee was right about, each verified

**The design-space declaration.** Definition 1 lists nine axes, Table 2 has
no target row, and the per-pair factorial is five wide. Table 4 (`roles`) is
new, in the main text, and states per pair which attribute plays each role and
how many levels each axis carries. §3.1 and §5.2 now say that the target
*indexes* surfaces rather than being an axis of one, and that the decision
time, operating point and cohort vary on one log only.

**A directional label on two cells of a hundred and eighty.** Definition 3
now requires 5% of the inference family to resolve before any direction is
reported, and Table 7 prints the (beneficial, harmful, unresolved) triple
beside every label. The condition withdraws the direction on **4 of the 13**
pairs that carried one — including BPIC15\_1/duration and UCI498/handover,
the two the referee named.

**Specification regret.** Demoted from a reporting object to a robustness
check, in the contribution list, in §4.7's title and first paragraph, and in
§11. The paper's own results say the rules mostly tie; an object that reports
a null is a check.

**Propositions 1 and 2** are Remarks 1 and 2, about a page shorter, with the
Richness assumption and both constructions moved to Supplement B, and the
three repository file paths gone from the body.

**The UCI Adult coincidence.** The referee asked whether two indices printed
as 25.9% and 25.9% were a copy error. They are not — 25.94% against 25.90% —
and §9.3 now prints the fourth figure so a reader can see that for
themselves rather than being told.

## R26.8 A caption this round wrote was false, and now a gate says so

Figure 1's caption was rewritten to state its own cell count and the product
that gives it, because the referee had to reconstruct that arithmetic from
five numbers in two sections. It reached for `nPipelines` — the **crossed**
factorial of families, encodings and targets, three times the number of
pipeline levels that pair runs — and printed a product that missed its stated
total by a factor of three. Every macro in it was correct and the sentence was
not, which is the failure mode this repository's macro discipline does not
cover.

`scripts/round26_verify.py` now multiplies a caption's stated factors and
compares them with its stated total, checks that the four-way partition's
residual is machine epsilon, and checks that the MPID, resolved and
fully-restricted cell counts are nested. All three were exercised against
injected errors before being accepted. The verifier reports 28 conditions.

## R26.9 What the round added to the main text, and the tension it exposed

Moved in or written new: the roles-and-levels table (was S11), the four-way
partition table, the resolution-triple table, the MPID table, a glossary with
the case study's own value for every term, an overview figure of the method,
and **§7.4, which is now a real subsection** — the field-to-role map for
BPIC14, the three decision times in service-desk terms, the register-layer
result (type 0.134, subtype 0.163, item 0.257 AUC over intake, 0.109 marginal
over subtype), and three named conditions under which the answer would move.

**The report asks for two things that cannot both be had.** C3 asks for six
more tables and figures in the main text; C6 asks for a target of ~30 pages.
The article was 48 pages before this round and is 59 after, of which the body
is 49. Everything added is something the report asked for. The response letter
puts the arithmetic in front of the editor with a list of what can move back
out, because which of the two the journal wants is a decision for the editor
and not for the author.

## R26.10 What this round did not do

**The four refitting items** — A1 weighted bootstrap, A2 400 draws on a
designed inference surface, A6 a both-halves *re-run*, A7 a prefix axis. A1
and A2 are the ones that would let the paper keep the word
"coverage-calibrated" in a headline; until they are run, §11 says the bands
are descriptive diagnostics and the front matter no longer claims otherwise.

**The affiliation.** The Guide for Authors wants a city and a country and the
referee found neither. They are not derivable from any file in this
repository, so `round26_numbers.AFFILIATION_CITY` and `_COUNTRY` are `None`
and the title block prints the visible `??` marker — the same marker a
missing result gets. The build is otherwise green; this is the only
unresolved macro, and it is one line to fix. See
`submission/OWNER-ACTIONS.md`.

**The DOI**, still, and for the same reason as in round twenty-five.

## R26.11 Reading the rendered pages, after the round was "done"

Every gate was green and the round was written up when the sixty rendered
pages were read end to end. Nine more defects, four of them false statements.
The count is the point: this is the twenty-sixth pass over this manuscript,
and a section rewritten in the same session still carried four claims that
were wrong.

**Two macros for one idea, differing.** Round twenty-six recomputed the pooled
decomposition's medians in order to compare them with the fold-averaged ones,
and grouped over a cell set that includes `ALL_SCALAR` --- the demoted
cross-instrument headroom scale. The manuscript then carried **28.7% and 29.1%
for "the pooled largest first-order index at the median pair"**, and **56.0%
and 52.5% for the pooled higher-order share**, four sections apart, with the
archive's own description quoting the second of each. The registry that exists
for exactly this (`round21_verify.ESTIMANDS`) had no entry for them; it does
now, and the negative test was run. On the canonical basis the count of pairs
where the interactions exceed the largest main effect is **13 of 19, not 16**,
which is what the log and the letter said an hour earlier.

**The Figure 1 macro bug, twice more.** `\nPipelines` is the *crossed*
factorial --- families $\times$ encodings $\times$ targets, twelve --- and the
case study's pipeline axis runs four levels. Having found and fixed that in
Figure 1's caption, the round had used the same wrong macro in two further
sentences of section 6.2, including one that contrasts the case study's grid
with the rest of the corpus. The macro is now named `nPipelineLevelsCase`,
which is not a name anybody reaches for by accident.

**Round twenty-four's defect, recurred.** Section 6.4 opened with "Two things
are wrong with reading that as what a one-number report exposes a reader to,
and both are corrected" --- while the section now makes **three** corrections,
because this round added the MPID. Round twenty-four's minor 4 was that this
section names its own defects and corrects them one at a time; adding a third
and not updating the count reproduced it.

**A layer claim that was false.** Section 7.4 said that on the duration target
"the coarse layers are nearly free". They are not: the item's type is worth
\layerTypeDuration\ against the item's own \layerItemDuration, which is about
a third, not nothing. The sentence now says a third, and the contrast with
handover --- where the type reaches about half --- is stated as the result it
is: **which layer pays is a property of the target, not of the register.**

**Five more, each a contradiction with the round's own decision.** Table 1's
caption still called regret one of "the four reporting objects this paper
supplies" two pages after the contribution list demoted it, and so did section
4.5, section 10.4 and the supplement's abstract. The contribution paragraph
cited section 6.4 for the regret results, which are in 6.6. Section 9.3's
correction of the UCI Adult coincidence --- claimed in the response letter ---
had silently not applied, because the replacement did not match the source and
nothing re-read it. Section 12 said "1 of 42 admissible cells" without the AUC
denominator, in a paper whose subject is denominator discipline. And section
3.3's claim that the sign disagrees across cells needed restating once the
disagreement *rate* was withdrawn: it now leads with the point-estimate fact
that survives every restriction --- on \nSignVaries\ of \nPairs\ pairs,
between a tenth and nine tenths of admissible cells are positive.

**What this says about the length argument.** The referee asks for the body at
about thirty pages and for six more objects moved into it. The body is
forty-nine. Everything this round added is something the report asked for, and
the cuts the report sanctioned --- section 4.3, section 4.4, the propositions,
the tie-break paragraph, the threats section --- were taken. The rest is a
decision about what an *Information Systems* reader should be able to check
without a second document, and `submission/response_to_review26.md` puts it to
the editor with a ranked list of what can move back out.

---

# Round twenty-seven — a seventh referee, and the repair the paper had priced and not run

A seventh review, of the round-twenty-six PDF, returned **major revision
(narrow)**. Its judgement is that the paper's candour and presentation are no
longer what blocks it, and that its remaining problem is *delivery*:

> A methods paper whose subject is inference discipline cannot ship its
> central inferential object as a diagnostic when its own text prices the fix
> at one function.

That is the correct reading of Section 11 and it is conceded without
argument. The round runs the repair.

## R27.0 Three findings were already repaired before the report was written

The reviewed PDF was built at commit `d854e9d` and six commits of
round-twenty-seven work land after it. Two of the report's three
inconsistencies — the master table printing region labels Definition 3
withdraws, and "that pair carries" quoting the log's cell count — were
repaired in `a03b560`, together with three more of the same class the report
did not find. **DISMISSED as already-closed**, with the commit named, and
recorded here rather than claimed as new work in the response letter.

The class matters more than the instances: *a macro is right, a table is
right, and the pair contradicts*. Six of them in one manuscript says the
class needed a gate and not a proofread. It has one — `round27_verify.py`,
six conditions, each exercised against the exact defect it replaces.

## R27.1 The band is delivered as a diagnostic while the repair sits unrun. **CONCEDED — the round's central item**

Round twenty-five measured the band's family-wise coverage at a median 84.6%
against a nominal 95% and named the repair; round twenty-six reported the
measurement honestly and did not run it. The referee is right that honesty is
not a substitute, and right that our own cost estimate defeats the cost
excuse.

**Disposition.** `s44_designed.py` runs both resampling schemes over one
balanced design at 400 draws: weights per moving block, so every register
level is present in every refit and the displacement disappears at source
rather than being pivoted around. The design is a full factorial on every
pair — 2 learners x 2 splits x 3 quality conditions x 3 rungs, 180 scalar
members — which is strictly stronger than the resolution-IV fraction
Section 11 asked for, and it retires the "corner, not a design" limitation:
the decomposition can now be computed on the inference surface too.

The success criterion is the count of cells whose pivotal interval excludes
its own point estimate, 74 of 3,900 in round twenty-five, because it is a
defect a reader can see without believing any theory about why it happens.

## R27.2 The decision-curve widening is measured and never applied. **CONCEDED**

Section 10.4 measures that the decision-curve families need a multiplicative
widening of 1.90 to 2.05; Section 8.3 printed counts from the uncorrected
band; Section 11 told the reader to distrust them. Unlike R27.1 this had no
cost defence at all — widening an already-computed critical value is matrix
arithmetic on existing draws. `s49_dcaband.py` applies it and reprints every
count that rests on it, with the uncorrected column beside it as the scalar
family's table already does.

## R27.3 The inference share is quoted against a denominator it was not computed on. **CONCEDED — a seventh instance of R27.0's class**

`inferenceShareMedianPct` was computed as observed inference cells over
*computational* cells — a denominator including the intercept-only rung — and
used at four call sites, three of which say *admissible*, which by the
paper's own definition excludes that rung. One macro, two denominators, so at
least one site was wrong wherever they differed.

**Disposition.** Two macros, each derived from the axis declaration; the call
sites matched to the denominator their sentence names; and a sweep in
`round27_verify.py` that recomputes every per-pair and per-surface count and
share from the axis declaration, so the eighth instance fails the build
instead of reaching a referee.

## R27.4 The reproduction claim is not true on another machine. **CONCEDED — found by us, not by the referee**

Not in the report. Recorded here because it would have been in the next one.
The boosting learner does not reproduce this repository's committed results
across machines at identical pinned dependency versions, up to 0.14 in
Nagelkerke on Sepsis, while the logistic learner reproduces to 5e-10. No gate
caught it, because `verify_release.py` re-derives macros from committed
result files and never re-runs an analysis — a checker that cannot see the
thing it certifies, which is this project's rule 5 exactly.

## R27.5 Two smaller items, both conceded

**The generative-AI declaration** is trimmed to Elsevier's template plus the
facts that belong with it. Trimming it exposed an overclaim: the assertion
that no generative model produced any datum, result or citation was
*unscoped*, and was true only because the pilot carve-out followed it. The
supplement does report prevalence estimates from machine-assisted
adjudications. Scoped to "behind a claim of this paper" in the article and in
`credit_statement.md`. **This is rule 2 landing again** — the trim looked
like pure subtraction and was not.

**The keyword "predictive process monitoring"** is retired for "event logs".
Section 11 states that prefix length, bucketing and sequence encoding are not
axes of this design space and cannot be; the prefix pilot says of itself that
it does not make this a predictive-process-monitoring paper. A keyword is a
claim of topical membership and the body disclaims it.

## R27.6 An internal adversarial pass found eighteen more, eight of them blocking. **CONCEDED, every one**

After the seventh referee's report was answered, the same class of defect it
named — *a macro is right, a table is right, and the pair contradicts* — was
hunted deliberately rather than waited for. Eighteen findings, none of them
previously known, in sections no referee has yet complained about.

The eight blocking ones, because a paper about denominator discipline cannot
have these and be believed:

1. **The subset relation between the two cohorts is stated backwards.** The
   registered cohort is 46,606 and the estate's is 45,455, and Section 7 said
   the first was a strict subset of the second. Its own next clause proves the
   opposite: the 1,151 extra cases are the ones *the estate* excludes.
2. **A table caption asserted the conclusion the body withdrew**, and the
   table's own rows refute it: under the concentrated measure the largest
   first-order index is 0.392 against a higher-order remainder of 0.317, and
   the caption said no first-order index approaches the remainder.
3. **The resolution denominator was the admissible surface, not the
   inference family** — "197 of 5,808 AUC cells", where 5,028 of those cells
   carry no draws at all and so are neither resolved nor unresolved. The
   honest figure is 197 of 780. The error understates the corpus's resolution
   by a factor of seven, in the sentence whose purpose is to say the data
   resolve little, and forty lines away the same section uses the correct
   denominator for the same notion.
4. **The specification-curve table printed region labels Definition 3
   retracts** — the identical defect repaired in the master table a week
   earlier, left standing in a second table, which now disagreed with the
   first about the same four pairs.
5. **The supplement asserted one conditionally harmful surface exists** while
   the article's master table shows none: 9/3/1/6 against the post-minimum-
   share 6/3/0/10.
6. **"Uniformly beneficial" was restated over the admissible surface** rather
   than over the inference family the definition uses — on the one label the
   paper had already identified as the most flattered by that substitution.
7. **"The two largest logs carry two pipelines"** where both tables say three,
   and where the declared cell count of 1,620 depends on the three.
8. **"The other 15 pairs"**, where two plus fifteen is not nineteen: the macro
   counted pairs with at most two pipeline levels rather than the pairs the
   sentence names, understating a limitation by two pairs.

Ten further findings are serious: a per-pair count true only of the modal
pair and used as a headline denominator; a directional claim ("that range is
carried by the half-of-intake rung") true at the median and false at the
maximum the same sentence quotes; an interaction called "as large as either
main effect" while being strictly smaller than one of them; the crossed
decomposition quoting an aggregation the section itself insists must be named;
the calibration's *applied* range quoted from the simulation plane rather than
from the corpus; a register cardinality attributed to the wrong cohort in two
places; the layer ladder labelled with the target Section 7.1 exists to prove
it is not; an accounting that omits the one pair resolving only harmful cells
and then misclassifies it; and a rate whose denominator counts sign-changing
pairs among "pairs that carry a direction".

**One finding is worse than the rest and is recorded separately.** The
paper's advertised *first* auditability check — "multiplying Table 3's level
counts gives the cell counts of Section 6, and that multiplication is the
first check the verification harness runs" — **does not work.** Three of the
nine rows break the product: encoding is already fused into the learner row,
the decision time is not a factor of any surface, and the baseline appears
twice. The naive product for a modal pair is 267,840 against a declared 1,080.
A reader following the paper's own instruction to check its denominator gets a
number six times too large. That is not a typo; it is the one check the
manuscript invites the reader to run.

**What the pass also established.** Verified clean, and recorded so a later
round does not re-check: the whole denominator table multiplies exactly, cell
for cell, to 29,040 and 273,024; the master, triple and calibrated-band tables
reconcile on all nineteen rows for every resolved share and every rho; the
decomposition tables reproduce all four corpus medians and the higher-order
interval; the decision-time ladder's six increments, intervals and ordinals
are right; and roughly thirty further identities hold to the printed
precision. The defects are concentrated in *prose that describes* tables, not
in the tables.

## R27.7 The reproduction claim was false across machines, and the record of it was wrong twice. **CONCEDED — found by us**

`ROUND27-STATE.md` had recorded that the boosting learner does not reproduce
this repository's committed results on another machine, that the logistic
learner reproduces to 5e-10, and that the divergence reaches 0.14. Round
twenty-seven diagnosed it properly and **both of those numbers were wrong in
the direction that flatters nobody.**

**It is the machine, not the threading, and not the library.** Four candidate
causes were eliminated by measurement rather than by argument: thread count
(pinned to one against four — bit-identical), library version (the pinned
set against a newer one — bit-identical), source drift (the analysis module
at the commit that wrote the surface against the current one — bit-identical),
and run-to-run nondeterminism (exactly deterministic). What is left is the
processor architecture: the committed surface was produced on x86-64 and the
re-run on arm64. Thread pinning does not fix it because the pins were already
there.

**The mechanism is amplification, and it was measured.** A one-unit-in-the-
last-place nudge to the boosting encoding matrix — a relative 2.2e-16 — moves
a predicted probability by 0.37 and Nagelkerke by 0.038. The logistic learner
is not chaotic at all; its probabilities agree to 1.4e-15. But a
rank-based metric is a step function, and a high-cardinality register ties
test rows to equal predictions that a difference in the last bit unties.

**Two corrections to the record.** "The logistic learner reproduces to 5e-10"
is **false** — it diverges by up to 0.094 in Nagelkerke, 0.039 in AUC and
0.128 in net benefit. The 5e-10 held only on the cells the earlier check
happened to look at. And "up to 0.14" is **0.851**. The right
characterisation is not a learner at all: **the divergence tracks the
register's cardinality**, and the low-cardinality rungs of both families
reproduce to 2.3e-12.

**Disposition.** `REPRODUCE.md` gains a section measuring the divergence with
six documented tolerances; the code-availability statement now claims
bit-exactness inside the container and states plainly what holds outside it,
with the distinction a reader needs — checking a *digit* requires the
container, checking a *conclusion* does not. Two new scripts execute the
claim rather than asserting it: a gate that re-runs part of the surface
against the documented tolerances, and its own corruption suite, which caught
a labelling bug in the gate before the gate was trusted.

**And a second undeclared tie order, found on the way.** The register-quality
mechanisms cut a cumulative-count curve *inside* a group of tied identities,
and the corruption mechanism maps its draws onto the same tie-ordered index —
so which identities a degradation removes rests on a sort nothing pins. This
is the second instance of the defect Section 7.1 reports about the split sort,
which is why the reporting standard's tie-break item is now stated over
**every** sort a procedure cuts on. It is recorded rather than repaired:
repairing it moves every number on the quality axis and belongs with the run
that regenerates them.

## R27.8 The run was made, and both repairs it was made for failed. **MEASURED**

Round twenty-seven's purpose was to run the two changes Section 11 named as the
first to make. Both ran. Neither did what it was named for, and that is the
round's result.

**Level loss does not explain the displacement.** The multinomial resample
holds about $1-e^{-1}$ of a high-cardinality register's levels, and that was
offered as the reason the bootstrap distribution is displaced. Weights remove
the mechanism completely --- the share of levels present in a draw goes from
80.8 per cent, 60.2 at worst, to 100 by construction --- and the displacement's
median moves only from 0.0050 to 0.0041. A mechanism removed entirely leaves
its supposed consequence standing, so it was not the cause, and this paper does
not know what is.

**More draws do not fix the coverage.** Round twenty-five wrote that the
binding constraint on family-wise coverage was the draw count. On families
matched to the surface this paper now reports, coverage is 91.2 per cent at 150
draws, 91.6 at 400 and 91.3 at 1,000: it plateaus, and the spread across those
three sits inside one Monte Carlo standard error while the rise from 33 draws
does not. The corpus runs at 400 throughout, on the plateau, and the band still
covers a median 83.7 per cent under this corpus's tails against a nominal 95.

**Consequences, stated rather than softened.** Region labels and rho remain
descriptive diagnostics. The abstract's "find short of nominal" stands. The K/n
calibration is not retired but under-sized --- the widening these families need
is 1.36 to 1.88 against the 1.18 to 1.77 it supplies --- so it is not applied,
and the manuscript says the labels are anti-conservative by an amount it has
measured and cannot remove.

**What the round did buy.** Level coverage 80.8 to 100 per cent. Cells that
could not be given a band at all: 150 to 0 --- a category this paper had never
reported, because a cell with no band is not resolved and was therefore counted
as UNRESOLVED, putting cells the data were never given a chance to resolve
inside the denominator of every statement about how little the data resolve.
The excludes-own-estimate rate from 3.9 to 1.3 per cent. A balanced full
factorial, checked cell by cell, that retires the corner-not-a-design
concession and makes the decomposition computable on the inference surface.
And one surface that reaches rho = 1, which answers a question Section 4.6
poses and that this corpus had only ever answered with "never" --- over a
family that is 3.75 per cent of that pair's admissible cells, which is the part
of the answer that matters.

## R27.9 Five adversarial passes, and the last three audited this round's own work

Three passes audited the manuscript and two audited the repairs. The second
pair found 8 and 15 defects respectively, every one of them created by a fix
made hours earlier. Two root causes, both worth recording because they are
general:

**A check that reads a fixed filename cannot notice that the analysis moved.**
Five separate places went on reading the previous inference surface after it
was replaced: two macro generators, the coverage matcher, the region figure,
and --- the one that stings --- the verifiers themselves, which then failed on
eleven macros by disagreeing with the files they were supposed to check. A
sixth layer, the resolved-cell statistics behind the abstract, was found only
by checking the abstract's numbers by hand.

**A rewritten passage deletes its own statement of a claim and not the pointers
elsewhere that restate it.** Fifteen instances, of which two were worse than
the rest: a section citing, as its supporting authority, an appendix that
asserted the opposite; and a printed table whose caption told the reader its
labels were not the ones the article quotes, when by then they were.

The defence added is a condition that fails on a HALF-MIGRATED tree --- cell
counts from one surface, region labels from another --- because that state
passes every other gate: both files are internally consistent, every number
resolves, and the manuscript reports a family size no label was computed over.

## R27.10 A sixth pass, on the repairs made after the fifth. **EIGHTEEN FINDINGS**

The fifth pass repaired fifteen contradictions. The sixth audited those
repairs and found eighteen more, of which nine were blocking. The pattern did
not change, and by now it is the round's real subject: **a repair applied at
one site is a repair applied at one site**.

**Four printed tables carried the retired surface under captions saying they
carried the reported one.** The master table --- the one a referee quotes ---
printed a robustness index taken from the previous surface's CALIBRATED
column: one row showed a resolved share of a hundred per cent with no harmful
cells beside a rho of 0.096, which its own neighbouring columns force to be
1.000. The specification-curve table had the same defect from a different
file, the family table from a third, and the comparison table printed a
widening column of ones beside two pairs of identical columns, under a caption
promising the reader the size of a correction.

**A number set to one to mean "nothing is applied" emptied the argument that
says why.** The factor's supplied range became 1.00 to 1.00, and three
sentences asking what the calibration WOULD supply rendered "1.00 to 1.00" ---
one of them concluding that this range lies ABOVE the 1.36 to 1.88 the
measurement asks for, and calling it conservative. Whether a factor is applied
is a fact about the manuscript; what it supplies is a measurement. Conflating
them cost the paper its own central caveat, in the direction that flatters.

**A coverage was quoted for a design the corpus does not run.** The headline
83.7 per cent pooled decision-curve families with surface ones --- two sets
whose shortfalls this paper reports separately, precisely because they are not
the same object --- across draw counts from 33 to 1000 and family sizes from
120 to 2966, while every reported pair carries 180 cells at 400 draws. The
family matched to the reported design covers 91.6 per cent, and the table of
"families matched to this corpus" did not contain it. THE CORRECTION RAISES
THE NUMBER, which is why it is reported with its Monte Carlo standard error
and its neighbours: 91.6 against a nominal 95 is short by more than five of
them, so the paper's sharpest limitation stands, on a number that is now the
right one.

**A list of labels could not notice a label nobody had written down.** The set
of regions "that carry a direction" was a hard-coded pair of conditional
labels, correct until a pair attained UNIFORMLY BENEFICIAL --- which names a
sign too. The denominator was eleven and should have been twelve, and an
enumeration of the corpus printed four labels summing to eighteen over
nineteen pairs. The missing pair was the one the round turns on. The rule is
now a membership test, and any list claiming to partition the corpus is
checked by adding it up.

**And a build command that is not installed reports nothing at all.** Several
rebuilds during this pass invoked a tool absent from the environment; the
shell said only "command not found", the page count was then read from a PDF
five hours stale, and a spliced line that had eaten the clause closing a bold
run went unnoticed through four commits --- while the article did not compile.
`check_package`'s rule that a PDF older than its source is a stale document is
what caught it. THE GATE THAT MATTERED WAS THE ONE COMPARING TWO TIMESTAMPS,
not any of the ones reading the document.

## R27.11 The recurring defect becomes a gate, and the gate finds two more

Fourteen times this round, in fourteen files, the same defect: **a check that
reads a fixed filename cannot notice that the analysis moved.** Every instance
was caught by a reader noticing an impossible number in a table. None was
caught by a gate, because no gate asked the question that generalises --- does
any generator still name the old surface?

`scripts/check_sources.py` asks it. It scans every generator for a read of a
retired surface's bands, cells, regions, critical values or incomplete
families, and fails unless the line carries `# retired-ok: <reason>`. The
reason is required: a bare marker is how a gate gets switched off one line at
a time. It is scoped to the SURFACE-SHAPED files rather than to the prefix,
because `s17_facts` holds a diagnostic nothing later recomputes while
`s17_bands` is a superseded band, and a gate that cannot tell them apart is
one people learn to skip.

Run for the first time it found **two live defects nobody had looked for**.
The count of pairs carrying a negative cell was computed on the retired
surface, where every pair has one; on the reported surface two do not, so the
macro said nineteen and the answer is seventeen. And the cell-for-cell
identity check --- whose own comment calls it "the only version that would
have caught it" --- was running against the surface the article no longer
reports. **A verifier checking a retired object is worse than no verifier,
because it reports success.** Both are repaired, and the identity check now
passes against the reported surface, which is the first time that has actually
been established.

## R27.12 The length pass, what it yielded, and the two things it found instead

Two independent analyses measured the whole body against one rule --- **a cut
that removes a number is a saving; a cut that removes a concession is a
regression** --- and both returned the same verdict: the 46-page target is not
reachable from 66 without breaking it.

**What was taken.** The reporting standard moved to the supplement entire,
with the prescription kept in the body as a paragraph, because the standard is
the contribution and the recipe, the package and the worked example are the
apparatus. The case study's two side experiments; four detail blocks in
Section 6; the design rule's full statement; two constructions the supplement
already carried verbatim; and ten passages that restated a number where it was
not computed. **66 pages to 62, and 22,100 body words to 19,900.**

**Why the rest is not available, stated as arithmetic rather than as
reluctance.** About a quarter of body prose is protected outright. **All
eleven floats are protected by the referee's own earlier report**, which asked
for six more floats moved IN --- the four-way partition table, the resolution
triple, the MPID table and the overview figure were each moved in or written
new to answer it. Eleven floats are 6.6 of 53 body pages and none is
available. Reaching 38 body pages therefore means cutting 43 per cent of
everything not protected, from sections that have had material moved out in
four consecutive rounds --- which is the density at which this log's own
evidence says a rewrite starts manufacturing defects faster than it removes
pages.

**One saving deliberately refused.** Section 6.5 runs specification-curve
analysis unchanged against this paper's region labels and reports where the
two part company. It is the largest single saving left and it is also the only
head-to-head with the closest existing practice. A page count is recoverable;
a reader asking where the comparison went is not.

**And the pass found two defects that had nothing to do with length.** The
first: `app_corrections.tex` and `app_pilot.tex` were reachable only from a
file no built document includes, so **the correction register was in neither
PDF** --- while the article's front matter, the supplement's own abstract and
the archive description each promised it by name. A promise a referee can
check in one click had been broken for at least a round. The second: the
article's overview figure was referenced by nothing, which is the kind of
thing a copy-editor returns a manuscript for.

Both are now fixed, and the supplement carries the register it advertises.

## R27.13 The two "owner-only" items were not entirely owner-only

Both blocking items were recorded as needing the depositing account. One of
them did not, and the distinction is worth stating because it is the same
mistake as reading a fixed filename: **an item was classified by its hardest
half.**

**The container was pinned by a mutable tag while the paper claimed
bit-exactness inside it.** `Dockerfile` read
`FROM python:3.10.0-slim-bullseye` --- a tag, so the same file would build a
different image after any upstream rebuild, and the code-availability
statement's promise had nothing fixed to attach to. Minting the digest of a
BUILT image needs the deposit; **resolving the base to a digest does not**. It
is a public read. The base is now pinned by the multi-architecture manifest
list, so a build still selects the host's platform while the content is fixed,
and the digest was verified rather than trusted: fetching the manifest BY that
digest returns bytes that hash to exactly it.

The manuscript's sentence now reads the digest OUT OF the `Dockerfile` rather
than carrying a typed copy, and `round27_verify` condition 20 fails the build
if the two disagree --- proved by zeroing the digest and watching it fail. So
an edit to the container cannot silently falsify the paper, which is the
property the original claim never had.

**And the DOI's worst symptom was not the missing DOI.** Reference [11] read
"the archived release cited in the data-availability statement (DOI reserved,
inserted at proof)", and that statement carried the same macro --- so a desk
check following the reference arrived back where it started. A reference list
that loops is a likelier cause of a desk return than one that is candidly
incomplete. The entry now carries its own resolvable URL and states the DOI's
status in one clause. The DOI remains the owner's to mint; the loop was not.

`REPRODUCE.md` still described the tag pinning three paragraphs after it
stopped being true, and the response letter still listed both items as
unsupportable claims. Both corrected. **A repair is not finished until every
document that described the defect stops describing it** --- which is this
round's oldest lesson, arriving for the last time.

## R27.14 The submission package pointed at the wrong documents

Three defects in the instructions the owner would follow, none of them in the
manuscript, all of them capable of shipping the wrong package.

**The upload list omitted the letter that answers the current report.** Both
`submission/README.md` and `OWNER-ACTIONS.md` §1.4 listed responses up to the
second developmental review, and the README told the owner to upload
`response_to_blueprint.md` "if the system takes a single response document"
--- a letter four reviews old. Three further letters had been written since
and none was listed. Following the instructions would have submitted this
version with a reply to a report it does not answer. All six are now listed,
the round-27 letter first and marked as the one to upload, and the package
check went from 15 entries to 19 --- the four it had never been watching.

**The DOI instructions told the owner to tag `v27.0` and then to draft the
release from `v25.0`.** Two steps apart, in a numbered list whose whole
purpose is to be followed literally. The tag message named round twenty-six.

**And the branch item named `round25-coverage`**, which the work left two
rounds ago; it is on `round27-inference`.

The pattern is the round's own: **a document that describes a state is a claim
about that state, and it goes stale exactly like a number does.** These three
had no macro behind them and no gate watching them, which is why they survived
while every number in the manuscript was re-derived from its source. The
package manifest now covers the response letters, so at least that class
cannot recur silently.

Separately: `verify_release.py` passes --- a checkout carrying only what is
committed regenerates every macro and all 58 generated tables byte for byte
and builds both documents without any file under `data/`.

## R27.15 The cover letter told the editor the opposite of what the paper says

The document an editor reads first said this:

> "every region label and every robustness index in the article is the
> calibrated one, with the nominal one printed beside it so the size of the
> correction is visible."

The article applies no calibration. It derives one, measures that the widening
these families need is larger than it supplies, and reports nominal labels
while saying by how much they are anti-conservative --- which is the paper's
central caveat and the thing three rounds of review pushed hardest on. The
cover letter asserted its negation, in the first two pages, under a bullet
summarising the contribution.

It also said the article is 58 pages with 7 tables and five figures. It is 62
with 8 and 3.

**Why this survived every gate.** `verify_numbers` re-derives macros;
`texlint` forbids numeric literals in the manuscript's prose; `check_sources`
watches the generators. **Nothing was watching the submission package's
prose**, which contains typed numbers and typed claims by design, because it
is not built from `numbers.tex`. The manuscript could not have carried this
contradiction --- there is one of each number and a condition tying the
calibration's direction to the measurement --- and the letter carried it for
as long as it took someone to read it.

Moving Section 9 to the supplement then renumbered five sections, and both
letters went on naming the old ones; eight references to "Section 11" meant
the threats section, which is now Section 10, and one pointed at a subsection
that had left the article entirely. Corrected, and `check_response_refs`
validates the section references --- which is why that half was caught by a
gate and the calibration half was not.

## R27.16 A second gate, for the class the cover letter carried

`check_claims.py` fails if a document that speaks for the CURRENT version
still asserts a phrasing the project has withdrawn. Five are declared, each
with the reason and the round that retired it, so adding a withdrawal is one
entry rather than a memory.

Two design decisions are worth recording because both were made after the
first run reported six hits and only one was real.

**A claim inside quotation marks is reported, not asserted.** Every letter
that explains a withdrawal quotes the sentence it withdrew --- the round-27
response letter quotes the old reference text in the paragraph explaining why
it changed --- so quoted spans are blanked before matching. Without that the
gate fires hardest on the documents doing exactly the right thing.

**Two of round twenty-six's withdrawals were deliberately left out.** "The
sign-disagreement rate" is the NAME OF A QUANTITY the paper still computes and
still prints in a table; what was withdrawn is its use as a headline, which is
a fact about prominence and not about wording. "Most of the variance belongs
to no single axis" appears inside the very sentences that withdraw it. A
pattern firing on both a claim and its retraction reports noise, and **a noisy
gate is one people learn to skip** --- which would cost more than the two rules
are worth. Only claims a regex can separate from their denial belong in the
list; the rest are held by the manuscript's prose and by R26 above.

It was proved by reinstating the cover letter's withdrawn sentence and
watching it fail on the exact line.

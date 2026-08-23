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

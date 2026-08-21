# Referee log, round seventeen

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

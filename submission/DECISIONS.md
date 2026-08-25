> **SUPERSEDED IN ITS PARTICULARS — round sixteen.** This file records four
> decisions taken three rounds before the manuscript being submitted, and its
> section numbers, its title and several of its numbers belong to a document
> that no longer exists: the title settled in decision 1 was replaced in round
> nineteen, and the headline it defends was withdrawn as inflated by an
> intercept-only baseline. It is kept, and shipped, because the *reasoning* is
> still the reasoning — each decision says what was chosen, what was rejected,
> and what would overturn it — and because a decision recorded and later
> reversed is more useful to a reader than a decision never written down.
> The current record is `response_to_blueprint.md` and `../REFEREE-LOG.md`.

# Decisions taken in round sixteen, and why

The plan (`PLAN-INFORMATION-SYSTEMS.md`, §9) left four decisions open. Three
of them had to be settled for the manuscript to build. Each is recorded here
with its reasoning so it can be overturned cheaply rather than
re-litigated.

---

## 1. Title — settled

**Chosen:** *Identity, Not Attributes: What Configuration Data Contributes to
Incident Prediction in Two Organisations* (option 2 in the plan's §5).

**Why.** The plan's own §2 promotes "identity, not attributes" to the lead
contribution and demotes the admissibility effect to the mechanism that
explains it. A title should name the lead contribution. Option 1 —
*Which Layer of Configuration Data Pays? Attribute Admissibility and Measured
Feature Value…* — names both, at 23 words, and leads with a question whose
answer the subtitle then gives away. Option 3 leads with admissibility, which
is the axis four referees scored as the weak one.

**Constraint the choice had to satisfy.** `verify_paper.py` asserts that the
title names the paper's subject and does **not** assert a magnitude the body
ranges over — the previous title said "Nearly in Half" about a quantity the
paper reports as 36.1%–48.3%. Option 2 satisfies both.

**To overturn:** edit `\title{}` and re-run the verifier.

---

## 2. Acknowledgement — settled provisionally, needs the author

**Chosen:** the manuscript describes the later review rounds as
machine-assisted, and says the author set every research question and
adjudicated every correction.

**Why.** The repository records rounds eleven to eighteen as agent-run
adversarial review and contains no practitioner's name. Crediting a
practitioner who cannot be identified from the record would be an assertion
of exactly the kind Section 10 of the paper is about.

**This is the one decision I could get wrong in the direction that matters.**
If a real person did review this work, the credit was removed in error. See
`OWNER-ACTIONS.md` §5.2.

---

## 3. Repository URL — decided, not executed

**Chosen:** `cmdb-field-admission`, as the plan proposed. The manuscript
already prints it.

**Not executed** because the repository does not exist yet and creating or
renaming one is an outward-facing action needing the author's GitHub
credentials. `OWNER-ACTIONS.md` §1 has the two commands.

---

## 4. The reproducibility track — recommended, not binding

**Recommendation:** accept if invited. It is a second publication from the
same work and the artifact was built for that review.

---

# Decisions the plan did not anticipate

Two of the six Phase 1 analyses came back against the paper. The plan's own
rule — *"if a result contradicts the paper, the paper changes. Five of the
last six corrections flattered the result; assume the next one will too"* —
settled what to do, but the size of the change is worth recording.

## 5. The operational factor of 4.3 is withdrawn

**What happened.** Plan item 1.4 asked for a tie-free naive baseline, to kill
the objection that the 4.3× factor is rank resolution rather than
information. It did not kill it; it confirmed it, twice over.

- The repair is impossible. The four intake fields take **23** distinct
  combinations, so no function of them can rank 13,637 incidents into more
  than 23 classes. Cross-fitted target encoding produces **19** distinct
  scores — fewer than the one-hot model's, not more.
- The factor's sign is a tie-break. At 5% capacity **93.1%** of what the
  naive baseline nominates comes from one tied block of 1,944 rows. Ordering
  rows inside that block optimally moves the naive arm from **+271** to
  **−26**; adversarially, to **+608**. Nothing any model knows changes
  between those three numbers.

**And item 1.3 agreed independently.** Decision curve analysis — which never
breaks a tie, because a threshold admits or excludes a whole tied block —
puts the overstatement at **1.07** at the threshold where the item is worth
most, against an AUC ratio of 1.8. The large factors appear only where the
honest increment is crossing zero.

**Consequence.** Section 8 was rebuilt on net benefit; the capacity table was
deleted rather than adapted; the abstract, the conclusion and the corrections
list all name the withdrawal; and the verifier now asserts that the old
table's figures stay out of the paper.

## 6. A band where the configuration item is worth nothing

Net benefit is resolvably **negative** at four grid points between 0.475 and
0.575, reaching **−16.1 [−23.0, −8.9]** per thousand arrivals at
p_t = 0.50. At a one-for-one exchange rate, adding item identity to a
group-aware model makes the desk worse off on this task.

This was not in the plan and no earlier round had looked. It is reported in
Section 8 and again in the Limitations. The only mechanism offered is the
obvious one — a model with 2,554 item indicators can be confidently wrong
where a coarse model abstains — and the paper says that is all it has.

## 7. The corrections list went from six to eight

Item 7 is the withdrawn factor above. Item 8 is plan item 1.5: the
shuffled-item encoder null had been run on the group-aware rung only, while
the reduction it bounds is computed from two rungs, and its boosting residual
is eleven standard errors from zero rather than noise. Run on both rungs the
correction moves the boosting reduction from 47.1% to 50.5% — **upward**,
which makes it the first correction in this project's history that would have
made the result larger had it been noticed earlier. That is worth one
sentence in the paper and it has one.

## 8. Coverage in the checker is now literal-level

Not a paper decision, but it changes what the artifact claims. The one
corruption the suite had never caught appended `confirmed on $10$ independent
extracts` to a checked sentence: a check used to vouch for its whole
400-character window, so any number dropped into a checked neighbourhood was
"covered". A check now vouches for the number it compared and nothing else.
That took the check count from 446 to 674 and the corruption suite from
109 of 110 to 149 of 149.

---
---

# Decisions taken in round seventeen, and why

`PLAN-STRONG-ACCEPT.md` §0.3 says a decision is taken and recorded, never
parked. These are the ones round seventeen took.

---

## 9. Title — changed, and the previous choice is now wrong

**Chosen:** *Four Choices Behind One Number: Reporting the Incremental Value
of a Recorded Field*.

**Why the previous title had to go.** *Identity, Not Attributes* names a
finding that this round showed does not replicate. `r34` tested the four layer
hierarchies `PLAN-STRONG-ACCEPT.md` §4.1 named before any was run. Only the
primary log has a genuine deterministic hierarchy; BPI Challenge 2019's
item/category/vendor levels **cross** — item category determines vendor on
0.00% of items — so it is not a hierarchy and was not treated as one. UCI
498's configuration link is populated on 51 of 24,918 traces. BPI Challenge
2013's product strings carry no separator in any value, so no coarser level
exists and none was invented by clustering. Plan §4.3 says: replicate it on at
least two more logs or demote it out of the lead. It did not, so it is
demoted, and a title may not name a demoted claim.

**Rejected alternatives.**

- *V(f | B, m, θ): Reporting the Incremental Value of a Recorded Field.*
  Names the estimand precisely and is unreadable in a table of contents.
- *A Feature's Value Is Not a Number.* Shorter and more quotable, and it
  asserts a negative the paper spends forty pages qualifying.
- *What a Configuration Register Is Worth, and to Whom.* Keeps the CMDB in the
  title, which is the empirical demonstration rather than the contribution,
  and would misdirect a reader about what the paper is for.

**The constraint the choice had to satisfy.** `verify_paper.py` asserts the
title names the paper's subject and does not assert a magnitude the body
ranges over. It now additionally asserts the title does **not** carry
*Identity, Not Attributes*. To overturn: edit `\title{}` and re-run the
verifier.

**One honest wrinkle.** "Four" is a claim about how many choices are usually
left implicit, not about how many exist. The estimator is a fifth and the
cohort a sixth. §3 says so, because a hostile referee asked
(`REFEREE-LOG.md`, H1) and the alternative was a title that overclaims by one
word.

---

## 10. The generality claim is reported as falsified

**Decision.** `PROTOCOL.md` §8 registered a falsification condition before the
corpus was run. The condition is met. The paper reports the claim as falsified
by its own criterion, in those words, in the abstract, the introduction, §11
and the conclusion.

**Why not soften it.** Pre-registration is worth nothing if the verdict is
renegotiated after the fact. The whole value of §8 is that it was written
before the answer was known.

**What the paper adds beside it, because the hostile pass was right**
(`REFEREE-LOG.md`, H2). On 10 of 19 log-target pairs the entity is not
resolvably worth anything over the intake block, so the reduction has no
denominator and the test had no power. Reporting that as a falsification alone
would conflate *absent* with *untestable*. §11 states both: the registered
claim is falsified by the registered criterion, and a narrower claim — that
where a high-cost entity predicts at all, a free opening stamp absorbs a large
share of it — is neither refuted nor asserted by this corpus.

---

## 11. Eight amendments to a pre-registered protocol, declared rather than hidden

**Decision.** Every amendment is recorded in `PROTOCOL.md` §10 with its date,
its reason and the original text left in place, and both the registered and
the amended selection are reported for every log where they differ.

**Why this is not protocol laundering.** All eight were made after running the
role assignment, which reads attribute names, cardinalities, missing rates and
the split point, and **reads no outcome and no target**;
`r33_generic_ladder.py --roles-only` is that stage and can be re-run to check.
Every one is the registered text failing to implement its own stated intent:
§3.1 says "any timestamp" and the first implementation matched a name list
that missed five; §3.5 gives coarsenings of *f* their own role and the first
implementation left them in the baseline.

**The check that they stop there.** After all eight, the generic rules assign
the primary log exactly the roles the published paper assigns by hand — *f*
the configuration item, *g* the opening group, *B₀* the four intake fields,
and CI Type and CI Subtype as layers — although nothing in the rules names
that log or those fields. That agreement is the closest thing to a validation
the protocol can have and it is why the amendments stop.

**A defect inside amendment 2, recorded because it is the kind that ships.** A
bare integer parses as a date, so the first version of the timestamp test
classified `Impact`, `Urgency` and `Priority` — the published paper's own
intake block — as timestamps and threw them away. Caught by reading the
printed baseline against the paper.

---

## 12. The knowledge reference is admitted, and the headline goes with it

**Decision.** §12 reports that admitting the knowledge-article reference takes
item identity from +0.103 to +0.001 [−0.002, +0.003], and the abstract,
introduction and conclusion carry that figure beside the other two.

**What is claimed and what is not.** The paper claims the field is written by
the service desk and not by the incident process — it is populated on 100% of
the 94,250 interactions that never become an incident, across 1,978 distinct
articles, 99.7% of them resolved on the first call. It does **not** claim the
field is proved available at creation: agreement with a closed record still
cannot discriminate it from the closure code, and §12 says so. What changed is
the balance of evidence, and a paper whose headline is contingent on excluding
a field must report what admitting it does.

**Why the result is believed.** Two nulls, both reported. A matched-mass
random partition of the same cardinality reaches base AUC at most 0.6479 over
five draws and leaves the item worth +0.094 to +0.099; a partition matched
additionally on each cell's distribution over twenty time strata does not
reproduce it either. The real field reaches 0.8041 and leaves the item worth
+0.001. And it is not the item relabelled: 78.8% of articles map to exactly
one item against 80.7% for the opening group, which absorbs less than half of
the item's value rather than all of it.

---

## 13. Detection at a fixed capacity stays in the instrument table

**Decision.** Round sixteen withdrew it as a headline. It is nonetheless a row
in §7's instrument matrix.

**Why.** A matrix of instruments is the right place to show what a
tie-degenerate instrument does to a ratio, and deleting it would leave a
reader unable to see why the withdrawn number was as large as it was. It is
labelled as withdrawn where it appears.

---

## 14. Forty-five pages

**Decision.** The manuscript is 47 pages and nothing was cut to make it
shorter.

**Why.** `PLAN-STRONG-ACCEPT.md` §6.3: *Information Systems* enforces no hard
limit; do not pad, and do not compress out a disclosure to save a page. Every
section added this round carries a measurement. If an editor asks for a cut,
§9's mechanism material and §13's per-axis detail move to supplementary
material without removing a claim, and that is recorded here so the decision
does not have to be re-made under time pressure.

---

## 15. The venue decision, re-taken: *Empirical Software Engineering*

**Decision.** Submit to **Empirical Software Engineering** (Springer).
*Information Systems* — the incumbent since round fifteen — is the first
fallback; *Journal of Systems and Software* is the second.

**Why the decision was re-taken at all.** Round fifteen retargeted the paper
to *Information Systems* when it was a CMDB empirical study. Its centre of
gravity is now evaluation methodology with a CMDB demonstration, a
pre-registered literature audit, three propositions, a prospective test and a
tool. That may not be the same journal's paper, and `PLAN-REVIEWER-PROOF.md`
§8 says an inherited decision is worth less than a re-examined one —
*including when the re-examination changes nothing*. It did not change
nothing.

**The criteria, fixed before comparing** (§8.1), and what each one says:

| # | criterion | verdict |
|---|---|---|
| 1 | publishes evaluation-methodology work with empirical demonstrations | EMSE, TOSEM, JSS yes; IS yes but rarely |
| 2 | a reproducibility or artifact track that engages the paper's strongest asset | EMSE open-science policy and badges; TOSEM ACM badging; JSS badges; **IS has no formal track** |
| 3 | publishes literature audits | EMSE yes, a standing category; JSS and TOSEM yes; IS rare |
| 4 | length allowance | no hard limit at any of the four |
| 5 | median time to first decision | **not machine-collectable; owner action** |
| 6 | accepts single-author unaffiliated submissions **in practice**, counted | see below |

**Criterion 6 is the uncomfortable one and it is measured, not assumed.**
`r48_venue.py` counts, over 3,360 research articles published 2024–2026 in
eight candidate venues: **five are single-author *and* unaffiliated —
0.15%.** In the incumbent, **zero of 275**. In *Empirical Software
Engineering*, zero of 502. The only venue with any at all is *Journal of
Systems and Software*, at 5 of 755 (0.66%). The median paper at every
candidate has four authors.

That does not discriminate between EMSE and the incumbent, because neither has
one. What it does establish is that **the author profile of this submission is
close to unprecedented at every venue considered**, and that fact belongs in
the cover letter and in the Limitations rather than in a hope. It is now in
both.

**What decided it, then.** Criteria 1–3, plus two things the count reached:

- *Empirical Software Engineering* carries **6** papers 2019–2026 whose title
  or abstract says "registered report"; *Information Systems* carries **0**.
  This paper has a pre-registered protocol, a pre-registered audit and a
  pre-registered prediction. Few submissions are better shaped for a venue
  that has actually run that route.
- Its topical share — the fraction of recent articles whose title or abstract
  carries this paper's vocabulary — is **17.3%** against the incumbent's
  **13.5%**.

**And one argument that is about the next paper, stated so it is not
mistaken for evidence about this one.** `HANDOFF.md` §19.8 and §20.10 argue
that the verification apparatus is a stronger contribution than the CMDB
finding and belongs at MSR or EMSE. If that paper follows this one, the two
sit in the same place. That is a convenience, not a reason, and it did not
decide anything on its own.

**Rejected alternatives, with the reason.**

- *Information Systems* (incumbent). Rejected on criteria 2 and 3: no artifact
  track, and audits are rare. Kept as the first fallback because seven
  referees over fifteen rounds scored the technical work 6–8 there and the
  CMDB demonstration reads naturally in it.
- *ACM TOSEM*. Highest topical share (20.8%) and strong on 1–3, but the median
  paper has five authors and the venue's centre is software engineering
  methods rather than measurement practice. Rejected, narrowly.
- *Journal of Systems and Software*. The only venue with any single-author
  unaffiliated papers. Rejected as primary because its audit and methodology
  culture is comparable to EMSE's rather than better and its topical share is
  lower (13.1%); kept as the second fallback for exactly the criterion-6
  reason.
- *Decision Support Systems*, *Information & Management*, *BISE*, *ACM TMIS*.
  Rejected on criterion 1 or 3, and I&M on topical share (3.1%).

**What would change this.** Criterion 5. If EMSE's median time to first
decision is materially worse than the incumbent's, the ordering of the first
two flips. That check is in `OWNER-ACTIONS.md` with the URL, because it is not
in any API.

---

## 16. Forty-two pages of main text, against a target of thirty-six

**Decision.** The main text runs to 42 pages and the whole document to 71.
Nothing further is cut.

**Why.** `PLAN-REVIEWER-PROOF.md` §7.1 sets a target of 36 main-text pages —
and its own per-section table sums to **41**. What landed is 42, one page over
the plan's own arithmetic and six over its headline number. Getting there
moved, without removing a claim:

| moved to an appendix | pages |
|---|---|
| "Which layer of configuration data pays?" (whole section) | ~3 |
| "Where the difference goes" (whole section) | ~4 |
| "Why the instruments disagree" | ~1.5 |
| "Why the capacity framing was withdrawn" | ~2 |
| "The second organisation", and its figure | ~2 |
| "The corpus, and what the rules exclude" | ~1 |
| "Two things the corpus does establish" | ~1 |
| "Net benefit, which needs no capacity" | ~2 |
| the three nulls behind §14's collapse | ~1.5 |

Every one left a pointer in the main text carrying the numbers a reader needs
to follow the argument without turning to the appendix, and every moved number
is still checked: the checker's body now runs to `\end{document}`, which it
did not before this round, and that was itself a hole.

**What was added rather than cut**, and why the count went up before it came
down: the audit (5 pages), the propositions (1.5), the three-log surface (1),
the simulation (2), the registered prediction (1.5), the tool (1.5), the
signature figure (0.5) and a threats-to-validity section the plan's table
allocated and the previous version did not have (2).

**What would go next, recorded so it is not re-decided under time pressure.**
In order: §5's estimator and interval paragraph, §7's "seven instruments"
detail, and §12's per-log narrative. That is about four pages and it would
reach the target. It is not done because each of the three states a
measurement the main text's argument leans on, and the venue has no hard page
limit.

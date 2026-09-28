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

---

# IJF retarget — 2026-09-12

*Information Systems* desk-rejected INFOSYS-D-26-00926 on 2026-09-10 with
no referee comments; the Editor-in-Chief wrote that the paper "should be
sent to a forecasting journal where your treatment of the value of a
feature may give new insight." The manuscript is retargeted to the
*International Journal of Forecasting*. `PLAN-IJF.md` is the plan. Five
decisions were taken with the author before it was written; each is
recorded with what would overturn it.

## 1. Full reframe, not a targeted pass — settled (author, 2026-09-12)

**Chosen:** the register is treated as a *predictor* and its incremental
predictive performance as *incremental forecast value* throughout: title,
abstract, keywords, introduction, related work, section openings and
conclusion, with a vocabulary map applied by script to the body.
**Rejected:** a targeted pass on the front matter only (cheaper; leaves a
body that never says "forecast" for a screen that checks scope); the
minimum the guide forces (highest desk-reject risk).
**What would overturn it:** a rewrite that needed a new claim to read as a
forecasting paper. None is permitted; the rewrite is vocabulary and
framing, audited sentence by sentence against the built PDF.

## 2. Length by relocation, target ≤ 44 pp, aim 40 — settled

**Chosen:** whole subsections move to the supplement behind pointer
paragraphs (§4.7, §5.4, §6.5, §6.6, §7.5, §9.1, the detail of §10); the
blinding removes the two pages of statements.
**Rejected:** keeping 56 pp (IJF tells referees to weigh value against
length); cutting to ~30 pp (real rewriting of the case study and the
simulation, each cut a claim to re-audit).
**Corrected premise:** the plan was first described as moving "in-article
appendices"; there are none — every `app_*` part is already in the
supplement. The relocation is of subsections.
**What would overturn it:** the seven moves leaving the article above
44 pp, in which case the count is recorded and the next candidate named,
not moved.

## 3. Archive stays at v28.0 / 10.5281/zenodo.22557927 — settled (author)

**Chosen:** no new release. Results are byte-identical (`verify_release.py`);
the title page and the cover letter cite v28.0 as the results archive and
say the manuscript source at HEAD post-dates it.
**Rejected:** cutting v29.0 with a new version DOI so the archived source
matches the submitted text.
**What would overturn it:** any result file or number-producing script
changing, which would make v28.0 no longer the archive of these numbers.

**Status 2026-09-19 — the overturn condition is met.** No analysis result
changed, but three number-producing generators did (corrections C32–C34 in
Supplement S22: the BPIC19 layer macros on the excluded pair, the unseen
minimum without the rung filter, the case-study seed count), so v28.0's
generators would print three result summaries (and the harness's own check
count) differently from the submitted supplement. The statements on the
title page, in the article's data availability and in the cover letter say
what the archive holds and what the head post-dates. The choice is the author's: cut
`v29.0` from the pushed head and paste the new DOI with
`python scripts/insert_doi.py <DOI>` (recommended; every statement then
describes an archive that matches the submission), or keep v28.0 with the
statements as written. Recorded here rather than decided.

## 4. No graphical abstract — settled

Optional at Elsevier; the paper's figure 1 is the surface and would need a
new, caption-free rendering. Not supplied. Overturned if the submission
form makes it mandatory.

## 5. IJF LaTeX template — settled 2026-09-18

The template (`IJFTemplate.zip` from forecasters.org/ijf/authors, kept under
`submission/ijf-template/`) is `\documentclass[11pt,3p,review,authoryear]
{elsarticle}` with `model5-names` and `\biboptions{longnamesfirst}`; the
build had `[preprint,12pt,authoryear]` with `elsarticle-harv`. **Chosen:**
the article takes the template's options and both documents its bibliography
style; the supplement keeps `preprint,12pt` (no template governs an online
supplement, and its 122 pages at 1.5 spacing would be about 180). Diff and
consequences in `submission/IJF-TEMPLATE-CHECKED.md`. **What would overturn
it:** production asking for other options at acceptance.

## 6. The object is *incremental forecast performance*, not *forecast value* — settled during execution

**Chosen:** the vocabulary map renames *incremental predictive performance*
to *incremental forecast performance*. **Rejected:** *incremental forecast
value*, which the approved design named. **Why:** Section 1 says "we say
incremental predictive performance and not value" and Section 10's construct
paragraph is titled "this is predictive performance, not value"; in
forecasting, *forecast value* is the decision-based quantity (Murphy 1993;
Granger and Pesaran 2000), which only Section 8's net benefit computes. The
name would have claimed what the paper disclaims (rule 6). The introduction
says that the object is what the forecasting literature calls the value of a
predictor and why the word is reserved. **What would overturn it:** nothing
short of the paper measuring value.

## 7. Names a search resolves to the author are blinded — settled 2026-09-18

A web search for the package name with the paper's title returns the
author's repository first. **Chosen:** the package name and seven repository
file names print as generic descriptions in the blind build through
`paper/parts/blindnames.tex`; `check_blind` scans for the package name.
**Kept by decision:** the supplement's verification-harness section names
its scripts, because the scripts are its content. **Rejected:** leaving the
names (a one-search route to the author); scrubbing the harness section.

## 8. Four more passages to the supplement — settled 2026-09-18

§3.4 (the relative reduction's pathologies and rules), §4.7 (regret as a
check), §6.6 (decision rules in and out of sample) and the rules paragraph
of §8.3 moved behind pointers, after the pre-upload read named them as the
first moves. The regret null stays reported, in the supplement with pointers
in §1 and §4, because a null reported is part of the paper's honesty. The
article keeps its definition of the absolute absorption and the relative
reduction (equation 2), which §4.4, §6.4 and §7.5 use; the first cut had
dropped it and three independent reads caught that. Pages: 53 → 52 (the
template's options) → 52 after the moves → 54 after the 2026-09-19 reads added
the primary decomposition's per-pair table, two table columns and several
glosses; the
supplement 115 → 122.

## 9. The widest supplement tables in landscape — settled 2026-09-18

Tables set by `\resizebox` below about 5-point type (the region tables, the
denominator audit and the specification-curve table; S10, S15, S17 and S23
after the 2026-09-19 insertion of Table S9) are on landscape pages; the
measures and rules tables came back to portrait on 2026-09-19 (they fit at
body size with stacked headings), and S1 and S36 stay portrait because they
measured legible there and a landscape page cost each a stub or an
oversized float. The declared set is `LANDSCAPE_TABLES` in
`scripts/make_numbers.py`.

## 10. Keywords — settled 2026-09-18

"Uncertainty" and "specification surface" repeated title words, which the
guide says is pointless; replaced by "Decomposition" and "Statistical tests"
from the IIF list. Seven of eight keywords are the journal's; "Event logs"
is the paper's own. (2026-09-25: "Event logs" replaced by "Forecasting
practice", so all eight are from the IIF list; §IJF.14.)

## 11. The earlier value is "an earlier, unpublished analysis" — settled 2026-09-18

The case study reconciles its increment with one an earlier draft reported;
the article, Table S11 and the supplement's S15.1 had called that value
"published" or "reported". It was neither published nor citable, and the
word pointed at the author. It is now "an earlier, unpublished analysis of
this log", which is what it is.

## 12. The primary instrument, answered in one place — settled 2026-09-18

A forecasting referee's first question is why the area under the ROC curve
is primary when proper scores exist. The answer was in §1, §2, §3.4's
remarks, §6.2 and §8; it is gathered into one run-in paragraph at the end of
§3.4 that restates those sentences and adds nothing. An independent read
refuted the first draft of it ("nothing is averaged across instruments" is
false of §6.2 and §6.4) and the paragraph was cut back to what the article
says.


## 13. Pre-upload review against the live guide — settled (author, 2026-09-24)

A review on 2026-09-24 read the package against Elsevier's generative-AI
policy (updated June 2026), an archived copy of the IJF guide, a cold
referee read of the article and a consistency read of the supplement. The
author chose **Tiers 1 and 2** — fix compliance defects and errors, and
reframe for a forecasting readership without new analysis — and to
**neutralise** rather than remove the correction register (S22) and the
harness section (S8).

* **AI declaration in the manuscript.** The policy places it "immediately
  before the references" and asks that AI-written code be described in the
  Methods section. It moved from `statements.tex` (title page only) to
  `parts/aideclaration.tex`, which the blind article, the unblinded article
  and the title page all carry; §4.1 gained the Methods sentence.
  `check_blind.py` allows the tool's name inside that one section only.
  Rejected: leaving it on the title page (a referee holding the blind PDF
  would see no declaration).
* **Title** drops "Multi-Log" (to a forecaster "log" reads as the log score)
  for "Decomposition and Simultaneous Inference for Nested Probability
  Forecasts". The Zenodo v28.0 record keeps its own title; a v29.0 cut
  (§3, OWNER-ACTIONS 7a) would carry the new one.
* **Abstract and highlights** state that the forecasts are out-of-sample
  probability forecasts from nested models; the 71.7% is described as "the
  split and its interactions", which is what the macro measures; the case
  study's target sign flip — between two estimates whose intervals both
  include zero — is no longer in the abstract or highlights.
* **Forecast-evaluation literature**: seventeen references added, each
  verified against Crossref (Leamer 1983 and Hansen & Timmermann 2012 on
  RePEc/EUI). The article previously cited no IJF paper. "Which we have not
  seen elsewhere" is replaced by the precedents (Leamer; Young & Holsteen).
* **"Registered"** is now "pre-specified" in the §5 title and the
  contributions; §5.1 already says it is not a third-party registration.
* **Supplement**: stale captions of Tables S10, S17 and S42 (which said the
  families need more widening than the calibration supplies, contradicting
  §9.2) rewritten; the S1.1/S14.5 claim that staleness is visible under one
  encoder and not another, which S14.5's own numbers contradict, rewritten;
  revision-history language removed throughout.
* **Not done (Tier 3, would need new analysis):** intervals on the
  decomposition shares; a τ²-style separation of sampling from fold
  variation; a proper score as primary instrument; within-metric region
  labels; paired intervals for the case study's origin steps at a fixed
  baseline; cutting the article toward 35 pp. These are the likeliest
  referee requests.

## 14. Second pre-upload review: five lenses, four implementation passes — settled (2026-09-25)

The author asked for a further multi-agent review aimed at removing every
reason for a desk rejection. Five reviewers read the build: an IJF handling
editor's desk screen calibrated on recent IJF papers and the editor reports,
a forecast-comparison econometrician, a scoring-rules statistician, a
structural editor, and a compliance check (the live guide stayed behind a
bot check). Their findings were implemented by four passes in isolated
worktrees, merged and gated:

* **Framing and positioning.** The abstract opens on forecast evaluation; the
  introduction is anchored in the nested-comparison literature and frames the
  case as service-operations forecasting; contributions are three positive
  forecasting claims; related work keeps the forecasting frame and moves the
  ML-importance, process-mining, many-analysts and data-quality strands to
  Supplement S1.1; sixteen further references, IJF-anchored, each verified
  against Crossref. Keyword "Event logs" → "Forecasting practice". The cover
  letter is rewritten (about 650 words): the history is two sentences and the
  account of internal machine-assisted reviews, the weaknesses paragraph and
  the repository bookkeeping are gone (the AI declaration is in the
  manuscript).
* **Length.** Article 57 → 45 pp by moving to the supplement what it already
  held and by consolidating tables (roles, resolution triple and MPID tables
  to the supplement; the master table absorbs counts, n and K). Printed
  terminology: "instrument" → "metric", "rung/ladder" → "nested baselines",
  "estate" → the bank's service desk, "registered" → "pre-specified".
* **Figures** redrawn at print size (≥ 8 pt); Figure 1 is AUC-only; Figure 3
  now shows the stratum partition that carries the headline share.
* **New analyses from existing results** (`scripts/s60_ijf_checks.py`,
  Supplement "Forecast-evaluation checks"; re-derived by
  `round31_verify.py`): the sign-disagreement rate against each cell's own
  metric (2.9%, against 13.0% against the AUC reference; the whole gap is
  BPIC19's proper-score cells); region labels within each metric; pair-
  bootstrap intervals for the corpus-median shares; the split's main effect
  against its interactions; the headline shares in Brier and log-loss skill;
  Diebold–Mariano and Clark–West tests at the reference cell (refit only
  that cell); a fold-trend diagnostic. The article states each where it
  bears (§4.4, §6.2, §6.3, §6.4, §10).
* **Not done — needs a new bootstrap run:** draws shared across splits (so
  sampling noise can be subtracted from the split stratum), a zero-increment
  simulation world, step-down bands, a surface-wide Clark–West comparison,
  and adopting a finite-window (Giacomini–White) estimand throughout. §10
  states them as open.
* **Final verification (three independent reads of the merged build) and
  its fixes.** The desk-reject estimate from a fresh editor's screen stayed
  near 40%, driven by substance rather than presentation (the pointwise
  interval's undercoverage at this corpus's K/n, no theorem, novelty as a
  combination). Fixed from those reads: "separates forecaster choices from
  sampling variability" overstated what an exact partition can do — the
  split stratum is now described as sampling variability and fold-to-fold
  instability that this design cannot separate; "bands over the design
  family" → "over a declared family"; the 1.71-versus-0.003 desk figure is
  now described as what it is — the arrival attributes alone against the
  fields assumed recorded by incident creation, on the pre-specified
  handover target — not as a comparison of two §7 origins; the Clark–West
  sentence counts one-sided rejections, not signs; every admitted log is
  cited as a [dataset] reference (DataCite-verified); four references added
  (Ehm et al. 2016; Patton 2020; Stock & Watson 2003; Welch & Goyal 2008);
  supplement terminology aligned with the article; Table 3 prints larger.
* **Archive consequence.** The forecast-evaluation checks' code and result
  files are at the repository's head, not in v28.0; the title page's code
  statement says so. This makes cutting v29.0 (OWNER-ACTIONS 7a) the
  cleaner route: the archive would then hold every result the submission
  cites.

## 15. Final pre-upload review: four lenses and a reference check — settled (2026-09-25)

Four independent reads of the rebuilt package (IJF guide compliance, a
forecast-evaluation referee, a page-by-page copy-edit, package consistency)
and a Crossref check of every cited DOI. What changed:

* **References.** `senderovich2017intercase` carried the BPM 2017 paper's
  title with an unrelated *Information Systems* article's venue and DOI; it
  now points at the BPM 2017 record. Added, each verified on Crossref:
  Murphy (1973) where the resolution component is named; Pesaran and
  Timmermann (1995), Granger and Jeon (2004) and Aiolfi and Favero (2005) as
  the forecasting precedents for working over a specification space. Dataset
  titles keep their capitals; proceedings series are folded into the
  booktitle so they are punctuated.
* **Abstract and keywords.** AUC is spelled out; the resolved-distance median
  says it is over 9 tasks (`nPairsMadResolved`, re-derived in
  `round31_verify`). "Decomposition" became a title word on 2026-09-24, so
  the keyword is replaced by "Error measures" (IIF list). 150 words.
* **The no-signal benchmark.** With six split levels the split-involving
  components hold 83.4–83.7% of the degrees of freedom, so independent cell
  noise alone would put that share there; the observed 71.7% is below it on
  17 of 19 pairs, and the analyst's choices carry 13.3% against 2.3%. §6.2
  and §11 now say so (four macros from `round31_numbers`, re-derived by
  enumerating the components in `round31_verify`). The abstract is unchanged
  and is the author's call.
* **Internal consistency.** The case study no longer calls a move between
  −0.0029 and +0.00768 consequential: both are inside the declared MPID.
  §4.1 no longer presents level loss as the cause of the displacement, which
  S3.9 shows it is not. Skill scores are "affine in a strictly proper score
  on a fixed test set", not strictly proper. The conclusion's coverage claim
  carries the ideal-bootstrap bound and the pointwise undercoverage.
* **Reproduction.** `s60_ijf_checks.py` now runs in `round27_chain.sh`, so
  the one command regenerates Supplement S14.
* **Statements.** Corresponding-author mark on the title page; CRediT en
  dashes; `declaration_of_interests.md` no longer names two organisations
  for thirteen logs; the supplement's abstract lists what it holds; AI-USE
  pointers S24/S22.3.
* **Not done, by choice:** cutting to ~35 pages, renaming the paper's
  vocabulary, bias-corrected point estimates, re-sizing Tables 2, 3 and 5
  (legible at 6–7 pt). These are the likeliest referee asks.
* **The archive: v29.0 (author, 2026-09-25).** Under v28.0 the article's
  data-availability sentence, the §4.1 note and the AI declaration ("every
  result is archived") were false for S14. The tree now says v29.0:
  `.zenodo.json` version v29.0 with no `doi` key (the DOI is minted by the
  release; `finalise.py` owes it until `insert_doi.py` writes it), the
  title-page code statement says the release holds every cited result, S23
  Class N names v28.0 as the release that prints the old values, and the
  cover letter reads `DOI-PENDING`, which `finalise.py` also flags. A local
  commit was approved; the push and the GitHub release are
  the author's (the local `gh` account is not the repository owner's).

## 16. The GitHub release, not a Zenodo DOI — settled (author, 2026-09-28)

The author pushed `main` and `ijf-retarget` and published the GitHub release
`v29.0` on `88c7f66` (both done from this session at the author's request,
signed in as sudhirdixit1). The author then chose to cite the GitHub release
rather than a Zenodo DOI. The title-page code statement names the repository
and release v29.0 and says that release holds the analysis code, the figures
and every result file the paper cites (not "the manuscript source": the
statements were reworded after the tag, and the tag is not moved); the
article's data-availability sentence says the results are in the release the
code statement names; the software reference's note is the release; the
cover letter and the data-availability form text name the repository and
release. `finalise.py` now owes the release tag on the remote instead of a
DOI. The repository's Zenodo webhook (installed for v28.0) accepted the
v29.0 release event, so Zenodo may hold a v29.0 record; the submission does
not cite it. The AI declaration's span runs to 2026-09-28.

## 17. The author's employment is disclosed — settled (author, 2026-09-28)

The Editorial Manager registration lists the author's employer (Cognizant,
Solutions Architect). The title page said "no affiliation with ... any vendor
of ... IT service management ... software", which an editor could read as
untrue of an IT-services employee. The author chose to keep "Independent
Researcher" as the affiliation and disclose the employment: the title page's
competing-interest section, `declaration_of_interests.md` and the cover
letter now say the author is employed by Cognizant, that the work was done
independently of that employment without its support or data, and that
Cognizant had no role in it. The blind documents carry no competing-interest
statement and are unchanged.

# Plan: remove every nameable reason to reject

**Written:** 2026-08-22, after round seventeen shipped
**Predecessors:** `PLAN-INFORMATION-SYSTEMS.md` (executed, see its §12),
`PLAN-STRONG-ACCEPT.md` (executed, see its §12)
**Audience:** an autonomous agent. Read §0 before doing anything.

---

## 0. How to work

### 0.1 What this plan can and cannot do

It cannot guarantee acceptance. No plan can, and a plan that implies otherwise
is lying to whoever executes it.

What it *can* do is different and worth stating precisely:

> **Every objection a referee can name gets a section that answers it with a
> measurement, a proof, a documented negative, or an explicit concession —
> and the paper contains a map from objection to answer.**

That is the target. It is achievable. Round seventeen's honest verdict was
that the paper's remaining exposure is not sloppiness — the numbers survive —
but *contribution size and scope*. Those are fixable, and this plan fixes
them by adding evidence the paper does not currently have, not by rewriting
claims it already makes.

### 0.2 The rules, inherited

These are not new. Seventeen rounds arrived at them by getting each one wrong
first. `PLAN-STRONG-ACCEPT.md` §0.1 has the full list; they all still apply.
The four that will bite hardest in this round:

1. **If a result contradicts the paper, the paper changes.** This round adds
   a literature audit, a theorem, a prospective test and a simulation. Any of
   them can come back against the paper. Round seventeen had three do exactly
   that and the paper is better for it.
2. **Assume the next correction flatters the result.** Eight of eleven so far
   did.
3. **Every constructed control introduces a confound. Null it.**
4. **Write the corruption before you believe the check.** Round seventeen
   found five more holes in the checker and every one was found by the suite.

### 0.3 The rules, new to this round

5. **A pre-registered prediction beats a post-hoc explanation, and this round
   has exactly one chance to make that trade.** Round seventeen ended by
   *explaining* where the effect appears. §4 turns that explanation into a
   registered prediction and tests it on logs this project has never opened.
   Once a log is opened it is burned as held-out data forever. **Do not open
   BPIC 2011, BPIC 2018, or any log added to 4TU since round seventeen until
   §4.2 is committed.**
6. **The audit is evidence about other people's papers. Code it mechanically,
   publish the sheet, and never characterise a paper you have not read.** A
   literature audit done carelessly is worse than none: it invites a referee
   who wrote one of the audited papers to check your coding of it.
7. **Anything the paper claims a reader can do, ship as something they can
   run.** §6's tool is not a convenience. It is the difference between
   proposing a standard and demonstrating one.

### 0.4 When you are blocked

Unchanged from `PLAN-STRONG-ACCEPT.md` §0.3:

| Kind | What to do |
|---|---|
| **A decision** | Take it. Record it in `submission/DECISIONS.md` with the rejected alternatives. Never park it. |
| **A credential** | Stop *that item only*, write the steps into `submission/OWNER-ACTIONS.md`, continue with everything else. Do not work around it. |
| **A dead end** | Record the search in enough detail that nobody repeats it, state the negative as a finding, move on. |

### 0.5 What is still outside reach, and stays in the Limitations

Say these in the paper rather than hoping nobody notices. They were true at
the end of round seventeen and this plan does not change them:

- No deployment, no organisational partner, no practitioner validation.
- A single author with no institutional affiliation.
- Public benchmark data only; the newest event log is from 2019.
- No inter-rater reliability on the literature audit, because there is one
  author. §2.5 says what is done instead.

---

## 1. The diagnosis: seven things a referee can still say

Round seventeen closed the rigour objections. What remains is scope and
contribution. Each item below names the objection in a referee's voice, then
names the phase that answers it.

| # | The objection, as a referee would write it | Answered by |
|---|---|---|
| **D1** | "This assembles known critiques — Cook 2007 on AUC increments, Hand 2009 on metric incoherence, Vickers–Elkin on operating points, Williamson and Covert on baseline-relativity — and measures their magnitudes on a single dataset." | §2, §3 |
| **D2** | "The empirical result is a null on one log. What did we learn?" | §5 |
| **D3** | "The generality claim was registered and falsified. The corpus section reports a failure." | §4 |
| **D4** | "Everything is demonstrated on BPI Challenge 2014. The claim that each choice moves the answer by more than the effect is an n = 1 claim." | §5 |
| **D5** | "Eleven self-reported errors. Why should I trust the twelfth number?" | §7.3 |
| **D6** | "Forty-seven pages, single unaffiliated author, no deployment. Is this the right journal?" | §7, §8 |
| **D7** | "The proposed standard is a paragraph of prose. Nothing here makes it easier to follow than to ignore." | §6 |

**D1 is the one that decides the paper.** Everything else is survivable on its
own; D1 is the objection a competent referee reaches for first, and it is the
one round seventeen did nothing about. §2 and §3 exist to make it
unwritable.

---

## 2. Phase 1 — Prove the practice failure is real

**Do this first. It is the highest-leverage work in the plan and everything
else is easier once it exists.**

The answer to *"this is a known critique"* is: **yes, and here is how often
the field ignores it, measured.** A critique that everyone already accepts and
nobody follows is not a known critique — it is a documented practice failure,
and documenting one is a contribution in its own right at an IS venue.

### 2.1 The claim to be established

> Among published papers that report the incremental value of a feature, a
> field or a data source, a large majority state **none** of the four
> choices, and almost none report a range over any of them.

If that is false — if most papers do state their baseline and justify their
metric — **the paper's central premise collapses and you must say so.** That
outcome is possible and it would be the most important finding this project
has ever produced. Report it either way.

### 2.2 Pre-register the audit before reading anything

Write `AUDIT-PROTOCOL.md` and **commit it before screening a single paper**,
in a commit that adds no coded row. Same discipline as `PROTOCOL.md`, same
evidence: `git log --stat` shows it arriving alone.

It must fix, in advance:

**Sampling frame.** Name it precisely and defensibly. The recommended frame:

- Papers published 2019–2026 in a fixed venue set: *Information Systems*,
  *Decision Support Systems*, *Information & Management*, BPM, ICPM, CAiSE,
  and *Empirical Software Engineering*.
- Plus every paper citing Teinemaa et al.'s outcome-oriented predictive
  process monitoring benchmark, via a named index (Semantic Scholar or
  OpenAlex API), which is machine-enumerable and therefore reproducible.
- Cap the frame at a stated N and sample at random with a recorded seed if
  the frame exceeds what can be screened. **Never sample by convenience.**

**Inclusion rule.** A paper is included iff it reports, anywhere, a
quantitative comparison of predictive performance *with* and *without* a
named feature, field, feature group or data source. Everything else is
excluded, with the exclusion reason recorded.

**The coding sheet.** Five binary items per included paper, each with a
mechanical rule and each requiring a supporting quote:

| code | question | rule |
|---|---|---|
| `B_stated` | Is the baseline's feature set enumerated? | The reader can list the baseline's features from the paper without guessing |
| `B_justified` | Is the choice of which already-available fields to exclude from the baseline argued? | An explicit sentence, not an implication |
| `M_justified` | Is the metric argued for, rather than only named? | A reason is given for that metric over others |
| `Theta_stated` | Is an operating point or a cost ratio stated? | A threshold, a capacity, a cost ratio, or an explicit statement that the metric integrates over them |
| `Range_reported` | Is the incremental value reported as a range or surface over any of the four choices? | An interval over a *choice*, not a confidence interval |

**Every code carries a verbatim quote and a page number, or it is coded
`unclear` and counted as such.** `unclear` is a legitimate value and is
reported separately from `no`.

### 2.3 Run it

**Script:** `r40_audit.py` (frame enumeration, deduplication, screening log)
**Output:** `results/r40_frame.csv`, `r40_screening.csv`, `r40_coding.csv`

The coding sheet ships with the paper as supplementary material. Every row has
the DOI, the quote and the page, so a referee — including one whose own paper
is in the sample — can check any row in a minute.

### 2.4 Report

- The frame, the screening funnel (a PRISMA-style count is appropriate and
  reviewers expect it), and the inclusion rate.
- Each of the five codes as a proportion with a binomial interval.
- The joint distribution: how many papers state **zero** of the four choices.
- **A worked example of the consequence.** Take one included paper — one
  whose data is public, so the reader can follow — and show what its reported
  number would look like as a surface. This is the single most persuasive
  paragraph the paper can contain, and it must be done without impugning that
  paper's authors: the point is that the practice is universal, not that
  anyone was careless.

### 2.5 The inter-rater problem, and what to do instead

One author cannot compute inter-rater reliability, and a referee will say so.
Do all four of these:

1. **Publish every code with its quote**, so the coding is auditable rather
   than trusted.
2. **Re-code a random 20% after at least seven days**, blind to the first
   pass, and report intra-rater agreement (Cohen's κ) with the disagreements
   listed.
3. **Write the coding rules to be mechanical**, and record every case where a
   rule had to be interpreted.
4. **State the limitation in the Limitations section in the referee's own
   terms.** Do not bury it in a footnote.

### 2.6 What would sink this phase

The audit finding that the field already reports these choices. Then D1 is
correct, the paper's premise is wrong, and the honest response is to say so
and reframe the paper around the CMDB null. Record it in §13 and do not dress
it up.

---

## 3. Phase 2 — Make the four axes a result, not an observation

D1 also has a formal half: *the dependence is a known theorem.* The answer is
to prove something the existing frameworks do not say.

### 3.1 The three propositions to establish

Each is provable or constructible, and each has an empirical shadow already in
the paper.

**Proposition 1 (metric-unboundedness).** For any target value
$r \in [0,1)$ there exist score distributions, a baseline $B_0$, a feature
$f$ and two defensible metrics under which the admissibility reduction
$R$ equals $r$ and $0$ respectively. *Construct it.* A two-point score
distribution with a tunable tie mass suffices; the paper already reports the
empirical version — $43.7\%$ under AUC against $60.3\%$ under average
precision on identical scores.

**Proposition 2 (rank-invariance boundary).** $R$ is invariant under any
strictly monotone transformation of the scores **iff** $m$ is rank-based.
This is short, it is exactly true, and it converts §8's calibration result
from an observation into a statement about which instruments can and cannot
see calibration. The paper already reports the empirical version:
recalibration moved the proper-score reductions by up to $0.014$ and the rank
reductions by exactly zero.

**Proposition 3 (non-redundancy).** No one of the four choices determines
another: for each ordered pair of axes, exhibit two configurations agreeing
on the first and differing on the second. Four axes give twelve pairs;
construct all twelve or state which cannot be constructed and why.

### 3.2 How to write them

**These are propositions with constructive proofs, not a theory section.**
Two pages, in an appendix, with the constructions given as runnable code so
the reader can execute the counterexamples. A referee who distrusts a proof
can run it.

**Script:** `r41_propositions.py` — each proposition's construction, executed,
with the resulting numbers asserted against the claim. If a construction
fails to produce the claimed value, the proposition is wrong and comes out.

**Do not overclaim.** These are small results. Their job is to move the
paper's contribution from "measured some magnitudes" to "established what can
and cannot happen, and then measured what does". Say that in those words.

### 3.3 What would sink this phase

Proposition 2 failing — a rank statistic that moves under a monotone
transform would mean the implementation is broken. Proposition 1 failing to
reach the full range would bound the claim and the paper reports the bound
instead.

---

## 4. Phase 3 — Turn round seventeen's explanation into a tested prediction

Round seventeen ended with an explanation: the effect appears where the
opening field carries information and not where it is nearly constant. An
explanation produced after seeing the data is worth little. **A registered
prediction tested on unopened data is worth a great deal, and this project
has exactly one opportunity to make that trade.**

### 4.1 The held-out set, and the rule protecting it

Never opened by this project:

- **BPI Challenge 2011** (hospital) — excluded in `PROTOCOL.md` §2 for size.
- **BPI Challenge 2018** (agricultural subsidies) — excluded for parsing cost.
- **Any event log published on 4TU.ResearchData after 2026-08-21.** Enumerate
  these via the API and record the enumeration; do not open them.

**Rule.** Do not parse, inspect, or compute anything from these logs until
§4.2 is committed. The commit that adds the prediction adds no result file
from any held-out log. `git log --stat` is the evidence.

### 4.2 Register the prediction

Write `PREDICTION.md` and commit it alone. It must state:

**The rule, with its parameters fixed numerically from round-seventeen data.**
For a log admitted by `PROTOCOL.md` §3:

> $R$ will be resolvably positive **iff** (i) $V(f \mid B_0)$ is resolvably
> positive, and (ii) the normalised entropy of the opening field $g$ exceeds
> $H^*$.

Fit $H^*$ on the thirteen round-seventeen logs, print it, and freeze it in
the file. **A rule with a free parameter is not a prediction.**

**The scoring.** For each held-out log, the rule predicts one of three
outcomes — resolvable, not resolvable, or excluded by a `PROTOCOL.md` code —
before the log is opened. Report a confusion matrix. State in advance how
many misses falsify the rule.

**What a failure means.** If the rule fails, the paper reports it and drops
the condition to a post-hoc observation, which is what it is today. That is a
smaller paper and an honest one.

### 4.3 Run it

**Scripts:** `r42_holdout_fetch.py` (by DOI, checksums, same discipline as
`fetch_corpus.py`), `r43_holdout_test.py`

Apply `PROTOCOL.md` §3–§5 unchanged. Change nothing about the protocol for
the held-out logs; that is the whole point.

### 4.4 Why this is the answer to D3

D3 says the corpus section reports a failure. After §4 it reports a
falsification **and** a successful prospective test of the mechanism the
falsification revealed. Those are different papers. The first is a negative
result; the second is a negative result that produced a rule that then
predicted correctly on data it had never seen.

---

## 5. Phase 4 — n = 1 becomes n = 3, plus a case with a known answer

### 5.1 The four-axis demonstration, on every log that can carry it

Round seventeen varied all four choices on BPI Challenge 2014 alone. Three
logs have a resolvable reduction: BPIC 2014, BPIC 2013 incidents, BPIC 2019.

Run the **full** four-axis surface — baseline ladder, six instruments, the
threshold grid, the population curve — on all three, with the same code path.

**Script:** `r44_axes_multilog.py`
**Reports:** the surface per log, and the *range of the range*: how much the
four choices move the answer on each. If the spread is comparable across
three organisations, three tools, two countries and two domains, D4 is gone.

**What would sink it:** the choices mattering on BPIC 2014 and not elsewhere.
Then the paper's central claim is about one estate and must say so.

### 5.2 A case where the answer is known by construction

Every number in this paper is estimated. None is checked against a truth,
because on real data there is no truth to check against. A simulation fixes
that and costs a day.

**Design.** Generate $(B_0, g, f, y)$ with a controlled overlap parameter
$\rho$ governing how much of $f$'s information about $y$ is also carried by
$g$. The true reduction $R^*(\rho)$ is then known in closed form or by
exhaustive enumeration.

**Report.** Estimated $R$ against $R^*$ across $\rho$, with the estimator's
bias and coverage. Repeat under the four choices to show the surface behaves
as Propositions 1–3 say it must.

**Script:** `r45_simulation.py`

This does three things at once: it validates the estimator, it demonstrates
the propositions numerically, and it is entirely era-independent, which
partially answers the 2019-data objection in §0.5.

### 5.3 The CMDB null, stated as the finding it is

D2 asks what we learned. The answer, said plainly and scoped exactly:

> On this task, this estate and this target, a register that costs money to
> build and maintain adds nothing measurable over two fields the organisation
> already records — and one of those fields is a knowledge-article reference
> that no baseline in this literature would have thought to admit.

Round seventeen already has that sentence in the conclusion. **Promote it.**
It is more interesting than "the reduction is 43.7%" and it is what a
practitioner will remember.

---

## 6. Phase 5 — Make the standard runnable

D7: the proposed standard is prose. Ship code.

### 6.1 The package

A small, dependency-light Python package in `fieldvalue/`, installable and
tested, with one job:

```python
from fieldvalue import surface

s = surface(
    X, y,
    feature="ci_name",
    baselines={"intake": INTAKE, "intake+group": INTAKE + ["group"]},
    metrics=["auc", "ap", "brier_skill", "nagelkerke", "net_benefit"],
    thresholds=np.arange(0.05, 0.80, 0.025),
    population=[1.0, 0.75, 0.50, 0.25],
    n_boot=2000, seed=20260819,
)
s.report()            # the minimum reportable form, as text
s.to_frame()          # the surface as a tidy DataFrame
s.plot()              # the signature figure
```

Plus a CLI: `python -m fieldvalue --data x.csv --target y --feature f ...`

**Requirements, all of which a referee will check:**

- Unit tests, including the Propositions 1–3 constructions as test cases.
- A worked example notebook on a public dataset that is **not** one of this
  paper's logs.
- An independence check: `r46_tool_agreement.py` re-derives the paper's
  headline surface through the package and asserts it matches `r30`'s output.
  Two independent code paths agreeing is a check the paper does not currently
  have.
- A refusal path: the package **declines** to emit a single number, by
  design, and says why. That is the standard, encoded.

### 6.2 Why this is worth the effort

It converts the contribution from *"you should report a surface"* to
*"here is the surface, computed, for your data, in four lines"*. Referees
weigh proposals they can run differently from proposals they must adopt.

---

## 7. Phase 6 — Rebuild the manuscript around the new evidence

Only after §2–§6 exist.

### 7.1 Target shape

| § | Content | Target pages |
|---|---|---|
| 1 | Introduction — four contributions | 3 |
| 2 | Background and related work | 3 |
| 3 | The estimand, and three propositions | 4 |
| 4 | **The audit: how the field reports feature value today** | 5 |
| 5 | Data, protocol and pre-registration | 3 |
| 6 | The four axes, on three organisations | 6 |
| 7 | The simulation: the estimator against a known answer | 3 |
| 8 | The corpus, the falsification, and the registered prediction | 5 |
| 9 | The reporting standard, and the tool | 3 |
| 10 | Threats, each measured | 3 |
| 11 | Limitations | 2 |
| 12 | Conclusion | 1 |
| App. A | Proposition constructions | 2 |
| App. B | The corrections, and the defect taxonomy | 3 |

**Main text target: 36 pages.** Round seventeen shipped 47. The material
being cut is not disclosure — it is per-axis detail that moves to
supplementary. `submission/DECISIONS.md` §14 already identified §9's mechanism
material and §13's per-axis detail as the two that move.

### 7.2 The signature figure

The paper currently has ten figures and no single image a reader carries
away. Build one: **the surface itself**, as a small-multiple grid — baseline
on one axis, metric on the other, each cell a miniature threshold curve, the
cell's colour the reduction. One image showing that the same data gives
answers from $6\%$ to $119\%$ depending on which cell you stand in.

**Script:** `r47_signature_figure.py`

Requirements: readable in greyscale, readable at half width, every value read
from a result file, and a caption that states what it does *not* show.

### 7.3 The corrections, restructured

D5 says eleven self-reported errors read as unreliability. The fix is not to
hide them — `PLAN-STRONG-ACCEPT.md` §11 settled that and the decision stands
— but to change what they are *for*.

**Promote the taxonomy, demote the incidents.**

- In the main text, a short section on the **defect classes** the eleven
  instances fall into: a null drawn at the wrong level; a ratio without an
  interval; a claim about a number's meaning that every literal supports; a
  consumer placed above its producers; a harness that can modify its subject.
  That is a contribution to research practice and it reads as expertise.
- In an appendix and in the repository, the eleven incidents with their
  causes.
- **Say once, early, why they are there**: a paper whose thesis is that
  unexamined choices set the answer cannot suppress its own.

### 7.4 The reviewer's map

A one-page supplementary document, `submission/reviewer_map.md`: a table with
one row per objection from §1 of this plan plus every objection in
`REFEREE-LOG.md`, and the section that answers it.

This is not padding. It is the difference between a referee who has to hunt
for your answer and one who is handed it.

---

## 8. Phase 7 — Re-take the venue decision

The paper was retargeted to *Information Systems* in round fifteen when it was
a CMDB empirical study. Its centre of gravity is now evaluation methodology
with a CMDB demonstration, an audit and a tool. **That may not be the same
journal's paper.** Re-take the decision explicitly rather than inheriting it.

### 8.1 Criteria, fixed before comparing

1. Does the venue publish evaluation-methodology work with empirical
   demonstrations?
2. Does it have a reproducibility or artifact track that engages with this
   paper's strongest asset?
3. Does it publish literature audits?
4. Typical length allowance.
5. Median time to first decision.
6. Does it accept single-author unaffiliated submissions in practice? Check
   by counting, in the last two years' issues, not by assuming.

### 8.2 Candidates

*Information Systems* (incumbent), *Empirical Software Engineering*,
*ACM TOSEM*, *Decision Support Systems*, *Information & Management*,
*Journal of Systems and Software*, and the *Empirical Software Engineering*
registered-reports track if it exists at submission time.

**A registered-reports track deserves special attention.** This paper has a
pre-registered protocol, a pre-registered prediction and a pre-registered
audit. Few submissions are better shaped for that route, and it converts the
"contribution is incremental" objection into a review of the *design* before
results are known.

**Script:** `r48_venue.py` — collect what is machine-collectable (scope
statements, length limits, decision times where published, author-affiliation
counts from recent issues) into `results/r48_venue.csv`.

Record the decision and every rejected alternative in
`submission/DECISIONS.md`. If the answer is that the incumbent is still
right, record *that* with its reasoning; an unchanged decision that has been
re-examined is worth more than one that has not.

---

## 9. Phase 8 — The artifact, extended

Round seventeen's artifact is strong. Four additions, each closing something
a referee could pick at.

- [ ] `verify_paper.py` covers every new number: the audit proportions, the
      proposition constructions, the simulation, the held-out test, the
      three-log surfaces. Same discipline — a check with an anchor, or the
      paper does not print it.
- [ ] `attack_verifier.py` gains a corruption per new claim, **including at
      least three that mutate a relation rather than a value**, which is the
      class corrections nine and ten belong to.
- [ ] The audit's coding sheet ships as supplementary material with every
      quote and page number.
- [ ] `fieldvalue/` has its own test suite, run by `reproduce_all.py`, and the
      independence check of §6.1 is one of the stages.

Carry forward, unchanged, from `PLAN-STRONG-ACCEPT.md` §7: the lockfile, the
container, the DOI-and-checksum fetch, the per-script runtimes, and the
README's statement of what the checker does *not* cover.

---

## 10. Phase 9 — Six adversarial passes

Round seventeen ran four. Run six, each with a brief, each instructed to
reject, and log every objection with its disposition in `REFEREE-LOG.md`.
The four from `PLAN-STRONG-ACCEPT.md` §8, plus two new ones:

5. **The literature-audit referee.** Is the frame defensible? Is the coding
   reproducible? Would you accept this audit if your own paper were in the
   sample? Check three coded rows against the actual papers.
6. **The editor.** Is this one paper or three? Would you send it out? What
   would you say in a desk-reject letter? **This pass matters most** — a desk
   reject is the outcome §1's D6 describes and no referee ever sees it.

Every objection gets a measurement, a documented negative, or an explicit
concession. Log the dismissed ones and why.

---

## 11. Definition of done

**Necessary**

- [ ] The audit is pre-registered, run, and reported with its funnel, its
      proportions with intervals, and its full coding sheet (§2)
- [ ] Intra-rater agreement reported on a re-coded 20%, with disagreements
      listed (§2.5)
- [ ] Three propositions stated, constructed, and executed as tests (§3)
- [ ] The precondition registered as a prediction **before** any held-out log
      is opened, and tested, with a confusion matrix (§4)
- [ ] The four-axis surface run on all three logs that can carry it (§5.1)
- [ ] The simulation reports estimator bias and coverage against a known
      answer (§5.2)
- [ ] `fieldvalue/` installs, tests, and re-derives the paper's headline
      through an independent code path (§6)
- [ ] Main text at or under 36 pages, with a signature figure (§7)
- [ ] The corrections restructured as a taxonomy in the text and incidents in
      an appendix (§7.3)
- [ ] `submission/reviewer_map.md` maps every objection to its section (§7.4)
- [ ] The venue decision re-taken against stated criteria and recorded (§8)
- [ ] Every new number checked; every new claim has a corruption; suite passes
      0 missed, 0 skipped (§9)
- [ ] Six adversarial passes, every objection dispositioned (§10)
- [ ] The manuscript builds with 0 errors and 0 undefined references
- [ ] §13 records what each phase found, **including the phases that found
      nothing**

**Sufficient — what would make a referee unable to name a reason**

- [ ] **D1 is unwritable.** The audit shows the practice failure is real and
      quantified, and the propositions establish what can happen before the
      measurements show what does.
- [ ] **D3 is inverted.** The falsification is followed by a prospective test
      the paper passed.
- [ ] **D4 is gone.** Three organisations, and a simulation with a known
      answer.
- [ ] **D7 is gone.** The standard is four lines of code.
- [ ] **No claim rests on an unvaried choice**, and for every number in the
      abstract a reader can find where the paper varies the choices behind it.

**The honest test**, unchanged from `PLAN-STRONG-ACCEPT.md` §10. Write the
rejection letter yourself, the strongest one you can. Round seventeen could
write a persuasive one; every clause of it was a sentence the paper already
contained. **Round eighteen's target is a rejection letter whose only
remaining clauses are the four items in §0.5.** If you can still write a
clause about contribution size or scope, this plan has not finished.

---

## 12. What this plan deliberately does not attempt

Recorded so it is not proposed as fresh in round nineteen.

- **A deployment or an industry partner.** Not obtainable by an agent, and a
  fabricated one would be the exact failure the paper is about.
- **Modern proprietary data.** Same.
- **A second author or an affiliation.** Only the author can change that, and
  it is not a research action.
- **Removing the Corrections section.** §7.3 restructures it; it does not go.
- **A second corpus sweep.** Round seventeen's corpus result is the honest
  ceiling on generality from public data. §4 tests the *mechanism* on held-out
  logs, which is a different and better use of what remains.
- **The checker paper.** `HANDOFF.md` §19.8 and §20.10 argue the verification
  apparatus is a stronger contribution than the CMDB finding and belongs at
  MSR or EMSE. Round seventeen strengthened that case with three new defect
  classes. It remains true and remains *after* this submission.

---

## 13. Execution record

*Append after each phase: what ran, what it found, what changed in the paper,
what it cost. Numbers in this record are checked against the result files like
any other numbers. Record the phases that found nothing, in those words.*

### The record

*Executed 2026-08-22 on branch `round-eighteen-reviewer-proof`, under a
directive to work through the plan without stopping to ask questions. Every
phase ran. Four came back against the paper and one of those was the plan's
own premise.*

| Phase | Outcome | Cost |
|---|---|---|
| **§2 the audit** | **Against the paper's premise, and the paper changed.** 600 papers, 369 full texts, 54 included, 30 read, 20 confirmed. `B_stated` 40%, `M_justified` 50% — so "a large majority state none of the four" is false and is withdrawn. What survives: **0 of 20 report the increment across a range of operating points, and 0 of 20 across a range of register populations.** Three registered patterns did not implement their own rules and one over-correction was discarded; all four are in amendment 1. | ~3 h |
| **§3 the propositions** | **All three hold.** P1's exact zero needed an integer construction — the first version, in proportions, produced 4.4e-4 and failed its own assertion. P3 is ten of twelve, and the two failures are named; a referee pass then measured the count across sixteen tolerance cells, where it runs 8 to 12. | ~1 h |
| **§4 the prediction** | **Registered, tested, and half of it is untested.** The form the plan named reaches in-sample balanced accuracy 0.600 and is registered anyway, beside the form that separates all nine. Two scored pairs on BPI Challenge 2011, both correct, **both negative**. BPI Challenge 2018 excluded by registered codes because 99.9% of its cases open with `0;n/a`. | ~2 h |
| **§5.1 three organisations** | **Replicates, and then an adversarial pass halved it.** The baseline spread exceeded R on all three logs over the full ladder; restricted to baselines an analyst would build it is 0.346, 0.347, 0.382 against 0.350, 0.378, 0.471. The stronger sentence is gone. | ~1 h |
| **§5.2 the simulation** | **Survives, and it is the strongest new evidence about the estimator.** Bias ≤ 0.0044 at n = 60,000, coverage 0.850–0.975, and the ordering of the four axes matches the three real logs on data nobody chose to make agree. | ~1 h |
| **§6 the tool** | **Survives, and it found correction twelve on its first run.** 91 tests, `float(s)` raises, 20 of 20 quantities agree with the pipeline to 2.2e-16. | ~2 h |
| **§7 the manuscript** | 42 pages of main text against a target of 36 and the plan's own per-section budget of 41. Nine blocks moved to appendices, each with a pointer; a threats section the plan allocated and the paper did not have was added. | ~4 h |
| **§8 the venue** | **The decision changed.** Empirical Software Engineering. Criterion 6 was counted: 5 of 3,360 recent articles across eight venues are single-author and unaffiliated. | ~0.5 h |
| **§9 the artifact** | 1,386 checks, 0 failed, 0 unaccounted. 253 corruptions, 19 of them relation mutations. Two more holes found in the checker, both by adding material. | ~2 h |
| **§10 six passes** | Six briefs, every objection dispositioned. One weakened the paper's central claim; four produced measurements; four were dismissed with reasons. | ~1.5 h |

### The honest test, taken

`PLAN-STRONG-ACCEPT.md` §10 asks for the strongest rejection letter the author
can write, and §11 above sets the target: *a rejection letter whose only
remaining clauses are the four items in §0.5.* Here is the strongest one
available now.

> The manuscript is careful and its artifact is unusually strong. It is not
> ready. **(a)** The central empirical claim — that the choices move the
> answer by more than the effect — is established on one log and, on the
> other two, the baseline axis moves it by *less* than the effect. **(b)** The
> audit's primary numbers rest on twenty papers read by a single author, whose
> own mechanical instrument disagrees with that reading on 39 codes. **(c)**
> The prospective test scored two pairs, both negative, so the rule's positive
> half is untested. **(d)** There is no deployment, no partner, and a single
> unaffiliated author.

**Three of those four clauses are sentences the paper writes about itself**,
and the fourth is §0.5's. That is not the target §11 set — the target was a
letter containing *only* §0.5's four items, and (a), (b) and (c) are about
contribution and scope. **The plan did not finish.**

What it did instead is worth stating precisely, because it is not nothing: at
the start of this round those three clauses were true and unstated, and a
referee would have had to find them. Now the paper states each of them, in the
referee's own terms, with the measurement that establishes it. A reviewer who
writes that letter is quoting the manuscript.

### What the next round should not repeat

- **Do not enlarge the audit's frame.** Its constraint is the twenty papers
  read, not the six hundred enumerated.
- **Do not re-open the held-out logs.** They are spent, and
  `r42_new_since.csv` shows there is nothing else yet.
- **Do not chase the page target by cutting a section that carries a claim.**
  `submission/DECISIONS.md` §16 names the four pages that would go next and
  why they have not.

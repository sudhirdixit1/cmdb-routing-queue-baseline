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

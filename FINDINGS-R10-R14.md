# New evidence, r10–r14 (2026-08-20)

Run in response to a referee report on the 2026-08-19 draft. Five scripts,
each answering one numbered objection. Two of them changed what the paper is
allowed to say.

## r10 — three estimator families (objection: one estimator)

The item column is re-represented as a single cross-fitted target-encoded
column, which makes the dimensionality confound vacuous and makes histogram
boosting usable.

| estimator | intake rung | +queue rung | shrinkage |
|---|---|---|---|
| E1 one-hot logistic (the paper's) | +0.1835 | +0.1033 | 43.7% |
| E2 logistic, item target-encoded | +0.1796 | +0.1029 | 42.7% |
| E3 hist. boosting, item target-encoded | +0.1734 | +0.0918 | 47.1% |

Encoder-leak control: a *shuffled* item column encodes to −0.0001 ± 0.0016
under E2 and +0.0042 ± 0.0020 under E3. E3's null is small but genuinely
positive and is disclosed rather than rounded away.

**Verdict: the objection is dead.** Under E2 and E3 adding item identity adds
one column, not 2,554, so there is no regularisation burden for the effect to
be an artifact of.

## r11 — what the gain buys, and the target's definition

Test window 2014-02-03 to 2014-03-31: 13,637 incidents, 56 days, 1.8 months.

At a fixed review capacity, extra reassignment-bound incidents surfaced by
adding item identity:

| capacity | honest baseline (intake+queue) | naive baseline (intake only) | overstatement |
|---|---|---|---|
| 5% | +56 | +303 | 5.4× |
| 10% | +34 | +432 | 12.7× |
| 20% | +34 | +501 | 14.7× |

**This is the strongest new result.** The operational overstatement (12.7× at
10% capacity) is far larger than the ratio of the two AUC gains (1.8×),
because AUC averages over all operating points while a capacity-limited desk
works at one, near the top of the ranking where the queue-aware baseline is
already close to its ceiling.

Target threshold ladder — the magnitude moves, the shrinkage does not:

| target | rate | intake | +queue | shrinkage |
|---|---|---|---|---|
| ≥1 reassignment | 37.2% | +0.183 | +0.103 | 44% |
| ≥2 | 21.8% | +0.131 | +0.068 | 48% |
| ≥3 | 10.6% | +0.151 | +0.080 | 47% |

Non-monotone in magnitude; every interval excludes zero; shrinkage 44–48%.

## r12 — the queue/item relationship without a model

Model-free, so the mechanism does not rest on the one estimator.

- U(queue | item) = **60.4%**; U(item | queue) = 19.6%. Strongly asymmetric.
- Modal-queue lookup: 90.3% raw test accuracy — but the constant guess scores
  78.6%, and class-balanced the lookup reaches only **34.1%**.
- 2,060 of 2,554 items route to exactly one queue, but they are the rare ones:
  together only 8.8% of incidents.

**This forced a correction.** The draft said "the routing decision is very
nearly a function of the affected item." The model-free evidence does not
support that strength. What is supported: the queue's *predictive content for
this target* is nearly absorbed by the item (91% retained under within-item
randomisation, unique contribution < 0.01 AUC), and item identity resolves the
*coarse* routing contrast far better than the fine one.

## r13 — the shape of the free field

Turned up by r12 and not looked at in any earlier draft.

- The queue is **not** 50 comparable groups. Training: 49 groups, perplexity
  **5.4**, top group **62.1%**. Test: 32 groups, perplexity **2.8**, top group
  **78.6%**. The field drifts hard across the split.
- Reassignment rate inside the dominant pool 0.309, outside 0.603.

Ladder with the queue coarsened — a clean dose-response:

| queue variant | levels | queue gain | item gain | shrinkage |
|---|---|---|---|---|
| binary: main pool vs rest | 2 | +0.050 | +0.133 | 27% |
| top 3 + tail | 4 | +0.049 | +0.133 | 28% |
| top 10 + tail | 11 | +0.066 | +0.117 | 36% |
| full queue | 49 | +0.082 | +0.103 | 44% |

A single binary flag recovers 61% of the queue's gain and 63% of the
shrinkage. The graded shape is what a proxy story predicts and a coincidence
does not — better evidence than any single number.

## r14 — scoping, and a correction to the referee

The referee asked us to explain a flat between k=16 and k=32 in the scoping
curve. **There is nothing to explain: the flat is split-specific noise.** Two
candidate mechanisms were tested and both are false — ranks 17–32 have the
joint-*largest* departure from the pool rate (0.207), not the smallest, and
the *highest* train-to-test rate correlation of any band (0.93).

At k=32 the across-split range is [67%, 76%], a 9-point spread; a one-point
dip between adjacent k on one split carries no information. An earlier version
of this script printed a conclusion its own table contradicted — the defect
`r7_final.py` is retained as a record of — and it was rewritten.

Curve averaged over five splits, baseline intake+queue:

| top k | % of vocabulary | % of incidents | recovered |
|---|---|---|---|
| 8 | 0.3% | 30% | 56% [53, 58] |
| 64 | 2.5% | 70% | 88% [82, 92] |
| 128 | 5.0% | 82% | 93% [91, 95] |

Holds with the queue removed (89% at k=64), so it is a property of the
estate's concentration, not of the field-admission decision.

## What changed in the paper as a result

1. Mechanism claim softened — "the routing decision is nearly a function of
   the item" is not supported at that strength; the predictive-content claim
   is.
2. Queue concentration and drift now disclosed. The paper previously said "50
   groups" without qualification.
3. Scoping figures replaced with split-averaged ones and intervals; the old
   single-split numbers (57.9 / 90.0 / 95.4) were over-precise.
4. Target renamed from "misrouting" to "reassignment" throughout.

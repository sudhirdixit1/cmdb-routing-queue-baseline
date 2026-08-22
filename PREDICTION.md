# Pre-registered prediction: where the admissibility reduction will appear

**Registered:** 2026-08-22, round eighteen
**Registered by:** committed to `round-eighteen-reviewer-proof` **before** any
held-out log was downloaded, parsed, inspected or counted. The commit that
adds this file adds no result file from any held-out log. `git log --stat` is
the evidence.

**Why this exists.** Round seventeen ended with an *explanation*: the
admissibility reduction appears where the opening field carries information
and not where it is nearly constant. That explanation was written after seeing
the corpus, and an explanation written after seeing the data is worth very
little. This document turns it into a rule with no free parameter, fixes the
parameter numerically from the round-seventeen logs, and states what will
falsify it — before the logs it will be tested on have been opened.

**This project has exactly one opportunity to make that trade, and this is it.**

---

## 1. The held-out set

Never opened by this project. `PROTOCOL.md` §2 records the first two as
considered and not included, for size and parsing cost respectively, in round
seventeen and before any of this was contemplated.

| key | log | domain | DOI |
|---|---|---|---|
| `BPIC11` | BPI Challenge 2011, a Dutch academic hospital | healthcare | `10.4121/uuid:d9769f3d-0ab0-4fb8-803b-0d1120ffcf54` |
| `BPIC18` | BPI Challenge 2018, EU agricultural subsidies | agriculture | `10.4121/uuid:3301445f-95e8-4ff0-98a4-901f1f204972` |

**The rule protecting them.** Nothing in this repository has parsed, loaded,
inspected or counted either file. `data/normalized/` contains no
`BPIC11.parquet` or `BPIC18.parquet` at the moment this file is committed, and
`results/` contains no `r43_holdout*.csv`. `scripts/r42_holdout_fetch.py`,
which downloads them, is committed *after* this file.

**Logs published on 4TU.ResearchData after 2026-08-21.** `r42_holdout_fetch.py`
enumerates them through the 4TU API and records the enumeration in
`results/r42_new_since.csv`. They are **not** opened: the enumeration records
identifiers and dates only, so that a later round has a held-out set this round
did not burn.

---

## 2. The rule

For a log admitted by `PROTOCOL.md` §3–§4, with the registered roles $B_0$,
$f$, $g$ and either registered target:

> $R$ will be **resolvably positive** iff
> **(i)** $V(f \mid B_0)$ is resolvably positive — its paired-bootstrap 2.5th
> percentile exceeds zero — **and**
> **(ii)** the opening field $g$ clears a threshold fixed below.

Condition (i) is not fitted. It is a definitional precondition: where $V(f \mid
B_0)$ is not resolvably positive the reduction has no denominator, and
`PROTOCOL.md` §1 already refuses to report a ratio whose denominator crosses
zero. Ten of round seventeen's nineteen pairs fail it.

Condition (ii) is the substantive half, and **two forms of it are registered**,
for a reason §3 states in full.

### Rule E — the form `PLAN-REVIEWER-PROOF.md` §4.2 names

> (ii-E) the **normalised entropy of the opening field** $g$, computed on the
> opening value of every trace as $-\sum_v p_v \ln p_v / \ln k$, exceeds
> $H^{*}$.

$$\boxed{H^{*} = 0.331293}$$

### Rule L — the form the round-seventeen data actually supports

> (ii-L) the **incremental AUC of the opening field over the intake block**,
> $V(g \mid B_0) = \mathrm{AUC}(B_0 \cup \{g\}) - \mathrm{AUC}(B_0)$ on the
> test half, exceeds $V^{*}$.

$$\boxed{V^{*} = 0.013302}$$

Both thresholds are **frozen**. Neither is re-fitted, re-centred or rounded
after a held-out log is opened. `results/r43_hstar.csv` carries both, was
written before this file, and `r43_holdout_test.py` reads them from that file
rather than from a literal.

### How the thresholds were fitted

`python scripts/r43_holdout_test.py --fit`, on the nine round-seventeen pairs
that satisfy condition (i). The threshold is the **smallest** midpoint between
consecutive sorted unique values of the discriminator that maximises balanced
accuracy. The tie-break is stated in the code rather than left to a sort
order.

---

## 3. What the fit already shows, and why two rules are registered rather than one

**Rule E, the rule the plan named, barely beats chance on the data it was fitted
to.** In-sample: 4 true positives, 4 false positives, 1 true negative, 0 false
negatives; balanced accuracy **0.600**. $H^{*} = 0.331293$ is, in substance,
"every log except Sepsis". The flagship log — BPI Challenge 2014, where the
effect is largest — has the *second lowest* normalised entropy of the nine.
Normalising by $\ln k$ is what breaks it: BPI Challenge 2014's opening group
has 57 values with a heavy skew, and BPI Challenge 2015's has seven values
spread evenly, so the normalisation ranks the second above the first.

**Rule L separates the nine pairs perfectly**: 4 true positives, 0 false
positives, 5 true negatives, 0 false negatives; balanced accuracy **1.000**.
It is also the form the mechanism implies. $R$ measures how much of $f$'s value
$g$ absorbs, and a field that is worth nothing over the intake block cannot
absorb anything.

**Rule L was chosen after seeing that Rule E fails in sample.** That is stated
here, in the registration, rather than discovered by a referee. A rule selected
on the training data can only be tested on data it was not selected on, which
is exactly what §5 does. Both rules are frozen; both are scored; neither is
dropped after the answer is known.

**A limit no threshold can pass.** BPI Challenge 2013 incidents appears twice
in the fitting set with the same $g$ and therefore the same value of every
log-level discriminator, and its reduction is resolvable on one target and not
the other. **No rule that reads only log-level properties can be perfect**, and
Rule L achieves 1.000 in sample only because the two pairs happen to fall on
opposite sides of $V^{*}$ through their *target-level* $V(g \mid B_0)$. Rule E,
whose discriminator is target-independent, cannot separate them even in
principle. That asymmetry is a property of the two forms and is reported.

---

## 4. The scoring

For each held-out log and each registered target, the rule predicts one of
three outcomes **before the log is opened**:

- **resolvable** — condition (i) and condition (ii) both hold;
- **not resolvable** — either fails;
- **excluded** — `PROTOCOL.md` §4.4 assigns the pair an exclusion code
  (`NO_G`, `NO_F`, `NO_B0`, `SMALL_N`, `NO_HEADROOM`, `NO_TEST_VARIATION`).

Excluded pairs are reported with their code and are **not** scored: an
exclusion rule is not a prediction, and counting exclusions as correct
predictions would be the cheapest possible way to win this test.

`results/r43_confusion.csv` reports, per rule, the 2×2 confusion matrix over
scored pairs and the count of errors.

### What falsifies each rule, stated in advance

The held-out set can yield at most **four** scored pairs — two logs, two
targets — and fewer if either log is excluded. **This test has very low power
and that is stated here rather than discovered in review.**

> A rule is **falsified** if it errs on **more than one** scored pair, or if it
> errs at all on a pair where $R$ is resolvable and the rule said it would not
> be (a false negative is the expensive error: the rule's job is to say where
> the effect appears).
>
> A rule **survives** if it errs on no scored pair.
>
> A rule is **untested** if fewer than two pairs are scored, and the paper
> reports it as untested rather than as passed.

### What a failure means, written down before it can happen

If a rule fails, the paper reports the failure, drops the condition to a
**post-hoc observation** — which is what it is today — and says so in the
section that currently states it as a mechanism. That is a smaller paper and an
honest one. If Rule E fails and Rule L survives, the paper says both, and says
that Rule L was chosen after Rule E failed in sample.

**If both rules fail, §11 of the manuscript loses its mechanism paragraph and
the corpus section reverts to a bare negative.** That outcome is acceptable and
it will not be dressed up.

---

## 5. The procedure, in order

1. `python scripts/r42_holdout_fetch.py` — download by DOI, record SHA-256,
   enumerate 4TU datasets published after 2026-08-21 without opening them.
2. `python scripts/r43_holdout_test.py` — parse each held-out log with
   `r32_corpus.parse_xes`, assign roles with `r33_generic_ladder.assign_roles`,
   build both targets with `r33_generic_ladder.targets`, fit with
   `r33_generic_ladder.fit`, and bootstrap with
   `r33_generic_ladder.boot_reduction`. **Every one of those is imported, not
   re-implemented**, and `test_holdout_uses_protocol_code()` asserts at run
   time that none of them is shadowed in `r43`.
3. Nothing about `PROTOCOL.md` changes for the held-out logs. That is the whole
   point of the exercise, and any amendment made after a held-out log is opened
   invalidates the test and must be reported as invalidating it.

---

## 6. Changes to this document after registration

Any change is appended below with its date and reason, and the original text
stays. Nothing is edited in place. **A change to $H^{*}$ or $V^{*}$ after a
held-out log is opened voids the prediction**, and the paper would have to say
so.

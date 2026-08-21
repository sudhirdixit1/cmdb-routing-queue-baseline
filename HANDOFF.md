# HANDOFF

For whoever picks this up next. **Start at §19 (round sixteen).** It is the
current state; everything before it is history, some of it retracted
history. Then read §4 (withdrawn findings) — that is the part that will
save you time.

**§§1–18 were written earlier and much of §§1–5 is now WRONG.** The paper is
no longer a single-organisation study, is no longer aimed at IAAI, is no
longer six pages, and no longer reports the operational factor §1 quotes.
Where an earlier section conflicts with a later one, the later wins. Where
anything conflicts with §19, §19 wins.

**One-line summary of where this is:** a 33-page Elsevier `elsarticle`
manuscript targeted at *Information Systems*, with 674 verified numeric
claims, a 149-corruption regression suite the verifier now passes cleanly,
five figures, a one-command reproduction script, and a submission package.
What is left needs the author's credentials, not another revision round —
see `submission/OWNER-ACTIONS.md`.

---

## 1. What this is

A single-organisation empirical study for **IAAI-27, Deployment Insights
track**. Deadline **8 September 2026** (AAAI's page; the OpenReview listing
showed 9 September — treat the earlier as binding). Review is not anonymous.

**The surviving claim, in full:**

> On the BPI Challenge 2014 incident log (Rabobank Group ICT, 45,455
> incidents), knowing which configuration item an incident concerns is worth
> **+0.183 AUC** for predicting reassignment when measured against four
> intake fields, and **+0.103 [+0.094, +0.113]** when the baseline also
> includes **the group that logged the incident** — a field recorded for free
> at intake. The measured value of a CMDB is therefore dominated by a
> field-admission decision that is usually left implicit.

Plus a mechanism: the group's *predictive content for this target* is largely
carried by the item (randomising the group label within each item retains
**91%** of its gain, against an item-level floor of **41%** at matched
cardinality — see §12.2), and the group's unique contribution once the item
is known is **under 0.01 AUC**.

Three corrections are reported *in the paper* rather than edited away: a null
that could not fail, an operational factor first printed without an interval,
and the field's meaning. See §12.

⚠️ **Two things in this section were wrong until 2026-08-20** and are fixed
above: the field is NOT "the opening assignment queue" (it is the group that
logged the ticket — §12.1), and the mirror floor is NOT 2% (§12.2).

Everything else that was ever claimed has been withdrawn. See §4.

---

## 2. Where things are

```
emptycmdb/
  paper/iaai27_empty_cmdb.tex   the draft (3 figures, 2 tables, 22 refs)
  paper/references.bib          22 entries, all author lists verified
  scripts/                      see below
  results/                      every CSV the scripts produce
  FINDINGS-R10-R14.md           what round seven added, and walked back
  README.md                     reproduction instructions
```

Raw data lives in `data/raw/` (gitignored). It needs `Detail_Incident.csv`,
`Detail_Change.csv` and `Detail_Incident_Activity.csv` from BPIC 2014
(`doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35`), plus
`incident_event_log.zip` (UCI 498) and `BPI_Challenge_2013_incidents.xes.gz`
for `r15`. All public; none redistributed.

### Scripts that matter

| file | role |
|---|---|
| `common.py` | loaders, missing-token handling, paths |
| `r4_final.py` | **the canonical loader.** Cohort, baselines, stability, mutation disclosure. Everything else imports `r4_final as M` |
| `r5_final.py` | nulls, mutation sensitivity, leak evidence |
| `r6_final.py` | gains with pooled uncertainty |
| `r8_final.py` | mechanism, design-space range, deployment scoping. **§B's floor is superseded by `r17`** |
| `r10`–`r17` | estimators, operational framing, field semantics, rebuilt floor — see §11, §12 |
| `verify_paper.py` | checks every number in the paper against a result file |
| `attack_verifier.py` | regression suite for the verifier — 54 corruption classes |
| `texlint.py` | structural LaTeX lint; `--fix` repairs row terminators |

### Scripts that are dead weight

`e1`–`e16`, `r1`–`r3`, `r7`. They implement withdrawn analyses. Kept so the
withdrawals are auditable. **Nothing in the paper depends on them.**
`r7_final.py:124–148` in particular prints a conclusion its own output CSV
contradicts — it is retained deliberately as the record of a failed control.
Do not reuse code from these without re-deriving why it was abandoned.

---

## 3. How to check the current state

⚠️ **These counts are round-eight's and are stale.** Current, and the only
command you need:

```
python scripts/reproduce_all.py    # everything, in dependency order
```

Individual stages, if you want them:

```
python scripts/texlint.py          # must exit 0 before anything else
python scripts/verify_paper.py     # 674 checks, 0 failed, 0 unaccounted
python scripts/attack_verifier.py  # 149 caught, 0 missed, 0 skipped
python scripts/build_journal.py    # 33 pages, 0 errors, 0 undefined refs
```

`verify_paper.py` runs `texlint` first and refuses to proceed on a document
that would not compile. If you change a number in the paper, the verifier
will fail until you change the corresponding check — that is the intent.

---

## 4. Eight withdrawn findings — READ THIS

Every one was an artifact of a control we built ourselves, and **every one
erred in the direction that flattered the result.** Six adversarial review
rounds found them. If you propose a new control, assume it is wrong until
you have nulled it.

| # | Claim | Why it died |
|---|---|---|
| 1 | "Service layer carries the capability, CI adds 10%" | Artifact of feature **entry order**. Reversing the order reversed the conclusion |
| 2 | "The CMDB taxonomy is worthless" | Random baseline matched on **nominal** cardinality, not effective. `CI Type` has 13 labels but perplexity 2.7 |
| 3 | "Real taxonomies beat matched-random" | The "mass-matched" null **did not match mass** — `searchsorted` let high-mass items swallow boundaries, leaving empty cells |
| 4 | "Class hierarchy costs −0.004" | Regularisation burden of ~330 **collinear** columns at fixed `C`. `CI Type`/`CI Subtype` are deterministic functions of `CI Name` (0 of 2,929 items vary) |
| 5 | "Recovery tracks coverage, R²=0.94" | Linear fit with **positive intercept** predicting recovery at zero coverage and >100% at full |
| 6 | "The rules converge above 55% coverage" | Two-rule comparison reported as three. Uniform-random tops out at ~40% coverage and has no points above it |
| 7 | "The decomposition closes to 0.0004" | The quantity is an **algebraic identity** — `(Aᵢ−A₀)−(A_qi−A_q) ≡ (A_q−A₀)−(A_qi−Aᵢ)` — restated by Monte Carlo. Its agreement's bootstrap interval was 11× the agreement |
| 8 | "44% of the item's signal is the queue" | A **random 50-cell grouping of items** retains more (54%) than the real queue (44%). Defensible nulls disagree on the floor |

**The lesson that actually generalises:** "this comparison is already in the
experimental design, so it needs no null" is false. That reasoning is what
let #4 through. Every comparison — constructed or in-design — needs to be
checked for the confound it introduces.

**What has survived every attack so far:** the **+0.103** headline — outside
a matched-dimension null, stable across six splits, three cleaning cutoffs,
four penalty settings, mutation restriction, and (round seven) three
estimator families including one where item identity is a single column.

⚠️ **The second item on this list did not survive.** It read "the 91% / 2%
mirror (89-point margin over its floor)". The 2% floor was drawn at row level
and could not fail; the honest margin is ~50 points against an item-level
floor at matched cardinality, and it varies with granularity. See §12.2. The
91% retention itself stands.

*Correction (2026-08-19).* An earlier version of this line claimed the
headline survived "two estimator families." It does not: the surviving
pipeline (`r4`/`r5`/`r6`/`r8`) uses one-hot logistic regression **only**.
Gradient boosting appears exclusively in the withdrawn `e*` and `r1`
scripts, on the pre-queue-baseline framing. `r5_final.py` REPAIR 6 computes
why boosting is not usable here — 2,554 items collapse into 137 bins — and
that justification belongs in the paper, which currently states the
one-estimator limitation without giving the reason.

*Corrected 2026-08-20.* This line said **256** bins until round seven. 256
is `max_bins`, the *parameter*; `r5_binning.csv` computes 137 actual
distinct bins, and the wrong figure had reached the paper. **Also
superseded**: §11 records that `r10_estimators.py` removed the
one-estimator limitation entirely rather than justifying it — target
encoding makes the item one column, which makes both a second logistic
specification and boosting usable, and all three agree on the shrinkage.

---

## 5. The verifier has been rebuilt four times

Each version shipped with a hole a reviewer found. Do not weaken it.

| version | hole |
|---|---|
| v1 | Stripped comments with `re.sub(r"%.*")`, so an **escaped** `\%` ate the rest of the line — 38 literals never scanned |
| v2 | **Substring** containment: a fabricated `737` hid inside `466{,}737` |
| v3 | Over-normalised registration (stripped a leading `.`), freeing bare `172`, `195`, `094` from the CI bounds. Also still substring for the in-paper test, so `"47"` matched `47.53`. **5 of 7 fabrications passed** |
| v4 | Proximity, not position: **22 of 42** corruptions passed by changing a value in one place while the literal survived elsewhere. Signs were invisible to the tokeniser |

Current design: sign-aware tokeniser, exact set membership only, **mandatory**
anchor phrases, exact-phrase pinning for ordered pairs and values repeated
between abstract and body, and a structural lint gate. If you add a claim to
the paper, add a `ck(...)` with an anchor, and add a corruption to
`attack_verifier.py`.

---

## 6. Outstanding

**Done on 2026-08-19** — author block (Sudhir Dixit, Independent Researcher,
personal email; solo author), acknowledgements, AI-disclosure section,
repository URL, and the first successful compile. See §9.

**Still needs the author:**

- **Push the repo.** `git init` and the first commit are done locally, but
  the GitHub remote does not exist yet and creating it needs credentials an
  agent must not handle. The paper already cites
  `github.com/sudhirdixit1/cmdb-routing-queue-baseline`, so that URL is a
  dead link until the repo is created and pushed
- **Name the practitioner** in the Acknowledgements if they consent. The
  section currently credits them unnamed because no name is recorded
  anywhere in this repository, and inventing one is not an option
- **Read the AI-disclosure section and confirm it describes your process.**
  AAAI permits LLM use for "editing or polishing author-written text" but
  prohibits papers containing LLM-*generated* text except as experimental
  analysis, and requires the role of any AI system to be documented. The
  disclosure as written documents assistance in code, adversarial review,
  and drafting. Whether that is the right characterisation is a factual
  claim about your process, and sanctions attach to getting it wrong
- Employer publication clearance, if your employment agreement covers
  publishing in this domain — the affiliation is independent, but that does
  not by itself settle the obligation

**Optional:**

- A CSDM/ITIL reference. Marked optional in `references.bib` because the
  paper no longer leans on CSDM — those maturity claims were withdrawn
- Move `r5_final.py` REPAIR 6's binning computation into the Limitations
  section, to justify the single estimator family rather than just concede it

---

## 7. Working notes

- **Shell heredocs mangle backslashes.** Several LaTeX edits were corrupted
  this way, including the broken table that made the paper uncompilable.
  Write a `.py` file and run it; do not patch `.tex` through `bash <<'PY'`.
- **`groupby.first()` is column-wise first non-null**, not first row. It is
  safe here only because the `Open` activity rows have zero nulls and zero
  timestamp ties — both verified. Do not assume that elsewhere.
- **`np.std` defaults to `ddof=0`** and Monte-Carlo dispersion at 30 draws
  has ~13% relative error. Two significant figures on a null's sd are not
  earned.
- **A test that silently no-ops looks exactly like a passing test.** One
  corruption suite reported PASSED because the search string spanned a LaTeX
  line break and the replacement never fired. `attack_verifier.py` now
  reports SKIP separately and exits non-zero on it.
- Cross-script consistency has been checked: `r4`/`r5`/`r6`/`r8` agree to
  ~10 decimals on shared quantities.

---

## 8. If you are asked to make it bigger

Resist adding a fourth contribution. Six review rounds reduced this from
four claims to one plus a mechanism, and every reduction came from a claim
that could not survive its own null. The paper is thin because the evidence
is thin, and the honest version is the publishable one.

If more substance is genuinely wanted, the defensible directions are:
replicate on a second organisation's log (the ServiceNow UCI log and BPIC
2013 were both used and dropped for good reasons — see `e1`–`e16` — but a
*fresh* instance would be real), or measure a second prediction task on this
log with the same baseline discipline.

---

## 9. The paper now compiles — and the build caught four real defects

Built 2026-08-19 with MiKTeX 25.12 against the official AAAI-27 author kit.
**3 pages against a 6-page limit** (references and appendices are unlimited
per the CFP), 0 errors, 0 undefined references, 1 overfull hbox of 5.06pt.
Reproduce with `python scripts/build_paper.py`, which fetches the kit itself.

Everything below passed `texlint` and `verify_paper` beforehand. A structural
lint is not a build:

1. **The kit ships `aaai2027.sty`/`.bst`, not `aaai27.*`.** The preamble named
   the short form. It would not have resolved.
2. **`aaai2027.sty` issues its own `\bibliographystyle`.** The document had a
   second one, which makes bibtex die with *"Illegal, another `\bibstyle`
   command"* — and bibtex's failure does not stop pdflatex, so this fails
   quietly and ships a paper with unresolved citations.
3. **`\usepackage{times}` is explicitly forbidden** by the style file, which
   loads `newtxtext`, `helvet` and `courier` itself and owns the page size.
   The preamble loaded all three plus `pdfpagewidth`/`pdfpageheight`.
4. **`secnumdepth` defaults to 0** in the AAAI template, but the body
   cross-references sections by number, which silently yields wrong numbers.
   Now set to 2.

Also removed: two `note` fields in `references.bib` that were private
research annotations and rendered into the printed reference list — one of
them read "the closest prior statement of this paper's thesis in another
domain."

**Note for the next agent:** `texlint.py` scans raw source without stripping
comments, so a `\ref{...}` written inside a `%` comment is reported as an
undefined label. That is the lint being conservative, not a bug. Reword the
comment; do not weaken the check (see §5).

---

## 10. The second task (r9) — a claim that survived

`r9_second_task.py` repeats the baseline ladder on two further targets,
which §8 named as one of the two defensible ways to add substance. It
holds the cohort, split, estimator, intake block and null construction
fixed and changes only what is predicted.

| target | corr. with reassigned | gain, intake | gain, +queue | shrinkage |
|---|---|---|---|---|
| reassigned | — | +0.183 | +0.103 | 44% |
| reopened | +0.14 | +0.083 | +0.055 | 33% |
| long-handling | +0.40 | +0.118 | +0.078 | 34% |

Every rung on every target is outside its matched-dimension null. Across
five split points the shrinkage ranges 30–46%.

**Read the caveats before quoting this.** Reopening is the only near-
independent target and it is rare: its two gains are 5.5 and 4.2 pooled sd
from their nulls, against 28.1 and 17.4 for reassignment. It establishes
the *direction*, not the size. Long-handling correlates +0.40 with the
primary target, so it is corroboration, not independent evidence. Both
caveats are in the paper; do not let a later draft quietly promote them.

**Cross-script note.** `r9` draws its null 50 times, `r6` 100 times, so the
two disagree on the pooled z of the one row they share (r6: 28.1, r9:
~27.4). Monte-Carlo dispersion, not a data disagreement — the gain agrees
to ten decimals. The paper quotes r6 for that row and r9 only for the new
targets, so no quantity appears twice with two values.

### Figures

`r9_figures.py` writes three. `figG3_overlap.png` is area-faithful: the
circle areas are the two measured gains and the centre distance is solved
with `brentq` so the intersection equals the measured overlap. If you
change the numbers, re-run it rather than editing the picture.

`figG1` is a `figure*`. Its artwork is 6.9in wide; at `\columnwidth`
(3.31in here) it rendered at 48% and its 9pt labels came out near 4pt.

### Verification

Now **127 checks** and **21 corruptions**, both extended for r9. The
residue guard caught the phrase "mass-matched" re-entering via a new figure
caption — that phrase is banned because withdrawn finding #3 was a null
that did not match mass. Reword; do not delete the guard.

---

## 11. Round seven (2026-08-20): the referee round

A full referee report was produced against the 2026-08-19 draft and worked
through. Five new scripts, `r10`–`r14`. Full detail in `FINDINGS-R10-R14.md`;
this section records only what a future agent must not undo.

### What got stronger

- **Three estimator families, not one.** `r10_estimators.py` re-represents
  item identity as a single cross-fitted target-encoded column. That makes
  the dimensionality confound *vacuous* rather than merely controlled — the
  item is one column, not 2,554 — and makes boosting usable. Shrinkage is
  43%/43%/47% across the three. The single-estimator limitation is gone.
- **A detection framing.** `r11_operational.py`. At 10% review capacity the
  queue-free baseline credits item identity with 432 extra catches where the
  queue-aware one credits 34: **an overstatement of 12.7×**, against only
  1.8× on AUC. This is now the abstract's second headline and it is the most
  practitioner-legible thing in the paper.
- **A dose-response.** `r13_queue_shape.py`. Shrinkage runs 27%, 28%, 36%,
  44% as the queue goes from 2 to 49 levels. A graded response is much
  better evidence for a proxy story than any single number.

### What got WEAKER, and must stay weak

Two claims were overstated in the 2026-08-19 draft and are now corrected.
**Do not let a later draft quietly restore them.**

1. **"The routing decision is very nearly a function of the affected item."**
   Not supported. Model-free (`r12`): U(queue|item) is 60.4%, not 91%; the
   modal-queue lookup scores 90.3% raw but the constant guess already scores
   78.6%, and class-balanced the lookup reaches **34.1%**. The supported
   claim is about the queue's *predictive content for this target*, and about
   the *coarse* routing contrast — not about determination.
2. **The scoping figures.** The old 57.9 / 90.0 / 95.4 were one split's
   curve. Split-averaged they are 56 / 88 / 93 with ranges [53,58], [82,92],
   [91,95]. Quote the averaged ones with the range.

### A defect this round reproduced, and the fix

The first version of `r14_scope.py` printed an explanation for the k=16→k=32
flat in the scoping curve — and its own table contradicted it. That is
exactly the `r7_final.py` failure mode this file warns about, reproduced by
an agent that had read the warning. The flat is **split-specific noise**: the
across-split range at k=32 is 9 points. Two candidate explanations were
tested and both are false (ranks 17–32 have the joint-*largest* departure
from the pool rate and the *highest* train-to-test correlation).

Lesson to carry: a plausible mechanism you have not tested is not an
explanation, and a curve read at one split is not a curve.

### A real number error the verifier caught

The draft said histogram boosting collapses 2,554 items into **256** bins.
256 is the `max_bins` *parameter*. `r5_binning.csv` computes **137** actual
distinct bins. Section 4 of this file had propagated the wrong figure.
Fixed, and `attack_verifier.py` now contains "restore the wrong bin count"
so it cannot come back.

### Verifier

Now **224 checks** and **44 corruptions**. The suite found two live holes in
the new checks — swapped pairs sharing a sentence (the 60.4/19.6 asymmetry
and the 0.309/0.603 pool rates), which anchoring alone cannot separate
because each anchor sits inside the other's window. Both are pinned with
`ck_phrase` now. **Any ordered pair you add needs the same treatment.**

### Still needs the author

- **Read `\section*{Use of AI Systems}` and confirm it describes your
  process.** It was removed in commit `b4aded4` and has been restored,
  because AAAI permits AI use in developing a publication *only if its role
  is documented in the manuscript*, and `HANDOFF.md` — this file — is public
  in the repository the paper cites for reproducibility, is addressed to
  agents throughout, and a single-blind reviewer can follow that link. The
  restored text is a good-faith description based on what this repository
  evidences. Only you know whether it is accurate, and sanctions attach to
  getting it wrong. Edit it or remove it, but do not leave it unread.
- **Name the practitioner** in the Acknowledgements if they consent.
- **Consider offering them co-authorship.** The CFP recommends co-authors
  from the deploying organisation and it is the cleanest answer to the
  "no deployment" objection. Weigh against a solo-authorship preference.
- Employer publication clearance, if applicable.

---

## 12. Round eight (2026-08-20): the referee found three real defects

An independent referee reviewed the round-seven draft and returned **weak
reject, 5/10**. Three findings were substantive and all three were confirmed
by re-derivation. Two are now reported *in the paper* rather than edited away.

### 1. The central field was not what we said it was

The paper called the `Open`-row Assignment Group "the queue the service desk
routed it to." **It is the group that logged the incident.** Evidence
(`r16_field_semantics.py`):

| check | value |
|---|---|
| distinct groups, `Open` rows vs `Assignment` rows | 50 vs 218 |
| dominant group's share of `Open` rows vs all rows | 67.0% vs 18.4% |
| `Open` group == first `Assignment` group | 15.1% |

A routing destination cannot be less diverse than the teams doing the work.

**The natural repair is not available**, and this is now a result rather than
a footnote: the first `Assignment` occurs strictly after `Open` on every
incident that has one (median 46 min), and 7,878 of 45,455 never have one.
It fails the paper's own admissibility criterion. Substituting it would
introduce exactly the leakage that criterion exists to prevent.

**No measured number changed.** The field is still on the intake event, still
100% populated, still free, still absorbs 44%. What changed is the title and
every sentence that described the field's meaning.

### 2. The mechanism's floor could not fail — fourth time at this

`r8_final.py:118` drew cell labels **per row**, so two incidents sharing an
item landed in different cells. Shuffling within those cells destroys the
association by construction; the null could only return ~0. The published
"retains 2%, margin 89 points" was not a measurement.

Worse: **the same script already does it correctly** in section C, for the leg
it *drops*. The surviving leg got the permissive null and the dropped leg the
strict one.

`r17_mechanism_floor.py` rebuilds it as a random partition **of items**:

| cells | 10 | 49 | 100 | 200 | 400 | 800 |
|---|---|---|---|---|---|---|
| retained | 9% | **41%** | 54% | 69% | 77% | 82% |

Honest margin at matched cardinality: **50 points, not 89** — and it is a
function of a granularity knob, so the paper reports the sweep and claims only
the ordering.

### 3. The operational factor was misconstructed and unresolved

Two defects at once. `r11` used ONE treatment model for both contrasts, so the
"naive" arm credited item identity with the group's own contribution. And the
factor was printed bare in a paper that refuses to resolve +0.0017's third
decimal.

Matched arms + paired bootstrap + random tie-breaking:

| capacity | honest extra | naive extra | factor |
|---|---|---|---|
| 5% | +67 [43, 84] | +262 [242, 300] | **3.9 [3.2, 6.4]** |
| 10% | +33 [6, 70] | +353 [304, 404] | 10.7 [5.5, 39.9] |
| 20% | +18 [−28, 82] | +481 [407, 524] | 26.7 [5.8, 221.0] |

The paper now quotes the **5%** figure because it is the only well-resolved
one, and says why. At 20% the denominator's interval includes zero.

### 4. Three printed digits were wrong, and why the verifier missed them

`+0.114`→`+0.113`, `+0.176`→`+0.175`, `0.0006`→`0.0005`. Two flattered the
claim. Cause: `ck()` compared with `tol=6e-4` against three-decimal literals
when the half-ulp is `5e-4`.

**`ck()` now tests rounding EQUALITY** at the paper's own printed precision
(`_rounds_to`). It immediately caught a fourth case — and that one was a
*false* positive worth understanding: a range's lower bound is **floored**,
not rounded (76.5% justifies "76--100%", and "77" would be false), so that
endpoint gets an explicit bound check instead.

### 5. Live scripts narrating withdrawn conclusions

A referee following the README's reproduce instructions ran the pipeline and
read conclusions the paper disowns. `r8_final.py:162` printed that a random
grouping retains **MORE** than the real one; `results/r8_dropped_leg.csv`
written six lines later says 0.0450 vs 0.0805 — **less**. Also `r4_final.py`
(three sites), `r5_final.py` (three sites). All corrected to state what their
own output says.

**The README's claim that this defect was confined to `r7_final.py` was
false.** Do not assume it is confined anywhere; check.

### 6. Two scripts owned one filename

`r9_figures.py` and `r14_figures.py` both wrote `figG5_scope.png`, so
whichever ran last decided which figure shipped — and only one matched the
caption. `r14_figures.py` is now the sole writer.

### Verifier

**252 checks, 54 corruptions**, 0 failed, 0 unaccounted, 0 missed. Body ends
on page 6; references run to 7.

### What is still open

- **The AI-disclosure section was REMOVED on the author's instruction
  (2026-08-20).** It had been restored in round seven; the author directed
  its removal after review. Two facts that bear on that decision are
  recorded here so a future reader does not have to rediscover them, not to
  reopen it: AAAI's policy permits AI use in developing a publication only
  where its role is documented in the manuscript, and `HANDOFF.md` — this
  file — is public in the repository the paper cites for reproducibility and
  is addressed to agents throughout. If the disclosure is to stay out, the
  repository should be made consistent with that.
- Naming the practitioner; considering co-authorship.
- The repo URL still contains "routing-queue", which the paper no longer
  claims the field is. Renaming would break the cited link; left alone
  deliberately, but worth a decision before camera-ready.
- `Detail_Interaction.csv` was never obtained. Section 8 now says so
  explicitly rather than asserting a limit of the whole export.

---

## 13. Rounds nine and ten (2026-08-20): two more referees

Two further independent reviews. Scores: **5/10 → 4/10 → 4/10**, with
technical soundness moving **6 → 5 → 7**. The third reviewer, having
re-implemented the pipeline from scratch, reported finding *"no fabricated
number, no favourably constructed null, no leakage, and no script whose
output contradicts its own CSV."*

**Read this next part carefully, because it is the conclusion the numbers
support and it is not a comfortable one.** All three reviewers scored **venue
fit 3–4/10** and said it is not fixable by revision. The paper's science is
now in good shape; what holds it back at IAAI is that the track requires a
deployed system and recommends a co-author from the deploying organisation,
and this is a retrospective study on a 2014 public benchmark by a solo
independent researcher. Further rounds of revision will not move that.

### What round nine fixed (the correction had stopped at the prose)

The most damaging single observation: §3 retracted "routing queue" and
**Figure 1 still said "+ routing queue" in the headline figure**. Also three
of four figure cross-references pointed at the wrong panel, and Figure 2 was
never cited. If you make a correction, `grep` the whole repository for the
retracted phrase — prose, figures, CSV row labels, script prints, and the
repository name.

Controls that were missing and are now present:

| gap | what it turned out to be |
|---|---|
| MI figures 60.4% / 19.6% had no floor | shuffling item identity leaves **14.0%** and **4.5%**. A quarter of the headline figure was finite-sample bias. Asymmetry survives, 46 points against 15 |
| `Service Component WBS (aff)` never mentioned | 100% populated, free, and admitting it takes the item's value to **+0.023**. Excluded because only 58 of 2,929 items carry more than one value |
| hour of day / day of week never tested | +0.103 → **+0.099**. The baseline is not a terminus, and the paper now says so |
| the rebuilt floor's ordering | **structural**. At one cell per item the null *is* the real leg, so "beats every floor" is true by construction. Only the matched-cardinality comparison is claimed |

### What round ten fixed

- **The free-field objection.** Every referee raised it; it lived only in
  `r12_queue_from_item.py:4-8` and never in the paper. Now a paragraph in §5.
  The answer that works: the measurement is identical under both readings and
  only the moral changes — and the "it is tacit configuration knowledge"
  reading is *more* useful to a practitioner, not less.
- **Interval provenance, again.** Methods promised every `[a,b]` was a
  bootstrap; the scoping figures were min–max spreads across five splits in
  the same notation. This is the second time an interval-provenance error has
  shipped. Check it whenever you add a bracket.
- **Range endpoints.** Three ranges rounded both ends *inward*, making each
  narrower than the data supports. **A range endpoint floors or ceils; it
  does not round.** `ck_bound()` now enforces this.
- **A real leak.** `r9_second_task.py` fitted the long-handling threshold at
  the 70% split and reused it for the 60% and 65% stability rows, whose
  target definition therefore saw their own test half. Refitted per split;
  the published range moved.

### Two more bugs found while fixing

- `r8_final.py` section C built its train and test partitions from
  **different draws** of the same generator, depressing a floor to 25% where
  the correct value is 55%. That flips the conclusion: a routing-blind
  grouping retaining *more* than the real one is a clean reason to exclude
  the reverse leg.
- `r9_figures.py` and `r14_figures.py` both wrote `figG5_scope.png`.

### The verifier now checks caveats, not only numbers

Three sentences are checked as if they were numbers — the structural-ordering
note, the interval-provenance disclosure, and the free-field engagement —
because **deleting any of them leaves every number correct and the claim
wrong**. That is a class of defect the old verifier could not see. If you add
a load-bearing qualification, add a `ck_phrase` for it.

**281 checks, 65 corruptions**, 0 failed, 0 unaccounted, 0 missed. Body ends
on page 6, 0 overfull boxes.

---

## 14. Round eleven, and the conclusion four referees converged on

Fourth independent review. **Reject for IAAI-27 (10–15%)** — with **technical
soundness 8** and **reproducibility 9**, and the sentence that matters most:

> "It is, on the evidence I could gather, more carefully verified than most
> papers I review. **It is the wrong paper for this venue.**"

### The worst defect in the paper was in its Limitations, and it was mine

The transferable-claims sentence read *"the mechanism is the item column
proxying for the opening group"* — the **exact leg §5 excludes** as
floor-dominated. The paper contradicted itself in the sentence enumerating
what a reader should carry away, and it survived four revisions **because it
contains no numeral**. The verifier could not see it.

That is the general lesson of this round: *every number correct, the claim
wrong* is a real defect class. Seven `ck_phrase` guards now cover the
load-bearing sentences, and `attack_verifier.py` has prose-only corruptions
that were **MISSED** until those guards existed.

### And one I introduced while fixing the previous round

The correction comment I added to `r8_final.py` quoted the **pre-fix**
numbers, so it went stale in the same edit that wrote it — the `r7_final.py`
defect, committed while removing the `r7_final.py` defect. **When a fix
changes an output, re-read the comment you just wrote against the new
output.**

### The rest

| defect | fix |
|---|---|
| "every interval excludes zero" covered three gains with no interval anywhere | narrowed to the `+group` rungs, and the verifier checks the file carries them |
| scope spreads rounded **inward** while every other range rounds outward | 52–58, 81–93, 90–96 via `ck_bound` |
| abstract claimed the choice is "worth as much as the data" (0.080 vs 0.103) | "nearly as much" |
| "(0.66 against 0.39)" was the **mean of two overlapping subgroups** sold as a union rate — and the verifier blessed it by averaging the same two rows | both rows reported separately |
| rebuilt floor reported bare (30 draws, **12 points** of dispersion) | disclosed |
| Table 2's points are one tie-break draw, its intervals average 400 | disclosed |
| the free-field paragraph **endorsed** the reading that would falsify the headline | no longer picks a reading |
| r8 used 50 cells, r18 used 49, so they disagreed on one quoted number | r8 uses the field's own cardinality; both give 56% |
| 21.35% and 92.56% existed only inside the checker | live producers in `r16` |

**292 checks, 71 corruptions**, 0 failed, 0 unaccounted, 0 missed. Body ends
on page 6, 0 overfull boxes, 0 undefined references.

---

## 15. STOP REVISING FOR IAAI. Read this before starting a sixth round.

Four independent referees. Scores: **5, 4, 4, 4**. Technical soundness went
**6 → 5 → 7 → 8**. Venue fit went **4 → 3 → 3 → 3** and never moved, because
it cannot:

- the track states *"Tools must be deployed"*; the paper's second paragraph
  states *"We report no deployed system"*;
- the CFP recommends a co-author from the deploying organisation; there is no
  deploying organisation involved at all;
- the data is a 2013–14 public benchmark.

The fourth referee's verdict on strategy: *"Spending a fifth [revision] on
IAAI-27 is the sunk-cost move."*

**The science is done.** Further rounds will keep finding small things —
they always do — but they will not move the two scores that decide it.

### Where this should go instead

1. **ICPM** (International Conference on Process Mining) or its **BPI /
   ML4PM workshops.** The data *is* a BPI Challenge log, the task is
   textbook predictive process monitoring, and this community owns the
   baseline-specification and leakage problem the paper is about — it
   already cites Weytjens & De Weerdt, who are in exactly this line.
   Single-log studies are normal there. **This is the natural home.**
2. **Empirical Software Engineering (EMSE)** or **MSR.** Journal length would
   un-strangle the three withdrawal sections the 6-page limit is crushing,
   and the artifact would likely earn a badge. A journal article is also
   stronger evidence for the scholarly-articles criterion than a 6-page
   conference paper.
3. **An evaluation/benchmarking venue.** The transferable claim is a
   benchmarking claim, and such venues do not expect a deployment.

### What would actually make this an IAAI paper

Partner with an operator, put a co-author from that organisation on it, run
the ladder against their live CMDB and triage model, and report what their
business case said before the measurement and after. That is a genuinely
valuable IAAI paper nobody has written — and it is a different paper on a
two-year horizon, not a revision of this one.

---

## 16. Rounds twelve and thirteen: the checker's fifth hole was a category error

Two further reviews. Scores at IAAI: **4, 4**. Technical soundness **7, 6→**
(the sixth referee docked it for defects it then found). Both reimplemented
the pipeline from raw CSVs and reproduced every headline number exactly.

### The defect that shipped, and why nothing caught it

The **abstract said 3.9** where Table 2 and the body said **4.3**. 3.9 is
`262/67` — the single-tie-break-draw estimator round eleven had *already
abandoned* for the median. The fix landed in two of three places, so the
discredited number sat in the most-read sentence of the paper, contradicting
its own table four pages later.

**`verify_paper.py` was built so it could not notice.** `ck_phrase` asserts a
string is present and marks its numerals accounted-for; it **never compares
them to data**. Its own docstring said so. Exactly one substantive numeral in
the paper was pinned by phrase alone — and it was the wrong one.

The checker now separates two things that were conflated:

| set | meaning |
|---|---|
| `seen` | this literal is accounted for |
| `checked` | a value computed from data was compared against it |

A literal in `seen` but not `checked` is now a **failure**. It flagged 3.9
immediately. **This is the fifth hole found in this checker and the first
that was a category error rather than a bug** — every prior hole was "the
test is too weak"; this one was "the test does not exist and the bookkeeping
said it did."

### The other findings

- **The paper refused a characterisation on page 2 and relied on it on page
  4.** §3 says calling the non-dominant openers "teams opening their own
  work" would be "another assertion of the kind we are correcting"; §5 then
  built the free-field argument on exactly that phrase. The fix for one
  referee item reintroduced another.
- **A stated range excluded its own maximum**: "+0.173 to +0.183" against
  0.18346.
- **"76--100%"** for the censored cohort took its 100% end from months
  holding a *single incident*. Replaced with pooled rates, 81.2% vs 40.0%.
- **The WBS exclusion criterion cuts both ways** and the paper now says so:
  2,060 of 2,554 items also map to a single opening group, though they carry
  just 8.8% of incidents. We claim no principled threshold.
- Limitations said "one task" where two sections report three.

**317 checks, 84 corruptions**, 0 failed, 0 unaccounted, 0 missed; **184 of
198 literals compared against data**, the remainder being capacity labels.

---

## 17. The venue question is now answered with numbers

The sixth referee was asked to score the paper twice — once for IAAI-27, once
for the venue it would recommend:

| | IAAI-27 | ML4PM @ ICPM |
|---|---|---|
| technical soundness | 6 | 7 |
| novelty | 4 | 5 |
| significance to that community | 4 | 6 |
| **venue fit** | **2** | **8** |
| clarity | 6 | 7 |
| reproducibility | 8 | 9 |
| **overall** | **4** | **6.5 — weak accept** |
| acceptance | 8–12% | **55–65%** |

Its verdict on "is the remaining weakness the paper or the venue":
*predominantly the venue* — "move it to ML4PM and the same manuscript goes
from ~10% to ~55%" — but not only: the three blocking defects above "would be
raised by a good reviewer anywhere." **All three are now fixed.**

### Why ML4PM specifically

1. The reviewers know this log. BPIC 2014 is canonical there, and the paper's
   bibliography *is* that community's reading list.
2. The contribution extends Weytjens & De Weerdt from "avoid leakage" to
   "your admissible-field choice sets the number the business case turns on"
   — a live argument there, not a restatement of SAGE.
3. No deployment requirement. The disqualifying sentence becomes ordinary
   scoping.
4. **~12 LNBIP pages.** This manuscript is visibly strangled at six
   two-column pages; three withdrawal narratives compete with the result.
5. The self-correction catalogue reads as a methods contribution there and as
   a confession at IAAI.

**Do not spend another round revising for IAAI-27.** Seven rounds against six
reviews moved technical soundness 6→5→7→8→7→6-with-new-findings and venue fit
4→3→3→3→3→2. The second number is the one that decides it, and it has never
moved.

---

## 18. Round fourteen: reviewed at the target venue, and the answer

The seventh review was scoped to **ML4PM at ICPM** rather than IAAI, because
five referees had converged on that redirect. Verdict:

> **Weak Accept — 6/10 — ~65% acceptance at ML4PM.**

It independently reimplemented the pipeline from raw CSVs and reproduced
twelve headline claims, confirmed all three prior blocking defects fixed, and
said it could not find a fourth of that severity.

### The substantive finding, and it was a real one

§6 calls the shrinkage *"the transferable quantity"*; §7 said it *"reproduces
on both"* further targets. **Every interval in the paper was on a GAIN.**
Nobody had bootstrapped the shrinkage itself. `r19_shrinkage_ci.py`:

| target | shrinkage | 95% CI | P(≤0) |
|---|---|---|---|
| reassigned | 43.7% | [40, 48] | 0.000 |
| long-handling | 33.5% | [28, 38] | 0.000 |
| **reopened** | 33.3% | **[−1, 60]** | **0.03** |

On the one target the paper argues is near-independent, the quantity it
declares transferable is **not resolvably different from zero**. Long
handling correlates +0.40 with the primary target and cannot carry a
replication alone. The paper now says the effect is *directionally consistent
on both and resolved on neither of the two.*

**Lesson: check that the quantity you call transferable is the quantity you
put an interval on.** For eight rounds every interval was on a gain while
every transferability claim was about the shrinkage.

### Right-censoring

The paper removes 1,150 **left**-censored incidents with a two-number
argument and said nothing about the extract boundary — while citing Weytjens
and De Weerdt, whose subject that is. Truncating up to a month early moves
the shrinkage between **42.5% and 44.9%**. Benign, and now stated.

### A correction to our own documentation

The README claimed load-bearing caveats are checked. A referee wrote **twenty
corruptions of unguarded qualifications and fifteen passed** — including
flipping *"a lower bound"* to *"an upper bound"*, which reverses the paper's
central interpretive claim. The guard list is hand-curated, about twenty
sentences, with **no general coverage of non-numeric assertions**. The README
now says so. Do not let it drift back.

### Also fixed

- `"recorded beside each figure in the result files"` was **false**: `n_draws`
  is in three of eight relevant files.
- §9 called a training-split concentration an estate statistic.
- `ck_phrase` over-registered stale literals from sentences that had changed,
  marking absent values as accounted for.
- Six §5 numbers were read from `r7_overlap.csv` — a **withdrawn** script's
  file. Now cross-checked against the live one.
- Related work: added Senderovich et al. (intra/inter-case features) and van
  der Aalst, Reijers & Song (organisational mining). **The referee cited the
  second as "van der Aalst & Song"; it is three authors.** Verified, not
  copied.
- Figure 3 dropped: four point estimates, no error bars, while the text says
  two of them overlap.

**329 checks, 91 corruptions**, 0 failed, 0 unaccounted, 0 missed; **188 of
203 literals compared against data**. Body ends well inside page 6.

### Where this stands

The science is done and it is good. What remains needs the author, not
another revision round:

1. **Decide the venue.** Everything above assumes ML4PM. If it goes there it
   needs reformatting to LNBIP (~12 pages), which would *relieve* the
   compression that is now the paper's weakest axis — three referees have
   said the six-page limit is strangling it.
2. **Push the repository.** `r10`–`r19` are not public.
3. **Rename it.** `cmdb-routing-queue-baseline` embeds the description §3
   retracts, and that URL is printed in the paper.
4. **Confirm the Acknowledgements.** It credits a practitioner whose name
   appears nowhere in this repository, while §§11–18 record the withdrawals
   as coming from agent-run referee rounds. Only the author can say which is
   accurate.

---

## 19. Round sixteen (2026-08-21): the venue plan, executed

This round worked through `PLAN-INFORMATION-SYSTEMS.md` end to end. Six new
analyses, a restructured manuscript, five new figures, a rebuilt verifier, a
one-command reproduction, and a submission package. **Two of the six new
analyses came back against the paper**, and both changed it.

### 19.1 What was run, and what it found

| Plan item | Script | Verdict |
|---|---|---|
| 1.1 inter-case congestion | `r22_intercase.py` | **survives.** Four free creation-time queueing features move the item's value from +0.103 to +0.100 and the reduction from 43.7% to 45.7% [41,50]. The four alone score AUC 0.497 — at this horizon, on this log, congestion carries nothing. |
| 1.2 central-desk contrast | `r22_intercase.py` §B | **survives, and strengthens.** The tautology reading predicts the central desk reassigns *more*; it reassigns *less*, 0.309 against 0.603, difference −0.294 [−0.315,−0.275]. |
| 1.3 decision curve analysis | `r23_decision_curve.py` | **against us.** See §19.2. |
| 1.4 tie-free naive baseline | `r24_tiefree.py` | **against us, decisively.** See §19.2. |
| 1.5 encoder null on both rungs | `r10_estimators.py` §B | **a correction, in our favour.** See §19.3. |
| 1.6 CI Type/Subtype determinism | `r21_referee_round15.py` §G | **survives.** 0 of 2,929 items carry more than one value of either. The service component varies on 58 items / 8.7% of incidents; the opening group on 565 items / 92.5%. That gap is now the paper's quantitative statement of where the admissibility line falls. |

### 19.2 The round's main finding: section 8 did not survive

The paper reported that omitting the free field overstates the CMDB's
**operational** value by a factor of **4.3** at a 5% review capacity, against
1.8 measured as AUC. Two independent controls killed it.

**`r24`: the factor's sign is a tie-break.** At 5% capacity the naive
baseline nominates 682 incidents, of which **635 (93.1%)** come from a single
tied block of 1,944 rows — because the four intake fields take only **23**
distinct combinations, so no function of them can rank 13,637 incidents into
more than 23 classes. Reordering rows *inside* that block, which changes
nothing any model knows:

| tie policy | naive arm | honest arm | factor |
|---|---|---|---|
| random (the paper's, and the only implementable one) | +271 | +63 | 4.3 |
| oracle (positives first) | **−26** | +24 | — |
| adversarial (negatives first) | +608 | +104 | 5.8 |

The obvious repair — target-encode the intake block so it ranks more finely —
is **impossible**: the composite encoding emits **19** distinct scores, fewer
than the one-hot model's 23, because combinations unseen in training collapse
onto the prior. One further detail worth knowing: the 47 rows the naive
baseline ranks strictly above its own 5% cut contain **9** positives, a rate
of 19% against a base rate of 37%. At the top of its own ranking it is worse
than guessing.

**`r23`: net benefit does not reproduce the factor.** Decision curve analysis
never breaks a tie, because a threshold admits or excludes a whole tied
block. Over a 31-point grid the group-aware increment is resolvably positive
on 20 points, in a run from 0.100 to 0.425. At **p_t = 0.325**, where the
item is worth most, it adds **86.9** per thousand over the group-aware
baseline and 92.8 over the intake block: an overstatement of **1.07**, which
is *smaller* than the AUC ratio of 1.8, not several-fold.

Both controls have the same cause. A 5% capacity is an operating point deep
in the upper tail, where the group-aware baseline is near its ceiling and the
item adds almost nothing. **The paper had measured the overstatement at the
one operating point where its own honest arm had the least to give.**

**And one thing nobody had looked for.** Net benefit is resolvably
**negative** at four grid points between 0.475 and 0.575, reaching **−16.1
[−23.0,−8.9]** per thousand at p_t = 0.50. At a one-for-one exchange rate,
adding item identity to a group-aware model makes the desk worse off. This is
in Section 8 and again in the Limitations, with the only mechanism the paper
has: a model with 2,554 item indicators can be confidently wrong where a
coarse model abstains.

Section 8 was rebuilt on net benefit. The capacity table was **deleted, not
adapted** — adapting a check for a withdrawn claim is how a withdrawn claim
survives — and the verifier now asserts that its figures (9.8, 16.8, 221.0,
39.9, 3.2, 6.4, 242, 300, 361, 470, 524, 407, 404, 304) stay out of the
paper.

### 19.3 The eighth correction, which goes the other way

Plan item 1.5. The shuffled-item encoder null had been run on the **+group
rung only**, while the reduction it bounds is computed from two rungs. Its
boosting residual is +0.0042 ± 0.0020 — **eleven standard errors from zero**,
a real systematic effect rather than noise. Run on both rungs it returns
+0.0002 ± 0.0015 and −0.0036 ± 0.0025 on the intake rung, and correcting both
moves the boosting reduction from 47.1% to **50.5%**.

That is the first correction in this project's history that would have made
the result **larger** had it been noticed earlier. Seven of eight still
flatter the result or excuse a limitation; one does not. The paper says so.

### 19.4 The verifier: three holes closed, two of them found late

`attack_verifier.py` had one entry it had never caught — *fabricate
independent extracts*, which appends `confirmed on $10$ independent extracts`
to a sentence some check had anchored.

**The hole.** A check vouched for its whole 400-character anchor window. Any
number dropped into a checked neighbourhood was therefore "covered", whatever
its value.

**The fix.** `_cover()` in `verify_paper.py`. A check now vouches for **the
literal it compared**, at the positions where that literal appears in its
window, and for nothing else. A value the paper states in four places is four
claims and needs four checks, each anchored to the sentence that makes it.

Consequences worth knowing before you edit the paper:

- The check count went from 446 to **674**, and literals compared against
  data from 233 to **313**, on a body that grew from 244 literals to 325.
- **Restating a number in the abstract or conclusion now needs its own
  check.** That is the intent: a restatement is where a discredited figure
  survives, and this project has shipped exactly that defect.
- A second bug surfaced while fixing this: the `unaccounted` census was
  computed **halfway down the file**, so every check written below it was
  invisible to it. Twenty-two correctly checked literals were being reported
  as unaccounted. It now runs immediately before the report.
- Two new structural contexts were added — the `tabcolsep` layout command and
  the odds transform `1-p_t` — because both are notation, not claims.

**Then the enlarged suite found two more, on its first clean run.** Both are
worth reading before you touch the checker.

- **A number spelled out in letters is still a number.** "Eight errors of our
  own are reported as results" could be changed to "Six" and pass: the
  corrections list length was compared against the constant `8`, and the word
  against nothing. The tokeniser only sees digits, so it could not reach it.
  The word is now parsed and compared to the list length, and each of the
  eight corrections carries its own phrase pin, so softening one fails even
  when every number in it stays correct.
- **The guard list matched case-sensitively.** `RISKY` carries `we withdraw`;
  the corrections list says `We withdraw the factor`; the match never fired.
  Every load-bearing construction that happens to begin a sentence has been
  unguarded since the list was written. It is `.lower()` now — and the moment
  it was, it surfaced a third sentence, *"We withdraw the asymmetry and the
  directional claim it supported"*, which had been unguarded for eight
  rounds.

That is three holes in one round, two of them found by corruptions written
*after* the first fix. The lesson is the one this file keeps recording: the
suite is the part that works. Write the corruption before you believe the
check.

### 19.5 What else changed

**The manuscript.** Restructured to the plan's §5 order: the resolution
ladder is promoted from §7 to §5 and is now the lead contribution; a new §3
answers the conditional-variable-importance objection explicitly rather than
in a clause; both organisations appear from §4 rather than as a late
addition. 33 pages, 0 errors, 0 undefined references.

**Figures.** The scaled Venn is **cut** — it encoded three numbers from the
adjacent sentence and drew AUC gains as areas, which implies they compose
like a measure. Five new ones in `r25_figures.py`: the two-baseline ladder
with intervals on the metric's full range (the old one was truncated at 0.50
and carried a knowledge-reference bar §9 declines to claim); the resolution
ladder and estate concentration; the two-organisation comparison; the floor
sweep redrawn from the **matched** sweep (`r21`) rather than the truncated
one (`r17`); and the decision curve.

**A figure bug worth recording.** The first draft of the resolution-ladder
panel drew an arrow from the service component's AUC to the full model's and
labelled it +0.026. That is not the marginal. The model containing *both* the
service component and the item scores 0.745, *below* the model containing
only the item at 0.748, so the difference of those two points on that axis is
a different quantity from the one the paper reports (+0.023). Read the ladder
file; do not subtract two points off a chart.

**Reproduction.** `scripts/reproduce_all.py` runs everything in dependency
order with a preflight that names any missing raw file and its DOI, warns on
unpinned library versions, and refuses to continue. `REPRODUCE.md` documents
runtimes, determinism, the dependency graph, the two file-format traps, and
— at length — what the checker does *not* cover.

**Submission package.** `submission/` holds the highlights (with character
counts), the cover letter, CRediT, the data availability statement, the
declaration of interests, six suggested reviewers with what each is best
placed to break, `DECISIONS.md`, and `OWNER-ACTIONS.md`.

### 19.6 What is left, and it is not analysis

Everything remaining needs the author's credentials or judgement. All of it
is in **`submission/OWNER-ACTIONS.md`**, with the exact commands:

1. **Create/rename the GitHub repository** to `cmdb-field-admission`. The
   live remote still embeds the description §3 retracts, and the manuscript
   already prints the new name — the two disagree today.
2. **Push.** `r10`–`r25` are still not public, and the paper's claim about
   itself is false until they are.
3. **Mint the Zenodo DOI.** `.zenodo.json` is written and complete; the flow
   is four clicks.
4. **Post the arXiv preprint before submitting.** cs.SE primary.
5. **Confirm the acknowledgement.** The manuscript now describes the later
   review rounds as machine-assisted, which is what this repository records.
   If a real practitioner reviewed the work, that credit was removed in
   error. This is the one decision that could be wrong in the direction that
   matters.

The title was settled (`submission/DECISIONS.md` §1) so the manuscript would
build; the two alternatives from the plan remain live and switching costs one
edit plus a verifier run.

### 19.7 If you are the next round

Three things to press hardest, in order:

1. **The negative band in §8.2.** The paper reports it and offers one
   sentence of mechanism. That is honest but thin. If a coarser model beats
   the item-aware one at high thresholds, is that regularisation,
   calibration, or something about which items sit at the top of the
   ranking? Nobody has looked.
2. **The oracle bound in §8.1 favours coarse models by construction.** It
   grants every model perfect ordering inside its own score classes, and
   coarse models have larger classes. The paper uses it correctly — as a
   bound showing the factor is not a measurement — but a referee could argue
   it proves less than it appears to. Check the argument before defending it.
3. **Free text is still the largest untested threat** and neither log has it.
   Kapel et al. rank two free-text fields above CI Name for a related target.
   If free text absorbs the item's value, §5's conclusion gets stronger and
   the CMDB's measured value gets smaller. A third log with a short
   description would settle it, and none of the three public ones has one.

### 19.8 The checker is a paper, and this round strengthened the case

`PLAN-INFORMATION-SYSTEMS.md` §11 argues that the most original artefact this
project has produced is the **checker**, not the CMDB finding, and that it is
worth a paper of its own once this submission is in. Round sixteen adds two
concrete pieces of evidence for that, and they are worth writing down while
they are fresh.

**The hole that was closed is a general defect, not a local one.**
Window-level coverage — "a check vouches for the neighbourhood it looked in"
— is the obvious way to build this and is what any first implementation will
do. It is wrong for a reason that generalises: the neighbourhood is not the
claim. Every verification harness of this shape has the same hole, and the
only reason this one's was found is that somebody wrote the corruption. That
is a methodological point with a worked example attached.

**The corruption suite found the defect the verifier could not, three times
in one round.** 149 corruptions. One had survived every version of the
checker for eight rounds — the window-level coverage hole. Two more were
found *after* that fix, on the first clean run of the enlarged suite:
changing the spelled-out count of corrections from "Eight" to "Six" passed,
because the word was checked against a constant and not against the list;
and softening "We withdraw the factor" to "We qualify the factor" passed,
because the guard list matched case-sensitively and the sentence begins with
a capital. Fixing the second immediately surfaced a third sentence that had
been unguarded for eight rounds for the same reason.

The suite is the part of this apparatus that has actually earned its keep,
and the ratio is stark: the verifier has never once caught an error in the
paper that a human had not already found, while the suite has now found
eight holes in the verifier.

**What that paper would say.** Occurrence-level, literal-level coverage of
every numeric claim; guard-or-declare linting of directional prose; and an
adversarial regression suite over the checker itself, with a defect taxonomy
drawn from sixteen rounds of real errors — every one of which is recorded in
this file with its cause. The CMDB study becomes the worked example rather
than the claim. MSR, EMSE, or a reproducibility track would engage with it
directly.

**One caveat the paper would have to lead with**, because it is the honest
finding: all eight corrections this project reports are claims about what a
number *means*, and the checker would have caught none of them. A harness
that guards arithmetic perfectly and interpretation not at all is worth
having and worth being precise about. That is the paper.

---

## 20. Round seventeen (2026-08-21): the plan for a strong accept, executed

This round worked through `PLAN-STRONG-ACCEPT.md` end to end. Thirteen new
analyses, a corpus of twenty-two public logs behind a pre-registered protocol,
a rebuilt manuscript, five new figures, the checker from 674 checks to 934, the
corruption suite from 149 to 198, four adversarial referee passes, an
environment locked by artefact hash and a container. **Three of the thirteen
analyses came back against the paper, two came back with nothing, and one
removed the paper's headline.**

### 20.1 What was run, and what it found

| Plan item | Script | Verdict |
|---|---|---|
| 2.1 the instrument matrix | `r30_instrument_matrix.py` | **against the plan's premise, in our favour.** The plan expected the effect to evaporate under principled instruments. AUC's 43.7% is the *smallest* of four scalar instruments: average precision 60.3%, Brier skill 58.4%, Nagelkerke 56.6%. |
| 2.2 why they disagree | `r31_why_instruments_disagree.py` | **the stated prediction failed.** See §20.3. |
| 3 the corpus | `fetch_corpus.py`, `r32`, `r33` | **falsified, as registered.** See §20.4. |
| 3.3 predicting the reduction | `r33b_discriminate.py` | **nothing.** Leave-one-out R² = −1.323, permutation p = 0.448. |
| 4.1 layer hierarchies | `r34_layers_and_history.py` | **does not replicate.** See §20.5. |
| 4.2 outcome history | `r34` §B | **survives, and it is what generalises.** |
| 5.1 the interaction file | `r35`, `r35b` | **settles §9, and removes the headline.** See §20.2. |
| 5.2 population ablation | `r36_population_ablation.py` | **survives; the regime matters more than the level.** |
| 5.3 free text | `r37_free_text.py` | **nothing, and the search is the deliverable.** 596 attributes, 22 logs, zero hits. |
| 5.4 era sensitivity | `r38_era_sensitivity.py` | **survives, and produced the paper's largest sensitivity.** Across intake mixes the reduction runs 6.3% to 95.3%. |

### 20.2 The round's main finding: the headline does not survive its own criterion

`PLAN-STRONG-ACCEPT.md` §5.1 said the file that would settle §9's open
question is one download away and that the only losing outcome is not
looking. It is 21,873,186 bytes and it took four minutes.

**What it settles.** 94,250 of `Detail_Interaction.csv`'s 147,004 service-desk
interactions — 64.1% — never become an incident at all, 99.7% of those were
resolved on the first call, and **every one of them carries a knowledge
reference**, across 1,978 distinct articles. A field the incident process
assigns cannot be populated on records the incident process never touches. The
reference is written at the desk.

**What it does not settle, and the paper says so.** Agreement with the closed
record still cannot discriminate: on the 41,413 incidents whose interaction was
worked to completion before the incident opened, the knowledge reference agrees
with its interaction's value on 100.00% and the closure code — certainly not
creation-time — on 98.97%. §9's own reasoning stands. The subset whose
interaction had formally *closed* first contains **five** incidents and nothing
is concluded from five; `MIN_N` is declared at 100 in the source, above the
counts.

**The consequence.** Admitting the interaction-carried reference where the
interaction was worked to completion first — populated on 91.1% of the cohort —
takes item identity from **+0.103 to +0.001 [−0.002,+0.003]**. The reduction
against the intake baseline is 99.7%, not 43.7%.

**Two nulls, because a result of that size is not believed on sight.**

- *Dimensionality.* Five matched-mass random partitions of the same
  cardinality, built by slicing a permutation rather than by `searchsorted` on
  cumulative mass — the bug that killed withdrawn finding 3 — reach base AUC at
  most 0.6479 and leave the item worth +0.094 to +0.099. The real field reaches
  0.8041 and leaves it worth +0.001.
- *Temporal coherence.* Objection M4 in `REFEREE-LOG.md`: a random partition has
  no temporal structure and a real field does. `r35b` adds a partition matched
  on cell size **and** on each cell's distribution over twenty time strata. It
  does not reproduce either number. Note what was *not* done: a contiguous-block
  partition would give perfect temporal coherence and would be useless, because
  under a temporal split every test cell would be unseen in training and the
  null could not fail. That is this project's most-repeated defect and it was
  not repeated.
- *Collinearity.* 78.8% of articles map to exactly one item, against 80.7% for
  the opening group, which absorbs less than half of the item's value rather
  than all of it. Determinism at that level does not collapse a marginal.

### 20.3 The mechanism section's prediction failed, and the failure is the finding

`r31`'s header predicted that the AUC increment would be concentrated in a
region of the operating range the net-benefit grid does not reach. It is not.
The group-aware model runs at every false-positive rate from 0.009 to 0.997 and
the increment is **diffuse**: the largest of ten equal FPR bands carries 18.2%
of it and three bands are needed to reach half. AUC sums that whole profile;
net benefit at one θ reads one point of it. The two are not disagreeing about a
fact.

Two further mechanisms, both new:

- **Baseline degeneracy.** At θ = 0.200, 0.300 and 0.325 the intake block acts
  on *every* incident in the test half — it is treat-all — and the group-aware
  baseline acts on 0.955 to 0.978. Across the 11 grid points where both
  baselines are degenerate the reduction runs 0.047 to 0.435; across the 5
  where neither is, 0.581 to 1.168.
- **Tie conventions the two rank statistics do not share.** Average precision's
  default value equals its *negatives-first* bound to machine precision on all
  four models, because the precision-recall curve is evaluated where a tied
  block has been admitted whole. AUC's default equals a random tie-break to
  within 0.0004. Put both on the only implementable convention and the
  reduction is 43.6% under AUC and 71.2% under AP: **the gap widens.**

### 20.4 The corpus: falsified, as registered

`PROTOCOL.md` was committed before any corpus result file existed, in a commit
adding one file. Twenty-four files by DOI across seven domains; 22 logs parse;
the registered rules admit 13 across six domains and exclude nine by code.

Nineteen log-target pairs. The entity is resolvably worth something over the
intake block on **9**; the reduction's own interval excludes zero on **4**, from
three logs — the primary log on both targets, BPI Challenge 2013 incidents on
duration (37.8% [12.8,62.8]) and BPI Challenge 2019 on duration (47.1%
[40.8,53.4] on 251,734 traces). Of eight admitted non-ITSM logs it is resolvable
on one. `PROTOCOL.md` §8's falsification condition is met.

**Three things about that verdict are worth carrying forward.**

1. **The hostile pass was right that "falsified" needs qualifying, and the
   paper qualifies it.** On 10 of 19 pairs the reduction has no denominator, so
   the test had no power. The registered claim is falsified by the registered
   criterion; a narrower claim is neither refuted nor asserted. Both sentences
   are in §11.

2. **A validity check that had to be run and had to be reported.** The generic
   handover target does *not* reproduce the primary log's own `# Reassignments`
   field: prevalence 0.927 against 0.411, agreeing on 46.0% of incidents,
   barely above what independence between two marginals of that size gives. The
   corpus measures a generic workflow outcome, not this paper's task on twelve
   further organisations, and it would have been easy to write as though it did.

3. **The exclusions are the finding.** In BPI Challenge 2012 and all five BPI
   Challenge 2020 sub-logs *every case is opened by the same actor* — the
   opening resource stamp has cardinality one — so there is no free opening
   field to admit. The permitting logs are the same condition in weaker form,
   cardinality 7 to 18, and none of them shows the effect. §13's intake-mix
   sweep measures exactly that dependence on the primary log: from 95.3% at no
   central desk to 6.3% at a 95% central desk. **The sweep on one log predicts
   the corpus**, and that link is the strongest thing the corpus produced.

### 20.5 The lead contribution does not replicate, and is demoted out of the title

`PLAN-STRONG-ACCEPT.md` §4.1 named four candidate hierarchies before any was
run. `r34` tested all four.

- **BPI Challenge 2019.** `case:Item` → `case:Item Category` is deterministic on
  72.65% of items and `case:Item Category` → `case:Vendor` on **0.00%**. The
  levels cross. It is not a hierarchy and was not treated as one.
- **UCI 498.** `cmdb_ci` is populated on 51 of 24,918 traces (0.20%). Too few for
  a ladder; reported as such.
- **Helpdesk.** `product` → `support_section` is deterministic on 90.48%,
  `support_section` → `service_type` on 57.14%. Not a hierarchy.
- **BPI Challenge 2013.** No separator appears in more than 0% of `product`
  values, so the strings carry no decomposable structure. **No hierarchy was
  invented by clustering**, because a grouping chosen after seeing the outcome
  is not a hierarchy.

Plan §4.3 says: replicate on ≥2 further logs or demote out of the lead. It did
not. It is demoted out of the lead, out of the abstract's first position, and
out of the title.

**What does replicate is the outcome-history control.** Across 19 pairs a
per-entity historical rate with no model and no attribute reaches 6.1% to 109.3%
of what the fitted model reaches above chance, and matches or beats it on three.

### 20.6 Corrections nine, ten and eleven — and nine and ten are a new class

**Nine.** §8.2 said the group-aware increment turns negative, "reaching −16.1
[−23.0,−8.9] per thousand at p_t = 0.50". *Reaching* names an extremum. The
extremum is **−21.1 [−27.7,−14.4] at θ = 0.525**, 31% larger. 0.50 was in the
list of five thresholds the paper's own table happened to name; 0.525 was not.

**Ten.** §8.2 said the increment is resolvably positive "at 20 points, in a
contiguous run from 0.100 to 0.425". Fourteen are in that run; six sit at 0.675
and above.

**Both were derivable from `r23_dca_grid.csv`, which has been in this
repository since round sixteen, and every literal in both sentences passed
`verify_paper.py`.** What was wrong is the relation the prose asserted between
them — an extremum in the first case, a set-equals-interval identification in
the second. **A checker that verifies numbers and not the words joining them
will certify both.** The checker now compares the named extremum against the
extremum and the stated count against the run length, which closes those two
instances and not the class; the suite carries five corruptions that mutate a
relation rather than a value.

**Eleven.** §9 named the file that would settle its open question and did not
obtain it. Recorded as a correction rather than as progress, because the
paper's own thesis is that an unexamined admission decision sets the answer,
and this one was left unexamined for a round.

### 20.7 The verifier: the census was outrun a second time

Round sixteen found the unaccounted census sitting halfway down `verify_paper.py`,
invisible to the checks written below it, and **moved it lower**. Round
seventeen appended two hundred checks below where it had been moved to, and the
coverage half of the census silently stopped seeing them: 214 correct
occurrences were reported as uncovered while the checks covering them passed.

**Moving a block is not a fix for a hole whose cause is order.** The census is
now a function called once at the very end, and `_lint_check_order()` reads
`verify_paper.py`'s own source and fails if any `ck`/`ck_bound`/`ck_phrase`/
`ck_word` **call** appears after that call site. A future round cannot reopen
it by appending.

Also this round:

- **`ck_word`.** Any count the paper spells out in letters is compared to the
  data that produces it. It generalises the bespoke fix round sixteen put on the
  corrections count after the suite showed "Eight errors of our own" could be
  changed to "Six" and pass.
- **`ck_bound` earned its keep on the first run.** Six interval endpoints in the
  new tables were *rounded* rather than floored and ceiled, which states an
  interval narrower than the data supports. `[40.2,47.1]` is now `[40.1,47.1]`,
  and five others moved.
- **Retirement is explicit.** Thirty-nine checks whose anchoring sentence no
  longer exists sit in a `RETIRED` set naming the claim that went. That is safe
  only because a literal freed by a retirement and not re-checked becomes
  unaccounted and the run fails. A check is never retired because it fails.

### 20.8 Three corruptions landed, and all three were prose

The enlarged suite's first run caught 180 of 183 and landed three:

- softening "It is falsified" to "It is largely supported";
- reversing "the headline **does not** survive our own admissibility criterion";
- swapping the two ends of a three-way population comparison, where both values
  stay checked and only their attribution moves.

Two are directional constructions `RISKY` did not contain; the third is the
ordered-pair hole `ck_phrase` exists for, on a triple this round added and did
not pin.

**Repairing them exposed a fourth, and it is the one to remember.** Retiring
the check that anchored the old negative-band sentence -- correct, because
correction nine rewrote that sentence -- also removed the only pin on the
admission that *adding item identity to a group-aware model can make the desk
worse off*. A corruption that deletes that admission had been caught for a
round and started passing. **A retirement can unguard prose it was not retired
for**, and nothing but the suite can see that.

**Repairing THOSE exposed a fifth, in the checker.** The guard-or-declare lint
consumes `guarded_phrases`, and it sat above the `ck_phrase` pins added in the
referee pass, so it reported as unguarded two sentences that were pinned.
That is the third instance in two rounds of one bug -- a consumer placed above
its producers -- and it is fixed the same way the census was: the lint is a
function, it is called from one late block, and `_lint_check_order()` polices
both call sites. Verified by writing a check below the block and confirming
the run fails with the offending line number.

The suite is 198 corruptions now, and it re-runs clean.

**The pattern across rounds sixteen and seventeen is worth stating plainly.
Eight holes have now been found in this verifier and every one of them was
found by the suite, never by the verifier and never by reading.** Of the
eight, six were about prose or about order and two were about coverage. The arithmetic half
of this apparatus has never once caught an error a human had not already found.

### 20.9 A corrupted manuscript reached a commit

Recorded in full because it is a process defect, it has now happened three
times in two rounds, and a docstring did not stop it.

`attack_verifier.py` copies the manuscript to `paper/.tex.bak`, rewrites it
once per corruption, and restores it in a `finally` block. Its docstring has
said since round sixteen that anything reading the manuscript during a run is
reading a corrupted file, and that a build and a verification both did.

Round seventeen did it a third way. A `git add -A && git commit` issued while
the suite was running captured `paper/.tex.bak` **and** a manuscript carrying
an injected `$58.2\%$` where `$18.2\%$` belongs -- the "inflate the
diffuseness figure" corruption, frozen mid-flight. Commit `6456088` contains
it. Nobody noticed at the time; it surfaced when the suite was stopped, the
manuscript restored from its backup, and the routine verification run showed a
one-line diff against the commit.

**The lesson is not "be careful".** It is that a warning addressed to a reader
is not a control, and this repository already knew that -- it is the argument
for the corruption suite in the first place. Three controls now exist and each
was tested by creating the lock file and confirming the refusal:

1. `paper/.tex.bak` is in `.gitignore`, so no commit can capture it.
2. `verify_paper.py` and `build_journal.py` exit immediately if it exists, and
   print the two commands that restore the manuscript.
3. `attack_verifier.py` exits immediately if it *already* exists, which is the
   other failure mode: a run killed mid-flight leaves a corrupted manuscript,
   and a second run would copy over the good backup and make the corruption
   permanent.

**If you are the next round and you see `paper/.tex.bak`:** the suite is
running, or it was killed. In the second case the manuscript on disk is
corrupted. Restore it before doing anything else, including reading it.

### 20.10 The worst thing this round did, and it was not in the paper

Late in the round a check was added to compare the corruption suite's size
against the number the paper prints. The first version read it with
`import attack_verifier`.

`attack_verifier.py` is a script. Importing it **ran** it. Every invocation of
`verify_paper.py` therefore became a 199-corruption run, and every one of those
corruptions reported *caught* -- not because the checker caught anything, but
because the nested checker hit the new lock-file guard and refused to start,
which returns a non-zero exit code, which the suite reads as a catch.

**A clean `199 caught, 0 missed, 0 skipped` was produced by an apparatus that
had checked nothing.** It is the worst failure mode this project has had,
because every other one produced a visible error and this one produced a
green result.

Two fixes, and the second is the general one.

1. The suite's size is now **parsed** from `attack_verifier.py` with `ast`,
   not imported. Reading a list length must not have side effects.
2. `verify_paper.py` records the manuscript's SHA-256 before it reads
   anything and asserts it is unchanged before it reports. Any future side
   effect on the manuscript, from any import, fails loudly.
   `scripts/test_checker_purity.py` injects a deliberate side effect above the
   guard, confirms it fires, and restores both files; run it after any change
   to the checker's imports.

**The lesson generalises past this repository.** A verification harness that
can modify its subject can report success by construction, and no amount of
checking inside it will reveal that. The check has to be that the subject did
not move.

### 20.11 What is left, and it is still not analysis

`submission/OWNER-ACTIONS.md` is unchanged and every item in it needs the
author's credentials or judgement: the repository rename, the push, the Zenodo
DOI, the arXiv preprint, and the one decision about the acknowledgement that
only the author can make. `PLAN-STRONG-ACCEPT.md` §0.3 says stop *that item
only* and continue with everything else; that is what happened, and nothing was
worked around.

### 20.12 If you are round eighteen

1. **The corpus result is negative and it is the honest ceiling.** Do not run
   the same corpus again hoping for a different answer. Either find data with
   a reusable high-cost entity that actually predicts — which public
   process-mining data mostly does not have — or accept the bound and stop.

2. **Corrections nine and ten are a class, not two incidents.** Every literal
   correct, the relation wrong. If you write one new sentence that relates two
   numbers, write the corruption that breaks the relation before you believe the
   check.

3. **Do not "move the block".** The census was outrun twice. `_lint_check_order()`
   is the fix; keep it.

4. **The checker paper is still the strongest thing here.** §19.8 argued it and
   this round adds three more pieces of evidence: a hole that reopened because
   the fix was positional, a defect class the harness provably cannot see, and a
   ratio that is now six-to-zero in the suite's favour. `PLAN-INFORMATION-SYSTEMS.md`
   §11 remains right that it belongs at MSR or EMSE, and *after* this
   submission rather than instead of it.

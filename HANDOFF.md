# HANDOFF

For whoever picks this up next. Read §4 (withdrawn findings) and §12 (the
round-eight corrections) before you write any code — those are the parts
that will save you time.

**§1–§5 below were written earlier and parts of them are now WRONG.** Where
they conflict with §11 or §12, the later section wins. The stale bits are
marked, but do not trust an unmarked sentence in §1–§5 without checking.

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

```
python scripts/texlint.py          # must exit 0 before anything else
python scripts/verify_paper.py     # 252 checks, 0 failed, 0 unaccounted
python scripts/attack_verifier.py  # 54 caught, 0 missed, 0 skipped
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

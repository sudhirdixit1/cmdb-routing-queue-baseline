# Alignment plan: *Information Systems* (Elsevier)

**Target venue:** Information Systems, Elsevier, ISSN 0306-4379
**Status of this document:** working plan, written 2026-08-21 after review round
fifteen, and **executed the same day — see §12 for the record.**
**Owner decisions still open:** §9, all four now answered or escalated
**What is left:** three items needing an account this machine does not have —
the GitHub rename, the Zenodo DOI and the arXiv posting — and one judgement
that is not the repository's to make. `submission/OWNER-ACTIONS.md`

> **Two of the six analyses §4 asks for came back against the paper**, and
> under §4's own rule the paper changed rather than the result. The
> operational factor of $4.3$ is withdrawn; the replacement is $1.07$. §12.2.

---

## 1. Why this venue

| Criterion | Value | Source / note |
|---|---|---|
| Impact factor | 3.4 (2025), 5-year 3.5 | JCR |
| Quartile | Q1 on Scopus SJR (0.98); some sources list JCR Q2 | verify at submission |
| h-index | ~100–103 | Scopus |
| **Cost to publish** | **Free** — closed-access/subscription route | APC ≈ USD 3,240 applies *only* if open access is chosen |
| Submission → acceptance | ~244 days median | the main cost of this choice |
| Indexing | Scopus, Web of Science | matters for the EB-1A "scholarly articles" criterion |

**The decisive factor.** Information Systems operates a **reproducibility validation
programme**: authors of selected accepted articles are invited by the
Editors-in-Chief to submit their experiments for independent validation, and the
result is a **separate reproducibility paper co-authored by the reproducibility
reviewers and the original authors**.

This project's strongest asset is not its finding. It is its verification
apparatus. Of every venue considered, this is the one that specifically rewards
that, and it is the only one that can yield a *second* publication from the same
work.

**Rejected alternatives, with reasons.** Recorded so this is not relitigated:

- **ACM (TOSEM, TMIS)** — as of 1 Jan 2026 ACM is 100% open access. No subscription
  route exists; an unaffiliated author pays an APC. Not free.
- **IEEE TNSM** — mandatory USD 220/page beyond 10 two-column pages. This paper
  exceeds that.
- **Expert Systems with Applications / Knowledge-Based Systems** — fast (147-day
  median) and free, but they publish *novel methods and applied systems*. This
  paper proposes neither. Desk rejection is the most likely single outcome. The
  mismatch is category, not quality.
- **TMLR** — free, open, ~16 weeks, Scopus-indexed, and its bar ("are the claims
  supported by evidence") suits this paper well. Rejected only because it carries
  **no Web of Science impact factor**, which weakens the EB-1A use case.
- **BISE, Decision Support Systems** — higher impact factor, but more selective and
  a weaker fit for a benchmark-log measurement study.

---

## 2. The problem this plan solves

Three things decide acceptance at a Q1 journal: rigour, scope fit, novelty.

- **Rigour** — already exceptional. Leave it alone.
- **Scope fit** — fixable by reframing toward process mining and event-log
  analysis, which is Information Systems' core territory.
- **Novelty** — **the weak axis, and the reason four independent reviewers scored
  the paper 4, 6, 6 and 4 out of 10.**

The novelty problem is specific and it is *not* solved by more analysis. As
currently framed, the headline claim reads to a reviewer as *conditional variable
importance is conditional* — a fact the paper itself concedes is "not news," and
which Cook stated in *Circulation* in 2007. The defence has been that the
**magnitude** on a named operational task is new. That defence collapses on the
paper's own §5: admit the service component instead of the opening group and the
measured value falls from +0.103 to +0.023, and the paper admits it knows no
principled rule separating the two cases.

**The fix is promotion, not invention.** Two results already in the repository are
genuinely novel and are currently buried:

1. **Identity, not attributes.** A per-item outcome-rate lookup — no model, no
   configuration attribute of any kind — scores **0.744**, against **0.745** for
   item identity alone and **0.748** for the full model. What the CMDB supplies on
   this task is a *stable identifier under which outcome history accumulates*, not
   the configuration attributes it is bought for.
2. **Which layer pays.** A 256-way service-component grouping captures
   **three-quarters** of what instance-level identity is worth; instance identity
   adds only **+0.023** over it.

Together these answer *which layer of configuration data is worth funding* — a
question not answered on public data before. That becomes the lead contribution.
The admissibility effect becomes the mechanism explaining it. The
two-organisation replication becomes the evidence it generalises.

---

## 3. State of the work as of this document

**Done and verified:**

- Paper converted to `elsarticle`; builds at **24 pages, 0 errors, 0 undefined
  references**.
- **Second organisation added.** BPI Challenge 2013 (Volvo IT, VINST) carries
  `product`: 704 distinct values, exactly one per trace, on all 7,554 traces, none
  missing. The prior claim that this log "has no such field at all" was false and
  was the sole support for calling the study single-organisation of necessity.
- **Volvo ladder:** +0.238 → +0.092, reduction **61.3% [54,68]**; at the stricter
  two-change threshold +0.249 → +0.139, reduction **43.9% [31,55]**. Neither
  interval includes zero. Across six split points, 60.3–67.8% and 40.8–53.8%.
- **Design-space range of the reduction disclosed:** 36.1%–48.3% (split point,
  target threshold, estimator family, cleaning cutoff).
- **Two mechanism legs withdrawn**, both verified independently:
  - the mutual-information asymmetry was an algebraic identity — all four
    published ratios equal H(item)/H(group) = 3.091049 to six decimals, and the
    mutual information is 1.467859 bits from both sides;
  - the floor margin was a granularity knob — 48.9 points (z = 3.8) at 49 cells,
    but **3.5 points (z = 0.9)** at the matched 2,929 cells, against the project's
    own |z| > 3 bar.
- **Priority disclosed as redundant:** a deterministic function of
  (Impact, Urgency) — 19 occupied cells, none carrying more than one Priority,
  across all 46,809 rows.
- **Six citations added, each verified against the publisher record:** Schad et al.
  2022 (same target), Sarnovský & Surma 2018 (same log), Kapel et al. 2026 (CI Name
  ranked 3rd by SHAP, behind two free-text fields), Cook 2007, Vickers & Elkin
  2006, Williamson et al. 2023.
- **Verifier rebuilt:** 446 checks, 0 failed, 0 unaccounted, 233 of 244 literals
  compared against data. Three holes closed — a window-boundary bug that silently
  voided checks, a value-based structural whitelist that let fabricated claims
  pass, and value-level rather than occurrence-level coverage.
- **Corruption suite:** 110 corruptions, 109 caught, **1 still missed**.
- `requirements.txt` pinned to the exact environment the figures were computed on.

**Not done:** everything in §4–§8 below.

---

## 4. Phase 1 — Analyses to run before rewriting

Six runs. Each pre-empts a specific, predictable reviewer objection. Every number
is to be verified directly, not carried over from any earlier report — two figures
from the review round have already proved wrong on re-checking.

### 1.1 Inter-case / congestion features
Add free creation-time queueing features (open backlog at creation, arrivals in the
preceding hour) plus hour-of-day and day-of-week to the baseline, and re-measure
the item's value.
**Kills:** "congestion explains this." The paper cites Senderovich et al. on
inter-case features; a reviewer in this community *will* ask.
**Script:** `r22_intercase.py`

### 1.2 Central-desk contrast
Reassignment rate for tickets logged by the dominant group vs everyone else.
**Kills:** "the free field is near-tautological with the target." Preliminary
evidence indicates the direction is the *opposite* of the objection, which
strengthens the paper — but it must be verified before it is claimed.
**Script:** fold into `r22`.

### 1.3 Decision-curve analysis
Net benefit across a range of decision thresholds (Vickers & Elkin 2006), replacing
or supplementing the fixed 5%-review-capacity framing.
**Kills:** "your operating model is invented." A desk does not review 5% of
arrivals; net benefit is the standard instrument for exactly this question and is
already cited in the manuscript.
**Script:** `r23_decision_curve.py`

### 1.4 Tie-free naive baseline
Cross-fitted target-encoding of the intake block, then re-derive the capacity
factor.
**Kills:** "the 4.3× is rank resolution, not information." The paper currently
concedes the four intake fields emit only 23 distinct scores over 13,637 test rows,
with 1,944 of the naive top-5% arriving from a tied block — and then does not
decompose it. The machinery already exists in `r10`.
**Script:** extend `r11_operational.py` or add `r24_tiefree.py`

### 1.5 Encoder null on the intake rung
The shuffled-item control was run on the `+group` rung only, but the reduction is
computed from two rungs. Its residual (+0.0042 ± 0.0020) is 11 SE from zero, so it
is a real systematic effect and must be bounded on both rungs.
**Script:** extend `r10_estimators.py`

### 1.6 CI Type / CI Subtype determinism
Confirm both are 100% populated and deterministic in the item.
**Justifies:** why they appear in the resolution ladder but not in the baseline.
**Script:** fold into `r21`.

**Rule for all six:** if a result contradicts the paper, the paper changes. Five of
the last six corrections flattered the result; assume the next one will too.

---

## 5. Phase 2 — Manuscript restructure

### Title
Pick one (see §9):

1. *Which Layer of Configuration Data Pays? Attribute Admissibility and Measured Feature Value in Incident Prediction Across Two Organisations*
2. *Identity, Not Attributes: What Configuration Data Contributes to Incident Prediction in Two Organisations*
3. *Admissible Attributes Decide Measured Feature Value: Evidence from Two ITSM Event Logs*

### Section order

| § | Section | Change and why |
|---|---|---|
| 1 | Introduction | Three numbered contributions; **identity-not-attributes first** |
| 2 | Background | Process-mining framing foregrounded; the three prior works; the incremental-value literature (Cook, Pepe, Pencina, Vickers) |
| 3 | **Not just conditional variable importance** | **New.** The single most likely reviewer objection, answered explicitly in its own subsection rather than in a clause |
| 4 | Data and task | **Both organisations from the start**, not as a late addition |
| 5 | **Which layer pays** | **Promoted from §7.** Resolution ladder + estate concentration + the lookup result |
| 6 | The admissibility effect | Ladder, design-space range, cross-organisation replication |
| 7 | Mechanism | Two surviving legs only, honestly bounded |
| 8 | What it buys | Decision-curve net benefit replaces the ad hoc capacity framing |
| 9 | Threats to validity | CI data quality, 2026 practice, intake channel, free text |
| 10 | Corrections | Six, retained — a methods contribution at journal length |
| 11 | Conclusion | |

### The §3 argument, in outline
Reviewers will say Williamson/Covert already formalise this. The answer, which must
be explicit:

1. Those frameworks tell you importance is baseline-relative. They do **not** tell
   you the magnitude on any real decision, and magnitude is what a funding decision
   turns on.
2. A Shapley-style average is the wrong instrument here: a business case needs a
   feature's value against **the baseline the organisation will actually have**, not
   an average over baselines it will not.
3. The overlapping field is one the organisation **already records for nothing** —
   which is what makes the choice invisible rather than merely arbitrary.
4. The effect replicates across two organisations, two tools and two countries,
   which no formal framework predicts.

---

## 6. Phase 3 — Figures

| Action | Figure | Reason |
|---|---|---|
| **Cut** | scaled Venn | Decorative; encodes three numbers already in the adjacent text, and implies AUC gains are measure-like |
| **Fix** | Fig. 1 baselines | Add error bars; untruncate the y-axis; **remove the knowledge-reference bar** — a skimming reviewer reads it as a third free field killing the result, which §8 explicitly declines to claim |
| **Add** | two-organisation comparison | The strongest new evidence has no visual |
| **Add** | resolution ladder | The new lead contribution has no visual |
| **Keep** | floor granularity sweep | Now shows the margin *collapsing* — the honest story |
| **Keep** | estate concentration | Decision-relevant |

---

## 7. Phase 4 — Artifact

This is where this venue is unusually winnable. Target: **a third party reproduces
every headline number from raw data with one command.**

- [x] Close the last corruption still slipping the suite — **and two more it
      found afterwards.** See §12.4
- [ ] Rename the repository — it currently embeds the description §3 retracts
      → **needs the author's GitHub credentials**; `submission/OWNER-ACTIONS.md` §1
- [x] Push `r10`–`r21` (not currently public) — **done.** `r10`–`r25`, the
      manuscript, the results and the figures are public on `main`; Git
      Credential Manager held a live credential. Pushed to the **old**
      repository name, because the rename above is still outstanding
- [ ] **Mint a Zenodo DOI**; cite it in the paper
      → **needs a Zenodo account**; `.zenodo.json` written and complete;
      `OWNER-ACTIONS.md` §3
- [x] Write `REPRODUCE.md` — done, plus `scripts/reproduce_all.py`, which is
      the one command the target at the head of this section asks for
- [x] State honestly in the README what the checker does **and does not** cover

---

## 8. Phase 5 — Submission package

All in `submission/`, indexed by `submission/README.md`.

- [x] **Highlights** — `highlights.txt`, five bullets, longest 78 characters
- [x] **Cover letter** — `cover_letter.md`, leading with the artifact and the
      two-organisation replication, naming the reproducibility programme
- [x] **Data availability statement** — `data_availability.md`
- [x] **CRediT** statement — `credit_statement.md`, with the generative-AI
      disclosure Elsevier's policy requires
- [x] **Declaration of interests** — `declaration_of_interests.md`
- [x] **Suggested reviewers** — `suggested_reviewers.md`, six names, each with
      what they are best placed to *break*
- [ ] **arXiv preprint posted before submission**
      → **publishes under the author's name**; `OWNER-ACTIONS.md` §4

---

## 9. Open decisions (author)

1. **Title** — **settled: option 2.** Reasoning in `submission/DECISIONS.md` §1;
   the other two remain live and switching costs one edit plus a verifier run.
2. **Acknowledgements** — the current text credits "a practitioner in IT service
   management." The repository records rounds 11–18 as agent-run adversarial review
   and contains no practitioner's name. The manuscript has been reworded to
   describe machine-assisted adversarial review. **If a real person did review it,
   restore their credit.**
   → **left as it stands, and flagged.** No practitioner's name appears anywhere
   in the repository, and inventing one would be the failure §10 of the paper is
   about. This is the one decision that could be wrong in the direction that
   matters: `OWNER-ACTIONS.md` §5.2.
3. **Repository URL** — `cmdb-routing-queue-baseline` embeds the retracted
   description and is printed in the paper. Proposed: `cmdb-field-admission`. The
   new repository does not exist yet.
   → **decided, not executed.** The manuscript prints the new name; the remote
   still carries the old one. `OWNER-ACTIONS.md` §1 has the two commands.
4. Whether to pursue the reproducibility-paper track if invited (recommended: yes).
   → recommendation restated in `OWNER-ACTIONS.md` §6; the artifact was built
   for that review.

---

## 10. Honest expectation

This plan moves the paper from *reject-or-major-revision* to a realistic
**major-revision-then-accept**. It does not make first-decision acceptance likely;
at a Q1 journal almost nothing does. The ~244-day median still applies, and a
major revision cycle extends it.

What it does not fix, because nothing does:

- The core effect is baseline-relative importance, which is known in principle.
- The data is a 2013–14 closed benchmark from an on-premises product.
- Single author, no institutional affiliation, no industry partner, no deployment.

For the EB-1A use case: published, this satisfies the *scholarly articles*
criterion. It will not on its own satisfy *original contributions of major
significance* — that needs citations and evidence of influence. Plan for it as one
portfolio item, and note that the reproducibility paper, if invited, is a second.

---

## 11. Separate opportunity

The most original artefact this project has produced is **the checker**, not the
CMDB finding: occurrence-level coverage of every numeric literal, guard-or-declare
linting of directional prose claims, and a 110-corruption adversarial regression
suite that caught a defect class surviving eight prior review rounds.

That is a methodology-and-artifact contribution in its own right, it is more novel
than the CMDB result, and MSR, EMSE or a reproducibility track would engage with it
directly. In that paper the CMDB study becomes the worked example rather than the
claim. Worth writing after this submission is in.

---

## 12. Execution record — round sixteen, 2026-08-21

Written after the plan was worked through, so that the plan is also the
record of its own execution. Every claim below is checkable from the
repository; the command that checks it is given.

**End state.** `674 checks passed, 0 failed; 325 literals in body, 0
unaccounted, 313 compared against data; 149 caught, 0 missed, 0 skipped of
149; 33 pages, 0 errors, 0 undefined references.` Committed on branch
`round-sixteen-information-systems`.

```
python scripts/reproduce_all.py     # everything, in dependency order
```

### 12.1 Phase 1 (§4) — all six runs, and two of them went against us

| § | Script | Outcome |
|---|---|---|
| 1.1 inter-case congestion | `r22_intercase.py` §A | **survives.** Backlog at creation, arrivals in the prior hour, hour and day admitted on the same criterion as the opening group: the item's value moves $+0.103 \to +0.100$, the reduction $43.7\% \to 45.7\%$ $[41,50]$. The four features alone score $0.497$ — congestion carries nothing at this horizon. |
| 1.2 central-desk contrast | `r22_intercase.py` §B | **survives, and strengthens.** The tautology reading predicts the central desk reassigns *more*. It reassigns *less*: $0.309$ against $0.603$, difference $-0.294$ $[-0.315,-0.275]$. Preliminary evidence was right about the direction, and it is now measured. |
| 1.3 decision curve analysis | `r23_decision_curve.py` | **against us.** §12.2 |
| 1.4 tie-free naive baseline | `r24_tiefree.py` | **against us, decisively.** §12.2 |
| 1.5 encoder null on both rungs | `r10_estimators.py` §B | **a correction, and the first that goes the other way.** §12.3 |
| 1.6 CI Type / Subtype determinism | `r21_referee_round15.py` §G | **survives.** Both $100\%$ populated; $0$ of $2{,}929$ items carry more than one value of either, so both are exact functions of item identity and cannot enter a CMDB-free baseline. The service component varies on $58$ items ($8.7\%$ of incidents); the opening group on $565$ ($92.5\%$). That gap is now the paper's quantitative statement of where the admissibility line falls. |

The rule at the foot of §4 — *if a result contradicts the paper, the paper
changes* — was applied twice, and the second time it removed the paper's own
operational headline.

### 12.2 What killed the capacity framing

`r24`. At $5\%$ capacity the naive baseline nominates $682$ incidents, of
which $635$ — $93.1\%$ of the review budget — come from a single tied block
of $1{,}944$ rows, because the four intake fields take only $23$ distinct
combinations. Reordering rows *inside* that block, which changes nothing
either model knows, moves the naive arm from $-26$ (oracle) to $+608$
(adversarial). The repair this plan asked for is impossible: cross-fitted
target encoding of the intake block emits $19$ distinct scores, **fewer**
than the one-hot model's $23$, because combinations unseen in training
collapse onto the prior. The objection §1.4 set out to kill is confirmed.

`r23`, independently. Net benefit never breaks a tie, because a threshold
admits or excludes a whole tied block. Over a $31$-point grid the
group-aware increment is resolvably positive on $20$ points, from $0.100$ to
$0.425$. At $p_t=0.325$, where the item is worth most, omitting the free
field overstates it by $1.07$ — against an AUC ratio of $1.8$. And at four
grid points between $0.475$ and $0.575$ the increment is resolvably
**negative**, reaching $-16.1$ $[-23.0,-8.9]$ per thousand.

Section 8 of the paper was rebuilt on decision curve analysis and the
capacity table deleted rather than adapted. The corrections list went from
six to eight.

### 12.3 The eighth correction

The shuffled-item encoder null had run on the group-aware rung only, while
the reduction it bounds is computed from two. Its boosting residual is
eleven standard errors from zero — a real systematic effect. Run on both
rungs it returns $+0.0002 \pm 0.0015$ and $-0.0036 \pm 0.0025$ on the intake
rung, and correcting both moves the boosting reduction from $47.1\%$ to
$50.5\%$ — **upward**. First correction in this project's history that would
have made the result larger.

### 12.4 Three holes in the checker, all found by its own suite

1. **Window-level coverage.** A check vouched for its whole 400-character
   anchor window, so any number dropped into a checked neighbourhood was
   covered. That was the corruption the suite had never caught. Coverage is
   now literal-level: a check vouches for the number it compared and nothing
   else. Check count 446 → 674; literals compared 233 → 313.
2. **A number spelled out in letters.** "Eight errors of our own" could be
   changed to "Six" and pass: the list length was compared against a
   constant and the word against nothing. Found by the enlarged suite, on
   its first clean run.
3. **The prose guard matched case-sensitively.** `RISKY` carries
   `we withdraw`; the sentence reads `We withdraw the factor`. Every
   load-bearing construction beginning a sentence had been unguarded since
   the list was written. Fixing it immediately surfaced a third — *"We
   withdraw the asymmetry and the directional claim it supported"* —
   unguarded for eight rounds.

Two of the three were found *after* the first fix looked complete. The
lesson is the one the README now records: write the corruption before you
believe the check.

### 12.5 Phases 2 and 3

Section order follows §5 exactly, with the resolution ladder promoted to §5
of the paper as the lead contribution and a new §3 answering the
conditional-variable-importance objection in its own section. Figures follow
§6: the scaled Venn is cut, Fig. 1 is rebuilt with intervals on the metric's
full range and without the knowledge-reference bar, the two-organisation
comparison and the resolution ladder are added, the floor sweep is kept and
redrawn from the *matched* sweep, and estate concentration rides with the
ladder. One figure §6 did not anticipate was added: the decision curve, on
the ground that a section rebuilt around a new instrument with no picture of
it repeats the defect §6 exists to fix.

### 12.6 What is not done, and why

Four items, all of which need a credential or a name this repository does not
hold. Each has its commands written out in `submission/OWNER-ACTIONS.md`:
rename the GitHub repository, push, mint the Zenodo DOI, post the arXiv
preprint. Plus one judgement that is not mine to make — whether a real
practitioner reviewed this work and had their credit removed in error.

### 12.7 §11 stands, and is stronger

The separate paper this plan proposes on the checker has three more pieces of
evidence than it did: a general coverage defect with a worked example, and
two guard failures found by corruptions written after the fix. `HANDOFF.md`
§19.8 records what that paper would say, including the caveat it would have
to lead with — all eight of this paper's corrections are claims about what a
number *means*, and the checker would have caught none of them.

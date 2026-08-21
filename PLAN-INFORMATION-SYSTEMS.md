# Alignment plan: *Information Systems* (Elsevier)

**Target venue:** Information Systems, Elsevier, ISSN 0306-4379
**Status of this document:** working plan, written 2026-08-21, after review round fifteen
**Owner decisions still open:** §9

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

- [ ] Close the last corruption still slipping the suite
- [ ] Rename the repository — it currently embeds the description §3 retracts
- [ ] Push `r10`–`r21` (not currently public)
- [ ] **Mint a Zenodo DOI**; cite it in the paper
- [ ] Write `REPRODUCE.md`: exact commands, pinned versions, expected runtimes,
      expected outputs, and the three public dataset DOIs
- [ ] State honestly in the README what the checker does **and does not** cover:
      it guards numbers thoroughly and prose only where a guard was written by hand

---

## 8. Phase 5 — Submission package

- [ ] **Highlights** — 5 bullets, ≤85 characters each
- [ ] **Cover letter** — lead with the reproducibility artifact and the
      two-organisation replication; name the reproducibility programme explicitly
- [ ] **Data availability statement** — all three logs public, none redistributed
- [ ] **CRediT** statement
- [ ] **Declaration of interests** — none
- [ ] **Suggested reviewers** — from the leakage-in-predictive-process-monitoring
      and organisational-mining lines
- [ ] **arXiv preprint posted before submission** — free, permitted, and it starts
      the citation clock during the ~244-day review

---

## 9. Open decisions (author)

1. **Title** — pick from §5.
2. **Acknowledgements** — the current text credits "a practitioner in IT service
   management." The repository records rounds 11–18 as agent-run adversarial review
   and contains no practitioner's name. The manuscript has been reworded to
   describe machine-assisted adversarial review. **If a real person did review it,
   restore their credit.**
3. **Repository URL** — `cmdb-routing-queue-baseline` embeds the retracted
   description and is printed in the paper. Proposed: `cmdb-field-admission`. The
   new repository does not exist yet.
4. Whether to pursue the reproducibility-paper track if invited (recommended: yes).

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

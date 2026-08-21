# Plan: from *major revision* to *strong accept*

**Target venue:** Information Systems, Elsevier, ISSN 0306-4379
**Written:** 2026-08-21, after round sixteen shipped
**Predecessor:** `PLAN-INFORMATION-SYSTEMS.md` — executed; see its §12
**Audience:** an autonomous agent. Read §0 before doing anything.

---

## 0. How to work

You are expected to run this to completion without asking the author
anything. That is not licence to be sloppy; it is the opposite. Every
decision you would have asked about, you take and **record with its
reasoning**, so it can be overturned cheaply later.

### 0.1 The rules this project runs on

These are not new. They are the rules the previous sixteen rounds arrived at
by getting each one wrong first. Violating them is how this paper acquired
eight corrections.

1. **If a result contradicts the paper, the paper changes.** Not the result,
   not the framing, not the emphasis. Round sixteen applied this twice and
   the second application removed the paper's own operational headline.
   Expect it to happen again.
2. **Assume the next correction flatters the result.** Seven of eight so far
   did. When a new number comes out in your favour, that is when to look
   hardest.
3. **Every constructed control introduces a confound. Null it.** Five nulls
   in this project's history were drawn at the wrong level. Before you
   believe a control, ask what it destroys *besides* the thing it means to
   destroy.
4. **Print only what your output supports.** `r7_final.py:124-148` is kept in
   the repository as the record of a script that printed a conclusion its own
   CSV contradicted.
5. **Write the corruption before you believe the check.** Three holes in the
   verifier were found in round sixteen alone, two of them *after* the first
   fix looked complete.
6. **A number is a claim; a number spelled out in letters is also a claim; a
   directional word is a claim.** `verify_paper.py` enforces the first two
   and part of the third. The third is where all eight corrections lived.

### 0.2 Recording progress

`PLAN-INFORMATION-SYSTEMS.md` was executed end to end and carried no record
of it, so the plan and the repository disagreed about the state of the work.
Do not repeat that.

- Append to **§12 of this file** after every phase: what ran, what it found,
  what changed in the paper, what it cost. Numbers in that record are checked
  against the result files like any other numbers.
- Tick the checkboxes in this file as you go, and write the outcome beside
  each, not just a tick.
- Commit per phase, on a branch, with a message that says what the phase
  found — including when it found nothing.

### 0.3 When you are blocked

Three categories, and they are treated differently.

| Kind | What to do |
|---|---|
| **A decision** (which target, which threshold, how to frame) | Take it. Record it in `submission/DECISIONS.md` with the alternatives and why you rejected them. Never park it. |
| **A credential** (GitHub admin, Zenodo, arXiv, an email account) | Stop *that item only*, write the exact steps into `submission/OWNER-ACTIONS.md`, and continue with everything else. Do not extract stored credentials to work around this. |
| **A dead end** (data does not exist, analysis does not resolve) | Record the search or the attempt in enough detail that nobody repeats it, state the negative as a finding, and move on. A negative that is documented is worth more than a gap that is silent. |

### 0.4 What you are optimising, and the honest ceiling

**Read this before you start, and again if you find yourself certain.**

"Strong accept" is a reviewer's subjective judgement and no plan can
guarantee it. What a plan *can* do is remove every reason to reject that is
within reach. So the operational target is:

> **Every objection a competent referee can raise is pre-empted by a
> measurement, and no claim in the paper depends on a choice that has not
> been varied.**

Four things are outside reach and will still be true when you finish. Say so
in the paper rather than hoping nobody notices:

- No deployment, no organisational partner, no practitioner validation.
- A single author with no institutional affiliation.
- Public benchmark data only, the newest of it from 2019.
- The Corrections section will polarise reviewers. It stays.

If you complete every phase below and the paper is still a major revision,
that is the correct outcome and not a failure of execution.

---

## 1. The diagnosis this plan is built on

Round sixteen made the paper more honest and, in one specific way, weaker.
Three problems now stand between it and a strong accept.

### 1.1 The paper's own instrument undercuts its own headline

The headline is stated in AUC: admitting one free field cuts the item's
measured value by 36.1–48.3%. The paper cites \citet{cook2007roc} saying an
AUC increment is a poor measure of incremental value. It then uses the
principled instrument — net benefit — and the effect largely evaporates:
**1.07** at the threshold where the item is worth most, against a withdrawn
4.3, and resolvably **negative** in a band above the base rate.

A referee will put those together and write: *the authors' own best
instrument contradicts their own headline.* Reporting it first does not
defuse it.

**This is the plan's central opportunity, not its central wound.** §2.

### 1.2 The lead contribution does not replicate

"Identity, not attributes" — the resolution ladder, the 256-way grouping
capturing three quarters of instance-level value — is **Rabobank only**.
BPIC 2013 carries `product` and no layer hierarchy, so it cannot carry the
finding. What replicates is the admissibility effect, which is the axis four
referees already scored as the weak one.

The paper leads with a single-log finding and replicates the less novel one.
§4.

### 1.3 Four named threats are conceded rather than measured

The Limitations section concedes: free text untested, CMDB data quality
unlike any real estate, 2013–14 era, construct validity of the target. Each
is currently a paragraph of honesty where it could be a measurement. §5.

---

## 2. Phase 1 — The reframe: the metric is chosen too

**This is the most important phase. Do it first; everything else is
evidence for it.**

The paper's conclusion already says *"the number is chosen, and whoever
writes the business case is choosing it."* Round sixteen proved that is true
of the **instrument** as well as the baseline: same data, same models, two
defensible measures, and the answer moves from 4.3 to 1.07. That is a
stronger, more general and more methodological claim than the one currently
made — and it turns §8 from an apologetic retraction into the paper's second
pillar.

### 2.1 The instrument matrix

Measure the item's value under both baselines using **every defensible
instrument**, not two:

| Instrument | Why it belongs |
|---|---|
| ROC AUC | the paper's current headline; integrates over all operating points |
| Average precision / PR-AUC | the standard answer when the positive class is what you care about |
| Net benefit, across the threshold grid | already built (`r23`) |
| Brier score and Brier skill | proper scoring rule; rewards calibration, which AUC ignores |
| Scaled Brier / Nagelkerke $R^2$ | the `williamson2021vimp` predictiveness family the paper cites |
| Detection at fixed capacity | withdrawn as a headline in round sixteen; **keep it in the matrix** as the demonstration of what a tie-degenerate instrument does |
| Expected cost at a stated cost ratio | what a buyer actually optimises |

For each: the two rungs, the reduction, and a paired bootstrap interval on
the reduction.

**Script:** `r30_instrument_matrix.py` → `results/r30_*.csv`

**What would sink it:** the reduction being stable across every instrument.
Then §1.1 is not a problem, the AUC headline stands unqualified, and this
phase collapses to a robustness paragraph. That would be a good outcome and
you should report it as one.

**What is far more likely:** the reduction is large under rank-based
instruments and small under calibration-aware ones, and the *reason* is
identifiable. Find the reason. §2.2.

### 2.2 Why the instruments disagree

Not "they disagree" — *why*. Candidate mechanisms, each testable:

- **Operating-point weighting.** AUC weights all thresholds equally; net
  benefit weights by the exchange rate. Compute the item's contribution to
  AUC as an integral over threshold and show which region carries it. If the
  item's AUC contribution comes from a region where the group-aware model is
  near its ceiling, that *is* the explanation and it is a clean one.
- **Calibration.** The item-aware model has slope 1.040 and the intake block
  1.391. Rank-based measures cannot see this; proper scores can. Quantify
  how much of the instrument gap is calibration by re-running the matrix on
  recalibrated scores — `r23` already has the machinery.
- **Score-resolution degeneracy.** 23 distinct intake scores. Already
  established for capacity; establish whether it also moves the rank-based
  instruments.

**Script:** `r31_why_instruments_disagree.py`

### 2.3 The reporting standard

The methodological contribution *Information Systems* would value. State the
measured incremental value of a feature as a function of three choices, all
of which are normally implicit:

$$V(f \mid B, m, \theta)$$

— feature $f$, **baseline** $B$ (which already-recorded fields are admitted),
**metric** $m$, **operating point** $\theta$. Show these are independent axes;
show that reporting a single number silently fixes all three; propose that a
feature-value claim be reported as a surface over them, and demonstrate the
surface on this data.

**Deliverable:** a new manuscript section, and a figure of the surface.

**This is what elevates the paper from a measurement study to a methods
contribution.** Without it you have a good empirical paper. With it you have
one that other people's papers have to cite.

---

## 3. Phase 2 — Generalise beyond one domain

**The single highest-leverage phase for novelty.** If the admissibility
effect is a property of *process event logs* rather than of CMDBs, the paper
stops being an ITSM case study and becomes a general finding about
predictive process monitoring evaluation. That is a strong-accept-shaped
contribution and it is achievable entirely with public data.

### 3.1 Assemble the corpus

At least **eight** public event logs, from at least **four** domains. All are
on 4TU.ResearchData or UCI. Candidates, with what each contributes:

| Log | Domain | Why it is here |
|---|---|---|
| BPIC 2014 (Rabobank) | ITSM | the primary; already loaded |
| BPIC 2013 incidents (Volvo) | ITSM | already loaded |
| **BPIC 2013 open problems** | ITSM | *ships in the same collection and has never been used* |
| **BPIC 2013 closed problems** | ITSM | same |
| **Italian Helpdesk log** | ITSM | ticketing with `product`, `workgroup`, `seriousness`, `responsible` — a genuine third organisation |
| UCI 498 (ServiceNow) | ITSM | richer intake block: `subcategory`, `location`, `contact_type`, `u_symptom` |
| BPIC 2017 / 2012 | lending | loan applications; high-cardinality resource stamps |
| BPIC 2019 | procurement | 250k purchase orders; vendor id is the high-cost entity |
| BPIC 2015 (5 municipalities) | permitting | **five organisations in one collection** — a replication set by itself |
| BPIC 2020 (5 sub-logs) | expenses | same |
| Sepsis, Hospital Billing | healthcare | tests whether the effect survives a non-administrative domain |
| Road Traffic Fines | enforcement | very different generative process; a good place for the effect to fail |

**Get the BPIC 2014 collection in full while you are at it.** It ships
`Detail_Interaction.csv`, which this repository has never obtained, and §9 of
the paper says in terms that it would settle the one question the paper
could not answer. See §5.1.

### 3.2 The generic protocol

The point is a *uniform* procedure, stated before it is applied, not a
per-log fishing expedition. For every log:

1. **Target.** A workflow-level outcome definable from the trace and not from
   any single event's attributes — a handover count, a rework loop, an
   SLA-style duration threshold. Declare the rule once, apply it everywhere.
2. **Intake block $B_0$.** Every attribute present on the first event.
3. **The high-cost entity $f$.** The highest-cardinality identifier that
   names a thing the organisation would have to maintain a register of — a
   configuration item, a vendor, a product, a case subject.
4. **The free overlapping field $g$.** A field on the first event that passes
   the same admissibility criterion the paper already states: it must be a
   per-event observation, tested by whether it varies across the trace.
5. **The ladder.** $V(f \mid B_0)$ and $V(f \mid B_0 \cup \{g\})$, and the
   reduction between them, under the instrument matrix from §2.

**Pre-register this.** Write the protocol, the log list and the exclusion
rules into `PROTOCOL.md` and commit it **before** running anything. Then a
reviewer can see the analyses were not chosen after seeing the answers. This
is cheap and it is worth a great deal at a rigour-focused venue.

**Script:** `r32_corpus.py` (loaders), `r33_generic_ladder.py` (the protocol)

### 3.3 What to report

The **distribution** of the reduction across logs — not an average, a
distribution, with each log named and its cohort characteristics beside it.

And then the part that matters most: **where the effect does not appear.**
Characterise what distinguishes those logs. Candidate discriminators, each
measurable before any model is fitted: the mutual information between $f$
and $g$; the concentration of $f$; whether $g$ is a resource stamp or a
classification; how many events precede the outcome.

If you can predict the reduction from log properties alone, that is a much
stronger paper than a list of case studies. **Try. Report the attempt even
if it fails.**

**What would sink this phase:** the effect appearing only in the two ITSM
logs already studied. That is still publishable — it bounds the claim
honestly to a domain — but it is not a strong accept, and you must say so in
§12 rather than dress it up.

---

## 4. Phase 3 — Make the lead contribution replicate

"Identity, not attributes" is currently Rabobank-only. Fix it or demote it.

### 4.1 Build a layer hierarchy on at least two more logs

The Rabobank ladder works because the estate has nested groupings: CI Name ⊂
Service Component ⊂ CI Subtype ⊂ CI Type. Find or construct the analogue:

- **UCI 498:** `cmdb_ci` ⊂ `subcategory` ⊂ `category`. The CI field is only
  0.2% populated, so run the ladder on the populated subset and report the
  cohort size honestly; a small-$n$ replication that is *labelled* small is
  worth more than none.
- **Helpdesk:** `product` ⊂ `support section` ⊂ `service`.
- **BPIC 2019:** item ⊂ item category ⊂ vendor ⊂ vendor country.
- **BPIC 2013:** `product` may decompose — check whether the strings have
  structure (prefix, family). If they do not, say so; do not invent a
  hierarchy by clustering, which would be a grouping chosen after seeing the
  outcome.

### 4.2 The outcome-history control, everywhere

The strongest single number in the current paper is that a per-item outcome
rate with no model and no attribute reaches 0.744 against 0.748. Run that
control on **every** log in the corpus. If entity identity is a carrier of
outcome history rather than of attributes generally, this is where it shows.

**Script:** `r34_layers_and_history.py`

### 4.3 If it does not replicate

Demote it. Move it out of the lead, state it as a single-organisation
observation, and let §2's instrument finding carry the paper. Do not keep a
non-replicating finding in the lead position because the previous plan put
it there.

---

## 5. Phase 4 — Convert the four conceded threats into measurements

### 5.1 The question the paper could not answer — answer it

§9, "One Thing We Could Not Establish": the knowledge-article reference
raises AUC to 0.805 and drives the item's value to −0.003, and the paper
cannot tell whether the field is available at creation. It says the missing
evidence is `Detail_Interaction.csv`, which it never obtained.

**Obtain it.** It is in the same public collection as the three files already
used. Then either the field is creation-time — in which case the paper's
headline is contingent on a field it must now admit, and the paper says so —
or it is not, and a section of open handwringing becomes a settled negative.

**Either outcome is a win. The current state — an unresolved question with
the evidence one download away — is the only losing one.**

**Script:** `r35_interaction_file.py`

### 5.2 Data quality: replace the caveat with a curve

The paper says its item field is 100% populated, that real CMDBs are not, and
that +0.103 should therefore be read as an upper bound. That is a caveat
where it could be a measurement.

Ablate the field: mask it at 90, 75, 50, 25, 10, 5% populated — both at
random and **non-randomly**, dropping the least-frequent items first, which
is how real estates actually degrade. Re-measure the ladder at each. Report
the value-versus-population curve.

This directly answers the single most common practitioner objection, and it
converts the paper's largest stated limitation into a figure.

**Script:** `r36_population_ablation.py`

### 5.3 Free text

The most important open question the paper leaves, and it currently has no
evidence at all. Two moves:

1. **Search the corpus for any log with a free-text or coded-symptom field.**
   UCI's `u_symptom`, Helpdesk's category strings, BPIC 2018's notes. If one
   exists, run the ladder with the text field admitted, using a simple
   bag-of-words or hashed n-gram encoder — nothing fancy, and cross-fitted.
2. **If no public log has usable free text**, say so as a finding, with the
   search recorded: which logs, which fields, why each fails. A documented
   negative closes the question; an undocumented gap invites the reviewer to
   assume you did not look.

**Script:** `r37_free_text.py`

### 5.4 Era

You cannot get 2026 data. You can decompose "practice has moved" into
properties and measure sensitivity to each:

| What changed since 2014 | Measurable proxy |
|---|---|
| discovery auto-populates the estate | §5.2's population curve, read the other way |
| event-driven incidents arrive pre-stamped | restrict to incidents opened by the dominant automated channel and re-run |
| service mapping, not item identity, is where spend goes | §4's layer ladder is exactly this measurement |
| more intake channels, fewer central desks | vary the intake mix by subsampling on the opening group's distribution |

Then say: *the counterfactual a 2026 buyer faces differs from ours along four
axes, and here is what each does to the measured value.* That is a much
stronger limitations section than an apology.

**Script:** `r38_era_sensitivity.py`

---

## 6. Phase 5 — Rebuild the manuscript

Only after §2–§5 are done. Do not restructure around findings you do not yet
have.

### 6.1 Provisional shape

| § | Content |
|---|---|
| 1 | Introduction — three contributions, **instrument-and-baseline first** |
| 2 | Background — process mining, incremental value, evaluation practice |
| 3 | The estimand: $V(f \mid B, m, \theta)$, and why one number fixes three choices |
| 4 | Protocol — pre-registered, generic, applied to $n$ logs |
| 5 | The corpus, and its properties |
| 6 | **The baseline axis** — the admissibility effect across the corpus |
| 7 | **The metric axis** — the instrument matrix, and why instruments disagree |
| 8 | **The layer axis** — which resolution pays, replicated |
| 9 | Mechanism |
| 10 | Threats, each now with a measurement (§5) |
| 11 | Limitations — the four in §0.4 that stay |
| 12 | Corrections |
| 13 | Conclusion — the reporting standard |

### 6.2 Title

The current one names a finding that may no longer be the lead. Re-pick after
§4 resolves, and record the choice and its rejected alternatives.

### 6.3 Length

*Information Systems* does not enforce a hard limit. Do not pad; do not
compress out a disclosure to save a page. The previous version was 33 pages
and could carry 45 if every page earns it.

---

## 7. Phase 6 — Harden the artifact

The reproducibility programme is the reason this venue was chosen. The
artifact is already unusual; make it unarguable.

- [ ] Extend `verify_paper.py` to the multi-log results. Every new number is
      checked or the paper does not print it.
- [ ] Grow `attack_verifier.py` with a corruption per new claim. **A claim
      without a corruption is not defended.**
- [ ] Add an environment lockfile (`conda-lock` or `pip-compile` hashes)
      alongside `requirements.txt`, and a container definition. Round sixteen
      found that a BLAS thread-count change moved a bootstrap percentile.
- [ ] `reproduce_all.py` must cover the corpus, including the download step
      for each public log, by DOI, with checksums.
- [ ] Record per-log runtimes; the corpus will be much slower than one log.
- [ ] Keep the README's statement of what the checker does **not** cover, and
      update it if the coverage changes.

---

## 8. Phase 7 — The adversarial round, against a rubric

Do not declare this finished because the checks pass. Checks catch
arithmetic; every one of this project's eight corrections was a claim about
what a number *means*.

Run **at least four independent referee passes**, each with a different
brief, each instructed to reject:

1. **The methodologist.** Is the estimand well defined? Are the nulls matched?
   Does any control destroy more than it means to?
2. **The process-mining referee.** Is the protocol faithful to how these logs
   are generated? Are the targets defensible? Is the inter-case perspective
   handled?
3. **The practitioner.** Would any of this change a funding decision? Is the
   population curve credible? Is the era argument honest?
4. **The hostile generalist.** Where does the paper overclaim by one word?
   Which sentence would you quote in a rejection?

Every objection either gets a measurement, a documented negative, or an
explicit concession in the text. **Log every objection and its disposition in
`REFEREE-LOG.md`, including the ones you dismissed and why.**

---

## 9. Phase 8 — Submission

Most of this exists from round sixteen; refresh rather than rewrite.

- [ ] Update `submission/` — highlights, cover letter, CRediT, data
      availability (now $n$ datasets), declaration, suggested reviewers
- [ ] Refresh every count quoted in the cover letter against a fresh
      `reproduce_all.py`
- [ ] `PROTOCOL.md` goes in the submission as supplementary material — a
      pre-registered protocol is a rigour signal and reviewers should see it
- [ ] Carry forward the three items in `submission/OWNER-ACTIONS.md` that
      need the author's accounts (GitHub rename, Zenodo DOI, arXiv)

---

## 10. Definition of done

Tick every box, or record why it cannot be ticked.

**Necessary — the paper is not finished without these**

- [ ] The instrument matrix is run and the reduction's dependence on the
      instrument is measured, explained and figured (§2)
- [ ] At least **eight** logs, at least **four** domains, one pre-registered
      protocol (§3)
- [ ] The layer finding either replicates on ≥2 further logs or is demoted
      out of the lead (§4)
- [ ] `Detail_Interaction.csv` obtained and §9's open question settled (§5.1)
- [ ] The population-ablation curve replaces the data-quality caveat (§5.2)
- [ ] Free text either measured or its absence documented as a search (§5.3)
- [ ] Every new number checked by `verify_paper.py`; every new claim has a
      corruption; suite passes 0 missed, 0 skipped
- [ ] Four adversarial passes run, every objection dispositioned in
      `REFEREE-LOG.md`
- [ ] The manuscript builds with 0 errors and 0 undefined references
- [ ] §12 of this file records what each phase found, including the phases
      that found nothing

**Sufficient — what would actually make a referee write "strong accept"**

- [ ] A finding that is **general**: the effect is a property of process
      logs, with named conditions under which it appears and does not
- [ ] A **methods contribution** other papers must cite: the
      $V(f \mid B, m, \theta)$ reporting standard, demonstrated
- [ ] A **reproducibility artifact** that a stranger runs in one command and
      that fails loudly when the paper is wrong
- [ ] **No claim resting on an unvaried choice.** For every number in the
      abstract, a reader can find where the paper varies the choices behind
      it

**And the honest test.** Before you declare this done, write the rejection
letter yourself — the strongest one you can, in the voice of a referee who
wants to reject. If you can write a persuasive one, you are not finished. If
the best you can manage is the four items in §0.4, you are.

---

## 11. What this plan deliberately does not attempt

Recorded so it is not proposed as a fresh idea in round nineteen.

- **A deployment or an industry partner.** Not obtainable by an agent, and a
  fabricated one would be the exact failure the paper is about.
- **Modern proprietary data.** Same.
- **A practitioner acknowledgement.** `submission/OWNER-ACTIONS.md` §5.2
  stands: if a real person reviewed this work, only the author can say so.
- **Removing the Corrections section.** It will cost some referees. It is the
  most honest thing in the paper and it stays.
- **The checker paper.** `PLAN-INFORMATION-SYSTEMS.md` §11 and `HANDOFF.md`
  §19.8 argue that the verification apparatus is a stronger contribution than
  the CMDB finding and belongs at MSR or EMSE. That remains true and remains
  *after* this submission, not instead of it.

---

## 12. Execution record

*Append after each phase. Nothing here until something has run.*

| Phase | Started | Outcome | Cost |
|---|---|---|---|
| | | | |

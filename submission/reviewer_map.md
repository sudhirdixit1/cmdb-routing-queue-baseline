> **SUPERSEDED — round eighteen.** This file maps objections to sections of
> *Four Choices Behind One Number*, the manuscript a referee for *Information
> Systems* recommended rejecting. Round nineteen replaced that manuscript with
> *Specification Surfaces for Incremental Predictive Performance*, so **every
> section number below points into a document that is no longer submitted**,
> and several of its claims were withdrawn — the three-log corpus became
> nineteen log--target pairs across thirteen logs, and the headline it defends
> was retracted as inflated by an intercept-only baseline.
>
> The current map is `submission/response_to_referee.md`, whose cross
> references `scripts/check_response_refs.py` checks against the built
> manuscript. This file is kept because the referee log cites it, not because
> it is current.

# The reviewer's map

One row per objection, and the section that answers it. Nothing here is an
argument; every cell points at a measurement, a construction, a documented
negative or an explicit concession.

**How to use it.** Find your objection. If it is not here, it is either in
`REFEREE-LOG.md` — which carries every objection seven referees raised over
eighteen rounds and its disposition — or it is new, and we would like to know.

---

## The seven objections a referee is most likely to reach for

| # | The objection | Answered in | With |
|---|---|---|---|
| **D1** | "This assembles known critiques — Cook on AUC increments, Hand on metric incoherence, Vickers–Elkin on operating points, Williamson–Covert on baseline-relativity — and measures their magnitudes on one dataset." | §4 (the audit); §3.3 and Appendix A (the propositions) | A pre-registered audit of 600 papers: **not one of 20 read reports the increment across a range of operating points, and not one across a range of register populations.** Three propositions establishing what *can* happen before the measurements show what does. |
| **D2** | "The empirical result is a null on one log. What did we learn?" | §14; §12; Conclusion | That a register costing money to build adds **nothing measurable** over two fields the organisation already records — one of which no baseline in this literature would have admitted. Stated as the finding, not buried. |
| **D3** | "The generality claim was registered and falsified. The corpus section reports a failure." | §12.5 | The falsification is followed by a **registered prediction**, frozen before either held-out log was downloaded, and tested. It produced two correct predictions — **both negative, so the rule's positive half was never tested**, and the paper says so rather than claiming a win. |
| **D4** | "Everything is on BPI Challenge 2014. 'Each choice moves the answer by more than the effect' is an n = 1 claim." | §10; §11 | The full four-axis surface on **all three logs** whose reduction is resolvable — three organisations, three information systems, two domains. **And the claim is weaker than we first wrote it**: restricted to baselines an analyst would actually build, the baseline axis moves *R* by 0.346, 0.347 and 0.382 against reference values of 0.350, 0.378 and 0.471 — larger than the effect on BPI Challenge 2014, smaller on the other two. A referee pass found that before it shipped and §10 states both versions. Plus a simulation whose true answer is known by exhaustive enumeration. |
| **D5** | "Twelve self-reported errors. Why should I trust the thirteenth number?" | §16; Appendix B | The main text reports the **defect classes**, not the incidents; the incidents are in an appendix. 1,388 checks against regenerated result files, 0 failed; a corruption suite of 255 mutations that has found every hole this apparatus has ever had, including three this round. |
| **D6** | "Forty-two pages, single unaffiliated author, no deployment. Is this the right journal?" | `DECISIONS.md` §15; §17 Limitations | The venue decision was **re-taken** against six criteria fixed in advance, and criterion 6 was counted rather than assumed: of 3,360 recent articles across eight candidate venues, **five are single-author and unaffiliated**. That is in the Limitations and in the cover letter, not in a hope. |
| **D7** | "The proposed standard is a paragraph of prose. Nothing here makes it easier to follow than to ignore." | §13.1; `fieldvalue/` | A package that computes the surface in four lines and **refuses to emit a single number**. 91 tests. Re-deriving the paper's headline through it agrees with our own pipeline on 20 of 20 quantities to 2.2 × 10⁻¹⁶ — and found an error in this paper's prose on its first run. |

---

## The methodological objections

| The objection | Answered in | With |
|---|---|---|
| "Your baseline is under-specified — the thing you are complaining about." | §5; §15 | `Priority` is a deterministic function of `(Impact, Urgency)` on this log and is disclosed as such; dropping it moves intake AUC from 0.562 to 0.564. |
| "A random split would be fine." | §5; §15 | The split is temporal because a random split on a process log leaks the future. Both censoring boundaries are measured: left-censored incidents are reassigned at 81.2% against 40.0% for those kept; truncating up to a month early moves the shrinkage between 42% and 45%. |
| "The estimator might be biased for a ratio of two differences of two fitted AUCs." | §11 | Against a world whose answer is known by enumeration of a 960-cell space: largest absolute bias 0.0044, bootstrap coverage 0.850–0.975 against a nominal 0.95. |
| "The interval near 1 in §14 is doing a lot of work." | §11 | Coverage at the boundary is 0.850, and the paper says an interval near 1 should be read as weaker evidence. |
| "One pipeline, one author, one chance to be systematically wrong." | §13.1 | An independent implementation of the metrics in numpy; 20 of 20 quantities agree. What is *not* independent — scikit-learn's estimator and the shared cohort loader — is stated. |
| "The tie conventions are doing the work." | §7; Appendix E | Both rank statistics are put on the only implementable convention and the gap *widens*: 43.6% under AUC against 71.2% under average precision. |
| "AUC is the wrong instrument." | §7; §3.3 | Six instruments are reported and AUC is the *smallest* of them. Proposition 2 states exactly which instruments can and cannot see calibration. |
| "The reduction is an artifact of collinearity / dimensionality / temporal structure." | Appendix J | Three nulls, all reported: 78.8% of articles map to one item against 80.7% for the opening group; five matched-mass partitions reach base AUC at most 0.6479 where the real field reaches 0.8041; a partition matched on cell size *and* on twenty time strata does not reproduce either number. |

---

## The objections about the audit specifically

| The objection | Answered in | With |
|---|---|---|
| "Your frame is convenient." | §4.1; `AUDIT-PROTOCOL.md` §2 | Two frames, both enumerated by a public API, both queries executed verbatim by the script. The cap and the sample seed are registered. |
| "You dropped BPM, ICPM and CAiSE because they were inconvenient." | §4.1 | No: they are **not machine-enumerable in OpenAlex**, and the counts that establish that were taken before any screening (BPM: 69 works 2019–2026, 0 open access). They are covered through the citation frame and the venue mix is reported. |
| "A mechanical coder is not a reader." | §4.3; `AUDIT-PROTOCOL.md` amendment 2 | Agreed, and it is measured: against a read of 30 papers the coder missed 39 `yes` codes and asserted 9 a read does not support. **The adjudicated proportions are the paper's primary numbers; the mechanical ones are labelled a lower bound.** |
| "One author, so no inter-rater reliability." | §4.4 | Correct, and the paper does not call it that. What is reported: every code with its quote and page; agreement between two independent implementations of the same rules (κ 0.256–0.501, which is *poor*, and is printed); and the seven-day blind re-code written into `OWNER-ACTIONS.md` because it needs elapsed time and a human. |
| "You only read open-access papers." | §4.2; §17 | Yes. 369 of 600 full texts retrieved, 61.5%; the 231 lost are recorded with their reason, and the paper does not assume the loss is uncorrelated with the codes. |
| "Would you accept this audit if your own paper were in the sample?" | `results/r40_coding.csv`; §4.3 | Every row carries the DOI, the quote and the PDF page, so any row can be checked in a minute; a spot-check of 9 quoted codes across 5 papers found the quote on the stated page in 9 of 9. The screen's precision is 66.7%, so a third of mechanically included papers are not in scope — `results/r40_adjudication.csv` says which, with a note per paper. |
| "The topical pre-filter selects careful papers." | §4.4 | Nulled against the unfiltered frame: the filtered arm is **more** careful on every comparable code, by up to 23.3 points, so the reported failure is a lower bound. |
| "Your propositions' constructibility thresholds are arbitrary." | Appendix A | Measured across 16 tolerance cells: the count runs 8 to 12, and the paper names the cell it reports. |

---

## The objections we agree with and cannot answer

These are in §17 (Limitations) in the referee's own terms, not softened.

- **No deployment, no organisational partner, no practitioner validation.** The
  paper is a retrospective study on public benchmarks, offered as an
  evaluation practice.
- **A single author with no institutional affiliation.** Counted rather than
  excused: 5 of 3,360 recent articles across eight candidate venues fit that
  profile.
- **Public benchmark data only; the newest event log is from 2019.** The
  simulation of §11 is era-independent and answers part of this, not all of
  it.
- **No inter-rater reliability on the audit.** §4.4 says what is done instead
  and does not claim it is equivalent.

---

## Where everything is

| | |
|---|---|
| pre-registered corpus protocol | `PROTOCOL.md` |
| pre-registered audit protocol | `AUDIT-PROTOCOL.md` |
| pre-registered prediction | `PREDICTION.md` |
| every objection and its disposition | `REFEREE-LOG.md` |
| every decision and its rejected alternatives | `submission/DECISIONS.md` |
| what only the author can do | `submission/OWNER-ACTIONS.md` |
| how to reproduce, and what that does not establish | `REPRODUCE.md` |
| the audit's coding sheet, with quotes and pages | `results/r40_coding.csv` |
| the package | `fieldvalue/`, `examples/worked_example.ipynb` |

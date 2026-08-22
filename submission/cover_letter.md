# Cover letter

**To:** The Editors-in-Chief, *Empirical Software Engineering*
**Re:** *Four Choices Behind One Number: Reporting the Incremental Value of a
Recorded Field*
**Article type:** Research article

---

Dear Editors,

I am submitting the manuscript above for consideration in *Empirical
Software Engineering*. It is a methodological paper with a pre-registered
literature audit, three propositions, an empirical demonstration on public
event logs, a prospective test on held-out data and a software artifact.

**Why this journal, and the decision recorded rather than inherited.** An
earlier version of this work was aimed at *Information Systems*, when it was
a CMDB empirical study. Its centre of gravity has moved, so I re-took the
decision against six criteria fixed before comparing venues rather than
carrying the old one forward. Three of the criteria pointed here: EMSE
publishes evaluation-methodology work with empirical demonstrations, treats
systematic literature work as a standing category, and has an open-science
policy that engages what this work's strongest asset actually is. Two counts
decided it. EMSE has published six papers in 2019–2026 whose title or abstract
describes them as registered reports, against zero at the incumbent — and this
submission carries a pre-registered protocol, a pre-registered audit and a
pre-registered prediction. Its topical share, the fraction of recent articles
carrying this paper's vocabulary, is 17.3% against 13.5%. The full comparison,
including the venues I rejected and why, is in `submission/DECISIONS.md` §15.

**One question for the editor.** If your registered-reports handling is open
to a submission whose results already exist, I would welcome that route: the
design of this work was registered before its results, three times over, and
a review of the design would be a fairer test of it than a review of the
findings.

**What the paper contributes.** Papers, business cases and tool evaluations
report what a recorded field is worth as a single number. That number is a
function of four choices which are almost never stated: the baseline of
already-recorded fields the comparison may contain, the metric, the operating
point, and the population of the register the field reads from. I write the
quantity as *V(f | B, m, θ)*, propose that a feature-value claim be reported
as a surface over those arguments, and then demonstrate on one dataset that
each choice moves the answer by more than the effect being reported.

The demonstration is a configuration management database on a public log of
45,455 incidents. Admitting one further field the organisation already
records takes the item's value from +0.183 AUC to +0.103; admitting a second
takes it to +0.001 [−0.002, +0.003]. Six defensible instruments on identical
scores put the reduction between 43.7% and 60.3%, and ROC AUC — the figure
the previous version of this work reported — is the smallest of them. Net
benefit, read at one operating point, puts it between 4.7% and 134.1%
depending on the point, and the item is resolvably harmful in a band above the
base rate. At half population the register is worth +0.082 or +0.064
depending on which half is missing.

**What this version adds, and what came back against it.** A pre-registered
audit of 600 published papers, to establish that the practice failure is real
rather than asserted; three propositions, constructed and executed, about what
can happen before the measurements show what does; the whole surface on all
three logs whose reduction is resolvable; a simulation whose true answer is
known by enumeration, which puts the estimator's bias at 0.0044 and its
coverage at 0.850–0.975; and a package that computes the surface and refuses
to emit a single number.

Three of those came back against the paper and all three are in it. The audit
**refuted the strong form of this paper's own premise** — two in five papers
do state their baseline, half do argue their metric — and the claim is
withdrawn and replaced by the narrower one the data support: not one of the
twenty papers read reports what a feature is worth across a range of operating
points, or across a range of register populations. The prospective test
produced two correct predictions, **both negative**, so half the registered
rule remains untested and the paper says so. And an independent
re-implementation of the estimator found the twelfth error in this paper's own
prose on its first run.

**On the author profile, which I would rather you heard from me.** I am a
single author with no institutional affiliation and no deployment to report.
Rather than excuse that I counted it: of 3,360 research articles published
2024–2026 across the eight venues I considered, five are single-author and
unaffiliated. This submission is close to unprecedented on that axis at every
one of them, including yours. What I can offer instead of an affiliation is an
artifact: 1,386 checks that re-derive every number in the manuscript from a
result file, a corruption suite of 253 mutations that has found every hole
that checker has ever had, and a one-command reproduction from the raw logs.

**The strongest evidence I can offer for the reporting standard is that
following it removed my own headline.** The previous version of this work
declined to admit a second free field because it could not establish when the
value was written, and named the file that would settle it. That file ships in
the same public collection and I had not obtained it. I obtained it, it
settles the question, and admitting the field takes the result from +0.103 to
+0.001. Section 13 reports that, with three nulls, and Section 15 records it as
one of the paper's corrections rather than as progress.

**I tried to make the finding general and it did not go.** I pre-registered a
protocol — the corpus, two targets, the rules assigning every attribute to a
role, six exclusion codes, the estimator, the seed, the instruments, and the
outcome that would falsify the claim — and committed it before any corpus
result file existed, in a commit that adds no result file. The rules admit 13
logs across six domains; the reduction is resolvably positive on three. The
claim I registered is falsified by its own criterion and Section 11 says so.
What the corpus does establish is the precondition, and it is the same
phenomenon the paper measures directly on the primary log: where the opening
field is nearly constant — in BPI Challenge 2012 and every BPI Challenge 2020
sub-log every case is opened by the same actor — there is nothing for it to
absorb.

**The artifact.** The submission is accompanied by a public repository
containing every analysis script, the pre-registered protocol, a referee log
recording twenty-two adversarial objections with their dispositions, every
derived result file, the figure generators, an environment locked by artefact
hash and a container that additionally pins BLAS thread counts, and a
verification harness that recomputes each of the 417 numeric literals in the
manuscript from a result file or from the raw data. It fails if any literal in
the body is unaccounted for, tests rounding equality at the paper's printed
precision rather than a tolerance, and treats range endpoints as floors and
ceilings rather than rounding them — a discipline that caught six real defects
in this round's new tables on its first run. A second harness, a suite of 199
corruptions drawn from defects found in earlier versions of this work, is the
verifier's own regression test. One command fetches all twenty-four datasets
by DOI, checksums them, and reproduces the whole result set.

I want to be equally precise about what the harness does **not** do. It guards
numbers thoroughly and prose only where a guard was written by hand. The paper
reports eleven of my own errors as results rather than editing them away, and
all eleven are claims about what a number *means* — the checker would have
caught none of them. Two of the three found in this round are sentences in
which every individual literal was correct and the relation the prose asserted
between them was not: an extremum that was the worst of the points the paper
happened to name, and a count identified with an interval. Both are reported,
both are now checked, and I regard the defect class as a contribution rather
than an embarrassment.

**Scope fit.** The estimand is an evaluation-practice question; the
demonstration is prediction at case creation on incident event logs; and the
paper's semantic core is an organisational-mining question — establishing from
the log, rather than from documentation, what a stamp on an opening event
denotes and when it was written. I engage the inter-case perspective directly,
by admitting four free creation-time congestion features and reporting what
they do to the result.

**Declarations.** The manuscript is original, is not under consideration
elsewhere, and has not been published previously. There is a single author
with no institutional affiliation and no funding. I declare no competing
interests; I have no relationship with any vendor in this space, nor with any
of the organisations whose logs are analysed. All twenty-four datasets are
public benchmark logs and none is redistributed. Rounds eleven to seventeen of
the adversarial review that produced this manuscript were machine-assisted;
this is disclosed in the paper's Acknowledgements and in the CRediT statement,
as your generative-AI policy requires. Suggested reviewers are listed
separately.

Thank you for considering the manuscript.

Yours sincerely,

**Sudhir Dixit**
Independent Researcher
sudhir.dixit1@gmail.com

---

## Notes to self before sending — delete this section

- [ ] Replace the repository URL throughout once the renamed repository
      exists (`submission/OWNER-ACTIONS.md` §1; the manuscript prints
      `github.com/sudhirdixit1/cmdb-field-admission`, which is **not yet
      created** — the live remote is still `cmdb-routing-queue-baseline`).
- [ ] Add the Zenodo DOI once minted, both here and in the manuscript's
      Acknowledgements. `.zenodo.json` is ready to upload.
- [ ] Post the arXiv preprint **before** submitting, and add its identifier
      to this letter. Elsevier permits preprints; posting first starts the
      citation clock during a ~244-day median review.
- [ ] Confirm the three counts in the artifact paragraph against a fresh
      `python scripts/reproduce_all.py` — 608 literals, 255 corruptions, 13
      admitted logs. They move whenever the paper does, and the last version
      of this letter quoted numbers that had.
- [ ] Offer `PROTOCOL.md` as supplementary material in the submission system,
      not only as a repository file. A pre-registration a referee has to go
      looking for is doing half its job.

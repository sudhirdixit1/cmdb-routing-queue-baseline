# Cover letter

**To:** The Editors-in-Chief, *Information Systems*
**Re:** *Four Choices Behind One Number: Reporting the Incremental Value of a
Recorded Field*
**Article type:** Research article

---

Dear Editors,

I am submitting the manuscript above for consideration in *Information
Systems*. It is a methodological paper with an empirical demonstration on
public event logs, and I am sending it to this journal for a specific reason:
of the venues I considered, this is the one whose reproducibility validation
programme is designed to engage with what the work's strongest asset actually
is.

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
benefit, read at one operating point, puts it between 6.3% and 119.2%
depending on the point, and the item is resolvably harmful in a band above the
base rate. At half population the register is worth +0.082 or +0.064
depending on which half is missing.

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
      `python scripts/reproduce_all.py` — 417 literals, 199 corruptions, 13
      admitted logs. They move whenever the paper does, and the last version
      of this letter quoted numbers that had.
- [ ] Offer `PROTOCOL.md` as supplementary material in the submission system,
      not only as a repository file. A pre-registration a referee has to go
      looking for is doing half its job.

# Cover letter

**To:** The Editors-in-Chief, *Information Systems*
**Re:** *Identity, Not Attributes: What Configuration Data Contributes to
Incident Prediction in Two Organisations*
**Article type:** Research article

---

Dear Editors,

I am submitting the manuscript above for consideration in *Information
Systems*. It is an empirical study on two public ITSM event logs, and I am
sending it to this journal for a specific reason: of the venues I considered,
this is the one whose reproducibility validation programme is designed to
engage with what the work's strongest asset actually is.

**The artifact is the point, and it is finished.** The submission is
accompanied by a public repository containing every analysis script, every
derived result file, the figure generator, and a verification harness that
recomputes each of the 325 numeric literals in the manuscript from a result
file or from the raw data. It fails if any literal in the body is
unaccounted for, tests rounding equality at the paper's printed precision
rather than a tolerance, and treats range endpoints as floors and ceilings
rather than rounding them. A second harness — a suite of 149 corruptions
drawn from defects found in earlier versions of this work — is the
verifier's own regression test. One command reproduces the whole result set
from the raw logs; `REPRODUCE.md` gives the dataset identifiers, the pinned
library versions, expected runtimes and expected output. Should the
manuscript be selected for the reproducibility validation programme, I would
welcome that, and the repository is built for it.

I want to be equally precise about what the harness does **not** do. It
guards numbers thoroughly and prose only where a guard was written by hand.
The paper reports eight of my own errors as results rather than editing them
away, and all eight are claims about what a number *means* — the checker
would have caught none of them. Both the repository and the manuscript say
so in those words.

**What the paper contributes.** A CMDB programme is justified by the
analytics it enables, and that justification is a comparison against a
baseline the analyst chooses. On these logs the answer turns out to be set
less by the configuration data than by two decisions that are rarely written
down. First, which layer is being bought: a 256-way service-component
grouping captures three quarters of what instance-level item identity is
worth, and instance identity adds +0.023 AUC over it — while a per-item
outcome rate with no model and no configuration attribute of any kind reaches
0.744 against the full model's 0.748. What the CMDB supplies on this task is
a stable identifier under which outcome history accumulates, not the
attributes it is bought for. Second, which already-recorded fields the
baseline may contain: admitting one free field halves the item's measured
value, and the reduction runs 36.1% to 48.3% across the design space.

**It replicates across organisations.** The same ladder, on the BPI Challenge
2013 log from Volvo IT — a second organisation, a second tool and a second
country — gives a reduction of 61.3% [54, 68] on that challenge's own
ping-pong target and 43.9% [31, 55] at a stricter threshold. I state in the
paper that the free field is more tightly coupled to the target there, so
the Volvo figure should be read as an upper bound rather than a second draw
from the same distribution.

**On the corrections.** Two of the eight were found in the round that
produced this version, and the larger of them removes the paper's own
previous operational headline: a factor of 4.3, which I now show has a sign
set by how ties inside a coarse baseline's scores are broken, and which
decision curve analysis replaces with 1.07. The manuscript also reports a
band of decision thresholds in which the configuration item is worth nothing
at all over the group-aware baseline. I would rather submit a paper that says
these things than one that does not.

**Scope fit.** The task is prediction at case creation on incident event
logs; the paper's semantic core is an organisational-mining question —
establishing from the log, rather than from documentation, what a group
stamp on an opening event denotes — and its methodological core is
baseline specification and leakage-adjacent field admission in predictive
process monitoring. I have engaged the inter-case perspective directly, by
admitting four free creation-time congestion features and reporting what
they do to the result.

**Declarations.** The manuscript is original, is not under consideration
elsewhere, and has not been published previously. There is a single author
with no institutional affiliation and no funding. I declare no competing
interests; I have no relationship with any vendor in this space, nor with
either of the organisations whose logs are analysed. All three datasets are
public benchmark logs and none is redistributed. Rounds eleven to eighteen of
the adversarial review that produced this manuscript were machine-assisted;
this is disclosed in the paper's Acknowledgements and in the CRediT
statement, as your generative-AI policy requires. Suggested reviewers are
listed separately.

Thank you for considering the manuscript.

Yours sincerely,

**Sudhir Dixit**
Independent Researcher
sudhir.dixit1@gmail.com

---

## Notes to self before sending — delete this section

- [ ] Replace the repository URL throughout once the renamed repository
      exists (§9 of the plan; the manuscript prints
      `github.com/sudhirdixit1/cmdb-field-admission`, which is **not yet
      created** — the live remote is still `cmdb-routing-queue-baseline`).
- [ ] Add the Zenodo DOI once minted, both here and in the manuscript's
      Acknowledgements. `submission/zenodo.json` is ready to upload.
- [ ] Post the arXiv preprint **before** submitting, and add its identifier
      to this letter. Elsevier permits preprints; posting first starts the
      citation clock during a ~244-day median review.
- [ ] Confirm the counts in paragraph two against a fresh
      `python scripts/reproduce_all.py` (325 literals, 149 corruptions) —
      they move whenever the paper does.

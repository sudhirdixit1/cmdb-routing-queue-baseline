# Data availability statement

All twenty-four event-log files this study fetches are public and none is
redistributed by the author. The registered admission rules of Section 5 admit
thirteen of them, giving nineteen log--target pairs; the eleven that are
excluded are listed with their exclusion code in Table S12 of the supplement, so
a reader can see what was screened out as well as what was kept. The analysis code, the pre-registered protocol,
the intermediate result files, the figures and the checker that recomputes
every quantity printed in the paper are available in the repository cited in
the manuscript.

## Statement for the submission system

> All data used in this study are publicly available benchmark event logs,
> cited in the manuscript by persistent identifier. No new data were
> generated. `scripts/fetch_corpus.py` in the accompanying repository
> resolves every dataset's DOI, downloads the named file and records its
> SHA-256, so a reader can verify that the corpus they hold is the corpus the
> paper was written against. Analysis code, the pre-registered protocol,
> derived result files and a verification harness that recomputes every
> number reported in the paper are openly available at the repository cited
> in the Acknowledgements, archived at the DOI given there.

## The datasets, by persistent identifier

Twenty-four files across seven domains. The first three carry the primary
analysis; the rest are the pre-registered corpus of Section 5.

| Log | Domain | Identifier |
|---|---|---|
| BPI Challenge 2014 (incident, activity and **interaction** detail) | ITSM | `doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35` |
| BPI Challenge 2013, incidents | ITSM | `doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee` |
| Incident management process enriched event log (UCI 498) | ITSM | `doi:10.24432/C57S4H` |
| BPI Challenge 2013, open problems | ITSM | `doi:10.4121/uuid:3537c19d-6c64-4b1d-815d-915ab0e479da` |
| BPI Challenge 2013, closed problems | ITSM | `doi:10.4121/uuid:c2c3b154-ab26-4b31-a0e8-8f2350ddac11` |
| Help desk log of an Italian company | ITSM | `doi:10.4121/uuid:0c60edf1-6f83-4e75-9367-4c63b3e9d5bb` |
| BPI Challenge 2012 | lending | `doi:10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f` |
| BPI Challenge 2017 | lending | `doi:10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b` |
| BPI Challenge 2019 | procurement | `doi:10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1` |
| BPI Challenge 2015, five municipalities | permitting | `doi:10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1` |
| BPI Challenge 2020, five sub-logs | expenses | `doi:10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51` |
| Sepsis cases | healthcare | `doi:10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460` |
| Hospital billing | healthcare | `doi:10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741` |
| Road traffic fine management | enforcement | `doi:10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5` |

The BPI Challenge collections are distributed by 4TU.ResearchData under the
terms attached at each DOI; the UCI log is distributed under CC BY 4.0. The
repository contains no row of any of them: `data/` is excluded from version
control, and the one thing that is tracked —
`data/corpus/CHECKSUMS.txt` — is a list of hashes.

**One file is new to this version and is worth naming.** The BPI Challenge
2014 collection ships `Detail_Interaction.csv`, which the previous version of
this paper did not obtain and named as the evidence that would settle its
Section 9. It is obtained, it settles it, and Section 7 reports the result.

## Pre-registration

`PROTOCOL.md` in the repository fixes the corpus, the two targets, the rules
that assign every attribute to a role, the six exclusion codes, the estimator,
the split, the seed, the instruments, the discriminators and the outcome that
would falsify the claim. It was committed **before** any corpus result file
existed, in a commit that adds no result file; `git log --stat` shows that.
Eight amendments were made after running the outcome-free role assignment and
before fitting any model; each is recorded in that file with its reason, and
Section 5 of the manuscript summarises them.

`PROTOCOL.md` is offered as supplementary material.

## What is in the repository, and what it does not cover

The repository holds every script, every derived `results/*.csv`, the LaTeX
source, `requirements.lock` (every dependency pinned by artefact hash), a
`Dockerfile` that additionally pins the BLAS thread counts, and
`scripts/verify_paper.py`, which recomputes each numeric literal in the
manuscript from a result file or from the raw data and fails if any literal is
unaccounted for. `scripts/attack_verifier.py` is that checker's own regression
suite: 255 corruptions.

The checker guards **numbers** thoroughly and **prose** only where a guard was
written by hand. It cannot tell you that an interpretation is sound. The
README says so in the same words. The correction register in the archive
carries twenty-eight corrections grouped by class, and **the largest class is
sentences in which every printed number was correct and the relation asserted
between them was not** --- which the generated-macro discipline cannot make
impossible. It makes one sub-class of it structurally impossible; the rest
is what the adversarial reading passes are for.

---

## The literature audit's frame and coding sheet (Supplement S18)

The audit does not analyse a dataset; it analyses **published papers**, and
the frame that selects them is machine-enumerable so a reader can rebuild it.

| what | where |
|---|---|
| the enumeration | the OpenAlex API, `https://api.openalex.org`; every query is executed verbatim by `scripts/s06_audit2.py`, and the PRISMA flow it produces is `results/s06_prisma.csv` |
| the sample | `results/s06_sample.csv` — 600 works, drawn under the pre-registered design of `AUDIT-PROTOCOL-2.md` |
| the coding sheet | `results/s06_coding.csv` — every sampled work with its codes |
| the agreement | `results/s06_agreement.csv` — per-code agreement and $\kappa$ from the two-screen design, with `results/s06_two_screens.csv` behind it |
| the adjudication | `results/s06_applicability.csv` and `results/s06_missing.csv`, with `data/audit/adjudication/*.txt`, the deterministic extract each was coded from |

**Full texts are not redistributed.** `scripts/s06_audit2.py --fetch`
retrieves them from each work's own open-access location and caches them under
`data/audit/fulltext/`, which is git-ignored. Everything needed to re-fetch
them is in `results/s06_sample.csv`.

## The held-out logs (Supplement S1)

| Log | Domain | Identifier |
|---|---|---|
| BPI Challenge 2011, a Dutch academic hospital | healthcare | `doi:10.4121/uuid:d9769f3d-0ab0-4fb8-803b-0d1120ffcf54` |
| BPI Challenge 2018, EU agricultural subsidies | agriculture | `doi:10.4121/uuid:3301445f-95e8-4ff0-98a4-901f1f204972` |

Both were named in `PROTOCOL.md` §2 in the previous round as considered and
not included. Neither was downloaded, parsed or inspected until after
`PREDICTION.md` was committed; `git log --stat` shows the order.

## The worked example (Supplement S7)

| Dataset | Identifier |
|---|---|
| UCI Adult (Census Income) | `doi:10.24432/C5XW20` |

Chosen because it is **not** one of this paper's event logs: the point of the
example is that the baseline choice moves the answer on data that has nothing
to do with configuration management.

# HANDOFF

For whoever picks this up next. Read the "Eight withdrawn findings" section
before you write any code — it is the part that will save you time.

---

## 1. What this is

A single-organisation empirical study for **IAAI-27, Deployment Insights
track**. Deadline **8 September 2026** (AAAI's page; the OpenReview listing
showed 9 September — treat the earlier as binding). Review is not anonymous.

**The surviving claim, in full:**

> On the BPI Challenge 2014 incident log (Rabobank Group ICT, 45,455
> incidents), knowing which configuration item an incident concerns is worth
> **+0.183 AUC** for predicting misrouting when measured against four intake
> fields, and **+0.103 [+0.094, +0.114]** when the baseline also includes the
> opening assignment queue — a field the service desk records for free at
> intake. The measured value of a CMDB is therefore dominated by a
> field-admission decision that is usually left implicit.

Plus a mechanism: the routing decision is very nearly a function of the item
(randomising the queue label within each item still retains **91%** of the
queue's gain, against a matched floor of **2%**), and the queue's unique
contribution once the item is known is **under 0.01 AUC**.

Everything else that was ever claimed has been withdrawn. See §4.

---

## 2. Where things are

```
emptycmdb/
  paper/iaai27_empty_cmdb.tex   the draft (2,217 words, 1 figure, 3 tables)
  paper/references.bib          7 entries, all author lists verified
  paper/figG1_baselines.png     the only figure the .tex references
  scripts/                      see below
  results/                      every CSV the scripts produce
  README.md                     reproduction instructions
```

Raw data is **not** in this folder. It lives in the session scratchpad at
`…\scratchpad\emptycmdb\data\raw\` and must contain `Detail_Incident.csv`,
`Detail_Change.csv`, `Detail_Incident_Activity.csv` from the BPIC 2014
collection (`doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35`). If you
are starting fresh, re-download them; `common.py` expects that path.

### Scripts that matter

| file | role |
|---|---|
| `common.py` | loaders, missing-token handling, paths |
| `r4_final.py` | **the canonical loader.** Cohort, baselines, stability, mutation disclosure. Everything else imports `r4_final as M` |
| `r5_final.py` | nulls, mutation sensitivity, leak evidence |
| `r6_final.py` | gains with pooled uncertainty |
| `r8_final.py` | mechanism, design-space range, deployment scoping |
| `verify_paper.py` | checks every number in the paper against a result file |
| `attack_verifier.py` | regression suite for the verifier — 14 corruption classes |
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
python scripts/verify_paper.py     # 111 checks, 0 failed, 0 unaccounted
python scripts/attack_verifier.py  # 14 caught, 0 missed
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

**Two things that are NOT artifacts** and survived every attack: the
**+0.103** headline (33σ outside a matched-dimension null, stable across six
splits, three cleaning cutoffs, four penalty settings, mutation
restriction) and the **91% / 2% mirror** (89-point margin over its floor).

*Correction (2026-08-19).* An earlier version of this line claimed the
headline survived "two estimator families." It does not: the surviving
pipeline (`r4`/`r5`/`r6`/`r8`) uses one-hot logistic regression **only**.
Gradient boosting appears exclusively in the withdrawn `e*` and `r1`
scripts, on the pre-queue-baseline framing. `r5_final.py` REPAIR 6 computes
why boosting is not usable here — 2,554 items collapse into 256 bins — and
that justification belongs in the paper, which currently states the
one-estimator limitation without giving the reason.

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

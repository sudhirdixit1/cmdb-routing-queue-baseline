# Pre-registered protocol: measuring a feature's incremental value across a corpus of event logs

**Registered:** 2026-08-21, round seventeen
**Registered by:** committed to `round-seventeen-strong-accept` **before** any
model in §5 below was fitted on any log other than the two already published.
The commit that adds this file adds no result file, and the commit message
says so. A reader who does not believe that can check: `git log --stat` shows
this file arriving alone, and every `results/r33_*.csv` arriving later.

**Why this exists.** Rounds one to sixteen of this project chose the analysis
after seeing the log. Eight findings were withdrawn, and every one of them was
an artifact of a control chosen after the fact. Extending to a corpus multiplies
the opportunity: with twenty-three files and seven domains, an analyst who picks
the target, the entity and the baseline per log can produce any distribution of
results they like. This document fixes every one of those choices in advance,
states the exclusion rules before the logs are inspected, and names the outcome
that would falsify the claim.

---

## 1. The estimand

For a feature $f$, a baseline feature set $B$, a metric $m$ and an operating
point $\theta$, define the **incremental value**

$$V(f \mid B, m, \theta) \;=\; m\bigl(B \cup \{f\},\ \theta\bigr) \;-\; m\bigl(B,\ \theta\bigr)$$

and, for two nested baselines $B_0 \subset B_1$, the **admissibility reduction**

$$R(f \mid B_0, B_1, m, \theta) \;=\; 1 \;-\; \frac{V(f \mid B_1, m, \theta)}{V(f \mid B_0, m, \theta)}.$$

$R$ is the quantity this paper reports. It is a function of four arguments and
the paper's own history is that all four have been left implicit. $\theta$ is
absent for metrics that integrate over the operating range; the protocol says
which those are.

**$R$ is reported only where $V(f \mid B_0, m, \theta) > 0$** in every bootstrap
draw. A ratio whose denominator crosses zero is not a quantity, and this
project has already published one that did.

---

## 2. The corpus

Every log is public, is cited by DOI, and is downloaded by
`scripts/fetch_corpus.py`, which records a SHA-256 for each file.

| Key | Domain | Source | DOI |
|---|---|---|---|
| BPIC14 | ITSM | Rabobank NL Group ICT | `10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35` |
| BPIC13_incidents | ITSM | Volvo IT Belgium (VINST) | `10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee` |
| BPIC13_open | ITSM | Volvo IT, open problems | `10.4121/uuid:3537c19d-6c64-4b1d-815d-915ab0e479da` |
| BPIC13_closed | ITSM | Volvo IT, closed problems | `10.4121/uuid:c2c3b154-ab26-4b31-a0e8-8f2350ddac11` |
| Helpdesk | ITSM | an Italian company | `10.4121/uuid:0c60edf1-6f83-4e75-9367-4c63b3e9d5bb` |
| UCI498 | ITSM | anonymised ServiceNow instance | `10.24432/C57S4H` |
| BPIC12 | lending | Dutch financial institution | `10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f` |
| BPIC17 | lending | same institution, later | `10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b` |
| BPIC19 | procurement | multinational coatings/paints | `10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1` |
| BPIC15_1 … BPIC15_5 | permitting | five Dutch municipalities | `10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1` |
| BPIC20_domestic, _intl, _prepaid, _permit, _rfp | expenses | a Dutch university | `10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51` |
| Sepsis | healthcare | a Dutch hospital | `10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460` |
| HospitalBilling | healthcare | a regional hospital | `10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741` |
| RoadFines | enforcement | an Italian police unit | `10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5` |

That is **21 candidate logs across 7 domains**. The plan's requirement is at
least eight logs and at least four domains *after* the exclusions in §4 are
applied; the corpus is deliberately larger than the requirement so that
exclusions do not have to be argued with.

**Logs considered and not included, with the reason.** BPIC 2011 (hospital)
and BPIC 2018 (agricultural subsidies) are omitted for size and parsing cost
respectively — BPIC 2018 is 158 MB compressed and ~2.5 GB expanded, and the
healthcare domain is already carried by two logs. Recorded here so that their
absence is a stated decision and not a silent one. If BPIC 2018 is later
loaded for the free-text search in §7, that is a search over field names and
not an addition to the ladder corpus.

---

## 3. The four roles, assigned by rule

For each log, every attribute is assigned to exactly one role by the rules
below, applied in this order. No attribute is assigned by judgement, and the
assignment for every log is written to `results/r33_roles.csv` so a reader can
check the rules were followed.

Let $n$ be the number of traces and $c(a)$ the number of distinct non-missing
values of attribute $a$ on the first event of each trace.

**3.1 Structural exclusions.** Never assigned to any role:
the case identifier; any timestamp; `concept:name`; `lifecycle:transition`;
any attribute whose name matches the log's declared outcome fields (§4);
any attribute with $c(a) < 2$ (constant) or with more than 50% missing on the
first event.

**3.2 The free overlapping field $g$.** The attribute that is
  (i) *resource-like* — its name is one of `org:group`, `org:resource`,
      `org:role`, or the per-log equivalent named in `r32_corpus.py`'s
      `RESOURCE_FIELDS`, declared in that file before any ladder is fitted; and
  (ii) *per-event* — it takes more than one value within at least one trace,
      which is the admissibility criterion the published paper already states
      and applies; and
  (iii) present on the first event of at least 50% of traces.
If more than one attribute qualifies, $g$ is the one with the highest $c(a)$.
If none qualifies, the log is **excluded** (§4, code `NO_G`).

**3.3 The high-cost entity $f$.** Among attributes not excluded by §3.1 and
not chosen as $g$ and not resource-like, $f$ is the attribute with the largest
$c(a)$ subject to
  (i) $c(a) \ge 50$ — below that it is a classification, not a register; and
  (ii) $n / c(a) \ge 2$ — each value is reused across at least two traces on
       average, so it names a maintained thing and not the case itself.
If none qualifies, the log is **excluded** (code `NO_F`).

**3.4 The intake block $B_0$.** Every remaining attribute with
$c(a) \le 200$. The cap keeps a second identifier out of the baseline; a log
whose $B_0$ would be empty is **excluded** (code `NO_B0`).

**3.5 The layer hierarchy (§8 only).** Where a log carries attributes
$a_1, \dots, a_k$ that are *deterministic coarsenings* of $f$ — every value of
$f$ maps to exactly one value of $a_j$, tested on the data and reported — they
form the resolution ladder. This test is the one `r21` already applies to
Rabobank's `CI Type` and `CI Subtype`. A hierarchy is never constructed by
clustering, because a grouping chosen after seeing the outcome is not a
hierarchy.

---

## 4. The target, and the exclusion rules

**4.1 Primary target $Y_H$ — handover.** Let $G(e)$ be the value of the
resource-like attribute chosen as $g$ in §3.2, read on event $e$. Let
$H = |\{G(e) : e \in \text{trace}\}| - 1$. Then $Y_H = \mathbb{1}[H \ge 1]$.

This is the generic form of the published target: Rabobank's
`# Reassignments >= 1` and BPIC 2013's distinct-`org:group` count are both
instances of it.

**4.2 Secondary target $Y_D$ — duration.** $Y_D = \mathbb{1}[\text{trace
duration} > \text{median trace duration in the training half}]$. The median is
taken on the training half only, so no test outcome enters the definition.

Both targets are declared here and **both are reported for every log**.
Reporting one and choosing it per log would be the fishing this document
exists to prevent.

**4.3 The tautology control, run on every log.** $g$ is the opening value of
the same attribute whose distinct-count defines $Y_H$. A reader is entitled to
suspect the relationship is definitional. The published paper answers this for
Rabobank with a contrast that has a sign a tautology cannot produce: if $Y_H$
were definitional in $g$, the *largest* opening group — the central desk, which
by construction has the most places to hand work to — would show the *highest*
target rate. On Rabobank it shows the lowest. That contrast is computed for
every log in the corpus and reported whatever it says.

**4.4 Exclusion codes, declared before inspection.** A log is excluded from the
ladder if any of:

| code | rule |
|---|---|
| `NO_G` | no attribute satisfies §3.2 |
| `NO_F` | no attribute satisfies §3.3 |
| `NO_B0` | $B_0$ is empty |
| `SMALL_N` | fewer than 1,000 traces |
| `NO_HEADROOM` | target prevalence below 0.05 or above 0.95 in the full log |
| `NO_TEST_VARIATION` | the test half contains only one class |

An excluded log is reported in the results table with its code. Exclusions are
**not** silent: `r33_excluded.csv` names every one.

---

## 5. The ladder, the estimator, and the split

For each admitted log and each of the two targets, four models:

| | features |
|---|---|
| $M_0$ | $B_0$ |
| $M_1$ | $B_0 \cup \{f\}$ |
| $M_2$ | $B_0 \cup \{g\}$ |
| $M_3$ | $B_0 \cup \{g, f\}$ |

$V_{\text{naive}} = m(M_1) - m(M_0)$, $V_{\text{honest}} = m(M_3) - m(M_2)$,
$R = 1 - V_{\text{honest}} / V_{\text{naive}}$.

**Estimator.** One-hot encoding with `handle_unknown="ignore"`, logistic
regression, `C=1.0`, `max_iter=3000`. Identical to `r4_final.fit`, which is the
estimator every published number in this paper uses.

**Split.** Traces sorted by first-event timestamp; first 70% train, last 30%
test. Temporal, not random, because a random split on a process log leaks the
future. Where a log has no usable timestamp the split is by file order and the
log is flagged; no log in §2 is expected to need this.

**Seed.** 20260819 everywhere, as in every other script in this repository.

**Instruments.** The r30 matrix: ROC AUC, average precision, Brier skill,
Nagelkerke $R^2$, and net benefit over the 31-point grid
$\theta \in \{0.05, 0.075, \dots, 0.80\}$. **ROC AUC is the primary**, for
comparability with the published number and for no other reason; the full
matrix is reported beside it for every log.

**Intervals.** Paired bootstrap over test rows, 2,000 draws, one index set per
draw shared by all four models.

---

## 6. What is reported, and in what form

**6.1** The *distribution* of $R$ across logs — every log named, never an
average alone. An average over a corpus assembled by convenience is not an
estimate of anything.

**6.2** Every log's cohort characteristics beside its $R$: $n$, prevalence,
$c(f)$, $c(g)$, $|B_0|$, mean trace length, and the discriminators in §6.3.

**6.3 Discriminators, computed before any model is fitted**, so that the
attempt to predict $R$ from log properties cannot be accused of using the
answer:

- normalised mutual information $\mathrm{NMI}(f, g)$ on the training half;
- concentration of $f$: normalised entropy, and the share of traces held by
  the top 1% of values;
- whether $g$ is a resource stamp or a classification (a declared property of
  the attribute name, from `RESOURCE_FIELDS`);
- events per trace, median and mean;
- $c(f)$, $c(g)$, $n$, prevalence.

**6.4 The prediction attempt.** $R$ is regressed on the §6.3 discriminators
across admitted logs. With fewer than twenty logs this is **exploratory and is
labelled so**: leave-one-out $R^2$ is reported, and a permutation test with
2,000 shuffles of the log labels gives the null. If leave-one-out $R^2$ is
negative, that is reported as the result. A positive in-sample $R^2$ on
fifteen points with five predictors is not evidence and will not be presented
as any.

---

## 7. Free text (§5.3 of the plan)

A separate, declared search rather than an analysis: for every log in §2, every
attribute is classified as free text if its values are, on the training half,
(i) more than 40% unique **and** (ii) mean length above 20 characters **and**
(iii) containing a space in more than half of values. Logs with such a field
get the ladder re-run with the field admitted via a hashed character n-gram
encoder, cross-fitted. Logs without one are recorded in `r37_free_text.csv`
with the field-by-field reason. **A documented negative is the deliverable if
no log has one.**

---

## 8. What would falsify the claim

Stated now, so it cannot be renegotiated later.

- **The claim.** The admissibility reduction $R$ is a property of process event
  logs with a reusable high-cost entity and a free per-event resource stamp,
  not a property of ITSM data or of CMDBs.
- **Falsified if** $R$ is resolvably positive on the two ITSM logs already
  published and is not resolvably positive on a majority of the admitted
  non-ITSM logs.
- **Also falsified if** the tautology control (§4.3) comes out the way a
  tautology predicts on a majority of logs.
- **Weakened, and to be reported as weakened, if** $R$ is positive everywhere
  but its spread across logs is wider than the spread across the design choices
  already reported for Rabobank (36.1%–48.3%), because then the corpus has
  established variability rather than generality.

If the claim is falsified the paper reports the negative and bounds itself to
ITSM. That outcome is written into `PLAN-STRONG-ACCEPT.md` §3.3 as an
acceptable one and it will not be dressed up.

---

## 9. What this protocol does not fix

- It does not fix the choice of **corpus**. The logs are the public ones a
  process-mining reader would recognise; a different corpus is a different
  study.
- It does not fix the **estimator family**. One-hot logistic is used because
  every published number in this paper uses it; `r10` shows two other families
  agree on Rabobank, and that is evidence for one log, not for twenty-one.
- It does not make the targets *the* targets. $Y_H$ and $Y_D$ are two workflow
  outcomes definable without a domain expert. A desk that cares about something
  else is measuring something else, which is the paper's own thesis applied to
  itself.

---

## 10. Changes to this document after registration

Any change is appended below with its date and reason, and the original text
stays. Nothing is edited in place.

*(no changes yet)*

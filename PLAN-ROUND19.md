# Round nineteen — the *Information Systems* reject, answered

**Input:** a full referee report on the round-eighteen manuscript, recommending
*reject as submitted* for **Information Systems** (Elsevier), with ten major
comments, a seven-phase redesign plan and six resubmission gates.

**Directive:** address every comment; rebuild the study where the comment
touches the evidence; rewrite the manuscript; ship the compliance and
reproducibility package.

---

## The ten major comments, and what each one costs

| # | Comment | Class | Response |
|---|---|---|---|
| 1 | Main conclusion contradicts §10 | evidence | One frozen master table; every claim re-derived from it |
| 2 | Not novel enough | contribution | Four new methodological objects (below) |
| 3 | Estimand incomplete; "value" overstated | definition | Full $V_s(f)$ over 10 axes; renamed *incremental predictive performance* |
| 4 | Audit cannot support field-wide claim | evidence | Rebuilt: larger frame, PRISMA, sensitivity/specificity-corrected prevalence; demoted to a *measured pilot* |
| 5 | $R$ unstable, read as a proportion | statistics | Absolute increments primary; $R$ secondary with Fieller intervals |
| 6 | Propositions not established | theory | Restated and reproved; Prop. 3 relabelled a computational result |
| 7 | Knowledge reference may be post-decision | evidence | Two decision times, two surfaces; availability becomes an axis |
| 8 | Inference inadequate | statistics | Refit-inside-bootstrap, blocked + rolling origin, simultaneous max-$t$ bands, Holm |
| 9 | External validation selected | design | Every admitted log reported; reframed as a heterogeneous benchmark |
| 10 | Population axis does not model quality | design | Five declared quality mechanisms, train-only, multi-seed |

## The four new methodological objects (comment 2)

1. **The specification surface** $\mathcal{S}$ — a declared, enumerable design
   space, and $V_s(f)$ over it.
2. **Sensitivity decomposition** — a functional-ANOVA (Sobol) decomposition of
   $\mathrm{Var}_s[V_s(f)]$ into per-axis main effects and interactions.
3. **Resolution regions** — *uniformly beneficial*, *sign-changing*,
   *unresolved*, defined by simultaneous bands over $\mathcal{S}$, with a
   scalar **robustness index** $\rho$.
4. **Specification regret** — a decision-theoretic benchmark of one-number
   reporting against the surface, measured over every log-target pair.

## Scripts

| file | what it produces |
|---|---|
| `s01_spec_surface.py` | the frozen master surface, all logs, all axes |
| `s02_decomposition.py` | Sobol/fANOVA variance decomposition |
| `s03_regions.py` | simultaneous bands, resolution regions, $\rho$ |
| `s04_regret.py` | specification regret vs. one-number reporting |
| `s05_ratio.py` | Fieller intervals for $R$; absolute absorption $D$ |
| `s06_audit2.py` | rebuilt audit: PRISMA, corrected prevalence |
| `s07_props.py` | the three restated propositions, executed |
| `s08_decision_time.py` | two decision times for the knowledge reference |
| `s09_quality.py` | five register-quality mechanisms |
| `s10_simulation2.py` | expanded simulation: misspecified, drifting, sparse |
| `s11_calibration.py` | calibration and unseen-category rates |
| `s12_figures.py` | the journal figures |

## Compliance package (Phase 7)

abstract ≤250 · keywords ≤7 · highlights 3–5 ≤85 chars · Zenodo DOI ·
lockfile + container · data availability · funding · competing interests ·
CRediT · generative-AI declaration · clean bibliography · no `Appendix
Appendix` · every number identical across abstract, tables, figures,
conclusion · main text 12,000–15,000 words.

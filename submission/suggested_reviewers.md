# Suggested reviewers

Six names, drawn from the two lines of work the paper's claims are most
exposed to: **leakage and evaluation design in predictive process
monitoring**, and **organisational mining and event-log data quality**. Each
entry says what that reviewer is well placed to break, because a suggested
reviewer who cannot damage the paper is not worth suggesting.

The author has no affiliation, no co-authors and no institutional
relationship with any of these researchers. Several are cited in the
manuscript; that is disclosed in each entry.

> **Before submitting:** verify each affiliation and supply a current email
> address from the researcher's own institutional page or from the
> corresponding-author line of a recent paper. Affiliations move. Do not
> submit an address taken from anywhere else.

---

### 1. Jochen De Weerdt — KU Leuven, Belgium
*Research Centre for Information Systems Engineering (LIRIS).*
Works on evaluation design and leakage in predictive process monitoring;
co-author of the work on temporal splitting and prefix leakage that the
paper adopts and cites. **Best placed to attack:** whether the field-admission
criterion is a leakage constraint properly stated, and whether the strict
temporal split and the extract-boundary treatment are adequate.
*Cited in the manuscript.*

### 2. Marlon Dumas — University of Tartu, Estonia
*Institute of Computer Science.*
Co-author of the outcome-oriented predictive process monitoring benchmark
that the paper both relies on and departs from — the benchmark explicitly
excluded the two BPI Challenge logs this paper uses, which is a point a
reviewer should press. **Best placed to attack:** whether a t=0 tabular
prediction on a process log belongs in this literature at all, and whether
the target definition is defensible.
*Cited in the manuscript.*

### 3. Arik Senderovich — York University, Toronto, Canada
*School of Information Technology.*
Originated the inter-case / queueing-feature line for predictive process
monitoring. **Best placed to attack:** the congestion control — whether four
free creation-time queueing features are the right ones, and whether the
affected item is standing in for load in a way the control does not reach.

### 4. Niels Martin — Hasselt University, Belgium
*Business Informatics; UHasselt Data Science Institute.*
Works on resource behaviour, queueing and data quality in process mining,
including what a resource stamp on an event actually denotes. **Best placed
to attack:** the paper's central semantic claim — that the field on the
`Open` row is the group that *logged* the incident rather than a routing
destination — which is established from the log rather than from
documentation.

### 5. Moe Thandar Wynn — Queensland University of Technology, Australia
*School of Information Systems.*
Works on event-log quality and imperfection patterns. **Best placed to
attack:** whether the 100% population rate of the affected-item field is an
export artifact that makes the primary result inapplicable to real CMDBs,
which is the paper's own largest stated limitation.
*Adjacent work cited in the manuscript.*

### 6. Chiara Di Francescomarino — University of Trento, Italy
*Department of Information Engineering and Computer Science.*
Predictive process monitoring, including feature encoding and the effect of
representation choices on measured performance. **Best placed to attack:**
whether the reduction survives representations the paper did not try, and
whether target encoding of the item column is a fair second estimator.

---

## Non-preferred reviewers

None. The author requests no exclusions.

## A note for the editor

The paper reports eight of its own errors as results, two of them found in
the round that produced this version and both of which removed a claim the
previous version made. A reviewer who reads the Corrections section as
evidence of unreliability rather than of method has read it as intended
except for the sign. The author would rather that reviewer be assigned than
avoided.

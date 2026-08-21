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

---

## Round-seventeen addendum: what each is now best placed to break

The manuscript changed substantially between the version this list was drawn
for and the one being submitted. The six names stand; what they are best
placed to attack has moved.

- **De Weerdt** and **Dumas** now also face a *pre-registered protocol* over
  22 public logs (`PROTOCOL.md`), with eight declared amendments. The sharpest
  attack available to either is on the generic targets: the handover target
  agrees with the primary log's own reassignment field on only 46.0% of
  incidents, which §11 reports and which bounds what the corpus can be said to
  replicate.
- **Senderovich** should be pointed at §13's intake-mix sweep. It is the
  paper's largest sensitivity and it is a *subsample* of one organisation, not
  a second organisation, which §13 concedes in those words.
- **Martin** now has a second semantic claim to attack, and it is the one that
  removes the paper's headline: that the knowledge-article reference is written
  by the service desk rather than by the incident process. §12's evidence is
  that the field is populated on all 94,250 interactions that never become an
  incident. If that inference is wrong, §12 is wrong.
- The two reviewers listed for evaluation methodology should be pointed at §7.
  The claim that six defensible instruments on identical scores put the same
  reduction between 43.7% and 60.3% is the paper's methodological core, and the
  place it is most exposed is the choice of which six count as defensible.

**One suggestion that is new.** If the editor is willing, a reviewer whose work
is on *reproducibility and verification tooling* rather than on process mining
would be well placed to attack the part of this submission that is least like
the rest of the literature: a checker that recomputes 417 numeric literals, a
suite of 199 corruptions over that checker, and a claim — stated in the paper
and in the repository — that the apparatus provably cannot see the class of
defect that two of this paper's eleven corrections belong to.

# Suggested reviewers

Six names, drawn from the two lines of work the manuscript's claims are most
exposed to: **evaluation design, leakage and encoding in predictive process
monitoring**, and **event-log data quality and resource semantics**. Each
entry says what that reviewer is best placed to break, because a suggested
reviewer who cannot damage the paper is not worth suggesting.

The author has no affiliation, no co-authors and no institutional
relationship with any of these researchers. Several are cited in the
manuscript; that is disclosed in each entry. Every e-mail address below was
taken on 2026-09-06 from the researcher's own institutional page or from the
corresponding-author line of a paper of theirs published in 2022 or later;
the source is given in each entry.

---

### 1. Jochen De Weerdt — KU Leuven, Belgium
*Faculty of Economics and Business, Information Systems Engineering Research
Group (LIRIS). Professor.*
E-mail: jochen.deweerdt@kuleuven.be (corresponding author, *Process Mining
Handbook*, LNBIP 448, 2022).
Works on evaluation design and leakage in predictive process monitoring;
co-author of the leakage-prevention benchmark work the paper adopts and
cites. **Best placed to attack:** whether the registered role-assignment rules
of Section 5 are a leakage constraint properly stated, whether excluding
closure-time fields by name is enough, and whether the stationarity the
moving-block bootstrap assumes — measured and failing on 6 of 19 pairs — is
carried honestly in Section 10.
*Cited in the manuscript.*

### 2. Marlon Dumas — University of Tartu, Estonia
*Institute of Computer Science, Chair of Software Engineering; Visiting
Professor. Since the Apromore acquisition (November 2025) also in an industry
role at Salesforce.*
E-mail: marlon.dumas@ut.ee (institutional page).
Co-author of the outcome-oriented predictive process monitoring benchmark the
paper relies on and departs from. **Best placed to attack:** whether a
creation-time prediction on a process log belongs in that literature at all
— the prefix axis is deliberately not varied, and Section 10 concedes it —
and whether the registered handover target, at prevalence 0.927 on the case
study's log, is a meaningful target.
*Cited in the manuscript.*

### 3. Arik Senderovich — York University, Toronto, Canada
*Faculty of Liberal Arts and Professional Studies, School of Information
Technology. Assistant Professor.*
E-mail: sariks@yorku.ca (institutional page).
Originated the inter-case and queueing-feature line for predictive process
monitoring; his *Information Systems* paper on intra- and inter-case features
is cited. **Best placed to attack:** the decision-time argument of Section 7
— whether the three moments are the right ones, whether the assignment group
used as the free field is standing in for load, and whether the reconciliation
of the two published values by target rather than cohort holds.
*Cited in the manuscript.*

### 4. Niels Martin — Hasselt University, Belgium
*Faculty of Business Economics, Business Informatics research group. Tenure
Track Assistant Professor.*
E-mail: niels.martin@uhasselt.be (institutional page).
Works on resource behaviour and data quality in process mining, including
what a resource stamp on an event actually denotes. **Best placed to
attack:** the register, free-field and intake roles of Section 5.2 as
semantic claims about real logs; the six register-quality mechanisms, which
Section 10 concedes are constructed rather than observed; and the undeclared
sort inside tied identities that Section 10 records and does not repair.

### 5. Moe Thandar Wynn — Queensland University of Technology, Australia
*School of Information Systems. Professor; Co-Director, QUT Centre for Data
Science.*
E-mail: m.wynn@qut.edu.au (corresponding author, ICPM 2021 Workshops, LNBIP
433, 2022).
Works on event-log quality and imperfection patterns; that work is cited and
is the vocabulary the register-quality axis borrows. **Best placed to
attack:** whether the degradation mechanisms correspond to imperfections that
occur in maintained registers, and whether a fully populated configuration
item field on a public log is an export artefact that limits what the case
study says about real configuration management databases.
*Cited in the manuscript.*

### 6. Chiara Di Francescomarino — University of Trento, Italy
*Department of Information Engineering and Computer Science (DISI).
Associate Professor.*
E-mail: c.difrancescomarino@unitn.it (institutional page).
Predictive process monitoring, including encodings and the effect of
representation choices on measured performance; co-author of the
remaining-time survey the paper cites. **Best placed to attack:** the pipeline
axis — a model family crossed with an encoding on the case study's log and on
the 8 ITSM pairs only, with two learners inside every inference family — and
the omission of sequence encodings, which Section 10 names as the structural
gap.
*Cited in the manuscript.*

---

## Non-preferred reviewers

None. The author requests no exclusions.

## A note for the editor

The paper's methodological core is statistical: an exact functional-ANOVA
decomposition, simultaneous max-*t* bands whose family-wise coverage is
measured against a known answer, and a decision rule between two estimators
of the critical value written before the measurement was run. If the editor
is willing, one reviewer with expertise in resampling inference and multiple
testing, rather than in process mining, would be well placed to examine
Sections 4 and 9 and the supplement's proofs; no name is suggested because the
author has no basis for choosing one.

The manuscript withdraws two claims a specification surface invites and one
of its own earlier headlines, and states where its band is short of nominal.
A reviewer who reads those withdrawals as evidence of unreliability rather
than of method has read them as intended except for the sign; the author
would rather that reviewer be assigned than avoided.

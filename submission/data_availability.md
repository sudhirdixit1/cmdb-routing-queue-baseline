# Data availability statement

All three event logs analysed in this study are public and none is
redistributed by the author. The analysis code, the intermediate result
files, the figures and the checker that recomputes every quantity printed in
the paper are available in the repository cited in the manuscript.

## Statement for the submission system

> All data used in this study are publicly available benchmark event logs,
> cited in the manuscript by persistent identifier. No new data were
> generated. Analysis code, derived result files and a verification harness
> that recomputes every number reported in the paper are openly available at
> the repository cited in the Acknowledgements, archived at the DOI given
> there.

## The datasets, by persistent identifier

| Log | Organisation | Identifier | Role in the paper |
|---|---|---|---|
| BPI Challenge 2014 | Rabobank Group ICT, HP Service Manager | `doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35` | primary organisation |
| BPI Challenge 2013, incidents | Volvo IT, VINST | `doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee` | second organisation |
| Incident management process enriched event log | anonymised IT company, ServiceNow | `doi:10.24432/C57S4H` (UCI 498) | third public log; population rates only |

The BPI Challenge collections are distributed by 4TU.ResearchData under the
terms attached at each DOI; the UCI log is distributed under CC BY 4.0. The
repository contains no row of any of them: `data/` is excluded from version
control and `REPRODUCE.md` tells a reader how to fetch each file and where to
put it.

## What is in the repository, and what it does not cover

The repository holds every script, every derived `results/*.csv`, the LaTeX
source, and `scripts/verify_paper.py`, which recomputes each numeric literal
in the manuscript from a result file or from the raw data and fails if any
literal is unaccounted for. `scripts/attack_verifier.py` is that checker's
own regression suite.

The checker guards **numbers** thoroughly and **prose** only where a guard
was written by hand. It cannot tell you that an interpretation is sound. The
README says so in the same words, and the paper's Corrections section reports
six of its eight corrections as claims about what a number *means* — none of
which the checker would have caught.

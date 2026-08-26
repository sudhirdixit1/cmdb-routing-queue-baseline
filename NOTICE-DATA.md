# What the MIT licence in `LICENSE` does and does not cover

`LICENSE` covers **this repository's own contents**: the analysis code under
`scripts/`, the `fieldvalue/` package, the pre-registrations and protocols,
the derived result files under `results/`, the manuscript sources under
`paper/`, and the verification harness. It is the licence `.zenodo.json`
declares, so the archived release and the repository say the same thing.

It does **not** cover, and cannot cover, three things the repository refers to
but does not contain.

**The event logs.** The corpus is public data fetched by DOI at run time by
`scripts/fetch_corpus.py` and is deliberately excluded from version control
(`.gitignore` excludes `data/raw/`, `data/corpus/` and `data/normalized/`).
Each log carries its own terms at its own DOI; `REPRODUCE.md` and
`data/corpus/CHECKSUMS.txt` name every one. Nothing here redistributes them.

**The audited papers.** `data/audit/fulltext/` and the `data/audit2/` dossiers
are other publishers' copyrighted PDFs, fetched for the reporting-practice
pilot and never committed. Only the two adjudication tables
(`data/audit2/adjudication_*.csv`), which contain the pilot's own coded
judgements and no publisher content, are tracked.

**The manuscript's eventual published version.** The sources in `paper/` are
licensed as above; a version of record, once one exists, carries whatever
terms the publisher and the author agree.

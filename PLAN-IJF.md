# Plan: retarget to the *International Journal of Forecasting*

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans
> (inline, this session) or superpowers:subagent-driven-development to
> implement this plan task by task. Steps use checkbox (`- [ ]`) syntax.
> `PLAN-STRONG-ACCEPT.md` §0 governs how to work; its six rules and §0.3
> (decisions taken and recorded, credentials stopped, dead ends documented)
> apply to every task below.

**Target venue:** International Journal of Forecasting (Elsevier/IIF, ISSN
0169-2070). Editorial Manager: `https://www.editorialmanager.com/ijf`.
**Written:** 2026-09-12, two days after *Information Systems* desk-rejected
manuscript INFOSYS-D-26-00926 (EIC, no referee comments): "Your very nice
paper should be sent to a forecasting journal where your treatment of the
value of a feature may give new insight."
**Predecessor:** `PLAN-ROUND28.md`, executed; its §10 is the record of the
manuscript as submitted to *Information Systems* (tag `v28.0`, 56 pp).
**Goal:** one command builds a blinded IJF manuscript, a separate title page
and a blinded supplement from the same source, every gate passes, and the
only steps left are the ones only the author can take.

**Architecture:** one LaTeX source with a `\ifblind` switch that
`build_journal.py --target ijf` sets; the five author statements move into
one part that the unblinded title-page document and the unblinded article
both `\input`; a new gate `check_blind.py` reads the *built* blind PDFs and
fails on any identifying string. The reframing is a recorded vocabulary map
applied by a script that prints every hit for review, followed by
hand-rewritten front, section openings and conclusion, each audited against
the built PDF. Length comes from moving whole subsections to the supplement
behind pointer paragraphs, measured after each move.

**Tech stack:** `elsarticle` (CTAN, `authoryear` option, `elsarticle-harv`),
pdflatex + bibtex, `xr`, Python 3 scripts under `scripts/`, `pdftotext`.

**Spec:** this file, §1–§3 (design approved in chat 2026-09-12). Decisions
taken during execution go to `submission/DECISIONS.md` §IJF.

## Global constraints

- Numbers reach the paper only through `paper/numbers.tex` macros
  (`make_numbers.py --strict`). No task types a number.
- **No number, sign or directional word changes.** The reframe is
  vocabulary and framing; every rewritten paragraph is diffed for claims
  (rule 6). If a rewrite would need a new claim, stop and record it.
- Archive stays at **v28.0 / DOI 10.5281/zenodo.22557927** (author's
  decision 2026-09-12). The tag is not moved. No new release.
- IJF rules, from the April 2020 Guide for Authors the IIF still links and
  the IIF page read 2026-09-11: double-blind; title page a separate file;
  abstract 100–150 words, no notation; ≥5 keywords; author–year citations,
  alphabetical list; `elsarticle` template; PDF at submission; 4–6
  suggested referees outside the author's institution; code and data
  mandatory; reproducibility check at acceptance; disclose related
  manuscripts elsewhere.
- Blind build outputs carry no author name in content, metadata or file
  name: `build/journal/manuscript.pdf`, `build/journal/supplement.pdf`;
  the unblinded `build/journal/title_page.pdf` carries everything.
- Length target: article **≤ 44 pp, aim 40** (12pt `preprint`). Record
  the count reached and what it would cost to go lower.
- Every new bibliography entry is verified against its DOI before it is
  cited (IJF: "check all references against their original sources").
- Commit per task on branch `ijf-retarget`; message says what the task
  found. Never `git add -A` while `paper/.tex.bak` exists.

---

## STATUS AT A GLANCE — update as tasks complete

| phase | state |
|---|---|
| 0 · branch, decisions, this plan | not started |
| 1 · mechanical: journal, author–year, blind switch, title page, `check_blind` | not started |
| 2 · length: seven subsections to the supplement | not started |
| 3 · full reframe: vocabulary map, title, abstract, keywords, intro, related work, openings, conclusion | not started |
| 4 · package: cover letter, referees, manifest, skill, highlights, logs | not started |
| 5 · gates, internal referee read (round 29), final build | not started |
| 6 · author-only steps | owner — `python scripts/finalise.py` |

---

## 1. What the venue asks, and what the repository has

| IJF rule | state at `v28.0` | task |
|---|---|---|
| double-blind main text; separate title page | name, e-mail, address on both documents; CRediT and AI declaration name the author; code availability names the GitHub user and DOI | 1.2–1.4 |
| author–year citations | `elsarticle-num`, five bare `\cite` used as "Hutter et al.~\cite{}" | 1.1 |
| abstract 100–150 words, no notation | 196 words, contains `$V_s(f)$` | 3.2 |
| ≥5 keywords, IJF list preferred | 6, none from the IJF list | 3.2 |
| `\journal{}` | `Information Systems` | 1.1 |
| value relative to length | 56 pp | 2.x |
| 4–6 referees, outside institution | six process-mining/IS names | 4.2 |
| code and data mandatory | archive at v28.0 with `REPRODUCE.md`, `verify_release.py` | none (done) |
| disclosure of related manuscripts | not written | 4.1 |
| scope: forecasting | the word "forecast" does not occur | 3.x |

## 2. Design (approved)

**2.1 Blinding — one source, one switch.** `\newif\ifblind` in both front
parts; `build_journal.py --target ijf` writes `blindflag.tex` (`\blindtrue`)
into the build directory before compiling, and the sources
`\InputIfFileExists{blindflag}{}{}`. Under `\ifblind`: no `\author`,
`\ead`, `\address`; the statements part is not input; the code-availability
paragraph says the archive and identifier are on the title page; the
software self-citation prints as *Anonymous (2026), details omitted for
double-blind reviewing* (a `.bbl` post-process in `build_journal.py`, the
same place the `\href` unwrap lives). Data availability stays: it names
public DOIs and nothing about the author. The five statements (CRediT,
competing interest, funding, code availability, generative AI) move to
`paper/parts/statements.tex`, input by the unblinded article and by the
title-page document.

**2.2 Title page.** `paper/title_page.tex`, assembled from
`T0_title_front.tex` + `statements.tex` + `T9_title_back.tex`: title,
author, affiliation with full address, e-mail, ORCID line, abstract,
keywords, then the statements.

**2.3 `check_blind.py`.** Runs `pdftotext` and `pdfinfo` on the two blind
PDFs and fails on: `Dixit`, `sudhir`, `sudhirdixit1`, `github.com`,
`zenodo`, `10.5281`, `\affiliationStreet` and `\affiliationCity` values
read from `numbers.tex`, `Independent Researcher`, `ORCID`, `Anthropic`,
`Claude`; also fails if any file under `build/journal/` matching `*.pdf`
has `dixit` in its name. `--selftest` proves it fires (rule 5).

**2.4 Reframe.** The object is the *incremental forecast value of a
predictor*. Vocabulary map (applied by `scripts/retarget_ijf.py`, every hit
printed, reviewed by hand, macros untouched):

| from | to | scope |
|---|---|---|
| incremental predictive performance | incremental forecast value | everywhere incl. title |
| predictive performance | forecast performance | everywhere |
| the outcome predicted / the target | the forecast target | first use per section; elsewhere "target" stays |
| decision time | forecast origin | everywhere; first use: "the forecast origin (the decision time at which the forecast is issued)" |
| one-number report | one-number report | kept as the coined term; defined at first use as "a point estimate of forecast improvement" |
| register / recorded field | register / recorded field | kept (domain object); first use adds "— a candidate predictor —" |
| prediction (the model's output) | forecast | hand, sentence by sentence, in §1, §3, §4 openings, §7, §8, §11 |

Anchors added to related work, each verified by DOI: Diebold & Mariano
(1995); West (1996); Clark & McCracken (2001) — nested-model forecast
comparison is the incremental-value question; Giacomini & White (2006);
White (2000) reality check and Hansen (2005) SPA — specification search
over a family; Hansen, Lunde & Nason (2011) model confidence set — nearest
relative of the simultaneous band; Granger & Pesaran (2000) and Murphy
(1993) — decision-based forecast value; Gneiting & Raftery (2007) — proper
scoring rules and probability forecasts. One paragraph in §1 says what
kind of forecast this is: a probability forecast of a binary event issued
at a forecast origin, scored by AUC and net benefit; not a time series.

**2.5 Length.** Subsections moved to the supplement with a 2–4 sentence
pointer paragraph left in place: §4.7 specification regret; §5.4 corpus
commonality; §6.5 against specification-curve analysis; §6.6 decision
rules in and out of sample; §7.5 the absorption ratio; §9.1 pointwise
certification; the itemised detail of §10 threats to validity. Page count
measured after each; stop when ≤ 44, record the count.

**2.6 Package.** New cover letter (why IJF; the IS EIC's sentence quoted;
prior review history; related-manuscript disclosure; the archive at v28.0
and that HEAD's source post-dates it with byte-identical results, which
`verify_release.py` proves). Highlights regenerated. Graphical abstract:
not supplied (optional; recorded). Referees: 4–6 from forecast
evaluation, institutional e-mails sourced. `response_to_referee.md` and
`summary_of_changes.md` leave the upload list and are marked superseded.
Skill `submitting-to-information-systems` → `submitting-to-ijf`.

## 3. File map

| file | change |
|---|---|
| `paper/parts/00_front_intro_related.tex` | class options, `\journal`, blind switch, front matter, §1, §2 |
| `paper/parts/S0_supplement_front.tex` | class options, blind switch, title |
| `paper/parts/90_backmatter.tex` | `\ifblind` code-availability paragraph / `\input{parts/statements}`; `elsarticle-harv` |
| `paper/parts/S9_supplement_back.tex` | new appendix inputs; `elsarticle-harv` |
| `paper/parts/statements.tex` | **new** — the five statements, moved verbatim |
| `paper/parts/T0_title_front.tex`, `T9_title_back.tex` | **new** — title-page document |
| `paper/parts/app_regret.tex`, `app_corpus_common.tex`, `app_specurve.tex`, `app_rules.tex`, `app_absorption.tex`, `app_pointwise.tex`, `app_threats.tex` | **new** — moved subsections |
| `paper/parts/20_inference.tex`, `30_design.tex`, `40_multilog.tex`, `50_cmdb.tex`, `60_dca.tex`, `75_simulation.tex`, `80_limits.tex`, `10_surface.tex` | pointer paragraphs; vocabulary; openings |
| `paper/references.bib` | ten verified entries |
| `scripts/assemble_paper.py` | `ORDER_TITLE`, third document |
| `scripts/build_journal.py` | `--target ijf`, blind flag, `.bbl` anonymiser, title-page build, output names |
| `scripts/check_blind.py` | **new** gate |
| `scripts/retarget_ijf.py` | **new** — vocabulary map, dry-run by default |
| `scripts/texlint.py` | abstract 100–150, keywords 5–8, statements read from `statements.tex`, `\journal` check |
| `scripts/final_search.py` | FORBIDDEN in PDF text: `Information Systems`; REVIEW: `predict` |
| `scripts/finalise.py` | owed items for IJF |
| `scripts/check_package.py` / `submission/README.md` | manifest |
| `scripts/make_highlights.py` | templates in the new vocabulary |
| `submission/cover_letter.md`, `suggested_reviewers.md`, `DECISIONS.md`, `OWNER-ACTIONS.md`, `README.md` | rewritten / appended |
| `.claude/skills/submitting-to-ijf/SKILL.md` | replaces the IS skill |
| `REFEREE-LOG.md`, `AI-USE.md` | the IS decision; this session |

---

## Phase 0 — branch and decisions

### Task 0.1: branch and record the decisions

**Files:** `submission/DECISIONS.md` (append), `PLAN-IJF.md` (this file)

- [ ] `git checkout -b ijf-retarget main` (main is at `2b9716f`, clean).
- [ ] Append to `submission/DECISIONS.md` a section `## IJF retarget — 2026-09-12` with five entries, each *chosen / rejected / what would overturn it*: (1) full reframe rather than targeted; (2) length by subsection relocation, target ≤44 aim 40, "cut harder" rejected; (3) archive stays v28.0, new release rejected; (4) graphical abstract not supplied; (5) IJF template not yet diffed — `elsarticle` with `authoryear` assumed; overturned if the downloaded template differs (owner step 6.1).
- [ ] Add to `REFEREE-LOG.md` one entry: 2026-09-10, Information Systems, EIC desk rejection, the sentence verbatim, disposition "retargeted to IJF, PLAN-IJF.md".
- [ ] Commit: `git add PLAN-IJF.md submission/DECISIONS.md REFEREE-LOG.md && git commit -m "Plan for the IJF retarget, with the five decisions it rests on and the IS decision logged"`.

---

## Phase 1 — mechanical

### Task 1.1: journal name and author–year references

**Files:** `paper/parts/00_front_intro_related.tex:20,83`,
`paper/parts/S0_supplement_front.tex` (same two lines),
`paper/parts/90_backmatter.tex` (last lines), `paper/parts/S9_supplement_back.tex`,
`paper/parts/20_inference.tex:239`, `paper/parts/app_pilot.tex:10,47`,
`paper/parts/app_protocol.tex:211,240`, `scripts/build_journal.py`,
`scripts/finalise.py:9,74`, `submission/OWNER-ACTIONS.md:52,384,399`

- [ ] In both front parts: `\documentclass[preprint,12pt,authoryear]{elsarticle}` and `\journal{International Journal of Forecasting}`.
- [ ] In `90_backmatter.tex` and `S9_supplement_back.tex`: `\bibliographystyle{elsarticle-harv}`.
- [ ] The five bare `\cite` are of the form `Hutter et al.~\cite{hutter2014efficient}`; under `authoryear` that prints the name twice. Replace each with `\citet{key}` and delete the preceding name and `~`: `Hutter et al.~\cite{hutter2014efficient}` → `\citet{hutter2014efficient}`; `Page et al.~\cite{page2021prisma}` → `\citet{page2021prisma}`; `Rogan--Gladen~\cite{rogan1978estimating}` → `Rogan--Gladen \citeyearpar{rogan1978estimating}`; `Suriadi et al.~\cite{suriadi2017imperfection}` → `\citet{suriadi2017imperfection}`; `Weytjens and De Weerdt~\cite{weytjens2022leakage}` → `\citet{weytjens2022leakage}`.
- [ ] Run `grep -n '\\cite{' paper/parts/*.tex` — expected: no output.
- [ ] `python scripts/assemble_paper.py && python scripts/build_journal.py`. Expected: `0 errors, 0 undefined references`. Open `build/journal/specification_surfaces.bbl`: entries begin `\bibitem[Armstrong and Collopy(1992)]` style and the list is alphabetical; DOIs still typeset (the `\href` unwrap in `build_one` applies to `harv` too — confirm by `grep -c href build/journal/specification_surfaces.bbl` → `0`).
- [ ] `pdftotext build/journal/specification_surfaces.pdf - | grep -c "\[46\]"` → `0`; `grep -n "(2014)" ` on the text shows `Hutter et al. (2014)` once, not twice.
- [ ] Replace "reference [46]" in `scripts/finalise.py` and `submission/OWNER-ACTIONS.md` with "the software reference (Dixit, 2026)".
- [ ] Gates: `for s in texlint verify_numbers check_package final_search; do python scripts/$s.py | tail -1; done` — all `0 failures` (texlint check 4 still finds the statements; nothing moved yet).
- [ ] Commit: `Author–year references and the IJF journal line; the five doubled citations fixed`.

### Task 1.2: the statements part and the blind switch

**Files:** create `paper/parts/statements.tex`; modify
`paper/parts/90_backmatter.tex`, `paper/parts/00_front_intro_related.tex:83-100`,
`paper/parts/S0_supplement_front.tex:85-92`, `scripts/texlint.py:118-135,265-268,315`

**Produces:** `\ifblind` defined in both documents; `paper/parts/statements.tex` containing the five `\section*` statements verbatim; `90_backmatter.tex` reduced to Data availability + `\ifblind … \else \input{parts/statements} \fi` + bibliography.

- [ ] Create `paper/parts/statements.tex` by cutting, unchanged, from `90_backmatter.tex`: `\section*{CRediT …}` block, `\section*{Declaration of competing interest}`, `\section*{Funding}`, `\section*{Code availability}` (whole paragraph) and `\section*{Declaration of generative AI …}` (whole block including its `%%` comment). Leave `\section*{Data availability}` in `90_backmatter.tex`, but change its last sentence "all code are in the archive below" → "all code are in the archive named in the code-availability statement".
- [ ] In `90_backmatter.tex`, after Data availability:
  ```latex
  \ifblind
  \section*{Code availability}
  Code, derived results, the registered protocols, the amendment log and the
  verification harness are archived under a persistent identifier and
  developed in a public repository; both are given on the title page and
  are omitted here for double-blind reviewing. The archive contains a
  \texttt{Dockerfile} and a \texttt{requirements.lock} pinning every
  transitive dependency, and \texttt{REPRODUCE.md} gives the exact commands.
  \else
  \input{parts/statements}
  \fi
  ```
- [ ] In `00_front_intro_related.tex`, before `\journal{…}`:
  ```latex
  %%  IJF reviews double-blind.  build_journal.py --target ijf writes
  %%  blindflag.tex (\blindtrue) into the build directory; without it the
  %%  document is the unblinded one.  check_blind.py reads the built PDF.
  \newif\ifblind
  \blindfalse
  \InputIfFileExists{blindflag}{}{}
  ```
  and wrap the author block: `\ifblind\else \author[ind]{Sudhir Dixit} \ead{…} \address[ind]{…} \fi`. Same in `S0_supplement_front.tex`.
- [ ] `texlint.py`: after `t = strip_comments(raw)` add `t += strip_comments((PAPER / "parts" / "statements.tex").read_text(encoding="utf-8"))` with a comment saying the statements live in a part the blind build omits. Add a check 8: `\\journal\{International Journal of Forecasting\}` present, else FAIL "journal line".
- [ ] `python scripts/assemble_paper.py && python scripts/build_journal.py` (unblinded — no flag file). Expected PDF identical in content to before: `pdftotext` both and `diff` → only the changed Data-availability sentence.
- [ ] `python scripts/texlint.py | tail -1` → `0 failures`.
- [ ] Commit: `The five statements are one part; the blind switch exists and is off`.

### Task 1.3: `build_journal.py --target ijf`, the title page, the anonymised self-citation

**Files:** `scripts/build_journal.py`, `scripts/assemble_paper.py:22-45`,
create `paper/parts/T0_title_front.tex`, `paper/parts/T9_title_back.tex`

**Produces:** `python scripts/build_journal.py --target ijf` → `build/journal/manuscript.pdf`, `build/journal/supplement.pdf`, `build/journal/title_page.pdf`; function `anonymise_bbl(text: str) -> str` in `build_journal.py`.

- [ ] `assemble_paper.py`: add `OUT_TITLE = ROOT / "paper" / "title_page.tex"`, `ORDER_TITLE = ["T0_title_front.tex", "statements.tex", "T9_title_back.tex"]`, `DOCS[OUT_TITLE] = ORDER_TITLE`.
- [ ] `T0_title_front.tex`: the same preamble as `00_front…` lines 20–80 (copy; `xr` and `\externaldocument{supplement}` included so `Supplement~\ref{app:standard}` in the AI declaration resolves), then `\journal{International Journal of Forecasting}`, `\begin{document}\begin{frontmatter}`, `\title{…}` (same macro-free title text as the article — Task 3.2 changes both together), `\author[ind]{Sudhir Dixit}`, `\ead{sudhir.dixit1@gmail.com}`, `\address[ind]{Independent Researcher, \affiliationStreet, \affiliationCity, \affiliationRegion, \affiliationCountry}`, a line `\fntext[orcid]{ORCID: registered in Editorial Manager}` bound to the author, the `abstract` and `keyword` blocks **copied verbatim from the article** (Task 3.2 edits both; texlint check 9 below asserts they are identical), `\end{frontmatter}`. `T9_title_back.tex`: `\bibliographystyle{elsarticle-harv}\bibliography{references}\end{document}` — the title page cites nothing but the statements' `\zenodoDOI` is a macro, so bibtex may report "no citations"; `build_one` treats "I couldn't open" and "Illegal" as failure only, so that is fine — verify in the log.
- [ ] `build_journal.py`: add `--target {is,ijf}` (default `ijf` from now; `is` keeps the old behaviour for `verify_release.py` on `v28.0` checkouts — check that script's call and pass `--target is` there if it builds the tagged tree). Under `ijf`: write `out/blindflag.tex` = `\blindtrue\n` before compiling article and supplement; after both, delete the flag, build `title_page` with `build_one("title_page", "t")`; copy outputs to `out/manuscript.pdf`, `out/supplement.pdf`, `out/title_page.pdf`; leave `paper/specification_surfaces.pdf` as the *unblinded* article for the archive (build it once more without the flag, or state in the docstring that `paper/*.pdf` are unblinded — pick the second, it is cheaper, and record it).
- [ ] `anonymise_bbl(text)`: regex `\\bibitem\[Dixit\((\d{4})\)\]\{([^}]*)\}.*?(?=\\bibitem|\\end\{thebibliography\})` (DOTALL) → `\\bibitem[Anonymous(\1)]{\2}\nAnonymous (\1). Details omitted for double-blind reviewing.\n\n`. Called inside `build_one` only when `blind` is true, after the `\href` unwrap. Under `harv`, `\citep{dixit2026fieldvalue}` then prints "(Anonymous, 2026)".
- [ ] Also under `blind`: after compiling, assert `pdfinfo out/manuscript.pdf` has no `Author:` line (pdflatex without hyperref writes none; assert anyway).
- [ ] Run `python scripts/assemble_paper.py && python scripts/build_journal.py --target ijf`. Expected: three `OK` lines; `pdftotext build/journal/manuscript.pdf - | grep -c Dixit` → `0`; `pdftotext build/journal/title_page.pdf - | grep -c Dixit` → `≥2`; `grep -c "Anonymous (2026)" <(pdftotext build/journal/manuscript.pdf -)` → `1`.
- [ ] `check_package.py` rule 3 (built documents newer than sources) reads fixed names — update it to the three new outputs in Task 4.3; until then expect it to fail and say so in the commit message.
- [ ] Commit: `build_journal --target ijf: blinded article and supplement, a separate title page, the self-citation anonymised in the .bbl`.

### Task 1.4: `check_blind.py`

**Files:** create `scripts/check_blind.py`

- [ ] Write the gate:
  ```python
  """check_blind -- THE BLIND PDFS CARRY NOTHING THAT NAMES THE AUTHOR.
  IJF reviews double-blind.  The manuscript and the supplement are built
  with a switch that removes the author block, the statements and the
  archive pointers; this reads what was BUILT, because the switch is a
  claim and the PDF is the fact.  --selftest proves the scanner fires.
  """
  import re, subprocess, sys
  from pathlib import Path
  ROOT = Path(__file__).resolve().parent.parent
  OUT = ROOT / "build" / "journal"
  BLIND = [OUT / "manuscript.pdf", OUT / "supplement.pdf"]
  def _macro(name):
      m = re.search(r"newcommand\{\\%s\}\{([^}]*)\}" % name,
                    (ROOT / "paper" / "numbers.tex").read_text(encoding="utf-8"))
      return m.group(1).strip() if m else None
  def patterns():
      p = ["Dixit", "sudhir", "sudhirdixit1", "github\\.com", "zenodo",
           "10\\.5281", "Independent Researcher", "ORCID", "Anthropic", "Claude"]
      for k in ("affiliationStreet", "affiliationCity"):
          v = _macro(k)
          if v: p.append(re.escape(v))
      return [re.compile(x, re.I) for x in p]
  def scan(text, pats):
      return [(m.group(0), text[max(0, m.start()-40):m.end()+40].replace("\n", " "))
              for pat in pats for m in pat.finditer(text)]
  def pdf_text(pdf):
      return subprocess.run(["pdftotext", "-q", str(pdf), "-"],
                            capture_output=True, text=True, timeout=180).stdout
  def pdf_meta(pdf):
      return subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
  def main(argv=None):
      pats = patterns()
      if argv and argv[0] == "--selftest":
          hits = scan("draft by Sudhir Dixit, github.com/x, Apex", pats)
          assert len(hits) >= 3, hits
          assert not scan("a register is a predictor", pats)
          print("check_blind selftest OK: %d hits on the planted text" % len(hits)); return 0
      fails = []
      for pdf in BLIND:
          if not pdf.exists():
              fails.append("%s missing (run build_journal.py --target ijf)" % pdf.name); continue
          for what, ctx in scan(pdf_text(pdf), pats) + scan(pdf_meta(pdf), pats):
              fails.append("%s: '%s' in ...%s..." % (pdf.name, what, ctx))
      for f in OUT.glob("*.pdf"):
          if "dixit" in f.name.lower(): fails.append("file name names the author: %s" % f.name)
      for f in fails: print("FAIL  " + f)
      print("check_blind: %d failures" % len(fails))
      return 1 if fails else 0
  if __name__ == "__main__":
      sys.exit(main(sys.argv[1:]))
  ```
- [ ] `python scripts/check_blind.py --selftest` → `check_blind selftest OK`.
- [ ] `python scripts/check_blind.py` → expected on the first run: **failures** — the supplement front matter and any `\texttt{github…}` path in the body (`80_limits.tex`, `app_*` files mention `REPRODUCE.md` etc.; a GitHub URL may sit in an appendix). Fix every hit at the source under `\ifblind` or by rewording (rule 5: the corruption came first and the check found it — record the count of hits in the commit message).
- [ ] Re-run until `check_blind: 0 failures`.
- [ ] Commit: `check_blind: the built blind PDFs name nobody; N hits found and removed on the first run`.

---

## Phase 2 — length

### Task 2.1: move seven subsections to the supplement

**Files:** create `paper/parts/app_regret.tex` (from `20_inference.tex:353-371`),
`app_corpus_common.tex` (`30_design.tex:95-end`), `app_specurve.tex`
(`40_multilog.tex:325-358`), `app_rules.tex` (`40_multilog.tex:359-end`),
`app_absorption.tex` (`50_cmdb.tex:182-end`), `app_pointwise.tex`
(`75_simulation.tex:9-52`), `app_threats.tex` (the itemised detail of
`80_limits.tex:1-167`); modify those seven parts and
`paper/parts/S9_supplement_back.tex:50-75`.

Do one move at a time; after each: assemble, build `--target ijf`, note the page count from the `OK` line, run `python scripts/texlint.py | tail -1` and `python scripts/verify_numbers.py | tail -1`.

- [ ] For each move: cut the subsection body into the new part as `\section{<same heading>}\label{app:<key>}` (supplement sections are lettered appendices; keep every `\label` inside so the article's `\ref`s resolve through `xr`), append `\clearpage\input{parts/app_<key>}` to `S9_supplement_back.tex` before `app_standard`, and leave in the article a pointer paragraph in the same voice, e.g. for §4.7: *"A specification-regret check — the gap between the best admissible cell and the conventional report — is reported in Supplement~\ref{app:regret}; it changes no label in Section~\ref{sec:multilog}."* The pointer states what the moved section concludes only if the moved section's own conclusion sentence is copied verbatim (rule 6).
- [ ] §10 threats to validity: keep the first paragraph of each numbered threat, move the elaboration; target 1,000 words in the article (texlint `--report` prints per-section words).
- [ ] Any `\ref{fig:…}`/`\ref{tab:…}` whose float moved with the text must be checked: `build_journal.py` exits non-zero on an undefined reference — that is the test.
- [ ] Record in the STATUS table: pages after each move. Stop moving when the article is ≤ 44 pp; if all seven leave it above 44, record the number and the next candidate (§9.2 or Table 3) without moving it.
- [ ] `python scripts/check_response_refs.py`: `response_to_referee.md` and `summary_of_changes.md` now point at renumbered sections. Add a `SUPERSEDED` banner at the top of both (they answer the *Information Systems* referee for a manuscript that no longer exists) and make `check_response_refs.py` skip a file whose first line starts with `> **SUPERSEDED`; the cover letter is still checked.
- [ ] Commit per move: `Length: §6.5 to the supplement as Appendix K; article 52 → 50 pp`.

---

## Phase 3 — the reframe

### Task 3.1: the vocabulary map, by script

**Files:** create `scripts/retarget_ijf.py`; modify the nine section parts and `S0_supplement_front.tex`

- [ ] Write the script: an ordered list `MAP = [(pattern, replacement, note), …]` exactly as §2.4's table (regexes with `\b`, case-preserving for a leading capital); `--dry-run` (default) prints every match with file, line and 60 characters of context; `--apply` writes. It never touches `paper/numbers.tex`, `paper/tables/`, or any line containing `\newcommand`. Macro names (e.g. `\nDecisionTimes`) are skipped by excluding matches preceded by `\`.
- [ ] `python scripts/retarget_ijf.py` (dry run). Read every hit. Any hit inside a quotation, a registered-protocol name, a file path or a table header is added to an `EXCLUDE` list of `(file, line)` in the script, with the reason.
- [ ] `python scripts/retarget_ijf.py --apply`; assemble; build; texlint; verify_numbers; `check_sources`.
- [ ] `grep -rn "decision time" paper/parts/*.tex` → only the parenthetical definition at first use and the excluded lines.
- [ ] Commit: `Vocabulary: forecast value, forecast origin, forecast target — N replacements, M excluded and why`.

### Task 3.2: title, abstract, keywords, highlights, texlint limits

**Files:** `paper/parts/00_front_intro_related.tex:85-138`, `paper/parts/T0_title_front.tex` (same blocks), `paper/parts/S0_supplement_front.tex` (title), `scripts/texlint.py:52-54,282-295`, `scripts/make_highlights.py`, `submission/upload/Highlights.txt`

- [ ] Title in all three places: *Specification Surfaces for the Incremental Forecast Value of a Predictor: Estimation, Uncertainty, and Multi-Log Evaluation*.
- [ ] Abstract, ≤150 words, no notation, same numbers by the same macros (`\nPairs`, `\nLogs`, `\shareResamplingStratumPct`, `\madResolvedMedian`, `\nCohort`). Draft:
  > How much a candidate predictor adds to a forecast is usually reported as one number, but that number depends on choices the report rarely states: the baseline, the pipeline, the forecast target, the split, the forecast origin, how completely the predictor is populated, and the score. We define incremental forecast value as a specification surface over a declared design space and give three objects for reporting it: an exact functional-ANOVA decomposition separating analyst choices from resampling; simultaneous bootstrap bands with measured family-wise coverage; and resolution regions, which say where the sign is determined. On \nPairs\ forecast targets from \nLogs\ public event logs, resampling carries a median \shareResamplingStratumPct\ of the variance; where the sign is determined, admissible specifications sit a median \madResolvedMedian\ AUC from the conventional report. In a bank's incident data, the predictor's value turns on the forecast origin and its sign on the target.
  Count with texlint's counter (macros count as one word).
- [ ] Keywords (8): `Evaluating forecasts \sep Uncertainty \sep Bootstrapping \sep Probability forecasting \sep Robustness \sep Decision making \sep specification surface \sep event logs`.
- [ ] `texlint.py`: `ABSTRACT_LIMIT = 150`, add `ABSTRACT_MIN = 100` with a FAIL below it; `KEYWORD_LIMIT = 8`, add `KEYWORD_MIN = 5`. Add check 9: the `abstract` and `keyword` blocks of `T0_title_front.tex` are byte-identical to the article's (they are copied, and a copy drifts).
- [ ] `make_highlights.py`: rewrite the five templates in the new vocabulary, same macros. Run `python scripts/make_highlights.py && python scripts/check_highlights.py`.
- [ ] Assemble, build, texlint → `0 failures`.
- [ ] Commit: `Title, abstract (≤150 words), IJF keywords, highlights in the forecast vocabulary`.

### Task 3.3: related work — the forecasting lineage, verified

**Files:** `paper/references.bib`, `paper/parts/00_front_intro_related.tex:301-end`

- [ ] For each of the ten anchors in §2.4, look up the DOI (Crossref: `curl -s "https://api.crossref.org/works?query.bibliographic=<title>&rows=1"`), add a bib entry with `doi`, and confirm `curl -sI https://doi.org/<doi> | head -1` returns a redirect. Record each lookup in the commit message. Do not cite an entry that fails.
- [ ] Add one paragraph to §2, placed first: the forecast-evaluation lineage and where this paper sits — nested-model comparison (Clark–McCracken) is the incremental-value question for one specification; reality check / SPA / MCS treat a *family* of forecasts; the surface makes the family explicit and reports its geometry rather than its best member; decision-based value (Granger–Pesaran, Murphy) is what §8's net-benefit evaluation computes. No claim about those papers beyond what their abstracts say.
- [ ] Build; `0 undefined`; commit: `Related work: the forecast-evaluation lineage, ten references verified by DOI`.

### Task 3.4: the introduction, the section openings, the conclusion

**Files:** `00_front_intro_related.tex:152-300`, first paragraph of each of `10_surface`, `20_inference`, `30_design`, `40_multilog`, `50_cmdb`, `60_dca`, `75_simulation`, `80_limits`; `80_limits.tex:168-end`

- [ ] Before editing, run `python scripts/texlint.py --report > /tmp/before.txt` and save `pdftotext` of the built article as `/tmp/before_pdf.txt`.
- [ ] §1: opening paragraph poses the forecasting question (a service desk issues a forecast at an origin; a register is a candidate predictor; what is it worth?); the contributions list restated in forecast-evaluation terms; add the "what kind of forecast this is" paragraph from §2.4 (binary event, probability forecast, forecast origin, AUC and net benefit; not a time series and the methods do not assume one).
- [ ] Each section's first paragraph: one to three sentences rewritten so a forecasting reader knows why the section exists. Body sentences untouched except via Task 3.1.
- [ ] §8 (decision-analytic): first paragraph ties net benefit to forecast value (Granger–Pesaran; Murphy) by citation.
- [ ] §11 conclusion: rewritten in the new vocabulary; the same five findings, the same macros.
- [ ] **Audit (rule 6):** `diff <(pdftotext …before) <(pdftotext …after)` — read every changed sentence; list in the commit message any sentence whose *claim* changed (there should be none). `python scripts/check_claims.py`, `final_search.py` → `0 failures`.
- [ ] Commit: `Introduction, openings and conclusion for a forecasting reader; claims unchanged (diff audited)`.

---

## Phase 4 — the package

### Task 4.1: cover letter

**Files:** `submission/cover_letter.md` (rewrite)

- [ ] Sections: the manuscript and its claim in forecast terms (four sentences); **why IJF** — evaluation of forecasts, forecast uncertainty and decision-making are on the journal's topic list, and the EIC of *Information Systems* wrote on 2026-09-10 (quoted verbatim, one sentence) that the work belongs in a forecasting journal; **prior review** — one referee report at *Information Systems* on an earlier manuscript (*Four Choices Behind One Number*), answered in full, then the desk decision above; **related manuscripts** — none under review elsewhere; the earlier AAAI-format version was never submitted (confirm with the author: `OWNER-ACTIONS.md` item); **data and code** — public logs by DOI; archive `10.5281/zenodo.22557927` (v28.0); the source at HEAD post-dates the archive with byte-identical results, `verify_release.py`; **AI use** — the three uses, declared in the title-page statements; **suggested referees** — see file.
- [ ] `python scripts/check_response_refs.py` and `check_claims.py` → `0 failures`.
- [ ] Commit.

### Task 4.2: suggested referees

**Files:** `submission/suggested_reviewers.md` (rewrite)

- [ ] Four to six researchers in forecast evaluation / forecast comparison tests / decision-based forecast value / probability-forecast scoring, none a collaborator, each with an institutional e-mail **sourced** (own institutional page, or corresponding-author line of a 2022+ paper), with the URL and date read beside each. Do not guess an address (`finalise.py` fails on a file without `@`).
- [ ] Commit.

### Task 4.3: manifest, `check_package`, `finalise`, skill

**Files:** `submission/README.md`, `scripts/check_package.py`, `scripts/finalise.py`, `.claude/skills/submitting-to-ijf/SKILL.md` (new; delete `submitting-to-information-systems/` and re-link from `../.claude/skills/`), `submission/OWNER-ACTIONS.md`

- [ ] `README.md` upload table: `../build/journal/manuscript.pdf` (blind), `../build/journal/title_page.pdf`, `../build/journal/supplement.pdf` (blind), `upload/Highlights.txt`, `cover_letter.md`, Elsevier's declaration `.docx`, `credit_statement.md`, `data_availability.md`, `suggested_reviewers.md`. Move `summary_of_changes.md` and `response_to_referee.md` to the archived/not-uploaded table with "superseded".
- [ ] `check_package.py`: manifest names updated; rule 3 compares the three PDFs' mtimes to the assembled sources.
- [ ] `finalise.py` `status()`: keep DOI (present), reviewers, address; add: ORCID line, the IJF template diff (a file `submission/IJF-TEMPLATE-CHECKED.md` present), `check_blind` passing.
- [ ] Write `submitting-to-ijf/SKILL.md` with the owner steps of §Phase 6, the upload table, and the "what not to upload" list; delete the IS skill directory and fix the symlink in `../.claude/skills/`.
- [ ] `OWNER-ACTIONS.md`: replace the IS section with the Phase 6 list.
- [ ] `AI-USE.md`: this session (model `claude-opus-5`, 2026-09-11/12, tasks).
- [ ] Commit.

---

## Phase 5 — gates and the round-29 read

### Task 5.1: every gate

- [ ] `python scripts/make_numbers.py --strict && python scripts/assemble_paper.py && python scripts/build_journal.py --target ijf`
- [ ] `for s in texlint verify_numbers check_package check_highlights check_claims check_response_refs check_sources final_search check_blind; do python scripts/$s.py | tail -1; done` — every line `0 failures`.
- [ ] `final_search.py`: add FORBIDDEN (PDF text only) `Information Systems` and REVIEW `\bpredict(?:ion|ive|ed)?\b` so every surviving "predict" is read once by a human and kept or changed. Re-run.
- [ ] `python scripts/verify_release.py` on HEAD → passes (it builds from `git archive HEAD`; pass `--target ijf` if the script forwards build flags, else it builds the unblinded article, which is also fine and says so).
- [ ] Record page counts (article, supplement, title page) in the STATUS table.

### Task 5.2: round-29 internal referee read

**Files:** `submission/review_round29.md`, `submission/response_to_review29.md`

- [ ] Read `build/journal/manuscript.pdf` as an IJF referee (double-blind, forecast-evaluation background); the report answers: does the paper read as a forecasting paper by page 3; is any claim stronger than at v28.0; is anything identifying; is the length justified. Same format as `review_round28.md`.
- [ ] Answer each major comment; make the changes; re-run Task 5.1.
- [ ] Commit: `Round 29: the IJF read, N comments, M changes`.

### Task 5.3: merge and hand-off

- [ ] `git checkout main && git merge --ff-only ijf-retarget`.
- [ ] Do **not** push and do **not** tag without the author's word (pushing publishes; the tag is pinned at v28.0 by decision).
- [ ] Update `PLAN-IJF.md` STATUS table and append §7 record (what ran, what it found, what it cost, page counts).

---

## Phase 6 — steps only the author can take (`python scripts/finalise.py` lists them)

| # | step | done when |
|---|---|---|
| 6.1 | Download the IJF LaTeX template (forecasters.org/ijf/authors → "this template", a Google Drive file) and diff its preamble against `00_front_intro_related.tex`; record the diff in `submission/IJF-TEMPLATE-CHECKED.md` | file exists; any class-option difference applied |
| 6.2 | Postcode into `AFFILIATION_REGION` in `scripts/round26_numbers.py`, rebuild | title page shows the full line |
| 6.3 | ORCID in the Editorial Manager IJF profile; create the account | profile complete |
| 6.4 | Elsevier's declaration-of-interests `.docx` | attached |
| 6.5 | Confirm in `cover_letter.md` that no related manuscript is under review elsewhere | sentence true |
| 6.6 | Read the title-page statements (CRediT, competing interest, AI) — they are claims about you | you agree with every sentence |
| 6.7 | `git push origin main ijf-retarget` (no tag) | `origin/main` = `main` |
| 6.8 | Upload: `manuscript.pdf`, `title_page.pdf`, `supplement.pdf`, Highlights, cover letter, declaration, referees | submission confirmed |

---

## 7. Execution record

(appended per phase: what ran, what it found, what changed, what it cost)

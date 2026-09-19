# The IJF LaTeX template, diffed against the build — 2026-09-18

The International Journal of Forecasting's authors page
(forecasters.org/ijf/authors) says "please use this template" and links a
Google Drive file, `IJFTemplate.zip`. It was downloaded and read on
2026-09-18 and its sources are kept under `submission/ijf-template/` so
this diff is reproducible. This file's existence is what clears the item
in `scripts/finalise.py`; its content is the diff and what was done about
it. DECISIONS.md §IJF.5 ("assumed to be `elsarticle` — provisional") is
settled by it: the class is `elsarticle`, and the options differed.

## 1. What the zip contains

| file | what it is | where it is kept |
|---|---|---|
| `ijftemplate.tex` | the template source, 61 lines | `submission/ijf-template/ijftemplate.tex` |
| `ijftemplate.pdf` | the template compiled by the IIF (pdfTeX 1.40.16, 2016-01-19, one page) | beside the `.tex` in the author's checkout; not committed |
| `refs.bib` | four sample entries (Hyndman et al. 2002, Hyndman & Athanasopoulos 2014, Goerg 2013, Timmermann 2006) | `submission/ijf-template/refs.bib` |
| `model5-names.bst` | Elsevier's author–year bibliography style, version 2.0 (2009–2012) | `paper/model5-names.bst`, so bibtex finds it beside `references.bib` |

The template's preamble is four lines:

```latex
\documentclass[11pt,3p,review,authoryear]{elsarticle}
\journal{International Journal of Forecasting}
\bibliographystyle{model5-names}
\biboptions{longnamesfirst}
% Please use \citet and \citep for citations.
```

Its comments say three further things:

- Blinding: "Leave this section commented out so that the paper is blinded
  for review" (the `\author`/`\address`/`\cortext`/`\ead` block is
  commented out), and "Only give the email address of the corresponding
  author".
- Acknowledgements: "Comment this section out if it reveals the authors'
  identities."
- Submission: "You only need to submit the pdf file, not the source files.
  If your article is accepted for publication, you will be asked for the
  source files."

The abstract line says "Keep it brief and avoid mathematical notation and
citations"; the keyword block points at ijf.forecasters.org/keywords/.

## 2. Template versus ours, line by line

"Before" is the build as of commit `919f25a`; "after" is this revision.

| preamble line | template | ours, before (article and supplement) | ours, after: article (`00_preamble.tex`) | ours, after: supplement (`S0_supplement_front.tex`) |
|---|---|---|---|---|
| `\documentclass` | `[11pt,3p,review,authoryear]{elsarticle}` | `[preprint,12pt,authoryear]{elsarticle}` | `[11pt,3p,review,authoryear]{elsarticle}` — the template's, exactly | `[preprint,12pt,authoryear]{elsarticle}` — kept, see §4 |
| `\journal` | `{International Journal of Forecasting}` | the same | the same | the same |
| `\bibliographystyle` | `{model5-names}` (in the preamble) | `{elsarticle-harv}` (in `90_backmatter.tex` / `S9_supplement_back.tex`, before `\bibliography`) | `{model5-names}` in `90_backmatter.tex` | `{model5-names}` in `S9_supplement_back.tex` |
| `\biboptions` | `{longnamesfirst}` | absent | `{longnamesfirst}`, the line after `\journal` | `{longnamesfirst}`, the line after `\journal` |
| citation commands | "Please use `\citet` and `\citep`" | 74 `\citep`, 15 `\citet`, 1 `\citeyearpar`, no bare `\cite` | unchanged | unchanged |
| author block | commented out for blinding | inside `\ifblind … \else … \fi`; the blind build prints none | unchanged | unchanged |
| acknowledgements | commented out if identifying | none in the article; the statements are on the separate title page, which the blind article omits | unchanged | unchanged |

The title page (`title_page.tex`) is assembled from the same
`00_preamble.tex`, so it takes the article's options too; it is not blind
by definition (`T0_unblind.tex`) and stays at three pages.

## 3. What was applied to the article

1. `\documentclass[11pt,3p,review,authoryear]{elsarticle}` and
   `\biboptions{longnamesfirst}` in `paper/parts/00_preamble.tex`.
2. `\bibliographystyle{model5-names}` in `paper/parts/90_backmatter.tex`.
3. `scripts/build_journal.py` copies `paper/*.bst` into `build/journal/`
   beside `references.bib`. The `.bbl` post-processing that removed
   `\href` around DOIs under `elsarticle-num`/`-harv` applies unchanged to
   `model5-names`, whose `.bbl` preamble defines
   `\doi` as `\href{http://dx.doi.org/#1}{\path{#1}}`: the wrapper is
   removed, `\path` reads the DOI, and every DOI prints (checked in the
   built PDF; a DOI with an underscore, `…/978-3-031-82225-4_15`, prints
   correctly).
4. The anonymised self-citation. Under both styles the blind build
   rewrote the software self-citation's `\bibitem` in place, which left
   "Anonymous (2026)" in the D slot of the alphabetical list (between
   Diebold and van Dongen in the article; between Davison and Fieller in
   the supplement) — a mis-sorted list and a hint at the initial the blind
   removes. `anonymise_bbl` now cuts the entry out and puts it at the head
   of the list, before the first remaining `\bibitem`, in the form
   `model5-names` prints for every other entry (`Author (year).` then the
   `\newblock`). In both blind PDFs the first reference is
   "Anonymous (2026). Details omitted for double-blind reviewing." and
   nothing for it remains under D; the in-text citations still print
   "(Anonymous, 2026)" (article §4.7; supplement §S21.2).
5. The title page's empty "References" heading. `T9_title_back.tex` had a
   `\bibliographystyle` and a `\bibliography` for a document that cites
   nothing, and `elsarticle` printed the heading with nothing under it on
   page 3. Both lines are gone; `build_one` skips bibtex for a stem whose
   `.aux` has no `\bibdata`. `pdftotext build/journal/title_page.pdf - |
   grep -c "^References"` is 0 and the five statements (CRediT, competing
   interest, funding, code availability, generative AI) are all on it.

### What `review` and `3p` do in the installed class

`kpsewhich elsarticle.cls` → `~/Library/texmf/tex/latex/elsarticle/elsarticle.cls`,
**elsarticle 3.5, 2026/01/09** (`\RCSversion{3.5}`, `\RCSdate{2026/01/09}`),
lines 71–86:

- `review` = `\global\preprinttrue\gdef\@blstr{1.5}`: `\baselinestretch`
  1.5, no line numbers (the class has no `lineno` option).
- `3p` = `\xdef\jtype{3}\global\preprintfalse`: the one-column A4 journal
  layout through `geometry` (text block 468 pt × 622 pt, `footskip` 18 pt).
- `\ProcessOptions` (line 114, unstarred) executes options in the order
  the class DECLARES them, and `3p` is declared after `review`, so
  `\preprintfalse` wins: `\maketitle` is the journal-style title box and no
  "Preprint submitted to …" footer is set. The template's own PDF, compiled
  in 2016 with an older class, does show that footer; the class removed
  the line in any case on an Elsevier instruction of 22 Oct 2024 (comment
  at line 1043). Compiling the template with the installed class today
  gives no footer, which is what our build gives.
- The class's defaults (line 112) are `a4paper,10pt,oneside,onecolumn,
  number,preprint,centertitle`; the template overrides the size, the
  layout, the spacing and the citation form. Version 3.5 also has a
  `doubleblind` option (line 110) that only suppresses the author block
  in `\maketitle`; the template does not use it and neither do we, since
  the `\ifblind` switch removes the author block, the statements and the
  archive pointers at source and `check_blind.py` reads the PDF.
- `11pt` is the base size (the class's default is 10pt; ours was 12pt).
- `authoryear` = natbib's `round,authoryear`; `\biboptions{longnamesfirst}`
  is appended to natbib's options through the `.spl` file the class writes,
  which takes effect from the second pdflatex run (the build runs three).
  In the built article the first citation of a three-author paper prints
  all three ("Hansen, Lunde & Nason, 2011") and the next prints
  "Hansen et al., 2011", which is what the option does.

## 4. What was deliberately not applied to the supplement, and why

The supplement keeps `\documentclass[preprint,12pt,authoryear]{elsarticle}`
(decision taken by the integrator before this revision). The template is
for the article; the journal publishes an online supplement as supplied
and has no template for it; and this document is 120 pages at single
spacing (115 before the same day's revision) — at the article's 1.5 spacing it would be about 175. It takes the
same bibliography options as the article (`model5-names`,
`longnamesfirst`), so a reference reads the same in both documents and
the anonymised entry heads both lists. The comment above its
`\documentclass` says so.

## 5. Page counts

| document | before (`preprint,12pt`) | after |
|---|---|---|
| `manuscript.pdf` | 53 | 52 (A4, 11pt, 1.5-spaced; the 3p text block is wider and taller than the letter-size preprint block); 53 after the 2026-09-19 read added a table and glosses |
| `supplement.pdf` | 115 | 120 (unchanged options; the day's relocations, landscape pages and one added table) |
| `title_page.pdf` | 3 | 3 |

Build summary after the change: article 0 overfull hboxes, 0 floats too
large for their page; supplement 2 overfull hboxes (the two that were
there before), 0 floats too large; 0 errors, 0 undefined references. No
float parameter was changed. Every gate at 0 (texlint, verify_numbers,
check_package, check_highlights, check_claims, check_response_refs,
check_sources, final_search, check_blind).

One bibtex warning is new to the style and is not an error:
`can't use both volume and number fields in hutter2014efficient`
(`model5-names` prints the series volume and ignores `number`; the entry
prints as "… (pp. 754–762). volume 32 of Proceedings of Machine Learning
Research."). Dropping `number = {1}` from that entry would silence it.

## 6. What the template says about what to submit

"You only need to submit the pdf file, not the source files. If your
article is accepted for publication, you will be asked for the source
files." So the upload is `build/journal/manuscript.pdf`,
`build/journal/title_page.pdf` and `build/journal/supplement.pdf` as
the package README lists them; the sources are owed at acceptance.

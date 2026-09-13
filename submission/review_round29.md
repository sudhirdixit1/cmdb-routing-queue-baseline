# Referee read of the IJF manuscript (internal, simulated ninth referee)

*Manuscript:* Specification Surfaces for Incremental Forecast Performance:
Estimation, Uncertainty, and Multi-Log Evaluation
*Version read:* `build/journal/manuscript.pdf` (blind) built 2026-09-12 after
commit `2e44fb2` (53 pages; supplement 115 pages; title page 3 pages), with
the repository open to check any number.
*Brief:* a referee for the *International Journal of Forecasting* with a
forecast-evaluation background, reading double-blind, asked four questions:
does the paper read as a forecasting paper by page 3; is any claim stronger
than at tag `v28.0`; is anything identifying; is the length justified.
*Written:* 2026-09-12.

> This is an internal review produced with a large-language-model assistant
> reading the built PDF against the repository. It is not a report from the
> journal's referees. `AI-USE.md` names the session.

## 1. Does it read as a forecasting paper by page 3?

Yes. Page 2 opens on the forecast a service desk issues, names the register
as a candidate predictor, defines the forecast origin at first use, and
says in a titled paragraph what kind of forecast this is (a probability
forecast of a binary event at a declared origin; not a time series) and
what does not depend on that. The related-work section opens on
Diebold–Mariano, West, Clark–McCracken, Giacomini–White, the reality check,
SPA and the model confidence set, and says in one sentence what object
this paper takes from the family tests that they do not return. Section 4.3
states the difference from the model confidence set where the band is
defined. Section 8 names net benefit as decision-based forecast value in
Murphy's and Granger–Pesaran's sense. A forecasting reader is not asked to
translate.

**Two things a referee would still say.** (a) The primary instrument is the
area under the ROC curve; a forecast-evaluation referee will ask why not a
proper score, and the paper's answer (five declared instruments, AUC first
among them; the decomposition inherits the score's scale, Proposition on
scale) is in the text but not gathered in one place. Left for the journal's
referee; the answer exists and gathering it is a rewrite. (b) The word
*register* is the domain's and is kept; it is glossed at first use.

## 2. Is any claim stronger than at v28.0?

No. Every number is the same macro from the same result file
(`verify_numbers`: 168 re-derived, 41 conditions, 0 failures;
`verify_release`: byte-identical). The rewrite audit found one invented
fact in a draft sentence — a third forecast target, "breach its deadline",
where the design has two — and corrected it before the build. The abstract
dropped two clauses for length (most specifications leave the sign
undetermined; which choice leads is a property of the pair); both remain in
Sections 6 and 11. The object was renamed *incremental forecast
performance* and not *forecast value*, because Section 1 says the paper
reports performance and not value and Section 8 is the only place value is
computed (`DECISIONS.md` §IJF.6); the first draft of the plan had the
stronger name and it would have claimed what the construct paragraph
disclaims.

## 3. Is anything identifying?

`check_blind` reads both blind PDFs and their metadata for the author's
name, e-mail, handle, repository host, archive host, DOI prefix, street, city,
affiliation label, ORCID and the AI vendor and model names: 0 hits. The
software self-citation prints as *Anonymous (2026), details omitted for
double-blind reviewing* in both documents. The code-availability paragraph
points at the title page. Nothing in the file names.

## 4. Is the length justified?

53 pages at the template's 12-point preprint setting: 45 of body, 8 of
references. Five passages were moved to the supplement for this submission
(the service-management reading, the specification-curve comparison, the
corpus commonality, the absorption ladder, the internal-validity detail of
the threats section). The plan's target was 44; the moves that remain
would cut results paragraphs (Section 9.2's per-family detail, the second
half of Section 6.2) and each is a claim to re-audit. The referee's view:
the length is defensible for a methods paper with a registered multi-log
benchmark and a case study; it is not short, and the cover letter says so.

## 5. Defects found in this read, and fixed

1. Five references still pointed at *sections* whose content had moved to
   the supplement (the layer comparison, the construct threats, the
   absorption ladder); each now points at the supplement appendix.
2. Three prose uses of *predict* survived the vocabulary map in Sections 5
   and 10 and one moved appendix; changed. The remaining 37 are the word
   *predictor*, the names of fields and tests, and citations, and are listed
   by `final_search` for the next reader.
3. The old venue's name survived nowhere in prose; the two reference-list
   entries in that journal are legitimate and the `final_search` pattern
   was narrowed to the venue form.

## Recommendation

Ready for the author's steps (`python scripts/finalise.py`: the postcode
and the template diff). No change to the science; the framing is now the
journal's.

# Response to the round-30 read (the pre-upload read of 2026-09-18)

`review_round30.md` read the package as the journal will receive it and
found nine items to fix before upload, eleven that should be fixed, and a
handful of smaller ones. Every item was acted on the same day, in seven
parallel branches and one sequential pass, each built and gated before it
merged; the relocation pass was then read by three independent reviewers,
who refuted its first version on five points, and corrected. What follows
is the disposition of each item.

## Must fix

| item | disposition |
|---|---|
| 1 AI declaration out of date | Macros in `round21_numbers.py` now give the full model sequence and the dates 2026-08-18 to 2026-09-18; `AI-USE.md` gained the 2026-09-18 row (two models, both listed). |
| 2 Anonymous entry sorted under the surname | `build_journal.py` cuts the anonymised `\bibitem` out of its slot and inserts it at the head of the list; first entry in both blind reference lists, nothing under D. |
| 3 "a referee for this journal" (S22) | "a referee of an earlier version"; the log sentence no longer implies this journal's referees. |
| 4 S21.3's pointer to the omitted declaration | Points at the declaration that accompanies the article on its title page; "the author" singular removed. |
| 5 Empty duplicate headings S1.3 / S14.13 | Removed; labels carried to the surviving subsections; S1 has four subsections, S14 seventeen after the compressed copy of S14.3 went too. |
| 6 `BPIC13\_closed` in Table S6 | The generator escaped once; no `textbackslash` in any generated table. |
| 7 Stale data-availability statement | S18 → S23 for the pilot, "Acknowledgements" → the title page's code-availability statement; the amendment count corrected to the protocol's six; `check_response_refs` now parses "(Supplement S<n>)". |
| 8 Three residues (Definition 1, Table 8's caption, equation 3) | "incremental-performance claim"; "forecast target"; the mixed stratum written out as the sum over split-free components that contain quality and an analyst axis. |
| 9 §6.4 against §6.2 | One clause says Table S20 leaves the higher-order remainder as a fourth column that §6.2's stratum partition assigns. |

## Should fix

| item | disposition |
|---|---|
| Template | Downloaded and diffed (`IJF-TEMPLATE-CHECKED.md`); the article builds with `[11pt,3p,review,authoryear]` and `model5-names`; the supplement keeps `preprint,12pt` by decision (`DECISIONS.md` §IJF.5). |
| Figures | Vector PDF beside every PNG, text kept as text; no title above a plot; Figure 2's stale "9.4" is 9.2 and its other pointers follow the renumbering. |
| Empty References heading on the title page | Gone; the title page runs no bibliography. |
| "this journal" in README and the CRediT narrative | README names *Information Systems*; the CRediT text is the current three-use disclosure. |
| Deanonymisation by search | The package name and seven file names print generically in the blind build (`blindnames.tex`); `check_blind` scans for the package name. The harness section keeps its script names by decision. |
| Uncited prior results | "an earlier, unpublished analysis of this log" in the article, Table S11 and S15.1. |
| Supplement tables | Six widest on landscape pages; the `q` column named for what it holds and the captions cite the operative quantile beside it; S15's headings carry a sentence each; Table S20's caption points at the article's §6.4; S18 says "section"; S20 opens by naming the measurement; S1's contrasts sentence weakened to what Table S15 and Class L state. |
| Length | §3.4, §4.7, §6.6 and the §8.3 rules paragraph moved behind pointers; the article keeps the definition of D and R. 54 pages under the template's options after the 2026-09-19 reads added the primary decomposition's per-pair table (Supplement Table S9), two table columns and glosses. |
| AUC as primary instrument | One run-in paragraph at the end of §3.4, restating §1, §2, the remarks, §6.2 and §8; refuted once for overstating, cut back. |
| 43.7% vs 56.0%; the 28.7% figure | Each number's quantity named; "pooled" said where it applies. |

## Smaller

Abstract 143 words; "Uncertainty" and "specification surface" replaced from
the IIF list; six reference entries name six authors before "et al."; Van
Calster written one way; the forecast origin's other two names glossed at
first use; the cover letter states the figures are greyscale vector PDFs and
gives the current page and passage counts; the rebuilt PDFs are committed.

## Found on the way, not in the read

A `\resizebox` on stacked column headings hid two columns from the round-27
verifier's name lookup, so two checks of the denominator table skipped
silently; the header parser now unwraps the stacked form. A sentence in §9
that an earlier length pass had garbled ("read at (Figure S5).") is restored
from its history. Table S8's caption cited an article equation by bare
number from inside the supplement; it now says "of the article".

Gates after everything: all nine at zero; `verify_release` untouched
(no analysis result changed); article 54 pages, supplement 121, title page 3.

## The 2026-09-19 reads

Three independent reads of the revised build (a fix-checker, a cold referee
read of the blind article, a package check) and eight read-only
investigations of the number-backed items found: the article said both that
stationarity is tested (§3.2) and not tested (§9) — the §9 sentence now says
mixing is assumed and stationarity tested; six pointers sent the reader to
§10 for internal-validity detail that lives in Supplement S20; "every table
prints what the multiplier would have resolved" was unsupported and now says
what is printed (the multiplier's critical value beside the operative one)
and what is in the archive (both estimators' edges and labels); the
amendments' dates are in the protocol file, not in S1, and both texts now
say so; the baseline rungs are enumerated once (§5.2) and the four decision
rules defined once (S3.1) and glossed at first use (§1, §4.6); "40 of 118
arms" is "models", a model being a pair–pipeline–baseline triple; S14.7
opens on the band the article reports; the plane/grid of §9.1 are named apart
(10-cell grid, Table S39; 33-cell calibration plane, Table S42) with each
number attributed to its source; "13 of 19 pairs" says what it counts (the
higher-order total against the largest first-order index within an
instrument, not against Table S8's column medians); Table 5's "304
decompositions" is now the 19 × 5 the strata identity was checked on, and S3
derives 304; the two 1,100s are named apart (a resolved-cell count; the
grid's rounding of the modal curve family); Table 2's origin row and caption
say the corpus surface has two origins on the primary log and the case
study's second surface three; Table S41 now rounds half-cases the way the
macros do (sixteen cells moved by one in the last digit); and the primary
decomposition's per-pair values, which the article quoted but no table
printed, are Supplement Table S9 (`tables/foldavg.tex`, generated from the
same aggregation as the macros). Also the headroom scale, PC3, the Fieller
set (now cited), the conservative and one-number rules, and "collapse rule"
glossed or renamed at first use; "the author" removed from a blind sentence;
one name for the literature pilot. The all-caps emphasis in several
generated supplement captions is a house style production may query; it is
left as is.

## The fourth and fifth reads (2026-09-19)

Two further rounds, each of a fix-checker, a cold referee read and a package
check, found: the operative critical value was not printed in the region
tables the article said print it beside the multiplier's — both tables now
carry `q (operative)', so `q calibrated' is visibly $c$ times it; Table S38
now prints the reported construction's coverage of the oracle increment,
which §9.1 quoted; the six declared mechanisms, the three dependent ones and
the discovery lag are named apart, and pointed at Supplement S1.2 where they
are defined; the pipeline tiers are stated as the rule gives them (the
primary log by designation, the rest by row count); the held-out set is
described as the two logs it was, one scored and one excluded by the rules;
the title page says the model register and the objection log are in the
repository, whose head post-dates the archived release; §10 no longer says
the operating point varies on the case study's log alone; §6.5 and S17 no
longer say the region label is computed on the permutation sub-surface,
which Table S23's caption denies; the three-measure claim is confined to the
pooled decomposition's headline shares (Table S27); Table 2's caption points
at §5 for why the target is not an axis; the glossary's case-study region
value points at the master table instead of a stale label; the two
empirical-over-multiplier ratios (1.24, 1.25) are named as a width ratio and
a critical-value ratio; and a dozen smaller pointer, naming and record
items. 54 / 119 / 3 pages; every gate at zero.

## The sixth and seventh reads (2026-09-19)

A cold read of the blind supplement — its first — and the fix and package
checks found, and the following fixed: two generator errors that changed what
the supplement prints (the BPIC19 layer macros had been computed on the
handover pair the registered rules exclude and Table S1 never prints, and the
"coarse max" left out the vendor, the one layer on that log worth anything;
the unseen-rate minimum had been read from the intercept-only rung no table
prints, so "0%" is now the admissible reference cell's 5%); a caption that
said twenty seeds where the case-study run used three (a new macro reads the
run's own count); a caption ratio (3.7) that divided quantities its own text
did not name (dropped); the noisy world's withdrawn 7.0% attributed to
Section 9 in the present tense (attributed to the first version, with the
corrected coverage beside it); a clause that pointed at a table for a
measurement no table prints (the indicator encoder's zero, now stated with
its macro and its result file); the desk distribution's thresholds derived
from cost ratios that do not give them (the mapping is now stated and the
quantiles named as the Beta's); reversed column headers on two rows of Table
S36 (the endpoints are named by level); S4 and S18 rewritten so BPIC19 is
described as the table shows it, with its non-nesting hierarchy said; the
sign-disagreement rate no longer called the headline the article withdrew;
S9.4's calibrated counts qualified as before the minimum resolved share; the
prevalence bases of §5.3, §7.1 and S1.4 named; the dossiers described as
rebuilt by script rather than committed; the form text's harness description
brought to the current scripts; the cover letter's archive claims made true
of the repository; stale pointers to §3.4, §6.3 and §4.1 for content in S2,
S9.4, S9.7 and §9.1; and a dozen grammar and pointer items. Two of the
previous round's own corrections (a prevalence base, an inference from two
shares) were refuted and corrected again.

## The eighth read (2026-09-19)

The supplement's second cold read, the fix-checker and the package check.
Fixed: three of the previous batch's own sentences overreached (a caption that
generalised the endpoints of a severity sweep to rows where the top level is
not the complete register; a determinism test invoked as if it singled out
BPIC19 when the cardinality inversion is the only log-specific fact; a
misplaced modifier that had the dossiers rebuilt "in the sample file"); the
supplement's abstract credited the article with the calibration's derivation;
Table S5's prevalence column is named as the test half's; S9.4's two
under-covered cells and the largest shortfall are attributed to the cells
they belong to; S8.1's "every family at 400 draws" is confined to the corpus
families; S5 says which folds enter the inference family; S13 says the two
drift mechanisms are in the result file, not Table S6; S6 says which table
holds the limit's coverage and where the oracle rows are; Table S1's case
counts are explained; negative numbers in text mode get a real minus sign
(the register had listed that as a fixed defect while six macros still
printed a hyphen); and the archive question: the archived release would
print three summaries the submitted supplement does not (corrections
C32–C34, now in the register's Class N), so the title page, the article's
data-availability paragraph and the cover letter say so, and `DECISIONS.md`
§IJF.3 records that the condition for re-cutting the archive is met and
leaves the choice to the author (`OWNER-ACTIONS.md` step 7a).
54 / 121 / 3 pages; every gate at zero.


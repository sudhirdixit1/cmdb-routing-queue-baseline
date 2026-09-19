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
(no result file changed); article 54 pages, supplement 120, title page 3.

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
items. 54 / 120 / 3 pages; every gate at zero.


# Round twenty-seven: where it stands, and how to resume

Stopped mid-run on the owner's instruction (the machine was running hot). No
work is lost: the long run resumes pair by pair.

## The one thing still running when it stopped

`scripts/s44_designed.py` — the designed, balanced inference surface at 400
draws under both resampling schemes. Killed with 13 of 38 pair-runs finished.

**Resume with exactly this, and nothing else:**

```bash
python scripts/s44_designed.py --scheme both --draws 400 --procs 12 --resume
```

`--resume` skips any pair whose output already carries 400 draws, so the 13
below are not recomputed. Lower `--procs` (6 or 8) if heat is the constraint;
it costs wall-clock and changes no number.

Finished (weighted): BPIC13_closed/handover, BPIC13_incidents/duration and
/handover, BPIC14/duration and /handover, BPIC15_1/duration and /handover,
BPIC15_3/duration and /handover, BPIC15_4/duration and /handover,
BPIC15_5/duration, BPIC17/duration.

Still to run: BPIC19, Helpdesk, RoadFines, Sepsis, UCI498 (both targets) under
`weighted`, and all nineteen under `multinomial`. BPIC19 is the expensive one
at about 70s a draw; RoadFines about 16s; everything else 3–9s.

**Note:** `results/s44_facts.csv` on disk is from the four-draw smoke run, not
the real one. Do not read it until the run completes. The per-pair `.csv.gz`
files are the truth: a finished pair is about 10 MB, a smoke pair about 130 KB.

## What runs after it, in order

```bash
python scripts/s21_bands.py --draws-dir s44_weighted    --prefix s48w
python scripts/s21_bands.py --draws-dir s44_multinomial --prefix s48m
python scripts/s47_schemes.py          # the two schemes, compared
python scripts/s41_bandcoverage.py     # coverage, now with a non-zero-truth regime
python scripts/provenance.py --accept s44_designed.py --note "..."
python scripts/provenance.py --accept s21_bands.py --note "..."
python scripts/provenance.py --accept s41_bandcoverage.py --note "..."
```

`s41` is the heaviest of these after `s44` — 58,000 replicates of matrix
arithmetic, no pipeline refitted. It parallelises; give it `--procs`.

## What is already done and committed

- **R3, all five inconsistencies**, each repaired at its generator and each
  made a condition in `scripts/round27_verify.py`, exercised against the exact
  defect it replaces.
- **R2, the revision narrative**: thirteen passages rewritten, and
  `texlint` check 16 now scans every part of both documents for three families
  of it. It found the two the manual pass missed.
- **R4, partly**: `LICENSE` (MIT, matching `.zenodo.json`), `NOTICE-DATA.md`,
  the supplement added to the submission manifest, and
  `scripts/check_package.py` to hold both. The DOI is still owner-only —
  see `submission/OWNER-ACTIONS.md`.
- **Phase 5**: the prefix-axis pilot (`s45_prefix.py`) and the stationarity
  diagnostic (`s46_drift.py`), both run, both written into Section 11 and the
  supplement.
- Two loader paths that could not find the corpus this repository fetches, and
  round twenty-two's withdrawn "coarse layers are close to free", which was
  still standing in the supplement.
- **Phase 3, partly**: 61 → 58 pages.

## What is not done

- **Phase 1's write-up.** The run above produces it. Section 4.3, Section 6.1
  and 6.3, Section 10.4 and Section 11 are written against the OLD inference
  surface and must be rewritten against the new one. Section 11's paragraph
  beginning "Internal --- the refitting bootstrap is the source of a bias"
  is the one that says the repair is not run.
- **Phase 3's remainder.** 58 pages against a target of 42. Getting there
  needs Section 4, Section 6, Section 10 and Section 11 — 27 of the body's 46
  pages — written compactly against the new numbers, which is why it waits for
  the run rather than being done twice.
- **Phase 4's DOI**, which needs the depositing account.
- **Phase 6**, the pre-submission red-team pass.

## One finding worth carrying forward — diagnosed, disclosed and gated

**The earlier statement of this finding was wrong in two ways, and both
corrections make it worse.** It said the problem was the boosting learner and
that `logit` reproduced to 5e-10. Neither holds. Phase 6 re-ran the surface
cell by cell and measured 41,472 values across four logs and both families.

What is actually true. The discrepancy tracks **cardinality**, not the
learner. Wherever the design matrix carries no high-cardinality categorical —
the `B_empty` and `B_half` rungs — everything reproduces to 2.3e-12, and the
boosting half of that to machine epsilon. Wherever it does carry one, both
families diverge: boosting by up to **0.85** in Nagelkerke (not 0.14), and
`logit` by up to **0.094** in Nagelkerke, 0.039 in AUC and 0.128 in net
benefit. `logit` reproduces to 5e-10 only on the undegraded `clean` and
`stale` cells, which is where the earlier check happened to look.

The cause is **platform**, and it is not fixable by pinning threads. Four
candidates were eliminated by measurement: thread count (one thread and four
are bit-identical), library version (scikit-learn 1.7.2 and 1.9.0, pandas
2.2.3 and 2.3.1, CPython 3.11 and 3.13 all bit-identical to each other),
source drift (the `spec.py` of the commit that wrote the surface is
bit-identical to the current one), and run-to-run nondeterminism (there is
none). The committed surface was produced on x86-64 and this machine is
arm64. The mechanism is amplification: a **one-ULP** nudge to the boosting
encoding matrix moves a predicted probability by 0.37 and Nagelkerke by 0.038.
The logistic model is not chaotic — its probabilities agree to 1.4e-15 — but
AUC, average precision and net benefit are step functions, and a one-hot
register ties test rows to equal predictions that a 1e-15 difference unties.

One genuine, repairable defect was found alongside it and is **not** repaired,
because repairing it changes every committed number: `mask_rare` cuts the
cumulative-count curve *inside* a group of identities that share a count, and
`corrupt` maps its draws onto a tie-ordered index, so which identities are
masked or corrupted rests on a tie order nothing pins. It belongs with the run
that regenerates the surface.

Disclosed in `REPRODUCE.md` §5.1, with the measured tolerance per family and
metric class and the container named as the canonical bit-exact environment.
Gated by `scripts/check_reproduction.py` — the first gate in this repository
that re-runs an analysis rather than re-deriving macros from the committed
CSVs, which is precisely why nothing caught this. Its own corruption suite is
`scripts/attack_reproduction.py`; six cases, all caught.

Still owner-only: the Dockerfile pins `python:3.10.0-slim-bullseye` by tag and
not by digest, and no built-image digest is recorded anywhere in the
repository. §5.1 calls that digest canonical, so it has to be minted and
written in at release.

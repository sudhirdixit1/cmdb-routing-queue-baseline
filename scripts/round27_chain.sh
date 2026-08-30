#!/bin/sh
#  Round twenty-seven.  s44_designed.py runs the weighted and multinomial
#  schemes over one balanced design at 400 draws; everything below reads its
#  output and nothing below refits a pipeline.  This file waits for that run
#  to end and then runs the readers in dependency order, so the long pole is
#  the only thing that needs a person watching it.
#
#      sh scripts/round27_chain.sh              # wait, then run
#      sh scripts/round27_chain.sh --now        # assume s44 is done already
#
#  WHY A WAIT RATHER THAN A DEPENDENCY.  s44 is resumable and was stopped once
#  mid-run for machine heat, so it may be restarted by hand more than once.
#  Waiting on the PROCESS rather than on a marker in a log means a restart is
#  invisible to this script: it notices only when no s44 is running at all.
#
#  WHAT IT DELIBERATELY DOES NOT DO.  It does not build the manuscript, does
#  not run make_numbers, and does not touch git.  The numbers this produces
#  change headline claims -- Section 4.1, 4.2, 4.3, 6.1, 6.3, 10.4 and 11 are
#  written against the OLD inference surface -- so a person has to read the
#  results before the paper quotes them.  PLAN-ROUND27.md 1.4 lists what has
#  to be rewritten, and 5.1a is the register of which claims move and which
#  are safe.  Regenerating macros before that reading would put new numbers
#  under old sentences, which is the failure this project has had before.
set -e
cd "$(dirname "$0")"
mkdir -p ../logs
PY=/usr/local/bin/python3

if [ "$1" != "--now" ]; then
  echo "== waiting for s44_designed.py to finish =="
  while pgrep -f s44_designed > /dev/null 2>&1; do
    sleep 60
  done
fi

W=$(ls -la ../results/s44_weighted/*.csv.gz 2>/dev/null | awk '$5 > 1000000' | wc -l | tr -d ' ')
M=$(ls -la ../results/s44_multinomial/*.csv.gz 2>/dev/null | awk '$5 > 1000000' | wc -l | tr -d ' ')
echo "== s44 finished: weighted $W/19, multinomial $M/19 =="
if [ "$W" -lt 19 ] || [ "$M" -lt 19 ]; then
  echo "!! INCOMPLETE.  A pair short of 19 means the run was interrupted, not"
  echo "!! that it failed: resume it and re-run this script."
  echo "!!   $PY scripts/s44_designed.py --scheme both --draws 400 --procs 8 --resume"
  exit 1
fi

#  The bands, once per scheme.  Two prefixes so the comparison in s47 has two
#  objects to compare rather than one overwritten one.
for arg in "s44_weighted s48w" "s44_multinomial s48m"; do
  set -- $arg
  echo "-- s21_bands.py --draws-dir $1 --prefix $2"
  $PY s21_bands.py --draws-dir "$1" --prefix "$2" > "../logs/${2}_r27.log" 2>&1
  tail -2 "../logs/${2}_r27.log"
  #  Validate the bands on their own terms before anything quotes them.  The
  #  condition that earns this is that the region labels are counted at the
  #  CONSERVATIVE edge: a band built from one edge with labels counted from
  #  another agrees on most pairs and differs on a few, which looks like a
  #  rounding difference until somebody checks a pair by hand.
  $PY check_bands.py --prefix "$2"
done

#  The comparison that decides whether the repair was worth making.  Its
#  headline is the count of cells whose pivotal interval excludes its own
#  point estimate: 74 of 3,900 under the old scheme, and the weighted scheme
#  is supposed to take that to zero.  If it does not, the paper says so.
echo "-- s47_schemes.py"
$PY s47_schemes.py > ../logs/s47_r27.log 2>&1
tail -4 ../logs/s47_r27.log

#  Family-wise coverage, now with the non-zero-truth regime.  Heaviest of the
#  readers -- 58,000 replicates of matrix arithmetic, no pipeline refitted.
#
#  --draws-dir IS NOT OPTIONAL HERE.  s41 matches its synthetic families to a
#  real surface's shape, and its default is the OLD surface, `s20'.  Running it
#  without this flag measures the coverage of families matched to a surface the
#  manuscript no longer reports, and the number looks entirely reasonable.  The
#  profile is cached per source, so a run interrupted after stage 1 resumes
#  from `results/s41_profile_s44_weighted.csv' rather than re-profiling.
echo "-- s41_bandcoverage.py --draws-dir s44_weighted"
$PY s41_bandcoverage.py --draws-dir s44_weighted --procs 8 \
    > ../logs/s41_r27.log 2>&1
tail -4 ../logs/s41_r27.log

#  The decision-curve widening is a function of s41's measured shortfall, so
#  it is recomputed after s41 rather than before it.
echo "-- s49_dcaband.py"
$PY s49_dcaband.py > ../logs/s49_r27.log 2>&1
tail -3 ../logs/s49_r27.log

echo
echo "== accepting the scripts into the provenance record =="
$PY provenance.py --accept s44_designed.py \
  --note "Round twenty-seven: the designed inference surface. One balanced full factorial on every pair -- 2 learners x 2 splits x 3 quality conditions x 3 rungs, 180 scalar members -- at 400 draws under both resampling schemes, replacing a surface chosen by row count that was axis-complete but unbalanced." || true
$PY provenance.py --accept s21_bands.py \
  --note "Round twenty-seven: bands on the designed surface, run once per scheme." || true
$PY provenance.py --accept s47_schemes.py \
  --note "Round twenty-seven: the two resampling schemes compared on one design at one draw count with one set of seeds." || true
$PY provenance.py --accept s41_bandcoverage.py \
  --note "Round twenty-seven: family-wise coverage with the non-zero-truth regime added, because under a zero truth every rejection is an error and coverage cannot tell a band that resolves correctly from one that never resolves." || true

#  FOUR GENERATORS THAT FEED MACROS AND THAT NO RUNNER INVOKED.
#
#  `s42_round26' produces the resolved map behind `madResolvedMedian' -- THE
#  ABSTRACT'S NUMBER -- and it consumes `s34_reporting''s output.  When s34
#  was re-pointed at the reported surface, nothing re-ran s42, so every macro
#  derived from it was fifteen minutes stale and the abstract printed 0.0510
#  where the current pipeline gives 0.0556.  `s45', `s46' and `s51' were
#  orphaned the same way: the prefix axis, the stationarity test the surface
#  definition now cites, and the decomposition on the inference surface.
#
#  Order matters: s42 reads s34, which `reproduce_all.py` runs in its
#  analysis waves before this chain.
echo
echo "== the generators the macro layer depends on =="
$PY s45_prefix.py
$PY s46_drift.py
$PY s51_infanova.py --draws-dir s44_weighted
$PY s42_round26.py

#  THE ESTIMATOR COMPARISON, ON THE SURFACE THE ARTICLE ACTUALLY REPORTS.
#  s40 read two fixed filenames, so when the inference surface moved it went
#  on comparing the two critical-value estimates on the RETIRED one -- and the
#  appendix then printed a multiplier total LARGER than the number of cells
#  the article says that same band resolves.  The multiplier band IS the
#  article's band, so its count has to equal the headline; round27_verify
#  now enforces that equality.
echo
echo "== s40  the two critical-value estimates, on the reported surface =="
$PY s40_qcheck.py --prefix s48w
$PY provenance.py --accept s40_qcheck.py \
  --note "Round twenty-seven: the bands prefix is an argument, so the estimator comparison follows the inference surface instead of reading a retired one." || true

echo
echo "== DONE.  Do not regenerate macros yet. =="
echo "Read these first:"
echo "  results/s47_facts.csv    displacement, level coverage, and the count"
echo "                           of cells whose interval excludes its estimate"
echo "  results/s41_facts.csv    family-wise coverage, per regime"
echo "Then work PLAN-ROUND27.md 1.3 (which scheme the paper adopts), 1.4"
echo "(the sections written against the old surface) and 5.1a (the register"
echo "of claims at risk).  Only then make_numbers, assemble, build."

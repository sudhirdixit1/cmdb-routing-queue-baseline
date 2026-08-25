#!/bin/sh
#  Round twenty-one.  The new experiments, in the order a run that is cut
#  short should have lost the least.  Each writes its own results/*.csv and
#  its own log; none reads another's output except s34, which reads s33's
#  calibrated critical value when it exists and falls back to the nominal
#  one when it does not.
set -e
cd "$(dirname "$0")"
mkdir -p ../logs

echo "== s38  the decision time as a real axis =="
python s38_tau.py --draws 300 > ../logs/s38.log 2>&1
tail -3 ../logs/s38.log

echo "== s37  learner and encoding, crossed =="
python s37_axes.py > ../logs/s37.log 2>&1
tail -3 ../logs/s37.log

echo "== s33  the coverage-calibrated critical value =="
python s33_calibrate.py --reps 500 > ../logs/s33.log 2>&1
tail -3 ../logs/s33.log

echo "== s36  against specification-curve analysis =="
python s36_sca.py --perms 200 > ../logs/s36.log 2>&1
tail -3 ../logs/s36.log

echo "== s34  sign disagreement, recomputed under the calibrated band =="
python -W ignore s34_reporting.py > ../logs/s34.log 2>&1
tail -3 ../logs/s34.log

echo "== s35  the decision in units a desk uses =="
python -W ignore s35_utility.py > ../logs/s35.log 2>&1
tail -3 ../logs/s35.log

echo "ROUND 21 CHAIN COMPLETE"

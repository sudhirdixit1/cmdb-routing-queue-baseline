#!/bin/sh
#  Round twenty-two.  The declared surface gained a pipeline on the two
#  largest logs so that the inference surface is a subset of it, so
#  everything that reads the surface has to be recomputed.  Waits for s01 to
#  finish, then runs the readers in dependency order.
set -e
cd "$(dirname "$0")"
mkdir -p ../logs
while ! grep -q "wrote s01_" ../logs/s01_r22.log 2>/dev/null; do
  sleep 30
done
echo "== s01 done; recomputing everything that reads the surface =="

for s in s03_decompose.py s04_regret.py s22_anova.py s25_denominator.py; do
  echo "-- $s"
  python "$s" > "../logs/${s%.py}_r22.log" 2>&1
  tail -2 "../logs/${s%.py}_r22.log"
done

echo "-- s23_regret.py"
python s23_regret.py > ../logs/s23_r22.log 2>&1
tail -2 ../logs/s23_r22.log

echo "-- s33_calibrate.py --reuse"
python s33_calibrate.py --reuse > ../logs/s33_r22.log 2>&1
tail -3 ../logs/s33_r22.log

echo "-- s34_reporting.py"
python -W ignore s34_reporting.py > ../logs/s34_r22.log 2>&1
tail -3 ../logs/s34_r22.log

echo "-- s35_utility.py"
python -W ignore s35_utility.py > ../logs/s35_r22.log 2>&1
tail -3 ../logs/s35_r22.log

echo "-- s36_sca.py on every admitted pair (the long one)"
python s36_sca.py --perms 200 > ../logs/s36_r22.log 2>&1
tail -4 ../logs/s36_r22.log

echo "ROUND 22 CHAIN COMPLETE"

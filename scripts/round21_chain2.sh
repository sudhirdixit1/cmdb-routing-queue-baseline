#!/bin/sh
#  The second half of round twenty-one's chain: the two runs that put
#  Section 7 on one cohort.  Waits for the first chain to release the pool.
set -e
cd "$(dirname "$0")"
mkdir -p ../logs
while ! grep -q "ROUND 21 CHAIN COMPLETE" ../logs/chain21.log 2>/dev/null; do
  sleep 30
done

echo "== s39  the case study's quality and absorption, on its own cohort =="
python s39_case_quality.py --draws 400 > ../logs/s39.log 2>&1
tail -3 ../logs/s39.log

echo "== s08  the decision-time ladder, under a declared tie-break =="
python s08_decision_time.py > ../logs/s08.log 2>&1
tail -3 ../logs/s08.log

echo "ROUND 21 CHAIN 2 COMPLETE"

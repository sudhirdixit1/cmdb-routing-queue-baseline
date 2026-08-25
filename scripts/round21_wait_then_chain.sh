#!/bin/sh
#  Wait for the cohort reconciliation to release the pool, then run the rest.
#  Oversubscribing fourteen cores with twenty-four workers makes both runs
#  slower than running them in sequence, which is the only reason this exists.
cd "$(dirname "$0")"
while [ ! -f ../results/s32_path.csv ] || \
      grep -q "24 cells" ../logs/s32.log && \
      ! grep -q "wrote s32" ../logs/s32.log; do
  sleep 20
done
exec sh round21_chain.sh

#!/usr/bin/env bash
#  Round twenty: everything downstream of the inference surface, in dependency
#  order, so the machine is never idle waiting for a human.
#
#  s20 (the inference surface) is the long pole and is launched separately.
#  This waits for it, then runs the analyses that read it, then the analyses
#  that read those, then the generators, the checks and the build.
#
#      bash scripts/round20_chain.sh
#
#  Every stage appends to logs/chain.log and prints its own header, so an
#  interrupted run can be resumed by commenting out what has completed.
set -u
cd "$(dirname "$0")/.."
LOG=logs/chain.log
mkdir -p logs
say() { echo ""; echo "=== $* ($(date +%H:%M:%S)) ==="; }

#  Wait for the s20 PROCESS, not for its output file.  A smoke run of one
#  pair writes results/s20_facts.csv too, and a chain that keyed on the file
#  would start the downstream analyses while the real run still had eighteen
#  pairs to go.  A process check cannot be fooled that way.
say "waiting for s20 to finish"
while true; do
  n=$(ps -W 2>/dev/null | grep -ci 'python' || echo 0)
  running=$(python - <<'PY'
import subprocess, sys
try:
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
         "Where-Object { $_.CommandLine -like '*s20_boot2*' } | "
         "Measure-Object).Count"],
        capture_output=True, text=True, timeout=60).stdout.strip()
    print(out or "0")
except Exception:
    print("0")
PY
)
  [ "${running:-0}" = "0" ] && break
  sleep 60
done
say "s20 done"

#  s24 and s26 are independent of each other and of s21; run them one at a
#  time so neither starves the other on a machine with under three cores of
#  sustained throughput.  s27 is not independent -- see below.
say "s24 planned contrasts at 2,000 draws"
python -u scripts/s24_confirm.py --draws 2000 --procs 12 || echo "s24 FAILED"

say "s26 calibration and decision curves"
python -u scripts/s26_calib_dca.py --draws 200 --procs 12 || echo "s26 FAILED"


say "s21 whole-surface bands"
python -u scripts/s21_bands.py || echo "s21 FAILED"

#  s27 is NOT independent of s21: it compares its mechanism variability
#  with the sampling standard errors in results/s21_cells.csv.  It ran
#  BEFORE s21 for one round, read the previous round's file, matched
#  nothing, and left a macro unresolved rather than wrong -- which only
#  surfaced because every macro is checked.

say "s27 register quality  (after s21: it reads s21_cells.csv)"
#  One target rather than two: the register-quality study is about the case
#  study, whose decision is the handover one, and twenty seeds over eleven
#  severities on two targets is twice the compute for a second answer to a
#  question this section does not ask.
python -u scripts/s27_quality.py --seeds 20 --levels 11 --procs 12 \
    --targets handover || echo "s27 FAILED"

say "s22 corrected decomposition, with draw-level uncertainty"
python -u scripts/s22_anova.py --envelope-draws 200 || echo "s22 FAILED"

say "s23 regret on a coherent scale"
python -u scripts/s23_regret.py || echo "s23 FAILED"

say "s25 denominator audit"
python -u scripts/s25_denominator.py || echo "s25 FAILED"

say "s28 figures"
python -u scripts/s28_figures.py || echo "s28 FAILED"

say "numbers, tables, registry"
python -u scripts/make_numbers.py || echo "make_numbers FAILED"
python -u scripts/assemble_paper.py || echo "assemble FAILED"
python -u scripts/claim_registry.py || echo "registry FAILED"

say "checks"
python -u scripts/texlint.py || echo "texlint reported failures"
python -u scripts/verify_numbers.py || echo "verify reported failures"

say "build"
python -u scripts/build_journal.py || echo "build reported problems"

say "chain complete"

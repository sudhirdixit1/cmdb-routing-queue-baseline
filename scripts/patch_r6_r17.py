"""`r6_final.py` has not parsed since 2026-08-20 03:13.

`python scripts/reproduce_all.py` -- the one-command reproduction this
repository advertises, and which the paper cites as evidence about itself --
fails in wave 2 with a SyntaxError. It has failed there since round four.
`results/r6_*.csv` are dated 02:00 that morning, an hour before the break, so
every round from five to seventeen has been reading result files no round
could regenerate.

The bug is one print statement. An f-string expression cannot span adjacent
string literals: each `f"..."` is parsed on its own, so

    f"({100*pd.read_csv(...).set_index('leg')"
    f".loc['random cells, ...', 'recovered'] / g_naive:.0f}%)."

leaves the first literal with an unclosed `{`. The value is computed before
the print now, which is what should have happened in the first place.

Two things this says about the artifact, both recorded in HANDOFF §20.12:

  * nobody had run `reproduce_all.py` to completion, including the round that
    wrote it and claimed it worked; and
  * a syntax error in a pipeline script is invisible to a checker that reads
    the pipeline's OUTPUT files. `verify_paper.py` passed 936 checks against
    `r6_gains.csv` while the script that writes it could not be parsed.

`scripts/lint_scripts.py` now compiles every script in `scripts/` and
`reproduce_all.py` runs it in preflight, so this class cannot reach wave 2
again.

    python scripts/patch_r6_r17.py --check
    python scripts/patch_r6_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R6 = ROOT / "scripts" / "r6_final.py"
RA = ROOT / "scripts" / "reproduce_all.py"

OLD = '''print(f"  equal-size partition of items retains MORE "
      f"({100*pd.read_csv(RESULTS / 'r8_dropped_leg.csv').set_index('leg')"
      f".loc['random cells, uniform over items', 'recovered'] / g_naive:.0f}%)."
      f"  The leg is")'''

NEW = '''#  An f-string expression may not span adjacent string literals: each
#  f"..." is parsed on its own, so splitting one across four of them leaves
#  the first with an unclosed brace.  This file has not parsed since
#  2026-08-20 03:13 for that reason.  Compute the value, then print it.
_rand_cells = float(pd.read_csv(RESULTS / "r8_dropped_leg.csv")
                    .set_index("leg")
                    .loc["random cells, uniform over items", "recovered"])
print(f"  equal-size partition of items retains MORE "
      f"({100 * _rand_cells / g_naive:.0f}%).  The leg is")'''

#  r6 reads r8_dropped_leg.csv, so it cannot share a wave with r8.
WAVE_OLD = '''        "r5_final.py",          # nulls, mutation sensitivity
        "r6_final.py",          # the gains the headline table prints
        "r8_final.py",          # mechanism, design space, scoping'''
WAVE_NEW = '''        "r5_final.py",          # nulls, mutation sensitivity
        "r8_final.py",          # mechanism, design space, scoping'''

WAVE_ADD_OLD = '''    [
        "r10_estimators.py",    # r21 section C reads r10_estimators.csv
        "r11_operational.py",   # r21 section C and r23 read r11_*.csv
    ],'''
WAVE_ADD_NEW = '''    [
        "r10_estimators.py",    # r21 section C reads r10_estimators.csv
        "r11_operational.py",   # r21 section C and r23 read r11_*.csv
        #  r6 reads r8_dropped_leg.csv, so it cannot share a wave with r8.
        #  It did, which nobody noticed because r6 never ran at all.
        "r6_final.py",          # the gains the headline table prints
    ],'''

LINT_OLD = '''    try:
        import numpy, pandas, sklearn, scipy, matplotlib
    except ImportError as e:
        sys.exit(f"missing dependency: {e}.  pip install -r requirements.txt")'''
LINT_NEW = '''    try:
        import numpy, pandas, sklearn, scipy, matplotlib
    except ImportError as e:
        sys.exit(f"missing dependency: {e}.  pip install -r requirements.txt")
    #  ROUND SEVENTEEN.  r6_final.py did not PARSE for thirteen rounds, and
    #  the failure only surfaced in wave 2 of a 70-minute run.  A checker that
    #  reads a pipeline's output files cannot see a pipeline script that never
    #  runs, so the parse check happens here, in seconds, before anything else.
    import ast as _ast
    _broken = []
    for _p in sorted(SCRIPTS.glob("*.py")):
        try:
            _ast.parse(_p.read_text(encoding="utf-8"))
        except SyntaxError as _e:
            _broken.append(f"{_p.name}:{_e.lineno}: {_e.msg}")
    if _broken:
        print("\\n  SCRIPTS THAT DO NOT PARSE:")
        for _b in _broken:
            print("    " + _b)
        sys.exit("preflight failed: fix these before running anything")
    print(f"  all {len(list(SCRIPTS.glob('*.py')))} scripts parse")'''


def main(argv):
    r6 = R6.read_text(encoding="utf-8")
    ra = RA.read_text(encoding="utf-8")
    checks = [("r6-fstring", r6, OLD), ("wave-remove", ra, WAVE_OLD),
              ("wave-add", ra, WAVE_ADD_OLD), ("preflight-lint", ra, LINT_OLD)]
    missing = [f"{n}: anchor appears {s.count(o)} times"
               for n, s, o in checks if s.count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print("all 4 anchors found")
        return 0
    R6.write_text(r6.replace(OLD, NEW, 1), encoding="utf-8")
    ra = ra.replace(WAVE_OLD, WAVE_NEW, 1)
    ra = ra.replace(WAVE_ADD_OLD, WAVE_ADD_NEW, 1)
    ra = ra.replace(LINT_OLD, LINT_NEW, 1)
    RA.write_text(ra, encoding="utf-8")
    print("  fixed r6_final.py, moved it out of r8's wave, added a parse "
          "check to preflight")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Refresh every count this round's documentation quotes.

`submission/cover_letter.md` has a standing note that the previous version
quoted counts that had moved; this script is the answer to that. Run it after
any change to the paper or the checker, and check the diff.

    python scripts/patch_counts_r17.py --check
    python scripts/patch_counts_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EDITS = [
    ("readme-counts", "README.md",
     """```
890 checks passed, 0 failed
410 literals in body; 0 unaccounted; 401 compared against data
183 caught, 0 missed, 0 skipped of 183
```""",
     """```
934 checks passed, 0 failed
417 literals in body; 0 unaccounted; 405 compared against data
198 caught, 0 missed, 0 skipped of 198
```"""),
    ("readme-suite-size", "README.md",
     "`attack_verifier.py` is its regression suite: 183\ncorruptions.",
     "`attack_verifier.py` is its regression suite: 198\ncorruptions."),
    ("readme-retired", "README.md",
     """  seventeen). Thirty-nine checks whose anchoring sentence no longer exists sit
  in a `RETIRED` set naming the claim that went. That is safe only because a
  literal freed by a retirement and not re-checked becomes unaccounted and the
  run fails. Never retire a check because it fails.""",
     """  seventeen). Forty-two checks whose anchoring sentence no longer exists sit
  in a `RETIRED` set naming the claim that went. That is safe only because a
  literal freed by a retirement and not re-checked becomes unaccounted and the
  run fails. Never retire a check because it fails — and note that a
  retirement can unguard PROSE it was not retired for, which is how the suite
  caught one this round.""",),
    ("repro-suite-size", "REPRODUCE.md",
     """`scripts/attack_verifier.py` is the checker's regression suite: 183
corruptions drawn from defects found in earlier versions of this work,
including five that mutate a *relation* rather than a value, because that is
the class the two new corrections belong to.""",
     """`scripts/attack_verifier.py` is the checker's regression suite: 198
corruptions drawn from defects found in earlier versions of this work,
including five that mutate a *relation* rather than a value, because that is
the class the two new corrections belong to."""),
    ("repro-guard-order", "REPRODUCE.md",
     """`ck`/`ck_bound`/`ck_phrase`/`ck_word` **call** appears after that call site.""",
     """`ck`/`ck_bound`/`ck_phrase`/`ck_word` **call** appears after that call site.
The guard-or-declare lint turned out to have the same bug for the same reason
and is now called from the same block; the self-lint names both call sites."""),
    ("cover-counts", "submission/cover_letter.md",
     """verification harness that recomputes each of the 410 numeric literals in the
manuscript from a result file or from the raw data.""",
     """verification harness that recomputes each of the 417 numeric literals in the
manuscript from a result file or from the raw data."""),
    ("cover-suite", "submission/cover_letter.md",
     """A second harness, a suite of 183
corruptions drawn from defects found in earlier versions of this work, is the
verifier's own regression test.""",
     """A second harness, a suite of 198
corruptions drawn from defects found in earlier versions of this work, is the
verifier's own regression test."""),
    ("cover-notes", "submission/cover_letter.md",
     """      `python scripts/reproduce_all.py` — 410 literals, 183 corruptions, 13
      admitted logs.""",
     """      `python scripts/reproduce_all.py` — 417 literals, 198 corruptions, 13
      admitted logs."""),
    ("data-suite", "submission/data_availability.md",
     """`scripts/attack_verifier.py` is that checker's own regression
suite: 183 corruptions.""",
     """`scripts/attack_verifier.py` is that checker's own regression
suite: 198 corruptions."""),
]


def main(argv):
    check = "--check" in argv
    problems = []
    for name, rel, old, _new in EDITS:
        p = ROOT / rel
        n = p.read_text(encoding="utf-8").count(old) if p.exists() else -1
        if n != 1:
            problems.append(f"{name} ({rel}): anchor appears {n} times")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if check:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for name, rel, old, new in EDITS:
        p = ROOT / rel
        p.write_text(p.read_text(encoding="utf-8").replace(old, new, 1),
                     encoding="utf-8")
        print(f"  applied {name} -> {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

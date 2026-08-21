"""Refresh every count the documentation quotes, and report what it could not
find.

The counts move whenever the manuscript or the checker does, and every
round-sixteen file quoted at least one that had. Run this after any change,
read the report, and fix by hand anything it reports as not found.

    python scripts/refresh_counts.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

FIX = [
    ("README.md", "934 checks passed, 0 failed", "936 checks passed, 0 failed"),
    ("README.md", "198 caught, 0 missed, 0 skipped of 198",
     "199 caught, 0 missed, 0 skipped of 199"),
    ("README.md", "is its regression suite: 198\ncorruptions.",
     "is its regression suite: 199\ncorruptions."),
    ("REPRODUCE.md", "is the checker's regression suite: 198",
     "is the checker's regression suite: 199"),
    ("submission/cover_letter.md", "A second harness, a suite of 198",
     "A second harness, a suite of 199"),
    ("submission/cover_letter.md", "417 literals, 198 corruptions, 13",
     "417 literals, 199 corruptions, 13"),
    ("submission/data_availability.md", "suite: 198 corruptions.",
     "suite: 199 corruptions."),
    ("submission/OWNER-ACTIONS.md", "674 checks to 934, the corruption suite",
     "674 checks to 936, the corruption suite"),
    ("submission/DECISIONS.md", "The manuscript is 45 pages and nothing was cut",
     "The manuscript is 47 pages and nothing was cut"),
    ("submission/suggested_reviewers.md", "suite of 183 corruptions over that checker",
     "suite of 199 corruptions over that checker"),
    ("submission/suggested_reviewers.md", "recomputes 410 numeric literals",
     "recomputes 417 numeric literals"),
    ("HANDOFF.md", "the checker from 674 checks to 934, the\ncorruption suite from 149 to 198,",
     "the checker from 674 checks to 936, the\ncorruption suite from 149 to 199,"),
    ("HANDOFF.md", "The suite is 198 corruptions now, and it re-runs clean.",
     "The suite is 199 corruptions now."),
    ("PLAN-STRONG-ACCEPT.md", "**890 checks, 410 literals, 0 unaccounted, 401 compared against data.**",
     "**936 checks, 417 literals, 0 unaccounted, 405 compared against data.**"),
    ("PLAN-STRONG-ACCEPT.md", "149 " + chr(8594) + " 183.", "149 " + chr(8594) + " 199."),
    ("PLAN-STRONG-ACCEPT.md", "890 checks, 0 unaccounted; 183 corruptions.",
     "936 checks, 0 unaccounted; 199 corruptions."),
    ("PLAN-STRONG-ACCEPT.md", "410 literals, 183 corruptions, 13 admitted logs.",
     "417 literals, 199 corruptions, 13 admitted logs."),
    ("PLAN-STRONG-ACCEPT.md", "45 pages, 0 errors, 0 undefined references, 2 overfull hboxes.",
     "47 pages, 0 errors, 0 undefined references, 2 overfull hboxes."),
    ("PLAN-STRONG-ACCEPT.md", "verifies 410 literals and runs 183 corruptions.",
     "verifies 417 literals and runs 199 corruptions."),
    ("PLAN-STRONG-ACCEPT.md", "rewritten conclusion. 45 pages, 0 errors",
     "rewritten conclusion. 47 pages, 0 errors"),
    ("PLAN-STRONG-ACCEPT.md",
     "`verify_paper.py` from 674 checks to 890, 410 literals, 0 unaccounted.",
     "`verify_paper.py` from 674 checks to 936, 417 literals, 0 unaccounted."),
    ("PLAN-STRONG-ACCEPT.md", "`attack_verifier.py` from 149 corruptions to 183,",
     "`attack_verifier.py` from 149 corruptions to 199,"),
]


def main():
    done, miss = 0, []
    for rel, old, new in FIX:
        p = ROOT / rel
        s = p.read_text(encoding="utf-8")
        n = s.count(old)
        if n == 1:
            p.write_text(s.replace(old, new), encoding="utf-8")
            done += 1
        elif s.count(new) >= 1 and n == 0:
            done += 0          # already applied
        else:
            miss.append((rel, n, old[:60]))
    print(f"{done} applied")
    if miss:
        print("NOT FOUND -- fix these by hand:")
        for rel, n, frag in miss:
            print(f"  {rel}: {n} occurrences of {frag!r}")
    return 1 if miss else 0


if __name__ == "__main__":
    sys.exit(main())

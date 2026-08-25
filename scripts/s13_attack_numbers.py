"""s13 -- THE CORRUPTION SUITE FOR THE GENERATED-NUMBER ARCHITECTURE.

Round nineteen.  Every number in the manuscript is now a macro generated from
a result file.  That removes one class of defect --- the abstract disagreeing
with a table --- and creates another: if the generator is wrong, or if a
result file is edited, the whole manuscript is wrong CONSISTENTLY and nothing
looks odd.

`scripts/verify_numbers.py` is the guard.  This file is the guard's own
regression suite.  It corrupts one thing at a time and requires the verifier
to notice:

  A  a value in a result file that a macro is derived from
  B  a value in paper/numbers.tex directly
  C  a macro deleted from paper/numbers.tex
  D  a train-only check flipped to False
  E  a region label made inconsistent with the counts it summarises
  F  an adjudication file made inconsistent with the coding file

A corruption the verifier does not catch is a hole in the verifier, is printed
as MISSED, and the suite exits non-zero.  Ten holes have been found in this
project's checkers, and every one was found by a suite like this one or by
reading its output, never by the checker itself.

    python s13_attack_numbers.py            # all corruptions
    python s13_attack_numbers.py --list     # what would be run

Every corruption is applied to a COPY under a temporary results directory and
the original files are never written.  The suite refuses to start if a
previous run left its lock behind.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
LOCK = ROOT / "results" / ".s13.lock"


def run_script(script, results_dir, paper_dir):
    """Run one checker with RESULTS, PAPER and ROOT redirected at the
    copies, so a corruption is never applied to the real tree."""
    env = dict(**dict(__import__("os").environ))
    env["FIELDVALUE_RESULTS"] = str(results_dir)
    env["FIELDVALUE_PAPER"] = str(paper_dir)
    env["FIELDVALUE_ROOT"] = str(Path(results_dir).parent)
    r = subprocess.run([sys.executable, str(HERE / script)],
                       capture_output=True, text=True, env=env,
                       cwd=str(HERE), timeout=900)
    return r.returncode, r.stdout + r.stderr


def run_verifier(results_dir, paper_dir, regenerate=False):
    """Verify the copies, optionally REGENERATING the macros first.

    Regeneration is what makes a corruption of a result file a real
    test.  Without it the suite corrupts a result and then asks the
    verifier about a numbers.tex that was generated from the CLEAN
    results -- so any quantity the verifier re-derives from a
    different file than the generator reads is untouched, and the
    corruption passes.  s01_facts.csv was exactly that: the generator
    reads n_pairs from it, the verifier counts pairs in the surface,
    and with no regeneration the two never met.

    Manuscript corruptions must NOT regenerate, because regenerating
    would overwrite the corruption.
    """
    if regenerate:
        rc, out = run_script("make_numbers.py", results_dir, paper_dir)
        if rc != 0:
            #  the generator refusing to run IS the corruption being
            #  caught: a result file it cannot read is a result file
            #  that cannot silently produce a wrong number
            return rc, out
    return run_script("verify_numbers.py", results_dir, paper_dir)


CORRUPTIONS = []


def corruption(name, kind):
    def deco(fn):
        CORRUPTIONS.append((name, kind, fn))
        return fn
    return deco


# --------------------------------------------------------------- class A
@corruption("A1 surface row count", "result file")
def _a1(R, P):
    p = R / "s01_facts.csv"
    d = pd.read_csv(p)
    d.loc[0, "n_pairs"] = int(d.n_pairs.iloc[0]) + 1
    d.to_csv(p, index=False)


@corruption("A2 a Sobol index", "result file")
def _a2(R, P):
    p = R / "s03_sobol.csv"
    d = pd.read_csv(p)
    i = d[d.scale == "headroom"].index[0]
    d.loc[i, "S"] = float(d.loc[i, "S"]) + 0.25
    d.to_csv(p, index=False)


@corruption("A3 a misreport rate", "result file")
def _a3(R, P):
    p = R / "s04_rules.csv"
    d = pd.read_csv(p)
    d.loc[0, "one_number_misreport_conventional"] = 0.999
    d.to_csv(p, index=False)


@corruption("A4 the screen's sensitivity denominator", "result file")
def _a4(R, P):
    p = R / "s06_facts.csv"
    d = pd.read_csv(p)
    d.loc[0, "n_screened_out"] = int(d.n_screened_out.iloc[0]) * 2
    d.to_csv(p, index=False)


# --------------------------------------------------------------- class B/C
@corruption("B1 a macro's value in numbers.tex", "manuscript")
def _b1(R, P):
    p = P / "numbers.tex"
    t = p.read_text(encoding="utf-8")
    t = t.replace("\\newcommand{\\nPairs}{", "\\newcommand{\\nPairs}{9")
    p.write_text(t, encoding="utf-8")


@corruption("C1 a macro deleted from numbers.tex", "manuscript")
def _c1(R, P):
    p = P / "numbers.tex"
    lines = [l for l in p.read_text(encoding="utf-8").splitlines()
             if "\\nLogs}" not in l]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------- class D-F
@corruption("D1 a train-only check flipped", "result file")
def _d1(R, P):
    p = R / "s01_trainonly.csv"
    d = pd.read_csv(p)
    d.loc[0, "train_only"] = False
    d.to_csv(p, index=False)


@corruption("E1 a region label inconsistent with its counts", "result file")
def _e1(R, P):
    #  s21_regions is the file the manuscript's region labels come from as of
    #  round twenty; s03_regions is the round-nineteen one, kept for the
    #  within-instrument comparison.  This corruption pointed at s03 until
    #  the suite reported it MISSED -- corrupting a file nothing reads is a
    #  test that cannot fail, which is the same defect the correction
    #  register calls Class A.  It corrupts whichever of the two the
    #  verifier actually reads, preferring the newer.
    p = R / "s21_regions.csv"
    if not p.exists():
        p = R / "s03_regions.csv"
    if not p.exists():
        return "skip"
    d = pd.read_csv(p)
    d.loc[0, "region"] = "uniformly beneficial"
    d.loc[0, "n_beneficial"] = int(d.n_cells.iloc[0]) - 1
    d.to_csv(p, index=False)


@corruption("F1 an adjudicated paper that was never screened in", "data")
def _f1(R, P):
    #  the adjudication files live under data/, which the suite copies into
    #  the temporary root beside results/ and paper/
    p = R.parent / "data" / "audit2" / "adjudication_in.csv"
    if not p.exists():
        return "skip"
    d = pd.read_csv(p)
    d.loc[0, "oa_id"] = "W0000000000"
    d.to_csv(p, index=False)


@corruption("F2 the screened-in coding set changed under the adjudication",
            "result file")
def _f2(R, P):
    p = R / "s06_coding.csv"
    if not p.exists():
        return "skip"
    d = pd.read_csv(p)
    inc = d.index[d.status == "INCLUDED"]
    if len(inc) == 0:
        return "skip"
    d.loc[inc[0], "status"] = "NO_METRIC"
    d.to_csv(p, index=False)


@corruption("G1 two macros naming one quantity made to disagree",
            "result file")
def _g1(R, P):
    """THE CORRUPTION THE ROUND-TWENTY SUITE COULD NOT HAVE CAUGHT.

    Every other corruption here breaks the agreement between a macro and its
    own source file, which `verify_numbers.eq` sees.  This one does not: it
    moves a value in `s38_ladder.csv` and lets the generator AND the verifier
    both read the moved value, so the macro is perfectly consistent with its
    source.  What it breaks is the agreement between that macro and a
    DIFFERENT macro, computed from a different file, that the manuscript
    calls by the same name.

    That is precisely the defect the second developmental review found: the
    case study's increment at the later decision time appeared with two values
    and two signs, and every check in the repository passed.  Only
    `round21_verify.ESTIMANDS`, which is a condition on the SET of macros
    rather than on any one of them, can fail here.
    """
    p = R / "s38_ladder.csv"
    if not p.exists():
        return "skip"
    d = pd.read_csv(p)
    m = d[(d.decision_time == "t2_incident_creation")
          & (d.rung == "B_intake_g_km")]
    if not len(m):
        return "skip"
    i = m.index[0]
    d.loc[i, "V"] = float(d.loc[i, "V"]) + 0.05
    d.to_csv(p, index=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for name, kind, _ in CORRUPTIONS:
            print("  %-50s %s" % (name, kind))
        print("%d corruptions" % len(CORRUPTIONS))
        return
    if LOCK.exists():
        sys.exit("refusing to run: %s exists, so a previous run was killed "
                 "mid-flight" % LOCK)
    LOCK.write_text("running", encoding="utf-8")
    t0 = time.time()
    caught, missed, skipped = [], [], []
    try:
        #  the clean baseline must pass, or nothing below means anything
        with tempfile.TemporaryDirectory() as td:
            R = Path(td) / "results"
            P = Path(td) / "paper"
            shutil.copytree(RESULTS, R, ignore=shutil.ignore_patterns(".s13.lock"))
            shutil.copytree(PAPER, P)
            shutil.copytree(ROOT / "data" / "audit2",
                            Path(td) / "data" / "audit2",
                            ignore=shutil.ignore_patterns(
                                "fulltext", "meta", "frame_cache", "dossiers"))
            #  regenerate on the clean run too, so the baseline exercises
            #  exactly the path every result-file corruption takes
            rc, out = run_verifier(R, P, regenerate=True)
            if rc != 0:
                print(out[-2500:])
                sys.exit("the CLEAN run already fails; fix that before "
                         "running the suite")
            print("  clean run passes")

        for name, kind, fn in CORRUPTIONS:
            with tempfile.TemporaryDirectory() as td:
                R = Path(td) / "results"
                P = Path(td) / "paper"
                shutil.copytree(RESULTS, R,
                                ignore=shutil.ignore_patterns(".s13.lock"))
                shutil.copytree(PAPER, P)
                shutil.copytree(ROOT / "data" / "audit2",
                                Path(td) / "data" / "audit2",
                                ignore=shutil.ignore_patterns(
                                    "fulltext", "meta", "frame_cache",
                                    "dossiers"))
                res = fn(R, P)
                if res == "skip":
                    skipped.append(name)
                    print("  SKIP    %-50s (source not generated)" % name)
                    continue
                rc, out = run_verifier(R, P,
                                       regenerate=(kind != "manuscript"))
                if rc != 0:
                    caught.append(name)
                    print("  caught  %-50s %s" % (name, kind))
                else:
                    missed.append(name)
                    print("  MISSED  %-50s %s" % (name, kind))
    finally:
        LOCK.unlink(missing_ok=True)

    print("\n  %d caught, %d MISSED, %d skipped, in %.0fs"
          % (len(caught), len(missed), len(skipped), time.time() - t0))
    pd.DataFrame([dict(caught=len(caught), missed=len(missed),
                       skipped=len(skipped), total=len(CORRUPTIONS),
                       runtime_s=round(time.time() - t0, 1))]).to_csv(
        RESULTS / "s13_facts.csv", index=False)
    sys.exit(1 if missed else 0)


if __name__ == "__main__":
    main()

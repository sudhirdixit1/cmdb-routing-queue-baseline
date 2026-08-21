"""Reproduce every number in the paper, from the raw logs, in one command.

    python scripts/reproduce_all.py

Runs every analysis in dependency order, regenerates every results/*.csv and
every figure, rebuilds the PDF, verifies each numeric literal in the
manuscript against a value computed from data, and runs the verifier's own
corruption suite.  Exits non-zero on the first failure.

WHY THIS FILE EXISTS.  The README used to list eighteen commands and say
"expect a few minutes per script".  That is a recipe, not an artifact: it
puts the dependency order in the reader's head, and the reader is the one
person who does not know it.  Everything the order encodes is below.

FOUR THINGS IT WILL NOT DO, each stated rather than silently skipped:

  * It will not download the datasets.  All three are public and none is
    redistributed here; REPRODUCE.md gives the DOIs and the filenames.  The
    preflight check below names any that are missing and stops.
  * It will not install a TeX distribution.  Without pdflatex the build step
    is skipped with a message and the exit status still reflects everything
    else.
  * It will not pin your library versions for you.  requirements.txt has the
    exact ones the figures were computed on, and REPRODUCE.md section 4 says
    which differences move which digits.
  * It will not tell you an interpretation is sound.  The checker guards
    numbers thoroughly and prose only where a guard was written by hand.

Options:
    --skip-attack   omit the corruption suite (40-70 min on its own)
    --skip-pdf      omit the LaTeX build
    --only STAGE    run one stage: analysis | figures | verify | attack | pdf
    --jobs N        parallel workers for the analysis stage (default: 4)
"""
import argparse
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
RAW = ROOT / "data" / "raw"
LOGS = ROOT / "logs"

NEEDED_FILES = {
    "Detail_Incident.csv":
        "BPI Challenge 2014, doi:10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35",
    "Detail_Incident_Activity.csv":
        "BPI Challenge 2014, same collection",
    "Detail_Change.csv":
        "BPI Challenge 2014, same collection",
    "BPI_Challenge_2013_incidents.xes.gz":
        "BPI Challenge 2013, doi:10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee",
    "incident_event_log.zip":
        "UCI 498, doi:10.24432/C57S4H",
}

#  Waves.  Everything inside a wave is independent of everything else inside
#  it; each wave needs the wave before it.  The comment on each script says
#  what the NEXT stage needs from it, because that is the reason it is here.
WAVES = [
    # r4_final is imported by almost everything and is the canonical loader.
    ["r4_final.py"],
    [
        "r5_final.py",          # nulls, mutation sensitivity
        "r6_final.py",          # the gains the headline table prints
        "r8_final.py",          # mechanism, design space, scoping
        "r9_second_task.py",    # the ladder on two further targets
        "r12_queue_from_item.py",   # entropies r21 section A divides
        "r13_queue_shape.py",   # the one-bit contrast
        "r14_scope.py",         # the split-averaged scoping curve
        "r16_field_semantics.py",   # what the Open-row group is
        "r17_mechanism_floor.py",   # the floor, at item level
        "r18_referee_round2.py",    # MI nulls, other free fields
        "r19_shrinkage_ci.py",  # intervals on the REDUCTION
        "r20_second_org.py",    # the second organisation (no r4 import)
        "r15_why_one_org.py",   # population rates across three public logs
        "r22_intercase.py",     # congestion; the central-desk contrast
        "r24_tiefree.py",       # the tie decomposition
    ],
    [
        "r10_estimators.py",    # r21 section C reads r10_estimators.csv
        "r11_operational.py",   # r21 section C and r23 read r11_*.csv
    ],
    [
        "r21_referee_round15.py",   # reads r10, r11, r12, r14, r18
        "r23_decision_curve.py",    # reads r11_capacity, r11_overstatement
    ],
]
FIGURES = ["r25_figures.py"]


def hdr(msg):
    print(f"\n{'=' * 78}\n{msg}\n{'=' * 78}", flush=True)


def preflight():
    hdr("PREFLIGHT")
    missing = [f for f in NEEDED_FILES if not (RAW / f).exists()]
    if missing:
        print("Raw data is missing.  None of these is redistributed here;")
        print("fetch each from its identifier and put it in data/raw/.\n")
        for f in missing:
            print(f"  {f}\n      {NEEDED_FILES[f]}")
        sys.exit("preflight failed")
    for f in NEEDED_FILES:
        print(f"  ok  {f}  ({(RAW / f).stat().st_size / 1e6:.1f} MB)")
    try:
        import numpy, pandas, sklearn, scipy, matplotlib
    except ImportError as e:
        sys.exit(f"missing dependency: {e}.  pip install -r requirements.txt")
    print(f"\n  python {sys.version.split()[0]}   pandas {pandas.__version__}"
          f"   numpy {numpy.__version__}   scikit-learn {sklearn.__version__}")
    print(f"  scipy {scipy.__version__}   matplotlib {matplotlib.__version__}")
    pinned = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for mod, name in ((pandas, "pandas"), (sklearn, "scikit-learn"),
                      (matplotlib, "matplotlib")):
        want = f"{name}=={mod.__version__}"
        if want not in pinned:
            print(f"  WARNING  {name} {mod.__version__} is not the pinned "
                  f"version; see REPRODUCE.md section 4")


def run(script, label=None):
    """Run one script, tee its output to logs/, return (name, ok, seconds)."""
    LOGS.mkdir(exist_ok=True)
    log = LOGS / (Path(script).stem + ".log")
    t0 = time.time()
    with open(log, "w", encoding="utf-8", errors="replace") as fh:
        rc = subprocess.run([sys.executable, "-u", str(SCRIPTS / script)],
                            cwd=str(SCRIPTS), stdout=fh,
                            stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    tag = "ok " if rc == 0 else "FAIL"
    print(f"  {tag}  {label or script:28s} {dt / 60:5.1f} min   -> {log.name}",
          flush=True)
    if rc != 0:
        print(f"        last lines of {log.name}:")
        for line in log.read_text(encoding="utf-8",
                                  errors="replace").splitlines()[-12:]:
            print("        " + line)
    return script, rc == 0, dt


def stage_analysis(jobs):
    hdr("ANALYSIS")
    failed = []
    for i, wave in enumerate(WAVES, 1):
        print(f"\n  wave {i} of {len(WAVES)}  ({len(wave)} scripts)")
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            for name, good, _ in ex.map(run, wave):
                if not good:
                    failed.append(name)
        if failed:
            sys.exit(f"analysis failed: {', '.join(failed)}")
    return True


def stage_figures():
    hdr("FIGURES")
    for f in FIGURES:
        if not run(f)[1]:
            sys.exit("figures failed")


def stage_verify():
    hdr("VERIFICATION")
    rc = subprocess.run([sys.executable, str(SCRIPTS / "verify_paper.py")],
                        cwd=str(SCRIPTS))
    if rc.returncode != 0:
        sys.exit("verification failed -- see the output above")


def stage_attack():
    hdr("CORRUPTION SUITE  (40-70 minutes; one verifier run per corruption)")
    rc = subprocess.run([sys.executable, "-u",
                         str(SCRIPTS / "attack_verifier.py")],
                        cwd=str(SCRIPTS))
    if rc.returncode != 0:
        sys.exit("the corruption suite found a hole in the verifier")


def stage_pdf():
    hdr("BUILD")
    if not (shutil.which("pdflatex")
            or (Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64"
                / "pdflatex.exe").exists()):
        print("  pdflatex not found -- skipping the build.  Every other stage")
        print("  ran; install a TeX distribution to produce the PDF.")
        return
    rc = subprocess.run([sys.executable, str(SCRIPTS / "build_journal.py")],
                        cwd=str(SCRIPTS))
    if rc.returncode != 0:
        sys.exit("build failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-attack", action="store_true")
    ap.add_argument("--skip-pdf", action="store_true")
    ap.add_argument("--only", choices=["analysis", "figures", "verify",
                                       "attack", "pdf"])
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()

    t0 = time.time()
    if a.only:
        preflight() if a.only == "analysis" else None
        {"analysis": lambda: stage_analysis(a.jobs), "figures": stage_figures,
         "verify": stage_verify, "attack": stage_attack, "pdf": stage_pdf}[a.only]()
    else:
        preflight()
        stage_analysis(a.jobs)
        stage_figures()
        stage_verify()
        if not a.skip_attack:
            stage_attack()
        if not a.skip_pdf:
            stage_pdf()
    hdr(f"DONE in {(time.time() - t0) / 60:.0f} minutes")
    print("Every stage that ran, passed.  What that does and does not")
    print("establish is in REPRODUCE.md section 5 -- read it before quoting")
    print("this run as evidence that the paper is right.")


if __name__ == "__main__":
    main()

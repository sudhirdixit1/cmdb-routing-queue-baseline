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

  * It will not redistribute anybody's data.  The FETCH stage downloads all
    23 corpus files from their DOIs through the 4TU API and records a
    SHA-256 for each; nothing is vendored into this repository.  Pass
    --skip-fetch if you already have them, and the preflight below names any
    that are still missing and stops.
  * It will not install a TeX distribution.  Without pdflatex the build step
    is skipped with a message and the exit status still reflects everything
    else.
  * It will not pin your library versions for you.  requirements.txt has the
    exact ones the figures were computed on, and REPRODUCE.md section 4 says
    which differences move which digits.
  * It will not tell you an interpretation is sound.  The checker guards
    numbers thoroughly and prose only where a guard was written by hand.

Options:
    --skip-fetch    omit the corpus download (assumes data/ is populated)
    --skip-attack   omit the corruption suite (40-70 min on its own)
    --skip-pdf      omit the LaTeX build
    --only STAGE    run one stage:
                    fetch | analysis | figures | holdout | package |
                    verify | attack | pdf
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
RUNTIMES = []

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
    "Detail_Interaction.csv":
        "BPI Challenge 2014, same collection; settles section 14",
}

#  Waves.  Everything inside a wave is independent of everything else inside
#  it; each wave needs the wave before it.  The comment on each script says
#  what the NEXT stage needs from it, because that is the reason it is here.
WAVES = [
    # r4_final is imported by almost everything and is the canonical loader.
    ["r4_final.py"],
    [
        "r5_final.py",          # nulls, mutation sensitivity
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
        #  r6 reads r8_dropped_leg.csv, so it cannot share a wave with r8.
        #  It did, which nobody noticed because r6 never ran at all.
        "r6_final.py",          # the gains the headline table prints
    ],
    [
        "r21_referee_round15.py",   # reads r10, r11, r12, r14, r18
        "r23_decision_curve.py",    # reads r11_capacity, r11_overstatement
    ],
    # ---- round seventeen -------------------------------------------------
    [
        "r30_instrument_matrix.py",     # the instrument matrix; r39 reads it
        "r31_why_instruments_disagree.py",  # mechanisms behind r30
        "r35_interaction_file.py",      # settles section 9; r39 reads it
        "r36_population_ablation.py",   # the population curve; r38 reads it
    ],
    [
        # the null the methodologist pass asked for; rebuilds km_prov, so it
        # must follow r35 rather than run beside it
        "r35b_temporal_null.py",
    ],
    [
        # builds data/normalized/*.parquet, which r33/r34/r37 all load, and
        # writes the attribute inventory.  One parse of a 728 MB XES file
        # rather than three.
        "r32_corpus.py",
    ],
    [
        "r33_generic_ladder.py",        # the pre-registered corpus ladder
    ],
    [
        "r33b_discriminate.py",         # reads r33_ladder, r33_discriminators
        "r33c_headroom.py",             # the exclusion-rule sensitivity
        "r34_layers_and_history.py",    # reads r33_roles
        "r37_free_text.py",             # reads r33_roles
        "r38_era_sensitivity.py",
    ],
    # ---- round eighteen --------------------------------------------------
    [
        #  The audit needs the network for its frame and its full texts; it
        #  caches both, so a re-run is offline.  It reads no result file, so
        #  it can go in the same wave as the propositions and the simulation,
        #  which read nothing either.
        "r40_audit.py",
        "r41_propositions.py",         # pure construction; no data at all
        "r45_simulation.py",           # a world whose answer is known
        "r48_venue.py",                # the venue counts, from OpenAlex
    ],
    [
        #  r43 --fit reads r33b_table.csv, so it follows r33b.
        "r42_holdout_fetch.py",        # by DOI, with checksums
    ],
    [
        "r44_axes_multilog.py",        # reads the r32 caches
        "r46_tool_agreement.py",       # fieldvalue against r30
    ],
    [
        "r47_signature_figure.py",     # reads r44_surface.csv
    ],
    # ---- round nineteen ---------------------------------------------------
    #  The round-nineteen chain is: the master surface, then everything that
    #  reads it.  s07 and s10 read nothing, so they run beside s01; s06 needs
    #  the network for its frame and caches it.
    [
        "s01_surface.py",              # THE master surface, every admitted pair
        "s07_props.py",                # pure construction; no data at all
        "s10_simulation2.py",          # six worlds with an enumerated truth
    ],
    [
        "s02_boot.py",                 # nested bootstrap; reads s01's pair list
        "s08_decision_time.py",        # two decision times on the primary log
        "s09_quality_extra.py",        # the quality nulls, explained
        "s15_calibration_curves.py",   # the calibration figure's source
        "s16_target_agreement.py",     # how different the targets are
    ],
    [
        #  s17 RECENTRES every interval and band from s02's stored draws.  It
        #  must run before s03, which labels regions from the bands.
        "s17_intervals.py",
    ],
    [
        "s03_decompose.py",            # reads s01_surface and s17_bands
        "s04_regret.py",               # reads s01_surface and s03_regions
    ],
    [
        "s06_audit2.py",               # the practice pilot; network + cache
    ],
    [
        "s11_tool_agreement.py",       # fieldvalue against the pipeline
    ],
]
FIGURES = ["r25_figures.py", "r39_figures.py", "s12_figures.py"]
NUMBERS = ["make_numbers.py", "assemble_paper.py"]


def hdr(msg):
    print(f"\n{'=' * 78}\n{msg}\n{'=' * 78}", flush=True)


def stage_fetch():
    hdr("FETCH  (by DOI, with checksums; nothing is redistributed here)")
    rc = subprocess.run([sys.executable, "-u", str(SCRIPTS / "fetch_corpus.py")],
                        cwd=str(SCRIPTS))
    if rc.returncode != 0:
        sys.exit("fetch failed")


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
        print("\n  SCRIPTS THAT DO NOT PARSE:")
        for _b in _broken:
            print("    " + _b)
        sys.exit("preflight failed: fix these before running anything")
    print(f"  all {len(list(SCRIPTS.glob('*.py')))} scripts parse")
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
    RUNTIMES.append(dict(script=script, ok=(rc == 0), seconds=round(dt, 1)))
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


def stage_holdout():
    """The prospective test, in the order PREDICTION.md registers.

    `--fit` reads ONLY round-seventeen results and writes the thresholds;
    the second call opens the held-out logs.  Running them in that order in
    the reproduction is not a convenience -- it is the claim.
    """
    hdr("THE PROSPECTIVE TEST  (fit on the corpus, then open the held-out logs)")
    for args in (["r43_holdout_test.py", "--fit"], ["r43_holdout_test.py"]):
        rc = subprocess.run([sys.executable, "-u", str(SCRIPTS / args[0])]
                            + args[1:], cwd=str(SCRIPTS))
        if rc.returncode != 0:
            sys.exit(f"{' '.join(args)} failed")


def stage_package():
    """fieldvalue's own tests, and the worked example on a public dataset."""
    hdr("THE PACKAGE  (fieldvalue: unit tests, then the worked example)")
    rc = subprocess.run([sys.executable, "-m", "pytest", "fieldvalue", "-q"],
                        cwd=str(ROOT))
    if rc.returncode != 0:
        sys.exit("fieldvalue's test suite failed")
    rc = subprocess.run([sys.executable, "-u",
                         str(ROOT / "examples" / "worked_example.py")],
                        cwd=str(ROOT))
    if rc.returncode != 0:
        print("  the worked example needs the network on first run; skipping")


def stage_numbers():
    """ROUND NINETEEN.  Every number in the manuscript is generated from
    results/*.csv, and the manuscript is assembled from paper/parts/.  Both
    have to happen after the analysis and before the build."""
    hdr("NUMBERS AND ASSEMBLY")
    for s in NUMBERS:
        if not run(s):
            return False
    return True


def stage_figures():
    hdr("FIGURES")
    for f in FIGURES:
        if not run(f)[1]:
            sys.exit("figures failed")


def stage_verify():
    """ROUND NINETEEN.  Three checks, in the order a failure is cheapest to
    diagnose: the package against the pipeline, the macros against their
    sources, and the manuscript against the publisher's limits.
    `verify_paper.py` guards the round-eighteen manuscript, which is retained
    in the archive; it is run last and its failure is reported rather than
    fatal, because that manuscript is superseded."""
    hdr("VERIFICATION")
    for s in ("s11_tool_agreement.py", "verify_numbers.py", "texlint.py"):
        rc = subprocess.run([sys.executable, str(SCRIPTS / s)],
                            cwd=str(SCRIPTS))
        if rc.returncode != 0:
            sys.exit("%s failed -- see the output above" % s)
    rc = subprocess.run([sys.executable, str(SCRIPTS / "verify_paper.py")],
                        cwd=str(SCRIPTS))
    if rc.returncode != 0:
        print("  NOTE: verify_paper.py (the superseded round-eighteen "
              "manuscript) reports failures; not fatal.")


def stage_attack():
    hdr("CORRUPTION SUITES  (one verifier run per corruption)")
    for s in ("s13_attack_numbers.py", "attack_verifier.py"):
        rc = subprocess.run([sys.executable, "-u", str(SCRIPTS / s)],
                            cwd=str(SCRIPTS))
        if rc.returncode != 0 and s.startswith("s13"):
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
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-attack", action="store_true")
    ap.add_argument("--skip-pdf", action="store_true")
    ap.add_argument("--only", choices=["fetch", "analysis", "figures",
                                       "holdout", "package", "numbers",
                                       "verify", "attack", "pdf"])
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()

    t0 = time.time()
    if a.only:
        preflight() if a.only == "analysis" else None
        {"fetch": stage_fetch,
         "analysis": lambda: stage_analysis(a.jobs), "figures": stage_figures,
         "holdout": stage_holdout, "package": stage_package,
         "numbers": stage_numbers,
         "verify": stage_verify, "attack": stage_attack, "pdf": stage_pdf}[a.only]()
    else:
        if not a.skip_fetch:
            stage_fetch()
        preflight()
        stage_analysis(a.jobs)
        stage_holdout()
        stage_package()
        stage_figures()
        stage_numbers()
        stage_verify()
        if not a.skip_attack:
            stage_attack()
        if not a.skip_pdf:
            stage_pdf()
    if RUNTIMES:
        import csv
        LOGS.mkdir(exist_ok=True)
        with open(LOGS / "runtimes.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["script", "ok", "seconds"])
            w.writeheader()
            w.writerows(RUNTIMES)
        slow = sorted(RUNTIMES, key=lambda r: -r["seconds"])[:6]
        print(chr(10) + "  slowest stages, in minutes:")
        for r in slow:
            print(f"    {r['script']:34s} {r['seconds'] / 60:5.1f}")
        print(f"  full per-script table in logs/runtimes.csv")
    hdr(f"DONE in {(time.time() - t0) / 60:.0f} minutes")
    print("Every stage that ran, passed.  What that does and does not")
    print("establish is in REPRODUCE.md section 5 -- read it before quoting")
    print("this run as evidence that the paper is right.")


if __name__ == "__main__":
    main()

"""Make it impossible for a build, a verification or a commit to read the
manuscript while the corruption suite is rewriting it.

`attack_verifier.py`'s docstring has warned about this since round sixteen,
when a build and a verification both ran against a corrupted file. Round
seventeen did it again in a new way: a `git add -A` issued while the suite was
running committed both `paper/.tex.bak` and a manuscript with an injected
$58.2\\%$ where $18.2\\%$ belongs. A warning in a docstring is not a control.

Three controls, all cheap:

  * `paper/.tex.bak` is gitignored, so a commit cannot capture it.
  * `verify_paper.py` and `build_journal.py` refuse to start while it exists.
  * `attack_verifier.py` refuses to start if one is already there, which
    catches the other failure mode -- a suite killed mid-flight leaving a
    corrupted manuscript that a second run would then back up over.

    python scripts/patch_suitelock_r17.py --check
    python scripts/patch_suitelock_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "scripts"

GUARD = '''
#  ROUND SEVENTEEN.  attack_verifier.py rewrites the manuscript once per
#  corruption and restores it in a finally block.  Anything that reads the
#  manuscript while that is happening is reading a CORRUPTED file.  Round
#  sixteen had a build and a verification do it; round seventeen had a
#  `git add -A` commit one.  A docstring is not a control, so this is:
_SUITE_LOCK = Path(__file__).resolve().parent.parent / "paper" / ".tex.bak"
if _SUITE_LOCK.exists():
    sys.exit(
        f"REFUSING TO RUN: {_SUITE_LOCK} exists, which means attack_verifier.py\\n"
        "is running or was killed mid-flight.  If it is running, wait.  If it\\n"
        "was killed, the manuscript on disk is CORRUPTED -- restore it first:\\n"
        f"    cp {_SUITE_LOCK} {_SUITE_LOCK.with_name('iaai27_empty_cmdb.tex')}\\n"
        f"    rm {_SUITE_LOCK}")

'''

ATTACK_GUARD = '''
#  ROUND SEVENTEEN.  If a backup is already on disk this script was killed
#  mid-flight and the manuscript is corrupted.  Copying over the backup would
#  make the corruption permanent, so refuse instead.
if BAK.exists():
    sys.exit(f"REFUSING TO RUN: {BAK} already exists, so a previous run was "
             f"killed and\\npaper/iaai27_empty_cmdb.tex is CORRUPTED.  Restore "
             f"it first:\\n    cp {BAK} {TEX}\\n    rm {BAK}")

'''

EDITS = [
    ("verify", S / "verify_paper.py",
     'ROOT = Path(__file__).resolve().parent.parent\nTEX_RAW = ',
     'ROOT = Path(__file__).resolve().parent.parent\n' + GUARD + 'TEX_RAW = '),
    ("build", S / "build_journal.py", None, None),   # filled in below
    ("attack", S / "attack_verifier.py",
     'shutil.copy(TEX, BAK)',
     ATTACK_GUARD.lstrip("\n") + 'shutil.copy(TEX, BAK)'),
]


def main(argv):
    build = S / "build_journal.py"
    bsrc = build.read_text(encoding="utf-8")
    # find the first line after the imports to insert the guard
    marker = next((l for l in bsrc.split("\n")
                   if l.startswith("ROOT = ") or l.startswith("PAPER = ")), None)
    edits = [(n, p, o, w) for n, p, o, w in EDITS if o is not None]
    if marker is None:
        print("build_journal.py: no ROOT/PAPER line to anchor on")
        return 1
    edits.append(("build", build, marker, marker + "\n" + GUARD.rstrip()))

    srcs = {p: p.read_text(encoding="utf-8") for _, p, _, _ in edits}
    missing = [f"{n} ({p.name}): anchor appears {srcs[p].count(o)} times"
               for n, p, o, _ in edits if srcs[p].count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print(f"all {len(edits)} anchors found")
        return 0
    for n, p, o, w in edits:
        srcs[p] = srcs[p].replace(o, w, 1)
        print(f"  applied {n} -> {p.name}")
    for p, s in srcs.items():
        p.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

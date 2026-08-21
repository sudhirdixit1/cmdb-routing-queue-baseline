"""Prove the purity guard in verify_paper.py fires.

Injects a deliberate side effect on the manuscript ABOVE the guard, runs the
checker, and restores both files. Nothing is left changed.

    python scripts/_purity_test.py
"""
import pathlib
import shutil
import subprocess
import sys

S = pathlib.Path(__file__).resolve().parent
V = S / "verify_paper.py"
TEX = S.parent / "paper" / "iaai27_empty_cmdb.tex"
VB, TB = S / ".purity_v.bak", S / ".purity_tex.bak"

shutil.copy(V, VB)
shutil.copy(TEX, TB)
try:
    src = V.read_text(encoding="utf-8")
    marker = "\n_lint_check_order()\n_run_guard_lint()\n_run_census()\n"
    assert src.count(marker) == 1, f"call block found {src.count(marker)} times"
    inject = ("\n_TEX_PATH.write_text(TEX_RAW + chr(10) + '% side effect'"
              " + chr(10), encoding='utf-8')" + marker)
    V.write_text(src.replace(marker, inject, 1), encoding="utf-8")

    r = subprocess.run([sys.executable, str(V)], capture_output=True, text=True)
    out = r.stdout + r.stderr
    fired = "THE CHECKER MODIFIED THE MANUSCRIPT" in out
    print("guard fired:", fired)
    print("exit code:", r.returncode)
    for line in out.splitlines():
        if "MODIFIED" in line or "checks passed" in line:
            print("   ", line.strip())
finally:
    shutil.copy(VB, V)
    shutil.copy(TB, TEX)
    VB.unlink()
    TB.unlink()
    print("restored")

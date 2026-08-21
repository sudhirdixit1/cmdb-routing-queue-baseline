"""The checker must not modify the thing it is checking.

A check added late in round seventeen read the corruption suite's size with
`import attack_verifier`. `attack_verifier.py` is a script, so importing it
RAN it: every invocation of the checker became a 199-corruption run, and every
one of those corruptions then reported "caught" only because the nested
checker refused to start while the lock file existed. A clean 199/199 was
produced by a checker that had checked nothing.

That is worse than any hole the suite has found, because it makes the whole
apparatus report success by construction. The specific cause is fixed -- the
list is parsed, not imported -- and this adds the general guard: the checker
records the manuscript's SHA-256 before it reads anything and asserts it is
unchanged before it reports. Any future side effect on the manuscript, from
any source, fails loudly instead of passing silently.

    python scripts/patch_purity_r17.py --check
    python scripts/patch_purity_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "scripts" / "verify_paper.py"

HEAD_OLD = "TEX_RAW = (ROOT / \"paper\" / \"iaai27_empty_cmdb.tex\").read_text(encoding=\"utf-8\")"
HEAD_NEW = '''_TEX_PATH = ROOT / "paper" / "iaai27_empty_cmdb.tex"
#  ROUND SEVENTEEN.  The checker must not modify the thing it is checking.
#  A check that read the corruption suite's size with `import
#  attack_verifier` RAN the suite -- attack_verifier.py is a script -- so
#  every invocation of this file became a 199-corruption run in which every
#  corruption "passed" because the nested checker refused to start.  A clean
#  199/199 from a checker that had checked nothing.  The specific cause is
#  fixed; this is the general guard.
import hashlib as _hashlib
_TEX_SHA_AT_START = _hashlib.sha256(_TEX_PATH.read_bytes()).hexdigest()
TEX_RAW = _TEX_PATH.read_text(encoding="utf-8")'''

TAIL_OLD = '''unaccounted = sorted(l for l in LITS if l not in STRUCTURAL and l not in seen)'''
TAIL_NEW = '''#  ROUND SEVENTEEN.  Purity check: nothing this file did may have touched the
#  manuscript.  See the note beside _TEX_SHA_AT_START.
if _hashlib.sha256(_TEX_PATH.read_bytes()).hexdigest() != _TEX_SHA_AT_START:
    bad.append("THE CHECKER MODIFIED THE MANUSCRIPT WHILE CHECKING IT. "
               "Every result below is meaningless.  Something this file "
               "imports has a side effect on paper/iaai27_empty_cmdb.tex; "
               "find it before trusting anything.")
else:
    ok += 1

unaccounted = sorted(l for l in LITS if l not in STRUCTURAL and l not in seen)'''


def main(argv):
    s = V.read_text(encoding="utf-8")
    pairs = [("head", HEAD_OLD, HEAD_NEW), ("tail", TAIL_OLD, TAIL_NEW)]
    missing = [f"{n}: anchor appears {s.count(o)} times"
               for n, o, _ in pairs if s.count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print("both anchors found")
        return 0
    for n, o, w in pairs:
        s = s.replace(o, w, 1)
        print(f"  applied {n}")
    V.write_text(s, encoding="utf-8")
    print(f"wrote {V}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""The guard lint had the same ordering bug as the coverage census.

Round seventeen moved the census to the end of `verify_paper.py` and added
`_lint_check_order()` so it could not be outrun again. The guard-or-declare
lint sat ABOVE that, so the two `ck_phrase` pins added in the referee pass
were registered after the lint had already run and their sentences were still
reported unguarded.

That is the third instance of one bug: a consumer of `guarded_phrases` or
`covered_spans` placed above the producers. The fix is the same shape as the
census fix and is applied to the lint too -- it becomes a function, it is
called from the same late block, and `_lint_check_order()` now names both.

Three real defects are repaired alongside it:

  * Section 3 illustrated the metric-relativity point with "$60.3\\%$ under
    Brier skill". $60.3\\%$ is average PRECISION; Brier skill is $58.4\\%$.
    The checker caught it because the value and the instrument named beside
    it disagreed.
  * The congestion-adjusted reduction was recomputed as a ratio of point
    estimates, $45.3\\%$, where the paper prints the bootstrap median the
    rest of the paper uses, $45.7\\%$. The check now reads the same column
    the original check reads.
  * The conclusion's practitioner sentence restates $+0.183$ and had no
    check at that occurrence.

    python scripts/patch_guardorder_r17.py --check
    python scripts/patch_guardorder_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"
V = ROOT / "scripts" / "verify_paper.py"

TEX_OLD = (r"""claim $R$ is comparable across $m$; Section~\ref{sec:metric} reports the
spread across $m$ as the finding.""")
TEX_NEW = (r"""claim $R$ is comparable across $m$; Section~\ref{sec:metric} reports the
spread across $m$ as the finding.""")

FIXES = [
    # the instrument named beside 60.3 was the wrong one
    ("brier-to-ap", TEX,
     r"""ratio needs, so ``$43.7\%$ of the value is absorbed'' under AUC and
``$60.3\%$'' under Brier skill are not one quantity measured twice.""",
     r"""ratio needs, so ``$43.7\%$ of the value is absorbed'' under AUC and
``$60.3\%$'' under average precision are not one quantity measured twice."""),
    # the check must read the column the paper's number comes from
    ("congestion-source", V,
     '''ck("corpus congestion to",
   100 * (1 - float(_r22L.iloc[3].gain) / float(_r22L.iloc[1].gain)), "45.7",
   0.06, anchor="move the primary log's reduction from")''',
     '''#  r22C.red_both is the bootstrap median the rest of the paper quotes; the
#  ratio of the two point estimates is 45.3 and is a different quantity.
ck("corpus congestion to", r22C.red_both, "45.7", 0.06,
   anchor="move the primary log's reduction from")'''),
    ("brier-check", V,
     '''ck("estimand brier example", _BS.reduction * 100, "60.3", 0.06,
   anchor="under Brier skill are not one quantity")''',
     '''ck("estimand ap example", _AP.reduction * 100, "60.3", 0.06,
   anchor="under average precision are not one quantity")
ck("buyer sentence rung 0", _A0, "+0.183", 6e-4,
   anchor="a business case built on")'''),
]

GUARD_FN_OLD = """_sentences = [x.strip() for x in re.split(r"(?<=[.;])\\s+", FLAT) if x.strip()]"""
GUARD_FN_NEW = """def _run_guard_lint():
    #  ROUND SEVENTEEN, third instance of one bug.  This lint consumes
    #  `guarded_phrases`, so like the coverage census it must run after every
    #  producer.  It did not: two ck_phrase pins added in the referee pass
    #  were registered below it and their sentences were still reported
    #  unguarded.  It is a function now and is called from the same late
    #  block as the census; _lint_check_order() names both call sites.
    _sentences = [x.strip() for x in re.split(r"(?<=[.;])\\s+", FLAT) if x.strip()]"""


def main(argv):
    check = "--check" in argv
    srcs = {TEX: TEX.read_text(encoding="utf-8"), V: V.read_text(encoding="utf-8")}
    problems = [f"{n}: anchor appears {srcs[p].count(o)} times"
                for n, p, o, _ in FIXES if srcs[p].count(o) != 1]
    if srcs[V].count(GUARD_FN_OLD) != 1:
        problems.append("guard lint body not found")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if check:
        print(f"all {len(FIXES)} anchors and the guard-lint body found")
        return 0

    for n, p, o, w in FIXES:
        srcs[p] = srcs[p].replace(o, w, 1)
        print(f"  applied {n} -> {p.name}")

    v = srcs[V]
    # 1. wrap the lint body in a function and indent it
    start = v.index(GUARD_FN_OLD)
    end = v.index('unaccounted = sorted(l for l in LITS')
    # the lint body runs from _sentences up to the census call block
    tail_marker = "\n_lint_check_order()\n_run_census()\n"
    ti = v.index(tail_marker)
    body = v[start:ti]
    indented = "\n".join(("    " + l if l.strip() else l)
                         for l in body.rstrip().split("\n"))
    v = (v[:start] + GUARD_FN_NEW.split("\n", 0)[0] + "\n"
         + "\n".join(GUARD_FN_NEW.split("\n")[:-1]) + "\n" + indented
         + "\n\n" + v[ti:])
    # 2. call it from the late block, and lint both call sites
    v = v.replace("\n_lint_check_order()\n_run_census()\n",
                  "\n_lint_check_order()\n_run_guard_lint()\n_run_census()\n", 1)
    v = v.replace('''    try:
        at = next(i for i, l in enumerate(src)
                  if l.startswith("_run_census()"))
    except StopIteration:
        bad.append("the coverage census is never called")
        return''',
                  '''    try:
        at = min(i for i, l in enumerate(src)
                 if l.startswith(("_run_census()", "_run_guard_lint()")))
    except ValueError:
        bad.append("the coverage census or the guard lint is never called")
        return''')
    V.write_text(v, encoding="utf-8")
    TEX.write_text(srcs[TEX], encoding="utf-8")
    print("  guard lint moved into a function called from the late block")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

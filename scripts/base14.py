"""r4_final's cohort, without r4_final's analyses.

`r4_final.py` is a script, not a library: importing it re-runs every bootstrap
it contains (~90 s wall clock) before the caller sees a single row.  Round
seventeen adds nine scripts that all need the same cohort, so that overhead
would be paid nine times for nothing.

This module executes `r4_final.py`'s own source, verbatim, up to and including
the line that builds the cohort, and stops there.  The loader, the cutoff, the
split fraction, the intake block, the estimator and the seed are therefore not
re-implemented here -- they are the same characters in the same file.  If
`r4_final.py` changes, this changes with it.

`selftest()` imports the real module and asserts the frames, the split and the
fitted scores are identical.  Run it with `python base14.py`.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

_SRC = (HERE / "r4_final.py").read_text(encoding="utf-8")
_STOP = "D, counts, ACT, OPEN = load()"
if _SRC.count(_STOP) != 1:
    raise RuntimeError(
        "r4_final.py no longer contains exactly one cohort-construction line "
        f"{_STOP!r}; base14.py must be re-pointed before it is trusted.")
_PREFIX = _SRC.split(_STOP)[0] + _STOP + "\n"

_NS = {"__name__": "r4_final_prefix", "__file__": str(HERE / "r4_final.py")}
exec(compile(_PREFIX, str(HERE / "r4_final.py"), "exec"), _NS)

# --- the cohort, and the pieces every round-seventeen script needs -----------
D = _NS["D"]
ACT = _NS["ACT"]
OPEN = _NS["OPEN"]
counts = _NS["counts"]
TR, TE = _NS["split"](D)
y = TE._y.values

SEED = _NS["SEED"]
N_BOOT = _NS["N_BOOT"]
CUTOFF = _NS["CUTOFF"]
INTAKE = _NS["INTAKE"]
IDENT = _NS["IDENT"]
CLASSES = _NS["CLASSES"]
Q = "intake_group"
BQ = INTAKE + [Q]

fit = _NS["fit"]
split = _NS["split"]
bdelta = _NS["bdelta"]
load = _NS["load"]


def selftest() -> None:
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        import r4_final as M
    assert D.shape == M.D.shape, (D.shape, M.D.shape)
    assert list(D.columns) == list(M.D.columns)
    assert (D["Incident ID"].values == M.D["Incident ID"].values).all()
    assert (D._y.values == M.D._y.values).all()
    assert TR.shape == M.TR.shape and TE.shape == M.TE.shape
    assert (y == M.y).all()
    assert INTAKE == M.INTAKE and IDENT == M.IDENT and SEED == M.SEED
    p_here = fit(TR, TE, INTAKE + [IDENT])
    p_there = M.fit(M.TR, M.TE, M.INTAKE + [M.IDENT])
    assert np.allclose(p_here, p_there), "estimator diverged"
    print(f"base14 selftest OK: D={D.shape} TR={TR.shape} TE={TE.shape} "
          f"prev={y.mean():.6f}")


if __name__ == "__main__":
    selftest()

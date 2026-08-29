"""attack_reproduction -- THE REPRODUCTION GATE'S OWN REGRESSION SUITE.

Rule 5 of this project: write the corruption before you believe the check.
`check_reproduction.py` exists because no gate in this repository had ever
re-run an analysis, and a gate written to catch that failure is worth exactly
as much as its ability to fail.  This file breaks one thing at a time and
asserts that the intended condition fires.

Each case patches the pipeline in memory -- no file in the repository is
touched -- runs the gate, and requires a failure whose text begins with the
condition that should have caught it.  The baseline case requires the
opposite: with nothing broken, the gate must pass.

  baseline                        nothing broken            -> 0 failures
  the logistic learner perturbed  C = 0.999, not 1.0        -> condition 2b
  the boosting learner perturbed  199 iterations, not 200   -> condition 2a
  the split moved                 train fraction 0.69       -> condition 1
  the boosting learner made nondeterministic                -> condition 4
  REPRODUCE.md's table edited away from the gate            -> condition 6

Two of these are worth a note.  The boosting perturbation is caught by
condition 2a rather than by a tolerance, because the low-cardinality rungs
are the only place the boosting learner reproduces across machines and
therefore the only place it can be held tightly -- which is the whole reason
that condition is phrased by rung and not by arm.  And the doctored
`REPRODUCE.md` is the case that matters most in practice: the tolerances in
§5.1 are wide, so the temptation to widen them further when something fails
is real, and condition 6 makes that edit fail loudly instead of quietly.

    python scripts/attack_reproduction.py

About four minutes: six runs of the gate's cheap arm.  Exit status is
non-zero if any corruption goes unnoticed, or if the baseline does not pass.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import contextlib  # noqa: E402
import io  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import spec as S  # noqa: E402
import check_reproduction as R  # noqa: E402

ORIG_LEARNERS = dict(S.LEARNERS)
ORIG_FRAC = S.TRAIN_FRAC
ORIG_ROOT = R.ROOT
import sklearn.ensemble as E  # noqa: E402
ORIG_HGB = E.HistGradientBoostingClassifier

CASES = []


def case(name, want):
    def deco(fn):
        CASES.append((name, want, fn))
        return fn
    return deco


@case("baseline, nothing broken", None)
def _c0():
    pass


@case("the logistic learner is perturbed (C=0.999, not 1.0)", "condition 2b")
def _c1():
    S.LEARNERS["logit"] = (
        lambda tr, te, c, y, s, w=None:
        S._onehot_logit(tr, te, c, y, s, C_=0.999, w=w))


@case("the boosting learner is perturbed (199 iterations, not 200)",
      "condition 2a")
def _c2():
    def fake(*a, **k):
        k["max_iter"] = 199
        return ORIG_HGB(*a, **k)
    E.HistGradientBoostingClassifier = fake


@case("the split moves (train fraction 0.69, not 0.70)", "condition 1")
def _c3():
    S.TRAIN_FRAC = 0.69


@case("the boosting learner is made nondeterministic", "condition 4")
def _c4():
    base = ORIG_LEARNERS["hgb"]
    S.LEARNERS["hgb"] = (
        lambda tr, te, c, y, s, w=None:
        base(tr, te, c, y, s, w=w) + np.random.default_rng().normal(0, 1e-9))


@case("REPRODUCE.md's tolerance table is edited away from the gate",
      "condition 6")
def _c5():
    d = Path(tempfile.mkdtemp(prefix="attack_reproduction_"))
    txt = (ROOT / "REPRODUCE.md").read_text(encoding="utf-8")
    doctored = txt.replace("| 0.851086 | 0.90 |", "| 0.851086 | 0.99 |")
    if doctored == txt:
        raise SystemExit(
            "attack_reproduction: could not find the boosting/smooth row in "
            "REPRODUCE.md to doctor; the tolerance table's format changed and "
            "this case is no longer testing anything")
    (d / "REPRODUCE.md").write_text(doctored, encoding="utf-8")
    R.ROOT = d


def _restore():
    S.LEARNERS.clear()
    S.LEARNERS.update(ORIG_LEARNERS)
    S.TRAIN_FRAC = ORIG_FRAC
    R.ROOT = ORIG_ROOT
    E.HistGradientBoostingClassifier = ORIG_HGB


def main():
    bad = []
    for name, want, fn in CASES:
        _restore()
        fn()
        R.FAILS = []
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = R.main([])
        fails = list(R.FAILS)
        if want is None:
            ok = (rc == 0 and not fails)
            print("  %-58s %s" % (name, "passes, 0 failures" if ok else
                                  "BROKEN: %s" % (fails[:1] or "rc=%s" % rc)))
        else:
            hit = [f for f in fails if f.startswith(want)]
            ok = bool(hit) and rc != 0
            print("  %-58s %s" % (name, "caught by %s" % want if ok else
                                  "NOT CAUGHT (rc=%s, %d other failure(s))"
                                  % (rc, len(fails))))
        if not ok:
            bad.append(name)
    _restore()
    print("\nattack_reproduction: %d case(s), %d unnoticed"
          % (len(CASES), len(bad)))
    for b in bad:
        print("  FAIL  the gate did not notice: %s" % b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

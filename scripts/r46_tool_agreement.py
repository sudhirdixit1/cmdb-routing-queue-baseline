"""r46 -- THE INDEPENDENCE CHECK.

PLAN-REVIEWER-PROOF.md section 6.1.  The paper's headline surface is
re-derived through `fieldvalue`, the package shipped with the paper, and
asserted against `r30_instrument_matrix.py`'s output.  Two code paths agreeing
is a check this repository did not previously have: every number in it came
from one pipeline, and a systematic error in that pipeline would be invisible
to a checker that reads the pipeline's own output.

WHAT IS AND IS NOT INDEPENDENT, stated so the check is not oversold.

  INDEPENDENT.  The metric implementations (`fieldvalue/metrics.py` computes
  AUC from midranks and average precision from the PR steps, in numpy, and
  never calls scikit-learn), the surface assembly, the baseline pairing, the
  population masking and the reduction arithmetic.

  NOT INDEPENDENT.  scikit-learn's OneHotEncoder and LogisticRegression, which
  both paths call, and the cohort, which both read from `r4_final.py` through
  `base14`.  An error in the estimator or in the cohort would agree with
  itself and this check would not see it.  That is stated in the paper.

Outputs: results/r46_agreement.csv, r46_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))            # so `import fieldvalue` resolves

import base14 as B                                            # noqa: E402
from common import RESULTS                                    # noqa: E402
import fieldvalue                                             # noqa: E402
from fieldvalue import surface                                # noqa: E402

TOL = 1e-9
GRID = tuple(np.round(np.arange(0.05, 0.8001, 0.025), 4))
NAMED = ("auc", "ap", "brier_skill", "nagelkerke")


def main():
    t0 = time.time()
    print("=" * 92)
    print(f"r46 -- fieldvalue {fieldvalue.__version__} against r30")
    print("=" * 92)

    D = B.D
    X = D[list(B.INTAKE) + [B.Q, B.IDENT]].copy()
    y = D["_y"].values
    print(f"  cohort {len(X):,} rows; intake {B.INTAKE}; free field {B.Q!r}; "
          f"feature {B.IDENT!r}")

    s = surface(X, y, feature=B.IDENT,
                baselines={"intake": list(B.INTAKE),
                           "intake+group": list(B.INTAKE) + [B.Q]},
                metrics=NAMED, thresholds=GRID, population=(1.0,),
                seed=B.SEED, train_frac=0.70)
    F = s.to_frame()

    r30I = pd.read_csv(RESULTS / "r30_instruments.csv").set_index("model")
    r30F = pd.read_csv(RESULTS / "r30_facts.csv").iloc[0]

    rows = []

    def cmp(label, mine, theirs, tol=TOL):
        ok = bool(np.isfinite(mine) and np.isfinite(theirs)
                  and abs(mine - theirs) <= tol)
        rows.append(dict(quantity=label, fieldvalue=mine, r30=theirs,
                         abs_diff=abs(mine - theirs), tol=tol, agrees=ok))
        print(f"  {'OK  ' if ok else 'FAIL'} {label:44s} "
              f"{mine:+.10f}  vs  {theirs:+.10f}   "
              f"|d|={abs(mine - theirs):.3e}")

    # ---- the four scalar instruments, on all four legs ------------------
    LEGS = {"intake": ("intake", 0), "intake + item": ("intake", 1),
            "intake + group": ("intake+group", 0),
            "intake + group + item": ("intake+group", 1)}
    for m in NAMED:
        cell = F[(F.metric == m) & (F.threshold.isna())].iloc[0]
        cmp(f"V(item | intake), {m}", float(cell.V_lo),
            float(r30I.loc["intake + item"][m] - r30I.loc["intake"][m]))
        cmp(f"V(item | intake+group), {m}", float(cell.V_hi),
            float(r30I.loc["intake + group + item"][m]
                  - r30I.loc["intake + group"][m]))
        cmp(f"R under {m}", float(cell.R), float(r30F[f"{m}_reduction"]),
            tol=1e-9)

    # ---- net benefit, at the five thresholds r30 names -------------------
    for t in (0.2, 0.3, 0.4, 0.5):
        col = f"nb_{t}"
        if col not in r30I.columns:
            continue
        cell = F[(F.metric == "net_benefit")
                 & np.isclose(F.threshold.astype(float), t)].iloc[0]
        cmp(f"V(item | intake), net benefit at {t}", float(cell.V_lo),
            float(r30I.loc["intake + item"][col] - r30I.loc["intake"][col]))
        cmp(f"V(item | intake+group), net benefit at {t}", float(cell.V_hi),
            float(r30I.loc["intake + group + item"][col]
                  - r30I.loc["intake + group"][col]))

    A = pd.DataFrame(rows)
    A.to_csv(RESULTS / "r46_agreement.csv", index=False)
    n_ok = int(A.agrees.sum())
    print("\n" + "=" * 92)
    print(f"  {n_ok} of {len(A)} quantities agree to {TOL:g}; "
          f"largest disagreement {A.abs_diff.max():.3e}")

    #  the refusal, exercised rather than described
    refused = False
    try:
        float(s)
    except fieldvalue.SingleNumberRefused as e:
        refused = True
        print("\n  the package's refusal path, exercised:")
        print("    " + str(e).splitlines()[0])

    F.to_csv(RESULTS / "r46_surface.csv", index=False)
    sp = s.spread()
    sp.to_csv(RESULTS / "r46_spread.csv", index=False)
    print("\n  the same surface, summarised by fieldvalue:")
    print(sp.to_string(index=False))

    FA = pd.DataFrame([dict(
        version=fieldvalue.__version__, n_quantities=len(A), n_agree=n_ok,
        max_abs_diff=float(A.abs_diff.max()), tol=TOL,
        refused_single_number=refused,
        n_surface_cells=len(F), n_metrics=len(NAMED), n_grid=len(GRID),
        auc_reduction=float(F[(F.metric == "auc")
                              & (F.threshold.isna())].R.iloc[0]),
        runtime_s=round(time.time() - t0, 1))])
    FA.to_csv(RESULTS / "r46_facts.csv", index=False)
    print("\n" + FA.T.to_string())
    if n_ok != len(A) or not refused:
        sys.exit("the two code paths do not agree, or the refusal did not fire")
    print("\nTwo independent code paths agree on every quantity, and the "
          "package refused to emit a single number.")


if __name__ == "__main__":
    main()

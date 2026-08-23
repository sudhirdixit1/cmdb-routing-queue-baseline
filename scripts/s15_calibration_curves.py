"""s15 -- CALIBRATION CURVES.

Round nineteen.  The referee's Phase 4 asks for the calibration intercept, the
slope, the Brier score AND the calibration curves.  The first three are
columns of `results/s01_fits.csv`, computed for every fitted arm.  The fourth
is a picture, and a picture needs the scores, which the master surface does
not keep because keeping 14,592 score vectors would be a gigabyte.

This file refits the four learners at the reference cell on the primary log
and draws them.  It is the only script in the round that exists to produce one
figure, and it says so.

WHY IT MATTERS HERE.  Two of the five instruments on the metric axis --- Brier
skill and the log-loss skill --- are proper scoring rules and read
calibration; the two rank-based ones cannot see it at all
(Proposition~\\ref{prop:rank} in the manuscript).  So a learner whose
discrimination is fine and whose calibration is not will move the increment on
some instruments and not others, which is one concrete mechanism behind the
metric axis's contribution to the decomposition.

    python s15_calibration_curves.py

Outputs: paper/figS7_calibration.png, results/s15_calibration.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402

PAPER = HERE.parent / "paper"
LOG, TARGET, RUNG = "BPIC14", "handover", "B_intake_g"
NBINS = 10
plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6,
                     "figure.dpi": 200, "savefig.bbox": "tight"})


def main():
    t0 = time.time()
    d, ladder, f, meta = S01.prepare(LOG, TARGET)
    cols = list(dict(ladder)[RUNG]) + [f]
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tr, te = d.iloc[:cut], d.iloc[cut:]
    yte = te["_y"].values
    print("=" * 92)
    print("s15  CALIBRATION CURVES AT THE REFERENCE CELL")
    print("=" * 92)
    print("  %s/%s  train %d  test %d  prevalence %.4f"
          % (LOG, TARGET, len(tr), len(te), float(yte.mean())))

    rows = []
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.plot([0, 1], [0, 1], color="0.6", lw=0.8, ls="--", label="perfect")
    marks = {"logit": "o", "logit_fr": "s", "hgb": "^", "hgb_iso": "d"}
    shades = {"logit": "0.10", "logit_fr": "0.40", "hgb": "0.55",
              "hgb_iso": "0.30"}
    for learner in ("logit", "logit_fr", "hgb", "hgb_iso"):
        p = S.LEARNERS[learner](tr, te, cols, tr["_y"].values, S.SEED)
        cal = S.calibration(p, yte)
        #  equal-count bins, so every point carries the same weight; equal-
        #  width bins put nine tenths of the mass in one bin on a skewed
        #  score distribution and produce a curve that is mostly noise.
        q = np.quantile(p, np.linspace(0, 1, NBINS + 1))
        q[0], q[-1] = -np.inf, np.inf
        b = np.digitize(p, q[1:-1])
        xs, ys, ns = [], [], []
        for k in range(NBINS):
            m = b == k
            if m.sum() < 10:
                continue
            xs.append(float(p[m].mean()))
            ys.append(float(yte[m].mean()))
            ns.append(int(m.sum()))
            rows.append(dict(learner=learner, bin=k, n=int(m.sum()),
                             mean_predicted=xs[-1], observed=ys[-1]))
        ax.plot(xs, ys, marker=marks[learner], ms=3.5, lw=1.0,
                color=shades[learner],
                label="%s  (slope %.2f, Brier %.3f)"
                      % (S.LEARNER_LABEL[learner], cal["cal_slope"],
                         cal["brier"]))
        print("  %-28s intercept %+.3f  slope %.3f  Brier %.4f"
              % (S.LEARNER_LABEL[learner], cal["cal_intercept"],
                 cal["cal_slope"], cal["brier"]), flush=True)
    ax.set_xlabel("mean predicted risk in the decile")
    ax.set_ylabel("observed rate in the decile")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Calibration at the reference cell, by decile of predicted "
                 "risk", fontsize=8.5)
    p = PAPER / "figS7_calibration.png"
    fig.savefig(p)
    plt.close(fig)
    pd.DataFrame(rows).to_csv(RESULTS / "s15_calibration.csv", index=False)
    print("\n  wrote %s in %.0fs" % (p.name, time.time() - t0))


if __name__ == "__main__":
    main()

"""s16 -- DO THE TARGETS MEAN THE SAME THING?

Round nineteen.  The manuscript says the corpus is a benchmark of
specification sensitivity across heterogeneous problems and not a replication,
and the referee's ninth comment is that an earlier version called
semantically different fields and targets replications.  A claim of that shape
should carry a number.

This file computes two agreements.

  1  BETWEEN THE TWO REGISTERED TARGETS, per log: the share of cases on which
     `handover` (more than one resource group touches the case) and `duration`
     (longer than the training-half median) give the same label.  Two targets
     that agreed on almost every case would be one target measured twice, and
     the decomposition's `target` axis would be measuring nothing.

  2  BETWEEN THE CORPUS TARGET AND THE CASE STUDY'S, on the primary log: the
     corpus applies the registered handover rule to its own cohort; the case
     study uses the reassignment target this project defined for the estate.
     The manuscript points out that the log appears twice under two cohorts,
     and this is how far apart the two answers' targets are.

    python s16_target_agreement.py

Outputs: results/s16_target_agreement.csv, s16_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402


def main():
    t0 = time.time()
    import r32_corpus as C
    import r33_generic_ladder as L
    pairs = S01.admitted_pairs()
    logs = sorted({p[0] for p in pairs})
    print("=" * 92)
    print("s16  DO THE TARGETS MEAN THE SAME THING?")
    print("=" * 92)
    rows = []
    for key in logs:
        try:
            d = C.load(key)
            out = L.assign_roles(key, d)
            if out[5]:
                continue
            d, CAND, gsel, fsel, b0sel, code, has_time = out
            cut = int(len(d) * S.TRAIN_FRAC)
            y_h, y_d, _ = L.targets(d, gsel[1], cut)
            if y_h is None or y_d is None:
                continue
            a = float(np.mean(np.asarray(y_h) == np.asarray(y_d)))
            rows.append(dict(log=key, n=len(d), agreement=a,
                             prev_handover=float(np.mean(y_h)),
                             prev_duration=float(np.mean(y_d))))
            print("  %-18s n=%-7d agreement %.3f   prevalences %.3f / %.3f"
                  % (key, len(d), a, rows[-1]["prev_handover"],
                     rows[-1]["prev_duration"]), flush=True)
        except Exception as e:  # noqa: BLE001
            print("  %-18s skipped: %s" % (key, str(e)[:60]))
    A = pd.DataFrame(rows)
    A.to_csv(RESULTS / "s16_target_agreement.csv", index=False)

    #  the corpus target against the case study's, on the primary log
    cross = np.nan
    try:
        import base14 as B
        d14 = C.load("BPIC14")
        out = L.assign_roles("BPIC14", d14)
        d14, _c, gsel, _f, _b, code, _t = out
        cut = int(len(d14) * S.TRAIN_FRAC)
        y_h, _yd, _ = L.targets(d14, gsel[1], cut)
        corpus = pd.Series(np.asarray(y_h), index=d14["Incident ID"].astype(str)
                           if "Incident ID" in d14.columns else None)
        case = pd.Series(B.D["_y"].values,
                         index=B.D["Incident ID"].astype(str))
        if corpus.index is not None:
            both = corpus.index.intersection(case.index)
            if len(both):
                cross = float((corpus.loc[both].values
                               == case.loc[both].values).mean())
                print("\n  corpus handover vs the case study's reassignment "
                      "target on %d shared incidents: %.3f" % (len(both), cross))
    except Exception as e:  # noqa: BLE001
        print("\n  cross-target comparison skipped: %s" % str(e)[:100])

    facts = dict(n_logs=len(A), agreement_median=float(A.agreement.median())
                 if len(A) else np.nan,
                 agreement_min=float(A.agreement.min()) if len(A) else np.nan,
                 agreement_max=float(A.agreement.max()) if len(A) else np.nan,
                 cross_target_agreement=cross,
                 runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s16_facts.csv", index=False)
    print()
    print(pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

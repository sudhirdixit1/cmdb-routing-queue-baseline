"""s09 -- WHY TWO QUALITY MECHANISMS DO NOTHING, AND ONE THAT DOES.

Round nineteen.  The master surface reports six register-quality mechanisms
beside the clean field.  Two of them move the increment by essentially zero on
the primary log, and a paper that prints a null without understanding it is
printing noise.

  STALENESS moves the increment by EXACTLY zero.  The mechanism removes an
  identity that the register had not seen by the split point.  But the
  one-hot encoder is fitted on the training half and ignores levels it has
  never seen, so a test row carrying an undiscovered identity already
  contributes an all-zero encoding.  Replacing that identity with an explicit
  EMPTY token, which is itself absent from the training half, produces the
  same all-zero encoding.  The two are the same thing to the model.

  This is not a defect of the mechanism; it is an INTERACTION BETWEEN THE
  QUALITY AXIS AND THE ENCODING AXIS, which is the paper's thesis appearing
  inside its own apparatus.  Under an encoder that treats missingness as a
  level the two are different, and this file measures how different.

  DUPLICATION moves it by almost zero at 15%.  Splitting one identity into two
  halves the evidence behind each, and with thousands of cases per identity
  that costs little.  It should cost more when the split is deeper and when
  the register is already sparse, and this file sweeps it.

WHAT THIS FILE ADDS

  1  `stale_lag`: a DISCOVERY LAG.  An identity is in the register only if it
     was first used before a point at (1 - lag) of the training window, so
     late-arriving items are missing from BOTH halves rather than from the
     test half alone.  This is what an estate whose discovery tooling runs
     behind actually looks like.
  2  the same six mechanisms under an ENCODER THAT KEEPS MISSINGNESS: an
     explicit indicator column beside the one-hot block, so an absent
     identity is a fact the model can use rather than a row of zeros.
  3  a sweep of the duplication rate and of the corruption rate, so the two
     accuracy mechanisms are reported as curves rather than as one level.

    python s09_quality_extra.py

Outputs: results/s09_mechanisms.csv, s09_sweep.csv, s09_facts.csv
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
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402

from sklearn.metrics import roc_auc_score  # noqa: E402

LOG, TARGET = "BPIC14", "handover"
SEEDS = (0, 1, 2)


def stale_lag(col, lag, train_index):
    """A discovery lag.  An identity is in the register only if it was first
    USED before a point at (1 - lag) of the training window; everything first
    used after that is absent everywhere, in both halves, which is what an
    estate whose discovery runs behind looks like.  Reads positions and values
    only, never an outcome."""
    s = col.astype(str).reset_index(drop=True)
    cut = int(np.max(train_index)) + 1
    boundary = int(cut * (1.0 - lag))
    known = set(s.iloc[:boundary].unique())
    return s.where(s.isin(known), S.EMPTY)


def fit_indicator(tr, te, cols, y, seed):
    """One-hot plus an EXPLICIT MISSINGNESS INDICATOR for every column.  The
    contrast with `spec._onehot_logit` is the whole point: there, an absent
    identity is a row of zeros and is indistinguishable from an unseen one;
    here it is a fact."""
    from scipy import sparse
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    Xt = e.transform(te[cols].astype(str))
    mtr = np.column_stack([(tr[c].astype(str) == S.EMPTY).values.astype(float)
                           for c in cols])
    mte = np.column_stack([(te[c].astype(str) == S.EMPTY).values.astype(float)
                           for c in cols])
    X = sparse.hstack([X, sparse.csr_matrix(mtr)]).tocsr()
    Xt = sparse.hstack([Xt, sparse.csr_matrix(mte)]).tocsr()
    m = LogisticRegression(max_iter=3000, random_state=seed).fit(X, y)
    return m.predict_proba(Xt)[:, 1]


def main():
    t0 = time.time()
    d, ladder, f, meta = S01.prepare(LOG, TARGET)
    rungs = dict(ladder)
    cols = list(rungs["B_intake_g"])
    n = len(d)
    cut = int(n * S.TRAIN_FRAC)
    tri, tei = np.arange(cut), np.arange(cut, n)
    yte = d["_y"].values[tei]
    print("=" * 92)
    print("s09  REGISTER QUALITY: TWO NULLS EXPLAINED, AND A MECHANISM THAT "
          "BITES")
    print("=" * 92)
    print("  %s/%s  n=%d  feature=%r  baseline=%s" % (LOG, TARGET, n, f, cols))

    MECHS = [("clean", 1.00), ("mask_rare", 0.75), ("mask_rare", 0.50),
             ("mask_rare", 0.25), ("mask_random", 0.50), ("mask_common", 0.50),
             ("corrupt", 0.05), ("corrupt", 0.15), ("corrupt", 0.30),
             ("duplicate", 0.15), ("duplicate", 0.50), ("duplicate", 1.00),
             ("stale", 1.00), ("stale_lag", 0.10), ("stale_lag", 0.25),
             ("stale_lag", 0.50)]

    rows = []
    for kind, level in MECHS:
        for encoder in ("ignores-missing", "keeps-missing"):
            vals, pops = [], []
            seeds = SEEDS if kind in S.STOCHASTIC_KINDS else (0,)
            for sd in seeds:
                rng = np.random.default_rng(S.SEED + 1000 * sd)
                dd = d.copy()
                if kind == "stale_lag":
                    dd["_f"] = stale_lag(d[f], level, tri)
                else:
                    dd["_f"] = S.degrade(d[f], kind, level, rng, tri)
                pops.append(float((dd["_f"] != S.EMPTY).mean()))
                tr, te = dd.iloc[tri], dd.iloc[tei]
                fit = (S._onehot_logit if encoder == "ignores-missing"
                       else fit_indicator)
                p0 = fit(tr, te, cols, tr["_y"].values, S.SEED)
                p1 = fit(tr, te, cols + ["_f"], tr["_y"].values, S.SEED)
                vals.append(roc_auc_score(yte, p1) - roc_auc_score(yte, p0))
            rows.append(dict(mechanism=kind, level=level, encoder=encoder,
                             populated=float(np.mean(pops)),
                             V=float(np.mean(vals)), n_seeds=len(seeds)))
            print("  %-11s %.2f  %-16s populated %.3f  V %+.4f"
                  % (kind, level, encoder, rows[-1]["populated"],
                     rows[-1]["V"]), flush=True)
    M = pd.DataFrame(rows)
    M.to_csv(RESULTS / "s09_mechanisms.csv", index=False)

    #  the two contrasts the section turns on
    def val(kind, level, enc):
        r = M[(M.mechanism == kind) & (np.isclose(M.level, level))
              & (M.encoder == enc)]
        return float(r.V.iloc[0]) if len(r) else np.nan

    clean_i = val("clean", 1.00, "ignores-missing")
    clean_k = val("clean", 1.00, "keeps-missing")
    facts = dict(
        clean_ignores=clean_i, clean_keeps=clean_k,
        stale_ignores_delta=val("stale", 1.00, "ignores-missing") - clean_i,
        stale_keeps_delta=val("stale", 1.00, "keeps-missing") - clean_k,
        stale_lag_quarter_delta=val("stale_lag", 0.25, "ignores-missing") - clean_i,
        stale_lag_half_delta=val("stale_lag", 0.50, "ignores-missing") - clean_i,
        duplicate_15_delta=val("duplicate", 0.15, "ignores-missing") - clean_i,
        duplicate_100_delta=val("duplicate", 1.00, "ignores-missing") - clean_i,
        corrupt_30_delta=val("corrupt", 0.30, "ignores-missing") - clean_i,
        mask_rare_half=val("mask_rare", 0.50, "ignores-missing"),
        mask_common_half=val("mask_common", 0.50, "ignores-missing"),
        mask_random_half=val("mask_random", 0.50, "ignores-missing"),
        mask_rare_half_keeps=val("mask_rare", 0.50, "keeps-missing"),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s09_facts.csv", index=False)
    print()
    print(pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

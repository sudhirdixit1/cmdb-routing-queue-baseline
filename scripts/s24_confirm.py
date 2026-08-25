"""s24 -- THE FIVE PLANNED CONTRASTS, AT A BOOTSTRAP SIZE THAT CAN CARRY THEM.

Round twenty, blueprint P0.7.

TWO THINGS WERE WRONG.

1  A p-value of zero.  Round nineteen reported raw and Holm-adjusted bootstrap
   p-values of 0.000 from 200 draws.  A finite bootstrap cannot produce zero:
   the estimator

       p = (k + 1) / (B + 1)

   is the one to use, its smallest attainable value is 1/(B+1), and the
   manuscript must not print a number the design cannot produce.  With 5,000
   independent draws the floor is 0.00020, and the smallest attainable
   Holm-adjusted value over five tests is 0.00100.

2  "Confirmatory".  The five contrasts were fixed before the final bootstrap
   but after the same data had been analysed for eighteen rounds.  That is not
   what confirmatory means.  They are FINAL-ROUND PLANNED CONTRASTS: chosen
   before the analysis reported here, not before the data were seen.  Every
   other comparison in the manuscript is exploratory and is labelled so.

Each contrast below carries a COMPLETE estimand: log, cohort, target, learner,
encoding, split, decision time, register quality, baseline and instrument.  A
contrast whose estimand is not fully written down is not a contrast.

    python s24_confirm.py                # 5,000 draws
    python s24_confirm.py --draws 200    # a smoke test

Outputs: results/s24_contrasts.csv   the five, with plus-one p-values
         results/s24_draws.csv.gz    the draw distribution
         results/s24_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s01_surface as S01  # noqa: E402
from common import RESULTS  # noqa: E402

PRIMARY = "BPIC14"
TARGET = "handover"
LEARNER = "logit"
SPLIT = "holdout70"
ALPHA = 0.05

#  the cells the five contrasts are built from: (rung, quality, level)
CELLS = (("B_half", "clean", 1.00),
         ("B_intake", "clean", 1.00),
         ("B_intake_g", "clean", 1.00),
         ("B_intake_g_km", "clean", 1.00),
         ("B_intake_g", "mask_rare", 0.50))

#  Each contrast is (id, text, cell_a, cell_b or None, decision time).
#  `estimand` spells the specification out so nothing is implied.
CONTRASTS = [
    dict(id="PC1",
         text="the register adds to the intake baseline",
         a=("B_intake", "clean", 1.00), b=None, decision_time="t_incident"),
    dict(id="PC2",
         text="the register adds once the free assignment field is admitted",
         a=("B_intake_g", "clean", 1.00), b=None, decision_time="t_incident"),
    dict(id="PC3",
         text="the register adds at the later decision time, after the "
              "knowledge reference exists",
         a=("B_intake_g_km", "clean", 1.00), b=None,
         decision_time="t_incident, knowledge reference admitted"),
    dict(id="PC4",
         text="the free assignment field absorbs part of the register's "
              "contribution",
         a=("B_intake", "clean", 1.00), b=("B_intake_g", "clean", 1.00),
         decision_time="t_incident"),
    dict(id="PC5",
         text="a register missing its long tail is worth less than a "
              "complete one",
         a=("B_intake_g", "clean", 1.00),
         b=("B_intake_g", "mask_rare", 0.50), decision_time="t_incident"),
]

ESTIMAND = dict(log=PRIMARY, cohort="every incident at terminal state",
                target=TARGET, learner=LEARNER, encoding="one-hot",
                split=SPLIT, instrument="auc",
                register="CI Name (aff)", free_field="assignment group")


def one_draw(b):
    """One nested moving-block draw: refit every arm of every cell."""
    try:
        d, ladder, f, meta = S01.prepare(PRIMARY, TARGET)
        rungs = {nm: cols for nm, cols in ladder}
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri0, tei0 = np.arange(cut), np.arange(cut, n)
        if b < 0:
            tri, tei = tri0, tei0
        else:
            rng = np.random.default_rng(S.SEED + 7919 * b)
            tri = tri0[S.block_indices(len(tri0), rng)]
            tei = tei0[S.block_indices(len(tei0), rng)]
        yte = d["_y"].values[tei]
        if len(np.unique(yte)) < 2:
            return []
        prev_tr = float(d["_y"].values[tri].mean())
        out = []
        cache = {}
        for rung, kind, level in CELLS:
            if rung not in rungs:
                continue
            key = (kind, level)
            if key not in cache:
                dd = d.copy()
                dd["_f"] = S.degrade(d[f], kind, level,
                                     np.random.default_rng(S.SEED), tri0)
                cache[key] = (dd.iloc[tri], dd.iloc[tei])
            tr, te = cache[key]
            cols = list(rungs[rung])
            M = {}
            for arm, cc in (("without_f", cols), ("with_f", cols + ["_f"])):
                p = S.LEARNERS[LEARNER](tr, te, cc, tr["_y"].values, S.SEED)
                M[arm] = S.all_metrics(p, yte, prev_tr)
            out.append(dict(draw=b, rung=rung, quality=kind, level=level,
                            V=M["with_f"]["auc"] - M["without_f"]["auc"]))
        return out
    except Exception:  # noqa: BLE001
        sys.stderr.write(traceback.format_exc()[-400:])
        return []


def plus_one_p(stat, direction="gt"):
    """The plus-one bootstrap p-value.  For H0: theta <= 0 against theta > 0,
    k is the number of draws at or below zero."""
    a = np.asarray(stat, float)
    a = a[np.isfinite(a)]
    B = len(a)
    if B == 0:
        return np.nan, 0
    k = int((a <= 0).sum()) if direction == "gt" else int((a >= 0).sum())
    return (k + 1) / (B + 1.0), B


def holm(p):
    """Holm-Bonferroni, computed here and re-derived independently by
    verify_numbers so a transcription cannot hide in it."""
    p = list(p)
    k = len(p)
    order = np.argsort(p)
    out = [0.0] * k
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, p[j] * (k - i)))
        out[j] = run
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=5000)
    ap.add_argument("--procs", type=int, default=0)
    a = ap.parse_args(argv)
    t0 = time.time()
    nproc = a.procs or min(13, max(1, (os.cpu_count() or 4) - 1))

    print("=" * 92)
    print("s24  FIVE PLANNED CONTRASTS AT %d INDEPENDENT DRAWS" % a.draws)
    print("=" * 92)
    tasks = [-1] + list(range(a.draws))
    rows = []
    import multiprocessing as mp
    with mp.Pool(processes=nproc) as pool:
        for i, r in enumerate(pool.imap_unordered(one_draw, tasks,
                                                  chunksize=4)):
            rows += r
            if (i + 1) % 500 == 0:
                print("    %d/%d  %.0fs" % (i + 1, len(tasks),
                                            time.time() - t0), flush=True)
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "s24_draws.csv.gz", index=False, compression="gzip")

    pt = D[D.draw < 0].set_index(["rung", "quality", "level"]).V
    bt = D[D.draw >= 0]
    W = bt.pivot_table(index="draw", columns=["rung", "quality", "level"],
                       values="V")
    n_independent = int(W.shape[0])

    out = []
    for c in CONTRASTS:
        ka = (c["a"][0], c["a"][1], c["a"][2])
        if ka not in W.columns:
            continue
        if c["b"] is None:
            stat = W[ka]
            est = float(pt.get(ka, np.nan))
        else:
            kb = (c["b"][0], c["b"][1], c["b"][2])
            if kb not in W.columns:
                continue
            stat = W[ka] - W[kb]
            est = float(pt.get(ka, np.nan)) - float(pt.get(kb, np.nan))
        p_raw, B = plus_one_p(stat.values)
        out.append(dict(
            contrast=c["id"], text=c["text"],
            decision_time=c["decision_time"],
            cell_a="/".join(map(str, c["a"])),
            cell_b="/".join(map(str, c["b"])) if c["b"] else "",
            estimate=est, se=float(np.nanstd(stat.values, ddof=1)),
            lo=float(np.nanpercentile(stat.values, 100 * ALPHA / 2)),
            hi=float(np.nanpercentile(stat.values, 100 * (1 - ALPHA / 2))),
            basic_lo=2 * est - float(np.nanpercentile(stat.values,
                                                      100 * (1 - ALPHA / 2))),
            basic_hi=2 * est - float(np.nanpercentile(stat.values,
                                                      100 * ALPHA / 2)),
            p_raw=p_raw, n_draws=B, **ESTIMAND))
    C = pd.DataFrame(out)
    if len(C):
        C["p_holm"] = holm(C.p_raw.values)
        C["reject_holm_05"] = C.p_holm < ALPHA
        C["p_floor_raw"] = 1.0 / (n_independent + 1.0)
        C["p_floor_holm"] = len(C) / (n_independent + 1.0)
    C.to_csv(RESULTS / "s24_contrasts.csv", index=False)
    print("\n" + C[["contrast", "estimate", "se", "lo", "hi", "p_raw",
                    "p_holm", "reject_holm_05"]].to_string(
        index=False, float_format=lambda x: "%.5f" % x))

    facts = dict(
        n_contrasts=len(C), n_independent_draws=n_independent,
        n_draw_records=int(len(bt)),
        p_min_attainable_raw=1.0 / (n_independent + 1.0),
        p_min_attainable_holm=len(C) / (n_independent + 1.0),
        p_raw_min=float(C.p_raw.min()) if len(C) else np.nan,
        p_holm_min=float(C.p_holm.min()) if len(C) else np.nan,
        n_reject=int(C.reject_holm_05.sum()) if len(C) else 0,
        any_zero_p=int(((C.p_raw <= 0) | (C.p_holm <= 0)).sum())
        if len(C) else 0,
        runtime_s=round(time.time() - t0, 1))
    for _, r in C.iterrows():
        facts["est_" + r.contrast] = float(r.estimate)
        facts["p_" + r.contrast] = float(r.p_holm)
    pd.DataFrame([facts]).to_csv(RESULTS / "s24_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

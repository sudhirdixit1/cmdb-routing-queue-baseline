"""s37 -- LEARNER AND ENCODING, CROSSED RATHER THAN CONFOUNDED.  M7.

THE OBJECTION.  Table 1 declares encoding as an axis; the decomposition has no
encoding column.  What the four "learners" actually are is two model families
crossed with two encodings and a calibration, so a sensitivity index for
"learner" is a mixture of family and encoding, and on eighteen of nineteen
pairs only two of the four levels run at all -- making the index a statement
about a two-level axis.

THIS FILE CROSSES THEM.  On the case-study log, where the budget allows it,
the two model families are run against all three encodings:

                 one-hot      frequency     cross-fitted target
  logistic          x             x                  x
  gradient boosting x             x                  x

Six pipelines, a full 2 x 3 factorial, so the functional-ANOVA decomposition
can carry a FAMILY axis and an ENCODING axis separately and their interaction
is a term rather than a confound.

WHAT IT COSTS AND WHY IT IS WORTH IT.  Gradient boosting on a one-hot
expansion of a 3,019-level register is the expensive cell and is exactly the
one the confound was hiding: the existing grid never ran it, so "gradient
boosting" and "target encoding" had never been separated on this log.

THE DECOMPOSITION IS THE SAME ONE.  s22's exact functional ANOVA is applied to
the crossed design, so the shares reported here are comparable with the ones
Section 6 reports for the confounded axis.

    python s37_axes.py --plan
    python s37_axes.py

Outputs: results/s37_cells.csv     one row per (family, encoding, cell)
         results/s37_indices.csv   the decomposition with both axes
         results/s37_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import itertools
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

PAIRS = (("BPIC14", "handover"), ("BPIC14", "duration"))

#  ROUND TWENTY-SEVEN.  Section 11 conceded that the crossing runs on the case
#  study's log alone, so the other pairs carry family and encoding confounded,
#  and an internal audit then found the concession understated by two pairs.
#  The crossing needs POINT ESTIMATES ONLY --- a decomposition takes no
#  bootstrap and no band --- so extending it to the ITSM family costs six
#  pipelines on six further logs, which is a small fraction of what one
#  bootstrap pair costs.  The eight ITSM pairs are the population Section
#  S10.16 already reports every headline on separately, which is why they are
#  the extension rather than an arbitrary six.
#
#  This is a claim the paper LIKES, run on new pairs for the first time, so
#  rule 2 of PLAN-STRONG-ACCEPT applies with force: the prior is that
#  `encoding beats family' does not fully replicate, and if it does not, the
#  paper narrows the claim to the case study rather than the other way round.
ITSM_PAIRS = (("BPIC13_closed", "handover"),
              ("BPIC13_incidents", "duration"),
              ("BPIC13_incidents", "handover"),
              ("BPIC14", "duration"),
              ("BPIC14", "handover"),
              ("Helpdesk", "duration"),
              ("UCI498", "duration"),
              ("UCI498", "handover"))

PAIR_SETS = {"case": PAIRS, "itsm": ITSM_PAIRS}
#: appended to every output name so a wider run cannot overwrite the
#: case-study results the manuscript's macros are computed from.
SUFFIX = ""
FAMILIES = ("logistic", "gradient boosting")
ENCODINGS = ("one-hot", "frequency", "cross-fitted target")
QUALITY = (("clean", 1.00), ("mask_rare", 0.50), ("corrupt", 0.15))
RUNGS = ("B_half", "B_intake", "B_intake_g", "B_intake_g_km")
SPLIT_KINDS = ("holdout70", "rolling")
N_ROLLING_KEPT = 2
METRICS = ("auc", "ap", "brier_skill", "nagelkerke", "logloss_skill")


# --------------------------------------------------------------------------
def encode(tr, te, cols, encoding, seed):
    """The encoded design matrices for one encoding, fitted on train only."""
    if encoding == "one-hot":
        from sklearn.preprocessing import OneHotEncoder
        e = OneHotEncoder(handle_unknown="ignore")
        return e.fit_transform(tr[cols].astype(str)), \
            e.transform(te[cols].astype(str))
    if encoding == "frequency":
        Xtr, Xte = [], []
        for c in cols:
            a = tr[c].astype(str)
            vc = a.value_counts()
            Xtr.append(np.log1p(a.map(vc).fillna(0.0).values.astype(float)))
            Xte.append(np.log1p(te[c].astype(str).map(vc).fillna(0.0)
                                .values.astype(float)))
        return np.column_stack(Xtr), np.column_stack(Xte)
    if encoding == "cross-fitted target":
        from sklearn.preprocessing import TargetEncoder
        e = TargetEncoder(target_type="binary", cv=5, random_state=seed)
        X = e.fit_transform(tr[cols].astype(str).values, tr["_y"].values)
        return X, e.transform(te[cols].astype(str).values)
    raise ValueError(encoding)


def fit_predict(tr, te, cols, family, encoding, seed=S.SEED):
    """One (family, encoding) pipeline.  The encoding is fitted on the
    training half and applied to both, exactly as spec.py's learners do."""
    Xtr, Xte = encode(tr, te, cols, encoding, seed)
    y = tr["_y"].values
    if family == "logistic":
        from sklearn.linear_model import LogisticRegression
        if encoding != "one-hot":
            Xtr = np.asarray(Xtr, float)
            Xte = np.asarray(Xte, float)
            mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
            Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
        m = LogisticRegression(max_iter=3000, random_state=seed).fit(Xtr, y)
        return m.predict_proba(Xte)[:, 1]
    from sklearn.ensemble import HistGradientBoostingClassifier
    if encoding == "one-hot":
        #  HistGradientBoosting has no sparse path, and a dense 3,019-column
        #  expansion of 32,000 rows is 770 MB.  The expansion is kept sparse
        #  and reduced by a truncated SVD fitted on the TRAINING half, which
        #  is the standard way to give a tree learner a high-cardinality
        #  one-hot and is declared here as part of the pipeline rather than
        #  left as an implementation detail.
        from sklearn.decomposition import TruncatedSVD
        k = int(min(128, max(2, Xtr.shape[1] - 1)))
        svd = TruncatedSVD(n_components=k, random_state=seed).fit(Xtr)
        Xtr, Xte = svd.transform(Xtr), svd.transform(Xte)
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1,
                                       random_state=seed)
    return m.fit(np.asarray(Xtr, float), y).predict_proba(
        np.asarray(Xte, float))[:, 1]


def one(args):
    """One (pair, family, encoding): every cell of the sub-surface."""
    log, target, family, encoding = args
    t0 = time.time()
    try:
        d, ladder, f, meta = S01.prepare(log, target)
        if d is None:
            return [], dict(log=log, target=target, family=family,
                            encoding=encoding, reason=meta)
        rungs = dict(ladder)
        n = len(d)
        splits = []
        for kind in SPLIT_KINDS:
            got = list(S.splits(n, kind, n_folds=5))
            splits += got[:1] if kind == "holdout70" else got[:N_ROLLING_KEPT]
        rows = []
        for split_name, tri, tei in splits:
            yte = d["_y"].values[tei]
            if len(np.unique(yte)) < 2:
                continue
            prev_tr = float(d["_y"].values[tri].mean())
            for kind, level in QUALITY:
                dd = d.copy()
                dd["_f"] = S.degrade(d[f], kind, level,
                                     np.random.default_rng(S.SEED), tri)
                tr, te = dd.iloc[tri], dd.iloc[tei]
                for rung in RUNGS:
                    cols = list(rungs.get(rung, []))
                    if not cols:
                        continue
                    M = {}
                    for arm, cc in (("without_f", cols),
                                    ("with_f", cols + ["_f"])):
                        p = fit_predict(tr, te, cc, family, encoding)
                        M[arm] = S.all_metrics(p, yte, prev_tr)
                    for m in METRICS:
                        rows.append(dict(
                            log=log, target=target, family=family,
                            encoding=encoding, split=split_name,
                            quality=kind, level=level,
                            quality_level="%s/%s" % (kind, level),
                            rung=rung, metric=m,
                            without_f=M["without_f"][m],
                            with_f=M["with_f"][m],
                            V=M["with_f"][m] - M["without_f"][m]))
        print("  [%s/%s/%s/%s] %d rows %.0fs"
              % (log, target, family, encoding, len(rows), time.time() - t0),
              flush=True)
        return rows, None
    except Exception as e:  # noqa: BLE001
        return [], dict(log=log, target=target, family=family,
                        encoding=encoding, reason="ERROR:%s" % e,
                        trace=traceback.format_exc()[-500:])


# --------------------------------------------------------------------------
def decompose(sub, axes):
    """s22's exact functional ANOVA, unchanged, on the crossed design.

    The decomposition is not reimplemented here: `s22_anova.decompose` is the
    one Section 4 defines and Section 6 reports, and calling it is what makes
    the shares in this file comparable with the ones in that one.  The only
    thing that differs is the axis list.
    """
    import s22_anova as A22
    res = A22.decompose(sub, tuple(axes), "V", "equal-level")
    if res is None:
        return pd.DataFrame(), np.nan
    rows = []
    for u, share in res["components"].items():
        if not u:
            continue
        rows.append(dict(term=" x ".join(axes[j] for j in u),
                         order=len(u), share=float(share),
                         variance=float(share) * res["var"]))
    D = pd.DataFrame(rows)
    #  the identity the whole construction rests on, checked rather than
    #  asserted: the disjoint components sum to one
    D.attrs["check_sum"] = float(D.share.sum())
    return D, float(res["var"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--pairs", choices=sorted(PAIR_SETS), default="case",
                    help="which pair set to cross: `case' is the case study's "
                         "two pairs, `itsm' the eight ITSM pairs Section "
                         "S10.16 reports on separately")
    ap.add_argument("--procs", type=int, default=None,
                    help="pool size; lower it when another run holds the "
                         "machine")
    a = ap.parse_args(argv)
    global SUFFIX
    pairs = PAIR_SETS[a.pairs]
    SUFFIX = "" if a.pairs == "case" else "_" + a.pairs
    t0 = time.time()
    tasks = [(lg, tg, fam, enc) for (lg, tg) in pairs
             for fam in FAMILIES for enc in ENCODINGS]
    n_cells = (1 + N_ROLLING_KEPT) * len(QUALITY) * len(RUNGS)
    print("=" * 92)
    print("s37  LEARNER AND ENCODING, CROSSED")
    print("=" * 92)
    print("  %d pipelines x %d cells x 2 arms = %s fits"
          % (len(tasks), n_cells, format(len(tasks) * n_cells * 2, ",")))
    if a.plan:
        return
    R, X = [], []
    if a.serial:
        for t in tasks:
            rows, err = one(t)
            R += rows
            if err:
                X.append(err)
    else:
        import multiprocessing as mp
        with mp.Pool(processes=(a.procs if a.procs
                                else min(12,
                                         max(1, (os.cpu_count() or 4) - 2)))) as pool:
            for rows, err in pool.imap_unordered(one, tasks):
                R += rows
                if err:
                    X.append(err)
                    print("  FAILED %s" % err, flush=True)
    C = pd.DataFrame(R)
    C.to_csv(RESULTS / ("s37_cells%s.csv" % SUFFIX), index=False)
    if not len(C):
        raise SystemExit("s37 produced no cells")

    out = []
    for (lg, tg, metric), sub in C.groupby(["log", "target", "metric"]):
        D, tot = decompose(sub, ("family", "encoding", "quality_level",
                                 "rung", "split"))
        if not len(D):
            continue
        out.append(D.assign(log=lg, target=tg, metric=metric,
                            total_variance=tot))
    IDX = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    IDX.to_csv(RESULTS / ("s37_indices%s.csv" % SUFFIX), index=False)

    first = IDX[IDX.order == 1]
    piv = first.pivot_table(index=["log", "target"], columns="term",
                            values="share", aggfunc="median")
    print("\n  FIRST-ORDER SHARES, median over instruments")
    print(piv.to_string())

    fam = float(first[first.term == "family"].share.median())
    enc = float(first[first.term == "encoding"].share.median())
    inter = IDX[IDX.term.isin(["family x encoding"])]
    facts = dict(
        n_pipelines=len(tasks), n_cells_per_pipeline=n_cells,
        n_rows=len(C), n_failed=len(X),
        n_families=len(FAMILIES), n_encodings=len(ENCODINGS),
        share_family=fam, share_encoding=enc,
        share_family_x_encoding=float(inter.share.median()) if len(inter)
        else np.nan,
        share_rung=float(first[first.term == "rung"].share.median()),
        share_quality=float(first[first.term == "quality_level"].share.median()),
        share_split=float(first[first.term == "split"].share.median()),
        higher_order_share=float(
            IDX[IDX.order > 1].groupby(["log", "target", "metric"]).share.sum()
            .median()),
        larger_axis="encoding" if enc > fam else "family",
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / ("s37_facts%s.csv" % SUFFIX),
                                 index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s37_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

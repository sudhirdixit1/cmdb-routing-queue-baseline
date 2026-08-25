"""s26 -- CALIBRATION FIRST, THEN THE DECISION CURVE.

Round twenty, blueprint P0.8.

A decision curve reads its x-axis as a PROBABILITY THRESHOLD, and the whole
interpretation -- that t encodes the exchange rate between a false positive and
a false negative, so net benefit is measured in true-positives-per-case --
depends on the score being a probability.  Round nineteen reported calibration
slopes far from one on several pairs and then applied the same threshold grid
to those scores anyway.  A threshold of 0.2 on a score whose calibration slope
is 0.2 is not a statement about a cost ratio of 1:4.

WHAT THIS FILE DOES.

  1  Refits every arm of every rung under a TRAINING-ONLY calibration:
     isotonic and Platt, each fitted by cross-validation INSIDE the training
     half, so no test outcome touches the calibrator.
  2  Reports calibration intercept, slope, Brier score and a binned
     calibration curve for the raw and the calibrated scores.
  3  Recomputes the decision curve on both, so the reader can see what
     calibration changes.
  4  Declares which curves may be read as probability-threshold decision
     curves (calibrated) and which are score-threshold sensitivity analyses
     (raw).
  5  Runs a nested moving-block bootstrap on the primary pair's CALIBRATED
     curves and forms a SIMULTANEOUS band over the whole threshold grid, so
     the harmful band is identified with family-wise rather than pointwise
     coverage.

    python s26_calib_dca.py                # everything
    python s26_calib_dca.py --no-boot      # point estimates only
    python s26_calib_dca.py --draws 40     # a short bootstrap
    python s26_calib_dca.py --bands-only   # rebuild the bands from
                                           # stored draws, no refits

Outputs: results/s26_calibration.csv  intercept, slope, Brier, ECE per arm
         results/s26_curve.csv        binned calibration curves
         results/s26_dca.csv          net benefit by threshold, raw vs calib
         results/s26_bands.csv        simultaneous DCA bands, calibrated
         results/s26_facts.csv
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
ALPHA = 0.05
CALIBRATIONS = ("raw", "platt", "isotonic")


# --------------------------------------------------------------------------
def fit_predict(tr, te, cols, y, seed, base, calib):
    """Test-set scores from `base`, optionally wrapped in a training-only
    calibrator.  The calibrator is cross-validated inside the training half:
    CalibratedClassifierCV(cv=3) fits the base learner on two thirds and the
    link on the held-out third, three times, and averages.  No test outcome is
    used at any point."""
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, TargetEncoder

    Xtr = tr[cols].astype(str)
    Xte = te[cols].astype(str)
    if base == "logit":
        est = Pipeline([("e", OneHotEncoder(handle_unknown="ignore")),
                        ("m", LogisticRegression(max_iter=3000,
                                                 random_state=seed))])
        A, B = Xtr, Xte
    elif base == "hgb":
        est = Pipeline([("e", TargetEncoder(target_type="binary", cv=5,
                                            random_state=seed)),
                        ("m", HistGradientBoostingClassifier(
                            max_iter=200, learning_rate=0.1,
                            random_state=seed))])
        A, B = Xtr.values, Xte.values
    else:
        raise ValueError(base)
    if calib != "raw":
        est = CalibratedClassifierCV(
            est, method="sigmoid" if calib == "platt" else "isotonic", cv=3)
    return est.fit(A, y).predict_proba(B)[:, 1]


def ece(p, y, bins=10):
    """Expected calibration error on equal-count bins."""
    p = np.asarray(p, float)
    y = np.asarray(y, int)
    if len(p) < bins * 5:
        return np.nan
    q = np.quantile(p, np.linspace(0, 1, bins + 1))
    q[0], q[-1] = -np.inf, np.inf
    idx = np.digitize(p, q[1:-1])
    tot = 0.0
    for b in range(bins):
        m = idx == b
        if m.sum() == 0:
            continue
        tot += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(tot)


def curve_bins(p, y, bins=10):
    p = np.asarray(p, float)
    y = np.asarray(y, int)
    q = np.quantile(p, np.linspace(0, 1, bins + 1))
    q[0], q[-1] = -np.inf, np.inf
    idx = np.digitize(p, q[1:-1])
    out = []
    for b in range(bins):
        m = idx == b
        if m.sum() == 0:
            continue
        out.append(dict(bin=b, n=int(m.sum()), p_mean=float(p[m].mean()),
                        y_mean=float(y[m].mean())))
    return out


# --------------------------------------------------------------------------
def one_pair(args):
    """Point estimates for one (log, target): every rung, every learner,
    every calibration."""
    log, target = args
    try:
        d, ladder, f, meta = S01.prepare(log, target)
        if d is None:
            return [], [], []
        n = len(d)
        cut = int(n * S.TRAIN_FRAC)
        tri, tei = np.arange(cut), np.arange(cut, n)
        yte = d["_y"].values[tei]
        prev_tr = float(d["_y"].values[tri].mean())
        dd = d.copy()
        dd["_f"] = S.degrade(d[f], "clean", 1.0,
                             np.random.default_rng(S.SEED), tri)
        tr, te = dd.iloc[tri], dd.iloc[tei]
        cal, cur, dca = [], [], []
        for rung, cols in ladder:
            if rung in S.IMPLAUSIBLE_RUNGS or not cols:
                continue
            for base in ("logit", "hgb"):
                for calib in CALIBRATIONS:
                    P = {}
                    for arm, cc in (("without_f", list(cols)),
                                    ("with_f", list(cols) + ["_f"])):
                        P[arm] = fit_predict(tr, te, cc, tr["_y"].values,
                                             S.SEED, base, calib)
                    for arm in ("without_f", "with_f"):
                        c = S.calibration(P[arm], yte)
                        cal.append(dict(log=log, target=target, rung=rung,
                                        learner=base, calibration=calib,
                                        arm=arm, n_test=len(yte),
                                        ece=ece(P[arm], yte), **c))
                        if arm == "with_f":
                            for b in curve_bins(P[arm], yte):
                                cur.append(dict(log=log, target=target,
                                                rung=rung, learner=base,
                                                calibration=calib, **b))
                    for t in S.NB_GRID:
                        nb0 = S.net_benefit(P["without_f"], yte, float(t))
                        nb1 = S.net_benefit(P["with_f"], yte, float(t))
                        dca.append(dict(log=log, target=target, rung=rung,
                                        learner=base, calibration=calib,
                                        threshold=float(t), nb_without=nb0,
                                        nb_with=nb1, dnb=nb1 - nb0,
                                        prevalence=float(np.mean(yte))))
        return cal, cur, dca
    except Exception:  # noqa: BLE001
        sys.stderr.write("%s/%s\n%s\n" % (log, target,
                                          traceback.format_exc()[-600:]))
        return [], [], []


#: one prepared log per worker; see s20_boot2.prepare_cached.
_PREPARED = {}


def prepare_cached(log, target):
    key = (log, target)
    if key not in _PREPARED:
        _PREPARED.clear()
        _PREPARED[key] = S01.prepare(log, target)
    return _PREPARED[key]


def one_draw(args):
    """One bootstrap draw of the primary pair's CALIBRATED decision curves."""
    log, target, b, calib = args
    try:
        d, ladder, f, meta = prepare_cached(log, target)
        if d is None:
            return []
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
        dd = d.copy()
        dd["_f"] = S.degrade(d[f], "clean", 1.0,
                             np.random.default_rng(S.SEED), tri0)
        tr, te = dd.iloc[tri], dd.iloc[tei]
        rows = []
        for rung, cols in ladder:
            if rung in S.IMPLAUSIBLE_RUNGS or not cols:
                continue
            for base in ("logit", "hgb"):
                P = {}
                for arm, cc in (("without_f", list(cols)),
                                ("with_f", list(cols) + ["_f"])):
                    P[arm] = fit_predict(tr, te, cc, tr["_y"].values,
                                         S.SEED, base, calib)
                for t in S.NB_GRID:
                    rows.append(dict(
                        log=log, target=target, rung=rung, learner=base,
                        calibration=calib, threshold=float(t), draw=b,
                        dnb=S.net_benefit(P["with_f"], yte, float(t))
                        - S.net_benefit(P["without_f"], yte, float(t))))
        return rows
    except Exception:  # noqa: BLE001
        sys.stderr.write(traceback.format_exc()[-400:])
        return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-boot", action="store_true")
    ap.add_argument("--bands-only", action="store_true",
                    help="reload results/s26_draws.csv.gz and "
                         "recompute the band layer from it "
                         "without refitting anything.  The draws "
                         "cost an hour; the bands built from them "
                         "cost a second, and a change to the "
                         "interval CONSTRUCTION should not have "
                         "to pay for the draws again.")
    ap.add_argument("--draws", type=int, default=400)
    ap.add_argument("--procs", type=int, default=0)
    ap.add_argument("--only", default=None,
                    help="one log, for a smoke test")
    a = ap.parse_args(argv)
    t0 = time.time()
    nproc = a.procs or min(13, max(1, (os.cpu_count() or 4) - 1))
    pairs = [(l, t) for l, t, _d in S01.admitted_pairs()]
    if a.only:
        pairs = [q for q in pairs if q[0] == a.only]

    print("=" * 92)
    print("s26  CALIBRATION FIRST, THEN THE DECISION CURVE")
    print("=" * 92)
    import multiprocessing as mp
    CAL, CUR, DCA = [], [], []
    with mp.Pool(processes=nproc) as pool:
        for i, (c, u, g) in enumerate(pool.imap_unordered(one_pair, pairs)):
            CAL += c
            CUR += u
            DCA += g
            print("    %d/%d pairs  %.0fs" % (i + 1, len(pairs),
                                              time.time() - t0), flush=True)
    CAL = pd.DataFrame(CAL)
    CUR = pd.DataFrame(CUR)
    DCA = pd.DataFrame(DCA)
    CAL.to_csv(RESULTS / "s26_calibration.csv", index=False)
    CUR.to_csv(RESULTS / "s26_curve.csv", index=False)
    DCA.to_csv(RESULTS / "s26_dca.csv.gz", index=False, compression="gzip")

    #  which calibration is closest to a probability?  Slope near one and
    #  intercept near zero, judged by |slope-1| + |intercept|.
    CAL["miscal"] = (CAL.cal_slope - 1.0).abs() + CAL.cal_intercept.abs()
    best = (CAL.groupby(["log", "target", "rung", "learner", "arm"])
            .apply(lambda g: g.loc[g.miscal.idxmin(), "calibration"]
                   if g.miscal.notna().any() else "raw",
                   include_groups=False)
            .rename("best_calibration").reset_index())
    best.to_csv(RESULTS / "s26_best.csv", index=False)

    print("\nCALIBRATION BY CONSTRUCTION (median over arms)")
    print(CAL.groupby("calibration")[["cal_slope", "cal_intercept", "brier",
                                      "ece"]].median()
          .to_string(float_format=lambda x: "%.4f" % x))

    BND = pd.DataFrame()
    if a.bands_only:
        src = RESULTS / "s26_draws.csv.gz"
        if not src.exists():
            sys.exit("--bands-only needs results/s26_draws.csv.gz, which a "
                     "full run writes before it builds the bands")
        D = pd.read_csv(src)
        print("  --bands-only: %d stored draw rows reloaded" % len(D))
    if a.bands_only or not a.no_boot:
        if not a.bands_only:
            tasks = [(PRIMARY, "handover", -1, "isotonic")]
            tasks += [(PRIMARY, "handover", b, "isotonic")
                      for b in range(a.draws)]
            rows = []
            with mp.Pool(processes=nproc) as pool:
                for i, r in enumerate(pool.imap_unordered(one_draw, tasks,
                                                          chunksize=1)):
                    rows += r
                    if (i + 1) % 50 == 0:
                        print("    dca draw %d/%d  %.0fs"
                              % (i + 1, len(tasks), time.time() - t0),
                              flush=True)
            D = pd.DataFrame(rows)
            D.to_csv(RESULTS / "s26_draws.csv.gz", index=False,
                     compression="gzip")
        #  SIMULTANEOUS over the whole (rung, learner, threshold) family
        pt = D[D.draw < 0].set_index(["rung", "learner", "threshold"]).dnb
        bt = D[D.draw >= 0]
        W = bt.pivot_table(index="draw",
                           columns=["rung", "learner", "threshold"],
                           values="dnb")
        se = W.std(axis=0, ddof=1)
        mu = W.mean(axis=0)
        ok = se[se > 1e-15].index
        #  The critical value comes from the SAME multiplier bootstrap the
        #  scalar bands use (s21), so the two families are estimated the same
        #  way and the decision curve is not quietly held to a different
        #  standard.  The empirical quantile of the observed maxima is kept
        #  beside it, because the gap between them is the point.
        import s21_bands as S21
        Z = ((W[ok] - mu[ok]) / se[ok]).values
        Z = Z[np.isfinite(Z).all(axis=1)]
        T = np.sort(np.abs(Z).max(axis=1))
        q_emp = float(np.quantile(T, 1 - ALPHA))
        q, q_lo, q_hi = S21.multiplier_quantile(Z, ALPHA)
        rows = []
        for k in ok:
            v = float(pt.get(k, np.nan))
            shift = float(W[k].median()) - v
            rows.append(dict(rung=k[0], learner=k[1], threshold=k[2],
                             dnb=v, se=float(se[k]), q_maxt=q,
                             q_emp=q_emp,
                             q_lo=q_lo, q_hi=q_hi, n_family=len(ok),
                             n_draws=int(len(Z)),
                             sim_lo=v - shift - q * float(se[k]),
                             sim_hi=v - shift + q * float(se[k]),
                             #  BASIC, not percentile.  The manuscript says
                             #  every interval in it is the basic (pivotal)
                             #  construction, and until round twenty's second
                             #  session this one alone was a percentile
                             #  interval -- so the pointwise/simultaneous
                             #  comparison in Section 8.3 was comparing two
                             #  constructions as well as two families.  The
                             #  refit shift that motivates the basic form is
                             #  present in these draws exactly as it is in
                             #  the scalar ones.
                             pt_lo=2 * v - float(np.percentile(W[k], 97.5)),
                             pt_hi=2 * v - float(np.percentile(W[k], 2.5))))
        BND = pd.DataFrame(rows)
        #  Declared, so that a reader -- or verify_numbers -- can see
        #  which construction these columns are without reading this
        #  file.  Both interval columns are the basic (pivotal) form;
        #  until round twenty's second session the pointwise pair was
        #  a raw percentile interval while the manuscript said every
        #  interval in it was basic.
        BND["construction"] = "basic"
        BND["sim_harmful"] = BND.sim_hi < 0
        BND["pt_harmful"] = BND.pt_hi < 0
        BND.to_csv(RESULTS / "s26_bands.csv", index=False)
        print("\n  simultaneous DCA family = %d cells, q = %.3f [%.3f, %.3f]"
              % (len(ok), q, q_lo, q_hi))
        print("  harmful thresholds: %d pointwise, %d simultaneous"
              % (int(BND.pt_harmful.sum()), int(BND.sim_harmful.sum())))

    #  how many pairs would have their decision-curve conclusion changed by
    #  calibrating?  A conclusion is "the register helps at threshold t".
    ch = []
    for (log, target, rung, learner), g in DCA.groupby(
            ["log", "target", "rung", "learner"]):
        raw = g[g.calibration == "raw"].set_index("threshold").dnb
        iso = g[g.calibration == "isotonic"].set_index("threshold").dnb
        both = raw.index.intersection(iso.index)
        if not len(both):
            continue
        ch.append(dict(log=log, target=target, rung=rung, learner=learner,
                       n_thresholds=len(both),
                       n_sign_change=int(((raw[both] > 0)
                                          != (iso[both] > 0)).sum())))
    CH = pd.DataFrame(ch)
    CH.to_csv(RESULTS / "s26_signchange.csv", index=False)

    facts = dict(
        n_arms=len(CAL), n_pairs=int(CAL.groupby(["log", "target"]).ngroups),
        slope_raw_median=float(CAL[CAL.calibration == "raw"].cal_slope.median()),
        slope_iso_median=float(
            CAL[CAL.calibration == "isotonic"].cal_slope.median()),
        slope_platt_median=float(
            CAL[CAL.calibration == "platt"].cal_slope.median()),
        ece_raw_median=float(CAL[CAL.calibration == "raw"].ece.median()),
        ece_iso_median=float(CAL[CAL.calibration == "isotonic"].ece.median()),
        brier_raw_median=float(CAL[CAL.calibration == "raw"].brier.median()),
        brier_iso_median=float(CAL[CAL.calibration == "isotonic"].brier.median()),
        n_raw_slope_outside_half_two=int(
            ((CAL.calibration == "raw")
             & ((CAL.cal_slope < 0.5) | (CAL.cal_slope > 2.0))).sum()),
        n_iso_slope_outside_half_two=int(
            ((CAL.calibration == "isotonic")
             & ((CAL.cal_slope < 0.5) | (CAL.cal_slope > 2.0))).sum()),
        share_best_isotonic=float((best.best_calibration == "isotonic").mean()),
        dca_sign_change_share=float(
            (CH.n_sign_change / CH.n_thresholds).mean()) if len(CH) else np.nan,
        n_dca_rows=len(DCA),
        dca_q_maxt=float(BND.q_maxt.iloc[0]) if len(BND) else np.nan,
        dca_q_lo=float(BND.q_lo.iloc[0]) if len(BND) else np.nan,
        dca_q_hi=float(BND.q_hi.iloc[0]) if len(BND) else np.nan,
        dca_n_family=int(BND.n_family.iloc[0]) if len(BND) else 0,
        dca_harmful_pointwise=int(BND.pt_harmful.sum()) if len(BND) else 0,
        dca_harmful_simultaneous=int(BND.sim_harmful.sum()) if len(BND) else 0,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s26_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

"""s33 -- A COVERAGE-CALIBRATED CRITICAL VALUE.  Round twenty-one, M3.

THE DEFECT.  Two of this paper's four reporting objects -- the resolution
region and the robustness index -- are functions of a band, and Section 10
reports that the band undercovers wherever the register's cardinality K is
large relative to the training row count n.  The corpus lives there: the
median pair sits at K/n = 0.106.  A reviewer is entitled to say that the two
novel objects are unreliable on the corpus they were introduced on.

THE REPAIR.  Undercoverage that is governed by a single observable is
correctable by calibration against that observable, which is what this file
does.

  1  A DENSER (n, K) PLANE.  s31 ran ten cells at 150 replicates.  This runs
     `N_CELLS` cells at `REPS` replicates, chosen so that K/n covers the
     range the corpus actually occupies rather than three points inside it,
     and on two worlds rather than one so that world-dependence is measured.

  2  THE INFLATION FACTOR, EXACTLY.  For replicate i the basic interval is
     [V_i - L_i, V_i + U_i].  Widening it by a factor c gives
     [V_i - cL_i, V_i + cU_i], which covers the truth exactly when

         c >= r_i := max( (V_i - truth)/L_i , (truth - V_i)/U_i ).

     Coverage at c is therefore the empirical distribution function of r
     evaluated at c, and the smallest c attaining nominal coverage is the
     (1 - alpha) quantile of r.  No search and no smoothing: the calibration
     factor IS a quantile of the studentised error, and its Monte Carlo
     interval comes from the same order statistics.

  3  A CURVE, NOT A LOOKUP.  c is fitted against log(K/n) by weighted least
     squares on the cells' log c, weights the inverse Monte Carlo variance.
     The fit is monotone by construction because the slope is estimated and
     reported with its standard error, and the residuals are printed against
     n and against world so that a reader can see whether K/n is sufficient.

  4  APPLIED.  Every pair's whole-surface critical value is multiplied by
     c(K/n) at that pair's own ratio, the cells are relabelled, and the
     regions and rho recomputed.  Both sets are reported; the calibrated one
     is the one the manuscript leads with.

WHAT THIS DOES NOT DO.  The calibration is estimated on a pointwise interval
in a simulation and applied to a simultaneous band on real logs.  It corrects
the scale of the studentised statistic, which is the channel the (n, K) plane
identifies; it does not correct a change in the shape of the maximum's
distribution, and it assumes the simulated worlds' dependence on K/n
transfers.  Section 10 says so in those words.

    python s33_calibrate.py --plan          # cost, no fits
    python s33_calibrate.py                 # the calibration and its use
    python s33_calibrate.py --reuse         # skip the simulation, refit

Outputs: results/s33_replicates.csv.gz   the plane, replicate by replicate
         results/s33_cells.csv           c and its interval, per cell
         results/s33_fit.csv             the fitted curve and its residuals
         results/s33_regions.csv         regions and rho, nominal vs calibrated
         results/s33_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
from common import RESULTS  # noqa: E402

ALPHA = 0.05
SEED = 20260825
REPS = 500
N_BOOT = 50

#  (world, n_train, K).  K/n spans 0.0025 to 0.500, which brackets every pair
#  in the corpus (0.001 to 0.324) with points inside the range rather than
#  three points and an extrapolation.
PLANE = tuple(
    [("linear", n, k) for (n, k) in
     [(8000, 20), (4000, 20), (2000, 20),
      (8000, 100), (4000, 100), (2000, 100),
      (8000, 200), (4000, 200), (2000, 200),
      (8000, 400), (4000, 400), (2000, 400),
      (8000, 1000), (4000, 1000), (2000, 1000),
      (8000, 3019)]]
    + [("sparse", n, k) for (n, k) in
       [(8000, 100), (4000, 200), (2000, 200), (4000, 1000)]])

INTERVAL = "nested_basic"


# --------------------------------------------------------------------------
def one_rep(task):
    """One replicate of one cell.  The world, the truth and the estimator all
    come from s10/s31 so that this file cannot drift from the simulation the
    rest of the paper reports."""
    world, n_tr, K, rep = task
    import s10_simulation2 as SIM
    import s31_simboost as SB
    from sklearn.metrics import roc_auc_score

    n_te = n_tr // 2
    rng = np.random.default_rng(SEED + 1013 * rep + SIM.WORLD_SEED[world]
                                + 7 * K + 3 * n_tr)
    W = SIM.world_spec(world, np.random.default_rng(
        SIM.SEED + SIM.WORLD_SEED[world]), k_override=K)
    tr = SIM.draw(W, n_tr, 1, rng)
    te = SIM.draw(W, n_te, 2, rng)
    yte = te["_y"].values
    if len(np.unique(yte)) < 2:
        return None
    p0 = SIM.fit_scores(tr, te, ["b", "g"])
    p1 = SIM.fit_scores(tr, te, ["b", "g", "f"])
    V = float(roc_auc_score(yte, p1) - roc_auc_score(yte, p0))
    ell_tr, ell_te = SB.block_len(n_tr), SB.block_len(n_te)
    nn = []
    for b in range(N_BOOT):
        r = np.random.default_rng(SEED + 104729 * b + rep + 13 * K)
        tb = tr.iloc[S.block_indices(len(tr), r, ell=ell_tr)]
        eb = te.iloc[S.block_indices(len(te), r, ell=ell_te)]
        yb = eb["_y"].values
        if len(np.unique(yb)) < 2:
            continue
        q0 = SIM.fit_scores(tb, eb, ["b", "g"])
        q1 = SIM.fit_scores(tb, eb, ["b", "g", "f"])
        nn.append(roc_auc_score(yb, q1) - roc_auc_score(yb, q0))
    a = np.asarray(nn, float)
    if len(a) < 10:
        return None
    D = SB.intervals_from(a, V)
    lo, hi = D["basic"]
    return dict(world=world, K=K, n_train=n_tr, rep=rep, V=V, lo=lo, hi=hi)


def limits(cells):
    """V_limit once per (world, K), which is what the coverage is coverage
    OF.  The limit is a property of the world and the pipeline."""
    import s10_simulation2 as SIM
    out = {}
    for (w, n, K) in sorted({(w, n, K) for (w, n, K) in cells}):
        W = SIM.world_spec(w, np.random.default_rng(
            SIM.SEED + SIM.WORLD_SEED[w]), k_override=K)
        out[(w, n, K)] = float(SIM.limit_estimand(
            W, np.random.default_rng(SEED + 7 + K)))
        print("  limit  %-8s n=%-5d K=%-5d  V_limit %+.5f"
              % (w, n, K, out[(w, n, K)]), flush=True)
    return out


def factor(R, truth, alpha=ALPHA, n_boot=2000, seed=0):
    """The smallest inflation factor attaining nominal coverage, with a
    Monte Carlo interval from a nonparametric bootstrap over replicates."""
    L = (R.V - R.lo).values
    U = (R.hi - R.V).values
    ok = (L > 1e-12) & (U > 1e-12) & np.isfinite(L) & np.isfinite(U)
    L, U, V = L[ok], U[ok], R.V.values[ok]
    if len(V) < 30:
        return None
    r = np.maximum((V - truth) / L, (truth - V) / U)
    c = float(np.quantile(r, 1 - alpha))
    rng = np.random.default_rng(seed)
    bs = [float(np.quantile(r[rng.integers(0, len(r), len(r))], 1 - alpha))
          for _ in range(n_boot)]
    cov_nominal = float(np.mean(r <= 1.0))
    return dict(n=len(r), c=c, c_lo=float(np.quantile(bs, 0.025)),
                c_hi=float(np.quantile(bs, 0.975)),
                coverage_nominal=cov_nominal,
                coverage_nominal_se=float(
                    np.sqrt(max(cov_nominal * (1 - cov_nominal), 1e-12)
                            / len(r))),
                median_r=float(np.median(r)))


def fit_curve(C):
    """The calibration curve, two ways.

    A weighted log-linear fit of log c on log(K/n) is reported because its
    slope is the quotable summary of the mechanism -- the widening a pair
    needs grows with its register's cardinality relative to its training set.
    It is NOT what the corpus is calibrated with, for a reason worth stating:
    the fit sits BELOW the measured factor at the small ratios, so using it
    would under-correct exactly the pairs whose bands are already the
    narrowest.  Under-correcting is the anti-conservative direction and is the
    error this whole exercise exists to remove.

    The curve applied to the corpus is therefore an ISOTONIC (monotone)
    regression through the measured factors, weighted the same way.  It
    honours every cell's own measurement, it cannot fall below one, and it is
    monotone by construction rather than by assumption -- which is the only
    shape assumption the mechanism licenses.  Outside the plane's range it
    holds the nearest endpoint rather than extrapolating a power law.
    """
    from sklearn.isotonic import IsotonicRegression
    C = C[C.c > 0].sort_values("Kn").copy()
    x = np.log(C.Kn.values)
    y = np.log(C.c.values)
    sd = (np.log(C.c_hi.values) - np.log(C.c_lo.values)) / (2 * 1.959964)
    w = 1.0 / np.maximum(sd, 1e-6) ** 2
    X = np.column_stack([np.ones_like(x), x])
    WX = X * w[:, None]
    beta = np.linalg.solve(X.T @ WX, WX.T @ y)
    resid = y - X @ beta
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ WX)))

    iso = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(
        x, y, sample_weight=w)

    def c_of(kn):
        #  atleast_1d because sklearn's isotonic refuses a scalar, and a
        #  caller asking for one pair's factor is the common case
        kn = np.atleast_1d(np.asarray(kn, float))
        out = np.maximum(1.0, np.exp(iso.predict(
            np.log(np.maximum(kn, 1e-6)))))
        return out if out.size > 1 else float(out[0])

    return beta, se, resid, c_of


# --------------------------------------------------------------------------
def apply_to_corpus(c_of, scale=1.0, suffix=""):
    """Relabel every whole-surface cell under the calibrated critical value
    and recompute the regions and rho.

    `scale` multiplies the calibration factor, which is how the sensitivity
    of every downstream count to the calibration itself is measured: at
    scale 0 the factor is 1 and the nominal band is recovered, and at the
    upper end of each cell's Monte Carlo interval the correction is as large
    as the plane supports.  A conclusion that survives both ends is a
    conclusion the calibration is not carrying.
    """
    import s21_bands as S21
    B = pd.read_csv(RESULTS / "s21_bands.csv.gz")
    #  K/n comes from the surface itself, by the same expression the
    #  denominator table prints, so the two cannot disagree.
    SU = S.read_results("s01_surface.csv", usecols=["log", "target", "card_f",
                                                    "n", "n_test"])
    per = (SU.groupby(["log", "target"]).first().reset_index())
    kn = {(r.log, r.target): float(r.card_f) / float(r.n - r.n_test)
          for r in per.itertuples()}
    W = B[B.family == "whole-surface"].copy()
    W["Kn"] = [kn.get((l, t), np.nan) for l, t in zip(W.log, W.target)]
    W["c"] = np.maximum(1.0, np.asarray(c_of(W.Kn.values), float) * scale)
    W["cal_lo"] = W.centre - W.c * W.q_hi * W.se
    W["cal_hi"] = W.centre + W.c * W.q_hi * W.se
    rows = []
    for (lg, tg), sub in W.groupby(["log", "target"]):
        nom = sub.apply(lambda r: S21.label_of(r.cons_lo, r.cons_hi), axis=1)
        cal = sub.apply(lambda r: S21.label_of(r.cal_lo, r.cal_hi), axis=1)
        rn, nbn, nhn, nun = S21.region_of(nom)
        rc, nbc, nhc, nuc = S21.region_of(cal)
        n = len(sub)
        rows.append(dict(
            log=lg, target=tg, cells=n, k_over_n=float(sub.Kn.iloc[0]),
            c=float(sub.c.iloc[0]), q=float(sub.q_hi.iloc[0]),
            q_calibrated=float(sub.c.iloc[0] * sub.q_hi.iloc[0]),
            beneficial=nbn, harmful=nhn, unresolved=nun,
            rho=(nbn - nhn) / float(n), region=rn,
            beneficial_cal=nbc, harmful_cal=nhc, unresolved_cal=nuc,
            rho_calibrated=(nbc - nhc) / float(n), region_calibrated=rc,
            changed=bool(rn != rc)))
    return pd.DataFrame(rows).sort_values(["log", "target"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--serial", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s33  A COVERAGE-CALIBRATED CRITICAL VALUE")
    print("=" * 92)
    cells = list(PLANE)
    print("  %d cells x %d replicates x %d refits = %s fits"
          % (len(cells), a.reps, N_BOOT,
             format(len(cells) * a.reps * (N_BOOT + 1) * 2, ",")))
    for (w, n, K) in cells:
        print("     %-8s n=%-5d K=%-5d  K/n=%.4f" % (w, n, K, K / n))
    if a.plan:
        return

    path = RESULTS / "s33_replicates.csv.gz"
    if a.reuse and path.exists():
        R = pd.read_csv(path)
        print("  reusing %d replicates" % len(R))
    else:
        tasks = [(w, n, K, r) for (w, n, K) in cells for r in range(a.reps)]
        out = []
        if a.serial:
            for t in tasks:
                v = one_rep(t)
                if v:
                    out.append(v)
        else:
            import multiprocessing as mp
            done = 0
            with mp.Pool(processes=min(12,
                                       max(1, (os.cpu_count() or 4) - 2))) as p:
                for v in p.imap_unordered(one_rep, tasks, chunksize=8):
                    done += 1
                    if v:
                        out.append(v)
                    if done % 500 == 0:
                        print("    %d/%d  %.0fs" % (done, len(tasks),
                                                    time.time() - t0),
                              flush=True)
        R = pd.DataFrame(out)
        R.to_csv(path, index=False, compression="gzip")
    print("  %d replicates in %.0fs" % (len(R), time.time() - t0), flush=True)

    LIM = limits(cells)
    rows = []
    for (w, n, K), sub in R.groupby(["world", "n_train", "K"]):
        f = factor(sub, LIM[(w, n, K)], seed=int(K + n))
        if f is None:
            continue
        rows.append(dict(world=w, n_train=n, K=K, Kn=K / float(n),
                         truth=LIM[(w, n, K)], **f))
    C = pd.DataFrame(rows).sort_values("Kn")
    C.to_csv(RESULTS / "s33_cells.csv", index=False)
    print("\n" + C.to_string(index=False))

    beta, se, resid, c_of = fit_curve(C)
    C = C.sort_values("Kn")
    C = C.assign(c_applied=c_of(C.Kn.values),
                 c_loglinear=np.maximum(1.0, np.exp(
                     beta[0] + beta[1] * np.log(C.Kn.values))),
                 resid_log=resid)
    #  the applied curve must never sit below a cell's own measured factor by
    #  more than that factor's Monte Carlo error, or the calibration is
    #  under-correcting the cell it was measured on
    under = int((C.c_applied < C.c_lo - 1e-9).sum())
    if under:
        print("  WARNING: %d cells where the applied curve is below the "
              "measured factor's lower confidence limit" % under)
    C.to_csv(RESULTS / "s33_fit.csv", index=False)
    print("\n  log c = %.4f + %.4f log(K/n)   (se %.4f, %.4f)"
          % (beta[0], beta[1], se[0], se[1]))
    lin = C[C.world == "linear"]
    spa = C[C.world == "sparse"]
    world_gap = (float(spa.resid_log.mean() - lin.resid_log.mean())
                 if len(spa) and len(lin) else np.nan)
    print("  mean residual  linear %+.4f   sparse %+.4f   gap %+.4f"
          % (lin.resid_log.mean(),
             spa.resid_log.mean() if len(spa) else np.nan, world_gap))

    G = apply_to_corpus(c_of)
    G.to_csv(RESULTS / "s33_regions.csv", index=False)

    #  the sensitivity of every downstream count to the calibration itself.
    #  `scale` 0 recovers the nominal band; the upper scale widens every
    #  factor by the median relative half-width of its Monte Carlo interval,
    #  which is as far as the plane supports pushing it.
    up = float(np.median((C.c_hi - C.c) / C.c)) if len(C) else 0.0
    SENS = []
    for lab, sc in (("nominal (c = 1)", 0.0), ("calibrated", 1.0),
                    ("calibrated, upper Monte Carlo end", 1.0 + up)):
        g = apply_to_corpus(c_of, scale=sc)
        SENS.append(dict(
            setting=lab, scale=sc,
            resolved=int((g.beneficial_cal + g.harmful_cal).sum()),
            rho_median=float(g.rho_calibrated.median()),
            n_unresolved=int((g.region_calibrated == "unresolved").sum()),
            n_uniformly_beneficial=int(
                (g.region_calibrated == "uniformly beneficial").sum()),
            c_median=float(g.c.median())))
    SN = pd.DataFrame(SENS)
    SN.to_csv(RESULTS / "s33_sensitivity.csv", index=False)
    print("\n  SENSITIVITY OF THE COUNTS TO THE CALIBRATION ITSELF")
    print(SN.to_string(index=False))
    print("\n" + G[["log", "target", "k_over_n", "c", "q", "q_calibrated",
                    "rho", "rho_calibrated", "region", "region_calibrated",
                    "changed"]].to_string(index=False))

    facts = dict(
        n_cells=len(C), n_reps=a.reps, n_boot=N_BOOT,
        n_replicates=len(R),
        kn_min=float(C.Kn.min()), kn_max=float(C.Kn.max()),
        c_at_median_pair=float(c_of(float(G.k_over_n.median()))),
        c_intercept=float(np.exp(beta[0])), c_slope=float(beta[1]),
        c_slope_se=float(se[1]),
        world_residual_gap=world_gap,
        coverage_nominal_median=float(C.coverage_nominal.median()),
        n_regions_changed=int(G.changed.sum()),
        n_uniformly_beneficial_nominal=int(
            (G.region == "uniformly beneficial").sum()),
        n_uniformly_beneficial_calibrated=int(
            (G.region_calibrated == "uniformly beneficial").sum()),
        n_unresolved_nominal=int((G.region == "unresolved").sum()),
        n_unresolved_calibrated=int((G.region_calibrated == "unresolved").sum()),
        rho_median_nominal=float(G.rho.median()),
        rho_median_calibrated=float(G.rho_calibrated.median()),
        n_resolved_cells_nominal=int((G.beneficial + G.harmful).sum()),
        n_resolved_cells_calibrated=int(
            (G.beneficial_cal + G.harmful_cal).sum()),
        n_total_cells=int(G.cells.sum()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s33_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s33_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1:])

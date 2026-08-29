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
#: the bands the sensitivity ladder recomputes regions on (see main)
BANDS_PREFIX = "s48w"
SEED = 20260825

#: A cell is admitted to the plane only if the basic interval straddles its
#: own point estimate in at least this share of replicates.
#:
#: The guard used to be a COUNT --- at least thirty usable replicates --- and
#: that is the wrong shape of guard, for the reason the handoff's seventh rule
#: gives: the survivors of a filter are a SELECTED subset.  Where only seven
#: replicates in a hundred straddle, the ones that do are the ones whose
#: displacement happened to be small, and the factor computed on them is a
#: factor for a sample conditioned on the answer.  Two cells passed the count
#: guard on 34 and 39 replicates and returned c = 3074.7 and c = 0.86, one
#: absurd and one below one, and both would have entered the fit.
#:
#: The threshold is not load-bearing and the file prints why: the shares are
#: bimodal, every cell sitting either above 0.97 or below 0.08, so anything
#: between those two numbers admits and rejects the same cells.
STRADDLE_MIN = 0.90
REPS = 500
N_BOOT = 50

#  (world, n_train, K).  K/n spans 0.0025 to 0.500, which brackets every pair
#  in the corpus (0.001 to 0.324) with points inside the range rather than
#  three points and an extrapolation.
#
#  ROUND TWENTY-FIVE.  It bracketed the corpus in the RATIO and not in n.
#  Every cell ran at 2,000, 4,000 or 8,000 training rows while the corpus's
#  training halves run from about 500 to about 123,000, so three pairs of
#  nineteen sat inside the range the factor was measured on and sixteen were
#  extrapolations in n -- and Section 10.3 proves, in the same document, that
#  K/n alone does not determine coverage.  Every region label, every rho and
#  the headline inherit that.  Two blocks are added.
#
#  THE LADDER.  Three ratios held FIXED while n moves over two orders of
#  magnitude.  This is the design that identifies n-dependence at a fixed
#  ratio, which is the thing in doubt; the original plane could not, because
#  n and K/n moved together in it.
LADDER_RATIOS = (0.0125, 0.05, 0.125)
LADDER_N = (750, 2000, 8000, 50000)
#  THE ENDS.  Cells at and below the smallest training half in the corpus and
#  at the largest, so the applied factor is an interpolation in n for every
#  pair rather than an extrapolation for sixteen of them.
#  ROUND TWENTY-FIVE.  120,000 left ONE pair of the nineteen above the plane
#  -- BPIC19/duration, whose training half is 176,213 rows -- and one pair
#  outside is the same objection at one nineteenth the size.  The top cell is
#  above every pair in the corpus, so the factor is an interpolation in n for
#  all of them.
#  Two cells above every training half in the corpus, at the two ratio
#  regimes its two largest pairs occupy.  The first is defined and the second
#  is not, and that is the point: the estimator this file is built on needs
#  the basic interval to straddle its own point estimate, and past a crossing
#  in n it stops doing so.  Reporting the second as a measured absence is
#  worth more than leaving the plane silent above 50,000 rows.
ENDS = (("linear", 500, 50), ("linear", 500, 200),
        ("linear", 120000, 6000),
        ("linear", 180000, 200), ("linear", 180000, 2250))

PLANE = tuple(
    [("linear", n, k) for (n, k) in
     [(8000, 20), (4000, 20), (2000, 20),
      (8000, 100), (4000, 100), (2000, 100),
      (8000, 200), (4000, 200), (2000, 200),
      (8000, 400), (4000, 400), (2000, 400),
      (8000, 1000), (4000, 1000), (2000, 1000),
      (8000, 3019)]]
    + [("sparse", n, k) for (n, k) in
       [(8000, 100), (4000, 200), (2000, 200), (4000, 1000)]]
    + [("linear", n, max(10, int(round(r * n))))
       for r in LADDER_RATIOS for n in LADDER_N]
    + list(ENDS))
#  the ladder repeats cells the original plane already carries, and a repeated
#  cell would be averaged with itself rather than replicated
PLANE = tuple(dict.fromkeys(PLANE))

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
    if len(V) < 30 or ok.mean() < STRADDLE_MIN:
        return dict(n=len(V), n_offered=int(len(ok)),
                    share_straddling=float(ok.mean()), c=np.nan,
                    c_lo=np.nan, c_hi=np.nan, coverage_nominal=np.nan,
                    coverage_nominal_se=np.nan, median_r=np.nan)
    #  ROUND TWENTY-FIVE.  This guard used to drop a cell in silence.  It
    #  fires when the basic interval does not STRADDLE its own point estimate
    #  --- when the bootstrap displacement exceeds the interval's half-width,
    #  so that pivoting carries both endpoints to the same side of V --- and
    #  the widening this file estimates is a widening ABOUT V, which is not
    #  defined there.  The plane lost two of thirty-one cells to it, both at
    #  the top end in n, and the facts said only that there were twenty-nine.
    #  The share is now returned so that the loss is a measurement.
    r = np.maximum((V - truth) / L, (truth - V) / U)
    c = float(np.quantile(r, 1 - alpha))
    rng = np.random.default_rng(seed)
    bs = [float(np.quantile(r[rng.integers(0, len(r), len(r))], 1 - alpha))
          for _ in range(n_boot)]
    cov_nominal = float(np.mean(r <= 1.0))
    return dict(n=len(r), n_offered=int(len(ok)), share_straddling=float(
        ok.mean()), c=c, c_lo=float(np.quantile(bs, 0.025)),
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

    #  ROUND TWENTY-FIVE.  Does n carry anything once K/n is in the fit?
    #  Section 10.3 says K/n is not sufficient and the plane could not test it
    #  until the ladder existed, because n and K/n moved together.  A second
    #  weighted fit adds log n; its coefficient, standard error and the change
    #  in weighted residual sum of squares are reported so that the answer is
    #  a measurement rather than a sentence.
    ln = np.log(C.n_train.values.astype(float))
    X2 = np.column_stack([np.ones_like(x), x, ln])
    WX2 = X2 * w[:, None]
    try:
        beta2 = np.linalg.solve(X2.T @ WX2, WX2.T @ y)
        se2 = np.sqrt(np.diag(np.linalg.inv(X2.T @ WX2)))
        r1 = float(np.sum(w * (y - X @ beta) ** 2))
        r2 = float(np.sum(w * (y - X2 @ beta2) ** 2))
        #  and what the two-covariate fit would be worth AS AN APPLIED
        #  CURVE, which is the question section 6.4 asks: not whether log n
        #  belongs in a fit, but whether putting it there gives a better
        #  object to widen the corpus's bands with.  The criterion is the one
        #  the isotonic curve was adopted under -- how often the curve sits
        #  below a cell's own measured factor, which is the
        #  anti-conservative direction.
        riso = float(np.sum(w * (iso.predict(x) - y) ** 2))
        c1 = np.maximum(1.0, np.exp(X @ beta))
        c2c = np.maximum(1.0, np.exp(X2 @ beta2))
        ciso = np.maximum(1.0, np.exp(iso.predict(x)))
        lo_c = C.c_lo.values
        ndep = dict(beta_logn=float(beta2[2]), se_logn=float(se2[2]),
                    t_logn=float(beta2[2] / se2[2]) if se2[2] else np.nan,
                    wrss_ratio=r2 / r1 if r1 else np.nan,
                    beta_logkn_with_n=float(beta2[1]),
                    wrss_ratio_only=r1, wrss_with_n=r2, wrss_isotonic=riso,
                    under_ratio_only=int((c1 < lo_c - 1e-9).sum()),
                    under_with_n=int((c2c < lo_c - 1e-9).sum()),
                    under_isotonic=int((ciso < lo_c - 1e-9).sum()))
    except np.linalg.LinAlgError:
        ndep = dict(beta_logn=np.nan, se_logn=np.nan, t_logn=np.nan,
                    wrss_ratio=np.nan, beta_logkn_with_n=np.nan,
                    wrss_ratio_only=np.nan, wrss_with_n=np.nan,
                    wrss_isotonic=np.nan, under_ratio_only=0,
                    under_with_n=0, under_isotonic=0)
    return beta, se, resid, c_of, ndep


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
    #  ROUND TWENTY-SEVEN.  This filename was fixed, so the sensitivity
    #  ladder went on being computed on the RETIRED inference surface after
    #  the article moved to another one -- and its "nominal" rung, which is
    #  by construction the article's own reported band, disagreed with the
    #  article's own resolved count.  The plane above is legitimately fitted
    #  where it was fitted; the REGIONS are not, and must be recomputed on
    #  the bands the article prints.
    B = pd.read_csv(RESULTS / ("%s_bands.csv.gz" % BANDS_PREFIX))
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
    ap.add_argument("--resume", action="store_true",
                    help="keep the replicates already on disk and simulate "
                         "only the cells the plane has gained since")
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--bands-prefix", default="s48w",
                    help="the bands prefix the sensitivity ladder's regions "
                         "are recomputed on; the plane itself is unaffected")
    a = ap.parse_args(argv)
    global BANDS_PREFIX
    BANDS_PREFIX = a.bands_prefix
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
        #  ROUND TWENTY-FIVE.  Widening the plane in n is the whole point of
        #  this round's item B, and a plane that gains one cell should cost
        #  one cell and not the forty-five minutes the other thirty take.
        #  A cell counts as done when it already carries the full replicate
        #  count; anything short is redone, so a run interrupted inside a
        #  cell cannot leave a half-measured factor behind.
        have, keep = {}, None
        if a.resume and path.exists():
            keep = pd.read_csv(path)
            have = {k: int(v) for k, v in
                    keep.groupby(["world", "n_train", "K"]).size().items()}
        todo = [c for c in cells if have.get(c, 0) < a.reps]
        if a.resume:
            print("  resuming: %d of %d cells already complete, %d to run"
                  % (len(cells) - len(todo), len(cells), len(todo)))
            for c in todo:
                print("     to run   %-8s n=%-6d K=%-5d" % c)
        tasks = [(w, n, K, r) for (w, n, K) in todo for r in range(a.reps)]
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
        if keep is not None and len(keep):
            done_cells = {c for c in cells if have.get(c, 0) >= a.reps}
            kept = keep[[(w, n, K) in done_cells for w, n, K
                         in zip(keep.world, keep.n_train, keep.K)]]
            R = pd.concat([kept, R], ignore_index=True) if len(R) else kept
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
    #  the cells where the factor is not defined, named rather than absent
    UND = C[~np.isfinite(C.c)]
    if len(UND):
        print("\n  THE FACTOR IS NOT DEFINED ON %d OF %d CELLS: the basic "
              "interval does not straddle its own point estimate there"
              % (len(UND), len(C)))
        print(UND[["world", "n_train", "K", "Kn", "share_straddling"]]
              .to_string(index=False, float_format=lambda x: "%.4f" % x))
    #  the threshold's own sensitivity, printed rather than asserted: the
    #  largest share among the rejected cells and the smallest among the
    #  admitted ones.  Any threshold between them gives the same plane.
    lo_gap = float(UND.share_straddling.max()) if len(UND) else float("nan")
    hi_gap = float(C[np.isfinite(C.c)].share_straddling.min())
    print("  admission at %.2f is not load-bearing: the rejected cells reach "
          "%.3f and the admitted ones start at %.3f"
          % (STRADDLE_MIN, lo_gap, hi_gap))
    C = C[np.isfinite(C.c)].copy()
    print("\n" + C.to_string(index=False))

    ALL = pd.DataFrame(rows)
    ALL["Kn"] = ALL.K / ALL.n_train.astype(float)
    #  the crossing, along whichever ladder ratio carries the most sample
    #  sizes and actually crosses
    STRAD = None
    for r_ in sorted(LADDER_RATIOS, reverse=True):
        s_ = ALL[(ALL.world == "linear")
                 & (np.abs(np.log(ALL.Kn / r_)) < 0.06)].sort_values("n_train")
        below = s_[s_.share_straddling < 0.5]
        full = s_[s_.share_straddling >= 0.99]
        if len(below) and len(full):
            STRAD = dict(ratio=r_, n_all=int(full.n_train.max()),
                         n_half=int(below.n_train.min()),
                         share_at_half=float(below.share_straddling.iloc[0]))
            break
    beta, se, resid, c_of, ndep = fit_curve(C)
    C = C.sort_values("Kn")
    C = C.assign(c_applied=c_of(C.Kn.values),
                 c_loglinear=np.maximum(1.0, np.exp(
                     beta[0] + beta[1] * np.log(C.Kn.values))),
                 resid_log=resid)
    #  the applied curve must never sit below a cell's own measured factor by
    #  more than that factor's Monte Carlo error, or the calibration is
    #  under-correcting the cell it was measured on
    under = int((C.c_applied < C.c_lo - 1e-9).sum())
    shortfall = float(np.max(C.c - C.c_applied))
    if under:
        print("  WARNING: %d cells where the applied curve is below the "
              "measured factor's lower confidence limit, worst shortfall "
              "%+.3f" % (under, shortfall))
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
    print("  adding log n:  coefficient %+.4f (se %.4f, t %+.1f), weighted "
          "residual sum of squares x%.3f"
          % (ndep["beta_logn"], ndep["se_logn"], ndep["t_logn"],
             ndep["wrss_ratio"]))

    #  THE LADDER, read directly: at each ratio the plane holds fixed, how far
    #  apart are the measured factors across n, and how far apart are they in
    #  units of their own Monte Carlo error?  A fit can hide a spread; this
    #  cannot.
    lad = []
    for r_ in LADDER_RATIOS:
        s_ = C[(C.world == "linear")
               & (np.abs(np.log(C.Kn / r_)) < 0.06)].sort_values("n_train")
        if len(s_) < 2:
            continue
        lo_, hi_ = s_.iloc[0], s_.iloc[-1]
        sd_ = np.sqrt(((lo_.c_hi - lo_.c_lo) / (2 * 1.959964)) ** 2
                      + ((hi_.c_hi - hi_.c_lo) / (2 * 1.959964)) ** 2)
        lad.append(dict(ratio=r_, n_lo=int(lo_.n_train), n_hi=int(hi_.n_train),
                        c_lo_n=float(lo_.c), c_hi_n=float(hi_.c),
                        n_cells=int(len(s_)),
                        spread=float(hi_.c - lo_.c),
                        spread_se=float((hi_.c - lo_.c) / sd_) if sd_ else
                        np.nan,
                        #  the same comparison in the units section 10.3
                        #  states it in: what holding the ratio fixed and
                        #  moving n does to COVERAGE, not to the factor
                        cov_lo_n=float(lo_.coverage_nominal),
                        cov_hi_n=float(hi_.coverage_nominal),
                        cov_spread=float(abs(hi_.coverage_nominal
                                             - lo_.coverage_nominal))))
    LAD = pd.DataFrame(lad)
    LAD.to_csv(RESULTS / "s33_ladder_n.csv", index=False)
    if len(LAD):
        print("\n  THE LADDER: the same ratio, n moved over two orders")
        print(LAD.to_string(index=False))

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
        n_train_min=int(C.n_train.min()), n_train_max=int(C.n_train.max()),
        beta_logn=ndep["beta_logn"], se_logn=ndep["se_logn"],
        t_logn=ndep["t_logn"], wrss_ratio=ndep["wrss_ratio"],
        wrss_ratio_only=ndep["wrss_ratio_only"],
        wrss_with_n=ndep["wrss_with_n"], wrss_isotonic=ndep["wrss_isotonic"],
        under_ratio_only=ndep["under_ratio_only"],
        under_with_n=ndep["under_with_n"],
        under_isotonic=ndep["under_isotonic"],
        n_ladder_ratios=int(len(LAD)),
        ladder_spread_max=float(LAD.spread.abs().max()) if len(LAD) else
        np.nan,
        ladder_spread_se_max=float(LAD.spread_se.abs().max()) if len(LAD)
        else np.nan,
        ladder_coverage_spread_max=float(LAD.cov_spread.max()) if len(LAD)
        else np.nan,
        n_cells_undefined=int(len(UND)), n_cells_offered=int(len(UND) + len(C)),
        straddle_min=STRADDLE_MIN,
        #  what the APPLIED curve, a function of the ratio alone, leaves on
        #  the table now that the plane has the leverage in n to see it
        n_cells_under_applied=under, max_shortfall_applied=shortfall,
        straddle_gap_lo=lo_gap, straddle_gap_hi=hi_gap,
        #  THE CROSSING, AT A FIXED RATIO.  The largest n at which the basic
        #  interval still straddles its own point estimate in every replicate,
        #  and the smallest at which it does in fewer than half.  Both are
        #  taken ALONG ONE LADDER RATIO and not over the whole plane: the
        #  straddling depends on n and on K/n together, so a maximum over the
        #  plane would be attained at whatever cell happens to carry the
        #  smallest ratio and would say nothing about n.  The ratio is the
        #  one the ladder runs at the most sample sizes.
        straddle_ratio=float(STRAD["ratio"]) if STRAD else np.nan,
        n_straddle_all_max=int(STRAD["n_all"]) if STRAD else 0,
        n_straddle_half_min=int(STRAD["n_half"]) if STRAD else 0,
        share_straddle_at_half=float(STRAD["share_at_half"]) if STRAD
        else np.nan,
        #  the same thing over the whole plane at a FIXED K, which is the
        #  comparison section 10.3 makes and states as a spelled-out number
        fixedk_coverage_spread=float(
            C.groupby("K").coverage_nominal.agg(lambda v: v.max() - v.min())
            .max()) if len(C) else np.nan,
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

"""s31 -- THE SIMULATION AT THE SIZE THE METHOD CLAIM NEEDS.

Round twenty.  The developmental review's P1.1 lists nine demands on the
bootstrap validation.  s10_simulation2.py met four of them; this file meets
the rest, and supersedes s10 for every coverage number the paper prints.

  1  at least 1000 replicates per world              -- EXPERIMENT `core`
  2  Monte Carlo standard errors for coverage,
     bias and width                                  -- every row carries one
  3  the sparse world expanded toward the observed
     3019-level regime                               -- EXPERIMENT `grid`
  4  sample size and register cardinality varied
     JOINTLY                                         -- EXPERIMENT `grid`
  5  at least three block lengths around n^(1/3)     -- EXPERIMENT `block`
  6  six constructions compared, including
     m-out-of-n in the sparse regime                 -- every experiment
  7  coverage for BOTH the fitted-pipeline limit and
     the oracle target                               -- s10 did this; kept
  8  the stationarity and mixing assumptions stated  -- prose, Section 5
  9  the consequence of a fixed split point          -- prose, Section 9

WHY IT IMPORTS s10 RATHER THAN COPYING IT
The worlds, the enumerated truth and the observed-population marginalisation
are the delicate part, and one of them was wrong for two rounds.  A copy would
let the two drift; an import cannot.  s10 is unchanged except that
`world_spec` and the row draw now take an optional cardinality, which every
existing caller leaves at its default.

THE SIX CONSTRUCTIONS
  naive_pct     resample the TEST rows, models fixed, percentile
  naive_basic   the same draws, basic (pivotal)
  naive_bc      the same draws, bias-corrected percentile
  nested_pct    block-resample the training half, REFIT, percentile
  nested_basic  the same draws, basic -- what the paper reports
  nested_bc     the same draws, bias-corrected percentile
  nested_mofn   m-out-of-n subsampling on the same nested design, m = n^(2/3),
                scaled by sqrt(m/n); the construction that is consistent
                under a sparse register even when the n-out-of-n bootstrap
                is not

    python s31_simboost.py --plan                 # cost, no fits
    python s31_simboost.py --only core --reps 1000
    python s31_simboost.py --only grid
    python s31_simboost.py --only block
    python s31_simboost.py --resume               # keep finished cells

Outputs: results/s31_replicates_<exp>.csv.gz, s31_coverage.csv, s31_facts.csv

A run at fewer than the declared replicate counts writes `s31_smoke_*`
instead, because nothing the manuscript reads should be writable by a smoke
test -- which is not a hypothetical: the two-replicate smoke run of this file
wrote s31_facts.csv and make_numbers printed a coverage of 100% at
\\nSimReps = 2 until the files were removed by hand.
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
import s10_simulation2 as SIM  # noqa: E402

SEED = 20260824
ALPHA = 0.05

#  the core experiment: every world, at the replicate count the review asks
#  for.  N_BOOT is the number of REFITS inside one replicate and is the whole
#  cost of the file.
REPS_CORE = 1000
N_BOOT = 100
N_BOOT_M = 50             # the extra draws the m-out-of-n interval needs

#  the auxiliary experiments trade replicates for coverage of the (n, K)
#  plane.  Their Monte Carlo standard error is larger and is printed with
#  every number they produce, so the resolution is never implicit.
REPS_GRID = 150
REPS_BLOCK = 250
N_BOOT_AUX = 50

#  P1.1.4: n and K varied jointly, not one at a time.  The last cell is the
#  observed regime -- the case study's register carries 3019 levels.
GRID = tuple([(n, k) for n in (2000, 4000, 8000) for k in (20, 200, 1000)]
             + [(8000, 3019)])

#  P1.1.5: three block lengths around n^(1/3), on the world where the
#  construction is well behaved and on the one where it is not.
BLOCK_WORLDS = ("linear", "sparse")
BLOCK_MULT = (0.5, 1.0, 2.0)


# --------------------------------------------------------------------------
def block_len(n, mult=1.0):
    """The rule of thumb, scaled.  max(4, .) so the halved length on a small
    sample is still a block."""
    return max(4, int(round(mult * (n ** (1.0 / 3.0)))))


def intervals_from(a, v, alpha=ALPHA, scale=1.0):
    """The four constructions available from one set of draws.

    `scale` is sqrt(m/n) for a subsample of size m and 1 for a full
    resample.  Under subsampling the draws estimate the distribution of
    sqrt(m)(V*-V) and the interval must be shrunk by sqrt(m/n) before it is
    pivoted, which is the only place the two differ.
    """
    from scipy.stats import norm
    if len(a) < 10:
        nan = (np.nan, np.nan)
        return dict(pct=nan, basic=nan, bc=nan, shift=np.nan)
    qa = float(np.percentile(a, 100 * alpha / 2))
    qb = float(np.percentile(a, 100 * (1 - alpha / 2)))
    #  basic: pivot the shift out.  With scale != 1 the deviations are
    #  rescaled first, which is the subsampling correction.
    basic = (v - scale * (qb - v), v - scale * (qa - v))
    share = float(np.mean(a < v))
    share = min(max(share, 1.0 / (2 * len(a))), 1 - 1.0 / (2 * len(a)))
    z0 = float(norm.ppf(share))
    za, zb = norm.ppf(alpha / 2), norm.ppf(1 - alpha / 2)
    pa = float(norm.cdf(2 * z0 + za)) * 100
    pb = float(norm.cdf(2 * z0 + zb)) * 100
    return dict(pct=(qa, qb), basic=basic,
                bc=(float(np.percentile(a, pa)),
                    float(np.percentile(a, pb))),
                shift=float(np.median(a)) - v)


# --------------------------------------------------------------------------
def one_rep(task):
    """One replicate of one CELL.  A cell is (world, K, n_train, n_test,
    block multiplier, whether to run m-out-of-n, n_boot).

    Everything about the world -- its truth, its observed population, its
    generator -- comes from s10.
    """
    (world, K, n_tr, n_te, mult, do_mofn, n_boot, rep) = task
    from sklearn.metrics import roc_auc_score

    rng = np.random.default_rng(SEED + 1013 * rep + SIM.WORLD_SEED[world]
                                + 7 * K + 3 * n_tr + int(100 * mult))
    W = SIM.world_spec(world, np.random.default_rng(
        SIM.SEED + SIM.WORLD_SEED[world]), k_override=K)
    T = SIM.truth(W)

    tr = SIM.draw(W, n_tr, 1, rng)
    te = SIM.draw(W, n_te, 2, rng)
    yte = te["_y"].values
    if len(np.unique(yte)) < 2:
        return None
    p0 = SIM.fit_scores(tr, te, ["b", "g"])
    p1 = SIM.fit_scores(tr, te, ["b", "g", "f"])
    V_hat = roc_auc_score(yte, p1) - roc_auc_score(yte, p0)

    ell_tr, ell_te = block_len(n_tr, mult), block_len(n_te, mult)

    #  the fixed-model arm: resample the test rows only
    nb = []
    for b in range(n_boot):
        r = np.random.default_rng(SEED + 7919 * b + rep + 13 * K)
        i = r.integers(0, len(yte), len(yte))
        if len(np.unique(yte[i])) < 2:
            continue
        nb.append(roc_auc_score(yte[i], p1[i]) - roc_auc_score(yte[i], p0[i]))
    nb = np.array(nb, float)

    #  the nested arm: block-resample the training half, REFIT, evaluate on a
    #  block resample of the test half
    nn = []
    for b in range(n_boot):
        r = np.random.default_rng(SEED + 104729 * b + rep + 13 * K)
        tb = tr.iloc[S.block_indices(len(tr), r, ell=ell_tr)]
        eb = te.iloc[S.block_indices(len(te), r, ell=ell_te)]
        yb = eb["_y"].values
        if len(np.unique(yb)) < 2:
            continue
        q0 = SIM.fit_scores(tb, eb, ["b", "g"])
        q1 = SIM.fit_scores(tb, eb, ["b", "g", "f"])
        nn.append(roc_auc_score(yb, q1) - roc_auc_score(yb, q0))
    nn = np.array(nn, float)

    N = intervals_from(nb, V_hat)
    X = intervals_from(nn, V_hat)

    out = dict(world=world, K=K, n_train=n_tr, n_test=n_te, block_mult=mult,
               ell_train=ell_tr, rep=rep, V_hat=V_hat,
               V_oracle=T["V_oracle"], auc_base=T["auc_base"],
               naive_shift=N["shift"], nested_shift=X["shift"])
    for tag, D in (("naive", N), ("nested", X)):
        for kind in ("pct", "basic", "bc"):
            lo, hi = D[kind]
            out["%s_%s_lo" % (tag, kind)] = lo
            out["%s_%s_hi" % (tag, kind)] = hi
            out["%s_%s_width" % (tag, kind)] = hi - lo

    #  m-out-of-n: the same nested design at a subsample size m, scaled.
    if do_mofn:
        m_tr = max(200, int(round(n_tr ** (2.0 / 3.0))))
        m_te = max(200, int(round(n_te ** (2.0 / 3.0))))
        em_tr, em_te = block_len(m_tr, mult), block_len(m_te, mult)
        mm = []
        for b in range(N_BOOT_M):
            r = np.random.default_rng(SEED + 15485863 * b + rep + 13 * K)
            i_tr = S.block_indices(m_tr, r, ell=em_tr) % len(tr)
            i_te = S.block_indices(m_te, r, ell=em_te) % len(te)
            tb, eb = tr.iloc[i_tr], te.iloc[i_te]
            yb = eb["_y"].values
            if len(np.unique(yb)) < 2:
                continue
            q0 = SIM.fit_scores(tb, eb, ["b", "g"])
            q1 = SIM.fit_scores(tb, eb, ["b", "g", "f"])
            mm.append(roc_auc_score(yb, q1) - roc_auc_score(yb, q0))
        mm = np.array(mm, float)
        M = intervals_from(mm, V_hat, scale=np.sqrt(m_tr / float(n_tr)))
        lo, hi = M["basic"]
        out["nested_mofn_lo"], out["nested_mofn_hi"] = lo, hi
        out["nested_mofn_width"] = hi - lo
        out["mofn_m"] = m_tr
    return out


# --------------------------------------------------------------------------
def tasks_for(exp, reps):
    """The cells of one experiment, as a flat task list."""
    T = []
    if exp == "core":
        for w in SIM.WORLDS:
            K = 200 if w == "sparse" else 20
            for r in range(reps):
                #  m-out-of-n is priced only where the review asks for it:
                #  the sparse regime, plus one well-behaved and one
                #  misspecified world so the comparison has a control.
                do = w in ("linear", "nonlinear", "sparse")
                T.append((w, K, 4000, 2000, 1.0, do, N_BOOT, r))
    elif exp == "grid":
        for (n, k) in GRID:
            for r in range(reps):
                T.append(("linear", k, n, n // 2, 1.0, False, N_BOOT_AUX, r))
    elif exp == "block":
        for w in BLOCK_WORLDS:
            K = 200 if w == "sparse" else 20
            for mult in BLOCK_MULT:
                for r in range(reps):
                    T.append((w, K, 4000, 2000, mult, False, N_BOOT_AUX, r))
    else:
        raise SystemExit("unknown experiment %r" % exp)
    return T


def limits_for(exp, tasks):
    """V_limit, once per distinct (world, K, n_train).  The limit is a
    property of the world and the pipeline, not of a replicate, and fitting
    it once per cell rather than once per replicate is most of why the
    auxiliary experiments are affordable."""
    keys = sorted({(w, K, n) for (w, K, n, _, _, _, _, _) in tasks})
    out = {}
    for (w, K, n) in keys:
        W = SIM.world_spec(w, np.random.default_rng(
            SIM.SEED + SIM.WORLD_SEED[w]), k_override=K)
        out[(w, K, n)] = SIM.limit_estimand(
            W, np.random.default_rng(SEED + 7 + K))
        print("  limit  %-11s K=%-5d n=%-5d  V_limit %+.4f"
              % (w, K, n, out[(w, K, n)]), flush=True)
    return out


def summarise(R):
    """Coverage, bias, width and the Monte Carlo standard error of each, per
    cell and construction.  P1.1.2 asks for the standard errors and they are
    the reason this table is worth printing: at 1000 replicates a coverage is
    resolved to about 0.7 percentage points, and differences below that are
    not differences."""
    kinds = [c[:-3] for c in R.columns if c.endswith("_lo")]
    rows = []
    #  `experiment` is IN the key, and has to be.  The block experiment
    #  carries a multiplier of 1.0 on the linear and sparse worlds as its own
    #  control, at 4000 rows and the same cardinality as the core -- so
    #  without it those rows would be pooled with the core's, mixing 250
    #  replicates at 50 refits into 1000 replicates at 100 and reporting the
    #  result as one coverage estimate.
    grp = ["experiment", "world", "K", "n_train", "block_mult"]
    for key, sub in R.groupby(grp):
        for target in ("V_limit", "V_oracle"):
            for kind in kinds:
                lo, hi = sub[kind + "_lo"], sub[kind + "_hi"]
                ok = ((lo <= sub[target]) & (sub[target] <= hi))
                ok = ok[lo.notna() & hi.notna()]
                n = int(ok.sum() + (~ok).sum())
                if n == 0:
                    continue
                cov = float(ok.mean())
                err = (sub.V_hat - sub[target]).dropna()
                w = sub[kind + "_width"].dropna()
                rows.append(dict(
                    zip(grp, key if isinstance(key, tuple) else (key,)))
                    | dict(
                    estimand=target, interval=kind, n=n, coverage=cov,
                    coverage_se=float(np.sqrt(max(cov * (1 - cov), 1e-12) / n)),
                    bias=float(err.mean()),
                    bias_se=float(err.std(ddof=1) / np.sqrt(max(len(err), 1))),
                    mean_width=float(w.mean()),
                    width_se=float(w.std(ddof=1) / np.sqrt(max(len(w), 1))),
                    rmse=float(np.sqrt((err ** 2).mean())),
                    truth=float(sub[target].iloc[0])))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="core,block,grid",
                    help="comma-separated: core, grid, block.  The order is "
                         "the order they run in, and it is deliberate: the "
                         "core experiment is the one the review requires, "
                         "the grid is the one that costs the most per "
                         "replicate, and a run that is cut short should have "
                         "lost the grid rather than the core.")
    ap.add_argument("--reps", type=int, default=0,
                    help="override the replicate count of every experiment")
    ap.add_argument("--procs", type=int, default=0)
    ap.add_argument("--plan", action="store_true",
                    help="print the fit count and exit")
    ap.add_argument("--resume", action="store_true",
                    help="skip an experiment whose replicate file exists")
    a = ap.parse_args(argv)
    t0 = time.time()
    exps = [e.strip() for e in a.only.split(",") if e.strip()]
    default_reps = dict(core=REPS_CORE, grid=REPS_GRID, block=REPS_BLOCK)

    if a.plan:
        #  the fixed-model arm SCORES resampled rows and does not refit, so
        #  it costs no fits.  Counting it -- which the first version of this
        #  planner did -- doubles the estimate and would have priced the file
        #  out of the session it was written in.
        tot = 0
        for e in exps:
            T = tasks_for(e, a.reps or default_reps[e])
            f = sum(2 + 2 * t[6] + (2 * N_BOOT_M if t[5] else 0) for t in T)
            print("  %-6s %6d replicates  %10d pipeline fits" % (e, len(T), f))
            tot += f
        ref = 6 * 200 * (2 + 2 * 100)
        print("  total %d fits; s10 ran %d fits in %d s (%.0f fits/s), so "
              "this is about %.1f h at the same cost per fit"
              % (tot, ref, 2707, ref / 2707.0, tot / (ref / 2707.0) / 3600.0))
        return

    print("=" * 92)
    print("s31  THE SIMULATION AT THE SIZE THE METHOD CLAIM NEEDS")
    print("=" * 92)
    SIM.check_observed_population()

    frames = []
    for e in exps:
        path = RESULTS / ("s31_replicates_%s.csv.gz" % e)
        if a.reps and a.reps < default_reps[e]:
            path = RESULTS / ("s31_smoke_replicates_%s.csv.gz" % e)
        if a.resume and path.exists():
            print("  %-6s already done, kept" % e)
            frames.append(pd.read_csv(path))
            continue
        reps = a.reps or default_reps[e]
        T = tasks_for(e, reps)
        LIM = limits_for(e, T)
        print("  %-6s %d replicates over %d cells"
              % (e, len(T), len({(t[0], t[1], t[2], t[4]) for t in T})),
              flush=True)
        out = []
        part = RESULTS / ("s31_partial_%s.csv.gz" % e)
        import multiprocessing as mp
        nproc = a.procs or min(12, max(1, (os.cpu_count() or 4) - 2))
        with mp.Pool(processes=nproc) as pool:
            for i, r in enumerate(pool.imap_unordered(one_rep, T,
                                                      chunksize=4)):
                if r:
                    out.append(r)
                if (i + 1) % 250 == 0:
                    print("    %s %d/%d  %.0fs"
                          % (e, i + 1, len(T), time.time() - t0), flush=True)
                #  a checkpoint, because this file runs for hours and a run
                #  that is interrupted at 80% should not be worth nothing.
                #  The partial file is never read by the paper; it exists so
                #  that a resumed run can be assembled by hand if it has to
                #  be, and it is deleted when the real file is written.
                if (i + 1) % 500 == 0 and out:
                    pd.DataFrame(out).to_csv(part, index=False,
                                             compression="gzip")
        R = pd.DataFrame(out)
        if part.exists():
            part.unlink()
        R["V_limit"] = [LIM[(w, k, n)] for w, k, n
                        in zip(R.world, R.K, R.n_train)]
        R["experiment"] = e
        R.to_csv(path, index=False, compression="gzip")
        print("  %-6s -> %s  (%d rows, %.0fs)"
              % (e, path.name, len(R), time.time() - t0), flush=True)
        frames.append(R)

    R = pd.concat(frames, ignore_index=True)
    C = summarise(R)

    #  A SHORT RUN MUST NOT BE ABLE TO WRITE THE FILES THE MANUSCRIPT READS.
    #  The two-replicate smoke test of this file wrote s31_facts.csv, and
    #  make_numbers picked it up and printed a coverage of 100% at
    #  \nSimReps = 2 before anybody noticed.  The verifier would have caught
    #  it, but a checker that fires is a worse defence than a file that
    #  cannot be written, so a run at anything below the declared replicate
    #  count writes under a different name and says so.
    full = (not a.reps) or a.reps >= min(default_reps.values())
    if a.reps and a.reps < REPS_CORE and "core" in exps:
        full = False
    prefix = "s31_" if full else "s31_smoke_"
    if not full:
        print("\n  !! SHORT RUN: %d replicates, below the declared counts %s."
              "\n  !! Writing %scoverage.csv and %sfacts.csv, which nothing "
              "in the manuscript reads." % (a.reps, default_reps, prefix,
                                            prefix))
    C.to_csv(RESULTS / (prefix + "coverage.csv"), index=False)

    #  the headline facts, all from the CORE experiment at full replicates.
    #  Every selector below names its experiment, because the three overlap
    #  in (world, K, n_train, block_mult) by design.
    lim = C[C.estimand == "V_limit"]
    core = lim[lim.experiment == "core"]

    def cov(kind, how="median"):
        s = core[core.interval == kind].coverage
        return float(getattr(s, how)()) if len(s) else float("nan")

    sparse = core[core.world == "sparse"]

    def scov(kind):
        s = sparse[sparse.interval == kind].coverage
        return float(s.iloc[0]) if len(s) else float("nan")

    blk = lim[(lim.experiment == "block") & (lim.interval == "nested_basic")]
    grid = lim[(lim.experiment == "grid") & (lim.interval == "nested_basic")]

    facts = dict(
        n_reps_core=int(core.n.max()) if len(core) else 0,
        n_worlds=len(SIM.WORLDS),
        n_grid_cells=len(GRID),
        n_block_lengths=len(BLOCK_MULT),
        cov_naive_pct_median=cov("naive_pct"),
        cov_naive_basic_median=cov("naive_basic"),
        cov_nested_pct_median=cov("nested_pct"),
        cov_nested_pct_min=cov("nested_pct", "min"),
        cov_nested_bc_median=cov("nested_bc"),
        cov_nested_bc_min=cov("nested_bc", "min"),
        cov_nested_basic_median=cov("nested_basic"),
        cov_nested_basic_min=cov("nested_basic", "min"),
        cov_mofn_median=cov("nested_mofn"),
        cov_sparse_pct=scov("nested_pct"),
        cov_sparse_basic=scov("nested_basic"),
        cov_sparse_bc=scov("nested_bc"),
        cov_sparse_mofn=scov("nested_mofn"),
        coverage_se_core=float(core.coverage_se.median()) if len(core) else np.nan,
        cov_grid_basic_min=float(grid.coverage.min()) if len(grid) else np.nan,
        cov_grid_basic_median=float(grid.coverage.median()) if len(grid) else np.nan,
        cov_block_basic_min=float(blk.coverage.min()) if len(blk) else np.nan,
        cov_block_basic_max=float(blk.coverage.max()) if len(blk) else np.nan,
        k_max=int(C.K.max()),
        n_max=int(C.n_train.max()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / (prefix + "facts.csv"),
                                 index=False)
    print()
    print(C.to_string(index=False, float_format=lambda x: "%.4f" % x))
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

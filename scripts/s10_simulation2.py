"""s10 -- THE SIMULATION, AGAINST AN ANSWER THAT IS KNOWN, IN SIX WORLDS.

Round nineteen.  The referee's eighth major comment ends with six demands on
the simulation, and the round-eighteen version met none of them: it used a
logistic data-generating process fitted by logistic regression, which is
unusually favourable; forty replicates, which cannot resolve a coverage
estimate; and it dismissed an 85% coverage as boundary behaviour rather than
treating it as undercoverage.

This file replaces it.

SIX WORLDS, each with an exactly computable truth.  The covariate space is
finite -- an intake block, a free field and a register with K levels -- so the
joint distribution of (cell, outcome) can be ENUMERATED and the population AUC
of any scoring rule computed in closed form rather than simulated.

  linear        a logistic surface; the estimator is correctly specified
  nonlinear     an interaction and a threshold the logistic model cannot see
  drift         the coefficients move between the training and test eras
  sparse        K = 200 register levels on the same sample size
  imbalanced    prevalence 0.02
  noisy         a share of register values are wrong

TWO ESTIMANDS, because under misspecification they are not the same:

  V_oracle   the increment between the two BAYES-OPTIMAL scoring rules -- what
             the register is worth in the world.
  V_limit    the increment between the two FITTED pipelines' limits -- what
             the estimator is estimating.  Approximated by fitting on a very
             large sample and scoring the enumerated population.

A confidence interval built by resampling can only cover V_limit.  Reporting
its coverage of V_oracle as though it were the estimator's coverage is the
error the round-eighteen simulation made, and both are reported here.

TWO INTERVALS, so the referee's central objection is measured and not
asserted:

  naive     the round-eighteen interval: resample the TEST rows, models held
            fixed.  Excludes training-sample and model-selection variability.
  nested    the round-nineteen interval: moving-block resample of the TRAINING
            half, REFIT, evaluate on a moving-block resample of the test half.

    python s10_simulation2.py                 # all six worlds
    python s10_simulation2.py --reps 50       # a short run

Outputs: results/s10_coverage.csv, s10_replicates.csv, s10_facts.csv
"""
from __future__ import annotations

import os

#  see s01_surface.py: the pool parallelises over tasks, so each task must be
#  single-threaded or OpenMP oversubscribes the machine.
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

SEED = 20260823
N_TRAIN, N_TEST = 4000, 2000
N_BOOT = 100
ALPHA = 0.05
N_BIG = 120000            # the sample the limit estimand is fitted on

WORLDS = ("linear", "nonlinear", "drift", "sparse", "imbalanced", "noisy")

#  A FIXED offset per world.  Python's built-in hash() for strings is salted
#  per process, so using it to seed a world would give every worker a
#  DIFFERENT world with the same name -- the truth computed in the parent
#  would not be the truth simulated in the child.  The offsets are literals.
WORLD_SEED = {"linear": 11, "nonlinear": 23, "drift": 37, "sparse": 53,
              "imbalanced": 71, "noisy": 97}


# --------------------------------------------------------------------------
def world_spec(world, rng):
    """Return (K, cell probabilities, P(y=1 | cell), and the era-2 version)."""
    K = 200 if world == "sparse" else 20
    nb, ng = 4, 3                       # intake cells, free-field levels
    uf = rng.normal(0, 1.0, K)
    ub = rng.normal(0, 0.8, nb)
    ug = rng.normal(0, 0.9, ng)
    #  a register whose levels are used with a long tail, as an estate is
    p_f = 1.0 / (np.arange(1, K + 1) ** 0.9)
    p_f = p_f / p_f.sum()
    p_b = np.full(nb, 1.0 / nb)
    p_g = np.full(ng, 1.0 / ng)
    idx = np.array(list(np.ndindex(nb, ng, K)))
    pc = p_b[idx[:, 0]] * p_g[idx[:, 1]] * p_f[idx[:, 2]]

    def logits(a_b, a_g, a_f, extra=0.0):
        z = (a_b * ub[idx[:, 0]] + a_g * ug[idx[:, 1]] + a_f * uf[idx[:, 2]])
        if world == "nonlinear":
            z = z + 1.2 * (ub[idx[:, 0]] > 0) * uf[idx[:, 2]]
            z = z + 0.9 * np.sign(uf[idx[:, 2]]) * (np.abs(uf[idx[:, 2]]) > 1.0)
        return z + extra

    if world == "imbalanced":
        intercept = -3.9
    else:
        intercept = 0.0
    z1 = logits(1.0, 1.0, 1.0, intercept)
    #  drift: the register's coefficient halves and the free field's grows
    z2 = logits(1.0, 1.6, 0.5, intercept) if world == "drift" else z1
    p1 = 1.0 / (1.0 + np.exp(-z1))
    p2 = 1.0 / (1.0 + np.exp(-z2))
    return dict(K=K, nb=nb, ng=ng, idx=idx, pc=pc, p1=p1, p2=p2, world=world)


NOISE_RATE = 0.20


def observed_population(W):
    """The population the ESTIMATOR sees, which in the noisy world is not the
    one the generator writes down.

    A register value is replaced by a uniform draw with probability
    NOISE_RATE, so the OBSERVED cell (b, g, j) is a mixture over the true
    cells:

        P(j | f)      = (1 - r) 1{j = f} + r / K
        w(b, g, j)    = sum_f  pc(b, g, f) P(j | f)
        P(y=1 | b,g,j)= sum_f  pc(b, g, f) P(j | f) p(b, g, f) / w(b, g, j)

    Enumerating the TRUE cells instead --- which is what this file did until
    an n-scaling and penalty-scaling experiment (s18) refuted every
    finite-sample explanation for the noisy world's coverage failure ---
    scores the large-sample fit on register values it never sees at that
    frequency, and both estimands come out too high.  The estimator was then
    measured against a target it is not estimating, and reported as biased.

    Returns (pc_obs, p_y_obs) on the same cell ordering as W['idx'].  Every
    other world returns its own population unchanged.
    """
    pc, p_y = W["pc"], W["p2"]
    if W["world"] != "noisy":
        return pc, p_y
    idx, K, r = W["idx"], W["K"], NOISE_RATE
    key = idx[:, 0] * 1000 + idx[:, 1]          # the (b, g) block
    w_obs = np.zeros_like(pc)
    m_obs = np.zeros_like(pc)                   # sum of weight * p
    for k in np.unique(key):
        sel = key == k
        f = idx[sel, 2]
        w, p = pc[sel], p_y[sel]
        order = np.argsort(f)                   # rows in f order within block
        w, p = w[order], p[order]
        #  (1-r) mass stays on its own level, r mass spreads uniformly
        tot_w, tot_wp = w.sum(), float((w * p).sum())
        w_j = (1.0 - r) * w + r * tot_w / K
        wp_j = (1.0 - r) * (w * p) + r * tot_wp / K
        back = np.empty_like(order)
        back[order] = np.arange(len(order))
        w_obs[sel] = w_j[back]
        m_obs[sel] = wp_j[back]
    with np.errstate(invalid="ignore", divide="ignore"):
        p_obs = np.where(w_obs > 0, m_obs / w_obs, 0.0)
    return w_obs, p_obs


def population_auc(score, p_y, pc):
    """Exact population AUC of a scoring rule over an enumerated space.

    score  one score per cell;  p_y  P(y=1|cell);  pc  P(cell).
    Ties contribute 1/2, which is the Mann-Whitney convention spec.py uses.
    """
    w_pos = pc * p_y
    w_neg = pc * (1.0 - p_y)
    P, N = w_pos.sum(), w_neg.sum()
    if P <= 0 or N <= 0:
        return np.nan
    o = np.argsort(score, kind="stable")
    s, wp, wn = score[o], w_pos[o], w_neg[o]
    #  sum over pairs: for each cell, the negative mass strictly below plus
    #  half the negative mass at the same score
    cum_neg = np.concatenate([[0.0], np.cumsum(wn)])[:-1]
    conc = 0.0
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        blk_wp = wp[i:j + 1].sum()
        blk_wn = wn[i:j + 1].sum()
        conc += blk_wp * cum_neg[i] + 0.5 * blk_wp * blk_wn
        i = j + 1
    return float(conc / (P * N))


def truth(W):
    """The two oracle scores and the exact population increment.

    Computed on the OBSERVED population (see observed_population): the oracle
    is the best rule available to somebody who reads the register the analyst
    actually has, not the one the generator wrote down.  In every world but
    `noisy` the two are the same object.
    """
    idx = W["idx"]
    pc, p_y = observed_population(W)
    #  oracle WITH the register: the cell probability itself
    s_full = p_y
    #  oracle WITHOUT it: E[p | intake, free field], marginalising the register
    key = idx[:, 0] * 100 + idx[:, 1]
    df = pd.DataFrame(dict(key=key, pc=pc, p=p_y))
    num = df.assign(w=df.pc * df.p).groupby("key").w.sum()
    den = df.groupby("key").pc.sum()
    s_base = df.key.map(num / den).values
    #  and one more rung: intake only
    key0 = idx[:, 0]
    df0 = pd.DataFrame(dict(key=key0, pc=pc, p=p_y))
    num0 = df0.assign(w=df0.pc * df0.p).groupby("key").w.sum()
    den0 = df0.groupby("key").pc.sum()
    s_intake = df0.key.map(num0 / den0).values
    return dict(
        auc_full=population_auc(s_full, p_y, pc),
        auc_base=population_auc(s_base, p_y, pc),
        auc_intake=population_auc(s_intake, p_y, pc),
        V_oracle=population_auc(s_full, p_y, pc) - population_auc(s_base, p_y, pc))


def draw(W, n, era, rng):
    idx, pc = W["idx"], W["pc"]
    p = W["p1"] if era == 1 else W["p2"]
    c = rng.choice(len(pc), size=n, p=pc)
    y = (rng.random(n) < p[c]).astype(int)
    d = pd.DataFrame(dict(b=idx[c, 0].astype(str), g=idx[c, 1].astype(str),
                          f=idx[c, 2].astype(str)))
    if W["world"] == "noisy":
        hit = rng.random(n) < NOISE_RATE
        d.loc[hit, "f"] = rng.choice(np.arange(W["K"]),
                                     size=int(hit.sum())).astype(str)
    d["_y"] = y
    return d


def fit_scores(tr, te, cols):
    return S._onehot_logit(tr, te, cols, tr["_y"].values, SEED)


def limit_estimand(W, rng, observed=True):
    """V_limit: fit the pipeline on a very large sample and score the
    ENUMERATED population, so no test-sampling noise enters.

    `observed=False` reproduces the PRE-CORRECTION definition, which weighted
    the enumerated cells by the generator's own table rather than by the
    distribution the estimator samples from.  It exists so that
    Appendix~G's evidence --- two finite-sample explanations tested against
    that definition and both refuted --- can be regenerated rather than
    quoted from a log, and it is used by nothing else.
    """
    big = draw(W, N_BIG, 1, rng)
    idx = W["idx"]
    pop = pd.DataFrame(dict(b=idx[:, 0].astype(str), g=idx[:, 1].astype(str),
                            f=idx[:, 2].astype(str)))
    pop["_y"] = 0
    s0 = fit_scores(big, pop, ["b", "g"])
    s1 = fit_scores(big, pop, ["b", "g", "f"])
    #  weighted by the OBSERVED population: the enumerated rows are the
    #  register values the model is shown, and in the noisy world they occur
    #  at frequencies, and carry outcome probabilities, that the generator's
    #  own table does not give.
    pc, p_y = (observed_population(W) if observed else (W["pc"], W["p2"]))
    return (population_auc(s1, p_y, pc) - population_auc(s0, p_y, pc))


def one_rep(args):
    world, rep = args
    rng = np.random.default_rng(SEED + 1013 * rep + WORLD_SEED[world])
    W = world_spec(world, np.random.default_rng(SEED + WORLD_SEED[world]))
    T = truth(W)
    tr = draw(W, N_TRAIN, 1, rng)
    te = draw(W, N_TEST, 2, rng)
    from sklearn.metrics import roc_auc_score
    yte = te["_y"].values
    if len(np.unique(yte)) < 2:
        return None
    p0 = fit_scores(tr, te, ["b", "g"])
    p1 = fit_scores(tr, te, ["b", "g", "f"])
    V_hat = roc_auc_score(yte, p1) - roc_auc_score(yte, p0)

    #  the naive interval: resample the TEST rows only, models fixed
    nb = []
    for b in range(N_BOOT):
        r = np.random.default_rng(SEED + 7919 * b + rep)
        i = r.integers(0, len(yte), len(yte))
        if len(np.unique(yte[i])) < 2:
            continue
        nb.append(roc_auc_score(yte[i], p1[i]) - roc_auc_score(yte[i], p0[i]))
    nb = np.array(nb, float)

    #  the nested interval: block-resample the training half, REFIT, and
    #  block-resample the test half
    nn = []
    for b in range(N_BOOT):
        r = np.random.default_rng(SEED + 104729 * b + rep)
        itr = S.block_indices(len(tr), r)
        ite = S.block_indices(len(te), r)
        tb, eb = tr.iloc[itr], te.iloc[ite]
        yb = eb["_y"].values
        if len(np.unique(yb)) < 2:
            continue
        q0 = fit_scores(tb, eb, ["b", "g"])
        q1 = fit_scores(tb, eb, ["b", "g", "f"])
        nn.append(roc_auc_score(yb, q1) - roc_auc_score(yb, q0))
    nn = np.array(nn, float)

    #  THREE interval constructions from the same draws, because the
    #  percentile interval assumes the bootstrap distribution is centred on
    #  the estimate and with a high-cardinality register it is not: a
    #  bootstrap training resample contains about 63% of the distinct levels,
    #  so every refit sees a sparser register than the real training half and
    #  the increment shrinks.  The percentile interval then sits below the
    #  estimand and misses no matter how wide it is.
    #
    #    percentile  [q_a, q_b]                          the naive choice
    #    basic       [2*V - q_b, 2*V - q_a]              pivots out a shift
    #    bc          percentile with the endpoints moved by the median bias
    from scipy.stats import norm

    def three(a, v):
        if len(a) < 10:
            return dict(pct=(np.nan, np.nan), basic=(np.nan, np.nan),
                        bc=(np.nan, np.nan), shift=np.nan)
        qa = float(np.percentile(a, 100 * ALPHA / 2))
        qb = float(np.percentile(a, 100 * (1 - ALPHA / 2)))
        share = float(np.mean(a < v))
        share = min(max(share, 1.0 / (2 * len(a))), 1 - 1.0 / (2 * len(a)))
        z0 = float(norm.ppf(share))
        za, zb = norm.ppf(ALPHA / 2), norm.ppf(1 - ALPHA / 2)
        pa = float(norm.cdf(2 * z0 + za)) * 100
        pb = float(norm.cdf(2 * z0 + zb)) * 100
        return dict(pct=(qa, qb), basic=(2 * v - qb, 2 * v - qa),
                    bc=(float(np.percentile(a, pa)),
                        float(np.percentile(a, pb))),
                    shift=float(np.median(a)) - v)

    N = three(nb, V_hat)
    X = three(nn, V_hat)
    out = dict(world=world, rep=rep, V_hat=V_hat, V_oracle=T["V_oracle"],
               auc_full=T["auc_full"], auc_base=T["auc_base"],
               naive_shift=N["shift"], nested_shift=X["shift"])
    for tag, D in (("naive", N), ("nested", X)):
        for kind in ("pct", "basic", "bc"):
            lo, hi = D[kind]
            out["%s_%s_lo" % (tag, kind)] = lo
            out["%s_%s_hi" % (tag, kind)] = hi
            out["%s_%s_width" % (tag, kind)] = hi - lo
    #  the names the rest of the file already uses
    out["naive_lo"], out["naive_hi"] = N["pct"]
    out["nested_lo"], out["nested_hi"] = X["pct"]
    out["naive_width"] = N["pct"][1] - N["pct"][0]
    out["nested_width"] = X["pct"][1] - X["pct"][0]
    return out


def check_observed_population(n=400000, z_max=6.0):
    """The exact marginalisation, checked against a Monte Carlo sample.

    This runs at the top of EVERY simulation, not on request.  The defect it
    guards against --- scoring the estimator against a population it never
    samples from --- produced a coverage of 0.04 in one world, survived being
    written up as a property of the estimator, and was found only because two
    finite-sample explanations for it were tested (s18) and both failed.  A
    truth that is wrong is worse than no truth, so it is checked every time.
    """
    for w in ("linear", "noisy"):
        W = world_spec(w, np.random.default_rng(SEED + WORLD_SEED[w]))
        pc, p_y = observed_population(W)
        if abs(float(pc.sum()) - 1.0) > 1e-9:
            raise AssertionError("%s: observed cell mass is %.6f, not 1"
                                 % (w, pc.sum()))
        rng = np.random.default_rng(SEED + 424242)
        d = draw(W, n, 2, rng)
        idx = W["idx"]
        key = (d.b.astype(int) * 1000000 + d.g.astype(int) * 1000
               + d.f.astype(int))
        want = (idx[:, 0] * 1000000 + idx[:, 1] * 1000 + idx[:, 2])
        emp_w = key.value_counts(normalize=True).reindex(want).fillna(0.0)
        emp_p = d.groupby(key.values)["_y"].mean().reindex(want).fillna(0.0)
        #  Standardised residuals, not raw distances.  A raw total-variation
        #  bound over 240 cells is dominated by Monte Carlo noise -- the first
        #  version of this check failed a CORRECT marginalisation for exactly
        #  that reason -- so each cell is compared with its own sampling
        #  standard error and the check is on the largest z.
        sd_w = np.sqrt(np.maximum(pc * (1.0 - pc), 1e-15) / n)
        zw = float(np.max(np.abs(emp_w.values - pc) / sd_w))
        heavy = pc * n >= 100                       # p is meaningless below
        sd_p = np.sqrt(np.maximum(p_y * (1.0 - p_y), 1e-15) / (pc * n))
        zp = float(np.max(np.abs(emp_p.values - p_y)[heavy] / sd_p[heavy]))
        print("  %-9s marginalisation check over %d cells: max z on the cell "
              "masses %.2f, on the outcome rates %.2f"
              % (w, len(pc), zw, zp))
        if zw > z_max or zp > z_max:
            raise AssertionError(
                "%s: the enumerated population does not match the sampler "
                "(max z = %.2f on masses, %.2f on rates).  Whatever this file "
                "calls the truth is not what the estimator sees."
                % (w, zw, zp))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--serial", action="store_true")
    ap.add_argument("--procs", type=int, default=0,
                    help="worker processes; 0 means min(12, cpus-2).  Set it "
                         "low to share the machine with a longer run.")
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s10  SIX WORLDS, EXACT TRUTH, TWO INTERVALS")
    print("=" * 92)
    check_observed_population()

    #  the limit estimand, once per world
    LIM = {}
    for w in WORLDS:
        W = world_spec(w, np.random.default_rng(SEED + WORLD_SEED[w]))
        LIM[w] = limit_estimand(W, np.random.default_rng(SEED + 7))
        T = truth(W)
        print("  %-12s  V_oracle %+.4f   V_limit %+.4f   base AUC %.4f"
              % (w, T["V_oracle"], LIM[w], T["auc_base"]), flush=True)

    tasks = [(w, r) for w in WORLDS for r in range(a.reps)]
    out = []
    if a.serial:
        for t in tasks:
            r = one_rep(t)
            if r:
                out.append(r)
    else:
        import multiprocessing as mp
        nproc = a.procs or min(12, max(1, (os.cpu_count() or 4) - 2))
        with mp.Pool(processes=nproc) as pool:
            for i, r in enumerate(pool.imap_unordered(one_rep, tasks,
                                                      chunksize=4)):
                if r:
                    out.append(r)
                if (i + 1) % 100 == 0:
                    print("    %d/%d  %.0fs" % (i + 1, len(tasks),
                                                time.time() - t0), flush=True)
    R = pd.DataFrame(out)
    R["V_limit"] = R.world.map(LIM)
    R.to_csv(RESULTS / "s10_replicates.csv", index=False)

    rows = []
    for w, sub in R.groupby("world"):
        for target, col in (("V_oracle", "V_oracle"), ("V_limit", "V_limit")):
            for kind in ("naive", "nested", "naive_pct", "naive_basic",
                         "naive_bc", "nested_pct", "nested_basic",
                         "nested_bc"):
                if kind + "_lo" not in sub.columns:
                    continue
                lo, hi = sub[kind + "_lo"], sub[kind + "_hi"]
                cov = float(((lo <= sub[col]) & (sub[col] <= hi)).mean())
                rows.append(dict(world=w, estimand=target, interval=kind,
                                 coverage=cov, n=len(sub),
                                 mean_width=float(sub[kind + "_width"].mean()),
                                 bias=float((sub.V_hat - sub[col]).mean()),
                                 rmse=float(np.sqrt(
                                     ((sub.V_hat - sub[col]) ** 2).mean())),
                                 truth=float(sub[col].iloc[0]),
                                 mean_estimate=float(sub.V_hat.mean()),
                                 median_shift=float(
                                     sub[kind.split("_")[0] + "_shift"].mean())
                                 if (kind.split("_")[0] + "_shift")
                                 in sub.columns else np.nan))
    C = pd.DataFrame(rows)
    C.to_csv(RESULTS / "s10_coverage.csv", index=False)
    print()
    print(C.to_string(index=False, float_format=lambda x: "%.4f" % x))

    lim = C[C.estimand == "V_limit"]
    facts = dict(
        n_worlds=len(WORLDS), n_reps=a.reps, n_rows=len(R), n_boot=N_BOOT,
        n_train=N_TRAIN, n_test=N_TEST,
        coverage_naive_min=float(lim[lim.interval == "naive"].coverage.min()),
        coverage_nested_basic_min=float(
            lim[lim.interval == "nested_basic"].coverage.min())
        if (lim.interval == "nested_basic").any() else np.nan,
        coverage_nested_basic_median=float(
            lim[lim.interval == "nested_basic"].coverage.median())
        if (lim.interval == "nested_basic").any() else np.nan,
        coverage_nested_bc_min=float(
            lim[lim.interval == "nested_bc"].coverage.min())
        if (lim.interval == "nested_bc").any() else np.nan,
        coverage_nested_bc_median=float(
            lim[lim.interval == "nested_bc"].coverage.median())
        if (lim.interval == "nested_bc").any() else np.nan,
        max_bootstrap_shift=float(R.nested_shift.abs().max())
        if "nested_shift" in R.columns else np.nan,
        coverage_naive_median=float(lim[lim.interval == "naive"].coverage.median()),
        coverage_nested_min=float(lim[lim.interval == "nested"].coverage.min()),
        coverage_nested_median=float(lim[lim.interval == "nested"].coverage.median()),
        width_ratio_median=float(
            (lim[lim.interval == "nested"].mean_width.values
             / lim[lim.interval == "naive"].mean_width.values).mean()),
        bias_vs_limit_max=float(lim.bias.abs().max()),
        bias_vs_oracle_max=float(C[C.estimand == "V_oracle"].bias.abs().max()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s10_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

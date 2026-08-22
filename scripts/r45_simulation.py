"""r45 -- THE ESTIMATOR AGAINST AN ANSWER THAT IS KNOWN BY CONSTRUCTION.

PLAN-REVIEWER-PROOF.md section 5.2.  Every number in this paper is estimated
and none is checked against a truth, because on real data there is no truth to
check against.  Here there is one.

THE DESIGN.  Four discrete variables on a finite cell space:

    b   the intake block            K_b levels
    g   the free opening field      K_g levels
    f   the high-cost entity        K_f levels
    y   the outcome                 Bernoulli, generated from (b, g, f)

The outcome's log-odds are

    eta(b, g, f) = e_b[b] + (1 - rho) * e_f[f] + rho * e_g[g] + c

with `rho` the OVERLAP: the share of the entity's information about y that the
opening field also carries.  Because the space is finite and every conditional
is known, the TRUE incremental value of f over any baseline can be computed by
EXHAUSTIVE ENUMERATION of the cell space at the population level -- no
sampling, no fitting, no estimator.  That is R*(rho), the answer.

WHAT IS REPORTED.

  1.  R-hat against R* across rho, with the estimator's bias and the coverage
      of its paired bootstrap interval over independent replicates.
  2.  The same sweep under the four choices, to show the surface behaves as
      Propositions 1-3 say it must.
  3.  Everything is era-independent, which partially answers the objection
      that the newest event log in the corpus is from 2019.

WHAT WOULD SINK THIS.  A bias that does not shrink with n, or coverage far
from nominal, would mean the paper's own point estimates are not estimating
what they claim to estimate.  The numbers are printed whatever they are.

Outputs: results/r45_truth.csv, r45_estimates.csv, r45_coverage.csv,
         r45_axes.csv, r45_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

SEED = 20260819
EPS = 1e-12
K_B, K_G, K_F = 4, 6, 40
RHOS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
N_MAIN = 60000
N_REP = 40                      # replicates per rho for bias and coverage
N_BOOT = 400                    # bootstrap draws inside each replicate
N_SWEEP = (5000, 20000, 60000)  # is the bias consistent?
GRID = np.round(np.arange(0.05, 0.8001, 0.05), 4)
METRICS = ("auc", "ap", "brier_skill", "nagelkerke")


# ------------------------------------------------------------------- the world
def world(rho, seed=SEED):
    """Every parameter of the data-generating process, as arrays.

    f determines g through a fixed many-to-one map corrupted at a fixed rate,
    which is what makes a register and a resource stamp overlap in real logs.
    """
    rng = np.random.default_rng(seed)
    e_b = rng.normal(0, 0.8, K_B)
    e_f = rng.normal(0, 1.6, K_F)
    e_g = rng.normal(0, 1.6, K_G)
    gmap = rng.integers(0, K_G, K_F)
    p_b = rng.dirichlet(np.full(K_B, 4.0))
    p_f = rng.dirichlet(np.full(K_F, 1.2))
    couple = 0.75                       # P(g is the coarsening of f)
    c = -0.4
    return dict(e_b=e_b, e_f=e_f, e_g=e_g, gmap=gmap, p_b=p_b, p_f=p_f,
                couple=couple, c=c, rho=rho)


def cell_table(W):
    """Every (b, g, f) cell with its probability and its true P(y=1).

    The cell space is K_B * K_G * K_F = 960 cells, so this is exact rather
    than a Monte Carlo approximation of itself.
    """
    b = np.repeat(np.arange(K_B), K_G * K_F)
    g = np.tile(np.repeat(np.arange(K_G), K_F), K_B)
    f = np.tile(np.arange(K_F), K_B * K_G)
    #  P(g | f): `couple` on the mapped value, the rest spread uniformly
    pg_f = np.full((K_F, K_G), (1.0 - W["couple"]) / K_G)
    pg_f[np.arange(K_F), W["gmap"]] += W["couple"]
    pg_f = pg_f / pg_f.sum(1, keepdims=True)
    p = W["p_b"][b] * W["p_f"][f] * pg_f[f, g]
    eta = (W["e_b"][b] + (1 - W["rho"]) * W["e_f"][f]
           + W["rho"] * W["e_g"][g] + W["c"])
    py = 1.0 / (1.0 + np.exp(-eta))
    return pd.DataFrame(dict(b=b, g=g, f=f, p=p / p.sum(), py=py))


def sample(W, n, seed):
    T = cell_table(W)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(T), size=n, p=T.p.values)
    d = T.iloc[idx][["b", "g", "f", "py"]].reset_index(drop=True)
    d["y"] = (rng.random(n) < d.py.values).astype(int)
    return d


# ---------------------------------------------------- the answer, by enumeration
def _auc_from_cells(T, score_col):
    """Population AUC of a scoring function that is constant within a cell.

    Exact, including the 1/2 credit for ties, computed from cell masses and
    cell outcome probabilities.  No sampling.
    """
    s = T[score_col].values
    w1 = (T.p * T.py).values                 # mass of positives per cell
    w0 = (T.p * (1 - T.py)).values           # mass of negatives per cell
    o = np.argsort(s, kind="stable")
    s, w1, w0 = s[o], w1[o], w0[o]
    P, N = w1.sum(), w0.sum()
    if P <= 0 or N <= 0:
        return np.nan
    #  group ties, then count concordant + half the tied mass
    conc = 0.0
    seen_neg = 0.0
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        tie_pos = w1[i:j + 1].sum()
        tie_neg = w0[i:j + 1].sum()
        conc += tie_pos * seen_neg + 0.5 * tie_pos * tie_neg
        seen_neg += tie_neg
        i = j + 1
    return float(conc / (P * N))


def true_scores(T, cols):
    """The Bayes-optimal score given `cols`: P(y=1 | cols), by enumeration."""
    if not cols:
        return np.full(len(T), float((T.p * T.py).sum()))
    grp = T.groupby(cols, sort=False)
    num = grp.apply(lambda x: float((x.p * x.py).sum()), include_groups=False)
    den = grp.p.sum()
    m = (num / den).rename("s").reset_index()
    return T[cols].merge(m, on=cols, how="left").s.values


def true_reduction(W, b_lo=("b",), b_hi=("b", "g")):
    T = cell_table(W)
    out = {}
    for nm, cols in (("lo", list(b_lo)), ("hi", list(b_hi))):
        T[f"s_{nm}_0"] = true_scores(T, cols)
        T[f"s_{nm}_1"] = true_scores(T, cols + ["f"])
        out[f"auc_{nm}_0"] = _auc_from_cells(T, f"s_{nm}_0")
        out[f"auc_{nm}_1"] = _auc_from_cells(T, f"s_{nm}_1")
    out["V_lo"] = out["auc_lo_1"] - out["auc_lo_0"]
    out["V_hi"] = out["auc_hi_1"] - out["auc_hi_0"]
    out["R_true"] = (1.0 - out["V_hi"] / out["V_lo"]
                     if out["V_lo"] > EPS else np.nan)
    out["prevalence"] = float((T.p * T.py).sum())
    return out


# ---------------------------------------------------------------- the estimator
def fit(tr, te, cols):
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=1.0).fit(X, tr.y.values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def brier_skill(p, y, p0):
    return 1.0 - float(np.mean((p - y) ** 2)) / float(np.mean((p0 - y) ** 2))


def nagelkerke(p, y, p0):
    pc = np.clip(p, EPS, 1 - EPS)
    ll_m = float((y * np.log(pc) + (1 - y) * np.log(1 - pc)).sum())
    ll_0 = float((y * np.log(p0) + (1 - y) * np.log(1 - p0)).sum())
    cs = 1.0 - np.exp((2.0 / len(y)) * (ll_0 - ll_m))
    return float(cs / (1.0 - np.exp((2.0 / len(y)) * ll_0)))


def net_benefit(p, y, t):
    a = p >= t
    return (float((a & (y == 1)).sum())
            - float((a & (y == 0)).sum()) * (t / (1 - t))) / len(y)


def metric(nm, p, y, p0):
    if nm == "auc":
        return roc_auc_score(y, p)
    if nm == "ap":
        return average_precision_score(y, p)
    if nm == "brier_skill":
        return brier_skill(p, y, p0)
    if nm == "nagelkerke":
        return nagelkerke(p, y, p0)
    return net_benefit(p, y, float(nm.split("_")[1]))


def estimate(d, b_lo=("b",), b_hi=("b", "g"), n_boot=0, seed=SEED,
             metrics=("auc",)):
    """The paper's own estimator: one-hot logistic, 70/30 split by row order,
    paired bootstrap over test rows sharing one index set per draw."""
    cut = int(len(d) * 0.70)
    tr, te = d.iloc[:cut], d.iloc[cut:]
    y = te.y.values
    p0 = float(tr.y.mean())
    P = {}
    P["lo0"] = fit(tr, te, list(b_lo))
    P["lo1"] = fit(tr, te, list(b_lo) + ["f"])
    P["hi0"] = fit(tr, te, list(b_hi))
    P["hi1"] = fit(tr, te, list(b_hi) + ["f"])
    out = {}
    for m in metrics:
        vn = metric(m, P["lo1"], y, p0) - metric(m, P["lo0"], y, p0)
        vh = metric(m, P["hi1"], y, p0) - metric(m, P["hi0"], y, p0)
        out[f"V_lo_{m}"] = vn
        out[f"V_hi_{m}"] = vh
        out[f"R_{m}"] = (1.0 - vh / vn) if vn > EPS else np.nan
    if n_boot:
        rng = np.random.default_rng(seed)
        n = len(y)
        rs = []
        for _ in range(n_boot):
            i = rng.integers(0, n, n)
            yy = y[i]
            if len(np.unique(yy)) < 2:
                continue
            vn = roc_auc_score(yy, P["lo1"][i]) - roc_auc_score(yy, P["lo0"][i])
            vh = roc_auc_score(yy, P["hi1"][i]) - roc_auc_score(yy, P["hi0"][i])
            rs.append(1.0 - vh / vn if vn > EPS else np.nan)
        rs = np.array(rs, float)
        ok = np.isfinite(rs)
        out["R_lo"] = float(np.percentile(rs[ok], 2.5)) if ok.any() else np.nan
        out["R_hi"] = float(np.percentile(rs[ok], 97.5)) if ok.any() else np.nan
        out["frac_denom_pos"] = float(ok.mean())
    return out


# ======================================================================
def main():
    t0 = time.time()
    print("=" * 96)
    print("A.  THE TRUTH, BY EXHAUSTIVE ENUMERATION OF THE CELL SPACE")
    print("=" * 96)
    truth = []
    for rho in RHOS:
        W = world(rho)
        t = true_reduction(W)
        t["rho"] = rho
        truth.append(t)
        print(f"  rho={rho:.1f}  prevalence={t['prevalence']:.4f}  "
              f"V(f|B0)={t['V_lo']:+.5f}  V(f|B0+g)={t['V_hi']:+.5f}  "
              f"R*={t['R_true']:.5f}")
    TRUTH = pd.DataFrame(truth)
    TRUTH.to_csv(RESULTS / "r45_truth.csv", index=False)

    print("\n" + "=" * 96)
    print("B.  THE ESTIMATOR AGAINST IT: BIAS AND COVERAGE OVER REPLICATES")
    print("=" * 96)
    est_rows, cov_rows = [], []
    for rho in RHOS:
        W = world(rho)
        r_true = float(TRUTH[TRUTH.rho == rho].R_true.iloc[0])
        for n in N_SWEEP:
            hats, covered, resolvable = [], 0, 0
            reps = N_REP if n == N_MAIN else max(10, N_REP // 4)
            for k in range(reps):
                d = sample(W, n, seed=SEED + 1000 * k + int(rho * 10))
                e = estimate(d, n_boot=(N_BOOT if n == N_MAIN else 0))
                hats.append(e["R_auc"])
                est_rows.append(dict(rho=rho, n=n, rep=k, R_hat=e["R_auc"],
                                     V_lo=e["V_lo_auc"], V_hi=e["V_hi_auc"],
                                     R_true=r_true))
                if n == N_MAIN and np.isfinite(e.get("R_lo", np.nan)):
                    if e["R_lo"] <= r_true <= e["R_hi"]:
                        covered += 1
                    if e["R_lo"] > 0:
                        resolvable += 1
            h = np.array(hats, float)
            ok = np.isfinite(h)
            cov_rows.append(dict(
                rho=rho, n=n, reps=reps, n_finite=int(ok.sum()),
                R_true=r_true, R_mean=float(np.nanmean(h)),
                bias=float(np.nanmean(h) - r_true),
                sd=float(np.nanstd(h, ddof=1)) if ok.sum() > 1 else np.nan,
                rmse=float(np.sqrt(np.nanmean((h - r_true) ** 2))),
                coverage=(covered / reps if n == N_MAIN else np.nan),
                share_resolvable=(resolvable / reps if n == N_MAIN else np.nan)))
            print(f"  rho={rho:.1f}  n={n:6,}  R*={r_true:+.4f}  "
                  f"mean R-hat={np.nanmean(h):+.4f}  bias={np.nanmean(h) - r_true:+.4f}"
                  f"  sd={cov_rows[-1]['sd']:.4f}"
                  + (f"  coverage={cov_rows[-1]['coverage']:.2f}"
                     if n == N_MAIN else ""), flush=True)
    pd.DataFrame(est_rows).to_csv(RESULTS / "r45_estimates.csv", index=False)
    COV = pd.DataFrame(cov_rows)
    COV.to_csv(RESULTS / "r45_coverage.csv", index=False)

    print("\n" + "=" * 96)
    print("C.  THE FOUR AXES ON A WORLD WHOSE ANSWER IS KNOWN")
    print("=" * 96)
    ax_rows = []
    for rho in RHOS:
        W = world(rho)
        d = sample(W, N_MAIN, seed=SEED)
        r_true = float(TRUTH[TRUTH.rho == rho].R_true.iloc[0])
        mm = list(METRICS) + [f"nb_{t:.2f}" for t in GRID]
        e = estimate(d, metrics=mm)
        for m in mm:
            ax_rows.append(dict(rho=rho, axis=("threshold"
                                               if m.startswith("nb_")
                                               else "metric"),
                                level=m, R=e[f"R_{m}"], R_true=r_true))
        #  the baseline axis: every nested pair of the four-rung ladder
        for lo_, hi_ in ((("b",), ("b", "g")), ((), ("b",)), ((), ("b", "g")),
                         (("b",), ("b", "g"))):
            key = f"{'+'.join(lo_) or 'empty'} -> {'+'.join(hi_)}"
            dd = d.assign(_const="c")
            e2 = estimate(dd, b_lo=(lo_ or ("_const",)), b_hi=hi_)
            ax_rows.append(dict(rho=rho, axis="baseline", level=key,
                                R=e2["R_auc"], R_true=r_true))
        #  the population axis: the register is masked
        for lvl in (1.0, 0.75, 0.50, 0.25):
            rng = np.random.default_rng(SEED)
            dd = d.copy()
            if lvl < 1.0:
                dd.loc[rng.random(len(dd)) > lvl, "f"] = -1
            e3 = estimate(dd)
            ax_rows.append(dict(rho=rho, axis="population", level=f"{lvl:.2f}",
                                R=e3["R_auc"], R_true=r_true))
    AX = pd.DataFrame(ax_rows)
    AX.to_csv(RESULTS / "r45_axes.csv", index=False)
    sp = (AX[np.isfinite(AX.R)].groupby(["rho", "axis"]).R
          .agg(["min", "max"]).reset_index())
    sp["spread"] = sp["max"] - sp["min"]
    print(sp.to_string(index=False))

    main_cov = COV[COV.n == N_MAIN]
    F = pd.DataFrame([dict(
        n_cells=K_B * K_G * K_F, K_b=K_B, K_g=K_G, K_f=K_F,
        n_rho=len(RHOS), n_main=N_MAIN, n_rep=N_REP, n_boot=N_BOOT,
        r_true_lo=float(TRUTH.R_true.min()), r_true_hi=float(TRUTH.R_true.max()),
        max_abs_bias=float(main_cov.bias.abs().max()),
        mean_abs_bias=float(main_cov.bias.abs().mean()),
        min_coverage=float(main_cov.coverage.min()),
        max_coverage=float(main_cov.coverage.max()),
        mean_coverage=float(main_cov.coverage.mean()),
        bias_at_5k=float(COV[COV.n == 5000].bias.abs().mean()),
        bias_at_60k=float(COV[COV.n == 60000].bias.abs().mean()),
        max_metric_spread=float(sp[sp.axis == "metric"].spread.max()),
        max_threshold_spread=float(sp[sp.axis == "threshold"].spread.max()),
        max_baseline_spread=float(sp[sp.axis == "baseline"].spread.max()),
        max_population_spread=float(sp[sp.axis == "population"].spread.max()),
        runtime_s=round(time.time() - t0, 1))])
    F.to_csv(RESULTS / "r45_facts.csv", index=False)
    print("\n" + F.T.to_string())
    print(f"\nWrote r45_*.csv ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

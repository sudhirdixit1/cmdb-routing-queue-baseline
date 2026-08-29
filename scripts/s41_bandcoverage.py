"""s41 -- THE BAND'S FAMILY-WISE COVERAGE, AGAINST A KNOWN ANSWER.

Round twenty-five.  Every referee asked for this and the methods referee
called it the single most important thing to fix.  Section 4.3 ended, until
this file existed, by saying so itself: "nothing in this paper measures the
band's FAMILY-WISE coverage against a known answer, because the simulation of
Section 10 validates the pointwise interval only."

WHAT WAS ALREADY KNOWN, AND WHAT IT DID NOT SETTLE
`s21_bands.py` writes two estimates of the same max-$t$ critical value: the
Gaussian multiplier quantile `q`, which the bands use, and the empirical
quantile `q_emp` of the B observed maxima.  `s40_qcheck.py` compared them and
found `q` below the entire order-statistic interval of `q_emp` on 15 of 19
whole-surface families and on all 19 decision-curve families.  A disagreement
between two estimators of one quantity says one of them is wrong.  It cannot
say which, because neither had been checked against a coverage it is supposed
to deliver.  This file supplies the missing arm.

--------------------------------------------------------------------------
STAGE 1 ASKS WHAT THE CORPUS'S DRAWS ACTUALLY LOOK LIKE, AND FINDS TWO
DIFFERENT ANSWERS UNDER ONE WORD

Section 4.3 says "these draws are heavy-tailed" and carries no number.  The
draws are in the repository, so the sentence is checkable, and it turns out to
be true of the surface families and true of the decision-curve families for
entirely different reasons.

  Whole-surface families.  The tail is real and it is statistical.  The median
  cell's excess kurtosis is 0.3 and the ninetieth percentile is 3.6, and the
  worst cells are genuine: a Nagelkerke $R^2$ cell whose eighty draws run
  between -2.5 and 1.4 with one draw at -24, which is one refit that came
  apart, on an instrument that is unbounded below.  No instrument dominates
  the family maximum -- each of the five attains it between 8% and 28% of the
  time -- so this is a property of refitting a pipeline, not of one metric.

  Decision-curve families.  The tail is mostly an artefact of DEGENERATE
  CELLS.  At a threshold where the two arms treat every case alike, the
  net-benefit difference is zero by arithmetic and not by estimation, and the
  corpus is full of such cells: 276 of BPIC14/handover's 2,853, 180 of
  BPIC15_4/handover's 1,045, 63 of RoadFines' 534, where at least nine draws
  in ten are exactly 0.0.  `s21.critical` keeps any cell whose spread exceeds
  1e-15 absolute, so a cell that is zero in 130 of 150 draws and 3e-5 in the
  rest survives, and standardising it by that spread sends its studentised
  value to the algebraic ceiling.  Sorted by how many DISTINCT values a cell's
  draws take, the pattern is unmistakable: cells with at most twenty distinct
  values have median excess kurtosis 11.2, cells with more than a hundred have
  0.24.

  What removing them does, and does not do.  Dropping every cell that is
  exactly zero in nine draws of ten takes the median ratio q_emp/q on the
  decision-curve families from 2.09 to 1.80 and the ninetieth-percentile
  kurtosis from 6.2 to 5.9.  It does NOT overturn s40: `q` still sits below
  the empirical interval on all 19 curve families and 15 of 19 surface ones.
  The degeneracy is a real defect in what the manuscript reports -- Section
  6.4's count of what `q_emp` resolves is partly a count of arithmetic -- and
  it is not the explanation of the disagreement.

--------------------------------------------------------------------------
STAGE 3 IS DELIBERATELY THE MOST FAVOURABLE CASE THE BAND CAN BE GIVEN

The truth theta_c is zero at every cell in three of the four regimes and a
fixed, heterogeneous, non-zero vector in the fourth.  A draw from the sampling
distribution, added to the truth, gives the point estimate; B further draws
FROM THE SAME DISTRIBUTION give the bootstrap.  That is the ideal bootstrap: its distribution is not an
approximation of the sampling distribution, it IS the sampling distribution.
Every way a real bootstrap can be wrong -- a resampling scheme that does not
reproduce the dependence, a refit that is unstable, a block length that is
misjudged -- is switched off.

This is the point of the design.  What remains is exactly the object under
test: se estimated from B draws, the max-$t$ critical value estimated from the
same B draws, and the max-$t$ construction itself.  A coverage measured here
is therefore an UPPER BOUND on the coverage the real procedure attains, and a
shortfall here is a shortfall that no improvement to the resampling can
repair.  It also means this file cannot be read as validating the bootstrap;
Section 10 and `s31_simboost.py` do that, and this file assumes their
conclusion rather than re-earning it.

THE POPULATION.  For one family of K cells,

    xi_c = [ sqrt(w) <lambda_c, f> + sqrt(1-w) e_c ] * g_c / sqrt(E g^2),

with r Gaussian factors f and loadings lambda_c ~ N(m, 1) reproducing the
corpus's cross-cell correlation and effective rank, and a scale mixture g_c
that equals `lam` when the draw is contaminated and the cell is FRAGILE, and 1
otherwise.  Contamination is drawn ONCE PER DRAW and applied to every fragile
cell of it, because that is what the corpus shows: an excursion arrives at
many cells of a family together.  A share p of cells is fragile.  Since
E g^2 = (1-eps) + eps*lam^2 divides it out, every cell has unit variance and
the tail knobs do not move the scale.

WHY A SCALE MIXTURE AND NOT A UNIT-LEVEL MECHANISM.  Two earlier versions of
this file built the tail from the resampling units -- a Student t innovation,
then a small set of influential units -- and neither could reach the corpus.
At six hundred units the central limit theorem flattens anything with a finite
variance: the whole grid's best fit was a ninetieth-percentile kurtosis of
0.58 against a target of 3.6.  The mechanism in the real bootstrap is not an
innovation, it is a discrete event at the level of the DRAW -- one refit comes
apart -- and a draw-level event is what is modelled here.

FOUR REGIMES ARE RUN.  The third exists because of what stage 1 found; the
fourth exists because the first three cannot distinguish a band that covers
from a band that never resolves anything.
  gaussian     no contamination; the case the multiplier is derived for
  heavy        contamination calibrated to the corpus's kurtosis profile
  degenerate   heavy, plus a share of cells put on a coarse lattice so that
               most of their draws are exactly zero -- the decision-curve
               cells above.  Their own bands are trivially right; what they
               do is inflate the critical value the OTHER cells are judged
               by, which is the cost this regime measures.
  nonzero      heavy, with the truth a fixed vector two sampling standard
               deviations wide rather than zero.  Under a zero truth every
               cell the band resolves is a mistake, so the experiment can only
               measure a type-I error and a band that resolves nothing scores
               perfectly.  Under a non-zero truth a cell can be resolved
               CORRECTLY, `n_resolved` counts them, and `n_false` counts only
               resolutions on the wrong side of the truth -- which is the
               quantity a resolution region actually rests on.  The band is
               equivariant in the truth and the VERDICT is not, which is why
               this is a regime and not an argument.

FIVE CANDIDATE CRITICAL VALUES ARE SCORED, not one:
  q_mult      the Gaussian multiplier quantile -- what the bands use now
  q_mult_hi   the upper end of its Monte Carlo interval -- what the RESOLVED
              flag uses now
  q_emp       the empirical quantile of the B observed maxima
  q_emp_hi    the upper end of ITS order-statistic interval
  q_rad       a Rademacher wild multiplier over the same standardised draws.
              It differs from `q_mult` in the one respect that matters here:
              it reuses the observed rows of Z with random signs instead of
              replacing them by Gaussians, so a row carrying a genuine
              excursion keeps its magnitude.  A Gaussian multiplier cannot
              reproduce an excursion a Gaussian process does not make, which
              is the mechanism s40 named and never measured.

`q_mult` and `q_mult_hi` come from CALLING `s21_bands.multiplier_quantile`
rather than from a copy of it, so what is scored is the shipped estimator.

THE CONTROL.  A band can miss for two reasons with different remedies: the
per-cell interval it is built from may not cover, or the multiplicity
correction may be too small.  Every replicate therefore also records the
coverage of the per-cell basic interval on the same draws.  It is not 95%
even here: built from 33 draws the basic interval covers at about 0.90 and
from 150 at about 0.93, reaching nominal only past about 400, and the corpus
runs at 33 to 150 while Section 10 validated the construction at 100 refits.
Part of what the band loses it loses before any critical value is chosen.

    python s41_bandcoverage.py --plan          # the cost, no simulation
    python s41_bandcoverage.py --only profile
    python s41_bandcoverage.py                 # all three stages
    python s41_bandcoverage.py --selftest      # the two exactness checks

Outputs: results/s41_profile.csv      per corpus family: the shape measured
         results/s41_calibration.csv  the population parameters, and the fit
         results/s41_replicates.csv.gz
         results/s41_coverage.csv     per cell and candidate: coverage
         results/s41_facts.csv

A run at fewer than the declared replicate count writes `s41_smoke_*`, for the
reason s31 does: a two-replicate smoke test of s31 once wrote the file the
manuscript reads.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s21_bands as B21  # noqa: E402
from common import RESULTS  # noqa: E402

SEED = 20260825
ALPHA = 0.05

#: a cell is DEGENERATE, and inadmissible to a simultaneous family, when at
#: least this share of its draws is exactly zero.  An exact zero is not a
#: small number: it is the arithmetic consequence of the two arms treating
#: every case alike, so the cell's value is determined rather than estimated
#: and a statement quantified over it is vacuous.  The manuscript already
#: excludes the B_empty rung on the same kind of ground.  The threshold is
#: reported alongside its neighbours in results/s41_profile.csv so that
#: nothing rests on the exact figure.
TAU_DEGENERATE = 0.90
TAU_ALT = (0.50, 0.75, 0.95, 0.99)

#: the coverage grid.  Each cell names the corpus family it is matched to, so
#: that a reader can check the match in results/s41_profile.csv rather than
#: take the word "matched" on trust.
GRID = (
    (120, 33, "whole-surface", "BPIC19/duration, the smallest surface family"),
    (180, 80, "whole-surface", "the modal surface family"),
    (480, 150, "whole-surface", "BPIC14, the largest surface family"),
    (534, 40, "decision-curve", "RoadFines, the smallest curve family"),
    (1100, 80, "decision-curve", "the modal curve family"),
    (2966, 150, "decision-curve", "BPIC14/duration, the largest family of all"),
)
#  ROUND TWENTY-SEVEN adds `nonzero`.  The three regimes above all put the
#  truth at zero at every cell, and the file argued that a non-zero truth
#  "would be the same experiment run slower" because the band is equivariant
#  in the truth.  That argument is right about the band and wrong about the
#  experiment, for two reasons a reader is entitled to see tested rather than
#  reasoned about.  The pivotal recentring the paper applies is a function of
#  the bootstrap MEDIAN, which is equivariant only when the bootstrap
#  distribution is; and the resolved/unresolved verdict a region label rests
#  on is NOT equivariant, because "excludes zero" is a statement about a fixed
#  point and not about the truth.  Under a zero truth every rejection is a
#  false one and the experiment can only measure a type-I error; under a
#  non-zero truth a cell can be correctly resolved, and family-wise coverage
#  is then the quantity a region label actually depends on.  The truth is
#  fixed per family and drawn once, so replicates of one grid cell remain
#  replicates of one experiment.
REGIMES = ("gaussian", "heavy", "degenerate", "nonzero")

#: the non-zero regime's truth, in units of a cell's own sampling standard
#: deviation -- two, which is the neighbourhood in which a 95% band is
#: actually being asked to resolve a sign.
TRUTH_SCALE = 2.0
REPS = 2000

#: the draw-count sensitivity, at the modal surface cell.  400 is past where
#: the per-cell interval reaches nominal and is not affordable on the corpus;
#: it is here to show what the corpus's draw counts cost.
BSENS = (33, 80, 150, 400, 1000)

CANDIDATES = ("q_mult", "q_mult_hi", "q_emp", "q_emp_hi", "q_rad")

#: the calibration grids.  Small and declared; the fit each achieves is
#: written beside the target it was fitting.
CAL_P = (0.05, 0.10, 0.20, 0.35, 0.50, 0.75, 1.0)   # share of cells fragile
CAL_EPS = (0.01, 0.02, 0.05, 0.10)        # share of draws contaminated
CAL_LAM = (1.5, 2.0, 3.0, 4.0, 6.0, 9.0)  # what a contaminated draw is worth
CAL_R = (2, 4, 8, 16, 32, 64)
CAL_W = (0.05, 0.10, 0.20, 0.35, 0.50)
CAL_M = (0.0, 0.2, 0.4, 0.8)
CAL_REPS = 60
CAL_CELL = {"whole-surface": (180, 80), "decision-curve": (1100, 80)}

#: the degenerate regime: this share of cells is put on a lattice this many
#: standard deviations coarse, which makes most of their draws exactly zero.
#: Both are set from stage 1 rather than chosen -- see `main`.
DEGEN_LATTICE = 3.0

CELLKEY = ["learner", "split", "quality", "level", "rung"]


# --------------------------------------------------------------------------
# stage one: what shape is this corpus, actually
# --------------------------------------------------------------------------
def family_matrix(sub):
    """The (draws x cells) matrix `s21.critical` is handed, by its own steps
    and its own admission rule: any cell whose spread exceeds 1e-15."""
    Wm = sub.assign(_c=sub[CELLKEY + ["metric"]].astype(str).agg("|".join,
                                                                 axis=1))
    W = Wm.pivot_table(index="draw", columns="_c", values="V")
    se = W.std(axis=0, ddof=1)
    ok = se[se > 1e-15].index
    return W[ok] if len(ok) else None


def standardise(W):
    """Standardise, drop replicates that do not carry every cell, then drop
    cells that became constant when they were dropped.

    Returns the matrix and the per-cell count of draws the STANDARDISATION
    used, which is not the number of rows that survive: pandas takes each
    column's moments over its own non-missing entries and the row filter comes
    after.  The ceiling below is a function of the former.
    """
    se = W.std(axis=0, ddof=1)
    ok = se[se > 1e-15].index
    if len(ok) < 2:
        return None, None
    n_moments = W[ok].notna().sum(axis=0).values.astype(float)
    Z = ((W[ok] - W[ok].mean()) / se[ok]).values
    Z = Z[np.isfinite(Z).all(axis=1)]
    if len(Z) < 20:
        return None, None
    keep = Z.std(axis=0, ddof=1) > 1e-12
    return Z[:, keep], n_moments[keep]


def shape_of(Z, n_moments, rng, tag=""):
    """Family size, draw count, tails, dependence, and the ceiling.

    THE CEILING.  A deviate standardised over n points cannot exceed
    (n-1)/sqrt(n): the squared standardised values sum to n-1 and a single one
    takes as much of that as the zero-sum constraint allows.  A maximum over
    cells is bounded by the largest such bound in the family, so that is what
    `q_emp` is compared against.  It is a property of the count each cell's
    moments were taken over, which is why that count is carried here rather
    than read off the matrix's height.
    """
    B, K = Z.shape
    g2 = (Z ** 4).mean(axis=0) / ((Z ** 2).mean(axis=0) ** 2) - 3.0
    M = np.sort(np.abs(Z).max(axis=1))
    ceiling = float(((n_moments - 1) / np.sqrt(n_moments)).max())
    idx = np.arange(K) if K <= 400 else rng.choice(K, 400, replace=False)
    C = np.nan_to_num(np.corrcoef(Z[:, idx].T), nan=0.0)
    np.fill_diagonal(C, 1.0)
    C = (C + C.T) / 2.0
    off = C[~np.eye(len(idx), dtype=bool)]
    ev = np.clip(np.linalg.eigvalsh(C), 0, None)
    eff = float(ev.sum() ** 2 / max((ev ** 2).sum(), 1e-30))
    k = 1.0 - ALPHA
    q_emp = float(np.quantile(M, k))
    lo_i = int(np.floor(B * k - 1.96 * np.sqrt(B * k * (1 - k)))) - 1
    mq = B21.multiplier_quantile(Z, ALPHA)
    q = float(mq[0]) if mq else np.nan
    return {tag + "K": K, tag + "B": B,
            tag + "kurt_med": float(np.median(g2)),
            tag + "kurt_p90": float(np.percentile(g2, 90)),
            tag + "kurt_max": float(g2.max()),
            tag + "rho_mean": float(off.mean()),
            tag + "absrho_mean": float(np.abs(off).mean()),
            tag + "eff_rank": eff, tag + "eff_rank_frac": eff / len(idx),
            tag + "q": q, tag + "q_emp": q_emp,
            tag + "q_emp_lo": float(M[max(0, lo_i)]),
            tag + "ratio": q_emp / q if q else np.nan,
            tag + "below": bool(q < M[max(0, lo_i)]),
            tag + "ceiling": ceiling,
            tag + "q_emp_at_ceiling": bool(q_emp >= ceiling - 1e-6),
            tag + "share_draws_at_ceiling":
                float(np.mean(np.abs(Z).max(axis=1) >= ceiling - 1e-6))}


def profile(out_path, draws_dir="s20"):
    """Measure the shape of the corpus's own bootstrap families.

    ROUND TWENTY-SEVEN made `draws_dir` an argument.  It was the literal
    "s20", the OLD inference surface, and the round replaced that surface with
    a balanced 400-draw one --- so a coverage measured here would have been
    measured on families matched to a surface the manuscript no longer
    reports, and reported as the new band's coverage.  That is the same defect
    an audit found in `round21_numbers` the same night: a check that reads a
    fixed filename cannot notice that the analysis moved.
    """
    rng = np.random.default_rng(SEED)
    rows = []
    src = RESULTS / draws_dir
    if not src.exists():
        raise SystemExit("s41: no draws directory results/%s" % draws_dir)
    for fn in sorted(src.glob("draws_*.csv.gz")):
        D = pd.read_csv(fn)
        log, target = str(D.log.iloc[0]), str(D.target.iloc[0])
        D = D[~D.rung.isin(S.IMPLAUSIBLE_RUNGS)]
        bt = D[D.draw >= 0]
        for fam, sub in (("whole-surface", bt[bt.metric.isin(S.SCALARS)]),
                         ("decision-curve",
                          bt[bt.metric.str.startswith("nb_")])):
            if not len(sub):
                continue
            W = family_matrix(sub)
            if W is None:
                continue
            zero_share = (W == 0.0).sum(axis=0) / W.notna().sum(axis=0)
            n_distinct = W.nunique()
            Z, nm = standardise(W)
            if Z is None:
                continue
            row = dict(log=log, target=target, family=fam) | shape_of(Z, nm,
                                                                      rng)
            adm = zero_share[zero_share < TAU_DEGENERATE].index
            row["n_degenerate"] = int(W.shape[1] - len(adm))
            row["share_degenerate"] = 1.0 - len(adm) / float(W.shape[1])
            for t in TAU_ALT:
                row["n_degenerate_tau%02d" % round(100 * t)] = \
                    int((zero_share >= t).sum())
            #  the discreteness that produces the tail, independently of the
            #  zero-share rule: how many cells take few distinct values
            row["n_lowdistinct_20"] = int((n_distinct <= 20).sum())
            row["share_lowdistinct_20"] = float((n_distinct <= 20).mean())
            if len(adm) >= 2:
                Za, nma = standardise(W[adm])
                if Za is not None:
                    row |= shape_of(Za, nma, rng, tag="adm_")
            rows.append(row)
        print("  profiled %s" % fn.name, flush=True)
    P = pd.DataFrame(rows)
    P.to_csv(out_path, index=False)
    return P


# --------------------------------------------------------------------------
# the population, and one replicate of the whole procedure
# --------------------------------------------------------------------------
def loadings(K, r, m, seed):
    """Cell loadings on the r shared factors, scaled to unit norm so that `w`
    is exactly the share of a cell's variance the factors carry.  `m` shifts
    them off zero, which is what makes the average cross-cell correlation
    POSITIVE: with m = 0 the loadings are symmetric about zero and so is the
    mean correlation, and the corpus's is not."""
    rng = np.random.default_rng(seed)
    L = rng.standard_normal((K, r)) + m
    return L / np.sqrt((L ** 2).sum(axis=1, keepdims=True))


def truth_vector(K, regime, seed):
    """The truth at every cell of a family: zero under the three regimes that
    had it, and a fixed heterogeneous vector under `nonzero`.  Drawn from the
    family's own seed, so it is a property of the family and not of the
    replicate."""
    if regime != "nonzero":
        return np.zeros(K)
    rng = np.random.default_rng(seed + 5779)
    return TRUTH_SCALE * rng.standard_normal(K)


def fragile_cells(K, p, seed):
    """Which cells a contaminated draw is amplified at.  Fixed for a family,
    so every replicate of one grid cell is a replicate of ONE experiment."""
    m = np.zeros(K, bool)
    if p > 0:
        rng = np.random.default_rng(seed + 1)
        m[rng.choice(K, max(1, int(round(p * K))), replace=False)] = True
    return m


def draw_family(n, K, L, w, frag, eps, lam, rng):
    """n independent draws from the sampling distribution of the standardised
    estimator: mean zero, unit variance at every cell, the corpus's dependence
    and, on the fragile cells, its tails.

    Contamination is drawn once per DRAW and applied to every fragile cell of
    it, so an excursion arrives across the family at once.
    """
    X = (np.sqrt(w) * (rng.standard_normal((n, L.shape[1])) @ L.T)
         + np.sqrt(1.0 - w) * rng.standard_normal((n, K)))
    if eps <= 0 or lam == 1.0 or not frag.any():
        return X
    hit = rng.random(n) < eps
    cols = np.flatnonzero(frag)
    X[np.ix_(hit, cols)] *= lam
    X[:, cols] /= np.sqrt((1.0 - eps) + eps * lam * lam)
    return X


def rademacher_quantile(Z, alpha=ALPHA, n_mult=B21.N_MULT, seed=0):
    """The wild multiplier quantile with Rademacher weights.

    Identical to `s21.multiplier_quantile` except that e_b is +-1 rather than
    N(0,1).  The two have the same first two moments, so they agree exactly on
    the covariance the Gaussian construction is justified by; they differ in
    that this one carries an observed row of Z into the maximum at full
    magnitude instead of scaling a Gaussian by it.
    """
    rng = np.random.default_rng(seed)
    B, K = Z.shape
    if B < 20 or K == 0:
        return None
    out = np.empty(n_mult, float)
    done = 0
    while done < n_mult:
        m = min(B21.CHUNK, n_mult - done)
        E = rng.integers(0, 2, size=(m, B)).astype(float) * 2.0 - 1.0
        out[done:done + m] = (np.abs(E @ Z) / np.sqrt(B)).max(axis=1)
        done += m
    return float(np.quantile(out, 1.0 - alpha))


def one_rep(task):
    """One replicate: draw an estimate and its ideal bootstrap, build every
    candidate band, and ask whether each covers the truth at EVERY cell at
    once.

    The truth is zero at every cell, so a cell whose band excludes zero is a
    cell this family has resolved wrongly, and one minus the family-wise
    coverage is the rate at which a family produces at least one such cell.
    That is the quantity a region label depends on: `uniformly beneficial`
    quantifies over every cell of the family, so one wrong cell is one wrong
    label.  `--selftest` shows the construction is equivariant in the truth,
    so a non-zero truth would be the same experiment run slower.
    """
    (K, Bd, fam, regime, par, rep) = task
    K_nom = K
    rng = np.random.default_rng(SEED + 7919 * rep + 13 * K + 31 * Bd
                                + 101 * REGIMES.index(regime))
    L = loadings(K, par["r"], par["m"], SEED + 101 * K)
    frag = fragile_cells(K, par["p"], SEED + 211 * K)
    eps, lam = ((0.0, 1.0) if regime == "gaussian"
                else (par["eps"], par["lam"]))

    #  one draw for the estimate and Bd for the bootstrap, from the SAME
    #  distribution: the bootstrap is ideal by construction
    mu = truth_vector(K, regime, SEED + 101 * K)
    X = draw_family(Bd + 1, K, L, w=par["w"], frag=frag, eps=eps, lam=lam,
                    rng=rng)
    #  the estimate is the truth plus one draw from the sampling distribution,
    #  and the bootstrap is Bd more draws centred on the estimate -- which is
    #  the ideal bootstrap, as before, and reduces to the old line when mu = 0
    V_hat, Wd = mu + X[0], X[1:] + (mu + X[0])

    if regime == "degenerate":
        #  a share of cells put on a lattice coarse enough that most of their
        #  draws land on exactly zero: the decision-curve cells of stage 1.
        #  Their own band is trivially right; the question is what they do to
        #  the critical value every other cell is judged by.
        dg = fragile_cells(K, par["share_degenerate"], SEED + 307 * K)
        Wd[:, dg] = np.round(Wd[:, dg] / DEGEN_LATTICE) * DEGEN_LATTICE
        V_hat = V_hat.copy()
        V_hat[dg] = np.round(V_hat[dg] / DEGEN_LATTICE) * DEGEN_LATTICE

    se = Wd.std(axis=0, ddof=1)
    keep = se > 1e-15
    if keep.sum() < 2:
        return None
    Wd, se, V_hat, mu = Wd[:, keep], se[keep], V_hat[keep], mu[keep]
    Z = (Wd - Wd.mean(axis=0)) / se
    ok = Z.std(axis=0, ddof=1) > 1e-12
    Z, Wd, se, V_hat, mu = Z[:, ok], Wd[:, ok], se[ok], V_hat[ok], mu[ok]

    mq = B21.multiplier_quantile(Z, ALPHA, seed=int(rng.integers(1 << 31)))
    if mq is None:
        return None
    q_mult, _q_lo, q_mult_hi = mq
    q_rad = rademacher_quantile(Z, ALPHA, seed=int(rng.integers(1 << 31)))

    T = np.sort(np.abs(Z).max(axis=1))
    k = 1.0 - ALPHA
    q_emp = float(np.quantile(T, k))
    hi_i = int(np.ceil(Bd * k + 1.96 * np.sqrt(Bd * k * (1 - k)))) - 1
    q_emp_hi = float(T[min(len(T) - 1, hi_i)])
    ceiling = (Bd - 1) / np.sqrt(Bd)

    #  the basic (pivotal) recentring s21 applies before it widens
    centre = V_hat - (np.median(Wd, axis=0) - V_hat)
    #  THE CONTROL: the per-cell basic interval, on the same draws
    lo_b = 2 * V_hat - np.percentile(Wd, 100 * (1 - ALPHA / 2), axis=0)
    hi_b = 2 * V_hat - np.percentile(Wd, 100 * ALPHA / 2, axis=0)

    g2 = (Z ** 4).mean(axis=0) / ((Z ** 2).mean(axis=0) ** 2) - 3.0
    #  K_nom is the family the grid ASKED for and K what survived the
    #  admission filter.  They differ in the degenerate regime, where a cell
    #  whose draws all landed on one lattice point has no spread and is
    #  dropped -- and grouping on the realised K would then split one
    #  experiment into a group per distinct survivor count, which it did.
    out = dict(K_nom=K_nom, K=int(Z.shape[1]), B=Bd, family=fam,
               regime=regime, rep=rep,
               truth_scale=float(np.abs(mu).mean()),
               cov_point_basic=float(np.mean((lo_b <= mu) & (mu <= hi_b))),
               q_mult=q_mult, q_mult_hi=q_mult_hi, q_emp=q_emp,
               q_emp_hi=q_emp_hi, q_rad=q_rad, ceiling=ceiling,
               q_emp_at_ceiling=bool(q_emp >= ceiling - 1e-9),
               kurt_med=float(np.median(g2)),
               kurt_p90=float(np.percentile(g2, 90)),
               #  the value that WOULD have covered on this replicate, had it
               #  been known: every candidate is trying to estimate its 95th
               #  percentile across replicates
               t_max=float(np.abs((centre - mu) / se).max()))
    for name in CANDIDATES:
        q = out[name]
        lo, hi = centre - q * se, centre + q * se
        out["cov_all_" + name] = bool(np.all((lo <= mu) & (mu <= hi)))
        out["cov_point_" + name] = float(np.mean((lo <= mu) & (mu <= hi)))
        out["width_" + name] = float(np.mean(hi - lo))
        #  a FALSE resolution is a cell whose band excludes zero on the wrong
        #  side of the truth.  Under a zero truth that is any cell the band
        #  resolves, which is what this counted before; under a non-zero truth
        #  a cell the band resolves in the truth's own direction is a CORRECT
        #  resolution, and only a sign error counts.
        res_pos, res_neg = lo > 0, hi < 0
        out["n_resolved_" + name] = int(np.sum(res_pos | res_neg))
        out["n_false_" + name] = int(np.sum((res_pos & (mu <= 0))
                                            | (res_neg & (mu >= 0))))
    return out


# --------------------------------------------------------------------------
# stage two: calibrate the population to the shape stage one measured
# --------------------------------------------------------------------------
def dependence_fit(K, r, w, m, seed):
    """The mean correlation and effective rank a (r, w, m) gives, in closed
    form from the loadings: corr(c, c') = w <l_c, l_c'> for unit-norm loadings,
    because the idiosyncratic parts are independent.  No simulation is needed
    for this half, which is why it is separated from the tail half."""
    L = loadings(K, r, m, seed)
    idx = (np.arange(K) if K <= 400
           else np.random.default_rng(seed).choice(K, 400, replace=False))
    C = w * (L[idx] @ L[idx].T)
    np.fill_diagonal(C, 1.0)
    off = C[~np.eye(len(idx), dtype=bool)]
    ev = np.clip(np.linalg.eigvalsh((C + C.T) / 2.0), 0, None)
    return (float(off.mean()), float(np.abs(off).mean()),
            float(ev.sum() ** 2 / max((ev ** 2).sum(), 1e-30)) / len(idx))


def calibrate(P, procs):
    """Grid search, in two independent halves because the knobs are: (r, w, m)
    set the dependence and not the tails, and (p, eps, lam) set the tails and
    not the dependence, since every cell is returned to unit variance.  Joint
    search would have cost the product of the grids to learn the same answer.

    The targets are the corpus medians for that family type, taken from the
    ADMISSIBLE cells where stage 1 could compute them, because a population
    calibrated to include the degenerate cells' kurtosis would be calibrated
    to an artefact.  The degenerate regime puts them back deliberately.
    """
    rows = []
    for fam in ("whole-surface", "decision-curve"):
        F = P[P.family == fam]
        col = (lambda c: F["adm_" + c] if ("adm_" + c) in F
               and F["adm_" + c].notna().any() else F[c])
        tgt = dict(rho_mean=float(col("rho_mean").median()),
                   absrho_mean=float(col("absrho_mean").median()),
                   eff_rank_frac=float(col("eff_rank_frac").median()),
                   kurt_med=float(col("kurt_med").median()),
                   kurt_p90=float(col("kurt_p90").median()))
        K, Bd = CAL_CELL[fam]

        best, best_loss = None, np.inf
        for r in CAL_R:
            for w in CAL_W:
                for m in CAL_M:
                    rm, am, ef = dependence_fit(K, r, w, m, SEED + 101 * K)
                    loss = ((rm - tgt["rho_mean"]) ** 2
                            + (am - tgt["absrho_mean"]) ** 2
                            + (ef - tgt["eff_rank_frac"]) ** 2)
                    if loss < best_loss:
                        best, best_loss = dict(r=r, w=w, m=m), loss
        rm, am, ef = dependence_fit(K, best["r"], best["w"], best["m"],
                                    SEED + 101 * K)

        combos = [(p, e, la) for p in CAL_P for e in CAL_EPS for la in CAL_LAM]
        tasks = [(K, Bd, fam, "heavy",
                  dict(best) | dict(p=p, eps=e, lam=la, share_degenerate=0.0),
                  i)
                 for (p, e, la) in combos for i in range(CAL_REPS)]
        got = _run(tasks, procs, "calibrate/%s" % fam)
        keep = [(t, g) for t, g in zip(tasks, got) if g]
        G = pd.DataFrame([g for _t, g in keep])
        for fld in ("p", "eps", "lam"):
            G[fld] = [t[4][fld] for t, _g in keep]
        A = G.groupby(["p", "eps", "lam"])[["kurt_med",
                                            "kurt_p90"]].median().reset_index()
        #  relative error, because the two targets differ by an order of
        #  magnitude and an absolute loss would fit only the larger
        A["loss"] = (((A.kurt_med - tgt["kurt_med"])
                      / max(abs(tgt["kurt_med"]), .1)) ** 2
                     + ((A.kurt_p90 - tgt["kurt_p90"])
                        / max(abs(tgt["kurt_p90"]), .1)) ** 2)
        i = A.loss.idxmin()
        best |= dict(p=float(A.p[i]), eps=float(A.eps[i]), lam=float(A.lam[i]),
                     share_degenerate=float(F.share_degenerate.max()))
        rows.append(dict(
            family=fam, cal_K=K, cal_B=Bd, **best,
            target_rho_mean=tgt["rho_mean"], fit_rho_mean=rm,
            target_absrho_mean=tgt["absrho_mean"], fit_absrho_mean=am,
            target_eff_rank_frac=tgt["eff_rank_frac"], fit_eff_rank_frac=ef,
            target_kurt_med=tgt["kurt_med"], fit_kurt_med=float(A.kurt_med[i]),
            target_kurt_p90=tgt["kurt_p90"], fit_kurt_p90=float(A.kurt_p90[i]),
            n_cal_reps=CAL_REPS, n_cal_combos=len(A)))
        print("  calibrated %-15s r=%d w=%.2f m=%.1f | p=%.2f eps=%.2f "
              "lam=%.1f | kurt %.2f/%.2f against %.2f/%.2f"
              % (fam, best["r"], best["w"], best["m"], best["p"], best["eps"],
                 best["lam"], A.kurt_med[i], A.kurt_p90[i],
                 tgt["kurt_med"], tgt["kurt_p90"]), flush=True)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def _run(tasks, procs, label):
    import multiprocessing as mp
    n = procs or min(12, max(1, (os.cpu_count() or 4) - 2))
    t0 = time.time()
    out = []
    with mp.Pool(processes=n) as pool:
        for i, r in enumerate(pool.imap(one_rep, tasks, chunksize=4)):
            out.append(r)
            if (i + 1) % 2000 == 0:
                print("    %s %d/%d  %.0fs"
                      % (label, i + 1, len(tasks), time.time() - t0),
                      flush=True)
    return out


def summarise(R):
    """Family-wise and pointwise coverage per cell and candidate, each with
    its Monte Carlo standard error.  At 2000 replicates a coverage near 0.95
    is resolved to about 0.5 percentage points; differences below that are not
    differences, which is why the standard error is on every row rather than
    quoted once in a caption."""
    rows = []
    grp = ["family", "regime", "K_nom", "B"]
    for key, sub in R.groupby(grp):
        for c in CANDIDATES:
            fw = sub["cov_all_" + c].astype(float)
            n = len(fw)
            cov = float(fw.mean())
            rows.append(dict(zip(grp, key)) | dict(
                candidate=c, n=n, coverage=cov, K=float(sub.K.mean()),
                coverage_se=float(np.sqrt(max(cov * (1 - cov), 1e-12) / n)),
                coverage_pointwise=float(sub["cov_point_" + c].mean()),
                coverage_percell_basic=float(sub.cov_point_basic.mean()),
                mean_width=float(sub["width_" + c].mean()),
                q_median=float(sub[c].median()),
                q_oracle=float(sub.t_max.quantile(1 - ALPHA)),
                #  THE FACTOR THE BAND IS SHORT BY: the multiplicative
                #  widening that WOULD have given nominal family-wise
                #  coverage on this cell.  It is the quantity to compare the
                #  coverage calibration of Section 6.4 against, because that
                #  calibration is a multiplicative widening of exactly this
                #  critical value -- fitted to restore POINTWISE coverage,
                #  and therefore not fitted to this.
                #
                #  Widening by f covers when f*q >= t_max, so the f attaining
                #  nominal is the (1-alpha) quantile of t_max/q taken WITHIN
                #  the replicate.  The ratio of the two marginal quantiles is
                #  not the same number: q and t_max are estimated from the
                #  same draws and move together, and the first version of
                #  this line used the ratio.
                shortfall_factor=float(
                    (sub.t_max / sub[c].replace(0, np.nan)).quantile(
                        1 - ALPHA)),
                mean_false_cells=float(sub["n_false_" + c].mean()),
                #  under a non-zero truth a resolved cell is not automatically
                #  a mistake, so the two are counted apart: `mean_resolved` is
                #  how much the band decides and `mean_false_cells` how much
                #  of that it gets wrong.  A band that resolves nothing has a
                #  perfect false rate and is useless, which is the failure
                #  mode the zero-truth regimes cannot see.
                mean_resolved_cells=float(sub["n_resolved_" + c].mean()),
                truth_scale=float(sub.truth_scale.mean()),
                kurt_med=float(sub.kurt_med.median()),
                kurt_p90=float(sub.kurt_p90.median()),
                share_q_emp_at_ceiling=float(sub.q_emp_at_ceiling.mean())))
    return pd.DataFrame(rows)


def selftest():
    """Two exactness checks the experiment's reading depends on.

    ONE, equivariance in the truth.  Adding a constant to a cell shifts the
    estimate, every draw, the band and the estimand by the same amount, so
    coverage at a non-zero truth is the SAME EVENT as coverage at zero.  A
    coverage measured only at zero would otherwise be exactly that.

    TWO, the population is what it says it is.  Every cell must have unit
    variance under contamination, or `w` stops being the share of variance the
    factors carry and the dependence calibration silently means something
    else.
    """
    par = dict(r=8, w=0.2, m=0.4, p=0.2, eps=0.05, lam=4.0)
    rng = np.random.default_rng(SEED)
    K, Bd = 60, 60
    L = loadings(K, par["r"], par["m"], SEED)
    frag = fragile_cells(K, par["p"], SEED)
    X = draw_family(Bd + 1, K, L, par["w"], frag, par["eps"], par["lam"], rng)
    V, Wd = X[0], X[1:] + X[0]
    mu = rng.standard_normal(K) * 0.3

    def band(v, W):
        se = W.std(axis=0, ddof=1)
        c = v - (np.median(W, axis=0) - v)
        return c - 2.5 * se, c + 2.5 * se

    lo0, hi0 = band(V, Wd)
    lo1, hi1 = band(V + mu, Wd + mu)
    d = max(np.abs((lo1 - mu) - lo0).max(), np.abs((hi1 - mu) - hi0).max())
    ok0 = (lo0 <= 0) & (0 <= hi0)
    ok1 = (lo1 <= mu) & (mu <= hi1)
    print("  equivariance: max endpoint shift error %.3e" % d)
    print("  same coverage event at every cell: %s" % bool((ok0 == ok1).all()))

    #  THREE, the verdict is NOT equivariant, which is why `nonzero` is a
    #  regime and not an argument.  Coverage of the truth is the same event
    #  at every truth (check one); "the band excludes zero" is not, because
    #  zero is a fixed point and the truth moves relative to it.  A file that
    #  measures only coverage at zero can therefore report a band that never
    #  resolves anything as a band that never errs.
    res0 = int(np.sum((lo0 > 0) | (hi0 < 0)))
    res1 = int(np.sum((lo1 > 0) | (hi1 < 0)))
    print("  cells the band resolves: %d at truth zero, %d at truth mu -- "
          "equivariant verdict: %s" % (res0, res1, res0 == res1))
    #  and the non-zero regime's own truth must be non-zero and heterogeneous
    tv = truth_vector(200, "nonzero", SEED)
    z = truth_vector(200, "heavy", SEED)
    print("  truth vector: |mu| mean %.3f, sd %.3f, zero regimes at %.3f"
          % (float(np.abs(tv).mean()), float(tv.std()),
             float(np.abs(z).max())))

    big = draw_family(400000, 200, loadings(200, 8, 0.4, SEED),
                      0.2, fragile_cells(200, 0.2, SEED), 0.05, 4.0,
                      np.random.default_rng(SEED + 5))
    v = big.var(axis=0)
    print("  cell variance under contamination: %.4f to %.4f (want 1)"
          % (v.min(), v.max()))

    #  THREE, the critical value against a case with a closed form.  For K
    #  INDEPENDENT standard Gaussian cells the max-$t$ critical value solves
    #  (2 Phi(x) - 1)^K = 1 - alpha, so the estimator can be checked rather
    #  than trusted.  Given enough draws that the sample correlation is
    #  essentially the true one, `multiplier_quantile` must return it.  This
    #  is the check that says a coverage below nominal in stage 3 is a
    #  property of the draw counts and not of this file.
    from scipy.stats import norm
    r3 = np.random.default_rng(SEED + 9)
    for K in (20, 180):
        want = float(norm.ppf((1 + (1 - ALPHA) ** (1.0 / K)) / 2.0))
        Zi = r3.standard_normal((20000, K))
        Zi = (Zi - Zi.mean(axis=0)) / Zi.std(axis=0, ddof=1)
        got = B21.multiplier_quantile(Zi, ALPHA, seed=3)[0]
        print("  independent K=%3d: multiplier %.4f, closed form %.4f, "
              "error %+.4f" % (K, got, want, got - want))
        if abs(got - want) > 0.05:
            raise SystemExit("s41 selftest FAILED: multiplier_quantile is "
                             "%.4f where the closed form is %.4f"
                             % (got, want))
    if d > 1e-9 or not (ok0 == ok1).all() or not (0.95 < v.min()
                                                  and v.max() < 1.05):
        raise SystemExit("s41 selftest FAILED")
    print("  selftest OK")


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="profile,calibrate,coverage")
    ap.add_argument("--reps", type=int, default=0)
    ap.add_argument("--procs", type=int, default=0)
    ap.add_argument("--draws-dir", default="s20",
                    help="the results/ subdirectory of bootstrap draw files "
                         "whose family shape the synthetic populations are "
                         "matched to; round 27's surface is s44_weighted")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--resummarise", action="store_true",
                    help="re-derive the coverage table and the facts from the "
                         "replicates already on disk, without simulating")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    stages = [s.strip() for s in a.only.split(",") if s.strip()]
    reps = a.reps or REPS
    full = reps >= REPS
    prefix = "s41_" if full else "s41_smoke_"

    if a.plan:
        n = len(GRID) * len(REGIMES) * reps + len(BSENS) * reps
        cal = 2 * CAL_REPS * len(CAL_P) * len(CAL_EPS) * len(CAL_LAM)
        print("  coverage    %6d replicates over %d cells"
              % (n, len(GRID) * len(REGIMES) + len(BSENS)))
        print("  calibrate   %6d replicates" % cal)
        print("  no pipeline is refitted: the cost is matrix arithmetic")
        return

    t0 = time.time()
    print("=" * 92)
    print("s41  THE BAND'S FAMILY-WISE COVERAGE, AGAINST A KNOWN ANSWER")
    print("=" * 92)
    if not full:
        print("  !! SHORT RUN: %d replicates below the declared %d.  Writing "
              "%s*, which nothing in the manuscript reads." % (reps, REPS,
                                                               prefix))

    #  the profile is cached PER SOURCE, so switching surfaces cannot serve a
    #  stale profile from the previous one
    _sfx = "" if a.draws_dir == "s20" else "_" + a.draws_dir
    ppath = RESULTS / ("s41_profile%s.csv" % _sfx)
    if "profile" in stages or not ppath.exists():
        print("\nSTAGE 1  the shape of the corpus's own families (%s)"
              % a.draws_dir)
        P = profile(ppath, a.draws_dir)
    else:
        P = pd.read_csv(ppath)
    ws, dc = P[P.family == "whole-surface"], P[P.family == "decision-curve"]
    print("  %d families: K %d-%d, B %d-%d" % (len(P), P.K.min(), P.K.max(),
                                               P.B.min(), P.B.max()))
    print("  degenerate cells: %d in the curve families, %d in the surface "
          "ones; q_emp on its ceiling in %d of %d curve families"
          % (int(dc.n_degenerate.sum()), int(ws.n_degenerate.sum()),
             int(dc.q_emp_at_ceiling.sum()), len(dc)))
    print("  ratio q_emp/q, curve families: %.2f over all cells, %.2f over "
          "the admissible ones" % (dc.ratio.median(), dc.adm_ratio.median()))

    cpath = RESULTS / "s41_calibration.csv"
    if "calibrate" in stages or not cpath.exists():
        print("\nSTAGE 2  a population matched to that shape")
        CAL = calibrate(P, a.procs)
        CAL.to_csv(cpath, index=False)
    else:
        CAL = pd.read_csv(cpath)
    par = {r.family: dict(r=int(r.r), w=float(r.w), m=float(r.m),
                          p=float(r.p), eps=float(r.eps), lam=float(r.lam),
                          share_degenerate=float(r.share_degenerate))
           for r in CAL.itertuples()}

    if "coverage" not in stages:
        return
    print("\nSTAGE 3  coverage of five candidate critical values")
    tasks = []
    for (K, Bd, fam, _why) in GRID:
        for regime in REGIMES:
            tasks += [(K, Bd, fam, regime, par[fam], r) for r in range(reps)]
    for Bd in BSENS:
        tasks += [(180, Bd, "whole-surface", "heavy", par["whole-surface"], r)
                  for r in range(reps)]
    print("  %d replicates over %d cells"
          % (len(tasks), len(GRID) * len(REGIMES) + len(BSENS)))
    if a.resummarise:
        R = pd.read_csv(RESULTS / (prefix + "replicates.csv.gz"))
        print("  re-derived from %d replicates already on disk" % len(R))
    else:
        R = pd.DataFrame([r for r in _run(tasks, a.procs, "coverage") if r])
        R.to_csv(RESULTS / (prefix + "replicates.csv.gz"), index=False,
                 compression="gzip")
    C = summarise(R)
    C.to_csv(RESULTS / (prefix + "coverage.csv"), index=False)

    #  the sensitivity rows share (family, K) with a grid cell, so every
    #  selector below names B as well -- and it names K_nom and not K, which
    #  is the family the grid ASKED for.  Selecting on the realised K silently
    #  dropped every degenerate-regime row, because a cell whose draws all
    #  landed on one lattice point is not there to be counted: the minimum
    #  coverage of the multiplier came out 0.835 when the experiment had
    #  measured 0.392.
    grid_B = {(K, Bd) for (K, Bd, _f, _w) in GRID}
    G = C[[(k, b) in grid_B for k, b in zip(C.K_nom, C.B)]]
    heavy = G[G["regime"] == "heavy"]

    def cv(regime, cand, how="median"):
        s = G[(G.regime == regime) & (G.candidate == cand)].coverage
        return float(getattr(s, how)()) if len(s) else np.nan

    def wd(regime, cand):
        s = G[(G.regime == regime) & (G.candidate == cand)].mean_width
        return float(s.median()) if len(s) else np.nan

    BS = C[(C.K == 180) & (C.regime == "heavy")]
    facts = dict(
        n_reps=int(reps), n_cells=int(G.groupby(["family", "regime", "K",
                                                 "B"]).ngroups),
        k_min=int(C.K.min()), k_max=int(C.K.max()),
        b_min=int(C.B.min()), b_max=int(C.B.max()),
        coverage_se_max=float(C.coverage_se.max()),
        n_corpus_families=len(P),
        n_degenerate_dca=int(dc.n_degenerate.sum()),
        n_degenerate_whole=int(ws.n_degenerate.sum()),
        share_degenerate_dca_max=float(dc.share_degenerate.max()),
        n_qemp_ceiling_dca=int(dc.q_emp_at_ceiling.sum()),
        n_qemp_ceiling_dca_adm=int(dc.adm_q_emp_at_ceiling.sum()),
        ratio_dca_all=float(dc.ratio.median()),
        ratio_dca_adm=float(dc.adm_ratio.median()),
        ratio_whole_all=float(ws.ratio.median()),
        n_below_dca_adm=int(dc.adm_below.sum()),
        n_below_whole_adm=int(ws.adm_below.sum()),
        corpus_kurt_med_whole=float(ws.kurt_med.median()),
        corpus_kurt_p90_whole=float(ws.kurt_p90.median()),
        corpus_kurt_med_dca_adm=float(dc.adm_kurt_med.median()),
        corpus_kurt_p90_dca_adm=float(dc.adm_kurt_p90.median()),
        corpus_lowdistinct_dca=float(dc.share_lowdistinct_20.median()),
        #  what the multiplier band would have to be widened BY, under the
        #  corpus's own tails, on each family type
        shortfall_whole_min=float(
            heavy[(heavy.candidate == "q_mult")
                  & (heavy.family == "whole-surface")].shortfall_factor.min()),
        shortfall_whole_max=float(
            heavy[(heavy.candidate == "q_mult")
                  & (heavy.family == "whole-surface")].shortfall_factor.max()),
        shortfall_dca_min=float(
            heavy[(heavy.candidate == "q_mult")
                  & (heavy.family == "decision-curve")].shortfall_factor.min()),
        shortfall_dca_max=float(
            heavy[(heavy.candidate == "q_mult")
                  & (heavy.family == "decision-curve")].shortfall_factor.max()),
        runtime_s=round(time.time() - t0, 1))
    for regime in REGIMES:
        for cand in CANDIDATES:
            facts["cov_%s_%s_median" % (cand, regime)] = cv(regime, cand)
            facts["cov_%s_%s_min" % (cand, regime)] = cv(regime, cand, "min")
    for cand in ("q_emp_hi", "q_rad", "q_emp"):
        facts["width_%s_over_mult_heavy" % cand] = (wd("heavy", cand)
                                                    / wd("heavy", "q_mult"))
    for Bd in BSENS:
        s = BS[(BS.B == Bd) & (BS.candidate == "q_mult")]
        if len(s):
            facts["cov_mult_B%d" % Bd] = float(s.coverage.iloc[0])
            facts["cov_percell_B%d" % Bd] = float(
                s.coverage_percell_basic.iloc[0])
    pd.DataFrame([facts]).to_csv(RESULTS / (prefix + "facts.csv"), index=False)
    print()
    print(C.to_string(index=False, float_format=lambda x: "%.4f" % x))
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

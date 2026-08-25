"""s34 -- WHAT THE SIGN-DISAGREEMENT RATE COUNTS, AND OVER WHICH CORPUS.

Round twenty-one, review comments M4 and M10.

M4.  THE HEADLINE COUNTS CELLS WHOSE SIGN IS NOISE.  The reported misreport
rate is the weighted share of admissible cells whose point estimate has the
opposite sign from the cell a conventional report would stand on.  On the
median pair, 159 of 180 cells are unresolved: their sign is not determined by
the data, and sign agreement between two draws from a distribution centred
near zero is one half by construction.  A rate computed over them is partly
measuring that.  Three quantities are therefore reported instead of one:

  ALL CELLS         the existing definition, kept so the change is visible
  RESOLVED ONLY     restricted to cells whose whole-surface simultaneous band
                    excludes zero -- cells whose sign the data does determine
  MAGNITUDE-WEIGHTED   every cell weighted by |V| as well as by the declared
                    measure, so a disagreement about a cell worth 0.0001 AUC
                    counts for a ten-thousandth of one worth 0.1

The resolved-only rate is reported with the count it is computed on, because
on some pairs that count is small and a rate over four cells is not a rate.
A pair with no resolved cell has no resolved-only rate and is reported as
having none rather than as having zero.

M4b.  THE AXES ARE NOT ALL THE SAME KIND OF THING, AND POOLING THEM INFLATES
THE RATE.  The design space mixes three kinds of axis and the manuscript's
headline averages over all of them:

  ANALYST LATITUDE   the pipeline, the baseline rung and the instrument.
                     These are choices an analyst makes and could have made
                     otherwise, and they are what a reader of a one-number
                     report is exposed to.
  RESAMPLING         the split.  Five of its six levels are expanding-origin
                     folds on the same data: different SAMPLES, not different
                     analyses.  Section 4.2 insists that specification
                     sensitivity and sampling uncertainty answer different
                     questions, and then puts the split in the decomposition.
  COUNTERFACTUAL     the register-quality condition.  A degraded register is
                     a different state of the world, not a different way of
                     analysing this one.

The rate restricted to the analyst-latitude axes -- clean register, single
temporal holdout, varying only the pipeline, the rung and the instrument -- is
the one a reader will understand the headline to mean, and it is reported
beside the pooled one rather than instead of it.  The same partition is
applied to the variance decomposition.

M10.  THE CORPUS IS NOT ONE POPULATION.  Eight of the nineteen pairs are IT
service management, where the register is a maintained configuration or
customer register and the construct is what this paper is about; the other
eleven include a loan amount, a case-type reference and an article of law.
Section 5.4 promised every corpus statistic separately for the ITSM family and
Section 6 did not deliver it.  This file computes every headline corpus
statistic on both populations and on the eleven that remain, so a reader can
see which conclusions are carried by the construct and which by the rest.

    python s34_reporting.py

Outputs: results/s34_misreport.csv   per pair: three rates, three measures
         results/s34_family.csv      every headline statistic, three
                                     populations, with the count behind it
         results/s34_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import s22_anova as A22  # noqa: E402
import s23_regret as S23  # noqa: E402
from common import RESULTS  # noqa: E402

MEASURES = ("equal-level", "reference", "concentrated")
CELLKEY = ["learner", "split", "quality", "level", "rung", "metric"]
ITSM = "itsm"


# --------------------------------------------------------------------------
def resolved_map():
    """Which (pair, cell) the whole-surface band resolves, under the nominal
    critical value and under the calibrated one when s33 has produced it."""
    B = pd.read_csv(RESULTS / "s21_bands.csv.gz")
    W = B[B.family == "whole-surface"].copy()
    W["resolved_nominal"] = (W.cons_lo > 0) | (W.cons_hi < 0)
    W["resolved_calibrated"] = W["resolved_nominal"]
    p = RESULTS / "s33_regions.csv"
    if p.exists():
        G = pd.read_csv(p)
        c = {(r.log, r.target): float(r.c) for r in G.itertuples()}
        f = np.array([c.get((l, t), 1.0) for l, t in zip(W.log, W.target)])
        lo = W.centre - f * W.q_hi * W.se
        hi = W.centre + f * W.q_hi * W.se
        W["resolved_calibrated"] = (lo > 0) | (hi < 0)
    keep = ["log", "target"] + CELLKEY + ["resolved_nominal",
                                          "resolved_calibrated"]
    return W[[c for c in keep if c in W.columns]]


def three_rates(SC, RES):
    """Per pair and measure: the three sign-disagreement rates."""
    axes5 = tuple(list(S23.AXES) + ["metric"])
    key = [c for c in CELLKEY if c in RES.columns]
    rows = []
    for (log, target), sub in SC.groupby(["log", "target"]):
        if len(sub) < 16:
            continue
        r = RES[(RES.log == log) & (RES.target == target)]
        sub = sub.copy()
        #  the surface names the quality axis by (quality, level); the band
        #  file names it the same way, so the join is on the cell itself
        if len(r):
            sub = sub.merge(r.drop(columns=["log", "target"]), on=key,
                            how="left")
        for c in ("resolved_nominal", "resolved_calibrated"):
            if c not in sub.columns:
                sub[c] = False
            sub[c] = sub[c].fillna(False).astype(bool)
        v = sub.V.values.astype(float)
        v_conv = S23.reference_value(
            sub[sub.metric == A22.REFERENCE["metric"]]
            if (sub.metric == A22.REFERENCE["metric"]).any() else sub)
        disagree = (v > 0) if v_conv <= 0 else (v <= 0)
        #  the analyst-latitude sub-space: the register clean and the split
        #  at the single temporal holdout, so the only things varying are the
        #  three axes an analyst chooses
        lat = ((sub.quality.astype(str) == "clean")
               & (sub.split.astype(str) == "holdout70")).values
        for meas in MEASURES:
            w = S23.product_weights(sub, meas, axes=axes5)
            all_rate = float((w * disagree).sum() / w.sum())
            out = dict(log=log, target=target, measure=meas,
                       n_cells=len(sub), v_reference=v_conv,
                       misreport_all=all_rate)
            wl = w * lat
            out["n_cells_latitude"] = int(lat.sum())
            out["misreport_latitude"] = (float((wl * disagree).sum()
                                               / wl.sum())
                                         if wl.sum() > 0 else np.nan)
            mag = w * np.abs(v)
            out["misreport_magnitude"] = (float((mag * disagree).sum()
                                                / mag.sum())
                                          if mag.sum() > 0 else np.nan)
            for tag, col in (("nominal", "resolved_nominal"),
                             ("calibrated", "resolved_calibrated")):
                m = sub[col].values
                n_res = int(m.sum())
                out["n_resolved_" + tag] = n_res
                #  the raw count, unweighted, so a pooled corpus rate can be
                #  formed as a ratio of counts rather than a mean of rates
                out["n_disagree_" + tag] = int((m & disagree).sum())
                ww = w * m
                out["misreport_resolved_" + tag] = (
                    float((ww * disagree).sum() / ww.sum())
                    if ww.sum() > 0 else np.nan)
                #  ROUND TWENTY-THREE.  A referee pointed out that this
                #  section names TWO defects in the all-cells rate -- that the
                #  axes are not all the same kind, and that most cells are
                #  unresolved -- corrects each of them separately, and never
                #  applies both at once, although the argument asks for it.
                #  The joint restriction is the analyst-latitude cells that
                #  the band also resolves, and it is a different number from
                #  either single correction.
                mj = m & lat
                out["n_resolved_latitude_" + tag] = int(mj.sum())
                out["n_disagree_latitude_" + tag] = int((mj & disagree).sum())
                wj = w * mj
                out["misreport_resolved_latitude_" + tag] = (
                    float((wj * disagree).sum() / wj.sum())
                    if wj.sum() > 0 else np.nan)
            rows.append(out)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def family_of(SC):
    return (SC[["log", "target", "domain"]].drop_duplicates()
            .assign(family=lambda d: np.where(d.domain == ITSM, "itsm",
                                              "other")))


#: the log--target pair is the resampling unit for every corpus-level median,
#: because two targets on the same log share a cohort and are not two
#: independent observations.  The bootstrap resamples LOGS and takes every
#: pair of a drawn log with it, which is the cluster the dependence lives in.
N_BOOT_CORPUS = 2000


def cluster_ci(d, value_col, seed=0, alpha=0.05):
    """A percentile interval for the median of `value_col` over pairs, with
    the LOG as the resampling unit.

    The manuscript's thesis is that a point estimate without its uncertainty
    misleads, and its own corpus-level medians were printed without one.  This
    is the cheapest honest repair.  It is a cluster bootstrap and not an
    independent one because two targets on the same log share a cohort; on
    this corpus that matters for the six logs that carry both.
    """
    s = d[["log", value_col]].dropna()
    if len(s) < 3:
        return (np.nan, np.nan)
    logs = s.log.unique()
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(N_BOOT_CORPUS):
        drawn = rng.choice(logs, size=len(logs), replace=True)
        vals = np.concatenate([s.loc[s.log == g, value_col].values
                               for g in drawn])
        if len(vals):
            out.append(float(np.median(vals)))
    if not out:
        return (np.nan, np.nan)
    return (float(np.quantile(out, alpha / 2)),
            float(np.quantile(out, 1 - alpha / 2)))


def summarise(per_pair, value_col, fam, statistic="median"):
    """One headline statistic on three populations, with a cluster-bootstrap
    interval on each."""
    d = per_pair.merge(fam[["log", "target", "family"]],
                       on=["log", "target"], how="left")
    out = {}
    for i, (pop, sel) in enumerate((("all 19", d),
                                    ("itsm 8", d[d.family == "itsm"]),
                                    ("other 11", d[d.family == "other"]))):
        s = sel[value_col].dropna()
        lo, hi = cluster_ci(sel, value_col, seed=17 + i)
        out[pop] = (float(getattr(s, statistic)()) if len(s) else np.nan,
                    len(s), lo, hi)
    return out


def main():
    t0 = time.time()
    print("=" * 92)
    print("s34  SIGN DISAGREEMENT, AND THE CORPUS IT IS COMPUTED ON")
    print("=" * 92)
    SC = S.read_results("s01_surface.csv")
    SC = SC[SC.metric.isin(S.SCALARS) & ~SC.rung.isin(S.IMPLAUSIBLE_RUNGS)]
    SC = SC.rename(columns={"level": "level"})
    SC["quality_level"] = (SC.quality.astype(str) + "/"
                           + SC.level.astype(str))
    fam = family_of(SC)
    print("  %d pairs, %d itsm" % (len(fam), int((fam.family == "itsm").sum())))

    RES = resolved_map()
    M = three_rates(SC, RES)
    M.to_csv(RESULTS / "s34_misreport.csv", index=False)
    eq = M[M.measure == "equal-level"]
    print("\n" + eq[["log", "target", "misreport_all",
                     "misreport_resolved_nominal", "n_resolved_nominal",
                     "misreport_resolved_calibrated",
                     "n_resolved_calibrated",
                     "misreport_magnitude"]].to_string(index=False))

    # ---- every headline statistic, three populations --------------------
    rows = []

    def add(name, per_pair, col, statistic="median", note=""):
        r = summarise(per_pair, col, fam, statistic)
        rows.append(dict(statistic=name, note=note,
                         **{k: r[k][0] for k in r},
                         **{k + " n": r[k][1] for k in r},
                         **{k + " lo": r[k][2] for k in r},
                         **{k + " hi": r[k][3] for k in r}))

    #  baseline spread: the range of V over the rung axis at the reference
    #  cell, per pair
    ref = SC[(SC.metric == "auc") & (SC.quality == "clean")
             & (SC.split == "holdout70") & (SC.learner == "logit")]
    sp = (ref.groupby(["log", "target"]).V.agg(lambda x: x.max() - x.min())
          .reset_index(name="spread"))
    add("baseline spread (AUC)", sp, "spread")

    #  the decomposition
    IDX = pd.read_csv(RESULTS / "s22_indices.csv")
    pr = IDX[(IDX.scale == "raw-within-metric") & (IDX.measure == "equal-level")]
    s1 = pr.groupby(["log", "target", "metric"]).S.sum()
    inter = (1.0 - s1).groupby(level=[0, 1]).median().reset_index(
        name="interaction_total")
    add("higher-order share", inter, "interaction_total")
    top = (pr.groupby(["log", "target", "metric"]).S.max()
           .groupby(level=[0, 1]).median().reset_index(name="largest_first"))
    add("largest first-order index", top, "largest_first")

    #  the sign-disagreement rates.  The resolved-cell row is a POOLED
    #  RATIO -- disagreeing cells over resolved cells, summed across the
    #  population -- and not a median of per-pair rates: a median of rates
    #  over a population where most pairs resolve nothing prints zero and
    #  says nothing, which is what this row used to do.
    add("misreport, all cells", eq, "misreport_all")
    add("misreport, analyst latitude only", eq, "misreport_latitude",
        note="clean register, single holdout; pipeline, rung and metric only")
    add("misreport, magnitude-weighted", eq, "misreport_magnitude")

    d = eq.merge(fam[["log", "target", "family"]], on=["log", "target"],
                 how="left")
    row = dict(statistic="misreport, resolved cells (pooled)",
               note="disagreeing cells / resolved cells, calibrated band")
    for pop, sel in (("all 19", d), ("itsm 8", d[d.family == "itsm"]),
                     ("other 11", d[d.family == "other"])):
        n_res = int(sel.n_resolved_calibrated.sum())
        row[pop] = (float(sel.n_disagree_calibrated.sum() / n_res)
                    if n_res else np.nan)
        row[pop + " n"] = n_res
    rows.append(row)

    #  regions and rho
    for path, tag in ((RESULTS / "s33_regions.csv", "calibrated"),
                      (RESULTS / "s21_regions.csv", "nominal")):
        if path.exists():
            G = pd.read_csv(path)
            col = "rho_calibrated" if ("rho_calibrated" in G.columns
                                       and tag == "calibrated") else "rho"
            add("robustness index rho (%s)" % tag, G, col)
            break

    #  regret
    A = pd.read_csv(RESULTS / "s23_metric_regret.csv")
    a = A[(A.metric == "auc") & (A.measure == "equal-level")
          & (A.rule == "one-number")]
    add("one-number excess regret (AUC)", a, "excess")

    F = pd.DataFrame(rows)
    F.to_csv(RESULTS / "s34_family.csv", index=False)
    print("\n" + F[["statistic", "all 19", "all 19 lo", "all 19 hi",
                    "itsm 8", "other 11"]].to_string(index=False))

    # ---- the decomposition, partitioned by what KIND of axis it is -------
    KIND = {"learner": "analyst latitude", "rung": "analyst latitude",
            "metric": "analyst latitude", "quality_level": "counterfactual",
            "split": "resampling"}
    prk = IDX[(IDX.scale == "raw-within-metric")
              & (IDX.measure == "equal-level")].copy()
    prk["kind"] = prk.axis.map(KIND).fillna("analyst latitude")
    per = (prk.groupby(["log", "target", "metric", "kind"]).S.sum()
           .groupby(level=[0, 1, 3]).median().reset_index())
    K = (per.pivot_table(index=["log", "target"], columns="kind", values="S")
         .reset_index())
    #  whatever is left belongs to no single axis
    K["higher-order"] = 1.0 - K[[c for c in K.columns
                                 if c not in ("log", "target")]].sum(axis=1)
    K.to_csv(RESULTS / "s34_axiskind.csv", index=False)
    print("\n  FIRST-ORDER VARIANCE BY KIND OF AXIS, median over pairs")
    print(K.drop(columns=["log", "target"]).median().to_string())

    med = eq.misreport_all.median()
    med_res = eq.misreport_resolved_nominal.dropna()
    med_cal = eq.misreport_resolved_calibrated.dropna()
    facts = dict(
        n_pairs=len(fam), n_itsm=int((fam.family == "itsm").sum()),
        misreport_all_median=float(med),
        misreport_resolved_median=float(med_res.median()) if len(med_res)
        else np.nan,
        misreport_resolved_n_pairs=int(len(med_res)),
        misreport_resolved_calibrated_median=float(med_cal.median())
        if len(med_cal) else np.nan,
        misreport_resolved_calibrated_n_pairs=int(len(med_cal)),
        misreport_magnitude_median=float(eq.misreport_magnitude.median()),
        #  the article quotes the CALIBRATED band's counts, because that is
        #  the band its region labels are computed under; the nominal ones are
        #  kept beside them so the size of the correction is visible
        n_resolved_median=float(eq.n_resolved_calibrated.median()),
        n_resolved_total=int(eq.n_resolved_calibrated.sum()),
        n_disagree_total=int(eq.n_disagree_calibrated.sum()),
        misreport_pooled_resolved=float(
            eq.n_disagree_calibrated.sum()
            / max(1, eq.n_resolved_calibrated.sum())),
        n_resolved_total_nominal=int(eq.n_resolved_nominal.sum()),
        n_disagree_total_nominal=int(eq.n_disagree_nominal.sum()),
        misreport_pooled_resolved_nominal=float(
            eq.n_disagree_nominal.sum()
            / max(1, eq.n_resolved_nominal.sum())),
        #  ROUND TWENTY-THREE: both corrections at once, and how concentrated
        #  the disagreements are.  A pooled ratio over pairs whose resolved
        #  denominators run from 0 to 269 is not a corpus average, and a
        #  referee was right that the text should say where it comes from.
        n_resolved_latitude_total=int(eq.n_resolved_latitude_calibrated.sum()),
        n_disagree_latitude_total=int(eq.n_disagree_latitude_calibrated.sum()),
        misreport_pooled_resolved_latitude=float(
            eq.n_disagree_latitude_calibrated.sum()
            / max(1, eq.n_resolved_latitude_calibrated.sum())),
        n_disagree_top_three=int(
            eq.groupby("log").n_disagree_calibrated.sum()
            .sort_values(ascending=False).head(3).sum()),
        n_logs_disagree=int(
            (eq.groupby("log").n_disagree_calibrated.sum() > 0).sum()),
        n_pairs_no_resolved_disagreement=int(
            ((eq.n_resolved_calibrated > 0)
             & (eq.n_disagree_calibrated == 0)).sum()),
        n_pairs_some_resolved_disagreement=int(
            (eq.n_disagree_calibrated > 0).sum()),
        n_pairs_no_resolved_cell=int((eq.n_resolved_calibrated == 0).sum()),
        n_cells_total=int(eq.n_cells.sum()),
        misreport_itsm_median=float(
            eq.merge(fam, on=["log", "target"])
            .query("family == 'itsm'").misreport_all.median()),
        misreport_magnitude_itsm_median=float(
            eq.merge(fam, on=["log", "target"])
            .query("family == 'itsm'").misreport_magnitude.median()),
        #  the analyst-latitude rate, which is the one a reader will take the
        #  headline to mean
        misreport_latitude_median=float(eq.misreport_latitude.median()),
        n_cells_latitude=int(eq.n_cells_latitude.median()),
        #  the pooled resolved rate by family: the headline is LOWER on the
        #  population the paper is about, and that is reported rather than
        #  left in the archive
        misreport_pooled_resolved_itsm=float(
            eq.merge(fam, on=["log", "target"]).query("family == 'itsm'")
            .pipe(lambda g: g.n_disagree_calibrated.sum()
                  / max(1, g.n_resolved_calibrated.sum()))),
        misreport_pooled_resolved_other=float(
            eq.merge(fam, on=["log", "target"]).query("family == 'other'")
            .pipe(lambda g: g.n_disagree_calibrated.sum()
                  / max(1, g.n_resolved_calibrated.sum()))),
        share_latitude=float(K["analyst latitude"].median())
        if "analyst latitude" in K.columns else np.nan,
        share_resampling=float(K["resampling"].median())
        if "resampling" in K.columns else np.nan,
        share_counterfactual=float(K["counterfactual"].median())
        if "counterfactual" in K.columns else np.nan,
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s34_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    print("\nwrote s34_*.csv in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

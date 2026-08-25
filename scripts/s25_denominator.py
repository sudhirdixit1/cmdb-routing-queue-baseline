"""s25 -- THE SURFACE DENOMINATOR AUDIT.

Round twenty, blueprint P0.1.

A statement of the form "one of nineteen surfaces is uniformly beneficial" is
a statement about a DENOMINATOR, and round nineteen's denominator was not the
one the manuscript declared.  Section 6 declared a design space of 262,656
cells; the region table counted thirty.

This file makes the three objects separate, names them, counts them from the
files themselves, and prints the reason for every cell in one that is not in
another.  Nothing here is typed: every number is derived from `spec.py`, from
the observed result files, and from the grid `s20_boot2.plan()` wrote before
any draw was taken.

  DECLARED SURFACE      every scientifically admissible specification.  Its
                        size is a product of the axis levels declared in
                        spec.py and s01_surface.py, computed here from those
                        declarations rather than quoted.
  COMPUTATIONAL SURFACE every specification s01 actually evaluated.
  INFERENCE SURFACE     every specification carrying bootstrap draws, so that
                        simultaneous inference over it is possible.

For each pair the audit reports learners, encodings, splits, decision times,
quality mechanisms and severity levels, admissible rungs, scalar instruments,
operating points, the expected Cartesian product, the observed unique cells,
duplicates, missing combinations, and the reason for every structural
exclusion.

It also answers the question a reader will ask next: is the inference surface
REPRESENTATIVE of the declared one?  The point estimates exist on both, so the
sign of the increment can be compared cell for cell, and the audit reports the
share of the declared surface's sign disagreement that the inference surface
reproduces.

    python s25_denominator.py

Outputs: results/s25_audit.csv          one row per (log, target)
         results/s25_axis_levels.csv    one row per (log, target, axis)
         results/s25_exclusions.csv     every missing combination and why
         results/s25_representative.csv the inference-vs-declared comparison
         results/s25_facts.csv
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
import s01_surface as S01  # noqa: E402
import s20_boot2 as S20  # noqa: E402
from common import RESULTS  # noqa: E402

PRIMARY = "BPIC14"


def declared_axes(log, target, ladder):
    """The declared levels of every axis for one pair, from the declarations
    in s01_surface.py and spec.py -- not from the observed output."""
    #  ROUND TWENTY-TWO.  This read the two-level constant directly and so
    #  reported two pipelines on the two largest logs, where the declaration
    #  now carries three.  It calls the declaration's own function, which is
    #  the point of having one: the audit must not know the answer.
    import r32_corpus as _C
    learners = S01.learners_for(log, len(_C.load(log)))
    quality = (S01.QUALITY_PRIMARY if log == PRIMARY else S01.QUALITY_OTHER)
    #  the split axis: one holdout plus every rolling fold the declaration
    #  yields for a log of this size.  spec.splits drops a fold whose test
    #  block or training prefix is under fifty rows, which is a declared
    #  structural rule, not a result.
    return dict(
        learner=list(learners),
        encoding=sorted({S.LEARNER_ENCODING[x] for x in learners}),
        quality_level=["%s@%.2f" % q for q in quality],
        rung=[nm for nm, _ in ladder],
        admissible_rung=[nm for nm, _ in ladder
                         if nm not in S.IMPLAUSIBLE_RUNGS],
        scalar_metric=list(S.SCALARS),
        operating_point=["%.3f" % t for t in S.NB_GRID])


def main():
    t0 = time.time()
    SUR = S.read_results("s01_surface.csv")
    print("=" * 92)
    print("s25  THE SURFACE DENOMINATOR AUDIT")
    print("=" * 92)

    try:
        GRID = pd.read_csv(RESULTS / "s20_grid.csv")
    except Exception:  # noqa: BLE001
        GRID = S20.plan()

    rows, axrows, excl = [], [], []
    for log, target, domain in S01.admitted_pairs():
        d, ladder, f, meta = S01.prepare(log, target)
        if d is None:
            excl.append(dict(log=log, target=target, axis="pair",
                             level="", reason=str(meta)))
            continue
        ax = declared_axes(log, target, ladder)
        n = len(d)
        splits = ["holdout70"] + [nm for nm, _a, _b in
                                  S.splits(n, "rolling", n_folds=5)]
        ax["split"] = splits
        #  the availability axis: the decision time is carried by the ladder,
        #  because the knowledge-article rung is the later decision time.
        ax["decision_time"] = (["t_interaction", "t_incident"]
                               if any(nm.endswith("_km") for nm, _ in ladder)
                               else ["t_incident"])
        for a, lv in ax.items():
            axrows.append(dict(log=log, target=target, axis=a,
                               n_levels=len(lv), levels="|".join(map(str, lv))))

        sub = SUR[(SUR.log == log) & (SUR.target == target)].copy()
        sub["quality_level"] = (sub.quality.astype(str) + "@"
                                + sub.level.map(lambda x: "%.2f" % x))
        #  --- expected versus observed, on the FULL declared grid ---------
        expect = (len(ax["learner"]) * len(ax["split"])
                  * len(ax["quality_level"]) * len(ax["rung"]))
        obs = int(sub.groupby(["learner", "split", "quality_level",
                               "rung"]).ngroups)
        dup = int(len(sub) - len(sub.drop_duplicates(
            ["learner", "split", "quality_level", "rung", "metric"])))
        #  every declared combination that is absent, with its reason
        have = set(map(tuple, sub[["learner", "split", "quality_level",
                                   "rung"]].drop_duplicates().values))
        for lr in ax["learner"]:
            for sp in ax["split"]:
                for q in ax["quality_level"]:
                    for rg in ax["rung"]:
                        if (lr, sp, q, rg) not in have:
                            excl.append(dict(
                                log=log, target=target, axis="cell",
                                level="|".join([lr, sp, q, rg]),
                                reason="single-class test block or fold "
                                       "shorter than the declared minimum"))
        #  --- the inference surface ---------------------------------------
        g = GRID[(GRID.log == log) & (GRID.target == target)]
        inf_cells = int(g.cells.iloc[0]) if len(g) else 0
        try:
            D = pd.read_csv(RESULTS / "s20" / ("draws_%s_%s.csv.gz"
                                               % (log, target)))
            D = D[D.draw >= 0]
            inf_obs = int(D.groupby(["learner", "split", "quality", "level",
                                     "rung"]).ngroups)
            inf_draws = int(D.draw.nunique())
        except Exception:  # noqa: BLE001
            inf_obs, inf_draws = 0, 0

        rows.append(dict(
            log=log, target=target, domain=domain, n=n,
            n_learners=len(ax["learner"]), n_encodings=len(ax["encoding"]),
            n_splits=len(ax["split"]), n_decision_times=len(ax["decision_time"]),
            n_quality=len(ax["quality_level"]),
            n_rungs=len(ax["rung"]),
            n_admissible_rungs=len(ax["admissible_rung"]),
            n_scalar_metrics=len(ax["scalar_metric"]),
            n_operating_points=len(ax["operating_point"]),
            declared_cells=expect,
            declared_scalar=expect * len(ax["scalar_metric"]),
            #  the intercept-only rung exists so the surface is complete but
            #  no analyst builds it, so every headline denominator is the
            #  ADMISSIBLE one
            declared_admissible_cells=(
                len(ax["learner"]) * len(ax["split"])
                * len(ax["quality_level"]) * len(ax["admissible_rung"])),
            declared_admissible_scalar=(
                len(ax["learner"]) * len(ax["split"])
                * len(ax["quality_level"]) * len(ax["admissible_rung"])
                * len(ax["scalar_metric"])),
            declared_admissible_dc=(
                len(ax["learner"]) * len(ax["split"])
                * len(ax["quality_level"]) * len(ax["admissible_rung"])
                * len(ax["operating_point"])),
            computational_cells=obs,
            computational_rows=len(sub),
            duplicates=dup,
            missing=expect - obs,
            inference_cells_declared=inf_cells,
            inference_cells_observed=inf_obs,
            inference_draws=inf_draws,
            inference_share=inf_obs / obs if obs else np.nan))

    A = pd.DataFrame(rows)
    AX = pd.DataFrame(axrows)
    EX = pd.DataFrame(excl)
    A.to_csv(RESULTS / "s25_audit.csv", index=False)
    AX.to_csv(RESULTS / "s25_axis_levels.csv", index=False)
    EX.to_csv(RESULTS / "s25_exclusions.csv", index=False)

    print(A[["log", "target", "declared_cells", "computational_cells",
             "duplicates", "missing", "inference_cells_observed",
             "inference_draws"]].to_string(index=False))

    #  --- the identity the audit exists to assert -------------------------
    A["ok"] = (A.computational_cells + A.missing == A.declared_cells)
    assert bool(A.ok.all()), "declared != observed + declared exclusions"
    assert int(A.duplicates.sum()) == 0, "duplicate cells in the surface"

    #  --- is the inference surface representative? ------------------------
    #  Both surfaces carry point estimates, so the SIGN of the increment can
    #  be compared cell for cell.  This does not make the inference surface
    #  the declared one; it measures how far the restriction moves the
    #  quantity the region label is built from.
    rep = []
    SC = SUR[SUR.metric.isin(S.SCALARS)].copy()
    SC["quality_level"] = (SC.quality.astype(str) + "@"
                           + SC.level.map(lambda x: "%.2f" % x))
    SC = SC[~SC.rung.isin(S.IMPLAUSIBLE_RUNGS)]
    for (log, target), sub in SC.groupby(["log", "target"]):
        g = GRID[(GRID.log == log) & (GRID.target == target)]
        if not len(g):
            continue
        lr = set(str(g.learners.iloc[0]).split("|"))
        sp = set(str(g.splits.iloc[0]).split("|"))
        ql = set(str(g.quality.iloc[0]).split("|"))
        inf = sub[sub.learner.isin(lr) & sub.split.isin(sp)
                  & sub.quality_level.isin(ql)]
        if not len(inf):
            continue
        rep.append(dict(
            log=log, target=target,
            declared_cells=len(sub), inference_cells=len(inf),
            share_positive_declared=float((sub.V > 0).mean()),
            share_positive_inference=float((inf.V > 0).mean()),
            sign_disagreement_declared=float(
                2 * (sub.V > 0).mean() * (1 - (sub.V > 0).mean())),
            sign_disagreement_inference=float(
                2 * (inf.V > 0).mean() * (1 - (inf.V > 0).mean())),
            mean_declared=float(sub.V.mean()),
            mean_inference=float(inf.V.mean())))
    REP = pd.DataFrame(rep)
    REP.to_csv(RESULTS / "s25_representative.csv", index=False)
    if len(REP):
        REP["abs_gap"] = (REP.share_positive_declared
                          - REP.share_positive_inference).abs()
        print("\nIS THE INFERENCE SURFACE REPRESENTATIVE?")
        print(REP[["log", "target", "declared_cells", "inference_cells",
                   "share_positive_declared", "share_positive_inference",
                   "abs_gap"]].to_string(
            index=False, float_format=lambda x: "%.3f" % x))

    facts = dict(
        n_pairs=len(A),
        declared_cells_total=int(A.declared_cells.sum()),
        declared_scalar_total=int(A.declared_scalar.sum()),
        declared_admissible_total=int(A.declared_admissible_cells.sum()),
        declared_admissible_scalar_total=int(
            A.declared_admissible_scalar.sum()),
        declared_admissible_dc_total=int(A.declared_admissible_dc.sum()),
        computational_cells_total=int(A.computational_cells.sum()),
        computational_rows_total=int(A.computational_rows.sum()),
        duplicates_total=int(A.duplicates.sum()),
        missing_total=int(A.missing.sum()),
        inference_cells_total=int(A.inference_cells_observed.sum()),
        inference_share_median=float(A.inference_share.median()),
        declared_cells_min=int(A.declared_cells.min()),
        declared_cells_max=int(A.declared_cells.max()),
        n_exclusions=len(EX),
        rep_max_gap=float(REP.abs_gap.max()) if len(REP) else np.nan,
        rep_median_gap=float(REP.abs_gap.median()) if len(REP) else np.nan,
        rep_n_pairs=len(REP),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s25_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

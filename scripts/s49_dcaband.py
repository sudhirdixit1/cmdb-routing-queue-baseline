"""s49 -- APPLY THE MEASURED WIDENING TO THE DECISION-CURVE BAND.

Round twenty-seven, Phase 2.  Arithmetic only: no refit, no draw is taken, and
nothing here is estimated that s26 and s41 did not already estimate.

THE DEFECT THIS CLOSES.  Section 8.3 printed counts from the decision-curve
family's simultaneous band -- how many operating points of the case study's
curve resolve as beneficial pointwise and how many under the band -- while
Section 10.4 MEASURED that same band as attaining well under its nominal
family-wise level, and named the multiplicative widening that would close the
gap.  The widening was never applied.  A paper that prints a count from an
uncorrected band and then tells the reader in Section 11 to distrust it has
reported the correction instead of making it.  A critical value is widened
multiplicatively, the draws are already on disk, and the factor is already
measured, so the correction costs one multiplication per cell.

WHAT IS WIDENED, AND WHAT IS NOT.  s26 builds the band as

    centre_c  +/-  q * se_c ,        centre_c = dnb_c - (median_b W_bc - dnb_c)

with one q for the whole family, from the Gaussian multiplier bootstrap of
s21.multiplier_quantile.  The correction replaces q by f*q and leaves centre
and se alone, which is exactly the object s41 measured: its `shortfall_factor`
is the (1-alpha) quantile, WITHIN a replicate, of t_max/q -- the factor by
which that replicate's critical value would have had to be multiplied to cover.
The POINTWISE interval is not widened here.  It does not rest on q, and its own
coverage is a separate measurement (s41's `coverage_percell_basic`); widening
it with a family-wise factor would price a pointwise statement at a
simultaneous rate, which is the mistake Section 8.3 exists to name.

WHICH FACTOR, AND WHY.  Two questions, taken apart because the file that first
conflated them got the answer wrong.

  1  A SHORTFALL IS NOT A RATIO.  s41 reports both `ratio_dca_all` (2.09) and
     `ratio_dca_adm` (1.80) -- the corpus's own median q_emp/q, over all cells
     and over the non-degenerate ones -- and separately reports
     `shortfall_factor` per matched family.  Only the second is a widening.
     s41's own comment records why: q and t_max are estimated from the same
     draws and move together, so the ratio of their marginal quantiles is not
     the factor that attains nominal coverage, and an earlier version of that
     line used the ratio and was wrong.  The corpus ratios are therefore
     carried here as diagnostics and are never the operative value.

  2  WITH OR WITHOUT THE DEGENERATE CELLS.  The two candidate shortfalls are
     s41's `heavy` regime, whose matched families carry this corpus's tails and
     no degenerate cells, and its `degenerate` regime, which adds cells on a
     coarse lattice so as to reproduce the 841 all-alike cells the corpus's
     curve families carry.  The heavy regime is the admissible-cells factor;
     the degenerate regime is the all-cells one.

     The family the correction is applied to decides between them, and it is
     measured here rather than assumed: of the 248 cells of s26's band, two are
     degenerate under s41's own rule (exactly zero in at least nine draws of
     ten), and one of the 31 operating points of the case study's curve.  That
     is under one per cent, against a corpus maximum of 14.3 per cent
     (results/s41_facts.csv, share_degenerate_dca_max).  s26's family is calibrated, is one pair's, and excludes the
     zero-variance cells at construction; the 841 are spread over the whole
     corpus's uncalibrated curve families.  So the matched regime for THIS
     family is `heavy`, and the admissible factor is the operative one.

     Within the heavy regime the file takes the MAXIMUM of the three matched
     family sizes, not the median or the minimum.  The three are 1.90, 1.92 and
     2.05 and the widening is conservative in the direction that costs the
     paper resolution, which is the direction this project's rule 2 says to
     err in.  The all-cells factor is reported beside it at every count, as
     Table S6 already prints nominal beside calibrated for the scalar family,
     and the counts are given across the whole candidate ladder so that a
     reader can see which conclusions the choice of factor is carrying.  On
     this curve it carries one point out of thirty-one.

WHAT THE CORRECTION COSTS.  It is written to s49_sensitivity.csv rather than
described: the count of operating points at which the increment is resolvably
positive falls from 18 under the uncorrected band to 8 under the corrected one,
and the harmful counts stay at nil pointwise and nil simultaneously -- so the
finding that survives is weaker and is still a finding.  Over the whole
248-cell family the one cell that resolved as harmful under the uncorrected
band no longer resolves, which removes a claim rather than adding one.

    python s49_dcaband.py

Outputs: results/s49_dcaband.csv      per-cell band, nominal and widened
         results/s49_sensitivity.csv  counts at every candidate factor
         results/s49_facts.csv
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

#: the cell Section 8 and Figure S4 read the curve at.  Named here so that the
#: 31 operating points this file counts are the same 31 the manuscript's other
#: generators count; round20_numbers.py selects the same pair.
REF_RUNG, REF_LEARNER = "B_intake_g", "logit"

#: s41's rule for a degenerate cell: exactly zero in at least this share of
#: draws.  Repeated rather than imported because s41 costs a simulation to
#: import cleanly, and a constant that drifts between the two files would make
#: the regime choice below unfalsifiable.
TAU_DEGENERATE = 0.90


# --------------------------------------------------------------------------
def _load(name, **kw):
    p = RESULTS / name
    if not p.exists():
        sys.exit("s49 needs results/%s, which %s writes"
                 % (name, "s26_calib_dca.py" if name.startswith("s26")
                    else "s41_bandcoverage.py"))
    return pd.read_csv(p, **kw)


def family_shape():
    """What s26's own band family looks like, in the two quantities s41 uses
    to choose a regime: the share of degenerate cells and the per-cell excess
    kurtosis of the standardised draws.  Measured, because the regime choice
    rests on it."""
    D = _load("s26_draws.csv.gz")
    W = (D[D.draw >= 0]
         .pivot_table(index="draw", columns=["rung", "learner", "threshold"],
                      values="dnb"))
    zero_share = (W == 0.0).sum(axis=0) / W.notna().sum(axis=0)
    se = W.std(axis=0, ddof=1)
    ok = se[se > 1e-15].index
    Z = (W[ok] - W[ok].mean(axis=0)) / se[ok]
    kurt = Z.kurtosis(axis=0)
    ref = [c for c in W.columns
           if c[0] == REF_RUNG and str(c[1]) == REF_LEARNER]
    return dict(
        n_cells=int(W.shape[1]),
        n_draws=int(W.shape[0]),
        n_degenerate_band=int((zero_share >= TAU_DEGENERATE).sum()),
        share_degenerate_band=float((zero_share >= TAU_DEGENERATE).mean()),
        n_degenerate_ref=int((zero_share[ref] >= TAU_DEGENERATE).sum()),
        n_lowdistinct_band=int((W.nunique() <= 20).sum()),
        kurt_med_band=float(kurt.median()),
        kurt_p90_band=float(kurt.quantile(0.90)))


def candidate_factors():
    """Every factor a reader might ask for, each labelled with what it is and
    whether this file will treat it as a widening.  The two corpus ratios are
    carried so that the reason they are NOT applied is visible in the output
    and not only in this file's docstring."""
    C = _load("s41_coverage.csv")
    F = _load("s41_facts.csv")
    dc = C[(C.family == "decision-curve") & (C.candidate == "q_mult")]

    def span(regime):
        s = dc[dc.regime == regime].shortfall_factor.astype(float)
        return float(s.min()), float(s.median()), float(s.max())

    heavy_lo, heavy_md, heavy_hi = span("heavy")
    degen_lo, degen_md, degen_hi = span("degenerate")
    rows = [
        dict(label="nominal", kind="none", regime="", factor=1.0,
             is_widening=False,
             what="the band as s26 built it, no correction applied"),
        dict(label="corpus ratio, admissible cells", kind="ratio",
             regime="", factor=float(F.ratio_dca_adm.iloc[0]),
             is_widening=False,
             what="median q_emp/q over the corpus's non-degenerate curve "
                  "cells; a diagnostic of draw shape, not a coverage repair"),
        dict(label="corpus ratio, all cells", kind="ratio", regime="",
             factor=float(F.ratio_dca_all.iloc[0]), is_widening=False,
             what="median q_emp/q over all the corpus's curve cells; same "
                  "objection"),
        dict(label="admissible, smallest shortfall", kind="shortfall",
             regime="heavy", factor=heavy_lo, is_widening=True,
             what="largest matched curve family, K=2966"),
        dict(label="admissible, median shortfall", kind="shortfall",
             regime="heavy", factor=heavy_md, is_widening=True,
             what="modal matched curve family, K=1100"),
        dict(label="admissible, largest shortfall", kind="shortfall",
             regime="heavy", factor=heavy_hi, is_widening=True,
             what="smallest matched curve family, K=534; APPLIED"),
        dict(label="all cells, smallest shortfall", kind="shortfall",
             regime="degenerate", factor=degen_lo, is_widening=True,
             what="degenerate regime, K=2966"),
        dict(label="all cells, median shortfall", kind="shortfall",
             regime="degenerate", factor=degen_md, is_widening=True,
             what="degenerate regime, K=1100"),
        dict(label="all cells, largest shortfall", kind="shortfall",
             regime="degenerate", factor=degen_hi, is_widening=True,
             what="degenerate regime, K=534; reported beside the applied "
                  "factor"),
    ]
    return pd.DataFrame(rows), dict(
        heavy_lo=heavy_lo, heavy_md=heavy_md, heavy_hi=heavy_hi,
        degen_lo=degen_lo, degen_md=degen_md, degen_hi=degen_hi,
        ratio_adm=float(F.ratio_dca_adm.iloc[0]),
        ratio_all=float(F.ratio_dca_all.iloc[0]),
        shortfall_whole_lo=float(F.shortfall_whole_min.iloc[0]),
        shortfall_whole_hi=float(F.shortfall_whole_max.iloc[0]))


def counts(B, f, q):
    """Resolved counts under a band widened by `f`.  `B` carries the centre and
    the standard error; nothing else about the band moves."""
    lo = B.centre - f * q * B.se
    hi = B.centre + f * q * B.se
    return dict(n_beneficial=int((lo > 0).sum()),
                n_harmful=int((hi < 0).sum()),
                n_unresolved=int(((lo <= 0) & (hi >= 0)).sum()),
                median_width=float((hi - lo).median()),
                min_lo=float(lo.min()))


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="print the tables without writing them")
    a = ap.parse_args(argv)
    t0 = time.time()
    print("=" * 92)
    print("s49  THE DECISION-CURVE BAND, WITH ITS MEASURED WIDENING APPLIED")
    print("=" * 92)

    B = _load("s26_bands.csv")
    q = float(B.q_maxt.iloc[0])
    #  s26 writes the two edges, not the centre; the centre is their midpoint
    #  and the half-width is q*se, which is checked rather than assumed --
    #  if s26's construction ever changes, this file must not silently apply
    #  a factor to a band it no longer describes.
    B["centre"] = (B.sim_lo + B.sim_hi) / 2.0
    resid = float(((B.sim_hi - B.sim_lo) / 2.0 - q * B.se).abs().max())
    if resid > 1e-9:
        sys.exit("s49: s26_bands.csv half-width is not q*se (max |resid| = "
                 "%.3g); the widening below would not be the correction it "
                 "claims to be" % resid)
    ref = B[(B.rung == REF_RUNG) & (B.learner == REF_LEARNER)].copy()
    if not len(ref):
        sys.exit("s49: no %s/%s rows in s26_bands.csv" % (REF_RUNG,
                                                          REF_LEARNER))

    shape = family_shape()
    CAND, fx = candidate_factors()
    print("\nTHE FAMILY THIS CORRECTION IS APPLIED TO")
    print("  %d cells, %d draws, critical value q = %.3f"
          % (shape["n_cells"], shape["n_draws"], q))
    print("  degenerate cells (zero in >= %.0f%% of draws): %d of %d "
          "(%.1f%%), %d of the %d reference operating points"
          % (100 * TAU_DEGENERATE, shape["n_degenerate_band"],
             shape["n_cells"], 100 * shape["share_degenerate_band"],
             shape["n_degenerate_ref"], len(ref)))
    print("  per-cell excess kurtosis: median %.2f, ninetieth %.2f"
          % (shape["kurt_med_band"], shape["kurt_p90_band"]))
    print("  -> the matched regime is `heavy`, so the ADMISSIBLE shortfall "
          "is the operative factor")

    #  THE OPERATIVE FACTOR.  Declared once, here, and used everywhere below.
    f_applied = fx["heavy_hi"]
    f_allcells = fx["degen_hi"]

    print("\nCANDIDATE FACTORS")
    print(CAND[["label", "kind", "regime", "factor", "is_widening"]]
          .to_string(index=False, float_format=lambda x: "%.4f" % x))

    rows = []
    for r in CAND.itertuples():
        for scope, sub in (("reference curve", ref), ("whole family", B)):
            rows.append(dict(scope=scope, label=r.label, kind=r.kind,
                             regime=r.regime, factor=float(r.factor),
                             is_widening=bool(r.is_widening),
                             applied=bool(abs(float(r.factor) - f_applied)
                                          < 1e-12),
                             n_cells=len(sub), q=q, q_effective=r.factor * q,
                             **counts(sub, float(r.factor), q)))
    SENS = pd.DataFrame(rows)
    print("\nWHAT EACH FACTOR COSTS")
    print(SENS[["scope", "label", "factor", "q_effective", "n_beneficial",
                "n_harmful", "n_unresolved"]]
          .to_string(index=False, float_format=lambda x: "%.3f" % x))

    #  the per-cell file: both bands side by side, so a table or a figure can
    #  draw either without recomputing the factor
    OUT = B[["rung", "learner", "threshold", "dnb", "se", "n_family",
             "n_draws", "pt_lo", "pt_hi", "sim_lo", "sim_hi"]].copy()
    OUT["centre"] = B.centre
    OUT["q_nominal"] = q
    OUT["factor"] = f_applied
    OUT["q_widened"] = f_applied * q
    OUT["wid_lo"] = B.centre - f_applied * q * B.se
    OUT["wid_hi"] = B.centre + f_applied * q * B.se
    OUT["factor_all_cells"] = f_allcells
    OUT["all_lo"] = B.centre - f_allcells * q * B.se
    OUT["all_hi"] = B.centre + f_allcells * q * B.se
    OUT["is_reference"] = (B.rung == REF_RUNG) & (B.learner == REF_LEARNER)
    OUT["wid_beneficial"] = OUT.wid_lo > 0
    OUT["wid_harmful"] = OUT.wid_hi < 0
    OUT["construction"] = "basic, max-t, widened by the measured shortfall"

    rw = OUT[OUT.is_reference]
    nom = counts(ref, 1.0, q)
    wid = counts(ref, f_applied, q)
    alc = counts(ref, f_allcells, q)
    fam_nom = counts(B, 1.0, q)
    fam_wid = counts(B, f_applied, q)
    fam_alc = counts(B, f_allcells, q)
    dip_nom = ref.loc[(ref.centre - q * ref.se).idxmin()]
    dip_wid = ref.loc[(ref.centre - f_applied * q * ref.se).idxmin()]
    ben = sorted(float(t) for t in rw[rw.wid_beneficial].threshold)

    print("\nTHE REFERENCE CURVE, POINT BY POINT")
    print(rw[["threshold", "dnb", "se", "pt_lo", "sim_lo", "wid_lo",
              "wid_hi"]].to_string(index=False,
                                   float_format=lambda x: "%.5f" % x))
    print("\n  resolvably positive under the widened band at %d of %d points, "
          "all at or above theta = %.3f%s"
          % (len(ben), len(ref), ben[0] if ben else float("nan"),
             "" if not ben or len(ben) == int((ref.threshold >= ben[0]).sum())
             else " -- and NOT every point above it"))

    facts = dict(
        n_cells=shape["n_cells"], n_draws=shape["n_draws"],
        n_ref_points=len(ref),
        n_degenerate_band=shape["n_degenerate_band"],
        share_degenerate_band=shape["share_degenerate_band"],
        n_degenerate_ref=shape["n_degenerate_ref"],
        n_lowdistinct_band=shape["n_lowdistinct_band"],
        kurt_med_band=shape["kurt_med_band"],
        kurt_p90_band=shape["kurt_p90_band"],
        q_nominal=q,
        factor_applied=f_applied, factor_all_cells=f_allcells,
        factor_admissible_min=fx["heavy_lo"],
        factor_admissible_median=fx["heavy_md"],
        factor_all_cells_min=fx["degen_lo"],
        ratio_dca_adm=fx["ratio_adm"], ratio_dca_all=fx["ratio_all"],
        q_widened=f_applied * q, q_all_cells=f_allcells * q,
        #  the reference curve: the counts Section 8.3 prints
        n_beneficial_pointwise=int((ref.pt_lo > 0).sum()),
        n_harmful_pointwise=int((ref.pt_hi < 0).sum()),
        n_beneficial_sim_nominal=nom["n_beneficial"],
        n_harmful_sim_nominal=nom["n_harmful"],
        n_beneficial_sim_widened=wid["n_beneficial"],
        n_harmful_sim_widened=wid["n_harmful"],
        n_unresolved_sim_widened=wid["n_unresolved"],
        n_beneficial_sim_all_cells=alc["n_beneficial"],
        n_harmful_sim_all_cells=alc["n_harmful"],
        n_beneficial_lost_to_widening=(nom["n_beneficial"]
                                       - wid["n_beneficial"]),
        #  the LOWEST threshold that still resolves under the widened band.
        #  Not "from here upward": the run is not contiguous -- one interior
        #  point above it does not resolve -- and a macro named `first` was
        #  read as contiguity by the first draft of Section 8.3.
        theta_min_beneficial_widened=ben[0] if ben else np.nan,
        n_beneficial_widened_above_min=int(sum(t >= ben[0] for t in ben))
        if ben else 0,
        beneficial_widened_contiguous=bool(
            ben and len(ben) == int((ref.threshold >= ben[0]).sum())),
        width_sim_nominal=nom["median_width"],
        width_sim_widened=wid["median_width"],
        width_pointwise=float((ref.pt_hi - ref.pt_lo).median()),
        dip_theta_nominal=float(dip_nom.threshold),
        dip_value_nominal=float(dip_nom.centre - q * dip_nom.se),
        dip_theta_widened=float(dip_wid.threshold),
        dip_value_widened=float(dip_wid.centre
                                - f_applied * q * dip_wid.se),
        #  the whole declared family, which is what the supplement's
        #  corpus-wide harmful counts are taken over
        n_family_beneficial_nominal=fam_nom["n_beneficial"],
        n_family_harmful_nominal=fam_nom["n_harmful"],
        n_family_beneficial_widened=fam_wid["n_beneficial"],
        n_family_harmful_widened=fam_wid["n_harmful"],
        n_family_beneficial_all_cells=fam_alc["n_beneficial"],
        n_family_harmful_all_cells=fam_alc["n_harmful"],
        #  what the scalar families' widening is, for the comparison Section
        #  10.4 draws
        shortfall_whole_min=fx["shortfall_whole_lo"],
        shortfall_whole_max=fx["shortfall_whole_hi"],
        runtime_s=round(time.time() - t0, 3))

    if a.report:
        print("\n(--report: nothing written)")
    else:
        OUT.to_csv(RESULTS / "s49_dcaband.csv", index=False)
        SENS.to_csv(RESULTS / "s49_sensitivity.csv", index=False)
        pd.DataFrame([facts]).to_csv(RESULTS / "s49_facts.csv", index=False)
    print("\n" + pd.Series(facts).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())

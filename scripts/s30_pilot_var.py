"""s30 -- A DESIGN-BASED VARIANCE FOR THE PILOT'S PROPORTIONS.

Round twenty, blueprint P1.6.

The pilot estimates each proportion over an ELIGIBLE population that is itself
estimated, from two strata: the papers a mechanical screen accepted, all of
which were adjudicated, and a subsample of the papers it rejected, adjudicated
at a known sampling fraction so the screen's misses are counted rather than
assumed away.  That makes every proportion a RATIO of two weighted totals

    p_hat = sum_i w_i y_i / sum_i w_i e_i ,

where e_i is eligibility and y_i the code among the eligible.  Round nineteen
put a Wilson interval around it, computed from a fractional "effective sample
size".  A Wilson interval is a binomial interval for a binomial count, and
neither the numerator nor the denominator here is one: the denominator is a
random weighted total, and the weights differ between strata by a factor of
about two and a half.

This file replaces that interval with two that respect the design:

  DESIGN-BASED.  The standard linearisation for a stratified ratio estimator,
      Var(p) ~ sum_h (1 - f_h) n_h / (n_h - 1) * sum_i (w_i u_i - mean)^2
                / (sum_i w_i e_i)^2 ,      u_i = y_i - p * e_i,
      with the finite-population correction f_h = n_h / N_h, which is one in
      the screened-in stratum -- every accepted paper was adjudicated -- so
      that stratum contributes no sampling variance at all.

  BOOTSTRAP.  Resampling adjudicated papers WITHIN STRATUM with replacement
      and recomputing the ratio, which needs no linearisation and handles the
      small counts the screened-out stratum has.

    python s30_pilot_var.py

Outputs: results/s30_proportions.csv  each code, three intervals side by side
         results/s30_facts.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

CODES = ("B_stated", "B_justified", "M_justified", "Theta_stated",
         "Range_reported")
N_BOOT = 20000
ALPHA = 0.05


def wilson(k, n, alpha=ALPHA):
    from scipy.stats import norm
    if n <= 0:
        return np.nan, np.nan
    z = float(norm.ppf(1 - alpha / 2))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main():
    t0 = time.time()
    AUDIT = Path(RESULTS).parent / "data" / "audit2"
    A_in = pd.read_csv(AUDIT / "adjudication_in.csv")
    A_out = pd.read_csv(AUDIT / "adjudication_out.csv")
    C = pd.read_csv(RESULTS / "s06_coding.csv")
    F = pd.read_csv(RESULTS / "s06_facts.csv").iloc[0]
    print("=" * 92)
    print("s30  A DESIGN-BASED VARIANCE FOR THE PILOT")
    print("=" * 92)

    #  the two strata, exactly as s06 defines them
    n_in_total = int((C.status == "INCLUDED").sum())
    n_out_total = int(C.status.isin(["NO_METRIC", "NO_ABLATION"]).sum())
    n_in_adj, n_out_adj = len(A_in), len(A_out)
    w_in = n_in_total / float(n_in_adj)          # a census: 1.0
    w_out = n_out_total / float(n_out_adj)
    print("  screened-in  %d of %d adjudicated, weight %.3f"
          % (n_in_adj, n_in_total, w_in))
    print("  screened-out %d of %d adjudicated, weight %.3f"
          % (n_out_adj, n_out_total, w_out))

    A_in = A_in.assign(_stratum="screened-in", _w=w_in, _N=n_in_total)
    A_out = A_out.assign(_stratum="screened-out", _w=w_out, _N=n_out_total)
    A = pd.concat([A_in, A_out], ignore_index=True)
    A["_e"] = (A.eligible.astype(str).str.strip().str.lower() == "yes").astype(float)

    rows = []
    rng = np.random.default_rng(20260823)
    for code in CODES:
        v = A[code].astype(str).str.strip().str.lower()
        #  `unclear` counts as NOT demonstrated.  That is the conservative
        #  direction for a paper arguing practice is thin: it lowers every
        #  reported rate that the paper would prefer to be high, and raises
        #  none.
        A["_y"] = np.where(v.eq("yes"), 1.0, 0.0) * A._e
        num = float((A._w * A._y).sum())
        den = float((A._w * A._e).sum())
        p = num / den if den > 0 else np.nan

        #  design-based linearised variance for a stratified ratio estimator
        var = 0.0
        for st, g in A.groupby("_stratum"):
            n_h, N_h = len(g), float(g._N.iloc[0])
            if n_h < 2:
                continue
            fpc = max(0.0, 1.0 - n_h / N_h)
            u = (g._y.values - p * g._e.values) * g._w.values
            var += fpc * n_h / (n_h - 1.0) * float(np.sum((u - u.mean()) ** 2))
        var = var / (den * den) if den > 0 else np.nan
        se = float(np.sqrt(max(0.0, var)))
        lo_d, hi_d = max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se)

        #  stratified bootstrap, which needs no linearisation
        groups = [(g._w.values, g._y.values, g._e.values)
                  for _st, g in A.groupby("_stratum")]
        bs = np.empty(N_BOOT)
        for b in range(N_BOOT):
            nu = de = 0.0
            for wv, yv, ev in groups:
                idx = rng.integers(0, len(wv), len(wv))
                nu += float((wv[idx] * yv[idx]).sum())
                de += float((wv[idx] * ev[idx]).sum())
            bs[b] = nu / de if de > 0 else np.nan
        lo_b = float(np.nanpercentile(bs, 100 * ALPHA / 2))
        hi_b = float(np.nanpercentile(bs, 100 * (1 - ALPHA / 2)))

        #  the interval an earlier version printed, for comparison
        n_eff = float(F.get("n_effective", np.nan))
        lo_w, hi_w = wilson(p * n_eff, n_eff)

        rows.append(dict(code=code, n_eligible_adjudicated=int(A._e.sum()),
                         n_in=int(A_in._e.sum()) if "_e" in A_in else 0,
                         weighted_eligible=den, p=p, se_design=se,
                         design_lo=lo_d, design_hi=hi_d,
                         boot_lo=lo_b, boot_hi=hi_b,
                         wilson_lo=lo_w, wilson_hi=hi_w,
                         design_width=hi_d - lo_d, boot_width=hi_b - lo_b,
                         wilson_width=hi_w - lo_w))
    P = pd.DataFrame(rows)
    P.to_csv(RESULTS / "s30_proportions.csv", index=False)
    print()
    print(P[["code", "p", "se_design", "design_lo", "design_hi",
             "boot_lo", "boot_hi", "wilson_lo", "wilson_hi"]].to_string(
        index=False, float_format=lambda x: "%.3f" % x))

    contained = int(((P.design_lo <= P.wilson_lo)
                     & (P.wilson_hi <= P.design_hi)).sum())
    facts = dict(
        n_codes=len(P), n_boot=N_BOOT,
        n_in_total=n_in_total, n_out_total=n_out_total,
        n_in_adjudicated=n_in_adj, n_out_adjudicated=n_out_adj,
        weight_in=w_in, weight_out=w_out,
        weighted_eligible=float(P.weighted_eligible.iloc[0]) if len(P) else np.nan,
        design_width_median=float(P.design_width.median()),
        boot_width_median=float(P.boot_width.median()),
        wilson_width_median=float(P.wilson_width.median()),
        n_wilson_inside_design=contained,
        max_lo_gap=float((P.design_lo - P.wilson_lo).abs().max()),
        max_hi_gap=float((P.design_hi - P.wilson_hi).abs().max()),
        runtime_s=round(time.time() - t0, 1))
    pd.DataFrame([facts]).to_csv(RESULTS / "s30_facts.csv", index=False)
    print()
    print(pd.Series(facts).to_string())


if __name__ == "__main__":
    main()

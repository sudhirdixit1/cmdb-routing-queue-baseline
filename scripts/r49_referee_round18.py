"""r49 -- THE MEASUREMENTS SIX ADVERSARIAL PASSES DEMANDED.

Every objection in `REFEREE-LOG.md` for round eighteen that could be answered
with a number rather than a concession is answered here.  Each section names
the objection it answers, and each prints its result whatever the result is.

    python r49_referee_round18.py

Outputs: results/r49_facts.csv, r49_baseline_spread.csv, r49_prop3_tol.csv,
         r49_holdout_roles.csv, r49_audit_spotcheck.csv
"""
import gzip
import itertools
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-12
NEST = ["empty", "B0_half", "B0", "B0+g"]


# =====================================================================
# M2.  "The baseline spread is inflated by a rung no analyst would use."
# =====================================================================
def m2_baseline_spread():
    print("=" * 92)
    print("M2  the baseline axis, with and without the intercept-only rung")
    print("=" * 92)
    SUR = pd.read_csv(RESULTS / "r44_surface.csv")
    rows = []
    for log, sub_log in SUR.groupby("log"):
        for (inst, pop, reg), sub in sub_log.groupby(
                ["instrument", "population", "regime"]):
            v = sub.set_index("baseline").V.to_dict()
            for i, j in itertools.combinations(range(len(NEST)), 2):
                lo_, hi_ = NEST[i], NEST[j]
                if lo_ not in v or hi_ not in v or v[lo_] <= EPS:
                    continue
                rows.append(dict(log=log, instrument=inst, population=pop,
                                 regime=reg, b_lo=lo_, b_hi=hi_,
                                 R=1.0 - v[hi_] / v[lo_]))
    RED = pd.DataFrame(rows)
    out = []
    for log, sub in RED.groupby("log"):
        s = sub[(sub.instrument == "auc") & (sub.population == 1.00)]
        real = s[s.b_lo != "empty"]
        out.append(dict(
            log=log,
            all_lo=float(s.R.min()), all_hi=float(s.R.max()),
            all_spread=float(s.R.max() - s.R.min()), all_pairs=len(s),
            real_lo=float(real.R.min()), real_hi=float(real.R.max()),
            real_spread=float(real.R.max() - real.R.min()),
            real_pairs=len(real)))
    D = pd.DataFrame(out)
    D.to_csv(RESULTS / "r49_baseline_spread.csv", index=False)
    print(D.to_string(index=False))
    print("\n  The referee is right that the intercept-only rung is not a "
          "baseline anyone\n  would build.  Dropping every pair that uses it "
          "leaves the spread at")
    for _, r in D.iterrows():
        print(f"    {r.log:20s} {r.all_spread:.3f} -> {r.real_spread:.3f}")
    return D


# =====================================================================
# M4.  "Proposition 3's constructibility thresholds are arbitrary."
# =====================================================================
def m4_prop3_tolerance():
    print("=" * 92)
    print("M4  proposition 3's twelve pairs, across a grid of tolerances")
    print("=" * 92)
    S = pd.read_csv(RESULTS / "r41_prop3_spreads.csv")
    AXES = ["baseline", "metric", "threshold", "population"]
    rng_ = {a: (float(np.nanmax(S[f"spread_{a}"]))
                - float(np.nanmin(S[f"spread_{a}"]))) for a in AXES}
    rows = []
    for tol in (0.02, 0.05, 0.10, 0.20):
        for diff in (0.10, 0.25, 0.40, 0.50):
            ok = 0
            for X, Y in itertools.permutations(AXES, 2):
                t_, need = tol * rng_[X], diff * rng_[Y]
                best = 0.0
                for i, j in itertools.combinations(range(len(S)), 2):
                    dx = abs(S.iloc[i][f"spread_{X}"] - S.iloc[j][f"spread_{X}"])
                    dy = abs(S.iloc[i][f"spread_{Y}"] - S.iloc[j][f"spread_{Y}"])
                    if np.isfinite(dx) and np.isfinite(dy) and dx <= t_:
                        best = max(best, dy)
                ok += int(best >= need)
            rows.append(dict(agree_tol=tol, differ_tol=diff, constructible=ok))
            print(f"  agree within {tol:.0%} of the axis range, differ by "
                  f"{diff:.0%}:  {ok} of 12")
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r49_prop3_tol.csv", index=False)
    print(f"\n  across all {len(D)} tolerance pairs the count runs "
          f"{int(D.constructible.min())} to {int(D.constructible.max())}; "
          f"the paper reports the cell at (0.05, 0.25).")
    return D


# =====================================================================
# P1/P2.  "What actually are the roles the rules assigned on the held-out
#          logs?  BPIC 2018's exclusion needs a reason a reader can see."
# =====================================================================
def p1_holdout_roles():
    print("=" * 92)
    print("P1  the held-out logs' assigned roles, and why BPIC 2018 excludes")
    print("=" * 92)
    rows = []
    for key in ("BPIC11", "BPIC18"):
        p = ROOT / "data" / "normalized" / f"{key}.parquet"
        if not p.exists():
            print(f"  {key}: not parsed")
            continue
        d = pd.read_parquet(p)
        H = (pd.read_csv(RESULTS / "r43_holdout.csv")
             if (RESULTS / "r43_holdout.csv").exists() else pd.DataFrame())
        g = "org:group" if key == "BPIC11" else "org:resource"
        f = "case:Diagnosis" if key == "BPIC11" else "case:applicant"
        seq = next((c for c in d.columns if c.startswith("_seq_")
                    and c.endswith(g.split(":")[-1])), None)
        n_g = int(d[g].astype(str).nunique()) if g in d.columns else -1
        n_f = int(d[f].astype(str).nunique()) if f in d.columns else -1
        reuse = (len(d) / n_f) if n_f > 0 else np.nan
        #  the handover target's prevalence, and WHY it is what it is
        prev = np.nan
        if seq:
            h = d[seq].astype(str).map(
                lambda s: len({x for x in s.split("|") if x and x != "nan"}))
            prev = float((h >= 2).mean())
            mean_distinct = float(h.mean())
        else:
            mean_distinct = np.nan
        top = (d[g].astype(str).value_counts(normalize=True).head(3).to_dict()
               if g in d.columns else {})
        rows.append(dict(log=key, n=len(d), g=g, card_g=n_g, f=f, card_f=n_f,
                         reuse_f=reuse, handover_prevalence=prev,
                         mean_distinct_g_per_case=mean_distinct,
                         top_g_shares="; ".join(f"{k}={v:.3f}"
                                                for k, v in top.items())))
        print(f"  {key}: n={len(d):,}  g={g!r} card {n_g}  f={f!r} card {n_f} "
              f"reuse {reuse:.1f}")
        print(f"        distinct {g} per case: mean {mean_distinct:.2f}; "
              f"handover prevalence {prev:.4f}")
        print(f"        the three commonest opening values: "
              f"{rows[-1]['top_g_shares']}")
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r49_holdout_roles.csv", index=False)
    return D


# =====================================================================
# A1.  "Check three coded rows against the actual papers."
# =====================================================================
def a1_audit_spotcheck(n_rows=6, seed=20260819):
    print("=" * 92)
    print("A1  the coding sheet's quotes, checked back against the full text")
    print("=" * 92)
    C = pd.read_csv(RESULTS / "r40_coding.csv")
    TEXTS = ROOT / "data" / "audit" / "fulltext"
    rng = np.random.default_rng(seed)
    have = C[C.oa_id.apply(lambda i: (TEXTS / f"{i}.txt.gz").exists())]
    if have.empty:
        print("  no cached full texts; run r40_audit.py --fetch first")
        return pd.DataFrame()
    pick = have.iloc[np.sort(rng.choice(len(have),
                                        size=min(n_rows, len(have)),
                                        replace=False))]
    rows = []
    for _, r in pick.iterrows():
        with gzip.open(TEXTS / f"{r.oa_id}.txt.gz", "rt",
                       encoding="utf-8") as fh:
            pages = fh.read().split("\f")
        for code in ("B_stated", "B_justified", "M_justified",
                     "Theta_stated", "Range_reported"):
            q = str(r.get(f"{code}_quote", "") or "")
            pg = r.get(f"{code}_pdf_page", 0)
            if not q or q == "nan" or not pg or pd.isna(pg):
                continue
            pg = int(pg)
            flat = re.sub(r"\s+", " ", pages[pg - 1]) if pg <= len(pages) else ""
            flat = re.sub(r"-\s", "", flat)
            probe = re.sub(r"\s+", " ", q)[:60]
            rows.append(dict(oa_id=r.oa_id, code=code, pdf_page=pg,
                             page_exists=pg <= len(pages),
                             quote_on_that_page=probe in flat,
                             quote=probe))
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r49_audit_spotcheck.csv", index=False)
    if len(D):
        print(f"  {len(D)} quoted codes across {D.oa_id.nunique()} papers")
        print(f"  the page exists in {int(D.page_exists.sum())} of {len(D)}")
        print(f"  the quote is ON that page in "
              f"{int(D.quote_on_that_page.sum())} of {len(D)}")
        bad = D[~D.quote_on_that_page]
        for _, b in bad.iterrows():
            print(f"    MISMATCH {b.oa_id} {b.code} p{b.pdf_page}: "
                  f"{b.quote[:60]}")
    return D


# =====================================================================
# A5.  "Your topical pre-filter is a constructed control.  Null it."
#      Frame A applies a keyword filter to titles and abstracts; frame B
#      applies none.  If the filter selects papers that are unusually
#      careful about metrics, the audit understates the practice failure.
#      Comparing the two frames' codes is the null, and it costs nothing.
# =====================================================================
def a5_frame_null():
    print("=" * 92)
    print("A5  the topical pre-filter, nulled: frame A against frame B")
    print("=" * 92)
    S = pd.read_csv(RESULTS / "r40_screening.csv")
    INC = S[S.screen_amd == "INCLUDED"]
    CODES = ["B_stated", "B_justified", "M_justified", "Theta_stated",
             "Range_reported"]
    rows = []
    for code in CODES:
        a = INC[INC.frame == "A"][code]
        b = INC[INC.frame == "B"][code]
        rows.append(dict(code=code, n_A=len(a), n_B=len(b),
                         yes_A=int((a == "yes").sum()),
                         yes_B=int((b == "yes").sum()),
                         p_A=float((a == "yes").mean()) if len(a) else np.nan,
                         p_B=float((b == "yes").mean()) if len(b) else np.nan))
        rows[-1]["gap"] = rows[-1]["p_A"] - rows[-1]["p_B"]
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "r49_frame_null.csv", index=False)
    print(D.to_string(index=False))
    print(f"\n  the filtered frame ({int(D.n_A.iloc[0])} papers) against the "
          f"unfiltered one ({int(D.n_B.iloc[0])})")
    print(f"  largest gap in any code: {D.gap.abs().max():.3f}")
    print("  A gap that is POSITIVE means the pre-filter selected papers that "
          "are MORE\n  careful, which would make the audit understate the "
          "practice failure.")
    return D


def main():
    t0 = time.time()
    D2 = m2_baseline_spread()
    D4 = m4_prop3_tolerance()
    D1 = p1_holdout_roles()
    DA = a1_audit_spotcheck()
    D5 = a5_frame_null()
    F = pd.DataFrame([dict(
        m2_min_real_spread=float(D2.real_spread.min()),
        m2_max_real_spread=float(D2.real_spread.max()),
        m2_min_all_spread=float(D2.all_spread.min()),
        m2_max_all_spread=float(D2.all_spread.max()),
        m2_min_real_lo=float(D2.real_lo.min()),
        m2_max_real_hi=float(D2.real_hi.max()),
        m4_min_constructible=int(D4.constructible.min()),
        m4_max_constructible=int(D4.constructible.max()),
        m4_cells=len(D4),
        p1_bpic18_card_g=int(D1[D1.log == "BPIC18"].card_g.iloc[0])
        if "BPIC18" in set(D1.log) else -1,
        p1_bpic18_mean_distinct=float(
            D1[D1.log == "BPIC18"].mean_distinct_g_per_case.iloc[0])
        if "BPIC18" in set(D1.log) else np.nan,
        p1_bpic11_card_f=int(D1[D1.log == "BPIC11"].card_f.iloc[0])
        if "BPIC11" in set(D1.log) else -1,
        a1_codes_checked=len(DA),
        a1_quotes_on_page=int(DA.quote_on_that_page.sum()) if len(DA) else 0,
        a1_papers=int(DA.oa_id.nunique()) if len(DA) else 0,
        a5_n_frame_a=int(D5.n_A.iloc[0]), a5_n_frame_b=int(D5.n_B.iloc[0]),
        a5_max_abs_gap=float(D5.gap.abs().max()),
        a5_max_gap_code=str(D5.loc[D5.gap.abs().idxmax()].code),
        a5_gap_direction=("filtered frame more careful"
                          if D5.loc[D5.gap.abs().idxmax()].gap > 0
                          else "unfiltered frame more careful"),
        runtime_s=round(time.time() - t0, 1))])
    F.to_csv(RESULTS / "r49_facts.csv", index=False)
    print("\n" + "=" * 92)
    print(F.T.to_string())


if __name__ == "__main__":
    main()

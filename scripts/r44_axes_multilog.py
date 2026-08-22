"""r44 -- THE FOUR AXES, ON EVERY LOG THAT CAN CARRY THEM.

PLAN-REVIEWER-PROOF.md section 5.1.  Round seventeen varied all four choices
on BPI Challenge 2014 alone, so the claim that each choice moves the answer by
more than the effect is an n = 1 claim.  Three logs have a resolvable
reduction -- BPIC14, BPIC13 incidents and BPIC19 -- and this file runs the
whole surface on all three through one code path.

    python r44_axes_multilog.py                 # all three
    python r44_axes_multilog.py BPIC14          # one

THE FOUR AXES, and what each one's levels are:

  baseline     a nested ladder: {} subset B0_half subset B0 subset B0 + g.
               Every ordered nested pair gives a reduction, so the axis has
               six levels rather than the two the corpus reports.
  metric       auc, average precision, Brier skill, Nagelkerke R^2, and net
               benefit, which carries the third axis inside it.
  threshold    the r23/r30 grid, 0.05 to 0.80 in steps of 0.025.
  population   the register is masked to a declared level, rare-first (how an
               estate actually empties) and at random (the convenient and
               wrong assumption), exactly as r36 does on the primary log.

WHAT WOULD SINK THIS.  The choices mattering on BPIC14 and not elsewhere.
Then the paper's central claim is about one estate and must say so.  The
`range of the range` table is where that is read off, and it is printed
whatever it says.

Outputs: results/r44_surface.csv, r44_spread.csv, r44_facts.csv
"""
import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
import r33_generic_ladder as L
from common import RESULTS

SEED = 20260819
GRID = np.round(np.arange(0.05, 0.8001, 0.025), 4)
POPULATIONS = ((1.00, "full"), (0.75, "rare-first"), (0.50, "rare-first"),
               (0.25, "rare-first"), (0.50, "random"))
EMPTY = "__EMPTY__"
EPS = 1e-12
LOGS = ("BPIC14", "BPIC13_incidents", "BPIC19")
#  The target on which each log's reduction is resolvable in r33; the surface
#  is run on THAT target so the three logs are comparable.  BPIC14 is
#  resolvable on both and the registered primary is used.
TARGET = {"BPIC14": "handover", "BPIC13_incidents": "duration",
          "BPIC19": "duration"}


def mask_population(col, level, regime, rng):
    """r36's construction, generalised.  A masked value becomes an explicit
    EMPTY level rather than a dropped row: a desk with a half-empty register
    still has the incidents."""
    s = col.astype(str).copy()
    if level >= 1.0:
        return s
    if regime == "random":
        keep = rng.random(len(s)) < level
        return s.where(keep, EMPTY)
    #  rare-first: the least frequent values go whole, which is how discovery
    #  and manual curation actually leave an estate.
    vc = s.value_counts()
    order = vc.index[::-1]                       # rarest first
    cum = vc.loc[order].cumsum() / len(s)
    drop = set(order[cum <= (1.0 - level)])
    return s.where(~s.isin(drop), EMPTY)


def instruments(p, y, prev_tr):
    out = dict(auc=L.roc_auc_score(y, p),
               ap=L.average_precision_score(y, p),
               brier_skill=L.brier_skill(p, y, float(prev_tr)),
               nagelkerke=L.nagelkerke(p, y, float(prev_tr)))
    for t in GRID:
        out[f"nb_{t:.3f}"] = L.net_benefit(p, y, float(t))
    return out


def run_log(key):
    domain = C.LOGS[key][0]
    print("=" * 96)
    print(f"{key}  ({domain})")
    d = C.load(key)
    d, CAND, gsel, fsel, b0sel, code, has_time = L.assign_roles(key, d)
    if code:
        print(f"  EXCLUDED {code}")
        return []
    g, g_seq, g_alt, g_alt_seq = gsel
    f_reg, f_amd = fsel
    b0, layers = b0sel
    f = f_amd or f_reg
    n = len(d)
    cut = int(n * L.TRAIN_FRAC)
    y_h, y_d, _ = L.targets(d, g_seq, cut)
    yv = y_h if TARGET[key] == "handover" else y_d
    print(f"  n={n:,}  target={TARGET[key]}  f={f!r} (card {L.card(d[f])})  "
          f"g={g!r} (card {L.card(d[g])})  |B0|={len(b0)}")

    #  the baseline ladder.  B0_half is the FIRST HALF of B0 in a
    #  deterministic order -- by cardinality then name -- so the rung is not
    #  chosen after seeing anything.
    order = sorted(b0, key=lambda c: (L.card(d[c]), str(c)))
    half = order[:max(1, len(order) // 2)]
    LADDER = [("empty", []), ("B0_half", half), ("B0", list(b0)),
              ("B0+g", list(b0) + [g])]
    print(f"  ladder: " + "  ".join(f"{nm}({len(cs)})" for nm, cs in LADDER))

    rows = []
    for level, regime in POPULATIONS:
        rng = np.random.default_rng(SEED)
        dd = d.copy()
        dd["_y"] = yv
        dd["_f"] = mask_population(dd[f], level, regime, rng)
        pop_rate = float((dd["_f"] != EMPTY).mean())
        tr, te = dd.iloc[:cut], dd.iloc[cut:]
        yte = te["_y"].values
        if len(np.unique(yte)) < 2:
            continue
        prev_tr = float(tr["_y"].mean())
        scores = {}
        t0 = time.time()
        for nm, cols in LADDER:
            #  an empty baseline is the intercept-only model; one constant
            #  column implements it without a special case in the estimator
            use = cols if cols else ["_const"]
            if not cols:
                tr = tr.assign(_const="c")
                te = te.assign(_const="c")
            scores[(nm, False)] = L.fit(tr, te, use)
            scores[(nm, True)] = L.fit(tr, te, use + ["_f"])
        print(f"  [{regime:10s} level {level:.2f} -> populated {pop_rate:.3f}] "
              f"{len(LADDER) * 2} fits in {time.time() - t0:.0f}s", flush=True)
        I = {k: instruments(p, yte, prev_tr) for k, p in scores.items()}
        for nm, _ in LADDER:
            for inst in I[(nm, False)]:
                rows.append(dict(
                    log=key, domain=domain, target=TARGET[key],
                    population=level, regime=regime, populated=pop_rate,
                    baseline=nm, instrument=inst,
                    without_f=I[(nm, False)][inst], with_f=I[(nm, True)][inst],
                    V=I[(nm, True)][inst] - I[(nm, False)][inst],
                    n=n, n_test=len(te), card_f=L.card(d[f]),
                    card_g=L.card(d[g]), n_b0=len(b0), f=f, g=g))
    return rows


def spreads(SUR):
    """The range of the range: how much each axis moves R, per log.

    R(B_lo -> B_hi) = 1 - V(f | B_hi) / V(f | B_lo) over every ordered nested
    pair of ladder rungs whose lower leg is resolvably positive.
    """
    NEST = ["empty", "B0_half", "B0", "B0+g"]
    out, red_rows = [], []
    for (log, inst, pop, reg), sub in SUR.groupby(
            ["log", "instrument", "population", "regime"]):
        v = sub.set_index("baseline").V.to_dict()
        for i, j in itertools.combinations(range(len(NEST)), 2):
            lo_, hi_ = NEST[i], NEST[j]
            if lo_ not in v or hi_ not in v or v[lo_] <= EPS:
                continue
            red_rows.append(dict(log=log, instrument=inst, population=pop,
                                 regime=reg, b_lo=lo_, b_hi=hi_,
                                 V_lo=v[lo_], V_hi=v[hi_],
                                 R=1.0 - v[hi_] / v[lo_]))
    RED = pd.DataFrame(red_rows)
    if RED.empty:
        return RED, pd.DataFrame()

    #  the reference cell: the paper's own choice on every axis.
    REF = dict(instrument="auc", population=1.00, regime="full",
               b_lo="B0", b_hi="B0+g")
    for log, sub in RED.groupby("log"):
        ref = sub[(sub.instrument == REF["instrument"])
                  & (sub.population == REF["population"])
                  & (sub.b_lo == REF["b_lo"]) & (sub.b_hi == REF["b_hi"])]
        r0 = float(ref.R.iloc[0]) if len(ref) else np.nan
        row = dict(log=log, R_reference=r0)
        #  baseline axis: hold metric/population, vary the nested pair
        s = sub[(sub.instrument == "auc") & (sub.population == 1.00)]
        row["baseline_lo"], row["baseline_hi"] = float(s.R.min()), float(s.R.max())
        #  metric axis: hold baseline/population, vary the instrument, but
        #  keep net benefit out of it -- the threshold axis is measured
        #  separately and mixing them double-counts one choice.
        s = sub[(sub.b_lo == "B0") & (sub.b_hi == "B0+g")
                & (sub.population == 1.00)
                & (~sub.instrument.str.startswith("nb_"))]
        row["metric_lo"], row["metric_hi"] = float(s.R.min()), float(s.R.max())
        #  threshold axis: net benefit over the grid.  Reported TWICE.
        #  A ratio whose denominator is positive but tiny is not a quantity --
        #  PROTOCOL.md section 1 already refuses one whose denominator crosses
        #  zero -- so the full range is printed beside a STABLE range
        #  restricted to grid points where the naive net-benefit increment is
        #  at least a tenth of its maximum over the grid.  The rule is
        #  declared, is the same for every log, and reads no outcome beyond
        #  the increment it is filtering.
        s = sub[(sub.b_lo == "B0") & (sub.b_hi == "B0+g")
                & (sub.population == 1.00)
                & (sub.instrument.str.startswith("nb_"))]
        row["threshold_lo"] = float(s.R.min()) if len(s) else np.nan
        row["threshold_hi"] = float(s.R.max()) if len(s) else np.nan
        row["threshold_n"] = int(len(s))
        if len(s):
            floor = 0.10 * float(s.V_lo.max())
            st = s[s.V_lo >= floor]
            row["threshold_lo_stable"] = float(st.R.min()) if len(st) else np.nan
            row["threshold_hi_stable"] = float(st.R.max()) if len(st) else np.nan
            row["threshold_n_stable"] = int(len(st))
        else:
            row["threshold_lo_stable"] = row["threshold_hi_stable"] = np.nan
            row["threshold_n_stable"] = 0
        #  population axis: AUC, primary pair, over the declared levels
        s = sub[(sub.b_lo == "B0") & (sub.b_hi == "B0+g")
                & (sub.instrument == "auc")]
        row["population_lo"], row["population_hi"] = float(s.R.min()), float(s.R.max())
        for a in ("baseline", "metric", "threshold", "population",
                  "threshold_stable"):
            lo_k = (f"{a}_lo" if not a.endswith("_stable")
                    else "threshold_lo_stable")
            hi_k = (f"{a}_hi" if not a.endswith("_stable")
                    else "threshold_hi_stable")
            row[f"{a}_spread"] = row[hi_k] - row[lo_k]
        out.append(row)
    return RED, pd.DataFrame(out)


def main(argv):
    keys = [a for a in argv if a in LOGS] or list(LOGS)
    t0 = time.time()
    rows = []
    for k in keys:
        rows += run_log(k)
    SUR = pd.DataFrame(rows)
    SUR.to_csv(RESULTS / "r44_surface.csv", index=False)
    RED, SPR = spreads(SUR)
    RED.to_csv(RESULTS / "r44_reductions.csv", index=False)
    SPR.to_csv(RESULTS / "r44_spread.csv", index=False)
    print("\n" + "=" * 96)
    print("THE RANGE OF THE RANGE: how much each choice moves R, per log")
    print("=" * 96)
    cols = (["log", "R_reference"]
            + [f"{a}_{s}" for a in ("baseline", "metric", "population")
               for s in ("lo", "hi")]
            + ["threshold_lo", "threshold_hi", "threshold_lo_stable",
               "threshold_hi_stable", "threshold_n_stable"])
    print(SPR[[c for c in cols if c in SPR.columns]].to_string(index=False))
    if len(SPR):
        F = pd.DataFrame([dict(
            n_logs=int(SPR.log.nunique()), n_surface_rows=len(SUR),
            n_reductions=len(RED),
            n_instruments=int(SUR[~SUR.instrument.str.startswith("nb_")]
                              .instrument.nunique()),
            n_grid=len(GRID), n_populations=len(POPULATIONS),
            min_baseline_spread=float(SPR.baseline_spread.min()),
            max_baseline_spread=float(SPR.baseline_spread.max()),
            min_metric_spread=float(SPR.metric_spread.min()),
            max_metric_spread=float(SPR.metric_spread.max()),
            min_threshold_spread=float(SPR.threshold_spread.min()),
            max_threshold_spread=float(SPR.threshold_spread.max()),
            min_threshold_stable_spread=float(SPR.threshold_stable_spread.min()),
            max_threshold_stable_spread=float(SPR.threshold_stable_spread.max()),
            min_population_spread=float(SPR.population_spread.min()),
            max_population_spread=float(SPR.population_spread.max()),
            runtime_s=round(time.time() - t0, 1))])
        F.to_csv(RESULTS / "r44_facts.csv", index=False)
        print("\n" + F.T.to_string())
    print(f"\nWrote r44_*.csv ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[1:])

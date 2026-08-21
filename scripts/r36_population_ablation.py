"""r36 -- THE DATA-QUALITY CAVEAT, REPLACED BY A CURVE.

The manuscript's Limitations say the item field is 100% populated here, that
real configuration databases are not, and that +0.103 should therefore be read
as an upper bound.  That is a caveat where a measurement is available, and it
is the single most common objection a practitioner raises.

WHAT IS MEASURED.  The item column is masked to a declared population level
and the whole ladder is re-measured.  Both baselines are untouched -- only the
item degrades -- so the curve is the value of a partially populated register,
not the value of a smaller dataset.

THREE DEGRADATION REGIMES, because how an estate empties matters more than how
empty it is:

  random            each incident's item is masked independently.  The
                    convenient assumption, and the wrong one.
  rare-first        the least frequently occurring items are dropped whole.
                    This is how a real estate degrades: discovery and manual
                    curation cover the big, central, expensive things, and the
                    long tail is what nobody has got to.
  common-first      the most frequent items are dropped whole.  Not realistic;
                    reported as the other end of the range, so the reader can
                    see how much of the answer is the regime rather than the
                    level.

A masked item becomes an explicit `__EMPTY__` level rather than a dropped row,
because a desk with a half-empty register still has the incidents.

Outputs: results/r36_curve.csv, r36_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base14 as B
from common import RESULTS

t0 = time.time()
LEVELS = (1.00, 0.90, 0.75, 0.50, 0.25, 0.10, 0.05)
REGIMES = ("random", "rare-first", "common-first")
N_BOOT = 2000
EMPTY = "__EMPTY__"

D = B.D.copy()
TR, TE = B.split(D)
y = B.y
n = len(D)

# the two baselines never move
p_b0 = B.fit(TR, TE, B.INTAKE)
p_bg = B.fit(TR, TE, B.BQ)
auc_b0, auc_bg = roc_auc_score(y, p_b0), roc_auc_score(y, p_bg)
print("=" * 92)
print("THE VALUE OF A PARTIALLY POPULATED REGISTER")
print("=" * 92)
print(f"  cohort {n:,}   test {len(y):,}   items {D[B.IDENT].nunique():,}")
print(f"  intake-only baseline AUC {auc_b0:.4f};  "
      f"intake + group baseline AUC {auc_bg:.4f}\n")


def mask_item(level, regime, seed=B.SEED):
    """Return a copy of the item column masked to `level` population."""
    col = D[B.IDENT].astype(str).values
    if level >= 1.0:
        return col.copy()
    if regime == "random":
        r = np.random.default_rng(seed)
        keep = r.random(n) < level
        out = np.where(keep, col, EMPTY)
        return out
    vc = pd.Series(col).value_counts()
    order = vc.index.tolist()
    if regime == "rare-first":
        order = order[::-1]                 # rarest first in the drop order
    # Drop whole items, never overshooting the requested level.  The first
    # version stopped AFTER the item that crossed the target, and since the
    # two largest items hold 11% of this estate between them, "5% populated,
    # rarest dropped first" came out at 0.0% populated with zero items left.
    # `actual_population` is reported beside `level` either way, but a row
    # labelled 5% that holds nothing is not a point on a curve.
    target_drop = (1.0 - level) * n
    dropped, acc = set(), 0.0
    for v in order:
        w = float(vc[v])
        if acc + w > target_drop:
            continue
        dropped.add(v)
        acc += w
    return np.where(pd.Series(col).isin(dropped).values, EMPTY, col)


def paired_boot(pa, pb, pc, pd_, n_boot=N_BOOT, seed=B.SEED):
    """Intervals on both increments and on the reduction, one index set per
    draw shared by all four score vectors."""
    rng = np.random.default_rng(seed)
    dn, dh = [], []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        yy = y[i]
        if len(np.unique(yy)) < 2:
            continue
        dn.append(roc_auc_score(yy, pb[i]) - roc_auc_score(yy, pa[i]))
        dh.append(roc_auc_score(yy, pd_[i]) - roc_auc_score(yy, pc[i]))
    dn, dh = np.array(dn), np.array(dh)
    ok = dn > 0
    red = np.full(len(dn), np.nan)
    red[ok] = 1.0 - dh[ok] / dn[ok]
    return dict(naive_lo=float(np.percentile(dn, 2.5)),
                naive_hi=float(np.percentile(dn, 97.5)),
                honest_lo=float(np.percentile(dh, 2.5)),
                honest_hi=float(np.percentile(dh, 97.5)),
                frac_denom_pos=float(ok.mean()),
                reduction_lo=float(np.nanpercentile(red, 2.5)) if ok.all() else np.nan,
                reduction_hi=float(np.nanpercentile(red, 97.5)) if ok.all() else np.nan)


rows = []
print(f"  {'regime':13s} {'level':>6s} {'actual':>7s} {'items':>6s} "
      f"{'naive':>9s} {'honest':>9s} {'reduction':>10s} {'95% CI':>16s}")
for regime in REGIMES:
    for level in LEVELS:
        if level >= 1.0 and regime != REGIMES[0]:
            continue                      # 100% is the same column in all three
        col = mask_item(level, regime)
        d2 = D.copy()
        d2["_item"] = col
        actual = float((col != EMPTY).mean())
        n_items = int(pd.Series(col[col != EMPTY]).nunique())
        tr2, te2 = B.split(d2)
        p_n1 = B.fit(tr2, te2, B.INTAKE + ["_item"])
        p_h1 = B.fit(tr2, te2, B.BQ + ["_item"])
        a_n1, a_h1 = roc_auc_score(y, p_n1), roc_auc_score(y, p_h1)
        vn, vh = a_n1 - auc_b0, a_h1 - auc_bg
        rec = dict(regime=regime if level < 1.0 else "full",
                   level=level, actual_population=actual, n_items=n_items,
                   auc_b0=auc_b0, auc_b0f=a_n1, auc_b0g=auc_bg,
                   auc_b0gf=a_h1, naive=vn, honest=vh,
                   reduction=(1 - vh / vn) if vn > 0 else np.nan)
        rec.update(paired_boot(p_b0, p_n1, p_bg, p_h1))
        rows.append(rec)
        ci = (f"[{rec['reduction_lo']:.3f},{rec['reduction_hi']:.3f}]"
              if np.isfinite(rec["reduction_lo"]) else "not reportable")
        print(f"  {rec['regime']:13s} {level:>6.0%} {actual:>7.1%} "
              f"{n_items:>6,} {vn:>+9.4f} {vh:>+9.4f} "
              f"{rec['reduction']:>10.4f} {ci:>16s}"
              f"   ({time.time() - t0:.0f}s)")

CUR = pd.DataFrame(rows)
CUR.to_csv(RESULTS / "r36_curve.csv", index=False)

full = CUR[CUR.regime == "full"].iloc[0]
rare = CUR[CUR.regime == "rare-first"].sort_values("level")
rand = CUR[CUR.regime == "random"].sort_values("level")
comm = CUR[CUR.regime == "common-first"].sort_values("level")


def half_life(sub):
    """The population level at which the honest increment falls to half its
    full-population value.  Linear interpolation between the two bracketing
    grid points; None if it does not cross."""
    s = sub.sort_values("level")
    tgt = float(full.honest) / 2.0
    lo = s[s.honest < tgt]
    hi = s[s.honest >= tgt]
    if lo.empty or hi.empty:
        return np.nan
    a, b = lo.iloc[-1], hi.iloc[0]
    if b.honest == a.honest:
        return float(b.level)
    return float(a.level + (tgt - a.honest) * (b.level - a.level)
                 / (b.honest - a.honest))


hl = {r: half_life(CUR[CUR.regime == r]) for r in REGIMES}
print("\n" + "=" * 92)
print("WHAT THE CURVE SAYS")
print("=" * 92)
print(f"""  At full population the item is worth {full.naive:+.4f} over the intake block
  and {full.honest:+.4f} over intake + the opening group, a reduction of {full.reduction:.1%}.

  Population at which the group-aware increment falls to half of that:
    random        {hl['random']:.1%}
    rare-first    {hl['rare-first']:.1%}
    common-first  {hl['common-first']:.1%}

  The gap between the regimes is the point.  Dropping the long tail costs
  little because the long tail is thin; dropping the frequent items costs a
  great deal.  A practitioner reading only the random curve would price a
  half-populated register wrongly in whichever direction their estate
  actually degrades.""")

facts = dict(
    n=n, n_test=len(y), n_items=int(D[B.IDENT].nunique()),
    auc_b0=auc_b0, auc_bg=auc_bg,
    full_naive=float(full.naive), full_honest=float(full.honest),
    full_reduction=float(full.reduction),
    half_life_random=hl["random"], half_life_rare=hl["rare-first"],
    half_life_common=hl["common-first"],
    honest_at_50_random=float(rand[rand.level == 0.50].honest.iloc[0]),
    honest_at_50_rare=float(rare[rare.level == 0.50].honest.iloc[0]),
    honest_at_50_common=float(comm[comm.level == 0.50].honest.iloc[0]),
    honest_at_25_rare=float(rare[rare.level == 0.25].honest.iloc[0]),
    honest_at_10_rare=float(rare[rare.level == 0.10].honest.iloc[0]),
    reduction_lo=float(CUR.reduction.min()), reduction_hi=float(CUR.reduction.max()),
    n_resolved_honest=int((CUR.honest_lo > 0).sum()), n_rows=len(CUR),
    runtime_s=round(time.time() - t0, 1),
)
pd.DataFrame([facts]).to_csv(RESULTS / "r36_facts.csv", index=False)
print(f"\n  The group-aware increment's interval excludes zero at "
      f"{facts['n_resolved_honest']} of {len(CUR)} points on the curve.")
print(f"  Wrote r36_curve.csv, r36_facts.csv  ({facts['runtime_s']:.0f}s)")

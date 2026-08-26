"""s45 -- A PREFIX AXIS, ON ONE LOG.  DOES THE ARGUMENT SURVIVE IT?

Round twenty-seven.  Section 11 names one structural omission and calls it
the clearest next study: prefix length, prefix bucketing and sequence encoding
are the axes predictive process monitoring varies most, and this paper varies
none of them, because it predicts at ONE prediction point from creation-time
attributes.  Section 11 therefore claims no result about that literature's
benchmark.  A reviewer from that literature is entitled to ask the obvious
next question anyway -- *does your conclusion survive on our axis, or is it an
artefact of predicting at case creation?* -- and this file answers it on one
log rather than leaving the question open.

WHAT A PREFIX AXIS IS HERE.  A case is a service-desk incident and its events
are its assignment-group activities.  At prefix length k the analyst stands
after the case's k-th event: more is known, fewer cases are still in scope,
and the question is about what happens NEXT.  So the axis moves three things
at once -- population, information and admissible set -- which is exactly what
Section 7.2 shows the DECISION TIME moves.  The prefix axis is the same
argument of the estimand under the other literature's name, and that is the
claim this file tests.

THE SETUP, DECLARED BEFORE IT WAS RUN.
  population    cases with more than k events AND no group change in the first
                k, i.e. the cases still at risk at the moment of prediction.
                A case whose outcome is already determined by k is not a
                prediction problem.
  target        does a group change occur AFTER event k?  This is the
                registered handover rule of Section 5 restricted to the
                remaining suffix, so nothing already observed is predicted.
  baseline      the intake block, PLUS what the prefix has revealed: the
                group the case sits in now, how many events have happened,
                and how many distinct groups have been seen.  This is a
                prefix-aware baseline, which is what the PPM literature
                builds; giving the baseline the prefix and not the register is
                the comparison that can embarrass the register.
  register      the affected configuration item, as everywhere else.
  split         the same fixed temporal holdout at 70% of the row order,
                under the same declared tie-break, taken on the ORIGINAL case
                order so that every prefix uses the same cut in time.
  inference     the weighted block bootstrap of `spec.block_weights`, at
                --draws draws, pivotal interval.

WHAT WOULD FALSIFY THE PAPER'S ARGUMENT.  If the register's increment were
flat across prefixes, the decision time would not be an argument of the
estimand after all and Section 7 would be describing an artefact of one
prediction point.  The result is written to results/s45_prefix.csv whichever
way it comes out.

    python s45_prefix.py                    # BPIC14, the case study's log
    python s45_prefix.py --draws 50         # a smoke test

Outputs: results/s45_prefix.csv, results/s45_facts.csv
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec as S  # noqa: E402
import r32_corpus as C  # noqa: E402
from common import RESULTS  # noqa: E402

LOG = "BPIC14"
SEQ = "_seq_assignment group"
REGISTER = "CI Name (aff)"
INTAKE = ["Category", "Impact", "Urgency", "Priority"]
#: declared before the run.  0 is case creation, which is the paper's own
#: prediction point and the anchor the rest are read against.
PREFIXES = (0, 1, 2, 3, 5, 8)
DRAWS = 300


def sequences(d):
    """One list of assignment groups per case, in time order, missing values
    dropped -- the same parse the registered handover rule uses."""
    return [[x for x in str(s).split("|") if x and x != "nan"]
            for s in d[SEQ].values]


def at_prefix(d, seqs, k):
    """The population, the target and the prefix-revealed features at prefix
    k.  Returns a frame with `_y` attached, or None when too little is left.

    A case is in scope when it has more than k events and its first k events
    are all in one group; the target is whether any LATER event changes group.
    At k = 0 that is exactly the registered handover rule on the whole cohort,
    which is the anchor.
    """
    keep, y, now, n_ev, n_grp = [], [], [], [], []
    for i, s in enumerate(seqs):
        if len(s) <= k:
            continue
        pre, post = s[:k], s[k:]
        if k > 0 and len(set(pre)) > 1:
            continue                      # already handed over: not at risk
        seen = set(pre) if k else set()
        here = pre[-1] if k else (post[0] if post else "")
        #  a change after the moment of prediction: any later group differing
        #  from the one the case is in now, or from any group already seen
        later = set(post) | ({here} if here else set())
        keep.append(i)
        y.append(int(len(later - ({here} if here else set())) > 0
                     if k else len(set(s)) > 1))
        now.append(here or "?")
        n_ev.append(k)
        n_grp.append(len(seen) if k else 0)
    if len(keep) < 400:
        return None
    out = d.iloc[keep].copy()
    out["_y"] = np.asarray(y, int)
    out["_pre_group"] = now
    out["_pre_n_events"] = n_ev
    out["_pre_n_groups"] = n_grp
    return out


def one_cell(d, cols_base, cols_full, cut, w=None):
    tr, te = d.iloc[:cut], d.iloc[cut:]
    y = te["_y"].values
    if len(np.unique(y)) < 2 or len(np.unique(tr["_y"].values)) < 2:
        return None
    kw = {} if w is None else {"sample_weight": w[1]}
    p0 = S._onehot_logit(tr, te, cols_base, tr["_y"].values, S.SEED,
                         w=None if w is None else w[0])
    p1 = S._onehot_logit(tr, te, cols_full, tr["_y"].values, S.SEED,
                         w=None if w is None else w[0])
    a0 = roc_auc_score(y, p0, **kw)
    a1 = roc_auc_score(y, p1, **kw)
    return float(a0), float(a1), float(a1 - a0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args(argv)

    t0 = time.time()
    print("=" * 92)
    print("s45  A PREFIX AXIS ON %s -- THE ONE AXIS SECTION 11 SAYS THIS "
          "STUDY CANNOT VARY" % LOG)
    print("=" * 92)
    d = C.load(LOG)
    #  the same temporal order and the same declared tie-break as the case
    #  study: by open time, then by incident identifier
    d = d.dropna(subset=["_t_first"]).sort_values(
        ["_t_first", "Incident ID"], kind="mergesort").reset_index(drop=True)
    seqs = sequences(d)
    rows = []
    for k in PREFIXES:
        sub = at_prefix(d, seqs, k)
        if sub is None:
            print("  prefix %d: too few cases still at risk" % k)
            continue
        cut = int(len(sub) * S.TRAIN_FRAC)
        base = list(INTAKE)
        if k > 0:
            base += ["_pre_group", "_pre_n_groups"]
        full = base + [REGISTER]
        pt = one_cell(sub, base, full, cut)
        if pt is None:
            print("  prefix %d: degenerate target" % k)
            continue
        a0, a1, v = pt
        #  the weighted block bootstrap, on the same split
        vs = []
        rng = np.random.default_rng(S.SEED + 31 * k)
        ntr, nte = cut, len(sub) - cut
        for b in range(a.draws):
            wtr = S.block_weights(ntr, rng)
            wte = S.block_weights(nte, rng)
            r = one_cell(sub, base, full, cut, w=(wtr, wte))
            if r is not None:
                vs.append(r[2])
        vs = np.asarray(vs, float)
        lo = hi = np.nan
        if len(vs) > 20:
            lo = 2 * v - float(np.percentile(vs, 97.5))
            hi = 2 * v - float(np.percentile(vs, 2.5))
        rows.append(dict(
            log=LOG, prefix=k, n=len(sub), n_train=cut, n_test=len(sub) - cut,
            prevalence=float(sub["_y"].mean()),
            prevalence_test=float(sub["_y"].values[cut:].mean()),
            card_register=int(sub[REGISTER].astype(str).nunique()),
            base_auc=a0, with_auc=a1, V=v,
            se=float(vs.std(ddof=1)) if len(vs) > 1 else np.nan,
            lo=lo, hi=hi, n_draws=int(len(vs)),
            resolved=bool(np.isfinite(lo) and (lo > 0 or hi < 0))))
        print("  prefix %d  n %6d  prev %.3f  base %.4f  with %.4f  "
              "V %+.4f [%+.4f, %+.4f]"
              % (k, len(sub), rows[-1]["prevalence_test"], a0, a1, v, lo, hi))

    P = pd.DataFrame(rows)
    P.to_csv(RESULTS / "s45_prefix.csv", index=False)
    if len(P):
        anchor = P[P.prefix == 0]
        v0 = float(anchor.V.iloc[0]) if len(anchor) else np.nan
        deepest = P[P.prefix == P.prefix.max()].iloc[0]
        facts = dict(
            log=LOG, n_prefixes=len(P), draws=a.draws,
            prefix_min=int(P.prefix.min()), prefix_max=int(P.prefix.max()),
            v_at_creation=v0,
            v_at_deepest=float(deepest.V),
            n_at_creation=int(anchor.n.iloc[0]) if len(anchor) else 0,
            n_at_deepest=int(deepest.n),
            v_min=float(P.V.min()), v_max=float(P.V.max()),
            v_range=float(P.V.max() - P.V.min()),
            share_of_creation_retained=(float(deepest.V) / v0
                                        if v0 else np.nan),
            n_resolved=int(P.resolved.sum()),
            n_prefixes_positive=int((P.V > 0).sum()),
            base_auc_at_creation=float(anchor.base_auc.iloc[0])
            if len(anchor) else np.nan,
            base_auc_at_deepest=float(deepest.base_auc),
            runtime_s=round(time.time() - t0, 1))
        pd.DataFrame([facts]).to_csv(RESULTS / "s45_facts.csv", index=False)
        print("\n" + pd.Series(facts).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())

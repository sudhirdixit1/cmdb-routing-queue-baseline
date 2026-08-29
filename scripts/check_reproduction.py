"""check_reproduction -- IS THE REPRODUCTION CLAIM TRUE, OR ONLY ASSERTED?

Round twenty-seven.  `ROUND27-STATE.md` recorded that the boosting learner
does not reproduce this repository's committed surface on a second machine.
No gate caught it, and the reason is structural: `verify_release.py`,
`verify_numbers.py` and `claim_registry.py` all re-derive macros from the
committed CSVs.  They check that the manuscript agrees with the result files.
Not one of them re-runs an analysis, so none of them can see a result file
that the code no longer produces.  This file re-runs one.

WHAT THE DIAGNOSIS FOUND, and why the tolerances below are not symmetric.
Four candidate causes were eliminated by measurement rather than argument:
thread count (one thread and four give bit-identical answers), library
version (scikit-learn 1.7.2 and 1.9.0, pandas 2.2.3 and 2.3.1, CPython 3.11
and 3.13 all give bit-identical answers), source drift (the `spec.py` of the
commit that wrote the surface gives bit-identical answers), and run-to-run
nondeterminism (there is none).  What remains is the machine.  The committed
surface was produced on x86-64; this one is arm64.

The divergence is not spread evenly, and that is the useful part.  It tracks
CARDINALITY, not the arm and not the learner:

  *  wherever the design matrix is low-cardinality -- the `B_empty` and
     `B_half` rungs, either arm, either family -- the surface reproduces to
     2.3e-12, and the boosting half of that to 4.4e-16, machine epsilon;
  *  the logistic learner reproduces to 2.0e-8 on the `without_f` arm at
     EVERY rung, and to 6.9e-9 on the `with_f` arm wherever the register is
     undegraded;
  *  everything else -- the boosting learner as soon as any high-cardinality
     column enters, and both learners once a degradation mechanism runs --
     is where the discrepancies are.

The two families fail differently there.  The logistic model itself is
reproducible: its predicted probabilities agree to 1.4e-15, and on undegraded
cells its smooth metrics agree to 1e-11.  What moves is the DISCRETE
summaries -- AUC, average precision, net benefit -- because a one-hot design
over a register produces test rows with exactly equal predictions, and a
1e-15 difference resolves those ties the other way.  (Fitting the same cell
through the sparse and the dense code path on THIS machine reproduces the
committed AUC discrepancy exactly: identical probabilities, AUC apart by
1.3e-4.)  The degraded cells add a second, larger source: `mask_rare` cuts
the cumulative-count curve inside a group of identities that share a count,
and `corrupt` maps its draws onto a tie-ordered index, so which identities
are masked or corrupted is decided by a tie order nothing pins.

The boosting model is not reproducible at all in that arm.  It is chaotic,
and measurably so: nudging the encoding matrix by ONE ULP -- a relative
change of 2.2e-16 -- moves a predicted probability by 0.37 and Nagelkerke by
0.038.  Histogram binning and split-gain ties do that.  59% of its committed
values still come back to 1e-12; the rest can land anywhere.

SO WHAT IS GATED.  Conditions 1-4 are tight and would fail on a real
regression.  Condition 5 is a ceiling, not a proof of reproduction, and is
labelled as one: it catches a change LARGER than platform drift explains and
is honest that it cannot catch a smaller one.  Condition 6 stops the prose
and this file from drifting apart.

  1.  THE INPUTS MUST BE THE SAME INPUTS.  Before any tolerance means
      anything, the frame, the split, the role assignment and the prevalence
      must be identical to the committed run's.  If a corpus file were
      re-fetched at a different version this condition, not the tolerances,
      is the one that fires.

  2a. THE LOW-CARDINALITY RUNGS ARE BIT-EXACT, BOTH FAMILIES.  On `B_empty`
      and `B_half`, `without_f`, to 1e-9.  Measured across machines: 2.3e-12,
      and 4.4e-16 for the boosting learner alone.  This is the condition that
      reaches the boosting code path tightly -- the only one that does -- and
      it still exercises the loader, the roles, the ladder, the splits and
      the degradation.

  2b. THE LOGISTIC `without_f` ARM IS BIT-EXACT AT EVERY RUNG.  To 1e-6;
      measured 2.0e-8.  This is the widest tight condition available: every
      rung, every quality mechanism, every split, 2,592 values per arm.

  3.  THE LOGISTIC MODEL REPRODUCES WHERE NOTHING IS DEGRADED.  On `clean`
      and `stale` cells the smooth metrics -- Nagelkerke, scaled Brier,
      log-loss skill -- reproduce to 1e-6 on the `with_f` arm too.  Measured:
      6.9e-9.  Note the deliberate restriction to SMOOTH metrics: AUC on the
      same cells moves by 9.4e-4, because the one-hot register ties test rows
      to equal predictions and a 1e-15 difference unties them.

  4.  ONE MACHINE IS DETERMINISTIC.  The manuscript claims a seeded pipeline.
      The same cell is fitted twice in this process and the two results must
      be bit-identical, for both families.  This is the property the paper
      actually needs and the one that is actually true.

  5.  NOTHING EXCEEDS THE DOCUMENTED PLATFORM TOLERANCE.  Every value is
      required to sit inside the bound `REPRODUCE.md` prints for its family
      and metric class.  A code change that moved a number further than the
      platform can is caught here; one that moved it less is not, and no
      arrangement of this repository's current pipeline could catch it.

  6.  THE GATE AND THE PROSE QUOTE ONE NUMBER.  The bounds below are parsed
      out of `REPRODUCE.md`'s tolerance table and compared against the
      constants here, so the disclosure cannot be edited into disagreeing
      with the check that is supposed to execute it.

COST.  The default re-runs ONE (log, target) pair -- Sepsis, 1,050 cases --
for both learner families, which is the smallest arm that exercises both:
about 50 s, single-threaded, one process.  It is deliberately not the whole
surface; the whole surface is 35 minutes and this has to be cheap enough to
run beside the other gates.  `--wide` re-runs the four cheap logs the
documented bounds were measured over (about 3 min) and re-derives the table.

    python scripts/check_reproduction.py           # the gate, ~50 s
    python scripts/check_reproduction.py --wide    # re-derive the bounds
    python scripts/check_reproduction.py --table   # print, do not judge

Exit status is non-zero on any failure.
"""
from __future__ import annotations

import os

#  Single-threaded, and set before numpy or sklearn is imported, for the same
#  reason s01 does it: the pool parallelises over tasks and the boosting
#  learner over threads.  Pinning these does NOT make the surface reproduce
#  across machines -- that was measured, and it is why this file exists -- but
#  it keeps the gate from fighting whatever else is running.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

FAILS = []

#  the metric classes, which fail for different reasons and so carry different
#  bounds.  `smooth` is a differentiable function of the predictions; `rank`
#  and `threshold` are step functions of them and move by a whole step when a
#  tie resolves the other way.
SMOOTH = ("nagelkerke", "brier_skill", "logloss_skill")
RANK = ("auc", "ap")


def metric_class(m):
    if m in SMOOTH:
        return "smooth"
    if m in RANK:
        return "rank"
    return "threshold"


#  The gate's own tight bounds.  These are not platform tolerances; they are
#  the parts that DO reproduce, with headroom over the measured value.
LOWCARD_TOL = 1e-9             # measured 2.3e-12 (the boosting half: 4.4e-16)
LOGIT_WITHOUT_TOL = 1e-6       # measured 2.0e-8, every rung
LOGIT_UNDEGRADED_TOL = 1e-6    # measured 6.9e-9, smooth metrics only
UNDEGRADED = ("clean", "stale")
#  the rungs whose design matrix carries no high-cardinality categorical, and
#  which therefore reproduce for the boosting learner as well
LOW_RUNGS = ("B_empty", "B_half")

#  The documented platform tolerance, per family and metric class.  These are
#  the numbers REPRODUCE.md prints; condition 6 checks that they still are.
#  Measured over 41,472 values: four logs, both families, every cell of the
#  quality and split axes.  Re-derive with --wide.
PLATFORM = {
    ("logistic", "smooth"): 0.10,
    ("logistic", "rank"): 0.05,
    ("logistic", "threshold"): 0.15,
    ("boosting", "smooth"): 0.90,
    ("boosting", "rank"): 0.15,
    ("boosting", "threshold"): 0.40,
}

CHEAP = [("Sepsis", "duration")]
WIDE = [("Sepsis", "duration"), ("BPIC13_closed", "handover"),
        ("Helpdesk", "duration"), ("BPIC15_1", "duration")]
KEY = ["log", "target", "learner", "split", "quality", "level", "rung",
       "metric"]
STRUCTURAL = ("n", "n_test", "card_f", "card_g", "n_b0")


def _committed():
    from common import RESULTS
    p = RESULTS / "s01_surface.csv.gz"
    if not p.exists():
        FAILS.append("results/s01_surface.csv.gz is absent; there is nothing "
                     "to reproduce against")
        return None
    return pd.read_csv(p)


def _rerun(log, target, learner, C):
    """One (log, target, learner) arm, through s01's own run_task, merged
    against the committed rows.  Using s01's function rather than a copy of
    its loop is deliberate: a gate that reimplements the thing it checks
    checks the reimplementation."""
    import s01_surface as A
    domain = str(C[(C.log == log) & (C.target == target)].domain.iloc[0])
    rows, _fits, _checks, err = A.run_task((log, target, domain, learner))
    if err:
        FAILS.append("re-running %s/%s/%s failed: %s"
                     % (log, target, learner, err.get("reason")))
        return None
    G = pd.DataFrame(rows)
    sub = C[(C.log == log) & (C.target == target) & (C.learner == learner)]
    M = sub.merge(G, on=KEY, suffixes=("_c", "_g"), how="inner")
    if len(M) != len(sub):
        FAILS.append(
            "re-running %s/%s/%s produced %d of the committed run's %d cells; "
            "the grid the code walks is not the grid the surface carries"
            % (log, target, learner, len(M), len(sub)))
        return None
    M["d_without"] = (M.without_f_c - M.without_f_g).abs()
    M["d_with"] = (M.with_f_c - M.with_f_g).abs()
    M["d_max"] = np.maximum(M.d_without, M.d_with)
    M["family"] = "boosting" if learner.startswith("hgb") else "logistic"
    M["cls"] = M.metric.map(metric_class)
    return M


def _documented_bounds():
    """The tolerance table as REPRODUCE.md prints it.  Rows look like

        | boosting | smooth ... | 0.851086 | 0.90 |

    and the last cell is the bound.  Returns {(family, cls): bound}."""
    p = ROOT / "REPRODUCE.md"
    if not p.exists():
        FAILS.append("REPRODUCE.md is absent; the tolerances are undocumented")
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        fam = cells[0].lower()
        if fam not in ("logistic", "boosting"):
            continue
        cls = cells[1].split()[0].lower()
        try:
            out[(fam, cls)] = float(cells[-1])
        except ValueError:
            continue
    return out


def _determinism(log, target, C):
    """Condition 4.  Fit the same cell twice, in this process, and require
    bit-identity -- for the boosting learner especially, because that is the
    learner whose reproducibility is in question and determinism on one
    machine is the part of it that holds."""
    import spec as S
    import s01_surface as A
    d, ladder, f, meta = A.prepare(log, target)
    if d is None:
        FAILS.append("determinism check could not prepare %s/%s: %s"
                     % (log, target, meta))
        return
    n = len(d)
    _nm, tri, tei = next(iter(S.splits(n, "holdout70")))
    yte = d["_y"].values[tei]
    prev = float(d["_y"].values[tri].mean())
    dd = d.copy()
    dd["_f"] = S.degrade(d[f], "clean", 1.0, np.random.default_rng(S.SEED),
                         tri)
    tr, te = dd.iloc[tri], dd.iloc[tei]
    cols = [c for r, c in ladder if r == "B_intake"][0]
    cc = list(cols) + ["_f"]
    for learner in ("logit", "hgb"):
        a = S.LEARNERS[learner](tr, te, cc, tr["_y"].values, S.SEED)
        b = S.LEARNERS[learner](tr, te, cc, tr["_y"].values, S.SEED)
        if not np.array_equal(a, b):
            FAILS.append(
                "condition 4: %s is not deterministic on one machine -- two "
                "fits of the same cell differ by up to %.3e, and the "
                "manuscript claims a seeded pipeline"
                % (learner, float(np.max(np.abs(a - b)))))
        Ma = S.all_metrics(a, yte, prev)
        Mb = S.all_metrics(b, yte, prev)
        bad = [k for k in Ma if Ma[k] != Mb[k]]
        if bad:
            FAILS.append(
                "condition 4: %s gives %d metric(s) that differ between two "
                "identical fits: %s"
                % (learner, len(bad), ", ".join(sorted(bad)[:4])))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--wide", action="store_true",
                    help="the four logs the documented bounds were measured "
                         "over, instead of the one")
    ap.add_argument("--table", action="store_true",
                    help="print the measured table and exit 0 without judging")
    a = ap.parse_args(argv)

    t0 = time.time()
    C = _committed()
    if C is None:
        print("check_reproduction: 1 failure")
        print("  FAIL  " + FAILS[0])
        return 1

    pairs = WIDE if a.wide else CHEAP
    parts = []
    for log, target in pairs:
        for learner in ("logit", "hgb"):
            M = _rerun(log, target, learner, C)
            if M is not None:
                parts.append(M)
    if not parts:
        print("check_reproduction: %d failure(s)" % len(FAILS))
        for f in FAILS:
            print("  FAIL  " + f)
        return 1
    D = pd.concat(parts, ignore_index=True)

    T = D.groupby(["family", "cls"]).agg(
        n=("d_max", "size"), measured=("d_max", "max"),
        exact=("d_max", lambda s: float((s <= 1e-12).mean())))
    if a.table:
        print("check_reproduction --table   %d values, %d arms, %.0fs"
              % (len(D), len(parts), time.time() - t0))
        print(T.to_string())
        print("\nwithout_f arm, max |delta|   %.3e" % D.d_without.max())
        print("with_f    arm, max |delta|   %.3e" % D.d_with.max())
        return 0

    # 1.  the inputs must be the same inputs
    for c in STRUCTURAL:
        bad = D[D[c + "_c"].values != D[c + "_g"].values]
        if len(bad):
            FAILS.append(
                "condition 1: %s differs between the committed run and this "
                "one (%s vs %s) on %d cells; the data or the split is not the "
                "same, so no tolerance below means anything"
                % (c, sorted(set(bad[c + "_c"]))[:3],
                   sorted(set(bad[c + "_g"]))[:3], len(bad)))
    bad = D[~np.isclose(D.prevalence_c, D.prevalence_g, rtol=0, atol=1e-12)]
    if len(bad):
        FAILS.append("condition 1: the target prevalence differs on %d cells; "
                     "the outcome is not the same outcome" % len(bad))
    for c in ("f", "g"):
        bad = D[D[c + "_c"].values != D[c + "_g"].values]
        if len(bad):
            FAILS.append(
                "condition 1: the %s field resolved to %r and the committed "
                "run used %r; the roles are not the same roles"
                % (c, sorted(set(bad[c + "_g"]))[:2],
                   sorted(set(bad[c + "_c"]))[:2]))

    # 2a.  the low-cardinality rungs are bit-exact, both families
    L = D[D.rung.isin(LOW_RUNGS)]
    bad = L[L.d_without > LOWCARD_TOL]
    if len(bad):
        w = bad.nlargest(1, "d_without").iloc[0]
        FAILS.append(
            "condition 2a: the low-cardinality rungs do not reproduce -- %d "
            "of %d values exceed %.0e, worst %.3e at %s/%s/%s %s %s %.2f "
            "%s/%s.  Those rungs carry no high-cardinality categorical and "
            "reproduce to 2.3e-12 across machines, so this is a regression in "
            "the pipeline, not the platform"
            % (len(bad), len(L), LOWCARD_TOL, w.d_without, w.log, w.target,
               w.learner, w.split, w.quality, w.level, w.rung, w.metric))

    # 2b.  the logistic without_f arm is bit-exact at every rung
    G = D[D.family == "logistic"]
    bad = G[G.d_without > LOGIT_WITHOUT_TOL]
    if len(bad):
        w = bad.nlargest(1, "d_without").iloc[0]
        FAILS.append(
            "condition 2b: the logistic without_f arm does not reproduce -- "
            "%d of %d values exceed %.0e, worst %.3e at %s/%s %s %s %.2f "
            "%s/%s.  That arm reproduces to 2.0e-8 across machines at every "
            "rung; this is the code changing"
            % (len(bad), len(G), LOGIT_WITHOUT_TOL, w.d_without, w.log,
               w.target, w.split, w.quality, w.level, w.rung, w.metric))

    # 3.  the logistic model is bit-exact where nothing is degraded
    U = D[(D.family == "logistic") & (D.quality.isin(UNDEGRADED))
          & (D.cls == "smooth")]
    bad = U[U.d_with > LOGIT_UNDEGRADED_TOL]
    if len(bad):
        w = bad.nlargest(1, "d_with").iloc[0]
        FAILS.append(
            "condition 3: the logistic learner's smooth metrics do not "
            "reproduce on undegraded cells -- %d of %d exceed %.0e, worst "
            "%.3e at %s/%s %s %s/%s.  The logistic model reproduces across "
            "machines to 6.9e-9 there; this is the code changing"
            % (len(bad), len(U), LOGIT_UNDEGRADED_TOL, w.d_with, w.log,
               w.target, w.split, w.rung, w.metric))

    # 4.  one machine is deterministic
    _determinism(*CHEAP[0], C)

    # 5.  nothing exceeds the documented platform tolerance
    for (fam, cls), bound in sorted(PLATFORM.items()):
        sub = D[(D.family == fam) & (D.cls == cls)]
        if not len(sub):
            continue
        bad = sub[sub.d_max > bound]
        if len(bad):
            w = bad.nlargest(1, "d_max").iloc[0]
            FAILS.append(
                "condition 5: %s / %s reaches %.3e against a documented "
                "platform tolerance of %.2f, at %s/%s %s %s %.2f %s/%s.  "
                "Platform drift does not reach that far; something changed"
                % (fam, cls, w.d_max, bound, w.log, w.target, w.split,
                   w.quality, w.level, w.rung, w.metric))

    # 6.  the gate and the prose quote one number
    doc = _documented_bounds()
    if doc:
        for k, v in sorted(PLATFORM.items()):
            if k not in doc:
                FAILS.append(
                    "condition 6: REPRODUCE.md's tolerance table has no row "
                    "for %s / %s, and this gate enforces one at %.2f"
                    % (k[0], k[1], v))
            elif abs(doc[k] - v) > 1e-12:
                FAILS.append(
                    "condition 6: REPRODUCE.md documents a tolerance of %.3f "
                    "for %s / %s and this gate enforces %.3f; the disclosure "
                    "and the check that executes it disagree"
                    % (doc[k], k[0], k[1], v))
        for k in sorted(set(doc) - set(PLATFORM)):
            FAILS.append(
                "condition 6: REPRODUCE.md documents a tolerance for %s / %s "
                "that this gate does not enforce" % (k[0], k[1]))

    print("check_reproduction: %d values re-run over %d arm(s) in %.0fs, "
          "%d failure(s)" % (len(D), len(parts), time.time() - t0, len(FAILS)))
    print("  low-cardinality rungs, without_f   %.3e   (bound %.0e)"
          % (D[D.rung.isin(LOW_RUNGS)].d_without.max(), LOWCARD_TOL))
    print("  logistic without_f, every rung     %.3e   (bound %.0e)"
          % (D[D.family == "logistic"].d_without.max(), LOGIT_WITHOUT_TOL))
    print("  logistic with_f, undegraded, smooth %.3e   (bound %.0e)"
          % (U.d_with.max() if len(U) else float("nan"),
             LOGIT_UNDEGRADED_TOL))
    for (fam, cls), r in T.iterrows():
        print("  %-9s %-9s n=%5d  measured %.3e  bound %.2f  exact %5.1f%%"
              % (fam, cls, r.n, r.measured, PLATFORM.get((fam, cls), float("nan")),
                 100.0 * r.exact))
    for f in FAILS:
        print("  FAIL  " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

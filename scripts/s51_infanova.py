"""s51 -- THE DECOMPOSITION ON THE INFERENCE SURFACE, AND WHAT IT DOES NOT SHOW.

Round twenty-seven.  Section 4.2 conceded that the inference surface is "a
corner of the declared surface rather than a design ... which is why the
decomposition cannot be computed on it".  That was true of a surface chosen by
row count, which was axis-complete and UNBALANCED.  The designed surface is a
balanced full factorial on every pair, so the exact functional ANOVA of s22
applies to it unchanged, and this file applies it.

WHAT IT SETTLES.  The concession goes: the decomposition IS computable there,
on every pair and every instrument, and this file is the evidence.

WHAT IT DOES NOT SETTLE, WHICH IS THE REASON THIS DOCSTRING IS LONG.  The
tempting next sentence is that the inference surface's decomposition
"confirms" the declared surface's.  IT DOES NOT.  The two agree on which axis
carries the largest first-order index on a minority of pairs, and their corpus
medians differ.

Nor is the opposite available.  THE TWO SURFACES DO NOT DECLARE THE SAME
LEVELS: the inference surface carries two splits, three quality conditions and
three rungs against the declared surface's six, six-to-ten and three-to-four.
An axis cannot show the same variance share at three levels as at ten.  So the
disagreement is a comparison BETWEEN TWO DESIGNS and not a check of one
against the other, and it establishes neither as unrepresentative.

What survives is narrower and is what the manuscript should say: a first-order
index is a statement about THE LEVELS AN ANALYST DECLARED and not only about
the pair.  That qualifies the corpus claim that which axis leads is a property
of the pair; it does not refute it.  A clean test would match the two surfaces
on level counts, which is a further run and is not this round's.

    python s51_infanova.py [--draws-dir s44_weighted]

Outputs: results/s51_inference_anova.csv   one row per (pair, instrument)
         results/s51_facts.csv
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s22_anova as A  # noqa: E402
from common import RESULTS  # noqa: E402

SCALARS = ("auc", "ap", "brier_skill", "nagelkerke", "logloss_skill")
#: s22's axis names, and the columns of a designed-surface draw file they come
#: from.  `quality_level' is one axis there and two columns here, so it is
#: built rather than renamed -- a rename would silently drop the severity.
NICE = {"first_learner": "pipeline", "first_split": "split",
        "first_quality_level": "quality", "first_rung": "rung"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws-dir", default="s44_weighted",
                    help="the results/ subdirectory of designed-surface draw "
                         "files; only the point estimates (draw < 0) are read")
    a = ap.parse_args(argv)
    t0 = time.time()
    src = RESULTS / a.draws_dir
    files = sorted(src.glob("draws_*.csv.gz"))
    if not files:
        raise SystemExit("s51: no draw files in results/%s" % a.draws_dir)

    rows, skipped = [], []
    for fn in files:
        d = pd.read_csv(fn)
        d = d[(d.draw < 0) & (d.metric.isin(SCALARS))].copy()
        if d.empty:
            skipped.append(fn.name)
            continue
        d["quality_level"] = d.quality.astype(str) + "@" + d.level.astype(str)
        log, target = str(d.log.iloc[0]), str(d.target.iloc[0])
        for metric, sub in d.groupby("metric"):
            r = A.decompose(sub, A.AXES, "V", "equal")
            if r is None:
                skipped.append("%s/%s/%s" % (log, target, metric))
                continue
            first = {("first_" + k): v for k, v in r["first"].items()}
            rows.append(dict(log=log, target=target, metric=metric,
                             n_cells=r["n_cells"], var=r["var"],
                             higher=1.0 - sum(r["first"].values()), **first))
    if not rows:
        raise SystemExit("s51: nothing decomposed")
    D = pd.DataFrame(rows)
    D.to_csv(RESULTS / "s51_inference_anova.csv", index=False)

    per = D.groupby(["log", "target"])[list(NICE)].median()
    lead_inf = per.rename(columns=NICE).idxmax(axis=1)

    #  the declared surface's fold-averaged leader, for the comparison the
    #  docstring warns about.  Absent is not an error: this file's own result
    #  stands without it.
    n_pairs_cmp = n_agree = -1
    FA = RESULTS / "s42_foldavg.csv"
    if FA.exists():
        fa = pd.read_csv(FA)
        if "split_set" in fa.columns:
            fa = fa[fa.split_set == "all"]
        if "largest_first_order_axis" in fa.columns:
            lead_dec = (fa.groupby(["log", "target"]).largest_first_order_axis
                        .agg(lambda s: s.mode().iloc[0]))
            j = pd.concat([lead_dec.rename("declared"),
                           lead_inf.rename("inference")], axis=1).dropna()
            #  s22 calls the pipeline axis `learner' and the designed surface
            #  calls it `pipeline'; they are the same axis under two names, so
            #  the comparison maps one onto the other rather than counting a
            #  naming difference as a disagreement.
            def same(dec, inf):
                dec = str(dec).replace("learner", "pipeline")
                dec = dec.replace("quality_level", "quality")
                return dec == str(inf)
            n_pairs_cmp = int(len(j))
            n_agree = int(sum(same(r.declared, r.inference)
                              for r in j.itertuples()))

    facts = dict(
        draws_dir=a.draws_dir,
        n_decompositions=int(len(D)),
        n_pairs=int(per.shape[0]),
        n_instruments=int(D.metric.nunique()),
        n_cells_per_decomposition=int(D.n_cells.iloc[0]),
        n_skipped=int(len(skipped)),
        share_pipeline_median=float(per.first_learner.median()),
        share_split_median=float(per.first_split.median()),
        share_quality_median=float(per.first_quality_level.median()),
        share_rung_median=float(per.first_rung.median()),
        higher_order_median=float(
            D.groupby(["log", "target"]).higher.median().median()),
        n_pairs_leader_compared=n_pairs_cmp,
        n_pairs_leader_agrees=n_agree,
        runtime_s=round(time.time() - t0, 1),
    )
    pd.DataFrame([facts]).to_csv(RESULTS / "s51_facts.csv", index=False)

    print("=" * 78)
    print("s51  THE DECOMPOSITION ON THE INFERENCE SURFACE")
    print("=" * 78)
    print("  %d decompositions over %d pairs x %d instruments, %d cells each"
          % (facts["n_decompositions"], facts["n_pairs"],
             facts["n_instruments"], facts["n_cells_per_decomposition"]))
    if skipped:
        print("  SKIPPED: %d -- %s" % (len(skipped), "; ".join(skipped[:4])))
    print("  medians  pipeline %.3f  split %.3f  quality %.3f  rung %.3f"
          "  higher-order %.3f"
          % (facts["share_pipeline_median"], facts["share_split_median"],
             facts["share_quality_median"], facts["share_rung_median"],
             facts["higher_order_median"]))
    if n_pairs_cmp > 0:
        print("  leading axis agrees with the declared surface's on %d of %d"
              " pairs" % (n_agree, n_pairs_cmp))
        print("  -- which is a comparison BETWEEN DESIGNS: the two do not")
        print("     declare the same levels, so neither is shown")
        print("     unrepresentative by it.  See this file's docstring.")
    print("  wrote s51_inference_anova.csv, s51_facts.csv in %.1fs"
          % facts["runtime_s"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

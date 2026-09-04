"""check_bands -- THE INTERNAL CONSISTENCY OF A BANDS OUTPUT, FOR ANY PREFIX.

`verify_numbers` checks the bands the MANUSCRIPT reads.  Round twenty-seven
produces bands under two resampling schemes before either is the manuscript's,
and the interval between computing them and quoting them is exactly where an
inconsistent band would go unnoticed.  So this file checks a bands output on
its own terms, takes the prefix as an argument, and is cheap enough to run
after every `s21_bands` invocation.

THE FIVE CONDITIONS, and why each is here rather than assumed:

  1.  THE SIMULTANEOUS BAND CONTAINS THE POINTWISE INTERVAL.  A max-t band is
      a pointwise interval widened by a critical value above 1.96, so a cell
      where it is narrower is a cell where the arithmetic went wrong.

  2.  THE CONSERVATIVE EDGE CONTAINS THE SIMULTANEOUS BAND.  The conservative
      edge is the upper end of the critical value's own Monte Carlo interval,
      so it can only widen.

  3.  EVERY CRITICAL VALUE EXCEEDS THE POINTWISE 1.96.  A family of one would
      not, and a family of one is a bug rather than a result.

  4.  THE BAND EDGES REPRODUCE THE REGION FILE'S COUNTS.  This is the one that
      earns the file.  The labels are counted at the CONSERVATIVE edge, and a
      band built from one edge with labels counted from another agrees on most
      pairs and differs on a few -- which is a defect that looks like a
      rounding difference until someone checks a pair by hand.  The condition
      was written after exactly that mistake was made by hand here.

  5.  NO EDGE IS NaN.  A NaN edge resolves nothing and is counted as
      unresolved, so it is invisible in a region label.

    python check_bands.py --prefix s48w
    python check_bands.py --prefix s48w --family decision-curve

Exit status is non-zero on any failure, so it is usable as a gate.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

Z = 1.959963984540054  # the two-sided 95% normal quantile
TOL = 1e-12


def check(prefix: str, family: str) -> list[str]:
    fails: list[str] = []
    bpath = RESULTS / ("%s_bands.csv.gz" % prefix)
    rpath = RESULTS / ("%s_regions.csv" % prefix)
    if not bpath.exists():
        return ["no bands file at results/%s" % bpath.name]
    b = pd.read_csv(bpath)
    w = b[b.family == family].copy()
    if w.empty:
        return ["the bands file carries no %r family" % family]

    n_pairs = w.groupby(["log", "target"]).ngroups
    print("  %s / %s: %d cells over %d pairs"
          % (prefix, family, len(w), n_pairs))

    #  1 and 2 -- nesting
    pw_lo, pw_hi = w.centre - Z * w.se, w.centre + Z * w.se
    n1 = int(((w.sim_lo > pw_lo + TOL) | (w.sim_hi < pw_hi - TOL)).sum())
    if n1:
        fails.append("the simultaneous band is narrower than the pointwise "
                     "interval on %d cells" % n1)
    n2 = int(((w.cons_lo > w.sim_lo + TOL)
              | (w.cons_hi < w.sim_hi - TOL)).sum())
    if n2:
        fails.append("the conservative edge is narrower than the simultaneous "
                     "band on %d cells" % n2)

    #  3 -- critical values
    q = w.groupby(["log", "target"]).q.first()
    if not (q > Z).all():
        bad = q[q <= Z]
        fails.append("critical values at or below the pointwise %.2f on %d "
                     "pairs (%s)" % (Z, len(bad), ", ".join(map(str, bad.index[:3]))))
    print("     critical value: min %.3f  median %.3f  max %.3f"
          % (q.min(), q.median(), q.max()))

    #  4 -- the labels are counted at the CONSERVATIVE edge
    if rpath.exists():
        reg = pd.read_csv(rpath)
        if {"n_beneficial", "n_harmful"} <= set(reg.columns):
            reg = reg.set_index(["log", "target"])[["n_beneficial",
                                                    "n_harmful"]]
            got = (w.assign(ben=w.cons_lo > 0, harm=w.cons_hi < 0)
                   .groupby(["log", "target"])[["ben", "harm"]].sum())
            j = got.join(reg, how="inner")
            bad = j[(j.ben != j.n_beneficial) | (j.harm != j.n_harmful)]
            if len(bad):
                fails.append(
                    "the conservative band edges do not reproduce the region "
                    "file's counts on %d pairs -- %s" % (
                        len(bad),
                        "; ".join("%s/%s: band %d/%d, file %d/%d"
                                  % (i[0], i[1], r.ben, r.harm,
                                     r.n_beneficial, r.n_harmful)
                                  for i, r in bad.head(3).iterrows())))
            elif len(j) != n_pairs:
                fails.append("the region file covers %d of the bands file's "
                             "%d pairs" % (len(j), n_pairs))
    elif family == "whole-surface":
        fails.append("no region file at results/%s to check the counts against"
                     % rpath.name)

    #  5 -- NaN edges
    n5 = int(w[["sim_lo", "sim_hi", "cons_lo", "cons_hi"]].isna().sum().sum())
    if n5:
        fails.append("%d NaN band edges, which resolve nothing and are "
                     "invisible in a region label" % n5)

    #  ROUND TWENTY-EIGHT.  s21 writes BOTH estimators' edges and label sets
    #  whichever is operative, and `cons_*' is a copy of one of them.
    #
    #  6 -- THE OPERATIVE EDGES ARE ONE OF THE TWO NAMED SETS, exactly, and
    #       the one the file says they are.  A `cons_*' that matched neither
    #       would be a third band nothing names.
    #  7 -- THE EMPIRICAL BAND IS NEVER NARROWER THAN THE MULTIPLIER'S
    #       CONSERVATIVE EDGE.  Supplement S3.5 says the multiplier lies
    #       below the empirical quantile's whole order-statistic interval on
    #       every family; a cell where the empirical band is the narrower one
    #       would falsify the sentence that the level is bought with width.
    #  8 -- EACH NAMED LABEL SET IN THE REGION FILE REPRODUCES FROM ITS OWN
    #       EDGES, so the comparison the manuscript prints between the two
    #       estimators is a comparison of two things actually on disk.
    if {"mult_lo", "emp_lo", "operative"} <= set(w.columns):
        op = str(w.operative.iloc[0])
        src = {"mult": ("mult_lo", "mult_hi"), "emp": ("emp_lo", "emp_hi")}
        if op not in src:
            fails.append("the bands file names an operative estimator %r "
                         "this gate does not know" % op)
        else:
            lo, hi = src[op]
            n6 = int(((w.cons_lo - w[lo]).abs() > TOL).sum()
                     + ((w.cons_hi - w[hi]).abs() > TOL).sum())
            if n6:
                fails.append("the operative edges are not the %s edges on "
                             "%d cell edges" % (op, n6))
        print("     operative estimator: %s" % op)
        n7 = int(((w.emp_lo > w.mult_lo + TOL)
                  | (w.emp_hi < w.mult_hi - TOL)).sum())
        if n7:
            fails.append("the empirical band is narrower than the "
                         "multiplier's conservative edge on %d cells" % n7)
        if rpath.exists():
            reg = pd.read_csv(rpath)
            for tag in ("mult", "emp", "emphi"):
                cb, ch = "n_beneficial_" + tag, "n_harmful_" + tag
                if not {cb, ch} <= set(reg.columns):
                    fails.append("the region file carries no %s label set"
                                 % tag)
                    continue
                r8 = reg.set_index(["log", "target"])[[cb, ch]]
                g8 = (w.assign(ben=w[tag + "_lo"] > 0,
                               harm=w[tag + "_hi"] < 0)
                      .groupby(["log", "target"])[["ben", "harm"]].sum())
                j8 = g8.join(r8, how="inner")
                bad = j8[(j8.ben != j8[cb]) | (j8.harm != j8[ch])]
                if len(bad):
                    fails.append("the %s edges do not reproduce the region "
                                 "file's %s counts on %d pairs"
                                 % (tag, tag, len(bad)))
    else:
        print("     (a bands file older than round twenty-eight: one "
              "estimator only)")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="s48w",
                    help="the bands prefix under results/, e.g. s48w or s48m")
    ap.add_argument("--family", default="whole-surface")
    a = ap.parse_args(argv)
    print("=" * 74)
    print("check_bands  %s" % a.prefix)
    print("=" * 74)
    fails = check(a.prefix, a.family)
    for f in fails:
        print("  FAIL  %s" % f)
    print("check_bands: %d condition(s) failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

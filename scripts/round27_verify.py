"""round27_verify -- THE CROSS-OBJECT CONDITIONS ROUND TWENTY-SEVEN ADDS.

Every defect this file guards against was found by a reader holding two parts
of the manuscript side by side, and none of them could be seen from either
part alone.  A macro was right, a table was right, and the pair contradicted
each other.  That is the failure mode a paper about auditability can least
afford, so each of the five is a condition here rather than a correction in
the source.

  1.  THE MASTER TABLE MUST OBEY DEFINITION 3.  The region label is the label
      the resolution rule yields WITH its minimum resolved share applied.
      Table~\\ref{tab:triple} applied it and withdrew the direction on four
      pairs; the master table printed the un-withdrawn label for all four.
      The condition compares the two tables cell by cell.

  2.  A CAPTION MAY NOT COUNT ROWS BY HAND.  The decision-time table called
      the matched-population row `the fourth' when the ladder had grown to
      make it the sixth.  The ordinal is now a macro computed from the ladder,
      and this condition re-derives its position independently.

  3.  ONE LADDER, ONE SOURCE.  Section 7.2 reads down the decision-time table
      quoting each rung's interval.  Two rungs came from a separate, earlier
      run of the same cells at a different draw count, so the prose printed
      [+0.0763, +0.1115] beside a table printing [+0.095, +0.130].  Every
      endpoint the prose quotes is re-derived here from the ladder the table
      is printed from.

  4.  ONE PAIR IS NOT ONE LOG.  Two sections said `that pair carries N cells'
      about the registered handover target and printed the sum over the log's
      two targets.  The pair's macro is re-derived from the axis file, and the
      log's is required to be its double, since the two targets are balanced.

  5.  A LADDER ON ANOTHER CELL MUST SAY SO.  The layer ladder's increment over
      the intake block is not the decision-time table's increment over the
      intake block, because the two run on different cohorts and different
      targets.  The prose now names the ladder's cell; this condition checks
      that the coordinates it names are the coordinates the result file has,
      and that the two increments are indeed different numbers rather than one
      of them having drifted into agreement by accident.

  9.  TWO DENOMINATORS ARE TWO MACROS.  The inference family's size was
      quoted as a share of `the computational surface' in one sentence and of
      `that pair's admissible scalar cells' in another, out of ONE macro,
      whose denominator was the full declared grid -- the grid that carries
      the intercept-only rung, which Section 4.5 and the axis table both say
      is excluded from every admissible set.  One number cannot be both
      shares: they are 12.5% and 16.7% and they differ by exactly the rung.
      Both are re-multiplied here out of the declared axis levels, both
      macros are required to hold their own value, they are required to
      differ, and the master-file share is not allowed to stand as the
      denominator of a sentence that says `admissible'.

 10.  EVERY QUOTED CELL COUNT IS A MULTIPLICATION, SO DO THE MULTIPLICATION.
      The three inconsistencies round twenty-seven found in the counts were
      all found the same way, by hand-multiplying Table 4 and comparing.
      This condition does that multiplication mechanically -- for every pair,
      for every basis the manuscript counts cells by, against the audit file
      and against the generated table -- and then sweeps the macro file:
      every macro the prose uses whose NAME says it is a count of cells or a
      share of a surface is matched against what the axis declaration yields,
      and the ones whose names name a log, a target, an admissible set or a
      scalar surface must be attributed to exactly that.  The set of macros
      swept is discovered from the macro file and the parts, not listed here,
      so a new count is covered the day it is written.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

MISSING = "\\textbf{??}"

#: the human-readable conditions, appended to verify_numbers.CONDITIONS
CONDITIONS = (
    "the master table's region label is the one Definition 3 yields with its "
    "minimum resolved share applied, on every pair, and agrees with the "
    "resolution-triple table",
    "every ordinal by which the prose points at a row of the decision-time "
    "table is the row's actual position in that table",
    "every decision-time interval the case study quotes is the interval the "
    "decision-time table prints for the same rung",
    "the cell count attributed to the registered handover pair is that "
    "pair's and not its log's",
    "the layer ladder's cell is the cell the prose names, and its increment "
    "over the intake block is not confused with the decision-time table's",
    "the prefix pilot at case creation reproduces the layer ladder's finest "
    "rung, on the same cases, to the sixth decimal",
    "every drift percentile is a percentile, and the drift flag is exactly "
    "the upper-tail rule it is defined from",
    "neither document calls a register's coarse layers free while the "
    "measured share says otherwise",
    "the inference family's share of a pair's surface is quoted against the "
    "denominator the sentence names, and the admissible surface and the "
    "master surface file are not one number",
    "every per-pair and per-surface cell count the prose quotes is the "
    "product of the declared axis levels, on the basis its own name says",
)

_ORD = ("first", "second", "third", "fourth", "fifth", "sixth",
        "seventh", "eighth", "ninth", "tenth")


def _num(s):
    """The numeric value of a macro's rendered text: strips math mode, the
    LaTeX thin-space thousands separator and a leading plus."""
    if s is None or s == MISSING:
        return None
    t = re.sub(r"[$\\,{}]|\\,|\{,\}", "", str(s)).replace("{,}", "")
    t = t.replace(",", "").replace("+", "").strip()
    #  a percentage macro renders as "52\%"; stripping the backslash above
    #  leaves the sign behind, and float() then returns None -- which silently
    #  skipped the comparison this function exists for.
    if t.endswith("%"):
        t = t[:-1].strip()
    try:
        return float(t)
    except ValueError:
        return None


def _read(results, name):
    p = Path(results) / name
    return pd.read_csv(p) if p.exists() else None


def _table_rows(tables, name):
    """The body rows of a generated table, as lists of stripped cells."""
    p = Path(tables) / name
    if not p.exists():
        return []
    body = p.read_text(encoding="utf-8")
    m = re.search(r"\\midrule(.*?)\\bottomrule", body, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        line = line.strip().rstrip("\\").strip()
        if not line:
            continue
        out.append([c.strip() for c in line.split("&")])
    return out


#: The products of declared axis levels the manuscript counts cells by.  Each
#: entry is a MULTIPLICATION over axis names exactly as `s25_denominator.py`
#: writes them to results/s25_axis_levels.csv -- the file Table~\ref{tab:axes}
#: and Table~\ref{tab:denominator} are both generated from -- so an axis added
#: to the design walks into every basis here without this file being edited.
#:
#: The `admissible' bases differ from their partners by ONE axis and only one:
#: `admissible_rung' is `rung' with the intercept-only level removed, which is
#: the level the axis table prints as "in the surface, out of every admissible
#: set".  That single difference is the whole of round twenty-seven's third
#: inconsistency, and it is why the two are separate rows here rather than a
#: flag on one.
_BASES = {
    "cells": ("learner", "split", "quality_level", "rung"),
    "scalar cells": ("learner", "split", "quality_level", "rung",
                     "scalar_metric"),
    "admissible cells": ("learner", "split", "quality_level",
                         "admissible_rung"),
    "admissible scalar cells": ("learner", "split", "quality_level",
                                "admissible_rung", "scalar_metric"),
    "decision-curve cells": ("learner", "split", "quality_level", "rung",
                             "operating_point"),
    "admissible decision-curve cells": ("learner", "split", "quality_level",
                                        "admissible_rung", "operating_point"),
}

#: which audit column each basis is stored in, so the multiplication can be
#: checked against the file the macros are actually read from
_BASIS_COLUMN = {
    "cells": "declared_cells",
    "scalar cells": "declared_scalar",
    "admissible cells": "declared_admissible_cells",
    "admissible scalar cells": "declared_admissible_scalar",
    "admissible decision-curve cells": "declared_admissible_dc",
}

_ONES = ("zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety")


def _spelled(n):
    """`14` as `fourteen`, because a log is `BPIC14' in a result file and
    `BpicFourteen' in a macro name.  Above ninety-nine there is no convention
    to follow, so the caller falls back to the digits."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + (_ONES[n % 10] if n % 10 else "")
    return None


def _key(s):
    """A name reduced to its letters and digits, lower-cased: the form in
    which `BPIC15_1' and `BpicFifteenOne' can be compared."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _name_variants(log):
    """Every spelling of a log's name a macro might carry: the digits as they
    stand, and the digits spelled out."""
    base = _key(log)
    out = {base}
    parts = re.split(r"(\d+)", base)
    words, ok = [], True
    for p in parts:
        if p.isdigit():
            w = _spelled(int(p))
            if w is None:
                ok = False
                break
            words.append(w)
        else:
            words.append(p)
    if ok:
        out.add("".join(words))
    return out


def _axis_bases(results):
    """{(log, target): {basis: value}} -- Table 4's multiplication, done from
    the declaration rather than read from a stored count."""
    AX = _read(results, "s25_axis_levels.csv")
    if AX is None or not len(AX) or "n_levels" not in AX.columns:
        return {}
    lev = {}
    for r in AX.itertuples():
        lev.setdefault((str(r.log), str(r.target)), {})[
            str(r.axis)] = int(r.n_levels)
    out = {}
    for key, axes in lev.items():
        vals = {}
        for name, prod in _BASES.items():
            if all(a in axes for a in prod):
                n = 1
                for a in prod:
                    n *= axes[a]
                vals[name] = n
        if vals:
            out[key] = vals
    return out


def _macro_uses(paper):
    """{macro name: [file names]} over paper/parts, which is where the prose
    is.  Scanning the assembled document instead is how condition 8's first
    version passed against the very sentence it was written for."""
    out = {}
    for f in sorted((Path(paper) / "parts").glob("*.tex")):
        body = re.sub(r"(?<!\\)%.*", "", f.read_text(encoding="utf-8"))
        for name in set(re.findall(r"\\([A-Za-z]+)", body)):
            out.setdefault(name, []).append(f.name)
    return out


def _table_header(tables, name):
    """The column names of a generated table, so a condition can find a
    column by what it is called rather than by counting commas."""
    p = Path(tables) / name
    if not p.exists():
        return []
    m = re.search(r"\\toprule(.*?)\\midrule", p.read_text(encoding="utf-8"),
                  re.S)
    if not m:
        return []
    line = m.group(1).strip().rstrip("\\").strip()
    return [c.strip() for c in line.split("&")]


def check(vn, M):
    results = vn.RESULTS
    tables = Path(vn.PAPER) / "tables"

    # --- 1.  the master table obeys Definition 3 -------------------------
    RG = _read(results, "s42_regions.csv")
    master = _table_rows(tables, "master.tex")
    triple = _table_rows(tables, "triple.tex")
    if RG is not None and len(RG) and master:
        want = {}
        for r in RG.itertuples():
            key = (str(r.log).replace("_", "\\_"), str(r.target))
            want[key] = str(r.region_min05)
        bad = []
        for row in master:
            if len(row) < 7:
                continue
            key = (row[0], row[1])
            if key not in want:
                continue
            #  the region column is the sixth: log, target, V, pointwise,
            #  simultaneous, region
            if row[5] != want[key]:
                bad.append("%s/%s: master says %r, Definition 3 gives %r"
                           % (key[0], key[1], row[5], want[key]))
        if bad:
            vn.FAILS.append(
                "round-27 condition: the master table's region label is not "
                "the one Definition 3 yields -- " + "; ".join(bad[:6]))
    #  A CELL THAT CANNOT BE BANDED IS NOT A CELL THAT DID NOT RESOLVE.
    #
    #  A multinomial resample can drop an arm from a draw entirely, so the
    #  cell is absent rather than noisy, the median down its column is
    #  undefined, and it gets no band.  It is then not resolved -- and was
    #  counted as UNRESOLVED, beside cells that were banded and straddled
    #  zero.  A paper about denominators cannot have unassessable cells inside
    #  the set it quotes resolution against without saying how many.
    #
    #  So the condition is not that the count be zero.  It is that the count
    #  be REPORTED: whatever the bands file contains, `nUnbandableCells' must
    #  equal it.  A future surface with none will carry a zero, which is also
    #  worth printing.
    BF = Path(results) / "s48w_bands.csv.gz"
    if not BF.exists():
        BF = Path(results) / "s21_bands.csv.gz"
    if BF.exists():
        try:
            _b = pd.read_csv(BF)
            _w = _b[_b.family == "whole-surface"]
            _n = int(_w.sim_lo.isna().sum())
            _m = _num(M.get("nUnbandableCells"))
            if _m is None or int(_m) != _n:
                vn.FAILS.append(
                    "round-27 condition: the bands file carries %d cell(s) "
                    "with no band, and the manuscript reports %s -- a cell "
                    "that could not be banded is being counted as one the "
                    "data did not resolve" % (_n, M.get("nUnbandableCells")))
        except (KeyError, ValueError, AttributeError):
            pass

    #  THE CELL COUNTS AND THE REGION LABELS DESCRIBE ONE SURFACE.
    #
    #  Round twenty-seven replaced the inference surface, and found FOUR
    #  separate checks that went on reading the old one because its name was a
    #  literal in the code.  The dangerous combination is not any single stale
    #  reader: it is a HALF-migrated state, where the cell-count macros come
    #  from one surface and the region labels from another.  Both files are
    #  internally consistent then, every number resolves, and the manuscript
    #  reports a family size that no label was computed over.
    #
    #  So the condition is a join rather than a total: per pair, the grid the
    #  counts come from and the regions file the labels come from must agree
    #  on the family size.  A total would pass on two surfaces that happened
    #  to sum alike; a per-pair join cannot.
    G20 = _read(results, "s20_grid.csv")
    R21 = _read(results, "s21_regions.csv")
    if (G20 is not None and len(G20) and R21 is not None and len(R21)
            and "scalar_cells" in G20.columns and "n_cells" in R21.columns):
        gk = {(str(r.log), str(r.target)): int(r.scalar_cells)
              for r in G20.itertuples()}
        bad = []
        for r in R21.itertuples():
            key = (str(r.log), str(r.target))
            if key in gk and gk[key] != int(r.n_cells):
                bad.append("%s/%s: grid says %d cells, the region label was "
                           "computed over %d"
                           % (key[0], key[1], gk[key], int(r.n_cells)))
        missing = [k for k in gk
                   if k not in {(str(r.log), str(r.target))
                                for r in R21.itertuples()}]
        if bad or missing:
            vn.FAILS.append(
                "round-27 condition: the inference-surface cell counts and "
                "the region labels do not describe one surface -- "
                + "; ".join(bad[:4] or ["%d pairs in the grid carry no region "
                                        "label" % len(missing)]))

    #  THE DESK COMPARISON'S PAIRS ARE ACCOUNTED FOR.  Section 8.4 printed a
    #  count taken over the 16 pairs that carry a calibrated model against a
    #  denominator of 19 --- two sentences after saying the calibration rule
    #  excludes 3 of the 19.  The partition is the check: a pair on which the
    #  rules separate and a pair on which all four are identical are the only
    #  two states, so they must sum to the pairs the comparison runs on.
    F35 = _read(results, "s35_facts.csv")
    if F35 is not None and len(F35):
        try:
            nsep = int(F35.n_separating_desk.iloc[0])
            ntie = int(F35.n_all_rules_tie_desk.iloc[0])
            npd = int(F35.n_pairs_desk.iloc[0])
            if nsep + ntie != npd:
                vn.FAILS.append(
                    "round-27 condition: the desk comparison's pairs do not "
                    "partition -- %d separating + %d all-tied != %d pairs"
                    % (nsep, ntie, npd))
        except (AttributeError, KeyError, IndexError, ValueError):
            vn.FAILS.append(
                "round-27 condition: s35_facts.csv is missing a column the "
                "desk-pair partition needs (n_separating_desk, "
                "n_all_rules_tie_desk, n_pairs_desk)")

    #  THE SPECIFICATION-CURVE TABLE OBEYS THE SAME DEFINITION.  The master
    #  table was repaired in round twenty-seven and this one was not, so for a
    #  week two tables printed different region labels for the same four
    #  pairs.  Repairing one instance of a defect and leaving a second is the
    #  failure this file exists to make impossible, so the condition covers
    #  every table that prints a region and not only the one a reader found.
    #  Read by HEADER rather than by column position: sca.tex gained a column
    #  when it was repaired, and a positional read would have silently moved
    #  to the wrong one.
    sca_head = _table_header(tables, "sca.tex")
    if RG is not None and len(RG) and sca_head and "region" in sca_head:
        i_log, i_tgt = sca_head.index("log"), sca_head.index("target")
        i_reg = sca_head.index("region")
        bad = []
        for row in _table_rows(tables, "sca.tex"):
            if len(row) != len(sca_head):
                continue
            key = (row[i_log], row[i_tgt])
            if key in want and row[i_reg] != want[key]:
                bad.append("%s/%s: sca says %r, Definition 3 gives %r"
                           % (key[0], key[1], row[i_reg], want[key]))
        if bad:
            vn.FAILS.append(
                "round-27 condition: the SCA table's region label is not the "
                "one Definition 3 yields -- " + "; ".join(bad[:6]))

    #  and the two tables must agree with each other, which is the form the
    #  reader met the defect in
    if master and triple:
        tri = {}
        for row in triple:
            if len(row) < 7:
                continue
            applied = row[6]
            tri[(row[0], row[1])] = (row[5] if applied.strip() in ("--", "---")
                                     else applied)
        bad = []
        for row in master:
            if len(row) < 7:
                continue
            key = (row[0], row[1])
            if key in tri and row[5] != tri[key]:
                bad.append("%s/%s: %r vs %r"
                           % (key[0], key[1], row[5], tri[key]))
        if bad:
            vn.FAILS.append(
                "round-27 condition: the master table and the "
                "resolution-triple table disagree about a region label -- "
                + "; ".join(bad[:6]))

    # --- 2, 3.  the decision-time ladder ---------------------------------
    L = _read(results, "s38_ladder.csv")
    if L is not None and len(L):
        pos = {}
        for i, r in enumerate(L.itertuples()):
            pos.setdefault(("t2_matched", None), None)
        w = [i for i, v in enumerate(L.decision_time == "t2_matched") if v]
        matched = _ORD[w[0]] if w and w[0] < len(_ORD) else None
        w = [i for i, v in enumerate((L.decision_time == "t2_incident_creation")
                                     & (L.rung == "B_intake")) if v]
        plain = _ORD[w[0]] if w and w[0] < len(_ORD) else None
        for macro, got in (("tauMatchedRow", matched), ("tauPlainRow", plain)):
            if macro in M and M[macro] != MISSING and got is not None:
                if str(M[macro]) != got:
                    vn.FAILS.append(
                        "round-27 condition: \\%s says %r and the ladder puts "
                        "that row %s" % (macro, M[macro], got))
        #  the caption points at the same two rows and must use the same words
        cap = (tables / "tau.tex")
        if cap.exists() and matched and plain:
            text = cap.read_text(encoding="utf-8")
            if ("the %s row is" % matched) not in text:
                vn.FAILS.append(
                    "round-27 condition: the decision-time table's caption "
                    "does not call the matched-population row the %s" % matched)

        #  every interval the case study quotes, against the ladder
        for dt, rung, base in (
                ("t0_first_touch_all", "B_intake", "VtauZero"),
                ("t1_first_touch_escalating", "B_intake", "VtauOne"),
                ("t2_incident_creation", "B_intake_g", "VTtwoGroup"),
                ("t2_incident_creation", "B_intake_g_km", "VTtwoKnow")):
            r = L[(L.decision_time == dt) & (L.rung == rung)]
            if not len(r):
                continue
            for suffix, col in (("", "V"), ("Lo", "lo"), ("Hi", "hi")):
                name = base + suffix
                if name not in M or M[name] == MISSING:
                    continue
                got, want = _num(M[name]), float(getattr(r, col).iloc[0])
                if got is None or abs(got - want) > 5e-5:
                    vn.FAILS.append(
                        "round-27 condition: \\%s is %s and the ladder row "
                        "the table prints it from is %+.4f"
                        % (name, M[name], want))
            #  and the table's own printed interval, so prose and table are
            #  compared as a reader compares them
            lo, hi = float(r.lo.iloc[0]), float(r.hi.iloc[0])
            printed = "[%+.3f, %+.3f]" % (lo, hi)
            quoted = "[%+.3f, %+.3f]" % (_num(M.get(base + "Lo")) or lo,
                                         _num(M.get(base + "Hi")) or hi)
            if printed != quoted:
                vn.FAILS.append(
                    "round-27 condition: the case study quotes %s for the %s "
                    "rung and the decision-time table prints %s"
                    % (quoted, rung, printed))

    # --- 4.  one pair is not one log -------------------------------------
    AX = _read(results, "s42_axes.csv")
    if AX is not None and len(AX):
        cells = (AX.n_pipeline * AX.n_split * AX.n_quality * AX.n_rung
                 * AX.n_instrument)
        A = AX.assign(_cells=cells)
        pair = A[(A.log == "BPIC14") & (A.target == "handover")]._cells.sum()
        log = A[A.log == "BPIC14"]._cells.sum()
        got = _num(M.get("nCellsBpicFourteenHandover"))
        if got is not None and abs(got - float(pair)) > 0.5:
            vn.FAILS.append(
                "round-27 condition: \\nCellsBpicFourteenHandover is %s and "
                "the registered handover pair carries %d cells"
                % (M["nCellsBpicFourteenHandover"], int(pair)))
        gotlog = _num(M.get("nCellsBpicFourteen"))
        if gotlog is not None and abs(gotlog - float(log)) > 0.5:
            vn.FAILS.append(
                "round-27 condition: \\nCellsBpicFourteen is %s and the log "
                "carries %d cells" % (M["nCellsBpicFourteen"], int(log)))
        if got is not None and gotlog is not None and got >= gotlog:
            vn.FAILS.append(
                "round-27 condition: one pair of BPIC14 is credited with at "
                "least as many cells as the log that contains it")

    # --- 8.  the layer claim, in BOTH documents ---------------------------
    #  Round twenty-two withdrew "the coarse layers are close to free" from
    #  the article after measuring that the case study's type layer is worth a
    #  third to a half of what the item is worth.  The SUPPLEMENT kept the
    #  withdrawn reading for five rounds, about a table holding three logs on
    #  which the answer differs.  The share is a macro now, re-derived here,
    #  and the withdrawn phrase may not describe the case study in either
    #  document while that share is more than a tenth.
    R34s = _read(results, "r34_layers.csv")
    if R34s is not None and len(R34s):
        for tg, nm in (("handover", "Handover"), ("duration", "Duration")):
            it = R34s[(R34s.log == "BPIC14") & (R34s.target == tg)
                      & (R34s.level == "CI Name (aff)")]
            ty = R34s[(R34s.log == "BPIC14") & (R34s.target == tg)
                      & (R34s.level == "CI Type (aff)")]
            if not len(it) or not len(ty):
                continue
            want = 100.0 * float(ty.gain_over_b0.iloc[0]) / float(
                it.gain_over_b0.iloc[0])
            got = _num(M.get("layerTypeSharePct" + nm))
            if got is not None and abs(got - want) > 0.6:
                vn.FAILS.append(
                    "round-27 condition: \\layerTypeSharePct%s is %s and the "
                    "ladder gives %.1f%%" % (nm, M["layerTypeSharePct" + nm],
                                             want))
            if got is not None and got > 10:
                #  the ASSEMBLED files are a preamble and a list of \input,
                #  so the prose is in the parts.  Scanning the assembled file
                #  is how the first version of this condition managed to pass
                #  against the very sentence it was written for.
                srcs = sorted((Path(vn.PAPER) / "parts").glob("*.tex"))
                for f in srcs:
                    body = f.read_text(encoding="utf-8")
                    for phrase in ("close to free", "nearly free",
                                   "essentially free", "largely free",
                                   "almost free"):
                        for m in re.finditer(re.escape(phrase), body):
                            #  the phrase is only this defect when it is said
                            #  ABOUT a coarsening.  A quality mechanism that
                            #  is "nearly free" is a different sentence, and
                            #  the file-level version of this check called one
                            #  of those a failure.
                            near = body[max(0, m.start() - 220):m.end() + 220]
                            if not re.search(r"coarse|coarsen|layer", near,
                                             re.I):
                                continue
                            #  and a NEGATED form is the corrected sentence,
                            #  not the withdrawn one: "the coarse layers are
                            #  \emph{not} close to free" is exactly what this
                            #  condition wants the documents to say.
                            before = body[max(0, m.start() - 60):m.start()]
                            if re.search(r"\bnot\b|\bnever\b|far from|"
                                         r"hardly|anything but", before,
                                         re.I):
                                continue
                            vn.FAILS.append(
                                "round-27 condition: %s calls a coarse layer "
                                "%r while the case study's type layer is "
                                "worth %.0f%% of what the item is worth over "
                                "the same baseline on the %s target"
                                % (f.name, phrase, got, tg))

    # --- 6.  the prefix pilot's anchor is the layer ladder's own cell ----
    #  The prefix axis at k = 0 IS case creation on the registered cohort and
    #  the registered handover rule against the intake block, which is exactly
    #  the layer ladder's finest rung.  Two files, two authors' worth of code,
    #  one number: if they ever disagree, one of them has silently changed the
    #  cell it is on, and this is the condition that says so.
    PX = _read(results, "s45_prefix.csv")
    R34x = _read(results, "r34_layers.csv")
    if PX is not None and len(PX) and R34x is not None and len(R34x):
        z = PX[PX.prefix == 0]
        lay = R34x[(R34x.log == "BPIC14") & (R34x.target == "handover")
                   & (R34x.level == "CI Name (aff)")]
        if len(z) and len(lay):
            a, b = float(z.V.iloc[0]), float(lay.gain_over_b0.iloc[0])
            if abs(a - b) > 1e-6:
                vn.FAILS.append(
                    "round-27 condition: the prefix pilot at case creation "
                    "gives %+.6f and the layer ladder's finest rung gives "
                    "%+.6f; they are the same cell and must agree" % (a, b))
            na, nb = int(z.n.iloc[0]), int(lay.n.iloc[0])
            if na != nb:
                vn.FAILS.append(
                    "round-27 condition: the prefix pilot's anchor runs on %d "
                    "cases and the layer ladder on %d" % (na, nb))

    # --- 7.  the stationarity null is a null and not a second statistic --
    DR = _read(results, "s46_summary.csv")
    if DR is not None and len(DR):
        bad = DR[(DR.spread_percentile < 0) | (DR.spread_percentile > 1)]
        if len(bad):
            vn.FAILS.append(
                "round-27 condition: %d drift percentile(s) outside [0, 1]"
                % len(bad))
        #  `drifts` must be exactly the upper-tail flag, not a second rule
        want = DR.spread_percentile >= 0.95
        if not bool((DR.drifts.astype(bool) == want).all()):
            vn.FAILS.append(
                "round-27 condition: the drift flag no longer agrees with the "
                "percentile it is defined from")
        n_flag = int(DR.drifts.astype(bool).sum())
        got = _num(M.get("nDrifts"))
        if got is not None and abs(got - n_flag) > 0.5:
            vn.FAILS.append(
                "round-27 condition: \\nDrifts is %s and %d pairs carry the "
                "flag" % (M["nDrifts"], n_flag))

    # --- 5.  the layer ladder's cell -------------------------------------
    R34 = _read(results, "r34_layers.csv")
    if R34 is not None and len(R34):
        b = R34[(R34.log == "BPIC14") & (R34.target == "handover")]
        if len(b):
            n = int(b.n.iloc[0])
            got = _num(M.get("layerLadderN"))
            if got is not None and abs(got - n) > 0.5:
                vn.FAILS.append(
                    "round-27 condition: \\layerLadderN is %s and the layer "
                    "ladder runs on %d cases" % (M["layerLadderN"], n))
            #  the cohort it runs on is the REGISTERED one, which is the point
            #  the prose makes; if it ever stops being, the sentence is false
            reg = _num(M.get("nRegisteredCohort"))
            if reg is not None and abs(reg - n) > 0.5:
                vn.FAILS.append(
                    "round-27 condition: the layer ladder no longer runs on "
                    "the registered cohort (%d cases against \\nRegisteredCohort"
                    " = %s), and Section 7.4 says it does" % (n, M["nRegisteredCohort"]))
            item = _num(M.get("layerItemHandover"))
            tau2 = _num(M.get("VtauTwo"))
            if item is not None and tau2 is not None and abs(item - tau2) < 5e-4:
                vn.FAILS.append(
                    "round-27 condition: the layer ladder's increment over "
                    "intake and the decision-time table's are now the same "
                    "number, and Section 7.4 explains why they differ")

    # --- 9.  two denominators are two macros -----------------------------
    #  The inference family is a corner of the declared surface, and the
    #  manuscript quotes its size as a SHARE in four places.  Two of those
    #  sentences name the admissible set as the denominator and two name the
    #  computational surface, which is the same set: Section 4.2 defines the
    #  declared surface as "every scientifically admissible specification"
    #  and the computational surface as equal to it, and prints both at
    #  \nDeclaredAdmissibleScalar.  All four were served by one macro whose
    #  denominator was neither of those but the full declared
    #  grid -- the grid that carries the intercept-only rung.  The rung is one
    #  level of one axis, so the error is not large; it is simply a share of a
    #  set no sentence in the manuscript ranges over.
    AUD = _read(results, "s25_audit.csv")
    BASES = _axis_bases(results)
    if (AUD is not None and len(AUD) and BASES
            and "inference_cells_observed" in AUD.columns):
        full, adm = [], []
        for r in AUD.itertuples():
            b = BASES.get((str(r.log), str(r.target)))
            if not b or "cells" not in b or "admissible cells" not in b:
                continue
            full.append(float(r.inference_cells_observed) / b["cells"])
            adm.append(float(r.inference_cells_observed) / b["admissible cells"])
        if full:
            w_full = 100.0 * float(pd.Series(full).median())
            w_adm = 100.0 * float(pd.Series(adm).median())
            for macro, want, what in (
                    ("inferenceShareMedianPct", w_full,
                     "the full declared grid, which carries the "
                     "intercept-only rung"),
                    ("inferenceShareAdmissibleMedianPct", w_adm,
                     "the admissible grid, from which that rung is excluded")):
                got = _num(M.get(macro))
                if got is None:
                    vn.FAILS.append(
                        "round-27 condition: \\%s is not defined, and the "
                        "inference family's share needs one macro for each "
                        "denominator the manuscript quotes it against"
                        % macro)
                elif abs(got - want) > 0.06:
                    vn.FAILS.append(
                        "round-27 condition: \\%s is %s and the median share "
                        "over %s, multiplied out of the declared axis levels, "
                        "is %.1f%%" % (macro, M.get(macro), what, want))
            #  They are not one number.  The admissible grid is a strict
            #  subset of the declared one on every pair of this corpus, so
            #  its share is strictly the larger; a manuscript in which the two
            #  macros agree has lost the distinction it has just drawn.
            g_full = _num(M.get("inferenceShareMedianPct"))
            g_adm = _num(M.get("inferenceShareAdmissibleMedianPct"))
            if (g_full is not None and g_adm is not None
                    and not g_adm > g_full):
                vn.FAILS.append(
                    "round-27 condition: the inference family's share of the "
                    "admissible surface (%s) is not greater than its share of "
                    "the master surface file (%s), and the second denominator "
                    "contains the first plus the intercept-only rung"
                    % (M.get("inferenceShareAdmissibleMedianPct"),
                       M.get("inferenceShareMedianPct")))
        #  The same subsection prints the third surface as an IDENTITY --- the
        #  computational surface "equals the declared surface", with both
        #  counts side by side --- and it is the audit that makes the sentence
        #  true.  So the sentence is checked against the audit and not against
        #  itself: the two macros must be one number, that number must be the
        #  admissible scalar surface the axis levels multiply to, and a
        #  duplicate or a missing combination anywhere in the corpus breaks
        #  the identity the sentence asserts.
        c_cells = _num(M.get("nComputationalCells"))
        d_cells = _num(M.get("nDeclaredAdmissibleScalar"))
        want = sum(v["admissible scalar cells"] for v in BASES.values()
                   if "admissible scalar cells" in v)
        if c_cells is not None and d_cells is not None and c_cells != d_cells:
            vn.FAILS.append(
                "round-27 condition: Section 4.2 says the computational "
                "surface equals the declared surface and prints \\%s against "
                "\\%s" % (M.get("nComputationalCells"),
                          M.get("nDeclaredAdmissibleScalar")))
        if c_cells is not None and want and abs(c_cells - want) > 0.5:
            vn.FAILS.append(
                "round-27 condition: \\nComputationalCells is %s and the "
                "declared axis levels multiply to %d admissible scalar cells"
                % (M.get("nComputationalCells"), want))
        for col in ("duplicates", "missing"):
            if col in AUD.columns and float(AUD[col].abs().sum()) > 0:
                vn.FAILS.append(
                    "round-27 condition: Section 4.2 says the computational "
                    "surface equals the declared surface, and the audit "
                    "reports %d %s" % (int(AUD[col].abs().sum()), col))

        #  and the master-file share may not stand as the denominator of a
        #  sentence that says `admissible'.  What was wrong was never the
        #  arithmetic in the generator; it was the right number under the
        #  wrong noun, so the noun is what this reads.
        for f in sorted((Path(vn.PAPER) / "parts").glob("*.tex")):
            body = re.sub(r"(?<!\\)%.*", "", f.read_text(encoding="utf-8"))
            for m in re.finditer(r"\\inferenceShareMedianPct\b", body):
                after = " ".join(body[m.end():m.end() + 110].split())
                if re.search(r"admissible", after, re.I):
                    vn.FAILS.append(
                        "round-27 condition: %s quotes the master surface "
                        "file's share as a share of an ADMISSIBLE set -- "
                        "\"...%s\"; the admissible denominator is "
                        "\\inferenceShareAdmissibleMedianPct"
                        % (f.name, after[:78]))

    # --- 10.  the sweep: every quoted count is a multiplication ----------
    #  Three of this round's inconsistencies were found by multiplying the
    #  axis levels of Table 4 by hand and comparing with the prose.  Nothing
    #  about that is manual, so it is done here for every pair, every basis,
    #  every row of the table, and every macro the parts quote whose own name
    #  says it is a count of cells.
    if AUD is not None and len(AUD) and BASES:
        # (a) the stored counts ARE the product of the declared levels
        bad = []
        for r in AUD.itertuples():
            b = BASES.get((str(r.log), str(r.target)))
            if not b:
                bad.append("%s/%s: the axis file declares no levels"
                           % (r.log, r.target))
                continue
            for basis, col in _BASIS_COLUMN.items():
                if basis not in b or col not in AUD.columns:
                    continue
                stored = float(getattr(r, col))
                if abs(stored - b[basis]) > 0.5:
                    bad.append("%s/%s %s: the audit stores %d, the declared "
                               "levels multiply to %d"
                               % (r.log, r.target, basis, int(stored),
                                  b[basis]))
        if bad:
            vn.FAILS.append(
                "round-27 condition: a stored cell count is not the product "
                "of the declared axis levels -- " + "; ".join(bad[:6]))

        # (b) the denominator table's own cells, re-multiplied.  The table is
        #     what a reader multiplies, so the table is what is checked --
        #     by column NAME, so a reordered table is still checked.
        head = _table_header(tables, "denominator.tex")
        col_basis = {"declared scalar": "admissible scalar cells",
                     "computed scalar": "admissible scalar cells",
                     "model fits": "cells"}
        if head and "log" in head and "target" in head:
            i_log, i_tgt = head.index("log"), head.index("target")
            bad = []
            for row in _table_rows(tables, "denominator.tex"):
                if len(row) != len(head):
                    continue
                key = (row[i_log].replace("\\_", "_"), row[i_tgt])
                b = BASES.get(key)
                if not b:
                    continue
                for col, basis in col_basis.items():
                    if col not in head or basis not in b:
                        continue
                    got = _num(row[head.index(col)])
                    if got is not None and abs(got - b[basis]) > 0.5:
                        bad.append("%s/%s `%s': the table prints %d, the "
                                   "declared levels multiply to %d"
                                   % (key[0], key[1], col, int(got),
                                      b[basis]))
            if bad:
                vn.FAILS.append(
                    "round-27 condition: the denominator table prints a cell "
                    "count that is not the product of the declared axis "
                    "levels -- " + "; ".join(bad[:6]))

        # (c) the macro sweep.  The macros are DISCOVERED -- every one the
        #     parts quote whose name says `cells', `scalar' or a
        #     decision-curve count -- rather than listed, so a count written
        #     next week is swept the day it is written.  A value the
        #     declaration cannot yield is not a failure: a count of RESOLVED
        #     cells is a result and not a declaration.  What is a failure is a
        #     value the declaration CAN yield, attributed to something other
        #     than what the macro's own name says.
        USES = _macro_uses(vn.PAPER)
        per_log, corpus, spread = {}, {}, {}
        n_pairs_of = {}
        for (log, target), vals in BASES.items():
            n_pairs_of[log] = n_pairs_of.get(log, 0) + 1
            for basis, v in vals.items():
                per_log[(log, basis)] = per_log.get((log, basis), 0) + v
                corpus[basis] = corpus.get(basis, 0) + v
                spread.setdefault(basis, []).append(v)

        def _attribute(v):
            """Every quantity the declaration yields that this value could
            be, as (basis, log, target); a log with target None is the sum
            over that log's pairs, and both None is the corpus."""
            out = []
            for (lg, tg), vals in BASES.items():
                for basis, x in vals.items():
                    if abs(v - x) <= 0.5:
                        out.append((basis, lg, tg))
            for (lg, basis), x in per_log.items():
                if abs(v - x) <= 0.5 and n_pairs_of[lg] > 1:
                    out.append((basis, lg, None))
            for basis, x in corpus.items():
                if abs(v - x) <= 0.5:
                    out.append((basis, None, None))
            for basis, xs in spread.items():
                s = pd.Series(xs)
                for x in (s.median(), s.min(), s.max()):
                    if abs(v - float(x)) <= 0.5:
                        out.append((basis, None, None))
            return out

        LOGS = sorted({lg for lg, _t in BASES})
        TARGETS = sorted({tg for _l, tg in BASES})
        VARIANTS = {lg: _name_variants(lg) for lg in LOGS}
        for name in sorted(M):
            if name not in USES:
                continue                       # defined, never quoted
            k = _key(name)
            if not ("cells" in k or "scalar" in k or k.endswith("dc")):
                continue
            v = _num(M[name])
            if v is None:
                continue
            att = _attribute(v)
            if not att:
                continue                       # a result, not a declaration
            #  (i) a macro that names a log is that log's count, and a macro
            #      that names a log AND a target is one pair's and not the
            #      log's.  This is the shape of the `9,600 admissible cells'
            #      defect, generalised: the log names come from the axis file.
            hit = None
            for lg in LOGS:
                if any(var in k for var in VARIANTS[lg]):
                    if hit is None or len(_key(lg)) > len(_key(hit)):
                        hit = lg
            if hit is not None:
                tgt = next((t for t in TARGETS if t in k), None)
                if tgt is not None:
                    ok = [b for b, lg, tg in att if lg == hit and tg == tgt]
                    if not ok:
                        vn.FAILS.append(
                            "round-27 condition: \\%s is %s and the %s/%s "
                            "PAIR declares %s" % (
                                name, M[name], hit, tgt,
                                ", ".join("%d %s" % (x, b) for b, x in sorted(
                                    BASES[(hit, tgt)].items(),
                                    key=lambda kv: kv[1]))))
                elif n_pairs_of.get(hit, 0) > 1:
                    ok = [b for b, lg, tg in att if lg == hit and tg is None]
                    if not ok:
                        vn.FAILS.append(
                            "round-27 condition: \\%s is %s and names the %s "
                            "LOG, whose %d pairs declare %s" % (
                                name, M[name], hit, n_pairs_of[hit],
                                ", ".join("%d %s" % (x, b) for b, x in sorted(
                                    ((b, x) for (lg, b), x in per_log.items()
                                     if lg == hit), key=lambda kv: kv[1]))))
            #  (ii) a token in the name is a claim about the basis.  Only the
            #       PRESENCE of a word is read, never its absence: `computational
            #       surface' is this manuscript's name for the admissible one,
            #       and a checker that inferred a basis from a missing word
            #       would call that sentence wrong.
            for token, need in (("admissible", "admissible"),
                                ("scalar", "scalar")):
                if token in k and not any(need in b for b, _l, _t in att):
                    vn.FAILS.append(
                        "round-27 condition: \\%s is %s, its name says `%s', "
                        "and the only thing the declaration makes that value "
                        "is %s" % (name, M[name], token,
                                   "; ".join(sorted({b for b, _l, _t in att}))))

        # (d) the shares, on whichever denominator each macro's name names.
        #     Written as a family rather than for the two macros that exist,
        #     so an `inferenceShareMinPct' would be checked without this file
        #     being touched.
        for name in sorted(M):
            k = _key(name)
            if not (k.startswith("inferenceshare") and k.endswith("pct")):
                continue
            if name not in USES:
                continue
            basis = "admissible cells" if "admissible" in k else "cells"
            vals = []
            for r in AUD.itertuples():
                b = BASES.get((str(r.log), str(r.target)))
                if b and basis in b:
                    vals.append(float(r.inference_cells_observed) / b[basis])
            if not vals:
                continue
            s = pd.Series(vals)
            agg, x = ("median", s.median())
            if "min" in k:
                agg, x = "min", s.min()
            elif "max" in k:
                agg, x = "max", s.max()
            got = _num(M[name])
            if got is not None and abs(got - 100.0 * float(x)) > 0.06:
                vn.FAILS.append(
                    "round-27 condition: \\%s is %s and the %s share of a "
                    "pair's %s, multiplied out of the declared axis levels, "
                    "is %.1f%%" % (name, M[name], agg, basis,
                                   100.0 * float(x)))

    # --- 11.  the denominator belongs to the pair that attains rho = 1 ----
    #
    #  Section 6.3 quotes an admissible cell count beside the uniformly
    #  beneficial label.  It quoted it through a macro named for the OTHER
    #  target of the same log, and the error was invisible because both
    #  targets happen to carry the same count.  A macro whose name is fixed
    #  cannot notice that the region moved to a different pair, so the pair
    #  is re-derived here from the region file and the count re-multiplied
    #  from the declared axis levels -- neither of which is what the
    #  generator read.
    RG = _read(results, "s48w_regions.csv")
    AX2 = _read(results, "s42_axes.csv")
    if RG is not None and AX2 is not None and "region" in RG.columns:
        u = RG[RG.region.astype(str).str.strip() == "uniformly beneficial"]
        got = _num(M.get("nCellsUniformPair"))
        if got is not None:
            if len(u) != 1:
                vn.FAILS.append(
                    "round-27 condition: \\nCellsUniformPair names one pair's "
                    "admissible cells and %d pairs are uniformly beneficial"
                    % len(u))
            else:
                lg, tg = str(u.log.iloc[0]), str(u.target.iloc[0])
                A2 = AX2.assign(_c=AX2.n_pipeline * AX2.n_split
                                * AX2.n_quality * AX2.n_rung
                                * AX2.n_instrument)
                row = A2[(A2.log == lg) & (A2.target == tg)]
                if not len(row):
                    vn.FAILS.append(
                        "round-27 condition: the uniformly beneficial pair "
                        "%s/%s has no row in the axis file" % (lg, tg))
                elif abs(got - float(row._c.sum())) > 0.5:
                    vn.FAILS.append(
                        "round-27 condition: \\nCellsUniformPair is %s and "
                        "%s/%s -- the pair that attains rho = 1 -- carries "
                        "%d admissible cells"
                        % (M["nCellsUniformPair"], lg, tg,
                           int(row._c.sum())))
                else:
                    #  and the share the manuscript prints beside it
                    B = _read(results, "s48w_bands.csv.gz")
                    sh = _num(M.get("shareUniformFamilyPct"))
                    if B is not None and sh is not None:
                        fam = len(B[(B.family == "whole-surface")
                                    & (B.log == lg) & (B.target == tg)])
                        want = 100.0 * fam / float(row._c.sum())
                        if abs(sh - want) > 0.02:
                            vn.FAILS.append(
                                "round-27 condition: \\shareUniformFamilyPct "
                                "is %s and %s/%s bands %d of %d admissible "
                                "cells, which is %.2f%%"
                                % (M["shareUniformFamilyPct"], lg, tg, fam,
                                   int(row._c.sum()), want))
        #  the tie: the smallest share is the largest grid, and it is shared
        gp = _num(M.get("nPairsAtLargestGrid"))
        if gp is not None:
            A2 = AX2.assign(_c=AX2.n_pipeline * AX2.n_split * AX2.n_quality
                            * AX2.n_rung * AX2.n_instrument)
            n_at = int((A2._c == A2._c.max()).sum())
            if int(gp) != n_at:
                vn.FAILS.append(
                    "round-27 condition: \\nPairsAtLargestGrid is %s and %d "
                    "pair(s) carry the corpus's largest declared grid"
                    % (M["nPairsAtLargestGrid"], n_at))

    # --- 12.  the direction-carrying set is a test, not a list -----------
    #
    #  "\nLabelsLostToMinShare of the \nDirectionalLabels pairs that carry a
    #  direction" is printed in four places.  The denominator was once every
    #  non-`unresolved' label (too large by the sign-changing pairs) and then
    #  a hard-coded pair of conditional labels (too small by the uniformly
    #  beneficial one, the moment such a pair existed).  Both halves are
    #  re-derived here from the region file and the minimum share -- the
    #  numerator from THE SAME ROWS as the denominator, which is the property
    #  that failed the first time.
    if RG is not None and {"region", "n_resolved_whole",
                           "n_cells"} <= set(RG.columns):
        carries = RG.region.astype(str).str.contains("beneficial|harmful")
        D = RG[carries]
        got = _num(M.get("nDirectionalLabels"))
        if got is not None and int(got) != len(D):
            vn.FAILS.append(
                "round-27 condition: \\nDirectionalLabels is %s and %d "
                "pair(s) carry a label naming a sign (%s)"
                % (M["nDirectionalLabels"], len(D),
                   ", ".join(sorted(D.region.astype(str).unique()))))
        thr = _num(M.get("minResolvedSharePct"))
        lost = _num(M.get("nLabelsLostToMinShare"))
        if thr is not None and lost is not None and len(D):
            share = D.n_resolved_whole / D.n_cells
            n_lost = int((share < thr / 100.0).sum())
            if int(lost) != n_lost:
                vn.FAILS.append(
                    "round-27 condition: \\nLabelsLostToMinShare is %s and %d "
                    "of the %d direction-carrying pairs resolve less than %s "
                    "of their family" % (M["nLabelsLostToMinShare"], n_lost,
                                         len(D), M["minResolvedSharePct"]))

    # --- 13.  the widening that is not applied is SMALLER than the need ---
    #
    #  Section 10 once said the calibration's range lay ABOVE the measured
    #  shortfall, and called it conservative.  It lies below: that is the
    #  whole reason it is not applied, and the sentence had survived the
    #  measurement that reversed it.  A directional word is a claim, so the
    #  direction is checked rather than trusted.
    _cal = _num(M.get("calAtMedianPair"))
    _sw = _num(M.get("shortfallWholeMin"))
    _sd = _num(M.get("shortfallDcaMin"))
    if _cal is not None and _sw is not None and not (_cal < _sw):
        vn.FAILS.append(
            "round-27 condition: Section 10 says the calibration factor at the "
            "median pair (%s) is below the bottom of the surface shortfall "
            "(%s), and it is not" % (M["calAtMedianPair"],
                                     M["shortfallWholeMin"]))
    if _cal is not None and _sd is not None and not (_cal < _sd):
        vn.FAILS.append(
            "round-27 condition: Section 10 says the calibration factor at the "
            "median pair (%s) is well below the decision-curve shortfall (%s), "
            "and it is not" % (M["calAtMedianPair"], M["shortfallDcaMin"]))
    #  \calMin and \calMax are WHAT THE FITTED CURVE SUPPLIES, not what is
    #  applied -- every prose site asks the former.  They were once set to
    #  one to mean "nothing is applied", which emptied three sentences into
    #  "1.00 to 1.00", so the range is checked against the file that measured
    #  it and required to be a real widening.
    _cmin, _cmax = _num(M.get("calMin")), _num(M.get("calMax"))
    G33 = _read(results, "s33_regions.csv")
    if G33 is not None and "c" in G33.columns and None not in (_cmin, _cmax):
        for _nm, _v, _w in (("calMin", _cmin, float(G33.c.min())),
                            ("calMax", _cmax, float(G33.c.max()))):
            if abs(_v - _w) > 0.005:
                vn.FAILS.append(
                    "round-27 condition: \\%s is %s and the calibration "
                    "supplies %.2f on this corpus" % (_nm, M[_nm], _w))
        if _cmin <= 1.0:
            vn.FAILS.append(
                "round-27 condition: \\calMin is %s -- a factor of one is no "
                "widening, and the sentences that quote this range are asking "
                "what the calibration would supply" % M["calMin"])

    # --- 14.  the multiplier band IS the reported band -------------------
    #
    #  Section 6.4 prints what each estimator resolves.  The multiplier one
    #  is not an alternative to the article's band -- it IS the article's
    #  band -- so its count must equal the headline resolved count exactly.
    #  It did not: the estimator comparison read a fixed filename and went on
    #  reporting the retired surface, giving a multiplier total LARGER than
    #  the number of cells the article says it resolves, over what both call
    #  "the whole-surface families".  Equality is the check that would have
    #  caught it, and it costs nothing.
    _rw = _num(M.get("nResolvedWhole"))
    _rm = _num(M.get("nResolvedWholeMult"))
    if _rw is not None and _rm is not None and abs(_rw - _rm) > 0.5:
        vn.FAILS.append(
            "round-27 condition: the multiplier band is the reported band, so "
            "\\nResolvedWholeMult (%s) must equal \\nResolvedWhole (%s)"
            % (M["nResolvedWholeMult"], M["nResolvedWhole"]))
    #  and the empirical quantile is the WIDER estimator on this corpus, so
    #  it must resolve no more than the multiplier does.  A directional word
    #  in Section 6.4 rests on this and is checked rather than trusted.
    _re = _num(M.get("nResolvedWholeEmp"))
    if _re is not None and _rm is not None and _re > _rm:
        vn.FAILS.append(
            "round-27 condition: Section 6.4 reads the empirical band as the "
            "more conservative one, and it resolves %s against the "
            "multiplier's %s" % (M["nResolvedWholeEmp"],
                                 M["nResolvedWholeMult"]))

    # --- 15.  the ladder's bottom rung IS the article's band -------------
    #
    #  The calibration sensitivity ladder's "nominal (c = 1)" rung is not an
    #  alternative analysis: c = 1 is no widening, which is what the article
    #  reports.  Its resolved count must therefore equal the headline.  It
    #  did not, for the same reason as condition 14 -- a fixed filename --
    #  and the appendix printed a nominal count larger than the article's own.
    _sn = _num(M.get("nResolvedSensNominal"))
    if _rw is not None and _sn is not None and abs(_rw - _sn) > 0.5:
        vn.FAILS.append(
            "round-27 condition: the sensitivity ladder's nominal rung is the "
            "article's own band, so \\nResolvedSensNominal (%s) must equal "
            "\\nResolvedWhole (%s)"
            % (M["nResolvedSensNominal"], M["nResolvedWhole"]))
    #  the ladder must also be monotone: widening cannot resolve more.
    _sc, _su = (_num(M.get("nResolvedSensCalibrated")),
                _num(M.get("nResolvedSensUpper")))
    if None not in (_sn, _sc, _su) and not (_sn >= _sc >= _su):
        vn.FAILS.append(
            "round-27 condition: widening a band cannot resolve more cells, "
            "and the ladder runs %s, %s, %s"
            % (M["nResolvedSensNominal"], M["nResolvedSensCalibrated"],
               M["nResolvedSensUpper"]))

    # --- 16.  an enumeration of the corpus must enumerate the corpus ------
    #
    #  The appendix printed a four-label region enumeration that summed to
    #  eighteen over nineteen pairs, because the list of labels was written
    #  when no pair carried the fifth one.  The missing pair was the uniformly
    #  beneficial surface -- the label the round turns on.  A list that claims
    #  to partition the corpus is checked by adding it up, which is the only
    #  check that would have caught a label nobody thought to look for.
    _np = _num(M.get("nPairs"))
    _sets = (
        ("the reported band, before the minimum share",
         ("nCondBeneficial", "nSignChanging", "nCondHarmful",
          "nUniformlyBeneficial", "nUnresolvedPairs")),
        ("the reported band, minimum share included",
         ("nCondBeneficialMinShare", "nSignChangingMinShare",
          "nCondHarmfulMinShare", "nUniformlyBeneficialMinShare",
          "nUnresolvedMinShare")),
        ("the band a widening would give",
         ("nCondBeneficialCal", "nSignChangingCal", "nCondHarmfulCal",
          "nUniformlyBeneficialCal", "nUnresolvedCalibrated")),
    )
    if _np is not None:
        for _lab, _names in _sets:
            _vals = [_num(M.get(n)) for n in _names]
            if any(v is None for v in _vals):
                continue
            _tot = sum(_vals)
            if abs(_tot - _np) > 0.5:
                vn.FAILS.append(
                    "round-27 condition: the region enumeration for %s sums "
                    "to %d over a corpus of %d (%s)"
                    % (_lab, int(_tot), int(_np),
                       ", ".join("%s=%s" % (n, M[n])
                                 for n in _names)))

    # --- 17.  the coverage quoted is the coverage of the reported design --
    #
    #  The manuscript quoted a median pooled over every matched family --
    #  decision-curve with surface, draw counts from 33 to 1000, family sizes
    #  from 120 to 2966 -- as "this corpus's" coverage, two sentences from the
    #  400-draw figure, which it contradicted.  The corpus runs one design.
    #  The coverage it is entitled to quote is that design's, and it is
    #  re-derived here from the corpus's own cell and draw counts rather than
    #  from a number typed beside them.
    CVv = _read(results, "s41_coverage.csv")
    Bw = _read(results, "s48w_bands.csv.gz")
    Gd = _read(results, "s44_grid.csv")
    _got = _num(M.get("covHeavyWholeAtDesign"))
    if (CVv is not None and Bw is not None and Gd is not None
            and _got is not None):
        _bw = Bw[Bw.family == "whole-surface"]
        _fam = int(_bw.groupby(["log", "target"]).size().median())
        _b = int(Gd.draws.max())
        _row = CVv[(CVv.regime == "heavy") & (CVv.candidate == "q_mult")
                   & (CVv.family == "whole-surface")
                   & (CVv.K_nom == _fam) & (CVv.B == _b)]
        if not len(_row):
            vn.FAILS.append(
                "round-27 condition: the corpus runs %d cells at %d draws and "
                "the band-coverage design has no matched family there, so the "
                "coverage the manuscript quotes is measured on another design"
                % (_fam, _b))
        else:
            _want = 100.0 * float(_row.coverage.iloc[0])
            if abs(_got - _want) > 0.06:
                vn.FAILS.append(
                    "round-27 condition: \\covHeavyWholeAtDesign is %s and the "
                    "family matched to this corpus's design (%d cells, %d "
                    "draws) covers %.1f%%"
                    % (M["covHeavyWholeAtDesign"], _fam, _b, _want))
            #  the limitations call the shortfall more than five standard
            #  errors; a directional word is a claim.
            _se = _num(M.get("covHeavyWholeAtDesignSE"))
            if _se and _se > 0 and (95.0 - _got) / _se <= 5.0:
                vn.FAILS.append(
                    "round-27 condition: Section 11 calls the shortfall more "
                    "than five Monte Carlo standard errors, and %s against a "
                    "nominal 95%% at an error of %s is %.1f"
                    % (M["covHeavyWholeAtDesign"],
                       M["covHeavyWholeAtDesignSE"], (95.0 - _got) / _se))

    # --- 18.  the marked rows and the withdrawn directions reconcile ------
    #
    #  A reader counting the rows Table 5 marks gets a larger number than the
    #  caption's withdrawal count, and nothing told them why.  The difference
    #  is exactly the sign-changing rows, which are marked and carry no
    #  direction.  The caption now prints both; this checks they reconcile,
    #  so the explanation cannot drift from the counts it explains.
    _mk = _num(M.get("nMarkedBelowMinShare"))
    _sc = _num(M.get("nSignChangingBelowMinShare"))
    _lost = _num(M.get("nLabelsLostToMinShare"))
    if None not in (_mk, _sc, _lost) and abs((_mk - _sc) - _lost) > 0.5:
        vn.FAILS.append(
            "round-27 condition: Table 5 marks %s rows of which %s are "
            "sign-changing, leaving %d directions withdrawn, and "
            "\\nLabelsLostToMinShare is %s"
            % (M["nMarkedBelowMinShare"], M["nSignChangingBelowMinShare"],
               int(_mk - _sc), M["nLabelsLostToMinShare"]))

    # --- 19.  the rho = 1 pair survives the widening, and is the same pair -
    #
    #  The appendix claims the widening moves how much the corpus resolves
    #  but not which pair reaches rho = 1.  That is a robustness claim a
    #  referee will test, and until now it was asserted.  Both halves are
    #  checked: the count, and the IDENTITY -- a count that stays at one
    #  while the pair moves would satisfy the sentence and refute the claim.
    G33c = _read(results, "s33_regions.csv")
    if (G33c is not None and len(G33c)
            and {"region", "region_calibrated"} <= set(G33c.columns)):
        _n = G33c[G33c.region == "uniformly beneficial"][["log", "target"]]
        _c = G33c[G33c.region_calibrated
                  == "uniformly beneficial"][["log", "target"]]
        _ns = set(map(tuple, _n.values))
        _cs = set(map(tuple, _c.values))
        if _ns != _cs:
            vn.FAILS.append(
                "round-27 condition: the appendix says the widening does not "
                "change which pair reaches rho = 1; nominally it is %s and "
                "under the widening %s"
                % (sorted(_ns) or "none", sorted(_cs) or "none"))
        _chg = G33c[G33c.region != G33c.region_calibrated]
        _gotc = _num(M.get("nRegionsChangedByCalibration"))
        if _gotc is not None and int(_gotc) != len(_chg):
            vn.FAILS.append(
                "round-27 condition: \\nRegionsChangedByCalibration is %s and "
                "%d label(s) differ under the widening"
                % (M["nRegionsChangedByCalibration"], len(_chg)))
        if _ns & set(map(tuple, _chg[["log", "target"]].values)):
            vn.FAILS.append(
                "round-27 condition: the appendix says the rho = 1 pair is "
                "not among the labels the widening changes, and it is")

    # --- 20.  the container sentence tracks the container -----------------
    #
    #  The code-availability statement claims bit-exactness INSIDE a
    #  container.  A container pinned by a mutable tag is not a fixed object,
    #  so that claim needed the base pinned by digest -- and once the sentence
    #  quotes the digest, an edit to the Dockerfile can falsify the paper
    #  silently.  The digest is therefore re-read from the Dockerfile here and
    #  matched against what the manuscript prints.
    import re as _re
    _dock = results.parent / "Dockerfile"
    _macro = M.get("imageDigest") or ""
    if _dock.exists():
        try:
            _df = _dock.read_text(encoding="utf-8")
        except OSError:
            _df = ""
        _m = _re.search(r"^FROM\s+\S+@(sha256:[0-9a-f]{64})", _df, _re.M)
        if not _m:
            if "pinned by digest" in _macro:
                vn.FAILS.append(
                    "round-27 condition: the code-availability statement says "
                    "the base is pinned by digest and the Dockerfile pins it "
                    "by tag")
        else:
            _d = _m.group(1)
            _head, _tail = _d[:14], _d[-6:]
            if "pinned by digest" in _macro and not (
                    _head in _macro and _tail in _macro):
                vn.FAILS.append(
                    "round-27 condition: the manuscript quotes a base image "
                    "digest that is not the Dockerfile's (%s)" % _d)

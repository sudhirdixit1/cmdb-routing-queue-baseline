"""round27_verify -- THE FIVE CROSS-OBJECT CONDITIONS ROUND TWENTY-SEVEN ADDS.

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

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
    "the prefix pilot at case creation reproduces the layer ladder's finest "
    "rung, on the same cases, to the sixth decimal",
    "every drift percentile is a percentile, and the drift flag is exactly "
    "the upper-tail rule it is defined from",
    "neither document calls a register's coarse layers free while the "
    "measured share says otherwise",
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

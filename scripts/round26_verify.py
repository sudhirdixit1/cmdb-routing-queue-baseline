"""round26_verify -- the conditions round twenty-six earned.

Two of them exist because this round broke them itself, which is the only
reason a guard is worth writing.

1.  A CAPTION THAT MULTIPLIES A PRODUCT MUST REACH ITS OWN TOTAL.  Figure 1's
    caption now states the cell count and the product that gives it, because
    the referee had to reconstruct that arithmetic from five numbers in two
    sections.  Writing it, we reached for `nPipelines' -- which is the CROSSED
    factorial of families, encodings and targets, three times the number of
    pipeline levels the figure's pair actually runs -- and printed a product
    that missed its own stated total by a factor of three.  Every macro in it
    was correct; the sentence was not.  The check multiplies the factors and
    compares.

2.  AN EXACT PARTITION MUST SUM TO ONE.  The four shares of equation (7) are
    a partition of the decomposition's components, so their medians need not
    sum to one -- a median is not linear -- but the partition's own residual
    is computed and carried as a macro, and if it ever stops being of the
    order of machine epsilon the partition has stopped being one.

3.  A RESTRICTED COUNT CANNOT EXCEED THE SET IT RESTRICTS.  The
    MPID-restricted, resolved and fully-restricted cell counts are nested by
    construction; if the code that computes them ever stops nesting them, the
    rates built on them are ratios of unrelated sets.
"""
from __future__ import annotations

import re

#: (total macro, factor macros, what the product is of)
PRODUCTS = (
    ("nCellsFigOne",
     ("nPipelineLevelsCase", "nRungsFigOne", "nInstruments",
      "nQualityFigOne", "nSplits"),
     "Figure 1's cell count against the product its caption prints"),
)

#: counts that must be nested, outermost first
NESTED = (
    (("nCellsAuc", "nCellsAboveMpid"),
     "cells above the MPID cannot outnumber the AUC cells they are drawn "
     "from"),
    (("nCellsAuc", "nCellsResolvedAuc"),
     "resolved AUC cells cannot outnumber the AUC cells"),
    (("nCellsResolvedAuc", "nCellsResolvedMpid"),
     "resolved cells above the MPID cannot outnumber the resolved cells"),
    (("nCellsResolvedMpid", "nCellsFullyRestricted"),
     "the fully restricted set cannot outnumber the resolved-and-above-MPID "
     "set it restricts"),
    (("nCellsFullyRestricted", "nDisagreeFullyRestricted"),
     "disagreements cannot outnumber the cells they are counted in"),
)


def _n(s):
    """A macro's numeric value, or None.  Macros carry thousands separators
    as `{,}', percent signs escaped, and signs inside math mode."""
    if s is None:
        return None
    t = re.sub(r"\{,\}|,", "", str(s))
    t = t.replace("\\%", "").replace("$", "").replace("+", "").strip()
    try:
        return float(t)
    except ValueError:
        return None


def check(vn, M):
    missing = "\\textbf{??}"

    for total, factors, why in PRODUCTS:
        if total not in M or M[total] == missing:
            continue
        vals = [_n(M.get(f)) for f in factors]
        if any(v is None for v in vals):
            continue
        prod = 1.0
        for v in vals:
            prod *= v
        got = _n(M[total])
        if got is None or abs(prod - got) > 0.5:
            vn.FAILS.append(
                "round-26 condition: %s -- %s is %s but %s multiply to %d"
                % (why, total, M[total], " x ".join(factors), int(prod)))

    if "stratumPartitionError" in M and M["stratumPartitionError"] != missing:
        #  the macro is rendered in LaTeX scientific notation, so read the
        #  exponent rather than the mantissa
        m = re.search(r"10\^\{(-?\d+)\}", str(M["stratumPartitionError"]))
        if m and int(m.group(1)) > -10:
            vn.FAILS.append(
                "round-26 condition: the four-way partition's residual is "
                "%s, which is not machine epsilon -- it has stopped being a "
                "partition" % M["stratumPartitionError"])

    for (outer, inner), why in NESTED:
        a, b = _n(M.get(outer)), _n(M.get(inner))
        if a is None or b is None:
            continue
        if b > a:
            vn.FAILS.append("round-26 condition: %s (%s = %s, %s = %s)"
                            % (why, outer, M[outer], inner, M[inner]))


#: the human-readable conditions, appended to verify_numbers.CONDITIONS
CONDITIONS = (
    "Figure 1's stated cell count equals the product its caption prints",
    "the four-way variance partition's residual is machine epsilon",
    "the MPID, resolved and fully-restricted cell counts are nested",
)

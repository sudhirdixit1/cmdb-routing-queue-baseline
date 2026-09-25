"""s43 -- THE OVERVIEW FIGURE.  Round twenty-six, item C1.

The sixth referee's first presentation complaint was that a reader meets four
reporting objects, three denominators and a private vocabulary before anything
shows them how the pieces fit.  This draws the method once: the roles a log is
read into, the design space they are crossed over, the surface that produces,
the three denominators a claim may quantify over, and the objects computed
from it.

It is a schematic and carries no result, which is why it lives in its own file
and reads no result file: nothing here can go stale against a number, and the
provenance guard has nothing to certify.  Every quantity a reader might want
beside it is in Table~1 (the objects), Table~2 (the axes) and Table~3 (the
roles per pair).

What CAN go stale is a pointer: the boxes name sections, tables, definitions
and an equation by number, and the article's numbering moves when a section
is cut or added.  Every such string is in POINTERS below, in one place, and is
checked against the built manuscript's headings before a submission.

    python s43_overview.py     -> paper/figS8_overview.png and .pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

PAPER = HERE.parent / "paper"
#  pdf.fonttype 42 embeds the text as TrueType so it stays text in the vector
#  file (type 3, the default, outlines every glyph).
#  IJF print geometry: the canvas is the article's text width (468 TeX pt,
#  elsarticle 3p) and is saved WITHOUT a tight bounding box, so at
#  \includegraphics[width=\textwidth] it prints at 1:1 and the sizes below
#  are the sizes on the page -- 8 pt body, 8.5 pt titles.
TEXTWIDTH_IN = 468.0 / 72.27
BODY_PT = 8.0
TITLE_PT = 8.5
plt.rcParams.update({"font.size": BODY_PT, "figure.dpi": 400,
                     "savefig.bbox": "standard",
                     "axes.grid": False,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
DARK = "0.20"
MID = "0.30"

#  EVERY section, table, definition and equation number the diagram prints.
#  These are literals: the figure is drawn outside LaTeX and cannot \ref.
#  CHECK EACH against the built manuscript's headings before a submission --
#      pdftotext -layout build/journal/manuscript.pdf - | grep -n "^ *[0-9]"
#  -- and against its table captions and definitions, and re-run this script
#  whenever the article's numbering moves.  The keys name the box; the values
#  are printed verbatim.
POINTERS = {
    #  2026-09-25: set from build/journal/*.aux after the IJF length pass.
    "roles": "Section 5.2, Table S20",        # 5.2 Roles; the roles table is in the supplement
    "design_space": "Definition 1, Table 2",  # Def. 1 design space; Table 2 axes
    "surface": "Equation 1",                  # (1) the increment V_s(f)
    "denominators": "Section 4.2",            # 4.2 three surfaces / denominators
    "decomposition": "Section 4.4, Table 4",  # 4.4 decomposition; Table 4 strata
    "band": "Sections 4.3, 9.2",              # 4.3 bands; 9.2 family-wise coverage
    "region": "Definition 3, Table 3",        # Def. 3 regions; Table 3 master (labels)
    "standard": "Section 11; S22",            # 11 conclusion; Supplement S22 the standard in full
    #  The footer that pointed to specification regret (Supplement S3.2) is
    #  gone: it repeated the text in smaller grey type, and regret is not a
    #  contribution, so the figure no longer prints that pointer.
}


def box(ax, x, y, w, h, title, body, fill="0.97", edge=DARK, lw=0.9):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.012",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h - 0.036, title, ha="center", va="top",
            fontsize=TITLE_PT, fontweight="bold", color=DARK, zorder=3)
    if body:
        ax.text(x + w / 2, y + h - 0.098, body, ha="center", va="top",
                fontsize=BODY_PT, color=DARK, linespacing=1.35, zorder=3)


def arrow(ax, xy_from, xy_to, style="-|>", rad=0.0, colour=MID):
    ax.add_patch(FancyArrowPatch(
        xy_from, xy_to, arrowstyle=style, mutation_scale=9,
        linewidth=0.9, color=colour,
        connectionstyle="arc3,rad=%.2f" % rad, zorder=1))


def main():
    fig = plt.figure(figsize=(TEXTWIDTH_IN, 3.70))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    #  a margin round the unit square, so the boxes' rounded pads and
    #  outlines are inside the canvas
    ax.set_xlim(-0.012, 1.012)
    ax.set_ylim(-0.012, 1.012)
    ax.axis("off")

    #  ---- row one: the log, the roles, the design space, the surface -----
    TOP_Y, TOP_H = 0.665, 0.325
    box(ax, 0.000, TOP_Y, 0.205, TOP_H, "case data",
        "cases, attributes,\ntimestamps\n\n"
        "BPIC14: incidents at\na bank's service desk")
    box(ax, 0.250, TOP_Y, 0.225, TOP_H, "roles, pre-specified",
        "predictor $f$\nfree field $g$\nbenchmark $B_0$\n\n"
        "(%s)" % POINTERS["roles"])
    box(ax, 0.520, TOP_Y, 0.225, TOP_H, "design space $\\mathcal{S}$",
        "pipeline $\\times$ split\n"
        "$\\times$ quality $\\times$ baseline\n$\\times$ metric\n\n"
        "(%s)" % POINTERS["design_space"])
    box(ax, 0.790, TOP_Y, 0.210, TOP_H, "the surface",
        "$s \\mapsto V_s(f)$\none increment\nper cell\n\n"
        "(%s)" % POINTERS["surface"])

    ymid = TOP_Y + TOP_H / 2
    for x0, x1 in ((0.215, 0.240), (0.485, 0.510), (0.755, 0.780)):
        arrow(ax, (x0, ymid), (x1, ymid))

    #  ---- the denominator gate -------------------------------------------
    box(ax, 0.150, 0.440, 0.700, 0.165,
        "three sets of specifications  (%s)" % POINTERS["denominators"],
        "declared  |  computed  |  bootstrapped \u2014 each claim\n"
        "states which one it covers",
        fill="0.93")
    arrow(ax, (0.895, TOP_Y - 0.012), (0.862, 0.525), rad=-0.20)

    #  ---- row two: the objects -------------------------------------------
    BOT_Y, BOT_H = 0.000, 0.370
    XS = (0.000, 0.260, 0.520, 0.780)
    BW = 0.220
    box(ax, XS[0], BOT_Y, BW, BOT_H,
        "decomposition",
        "which choice moves\nthe answer, with the\n"
        "split as an $\\bf{error}$\n$\\bf{stratum}$\n\n"
        + POINTERS["decomposition"])
    box(ax, XS[1], BOT_Y, BW, BOT_H,
        "simultaneous band",
        "max-$t$ over the whole\nfamily the claim\n"
        "ranges over, $\\bf{coverage}$\n$\\bf{measured}$\n\n"
        + POINTERS["band"])
    box(ax, XS[2], BOT_Y, BW, BOT_H,
        "region and $\\rho$",
        "where the sign is\ndetermined, with the\n"
        "counts and a minimum\nresolved share\n\n"
        + POINTERS["region"])
    box(ax, XS[3], BOT_Y, BW, BOT_H,
        "reporting standard",
        "the minimum form a\nclaim must carry, and\n"
        "the package that\nemits it\n\n" + POINTERS["standard"],
        fill="0.93")

    #  the gate feeds the three objects; the region feeds the standard
    for x in XS[:3]:
        xc = x + BW / 2
        arrow(ax, (min(max(xc, 0.20), 0.80), 0.428), (xc, BOT_Y + BOT_H + 0.012))
    arrow(ax, (XS[2] + BW + 0.005, BOT_H / 2), (XS[3] - 0.005, BOT_H / 2))

    p = PAPER / "figS8_overview.png"
    fig.savefig(p)
    fig.savefig(p.with_suffix(".pdf"))
    plt.close(fig)
    print("  wrote %s and %s" % (p, p.with_suffix(".pdf").name))


if __name__ == "__main__":
    main()

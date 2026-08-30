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
beside it is in Table~1 (the objects), Table~2 (the axes) and Table~4 (the
roles per pair).

    python s43_overview.py     -> paper/figS8_overview.png
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
plt.rcParams.update({"font.size": 7.4, "figure.dpi": 400,
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
                     "axes.grid": False})
DARK = "0.20"
MID = "0.45"


def box(ax, x, y, w, h, title, body, fill="0.97", edge=DARK, lw=0.9):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.012",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h - 0.036, title, ha="center", va="top",
            fontsize=7.6, fontweight="bold", color=DARK, zorder=3)
    if body:
        ax.text(x + w / 2, y + h - 0.098, body, ha="center", va="top",
                fontsize=7.0, color=DARK, linespacing=1.45, zorder=3)


def arrow(ax, xy_from, xy_to, style="-|>", rad=0.0, colour=MID):
    ax.add_patch(FancyArrowPatch(
        xy_from, xy_to, arrowstyle=style, mutation_scale=9,
        linewidth=0.9, color=colour,
        connectionstyle="arc3,rad=%.2f" % rad, zorder=1))


def main():
    fig, ax = plt.subplots(figsize=(7.1, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    #  ---- row one: the log, the roles, the design space, the surface -----
    box(ax, 0.005, 0.660, 0.205, 0.320, "an event log",
        "cases, attributes,\ntimestamps\n\n"
        "BPIC14: incidents at\na bank's service desk")
    box(ax, 0.245, 0.660, 0.235, 0.320, "roles, by rule",
        "register $f$\nfree field $g$\nintake block $B_0$\n\n"
        "(Section 5.2, Table 3)")
    box(ax, 0.515, 0.660, 0.235, 0.320, "design space $\\mathcal{S}$",
        "pipeline $\\times$ split\n"
        "$\\times$ quality $\\times$ rung\n$\\times$ instrument\n\n"
        "(Definition 1, Table 2)")
    box(ax, 0.785, 0.660, 0.210, 0.320, "the surface",
        "$s \\mapsto V_s(f)$\none increment per cell\n\n"
        "(Equation 1)")

    for x0, x1 in ((0.210, 0.245), (0.480, 0.515), (0.750, 0.785)):
        arrow(ax, (x0, 0.820), (x1, 0.820))

    #  ---- the denominator gate -------------------------------------------
    box(ax, 0.150, 0.430, 0.700, 0.175,
        "three denominators, audited apart  (Section 4.2)",
        "declared  |  computational  |  inference \u2014 a claim\n"
        "quantifies over exactly one",
        fill="0.93")
    arrow(ax, (0.890, 0.660), (0.855, 0.530), rad=-0.20)

    #  ---- row two: the objects -------------------------------------------
    box(ax, 0.005, 0.045, 0.240, 0.345,
        "decomposition",
        "which choice moves\nthe answer, with the\n"
        "split as an $\\bf{error}$\n$\\bf{stratum}$\n\n"
        "Section 4.5, Table 5")
    box(ax, 0.255, 0.045, 0.240, 0.345,
        "simultaneous band",
        "max-$t$ over the whole\nfamily the claim ranges\n"
        "over, $\\bf{coverage}$\n$\\bf{measured}$\n\n"
        "Sections 4.3, 9.4")
    box(ax, 0.505, 0.045, 0.240, 0.345,
        "region and $\\rho$",
        "where the sign is\ndetermined, with the\n"
        "counts and a minimum\nresolved share\n\n"
        "Definition 3, Table 6")
    box(ax, 0.755, 0.045, 0.240, 0.345,
        "reporting standard",
        "the minimum form a\nclaim must carry, and\n"
        "the package that\nemits it\n\nSection 4.8", fill="0.93")

    for x in (0.125, 0.375, 0.625):
        arrow(ax, (0.500, 0.430), (x, 0.390), rad=0.12)
    arrow(ax, (0.745, 0.215), (0.755, 0.215))

    ax.text(0.5, -0.035,
            "Specification regret \u2014 what one specification costs against "
            "the best \u2014 is computed from the same surface and reported "
            "as a robustness check (Section 4.7).",
            fontsize=6.4, color=MID, ha="center", va="top")

    p = PAPER / "figS8_overview.png"
    fig.savefig(p)
    plt.close(fig)
    print("  wrote %s" % p)


if __name__ == "__main__":
    main()

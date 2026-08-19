"""Figures for the revised thesis: resolution and targeting."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import FIGURES, RESULTS

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04,
})
C = {"Rabobank": "#0D6B6E", "ServiceNow-IT": "#A8442B", "VolvoIT": "#7A6112"}

# ------------------------------------------------------- resolution curve
curve = pd.read_csv(RESULTS / "e13_resolution_curve.csv")
real = pd.read_csv(RESULTS / "e13_real_fields.csv")

fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.7), sharey=False)
for ax, org in zip(axes, ["Rabobank", "VolvoIT", "ServiceNow-IT"]):
    c = curve[curve.org == org].sort_values("k")
    ax.plot(c.k, c.gain, "-o", ms=3.4, lw=1.5, color=C[org], zorder=3,
            label="random partition")
    ax.fill_between(c.k, c.gain - c.sd, c.gain + c.sd, color=C[org], alpha=.15)
    full = c.gain.iloc[-1]
    ax.axhline(full * 0.90, color="#888", lw=.9, ls=":")
    r = real[real.org == org]
    for _, row in r.iterrows():
        mk = "^" if row.gain > np.interp(np.log2(max(row.cardinality, 2)),
                                         np.log2(c.k.clip(lower=2)),
                                         c.gain) + .01 else "s"
        ax.scatter([row.cardinality], [row.gain], marker=mk, s=42, zorder=5,
                   color="white", edgecolor=C[org], linewidth=1.4)
        ax.annotate(row.field, (row.cardinality, row.gain), fontsize=6,
                    textcoords="offset points", xytext=(3, -9), color="#333")
    ax.set_xscale("log", base=2)
    ax.set_title(org, fontsize=8.5)
    ax.set_xlabel("distinct component values ($k$)")
    if org == "Rabobank":
        ax.set_ylabel("AUC gain over no component id")
    ax.text(2.2, full * 0.90 + .004, "90% of full", fontsize=6.2, color="#666")
fig.savefig(FIGURES / "figA_resolution_curve.png")
plt.close(fig)

# ------------------------------------------------------- targeting curve
w = pd.read_csv(RESULTS / "e14_which_cis.csv").sort_values("k")
fig, ax = plt.subplots(figsize=(6.6, 3.2))
ax.axhline(w.full.iloc[0], color="#0D6B6E", lw=1.1, ls=":")
ax.text(9, w.full.iloc[0] + .004, "full CMDB, all 3,019 CIs", fontsize=7.2,
        color="#0D6B6E")
ax.axhline(w.base.iloc[0], color="#999", lw=1.1, ls="--")
ax.text(9, w.base.iloc[0] + .004, "no component identity", fontsize=7.2,
        color="#777")
ax.plot(w.k, w.top_k, "-o", ms=4.5, lw=1.9, color="#0D6B6E",
        label="top-$k$ by incident volume")
ax.plot(w.k, w.partition_k, "-s", ms=4, lw=1.5, color="#7A6112",
        label="all CIs, grouped into $k$ random buckets")
ax.plot(w.k, w.random_k, "-^", ms=4, lw=1.5, color="#A8442B",
        label="$k$ CIs chosen at random")
ax.axvline(128, color="#0D6B6E", lw=.9, ls="-.")
ax.annotate("128 CIs (4% of estate,\n82% of incidents)\nreaches the ceiling",
            (128, 0.63), fontsize=7, color="#0D6B6E", ha="left",
            xytext=(8, 0), textcoords="offset points")
ax.set_xscale("log", base=2)
ax.set_xlabel("number of configuration items identified ($k$)")
ax.set_ylabel("AUC, misrouting prediction")
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.savefig(FIGURES / "figB_targeting.png")
plt.close(fig)

print("written:")
for p in ["figA_resolution_curve.png", "figB_targeting.png"]:
    print(f"  {p}  {(FIGURES/p).stat().st_size/1024:.1f} KB")

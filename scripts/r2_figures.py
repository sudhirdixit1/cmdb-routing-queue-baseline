"""Figures for the single-organisation paper."""
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
TEAL, RUST, OCHRE = "#0D6B6E", "#A8442B", "#7A6112"

# ---------------------------------------------------------------- Figure 1
t = pd.read_csv(RESULTS / "r1_targeting.csv").sort_values("k")
base, full = t.base.iloc[0], t.full.iloc[0]
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ax.axhline(full, color=TEAL, lw=1.1, ls=":")
ax.text(8.6, full + .004, f"all {2554:,} CIs identified ({full:.3f})",
        fontsize=7.2, color=TEAL)
ax.axhline(base, color="#888", lw=1.1, ls="--")
ax.text(8.6, base + .004, f"no CI identity ({base:.3f})", fontsize=7.2,
        color="#777")
ax.fill_between(t.k, t.top_lo, t.top_hi, color=TEAL, alpha=.15)
ax.plot(t.k, t.top_k, "-o", ms=4.5, lw=1.9, color=TEAL,
        label="top-$k$ by incident volume")
ax.fill_between(t.k, t.partition_k - t.partition_sd, t.partition_k + t.partition_sd,
                color=OCHRE, alpha=.15)
ax.plot(t.k, t.partition_k, "-s", ms=4, lw=1.6, color=OCHRE,
        label="all CIs collapsed into $k$ random buckets")
ax.axvline(64, color=TEAL, lw=.9, ls="-.")
ax.annotate("$k$=64 recovers 90%\n(70% of incidents)", (64, 0.60), fontsize=7,
            color=TEAL, ha="left", xytext=(7, 0), textcoords="offset points")
ax.set_xscale("log", base=2)
ax.set_xlabel("configuration items individually identified ($k$)")
ax.set_ylabel("AUC, misrouting prediction")
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
ax.set_ylim(base - .02, full + .02)
fig.savefig(FIGURES / "figR1_targeting.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
x = pd.read_csv(RESULTS / "r1_taxonomy.csv")
order = ["CI Type", "CI Subtype", "Service Component", "CI Name"]
x = x.set_index("field").reindex(order).reset_index()
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.9),
                         gridspec_kw={"width_ratios": [1, 1.25]})

a = axes[0]
yp = np.arange(len(x))
a.barh(yp + .18, x.nominal_k, .34, color="#C9D3D8", label="nominal labels")
a.barh(yp - .18, x.perplexity, .34, color=TEAL, label="effective ($2^H$)")
a.set_yticks(yp); a.set_yticklabels(x.field, fontsize=7.5)
a.set_xscale("log"); a.set_xlabel("distinct values")
a.legend(frameon=False, fontsize=7)
a.set_title("(a) label count overstates resolution", fontsize=8.5)
a.invert_yaxis()

b = axes[1]
cols = [TEAL if lo > 0 else (RUST if hi < 0 else "#8A97A0")
        for lo, hi in zip(x.lo, x.hi)]
b.errorbar(x.delta, yp, xerr=[x.delta - x.lo, x.hi - x.delta], fmt="none",
           ecolor="#999", lw=1.1, capsize=2.5)
b.scatter(x.delta, yp, s=54, color=cols, zorder=4, edgecolor="white", lw=.8)
b.axvline(0, color="#333", lw=1)
b.set_yticks(yp); b.set_yticklabels([]); b.invert_yaxis()
b.set_xlabel("AUC vs mass-matched random partition")
b.set_title("(b) does the taxonomy beat chance\nat matched resolution?",
            fontsize=8.5)
for i, (d, f) in enumerate(zip(x.delta, x.field)):
    b.annotate(f, (d, i), fontsize=7, textcoords="offset points",
               xytext=(0, 11), ha="center", color="#333")
fig.savefig(FIGURES / "figR2_taxonomy.png")
plt.close(fig)

print("written: figR1_targeting.png, figR2_taxonomy.png")

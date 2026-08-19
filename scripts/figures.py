"""Publication figures for the IAAI-27 submission."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from common import FIGURES, RESULTS, load_bpic13, load_bpic14, load_uci

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .5,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": .04,
})
C = {"Rabobank": "#0D6B6E", "ServiceNow-IT": "#A8442B", "VolvoIT": "#7A6112"}
ORDER = ["VolvoIT", "ServiceNow-IT", "Rabobank"]

# ---------------------------------------------------------------- Figure 1
audit = pd.read_csv(RESULTS / "e1_field_audit.csv")
classes = ["intake", "descriptive", "workflow", "outcome",
           "configuration", "relational"]
fig, ax = plt.subplots(figsize=(6.6, 2.9))
w, x = 0.26, np.arange(len(classes))
for i, org in enumerate(ORDER):
    vals = []
    for c in classes:
        s = audit[(audit.org == org) & (audit.field_class == c)]
        s = s[s.present_in_export]
        vals.append(s.population.mean() * 100 if len(s) else np.nan)
    pos = x + (i - 1) * w
    bars = ax.bar(pos, vals, w, label=org, color=C[org], edgecolor="none")
    for p, v in zip(pos, vals):
        if np.isnan(v):
            ax.text(p, 3, "absent", rotation=90, ha="center", va="bottom",
                    fontsize=6.5, color=C[org], style="italic")
        elif v < 12:
            ax.text(p, v + 2, f"{v:.1f}", ha="center", va="bottom", fontsize=6.5,
                    color=C[org], fontweight="bold")
ax.axvline(3.5, color="#333", lw=.8, ls=(0, (4, 3)))
ax.text(1.5, 108, "operational fields", ha="center", fontsize=8, color="#333")
ax.text(4.5, 108, "configuration model", ha="center", fontsize=8, color="#333")
ax.set_xticks(x); ax.set_xticklabels(classes, fontsize=8)
ax.set_ylabel("mean population rate (%)"); ax.set_ylim(0, 118)
ax.set_yticks([0, 25, 50, 75, 100])
ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower left",
          bbox_to_anchor=(0, -0.34))
fig.savefig(FIGURES / "fig1_population_by_class.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
d = pd.read_csv(RESULTS / "e5_component_identity.csv")
d = d[d.population > 0.05].copy()
COMPONENT = {"product", "CI Name (aff)", "Service Component WBS (aff)",
             "CI Subtype (aff)", "CI Type (aff)", "subcategory", "category"}
PERSON = {"caller_id", "opened_by", "assigned_to"}
def kind(f):
    if f in COMPONENT: return "identifies a component"
    if f in PERSON:    return "identifies a person"
    return "other attribute"
d["kind"] = d.field.map(kind)
M = {"identifies a component": ("o", "#0D6B6E"),
     "identifies a person": ("s", "#A8442B"),
     "other attribute": ("^", "#8A97A0")}
fig, ax = plt.subplots(figsize=(6.6, 3.4))
for k, (mk, col) in M.items():
    s = d[d.kind == k]
    ax.scatter(s.cardinality, s.auc, marker=mk, s=46, color=col, label=k,
               zorder=3, edgecolor="white", linewidth=.6)
OFF = {"caller_id": (-8, -20), "opened_by": (6, 6), "location": (6, -14),
       "CI Name (aff)": (-14, 10), "product": (6, 6),
       "Service Component WBS (aff)": (-30, -20)}
for _, r in d.iterrows():
    if r.auc > 0.69 or r.field in ("caller_id", "opened_by", "location"):
        dx, dy = OFF.get(r.field, (7, -2))
        ax.annotate(f"{r.field}\n({r.org})", (r.cardinality, r.auc),
                    textcoords="offset points", xytext=(dx, dy), fontsize=6.4,
                    color="#333", ha="left")
ax.set_xscale("log"); ax.axhline(.5, color="#999", lw=.8, ls=":")
ax.set_xlabel("field cardinality (distinct values, log scale)")
ax.set_ylabel("single-field AUC, misrouting")
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
ax.set_ylim(.48, .79)
fig.savefig(FIGURES / "fig2_component_identity.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 3
g = pd.read_csv(RESULTS / "e3_degradation.csv").sort_values("rate")
base, ceil = 0.566, 0.743
fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.0))

# (a) linear -- the headline: benefit is roughly proportional to population
a = axes[0]
a.plot([0, 100], [0, 100], color="#999", lw=1, ls=":", zorder=1)
a.plot(g.rate * 100, g.headroom_kept * 100, "-o", color="#0D6B6E", ms=4,
       lw=1.6, zorder=3)
a.text(52, 44, "proportional\nreference", fontsize=7, color="#777",
       rotation=38, ha="center")
a.set_xlabel("CI population rate (%)")
a.set_ylabel("CMDB benefit retained (%)")
a.set_xlim(-3, 103); a.set_ylim(-3, 103)
a.set_title("(a) benefit scales with population", fontsize=8.5)

# (b) log -- where the observed instances actually sit
b = axes[1]
b.axhspan(base, ceil, color="#0D6B6E", alpha=.07)
b.plot(g.rate.clip(lower=0.0015) * 100, g.auc, "-o", color="#0D6B6E", ms=4,
       lw=1.6, zorder=3)
b.axhline(base, color="#A8442B", lw=1.1, ls="--")
b.axhline(ceil, color="#0D6B6E", lw=1.1, ls=":")
b.axvline(0.2, color="#A8442B", lw=.9, ls="-.")
b.annotate("ServiceNow-IT\nobserved (0.2%)", (0.22, 0.695), fontsize=6.8,
           color="#A8442B", ha="left")
b.text(1.1, ceil - .012, "full CMDB ceiling", fontsize=6.8, color="#0D6B6E")
b.text(1.1, base + .005, "intake-only baseline", fontsize=6.8, color="#A8442B")
b.set_xscale("log")
b.set_xlabel("CI population rate (%)")
b.set_ylabel("AUC, misrouting")
b.set_xticks([0.2, 1, 5, 20, 100])
b.set_xticklabels(["0.2", "1", "5", "20", "100"])
b.set_ylim(.555, .755)
b.set_title("(b) observed instances on the curve", fontsize=8.5)
fig.savefig(FIGURES / "fig3_degradation.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 4
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.8))
u = load_uci()
u["ra"] = pd.to_numeric(u.reassignment_count, errors="coerce").clip(upper=5)
gu = u.groupby("ra").sla_breach.mean() * 100
axes[0].plot(gu.index, gu.values, "-o", color=C["ServiceNow-IT"], ms=4)
axes[0].set_title("ServiceNow-IT · SLA breach", fontsize=8.5)
axes[0].set_ylabel("breach rate (%)")

r = load_bpic14()
r["ht"] = pd.to_numeric(r["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                        errors="coerce")
r["ra"] = pd.to_numeric(r["# Reassignments"], errors="coerce").clip(upper=5)
gr = r.dropna(subset=["ht"]).groupby("ra").ht.median()
axes[1].plot(gr.index, gr.values, "-o", color=C["Rabobank"], ms=4)
axes[1].set_title("Rabobank · median handling time", fontsize=8.5)
axes[1].set_ylabel("hours")
for a in axes:
    a.set_xlabel("reassignments")
    a.set_xticks(range(6)); a.set_xticklabels(["0", "1", "2", "3", "4", "5+"])
fig.savefig(FIGURES / "fig4_cost_of_misrouting.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 5
c = pd.read_csv(RESULTS / "e4_cost.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.0))
for label, col, ls in [("intake-only", "#A8442B", "--"),
                       ("intake+CMDB", "#0D6B6E", "-")]:
    s = c[c.model == label].sort_values("capacity")
    ax.plot(s.capacity * 100, s.precision * 100, ls, marker="o", ms=4,
            color=col, label=label, lw=1.6)
base_rate = 0.373 * 100
ax.axhline(base_rate, color="#999", lw=1, ls=":")
ax.text(41, base_rate + 1.2, "base rate (37.3% of incidents are misrouted)",
        fontsize=7.2, color="#666")
ax.set_xlabel("triage review capacity (% of incoming incidents reviewed)")
ax.set_ylabel("precision of the review queue (%)")
ax.legend(frameon=False, fontsize=8)
fig.savefig(FIGURES / "fig5_review_precision.png")
plt.close(fig)

print("figures written:")
for p in sorted(FIGURES.glob("*.png")):
    print(f"  {p.name:38s} {p.stat().st_size/1024:7.1f} KB")

# ---------------------------------------------------------------- Figure 6
lay = pd.read_csv(RESULTS / "e10b_layers.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.1))
tasks = lay.task.unique()
LAY_ORDER = ["1 intake", "2 + time", "3 + service", "4 + CI"]
COLS = ["#8A97A0", "#B8B0A0", "#0D6B6E", "#A8442B"]
w, x = 0.34, np.arange(len(LAY_ORDER))
for i, t in enumerate(tasks):
    s = lay[lay.task == t].set_index("layer").reindex(LAY_ORDER)
    ax.plot(x, s.auc, "-o", ms=5, lw=1.8,
            color="#0D6B6E" if i == 0 else "#A8442B",
            label=t.split(" (")[0])
    for xi, a in zip(x, s.auc):
        ax.annotate(f"{a:.3f}", (xi, a), textcoords="offset points",
                    xytext=(0, 8 if i == 0 else -14), ha="center", fontsize=7,
                    color="#0D6B6E" if i == 0 else "#A8442B")
ax.set_xticks(x)
ax.set_xticklabels(["intake\nonly", "+ time", "+ service\nlayer", "+ CI\nlayer"],
                   fontsize=8)
ax.set_ylabel("AUC")
ax.set_ylim(0.53, 0.80)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.annotate("", xy=(2, 0.775), xytext=(1, 0.775),
            arrowprops=dict(arrowstyle="<->", color="#0D6B6E", lw=1.1))
ax.text(1.5, 0.782, "service layer carries the gain", ha="center", fontsize=7.5,
        color="#0D6B6E")
ax.annotate("", xy=(3, 0.545), xytext=(2, 0.545),
            arrowprops=dict(arrowstyle="<->", color="#A8442B", lw=1.1))
ax.text(2.5, 0.534, "CI layer adds 10-27%", ha="center", fontsize=7.5,
        color="#A8442B")
fig.savefig(FIGURES / "fig6_layer_decomposition.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 7
tl = pd.read_csv(RESULTS / "e3b_two_layer.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.1))
for key, col, lbl in [("CI layer", "#A8442B", "CI layer only (service held at 99.6%)"),
                      ("service + CI", "#0D6B6E", "service + CI together")]:
    s = tl[tl.layer.str.startswith(key)].sort_values("rate")
    ax.plot(s.rate * 100, s.auc, "-o", ms=4, lw=1.7, color=col, label=lbl)
ax.axvline(65, color="#7A6112", lw=1, ls="-.")
ax.annotate("CSDM 'Walk'\n(practitioner anchor, 65%)", (65, 0.60), fontsize=7,
            color="#7A6112", ha="center", xytext=(0, -4),
            textcoords="offset points")
ax.set_xlabel("population rate of the degraded layer (%)")
ax.set_ylabel("AUC, misrouting")
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.savefig(FIGURES / "fig7_two_layer_degradation.png")
plt.close(fig)
print("added fig6, fig7")

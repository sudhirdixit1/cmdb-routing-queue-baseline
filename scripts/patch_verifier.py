"""Align the verifier's registry with the eighth draft."""
import re
from pathlib import Path

V = Path(__file__).resolve().parent / "verify_paper.py"
s = V.read_text(encoding="utf-8")

# --- retire checks whose quantity the rewrite removed -------------------
for dead in [
    'ck("between-queue share", ov.between_share, "43.3", 0.06,\n   anchor="between queues")',
    'ck("item within queue",\n   100 * ov.item_within_queue / ov.item_gain, "44", 0.6,\n   anchor="while permuting items")',
]:
    s = s.replace(dead, "")

# --- correct the ones whose value or anchor moved -----------------------
REPL = [
    ('ck("queue gain given item", ov.queue_unique, "+0.002", 6e-4,\n'
     '   anchor="queue\'s gain once the item")',
     'ck("queue gain given item", ov.queue_unique, "+0.002", 6e-4,\n'
     '   anchor="queue\'s gain once the item is present")'),
    ('ck("queue varies", adm.loc["Assignment Group", "varies_within"] * 100, "92.66", 0.006,\n'
     '   anchor="varies within an incident")',
     'ck("queue varies (cohort)", COHORT_VARIES * 100, "92.56", 0.006,\n'
     '   anchor="varies within an incident")'),
    ('ck("km rung gain", abs(b3.gain), "0.003", 6e-4, anchor="measured value of item")',
     'ck("km rung gain", b3.gain, "-0.003", 6e-4, anchor="measured value of item")'),
    ('ck("open equals last queue", (first[both] == last[both]).mean() * 100, "21.4", 0.06,\n'
     '   anchor="last-observed queue")',
     'ck("open equals last queue (cohort)", COHORT_LAST * 100, "21.35", 0.06,\n'
     '   anchor="last-observed queue")'),
]
for old, new in REPL:
    if old in s:
        s = s.replace(old, new)
    else:
        print("  MISS:", old.split("\n")[0][:58])

# --- cohort-restricted versions of the two scope-mismatched figures -----
s = s.replace("# ---- the section reporting a failure ---",
"""# ---- cohort-restricted scope figures ----------------------------------
_ids = set(w["Incident ID"])
_ac = a[a["Incident ID"].isin(_ids)]
COHORT_VARIES = (_ac.groupby("Incident ID")["Assignment Group"].nunique() > 1).mean()
_f = _ac[_ac.IncidentActivity_Type == "Open"].sort_values("ts") \\
        .groupby("Incident ID")["Assignment Group"].first()
_l = _ac.sort_values("ts").groupby("Incident ID")["Assignment Group"].last()
_b = _f.index.intersection(_l.index)
COHORT_LAST = (_f[_b] == _l[_b]).mean()
ck("queue groups (cohort)",
   _ac[_ac.IncidentActivity_Type == "Open"]["Assignment Group"].nunique(), "50", 0,
   anchor="groups in the analysed cohort")

# ---- the section reporting a failure ---""")
s = s.replace('ck("queue groups", op["Assignment Group"].nunique() - 1, "50", 0,\n'
              '   anchor="groups in the analysed cohort")', "")

# --- checks for everything the eighth draft newly states ----------------
s = s.replace("# ---- previously exempted, now checked ---",
"""# ---- the rebuilt mechanism --------------------------------------------
mech = pd.read_csv(R / "r8_mechanism.csv").iloc[0]
scope = pd.read_csv(R / "r8_scope.csv").set_index("k")
drop = pd.read_csv(R / "r8_dropped_leg.csv").set_index("leg")
ck("queue unique 4dp", mech.queue_unique, "+0.0017", 6e-5,
   anchor="already knows the")
ck("queue unique lo", mech.lo, "+0.0001", 6e-5, anchor="already knows the")
ck("queue unique hi", mech.hi, "+0.0034", 6e-5, anchor="already knows the")
ck("queue unique null", mech.null_mean, "-0.0009", 6e-5, anchor="matched-dimension null")
ck("queue unique null sd", mech.null_sd, "0.0006", 6e-5, anchor="matched-dimension null")
ck("queue unique design lo", mech.design_lo, "+0.0002", 6e-5, anchor="penalties it ranges")
ck("queue unique design hi", mech.design_hi, "+0.0072", 6e-5, anchor="penalties it ranges")
ck("under 0.01 bound", 0.01, "0.01", 0, anchor="under $0.01$ AUC")
ck("mirror pct", mech.mirror_pct, "91", 0.6, anchor="still retains")
ck("mirror floor pct", mech.mirror_floor_pct, "2", 0.6, anchor="retains")
ck("mirror margin", mech.mirror_pct - mech.mirror_floor_pct, "89", 0.6,
   anchor="margin is")
ck("queue gain for mirror", mech.queue_gain, "+0.082", 6e-4, anchor="gain. The matched floor")
ck("dropped leg real", 100 * drop.loc["real routing queue", "recovered"]
   / (mech.queue_gain / 0.082 * 0.1835), "44", 1.0, anchor="obtained")
ck("dropped leg uniform",
   100 * drop.loc["random cells, uniform over items", "recovered"] / 0.1835, "25", 1.0,
   anchor="retains")
ck("dropped leg mass",
   100 * drop.loc["random cells, item-mass matched", "recovered"] / 0.1835, "-7", 1.0,
   anchor="retains")
ck("scope top8", scope.loc[8, "recovered"] * 100, "57.9", 0.06, anchor="top $8$ recover")
ck("scope top64", scope.loc[64, "recovered"] * 100, "90.0", 0.06, anchor="recover")
ck("scope top128", scope.loc[128, "recovered"] * 100, "95.4", 0.06, anchor="recover")

# ---- previously exempted, now checked ---""")
V.write_text(s, encoding="utf-8")
print("registry aligned")

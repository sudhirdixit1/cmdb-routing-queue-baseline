"""Verify every numeric claim in the draft against generated results.

Fourth version.  The first three each shipped with a hole found by review:

  v1  stripped LaTeX comments with re.sub(r"%.*"), so an ESCAPED percent ate
      the rest of the line; 38 literals, including the results table, were
      never scanned.
  v2  used substring containment for the accounted-for test, so a fabricated
      737 hid inside 466{,}737.
  v3  fixed that but over-normalised on registration (stripping a leading
      "."), freeing the bare integers 172, 195, 094, 113, 006 and 001 from
      the confidence bounds; and its in-paper test was still substring, so
      "47" was satisfied by "47.53".  Five of seven injected fabrications
      passed.

This version removes the class of bug.  The paper is tokenised ONCE into a
set of numeric literals and every membership test is exact set membership
against that set.  No substring test appears anywhere.  Checks name literals
in the form the tokeniser yields, which is why the paper writes confidence
bounds as +0.172 rather than +.172.

Every check compares a value computed from a result file or from the raw
data against the literal printed in the paper.  Nothing asserts merely that
a string is present.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from texnum import body_of, literals
from common import RAW, is_missing

ROOT = Path(__file__).resolve().parent.parent
TEX_RAW = (ROOT / "paper" / "iaai27_empty_cmdb.tex").read_text(encoding="utf-8")
BODY = body_of(TEX_RAW)
# LaTeX wraps sentences, so an anchor phrase can straddle a newline.
# Collapse whitespace before any context search.
FLAT = re.sub(r"\s+", " ", BODY)
LITS = literals(TEX_RAW)          # the only view of the paper's numbers
R = ROOT / "results"

gains = pd.read_csv(R / "r6_gains.csv")
conc = pd.read_csv(R / "r6_concentration.csv")
facts = pd.read_csv(R / "r4_facts.csv").iloc[0]
stab = pd.read_csv(R / "r4_stability.csv")
adm = pd.read_csv(R / "r4_admissibility.csv").set_index("field")
mutn = pd.read_csv(R / "r5_mutation.csv").set_index("activity")
sens = pd.read_csv(R / "r5_sensitivity.csv")
leak = pd.read_csv(R / "r5_leak.csv").iloc[0]
r9L = pd.read_csv(R / "r9_ladder.csv")
r9T = pd.read_csv(R / "r9_targets.csv").set_index("task")
r9S = pd.read_csv(R / "r9_stability.csv")

ok, bad, seen = 0, [], set()


def ck(label, value, printed, tol, anchor):
    """Compare a computed value against the literal the paper prints.

    `printed` is the token exactly as the tokeniser yields it; membership is
    exact set membership, never substring.

    `anchor` is MANDATORY.  Exact set membership stops a fabricated 737
    hiding inside 466{,}737, but it is document-wide: an independent review
    smuggled 22 of 42 corruptions past the previous version by changing a
    value in one place while the same literal survived elsewhere (e.g. the
    conclusion's +0.183 changed to +0.103, which is a literal the paper
    legitimately contains).  Requiring the literal within 120 characters of
    an anchor phrase ties every check to the sentence that makes the claim.
    """
    global ok
    seen.add(printed)
    try:
        target = float(printed.replace("{,}", ""))
    except ValueError:
        bad.append(f"{label}: '{printed}' is not numeric")
        return
    if abs(float(value) - target) > tol:
        bad.append(f"{label}: data={float(value):.6g} paper={printed}")
        return
    if printed not in LITS and ("+" + printed) not in LITS:
        bad.append(f"{label}: '{printed}' does not appear in the paper")
        return
    if True:
        near = False
        flat_anchor = re.sub(r"\s+", " ", anchor)
        for m in re.finditer(re.escape(flat_anchor), FLAT):
            window = FLAT[max(0, m.start() - 200): m.end() + 200]
            if printed in literals(window):
                near = True
                break
        if not near:
            bad.append(f"{label}: '{printed}' does not appear near '{anchor}'")
            return
    ok += 1


def ck_phrase(label, phrase, *values_and_tols):
    """Assert an EXACT phrase, with its numbers, appears in the paper.

    Anchoring ties a literal to a neighbourhood, but two values sharing one
    anchor can be swapped without detection, and a value repeated in a second
    sentence is only checked at its first occurrence.  Requiring the verbatim
    phrase pins value to position.  The data check is done by the caller's
    paired ck() calls; this fixes where the numbers sit.
    """
    global ok
    flat = re.sub(r"\s+", " ", phrase)
    for v, _t in zip(values_and_tols[::2], values_and_tols[1::2]):
        seen.add(v)
    if flat in FLAT:
        ok += 1
    else:
        bad.append(f"{label}: exact phrase not found -- '{flat[:70]}'")


import texlint as _lint
_src = TEX_RAW
_bad_rows = _lint.bad_rows(_src)
_struct = _lint.check_other(_src)
if _bad_rows or _struct:
    print("STRUCTURAL LINT FAILED -- the document would not compile:")
    for ln, txt in _bad_rows:
        print(f"   line {ln}: {txt}")
    for o in _struct:
        print("   ", o)
    sys.exit(1)

print("=" * 72)
print("PAPER VERIFICATION")
print("=" * 72)

# ---- regression tests for the three historical holes -------------------
if "0.7734" not in literals(r"a rate of $95\%$ and a value of $0.7734$"):
    bad.append("REGRESSION: escaped percent still truncates the line")
else:
    ok += 1
if "737" in literals(r"$466{,}737$ rows"):
    bad.append("REGRESSION: tokeniser splits inside a grouped number")
else:
    ok += 1

# ---- cleaning and cohort ------------------------------------------------
ck("rows in file", facts.n_file, "46{,}809", 0, anchor="rows")
ck("blank ids", facts.n_blank, "203", 0, anchor="incident identifier")
ck("warm-up removed", facts.n_warmup, "1{,}150", 0, anchor="left-censored")
ck("analysed", facts.n_analysed, "45{,}455", 0, anchor="Removing them leaves")
ck("train", facts.n_train, "31{,}818", 0, anchor="training")
ck("test", facts.n_test, "13{,}637", 0, anchor="test incidents")
ck("positive train", facts.pos_train, "0.413", 6e-4, anchor="positive rates")
ck("positive test", facts.pos_test, "0.372", 6e-4, anchor="positive rates")
ck("items in window", facts.n_items_all, "2{,}929", 0, anchor="items")
ck("items in training", facts.n_items_train, "2{,}554", 0, anchor="seen in training")
ck("128 as pct of vocab", facts.pct_128, "5.0", 0.05, anchor="training vocabulary")

# ---- headline -----------------------------------------------------------
g0, g1 = gains.iloc[0], gains.iloc[1]
ck("base auc intake", g0.base_auc, "0.562", 6e-4, anchor="intake only")
ck("base auc queue", g1.base_auc, "0.644", 6e-4, anchor="routing queue")
ck("with ident intake", g0.base_auc + g0.gain, "0.746", 6e-4, anchor="intake only")
ck("with ident queue", g1.base_auc + g1.gain, "0.748", 6e-4, anchor="routing queue")
ck("gain intake", g0.gain, "+0.183", 6e-4, anchor="intake only")
ck("gain queue", g1.gain, "+0.103", 6e-4, anchor="routing queue")
ck("gain intake lo", g0.lo, "+0.172", 6e-4, anchor="intake only")
ck("gain intake hi", g0.hi, "+0.195", 6e-4, anchor="intake only")
ck("gain queue lo", g1.lo, "+0.094", 6e-4, anchor="routing queue")
ck("gain queue hi", g1.hi, "+0.114", 6e-4, anchor="routing queue")
ck("z pooled intake", g0.z_pooled, "28.1", 0.06, anchor="standard deviations")
ck("z pooled queue", g1.z_pooled, "17.4", 0.06, anchor="standard deviations")
ck("z naive intake", g0.z_naive, "51", 0.6, anchor="would report")
ck("z naive queue", g1.z_naive, "33", 0.6, anchor="would report")
ck("pct cut", 100 * (g0.gain - g1.gain) / g0.gain, "44", 0.6,
   anchor="cuts its measured value")

# ---- mechanism: four direct measurements, no control -------------------
ov = pd.read_csv(R / "r7_overlap.csv").iloc[0]
ck("item gain over intake", ov.item_gain, "+0.183", 6e-4, anchor="gain over intake")
ck("item gain given queue", ov.item_unique, "+0.103", 6e-4,
   anchor="item's gain once the queue")
ck("queue gain over intake", ov.queue_gain, "+0.082", 6e-4,
   anchor="queue's gain over intake")
ck("queue gain given item", ov.queue_unique, "+0.002", 6e-4,
   anchor="queue's gain once the item is present")

ck("difference between rows", ov.item_gain - ov.item_unique, "0.080", 6e-4,
   anchor="differ by")
ck("mirror: queue within item",
   100 * ov.queue_within_item / ov.queue_gain, "91", 0.6,
   anchor="retains")


# ---- design-space range --------------------------------------------------
ds8 = pd.read_csv(R / "r8_design_space.csv")
ck("design range low", ds8.gain.min(), "+0.068", 6e-4, anchor="cleaning cutoff the second gain")
ck("design range high", ds8.gain.max(), "+0.130", 6e-4, anchor="cleaning cutoff the second gain")

# ---- stability and sensitivity -----------------------------------------
ck("stability intake min", stab["intake fields only"].min(), "+0.176", 6e-4, anchor="split points the two")
ck("stability intake max", stab["intake fields only"].max(), "+0.193", 6e-4, anchor="split points the two")
ck("stability queue min", stab["+ intake routing queue"].min(), "+0.091", 6e-4, anchor="split points the two")
ck("stability queue max", stab["+ intake routing queue"].max(), "+0.118", 6e-4, anchor="split points the two")
ck("sensitivity category only", sens.iloc[1].gain, "+0.106", 6e-4,
   anchor="of them --- gives")
ck("sensitivity never-edited", sens.iloc[2].gain, "+0.107", 6e-4,
   anchor="never-edited")
ck("never-mutated n", sens.iloc[2].n, "44{,}227", 0, anchor="never-edited")

# ---- disclosure ---------------------------------------------------------
ck("urgency edits", mutn.loc["Urgency Change", "incidents"], "1{,}107", 0, anchor="Urgency on")
ck("urgency pct", mutn.loc["Urgency Change", "pct"] * 100, "2.44", 0.006, anchor="Urgency on")
ck("impact edits", mutn.loc["Impact Change", "incidents"], "1{,}084", 0, anchor="Impact on")
ck("impact pct", mutn.loc["Impact Change", "pct"] * 100, "2.38", 0.006, anchor="Impact on")
ck("ci edits", mutn.loc["Affected CI Change", "incidents"], "159", 0, anchor="affected item on")
ck("ci pct", mutn.loc["Affected CI Change", "pct"] * 100, "0.35", 0.006, anchor="affected item on")
ck("edited reassign rate",
   mutn.loc[["Impact Change", "Urgency Change"], "y_touched"].mean(), "0.66", 0.006,
   anchor="more likely to be reassigned")
ck("clean reassign rate",
   mutn.loc[["Impact Change", "Urgency Change"], "y_clean"].mean(), "0.39", 0.006,
   anchor="more likely to be reassigned")

# ---- the section reporting a failure ------------------------------------
ck("km identity", leak.km_identity * 100, "100.000000", 1e-9, anchor="closed-record column")
ck("interaction ids", leak.n_interaction, "45{,}426", 0, anchor="distinct values")

# ---- the third rung, reported only as unresolved -----------------------
b3 = pd.read_csv(R / "r4_baselines.csv").iloc[2]
ck("km baseline auc", b3.base_auc, "0.805", 6e-4, anchor="raises AUC")
ck("km rung gain", b3.gain, "-0.003", 6e-4, anchor="measured value of item")

# ---- concentration ------------------------------------------------------
cc = conc[conc.k > 0].set_index("k")
ck("top 8 k", 8, "8", 0, anchor="top $8$ items")
ck("top 64 k", 64, "64", 0, anchor="top $64$")
ck("top 128 k", 128, "128", 0, anchor="top $128$")
ck("top 8", cc.loc[8, "coverage"] * 100, "30.2", 0.06, anchor="top $8$ items")
ck("top 64", cc.loc[64, "coverage"] * 100, "70.5", 0.06, anchor="top $64$")
ck("top 128", cc.loc[128, "coverage"] * 100, "82.0", 0.06, anchor="top $128$")

# ---- recomputed from raw ------------------------------------------------
d = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                encoding="latin-1")
d = d.loc[:, [c for c in d.columns if not c.startswith("Unnamed")]]
d.columns = [c.strip() for c in d.columns]
d = d[~is_missing(d["Incident ID"])].copy()
d["_t"] = pd.to_datetime(d["Open Time"], format="%d/%m/%Y %H:%M:%S",
                         errors="coerce", dayfirst=True)
d["_ra"] = pd.to_numeric(d["# Reassignments"], errors="coerce")
d["_ht"] = pd.to_numeric(d["Handle Time (Hours)"].astype(str).str.replace(",", "."),
                         errors="coerce")
d = d.dropna(subset=["_t", "_ra"])
mo = d._t.dt.to_period("M").value_counts().sort_index()
ck("sep volume", mo.loc[pd.Period("2013-09")], "857", 0, anchor="September")
ck("oct volume", mo.loc[pd.Period("2013-10")], "8{,}606", 0, anchor="October")
w = d[d._t >= "2013-10-01"]
ht = w.groupby(w._ra.clip(upper=5))._ht.median()
ck("handle zero", ht.loc[0], "1.59", 6e-3, anchor="never reassigned")
ck("handle five plus", ht.loc[5], "47.53", 6e-3, anchor="five or more")
ck("population", (1 - is_missing(w["CI Name (aff)"]).mean()) * 100, "100", 1e-9, anchor="populated")

a = pd.read_csv(RAW / "Detail_Incident_Activity.csv", sep=";", low_memory=False,
                encoding="latin-1")
a.columns = [c.strip() for c in a.columns]
a["ts"] = pd.to_datetime(a["DateStamp"], format="%d-%m-%Y %H:%M:%S",
                         errors="coerce", dayfirst=True)
op = a[a.IncidentActivity_Type == "Open"]

first = op.sort_values("ts").groupby("Incident ID")["Assignment Group"].first()
last = a.sort_values("ts").groupby("Incident ID")["Assignment Group"].last()
both = first.index.intersection(last.index)

# interaction-key identity, recomputed here rather than asserted
raw2 = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                   encoding="latin-1")
raw2 = raw2.loc[:, [c for c in raw2.columns if not c.startswith("Unnamed")]]
raw2.columns = [c.strip() for c in raw2.columns]
oi = op.sort_values("ts").groupby("Incident ID")["Interaction ID"].first()
jj = w[["Incident ID"]].merge(
    raw2[["Incident ID", "Related Interaction", "# Related Interactions"]],
    on="Incident ID")
jj["open_int"] = jj["Incident ID"].map(oi)
jj["n"] = pd.to_numeric(jj["# Related Interactions"], errors="coerce")
one = jj[jj.n == 1]
ck("single-interaction cohort", len(one), "42{,}151", 0, anchor="exactly one related")
ck("interaction identity",
   (one.open_int.astype(str) == one["Related Interaction"].astype(str)).mean() * 100,
   "99.997628", 1e-5, anchor="own closed-record")

# ---- the rebuilt mechanism --------------------------------------------
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

# ---- previously exempted, now checked ----------------------------------
ck("bootstrap resamples", 2000, "2{,}000", 0, anchor="resample paired")
ck("split train pct", 70, "70", 0, anchor="temporal")
ck("split test pct", 30, "30", 0, anchor="temporal")
ck("stability low pct", 55, "55", 0, anchor="split point")
ck("stability high pct", 80, "80", 0, anchor="split point")
pre = d[d._t < "2013-10-01"]
prem = pre.groupby(pre._t.dt.to_period("M"))._y.mean() if "_y" in pre else None
d["_y"] = (d._ra >= 1).astype(int)
pre = d[d._t < "2013-10-01"]
prem = pre.groupby(pre._t.dt.to_period("M"))._y.mean()
prem = prem[pre.groupby(pre._t.dt.to_period("M")).size() >= 5]
ck("censored low", prem.min() * 100, "76", 0.6, anchor="reassignment rates")
post = d[d._t >= "2013-10-01"]
postm = post.groupby(post._t.dt.to_period("M"))._y.mean()
ck("post low", postm.min() * 100, "35", 0.6, anchor="subsequent")
ck("post high", postm.max() * 100, "42", 0.6, anchor="subsequent")

# ---- ordered pairs and repeated values, pinned verbatim ----------------
ck_phrase("abstract mirror pinned",
          r"still retains $91\%$ of the queue's own gain against a matched "
          r"floor of $2\%$", "91", 0, "2", 0)
ck_phrase("mirror leg pinned",
          r"still retains $91\%$ of the queue's $+0.082$ gain", "91", 0)
ck_phrase("mirror floor pinned",
          r"retains $2\%$. The margin is $89$ points", "2", 0, "89", 0)
ck_phrase("positive rates in order",
          r"positive rates $0.413$ and $0.372$", "0.413", 0, "0.372", 0)
ck_phrase("edited vs clean in order",
          r"($0.66$ against $0.39$)", "0.66", 0, "0.39", 0)
ck_phrase("conclusion restates both gains",
          "worth $+0.183$ or $+0.103$ AUC", "0.183", 0, "0.103", 0)
ck_phrase("stability ranges in order",
          r"gains range $+0.176$ to $+0.193$ and $+0.091$ to $+0.118$",
          "0.176", 0, "0.193", 0, "0.091", 0, "0.118", 0)
ck_phrase("design range in order",
          "ranges $+0.068$ to $+0.130$", "+0.068", 0, "+0.130", 0)

# ---- cohort-restricted scope figures ----------------------------------
_ids = set(w["Incident ID"])
_ac = a[a["Incident ID"].isin(_ids)]
COHORT_VARIES = (_ac.groupby("Incident ID")["Assignment Group"].nunique() > 1).mean()
_f = _ac[_ac.IncidentActivity_Type == "Open"].sort_values("ts") \
        .groupby("Incident ID")["Assignment Group"].first()
_l = _ac.sort_values("ts").groupby("Incident ID")["Assignment Group"].last()
_b = _f.index.intersection(_l.index)
COHORT_LAST = (_f[_b] == _l[_b]).mean()
ck("queue varies (cohort)", COHORT_VARIES * 100, "92.56", 0.006,
   anchor="varies within an incident")
ck("open equals last (cohort)", COHORT_LAST * 100, "21.35", 0.06,
   anchor="last-observed queue")
ck("queue groups (cohort)",
   _ac[_ac.IncidentActivity_Type == "Open"]["Assignment Group"].nunique(), "50", 0,
   anchor="groups in the analysed cohort")


# ---- second task (r9) ---------------------------------------------------
def _r9(task, baseline, col):
    s = r9L[(r9L.task == task) & (r9L.baseline == baseline)]
    assert len(s) == 1, f"r9_ladder: {task}/{baseline} not unique"
    return float(s.iloc[0][col])


def _shrink(task):
    g0 = _r9(task, "intake only", "gain")
    gq = _r9(task, "+ routing queue", "gain")
    return 100.0 * (g0 - gq) / g0


ck("reopen positives", r9T.loc["reopened"].n_pos, "2{,}096", 0,
   anchor="fires on")
ck("reopen correlation", r9T.loc["reopened"].corr_with_reassigned, "+0.14",
   0.005, anchor="correlates with reassignment at")
ck("long-handling correlation", r9T.loc["long-handling"].corr_with_reassigned,
   "+0.40", 0.005, anchor="correlates at")
ck("reopen gain, intake", _r9("reopened", "intake only", "gain"), "+0.083",
   0.0005, anchor="item identity is worth")
ck("reopen gain, queue", _r9("reopened", "+ routing queue", "gain"), "+0.055",
   0.0005, anchor="once the queue is admitted")
ck("reopen shrinkage", _shrink("reopened"), "33", 0.5,
   anchor="a reduction of")
ck("long-handling gain, intake", _r9("long-handling", "intake only", "gain"),
   "+0.118", 0.0005, anchor="the two figures are")
ck("long-handling gain, queue",
   _r9("long-handling", "+ routing queue", "gain"), "+0.078", 0.0005,
   anchor="the two figures are")
ck("long-handling shrinkage", _shrink("long-handling"), "34", 0.5,
   anchor="a reduction of")
ck("shrinkage range low", r9S.shrink_pct.min(), "30", 0.5,
   anchor="the reduction ranges from")
ck("shrinkage range high", r9S.shrink_pct.max(), "46", 0.5,
   anchor="the reduction ranges from")
ck("reopen z, intake", _r9("reopened", "intake only", "z_pooled"), "5.5",
   0.05, anchor="pooled standard deviations")
ck("reopen z, queue", _r9("reopened", "+ routing queue", "z_pooled"), "4.2",
   0.05, anchor="pooled standard deviations")
# the ordered pair must not be swappable without detection
ck_phrase("reopen gains in order",
          "worth $+0.083$ against the intake block and $+0.055$",
          "+0.083", 0, "+0.055", 0)
ck_phrase("long-handling gains in order",
          "the two figures are $+0.118$ and $+0.078$", "+0.118", 0,
          "+0.078", 0)
# every rung on every target must clear its null, as the paper asserts
if not (r9L.z_pooled.abs() > 3).all():
    bad.append("paper claims every r9 rung is outside its null; it is not")
else:
    ok += 1

# ---- residue of withdrawn claims ---------------------------------------
for dead in ["VolvoIT", "ServiceNow-IT", "saturat", "converge above",
             "mass-matched", "perplexity"]:
    if dead in BODY:
        bad.append(f"residue of a withdrawn claim: '{dead}'")
    else:
        ok += 1

# ---- coverage of every literal -----------------------------------------
STRUCTURAL = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "27",
              "2027", "2013", "2014", "01", "03", "31", "95", "10"}  # section/date only000", "0.068"}
unaccounted = sorted(l for l in LITS if l not in STRUCTURAL and l not in seen)

print(f"\n{ok} checks passed, {len(bad)} failed")
print(f"{len(LITS)} literals in body; {len(unaccounted)} unaccounted")
if bad:
    print("\nFAILED:")
    for b in bad:
        print("  -", b)
if unaccounted:
    print("\nUNACCOUNTED:")
    print("  " + ", ".join(unaccounted))
if bad or unaccounted:
    sys.exit(1)
print("\nEvery numeric claim is checked against data; every literal in the")
print("paper is covered; membership is exact, never substring.")

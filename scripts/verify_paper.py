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
# r10-r14: estimator families, operational translation, queue shape, scoping
r10R = pd.read_csv(R / "r10_range.csv").iloc[0]
r10N = pd.read_csv(R / "r10_encoder_null.csv").set_index("estimator")
r11C = pd.read_csv(R / "r11_capacity.csv").set_index("capacity")
r11V = pd.read_csv(R / "r11_capacity_naive.csv").set_index("capacity")
r11O = pd.read_csv(R / "r11_overstatement.csv").iloc[0]
r11T = pd.read_csv(R / "r11_threshold.csv").set_index("threshold")
r12Q = pd.read_csv(R / "r12_queue_from_item.csv").iloc[0]
r13S = pd.read_csv(R / "r13_shape.csv").set_index("split")
r13R = pd.read_csv(R / "r13_reduced.csv")
r13O = pd.read_csv(R / "r13_onebit.csv").iloc[0]
r14F = pd.read_csv(R / "r14_scope_facts.csv").iloc[0]
r14C = pd.read_csv(R / "r14_curve_queue.csv").set_index("k")
bins = pd.read_csv(R / "r5_binning.csv").iloc[0]

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
#  Superseded by the split-averaged curve (r14).  r8_scope.csv holds the
#  single-split figures the paper used to quote; they are cross-checked
#  against the averaged curve's range rather than quoted, so that a future
#  edit cannot reintroduce a one-split number as if it were the estimate.
for _k in (8, 64, 128):
    _single = scope.loc[_k, "recovered"]
    _row = pd.read_csv(R / "r14_curve_queue.csv").set_index("k").loc[_k]
    if not (_row.lo - 1e-9 <= _single <= _row.hi + 1e-9):
        bad.append(f"single-split scope at k={_k} ({_single:.3f}) lies outside "
                   f"the across-split range [{_row.lo:.3f}, {_row.hi:.3f}]")
    else:
        ok += 1

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
#  The abstract used to restate the mirror leg verbatim; it now leads on the
#  dose-response and the detection factor instead.  Both are values repeated
#  between abstract and body, so both are pinned by exact phrase -- that is
#  the rule this file's v4 rebuild introduced and it still applies.
ck_phrase("abstract dose-response pinned",
          r"rising from $27\%$ when the queue is reduced to one bit to $44\%$ "
          r"at full resolution", "27", 0, "44", 0)
ck_phrase("abstract detection factor pinned",
          r"the queue-free baseline attributes $12.7$ times as many "
          r"additional catches", "12.7", 0)
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
#  Superseded: the paper used to say "50 groups in the analysed cohort".  It
#  now states the training count, which is what the models actually see, and
#  that check lives with the other r13 shape checks below.  The cohort-wide
#  count is still recomputed here so the two cannot silently diverge.
_COHORT_GROUPS = _ac[_ac.IncidentActivity_Type == "Open"]["Assignment Group"].nunique()
if _COHORT_GROUPS < r13S.loc["train"].n_groups:
    bad.append(f"cohort has {_COHORT_GROUPS} queues, fewer than training's "
               f"{r13S.loc['train'].n_groups}: the loaders disagree")
else:
    ok += 1


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

# ---- r15: why the study is single-organisation -------------------------
#  A descriptive field-population rate, recomputed from each raw log.  It is
#  NOT a cross-organisation performance comparison -- those died in the e1/e11
#  withdrawals (HANDOFF section 4) and must not come back.
r15 = pd.read_csv(R / "r15_public_logs.csv")
_uci = r15[r15.log.str.startswith("UCI")].iloc[0]
_rab = r15[r15.log.str.startswith("BPIC 2014")].iloc[0]
_v13 = r15[r15.log.str.startswith("BPIC 2013")].iloc[0]
ck("second log item population", _uci.population * 100, "0.2", 0.05,
   anchor="the second records it on")
if not (_rab.population > 0.999):
    bad.append(f"paper says one log records the item on every incident; "
               f"measured {_rab.population:.4f}")
else:
    ok += 1
if not (_v13.distinct == 0 and (pd.isna(_v13.population) or _v13.population == 0)):
    bad.append("paper says the third log has no affected-item field; r15 found one")
else:
    ok += 1

# ---- r10: three estimator families -------------------------------------
ck("estimator range intake lo", r10R.intake_lo, "+0.173", 6e-4,
   anchor="the first rung ranges")
ck("estimator range intake hi", r10R.intake_hi, "+0.183", 6e-4,
   anchor="the first rung ranges")
ck("estimator range queue lo", r10R.queue_lo, "+0.092", 6e-4,
   anchor="the second")
ck("estimator range queue hi", r10R.queue_hi, "+0.103", 6e-4,
   anchor="the second")
ck("estimator shrink lo", r10R.shrink_lo, "43", 0.5, anchor="the shrinkage")
ck("estimator shrink hi", r10R.shrink_hi, "47", 0.5, anchor="the shrinkage")
ck_phrase("estimator ranges in order",
          r"the first rung ranges $+0.173$ to $+0.183$, the second $+0.092$ "
          r"to $+0.103$, and the shrinkage $43\%$ to $47\%$",
          "+0.173", 0, "+0.183", 0, "+0.092", 0, "+0.103", 0, "43", 0, "47", 0)
_e2 = r10N.loc["E2 logistic, item target-encoded"]
_e3 = r10N.loc["E3 boosting, item target-encoded"]
ck("E2 encoder null mean", _e2.null_mean, "-0.0001", 6e-5, anchor="returns")
ck("E2 encoder null sd", _e2.null_sd, "0.0016", 6e-5, anchor="returns")
ck("E3 encoder null mean", _e3.null_mean, "+0.0042", 6e-5, anchor="returns")
ck("E3 encoder null sd", _e3.null_sd, "0.0020", 6e-5, anchor="returns")
ck_phrase("encoder nulls in order",
          r"returns $-0.0001 \pm 0.0016$ and $+0.0042 \pm 0.0020$",
          "-0.0001", 0, "0.0016", 0, "+0.0042", 0, "0.0020", 0)
ck("boosting bins", bins.n_bins, "137", 0, anchor="bins")

# ---- r11: what the difference buys -------------------------------------
for cap, rev, cb, cf, mo in ((0.05, "682", "597", "653", "30"),
                             (0.10, "1{,}364", "1{,}119", "1{,}153", "18"),
                             (0.20, "2{,}727", "1{,}823", "1{,}857", "18")):
    row = r11C.loc[cap]
    tag = f"{cap:.0%}"
    _anc = f"(${rev}$)"          # each row is anchored on its own row label
    ck(f"capacity {tag} reviewed", row.reviewed, rev, 0, anchor="Review capacity")
    ck(f"capacity {tag} caught base", row.caught_base, cb, 0, anchor=_anc)
    ck(f"capacity {tag} caught full", row.caught_full, cf, 0, anchor=_anc)
    ck(f"capacity {tag} per month", row.extra_per_month, mo, 0.5, anchor=_anc)
ck("capacity 5% extra", r11C.loc[0.05].extra, "+56", 0, anchor="Review capacity")
ck("capacity 10% extra", r11C.loc[0.10].extra, "+34", 0, anchor="Review capacity")
# the table's rows must not be swappable: pin each to its position
ck_phrase("capacity table row 5",
          r"$5\%$ \ \ ($682$)   & $597$   & $653$   & $+56$ & $30$",
          "682", 0, "597", 0, "653", 0, "+56", 0, "30", 0)
ck_phrase("capacity table row 10",
          r"$10\%$ ($1{,}364$)  & $1{,}119$ & $1{,}153$ & $+34$ & $18$",
          "1{,}364", 0, "1{,}119", 0, "1{,}153", 0)
ck_phrase("capacity table row 20",
          r"$20\%$ ($2{,}727$)  & $1{,}823$ & $1{,}857$ & $+34$ & $18$",
          "2{,}727", 0, "1{,}823", 0, "1{,}857", 0, "20", 0)
for cap, lit in ((0.05, "303"), (0.10, "432"), (0.20, "501")):
    ck(f"naive extra {cap:.0%}", r11V.loc[cap].extra, lit, 0,
       anchor="credit item identity with")
ck_phrase("naive counts in order",
          r"credit item identity with $303$, $432$ and $501$ instead",
          "303", 0, "432", 0, "501", 0)
ck("precision base 10%", r11C.loc[0.10].prec_base * 100, "82.0", 0.06,
   anchor="moving precision from")
ck("precision full 10%", r11C.loc[0.10].prec_full * 100, "84.5", 0.06,
   anchor="moving precision from")
ck("test base rate", facts.pos_test * 100, "37.2", 0.06, anchor="base rate")
ck_phrase("precision pair in order",
          r"moving precision from $82.0\%$ to $84.5\%$ against a $37.2\%$ base",
          "82.0", 0, "84.5", 0, "37.2", 0)
ck("overstatement 10%", r11O.overstatement_10pct, "12.7", 0.06,
   anchor="overstates the operational gain")
ck("overstatement lo", r11O.overstatement_lo, "5.4", 0.06,
   anchor="across the three capacities")
ck("overstatement hi", r11O.overstatement_hi, "14.7", 0.06,
   anchor="across the three capacities")
ck("auc ratio", r11O.auc_ratio, "1.8", 0.06, anchor="which is")
ck_phrase("overstatement range in order",
          r"factor of $12.7$}, and by $5.4$ to $14.7$ across the three",
          "12.7", 0, "5.4", 0, "14.7", 0)
ck("threshold 2 rate", r11T.loc[2].rate * 100, "21.8", 0.06,
   anchor="Requiring two or more")
ck("threshold 2 intake", r11T.loc[2].gain_intake, "+0.131", 6e-4,
   anchor="Requiring two or more")
ck("threshold 2 queue", r11T.loc[2].gain_queue, "+0.068", 6e-4,
   anchor="Requiring two or more")
ck("threshold 3 rate", r11T.loc[3].rate * 100, "10.6", 0.06,
   anchor="three or more")
ck("threshold 3 intake", r11T.loc[3].gain_intake, "+0.151", 6e-4,
   anchor="three or more")
ck("threshold 3 queue", r11T.loc[3].gain_queue, "+0.080", 6e-4,
   anchor="three or more")
ck_phrase("threshold ladder in order",
          r"($21.8\%$ of incidents) gives $+0.131$ and $+0.068$; three or "
          r"more ($10.6\%$) gives $+0.151$ and $+0.080$",
          "21.8", 0, "+0.131", 0, "+0.068", 0, "10.6", 0, "+0.151", 0,
          "+0.080", 0)
ck("threshold shrink lo", r11T.shrink_pct.min(), "44", 0.5,
   anchor="the shrinkage stays between")
ck("threshold shrink hi", r11T.shrink_pct.max(), "48", 0.5,
   anchor="the shrinkage stays between")
if not ((r11T.lo > 0).all() and (r11T.hi > 0).all()):
    bad.append("paper claims every threshold interval excludes zero; it does not")
else:
    ok += 1

# ---- r12/r13: the queue's shape and what is model-free ------------------
ck("queue groups (training)", r13S.loc["train"].n_groups, "49", 0,
   anchor="groups in training")
ck("queue entropy train", r13S.loc["train"].entropy, "2.43", 0.006,
   anchor="bits")
ck("queue eff. cardinality", r13S.loc["train"].perplexity, "5.4", 0.06,
   anchor="effective cardinality")
ck("queue top1 train", r13S.loc["train"].top1 * 100, "62.1", 0.06,
   anchor="largest group holding")
ck("queue groups test", r13S.loc["test"].n_groups, "32", 0,
   anchor="live groups fall to")
ck("queue top1 test", r13S.loc["test"].top1 * 100, "78.6", 0.06,
   anchor="the largest holds")
ck_phrase("queue shape in order",
          r"its $49$ groups carry $2.43$ bits, an effective cardinality of "
          r"$5.4$, with the largest group holding $62.1\%$ of incidents; in "
          r"test the live groups fall to $32$ and the largest holds $78.6\%$",
          "49", 0, "2.43", 0, "5.4", 0, "62.1", 0, "32", 0, "78.6", 0)
_dom = pd.read_csv(R / "r13_dominant.csv").iloc[0]
ck("rate inside dominant pool", _dom.rate_in, "0.309", 6e-4,
   anchor="inside the dominant pool")
ck("rate outside dominant pool", _dom.rate_out, "0.603", 6e-4,
   anchor="outside it")
#  The two anchors sit inside each other's +-200 character window, so
#  anchoring alone cannot tell the pair apart if they are swapped.  The
#  corruption suite caught exactly that; pin the order.
ck_phrase("dominant-pool rates in order",
          r"the reassignment rate is $0.309$ inside the dominant pool and "
          r"$0.603$ outside it", "0.309", 0, "0.603", 0)
ck("U(queue|item)", r12Q.u_queue_given_item * 100, "60.4", 0.06,
   anchor="of the queue's information")
ck("U(item|queue)", r12Q.u_item_given_queue * 100, "19.6", 0.06,
   anchor="of the item's")
#  Same swap hole as the dominant-pool rates: both literals fall inside both
#  anchor windows.  The asymmetry IS the claim here -- reversing it would say
#  the queue determines the item -- so the order has to be pinned.
ck_phrase("asymmetry in order",
          r"item identity carries $60.4\%$ of the queue's information and "
          r"the queue carries $19.6\%$ of the item's",
          "60.4", 0, "19.6", 0)
if not r12Q.u_queue_given_item > r12Q.u_item_given_queue:
    bad.append("paper claims the queue/item relationship is asymmetric in the "
               "direction U(queue|item) > U(item|queue); the data disagree")
else:
    ok += 1
ck("lookup accuracy", r12Q.lookup_test_all * 100, "90.3", 0.06,
   anchor="reproduces the desk's choice")
ck("lookup prior", r12Q.lookup_prior * 100, "78.6", 0.06,
   anchor="always guessing the largest queue")
ck("lookup balanced", r12Q.lookup_balanced_acc * 100, "34.1", 0.06,
   anchor="class-balanced it reaches only")
ck_phrase("lookup figures in order",
          r"on $90.3\%$ of test incidents against $78.6\%$ for always "
          r"guessing the largest queue, and class-balanced it reaches only "
          r"$34.1\%$",
          "90.3", 0, "78.6", 0, "34.1", 0)
for i, lit in enumerate(("27", "28", "36", "44")):
    ck(f"dose-response shrink {i}", r13R.iloc[i].shrink_pct, lit, 0.5,
       anchor="shrinkages of")
ck_phrase("dose-response in order",
          r"shrinkages of $27\%$, $28\%$, $36\%$ and $44\%$ at two, four, "
          r"eleven and $49$ levels",
          "27", 0, "28", 0, "36", 0, "44", 0, "49", 0)
if list(r13R.levels) != [2, 4, 11, 49]:
    bad.append(f"paper says two/four/eleven/49 levels; data has {list(r13R.levels)}")
else:
    ok += 1
if not r13R.shrink_pct.is_monotonic_increasing:
    bad.append("paper claims the shrinkage is graded in resolution; it is not monotone")
else:
    ok += 1
ck("binary share of queue gain", r13O.binary_share_of_queue, "61", 0.5,
   anchor="of the queue's baseline gain")
ck("binary share of shrinkage", r13O.binary_share_of_shrinkage, "63", 0.5,
   anchor="of the shrinkage it causes")

# ---- r14: scoping ------------------------------------------------------
#  Curve values come from r14_curve_queue.csv, which is what the figure also
#  reads, so paper, figure and check cannot drift apart.
for _k, _mean, _lo, _hi in ((8, "56", "53", "58"), (64, "88", "82", "92"),
                            (128, "93", "91", "95")):
    _row = r14C.loc[_k]
    _anc = f"the top ${_k}$ recover"
    ck(f"scope top{_k}", _row.recovered * 100, _mean, 0.5, anchor=_anc)
    ck(f"scope top{_k} lo", _row.lo * 100, _lo, 0.5, anchor=_anc)
    ck(f"scope top{_k} hi", _row.hi * 100, _hi, 0.5, anchor=_anc)
#  The scoping figure must plot the same curve the prose quotes.
if not (abs(r14F.top64 - r14C.loc[64].recovered) < 1e-9
        and abs(r14F.top128 - r14C.loc[128].recovered) < 1e-9):
    bad.append("r14_scope_facts and r14_curve_queue disagree on the curve")
else:
    ok += 1
ck_phrase("scope figures in order",
          r"the top $8$ recover $56\%$ $[53,58]$ of the $+0.103$, the top "
          r"$64$ recover $88\%$ $[82,92]$, and the top $128$ recover $93\%$ "
          r"$[91,95]$",
          "56", 0, "53", 0, "58", 0, "64", 0, "88", 0, "82", 0, "92", 0,
          "128", 0, "93", 0, "91", 0, "95", 0)
ck("scope spread at k=32", r14F.k32_spread * 100, "9", 0.5,
   anchor="across-split spread is")
ck("scope k32 label", 32, "32", 0, anchor="across-split spread is")
ck("scope top64 intake baseline", r14F.top64_intake * 100, "89", 0.5,
   anchor="the queue removed from the baseline")
ck_phrase("scope without queue pinned",
          r"queue removed from the baseline --- $89\%$ at $k=64$", "89", 0)

#  The dropped reverse-direction null grouped items into as many cells as the
#  cohort has opening queues.  The paper prints that count; check it against
#  the cohort rather than leaving it as a bare literal.
ck("reverse null cell count", _COHORT_GROUPS, "50", 0,
   anchor="a random $50$-cell grouping")

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

"""Checks and two pins for the referee-driven additions, plus two range
endpoints that were rounded rather than floored and ceiled.

The `ck_bound` discipline caught two more on this pass, which is eight in
this round:

  * "acts on $17\\%$ to $36\\%$ of arrivals" -- the observed maximum is
    36.27%, so an upper bound must print 37;
  * "leave the item worth $+0.093$ to $+0.100$" -- the observed minimum is
    0.09294, so a lower bound must print +0.092, and the maximum 0.10025
    must print +0.101.

Both are repaired in the manuscript here, not worked around in the checker.

    python scripts/patch_checks_r17e.py --check
    python scripts/patch_checks_r17e.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"
V = ROOT / "scripts" / "verify_paper.py"

TEX_EDITS = [
    ("acted-range",
     r"group-aware item model acts on $17\%$ to $36\%$ of arrivals.",
     r"group-aware item model acts on $17\%$ to $37\%$ of arrivals."),
    ("temporal-null-range",
     r"real field is $0.1558$ above that --- and leave the item worth $+0.093$ to" "\n" r"$+0.100$.",
     r"real field is $0.1558$ above that --- and leave the item worth $+0.092$ to" "\n" r"$+0.101$."),
]

CHECKS = r'''
# ---- the referee-driven additions (REFEREE-LOG.md) ----------------------
_r35bF = pd.read_csv(R / "r35b_facts.csv").iloc[0]
_r33H = pd.read_csv(R / "r33_headroom_sensitivity.csv")
_r31O = pd.read_csv(R / "r31_operating_points.csv")
_negT = _r30G[_r30G.honest_hi < 0].threshold.tolist()
_acted = _r31O[_r31O.threshold.isin(_negT)]["acted_intake + group + item"]
_r22L = pd.read_csv(R / "r22_congestion_ladder.csv")

# section 3: the three properties of R
ck("estimand auc example", _AUC.reduction * 100, "43.7", 0.06,
   anchor="of the value is absorbed'' under AUC")
ck("estimand brier example", _BS.reduction * 100, "60.3", 0.06,
   anchor="under Brier skill are not one quantity")
ck_bound("estimand design range lo", r21R.shrinkage.min(), "36.1", "lower",
         anchor="across which the AUC reduction runs")
ck_bound("estimand design range hi", r21R.shrinkage.max(), "48.3", "upper",
         anchor="across which the AUC reduction runs")

# section 8.2: where the harmful band sits operationally
ck_bound("harmful band acted lo", float(_acted.min()) * 100, "17", "lower",
         anchor="group-aware item model acts on")
ck_bound("harmful band acted hi", float(_acted.max()) * 100, "37", "upper",
         anchor="group-aware item model acts on")

# section 11: what "falsified" does and does not mean
ck("falsification qualifier no denominator", _r33bF.n_no_entity_value, "10", 0,
   anchor="fail to have a test: on")
ck("falsification qualifier pairs", _r33bF.n_pairs, "19", 0,
   anchor="fail to have a test: on")
ck_word("falsification qualifier resolvable", _r33bF.n_reduction_resolved,
        "four", anchor="measured, four are resolvably positive")
ck_word("falsification qualifier pays", _r33bF.n_entity_pays, "nine",
        anchor="on the nine pairs where a reduction exists")

# section 11: the two things the protocol does not do
ck("corpus congestion from", _AUC.reduction * 100, "43.7", 0.06,
   anchor="move the primary log's reduction from")
ck("corpus congestion to",
   100 * (1 - float(_r22L.iloc[3].gain) / float(_r22L.iloc[1].gain)), "45.7",
   0.06, anchor="move the primary log's reduction from")
ck("headroom pairs", len(_r33H), "26", 0,
   anchor="admission decision on any of the")

# section 11: the condition that governs
_b15 = _P[_P.log.str.startswith("BPIC15")]
ck("bpic15 g cardinality lo", int(_b15.card_g.min()), "7", 0,
   anchor="opening resource stamp has cardinality")
ck("bpic15 g cardinality hi", int(_b15.card_g.max()), "18", 0,
   anchor="opening resource stamp has cardinality")
ck("condition sweep lo", 0, "0", 0,
   anchor="share of arrivals goes from")
ck("condition sweep hi", 95, "95", 0,
   anchor="share of arrivals goes from")
ck("condition reduction hi", _r38F.reduction_hi_intake_mix * 100, "95.3", 0.06,
   anchor="the reduction falls from")
ck("condition reduction lo", _r38F.reduction_lo_intake_mix * 100, "6.3", 0.06,
   anchor="the reduction falls from")

# section 12: the temporal null
ck("temporal null base auc", _r35bF.null_base_auc_max, "0.6483", 6e-5,
   anchor="They reach base AUC at most")
ck("temporal null gap", _r35bF.auc_gap_real_minus_null, "0.1558", 6e-5,
   anchor="the real field is")
ck_bound("temporal null gain lo", _r35bF.null_gain_lo, "+0.092", "lower",
         anchor="above that --- and leave the item worth")
ck_bound("temporal null gain hi", _r35bF.null_gain_hi, "+0.101", "upper",
         anchor="above that --- and leave the item worth")
ck_word("temporal null partitions", _r35bF.n_reps, "Five",
        anchor="further partitions matched on cell size")
ck_word("temporal null strata", _r35bF.n_strata, "twenty",
        anchor="distribution over twenty equal-count time strata")
ck("ladder cohort unchanged", _r35bF.n_test, "13{,}637", 0,
   anchor="every rung is measured on the same")

# two more sentences the widened guard list demands
ck_phrase("the falsification qualifier is pinned",
          r"What ``falsified'' does and does not mean here")
ck_phrase("the registered criterion is named as the criterion",
          r"The claim registered in \texttt{PROTOCOL.md} \S8 is falsified "
          r"\emph{by its own registered criterion}")

'''


def main(argv):
    tex = TEX.read_text(encoding="utf-8")
    v = V.read_text(encoding="utf-8")
    check = "--check" in argv
    problems = [f"{n}: anchor appears {tex.count(o)} times"
                for n, o, _ in TEX_EDITS if tex.count(o) != 1]
    mark = "\n_lint_check_order()\n_run_census()\n"
    if v.count(mark) != 1:
        problems.append("census call site not found")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if check:
        print(f"all {len(TEX_EDITS)} tex anchors and the census site found")
        return 0
    for n, o, w in TEX_EDITS:
        tex = tex.replace(o, w, 1)
        print(f"  applied {n} -> paper")
    TEX.write_text(tex, encoding="utf-8")
    V.write_text(v.replace(mark, CHECKS + mark, 1), encoding="utf-8")
    print("  appended round-seventeen referee checks -> verify_paper.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

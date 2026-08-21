"""Round seventeen's edits to the corruption suite.

Nine corruptions went stale because the sentence they attacked was rewritten;
each is REPOINTED at the sentence that replaced it rather than deleted, so the
attack it encodes survives.  Thirty-two are added, one per claim the
four-choice rebuild put in the paper, plus five that attack the two new
DEFECT CLASSES this round found in our own prose:

  * an extremum stated as the worst of the points the paper happened to
    name (correction nine), and
  * a count identified with an interval (correction ten).

Both of those passed every check the previous verifier had, because every
literal in them was correct.  A suite that only mutates values cannot find
them, so five of the new entries mutate the RELATION instead: they move the
named extremum off the extremum, and they swap the count for the run length.

    python scripts/patch_attacks_r17.py --check
    python scripts/patch_attacks_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "scripts" / "attack_verifier.py"

REPOINT = [
    # (old label, new entry)
    ("corrupt the abstract's replacement factor",
     ('("corrupt the abstract\'s instrument range",\n'
      '     "the reduction runs $43.7\\\\%$ to $60.3\\\\%$, and the AUC figure",\n'
      '     "the reduction runs $23.7\\\\%$ to $60.3\\\\%$, and the AUC figure"),')),
    ("restore the withdrawn factor as a live claim in the abstract",
     ('("restore a withdrawn claim as a live one in the abstract",\n'
      '     "the headline does not survive our own admissibility criterion",\n'
      '     "the headline survives our own admissibility criterion"),')),
    ("fabricate a multi-organisation replication",
     ('("fabricate a multi-organisation replication",\n'
      '     "the reduction is resolvably positive on three.",\n'
      '     "the reduction is resolvably positive on three, and replicates "\n'
      '     "across $7$ further organisations."),')),
    ("fabricate a confidence level",
     ('("fabricate a confidence level",\n'
      '     "the reduction is resolvably positive on three.",\n'
      '     "the reduction is resolvably positive on three, at $95\\\\%$ "\n'
      '     "confidence on every rung."),')),
    ("fabricate independent extracts",
     ('("fabricate independent extracts",\n'
      '     "the reduction is resolvably positive on three.",\n'
      '     "the reduction is resolvably positive on three, confirmed on "\n'
      '     "$10$ independent extracts."),')),
    ("restore the old count of corrections",
     ('("restore the old count of corrections",\n'
      '     "Eleven errors of our own are reported",\n'
      '     "Eight errors of our own are reported"),')),
    ("corrupt the abstract's lookup result",
     ('("corrupt the abstract\'s population figures",\n'
      '     "the item is worth $+0.082$ if the register\'s long",\n'
      '     "the item is worth $+0.182$ if the register\'s long"),')),
    ("corrupt the conclusion's marginal",
     ('("corrupt the conclusion\'s second rung",\n'
      '     "and $+0.001$\\n$[-0.002,+0.003]$ once a second is",\n'
      '     "and $+0.101$ $[-0.002,+0.003]$ once a second is"),')),
    ("fabricate a third organisation in the conclusion",
     ('("fabricate further organisations in the conclusion",\n'
      '     "finds a resolvable reduction on\\nthree",\n'
      '     "finds a resolvable reduction on three and on $3$ others"),')),
]

NEW = r'''
    # ================================================================
    #  ROUND SEVENTEEN.  One corruption per claim the four-choice
    #  rebuild added, and five that attack a RELATION rather than a
    #  value -- the defect class corrections nine and ten belong to,
    #  which no value mutation can reach.
    # ================================================================
    # -- the relation attacks --------------------------------------
    ("move the named extremum off the extremum",
     r"its minimum over the whole grid is $-21.1$ $[-27.7,-14.4]$ per "
     r"thousand at $\theta=0.525$",
     r"its minimum over the whole grid is $-16.1$ $[-23.0,-8.9]$ per "
     r"thousand at $\theta=0.50$"),
    ("shift the extremum's threshold only",
     r"per thousand at $\theta=0.525$",
     r"per thousand at $\theta=0.500$"),
    ("identify the count with the run again",
     r"Those $20$ are not one run: $14$ of them form a contiguous block",
     r"Those $20$ points form a contiguous block"),
    ("swap the count for the run length",
     r"Those $20$ are not one run: $14$ of them",
     r"Those $14$ are not one run: $20$ of them"),
    ("soften the falsification",
     "It is falsified. We report that rather",
     "It is largely supported. We report that rather"),
    # -- the metric axis -------------------------------------------
    ("corrupt the AP row of the instrument table",
     r"Average precision    & $+0.226$ & $+0.090$ & $60.3\%$",
     r"Average precision    & $+0.226$ & $+0.190$ & $60.3\%$"),
    ("narrow an instrument interval inward",
     r"$58.4\%$ $[54.4,62.4]$",
     r"$58.4\%$ $[54.5,62.3]$"),
    ("swap the two net-benefit rows",
     r"Net benefit, $\theta=0.325$ & $+0.093$ & $+0.087$ & $6.3\%$",
     r"Net benefit, $\theta=0.325$ & $+0.084$ & $-0.016$ & $6.3\%$"),
    ("claim seven independent instruments",
     "and report six instruments rather than seven",
     "and report seven instruments rather than six"),
    ("inflate the diffuseness figure",
     r"equal FPR bands carries $18.2\%$ of it",
     r"equal FPR bands carries $58.2\%$ of it"),
    ("change the spelled-out band count",
     "and three bands are needed to reach half",
     "and six bands are needed to reach half"),
    ("corrupt the degenerate-baseline range",
     r"the reduction runs $0.047$ to $0.435$ across",
     r"the reduction runs $0.247$ to $0.435$ across"),
    ("make recalibration move a rank statistic",
     "It moves the AUC and average precision reductions by exactly zero",
     "It moves the AUC and average precision reductions by up to $0.4$"),
    ("corrupt the tie-convention pair",
     r"the reduction is $43.6\%$ under AUC and $71.2\%$ under",
     r"the reduction is $43.6\%$ under AUC and $41.2\%$ under"),
    # -- the population axis ----------------------------------------
    ("swap the two population regimes",
     r"increment is $+0.082$ when the long tail is missing, $+0.067$ at "
     r"random, and $+0.064$ when the core is",
     r"increment is $+0.064$ when the long tail is missing, $+0.067$ at "
     r"random, and $+0.082$ when the core is"),
    ("corrupt the population reduction range",
     r"the reduction runs $-0.6\%$ to $47.1\%$",
     r"the reduction runs $-0.6\%$ to $67.1\%$"),
    ("overstate the estate concentration",
     r"that $246$ of $2{,}929$ items carry $90\%$",
     r"that $46$ of $2{,}929$ items carry $90\%$"),
    # -- the corpus --------------------------------------------------
    ("inflate the admitted logs",
     "The registered rules admit $13$ across six",
     "The registered rules admit $18$ across six"),
    ("inflate the resolvable count",
     "interval excludes zero on four, drawn from three logs",
     "interval excludes zero on nine, drawn from three logs"),
    ("corrupt BPIC 2019's reduction",
     r"duration target ($47.1\%$ $[40.8,53.4]$ on $251{,}734$ traces)",
     r"duration target ($67.1\%$ $[40.8,53.4]$ on $251{,}734$ traces)"),
    ("hide the number of logs with no entity value",
     "On $10$ of the $19$ the entity is not resolvably",
     "On $2$ of the $19$ the entity is not resolvably"),
    ("turn the negative prediction result positive",
     r"the leave-one-out $R^2$ is $-1.323$ against",
     r"the leave-one-out $R^2$ is $+0.323$ against"),
    ("corrupt the target-validity agreement",
     r"and the two agree on $46.0\%$ of them",
     r"and the two agree on $96.0\%$ of them"),
    # -- the settled section 12 --------------------------------------
    ("restore the headline the interaction file removed",
     r"takes the item's measured value from $+0.103$ to $+0.001$",
     r"takes the item's measured value from $+0.103$ to $+0.101$"),
    ("corrupt the orphan interaction count",
     r"$94{,}250$ of those interactions --- $64.1\%$",
     r"$14{,}250$ of those interactions --- $64.1\%$"),
    ("make the discriminating test discriminate",
     r"and the closure code --- which is certainly not creation-time --- on "
     r"$98.97\%$",
     r"and the closure code --- which is certainly not creation-time --- on "
     r"$48.97\%$"),
    ("hide that the closed-before subset is five rows",
     "contains five incidents, and nothing is concluded from five",
     "contains fifteen incidents, and nothing is concluded from fifteen"),
    ("make the null reproduce the finding",
     r"reach base AUC at most\n$0.6479$",
     r"reach base AUC at most $0.8479$"),
    ("overclaim the settled question",
     r"We do not claim the knowledge reference is \emph{proved}",
     r"We claim the knowledge reference is \emph{proved}"),
    # -- the era decomposition ---------------------------------------
    ("corrupt the pre-stamped share",
     r"$97.7\%$ of incidents that came through the service desk",
     r"$67.7\%$ of incidents that came through the service desk"),
    ("corrupt the intake-mix sweep",
     r"moves the reduction from $95.3\%$\nto $6.3\%$",
     r"moves the reduction from $95.3\%$ to $46.3\%$"),
    ("corrupt the service-component share",
     r"so it captures $75.3\%$ of it",
     r"so it captures $95.3\%$ of it"),
    # -- the free-text search ----------------------------------------
    ("shrink the free-text search",
     "Of $596$ attributes, zero satisfy it",
     "Of $96$ attributes, zero satisfy it"),
    ("corrupt the u_symptom figures",
     r"is\n$3.4\%$ unique with a mean length of $10.9$ characters",
     r"is $43.4\%$ unique with a mean length of $10.9$ characters"),
'''


def main(argv):
    src = A.read_text(encoding="utf-8")
    check = "--check" in argv
    problems = []
    for label, _new in REPOINT:
        if src.count(f'("{label}"') != 1:
            problems.append(f"repoint target not found exactly once: {label}")
    if "CORRUPTIONS = [" not in src:
        problems.append("CORRUPTIONS list not found")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if check:
        print(f"all {len(REPOINT)} repoint targets found")
        return 0

    lines = src.split("\n")
    for label, new in REPOINT:
        start = next(i for i, l in enumerate(lines) if l.strip().startswith(f'("{label}"'))
        depth, end = 0, start
        for i in range(start, len(lines)):
            depth += lines[i].count("(") - lines[i].count(")")
            if depth == 0:
                end = i
                break
        lines[start:end + 1] = ["    " + x for x in new.split("\n")]
        print(f"  repointed {label}")
    src = "\n".join(lines)

    src = src.replace("CORRUPTIONS = [", "CORRUPTIONS = [" + NEW, 1)
    n_new = NEW.count('\n    ("')
    print(f"  added {n_new} new corruptions")
    A.write_text(src, encoding="utf-8")
    print(f"wrote {A}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

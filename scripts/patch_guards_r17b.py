"""Pin every sentence the widened guard list now demands, plus one the
corruption suite showed a retirement had unguarded.

Widening `RISKY` makes MORE sentences require a verbatim pin, which is the
point of widening it. Nine sentences containing the new constructions were
unguarded and are pinned here.

The tenth is the one that matters most as a lesson. Retiring
"the negative region is stated, not buried" -- correct, because the sentence
it anchored was rewritten for correction nine -- also removed the pin from
the admission that *adding item identity to a group-aware model can make the
desk worse off*. The suite caught it: the corruption that deletes that
admission had been caught for a round and started passing. **A retirement can
unguard prose it was not retired for**, and only the suite can see that.

    python scripts/patch_guards_r17b.py --check
    python scripts/patch_guards_r17b.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "scripts" / "verify_paper.py"

PINS = r'''
#  ROUND SEVENTEEN, second pass.  Widening RISKY made these nine sentences
#  require a pin; the tenth was unguarded by a retirement and the suite
#  found it.  Each pins POSITION; every literal inside is separately checked.
ck_phrase("the abstract's falsification is pinned",
          r"The generality claim we registered is therefore falsified, and we "
          r"report the negative, the exclusions and the condition that does "
          r"govern")
ck_phrase("the introduction says a demonstration removes the headline",
          r"One of those demonstrations removes the headline")
ck_phrase("the contribution heading names the falsification",
          r"A pre-registered protocol over $22$ public logs, and a falsified "
          r"generality claim")
ck_phrase("the introduction's falsification is pinned",
          r"The registered claim that the effect is a property of process "
          r"event logs rather than of ITSM data is therefore \emph{falsified}")
ck_phrase("the withdrawn ratio is still withdrawn",
          r"What does not survive is the ratio, and with it the claim that "
          r"omitting the free field overstates the operational gain by more "
          r"than it overstates the AUC gain")
ck_phrase("the registered falsification condition is quoted",
          r"\texttt{PROTOCOL.md} \S8 states that the claim is falsified if "
          r"the effect appears on the two published ITSM logs and not on a "
          r"majority of the admitted non-ITSM logs")
ck_phrase("the free-text threat is scoped, not disposed of",
          r"it is the most important open question this study leaves, and it "
          r"cannot be tested on public process-mining data")
ck_phrase("the conclusion keeps the harmful band",
          r"in a band above the base rate the item is resolvably harmful")
ck_phrase("the conclusion's falsification is pinned",
          r"the registered generality claim is falsified and "
          r"Section~\ref{sec:corpus} reports it")
ck_phrase("the item can be worth less than nothing, and the paper says so",
          r"adding item identity to a model that already knows the opening "
          r"group makes the desk worse off on this task")

'''


def main(argv):
    src = V.read_text(encoding="utf-8")
    mark = "ck_phrase(\"the falsification verdict is pinned\","
    if src.count(mark) != 1:
        print(f"anchor appears {src.count(mark)} times -- nothing written")
        return 1
    if "--check" in argv:
        print("anchor found")
        return 0
    V.write_text(src.replace(mark, PINS.lstrip("\n") + mark, 1), encoding="utf-8")
    print(f"wrote {V}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

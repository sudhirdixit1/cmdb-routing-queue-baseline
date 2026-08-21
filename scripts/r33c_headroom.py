"""r33c -- DOES THE EXCLUSION RULE PEEK AT THE TEST HALF?

`PROTOCOL.md` section 4.4 excludes a log-target pair as `NO_HEADROOM` when the
target's prevalence is below 0.05 or above 0.95 **in the full log**.  Referee
pass 1, objection M5 (`REFEREE-LOG.md`): the full log includes the test half,
so the inclusion decision reads test-set outcomes.  It selects on class
balance rather than on effect, which makes it mild, but "mild" is not an
argument and this project has published five nulls that were wrong at the
level rather than in the direction.

This recomputes every pair's prevalence on the TRAINING HALF ONLY, applies the
same registered bounds, and reports every pair whose admission decision
changes.  It fits no model: the prevalence and the split point are all it
needs, so it is cheap and it cannot be accused of choosing a rule by its
result.

Outputs: results/r33_headroom_sensitivity.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
import r33_generic_ladder as L
from common import RESULTS

t0 = time.time()
ROLES = pd.read_csv(RESULTS / "r33_roles.csv")
ADMITTED = sorted(ROLES.log.unique())

rows = []
for key in ADMITTED:
    r = ROLES[ROLES.log == key]
    g = r[r.role == "g"].attribute.tolist()
    if not g:
        continue
    g = g[0]
    d = C.load(key)
    d, _ = L.temporal_order(d)
    cut = int(len(d) * L.TRAIN_FRAC)
    seq = next((c for c in d.columns if c.startswith("_seq_")
                and c[5:].lower() == str(g).lower()), None)
    if seq is None:
        continue
    y_h, y_d, _ = L.targets(d, seq, cut)
    for tname, yv in (("handover", y_h), ("duration", y_d)):
        if yv is None:
            continue
        p_full = float(yv.mean())
        p_train = float(yv[:cut].mean())
        adm_full = bool(L.PREV_LO <= p_full <= L.PREV_HI)
        adm_train = bool(L.PREV_LO <= p_train <= L.PREV_HI)
        rows.append(dict(log=key, target=tname, n=len(d),
                         prevalence_full=p_full, prevalence_train=p_train,
                         admitted_as_registered=adm_full,
                         admitted_train_only=adm_train,
                         decision_changes=(adm_full != adm_train)))
S = pd.DataFrame(rows)
S.to_csv(RESULTS / "r33_headroom_sensitivity.csv", index=False)

print("=" * 92)
print("HEADROOM: THE REGISTERED RULE AGAINST A TRAINING-HALF-ONLY RULE")
print("=" * 92)
print(f"  {'log':18s} {'target':9s} {'prev full':>10s} {'prev train':>11s} "
      f"{'registered':>11s} {'train-only':>11s}")
for _, r in S.iterrows():
    flag = "  <-- CHANGES" if r.decision_changes else ""
    print(f"  {r.log:18s} {r.target:9s} {r.prevalence_full:>10.4f} "
          f"{r.prevalence_train:>11.4f} {str(r.admitted_as_registered):>11s} "
          f"{str(r.admitted_train_only):>11s}{flag}")

n_chg = int(S.decision_changes.sum())
print(f"""
  {len(S)} log-target pairs; {n_chg} admission decision{'s' if n_chg != 1 else ''} change{'' if n_chg != 1 else 's'}.""")
if n_chg == 0:
    print("""  The registered rule and a rule that never looks at the test half admit
  exactly the same set.  Objection M5 is answered: the peek exists in the
  registered text and changes nothing in the result.""")
else:
    print("  The rules disagree on:")
    for _, r in S[S.decision_changes].iterrows():
        print(f"    {r.log} / {r.target}: full {r.prevalence_full:.4f}, "
              f"train {r.prevalence_train:.4f}")
    print("""  The paper reports the disagreement and states which rule its table
  uses.  A rule that changes the corpus is not a footnote.""")
print(f"\n  Wrote r33_headroom_sensitivity.csv  ({time.time() - t0:.0f}s)")

"""R17 -- rebuilding the mechanism's floor at the right level.

A referee found that the floor in `r8_final.py` section B is drawn at ROW
level:

    lab = r.choice(isz.index, size=len(p), p=(isz / isz.sum()).values)

so two rows carrying the SAME item land in different cells.  Shuffling the
opening group within such cells destroys the item-group association by
construction, and the floor is therefore ~0 by construction rather than by
measurement.  The published "retains 2%, the margin is 89 points" is
measured against a null that cannot fail.

This is the fourth time this project has been caught by a null built at the
wrong level (HANDOFF section 4, withdrawn findings 3 and 8), and worse, the
SAME script already does it correctly in section C, where the dropped leg is
nulled with an item-level partition.  The surviving leg got the permissive
null and the dropped leg got the strict one.  That asymmetry is exactly what
a referee should catch and did.

This script rebuilds the floor properly:

  * cells are a random partition OF ITEMS, so every row of an item shares a
    cell.  The partition knows nothing about the opening group.
  * the number of cells is swept, because retention is a monotone function
    of granularity and any single choice is an author's choice.  At one
    extreme (few cells) the null is uninformative; at the other (cells ~
    items) the null converges on the real thing and stops being a floor.
  * the principled comparison point is a cell count equal to the number of
    opening groups, which is the real field's own cardinality.

Everything else is held to r4_final.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

SEED = 20260819
N_DRAW = 30
Q = "intake_group"

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)
y = TE._y.values

A0 = roc_auc_score(y, M.fit(TR, TE, M.INTAKE))
Aq = roc_auc_score(y, M.fit(TR, TE, M.INTAKE + [Q]))
qg = Aq - A0
N_GROUPS = int(TR[Q].astype(str).nunique())
ITEMS = pd.Index(D[M.IDENT].astype(str).unique())

print("=" * 88)
print("A. THE REAL LEG (unchanged)")
print("=" * 88)
real = []
for rep in range(N_DRAW):
    r = np.random.default_rng(900 + rep)
    tr, te = TR.copy(), TE.copy()
    for p in (tr, te):
        p["_s"] = p.groupby(M.IDENT)[Q].transform(lambda s: r.permutation(s.values))
    real.append(roc_auc_score(te._y.values, M.fit(tr, te, M.INTAKE + ["_s"])) - A0)
real = np.array(real)
print(f"  opening group's own gain over intake      {qg:+.4f}")
print(f"  group randomised WITHIN item              {real.mean():+.4f} "
      f"+- {real.std():.4f}  = {100*real.mean()/qg:.0f}% retained")

print("\n" + "=" * 88)
print("B. THE FLOOR, DRAWN AT ITEM LEVEL, AS A FUNCTION OF GRANULARITY")
print("=" * 88)
print("  Cells are a random partition of ITEMS.  A partition that knows")
print("  nothing about routing still retains some of the gain, because item")
print("  identity is itself predictive; that is the point of the floor.\n")
print(f"  {'cells':>7s} {'retained':>10s} {'sd':>8s}   note")
rows = []
for k in (10, N_GROUPS, 100, 200, 400, 800):
    vals = []
    for rep in range(N_DRAW):
        r = np.random.default_rng(SEED + rep)
        lut = pd.Series(r.integers(0, k, len(ITEMS)).astype(str), index=ITEMS)
        tr, te = TR.copy(), TE.copy()
        for p in (tr, te):
            p["_c"] = p[M.IDENT].astype(str).map(lut)
            p["_s"] = p.groupby("_c")[Q].transform(lambda s: r.permutation(s.values))
        vals.append(roc_auc_score(te._y.values,
                                  M.fit(tr, te, M.INTAKE + ["_s"])) - A0)
    v = np.array(vals)
    note = ""
    if k == N_GROUPS:
        note = "<- matched to the field's own cardinality"
    if k >= 800:
        note = "cells approach items; no longer a floor"
    rows.append(dict(cells=k, retained=float(v.mean() / qg), sd=float(v.std() / qg),
                     gain=float(v.mean())))
    print(f"  {k:>7,} {100*v.mean()/qg:>9.1f}% {100*v.std()/qg:>7.1f}%   {note}")
F = pd.DataFrame(rows)
F.to_csv(RESULTS / "r17_floor_sweep.csv", index=False)

matched = F[F.cells == N_GROUPS].iloc[0]
margin = 100 * real.mean() / qg - 100 * matched.retained
print(f"\n  At the matched cell count ({N_GROUPS}) the floor retains "
      f"{100*matched.retained:.0f}%.")
print(f"  Real leg {100*real.mean()/qg:.0f}%.  HONEST MARGIN: {margin:.0f} points, "
      f"not the 89 previously")
print("  published against a row-level null.")
print("\n  The floor rises with granularity, so the margin is a function of a")
print("  knob.  The paper now reports the sweep rather than one number.")

print("\n" + "=" * 88)
print("C. WHAT SURVIVES")
print("=" * 88)
print(f"  Real within-item shuffle retains {100*real.mean()/qg:.0f}% of the")
print(f"  opening group's gain.  Every item-level floor from {F.cells.min()} to")
print(f"  {int(F[F.cells<=400].cells.max())} cells retains less "
      f"({100*F[F.cells<=400].retained.min():.0f}%-"
      f"{100*F[F.cells<=400].retained.max():.0f}%).  The ordering is stable; the")
print("  MAGNITUDE of the margin is not, and is no longer claimed.")
pd.DataFrame([dict(
    real_retained=float(real.mean() / qg), real_sd=float(real.std() / qg),
    queue_gain=qg, n_groups=N_GROUPS,
    floor_matched=float(matched.retained), margin_matched=float(margin),
    floor_lo=float(F[F.cells <= 400].retained.min()),
    floor_hi=float(F[F.cells <= 400].retained.max()),
)]).to_csv(RESULTS / "r17_floor.csv", index=False)

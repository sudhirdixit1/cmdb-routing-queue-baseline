"""R12 -- how far the opening queue is determined by the affected item,
measured without a classifier.

Review objection (O1).  The paper calls the opening routing queue "free",
and a reviewer can reasonably answer that it is only free because a human at
the service desk already knew, informally, what the ticket was about.  On
that reading the queue IS configuration knowledge -- undocumented, carried in
people's heads -- and a baseline containing it is not a CMDB-free baseline.

The paper's mechanism section already reports that randomising the queue
label within each item retains 91% of the queue's gain, but that is a
statement about a fitted model.  This script measures the same relationship
directly on the data, with no estimator involved, so the claim does not
depend on the paper's one modelling choice:

  A  Conditional entropy H(queue | item) against H(queue), and the
     uncertainty coefficient U = 1 - H(queue|item)/H(queue), the share of
     the queue's information that item identity already carries.
  B  The accuracy of the trivial lookup "route this to the modal queue of
     its affected item", fitted on training and evaluated on test.  A rule
     with no model, no features and no fitting.
  C  The share of items whose queue is completely determined.
  D  The reverse direction, H(item | queue), which is where the asymmetry
     lives and why the paper does not run the argument backwards.

Entropies are computed on training rows only and evaluated on test where a
held-out figure is meaningful, so nothing here uses the test outcome.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).parent))
import r4_final as M
from common import RESULTS

D, counts, ACT, OPEN = M.load()
TR, TE = M.split(D)

Q = "intake_group"
I = M.IDENT


def H(s):
    p = pd.Series(s).value_counts(normalize=True).values
    return float(-(p * np.log2(p)).sum())


def H_cond(inner, outer, df):
    """H(inner | outer), weighted by cell mass."""
    g = df.groupby(outer, observed=True)[inner]
    w = g.size() / len(df)
    h = g.apply(lambda s: H(s))
    return float((w * h).sum())


tr = TR[[I, Q]].astype(str)
te = TE[[I, Q]].astype(str)

print("=" * 92)
print("A. CONDITIONAL ENTROPY  (training rows, no model)")
print("=" * 92)
h_q = H(tr[Q])
h_q_i = H_cond(Q, I, tr)
h_i = H(tr[I])
h_i_q = H_cond(I, Q, tr)
u_q = 1 - h_q_i / h_q
u_i = 1 - h_i_q / h_i
print(f"  H(queue)                      {h_q:6.3f} bits over "
      f"{tr[Q].nunique()} groups")
print(f"  H(queue | item)               {h_q_i:6.3f} bits")
print(f"  U(queue | item)               {u_q:6.1%}  <- share of the queue's")
print(f"                                        information the item carries")
print()
print(f"  H(item)                       {h_i:6.3f} bits over "
      f"{tr[I].nunique():,} items")
print(f"  H(item | queue)               {h_i_q:6.3f} bits")
print(f"  U(item | queue)               {u_i:6.1%}")
# CORRECTED 2026-08-20.  "Nearly determines" is contradicted by section B of
# this same script (class-balanced lookup accuracy 34.1%) and by the paper.
# These plug-in coefficients are also biased upward by conditioning on 2,554
# levels: r18_referee_round2.py measures the floor at 14.0% and 4.5%.
print(f"\n  The relationship is strongly asymmetric: {u_q:.0%} against {u_i:.0%}.")
print("  Both are inflated by finite-sample bias -- see r18_mi_null.csv, which")
print("  puts the floors at 14.0% and 4.5% -- so read the ASYMMETRY, not the")
print("  levels.  Item identity does NOT determine which group opens the")
print("  ticket; section B below is the check that keeps this honest.")

print("\n" + "=" * 92)
print("B. THE TRIVIAL LOOKUP RULE, EVALUATED OUT OF SAMPLE")
print("=" * 92)
modal = tr.groupby(I)[Q].agg(lambda s: s.value_counts().idxmax())
prior = tr[Q].value_counts().idxmax()
pred_tr = tr[I].map(modal)
pred_te = te[I].map(modal)
seen = pred_te.notna()
acc_tr = float((pred_tr == tr[Q]).mean())
acc_te_seen = float((pred_te[seen] == te.loc[seen, Q]).mean())
acc_te_all = float((pred_te.fillna(prior) == te[Q]).mean())
base_te = float((te[Q] == prior).mean())
print("  Rule: route each incident to the most common opening queue of its")
print("  affected item, learned from training rows only.\n")
print(f"  accuracy on training rows                     {acc_tr:6.1%}")
print(f"  accuracy on test rows whose item was seen     {acc_te_seen:6.1%}  "
      f"({seen.sum():,} of {len(te):,})")
print(f"  accuracy on all test rows (prior for unseen)  {acc_te_all:6.1%}")
print(f"  always guess the single largest queue         {base_te:6.1%}")

# Raw accuracy flatters this rule badly: one queue holds most of the test
# rows, so a constant guess already scores 79%.  Report the class-balanced
# figures too, and do not quote the raw number without them.
bal = balanced_accuracy_score(te[Q], pred_te.fillna(prior))
mf1 = f1_score(te[Q], pred_te.fillna(prior), average="macro", zero_division=0)
mf1_const = f1_score(te[Q], pd.Series([prior] * len(te), index=te.index),
                     average="macro", zero_division=0)
print(f"\n  balanced accuracy of the lookup               {bal:6.1%}")
print(f"  macro-F1 of the lookup                        {mf1:6.3f}")
print(f"  macro-F1 of the constant guess                {mf1_const:6.3f}")
print(f"\n  READ THESE TOGETHER.  The {acc_te_all:.0%} raw figure is inflated by a "
      f"dominant\n  queue holding {base_te:.0%} of test rows; the constant guess already scores")
print(f"  {base_te:.0%}.  Class-balanced, the lookup reaches only {bal:.0%}.  So the correct")
print("  statement is NOT that the item determines the routing decision.  It")
print("  is that item identity resolves most of the coarse routing contrast --")
print("  main pool or not -- and much less of the fine one.  r13 quantifies")
print("  what that coarse contrast is worth.")

print("\n" + "=" * 92)
print("C. HOW MANY ITEMS ARE FULLY DETERMINED")
print("=" * 92)
nq = tr.groupby(I)[Q].nunique()
mass = tr[I].value_counts()
det_items = float((nq == 1).mean())
det_mass = float(mass[nq[nq == 1].index].sum() / len(tr))
conc = tr.groupby(I)[Q].agg(lambda s: s.value_counts(normalize=True).iloc[0])
print(f"  items routed to exactly one queue     {int((nq==1).sum()):,} of "
      f"{len(nq):,}  ({det_items:.1%})")
print(f"  share of incidents they account for   {det_mass:.1%}")
print(f"  mass-weighted modal-queue purity      "
      f"{float((conc.reindex(mass.index) * mass).sum() / len(tr)):.1%}")

print("\n" + "=" * 92)
print("D. WHAT THIS DOES AND DOES NOT SETTLE")
print("=" * 92)
print("  It settles that the queue label carries little that item identity")
print("  does not, on this log, without reference to any estimator.")
print()
print("  It does NOT settle the direction of the dependence.  These figures")
print("  are equally consistent with (i) the desk reading the item off the")
print("  ticket and routing accordingly, and (ii) the queue being an")
print("  independent signal that happens to align.  The log records no")
print("  intervention and no counterfactual routing, so the question is not")
print("  identified here.  The paper's claim is about what the analyst's")
print("  baseline choice does to a measured number, which does not depend on")
print("  which of these is true.")
pd.DataFrame([dict(
    h_queue=h_q, h_queue_given_item=h_q_i, u_queue_given_item=u_q,
    h_item=h_i, h_item_given_queue=h_i_q, u_item_given_queue=u_i,
    n_queues=int(tr[Q].nunique()), n_items=int(tr[I].nunique()),
    lookup_train=acc_tr, lookup_test_seen=acc_te_seen,
    lookup_test_all=acc_te_all, lookup_prior=base_te,
    n_test_seen=int(seen.sum()), n_test=len(te),
    lookup_balanced_acc=float(bal), lookup_macro_f1=float(mf1),
    const_macro_f1=float(mf1_const),
    items_single_queue=int((nq == 1).sum()), items_single_pct=det_items,
    single_queue_mass=det_mass,
)]).to_csv(RESULTS / "r12_queue_from_item.csv", index=False)

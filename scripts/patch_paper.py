"""Apply the remaining seventh-review repairs to the paper.

Kept in a file rather than a shell heredoc because backslash-heavy LaTeX
edits were repeatedly mangled by shell quoting -- which is how the broken
table row terminators reached the draft in the first place.
"""
from pathlib import Path

TEX = Path(__file__).resolve().parent.parent / "paper" / "iaai27_empty_cmdb.tex"
s = TEX.read_text(encoding="utf-8")

EDITS = [
    # abstract: replace the two dropped legs with the two that have nulls
    ("""Two direct measurements explain the
gap. Adding the queue to a model that already knows the item is worth
$+0.002$: the item column already carries almost all of the queue's
predictive content. And projecting the item's outcome-rate predictor onto
the queue partition puts $43.3\\%$ of its variance between queues. The two
fields overlap heavily, and because a shared term cannot be assigned to
either by measurement, we report the overlap rather than attributing it. We
also report one attempt that failed: a third free-looking field drives the
measured gain to zero, and we could not establish from this export whether
it is a legitimate baseline field or a leak.""",
     """Two measurements explain the gap.
Adding the queue to a model that already knows the item is worth under
$0.01$ AUC. And randomising the queue label within each item, which destroys
the queue's identity but keeps what the item implies about it, still retains
$91\\%$ of the queue's own gain against a matched floor of $2\\%$: the routing
decision is very nearly a function of the affected item. We report two
attempts that failed --- a third free-looking field drives the measured gain
to zero and we could not establish whether it is admissible, and a
reverse-direction measurement whose defensible nulls disagree."""),

    # design-space range now includes the cleaning cutoff
    ("""across split point
and target threshold the second gain ranges $+0.068$ to $+0.118$, and it
rises monotonically with training volume.""",
     """across split point,
target threshold and cleaning cutoff the second gain ranges $+0.068$ to
$+0.130$, and it rises with training volume."""),

    # deployment scoping, which the track rewards and which costs three lines
    ("""An organisation can compute this from a frequency
count before funding anything.""",
     """An organisation can compute this from a frequency
count before funding anything. Identifying only those items recovers most of
the measured value: the top $8$ recover $57.9\\%$ of the $+0.103$, the top
$64$ recover $90.0\\%$, and the top $128$ recover $95.4\\%$."""),

    # scope corrections
    ("value varies within an incident for $92.66\\%$ of cases",
     "value varies within an incident for $92.56\\%$ of cases in the cohort"),
    ("it matches the last-observed queue for\nonly $21.4\\%$ of incidents.",
     "it matches the last-observed queue for\nonly $21.35\\%$ of incidents."),

    # the conclusion's arithmetic was wrong on its face
    ("""and $44\\%$ of
the difference is that same queue, reappearing inside the item column.""",
     """and the difference
is an overlap: the queue is very nearly a function of the item, so a model
given the item has already been told the queue."""),

    # the introduction's confession, cut to one sentence
    ("""Six findings were withdrawn across earlier versions of this work, each an
artifact of a control we had built: feature entry order; a random baseline
matched on label count rather than effective resolution; a null whose
construction did not reproduce the mass profile it matched on; a
within-table comparison confounded by regularisation burden; a linear fit
with a positive intercept; and a convergence claim resting on two rules
where three were reported. We state this because the paper is deliberately
smaller than its predecessors: what follows is what survived adversarial
review, and the discarded material was in every case larger and more
interesting.""",
     """Earlier versions of this work reported several larger findings that were
withdrawn under adversarial review, each an artifact of a control we had
constructed. The paper is deliberately smaller as a result: every claim
below is either a direct measurement or is reported against a null, and
where a null is ambiguous we say so and drop the claim."""),
]

missing = []
for old, new in EDITS:
    if old in s:
        s = s.replace(old, new, 1)
    else:
        missing.append(old.split("\n")[0][:60])

TEX.write_text(s, encoding="utf-8")
print(f"applied {len(EDITS) - len(missing)} of {len(EDITS)} edits")
for m in missing:
    print("  NOT FOUND:", m)

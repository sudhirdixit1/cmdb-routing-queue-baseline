"""Move the cohort block after its dependencies and fix the three misses."""
import re
from pathlib import Path

V = Path(__file__).resolve().parent / "verify_paper.py"
lines = V.read_text(encoding="utf-8").split("\n")

# 1. lift the cohort block out of its current position
start = next(i for i, l in enumerate(lines)
             if l.startswith("# ---- cohort-restricted scope figures"))
end = next(i for i, l in enumerate(lines[start + 1:], start + 1)
           if l.startswith("# ---- the section reporting a failure"))
block = lines[start:end]
del lines[start:end]

# 2. drop the stale checks it replaces
lines = [l for l in lines
         if '"92.66"' not in l and '"21.4"' not in l]

# 3. re-insert after the raw-data section has defined w, a, op, first, last
anchor = next(i for i, l in enumerate(lines)
              if l.startswith("# ---- residue of withdrawn claims"))
lines[anchor:anchor] = block + [""]

s = "\n".join(lines)

# 4. the remaining value/anchor corrections
s = s.replace('ck("queue gain given item", ov.queue_unique, "0.002", 6e-4,',
              'ck("queue gain given item", ov.queue_unique, "+0.002", 6e-4,')
s = s.replace('anchor="queue\'s gain once the item")',
              'anchor="queue\'s gain once the item is present")')
s = s.replace('ck("km rung gain", abs(b3.gain), "0.003", 6e-4, anchor="measured value of item")',
              'ck("km rung gain", b3.gain, "-0.003", 6e-4, anchor="measured value of item")')

V.write_text(s, encoding="utf-8")
print("cohort block relocated; stale checks removed")

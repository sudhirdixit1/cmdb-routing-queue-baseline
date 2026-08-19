"""Add the two verified references and wire them into the paper."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "paper" / "references.bib"
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"

NEW = r"""
% ------------------------------------------------- evaluation methodology
@article{rendle2019baselines,
  author  = {Rendle, Steffen and Zhang, Li and Koren, Yehuda},
  title   = {On the Difficulty of Evaluating Baselines: A Study on
             Recommender Systems},
  journal = {arXiv preprint arXiv:1905.01395},
  year    = {2019},
  note    = {Shows that inadequately tuned baselines invalidate reported
             improvements; the closest prior statement of this paper's thesis
             in another domain}
}

% ------------------------------------- prior work on these very event logs
@article{teinemaa2019outcome,
  author  = {Teinemaa, Irene and Dumas, Marlon and La Rosa, Marcello and
             Maggi, Fabrizio Maria},
  title   = {Outcome-Oriented Predictive Process Monitoring: Review and
             Benchmark},
  journal = {ACM Transactions on Knowledge Discovery from Data},
  volume  = {13},
  number  = {2},
  pages   = {17:1--17:57},
  year    = {2019},
  doi     = {10.1145/3301300},
  note    = {Benchmarks outcome prediction across 24 real-world logs
             including the BPI Challenge collection}
}
"""

bib = BIB.read_text(encoding="utf-8")
marker = "%% ------------------------------------------------------------------------\n%% STILL TO ADD"
if "rendle2019baselines" not in bib:
    bib = bib.replace(marker, NEW.strip() + "\n\n" + marker, 1) \
        if marker in bib else bib + NEW
BIB.write_text(bib, encoding="utf-8")

s = TEX.read_text(encoding="utf-8")
EDITS = [
    # position the task against the literature that uses these logs
    ("""A CMDB records configuration items and their relationships. Surveys of AIOps
for failure management \\citep{zhang2024aiops,remil2024aiops} catalogue
triage, failure-prediction and root-cause methods that consume such data.
Our question is not whether those methods work but what their evaluation is
measured against.""",
     """A CMDB records configuration items and their relationships. Surveys of AIOps
for failure management \\citep{zhang2024aiops,remil2024aiops} catalogue
triage, failure-prediction and root-cause methods that consume such data,
and outcome prediction on incident logs of this kind is benchmarked in the
predictive process monitoring literature \\citep{teinemaa2019outcome}. Our
question is not whether those methods work but what their evaluation is
measured against --- a concern raised for recommender systems by
\\citet{rendle2019baselines}, who show that inadequately specified baselines
can account for reported gains. We report the same failure mode for a
deployment decision rather than a leaderboard."""),
]
missing = []
for old, new in EDITS:
    if old in s:
        s = s.replace(old, new, 1)
    else:
        missing.append(old.split("\n")[0][:50])
TEX.write_text(s, encoding="utf-8")
print(f"bib entries: {bib.count('@')} total")
print(f"applied {len(EDITS)-len(missing)} of {len(EDITS)} tex edits")
for m in missing:
    print("  NOT FOUND:", m)

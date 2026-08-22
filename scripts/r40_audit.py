"""r40 -- THE LITERATURE AUDIT.  AUDIT-PROTOCOL.md, implemented.

Four stages, each cached so a re-run costs seconds and a fresh run costs one
network pass:

    python r40_audit.py --frame      # AUDIT-PROTOCOL.md 2: enumerate + sample
    python r40_audit.py --fetch      # 3: retrieve full text, cache it
    python r40_audit.py --code       # 4, 5: screen and code
    python r40_audit.py --report     # 6, 7: proportions, funnel, kappa
    python r40_audit.py              # all four, in order

WHAT THIS FILE IS AND IS NOT.  It is a mechanical coder: it applies a fixed
pattern set to extracted full text and records, for every code it assigns, the
sentence that produced it and the PDF page it was on.  It is NOT a reader.
AUDIT-PROTOCOL.md 7 says so, says what is done instead, and says which of the
four substitutes needs the author rather than an agent.

THE PATTERNS BELOW ARE THE PROTOCOL'S RULES, AND THEY ARE FIXED BEFORE THE
FIRST PAPER IS SCREENED.  CODE_RULES_B is a second implementation of the same
five rules in AUDIT-PROTOCOL.md 5, written against that prose and not against
CODE_RULES; the agreement between them is the reliability evidence a single
author can produce.
"""
import argparse
import gzip
import json
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "data" / "audit"
TEXTS = AUDIT / "fulltext"
META = AUDIT / "meta"
for d in (AUDIT, TEXTS, META):
    d.mkdir(parents=True, exist_ok=True)

SEED = 20260819
CAP = 600
MAILTO = "sudhir.dixit1@gmail.com"
UA = {"User-Agent": f"emptycmdb-audit/1.0 (mailto:{MAILTO})"}
OA = "https://api.openalex.org"

# --- AUDIT-PROTOCOL.md 2.1 -------------------------------------------------
VENUES = {
    "Information Systems": "S193006928",
    "Decision Support Systems": "S11479521",
    "Information & Management": "S38883057",
    "Empirical Software Engineering": "S109852484",
}
TOPICAL = ('(predict OR prediction OR predictive OR classifier OR '
           'classification OR "machine learning" OR AUC OR forecasting)')
# --- AUDIT-PROTOCOL.md 2.2 -------------------------------------------------
BENCHMARK = ["W2964066696", "W2737745668"]
YEARS = "2019-2026"

# --- AUDIT-PROTOCOL.md 3 ---------------------------------------------------
MIN_CHARS = 6000
MIN_PAGES = 4
PAGE_SEP = "\f"

# --- AUDIT-PROTOCOL.md 4 ---------------------------------------------------
METRIC_LEXICON = [
    r"\bAUC\b", r"\bAUROC\b", r"\bROC\b", r"\bF1\b", r"\bF-?measure\b",
    r"\bprecision\b", r"\brecall\b", r"\baccuracy\b", r"\bMCC\b",
    r"\bBrier\b", r"\baverage precision\b", r"\bAUPRC\b", r"\bMAE\b",
    r"\bRMSE\b", r"\bR2\b", r"\bR\^?2\b",
]
_METRIC = re.compile("|".join(METRIC_LEXICON), re.I)
_NUMBER = re.compile(r"\b\d+\.\d+\b|\b\d{1,3}(\.\d+)?\s?%")

ABLATION_PATTERNS = [
    # class 1: with/without
    r"\bwith and without\b",
    r"\bwithout\s+(the|these|those|any|our|their)?\s*[\w\-\s]{0,40}"
    r"(features?|attributes?|variables?|fields?|predictors?|data|information)\b",
    # class 2: adding / removing a feature
    r"\b(add(ing|ed)?|includ(ing|ed)|inclusion of|incorporat(ing|ed)|"
    r"introduc(ing|ed))\b[^.]{0,70}\b(features?|attributes?|variables?|"
    r"fields?|predictors?|data sources?|information)\b[^.]{0,90}"
    r"\b(improv|increas|boost|gain|rais|reduc|decreas|lower|deteriorat|drop)",
    r"\b(remov(ing|ed|al of)|exclud(ing|ed)|exclusion of|drop(ping|ped)|"
    r"omit(ting|ted)?)\b[^.]{0,70}\b(features?|attributes?|variables?|"
    r"fields?|predictors?|data sources?)\b",
    # class 3: ablation
    r"\bablation\b",
    # class 4: feature-set comparison
    r"\b(feature (sets?|groups?|subsets?)|encodings?)\b[^.]{0,90}"
    r"\b(compar|versus|vs\.?|against|baseline)\b",
    # class 5: with the X feature the model improves by
    r"\b(with|using)\b[^.]{0,60}\b(features?|attributes?|variables?|"
    r"predictors?)\b[^.]{0,60}\b(the model|performance|accuracy|AUC|F1)\b"
    r"[^.]{0,60}\b(improv|increas|gain|rais|higher|better)\b",
    # class 6: inclusion of X increases/decreases
    r"\bcontribution of (the\s+)?[\w\-\s]{0,40}"
    r"(features?|attributes?|variables?|fields?|predictors?|data)\b",
    # class 7: baseline augmented with
    r"\b(baseline|base model|reference model)\b[^.]{0,80}"
    r"\b(plus|augmented with|enriched with|extended with|combined with)\b",
    # class 8: explicit ablation vocabulary
    r"\b(leave-one-(feature|group|out)|one-at-a-time|knock-?out)\b"
    r"[^.]{0,60}\b(features?|variables?|attributes?)\b",
]
_ABLATION = [re.compile(p, re.I) for p in ABLATION_PATTERNS]

# --- AUDIT-PROTOCOL.md 5 ---------------------------------------------------
#  Every code has a STRONG list and a WEAK list.  A strong hit codes `yes`; a
#  weak hit and no strong hit codes `unclear`; nothing codes `no`.  `unclear`
#  is therefore a value the rule ASSIGNS, not a value it falls back to when it
#  crashes, and AUDIT-PROTOCOL.md 5 says it is reported separately from `no`.
CODE_RULES = {
    "B_stated": dict(
        strong=[
            r"\b(baseline|base model|reference model|control model)\b[^.]{0,120}"
            r"\b(consists? of|compris\w+|contains?|includes?|uses?|is built "
            r"(on|from)|is based on)\b[^.]{0,120}"
            r"\b(features?|attributes?|variables?|predictors?)\b",
            r"\bthe following (features?|attributes?|variables?|predictors?)\b",
            r"\bTable\s+\d+\b[^.]{0,60}\b(lists?|shows?|presents?|summari[sz]es?|"
            r"describes?|reports?)\b[^.]{0,60}"
            r"\b(features?|attributes?|variables?|predictors?)\b",
            r"\b(feature (set|vector)|set of features)\b[^.]{0,60}"
            r"\b(consists? of|compris\w+|contains?|includes?|is made up of)\b",
            r"\bwe use the following\b[^.]{0,60}"
            r"\b(features?|attributes?|variables?)\b",
        ],
        weak=[
            r"\b(features?|attributes?|variables?) (used|considered|selected|"
            r"extracted|available)\b[^.]{0,80}\b(are|were|is|was)\b",
            r"\bTable\s+\d+\b[^.]{0,40}\b(features?|attributes?|variables?)\b",
            r"\b(feature|attribute|variable) (description|overview|list)\b",
        ]),
    "B_justified": dict(
        strong=[
            r"\b(we|the (baseline|model|study))\b[^.]{0,70}"
            r"\b(exclude[ds]?|omit(ted|s)?|drop(ped|s)?|left out|discard(ed|s)?|"
            r"do(es)? not (use|include)|did not (use|include))\b[^.]{0,110}"
            r"\b(because|since|as it|as they|in order to|to avoid|to prevent|"
            r"due to|for this reason|on the grounds that|so as not to)\b",
            r"\b(features?|attributes?|variables?|fields?)\b[^.]{0,60}"
            r"\b(were|are|was|is) (excluded|omitted|removed|discarded|"
            r"left out|not (used|included))\b[^.]{0,90}"
            r"\b(because|since|as|due to|to avoid|in order to|to prevent)\b",
            r"\b(because|since|as)\b[^.]{0,90}\b(we|it|they)\b[^.]{0,40}"
            r"\b(exclude[ds]?|omit(ted|s)?|drop(ped|s)?|do(es)? not include)\b",
        ],
        weak=[
            r"\b(exclude[ds]?|omit(ted|s)?|discard(ed|s)?|remov(e[ds]?|ed))\b"
            r"[^.]{0,70}\b(leakage|leak|future information|not available at|"
            r"unavailable at|post-hoc|after the fact)\b",
            r"\b(only|solely) (features?|attributes?|variables?)\b[^.]{0,70}"
            r"\b(available|known|recorded) (at|before|prior to)\b",
        ]),
    "M_justified": dict(
        strong=[
            r"\b(AUC|AUROC|ROC|F1|F-?measure|MCC|Brier|accuracy|"
            r"average precision|AUPRC|precision|recall)\b[^.]{0,140}"
            r"\b(because|since|as it is|is preferred|is appropriate|"
            r"is suitable|is robust|is insensitive|for comparability|"
            r"to be comparable|to allow comparison|is the standard)\b",
            r"\b(because|since|due to|given)\b[^.]{0,90}"
            r"\b(class imbalance|imbalanced|skewed class|rare (class|event))\b"
            r"[^.]{0,110}\b(AUC|F1|MCC|precision|recall|average precision|"
            r"AUPRC|balanced accuracy|PR curve)\b",
            r"\bwe (report|use|adopt|select|choose|chose)\b[^.]{0,60}"
            r"\b(AUC|AUROC|F1|MCC|Brier|average precision|AUPRC)\b"
            r"[^.]{0,120}\b(because|since|as it|in order to|to allow|to enable|"
            r"for comparability|to be comparable|so that)\b",
        ],
        weak=[
            r"\b(AUC|AUROC|F1|MCC|Brier|average precision)\b[^.]{0,90}"
            r"\b(is (a )?(common|widely used|standard|popular)|"
            r"has been used|following (prior|previous|earlier) work)\b",
            r"\b(class imbalance|imbalanced (data|dataset|classes))\b"
            r"[^.]{0,110}\b(metric|measure|evaluation)\b",
        ]),
    "Theta_stated": dict(
        strong=[
            r"\b(threshold|cut-?off|operating point|decision threshold)\b"
            r"[^.]{0,80}\b(of|=|set (to|at)|is|was|equal to|fixed (at|to))\b"
            r"[^.]{0,25}\d",
            r"\b(cost|utility|misclassification) (ratio|matrix|weights?)\b",
            r"\b(false positives?|false negatives?)\b[^.]{0,90}"
            r"\b(cost|costs|weight|weighted|ratio|times as|more expensive)\b",
            r"\b(AUC|AUROC|ROC curve)\b[^.]{0,130}"
            r"\b(integrat\w+|across (all )?(possible )?thresholds|"
            r"over (all|the whole|the entire) (range of )?thresholds|"
            r"threshold[- ]independent|independent of the threshold|"
            r"all possible (decision )?thresholds)\b",
            r"\btop[- ]?(k|\d+)\b[^.]{0,50}\b(cases|instances|alerts|"
            r"predictions|candidates|items)\b",
            r"\b(capacity|budget)\b[^.]{0,60}\b(of|=|limited to|constrained to)\b"
            r"[^.]{0,25}\d",
        ],
        weak=[
            r"\b(threshold|cut-?off|operating point)\b",
            r"\bdecision curve analys\w+\b",
            r"\bnet benefit\b",
        ]),
    "Range_reported": dict(
        strong=[
            r"\bthe (improvement|increment|gain|increase|contribution|uplift|"
            r"difference|benefit)\b[^.]{0,70}\b(rang\w+|vari(es|ed))\b"
            r"[^.]{0,60}\bfrom\b[^.]{0,40}\bto\b",
            r"\brang\w+ from\b[^.]{0,45}\bto\b[^.]{0,70}"
            r"\b(depending on|across|according to)\b[^.]{0,60}"
            r"\b(baselines?|metrics?|thresholds?|feature sets?|"
            r"operating points?|measures?)\b",
            r"\b(across|over|for) (several|multiple|different|various|all|the "
            r"different) (baselines?|feature sets?|metrics?|thresholds?|"
            r"operating points?|population levels?)\b[^.]{0,150}"
            r"\b(rang\w+|vari(es|ed)|from\b[^.]{0,30}\bto)\b",
            r"\b(sensitivity|robustness) (analys\w+|check|study)\b[^.]{0,140}"
            r"\b(baselines?|metrics?|thresholds?|operating points?|"
            r"feature sets?)\b",
        ],
        weak=[
            r"\b(we|the paper) (report|present|show)s?\b[^.]{0,60}"
            r"\b(several|multiple|three|four|five|six) (metrics|measures)\b",
            r"\b(for (each|every)|under (each|all)) (metric|threshold|baseline)\b",
        ]),
}

#  AUDIT-PROTOCOL.md 5: a confidence interval is NOT a range over a choice.
_CI_DISQUALIFIER = re.compile(
    r"\b(confidence interval|credible interval|95\s?%\s?(CI|interval)|"
    r"standard (deviation|error)|\bCI\b|bootstrap interval)\b", re.I)

# --- AUDIT-PROTOCOL.md 7.2:  the SECOND implementation --------------------
#  Written against the section-5 prose.  Different vocabulary, different
#  anchors, same five questions.  It is not tuned against CODE_RULES and no
#  pattern here was copied from above.
CODE_RULES_B = {
    "B_stated": dict(
        strong=[
            r"\b(features?|attributes?|variables?|predictors?)\b[^.]{0,40}"
            r"\b(listed|enumerated|shown|given|summari[sz]ed|detailed)\b"
            r"[^.]{0,40}\b(in )?(Table|Appendix|Section)\b",
            r"\b(our|the) (baseline|reference|control)\b[^.]{0,60}"
            r"\b(uses?|employs?|contains?|has)\b[^.]{0,90}"
            r"\b(\d+ (features?|attributes?|variables?)|"
            r"(features?|attributes?|variables?) such as)\b",
            r"\b(features?|attributes?|variables?):\s*[A-Za-z][\w \-]{2,30},"
            r"\s*[A-Za-z][\w \-]{2,30},",
            r"\bconsider(ed)? the (features?|attributes?|variables?)\b"
            r"[^.]{0,40}\b(namely|specifically|i\.e\.|that is)\b",
        ],
        weak=[
            r"\b\d+ (input )?(features?|attributes?|variables?|predictors?)\b",
            r"\bfeature engineering\b",
        ]),
    "B_justified": dict(
        strong=[
            r"\b(rationale|reason|justification) for (excluding|omitting|"
            r"removing|not using)\b",
            r"\bwe (deliberately|intentionally|purposely) (exclude|omit|leave "
            r"out|do not include)\b",
            r"\b(not|never) (used|included|considered)\b[^.]{0,70}"
            r"\b(because|since|as it would|to prevent|to avoid)\b",
            r"\b(would (leak|bias|inflate)|leakage|not known at (prediction|"
            r"decision) time)\b[^.]{0,90}\b(exclud|omit|remov|drop)\w*",
        ],
        weak=[
            r"\b(only|restrict\w*) (to )?(information|data|fields?|features?)\b"
            r"[^.]{0,60}\b(available|known)\b",
            r"\bdomain (expert|knowledge)\b[^.]{0,70}\b(select|choose|chose|"
            r"exclude|omit)\w*",
        ]),
    "M_justified": dict(
        strong=[
            r"\b(motivat\w+|justif\w+|rationale)\b[^.]{0,70}"
            r"\b(metric|measure|evaluation criterion)\b",
            r"\b(metric|measure)\b[^.]{0,60}\bis (chosen|selected|used)\b"
            r"[^.]{0,90}\b(because|since|as|to)\b",
            r"\b(prefer|prefers|preferred|more (appropriate|informative|"
            r"reliable|robust))\b[^.]{0,90}\b(than|over|to)\b[^.]{0,50}"
            r"\b(accuracy|AUC|F1|precision|recall|MCC|Brier)\b",
            r"\b(imbalanc\w+|skew\w+|rare (class|event))\b[^.]{0,120}"
            r"\b(therefore|thus|hence|so) we (report|use|adopt)\b",
        ],
        weak=[
            r"\bevaluation (metrics?|measures?|criteria)\b[^.]{0,60}"
            r"\b(are|is|we use|we report)\b",
            r"\b(standard|common|widely (used|adopted)) (metric|measure)\b",
        ]),
    "Theta_stated": dict(
        strong=[
            r"\b(probability|score|risk) (threshold|cut-?off)\b",
            r"\bthreshold\w*\b[^.]{0,40}\b0\.\d+\b",
            r"\b(alarm|alert|intervention)\b[^.]{0,70}\b(threshold|cost|budget|"
            r"capacity)\b",
            r"\b(cost[- ]sensitive|cost matrix|utility function|expected "
            r"(cost|utility))\b",
            r"\barea under\b[^.]{0,80}\b(all|every|the whole|the entire)\b"
            r"[^.]{0,40}\bthreshold",
            r"\b(precision|recall)\s*@\s*\d+\b",
        ],
        weak=[
            r"\bthreshold\w*\b",
            r"\boperating (point|characteristic)\b",
        ]),
    "Range_reported": dict(
        strong=[
            r"\b(between|from)\s*[+-]?\d+(\.\d+)?\s*%?\s*(and|to|--|-|–)\s*"
            r"[+-]?\d+(\.\d+)?\s*%?\b[^.]{0,90}\b(depending|across|"
            r"according to|by (metric|baseline|threshold))\b",
            r"\b(vary|varies|varied|varying|fluctuat\w+)\b[^.]{0,90}"
            r"\b(with the choice of|by (metric|baseline|threshold|feature set)|"
            r"across (metrics|baselines|thresholds|feature sets))\b",
            r"\b(report|present|show)\w*\b[^.]{0,50}\b(a )?(surface|grid|"
            r"matrix|sweep|profile) of\b[^.]{0,60}\b(results|performance|"
            r"improvements?|gains?)\b",
            r"\b(different|alternative|several) (baselines?|reference sets?)\b"
            r"[^.]{0,120}\b(the (gain|improvement|increment)|results)\b"
            r"[^.]{0,60}\b(differ|change|vary|rang)\w*",
        ],
        weak=[
            r"\b(sensitivity analys\w+|ablation study)\b",
            r"\breport\w*\b[^.]{0,40}\bfor (each|all) (metrics?|thresholds?)\b",
        ]),
}

CODES = list(CODE_RULES)
CHOICE_CODES = ["B_stated", "M_justified", "Theta_stated", "Range_reported"]

# =========================================================================
#  AUDIT-PROTOCOL.md section 9, AMENDMENT 1 (declared 2026-08-22)
# =========================================================================
#  Three registered patterns did not implement the registered rule above
#  them.  The registered forms are NOT deleted: both codings are run and both
#  are reported, exactly as PROTOCOL.md amendment 1 reports `f_rule =
#  registered` beside `f_rule = amended`.  The amendment adds a CONTEXT
#  requirement to patterns that were matching sentences about something else.
#
#  Defect A.  The with/without class allowed its object to be `data` or
#  `information`, which admitted "Without basic knowledge over the data
#  domain".  The object must be one of the four nouns section 4 names, and
#  section 4's word "quantitative" is implemented: the ablation sentence or a
#  neighbour must carry a metric term AND a number that is not a citation
#  marker.
ABLATION_PATTERNS_AMD = [
    p.replace("|fields?|predictors?|data|information)", "|fields?|predictors?)")
     .replace("|fields?|predictors?|data sources?|information)",
              "|fields?|predictors?|data sources?)")
     .replace("|fields?|predictors?|data)", "|fields?|predictors?)")
    for p in ABLATION_PATTERNS
]
_ABLATION_AMD = [re.compile(p, re.I) for p in ABLATION_PATTERNS_AMD]
#  `ablation` on its own is unambiguous and needs no context test.
ABLATION_CONTEXT_FREE = {4}

#  A sentence whose only digits sit inside bracketed citation markers is a
#  claim about the literature, not a quantitative result.
_CITE = re.compile(r"\[[\d,;\s\-]+\]")
_PERF_WORD = re.compile(
    r"\b(performance|improv\w*|outperform\w*|accuracy|accurate|errors?|"
    r"effectiveness|predictive power|better|worse|gains?|degrad\w*|"
    r"deteriorat\w*|benefit\w*)\b", re.I)

#  Defect B.  Context vocabularies, one per code.
_EVAL_WORD = re.compile(r"\b(evaluat\w+|metric|measure|report\w*|"
                        r"performance|score[sd]?)\b", re.I)
_MODEL_WORD = re.compile(r"\b(model|classifier|baseline|predict\w*|"
                         r"training|train\b|input|regression|learner)\b", re.I)
_DECISION_WORD = re.compile(r"\b(classif\w+|predict\w*|decision|alert|alarm|"
                            r"positives?|probabilit\w+|scores?|risk|"
                            r"flag\w*|intervention)\b", re.I)
_FEATURE_WORD = re.compile(r"\b(features?|attributes?|variables?|fields?|"
                           r"predictors?|leak\w*)\b", re.I)

#  Which of a code's STRONG patterns are unambiguous on their own, by index.
#  Everything else must additionally satisfy the code's context test.
CONTEXT_FREE_STRONG = {
    "Theta_stated": {1, 2, 3, 4, 5},     # cost ratio, FP/FN cost, AUC
                                         # integrates, top-k, capacity
}
#  Strong patterns demoted to weak by the amendment, by index.
DEMOTED = {"B_stated": {2}}              # bare "Table N ... features"

CODE_CONTEXT = {
    "B_stated": _MODEL_WORD,
    "B_justified": _FEATURE_WORD,
    "M_justified": None,                 # handled specially: metric + eval
    "Theta_stated": _DECISION_WORD,
    "Range_reported": _METRIC,
}


def _numeric_result(sent):
    """A number that is not inside a bracketed citation marker."""
    return bool(_NUMBER.search(_CITE.sub(" ", sent)))


# ======================================================================
#  stage 1 -- the frame
# ======================================================================
def _oa(path, **params):
    params.setdefault("mailto", MAILTO)
    url = f"{OA}/{path}?" + urllib.parse.urlencode(params)
    for k in range(6):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 429:
            time.sleep(3 * (k + 1))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def _page_all(filt, select):
    """Every work matching `filt`, by cursor.  Deterministic order."""
    out, cursor = [], "*"
    while cursor:
        d = _oa("works", filter=filt, select=select, per_page=200, cursor=cursor)
        out += d["results"]
        cursor = d["meta"].get("next_cursor")
        if not d["results"]:
            break
        time.sleep(0.3)
    return out


SELECT = ("id,doi,title,publication_year,type,open_access,"
          "primary_location,locations,authorships")


def stage_frame():
    print("=" * 92)
    print("STAGE 1 -- THE FRAME  (AUDIT-PROTOCOL.md section 2)")
    print("=" * 92)
    frame_rows, works = [], {}

    for name, sid in VENUES.items():
        base = (f"primary_location.source.id:{sid},publication_year:{YEARS},"
                f"type:article")
        n_all = _oa("works", filter=base, per_page=1)["meta"]["count"]
        n_oa = _oa("works", filter=base + ",open_access.is_oa:true",
                   per_page=1)["meta"]["count"]
        filt = (base + ",open_access.is_oa:true,"
                f"title_and_abstract.search:{TOPICAL}")
        got = _page_all(filt, SELECT)
        frame_rows.append(dict(frame="A", venue=name, source=sid,
                               n_venue_years=n_all, n_open_access=n_oa,
                               n_after_topical=len(got)))
        print(f"  {name:32s} {n_all:5d} -> OA {n_oa:5d} -> topical {len(got):5d}")
        for w in got:
            w["_frame"] = "A"
            w["_venue"] = name
            works[w["id"]] = w

    for bid in BENCHMARK:
        filt = (f"cites:{bid},publication_year:{YEARS},"
                f"open_access.is_oa:true")
        n = _oa("works", filter=f"cites:{bid},publication_year:{YEARS}",
                per_page=1)["meta"]["count"]
        got = _page_all(filt, SELECT)
        frame_rows.append(dict(frame="B", venue=f"cites:{bid}", source=bid,
                               n_venue_years=n, n_open_access=len(got),
                               n_after_topical=len(got)))
        print(f"  cites {bid:14s}          {n:5d} -> OA {len(got):5d}")
        for w in got:
            if w["id"] not in works:
                w["_frame"] = "B"
                w["_venue"] = ((w.get("primary_location") or {})
                               .get("source") or {}).get("display_name") or ""
                works[w["id"]] = w

    pd.DataFrame(frame_rows).to_csv(RESULTS / "r40_frame.csv", index=False)

    # --- dedup on DOI, then on OpenAlex id (AUDIT-PROTOCOL.md 2.4) --------
    rows = []
    for w in works.values():
        doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
        rows.append(dict(oa_id=w["id"].rsplit("/", 1)[-1], doi=doi,
                         title=str(w.get("title"))[:200],
                         year=w.get("publication_year"),
                         frame=w["_frame"], venue=w["_venue"]))
        (META / f"{w['id'].rsplit('/', 1)[-1]}.json").write_text(
            json.dumps(w), encoding="utf-8")
    D = pd.DataFrame(rows)
    n_raw = len(D)
    D["_key"] = np.where(D.doi.astype(bool), D.doi, D.oa_id)
    D = D.sort_values("oa_id").drop_duplicates(subset="_key", keep="first")
    n_dedup = len(D)

    sampled = D
    if len(D) > CAP:
        rng = np.random.default_rng(SEED)
        idx = rng.choice(len(D), size=CAP, replace=False)
        sampled = D.iloc[np.sort(idx)]
    sampled = sampled.drop(columns="_key").reset_index(drop=True)
    sampled.to_csv(RESULTS / "r40_sample.csv", index=False)
    print(f"\n  enumerated {n_raw}  ->  deduplicated {n_dedup}  ->  "
          f"sampled {len(sampled)}  (cap {CAP}, seed {SEED})")
    return sampled


# ======================================================================
#  stage 2 -- full text
# ======================================================================
def _pdf_candidates(meta, doi):
    urls = []
    b = meta.get("best_oa_location") or {}
    if b.get("pdf_url"):
        urls.append(b["pdf_url"])
    for loc in meta.get("locations") or []:
        u = loc.get("pdf_url")
        if u and u not in urls:
            urls.append(u)
    if doi.startswith("10.1007/"):
        urls.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
    for loc in (meta.get("locations") or []):
        lp = str((loc.get("landing_page_url") or ""))
        m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", lp)
        if m:
            urls.append(f"https://arxiv.org/pdf/{m.group(1)}")
    if b.get("landing_page_url"):
        urls.append(b["landing_page_url"])
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _extract(pdf_bytes):
    import fitz
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        pages = [p.get_text() for p in doc]
    return PAGE_SEP.join(pages), len(pages)


def _fetch_one(rec):
    oa_id, doi = rec["oa_id"], rec["doi"]
    cache = TEXTS / f"{oa_id}.txt.gz"
    if cache.exists():
        return oa_id, "cached", ""
    mp = META / f"{oa_id}.json"
    if not mp.exists():
        return oa_id, "NO_META", ""
    meta = json.loads(mp.read_text(encoding="utf-8"))
    for url in _pdf_candidates(meta, doi):
        try:
            r = requests.get(url, headers=UA, timeout=45)
        except Exception:                                   # noqa: BLE001
            continue
        if r.status_code != 200:
            continue
        if "pdf" not in r.headers.get("content-type", "").lower() \
                and not r.content[:5].startswith(b"%PDF"):
            continue
        try:
            text, npages = _extract(r.content)
        except Exception:                                   # noqa: BLE001
            continue
        if len(text) < MIN_CHARS or npages < MIN_PAGES:
            continue
        with gzip.open(cache, "wt", encoding="utf-8") as fh:
            fh.write(text)
        return oa_id, "ok", url
    return oa_id, "NO_FULLTEXT", ""


def stage_fetch(sample):
    print("=" * 92)
    print("STAGE 2 -- FULL TEXT  (AUDIT-PROTOCOL.md section 3)")
    print("=" * 92)
    recs = sample.to_dict("records")
    done = 0
    out = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for oa_id, status, url in ex.map(_fetch_one, recs):
            out.append(dict(oa_id=oa_id, fulltext=status, source_url=url))
            done += 1
            if done % 50 == 0:
                print(f"    {done}/{len(recs)}", flush=True)
    F = pd.DataFrame(out)
    n_ok = int((F.fulltext.isin(["ok", "cached"])).sum())
    print(f"  full text retrieved for {n_ok} of {len(F)} "
          f"({n_ok / max(1, len(F)):.1%})")
    return F


# ======================================================================
#  stage 3 -- screen and code
# ======================================================================
_SENT = re.compile(r"[^.!?]{15,600}[.!?]")


def _sentences_with_pages(text):
    """(sentence, 1-based pdf page) for every sentence in the extracted text."""
    out = []
    for pi, page in enumerate(text.split(PAGE_SEP), start=1):
        flat = re.sub(r"-\n", "", page)
        flat = re.sub(r"\s+", " ", flat)
        for m in _SENT.finditer(flat):
            out.append((m.group(0).strip(), pi))
    return out


def _first_match(sents, pats, ctx=None, skip=()):
    """First sentence matching any pattern, optionally in a context.

    `ctx(sentence, index) -> bool` is the amendment-1 context test; without it
    the behaviour is the registered one.  `skip` names pattern indices the
    context test does not apply to, because those patterns are unambiguous on
    their own.
    """
    for i, (s, pg) in enumerate(sents):
        for k, p in enumerate(pats):
            if not p.search(s):
                continue
            if ctx is not None and k not in skip and not ctx(s, i):
                continue
            return s[:300], pg
    return "", 0


def _screen(sents):
    metric = any(_METRIC.search(s) and _NUMBER.search(s) for s, _ in sents)
    q, pg = _first_match(sents, _ABLATION)
    if not metric:
        return "NO_METRIC", "", 0
    if not q:
        return "NO_ABLATION", "", 0
    return "INCLUDED", q, pg


def _screen_amd(sents):
    """AUDIT-PROTOCOL.md amendment 1, defect A.

    "Quantitative" is tested at the DOCUMENT level, which is where section 4
    puts it: condition (M) already requires a metric term beside a number that
    is not a citation marker.  The sentence-level test is that the ablation
    sentence is about PERFORMANCE and is not a bare claim about the
    literature.  A first attempt made the number a sentence-neighbourhood
    requirement and cut the included set from 117 to 15, because most papers
    state the ablation in prose and put the numbers in a table; that attempt
    is recorded in AUDIT-PROTOCOL.md amendment 1 and is not what runs.
    """
    metric = any(_METRIC.search(s) and _numeric_result(s) for s, _ in sents)

    def about_performance(sent, i):
        if _CITE.search(sent) and not _numeric_result(sent):
            return False        # a claim about other people's papers
        return bool(_METRIC.search(sent) or _PERF_WORD.search(sent))

    q, pg = _first_match(sents, _ABLATION_AMD, ctx=about_performance,
                         skip=ABLATION_CONTEXT_FREE)
    if not metric:
        return "NO_METRIC", "", 0
    if not q:
        return "NO_ABLATION", "", 0
    return "INCLUDED", q, pg


def _apply(rules, sents, amended=False):
    """One code per rule.  strong -> yes, weak-only -> unclear, else no."""
    out = {}
    for code, spec in rules.items():
        strong_src = list(spec["strong"])
        weak_src = list(spec["weak"])
        ctx, skip = None, ()
        if amended:
            dem = DEMOTED.get(code, set())
            if dem:
                weak_src = weak_src + [strong_src[i] for i in sorted(dem)]
                strong_src = [p for i, p in enumerate(strong_src)
                              if i not in dem]
                skip = ()
            else:
                skip = CONTEXT_FREE_STRONG.get(code, ())
            cw = CODE_CONTEXT[code]
            if code == "M_justified":
                def ctx(s, i):
                    return bool(_METRIC.search(s) and _EVAL_WORD.search(s))
            elif cw is not None:
                def ctx(s, i, _cw=cw):
                    return bool(_cw.search(s))
        strong = [re.compile(p, re.I) for p in strong_src]
        weak = [re.compile(p, re.I) for p in weak_src]
        q, pg = _first_match(sents, strong, ctx=ctx, skip=skip)
        if q and code == "Range_reported" and _CI_DISQUALIFIER.search(q):
            #  AUDIT-PROTOCOL.md 5: an interval that is a CI is not a range
            #  over a choice.  Look past it for one that is not.
            q2, pg2 = "", 0
            for i, (s, p) in enumerate(sents):
                if any(r.search(s) for r in strong) \
                        and not _CI_DISQUALIFIER.search(s) \
                        and (ctx is None or ctx(s, i)):
                    q2, pg2 = s[:300], p
                    break
            q, pg = q2, pg2
        if q:
            out[code] = ("yes", q, pg)
            continue
        q, pg = _first_match(sents, weak)
        out[code] = ("unclear", q, pg) if q else ("no", "", 0)
    return out


def _code_one(rec):
    oa_id = rec["oa_id"]
    cache = TEXTS / f"{oa_id}.txt.gz"
    if not cache.exists():
        return dict(oa_id=oa_id, screen="NO_FULLTEXT", screen_amd="NO_FULLTEXT")
    try:
        with gzip.open(cache, "rt", encoding="utf-8") as fh:
            text = fh.read()
    except Exception as e:                                  # noqa: BLE001
        return dict(oa_id=oa_id, screen="PARSE_FAILED",
                    screen_amd="PARSE_FAILED", detail=f"{type(e).__name__}")
    sents = _sentences_with_pages(text)
    status, q, pg = _screen(sents)
    status_a, qa, pga = _screen_amd(sents)
    row = dict(oa_id=oa_id, screen=status, screen_amd=status_a,
               include_quote=q, include_page=pg,
               include_quote_amd=qa, include_page_amd=pga,
               n_sentences=len(sents), n_chars=len(text),
               n_pages=text.count(PAGE_SEP) + 1)
    if "INCLUDED" not in (status, status_a):
        return row
    for code, (v, quote, page) in _apply(CODE_RULES, sents).items():
        row[f"{code}_reg"] = v
    for code, (v, quote, page) in _apply(CODE_RULES, sents,
                                         amended=True).items():
        row[code] = v
        row[f"{code}_quote"] = quote
        row[f"{code}_pdf_page"] = page
    for code, (v, quote, page) in _apply(CODE_RULES_B, sents,
                                         amended=True).items():
        row[f"{code}_B"] = v
    return row


def stage_code(sample):
    print("=" * 92)
    print("STAGE 3 -- SCREEN AND CODE  (AUDIT-PROTOCOL.md sections 4-5)")
    print("=" * 92)
    recs = sample.to_dict("records")
    rows, done = [], 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(_code_one, recs):
            rows.append(r)
            done += 1
            if done % 100 == 0:
                print(f"    {done}/{len(recs)}", flush=True)
    C = pd.DataFrame(rows)
    S = sample.merge(C, on="oa_id", how="left")
    S.to_csv(RESULTS / "r40_screening.csv", index=False)
    INC = S[S.screen_amd == "INCLUDED"].copy()
    keep = (["oa_id", "doi", "title", "year", "frame", "venue",
             "include_quote_amd", "include_page_amd", "screen"]
            + [c for code in CODES
               for c in (code, f"{code}_quote", f"{code}_pdf_page",
                         f"{code}_reg", f"{code}_B")])
    INC[[c for c in keep if c in INC.columns]].to_csv(
        RESULTS / "r40_coding.csv", index=False)
    print(f"  screened {len(S)}")
    print(f"  registered screen included {int((S.screen == 'INCLUDED').sum())}; "
          f"amended screen included {len(INC)}")
    print(pd.crosstab(S.screen, S.screen_amd).to_string())
    return S, INC


# ======================================================================
#  stage 4 -- report
# ======================================================================
def wilson(k, n, z=1.959963985):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return float((c - h) / d), float((c + h) / d)


def cohen_kappa(a, b, labels=("yes", "no", "unclear")):
    a, b = list(a), list(b)
    n = len(a)
    if n == 0:
        return np.nan
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    if pe >= 1 - 1e-12:
        return 1.0 if po >= 1 - 1e-12 else np.nan
    return float((po - pe) / (1 - pe))


def stage_report(S, INC):
    print("=" * 92)
    print("STAGE 4 -- THE REPORT  (AUDIT-PROTOCOL.md sections 6-7)")
    print("=" * 92)
    n_inc = len(INC)

    # --- the funnel ---------------------------------------------------
    funnel = [
        dict(step="enumerated and deduplicated", n=len(S)),
        dict(step="full text retrieved",
             n=int((S.screen_amd != "NO_FULLTEXT").sum())),
        dict(step="reports a quantitative performance metric",
             n=int((~S.screen_amd.isin(["NO_FULLTEXT", "PARSE_FAILED",
                                        "NO_METRIC"])).sum())),
        dict(step="included, amended screen", n=n_inc),
        dict(step="included, registered screen",
             n=int((S.screen == "INCLUDED").sum())),
    ]
    for code, k in S.screen_amd.value_counts().items():
        if code != "INCLUDED":
            funnel.append(dict(step=f"excluded: {code}", n=int(k)))
    pd.DataFrame(funnel).to_csv(RESULTS / "r40_funnel.csv", index=False)
    for f in funnel:
        print(f"  {f['step']:44s} {f['n']:5d}")

    # --- the five proportions, under BOTH codings ----------------------
    #  AUDIT-PROTOCOL.md amendment 1: the registered coding is reported
    #  beside the amended one, on each screen's own included set, so a reader
    #  can see what the amendment did to every proportion.
    REG = S[S.screen == "INCLUDED"]
    prop = []
    for code in CODES:
        yes = int((INC[code] == "yes").sum())
        unc = int((INC[code] == "unclear").sum())
        no = int((INC[code] == "no").sum())
        lo, hi = wilson(yes, n_inc)
        ryes = int((REG[f"{code}_reg"] == "yes").sum())
        prop.append(dict(code=code, n=n_inc, yes=yes, no=no, unclear=unc,
                         p_yes=yes / n_inc if n_inc else np.nan,
                         lo=lo, hi=hi, n_reg=len(REG), yes_reg=ryes,
                         p_yes_reg=ryes / max(1, len(REG)),
                         shift=(yes / n_inc if n_inc else np.nan)
                         - ryes / max(1, len(REG))))
    P = pd.DataFrame(prop)
    P.to_csv(RESULTS / "r40_proportions.csv", index=False)
    print()
    print(P.to_string(index=False))

    #  the same five proportions under the SECOND implementation, on the
    #  whole included set.  Per-paper agreement is reported below and is
    #  poor; the marginal proportions are what the paper prints, so the
    #  reader is entitled to see whether THEY move.
    propB = []
    for code in CODES:
        yes = int((INC[f"{code}_B"] == "yes").sum())
        lo, hi = wilson(yes, n_inc)
        propB.append(dict(code=code, n=n_inc, yes_B=yes,
                          p_yes_B=yes / n_inc if n_inc else np.nan,
                          lo=lo, hi=hi,
                          p_yes_A=float(P[P.code == code].p_yes.iloc[0]),
                          marginal_shift=abs(
                              yes / max(1, n_inc)
                              - float(P[P.code == code].p_yes.iloc[0]))))
    PB = pd.DataFrame(propB)
    PB.to_csv(RESULTS / "r40_proportions_B.csv", index=False)
    print("\n  the same five proportions under the second implementation:")
    print(PB.to_string(index=False))

    # --- the joint distribution ---------------------------------------
    k = (INC[CHOICE_CODES] == "yes").sum(axis=1)
    joint = (k.value_counts().reindex(range(0, 5), fill_value=0)
             .rename_axis("n_choices_stated").reset_index(name="n_papers"))
    joint["share"] = joint.n_papers / max(1, n_inc)
    joint.to_csv(RESULTS / "r40_joint.csv", index=False)
    print("\n  how many of the four choices a paper states:")
    print(joint.to_string(index=False))

    # --- venue and year mix -------------------------------------------
    mix = (INC.groupby(["frame", "venue"]).size()
           .rename("n").reset_index().sort_values("n", ascending=False))
    mix.to_csv(RESULTS / "r40_venue_mix.csv", index=False)
    yr = INC.year.value_counts().sort_index().rename_axis("year") \
        .reset_index(name="n")
    yr.to_csv(RESULTS / "r40_year_mix.csv", index=False)

    # --- AUDIT-PROTOCOL.md 7.2: the second implementation, on a 20% ----
    rng = np.random.default_rng(SEED)
    m = max(1, int(round(0.20 * n_inc)))
    pick = np.sort(rng.choice(n_inc, size=m, replace=False))
    R = INC.iloc[pick]
    kap = []
    for code in CODES:
        kap.append(dict(code=code, n=len(R),
                        agree=int((R[code] == R[f"{code}_B"]).sum()),
                        agreement=float((R[code] == R[f"{code}_B"]).mean()),
                        kappa=cohen_kappa(R[code], R[f"{code}_B"])))
    K = pd.DataFrame(kap)
    K.to_csv(RESULTS / "r40_kappa.csv", index=False)
    dis = R[(R[CODES].values != R[[f"{c}_B" for c in CODES]].values).any(axis=1)]
    dis[["oa_id", "doi", "title"] + CODES + [f"{c}_B" for c in CODES]] \
        .to_csv(RESULTS / "r40_kappa_disagreements.csv", index=False)
    print("\n  two implementations of the same five rules, on a random 20%:")
    print(K.to_string(index=False))
    print(f"  {len(dis)} of {len(R)} papers disagree on at least one code; "
          f"listed in r40_kappa_disagreements.csv")

    # --- AUDIT-PROTOCOL.md 7.3 + amendment 2: the validation subsample --
    m2 = min(30, n_inc)
    pick2 = np.sort(rng.choice(n_inc, size=m2, replace=False))
    VS = INC.iloc[pick2]
    VS[["oa_id", "doi", "title", "year", "venue"] + CODES] \
        .to_csv(RESULTS / "r40_validation_sample.csv", index=False)

    #  AUDIT-PROTOCOL.md amendment 2.  The adjudication is the primary
    #  evidence and the mechanical coding is a LOWER BOUND whose
    #  under-detection is measured here rather than assumed away.  Agreement
    #  is computed on the papers a read of the paper CONFIRMS are includable;
    #  the screen's own precision is reported beside it.
    adj_rows, ADJ, M, INC_ADJ = [], None, None, None
    ap = RESULTS / "r40_adjudication.csv"
    if ap.exists():
        ADJ = pd.read_csv(ap)
        M = VS.merge(ADJ, on="oa_id", how="inner")
        INC_ADJ = M[M.included_adj == "yes"]
        for code in CODES:
            a, b = M[code], M[f"{code}_adj"]
            aa, bb = INC_ADJ[code], INC_ADJ[f"{code}_adj"]
            yes_a = int((bb == "yes").sum())
            lo, hi = wilson(yes_a, len(INC_ADJ))
            adj_rows.append(dict(
                code=code, n=len(INC_ADJ),
                mech_yes=int((aa == "yes").sum()), adj_yes=yes_a,
                p_yes_mech=int((aa == "yes").sum()) / max(1, len(INC_ADJ)),
                p_yes_adj=yes_a / max(1, len(INC_ADJ)), lo=lo, hi=hi,
                agreement=float((a == b).mean()),
                kappa=cohen_kappa(a, b),
                mech_false_yes=int(((aa == "yes") & (bb != "yes")).sum()),
                mech_missed=int(((aa != "yes") & (bb == "yes")).sum())))
        A = pd.DataFrame(adj_rows)
        A.to_csv(RESULTS / "r40_adjudication_agreement.csv", index=False)
        print(f"\n  the screen's precision: {len(INC_ADJ)} of {len(M)} "
              f"({len(INC_ADJ) / max(1, len(M)):.1%}) of the papers the "
              f"amended screen admitted are confirmed includable by a read")
        print("\n  the mechanical coder against a read of the paper "
              f"({len(INC_ADJ)} confirmed-includable papers):")
        print(A.to_string(index=False))

        #  WHICH AXIS the range was reported over.  The four choices are not
        #  reported at equal rates and averaging them would hide that.
        #  A paper can report a range over more than one axis, so these
        #  shares are NOT exclusive and must not be summed.
        rows_ax = []
        for a_ in ("baseline", "metric", "threshold", "population"):
            n_ = int(INC_ADJ.range_axes_adj.str.contains(a_).sum())
            lo_, hi_ = wilson(n_, len(INC_ADJ))
            rows_ax.append(dict(axis=a_, n=n_,
                                share=n_ / max(1, len(INC_ADJ)),
                                lo=lo_, hi=hi_))
        n2 = int((INC_ADJ.range_axes_adj.str.count(";") >= 1).sum())
        lo_, hi_ = wilson(n2, len(INC_ADJ))
        rows_ax.append(dict(axis="two or more axes", n=n2,
                            share=n2 / max(1, len(INC_ADJ)), lo=lo_, hi=hi_))
        n0 = int((INC_ADJ.range_axes_adj == "none").sum())
        lo_, hi_ = wilson(n0, len(INC_ADJ))
        rows_ax.append(dict(axis="no axis", n=n0,
                            share=n0 / max(1, len(INC_ADJ)), lo=lo_, hi=hi_))
        ax = pd.DataFrame(rows_ax)
        ax.to_csv(RESULTS / "r40_range_axis.csv", index=False)
        print("\n  when a range IS reported, which choice is it over "
              "(shares are NOT exclusive):")
        print(ax.to_string(index=False))

    zero = int((k == 0).sum())
    fac = dict(
        n_frame=len(S), n_included=n_inc,
        n_included_registered=int((S.screen == "INCLUDED").sum()),
        n_fulltext=int((S.screen_amd != "NO_FULLTEXT").sum()),
        include_rate=n_inc / max(1, int((S.screen_amd != "NO_FULLTEXT").sum())),
        n_zero_choices=zero, share_zero_choices=zero / max(1, n_inc),
        n_all_four=int((k == 4).sum()),
        n_venues=int(INC.venue.nunique()),
        min_kappa=float(K.kappa.min()), mean_kappa=float(K.kappa.mean()),
        max_marginal_shift=float(PB.marginal_shift.max()),
        max_amendment_shift=float(P["shift"].abs().max()),
        p_B_stated=float(P[P.code == "B_stated"].p_yes.iloc[0]),
        p_B_justified=float(P[P.code == "B_justified"].p_yes.iloc[0]),
        p_M_justified=float(P[P.code == "M_justified"].p_yes.iloc[0]),
        p_Theta_stated=float(P[P.code == "Theta_stated"].p_yes.iloc[0]),
        p_Range_reported=float(P[P.code == "Range_reported"].p_yes.iloc[0]),
    )
    if adj_rows:
        A = pd.DataFrame(adj_rows)
        _ax = pd.read_csv(RESULTS / "r40_range_axis.csv").set_index("axis")
        fac.update(n_adjudicated=int(A.n.iloc[0]),
                   n_adjudication_read=int(len(M)),
                   screen_precision=len(INC_ADJ) / max(1, len(M)),
                   adj_mean_agreement=float(A.agreement.mean()),
                   adj_min_agreement=float(A.agreement.min()),
                   adj_mean_kappa=float(A.kappa.mean()),
                   adj_total_missed=int(A.mech_missed.sum()),
                   adj_total_false_yes=int(A.mech_false_yes.sum()),
                   share_range_baseline=float(_ax.loc["baseline"].share),
                   share_range_metric=float(_ax.loc["metric"].share),
                   share_range_threshold=float(_ax.loc["threshold"].share),
                   share_range_population=float(_ax.loc["population"].share),
                   n_range_threshold=int(_ax.loc["threshold"].n),
                   n_range_population=int(_ax.loc["population"].n),
                   hi_range_threshold=float(_ax.loc["threshold"].hi),
                   share_range_two_axes=float(_ax.loc["two or more axes"].share),
                   p_B_stated_adj=float(A[A.code == "B_stated"].p_yes_adj.iloc[0]),
                   p_M_justified_adj=float(A[A.code == "M_justified"].p_yes_adj.iloc[0]),
                   p_Theta_stated_adj=float(A[A.code == "Theta_stated"].p_yes_adj.iloc[0]),
                   p_Range_reported_adj=float(A[A.code == "Range_reported"].p_yes_adj.iloc[0]),
                   p_B_justified_adj=float(A[A.code == "B_justified"].p_yes_adj.iloc[0]))
    F = pd.DataFrame([fac])
    F.to_csv(RESULTS / "r40_facts.csv", index=False)
    print("\n" + F.T.to_string())

    # --- AUDIT-PROTOCOL.md 1: is the premise refuted? ------------------
    #  Evaluated on the ADJUDICATED subsample where one exists, because
    #  amendment 2 makes that the primary evidence and the mechanical coding
    #  a measured lower bound.  Both are printed.
    b = float(P[P.code == "B_stated"].p_yes.iloc[0])
    m_ = float(P[P.code == "M_justified"].p_yes.iloc[0])
    print("\n" + "=" * 92)
    print(f"  mechanical, n={n_inc}:   B_stated {b:.1%}   M_justified {m_:.1%}")
    if adj_rows:
        A = pd.DataFrame(adj_rows)
        ba = float(A[A.code == "B_stated"].p_yes_adj.iloc[0])
        ma = float(A[A.code == "M_justified"].p_yes_adj.iloc[0])
        print(f"  adjudicated, n={int(A.n.iloc[0])}:  B_stated {ba:.1%}   "
              f"M_justified {ma:.1%}   <- the primary evidence")
        b, m_ = ba, ma
    if b > 0.5 and m_ > 0.5:
        print("\nTHE PREMISE IS REFUTED BY ITS OWN REGISTERED CRITERION.")
        print("A majority state the baseline AND a majority justify the "
              "metric.  AUDIT-PROTOCOL.md section 1 says what happens now.")
    else:
        print("\nThe premise is NOT refuted by the registered criterion "
              f"(B_stated {b:.1%}, M_justified {m_:.1%}; a majority on both "
              "was required).")
        if b > 0.25 or m_ > 0.25:
            print("But the STRONG wording -- 'a large majority state none of "
                  "the four' -- is NOT supported and the paper must not use "
                  "it.  What the audit supports is narrower and is in "
                  "r40_range_axis.csv.")
    print("=" * 92)


# ======================================================================
#  AUDIT-PROTOCOL.md amendment 2 -- the adjudication extract
# ======================================================================
#  The extract is DETERMINISTIC and is written to disk, so the evidence the
#  human codes were assigned from is as auditable as the mechanical codes.
#  It is not a summary and nothing here decides anything: it selects
#  sentences by declared vocabulary and prints them with their page numbers.
_EX_BUCKETS = {
    "metric result": lambda s: bool(_METRIC.search(s) and _numeric_result(s)),
    "baseline / features": lambda s: bool(
        re.search(r"\b(baseline|base model|reference model|features?|"
                  r"attributes?|variables?|predictors?|feature set)\b", s, re.I)),
    "metric choice": lambda s: bool(
        _METRIC.search(s) and re.search(r"\b(because|since|we (use|report|"
                                        r"adopt|choose|chose|select)|"
                                        r"imbalanc\w+|comparab\w+)\b", s, re.I)),
    "threshold / cost": lambda s: bool(
        re.search(r"\b(threshold|cut-?off|operating point|cost|utility|"
                  r"top-?\d+|top-?k|capacity|false (positive|negative))\b",
                  s, re.I)),
    "range over a choice": lambda s: bool(
        re.search(r"\b(rang\w+|vari(es|ed|ation)|sensitivity analys\w+|"
                  r"ablation|across (metrics|baselines|thresholds)|"
                  r"depending on)\b", s, re.I)),
}
MAX_PER_BUCKET = 14


def stage_extract():
    S = pd.read_csv(RESULTS / "r40_screening.csv")
    INC = S[S.screen_amd == "INCLUDED"].reset_index(drop=True)
    rng = np.random.default_rng(SEED)
    _ = rng.choice(len(INC), size=max(1, int(round(0.20 * len(INC)))),
                   replace=False)              # the kappa draw, consumed first
    pick = np.sort(rng.choice(len(INC), size=min(30, len(INC)), replace=False))
    out = AUDIT / "adjudication"
    out.mkdir(parents=True, exist_ok=True)
    for _, r in INC.iloc[pick].iterrows():
        with gzip.open(TEXTS / f"{r.oa_id}.txt.gz", "rt",
                       encoding="utf-8") as fh:
            text = fh.read()
        sents = _sentences_with_pages(text)
        lines = [f"# {r.oa_id}   {r.doi}", f"# {r.title}",
                 f"# {r.venue}  {r.year}",
                 f"# admitted by: {r.include_quote_amd}", ""]
        for bucket, test in _EX_BUCKETS.items():
            hits = [(s, pg) for s, pg in sents if test(s)][:MAX_PER_BUCKET]
            lines.append(f"## {bucket}  ({len(hits)} shown)")
            for s, pg in hits:
                lines.append(f"  [p{pg}] {s}")
            lines.append("")
        (out / f"{r.oa_id}.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote {len(pick)} adjudication extracts to {out}")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--code", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--extract", action="store_true")
    a = ap.parse_args(argv)
    if a.extract:
        stage_extract()
        return
    allst = not (a.frame or a.fetch or a.code or a.report)
    t0 = time.time()

    sample = None
    if a.frame or allst:
        sample = stage_frame()
    if sample is None and (RESULTS / "r40_sample.csv").exists():
        sample = pd.read_csv(RESULTS / "r40_sample.csv")
        sample["doi"] = sample.doi.fillna("").astype(str)
    if a.fetch or allst:
        stage_fetch(sample)
    if a.code or allst:
        stage_code(sample)
    if a.report or allst:
        S = pd.read_csv(RESULTS / "r40_screening.csv")
        INC = S[S.screen_amd == "INCLUDED"].copy()
        stage_report(S, INC)
    print(f"\nr40 done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1:])

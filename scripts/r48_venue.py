"""r48 -- THE VENUE DECISION, RE-TAKEN AGAINST STATED CRITERIA.

PLAN-REVIEWER-PROOF.md section 8.  The paper was retargeted to *Information
Systems* in round fifteen when it was a CMDB empirical study.  Its centre of
gravity is now evaluation methodology with a CMDB demonstration, a literature
audit, three propositions, a prospective test and a tool.  That may not be the
same journal's paper, and an inherited decision is worth less than a
re-examined one -- including when the re-examination changes nothing.

WHAT THIS SCRIPT COLLECTS, and it is only the machine-collectable half.
Criterion 6 -- "does the venue accept single-author unaffiliated submissions
IN PRACTICE?  Check by counting, not by assuming" -- is the one that matters
most to this paper and the one OpenAlex can answer exactly:

    n_recent               research articles 2024-2026
    share_single_author    exactly one authorship
    share_no_affiliation   at least one author with no institution recorded
    share_single_unaff     BOTH: one author, and that author unaffiliated
    median_authors         the norm the paper is being read against
    share_topical          the share of recent articles whose title/abstract
                           carries this paper's own vocabulary

WHAT IT CANNOT COLLECT, and says so rather than guessing: scope statements,
page limits and time-to-first-decision are on publisher pages that are not an
API, they change, and a number scraped from a marketing page is not evidence.
Those three go to `submission/OWNER-ACTIONS.md` with the exact URL to read.

Outputs: results/r48_venue.csv, r48_facts.csv
"""
import sys
import time
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

MAILTO = "sudhir.dixit1@gmail.com"
UA = {"User-Agent": f"emptycmdb-venue/1.0 (mailto:{MAILTO})"}
OA = "https://api.openalex.org"
YEARS = "2024-2026"
PAGES = 5                      # 200 works per page; enough for every candidate

#  PLAN-REVIEWER-PROOF.md section 8.2's candidate list, plus the two venues
#  round sixteen's scoring named and this round should not silently drop.
CANDIDATES = {
    "Information Systems (incumbent)": "S193006928",
    "Empirical Software Engineering": "S109852484",
    "ACM TOSEM": "S142627899",
    "Decision Support Systems": "S11479521",
    "Information & Management": "S38883057",
    "Journal of Systems and Software": "S37879656",
    "Business & Information Systems Engineering": "S27339233",
    "ACM TMIS": "S4210170305",
}

#  The paper's own vocabulary, as a declared query.  A venue that publishes
#  none of this is a venue this paper would arrive at cold.
TOPICAL = ('("incremental value" OR "feature importance" OR "variable '
           'importance" OR baseline OR "evaluation metric" OR "predictive '
           'process monitoring" OR "decision curve" OR reproducibility)')

#  Criterion 1-4 are judgements about published policy, not counts.  They are
#  recorded here as DECLARED values with the URL a reader checks them against,
#  so the table is auditable even though it is not machine-collected.
DECLARED = {
    "Information Systems (incumbent)": dict(
        publishes_methodology="yes", artifact_track="no formal track",
        publishes_audits="rare", length_guidance="no hard limit",
        url="https://www.sciencedirect.com/journal/information-systems"),
    "Empirical Software Engineering": dict(
        publishes_methodology="yes", artifact_track="open science policy, "
        "badges via ROSE festival at co-located venues",
        publishes_audits="yes, systematic reviews are a standing category",
        length_guidance="no hard limit",
        url="https://link.springer.com/journal/10664"),
    "ACM TOSEM": dict(
        publishes_methodology="yes", artifact_track="ACM artifact badging",
        publishes_audits="yes", length_guidance="no hard limit",
        url="https://dl.acm.org/journal/tosem"),
    "Decision Support Systems": dict(
        publishes_methodology="some", artifact_track="no",
        publishes_audits="rare", length_guidance="no hard limit",
        url="https://www.sciencedirect.com/journal/decision-support-systems"),
    "Information & Management": dict(
        publishes_methodology="rare", artifact_track="no",
        publishes_audits="rare", length_guidance="no hard limit",
        url="https://www.sciencedirect.com/journal/information-and-management"),
    "Journal of Systems and Software": dict(
        publishes_methodology="yes", artifact_track="open science badges",
        publishes_audits="yes", length_guidance="no hard limit",
        url="https://www.sciencedirect.com/journal/journal-of-systems-and-software"),
    "Business & Information Systems Engineering": dict(
        publishes_methodology="some", artifact_track="no",
        publishes_audits="some", length_guidance="research papers are short",
        url="https://link.springer.com/journal/12599"),
    "ACM TMIS": dict(
        publishes_methodology="some", artifact_track="ACM artifact badging",
        publishes_audits="rare", length_guidance="no hard limit",
        url="https://dl.acm.org/journal/tmis"),
}


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


def works(sid):
    out, cursor, page = [], "*", 0
    while cursor and page < PAGES:
        d = _oa("works", filter=f"primary_location.source.id:{sid},"
                                f"publication_year:{YEARS},type:article",
                select="id,doi,publication_year,authorships", per_page=200,
                cursor=cursor)
        out += d["results"]
        cursor = d["meta"].get("next_cursor")
        page += 1
        if not d["results"]:
            break
        time.sleep(0.3)
    return out


def main():
    t0 = time.time()
    print("=" * 100)
    print(f"r48 -- the venue decision, re-taken.  Counts are over {YEARS}.")
    print("=" * 100)
    rows = []
    for name, sid in CANDIDATES.items():
        W = works(sid)
        n = len(W)
        if n == 0:
            print(f"  {name:44s} no works returned")
            continue
        n_auth = np.array([len(w.get("authorships") or []) for w in W])
        single = n_auth == 1
        unaff = np.array([
            any(not (a.get("institutions") or []) for a in
                (w.get("authorships") or []))
            for w in W])
        single_unaff = single & unaff
        topical = _oa("works", filter=f"primary_location.source.id:{sid},"
                                      f"publication_year:{YEARS},type:article,"
                                      f"title_and_abstract.search:{TOPICAL}",
                      per_page=1)["meta"]["count"]
        #  PLAN-REVIEWER-PROOF.md 8.2: "a registered-reports track deserves
        #  special attention."  Whether one exists is checkable by counting
        #  papers that say so, over the whole 2019-2026 window rather than
        #  the recent one, because such a track produces few papers a year.
        rr = _oa("works", filter=f"primary_location.source.id:{sid},"
                                 f"publication_year:2019-2026,"
                                 f'title_and_abstract.search:"registered report"',
                 per_page=1)["meta"]["count"]
        d = dict(venue=name, source=sid, n_recent=n,
                 median_authors=float(np.median(n_auth)),
                 mean_authors=float(n_auth.mean()),
                 n_single_author=int(single.sum()),
                 share_single_author=float(single.mean()),
                 n_no_affiliation=int(unaff.sum()),
                 share_no_affiliation=float(unaff.mean()),
                 n_single_unaffiliated=int(single_unaff.sum()),
                 share_single_unaffiliated=float(single_unaff.mean()),
                 n_topical=topical, share_topical=topical / n,
                 n_registered_reports=rr)
        d.update(DECLARED.get(name, {}))
        rows.append(d)
        print(f"  {name:44s} n={n:5d}  authors median {np.median(n_auth):.0f}  "
              f"single {single.mean():6.1%}  unaffiliated {unaff.mean():6.1%}  "
              f"single+unaffiliated {single_unaff.mean():6.1%}  "
              f"topical {topical / n:6.1%}  reg.reports {rr:3d}",
              flush=True)
        time.sleep(0.5)

    V = pd.DataFrame(rows)
    V.to_csv(RESULTS / "r48_venue.csv", index=False)
    inc = V[V.venue.str.startswith("Information Systems")]
    best_unaff = V.loc[V.share_single_unaffiliated.idxmax()]
    best_top = V.loc[V.share_topical.idxmax()]
    F = pd.DataFrame([dict(
        n_venues=len(V), years=YEARS, n_works=int(V.n_recent.sum()),
        incumbent_single_unaffiliated=float(inc.share_single_unaffiliated.iloc[0]),
        incumbent_n_single_unaffiliated=int(inc.n_single_unaffiliated.iloc[0]),
        incumbent_share_topical=float(inc.share_topical.iloc[0]),
        incumbent_median_authors=float(inc.median_authors.iloc[0]),
        best_single_unaffiliated_venue=str(best_unaff.venue),
        best_single_unaffiliated_share=float(best_unaff.share_single_unaffiliated),
        best_topical_venue=str(best_top.venue),
        best_topical_share=float(best_top.share_topical),
        incumbent_registered_reports=int(inc.n_registered_reports.iloc[0]),
        max_registered_reports=int(V.n_registered_reports.max()),
        best_registered_reports_venue=str(
            V.loc[V.n_registered_reports.idxmax()].venue),
        min_single_unaffiliated=float(V.share_single_unaffiliated.min()),
        max_single_unaffiliated=float(V.share_single_unaffiliated.max()),
        runtime_s=round(time.time() - t0, 1))])
    F.to_csv(RESULTS / "r48_facts.csv", index=False)
    print("\n" + F.T.to_string())
    print("\n  Criteria 1-5 are not machine-collectable and are NOT guessed "
          "here: scope, artifact track,\n  page limit and time-to-decision go "
          "to submission/OWNER-ACTIONS.md with the URL to read.")
    print(f"\nWrote r48_venue.csv, r48_facts.csv ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

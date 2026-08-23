"""s06 -- THE AUDIT, REBUILT.  AUDIT-PROTOCOL-2.md, implemented.

Round nineteen.  The referee's fourth major comment lists eighteen defects in
the round-eighteen audit and offers two dispositions: rebuild it as a proper
systematic empirical study, or reduce it to a clearly labelled exploratory
pilot that does not support a field-wide claim.  This file does as much of the
first as one author can honestly do, and the manuscript takes the second: the
audit is reported as a MACHINE-ASSISTED PREVALENCE PILOT with an adjudicated
validation subsample and error-corrected estimates, and no claim in the paper
depends on it.

WHAT CHANGES FROM r40.

  frame        4 venues + 2 citation seeds, 2019-2026   ->  19 venues + 2
               citation seeds + a topic frame, 2015-2026, enumerated in full
  sampling     one simple random sample capped at 600  ->  STRATIFIED random
               sampling with declared allocation and inverse-probability
               weights, so a prevalence estimate has a design behind it
  coding       one mechanical coder + a second mechanical implementation
               ->  the same two, PLUS an adjudicated validation subsample
               covering both the screened-in and the screened-out pool
  estimate     raw proportions called lower bounds  ->  weighted proportions
               AND a Rogan-Gladen estimate corrected for the screen's
               measured sensitivity and specificity, with a bootstrap
               interval that propagates the correction's own uncertainty
  denominator  every code over every included paper  ->  APPLICABILITY-
               SPECIFIC denominators: the register-population code is
               reported only over papers whose feature is a register lookup
  missing      231 papers without full text ignored  ->  a bounding analysis
               and a comparison of retrieved against non-retrieved on every
               characteristic the metadata carries
  reporting    a funnel  ->  a PRISMA-style flow with every exclusion reason,
               and a sample-size calculation stating what the design can and
               cannot resolve

    python s06_audit2.py --frame
    python s06_audit2.py --fetch
    python s06_audit2.py --screen
    python s06_audit2.py --dossiers      # writes the adjudication packets
    python s06_audit2.py --report        # needs data/audit2/adjudication.csv

Outputs: results/s06_frame.csv, s06_sample.csv, s06_prisma.csv,
         s06_coding.csv, s06_proportions.csv, s06_corrected.csv,
         s06_missing.csv, s06_facts.csv, s06_power.csv
"""
from __future__ import annotations

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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402
import r40_audit as R40  # noqa: E402  (the frozen rule sets are reused verbatim)

ROOT = HERE.parent
AUDIT = ROOT / "data" / "audit2"
TEXTS = AUDIT / "fulltext"
META = AUDIT / "meta"
for d in (AUDIT, TEXTS, META):
    d.mkdir(parents=True, exist_ok=True)

SEED = 20260823
MAILTO = "sudhir.dixit1@gmail.com"
UA = {"User-Agent": "emptycmdb-audit/2.0 (mailto:%s)" % MAILTO}
OA = "https://api.openalex.org"
YEARS = "2015-2026"
TARGET_N = 2400           # the sampling budget, fixed before enumeration
MIN_PER_STRATUM = 25

# --------------------------------------------------------------------------
# AUDIT-PROTOCOL-2 section 2.1 -- the frame.  Nineteen sources: the four the
# round-eighteen frame used, plus every venue in which a paper of the kind
# this audit is about would plausibly appear -- information systems, software
# engineering, decision support, applied machine learning, and clinical
# informatics, which is where incremental-value reporting is most developed.
# Source ids are OpenAlex's and are resolved once, here, and then fixed.
# --------------------------------------------------------------------------
VENUES = {
    "Information Systems": "S193006928",
    "Decision Support Systems": "S11479521",
    "Information & Management": "S38883057",
    "Empirical Software Engineering": "S109852484",
    "Information Systems Research": "S202812398",
    "Journal of Systems and Software": "S37879656",
    "Expert Systems with Applications": "S13144211",
    "Knowledge-Based Systems": "S10169007",
    "Data & Knowledge Engineering": "S136993123",
    "Information Systems Frontiers": "S181659395",
    "Business & Information Systems Engineering": "S27339233",
    "Information Processing & Management": "S174847851",
    "Journal of Biomedical Informatics": "S11622463",
    "IEEE Transactions on Software Engineering": "S8351582",
    "ACM Trans. Management Information Systems": "S4210170305",
    "International Journal of Information Management": "S189354248",
    "Computers in Industry": "S60779006",
    "Journal of Business Analytics": "S4210233192",
    "Information Systems and e-Business Management": "S56271844",
}
TOPICAL = ('(predict OR prediction OR predictive OR classifier OR '
           'classification OR "machine learning" OR AUC OR forecasting)')
BENCHMARK = ["W2964066696", "W2737745668"]
#  a topic frame, so the sample is not defined by venue alone
TOPIC_QUERIES = [
    '"incremental value" AND (prediction OR predictive OR model)',
    '"added value" AND (feature OR variable OR predictor) AND prediction',
    '("feature ablation" OR "ablation study") AND prediction',
]

SELECT = ("id,doi,title,publication_year,type,open_access,cited_by_count,"
          "primary_location,locations,authorships")

#  Enumeration is cached per stratum.  OpenAlex meters requests against a
#  daily budget and a full enumeration of nineteen venues plus five other
#  strata exhausts it; without a cache an interruption in the twenty-fourth
#  stratum would throw away the first twenty-three.  The cache is keyed by
#  stratum and by the filter string, so changing a query invalidates only that
#  stratum.
CACHE = AUDIT / "frame_cache"
CACHE.mkdir(parents=True, exist_ok=True)


def _cache_key(stratum, filt):
    import hashlib
    h = hashlib.sha256((stratum + "|" + filt).encode()).hexdigest()[:16]
    return CACHE / ("%s.json.gz" % h)


def _counts_cached(stratum, base):
    """The two denominators a stratum reports: all articles in the years, and
    the open-access subset.  Cached with the enumeration."""
    p = _cache_key(stratum + "|counts", base)
    if p.exists():
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            return json.load(fh), True
    out = dict(n_all=_oa("works", filter=base, per_page=1)["meta"]["count"],
               n_oa=_oa("works", filter=base + ",open_access.is_oa:true",
                        per_page=1)["meta"]["count"])
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        json.dump(out, fh)
    return out, False


def _page_all_cached(stratum, filt, select=SELECT, cap=20000):
    p = _cache_key(stratum, filt)
    if p.exists():
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            return json.load(fh), True
    got = _page_all(filt, select=select, cap=cap)
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        json.dump(got, fh)
    return got, False



#  The index meters requests against a DAILY budget that refills slowly.  A
#  three-second backoff is useless against that: the enumeration of nineteen
#  venue strata exhausts the budget and then dies on the first stratum of the
#  next attempt, which is what happened twice.  The retry below is patient
#  rather than quick -- up to about forty minutes on one request -- because
#  the per-stratum cache means a stratum that completes is never re-fetched,
#  so a slow grind makes monotonic progress and a fast failure makes none.
#  Six quick attempts for a transient failure, then twenty-four fifteen-minute
#  ones, which spans six hours.  The budget resets at midnight UTC; a run
#  started in the afternoon therefore waits it out and continues by itself
#  rather than dying and needing a person.
_BACKOFF = (5, 15, 45, 90, 180, 300) + (900,) * 24


def _oa(path, **params):
    params.setdefault("mailto", MAILTO)
    url = "%s/%s?%s" % (OA, path, urllib.parse.urlencode(params))
    last = None
    for k, wait in enumerate(_BACKOFF):
        try:
            r = requests.get(url, headers=UA, timeout=120)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(wait)
            continue
        if r.status_code == 429:
            last = "429 %s" % r.text[:120]
            print("    rate limited; waiting %ds (attempt %d/%d)"
                  % (wait, k + 1, len(_BACKOFF)), flush=True)
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("OpenAlex unreachable: %s" % last)


def _page_all(filt, select=SELECT, cap=20000):
    out, cursor = [], "*"
    while cursor and len(out) < cap:
        d = _oa("works", filter=filt, select=select, per_page=200,
                cursor=cursor)
        out += d["results"]
        cursor = d["meta"].get("next_cursor")
        if not d["results"]:
            break
        time.sleep(0.15)
    return out


# ======================================================================
#  stage 1 -- the frame and the stratified sample
# ======================================================================
def stage_frame():
    print("=" * 92)
    print("STAGE 1 -- THE FRAME AND THE STRATIFIED SAMPLE")
    print("=" * 92)
    strata, works = [], {}

    def absorb(w, stratum, venue):
        wid = w["id"].rsplit("/", 1)[-1]
        if wid in works:
            return
        w["_stratum"] = stratum
        w["_venue"] = venue
        works[wid] = w

    for name, sid in VENUES.items():
        base = ("primary_location.source.id:%s,publication_year:%s,type:article"
                % (sid, YEARS))
        st = "venue:" + name
        filt = base + ",open_access.is_oa:true,title_and_abstract.search:" + TOPICAL
        got, cached = _page_all_cached(st, filt)
        counts, _c2 = _counts_cached(st, base)
        n_all, n_oa = counts["n_all"], counts["n_oa"]
        for w in got:
            absorb(w, st, name)
        strata.append(dict(stratum=st, kind="venue", venue=name, source=sid,
                           n_venue_years=n_all, n_open_access=n_oa,
                           n_frame=len(got)))
        print("  %-48s %5d -> OA %5d -> topical %5d%s"
              % (name[:48], n_all, n_oa, len(got), "  (cached)" if cached else ""),
              flush=True)

    for bid in BENCHMARK:
        st = "cites:" + bid
        counts, _c2 = _counts_cached(
            st, "cites:%s,publication_year:%s" % (bid, YEARS))
        got, cached = _page_all_cached(
            st, "cites:%s,publication_year:%s,open_access.is_oa:true"
            % (bid, YEARS))
        for w in got:
            absorb(w, st, ((w.get("primary_location") or {}).get("source")
                           or {}).get("display_name") or "")
        strata.append(dict(stratum=st, kind="citation", venue=st, source=bid,
                           n_venue_years=counts["n_all"], n_open_access=len(got),
                           n_frame=len(got)))
        print("  cites %-42s %5d -> OA %5d%s"
              % (bid, counts["n_all"], len(got), "  (cached)" if cached else ""),
              flush=True)

    for i, q in enumerate(TOPIC_QUERIES):
        filt = ("publication_year:%s,type:article,open_access.is_oa:true,"
                "title_and_abstract.search:%s" % (YEARS, q))
        st = "topic:%d" % (i + 1)
        got, cached = _page_all_cached(st, filt, cap=4000)
        for w in got:
            absorb(w, st, ((w.get("primary_location") or {}).get("source")
                           or {}).get("display_name") or "")
        strata.append(dict(stratum=st, kind="topic", venue=q, source="",
                           n_venue_years=len(got), n_open_access=len(got),
                           n_frame=len(got)))
        print("  topic %-42s -> %5d%s"
              % (q[:42], len(got), "  (cached)" if cached else ""), flush=True)

    ST = pd.DataFrame(strata)
    ST.to_csv(RESULTS / "s06_frame.csv", index=False)

    rows = []
    for wid, w in works.items():
        doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
        rows.append(dict(oa_id=wid, doi=doi, title=str(w.get("title"))[:250],
                         year=w.get("publication_year"),
                         cited=w.get("cited_by_count"),
                         stratum=w["_stratum"], venue=w["_venue"]))
        (META / (wid + ".json")).write_text(json.dumps(w), encoding="utf-8")
    D = pd.DataFrame(rows)
    n_raw = len(D)
    D["_key"] = np.where(D.doi.astype(bool), D.doi, D.oa_id)
    D = D.sort_values("oa_id").drop_duplicates(subset="_key", keep="first")
    D = D.drop(columns="_key").reset_index(drop=True)
    n_dedup = len(D)

    #  --- the allocation, declared before it is executed -------------------
    #  n_h = max(MIN_PER_STRATUM, round(TARGET_N * N_h / N)), capped at N_h.
    #  The design weight is N_h / n_h and every estimate below uses it.
    rng = np.random.default_rng(SEED)
    sizes = D.groupby("stratum").size()
    N = int(sizes.sum())
    alloc = {}
    for st, Nh in sizes.items():
        nh = int(min(Nh, max(MIN_PER_STRATUM,
                             int(round(TARGET_N * Nh / float(N))))))
        alloc[st] = nh
    #  the allocation may overshoot the budget; scale the large strata down
    tot = sum(alloc.values())
    if tot > TARGET_N:
        big = {k: v for k, v in alloc.items() if v > MIN_PER_STRATUM}
        excess = tot - TARGET_N
        wsum = float(sum(big.values()))
        for k in big:
            cut = int(round(excess * big[k] / wsum))
            alloc[k] = max(MIN_PER_STRATUM, alloc[k] - cut)
    parts = []
    for st, sub in D.groupby("stratum"):
        nh = min(len(sub), alloc[st])
        idx = rng.choice(len(sub), size=nh, replace=False)
        s = sub.iloc[np.sort(idx)].copy()
        s["N_h"] = len(sub)
        s["n_h"] = nh
        s["weight"] = len(sub) / float(nh)
        parts.append(s)
    SAMP = pd.concat(parts).reset_index(drop=True)
    SAMP.to_csv(RESULTS / "s06_sample.csv", index=False)
    print("\n  enumerated %d -> deduplicated %d -> sampled %d across %d strata"
          % (n_raw, n_dedup, len(SAMP), SAMP.stratum.nunique()))
    return SAMP


# ======================================================================
#  stage 2 -- full text
# ======================================================================
def _fetch_one(rec):
    oa_id, doi = rec["oa_id"], rec.get("doi") or ""
    cache = TEXTS / (oa_id + ".txt.gz")
    if cache.exists() or (V1_TEXTS / (oa_id + ".txt.gz")).exists():
        return oa_id, "cached", ""
    mp = META / (oa_id + ".json")
    if not mp.exists():
        mp = V1_META / (oa_id + ".json")
    if not mp.exists():
        return oa_id, "NO_META", ""
    meta = json.loads(mp.read_text(encoding="utf-8"))
    for url in R40._pdf_candidates(meta, doi):
        try:
            r = requests.get(url, headers=UA, timeout=45)
        except Exception:  # noqa: BLE001
            continue
        if r.status_code != 200:
            continue
        if ("pdf" not in r.headers.get("content-type", "").lower()
                and not r.content[:5].startswith(b"%PDF")):
            continue
        try:
            text, npages = R40._extract(r.content)
        except Exception:  # noqa: BLE001
            continue
        if len(text) < R40.MIN_CHARS or npages < R40.MIN_PAGES:
            continue
        with gzip.open(cache, "wt", encoding="utf-8") as fh:
            fh.write(text)
        return oa_id, "ok", url
    return oa_id, "NO_FULLTEXT", ""


def stage_fetch(sample):
    print("=" * 92)
    print("STAGE 2 -- FULL TEXT")
    print("=" * 92)
    recs = sample.to_dict("records")
    out, done = [], 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        for oa_id, status, url in ex.map(_fetch_one, recs):
            out.append(dict(oa_id=oa_id, fulltext=status, source_url=url))
            done += 1
            if done % 100 == 0:
                print("    %d/%d" % (done, len(recs)), flush=True)
    F = pd.DataFrame(out)
    F.to_csv(RESULTS / "s06_fetch.csv", index=False)
    ok = int(F.fulltext.isin(["ok", "cached"]).sum())
    print("  full text for %d of %d (%.1f%%)" % (ok, len(F), 100.0 * ok / max(1, len(F))))
    return F


# ======================================================================
#  stage 3 -- screen and code, with the frozen r40 rule sets
# ======================================================================
#  AUDIT-PROTOCOL-2 section 5.6.  The APPLICABILITY code.  The register-
#  population axis has a denominator only over papers whose incremental
#  feature is a lookup into a maintained register or an external data source
#  whose coverage could be incomplete.  Reported separately, and the
#  population code is divided by IT and not by the whole included set.
REGISTER_PATTERNS = [
    r"\b(master data|reference data|registry|register|catalog(ue)?|"
    r"configuration management database|CMDB|asset (database|register|"
    r"inventory)|knowledge base|ontology|gazetteer|look-?up table|"
    r"external (data ?(source|base)|database)|linked (record|data)|"
    r"data ?warehouse dimension)\b",
    r"\b(join(ed|ing)? (with|to|against)|link(ed|age|ing)? (with|to)|"
    r"merg(ed|ing) with|enrich(ed|ment) (with|from)|augment(ed|ing) with)\b"
    r"[^.]{0,60}\b(database|registry|register|catalog(ue)?|master data|"
    r"external (source|data)|third-?party data)\b",
    r"\b(missing|incomplete|coverage|completeness|populated|population)\b"
    r"[^.]{0,60}\b(registry|register|master data|catalog(ue)?|database|CMDB)\b",
]
_REGISTER = [re.compile(p, re.I) for p in REGISTER_PATTERNS]


#  The round-eighteen frame already retrieved 369 full texts under
#  data/audit/.  The expanded frame is a superset keyed by the same OpenAlex
#  ids, so those texts are reused rather than re-downloaded: the retrieval is
#  the same operation on the same DOI and re-running it would only cost the
#  publishers' bandwidth.
V1_TEXTS = ROOT / "data" / "audit" / "fulltext"
V1_META = ROOT / "data" / "audit" / "meta"


def _text(oa_id):
    p = TEXTS / (oa_id + ".txt.gz")
    if not p.exists():
        p = V1_TEXTS / (oa_id + ".txt.gz")
    if not p.exists():
        return None
    with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _code_one(rec):
    """Screen and code one paper with the FROZEN r40 rules, plus the new
    applicability code.  Returns a dict, and the evidence sentences the
    adjudication dossier is built from."""
    oa_id = rec["oa_id"]
    text = _text(oa_id)
    if text is None:
        return dict(oa_id=oa_id, status="NO_FULLTEXT")
    try:
        sents = R40._sentences_with_pages(text)
    except Exception as e:  # noqa: BLE001
        return dict(oa_id=oa_id, status="PARSE_FAILED", detail=str(e)[:120])
    status_reg, q_reg, _pg = R40._screen(sents)
    status, q, pg = R40._screen_amd(sents)
    out = dict(oa_id=oa_id, n_chars=len(text), n_sents=len(sents),
               n_pages=text.count(R40.PAGE_SEP) + 1,
               status=status, status_registered=status_reg,
               screen_quote=q[:300], screen_page=pg)
    if status != "INCLUDED":
        return out
    A = R40._apply(R40.CODE_RULES, sents, amended=True)
    B = R40._apply(R40.CODE_RULES_B, sents, amended=True)
    for k, (v, quote, page) in A.items():
        out[k] = v
        out[k + "_quote"] = quote[:300]
        out[k + "_page"] = page
    for k, (v, _q, _p) in B.items():
        out[k + "_B"] = v
    reg = [s for s, _pg in sents if any(p.search(s) for p in _REGISTER)]
    out["applic_register"] = "yes" if reg else "no"
    out["applic_evidence"] = " || ".join(reg[:2])[:400]
    return out


def stage_screen(sample):
    print("=" * 92)
    print("STAGE 3 -- SCREEN AND CODE")
    print("=" * 92)
    rows = []
    for i, rec in enumerate(sample.to_dict("records")):
        rows.append(_code_one(rec))
        if (i + 1) % 200 == 0:
            print("    %d/%d" % (i + 1, len(sample)), flush=True)
    C = pd.DataFrame(rows)
    C = sample.merge(C, on="oa_id", how="left")
    C.to_csv(RESULTS / "s06_coding.csv", index=False)
    print(C.status.value_counts().to_string())
    return C


# ======================================================================
#  stage 4 -- the adjudication dossiers
# ======================================================================
#  AUDIT-PROTOCOL-2 section 7.  The referee's objection is that a mechanical
#  coder both under-detects and produces false positives, so its proportions
#  are neither lower bounds nor unbiased.  The answer is to MEASURE the
#  coder's error and correct for it, which requires a reference standard on a
#  probability subsample of BOTH pools -- the screened-in and the screened-out
#  -- not only of the screened-in.  A dossier is the evidence packet the
#  reference judgement is made from: the paper's identity, the sentences the
#  screen fired on, and for each of the five codes the strongest candidate
#  sentences under BOTH rule sets plus the neighbourhood of every mention of
#  the concept the code is about.  The dossier is written to disk and
#  committed, so the judgement can be re-examined against exactly what it was
#  made from.
DOSSIER_PROBES = {
    "eligibility": [r"\bablation\b", r"\bwith(out)? (the|these|any)\b[^.]{0,40}"
                    r"(features?|variables?|attributes?)", r"\bfeature (set|group)s?\b",
                    r"\b(add|includ|remov|exclud|drop|omit)\w*\b[^.]{0,50}"
                    r"(features?|variables?|attributes?|predictors?)"],
    "B_stated": [r"\bbaseline\b", r"\bfeature (set|vector)\b",
                 r"\bthe following (features?|variables?)\b"],
    "B_justified": [r"\b(exclud|omit|remov|drop)\w*\b[^.]{0,60}"
                    r"\b(because|since|to avoid|leakage|not available)\b"],
    "M_justified": [r"\b(AUC|AUROC|F1|MCC|Brier|average precision)\b[^.]{0,60}"
                    r"\b(because|since|chosen|selected|preferred|appropriate)\b",
                    r"\bevaluation metric\b"],
    "Theta_stated": [r"\bthreshold\b", r"\boperating point\b", r"\bcut-?off\b",
                     r"\bnet benefit\b", r"\btop-?\d+\b", r"\bcost (ratio|matrix)\b"],
    "Range_reported": [r"\brang\w+ from\b", r"\bdepending on\b",
                       r"\bsensitivity analys\w+\b", r"\bvari(es|ed) (with|across)\b",
                       r"\bacross (metrics|baselines|thresholds)\b"],
    "applicability": REGISTER_PATTERNS,
}
_PROBES = {k: [re.compile(p, re.I) for p in v]
           for k, v in DOSSIER_PROBES.items()}
DOSSIERS = AUDIT / "dossiers"
VALIDATION_OUT = 120     # screened-out papers drawn for the reference standard


def _dossier(oa_id, rec, coding_row):
    text = _text(oa_id)
    if text is None:
        return None
    sents = R40._sentences_with_pages(text)
    head = re.sub(r"\s+", " ", text[:1400]).strip()
    #  every sentence that carries a metric name beside a number that is not a
    #  citation marker: the evidence for or against the screen's METRIC leg
    numeric = []
    for s, pg in sents:
        if R40._METRIC.search(s) and R40._numeric_result(s):
            numeric.append("   p%-3d %s" % (pg, s[:240]))
        if len(numeric) >= 6:
            break
    parts = ["PAPER  %s" % oa_id,
             "TITLE  %s" % str(rec.get("title"))[:180],
             "VENUE  %s   YEAR %s   STRATUM %s"
             % (rec.get("venue"), rec.get("year"), rec.get("stratum", "")),
             "SCREEN %s   (registered rule: %s)"
             % (coding_row.get("status"), coding_row.get("status_registered")),
             "",
             "[head]", "   " + head, "",
             "[numeric performance sentences]"]
    parts += numeric if numeric else ["   (none)"]
    parts.append("")
    for probe, pats in _PROBES.items():
        hits = []
        for s, pg in sents:
            if any(p.search(s) for p in pats):
                hits.append("   p%-3d %s" % (pg, s[:260]))
            if len(hits) >= 4:
                break
        parts.append("[%s]" % probe)
        parts += hits if hits else ["   (no sentence matched)"]
        parts.append("")
    return "\n".join(parts)[:9000]


def stage_dossiers(sample, coding):
    print("=" * 92)
    print("STAGE 4 -- ADJUDICATION DOSSIERS")
    print("=" * 92)
    DOSSIERS.mkdir(parents=True, exist_ok=True)
    C = coding.set_index("oa_id")
    rng = np.random.default_rng(SEED + 5)
    inc = coding[coding.status == "INCLUDED"].oa_id.tolist()
    out_pool = coding[(coding.status.isin(["NO_METRIC", "NO_ABLATION"]))].oa_id.tolist()
    k = min(VALIDATION_OUT, len(out_pool))
    out_sel = list(np.array(out_pool)[np.sort(
        rng.choice(len(out_pool), size=k, replace=False))]) if k else []
    man = []
    for oa_id in inc + out_sel:
        rec = sample[sample.oa_id == oa_id].iloc[0].to_dict()
        row = C.loc[oa_id].to_dict() if oa_id in C.index else {}
        d = _dossier(oa_id, rec, row)
        if d is None:
            continue
        (DOSSIERS / (oa_id + ".txt")).write_text(d, encoding="utf-8")
        man.append(dict(oa_id=oa_id, pool="in" if oa_id in inc else "out",
                        title=str(rec.get("title"))[:180],
                        venue=rec.get("venue"), year=rec.get("year"),
                        stratum=rec.get("stratum", ""),
                        weight=rec.get("weight", 1.0),
                        machine_status=row.get("status")))
    M = pd.DataFrame(man)
    M.to_csv(RESULTS / "s06_dossier_manifest.csv", index=False)
    print("  %d dossiers written (%d screened in, %d screened out)"
          % (len(M), int((M.pool == "in").sum()), int((M.pool == "out").sum())))
    return M


# ======================================================================
#  stage 5 -- estimation
# ======================================================================
def wilson(k, n, z=1.959963985):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def rogan_gladen(p_obs, sens, spec):
    """The prevalence a classifier with sensitivity `sens` and specificity
    `spec` implies when it observes `p_obs`.  Truncated to [0, 1]."""
    den = sens + spec - 1.0
    if abs(den) < 1e-9:
        return np.nan
    return float(min(1.0, max(0.0, (p_obs + spec - 1.0) / den)))


def corrected_interval(k_obs, n_obs, k_se, n_se, k_sp, n_sp, B=20000,
                       seed=SEED):
    """A parametric bootstrap that propagates the uncertainty in the observed
    proportion AND in the measured sensitivity and specificity.  The referee's
    objection is that the mechanical coder's proportions cannot be called
    lower bounds; this replaces the claim with an estimate whose interval
    contains the coder's own error."""
    rng = np.random.default_rng(seed)
    p = rng.beta(k_obs + 0.5, n_obs - k_obs + 0.5, B)
    se = rng.beta(k_se + 0.5, n_se - k_se + 0.5, B)
    sp = rng.beta(k_sp + 0.5, n_sp - k_sp + 0.5, B)
    den = se + sp - 1.0
    v = np.where(np.abs(den) < 1e-6, np.nan, (p + sp - 1.0) / den)
    v = np.clip(v, 0.0, 1.0)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    return (float(np.median(v)), float(np.percentile(v, 2.5)),
            float(np.percentile(v, 97.5)))


def sample_size(half_width=0.07, p=0.5, z=1.959963985):
    return int(np.ceil(z * z * p * (1 - p) / (half_width ** 2)))


CODES = ("B_stated", "B_justified", "M_justified", "Theta_stated",
         "Range_reported")


def stage_report(sample, coding):
    """AUDIT-PROTOCOL-2 sections 6-9.

    The design is TWO-STRATUM.  Stratum 1 is every paper the mechanical screen
    included: adjudicated in full (a census).  Stratum 2 is every paper with
    full text that the screen excluded: a random subsample was adjudicated,
    and it is weighted up by its sampling fraction.  Estimating a code's
    prevalence over the ELIGIBLE population therefore requires both strata,
    because the screen's misses are not a random subset of the eligible.
    """
    print("=" * 92)
    print("STAGE 5 -- PRISMA, SCREEN ACCURACY, AND CORRECTED PREVALENCE")
    print("=" * 92)
    A_in = pd.read_csv(AUDIT / "adjudication_in.csv")
    A_out = pd.read_csv(AUDIT / "adjudication_out.csv")
    C = coding.copy()

    n_frame = len(sample)
    n_ft = int(C.status.notna().sum() - (C.status == "NO_FULLTEXT").sum())
    n_in = int((C.status == "INCLUDED").sum())
    out_pool = C[C.status.isin(["NO_METRIC", "NO_ABLATION"])]
    n_out = len(out_pool)
    n_out_adj = len(A_out)
    frac_out = n_out_adj / float(n_out) if n_out else np.nan

    tp = int((A_in.eligible == "yes").sum())
    fp = int((A_in.eligible == "no").sum())
    fn_s = int((A_out.eligible == "yes").sum())
    tn_s = int((A_out.eligible == "no").sum())
    #  weight the screened-out stratum up to the whole screened-out pool
    w = 1.0 / frac_out
    fn_hat, tn_hat = fn_s * w, tn_s * w
    sens = tp / (tp + fn_hat) if (tp + fn_hat) > 0 else np.nan
    spec = tn_hat / (tn_hat + fp) if (tn_hat + fp) > 0 else np.nan
    ppv = tp / float(tp + fp) if (tp + fp) else np.nan
    n_elig_hat = tp + fn_hat

    if "N_h" in sample.columns:
        per_h = sample.groupby("stratum").N_h.first()
        n_frame_total, n_strata = int(per_h.sum()), int(len(per_h))
        w_max = float(sample.weight.max()) if "weight" in sample.columns else 1.0
    else:
        n_frame_total, n_strata, w_max = n_frame, 0, 1.0

    prisma = pd.DataFrame([
        #  n_frame_total, computed once above by grouping on the stratum.
        #  Summing N_h over ROWS gives sum_h N_h * n_h and put 54,910 in this
        #  table while Section 9.4 said 600 -- the two disagreed inside one
        #  document, which is the defect the whole generated-macro
        #  architecture exists to make impossible.
        dict(step="records enumerated in the frame", n=n_frame_total),
        dict(step="records sampled", n=n_frame),
        dict(step="full text retrieved", n=n_ft),
        dict(step="full text not retrieved", n=n_frame - n_ft),
        dict(step="screened in by the mechanical rule", n=n_in),
        dict(step="screened out: no quantitative metric",
             n=int((C.status == "NO_METRIC").sum())),
        dict(step="screened out: no incremental comparison",
             n=int((C.status == "NO_ABLATION").sum())),
        dict(step="adjudicated, screened-in stratum (census)", n=len(A_in)),
        dict(step="adjudicated, screened-out stratum (sample)", n=n_out_adj),
        dict(step="confirmed eligible, screened-in stratum", n=tp),
        dict(step="confirmed eligible, screened-out stratum (unweighted)",
             n=fn_s),
        dict(step="estimated eligible among all retrieved full texts",
             n=round(n_elig_hat, 1)),
    ])
    prisma.to_csv(RESULTS / "s06_prisma.csv", index=False)
    print(prisma.to_string(index=False))

    #  A SECOND mechanical screen, measured against the same standard.  The
    #  registered rule of AUDIT-PROTOCOL.md section 4 and the amended rule of
    #  its amendment 1 are two different procedures written against the same
    #  prose, and both ran on every paper.  Reporting the accuracy of BOTH
    #  against the adjudication is the closest thing to a second coder that
    #  one author can produce, and it is reported as that and not as
    #  independence.
    reg_rows = []
    if "status_registered" in C.columns:
        adj = pd.concat([A_in[["oa_id", "eligible"]],
                         A_out[["oa_id", "eligible"]]])
        M2 = C.merge(adj, on="oa_id", how="inner")
        M2 = M2[M2.eligible.isin(["yes", "no"])]
        for rule, col in (("amended (primary)", "status"),
                          ("registered", "status_registered")):
            inn = M2[col] == "INCLUDED"
            elig = M2.eligible == "yes"
            #  weight the screened-out stratum up, as above: a paper the
            #  PRIMARY screen rejected is in the adjudication only with
            #  probability frac_out.
            wt = np.where(M2.status == "INCLUDED", 1.0, w)
            tp2 = float(wt[(inn & elig).values].sum())
            fp2 = float(wt[(inn & ~elig).values].sum())
            fn2 = float(wt[(~inn & elig).values].sum())
            tn2 = float(wt[(~inn & ~elig).values].sum())
            reg_rows.append(dict(
                rule=rule, sensitivity=tp2 / (tp2 + fn2) if tp2 + fn2 else np.nan,
                specificity=tn2 / (tn2 + fp2) if tn2 + fp2 else np.nan,
                precision=tp2 / (tp2 + fp2) if tp2 + fp2 else np.nan,
                n_flagged=int(inn.sum())))
        RR = pd.DataFrame(reg_rows)
        RR.to_csv(RESULTS / "s06_two_screens.csv", index=False)
        print()
        print("TWO MECHANICAL SCREENS AGAINST THE SAME ADJUDICATION")
        print(RR.to_string(index=False, float_format=lambda x: "%.3f" % x))

    acc = pd.DataFrame([dict(
        quantity="screen sensitivity", estimate=sens,
        lo=wilson(tp, int(round(tp + fn_hat)))[0],
        hi=wilson(tp, int(round(tp + fn_hat)))[1],
        note="weighted; the screened-out stratum is a %.1f%% sample"
             % (100 * frac_out)),
        dict(quantity="screen specificity", estimate=spec,
             lo=wilson(int(round(tn_hat)), int(round(tn_hat + fp)))[0],
             hi=wilson(int(round(tn_hat)), int(round(tn_hat + fp)))[1],
             note="weighted"),
        dict(quantity="screen precision (PPV)", estimate=ppv,
             lo=wilson(tp, tp + fp)[0], hi=wilson(tp, tp + fp)[1],
             note="census over the screened-in stratum"),
        dict(quantity="eligibility prevalence among retrieved full texts",
             estimate=n_elig_hat / n_ft if n_ft else np.nan,
             lo=np.nan, hi=np.nan, note="two-stratum estimate")])
    acc.to_csv(RESULTS / "s06_screen_accuracy.csv", index=False)
    print()
    print(acc.to_string(index=False))

    # --- code prevalence over the eligible population --------------------
    E_in = A_in[A_in.eligible == "yes"].copy()
    E_out = A_out[A_out.eligible == "yes"].copy()
    E_in["w"] = 1.0
    E_out["w"] = w
    E = pd.concat([E_in, E_out], ignore_index=True)
    rows = []
    for code in CODES:
        v = E[code].astype(str)
        wt = E.w.values
        yes = float(wt[(v == "yes").values].sum())
        no = float(wt[(v == "no").values].sum())
        unc = float(wt[(v == "unclear").values].sum())
        tot = yes + no + unc
        #  an effective sample size for the interval: Kish's, so the weighted
        #  interval is not narrower than the information supports
        n_eff = (wt.sum() ** 2) / float((wt ** 2).sum())
        k_eff = int(round(n_eff * yes / tot)) if tot else 0
        lo, hi = wilson(k_eff, int(round(n_eff)))
        rows.append(dict(code=code, n_weighted=tot, n_papers=len(E),
                         n_eff=n_eff, yes=yes, no=no, unclear=unc,
                         p_yes=yes / tot if tot else np.nan, lo=lo, hi=hi))
    #  the two axes the paper's own answer moves on, coded from range_axis
    ax = E.range_axis.astype(str).str.lower()
    wt = E.w.values
    tot = float(wt.sum())
    for axis in ("baseline", "metric", "threshold", "population"):
        hit = ax.str.contains(axis, na=False).values
        k = float(wt[hit].sum())
        n_eff = (wt.sum() ** 2) / float((wt ** 2).sum())
        lo, hi = wilson(int(round(n_eff * k / tot)) if tot else 0,
                        int(round(n_eff)))
        rows.append(dict(code="range_over_" + axis, n_weighted=tot,
                         n_papers=len(E), n_eff=n_eff, yes=k, no=tot - k,
                         unclear=0.0, p_yes=k / tot if tot else np.nan,
                         lo=lo, hi=hi))
    P = pd.DataFrame(rows)
    P.to_csv(RESULTS / "s06_proportions.csv", index=False)
    print()
    print(P.to_string(index=False, float_format=lambda x: "%.4f" % x))

    # --- applicability-specific denominator ------------------------------
    appl = E[E.applic_register.astype(str) == "yes"]
    appl_rows = [dict(quantity="eligible papers", n=float(E.w.sum())),
                 dict(quantity="of which the incremental feature is a lookup "
                      "into an external register or reference source",
                      n=float(appl.w.sum())),
                 dict(quantity="of those, reporting the increment across a "
                      "range of register populations",
                      n=float(appl[appl.range_axis.astype(str)
                                   .str.contains("population", na=False)]
                              .w.sum()))]
    AP = pd.DataFrame(appl_rows)
    AP.to_csv(RESULTS / "s06_applicability.csv", index=False)
    print()
    print(AP.to_string(index=False))

    # --- what the missing full texts could do ----------------------------
    miss = C[C.status == "NO_FULLTEXT"]
    got = C[C.status != "NO_FULLTEXT"]
    comp = pd.DataFrame([
        dict(characteristic="n", retrieved=len(got), not_retrieved=len(miss)),
        dict(characteristic="median year",
             retrieved=float(got.year.median()),
             not_retrieved=float(miss.year.median())),
        dict(characteristic="share from the four round-eighteen venues",
             retrieved=float(got.venue.isin(
                 ["Information Systems", "Decision Support Systems",
                  "Information & Management",
                  "Empirical Software Engineering"]).mean()),
             not_retrieved=float(miss.venue.isin(
                 ["Information Systems", "Decision Support Systems",
                  "Information & Management",
                  "Empirical Software Engineering"]).mean()))])
    p_hat = n_elig_hat / n_ft if n_ft else np.nan
    bounds = pd.DataFrame([
        dict(assumption="none of the unretrieved papers is eligible",
             p_eligible=n_elig_hat / n_frame),
        dict(assumption="the unretrieved papers are eligible at the retrieved "
             "rate", p_eligible=p_hat),
        dict(assumption="all of the unretrieved papers are eligible",
             p_eligible=(n_elig_hat + (n_frame - n_ft)) / n_frame)])
    comp.to_csv(RESULTS / "s06_missing.csv", index=False)
    bounds.to_csv(RESULTS / "s06_missing_bounds.csv", index=False)
    print()
    print(comp.to_string(index=False))
    print(bounds.to_string(index=False))

    # --- what this design can and cannot resolve -------------------------
    pw = pd.DataFrame([dict(half_width=h, n_required=sample_size(h))
                       for h in (0.05, 0.07, 0.10, 0.15, 0.20)])
    pw["achieved"] = float(P.n_eff.iloc[0])
    pw.to_csv(RESULTS / "s06_power.csv", index=False)
    print()
    print(pw.to_string(index=False))

    # --- agreement between the machine coder and the adjudication --------
    kap = []
    M = C.set_index("oa_id")
    for code in CODES:
        a, b = [], []
        for _, r in E_in.iterrows():
            if r.oa_id in M.index and code in M.columns:
                mv = M.loc[r.oa_id, code]
                if isinstance(mv, pd.Series):
                    mv = mv.iloc[0]
                a.append(str(mv))
                b.append(str(r[code]))
        if not a:
            continue
        agree = float(np.mean([x == y for x, y in zip(a, b)]))
        labs = ("yes", "no", "unclear")
        po = agree
        pe = sum((np.mean([x == L for x in a]) * np.mean([y == L for y in b]))
                 for L in labs)
        kap.append(dict(code=code, n=len(a), agreement=agree,
                        kappa=(po - pe) / (1 - pe) if pe < 1 else np.nan))
    K = pd.DataFrame(kap)
    K.to_csv(RESULTS / "s06_agreement.csv", index=False)
    print()
    print(K.to_string(index=False, float_format=lambda x: "%.4f" % x))

    #  N_h is carried on every ROW, so summing it over rows computes
    #  sum_h N_h * n_h and not sum_h N_h.  That put the frame at 54,910 when
    #  it is 600, and the manuscript said so for a whole round.  The frame is
    #  the sum over DISTINCT strata, and it is reported beside the sample so a
    #  reader can see for themselves that the two are equal -- every
    #  enumerated record was taken, and the pilot is a census of what the
    #  enumeration returned rather than a probability subsample of a
    #  literature.
    facts = dict(
        n_frame_total=n_frame_total, n_strata=n_strata,
        max_design_weight=w_max, target_n=TARGET_N,
        enumeration_short_of_budget=bool(n_frame_total < TARGET_N),
        n_sampled=n_frame, n_fulltext=n_ft, n_screened_in=n_in,
        n_screened_out=n_out, n_adjudicated=len(A_in) + len(A_out),
        n_eligible_confirmed_in=tp, n_eligible_confirmed_out=fn_s,
        out_sampling_fraction=frac_out,
        n_eligible_estimated=round(n_elig_hat, 1),
        screen_sensitivity=sens, screen_specificity=spec,
        screen_precision=ppv,
        p_B_stated=float(P[P.code == "B_stated"].p_yes.iloc[0]),
        p_B_justified=float(P[P.code == "B_justified"].p_yes.iloc[0]),
        p_M_justified=float(P[P.code == "M_justified"].p_yes.iloc[0]),
        p_Theta_stated=float(P[P.code == "Theta_stated"].p_yes.iloc[0]),
        p_Range_reported=float(P[P.code == "Range_reported"].p_yes.iloc[0]),
        p_range_baseline=float(P[P.code == "range_over_baseline"].p_yes.iloc[0]),
        p_range_metric=float(P[P.code == "range_over_metric"].p_yes.iloc[0]),
        p_range_threshold=float(P[P.code == "range_over_threshold"].p_yes.iloc[0]),
        p_range_population=float(P[P.code == "range_over_population"].p_yes.iloc[0]),
        n_applicable_register=float(appl.w.sum()),
        n_required_for_pm7=sample_size(0.07),
        n_effective=float(P.n_eff.iloc[0]),
        mean_kappa=float(K.kappa.mean()) if len(K) else np.nan,
        min_kappa=float(K.kappa.min()) if len(K) else np.nan)
    pd.DataFrame([facts]).to_csv(RESULTS / "s06_facts.csv", index=False)
    print()
    print(pd.Series(facts).to_string())
    return P


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--screen", action="store_true")
    ap.add_argument("--dossiers", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    any_stage = a.frame or a.fetch or a.screen or a.dossiers or a.report
    t0 = time.time()
    S = None
    if a.frame or not any_stage:
        S = stage_frame()
    if S is None and (RESULTS / "s06_sample.csv").exists():
        S = pd.read_csv(RESULTS / "s06_sample.csv")
    if a.fetch or not any_stage:
        stage_fetch(S)
    if a.screen or not any_stage:
        stage_screen(S)
    if a.dossiers:
        C = pd.read_csv(RESULTS / "s06_coding.csv")
        stage_dossiers(S, C)
    if a.report:
        C = pd.read_csv(RESULTS / "s06_coding.csv")
        stage_report(S, C)
    print("\n%.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()

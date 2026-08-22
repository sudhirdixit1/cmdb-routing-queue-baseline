"""r42 -- FETCH THE HELD-OUT LOGS, AND ENUMERATE WHAT THIS ROUND DOES NOT BURN.

Same discipline as fetch_corpus.py: resolve by DOI through the 4TU API,
download the named file, record a SHA-256 in data/corpus/CHECKSUMS.txt.

TWO THINGS THIS FILE DELIBERATELY DOES NOT DO.

  * It does not parse.  Downloading a gzip is not opening a log; the parse
    happens in r43_holdout_test.py, after PREDICTION.md is committed, and
    PREDICTION.md was committed before this file existed.
  * It does not open the datasets published on 4TU after 2026-08-21.  It
    records their identifiers, titles and publication dates in
    results/r42_new_since.csv so that a LATER round has a held-out set this
    round did not burn.  A held-out set is spent the moment it is looked at,
    and this round has already spent the two logs it needs.

Usage:
    python r42_holdout_fetch.py            # both held-out logs + the census
    python r42_holdout_fetch.py --census   # the 4TU census only, no download
"""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "corpus"
DEST.mkdir(parents=True, exist_ok=True)
CHECKSUMS = DEST / "CHECKSUMS.txt"
RESULTS = ROOT / "results"
API = "https://data.4tu.nl/v2"

#  PREDICTION.md section 1.  Article ids are what the DOI resolves to today;
#  the DOI is the citable identifier and the id is recorded so the fetch is
#  reproducible without a second redirect hop.
HOLDOUT = {
    "BPIC11": ("healthcare",
               "10.4121/uuid:d9769f3d-0ab0-4fb8-803b-0d1120ffcf54",
               12716513, "Hospital_log.xes.gz", 2384410),
    "BPIC18": ("agriculture",
               "10.4121/uuid:3301445f-95e8-4ff0-98a4-901f1f204972",
               12688355, "BPI Challenge 2018.xes.gz", 158270992),
}

#  PREDICTION.md section 1.  Anything published on or after this date is
#  enumerated and NOT opened.
CUTOFF = "2026-08-21"


def _get(url, tries=4, timeout=180):
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.read()
        except Exception as e:                             # noqa: BLE001
            last = e
            time.sleep(2 * (k + 1))
    raise last


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_checksums():
    if not CHECKSUMS.exists():
        return {}
    out = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, key = line.split(None, 1)
        out[key.strip()] = digest
    return out


def save_checksums(d):
    lines = ["# SHA-256 of the corpus, recorded on first download from each DOI.",
             "# Verified on every later run; see REPRODUCE.md.", ""]
    lines += [f"{v}  {k}" for k, v in sorted(d.items())]
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve(article_id, filename):
    d = json.loads(_get(f"{API}/articles/{article_id}").decode())
    for f in d.get("files", []):
        if f["name"] == filename:
            return f["download_url"], f["size"]
    raise FileNotFoundError(f"{filename!r} not in article {article_id} "
                            f"({[f['name'] for f in d.get('files', [])]})")


def fetch(key, sums):
    domain, doi, aid, name, size = HOLDOUT[key]
    p = DEST / name
    if p.exists() and p.stat().st_size == size:
        if key in sums:
            ok = sha256(p) == sums[key]
            print(f"  {key:8s} present, checksum {'OK' if ok else 'MISMATCH'}")
            if not ok:
                raise SystemExit(f"{p} does not match the recorded SHA-256")
        else:
            sums[key] = sha256(p)
            print(f"  {key:8s} present, checksum recorded")
        return
    url, rsize = resolve(aid, name)
    print(f"  {key:8s} downloading {rsize:,} bytes from {doi} ...", flush=True)
    t = time.time()
    tmp = p.with_suffix(p.suffix + ".part")
    with urllib.request.urlopen(url, timeout=3600) as r, open(tmp, "wb") as fh:
        got = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            fh.write(b)
            got += len(b)
            if got % (32 << 20) < (1 << 20):
                print(f"           {got / 1e6:8.0f} MB "
                      f"({time.time() - t:.0f}s)", flush=True)
    got = tmp.stat().st_size
    if size and got != size:
        print(f"  {key:8s} WARNING size {got:,} != manifest {size:,}")
    tmp.replace(p)
    sums[key] = sha256(p)
    print(f"  {key:8s} done, {got:,} bytes in {time.time() - t:.0f}s")


def census():
    """Datasets published on 4TU on or after CUTOFF.  Identifiers only.

    This is the part of the held-out set this round does NOT spend.  Nothing
    below downloads or parses anything: it records what exists, so a later
    round can register a prediction against data that was already public and
    already untouched when this round ended.
    """
    rows, page = [], 1
    while page <= 40:
        try:
            batch = json.loads(_get(
                f"{API}/articles?page={page}&page_size=100"
                f"&published_since={CUTOFF}", tries=3, timeout=120).decode())
        except Exception as e:                             # noqa: BLE001
            print(f"  census: page {page} failed ({type(e).__name__}); "
                  f"recording what was enumerated")
            break
        if not batch:
            break
        for a in batch:
            rows.append(dict(uuid=a.get("uuid"), doi=a.get("doi"),
                             title=str(a.get("title"))[:120],
                             published_date=a.get("published_date"),
                             url=a.get("url_public_html")))
        page += 1
    D = pd.DataFrame(rows)
    if len(D):
        D = D.drop_duplicates(subset=["uuid"])
        #  A crude but declared filter, so a later round knows which rows are
        #  worth looking at.  It reads TITLES from a catalogue, not data.
        kw = ("event log", "process mining", "bpi challenge", "xes")
        D["looks_like_event_log"] = D.title.str.lower().apply(
            lambda s: any(k in s for k in kw))
    D.to_csv(RESULTS / "r42_new_since.csv", index=False)
    print(f"\n  4TU census since {CUTOFF}: {len(D)} datasets enumerated, "
          f"{int(D.looks_like_event_log.sum()) if len(D) else 0} whose title "
          f"looks like an event log.")
    print(f"  Written to results/r42_new_since.csv.  NONE was opened.")


def main(argv):
    if "--census" not in argv:
        sums = load_checksums()
        print(f"Fetching the held-out logs into {DEST}")
        for k in HOLDOUT:
            try:
                fetch(k, sums)
            except Exception as e:                         # noqa: BLE001
                print(f"  {k:8s} FAILED: {type(e).__name__}: {e}")
            save_checksums(sums)
    census()


if __name__ == "__main__":
    main(sys.argv[1:])

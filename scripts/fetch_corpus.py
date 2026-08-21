"""Fetch the public event-log corpus, by DOI, with checksums.

Nothing in this repository redistributes anybody's data.  This script resolves
each dataset's DOI through the 4TU.ResearchData API, downloads the named file,
and records its SHA-256 in `data/corpus/CHECKSUMS.txt`.  On every later run the
checksum is verified and an unchanged file is skipped, so `reproduce_all.py`
can assert that the corpus a reader has is the corpus the paper was written
against.

The checksums cannot be pinned in advance -- they are recorded on first
download from the DOI and verified from then on.  REPRODUCE.md says so
explicitly; a checksum a reader cannot independently obtain is a checksum that
proves nothing, and the DOI is the thing that is citable.

Usage:
    python fetch_corpus.py             # everything not already present
    python fetch_corpus.py --list      # manifest only, no network
    python fetch_corpus.py BPIC15_1 Sepsis
"""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "corpus"
DEST.mkdir(parents=True, exist_ok=True)
CHECKSUMS = DEST / "CHECKSUMS.txt"
API = "https://data.4tu.nl/v2"

# key -> (domain, DOI, article id, filename, expected size in bytes)
# Article ids are what the DOI resolves to today; the DOI is the citable
# identifier and the id is recorded so the fetch is reproducible without a
# second redirect hop.
CORPUS = {
    # --- ITSM -------------------------------------------------------------
    "BPIC14_incident":  ("itsm", "10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35",
                         12692378, "Detail_Incident.csv", 14306331),
    "BPIC14_activity":  ("itsm", "10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35",
                         12706424, "Detail_Incident_Activity.csv", 39172687),
    "BPIC14_interaction": ("itsm", "10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35",
                           12692411, "Detail_Interaction.csv", 21873186),
    "BPIC13_incidents": ("itsm", "10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee",
                         12693914, "BPI_Challenge_2013_incidents.xes.gz", 1322247),
    "BPIC13_open":      ("itsm", "10.4121/uuid:3537c19d-6c64-4b1d-815d-915ab0e479da",
                         12688556, "BPI_Challenge_2013_open_problems.xes.gz", 68697),
    "BPIC13_closed":    ("itsm", "10.4121/uuid:c2c3b154-ab26-4b31-a0e8-8f2350ddac11",
                         12714476, "BPI_Challenge_2013_closed_problems.xes.gz", 186515),
    "Helpdesk":         ("itsm", "10.4121/uuid:0c60edf1-6f83-4e75-9367-4c63b3e9d5bb",
                         12675977, "finale.csv", 3271588),
    # --- lending ----------------------------------------------------------
    "BPIC12":           ("lending", "10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f",
                         12689204, "BPI_Challenge_2012.xes.gz", 3342406),
    "BPIC17":           ("lending", "10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b",
                         12696884, "BPI Challenge 2017.xes.gz", 29658747),
    # --- procurement ------------------------------------------------------
    "BPIC19":           ("procurement", "10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1",
                         12715853, "BPI_Challenge_2019.xes", 728558522),
    # --- permitting (five municipalities) ---------------------------------
    "BPIC15_1":         ("permitting", "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",
                         12709154, "BPIC15_1.xes", 41227060),
    "BPIC15_2":         ("permitting", "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",
                         12697349, "BPIC15_2.xes", 34423078),
    "BPIC15_3":         ("permitting", "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",
                         12718370, "BPIC15_3.xes", 46768886),
    "BPIC15_4":         ("permitting", "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",
                         12697898, "BPIC15_4.xes", 36998010),
    "BPIC15_5":         ("permitting", "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",
                         12713285, "BPIC15_5.xes", 46039768),
    # --- expenses (five sub-logs) -----------------------------------------
    "BPIC20_domestic":  ("expenses", "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",
                         12692543, "DomesticDeclarations.xes.gz", 933930),
    "BPIC20_intl":      ("expenses", "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",
                         12687374, "InternationalDeclarations.xes.gz", 1581144),
    "BPIC20_prepaid":   ("expenses", "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",
                         12696722, "PrepaidTravelCost.xes.gz", 370047),
    "BPIC20_permit":    ("expenses", "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",
                         12718178, "PermitLog.xes.gz", 1938192),
    "BPIC20_rfp":       ("expenses", "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",
                         12706886, "RequestForPayment.xes.gz", 696896),
    # --- healthcare -------------------------------------------------------
    "Sepsis":           ("healthcare", "10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460",
                         12707639, "Sepsis Cases - Event Log.xes.gz", 202508),
    "HospitalBilling":  ("healthcare", "10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741",
                         12705113, "Hospital Billing - Event Log.xes.gz", 6615825),
    # --- enforcement ------------------------------------------------------
    "RoadFines":        ("enforcement", "10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5",
                         12683249, "Road_Traffic_Fine_Management_Process.xes.gz", 3454978),
}

# The three already-loaded BPIC 2014 files live in data/raw and are not
# re-downloaded; the corpus loader looks in both places.
IN_RAW = {"BPIC14_incident", "BPIC14_activity", "BPIC14_interaction",
          "BPIC13_incidents"}

COLLECTIONS = {"BPIC15": 5065424, "BPIC20": 5065541,
               "BPIC14": 5065469}


def _get(url, tries=4):
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return r.read()
        except Exception as e:                             # noqa: BLE001
            last = e
            time.sleep(2 * (k + 1))
    raise last


def resolve(article_id, filename):
    """The download URL for one named file inside one 4TU article."""
    d = json.loads(_get(f"{API}/articles/{article_id}").decode())
    for f in d.get("files", []):
        if f["name"] == filename:
            return f["download_url"], f["size"]
    raise FileNotFoundError(f"{filename!r} not in article {article_id} "
                            f"({[f['name'] for f in d.get('files', [])]})")


def resolve_by_search(filename):
    """Fallback: find `filename` anywhere in the three known collections."""
    for cid in COLLECTIONS.values():
        arts = json.loads(_get(f"{API}/collections/{cid}/articles?page_size=50").decode())
        for a in arts:
            d = json.loads(_get(a["url_public_api"]).decode())
            for f in d.get("files", []):
                if f["name"] == filename:
                    return f["download_url"], f["size"]
    raise FileNotFoundError(filename)


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


def local_path(key):
    domain, doi, aid, name, size = CORPUS[key]
    if key in IN_RAW:
        p = ROOT / "data" / "raw" / name
        if p.exists():
            return p
    return DEST / name


def fetch(key, sums):
    domain, doi, aid, name, size = CORPUS[key]
    p = local_path(key)
    if p.exists() and p.stat().st_size == size:
        if key in sums:
            got = sha256(p)
            ok = got == sums[key]
            print(f"  {key:20s} present, checksum {'OK' if ok else 'MISMATCH'}")
            if not ok:
                raise SystemExit(f"{p} does not match the recorded SHA-256")
        else:
            sums[key] = sha256(p)
            print(f"  {key:20s} present, checksum recorded")
        return
    try:
        url, rsize = resolve(aid, name)
    except FileNotFoundError:
        url, rsize = resolve_by_search(name)
    print(f"  {key:20s} downloading {rsize:,} bytes ...", flush=True)
    t = time.time()
    tmp = p.with_suffix(p.suffix + ".part")
    with urllib.request.urlopen(url, timeout=1800) as r, open(tmp, "wb") as fh:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            fh.write(b)
    got = tmp.stat().st_size
    if size and got != size:
        print(f"  {key:20s} WARNING size {got:,} != manifest {size:,}")
    tmp.replace(p)
    sums[key] = sha256(p)
    print(f"  {key:20s} done, {got:,} bytes in {time.time() - t:.0f}s")


def main(argv):
    if "--list" in argv:
        by_dom = {}
        for k, (dom, doi, aid, name, size) in CORPUS.items():
            by_dom.setdefault(dom, []).append((k, name, size, doi))
        tot = 0
        for dom in sorted(by_dom):
            print(f"\n{dom}")
            for k, name, size, doi in by_dom[dom]:
                print(f"  {k:20s} {name:48s} {size:>12,}  {doi}")
                tot += size
        print(f"\n{len(CORPUS)} files, {tot:,} bytes, {len(by_dom)} domains")
        return
    keys = [a for a in argv if a in CORPUS] or list(CORPUS)
    sums = load_checksums()
    print(f"Fetching {len(keys)} files into {DEST}")
    for k in keys:
        try:
            fetch(k, sums)
        except Exception as e:                             # noqa: BLE001
            print(f"  {k:20s} FAILED: {type(e).__name__}: {e}")
        save_checksums(sums)
    print(f"\nChecksums in {CHECKSUMS}")


if __name__ == "__main__":
    main(sys.argv[1:])

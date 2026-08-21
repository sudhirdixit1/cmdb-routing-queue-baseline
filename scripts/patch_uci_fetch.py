"""Add UCI 498 to the corpus fetcher, so "one command fetches every dataset"
is true rather than nearly true.

Section 11 said "Twenty-three files ... 22 logs parse". The twenty-three are
the files `fetch_corpus.py` resolves through the 4TU API; the twenty-two logs
include UCI 498, which is on the UCI Machine Learning Repository and was
therefore not among them. The sentence implied the twenty-two came from the
twenty-three and they did not.

Two ways to fix that. Restate the sentence, or fetch the file. Fetching it is
better: it makes the one-command claim exact, and it removes the last dataset
a reader had to go and find by hand.

    python scripts/patch_uci_fetch.py --check
    python scripts/patch_uci_fetch.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "scripts" / "fetch_corpus.py"

OLD_MANIFEST = '''    # --- enforcement ------------------------------------------------------
    "RoadFines":        ("enforcement", "10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5",
                         12683249, "Road_Traffic_Fine_Management_Process.xes.gz", 3454978),
}'''
NEW_MANIFEST = '''    # --- enforcement ------------------------------------------------------
    "RoadFines":        ("enforcement", "10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5",
                         12683249, "Road_Traffic_Fine_Management_Process.xes.gz", 3454978),
    # --- ITSM, and the one file that is not on 4TU ------------------------
    # UCI 498 lives on the UCI Machine Learning Repository, so it resolves
    # through UCI_DIRECT below rather than through the 4TU API.  It is listed
    # here anyway: a reader should not have to know which registry a dataset
    # happens to sit in, and section 11 counts files, not registries.
    "UCI498":           ("itsm", "10.24432/C57S4H",
                         None, "incident_event_log.zip", 2400214),
}

#  key -> a direct URL, for datasets not on 4TU.
UCI_DIRECT = {
    "UCI498": "https://archive.ics.uci.edu/static/public/498/"
              "incident+management+process+enriched+event+log.zip",
}'''

OLD_INRAW = '''IN_RAW = {"BPIC14_incident", "BPIC14_activity", "BPIC14_interaction",
          "BPIC13_incidents"}'''
NEW_INRAW = '''IN_RAW = {"BPIC14_incident", "BPIC14_activity", "BPIC14_interaction",
          "BPIC13_incidents", "UCI498"}'''

OLD_FETCH = '''    try:
        url, rsize = resolve(aid, name)
    except FileNotFoundError:
        url, rsize = resolve_by_search(name)'''
NEW_FETCH = '''    if key in UCI_DIRECT:
        url, rsize = UCI_DIRECT[key], size
    else:
        try:
            url, rsize = resolve(aid, name)
        except FileNotFoundError:
            url, rsize = resolve_by_search(name)'''


def main(argv):
    s = F.read_text(encoding="utf-8")
    pairs = [("manifest", OLD_MANIFEST, NEW_MANIFEST),
             ("in-raw", OLD_INRAW, NEW_INRAW),
             ("fetch", OLD_FETCH, NEW_FETCH)]
    missing = [f"{n}: anchor appears {s.count(o)} times"
               for n, o, _ in pairs if s.count(o) != 1]
    if missing:
        print("ANCHORS NOT FOUND -- nothing written:")
        for m in missing:
            print("  " + m)
        return 1
    if "--check" in argv:
        print("all 3 anchors found")
        return 0
    for n, o, w in pairs:
        s = s.replace(o, w, 1)
        print(f"  applied {n}")
    F.write_text(s, encoding="utf-8")
    print(f"wrote {F}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

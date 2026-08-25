"""provenance -- WHICH VERSION OF WHICH SCRIPT PRODUCED THE NUMBERS.

Round nineteen.  `make_numbers.py --strict` guarantees that every macro in the
manuscript resolved.  It does not guarantee that the file it resolved from is
current, and this round produced the exact failure that gap allows: a
two-replicate smoke test of s18, run under the wrong seed and against an
estimand that was corrected an hour later, left result files behind.  Every
macro reading them resolved cleanly, to a wrong number, and `--strict` passed.

A missing file is loud.  A stale one is silent, which is worse.

Modification time alone cannot answer the question --- editing a script's
output format, or its docstring, makes its results "stale" without making them
wrong --- so this file records the SHA-256 of each analysis script at the
moment its outputs were last ACCEPTED, in `results/provenance.json`, together
with a note saying why.  Accepting is a deliberate act with a reason attached,
and the reason is in the repository.

    python provenance.py                       # report
    python provenance.py --accept s01_surface.py --note "why"
    python provenance.py --accept-all --note "full pipeline rerun"

`make_numbers.py` calls `mismatches()` and refuses under `--strict`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STORE = ROOT / "results" / "provenance.json"

#  Only the scripts that WRITE the result files the manuscript reads.  A
#  helper module that several of them import is covered by their own hashes
#  changing when its interface does, and by the tests.
def analysis_scripts():
    return sorted(p for p in HERE.glob("s[0-9][0-9]*.py")
                  if not p.name.endswith("_test.py"))


def _normalise(b: bytes) -> bytes:
    """CRLF and lone CR to LF.

    Round twenty-five.  The hash was taken over raw bytes, so a checkout whose
    line endings differed from the accepting machine's reported every script as
    out of date.  A fresh clone on Unix of the state this repository was handed
    over in reported twenty of thirty-seven stale, and not one of them had
    changed by a character: the store had been written where those twenty stood
    with CRLF.  A guard that fires on a checkout artefact teaches its reader to
    ignore it, which is the opposite of what this file is for, so the hash is
    now taken over content with the line endings normalised away.
    """
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha(path):
    return hashlib.sha256(_normalise(Path(path).read_bytes())).hexdigest()[:16]


def sha_crlf(path):
    """What `sha` would have returned for this content rendered with CRLF.

    Only `--renormalise` uses it, to recognise an entry that is stale by line
    ending alone and migrate it without asserting anything new about the run.
    """
    b = _normalise(Path(path).read_bytes()).replace(b"\n", b"\r\n")
    return hashlib.sha256(b).hexdigest()[:16]


def load():
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save(d):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")


def mismatches():
    """[(script, recorded_sha, current_sha, note)] for every script whose
    source has changed since its outputs were accepted, plus every script that
    has never been accepted at all."""
    rec, out = load(), []
    for p in analysis_scripts():
        cur = sha(p)
        got = rec.get(p.name)
        if got is None:
            out.append((p.name, None, cur, "never accepted"))
        elif got.get("sha") != cur:
            out.append((p.name, got.get("sha"), cur, got.get("note", "")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--accept", action="append", default=[],
                    help="script filename whose current outputs are correct")
    ap.add_argument("--accept-all", action="store_true")
    ap.add_argument("--renormalise", action="store_true",
                    help="one-time migration: rewrite entries that are stale "
                         "only because they were recorded over CRLF bytes")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)

    if a.renormalise:
        rec, moved, left = load(), [], []
        for p in analysis_scripts():
            got = rec.get(p.name)
            if got is None or got.get("sha") == sha(p):
                continue
            if got.get("sha") == sha_crlf(p):
                got["sha"] = sha(p)
                got["renormalised"] = time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                moved.append(p.name)
            else:
                left.append(p.name)
        save(rec)
        print("renormalised %d entries; %d still out of date"
              % (len(moved), len(left)))
        for n in moved:
            print("  line endings only  %-26s %s" % (n, rec[n]["sha"]))
        for n in left:
            print("  CHANGED, re-run it %-26s" % n)
        return 1 if left else 0

    if a.accept or a.accept_all:
        if not a.note:
            sys.exit("--note is required: say why these outputs are current")
        rec = load()
        names = ([p.name for p in analysis_scripts()] if a.accept_all
                 else a.accept)
        for n in names:
            p = HERE / n
            if not p.exists():
                sys.exit("no such script: %s" % n)
            rec[n] = dict(sha=sha(p), note=a.note,
                          at=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           time.gmtime()))
            print("  accepted %-26s %s" % (n, rec[n]["sha"]))
        save(rec)
        return 0

    bad = mismatches()
    rec = load()
    print("provenance: %d analysis scripts, %d accepted, %d out of date"
          % (len(analysis_scripts()), len(rec), len(bad)))
    for name, was, now, note in bad:
        print("  %-26s %s -> %s   %s"
              % (name, was or "(none)", now, note))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

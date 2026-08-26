"""insert_doi -- PUT THE MINTED ARCHIVE DOI INTO THE MANUSCRIPT.

Round twenty-five.  `submission/OWNER-ACTIONS.md` item E has two clauses.
The second --- *confirm the archived release reproduces the submitted numbers
to the digit* --- is `scripts/verify_release.py`, and it passes.  The first
--- *mint the archive DOI and insert it* --- is two halves that are not alike:

  MINTING is owner-only and cannot be automated.  A DOI is minted by Zenodo
  when the depositing account publishes a deposit.  No credential in this
  repository can create one, and no other repository's DOI is this archive's
  DOI.  That half is a person logging in.

  INSERTING is mechanical, and it is what this file does.  Everything the
  manuscript says about the archive flows from one macro, `\\zenodoDOI`,
  which `scripts/make_numbers.py` reads out of `.zenodo.json`.  So the whole
  insertion is: write the key, regenerate, rebuild, re-run every gate.

    python scripts/insert_doi.py 10.5281/zenodo.1234567

WHY IT CHECKS THE DOI BEFORE WRITING IT.  A DOI is an identifier the reader
will follow.  A mistyped one, or one belonging to a different deposit, puts a
live link in a submitted paper that goes somewhere else --- which is worse
than the honest placeholder now standing in its place, because the
placeholder cannot mislead.  So the DOI is resolved against Zenodo's public
API first (no credential needed to read), and the record it names is checked
against this archive: the title must match `.zenodo.json`'s, and the
depositing creator must be among its creators.  A DOI that does not resolve,
or resolves to somebody else's record, is refused.

    --no-verify   skip the network check (use only offline, and check by hand)
    --dry-run     say what would change, write nothing

Exit status is non-zero if the DOI is refused or any gate fails.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZEN = ROOT / ".zenodo.json"

#: Zenodo mints DOIs under a single prefix; a concept DOI and a version DOI
#: differ only in the record number.  Either is acceptable --- the concept DOI
#: is arguably the better citation --- so both shapes pass.
DOI_RE = re.compile(r"^10\.5281/zenodo\.(\d+)$")

API = "https://zenodo.org/api/records/%s"

#: the chain the manuscript's own gates run, in the order a failure is most
#: usefully reported.  `make_numbers` first because the DOI enters there.
CHAIN = [
    ("make_numbers.py", ["--strict"], "regenerate every macro from results/"),
    ("assemble_paper.py", [], "parts -> the two documents"),
    ("texlint.py", [], "the manuscript's own compliance checks"),
    ("verify_numbers.py", [], "re-derive each macro with independent code"),
    ("build_journal.py", [], "build both documents"),
    ("check_response_refs.py", [], "every cross-reference and archive claim"),
]

ENV = dict(os.environ)
ENV.update({v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                             "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                             "VECLIB_MAXIMUM_THREADS")})


def normalise(raw: str) -> str:
    """Accept what a person will actually paste, return the bare DOI."""
    d = raw.strip()
    for prefix in ("https://doi.org/", "http://doi.org/",
                   "https://zenodo.org/doi/", "doi:", "DOI:"):
        if d.lower().startswith(prefix.lower()):
            d = d[len(prefix):]
    return d.strip().strip("/")


def fetch(url: str):
    """(status, parsed body).  `requests` if it is installed, because the
    stock urllib on a framework Python has no CA bundle and fails every
    HTTPS fetch with a certificate error --- which would read as `the DOI
    could not be checked' on a machine where it can be."""
    try:
        import requests
        r = requests.get(url, timeout=30)
        return r.status_code, (r.json() if r.status_code == 200 else None)
    except ImportError:
        pass
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = None
    try:
        with urllib.request.urlopen(url, timeout=30, context=ctx) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None


def resolve(doi: str, meta: dict) -> list[str]:
    """Is this DOI a real Zenodo record, and is it THIS archive?"""
    rec_id = DOI_RE.match(doi).group(1)
    try:
        status, rec = fetch(API % rec_id)
    except Exception as e:  # noqa: BLE001
        return ["could not reach Zenodo to check the DOI (%s). Re-run when "
                "the network is available, or pass --no-verify and check by "
                "hand. Nothing was written." % e]
    if status == 404:
        return ["Zenodo has no record %s --- the DOI %s does not resolve. "
                "Nothing was written." % (rec_id, doi)]
    if status != 200 or rec is None:
        return ["Zenodo returned HTTP %s for record %s; could not check the "
                "DOI. Nothing was written." % (status, rec_id)]

    m = rec.get("metadata", {})
    bad = []
    got = (m.get("title") or "").strip()
    want = (meta.get("title") or "").strip()
    if got and want and got != want:
        bad.append("record %s is titled\n          %r\n        but this "
                   "archive is titled\n          %r\n        --- that is a "
                   "different deposit." % (rec_id, got[:90], want[:90]))
    names = {c.get("name", "") for c in (m.get("creators") or [])}
    ours = {c.get("name", "") for c in (meta.get("creators") or [])}
    if names and ours and not (names & ours):
        bad.append("record %s is deposited by %s, and this archive's creators "
                   "are %s." % (rec_id, ", ".join(sorted(names)[:3]),
                                ", ".join(sorted(ours)[:3])))
    if not bad:
        print("  resolves to Zenodo record %s, titled as this archive is, "
              "by %s" % (rec_id, ", ".join(sorted(names)) or "(no creator)"))
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("doi", help="the minted DOI, e.g. 10.5281/zenodo.1234567")
    ap.add_argument("--no-verify", action="store_true",
                    help="do not resolve the DOI against Zenodo first")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change, write nothing")
    a = ap.parse_args(argv)

    print("=" * 92)
    print("insert_doi  PUT THE MINTED ARCHIVE DOI INTO THE MANUSCRIPT")
    print("=" * 92)

    doi = normalise(a.doi)
    if not DOI_RE.match(doi):
        print("  REFUSED  %r is not a Zenodo DOI. It should look like\n"
              "           10.5281/zenodo.1234567 (a bare DOI or a "
              "doi.org URL).\n           Nothing was written." % doi)
        return 1
    print("  DOI       %s" % doi)

    meta = json.loads(ZEN.read_text(encoding="utf-8"))
    have = meta.get("doi") or ""
    if have and have != doi:
        print("  note      .zenodo.json already carries %s; it will be "
              "replaced." % have)

    if not a.no_verify:
        bad = resolve(doi, meta)
        if bad:
            for b in bad:
                print("  REFUSED  %s" % b)
            return 1
    else:
        print("  note      --no-verify: the DOI was NOT checked against "
              "Zenodo. Check it by hand.")

    if a.dry_run:
        print("\n  --dry-run: would write \"doi\": %r into .zenodo.json and "
              "run\n  %s" % (doi, ", ".join(s for s, _, _ in CHAIN)))
        return 0

    #  `version` is the last key, and the DOI belongs beside it: the archive's
    #  identity, not its content.  Rewriting the whole file preserves the
    #  order of everything above it.
    ordered = {k: v for k, v in meta.items() if k != "doi"}
    ordered["doi"] = doi
    ZEN.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print("  written   .zenodo.json now carries the DOI")

    print()
    for script, args, what in CHAIN:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / script),
                            *args], capture_output=True, text=True, env=ENV,
                           cwd=ROOT)
        tail = (r.stdout or r.stderr).strip().splitlines()
        print("  %-24s exit=%d  %s"
              % (script, r.returncode, tail[-1][:54] if tail else ""))
        if r.returncode != 0:
            print("\n" + "\n".join((r.stdout + r.stderr).splitlines()[-15:]))
            print("\ninsert_doi: %s failed (%s). The DOI is written but the "
                  "manuscript\n  did not rebuild --- fix the failure and "
                  "re-run the gates." % (script, what))
            return 1

    macro = subprocess.run(
        ["grep", "-n", r"newcommand{\\zenodoDOI}", str(ROOT / "paper" /
                                                       "numbers.tex")],
        capture_output=True, text=True).stdout.strip()
    print("\n  macro     %s" % (macro[:110] or "(not found)"))
    print("\ninsert_doi: the DOI is in .zenodo.json, `\\zenodoDOI` carries it,"
          "\n  both documents rebuilt and every gate is green. Commit "
          "`.zenodo.json`,\n  `paper/numbers.tex` and the assembled documents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

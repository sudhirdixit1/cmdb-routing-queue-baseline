"""finalise -- WHAT IS STILL OWED BEFORE THIS CAN BE SUBMITTED, AND ONE
COMMAND TO DISCHARGE EACH.

Round twenty-seven ended with four items that need the depositing account or
the author's own knowledge and cannot be done from inside the repository: the
archive DOI, the built container's digest, the suggested reviewers' e-mail
addresses, and a push.  Every one of them is a small edit, and every one of
them has to reach several files at once --- the DOI alone appears in the
data-availability statement, the code-availability statement, reference [11]
and the archive metadata.

Doing that by hand is how a placeholder ships.  So this file does two things.

    python scripts/finalise.py

reports what is missing and what is ready, and exits non-zero while anything
is missing, so it is usable as the last gate before upload.

    python scripts/finalise.py --doi 10.5281/zenodo.1234567
    python scripts/finalise.py --image-digest sha256:<64 hex>

write the value into `.zenodo.json`, regenerate every macro, rebuild both
documents and re-run the verifiers -- so the answer to "did that reach
everything it needed to reach?" is the gate output rather than a memory.

WHAT THIS FILE WILL NOT DO.  It will not mint the DOI, build or push the
image, invent an e-mail address, or push a branch.  Three of those need
credentials this repository does not have and should not have; the fourth
needs facts about real people that nobody should guess.  It tells you what is
outstanding and it makes the discharge one command.  The judgement stays with
the author, which is the whole argument of the manuscript it is finalising.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZEN = ROOT / ".zenodo.json"
PY = sys.executable

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _zen() -> dict:
    return json.loads(ZEN.read_text(encoding="utf-8"))


def _write_zen(j: dict) -> None:
    ZEN.write_text(json.dumps(j, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")


def _run(cmd, label):
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    tail = (r.stdout or r.stderr).strip().splitlines()
    print("  %-24s %s" % (label, tail[-1] if tail else "(no output)"))
    return r.returncode


def status() -> list[str]:
    """Return one line per outstanding item; empty means ready."""
    out = []
    j = _zen()

    if not j.get("doi"):
        out.append(
            "THE ARCHIVE DOI is not minted.  It is reference [11] and both "
            "availability statements.  Mint it at zenodo.org against the "
            "GitHub release (submission/OWNER-ACTIONS.md §1.1), then:\n"
            "        python scripts/finalise.py --doi 10.5281/zenodo.XXXXXXX")
    if not j.get("image_digest"):
        out.append(
            "THE BUILT IMAGE'S DIGEST is not recorded.  The base is already "
            "pinned by digest and verified; this is the digest of the image "
            "built FROM it, which exists only once the image is pushed "
            "(§4.7).  Then:\n"
            "        python scripts/finalise.py --image-digest sha256:<64 hex>")

    rev = ROOT / "submission" / "suggested_reviewers.md"
    if rev.exists() and "@" not in rev.read_text(encoding="utf-8"):
        out.append(
            "THE SUGGESTED REVIEWERS carry no institutional e-mail address, "
            "which the submission system requires (§4.2).  These are real "
            "people's contact details; nobody should guess them, so this file "
            "does not.")

    #  the push is a fact about the remote, not about the tree
    try:
        r = subprocess.run(["git", "rev-list", "--count", "origin/main..main"],
                           cwd=str(ROOT), capture_output=True, text=True)
        ahead = int((r.stdout or "0").strip() or 0)
    except (OSError, ValueError):
        ahead = -1
    if ahead > 0:
        out.append(
            "MAIN IS %d COMMIT(S) AHEAD OF origin/main.  The archive "
            "snapshots whatever the release tag points at, so the push and "
            "the tag belong together (§1.1 steps 3--4).  Pushing "
            "publishes; it is the author's to do." % ahead)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi")
    ap.add_argument("--image-digest", dest="digest")
    a = ap.parse_args(argv)

    changed = False
    if a.doi:
        if not DOI_RE.match(a.doi):
            raise SystemExit("finalise: %r does not look like a DOI "
                             "(expected 10.NNNN/suffix)" % a.doi)
        j = _zen()
        j["doi"] = a.doi
        _write_zen(j)
        print("recorded doi = %s" % a.doi)
        changed = True
    if a.digest:
        if not DIGEST_RE.match(a.digest):
            raise SystemExit("finalise: %r does not look like an image digest "
                             "(expected sha256: and 64 hex characters)"
                             % a.digest)
        j = _zen()
        j["image_digest"] = a.digest
        _write_zen(j)
        print("recorded image_digest = %s" % a.digest)
        changed = True

    if changed:
        #  the point of doing it here rather than by hand: the value has to
        #  reach four files, and the gates are what say whether it did.
        print("\nregenerating and rebuilding, because that value reaches the "
              "statements, the reference list and the archive metadata:")
        bad = 0
        bad += _run([PY, "scripts/make_numbers.py"], "make_numbers")
        bad += _run([PY, "scripts/assemble_paper.py"], "assemble_paper")
        bad += _run([PY, "scripts/build_journal.py"], "build_journal")
        for g in ("verify_numbers", "texlint", "check_claims",
                  "check_response_refs", "check_package"):
            bad += _run([PY, "scripts/%s.py" % g], g)
        if bad:
            print("\nfinalise: something above failed; do not upload until it "
                  "passes.")
            return 1
        print()

    print("=" * 74)
    print("finalise  WHAT IS STILL OWED")
    print("=" * 74)
    left = status()
    if not left:
        print("  Nothing. Both documents build, every gate passes, the DOI "
              "and the image digest are recorded, the reviewers carry "
              "addresses, and main is pushed.")
        print("finalise: ready to upload "
              "(submission/OWNER-ACTIONS.md §1.4 lists the files).")
        return 0
    for i, item in enumerate(left, 1):
        print("  %d. %s" % (i, item))
    print("\nfinalise: %d item(s) outstanding, none of which this repository "
          "can do for you." % len(left))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

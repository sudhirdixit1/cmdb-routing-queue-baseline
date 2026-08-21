"""Bring `.zenodo.json` up to date with round seventeen.

It still carried the round-sixteen title, a description quoting 325 literals
and 119 corruptions, and three dataset DOIs. The corpus is now fourteen
collections and the counts have moved twice since. Zenodo reads this file
automatically when the DOI is minted, so a stale one publishes stale metadata
that nobody re-reads.

    python scripts/patch_zenodo_r17.py --check
    python scripts/patch_zenodo_r17.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Z = ROOT / ".zenodo.json"

TITLE = ("Four Choices Behind One Number: analysis code, a pre-registered "
         "protocol, derived results and a verification harness")

DESCRIPTION = (
    "<p>Analysis code, a pre-registered protocol, derived result files, "
    "figures and a verification harness for the study <em>Four Choices Behind "
    "One Number: Reporting the Incremental Value of a Recorded Field</em>.</p>"
    "<p>The study argues, and then measures, that what a recorded field is "
    "worth is a function of four choices which are almost never stated: the "
    "baseline of already-recorded fields the comparison may contain, the "
    "metric, the operating point, and the population of the register the "
    "field reads from. The demonstration is a configuration management "
    "database on a public log of 45,455 incidents, and each choice moves the "
    "answer by more than the effect being reported. Admitting one further "
    "already-recorded field takes the item's value from +0.183 AUC to +0.103; "
    "admitting a second takes it to +0.001.</p>"
    "<p><strong>Pre-registration.</strong> <code>PROTOCOL.md</code> fixes the "
    "corpus, the targets, the rules assigning every attribute to a role, the "
    "exclusion codes, the estimator, the seed, the instruments and the "
    "outcome that would falsify the claim. It was committed before any corpus "
    "result file existed, in a commit that adds no result file. The "
    "registered generality claim is falsified by its own criterion and the "
    "paper reports the negative.</p>"
    "<p><strong>What is included.</strong> Every analysis script, every "
    "derived <code>results/*.csv</code>, the figure generators, the LaTeX "
    "source, an environment locked by artefact hash, a container that pins "
    "BLAS thread counts, a referee log recording twenty-two adversarial "
    "objections with their dispositions, and "
    "<code>scripts/verify_paper.py</code>, which recomputes each of the 417 "
    "numeric literals in the manuscript from a result file or from the raw "
    "data and fails if any literal in the body is unaccounted for. "
    "<code>scripts/attack_verifier.py</code> is that checker's own regression "
    "suite: 199 corruptions drawn from defects found in earlier versions of "
    "this work. <code>scripts/reproduce_all.py</code> fetches all twenty-four "
    "public files by DOI, checksums them, and runs the whole thing in "
    "dependency order in one command.</p>"
    "<p><strong>What is not included.</strong> No row of any dataset. All "
    "twenty-four files are public and are cited by persistent identifier "
    "below and in <code>REPRODUCE.md</code>; none is redistributed here.</p>"
    "<p><strong>What the harness does not do.</strong> It guards numbers "
    "thoroughly and prose only where a guard was written by hand. The paper "
    "reports eleven of the author's own errors as results rather than editing "
    "them away, and all eleven are claims about what a number means -- the "
    "checker would have caught none of them. Two of the three found in the "
    "final round are sentences in which every individual literal was correct "
    "and the relation the prose asserted between them was not. This is stated "
    "in the repository and in the paper in the same words.</p>")

DOIS = [
    "10.4121/uuid:c3e5d162-0cfd-4bb0-bd82-af5268819c35",   # BPIC 2014
    "10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee",   # BPIC 2013 incidents
    "10.4121/uuid:3537c19d-6c64-4b1d-815d-915ab0e479da",   # BPIC 2013 open
    "10.4121/uuid:c2c3b154-ab26-4b31-a0e8-8f2350ddac11",   # BPIC 2013 closed
    "10.4121/uuid:0c60edf1-6f83-4e75-9367-4c63b3e9d5bb",   # Helpdesk
    "10.24432/C57S4H",                                     # UCI 498
    "10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f",   # BPIC 2012
    "10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b",   # BPIC 2017
    "10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1",   # BPIC 2019
    "10.4121/uuid:31a308ef-c844-48da-948c-305d167a0ec1",   # BPIC 2015
    "10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51",   # BPIC 2020
    "10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460",   # Sepsis
    "10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741",   # Hospital billing
    "10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5",   # Road fines
]

KEYWORDS = [
    "incremental value", "baseline specification", "evaluation metrics",
    "pre-registration", "predictive process monitoring",
    "configuration management database", "CMDB", "variable importance",
    "decision curve analysis", "reproducibility", "event log",
    "IT service management",
]


def main(argv):
    d = json.loads(Z.read_text(encoding="utf-8"))
    if "--check" in argv:
        print(f"current title: {d['title'][:60]}...")
        print(f"current related_identifiers: {len(d.get('related_identifiers', []))}")
        return 0
    d["title"] = TITLE
    d["description"] = DESCRIPTION
    d["keywords"] = KEYWORDS
    d["related_identifiers"] = [
        {"identifier": x, "relation": "isDerivedFrom",
         "resource_type": "dataset", "scheme": "doi"} for x in DOIS]
    Z.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8")
    print(f"wrote {Z}: {len(DOIS)} dataset DOIs, {len(KEYWORDS)} keywords")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

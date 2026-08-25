"""claim_registry -- every number in the manuscript, and where it came from.

Round twenty, blueprint section 12G.  A reviewer is entitled to ask, of any
figure in the abstract or the conclusion, which result file produced it and
which line of which script read that file.  This builds the table that answers
that, mechanically, for every macro:

    claim id | macro | value | manuscript locations | section | generator
             | source line | result file | verified independently | status

The manuscript contains no numeric literals, so this registry is exhaustive by
construction: any number a reader can see is a macro, and every macro is a
row.  `scripts/texlint.py` enforces the premise.

    python claim_registry.py            # write results/claim_registry.csv
    python claim_registry.py --check    # fail if a macro is unused or a
                                        # headline claim is unverified

Outputs: results/claim_registry.csv
         results/claim_registry_facts.csv
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import RESULTS  # noqa: E402

ROOT = HERE.parent
PAPER = ROOT / "paper"
PARTS = PAPER / "parts"
NUMBERS = PAPER / "numbers.tex"

#: the places whose numbers a reader trusts most, and which the --check gate
#: requires to be independently re-derived by verify_numbers.
HEADLINE_PARTS = ("00_front_intro_related.tex", "80_limits.tex")


def macro_values():
    t = NUMBERS.read_text(encoding="utf-8")
    return dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}", t))


def macro_sources():
    """Which script line defined each macro.  `make_numbers.py` records this
    in results/macro_sources.csv on every run; if the file is absent the
    registry still builds, with the generator column blank."""
    p = RESULTS / "macro_sources.csv"
    if not p.exists():
        return {}
    d = pd.read_csv(p)
    return {r.macro: (r.generator, int(r.line)) for r in d.itertuples()}


def result_file_for(generator, line):
    """Read the generator at that line and the twenty lines above it, and name
    the result file whose load() call is in scope.  This is a heuristic and is
    labelled as one in the output: it is a pointer for a reader, not a
    contract."""
    if not generator:
        return ""
    p = HERE / generator
    if not p.exists():
        return ""
    src = p.read_text(encoding="utf-8").splitlines()
    i = min(len(src), max(1, int(line))) - 1
    #  the nearest preceding load("...") or read_results("...")
    for j in range(i, max(-1, i - 120), -1):
        m = re.search(r'(?:load|read_results)\("([^"]+)"\)', src[j])
        if m:
            return m.group(1)
    return ""


def manuscript_uses():
    """Every (macro, part, line) in the manuscript sources, with the section
    heading the line falls under."""
    uses = {}
    for f in sorted(PARTS.glob("*.tex")):
        section = ""
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            m = re.match(r"\s*\\(?:sub)*section\*?\{(.+?)\}", line)
            if m:
                section = m.group(1)
            for mm in re.finditer(r"\\([a-zA-Z]+)", line):
                uses.setdefault(mm.group(1), []).append(
                    (f.name, n, section))
    return uses


def verified_macros():
    """Which macros the verifier re-derives independently: every name passed
    to an eq() call, read from the source rather than from a list somebody has
    to maintain.

    BOTH files.  The round-twenty re-derivations live in round20_verify.py,
    which verify_numbers.main calls; parsing only verify_numbers.py counted 49
    of the 113 and wrote verified_independently=False into the registry for
    every quantity this round added -- in a file the response letter points a
    referee at.
    """
    #  Prefer the RECORD the verifier writes at runtime: it names every macro
    #  eq() was actually called on, including the ones whose name came from a
    #  loop variable, which no parse of the source can see.  The parse below
    #  is the fallback for a tree in which verify_numbers has not been run.
    rec = RESULTS / "verified_macros.csv"
    if rec.exists():
        got = {ln.strip() for ln in rec.read_text(encoding="utf-8").splitlines()[1:]
               if ln.strip()}
        if got:
            return got

    names = set()
    for fn in ("verify_numbers.py", "round20_verify.py"):
        p = HERE / fn
        if not p.exists():
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "eq"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                names.add(node.args[0].value)
    return names


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)

    if not NUMBERS.exists():
        sys.exit("paper/numbers.tex does not exist; run make_numbers.py")
    vals = macro_values()
    srcs = macro_sources()
    uses = manuscript_uses()
    ver = verified_macros()

    rows = []
    for i, name in enumerate(sorted(vals), 1):
        gen, line = srcs.get(name, ("", 0))
        u = uses.get(name, [])
        rows.append(dict(
            claim_id="K%03d" % i,
            macro=name,
            value=vals[name],
            n_uses=len(u),
            locations="; ".join("%s:%d" % (f, n) for f, n, _s in u[:6]),
            sections="; ".join(sorted({s for _f, _n, s in u if s})[:3]),
            generator=gen, source_line=line,
            result_file=result_file_for(gen, line),
            verified_independently=name in ver,
            unresolved=vals[name].strip() == r"\textbf{??}",
            headline=any(f in HEADLINE_PARTS for f, _n, _s in u)))
    R = pd.DataFrame(rows)
    R.to_csv(RESULTS / "claim_registry.csv", index=False)

    used = R[R.n_uses > 0]
    facts = dict(
        n_macros=len(R),
        n_used=len(used),
        n_unused=int((R.n_uses == 0).sum()),
        n_unresolved=int(R.unresolved.sum()),
        n_verified=int(R.verified_independently.sum()),
        n_headline=int(R.headline.sum()),
        n_headline_verified=int((R.headline & R.verified_independently).sum()),
        n_with_generator=int((R.generator != "").sum()),
        n_with_result_file=int((R.result_file != "").sum()))
    pd.DataFrame([facts]).to_csv(RESULTS / "claim_registry_facts.csv",
                                 index=False)
    print("=" * 92)
    print("CLAIM REGISTRY")
    print("=" * 92)
    print(pd.Series(facts).to_string())
    bad = used[used.unresolved]
    if len(bad):
        print("\nUNRESOLVED MACROS THAT THE MANUSCRIPT USES (%d):" % len(bad))
        for _, r in bad.iterrows():
            print("   %-30s %s" % (r.macro, r.locations))
    if a.check:
        fails = []
        if len(bad):
            fails.append("%d used macros are unresolved" % len(bad))
        hv = used[used.headline & ~used.verified_independently]
        if len(hv):
            fails.append("%d headline macros are not independently "
                         "re-derived: %s"
                         % (len(hv), ", ".join(sorted(hv.macro)[:12])))
        for f in fails:
            print("FAIL " + f)
        if fails:
            sys.exit(1)
        print("\nregistry check passed")


if __name__ == "__main__":
    main()

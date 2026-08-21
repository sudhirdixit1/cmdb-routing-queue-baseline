"""Twenty-three becomes twenty-four, everywhere.

Section 11 said "Twenty-three files ... 22 logs parse". The twenty-three were
the files `fetch_corpus.py` resolved through the 4TU API; the twenty-two logs
included UCI 498, which sits on the UCI Machine Learning Repository and was
therefore not among them. The sentence implied the twenty-two came from the
twenty-three, and they did not.

`patch_uci_fetch.py` added UCI 498 to the fetcher, so there are now
twenty-four files and every one of them comes down with one command. This
updates every place that quoted the old count, including the checker's own
`ck_word` and the word list it compares against.

    python scripts/patch_24_r17.py --check
    python scripts/patch_24_r17.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EDITS = [
    ("paper", "paper/iaai27_empty_cmdb.tex",
     "Twenty-three files across seven domains, fetched by DOI with a recorded",
     "Twenty-four files across seven domains, fetched by DOI with a recorded"),
    ("verifier-word-list", "scripts/verify_paper.py",
     '"twenty-two": 22, "twenty-three": 23}',
     '"twenty-two": 22, "twenty-three": 23,\n         "twenty-four": 24}'),
    ("verifier-check", "scripts/verify_paper.py",
     'ck_word("corpus files", 23, "twenty-three",\n        anchor="files across seven domains")',
     'ck_word("corpus files", len(_FETCH.CORPUS), "twenty-four",\n'
     '        anchor="files across seven domains")'),
    ("verifier-import", "scripts/verify_paper.py",
     '_r38D = pd.read_csv(R / "r38_axisD.csv")',
     '_r38D = pd.read_csv(R / "r38_axisD.csv")\n'
     '#  the file count is read from the fetcher\'s own manifest, so the paper\n'
     '#  and the thing that downloads the data cannot drift apart.\n'
     'import fetch_corpus as _FETCH'),
    ("handoff", "HANDOFF.md",
     "adding one file. Twenty-three files by DOI across seven domains; 22 logs parse;",
     "adding one file. Twenty-four files by DOI across seven domains; 22 logs parse;"),
    ("protocol", "PROTOCOL.md",
     "the opportunity: with twenty-three files and seven domains, an analyst who picks",
     "the opportunity: with twenty-four files and seven domains, an analyst who picks"),
    ("plan-fetch", "PLAN-STRONG-ACCEPT.md",
     "— A `fetch` stage runs `fetch_corpus.py`: 23 files, 7 domains, resolved",
     "— A `fetch` stage runs `fetch_corpus.py`: 24 files, 7 domains, resolved"),
    ("plan-data", "PLAN-STRONG-ACCEPT.md",
     "— All rewritten. Data availability now lists **23 files across 7",
     "— All rewritten. Data availability now lists **24 files across 7"),
    ("plan-repro", "PLAN-STRONG-ACCEPT.md",
     "— `python scripts/reproduce_all.py` now fetches all 23 datasets by DOI,",
     "— `python scripts/reproduce_all.py` now fetches all 24 datasets by DOI,"),
    ("plan-record", "PLAN-STRONG-ACCEPT.md",
     "**Falsified, as registered.** 23 files by DOI over 7 domains; 22 parse;",
     "**Falsified, as registered.** 24 files by DOI over 7 domains; 22 parse;"),
    ("readme-scripts", "README.md",
     "| `fetch_corpus.py` | 23 files, 7 domains, by DOI, with checksums |",
     "| `fetch_corpus.py` | 24 files, 7 domains, by DOI, with checksums |"),
    ("readme-datasets", "README.md",
     "Twenty-three files across seven domains, all public, none redistributed here.",
     "Twenty-four files across seven domains, all public, none redistributed here."),
    ("repro", "REPRODUCE.md",
     "python scripts/fetch_corpus.py          # 23 files, 7 domains, by DOI",
     "python scripts/fetch_corpus.py          # 24 files, 7 domains, by DOI"),
    ("cover-1", "submission/cover_letter.md",
     "verifier's own regression test. One command fetches all twenty-three datasets",
     "verifier's own regression test. One command fetches all twenty-four datasets"),
    ("cover-2", "submission/cover_letter.md",
     "of the organisations whose logs are analysed. All twenty-three datasets are",
     "of the organisations whose logs are analysed. All twenty-four datasets are"),
    ("credit", "submission/credit_statement.md",
     "and twenty-three public files to provide (Resources).",
     "and twenty-four public files to provide (Resources)."),
    ("data-1", "submission/data_availability.md",
     "All twenty-three files analysed in this study are public and none is",
     "All twenty-four files analysed in this study are public and none is"),
    ("data-2", "submission/data_availability.md",
     "Twenty-three files across seven domains. The first three carry the primary",
     "Twenty-four files across seven domains. The first three carry the primary"),
]


def main(argv):
    problems = []
    for name, rel, old, _new in EDITS:
        p = ROOT / rel
        n = p.read_text(encoding="utf-8").count(old) if p.exists() else -1
        if n != 1:
            problems.append(f"{name} ({rel}): anchor appears {n} times")
    if problems:
        print("ANCHORS NOT FOUND -- nothing written:")
        for p in problems:
            print("  " + p)
        return 1
    if "--check" in argv:
        print(f"all {len(EDITS)} anchors found")
        return 0
    for name, rel, old, new in EDITS:
        p = ROOT / rel
        p.write_text(p.read_text(encoding="utf-8").replace(old, new, 1),
                     encoding="utf-8")
        print(f"  applied {name} -> {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

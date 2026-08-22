"""Re-derive the character counts in submission/highlights.txt.

    python scripts/check_highlights.py          # lint
    python scripts/check_highlights.py --fix    # rewrite the prefixes

WHY THIS EXISTS.  The file has now shipped twice with hand-counted lengths
that were wrong -- round sixteen's five were wrong by 3 to 11 characters, and
round eighteen's rewrite got four of nine wrong on the first try, in a file
whose own preamble warns against exactly that.  A count a human writes is a
claim like any other and belongs in a script.  Exit status is non-zero if any
stated length is wrong or any bullet exceeds the publisher's limit.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "submission" / "highlights.txt"
LIMIT = 85
LINE = re.compile(r"(?m)^\[(\d+)\] (.+)$")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args(argv)
    t = P.read_text(encoding="utf-8")
    wrong, over = [], []
    for m in LINE.finditer(t):
        stated, text = int(m.group(1)), m.group(2)
        if len(text) != stated:
            wrong.append((stated, len(text), text))
        if len(text) > LIMIT:
            over.append((len(text), text))
    if a.fix:
        t = LINE.sub(lambda m: f"[{len(m.group(2))}] {m.group(2)}", t)
        P.write_text(t, encoding="utf-8")
        print(f"rewrote {len(list(LINE.finditer(t)))} prefixes")
    for stated, actual, text in wrong:
        print(f"  WRONG  stated {stated}, actual {actual}: {text[:56]}")
    for actual, text in over:
        print(f"  OVER {LIMIT}  ({actual}): {text[:56]}")
    n = len(list(LINE.finditer(P.read_text(encoding='utf-8'))))
    if a.fix:
        over = [(len(m.group(2)), m.group(2))
                for m in LINE.finditer(P.read_text(encoding="utf-8"))
                if len(m.group(2)) > LIMIT]
        for actual, text in over:
            print(f"  OVER {LIMIT}  ({actual}): {text[:56]}")
        wrong = []
    print(f"{n} bullets; {len(wrong)} miscounted; {len(over)} over {LIMIT}")
    return 1 if (wrong or over) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

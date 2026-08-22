"""Extract numeric literals from LaTeX source, correctly.

The previous verifier stripped comments with re.sub(r"%.*", " ", body), which
treats an ESCAPED percent (\\%) as a comment marker.  In a paper full of
percentages that deleted 8.2% of the body and 24 literals -- including most
of the results table -- and a fabricated number injected into such a line
passed verification with "0 failed".

This module strips only genuine comments: a % that is not preceded by an odd
number of backslashes.
"""
import re

_COMMENT = re.compile(r"(?<!\\)((?:\\\\)*)%.*")


def strip_comments(tex: str) -> str:
    """Remove LaTeX comments, preserving escaped percent signs."""
    out = []
    for line in tex.split("\n"):
        out.append(_COMMENT.sub(r"\1", line))
    return "\n".join(out)


def body_of(tex: str) -> str:
    #  ROUND EIGHTEEN, and it is the same shape as every other hole this
    #  apparatus has had: a consumer that silently stops seeing part of its
    #  input.  This function used to cut the body at \bibliographystyle,
    #  which was a convenient end-marker in a paper that had no appendix.
    #  The moment round eighteen moved five subsections and added five more
    #  into an \appendix -- which sits AFTER the bibliography commands in
    #  this document -- every number in them became invisible: 870 checks
    #  failed with "does not appear in the paper" against text that was
    #  sitting in the file.  An appendix is part of the paper and its numbers
    #  are claims.  The body now runs to \end{document} and the two
    #  bibliography COMMANDS are removed individually.
    if "\\begin{document}" in tex:
        tex = tex.split("\\begin{document}", 1)[1]
    if "\\end{document}" in tex:
        tex = tex.split("\\end{document}", 1)[0]
    tex = re.sub(r"\\bibliographystyle\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\bibliography\{[^}]*\}", " ", tex)
    tex = strip_comments(tex)
    tex = re.sub(r"\\includegraphics\[[^\]]*\]\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\cite[a-z]*\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(?:label|ref|usepackage|documentclass)\{[^}]*\}", " ", tex)
    return tex


def literals(tex: str) -> set:
    """Every numeric literal a reader would see as a claim.

    SIGN-AWARE.  An earlier version dropped the sign, so changing $+0.103$ to
    $-0.103$ in a results table left the literal set unchanged and passed
    verification.  A leading + or - is now part of the token when the source
    carries one.
    """
    b = body_of(tex)
    # a sign only counts when it is not a hyphen inside a date or word
    pat = (r"(?<![\w])[+-]?\d+\.\d+"
           r"|(?<![\w])[+-]?\d{1,3}(?:\{,\}\d{3})+"
           r"|(?<![\w])[+-]?\d+")
    return set(re.findall(pat, b))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    t = Path(sys.argv[1]).read_text(encoding="utf-8")
    naive = re.sub(r"%.*", " ", body_of(t))
    pat = r"\d+\.\d+|\d+"
    naive_lits = set(re.findall(pat, naive))
    print(f"correct strip : {len(literals(t))} literals")
    print(f"naive strip   : {len(naive_lits)} literals")
    missed = literals(t) - naive_lits
    print(f"literals the naive version never scans ({len(missed)}):")
    print("  " + ", ".join(sorted(missed)))

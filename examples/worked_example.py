"""A worked example of `fieldvalue`, on a dataset that is NOT one of the
paper's event logs.

THE QUESTION.  UCI Adult (Census Income, doi:10.24432/C5XW20) predicts whether
a person's income exceeds $50k.  Suppose an analyst wants to report what
`occupation` is worth.  `occupation` is the expensive field here: it is the
one a survey has to ask about and code, where `age`, `sex` and `race` come
free with the sampling frame and `education` comes with the enrolment record.

The question this package exists to make hard to dodge: worth **compared with
what**, measured **how**, at **which operating point**, and with the register
**how complete**?

    python examples/worked_example.py

Writes examples/worked_example_surface.csv and examples/worked_example.png,
and prints the minimum reportable form.  The download is cached in
data/example/ and its SHA-256 is recorded, so a re-run is offline.
"""
import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fieldvalue import (SingleNumberRefused, decompose, regret,  # noqa: E402
                        robustness, surface)

CACHE = ROOT / "data" / "example"
CACHE.mkdir(parents=True, exist_ok=True)
URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
DOI = "10.24432/C5XW20"
COLS = ["age", "workclass", "fnlwgt", "education", "education_num",
        "marital_status", "occupation", "relationship", "race", "sex",
        "capital_gain", "capital_loss", "hours_per_week", "native_country",
        "income"]

FREE = ["age_band", "sex", "race", "native_country"]      # come with the frame
CHEAP = FREE + ["education"]                              # enrolment record
EXPENSIVE = "occupation"                                  # the field in question


def load():
    csv = CACHE / "adult.data"
    if not csv.exists():
        print(f"  downloading UCI Adult from {DOI} ...")
        raw = urllib.request.urlopen(URL, timeout=120).read()
        (CACHE / "adult.sha256").write_text(
            hashlib.sha256(raw).hexdigest() + "  adult.zip\n", encoding="utf-8")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            csv.write_bytes(z.read("adult.data"))
    d = pd.read_csv(csv, header=None, names=COLS, skipinitialspace=True,
                    na_values="?")
    d = d.dropna(subset=[EXPENSIVE, "education", "native_country"])
    d["age_band"] = pd.cut(d.age, [0, 25, 35, 45, 55, 65, 200],
                           labels=["<25", "25-34", "35-44", "45-54", "55-64",
                                   "65+"]).astype(str)
    d["hours_band"] = pd.cut(d.hours_per_week, [0, 20, 35, 40, 50, 200],
                             labels=["<=20", "21-35", "36-40", "41-50",
                                     ">50"]).astype(str)
    d["_y"] = (d.income.astype(str).str.strip().str.rstrip(".")
               == ">50K").astype(int)
    #  a stable, meaningless order: the file's own.  There is no timestamp
    #  here, and the package says so in its notes rather than pretending.
    return d.reset_index(drop=True)


def main():
    print("=" * 78)
    print("fieldvalue, worked on UCI Adult -- what is `occupation` worth?")
    print("=" * 78)
    d = load()
    X = d[CHEAP + ["hours_band", EXPENSIVE]]
    y = d._y.values
    print(f"  {len(d):,} rows, prevalence {y.mean():.4f}")
    print(f"  free fields    : {FREE}")
    print(f"  cheap fields   : {CHEAP}")
    print(f"  expensive field: {EXPENSIVE!r}\n")

    s = surface(
        X, y, feature=EXPENSIVE,
        baselines={"nothing": [],
                   "free": FREE,
                   "free+education": CHEAP,
                   "free+education+hours": CHEAP + ["hours_band"]},
        metrics=["auc", "ap", "brier_skill", "nagelkerke"],
        thresholds=tuple(np.round(np.arange(0.05, 0.8001, 0.05), 4)),
        population=(1.00, 0.75, 0.50, 0.25),
        regimes=("rare-first",), seed=20260819)
    s.report()

    out = Path(__file__).resolve().parent
    s.to_frame().to_csv(out / "worked_example_surface.csv", index=False)
    s.plot(path=str(out / "worked_example.png"))
    print(f"\n  surface -> {out / 'worked_example_surface.csv'}")
    print(f"  figure  -> {out / 'worked_example.png'}")

    print("\n" + "=" * 78)
    print("AND THE POINT OF THE EXERCISE")
    print("=" * 78)
    try:
        float(s)
    except SingleNumberRefused as e:
        print(e)
    F = s.to_frame()
    cell = F[(F.metric == "auc") & F.threshold.isna() & (F.population == 1.0)]
    print("\n  Every one of these is a defensible answer to "
          "'what is occupation worth?':")
    for _, r in cell.iterrows():
        print(f"    against {r.baseline_pair:34s}  R = {r.R:+.3f}")

    # ---- the four reporting objects, on the same surface ------------------
    #  The point of restoring this example is that the standard is not about
    #  event logs and not about configuration databases.  `occupation` on a
    #  census file is the same problem: worth compared with what, measured
    #  how, at which operating point, with the register how complete.
    print()
    print("=" * 78)
    print("THE MINIMUM REPORTABLE FORM, AS THE FOUR OBJECTS")
    print("=" * 78)
    G = F.rename(columns={"V_hi": "V"})
    G = G[G.V.notna()]
    dec = decompose(G, value="V",
                    axes=("baseline_pair", "metric", "population"))
    rob = robustness(G, value="V")
    reg = regret(G, value="V")
    print()
    print("  sensitivity decomposition")
    print(dec.to_string(index=False, float_format=lambda x: "%.3f" % x))
    print()
    print("  robustness")
    print(rob.to_string(index=False, float_format=lambda x: "%.3f" % x))
    print()
    print("  specification regret: a one-number report misstates the sign for "
          "a mean %.1f%% of the other admissible cells"
          % (100 * reg.misreport.mean()))

    sys.path.insert(0, str(ROOT / "scripts"))
    from common import RESULTS
    dec.to_csv(RESULTS / "s14_example_decomposition.csv", index=False)

    def _S(ax):
        r = dec[dec.axis == ax]
        return float(r.S.iloc[0]) if len(r) else float("nan")

    facts = dict(n_rows=len(d), prevalence=float(y.mean()), n_cells=len(G),
                 share_positive=float((G.V > 0).mean()),
                 misreport_mean=float(reg.misreport.mean()),
                 S_baseline=_S("baseline_pair"), S_metric=_S("metric"),
                 S_population=_S("population"),
                 R_min=float(cell.R.min()), R_max=float(cell.R.max()))
    pd.DataFrame([facts]).to_csv(RESULTS / "s14_facts.csv", index=False)
    print()
    print("  facts -> results/s14_facts.csv")


if __name__ == "__main__":
    main()

"""r43 -- THE REGISTERED PRECONDITION, FITTED AND THEN TESTED PROSPECTIVELY.

Two modes, and the separation between them is the point of the exercise.

    python r43_holdout_test.py --fit     # round-seventeen logs ONLY.
                                         # Fits the two rules' thresholds and
                                         # writes results/r43_hstar.csv.  Opens
                                         # no held-out log.  Runs BEFORE
                                         # PREDICTION.md is committed.

    python r43_holdout_test.py           # opens the held-out logs, applies
                                         # PROTOCOL.md sections 3-5 through the
                                         # SAME functions r33 uses, and scores
                                         # the frozen rules.  Runs AFTER
                                         # PREDICTION.md is committed.

WHY THE PROTOCOL CODE IS IMPORTED RATHER THAN COPIED.  A prospective test whose
analysis code is a re-implementation is not a prospective test of the same
analysis.  `assign_roles`, `targets`, `fit`, `instruments` and `boot_reduction`
are imported from r33_generic_ladder unchanged; nothing in this file redefines
any of them, and `test_holdout_uses_protocol_code()` asserts that at run time.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
import r33_generic_ladder as L
from common import RESULTS

ROOT = Path(__file__).resolve().parent.parent
SEED = 20260819
TRAIN_FRAC = L.TRAIN_FRAC

#  The held-out logs.  PROTOCOL.md section 2 records both as considered and
#  not included, for size and parsing cost.  Neither has been parsed, loaded,
#  inspected or counted by any script in this repository before this file ran.
HOLDOUT = {
    "BPIC11": ("healthcare", "Hospital_log.xes.gz"),
    "BPIC18": ("agriculture", "BPI_Challenge_2018.xes.gz"),
}


# ----------------------------------------------------------------- the rules
def norm_entropy(s):
    """PROTOCOL.md section 6.3's normalised entropy, on the OPENING value."""
    v = pd.Series(s).astype(str).value_counts(normalize=True).values
    k = len(v)
    if k < 2:
        return 0.0
    return float(-(v * np.log(v)).sum() / np.log(k))


def balanced_accuracy(pred, truth):
    pred, truth = np.asarray(pred, bool), np.asarray(truth, bool)
    tp = float((pred & truth).sum())
    fn = float((~pred & truth).sum())
    tn = float((~pred & ~truth).sum())
    fp = float((pred & ~truth).sum())
    sens = tp / (tp + fn) if (tp + fn) else np.nan
    spec = tn / (tn + fp) if (tn + fp) else np.nan
    return float(np.nanmean([sens, spec])), tp, fp, tn, fn


def fit_threshold(x, truth):
    """The smallest threshold t maximising balanced accuracy of (x > t).

    Candidates are the midpoints between consecutive sorted unique values,
    plus one below the minimum and one above the maximum.  Deterministic, and
    the tie-break is stated rather than left to argsort.
    """
    x = np.asarray(x, float)
    u = np.unique(x)
    cands = [u[0] - 1e-9] + [(u[i] + u[i + 1]) / 2 for i in range(len(u) - 1)] \
        + [u[-1] + 1e-9]
    best = None
    for t in cands:
        ba = balanced_accuracy(x > t, truth)[0]
        if best is None or ba > best[1] + 1e-12:
            best = (t, ba)
    return float(best[0]), float(best[1])


# ------------------------------------------------------------------ mode: fit
def mode_fit():
    """Round-seventeen logs only.  Writes results/r43_hstar.csv."""
    T = pd.read_csv(RESULTS / "r33b_table.csv")
    rows = []
    for (log, g), _ in T.groupby(["log", "g"]):
        d = C.load(log)
        rows.append(dict(log=log, g=g, H_g=norm_entropy(d[g]),
                         card_g=int(d[g].astype(str).nunique())))
    E = pd.DataFrame(rows)
    T = T.merge(E, on=["log", "g"], how="left", suffixes=("", "_e"))
    T["g_lift"] = T.auc_b0g - T.auc_b0

    #  Condition (i) is common to both rules and is not fitted: the entity
    #  must be resolvably worth something over the intake block, or the
    #  reduction has no denominator and cannot be resolvable by construction.
    S = T[T.entity_pays_resolved].copy()
    truth = S.reduction_resolved.values.astype(bool)
    print("=" * 92)
    print("FITTING THE PRECONDITION ON THE THIRTEEN ROUND-SEVENTEEN LOGS")
    print("=" * 92)
    print(f"  {len(T)} log-target pairs; {len(S)} have a denominator "
          f"(V(f|B0) resolvably positive); {int(truth.sum())} of those have a "
          f"resolvable reduction.")
    print(f"\n  {'log':20s} {'target':9s} {'H_g':>7s} {'g_lift':>8s} "
          f"{'R resolvable':>13s}")
    for _, r in S.iterrows():
        print(f"  {r.log:20s} {r.target:9s} {r.H_g:7.4f} {r.g_lift:8.4f} "
              f"{str(bool(r.reduction_resolved)):>13s}")

    out = {}
    for name, col in (("H_g", "H_g"), ("g_lift", "g_lift")):
        t, ba = fit_threshold(S[col].values, truth)
        b, tp, fp, tn, fn = balanced_accuracy(S[col].values > t, truth)
        out[name] = dict(threshold=t, balanced_accuracy=b,
                         tp=tp, fp=fp, tn=tn, fn=fn)
        print(f"\n  rule on {name}: threshold {t:.6f}   in-sample balanced "
              f"accuracy {b:.3f}")
        print(f"    tp={tp:.0f} fp={fp:.0f} tn={tn:.0f} fn={fn:.0f}")

    F = pd.DataFrame([dict(
        n_pairs=len(T), n_with_denominator=len(S),
        n_resolvable=int(truth.sum()),
        h_star=out["H_g"]["threshold"],
        h_star_balacc=out["H_g"]["balanced_accuracy"],
        h_star_tp=out["H_g"]["tp"], h_star_fp=out["H_g"]["fp"],
        h_star_tn=out["H_g"]["tn"], h_star_fn=out["H_g"]["fn"],
        l_star=out["g_lift"]["threshold"],
        l_star_balacc=out["g_lift"]["balanced_accuracy"],
        l_star_tp=out["g_lift"]["tp"], l_star_fp=out["g_lift"]["fp"],
        l_star_tn=out["g_lift"]["tn"], l_star_fn=out["g_lift"]["fn"],
    )])
    F.to_csv(RESULTS / "r43_hstar.csv", index=False)
    S[["log", "domain", "target", "H_g", "g_lift", "card_g",
       "entity_pays_resolved", "reduction_resolved"]].to_csv(
        RESULTS / "r43_fit_rows.csv", index=False)
    print(f"\nWrote r43_hstar.csv and r43_fit_rows.csv.  No held-out log was "
          f"opened by this run.")


# -------------------------------------------------------------- mode: predict
def test_holdout_uses_protocol_code():
    """The prospective test must run the registered code, not a copy of it."""
    import inspect
    here = Path(__file__).read_text(encoding="utf-8")
    for fn in ("assign_roles", "targets", "fit", "instruments",
               "boot_reduction"):
        assert inspect.getmodule(getattr(L, fn)) is L, fn
        assert f"\ndef {fn}(" not in here, (
            f"{fn} is redefined in r43; the prospective test would not be "
            f"running the registered analysis")


def load_holdout(key):
    """Parse a held-out log with r32's parser, cached like any other."""
    cache = ROOT / "data" / "normalized" / f"{key}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    domain, name = HOLDOUT[key]
    p = ROOT / "data" / "corpus" / name
    if not p.exists():
        p = ROOT / "data" / "raw" / name
    if not p.exists():
        raise FileNotFoundError(f"{name} -- run r42_holdout_fetch.py first")
    print(f"    parsing {key} ...", flush=True)
    t = time.time()
    d = C.parse_xes(p)
    d = d.loc[:, [c for c in d.columns if not str(c).startswith("Unnamed")]]
    d.columns = [str(c) for c in d.columns]
    for c in d.columns:
        if c.startswith("_t_"):
            continue
        if d[c].dtype == object:
            d[c] = d[c].astype(str)
    print(f"    {key}: {len(d):,} traces, {len(d.columns)} columns "
          f"({time.time() - t:.0f}s)", flush=True)
    d.to_parquet(cache, index=False)
    return d


def mode_predict(keys):
    test_holdout_uses_protocol_code()
    hs = pd.read_csv(RESULTS / "r43_hstar.csv").iloc[0]
    H_STAR, L_STAR = float(hs.h_star), float(hs.l_star)
    print("=" * 92)
    print("THE PROSPECTIVE TEST")
    print("=" * 92)
    print(f"  frozen in PREDICTION.md:  H* = {H_STAR:.6f}   "
          f"V*(g|B0) = {L_STAR:.6f}")

    lad, exc, inst = [], [], []
    for key in keys:
        domain, _ = HOLDOUT[key]
        print("=" * 92)
        print(f"{key}  ({domain})")
        try:
            d = load_holdout(key)
        except Exception as e:                              # noqa: BLE001
            print(f"  load FAILED {type(e).__name__}: {e}")
            exc.append(dict(log=key, domain=domain, code="LOAD_FAILED",
                            detail=f"{type(e).__name__}: {e}"))
            continue
        d, CAND, gsel, fsel, b0sel, code, has_time = L.assign_roles(key, d)
        n = len(d)
        if code:
            print(f"  EXCLUDED {code}   n={n:,}")
            exc.append(dict(log=key, domain=domain, code=code, detail=f"n={n}"))
            continue
        g, g_seq, g_alt, g_alt_seq = gsel
        f_reg, f_amd = fsel
        b0, layers = b0sel
        if n < L.MIN_TRACES:
            print(f"  EXCLUDED SMALL_N   n={n:,}")
            exc.append(dict(log=key, domain=domain, code="SMALL_N",
                            detail=f"n={n}"))
            continue
        print(f"  n={n:,}  g={g!r} (card {L.card(d[g])})  "
              f"f_amended={f_amd!r}  |B0|={len(b0)}")
        print(f"  B0 = {b0}")
        cut = int(n * TRAIN_FRAC)
        gset = L.ALL_G.get(key, [(g, 0, g_seq, 0.0)])
        _, y_d, _ = L.targets(d, g_seq, cut)
        TASKS = [("duration", y_d, g, g_seq, "primary")]
        for gc, gcard, gsq, _v in gset:
            yh_i, _, _ = L.targets(d, gsq, cut)
            TASKS.append(("handover", yh_i, gc, gsq,
                          "primary" if gc == g else f"g={gc}"))
        for tname, yv, gcol_t, gseq_t, grule in TASKS:
            if grule != "primary":
                continue          # the registered tie-break is the prediction
            if yv is None:
                exc.append(dict(log=key, domain=domain, code="NO_TARGET",
                                detail=tname))
                continue
            prev = float(yv.mean())
            if not (L.PREV_LO <= prev <= L.PREV_HI):
                print(f"  [{tname}] EXCLUDED NO_HEADROOM prevalence {prev:.4f}")
                exc.append(dict(log=key, domain=domain, code="NO_HEADROOM",
                                detail=f"{tname} prev={prev:.4f}"))
                continue
            dd = d.copy()
            dd["_y"] = yv
            tr, te = dd.iloc[:cut], dd.iloc[cut:]
            yte = te["_y"].values
            if len(np.unique(yte)) < 2:
                print(f"  [{tname}] EXCLUDED NO_TEST_VARIATION")
                exc.append(dict(log=key, domain=domain,
                                code="NO_TEST_VARIATION", detail=tname))
                continue
            prev_tr = float(tr["_y"].mean())
            fcol = f_amd or f_reg
            p_n0 = L.fit(tr, te, b0)
            p_n1 = L.fit(tr, te, b0 + [fcol])
            p_h0 = L.fit(tr, te, b0 + [gcol_t])
            p_h1 = L.fit(tr, te, b0 + [gcol_t, fcol])
            I = {nm: L.instruments(p, yte, prev_tr)
                 for nm, p in (("B0", p_n0), ("B0+f", p_n1),
                               ("B0+g", p_h0), ("B0+g+f", p_h1))}
            for m in I["B0"]:
                inst.append(dict(log=key, domain=domain, target=tname,
                                 instrument=m, base=I["B0"][m],
                                 with_f=I["B0+f"][m], base_g=I["B0+g"][m],
                                 with_gf=I["B0+g+f"][m]))
            vn = I["B0+f"]["auc"] - I["B0"]["auc"]
            vh = I["B0+g+f"]["auc"] - I["B0+g"]["auc"]
            rec = dict(log=key, domain=domain, target=tname, n=n,
                       n_test=len(te), prevalence=prev, f=fcol, g=gcol_t,
                       n_b0=len(b0), card_f=L.card(d[fcol]),
                       card_g=L.card(d[gcol_t]),
                       auc_b0=I["B0"]["auc"], auc_b0f=I["B0+f"]["auc"],
                       auc_b0g=I["B0+g"]["auc"], auc_b0gf=I["B0+g+f"]["auc"],
                       naive=vn, honest=vh,
                       reduction=(1 - vh / vn) if vn > 0 else np.nan)
            rec.update(L.boot_reduction(yte, p_n0, p_n1, p_h0, p_h1))
            rec["H_g"] = norm_entropy(d[gcol_t])
            rec["g_lift"] = I["B0+g"]["auc"] - I["B0"]["auc"]
            rec["entity_pays_resolved"] = bool(rec["naive_lo"] > 0)
            rec["reduction_resolved"] = bool(
                np.isfinite(rec.get("reduction_lo", np.nan))
                and rec["reduction_lo"] > 0)
            rec["pred_entropy"] = bool(rec["entity_pays_resolved"]
                                       and rec["H_g"] > H_STAR)
            rec["pred_lift"] = bool(rec["entity_pays_resolved"]
                                    and rec["g_lift"] > L_STAR)
            lad.append(rec)
            print(f"  [{tname:8s}] naive {vn:+.4f} [{rec['naive_lo']:+.4f},"
                  f"{rec['naive_hi']:+.4f}]  honest {vh:+.4f}  "
                  f"reduction {rec['reduction']:.3f} "
                  f"[{rec.get('reduction_lo', float('nan')):.3f},"
                  f"{rec.get('reduction_hi', float('nan')):.3f}]")
            print(f"            H_g={rec['H_g']:.4f}  g_lift={rec['g_lift']:+.4f}"
                  f"   predicted(entropy)={rec['pred_entropy']}  "
                  f"predicted(lift)={rec['pred_lift']}  "
                  f"observed={rec['reduction_resolved']}")

            # ---- 4.3 the tautology control, unchanged --------------------
            big = d[gcol_t].astype(str).value_counts().idxmax()
            m_big = (d[gcol_t].astype(str) == big).values
            rec["taut_largest"] = float(yv[m_big].mean())
            rec["taut_rest"] = float(yv[~m_big].mean())
            rec["tautology_predicted"] = bool(rec["taut_largest"]
                                              > rec["taut_rest"])

    LAD = pd.DataFrame(lad)
    if len(LAD):
        LAD.to_csv(RESULTS / "r43_holdout.csv", index=False)
    if inst:
        pd.DataFrame(inst).to_csv(RESULTS / "r43_holdout_instruments.csv",
                                  index=False)
    if exc:
        pd.DataFrame(exc).to_csv(RESULTS / "r43_holdout_excluded.csv",
                                 index=False)

    # ---- the confusion matrix, exactly as PREDICTION.md section 4 says ---
    conf = []
    for rule in ("pred_entropy", "pred_lift"):
        if not len(LAD):
            break
        p = LAD[rule].values.astype(bool)
        t = LAD.reduction_resolved.values.astype(bool)
        ba, tp, fp, tn, fn = balanced_accuracy(p, t)
        conf.append(dict(rule=rule, n_scored=len(LAD), tp=tp, fp=fp, tn=tn,
                         fn=fn, n_errors=int(fp + fn), balanced_accuracy=ba))
    if conf:
        CF = pd.DataFrame(conf)
        CF.to_csv(RESULTS / "r43_confusion.csv", index=False)
        print("\n" + "=" * 92)
        print("CONFUSION MATRIX ON DATA THIS PROJECT HAD NEVER OPENED")
        print("=" * 92)
        print(CF.to_string(index=False))
    print(f"\nWrote r43_holdout*.csv")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("keys", nargs="*")
    a = ap.parse_args(argv)
    if a.fit:
        mode_fit()
    else:
        mode_predict([k for k in a.keys if k in HOLDOUT] or list(HOLDOUT))


if __name__ == "__main__":
    main(sys.argv[1:])

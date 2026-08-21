"""r33 -- THE PRE-REGISTERED LADDER, APPLIED TO THE WHOLE CORPUS.

Implements PROTOCOL.md sections 3-6 verbatim.  Nothing in this file chooses
anything per log: every attribute is assigned to a role by the registered
rules, every log gets both registered targets, and every exclusion is reported
with its registered code.

    python r33_generic_ladder.py --roles-only    # section 3 only; no outcome
    python r33_generic_ladder.py                 # everything
    python r33_generic_ladder.py Sepsis BPIC19   # a subset

Outputs: results/r33_roles.csv, r33_excluded.csv, r33_ladder.csv,
         r33_instruments.csv, r33_discriminators.csv, r33_tautology.csv,
         r33_facts.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r32_corpus as C
from common import RESULTS

SEED = 20260819
N_BOOT = 2000
TRAIN_FRAC = 0.70
NAMED_T = (0.20, 0.30, 0.40, 0.50)
EPS = 1e-12

# --- PROTOCOL.md section 3 thresholds, restated as constants ---------------
MIN_CARD_F = 50          # 3.3(i)
MIN_REUSE_F = 2.0        # 3.3(ii)
MAX_CARD_B0 = 200        # 3.4
MAX_MISSING = 0.50       # 3.1
MIN_G_PRESENT = 0.50     # 3.2(iii)
MIN_TRACES = 1000        # 4.4 SMALL_N
PREV_LO, PREV_HI = 0.05, 0.95   # 4.4 NO_HEADROOM

# --- PROTOCOL.md section 10, amendment 1 (declared 2026-08-21) -------------
# The registered rule 3.3 admits any attribute reused across two traces on
# average.  On BPI Challenge 2019 that admits `case:Purchasing Document`
# (76,349 values over 251,734 traces, reuse 3.3), which is a document number
# and not a register: almost none of its values recur across the temporal
# split, so it is a coarsening of the case key rather than a maintained
# entity.  Amendment 1 adds a second, outcome-free condition -- a register's
# values must actually recur across time -- and BOTH selections are reported
# for every log.  The condition is computed from feature values and the split
# point only; no outcome is read.
MIN_TRAIN_COVERAGE = 0.50


def missing_mask(s):
    return C.is_missing(s)


def card(s):
    v = s[~missing_mask(s)]
    return int(v.nunique())


def base_name(c):
    return (c[5:] if c.startswith("case:") else c).strip().lower()


def temporal_order(d):
    if "_t_first" in d.columns and d["_t_first"].notna().any():
        return d.sort_values("_t_first", kind="stable").reset_index(drop=True), True
    return d.reset_index(drop=True), False


def train_coverage(d, col, cut):
    """Share of test-half traces whose value of `col` was seen in training.
    Uses feature values and the split point only."""
    a = d[col].astype(str)
    seen = set(a.iloc[:cut].unique())
    tail = a.iloc[cut:]
    return float(tail.isin(seen).mean()) if len(tail) else 0.0


ALL_G = {}


def assign_roles(key, d):
    """PROTOCOL.md section 3.  Reads no outcome."""
    d, has_time = temporal_order(d)
    n = len(d)
    cut = int(n * TRAIN_FRAC)
    seq_cols = {c[5:]: c for c in d.columns if c.startswith("_seq_")}

    act = d["concept:name"] if "concept:name" in d.columns else None
    cands = []
    for c in d.columns:
        if c.startswith(("_seq_", "_t_")) or c in ("n_events", "duration_h"):
            continue
        bn = base_name(c)
        if bn in C.OUTCOME_FIELDS:
            continue
        # amendment 2: section 3.1's "any timestamp", implemented
        if C.looks_like_timestamp(c, d[c]):
            continue
        miss = float(missing_mask(d[c]).mean())
        k = card(d[c])
        if k < 2 or miss > MAX_MISSING:
            continue
        # amendment 3: a relabelling of concept:name IS concept:name
        if act is not None and C.is_activity_alias(d[c], act):
            continue
        cands.append(dict(attribute=c, base=bn, cardinality=k, missing=miss,
                          reuse=(n / k) if k else np.nan,
                          resource_like=bn in C.RESOURCE_FIELDS,
                          coverage=train_coverage(d, c, cut)))
    CAND = pd.DataFrame(cands)
    if CAND.empty:
        return d, CAND, None, None, [], "NO_B0", has_time

    # --- 3.2  the free overlapping field g --------------------------------
    gcands = []
    for _, r in CAND[CAND.resource_like].iterrows():
        sc = seq_cols.get(r.base) or seq_cols.get(r.attribute)
        if sc is None:
            continue
        varies = d[sc].astype(str).map(
            lambda s: len(set(x for x in s.split("|") if x and x != "nan")) > 1)
        present = 1.0 - r.missing
        if bool(varies.any()) and present >= MIN_G_PRESENT:
            gcands.append((r.attribute, r.cardinality, sc,
                           float(varies.mean())))
    if not gcands:
        return d, CAND, None, None, [], "NO_G", has_time
    gcands.sort(key=lambda t: -t[1])
    g, g_card, g_seq, g_varies = gcands[0]
    g_alt = gcands[-1][0] if len(gcands) > 1 else None
    g_alt_seq = gcands[-1][2] if len(gcands) > 1 else None
    ALL_G[key] = gcands

    # --- 3.3  the high-cost entity f --------------------------------------
    pool = CAND[(~CAND.resource_like) & (CAND.attribute != g)
                & (CAND.cardinality >= MIN_CARD_F)
                & (CAND.reuse >= MIN_REUSE_F)]
    if pool.empty:
        return d, CAND, g, None, [], "NO_F", has_time
    f_reg = pool.sort_values("cardinality", ascending=False).iloc[0].attribute
    pool2 = pool[pool.coverage >= MIN_TRAIN_COVERAGE]
    f_amd = (pool2.sort_values("cardinality", ascending=False).iloc[0].attribute
             if not pool2.empty else None)

    # --- 3.5  the layer hierarchy (amendment 4) ---------------------------
    # Every attribute has exactly one role, and section 3.5 gives
    # deterministic coarsenings of f their own.  They are therefore NOT in
    # B0; r34 uses them for the resolution ladder.
    f_use = f_amd or f_reg
    used = {g, f_reg, f_amd}
    layers = [r.attribute for _, r in CAND.iterrows()
              if r.attribute not in used
              and r.cardinality < card(d[f_use])
              and C.is_coarsening_of(d[r.attribute], d[f_use])]

    # --- 3.4  the intake block B0 -----------------------------------------
    used = used | set(layers)
    b0 = [r.attribute for _, r in CAND.iterrows()
          if r.attribute not in used and r.cardinality <= MAX_CARD_B0]
    if not b0:
        return d, CAND, g, f_reg, [], "NO_B0", has_time
    return (d, CAND, (g, g_seq, g_alt, g_alt_seq), (f_reg, f_amd),
            (b0, layers), None, has_time)


# ------------------------------------------------------------- section 4/5
def targets(d, g_seq, cut):
    """PROTOCOL.md section 4.  Y_H from the handover count; Y_D from the
    training-half median duration."""
    seq = d[g_seq].astype(str)
    h = seq.map(lambda s: len(set(x for x in s.split("|")
                                  if x and x != "nan")) - 1)
    y_h = (h >= 1).astype(int).values
    dur = pd.to_numeric(d.get("duration_h"), errors="coerce")
    if dur is None or dur.isna().all():
        y_d = None
    else:
        med = float(dur.iloc[:cut].median())
        y_d = (dur.fillna(-1) > med).astype(int).values
    return y_h, y_d, h.values


def fit(tr, te, cols, C_=1.0):
    e = OneHotEncoder(handle_unknown="ignore")
    X = e.fit_transform(tr[cols].astype(str))
    m = LogisticRegression(max_iter=3000, C=C_).fit(X, tr["_y"].values)
    return m.predict_proba(e.transform(te[cols].astype(str)))[:, 1]


def brier_skill(p, y, p0):
    return 1.0 - float(np.mean((p - y) ** 2)) / float(np.mean((p0 - y) ** 2))


def nagelkerke(p, y, p0):
    pc = np.clip(p, EPS, 1 - EPS)
    ll_m = float((y * np.log(pc) + (1 - y) * np.log(1 - pc)).sum())
    ll_0 = float((y * np.log(p0) + (1 - y) * np.log(1 - p0)).sum())
    cs = 1.0 - np.exp((2.0 / len(y)) * (ll_0 - ll_m))
    return float(cs / (1.0 - np.exp((2.0 / len(y)) * ll_0)))


def net_benefit(p, y, t):
    a = p >= t
    return (float((a & (y == 1)).sum())
            - float((a & (y == 0)).sum()) * (t / (1 - t))) / len(y)


def instruments(p, y, prev_tr):
    p0 = float(prev_tr)
    out = dict(auc=roc_auc_score(y, p), ap=average_precision_score(y, p),
               brier_skill=brier_skill(p, y, p0),
               nagelkerke=nagelkerke(p, y, p0))
    for t in NAMED_T:
        out[f"nb_{t}"] = net_benefit(p, y, t)
    return out


def boot_reduction(y, pn0, pn1, ph0, ph1, n_boot=N_BOOT, seed=SEED):
    """Paired bootstrap on the AUC reduction.  One index set per draw, shared
    by all four models.  AUC only: PROTOCOL.md section 5 names it primary."""
    rng = np.random.default_rng(seed)
    n = len(y)
    dn, dh = [], []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        yy = y[i]
        if len(np.unique(yy)) < 2:
            continue
        dn.append(roc_auc_score(yy, pn1[i]) - roc_auc_score(yy, pn0[i]))
        dh.append(roc_auc_score(yy, ph1[i]) - roc_auc_score(yy, ph0[i]))
    dn, dh = np.array(dn), np.array(dh)
    ok = dn > 0
    red = np.full(len(dn), np.nan)
    red[ok] = 1.0 - dh[ok] / dn[ok]
    return dict(naive_lo=float(np.percentile(dn, 2.5)),
                naive_hi=float(np.percentile(dn, 97.5)),
                honest_lo=float(np.percentile(dh, 2.5)),
                honest_hi=float(np.percentile(dh, 97.5)),
                frac_denom_pos=float(ok.mean()),
                reduction_lo=float(np.nanpercentile(red, 2.5)) if ok.all() else np.nan,
                reduction_hi=float(np.nanpercentile(red, 97.5)) if ok.all() else np.nan,
                n_draws=len(dn))


def nmi(a, b):
    """Normalised mutual information, computed on the training half only."""
    a = pd.Series(a).astype(str)
    b = pd.Series(b).astype(str)
    ct = pd.crosstab(a, b).values.astype(float)
    n = ct.sum()
    if n == 0:
        return np.nan
    pxy = ct / n
    px = pxy.sum(1, keepdims=True)
    py = pxy.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = pxy * np.log(pxy / (px * py))
    mi = float(np.nansum(t))
    hx = float(-np.nansum(px * np.log(px)))
    hy = float(-np.nansum(py * np.log(py)))
    d = np.sqrt(hx * hy)
    return float(mi / d) if d > 0 else np.nan


def norm_entropy(s):
    v = pd.Series(s).astype(str).value_counts(normalize=True).values
    k = len(v)
    if k < 2:
        return 0.0
    return float(-(v * np.log(v)).sum() / np.log(k))


# =========================================================================
def main(argv):
    roles_only = "--roles-only" in argv
    keys = [a for a in argv if a in C.LOGS] or list(C.LOGS)
    t0 = time.time()
    role_rows, exc_rows, lad_rows, inst_rows, disc_rows, taut_rows = \
        [], [], [], [], [], []

    for key in keys:
        domain = C.LOGS[key][0]
        print("=" * 92)
        print(f"{key}  ({domain})")
        try:
            d = C.load(key)
        except Exception as e:                              # noqa: BLE001
            print(f"  load FAILED {type(e).__name__}: {e}")
            exc_rows.append(dict(log=key, domain=domain, code="LOAD_FAILED",
                                 detail=f"{type(e).__name__}: {e}"))
            continue
        d, CAND, gsel, fsel, b0sel, code, has_time = assign_roles(key, d)
        n = len(d)
        if code:
            print(f"  EXCLUDED {code}   n={n:,}")
            exc_rows.append(dict(log=key, domain=domain, code=code,
                                 detail=f"n={n}"))
            continue
        g, g_seq, g_alt, g_alt_seq = gsel
        f_reg, f_amd = fsel
        b0, layers = b0sel
        if n < MIN_TRACES:
            print(f"  EXCLUDED SMALL_N   n={n:,}")
            exc_rows.append(dict(log=key, domain=domain, code="SMALL_N",
                                 detail=f"n={n}"))
            continue
        print(f"  n={n:,}  g={g!r} (card {card(d[g])})  "
              f"f_registered={f_reg!r} (card {card(d[f_reg])})  "
              f"f_amended={f_amd!r}  |B0|={len(b0)}")
        print(f"  B0 = {b0}")
        print(f"  layers (deterministic coarsenings of f) = {layers}")
        for _, r in CAND.iterrows():
            role = ("g" if r.attribute == g else
                    "f_registered" if r.attribute == f_reg else
                    "f_amended" if r.attribute == f_amd else
                    "layer" if r.attribute in layers else
                    "B0" if r.attribute in b0 else "unused")
            role_rows.append(dict(log=key, domain=domain, attribute=r.attribute,
                                  role=role, cardinality=r.cardinality,
                                  missing=r.missing, reuse=r.reuse,
                                  coverage=r.coverage,
                                  resource_like=r.resource_like,
                                  g_alt=(r.attribute == g_alt)))
        if roles_only:
            continue

        cut = int(n * TRAIN_FRAC)
        # --- PROTOCOL.md section 10, amendment 8 (declared 2026-08-21) ----
        # The registered tie-break in 3.2 takes the HIGHEST-cardinality
        # resource field as g.  On most logs that is `org:resource`, an
        # individual, and "more than one PERSON touched this case" is true of
        # 96-100% of traces -- so the registered handover target is excluded
        # by the registered NO_HEADROOM rule on seven of thirteen admitted
        # logs, and the corpus loses the paper's own target.  Every
        # qualifying resource field is now run as g with Y_H rebuilt from
        # THAT field's sequence, and all of them are reported.  The
        # registered choice stays primary.  This is not a selection: nothing
        # is dropped, and the g_rule column names which field each row used.
        gset = ALL_G.get(key, [(g, 0, g_seq, 0.0)])
        _, y_d, _ = targets(d, g_seq, cut)
        TASKS = [("duration", y_d, g, g_seq, "primary")]
        for gi, (gc, gcard, gsq, _v) in enumerate(gset):
            yh_i, _, _ = targets(d, gsq, cut)
            TASKS.append((f"handover", yh_i, gc, gsq,
                          "primary" if gc == g else f"g={gc}"))
        for tname, yv, gcol_t, gseq_t, grule in TASKS:
            if yv is None:
                exc_rows.append(dict(log=key, domain=domain, code="NO_TARGET",
                                     detail=tname))
                continue
            prev = float(yv.mean())
            if not (PREV_LO <= prev <= PREV_HI):
                print(f"  [{tname}/{grule}] EXCLUDED NO_HEADROOM prevalence {prev:.3f}")
                exc_rows.append(dict(log=key, domain=domain,
                                     code="NO_HEADROOM",
                                     detail=f"{tname}/{grule} prev={prev:.4f}"))
                continue
            dd = d.copy()
            dd["_y"] = yv
            tr, te = dd.iloc[:cut], dd.iloc[cut:]
            yte = te["_y"].values
            if len(np.unique(yte)) < 2:
                print(f"  [{tname}] EXCLUDED NO_TEST_VARIATION")
                exc_rows.append(dict(log=key, domain=domain,
                                     code="NO_TEST_VARIATION", detail=tname))
                continue
            prev_tr = float(tr["_y"].mean())

            for fname, fcol in (("registered", f_reg), ("amended", f_amd)):
                if fcol is None:
                    continue
                for gname, gcol in ((grule, gcol_t),):
                    if gcol is None:
                        continue
                    try:
                        p_n0 = fit(tr, te, b0)
                        p_n1 = fit(tr, te, b0 + [fcol])
                        p_h0 = fit(tr, te, b0 + [gcol])
                        p_h1 = fit(tr, te, b0 + [gcol, fcol])
                    except Exception as e:                  # noqa: BLE001
                        print(f"  [{tname}/{fname}/{gname}] FIT FAILED "
                              f"{type(e).__name__}: {e}")
                        exc_rows.append(dict(log=key, domain=domain,
                                             code="FIT_FAILED",
                                             detail=f"{tname}/{fname}/{gname}"))
                        continue
                    I = {nm: instruments(p, yte, prev_tr)
                         for nm, p in (("B0", p_n0), ("B0+f", p_n1),
                                       ("B0+g", p_h0), ("B0+g+f", p_h1))}
                    for m in I["B0"]:
                        vn = I["B0+f"][m] - I["B0"][m]
                        vh = I["B0+g+f"][m] - I["B0+g"][m]
                        inst_rows.append(dict(
                            log=key, domain=domain, target=tname,
                            f_rule=fname, g_rule=gname, instrument=m,
                            base=I["B0"][m], with_f=I["B0+f"][m],
                            base_g=I["B0+g"][m], with_gf=I["B0+g+f"][m],
                            naive=vn, honest=vh,
                            reduction=(1 - vh / vn) if vn > 0 else np.nan))
                    vn = I["B0+f"]["auc"] - I["B0"]["auc"]
                    vh = I["B0+g+f"]["auc"] - I["B0+g"]["auc"]
                    rec = dict(log=key, domain=domain, target=tname,
                               f_rule=fname, g_rule=gname,
                               n=n, n_test=len(te), prevalence=prev,
                               f=fcol, g=gcol, n_b0=len(b0),
                               card_f=card(d[fcol]), card_g=card(d[gcol]),
                               auc_b0=I["B0"]["auc"], auc_b0f=I["B0+f"]["auc"],
                               auc_b0g=I["B0+g"]["auc"],
                               auc_b0gf=I["B0+g+f"]["auc"],
                               naive=vn, honest=vh,
                               reduction=(1 - vh / vn) if vn > 0 else np.nan,
                               primary=(fname == "amended" and gname == "primary"))
                    if rec["primary"]:
                        rec.update(boot_reduction(yte, p_n0, p_n1, p_h0, p_h1))
                    lad_rows.append(rec)
                    star = "*" if rec["primary"] else " "
                    print(f"  {star}[{tname:8s} f={fname:10s} g={gname:7s}] "
                          f"naive {vn:+.4f}  honest {vh:+.4f}  "
                          f"reduction "
                          f"{rec['reduction'] if np.isfinite(rec['reduction']) else float('nan'):>7.3f}"
                          + (f"  [{rec.get('reduction_lo', float('nan')):.3f},"
                             f"{rec.get('reduction_hi', float('nan')):.3f}]"
                             if rec["primary"] else ""))

            # ---- 4.3 the tautology control -------------------------------
            big = d[gcol_t].astype(str).value_counts().idxmax()
            m_big = d[gcol_t].astype(str) == big
            r_big, r_rest = float(yv[m_big.values].mean()), float(yv[~m_big.values].mean())
            taut_rows.append(dict(log=key, domain=domain, target=tname,
                                  g=gcol_t, g_rule=grule,
                                  largest_group=str(big)[:40],
                                  share=float(m_big.mean()),
                                  rate_largest=r_big, rate_rest=r_rest,
                                  difference=r_big - r_rest,
                                  tautology_predicted=bool(r_big > r_rest)))
            print(f"   [{tname}/{grule}] tautology control: largest opening value "
                  f"{r_big:.3f} vs rest {r_rest:.3f}  "
                  f"({'PREDICTED BY TAUTOLOGY' if r_big > r_rest else 'opposite'})")

        # ---- 6.3 discriminators, computed on the training half -----------
        f_use = f_amd or f_reg
        tr_slice = d.iloc[:cut]
        vc = d[f_use].astype(str).value_counts(normalize=True)
        top1 = float(vc.head(max(1, int(np.ceil(0.01 * len(vc))))).sum())
        disc_rows.append(dict(
            log=key, domain=domain, n=n, f=f_use, g=g,
            card_f=card(d[f_use]), card_g=card(d[g]), n_b0=len(b0),
            nmi_f_g=nmi(tr_slice[f_use], tr_slice[g]),
            entropy_f=norm_entropy(d[f_use]), top1pct_share=top1,
            g_is_stamp=bool(base_name(g) in C.RESOURCE_STAMP),
            events_mean=float(pd.to_numeric(d.n_events, errors="coerce").mean()),
            events_median=float(pd.to_numeric(d.n_events, errors="coerce").median()),
            coverage_f=train_coverage(d, f_use, cut),
            has_time=has_time))

    if role_rows:
        pd.DataFrame(role_rows).to_csv(RESULTS / "r33_roles.csv", index=False)
    if exc_rows:
        pd.DataFrame(exc_rows).to_csv(RESULTS / "r33_excluded.csv", index=False)
    if roles_only:
        print(f"\nroles only; wrote r33_roles.csv and r33_excluded.csv "
              f"({time.time() - t0:.0f}s)")
        return
    # ---- validity: does the GENERIC target reproduce the PUBLISHED one? --
    # The paper's target on BPI Challenge 2014 is the log's own
    # `# Reassignments` column.  The generic target counts distinct opening
    # groups in the activity trace.  They are not the same construction and a
    # corpus study that silently substitutes one for the other has changed
    # the question.  This prints the agreement whatever it is.
    if "BPIC14" in keys:
        try:
            d = C.load("BPIC14")
            d, _ = temporal_order(d)
            cut = int(len(d) * TRAIN_FRAC)
            gs = next(c for c in d.columns if c.startswith("_seq_"))
            y_gen, _, h = targets(d, gs, cut)
            pub = pd.to_numeric(d["# Reassignments"], errors="coerce")
            y_pub = (pub >= 1).astype(float).values
            ok = ~pd.isna(pub).values
            agree = float((y_gen[ok] == y_pub[ok]).mean())
            big = d[ "assignment group"].astype(str).value_counts().idxmax()
            mb = (d["assignment group"].astype(str) == big).values
            print(chr(10) + "=" * 92)
            print("VALIDITY: the generic target against the published one, on BPIC14")
            print("=" * 92)
            print(f"  generic  Y_H prevalence {y_gen[ok].mean():.4f}")
            print(f"  published Y_R prevalence {y_pub[ok].mean():.4f}")
            print(f"  they agree on {agree:.2%} of {int(ok.sum()):,} incidents")
            print(f"  tautology control, generic  : largest group "
                  f"{y_gen[ok & mb].mean():.3f} vs rest {y_gen[ok & ~mb].mean():.3f}")
            print(f"  tautology control, published: largest group "
                  f"{y_pub[ok & mb].mean():.3f} vs rest {y_pub[ok & ~mb].mean():.3f}")
            pd.DataFrame([dict(
                n=int(ok.sum()), prevalence_generic=float(y_gen[ok].mean()),
                prevalence_published=float(y_pub[ok].mean()), agreement=agree,
                taut_generic_largest=float(y_gen[ok & mb].mean()),
                taut_generic_rest=float(y_gen[ok & ~mb].mean()),
                taut_published_largest=float(y_pub[ok & mb].mean()),
                taut_published_rest=float(y_pub[ok & ~mb].mean()),
            )]).to_csv(RESULTS / "r33_target_validity.csv", index=False)
        except Exception as e:                              # noqa: BLE001
            print(f"  validity check failed: {type(e).__name__}: {e}")

    for rows, name in ((lad_rows, "r33_ladder.csv"),
                       (inst_rows, "r33_instruments.csv"),
                       (disc_rows, "r33_discriminators.csv"),
                       (taut_rows, "r33_tautology.csv")):
        if rows:
            pd.DataFrame(rows).to_csv(RESULTS / name, index=False)
    print(f"\nWrote r33_*.csv  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[1:])

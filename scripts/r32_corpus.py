"""r32 -- CORPUS LOADERS.

One row per trace, for every log in PROTOCOL.md section 2.  Each row carries

    case_id, t_first, t_last, n_events, duration_h
    <trace attributes, prefixed "case:">
    <first-event attributes, unprefixed>
    _seq_<resource field>   the full sequence of that field over the trace,
                            joined by "|", from which the handover target is
                            built

and nothing else.  Nothing here computes a target, fits a model or reads an
outcome; `r33_generic_ladder.py` does that, against the rules in PROTOCOL.md.

XES is parsed with `iterparse`, clearing each trace as it closes, because
BPI Challenge 2019 is a 728 MB single XML document and will not fit in memory
as a tree.

RESOURCE_FIELDS and OUTCOME_FIELDS below are the two declarations PROTOCOL.md
sections 3.2 and 3.1 say must be fixed before any ladder is fitted.  They are
in this file, and this file is committed before `r33` produces its first
result.
"""
import gzip
import re
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CORPUS = ROOT / "data" / "corpus"

# ---------------------------------------------------------------------------
# DECLARATION 1 (PROTOCOL.md section 3.2).  An attribute is resource-like if
# its name, lowercased, is in this set.  These are the XES standard extension
# names plus the four column names the three CSV logs use for the same thing.
# Nothing is added to this set after r33 has been run.
# ---------------------------------------------------------------------------
RESOURCE_FIELDS = {
    "org:resource", "org:group", "org:role",          # XES organisational ext.
    "assignment group", "assignment_group",           # BPIC14 / UCI 498
    "workgroup", "assigned_to", "opened_by",          # Helpdesk / UCI 498
    "resource", "responsible",                        # Helpdesk
}

# A resource STAMP names a person or a machine account; a resource
# CLASSIFICATION names a team or a role.  PROTOCOL.md section 6.3 uses the
# distinction as a discriminator, so it is declared here rather than inferred.
RESOURCE_STAMP = {"org:resource", "assigned_to", "opened_by", "resource",
                  "responsible"}

# ---------------------------------------------------------------------------
# DECLARATION 2 (PROTOCOL.md section 3.1).  Attributes that are outcomes, or
# are determined only at closure, and may never enter a feature set.  Matched
# case-insensitively against the attribute name with the "case:" prefix
# stripped.  Where a name is ambiguous it is listed: a feature wrongly
# excluded costs power, a feature wrongly admitted costs the result.
# ---------------------------------------------------------------------------
OUTCOME_FIELDS = {
    # generic
    "lifecycle:transition", "concept:name", "time:timestamp",
    # BPIC 2013 / ITSM closure
    "resolution", "closure code", "closed_code", "close time", "closure_code",
    "sla", "made_sla", "sla_breach", "resolved_by", "resolved_at", "closed_at",
    "reassignment_count", "reopen_count", "# reassignments", "handle time",
    "handle time (hours)", "handle time (secs)", "sys_mod_count",
    "incident_state", "active", "status", "state",
    # BPIC 2015 / 2020 terminal fields
    "case:last_phase", "last_phase", "endstate", "end_state",
    # BPIC 2019 / procurement terminal fields
    "case:goods receipt", "cumulative net worth (eur)",
    # BPIC 2012 / 2017 terminal fields
    "accepted", "selected", "case:selected", "case:accepted",
    # Sepsis / billing terminal fields
    "dischargereason", "closecode", "isclosed", "iscancelled",
}

_ATTR_TAGS = {"string", "date", "int", "float", "boolean", "id"}


def _strip_ns(tag):
    return tag.rsplit("}", 1)[-1]


def parse_xes(path, max_traces=None, progress_every=50000):
    """One row per trace.  Streaming; memory is bounded by one trace."""
    opener = gzip.open if str(path).endswith(".gz") else open
    rows, seqs = [], []
    t0 = time.time()
    with opener(path, "rb") as fh:
        trace_attrs, events = {}, []
        in_trace = False
        cur_event = None
        depth_event = 0
        for ev, el in ET.iterparse(fh, events=("start", "end")):
            tag = _strip_ns(el.tag)
            if ev == "start":
                if tag == "trace":
                    in_trace, trace_attrs, events = True, {}, []
                elif tag == "event" and in_trace:
                    cur_event, depth_event = {}, 1
            elif ev == "end":
                if tag in _ATTR_TAGS and in_trace:
                    k = el.get("key")
                    v = el.get("value")
                    if k is not None:
                        if cur_event is not None and depth_event:
                            cur_event.setdefault(k, v)
                        else:
                            trace_attrs.setdefault(k, v)
                elif tag == "event" and in_trace:
                    events.append(cur_event or {})
                    cur_event, depth_event = None, 0
                    el.clear()
                elif tag == "trace":
                    rows.append((dict(trace_attrs), events))
                    in_trace = False
                    el.clear()
                    if len(rows) % progress_every == 0:
                        print(f"      {len(rows):,} traces "
                              f"({time.time() - t0:.0f}s)", flush=True)
                    if max_traces and len(rows) >= max_traces:
                        break
    return _to_frame(rows)


def _to_frame(rows):
    out = []
    for tattrs, events in rows:
        rec = {f"case:{k}": v for k, v in tattrs.items()}
        rec["n_events"] = len(events)
        if events:
            for k, v in events[0].items():
                rec[k] = v
            ts = [e.get("time:timestamp") for e in events
                  if e.get("time:timestamp")]
            rec["_t_first"] = ts[0] if ts else None
            rec["_t_last"] = ts[-1] if ts else None
            for rf in RESOURCE_FIELDS:
                vals = [e.get(rf) for e in events if e.get(rf) is not None]
                if vals:
                    rec[f"_seq_{rf}"] = "|".join(vals)
        out.append(rec)
    d = pd.DataFrame(out)
    for c in ("_t_first", "_t_last"):
        if c in d.columns:
            d[c] = pd.to_datetime(d[c], errors="coerce", utc=True, format="mixed")
    if "_t_first" in d.columns and "_t_last" in d.columns:
        d["duration_h"] = (d._t_last - d._t_first).dt.total_seconds() / 3600.0
    return d


# ---------------------------------------------------------------------------
# CSV / zip logs.  Each returns the same shape as parse_xes.
# ---------------------------------------------------------------------------
def load_bpic14_corpus():
    """Rabobank, assembled from the incident table and the activity table.

    This is the SAME cohort construction as r4_final for the fields it shares,
    but the target here is the generic handover target, not the log's own
    `# Reassignments` column.  r33 reports both and their agreement.
    """
    inc = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                      encoding="latin-1")
    inc = inc.loc[:, [c for c in inc.columns if not c.startswith("Unnamed")]]
    inc.columns = [c.strip() for c in inc.columns]
    act = pd.read_csv(RAW / "Detail_Incident_Activity.csv", sep=";",
                      low_memory=False, encoding="latin-1")
    act.columns = [c.strip() for c in act.columns]
    act["ts"] = pd.to_datetime(act["DateStamp"], format="%d-%m-%Y %H:%M:%S",
                               errors="coerce", dayfirst=True)
    act = act.sort_values("ts")
    g = act.groupby("Incident ID")
    seq = g["Assignment Group"].apply(lambda s: "|".join(s.dropna().astype(str)))
    first = g.first()
    last = g.last()

    d = inc.copy()
    d["_t_first"] = pd.to_datetime(d["Open Time"], format="%d/%m/%Y %H:%M:%S",
                                   errors="coerce", dayfirst=True)
    d["_t_last"] = d["Incident ID"].map(last["ts"])
    d["n_events"] = d["Incident ID"].map(g.size())
    d["_seq_assignment group"] = d["Incident ID"].map(seq)
    d["assignment group"] = d["Incident ID"].map(first["Assignment Group"])
    d["KM number"] = d["Incident ID"].map(first["KM number"])
    d["case_id"] = d["Incident ID"]
    d["duration_h"] = (d._t_last - d._t_first).dt.total_seconds() / 3600.0
    d = d.dropna(subset=["_t_first"])
    return d


def load_uci_corpus():
    z = RAW / "incident_event_log.zip"
    with zipfile.ZipFile(z) as zf:
        df = pd.read_csv(zf.open("incident_event_log.csv"), low_memory=False)
    df["sys_mod_count"] = pd.to_numeric(df["sys_mod_count"], errors="coerce")
    df["_ts"] = pd.to_datetime(df["sys_updated_at"], format="%d/%m/%Y %H:%M",
                               errors="coerce")
    df = df.sort_values(["number", "sys_mod_count"])
    g = df.groupby("number")
    first = g.first()
    d = first.reset_index().rename(columns={"number": "case_id"})
    d["n_events"] = d.case_id.map(g.size())
    d["_seq_assignment_group"] = d.case_id.map(
        g["assignment_group"].apply(lambda s: "|".join(s.dropna().astype(str))))
    d["_seq_assigned_to"] = d.case_id.map(
        g["assigned_to"].apply(lambda s: "|".join(s.dropna().astype(str))))
    d["_t_first"] = pd.to_datetime(d["opened_at"], format="%d/%m/%Y %H:%M",
                                   errors="coerce")
    d["_t_last"] = d.case_id.map(g["_ts"].max())
    d["duration_h"] = (d._t_last - d._t_first).dt.total_seconds() / 3600.0
    return d.dropna(subset=["_t_first"])


def load_helpdesk_corpus():
    d = pd.read_csv(CORPUS / "finale.csv", low_memory=False)
    d.columns = [c.strip() for c in d.columns]
    cid = next(c for c in d.columns
               if c.lower() in ("case id", "case_id", "caseid", "case"))
    tsc = next(c for c in d.columns
               if "complete" in c.lower() or "timestamp" in c.lower())
    d["_ts"] = pd.to_datetime(d[tsc], errors="coerce", dayfirst=True,
                              format="mixed")
    d = d.sort_values([cid, "_ts"])
    g = d.groupby(cid)
    out = g.first().reset_index().rename(columns={cid: "case_id"})
    out["n_events"] = out.case_id.map(g.size())
    out["_t_first"] = out.case_id.map(g["_ts"].min())
    out["_t_last"] = out.case_id.map(g["_ts"].max())
    out["duration_h"] = (out._t_last - out._t_first).dt.total_seconds() / 3600.0
    for rf in RESOURCE_FIELDS:
        col = next((c for c in d.columns if c.lower() == rf), None)
        if col is not None:
            out[f"_seq_{rf}"] = out.case_id.map(
                g[col].apply(lambda s: "|".join(s.dropna().astype(str))))
    return out.dropna(subset=["_t_first"])


# ---------------------------------------------------------------------------
# the registry
# ---------------------------------------------------------------------------
def _xes(name, **kw):
    def f():
        p = CORPUS / name
        if not p.exists():
            p = RAW / name
        return parse_xes(p, **kw)
    return f


LOGS = {
    # key                domain          loader
    "BPIC14":            ("itsm",        load_bpic14_corpus),
    "UCI498":            ("itsm",        load_uci_corpus),
    "Helpdesk":          ("itsm",        load_helpdesk_corpus),
    "BPIC13_incidents":  ("itsm",        _xes("BPI_Challenge_2013_incidents.xes.gz")),
    "BPIC13_open":       ("itsm",        _xes("BPI_Challenge_2013_open_problems.xes.gz")),
    "BPIC13_closed":     ("itsm",        _xes("BPI_Challenge_2013_closed_problems.xes.gz")),
    "BPIC12":            ("lending",     _xes("BPI_Challenge_2012.xes.gz")),
    "BPIC17":            ("lending",     _xes("BPI Challenge 2017.xes.gz")),
    "BPIC19":            ("procurement", _xes("BPI_Challenge_2019.xes")),
    "BPIC15_1":          ("permitting",  _xes("BPIC15_1.xes")),
    "BPIC15_2":          ("permitting",  _xes("BPIC15_2.xes")),
    "BPIC15_3":          ("permitting",  _xes("BPIC15_3.xes")),
    "BPIC15_4":          ("permitting",  _xes("BPIC15_4.xes")),
    "BPIC15_5":          ("permitting",  _xes("BPIC15_5.xes")),
    "BPIC20_domestic":   ("expenses",    _xes("DomesticDeclarations.xes.gz")),
    "BPIC20_intl":       ("expenses",    _xes("InternationalDeclarations.xes.gz")),
    "BPIC20_prepaid":    ("expenses",    _xes("PrepaidTravelCost.xes.gz")),
    "BPIC20_permit":     ("expenses",    _xes("PermitLog.xes.gz")),
    "BPIC20_rfp":        ("expenses",    _xes("RequestForPayment.xes.gz")),
    "Sepsis":            ("healthcare",  _xes("Sepsis Cases - Event Log.xes.gz")),
    "HospitalBilling":   ("healthcare",  _xes("Hospital Billing - Event Log.xes.gz")),
    "RoadFines":         ("enforcement", _xes("Road_Traffic_Fine_Management_Process.xes.gz")),
}

_CACHE = ROOT / "data" / "normalized"
_CACHE.mkdir(parents=True, exist_ok=True)


def load(key, use_cache=True):
    """One row per trace, cached as parquet so r33/r34/r36/r37 pay the parse
    cost once.  The cache is keyed by file name only; delete data/normalized
    to force a re-parse."""
    p = _CACHE / f"{key}.parquet"
    if use_cache and p.exists():
        return pd.read_parquet(p)
    domain, loader = LOGS[key]
    print(f"    parsing {key} ...", flush=True)
    t = time.time()
    d = loader()
    d = d.loc[:, [c for c in d.columns if not str(c).startswith("Unnamed")]]
    d.columns = [str(c) for c in d.columns]
    for c in d.columns:
        if c.startswith("_t_"):
            continue
        if d[c].dtype == object:
            d[c] = d[c].astype(str)
    print(f"    {key}: {len(d):,} traces, {len(d.columns)} columns "
          f"({time.time() - t:.0f}s)", flush=True)
    if use_cache:
        d.to_parquet(p, index=False)
    return d


# ---------------------------------------------------------------------------
# inventory -- names and cardinalities only.  No outcome is read.
# ---------------------------------------------------------------------------
MISSING = {"", "?", "nan", "none", "null", "na", "n/a", "-", "#n/b", "unknown",
           "nat", "<na>"}


def is_missing(s):
    v = s.astype(str).str.strip().str.lower()
    return v.isin(MISSING) | s.isna()


def inventory(key, d):
    rows = []
    n = len(d)
    for c in d.columns:
        if c.startswith(("_seq_", "_t_")) or c in ("n_events", "duration_h"):
            continue
        s = d[c]
        miss = float(is_missing(s).mean())
        vals = s[~is_missing(s)]
        card = int(vals.nunique())
        base = c[5:] if c.startswith("case:") else c
        rows.append(dict(log=key, attribute=c, cardinality=card,
                         missing_rate=miss, n=n,
                         reuse=(n / card) if card else np.nan,
                         resource_like=base.strip().lower() in RESOURCE_FIELDS,
                         outcome_listed=base.strip().lower() in OUTCOME_FIELDS,
                         example=str(vals.iloc[0])[:40] if len(vals) else ""))
    return pd.DataFrame(rows)


def main(argv):
    keys = [a for a in argv if a in LOGS] or list(LOGS)
    inv = []
    for k in keys:
        try:
            d = load(k)
            inv.append(inventory(k, d))
            seqs = [c for c in d.columns if c.startswith("_seq_")]
            print(f"      resource sequences present: {seqs}")
        except Exception as e:                              # noqa: BLE001
            print(f"    {k}: FAILED {type(e).__name__}: {e}")
    if inv:
        INV = pd.concat(inv, ignore_index=True)
        INV.to_csv(RESULTS / "r32_inventory.csv", index=False)
        print(f"\nWrote r32_inventory.csv: {len(INV)} attributes over "
              f"{INV.log.nunique()} logs")


if __name__ == "__main__":
    main(sys.argv[1:])

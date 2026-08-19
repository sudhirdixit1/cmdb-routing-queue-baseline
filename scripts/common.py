"""Shared loaders for the three ITSM instances.

Each loader returns one row per incident at terminal state, plus a FIELD_CLASS
map assigning every field to a semantic class:

  intake        mandatory on the intake form / always captured at creation
  descriptive   free-ish classification added by an agent
  workflow      routing / ownership / state
  configuration reference to a configuration item (the CMDB link)
  relational    reference to another record (change, problem, cause, interaction)
  outcome       resolution / SLA / timing (targets, not features)
"""
import gzip
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
NORM = ROOT / "data" / "normalized"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
for d in (RAW, NORM, RESULTS, FIGURES):
    d.mkdir(parents=True, exist_ok=True)

MISSING_TOKENS = {"", "?", "nan", "none", "null", "na", "n/a", "-", "#n/b", "unknown"}


def is_missing(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    return s.isin(MISSING_TOKENS) | series.isna()


def population_rate(series: pd.Series) -> float:
    return float(1.0 - is_missing(series).mean())


def entropy(series: pd.Series) -> float:
    s = series[~is_missing(series)]
    if len(s) == 0:
        return 0.0
    p = s.value_counts(normalize=True).values
    return float(-(p * np.log2(p)).sum())


# --------------------------------------------------------------------------
# 1. UCI 498 -- anonymised IT company, ServiceNow
# --------------------------------------------------------------------------
UCI_CLASS = {
    "category": "intake", "subcategory": "intake", "location": "intake",
    "contact_type": "intake", "impact": "intake", "urgency": "intake",
    "priority": "intake", "opened_by": "intake", "caller_id": "intake",
    "u_symptom": "descriptive", "knowledge": "descriptive",
    "u_priority_confirmation": "descriptive", "notify": "descriptive",
    "assignment_group": "workflow", "assigned_to": "workflow",
    "incident_state": "workflow", "active": "workflow",
    "cmdb_ci": "configuration",
    "problem_id": "relational", "rfc": "relational", "caused_by": "relational",
    "vendor": "relational",
    "made_sla": "outcome", "closed_code": "outcome", "resolved_by": "outcome",
    "reassignment_count": "outcome", "reopen_count": "outcome",
}


def load_uci(state: str = "terminal") -> pd.DataFrame:
    """state='terminal' -> last observed row per incident (outcomes).
    state='first'      -> earliest observed row per incident (creation-time
                          features), with terminal outcome columns attached."""
    zpath = RAW / "incident_event_log.zip"
    if not zpath.exists():  # fall back to the earlier download location
        alt = RAW.parent.parent.parent / "inc.zip"
        zpath = alt if alt.exists() else zpath
    with zipfile.ZipFile(zpath) as z:
        df = pd.read_csv(z.open("incident_event_log.csv"), low_memory=False)
    df["sys_mod_count"] = pd.to_numeric(df["sys_mod_count"], errors="coerce")
    df = df.sort_values(["number", "sys_mod_count"])
    last = df.groupby("number", as_index=False).last()
    inc = df.groupby("number", as_index=False).first() if state == "first" else last

    # outcomes always come from the terminal state
    term = last.set_index("number")
    inc = inc.set_index("number")
    inc["reassignment_count"] = pd.to_numeric(term["reassignment_count"],
                                              errors="coerce")
    inc["reopen_count"] = pd.to_numeric(term["reopen_count"], errors="coerce")
    inc["made_sla"] = term["made_sla"]
    inc["sla_breach"] = (term["made_sla"].astype(str).str.lower() == "false").astype(int)
    inc = inc.reset_index()

    inc["opened_at"] = pd.to_datetime(inc["opened_at"], format="%d/%m/%Y %H:%M",
                                      errors="coerce")
    inc["org"] = "ServiceNow-IT"
    return inc


# --------------------------------------------------------------------------
# 2. BPIC 2013 -- Volvo IT, VINST
# --------------------------------------------------------------------------
BPIC13_CLASS = {
    "impact": "intake", "product": "intake",
    "organization involved": "descriptive", "organization country": "descriptive",
    "resource country": "descriptive",
    "org:group": "workflow", "org:resource": "workflow", "org:role": "workflow",
    "concept:name": "outcome",
}


def load_bpic13(state: str = "terminal") -> pd.DataFrame:
    """state='first' takes attributes from the FIRST event of each trace, so
    features cannot encode anything that happened after the incident was
    logged.  The reassignment target is always derived from the whole trace."""
    raw = gzip.open(RAW / "BPI_Challenge_2013_incidents.xes.gz", "rt",
                    encoding="utf-8", errors="replace").read()
    traces = re.findall(r"<trace>(.*?)</trace>", raw, flags=re.S)
    idx = 0 if state == "first" else -1
    rows = []
    for t in traces:
        rec = {}
        head = t.split("<event>")[0]
        for k, v in re.findall(r'key="([^"]+)"\s+value="([^"]*)"', head):
            rec[k] = v
        events = re.findall(r"<event>(.*?)</event>", t, flags=re.S)
        rec["n_events"] = len(events)
        if events:
            for k, v in re.findall(r'key="([^"]+)"\s+value="([^"]*)"', events[idx]):
                rec[k] = v
            groups = re.findall(r'key="org:group"\s+value="([^"]*)"', t)
            rec["n_groups"] = len(set(groups))
            rec["reassignment_count"] = max(0, len(set(groups)) - 1)
            ts = re.findall(r'key="time:timestamp"\s+value="([^"]*)"', t)
            if ts:
                rec["opened_at"] = pd.to_datetime(ts[0], errors="coerce", utc=True)
        rows.append(rec)
    inc = pd.DataFrame(rows)
    inc["org"] = "VolvoIT"
    return inc


# --------------------------------------------------------------------------
# 3. BPIC 2014 -- Rabobank NL Group ICT, HP Service Manager
# --------------------------------------------------------------------------
BPIC14_CLASS = {
    "Category": "intake", "Impact": "intake", "Urgency": "intake",
    "Priority": "intake",
    "Alert Status": "descriptive", "KM number": "descriptive",
    "Status": "workflow", "Service Component WBS (aff)": "workflow",
    "CI Name (aff)": "configuration", "CI Type (aff)": "configuration",
    "CI Subtype (aff)": "configuration",
    "CI Name (CBy)": "relational", "CI Type (CBy)": "relational",
    "Related Change": "relational", "Related Interaction": "relational",
    "# Related Changes": "relational", "# Related Incidents": "relational",
    "Closure Code": "outcome", "Handle Time (Hours)": "outcome",
    "# Reassignments": "outcome",
}


def load_bpic14() -> pd.DataFrame:
    inc = pd.read_csv(RAW / "Detail_Incident.csv", sep=";", low_memory=False,
                      encoding="latin-1")
    inc = inc.loc[:, [c for c in inc.columns if not c.startswith("Unnamed")]]
    inc.columns = [c.strip() for c in inc.columns]
    inc["opened_at"] = pd.to_datetime(inc["Open Time"], format="%d/%m/%Y %H:%M:%S",
                                      errors="coerce", dayfirst=True)
    inc["reassignment_count"] = pd.to_numeric(inc["# Reassignments"], errors="coerce")
    inc["org"] = "Rabobank"
    return inc


LOADERS = {
    "ServiceNow-IT": (load_uci, UCI_CLASS),
    "VolvoIT": (load_bpic13, BPIC13_CLASS),
    "Rabobank": (load_bpic14, BPIC14_CLASS),
}

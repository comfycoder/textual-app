"""Shared data store for the Search → Grid → Edit feature.

Both screen.py (SearchGridDemoScreen) and edit.py (EditJobScreen) import
from here.  _RECORDS and _RECORD_BY_ID are the live in-memory store;
EditJobScreen mutates individual dicts in-place via dict.update(), so
SearchGridDemoScreen always sees the latest values on resume.
"""

from __future__ import annotations

import random
from typing import Any

# ── Select-widget option lists ────────────────────────────────────────────────

_STATUS_OPTS   = [("Queued","queued"),("Running","running"),("Done","done"),
                  ("Failed","failed"),("Pending","pending")]
_TYPE_OPTS     = [("Training","training"),("Validation","validation"),
                  ("Export","export"),("Inference","inference"),
                  ("Preprocessing","preprocessing")]
_PRIORITY_OPTS = [("Low","low"),("Medium","medium"),
                  ("High","high"),("Critical","critical")]
_TENANT_OPTS   = [("JHU","jhu"),("UNC","unc"),("Mayo","mayo"),("Stanford","stanford")]
_ENV_OPTS      = [("Production","prod"),("Staging","staging"),("Development","dev")]

# ── Display colour maps ───────────────────────────────────────────────────────

_STATUS_COLORS = {
    "queued": "yellow", "running": "cyan", "done": "green",
    "failed": "red",    "pending": "dim",
}
_PRI_COLORS = {
    "low": "dim", "medium": "yellow", "high": "red", "critical": "bold red",
}

# ── Record generation ─────────────────────────────────────────────────────────

_SUBMITTERS = [
    "alice@jhu.edu", "bob@unc.edu", "carol@mayo.org",
    "dave@stanford.edu", "eve@jhu.edu",
]
_TAGS_POOL = [
    "baseline", "nightly", "ablation", "prod",
    "dev", "manual", "scheduled", "experiment",
]

random.seed(42)

_RECORDS: list[dict[str, Any]] = [
    {
        "id":           f"wi-{i:03d}",
        "tenant":       random.choice([v for _, v in _TENANT_OPTS]),
        "type":         random.choice([v for _, v in _TYPE_OPTS]),
        "status":       random.choice([v for _, v in _STATUS_OPTS]),
        "priority":     random.choice([v for _, v in _PRIORITY_OPTS]),
        "environment":  random.choice([v for _, v in _ENV_OPTS]),
        "submitted_by": random.choice(_SUBMITTERS),
        "node":         f"gpu-node-{random.randint(1, 8):02d}",
        "max_jobs":     str(random.randint(1, 8)),
        "timeout_min":  str(random.randint(10, 120)),
        "gpu_required": random.choice([True, False]),
        "auto_retry":   random.choice([True, False]),
        "tags":         ", ".join(random.sample(_TAGS_POOL, random.randint(0, 3))),
        "notes":        random.choice([
            "Baseline run", "Nightly batch", "Ablation study",
            "Prod deployment", "", "",
        ]),
        "description":  random.choice([
            "Full training run.", "Validate checkpoint.",
            "Export to ONNX.", "", "", "",
        ]),
    }
    for i in range(1, 201)
]

_RECORD_BY_ID: dict[str, dict[str, Any]] = {r["id"]: r for r in _RECORDS}

# ── Grid display settings ─────────────────────────────────────────────────────

_PAGE_SIZE_OPTS    = [("10", 10), ("20", 20), ("50", 50), ("100", 100)]
_DEFAULT_PAGE_SIZE = 10

# (header label, record field key, fixed width or None for auto)
# Fixed widths on "Submitted by" and "Tags" allow those cells to wrap.
_SG_COLUMNS: list[tuple[str, str, int | None]] = [
    ("ID",           "id",           None),
    ("Tenant",       "tenant",       None),
    ("Type",         "type",         None),
    ("Status",       "status",       None),
    ("Priority",     "priority",     None),
    ("Env",          "environment",  None),
    ("Submitted by", "submitted_by", 20),
    ("Tags",         "tags",         22),
]

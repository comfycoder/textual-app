"""5 000 deterministic work-item rows for the large-dataset DataTable demo.

Generated once at import time with a fixed seed so the data is consistent
across runs.  Each row is a plain dict — no Rich markup — so add_row() is
fast even for thousands of calls.
"""

from __future__ import annotations

import random

_RNG = random.Random(99)

_TYPES     = ["training", "validation", "export", "inference", "preprocessing"]
_STATUSES  = ["done"] * 8 + ["failed"] * 2 + ["running"] * 3 + ["queued"] * 2 + ["pending"]
_PRIORITIES = ["low", "medium", "high", "critical"]
_TENANTS   = ["jhu", "unc", "mayo", "stanford"]

#: 5 000 rows — the full dataset rendered by the screen.
ROWS: list[dict[str, str]] = [
    {
        "id":       f"wi-{i:05d}",
        "type":     _RNG.choice(_TYPES),
        "status":   _RNG.choice(_STATUSES),
        "priority": _RNG.choice(_PRIORITIES),
        "tenant":   _RNG.choice(_TENANTS),
    }
    for i in range(1, 5_001)
]

#: Column specs used by the screen: (header label, dict key, fixed width).
COLUMNS: list[tuple[str, str, int]] = [
    ("Work Item",  "id",       12),
    ("Type",       "type",     14),
    ("Status",     "status",   10),
    ("Priority",   "priority", 10),
    ("Tenant",     "tenant",   10),
]

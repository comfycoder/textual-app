"""Shared colour maps for status and priority values.

Import these instead of re-declaring local dicts in each feature screen.
"""

STATUS_COLORS: dict[str, str] = {
    "queued":  "yellow",
    "running": "cyan",
    "done":    "green",
    "failed":  "red",
    "pending": "dim",
}

PRI_COLORS: dict[str, str] = {
    "low":      "dim",
    "medium":   "yellow",
    "high":     "red",
    "critical": "bold red",
}

# Used by master_detail — step-level statuses differ slightly from job-level.
STEP_STATUS_COLORS: dict[str, str] = {
    "pending": "dim",
    "running": "cyan",
    "done":    "green",
    "failed":  "red",
    "skipped": "yellow",
}

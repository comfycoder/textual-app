"""Demo: Master / Detail — selecting a row in one table populates a child table."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from typing import Any

from textual.widgets import DataTable, Footer, Header, Static

from your_cli.tui.palette import STATUS_COLORS, STEP_STATUS_COLORS
_TYPES   = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS = ["jhu", "unc", "mayo"]
_STEPS = {
    "training":      ["data-load", "tokenize", "train-epoch", "validate", "checkpoint", "cleanup"],
    "validation":    ["data-load", "validate", "score", "report"],
    "export":        ["load-model", "convert", "quantize", "package", "upload"],
    "inference":     ["data-load", "preprocess", "infer", "postprocess", "write-results"],
    "preprocessing": ["ingest", "clean", "split", "transform", "save"],
}

random.seed(17)

def _make_jobs() -> list[dict[str, Any]]:
    jobs = []
    for i in range(1, 26):
        job_type = random.choice(_TYPES)
        status   = random.choice(list(STATUS_COLORS))
        steps    = _STEPS[job_type]
        # Determine how many steps completed based on status
        if status == "done":
            done_up_to = len(steps)
        elif status == "running":
            done_up_to = random.randint(1, len(steps) - 1)
        elif status == "failed":
            done_up_to = random.randint(0, len(steps) - 1)
        else:
            done_up_to = 0

        step_records = []
        for j, name in enumerate(steps):
            if j < done_up_to:
                s = "done"
                dur = f"{random.randint(2, 120)}s"
                msg = "OK"
            elif j == done_up_to and status == "running":
                s = "running"
                dur = "…"
                msg = "in progress"
            elif j == done_up_to and status == "failed":
                s = "failed"
                dur = f"{random.randint(1, 30)}s"
                msg = random.choice(["OOM", "timeout", "assertion error", "connection refused"])
            else:
                s = "pending"
                dur = "—"
                msg = "waiting"
            step_records.append({
                "step":     j + 1,
                "name":     name,
                "status":   s,
                "duration": dur,
                "message":  msg,
            })

        jobs.append({
            "id":       f"wi-{i:03d}",
            "type":     job_type,
            "tenant":   random.choice(_TENANTS),
            "status":   status,
            "steps":    step_records,
            "duration": f"{random.randint(0,59):02d}m {random.randint(0,59):02d}s",
            "node":     f"gpu-node-{random.randint(1,8):02d}",
        })
    return jobs


_JOBS = _make_jobs()
_JOB_BY_ID = {j["id"]: j for j in _JOBS}


class MasterDetailDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("[",      "narrow_master",  "Narrow"),
        Binding("]",      "widen_master",   "Widen"),
    ]

    master_width: reactive[int] = reactive(45)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="md-body"):
            with Vertical(id="md-master"):
                yield Static("[b]Jobs[/b]  [dim]↑↓ navigate · Enter to pin selection[/dim]", id="md-master-title")
                yield DataTable(id="md-master-table", cursor_type="row")
            with Vertical(id="md-detail"):
                yield Static("Select a job to see its steps.", id="md-detail-header")
                yield DataTable(id="md-detail-table", cursor_type="row", show_cursor=False)
        yield Footer()

    def on_mount(self) -> None:
        master = self.query_one("#md-master-table", DataTable)
        master.add_columns("ID", "Type", "Tenant", "Status", "Duration", "Node")
        for job in _JOBS:
            color = STATUS_COLORS.get(job["status"], "white")
            master.add_row(
                job["id"],
                job["type"],
                job["tenant"],
                f"[{color}]{job['status']}[/{color}]",
                job["duration"],
                job["node"],
                key=job["id"],
            )

        detail = self.query_one("#md-detail-table", DataTable)
        detail.add_columns("#", "Step", "Status", "Duration", "Message")

        self.watch_master_width(self.master_width)
        master.focus()
        self._load_detail(_JOBS[0]["id"])

    def watch_master_width(self, width: int) -> None:
        self.query_one("#md-master").styles.width = f"{width}%"

    def action_narrow_master(self) -> None:
        self.master_width = max(20, self.master_width - 5)

    def action_widen_master(self) -> None:
        self.master_width = min(75, self.master_width + 5)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "md-master-table" and event.row_key:
            self._load_detail(str(event.row_key.value))

    def _load_detail(self, job_id: str) -> None:
        job = _JOB_BY_ID.get(job_id)
        if not job:
            return

        color = STATUS_COLORS.get(job["status"], "white")
        self.query_one("#md-detail-header", Static).update(
            f"[b]{job['id']}[/b]  ·  {job['type']}  ·  {job['tenant']}"
            f"  ·  [{color}]{job['status']}[/{color}]"
            f"  ·  {job['duration']}  ·  {job['node']}"
        )

        detail = self.query_one("#md-detail-table", DataTable)
        detail.clear()
        for step in job["steps"]:
            sc = STEP_STATUS_COLORS.get(step["status"], "white")
            detail.add_row(
                str(step["step"]),
                step["name"],
                f"[{sc}]{step['status']}[/{sc}]",
                step["duration"],
                f"[dim]{step['message']}[/dim]",
            )


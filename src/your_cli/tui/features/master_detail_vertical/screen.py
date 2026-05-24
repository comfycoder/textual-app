"""Demo: Master / Detail (vertical) — master table above, child table below."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import Screen
from typing import Any

from textual.widgets import DataTable, Footer, Header, Static

_STATUS_COLORS = {
    "queued": "yellow", "running": "cyan", "done": "green",
    "failed": "red",    "pending": "dim",
}
_STEP_STATUS_COLORS = {
    "pending": "dim", "running": "cyan", "done": "green",
    "failed": "red",  "skipped": "yellow",
}
_TYPES   = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS = ["jhu", "unc", "mayo"]
_STEPS = {
    "training":      ["data-load", "tokenize", "train-epoch", "validate", "checkpoint", "cleanup"],
    "validation":    ["data-load", "validate", "score", "report"],
    "export":        ["load-model", "convert", "quantize", "package", "upload"],
    "inference":     ["data-load", "preprocess", "infer", "postprocess", "write-results"],
    "preprocessing": ["ingest", "clean", "split", "transform", "save"],
}

random.seed(31)


def _make_jobs() -> list[dict[str, Any]]:
    jobs = []
    for i in range(1, 21):
        job_type = random.choice(_TYPES)
        status   = random.choice(list(_STATUS_COLORS))
        steps    = _STEPS[job_type]
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
                s, dur, msg = "done", f"{random.randint(2, 120)}s", "OK"
            elif j == done_up_to and status == "running":
                s, dur, msg = "running", "…", "in progress"
            elif j == done_up_to and status == "failed":
                s, dur, msg = "failed", f"{random.randint(1,30)}s", random.choice(
                    ["OOM", "timeout", "assertion error", "connection refused"]
                )
            else:
                s, dur, msg = "pending", "—", "waiting"
            step_records.append({"step": j + 1, "name": name,
                                  "status": s, "duration": dur, "message": msg})

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


_JOBS    = _make_jobs()
_JOB_BY_ID = {j["id"]: j for j in _JOBS}


class MasterDetailVerticalScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back",      "Back"),
        Binding("[",      "shrink_master", "Shrink"),
        Binding("]",      "grow_master",   "Grow"),
    ]

    master_height: reactive[int] = reactive(40)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="mdv-body"):
            with Vertical(id="mdv-master"):
                yield Static(
                    "[b]Jobs[/b]  [dim]↑↓ navigate  Tab switch pane  [  ] resize split[/dim]",
                    id="mdv-master-title",
                )
                yield DataTable(id="mdv-master-table", cursor_type="row")
            with Vertical(id="mdv-detail"):
                yield Static("Select a job above to see its steps.", id="mdv-detail-header")
                yield DataTable(id="mdv-detail-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        master = self.query_one("#mdv-master-table", DataTable)
        master.add_columns("ID", "Type", "Tenant", "Status", "Duration", "Node")
        for job in _JOBS:
            color = _STATUS_COLORS.get(job["status"], "white")
            master.add_row(
                job["id"], job["type"], job["tenant"],
                f"[{color}]{job['status']}[/{color}]",
                job["duration"], job["node"],
                key=job["id"],
            )

        detail = self.query_one("#mdv-detail-table", DataTable)
        detail.add_columns("#", "Step", "Status", "Duration", "Message")

        self.watch_master_height(self.master_height)
        master.focus()
        self._load_detail(_JOBS[0]["id"])

    def watch_master_height(self, height: int) -> None:
        self.query_one("#mdv-master").styles.height = f"{height}%"

    def action_shrink_master(self) -> None:
        self.master_height = max(20, self.master_height - 5)

    def action_grow_master(self) -> None:
        self.master_height = min(75, self.master_height + 5)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "mdv-master-table" and event.row_key:
            self._load_detail(str(event.row_key.value))

    def _load_detail(self, job_id: str) -> None:
        job = _JOB_BY_ID.get(job_id)
        if not job:
            return
        color = _STATUS_COLORS.get(job["status"], "white")
        self.query_one("#mdv-detail-header", Static).update(
            f"[b]{job['id']}[/b]  ·  {job['type']}  ·  {job['tenant']}"
            f"  ·  [{color}]{job['status']}[/{color}]"
            f"  ·  {job['duration']}  ·  {job['node']}"
        )
        detail = self.query_one("#mdv-detail-table", DataTable)
        detail.clear()
        for step in job["steps"]:
            sc = _STEP_STATUS_COLORS.get(step["status"], "white")
            detail.add_row(
                str(step["step"]), step["name"],
                f"[{sc}]{step['status']}[/{sc}]",
                step["duration"],
                f"[dim]{step['message']}[/dim]",
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

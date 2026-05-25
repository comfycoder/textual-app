"""Demo: Concurrent workers — multiple parallel jobs with individual progress bars."""

import asyncio
import random
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Footer, Header, ProgressBar, Static

_JOBS = [
    ("job-1", "Data ingestion",    4.0),
    ("job-2", "Model training",    7.0),
    ("job-3", "Validation sweep",  5.0),
    ("job-4", "Result export",     3.0),
    ("job-5", "Report generation", 2.5),
]
_STEPS = 20


class WorkersDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._active: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="workers-body"):
            yield Static("[b]Concurrent Job Runner[/b]", classes="demo-label")
            for job_id, name, _ in _JOBS:
                with Horizontal(classes="worker-row"):
                    yield Static(name, classes="worker-name", id=f"wname-{job_id}")
                    yield ProgressBar(total=100, show_eta=False, id=f"pb-{job_id}")
                    yield Static("[dim]idle[/dim]", classes="worker-status", id=f"wstatus-{job_id}")
                    yield Button("Run",    variant="primary", id=f"btn-run-{job_id}",    classes="worker-btn")
                    yield Button("Cancel", variant="error",   id=f"btn-cancel-{job_id}", classes="worker-btn", disabled=True)
            with Horizontal(id="workers-global"):
                yield Button("Run All",    variant="success", id="btn-run-all")
                yield Button("Cancel All", variant="error",   id="btn-cancel-all")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "btn-run-all":
            for job_id, _, _ in _JOBS:
                if job_id not in self._active:
                    self._start_job(job_id)
        elif btn_id == "btn-cancel-all":
            self._active.clear()
        elif btn_id.startswith("btn-run-"):
            job_id = btn_id.removeprefix("btn-run-")
            if job_id not in self._active:
                self._start_job(job_id)
        elif btn_id.startswith("btn-cancel-"):
            job_id = btn_id.removeprefix("btn-cancel-")
            self._active.discard(job_id)
            self._set_state(job_id, "cancelled")

    def _start_job(self, job_id: str) -> None:
        duration = next(d for jid, _, d in _JOBS if jid == job_id)
        self._active.add(job_id)
        self._set_state(job_id, "running")
        self.query_one(f"#pb-{job_id}", ProgressBar).progress = 0
        self._run_job(job_id, duration)

    def _set_state(self, job_id: str, state: str) -> None:
        colors = {
            "running": "cyan", "done": "green", "failed": "red",
            "cancelled": "yellow", "idle": "dim",
        }
        color = colors.get(state, "white")
        self.query_one(f"#wstatus-{job_id}", Static).update(f"[{color}]{state}[/{color}]")
        is_running = (state == "running")
        self.query_one(f"#btn-run-{job_id}",    Button).disabled = is_running
        self.query_one(f"#btn-cancel-{job_id}", Button).disabled = not is_running

    @work
    async def _run_job(self, job_id: str, duration: float) -> None:
        pb = self.query_one(f"#pb-{job_id}", ProgressBar)
        step_time = duration / _STEPS
        for _ in range(_STEPS):
            if job_id not in self._active:
                return
            await asyncio.sleep(step_time + random.uniform(-0.05, 0.05))
            pb.advance(100 / _STEPS)
        if job_id in self._active:
            self._active.discard(job_id)
            pb.progress = 100
            state = "done" if random.random() > 0.15 else "failed"
            self._set_state(job_id, state)

    def action_go_back(self) -> None:
        self._active.clear()
        self.workers.cancel_all()   # stop sleeping _run_job coroutines before pop
        super().action_go_back()

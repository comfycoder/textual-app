"""Demo: Log — plain-text append-only log widget, compared side-by-side with RichLog."""

import random
from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Footer, Header, Label, Log, RichLog, Static

_LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
_MESSAGES = [
    "Job wi-042 submitted to queue",
    "Worker node-03 picked up job wi-042",
    "Preprocessing step 1/8 complete",
    "GPU memory usage: 14.2 / 24.0 GB",
    "Checkpoint saved at epoch 10",
    "Validation loss: 0.0519  accuracy: 0.9801",
    "Connection to mayo endpoint timed out",
    "Retry 1/3 — backing off 5s",
    "Scheduler queue depth: 14 jobs waiting",
    "Job wi-039 failed — OOM at step 3",
]

random.seed(7)


def _fake_line(rich: bool) -> str:
    ts  = datetime.now().strftime("%H:%M:%S")
    lvl = random.choice(_LEVELS)
    msg = random.choice(_MESSAGES)
    if rich:
        color = {"INFO": "cyan", "WARN": "yellow", "ERROR": "red", "DEBUG": "dim"}.get(lvl, "white")
        return f"[dim]{ts}[/dim]  [{color}]{lvl:5}[/{color}]  {msg}"
    return f"{ts}  {lvl:5}  {msg}"


class LogDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("space",  "add_line", "Add line"),
        Binding("c",      "clear",    "Clear"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="lg-controls"):
            yield Button("Add line",  id="btn-lg-add")
            yield Button("Add 10",    id="btn-lg-add10")
            yield Button("Clear",     variant="warning", id="btn-lg-clear")
            yield Static("", id="lg-count")
        with Horizontal(id="lg-body"):
            with Vertical(id="lg-left"):
                yield Label("[b]Log[/b]  [dim](plain text — no markup)[/dim]", classes="demo-label")
                yield Log(id="lg-plain", max_lines=200)
            with Vertical(id="lg-right"):
                yield Label("[b]RichLog[/b]  [dim](Rich markup + highlighting)[/dim]", classes="demo-label")
                yield RichLog(id="lg-rich", markup=True, max_lines=200)
        yield Footer()

    def on_mount(self) -> None:
        for _ in range(5):
            self._append_one()

    def _append_one(self) -> None:
        self.query_one("#lg-plain", Log).write_line(_fake_line(rich=False))
        self.query_one("#lg-rich",  RichLog).write(_fake_line(rich=True))
        count = self.query_one("#lg-plain", Log).line_count
        self.query_one("#lg-count", Static).update(f"[dim]{count} lines[/dim]")

    def action_add_line(self) -> None:
        self._append_one()

    def action_clear(self) -> None:
        self.query_one("#lg-plain", Log).clear()
        self.query_one("#lg-rich",  RichLog).clear()
        self.query_one("#lg-count", Static).update("[dim]0 lines[/dim]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-lg-add":
                self._append_one()
            case "btn-lg-add10":
                for _ in range(10):
                    self._append_one()
            case "btn-lg-clear":
                self.action_clear()


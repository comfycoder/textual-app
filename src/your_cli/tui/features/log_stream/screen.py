"""Demo: Streaming log viewer — async worker feeds a RichLog in real time."""

import asyncio
import random
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Footer, Header, RichLog, Static

_LEVELS = ["DEBUG", "DEBUG", "INFO", "INFO", "INFO", "WARNING", "ERROR"]
_LEVEL_COLORS = {
    "DEBUG":   "dim",
    "INFO":    "green",
    "WARNING": "yellow",
    "ERROR":   "red bold",
}
_SOURCES = ["pipeline", "worker", "scheduler", "api", "auth", "storage"]
_MESSAGES = [
    "Job {id} started on worker {n}",
    "Checkpoint saved to /data/checkpoints/{n}",
    "Retrying request (attempt {n} of 3)",
    "Connected to node 10.0.0.{n}",
    "Queue depth: {n} items pending",
    "Batch {id} complete — {n} items processed",
    "Health check passed",
    "Token refreshed for tenant {id}",
    "Config reloaded from /etc/config.yaml",
    "Timeout after {n}s — backing off",
    "Validation error in job {id}: missing subject_id",
]


def _make_line() -> str:
    level = random.choice(_LEVELS)
    source = random.choice(_SOURCES)
    msg = random.choice(_MESSAGES).format(
        id=f"wi-{random.randint(1, 999):03d}",
        n=random.randint(1, 300),
    )
    ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
    color = _LEVEL_COLORS[level]
    return f"[dim]{ts}[/dim]  [{color}]{level:<7}[/{color}]  [dim]{source:<10}[/dim]  {msg}"


class LogStreamDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("c", "clear_log", "Clear"),
    ]

    _streaming: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="log-controls"):
            yield Button("▶  Start", variant="success", id="btn-start")
            yield Button("■  Stop",  variant="error",   id="btn-stop",  disabled=True)
            yield Button("Clear",                        id="btn-clear")
            yield Static("", id="log-status")
        yield RichLog(id="log-output", highlight=True, wrap=False, markup=True)
        yield Footer()

    def watch__streaming(self, streaming: bool) -> None:
        self.query_one("#btn-start", Button).disabled = streaming
        self.query_one("#btn-stop",  Button).disabled = not streaming
        status = "[green]● Streaming[/green]" if streaming else "[dim]○ Stopped[/dim]"
        self.query_one("#log-status", Static).update(f"  {status}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-start":
                self._streaming = True
                self._stream_logs()
            case "btn-stop":
                self._streaming = False
            case "btn-clear":
                self.action_clear_log()

    @work(exclusive=True)
    async def _stream_logs(self) -> None:
        log = self.query_one("#log-output", RichLog)
        while self._streaming:
            log.write(_make_line())
            await asyncio.sleep(random.uniform(0.1, 0.5))

    def action_clear_log(self) -> None:
        self.query_one("#log-output", RichLog).clear()

    def action_go_back(self) -> None:
        self._streaming = False
        super().action_go_back()

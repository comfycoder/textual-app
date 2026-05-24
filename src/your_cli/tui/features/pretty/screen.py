"""Demo: Pretty — renders any Python object as syntax-highlighted formatted output."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Pretty, Static

_OBJECTS = {
    "Job record": {
        "id": "wi-042",
        "tenant": "jhu",
        "status": "done",
        "type": "training",
        "config": {
            "epochs": 50,
            "batch_size": 32,
            "learning_rate": 0.001,
            "optimizer": "adam",
        },
        "metrics": {
            "loss": 0.0412,
            "accuracy": 0.9876,
            "val_loss": 0.0519,
            "val_accuracy": 0.9801,
        },
        "duration_s": 252,
        "worker_node": "gpu-node-04",
    },
    "Cluster status": {
        "nodes": [
            {"id": "gpu-node-01", "gpus": 4, "state": "healthy",  "jobs": 2},
            {"id": "gpu-node-02", "gpus": 4, "state": "healthy",  "jobs": 3},
            {"id": "gpu-node-03", "gpus": 4, "state": "degraded", "jobs": 1},
            {"id": "gpu-node-04", "gpus": 4, "state": "healthy",  "jobs": 4},
        ],
        "total_gpus": 16,
        "available_gpus": 6,
        "queue_depth": 14,
    },
    "Config file": {
        "version": "2.1.0",
        "api_url": "https://api.aiq-solutions.com",
        "timeout_s": 30,
        "retry": {"max_attempts": 3, "backoff_s": 5},
        "tenants": ["jhu", "unc", "mayo"],
        "features": {
            "live_dashboard": True,
            "auto_retry": True,
            "telemetry": False,
        },
    },
    "Error response": {
        "error": "OOMError",
        "message": "Out of memory during preprocessing step 3",
        "job_id": "wi-039",
        "timestamp": "2024-12-31T14:22:07Z",
        "context": {
            "node": "gpu-node-03",
            "peak_memory_gb": 23.8,
            "limit_gb": 24.0,
            "step": 3,
            "total_steps": 8,
        },
        "traceback": ["...step3.py:142", "...runner.py:87", "...main.py:34"],
    },
    "Simple list": [1, 2, 3, "four", 5.0, True, None, {"nested": "dict"}],
}


class PrettyDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="pp-body"):
            with Vertical(id="pp-left"):
                yield Label("[b]Objects[/b]", classes="demo-label")
                yield ListView(
                    *[ListItem(Label(name), id=f"pp-item-{i}") for i, name in enumerate(_OBJECTS)],
                    id="pp-list",
                )
            with Vertical(id="pp-right"):
                yield Label("[b]Output[/b]", classes="demo-label")
                yield Static("[dim]Select an object on the left[/dim]", id="pp-hint")
                yield Pretty({}, id="pp-widget")
        yield Footer()

    def on_mount(self) -> None:
        lv = self.query_one("#pp-list", ListView)
        lv.focus()
        lv.index = 0
        self._show(0)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        idx = self.query_one("#pp-list", ListView).index
        if idx is not None:
            self._show(idx)

    def _show(self, index: int) -> None:
        names = list(_OBJECTS.keys())
        if 0 <= index < len(names):
            obj = _OBJECTS[names[index]]
            self.query_one("#pp-hint", Static).update(
                f"[dim]Showing: [b]{names[index]}[/b][/dim]"
            )
            self.query_one("#pp-widget", Pretty).update(obj)

    def action_go_back(self) -> None:
        self.app.pop_screen()

"""Demo: Live search and filter over a DataTable."""

import random

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Static

_STATUS_COLORS = {
    "queued": "yellow", "running": "cyan", "done": "green",
    "failed": "red",    "pending": "dim",
}
_STATUSES = list(_STATUS_COLORS)
_TYPES    = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS  = ["jhu", "unc", "mayo"]

random.seed(42)
_ITEMS = [
    {
        "id":      f"wi-{i:03d}",
        "tenant":  random.choice(_TENANTS),
        "status":  random.choice(_STATUSES),
        "type":    random.choice(_TYPES),
        "updated": f"{random.randint(8,17):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}",
    }
    for i in range(1, 31)
]


def _markup(status: str) -> str:
    color = _STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


class SearchFilterDemoScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    _filter: reactive[str] = reactive("")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="search-body"):
            yield Input(placeholder="Filter by ID, tenant, status, type…", id="search-input")
            yield Static("", id="search-count")
            yield DataTable(id="search-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Tenant", "Type", "Updated")
        self._refresh_table()
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._filter = event.value.lower()

    def watch__filter(self, _: str) -> None:
        self._refresh_table()

    def _refresh_table(self) -> None:
        query = self._filter
        matches = [
            item for item in _ITEMS
            if not query or any(query in item[f] for f in ("id", "tenant", "status", "type"))
        ]
        table = self.query_one(DataTable)
        table.clear()
        for item in matches:
            table.add_row(
                item["id"], _markup(item["status"]),
                item["tenant"], item["type"], item["updated"],
            )
        shown, total = len(matches), len(_ITEMS)
        color = "green" if shown == total else "yellow"
        self.query_one("#search-count", Static).update(
            f"  [{color}]{shown}[/{color}] of [b]{total}[/b] items"
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

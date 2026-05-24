"""Demo: Multi-select DataTable — Space to toggle, A/D to select all/none."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

_STATUS_COLORS = {
    "queued": "yellow", "running": "cyan", "done": "green",
    "failed": "red",    "pending": "dim",
}
_TYPES   = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS = ["jhu", "unc", "mayo"]

random.seed(42)
_ALL_ITEMS = [
    {
        "id":       f"wi-{i:03d}",
        "tenant":   random.choice(_TENANTS),
        "status":   random.choice(list(_STATUS_COLORS)),
        "type":     random.choice(_TYPES),
        "priority": random.choice(["high", "medium", "low"]),
    }
    for i in range(1, 26)
]

_CHECK = "[green]✓[/green]"
_EMPTY = "[dim] [/dim]"


class MultiSelectDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back",       "Back"),
        Binding("space",  "toggle_row",    "Toggle"),
        Binding("a",      "select_all",    "All"),
        Binding("d",      "deselect_all",  "None"),
    ]

    _selected: reactive[frozenset] = reactive(frozenset())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="ms-body"):
            yield Static("", id="ms-hint", classes="demo-label")
            yield DataTable(id="ms-table", cursor_type="row")
            with Horizontal(id="ms-actions"):
                yield Button("Run Selected",    variant="primary", id="btn-ms-run",    disabled=True)
                yield Button("Cancel Selected", variant="error",   id="btn-ms-cancel", disabled=True)
                yield Static("", id="ms-count")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("", "ID", "Status", "Tenant", "Type", "Priority")
        for item in _ALL_ITEMS:
            color  = _STATUS_COLORS.get(item["status"], "white")
            pri_color = {"high": "red", "medium": "yellow", "low": "green"}.get(item["priority"], "white")
            table.add_row(
                _EMPTY,
                item["id"],
                f"[{color}]{item['status']}[/{color}]",
                item["tenant"],
                item["type"],
                f"[{pri_color}]{item['priority']}[/{pri_color}]",
                key=item["id"],
            )
        self.query_one("#ms-hint", Static).update(
            "[b]Space[/b] toggle  [b]A[/b] select all  [b]D[/b] deselect all"
        )
        table.focus()

    def watch__selected(self, selected: frozenset) -> None:
        count = len(selected)
        self.query_one("#ms-count", Static).update(
            f"  [b]{count}[/b] of [b]{len(_ALL_ITEMS)}[/b] selected"
        )
        has_sel = count > 0
        self.query_one("#btn-ms-run",    Button).disabled = not has_sel
        self.query_one("#btn-ms-cancel", Button).disabled = not has_sel

    def _refresh_checkmarks(self) -> None:
        table = self.query_one(DataTable)
        for item in _ALL_ITEMS:
            mark = _CHECK if item["id"] in self._selected else _EMPTY
            table.update_cell(item["id"], table.columns[table.ordered_columns[0].key].key, mark)

    def action_toggle_row(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return
        row_key = table.ordered_rows[table.cursor_row].key.value
        current = set(self._selected)
        if row_key in current:
            current.discard(row_key)
        else:
            current.add(row_key)
        self._selected = frozenset(current)
        self._refresh_checkmarks()

    def action_select_all(self) -> None:
        self._selected = frozenset(item["id"] for item in _ALL_ITEMS)
        self._refresh_checkmarks()

    def action_deselect_all(self) -> None:
        self._selected = frozenset()
        self._refresh_checkmarks()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        ids = ", ".join(sorted(self._selected))
        match event.button.id:
            case "btn-ms-run":
                self.notify(
                    f"Queued {len(self._selected)} jobs: {ids}",
                    title="Jobs Queued",
                    severity="information",
                )
                self.action_deselect_all()
            case "btn-ms-cancel":
                self.notify(
                    f"Cancelled {len(self._selected)} jobs: {ids}",
                    title="Jobs Cancelled",
                    severity="warning",
                )
                self.action_deselect_all()

    def action_go_back(self) -> None:
        self.app.pop_screen()

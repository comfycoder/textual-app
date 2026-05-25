"""Demo: Inline editing — select a row, press E to edit in a panel below the table."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from typing import Any

from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static

from your_cli.tui.palette import STATUS_COLORS
_TENANTS  = [("JHU", "jhu"), ("UNC", "unc"), ("Mayo", "mayo")]
_STATUSES = [(s, s) for s in STATUS_COLORS]

_DATA: list[dict[str, Any]] = [
    {"id": "wi-001", "name": "Alpha pipeline",    "tenant": "jhu",  "status": "running"},
    {"id": "wi-002", "name": "Beta validation",   "tenant": "unc",  "status": "queued"},
    {"id": "wi-003", "name": "Mayo export",       "tenant": "mayo", "status": "done"},
    {"id": "wi-004", "name": "JHU inference",     "tenant": "jhu",  "status": "failed"},
    {"id": "wi-005", "name": "UNC preprocessing", "tenant": "unc",  "status": "pending"},
]


def _markup(status: str) -> str:
    color = STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


class InlineEditDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "cancel_or_back", "Back / Cancel"),
        Binding("e",      "start_edit",     "Edit"),
    ]

    _editing:      reactive[bool] = reactive(False)
    _cursor_row:   int = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "  Navigate rows with arrows · press [b]E[/b] to edit · [b]Escape[/b] to cancel / go back.",
            id="edit-hint",
        )
        yield DataTable(id="edit-table", cursor_type="row")
        with Vertical(id="edit-panel"):
            yield Static("[b]Edit row[/b]", classes="demo-label")
            yield Static("", id="edit-id-label")
            yield Label("Name")
            yield Input(placeholder="Job name", id="edit-name")
            yield Label("Tenant")
            yield Select(_TENANTS,  prompt="Tenant…", id="edit-tenant")
            yield Label("Status")
            yield Select(_STATUSES, prompt="Status…", id="edit-status")
            with Horizontal(id="edit-actions"):
                yield Button("Save",   variant="primary", id="btn-edit-save")
                yield Button("Cancel",                    id="btn-edit-cancel")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_table()
        self.query_one(DataTable).focus()
        self.query_one("#edit-panel").display = False

    def _refresh_table(self) -> None:
        table = self.query_one(DataTable)
        if not table.columns:
            table.add_columns("ID", "Name", "Tenant", "Status")
        table.clear()
        for item in _DATA:
            table.add_row(
                item["id"], item["name"], item["tenant"], _markup(item["status"]),
                key=item["id"],
            )

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._cursor_row = event.cursor_row

    def action_start_edit(self) -> None:
        if self._cursor_row >= len(_DATA):
            return
        item = _DATA[self._cursor_row]
        self.query_one("#edit-id-label", Static).update(f"Editing: [b]{item['id']}[/b]")
        self.query_one("#edit-name",   Input).value = item["name"]
        self.query_one("#edit-tenant", Select).value = item["tenant"]
        self.query_one("#edit-status", Select).value = item["status"]
        self.query_one("#edit-panel").display = True
        self._editing = True
        self.query_one("#edit-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-edit-save":
                self._save_edit()
            case "btn-edit-cancel":
                self._cancel_edit()

    def _save_edit(self) -> None:
        if self._cursor_row >= len(_DATA):
            return
        name   = self.query_one("#edit-name",   Input ).value.strip()
        tenant = self.query_one("#edit-tenant", Select).value
        status = self.query_one("#edit-status", Select).value

        missing = []
        if not name:
            missing.append("Name")
        if not isinstance(tenant, str):
            missing.append("Tenant")
        if not isinstance(status, str):
            missing.append("Status")
        if missing:
            self.notify(
                f"Required: {', '.join(missing)}",
                title="Cannot save",
                severity="error",
            )
            return

        item = _DATA[self._cursor_row]
        item["name"]   = name
        item["tenant"] = tenant
        item["status"] = status
        self._cancel_edit()
        self._refresh_table()
        self.notify(f"[b]{item['id']}[/b] updated.", title="Saved", severity="information")

    def _cancel_edit(self) -> None:
        self.query_one("#edit-panel").display = False
        self._editing = False
        self.query_one(DataTable).focus()

    def action_cancel_or_back(self) -> None:
        if self._editing:
            self._cancel_edit()
        else:
            self.app.pop_screen()

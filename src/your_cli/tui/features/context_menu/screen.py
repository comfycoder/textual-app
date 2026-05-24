"""Demo: Context menu triggered from a DataTable row — press Enter on any row."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from typing import Any

from textual.screen import ModalScreen
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import DataTable, Footer, Header, Label, ListItem, ListView, Static

from your_cli.tui.palette import STATUS_COLORS
_ITEMS = [
    {"id": "wi-001", "tenant": "jhu",  "status": "running", "type": "training"},
    {"id": "wi-002", "tenant": "unc",  "status": "queued",  "type": "validation"},
    {"id": "wi-003", "tenant": "mayo", "status": "done",    "type": "export"},
    {"id": "wi-004", "tenant": "jhu",  "status": "failed",  "type": "inference"},
    {"id": "wi-005", "tenant": "unc",  "status": "pending", "type": "preprocessing"},
    {"id": "wi-006", "tenant": "mayo", "status": "running", "type": "training"},
]
_ACTIONS = [
    ("▶  Run job",       "run"),
    ("■  Cancel job",    "cancel"),
    ("👁  View details",  "view"),
    ("📋  Copy ID",       "copy"),
    ("🗑  Delete",        "delete"),
]


class ContextMenuModal(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "dismiss_none", "Close")]

    def __init__(self, item: dict[str, Any]) -> None:
        super().__init__()
        self._item = item

    def compose(self) -> ComposeResult:
        with Vertical(id="ctx-modal-body"):
            yield Static(
                f"[b]{self._item['id']}[/b]  "
                f"[dim]{self._item['tenant']} · {self._item['type']}[/dim]",
                id="ctx-title",
            )
            yield ListView(
                *[ListItem(Label(label), id=f"ctx-{key}") for label, key in _ACTIONS],
                id="ctx-list",
            )

    def on_mount(self) -> None:
        self.query_one(ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            self.dismiss(event.item.id.removeprefix("ctx-"))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


class ContextMenuDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "  Select a row and press [b]Enter[/b] to open its context menu.",
            id="ctx-hint",
        )
        yield DataTable(id="ctx-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Tenant", "Type")
        for item in _ITEMS:
            color = STATUS_COLORS.get(item["status"], "white")
            table.add_row(
                item["id"],
                f"[{color}]{item['status']}[/{color}]",
                item["tenant"],
                item["type"],
                key=item["id"],
            )
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None:
            return
        item_id = str(event.row_key.value)
        item = next((i for i in _ITEMS if i["id"] == item_id), None)
        if item is None:
            return

        def handle(action: str | None) -> None:
            if action:
                self.notify(
                    f"[b]{action}[/b] → {item['id']}",
                    title="Context Menu",
                    severity="information",
                )

        self.app.push_screen(ContextMenuModal(item), handle)


"""ContextMenuModal — action-menu overlay for a DataTable row."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static

_ACTIONS = [
    ("▶  Run job",       "run"),
    ("■  Cancel job",    "cancel"),
    ("👁  View details",  "view"),
    ("📋  Copy ID",       "copy"),
    ("🗑  Delete",        "delete"),
]


class ContextMenuModal(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "dismiss_none", "Close")]

    def __init__(self, item: dict) -> None:
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

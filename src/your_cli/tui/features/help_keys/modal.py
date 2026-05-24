"""HelpModal — keyboard-reference overlay."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label


class HelpModal(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss", "Close")]

    def __init__(self, bindings: list[tuple[str, str, str]]) -> None:
        super().__init__()
        self._bindings = bindings

    def compose(self) -> ComposeResult:
        with Vertical(id="help-modal-body"):
            yield Label("[b]Keyboard Reference[/b]", id="help-modal-title")
            tbl = DataTable(id="help-table", show_cursor=False)
            yield tbl
            yield Button("Close", variant="primary", id="btn-help-close")

    def on_mount(self) -> None:
        tbl = self.query_one(DataTable)
        tbl.add_columns("Key", "Action", "Description")
        for key, action, desc in self._bindings:
            if desc:
                tbl.add_row(f"[b]{key}[/b]", action, desc)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

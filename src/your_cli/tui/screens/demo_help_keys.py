"""Demo: Help / keyboard reference — ? opens a modal listing all active bindings."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static


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


class HelpKeysDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape",   "go_back",    "Back"),
        Binding("?",        "show_help",  "Help"),
        Binding("r",        "refresh",    "Refresh data"),
        Binding("f",        "toggle_filter","Toggle filter"),
        Binding("e",        "export",     "Export CSV"),
        Binding("ctrl+a",   "select_all", "Select all"),
        Binding("ctrl+d",   "deselect",   "Deselect"),
        Binding("[",        "narrow",     "Narrow sidebar"),
        Binding("]",        "widen",      "Widen sidebar"),
        Binding("ctrl+r",   "hard_refresh","Hard refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="hk-body"):
            yield Static("[b]Help & Keyboard Reference Demo[/b]", classes="demo-label")
            yield Static(
                "This screen has many bindings registered. "
                "Press [b]?[/b] to open the keyboard reference modal.\n\n"
                "The modal reads the screen's BINDINGS list at runtime — "
                "no hardcoded list needed.\n\n"
                "Registered bindings on this screen:",
                id="hk-intro",
            )
            yield DataTable(id="hk-preview", show_cursor=False)
            yield Static(
                "\n[dim]Try pressing the keys above — most just show a toast "
                "to confirm they fire.[/dim]",
                id="hk-hint",
            )
        yield Footer()

    def on_mount(self) -> None:
        tbl = self.query_one("#hk-preview", DataTable)
        tbl.add_columns("Key", "Action", "Description")
        for binding in self.BINDINGS:
            if binding.description:
                tbl.add_row(f"[b]{binding.key}[/b]", binding.action, binding.description)

    def action_show_help(self) -> None:
        rows = [
            (b.key, b.action, b.description)
            for b in self.BINDINGS
            if b.description
        ]
        self.app.push_screen(HelpModal(rows))

    def action_refresh(self) -> None:
        self.notify("Data refreshed", title="Refresh")

    def action_toggle_filter(self) -> None:
        self.notify("Filter toggled", title="Filter")

    def action_export(self) -> None:
        self.notify("Export started", title="Export")

    def action_select_all(self) -> None:
        self.notify("All rows selected", title="Select")

    def action_deselect(self) -> None:
        self.notify("Selection cleared", title="Deselect")

    def action_narrow(self) -> None:
        self.notify("Sidebar narrowed", title="Sidebar")

    def action_widen(self) -> None:
        self.notify("Sidebar widened", title="Sidebar")

    def action_hard_refresh(self) -> None:
        self.notify("Hard refresh triggered", title="Hard Refresh")

    def action_go_back(self) -> None:
        self.app.pop_screen()

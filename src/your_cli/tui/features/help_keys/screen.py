"""Demo: Help / keyboard reference — ? opens a modal listing all active bindings."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import DataTable, Footer, Header, Static

from your_cli.tui.features.help_keys.modal import HelpModal


class HelpKeysDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("?",        "show_help",     "Help"),
        Binding("r",        "refresh",       "Refresh data"),
        Binding("f",        "toggle_filter", "Toggle filter"),
        Binding("e",        "export",        "Export CSV"),
        Binding("ctrl+a",   "select_all",    "Select all"),
        Binding("ctrl+d",   "deselect",      "Deselect"),
        Binding("[",        "narrow",        "Narrow sidebar"),
        Binding("]",        "widen",         "Widen sidebar"),
        Binding("ctrl+r",   "hard_refresh",  "Hard refresh"),
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
        tbl: DataTable[str] = self.query_one("#hk-preview", DataTable)
        tbl.add_columns("Key", "Action", "Description")
        for b in self.BINDINGS:
            if isinstance(b, Binding) and b.description:
                tbl.add_row(f"[b]{b.key}[/b]", b.action, b.description)

    def action_show_help(self) -> None:
        rows = [
            (b.key, b.action, b.description)
            for b in self.BINDINGS
            if isinstance(b, Binding) and b.description
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


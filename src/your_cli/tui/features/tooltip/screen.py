"""Demo: Tooltip — hover any widget to see its tooltip."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
    Switch,
)


class TooltipDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="tt-body"):
            yield Static("[b]Tooltip Demo[/b]", classes="demo-label")
            yield Static(
                "Hover over any widget below to see its tooltip.\n"
                "Tooltips are set via [b]widget.tooltip = \"text\"[/b] — "
                "works on any widget.\n",
                id="tt-intro",
            )

            yield Static("[b]Buttons[/b]", classes="demo-label")
            with Horizontal(id="tt-buttons"):
                yield Button("Submit",  variant="primary", id="tt-btn-submit")
                yield Button("Reset",   variant="default", id="tt-btn-reset")
                yield Button("Delete",  variant="error",   id="tt-btn-delete")

            yield Static("[b]Form Controls[/b]", classes="demo-label")
            with Vertical(id="tt-form"):
                yield Label("Project name")
                yield Input(id="tt-input")
                with Horizontal(id="tt-toggles"):
                    yield Switch(id="tt-switch")
                    yield Label("Auto-submit", id="tt-switch-label")
                yield Checkbox("Priority job", id="tt-checkbox")
                yield Select(
                    [("JHU", "jhu"), ("UNC", "unc"), ("Mayo", "mayo")],
                    prompt="Select tenant…",
                    id="tt-select",
                )

            yield Static("[b]Data & Progress[/b]", classes="demo-label")
            yield ProgressBar(total=100, id="tt-progress")
            tbl: DataTable[str] = DataTable(id="tt-table", show_cursor=False)
            yield tbl

        yield Footer()

    def on_mount(self) -> None:
        # Buttons
        self.query_one("#tt-btn-submit", Button).tooltip = (
            "Submit the current form — validates all fields before sending"
        )
        self.query_one("#tt-btn-reset", Button).tooltip = (
            "Reset all fields to their default values"
        )
        self.query_one("#tt-btn-delete", Button).tooltip = (
            "Permanently delete this record — this action cannot be undone"
        )

        # Form controls
        self.query_one("#tt-input", Input).tooltip = (
            "Enter a project name: 3–50 chars, letters/numbers/hyphens only"
        )
        self.query_one("#tt-switch", Switch).tooltip = (
            "When ON, the form is submitted automatically on valid input"
        )
        self.query_one("#tt-checkbox", Checkbox).tooltip = (
            "Priority jobs skip the normal queue and run on dedicated nodes"
        )
        self.query_one("#tt-select", Select).tooltip = (
            "Choose the tenant whose compute cluster will run this job"
        )

        # Progress
        pb = self.query_one("#tt-progress", ProgressBar)
        pb.advance(62)
        pb.tooltip = "Overall job completion — 62 of 100 tasks finished"

        # DataTable
        tbl = self.query_one("#tt-table", DataTable)
        tbl.add_columns("ID", "Status", "Duration")
        tbl.add_row("wi-042", "[green]done[/green]",    "4m 12s")
        tbl.add_row("wi-043", "[cyan]running[/cyan]",   "1m 08s…")
        tbl.add_row("wi-044", "[yellow]queued[/yellow]","—")
        tbl.tooltip = "Recent jobs — press Enter on a row for details"

    def action_go_back(self) -> None:
        self.app.pop_screen()

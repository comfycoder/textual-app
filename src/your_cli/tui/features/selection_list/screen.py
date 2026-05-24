"""Demo: SelectionList — checkbox-style multi-select with built-in state tracking."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, SelectionList, Static
from textual.widgets.selection_list import Selection

_JOB_TYPES = [
    ("Training",        "training"),
    ("Validation",      "validation"),
    ("Inference",       "inference"),
    ("Export",          "export"),
    ("Preprocessing",   "preprocessing"),
    ("Fine-tuning",     "fine-tuning"),
    ("Evaluation",      "evaluation"),
    ("Data Ingestion",  "data-ingestion"),
]

_TENANTS = [
    ("Johns Hopkins (JHU)", "jhu",      True),   # pre-selected
    ("UNC Chapel Hill",     "unc",      True),
    ("Mayo Clinic",         "mayo",     False),
    ("Stanford",            "stanford", False),
    ("MIT",                 "mit",      False),
]


class SelectionListDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="sl-body"):
            with Vertical(id="sl-left"):
                yield Label("[b]Job Types[/b]", classes="demo-label")
                yield Label("[dim]Space to toggle · a select all · n select none[/dim]", id="sl-hint")
                yield SelectionList(
                    *[Selection(label, value) for label, value in _JOB_TYPES],
                    id="sl-jobtypes",
                )
                yield Label("[b]Tenants[/b]", classes="demo-label")
                yield SelectionList(
                    *[Selection(label, value, initial_state) for label, value, initial_state in _TENANTS],
                    id="sl-tenants",
                )
            with Vertical(id="sl-right"):
                yield Label("[b]Selected[/b]", classes="demo-label")
                yield Static("", id="sl-summary")
                yield Button("Run Jobs", variant="primary", id="btn-sl-run", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sl-jobtypes", SelectionList).focus()
        self._update_summary()

    def on_selection_list_selection_toggled(
        self, event: SelectionList.SelectionToggled
    ) -> None:
        self._update_summary()

    def _update_summary(self) -> None:
        types   = self.query_one("#sl-jobtypes", SelectionList).selected
        tenants = self.query_one("#sl-tenants",  SelectionList).selected

        lines = []
        if types:
            lines.append("[b]Job types:[/b]  " + ", ".join(str(v) for v in types))
        else:
            lines.append("[dim]No job types selected[/dim]")

        if tenants:
            lines.append("[b]Tenants:[/b]  " + ", ".join(str(v) for v in tenants))
        else:
            lines.append("[dim]No tenants selected[/dim]")

        self.query_one("#sl-summary", Static).update("\n".join(lines))
        self.query_one("#btn-sl-run", Button).disabled = not (types and tenants)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        types   = self.query_one("#sl-jobtypes", SelectionList).selected
        tenants = self.query_one("#sl-tenants",  SelectionList).selected
        self.notify(
            f"{len(types)} type(s) × {len(tenants)} tenant(s) = "
            f"{len(types)*len(tenants)} jobs queued",
            title="Jobs Submitted",
            severity="information",
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

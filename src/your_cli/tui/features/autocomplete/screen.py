"""Demo: Autocomplete — Input with SuggestFromList drops suggestions inline."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.suggester import SuggestFromList
from textual.widgets import Button, Footer, Header, Input, Label, Static

_TENANTS = ["jhu", "unc", "mayo", "stanford", "mit", "caltech", "oxford", "cambridge"]

_JOB_TYPES = [
    "training", "validation", "export", "inference", "preprocessing",
    "fine-tuning", "evaluation", "data-ingestion", "model-serving", "hyperparameter-search",
]

_USERS = [
    "alice@jhu.edu", "bob@unc.edu", "carol@mayo.org", "dave@stanford.edu",
    "eve@mit.edu", "frank@caltech.edu", "grace@oxford.ac.uk", "henry@cam.ac.uk",
    "iris@jhu.edu", "jack@unc.edu",
]

_TAGS = [
    "prod", "dev", "staging", "experiment", "baseline", "ablation",
    "batch-1", "batch-2", "nightly", "weekly", "manual", "scheduled",
    "high-priority", "low-priority", "gpu-required", "cpu-only",
]


class AutocompleteDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "submit",  "Submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="ac-body"):
            yield Static("[b]Autocomplete Input Demo[/b]", classes="demo-label")
            yield Static(
                "Each field has a [b]SuggestFromList[/b] suggester attached.\n"
                "Start typing — the best matching suggestion appears inline.\n"
                "Press [b]→[/b] (right arrow) to accept the suggestion.\n",
                id="ac-intro",
            )

            yield Label("Tenant  [dim]e.g. jhu[/dim]")
            yield Input(
                id="ac-tenant",
                suggester=SuggestFromList(_TENANTS, case_sensitive=False),
            )

            yield Label("Job type  [dim]e.g. training[/dim]")
            yield Input(
                id="ac-jobtype",
                suggester=SuggestFromList(_JOB_TYPES, case_sensitive=False),
            )

            yield Label("Submitted by  [dim]e.g. alice@jhu.edu[/dim]")
            yield Input(
                id="ac-user",
                suggester=SuggestFromList(_USERS, case_sensitive=False),
            )

            yield Label("Tag  [dim]e.g. prod[/dim]")
            yield Input(
                id="ac-tag",
                suggester=SuggestFromList(_TAGS, case_sensitive=False),
            )

            yield Button("Submit", variant="primary", id="btn-ac-submit")
            yield Static("", id="ac-result")
        yield Footer()

    def action_submit(self) -> None:
        self.query_one("#btn-ac-submit", Button).press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "btn-ac-submit":
            return
        tenant  = self.query_one("#ac-tenant",  Input).value
        jobtype = self.query_one("#ac-jobtype", Input).value
        user    = self.query_one("#ac-user",    Input).value
        tag     = self.query_one("#ac-tag",     Input).value

        parts = []
        if tenant:
            parts.append(f"tenant=[b]{tenant}[/b]")
        if jobtype:
            parts.append(f"type=[b]{jobtype}[/b]")
        if user:
            parts.append(f"by=[b]{user}[/b]")
        if tag:
            parts.append(f"tag=[b]{tag}[/b]")

        if parts:
            self.query_one("#ac-result", Static).update(
                "[green]Submitted:[/green]  " + "  ".join(parts)
            )
            self.notify("Job submitted", title="Success", severity="information")
        else:
            self.query_one("#ac-result", Static).update(
                "[dim]Fill in at least one field.[/dim]"
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

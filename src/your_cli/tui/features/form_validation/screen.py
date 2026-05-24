"""Demo: Form validation — inline errors, live re-validation after first submit."""

import re
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

_TENANTS = [
    ("Johns Hopkins (JHU)", "jhu"),
    ("UNC Chapel Hill",     "unc"),
    ("Mayo Clinic",         "mayo"),
]


class FormValidationDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self._submitted_once = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="vf-body"):
            yield Static("[b]Job Submission Form[/b]", classes="demo-label")

            yield Label("Project name  [dim](required · letters, numbers, - _)  e.g. my-pipeline[/dim]")
            yield Input(id="vf-name")
            yield Static("", id="vf-name-err", classes="field-error")

            yield Label("Email  [dim](required)  e.g. you@institution.edu[/dim]")
            yield Input(id="vf-email")
            yield Static("", id="vf-email-err", classes="field-error")

            yield Label("Tenant  [dim](required)[/dim]")
            yield Select(_TENANTS, prompt="Select tenant…", id="vf-tenant")
            yield Static("", id="vf-tenant-err", classes="field-error")

            yield Label("Max concurrent jobs  [dim](required · 1–20)  e.g. 4[/dim]")
            yield Input(id="vf-jobs")
            yield Static("", id="vf-jobs-err", classes="field-error")

            yield Label("Description  [dim](optional · max 200 chars)[/dim]")
            yield Input(id="vf-desc")
            yield Static("", id="vf-desc-err", classes="field-error")

            with Horizontal(id="vf-actions"):
                yield Button("Submit", variant="primary", id="btn-vf-submit")
                yield Button("Reset",                    id="btn-vf-reset")
        yield Footer()

    # ── Validation ────────────────────────────────────────────────

    def _validate(self) -> bool:
        errors: dict[str, str] = {}

        name = self.query_one("#vf-name", Input).value.strip()
        if not name:
            errors["vf-name"] = "Required"
        elif len(name) < 3:
            errors["vf-name"] = "Minimum 3 characters"
        elif len(name) > 50:
            errors["vf-name"] = "Maximum 50 characters"
        elif not re.match(r"^[a-zA-Z0-9_-]+$", name):
            errors["vf-name"] = "Only letters, numbers, hyphens and underscores"

        email = self.query_one("#vf-email", Input).value.strip()
        if not email:
            errors["vf-email"] = "Required"
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            errors["vf-email"] = "Enter a valid email address"

        if self.query_one("#vf-tenant", Select).value is Select.BLANK:
            errors["vf-tenant"] = "Please select a tenant"

        jobs_str = self.query_one("#vf-jobs", Input).value.strip()
        if not jobs_str:
            errors["vf-jobs"] = "Required"
        else:
            try:
                jobs = int(jobs_str)
                if not (1 <= jobs <= 20):
                    errors["vf-jobs"] = "Must be between 1 and 20"
            except ValueError:
                errors["vf-jobs"] = "Must be a whole number"

        desc = self.query_one("#vf-desc", Input).value
        if len(desc) > 200:
            errors["vf-desc"] = f"Maximum 200 characters ({len(desc)} entered)"

        for field in ("vf-name", "vf-email", "vf-tenant", "vf-jobs", "vf-desc"):
            w = self.query_one(f"#{field}-err", Static)
            if field in errors:
                w.update(f"[red]⚠  {errors[field]}[/red]")
            elif field == "vf-desc" and not self.query_one("#vf-desc", Input).value:
                w.update("")
            else:
                w.update("[green]✓[/green]")

        return len(errors) == 0

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._submitted_once:
            self._validate()

    def on_select_changed(self, event: Select.Changed) -> None:
        if self._submitted_once:
            self._validate()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-vf-submit":
                self._submitted_once = True
                if self._validate():
                    self.notify(
                        "Job submitted successfully!",
                        title="Success",
                        severity="information",
                    )
                    self._submitted_once = False
            case "btn-vf-reset":
                self._submitted_once = False
                for inp_id in ("#vf-name", "#vf-email", "#vf-jobs", "#vf-desc"):
                    self.query_one(inp_id, Input).value = ""
                self.query_one("#vf-tenant", Select).clear()
                for err_id in (
                    "#vf-name-err", "#vf-email-err", "#vf-tenant-err",
                    "#vf-jobs-err", "#vf-desc-err",
                ):
                    self.query_one(err_id, Static).update("")

    def action_go_back(self) -> None:
        self.app.pop_screen()

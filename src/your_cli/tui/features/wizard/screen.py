"""Demo: Multi-step wizard with forward/back navigation and a review step."""

from dataclasses import dataclass
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Select, Static

_TENANTS = [("Johns Hopkins (JHU)", "jhu"), ("UNC Chapel Hill", "unc"), ("Mayo Clinic", "mayo")]
_PRIORITIES = [("Normal", "normal"), ("High", "high"), ("Low", "low")]
TOTAL_STEPS = 3


@dataclass
class WizardData:
    project_name: str = ""
    tenant: str = ""
    enable_logging: bool = True
    enable_validation: bool = True
    enable_notifications: bool = False
    priority: str = "normal"


class WizardDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    _step: reactive[int] = reactive(1)

    def __init__(self) -> None:
        super().__init__()
        self._data = WizardData()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-body"):
            yield Static("", id="wizard-step-label")

            with Vertical(id="wizard-step-1", classes="wizard-step"):
                yield Static("[b]Project Details[/b]", classes="wizard-title")
                yield Label("Project name  [dim]e.g. my-pipeline[/dim]")
                yield Input(id="wiz-project-name")
                yield Label("Tenant")
                yield Select(_TENANTS, prompt="Select tenant…", id="wiz-tenant")

            with Vertical(id="wizard-step-2", classes="wizard-step"):
                yield Static("[b]Configuration[/b]", classes="wizard-title")
                yield Checkbox("Enable logging",        value=True,  id="wiz-logging")
                yield Checkbox("Enable validation",     value=True,  id="wiz-validation")
                yield Checkbox("Enable notifications",  value=False, id="wiz-notifications")
                yield Label("Priority")
                yield Select(_PRIORITIES, value="normal", id="wiz-priority")

            with Vertical(id="wizard-step-3", classes="wizard-step"):
                yield Static("[b]Review & Submit[/b]", classes="wizard-title")
                yield Static("", id="wiz-summary")

            with Horizontal(id="wizard-nav"):
                yield Button("← Back",  id="btn-wiz-back",   disabled=True)
                yield Button("Next →",  id="btn-wiz-next",   variant="primary")
                yield Button("Submit",  id="btn-wiz-submit", variant="success", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        self._show_step(1)

    def _show_step(self, step: int) -> None:
        for i in range(1, TOTAL_STEPS + 1):
            self.query_one(f"#wizard-step-{i}").display = (i == step)
        back = self.query_one("#btn-wiz-back",   Button)
        nxt  = self.query_one("#btn-wiz-next",   Button)
        sub  = self.query_one("#btn-wiz-submit", Button)
        back.disabled = (step == 1)
        nxt.display   = (step < TOTAL_STEPS)
        sub.display   = (step == TOTAL_STEPS)
        if step == TOTAL_STEPS:
            self._update_summary()
        self.query_one("#wizard-step-label", Static).update(
            f"[dim]Step {step} of {TOTAL_STEPS}[/dim]"
        )

    def _collect_step(self, step: int) -> None:
        if step == 1:
            self._data.project_name = self.query_one("#wiz-project-name", Input).value
            v = self.query_one("#wiz-tenant", Select).value
            if isinstance(v, str):
                self._data.tenant = v
        elif step == 2:
            self._data.enable_logging       = self.query_one("#wiz-logging",       Checkbox).value
            self._data.enable_validation    = self.query_one("#wiz-validation",    Checkbox).value
            self._data.enable_notifications = self.query_one("#wiz-notifications", Checkbox).value
            v = self.query_one("#wiz-priority", Select).value
            if isinstance(v, str):
                self._data.priority = v

    def _update_summary(self) -> None:
        d = self._data
        tenant_label = next((lbl for lbl, val in _TENANTS if val == d.tenant), d.tenant or "[red]not set[/red]")
        name = d.project_name or "[red]not set[/red]"
        features = [
            feat for feat, enabled in [
                ("Logging",       d.enable_logging),
                ("Validation",    d.enable_validation),
                ("Notifications", d.enable_notifications),
            ] if enabled
        ]
        self.query_one("#wiz-summary", Static).update(
            f"  [dim]Project   [/dim]  {name}\n"
            f"  [dim]Tenant    [/dim]  {tenant_label}\n"
            f"  [dim]Priority  [/dim]  {d.priority}\n"
            f"  [dim]Features  [/dim]  {', '.join(features) or 'none'}\n"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-wiz-back":
                self._step = max(self._step - 1, 1)
                self._show_step(self._step)
            case "btn-wiz-next":
                self._collect_step(self._step)
                self._step = min(self._step + 1, TOTAL_STEPS)
                self._show_step(self._step)
            case "btn-wiz-submit":
                self._collect_step(self._step)
                d = self._data
                self.notify(
                    f"Project [b]{d.project_name or 'unnamed'}[/b] submitted for [b]{d.tenant or '—'}[/b]",
                    title="Wizard Complete",
                    severity="information",
                )


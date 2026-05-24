"""Demo: Label Form — each field on its own line with the label to the left."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Footer, Header, Input, Label, Rule, Select, Static, Switch

_TYPE_OPTS     = [("Training","training"),("Validation","validation"),("Export","export"),("Inference","inference"),("Preprocessing","preprocessing")]
_STATUS_OPTS   = [("Queued","queued"),("Running","running"),("Done","done"),("Failed","failed"),("Pending","pending")]
_PRIORITY_OPTS = [("Low","low"),("Medium","medium"),("High","high"),("Critical","critical")]
_TENANT_OPTS   = [("JHU","jhu"),("UNC","unc"),("Mayo","mayo"),("Stanford","stanford")]
_ENV_OPTS      = [("Production","prod"),("Staging","staging"),("Development","dev")]


class LabelFormDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("ctrl+s", "save",    "Save"),
        Binding("ctrl+n", "clear",   "Clear"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="lf-body"):
            with Vertical(id="lf-form"):
                yield Static("[b]Create / Edit Job[/b]", id="lf-title")
                yield Rule()

                # ── Identity ──────────────────────────────────────
                yield Static("[dim]Identity[/dim]", classes="lf-section")

                with Horizontal(classes="lf-row"):
                    yield Label("Job name", classes="lf-label")
                    yield Input(id="lf-name")

                with Horizontal(classes="lf-row"):
                    yield Label("Type", classes="lf-label")
                    yield Select(_TYPE_OPTS, prompt="Select…", id="lf-type")

                with Horizontal(classes="lf-row"):
                    yield Label("Tenant", classes="lf-label")
                    yield Select(_TENANT_OPTS, prompt="Select…", id="lf-tenant")

                yield Rule(line_style="dashed")

                # ── State ─────────────────────────────────────────
                yield Static("[dim]State[/dim]", classes="lf-section")

                with Horizontal(classes="lf-row"):
                    yield Label("Status", classes="lf-label")
                    yield Select(_STATUS_OPTS, prompt="Select…", id="lf-status")

                with Horizontal(classes="lf-row"):
                    yield Label("Priority", classes="lf-label")
                    yield Select(_PRIORITY_OPTS, prompt="Select…", id="lf-priority")

                with Horizontal(classes="lf-row"):
                    yield Label("Environment", classes="lf-label")
                    yield Select(_ENV_OPTS, prompt="Select…", id="lf-env")

                yield Rule(line_style="dashed")

                # ── Execution ─────────────────────────────────────
                yield Static("[dim]Execution[/dim]", classes="lf-section")

                with Horizontal(classes="lf-row"):
                    yield Label("Submitted by", classes="lf-label")
                    yield Input(id="lf-submitted-by")

                with Horizontal(classes="lf-row"):
                    yield Label("Worker node", classes="lf-label")
                    yield Input(id="lf-node")

                with Horizontal(classes="lf-row"):
                    yield Label("Max concurrent jobs", classes="lf-label")
                    yield Input(id="lf-max-jobs", type="integer")

                with Horizontal(classes="lf-row"):
                    yield Label("Timeout  [dim](minutes)[/dim]", classes="lf-label")
                    yield Input(id="lf-timeout", type="integer")

                with Horizontal(classes="lf-row lf-toggle-row"):
                    yield Label("GPU required", classes="lf-label")
                    yield Switch(id="lf-gpu")

                with Horizontal(classes="lf-row lf-toggle-row"):
                    yield Label("Auto-retry", classes="lf-label")
                    yield Switch(id="lf-retry")

                yield Rule(line_style="dashed")

                # ── Metadata ──────────────────────────────────────
                yield Static("[dim]Metadata[/dim]", classes="lf-section")

                with Horizontal(classes="lf-row"):
                    yield Label("Tags  [dim](comma-separated)[/dim]", classes="lf-label")
                    yield Input(id="lf-tags")

                with Horizontal(classes="lf-row"):
                    yield Label("Notes", classes="lf-label")
                    yield Input(id="lf-notes")

                with Horizontal(classes="lf-row"):
                    yield Label("Description", classes="lf-label")
                    yield Input(id="lf-description")

                yield Rule()

                with Horizontal(id="lf-actions"):
                    yield Button("Save",  variant="primary", id="btn-lf-save")
                    yield Button("Clear", id="btn-lf-clear")
                    yield Static("", id="lf-msg")

        yield Footer()

    # ── Button / action handlers ───────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-lf-save":
                self._save()
            case "btn-lf-clear":
                self._clear()

    def action_save(self)    -> None: self._save()
    def action_clear(self)   -> None: self._clear()

    # ── Save ──────────────────────────────────────────────────────

    def _save(self) -> None:
        name = self.query_one("#lf-name", Input).value.strip()
        if not name:
            self.query_one("#lf-msg", Static).update("[red]Job name is required[/red]")
            self.query_one("#lf-name", Input).focus()
            return
        jtype  = self.query_one("#lf-type",     Select).value
        status = self.query_one("#lf-status",   Select).value
        pri    = self.query_one("#lf-priority", Select).value
        if any(v is Select.BLANK for v in (jtype, status, pri)):
            self.query_one("#lf-msg", Static).update("[red]Type, Status, and Priority are required[/red]")
            return
        self.query_one("#lf-msg", Static).update(f"[green]✓  Saved: {name}[/green]")
        self.notify(f"Job '{name}' saved", title="Saved", severity="information")

    # ── Clear ─────────────────────────────────────────────────────

    def _clear(self) -> None:
        for wid in ("#lf-name","#lf-submitted-by","#lf-node",
                    "#lf-max-jobs","#lf-timeout","#lf-tags",
                    "#lf-notes","#lf-description"):
            self.query_one(wid, Input).value = ""
        for wid in ("#lf-type","#lf-status","#lf-priority","#lf-tenant","#lf-env"):
            self.query_one(wid, Select).clear()
        self.query_one("#lf-gpu",   Switch).value = False
        self.query_one("#lf-retry", Switch).value = False
        self.query_one("#lf-msg",   Static).update("")
        self.query_one("#lf-name",  Input).focus()

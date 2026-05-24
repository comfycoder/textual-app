"""Demo: Card patterns — five composable card styles built with compose()."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, ProgressBar, Rule, Static


# ── Card widgets ──────────────────────────────────────────────────────────────

class AlertCard(Widget):
    """Severity-coloured card with a left accent border.

    severity: "info" | "success" | "warning" | "error"
    """

    DEFAULT_CSS: ClassVar[str] = """
    AlertCard {
        height: auto;
        width: 1fr;
        padding: 1 2;
        background: $boost;
    }
    AlertCard.-info    { border-left: outer $primary; }
    AlertCard.-success { border-left: outer $success; }
    AlertCard.-warning { border-left: outer $warning; }
    AlertCard.-error   { border-left: outer $error;   }

    AlertCard .alert-title { text-style: bold; margin-bottom: 1; }
    AlertCard.-info    .alert-title { color: $primary; }
    AlertCard.-success .alert-title { color: $success; }
    AlertCard.-warning .alert-title { color: $warning; }
    AlertCard.-error   .alert-title { color: $error;   }
    """

    _ICONS: ClassVar[dict[str, str]] = {
        "info":    "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error":   "✗",
    }

    def __init__(self, severity: str, title: str, body: str, **kw) -> None:
        existing = kw.pop("classes", "")
        super().__init__(classes=f"-{severity} {existing}".strip(), **kw)
        self._severity = severity
        self._title    = title
        self._body     = body

    def compose(self) -> ComposeResult:
        icon = self._ICONS.get(self._severity, "•")
        yield Static(f"{icon}  {self._title}", classes="alert-title")
        yield Static(self._body)


class ProfileCard(Widget):
    """Person / entity card: avatar initial, name, role, bio, and tags."""

    DEFAULT_CSS: ClassVar[str] = """
    ProfileCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ProfileCard:hover { border: round $accent; }

    ProfileCard .prc-header  { height: auto; align: left middle; }
    ProfileCard .prc-avatar  {
        width: 5;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $background;
        text-style: bold;
        margin-right: 1;
    }
    ProfileCard .prc-name    { text-style: bold; }
    ProfileCard .prc-role    { color: $text-muted; }
    ProfileCard .prc-bio     { margin-top: 1; }
    ProfileCard .prc-tags    { margin-top: 1; color: $accent; }
    """

    def __init__(self, name: str, role: str, bio: str, tags: list[str], **kw) -> None:
        super().__init__(**kw)
        self._name = name
        self._role = role
        self._bio  = bio
        self._tags = tags

    def compose(self) -> ComposeResult:
        initial = self._name[0].upper() if self._name else "?"
        with Horizontal(classes="prc-header"):
            yield Static(initial, classes="prc-avatar")
            with Vertical():
                yield Static(self._name, classes="prc-name")
                yield Static(self._role, classes="prc-role")
        yield Rule(line_style="dashed")
        yield Static(self._bio, classes="prc-bio")
        if self._tags:
            yield Static(
                "  ".join(f"[b]#{t}[/b]" for t in self._tags),
                classes="prc-tags",
                markup=True,
            )


class ProgressCard(Widget):
    """Task / quota card with a labeled progress bar."""

    DEFAULT_CSS: ClassVar[str] = """
    ProgressCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ProgressCard:hover { border: round $accent; }

    ProgressCard .pgc-title  { text-style: bold; color: $accent; }
    ProgressCard .pgc-sub    { color: $text-muted; margin-bottom: 1; }
    ProgressCard ProgressBar { width: 1fr; margin-top: 1; }
    ProgressCard .pgc-footer { color: $text-muted; margin-top: 1; }
    """

    def __init__(
        self,
        title: str,
        progress: float,
        total: float = 100.0,
        subtitle: str = "",
        footer: str = "",
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title    = title
        self._progress = progress
        self._total    = total
        self._subtitle = subtitle
        self._footer   = footer

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="pgc-title")
        if self._subtitle:
            yield Static(self._subtitle, classes="pgc-sub")
        yield ProgressBar(total=self._total, show_eta=False)
        if self._footer:
            yield Static(self._footer, classes="pgc-footer")

    def on_mount(self) -> None:
        self.query_one(ProgressBar).advance(self._progress)


class ActionCard(Widget):
    """Call-to-action card: title, body, primary button, optional secondary button."""

    DEFAULT_CSS: ClassVar[str] = """
    ActionCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ActionCard:hover { border: round $accent; }

    ActionCard .avc-title   { text-style: bold; color: $accent; margin-bottom: 1; }
    ActionCard .avc-body    { margin-bottom: 1; }
    ActionCard .avc-actions { height: auto; margin-top: 1; align: left middle; }
    ActionCard .avc-actions Button { margin-right: 1; }
    """

    def __init__(
        self,
        title: str,
        body: str,
        primary_label: str,
        secondary_label: str = "",
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title     = title
        self._body      = body
        self._primary   = primary_label
        self._secondary = secondary_label

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="avc-title")
        yield Rule(line_style="dashed")
        yield Static(self._body, classes="avc-body")
        with Horizontal(classes="avc-actions"):
            yield Button(self._primary, variant="primary")
            if self._secondary:
                yield Button(self._secondary)


class KVCard(Widget):
    """Key-value summary card: title plus a list of label → value pairs."""

    DEFAULT_CSS: ClassVar[str] = """
    KVCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    KVCard:hover { border: round $accent; }

    KVCard .kvc-title    { text-style: bold; color: $accent; margin-bottom: 1; }
    KVCard .kvc-row      { height: auto; margin-bottom: 0; }
    KVCard .kvc-key      { width: 16; color: $text-muted; }
    KVCard .kvc-value    { width: 1fr; }
    """

    def __init__(self, title: str, items: list[tuple[str, str]], **kw) -> None:
        super().__init__(**kw)
        self._title = title
        self._items = items

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="kvc-title")
        yield Rule(line_style="dashed")
        for key, value in self._items:
            with Horizontal(classes="kvc-row"):
                yield Static(key, classes="kvc-key")
                yield Static(value, classes="kvc-value")


# ── Demo screen ───────────────────────────────────────────────────────────────

class CardsDemoScreen(Screen[None]):
    """Five composable card patterns: alert, profile, progress, action, key-value."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="crd-body"):

            # ── Alert cards ───────────────────────────────────────
            yield Static(
                "[b]Alert Cards[/b]  [dim]severity-coloured status messages[/dim]",
                classes="crd-section",
            )
            with Horizontal(classes="crd-row"):
                yield AlertCard(
                    "info", "Maintenance window",
                    "Scheduled downtime tonight 02:00–04:00 UTC. No action required.",
                )
                yield AlertCard(
                    "success", "Deployment complete",
                    "Release v2.4.1 rolled out to all nodes without errors.",
                )
                yield AlertCard(
                    "warning", "Disk space low",
                    "Node gpu-07 at 87 % capacity — consider pruning old checkpoints.",
                )
                yield AlertCard(
                    "error", "Job wi-039 failed",
                    "OOM error during preprocessing step 3. Check node memory limits.",
                )

            # ── Profile cards ─────────────────────────────────────
            yield Static(
                "[b]Profile Cards[/b]  [dim]person / entity with avatar, bio, and tags[/dim]",
                classes="crd-section",
            )
            with Horizontal(classes="crd-row"):
                yield ProfileCard(
                    "Alice Chen", "ML Engineer · JHU",
                    "Specialises in training pipeline optimisation and distributed workloads.",
                    ["pytorch", "distributed", "gpu"],
                )
                yield ProfileCard(
                    "Bob Nguyen", "DevOps · UNC",
                    "Owns the Kubernetes cluster and CI/CD pipelines for the platform.",
                    ["k8s", "terraform", "ci-cd"],
                )
                yield ProfileCard(
                    "Carol Smith", "Data Scientist · Mayo",
                    "Leads the clinical NLP initiative and model validation workflows.",
                    ["nlp", "clinical", "validation"],
                )

            # ── Progress cards ────────────────────────────────────
            yield Static(
                "[b]Progress Cards[/b]  [dim]task / quota with a progress bar[/dim]",
                classes="crd-section",
            )
            with Horizontal(classes="crd-row"):
                yield ProgressCard(
                    "Training — wi-101", 72,
                    subtitle="Epoch 72 of 100",
                    footer="ETA ~18 min  ·  gpu-node-03",
                )
                yield ProgressCard(
                    "Storage quota", 55,
                    subtitle="55 GB of 100 GB used",
                    footer="45 GB remaining",
                )
                yield ProgressCard(
                    "Monthly API budget", 91,
                    subtitle="91 % consumed",
                    footer="[red]Approaching limit[/red]",
                )
                yield ProgressCard(
                    "Onboarding checklist", 40,
                    subtitle="2 of 5 steps complete",
                    footer="Next: invite team members",
                )

            # ── Action cards ──────────────────────────────────────
            yield Static(
                "[b]Action Cards[/b]  [dim]call-to-action with one or two buttons[/dim]",
                classes="crd-section",
            )
            with Horizontal(classes="crd-row"):
                yield ActionCard(
                    "Deploy to Production",
                    "Release v2.4.1 has passed all staging checks and is ready to promote.",
                    "Deploy", "View diff",
                )
                yield ActionCard(
                    "Invite team member",
                    "Add a colleague to your tenant workspace and assign a role.",
                    "Send invite",
                )
                yield ActionCard(
                    "Export results",
                    "Download job wi-037 outputs as a compressed archive (1.2 GB).",
                    "Export", "Preview",
                )

            # ── Key-value cards ───────────────────────────────────
            yield Static(
                "[b]Key-Value Cards[/b]  [dim]structured data summary[/dim]",
                classes="crd-section",
            )
            with Horizontal(classes="crd-row"):
                yield KVCard("Job wi-042", [
                    ("Status",      "[green]Done[/green]"),
                    ("Type",        "Training"),
                    ("Duration",    "4m 12s"),
                    ("Node",        "gpu-node-04"),
                    ("Tenant",      "JHU"),
                    ("Submitted",   "alice@jhu.edu"),
                ])
                yield KVCard("Cluster health", [
                    ("Nodes online",  "[green]8 / 8[/green]"),
                    ("GPU util avg",  "64 %"),
                    ("Memory free",   "142 GB"),
                    ("Queue depth",   "14 jobs"),
                    ("Errors (24 h)", "[red]3[/red]"),
                    ("Uptime",        "99.6 %"),
                ])
                yield KVCard("Tenant · Mayo", [
                    ("Plan",          "Enterprise"),
                    ("Users",         "12 active"),
                    ("Jobs today",    "47"),
                    ("Storage used",  "55 GB"),
                    ("API calls",     "18,240"),
                    ("Next renewal",  "2026-08-01"),
                ])

        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

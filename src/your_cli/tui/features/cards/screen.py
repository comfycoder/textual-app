"""Demo: Card patterns — five composable card styles built with compose()."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from your_cli.tui.widgets import ActionCard, AlertCard, KVCard, ProfileCard, ProgressCard

# ── Demo screen ───────────────────────────────────────────────────────────────

class CardsDemoScreen(Screen[None]):
    """Five composable card patterns: alert, profile, progress, action, key-value."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

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

"""Demo: Custom reusable widgets — MetricCard and StatusBadge."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Button, Footer, Header, Static

from your_cli.tui.widgets import MetricCard, StatusBadge


class CustomWidgetDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("r",      "randomise", "Randomise"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="custom-body"):
            yield Static("[b]MetricCard[/b]  — reusable KPI widget", classes="demo-label")
            with Horizontal(id="metric-row"):
                yield MetricCard("Jobs completed", "4,821", trend="up",   detail="↑ 12% vs last month", id="mc-jobs")
                yield MetricCard("Success rate",   "97.4%", trend="up",   detail="↑ 0.8pp",             id="mc-success")
                yield MetricCard("Avg duration",   "4m 32s",trend="down", detail="↓ 18s faster",        id="mc-duration")
                yield MetricCard("Queue depth",    "14",    trend="flat", detail="no change",            id="mc-queue")
            yield Static("\n[b]StatusBadge[/b]  — inline status pill", classes="demo-label")
            with Horizontal(id="badge-row", classes="demo-row"):
                yield Static("API gateway  ")
                yield StatusBadge("healthy",  id="badge-api")
                yield Static("  Worker pool  ")
                yield StatusBadge("degraded", id="badge-workers")
                yield Static("  Storage  ")
                yield StatusBadge("healthy",  id="badge-storage")
                yield Static("  Auth service  ")
                yield StatusBadge("down",     id="badge-auth")
            yield Static(
                "\n[b]Live update[/b]  — reactive attributes re-render without touching the DOM",
                classes="demo-label",
            )
            yield Button("Randomise values  (R)", variant="primary", id="btn-randomise")
        yield Footer()

    def action_randomise(self) -> None:
        trends   = ["up", "down", "flat"]
        statuses = ["healthy", "degraded", "down", "unknown"]
        self.query_one("#mc-jobs",     MetricCard).value = f"{random.randint(3_000, 6_000):,}"
        self.query_one("#mc-success",  MetricCard).value = f"{random.uniform(92, 99.9):.1f}%"
        self.query_one("#mc-duration", MetricCard).value = f"{random.randint(2, 9)}m {random.randint(0, 59):02d}s"
        self.query_one("#mc-queue",    MetricCard).value = str(random.randint(0, 150))
        for mc_id in ("#mc-jobs", "#mc-success", "#mc-duration", "#mc-queue"):
            self.query_one(mc_id, MetricCard).trend = random.choice(trends)
        for badge_id in ("#badge-api", "#badge-workers", "#badge-storage", "#badge-auth"):
            self.query_one(badge_id, StatusBadge).status = random.choice(statuses)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-randomise":
            self.action_randomise()


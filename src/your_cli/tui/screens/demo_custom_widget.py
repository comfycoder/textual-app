"""Demo: Custom reusable widgets — MetricCard and StatusBadge."""

import random
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Static


class MetricCard(Widget):
    """Reusable KPI card: title, value, trend arrow, and detail line.

    Reactives re-render automatically — no explicit watchers needed.
    """

    DEFAULT_CSS: ClassVar[str] = """
    MetricCard {
        height: 7;
        border: solid $primary;
        padding: 1 2;
        width: 1fr;
        content-align: center middle;
    }
    MetricCard:hover {
        border: solid $accent;
    }
    """

    title:  reactive[str] = reactive("")
    value:  reactive[str] = reactive("")
    trend:  reactive[str] = reactive("flat")   # "up" | "down" | "flat"
    detail: reactive[str] = reactive("")

    def __init__(
        self,
        title: str,
        value: str,
        trend: str = "flat",
        detail: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title  = title
        self.value  = value
        self.trend  = trend
        self.detail = detail

    def render(self) -> str:
        icons = {"up": "[green]↑[/green]", "down": "[red]↓[/red]", "flat": "[dim]→[/dim]"}
        icon = icons.get(self.trend, "")
        lines = [
            f"[dim]{self.title}[/dim]",
            f"[b]{self.value}[/b]  {icon}",
        ]
        if self.detail:
            lines.append(f"[dim]{self.detail}[/dim]")
        return "\n".join(lines)


class StatusBadge(Widget):
    """Inline status pill with colour-coded indicator dot."""

    DEFAULT_CSS: ClassVar[str] = """
    StatusBadge {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    """

    _COLORS: ClassVar[dict[str, str]] = {
        "healthy":  "green",
        "degraded": "yellow",
        "down":     "red",
        "unknown":  "dim",
    }

    status: reactive[str] = reactive("unknown")

    def __init__(self, status: str = "unknown", **kwargs) -> None:
        super().__init__(**kwargs)
        self.status = status

    def render(self) -> str:
        color = self._COLORS.get(self.status, "white")
        return f"[{color}]● {self.status}[/{color}]"


class CustomWidgetDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "go_back",    "Back"),
        Binding("r",      "randomise",  "Randomise"),
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

    def action_go_back(self) -> None:
        self.app.pop_screen()

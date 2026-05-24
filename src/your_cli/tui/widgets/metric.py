"""MetricCard — reusable KPI card with reactive value, trend, and detail."""

from typing import Any, ClassVar

from textual.reactive import reactive
from textual.widget import Widget


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
        **kwargs: Any,
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

"""TimelineCard — vertical sequence of timestamped steps with status icons."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Rule, Static


class TimelineCard(Widget):
    """Vertical sequence of timestamped steps with status icons.

    Each step is a (time, label, status) tuple where status is one of:
    "done" | "active" | "pending" | "error"
    """

    DEFAULT_CSS: ClassVar[str] = """
    TimelineCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    TimelineCard:hover { border: round $accent; }

    TimelineCard .tlc-title  { text-style: bold; color: $accent; margin-bottom: 1; }
    TimelineCard .tlc-step   { height: 1; }
    TimelineCard .tlc-time   { width: 7; color: $text-muted; }
    TimelineCard .tlc-icon   { width: 3; }
    TimelineCard .tlc-label  { width: 1fr; }
    """

    _ICONS: ClassVar[dict[str, str]] = {
        "done":    "[green]✓[/green]",
        "active":  "[yellow]●[/yellow]",
        "pending": "[dim]○[/dim]",
        "error":   "[red]✗[/red]",
    }

    def __init__(
        self,
        title: str,
        steps: list[tuple[str, str, str]],   # (time, label, status)
        **kw: Any,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._steps = steps

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="tlc-title")
        yield Rule(line_style="dashed")
        for time, label, status in self._steps:
            icon = self._ICONS.get(status, "[dim]○[/dim]")
            with Horizontal(classes="tlc-step"):
                yield Static(time,  classes="tlc-time",  markup=True)
                yield Static(icon,  classes="tlc-icon",  markup=True)
                yield Static(label, classes="tlc-label")

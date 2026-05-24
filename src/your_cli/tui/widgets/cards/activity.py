"""ActivityCard — recent-activity feed with icons and timestamps."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Rule, Static


class ActivityCard(Widget):
    """Recent-activity feed: icon, actor/event, and relative timestamp."""

    DEFAULT_CSS: ClassVar[str] = """
    ActivityCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ActivityCard:hover { border: round $accent; }

    ActivityCard .acc-title  { text-style: bold; color: $accent; margin-bottom: 1; }
    ActivityCard .acc-item   { height: 1; margin-bottom: 0; }
    ActivityCard .acc-icon   { width: 3; }
    ActivityCard .acc-text   { width: 1fr; }
    ActivityCard .acc-time   { width: 10; color: $text-muted; text-align: right; }
    """

    _KIND_ICON: ClassVar[dict[str, str]] = {
        "success": "[green]✓[/green]",
        "error":   "[red]✗[/red]",
        "warning": "[yellow]⚠[/yellow]",
        "info":    "[cyan]ℹ[/cyan]",
        "user":    "[blue]●[/blue]",
    }

    def __init__(
        self,
        title: str,
        items: list[tuple[str, str, str]],   # (kind, text, relative_time)
        **kw: Any,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._items = items

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="acc-title")
        yield Rule(line_style="dashed")
        for kind, text, when in self._items:
            icon = self._KIND_ICON.get(kind, "[dim]●[/dim]")
            with Horizontal(classes="acc-item"):
                yield Static(icon, classes="acc-icon", markup=True)
                yield Static(text, classes="acc-text")
                yield Static(when, classes="acc-time")

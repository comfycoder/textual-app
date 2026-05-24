"""SparklineCard — card embedding a Sparkline widget with summary stats."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Sparkline, Static


class SparklineCard(Widget):
    """Card embedding a Sparkline widget with a title and summary stats."""

    DEFAULT_CSS: ClassVar[str] = """
    SparklineCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    SparklineCard:hover { border: round $accent; }

    SparklineCard .slc-title    { text-style: bold; color: $accent; margin-bottom: 1; }
    SparklineCard Sparkline     { height: 4; width: 1fr; margin-bottom: 1; }
    SparklineCard .slc-stats    { height: auto; }
    SparklineCard .slc-stat     { width: 1fr; text-align: center; }
    SparklineCard .slc-stat-val { text-style: bold; color: $foreground; }
    SparklineCard .slc-stat-lbl { color: $text-muted; }
    """

    def __init__(
        self,
        title: str,
        data: list[float],
        stats: list[tuple[str, str]],   # (label, formatted_value)
        **kw: Any,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._data  = data
        self._stats = stats

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="slc-title")
        yield Sparkline(self._data)
        with Horizontal(classes="slc-stats"):
            for label, value in self._stats:
                with Vertical(classes="slc-stat"):
                    yield Static(value, classes="slc-stat-val")
                    yield Static(label, classes="slc-stat-lbl")

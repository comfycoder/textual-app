"""ProgressCard — task / quota card with a labeled progress bar."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import ProgressBar, Static


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
        **kw: Any,
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

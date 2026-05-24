"""ComparisonCard — side-by-side two-option comparison table."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Rule, Static


class ComparisonCard(Widget):
    """Side-by-side plan / option comparison table."""

    DEFAULT_CSS: ClassVar[str] = """
    ComparisonCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ComparisonCard:hover { border: round $accent; }

    ComparisonCard .cmc-title   { text-style: bold; color: $accent; margin-bottom: 1; }
    ComparisonCard .cmc-header  { height: 1; }
    ComparisonCard .cmc-spacer  { width: 1fr; }
    ComparisonCard .cmc-col-a   { width: 14; text-style: bold; color: $primary; text-align: center; }
    ComparisonCard .cmc-col-b   { width: 14; text-style: bold; color: $accent;  text-align: center; }
    ComparisonCard .cmc-row     { height: 1; }
    ComparisonCard .cmc-label   { width: 1fr; color: $text-muted; }
    ComparisonCard .cmc-val-a   { width: 14; text-align: center; }
    ComparisonCard .cmc-val-b   { width: 14; text-align: center; color: $accent; }
    """

    def __init__(
        self,
        title: str,
        col_a: str,
        col_b: str,
        rows: list[tuple[str, str, str]],   # (label, value_a, value_b)
        **kw: Any,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._col_a = col_a
        self._col_b = col_b
        self._rows  = rows

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="cmc-title")
        with Horizontal(classes="cmc-header"):
            yield Static("",          classes="cmc-spacer")
            yield Static(self._col_a, classes="cmc-col-a")
            yield Static(self._col_b, classes="cmc-col-b")
        yield Rule(line_style="dashed")
        for label, val_a, val_b in self._rows:
            with Horizontal(classes="cmc-row"):
                yield Static(label, classes="cmc-label")
                yield Static(val_a, classes="cmc-val-a", markup=True)
                yield Static(val_b, classes="cmc-val-b", markup=True)

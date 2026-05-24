"""ActionCard — call-to-action card with one or two buttons."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Rule, Static


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
        **kw: Any,
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

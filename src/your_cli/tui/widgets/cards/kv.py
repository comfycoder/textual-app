"""KVCard — key-value summary card."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Rule, Static


class KVCard(Widget):
    """Key-value summary card: title plus a list of label → value pairs."""

    DEFAULT_CSS: ClassVar[str] = """
    KVCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    KVCard:hover { border: round $accent; }

    KVCard .kvc-title    { text-style: bold; color: $accent; margin-bottom: 1; }
    KVCard .kvc-row      { height: auto; margin-bottom: 0; }
    KVCard .kvc-key      { width: 16; color: $text-muted; }
    KVCard .kvc-value    { width: 1fr; }
    """

    def __init__(self, title: str, items: list[tuple[str, str]], **kw: Any) -> None:
        super().__init__(**kw)
        self._title = title
        self._items = items

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="kvc-title")
        yield Rule(line_style="dashed")
        for key, value in self._items:
            with Horizontal(classes="kvc-row"):
                yield Static(key, classes="kvc-key")
                yield Static(value, classes="kvc-value")

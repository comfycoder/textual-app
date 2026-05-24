"""AlertCard — severity-coloured card with a left accent border."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class AlertCard(Widget):
    """Severity-coloured card with a left accent border.

    severity: "info" | "success" | "warning" | "error"
    """

    DEFAULT_CSS: ClassVar[str] = """
    AlertCard {
        height: auto;
        width: 1fr;
        padding: 1 2;
        background: $boost;
    }
    AlertCard.-info    { border-left: outer $primary; }
    AlertCard.-success { border-left: outer $success; }
    AlertCard.-warning { border-left: outer $warning; }
    AlertCard.-error   { border-left: outer $error;   }

    AlertCard .alert-title { text-style: bold; margin-bottom: 1; }
    AlertCard.-info    .alert-title { color: $primary; }
    AlertCard.-success .alert-title { color: $success; }
    AlertCard.-warning .alert-title { color: $warning; }
    AlertCard.-error   .alert-title { color: $error;   }
    """

    _ICONS: ClassVar[dict[str, str]] = {
        "info":    "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error":   "✗",
    }

    def __init__(self, severity: str, title: str, body: str, **kw: Any) -> None:
        existing = kw.pop("classes", "")
        super().__init__(classes=f"-{severity} {existing}".strip(), **kw)
        self._severity = severity
        self._title    = title
        self._body     = body

    def compose(self) -> ComposeResult:
        icon = self._ICONS.get(self._severity, "•")
        yield Static(f"{icon}  {self._title}", classes="alert-title")
        yield Static(self._body)

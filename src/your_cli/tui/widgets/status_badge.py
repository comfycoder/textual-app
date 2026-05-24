"""StatusBadge — inline status pill with colour-coded indicator dot."""

from typing import Any, ClassVar

from textual.reactive import reactive
from textual.widget import Widget


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

    def __init__(self, status: str = "unknown", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.status = status

    def render(self) -> str:
        color = self._COLORS.get(self.status, "white")
        return f"[{color}]● {self.status}[/{color}]"

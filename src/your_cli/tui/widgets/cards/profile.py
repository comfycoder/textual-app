"""ProfileCard — person / entity card with avatar, bio, and tags."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Rule, Static


class ProfileCard(Widget):
    """Person / entity card: avatar initial, name, role, bio, and tags."""

    DEFAULT_CSS: ClassVar[str] = """
    ProfileCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ProfileCard:hover { border: round $accent; }

    ProfileCard .prc-header  { height: auto; align: left middle; }
    ProfileCard .prc-avatar  {
        width: 5;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $background;
        text-style: bold;
        margin-right: 1;
    }
    ProfileCard .prc-name    { text-style: bold; }
    ProfileCard .prc-role    { color: $text-muted; }
    ProfileCard .prc-bio     { margin-top: 1; }
    ProfileCard .prc-tags    { margin-top: 1; color: $accent; }
    """

    def __init__(self, name: str, role: str, bio: str, tags: list[str], **kw: Any) -> None:
        super().__init__(**kw)
        self._display_name: str = name
        self._role = role
        self._bio  = bio
        self._tags = tags

    def compose(self) -> ComposeResult:
        initial = self._display_name[0].upper() if self._display_name else "?"
        with Horizontal(classes="prc-header"):
            yield Static(initial, classes="prc-avatar")
            with Vertical():
                yield Static(self._display_name, classes="prc-name")
                yield Static(self._role, classes="prc-role")
        yield Rule(line_style="dashed")
        yield Static(self._bio, classes="prc-bio")
        if self._tags:
            yield Static(
                "  ".join(f"[b]#{t}[/b]" for t in self._tags),
                classes="prc-tags",
                markup=True,
            )

"""Reusable pagination control bar widget.

Encapsulates the First / Prev / [page N of M] / Next / Last navigation row
that was previously duplicated in every paginated screen.

Usage::

    # In compose():
    yield PaginationBar(id="my-pbar")

    # After any page change — call update() to sync button states and label:
    self.query_one(PaginationBar).update(self._pager)

    # React to user clicks:
    def on_pagination_bar_navigated(self, event: PaginationBar.Navigated) -> None:
        if getattr(self._pager, event.action)():   # first/prev/next/last
            self._load_page()
"""

from __future__ import annotations

from typing import Literal

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Static

from your_cli.tui.paginator import Paginator


class PaginationBar(Widget):
    """Four-button pagination row that posts ``Navigated`` messages upward.

    The widget owns its own buttons and page-label; callers drive it by
    passing a ``Paginator`` to ``update()``.  Button presses are consumed
    here (``event.stop()``) so they never reach the screen's
    ``on_button_pressed``.
    """

    DEFAULT_CSS = """
    PaginationBar {
        height: auto;
        width: 1fr;
        layout: horizontal;
        align: left middle;
    }
    PaginationBar > #pgbar-label {
        width: 1fr;
        height: 3;
        padding: 0 2;
        content-align: center middle;
        color: $text-muted;
    }
    """

    class Navigated(Message):
        """Posted when the user clicks First / Prev / Next / Last.

        ``event.action`` is one of ``"first"``, ``"prev"``, ``"next"``,
        ``"last"`` — matching the ``Paginator`` method names, so callers can
        use ``getattr(pager, event.action)()``.
        """

        def __init__(self, action: Literal["first", "prev", "next", "last"]) -> None:
            super().__init__()
            self.action = action

    def compose(self) -> ComposeResult:
        yield Button("|◀ First", id="pgbar-first", disabled=True)
        yield Button("◀ Prev",   id="pgbar-prev",  disabled=True)
        yield Static("",         id="pgbar-label")
        yield Button("Next ▶",   id="pgbar-next",  disabled=True)
        yield Button("Last ▶|",  id="pgbar-last",  disabled=True)

    def update(self, pager: Paginator) -> None:
        """Sync button states and label text from *pager*.

        Call this after every navigation action that may have changed the
        page, or after a data reload that changes ``pager.total``.
        """
        total      = pager.total
        start, end = pager.slice()
        if total:
            row_info = f"  [dim](rows {start + 1}–{min(end, total)} of {total})[/dim]"
        else:
            row_info = "  [dim](no results)[/dim]"
        self.query_one("#pgbar-label", Static).update(
            f"Page [b]{pager.display_page}[/b] of [b]{pager.page_count}[/b]{row_info}"
        )
        self.query_one("#pgbar-first", Button).disabled = pager.at_first
        self.query_one("#pgbar-prev",  Button).disabled = pager.at_first
        self.query_one("#pgbar-next",  Button).disabled = pager.at_last
        self.query_one("#pgbar-last",  Button).disabled = pager.at_last

    def on_button_pressed(self, event: Button.Pressed) -> None:
        _MAP: dict[str, Literal["first", "prev", "next", "last"]] = {
            "pgbar-first": "first",
            "pgbar-prev":  "prev",
            "pgbar-next":  "next",
            "pgbar-last":  "last",
        }
        action = _MAP.get(event.button.id or "")
        if action:
            event.stop()  # don't bubble to the screen's on_button_pressed
            self.post_message(self.Navigated(action))

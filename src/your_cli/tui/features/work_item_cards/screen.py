"""Demo: Work Item Cards — status-coloured cards with drill-down to detail.

Shows a 3-column grid of work item cards.  Each card is focusable and
clickable; pressing Enter or clicking opens the full detail screen.

Filtering by status, type, and priority hides non-matching cards in place —
no re-mount required.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, Select, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.features.search_grid._data import (
    _PRIORITY_OPTS,
    _RECORDS,
    _STATUS_OPTS,
    _TYPE_OPTS,
)
from your_cli.tui.features.work_item_cards.detail import WorkItemDetailScreen
from your_cli.tui.palette import PRI_COLORS, STATUS_COLORS

__all__ = ["WorkItemCardsScreen"]

# First 30 records — enough variety for a demo, fast to render
_DEMO_RECORDS: list[dict[str, Any]] = _RECORDS[:30]


# ── Card widget ───────────────────────────────────────────────────────────────

class WorkItemCard(Widget):
    """Focusable, clickable card for a single work item.

    Posts ``WorkItemCard.Pressed`` when activated by mouse click or
    Enter / Space.  The ``control`` property follows Textual's message
    convention (same pattern as ``Button.Pressed``).
    """

    can_focus = True

    DEFAULT_CSS = """
    WorkItemCard {
        height: 9;
        padding: 1 2;
        width: 1fr;
    }
    """

    class Pressed(Message):
        """Posted when this card is clicked or activated by keyboard."""

        def __init__(self, card: "WorkItemCard") -> None:
            super().__init__()
            self._card = card

        @property
        def control(self) -> "WorkItemCard":
            """The ``WorkItemCard`` that posted this message."""
            return self._card

    def __init__(self, record: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._record = record

    @property
    def record(self) -> dict[str, Any]:
        """The underlying work item dict."""
        return self._record

    def render(self) -> str:
        rec       = self._record
        sc        = STATUS_COLORS.get(rec["status"], "white")
        pc        = PRI_COLORS.get(rec["priority"], "white")
        env_label = {"prod": "PROD", "staging": "STG", "dev": "DEV"}.get(
            rec["environment"], rec["environment"].upper()
        )
        return "\n".join([
            f"[b]{rec['id']}[/b]",
            f"[{sc}]● {rec['status'].upper()}[/{sc}]  [{pc}]{rec['priority']}[/{pc}]",
            f"[dim]{rec['type']}[/dim]",
            f"[dim]{rec['tenant'].upper()}  ·  {env_label}[/dim]",
            "[dim]↵ to open detail[/dim]",
        ])

    def _flash(self) -> None:
        """Add the pressed CSS class briefly, then remove it."""
        self.add_class("wic-pressing")
        self.set_timer(0.15, lambda: self.remove_class("wic-pressing"))

    def on_click(self) -> None:
        self._flash()
        self.post_message(self.Pressed(self))

    def on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "space"):
            event.stop()
            self._flash()
            self.post_message(self.Pressed(self))


# ── Main screen ───────────────────────────────────────────────────────────────

class WorkItemCardsScreen(FeatureScreen):
    """Card grid view of work items with status-based colour coding and drill-down."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("ctrl+f", "focus_filter", "Filter"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._all_records: list[dict[str, Any]] = list(_DEMO_RECORDS)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wic-body"):

            # ── Filter bar ────────────────────────────────────────
            with Horizontal(id="wic-filter-bar"):
                with Vertical(classes="wic-filter-field"):
                    yield Label("Status")
                    yield Select(_STATUS_OPTS, prompt="All statuses", id="wic-status")
                with Vertical(classes="wic-filter-field"):
                    yield Label("Type")
                    yield Select(_TYPE_OPTS, prompt="All types", id="wic-type")
                with Vertical(classes="wic-filter-field"):
                    yield Label("Priority")
                    yield Select(_PRIORITY_OPTS, prompt="All priorities", id="wic-priority")

            yield Static("", id="wic-summary")

            # ── Card grid ─────────────────────────────────────────
            with ScrollableContainer(id="wic-scroll"):
                with Vertical(id="wic-grid"):
                    for rec in self._all_records:
                        yield WorkItemCard(
                            rec,
                            classes="wic-card",
                            id=f"card-{rec['id']}",
                        )

        yield Footer()

    def on_mount(self) -> None:
        self._update_summary(len(self._all_records))
        # Focus the first card so keyboard nav works immediately
        cards = list(self.query(WorkItemCard))
        if cards:
            cards[0].focus()

    # ── Filter logic ──────────────────────────────────────────────

    def _apply_filters(self) -> None:
        status = self.query_one("#wic-status",   Select).value
        wtype  = self.query_one("#wic-type",     Select).value
        pri    = self.query_one("#wic-priority", Select).value

        shown = 0
        for card in self.query(WorkItemCard):
            rec     = card.record
            visible = (
                (not isinstance(status, str) or rec["status"]   == status) and
                (not isinstance(wtype,  str) or rec["type"]     == wtype)  and
                (not isinstance(pri,    str) or rec["priority"] == pri)
            )
            card.display = visible
            if visible:
                shown += 1

        self._update_summary(shown)

        # Re-focus first visible card after filter
        for card in self.query(WorkItemCard):
            if card.display:
                card.focus()
                break

    def _update_summary(self, shown: int) -> None:
        total = len(self._all_records)
        if shown == total:
            msg = f"[dim]Showing all [b]{total}[/b] work items  ·  click or [b]Enter[/b] to open detail[/dim]"
        else:
            msg = f"[dim]Showing [b]{shown}[/b] of {total} work items  ·  click or [b]Enter[/b] to open detail[/dim]"
        self.query_one("#wic-summary", Static).update(msg)

    # ── Event handlers ────────────────────────────────────────────

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id in ("wic-status", "wic-type", "wic-priority"):
            self._apply_filters()

    def on_work_item_card_pressed(self, event: WorkItemCard.Pressed) -> None:
        self.app.push_screen(WorkItemDetailScreen(event.control.record))

    # ── Actions ───────────────────────────────────────────────────

    def action_focus_filter(self) -> None:
        self.query_one("#wic-status", Select).focus()

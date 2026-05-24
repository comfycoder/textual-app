"""Demo: Auto-refreshing dashboard using set_interval and workers.

The _fake_api_fetch function simulates an httpx call — swap it for your
real OpenAPI client when ready.
"""

import asyncio
import random
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from typing import Any

from textual.widgets import Button, DataTable, Footer, Header, Label, Static

REFRESH_SECONDS = 10

_STATUS_COLORS = {
    "queued":  "yellow",
    "running": "cyan",
    "done":    "green",
    "failed":  "red",
    "pending": "dim",
}

_BASE_ITEMS = [
    {"id": "wi-001", "tenant": "jhu"},
    {"id": "wi-002", "tenant": "unc"},
    {"id": "wi-003", "tenant": "mayo"},
    {"id": "wi-004", "tenant": "jhu"},
    {"id": "wi-005", "tenant": "unc"},
]


async def _fake_api_fetch() -> list[dict[str, Any]]:
    """Simulated API call — replace with real httpx call."""
    await asyncio.sleep(0.4)
    now = datetime.now().strftime("%H:%M:%S")
    statuses = list(_STATUS_COLORS.keys())
    return [
        {**item, "status": random.choice(statuses), "updated": now}
        for item in _BASE_ITEMS
    ]


def _markup_status(status: str) -> str:
    color = _STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


class LiveDashboardScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("r", "manual_refresh", "Refresh"),
    ]

    _countdown: reactive[int] = reactive(REFRESH_SECONDS)
    _refreshing: reactive[bool] = reactive(False)
    _last_updated: reactive[str] = reactive("—")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="live-status-bar"):
            yield Label("", id="live-indicator")
            yield Static("", id="live-last-updated")
            yield Static("", id="live-countdown")
            yield Button("Refresh Now", variant="primary", id="btn-refresh", classes="refresh-btn")
        yield DataTable(id="live-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Tenant", "Updated")
        self.set_interval(1.0, self._tick)
        self._fetch()

    # ── Countdown & auto-refresh ──────────────────────────────────────────────

    def _tick(self) -> None:
        if self._refreshing:
            return
        self._countdown -= 1
        if self._countdown <= 0:
            self._countdown = REFRESH_SECONDS
            self._fetch()

    def watch__countdown(self, value: int) -> None:
        self.query_one("#live-countdown", Static).update(
            f"  Next refresh in [b]{value}[/b]s"
        )

    def watch__refreshing(self, refreshing: bool) -> None:
        indicator = self.query_one("#live-indicator", Label)
        btn = self.query_one("#btn-refresh", Button)
        if refreshing:
            indicator.update("[yellow]⟳[/yellow] Refreshing…")
            btn.disabled = True
        else:
            indicator.update("[green]●[/green] Live")
            btn.disabled = False

    def watch__last_updated(self, value: str) -> None:
        self.query_one("#live-last-updated", Static).update(
            f"  Last updated: [b]{value}[/b]"
        )

    # ── Data fetch ────────────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _fetch(self) -> None:
        self._refreshing = True
        try:
            items = await _fake_api_fetch()
            table = self.query_one(DataTable)
            table.clear()
            for item in items:
                table.add_row(
                    item["id"],
                    _markup_status(item["status"]),
                    item["tenant"],
                    item["updated"],
                )
            self._last_updated = datetime.now().strftime("%H:%M:%S")
            self._countdown = REFRESH_SECONDS
        finally:
            self._refreshing = False

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_manual_refresh(self) -> None:
        self._countdown = REFRESH_SECONDS
        self._fetch()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refresh":
            self.action_manual_refresh()

    def action_go_back(self) -> None:
        self.app.pop_screen()

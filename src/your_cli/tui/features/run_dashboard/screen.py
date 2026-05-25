"""Demo: Run Dashboard — multi-tenant live polling via Repository.

Domain-specific counterpart to the generic live_dashboard demo.
Demonstrates:
  • asyncio.gather() to fetch all four tenants concurrently in a single poll
  • Repository.get_recent_runs() instead of a local fake generator
  • 2 × 2 grid layout — one DataTable per tenant
  • set_interval() + @work(exclusive=True) for non-blocking auto-refresh
  • Reactive countdown label (same pattern as live_dashboard)
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Footer, Header, Label, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.palette import STATUS_COLORS

__all__ = ["RunDashboardScreen"]

_TENANTS     = ["jhu", "unc", "mayo", "stanford"]
_LIMIT       = 5          # most-recent runs shown per tenant
_REFRESH_SEC = 10         # auto-refresh interval

# Column specs: (header, key, width)
_COLS: list[tuple[str, str, int]] = [
    ("Run ID",    "run_id",    12),
    ("Status",    "status",     9),
    ("Submitted", "submitted", 11),
]


class RunDashboardScreen(FeatureScreen):
    """Four-pane dashboard: most-recent Runs for each tenant, live-polled."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("r", "refresh_now", "Refresh"),
    ]

    _countdown:  reactive[int]  = reactive(_REFRESH_SEC)
    _refreshing: reactive[bool] = reactive(False)

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="rd-body"):

            # ── Top bar ───────────────────────────────────────────
            with Horizontal(id="rd-topbar"):
                yield Label("", id="rd-indicator")
                yield Static("", id="rd-last-updated")
                yield Static("", id="rd-countdown")
                yield Button(
                    "⟳ Refresh now",
                    variant="primary",
                    id="btn-rd-refresh",
                    classes="rd-refresh-btn",
                )

            # ── 2 × 2 tenant grid ─────────────────────────────────
            with Horizontal(id="rd-grid"):
                for tenant in _TENANTS:
                    with Vertical(classes="rd-panel", id=f"rd-panel-{tenant}"):
                        yield Static(
                            f"[b]{tenant.upper()}[/b]  "
                            f"[dim]last {_LIMIT} runs[/dim]",
                            classes="rd-panel-title",
                        )
                        yield DataTable(
                            id=f"rd-table-{tenant}",
                            cursor_type="row",
                            zebra_stripes=True,
                        )

        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        for tenant in _TENANTS:
            tbl = self.query_one(f"#rd-table-{tenant}", DataTable)
            for label, key, width in _COLS:
                tbl.add_column(label, key=key, width=width)

        self._poll()                       # immediate first load
        self.set_interval(1.0, self._tick) # countdown ticker
        self.set_interval(_REFRESH_SEC, self._poll)  # auto-refresh

    # ── Countdown ──────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if not self._refreshing:
            self._countdown = max(0, self._countdown - 1)

    def watch__countdown(self, value: int) -> None:
        self.query_one("#rd-countdown", Static).update(
            f"  [dim]Next refresh in[/dim] [b]{value}[/b][dim]s[/dim]"
        )

    def watch__refreshing(self, refreshing: bool) -> None:
        indicator = self.query_one("#rd-indicator", Label)
        btn       = self.query_one("#btn-rd-refresh", Button)
        if refreshing:
            indicator.update("[yellow]⟳[/yellow] Refreshing…")
            btn.disabled = True
        else:
            indicator.update("[green]●[/green] Live")
            btn.disabled = False

    # ── Data fetch ─────────────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _poll(self) -> None:
        """Fetch the most-recent Runs for all tenants concurrently."""
        self._refreshing = True
        try:
            repo = getattr(self.app, "repository")
            # One gather call — all four tenant requests fire simultaneously.
            results = await asyncio.gather(
                *[repo.get_recent_runs(t, _LIMIT) for t in _TENANTS],
                return_exceptions=True,
            )

            for tenant, runs_or_exc in zip(_TENANTS, results):
                tbl = self.query_one(f"#rd-table-{tenant}", DataTable)
                tbl.clear()
                if isinstance(runs_or_exc, Exception):
                    tbl.add_row(Text(f"Error: {runs_or_exc}", style="red"))
                    continue
                for run in runs_or_exc:
                    color = STATUS_COLORS.get(run.status, "dim")
                    tbl.add_row(
                        Text(run.run_id),
                        Text(run.status, style=color),
                        Text(run.submitted_at.strftime("%m-%d %H:%M")),
                        key=run.run_id,
                    )

            now = datetime.now(timezone.utc).strftime("%H:%M:%S")
            self.query_one("#rd-last-updated", Static).update(
                f"  [dim]Updated[/dim] [b]{now} UTC[/b]"
            )
            self._countdown = _REFRESH_SEC

        finally:
            self._refreshing = False

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_refresh_now(self) -> None:
        self._countdown = _REFRESH_SEC
        self._poll()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-rd-refresh":
            self.action_refresh_now()

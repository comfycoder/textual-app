"""Demo: Run History Browser — paginated Runs with date-range filter from Repository.

Exercises Repository.get_runs() (server-side pagination) and demonstrates:
  - MaskedInput for structured date entry
  - @work async worker for non-blocking API calls
  - PaginationBar driving server-side pages
  - STATUS_COLORS for coloured run status text
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    MaskedInput,
    Select,
    Static,
)

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.paginator import Paginator
from your_cli.tui.palette import STATUS_COLORS
from your_cli.tui.widgets import PaginationBar

__all__ = ["RunHistoryScreen"]

# ── Constants ──────────────────────────────────────────────────────────────────

_TENANTS = [("JHU", "jhu"), ("UNC", "unc"), ("Mayo", "mayo"), ("Stanford", "stanford")]
_PAGE_SIZE = 15
_TODAY = date(2026, 5, 25)
_DEFAULT_FROM = _TODAY - timedelta(days=30)

_COLUMNS: list[tuple[str, str, int]] = [
    ("Run ID",       "run_id",       14),
    ("Status",       "status",       10),
    ("Submitted At", "submitted_at", 22),
    ("Rerun Of",     "parent",       14),
]


# ── Screen ─────────────────────────────────────────────────────────────────────

class RunHistoryScreen(FeatureScreen):
    """Paginated list of Runs for a chosen tenant and date range.

    Data comes from ``self.app.repository.get_runs()`` via a ``@work`` async
    worker so the UI stays responsive during the (simulated) network call.
    """

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("ctrl+r", "search", "Search"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._pager: Paginator = Paginator(total=0, page_size=_PAGE_SIZE)
        self._col_keys: dict[str, Any] = {}

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="rh-body"):

            # ── Filter bar ────────────────────────────────────────
            with Horizontal(id="rh-filters"):
                with Vertical(classes="rh-filter-field"):
                    yield Label("Tenant")
                    yield Select(
                        _TENANTS,
                        value="jhu",
                        allow_blank=False,
                        id="rh-tenant",
                    )
                with Vertical(classes="rh-filter-field"):
                    yield Label("From  [dim]YYYY-MM-DD[/dim]")
                    yield MaskedInput(
                        template="9999-99-99",
                        value=_DEFAULT_FROM.strftime("%Y-%m-%d"),
                        id="rh-from",
                    )
                with Vertical(classes="rh-filter-field"):
                    yield Label("To  [dim]YYYY-MM-DD[/dim]")
                    yield MaskedInput(
                        template="9999-99-99",
                        value=_TODAY.strftime("%Y-%m-%d"),
                        id="rh-to",
                    )
                with Vertical(id="rh-search-col"):
                    yield Label(" ")
                    yield Button("Search", variant="primary", id="btn-rh-search")

            # ── Status / summary bar ──────────────────────────────
            yield Static("", id="rh-status")

            # ── Results table ─────────────────────────────────────
            yield DataTable(id="rh-table", cursor_type="row", zebra_stripes=True)

            # ── Pagination controls ───────────────────────────────
            yield PaginationBar(id="rh-pbar")

        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        tbl = self.query_one("#rh-table", DataTable)
        self._col_keys = {
            key: tbl.add_column(label, key=key, width=width)
            for label, key, width in _COLUMNS
        }
        self._do_search()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _parse_dates(self) -> tuple[date, date] | None:
        """Read and parse the two MaskedInput date fields.

        Returns ``(date_from, date_to)`` or ``None`` if either value is
        not a valid ISO date (e.g. the user hasn't finished typing).
        """
        from_str = self.query_one("#rh-from", MaskedInput).value
        to_str   = self.query_one("#rh-to",   MaskedInput).value
        try:
            return date.fromisoformat(from_str), date.fromisoformat(to_str)
        except ValueError:
            self.notify(
                "Invalid date — use YYYY-MM-DD format",
                severity="warning",
                timeout=4,
            )
            return None

    def _do_search(self) -> None:
        """Reset to page 0 and fire a fresh fetch."""
        dates = self._parse_dates()
        if dates is None:
            return
        tenant = self.query_one("#rh-tenant", Select).value
        if not isinstance(tenant, str):
            self.notify("Please select a tenant", severity="warning")
            return
        self._pager = Paginator(total=0, page_size=_PAGE_SIZE)
        self._fetch(tenant, dates[0], dates[1], page=0)

    def _load_page(self) -> None:
        """Fetch the current page (called after Paginator navigation)."""
        dates = self._parse_dates()
        if dates is None:
            return
        tenant = self.query_one("#rh-tenant", Select).value
        if not isinstance(tenant, str):
            return
        self._fetch(tenant, dates[0], dates[1], page=self._pager.page)

    # ── Async data fetch ───────────────────────────────────────────────────────

    @work(exclusive=True)
    async def _fetch(
        self,
        tenant:    str,
        date_from: date,
        date_to:   date,
        page:      int,
    ) -> None:
        """Fetch one page of Runs from the Repository and populate the table.

        ``exclusive=True`` cancels any in-flight fetch when a new one starts,
        so rapid filter changes don't produce stale interleaved results.
        """
        self.query_one("#rh-status", Static).update("[dim]Loading…[/dim]")

        try:
            repo = getattr(self.app, "repository")
            runs, total = await repo.get_runs(
                tenant, date_from, date_to, page, _PAGE_SIZE
            )
        except Exception as exc:  # noqa: BLE001
            self.notify(f"Fetch error: {exc}", severity="error", timeout=8)
            self.query_one("#rh-status", Static).update("[red]Fetch failed.[/red]")
            return

        # ── Update paginator ──────────────────────────────────────
        self._pager.total = total
        self._pager.page  = page

        # ── Repopulate table ──────────────────────────────────────
        tbl = self.query_one("#rh-table", DataTable)
        tbl.clear()
        for run in runs:
            color = STATUS_COLORS.get(run.status, "dim")
            tbl.add_row(
                Text(run.run_id),
                Text(run.status, style=color),
                Text(run.submitted_at.strftime("%Y-%m-%d %H:%M UTC")),
                Text(run.parent_run_id or "—", style="" if run.parent_run_id else "dim"),
                key=run.run_id,
            )

        # ── Update pagination bar ─────────────────────────────────
        self.query_one(PaginationBar).update(self._pager)

        # ── Update status line ────────────────────────────────────
        start, end = self._pager.slice()
        if total:
            self.query_one("#rh-status", Static).update(
                f"[dim]Tenant:[/dim] [b]{tenant.upper()}[/b]  "
                f"[dim]·[/dim]  "
                f"[dim]{date_from} → {date_to}[/dim]  "
                f"[dim]·[/dim]  "
                f"Showing [b]{start + 1}–{min(end, total)}[/b] of [b]{total}[/b] runs"
            )
        else:
            self.query_one("#rh-status", Static).update(
                f"[dim]No runs found for [b]{tenant.upper()}[/b] "
                f"between {date_from} and {date_to}.[/dim]"
            )

    # ── Event handlers ─────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-rh-search":
            self._do_search()

    def action_search(self) -> None:
        self._do_search()

    def on_pagination_bar_navigated(self, event: PaginationBar.Navigated) -> None:
        _nav = {
            "first": self._pager.first,
            "prev":  self._pager.prev,
            "next":  self._pager.next,
            "last":  self._pager.last,
        }
        nav_fn = _nav.get(event.action)
        if nav_fn and nav_fn():
            self._load_page()

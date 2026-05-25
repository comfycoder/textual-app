"""Demo: Large Dataset — 5 000-row DataTable with virtual scrolling.

Key patterns demonstrated:
  • Add all rows in on_mount — Textual virtualises rendering so only visible
    rows are ever drawn.  There is no need to batch or paginate.
  • move_cursor(row=N) to jump programmatically without scrolling manually.
  • DataTable.RowHighlighted to track cursor position in a status bar.
  • Client-side sort: re-add rows after sorting the Python list; DataTable
    internally recalculates layout dimensions only for visible rows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Input, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.palette import PRI_COLORS, STATUS_COLORS
from your_cli.tui.features.large_dataset._data import COLUMNS, ROWS

__all__ = ["LargeDatasetDemoScreen"]

_TOTAL = len(ROWS)


class LargeDatasetDemoScreen(FeatureScreen):
    """5 000-row DataTable with sort, jump-to-row, and cursor tracking."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("g",       "go_top",     "Top",     show=True),
        Binding("shift+g", "go_bottom",  "Bottom",  show=True),
        Binding("ctrl+j",  "focus_jump", "Jump to", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._display_rows: list[dict[str, str]] = list(ROWS)
        self._sort_col: str | None = None
        self._sort_asc: bool = True
        self._col_keys: dict[str, Any] = {}

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="ld-body"):
            yield Static(
                f"[b]{_TOTAL:,} rows[/b]  "
                "[dim]Textual virtualises rendering — only visible rows are drawn. "
                "Click any column header to sort · "
                "[b]g[/b] / [b]G[/b] jump to top / bottom · "
                "[b]Ctrl+J[/b] jump to row number[/dim]",
                id="ld-hint",
            )
            yield DataTable(id="ld-table", cursor_type="row", zebra_stripes=True)
            with Horizontal(id="ld-footer"):
                yield Static("", id="ld-status")
                yield Static(
                    "[dim]Jump to row:[/dim]",
                    id="ld-jump-label",
                )
                yield Input(id="ld-jump", placeholder=f"1 – {_TOTAL:,}")
        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        tbl = self.query_one("#ld-table", DataTable)
        self._col_keys = {
            key: tbl.add_column(label, key=key, width=width)
            for label, key, width in COLUMNS
        }
        # All rows added synchronously.  Textual's DataTable virtualises its
        # render pass, so add_row() is pure Python list work — fast enough
        # for thousands of rows.
        self._populate()

    # ── Data helpers ───────────────────────────────────────────────────────────

    def _populate(self) -> None:
        tbl = self.query_one("#ld-table", DataTable)
        tbl.clear()
        for row in self._display_rows:
            tbl.add_row(
                Text(row["id"]),
                Text(row["type"]),
                Text(row["status"],   style=STATUS_COLORS.get(row["status"], "")),
                Text(row["priority"], style=PRI_COLORS.get(row["priority"], "")),
                Text(row["tenant"]),
                key=row["id"],
            )
        self._update_column_labels()
        self._update_status(0)

    def _update_status(self, cursor_row: int) -> None:
        n = len(self._display_rows)
        if self._sort_col:
            direction = "↑" if self._sort_asc else "↓"
            sort_info = (
                f"  [dim]sorted by [b]{self._sort_col}[/b] {direction}[/dim]"
            )
        else:
            sort_info = ""
        self.query_one("#ld-status", Static).update(
            f"Row [b]{cursor_row + 1:,}[/b] of [b]{n:,}[/b]{sort_info}"
        )

    def _update_column_labels(self) -> None:
        """Apply sort-direction indicators to column headers per CLAUDE.md pattern."""
        from rich.text import Text as RText

        tbl = self.query_one("#ld-table", DataTable)
        changed = False
        for label, key, _ in COLUMNS:
            col = tbl.columns[self._col_keys[key]]
            indicator = (" ↑" if self._sort_asc else " ↓") if key == self._sort_col else ""
            new_label = RText(label + indicator)
            col.label = new_label
            w = len(label + indicator)
            if w > col.content_width:
                col.content_width = w
                changed = True
        if changed:
            tbl._require_update_dimensions = True  # type: ignore[attr-defined]
        tbl.refresh()

    # ── Event handlers ─────────────────────────────────────────────────────────

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        self._update_status(event.cursor_row)

    def on_data_table_header_selected(
        self, event: DataTable.HeaderSelected
    ) -> None:
        col_key = event.column_key.value
        if self._sort_col == col_key:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col_key
            self._sort_asc = True
        self._display_rows.sort(
            key=lambda r: r[col_key],
            reverse=not self._sort_asc,
        )
        self._populate()
        self.query_one("#ld-table", DataTable).move_cursor(row=0)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "ld-jump":
            return
        raw = event.value.strip()
        event.input.clear()
        try:
            n = int(raw)
        except ValueError:
            return
        n = max(1, min(n, len(self._display_rows)))
        tbl = self.query_one("#ld-table", DataTable)
        tbl.move_cursor(row=n - 1)
        tbl.focus()

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_go_top(self) -> None:
        tbl = self.query_one("#ld-table", DataTable)
        tbl.move_cursor(row=0)
        tbl.focus()

    def action_go_bottom(self) -> None:
        tbl = self.query_one("#ld-table", DataTable)
        tbl.move_cursor(row=len(self._display_rows) - 1)
        tbl.focus()

    def action_focus_jump(self) -> None:
        self.query_one("#ld-jump", Input).focus()

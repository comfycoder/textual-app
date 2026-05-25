"""Demo: Search → Grid → Edit — filter records, page through results, open edit form on row select."""

from pathlib import Path
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from your_cli.tui.widgets import PaginationBar

from your_cli.tui.features.search_grid._data import (
    _DEFAULT_PAGE_SIZE,
    _PAGE_SIZE_OPTS,
    _PRIORITY_OPTS,
    _RECORDS,
    _SG_COLUMNS,
    _STATUS_OPTS,
    _TYPE_OPTS,
)
from your_cli.tui.palette import PRI_COLORS, STATUS_COLORS
from your_cli.tui.paginator import Paginator
from your_cli.tui.features.search_grid.edit import EditJobScreen

__all__ = ["SearchGridDemoScreen", "EditJobScreen"]


# ── Search + Grid screen ──────────────────────────────────────────────────────

class SearchGridDemoScreen(FeatureScreen):
    """Search form above a pageable DataTable; Enter on any row opens the edit screen."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("f5",     "do_search",    "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._filtered:       list[dict[str, Any]] = []
        self._last_edited_id: str | None           = None
        self._page_size:      int                  = _DEFAULT_PAGE_SIZE
        self._sort_key:       str | None           = None   # record field name, or None
        self._sort_asc:       bool                 = True
        self._col_keys:       dict[str, Any]       = {}     # field key → ColumnKey
        self._pager:          Paginator            = Paginator(total=0, page_size=_DEFAULT_PAGE_SIZE)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sg-body"):

            # ── Filter bar ────────────────────────────────────────
            with Vertical(id="sg-search-panel"):
                yield Static(
                    "[b]Search Jobs[/b]  "
                    "[dim]Ctrl+F · Enter on a row to edit[/dim]",
                    id="sg-search-title",
                )
                with Horizontal(classes="sg-filter-row"):
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Job ID / Submitter / Tags")
                        yield Input(id="sg-q")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Status")
                        yield Select(_STATUS_OPTS, prompt="All statuses", id="sg-status")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Type")
                        yield Select(_TYPE_OPTS, prompt="All types", id="sg-type")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Priority")
                        yield Select(_PRIORITY_OPTS, prompt="All priorities", id="sg-priority")
                with Horizontal(id="sg-search-actions"):
                    yield Button("Search", variant="primary", id="btn-sg-search")
                    yield Button("Clear",  id="btn-sg-clear")
                    yield Static("", id="sg-search-spacer")
                    yield Label("Per page", id="sg-per-page-label")
                    yield Select(
                        _PAGE_SIZE_OPTS,
                        value=_DEFAULT_PAGE_SIZE,
                        id="sg-page-size",
                        allow_blank=False,
                    )

            # ── Results grid ──────────────────────────────────────
            with Vertical(id="sg-grid-area"):
                yield DataTable(id="sg-table", cursor_type="row", zebra_stripes=True)

            # ── Pagination bar ────────────────────────────────────
            with Horizontal(id="sg-pagination"):
                yield PaginationBar(id="sg-pbar")

        yield Footer()

    def on_mount(self) -> None:
        tbl = self.query_one("#sg-table", DataTable)
        self._col_keys = {
            key: tbl.add_column(label, key=key, width=width)
            for label, key, width in _SG_COLUMNS
        }
        self._filtered = list(reversed(_RECORDS))
        self._pager = Paginator(total=len(self._filtered), page_size=self._page_size)
        self._load_page()
        tbl.focus()

    def on_screen_resume(self) -> None:
        """Refresh current page and re-select the last-edited row."""
        self._load_page()
        self._restore_cursor()

    def _restore_cursor(self) -> None:
        if not self._last_edited_id:
            return
        for i, rec in enumerate(self._filtered):
            if rec["id"] == self._last_edited_id:
                target_page = i // self._page_size
                if target_page != self._pager.page:
                    self._pager.page = target_page
                    self._load_page()
                self.query_one("#sg-table", DataTable).move_cursor(row=i % self._page_size)
                return

    # ── Sort helpers ──────────────────────────────────────────────

    def _apply_sort(self) -> None:
        """Sort self._filtered in-place by the active sort column."""
        if not self._sort_key:
            return
        sort_key = self._sort_key  # already guarded by `if not self._sort_key` above
        self._filtered.sort(
            key=lambda r: (r.get(sort_key) or "").lower(),
            reverse=not self._sort_asc,
        )

    def _update_column_headers(self) -> None:
        """Refresh header labels to show/hide the sort indicator."""
        tbl = self.query_one("#sg-table", DataTable)
        dimensions_changed = False
        for label, key, _width in _SG_COLUMNS:
            ck = self._col_keys[key]
            col = tbl.columns[ck]
            indicator = (" ▲" if self._sort_asc else " ▼") if key == self._sort_key else ""
            new_label = Text(label + indicator)
            col.label = new_label
            # auto_width columns track content_width; grow it if the new label is wider
            label_width = len(label + indicator)
            if label_width > col.content_width:
                col.content_width = label_width
                dimensions_changed = True
        if dimensions_changed:
            tbl._require_update_dimensions = True
        tbl.refresh()

    # ── Filter + render ───────────────────────────────────────────

    def _run_search(self) -> None:
        q      = self.query_one("#sg-q",        Input ).value.strip().lower()
        status = self.query_one("#sg-status",   Select).value
        jtype  = self.query_one("#sg-type",     Select).value
        pri    = self.query_one("#sg-priority", Select).value

        results = list(reversed(_RECORDS))
        if q:
            results = [r for r in results
                       if q in r["id"].lower()
                       or q in r["submitted_by"].lower()
                       or q in r["tags"].lower()]
        # Use isinstance(str) rather than `is not Select.BLANK` — after select.clear()
        # the value may be None or a non-BLANK sentinel, not Select.BLANK itself.
        if isinstance(status, str):
            results = [r for r in results if r["status"] == status]
        if isinstance(jtype, str):
            results = [r for r in results if r["type"]   == jtype]
        if isinstance(pri, str):
            results = [r for r in results if r["priority"] == pri]

        self._filtered = results
        self._apply_sort()
        self._pager = Paginator(total=len(self._filtered), page_size=self._page_size)
        self._load_page()

    def _load_page(self) -> None:
        tbl          = self.query_one("#sg-table", DataTable)
        start, end   = self._pager.slice()
        chunk        = self._filtered[start:end]

        tbl.clear()
        for rec in chunk:
            sc = STATUS_COLORS.get(rec["status"], "white")
            pc = PRI_COLORS.get(rec["priority"], "white")
            tbl.add_row(
                rec["id"], rec["tenant"], rec["type"],
                f"[{sc}]{rec['status']}[/{sc}]",
                f"[{pc}]{rec['priority']}[/{pc}]",
                rec["environment"],
                rec["submitted_by"],
                rec["tags"] or "[dim]—[/dim]",
                key=rec["id"],
                height=None,
            )

        self.query_one(PaginationBar).update(self._pager)

    # ── Button / row events ───────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-sg-search":
                self._run_search()
            case "btn-sg-clear":
                self._clear_search()

    def on_pagination_bar_navigated(self, event: PaginationBar.Navigated) -> None:
        if event.control is not self.query_one(PaginationBar):
            return
        _nav = {"first": self._pager.first, "prev": self._pager.prev,
                "next":  self._pager.next,  "last": self._pager.last}
        if (nav := _nav.get(event.action)) is None:
            raise ValueError(f"Unknown PaginationBar action: {event.action!r}")
        if nav():
            self._load_page()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "sg-q":
            self._run_search()

    def on_select_changed(self, event: Select.Changed) -> None:
        match event.select.id:
            case "sg-page-size":
                if isinstance(event.value, int):
                    self._page_size = event.value
                    self._pager = Paginator(total=len(self._filtered), page_size=self._page_size)
                    self._load_page()
            case "sg-status" | "sg-type" | "sg-priority":
                self._run_search()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        if event.data_table.id != "sg-table":
            return
        col_key = event.column_key.value
        if col_key is None:
            return
        if self._sort_key == col_key:
            if self._sort_asc:
                self._sort_asc = False              # 2nd click → descending
            else:
                self._sort_key = None               # 3rd click → no sort
        else:
            self._sort_key = col_key
            self._sort_asc = True                   # 1st click → ascending
        self._update_column_headers()
        if self._sort_key is None:
            # Sort removed — re-run search to restore natural order
            self._run_search()
        else:
            self._apply_sort()
            self._pager = Paginator(total=len(self._filtered), page_size=self._page_size)
            self._load_page()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "sg-table" and event.row_key:
            self._last_edited_id = str(event.row_key.value)
            self.app.push_screen(EditJobScreen(self._last_edited_id))

    def _clear_search(self) -> None:
        self.query_one("#sg-q",      Input ).value = ""
        self.query_one("#sg-status", Select).clear()
        self.query_one("#sg-type",   Select).clear()
        self.query_one("#sg-priority", Select).clear()
        self._run_search()

    def action_focus_search(self) -> None:
        self.query_one("#sg-q", Input).focus()

    def action_do_search(self) -> None:
        self._run_search()


"""Demo: Pagination — browse a large dataset in fixed-size pages."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.paginator import Paginator
from your_cli.tui.palette import STATUS_COLORS

_TYPES   = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS = ["jhu", "unc", "mayo"]

random.seed(99)
_ALL_ITEMS = [
    {
        "id":       f"wi-{i:03d}",
        "tenant":   random.choice(_TENANTS),
        "status":   random.choice(list(STATUS_COLORS)),
        "type":     random.choice(_TYPES),
        "duration": f"{random.randint(0, 59):02d}m {random.randint(0, 59):02d}s",
    }
    for i in range(1, 101)
]

PAGE_SIZE = 10


class PaginationDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("left",  "prev_page", "Prev page"),
        Binding("right", "next_page", "Next page"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._pager = Paginator(total=len(_ALL_ITEMS), page_size=PAGE_SIZE)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="page-body"):
            yield DataTable(id="page-table", cursor_type="row")
            with Horizontal(id="page-controls"):
                yield Button("|◀",      id="btn-pg-first", disabled=True)
                yield Button("◀  Prev", id="btn-pg-prev",  disabled=True)
                yield Static("", id="page-label")
                yield Button("Next  ▶", id="btn-pg-next")
                yield Button("▶|",      id="btn-pg-last")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Tenant", "Type", "Duration")
        self._render_page()
        table.focus()

    def _render_page(self) -> None:
        start, end = self._pager.slice()
        table = self.query_one(DataTable)
        table.clear()
        for item in _ALL_ITEMS[start:end]:
            color = STATUS_COLORS.get(item["status"], "white")
            table.add_row(
                item["id"],
                f"[{color}]{item['status']}[/{color}]",
                item["tenant"],
                item["type"],
                item["duration"],
            )
        total = self._pager.total
        self.query_one("#page-label", Static).update(
            f"  Page [b]{self._pager.display_page}[/b] of [b]{self._pager.page_count}[/b]"
            f"  [dim](rows {start + 1}–{min(end, total)} of {total})[/dim]  "
        )
        self.query_one("#btn-pg-first", Button).disabled = self._pager.at_first
        self.query_one("#btn-pg-prev",  Button).disabled = self._pager.at_first
        self.query_one("#btn-pg-next",  Button).disabled = self._pager.at_last
        self.query_one("#btn-pg-last",  Button).disabled = self._pager.at_last

    def action_prev_page(self) -> None:
        if self._pager.prev():
            self._render_page()

    def action_next_page(self) -> None:
        if self._pager.next():
            self._render_page()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-pg-first":
                if self._pager.first():
                    self._render_page()
            case "btn-pg-prev":
                self.action_prev_page()
            case "btn-pg-next":
                self.action_next_page()
            case "btn-pg-last":
                if self._pager.last():
                    self._render_page()

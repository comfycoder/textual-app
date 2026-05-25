"""Demo: Pagination — browse a large dataset in fixed-size pages."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.paginator import Paginator
from your_cli.tui.palette import STATUS_COLORS
from your_cli.tui.widgets import PaginationBar

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
                yield PaginationBar(id="page-pbar")
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
        self.query_one(PaginationBar).update(self._pager)

    def on_pagination_bar_navigated(self, event: PaginationBar.Navigated) -> None:
        if getattr(self._pager, event.action)():
            self._render_page()

    def action_prev_page(self) -> None:
        if self._pager.prev():
            self._render_page()

    def action_next_page(self) -> None:
        if self._pager.next():
            self._render_page()

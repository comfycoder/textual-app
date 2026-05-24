"""Demo: Pagination — browse a large dataset in fixed-size pages."""

import random

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

_STATUS_COLORS = {
    "queued": "yellow", "running": "cyan", "done": "green",
    "failed": "red",    "pending": "dim",
}
_TYPES   = ["training", "validation", "export", "inference", "preprocessing"]
_TENANTS = ["jhu", "unc", "mayo"]

random.seed(99)
_ALL_ITEMS = [
    {
        "id":       f"wi-{i:03d}",
        "tenant":   random.choice(_TENANTS),
        "status":   random.choice(list(_STATUS_COLORS)),
        "type":     random.choice(_TYPES),
        "duration": f"{random.randint(0, 59):02d}m {random.randint(0, 59):02d}s",
    }
    for i in range(1, 101)
]

PAGE_SIZE = 10


class PaginationDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "go_back",   "Back"),
        Binding("left",   "prev_page", "Prev page"),
        Binding("right",  "next_page", "Next page"),
    ]

    _page: reactive[int] = reactive(1)

    @property
    def _total_pages(self) -> int:
        return (len(_ALL_ITEMS) + PAGE_SIZE - 1) // PAGE_SIZE

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="page-body"):
            yield DataTable(id="page-table", cursor_type="row")
            with Horizontal(id="page-controls"):
                yield Button("|◀",   id="btn-pg-first", disabled=True)
                yield Button("◀  Prev", id="btn-pg-prev",  disabled=True)
                yield Static("", id="page-label")
                yield Button("Next  ▶", id="btn-pg-next")
                yield Button("▶|",   id="btn-pg-last")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Status", "Tenant", "Type", "Duration")
        self._render_page()
        table.focus()

    def watch__page(self, _: int) -> None:
        self._render_page()

    def _render_page(self) -> None:
        start = (self._page - 1) * PAGE_SIZE
        end   = start + PAGE_SIZE
        table = self.query_one(DataTable)
        table.clear()
        for item in _ALL_ITEMS[start:end]:
            color = _STATUS_COLORS.get(item["status"], "white")
            table.add_row(
                item["id"],
                f"[{color}]{item['status']}[/{color}]",
                item["tenant"],
                item["type"],
                item["duration"],
            )
        total = len(_ALL_ITEMS)
        self.query_one("#page-label", Static).update(
            f"  Page [b]{self._page}[/b] of [b]{self._total_pages}[/b]"
            f"  [dim](rows {start + 1}–{min(end, total)} of {total})[/dim]  "
        )
        at_first = self._page == 1
        at_last  = self._page == self._total_pages
        self.query_one("#btn-pg-first", Button).disabled = at_first
        self.query_one("#btn-pg-prev",  Button).disabled = at_first
        self.query_one("#btn-pg-next",  Button).disabled = at_last
        self.query_one("#btn-pg-last",  Button).disabled = at_last

    def action_prev_page(self) -> None:
        if self._page > 1:
            self._page -= 1

    def action_next_page(self) -> None:
        if self._page < self._total_pages:
            self._page += 1

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-pg-first": self._page = 1
            case "btn-pg-prev":  self.action_prev_page()
            case "btn-pg-next":  self.action_next_page()
            case "btn-pg-last":  self._page = self._total_pages

    def action_go_back(self) -> None:
        self.app.pop_screen()

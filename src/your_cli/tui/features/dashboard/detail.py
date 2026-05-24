"""Work item detail screen."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class DetailScreen(Screen[None]):
    """Full-screen detail view for a single work item."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
    ]

    def __init__(self, item_id: str, status: str, tenant: str, updated: str) -> None:
        super().__init__()
        self._item_id = item_id
        self._status = status
        self._tenant = tenant
        self._updated = updated

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="detail-body"):
            yield Static(f"[b]Work Item — {self._item_id}[/b]", classes="panel-title")
            yield Static(f"[dim]Status[/dim]   {self._status}", classes="detail-field")
            yield Static(f"[dim]Tenant[/dim]   {self._tenant}", classes="detail-field")
            yield Static(f"[dim]Updated[/dim]  {self._updated}", classes="detail-field")
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

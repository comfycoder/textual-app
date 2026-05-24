"""Dashboard screen."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import DataTable, Footer, Header, Static

from your_cli.tui.features.dashboard.detail import DetailScreen


class DashboardScreen(FeatureScreen):
    """Two-pane dashboard with a resizable sidebar."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("[", "narrow_sidebar", "Narrow"),
        Binding("]", "widen_sidebar", "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(30)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("[b]Status[/b]", classes="panel-title")
                yield Static("API: not yet connected", id="api-status")
                yield Static("Auth: not signed in", id="auth-status")
                yield Static("", id="sidebar-width-label")
            with Vertical(id="main"):
                yield Static("[b]Recent work items[/b]", classes="panel-title")
                yield DataTable(id="items", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.query_one("#api-status", Static).update(f"API: {app.settings.api_base_url}")
        self.sidebar_width = app.settings.sidebar_width

        table = self.query_one(DataTable)
        table.focus()
        table.add_columns("ID", "Status", "Tenant", "Updated")
        table.add_rows([
            ("wi-001", "queued",  "jhu",  "2026-05-23 09:14"),
            ("wi-002", "running", "unc",  "2026-05-23 09:17"),
            ("wi-003", "done",    "mayo", "2026-05-23 09:21"),
        ])

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#sidebar").styles.width = f"{width}%"
        self.query_one("#sidebar-width-label", Static).update(f"[dim]width: {width}%[/dim]")

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)


    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one(DataTable)
        row = table.get_row(event.row_key)
        self.app.push_screen(
            DetailScreen(
                item_id=str(row[0]),
                status=str(row[1]),
                tenant=str(row[2]),
                updated=str(row[3]),
            )
        )

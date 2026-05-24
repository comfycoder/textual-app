"""Demo: Theme switcher — select any theme for an instant live preview."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    ProgressBar,
    Select,
    Static,
    Switch,
)

from your_cli.tui.themes import THEME_NAMES


class ThemeToggleDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back",        "Back"),
        Binding("[",      "narrow_sidebar", "Narrow"),
        Binding("]",      "widen_sidebar",  "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(25)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="theme-body"):
            yield ListView(
                *[ListItem(Label(name), id=f"ti-{name}") for name in THEME_NAMES],
                id="theme-list",
            )
            with Vertical(id="theme-preview"):
                yield Static("", id="theme-active-label", classes="demo-label")
                yield Static("[b]Widget preview[/b]", classes="demo-label")
                with Horizontal(classes="demo-row"):
                    yield Label("Input  ")
                    yield Input(value="sample text")
                with Horizontal(classes="demo-row"):
                    yield Label("Switch  ")
                    yield Switch(value=True)
                with Horizontal(classes="demo-row"):
                    yield Label("Checkbox  ")
                    yield Checkbox("Enabled", value=True)
                with Horizontal(classes="demo-row"):
                    yield Label("Select  ")
                    yield Select(
                        [("Option A", "a"), ("Option B", "b"), ("Option C", "c")],
                        value="a",
                    )
                yield Label("Progress")
                yield ProgressBar(total=100, id="theme-pb")
                yield Static("[b]DataTable[/b]", classes="demo-label")
                yield DataTable(id="theme-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width

        self.query_one("#theme-pb", ProgressBar).advance(65)
        table = self.query_one("#theme-table", DataTable)
        table.add_columns("ID", "Status", "Tenant")
        table.add_row("wi-001", "[green]done[/green]",     "jhu")
        table.add_row("wi-002", "[cyan]running[/cyan]",    "unc")
        table.add_row("wi-003", "[yellow]queued[/yellow]", "mayo")

        lv = self.query_one(ListView)
        current = self.app.theme or "textual-dark"
        try:
            lv.index = THEME_NAMES.index(current)
        except ValueError:
            pass
        lv.focus()
        self._update_label()

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#theme-list").styles.width = f"{width}%"

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            name = event.item.id.removeprefix("ti-")
            self.app.theme = name
            self._update_label()

    def _update_label(self) -> None:
        self.query_one("#theme-active-label", Static).update(
            f"Active: [b]{self.app.theme or 'textual-dark'}[/b]"
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

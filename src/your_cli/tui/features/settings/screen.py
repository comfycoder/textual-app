"""Demo: Settings screen with category sidebar and resizable sidebar."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    Switch,
)

_CATEGORIES = [
    ("General",  "general"),
    ("Display",  "display"),
    ("API",      "api"),
    ("Pipeline", "pipeline"),
]


class SettingsDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("[", "narrow_sidebar", "Narrow"),
        Binding("]", "widen_sidebar",  "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(25)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="settings-body"):
            yield ListView(
                *[ListItem(Label(name), id=f"cat-{key}") for name, key in _CATEGORIES],
                id="settings-list",
            )
            with Vertical(id="settings-content"):
                with Vertical(id="settings-general", classes="settings-pane"):
                    yield Static("[b]General[/b]", classes="demo-label")
                    yield Label("Default sidebar width (%)")
                    yield Input(value="20", id="set-sidebar-width")
                    yield Label("Auto-refresh interval (seconds)")
                    yield Input(value="10", id="set-refresh-interval")
                    yield Label("Max file preview lines")
                    yield Input(value="200", id="set-preview-lines")

                with Vertical(id="settings-display", classes="settings-pane"):
                    yield Static("[b]Display[/b]", classes="demo-label")
                    yield Label("Dark mode")
                    yield Switch(value=True,  id="set-dark-mode")
                    yield Label("Show clock in header")
                    yield Switch(value=True,  id="set-show-clock")
                    yield Label("Compact row spacing")
                    yield Switch(value=False, id="set-compact")

                with Vertical(id="settings-api", classes="settings-pane"):
                    yield Static("[b]API[/b]", classes="demo-label")
                    yield Label("Base URL")
                    yield Input(value="https://api.aiq.example.com", id="set-api-url")
                    yield Label("Timeout (seconds)")
                    yield Input(value="30", id="set-api-timeout")
                    yield Label("Auth method")
                    yield Select(
                        [("API Key", "apikey"), ("OAuth2", "oauth2"), ("mTLS", "mtls")],
                        value="apikey",
                        id="set-auth-method",
                    )

                with Vertical(id="settings-pipeline", classes="settings-pane"):
                    yield Static("[b]Pipeline[/b]", classes="demo-label")
                    yield Label("Default tenant")
                    yield Select(
                        [("Johns Hopkins (JHU)", "jhu"), ("UNC Chapel Hill", "unc"), ("Mayo Clinic", "mayo")],
                        prompt="Select…",
                        id="set-default-tenant",
                    )
                    yield Label("Max concurrent jobs")
                    yield Input(value="4", id="set-max-jobs")
                    yield Label("Retry on failure")
                    yield Switch(value=True, id="set-retry")

                with Horizontal(id="settings-actions"):
                    yield Button("Save",             variant="primary", id="btn-settings-save")
                    yield Button("Reset to defaults",                   id="btn-settings-reset")
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width
        self.query_one(ListView).focus()
        self._show_category("general")

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#settings-list").styles.width = f"{width}%"

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            key = event.item.id.removeprefix("cat-")
            self._show_category(key)

    def _show_category(self, key: str) -> None:
        for _, cat_key in _CATEGORIES:
            self.query_one(f"#settings-{cat_key}").display = (cat_key == key)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-settings-save":
                self.notify("Settings saved.", title="Settings", severity="information")
            case "btn-settings-reset":
                self.notify("Reset to defaults.", title="Settings", severity="warning")


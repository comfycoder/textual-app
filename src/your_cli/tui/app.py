"""Root Textual application."""

from textual.app import App

import your_cli.tui.routes  # noqa: F401 — side-effect: populates the route registry
from your_cli.config import Settings
from your_cli.tui.fake_api import FakeApiClient
from your_cli.tui.repository import Repository
from your_cli.tui.themes import ALL_THEMES


class YourCliApp(App[None]):
    """Top-level TUI app. Screens are registered here; state lives on the App."""

    CSS_PATH = "styles.tcss"
    TITLE = "AIQ CLI"
    SUB_TITLE = "Press q to quit"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings   = settings
        self.token:       str | None = None
        # Swap FakeApiClient for the real generated client once available.
        self.repository = Repository(FakeApiClient())

    def on_mount(self) -> None:
        for theme in ALL_THEMES:
            self.register_theme(theme)
        self.theme = "aiq"
        from your_cli.tui.router import navigate
        navigate(self, "gallery")

    def action_toggle_dark(self) -> None:
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

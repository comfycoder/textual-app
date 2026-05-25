"""Gallery screen — widget demo navigation hub."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static


class GalleryScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "app.quit", "Quit"),
        Binding("[", "narrow_sidebar", "Narrow"),
        Binding("]", "widen_sidebar", "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(30)

    def __init__(self) -> None:
        super().__init__()
        # Populated after routes.py has been imported (guaranteed by app.py).
        from your_cli.tui.router import get_gallery_demos
        self._demos: list[tuple[str, str, str]] = get_gallery_demos()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="gallery-body"):
            yield ListView(
                *[ListItem(Label(name), id=f"demo-{key}") for name, key, _ in self._demos],
                id="gallery-list",
            )
            yield Vertical(
                Static("[b]Widget Gallery[/b]", id="gallery-title"),
                Static("Select a demo and press [b]Enter[/b] to open it.", id="gallery-hint"),
                Static("", id="gallery-desc"),
                Static("", id="gallery-width-label"),
                id="gallery-detail",
            )
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width
        self.query_one(ListView).focus()

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#gallery-list").styles.width = f"{width}%"
        self.query_one("#gallery-width-label", Static).update(f"[dim]width: {width}%[/dim]")

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        index = self.query_one(ListView).index
        if index is not None and index < len(self._demos):
            _, _, desc = self._demos[index]
            self.query_one("#gallery-desc", Static).update(f"\n{desc}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = self.query_one(ListView).index
        if index is None or index >= len(self._demos):
            return
        _, key, _ = self._demos[index]
        self._open_demo(key)

    def _open_demo(self, key: str) -> None:
        from your_cli.tui.router import navigate
        navigate(self.app, key)

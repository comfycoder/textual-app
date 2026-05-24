"""CommandPaletteModal — fuzzy-search command overlay."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView

_COMMANDS = [
    ("New project…",               "new-project"),
    ("Open recent: alpha-run-42",  "recent-alpha"),
    ("Open recent: beta-run-17",   "recent-beta"),
    ("Go to Jobs Dashboard",       "jobs"),
    ("Go to Reports",              "reports"),
    ("Go to Settings",             "settings"),
    ("Refresh data",               "refresh"),
    ("Export current view",        "export"),
    ("Show keyboard shortcuts",    "shortcuts"),
    ("Switch tenant → JHU",        "tenant-jhu"),
    ("Switch tenant → UNC",        "tenant-unc"),
    ("Switch tenant → Mayo",       "tenant-mayo"),
    ("Quit application",           "quit"),
]


class CommandPaletteModal(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "dismiss_none", "Close")]

    def compose(self) -> ComposeResult:
        with Vertical(id="cp-modal-body"):
            yield Input(placeholder="Type to search commands…", id="cp-input")
            yield ListView(id="cp-list")

    def on_mount(self) -> None:
        self.query_one("#cp-input", Input).focus()
        self._render_list(_COMMANDS)

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        filtered = [(n, k) for n, k in _COMMANDS if query in n.lower()]
        self._render_list(filtered)

    def _render_list(self, items: list[tuple[str, str]]) -> None:
        lv = self.query_one("#cp-list", ListView)
        lv.clear()
        for name, key in items:
            lv.append(ListItem(Label(name), id=f"cp-item-{key}"))
        if lv.children:
            lv.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            key = event.item.id.removeprefix("cp-item-")
            self.dismiss(key)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

"""Demo: Tabs — standalone tab bar driving a ContentSwitcher manually."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import (
    Button,
    ContentSwitcher,
    Footer,
    Header,
    Static,
    Tab,
    Tabs,
)

_PANELS = {
    "tab-overview":  (
        "[b]Overview[/b]\n\n"
        "Standalone [b]Tabs[/b] widget — unlike [b]TabbedContent[/b], the tab bar\n"
        "and content area are separate widgets that you wire together yourself.\n\n"
        "This gives you full control: animate the content swap, conditionally\n"
        "disable tabs, add/remove tabs at runtime, or drive any widget (not just\n"
        "panels) from the same tab bar."
    ),
    "tab-dynamic": (
        "[b]Dynamic Tabs[/b]\n\n"
        "Use the buttons above to add or remove tabs at runtime.\n"
        "The [b]Tabs.TabActivated[/b] message fires whenever the active tab\n"
        "changes — either by user interaction or [b]tabs.active = \"tab-id\"[/b].\n\n"
        "Dynamic tabs are useful for editor-style multi-document interfaces."
    ),
    "tab-events": (
        "[b]Events & API[/b]\n\n"
        "[b]Tabs.TabActivated[/b]  — tab changed (by user or code)\n"
        "[b]Tabs.Cleared[/b]       — last tab was removed\n\n"
        "[b]tabs.active[/b]        — reactive ID of the active tab\n"
        "[b]tabs.add_tab()[/b]     — add a new tab\n"
        "[b]tabs.remove_tab()[/b]  — remove a tab by ID\n"
        "[b]tabs.disable()[/b]     — grey out a tab\n"
        "[b]tabs.enable()[/b]      — re-enable a disabled tab\n"
        "[b]tabs.clear()[/b]       — remove all tabs"
    ),
    "tab-vs-tabbed": (
        "[b]Tabs vs TabbedContent[/b]\n\n"
        "[b]TabbedContent[/b]:\n"
        "  • Declares panels inline in [b]compose()[/b] using TabPane\n"
        "  • Content is always mounted, just hidden/shown\n"
        "  • Simpler for static sets of panels\n\n"
        "[b]Tabs[/b] (this demo):\n"
        "  • Tab bar and content are separate — wire with ContentSwitcher\n"
        "  • Supports dynamic add/remove at runtime\n"
        "  • Full control over what the tab activates"
    ),
}

_STATIC_TABS = list(_PANELS.keys())[:4]
_dynamic_counter = 0


class TabsDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="tabs-outer"):
            yield Tabs(
                Tab("Overview",        id="tab-overview"),
                Tab("Dynamic tabs",    id="tab-dynamic"),
                Tab("Events & API",    id="tab-events"),
                Tab("Tabs vs Tabbed",  id="tab-vs-tabbed"),
                active="tab-overview",
                id="tabs-bar",
            )
            with ContentSwitcher(initial="tab-overview", id="tabs-switcher"):
                for tab_id, content in _PANELS.items():
                    yield Static(content, id=tab_id, classes="tabs-panel")
            from textual.containers import Horizontal
            with Horizontal(id="tabs-actions"):
                yield Button("+ Add tab",    id="btn-tabs-add")
                yield Button("✕ Remove last added", id="btn-tabs-remove", disabled=True)
                yield Static("", id="tabs-dyn-label")
        yield Footer()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab is None:
            return
        tab_id = event.tab.id
        switcher = self.query_one("#tabs-switcher", ContentSwitcher)
        if tab_id and switcher.query(f"#{tab_id}"):
            switcher.current = tab_id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        global _dynamic_counter
        tabs = self.query_one("#tabs-bar", Tabs)
        switcher = self.query_one("#tabs-switcher", ContentSwitcher)

        if event.button.id == "btn-tabs-add":
            _dynamic_counter += 1
            tab_id = f"tab-dyn-{_dynamic_counter}"
            tabs.add_tab(Tab(f"Tab {_dynamic_counter}", id=tab_id))
            panel = Static(
                f"[b]Dynamic Tab {_dynamic_counter}[/b]\n\n"
                f"This tab was added at runtime via [b]tabs.add_tab()[/b].\n"
                f"The matching panel was mounted into the ContentSwitcher.",
                id=tab_id,
                classes="tabs-panel",
            )
            switcher.mount(panel)
            self.query_one("#btn-tabs-remove", Button).disabled = False
            self.query_one("#tabs-dyn-label", Static).update(
                f"[dim]{_dynamic_counter} dynamic tab(s) added[/dim]"
            )

        elif event.button.id == "btn-tabs-remove" and _dynamic_counter > 0:
            tab_id = f"tab-dyn-{_dynamic_counter}"
            tabs.remove_tab(tab_id)
            try:
                switcher.query_one(f"#{tab_id}").remove()
            except Exception:
                pass
            _dynamic_counter -= 1
            self.query_one("#btn-tabs-remove", Button).disabled = _dynamic_counter == 0
            label = f"[dim]{_dynamic_counter} dynamic tab(s) added[/dim]" if _dynamic_counter else ""
            self.query_one("#tabs-dyn-label", Static).update(label)


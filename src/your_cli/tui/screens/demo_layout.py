"""Demo: Layout & Navigation."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Collapsible,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)


class LayoutDemoScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Grid", id="tab-grid"):
                with Static(id="demo-grid"):
                    yield Static("Cell A — top left",     classes="grid-cell")
                    yield Static("Cell B — top centre",   classes="grid-cell")
                    yield Static("Cell C — top right",    classes="grid-cell")
                    yield Static("Cell D — bottom left",  classes="grid-cell")
                    yield Static("Cell E — bottom centre",classes="grid-cell")
                    yield Static("Cell F — bottom right", classes="grid-cell")
            with TabPane("Collapsible", id="tab-collapsible"):
                yield Collapsible(
                    Static(
                        "This section is open by default. "
                        "Click the title or press Space/Enter to collapse it."
                    ),
                    title="Section One — expanded",
                    collapsed=False,
                )
                yield Collapsible(
                    Static(
                        "This section starts collapsed. "
                        "Any widget can be nested inside a Collapsible."
                    ),
                    title="Section Two — collapsed",
                    collapsed=True,
                )
                yield Collapsible(
                    Static("Multiple independent sections can coexist on the same screen."),
                    title="Section Three — collapsed",
                    collapsed=True,
                )
            with TabPane("Tree", id="tab-tree"):
                tree: Tree[str] = Tree("Tenants", id="demo-tree")
                tree.root.expand()
                jhu = tree.root.add("JHU", expand=True)
                jhu.add_leaf("wi-001 — queued")
                jhu.add_leaf("wi-002 — done")
                unc = tree.root.add("UNC", expand=True)
                unc.add_leaf("wi-003 — running")
                mayo = tree.root.add("Mayo Clinic")
                mayo.add_leaf("wi-004 — pending")
                mayo.add_leaf("wi-005 — queued")
                yield tree
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

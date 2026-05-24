"""Demo: ContentSwitcher — sidebar nav swaps main panel without a new screen."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import (
    ContentSwitcher,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

_PANELS = [
    ("Overview",      "cs-overview"),
    ("Jobs",          "cs-jobs"),
    ("Infrastructure","cs-infra"),
    ("Alerts",        "cs-alerts"),
    ("Help",          "cs-help"),
]

_CONTENT = {
    "cs-overview": (
        "[b]Platform Overview[/b]\n\n"
        "The AIQ platform orchestrates distributed ML workloads across multiple tenant\n"
        "sites.  Each site maintains an isolated compute pool; jobs are scheduled by the\n"
        "central broker and streamed back to the submitting researcher.\n\n"
        "• [cyan]42[/cyan]  active jobs this week\n"
        "• [green]98.4 %[/green]  scheduler uptime (30-day)\n"
        "• [yellow]3[/yellow]  tenants currently connected\n"
        "• [dim]Last sync: 2 minutes ago[/dim]"
    ),
    "cs-jobs": (
        "[b]Recent Jobs[/b]\n\n"
        "[green]✓[/green]  wi-097  training     jhu    4 m 12 s\n"
        "[green]✓[/green]  wi-096  validation   unc    1 m 08 s\n"
        "[cyan]▶[/cyan]  wi-098  inference    mayo   running…\n"
        "[yellow]⏸[/yellow]  wi-099  export       jhu    queued\n"
        "[red]✗[/red]  wi-094  preprocessing unc   failed  [dim]OOM[/dim]\n\n"
        "Press [b]Enter[/b] on the Jobs row to open the full dashboard."
    ),
    "cs-infra": (
        "[b]Infrastructure[/b]\n\n"
        "Cluster          Nodes   GPUs   Status\n"
        "─────────────────────────────────────\n"
        "jhu-prod         8       32     [green]healthy[/green]\n"
        "unc-research     4       16     [green]healthy[/green]\n"
        "mayo-inference   6       24     [yellow]degraded[/yellow]  [dim]1 node offline[/dim]\n\n"
        "Total capacity: [b]18 nodes / 72 GPUs[/b]"
    ),
    "cs-alerts": (
        "[b]Active Alerts[/b]\n\n"
        "[red][CRIT][/red]  mayo-inference node-4 unreachable since 14:22 UTC\n"
        "[yellow][WARN][/yellow]  unc-research GPU memory > 90 % on node-2\n"
        "[yellow][WARN][/yellow]  wi-094 failed — OOM on preprocessing step 3\n"
        "[dim][INFO][/dim]  Scheduled maintenance window: Sun 02:00–04:00 UTC\n\n"
        "[b]3 open alerts[/b]  ([red]1 critical[/red], [yellow]2 warning[/yellow])"
    ),
    "cs-help": (
        "[b]Navigation Help[/b]\n\n"
        "Click any item in the sidebar [b]or[/b] use the number keys 1–5 to jump\n"
        "directly to that panel.\n\n"
        "[b]Keyboard shortcuts[/b]\n"
        "  [b]1[/b]  Overview\n"
        "  [b]2[/b]  Jobs\n"
        "  [b]3[/b]  Infrastructure\n"
        "  [b]4[/b]  Alerts\n"
        "  [b]5[/b]  Help\n"
        "  [b][[/b] / [b]][/b]  Resize sidebar\n"
        "  [b]Esc[/b]  Return to gallery"
    ),
}


class ContentSwitcherDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("1",      "show_panel_0", "Overview",       show=False),
        Binding("2",      "show_panel_1", "Jobs",           show=False),
        Binding("3",      "show_panel_2", "Infrastructure", show=False),
        Binding("4",      "show_panel_3", "Alerts",         show=False),
        Binding("5",      "show_panel_4", "Help",           show=False),
        Binding("[",      "narrow_sidebar","Narrow"),
        Binding("]",      "widen_sidebar", "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(25)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="cs-body"):
            with Vertical(id="cs-sidebar"):
                yield Label("[b]Sections[/b]", id="cs-sidebar-title")
                yield ListView(
                    *[ListItem(Label(name), id=f"li-{panel_id}") for name, panel_id in _PANELS],
                    id="cs-nav",
                )
            with ContentSwitcher(initial="cs-overview", id="cs-switcher"):
                for _, panel_id in _PANELS:
                    yield Static(_CONTENT[panel_id], id=panel_id, classes="cs-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.watch_sidebar_width(self.sidebar_width)
        self.query_one(ListView).focus()

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#cs-sidebar").styles.width = f"{width}%"

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(60, self.sidebar_width + 5)

    def _switch_to(self, index: int) -> None:
        if 0 <= index < len(_PANELS):
            _, panel_id = _PANELS[index]
            self.query_one("#cs-switcher", ContentSwitcher).current = panel_id
            self.query_one("#cs-nav", ListView).index = index

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = self.query_one("#cs-nav", ListView).index
        if index is not None:
            self._switch_to(index)

    def action_show_panel_0(self) -> None: self._switch_to(0)
    def action_show_panel_1(self) -> None: self._switch_to(1)
    def action_show_panel_2(self) -> None: self._switch_to(2)
    def action_show_panel_3(self) -> None: self._switch_to(3)
    def action_show_panel_4(self) -> None: self._switch_to(4)


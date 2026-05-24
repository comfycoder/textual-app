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

    DEMOS = [
        ("Inputs & Forms",       "inputs",   "Input, TextArea, Checkbox, Switch, Select, RadioSet, Button"),
        ("Data Display",         "data",     "DataTable, RichLog, Markdown — across three tabs"),
        ("Layout & Navigation",  "layout",   "Grid layout, Collapsible sections, Tree widget"),
        ("Progress & Feedback",  "progress", "ProgressBar, Digits, Sparkline, LoadingIndicator, Toast, Modal"),
        ("Work Items Dashboard", "dashboard","The original two-pane dashboard with row drill-down"),
        ("File Manager",         "files",    "DirectoryTree navigation with file content preview"),
        ("API File Browser",     "apifiles", "Tree populated from API calls with lazy loading"),
        ("Live Dashboard",       "live",       "DataTable that auto-refreshes every 10 seconds via set_interval"),
        ("Command Palette",     "cmdpalette", "Fuzzy-search overlay — filter and trigger any action with Ctrl+P"),
        ("Streaming Log",       "logstream",  "RichLog fed by an async worker — live scrolling log output"),
        ("Multi-step Wizard",   "wizard",     "Step-by-step form with Back / Next / Submit and a review pane"),
        ("Markdown Report",     "report",       "Report viewer with Markdown tables, code blocks, and callouts"),
        ("Search & Filter",     "searchfilter", "Live Input filters a DataTable as you type"),
        ("Settings Screen",     "settings",     "Category sidebar with forms — resizable like other sidebars"),
        ("Concurrent Workers",  "workers",      "Multiple @work tasks running in parallel with individual progress bars"),
        ("Context Menu",        "contextmenu",  "Press Enter on a DataTable row to open a ModalScreen action menu"),
        ("Inline Edit",         "inlineedit",   "Press E on a row to edit its fields in a panel below the table"),
        ("Theme Toggle",        "theme",        "Toggle dark / light mode at runtime with app.dark"),
        ("Custom Widgets",      "customwidget",   "MetricCard and StatusBadge built from Widget with reactive render()"),
        ("Form Validation",     "formvalidation", "Inline field errors with live re-validation after first submit"),
        ("Pagination",          "pagination",     "Browse 100 items in fixed-size pages with keyboard and button nav"),
        ("Multi-select Table",  "multiselect",    "Space to toggle rows, A/D for all/none, bulk Run/Cancel actions"),
        ("Content Switcher",    "contentswitcher", "Sidebar ListView driving ContentSwitcher panel swap without new screens"),
        ("Help / Key Reference","helpkeys",        "Press ? to open a modal listing every active binding on the current screen"),
        ("OptionList",          "optionlist",       "OptionList with separators, highlight events, and selected-action feedback"),
        ("Masked Input",        "maskedinput",      "MaskedInput with date, time, phone, job-ID, IPv4, and hex-color templates"),
        ("Notification Drawer", "notifydrawer",     "Accumulate notify() calls in a slide-in history panel with Clear"),
        ("Autocomplete Input",  "autocomplete",     "Input + SuggestFromList — Tab or → accepts the inline suggestion"),
        ("SelectionList",       "selectionlist",    "Checkbox-style multi-select with built-in state, pre-selection, and .selected"),
        ("Toggle Button",       "togglebutton",     "Checkbox and RadioButton as standalone toggle widgets with Changed events"),
        ("Rule",                "rule",             "Horizontal and vertical dividers in every line style — solid, heavy, dashed, double"),
        ("Tooltip",             "tooltip",          "widget.tooltip = text — hover any widget to see its tooltip"),
        ("Pretty",              "pretty",           "Pretty widget renders any Python object as syntax-highlighted formatted output"),
        ("Link",                "link",             "Clickable Link widgets that open URLs via app.open_url()"),
        ("Log vs RichLog",      "log",              "Plain Log (no markup) side-by-side with RichLog — write, clear, max_lines"),
        ("Tabs (standalone)",   "tabs",             "Tabs widget driving ContentSwitcher manually — dynamic add/remove at runtime"),
        ("Master / Detail",          "masterdetail",         "Navigating a master DataTable populates a child step table in real time"),
        ("Master / Detail (vertical)", "masterdetailvertical", "Same pattern with master table above and detail table below"),
        ("Form + Table",               "formtable",            "Selecting a row in the grid populates the edit form above it"),
        ("Label Form",                 "labelform",            "Each field on its own line — label on the left, input on the right"),
        ("Search → Grid → Edit",       "searchgrid",           "Filter bar, pageable results grid, row opens a full edit form"),
        ("Card Patterns",              "cards",                "Alert, Profile, Progress, Action, and Key-Value cards built with compose()"),
        ("Card Patterns II",           "cards2",               "Timeline, Pricing, Sparkline, Activity, and Comparison cards"),
        ("DICOM → NRRD",               "dicomnrrd",            "Batch conversion dashboard: progress, volume metadata, validation alerts, activity log"),
    ]

    sidebar_width: reactive[int] = reactive(30)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="gallery-body"):
            yield ListView(
                *[ListItem(Label(name), id=f"demo-{key}") for name, key, _ in self.DEMOS],
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
        if index is not None and index < len(self.DEMOS):
            _, _, desc = self.DEMOS[index]
            self.query_one("#gallery-desc", Static).update(f"\n{desc}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = self.query_one(ListView).index
        if index is None or index >= len(self.DEMOS):
            return
        _, key, _ = self.DEMOS[index]
        self._open_demo(key)

    def _open_demo(self, key: str) -> None:
        from your_cli.tui.router import navigate
        navigate(self.app, key)

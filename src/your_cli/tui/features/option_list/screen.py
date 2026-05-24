"""Demo: OptionList — built-in highlight, separators, and selection."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import (
    Footer,
    Header,
    Label,
    OptionList,
    Static,
)
from textual.widgets._option_list import Option

_ACTIONS = [
    ("Run Job",        "run",     "Submit the selected work item for execution"),
    ("Pause Job",      "pause",   "Suspend execution without losing progress"),
    ("Cancel Job",     "cancel",  "Terminate and discard the job"),
    None,  # separator
    ("Duplicate",      "dup",     "Clone this job with identical parameters"),
    ("Edit Config",    "edit",    "Open the job configuration for editing"),
    ("View Logs",      "logs",    "Stream the live log output"),
    None,  # separator
    ("Download Output","dl",      "Export result artefacts to local disk"),
    ("Share Link",     "share",   "Copy a shareable deep-link to clipboard"),
    None,  # separator
    ("Archive",        "archive", "Move to archive — hidden from active lists"),
    ("Delete",         "delete",  "Permanently remove this job record"),
]


class OptionListDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="ol-body"):
            with Vertical(id="ol-left"):
                yield Label("[b]Job Actions[/b]", classes="demo-label")
                yield Label(
                    "[dim]↑↓ Navigate · Enter / click to select[/dim]",
                    id="ol-nav-hint",
                )
                ol = OptionList(id="ol-list")
                for item in _ACTIONS:
                    if item is None:
                        ol.add_option(None)
                    else:
                        label, id_, _ = item
                        ol.add_option(Option(label, id=id_))
                yield ol
            with Vertical(id="ol-right"):
                yield Label("[b]Action Detail[/b]", classes="demo-label")
                yield Static("Select an action to see its description.", id="ol-desc")
                yield Static("", id="ol-last", classes="ol-result")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        opt_id = event.option.id
        desc = next(
            (d for item in _ACTIONS if item is not None and item[1] == opt_id for d in [item[2]]),
            "",
        )
        self.query_one("#ol-desc", Static).update(desc or "")

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        opt_id = event.option.id
        label = next(
            (item[0] for item in _ACTIONS if item is not None and item[1] == opt_id),
            opt_id,
        )
        self.query_one("#ol-last", Static).update(
            f"[green]✓[/green]  Last selected: [b]{label}[/b]"
        )
        self.notify(f"Action: {label}", title="Selected")


"""Demo: Inputs & Forms."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Select,
    Static,
    Switch,
    TextArea,
)


class InputsDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="inputs-body"):
            yield Static("[b]Text Input[/b]", classes="demo-label")
            yield Input(placeholder="Type something...", id="text-input")

            yield Static("[b]Password Input[/b]", classes="demo-label")
            yield Input(placeholder="Password", password=True, id="pass-input")

            yield Static("[b]Number Input (validated)[/b]", classes="demo-label")
            yield Input(placeholder="Enter a number", type="number", id="num-input")

            yield Static("[b]Text Area[/b]", classes="demo-label")
            yield TextArea("Edit this multi-line text.\nSecond line here.", id="textarea")

            yield Static("[b]Checkbox & Switch[/b]", classes="demo-label")
            with Horizontal(classes="demo-row"):
                yield Checkbox("Enable feature", id="checkbox")
                yield Switch(value=True, id="switch")
                yield Label("  Toggle", id="switch-label")

            yield Static("[b]Select Dropdown[/b]", classes="demo-label")
            yield Select(
                [("Option A", "a"), ("Option B", "b"), ("Option C", "c")],
                prompt="Choose an option",
                id="select",
            )

            yield Static("[b]Radio Buttons[/b]", classes="demo-label")
            with RadioSet(id="radio"):
                yield RadioButton("Low priority")
                yield RadioButton("Medium priority", value=True)
                yield RadioButton("High priority")

            yield Static("[b]Buttons[/b]", classes="demo-label")
            with Horizontal(classes="demo-row"):
                yield Button("Primary", variant="primary", id="btn-primary")
                yield Button("Warning", variant="warning", id="btn-warning")
                yield Button("Error", variant="error", id="btn-error")
                yield Button("Default", id="btn-default")

            yield Static("", id="feedback")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one("#feedback", Static).update(
            f"[dim]Button pressed:[/dim] [b]{event.button.label}[/b]  "
            f"(variant={event.button.variant})"
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()

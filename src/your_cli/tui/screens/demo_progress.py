"""Demo: Progress & Feedback."""

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Digits,
    Footer,
    Header,
    Label,
    LoadingIndicator,
    ProgressBar,
    Sparkline,
    Static,
)

_SPARKLINE_DATA = [2, 5, 3, 8, 6, 4, 9, 7, 3, 5, 8, 6, 2, 7, 9, 4, 6, 8, 3, 7]


class ConfirmModal(ModalScreen[bool]):
    BINDINGS = [Binding("escape", "dismiss_false", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-body"):
            yield Static("[b]Confirm Action[/b]", classes="panel-title")
            yield Static("Are you sure you want to proceed?")
            with Horizontal(classes="demo-row"):
                yield Button("Confirm", variant="error", id="btn-yes")
                yield Button("Cancel", variant="primary", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")

    def action_dismiss_false(self) -> None:
        self.dismiss(False)


class ProgressDemoScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="progress-body"):
            yield Static("[b]Progress Bar[/b]", classes="demo-label")
            yield ProgressBar(total=100, id="demo-bar")
            with Horizontal(classes="demo-row"):
                yield Button("Run", variant="primary", id="btn-run")
                yield Button("Reset", id="btn-reset")

            yield Static("[b]Digits[/b]", classes="demo-label")
            yield Digits("3.14159", id="demo-digits")

            yield Static("[b]Sparkline[/b]", classes="demo-label")
            yield Sparkline(_SPARKLINE_DATA, id="demo-sparkline")

            yield Static("[b]Loading Indicator[/b]", classes="demo-label")
            with Horizontal(classes="demo-row"):
                yield LoadingIndicator(id="demo-loader")
                yield Label("  Waiting for response...", id="loader-label")

            yield Static("[b]Toast & Modal[/b]", classes="demo-label")
            with Horizontal(classes="demo-row"):
                yield Button("Show Toast", variant="primary", id="btn-toast")
                yield Button("Show Modal", variant="warning", id="btn-modal")

            yield Static("", id="modal-result")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-run":
                self._run_progress()
            case "btn-reset":
                self.query_one(ProgressBar).update(progress=0)
            case "btn-toast":
                self.notify("Operation completed successfully.", title="Success")
            case "btn-modal":
                self.app.push_screen(ConfirmModal(), self._on_modal_result)

    def _on_modal_result(self, confirmed: bool) -> None:
        msg = "[green]Confirmed[/green] — action would proceed." if confirmed else "[dim]Cancelled.[/dim]"
        self.query_one("#modal-result", Static).update(msg)

    @work(exclusive=True)
    async def _run_progress(self) -> None:
        bar = self.query_one(ProgressBar)
        bar.update(progress=0)
        for _ in range(100):
            await asyncio.sleep(0.04)
            bar.advance(1)

    def action_go_back(self) -> None:
        self.app.pop_screen()

"""Demo: Toggle Button — Checkbox and RadioButton (inside RadioSet) toggle widgets."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Label,
    RadioButton,
    RadioSet,
    Rule,
    Static,
)


class ToggleButtonDemoScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="tb-body"):
            with ScrollableContainer(id="tb-left"):
                yield Static("[b]Checkbox[/b]", classes="demo-label")
                yield Static(
                    "[dim]Each checkbox is independent. "
                    "Space or click to toggle.[/dim]",
                    id="tb-cb-hint",
                )
                yield Rule()
                yield Checkbox("Enable auto-retry",    id="cb-retry",    value=True)
                yield Checkbox("Send notifications",   id="cb-notify",   value=True)
                yield Checkbox("Priority queue",       id="cb-priority", value=False)
                yield Checkbox("GPU required",         id="cb-gpu",      value=False)
                yield Checkbox("Archive on complete",  id="cb-archive",  value=False)
                yield Checkbox("Dry run (no write)",   id="cb-dryrun",   value=False)

                yield Static("[b]RadioButton inside RadioSet[/b]", classes="demo-label")
                yield Static(
                    "[dim]RadioButtons inside a RadioSet are mutually exclusive — "
                    "selecting one automatically deselects the others.[/dim]",
                    id="tb-rb-hint",
                )
                yield Rule()
                with RadioSet(id="rb-priority"):
                    yield RadioButton("Low priority",    id="rb-low")
                    yield RadioButton("Medium priority", id="rb-medium")
                    yield RadioButton("High priority",   id="rb-high")
                    yield RadioButton("Critical",        id="rb-crit")

                with Horizontal(id="tb-actions"):
                    yield Button("Submit config", variant="primary", id="btn-tb-submit")
                    yield Button("Reset",                            id="btn-tb-reset")

            with Vertical(id="tb-right"):
                yield Static("[b]Current State[/b]", classes="demo-label")
                yield Static("", id="tb-state")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#rb-medium", RadioButton).value = True
        self._refresh_state()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self._refresh_state()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self._refresh_state()

    def _refresh_state(self) -> None:
        checked = [
            cb_id for cb_id in
            ("cb-retry", "cb-notify", "cb-priority", "cb-gpu", "cb-archive", "cb-dryrun")
            if self.query_one(f"#{cb_id}", Checkbox).value
        ]
        rs = self.query_one("#rb-priority", RadioSet)
        pressed = rs.pressed_button
        priority = pressed.label.plain.lower() if pressed else "—"

        lines = ["[b]Checkboxes:[/b]"]
        for cb_id in ("cb-retry", "cb-notify", "cb-priority", "cb-gpu", "cb-archive", "cb-dryrun"):
            val = self.query_one(f"#{cb_id}", Checkbox).value
            icon  = "[green]✓[/green]" if val else "[dim]✗[/dim]"
            label = cb_id.replace("cb-", "").replace("-", " ")
            lines.append(f"  {icon}  {label}")

        lines.append("")
        lines.append(f"[b]Priority:[/b]  {priority}")

        self.query_one("#tb-state", Static).update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-tb-submit":
            checked = [
                cb_id.replace("cb-", "")
                for cb_id in ("cb-retry", "cb-notify", "cb-priority", "cb-gpu", "cb-archive", "cb-dryrun")
                if self.query_one(f"#{cb_id}", Checkbox).value
            ]
            self.notify(
                f"Options: {', '.join(checked) or 'none'}",
                title="Config Submitted",
                severity="information",
            )
        elif event.button.id == "btn-tb-reset":
            defaults = {"cb-retry": True, "cb-notify": True}
            for cb_id in ("cb-retry", "cb-notify", "cb-priority", "cb-gpu", "cb-archive", "cb-dryrun"):
                self.query_one(f"#{cb_id}", Checkbox).value = defaults.get(cb_id, False)
            self.query_one("#rb-medium", RadioButton).value = True

    def action_go_back(self) -> None:
        self.app.pop_screen()

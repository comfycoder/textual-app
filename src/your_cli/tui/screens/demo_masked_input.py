"""Demo: MaskedInput — date, time, phone, and job-ID format templates."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, MaskedInput, Static

# MaskedInput template characters:
#   9  required digit (0-9)
#   0  optional digit
#   A  required letter (A-Za-z)
#   a  optional letter
#   N  required alphanumeric
#   n  optional alphanumeric
#   X  required any non-space
#   Literal characters become separators (auto-inserted)

_FIELDS = [
    ("Date",       "99-AAA-9999",    "mi-date",  "DD-MMM-YYYY  e.g. 31-DEC-2024"),
    ("Time",       "99:99:99",       "mi-time",  "HH:MM:SS  e.g. 14:30:00"),
    ("Phone",      "(999) 999-9999", "mi-phone", "US format  e.g. (919) 555-0123"),
    ("Job ID",     "AA-XXXX-999",    "mi-jobid", "e.g. WI-ABCD-042"),
    ("IPv4",       "990.990.990.990","mi-ip",    "e.g. 192.168.001.001"),
    ("Hex Color",  "#HHHHHH",        "mi-hex",   "e.g. #FF5733"),
]


class MaskedInputDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "submit",  "Submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="mi-body"):
            yield Static("[b]Masked Input Demo[/b]", classes="demo-label")
            yield Static(
                "Each field enforces a format template. Separators are inserted "
                "automatically as you type — only the data characters need to be "
                "entered.\n",
                id="mi-intro",
            )
            for label_text, template, field_id, hint in _FIELDS:
                yield Label(f"{label_text}  [dim]{hint}[/dim]")
                yield MaskedInput(template, id=field_id)
                yield Static("", id=f"{field_id}-err", classes="field-error")

            yield Button("Submit", variant="primary", id="btn-mi-submit")
            yield Static("", id="mi-result")
        yield Footer()

    def action_submit(self) -> None:
        self.query_one("#btn-mi-submit", Button).press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "btn-mi-submit":
            return

        all_valid = True
        for _, _, field_id, _ in _FIELDS:
            widget = self.query_one(f"#{field_id}", MaskedInput)
            err = self.query_one(f"#{field_id}-err", Static)
            val = widget.value.strip()
            if widget.is_valid:
                err.update("[green]✓[/green]")
            elif not val:
                err.update("[dim]—  optional[/dim]")
            else:
                err.update("[red]⚠  Incomplete — fill all required positions[/red]")
                all_valid = False

        if all_valid:
            self.notify("All fields valid!", title="Submitted", severity="information")
            self.query_one("#mi-result", Static).update(
                "[green]Form submitted successfully.[/green]"
            )
        else:
            self.query_one("#mi-result", Static).update(
                "[red]Please fix errors above.[/red]"
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

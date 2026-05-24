"""Demo: Rule — horizontal and vertical dividers with every line style."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from your_cli.tui.feature_screen import FeatureScreen
from typing import Literal

from textual.widgets import Footer, Header, Label, Rule, Static

_LineStyle = Literal["ascii", "blank", "dashed", "double", "heavy", "hidden", "none", "solid", "thick"]
_H_STYLES: list[_LineStyle] = ["solid", "heavy", "double", "dashed", "ascii"]
_V_STYLES: list[_LineStyle] = ["solid", "heavy", "double", "dashed", "ascii"]


class RuleDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="rule-body"):
            yield Static("[b]Rule — Horizontal[/b]", classes="demo-label")
            yield Static("[dim]Five line styles, horizontal orientation[/dim]")

            for style in _H_STYLES:
                yield Label(f"[dim]{style}[/dim]", classes="rule-style-label")
                yield Rule(line_style=style)

            yield Static("[b]Rule — Vertical[/b]", classes="demo-label")
            yield Static("[dim]Vertical rules separate columns[/dim]")
            with Horizontal(id="rule-v-row"):
                yield Static("Left panel\nwith content\nhere", classes="rule-panel")
                yield Rule(orientation="vertical", line_style="solid")
                yield Static("Middle\npanel", classes="rule-panel")
                yield Rule(orientation="vertical", line_style="heavy")
                yield Static("Right panel\ncontent", classes="rule-panel")

            yield Static("[b]Rule in a Form[/b]", classes="demo-label")
            yield Static("[dim]Rules visually group form sections[/dim]")
            with Vertical(id="rule-form"):
                yield Label("[b]Contact Details[/b]")
                yield Rule()
                yield Label("Name")
                yield Static("[dim]Alice Johnson[/dim]", classes="rule-field")
                yield Label("Email")
                yield Static("[dim]alice@jhu.edu[/dim]", classes="rule-field")
                yield Rule(line_style="dashed")
                yield Label("[b]Job Settings[/b]")
                yield Rule()
                yield Label("Type")
                yield Static("[dim]training[/dim]", classes="rule-field")
                yield Label("Tenant")
                yield Static("[dim]jhu[/dim]", classes="rule-field")
        yield Footer()


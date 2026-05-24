"""Demo: Link — clickable widgets that open URLs via app.open_url()."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Footer, Header, Link, Rule, Static


class LinkDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="lk-body"):
            yield Static("[b]Link Widget Demo[/b]", classes="demo-label")
            yield Static(
                "Links open URLs in the system browser via [b]app.open_url()[/b].\n"
                "Navigate with Tab, activate with Enter or click.\n",
                id="lk-intro",
            )

            yield Static("[b]Documentation[/b]", classes="demo-label")
            yield Rule()
            yield Link("Textual Documentation",         url="https://textual.textualize.io")
            yield Link("Textual Widget Reference",      url="https://textual.textualize.io/widgets/")
            yield Link("Textual CSS Reference",         url="https://textual.textualize.io/css_types/")
            yield Link("GitHub — Textualize/textual",   url="https://github.com/Textualize/textual")

            yield Static("[b]Platform Links[/b]", classes="demo-label")
            yield Rule()
            yield Link("AIQ Solutions",                 url="https://www.aiq-solutions.com")
            yield Link("Johns Hopkins University",      url="https://www.jhu.edu")
            yield Link("UNC Chapel Hill",               url="https://www.unc.edu")
            yield Link("Mayo Clinic",                   url="https://www.mayoclinic.org")

            yield Static("[b]Custom Label vs URL[/b]", classes="demo-label")
            yield Rule()
            yield Static(
                "[dim]When [b]url[/b] is omitted the text itself is used as the URL.[/dim]\n"
                "[dim]When [b]url[/b] is provided the label can be any text.[/dim]\n"
            )
            yield Link(
                "Open the Textual showcase",
                url="https://github.com/Textualize/textual/tree/main/examples",
                id="lk-custom",
            )
            yield Link("https://textual.textualize.io")   # text == url

        yield Footer()


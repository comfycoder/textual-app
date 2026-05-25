"""Demo: Reactive Attributes — reactive, watch_, and fan-out patterns.

Three self-contained examples that show how Textual's reactive system works:

  Pattern 1 — Counter (reactive + watch_)
      A single reactive int.  Textual calls watch_count() on every change,
      which updates the display.  No manual refresh() needed.

  Pattern 2 — Color mixer (multiple reactives → shared helper)
      Three separate reactive ints (r, g, b).  Each has its own watch_*
      method, but all three delegate to _refresh_color() so the preview
      updates whenever any channel changes.

  Pattern 3 — Text inputs → reactive → fan-out
      Two Input widgets write into reactives via on_input_changed.  A single
      pair of watch_* methods then fans out to three different display
      widgets that all update simultaneously.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Label, Static

from your_cli.tui.feature_screen import FeatureScreen

__all__ = ["ReactivesDemoScreen"]


class ReactivesDemoScreen(FeatureScreen):
    """Three reactive patterns in one scrollable screen."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    # ── Reactive declarations ──────────────────────────────────────────────────
    #
    # Class-level reactive attributes.  Textual automatically wires each one
    # to its watch_<name>() method when the value changes.

    count:  reactive[int] = reactive(0)
    r:      reactive[int] = reactive(100)
    g:      reactive[int] = reactive(149)
    b:      reactive[int] = reactive(237)
    first:  reactive[str] = reactive("")
    surname: reactive[str] = reactive("")

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="ra-body"):

            # ── Pattern 1: Counter ────────────────────────────────
            yield Static(
                "[b]Pattern 1 — reactive + watch_[/b]",
                classes="ra-section",
            )
            yield Static(
                "[dim]Declare [b]count: reactive[int] = reactive(0)[/b]. "
                "Textual calls [b]watch_count(new_value)[/b] on every assignment — "
                "no [b]refresh()[/b] needed.[/dim]",
                classes="ra-hint",
            )
            yield Static("Count: [b]0[/b]", id="ra-count-display", classes="ra-display")
            with Horizontal(classes="ra-btn-row"):
                yield Button("−5",    id="btn-count-m5",    classes="ra-btn")
                yield Button("−1",    id="btn-count-m1",    classes="ra-btn")
                yield Button("Reset", id="btn-count-reset", classes="ra-btn")
                yield Button("+1",    id="btn-count-p1",    classes="ra-btn")
                yield Button("+5",    id="btn-count-p5",    classes="ra-btn")

            # ── Pattern 2: Color mixer ────────────────────────────
            yield Static(
                "[b]Pattern 2 — multiple reactives → shared helper[/b]",
                classes="ra-section",
            )
            yield Static(
                "[dim]Each channel ([b]r[/b], [b]g[/b], [b]b[/b]) is its own reactive. "
                "All three [b]watch_*[/b] methods call [b]_refresh_color()[/b] so the "
                "preview updates whenever any channel changes.[/dim]",
                classes="ra-hint",
            )
            with Horizontal(id="ra-color-area"):
                with Vertical(id="ra-channels"):
                    for ch_label, ch_id in (("R", "r"), ("G", "g"), ("B", "b")):
                        with Horizontal(classes="ra-channel-row"):
                            yield Static(ch_label, classes="ra-channel-label")
                            yield Button("−", id=f"btn-{ch_id}-dec",
                                         classes="ra-small-btn")
                            yield Static("000", id=f"ra-{ch_id}-val",
                                         classes="ra-channel-val")
                            yield Button("+", id=f"btn-{ch_id}-inc",
                                         classes="ra-small-btn")
                yield Static("", id="ra-color-swatch")
                with Vertical(id="ra-color-info"):
                    yield Static("", id="ra-color-hex")
                    yield Static(
                        "[dim]Use ± buttons to mix channels.[/dim]",
                        id="ra-color-tip",
                    )

            # ── Pattern 3: Input → reactive → fan-out ─────────────
            yield Static(
                "[b]Pattern 3 — Input → reactive → fan-out[/b]",
                classes="ra-section",
            )
            yield Static(
                "[dim][b]on_input_changed[/b] writes to [b]first[/b] and [b]surname[/b]. "
                "Their [b]watch_*[/b] methods both call [b]_refresh_name()[/b], which "
                "updates three separate display widgets in one pass.[/dim]",
                classes="ra-hint",
            )
            with Horizontal(classes="ra-name-row"):
                with Vertical(classes="ra-name-field"):
                    yield Label("First name")
                    yield Input(id="ra-first", placeholder="Alice")
                with Vertical(classes="ra-name-field"):
                    yield Label("Last name")
                    yield Input(id="ra-last", placeholder="Smith")
            yield Static("[dim](waiting for input…)[/dim]",
                         id="ra-greeting",  classes="ra-display")
            yield Static("[dim](waiting for input…)[/dim]",
                         id="ra-initials",  classes="ra-display")
            yield Static("[dim](waiting for input…)[/dim]",
                         id="ra-namelength", classes="ra-display")

        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        # Trigger initial render of color preview without waiting for a button click
        self._refresh_color()

    # ── Button handler ─────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            # Pattern 1 — counter
            case "btn-count-m5":
                self.count = max(-999, self.count - 5)
            case "btn-count-m1":
                self.count -= 1
            case "btn-count-reset":
                self.count = 0
            case "btn-count-p1":
                self.count += 1
            case "btn-count-p5":
                self.count = min(999, self.count + 5)
            # Pattern 2 — color channels (step of 10 per click)
            case "btn-r-dec":
                self.r = max(0, self.r - 10)
            case "btn-r-inc":
                self.r = min(255, self.r + 10)
            case "btn-g-dec":
                self.g = max(0, self.g - 10)
            case "btn-g-inc":
                self.g = min(255, self.g + 10)
            case "btn-b-dec":
                self.b = max(0, self.b - 10)
            case "btn-b-inc":
                self.b = min(255, self.b + 10)

    # ── Input handler ──────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "ra-first":
            self.first = event.value
        elif event.input.id == "ra-last":
            self.surname = event.value

    # ── Watchers ───────────────────────────────────────────────────────────────

    def watch_count(self, value: int) -> None:
        sign = "+" if value > 0 else ""
        self.query_one("#ra-count-display", Static).update(
            f"Count: [b]{sign}{value}[/b]"
        )

    # All three color watchers delegate to the shared helper — no duplication.
    def watch_r(self, _: int) -> None:
        self._refresh_color()

    def watch_g(self, _: int) -> None:
        self._refresh_color()

    def watch_b(self, _: int) -> None:
        self._refresh_color()

    def watch_first(self, _: str) -> None:
        self._refresh_name()

    def watch_surname(self, _: str) -> None:
        self._refresh_name()

    # ── Shared render helpers ──────────────────────────────────────────────────

    def _refresh_color(self) -> None:
        """Recompute hex color and push it to the swatch + info panel."""
        hex_color = f"#{self.r:02x}{self.g:02x}{self.b:02x}"
        # Inline style wins over any CSS — sets the background directly.
        self.query_one("#ra-color-swatch").styles.background = hex_color
        self.query_one("#ra-color-hex", Static).update(
            f"[b]{hex_color.upper()}[/b]\n"
            f"[dim]rgb({self.r}, {self.g}, {self.b})[/dim]"
        )
        # Keep channel value labels in sync
        for val, ch in ((self.r, "r"), (self.g, "g"), (self.b, "b")):
            self.query_one(f"#ra-{ch}-val", Static).update(f"{val:3d}")

    def _refresh_name(self) -> None:
        """Recompute all three name-derived displays from first + surname."""
        first = self.first.strip()
        last  = self.surname.strip()
        full  = f"{first} {last}".strip()

        if not full:
            placeholder = "[dim](waiting for input…)[/dim]"
            for wid in ("#ra-greeting", "#ra-initials", "#ra-namelength"):
                self.query_one(wid, Static).update(placeholder)
            return

        initials = "".join(part[0].upper() for part in full.split() if part)
        self.query_one("#ra-greeting",   Static).update(f"Hello, [b]{full}[/b]!")
        self.query_one("#ra-initials",   Static).update(f"Initials: [b]{initials}[/b]")
        self.query_one("#ra-namelength", Static).update(
            f"Name length: [b]{len(full)}[/b] characters"
        )

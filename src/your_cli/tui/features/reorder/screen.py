"""Demo: Drag-to-reorder list — keyboard reordering with Alt+Up / Alt+Down.

Textual has no built-in drag-and-drop, but a fluid reorder UX can be built
entirely from keyboard bindings:

  Alt+↑   — move the highlighted item one position up
  Alt+↓   — move the highlighted item one position down

The list is rebuilt from a Python list on every swap, then ListView.index
is reset to follow the moved item.  Rebuilding the whole widget on each
swap keeps the code simple; for very long lists, targeted DOM surgery would
be more efficient.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static

from your_cli.tui.feature_screen import FeatureScreen

__all__ = ["ReorderDemoScreen"]

# ── Stage data ─────────────────────────────────────────────────────────────────

_STAGES: list[tuple[str, str]] = [
    ("Preprocessing",   "Load and normalise DICOM data"),
    ("Validation",      "Schema and range checks"),
    ("Segmentation",    "Tissue boundary detection"),
    ("Registration",    "Multi-atlas alignment"),
    ("Inference",       "Model prediction pass"),
    ("Post-processing", "Smoothing and artefact removal"),
    ("Export",          "Write NRRD / NIfTI output"),
    ("Notification",    "Webhook and e-mail dispatch"),
]


# ── Screen ─────────────────────────────────────────────────────────────────────

class ReorderDemoScreen(FeatureScreen):
    """Pipeline stage list that can be reordered with Alt+↑/↓."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("alt+up",   "move_up",   "Move up"),
        Binding("alt+down", "move_down", "Move down"),
    ]

    def __init__(self) -> None:
        super().__init__()
        # Working order stored as indices into _STAGES so the label/description
        # pairing never drifts when items are swapped.
        self._order: list[int] = list(range(len(_STAGES)))

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="ro-body"):
            yield Static(
                "[b]Pipeline Stage Order[/b]  "
                "[dim][b]Alt+↑[/b] / [b]Alt+↓[/b] to reorder · "
                "focus the list first with a click or Tab[/dim]",
                id="ro-title",
            )
            yield ListView(id="ro-list")
            yield Static("", id="ro-order", classes="ro-result")
            with Horizontal(id="ro-actions"):
                yield Button("Reset order",  id="btn-ro-reset",  classes="ro-btn")
                yield Button("Copy as list", id="btn-ro-copy",   classes="ro-btn")
        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._rebuild(focus_idx=0)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _rebuild(self, focus_idx: int = 0) -> None:
        """Clear and repopulate the ListView, then restore focus to focus_idx."""
        lv = self.query_one("#ro-list", ListView)
        lv.clear()
        for i, stage_idx in enumerate(self._order):
            name, desc = _STAGES[stage_idx]
            lv.append(
                ListItem(
                    Label(
                        f"[dim]{i + 1:2d}.[/dim]  [b]{name}[/b]  "
                        f"[dim]— {desc}[/dim]"
                    )
                )
            )
        lv.index = focus_idx
        self._update_order_display()

    def _update_order_display(self) -> None:
        names = [_STAGES[i][0] for i in self._order]
        self.query_one("#ro-order", Static).update(
            "[dim]Order →[/dim]  " + " → ".join(f"[b]{n}[/b]" for n in names)
        )

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_move_up(self) -> None:
        lv = self.query_one("#ro-list", ListView)
        idx = lv.index
        if idx is None or idx == 0:
            return
        self._order[idx], self._order[idx - 1] = self._order[idx - 1], self._order[idx]
        self._rebuild(focus_idx=idx - 1)

    def action_move_down(self) -> None:
        lv = self.query_one("#ro-list", ListView)
        idx = lv.index
        if idx is None or idx >= len(self._order) - 1:
            return
        self._order[idx], self._order[idx + 1] = self._order[idx + 1], self._order[idx]
        self._rebuild(focus_idx=idx + 1)

    # ── Button handler ─────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ro-reset":
            self._order = list(range(len(_STAGES)))
            self._rebuild(focus_idx=0)
        elif event.button.id == "btn-ro-copy":
            text = ", ".join(_STAGES[i][0] for i in self._order)
            self.app.copy_to_clipboard(text)
            self.notify("Stage order copied to clipboard", timeout=2)

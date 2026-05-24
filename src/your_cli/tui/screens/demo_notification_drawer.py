"""Demo: Notification drawer — collects app notifications into a slide-in panel."""

import random
from datetime import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, RichLog, Static

_SAMPLE_EVENTS = [
    ("information", "Job wi-042 completed",          "Training finished in 4m 12s"),
    ("warning",     "GPU memory high on node-2",     "Usage at 91% — approaching limit"),
    ("error",       "Job wi-039 failed",             "OOM error during preprocessing step 3"),
    ("information", "New tenant jhu connected",      "3 nodes registered in the broker"),
    ("warning",     "Scheduler lag detected",        "Queue depth > 50 — consider scaling"),
    ("information", "Export ready: wi-037",          "Results available for download"),
    ("error",       "API timeout on mayo endpoint",  "Retry 3/3 failed — circuit open"),
    ("information", "Maintenance window starting",   "Scheduled downtime in 10 minutes"),
]

_SEV_COLOR = {
    "information": "cyan",
    "warning":     "yellow",
    "error":       "red",
}
_SEV_ICON = {
    "information": "ℹ",
    "warning":     "⚠",
    "error":       "✗",
}


class NotificationDrawerDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "go_back",       "Back"),
        Binding("n",      "toggle_drawer", "Drawer"),
        Binding("c",      "clear_drawer",  "Clear"),
    ]

    _drawer_open: reactive[bool] = reactive(False)
    _count: reactive[int]        = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="nd-body"):
            with Vertical(id="nd-main"):
                yield Static("[b]Notification Drawer Demo[/b]", classes="demo-label")
                yield Static(
                    "Press the buttons below to fire different notification types.\n"
                    "They appear as standard toasts AND accumulate in the drawer.\n"
                    "Press [b]N[/b] or the Drawer button to open/close the history panel.",
                    id="nd-intro",
                )
                with Horizontal(id="nd-buttons"):
                    yield Button("Info",    variant="default",   id="btn-nd-info")
                    yield Button("Warning", variant="warning",   id="btn-nd-warn")
                    yield Button("Error",   variant="error",     id="btn-nd-err")
                    yield Button("Random",  variant="primary",   id="btn-nd-rand")
                    yield Button("Drawer ▶", variant="default",  id="btn-nd-toggle")
                yield Static("", id="nd-badge")
            with Vertical(id="nd-drawer"):
                with Horizontal(id="nd-drawer-header"):
                    yield Label("[b]Notification History[/b]", id="nd-drawer-title")
                    yield Button("✕", id="btn-nd-close", classes="nd-close-btn")
                yield RichLog(id="nd-log", highlight=True, markup=True, wrap=True)
                yield Button("Clear all", id="btn-nd-clear", classes="nd-clear-btn")
        yield Footer()

    def on_mount(self) -> None:
        self._set_drawer(False)

    # ── Drawer open/close ────────────────────────────────────────

    def watch__drawer_open(self, open: bool) -> None:
        self._set_drawer(open)

    def _set_drawer(self, open: bool) -> None:
        drawer = self.query_one("#nd-drawer")
        drawer.display = open
        lbl = "Drawer ◀" if open else "Drawer ▶"
        self.query_one("#btn-nd-toggle", Button).label = lbl

    def action_toggle_drawer(self) -> None:
        self._drawer_open = not self._drawer_open

    def action_clear_drawer(self) -> None:
        self.query_one(RichLog).clear()
        self._count = 0
        self._update_badge()

    # ── Notification helpers ─────────────────────────────────────

    def _fire(self, severity: str, title: str, message: str) -> None:
        self.notify(message, title=title, severity=severity)  # type: ignore[arg-type]
        color = _SEV_COLOR.get(severity, "white")
        icon  = _SEV_ICON.get(severity, "•")
        ts    = datetime.now().strftime("%H:%M:%S")
        log   = self.query_one(RichLog)
        log.write(
            f"[dim]{ts}[/dim]  [{color}]{icon}[/{color}]  "
            f"[b]{title}[/b]  [dim]{message}[/dim]"
        )
        self._count += 1
        self._update_badge()

    def _update_badge(self) -> None:
        n = self._count
        if n == 0:
            badge = ""
        else:
            badge = f"[dim]{n} notification{'s' if n != 1 else ''} in drawer[/dim]"
        self.query_one("#nd-badge", Static).update(badge)

    # ── Button handlers ──────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-nd-info":
                self._fire("information", "Info", "Job wi-042 completed in 4m 12s")
            case "btn-nd-warn":
                self._fire("warning", "Warning", "GPU memory at 91% on node-2")
            case "btn-nd-err":
                self._fire("error", "Error", "Job wi-039 failed — OOM in step 3")
            case "btn-nd-rand":
                sev, title, msg = random.choice(_SAMPLE_EVENTS)
                self._fire(sev, title, msg)
            case "btn-nd-toggle":
                self.action_toggle_drawer()
            case "btn-nd-close":
                self._drawer_open = False
            case "btn-nd-clear":
                self.action_clear_drawer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

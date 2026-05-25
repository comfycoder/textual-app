"""Six reusable modal dialog patterns for the modal dialogs demo.

Each class is a self-contained ModalScreen[T] — the type parameter is the
value returned via self.dismiss(value) when the user makes a choice.

Patterns covered
────────────────
AlertModal(ModalScreen[None])       — inform; severity-coloured icon + title
ConfirmModal(ModalScreen[bool])     — confirm a destructive action
InputModal(ModalScreen[str|None])   — prompt for a single text value
SelectionModal(ModalScreen[str|None]) — pick one item from a list
FormModal(ModalScreen[dict|None])   — submit a small multi-field form
ProgressModal(ModalScreen[str])     — blocking-operation feedback; auto-dismisses
"""

from __future__ import annotations

import asyncio
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Select,
    Static,
)

from your_cli.tui.features.search_grid._data import (
    _PRIORITY_OPTS,
    _TENANT_OPTS,
    _TYPE_OPTS,
)


# ── Alert ──────────────────────────────────────────────────────────────────────

_ALERT_STYLES: dict[str, tuple[str, str]] = {
    "info":    ("ℹ", "$primary"),
    "warning": ("⚠", "$warning"),
    "error":   ("✖", "$error"),
    "success": ("✔", "$success"),
}


class AlertModal(ModalScreen[None]):
    """Inform the user of an event.  No choice required — just dismiss.

    Usage::

        await self.app.push_screen_wait(
            AlertModal("warning", "Disk space low",
                       "Node gpu-07 is at 87 % capacity.")
        )
    """

    DEFAULT_CSS = """
    AlertModal { align: center middle; }
    #alert-body {
        width: 52; height: auto; padding: 2 4;
        border: solid $primary; background: $surface;
    }
    #alert-header { height: auto; margin-bottom: 1; }
    #alert-icon   { width: auto; margin-right: 1; }
    #alert-title  { width: 1fr; }
    #alert-msg    { margin-bottom: 2; color: $text-muted; }
    """

    BINDINGS = [Binding("escape", "ok", "OK")]

    def __init__(
        self,
        severity: str,
        title: str,
        message: str,
    ) -> None:
        super().__init__()
        self._severity = severity
        self._title    = title
        self._message  = message

    def compose(self) -> ComposeResult:
        icon, color = _ALERT_STYLES.get(self._severity, ("●", "$primary"))
        with Vertical(id="alert-body"):
            with Horizontal(id="alert-header"):
                yield Static(f"[{color}]{icon}[/{color}]", id="alert-icon")
                yield Static(f"[b]{self._title}[/b]",      id="alert-title")
            yield Static(self._message, id="alert-msg")
            yield Button("OK", variant="primary", id="btn-alert-ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-alert-ok":
            self.dismiss(None)

    def action_ok(self) -> None:
        self.dismiss(None)


# ── Confirm ────────────────────────────────────────────────────────────────────

class ConfirmModal(ModalScreen[bool]):
    """Ask the user to confirm or cancel an action.

    Returns ``True`` when confirmed, ``False`` when cancelled or Escaped.

    Usage::

        confirmed = await self.app.push_screen_wait(
            ConfirmModal(
                title="Delete wi-042?",
                message="This cannot be undone.",
                confirm_label="Delete",
                confirm_variant="error",
            )
        )
    """

    DEFAULT_CSS = """
    ConfirmModal { align: center middle; }
    #confirm-body {
        width: 52; height: auto; padding: 2 4;
        border: solid $primary; background: $surface;
    }
    #confirm-title  { margin-bottom: 1; }
    #confirm-msg    { margin-bottom: 2; color: $text-muted; }
    #confirm-btns   { height: auto; }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(
        self,
        title:           str,
        message:         str,
        confirm_label:   str = "Confirm",
        confirm_variant: str = "error",
    ) -> None:
        super().__init__()
        self._title           = title
        self._message         = message
        self._confirm_label   = confirm_label
        self._confirm_variant = confirm_variant

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-body"):
            yield Static(f"[b]{self._title}[/b]", id="confirm-title")
            yield Static(self._message,            id="confirm-msg")
            with Horizontal(id="confirm-btns"):
                yield Button(self._confirm_label, variant=self._confirm_variant,
                             id="btn-confirm-yes")
                yield Button("Cancel", id="btn-confirm-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-confirm-yes")

    def action_cancel(self) -> None:
        self.dismiss(False)


# ── Input prompt ───────────────────────────────────────────────────────────────

class InputModal(ModalScreen[str | None]):
    """Prompt for a single text value.

    Returns the entered string (stripped) on submit, or ``None`` if cancelled
    or Escaped.

    Usage::

        value = await self.app.push_screen_wait(
            InputModal("Rename job", "New job ID", placeholder="wi-NNN")
        )
    """

    DEFAULT_CSS = """
    InputModal { align: center middle; }
    #input-modal-body {
        width: 52; height: auto; padding: 2 4;
        border: solid $primary; background: $surface;
    }
    #input-modal-title  { margin-bottom: 1; }
    #input-modal-prompt { margin-bottom: 1; color: $text-muted; }
    #input-modal-field  { margin-bottom: 2; }
    #input-modal-btns   { height: auto; }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(
        self,
        title:       str,
        prompt:      str,
        default:     str = "",
        placeholder: str = "",
    ) -> None:
        super().__init__()
        self._title       = title
        self._prompt      = prompt
        self._default     = default
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="input-modal-body"):
            yield Static(f"[b]{self._title}[/b]",  id="input-modal-title")
            yield Static(self._prompt,              id="input-modal-prompt")
            yield Input(
                value=self._default,
                placeholder=self._placeholder,
                id="input-modal-field",
            )
            with Horizontal(id="input-modal-btns"):
                yield Button("Submit", variant="primary", id="btn-input-submit")
                yield Button("Cancel",                    id="btn-input-cancel")

    def on_mount(self) -> None:
        self.query_one("#input-modal-field", Input).focus()

    def _submit(self) -> None:
        value = self.query_one("#input-modal-field", Input).value.strip()
        self.dismiss(value if value else None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-input-submit":
            self._submit()
        elif event.button.id == "btn-input-cancel":
            self.dismiss(None)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit()

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Selection ──────────────────────────────────────────────────────────────────

class SelectionModal(ModalScreen[str | None]):
    """Pick one item from a labelled list.

    Returns the value string of the chosen item, or ``None`` if Escaped.

    Usage::

        tenant = await self.app.push_screen_wait(
            SelectionModal("Select tenant", [
                ("JHU",      "jhu"),
                ("UNC",      "unc"),
                ("Mayo",     "mayo"),
                ("Stanford", "stanford"),
            ])
        )
    """

    DEFAULT_CSS = """
    SelectionModal { align: center middle; }
    #sel-body {
        width: 40; height: auto; padding: 0;
        border: solid $primary; background: $surface;
    }
    #sel-title {
        padding: 1 2;
        border-bottom: solid $panel;
        background: $panel;
    }
    #sel-list { height: auto; max-height: 14; }
    #sel-hint {
        padding: 0 2;
        color: $text-muted;
        border-top: solid $panel;
        height: 1;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, options: list[tuple[str, str]]) -> None:
        super().__init__()
        self._title   = title
        self._options = options

    def compose(self) -> ComposeResult:
        with Vertical(id="sel-body"):
            yield Static(f"[b]{self._title}[/b]", id="sel-title")
            yield ListView(
                *[ListItem(Label(label), id=f"sel-{value}")
                  for label, value in self._options],
                id="sel-list",
            )
            yield Static("[dim]Enter to select · Escape to cancel[/dim]",
                         id="sel-hint")

    def on_mount(self) -> None:
        self.query_one(ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            value = event.item.id.removeprefix("sel-")
            self.dismiss(value)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Form ───────────────────────────────────────────────────────────────────────

class FormModal(ModalScreen[dict[str, Any] | None]):
    """Submit a small multi-field form.

    Returns a ``dict`` of field values on submit, or ``None`` if cancelled.
    Validates that all Select fields have real selections before submitting.

    Usage::

        result = await self.app.push_screen_wait(FormModal())
        if result:
            print(result["type"], result["priority"], result["tenant"])
    """

    DEFAULT_CSS = """
    FormModal { align: center middle; }
    #form-modal-body {
        width: 56; height: auto; padding: 2 4;
        border: solid $primary; background: $surface;
    }
    #form-modal-title  { margin-bottom: 2; }
    .form-modal-row    { height: auto; margin-bottom: 1; align: left middle; }
    .form-modal-label  { width: 12; }
    .form-modal-field  { width: 1fr; }
    #form-modal-error  { color: $error; height: 1; margin-bottom: 1; }
    #form-modal-btns   { height: auto; margin-top: 1; }
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="form-modal-body"):
            yield Static("[b]New Work Item[/b]", id="form-modal-title")

            with Horizontal(classes="form-modal-row"):
                yield Label("Type",     classes="form-modal-label")
                yield Select(_TYPE_OPTS,     prompt="Select type…",     id="fm-type",
                             classes="form-modal-field")
            with Horizontal(classes="form-modal-row"):
                yield Label("Priority", classes="form-modal-label")
                yield Select(_PRIORITY_OPTS, prompt="Select priority…", id="fm-priority",
                             classes="form-modal-field")
            with Horizontal(classes="form-modal-row"):
                yield Label("Tenant",   classes="form-modal-label")
                yield Select(_TENANT_OPTS,   prompt="Select tenant…",   id="fm-tenant",
                             classes="form-modal-field")

            yield Static("", id="form-modal-error")
            with Horizontal(id="form-modal-btns"):
                yield Button("Create", variant="primary", id="btn-form-submit")
                yield Button("Cancel",                    id="btn-form-cancel")

    def _submit(self) -> None:
        wtype  = self.query_one("#fm-type",     Select).value
        pri    = self.query_one("#fm-priority", Select).value
        tenant = self.query_one("#fm-tenant",   Select).value

        missing = []
        if not isinstance(wtype, str):
            missing.append("Type")
        if not isinstance(pri, str):
            missing.append("Priority")
        if not isinstance(tenant, str):
            missing.append("Tenant")

        if missing:
            self.query_one("#form-modal-error", Static).update(
                f"[b]Required:[/b] {', '.join(missing)}"
            )
            return

        self.dismiss({"type": wtype, "priority": pri, "tenant": tenant})

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-form-submit":
            self._submit()
        elif event.button.id == "btn-form-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Progress / Loading ─────────────────────────────────────────────────────────

class ProgressModal(ModalScreen[str]):
    """Show a loading indicator while a background task runs.

    The modal owns the worker — it auto-dismisses with ``"done"`` when the
    task completes.  The caller receives the result via ``push_screen_wait``.

    Usage::

        result = await self.app.push_screen_wait(
            ProgressModal("Exporting results", "Writing ONNX file…", duration=2.0)
        )
        # result == "done"
    """

    DEFAULT_CSS = """
    ProgressModal { align: center middle; }
    #prog-body {
        width: 44; height: auto; padding: 2 4;
        border: solid $primary; background: $surface;
    }
    #prog-title    { margin-bottom: 1; }
    #prog-message  { color: $text-muted; margin-bottom: 1; }
    #prog-spinner  { height: 3; }
    #prog-hint     { color: $text-muted; margin-top: 1; }
    """

    def __init__(self, title: str, message: str, duration: float = 2.5) -> None:
        super().__init__()
        self._title    = title
        self._message  = message
        self._duration = duration

    def compose(self) -> ComposeResult:
        with Vertical(id="prog-body"):
            yield Static(f"[b]{self._title}[/b]", id="prog-title")
            yield Static(self._message,            id="prog-message")
            yield LoadingIndicator(id="prog-spinner")
            yield Static("[dim]Please wait…[/dim]", id="prog-hint")

    def on_mount(self) -> None:
        self._run_task()

    @work
    async def _run_task(self) -> None:
        await asyncio.sleep(self._duration)
        self.dismiss("done")

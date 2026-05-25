"""Demo: Modal Dialogs — six modal patterns with typed return values."""

from __future__ import annotations

from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Button, Footer, Header, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.features.modal_dialogs.modals import (
    AlertModal,
    ConfirmModal,
    FormModal,
    InputModal,
    ProgressModal,
    SelectionModal,
)

__all__ = ["ModalDialogsDemoScreen"]

_TENANT_OPTIONS = [
    ("JHU",      "jhu"),
    ("UNC",      "unc"),
    ("Mayo",     "mayo"),
    ("Stanford", "stanford"),
]

_PRIORITY_OPTIONS = [
    ("Low",      "low"),
    ("Medium",   "medium"),
    ("High",     "high"),
    ("Critical", "critical"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _result_id(section: str) -> str:
    return f"result-{section}"


# ── Screen ────────────────────────────────────────────────────────────────────

class ModalDialogsDemoScreen(FeatureScreen):
    """Six modal dialog patterns, each with a trigger button and result display."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="md-body"):

            # ── Alert ─────────────────────────────────────────────
            yield Static("[b]Alert[/b]  [dim]inform the user; no choice required[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]None[/b]  "
                "[dim]— one severity variant per button[/dim]",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("ℹ Info",    id="btn-alert-info",    classes="md-btn")
                yield Button("⚠ Warning", id="btn-alert-warning", classes="md-btn",
                             variant="warning")
                yield Button("✖ Error",   id="btn-alert-error",   classes="md-btn",
                             variant="error")
                yield Button("✔ Success", id="btn-alert-success", classes="md-btn",
                             variant="success")
            yield Static("[dim]—[/dim]", id=_result_id("alert"), classes="md-result")

            # ── Confirm ───────────────────────────────────────────
            yield Static("[b]Confirm[/b]  [dim]ask before a destructive action[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]True[/b] (confirmed) or [b]False[/b] (cancelled)",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("Delete work item", variant="error",
                             id="btn-confirm", classes="md-btn")
            yield Static("[dim]—[/dim]", id=_result_id("confirm"), classes="md-result")

            # ── Input prompt ──────────────────────────────────────
            yield Static("[b]Input Prompt[/b]  [dim]collect a single text value[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]str[/b] (entered text) or [b]None[/b] (cancelled)",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("Rename job", id="btn-input", classes="md-btn")
            yield Static("[dim]—[/dim]", id=_result_id("input"), classes="md-result")

            # ── Selection ─────────────────────────────────────────
            yield Static("[b]Selection[/b]  [dim]pick one item from a list[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]str[/b] (selected value) or [b]None[/b] (cancelled)",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("Select tenant",   id="btn-sel-tenant",   classes="md-btn")
                yield Button("Select priority", id="btn-sel-priority", classes="md-btn")
            yield Static("[dim]—[/dim]", id=_result_id("selection"), classes="md-result")

            # ── Form ──────────────────────────────────────────────
            yield Static("[b]Form[/b]  [dim]submit a small multi-field form[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]dict[/b] (field values) or [b]None[/b] (cancelled)",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("New work item", variant="primary",
                             id="btn-form", classes="md-btn")
            yield Static("[dim]—[/dim]", id=_result_id("form"), classes="md-result")

            # ── Progress / Loading ────────────────────────────────
            yield Static("[b]Progress / Loading[/b]  "
                         "[dim]block while a background task runs[/dim]",
                         classes="md-section-title")
            yield Static(
                "[dim]Returns:[/dim] [b]\"done\"[/b] — auto-dismisses when the worker finishes",
                classes="md-subtitle",
            )
            with Horizontal(classes="md-btn-row"):
                yield Button("Export results (2.5 s)", id="btn-progress",
                             classes="md-btn")
            yield Static("[dim]—[/dim]", id=_result_id("progress"), classes="md-result")

        yield Footer()

    # ── Button dispatcher ─────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: PLR0912
        match event.button.id:

            # Alert variants
            case "btn-alert-info":
                self.app.push_screen(
                    AlertModal("info", "Maintenance window",
                               "Scheduled downtime tonight 02:00–04:00 UTC."),
                    callback=lambda _: self._set_result("alert", "dismissed (info)"),
                )
            case "btn-alert-warning":
                self.app.push_screen(
                    AlertModal("warning", "Disk space low",
                               "Node gpu-07 is at 87 % capacity."),
                    callback=lambda _: self._set_result("alert", "dismissed (warning)"),
                )
            case "btn-alert-error":
                self.app.push_screen(
                    AlertModal("error", "Job wi-039 failed",
                               "OOM error during preprocessing step 3."),
                    callback=lambda _: self._set_result("alert", "dismissed (error)"),
                )
            case "btn-alert-success":
                self.app.push_screen(
                    AlertModal("success", "Deployment complete",
                               "Release v2.4.1 rolled out to all nodes."),
                    callback=lambda _: self._set_result("alert", "dismissed (success)"),
                )

            # Confirm
            case "btn-confirm":
                self.app.push_screen(
                    ConfirmModal(
                        title="Delete wi-042?",
                        message="This work item will be permanently removed.",
                        confirm_label="Delete",
                        confirm_variant="error",
                    ),
                    callback=lambda v: self._set_result(
                        "confirm",
                        "[green]confirmed — deleted[/green]" if v
                        else "[dim]cancelled[/dim]",
                    ),
                )

            # Input prompt
            case "btn-input":
                self.app.push_screen(
                    InputModal(
                        title="Rename job",
                        prompt="Enter a new job ID",
                        placeholder="wi-NNN",
                    ),
                    callback=lambda v: self._set_result(
                        "input",
                        f"[green]entered:[/green] [b]{v}[/b]" if v
                        else "[dim]cancelled[/dim]",
                    ),
                )

            # Selection
            case "btn-sel-tenant":
                self.app.push_screen(
                    SelectionModal("Select tenant", _TENANT_OPTIONS),
                    callback=lambda v: self._set_result(
                        "selection",
                        f"[green]selected:[/green] [b]{v}[/b]" if v
                        else "[dim]cancelled[/dim]",
                    ),
                )
            case "btn-sel-priority":
                self.app.push_screen(
                    SelectionModal("Select priority", _PRIORITY_OPTIONS),
                    callback=lambda v: self._set_result(
                        "selection",
                        f"[green]selected:[/green] [b]{v}[/b]" if v
                        else "[dim]cancelled[/dim]",
                    ),
                )

            # Form
            case "btn-form":
                self.app.push_screen(
                    FormModal(),
                    callback=lambda v: self._set_result(
                        "form",
                        (
                            f"[green]created:[/green] "
                            f"type=[b]{v['type']}[/b]  "
                            f"priority=[b]{v['priority']}[/b]  "
                            f"tenant=[b]{v['tenant']}[/b]"
                        ) if v else "[dim]cancelled[/dim]",
                    ),
                )

            # Progress
            case "btn-progress":
                self.app.push_screen(
                    ProgressModal(
                        title="Exporting results",
                        message="Writing ONNX file to output/wi-042/…",
                        duration=2.5,
                    ),
                    callback=lambda v: self._set_result(
                        "progress",
                        f"[green]task {v}[/green]",
                    ),
                )

    # ── Result helpers ────────────────────────────────────────────

    def _set_result(self, section: str, text: str) -> None:
        self.query_one(f"#{_result_id(section)}", Static).update(
            f"[dim]Result →[/dim] {text}"
        )

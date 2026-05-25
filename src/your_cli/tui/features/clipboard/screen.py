"""Demo: Clipboard Copy — app.copy_to_clipboard() with toast feedback.

Shows four payload types so the caller can see the API works for anything
from a single identifier to a multi-line shell command to JSON.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Button, Footer, Header, Static

from your_cli.tui.feature_screen import FeatureScreen

__all__ = ["ClipboardDemoScreen"]

# ── Sample payloads ────────────────────────────────────────────────────────────

_SAMPLES: list[tuple[str, str, str, str]] = [
    (
        "plain",
        "Plain text  [dim]— a single short identifier[/dim]",
        "wi-0042",
        "Copy job ID",
    ),
    (
        "cmd",
        "Shell command  [dim]— multi-line with line continuations[/dim]",
        "aiq infer \\\n  --tenant jhu \\\n  --run run-0017 \\\n  --model onnx/v2.4.1",
        "Copy command",
    ),
    (
        "json",
        "JSON payload  [dim]— a serialised API response object[/dim]",
        (
            '{\n'
            '  "tenant": "jhu",\n'
            '  "run_id": "run-0017",\n'
            '  "work_item_id": "wi-0042",\n'
            '  "status": "failed",\n'
            '  "priority": "high"\n'
            '}'
        ),
        "Copy JSON",
    ),
    (
        "csv",
        "CSV row  [dim]— a DataTable row exported as comma-separated values[/dim]",
        "wi-0042,run-0017,jhu,failed,high,prod,jsmith",
        "Copy CSV row",
    ),
]


# ── Screen ─────────────────────────────────────────────────────────────────────

class ClipboardDemoScreen(FeatureScreen):
    """Demonstrates app.copy_to_clipboard() for plain text, commands, JSON, and CSV."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="cb-body"):
            yield Static(
                "[b]Clipboard Copy[/b]  "
                "[dim]app.copy_to_clipboard() writes to the system clipboard; "
                "each button also fires a toast via self.notify()[/dim]",
                id="cb-title",
            )

            for section, title, content, btn_label in _SAMPLES:
                yield Static(f"[b]{title}[/b]", classes="cb-section")
                yield Static(content, classes="cb-code")
                with Horizontal(classes="cb-btn-row"):
                    yield Button(btn_label, id=f"btn-{section}", classes="cb-btn")
                yield Static("[dim]—[/dim]", id=f"result-{section}", classes="cb-result")

        yield Footer()

    # ── Handlers ───────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if not bid.startswith("btn-"):
            return
        section = bid[4:]  # strip "btn-"
        for key, _, content, _ in _SAMPLES:
            if key == section:
                self._copy(section, content)
                return

    def _copy(self, section: str, text: str) -> None:
        self.app.copy_to_clipboard(text)
        lines = text.count("\n") + 1
        chars = len(text)
        desc = f"{chars} chars" if lines == 1 else f"{lines} lines · {chars} chars"
        self.notify("Copied to clipboard", timeout=2)
        self.query_one(f"#result-{section}", Static).update(
            f"[dim]Copied →[/dim] [green]✔[/green]  [dim]{desc}[/dim]"
        )

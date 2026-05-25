"""Work item detail screen — pushed directly from WorkItemCardsScreen.

Not registered in routes.py — pushed via push_screen(WorkItemDetailScreen(record)).
See ADR-0001.
"""

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Static

from your_cli.tui.feature_screen import FeatureScreen
from your_cli.tui.palette import PRI_COLORS, STATUS_COLORS
from your_cli.tui.widgets import KVCard


class WorkItemDetailScreen(FeatureScreen):
    """Full detail view for a single work item.

    Receives the record dict at construction time — follows the push-directly
    pattern (ADR-0001) since it requires caller-supplied data to render.
    """

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self, record: dict[str, Any]) -> None:
        super().__init__()
        self._record = record

    def compose(self) -> ComposeResult:
        rec = self._record
        sc  = STATUS_COLORS.get(rec["status"], "white")
        pc  = PRI_COLORS.get(rec["priority"], "white")

        yield Header(show_clock=True)
        with ScrollableContainer(id="wid-body"):

            yield Static(
                f"[b]{rec['id']}[/b]  [dim]·  {rec['type']}[/dim]",
                id="wid-title",
            )

            with Horizontal(id="wid-cards"):
                yield KVCard("Work Item", [
                    ("Status",       f"[{sc}]● {rec['status']}[/{sc}]"),
                    ("Priority",     f"[{pc}]{rec['priority']}[/{pc}]"),
                    ("Type",         rec["type"]),
                    ("Tenant",       rec["tenant"].upper()),
                    ("Environment",  rec["environment"]),
                    ("Submitted by", rec["submitted_by"]),
                    ("Tags",         rec["tags"] or "[dim]—[/dim]"),
                ])

                yield KVCard("Configuration", [
                    ("Node",         rec.get("node",        "[dim]—[/dim]")),
                    ("Max jobs",     rec.get("max_jobs",    "[dim]—[/dim]")),
                    ("Timeout",
                     f"{rec['timeout_min']} min" if rec.get("timeout_min") else "[dim]—[/dim]"),
                    ("GPU required",
                     "[green]Yes[/green]" if rec.get("gpu_required") else "[dim]No[/dim]"),
                    ("Auto retry",
                     "[green]Yes[/green]" if rec.get("auto_retry")   else "[dim]No[/dim]"),
                ])

            has_notes = rec.get("description") or rec.get("notes")
            if has_notes:
                with Vertical(id="wid-notes"):
                    yield KVCard("Notes", [
                        ("Description", rec.get("description") or "[dim]—[/dim]"),
                        ("Notes",       rec.get("notes")       or "[dim]—[/dim]"),
                    ])

        yield Footer()

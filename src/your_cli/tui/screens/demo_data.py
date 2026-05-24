"""Demo: Data Display."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Markdown, RichLog, TabbedContent, TabPane

SAMPLE_MARKDOWN = """\
# Markdown Viewer

Textual renders **rich markdown** natively, including:

- *Italic* and **bold** text
- `inline code` snippets
- Block quotes and lists

## Code Block

```python
async def fetch_items(client: httpx.AsyncClient) -> list[dict]:
    response = await client.get("/work-items")
    response.raise_for_status()
    return response.json()
```

## Table

| ID      | Status  | Tenant | Updated          |
|---------|---------|--------|------------------|
| wi-001  | queued  | jhu    | 2026-05-23 09:14 |
| wi-002  | running | unc    | 2026-05-23 09:17 |
| wi-003  | done    | mayo   | 2026-05-23 09:21 |

> **Note:** Replace this stub with real API data once the OpenAPI client is generated.
"""


class DataDemoScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("DataTable", id="tab-table"):
                yield DataTable(id="demo-table", cursor_type="row")
            with TabPane("RichLog", id="tab-log"):
                yield RichLog(id="demo-log", highlight=True, markup=True)
            with TabPane("Markdown", id="tab-md"):
                yield Markdown(SAMPLE_MARKDOWN, id="demo-md")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#demo-table", DataTable)
        table.add_columns("Name", "Status", "Score", "Region")
        table.add_rows([
            ("Alice",   "active",   "98.2", "North"),
            ("Bob",     "pending",  "74.5", "South"),
            ("Carol",   "active",   "88.0", "East"),
            ("Dan",     "inactive", "61.3", "West"),
            ("Eve",     "active",   "95.7", "North"),
        ])

        log = self.query_one("#demo-log", RichLog)
        entries = [
            ("[green]INFO[/green]    ", "Application started"),
            ("[green]INFO[/green]    ", "Loading configuration from environment"),
            ("[yellow]WARN[/yellow]    ", "API response time elevated: 1.2 s"),
            ("[green]INFO[/green]    ", "Worker pool initialised (4 threads)"),
            ("[red]ERROR[/red]   ", "Connection refused: https://api.example.com/health"),
            ("[green]INFO[/green]    ", "Retrying in 5 seconds..."),
            ("[green]INFO[/green]    ", "Connection restored"),
            ("[cyan]DEBUG[/cyan]   ", "Cache hit rate: 94.3%"),
            ("[green]INFO[/green]    ", "Fetched 42 work items"),
        ]
        for level, msg in entries:
            log.write(f"{level} {msg}")

    def action_go_back(self) -> None:
        self.app.pop_screen()

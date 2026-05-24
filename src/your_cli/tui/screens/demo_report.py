"""Demo: Markdown report viewer with a report-switcher sidebar."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, MarkdownViewer

_REPORTS: dict[str, tuple[str, str]] = {
    "summary": (
        "Executive Summary",
        """\
# Platform Status — Executive Summary

**Generated:** 2026-05-23  ·  **Period:** last 30 days

## Key Metrics

| Metric             | Value   | Change   |
|--------------------|---------|----------|
| Jobs completed     | 4,821   | ↑ 12%    |
| Success rate       | 97.4%   | ↑ 0.8pp  |
| Avg. job duration  | 4m 32s  | ↓ 18s    |
| Active tenants     | 3       | —        |
| Data processed     | 2.1 TB  | ↑ 340 GB |

## Highlights

- **JHU** pipeline achieved 100% uptime this month
- New **validation layer** reduced failed jobs by 41%
- Storage costs down 8% after cold-tier migration

## Risks

> **Warning:** UNC batch queue depth exceeded threshold on 3 occasions.
> Root cause: upstream data delivery delays. Mitigation in progress.
""",
    ),
    "jobs": (
        "Job Report",
        """\
# Job Execution Report

## By Tenant

### Johns Hopkins (JHU)
- Total jobs: **1,834**
- Failed: **12** (0.65%)
- Most common failure: `timeout` after 15 min

### UNC Chapel Hill
- Total jobs: **1,623**
- Failed: **67** (4.1%)
- Most common failure: `validation_error`

### Mayo Clinic
- Total jobs: **1,364**
- Failed: **24** (1.76%)

## Slowest Job Types

1. `full_cohort_analysis` — avg 22m 14s
2. `model_retrain` — avg 18m 07s
3. `data_export_large` — avg 9m 45s

## Sample Failed Job

```json
{
  "id": "wi-8821",
  "tenant": "unc",
  "status": "failed",
  "error": "ValidationError: missing required field 'subject_id'",
  "duration": "0m 04s"
}
```
""",
    ),
    "infra": (
        "Infrastructure",
        """\
# Infrastructure Report

## Compute

| Node     | CPU (avg) | Mem (avg) | Status  |
|----------|-----------|-----------|---------|
| worker-1 | 64%       | 71%       | healthy |
| worker-2 | 58%       | 68%       | healthy |
| worker-3 | 12%       | 45%       | standby |

## Storage

- **Hot tier:** 480 GB used of 1 TB (48%)
- **Cold tier:** 1.7 TB archived
- **Retention policy:** 90 days hot, 2 years cold

## Upcoming Maintenance

- **2026-06-01:** worker-3 OS patch (30 min window, no downtime)
- **2026-06-15:** Storage tier migration (rolling, no downtime)

## Recommendations

1. Scale worker pool during UNC batch windows (Mon/Wed 02:00–06:00)
2. Enable auto-scaling trigger at 80% CPU sustained for 5 min
3. Review cold-tier access patterns — 12% of archived data accessed within 7 days
""",
    ),
    "pipeline": (
        "Pipeline Health",
        """\
# Pipeline Health Report

## Stage Latencies (p50 / p95)

| Stage           | p50     | p95     |
|-----------------|---------|---------|
| Ingestion       | 1.2s    | 4.8s    |
| Validation      | 0.3s    | 1.1s    |
| Transformation  | 8.4s    | 31.2s   |
| Model inference | 22.0s   | 58.6s   |
| Export          | 3.1s    | 12.4s   |

## Error Budget

- **SLO target:** 99.0% success rate
- **Current:** 97.4% — **budget exhausted by 1.4pp**
- Remaining burn window: 0 days (reset 2026-06-01)

## Top Error Categories

```
ValidationError    41%  ████████████████░░░░
Timeout            28%  ███████████░░░░░░░░░
NetworkError       18%  ███████░░░░░░░░░░░░░
UnknownError       13%  █████░░░░░░░░░░░░░░░
```

## Action Items

- [ ] Increase validation timeout from 30s → 60s for large cohorts
- [ ] Add retry logic for transient `NetworkError` in export stage
- [ ] Profile `model_retrain` — 3× slower than baseline since 2026-04-12
""",
    ),
}


class ReportDemoScreen(Screen[None]):
    BINDINGS = [
        Binding("escape", "go_back",        "Back"),
        Binding("[",      "narrow_sidebar", "Narrow"),
        Binding("]",      "widen_sidebar",  "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(25)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="report-body"):
            yield ListView(
                *[ListItem(Label(title), id=f"rpt-{key}") for key, (title, _) in _REPORTS.items()],
                id="report-list",
            )
            with Vertical(id="report-content"):
                yield MarkdownViewer("", show_table_of_contents=False, id="report-md")
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width
        lv = self.query_one(ListView)
        lv.focus()
        self._load_report(next(iter(_REPORTS)))

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#report-list").styles.width = f"{width}%"

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id:
            key = event.item.id.removeprefix("rpt-")
            if key in _REPORTS:
                self._load_report(key)

    def _load_report(self, key: str) -> None:
        _, content = _REPORTS[key]
        self.query_one("#report-md", MarkdownViewer).document.update(content)

    def action_go_back(self) -> None:
        self.app.pop_screen()

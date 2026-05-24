"""Demo: More card patterns — timeline, pricing, sparkline, activity, comparison."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Rule, Sparkline, Static


# ── Card widgets ──────────────────────────────────────────────────────────────

class TimelineCard(Widget):
    """Vertical sequence of timestamped steps with status icons.

    Each step is a (time, label, status) tuple where status is one of:
    "done" | "active" | "pending" | "error"
    """

    DEFAULT_CSS: ClassVar[str] = """
    TimelineCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    TimelineCard:hover { border: round $accent; }

    TimelineCard .tlc-title  { text-style: bold; color: $accent; margin-bottom: 1; }
    TimelineCard .tlc-step   { height: 1; }
    TimelineCard .tlc-time   { width: 7; color: $text-muted; }
    TimelineCard .tlc-icon   { width: 3; }
    TimelineCard .tlc-label  { width: 1fr; }
    """

    _ICONS: ClassVar[dict[str, str]] = {
        "done":    "[green]✓[/green]",
        "active":  "[yellow]●[/yellow]",
        "pending": "[dim]○[/dim]",
        "error":   "[red]✗[/red]",
    }

    def __init__(
        self,
        title: str,
        steps: list[tuple[str, str, str]],   # (time, label, status)
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._steps = steps

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="tlc-title")
        yield Rule(line_style="dashed")
        for time, label, status in self._steps:
            icon = self._ICONS.get(status, "[dim]○[/dim]")
            with Horizontal(classes="tlc-step"):
                yield Static(time,  classes="tlc-time",  markup=True)
                yield Static(icon,  classes="tlc-icon",  markup=True)
                yield Static(label, classes="tlc-label")


class PricingCard(Widget):
    """Pricing tier card: price, feature checklist, CTA button.

    Pass ``highlight=True`` to give the card a prominent accent border.
    """

    DEFAULT_CSS: ClassVar[str] = """
    PricingCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    PricingCard.-highlight {
        border: round $accent;
        background: $boost;
    }
    PricingCard:hover { border: round $accent; }

    PricingCard .pcc-tier     { text-style: bold; color: $accent; }
    PricingCard .pcc-badge    { color: $background; background: $accent; width: auto; padding: 0 1; margin-left: 1; }
    PricingCard .pcc-price    { text-style: bold; height: 2; content-align: center middle; }
    PricingCard .pcc-period   { color: $text-muted; text-align: center; margin-bottom: 1; }
    PricingCard .pcc-feature  { height: 1; }
    PricingCard .pcc-check    { width: 3; }
    PricingCard .pcc-feat-lbl { width: 1fr; }
    PricingCard .pcc-actions  { height: auto; margin-top: 1; align: center middle; }
    """

    def __init__(
        self,
        tier: str,
        price: str,
        period: str,
        features: list[tuple[str, bool]],   # (label, included)
        cta: str,
        highlight: bool = False,
        **kw,
    ) -> None:
        existing = kw.pop("classes", "")
        classes  = ("-highlight " + existing).strip() if highlight else existing
        super().__init__(classes=classes, **kw)
        self._tier     = tier
        self._price    = price
        self._period   = period
        self._features = features
        self._cta      = cta
        self._highlight = highlight

    def compose(self) -> ComposeResult:
        header = Horizontal()
        with Horizontal():
            yield Static(self._tier, classes="pcc-tier")
            if self._highlight:
                yield Static("Recommended", classes="pcc-badge")
        yield Rule(line_style="dashed")
        yield Static(self._price,  classes="pcc-price")
        yield Static(self._period, classes="pcc-period")
        for label, included in self._features:
            icon  = "[green]✓[/green]" if included else "[dim]✗[/dim]"
            color = "" if included else "dim"
            lbl   = f"[{color}]{label}[/{color}]" if color else label
            with Horizontal(classes="pcc-feature"):
                yield Static(icon, classes="pcc-check",    markup=True)
                yield Static(lbl,  classes="pcc-feat-lbl", markup=True)
        with Horizontal(classes="pcc-actions"):
            variant = "primary" if self._highlight else "default"
            yield Button(self._cta, variant=variant)


class SparklineCard(Widget):
    """Card embedding a Sparkline widget with a title and summary stats."""

    DEFAULT_CSS: ClassVar[str] = """
    SparklineCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    SparklineCard:hover { border: round $accent; }

    SparklineCard .slc-title   { text-style: bold; color: $accent; margin-bottom: 1; }
    SparklineCard Sparkline    { height: 4; width: 1fr; margin-bottom: 1; }
    SparklineCard .slc-stats   { height: auto; }
    SparklineCard .slc-stat    { width: 1fr; text-align: center; }
    SparklineCard .slc-stat-val{ text-style: bold; color: $foreground; }
    SparklineCard .slc-stat-lbl{ color: $text-muted; }
    """

    def __init__(
        self,
        title: str,
        data: list[float],
        stats: list[tuple[str, str]],   # (label, formatted_value)
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._data  = data
        self._stats = stats

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="slc-title")
        yield Sparkline(self._data)
        with Horizontal(classes="slc-stats"):
            for label, value in self._stats:
                with Vertical(classes="slc-stat"):
                    yield Static(value, classes="slc-stat-val")
                    yield Static(label, classes="slc-stat-lbl")


class ActivityCard(Widget):
    """Recent-activity feed: icon, actor/event, and relative timestamp."""

    DEFAULT_CSS: ClassVar[str] = """
    ActivityCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ActivityCard:hover { border: round $accent; }

    ActivityCard .acc-title  { text-style: bold; color: $accent; margin-bottom: 1; }
    ActivityCard .acc-item   { height: 1; margin-bottom: 0; }
    ActivityCard .acc-icon   { width: 3; }
    ActivityCard .acc-text   { width: 1fr; }
    ActivityCard .acc-time   { width: 10; color: $text-muted; text-align: right; }
    """

    _KIND_ICON: ClassVar[dict[str, str]] = {
        "success": "[green]✓[/green]",
        "error":   "[red]✗[/red]",
        "warning": "[yellow]⚠[/yellow]",
        "info":    "[cyan]ℹ[/cyan]",
        "user":    "[blue]●[/blue]",
    }

    def __init__(
        self,
        title: str,
        items: list[tuple[str, str, str]],   # (kind, text, relative_time)
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._items = items

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="acc-title")
        yield Rule(line_style="dashed")
        for kind, text, when in self._items:
            icon = self._KIND_ICON.get(kind, "[dim]●[/dim]")
            with Horizontal(classes="acc-item"):
                yield Static(icon, classes="acc-icon", markup=True)
                yield Static(text, classes="acc-text")
                yield Static(when, classes="acc-time")


class ComparisonCard(Widget):
    """Side-by-side plan / option comparison table."""

    DEFAULT_CSS: ClassVar[str] = """
    ComparisonCard {
        height: auto;
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    ComparisonCard:hover { border: round $accent; }

    ComparisonCard .cmc-title   { text-style: bold; color: $accent; margin-bottom: 1; }
    ComparisonCard .cmc-header  { height: 1; }
    ComparisonCard .cmc-spacer  { width: 1fr; }
    ComparisonCard .cmc-col-a   { width: 14; text-style: bold; color: $primary; text-align: center; }
    ComparisonCard .cmc-col-b   { width: 14; text-style: bold; color: $accent;  text-align: center; }
    ComparisonCard .cmc-row     { height: 1; }
    ComparisonCard .cmc-label   { width: 1fr; color: $text-muted; }
    ComparisonCard .cmc-val-a   { width: 14; text-align: center; }
    ComparisonCard .cmc-val-b   { width: 14; text-align: center; color: $accent; }
    """

    def __init__(
        self,
        title: str,
        col_a: str,
        col_b: str,
        rows: list[tuple[str, str, str]],   # (label, value_a, value_b)
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._title = title
        self._col_a = col_a
        self._col_b = col_b
        self._rows  = rows

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="cmc-title")
        with Horizontal(classes="cmc-header"):
            yield Static("",          classes="cmc-spacer")
            yield Static(self._col_a, classes="cmc-col-a")
            yield Static(self._col_b, classes="cmc-col-b")
        yield Rule(line_style="dashed")
        for label, val_a, val_b in self._rows:
            with Horizontal(classes="cmc-row"):
                yield Static(label, classes="cmc-label")
                yield Static(val_a, classes="cmc-val-a", markup=True)
                yield Static(val_b, classes="cmc-val-b", markup=True)


# ── Demo screen ───────────────────────────────────────────────────────────────

class Cards2DemoScreen(Screen[None]):
    """Five more card patterns: timeline, pricing, sparkline, activity, comparison."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="cd2-body"):

            # ── Timeline cards ────────────────────────────────────
            yield Static(
                "[b]Timeline Cards[/b]  [dim]ordered steps with status[/dim]",
                classes="cd2-section",
            )
            with Horizontal(classes="cd2-row"):
                yield TimelineCard("Deployment — v2.4.1", [
                    ("09:14", "Build passed",             "done"),
                    ("09:18", "Unit tests passed",        "done"),
                    ("09:23", "Deploying to staging",     "done"),
                    ("09:31", "Staging smoke tests",      "active"),
                    ("—",     "Production rollout",       "pending"),
                    ("—",     "Post-deploy verification", "pending"),
                ])
                yield TimelineCard("Job wi-204 — Training", [
                    ("08:00", "Queued",                   "done"),
                    ("08:02", "Node assigned: gpu-04",    "done"),
                    ("08:03", "Data loader initialised",  "done"),
                    ("08:05", "Epoch 1 / 100 started",    "done"),
                    ("08:47", "Epoch 72 / 100 in progress","active"),
                    ("—",     "Checkpoint & export",      "pending"),
                ])
                yield TimelineCard("Onboarding — Mayo tenant", [
                    ("Day 1", "Account created",          "done"),
                    ("Day 1", "SSO configured",           "done"),
                    ("Day 2", "First job submitted",      "done"),
                    ("Day 3", "Team members invited",     "error"),
                    ("—",     "GPU quota approved",       "pending"),
                    ("—",     "Production sign-off",      "pending"),
                ])

            # ── Pricing cards ─────────────────────────────────────
            yield Static(
                "[b]Pricing Cards[/b]  [dim]tier feature checklist with CTA[/dim]",
                classes="cd2-section",
            )
            with Horizontal(classes="cd2-row"):
                yield PricingCard(
                    "Starter", "$0", "Free forever",
                    [
                        ("5 concurrent jobs",         True),
                        ("10 GB storage",             True),
                        ("Community support",         True),
                        ("GPU node access",           False),
                        ("Priority scheduling",       False),
                        ("Dedicated account manager", False),
                    ],
                    "Get started",
                )
                yield PricingCard(
                    "Pro", "$49", "per month",
                    [
                        ("50 concurrent jobs",        True),
                        ("100 GB storage",            True),
                        ("Email support",             True),
                        ("GPU node access",           True),
                        ("Priority scheduling",       True),
                        ("Dedicated account manager", False),
                    ],
                    "Start free trial",
                    highlight=True,
                )
                yield PricingCard(
                    "Enterprise", "Custom", "contact sales",
                    [
                        ("Unlimited concurrent jobs", True),
                        ("1 TB+ storage",             True),
                        ("24/7 phone support",        True),
                        ("GPU node access",           True),
                        ("Priority scheduling",       True),
                        ("Dedicated account manager", True),
                    ],
                    "Contact sales",
                )

            # ── Sparkline cards ───────────────────────────────────
            yield Static(
                "[b]Sparkline Cards[/b]  [dim]embedded Sparkline widget with summary stats[/dim]",
                classes="cd2-section",
            )
            with Horizontal(classes="cd2-row"):
                yield SparklineCard(
                    "Job throughput  (last 24 h)",
                    [18,24,31,42,58,74,91,112,98,84,72,65,58,63,79,95,118,142,131,108,87,64,42,28],
                    [("Peak", "142 / h"), ("Average", "76 / h"), ("Total", "1,836")],
                )
                yield SparklineCard(
                    "GPU utilisation  (last 24 h)",
                    [12,18,25,38,52,71,88,94,91,85,79,72,68,73,82,90,96,99,95,87,74,55,34,19],
                    [("Peak", "99 %"), ("Average", "67 %"), ("Now", "19 %")],
                )
                yield SparklineCard(
                    "API response time  ms  (last 24 h)",
                    [210,198,215,224,312,445,389,298,245,232,218,212,208,215,228,242,318,412,364,287,241,225,214,209],
                    [("Peak", "445 ms"), ("Average", "268 ms"), ("P99", "420 ms")],
                )

            # ── Activity cards ────────────────────────────────────
            yield Static(
                "[b]Activity Cards[/b]  [dim]timestamped event feed[/dim]",
                classes="cd2-section",
            )
            with Horizontal(classes="cd2-row"):
                yield ActivityCard("Platform events", [
                    ("success", "wi-204 training completed",     "2 m ago"),
                    ("user",    "alice@jhu.edu submitted wi-205","4 m ago"),
                    ("warning", "gpu-node-07 memory at 91 %",    "12 m ago"),
                    ("success", "wi-198 export finished",        "18 m ago"),
                    ("error",   "wi-193 failed — OOM step 3",    "1 h ago"),
                    ("info",    "Scheduler restarted (planned)", "2 h ago"),
                ])
                yield ActivityCard("Tenant · JHU", [
                    ("success", "wi-201 validation passed",      "5 m ago"),
                    ("user",    "eve@jhu.edu joined workspace",  "22 m ago"),
                    ("info",    "Storage quota increased → 200 GB","1 h ago"),
                    ("success", "wi-189 checkpoint exported",    "2 h ago"),
                    ("warning", "wi-175 retry 2/3 in progress",  "3 h ago"),
                    ("user",    "alice@jhu.edu updated API key", "5 h ago"),
                ])
                yield ActivityCard("Tenant · Stanford", [
                    ("error",   "wi-112 cancelled by user",      "8 m ago"),
                    ("success", "wi-111 preprocessing done",     "15 m ago"),
                    ("user",    "dave@stanford.edu invited 3 users","30 m ago"),
                    ("info",    "New node registered: gpu-09",   "45 m ago"),
                    ("success", "wi-108 inference completed",    "1 h ago"),
                    ("warning", "API budget at 91 % (monthly)",  "2 h ago"),
                ])

            # ── Comparison cards ──────────────────────────────────
            yield Static(
                "[b]Comparison Cards[/b]  [dim]side-by-side two-option table[/dim]",
                classes="cd2-section",
            )
            with Horizontal(classes="cd2-row"):
                yield ComparisonCard("Scheduling modes",
                    "FIFO", "Priority",
                    [
                        ("Fairness",       "High",      "[b]Medium[/b]"),
                        ("Latency (high)", "High",      "[b]Low[/b]"),
                        ("Starvation",     "None",      "[b]Possible[/b]"),
                        ("Config",         "None",      "[b]Per-job[/b]"),
                        ("Best for",       "Batch",     "[b]Interactive[/b]"),
                    ],
                )
                yield ComparisonCard("Storage tiers",
                    "Hot", "Cold",
                    [
                        ("Access latency",  "[b]< 10 ms[/b]",  "~5 s"),
                        ("Cost / GB",       "[b]$0.08[/b]",    "$0.002"),
                        ("Retrieval fee",   "None",            "[b]$0.01/GB[/b]"),
                        ("Replication",     "[b]3×[/b]",       "1×"),
                        ("Best for",        "[b]Active jobs[/b]","Archives"),
                    ],
                )
                yield ComparisonCard("GPU node classes",
                    "A100", "H100",
                    [
                        ("VRAM",            "80 GB",     "[b]96 GB[/b]"),
                        ("FP16 TFLOPS",     "312",       "[b]1,979[/b]"),
                        ("NVLink",          "600 GB/s",  "[b]900 GB/s[/b]"),
                        ("Cost / h",        "$3.20",     "[b]$8.50[/b]"),
                        ("Availability",    "[b]High[/b]","Medium"),
                    ],
                )

        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

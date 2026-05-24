"""Demo: More card patterns — timeline, pricing, sparkline, activity, comparison."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from your_cli.tui.feature_screen import FeatureScreen
from textual.widgets import Footer, Header, Static

from your_cli.tui.widgets import (
    ActivityCard,
    ComparisonCard,
    PricingCard,
    SparklineCard,
    TimelineCard,
)

# ── Demo screen ───────────────────────────────────────────────────────────────

class Cards2DemoScreen(FeatureScreen):
    """Five more card patterns: timeline, pricing, sparkline, activity, comparison."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"


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
                    ("08:00", "Queued",                    "done"),
                    ("08:02", "Node assigned: gpu-04",     "done"),
                    ("08:03", "Data loader initialised",   "done"),
                    ("08:05", "Epoch 1 / 100 started",     "done"),
                    ("08:47", "Epoch 72 / 100 in progress","active"),
                    ("—",     "Checkpoint & export",       "pending"),
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
                    ("success", "wi-204 training completed",      "2 m ago"),
                    ("user",    "alice@jhu.edu submitted wi-205", "4 m ago"),
                    ("warning", "gpu-node-07 memory at 91 %",     "12 m ago"),
                    ("success", "wi-198 export finished",         "18 m ago"),
                    ("error",   "wi-193 failed — OOM step 3",     "1 h ago"),
                    ("info",    "Scheduler restarted (planned)",  "2 h ago"),
                ])
                yield ActivityCard("Tenant · JHU", [
                    ("success", "wi-201 validation passed",         "5 m ago"),
                    ("user",    "eve@jhu.edu joined workspace",     "22 m ago"),
                    ("info",    "Storage quota increased → 200 GB", "1 h ago"),
                    ("success", "wi-189 checkpoint exported",       "2 h ago"),
                    ("warning", "wi-175 retry 2/3 in progress",     "3 h ago"),
                    ("user",    "alice@jhu.edu updated API key",    "5 h ago"),
                ])
                yield ActivityCard("Tenant · Stanford", [
                    ("error",   "wi-112 cancelled by user",           "8 m ago"),
                    ("success", "wi-111 preprocessing done",          "15 m ago"),
                    ("user",    "dave@stanford.edu invited 3 users",  "30 m ago"),
                    ("info",    "New node registered: gpu-09",        "45 m ago"),
                    ("success", "wi-108 inference completed",         "1 h ago"),
                    ("warning", "API budget at 91 % (monthly)",       "2 h ago"),
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
                        ("Fairness",       "High",    "[b]Medium[/b]"),
                        ("Latency (high)", "High",    "[b]Low[/b]"),
                        ("Starvation",     "None",    "[b]Possible[/b]"),
                        ("Config",         "None",    "[b]Per-job[/b]"),
                        ("Best for",       "Batch",   "[b]Interactive[/b]"),
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
                        ("VRAM",        "80 GB",    "[b]96 GB[/b]"),
                        ("FP16 TFLOPS", "312",      "[b]1,979[/b]"),
                        ("NVLink",      "600 GB/s", "[b]900 GB/s[/b]"),
                        ("Cost / h",    "$3.20",    "[b]$8.50[/b]"),
                        ("Availability","[b]High[/b]","Medium"),
                    ],
                )

        yield Footer()


"""Reusable widget library for the AIQ TUI.

Import everything from here — never import from individual widget modules
in screen files, and never import widgets from screen files.

Example:
    from your_cli.tui.widgets import AlertCard, MetricCard, SparklineCard
"""

from .cards import (
    ActionCard,
    ActivityCard,
    AlertCard,
    ComparisonCard,
    KVCard,
    PricingCard,
    ProfileCard,
    ProgressCard,
    SparklineCard,
    TimelineCard,
)
from .metric          import MetricCard
from .pagination_bar  import PaginationBar
from .status_badge    import StatusBadge

__all__ = [
    # Cards
    "ActionCard",
    "ActivityCard",
    "AlertCard",
    "ComparisonCard",
    "KVCard",
    "PricingCard",
    "ProfileCard",
    "ProgressCard",
    "SparklineCard",
    "TimelineCard",
    # Standalone
    "MetricCard",
    "PaginationBar",
    "StatusBadge",
]

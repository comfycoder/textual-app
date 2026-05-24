"""PricingCard — pricing tier card with feature checklist and CTA button."""

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Rule, Static


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
        **kw: Any,
    ) -> None:
        existing = kw.pop("classes", "")
        classes  = ("-highlight " + existing).strip() if highlight else existing
        super().__init__(classes=classes, **kw)
        self._tier      = tier
        self._price     = price
        self._period    = period
        self._features  = features
        self._cta       = cta
        self._highlight = highlight

    def compose(self) -> ComposeResult:
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
            yield Button(self._cta, variant="primary" if self._highlight else "default")

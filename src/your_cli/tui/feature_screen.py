"""Base class for all navigable feature screens.

Every demo screen (and the dashboard / edit screens) inherits from this
instead of Screen[None] directly.  It provides:

  - A canonical Escape → go_back binding so each screen doesn't have to
    declare it.  Textual collects BINDINGS from the full MRO, so subclasses
    that declare extra bindings simply omit the Escape entry.
  - A single action_go_back() implementation.

CSS_PATH must still be set in each subclass because it must resolve to that
subclass's own package directory, not to this file's directory.
"""

from textual.binding import Binding
from textual.screen import Screen


class FeatureScreen(Screen[None]):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def action_go_back(self) -> None:
        self.app.pop_screen()

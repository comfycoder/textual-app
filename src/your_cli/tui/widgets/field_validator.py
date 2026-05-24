"""Field-error helpers that hide Textual's private SelectCurrent internals.

Import these functions instead of reaching into textual.widgets._select
directly.  All knowledge of SelectCurrent lives here; every other module
stays clean.

Usage
-----
    from your_cli.tui.widgets.field_validator import (
        clear_all_select_errors,
        set_field_error,
    )

    # Toggle error state on a single label + widget pair:
    set_field_error(label, widget, has_error=True, error_hex=hex_color)

    # Bulk-clear all Select highlights inside a container (e.g. on form reset):
    clear_all_select_errors(self.query_one("#my-form"))

Background
----------
Select widgets render through an inner SelectCurrent child that overrides its
own DEFAULT_CSS background at higher specificity than any external CSS class.
The only reliable way to highlight a Select as invalid is to set an inline
style directly on SelectCurrent.  Inline styles win over DEFAULT_CSS.
Setting the inline style to None calls clear_rule() and restores the default.
"""

from textual.widget import Widget
from textual.widgets import Label, Select
from textual.widgets._select import SelectCurrent as _SelectCurrent  # private Textual API


def set_field_error(
    label: Label,
    widget: Widget,
    has_error: bool,
    error_hex: str = "#ba3c5b",
) -> None:
    """Toggle field-error CSS classes and, for Select widgets, the inline background.

    Args:
        label:     The Label widget that describes the field.
        widget:    The Input, Select, or other widget being validated.
        has_error: True to mark the field invalid, False to clear it.
        error_hex: Hex colour for the Select background tint (default matches
                   Textual's built-in $error variable).  Ignored when
                   has_error is False.  Callers should pass
                   ``app.get_css_variables().get("error", "#ba3c5b")`` to
                   keep in sync with the active theme.
    """
    if has_error:
        label.add_class("field-error-label")
        widget.add_class("field-error")
    else:
        label.remove_class("field-error-label")
        widget.remove_class("field-error")

    # CSS class overrides don't reach SelectCurrent's DEFAULT_CSS — use
    # inline styles instead, which always win.
    if isinstance(widget, Select):
        bg = f"{error_hex} 15%" if has_error else None
        for child in widget.children:
            if isinstance(child, _SelectCurrent):
                child.styles.background = bg


def clear_all_select_errors(container: Widget) -> None:
    """Remove the error background from every Select inside *container*.

    Call this during a bulk form-reset rather than iterating Select widgets
    and touching _SelectCurrent manually in screen code.
    """
    for sel in container.query(Select):
        for child in sel.children:
            if isinstance(child, _SelectCurrent):
                child.styles.background = None

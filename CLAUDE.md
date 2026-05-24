# Claude Development Rules

This file captures hard-won lessons from building this project. Follow these rules to avoid repeating known bugs.

---

## Textual-specific rules

### Select widget — clearing a selection

**Rule:** Use `select.clear()` to reset a Select to no-selection. Never set `select.value = Select.BLANK`.

**Why:** In Textual 8.x, `Select.BLANK` is a sentinel that is only valid for reading. Setting `.value = Select.BLANK` raises `InvalidSelectValueError: Illegal select value False`.

```python
# ✗ Wrong — raises InvalidSelectValueError
select.value = Select.BLANK

# ✓ Correct
select.clear()
```

---

### Select widget — testing for "no selection" in filter logic

**Rule:** Use `isinstance(value, str)` to test whether a Select has a real selection, not `value is not Select.BLANK`.

**Why:** After calling `select.clear()`, the widget value becomes `None` (not `Select.BLANK`). The check `value is not Select.BLANK` then evaluates `True`, and the filter runs with `None` as the comparison value, silently returning zero results.

All real option values in this project are strings, so `isinstance` is the robust guard.

```python
# ✗ Wrong — breaks silently after select.clear()
if status is not Select.BLANK:
    results = [r for r in results if r["status"] == status]

# ✓ Correct
if isinstance(status, str):
    results = [r for r in results if r["status"] == status]
```

---

### MaskedInput — placeholder text

**Rule:** Never use the `placeholder=` parameter on `MaskedInput`. Put example text in the field `Label` instead.

**Why:** In `MaskedInput`, the `placeholder` parameter fills the template slot characters positionally (not as hint text), producing garbled display. Use `[dim]` markup in the label to show format examples.

```python
# ✗ Wrong — placeholder fills template slots, looks broken
yield MaskedInput(template="99/99/9999", placeholder="DD/MM/YYYY")

# ✓ Correct
yield Label("Date  [dim]DD/MM/YYYY[/dim]")
yield MaskedInput(template="99/99/9999")
```

---

### SuggestFromList — accepting suggestions

**Rule:** Document that suggestions are accepted with the **→ (right arrow)** key, not Tab.

**Why:** Tab is intercepted by Textual's focus system before it reaches the Input widget, so it moves focus rather than accepting the suggestion. Only the right arrow key reliably accepts an inline suggestion.

---

### RadioButton — mutual exclusivity

**Rule:** Standalone `RadioButton` widgets are independent. Wrap them in a `RadioSet` to get mutual exclusivity.

```python
# ✗ Wrong — buttons are independent, any combination can be active
yield RadioButton("Low",    id="rb-low")
yield RadioButton("Medium", id="rb-medium")

# ✓ Correct — only one active at a time
with RadioSet(id="rb-priority"):
    yield RadioButton("Low")
    yield RadioButton("Medium")
```

Use `on_radio_set_changed` (not `on_radio_button_changed`) to react to changes, and read the active choice via `radio_set.pressed_button.label.plain`.

---

### Tabs + ContentSwitcher — checking for existing panels

**Rule:** Use `switcher.query(f"#{tab_id}")` (falsy when empty) to test whether a panel exists. Never access `switcher._nodes._by_id`.

**Why:** `NodeList` does not expose a `_by_id` attribute — accessing it raises `AttributeError`.

```python
# ✗ Wrong — AttributeError
if tab_id in switcher._nodes._by_id:
    ...

# ✓ Correct
if switcher.query(f"#{tab_id}"):
    ...
```

---

### DataTable inside a scrollable page — sizing

**Rule:** When a `DataTable` sits inside a `ScrollableContainer` (full-page scroll), give it a fixed line height (e.g. `height: 30`) rather than `height: 1fr`.

**Why:** `1fr` means "fill remaining space in the parent". Inside a `ScrollableContainer` whose content has `height: auto`, there is no bounded remaining space — the table collapses to zero or expands infinitely.

```css
/* ✓ Correct — fixed height inside a scrollable page */
#my-table {
    height: 30;
}

/* ✓ Correct — fills a fixed-height non-scrollable container */
#my-table {
    height: 1fr;
}
```

---

### Field validation highlight — use label colour, not widget border

**Rule:** Do not rely on `border` CSS overrides to highlight invalid form fields. Textual's default widget CSS has higher specificity and the override silently fails for both `Input` and `Select`. Instead, add a CSS class to the field's `Label` widget and style that.

```python
# ✓ Correct — add an ID to each required field's Label
yield Label("Tenant", id="lbl-tenant", classes="my-label")
yield Input(id="fld-tenant")

# On validation failure:
self.query_one("#lbl-tenant", Label).add_class("field-error-label")
# On fix (on_input_changed / on_select_changed):
self.query_one("#lbl-tenant", Label).remove_class("field-error-label")
```

```css
/* styles.tcss */
Label.field-error-label {
    color: $error;
    text-style: bold;
}
Input.field-error {
    background: $error 15%;
}
```

**Note:** Textual does **not** support the `:invalid` pseudo-class. Use a manually-toggled `.field-error` class on the `Input` widget instead.

For `Select` widgets, the visible surface is the inner `SelectCurrent` child widget, not the `Select` itself. CSS class rules on `SelectCurrent` don't reliably override its DEFAULT_CSS `background: $surface`. The `widget.query("SelectCurrent")` string selector can also silently return nothing for internal/unexported widget types.

**Correct approach:** import `SelectCurrent` directly and walk `widget.children` with `isinstance`. Use inline styles — they always win over all CSS. Setting to `None` calls `clear_rule()` and restores the CSS-driven default.

```python
from textual.widgets._select import SelectCurrent as _SelectCurrent  # not in public __init__

# In _set_field_error, after the label / widget class logic:
if isinstance(widget, Select):
    err = self.app.get_css_variables().get("error", "#ba3c5b") if has_error else None
    for child in widget.children:
        if isinstance(child, _SelectCurrent):
            child.styles.background = f"{err} 15%" if has_error else None
```

Key facts about `widget.styles.background`:
- `"#hexcolor 15%"` — color + alpha% string; splits on whitespace internally
- `Color(...)` — accepted directly
- `None` — calls `clear_rule()`, restores CSS-driven value
- `app.get_css_variables()["error"]` returns a plain hex string (e.g. `"#ba3c5b"`)

---

### Static inside a Horizontal — width defaults to 1fr

**Rule:** When placing a `Static` widget between other widgets in a `Horizontal` container, always set `width: auto` on it (or give it an explicit width). Without it the Static expands to fill all remaining space and pushes everything to its right off screen.

```css
/* ✗ Wrong — Static consumes all remaining width, Next button hidden */
#my-label { padding: 0 2; }

/* ✓ Correct */
#my-label { width: auto; padding: 0 2; }
```

---

### DataTable — avoid padding in CSS

**Rule:** Do not set `padding` on a `DataTable` widget.

**Why:** Padding clips the DataTable's internal scroll viewport, making rows below the padding boundary unreachable by keyboard navigation.

---

### OptionList — guarding None separators

**Rule:** When iterating `OptionList` items (e.g. to match a highlighted option against an action list), always guard against `None` entries before tuple-unpacking.

**Why:** `None` entries in the items list are rendered as visual separators. Unpacking them as tuples raises `TypeError`.

```python
# ✗ Wrong — crashes on None separators
for label, id_, desc in _ACTIONS:
    ...

# ✓ Correct
for item in _ACTIONS:
    if item is not None and item[1] == opt_id:
        ...
```

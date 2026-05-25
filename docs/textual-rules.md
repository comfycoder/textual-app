# Textual-specific rules

Hard-won lessons specific to **Textual 8.x**. Check this file before writing any new screen or widget code.

---

## Select widget — clearing a selection

**Rule:** Use `select.clear()` to reset a Select to no-selection. Never set `select.value = Select.BLANK`.

**Why:** In Textual 8.x, `Select.BLANK` is a sentinel that is only valid for reading. Setting `.value = Select.BLANK` raises `InvalidSelectValueError: Illegal select value False`.

```python
# ✗ Wrong — raises InvalidSelectValueError
select.value = Select.BLANK

# ✓ Correct
select.clear()
```

---

## Select widget — testing for "no selection" in filter logic

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

## MaskedInput — placeholder text

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

## SuggestFromList — accepting suggestions

**Rule:** Document that suggestions are accepted with the **→ (right arrow)** key, not Tab.

**Why:** Tab is intercepted by Textual's focus system before it reaches the Input widget, so it moves focus rather than accepting the suggestion. Only the right arrow key reliably accepts an inline suggestion.

---

## RadioButton — mutual exclusivity

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

## Tabs + ContentSwitcher — checking for existing panels

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

## DataTable inside a scrollable page — sizing

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

## Field validation highlight — use label colour, not widget border

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

## Static inside a Horizontal — width defaults to 1fr

**Rule:** When placing a `Static` widget between other widgets in a `Horizontal` container, always set `width: auto` on it (or give it an explicit width). Without it the Static expands to fill all remaining space and pushes everything to its right off screen.

```css
/* ✗ Wrong — Static consumes all remaining width, Next button hidden */
#my-label { padding: 0 2; }

/* ✓ Correct */
#my-label { width: auto; padding: 0 2; }
```

---

## DataTable — avoid padding in CSS

**Rule:** Do not set `padding` on a `DataTable` widget.

**Why:** Padding clips the DataTable's internal scroll viewport, making rows below the padding boundary unreachable by keyboard navigation.

---

## Static next to Buttons — vertical text alignment

**Rule:** A `Static` placed alongside `Button` widgets in a `Horizontal` bar will have its text at the top, not centred, even when the parent has `align: left middle`. Give the Static `height: 3` (matching Button's height) and `content-align: left middle` so the text sits on the same visual line as the button labels.

**Why:** Buttons have `min-height: 3` and `border: tall` so they always occupy 3 rows. `align: left middle` on the parent positions the child widget's *box*, but if the Static's box is only 1 row tall (auto height) the text is already at the top — there is nothing to centre.

```css
/* ✗ Wrong — text sits at the top of the bar */
#my-label { width: auto; padding: 0 2; }

/* ✓ Correct — text sits on the same row as button text */
#my-label { width: auto; height: 3; padding: 0 2; content-align: left middle; }
```

---

## Static replacing an Input — matching position and height

**Rule:** When displaying a read-only value in place of an `Input` widget, give the Static `height: 3; padding: 1 0 1 3` to match the Input's dimensions exactly.

**Why:** `Input` has `height: 3`, `border: tall` (1 cell each side), and `padding: 0 2`, so its text starts 3 cells from the widget's left edge (1 border + 2 padding) and sits on row 1 of 3. Without the matching padding the read-only text appears misaligned both vertically and horizontally relative to the other form fields.

```css
.my-readonly-display {
    height: 3;
    padding: 1 0 1 3;   /* top:1 matches border-top, left:3 matches border+padding */
}
```

---

## DataTable — sortable columns

**Rule:** Use `add_column(label, key=key)` (not `add_columns`) and store the returned `ColumnKey` objects. Handle `DataTable.HeaderSelected` to detect clicks; read the clicked key with `event.column_key.value`.

**Why:** `add_columns` returns keys but gives no per-column control. Storing keys lets you look up `tbl.columns[ck]` to update labels later.

```python
# Store keys at mount time
self._col_keys = {key: tbl.add_column(label, key=key) for label, key in _COLUMNS}

# Sort handler
def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
    col_key = event.column_key.value   # the string you passed to add_column
    ...
```

---

## DataTable — updating column labels (sort indicators)

**Rule:** After changing `column.label`, check whether the new label is wider than `column.content_width`. If so, bump `content_width` manually and set `tbl._require_update_dimensions = True`, then call `tbl.refresh()`.

**Why:** Auto-width columns (`auto_width=True`, the default) size themselves to `content_width`, which is set at creation and updated only when cells are added. Changing the label text alone does not widen the column — the indicator character gets silently clipped.

```python
from rich.text import Text

def _update_column_headers(self) -> None:
    tbl = self.query_one("#my-table", DataTable)
    changed = False
    for label, key in _COLUMNS:
        col = tbl.columns[self._col_keys[key]]
        new_label = Text(label + indicator)
        col.label = new_label
        w = len(label + indicator)
        if w > col.content_width:
            col.content_width = w
            changed = True
    if changed:
        tbl._require_update_dimensions = True
    tbl.refresh()
```

---

## DataTable — multi-line rows and wrapping

**Rule:** Pass `height=None` to `add_row` for automatic row height. For cell content to actually *wrap*, the column must have a **fixed width** set via `add_column(label, key=key, width=N)`. Auto-width columns always expand to fit content on one line and never wrap regardless of row height.

```python
# Fixed width on columns that should wrap
tbl.add_column("Tags", key="tags", width=22)

# Auto height — Textual measures the content and sets the minimum lines needed
tbl.add_row(..., height=None)
```

---

## DataTable — zebra striping

**Rule:** Pass `zebra_stripes=True` to the `DataTable` constructor. No CSS needed — Textual applies `.datatable--even-row` / `.datatable--odd-row` automatically and the colours are theme-driven.

```python
yield DataTable(id="my-table", cursor_type="row", zebra_stripes=True)
```

---

## ListView — dynamic rebuild and duplicate IDs

**Rule:** Do not assign `id=` to `ListItem`s that will be cleared and re-added. After `lv.clear()`, Textual's internal `_nodes_by_id` map is not immediately flushed, so re-inserting items with the same IDs raises `DuplicateIds`. Omit the `id=` unless you need to query a specific item by ID.

```python
# ✗ Wrong — DuplicateIds on second rebuild
lv.append(ListItem(Label(text), id=f"item-{i}"))

# ✓ Correct — no ID needed when you navigate by lv.index
lv.append(ListItem(Label(text)))
```

---

## OptionList — guarding None separators

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

---

## CSS — `justify` is not a valid property

**Rule:** Do not use `justify:` in TCSS. Use `align: <horizontal> <vertical>` instead.

```css
/* ✗ Wrong — CSS parse error: Invalid CSS property 'justify' */
#my-container { justify: center; }

/* ✓ Correct */
#my-container { align: left middle; }
```

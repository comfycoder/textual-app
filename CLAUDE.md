# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A Textual TUI for the AIQ platform. The app opens a **Widget Gallery** — 44 runnable demos covering nearly every Textual widget and pattern — plus the main work-items dashboard.

---

## Commands

```bash
# Environment setup (Conda)
conda env create -f environment.yml       # First time
conda env update -f environment.yml --prune  # Update

# Run the app
your-cli                                  # Launch TUI
textual run --dev src/your_cli/__main__.py  # Hot-reload (run textual console in second terminal)

# Lint / type-check / test
ruff check .                              # Linter (100-char line limit, py312)
mypy src                                  # Type checking (strict; generated client excluded)
pytest                                    # Run tests

# Regenerate API client (do not hand-edit src/your_cli/client/)
./scripts/regen-client.sh
```

---

## Architecture

**Entry flow:** `your-cli` CLI (Typer) → `src/your_cli/cli.py::run()` → loads Pydantic `Settings` → instantiates `YourCliApp` → `navigate(self, "gallery")`.

**Source layout:**
- `src/your_cli/cli.py` — CLI entry point; also handles `login`/`logout` subcommands
- `src/your_cli/config.py` — Pydantic `Settings`; env prefix `AIQ_`, optional `.env` via `--config`
- `src/your_cli/tui/app.py` — Root `YourCliApp`; registers 7 themes on mount; global bindings `q` (quit), `d` (dark toggle)
- `src/your_cli/tui/themes.py` — 7 themes (AIQ, AIQ_DARK, Nord, Gruvbox, Dracula, Solarized Light, Warm Linen)
- `src/your_cli/tui/styles.tcss` — Global CSS only: `Screen`, `Switch`, shared `.demo-label`/`.demo-row` utilities, form-validation helpers, `ConfirmModal`
- `src/your_cli/tui/router.py` — `navigate(app, key)` lazy-loads the screen module via `importlib` and calls `app.push_screen()`
- `src/your_cli/tui/routes.py` — **Single source of truth** for all routes: 45 `register(key, module_path, class_name)` calls; edit only this file to add, rename, or remove a screen
- `src/your_cli/tui/widgets/` — 12 reusable widget classes (10 card types, `MetricCard`, `StatusBadge`); import with `from your_cli.tui.widgets import MetricCard, AlertCard`
- `src/your_cli/tui/features/` — 45 feature packages, one per screen (or screen-group); each contains `__init__.py`, `screen.py`, and `styles.tcss`
  - `features/gallery/` — navigation hub (`GalleryScreen`)
  - `features/dashboard/` — two-pane dashboard; also contains `detail.py` (`DetailScreen`)
  - `features/<name>/` — one package per demo (43 total)
- `src/your_cli/client/` — Auto-generated OpenAPI client; never hand-edit

**Screen navigation:** `navigate(app, key)` in `router.py` lazy-imports the target module on first use and calls `app.push_screen()`. Escape calls `app.pop_screen()` via `action_go_back()` in each screen. `GalleryScreen` is the hub: its `ListView.Selected` handler calls `navigate(self.app, key)`. `routes.py` is the only file that maps route keys to screen modules.

**Most complete demo:** `features/search_grid/screen.py` — filter bar + pageable DataTable + sortable columns + full edit form with validation; good reference for complex screen patterns.

---

## Configuration

Settings priority (highest first): CLI flags → `AIQ_*` env vars → `.env` file (`--config path`) → defaults in `src/your_cli/config.py`.

Key env vars:
```
AIQ_API_BASE_URL=https://api.aiq.example.com
AIQ_TENANT_ID=00000000-0000-0000-0000-000000000000
AIQ_CLIENT_ID=00000000-0000-0000-0000-000000000000
```

---

## Adding a new demo screen

Three touch-points are required every time:

1. **Create** `src/your_cli/tui/features/<key>/` containing three files:
   - `__init__.py` — one line: `"""Feature package."""`
   - `screen.py` — `Screen[None]` subclass with `CSS_PATH = Path(__file__).parent / "styles.tcss"` and `BINDINGS = [Binding("escape", "go_back", "Back")]`
   - `styles.tcss` — feature-scoped CSS (can be empty to start)

2. **Register the gallery entry** in `GalleryScreen.DEMOS` (`features/gallery/screen.py`) — add a `("Display Name", "<key>", "one-line description")` tuple.

3. **Register the route** in `routes.py` — add one line:
   ```python
   register("<key>", "your_cli.tui.features.<key>.screen", "YourScreenClass")
   ```

`GalleryScreen._open_demo()` calls `navigate(self.app, key)`, which picks up the new entry automatically. No other files need to change.

---

## Windows requirement

Requires **Windows Terminal** (default on Windows 11). Legacy `cmd.exe` and PowerShell 5.1 in `conhost` are not supported.

---

## Textual-specific rules

This section captures hard-won lessons specific to **Textual 8.x**. Check before writing any new screen or widget code.

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

### Static next to Buttons — vertical text alignment

**Rule:** A `Static` placed alongside `Button` widgets in a `Horizontal` bar will have its text at the top, not centred, even when the parent has `align: left middle`. Give the Static `height: 3` (matching Button's height) and `content-align: left middle` so the text sits on the same visual line as the button labels.

**Why:** Buttons have `min-height: 3` and `border: tall` so they always occupy 3 rows. `align: left middle` on the parent positions the child widget's *box*, but if the Static's box is only 1 row tall (auto height) the text is already at the top — there is nothing to centre.

```css
/* ✗ Wrong — text sits at the top of the bar */
#my-label { width: auto; padding: 0 2; }

/* ✓ Correct — text sits on the same row as button text */
#my-label { width: auto; height: 3; padding: 0 2; content-align: left middle; }
```

---

### Static replacing an Input — matching position and height

**Rule:** When displaying a read-only value in place of an `Input` widget, give the Static `height: 3; padding: 1 0 1 3` to match the Input's dimensions exactly.

**Why:** `Input` has `height: 3`, `border: tall` (1 cell each side), and `padding: 0 2`, so its text starts 3 cells from the widget's left edge (1 border + 2 padding) and sits on row 1 of 3. Without the matching padding the read-only text appears misaligned both vertically and horizontally relative to the other form fields.

```css
.my-readonly-display {
    height: 3;
    padding: 1 0 1 3;   /* top:1 matches border-top, left:3 matches border+padding */
}
```

---

### DataTable — sortable columns

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

### DataTable — updating column labels (sort indicators)

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

### DataTable — multi-line rows and wrapping

**Rule:** Pass `height=None` to `add_row` for automatic row height. For cell content to actually *wrap*, the column must have a **fixed width** set via `add_column(label, key=key, width=N)`. Auto-width columns always expand to fit content on one line and never wrap regardless of row height.

```python
# Fixed width on columns that should wrap
tbl.add_column("Tags", key="tags", width=22)

# Auto height — Textual measures the content and sets the minimum lines needed
tbl.add_row(..., height=None)
```

---

### DataTable — zebra striping

**Rule:** Pass `zebra_stripes=True` to the `DataTable` constructor. No CSS needed — Textual applies `.datatable--even-row` / `.datatable--odd-row` automatically and the colours are theme-driven.

```python
yield DataTable(id="my-table", cursor_type="row", zebra_stripes=True)
```

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

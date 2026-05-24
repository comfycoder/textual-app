# Architecture Refactoring Plan

Derived from the [2026-05-24 architecture review](index.html).
Phases are ordered lowest → highest blast radius and are independent — stop after any one.

---

## Phase 1 — Fix the `search_grid` data seam
**Candidate 3 · Files: 1 edit**

`screen.py` lines 29–80 are a verbatim copy of everything already in `_data.py`.
The seam exists; it just isn't being used.

- Delete the 52-line duplicate block from `screen.py`
- Replace with `from ._data import (_STATUS_OPTS, _STATUS_COLORS, _PRI_COLORS, _RECORDS, _RECORD_BY_ID, _PAGE_SIZE_OPTS, _DEFAULT_PAGE_SIZE, _SG_COLUMNS, ...)`
- `_data.py` is unchanged — it already holds the canonical copies

---

## Phase 2 — Centralize color maps into `tui/palette.py`
**Candidate 2 · Files: 1 new + 8 edits**

`_STATUS_COLORS` is copy-pasted into 8 files. `_PRI_COLORS` into 3.

- Create `src/your_cli/tui/palette.py` with `STATUS_COLORS` and `PRI_COLORS`
- Remove local declarations from: `multiselect`, `pagination`, `inline_edit`,
  `live_dashboard`, `context_menu`, `form_table`, `master_detail`, `search_grid/_data.py`
- Each file gets one import line instead of 5 lines of dict

---

## Phase 3 — `FeatureScreen` base class
**Candidate 5 · Files: 1 new + 41 edits**

Every demo screen declares the same escape binding and `action_go_back`.
Textual collects `BINDINGS` up the MRO, so a base-class binding is additive —
subclasses with extra bindings just omit the escape entry.

- Create `src/your_cli/tui/feature_screen.py`:

  ```python
  class FeatureScreen(Screen[None]):
      BINDINGS = [Binding("escape", "go_back", "Back")]

      def action_go_back(self) -> None:
          self.app.pop_screen()
  ```

- In each of the 41 demo screens: change `(Screen[None])` → `(FeatureScreen)`,
  drop the escape `Binding(...)` entry, drop `action_go_back`
- `GalleryScreen` stays `Screen[None]` — its Escape quits the app, not pops
- `CSS_PATH = Path(__file__).parent / "styles.tcss"` stays in each screen
  (must resolve to the *subclass* package directory)

---

## Phase 4 — `FieldValidator` module
**Candidate 1 · Files: 1 new + 3 edits**

The `_SelectCurrent` private import and label-colouring pattern is duplicated across
`search_grid/screen.py`, `search_grid/edit.py`, and `form_validation/screen.py`.
One deep module hides it behind a stable interface.

- Create `src/your_cli/tui/widgets/field_validator.py`:

  ```python
  def set_field_error(
      label: Label,
      widget: Input | Select,
      has_error: bool,
      message: str = "",
  ) -> None: ...
  ```

  Contains the `_SelectCurrent` import and all inline-style logic.

- Update the three callers to use it; `_SelectCurrent` disappears from feature code entirely

---

## Phase 5 — `Paginator` dataclass
**Candidate 4 · Files: 1 new + 2 edits**

Page-math is reimplemented independently in `pagination/screen.py` and `search_grid/screen.py`.

- Create `src/your_cli/tui/paginator.py`:

  ```python
  @dataclass
  class Paginator:
      total: int
      page_size: int
      page: int = 0

      @property
      def page_count(self) -> int: ...
      def slice(self) -> tuple[int, int]: ...  # (start, end) for list slicing
      def next(self) -> bool: ...              # returns True if page changed
      def prev(self) -> bool: ...
  ```

- Update `pagination/screen.py` and the page logic in `search_grid/screen.py`

---

## Skipped — Candidate 6 (route child screens through `navigate()`)

`EditJobScreen` takes a live record dict as a constructor argument; routing it through
the string-key registry would need a different state-passing mechanism.
Friction is low and the change is structural enough to warrant a grilling conversation first.

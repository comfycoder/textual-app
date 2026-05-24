# Refactoring Plan: Feature-based Architecture

**Date:** 2026-05-24  
**Scope:** `src/your_cli/tui/`  
**Principles:** DRY · SRP · feature-co-location · lazy routing  
**Approach:** Four independent phases, each mergeable and deployable on its own.

---

## 1. Problems being solved

| # | Symptom | Principle violated |
|---|---------|-------------------|
| 1 | Widget classes (`AlertCard`, `MetricCard`, etc.) defined in demo screen files and imported *from* those demo files by other screens | DRY — one definition, but the demo file is now load-bearing infrastructure |
| 2 | `GalleryScreen._open_demo()` owns a 50-line import block and a 45-entry dict; gallery's job is navigation UI, not knowing every screen in the app | SRP — gallery does two jobs |
| 3 | All 1 400+ lines of CSS live in one `styles.tcss`; every feature's CSS is in the same file | SRP — one file owns all styling concerns |
| 4 | 44 screen files are siblings in a flat `screens/` directory with no feature grouping | Discoverability / SRP — unrelated concerns share a namespace |

---

## 2. Target structure

```
src/your_cli/
├── cli.py
├── config.py
└── tui/
    ├── app.py              # Root App — themes, global bindings, initial screen
    ├── themes.py           # Theme objects only
    ├── styles.tcss         # Global-only rules (Screen, DataTable, Switch, shared utilities)
    ├── router.py           # navigate() — lazy importlib screen loading
    ├── routes.py           # Central registry: key → (module_path, class_name)
    │
    ├── widgets/            # All reusable widget classes (no screen logic)
    │   ├── __init__.py     # Re-exports everything for one-line consumer imports
    │   ├── cards/
    │   │   ├── __init__.py
    │   │   ├── alert.py        # AlertCard
    │   │   ├── action.py       # ActionCard
    │   │   ├── activity.py     # ActivityCard
    │   │   ├── comparison.py   # ComparisonCard
    │   │   ├── kv.py           # KVCard
    │   │   ├── pricing.py      # PricingCard
    │   │   ├── profile.py      # ProfileCard
    │   │   ├── progress.py     # ProgressCard
    │   │   ├── sparkline.py    # SparklineCard
    │   │   └── timeline.py     # TimelineCard
    │   ├── metric.py           # MetricCard
    │   └── status_badge.py     # StatusBadge
    │
    └── features/               # One folder per screen or screen-group
        ├── gallery/
        │   ├── screen.py
        │   └── styles.tcss
        ├── dashboard/
        │   ├── screen.py       # DashboardScreen
        │   ├── detail.py       # DetailScreen (only ever pushed from DashboardScreen)
        │   └── styles.tcss
        ├── search_grid/
        │   ├── screen.py       # SearchGridDemoScreen (list + filter)
        │   ├── edit.py         # EditJobScreen (pushed from SearchGridDemoScreen)
        │   └── styles.tcss
        ├── context_menu/
        │   ├── screen.py       # ContextMenuDemoScreen
        │   ├── modal.py        # ContextMenuModal
        │   └── styles.tcss
        ├── command_palette/
        │   ├── screen.py       # CommandPaletteDemoScreen
        │   ├── modal.py        # CommandPaletteModal
        │   └── styles.tcss
        ├── help_keys/
        │   ├── screen.py       # HelpKeysDemoScreen
        │   ├── modal.py        # HelpModal
        │   └── styles.tcss
        ├── <name>/             # All remaining single-screen features
        │   ├── screen.py
        │   └── styles.tcss
        └── ...
```

---

## 3. Phases overview

| Phase | Name | Changes files | Can merge alone? |
|-------|------|--------------|-----------------|
| 1 | Widget library | ~16 new, 3 modified | Yes |
| 2 | Router infrastructure | 2 new, 2 modified | Yes |
| 3 | Feature folder migration | ~90 new, 44 deleted, 2 modified | Yes, screen-by-screen |
| 4 | CSS co-location | Trim `styles.tcss` | Do as part of Phase 3 |

Recommended merge order: **Phase 1 → Phase 2 → Phase 3+4 (one feature at a time)**.  
Phases 1 and 2 are independent and can be done in parallel on separate branches.

---

## Phase 1 — Widget library

**Goal:** Every reusable widget class lives in `tui/widgets/`. No screen file defines a widget that is imported by another screen file.

### 1.1 Create files

Create the following new files by cutting the class body from its current source and pasting it into the new file. The class itself is unchanged; only its location moves.

| New file | Class to move | Cut from |
|----------|--------------|----------|
| `widgets/cards/alert.py` | `AlertCard` | `screens/demo_cards.py` |
| `widgets/cards/action.py` | `ActionCard` | `screens/demo_cards.py` |
| `widgets/cards/kv.py` | `KVCard` | `screens/demo_cards.py` |
| `widgets/cards/profile.py` | `ProfileCard` | `screens/demo_cards.py` |
| `widgets/cards/progress.py` | `ProgressCard` | `screens/demo_cards.py` |
| `widgets/cards/activity.py` | `ActivityCard` | `screens/demo_cards2.py` |
| `widgets/cards/comparison.py` | `ComparisonCard` | `screens/demo_cards2.py` |
| `widgets/cards/pricing.py` | `PricingCard` | `screens/demo_cards2.py` |
| `widgets/cards/sparkline.py` | `SparklineCard` | `screens/demo_cards2.py` |
| `widgets/cards/timeline.py` | `TimelineCard` | `screens/demo_cards2.py` |
| `widgets/metric.py` | `MetricCard` | `screens/demo_custom_widget.py` |
| `widgets/status_badge.py` | `StatusBadge` | `screens/demo_custom_widget.py` |

### 1.2 Create `__init__` files

**`widgets/cards/__init__.py`**
```python
from .alert      import AlertCard
from .action     import ActionCard
from .activity   import ActivityCard
from .comparison import ComparisonCard
from .kv         import KVCard
from .pricing    import PricingCard
from .profile    import ProfileCard
from .progress   import ProgressCard
from .sparkline  import SparklineCard
from .timeline   import TimelineCard

__all__ = [
    "AlertCard", "ActionCard", "ActivityCard", "ComparisonCard",
    "KVCard", "PricingCard", "ProfileCard", "ProgressCard",
    "SparklineCard", "TimelineCard",
]
```

**`widgets/__init__.py`**
```python
from .cards       import (AlertCard, ActionCard, ActivityCard, ComparisonCard,
                           KVCard, PricingCard, ProfileCard, ProgressCard,
                           SparklineCard, TimelineCard)
from .metric      import MetricCard
from .status_badge import StatusBadge

__all__ = [
    "AlertCard", "ActionCard", "ActivityCard", "ComparisonCard",
    "KVCard", "PricingCard", "ProfileCard", "ProgressCard",
    "SparklineCard", "TimelineCard",
    "MetricCard", "StatusBadge",
]
```

### 1.3 Modify existing screen files

After cutting, each source file retains only its demo `Screen` subclass. Update the imports at the top of each file to pull from `widgets/`.

**`screens/demo_cards.py`** — remove the 5 widget class definitions; add:
```python
from your_cli.tui.widgets import AlertCard, ActionCard, KVCard, ProfileCard, ProgressCard
```

**`screens/demo_cards2.py`** — remove the 5 widget class definitions; add:
```python
from your_cli.tui.widgets import ActivityCard, ComparisonCard, PricingCard, SparklineCard, TimelineCard
```

**`screens/demo_custom_widget.py`** — remove `MetricCard` and `StatusBadge`; add:
```python
from your_cli.tui.widgets import MetricCard, StatusBadge
```

**`screens/demo_dicom_nrrd.py`** — update the three existing imports to:
```python
from your_cli.tui.widgets import AlertCard, KVCard, ProgressCard
from your_cli.tui.widgets import ActivityCard, SparklineCard, TimelineCard
from your_cli.tui.widgets import MetricCard
```
(or collapse to one line: `from your_cli.tui.widgets import AlertCard, ActivityCard, KVCard, MetricCard, ProgressCard, SparklineCard, TimelineCard`)

### 1.4 Verification

```bash
ruff check src/your_cli/tui/widgets/
mypy src/your_cli/tui/widgets/
python -c "from your_cli.tui.widgets import AlertCard, MetricCard, SparklineCard; print('ok')"
your-cli   # smoke test — Cards, Cards II, DICOM→NRRD, Custom Widgets demos must open
```

---

## Phase 2 — Router infrastructure

**Goal:** `GalleryScreen` no longer imports or lists every screen. A single `routes.py` owns the complete route map. `_open_demo()` is replaced by a one-liner.

### 2.1 Create `tui/router.py`

```python
"""Lazy screen router.

Usage:
    from your_cli.tui.router import navigate
    navigate(self.app, "dashboard")
"""
from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

# Registry populated by routes.py at import time.
# Maps route key → (dotted module path, class name)
_REGISTRY: dict[str, tuple[str, str]] = {}


def register(key: str, module_path: str, class_name: str) -> None:
    """Register a route. Called exclusively from routes.py."""
    _REGISTRY[key] = (module_path, class_name)


def navigate(app: App, key: str, **kwargs) -> None:
    """Lazy-load the screen module and push the screen onto the stack."""
    if key not in _REGISTRY:
        app.notify(f"Unknown route: {key!r}", severity="error")
        return
    module_path, class_name = _REGISTRY[key]
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    app.push_screen(cls(**kwargs))
```

### 2.2 Create `tui/routes.py`

Populate from the existing `_open_demo()` dict in `gallery.py`. One `register()` call per route. See the **Feature migration table** in Section 4 for the full list of module paths once Phase 3 is complete.

**Interim routes.py** (pointing at the current `screens/` location, valid before Phase 3):
```python
"""Central route registry. Edit this file to add, remove, or rename routes."""
from your_cli.tui.router import register

register("inputs",       "your_cli.tui.screens.demo_inputs",       "InputsDemoScreen")
register("data",         "your_cli.tui.screens.demo_data",         "DataDemoScreen")
register("layout",       "your_cli.tui.screens.demo_layout",       "LayoutDemoScreen")
register("progress",     "your_cli.tui.screens.demo_progress",     "ProgressDemoScreen")
register("dashboard",    "your_cli.tui.screens.dashboard",         "DashboardScreen")
register("files",        "your_cli.tui.screens.demo_files",        "FilesDemoScreen")
register("apifiles",     "your_cli.tui.screens.demo_api_files",    "ApiFilesDemoScreen")
register("live",         "your_cli.tui.screens.demo_live_dashboard", "LiveDashboardScreen")
register("cmdpalette",   "your_cli.tui.screens.demo_command_palette", "CommandPaletteDemoScreen")
register("logstream",    "your_cli.tui.screens.demo_log_stream",   "LogStreamDemoScreen")
register("wizard",       "your_cli.tui.screens.demo_wizard",       "WizardDemoScreen")
register("report",       "your_cli.tui.screens.demo_report",       "ReportDemoScreen")
register("searchfilter", "your_cli.tui.screens.demo_search_filter","SearchFilterDemoScreen")
register("settings",     "your_cli.tui.screens.demo_settings",     "SettingsDemoScreen")
register("workers",      "your_cli.tui.screens.demo_workers",      "WorkersDemoScreen")
register("contextmenu",  "your_cli.tui.screens.demo_context_menu", "ContextMenuDemoScreen")
register("inlineedit",   "your_cli.tui.screens.demo_inline_edit",  "InlineEditDemoScreen")
register("theme",        "your_cli.tui.screens.demo_theme",        "ThemeToggleDemoScreen")
register("customwidget",  "your_cli.tui.screens.demo_custom_widget","CustomWidgetDemoScreen")
register("formvalidation","your_cli.tui.screens.demo_form_validation","FormValidationDemoScreen")
register("pagination",    "your_cli.tui.screens.demo_pagination",  "PaginationDemoScreen")
register("multiselect",   "your_cli.tui.screens.demo_multiselect", "MultiSelectDemoScreen")
register("contentswitcher","your_cli.tui.screens.demo_content_switcher","ContentSwitcherDemoScreen")
register("helpkeys",      "your_cli.tui.screens.demo_help_keys",   "HelpKeysDemoScreen")
register("optionlist",    "your_cli.tui.screens.demo_option_list", "OptionListDemoScreen")
register("maskedinput",   "your_cli.tui.screens.demo_masked_input","MaskedInputDemoScreen")
register("notifydrawer",  "your_cli.tui.screens.demo_notification_drawer","NotificationDrawerDemoScreen")
register("autocomplete",  "your_cli.tui.screens.demo_autocomplete","AutocompleteDemoScreen")
register("selectionlist", "your_cli.tui.screens.demo_selection_list","SelectionListDemoScreen")
register("togglebutton",  "your_cli.tui.screens.demo_toggle_button","ToggleButtonDemoScreen")
register("rule",          "your_cli.tui.screens.demo_rule",        "RuleDemoScreen")
register("tooltip",       "your_cli.tui.screens.demo_tooltip",     "TooltipDemoScreen")
register("pretty",        "your_cli.tui.screens.demo_pretty",      "PrettyDemoScreen")
register("link",          "your_cli.tui.screens.demo_link",        "LinkDemoScreen")
register("log",           "your_cli.tui.screens.demo_log",         "LogDemoScreen")
register("tabs",          "your_cli.tui.screens.demo_tabs",        "TabsDemoScreen")
register("masterdetail",         "your_cli.tui.screens.demo_master_detail",         "MasterDetailDemoScreen")
register("masterdetailvertical", "your_cli.tui.screens.demo_master_detail_vertical","MasterDetailVerticalScreen")
register("formtable",            "your_cli.tui.screens.demo_form_table",            "FormTableDemoScreen")
register("labelform",            "your_cli.tui.screens.demo_label_form",            "LabelFormDemoScreen")
register("searchgrid",           "your_cli.tui.screens.demo_search_grid",           "SearchGridDemoScreen")
register("cards",                "your_cli.tui.screens.demo_cards",                 "CardsDemoScreen")
register("cards2",               "your_cli.tui.screens.demo_cards2",                "Cards2DemoScreen")
register("dicomnrrd",            "your_cli.tui.screens.demo_dicom_nrrd",            "DicomNrrdDemoScreen")
```

### 2.3 Modify `tui/app.py`

Add one import and remove the direct `GalleryScreen` import:
```python
# Before
from your_cli.tui.screens.gallery import GalleryScreen

# After — routes.py populates the registry as a side-effect of import
import your_cli.tui.routes  # noqa: F401

# on_mount: gallery is now just another route
def on_mount(self) -> None:
    for theme in ALL_THEMES:
        self.register_theme(theme)
    self.theme = "aiq"
    from your_cli.tui.router import navigate
    navigate(self, "gallery")
```

### 2.4 Modify `screens/gallery.py` — replace `_open_demo()`

```python
# Before: 50-line import block + 45-entry dict
def _open_demo(self, key: str) -> None:
    from your_cli.tui.screens.dashboard import DashboardScreen
    # ... 44 more imports ...
    screens = {"inputs": InputsDemoScreen, ...}
    if key in screens:
        self.app.push_screen(screens[key]())

# After: one line
def _open_demo(self, key: str) -> None:
    from your_cli.tui.router import navigate
    navigate(self.app, key)
```

### 2.5 Verification

```bash
ruff check src/your_cli/tui/router.py src/your_cli/tui/routes.py
your-cli   # all 44 gallery items must open
```

---

## Phase 3 — Feature folder migration

**Goal:** Each screen (or screen-group) lives in `tui/features/<name>/`. CSS is co-located in `features/<name>/styles.tcss` via `CSS_PATH`.

### Per-screen migration procedure (repeat for each row in the table below)

1. `mkdir src/your_cli/tui/features/<name>/`
2. Move the screen file(s):
   - `screens/<old>.py` → `features/<name>/screen.py`
   - Any modal defined in the same file → `features/<name>/modal.py`
   - Sub-screens pushed only from this screen → `features/<name>/<sub>.py`
3. Identify the CSS blocks that belong to this screen (use the **CSS prefix** column below).
4. Cut those blocks from `tui/styles.tcss` and paste them into `features/<name>/styles.tcss`.
5. Add `CSS_PATH` to the screen class:
   ```python
   from pathlib import Path
   class MyDemoScreen(Screen[None]):
       CSS_PATH = Path(__file__).parent / "styles.tcss"
   ```
6. Update the corresponding line in `routes.py` to point at the new module path.
7. Create `features/<name>/__init__.py` (empty).
8. Run smoke test: open that demo from the gallery.

### Feature migration table

44 screen files → 44 feature folders. Sorted by complexity (simple first).

| Route key | Feature folder | Screen file(s) | Modal/sub-screen? | CSS prefix(es) in styles.tcss |
|-----------|---------------|----------------|-------------------|-------------------------------|
| `inputs` | `inputs/` | `screen.py` | — | `#inputs-body` |
| `data` | `data_display/` | `screen.py` | — | `TabbedContent`, `TabPane` |
| `layout` | `layout/` | `screen.py` | — | `#demo-grid`, `.grid-cell` |
| `progress` | `progress/` | `screen.py` | — | `#progress-body`, `#demo-sparkline`, `#demo-loader` |
| `files` | `file_manager/` | `screen.py` | — | `#files-body`, `#file-tree`, `#file-preview`, `#file-content`, `#path-bar`, `#selected-path` |
| `apifiles` | `api_files/` | `screen.py` | — | `#api-files-body`, `#api-tree`, `#api-detail`, `#api-content`, `#api-path-bar`, `#api-selected-path` |
| `live` | `live_dashboard/` | `screen.py` | — | `#live-status-bar`, `.refresh-btn` |
| `logstream` | `log_stream/` | `screen.py` | — | `#log-controls`, `#log-output` |
| `wizard` | `wizard/` | `screen.py` | — | `#wizard-body`, `.wizard-step`, `.wizard-title`, `#wizard-step-label`, `#wizard-nav` |
| `report` | `report/` | `screen.py` | — | `#report-body`, `#report-list`, `#report-content`, `#report-md` |
| `searchfilter` | `search_filter/` | `screen.py` | — | `#search-body`, `#search-count` |
| `settings` | `settings/` | `screen.py` | — | `#settings-body`, `#settings-list`, `#settings-content`, `.settings-pane`, `#settings-actions` |
| `workers` | `workers/` | `screen.py` | — | `#workers-body`, `.worker-row`, `.worker-name`, `.worker-status`, `.worker-btn`, `#workers-global` |
| `inlineedit` | `inline_edit/` | `screen.py` | — | `#edit-hint`, `#edit-panel`, `#edit-actions` |
| `theme` | `theme_toggle/` | `screen.py` | — | `#theme-body`, `#theme-list`, `#theme-preview`, `#theme-active-label` |
| `formvalidation` | `form_validation/` | `screen.py` | — | `#vf-body`, `#vf-actions`, `.field-error` |
| `pagination` | `pagination/` | `screen.py` | — | `#page-body`, `#page-controls`, `#page-label` |
| `multiselect` | `multiselect/` | `screen.py` | — | `#ms-body`, `#ms-hint`, `#ms-actions`, `#ms-count` |
| `contentswitcher` | `content_switcher/` | `screen.py` | — | `#cs-body`, `#cs-sidebar`, `#cs-sidebar-title`, `#cs-nav`, `#cs-switcher`, `.cs-panel` |
| `optionlist` | `option_list/` | `screen.py` | — | `#ol-body`, `#ol-left`, `#ol-right`, `#ol-nav-hint`, `.ol-result` |
| `maskedinput` | `masked_input/` | `screen.py` | — | `#mi-body` |
| `notifydrawer` | `notification_drawer/` | `screen.py` | — | `#nd-body`, `#nd-main`, `#nd-buttons`, `#nd-drawer`, `#nd-drawer-header`, `#nd-drawer-title`, `.nd-close-btn`, `.nd-clear-btn`, `#nd-log` |
| `autocomplete` | `autocomplete/` | `screen.py` | — | `#ac-body` |
| `selectionlist` | `selection_list/` | `screen.py` | — | `#sl-body`, `#sl-left`, `#sl-right`, `#sl-hint` |
| `togglebutton` | `toggle_button/` | `screen.py` | — | `#tb-body`, `#tb-left`, `#tb-right`, `#tb-actions` |
| `rule` | `rule/` | `screen.py` | — | `#rule-body`, `.rule-style-label`, `#rule-v-row`, `.rule-panel`, `#rule-form`, `.rule-field` |
| `tooltip` | `tooltip/` | `screen.py` | — | `#tt-body`, `#tt-buttons`, `#tt-form`, `#tt-toggles` |
| `pretty` | `pretty/` | `screen.py` | — | `#pp-body`, `#pp-left`, `#pp-right`, `#pp-widget` |
| `link` | `link/` | `screen.py` | — | `#lk-body` |
| `log` | `log/` | `screen.py` | — | `#lg-controls`, `#lg-body`, `#lg-left`, `#lg-right`, `Log` |
| `tabs` | `tabs/` | `screen.py` | — | `#tabs-outer`, `#tabs-bar`, `#tabs-switcher`, `.tabs-panel`, `#tabs-actions`, `#tabs-dyn-label` |
| `masterdetail` | `master_detail/` | `screen.py` | — | `#md-body`, `#md-master`, `#md-master-title`, `#md-master-table`, `#md-detail`, `#md-detail-header`, `#md-detail-table` |
| `masterdetailvertical` | `master_detail_vertical/` | `screen.py` | — | `#mdv-body`, `#mdv-master`, `#mdv-master-title`, `#mdv-master-table`, `#mdv-detail`, `#mdv-detail-header`, `#mdv-detail-table` |
| `formtable` | `form_table/` | `screen.py` | — | `#ft-body`, `#ft-form`, `#ft-form-title`, `.ft-section`, `.ft-row`, `.ft-field`, `.ft-field-full`, `.ft-field-toggles`, `.ft-toggle-row`, `.ft-toggle-label`, `.ft-id`, `#ft-form-actions`, `#ft-status-msg`, `#ft-table-area`, `#ft-table-hint`, `#ft-table` |
| `labelform` | `label_form/` | `screen.py` | — | `#lf-body`, `#lf-form`, `#lf-title`, `.lf-section`, `.lf-row`, `.lf-label`, `.lf-toggle-row`, `#lf-actions`, `#lf-msg` |
| `cards` | `cards/` | `screen.py` | — | `#crd-body`, `.crd-section`, `.crd-row`, `.crd-row > *` |
| `cards2` | `cards2/` | `screen.py` | — | `#cd2-body`, `.cd2-section`, `.cd2-row`, `.cd2-row > *` |
| `dicomnrrd` | `dicom_nrrd/` | `screen.py` | — | `#dn-body`, `.dn-section`, `.dn-row`, `.dn-row > *` |
| `customwidget` | `custom_widget/` | `screen.py` | — | `#custom-body`, `#metric-row`, `#badge-row` |
| `cmdpalette` | `command_palette/` | `screen.py` | `modal.py` → `CommandPaletteModal` | `#cp-modal-body`, `#cp-list`, `#cp-hint`, `CommandPaletteModal` |
| `contextmenu` | `context_menu/` | `screen.py` | `modal.py` → `ContextMenuModal` | `#ctx-modal-body`, `#ctx-title`, `#ctx-list`, `#ctx-hint`, `ContextMenuModal` |
| `helpkeys` | `help_keys/` | `screen.py` | `modal.py` → `HelpModal` | `#help-modal-body`, `#help-modal-title`, `#help-table`, `#hk-body`, `#hk-preview` |
| `searchgrid` | `search_grid/` | `screen.py` + `edit.py` | `edit.py` → `EditJobScreen` | `#sg-*`, `#ej-*`, `Label.field-error-label`, `Input.field-error`, `#ej-errors`, `#ej-error-list`, `ConfirmModal` |
| `gallery` | `gallery/` | `screen.py` | — | `#gallery-body`, `#gallery-list`, `#gallery-detail`, `#gallery-title`, `#gallery-hint`, `#gallery-desc` |
| `dashboard` | `dashboard/` | `screen.py` + `detail.py` | `detail.py` → `DetailScreen` | `#sidebar`, `#main`, `.panel-title`, `#detail-body`, `.detail-field` |

> **Notes on complex cases:**
> - `search_grid`: `EditJobScreen` is in the same file as `SearchGridDemoScreen` today. Split into `screen.py` (list/filter) and `edit.py` (edit form). `SearchGridDemoScreen` imports `EditJobScreen` from `edit.py`. `routes.py` registers only `searchgrid` → `screen.py:SearchGridDemoScreen`.
> - `command_palette`, `context_menu`, `help_keys`: modal class moves to `modal.py` in the same feature folder; the screen file imports it from there.
> - `dashboard`: `DetailScreen` in `detail.py` is never routed to directly — it is always pushed by `DashboardScreen`. No route registration needed for `detail`.
> - `confirm_modal` (used in `search_grid`): currently defined inline in `demo_search_grid.py`. Extract to `search_grid/modal.py`.

### Updating `routes.py` after each feature is migrated

When `screens/demo_inputs.py` moves to `features/inputs/screen.py`, update the corresponding line:
```python
# Before
register("inputs", "your_cli.tui.screens.demo_inputs", "InputsDemoScreen")

# After
register("inputs", "your_cli.tui.features.inputs.screen", "InputsDemoScreen")
```

The rest of the app does not change. This is the router's key benefit.

---

## Phase 4 — CSS cleanup (do alongside Phase 3)

As each feature is migrated and its CSS is moved to `features/<name>/styles.tcss`, the corresponding blocks are cut from `tui/styles.tcss`.

### What stays in `tui/styles.tcss` after all migrations

Only rules that are either framework overrides or used by three or more features:

```css
/* tui/styles.tcss — global only after refactor */

Screen  { layout: vertical; background: $background; }

Switch.-on              { background: $primary; }
Switch.-on > .switch--slider { color: $primary-lighten-3; }

DataTable { height: 1fr; }
Log       { height: 1fr; }

/* shared utilities — used by multiple features */
.demo-label  { margin-top: 2; margin-bottom: 1; color: $accent; }
.demo-row    { height: auto; margin-bottom: 1; align: left middle; }
.panel-title { margin-bottom: 1; color: $accent; }

/* field validation — shared by form_validation and search_grid */
Label.field-error-label { color: $error; text-style: bold; }
Input.field-error       { background: $error 15%; }
```

Everything else lives in the owning feature's `styles.tcss`.

> **Rule of thumb:** if a CSS selector is referenced by only one `Screen` subclass, it belongs in that screen's `styles.tcss`. If it is referenced by two or more unrelated screens, it stays in the global file.

---

## 5. Files to delete after all migrations are complete

Once every screen has been migrated to `features/` and verified:

```
src/your_cli/tui/screens/   ← delete entire directory
```

This directory will be empty after Phase 3 (all 44 screen files moved + `__init__.py`). The `dashboard.py` and `detail.py` top-level files also move to `features/dashboard/`.

---

## 6. Final verification checklist

Run after every phase, and again after the last cleanup:

```bash
# Lint and type check
ruff check src/
mypy src/

# Import smoke test — exercises the lazy loader for every registered route
python - <<'EOF'
import importlib
import your_cli.tui.routes
from your_cli.tui.router import _REGISTRY
for key, (mod, cls) in _REGISTRY.items():
    m = importlib.import_module(mod)
    assert hasattr(m, cls), f"Missing: {mod}.{cls}"
    print(f"  ok  {key:24s}  {mod}.{cls}")
print(f"\n{len(_REGISTRY)} routes verified.")
EOF

# Full test suite
pytest

# Manual — open every gallery item and verify rendering
your-cli
```

---

## 7. Commit strategy

Each phase should be one pull request. Within Phase 3, commit one feature folder at a time so bisect is easy if a CSS split causes a regression:

```
feat: extract widget library to tui/widgets/           ← Phase 1
feat: add lazy router and routes registry              ← Phase 2
feat: migrate gallery feature to features/gallery/     ← Phase 3, commit 1
feat: migrate dashboard feature to features/dashboard/ ← Phase 3, commit 2
...                                                     ← one commit per feature
chore: delete empty screens/ directory                 ← final cleanup
```

---

## 8. Estimated effort

| Phase | Files touched | Estimated time |
|-------|--------------|----------------|
| 1 — Widget library | ~16 new, 3 modified | 2 h |
| 2 — Router | 2 new, 2 modified | 1 h |
| 3+4 — Feature migration (44 × ~15 min each) | ~90 new, 44 deleted | 11 h |
| Cleanup + final verification | — | 1 h |
| **Total** | | **~15 h** |

Phases 1 and 2 together take ~3 hours and deliver most of the architectural value (DRY widget library + decoupled router) before any file is moved.

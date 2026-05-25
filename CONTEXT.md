# textual-app

A Textual TUI for the AIQ platform. The app has two surfaces: an **operational dashboard** showing live work items, and a **widget gallery** of 44 interactive demos covering Textual patterns.

## Language

### Work item domain

**Work item**:
An AI platform job submitted by a tenant — one of training, validation, export, inference, or preprocessing. Identified by a sequential ID (`wi-NNN`). Carries a status, priority, type, environment, and submitter.
_Avoid_: Job, task, record (too generic)

**Tenant**:
The organisation that owns a work item — JHU, UNC, Mayo, or Stanford. Stored as a lowercase string key (`"jhu"`, `"unc"`, `"mayo"`, `"stanford"`).
_Avoid_: User, organisation, customer

**Status**:
A work item's lifecycle state — one of `queued`, `running`, `done`, `failed`, or `pending`. Displayed using colour from `palette.STATUS_COLORS`.
_Avoid_: State, phase

**Priority**:
The urgency of a work item — one of `low`, `medium`, `high`, or `critical`. Displayed using colour from `palette.PRI_COLORS`.
_Avoid_: Severity, urgency

**Environment**:
The deployment target for a work item — one of `prod`, `staging`, or `dev`.
_Avoid_: Stage, tier

### TUI navigation concepts

**Gallery**:
The top-level navigation hub (`GalleryScreen`). Lists every demo by display name and description; Enter opens one. The first screen shown after startup.
_Avoid_: Menu, home screen, launcher

**Demo**:
One of the 44 interactive feature screens reachable from the gallery. Each demo teaches a specific Textual widget or interaction pattern. Registered in `routes.py` and listed in `GalleryScreen.DEMOS`.
_Avoid_: Example, sample, screen (too broad)

**Route key**:
The short string identifier (e.g. `"searchgrid"`, `"pagination"`) used to address a screen via `navigate()`. Every gallery-reachable screen has exactly one route key, defined in `routes.py`.
_Avoid_: URL, path, slug

**Navigate** (verb):
Push a screen by route key via `router.navigate(app, key)`. The correct path for all gallery-reachable screens. Contrast with **push directly**.
_Avoid_: Route to, open, launch

**Push directly**:
Push a data-bound child screen via `app.push_screen(ScreenClass(args))`, bypassing the router. Used when a screen requires constructor arguments (`EditJobScreen(record_id)`, `DetailScreen(item)`). See ADR-0001.
_Avoid_: Navigate (reserved for the router path)

**Feature screen**:
Any screen that subclasses `FeatureScreen` (`tui/feature_screen.py`). All demos, the dashboard, and its child screens inherit from it. Provides the Escape → Back binding and `action_go_back()`.
_Avoid_: Screen (too broad), component

### Shared infrastructure

**Palette**:
The canonical source of status and priority colour maps (`tui/palette.py`). All screens must import from here — no local `_STATUS_COLORS` or `_PRI_COLORS` definitions.
_Avoid_: Theme colours, colour constants

**Paginator**:
The shared page-state dataclass (`tui/paginator.py`). Owns page arithmetic, navigation (first/prev/next/last), and slice computation. Screens hold a `Paginator` instance; they must call `_render_page()` or `_load_page()` after any navigation call returns `True`.
_Avoid_: Pager, page state

## Flagged ambiguities

**Screen vs Demo**: "Screen" is the Textual base class; "demo" is the project-specific term for a gallery-reachable feature screen. Not every screen is a demo (`DetailScreen`, `EditJobScreen` are not).

**Navigate vs push directly**: Both put a screen on the stack, but only `navigate()` goes through the route registry. Data-bound child screens always use `push_screen()` directly. Using "navigate" for `push_screen()` calls obscures the distinction — be precise.

## Example dialogue

> **Dev:** We need a new demo that shows a filterable list of work items by tenant. Where do we start?
>
> **Domain expert:** It's a new **demo**, so it gets its own feature package under `features/`. Give it a **route key** — say `"tenantlist"` — and add a `register()` call in `routes.py` with `display_name=` and `description=`. That's the only file to edit — the gallery reads its list from the route registry at startup. Use the work item seed data in `search_grid/_data.py` for the records.
>
> **Dev:** The list will need pagination. Do I write the slice logic myself?
>
> **Domain expert:** No — use the **Paginator**. Construct it with `total=len(records)` and your `page_size`. After every navigation call (`pager.next()`, `pager.first()`, etc.) that returns `True`, call your render method. Use `pager.slice()` to get the indices.
>
> **Dev:** And when a user selects a tenant row, do we navigate to a detail screen?
>
> **Domain expert:** If the detail screen needs the tenant record to render, that's a **push directly** — `app.push_screen(TenantDetailScreen(tenant_id))`. Don't route it; don't put it in `routes.py`. See ADR-0001.
>
> **Dev:** The status column — I should pick colours from the screen's own dict?
>
> **Domain expert:** No — import `STATUS_COLORS` from the **palette**. No local colour maps.

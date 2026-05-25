# textual-app

A Textual TUI for the AIQ platform. The app has two surfaces: an **operational dashboard** showing live work items, and a **widget gallery** of 44 interactive demos covering Textual patterns.

## Language

### Work item domain

**Work item**:
An AI platform job submitted by a tenant — one of training, validation, export, inference, or preprocessing. Identified by a sequential ID (`wi-NNN`). Carries a status, priority, type, environment, and submitter. Always belongs to exactly one Run (`run_id` is a non-nullable foreign key — work items never exist outside a Run). The `tenant` field is a plain string key (e.g. `"jhu"`), not a reference to a Tenant object. Status is the only field the user can mutate via the TUI; valid transitions are whitelisted (see **Stage retry**).
_Avoid_: Job, task, record (too generic)

**Stage retry**:
Retrying a single failed pipeline stage by transitioning its work item's status from `failed` back to `queued`. Operates within the existing Run — no new entity is created. Valid TUI status transitions are: `queued → failed` (cancel), `running → failed` (abort), `failed → queued` (retry), `pending → queued` (unblock). Transitioning a `done` work item to any other status is not permitted in the TUI. Contrast with **Run rerun**.
_Avoid_: Rerun (reserved for Run-level rerun), retry (too generic — use "stage retry")

**Run rerun**:
Retrying an entire failed Run by creating a new Run with `parent_run_id` pointing to the original. All pipeline stages are re-submitted in the new Run. Contrast with **Stage retry**, which retries a single stage within the existing Run without creating a new entity. See ADR-0002.
_Avoid_: Retry (too generic — use "run rerun")

**Tenant**:
The organisation that owns a Run and its work items — JHU, UNC, Mayo, or Stanford. Stored as a lowercase string key (`"jhu"`, `"unc"`, `"mayo"`, `"stanford"`). Referenced by string key on WorkItem and Run; never inflated into a nested object.
_Avoid_: User, organisation, customer

**Run**:
A single submission of work by a tenant — an independently addressable record that owns one or more work items. Identified by a `run_id` that is globally unique across all tenants (so the repository's internal cache uses `run_id` as a flat dict key). However, the API requires `tenant` as a routing parameter on every call (used to select the correct tenant database shard), so all repository fetch methods accept both `tenant` and `run_id`. Carries its own metadata: `tenant` (string key), `submitted_at`, and a `status` that is stored explicitly by the API (not derived from work item statuses on the client). Once a Run reaches a terminal status (`done` or `failed`) it is immutable; rerunning creates a new Run with a `parent_run_id` pointing to the original. Read-only from the TUI — the repository has no write path for Runs. See ADR-0002.
_Avoid_: Job batch, submission, execution

**Status**:
A work item's lifecycle state — one of `queued`, `running`, `done`, `failed`, or `pending`. Displayed using colour from `palette.STATUS_COLORS`.
_Avoid_: State, phase

**Priority**:
The urgency of a work item — one of `low`, `medium`, `high`, or `critical`. Displayed using colour from `palette.PRI_COLORS`.
_Avoid_: Severity, urgency

**Environment**:
The deployment target for a work item — one of `prod`, `staging`, or `dev`.
_Avoid_: Stage, tier

**Run dashboard**:
The multi-tenant overview screen — shows a small, bounded number of recent Runs for every tenant simultaneously (e.g. last 5 per tenant). The repository fetches each tenant's recent Runs in parallel via `get_recent_runs(tenant, limit=N)`; no server-side cursor is needed. Refreshes automatically on a fixed interval: the screen owns the polling lifecycle (starts `set_interval` on mount, cancels on pop); the repository is a passive data source and does not push notifications.
_Avoid_: Dashboard (too generic — use "run dashboard" to distinguish from the work-item dashboard)

**Run history screen**:
The single-tenant Run browse screen — defaults to today's Runs for the selected tenant, supports date-range search for historical data. Uses server-side pagination via `get_runs(tenant, date_from, date_to, page, page_size)`; the screen drives the cursor forward and backward. Load-and-search only — no live polling. The user issues a query and pages through results; a manual refresh is available if fresh data is needed.
_Avoid_: Run list, run search

### TUI navigation concepts

**Gallery**:
The top-level navigation hub (`GalleryScreen`). Lists every demo by display name and description; Enter opens one. The first screen shown after startup.
_Avoid_: Menu, home screen, launcher

**Demo**:
One of the 44 interactive feature screens reachable from the gallery. Each demo teaches a specific Textual widget or interaction pattern. Registered in `routes.py` with a `display_name` and `description`; the gallery reads the list from the route registry at startup.
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

### Operational data layer

**Repository**:
The single object through which all reads and writes for Runs and work items flow (`tui/repository.py`). Uses two distinct fetch strategies: Run listings use server-side pagination (the repository fetches one page at a time; the total Run population across a tenant's history is too large to hold in memory), while work items within a single Run are fetched in full (bounded at ~few hundred, safe for client-side pagination). Exposes a `get_run_with_items(tenant, run_id)` method that fetches a single Run's metadata and work items concurrently. Individual Run records fetched by `run_id` are cached by the repository; terminal Runs are cached indefinitely (immutable). Lives on the `App` instance; screens access it via `self.app.repository`. Demo screens do not use it — they hold their own self-contained seed data.
_Avoid_: Store, cache, service, data layer

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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A Textual TUI for the AIQ platform. The app opens a **Widget Gallery** — 49 runnable demos covering nearly every Textual widget and pattern — plus the main work-items dashboard.

---

## Commands

```bash
# Environment setup (Conda)
conda env create -f environment.yml          # First time
conda env update -f environment.yml --prune  # Update deps

# Run the app
your-cli                                     # Launch TUI
textual run --dev src/your_cli/__main__.py   # Hot-reload dev mode (run textual console in a second terminal)

# Lint / type-check / test
ruff check .                                 # Linter (100-char line limit, py312)
mypy src                                     # Type checking (strict; generated client excluded)
pytest                                       # Run tests

# Regenerate API client (do not hand-edit src/your_cli/client/)
./scripts/regen-client.sh
```

---

## Architecture

**Entry flow:** `your-cli` CLI (Typer) → `src/your_cli/cli.py::run()` → loads Pydantic `Settings` → instantiates `YourCliApp` → `navigate(self, "gallery")`.

### Source layout

**CLI / config**
- `src/your_cli/cli.py` — CLI entry point; `login`/`logout` subcommands
- `src/your_cli/config.py` — Pydantic `Settings`; env prefix `AIQ_`, optional `.env` via `--config`

**App core**
- `src/your_cli/tui/app.py` — Root `YourCliApp`; registers 7 themes on mount; holds `self.repository`; global bindings `q` (quit), `d` (dark toggle)
- `src/your_cli/tui/themes.py` — 7 themes: AIQ, AIQ_DARK, Nord, Gruvbox, Dracula, Solarized Light, Warm Linen
- `src/your_cli/tui/styles.tcss` — Global CSS only: `Screen`, `Switch`, shared `.demo-label`/`.demo-row` utilities, form-validation helpers

**Routing**
- `src/your_cli/tui/router.py` — `navigate(app, key)` lazy-loads the screen module via `importlib` and calls `app.push_screen()`
- `src/your_cli/tui/routes.py` — **Single source of truth** for all routes: 50 `register()` calls (1 hub + 49 gallery demos); edit only this file to add, rename, or remove a screen

**Shared utilities**
- `src/your_cli/tui/feature_screen.py` — `FeatureScreen(Screen[None])` base class; provides `Escape → go_back` binding for all demo screens
- `src/your_cli/tui/paginator.py` — Pure-Python `Paginator` dataclass with `slice()`, `next()`, `prev()`, `first()`, `last()`, `at_first`, `at_last`
- `src/your_cli/tui/palette.py` — `STATUS_COLORS`, `PRI_COLORS`, `STEP_STATUS_COLORS` — import these instead of redeclaring per-screen

**Data layer**
- `src/your_cli/tui/models.py` — Frozen dataclasses: `Run` (run_id, tenant, status, submitted_at, parent_run_id) and `WorkItem` (id, run_id, tenant, type, status, priority, environment, submitted_by, tags)
- `src/your_cli/tui/fake_api.py` — `FakeApiClient`: 160 deterministically-generated Runs across 4 tenants; satisfies `ApiClient` Protocol; 50 ms simulated latency on all methods
- `src/your_cli/tui/repository.py` — `Repository`: caching gateway over `ApiClient`; terminal Runs and their work items cached indefinitely; `get_run_with_items()` fetches both concurrently via `asyncio.gather()`; validates status transitions against `_VALID_TRANSITIONS` whitelist before writing

**Widgets**
- `src/your_cli/tui/widgets/` — 13 reusable widgets; import with `from your_cli.tui.widgets import <Name>`:
  - **10 card types**: `AlertCard`, `ProfileCard`, `ProgressCard`, `ActionCard`, `KVCard`, `TimelineCard`, `PricingCard`, `SparklineCard`, `ActivityCard`, `ComparisonCard`
  - **Standalone**: `MetricCard`, `StatusBadge`, `PaginationBar`

**Feature packages**
- `src/your_cli/tui/features/` — 50 packages, one per screen (or screen group); each has `__init__.py`, `screen.py`, `styles.tcss`
  - `features/gallery/` — navigation hub (`GalleryScreen`)
  - `features/dashboard/` — two-pane work-items dashboard; `detail.py` contains `DetailScreen` (child screen, not in router)
  - `features/search_grid/` — most complete demo; also has `edit.py` (child screen) and `_data.py` (seed data)
  - `features/work_item_cards/` — card grid demo; `detail.py` contains `WorkItemDetailScreen` (child screen)
  - `features/large_dataset/` — 5 000-row DataTable demo; `_data.py` generates seed rows
  - `features/<name>/` — all other demos: one package, one screen

**Auto-generated (do not edit)**
- `src/your_cli/client/` — OpenAPI-generated API client; regenerate with `./scripts/regen-client.sh`

### Data layer details

`YourCliApp.repository` is a `Repository(FakeApiClient())` instance, accessible from any screen as `self.app.repository`. Swap `FakeApiClient` for the real generated client in `app.py` when the API is ready.

Status transitions enforced by `Repository.update_work_item_status()`:

| From | Allowed next |
|------|-------------|
| queued | failed |
| running | failed |
| failed | queued *(stage retry)* |
| pending | queued |
| done | — *(immutable)* |

### Screen navigation

`navigate(app, key)` in `router.py` lazy-imports the target module on first use and calls `app.push_screen()`. Escape calls `app.pop_screen()` via `action_go_back()` in each screen (inherited from `FeatureScreen`). `GalleryScreen` is the hub: its `ListView.Selected` handler calls `navigate(self.app, key)`.

**Child screens** (e.g. `DetailScreen`, `WorkItemDetailScreen`, `EditJobScreen`) are pushed directly via `self.app.push_screen(ChildScreen(data))` — they are not registered in `routes.py` (see ADR-0001).

### Reference demos

| Goal | Look at |
|------|---------|
| Most complete pattern reference | `features/search_grid/screen.py` — filter bar + pageable DataTable + sort + full edit form |
| Server-side pagination via Repository | `features/run_history/screen.py` |
| Multi-tenant live polling | `features/run_dashboard/screen.py` |
| Large DataTable (virtual scroll, `move_cursor`) | `features/large_dataset/screen.py` |
| Typed modal dialogs | `features/modal_dialogs/modals.py` |
| Async workers (`@work`) | `features/workers/screen.py` |
| Reactive attributes (`reactive`, `watch_`) | `features/reactives/screen.py` |

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

Two touch-points only:

**1. Create the feature package** at `src/your_cli/tui/features/<key>/`:

```
__init__.py   →  one line: """Feature package."""
screen.py     →  FeatureScreen subclass (see below)
styles.tcss   →  feature-scoped CSS (can be empty)
```

Minimal `screen.py`:
```python
from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Footer, Header, Static
from your_cli.tui.feature_screen import FeatureScreen  # provides Escape → go_back

class MyDemoScreen(FeatureScreen):
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Hello")
        yield Footer()
```

**2. Register the route** in `routes.py` at the position where it should appear in the gallery:

```python
register("<key>",
         "your_cli.tui.features.<key>.screen", "MyDemoScreen",
         display_name="Human-readable Name",
         description="One-line description shown in the gallery detail pane")
```

No other files need to change — `GalleryScreen` reads the registry at instantiation time.

**Non-gallery screens** pushed directly via `app.push_screen()` (child/detail screens) do not go in `routes.py` at all. See ADR-0001.

---

## Architectural decisions

| ADR | Decision |
|-----|----------|
| [ADR-0001](docs/adr/0001-parameterised-child-screens-bypass-router.md) | Child screens that receive runtime data are instantiated and pushed directly; they are not registered in the router |
| [ADR-0002](docs/adr/0002-reruns-create-new-run.md) | Run-level rerun creates a new `Run` with `parent_run_id`; stage retry (failed→queued within the same Run) is a distinct concept |

---

## Windows requirement

Requires **Windows Terminal** (default on Windows 11). Legacy `cmd.exe` and PowerShell 5.1 in `conhost` are not supported.

---

## Textual-specific rules

Hard-won lessons specific to **Textual 8.x** are maintained in a dedicated reference document. **Read this before writing any new screen or widget code.**

@docs/textual-rules.md

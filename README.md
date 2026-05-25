# your-cli

A Textual TUI for the AIQ platform, built on [Textual](https://github.com/Textualize/textual) ≥ 8.2.7 / Python 3.12.

The app launches a **Widget Gallery** — 49 runnable demos covering nearly every Textual widget and pattern, plus the main AIQ work-items dashboard.

---

## Quick start (conda)

```bash
conda env create -f environment.yml
conda activate your-cli
your-cli
```

The `pip install -e .[dev]` step happens automatically via the `pip:` block in `environment.yml`, so editing source files takes effect on the next `your-cli` run with no reinstall.

## Updating dependencies

After changing `pyproject.toml`:

```bash
conda env update -f environment.yml --prune
```

---

## Running the app

```bash
your-cli                            # launches the TUI (Widget Gallery)
your-cli --help                     # full CLI help
your-cli --version
your-cli login --tenant <tenant-id> # scriptable subcommand
your-cli logout
```

Equivalently, during development:

```bash
python -m your_cli
```

---

## Widget gallery

The gallery opens on launch. Select any item and press **Enter** to open that demo. Press **Escape** to return. Use **[** / **]** to resize the sidebar.

| Demo | Key widgets / patterns |
|------|------------------------|
| Inputs & Forms | `Input`, `TextArea`, `Checkbox`, `Switch`, `Select`, `RadioSet`, `Button` |
| Layout & Navigation | Grid layout, `Collapsible`, `Tree` |
| Progress & Feedback | `ProgressBar`, `Digits`, `Sparkline`, `LoadingIndicator`, toast, modal |
| Work Items Dashboard | Two-pane dashboard with row drill-down |
| File Manager | `DirectoryTree` with file content preview |
| API File Browser | Tree populated from API calls with lazy loading |
| Live Dashboard | `DataTable` auto-refreshing every 10 s via `set_interval` |
| Command Palette | Fuzzy-search overlay — **Ctrl+P** |
| Streaming Log | `RichLog` fed by an async worker |
| Multi-step Wizard | Step-by-step form with Back / Next / Submit and a review pane |
| Markdown Report | Report viewer with tables, code blocks, callouts |
| Settings Screen | Category sidebar with forms |
| Concurrent Workers | Multiple `@work` tasks with individual progress bars |
| Context Menu | `ModalScreen` action menu on row **Enter** |
| Inline Edit | Press **E** on a row to edit its fields in a panel below the table |
| Theme Toggle | Dark / light mode switch with `app.dark` |
| Custom Widgets | `MetricCard` and `StatusBadge` with reactive `render()` |
| Form Validation | Inline field errors with live re-validation after first submit |
| Pagination | 100 items in fixed-size pages, keyboard + button nav |
| Multi-select Table | **Space** to toggle rows, **A**/**D** for all/none, bulk actions |
| Content Switcher | `ListView` driving `ContentSwitcher` without new screens |
| Help / Key Reference | Press **?** to open a modal listing every active binding |
| OptionList | Separators, highlight events, selected-action feedback |
| Masked Input | Date, time, phone, job-ID, IPv4, hex-colour templates |
| Notification Drawer | `notify()` calls accumulated in a slide-in history panel |
| Autocomplete Input | `SuggestFromList` — **→** accepts inline suggestion |
| SelectionList | Checkbox-style multi-select with `.selected` |
| Toggle Button | `Checkbox` and `RadioButton` as standalone toggles |
| Rule | Horizontal and vertical dividers in every line style |
| Tooltip | `widget.tooltip` — hover any widget |
| Pretty | Syntax-highlighted Python object display |
| Link | Clickable links opening URLs via `app.open_url()` |
| Log vs RichLog | Plain `Log` vs `RichLog` side by side |
| Tabs (standalone) | `Tabs` + `ContentSwitcher` with dynamic add/remove at runtime |
| Master / Detail | Master `DataTable` populates a child step table in real time |
| Form + Table | Row selection populates an edit form above |
| Label Form | Single-column form — label left, input right |
| Search → Grid → Edit | Filter bar → pageable grid → full edit screen |
| Card Patterns | `AlertCard`, `ProfileCard`, `ProgressCard`, `ActionCard`, `KVCard` |
| Card Patterns II | `TimelineCard`, `PricingCard`, `SparklineCard`, `ActivityCard`, `ComparisonCard` |
| Modal Dialogs | Alert, Confirm, Input, Selection, Form, and Progress modals with typed return values |
| Work Item Cards | Status-coloured card grid — click or Enter to drill into detail |
| DICOM → NRRD | Batch conversion dashboard — progress, metadata, validation alerts, activity log |
| Clipboard Copy | `app.copy_to_clipboard()` — plain text, commands, JSON, and CSV with toast feedback |
| Run History Browser | Paginated run list with date-range filter and tenant selector |
| Reactive Attributes | `reactive` + `watch_` patterns: counter, RGB mixer, Input→reactive→fan-out |
| Large Dataset | 5 000-row `DataTable` with virtual scrolling, column sort, `move_cursor()`, jump-to-row |
| Reorder List | **Alt+↑/↓** keyboard reordering of a `ListView` — no native drag needed |
| Run Dashboard | Multi-tenant 2×2 grid: `asyncio.gather()` + `Repository` + live polling |

### Search → Grid → Edit highlights

The most feature-rich demo (`searchgrid`) includes:

- Full-text + multi-select filter bar with live results
- Pageable `DataTable` with configurable page size (10 / 20 / 50 / 100)
- **Clickable column headers** — 3-state sort (ascending ▲ → descending ▼ → off)
- **Zebra striping** and **auto-height rows** (long cells wrap to a second line)
- Record count in the pagination bar
- Push-screen edit form with live validation, Select error highlighting, and an error summary panel
- **Ctrl+S** to save; **Escape** to cancel; cursor restored to the last-edited row on return

---

## Configuration

Settings are loaded in this order (highest priority first):

1. CLI flags (e.g. `--api-base-url`)
2. Environment variables prefixed with `AIQ_` (e.g. `AIQ_API_BASE_URL`)
3. A `.env`-style file passed via `--config path/to/.env`
4. Defaults in `src/your_cli/config.py`

Example `.env`:

```
AIQ_API_BASE_URL=https://api.aiq.example.com
AIQ_TENANT_ID=00000000-0000-0000-0000-000000000000
AIQ_CLIENT_ID=00000000-0000-0000-0000-000000000000
```

---

## Regenerating the OpenAPI client

Drop your spec into `api/openapi.yaml`, then:

```bash
./scripts/regen-client.sh
```

The generated client lands in `src/your_cli/client/` and is import-time available as `your_cli.client`. Do not hand-edit files there.

---

## Project layout

```
your-cli/
├── pyproject.toml               # package metadata, dependencies, entry point
├── environment.yml              # conda env (delegates pip install to pyproject)
├── CLAUDE.md                    # development rules and architecture reference
├── api/openapi.yaml             # OpenAPI spec (source of truth for the client)
├── scripts/regen-client.sh      # regenerates src/your_cli/client/
├── docs/
│   ├── textual-rules.md         # hard-won Textual 8.x lessons (read before writing screens)
│   └── adr/                     # architecture decision records
│       ├── 0001-parameterised-child-screens-bypass-router.md
│       └── 0002-reruns-create-new-run.md
└── src/your_cli/
    ├── __init__.py
    ├── __main__.py              # enables `python -m your_cli`
    ├── cli.py                   # Typer entry point (`your-cli` command)
    ├── config.py                # Pydantic Settings (env prefix AIQ_)
    ├── client/                  # generated OpenAPI client (do not edit)
    └── tui/
        ├── app.py               # root YourCliApp — registers 7 themes, holds repository
        ├── themes.py            # 7 themes: AIQ, AIQ Dark, Nord, Gruvbox, Dracula, Solarized Light, Warm Linen
        ├── styles.tcss          # global CSS: Screen, Switch, shared .demo-* utilities
        ├── routes.py            # single source of truth — 50 register() calls (1 hub + 49 demos)
        ├── router.py            # navigate(app, key) — lazy-imports and push_screen
        ├── feature_screen.py    # FeatureScreen base class — provides Escape → go_back
        ├── paginator.py         # Paginator dataclass with slice/next/prev/first/last
        ├── palette.py           # STATUS_COLORS, PRI_COLORS, STEP_STATUS_COLORS
        ├── models.py            # frozen dataclasses: Run, WorkItem
        ├── fake_api.py          # FakeApiClient — 160 deterministic runs, 50 ms latency
        ├── repository.py        # Repository — caching gateway over ApiClient
        ├── widgets/             # 13 reusable widgets
        │   ├── metric.py        # MetricCard
        │   ├── status_badge.py  # StatusBadge
        │   ├── pagination_bar.py # PaginationBar (posts Navigated messages)
        │   ├── field_validator.py
        │   └── cards/           # 10 card types
        │       ├── alert.py     # AlertCard
        │       ├── profile.py   # ProfileCard
        │       ├── progress.py  # ProgressCard
        │       ├── action.py    # ActionCard
        │       ├── kv.py        # KVCard
        │       ├── timeline.py  # TimelineCard
        │       ├── pricing.py   # PricingCard
        │       ├── sparkline.py # SparklineCard
        │       ├── activity.py  # ActivityCard
        │       └── comparison.py # ComparisonCard
        └── features/            # 50 packages — one per screen (or screen group)
            ├── gallery/         # navigation hub (GalleryScreen)
            ├── dashboard/       # two-pane dashboard; detail.py = child screen
            ├── search_grid/     # most complete demo; edit.py + _data.py
            ├── work_item_cards/ # card grid; detail.py = child screen
            ├── modal_dialogs/   # typed modals; modals.py contains all ModalScreen subclasses
            ├── large_dataset/   # 5 000-row DataTable; _data.py generates seed rows
            └── <43 other packages, one per demo>
```

---

## Windows notes

The TUI requires a modern terminal. **Windows Terminal** (default on Windows 11, free install on Windows 10) renders everything correctly including mouse support. Legacy `cmd.exe` and old PowerShell 5.1 in `conhost` are not supported.

---

## Linting and tests

```bash
ruff check .
mypy src
pytest
```

---

## Textual developer tools

The `textual-dev` package (pulled in via the `dev` extra) provides:

```bash
textual console      # live log viewer; run in a second terminal
textual run --dev src/your_cli/__main__.py   # hot-reload mode
```

These are invaluable when iterating on screens and widgets.

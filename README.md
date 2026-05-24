# your-cli

A Textual TUI for the AIQ platform, built on [Textual](https://github.com/Textualize/textual) ≥ 8.2.7 / Python 3.12.

The app launches a **Widget Gallery** — 44 runnable demos covering nearly every Textual widget and pattern, plus the main AIQ work-items dashboard.

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
| Data Display | `DataTable`, `RichLog`, `Markdown` across three tabs |
| Layout & Navigation | Grid layout, `Collapsible`, `Tree` |
| Progress & Feedback | `ProgressBar`, `Digits`, `Sparkline`, `LoadingIndicator`, toast, modal |
| Work Items Dashboard | Two-pane dashboard with row drill-down |
| File Manager | `DirectoryTree` with file content preview |
| API File Browser | Tree populated from API calls with lazy loading |
| Live Dashboard | `DataTable` auto-refreshing every 10 s via `set_interval` |
| Command Palette | Fuzzy-search overlay — Ctrl+P |
| Streaming Log | `RichLog` fed by an async worker |
| Multi-step Wizard | Step-by-step form with Back / Next / Submit |
| Markdown Report | Report viewer with tables, code blocks, callouts |
| Search & Filter | Live `Input` filtering a `DataTable` |
| Settings Screen | Category sidebar with forms |
| Concurrent Workers | Multiple `@work` tasks with individual progress bars |
| Context Menu | `ModalScreen` action menu on row Enter |
| Inline Edit | Row edit panel below the table |
| Theme Toggle | Dark / light mode switch with `app.dark` |
| Custom Widgets | `MetricCard` and `StatusBadge` with reactive `render()` |
| Form Validation | Inline field errors with live re-validation |
| Pagination | 100 items in fixed-size pages, keyboard + button nav |
| Multi-select Table | Space to toggle rows, bulk actions |
| Content Switcher | `ListView` driving `ContentSwitcher` without new screens |
| Help / Key Reference | Modal listing every active binding — press **?** |
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
| Tabs (standalone) | `Tabs` + `ContentSwitcher` with dynamic add/remove |
| Master / Detail | Master `DataTable` populates a child table |
| Master / Detail (vertical) | Same pattern, stacked vertically |
| Form + Table | Row selection populates an edit form above |
| Label Form | Single-column form — label left, input right |
| Search → Grid → Edit | Filter bar → pageable grid → full edit screen |
| Card Patterns | `AlertCard`, `ProfileCard`, `ProgressCard`, `ActionCard`, `KVCard` — all via `compose()` |
| Card Patterns II | `TimelineCard`, `PricingCard`, `SparklineCard`, `ActivityCard`, `ComparisonCard` |
| DICOM → NRRD | Batch conversion dashboard — progress, volume metadata, validation alerts, activity log |

### Search → Grid → Edit highlights

The most feature-rich demo (`searchgrid`) includes:

- Full-text + multi-select filter bar with live results
- Pageable `DataTable` with configurable page size (10 / 20 / 50 / 100)
- **Clickable column headers** — 3-state sort (ascending ▲ → descending ▼ → off)
- **Zebra striping** and **auto-height rows** (long cells wrap to a second line)
- Record count in the pagination bar
- Push-screen edit form with live validation, Select error highlighting, and an error summary panel
- Ctrl+S to save; Escape to cancel; cursor restored to the last-edited row on return

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
├── CLAUDE.md                    # development rules and hard-won Textual lessons
├── api/openapi.yaml             # OpenAPI spec (source of truth for the client)
├── scripts/regen-client.sh      # regenerates src/your_cli/client/
└── src/your_cli/
    ├── __init__.py
    ├── __main__.py              # enables `python -m your_cli`
    ├── cli.py                   # Typer entry point (`your-cli` command)
    ├── config.py                # Pydantic Settings
    ├── client/                  # generated OpenAPI client (do not edit)
    └── tui/
        ├── app.py               # root Textual App (registers themes, opens Gallery)
        ├── themes.py            # custom Textual themes
        ├── styles.tcss          # global Textual CSS for all screens
        └── screens/
            ├── gallery.py             # widget gallery navigation hub
            ├── dashboard.py           # work-items two-pane dashboard
            ├── detail.py              # drill-down detail screen
            ├── demo_inputs.py
            ├── demo_data.py
            ├── demo_layout.py
            ├── demo_progress.py
            ├── demo_files.py
            ├── demo_api_files.py
            ├── demo_live_dashboard.py
            ├── demo_command_palette.py
            ├── demo_log_stream.py
            ├── demo_wizard.py
            ├── demo_report.py
            ├── demo_search_filter.py
            ├── demo_settings.py
            ├── demo_workers.py
            ├── demo_context_menu.py
            ├── demo_inline_edit.py
            ├── demo_theme.py
            ├── demo_custom_widget.py
            ├── demo_form_validation.py
            ├── demo_pagination.py
            ├── demo_multiselect.py
            ├── demo_content_switcher.py
            ├── demo_help_keys.py
            ├── demo_option_list.py
            ├── demo_masked_input.py
            ├── demo_notification_drawer.py
            ├── demo_autocomplete.py
            ├── demo_selection_list.py
            ├── demo_toggle_button.py
            ├── demo_rule.py
            ├── demo_tooltip.py
            ├── demo_pretty.py
            ├── demo_link.py
            ├── demo_log.py
            ├── demo_tabs.py
            ├── demo_master_detail.py
            ├── demo_master_detail_vertical.py
            ├── demo_form_table.py
            ├── demo_label_form.py
            ├── demo_search_grid.py   # most complete demo — filter/grid/edit
            ├── demo_cards.py
            ├── demo_cards2.py
            └── demo_dicom_nrrd.py    # DICOM → NRRD conversion metrics dashboard
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

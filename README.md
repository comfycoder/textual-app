# your-cli

A Textual TUI for the AIQ platform.

## Quick start (conda)

```bash
conda env create -f environment.yml
conda activate your-cli
your-cli
```

That's the whole loop. The `pip install -e .[dev]` step happens automatically
via the `pip:` block in `environment.yml`, so editing source files takes effect
on the next `your-cli` run with no reinstall.

## Updating dependencies

After changing `pyproject.toml`:

```bash
conda env update -f environment.yml --prune
```

## Running the app

```bash
your-cli                            # launches the TUI
your-cli --help                     # full CLI help
your-cli --version
your-cli login --tenant <tenant-id> # scriptable subcommand
your-cli logout
```

Equivalently, during development:

```bash
python -m your_cli
```

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

## Regenerating the OpenAPI client

Drop your spec into `api/openapi.yaml`, then:

```bash
./scripts/regen-client.sh
```

The generated client lands in `src/your_cli/client/` and is import-time
available as `your_cli.client`. Do not hand-edit files there.

## Project layout

```
your-cli/
├── pyproject.toml               # package metadata + dependencies + entry point
├── environment.yml              # conda env definition (delegates to pyproject)
├── api/openapi.yaml             # OpenAPI spec (source of truth for the client)
├── scripts/regen-client.sh      # regenerates src/your_cli/client/
└── src/your_cli/
    ├── __init__.py
    ├── __main__.py              # enables `python -m your_cli`
    ├── cli.py                   # Typer app, `your-cli` entry point
    ├── config.py                # Pydantic Settings
    ├── client/                  # generated OpenAPI client (do not edit)
    └── tui/
        ├── app.py               # root Textual App
        ├── styles.tcss          # Textual CSS
        └── screens/
            └── dashboard.py     # stub two-pane screen
```

## Windows notes

The TUI requires a modern terminal. **Windows Terminal** (default on Windows 11,
free install on Windows 10) renders everything correctly including mouse
support. Legacy `cmd.exe` and old PowerShell 5.1 in `conhost` are not supported.

## Linting and tests

```bash
ruff check .
mypy src
pytest
```

## Textual developer tools

The `textual-dev` package (pulled in via the `dev` extra) provides:

```bash
textual console      # live log viewer; run in a second terminal
textual run --dev src/your_cli/__main__.py   # hot-reload mode
```

These are invaluable when iterating on screens and widgets.

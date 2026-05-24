"""Typer entry point.

Running `your-cli` with no subcommand launches the TUI.
Subcommands provide scriptable, non-interactive operations.
"""

from pathlib import Path
from typing import Annotated

import typer

from your_cli import __version__
from your_cli.config import Settings
from your_cli.tui.app import YourCliApp

app = typer.Typer(
    name="your-cli",
    help="TUI for the AIQ platform.",
    no_args_is_help=False,
    add_completion=True,
)


def _load_settings(config: Path | None, api_base_url: str | None) -> Settings:
    settings = Settings(_env_file=config) if config else Settings()
    if api_base_url:
        settings.api_base_url = api_base_url
    return settings


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: Annotated[
        Path | None,
        typer.Option("--config", "-c", help="Path to a .env-style config file."),
    ] = None,
    api_base_url: Annotated[
        str | None,
        typer.Option("--api-base-url", help="Override the API base URL."),
    ] = None,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show version and exit."),
    ] = False,
) -> None:
    """Global options. Runs before any subcommand, or alone to launch the TUI."""
    if version:
        typer.echo(f"your-cli {__version__}")
        raise typer.Exit()

    ctx.obj = _load_settings(config, api_base_url)

    if ctx.invoked_subcommand is None:
        YourCliApp(ctx.obj).run()


@app.command()
def login(
    ctx: typer.Context,
    tenant: Annotated[
        str | None,
        typer.Option("--tenant", help="Entra tenant ID (overrides config)."),
    ] = None,
) -> None:
    """Authenticate and cache a token."""
    settings: Settings = ctx.obj
    tenant_id = tenant or settings.tenant_id
    if not tenant_id:
        typer.echo("Error: --tenant or AIQ_TENANT_ID is required.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"[stub] Would start device-code flow against tenant {tenant_id}.")


@app.command()
def logout(ctx: typer.Context) -> None:
    """Clear cached credentials."""
    typer.echo("[stub] Would remove cached token.")

def run() -> None:
    app()

if __name__ == "__main__":
    run()

    
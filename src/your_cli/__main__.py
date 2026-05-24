"""Allow `python -m your_cli` as an alternative to the `your-cli` launcher."""

from your_cli.cli import app

if __name__ == "__main__":
    app()

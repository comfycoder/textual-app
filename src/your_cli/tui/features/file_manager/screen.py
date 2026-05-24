"""Demo: File Manager using DirectoryTree."""

from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, RichLog, Static

MAX_PREVIEW_LINES = 200


def _format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} TB"


class FilesDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("[", "narrow_sidebar", "Narrow"),
        Binding("]", "widen_sidebar", "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(30)
    _selected_path: reactive[Path | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="files-body"):
            yield DirectoryTree(Path("C:\\"), id="file-tree")
            with Vertical(id="file-preview"):
                yield Static("Select a file or folder", id="file-meta", classes="demo-label")
                yield RichLog(id="file-content", highlight=True, wrap=False)
                with Horizontal(id="path-bar"):
                    yield Static("", id="selected-path")
                    yield Button("Send to API", variant="primary", id="btn-use-path", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp
        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width
        self.query_one(DirectoryTree).focus()

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#file-tree").styles.width = f"{width}%"

    def watch__selected_path(self, path: Path | None) -> None:
        btn = self.query_one("#btn-use-path", Button)
        label = self.query_one("#selected-path", Static)
        if path is None:
            btn.disabled = True
            label.update("")
        else:
            btn.disabled = False
            label.update(f"[dim]Path:[/dim] [b]{path}[/b]")

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        path = event.path
        self._selected_path = path
        log = self.query_one("#file-content", RichLog)
        meta = self.query_one("#file-meta", Static)
        log.clear()
        try:
            stat = path.stat()
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            children = sum(1 for _ in path.iterdir())
            meta.update(
                f"[b]{path.name}/[/b]  "
                f"[dim]{children} items · modified {modified}[/dim]"
            )
            log.write(f"[dim]Folder:[/dim] {path}")
            for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name)):
                icon = "📄" if child.is_file() else "📁"
                log.write(f"  {icon}  {child.name}")
        except PermissionError:
            meta.update(f"[red]Permission denied:[/red] {path.name}")
        except OSError as exc:
            meta.update(f"[red]Error:[/red] {exc}")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = event.path
        self._selected_path = path
        log = self.query_one("#file-content", RichLog)
        meta = self.query_one("#file-meta", Static)
        log.clear()
        try:
            stat = path.stat()
            size = _format_size(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            meta.update(
                f"[b]{path.name}[/b]  "
                f"[dim]{size} · modified {modified} · {path.suffix or 'no ext'}[/dim]"
            )
            try:
                text = path.read_text(encoding="utf-8", errors="strict")
                lines = text.splitlines()
                for line in lines[:MAX_PREVIEW_LINES]:
                    log.write(line)
                if len(lines) > MAX_PREVIEW_LINES:
                    log.write(
                        f"\n[dim]… truncated — showing first {MAX_PREVIEW_LINES} "
                        f"of {len(lines)} lines[/dim]"
                    )
            except UnicodeDecodeError:
                log.write("[dim]Binary file — cannot preview.[/dim]")
        except PermissionError:
            meta.update(f"[red]Permission denied:[/red] {path.name}")
        except OSError as exc:
            meta.update(f"[red]Error:[/red] {exc}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-use-path" and self._selected_path is not None:
            # In a real app this would call your API client with self._selected_path
            self.notify(
                f"Would call API with path:\n{self._selected_path}",
                title="API Call",
                severity="information",
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

"""Demo: API-backed virtual filesystem using Tree with lazy loading.

The _fake_api_* functions simulate httpx calls — replace them with your
real OpenAPI client when ready.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, RichLog, Static, Tree
from textual.widgets.tree import TreeNode

# ── Simulated API ─────────────────────────────────────────────────────────────
# Replace these with real httpx calls against your OpenAPI client.


@dataclass
class ApiItem:
    path: str
    name: str
    kind: Literal["folder", "file"]
    size: int = 0
    modified: str = "2026-05-23 09:00"
    description: str = ""


_FAKE_FS: dict[str, list[ApiItem]] = {
    "/": [
        ApiItem("/projects", "projects", "folder",
                description="Active research projects"),
        ApiItem("/datasets", "datasets", "folder",
                description="Training and validation data"),
        ApiItem("/config.yaml", "config.yaml", "file",
                size=1_024, description="Platform configuration"),
    ],
    "/projects": [
        ApiItem("/projects/alpha", "alpha", "folder", description="Project Alpha — JHU"),
        ApiItem("/projects/beta",  "beta",  "folder", description="Project Beta — UNC"),
    ],
    "/projects/alpha": [
        ApiItem("/projects/alpha/run_001.log",   "run_001.log",   "file", size=45_678),
        ApiItem("/projects/alpha/results.csv",   "results.csv",   "file", size=12_345),
        ApiItem("/projects/alpha/pipeline.yaml", "pipeline.yaml", "file", size=2_048),
    ],
    "/projects/beta": [
        ApiItem("/projects/beta/run_001.log", "run_001.log", "file", size=38_912),
        ApiItem("/projects/beta/model.pt",    "model.pt",    "file", size=524_288,
                description="Trained model weights"),
    ],
    "/datasets": [
        ApiItem("/datasets/training",   "training",   "folder", description="Training split"),
        ApiItem("/datasets/validation", "validation", "folder", description="Validation split"),
    ],
    "/datasets/training": [
        ApiItem("/datasets/training/data.parquet",   "data.parquet",   "file", size=104_857_600),
        ApiItem("/datasets/training/labels.parquet", "labels.parquet", "file", size=2_097_152),
    ],
    "/datasets/validation": [
        ApiItem("/datasets/validation/data.parquet", "data.parquet", "file", size=26_214_400),
    ],
}


async def _fake_api_list(path: str) -> list[ApiItem]:
    await asyncio.sleep(0.3)  # simulates network latency
    return _FAKE_FS.get(path, [])


# ── Helpers ───────────────────────────────────────────────────────────────────

_LOADING = "__loading__"


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n //= 1024
    return f"{n:.1f} TB"


# ── Screen ────────────────────────────────────────────────────────────────────


class ApiFilesDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("[", "narrow_sidebar", "Narrow"),
        Binding("]", "widen_sidebar", "Widen"),
    ]

    sidebar_width: reactive[int] = reactive(30)
    _selected: ApiItem | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="api-files-body"):
            yield Tree("/ (root)", id="api-tree")
            with Vertical(id="api-detail"):
                yield Static(
                    "Select a file or folder", id="api-meta", classes="demo-label"
                )
                yield RichLog(id="api-content", highlight=True)
                with Horizontal(id="api-path-bar"):
                    yield Static("", id="api-selected-path")
                    yield Button(
                        "Send to API", variant="primary", id="btn-api-use", disabled=True
                    )
        yield Footer()

    def on_mount(self) -> None:
        from your_cli.tui.app import YourCliApp

        app = self.app
        assert isinstance(app, YourCliApp)
        self.sidebar_width = app.settings.sidebar_width

        tree = self.query_one("#api-tree", Tree)
        tree.root.data = ApiItem("/", "/", "folder", description="Root")
        tree.root.add_leaf("[dim]Loading…[/dim]", data=_LOADING)
        tree.root.expand()
        tree.focus()

    def watch_sidebar_width(self, width: int) -> None:
        self.query_one("#api-tree").styles.width = f"{width}%"

    def action_narrow_sidebar(self) -> None:
        self.sidebar_width = max(10, self.sidebar_width - 5)

    def action_widen_sidebar(self) -> None:
        self.sidebar_width = min(80, self.sidebar_width + 5)

    # ── Tree events ───────────────────────────────────────────────────────────

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node
        item = node.data
        if not isinstance(item, ApiItem) or item.kind != "folder":
            return
        children = list(node.children)
        if children and children[0].data == _LOADING:
            self._fetch_children(node, item.path)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        item = event.node.data
        if not isinstance(item, ApiItem):
            return
        self._selected = item
        self._show_detail(item)
        self.query_one("#api-selected-path", Static).update(
            f"[dim]Path:[/dim] [b]{item.path}[/b]"
        )
        self.query_one("#btn-api-use", Button).disabled = False

    # ── Workers ───────────────────────────────────────────────────────────────

    @work
    async def _fetch_children(self, node: TreeNode, path: str) -> None:
        items = await _fake_api_list(path)
        for child in list(node.children):
            child.remove()
        for item in items:
            if item.kind == "folder":
                child_node = node.add(f"📁  {item.name}", data=item)
                child_node.add_leaf("[dim]Loading…[/dim]", data=_LOADING)
            else:
                node.add_leaf(f"📄  {item.name}", data=item)

    # ── Detail panel ──────────────────────────────────────────────────────────

    def _show_detail(self, item: ApiItem) -> None:
        log = self.query_one("#api-content", RichLog)
        log.clear()
        if item.kind == "folder":
            self.query_one("#api-meta", Static).update(
                f"[b]{item.name}/[/b]  [dim]folder[/dim]"
            )
            log.write(f"[dim]Path        [/dim]  {item.path}")
            log.write(f"[dim]Description [/dim]  {item.description or '—'}")
        else:
            self.query_one("#api-meta", Static).update(
                f"[b]{item.name}[/b]  "
                f"[dim]{_fmt_size(item.size)} · {item.modified}[/dim]"
            )
            log.write(f"[dim]Path        [/dim]  {item.path}")
            log.write(f"[dim]Size        [/dim]  {_fmt_size(item.size)}")
            log.write(f"[dim]Modified    [/dim]  {item.modified}")
            log.write(f"[dim]Description [/dim]  {item.description or '—'}")

    # ── Button ────────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-api-use" and self._selected is not None:
            self.notify(
                f"Would call API with:\n{self._selected.path}",
                title="API Call",
                severity="information",
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()

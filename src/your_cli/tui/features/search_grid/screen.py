"""Demo: Search → Grid → Edit — filter records, page through results, open edit form on row select."""

import random
from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.validation import Integer, Length, Regex
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Rule,
    Select,
    Static,
    Switch,
)
from textual.widgets._select import SelectCurrent as _SelectCurrent  # internal, not exported

# ── Shared seed data ──────────────────────────────────────────────────────────

_STATUS_OPTS   = [("Queued","queued"),("Running","running"),("Done","done"),("Failed","failed"),("Pending","pending")]
_TYPE_OPTS     = [("Training","training"),("Validation","validation"),("Export","export"),("Inference","inference"),("Preprocessing","preprocessing")]
_PRIORITY_OPTS = [("Low","low"),("Medium","medium"),("High","high"),("Critical","critical")]
_TENANT_OPTS   = [("JHU","jhu"),("UNC","unc"),("Mayo","mayo"),("Stanford","stanford")]
_ENV_OPTS      = [("Production","prod"),("Staging","staging"),("Development","dev")]

_STATUS_COLORS = {"queued":"yellow","running":"cyan","done":"green","failed":"red","pending":"dim"}
_PRI_COLORS    = {"low":"dim","medium":"yellow","high":"red","critical":"bold red"}

_SUBMITTERS = ["alice@jhu.edu","bob@unc.edu","carol@mayo.org","dave@stanford.edu","eve@jhu.edu"]
_TAGS_POOL  = ["baseline","nightly","ablation","prod","dev","manual","scheduled","experiment"]

random.seed(42)

_RECORDS: list[dict] = [
    {
        "id":           f"wi-{i:03d}",
        "tenant":       random.choice([v for _, v in _TENANT_OPTS]),
        "type":         random.choice([v for _, v in _TYPE_OPTS]),
        "status":       random.choice([v for _, v in _STATUS_OPTS]),
        "priority":     random.choice([v for _, v in _PRIORITY_OPTS]),
        "environment":  random.choice([v for _, v in _ENV_OPTS]),
        "submitted_by": random.choice(_SUBMITTERS),
        "node":         f"gpu-node-{random.randint(1, 8):02d}",
        "max_jobs":     str(random.randint(1, 8)),
        "timeout_min":  str(random.randint(10, 120)),
        "gpu_required": random.choice([True, False]),
        "auto_retry":   random.choice([True, False]),
        "tags":         ", ".join(random.sample(_TAGS_POOL, random.randint(0, 3))),
        "notes":        random.choice(["Baseline run", "Nightly batch", "Ablation study", "Prod deployment", "", ""]),
        "description":  random.choice(["Full training run.", "Validate checkpoint.", "Export to ONNX.", "", "", ""]),
    }
    for i in range(1, 201)
]
_RECORD_BY_ID   = {r["id"]: r for r in _RECORDS}
_PAGE_SIZE_OPTS = [("10", 10), ("20", 20), ("50", 50), ("100", 100)]
_DEFAULT_PAGE_SIZE = 10

# (header label, record field key, fixed width or None for auto)
# Fixed widths on "Submitted by" and "Tags" allow those cells to wrap
# to a second line when height=2 is set on each row.
_SG_COLUMNS: list[tuple[str, str, int | None]] = [
    ("ID",           "id",           None),
    ("Tenant",       "tenant",       None),
    ("Type",         "type",         None),
    ("Status",       "status",       None),
    ("Priority",     "priority",     None),
    ("Env",          "environment",  None),
    ("Submitted by", "submitted_by", 20),
    ("Tags",         "tags",         22),
]


# ── Edit screen ───────────────────────────────────────────────────────────────

class EditJobScreen(Screen[None]):
    """Label-form editor for a single record; Ctrl+S saves and pops back."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save",    "Save"),
    ]

    def __init__(self, record_id: str) -> None:
        super().__init__()
        self._record_id    = record_id
        self._field_errors: dict[str, str] = {}   # field_id → message

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="ej-body"):
            with Vertical(id="ej-form"):
                yield Static("", id="ej-title")
                yield Rule()

                yield Static("[dim]Identity[/dim]", classes="ej-section")
                with Horizontal(classes="ej-row"):
                    yield Label("Job ID", classes="ej-label")
                    yield Static("", id="ej-id-display", classes="ej-id-display")
                with Horizontal(classes="ej-row"):
                    yield Label("Tenant", id="lbl-ej-tenant", classes="ej-label")
                    yield Input(id="ej-tenant",
                                validators=[Length(minimum=1, failure_description="Required")])
                with Horizontal(classes="ej-row"):
                    yield Label("Type", id="lbl-ej-type", classes="ej-label")
                    yield Select(_TYPE_OPTS, prompt="Select…", id="ej-type", allow_blank=True)

                yield Rule(line_style="dashed")
                yield Static("[dim]State[/dim]", classes="ej-section")
                with Horizontal(classes="ej-row"):
                    yield Label("Status", id="lbl-ej-status", classes="ej-label")
                    yield Select(_STATUS_OPTS, prompt="Select…", id="ej-status", allow_blank=True)
                with Horizontal(classes="ej-row"):
                    yield Label("Priority", id="lbl-ej-priority", classes="ej-label")
                    yield Select(_PRIORITY_OPTS, prompt="Select…", id="ej-priority", allow_blank=True)
                with Horizontal(classes="ej-row"):
                    yield Label("Environment", id="lbl-ej-env", classes="ej-label")
                    yield Select(_ENV_OPTS, prompt="Select…", id="ej-env", allow_blank=True)

                yield Rule(line_style="dashed")
                yield Static("[dim]Execution[/dim]", classes="ej-section")
                with Horizontal(classes="ej-row"):
                    yield Label("Submitted by", id="lbl-ej-submitted-by", classes="ej-label")
                    yield Input(id="ej-submitted-by",
                                validators=[Regex(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                                                  failure_description="Must be a valid email address")])
                with Horizontal(classes="ej-row"):
                    yield Label("Worker node", id="lbl-ej-node", classes="ej-label")
                    yield Input(id="ej-node",
                                validators=[Regex(r"^gpu-node-\d+$",
                                                  failure_description="Must match gpu-node-NN")])
                with Horizontal(classes="ej-row"):
                    yield Label("Max concurrent jobs  [dim]1–20[/dim]", id="lbl-ej-max-jobs", classes="ej-label")
                    yield Input(id="ej-max-jobs", type="integer",
                                validators=[Integer(minimum=1, maximum=20,
                                                    failure_description="Must be between 1 and 20")])
                with Horizontal(classes="ej-row"):
                    yield Label("Timeout  [dim](minutes)[/dim]", id="lbl-ej-timeout", classes="ej-label")
                    yield Input(id="ej-timeout", type="integer",
                                validators=[Integer(minimum=1, maximum=1440,
                                                    failure_description="Must be between 1 and 1440")])
                with Horizontal(classes="ej-row ej-toggle-row"):
                    yield Label("GPU required", classes="ej-label")
                    yield Switch(id="ej-gpu")
                with Horizontal(classes="ej-row ej-toggle-row"):
                    yield Label("Auto-retry", classes="ej-label")
                    yield Switch(id="ej-retry")

                yield Rule(line_style="dashed")
                yield Static("[dim]Metadata[/dim]", classes="ej-section")
                with Horizontal(classes="ej-row"):
                    yield Label("Tags  [dim](comma-separated)[/dim]", classes="ej-label")
                    yield Input(id="ej-tags")
                with Horizontal(classes="ej-row"):
                    yield Label("Notes", classes="ej-label")
                    yield Input(id="ej-notes")
                with Horizontal(classes="ej-row"):
                    yield Label("Description", classes="ej-label")
                    yield Input(id="ej-description")

                yield Rule()

                with Vertical(id="ej-errors"):
                    yield Static("", id="ej-error-list")

                with Horizontal(id="ej-actions"):
                    yield Button("Save",   variant="primary", id="btn-ej-save")
                    yield Button("Cancel", id="btn-ej-cancel")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#ej-errors").display = False
        rec = _RECORD_BY_ID.get(self._record_id)
        if not rec:
            return
        self.query_one("#ej-title",        Static).update(f"[b]Edit Job[/b]  [dim]{rec['id']}[/dim]")
        self.query_one("#ej-id-display",   Static).update(f"[b]{rec['id']}[/b]")
        self.query_one("#ej-tenant",       Input ).value  = rec["tenant"]
        self.query_one("#ej-type",         Select).value  = rec["type"]
        self.query_one("#ej-status",       Select).value  = rec["status"]
        self.query_one("#ej-priority",     Select).value  = rec["priority"]
        self.query_one("#ej-env",          Select).value  = rec["environment"]
        self.query_one("#ej-submitted-by", Input ).value  = rec["submitted_by"]
        self.query_one("#ej-node",         Input ).value  = rec["node"]
        self.query_one("#ej-max-jobs",     Input ).value  = rec["max_jobs"]
        self.query_one("#ej-timeout",      Input ).value  = rec["timeout_min"]
        self.query_one("#ej-gpu",          Switch).value  = rec["gpu_required"]
        self.query_one("#ej-retry",        Switch).value  = rec["auto_retry"]
        self.query_one("#ej-tags",         Input ).value  = rec["tags"]
        self.query_one("#ej-notes",        Input ).value  = rec["notes"]
        self.query_one("#ej-description",  Input ).value  = rec["description"]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-ej-save":
                self.action_save()
            case "btn-ej-cancel":
                self.action_go_back()

    # field_id → label_id for every validated field
    _LABEL_MAP: dict[str, str] = {
        "ej-tenant":       "lbl-ej-tenant",
        "ej-type":         "lbl-ej-type",
        "ej-status":       "lbl-ej-status",
        "ej-priority":     "lbl-ej-priority",
        "ej-env":          "lbl-ej-env",
        "ej-submitted-by": "lbl-ej-submitted-by",
        "ej-node":         "lbl-ej-node",
        "ej-max-jobs":     "lbl-ej-max-jobs",
        "ej-timeout":      "lbl-ej-timeout",
    }

    # field_id → display name used in error messages
    _FIELD_NAMES: dict[str, str] = {
        "ej-tenant":       "Tenant",
        "ej-type":         "Type",
        "ej-status":       "Status",
        "ej-priority":     "Priority",
        "ej-env":          "Environment",
        "ej-submitted-by": "Submitted by",
        "ej-node":         "Worker node",
        "ej-max-jobs":     "Max jobs",
        "ej-timeout":      "Timeout",
    }

    # required input field IDs (validated live in on_input_changed even when blank)
    _REQUIRED_INPUTS: frozenset[str] = frozenset({"ej-tenant"})

    # required select field IDs (validated live in on_select_changed when cleared)
    _REQUIRED_SELECTS: frozenset[str] = frozenset({"ej-type", "ej-status", "ej-priority", "ej-env"})

    def _set_field_error(self, field_id: str, has_error: bool, message: str = "") -> None:
        lbl_id = self._LABEL_MAP.get(field_id)
        if not lbl_id:
            return
        lbl    = self.query_one(f"#{lbl_id}", Label)
        widget = self.query_one(f"#{field_id}")
        if has_error:
            lbl.add_class("field-error-label")
            widget.add_class("field-error")
            self._field_errors[field_id] = message
        else:
            lbl.remove_class("field-error-label")
            widget.remove_class("field-error")
            self._field_errors.pop(field_id, None)
        # For Select widgets the visible surface is the inner SelectCurrent child.
        # CSS class rules on SelectCurrent lose to DEFAULT_CSS; the string-based
        # widget.query() can also silently return nothing for internal widgets.
        # Walk children directly with isinstance — always reliable.
        if isinstance(widget, Select):
            err = self.app.get_css_variables().get("error", "#ba3c5b") if has_error else None
            for child in widget.children:
                if isinstance(child, _SelectCurrent):
                    child.styles.background = f"{err} 15%" if has_error else None
        self._refresh_error_panel()

    def _refresh_error_panel(self) -> None:
        panel = self.query_one("#ej-errors")
        if not self._field_errors:
            panel.display = False
        else:
            self.query_one("#ej-error-list", Static).update(
                "\n".join(f"[red]▸ {m}[/red]" for m in self._field_errors.values())
            )
            panel.display = True

    def _clear_errors(self) -> None:
        self._field_errors.clear()
        for w in self.query(".field-error-label"):
            w.remove_class("field-error-label")
        for w in self.query(".field-error"):
            w.remove_class("field-error")
        # Also clear any inline backgrounds set on SelectCurrent children
        for sel in self.query_one("#ej-form").query(Select):
            for child in sel.children:
                if isinstance(child, _SelectCurrent):
                    child.styles.background = None
        self.query_one("#ej-errors").display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        field_id = event.input.id
        if field_id not in self._LABEL_MAP:
            return
        inp   = event.input
        val   = inp.value.strip()
        label = self._FIELD_NAMES.get(field_id, field_id)

        if not inp.validators:
            self._set_field_error(field_id, False)
            return

        # optional fields: clear error when blank, don't nag before Save
        if field_id not in self._REQUIRED_INPUTS and not val:
            self._set_field_error(field_id, False)
            return

        result = inp.validate(val)
        if result.is_valid:
            self._set_field_error(field_id, False)
        else:
            self._set_field_error(field_id, True,
                                   f"{label}: {result.failures[0].description}")

    def on_select_changed(self, event: Select.Changed) -> None:
        sel_id = event.select.id
        if sel_id not in self._LABEL_MAP:
            return
        if sel_id in self._REQUIRED_SELECTS:
            # Validate live: flag required selects that have been cleared
            ok    = isinstance(event.value, str)
            name  = self._FIELD_NAMES.get(sel_id, sel_id)
            self._set_field_error(sel_id, not ok, f"{name}: Required" if not ok else "")
        else:
            self._set_field_error(sel_id, False)

    def action_save(self) -> None:
        rec = _RECORD_BY_ID.get(self._record_id)
        if not rec:
            return

        def _check_select(field_id: str, label: str, value) -> None:
            ok = isinstance(value, str)
            self._set_field_error(field_id, not ok, f"{label}: Required" if not ok else "")

        def _check_input(field_id: str, label: str, required: bool = False) -> None:
            inp = self.query_one(f"#{field_id}", Input)
            val = inp.value.strip()
            if not required and not val:
                self._set_field_error(field_id, False)
                return
            result = inp.validate(val)
            if not result.is_valid:
                self._set_field_error(field_id, True, f"{label}: {result.failures[0].description}")
            else:
                self._set_field_error(field_id, False)

        _check_input("ej-tenant",       "Tenant",       required=True)
        _check_select("ej-type",        "Type",         self.query_one("#ej-type",     Select).value)
        _check_select("ej-status",      "Status",       self.query_one("#ej-status",   Select).value)
        _check_select("ej-priority",    "Priority",     self.query_one("#ej-priority", Select).value)
        _check_select("ej-env",         "Environment",  self.query_one("#ej-env",      Select).value)
        _check_input("ej-submitted-by", "Submitted by")
        _check_input("ej-node",         "Worker node")
        _check_input("ej-max-jobs",     "Max jobs")
        _check_input("ej-timeout",      "Timeout")

        if self._field_errors:
            return
        self._clear_errors()

        tenant = self.query_one("#ej-tenant", Input).value.strip()
        jtype  = self.query_one("#ej-type",   Select).value
        status = self.query_one("#ej-status", Select).value
        pri    = self.query_one("#ej-priority", Select).value
        env    = self.query_one("#ej-env",    Select).value
        rec.update({
            "tenant":       tenant,
            "type":         jtype,
            "status":       status,
            "priority":     pri,
            "environment":  env,
            "submitted_by": self.query_one("#ej-submitted-by", Input).value.strip(),
            "node":         self.query_one("#ej-node",         Input).value.strip(),
            "max_jobs":     self.query_one("#ej-max-jobs",     Input).value.strip(),
            "timeout_min":  self.query_one("#ej-timeout",      Input).value.strip(),
            "gpu_required": self.query_one("#ej-gpu",          Switch).value,
            "auto_retry":   self.query_one("#ej-retry",        Switch).value,
            "tags":         self.query_one("#ej-tags",         Input).value.strip(),
            "notes":        self.query_one("#ej-notes",        Input).value.strip(),
            "description":  self.query_one("#ej-description",  Input).value.strip(),
        })
        self.notify(f"{self._record_id} saved", title="Saved", severity="information")
        self.app.pop_screen()

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ── Search + Grid screen ──────────────────────────────────────────────────────

class SearchGridDemoScreen(Screen[None]):
    """Search form above a pageable DataTable; Enter on any row opens the edit screen."""
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("escape", "go_back",      "Back"),
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("f5",     "do_search",    "Refresh"),
    ]

    _page: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._filtered:       list[dict]  = []
        self._last_edited_id: str | None  = None
        self._page_size:      int         = _DEFAULT_PAGE_SIZE
        self._sort_key:       str | None  = None   # record field name, or None
        self._sort_asc:       bool        = True
        self._col_keys:       dict        = {}     # field key → ColumnKey

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sg-body"):

            # ── Filter bar ────────────────────────────────────────
            with Vertical(id="sg-search-panel"):
                yield Static(
                    "[b]Search Jobs[/b]  "
                    "[dim]Ctrl+F · Enter on a row to edit[/dim]",
                    id="sg-search-title",
                )
                with Horizontal(classes="sg-filter-row"):
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Job ID / Submitter / Tags")
                        yield Input(id="sg-q")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Status")
                        yield Select(_STATUS_OPTS, prompt="All statuses", id="sg-status")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Type")
                        yield Select(_TYPE_OPTS, prompt="All types", id="sg-type")
                    with Vertical(classes="sg-filter-field"):
                        yield Label("Priority")
                        yield Select(_PRIORITY_OPTS, prompt="All priorities", id="sg-priority")
                with Horizontal(id="sg-search-actions"):
                    yield Button("Search", variant="primary", id="btn-sg-search")
                    yield Button("Clear",  id="btn-sg-clear")
                    yield Static("", id="sg-search-spacer")
                    yield Label("Per page", id="sg-per-page-label")
                    yield Select(
                        _PAGE_SIZE_OPTS,
                        value=_DEFAULT_PAGE_SIZE,
                        id="sg-page-size",
                        allow_blank=False,
                    )

            # ── Results grid ──────────────────────────────────────
            with Vertical(id="sg-grid-area"):
                yield DataTable(id="sg-table", cursor_type="row", zebra_stripes=True)

            # ── Pagination bar ────────────────────────────────────
            with Horizontal(id="sg-pagination"):
                yield Button("|← First", id="btn-sg-first", disabled=True)
                yield Button("← Prev",   id="btn-sg-prev",  disabled=True)
                yield Static("", id="sg-page-label")
                yield Button("Next →",   id="btn-sg-next",  disabled=True)
                yield Button("Last →|",  id="btn-sg-last",  disabled=True)
                yield Static("", id="sg-result-count")

        yield Footer()

    def on_mount(self) -> None:
        tbl = self.query_one("#sg-table", DataTable)
        self._col_keys = {
            key: tbl.add_column(label, key=key, width=width)
            for label, key, width in _SG_COLUMNS
        }
        self._filtered = list(reversed(_RECORDS))
        self._load_page()
        tbl.focus()

    def on_screen_resume(self) -> None:
        """Refresh current page and re-select the last-edited row."""
        self._load_page()
        self._restore_cursor()

    def _restore_cursor(self) -> None:
        if not self._last_edited_id:
            return
        for i, rec in enumerate(self._filtered):
            if rec["id"] == self._last_edited_id:
                target_page = i // self._page_size
                if target_page != self._page:
                    self._page = target_page
                    self._load_page()
                self.query_one("#sg-table", DataTable).move_cursor(row=i % self._page_size)
                return

    # ── Sort helpers ──────────────────────────────────────────────

    def _apply_sort(self) -> None:
        """Sort self._filtered in-place by the active sort column."""
        if not self._sort_key:
            return
        self._filtered.sort(
            key=lambda r: (r.get(self._sort_key) or "").lower(),
            reverse=not self._sort_asc,
        )

    def _update_column_headers(self) -> None:
        """Refresh header labels to show/hide the sort indicator."""
        tbl = self.query_one("#sg-table", DataTable)
        dimensions_changed = False
        for label, key, _width in _SG_COLUMNS:
            ck = self._col_keys[key]
            col = tbl.columns[ck]
            indicator = (" ▲" if self._sort_asc else " ▼") if key == self._sort_key else ""
            new_label = Text(label + indicator)
            col.label = new_label
            # auto_width columns track content_width; grow it if the new label is wider
            label_width = len(label + indicator)
            if label_width > col.content_width:
                col.content_width = label_width
                dimensions_changed = True
        if dimensions_changed:
            tbl._require_update_dimensions = True
        tbl.refresh()

    # ── Filter + render ───────────────────────────────────────────

    def _run_search(self) -> None:
        q      = self.query_one("#sg-q",        Input ).value.strip().lower()
        status = self.query_one("#sg-status",   Select).value
        jtype  = self.query_one("#sg-type",     Select).value
        pri    = self.query_one("#sg-priority", Select).value

        results = list(reversed(_RECORDS))
        if q:
            results = [r for r in results
                       if q in r["id"].lower()
                       or q in r["submitted_by"].lower()
                       or q in r["tags"].lower()]
        # Use isinstance(str) rather than `is not Select.BLANK` — after select.clear()
        # the value may be None or a non-BLANK sentinel, not Select.BLANK itself.
        if isinstance(status, str):
            results = [r for r in results if r["status"] == status]
        if isinstance(jtype, str):
            results = [r for r in results if r["type"]   == jtype]
        if isinstance(pri, str):
            results = [r for r in results if r["priority"] == pri]

        self._filtered = results
        self._apply_sort()
        self._page = 0
        self._load_page()

    def _load_page(self) -> None:
        tbl   = self.query_one("#sg-table", DataTable)
        total = len(self._filtered)
        pages = max(1, (total + self._page_size - 1) // self._page_size)
        start = self._page * self._page_size
        chunk = self._filtered[start : start + self._page_size]

        tbl.clear()
        for rec in chunk:
            sc = _STATUS_COLORS.get(rec["status"], "white")
            pc = _PRI_COLORS.get(rec["priority"], "white")
            tbl.add_row(
                rec["id"], rec["tenant"], rec["type"],
                f"[{sc}]{rec['status']}[/{sc}]",
                f"[{pc}]{rec['priority']}[/{pc}]",
                rec["environment"],
                rec["submitted_by"],
                rec["tags"] or "[dim]—[/dim]",
                key=rec["id"],
                height=None,
            )

        self.query_one("#sg-result-count", Static).update(
            f"[dim]({total} record{'s' if total != 1 else ''})[/dim]"
        )
        self.query_one("#sg-page-label", Static).update(
            f"  Page {self._page + 1} of {pages}  "
        )
        at_first = self._page == 0
        at_last  = self._page >= pages - 1
        self.query_one("#btn-sg-first", Button).disabled = at_first
        self.query_one("#btn-sg-prev",  Button).disabled = at_first
        self.query_one("#btn-sg-next",  Button).disabled = at_last
        self.query_one("#btn-sg-last",  Button).disabled = at_last

    # ── Button / row events ───────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        total = len(self._filtered)
        pages = max(1, (total + self._page_size - 1) // self._page_size)
        match event.button.id:
            case "btn-sg-search":
                self._run_search()
            case "btn-sg-clear":
                self._clear_search()
            case "btn-sg-first":
                if self._page != 0:
                    self._page = 0
                    self._load_page()
            case "btn-sg-prev":
                if self._page > 0:
                    self._page -= 1
                    self._load_page()
            case "btn-sg-next":
                if self._page < pages - 1:
                    self._page += 1
                    self._load_page()
            case "btn-sg-last":
                if self._page != pages - 1:
                    self._page = pages - 1
                    self._load_page()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "sg-q":
            self._run_search()

    def on_select_changed(self, event: Select.Changed) -> None:
        match event.select.id:
            case "sg-page-size":
                if isinstance(event.value, int):
                    self._page_size = event.value
                    self._page = 0
                    self._load_page()
            case "sg-status" | "sg-type" | "sg-priority":
                self._run_search()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        if event.data_table.id != "sg-table":
            return
        col_key = event.column_key.value
        if col_key is None:
            return
        if self._sort_key == col_key:
            if self._sort_asc:
                self._sort_asc = False              # 2nd click → descending
            else:
                self._sort_key = None               # 3rd click → no sort
        else:
            self._sort_key = col_key
            self._sort_asc = True                   # 1st click → ascending
        self._update_column_headers()
        if self._sort_key is None:
            # Sort removed — re-run search to restore natural order
            self._run_search()
        else:
            self._apply_sort()
            self._page = 0
            self._load_page()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "sg-table" and event.row_key:
            self._last_edited_id = str(event.row_key.value)
            self.app.push_screen(EditJobScreen(self._last_edited_id))

    def _clear_search(self) -> None:
        self.query_one("#sg-q",      Input ).value = ""
        self.query_one("#sg-status", Select).clear()
        self.query_one("#sg-type",   Select).clear()
        self.query_one("#sg-priority", Select).clear()
        self._run_search()

    def action_focus_search(self) -> None:
        self.query_one("#sg-q", Input).focus()

    def action_do_search(self) -> None:
        self._run_search()

    def action_go_back(self) -> None:
        self.app.pop_screen()

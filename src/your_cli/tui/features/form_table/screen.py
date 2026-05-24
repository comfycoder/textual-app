"""Demo: Form + Table — selecting a grid row populates a tall scrollable form."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import Screen
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

_STATUS_OPTS   = [("Queued","queued"),("Running","running"),("Done","done"),("Failed","failed"),("Pending","pending")]
_TYPE_OPTS     = [("Training","training"),("Validation","validation"),("Export","export"),("Inference","inference"),("Preprocessing","preprocessing")]
_PRIORITY_OPTS = [("Low","low"),("Medium","medium"),("High","high"),("Critical","critical")]
_TENANT_OPTS   = [("JHU","jhu"),("UNC","unc"),("Mayo","mayo"),("Stanford","stanford")]
_ENV_OPTS      = [("Production","prod"),("Staging","staging"),("Development","dev")]

_STATUS_COLORS = {"queued":"yellow","running":"cyan","done":"green","failed":"red","pending":"dim"}
_PRI_COLORS    = {"low":"dim","medium":"yellow","high":"red","critical":"bold red"}

random.seed(55)

_SUBMITTERS = ["alice@jhu.edu","bob@unc.edu","carol@mayo.org","dave@stanford.edu","eve@jhu.edu"]
_TAGS_POOL  = ["baseline","nightly","ablation","prod","dev","manual","scheduled","experiment"]

_RECORDS = [
    {
        "id":          f"wi-{i:03d}",
        "tenant":      random.choice([v for _,v in _TENANT_OPTS]),
        "type":        random.choice([v for _,v in _TYPE_OPTS]),
        "status":      random.choice([v for _,v in _STATUS_OPTS]),
        "priority":    random.choice([v for _,v in _PRIORITY_OPTS]),
        "environment": random.choice([v for _,v in _ENV_OPTS]),
        "submitted_by":random.choice(_SUBMITTERS),
        "node":        f"gpu-node-{random.randint(1,8):02d}",
        "max_jobs":    str(random.randint(1,8)),
        "timeout_min": str(random.randint(10,120)),
        "gpu_required":random.choice([True,False]),
        "auto_retry":  random.choice([True,False]),
        "tags":        ", ".join(random.sample(_TAGS_POOL, random.randint(0,3))),
        "notes":       random.choice([
            "Baseline run","Nightly batch","Ablation study",
            "Prod deployment","Dev test","Manual trigger","",
        ]),
        "description": random.choice([
            "Full training run on the preprocessed dataset with early stopping.",
            "Validate the previous checkpoint against the held-out test set.",
            "Export the model to ONNX format for deployment.",
            "",
        ]),
    }
    for i in range(1, 21)
]


class FormTableDemoScreen(Screen[None]):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save",    "Save"),
        Binding("ctrl+n", "new_rec", "New"),
    ]

    _dirty: reactive[bool]  = reactive(False)
    _editing_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="ft-body"):

            # ── Form ──────────────────────────────────────────────
            with Vertical(id="ft-form"):
                yield Static(
                    "[b]Job Record[/b]  "
                    "[dim]scroll the page to see all fields and the table below[/dim]",
                    id="ft-form-title",
                )
                yield Rule()

                # Row 1: ID / Tenant / Type
                yield Static("[dim]Identity[/dim]", classes="ft-section")
                with Horizontal(classes="ft-row"):
                    with Vertical(classes="ft-field"):
                        yield Label("Job ID  [dim](read-only)[/dim]")
                        yield Static("—", id="ft-id-display", classes="ft-id")
                    with Vertical(classes="ft-field"):
                        yield Label("Tenant")
                        yield Input(id="ft-tenant")
                    with Vertical(classes="ft-field"):
                        yield Label("Type")
                        yield Select(_TYPE_OPTS, prompt="Select…", id="ft-type")

                yield Rule(line_style="dashed")

                # Row 2: Status / Priority / Environment
                yield Static("[dim]State[/dim]", classes="ft-section")
                with Horizontal(classes="ft-row"):
                    with Vertical(classes="ft-field"):
                        yield Label("Status")
                        yield Select(_STATUS_OPTS, prompt="Select…", id="ft-status")
                    with Vertical(classes="ft-field"):
                        yield Label("Priority")
                        yield Select(_PRIORITY_OPTS, prompt="Select…", id="ft-priority")
                    with Vertical(classes="ft-field"):
                        yield Label("Environment")
                        yield Select(_ENV_OPTS, prompt="Select…", id="ft-env")

                yield Rule(line_style="dashed")

                # Row 3: Submitted by / Node / Max jobs / Timeout
                yield Static("[dim]Execution[/dim]", classes="ft-section")
                with Horizontal(classes="ft-row"):
                    with Vertical(classes="ft-field"):
                        yield Label("Submitted by")
                        yield Input(id="ft-submitted-by")
                    with Vertical(classes="ft-field"):
                        yield Label("Worker node")
                        yield Input(id="ft-node")
                with Horizontal(classes="ft-row"):
                    with Vertical(classes="ft-field"):
                        yield Label("Max concurrent jobs  [dim]1–20[/dim]")
                        yield Input(id="ft-max-jobs", type="integer")
                    with Vertical(classes="ft-field"):
                        yield Label("Timeout  [dim](minutes)[/dim]")
                        yield Input(id="ft-timeout", type="integer")
                    with Vertical(classes="ft-field ft-field-toggles"):
                        yield Label("Options")
                        with Horizontal(classes="ft-toggle-row"):
                            yield Switch(id="ft-gpu")
                            yield Label("GPU required", classes="ft-toggle-label")
                        with Horizontal(classes="ft-toggle-row"):
                            yield Switch(id="ft-retry")
                            yield Label("Auto-retry", classes="ft-toggle-label")

                yield Rule(line_style="dashed")

                # Row 4: Tags / Notes / Description
                yield Static("[dim]Metadata[/dim]", classes="ft-section")
                with Horizontal(classes="ft-row"):
                    with Vertical(classes="ft-field"):
                        yield Label("Tags  [dim](comma-separated)[/dim]")
                        yield Input(id="ft-tags")
                    with Vertical(classes="ft-field"):
                        yield Label("Notes")
                        yield Input(id="ft-notes")
                with Vertical(classes="ft-field ft-field-full"):
                    yield Label("Description")
                    yield Input(id="ft-description")

                yield Rule()

                # Actions
                with Horizontal(id="ft-form-actions"):
                    yield Button("Save",  variant="primary", id="btn-ft-save", disabled=True)
                    yield Button("New",   id="btn-ft-new")
                    yield Button("Clear", id="btn-ft-clear")
                    yield Static("", id="ft-status-msg")

            # ── Table ──────────────────────────────────────────────
            with Vertical(id="ft-table-area"):
                yield Static(
                    "[dim]↑↓ navigate · selecting a row populates the form above[/dim]",
                    id="ft-table-hint",
                )
                yield DataTable(id="ft-table", cursor_type="row")

        yield Footer()

    # ── Mount ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        tbl = self.query_one("#ft-table", DataTable)
        tbl.add_columns("ID", "Tenant", "Type", "Status", "Priority", "Env", "Submitted by", "Tags")
        for rec in _RECORDS:
            self._add_table_row(tbl, rec)
        tbl.focus()
        self._populate_form(_RECORDS[0])

    def _add_table_row(self, tbl: DataTable, rec: dict) -> None:
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
        )

    # ── Row → form ────────────────────────────────────────────────

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "ft-table" and event.row_key:
            rec = next((r for r in _RECORDS if r["id"] == event.row_key.value), None)
            if rec:
                self._populate_form(rec)

    def _populate_form(self, rec: dict) -> None:
        self._editing_id = rec["id"]
        self.query_one("#ft-id-display",   Static).update(f"[b]{rec['id']}[/b]")
        self.query_one("#ft-tenant",       Input).value  = rec["tenant"]
        self.query_one("#ft-type",         Select).value = rec["type"]
        self.query_one("#ft-status",       Select).value = rec["status"]
        self.query_one("#ft-priority",     Select).value = rec["priority"]
        self.query_one("#ft-env",          Select).value = rec["environment"]
        self.query_one("#ft-submitted-by", Input).value  = rec["submitted_by"]
        self.query_one("#ft-node",         Input).value  = rec["node"]
        self.query_one("#ft-max-jobs",     Input).value  = rec["max_jobs"]
        self.query_one("#ft-timeout",      Input).value  = rec["timeout_min"]
        self.query_one("#ft-gpu",          Switch).value = rec["gpu_required"]
        self.query_one("#ft-retry",        Switch).value = rec["auto_retry"]
        self.query_one("#ft-tags",         Input).value  = rec["tags"]
        self.query_one("#ft-notes",        Input).value  = rec["notes"]
        self.query_one("#ft-description",  Input).value  = rec["description"]
        self._dirty = False
        self._update_save_btn()
        self.query_one("#ft-status-msg", Static).update("")

    # ── Dirty tracking ────────────────────────────────────────────

    def on_input_changed(self, _: Input.Changed) -> None:
        if self._editing_id:
            self._dirty = True
            self._update_save_btn()

    def on_select_changed(self, _: Select.Changed) -> None:
        if self._editing_id:
            self._dirty = True
            self._update_save_btn()

    def on_switch_changed(self, _: Switch.Changed) -> None:
        if self._editing_id:
            self._dirty = True
            self._update_save_btn()

    def _update_save_btn(self) -> None:
        self.query_one("#btn-ft-save", Button).disabled = not (self._editing_id and self._dirty)

    # ── Save ──────────────────────────────────────────────────────

    def action_save(self) -> None:
        self.query_one("#btn-ft-save", Button).press()

    def _save(self) -> None:
        if not self._editing_id:
            return
        rec = next((r for r in _RECORDS if r["id"] == self._editing_id), None)
        if not rec:
            return

        tenant  = self.query_one("#ft-tenant",       Input).value.strip()
        jtype   = self.query_one("#ft-type",         Select).value
        status  = self.query_one("#ft-status",       Select).value
        pri     = self.query_one("#ft-priority",     Select).value
        env     = self.query_one("#ft-env",          Select).value

        if not tenant or any(v is Select.BLANK for v in (jtype, status, pri, env)):
            self.query_one("#ft-status-msg", Static).update("[red]Complete all required fields[/red]")
            return

        rec.update({
            "tenant":       tenant,
            "type":         jtype,
            "status":       status,
            "priority":     pri,
            "environment":  env,
            "submitted_by": self.query_one("#ft-submitted-by", Input).value.strip(),
            "node":         self.query_one("#ft-node",         Input).value.strip(),
            "max_jobs":     self.query_one("#ft-max-jobs",     Input).value.strip(),
            "timeout_min":  self.query_one("#ft-timeout",      Input).value.strip(),
            "gpu_required": self.query_one("#ft-gpu",          Switch).value,
            "auto_retry":   self.query_one("#ft-retry",        Switch).value,
            "tags":         self.query_one("#ft-tags",         Input).value.strip(),
            "notes":        self.query_one("#ft-notes",        Input).value.strip(),
            "description":  self.query_one("#ft-description",  Input).value.strip(),
        })

        tbl = self.query_one("#ft-table", DataTable)
        sc, pc = _STATUS_COLORS.get(status,"white"), _PRI_COLORS.get(pri,"white")
        rk = self._editing_id
        cols = tbl.ordered_columns
        tbl.update_cell(rk, cols[1].key, tenant)
        tbl.update_cell(rk, cols[2].key, jtype)
        tbl.update_cell(rk, cols[3].key, f"[{sc}]{status}[/{sc}]")
        tbl.update_cell(rk, cols[4].key, f"[{pc}]{pri}[/{pc}]")
        tbl.update_cell(rk, cols[5].key, env)
        tbl.update_cell(rk, cols[7].key, rec["tags"] or "[dim]—[/dim]")

        self._dirty = False
        self._update_save_btn()
        self.query_one("#ft-status-msg", Static).update(f"[green]✓  {rk} saved[/green]")
        self.notify(f"{rk} updated", title="Saved", severity="information")

    # ── New / Clear ───────────────────────────────────────────────

    def _clear_form(self) -> None:
        self._editing_id = None
        self._dirty = False
        self.query_one("#ft-id-display", Static).update("—")
        for wid in ("#ft-tenant","#ft-submitted-by","#ft-node","#ft-max-jobs",
                    "#ft-timeout","#ft-tags","#ft-notes","#ft-description"):
            self.query_one(wid, Input).value = ""
        for wid in ("#ft-type","#ft-status","#ft-priority","#ft-env"):
            self.query_one(wid, Select).clear()
        self.query_one("#ft-gpu",   Switch).value = False
        self.query_one("#ft-retry", Switch).value = False
        self._update_save_btn()
        self.query_one("#ft-status-msg", Static).update("")

    def action_new_rec(self) -> None:
        self._clear_form()
        self.query_one("#ft-tenant", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-ft-save":
                self._save()
            case "btn-ft-new":
                self.action_new_rec()
            case "btn-ft-clear":
                self._clear_form()

    def action_go_back(self) -> None:
        self.app.pop_screen()

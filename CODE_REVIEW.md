# Code Review — textual-app session diff

**Scope:** 6 commits, 2026-05-24 → 2026-05-25  
**Range:** `9e5f096..65589ff` (HEAD~6..HEAD)  
**Effort:** High — 3 independent finder angles × verify pass  
**Reviewer:** Claude Sonnet

---

## Commits reviewed

| Hash | Message |
|------|---------|
| `65589ff` | fix: left-justify PaginationBar controls |
| `895389a` | fix: remove redundant result count from search grid pagination bar |
| `f5ae8a5` | refactor: PaginationBar widget + unified route registry |
| `0d1b0be` | harden: Paginator page_size guard + action_go_back super() chain |
| `acc88f1` | New docs (CONTEXT.md, ADR-0001) |
| `9e5f096` | fix: replace Select.BLANK checks with isinstance(v, str) in 5 screens |

---

## Summary of changes

The session addressed three classes of work:

1. **Correctness fixes** — replaced all `Select.BLANK` sentinel comparisons with `isinstance(v, str)` across five screens; added a `Paginator.__post_init__` guard against zero `page_size`; fixed `action_go_back` in `log_stream` and `workers` to chain through `super()` instead of calling `pop_screen()` directly.

2. **Architecture** — extracted a reusable `PaginationBar` widget (eliminating ~12 lines of duplicated button-disable + label-update boilerplate per screen); unified the route registry so `routes.py` is the single source of truth for both navigation and gallery display, eliminating the dual-maintenance obligation between `routes.py` and `GalleryScreen.DEMOS`.

3. **Documentation** — added `CONTEXT.md` domain glossary and `ADR-0001` for parameterised child screens; updated `CLAUDE.md` to reflect the new one-file demo registration process.

---

## Findings

### F-1 — CONFIRMED · Medium · Documentation

**File:** `CONTEXT.md:75`  
**Summary:** Example dialogue still instructs developers to add an entry to `GalleryScreen.DEMOS`, which was deleted in this session.

**Detail:**  
`CONTEXT.md` contains an example dialogue where the "Domain expert" says:

> *"add a `register()` call in `routes.py` plus an entry in `GalleryScreen.DEMOS`"*

`GalleryScreen.DEMOS` no longer exists. The gallery list is now built by `get_gallery_demos()` called in `GalleryScreen.__init__`. Any developer following the CONTEXT.md example will attempt to append to a deleted class attribute, silently fail (the append creates an instance attribute that is never read), and see their demo absent from the gallery with no error.

`CLAUDE.md` was correctly updated to say "two touch-points", but `CONTEXT.md` was not.

**Fix:** Update the example dialogue in `CONTEXT.md` to remove the DEMOS step. Replace with: *"add a `register()` call with `display_name=` and `description=` in `routes.py` — that's the only file to edit."*

---

### F-2 — CONFIRMED · Medium · Logic

**File:** `src/your_cli/tui/features/inline_edit/screen.py` ~line 107  
**Summary:** Clearing a Select in the edit panel silently preserves the old field value — users cannot clear tenant or status once set.

**Detail:**  
`_save_edit()` uses:

```python
v = self.query_one("#edit-tenant", Select).value
if isinstance(v, str):
    item["tenant"] = v
```

The guard was introduced to fix the `Select.BLANK` bug (correct for filter screens where "no selection" means "don't filter"). In an *edit form*, "no selection" most likely means "clear the field" or should trigger a validation error. Instead, the old value is silently preserved. The user clicks Save and sees no indication that the clear had no effect.

**Fix:** Add an `else` branch that either clears the field (`item["tenant"] = ""`) or adds a validation error, consistent with the form's intended semantics.

---

### F-3 — CONFIRMED · Low · Async lifecycle

**Files:** `src/your_cli/tui/features/log_stream/screen.py:96`, `src/your_cli/tui/features/workers/screen.py:98`  
**Summary:** Async `@work` workers may execute one more iteration against detached widgets after `pop_screen()` is called.

**Detail:**  
In `log_stream`:

```python
def action_go_back(self) -> None:
    self._streaming = False       # (1) flag cleared
    super().action_go_back()      # (2) pop_screen() called
```

The `_stream_logs` worker checks `while self._streaming` only at the top of its loop. If the worker is sleeping in `await asyncio.sleep(...)` when (1) executes, it resumes after (2), calls `log.write(...)` on the now-orphaned `RichLog` widget, and then exits on the next loop-top check. Textual typically handles writes to detached widgets gracefully, but it is not guaranteed across all versions.

The same pattern exists in `workers/screen.py`: `_active.clear()` is called, then `super().action_go_back()`. A sleeping `_run_job` worker resumes after `pop_screen()` and calls `pb.advance(100 / _STEPS)` on the detached `ProgressBar` before the next iteration's early-return check fires.

**Fix:** Cancel the worker(s) explicitly before calling `super()`. In `log_stream`, `self._stream_logs()` returns a `Worker`; store it in `self._worker` and call `self._worker.cancel()` before `super().action_go_back()`. In `workers`, iterate `self._active` and cancel each named worker, or use `self.workers.cancel_all()`.

---

### F-4 — Plausible · Low · Design / future-proofing

**File:** `src/your_cli/tui/features/search_grid/screen.py:230` (and `pagination/screen.py:75`)  
**Summary:** `on_pagination_bar_navigated` has no identity guard and uses `getattr` with an unguarded action string.

**Detail (identity):**  
```python
def on_pagination_bar_navigated(self, event: PaginationBar.Navigated) -> None:
    if getattr(self._pager, event.action)():
        self._load_page()
```

There is no check that `event` originated from *this screen's* `PaginationBar`. A future refactor adding a second `PaginationBar` (e.g. a header and a footer navigation bar) could cause `_load_page()` to fire twice per click — once from each bar's `Navigated` message — skipping a page per click. The old `on_button_pressed` with explicit `id` strings had no such ambiguity.

**Detail (getattr):**  
`event.action` is a `Literal["first", "prev", "next", "last"]` and `_MAP` in `PaginationBar.on_button_pressed` only ever produces those four values, so this cannot fail today. If `_MAP` were accidentally modified (typo changing `"prev"` to `"back"`), `getattr(self._pager, "back")()` raises `AttributeError` swallowed silently by Textual, leaving the user with a frozen page and no feedback.

**Fix (identity):** Add `event.stop()` is already handled inside `PaginationBar` so double-firing from two bars is not the current concern — but add a widget-identity check if a second bar is ever added: `if event.control is not self.query_one(PaginationBar): return`.

**Fix (getattr):** Prefer explicit dispatch:
```python
_NAV = {"first": self._pager.first, "prev": self._pager.prev,
        "next": self._pager.next, "last": self._pager.last}
if nav := _NAV.get(event.action):
    if nav():
        self._load_page()
```

---

## What was done well

- **`isinstance(v, str)` sweep** was thorough: Grep confirmed zero remaining `Select.BLANK` occurrences across all five affected screens, and the reasoning in CLAUDE.md is documented for future developers.
- **`Paginator.__post_init__` guard** is minimal and correct — raises `ValueError` immediately at construction rather than at the first arithmetic operation, giving a clear stack trace.
- **`PaginationBar` design** cleanly encapsulates the four buttons + label + `event.stop()` in one place. The `Navigated.action` field matching `Paginator` method names (`getattr(pager, event.action)()`) is a nice convention that keeps handler code to one line.
- **`_Route` NamedTuple** is the right type for `_REGISTRY` values — immutable, structured, and mypy-friendly. `get_gallery_demos()` correctly filters on `display_name is not None` and passes mypy strict mode.
- **`super().action_go_back()` fix** correctly threads the call through `FeatureScreen.action_go_back()` rather than calling `self.app.pop_screen()` directly, which preserves any future logic added to the base class.

---

## Verdict

**Ship with fixes.** F-1 (stale CONTEXT.md) is a one-line doc fix. F-2 (silent no-op on clear) needs a product decision about inline-edit semantics before the code fix. F-3 (worker lifecycle) is a real bug but low-impact in practice — Textual handles detached widget writes without crash in current versions. F-4 is a design note for when the codebase grows.

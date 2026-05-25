# Parameterised child screens bypass the router

Data-bound child screens (`EditJobScreen`, `DetailScreen`) are pushed directly
via `app.push_screen(ScreenClass(arg))` rather than through `navigate()`.
`navigate()` is the seam for top-level, gallery-reachable screens only.

## Why

`EditJobScreen` requires a `record_id` at construction time; `DetailScreen`
requires a work-item dict.  Routing them through `navigate(key)` would require
one of:

- **`**kwargs` on `navigate()`** — the registry loses knowledge of what each
  screen needs; wrong arguments crash at runtime instead of failing at the type
  checker.
- **App-level state store** — caller sets `app.pending_record_id` before
  navigating, screen reads it in `on_mount`.  Effectively a global variable;
  fragile under rapid navigation and an invisible coupling between two modules.

The constructor-as-contract pattern (`push_screen(EditJobScreen(record_id))`) is
typed, local, and explicit.  Applying the deletion test: routing these screens
through the registry would not reduce complexity — it would only move the record
ID somewhere harder to see.

## Boundary rule

`navigate()` is for **standalone feature screens** (every entry in
`routes.py` / `GalleryScreen.DEMOS`).  A screen that is only reachable as a
modal continuation of another screen, and that requires caller-supplied data to
render, should be pushed directly.

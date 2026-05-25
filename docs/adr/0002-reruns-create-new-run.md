# Run rerun creates a new Run; stage retry does not

This ADR covers **Run-level rerun** only — retrying an entire failed Run by
submitting all its pipeline stages again.  It does not cover **stage retry**
(transitioning a single failed work item back to `queued` within the existing
Run), which is a separate, finer-grained operation that creates no new entity.

When a Run is rerun, the platform creates a **new Run** whose `parent_run_id`
points to the original.  The original Run and its work items are never mutated
after the Run reaches a terminal status (`done` or `failed`).

## Why

A Run is a historical record of a submission — once it is terminal it must not
change state.  Three alternative approaches were considered:

- **Option A — new work item inside the original Run.**  The original run would
  need to re-enter a non-terminal status to accommodate the new item, then
  settle again.  This creates a "done but still active" paradox: the run is
  simultaneously a closed record and an ongoing container.  Consumers that
  cached the terminal status would have stale data with no safe invalidation
  point.

- **Option B — new Run with `parent_run_id` (chosen).**  Each retry produces a
  clean, independently addressable Run.  The original Run's status is frozen.
  Retry lineage is fully navigable by following the `parent_run_id` chain.
  Cache invalidation is simple: a terminal Run never needs re-fetching.

- **Option C — standalone work item with no parent Run.**  The Tenant → Run →
  Work Item hierarchy collapses for retried work.  Screens that scope their view
  by `run_id` cannot include the retried item without special-casing "orphan"
  work items.

## Consequences

- `Run` carries `parent_run_id: str | None`; `None` for first-time submissions.
- A Run's status never transitions away from `done` or `failed`; the repository
  may cache terminal Runs indefinitely.
- Retry lineage is navigable by walking `parent_run_id` chains; the repository
  should expose a helper for this (e.g. `get_run_lineage(run_id)`).
- Screens that show a Run's history implicitly show one attempt only; a
  "retry history" view must explicitly walk the lineage chain.

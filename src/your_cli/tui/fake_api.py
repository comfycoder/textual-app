"""Fake API client — hard-coded in-memory store that satisfies the ApiClient Protocol.

Swap for the real generated client (``your_cli.client``) in ``app.py`` once
the OpenAPI client has been generated.  All methods are async and include a
small simulated delay so the async fetch patterns are exercised during
development.

Data is generated at import time with a fixed seed, so it is deterministic
across restarts.  Mutation via ``update_work_item_status`` modifies the
in-memory store — changes persist for the lifetime of the process.
"""

from __future__ import annotations

import asyncio
import dataclasses
import random
from datetime import date, datetime, timedelta, timezone

from your_cli.tui.models import Run, WorkItem

# ── Seed data constants ────────────────────────────────────────────────────────

_TENANTS    = ["jhu", "unc", "mayo", "stanford"]
_RUN_STATUSES  = (
    ["done"] * 10 + ["failed"] * 5 + ["running"] * 4 + ["queued"] * 3 + ["pending"] * 2
)
_ITEM_TYPES    = ["training", "validation", "export", "inference", "preprocessing"]
_PRIORITIES    = ["low"] * 2 + ["medium"] * 4 + ["high"] * 3 + ["critical"]
_ENVIRONMENTS  = ["prod"] * 5 + ["staging"] * 3 + ["dev"] * 2
_SUBMITTERS    = ["jsmith", "mwang", "rdavis", "kpatel", "lchen", "abrown", "slee", "tkim"]
_TAGS          = ["", "urgent", "batch", "gpu", "cpu-only", "nightly", "ci", "manual", "scheduled", ""]

_NOW = datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc)

# ── Deterministic data generation ─────────────────────────────────────────────

def _item_status(run_status: str, idx: int, n: int, rng: random.Random) -> str:
    """Return a plausible work item status given the owning Run's status."""
    if run_status == "done":
        return "done"
    if run_status in ("queued", "pending"):
        return rng.choice(["queued", "pending"])
    if run_status == "running":
        done_up_to = max(0, int(n * rng.uniform(0.3, 0.8)))
        if idx < done_up_to:   return "done"
        if idx == done_up_to:  return "running"
        return "queued"
    if run_status == "failed":
        done_up_to = max(0, int(n * rng.uniform(0.3, 0.9)))
        if idx < done_up_to:   return "done"
        if idx == done_up_to:  return "failed"
        return "pending"
    return "queued"


def _generate() -> tuple[
    dict[str, Run],
    dict[str, list[Run]],
    dict[str, list[WorkItem]],
    dict[str, WorkItem],
]:
    rng = random.Random(42)

    runs_by_id:     dict[str, Run]             = {}
    runs_by_tenant: dict[str, list[Run]]       = {t: [] for t in _TENANTS}
    items_by_run:   dict[str, list[WorkItem]]  = {}
    items_by_id:    dict[str, WorkItem]        = {}

    run_counter  = 1
    item_counter = 1

    for _ in range(160):
        tenant    = rng.choice(_TENANTS)
        days_ago  = rng.randint(0, 89)
        hours_ago = rng.randint(0, 23)
        submitted = _NOW - timedelta(days=days_ago, hours=hours_ago)
        status    = rng.choice(_RUN_STATUSES)
        run_id    = f"run-{run_counter:04d}"
        run_counter += 1

        # ~10% of runs are reruns of an earlier run for the same tenant
        parent_run_id: str | None = None
        tenant_runs = runs_by_tenant[tenant]
        if tenant_runs and rng.random() < 0.10:
            parent_run_id = rng.choice(tenant_runs[:min(10, len(tenant_runs))]).run_id

        run = Run(
            run_id=run_id,
            tenant=tenant,
            status=status,
            submitted_at=submitted,
            parent_run_id=parent_run_id,
        )
        runs_by_id[run_id]  = run
        tenant_runs.append(run)

        # Work items for this run
        n_items = rng.randint(2, 12)
        items: list[WorkItem] = []
        for j in range(n_items):
            wi_id = f"wi-{item_counter:04d}"
            item_counter += 1
            wi = WorkItem(
                id=wi_id,
                run_id=run_id,
                tenant=tenant,
                type=rng.choice(_ITEM_TYPES),
                status=_item_status(status, j, n_items, rng),
                priority=rng.choice(_PRIORITIES),
                environment=rng.choice(_ENVIRONMENTS),
                submitted_by=rng.choice(_SUBMITTERS),
                tags=rng.choice(_TAGS),
            )
            items.append(wi)
            items_by_id[wi_id] = wi

        items_by_run[run_id] = items

    # Sort each tenant's runs newest-first
    for tenant in _TENANTS:
        runs_by_tenant[tenant].sort(key=lambda r: r.submitted_at, reverse=True)

    return runs_by_id, runs_by_tenant, items_by_run, items_by_id


_runs_by_id, _runs_by_tenant, _items_by_run, _items_by_id = _generate()


# ── Fake client ────────────────────────────────────────────────────────────────

_DELAY = 0.05  # seconds — simulates network latency


class FakeApiClient:
    """In-memory implementation of the ApiClient Protocol.

    All write operations mutate the module-level stores, so changes are
    visible to subsequent reads within the same process lifetime.
    """

    # ── Run reads ──────────────────────────────────────────────────────────

    async def get_recent_runs(self, tenant: str, limit: int) -> list[Run]:
        """Return the *limit* most recent Runs for *tenant*, newest first."""
        await asyncio.sleep(_DELAY)
        return _runs_by_tenant.get(tenant, [])[:limit]

    async def get_runs(
        self,
        tenant:    str,
        date_from: date,
        date_to:   date,
        page:      int,
        page_size: int,
    ) -> tuple[list[Run], int]:
        """Return a page of Runs for *tenant* within the given date range.

        Returns ``(page_runs, total_matching)`` where ``total_matching`` is the
        full count before slicing (for the caller's ``Paginator``).
        """
        await asyncio.sleep(_DELAY)
        from_dt = datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc)
        to_dt   = datetime(date_to.year,   date_to.month,   date_to.day,
                           23, 59, 59, tzinfo=timezone.utc)
        filtered = [
            r for r in _runs_by_tenant.get(tenant, [])
            if from_dt <= r.submitted_at <= to_dt
        ]
        total = len(filtered)
        start = page * page_size
        return filtered[start : start + page_size], total

    async def get_run(self, tenant: str, run_id: str) -> Run:
        """Fetch a single Run by ID.  Raises ``KeyError`` if not found."""
        await asyncio.sleep(_DELAY)
        run = _runs_by_id.get(run_id)
        if run is None or run.tenant != tenant:
            raise KeyError(f"Run {run_id!r} not found for tenant {tenant!r}")
        return run

    # ── Work item reads ────────────────────────────────────────────────────

    async def get_work_items(self, tenant: str, run_id: str) -> list[WorkItem]:
        """Return all work items for *run_id*.  Full list — no server-side cursor."""
        await asyncio.sleep(_DELAY)
        items = _items_by_run.get(run_id, [])
        if items and items[0].tenant != tenant:
            raise KeyError(f"Run {run_id!r} not found for tenant {tenant!r}")
        return list(items)

    # ── Work item writes ───────────────────────────────────────────────────

    async def update_work_item_status(
        self, tenant: str, work_item_id: str, new_status: str
    ) -> WorkItem:
        """Persist a status change on a work item and return the updated record."""
        await asyncio.sleep(_DELAY)
        item = _items_by_id.get(work_item_id)
        if item is None or item.tenant != tenant:
            raise KeyError(f"Work item {work_item_id!r} not found for tenant {tenant!r}")
        updated = dataclasses.replace(item, status=new_status)
        _items_by_id[work_item_id] = updated
        _items_by_run[updated.run_id] = [
            updated if wi.id == work_item_id else wi
            for wi in _items_by_run.get(updated.run_id, [])
        ]
        return updated

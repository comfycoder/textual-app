"""Repository — the single read/write gateway for Runs and work items.

All operational screens access live data through ``self.app.repository``.
Demo screens hold their own seed data and do not use this module.

Architecture notes
------------------
* The ``ApiClient`` Protocol defines the interface both ``FakeApiClient`` and
  the real generated client must satisfy.  The repository is agnostic to which
  is injected.
* Terminal Runs (``done`` or ``failed``) are cached indefinitely — they are
  immutable once the API sets them terminal.
* Work items for a terminal Run are also cached indefinitely once fetched.
  Active-Run item caches are always re-fetched on the next call.
* ``get_run_with_items`` fires both fetches concurrently so callers pay one
  round-trip latency even though the API uses separate endpoints.
* Status transitions are validated against the whitelist before the API call
  so the user receives a clear error rather than an opaque 4xx response.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Protocol

from your_cli.tui.models import Run, WorkItem

# ── Valid work item status transitions ─────────────────────────────────────────
#
# ``done`` is intentionally absent as a source — completed stages are immutable
# from the TUI's perspective.  The API may permit other transitions; the TUI
# enforces only the subset that makes semantic sense (see CONTEXT.md §Stage retry).

_VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued":  frozenset({"failed"}),           # cancel
    "running": frozenset({"failed"}),           # force-abort
    "failed":  frozenset({"queued"}),           # stage retry
    "pending": frozenset({"queued"}),           # unblock
    "done":    frozenset(),                     # immutable
}


# ── ApiClient Protocol ─────────────────────────────────────────────────────────

class ApiClient(Protocol):
    """Structural interface satisfied by both ``FakeApiClient`` and the real client.

    Every method accepts ``tenant`` as a routing parameter — the API uses it to
    select the correct tenant database shard even though ``run_id`` values are
    globally unique.
    """

    async def get_recent_runs(self, tenant: str, limit: int) -> list[Run]:
        """Return the *limit* most recent Runs for *tenant*, newest first."""
        ...

    async def get_runs(
        self,
        tenant:    str,
        date_from: date,
        date_to:   date,
        page:      int,
        page_size: int,
    ) -> tuple[list[Run], int]:
        """Return ``(page_runs, total_matching)`` within the date range."""
        ...

    async def get_run(self, tenant: str, run_id: str) -> Run:
        """Fetch a single Run's metadata by ID."""
        ...

    async def get_work_items(self, tenant: str, run_id: str) -> list[WorkItem]:
        """Return all work items for *run_id* in a single response."""
        ...

    async def update_work_item_status(
        self, tenant: str, work_item_id: str, new_status: str
    ) -> WorkItem:
        """Persist a status change and return the updated work item."""
        ...


# ── Repository ─────────────────────────────────────────────────────────────────

class Repository:
    """Caching gateway over the API client.

    Instantiated once on the ``App`` and accessed by screens via
    ``self.app.repository``.

    Caching rules
    ~~~~~~~~~~~~~
    * Terminal Runs (``done`` / ``failed``) → cached indefinitely.
    * Non-terminal Runs → always re-fetched.
    * Work items for a terminal Run → cached indefinitely once fetched.
    * Work items for a non-terminal Run → always re-fetched.
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client
        # run_id → Run (terminal Runs only)
        self._run_cache:   dict[str, Run]            = {}
        # run_id → list[WorkItem] (terminal Runs only)
        self._items_cache: dict[str, list[WorkItem]] = {}

    # ── Internal helpers ───────────────────────────────────────────────────

    @staticmethod
    def _is_terminal(run: Run) -> bool:
        return run.status in ("done", "failed")

    def _cache_run(self, run: Run) -> None:
        if self._is_terminal(run):
            self._run_cache[run.run_id] = run

    def _cache_items(self, run_id: str, items: list[WorkItem]) -> None:
        cached_run = self._run_cache.get(run_id)
        if cached_run and self._is_terminal(cached_run):
            self._items_cache[run_id] = items

    # ── Run reads ──────────────────────────────────────────────────────────

    async def get_recent_runs(self, tenant: str, limit: int = 5) -> list[Run]:
        """Return the *limit* most recent Runs for *tenant*.

        Used by the run dashboard.  Fires one API call per tenant; callers
        that need all tenants should gather these concurrently.
        """
        runs = await self._client.get_recent_runs(tenant, limit)
        for run in runs:
            self._cache_run(run)
        return runs

    async def get_runs(
        self,
        tenant:    str,
        date_from: date,
        date_to:   date,
        page:      int       = 0,
        page_size: int       = 20,
    ) -> tuple[list[Run], int]:
        """Return a page of Runs for *tenant* within the date range.

        Returns ``(page_runs, total_matching)`` — pass ``total_matching`` to
        ``Paginator(total=...)`` after the first fetch.

        Used by the run history screen.
        """
        runs, total = await self._client.get_runs(tenant, date_from, date_to, page, page_size)
        for run in runs:
            self._cache_run(run)
        return runs, total

    async def get_run(self, tenant: str, run_id: str) -> Run:
        """Fetch a single Run, using the cache for terminal Runs."""
        if run_id in self._run_cache:
            return self._run_cache[run_id]
        run = await self._client.get_run(tenant, run_id)
        self._cache_run(run)
        return run

    # ── Work item reads ────────────────────────────────────────────────────

    async def get_work_items(self, tenant: str, run_id: str) -> list[WorkItem]:
        """Return all work items for *run_id*, using the cache for terminal Runs.

        The full list is always returned — work items per Run are bounded
        (~few hundred) so client-side pagination via ``Paginator`` is safe.
        """
        if run_id in self._run_cache and run_id in self._items_cache:
            return self._items_cache[run_id]
        items = await self._client.get_work_items(tenant, run_id)
        self._cache_items(run_id, items)
        return items

    async def get_run_with_items(
        self, tenant: str, run_id: str
    ) -> tuple[Run, list[WorkItem]]:
        """Fetch a Run's metadata and work items concurrently.

        Screens that need both pieces of data (e.g. a Run detail screen) call
        this rather than two sequential awaits.
        """
        run, items = await asyncio.gather(
            self.get_run(tenant, run_id),
            self.get_work_items(tenant, run_id),
        )
        return run, items

    # ── Lineage ────────────────────────────────────────────────────────────

    async def get_run_lineage(self, tenant: str, run_id: str) -> list[Run]:
        """Return the ancestor chain from the original submission to *run_id*.

        The returned list is ordered oldest-first.  For a first-time
        submission with no ``parent_run_id`` the list contains only that Run.
        """
        chain: list[Run] = []
        current_id: str | None = run_id
        while current_id:
            run = await self.get_run(tenant, current_id)
            chain.append(run)
            current_id = run.parent_run_id
        return list(reversed(chain))

    # ── Work item writes ───────────────────────────────────────────────────

    async def update_work_item_status(
        self, tenant: str, work_item_id: str, new_status: str
    ) -> WorkItem:
        """Validate the transition whitelist, then persist the status change.

        Raises ``ValueError`` for disallowed transitions so the caller can
        surface a clear message to the user rather than an API error.

        Updates the in-memory items cache so callers see the change immediately
        without a round-trip re-fetch.
        """
        current = self._find_cached_item(work_item_id)
        if current is not None:
            allowed = _VALID_TRANSITIONS.get(current.status, frozenset())
            if new_status not in allowed:
                raise ValueError(
                    f"Cannot transition work item {work_item_id!r} "
                    f"from {current.status!r} to {new_status!r}. "
                    f"Allowed: {sorted(allowed) or 'none'}"
                )

        updated = await self._client.update_work_item_status(tenant, work_item_id, new_status)

        # Patch the cache entry if present
        cached = self._items_cache.get(updated.run_id)
        if cached is not None:
            self._items_cache[updated.run_id] = [
                updated if wi.id == work_item_id else wi
                for wi in cached
            ]

        return updated

    def _find_cached_item(self, work_item_id: str) -> WorkItem | None:
        """Search all cached item lists for *work_item_id*."""
        for items in self._items_cache.values():
            for item in items:
                if item.id == work_item_id:
                    return item
        return None

"""Domain dataclasses for the AIQ platform entities.

These are the canonical in-memory representations used by the repository and
all operational screens.  Demo screens use their own seed dicts and do not
import from here.

WorkItem fields are intentionally minimal until the real API schema is
confirmed (see Q8 in the grill session).  Do not add fields here until they
are verified against the actual API response shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Run:
    """A single tenant submission — owns one or more work items.

    ``status`` is set by the API; never derived client-side from work item
    statuses.  Once ``status`` is ``"done"`` or ``"failed"`` the Run is
    terminal and may be cached indefinitely.

    ``parent_run_id`` is ``None`` for first-time submissions; set to the
    originating Run's ID for run-level reruns (see ADR-0002).
    """

    run_id:        str
    tenant:        str           # lowercase string key, e.g. "jhu"
    status:        str           # queued | running | done | failed | pending
    submitted_at:  datetime
    parent_run_id: str | None = None


@dataclass(frozen=True)
class WorkItem:
    """A single pipeline stage belonging to a Run.

    ``run_id`` is always non-nullable — work items never exist outside a Run.
    ``tenant`` is a plain string key matching the owning Run's tenant; it is
    not inflated into a Tenant object.

    TODO (Q8): replace placeholder fields with the real API schema once the
    OpenAPI client is generated and the field list is confirmed.
    """

    id:           str
    run_id:       str
    tenant:       str           # lowercase string key
    type:         str           # training | validation | export | inference | preprocessing
    status:       str           # queued | running | done | failed | pending
    priority:     str           # low | medium | high | critical
    environment:  str           # prod | staging | dev
    submitted_by: str
    tags:         str           # TODO (Q8): likely list[str] on the real API

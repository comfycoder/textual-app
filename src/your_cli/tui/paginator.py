"""Pure-Python page-state dataclass.

Use this instead of reimplementing (total // page_size) arithmetic in each
screen that pages through a list.

Example
-------
    pager = Paginator(total=len(records), page_size=20)

    # Navigate
    if pager.next():          # returns True only if page actually changed
        _load_page()

    # Render
    start, end = pager.slice()
    chunk = records[start:end]
    label = f"Page {pager.display_page} of {pager.page_count}"

    # Button states
    prev_btn.disabled = pager.at_first
    next_btn.disabled = pager.at_last
"""

from dataclasses import dataclass


@dataclass
class Paginator:
    """Mutable page-state for a fixed-size list.

    Callers are responsible for calling the screen's render method after
    any navigation call returns True.  The Paginator does no rendering.
    """

    total: int
    page_size: int
    page: int = 0       # 0-based

    def __post_init__(self) -> None:
        if self.page_size < 1:
            raise ValueError(f"page_size must be ≥ 1, got {self.page_size}")

    # ── Derived state ─────────────────────────────────────────────────────────

    @property
    def page_count(self) -> int:
        """Total number of pages (always at least 1)."""
        return max(1, (self.total + self.page_size - 1) // self.page_size)

    @property
    def display_page(self) -> int:
        """1-based page number suitable for display."""
        return self.page + 1

    @property
    def at_first(self) -> bool:
        return self.page == 0

    @property
    def at_last(self) -> bool:
        return self.page >= self.page_count - 1

    # ── Slice ─────────────────────────────────────────────────────────────────

    def slice(self) -> tuple[int, int]:
        """Return (start, end) indices for ``records[start:end]``.

        ``end`` may exceed ``total`` — Python list slicing handles that safely.
        """
        start = self.page * self.page_size
        return start, start + self.page_size

    # ── Navigation ────────────────────────────────────────────────────────────

    def first(self) -> bool:
        """Jump to the first page. Returns True if the page changed."""
        if self.page != 0:
            self.page = 0
            return True
        return False

    def last(self) -> bool:
        """Jump to the last page. Returns True if the page changed."""
        target = self.page_count - 1
        if self.page != target:
            self.page = target
            return True
        return False

    def next(self) -> bool:
        """Advance one page. Returns True if the page changed."""
        if self.page < self.page_count - 1:
            self.page += 1
            return True
        return False

    def prev(self) -> bool:
        """Go back one page. Returns True if the page changed."""
        if self.page > 0:
            self.page -= 1
            return True
        return False

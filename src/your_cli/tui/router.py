"""Lazy screen router.

Usage::

    from your_cli.tui.router import navigate
    navigate(self.app, "dashboard")          # push a registered screen
    navigate(self.app, "searchgrid")         # lazy-imports the module on first use

The registry is populated by ``your_cli.tui.routes`` as a side-effect of
importing it.  ``app.py`` imports ``routes`` before the first ``navigate``
call, so the registry is always ready.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from textual.app import App


class _Route(NamedTuple):
    module_path:  str
    class_name:   str
    display_name: str | None = None   # None → not shown in the gallery
    description:  str | None = None


# Maps route key → _Route.
# Populated exclusively by register() calls in routes.py.
_REGISTRY: dict[str, _Route] = {}


def register(
    key: str,
    module_path: str,
    class_name: str,
    *,
    display_name: str | None = None,
    description:  str | None = None,
) -> None:
    """Register a route.  Called exclusively from routes.py.

    Args:
        key:          Short route identifier used in navigate() calls.
        module_path:  Fully-qualified dotted module path, e.g.
                      ``"your_cli.tui.features.inputs.screen"``.
        class_name:   Name of the Screen subclass inside that module.
        display_name: Human-readable name shown in the gallery list.
                      Omit (or pass None) for non-gallery screens such as
                      child screens pushed directly (EditJobScreen etc.).
        description:  One-line description shown in the gallery detail pane.
                      Ignored when display_name is None.
    """
    _REGISTRY[key] = _Route(module_path, class_name, display_name, description)


def get_gallery_demos() -> list[tuple[str, str, str]]:
    """Return ``(display_name, key, description)`` for every gallery-visible route.

    Routes appear in the same order they were registered (insertion order of
    ``routes.py``), which is the canonical display order for the gallery list.
    Only routes with a ``display_name`` are included.
    """
    return [
        (route.display_name, key, route.description or "")
        for key, route in _REGISTRY.items()
        if route.display_name is not None
    ]


def navigate(app: App[Any], key: str, **kwargs: Any) -> None:
    """Lazy-load the screen module for *key* and push it onto the stack.

    The module is imported the first time the route is navigated to;
    subsequent calls reuse the already-imported module from ``sys.modules``.

    Args:
        app:      The running ``App`` instance (use ``self`` in ``App.on_mount``,
                  or ``self.app`` inside a ``Screen``).
        key:      A route key registered in ``routes.py``.
        **kwargs: Passed verbatim to the ``Screen`` constructor.
    """
    if key not in _REGISTRY:
        app.notify(f"Unknown route: {key!r}", severity="error")
        return
    route = _REGISTRY[key]
    module = importlib.import_module(route.module_path)
    cls = getattr(module, route.class_name)
    app.push_screen(cls(**kwargs))

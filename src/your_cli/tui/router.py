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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.app import App

# Maps route key → (dotted module path, class name).
# Populated exclusively by register() calls in routes.py.
_REGISTRY: dict[str, tuple[str, str]] = {}


def register(key: str, module_path: str, class_name: str) -> None:
    """Register a route.  Called exclusively from routes.py.

    Args:
        key:         Short route identifier used in navigate() calls.
        module_path: Fully-qualified dotted module path, e.g.
                     ``"your_cli.tui.features.inputs.screen"``.
        class_name:  Name of the Screen subclass inside that module.
    """
    _REGISTRY[key] = (module_path, class_name)


def navigate(app: App[Any], key: str, **kwargs: Any) -> None:
    """Lazy-load the screen module for *key* and push it onto the stack.

    The module is imported the first time the route is navigated to;
    subsequent calls reuse the already-imported module from ``sys.modules``.

    Args:
        app:    The running ``App`` instance (use ``self`` in ``App.on_mount``,
                or ``self.app`` inside a ``Screen``).
        key:    A route key registered in ``routes.py``.
        **kwargs: Passed verbatim to the ``Screen`` constructor.
    """
    if key not in _REGISTRY:
        app.notify(f"Unknown route: {key!r}", severity="error")
        return
    module_path, class_name = _REGISTRY[key]
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    app.push_screen(cls(**kwargs))

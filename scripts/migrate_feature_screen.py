"""One-shot migration: replace Screen[None] with FeatureScreen in all demo screens.

Run from the repo root:
    python scripts/migrate_feature_screen.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT    = Path(__file__).parent.parent
FEATURES_DIR = REPO_ROOT / "src" / "your_cli" / "tui" / "features"

# gallery keeps Screen[None] (its Escape quits the app, not pops)
SKIP = {"gallery/screen.py"}

# Only transform these filenames inside the features tree
TARGET_NAMES = {"screen.py", "edit.py", "detail.py"}

# --- patterns ----------------------------------------------------------------

# Escape→go_back as the *only* entry: full BINDINGS line
_RE_SINGLE_BINDINGS = re.compile(
    r'^    BINDINGS = \[Binding\("escape",\s*"go_back",\s*"Back"\)\]\n',
    re.MULTILINE,
)

# Escape→go_back as one of several entries (has a trailing comma)
_RE_MULTI_BINDING_ENTRY = re.compile(
    r'^[ \t]+Binding\("escape",\s*"go_back",\s*"Back"\),\n',
    re.MULTILINE,
)

# action_go_back method (with optional preceding blank line)
_RE_GO_BACK = re.compile(
    r'\n    def action_go_back\(self\) -> None:\n        self\.app\.pop_screen\(\)\n',
)


def transform(text: str) -> str:
    # Only act on files that actually define a Screen[None] subclass
    if "(Screen[None])" not in text:
        return text

    # ── Imports ───────────────────────────────────────────────────────────────
    FEATURE_IMPORT = "from your_cli.tui.feature_screen import FeatureScreen"

    if "from textual.screen import ModalScreen, Screen" in text:
        text = text.replace(
            "from textual.screen import ModalScreen, Screen",
            f"from textual.screen import ModalScreen\n{FEATURE_IMPORT}",
        )
    elif "from textual.screen import Screen, ModalScreen" in text:
        text = text.replace(
            "from textual.screen import Screen, ModalScreen",
            f"from textual.screen import ModalScreen\n{FEATURE_IMPORT}",
        )
    elif "from textual.screen import Screen" in text:
        text = text.replace(
            "from textual.screen import Screen",
            FEATURE_IMPORT,
        )

    # ── Class declarations ────────────────────────────────────────────────────
    text = text.replace("(Screen[None])", "(FeatureScreen)")

    # ── Remove escape→go_back binding ────────────────────────────────────────
    # Single-binding BINDINGS → drop the entire BINDINGS line
    text = _RE_SINGLE_BINDINGS.sub("", text)

    # Multi-binding list → drop just the escape entry
    text = _RE_MULTI_BINDING_ENTRY.sub("", text)

    # ── Remove action_go_back method ─────────────────────────────────────────
    text = _RE_GO_BACK.sub("\n", text)
    # Handle end-of-file with no trailing newline after pop_screen()
    text = re.sub(
        r'\n    def action_go_back\(self\) -> None:\n        self\.app\.pop_screen\(\)$',
        "",
        text,
    )

    return text


changed = []
unchanged = []

for pyfile in sorted(FEATURES_DIR.rglob("*.py")):
    rel = pyfile.relative_to(FEATURES_DIR).as_posix()
    if rel in SKIP:
        continue
    if pyfile.name not in TARGET_NAMES:
        continue

    original = pyfile.read_text(encoding="utf-8")
    updated  = transform(original)

    if updated != original:
        pyfile.write_text(updated, encoding="utf-8")
        changed.append(rel)
    else:
        unchanged.append(rel)

print(f"\nChanged  ({len(changed)}):")
for f in changed:
    print(f"  {f}")

print(f"\nUnchanged ({len(unchanged)}):")
for f in unchanged:
    print(f"  {f}")

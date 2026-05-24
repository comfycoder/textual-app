"""Custom app themes.

Each Theme defines the colour tokens that map to every $primary, $accent,
$background, etc. reference in styles.tcss.  Register them all in app.py and
they become selectable at runtime.
"""

from textual.theme import Theme

NORD = Theme(
    name="nord",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#EBCB8B",
    background="#2E3440",
    surface="#3B4252",
    panel="#434C5E",
    warning="#EBCB8B",
    error="#BF616A",
    success="#A3BE8C",
    dark=True,
)

GRUVBOX = Theme(
    name="gruvbox",
    primary="#83A598",
    secondary="#689D6A",
    accent="#FABD2F",
    background="#282828",
    surface="#32302F",
    panel="#3C3836",
    warning="#FE8019",
    error="#CC241D",
    success="#98971A",
    dark=True,
)

DRACULA = Theme(
    name="dracula",
    primary="#BD93F9",
    secondary="#6272A4",
    accent="#50FA7B",
    background="#282A36",
    surface="#383A59",
    panel="#44475A",
    warning="#FFB86C",
    error="#FF5555",
    success="#50FA7B",
    dark=True,
)

SOLARIZED_LIGHT = Theme(
    name="solarized-light",
    primary="#268BD2",
    secondary="#2AA198",
    accent="#CB4B16",
    background="#FDF6E3",
    surface="#EEE8D5",
    panel="#E0D9C4",
    warning="#B58900",
    error="#DC322F",
    success="#859900",
    dark=False,
)

WARM_LINEN = Theme(
    name="warm-linen",
    # Backgrounds: cream paper, not harsh white
    background="#F4EFE6",
    surface="#EBE4D8",
    panel="#E1D9CB",
    # Accents: chambray blue borders, honey-amber titles
    primary="#4A7FA0",
    secondary="#5A8F78",
    accent="#A0712A",
    # Semantic: warm amber / terracotta / forest green — readable, not aggressive
    warning="#C17D11",
    error="#B03A2E",
    success="#2E7D4F",
    dark=False,
)

# ── AIQ brand themes ─────────────────────────────────────────────────────────
# Sampled from the aiq-solutions.com logo:
#   #8B1A22  deep crimson  — "AIQ" letters and accent dots
#   #3C3C3C  dark charcoal — "Solutions" wordmark
#   #9B9B9B  cool gray     — arc of small dots

AIQ = Theme(
    name="aiq",
    # White/near-white backgrounds — matches the website's clean aesthetic
    background="#F7F7F7",
    surface="#EEECEC",
    panel="#E5E1E1",
    # Brand crimson as primary, charcoal as secondary, dots-gray as a neutral
    primary="#8B1A22",
    secondary="#9B9B9B",
    accent="#6B1218",       # deeper crimson for titles/highlights
    warning="#C07010",
    error="#CC2020",
    success="#2A7050",
    dark=False,
)

AIQ_DARK = Theme(
    name="aiq-dark",
    # Near-black with a faint warm-red tint to echo the brand
    background="#1A1214",
    surface="#2A2022",
    panel="#332428",
    # Crimson brightened enough to read on dark backgrounds
    primary="#C0303C",
    secondary="#888888",
    accent="#E04050",       # lighter crimson for titles
    warning="#E0821A",
    error="#E03030",
    success="#30A060",
    dark=True,
)

ALL_THEMES = [NORD, GRUVBOX, DRACULA, SOLARIZED_LIGHT, WARM_LINEN, AIQ, AIQ_DARK]

# Ordered list used by the theme demo — built-ins first, then custom
THEME_NAMES = ["textual-dark", "textual-light"] + [t.name for t in ALL_THEMES]

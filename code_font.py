"""Set code in JetBrains Mono, the code font bundled with this skill.

Copy this file next to scene.py and import it before building any text:

    import code_font              # every Code block is now set in JetBrains Mono
    from code_font import MONO    # for code written with Text: Text("git status", font=MONO)

Importing it loads the font files from the skill's assets/fonts/jetbrains-mono/, so the font
doesn't have to be installed on the machine, and makes it the default font of `Code`.
JetBrains Mono is under the SIL Open Font License; the license is beside the font files.
"""

from pathlib import Path

import manimpango
from manim import Code, MarkupText, Text

# The files are the "NL" (no ligatures) cut of JetBrains Mono: the same letters, without the
# joined forms for pairs like != and ->. Manim's Code needs one glyph for every character
# and fails on a font that merges two characters into one.
MONO = "JetBrains Mono NL"

SEARCH = [
    Path(__file__).resolve().parent / "assets",
    Path.home() / ".claude/skills/manim/assets",
]


def _load():
    for root in SEARCH:
        files = sorted((root / "fonts" / "jetbrains-mono").glob("*.ttf"))
        if files:
            for file in files:
                if not manimpango.register_font(str(file)):
                    raise RuntimeError(f"could not load the font file {file}")
            return
    raise FileNotFoundError("no JetBrains Mono font files; looked in fonts/jetbrains-mono under "
                            + " and ".join(str(root) for root in SEARCH))


_load()
Code.default_paragraph_config["font"] = MONO
# Manim remembers the list of fonts it first saw and warns about any font not on it.
Text.font_list.cache_clear()
MarkupText.font_list.cache_clear()

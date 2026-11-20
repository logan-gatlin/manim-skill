"""Load icons from the skill's icon library (assets/) as Manim mobjects.

Copy this file next to scene.py:

    from icons import icon

    server = icon("tabler/outline/server", color=TEAL, height=1.2)
    lock = icon("fluent/locked", height=0.6)

Find an id with `grep -iw <word> assets/index.tsv` in the skill directory. Ids are
`tabler/outline/<name>` and `tabler/filled/<name>` (Tabler Icons, one-color line and solid
icons, recolored with `color`), and `fluent/<name>` (Fluent Emoji, Flat style, which keep their
own colors; `color` is ignored). Both sets are MIT licensed; the licenses are in assets/.
"""

from pathlib import Path

from manim import WHITE, SVGMobject

SEARCH = [
    Path(__file__).resolve().parent / "assets",
    Path.home() / ".claude/skills/manim/assets",
]


def icon_path(name):
    for root in SEARCH:
        path = root / f"{name}.svg"
        if path.exists():
            return path
    raise FileNotFoundError(f"no icon {name!r}; search assets/index.tsv for an id")


def icon(name, color=WHITE, height=1.0, stroke_width=None):
    """The icon `name` (an id from assets/index.tsv), `height` units tall.

    Tabler icons draw in `color`: line icons with a stroke of `stroke_width` (by default in
    proportion to `height`, matching the drawn 2/24 line weight), solid icons filled.
    """
    mob = SVGMobject(str(icon_path(name)), height=height)
    if name.startswith("tabler/"):
        # The files use `currentColor`, which Manim reads as black: recolor every part.
        width = 4.0 * height if stroke_width is None else stroke_width
        for part in mob.family_members_with_points():
            if part.get_fill_opacity() > 0:
                part.set_fill(color, 1)
            if part.get_stroke_width() > 0 and name.startswith("tabler/outline/"):
                part.set_stroke(color, width)
            else:
                part.set_stroke(width=0)
    return mob

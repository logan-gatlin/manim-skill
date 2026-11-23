"""A node for architecture diagrams: a card with an icon, a name and a second line. A bar
down its left edge shows its status by color; nothing else about the card changes.

Copy this file, icons.py and code_font.py next to scene.py:

    from node import Node

    api = Node("API", "gateway", icon="tabler/outline/server")
    db = Node("Postgres", "primary", icon="tabler/outline/database").next_to(api, RIGHT, buff=1.5)
    self.play(FadeIn(api, scale=0.9), FadeIn(db, scale=0.9))
    self.play(api.to("active"))        # the bar turns blue
    self.play(db.to("failed"))         # red, with a shake
    self.play(db.to("inactive"))       # grey again

A node is an ordinary group: place it, scale it, fade it and connect lines to it like any
other mobject. See README.md.
"""

import numpy as np
from manim import RIGHT, SEMIBOLD, Animation, ManimColor, RoundedRectangle, Text, VGroup, interpolate_color, smooth

from code_font import MONO
from icons import icon as load_icon

TRACK = "#1c2130"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE, RED, GREY = "#60a5fa", "#f87171", "#737b8c"
SANS = "Noto Sans"

# The color of the bar in each status.
STATUS = {"inactive": GREY, "active": BLUE, "failed": RED}
CHANGE = 0.4      # seconds a change of status takes
SHAKE = 0.75      # seconds a failing node shakes for


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _word(s, size, color, font, weight="NORMAL"):
    """Text centred on y = 0 by a box that always holds a capital and a descender, so the
    names of nodes side by side share a baseline whatever letters they have."""
    t = Text("Hg" + s, font=font, font_size=size, weight=weight, color=color)
    t.shift(-t.get_center())
    return VGroup(*t[2:])


class _Change(Animation):
    """Moves a node to another status, starting from however it looks when this begins."""

    def __init__(self, node, status, run_time, rate_func):
        if status not in STATUS:
            raise ValueError(f"status must be one of {', '.join(STATUS)}, not {status!r}")
        self.status = status
        self.fails = status == "failed"
        super().__init__(node, run_time=run_time or (SHAKE if self.fails else CHANGE), rate_func=rate_func)

    def begin(self):
        self.before, self.shaken = self.mobject._color, 0.0
        super().begin()

    def interpolate_mobject(self, alpha):
        node = self.mobject
        seconds = alpha * self.run_time
        k = self.rate_func(min(1.0, seconds / min(CHANGE, self.run_time)))
        node._paint(_mix(self.before, STATUS[self.status], k))
        if self.fails:                                  # a failure shakes the node as its bar turns red
            size = node.card.height / node._height
            offset = 0.07 * size * (1 - alpha) * np.exp(-4 * seconds) * np.sin(38 * seconds)
            node.shift(RIGHT * (offset - self.shaken))
            self.shaken = offset

    def finish(self):
        super().finish()
        self.mobject.status = self.status


class Node(VGroup):
    """A card for one thing in a diagram.

    name      its name.
    sub       a second, smaller line in the code font: a role, a host, a version. Without
              one the card is shorter.
    icon      an icon id from the skill's library, such as "tabler/outline/server".
    status    "inactive" (the default), "active" or "failed".
    width     the card's width. By default 2.3 with a second line and 1.5 without, and
              wider if the text needs it. Give nodes that sit together the same width.

    `node.card`, `node.bar`, `node.icon`, `node.name` and `node.sub` are its parts.
    """

    def __init__(self, name, sub=None, icon=None, status="inactive", width=None, **kwargs):
        super().__init__(**kwargs)
        self._height = 0.86 if sub else 0.62
        self.name = _word(name, 17 if sub else 16, INK, SANS, SEMIBOLD)
        self.sub = _word(sub, 12, MUTED, MONO) if sub else None
        self.icon = load_icon(icon, color=MUTED, height=0.38 if sub else 0.3) if icon else None
        text_at = 0.98 if sub else 0.84                 # from the card's left edge, when there is an icon
        if not icon:
            text_at = 0.42
        needs = text_at + max(self.name.width, self.sub.width if sub else 0) + 0.32
        w = max(width or (2.3 if sub else 1.5), needs)
        self.card = RoundedRectangle(corner_radius=0.1, width=w, height=self._height, stroke_width=0,
                                     fill_color=TRACK, fill_opacity=1)
        self.bar = RoundedRectangle(corner_radius=0.04, width=0.08, height=self._height - 0.22, stroke_width=0,
                                    fill_opacity=1).move_to([-w / 2 + 0.16, 0, 0])
        left = -w / 2
        self.name.shift([left + text_at - self.name.get_left()[0], 0.14 if sub else 0, 0])
        if sub:
            self.sub.shift([left + text_at - self.sub.get_left()[0], -0.17, 0])
        if icon:
            self.icon.move_to([left + (0.58 if sub else 0.52), 0, 0])
        self.add(self.card, self.bar, *[part for part in (self.icon, self.name, self.sub) if part is not None])
        self.status = status
        self._paint(STATUS[status])

    def to(self, status, run_time=None, rate_func=smooth):
        """Change to another status. Returns the animation."""
        return _Change(self, status, run_time, rate_func)

    def set_status(self, status):
        """Show another status at once, with no animation."""
        self.status = status
        self._paint(STATUS[status])
        return self

    def scale(self, scale_factor, **kwargs):
        """Scale the node. The icon's line weight scales with it."""
        super().scale(scale_factor, **kwargs)
        if self.icon is not None:
            for part in self.icon.family_members_with_points():
                part.set_stroke(width=part.get_stroke_width() * abs(scale_factor))
        return self

    def _paint(self, color):
        """Give the bar this color."""
        self._color = color
        self.bar.set_fill(color, 1)

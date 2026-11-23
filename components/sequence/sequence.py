"""A sequence diagram: who says what to whom, in order, down the page.

Copy this file and the skill's code_font.py next to scene.py:

    from sequence import Sequence

    seq = Sequence("Web", "API", "DB")
    self.play(seq.draw())                                   # the names and their lifelines
    self.play(seq.send("Web", "API", "GET /cart"))          # a request: a solid arrow
    self.play(seq.send("API", "DB", "SELECT"))
    self.play(seq.reply("DB", "API", "rows"))               # a reply: a dashed grey arrow
    self.play(seq.reply("API", "Web", "200"))
    self.play(seq.send("API", "DB", "INSERT", lost=True))   # never arrives: it stops and turns red
    self.play(seq.reply("API", "Web", "504", error=True))   # a failure: a dashed red arrow

Each message goes on the next row down. See README.md.
"""

import numpy as np
from manim import DOWN, SEMIBOLD, Animation, CapStyleType, LineJointType, Polygon, Text, VGroup, VMobject, ManimColor, interpolate_color, linear, smooth

from code_font import MONO

LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
RED = "#f87171"
SANS = "Noto Sans"

CROSS = 0.55      # seconds a message takes to cross
GIVE_UP = 0.9     # seconds before a lost message is seen to be lost...
TURN = 0.3        # ...and how long it takes to turn red


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def _word(s, size, color, font, weight="NORMAL"):
    """Text centred on y = 0 by a box that holds a capital and a descender, so words on a
    line share a baseline whatever letters they have."""
    t = Text("Hg" + s, font=font, font_size=size, weight=weight, color=color)
    t.shift(-t.get_center())
    g = VGroup(*t[2:])
    return g.shift([-g.get_center()[0], 0, 0])


def _stroke(color, width):
    return VMobject(joint_type=LineJointType.ROUND).set_stroke(color, width, 0).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)


class _Message(VGroup):
    """One message: a shaft (whole, or in dashes), a barbed tip, a label, and for a lost
    message the cross that marks where it stopped. Made empty, and drawn by `lay`."""

    def __init__(self, a, b, label, kind, size):
        super().__init__()
        self.a, self.b, self.kind, self.size = a, b, kind, size
        self.tint = {"ask": INK, "lost": INK, "reply": MUTED, "error": RED}[kind]
        self.dashed = kind in ("reply", "error")
        self.far = 0.62 if kind == "lost" else 1.0           # how much of the way it gets
        self.weight = (2.5 if self.dashed else 3.0) * size   # (`width` is the mobject's own size)
        self.shaft = VGroup(*[_stroke(self.tint, self.weight) for _ in range(60 if self.dashed else 1)])
        L, W = 0.38 * 0.62 * size, 0.32 * 0.62 * size
        self.outline = np.array([[0, 0, 0], [-L, W / 2, 0], [-L * 0.7, 0, 0], [-L, -W / 2, 0]])
        self.back = L * 0.68                                 # the shaft ends inside the tip's notch
        self.tip = Polygon(*self.outline, joint_type=LineJointType.ROUND, color=self.tint, fill_opacity=0,
                           stroke_width=1.2 * size, stroke_opacity=0)
        self.label = _word(label, 13.5 * size, {"ask": INK, "lost": INK, "reply": MUTED, "error": RED}[kind], MONO)
        self.label.set_opacity(0)
        self.cross = VGroup(*[_stroke(RED, 2.6 * size) for _ in range(2 if kind == "lost" else 0)])
        self.add(self.shaft, self.tip, self.label, self.cross)

    def route(self, xa, xb, y, row):
        """Fix the path: straight across from one lifeline to another, or out and back in
        a small loop for a message to itself."""
        s = self.size
        if abs(xa - xb) > 1e-6:
            way = 1 if xb > xa else -1
            pts = [[xa + way * 0.09 * s, y], [xb - way * 0.09 * s, y]]
            self.spot = np.array([(pts[0][0] + pts[0][0] + (pts[1][0] - pts[0][0]) * self.far) / 2, y + 0.23 * s, 0])
        else:
            out, drop, r = 0.62 * s, 0.42 * row, 0.12 * s
            pts = [[xa + 0.09 * s, y], [xa + out - r, y]]
            for cx, cy, a0 in ((xa + out - r, y - r, 90), (xa + out - r, y - drop + r, 0)):
                pts += [[cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a))] for a in np.linspace(a0, a0 - 90, 8)]
            pts.append([xa + 0.09 * s, y - drop])
            self.spot = None
            self.side = np.array([xa + out + 0.16 * s, y - drop / 2, 0])
        self.pts = np.array([[x, y, 0.0] for x, y in pts])
        self.cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(self.pts, axis=0), axis=1))])

    def at(self, s):
        i = min(int(np.searchsorted(self.cum, s, "right")) - 1, len(self.pts) - 2)
        return self.pts[i] + (s - self.cum[i]) / max(self.cum[i + 1] - self.cum[i], 1e-9) * (self.pts[i + 1] - self.pts[i])

    def cut(self, s0, s1):
        return [self.at(s0), *[self.pts[i] for i in range(len(self.pts)) if s0 < self.cum[i] < s1], self.at(s1)]

    def lay(self, seconds):
        """Draw the message as it is `seconds` after it set off."""
        s = self.size
        total = self.cum[-1] * self.far
        q = _ease(seconds / CROSS)
        head = total * q
        lost = _ease((seconds - GIVE_UP) / TURN) if self.kind == "lost" else 0.0
        color = _mix(self.tint, RED, lost)
        # the tip leads; it swells to full size as it sets off
        grown = min(1.0, seconds / CROSS * 4)
        d = self.at(min(head + 0.01, self.cum[-1])) - self.at(max(head - 0.01, 0))
        d = d / max(np.linalg.norm(d), 1e-9)
        turn = np.array([[d[0], d[1], 0], [-d[1], d[0], 0], [0, 0, 1]])
        self.tip.set_points(Polygon(*(self.outline * max(grown, 1e-3) @ turn + self.at(head))).points)
        self.tip.set_fill(color, 1 if grown > 0.02 else 0).set_stroke(color, opacity=1 if grown > 0.02 else 0)
        # the shaft, up to the tip's notch
        end = head - self.back * grown
        dash, gap = (0.13 * s, 0.1 * s) if self.dashed else (total + 1, 0)
        for i, piece in enumerate(self.shaft):
            s0 = i * (dash + gap)
            s1 = min(s0 + dash, end)
            if s1 - s0 < 2e-3:
                piece.set_stroke(opacity=0)
            else:
                piece.set_points_as_corners(self.cut(s0, s1)).set_stroke(color, opacity=1)
        # the label comes in as the message passes the middle
        said = _ease((seconds / CROSS - 0.25) / 0.4)
        if self.spot is not None:
            where = self.spot + DOWN * 0.04 * s * (1 - said)
        else:                                                # beside the loop, its left edge clear of it
            where = self.side + np.array([self.label.width / 2, 0, 0])
        self.label.shift(where - self.label.get_center())
        self.label.set_fill(_mix(INK, RED, lost) if self.kind == "lost" else None, said)
        # where a lost message stopped
        for stroke, way in zip(self.cross, (1, -1)):
            c, r = self.at(total) + d * 0.2 * s, 0.085 * s * lost
            if r < 1e-3:
                stroke.set_stroke(opacity=0)
            else:
                stroke.set_points_as_corners([c - np.array([r, way * r, 0]), c + np.array([r, way * r, 0])]).set_stroke(opacity=1)


class _Draw(Animation):
    def __init__(self, seq, **kwargs):
        super().__init__(seq, introducer=True, **kwargs)

    def interpolate_mobject(self, alpha):
        a = self.rate_func(alpha)
        self.mobject._grow(self.mobject._first_reach() * _ease(a / 0.8), names=_ease(a / 0.5))


class _Play(Animation):
    """Draws one message across, and grows the lifelines down to make room for it."""

    def __init__(self, seq, message, row, run_time):
        self.message, self.row = message, row
        seconds = CROSS + 0.05 if message.kind != "lost" else GIVE_UP + TURN
        super().__init__(seq, run_time=run_time or seconds, rate_func=linear)
        self.seconds = seconds

    def begin(self):
        seq = self.mobject
        self.message.route(seq._x(self.message.a), seq._x(self.message.b), seq._y(self.row), seq.row)
        self.start = seq._reach
        self.end = max(seq._reach, seq._below(self.row + (0.42 if self.message.a == self.message.b else 0)))
        super().begin()

    def interpolate_mobject(self, alpha):
        self.mobject._grow(self.start + (self.end - self.start) * _ease(alpha / 0.6))
        self.message.lay(alpha * self.seconds)


class Sequence(VGroup):
    """The participants' names across the top, each with a lifeline below it, and the
    messages between them, one row down at a time. Its top-left corner starts at the
    origin; place it with `move_to`, `to_edge` or `shift`.

    names     the participants, left to right.
    spacing   the distance between lifelines.
    row       the distance between messages.
    rows      how many messages to leave room for. Given this, the lifelines are drawn to
              their full length from the start and the diagram's size never changes;
              without it they grow as messages are added.
    size      scales the text, arrow tips and line weights. Don't `scale` the diagram.

    `seq.names`, `seq.lifelines` and `seq.messages` are its parts.
    """

    def __init__(self, *names, spacing=2.4, row=0.75, rows=None, size=1.0, **kwargs):
        super().__init__(**kwargs)
        self.who, self.spacing, self.row, self.size = list(names), spacing, row, size
        self.names = VGroup(*[_word(name, 20 * size, INK, SANS, SEMIBOLD).shift([i * spacing, 0, 0]) for i, name in enumerate(names)])
        self.lifelines = VGroup(*[_stroke(LINE, 2 * size) for _ in names])
        self.messages = VGroup()
        self.add(self.lifelines, self.messages, self.names)
        self._count, self._rows = 0.0, rows
        self._grow(self._first_reach())

    # ---- adding to it

    def draw(self, run_time=1.0, rate_func=smooth):
        """The animation that brings in the names and grows the lifelines. Adds the diagram
        to the scene."""
        return _Draw(self, run_time=run_time, rate_func=rate_func)

    def send(self, a, b, label, lost=False, run_time=None):
        """A request from `a` to `b` (names, or positions counting from 0), on the next row:
        a solid arrow. `lost=True` is one that never arrives: it stops part-way, turns red
        and is marked with a cross. `a` and `b` may be the same, for a step a participant
        does by itself. Returns the animation."""
        return self._message(a, b, label, "lost" if lost else "ask", run_time)

    def reply(self, a, b, label, error=False, run_time=None):
        """A reply from `a` to `b`, on the next row: a dashed grey arrow, or a dashed red
        one with `error=True`. Returns the animation."""
        return self._message(a, b, label, "error" if error else "reply", run_time)

    def skip(self, rows=1):
        """Leave rows empty before the next message, to separate one exchange from the next."""
        self._count += rows
        return self

    # ---- drawing it

    def _message(self, a, b, label, kind, run_time):
        a, b = (self.who.index(p) if isinstance(p, str) else p for p in (a, b))
        message = _Message(a, b, label, kind, self.size)
        message.shift(self.lifelines[a].get_start())       # out of sight, where it will start from
        self.messages.add(message)
        row = self._count
        self._count += 1 + (0.42 if a == b else 0)
        return _Play(self, message, row, run_time)

    def _x(self, i):
        return self.names[i].get_center()[0]

    def _top(self):
        return self.names[0].get_center()[1]

    def _y(self, row):
        """The height of a row, counting from 0."""
        return self._top() - 0.34 * self.size - (0.72 + row) * self.row

    def _below(self, row):
        """How far below the names the lifelines must reach to hold this row."""
        return self._top() - self._y(row) + 0.62 * self.row

    def _first_reach(self):
        return self._below(self._rows - 1) if self._rows else 0.34 * self.size + 0.5 * self.row

    def _grow(self, reach, names=1.0):
        """Draw the lifelines down to `reach` below the names, with the names `names` shown."""
        self._reach = reach
        top = self._top() - 0.34 * self.size
        for i, line in enumerate(self.lifelines):
            x = self._x(i)
            end = min(self._top() - reach, top - 1e-3)
            line.set_points_as_corners([[x, top, 0], [x, end, 0]]).set_stroke(opacity=1 if reach > 0.36 * self.size else 0)
        for name in self.names:
            name.set_opacity(names)

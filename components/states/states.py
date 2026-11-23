"""A state machine: named states, one of them current, and transitions that fire along the
arrows between them.

Copy this file next to scene.py, with the line component's line.py and the skill's
code_font.py:

    from states import StateMachine

    m = StateMachine(
        {"idle": (-3.2, 0), "loading": (0, 0), "done": (3.2, 0), "failed": (0, -1.9)},
        [("idle", "loading", "fetch"), ("loading", "done", "ok"), ("loading", "failed", "error"),
         ("failed", "loading", "retry"), ("done", "idle", "reset")],
        bad=["failed"])
    self.play(m.draw())
    self.play(m.fire("fetch"))        # idle -> loading
    self.play(m.fire("error"))        # loading -> failed, which lights red

The current state is a solid blue chip. See README.md.
"""

import numpy as np
from manim import DOWN, LEFT, RIGHT, SEMIBOLD, UP, Animation, ManimColor, RoundedRectangle, Text, VGroup, interpolate_color, smooth

from code_font import MONO
from line import Connector

TRACK = "#1c2130"
DARK = "#0d1118"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE, RED = "#60a5fa", "#f87171"
SANS = "Noto Sans"

FIRE = 0.75       # seconds a transition takes to fire


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def _word(s, size, color, font, weight="NORMAL"):
    """Text centred on y = 0 by a box that holds a capital and a descender, so the names of
    states side by side share a baseline."""
    t = Text("Hg" + s, font=font, font_size=size, weight=weight, color=color)
    t.shift(-t.get_center())
    g = VGroup(*t[2:])
    return g.shift([-g.get_center()[0], 0, 0])


class _Draw(Animation):
    """Brings the machine in: the states, then the arrows growing between them and their
    labels, then the starting state lighting up."""

    def __init__(self, machine, **kwargs):
        super().__init__(machine, introducer=True, **kwargs)

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole machine here, and never use the copy

    def interpolate_mobject(self, alpha):
        m, a = self.mobject, self.rate_func(alpha)
        for i, chip in enumerate(m.chips.values()):
            shown = _ease((a - 0.04 * i) / 0.3)
            chip[0].set_fill(opacity=shown)
            chip[1].set_fill(opacity=shown)
        for link, label in zip(m.arrows.values(), m.labels.values()):
            link.lay(_ease((a - 0.25) / 0.5))
            label.set_fill(opacity=_ease((a - 0.5) / 0.3))
        for name in m.chips:
            m._paint(name, _ease((a - 0.75) / 0.25) if name == m._start else 0.0)


class _Fire(Animation):
    """One transition: the state it leaves goes dark, its arrow and label light up, and the
    state it reaches lights."""

    def __init__(self, machine, key, run_time):
        self.key = key
        super().__init__(machine, run_time=run_time, rate_func=lambda t: t)

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole machine here, and never use the copy

    def interpolate_mobject(self, alpha):
        m = self.mobject
        a, b, _ = self.key
        hot = _ease(alpha / 0.2) * (1 - _ease((alpha - 0.8) / 0.2))
        m.arrows[self.key].set_color(_mix(INK, BLUE, hot))
        m.labels[self.key].set_fill(_mix(MUTED, INK, hot))
        if a != b:
            m._paint(a, 1 - _ease(alpha / 0.35))
            m._paint(b, _ease((alpha - 0.7) / 0.3))
        else:                                     # back to itself: it dims a little and relights
            m._paint(a, 1 - 0.6 * np.sin(np.pi * alpha) ** 2)

    def finish(self):
        super().finish()
        self.mobject.current = self.key[1]


class StateMachine(VGroup):
    """States as chips, joined by labelled arrows.

    states        where each state goes: {name: (x, y)}. A plain list of names is laid out
                  in a row, `spacing` apart.
    transitions   (from, to, label) for each arrow. A fourth item, a dict, is passed to the
                  line component's Connector to route that arrow yourself, for example
                  {"route": "u", "side": DOWN}.
    start         the state that is current to begin with; by default the first.
    bad           states that light red instead of blue when current: failures, errors.
    size          scales the chips, text and arrows. Don't `scale` the machine.

    `machine.current` is the current state's name. `machine.chips[name]`,
    `machine.arrows[(from, to, label)]` and `machine.labels[(from, to, label)]` are its parts.
    """

    def __init__(self, states, transitions, start=None, bad=(), spacing=3.2, size=1.0, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(states, dict):
            states = {name: ((i - (len(states) - 1) / 2) * spacing, 0) for i, name in enumerate(states)}
        self.size, self.bad = size, set(bad)
        self._start = start or next(iter(states))
        self.current = self._start
        self._planned = self._start               # where the machine will be after the moves made so far
        s = size
        self.chips = {}
        for name, at in states.items():
            text = _word(name, 19 * s, INK, SANS, SEMIBOLD)
            box = RoundedRectangle(corner_radius=0.16 * s, width=max(1.75 * s, text.width + 0.7 * s), height=0.7 * s,
                                   stroke_width=0, fill_color=TRACK, fill_opacity=1)
            self.chips[name] = VGroup(box, text).move_to([at[0], at[1], 0])
        keys = [(t[0], t[1], t[2]) for t in transitions]
        self.arrows, self.labels = {}, {}
        ups = 0
        for t in transitions:
            a, b, label = t[:3]
            options = dict(t[3]) if len(t) > 3 else None
            paired = any(k[0] == b and k[1] == a for k in keys) and a != b
            link, aside = self._route(a, b, paired, options, ups)
            if link.route_used == "over":
                ups += 1
            self.arrows[(a, b, label)] = link
            self.labels[(a, b, label)] = self._label(link, label, aside)
        self.add(*self.arrows.values(), *self.labels.values(), *self.chips.values())
        for name in self.chips:
            self._paint(name, 1.0 if name == self.current else 0.0)

    # ---- running it

    def draw(self, run_time=1.6, rate_func=smooth):
        """The animation that brings the machine in. Adds it to the scene."""
        return _Draw(self, run_time=run_time, rate_func=rate_func)

    def fire(self, transition, run_time=FIRE):
        """Fire a transition out of the current state, named by its label, or by (from, to)
        when labels repeat. Returns the animation."""
        matches = [k for k in self.arrows if k[0] == self._planned and (k[2] == transition or (k[0], k[1]) == tuple(transition))]
        if not matches:
            leaving = ", ".join(k[2] for k in self.arrows if k[0] == self._planned) or "none"
            raise ValueError(f"no transition {transition!r} out of {self._planned!r}; the ones that leave it are: {leaving}")
        self._planned = matches[0][1]
        return _Fire(self, matches[0], run_time)

    def set_state(self, name):
        """Make `name` the current state at once, with no animation."""
        self.current = self._planned = name
        for other in self.chips:
            self._paint(other, 1.0 if other == name else 0.0)
        return self

    # ---- building it

    def _paint(self, name, lit):
        box, text = self.chips[name]
        box.set_fill(_mix(TRACK, RED if name in self.bad else BLUE, lit))
        text.set_fill(_mix(INK, DARK, lit))

    def _route(self, a, b, paired, options, ups):
        """The arrow from a to b. Returns it and, for an arrow that runs beside its opposite
        number, the side its label belongs on."""
        s, A, B = self.size, self.chips[a][0], self.chips[b][0]
        style = dict(width=3.5 * s, tip_size=0.85 * s, corner=0.25 * s, buff=0.1 * s)
        if options is not None:
            link = Connector(A, B, **{**style, **options})
            link.route_used = "own"
            return link, None
        if a == b:                                # a loop out of the top and back
            link = Connector(A, A, route="u", side=UP, reach=0.5 * s, **style)
            link.route_used = "loop"
            return link, None
        ca, cb = A.get_center(), B.get_center()
        level, plumb = abs(ca[1] - cb[1]) < 0.05, abs(ca[0] - cb[0]) < 0.05
        if level or plumb:
            between = [c for n, c in ((n, chip[0].get_center()) for n, chip in self.chips.items()) if n not in (a, b) and (
                min(ca[0], cb[0]) < c[0] < max(ca[0], cb[0]) and abs(c[1] - ca[1]) < 0.6 * s if level else
                min(ca[1], cb[1]) < c[1] < max(ca[1], cb[1]) and abs(c[0] - ca[0]) < 1.0 * s)]
            if between:                           # another state is in the way: go over it (or under, or round)
                side = ((UP, DOWN) if level else (RIGHT, LEFT))[ups % 2]
                link = Connector(A, B, route="u", side=side, reach=0.55 * s, **style)
                link.route_used = "over"
                return link, None
            d = (cb - ca) / np.linalg.norm(cb - ca)
            right = np.array([d[1], -d[0], 0.0])                 # to the right of the way it travels
            off = right * (0.24 * s if paired else 0.0)
            half = lambda box: box.width / 2 if level else box.height / 2
            link = Connector(ca + d * (half(A) + 0.1 * s) + off, cb - d * (half(B) + 0.1 * s) + off, route="straight", **style)
            link.route_used = "straight"
            return link, (right if paired else None)
        link = Connector(A, B, **style)
        link.route_used = "elbows"
        return link, None

    def _label(self, link, label, aside):
        """The label, beside the middle of the arrow's longest straight run: above a level
        run, to the right of an upright one, and on the outer side of a pair."""
        s = self.size
        text = _word(label, 13.5 * s, MUTED, MONO)
        pts = link.paths[0].pts
        best, spot, along = -1.0, pts[0], RIGHT
        i = 0
        while i < len(pts) - 1:
            d = pts[i + 1] - pts[i]
            d = d / max(np.linalg.norm(d), 1e-9)
            j = i + 1
            while j < len(pts) - 1 and np.linalg.norm((pts[j + 1] - pts[j]) / max(np.linalg.norm(pts[j + 1] - pts[j]), 1e-9) - d) < 1e-3:
                j += 1
            run = np.linalg.norm(pts[j] - pts[i])
            if run > best:
                best, spot, along = run, (pts[i] + pts[j]) / 2, d
            i = j
        if aside is None:
            aside = UP if abs(along[0]) > abs(along[1]) else RIGHT
        reach = 0.26 * s if abs(aside[1]) > 0.5 else 0.2 * s + text.width / 2
        return text.shift(spot + aside * reach)

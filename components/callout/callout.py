"""A callout: a short label joined to the thing it describes by a thin line that leaves the
thing, turns once and ends at the words.

Copy this file next to scene.py:

    from callout import Callout

    note = Callout(api, "stateless")                     # up from the top of `api`, then right
    self.play(note.draw())                               # the line grows out, then the words
    self.play(note.erase())                              # ...and back again

    Callout(link.point(0.5), "TLS 1.3", side=DOWN)       # a point works as well as a mobject
    Callout(db, "primary", side=DOWN, turn=LEFT)         # down, then left
    Callout(db, "eu-west", side=RIGHT)                   # straight out sideways

See README.md for every option.
"""

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Animation, CapStyleType, LineJointType, Mobject, Text, VGroup, VMobject, linear)

INK = "#eef1f6"
MUTED = "#8a93a6"
SANS = "Noto Sans"

FONT = 18         # the size of the words
PITCH = 0.36      # the distance from one line of words down to the next
GAP = 0.13        # the space between the end of the line and the words
SLIDE = 0.15      # how far the words slide as they arrive


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def _rounded(points, r, n=10):
    """The points of a line through `points` with each corner turned through an arc."""
    out = [points[0]]
    for a, b, c in zip(points, points[1:], points[2:]):
        u, v = a - b, c - b
        lu, lv = np.linalg.norm(u), np.linalg.norm(v)
        u, v = u / lu, v / lv
        half = np.arccos(np.clip(np.dot(u, v), -1, 1)) / 2
        rr = min(r, min(lu, lv) / 2 * np.tan(half))
        d = rr / np.tan(half)
        centre = b + (u + v) / np.linalg.norm(u + v) * rr / np.sin(half)
        p1, p2 = b + u * d - centre, b + v * d - centre
        a0 = np.arctan2(p1[1], p1[0])
        sweep = (np.arctan2(p2[1], p2[0]) - a0 + np.pi) % (2 * np.pi) - np.pi
        out += [centre + rr * np.array([np.cos(a0 + sweep * k / n), np.sin(a0 + sweep * k / n), 0]) for k in range(n + 1)]
    out.append(points[-1])
    return np.array(out)


def _cut(pts, part):
    """The first `part` of a line through `pts`."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    want = max(part, 1e-3) * cum[-1]
    i = min(int(np.searchsorted(cum, want, "right")) - 1, len(pts) - 2)
    return np.vstack([pts[:i + 1], pts[i] + (want - cum[i]) / max(seg[i], 1e-9) * (pts[i + 1] - pts[i])])


class _Draw(Animation):
    """Draws a callout in: the line grows out from the thing, then the words arrive. Or,
    with `back`, the same in reverse, after which the callout is taken off the scene."""

    def __init__(self, callout, back, run_time):
        self.back = back
        super().__init__(callout, run_time=run_time, rate_func=linear, remover=back)

    def create_starting_mobject(self):
        return VMobject()       # Manim would copy the whole callout here, and never use the copy

    def interpolate_mobject(self, alpha):
        p = 1 - alpha if self.back else alpha
        self.mobject._drawn, self.mobject._said = _ease(p / 0.6), _ease((p - 0.45) / 0.55)
        self.mobject._lay()


class Callout(VGroup):
    """A label and the line that joins it to `target`.

    target   a mobject, or a point.
    text     a word or a few. "\\n" starts a second line.
    side     the side of the target the line leaves from: UP, DOWN, LEFT or RIGHT.
    turn     the direction the line turns to after `rise`. Unless given, a line that leaves
             up or down turns RIGHT, and one that leaves sideways does not turn. False is a
             straight line whatever its side.
    rise     how far the line goes before it turns (its whole length when it does not).
    run      how far it goes after the turn.
    at       where on the target's side the line starts: 0.5 is the middle, 0 and 1 the
             ends (left to right, or bottom to top).
    follow   True keeps the callout attached while its target moves.
    color    the line's color; `text_color` the words'.
    size     scales the words and the line's weight.
    buff     the gap between the target and the start of the line.
    corner   the radius of the turn.

    `callout.line` and `callout.label` are its parts.
    """

    def __init__(self, target, text, side=UP, turn=None, rise=0.7, run=0.4, at=0.5, follow=False,
                 color=MUTED, text_color=INK, size=1.0, buff=0.08, corner=0.14, font=SANS, **kwargs):
        super().__init__(**kwargs)
        side = np.array(side, dtype=float)
        if turn is None:
            turn = RIGHT if abs(side[1]) > 0.5 else False
        # (Not `self.target`: Manim keeps the copy a mobject is being moved to under that
        # name, so `callout.animate` would replace what the callout points at.)
        self._subject, self.side, self.rise, self.run, self.at = target, side, rise, run, at
        self.turn = None if turn is False else np.array(turn, dtype=float)
        if self.turn is not None and abs(float(np.dot(self.turn, side))) > 1e-6:
            raise ValueError("turn must be at right angles to side: RIGHT or LEFT for a line that leaves UP or DOWN")
        self.color_, self.text_color, self.size, self.buff, self.corner = color, text_color, size, buff, corner
        self._drawn, self._said = 1.0, 1.0        # how much of the line is drawn, and how far the words have arrived

        self.line = VMobject(joint_type=LineJointType.ROUND).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
        # The words, behind an invisible point that is put at the end of the line: the edge
        # of the words nearest the line, on the middle of their first or only row.
        last = self.turn if self.turn is not None else side
        rows = text.split("\n")
        letters = VGroup()
        for i, row in enumerate(rows):
            t = Text("Hg" + row, font=font, font_size=FONT * size)
            word = VGroup(*t[2:]).shift([0, -t[:2].get_center()[1], 0])
            if not len(word):
                continue
            x = word.get_left()[0] if last[0] > 0.5 else word.get_right()[0] if last[0] < -0.5 else word.get_center()[0]
            if abs(last[0]) > 0.5:                    # beside the line's end, centred on it
                y = ((len(rows) - 1) / 2 - i) * PITCH * size
            elif last[1] > 0:                         # above it, the last row nearest
                y = (len(rows) - 1 - i) * PITCH * size
            else:                                     # below it, the first row nearest
                y = -i * PITCH * size
            letters.add(*word.shift([-x, y, 0]))
        self._anchor = VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([ORIGIN, ORIGIN])
        self.label = VGroup(self._anchor, *letters)
        self.add(self.line, self.label)
        self._lay()
        if follow:
            self.add_updater(Callout._follow)

    def __deepcopy__(self, memo):
        # A copy is a still picture of the callout, which points at the same thing and does
        # not follow it: FadeIn, FadeOut and the like work on copies, and a copy that laid
        # itself out again on every frame would undo the fade.
        if isinstance(self._subject, Mobject):
            memo.setdefault(id(self._subject), self._subject)
        twin = super().__deepcopy__(memo)
        twin.updaters = []
        return twin

    # ---- using it

    def draw(self, run_time=0.8):
        """The entrance: the line grows out from the target, then the words slide in from
        its end. Returns the animation."""
        return _Draw(self, False, run_time)

    def erase(self, run_time=0.6):
        """The exit: the words go, the line draws back into the target, and the callout is
        taken off the scene. Returns the animation."""
        return _Draw(self, True, run_time)

    # ---- drawing it

    def _follow(self, dt=0):
        self._lay()

    def _start(self):
        """Where the line leaves the target."""
        if not isinstance(self._subject, Mobject):
            return np.array(self._subject, dtype=float) + self.side * self.buff
        along = np.array([abs(self.side[1]), abs(self.side[0]), 0.0])      # the direction the side runs in
        span = self._subject.width if along[0] else self._subject.height
        return self._subject.get_edge_center(self.side) + along * (self.at - 0.5) * span + self.side * self.buff

    def _lay(self):
        """Put the line and the words where the target is now."""
        start = self._start()
        pts = [start, start + self.side * self.rise]
        if self.turn is not None:
            pts.append(pts[-1] + self.turn * self.run)
        last = self.turn if self.turn is not None else self.side
        whole = _rounded(pts, self.corner)
        self.line.set_points_as_corners(_cut(whole, self._drawn))
        self.line.set_stroke(self.color_, 2.2 * self.size, 1.0 if self._drawn > 0.01 else 0.0)
        gap = GAP if abs(last[0]) > 0.5 else GAP + 0.14 * self.size       # words above or below stand clear by half their height
        spot = whole[-1] + last * (gap - SLIDE * (1 - self._said))
        self.label.shift(spot - self._anchor.points[0])
        for letter in self.label[1:]:
            letter.set_fill(self.text_color, self._said)
        return self

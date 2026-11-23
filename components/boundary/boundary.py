"""A boundary around a group of things in a diagram: a network, a cluster, a region, a
trust zone. An outline with its label set into the top edge.

Copy this file next to scene.py:

    from boundary import Boundary

    net = Boundary(api, worker, label="Private network")
    self.play(net.draw())                              # draws on, both ways round from the label
    self.play(net.include(cache), FadeIn(cache))       # widens to take in another member
    self.play(net.exclude(cache), FadeOut(cache))      # and closes up again

It always draws behind its members. See README.md.
"""

import numpy as np
from manim import MEDIUM, Animation, CapStyleType, LineJointType, Text, VGroup, VMobject, smooth

LINE = "#3a4252"
MUTED = "#8a93a6"
SANS = "Noto Sans"


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


class _Draw(Animation):
    """Draws the outline on from the label's corner, and brings the label in after it."""

    def __init__(self, boundary, **kwargs):
        super().__init__(boundary, introducer=True, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject._lay(self.mobject.box, self.rate_func(alpha))


class _Resize(Animation):
    """Moves the outline from where it is to another box."""

    def __init__(self, boundary, box, **kwargs):
        self.box = np.array(box, dtype=float)
        super().__init__(boundary, **kwargs)

    def begin(self):
        self.start = np.array(self.mobject.box, dtype=float)
        super().begin()

    def interpolate_mobject(self, alpha):
        self.mobject._lay(self.start + (self.box - self.start) * self.rate_func(alpha), 1.0)


class Boundary(VGroup):
    """An outline around `members`, with `label` set into its top edge.

    members      the mobjects to enclose: nodes, other boundaries, anything.
    label        a word or two naming the group. None leaves the outline whole.
    color        of the outline.
    pad          the space left around the members. The top gets a little more.
    radius       of the corners.
    label_size   the label's font size.

    `boundary.members` is the list of what it encloses; `boundary.label` is the label.
    """

    def __init__(self, *members, label=None, color=LINE, pad=0.28, radius=0.16, label_size=13, **kwargs):
        super().__init__(**kwargs)
        self.members, self.pad, self.radius = list(members), pad, radius
        self.sides = [VMobject(joint_type=LineJointType.ROUND).set_stroke(color, 2).set_fill(opacity=0)
                      .set_cap_style(CapStyleType.ROUND) for _ in range(2)]
        self.label = None
        if label:
            # Measured with a capital and a descender in front, so that the middle of the
            # label's line, not of its letters, sits on the edge.
            text = Text("Hg" + label, font=SANS, font_size=label_size, weight=MEDIUM, color=MUTED)
            text.shift(-text.get_center())
            self.label = VGroup(*text[2:])
            self._label_at = self.label.get_center().copy()
        self.add(*self.sides, *([self.label] if self.label is not None else []))
        self.set_z_index(-1)                     # behind what it encloses, whatever order they are added in
        self._lay(self._around(self.members), 1.0)

    # ---- changing it

    def draw(self, run_time=1.0, rate_func=smooth):
        """The animation that draws the boundary on. Adds it to the scene."""
        return _Draw(self, run_time=run_time, rate_func=rate_func)

    def include(self, *mobjects, run_time=0.6, rate_func=smooth):
        """Take in more members. Returns the animation of the outline moving to fit; fade
        the new members in alongside it."""
        self.members += [m for m in mobjects if m not in self.members]
        return _Resize(self, self._around(self.members), run_time=run_time, rate_func=rate_func)

    def exclude(self, *mobjects, run_time=0.6, rate_func=smooth):
        """Let members go. Returns the animation of the outline closing up around the rest."""
        self.members = [m for m in self.members if m not in mobjects]
        return _Resize(self, self._around(self.members), run_time=run_time, rate_func=rate_func)

    def fit(self, run_time=0.6, rate_func=smooth):
        """The animation of the outline moving to fit its members where they are now, for
        after they have moved."""
        return _Resize(self, self._around(self.members), run_time=run_time, rate_func=rate_func)

    def refit(self):
        """Fit the members where they are now, at once."""
        return self._lay(self._around(self.members), 1.0)

    # ---- drawing it

    def _around(self, members):
        """The box (left, right, bottom, top) that encloses these members, with padding."""
        if not members:
            return self.box
        left = min(m.get_left()[0] for m in members) - self.pad
        right = max(m.get_right()[0] for m in members) + self.pad
        bottom = min(m.get_bottom()[1] for m in members) - self.pad
        top = max(m.get_top()[1] for m in members) + self.pad + 0.14
        if self.label is not None:              # wide enough to hold the label in its top edge
            right = max(right, left + 2 * self.radius + self.label.width + 0.6)
        return (left, right, bottom, top)

    def _lay(self, box, a):
        """Draw the boundary around `box`, `a` (0..1) of the way through appearing."""
        self.box = tuple(float(v) for v in box)
        x0, x1, y0, y1 = self.box
        r = min(self.radius, (x1 - x0) / 2, (y1 - y0) / 2)
        # The label sits in a gap in the top edge, just after the top-left corner. The
        # outline is one path that starts after the gap, goes clockwise, and ends before it.
        gap = (0.1, 0.3 + self.label.width) if self.label is not None else (0.2, 0.2)
        pts = [[x0 + r + gap[1], y1]]
        for cx, cy, a0 in ((x1 - r, y1 - r, 90), (x1 - r, y0 + r, 0), (x0 + r, y0 + r, -90), (x0 + r, y1 - r, 180)):
            for angle in np.linspace(np.radians(a0), np.radians(a0 - 90), 10):
                pts.append([cx + r * np.cos(angle), cy + r * np.sin(angle)])
        pts.append([x0 + r + gap[0], y1])
        pts = np.array([[x, y, 0.0] for x, y in pts])
        cum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])

        def cut(s0, s1):
            def at(s):
                i = min(int(np.searchsorted(cum, s, "right")) - 1, len(pts) - 2)
                return pts[i] + (s - cum[i]) / max(cum[i + 1] - cum[i], 1e-9) * (pts[i + 1] - pts[i])
            return [at(s0), *[pts[i] for i in range(len(pts)) if s0 < cum[i] < s1], at(s1)]

        # It draws on from both ends of the path at once, so the two halves meet at the bottom.
        half = cum[-1] / 2 * _ease(a)
        for side, (lo, hi) in zip(self.sides, ((0.0, half), (cum[-1] - half, cum[-1]))):
            if hi - lo < 1e-3:
                side.set_points_as_corners([pts[0], pts[0]]).set_stroke(opacity=0)
            else:
                side.set_points_as_corners(cut(lo, hi)).set_stroke(opacity=1)
        if self.label is not None:              # the label follows a moment after, sliding into place
            shown = _ease((a - 0.25) / 0.5)
            spot = np.array([x0 + r + 0.2 + self.label.width / 2 - 0.06 * (1 - shown), y1, 0.0])
            self.label.shift(spot - (self.label.get_center() - self._label_at) - self._label_at)
            self.label.set_opacity(shown)
        return self

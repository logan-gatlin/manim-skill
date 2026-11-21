"""A run log: a list of steps that each spin while they run and get a check when done.

Copy this file and the skill's code_font.py next to scene.py:

    from log import log

    done = ValueTracker(0)
    steps = log(done, [("lint", 4), ("build", 21), ("test", 38), ("deploy", 9)])
    self.add(steps)
    self.play(done.animate.set_value(1), run_time=8, rate_func=linear)

The tracker holds progress through the whole list, from 0 to 1, each step taking an equal
share. A step is (name, seconds): the timer counts up to `seconds` while the step runs and
shows it when the step is done. A bare name has no timer. See README.md.
"""

import numpy as np
from manim import ORIGIN, LEFT, RIGHT, Arc, CapStyleType, Circle, Dot, LineJointType, ManimColor, RoundedRectangle, Text, VGroup, VMobject, interpolate_color, smooth

from code_font import MONO

PANEL = "#141821"
LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
AMBER, GREEN = "#fbbf24", "#4ade80"

R = 0.085                 # the spinner's radius
BALL = 0.045              # the ball it collapses into
SPIN = 5.5                # its speed, radians per second
COLLAPSE = 0.24           # seconds for the spinner to collapse into the ball...
MORPH = 0.3               # ...and for the ball to open out into the check
CHECK = np.array([[-0.074, 0.0, 0], [-0.022, -0.054, 0], [0.084, 0.056, 0]])


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _mark(center, t, running_for, done_for):
    """The mark at the start of a line. Waiting: a small dot. Running: a spinner. Finishing:
    the spinner closes and collapses into a small solid ball as it turns green; the ball
    slides to the check's corner, shrinking into the line, as the check's two strokes grow
    out of it; then the check settles with a small spring."""
    center = np.array(center, dtype=float)
    g = VGroup()
    if running_for is None:
        return g.add(Dot(center, radius=0.035, color=LINE))
    if done_for is None or done_for < COLLAPSE:
        q = 0.0 if done_for is None else smooth(done_for / COLLAPSE)
        color, r = _mix(AMBER, GREEN, q), R + (BALL - R) * q
        arrive = min(1.0, running_for / 0.2)             # the spinner fades up as the waiting dot fades
        if arrive < 1:
            g.add(Dot(center, radius=0.035, color=LINE, fill_opacity=1 - arrive))
        g.add(Circle(radius=r, stroke_color=color, stroke_width=2.5, stroke_opacity=(0.25 + 0.75 * q) * arrive,
                     fill_color=color, fill_opacity=q ** 2).move_to(center))
        arc = Arc(radius=r, start_angle=-t * SPIN, angle=1.7 + (2 * np.pi - 1.7) * q, arc_center=center,
                  stroke_color=color, stroke_width=2.5, stroke_opacity=arrive)
        return g.add(arc.set_cap_style(CapStyleType.ROUND))
    since = done_for - COLLAPSE
    q = 1 - (1 - min(1.0, since / MORPH)) ** 3
    settle = max(0.0, since - MORPH)
    spring = 1 + 0.2 * np.exp(-8 * settle) * np.sin(14 * settle)
    corner = CHECK[1] * q                                # the ball, on its way to the check's corner
    pts = [center + (corner + (end - corner) * q) * spring for end in (CHECK[0], CHECK[1], CHECK[2])]
    pts[1] = center + corner * spring
    line = VMobject(joint_type=LineJointType.ROUND).set_points_as_corners(pts)
    g.add(line.set_stroke(GREEN, 3).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND))
    return g.add(Dot(pts[1], radius=BALL + (0.015 - BALL) * q, color=GREEN))


def log(tracker, steps=(("lint", 4), ("build", 21), ("test", 38), ("deploy", 9)), width=5.2, row_gap=0.38,
        size=15, unit="s", panel=True):
    """A log `width` wide, centred where you put it.

    tracker   a ValueTracker from 0 to 1: progress through the whole list.
    steps     (name, seconds) pairs, or bare names for steps with no timer.
    unit      written after each time; `panel=False` leaves out the box behind the lines.
    """
    names = [s if isinstance(s, str) else s[0] for s in steps]
    seconds = [None if isinstance(s, str) else s[1] for s in steps]
    n = len(names)
    top = (n - 1) / 2 * row_gap
    left, right = -width / 2 + 0.35, width / 2 - 0.3
    cache = {}

    def text(s, size_, color):
        if (s, size_) not in cache:
            if len(cache) > 400:
                cache.clear()
            cache[s, size_] = Text(s, font=MONO, font_size=size_)
        return cache[s, size_].copy().set_color(color)

    def draw(p, t, started, finished):
        g = VGroup()
        if panel:
            g.add(RoundedRectangle(corner_radius=0.12, width=width, height=n * row_gap + 0.2, stroke_color=LINE,
                                   stroke_width=2, fill_color=PANEL, fill_opacity=1))
        for i in range(n):
            y, f = top - i * row_gap, float(np.clip(p * n - i, 0, 1))
            running_for = None if started[i] is None else t - started[i]
            done_for = None if finished[i] is None else t - finished[i]
            g.add(_mark([left, y, 0], t, running_for, done_for))
            name = text(names[i], size, INK if f > 0 else MUTED).move_to([left + 0.3, y, 0], aligned_edge=LEFT)
            g.add(name)
            if f <= 0 or seconds[i] is None:
                continue
            took = f"{seconds[i] * f:.1f}{unit}" if f < 1 else f"{seconds[i]:g}{unit}"
            settled = 0.0 if done_for is None else done_for / 0.3      # the time cools from amber as the step ends
            time = text(took, size - 2, _mix(AMBER, MUTED, settled)).move_to([right, y, 0], aligned_edge=RIGHT)
            g.add(time)
            # a dotted leader runs from the name toward the time as the step progresses
            a, b = name.get_right()[0] + 0.2, right - (0.105 * (size - 2) / 13) * len(f"{seconds[i]:.1f}{unit}") - 0.2
            for x in np.arange(a, a + (b - a) * f, 0.11):
                g.add(Dot([x, y - 0.05, 0], radius=0.014, color=LINE))
        return g

    # The holder carries one invisible point, its anchor: the renderer then re-reads its
    # children every frame, and moving the holder moves where the next drawing lands.
    holder = VMobject(stroke_width=0, fill_opacity=0)
    holder.set_points_as_corners([ORIGIN, ORIGIN])
    # When each step started and finished, by the holder's own clock. Steps already under
    # way or done when the log is made count as long since, so they show settled.
    p0 = float(tracker.get_value())
    state = {"t": 0.0,
             "started": [-1e9 if p0 * n > i else None for i in range(n)],
             "finished": [-1e9 if p0 * n >= i + 1 else None for i in range(n)]}

    def redraw(m, dt=0):
        state["t"] += dt
        p = float(tracker.get_value())
        for i in range(n):
            f = p * n - i
            if f <= 0:
                state["started"][i] = None
            elif state["started"][i] is None:
                state["started"][i] = state["t"]
            if f < 1:
                state["finished"][i] = None
            elif state["finished"][i] is None:
                state["finished"][i] = state["t"]
        for old in m.submobjects:
            old.set_opacity(0)
        m.submobjects = [draw(p, state["t"], state["started"], state["finished"]).shift(m.points[0])]

    redraw(holder)
    return holder.add_updater(redraw)

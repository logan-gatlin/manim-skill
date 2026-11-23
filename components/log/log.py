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
from manim import ORIGIN, LEFT, RIGHT, Arc, CapStyleType, Circle, LineJointType, ManimColor, RoundedRectangle, Text, VGroup, VMobject, interpolate_color, smooth

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
LEAP = 0.2                # seconds: a longer step than this is not a frame of video but skipped time
CHECK = np.array([[-0.074, 0.0, 0], [-0.022, -0.054, 0], [0.084, 0.056, 0]])


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


# The log is drawn afresh for every frame, so what it is drawn from has to be quick to make:
# Manim takes 0.2 ms to build a Dot and 10 ms to copy a line of Text.
ROUND = Circle(radius=1).points      # the points of a circle of radius 1


def _shape(points, **style):
    """A bare shape with these points and this style."""
    m = VMobject(**style)
    m.points = points
    return m


def _plain(mob):
    """The letters of a Text as bare shapes that look the same. A Text carries the SVG it
    was read from, which makes each copy of it slow; copies of these are quick."""
    return VGroup(*[_shape(part.points.copy()).match_style(part) for part in mob.family_members_with_points()])


def _dot(center, radius, color, fill_opacity=1.0):
    return _shape(ROUND * radius + center, color=color, stroke_width=0, fill_opacity=fill_opacity)


def _mark(center, t, running_for, done_for):
    """The mark at the start of a line. Waiting: a small dot. Running: a spinner. Finishing:
    the spinner closes and collapses into a small solid ball as it turns green; the ball
    slides to the check's corner, shrinking into the line, as the check's two strokes grow
    out of it; then the check settles with a small spring."""
    center = np.array(center, dtype=float)
    g = VGroup()
    if running_for is None:
        return g.add(_dot(center, 0.035, LINE))
    if done_for is None or done_for < COLLAPSE:
        q = 0.0 if done_for is None else smooth(done_for / COLLAPSE)
        color, r = _mix(AMBER, GREEN, q), R + (BALL - R) * q
        arrive = min(1.0, running_for / 0.2)             # the spinner fades up as the waiting dot fades
        if arrive < 1:
            g.add(_dot(center, 0.035, LINE, 1 - arrive))
        g.add(_shape(ROUND * r + center, stroke_color=color, stroke_width=2.5, stroke_opacity=(0.25 + 0.75 * q) * arrive,
                     fill_color=color, fill_opacity=q ** 2))
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
    return g.add(_dot(pts[1], BALL + (0.015 - BALL) * q, GREEN))


class _Holder(VMobject):
    """What a live drawing hangs from. It carries one invisible point, its anchor: the
    renderer then re-reads its children every frame, and moving it moves where the next
    drawing lands. A copy of it is a still picture, which does not redraw itself: FadeIn,
    FadeOut and the like work on copies, and fail if a copy changes under them."""

    def __init__(self):
        super().__init__(stroke_width=0, fill_opacity=0)
        self.set_points_as_corners([ORIGIN, ORIGIN])

    def __deepcopy__(self, memo):
        twin = super().__deepcopy__(memo)
        twin.updaters = []
        return twin


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
    cache, type_ = {}, {}
    box = RoundedRectangle(corner_radius=0.12, width=width, height=n * row_gap + 0.2, stroke_color=LINE,
                           stroke_width=2, fill_color=PANEL, fill_opacity=1)

    leader = _dot(ORIGIN, 0.014, LINE)          # one dot of a leader: a copy is quicker than a new one

    def text(s, size_, color):
        if (s, size_) not in cache:
            if len(cache) > 400:
                cache.clear()
            cache[s, size_] = _plain(Text(s, font=MONO, font_size=size_))
        return cache[s, size_].copy().set_color(color)

    def reading(s, size_, color):
        """A time that changes with every frame. A new Text for each would take 10 ms, so
        it is put together from the shape of each character, made once: in a font whose
        characters are all one width that gives the same letters in the same places."""
        if not s.isascii():
            return text(s, size_, color)
        if size_ not in type_:
            pair = Text("00", font=MONO, font_size=size_)
            type_[size_] = {" ": pair[1].get_center()[0] - pair[0].get_center()[0]}      # under " ", the advance
        made, row = type_[size_], VGroup()
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            if ch not in made:
                pair = Text("0" + ch, font=MONO, font_size=size_)
                made[ch] = _shape(pair[1].points - pair[0].get_center()).match_style(pair[1])
            row.add(made[ch].copy().shift([i * made[" "], 0, 0]))
        return row.set_color(color)

    def draw(p, t, started, finished):
        g = VGroup()
        if panel:
            g.add(box.copy())
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
            time = reading(took, size - 2, _mix(AMBER, MUTED, settled)).move_to([right, y, 0], aligned_edge=RIGHT)
            g.add(time)
            # a dotted leader runs from the name toward the time as the step progresses
            a, b = name.get_right()[0] + 0.2, right - (0.105 * (size - 2) / 13) * len(f"{seconds[i]:.1f}{unit}") - 0.2
            for x in np.arange(a, a + (b - a) * f, 0.11):
                g.add(leader.copy().shift([x, y - 0.05, 0]))
        return g

    holder = _Holder()
    # When each step started and finished, by the holder's own clock. Steps already under
    # way or done when the log is made count as long since, so they show settled.
    p0 = float(tracker.get_value())
    state = {"t": 0.0, "p": p0,
             "started": [-1e9 if p0 * n > i else None for i in range(n)],
             "finished": [-1e9 if p0 * n >= i + 1 else None for i in range(n)]}

    def redraw(m, dt=0):
        state["t"] += dt
        p, was = float(tracker.get_value()), state["p"]
        state["p"] = p

        def when(share):
            """When progress passed `share`. That is now, unless far more time than a
            frame's has gone by at once (a draft that skips its animations takes each in a
            single step): then progress is taken to have moved evenly through it, so that
            steps which ended early in it show as long done."""
            if dt <= LEAP or p <= was:
                return state["t"]
            return state["t"] - dt * float(np.clip((p - share) / (p - was), 0, 1))

        for i in range(n):
            f = p * n - i
            if f <= 0:
                state["started"][i] = None
            elif state["started"][i] is None:
                state["started"][i] = when(i / n)
            if f < 1:
                state["finished"][i] = None
            elif state["finished"][i] is None:
                state["finished"][i] = when((i + 1) / n)
        for old in m.submobjects:
            old.set_opacity(0)
        m.submobjects = [draw(p, state["t"], state["started"], state["finished"]).shift(m.points[0])]

    redraw(holder)
    return holder.add_updater(redraw)

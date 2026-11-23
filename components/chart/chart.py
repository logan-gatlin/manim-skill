"""A live chart: one metric as a line that scrolls past, turning red wherever it is over a
threshold.

Copy this file and the skill's code_font.py next to scene.py:

    from chart import chart

    latency = ValueTracker(45)
    c = chart(latency, limit=100, unit=" ms")
    self.add(c)                                               # fades in, already showing a few seconds of history
    self.wait(2)                                              # it scrolls by itself
    self.play(latency.animate.set_value(130), run_time=1.5)   # the line climbs, and turns red over 100
    self.wait(2)

The chart reads the tracker every frame and keeps its own clock. See README.md.
"""

import numpy as np
from manim import ORIGIN, CapStyleType, Dot, LineJointType, ManimColor, Rectangle, Text, VGroup, VMobject, interpolate_color

from code_font import MONO

LINE = "#3a4252"
INK = "#eef1f6"
BLUE, RED = "#60a5fa", "#f87171"


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _stroke(points, color, width):
    m = VMobject(joint_type=LineJointType.ROUND).set_points_as_corners([[p[0], p[1], 0] for p in points])
    return m.set_stroke(color, width).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)


def _plain(mob):
    """The letters of a Text as bare shapes that look the same. A Text carries the SVG it
    was read from, which makes each copy of it slow, and the chart copies its words for
    every frame; copies of these are quick."""
    return VGroup(*[VMobject().set_points(part.points).match_style(part) for part in mob.family_members_with_points()])


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


def chart(source, limit=None, top=None, window=6.0, width=5.5, height=1.6, unit="", jitter=0.1, color=BLUE, fade_in=0.4):
    """A chart `width` by `height`, with the reading written to the right of it. Its middle
    goes where you put it.

    source    a ValueTracker holding the metric, read every frame; or a function of the
              chart's own clock, in seconds, that returns it.
    limit     the threshold: a dashed line across the chart, labelled at its left end. The
              line, its head and the reading are red wherever the metric is over it. None
              leaves it out.
    top       the value at the top of the chart; the bottom is 0. By default 1.6 times the
              limit, or 2.5 times the starting value.
    window    how many seconds of history the chart shows.
    unit      written after the reading: " ms", "%", " req/s".
    jitter    how much the line wavers by itself, so that a tracker held steady still looks
              like a live reading. 0 draws the source exactly.
    color     of the line where it is under the limit.
    fade_in   seconds the chart takes to fade in once it is added to the scene. To bring it
              in with `FadeIn` instead, pass 0, or it would fade in twice.
    """
    read = source if callable(source) else (lambda t: float(source.get_value()))
    start = float(read(0.0))
    top = top or (1.6 * limit if limit else 2.5 * max(start, 1e-6))
    s = height / 1.25                                    # text and line weights follow the chart's height
    x0, x1, y0 = -width / 2, width / 2, -height / 2
    cache = {}

    def word(text, size, color_):
        if (text, size) not in cache:
            if len(cache) > 500:
                cache.clear()
            t = Text("Hg" + text, font=MONO, font_size=size)     # measured with a capital and a descender,
            t.shift(-t.get_center())                              # so the reading doesn't bob as its digits change
            cache[text, size] = _plain(VGroup(*t[2:]))
        return cache[text, size].copy().set_color(color_)

    def waver(t):
        return jitter * top * (0.056 * np.sin(1.3 * t) + 0.038 * np.sin(3.1 * t + 1) + 0.022 * np.sin(7.3 * t + 2)) / 0.1

    def y_of(v):
        return y0 + float(np.clip(v, 0, top)) / top * height

    def over(v):
        return limit is not None and v > limit

    # What is the same in every drawing, made once and copied. An invisible box over the
    # chart and the room for its reading keeps its size the same from frame to frame, so it
    # sits where it is put.
    fixed = VGroup(Rectangle(width=width + 2.6 * s, height=height + 0.3 * s, stroke_width=0, fill_opacity=0).shift([0.5 * s, 0, 0]))
    if limit is not None:
        yl, x = y_of(limit), x0
        while x < x1:
            fixed.add(_stroke([[x, yl], [min(x + 0.08 * s, x1), yl]], LINE, 1.5 * s))
            x += 0.16 * s
        label = word(f"{limit:g}", 10 * s, LINE)
        fixed.add(label.shift([x0 - 0.12 * s - label.get_right()[0], yl, 0]))

    def draw(t, history):
        g = fixed.copy()
        # the line, cut exactly where it crosses the limit so each stretch has one color
        pts = [(x1 - (t - when) / window * width, y_of(v), over(v)) for when, v in history if when >= t - window]
        pts = pts[::max(1, len(pts) // 160)] + pts[-1:]
        run = [pts[0][:2]]
        for (xa, ya, oa), (xb, yb, ob) in zip(pts, pts[1:]):
            if oa != ob:
                k = (y_of(limit) - ya) / (yb - ya) if yb != ya else 0.5
                cross = (xa + k * (xb - xa), y_of(limit))
                g.add(_stroke(run + [cross], RED if oa else color, 2.5 * s))
                run = [cross]
            run.append((xb, yb))
        if len(run) > 1:
            g.add(_stroke(run, RED if pts[-1][2] else color, 2.5 * s))
        # the head, and the reading beside it
        now = history[-1][1]
        hot = float(np.clip((now - limit + 0.03 * top) / (0.06 * top), 0, 1)) if limit is not None else 0.0
        g.add(Dot([x1, y_of(now), 0], radius=0.055 * s, color=_mix(color, RED, hot)))
        reading = word(f"{now:.0f}{unit}", 13 * s, _mix(INK, RED, hot))
        return g.add(reading.shift([x1 + 0.3 * s - reading.get_left()[0], y_of(now), 0]))

    holder = _Holder()
    # The chart starts with a window of history already on it, at the starting value.
    step = 1 / 60
    state = {"t": 0.0, "seen": 0.0, "value": start, "history": [(when, (float(read(when)) if callable(source) else start) + waver(when))
                                   for when in np.arange(-window, step / 2, step)]}

    def redraw(m, dt=0):
        if dt > 0:
            before, was = state["t"], state["value"]
            state["t"] += dt
            state["seen"] += dt
            state["value"] = float(read(state["t"]))
            # One reading for each frame. When far more time than a frame's goes by at once
            # (a draft that skips its animations takes each in a single step), the readings
            # in between are filled in, a tracker being taken to have moved evenly, so that
            # the line still wavers as it will in the video.
            parts = int(dt / step) if dt > 0.1 else 1
            for k in range(1, parts):
                when = before + dt * k / parts
                value = float(read(when)) if callable(source) else was + (state["value"] - was) * k / parts
                state["history"].append((when, value + waver(when)))
            state["history"].append((state["t"], state["value"] + waver(state["t"])))
            while state["history"][1][0] < state["t"] - window:
                state["history"].pop(0)
        for old in m.submobjects:
            old.set_opacity(0)
        drawing = draw(state["t"], state["history"]).shift(m.points[0])
        # It fades in over its first moments on screen. Before its first frame (a still, or
        # a chart not yet added) it is drawn whole.
        shown = 1.0 if state["seen"] == 0 or fade_in <= 0 else min(1.0, state["seen"] / fade_in)
        if shown < 1:
            for part in drawing.family_members_with_points():
                part.set_stroke(opacity=part.get_stroke_opacity() * shown)
                part.set_fill(opacity=part.get_fill_opacity() * shown)
        m.submobjects = [drawing]

    redraw(holder)
    return holder.add_updater(redraw)

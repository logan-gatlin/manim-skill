"""A timeline of named rows, each with one or more bars that fill as time passes.

Copy this file and the skill's code_font.py next to scene.py:

    from timeline import timeline

    now = ValueTracker(0)
    chart = timeline(now, [
        ("Lint", (0, 4)),
        ("Build", (2, 20)),                  # starts before Lint ends: the bars overlap in time
        ("Test", [(20, 31), (36, 44)]),      # two runs in one row, with a pause between
        ("Deploy", (44, 50)),
    ])
    self.add(chart)
    self.play(now.animate.set_value(50), run_time=6, rate_func=linear)

`now` is the time the cursor is at, in the same units as the bars. A bar appears as the
cursor reaches it and grows with the cursor, and its duration pops out of its end when it
finishes. See README.md.
"""

import numpy as np
from manim import ORIGIN, PI, LEFT, RIGHT, CapStyleType, Rectangle, RoundedRectangle, Text, Triangle, VGroup, VMobject

POP = 0.4       # seconds a duration takes to pop out of its bar

from code_font import MONO

INK = "#eef1f6"
MUTED = "#8a93a6"
DARK = "#0d1118"
TEAL, BLUE, VIOLET, PINK = "#2dd4bf", "#60a5fa", "#a78bfa", "#f472b6"
AMBER, GREEN = "#fbbf24", "#4ade80"
SANS = "Noto Sans"


def _bar(x0, x1, y, h, color):
    w = max(x1 - x0, 0.02)
    return RoundedRectangle(corner_radius=min(0.07, w / 2, h / 2), width=w, height=h, stroke_width=0,
                            fill_color=color, fill_opacity=1).move_to([(x0 + x1) / 2, y, 0])


def timeline(now, rows, width=4.5, row_gap=0.37, bar=0.22, colors=(BLUE, VIOLET, TEAL, GREEN, AMBER, PINK),
             unit="s", span=None, durations=True, cursor=True, label_size=14):
    """A timeline whose bars span `width`, centred where you put it; row names hang off its
    left side.

    now        a ValueTracker holding the current time.
    rows       (name, bars) pairs, top row first. `bars` is one (start, end) or a list of
               them, for work that stops and starts again. Rows may overlap in time freely.
    colors     one per row, repeating.
    unit       written after each duration ("s", " min", ...); `durations=False` leaves them out.
    span       (first, last) time shown; by default from the earliest start to the latest end.
    cursor     the line that marks `now`.
    """
    rows = [(name, [bars] if np.isscalar(bars[0]) else list(bars)) for name, bars in rows]
    first, last = span or (min(a for _, bars in rows for a, _ in bars), max(b for _, bars in rows for _, b in bars))
    scale = width / (last - first)
    top = (len(rows) - 1) / 2 * row_gap
    cache = {}

    def text(s, size, color, font=SANS):
        if (s, size, font) not in cache:
            cache[s, size, font] = Text(s, font=font, font_size=size)
        return cache[s, size, font].copy().set_color(color)

    def x_of(time):
        return -width / 2 + (time - first) * scale

    def pop(label, since):
        """How big and how solid a duration is `since` seconds after its bar finished: it
        grows from half size, a little past full size, and settles."""
        u = min(1.0, since / POP)
        back = 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2      # eases out, overshooting
        return label.scale(0.5 + 0.5 * back).set_opacity(min(1.0, u * 2.5)), 1 - (1 - u) ** 3

    def draw(time, finished, clock):
        behind, g = VGroup(), VGroup()   # a duration beside its bar is drawn under the bars: it comes out from behind
        # An invisible box over the whole chart keeps its size the same however much of it
        # is drawn, so it sits where it is put whether it is placed empty or part-way through.
        bottom = top - (len(rows) - 1) * row_gap
        behind.add(Rectangle(width=width, height=top - bottom + 0.6, stroke_width=0, fill_opacity=0)
                   .move_to([0, (top + bottom) / 2 + 0.03, 0]))
        for i, (name, bars) in enumerate(rows):
            y, color = top - i * row_gap, colors[i % len(colors)]
            started = any(time > a for a, _ in bars)
            g.add(text(name, label_size, INK if started else MUTED).move_to([-width / 2 - 0.25, y, 0], aligned_edge=RIGHT))
            for j, (a, b) in enumerate(bars):
                x0, x1 = x_of(a) + 0.02, x_of(b) - 0.02       # a hair of space between touching bars
                if time > a:
                    g.add(_bar(x0, min(x_of(min(time, b)), x1), y, bar, color))
                if durations and time >= b:
                    label = text(f"{b - a:g}{unit}", 11, MUTED, MONO)
                    width_, since = label.width, clock - finished[i, j]
                    room = (x_of(bars[j + 1][0]) if j + 1 < len(bars) else np.inf) - x1
                    if room >= width_ + 0.2:                    # beside the bar when there is room:
                        label, out = pop(label, since)          # it slides out of the bar's end
                        behind.add(label.move_to([x1 - 0.14 + 0.24 * out, y, 0], aligned_edge=LEFT))
                    elif x1 - x0 >= width_ + 0.14:              # else inside it
                        g.add(pop(label.set_color(DARK), since)[0].move_to([(x0 + x1) / 2, y, 0]))
        if cursor:
            x = x_of(float(np.clip(time, first, last)))
            line = VMobject().set_points_as_corners([[x, top + 0.26, 0], [x, top - (len(rows) - 1) * row_gap - 0.24, 0]])
            g.add(line.set_stroke(INK, 1.5, 0.8).set_cap_style(CapStyleType.ROUND))
            g.add(Triangle(color=INK, fill_opacity=1, stroke_width=0).scale(0.06).rotate(PI).move_to([x, top + 0.3, 0]))
        return VGroup(behind, g)

    # The holder carries one invisible point, its anchor: the renderer then re-reads its
    # children every frame, and moving the holder moves where the next drawing lands.
    holder = VMobject(stroke_width=0, fill_opacity=0)
    holder.set_points_as_corners([ORIGIN, ORIGIN])
    # When each bar finished, by the holder's own clock. Bars already finished when the
    # timeline is made count as long since, so their durations show settled.
    state = {"t": 0.0, "finished": {(i, j): -1e9 for i, (_, bars) in enumerate(rows)
                                    for j, (_, b) in enumerate(bars) if float(now.get_value()) >= b}}

    def redraw(m, dt=0):
        state["t"] += dt
        time = float(now.get_value())
        for i, (_, bars) in enumerate(rows):
            for j, (_, b) in enumerate(bars):
                if time < b:
                    state["finished"].pop((i, j), None)
                else:
                    state["finished"].setdefault((i, j), state["t"])
        for old in m.submobjects:
            old.set_opacity(0)
        m.submobjects = [draw(time, state["finished"], state["t"]).shift(m.points[0])]

    redraw(holder)
    return holder.add_updater(redraw)

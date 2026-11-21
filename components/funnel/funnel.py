"""A funnel that dots flow through, thinning out at each stage.

Copy this file next to scene.py:

    from funnel import funnel

    f = funnel([("Visit", 0.6), ("Sign up", 0.5), ("Activate", 0.6), ("Pay", 1.0)])
    self.add(f)           # already full of dots, and flowing
    self.wait(8)          # it runs by itself

Each stage is (name, share kept): the share of the dots entering that stage that get
through it. The walls narrow in the same proportion, so the picture is a true funnel chart
with the flow drawn on it. Dots fade and grow in as they arrive at the wide end, take their
color from where they are along the funnel, fade out as they travel on when they are lost,
and pop with a ring as they leave the narrow end. See README.md.
"""

import numpy as np
from manim import ORIGIN, CapStyleType, Circle, Dot, LineJointType, ManimColor, Rectangle, Text, VGroup, VMobject, interpolate_color, smooth

LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
TEAL, BLUE, VIOLET, GREEN = "#2dd4bf", "#60a5fa", "#a78bfa", "#4ade80"
SANS = "Noto Sans"

ENTRY = 0.6     # dots appear this far outside the wide end
FADE = 0.6      # a lost dot fades over this distance, still travelling
POP = 0.28      # a dot that makes it swells over this distance past the narrow end...
BURST = 0.45    # ...then bursts into a ring for this many seconds


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _stroke(pts, color, width, opacity=1.0):
    m = VMobject(joint_type=LineJointType.ROUND).set_points_as_corners([np.array([q[0], q[1], 0.0]) for q in pts])
    return m.set_stroke(color, width, opacity).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)


def _chance(k, j):
    """A repeatable number in 0..1 for dot k (the j-th one it needs), so a dot keeps its fate
    and its lane from frame to frame."""
    v = np.sin(k * 12.9898 + j * 78.233) * 43758.5453
    return float(v - np.floor(v))


def funnel(stages=(("Visit", 0.6), ("Sign up", 0.5), ("Activate", 0.6), ("Pay", 1.0)), width=5.8, height=1.3,
           colors=(BLUE, VIOLET, TEAL, GREEN), rate=9.0, speed=0.9, dot=0.055, label_size=14, filled=True):
    """A funnel `width` long and `height` tall at its wide end, centred where you put it.

    stages   (name, kept) pairs, or just names for stages that lose nothing. `kept` is the
             share of the dots entering the stage that get through it.
    colors   the colors the dots pass through from the wide end to the narrow end.
    rate     dots entering per second; `speed` is how fast they travel, in units per second.
    filled   the funnel starts with dots already all along it. False starts it empty.
    """
    names = [s if isinstance(s, str) else s[0] for s in stages]
    kept = [1.0 if isinstance(s, str) else float(s[1]) for s in stages]
    n = len(names)
    xs = np.linspace(-width / 2, width / 2, n + 1)                  # where each stage starts and ends
    half = np.maximum(height / 2 * np.cumprod([1.0, *kept]), 2.4 * dot)   # the wall's height there
    labels = [Text(name, font=SANS, font_size=label_size, color=MUTED) for name in names]
    life = (ENTRY + width + POP) / speed + BURST                   # how long a dot can be on screen

    def color_at(x):
        u = float(np.clip((x - xs[0]) / width, 0, 1)) * (len(colors) - 1)
        i = min(int(u), len(colors) - 2)
        return _mix(colors[i], colors[i + 1], u - i)

    def lost_at(k):
        """Where dot k starts to fade and how far it travels while fading, or None if it
        makes it through. It is gone before the end of the stage that lost it."""
        for i in range(n):
            if _chance(k, i) > kept[i]:
                stage = xs[i + 1] - xs[i]
                fade = min(FADE, 0.55 * stage)
                return xs[i] + 0.06 * stage + _chance(k, 20 + i) * (0.9 * stage - fade), fade
        return None

    def draw(t):
        # An invisible box over the walls keeps the funnel's size the same from frame to
        # frame, so it sits where it is put whatever the dots are doing.
        g = VGroup(Rectangle(width=width, height=2 * half[0], stroke_width=0, fill_opacity=0))
        top = list(zip(xs, half))
        g.add(_stroke(top, LINE, 3), _stroke([(x, -h) for x, h in top], LINE, 3))
        for i in range(1, n):
            g.add(_stroke([(xs[i], half[i]), (xs[i], -half[i])], LINE, 2, 0.7))
        for i, label in enumerate(labels):
            g.add(label.copy().move_to([(xs[i] + xs[i + 1]) / 2, half[0] + 0.28, 0]))
        for k in range(max(0, int(np.ceil((t - life) * rate)) - 1), int(np.floor(t * rate)) + 2):
            # each dot sets off a little early or late and keeps to a lane of its own, so the
            # flow looks loose rather than marching in rows
            age = t - (k + _chance(k, 41) - 0.5) / rate
            if age < 0:
                continue
            x = xs[0] - ENTRY + speed * age
            lane = _chance(k, 40) * 2 - 1
            opacity, size, color, ring = 1.0, 1.0, None, None
            lost = lost_at(k)
            if x < xs[0]:                               # arriving: fades and grows in, closing up
                e = smooth((x - xs[0] + ENTRY) / ENTRY)
                opacity, size = e, 0.4 + 0.6 * e
                lane *= 1 + 0.3 * (1 - e)
            elif lost is not None and x > lost[0]:      # lost: keeps moving as it fades and shrinks
                d = x - lost[0]
                if d >= lost[1]:
                    continue
                q = smooth(d / lost[1])
                opacity, size = 1 - q, 1 - 0.4 * q
            elif x > xs[-1]:                            # made it: swells, then bursts into a ring
                e = x - xs[-1]
                if e < POP:
                    q = smooth(e / POP)
                    size, color = 1 + 0.7 * q, _mix(colors[-1], INK, 0.6 * q)
                else:
                    u = (e - POP) / speed / BURST
                    if u >= 1:
                        continue
                    x = xs[-1] + POP + (e - POP) * 0.3
                    size, color, opacity = 1.7, _mix(colors[-1], INK, 0.6), max(0.0, 1 - 2.5 * u)
                    ring = Circle(radius=dot * 1.7 + 3.2 * dot * (1 - (1 - u) ** 2), stroke_color=colors[-1],
                                  stroke_width=2.5, stroke_opacity=(1 - u) ** 1.5)
            wall = float(np.interp(x, xs, half))
            p = np.array([x, lane * max(wall - dot - 0.05, 0.0), 0.0])
            if opacity > 0.01:
                g.add(Dot(p, radius=dot * size, color=color or color_at(x), fill_opacity=opacity))
            if ring is not None:
                g.add(ring.move_to(p))
        return g

    # The holder carries one invisible point, its anchor: the renderer then re-reads its
    # children every frame, and moving the holder moves where the next drawing lands.
    holder = VMobject(stroke_width=0, fill_opacity=0)
    holder.set_points_as_corners([ORIGIN, ORIGIN])
    state = {"t": (ENTRY + width) / speed if filled else 0.0}

    def redraw(m, dt=0):
        state["t"] += dt
        for old in m.submobjects:
            old.set_opacity(0)
        m.submobjects = [draw(state["t"]).shift(m.points[0])]

    redraw(holder)
    return holder.add_updater(redraw)

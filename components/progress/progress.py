"""Live progress indicators for Manim scenes: ring, liquid, stepper, phases, grid_fill.

Copy this file next to scene.py (and icons.py too when you use `stepper`, which draws its
checkmarks with an icon):

    from progress import liquid

    done = ValueTracker(0)                       # progress, 0..1
    bar = liquid(done, width=5).to_edge(DOWN)
    self.play(FadeIn(bar))
    self.play(done.animate.set_value(0.8), run_time=3)

Each function returns a mobject that redraws itself from the tracker on every frame, and keeps
its own clock for ambient motion (the liquid's waves, the stepper's pulse). When the tracker
reaches 1 the indicator celebrates for about a second (a springy pop, a white flash, a
shockwave and sparks), so finishing feels like an event. Give the scene that second
(`self.wait(1)`) before moving on. One created already full doesn't celebrate. Set its size with
the function's arguments, then place it with move_to / next_to / to_edge / shift. Don't scale
or Transform it: the next redraw would undo that. Example images are in images/.
"""

import numpy as np
from manim import (
    BOLD, DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP, WHITE,
    Arc, CapStyleType, Circle, Dot, Intersection, Line, ManimColor, Polygon, Rectangle,
    RoundedRectangle, Text, VGroup, VMobject, interpolate_color, smooth,
)

TRACK = "#252a35"       # empty track, filled
TRACK_LINE = "#3a4252"  # empty track, outlined
INK = "#eef1f6"
MUTED = "#8a93a6"
DARK = "#0d1118"
TEAL, BLUE, VIOLET, CYAN, GREEN = "#2dd4bf", "#60a5fa", "#a78bfa", "#22d3ee", "#4ade80"

SANS = "Noto Sans"
MONO = "DejaVu Sans Mono"


DONE = 0.999       # progress that counts as complete
CELEBRATION = 1.0  # seconds the completion effect lasts


def live(draw, tracker):
    """A mobject redrawn every frame as draw(p, t, since), from `tracker` (p, 0..1), a clock
    (t, seconds) and `since`, the seconds since p reached 1 (None while it hasn't).

    Why not always_redraw: during play() the Cairo renderer draws a list of point-bearing
    mobjects frozen when play() starts. Parts a redraw creates later (the fill, which appears
    once p > 0; a percentage that gains a digit) would never show, and the frozen parts would
    keep showing stale. Here the holder carries one invisible point, its anchor, so it is in
    that list and the camera re-reads its current children each frame; discarded drawings are
    hidden. Moving the holder moves the anchor, so the next drawing lands in the same place.
    """
    holder = VMobject(stroke_width=0, fill_opacity=0)
    holder.set_points_as_corners([ORIGIN, ORIGIN])
    # Created already full: count it as finished long ago, so it shows settled, not celebrating.
    state = {"t": 0.0, "done_at": -1e9 if tracker.get_value() >= DONE else None}

    def redraw(m, dt=0):
        state["t"] += dt
        p = float(tracker.get_value())
        if p < DONE:
            state["done_at"] = None
        elif state["done_at"] is None:
            state["done_at"] = state["t"]
        since = None if state["done_at"] is None else state["t"] - state["done_at"]
        for old in m.submobjects:
            old.set_opacity(0)
        m.submobjects = [draw(p, state["t"], since).shift(m.points[0])]

    redraw(holder)
    return holder.add_updater(redraw)


# ------------------------------------------------------------------- completion effects


def _phase(since, dur, delay=0.0):
    """How far (0..1) an effect of length `dur` starting `delay` after completion has got, or
    None when it isn't running."""
    if since is None:
        return None
    k = (since - delay) / dur
    return k if 0 <= k < 1 else None


def _spring(since, amp=0.08, delay=0.0):
    """A scale factor: a quick swell on completion that settles in a damped wobble."""
    k = _phase(since, CELEBRATION, delay)
    if k is None:
        return 1.0
    u = k * CELEBRATION
    return 1 + amp * np.exp(-6 * u) * np.sin(16 * u)


def _flash(shape, since, peak=0.8, dur=0.45):
    """A white copy of `shape` laid over it, fading out after completion."""
    k = _phase(since, dur)
    if k is None:
        return VGroup()
    a = peak * (1 - k) ** 2
    c = shape.copy()
    for m in c.family_members_with_points():
        m.set_fill(WHITE, a if m.get_fill_opacity() > 0 else 0)
        m.set_stroke(WHITE, opacity=a if m.get_stroke_width() > 0 else 0)
    return c


def _shockwave(shape, since, color, reach=0.5, width=6, waves=2, dur=0.75):
    """Outlines of `shape` racing outwards and fading, one after another."""
    g = VGroup()
    for i in range(waves):
        k = _phase(since, dur, 0.1 * i)
        if k is None:
            continue
        d = reach * (1 - 0.35 * i) * (1 - (1 - k) ** 3)
        o = shape.copy().set_fill(opacity=0)
        o.set_stroke(color, width * (1 - k) + 0.5, opacity=(1 - k) ** 1.5)
        o.stretch((shape.width + 2 * d) / shape.width, 0)
        o.stretch((shape.height + 2 * d) / shape.height, 1)
        g.add(o)
    return g


def _sparks(center, since, color, angles, r0, reach=0.5, length=0.2, dur=0.6):
    """Short streaks flying out from `center` along `angles`, starting `r0` from it."""
    k = _phase(since, dur)
    g = VGroup()
    if k is None:
        return g
    a = r0 + reach * (1 - (1 - k) ** 2)
    b = a + length * (1 - k) + 0.02
    center = np.array(center, dtype=float)
    for th in angles:
        u = np.array([np.cos(th), np.sin(th), 0])
        line = Line(center + a * u, center + b * u, stroke_color=color,
                    stroke_width=3.5 * (1 - k) + 0.5, stroke_opacity=1 - k ** 2)
        g.add(line.set_cap_style(CapStyleType.ROUND))
    return g


def _fan(n, spread=PI * 0.75, facing=0.0):
    """n angles fanned across `spread` radians around `facing`."""
    return facing + np.linspace(-spread / 2, spread / 2, n)


def _around(n, offset=0.0):
    return offset + np.arange(n) * TAU / n


def _text(s, size, color=MUTED, font=SANS, weight="NORMAL"):
    return Text(s, font=font, font_size=size, color=color, weight=weight)


def _pct(p):
    return f"{int(round(p * 100))}%"


def _capsule(w, h, **kw):
    return RoundedRectangle(corner_radius=h / 2, width=w, height=h, **kw)


def _left_of(shape, x0, x1, h):
    """The part of `shape` left of x1 (a fill that keeps the shape's rounded left end)."""
    box = Rectangle(width=max(x1 - x0, 1e-3) + 0.2, height=h + 0.2)
    return Intersection(shape, box.move_to([(x0 - 0.2 + x1) / 2, 0, 0]))


def _gradient(colors, a):
    """The color at a (0..1) along a list of colors."""
    colors = [ManimColor(c) for c in colors]
    if len(colors) == 1:
        return colors[0]
    x = float(np.clip(a, 0, 1)) * (len(colors) - 1)
    i = min(int(x), len(colors) - 2)
    return interpolate_color(colors[i], colors[i + 1], x - i)


# ------------------------------------------------------------------------------- ring


def ring(tracker, radius=0.72, thickness=12, colors=(TEAL, BLUE), caption="synced"):
    """A circle that fills clockwise from the top, with the percentage in the middle."""

    def draw(p, t, since):
        g = VGroup(Circle(radius=radius, stroke_color=TRACK, stroke_width=thickness))
        if p > 0.003:
            arc = Arc(radius=radius, start_angle=PI / 2, angle=-p * TAU, stroke_width=thickness)
            arc.set_stroke(list(colors)).set_cap_style(CapStyleType.ROUND)
            g.add(arc, _flash(arc, since))
        k = radius / 0.72
        num = _text(_pct(p), 30 * k, INK, SANS, BOLD)
        if caption:
            g.add(num.shift(0.08 * k * UP), _text(caption, 15 * k).shift(0.3 * k * DOWN))
        else:
            g.add(num)
        # Done: the ring pops, a shockwave rings out, and sparks fly all around.
        g.scale(_spring(since, 0.1), about_point=ORIGIN)
        edge = radius + thickness / 200
        g.add(_shockwave(Circle(radius=edge), since, colors[-1], reach=0.45 * k),
              _sparks(ORIGIN, since, colors[0], _around(12, PI / 12), edge + 0.12, 0.45 * k))
        return g

    return live(draw, tracker)


# ----------------------------------------------------------------------------- liquid


def liquid(tracker, width=4.8, height=0.56, colors=(BLUE, CYAN), show_percent=True):
    """A glass tube filling from the left, with a rolling wave at the front of the liquid."""
    x0 = -width / 2
    ys = np.linspace(height / 2 + 0.05, -height / 2 - 0.05, 30)

    def wave(front, amp, k, speed, phase, t):
        pts = [[x0 - 0.2, height, 0]]
        pts += [[front + amp * np.sin(k * y + speed * t + phase), y, 0] for y in ys]
        pts += [[x0 - 0.2, -height, 0]]
        return Polygon(*pts)

    def draw(p, t, since):
        shell = _capsule(width, height, stroke_color=TRACK_LINE, stroke_width=2,
                         fill_color=TRACK, fill_opacity=1)
        g = VGroup(shell)
        inner = _capsule(width - 0.08, height - 0.08)
        calm = 1.0 if since is None else float(np.exp(-4 * min(since, 10)))  # waves settle when full
        if p > 0.01:
            front = x0 + 0.04 + p * (width - 0.08)
            back = Intersection(inner, wave(front + 0.05, 0.06 * calm, 11, 6, 1.7, t))
            g.add(back.set_fill(colors[-1], 0.35).set_stroke(width=0))
            main = Intersection(inner, wave(front, 0.05 * calm, 9, -5, 0, t))
            main.set_fill(list(colors), 1).set_sheen_direction(RIGHT).set_stroke(width=0)
            g.add(main, _flash(main, since))
        shine = Line([x0 + 0.3, height / 2 - 0.1, 0], [-x0 - 0.3, height / 2 - 0.1, 0],
                     stroke_color=WHITE, stroke_width=3, stroke_opacity=0.12)
        g.add(shine.set_cap_style(CapStyleType.ROUND))
        # Done: the tube pops, a shockwave rings out, and a splash bursts off the far wall.
        g.scale(_spring(since), about_point=ORIGIN)
        g.add(_shockwave(_capsule(width, height), since, colors[-1], reach=0.35),
              _sparks([-x0 - height / 2, 0, 0], since, colors[-1], _fan(7), height / 2 + 0.12))
        if show_percent:
            g.add(_text(_pct(p), 18, INK, MONO, BOLD).next_to(shell, DOWN, buff=0.18)
                  .align_to(shell, RIGHT))
        return g

    return live(draw, tracker)


# ---------------------------------------------------------------------------- stepper


def stepper(tracker, steps=("Plan", "Draft", "Review", "Ship"), width=4.8, color=GREEN):
    """Named stages on a line. A stage is checked once progress passes it (the last one at
    100%); the first unchecked stage is the current one and pulses. Stage i sits at progress
    i / (len(steps) - 1), so set the tracker to that to land on it."""
    from icons import icon

    n = len(steps)
    xs = np.linspace(-width / 2 + 0.3, width / 2 - 0.3, n)
    r = 0.19

    def draw(p, t, since):
        g = VGroup(Line([xs[0], 0, 0], [xs[-1], 0, 0], stroke_color=TRACK_LINE, stroke_width=4))
        if p > 0.002:
            xp = xs[0] + min(p, 1) * (xs[-1] - xs[0])
            line = Line([xs[0], 0, 0], [xp, 0, 0], stroke_color=color, stroke_width=4)
            g.add(line, _flash(line, since))
        current_found = False
        for i, (x, name) in enumerate(zip(xs, steps)):
            done = p >= i / (n - 1) + 1e-4 if i < n - 1 else p >= 0.999
            if done:
                disc = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_width=0)
                node = VGroup(
                    disc, icon("tabler/outline/check", color=DARK, height=0.15, stroke_width=3.2),
                    _flash(disc, since, dur=0.35 + 0.08 * i),
                )
                # Done: the checks hop one after another, first to last.
                node.scale(_spring(since, 0.3, delay=0.07 * i))
                tone = INK
            elif not current_found:
                current_found = True
                ph = (t * 1.1) % 1
                node = VGroup(
                    Circle(radius=r + 0.2 * ph, stroke_color=color, stroke_width=3,
                           stroke_opacity=1 - ph),
                    Circle(radius=r, fill_color=DARK, fill_opacity=1, stroke_color=color,
                           stroke_width=3),
                    Dot(radius=0.06, color=color),
                )
                tone = INK
            else:
                node = Circle(radius=r, fill_color=DARK, fill_opacity=1, stroke_color=TRACK_LINE,
                              stroke_width=3)
                tone = MUTED
            g.add(node.move_to([x, 0, 0]), _text(name, 17, tone).next_to([x, 0, 0], DOWN, buff=0.38))
        # ...and the last one lands with a shockwave and sparks.
        last = [xs[-1], 0, 0]
        hit = 0.07 * (n - 1)
        later = None if since is None else since - hit
        g.add(_shockwave(Circle(radius=r).move_to(last), later, color, reach=0.3),
              _sparks(last, later, color, _around(10, PI / 10), r + 0.1, 0.35, 0.15))
        return g

    return live(draw, tracker)


# ----------------------------------------------------------------------------- phases


def phases(tracker, parts=(("Download", BLUE, 0.5), ("Verify", VIOLET, 0.2), ("Install", TEAL, 0.3)),
           width=4.8, show_percent=True):
    """One bar split into named phases, each (name, color, share of the total). Phases fill in
    order, and the legend underneath brightens the active one. Shares are normalized."""
    total = sum(s for _, _, s in parts)
    parts = [(name, col, s / total) for name, col, s in parts]
    h, gap = 0.26, 0.06
    usable = width - gap * (len(parts) - 1)

    def draw(p, t, since):
        bar, tones = VGroup(), []
        start, x = 0.0, -width / 2
        for name, col, share in parts:
            sw = usable * share
            seg = _capsule(sw, h, fill_color=TRACK, fill_opacity=1, stroke_width=0)
            bar.add(seg.move_to([x + sw / 2, 0, 0]))
            f = float(np.clip((p - start) / share, 0, 1))
            if f > 0.01:
                bar.add(_left_of(seg.copy(), x, x + f * sw, h).set_fill(col, 1).set_stroke(width=0))
            active = 0 < p - start < share
            tones.append((INK if active else (col if f >= 1 else MUTED), f > 0))
            x += sw + gap
            start += share
        # One Text for the whole legend keeps the names on one baseline; a dot goes before each.
        sep = " " * 6
        words = _text(sep.join(name for name, _, _ in parts), 16)
        legend, i = VGroup(words), 0
        for (name, col, _), (tone, begun) in zip(parts, tones):
            n = len(name.replace(" ", ""))
            word = words[i:i + n].set_color(tone)
            i += n
            first = word[0]
            dot = Dot(radius=0.06, color=col, fill_opacity=1 if begun else 0.35)
            legend.add(dot.move_to([word.get_left()[0] - 0.17, first.get_bottom()[1] + 0.07, 0]))
        legend.next_to(bar, DOWN, buff=0.28).align_to(bar, LEFT).shift(0.17 * RIGHT)
        # Done: the bar flashes and pops, a shockwave rings out, sparks fly off the end.
        bar.add(_flash(VGroup(*bar.submobjects), since))
        bar.scale(_spring(since), about_point=ORIGIN)
        bar.add(_shockwave(_capsule(width, h), since, parts[-1][1], reach=0.3),
                _sparks([width / 2 - h / 2, 0, 0], since, parts[-1][1], _fan(7), h / 2 + 0.12))
        g = VGroup(bar, legend)
        if show_percent:
            g.add(_text(_pct(p), 16, MUTED, MONO).next_to(bar, DOWN, buff=0.28).align_to(bar, RIGHT))
        return g

    return live(draw, tracker)


# -------------------------------------------------------------------------- grid_fill


def grid_fill(tracker, rows=8, cols=8, cell=0.22, gap=0.05, colors=(TEAL, BLUE, VIOLET),
              trail=3.0, show_percent=True):
    """A box that fills with small squares, row by row from the bottom, sweeping left to
    right, then right to left, and so on. Squares grow in over `trail` cells, so the front is a
    soft wave rather than a hard edge. A square grid by default; set cols > rows for a wide one.
    """
    n = rows * cols
    w = cols * cell + (cols - 1) * gap
    h = rows * cell + (rows - 1) * gap
    pad = 0.12
    corner = cell * 0.2
    centers = []
    for k in range(n):
        r, c = divmod(k, cols)
        if r % 2:
            c = cols - 1 - c
        centers.append([-w / 2 + cell / 2 + c * (cell + gap), -h / 2 + cell / 2 + r * (cell + gap), 0])

    last = np.array(centers[-1])
    dists = [float(np.linalg.norm(np.array(c) - last)) for c in centers]
    speed, band = 6.0, 0.7  # the completion ripple: units per second, and its width

    def draw(p, t, since):
        lit = _phase(since, 0.6)
        edge = TRACK_LINE if lit is None else interpolate_color(
            ManimColor(colors[-1]), ManimColor(TRACK_LINE), lit)
        frame = RoundedRectangle(corner_radius=corner + pad, width=w + 2 * pad, height=h + 2 * pad,
                                 stroke_color=edge, stroke_width=2.5)
        g = VGroup(frame)
        front = p * (n + trail)
        for k, pos in enumerate(centers):
            g.add(RoundedRectangle(corner_radius=corner, width=cell, height=cell, fill_color=TRACK,
                                   fill_opacity=1, stroke_width=0).move_to(pos))
            f = float(np.clip((front - k) / trail, 0, 1))
            if f > 0.08:
                s = smooth(f)
                col = _gradient(colors, k / max(n - 1, 1))
                if f < 1:  # still growing: brighter, the leading edge of the sweep
                    col = interpolate_color(ManimColor(WHITE), col, s)
                # Done: a ripple runs out from the last square, swelling and whitening each one.
                v = None if since is None else since * speed - dists[k]
                if v is not None and 0 < v < band:
                    bump = float(np.sin(PI * v / band))
                    s *= 1 + 0.3 * bump
                    col = interpolate_color(ManimColor(col), ManimColor(WHITE), 0.75 * bump)
                g.add(RoundedRectangle(corner_radius=corner * s, width=cell * s, height=cell * s,
                                       fill_color=col, fill_opacity=1, stroke_width=0).move_to(pos))
        g.scale(_spring(since, 0.04), about_point=ORIGIN)
        g.add(_shockwave(frame.copy(), since, colors[-1], reach=0.35))
        if show_percent:
            g.add(_text(_pct(p), 18, INK, MONO, BOLD).next_to(frame, DOWN, buff=0.18)
                  .align_to(frame, RIGHT))
        return g

    return live(draw, tracker)

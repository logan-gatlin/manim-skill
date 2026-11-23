"""One line for connecting things in a diagram: an arrow by default, routed straight or in
elbows, optionally dashed or dotted, two-way, labelled, forked, or turned back on itself.

Copy this file next to scene.py:

    from line import Connector

    link = Connector(client, server)                    # an arrow from one mobject to another
    self.play(link.grow())                              # draws in, tip leading

    Connector(a, b, style="dashed", label="HTTP")       # dashed, with a label on the line
    Connector(a, b, two_way=True)                       # a tip at both ends
    Connector(a, b, tip=False)                          # a plain line
    Connector(a, [b, c, d])                             # a fork: one line splitting to three tips
    Connector(a, a2, route="u", side=RIGHT)             # out, around and back (a U-turn)

Ends are mobjects or points. Between mobjects the line starts and stops a little outside
their edges. When the ends are level with each other the line is straight; otherwise it
turns through quarter-circle elbows, never a free curve. See README.md for every option.
"""

import numpy as np
from manim import (
    DOWN, LEFT, ORIGIN, RIGHT, UP,
    Animation, CapStyleType, Dot, LineJointType, Mobject, Polygon, RoundedRectangle, Text,
    VGroup, VMobject, smooth,
)

INK = "#eef1f6"
PANEL = "#141821"
SANS = "Noto Sans"

TIP_LENGTH, TIP_WIDTH, TIP_NOTCH = 0.38, 0.32, 0.3   # the barbed tip, before tip_size
DASH = (0.2, 0.14)        # dash and gap lengths for style="dashed"
DOT_STEP = 0.17           # distance between dots for style="dotted"


class _Path:
    """A polyline measured by distance along it."""

    def __init__(self, pts):
        self.pts = np.array(pts, dtype=float)
        seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1)
        self.cum = np.concatenate([[0.0], np.cumsum(seg)])
        self.len = float(self.cum[-1])

    def at(self, s):
        s = float(np.clip(s, 0, self.len))
        i = min(int(np.searchsorted(self.cum, s, "right")) - 1, len(self.pts) - 2)
        f = (s - self.cum[i]) / max(self.cum[i + 1] - self.cum[i], 1e-9)
        return self.pts[i] + f * (self.pts[i + 1] - self.pts[i])

    def direction(self, s):
        d = self.at(min(s + 0.02, self.len)) - self.at(max(s - 0.02, 0))
        return d / max(np.linalg.norm(d), 1e-9)

    def cut(self, s0, s1):
        inner = [self.pts[i] for i in range(len(self.pts)) if s0 < self.cum[i] < s1]
        return [self.at(s0), *inner, self.at(s1)]

    def nearest(self, point):
        """The distance along the path of its vertex closest to `point`."""
        return float(self.cum[np.argmin(np.linalg.norm(self.pts - point, axis=1))])


def _elbows(points, r, n=14):
    """A path through `points` in straight runs, each corner rounded to an arc of radius r
    (a quarter circle at a right angle), or less where a run is too short for it."""
    points = [np.array(p, dtype=float) for p in points]
    out = [points[0]]
    for before, corner, after in zip(points, points[1:], points[2:]):
        a, b = before - corner, after - corner
        la, lb = np.linalg.norm(a), np.linalg.norm(b)
        ua, ub = a / la, b / lb
        half = np.arccos(np.clip(np.dot(ua, ub), -1, 1)) / 2   # half the angle at the corner
        if half < 1e-3 or half > np.pi / 2 - 1e-3:             # doubling back, or no turn at all
            out.append(corner)
            continue
        rr = min(r, min(la, lb) / 2 * np.tan(half))
        d = rr / np.tan(half)
        bis = (ua + ub) / np.linalg.norm(ua + ub)
        center = corner + bis * rr / np.sin(half)
        p1, p2 = corner + ua * d - center, corner + ub * d - center
        a0 = np.arctan2(p1[1], p1[0])
        sweep = (np.arctan2(p2[1], p2[0]) - a0 + np.pi) % (2 * np.pi) - np.pi
        for k in range(n + 1):
            ang = a0 + sweep * k / n
            out.append(center + rr * np.array([np.cos(ang), np.sin(ang), 0.0]))
    out.append(points[-1])
    return _Path(out)


def _center(end):
    return end.get_center() if isinstance(end, Mobject) else np.array(end, dtype=float)


def _edge(end, direction, buff):
    """Where a line leaves `end` going `direction` (an axis direction): the middle of that
    edge, `buff` outside it. A point is its own edge."""
    if not isinstance(end, Mobject):
        return np.array(end, dtype=float)
    return end.get_edge_center(direction) + np.array(direction, dtype=float) * buff


def _exit(end, toward, buff):
    """Where a straight line toward the point `toward` leaves the box around `end`."""
    c = _center(end)
    if not isinstance(end, Mobject):
        return c
    d = toward - c
    d = d / max(np.linalg.norm(d), 1e-9)
    reach = min(end.width / 2 / max(abs(d[0]), 1e-9), end.height / 2 / max(abs(d[1]), 1e-9))
    return c + d * (reach + buff)


def _sign(x):
    return 1.0 if x >= 0 else -1.0


class _Grow(Animation):
    def __init__(self, connector, **kwargs):
        super().__init__(connector, introducer=True, **kwargs)

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole line here, and never use the copy

    def interpolate_mobject(self, alpha):
        self.mobject.lay(self.rate_func(alpha))


class Connector(VGroup):
    def __init__(self, start, end, route=None, via=None, side=RIGHT, reach=0.8, mid=0.5,
                 color=INK, width=4, style="solid", tip=True, start_tip=False, two_way=False,
                 label=None, label_at=None, label_size=16, font=SANS,
                 corner=0.25, buff=0.12, tip_size=1.0):
        """A line from `start` to `end`, each a mobject or a point. A list of ends makes a
        fork: one line that splits and runs to each of them.

        route      None picks for you: straight when the ends are level, else elbows.
                   "straight" goes directly, at any angle. "hvh" runs across, steps up or
                   down at `mid` (0..1 of the way), and runs across again; "vhv" is the same
                   turned on its side. "hv" and "vh" turn one corner. "u" leaves both ends on
                   the same `side` and turns back `reach` beyond them.
        via        points to pass through instead, with an elbow at each.
        style      "solid", "dashed" or "dotted".
        tip        a barbed tip at the end (at every end of a fork). `start_tip` puts one at
                   the start; `two_way=True` is both.
        label      a word or two set on the line in a pill, in the middle of the longest
                   straight run, or at `label_at` (0..1 of the way along).
        corner     the radius of the elbows; `buff` the gap left to a mobject's edge.
        """
        super().__init__()
        self.color_, self.stroke, self.style = color, width, style
        self.has_tip, self.has_start_tip = tip or two_way, start_tip or two_way
        self.tip_length = TIP_LENGTH * tip_size
        self.back = self.tip_length * (1 - TIP_NOTCH) - 0.02   # the shaft ends inside the notch
        ends = list(end) if self._is_list(end) else [end]
        self.paths = [_elbows(pts, corner) for pts in
                      self._waypoints(start, ends, route, via, np.array(side, dtype=float), reach, mid, buff)]
        self.shared = self._shared()
        # A two-way line grows from its middle outward; anything else from its start.
        self.from_middle = self.has_start_tip and self.has_tip and len(self.paths) == 1
        self._build(label, label_at, label_size, font, tip_size)
        self.lay(1)

    # ------------------------------------------------------------------------- public

    def grow(self, run_time=1.0, rate_func=smooth):
        """The animation that draws the line in, tip leading (a two-way line grows from its
        middle). Adds the line to the scene."""
        return _Grow(self, run_time=run_time, rate_func=rate_func)

    def point(self, fraction, branch=0):
        """A point on the line, `fraction` (0..1) of the way along; `branch` picks a fork's arm."""
        path = self.paths[branch]
        return path.at(fraction * path.len)

    # -------------------------------------------------------------------------- route

    @staticmethod
    def _is_list(end):
        return isinstance(end, (list, tuple)) and len(end) > 0 and not np.isscalar(end[0])

    def _waypoints(self, start, ends, route, via, side, reach, mid, buff):
        """The corner points of each arm's route."""
        a, bs = _center(start), [_center(e) for e in ends]
        if via is not None:
            via = [np.array(v, dtype=float) for v in via]
            first = _edge(start, self._axis(via[0] - a), buff)
            last = _edge(ends[0], self._axis(via[-1] - bs[0]), buff)
            return [[first, *via, last]]
        far = np.mean(bs, axis=0) - a
        if route is None:
            level = abs(far[1]) < 0.05 or abs(far[0]) < 0.05
            route = "straight" if level and len(ends) == 1 else "hvh" if abs(far[0]) >= abs(far[1]) else "vhv"
        if route == "straight":
            return [[_exit(start, b, buff), _exit(e, a, buff)] for e, b in zip(ends, bs)]
        if route == "u":
            p, q = _edge(start, side, buff), _edge(ends[0], side, buff)
            if ends[0] is start:   # a loop back to the same thing: leave and return side by side
                across = np.array([-side[1], side[0], 0.0])
                size = start.width if abs(across[0]) > 0.5 else start.height
                p, q = p + across * min(0.3, size / 4), q - across * min(0.3, size / 4)
            out = max(np.dot(p, side), np.dot(q, side)) + reach
            return [[p, p + side * (out - np.dot(p, side)), q + side * (out - np.dot(q, side)), q]]
        if route in ("hv", "vh"):
            b = bs[0]
            across, along = RIGHT * _sign(b[0] - a[0]), UP * _sign(b[1] - a[1])
            if route == "hv":
                p, q = _edge(start, across, buff), _edge(ends[0], -along, buff)
                return [[p, np.array([q[0], p[1], 0.0]), q]]
            p, q = _edge(start, along, buff), _edge(ends[0], -across, buff)
            return [[p, np.array([p[0], q[1], 0.0]), q]]
        # "hvh" and "vhv": out along one axis, a step across at the junction, in along the same axis
        i = 0 if route == "hvh" else 1
        axis = (RIGHT if i == 0 else UP) * _sign(far[i])
        p = _edge(start, axis, buff)
        qs = [_edge(e, -axis, buff) for e in ends]
        nearest = min(qs, key=lambda q: abs(q[i] - p[i]))
        junction = p[i] + (nearest[i] - p[i]) * mid
        routes = []
        for q in qs:
            if abs(q[1 - i] - p[1 - i]) < 1e-3:   # straight ahead
                routes.append([p, q])
                continue
            j1, j2 = p.copy(), q.copy()
            j1[i] = j2[i] = junction
            routes.append([p, j1, j2, q])
        return routes

    @staticmethod
    def _axis(d):
        return RIGHT * _sign(d[0]) if abs(d[0]) >= abs(d[1]) else UP * _sign(d[1])

    def _shared(self):
        """How far a fork's arms run together before the first one turns off."""
        if len(self.paths) == 1:
            return 0.0
        s, limit = 0.0, min(p.len for p in self.paths)
        while s + 0.01 <= limit:
            pts = [p.at(s + 0.01) for p in self.paths]
            if max(np.linalg.norm(q - pts[0]) for q in pts) > 1e-4:
                break
            s += 0.01
        return s

    # -------------------------------------------------------------------------- build

    def _build(self, label, label_at, label_size, font, tip_size):
        main = self.paths[0]
        # the label and the gap it leaves in the line
        self.label, self.gap = None, None
        if label:
            text = Text(label, font=font, font_size=label_size, color=INK)
            pill = RoundedRectangle(corner_radius=min(0.15, (text.height + 0.16) / 2), width=text.width + 0.32,
                                    height=text.height + 0.16, stroke_color=self.color_, stroke_width=2,
                                    fill_color=PANEL, fill_opacity=1)
            self.label_s = label_at * main.len if label_at is not None else self._label_spot(pill)
            self.label = VGroup(pill, text).move_to(main.at(self.label_s))
            d = main.direction(self.label_s)
            half = min(pill.width / 2 / max(abs(d[0]), 1e-9), pill.height / 2 / max(abs(d[1]), 1e-9)) + 0.07
            self.gap = (self.label_s - half, self.label_s + half)
        # the shaft, in pieces: (mobject, arm, from, to); a dot has from == to
        self.pieces = []
        # a solid or dashed shaft runs into the tip's notch; dots stop short of the tip
        clear = self.tip_length + 0.03 if self.style == "dotted" else self.back
        for i, path in enumerate(self.paths):
            first = clear if self.has_start_tip else 0.0
            lo = first if i == 0 else self.shared
            hi = path.len - (clear if self.has_tip else 0.0)
            # only the first arm passes under the label
            for s0, s1 in self._spans(first, lo, hi, len(self.paths) == 1, self.gap if i == 0 else None):
                if self.style == "dotted":
                    mob = Dot(path.at(s0), radius=self.stroke * 0.0105, color=self.color_)
                else:
                    mob = VMobject(joint_type=LineJointType.ROUND).set_points_as_corners(path.cut(s0, s1))
                    mob.set_stroke(self.color_, self.stroke).set_fill(opacity=0)
                    mob.set_cap_style(CapStyleType.ROUND)
                self.pieces.append((mob, i, s0, s1))
                self.add(mob)
        # the tips: (mobject, arm, at the start?, outline drawn pointing right with its tip at the origin)
        self.tips = []
        L, W = self.tip_length, TIP_WIDTH * tip_size
        ends = [(i, False) for i in range(len(self.paths))] if self.has_tip else []
        for i, at_start in ends + ([(0, True)] if self.has_start_tip else []):
            mob = Polygon([0, 0, 0], [-L, W / 2, 0], [-L * (1 - TIP_NOTCH), 0, 0], [-L, -W / 2, 0],
                          joint_type=LineJointType.ROUND, color=self.color_, fill_opacity=1, stroke_width=1.5)
            self.tips.append((mob, i, at_start, mob.points.copy()))
            self.add(mob)
        if self.label is not None:
            self.add(self.label)

    def _label_spot(self, pill):
        """Where the label goes: the middle of the straight run of the shaft with the most
        room to spare around the pill. On a fork that is a run the arms share, unless none
        of those can hold the label; then it goes on the first arm."""
        path = self.paths[0]
        lo = self.tip_length if self.has_start_tip else 0.0
        end = path.len - (self.tip_length if self.has_tip else 0.0)
        for hi in ([self.shared, end] if len(self.paths) > 1 else [end]):
            best, spot = -np.inf, (lo + hi) / 2
            for i in range(len(path.pts) - 1):
                a, b = max(path.cum[i], lo), min(path.cum[i + 1], hi)
                d = np.abs(path.pts[i + 1] - path.pts[i]) / max(path.cum[i + 1] - path.cum[i], 1e-9)
                need = min(pill.width / max(d[0], 1e-9), pill.height / max(d[1], 1e-9)) + 0.14
                if b - a - need > best:
                    best, spot = b - a - need, (a + b) / 2
            if best >= 0:
                break
        return spot

    def _spans(self, first, lo, hi, fit, skip):
        """The stretches of the shaft to draw between distances lo and hi: one for a solid
        line, one per dash, or a point per dot. The pattern starts at `first` and, on a
        single line (`fit`), is stretched slightly so it ends exactly at the tip."""
        if hi - lo < 1e-3:
            return []
        if self.style == "solid":
            spans = [(lo, hi)]
        elif self.style == "dashed":
            dash, gap = DASH
            if fit:
                n = max(1, round((hi - first + gap) / (dash + gap)))
                k = (hi - first) / (n * (dash + gap) - gap)
                dash, gap = dash * k, gap * k
            spans, s = [], first
            while s < hi - 1e-6:
                if s + dash > lo:
                    spans.append((max(s, lo), min(s + dash, hi)))
                s += dash + gap
        elif self.style == "dotted":
            step = DOT_STEP
            if fit:
                step = (hi - first) / max(1, round((hi - first) / step))
            spans, s = [], first + step / 2
            while s < hi:
                if s >= lo:
                    spans.append((s, s))
                s += step
        else:
            raise ValueError(f'style must be "solid", "dashed" or "dotted", not {self.style!r}')
        if skip is None:
            return spans
        g0, g1 = skip
        out = []
        for s0, s1 in spans:   # leave room for the label
            if s1 <= g0 or s0 >= g1:
                out.append((s0, s1))
            elif s0 != s1:
                out += [(a, b) for a, b in ((s0, g0), (g1, s1)) if b - a > 0.03]
        return out

    # --------------------------------------------------------------------------- draw

    def lay(self, alpha):
        """Draw the line as it is `alpha` (0..1) of the way through growing."""
        k = min(1.0, alpha / 0.25)   # a tip swells to full size as it sets off
        longest = max(p.len for p in self.paths)
        window = []                  # the part of each arm that is drawn so far
        for path in self.paths:
            if self.from_middle:
                window.append((path.len / 2 * (1 - alpha), path.len / 2 * (1 + alpha)))
            elif alpha * longest <= self.shared or longest - self.shared < 1e-6:
                window.append((0.0, min(alpha * longest, path.len)))
            else:   # past the split, each arm paces itself so all the tips land together
                f = (alpha * longest - self.shared) / (longest - self.shared)
                window.append((0.0, self.shared + f * (path.len - self.shared)))
        for mob, i, s0, s1 in self.pieces:
            lo, hi = window[i]
            a = max(s0, lo + (self.back * k if self.has_start_tip else 0))
            b = min(s1, hi - (self.back * k if self.has_tip else 0))
            if isinstance(mob, Dot):
                mob.set_fill(opacity=1 if a <= b else 0)
            elif b - a < 2e-3:
                mob.set_stroke(opacity=0)
            else:
                mob.set_points_as_corners(self.paths[i].cut(a, b)).set_stroke(opacity=1)
        for mob, i, at_start, outline in self.tips:
            path = self.paths[i]
            s = window[i][0] if at_start else window[i][1]
            d = path.direction(s) * (-1 if at_start else 1)
            turn = np.array([[d[0], d[1], 0], [-d[1], d[0], 0], [0, 0, 1]])
            mob.set_points(outline * max(k, 1e-3) @ turn + path.at(s))
            mob.set_fill(opacity=1 if k > 0.02 else 0).set_stroke(opacity=1 if k > 0.02 else 0)
        if self.label is not None:
            lo, hi = window[0]
            shown = float(np.clip(min(hi - self.label_s, self.label_s - lo) / 0.3 + 0.5, 0, 1))
            if self.from_middle:
                shown = float(np.clip(alpha / 0.3, 0, 1))
            pill, text = self.label
            pill.set_stroke(opacity=shown).set_fill(opacity=shown)
            text.set_opacity(shown)
        return self

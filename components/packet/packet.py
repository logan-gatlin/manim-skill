"""Packets that travel along a line: one, or a burst, each a dot with a comet's tail.

Copy this file next to scene.py, with the line component's line.py:

    from line import Connector
    from packet import send

    link = Connector(web, api)
    self.play(send(link))                          # one packet
    self.play(send(link, count=6))                 # a burst, of dots of different sizes
    self.play(send(link, drop=True))               # one that is lost part-way
    self.play(send(link, count=6, drop=[1, 4]))    # a burst that loses its second and fifth
    self.play(send(link, reverse=True, color=GREEN))   # a reply, coming back

Each packet grows out of the start of the line and shrinks into its tip, and the tip
swells for a moment as each one lands. See README.md.
"""

import numpy as np
from manim import TAU, Animation, CapStyleType, Circle, LineJointType, ManimColor, VGroup, VMobject, interpolate_color, linear

INK = "#eef1f6"
BLUE, RED = "#60a5fa", "#f87171"

SPEED = 3.4       # units a second a packet averages, when `travel` is not given
RADIUS = 0.085    # of a packet's dot, before `size`
TAIL = 1.1        # the length of a lone packet's tail; a burst's are shorter
LAYERS = 12       # a tail is see-through strokes laid over each other, each shorter and wider than the last
LAND = 0.32       # seconds the tip swells for when a packet lands...
SWELL = 0.32      # ...and by how much
POP = 0.45        # seconds a dropped packet takes to pop
SETTLE = 0.5      # seconds allowed after the last packet lands, for its tail to run in


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def _chance(k, j):
    """A repeatable number in 0..1 for packet k (the j-th one it needs)."""
    v = np.sin(k * 12.9898 + j * 78.233) * 43758.5453
    return float(v - np.floor(v))


def _gone(x):
    """How far a packet has gone, as a share of the way, x of the way through its travel
    time: it sets off briskly, is fastest in the middle, and past the end (x > 1) keeps
    the speed it landed at, which is what carries its tail in after it."""
    return 0.7 * x + 0.3 * _ease(x)


class _Send(Animation):
    def __init__(self, link, count, drop, drop_at, reverse, color, size, travel, gap, branch):
        self.link, self.count, self.color, self.gap = link, count, color, gap
        arms = range(len(link.paths)) if branch is None else [branch]
        # Each arm's route, in the direction of travel, and where on it a packet stops:
        # where the line meets its tip, if there is one there to receive it.
        self.routes = []
        for i in arms:
            path = link.paths[i]
            tipped = link.has_start_tip if reverse else link.has_tip
            if reverse:
                path = type(path)(path.pts[::-1])
            tip = [mob for mob, arm, at_start, _ in link.tips if arm == (0 if reverse else i) and at_start == reverse]
            self.routes.append((path, path.len - (link.back if tipped else 0), tip[0] if tip else None))
        longest = max(span for _, span, _ in self.routes)
        self.travel = travel or float(np.clip(longest / SPEED, 0.7, 2.2))
        # which packets are lost, and how far along
        lost = range(count) if drop is True else (drop or [])
        self.lost = {}
        for k in lost:
            at = drop_at if drop_at is not None else (0.55 if count == 1 else 0.35 + 0.4 * _chance(k, 3))
            lo, hi = 0.0, 1.0
            for _ in range(30):                        # when it gets there
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if _gone(mid) < at else (lo, mid)
            self.lost[k] = (at, lo)
        # a burst's packets differ in size, and each swells and shrinks as it goes
        lone = count == 1
        self.sizes = [size * (1.0 if lone else 0.62 + 0.62 * _chance(k, 1)) for k in range(count)]
        self.throb = [(0.0, 0.0, 0.0) if lone else (0.22, 1.5 + 1.2 * _chance(k, 5), TAU * _chance(k, 7)) for k in range(count)]
        self.tail = TAIL if lone else 0.62
        self.seconds = self.travel + (count - 1) * gap + SETTLE
        super().__init__(link, run_time=self.seconds, rate_func=linear)

    def begin(self):
        link = self.link
        # Every piece is made now and only moved afterwards: the renderer fixes its list of
        # things to draw when the animation begins.
        self.packets = []
        self.drawn = VGroup()
        for _ in self.routes:
            for _ in range(self.count):
                tail = [VMobject(joint_type=LineJointType.ROUND).set_points_as_corners([link.get_center()] * 2)
                        .set_stroke(self.color, 2, 0).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
                        for _ in range(LAYERS)]
                head = Circle(radius=RADIUS, stroke_width=0, fill_color=self.color, fill_opacity=0).move_to(link.get_center())
                self.packets.append((tail, head))
                self.drawn.add(*tail, head)
        self.round = Circle(radius=1).points.copy()
        # over the line, under its tips and its label
        over = [mob for mob, *_ in link.tips] + ([link.label] if link.label is not None else [])
        where = min([link.submobjects.index(mob) for mob in over], default=len(link.submobjects))
        link.submobjects.insert(where, self.drawn)
        # the tips as they are at rest, noted once however many sends are under way
        active = link.__dict__.setdefault("_sends", {})
        if not active:
            link._rest = {id(mob): mob.points.copy() for mob, *_ in link.tips}
        active[id(self)] = {}
        super().begin()

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole line here, and never use the copy

    def interpolate_mobject(self, alpha):
        u = self.rate_func(alpha) * self.seconds
        landing = {}
        for r, (path, span, tip) in enumerate(self.routes):
            bump = 0.0
            for k in range(self.count):
                x = (u - k * self.gap) / self.travel
                bump = max(bump, self._draw(self.packets[r * self.count + k], path, span, k, x, u))
            if tip is not None:
                landing[id(tip)] = max(landing.get(id(tip), 0.0), bump)
        self._swell(landing)

    def _draw(self, packet, path, span, k, x, u):
        """Draw packet k, x of the way through its travel time. Returns how much the tip
        should swell for it (0..1)."""
        tail, head = packet
        if x <= 0:
            return 0.0
        amount, rate, phase = self.throb[k]
        size = self.sizes[k] * (1 + amount * np.sin(rate * TAU * u + phase))
        length = self.tail * (0.6 + 0.4 * size)
        color, lost = self.color, self.lost.get(k)
        hole = 0.0
        if lost and x > lost[1]:
            # Lost: the packet stops where it is, turns red and pops. It swells while a hole
            # opens in its middle and widens until nothing is left, and its tail closes up.
            at, when = lost
            since = min((x - when) * self.travel / POP, 1.0)
            reach = at * span
            spot = path.at(reach)
            color = _mix(self.color, RED, since / 0.18)
            shut = _ease(since / 0.5)
            front, back, tail_solid = reach, reach - length * (1 - shut), 1 - shut
            grown, landed = 1 + 1.3 * (1 - (1 - since) ** 2), 0.0
            hole = _ease(since)
        else:
            reach = _gone(x) * span
            front, back, tail_solid = min(reach, span), reach - length, 1.0
            p = min(reach / span, 1.0)
            grown = float(np.clip(min(p / 0.07, (1 - p) / 0.05), 0, 1))     # out of the start, into the tip
            spot = path.at(front)
            after = (x - 1) * self.travel
            landed = 0.0 if lost or not 0 < after < LAND else np.sin(np.pi * (after / LAND) ** 0.6)
        r = RADIUS * size * grown
        ring = self.round * max(r, 1e-4) + spot
        if hole > 0:                       # the hole: the same circle, smaller and drawn the other way round
            ring = np.vstack([ring, (self.round * r * hole + spot)[::-1]])
        head.set_points(ring)
        head.set_fill(_mix(color, INK, 0.35), 1 if r > 1e-3 and hole < 0.999 else 0)
        # The tail: every layer ends at the head, and each starts a little nearer to it
        # and is a little wider, so the tail thickens and brightens toward the head.
        b = min(front, span)
        for j, layer in enumerate(tail):
            a = max(back + (front - back) * j / LAYERS, 0.0)
            if b - a < 2e-3 or tail_solid < 0.01:
                layer.set_stroke(opacity=0)
                continue
            layer.set_points_as_corners(path.cut(a, b))
            layer.set_stroke(color, size * (2 + 6 * (j + 1) / LAYERS), 0.2 * tail_solid * min(1.0, grown * 3 + 0.4))
        return landed

    def _swell(self, landing):
        """Scale each tip about its middle by the most any send under way asks of it."""
        link = self.link
        link._sends[id(self)] = landing
        for mob, *_ in link.tips:
            most = max((asked.get(id(mob), 0.0) for asked in link._sends.values()), default=0.0)
            rest = link._rest[id(mob)]
            centre = (rest.min(axis=0) + rest.max(axis=0)) / 2
            mob.set_points(centre + (rest - centre) * (1 + SWELL * most))

    def finish(self):
        super().finish()
        self._swell({})
        self.link._sends.pop(id(self), None)
        if self.drawn in self.link.submobjects:
            self.link.submobjects.remove(self.drawn)


def send(link, count=1, drop=False, drop_at=None, reverse=False, color=BLUE, size=1.0, travel=None, gap=0.14, branch=None):
    """The animation of packets travelling along `link`, a Connector that is on screen.

    count     how many packets. More than one is a burst: they set off `gap` seconds apart,
              differ in size, and each swells and shrinks as it goes.
    drop      True loses the packet (or every packet) part-way: it stops, turns red and
              pops. A list loses just those packets of a burst, counting from 0, and the
              rest arrive.
    drop_at   how far along a packet is lost, 0..1. By default just past half-way for one
              packet and a different place for each in a burst.
    reverse   travel from the line's end to its start: a reply.
    color     of the packets.
    size      1 is the usual size.
    travel    seconds each packet takes; by default it depends on the line's length.
    branch    on a fork, the one arm to travel. By default a packet goes down every arm.

    The animation lasts as long as the packets need. A `run_time` given to `play` stretches
    or squeezes the whole thing.
    """
    return _Send(link, count, drop, drop_at, reverse, color, size, travel, gap, branch)

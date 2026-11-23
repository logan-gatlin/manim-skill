"""A queue: items join at one end, wait their turn between a pair of brackets, and leave at
the other.

Copy this file next to scene.py (it is called fifo.py because a file named queue.py would
hide Python's own queue module):

    from fifo import Queue

    q = Queue(capacity=6)
    self.play(FadeIn(q))
    self.play(q.push(4))        # four items join, one after another
    self.play(q.pop())          # the one at the head leaves
    self.play(q.push(5))        # more than there is room for: the rest wait outside, in grey
    self.play(q.pop(2))         # as two leave, two of those waiting move in

The brackets turn red while the queue is full. See README.md.
"""

import numpy as np
from manim import Animation, CapStyleType, Dot, LineJointType, ManimColor, VGroup, VMobject, interpolate_color, linear

MUTED = "#8a93a6"
BLUE, RED, GREY = "#60a5fa", "#f87171", "#737b8c"

PITCH = 0.42      # the distance between items
DOT = 0.11        # an item's radius
MOVE = 0.4        # seconds an item takes to arrive, move up or leave
STAGGER = 0.16    # seconds between one item and the next when several join or leave at once


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


class _Shuffle(Animation):
    """Moves every item from where it is to where one push or pop leaves it."""

    def __init__(self, queue, plan, room, run_time):
        self.plan, self.room = plan, room                 # plan: [(item, place, shown, delay)]
        self.seconds = max([delay for *_, delay in plan], default=0) + MOVE
        super().__init__(queue, run_time=run_time or self.seconds, rate_func=linear)

    def begin(self):
        self.start = [(item.place, item.shown) for item, *_ in self.plan]
        self.room_start = self.mobject._room
        super().begin()

    def interpolate_mobject(self, alpha):
        queue, u = self.mobject, alpha * self.seconds
        for (item, place, shown, delay), (place0, shown0) in zip(self.plan, self.start):
            k = _ease((u - delay) / MOVE)
            item.place, item.shown = place0 + (place - place0) * k, shown0 + (shown - shown0) * k
        queue._room = self.room_start + (self.room - self.room_start) * _ease(u / MOVE)
        queue._lay()


class Queue(VGroup):
    """A queue whose head is at the right: items join from the left and leave to the right.

    capacity   how many items it holds. Items pushed beyond that wait outside, in grey, and
               move in as room appears. None is a queue with no limit, whose brackets widen
               to hold whatever is in it.

    `queue.count` is how many items are in it or waiting; `queue.capacity` its limit.
    """

    def __init__(self, capacity=6, **kwargs):
        super().__init__(**kwargs)
        self.capacity = capacity
        self.brackets = VGroup(*[VMobject(joint_type=LineJointType.ROUND).set_stroke(MUTED, 3).set_fill(opacity=0)
                                 .set_cap_style(CapStyleType.ROUND) for _ in range(2)])
        self.dots = VGroup()
        self.add(self.brackets, self.dots)
        self._items = []                          # in order, head first; each a Dot with .place and .shown
        self._room = float(capacity or 1)         # the places between the brackets
        # the right-hand bracket is the fixed point: everything is laid out from it
        self.brackets[1].set_points_as_corners([[-0.12, 0.3, 0], [0, 0.3, 0], [0, -0.3, 0], [-0.12, -0.3, 0]])
        self._lay()

    @property
    def count(self):
        return len(self._items)

    # ---- changing it

    def push(self, n=1, run_time=None):
        """`n` items join, one after another. Returns the animation."""
        self._tidy()
        plan = []
        for j in range(n):
            place = len(self._items)
            item = Dot(radius=DOT * self._size(), color=GREY, fill_opacity=0)
            item.place, item.shown = place + 3.0, 0.0
            self._items.append(item)
            self.dots.add(item)
            plan.append((item, float(place), 1.0, j * STAGGER))
        self._lay()
        return _Shuffle(self, plan, self._want(), run_time)

    def pop(self, n=1, run_time=None):
        """The `n` items at the head leave, and everything behind moves up. Returns the
        animation."""
        self._tidy()
        n = min(n, len(self._items))
        leaving, staying = self._items[:n], self._items[n:]
        self._items = staying
        plan = [(item, -1.6 - j, 0.0, j * STAGGER) for j, item in enumerate(leaving)]
        # everything behind moves up, setting off part-way through the departures
        plan += [(item, float(i), 1.0, 0.5 * max(n - 1, 0) * STAGGER) for i, item in enumerate(staying)]
        self._gone = leaving
        return _Shuffle(self, plan, self._want(), run_time)

    # ---- drawing it

    def _tidy(self):
        """Forget items that have left."""
        for item in getattr(self, "_gone", []):
            if item in self.dots.submobjects:
                self.dots.remove(item)
        self._gone = []

    def _want(self):
        return float(self.capacity or max(len(self._items), 1))

    def _size(self):
        """How much the queue has been scaled since it was made."""
        return self.brackets[1].height / 0.6

    def _lay(self):
        """Put the brackets and every item where they belong."""
        s = self._size()
        right = self.brackets[1].get_right()[0]
        y = self.brackets[1].get_center()[1]
        head = right - 0.24 * s
        left = head - (self._room - 1) * PITCH * s - 0.24 * s
        self.brackets[0].set_points_as_corners([[left + 0.12 * s, y + 0.3 * s, 0], [left, y + 0.3 * s, 0],
                                                [left, y - 0.3 * s, 0], [left + 0.12 * s, y - 0.3 * s, 0]])
        inside_count = 0.0
        for item in self.dots:
            # an item beyond the last place waits outside, a little apart from the bracket
            outside = float(np.clip(item.place - (self._room - 1), 0, 1))
            item.move_to([head - item.place * PITCH * s - 0.3 * s * outside, y, 0])
            item.set_fill(_mix(BLUE, GREY, outside), item.shown)
            inside_count += (1 - outside) * item.shown * (1 if item.place > -0.5 else 0)
        full = float(np.clip(inside_count - (self.capacity - 1), 0, 1)) if self.capacity else 0.0
        self.brackets.set_stroke(_mix(MUTED, RED, full))
        return self

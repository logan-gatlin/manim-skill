"""A tree: values on chips, each joined to its parent by a line that turns in elbows. Nodes
are added and removed, branches fold away and open again, and the rest of the tree moves
over to make room.

Copy this file and the skill's code_font.py next to scene.py:

    from tree import Tree

    t = Tree({8: [4, 12], 4: [2, 6], 12: [10, 14]}, binary=True)    # parent: its children
    self.play(t.draw())
    self.play(t.visit(8, 4, 6))            # each lights in turn
    self.play(t.add_node(5, 6))            # a line grows from 6, and 5 appears, marked green
    self.play(t.insert_value(11))          # a search tree finds the place itself
    self.play(t.fold(4))                   # the branch under 4 goes into it, leaving "+3"
    self.play(t.unfold(4))
    self.play(t.remove_node(14))           # marked red, then gone

See README.md.
"""

import numpy as np
from manim import (ORIGIN, RIGHT, Animation, CapStyleType, LineJointType, ManimColor, RoundedRectangle, Succession, Text, VGroup,
                   VMobject, interpolate_color, linear)

from code_font import MONO

BG = "#0d1118"
TRACK = "#1c2130"
LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE, RED, GREEN = "#60a5fa", "#f87171", "#4ade80"
SANS = "Noto Sans"

FONT = 18         # the size of a value
TALL = 0.52       # a chip's height
WIDE = 0.8        # ...and its width, unless the value needs more
LEVEL = 1.05      # the distance from one level down to the next
EMPTY = 0.6       # the room left for a missing child in a binary tree, in places
MOVE = 0.5        # seconds the tree takes to move over
GROW = 0.45       # seconds a line takes to grow, and a chip to appear
LIGHT = 0.2       # seconds a chip takes to light
FADE = 0.5        # ...and to go out


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def _word(s, size, font):
    """The letters of `s` behind an invisible point at their middle, half-way up the line:
    putting the point somewhere puts every word on the same baseline."""
    t = Text("Hg" + s, font=font, font_size=size)
    letters = VGroup(*t[2:])
    letters.shift([-letters.get_center()[0] if len(letters) else 0, -t[:2].get_center()[1], 0])
    word = VGroup(VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([ORIGIN, ORIGIN]), *letters)
    word.anchor = word[0]
    return word


def _elbow(a, b, c, r):
    """The points of a line from a to c that turns at b through a quarter circle."""
    r = min(r, np.linalg.norm(b - a), np.linalg.norm(c - b))
    if r < 1e-3:
        return [a, c]
    u, v = (a - b) / np.linalg.norm(a - b), (c - b) / np.linalg.norm(c - b)
    centre = b + r * (u + v)
    start, end = np.arctan2(*(b + r * u - centre)[::-1]), np.arctan2(*(b + r * v - centre)[::-1])
    sweep = (end - start + np.pi) % (2 * np.pi) - np.pi
    return [a] + [centre + r * np.array([np.cos(start + sweep * k / 8), np.sin(start + sweep * k / 8)]) for k in range(9)] + [c]


def _route(a, b, r):
    """Down from a, across, and down to b."""
    if abs(a[0] - b[0]) < 1e-3:
        return [a, b]
    mid, half = (a[1] + b[1]) / 2, (a[0] + b[0]) / 2
    return (_elbow(a, np.array([a[0], mid]), np.array([half, mid]), r)[:-1]
            + _elbow(np.array([half, mid]), np.array([b[0], mid]), b, r))


def _cut(pts, part):
    """The first `part` of a line through `pts`."""
    pts = np.array(pts, dtype=float)
    if part >= 1:
        return pts
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    want = part * cum[-1]
    i = min(int(np.searchsorted(cum, want, "right")) - 1, len(pts) - 2)
    return np.vstack([pts[:i + 1], pts[i] + (want - cum[i]) / max(seg[i], 1e-9) * (pts[i + 1] - pts[i])])


class _Node:
    """One value: where it is in the tree, and how it is drawn at this moment."""

    def __init__(self, value, parent):
        self.value, self.parent, self.kids = value, parent, []
        self.level = parent.level + 1 if parent else 0
        self.folded, self.gone, self.busy = False, False, 0
        self.pos = np.zeros(2)          # where it is, from the root
        self.shown, self.wire = 1.0, 1.0    # how visible the chip is, and the line to it
        self.grown = 1.0                # how much of the line is drawn, from the parent's end
        self.lit, self.tint = 0.0, ManimColor(BLUE)
        self.size, self.count = 1.0, 0.0    # the chip's size, and how visible its "+n" is
        self.badge = self.link = None

    def below(self):
        """Everything under it."""
        out = []
        for kid in self.kids:
            if kid is not None:
                out += [kid] + kid.below()
        return out


class _Change(Animation):
    """Runs a tree's state through a function of the seconds elapsed."""

    def __init__(self, tree, seconds, step, start=None, nodes=(), run_time=None):
        self.seconds, self.step, self.start, self.nodes = seconds, step, start, list(nodes)
        for node in self.nodes:
            node.busy += 1
        super().__init__(tree, run_time=run_time or seconds, rate_func=linear)

    def begin(self):
        if self.start:
            self.start()
        super().begin()

    def interpolate_mobject(self, alpha):
        self.step(alpha * self.seconds)
        self.mobject._lay()

    def finish(self):
        super().finish()
        for node in self.nodes:
            node.busy -= 1
        self.nodes = []


class Tree(VGroup):
    """A tree drawn from its root down.

    children   {parent: [its children]}, naming every node that has children. The root is
               the one that is nobody's child. A single value makes a tree of one node.
    binary     True for a binary tree: every node has a left and a right place, an only
               child sits to its side instead of straight below, and `[None, 7]` is a node
               with only a right child.
    spacing    the distance between neighbours. Unless given, the widest chip and a gap.
    level      the distance from one level down to the next.

    Values are shown as written and must differ from one another. Wherever a node is asked
    for, give its value.

    `tree.chip(value)` is one node's chip and text, for pointing at; `tree.links` and
    `tree.chips` are its parts. The root stays where it is while the tree changes under it.
    """

    def __init__(self, children, binary=False, spacing=None, level=LEVEL, **kwargs):
        super().__init__(**kwargs)
        self.binary, self.level = binary, level
        self._nodes, self._drawn = {}, []       # by value, as planned; and every node still on screen
        # An invisible line one unit long from the root's middle. It moves and grows with
        # the tree, so everything can be laid out from it wherever the tree has been put.
        self._anchor = VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([ORIGIN, RIGHT])
        self.links, self.chips = VGroup(), VGroup()
        self.add(self._anchor, self.links, self.chips)

        if not isinstance(children, dict):
            children = {children: []}
        kids = [k for group in children.values() for k in group if k is not None]
        roots = [v for v in children if v not in kids]
        if len(roots) != 1:
            raise ValueError(f"a tree needs one root, a node that is nobody's child: found {roots}")

        def build(value, parent):
            node = self._make(value, parent)
            for kid in children.get(value, []):
                node.kids.append(None if kid is None else build(kid, node))
            if binary:
                if len(node.kids) > 2:
                    raise ValueError(f"{value!r} has {len(node.kids)} children: a binary tree's nodes have two at most")
                node.kids += [None] * (2 - len(node.kids))
            return node

        self.root = build(roots[0], None)
        self.spacing = spacing or max(n.wide for n in self._drawn) + 0.35
        for node, (pos, shown) in self._plan().items():
            node.pos = pos
        self._order()
        self._lay()

    def chip(self, value):
        """One node's chip and text, for pointing at."""
        return self._find(value).group

    # ---- changing it

    def draw(self, run_time=None):
        """The entrance: the root appears, then each level's lines grow down to it and its
        chips appear. Returns the animation."""
        nodes = [n for n in self._drawn if not n.gone and n.shown > 0.5]
        was = {}

        def start():
            for n in nodes:
                was[n] = n.count
                n.shown, n.grown, n.wire = 0.0, 0.0, 1.0

        def step(u):
            for n in nodes:
                t0 = 0.15 + 0.3 * (n.level - 1)
                n.grown = _ease((u - t0) / 0.3)
                n.shown = _ease(u / 0.3) if n.level == 0 else _ease((u - t0 - 0.15) / 0.3)
                n.count = was.get(n, 0.0) * n.shown

        deepest = max([n.level for n in nodes], default=0)
        return _Change(self, 0.3 + (0.3 * deepest + 0.15 if deepest else 0), step, start, run_time=run_time)

    def add_node(self, value, parent, side=None, at=None, hold=0.8, color=GREEN, run_time=None):
        """A new node under `parent`: the tree moves over, a line grows down from the parent
        and the chip appears, lit for `hold` seconds (None leaves it lit until `unmark`).

        In a binary tree `side` is "left" or "right"; left out, a value smaller than its
        parent goes left and any other right, as in a search tree. Otherwise `at` is its
        place among the parent's children, the last unless given. Returns the animation."""
        self._tidy()
        above = self._find(parent)
        if value in self._nodes:
            raise ValueError(f"the tree already has a {value!r}")
        if above.folded:
            raise ValueError(f"{parent!r} is folded: unfold it before adding under it")
        if self.binary:
            if side is None:
                try:
                    side = "left" if value < above.value else "right"
                except TypeError:
                    side = "left" if above.kids[0] is None else "right"
            i = ("left", "right").index(side)
            if above.kids[i] is not None:
                raise ValueError(f"{parent!r} already has a {side} child, {above.kids[i].value!r}")
            node = self._make(value, above)
            above.kids[i] = node
        else:
            node = self._make(value, above)
            above.kids.insert(len(above.kids) if at is None else at, node)
        plan = self._plan()
        node.pos, node.shown, node.grown, node.size, node.tint = plan[node][0], 0.0, 0.0, 0.7, ManimColor(color)
        self._order()
        self._lay()
        start, slide = self._settle(plan)

        def step(u):
            slide(u)
            born = _ease((u - 0.25) / GROW)
            node.grown, node.shown, node.wire, node.size = _ease(u / GROW), born, 1.0, 0.7 + 0.3 * born
            node.lit = born * (1 if hold is None else 1 - _ease((u - 0.25 - GROW - hold) / FADE))

        seconds = max(MOVE, 0.25 + GROW + (0 if hold is None else hold + FADE))
        return _Change(self, seconds, step, start, [node], run_time)

    def insert_value(self, value, run_time=None):
        """For a binary search tree: go down from the root, left for smaller and right for
        larger, lighting each node passed, and add the value where the way down runs out.
        Returns the animation."""
        if not self.binary:
            raise ValueError("insert_value is for a binary tree: make it with binary=True")
        path, node = [], self.root
        while node is not None:
            if node.value == value:
                raise ValueError(f"the tree already has a {value!r}")
            path.append(node)
            node = node.kids[0 if value < node.value else 1]
        return Succession(self.visit(*[n.value for n in path]), self.add_node(value, path[-1].value), run_time=run_time)

    def remove_node(self, value, hold=0.5, color=RED, run_time=None):
        """A node is lit and, `hold` seconds later, goes with everything under it; the line
        to it draws back and the tree closes up. Returns the animation."""
        self._tidy()
        node = self._find(value)
        if node.parent is None:
            raise ValueError("the root cannot be removed")
        doomed = [node] + node.below()
        kids = node.parent.kids
        if self.binary:
            kids[kids.index(node)] = None
        else:
            kids.remove(node)
        for d in doomed:
            d.gone = True
            del self._nodes[d.value]
        start, slide = self._settle(self._plan(), LIGHT + hold + 0.15)
        was = {}

        def begin():
            start()
            was.update({d: (d.shown, d.wire, d.count) for d in doomed}, lit=node.lit, tint=node.tint)

        def step(u):
            slide(u)
            self._glow(node, color, u, was)
            out = _ease((u - LIGHT - hold) / GROW)
            for d in doomed:
                shown, wire, count = was[d]
                d.shown, d.wire, d.count, d.size = shown * (1 - out), wire * (1 - out), count * (1 - out), 1 - 0.3 * out
            node.grown, node.wire = 1 - out, was[node][1]

        return _Change(self, LIGHT + hold + 0.15 + MOVE, step, begin, doomed, run_time)

    def fold(self, value, run_time=None):
        """Everything under a node goes into it, leaving a count of what is hidden, and the
        tree closes up. Returns the animation."""
        self._tidy()
        node = self._find(value)
        hidden = node.below()
        if node.folded or not hidden:
            raise ValueError(f"{value!r} has nothing under it to fold" if not hidden else f"{value!r} is already folded")
        node.folded = True
        if node.badge is not None:
            node.group.remove(node.badge)
        node.badge = _word(f"+{len(hidden)}", 13 * self._size(), MONO)
        node.group.add(node.badge)
        self._lay()
        start, slide = self._settle(self._plan())

        def step(u):
            slide(u)
            node.count = _ease((u - 0.3) / 0.3)

        return _Change(self, MOVE + 0.1, step, start, [node], run_time)

    def unfold(self, value, run_time=None):
        """A folded node's branch comes back out of it. Returns the animation."""
        self._tidy()
        node = self._find(value)
        if not node.folded:
            raise ValueError(f"{value!r} is not folded")
        node.folded = False
        start, slide = self._settle(self._plan())
        was = {}

        def begin():
            start()
            was["count"] = node.count

        def step(u):
            slide(u)
            node.count = was["count"] * (1 - _ease(u / 0.2))

        return _Change(self, MOVE, step, begin, [node], run_time)

    def visit(self, *values, each=0.5, color=BLUE, run_time=None):
        """Light nodes one after another, `each` seconds apart, as a search passes through
        them. Each goes out as the next comes on. Returns the animation."""
        nodes = [self._find(v) for v in values]

        def step(u):
            for i, n in enumerate(nodes):
                n.tint = ManimColor(color)
                n.lit = _ease((u - i * each) / LIGHT) * (1 - _ease((u - (i + 1) * each) / 0.3))

        return _Change(self, len(nodes) * each + 0.3, step, nodes=nodes, run_time=run_time)

    def mark(self, value, color=BLUE, run_time=None):
        """Light a node and leave it lit, until `unmark`. Returns the animation."""
        node, was = self._find(value), {}
        return _Change(self, LIGHT, lambda u: self._glow(node, color, u, was),
                       lambda: was.update(lit=node.lit, tint=node.tint), [node], run_time)

    def unmark(self, value=None, run_time=None):
        """Put out one node, or every node that is lit. Returns the animation."""
        nodes = list(self._nodes.values()) if value is None else [self._find(value)]
        was = {}

        def step(u):
            for n in nodes:
                n.lit = was[n] * (1 - _ease(u / FADE))

        return _Change(self, FADE, step, lambda: was.update({n: n.lit for n in nodes}), nodes, run_time)

    def scale(self, factor, **kwargs):
        super().scale(factor, **kwargs)
        return self._lay() if hasattr(self, "chips") else self      # the lines thicken with it

    # ---- drawing it

    @staticmethod
    def _glow(node, color, u, was):
        """Bring a node's light up in `color` from however it was lit."""
        k, lit = _ease(u / LIGHT), was.get("lit", 0.0)
        node.tint = _mix(was["tint"], color, k) if lit > 0.01 else ManimColor(color)
        node.lit = lit + (1 - lit) * k

    def _size(self):
        """How much the tree has been scaled since it was made."""
        return float(np.linalg.norm(self._anchor.points[-1] - self._anchor.points[0]))

    def _find(self, value):
        if value not in self._nodes:
            raise ValueError(f"no node {value!r}: the tree has {', '.join(repr(v) for v in self._nodes)}")
        return self._nodes[value]

    def _make(self, value, parent):
        if value in self._nodes:
            raise ValueError(f"{value!r} is in the tree twice: every value must be different")
        node, s = _Node(value, parent), self._size()
        text = str(value)
        mono = not any(ch.isalpha() for ch in text)
        node.label = _word(text, (FONT - 0.5 if mono else FONT - 1) * s, MONO if mono else SANS)
        node.wide = max(WIDE, node.label.width / s + 0.44)
        node.chip = RoundedRectangle(corner_radius=0.13, width=node.wide, height=TALL, stroke_width=0, fill_color=TRACK, fill_opacity=1)
        node.group = VGroup(node.chip, node.label)
        if parent is not None:
            node.link = VMobject(joint_type=LineJointType.ROUND).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
            self.links.add(node.link)
        self._nodes[value] = node
        self._drawn.append(node)
        self.chips.add(node.group)
        return node

    def _order(self):
        """Draw the deepest chips first, so that a branch folds away under its parent."""
        self.chips.submobjects = [n.group for n in sorted(self._drawn, key=lambda n: -n.level)]

    def _tidy(self):
        """Forget nodes that have gone."""
        for node in list(self._drawn):
            if node.gone and not node.busy and node.shown < 0.01:
                self._drawn.remove(node)
                self.chips.remove(node.group)
                if node.link is not None:
                    self.links.remove(node.link)

    def _plan(self):
        """Where every node belongs, and whether it shows: {node: (position, 0 or 1)}. A
        node hidden in a fold belongs where the folded node is."""
        across = {}

        def place(node, left):
            kids = [] if node.folded else list(node.kids)
            if self.binary and kids.count(None) == 2:
                kids = []
            if not kids:
                across[node] = left + 0.5
                return 1.0
            x, middles = left, []
            for kid in kids:
                if kid is None:
                    middles.append(x + EMPTY / 2)
                    x += EMPTY
                else:
                    x += place(kid, x)
                    middles.append(across[kid])
            across[node] = (middles[0] + middles[-1]) / 2
            return x - left

        place(self.root, 0.0)
        plan = {n: (np.array([(x - across[self.root]) * self.spacing, -n.level * self.level]), 1.0) for n, x in across.items()}
        for node in self._nodes.values():
            if node not in plan:
                holder = node.parent
                while holder not in plan:
                    holder = holder.parent
                plan[node] = (plan[holder][0], 0.0)
        return plan

    def _settle(self, plan, delay=0.0):
        """Two functions for an animation: one to call as it begins, and one that moves
        every node `plan` names from where it was to where it belongs."""
        was = {}

        def start():
            was.update({n: (n.pos.copy(), n.shown, n.wire) for n in plan})

        def slide(u):
            k = _ease((u - delay) / MOVE)
            for n, (pos, shown) in plan.items():
                pos0, shown0, wire0 = was[n]
                n.pos, n.shown, n.wire = pos0 + (pos - pos0) * k, shown0 + (shown - shown0) * k, wire0 + (shown - wire0) * k

        return start, slide

    def _lay(self):
        """Put every chip and line where the state says."""
        origin, s = self._anchor.points[0], self._size()
        for n in self._drawn:
            middle = origin + np.array([n.pos[0] * s, n.pos[1] * s, 0])
            wide, tall = n.wide * s * n.size, TALL * s * n.size
            box = RoundedRectangle(corner_radius=min(0.13 * s * n.size, 0.49 * tall), width=wide, height=tall).move_to(middle)
            n.chip.set_points(box.points).set_fill(_mix(TRACK, n.tint, n.lit), n.shown)
            n.label.shift(middle - n.label.anchor.points[0])
            ink = _mix(INK, BG, n.lit)
            for letter in n.label[1:]:
                letter.set_fill(ink, n.shown)
            if n.badge is not None:
                n.badge.shift(middle + np.array([0, -(TALL / 2 + 0.2) * s, 0]) - n.badge.anchor.points[0])
                for letter in n.badge[1:]:
                    letter.set_fill(MUTED, n.count * n.shown)
            if n.link is None:
                continue
            a = origin[:2] + (n.parent.pos + [0, -TALL / 2]) * s
            b = origin[:2] + (n.pos + [0, TALL / 2]) * s
            if n.grown < 0.01 or a[1] - b[1] < 0.08 * s:
                n.link.set_points_as_corners([middle, middle]).set_stroke(LINE, 2.6 * s, 0)
                continue
            pts = _cut(_route(a, b, 0.14 * s), n.grown)
            n.link.set_points_as_corners([[x, y, 0] for x, y in pts]).set_stroke(LINE, 2.6 * s, n.wire)
        return self

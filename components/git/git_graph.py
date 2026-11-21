"""Animated Git history for Manim scenes: commits, branches, HEAD, merges, rebases, reverts.

Copy this file and the skill's icons.py next to scene.py:

    from git_graph import GitGraph

    g = GitGraph()                     # starts on "main", grows right from `origin`
    self.play(g.commit())
    self.play(g.commit())
    self.play(g.checkout("feature", create=True))
    self.play(g.commit())
    self.play(g.checkout("main"))
    self.play(g.merge("feature"))      # fast-forwards when it can, else makes a merge commit

Every operation updates the model at once and returns an animation of the change: pass it
to self.play, one operation per play. To set up history without animating it, pass the
operations to `g.instant(...)` and `self.add(g)`.

How to read the picture: time runs left to right, one column per commit, and each branch
draws its commits on a lane of its own in its own color and line type (solid, dashed,
dotted, dash-dot). The legend above the graph names each one. A branch points at the commit
where its line ends. When it points anywhere else (a new branch with no commits yet, a
branch that was fast-forwarded), that commit's ring is split between its own color and the
branch's. The filled dot is HEAD, in the
color of the checked-out branch (white when detached). Commits that no branch, tag or HEAD
can reach any more fade away. See README.md for every operation.
"""

import numpy as np
from manim import (
    BOLD, LEFT, ORIGIN, PI, RIGHT, TAU, UP,
    Animation, AnimationGroup, Arc, CapStyleType, Circle, Dot, Succession, Text, Transform, Triangle,
    VGroup, VMobject, Wait, interpolate, rush_from, smooth, squish_rate_func, there_and_back,
)

from icons import icon

BG = "#000000"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE, TEAL, VIOLET, PINK = "#60a5fa", "#2dd4bf", "#a78bfa", "#f472b6"
AMBER, GREEN, CYAN, RED = "#fbbf24", "#4ade80", "#22d3ee", "#f87171"

# A branch's look is a color and a line type; the n-th branch takes the n-th of each.
COLORS = [BLUE, TEAL, VIOLET, PINK, GREEN, CYAN]
# Line types as (dash, gap, dash, gap, ...) lengths in graph units; None is a solid line.
PATTERNS = [None, (0.16, 0.12), (0.015, 0.105), (0.25, 0.1, 0.015, 0.1)]

SANS = "Noto Sans"
MONO = "DejaVu Sans Mono"

R = 0.18              # commit radius
HEAD_R = 0.1          # the HEAD dot inside a commit
CORNER = 0.3          # radius of the one corner every lane change turns through
EDGE_WIDTH = 4
RING_WIDTH = 4
LINK_REACH = 0.34     # how far a revert's arrow runs from its lane
LINK_CORNER = 0.16    # the corner radius of that thinner line
LABEL_Y = 0.6         # an id or message sits this far above its commit
GHOST = 0.25          # opacity of a commit while its copy travels
MOVE = dict(run_time=0.9, rate_func=smooth)   # one timing for everything that travels together
Z_EDGE, Z_LINK, Z_NODE, Z_FLY, Z_ARC, Z_HEAD, Z_TEXT = 0, 1, 2, 3, 3.5, 4, 5
_KAPPA = 0.5523       # Bezier handle length for a quarter circle


def _fade(mob, k):
    """Scale every part's opacity by k (0 hides it), keeping parts that are hidden hidden."""
    for m in mob.family_members_with_points():
        m.set_fill(opacity=m.get_fill_opacity() * k)
        m.set_stroke(opacity=m.get_stroke_opacity() * k)
    return mob


def _no_scene(anim):
    """Let a Succession run outside a scene (it looks up self.scene as it steps)."""
    anim.scene = None
    for sub in getattr(anim, "animations", []):
        _no_scene(sub)


def _word(s, **kwargs):
    """Text set on a common baseline: its box is measured with a capital and a descender in
    front, so words with and without tall or hanging letters line up side by side. The word
    comes back centered on y = 0 by that box; place it by shifting sideways only."""
    t = Text("Hg" + s, **kwargs)
    t.shift(-t.get_center())
    return VGroup(*t[2:])


def _left_at(mob, x):
    return mob.shift(RIGHT * (x - mob.get_left()[0]))


def _elbows(points, r):
    """A path through `points` in straight runs, each corner rounded to a quarter circle of
    radius r (less where a run is too short for it)."""
    points = [np.array(p, dtype=float) for p in points]
    m = VMobject()
    m.start_new_path(points[0])
    for before, corner, after in zip(points, points[1:], points[2:]):
        a, b = before - corner, after - corner
        rr = min(r, np.linalg.norm(a) / 2, np.linalg.norm(b) / 2)
        enter = corner + a / np.linalg.norm(a) * rr
        leave = corner + b / np.linalg.norm(b) * rr
        m.add_line_to(enter)
        m.add_cubic_bezier_curve_to(enter + _KAPPA * (corner - enter),
                                    leave + _KAPPA * (corner - leave), leave)
    m.add_line_to(points[-1])
    return m


class _Route:
    """A path measured by distance travelled, so things moving along it keep an even pace
    through corners (Manim's own partial curves go by control points, not by length)."""

    def __init__(self, path):
        self.path = path
        n = path.get_num_curves()
        pieces = np.concatenate([path.get_nth_curve_length_pieces(k) for k in range(n)])
        self.lengths = np.concatenate([[0.0], np.cumsum(pieces)])
        self.props = np.linspace(0, 1, len(self.lengths))
        self.total = float(self.lengths[-1])

    def prop(self, s):
        return float(np.interp(s, self.lengths, self.props))

    def point(self, t):
        """The point a fraction t (0 to 1) of the way along."""
        n = self.path.get_num_curves()
        a = self.prop(t * self.total) * n
        k = min(int(a), n - 1)
        return self.path.get_nth_curve_function(k)(a - k)

    def piece(self, s0, s1):
        """The stretch between distances s0 and s1 from the start."""
        return self.path.get_subcurve(self.prop(s0), self.prop(s1))


class _Stroke(VGroup):
    """A path drawn solid or in a dash pattern, one piece per dash. `periods` fits that many
    whole repeats of the pattern (for closed rings); `inset` leaves that much undrawn at each
    end and fits the pattern so a dash meets both ends (for edges between two commits)."""

    def __init__(self, path, color, width, pattern=None, unit=1.0, periods=None, inset=0.0,
                 cap=CapStyleType.ROUND):
        super().__init__()
        self.recipe = (pattern, unit, periods, inset)
        self.route = _Route(path)
        self.spans = self._spans(self.route.total, *self.recipe)
        for _ in self.spans:
            piece = VMobject().set_stroke(color, width).set_fill(opacity=0)
            piece.set_cap_style(cap)
            self.add(piece)
        self.lay(path)

    def lay(self, path):
        """Draw the line along `path`, with the pieces it already has (see `reserve`):
        dashes keep their size, so a longer path shows more of them."""
        self.route = _Route(path)
        self.spans = self._spans(self.route.total, *self.recipe)[:len(self.submobjects)]
        for i, piece in enumerate(self.submobjects):
            shown = i < len(self.spans)
            piece.set_points(self.route.piece(*self.spans[i if shown else 0]).points)
            piece.set_stroke(opacity=1 if shown else 0)
        self.full = [p.points.copy() for p in self.submobjects[:len(self.spans)]]
        return self

    def reserve(self, n):
        """Have at least n pieces, the spare ones hidden. Pieces can't be added while an
        animation plays, so this comes first."""
        while len(self.submobjects) < n:
            self.add(self.submobjects[0].copy().set_stroke(opacity=0))
        return self

    def count_on(self, path):
        return len(self._spans(_Route(path).total, *self.recipe))

    @staticmethod
    def _spans(total, pattern, unit, periods, inset):
        if pattern is None:
            return [(0.0, total)]
        pattern = [x * unit for x in pattern]
        period, start, end = sum(pattern), inset, total - inset
        if periods:
            pattern = [x * total / (periods * period) for x in pattern]
        elif inset and end - start > period:
            n = max(1, round((end - start + pattern[-1]) / period))
            k = (end - start) / (n * period - pattern[-1])
            pattern = [x * k for x in pattern]
        spans, s, i = [], start, 0
        while s < end - 1e-6:
            step = pattern[i % len(pattern)]
            if i % 2 == 0:
                spans.append((s, min(s + step, end)))
            s += step
            i += 1
        return spans


class _Grow(Animation):
    """Draw a _Stroke in from its start, at an even pace along its length. The stroke stays
    hidden until the animation starts, even when it starts late in a Succession."""

    def __init__(self, stroke, **kwargs):
        for piece in stroke:
            piece.set_stroke(opacity=0)
        super().__init__(stroke, introducer=False, **kwargs)

    def interpolate_mobject(self, alpha):
        s = self.mobject
        reach = self.rate_func(alpha) * s.route.total
        for piece, (s0, s1), full in zip(s.submobjects, s.spans, s.full):
            if reach <= s0:
                piece.set_stroke(opacity=0)
                continue
            piece.set_stroke(opacity=1)
            piece.set_points(full if reach >= s1 else s.route.piece(s0, reach).points)


class _Morph(Animation):
    """Reshape a _Stroke onto another path with the same number of curves, laying the dashes
    afresh each frame so they slide along the line instead of stretching."""

    def __init__(self, stroke, path, **kwargs):
        self.a, self.b = stroke.route.path.points.copy(), path.points.copy()
        stroke.reserve(max(stroke.count_on(stroke.route.path), stroke.count_on(path)) + 3)
        super().__init__(stroke, introducer=False, **kwargs)

    def interpolate_mobject(self, alpha):
        t = self.rate_func(alpha)
        self.mobject.lay(VMobject().set_points(interpolate(self.a, self.b, t)))


class _Along(Transform):
    """A Transform whose mobject travels along `route` rather than in a straight line.
    The mobject must start centered on one end of the route and end centered on the other."""

    def __init__(self, mob, target, route, backwards=False, **kwargs):
        self.route, self.backwards = route, backwards
        super().__init__(mob, target, **kwargs)

    def interpolate_mobject(self, alpha):
        super().interpolate_mobject(alpha)
        a = self.rate_func(alpha)
        t0, t1 = (1, 0) if self.backwards else (0, 1)
        straight = interpolate(self.route.point(t0), self.route.point(t1), a)
        self.mobject.shift(self.route.point(interpolate(t0, t1, a)) - straight)


class _Ripple(Animation):
    """A ring that spreads out from a commit and fades: the commit was rewritten in place."""

    def __init__(self, ring, spread=1.1, **kwargs):
        self.base, self.spread = ring.points.copy(), spread
        self.center = ring.get_center()
        ring.set_stroke(opacity=0)
        super().__init__(ring, introducer=False, **kwargs)

    def interpolate_mobject(self, alpha):
        a = self.rate_func(alpha)
        self.mobject.set_points(self.center + (self.base - self.center) * (1 + self.spread * a))
        self.mobject.set_stroke(opacity=(1 - a) if 0 < alpha < 1 else 0)


class Commit:
    def __init__(self, id, parents, col, lane, style, message=None, kind="commit"):
        self.id, self.parents, self.col, self.lane, self.style = id, parents, col, lane, style
        self.message, self.kind = message, kind
        self.source = None   # the commit a revert undoes
        self.node = None
        self.edges = []
        self.extras = []


class Ref:
    def __init__(self, name, commit, style=None, lane=None, remote=False):
        self.name, self.commit, self.style, self.lane, self.remote = name, commit, style, lane, remote
        self.mob = None      # a branch's share of a ring (None while its line ends at its commit), or a tag's label
        self.key = None      # what the mobject currently shows
        self.entry = None    # a branch's legend entry
        self.entry_key = None


class GitGraph(VGroup):
    def __init__(self, origin=LEFT * 5.6 + UP * 1.2, spacing=1.2, lane_gap=1.0, main="main",
                 labels=False, legend=True):
        """`origin` is where the first commit goes; commits step `spacing` to the right and
        lanes `lane_gap` down. `labels=True` writes each commit's id (C1, C2, ...) above it.
        `legend` is True for a legend row above the graph, a point for the legend's left end,
        or False for none."""
        super().__init__()
        # Two invisible dots record where the graph is and how big: move or scale the whole
        # graph and new parts follow.
        origin = np.array(origin, dtype=float)
        self._anchor = Dot(origin, radius=0.001, fill_opacity=0, stroke_width=0)
        self._unit = Dot(origin + RIGHT, radius=0.001, fill_opacity=0, stroke_width=0)
        self.add(self._anchor, self._unit)
        self.spacing, self.lane_gap, self.show_labels = spacing, lane_gap, labels
        self.commits = {}
        self.branches = {main: Ref(main, None, style=0, lane=0)}
        self.tags = {}
        self.head_branch = main     # None when detached
        self.head_commit = None     # the commit when detached
        self.head_mob = None
        self._head_key = None
        self._col = 0
        self._count = 0
        self._garbage = []
        self._detached_lane = None
        # The legend is a part of the graph with an anchor of its own, so it can be moved
        # alone: g.legend.to_corner(DL).
        self.legend = VGroup()
        self._legend_on = legend is not False
        at = origin + UP * 1.15 + LEFT * R if legend is True or legend is False else np.array(legend, dtype=float)
        self._legend_anchor = Dot(at, radius=0.001, fill_opacity=0, stroke_width=0)
        self.legend.add(self._legend_anchor)
        self.add(self.legend)
        self._head_entry = None
        self._head_entry_key = None
        self._names = {}

    # ------------------------------------------------------------------ public helpers

    def node(self, rev):
        """The mobject of a commit (its ring, and its label if it has one), e.g. for
        Indicate or Circumscribe."""
        return self.commits[self.resolve(rev)].node

    def ref(self, name):
        """The label of tag `name`, the HEAD dot for `ref("HEAD")`, or branch `name`'s share
        of its commit's ring, which is None while the branch's line ends at its commit."""
        if name == "HEAD":
            return self.head_mob
        r = self.branches.get(name) or self.tags[name]
        return r.mob

    def position(self, rev):
        """Where a commit is on screen."""
        c = self.commits[self.resolve(rev)]
        return self._to_scene(self._local(c.col, c.lane))

    def instant(self, *animations):
        """Apply operations without animating them, for history that is there from the start:
        g.instant(g.commit(), g.commit(), g.branch("feature")); self.add(g)."""
        for a in animations:
            _no_scene(a)
            a.begin()
            a.finish()
        self._drop_garbage()
        return self

    def resolve(self, rev):
        """A commit id from a revision: an id, a branch, a tag, HEAD, optionally with ~n."""
        steps = 0
        if "~" in rev:
            rev, n = rev.split("~", 1)
            steps = int(n) if n else 1
        if rev == "HEAD":
            cid = self._head_id()
        elif rev in self.branches:
            cid = self.branches[rev].commit
        elif rev in self.tags:
            cid = self.tags[rev].commit
        elif rev in self.commits:
            cid = rev
        else:
            raise KeyError(f"no commit, branch or tag named {rev!r}")
        for _ in range(steps):
            cid = self.commits[cid].parents[0]
        return cid

    # ------------------------------------------------------------------------ operations

    def commit(self, message=None, id=None, on=None):
        """A new commit on the current branch (or on branch `on`, without checking it out).
        It slides out of its parent, and the branch pointer and HEAD ride along. `message`
        shows above the commit; keep it to a word or two."""
        self._drop_garbage()
        branch = on or self.head_branch
        parent = self.branches[branch].commit if branch else self.head_commit
        c = self._new_commit([parent] if parent else [], branch, message, id)
        self._advance(branch, c.id)
        return self._op(*self._grow_commit(c), *self._refresh_refs(slide_in=not c.parents))

    def branch(self, name, at="HEAD", remote=False):
        """A new branch pointing at `at`: half of that commit's ring takes its color, and it
        joins the legend. `remote=True` marks it in the legend as a remote-tracking branch, like
        origin/main."""
        self._drop_garbage()
        self.branches[name] = Ref(name, self.resolve(at), self._free_style(), remote=remote)
        return self._op(*self._refresh_refs())

    def checkout(self, target, create=False):
        """Move HEAD to a branch, or to a commit (detached HEAD). `create=True` makes the branch
        first, like `git switch -c`."""
        self._drop_garbage()
        if create:
            r = self.branches[target] = Ref(target, self._head_id(), self._free_style())
            here = self.commits.get(self._head_id())
            if not self.head_branch and here and here.lane == self._detached_lane:
                # a branch made on detached work carries on along the same lane
                r.lane, self._detached_lane = self._detached_lane, None
        if target in self.branches:
            self.head_branch, self.head_commit = target, None
        else:
            self.head_branch, self.head_commit = None, self.resolve(target)
        return self._op(*self._refresh_refs(straight=True, arc=-0.6))

    switch = checkout

    def merge(self, name, message=None, ff=True):
        """Merge branch (or commit) `name` into the current branch: a fast-forward when the
        current branch is behind it and `ff` allows, else a merge commit with two parents."""
        self._drop_garbage()
        theirs, ours = self.resolve(name), self._head_id()
        if self._is_ancestor(theirs, ours):
            return self._op(Wait(0.3))  # already up to date
        if ff and self._is_ancestor(ours, theirs):
            self._advance(self.head_branch, theirs)
            return self._op(*self._straighten(self.head_branch, ours, theirs, 1.2),
                            *self._refresh_refs(run_time=1.2))
        c = self._new_commit([ours, theirs], self.head_branch, message, None, "merge")
        self._advance(self.head_branch, c.id)
        return self._op(*self._grow_commit(c), *self._refresh_refs())

    def rebase(self, onto):
        """Replay the current branch's own commits on top of `onto`: copies of them travel
        to the new base together, as one chain, and the originals fade."""
        self._drop_garbage()
        branch = self.head_branch
        tip, base = self._head_id(), self.resolve(onto)
        mine = self._only_in(tip, base)
        if not mine:
            if self._is_ancestor(tip, base):  # nothing of our own: just catch up
                self._advance(branch, base)
                return self._op(*self._straighten(branch, tip, base, 1.2),
                                *self._refresh_refs(run_time=1.2))
            return self._op(Wait(0.3))
        # The copies take over the branch's lane, unless something else keeps the originals.
        self._advance(branch, None)
        kept = self._reachable() & set(mine)
        self._advance(branch, tip)
        lane = None if kept or not branch else self.branches[branch].lane
        parent, pairs = base, []
        for old in mine:
            o = self.commits[old]
            c = self._new_commit([parent], branch, o.message, self._prime(o.id), lane=lane)
            pairs.append((o, c))
            parent = c.id
        self._advance(branch, parent)
        return self._op(AnimationGroup(*self._replay(pairs, run_time=1.3),
                                       *self._refresh_refs(straight=True, run_time=1.3)),
                        self._collect(), sequential=True)

    def cherry_pick(self, rev, message=None):
        """Copy a commit onto the current branch: the copy flies over from the original as
        its edge grows out to meet it."""
        self._drop_garbage()
        o = self.commits[self.resolve(rev)]
        c = self._new_commit([self._head_id()], self.head_branch, message or o.message,
                             self._prime(o.id))
        self._advance(self.head_branch, c.id)
        final = self._build_node(c)
        c.node = o.node.copy().set_z_index(Z_FLY)
        edge = self._build_edge(self.commits[c.parents[0]], c)
        c.edges.append(edge)
        self.add(edge, c.node)
        return self._op(Transform(c.node, final, path_arc=-0.5, **MOVE), _Grow(edge, **MOVE),
                        *self._dim(o, o.id in self._reachable(), MOVE["run_time"]),
                        *self._refresh_refs())

    def revert(self, rev, message=None):
        """A new commit that undoes an earlier one, with a red arrow back to it."""
        self._drop_garbage()
        target = self.resolve(rev)
        c = self._new_commit([self._head_id()], self.head_branch, message, None, "revert")
        c.source = target
        self._advance(self.head_branch, c.id)
        grow = self._grow_commit(c)
        line, tip = self._build_revert_link(c)
        link = VGroup(line, tip)
        c.extras.append(link)
        self.add(link)
        tip_final = tip.copy()
        _fade(tip, 0)
        return self._op(AnimationGroup(*grow, *self._refresh_refs()),
                        _Grow(line, run_time=0.6), Transform(tip, tip_final, run_time=0.2),
                        sequential=True)

    def reset(self, target):
        """Move the current branch (or a detached HEAD) back or forward to `target`, e.g.
        "HEAD~1". Commits left unreachable fade away."""
        self._drop_garbage()
        self._advance(self.head_branch, self.resolve(target))
        return self._op(AnimationGroup(*self._refresh_refs()), self._collect(), sequential=True)

    def amend(self, message=None):
        """Replace the current commit with a new one, as `git commit --amend` does: the
        commit is swapped in place with a ripple."""
        self._drop_garbage()
        old = self.commits[self._head_id()]
        branch = self.head_branch
        self._advance(branch, None)
        in_place = old.id not in self._reachable()
        self._advance(branch, old.id)
        if not in_place:
            # Something else still points at the old commit, so it stays where it is and
            # the replacement finds a lane that is clear.
            c = self._new_commit(list(old.parents), branch, message or old.message, self._prime(old.id))
            self._advance(branch, c.id)
            return self._op(*self._replay([(old, c)]), *self._refresh_refs(straight=True))
        c = self._new_commit(list(old.parents), branch, message or old.message, self._prime(old.id),
                             col=old.col, lane=old.lane)
        self._advance(branch, c.id)
        c.edges, old.edges = old.edges, []
        final = self._build_node(c)
        c.node = _fade(final.copy(), 0)
        ripple = Circle(radius=R + 0.12).move_to(self._local(c.col, c.lane))
        ripple = self._place(ripple).set_stroke(self._color(c.style), 5).set_fill(opacity=0)
        ripple.set_z_index(Z_FLY)
        self.add(c.node, ripple)
        self._garbage.append(ripple)
        return self._op(Transform(c.node, final, run_time=0.5), _Ripple(ripple, run_time=0.9, rate_func=rush_from),
                        *self._refresh_refs(), self._collect())

    def tag(self, name, at="HEAD"):
        """A tag on commit `at`, written above it."""
        self._drop_garbage()
        self.tags[name] = Ref(name, self.resolve(at))
        return self._op(*self._refresh_refs())

    def move(self, name, to):
        """Point branch `name` at `to` without touching HEAD: a fetch moving origin/main, a
        push, or `git branch -f`."""
        self._drop_garbage()
        self.branches[name].commit = self.resolve(to)
        return self._op(AnimationGroup(*self._refresh_refs()), self._collect(), sequential=True)

    def delete_branch(self, name):
        """Delete branch `name`; commits only it reached fade away."""
        self._drop_garbage()
        r = self.branches.pop(name)
        gone = [self._vanish(m) for m in (r.mob, r.entry) if m is not None]
        return self._op(*gone, *self._refresh_refs(), self._collect())

    # ------------------------------------------------------------------------- model

    def _head_id(self):
        return self.branches[self.head_branch].commit if self.head_branch else self.head_commit

    def _advance(self, branch, cid):
        if branch:
            self.branches[branch].commit = cid
        else:
            self.head_commit = cid

    def _free_style(self):
        """The first look no branch has and no commit still on screen was drawn in."""
        used = {b.style for b in self.branches.values()} | {c.style for c in self.commits.values()}
        style = 0
        while style in used:
            style += 1
        return style

    def _reach(self):
        """For each lane, the last column a commit sits in, and the last column anything
        runs to (a merge's line runs along its lane up to the merge commit)."""
        commits, lines = {}, {}
        for c in self.commits.values():
            commits[c.lane] = max(commits.get(c.lane, -1), c.col)
            for p in c.parents[1:]:
                lane = self.commits[p].lane
                lines[lane] = max(lines.get(lane, -1), c.col + 0.5)
        return commits, {k: max(commits.get(k, -1), lines.get(k, -1)) for k in {*commits, *lines}}

    def _next_lane(self, branch, after):
        """The lane the next commit of `branch` (None: a detached HEAD) goes on, forking off
        at column `after`: its own lane while that has no commit further right, else the
        first lane nobody else holds that is empty from there on."""
        commits, anything = self._reach()
        own = self.branches[branch].lane if branch else self._detached_lane
        if own is not None and commits.get(own, -1) <= after:
            return own
        held = {b.lane for name, b in self.branches.items() if name != branch}
        if branch:
            held.add(self._detached_lane)
        lane = 0
        while lane in held or anything.get(lane, -1) > after:
            lane += 1
        return lane

    def _lane_for(self, branch, after):
        """A branch gets its lane with its first commit, so a branch that never commits
        (origin/main, say) doesn't leave an empty row."""
        lane = self._next_lane(branch, after)
        if branch:
            self.branches[branch].lane = lane
        else:
            self._detached_lane = lane
        return lane

    def _release_lanes(self):
        """A lane with no commits left on it goes back for the next branch to take."""
        used = {c.lane for c in self.commits.values()}
        for b in self.branches.values():
            if b.lane not in used:
                b.lane = None
        if self._detached_lane not in used:
            self._detached_lane = None

    def _new_commit(self, parents, branch, message, id, kind="commit", col=None, lane=None):
        if id is None:
            self._count += 1
            id = f"C{self._count}"
            while id in self.commits:
                self._count += 1
                id = f"C{self._count}"
        style = self.branches[branch].style if branch else None
        if col is None:
            col = self._col
            self._col += 1
        after = max((self.commits[p].col for p in parents), default=-1)
        if lane is None:
            lane = self._lane_for(branch, after)
        c = Commit(id, parents, col, lane, style, message, kind)
        self.commits[id] = c
        return c

    def _prime(self, id):
        new = id + "'"
        while new in self.commits:
            new += "'"
        return new

    def _ancestors(self, cid):
        seen, stack = set(), [cid] if cid else []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(self.commits[x].parents)
        return seen

    def _is_ancestor(self, a, b):
        return a in self._ancestors(b)

    def _only_in(self, tip, base):
        """Commits reachable from tip but not base, oldest first, merges left out."""
        theirs = self._ancestors(base)
        mine = [x for x in self._ancestors(tip) if x not in theirs]
        mine.sort(key=lambda x: self.commits[x].col)
        return [x for x in mine if len(self.commits[x].parents) < 2]

    def _reachable(self):
        tips = [b.commit for b in self.branches.values()] + [t.commit for t in self.tags.values()]
        tips.append(self._head_id())
        seen = set()
        for t in tips:
            if t:
                seen |= self._ancestors(t)
        return seen

    def _chain(self, ancestor, descendant):
        """The edges from `ancestor` up to `descendant`, as (parent, child, parent index),
        or None when one isn't an ancestor of the other. First parents are tried first."""
        if ancestor == descendant:
            return []
        seen = set()

        def walk(cid):
            if cid in seen:
                return None
            seen.add(cid)
            for i, p in enumerate(self.commits[cid].parents):
                if p == ancestor:
                    return [(p, cid, i)]
                found = walk(p)
                if found is not None:
                    return found + [(p, cid, i)]
            return None

        return walk(descendant)

    # ------------------------------------------------------------------------ drawing

    def _local(self, col, lane):
        return np.array([col * self.spacing, -lane * self.lane_gap, 0.0])

    def _scale(self):
        return float(np.linalg.norm(self._unit.get_center() - self._anchor.get_center()))

    def _to_scene(self, p):
        return self._anchor.get_center() + self._scale() * np.array(p)

    def _place(self, mob, legend=False):
        """Move a mobject drawn in graph units (first commit at the origin) onto the graph,
        or onto the legend (its left end at the origin)."""
        anchor = self._legend_anchor if legend else self._anchor
        return mob.scale(self._scale(), about_point=ORIGIN).shift(anchor.get_center())

    def _color(self, style):
        return MUTED if style is None else COLORS[style % len(COLORS)]

    def _pattern(self, style):
        return None if style is None else PATTERNS[style % len(PATTERNS)]

    def _stroke(self, path, style, width, color=None, legend=False, **kwargs):
        """`path`, drawn in graph units, as a line in a branch's color and line type."""
        return _Stroke(self._place(path, legend), color or self._color(style), width,
                       self._pattern(style), unit=self._scale(), **kwargs)

    def _label_of(self, c):
        return c.message or (c.id if self.show_labels else None)

    def _build_node(self, c):
        p = self._local(c.col, c.lane)
        ring = Circle(radius=R, stroke_color=self._color(c.style), stroke_width=RING_WIDTH,
                      fill_color=BG, fill_opacity=1).move_to(p)
        node = VGroup(ring)
        text = self._label_of(c)
        if text:
            label = Text(text, font=SANS if c.message else MONO, font_size=16,
                         color=INK if c.message else MUTED)
            label.move_to(p + UP * LABEL_Y)
            label.set_stroke(BG, 6, background=True)  # a halo: lines break cleanly behind it
            node.add(label)
        # Later commits sit under earlier ones, so a new commit slides out from beneath its parent.
        return self._place(node).set_z_index(Z_NODE - 1e-3 * c.col)

    def _edge_path(self, a, b, bend="start"):
        """From commit a to commit b, in graph units: straight along a lane, or between lanes
        through one quarter-circle corner. A branch drops straight out of its parent and
        turns onto its lane (bend "start"); a merge runs along its lane and turns up into
        the merge commit (bend "end")."""
        pa, pb = self._local(a.col, a.lane), self._local(b.col, b.lane)
        m = VMobject()
        m.start_new_path(pa)
        if abs(pa[1] - pb[1]) < 1e-6:
            # in three pieces, like a turn, so one can be reshaped into the other
            for t in (0.25, 0.75, 1):
                m.add_line_to(interpolate(pa, pb, t))
            return m
        corner = np.array([pa[0], pb[1], 0]) if bend == "start" else np.array([pb[0], pa[1], 0])
        r = min(CORNER, np.linalg.norm(corner - pa), np.linalg.norm(pb - corner))
        enter = corner + (pa - corner) / np.linalg.norm(pa - corner) * r
        leave = corner + (pb - corner) / np.linalg.norm(pb - corner) * r
        m.add_line_to(enter)
        m.add_cubic_bezier_curve_to(enter + _KAPPA * (corner - enter),
                                    leave + _KAPPA * (corner - leave), leave)
        m.add_line_to(pb)
        return m

    def _build_edge(self, parent, child, second=False):
        """The line into `child` from a parent, in the child's look. A merge's second parent
        arrives in the look of the branch that was merged in."""
        path = self._edge_path(parent, child, "end" if second else "start")
        style = parent.style if second else child.style
        return self._stroke(path, style, EDGE_WIDTH, inset=R * self._scale()).set_z_index(Z_EDGE)

    def _route(self, a, b):
        """The way along the history from commit a to commit b, when one is an ancestor of
        the other: (route, backwards)."""
        if a == b or a not in self.commits or b not in self.commits:
            return None
        chain, backwards = self._chain(a, b), False
        if chain is None:
            chain, backwards = self._chain(b, a), True
        if not chain:
            return None
        path = VMobject()
        for p, c, i in chain:
            seg = self._edge_path(self.commits[p], self.commits[c], "end" if i else "start")
            path.append_points(seg.points)
        return _Route(self._place(path)), backwards

    def _build_revert_link(self, c):
        """A thin red arrow from a revert back to the commit it undoes, in elbows like every
        other line: out of the revert, along beside the lane, into the commit. It runs over
        the lane, or under it when a label or tag is in the way above."""
        t = self.commits[c.source]
        tagged = {r.commit for r in self.tags.values()}
        side = -1 if any(self._label_of(x) or x.id in tagged for x in (c, t)) else 1

        a = self._local(c.col, c.lane) + UP * side * (R + 0.12)
        b = self._local(t.col, t.lane) + UP * side * (R + 0.18)
        y = (max if side > 0 else min)(a[1], b[1]) + side * LINK_REACH
        path = _elbows([a, [a[0], y, 0], [b[0], y, 0], b], LINK_CORNER)
        line = _Stroke(self._place(path), RED, 2.5).set_z_index(Z_LINK)
        tip = Triangle(fill_color=RED, fill_opacity=1, stroke_width=0).scale(0.07)
        if side > 0:
            tip.rotate(np.pi)
        tip.move_to(b - UP * side * 0.04)
        return line, self._place(tip).set_z_index(Z_LINK)

    def _guests(self):
        """Which branches need a mark, as {name: (index, count)}. A branch whose line ends
        at its commit needs none: the end of the line is the pointer. Any other branch is a
        guest on its commit and takes a share of that commit's ring; `count` is how many
        guests the commit has and `index` is this one's place among them."""
        continued = {(p, c.style) for c in self.commits.values() for p in c.parents[:1]}
        at = {}
        for name, r in self.branches.items():
            if not r.commit:
                continue
            tip = self.commits[r.commit]
            if tip.style != r.style or (tip.id, r.style) in continued:
                at.setdefault(tip.id, []).append(name)
        return {name: (i, len(names)) for names in at.values() for i, name in enumerate(names)}

    def _share(self, r, index, count):
        """A guest branch's share of its commit's ring: an arc in the branch's color laid
        over the ring. The commit keeps the share on its left, where its own line comes in;
        one guest takes the right half, two take a third each, and so on."""
        c = self.commits[r.commit]
        share = TAU / (count + 1)
        arc = Arc(radius=R, start_angle=PI + share / 2 + index * share, angle=share,
                  arc_center=self._local(c.col, c.lane))
        # a touch wider than the ring, so none of the ring's color shows at its edges
        return _Stroke(self._place(arc), self._color(r.style), RING_WIDTH + 0.5,
                       cap=CapStyleType.BUTT).set_z_index(Z_ARC)

    def _tag_target(self, r, index):
        c = self.commits[r.commit]
        parts = VGroup(icon("tabler/outline/tag", color=AMBER, height=0.2),
                       Text(r.name, font=SANS, font_size=17, color=AMBER)).arrange(RIGHT, buff=0.07)
        parts[1].set_stroke(BG, 5, background=True)
        y = LABEL_Y + (0.3 if self._label_of(c) else 0) + index * 0.28
        parts.move_to(self._local(c.col, c.lane) + UP * y)
        return self._place(parts).set_z_index(Z_TEXT)

    def _head_color(self):
        return self._color(self.branches[self.head_branch].style) if self.head_branch else INK

    def _head_target(self):
        c = self.commits[self._head_id()]
        dot = Dot(self._local(c.col, c.lane), radius=HEAD_R, color=self._head_color())
        return self._place(dot).set_z_index(Z_HEAD)

    # -------------------------------------------------------------------------- legend

    def _legend_head(self):
        dot = Dot(radius=HEAD_R, color=self._head_color()).move_to(RIGHT * HEAD_R)
        text = _word("HEAD", font=SANS, font_size=20, weight=BOLD, color=INK)
        return VGroup(dot, _left_at(text, 2 * HEAD_R + 0.12))

    def _legend_entry(self, r):
        """A sample of the branch's line, then its name."""
        line = _Stroke(VMobject().set_points_as_corners([ORIGIN, RIGHT * 0.56]), self._color(r.style),
                       EDGE_WIDTH, self._pattern(r.style))
        if r.name not in self._names:   # Text is slow to build; keep one per name
            parts = VGroup(_left_at(_word(r.name, font=SANS, font_size=20), 0))
            if r.remote:
                cloud = icon("tabler/outline/cloud", color=MUTED, height=0.24).move_to(ORIGIN)
                parts.add_to_back(_left_at(cloud, 0))
                _left_at(parts[1], cloud.width + 0.08)
            self._names[r.name] = parts
        name = self._names[r.name].copy()
        name[-1].set_color(INK if r.name == self.head_branch else MUTED)
        return VGroup(line, _left_at(name, 0.56 + 0.16))

    def _refresh_legend(self):
        if not self._legend_on:
            return []
        anims, x = [], 0.0
        head = self._legend_head()
        width = head.width
        key = self._head_color()
        if self._head_entry is None:
            if self._head_id() is not None:
                self._head_entry = self._place(head, legend=True)
                anims.append(self._enter(self._head_entry, shift=LEFT * 0.2, parent=self.legend))
        elif key != self._head_entry_key:
            anims.append(Transform(self._head_entry, self._place(head, legend=True), run_time=0.6))
        self._head_entry_key = key
        x += width + 0.5
        for r in self.branches.values():
            entry = self._legend_entry(r)
            entry.shift(RIGHT * x)
            key = (round(x, 3), r.name == self.head_branch)
            x += entry.width + 0.5
            if key == r.entry_key:
                continue
            self._place(entry, legend=True)
            if r.entry is None:
                r.entry = entry
                anims.append(self._enter(entry, shift=LEFT * 0.2, parent=self.legend))
            else:
                anims.append(Transform(r.entry, entry, run_time=0.6))
            r.entry_key = key
        return anims

    # ---------------------------------------------------------------------- animation

    def _op(self, *anims, sequential=False):
        anims = [a for a in anims if a is not None]
        if not anims:
            anims = [Wait(0.2)]
        if sequential:
            return Succession(*anims, group=self)
        return AnimationGroup(*anims, group=self)

    def _enter(self, mob, shift=None, scale=None, parent=None, run_time=0.6):
        """Add `mob`, hidden and nudged off its place (`shift`, in graph units) or resized,
        and return the animation that brings it in. Nothing pops: it fades as it settles."""
        final = mob.copy()
        if shift is not None:
            mob.shift(np.array(shift) * self._scale())
        if scale is not None:
            mob.scale(scale)
        _fade(mob, 0)
        (parent or self).add(mob)
        return Transform(mob, final, run_time=run_time)

    def _vanish(self, mob, run_time=0.6):
        """Fade `mob` out; it leaves the graph at the start of the next operation."""
        self._garbage.append(mob)
        return Transform(mob, _fade(mob.copy(), 0), run_time=run_time)

    def _drop_garbage(self):
        for m in self._garbage:
            self.remove(m)
            self.legend.remove(m)
        self._garbage = []

    def _grow_commit(self, c):
        """The commit slides out from under its first parent along its edge, which draws in
        behind it. A second parent's edge (a merge) arrives at the same moment."""
        final = self._build_node(c)
        if not c.parents:  # the first commit: there is nothing to grow from
            c.node = final.copy()
            return [self._enter(c.node, shift=LEFT * 0.5, run_time=MOVE["run_time"])]
        anims = []
        for i, pid in enumerate(c.parents):
            e = self._build_edge(self.commits[pid], c, second=i > 0)
            c.edges.append(e)
            self.add(e)
            anims.append(_Grow(e, **MOVE))
        first = self.commits[c.parents[0]]
        c.node = final.copy()
        c.node.shift((self._local(first.col, first.lane) - self._local(c.col, c.lane)) * self._scale())
        c.node[0].scale(0.8)
        _fade(c.node[1:], 0)
        self.add(c.node)
        anims.append(_Along(c.node, final, c.edges[0].route, **MOVE))
        return anims

    def _dim(self, o, survives, run_time):
        """A commit dims while its copy travels. It brightens again if it `survives` (still
        reachable); if not, it stays dim until the collection fades it away."""
        rate = there_and_back if survives else smooth
        return [Transform(m, _fade(m.copy(), GHOST), run_time=run_time, rate_func=rate)
                for m in [o.node, *o.edges, *o.extras]]

    def _replay(self, pairs, run_time=MOVE["run_time"]):
        """Copies of old commits, with their edges, travel to the new commits' places, all
        at once: a chain moves as one piece and stays connected the whole way."""
        live = self._reachable()
        timing = dict(run_time=run_time, rate_func=smooth)
        anims = []
        for o, c in pairs:
            final = self._build_node(c)
            c.node = o.node.copy().set_z_index(Z_FLY)
            if c.parents:
                parent = self.commits[c.parents[0]]
                if o.edges and o.style == c.style:  # the old edge's copy bends to its new shape
                    edge = o.edges[0].copy()
                    anims.append(_Morph(edge, self._place(self._edge_path(parent, c)), **timing))
                else:
                    edge = self._build_edge(parent, c)
                    anims.append(_Grow(edge, **timing))
                c.edges.append(edge)
                self.add(edge)
            self.add(c.node)
            anims.append(Transform(c.node, final, **timing))
            anims += self._dim(o, o.id in live, run_time)
        return anims

    def _straighten(self, branch, ours, theirs, run_time):
        """After a fast-forward the history from `ours` to `theirs` is one line, so draw it
        as one: its commits move onto the branch's own lane, when that lane is clear."""
        r = self.branches.get(branch)
        chain = self._chain(ours, theirs) if ours else None
        if r is None or r.lane is None or not chain or any(i for _, _, i in chain):
            return []
        o = self.commits[ours]
        if o.lane != r.lane or any(c.lane == r.lane and c.col > o.col for c in self.commits.values()):
            return []
        moved = {cid for _, cid, _ in chain if self.commits[cid].lane != r.lane}
        for cid in moved:
            self.commits[cid].lane = r.lane
        self._release_lanes()
        return self._relayout(moved, run_time)

    def _relayout(self, moved, run_time):
        """Commits in `moved` have new places: they and every line touching them follow."""
        timing = dict(run_time=run_time, rate_func=smooth)
        anims = []
        for c in self.commits.values():
            if c.id in moved:
                anims.append(Transform(c.node, self._build_node(c), **timing))
            for i, pid in enumerate(c.parents):
                if c.id in moved or pid in moved:
                    path = self._edge_path(self.commits[pid], c, "end" if i else "start")
                    anims.append(_Morph(c.edges[i], self._place(path), **timing))
            if c.source in self.commits and (c.id in moved or c.source in moved):
                anims.append(Transform(c.extras[0], VGroup(*self._build_revert_link(c)), **timing))
        return anims

    def _travel(self, mob, target, a, b, straight, run_time, arc=0):
        found = None if straight else self._route(a, b)
        timing = dict(run_time=run_time, rate_func=smooth)
        if found:
            return _Along(mob, target, found[0], backwards=found[1], **timing)
        return Transform(mob, target, path_arc=arc if a != b else 0, **timing)

    def _refresh_refs(self, straight=False, slide_in=False, run_time=MOVE["run_time"], arc=0):
        """Every pointer moves to where the model says, along the history when there is a
        way along it (unless `straight`); new ones come in. Returns the animations."""
        anims = []
        guests = self._guests()
        late = squish_rate_func(smooth, 0.55, 1)   # a share sweeps in once the pointer has arrived
        for name, r in self.branches.items():
            if not r.commit:
                continue
            key = None
            if name in guests:
                key = (r.commit, *guests[name], self.commits[r.commit].lane)
            if key == r.key:
                continue
            target = self._share(r, *guests[name]) if key else None
            if key is None:           # its line ends at its commit again: the mark goes
                anims.append(self._vanish(r.mob, run_time=0.3))
                r.mob = None
            elif r.mob is None:
                r.mob = target
                self.add(target)
                anims.append(_Grow(target, run_time=run_time, rate_func=late))
            else:
                anims.append(self._travel(r.mob, target, r.key[0], r.commit, straight, run_time))
            r.key = key
        per_commit = {}
        for r in self.tags.values():
            i = per_commit.get(r.commit, 0)
            per_commit[r.commit] = i + 1
            key = (r.commit, i, self.commits[r.commit].lane)
            if r.key == key:
                continue
            target = self._tag_target(r, i)
            if r.mob is None:
                r.mob = target
                anims.append(self._enter(target, shift=0.12 * LEFT))
            else:
                anims.append(Transform(r.mob, target, run_time=0.6))
            r.key = key
        cid = self._head_id()
        if cid is not None:
            key = (cid, self._head_color(), self.commits[cid].lane)
            if key != self._head_key:
                target = self._head_target()
                if self.head_mob is None:
                    self.head_mob = target
                    if slide_in:
                        anims.append(self._enter(target, shift=LEFT * 0.5, run_time=run_time))
                    else:
                        anims.append(self._enter(target, scale=0.5))
                else:
                    anims.append(self._travel(self.head_mob, target, self._head_key[0], cid,
                                              straight, run_time, arc=arc))
                self._head_key = key
        return anims + self._refresh_legend()

    def _collect(self):
        """Fade out commits that nothing reaches any more, and free the columns they held
        at the right end."""
        live = self._reachable()
        dead = [c for c in self.commits.values() if c.id not in live]
        anims = []
        for c in dead:
            del self.commits[c.id]
            for m in [c.node, *c.edges, *c.extras]:
                if m is not None:
                    anims.append(self._vanish(m))
        self._col = max((c.col for c in self.commits.values()), default=-1) + 1
        self._release_lanes()
        return AnimationGroup(*anims) if anims else None

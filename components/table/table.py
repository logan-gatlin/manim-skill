"""A table of records: rows are inserted, updated and deleted, and a bar at the left of a row
marks the change.

Copy this file and the skill's code_font.py next to scene.py:

    from table import DataTable

    t = DataTable(["id", "item", "qty", "status"],
                  [["1001", "Keyboard", 1, "shipped"],
                   ["1002", "Monitor", 2, "paid"],
                   ["1003", "Cable", 5, "paid"]])
    self.play(t.draw())
    self.play(t.insert_row(["1004", "Desk", 1, "new"]))    # opens at the bottom, marked green
    self.play(t.update_row("1002", status="shipped"))      # marked blue while the value changes
    self.play(t.delete_row("1003"))                        # marked red, then closes up

It is called DataTable because Manim has a Table of its own, and its methods end in _row
because every Manim object already has an insert and an update. See README.md.
"""

from types import SimpleNamespace

import numpy as np
from manim import (MEDIUM, NORMAL, ORIGIN, Animation, CapStyleType, ManimColor, RoundedRectangle, Text, VGroup, VMobject,
                   interpolate_color, linear)

from code_font import MONO

LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE, RED, GREEN = "#60a5fa", "#f87171", "#4ade80"
SANS = "Noto Sans"

FONT = 18         # the size of the text
PITCH = 0.55      # a row's height
GAP = 0.7         # the space between columns
PAD = 0.3         # the space at each end of a row
OPEN = 0.5        # seconds a row takes to open or close
LIGHT = 0.3       # seconds a bar takes to come on
FADE = 0.5        # ...and to go off
SWAP = 0.45       # seconds a value takes to change
SLIDE = 0.38      # how far the old value rises as it goes, in rows


def _mix(a, b, k):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(k, 0, 1)))


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


KAPPA = 4 / 3 * np.tan(np.pi / 8)      # how far a quarter circle's handles are from its ends, in radii


def _rounded(w, h, r):
    """The points Manim's RoundedRectangle has, worked out directly: four quarter circles
    of radius `r` joined by straight lines, anticlockwise from the right-hand side. Building
    the mobject takes 4 ms, which is too slow to do on every frame."""
    x, y, k = w / 2, h / 2, r * KAPPA
    a = np.array([[x, y - r], [x, y - r + k], [x - r + k, y], [x - r, y]])      # the top right corner
    corners = [a, a[::-1] * [-1, 1], a * [-1, -1], a[::-1] * [1, -1]]
    points = np.zeros((32, 3))
    for i, (corner, after) in enumerate(zip(corners, corners[1:] + corners[:1])):
        points[8 * i:8 * i + 4, :2] = corner
        points[8 * i + 4:8 * i + 8, :2] = np.linspace(corner[-1], after[0], 4)
    return points


def _word(s, size, font, weight=NORMAL, right=False):
    """The letters of `s` behind an invisible point: the point is where the text starts (or
    ends, when `right`) and half-way up its line, so putting the point somewhere puts every
    word on the same baseline whatever letters it has."""
    t = Text("Hg" + s + "H", font=font, font_size=size, weight=weight)
    x = t[-1].get_left()[0] if right else t[1].get_right()[0]
    letters = VGroup(*t[2:-1]).shift([-x, -t[:2].get_center()[1], 0])
    word = VGroup(VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([ORIGIN, ORIGIN]), *letters)
    word.anchor = word[0]
    word.extent = 0.0 if not len(letters) else float(-letters.get_left()[0] if right else letters.get_right()[0])
    return word


class _Change(Animation):
    """Runs a table's state through a function of the seconds elapsed."""

    def __init__(self, table, seconds, step, start=None, rows=(), run_time=None):
        self.seconds, self.step, self.start, self.rows = seconds, step, start, rows
        for row in rows:
            row.busy += 1
        super().__init__(table, run_time=run_time or seconds, rate_func=linear)

    def begin(self):
        if self.start:
            self.start()
        super().begin()

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole table here, and never use the copy

    def interpolate_mobject(self, alpha):
        self.step(alpha * self.seconds)
        self.mobject._lay()

    def finish(self):
        super().finish()
        for row in self.rows:
            row.busy -= 1
        self.rows = ()


class DataTable(VGroup):
    """Column names over a rule, and a row for each record.

    columns   the column names.
    rows      the records to begin with: a list of values for each, in column order.
    key       the column that names a row, by name or position: it is drawn muted, and it
              is what `update_row`, `delete_row` and `mark` look a row up by. The first column
              unless given; None for a table with no such column.
    right     the columns to align right. Unless given, those whose values are numbers.
    mono      the columns to set in the code font. Unless given, those whose values have no
              letters in them (ids, counts, prices, times).
    widths    {column: width} for columns that need more room than their first values take,
              because a longer value will arrive later.

    Wherever a row is asked for, a number is its position from the top, counting from 0,
    and a string is looked up in the key column.

    `table.header`, `table.rule` and `table.body` (the rows, top to bottom) are its parts;
    `table.cell(row, column)` is one value's text and `table.count` the number of rows.
    """

    def __init__(self, columns, rows=(), key=0, right=None, mono=None, widths=None, **kwargs):
        super().__init__(**kwargs)
        rows = [list(r) for r in rows]
        names = [str(c) for c in columns]
        self._cols = []
        for j, name in enumerate(names):
            values = [r[j] for r in rows]
            number = bool(values) and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)
            plain = bool(values) and not any(ch.isalpha() for v in values for ch in str(v))
            self._cols.append(SimpleNamespace(name=name, right=number if right is None else name in right,
                                              mono=plain if mono is None else name in mono, x=0.0))
        self._key = None if key is None else self._cols[key if isinstance(key, int) else names.index(key)]
        self._head = 1.0                       # how far the header and its rule are drawn in
        self._planned = []                     # the rows there will be once every move made so far has played

        self.header = VGroup(*[_word(c.name, FONT - 1.5, SANS, MEDIUM, c.right) for c in self._cols])
        self.rule = VMobject().set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
        self.body = VGroup()
        for values in rows:
            row = self._row(values)
            self._planned.append(row)
            self.body.add(row)

        # each column is as wide as its widest value
        x = PAD
        for j, col in enumerate(self._cols):
            width = max([self.header[j].extent] + [row.cells[j].extent for row in self.body])
            width = (widths or {}).get(col.name, width)
            col.x = x + (width if col.right else 0)
            x += width + GAP
        self._width = x - GAP + PAD
        # An invisible line along the rule under the header. It moves and grows with the
        # table, so everything can be laid out from it wherever the table has been put.
        self._anchor = VMobject(stroke_width=0, fill_opacity=0)
        self._anchor.set_points_as_corners([[-self._width / 2, 0, 0], [self._width / 2, 0, 0]])
        self.add(self._anchor, self.header, self.rule, self.body)
        self._lay()
        self.move_to(ORIGIN)

    @property
    def count(self):
        return len(self._planned)

    def cell(self, row, column):
        """The text of one value, for pointing at."""
        return VGroup(*self._find(row).cells[self._column(column)][1:])

    # ---- changing it

    def draw(self, run_time=None):
        """The entrance: the rule is drawn under the column names, and the rows fade in from
        the top down. Returns the animation."""
        rows = list(self.body)

        def start():
            self._head = 0.0
            for row in rows:
                row.shown = 0.0

        def step(u):
            self._head = _ease(u / 0.5)
            for i, row in enumerate(rows):
                row.shown = _ease((u - 0.2 - 0.07 * i) / 0.35)

        return _Change(self, max(0.5, 0.55 + 0.07 * (len(rows) - 1)), step, start, run_time=run_time)

    def insert_row(self, values, at=None, hold=0.8, color=GREEN, run_time=None):
        """A new row opens, at the bottom or at position `at`, with its bar lit for `hold`
        seconds (None leaves it lit until `unmark`). Returns the animation."""
        self._tidy()
        row = self._row(values)
        row.open, row.color = 0.0, ManimColor(color)
        if at is None or at >= len(self._planned):
            self._planned.append(row)
            self.body.add(row)
        else:
            self.body.insert(self.body.submobjects.index(self._planned[at]), row)
            self._planned.insert(at, row)
        self._lay()

        def step(u):
            row.open = _ease(u / OPEN)
            row.lit = row.open * (1 if hold is None else 1 - _ease((u - OPEN - hold) / FADE))

        return _Change(self, OPEN + (0 if hold is None else hold + FADE), step, rows=[row], run_time=run_time)

    def update_row(self, row, changes=None, hold=0.8, color=BLUE, run_time=None, **named):
        """Change values in a row: `update_row("1002", status="shipped")`, or with a dictionary
        for column names that are not words. The row's bar is lit while each old value
        slides up and out and the new one comes up into its place. Returns the animation."""
        self._tidy()
        row = self._find(row)
        swaps = []
        for name, value in {**(changes or {}), **named}.items():
            j = self._column(name)
            new = self._cell(self._cols[j], value)
            new.shown, new.rise = 0.0, -SLIDE
            swaps.append((row.cells[j], new))
            row.cells[j], row.values[j] = new, str(value)
            row.text.add(new)
        self._lay()
        was = {}

        def step(u):
            self._glow(row, color, u, was, None if hold is None else LIGHT + SWAP + hold)
            k = _ease((u - 0.25) / SWAP)
            for old, new in swaps:
                old.shown, old.rise = 1 - k, SLIDE * k
                new.shown, new.rise = k, -SLIDE * (1 - k)

        seconds = LIGHT + SWAP + (0 if hold is None else hold + FADE)
        return _Change(self, seconds, step, lambda: was.update(lit=row.lit, color=row.color), [row], run_time)

    def delete_row(self, row, hold=0.6, color=RED, run_time=None):
        """A row's bar is lit and its text dims; `hold` seconds later it closes up. Returns
        the animation."""
        self._tidy()
        row = self._find(row)
        self._planned.remove(row)
        row.gone = True
        was = {}

        def step(u):
            self._glow(row, color, u, was)
            row.fade = _ease(u / LIGHT)
            row.open = 1 - _ease((u - LIGHT - hold) / OPEN)

        return _Change(self, LIGHT + hold + OPEN, step, lambda: was.update(lit=row.lit, color=row.color), [row], run_time)

    def mark(self, row, color=BLUE, run_time=None):
        """Light a row's bar without changing the row: the one being read, say. It stays lit
        until `unmark`. Returns the animation."""
        row, was = self._find(row), {}
        return _Change(self, LIGHT, lambda u: self._glow(row, color, u, was),
                       lambda: was.update(lit=row.lit, color=row.color), [row], run_time)

    def unmark(self, row=None, run_time=None):
        """Put out a row's bar, or every bar that is lit. Returns the animation."""
        rows = list(self._planned) if row is None else [self._find(row)]
        was = {}

        def step(u):
            for i, r in enumerate(rows):
                r.lit = was[i] * (1 - _ease(u / FADE))

        return _Change(self, FADE, step, lambda: was.update({i: r.lit for i, r in enumerate(rows)}), rows, run_time)

    def scale(self, factor, **kwargs):
        super().scale(factor, **kwargs)
        return self._lay() if hasattr(self, "_anchor") else self     # the lines thicken with it

    # ---- drawing it

    @staticmethod
    def _glow(row, color, u, was, off=None):
        """Bring a row's bar up in `color` from however it was lit, and put it out again
        from `off` seconds if that is given."""
        k = _ease(u / LIGHT)
        lit = was.get("lit", 0.0)
        row.color = _mix(was["color"], color, k) if lit > 0.01 else ManimColor(color)
        row.lit = (lit + (1 - lit) * k) * (1 if off is None else 1 - _ease((u - off) / FADE))

    def _size(self):
        """How much the table has been scaled since it was made."""
        if not hasattr(self, "_anchor"):
            return 1.0
        return float(self._anchor.points[-1][0] - self._anchor.points[0][0]) / self._width

    def _column(self, name):
        names = [c.name for c in self._cols]
        if name not in names:
            raise ValueError(f"no column {name!r}: the columns are {', '.join(names)}")
        return names.index(name)

    def _find(self, row):
        if isinstance(row, (int, np.integer)) and not isinstance(row, bool):
            if not -len(self._planned) <= row < len(self._planned):
                raise IndexError(f"no row {row}: the table has {len(self._planned)} rows")
            return self._planned[row]
        if self._key is None:
            raise ValueError("this table has no key column: ask for a row by its position")
        j = self._cols.index(self._key)
        for r in self._planned:
            if r.values[j] == str(row):
                return r
        raise ValueError(f"no row whose {self._key.name} is {row!r}: there are {', '.join(r.values[j] for r in self._planned)}")

    def _cell(self, col, value):
        cell = _word(str(value), (FONT - 0.75 if col.mono else FONT) * self._size(), MONO if col.mono else SANS, right=col.right)
        cell.col, cell.shown, cell.rise = col, 1.0, 0.0
        return cell

    def _row(self, values):
        values = list(values)
        if len(values) != len(self._cols):
            raise ValueError(f"a row needs {len(self._cols)} values ({', '.join(c.name for c in self._cols)}), not {len(values)}")
        row = VGroup()
        row.rule = VMobject().set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
        row.bar = RoundedRectangle(corner_radius=0.004, width=0.01, height=0.01, stroke_width=0, fill_opacity=0)
        row.cells = [self._cell(col, v) for col, v in zip(self._cols, values)]
        row.text = VGroup(*row.cells)
        row.add(row.rule, row.bar, row.text)
        row.values = [str(v) for v in values]
        # how open the row is, how far it has faded in, how lit its bar is and in what
        # color, how far its text has dimmed, and whether it is on its way out
        row.open, row.shown, row.lit, row.color, row.fade, row.gone, row.busy = 1.0, 1.0, 0.0, ManimColor(BLUE), 0.0, False, 0
        return row

    def _tidy(self):
        """Forget rows that have closed and values that have been replaced."""
        for row in list(self.body):
            if row.busy:
                continue
            if row.gone and row.open < 0.01:
                self.body.remove(row)
            for cell in list(row.text):
                if cell.shown < 0.01 and not any(cell is c for c in row.cells):
                    row.text.remove(cell)

    def _lay(self):
        """Put the header, the rule and every row where the state says."""
        a, b = self._anchor.points[0], self._anchor.points[-1]
        left, right, y = float(a[0]), float(b[0]), float(a[1])
        s = (right - left) / self._width
        for word, col in zip(self.header, self._cols):
            word.shift(np.array([left + col.x * s, y + PITCH * s / 2, 0]) - word.anchor.points[0])
            for letter in word[1:]:
                letter.set_fill(MUTED, self._head)
        self.rule.set_points_as_corners([[left, y, 0], [left + (right - left) * max(self._head, 1e-3), y, 0]])
        self.rule.set_stroke(LINE, 2.5 * s, float(np.clip(self._head * 8, 0, 1)))
        first = True
        for row in self.body:
            h = row.open * PITCH * s
            middle, here = y - h / 2, row.open * row.shown
            # a hairline over every row but the first
            row.rule.set_points_as_corners([[left, y, 0], [right, y, 0]]).set_stroke(LINE, 1.2 * s, 0 if first else 0.7 * here)
            tall = max((PITCH - 0.14) * s * row.open, 0.01 * s)
            row.bar.set_points(_rounded(0.1 * s, tall, min(0.05 * s, 0.49 * tall)) + [left - 0.18 * s, middle, 0])
            row.bar.set_fill(row.color, row.lit * row.shown * float(np.clip(row.open * 4, 0, 1)))
            for cell in row.text:
                cell.shift(np.array([left + cell.col.x * s, middle + cell.rise * PITCH * s, 0]) - cell.anchor.points[0])
                ink = _mix(MUTED if cell.col is self._key else INK, MUTED, 0.5 * row.fade)
                for letter in cell[1:]:
                    letter.set_fill(ink, cell.shown * here)
            if row.open > 0.02:
                first = False
            y -= h
        return self

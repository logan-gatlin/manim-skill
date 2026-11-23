"""A terminal: commands typed at a prompt, and their output arriving line by line.

Copy this file and the skill's code_font.py next to scene.py:

    from terminal import Terminal, fail, ok

    term = Terminal()
    self.play(FadeIn(term))
    self.play(term.type("npm run build"))                 # typed a character at a time
    self.play(term.output("vite v5.4 building for production",
                          ok("142 modules transformed"),  # a green tick, then the text
                          ok("built in 1.31s")))          # ...and the prompt comes back
    self.play(term.run("npm test", ok("auth.test.js (12)"), fail("cart.test.js (1 failed)")))

The line being typed has a band behind it, and the cursor blinks while nothing is
happening. See README.md.
"""

import numpy as np
from manim import TAU, Animation, CapStyleType, RoundedRectangle, Succession, Text, VGroup, VMobject, Wait, linear

from code_font import MONO

PANEL = "#141821"
TRACK = "#1c2130"
INK = "#eef1f6"
MUTED = "#8a93a6"
GREEN, RED = "#4ade80", "#f87171"

TYPE = 0.065      # seconds a typed character
ARRIVE = 0.16     # seconds a line of output takes to fade in


def ok(text):
    """A line of output that reports success: a green tick, then the text."""
    return [("✓", GREEN), (" " + text, MUTED)]


def fail(text):
    """A line of output that reports failure: a red cross and red text."""
    return [("✗", RED), (" " + text, RED)]


def _ease(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


class _Change(Animation):
    """Runs a terminal's state through a function of the seconds elapsed."""

    def __init__(self, terminal, seconds, step, run_time):
        self.seconds, self.step = seconds, step
        super().__init__(terminal, run_time=run_time or seconds, rate_func=linear)

    def interpolate_mobject(self, alpha):
        self.step(alpha * self.seconds)
        self.mobject._idle = 0.0
        self.mobject._lay()


class Terminal(VGroup):
    """A panel of text in the code font, with a prompt on its first line.

    width    the panel's width. Lines are not wrapped: keep them shorter than this.
    lines    how many lines it holds. When more arrive, the text scrolls up.
    prompt   what a command line begins with.
    size     scales the text and spacing. Don't `scale` the terminal.

    `terminal.panel`, `terminal.band`, `terminal.cursor` and `terminal.text` are its parts.
    """

    def __init__(self, width=7.0, lines=8, prompt="❯", size=1.0, **kwargs):
        super().__init__(**kwargs)
        self.capacity, self.prompt, s = lines, prompt, size
        self._font = 18 * s
        pair = Text("00", font=MONO, font_size=self._font)
        self._advance = pair[1].get_center()[0] - pair[0].get_center()[0]
        self._pitch, self._pad = 0.4 * s, (0.36 * s, 0.34 * s)
        height = lines * self._pitch + 2 * self._pad[1] - 0.12 * s
        self.panel = RoundedRectangle(corner_radius=0.14 * s, width=width, height=height, stroke_width=0,
                                      fill_color=PANEL, fill_opacity=1)
        self.band = RoundedRectangle(corner_radius=0.07 * s, width=width - 0.28 * s, height=self._pitch, stroke_width=0,
                                     fill_color=TRACK, fill_opacity=1)
        self.cursor = VMobject().set_stroke(INK, 2.6 * s).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
        self.cursor.set_points_as_corners([[0, 0.14 * s, 0], [0, -0.14 * s, 0]])
        self.text = VGroup()
        self.add(self.panel, self.band, self.text, self.cursor)
        # The state everything is drawn from: how many lines are in (the last one may be
        # part-way in), which of them is the prompt, how much of its command is typed, and
        # whether a command is running (when there is no band or cursor).
        self._lines, self._count, self._current, self._typed, self._busy, self._idle = [], 0.0, 0, 0, 0.0, 0.0
        self._new_line([(prompt + " ", GREEN)], is_prompt=True)
        self._count = 1.0
        # ...and the same after every move made so far, so that moves can be made ahead of
        # being played
        self._planned = (1, 0)                       # (count, current)
        self._lay()
        self.add_updater(Terminal._blink)

    # ---- using it

    def type(self, command, run_time=None):
        """Type a command at the prompt, a character at a time. Returns the animation."""
        self._tidy()
        index = self._planned[1]
        line = self._lines[index]
        glyphs = self._row([(" " * (len(self.prompt) + 1) + command, INK)])[0].shift(line.anchor.points[0])
        line.add(glyphs)
        line.command, line.typed_glyphs = command, glyphs
        for g in glyphs:
            g.set_opacity(0)
        self._lay()

        def step(u):
            self._current, self._typed = index, int(np.clip(u / TYPE, 0, len(command)))

        return _Change(self, len(command) * TYPE + 0.05, step, run_time)

    def output(self, *lines, gap=0.5, prompt=True, run_time=None):
        """The command's output: each line fades in `gap` seconds after the one before, and
        then the prompt comes back. A line is a string, or a list of (text, color) parts;
        `ok(text)` and `fail(text)` make the usual two kinds. Returns the animation."""
        self._tidy()
        first = len(self._lines)
        for parts in lines:
            self._new_line([(parts, MUTED)] if isinstance(parts, str) else parts)
        if prompt:
            self._new_line([(self.prompt + " ", GREEN)], is_prompt=True)
        added, (base, was) = len(self._lines) - first, self._planned
        self._planned = (base + added, first + added - 1 if prompt else was)
        self._lay()

        def step(u):
            self._busy = _ease(u / 0.15) if not prompt else _ease(u / 0.15) * (1 - _ease((u - (added - 1) * gap - 0.3) / 0.15))
            self._count = base + sum(_ease((u - (k + 0.6) * gap) / ARRIVE) for k in range(added))
            if prompt and u >= (added - 0.4) * gap:
                self._current, self._typed = first + added - 1, 0
            else:
                self._current, self._typed = was, len(self._lines[was].command)

        return _Change(self, (added + 0.6) * gap + ARRIVE, step, run_time)

    def run(self, command, *lines, gap=0.5, pause=0.3):
        """Type a command, pause as if pressing Enter, and show its output. Returns the
        animation."""
        return Succession(self.type(command), Wait(pause), self.output(*lines, gap=gap))

    # ---- drawing it

    def _row(self, parts):
        """A line of text from (text, color) parts, each starting at the column the ones
        before it end on. Built with a capital and a descender in front, so every line sits
        on the same baseline and grid."""
        row, col = VGroup(), 0
        for text, color in parts:
            if text.strip():
                t = Text("Hg" + " " * col + text.rstrip(), font=MONO, font_size=self._font, color=color)
                t.shift([-t[0].get_left()[0] - 2 * self._advance, -t[:2].get_center()[1], 0])
                row.add(VGroup(*t[2:]))
            col += len(text)
        return row

    def _new_line(self, parts, is_prompt=False):
        line = self._row(parts)
        line.is_prompt, line.command, line.typed_glyphs = is_prompt, "", VGroup()
        # An invisible point at the start of the line: it moves with the line however the
        # terminal is moved, so the line can always be put back on its row.
        line.anchor = VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([[0, 0, 0], [0, 0, 0]])
        line.add_to_back(line.anchor)
        self._lines.append(line)
        self.text.add(line)
        return line

    def _tidy(self):
        """Forget lines that have scrolled out of the top, unless moves are still waiting
        to be played."""
        if abs(self._count - self._planned[0]) > 1e-6:
            return
        over = int(np.floor(max(0.0, self._count - self.capacity)))
        for line in self._lines[:over]:
            self.text.remove(line)
        self._lines = self._lines[over:]
        self._count -= over
        self._current -= over
        self._planned = (self._planned[0] - over, self._planned[1] - over)

    def _lay(self):
        """Put every line, the band and the cursor where the state says."""
        left = self.panel.get_left()[0] + self._pad[0]
        top = self.panel.get_top()[1] - self._pad[1] - self._pitch / 2 + 0.06
        scrolled = max(0.0, self._count - self.capacity)
        for i, line in enumerate(self._lines):
            row = i - scrolled
            shown = float(np.clip(self._count - i, 0, 1)) * float(np.clip(row + 1, 0, 1))
            spot = np.array([left, top - row * self._pitch - 0.05 * (1 - float(np.clip(self._count - i, 0, 1))), 0])
            line.shift(spot - line.anchor.points[0])
            for part in line[1:]:
                part.set_opacity(shown)
            if line.is_prompt and len(line.typed_glyphs):
                typed = self._typed if i == self._current else len(line.command)
                visible = len(line.command[:typed].replace(" ", ""))
                for k, glyph in enumerate(line.typed_glyphs):
                    glyph.set_opacity(shown if k < visible else 0)
        # the band and the cursor belong to the prompt, when no command is running
        row = self._current - scrolled
        here = float(np.clip(self._count - self._current, 0, 1)) * (1 - self._busy)
        y = top - row * self._pitch
        self.band.move_to([self.panel.get_center()[0], y, 0]).set_fill(opacity=here)
        self.cursor.move_to([left + (len(self.prompt) + 1 + self._typed) * self._advance + 0.02, y, 0])
        blink = 1.0 if self._idle < 0.3 else 0.5 + 0.5 * np.cos(TAU * (self._idle - 0.3) / 1.1)
        self.cursor.set_stroke(opacity=here * blink)
        return self

    def _blink(self, dt):
        self._idle += dt
        self._lay()

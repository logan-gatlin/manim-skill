"""A browser window to put an interface inside: a panel with three dots and an address, and a
screen area below for whatever the scene builds.

Copy this file and the skill's code_font.py next to scene.py:

    from browser import Browser

    b = Browser("shop.example")
    self.play(b.draw())                          # the window fades in, rising
    self.play(b.show(shop))                      # a mobject is fitted to the screen and fades in
    self.play(b.go("shop.example/cart", cart))   # the address changes, a bar runs across
                                                 # under the toolbar and the page is swapped

`b.screen` is the area a page may fill; build pages to its width and height. See README.md.
"""

import numpy as np
from manim import (LEFT, ORIGIN, UL, UP, Animation, AnimationGroup, CapStyleType, Dot, FadeIn, FadeOut, ManimColor, Rectangle,
                   RoundedRectangle, Succession, Text, VGroup, VMobject, Wait, interpolate_color, linear)

from code_font import MONO

BG = "#0d1118"
PANEL = "#141821"
LINE = "#3a4252"
MUTED = "#8a93a6"
BLUE = "#60a5fa"

BAR = 0.62        # the toolbar's height
PAD = 0.42        # the space between the window's edge and the screen
FONT = 15         # the size of the address
RISE = 0.12       # how far the window rises as it arrives
SWAP = 0.4        # seconds the address takes to change


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


class _Change(Animation):
    """Runs a browser's state through a function of the seconds elapsed."""

    def __init__(self, browser, seconds, step, run_time=None, words=()):
        self.seconds, self.step, self.words = seconds, step, words
        for word in words:
            word.busy += 1                       # it has a change still to make
        super().__init__(browser, run_time=run_time or seconds, rate_func=linear)

    def finish(self):
        super().finish()
        for word in self.words:
            word.busy -= 1
        self.words = ()

    def create_starting_mobject(self):
        return VGroup()         # Manim would copy the whole browser here, and never use the copy

    def interpolate_mobject(self, alpha):
        self.step(alpha * self.seconds)
        self.mobject._lay()


class Browser(VGroup):
    """A browser window.

    address   what the address bar says to begin with.
    width     the window's width, and `height` its height.
    dots      False leaves out the three dots.
    align     where a page smaller than the screen is put: UL, the top left corner, as a
              web page is; UP centres it against the top, ORIGIN in the middle.

    `browser.screen` is an invisible rectangle over the area for a page, `browser.content`
    the page being shown, and `browser.panel`, `browser.dots`, `browser.pill` and
    `browser.address` the window's parts.
    """

    def __init__(self, address="", width=8.0, height=4.8, dots=True, align=UL, **kwargs):
        super().__init__(**kwargs)
        self._size0, self.align = (width, height), align
        self.content = None
        self._shown = 1.0                            # how far the window has arrived
        self._run, self._glow = 0.0, 0.0             # the loading bar: how far across, and how bright
        # An invisible rectangle the size of the window. It moves and grows with the
        # browser, so everything can be laid out from it wherever the browser has been put.
        self._frame = Rectangle(width=width, height=height, stroke_width=0, fill_opacity=0)
        self.panel = RoundedRectangle(corner_radius=0.22, width=width, height=height, stroke_width=0, fill_color=PANEL, fill_opacity=1)
        self.dots = VGroup(*[Dot(radius=0.06, color=interpolate_color(ManimColor(LINE), ManimColor(MUTED), 0.4))
                             for _ in range(3 if dots else 0)])
        self.pill = RoundedRectangle(corner_radius=0.19, width=1, height=0.38, stroke_width=0, fill_color=BG, fill_opacity=1)
        self.address = VGroup()
        self.loading = VMobject().set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)
        self.screen = Rectangle(width=width - 2 * PAD, height=height - BAR - 0.3 - PAD, stroke_width=0, fill_opacity=0)
        self.add(self._frame, self.panel, self.dots, self.pill, self.address, self.loading, self.screen)
        self._current = self._word(address)
        self._lay()

    # ---- using it

    def draw(self, run_time=None):
        """The entrance: the window fades in, rising a little. Returns the animation."""

        def step(u):
            self._shown = _ease(u / 0.6)

        return _Change(self, 0.6, step, run_time)

    def place(self, content):
        """Fit a mobject to the screen: shrunk if it is too big, and put at `align`."""
        s = min(1.0, self.screen.width / max(content.width, 1e-6), self.screen.height / max(content.height, 1e-6))
        if s < 1:
            content.scale(s)
        content.move_to(self.screen.get_critical_point(self.align), aligned_edge=self.align)
        return content

    def show(self, content, run_time=None):
        """Put a page on the screen: it is fitted with `place` and fades in, rising, and
        any page already there fades out first. Returns the animation."""
        old, self.content = self.content, self.place(content)
        arrive = FadeIn(content, shift=UP * 0.12, run_time=0.5)
        move = arrive if old is None else Succession(FadeOut(old, run_time=0.3), arrive)
        return move if run_time is None else move.set_run_time(run_time)

    def go(self, address, content=None, run_time=None):
        """Go to another address: the old address slides up and out as the new one comes
        in, and a bar runs across under the toolbar. With `content`, the page on the screen
        fades out and the new one comes in from the right. Returns the animation."""
        for word in list(self.address):                  # forget addresses that have gone, but not
            if word is not self._current and word.shown < 0.01 and not word.busy:      # one still to come
                self.address.remove(word)
        old_word, new_word = self._current, self._word(address)
        new_word.shown, new_word.rise = 0.0, -1.0
        self._current = new_word
        self._lay()

        def step(u):
            k = _ease(u / SWAP)
            old_word.shown, old_word.rise = 1 - k, k
            new_word.shown, new_word.rise = k, -(1 - k)
            self._run = _ease(u / 0.55)
            self._glow = _ease(u / 0.1) * (1 - _ease((u - 0.5) / 0.25))

        chrome = _Change(self, 0.8, step, words=(old_word, new_word))
        if content is None:
            return chrome if run_time is None else chrome.set_run_time(run_time)
        old, self.content = self.content, self.place(content)
        leave = Wait(0.35) if old is None else Succession(Wait(0.05), FadeOut(old, run_time=0.3))
        move = AnimationGroup(chrome, Succession(leave, FadeIn(content, shift=LEFT * 0.15, run_time=0.45)))
        return move if run_time is None else move.set_run_time(run_time)

    def scale(self, factor, **kwargs):
        super().scale(factor, **kwargs)
        return self._lay() if hasattr(self, "screen") else self      # the loading bar thickens with it

    # ---- drawing it

    def _scale(self):
        """How much the browser has been scaled since it was made."""
        return self._frame.width / self._size0[0]

    def _word(self, text):
        """An address, behind an invisible point at its middle."""
        t = Text("Hg" + text, font=MONO, font_size=FONT * self._scale())
        letters = VGroup(*t[2:])
        letters.shift([-letters.get_center()[0] if len(letters) else 0, -t[:2].get_center()[1], 0])
        word = VGroup(VMobject(stroke_width=0, fill_opacity=0).set_points_as_corners([ORIGIN, ORIGIN]), *letters)
        word.anchor, word.shown, word.rise, word.busy = word[0], 1.0, 0.0, 0
        word.span = letters.width / self._scale() if len(letters) else 0.0
        self.address.add(word)
        return word

    def _lay(self):
        """Put the window's parts where the state says."""
        s, o = self._scale(), self._shown
        wide, tall = self._size0[0] * s, self._size0[1] * s
        middle = self._frame.get_center() + np.array([0, -RISE * s * (1 - o), 0])
        left, top = middle[0] - wide / 2, middle[1] + tall / 2
        row = top - BAR * s / 2
        self.panel.move_to(middle).set_fill(opacity=o)
        for k, dot in enumerate(self.dots):
            dot.move_to([left + (0.38 + 0.21 * k) * s, row, 0]).set_fill(opacity=o)
        # the pill is as wide as the longest address on it needs
        need = max([w.span for w in self.address if w.shown > 0.01] + [0.0]) + 0.7
        self.pill.set_points(_rounded(max(0.58 * self._size0[0], need) * s, 0.38 * s, 0.19 * s) + [middle[0], row, 0])
        self.pill.set_fill(opacity=o)
        for word in self.address:
            word.shift(np.array([middle[0], row + 0.1 * s * word.rise, 0]) - word.anchor.points[0])
            for letter in word[1:]:
                letter.set_fill(MUTED, word.shown * o)
        y, a, b = top - BAR * s, left + 0.24 * s, left + wide - 0.24 * s
        self.loading.set_points_as_corners([[a, y, 0], [a + (b - a) * max(self._run, 0.02), y, 0]])
        self.loading.set_stroke(BLUE, 3 * s, self._glow * o)
        self.screen.move_to([middle[0], (top - (BAR + 0.3) * s + middle[1] - tall / 2 + PAD * s) / 2, 0])
        return self

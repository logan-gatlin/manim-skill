"""Renders the images in images/ and a demo video. From this directory:

    manim render -s -r 1600,560 --media_dir /tmp/manim/progress-examples examples.py Ring
    (see README.md for the full list of commands)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # icons.py, at the skill root

from manim import *

from progress import grid_fill, liquid, phases, ring, stepper

STATES = (0.3, 0.62, 1.0)


class Example(MovingCameraScene):
    """Three states of one component, framed tightly."""

    direction = RIGHT
    buff = 1.2

    def make(self, tracker):
        raise NotImplementedError

    def construct(self):
        items = VGroup()
        for p in STATES:
            items.add(self.make(ValueTracker(p)))
        items.arrange(self.direction, buff=self.buff)
        self.add(items)
        frame = self.camera.frame
        aspect = config.pixel_width / config.pixel_height
        frame.set(width=max(items.width + 1.0, (items.height + 0.9) * aspect))
        frame.move_to(items)


class Ring(Example):
    def make(self, t):
        return ring(t)


class GridFill(Example):
    def make(self, t):
        return grid_fill(t)


class GridFillWide(Example):
    def construct(self):
        item = grid_fill(ValueTracker(0.62), rows=5, cols=18)
        self.add(item)
        aspect = config.pixel_width / config.pixel_height
        self.camera.frame.set(width=max(item.width + 1.0, (item.height + 0.9) * aspect)).move_to(item)


class Liquid(Example):
    direction, buff = DOWN, 0.7

    def make(self, t):
        return liquid(t, width=6)


class Stepper(Example):
    direction, buff = DOWN, 0.8

    def make(self, t):
        return stepper(t, width=6)


class Phases(Example):
    direction, buff = DOWN, 0.8

    def make(self, t):
        return phases(t, width=6)


def stalls(t):
    keys = [(0, 0), (0.22, 0.34), (0.36, 0.4), (0.62, 0.74), (0.74, 0.8), (1, 1)]
    for (a, pa), (b, pb) in zip(keys, keys[1:]):
        if t <= b:
            return pa + (pb - pa) * smooth((t - a) / (b - a))
    return 1.0


class Demo(Scene):
    """All of them filling, finishing one after another so each completion effect shows."""

    def construct(self):
        ps = [ValueTracker(0) for _ in range(6)]
        left = [liquid(ps[0], width=5.6), phases(ps[1], width=5.6), stepper(ps[2], width=5.6)]
        for m, y in zip(left, (2.4, 0.1, -2.3)):
            m.move_to([-3.3, y, 0])
        rg = ring(ps[3]).move_to([2.2, 1.9, 0])
        gr = grid_fill(ps[4], rows=8, cols=8).move_to([4.6, 1.9, 0])
        wide = grid_fill(ps[5], rows=4, cols=16).move_to([3.4, -1.8, 0])
        self.add(*left, rg, gr, wide)
        order = [0, 3, 1, 4, 2, 5]
        self.play(LaggedStart(*[ps[i].animate(rate_func=stalls).set_value(1) for i in order],
                              lag_ratio=0.15, run_time=10))
        self.wait(1.5)

"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from log import log

STEPS = [("lint", 4), ("build", 21), ("test", 38), ("deploy", 9)]


class Demo(MovingCameraScene):
    def construct(self):
        done = ValueTracker(0)
        steps = log(done, STEPS)
        self.add(steps)
        self.camera.frame.set(width=8).move_to(steps)
        self.wait(0.5)
        self.play(done.animate.set_value(1), run_time=9, rate_func=linear)
        self.wait(1.5)


class Still(MovingCameraScene):
    def construct(self):
        steps = log(ValueTracker(0.6), STEPS)
        steps.update(dt=1.3)
        self.add(steps)
        self.camera.frame.set(width=7).move_to(steps)

"""Renders the image in images/ and a demo video; see README.md for the commands."""

from manim import *

from funnel import funnel

STAGES = [("Visit", 0.6), ("Sign up", 0.5), ("Activate", 0.6), ("Pay", 1.0)]


class Demo(Scene):
    """The funnel running."""

    def construct(self):
        self.add(funnel(STAGES, width=9.5, height=2.4, dot=0.075, label_size=20, rate=11, speed=1.25))
        self.wait(12)


class Still(MovingCameraScene):
    def construct(self):
        f = funnel(STAGES)
        self.add(f)
        self.camera.frame.set(width=7.4).move_to(f)

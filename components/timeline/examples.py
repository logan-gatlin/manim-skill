"""Renders the images in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from timeline import timeline

MUTED = "#8a93a6"

EXAMPLES = [
    ("One after another", [("Lint", (0, 4)), ("Build", (4, 25)), ("Test", (25, 63)), ("Deploy", (63, 72))]),
    ("Overlapping", [("Lint", (0, 14)), ("Build", (6, 34)), ("Test", (20, 58)), ("Deploy", (50, 72))]),
    ("Stopping and starting again", [("Lint", [(0, 6), (30, 36)]), ("Build", [(6, 22), (36, 50)]),
                                     ("Test", [(22, 30), (50, 64)]), ("Deploy", (64, 72))]),
]


def charts(now):
    out = Group()
    for i, (title, rows) in enumerate(EXAMPLES):
        chart = timeline(now, rows, width=6.2).move_to([0.7, 2.35 - i * 2.35, 0])
        head = Text(title, font="Noto Sans", font_size=18, color=MUTED).move_to([-3.3, 3.25 - i * 2.35, 0], aligned_edge=LEFT)
        out.add(head, chart)
    return out


class Demo(Scene):
    def construct(self):
        now = ValueTracker(0)
        self.add(charts(now))
        self.wait(0.5)
        self.play(now.animate.set_value(72), run_time=9, rate_func=linear)
        self.wait(1.5)


class Still(Scene):
    def construct(self):
        self.add(charts(ValueTracker(45)))

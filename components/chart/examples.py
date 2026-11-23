"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from chart import chart
from code_font import MONO

config.background_color = "#0d1118"
MUTED = "#8a93a6"


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=22, color=MUTED).move_to(DOWN * 2.8)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        latency = ValueTracker(45)
        c = chart(latency, limit=100, unit=" ms", width=8, height=2.6).shift(LEFT * 0.6 + UP * 0.3)
        self.say('c = chart(latency, limit=100, unit=" ms")')
        self.add(c)
        self.wait(2.5)
        self.say("latency.animate.set_value(130)")
        self.play(latency.animate.set_value(130), run_time=1.2)
        self.wait(2.5)
        self.say("latency.animate.set_value(60)")
        self.play(latency.animate.set_value(60), run_time=1.5)
        self.wait(4)


class Still(Scene):
    def construct(self):
        spike = lambda t: 45 + 80 * smooth(np.clip((t + 2.3) / 1.0, 0, 1))      # it has been over the limit for a second
        c = chart(spike, limit=100, unit=" ms", width=8.5, height=2.6)
        self.add(c.shift(LEFT * 0.7))

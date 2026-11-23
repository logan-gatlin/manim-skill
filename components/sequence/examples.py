"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from code_font import MONO
from sequence import Sequence

config.background_color = "#0d1118"
MUTED = "#8a93a6"

STEPS = [('seq.send("Web", "API", "GET /cart")', lambda s: s.send("Web", "API", "GET /cart")),
         ('seq.send("API", "API", "check session")', lambda s: s.send("API", "API", "check session")),
         ('seq.send("API", "DB", "SELECT")', lambda s: s.send("API", "DB", "SELECT")),
         ('seq.reply("DB", "API", "rows")', lambda s: s.reply("DB", "API", "rows")),
         ('seq.reply("API", "Web", "200")', lambda s: s.reply("API", "Web", "200")),
         ('seq.send("Web", "API", "POST /pay")', lambda s: s.skip(0.5).send("Web", "API", "POST /pay")),
         ('seq.send("API", "DB", "INSERT", lost=True)', lambda s: s.send("API", "DB", "INSERT", lost=True)),
         ('seq.reply("API", "Web", "504", error=True)', lambda s: s.reply("API", "Web", "504", error=True))]


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=20, color=MUTED).move_to(DOWN * 3.5)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        seq = Sequence("Web", "API", "DB", row=0.62).move_to(UP * 3.55, aligned_edge=UP)
        self.say('seq = Sequence("Web", "API", "DB")   seq.draw()')
        self.play(seq.draw())
        self.wait(0.6)
        for call, step in STEPS:
            self.say(call)
            self.play(step(seq))
            self.wait(0.5)
        self.wait(1.5)


class Still(Scene):
    def construct(self):
        seq = Sequence("Web", "API", "DB")
        for _, step in STEPS:
            move = step(seq)
            move.begin()
            move.interpolate(1)
        self.add(seq.move_to(ORIGIN))

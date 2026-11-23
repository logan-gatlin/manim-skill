"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from code_font import MONO
from terminal import Terminal, fail, ok

config.background_color = "#0d1118"
MUTED = "#8a93a6"

BUILD = ["vite v5.4 building for production", ok("142 modules transformed"),
         [("dist/index.js", "#eef1f6"), ("   48.2 kB", MUTED)], ok("built in 1.31s")]
TEST = [ok("auth.test.js (12)"), fail("cart.test.js (1 failed)"), [("1 failed, 12 passed", "#f87171")]]


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=20, color=MUTED).move_to(DOWN * 3.3)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        term = Terminal(width=8.5, lines=9).shift(UP * 0.5)
        self.say("term = Terminal()")
        self.play(FadeIn(term), run_time=0.5)
        self.wait(1.5)
        self.say('term.type("npm run build")')
        self.play(term.type("npm run build"))
        self.wait(0.4)
        self.say("term.output(..., ok(...), ..., ok(...))")
        self.play(term.output(*BUILD))
        self.wait(1)
        self.say('term.run("npm test", ok(...), fail(...), ...)')
        self.play(term.run("npm test", *TEST))
        self.wait(1)
        self.say('term.run("git status", ...)     more lines than fit: the text scrolls')
        self.play(term.run("git status", "On branch main", "nothing to commit, working tree clean"))
        self.wait(2.5)


class Still(Scene):
    def construct(self):
        term = Terminal(width=8.5, lines=9)
        for move in (term.type("npm run build"), term.output(*BUILD), term.type("npm test"), term.output(*TEST)):
            move.begin()
            move.interpolate(1)
            move.finish()
        self.add(term)

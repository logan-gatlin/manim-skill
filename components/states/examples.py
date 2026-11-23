"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "components/line")]   # code_font.py; the line component

from manim import *

from code_font import MONO
from states import StateMachine

config.background_color = "#0d1118"
MUTED = "#8a93a6"

STATES = {"idle": (-3.4, 0.6), "loading": (0, 0.6), "done": (3.4, 0.6), "failed": (0, -1.5)}
MOVES = [("idle", "loading", "fetch"), ("loading", "done", "ok"), ("loading", "failed", "error"),
         ("failed", "loading", "retry"), ("done", "idle", "reset")]


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=22, color=MUTED).move_to(DOWN * 3.1)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        m = StateMachine(STATES, MOVES, bad=["failed"])
        self.say("m = StateMachine(states, transitions, bad=[\"failed\"])   m.draw()")
        self.play(m.draw())
        self.wait(0.8)
        for label in ("fetch", "error", "retry", "ok", "reset"):
            self.say(f'm.fire("{label}")')
            self.play(m.fire(label))
            self.wait(0.9)
        self.wait(1)


class Still(Scene):
    def construct(self):
        self.add(StateMachine(STATES, MOVES, start="loading", bad=["failed"]).move_to(ORIGIN))

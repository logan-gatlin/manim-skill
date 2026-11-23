"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from code_font import MONO
from fifo import Queue

config.background_color = "#0d1118"
MUTED = "#8a93a6"


def done(move):
    """Run an animation straight to its end."""
    move.begin()
    move.interpolate(1)
    move.finish()


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=22, color=MUTED).move_to(DOWN * 2.2)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        q = Queue(capacity=6).scale(2).move_to(RIGHT * 0.9)
        self.say("q = Queue(capacity=6)")
        self.play(FadeIn(q), run_time=0.5)
        self.wait(0.6)
        for call, move in [("q.push(4)", lambda: q.push(4)), ("q.pop()", lambda: q.pop()),
                           ("q.push(5)", lambda: q.push(5)), ("q.pop(2)", lambda: q.pop(2)),
                           ("q.pop(6)", lambda: q.pop(6))]:
            self.say(call)
            self.play(move())
            self.wait(0.9)
        self.play(FadeOut(q), run_time=0.4)

        endless = Queue(capacity=None).scale(2).move_to(RIGHT * 2.2)
        self.say("q = Queue(capacity=None)")
        self.play(FadeIn(endless), run_time=0.5)
        for call, move in [("q.push(3)", lambda: endless.push(3)), ("q.push(4)", lambda: endless.push(4)),
                           ("q.pop(5)", lambda: endless.pop(5))]:
            self.say(call)
            self.play(move())
            self.wait(0.9)
        self.wait(1)


class Still(Scene):
    def construct(self):
        shots = [("Part full", [("push", 3)]), ("Full, with two waiting", [("push", 8)]), ("No limit", [("push", 9)])]
        for i, (name, moves) in enumerate(shots):
            q = Queue(capacity=None if name == "No limit" else 6)
            for kind, n in moves:
                done(getattr(q, kind)(n))
            y = 1.5 - i * 1.5
            q.shift([2.2 - q.brackets[1].get_right()[0], y, 0])
            label = Text("Hg" + name, font="Noto Sans", font_size=20, color=MUTED)
            label.shift([0, y, 0] - label.get_center())
            self.add(q, VGroup(*label[2:]).shift([-5.6 - label[2].get_left()[0], 0, 0]))

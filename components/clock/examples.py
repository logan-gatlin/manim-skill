"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from clock import Clock
from code_font import MONO

config.background_color = "#0d1118"
MUTED = "#8a93a6"


class Demo(Scene):
    def say(self, call):
        """Show the call that the next move comes from, under the clock."""
        new = Text(call, font=MONO, font_size=22, color=MUTED).move_to(DOWN * 3.25)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        clock = Clock("09:15", radius=1.7, date="2026-11-28", weekday=True, zone="UTC").shift(UP * 0.55)
        self.add(clock)
        self.say('Clock("09:15", date="2026-11-28", weekday=True, zone="UTC")')
        self.wait(1)
        for call, move in [('clock.to("17:40")', lambda: clock.to("17:40")),
                           ("clock.back(hours=3)", lambda: clock.back(hours=3)),
                           ("clock.forward(minutes=3, run_time=2.5, rate_func=linear)",
                            lambda: clock.forward(minutes=3, run_time=2.5, rate_func=linear)),
                           ("clock.forward(hours=12)", lambda: clock.forward(hours=12)),
                           ('clock.to_zone("JST", hours=9)', lambda: clock.to_zone("JST", hours=9)),
                           ("clock.back(days=2, hours=5)", lambda: clock.back(days=2, hours=5))]:
            self.say(call)
            self.play(move())
            self.wait(1.2)

        ticking = Clock("23:59:54", radius=1.7, weekday="Sat", seconds=True, rate=1).shift(UP * 0.55)
        self.play(FadeOut(clock), run_time=0.4)
        self.say('Clock("23:59:54", weekday="Sat", seconds=True, rate=1)')
        self.play(FadeIn(ticking), run_time=0.4)
        self.wait(8)
        self.say("clock.back(minutes=30)")
        self.play(ticking.back(minutes=30))
        self.wait(2.5)


def caught(clock, move, at, fps=60):
    """`clock` as it looks `at` of the way through `move`, by stepping it frame by frame."""
    move.begin()
    for k in range(1, int(move.run_time * at * fps) + 1):
        move.interpolate(k / (move.run_time * fps))
        clock.update(dt=1 / fps)
    clock.clear_updaters()
    return clock


class Still(Scene):
    def construct(self):
        rest = Clock("09:15", radius=1.25)
        forward = Clock("09:15", radius=1.25)
        caught(forward, forward.to("17:40"), 0.42)
        back = Clock("17:40", radius=1.25)
        caught(back, back.back(hours=3), 0.5)
        full = Clock("10:08:36", radius=1.25, date="2026-11-28", weekday=True, zone="UTC", seconds=True)
        clocks = [rest, forward, back, full]
        names = ["At rest", "Turning forwards", "Turning backwards", "With seconds and the date"]
        for i, (clock, name) in enumerate(zip(clocks, names)):
            clock.move_to(RIGHT * (i - 1.5) * 3.4).align_to(UP * 1.5, UP)
            label = Text("Hg" + name, font="Noto Sans", font_size=20, color=MUTED)   # measured with a capital and a
            label.shift(UP * 2.0 - label.get_center())                                # descender, so the names line up
            self.add(clock, VGroup(*label[2:]).set_x(clock.get_x()))

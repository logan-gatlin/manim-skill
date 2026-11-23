"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from callout import Callout
from code_font import MONO

config.background_color = "#0d1118"
TRACK, MUTED, INK = "#1c2130", "#8a93a6", "#eef1f6"


def box(name, at):
    chip = RoundedRectangle(corner_radius=0.16, width=1.5, height=0.8, stroke_width=0, fill_color=TRACK, fill_opacity=1)
    return VGroup(chip, Text(name, font=MONO, font_size=22, color=INK)).move_to(at)


def diagram():
    api, db = box("api", LEFT * 2.2), box("db", RIGHT * 2.2)
    link = Arrow(api.get_right(), db.get_left(), buff=0.15, color=MUTED, stroke_width=4, max_tip_length_to_length_ratio=0.08)
    return api, db, link


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
        api, db, link = diagram()
        VGroup(api, db, link).scale(1.3).shift(UP * 0.3)
        self.add(api, db, link)
        made = []
        for call, note in [('Callout(api, "stateless")', lambda: Callout(api, "stateless", follow=True)),
                           ('Callout(link.get_center(), "TLS 1.3")', lambda: Callout(link.get_center(), "TLS 1.3")),
                           ('Callout(db, "primary", side=DOWN, turn=LEFT)', lambda: Callout(db, "primary", side=DOWN, turn=LEFT)),
                           ('Callout(db, "eu-west\\n3 replicas", side=RIGHT)', lambda: Callout(db, "eu-west\n3 replicas", side=RIGHT)),
                           ('Callout(db, "8 vCPU", turn=False)', lambda: Callout(db, "8 vCPU", turn=False))]:
            self.say(call)
            made.append(note())
            self.play(made[-1].draw())
            self.wait(0.7)
        self.say("note.erase()")
        self.play(*[note.erase() for note in made[1:]])
        self.wait(0.4)
        self.say('Callout(api, "stateless", follow=True)     it stays attached while api moves')
        self.play(FadeOut(link), run_time=0.3)
        self.play(api.animate.shift(RIGHT * 1.6 + DOWN * 1.2), run_time=1.2)
        self.play(api.animate.shift(LEFT * 1.6 + UP * 1.2), run_time=1.2)
        self.play(made[0].erase())
        self.wait(0.8)


class Still(Scene):
    def construct(self):
        api, db, link = diagram()
        self.add(VGroup(api, db, link).shift(LEFT * 0.4))
        self.add(Callout(api, "stateless"),
                 Callout(api, "2 instances", side=DOWN, turn=LEFT),
                 Callout(link.get_center(), "TLS 1.3", side=DOWN),
                 Callout(db, "8 vCPU", turn=False),
                 Callout(db, "eu-west\n3 replicas", side=RIGHT))

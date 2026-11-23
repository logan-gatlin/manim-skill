"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "components/line"), str(ROOT / "components/node")]

from manim import *

from code_font import MONO
from line import Connector
from node import Node
from packet import send

config.background_color = "#0d1118"
MUTED = "#8a93a6"
GREEN = "#4ade80"


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=22, color=MUTED).move_to(DOWN * 3.0)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        web = Node("Web", "client", icon="tabler/outline/browser", width=2.4).move_to(LEFT * 4.6 + DOWN * 0.9)
        api = Node("API", "gateway", icon="tabler/outline/server", width=2.4).move_to(UP * 0.3)
        db = Node("Postgres", "primary", icon="tabler/outline/database", width=2.4).move_to(RIGHT * 4.6 + UP * 1.4)
        cache = Node("Redis", "cache", icon="tabler/outline/bolt", width=2.4).move_to(RIGHT * 4.6 + DOWN * 0.8)
        link, fork = Connector(web, api), Connector(api, [db, cache])
        self.add(web, api, db, cache, link, fork)
        self.wait(0.5)
        for call, move in [("send(link)", lambda: send(link)),
                           ("send(link, count=6)", lambda: send(link, count=6)),
                           ("send(link, drop=True)", lambda: send(link, drop=True)),
                           ("send(link, count=8, drop=[2, 5])", lambda: send(link, count=8, drop=[2, 5])),
                           ("send(link, reverse=True, color=GREEN)", lambda: send(link, reverse=True, color=GREEN)),
                           ("send(fork, count=4)", lambda: send(fork, count=4)),
                           ("send(fork, branch=1, count=4, drop=[1])", lambda: send(fork, branch=1, count=4, drop=[1]))]:
            self.say(call)
            self.play(move())
            self.wait(0.6)

        # a request all the way through, and its reply
        self.say("a request, and its reply")
        self.play(send(link), web.to("active"))
        self.play(api.to("active"), run_time=0.3)
        self.play(send(fork, branch=0))
        self.play(db.to("active"), run_time=0.3)
        self.play(send(fork, branch=0, reverse=True, color=GREEN), db.to("inactive"))
        self.play(send(link, reverse=True, color=GREEN), api.to("inactive"))
        self.play(web.to("inactive"), run_time=0.3)
        self.wait(1)


def caught(move, at):
    """Stop the animation `move` part-way, `at` of the way through, leaving it drawn."""
    move.begin()
    move.interpolate(at)


class Still(Scene):
    def construct(self):
        shots = [("One packet", dict(), 0.52), ("A burst", dict(count=6), 0.55),
                 ("Dropped", dict(drop=True), 0.47), ("A burst that loses two", dict(count=7, drop=[1, 4]), 0.56)]
        for i, (name, options, at) in enumerate(shots):
            c = np.array([(i % 2 - 0.5) * 6.6, (0.5 - i // 2) * 2.5 - 0.15, 0])
            a = Node("Web", icon="tabler/outline/browser").move_to(c + LEFT * 2.2 + DOWN * 0.42)
            b = Node("API", icon="tabler/outline/server").move_to(c + RIGHT * 2.2 + UP * 0.22)
            link = Connector(a, b)
            caught(send(link, **options), at)
            label = Text("Hg" + name, font="Noto Sans", font_size=18, color=MUTED)
            label.shift(c + UP * 0.95 - label.get_center())
            self.add(a, b, link, VGroup(*label[2:]).set_x(c[0] - 2.2))

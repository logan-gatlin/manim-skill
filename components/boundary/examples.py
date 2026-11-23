"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "components/line"), str(ROOT / "components/node"), str(ROOT / "components/packet")]

from manim import *

from boundary import Boundary
from code_font import MONO
from line import Connector
from node import Node
from packet import send

config.background_color = "#0d1118"
MUTED = "#8a93a6"


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
        web = Node("Web", "client", icon="tabler/outline/browser", width=2.4).move_to(LEFT * 5.0)
        api = Node("API", "gateway", icon="tabler/outline/server", width=2.4).move_to(LEFT * 1.0 + UP * 0.9)
        worker = Node("Worker", "jobs", icon="tabler/outline/cpu", width=2.4).move_to(LEFT * 1.0 + DOWN * 0.9)
        db = Node("Postgres", "primary", icon="tabler/outline/database", width=2.4).move_to(RIGHT * 2.6 + UP * 0.9)
        cache = Node("Redis", "cache", icon="tabler/outline/bolt", width=2.4).move_to(RIGHT * 2.6 + DOWN * 0.9)
        self.play(LaggedStart(*[FadeIn(n, scale=0.9) for n in (web, api, worker)], lag_ratio=0.15), run_time=0.8)

        net = Boundary(api, worker, label="Private network")
        self.say('net = Boundary(api, worker, label="Private network")   net.draw()')
        self.play(net.draw())
        self.wait(1)
        self.say("net.include(db, cache)")
        self.play(net.include(db, cache), FadeIn(db, scale=0.9), FadeIn(cache, scale=0.9))
        self.wait(1)
        data = Boundary(db, cache, label="Data", pad=0.2)
        self.say('data = Boundary(db, cache, label="Data", pad=0.2)   net.include(data)')
        self.play(data.draw())
        self.play(net.include(data))
        self.wait(1)
        self.say("net.exclude(worker)")
        self.play(net.exclude(worker), worker.animate.shift(DOWN * 1.0 + LEFT * 3.2))
        self.wait(1)
        link = Connector(web, api)
        self.say("lines and packets cross it as usual")
        self.play(link.grow())
        self.play(send(link, count=5))
        self.wait(1.5)


class Still(Scene):
    def construct(self):
        web = Node("Web", "client", icon="tabler/outline/browser", width=2.4).move_to(LEFT * 5.0)
        api = Node("API", "gateway", icon="tabler/outline/server", width=2.4).move_to(LEFT * 1.2 + UP * 0.62)
        worker = Node("Worker", "jobs", icon="tabler/outline/cpu", width=2.4).move_to(LEFT * 1.2 + DOWN * 0.62)
        db = Node("Postgres", "primary", icon="tabler/outline/database", width=2.4).move_to(RIGHT * 2.3 + UP * 0.62)
        cache = Node("Redis", "cache", icon="tabler/outline/bolt", width=2.4).move_to(RIGHT * 2.3 + DOWN * 0.62)
        data = Boundary(db, cache, label="Data", pad=0.2)
        net = Boundary(api, worker, data, label="Private network")
        self.add(net, data, web, api, worker, db, cache, Connector(web, api), Connector(api, db))
        VGroup(*self.mobjects).move_to(ORIGIN)

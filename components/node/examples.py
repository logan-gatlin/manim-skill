"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "components/line")]   # icons.py and code_font.py; the line component

from manim import *

from code_font import MONO
from line import Connector
from node import Node

config.background_color = "#0d1118"
MUTED = "#8a93a6"


def caption(s, y, font=MONO, size=22):
    return Text(s, font=font, font_size=size, color=MUTED).move_to(UP * y)


class Demo(Scene):
    def say(self, call):
        new = caption(call, -2.9)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        api = Node("API", "gateway", icon="tabler/outline/server").scale(2)
        self.say('Node("API", "gateway", icon="tabler/outline/server")')
        self.play(FadeIn(api, scale=0.9), run_time=0.5)
        self.wait(1)
        for status in ("active", "failed", "inactive"):
            self.say(f'node.to("{status}")')
            self.play(api.to(status))
            self.wait(1.3)
        self.play(FadeOut(api), FadeOut(self.caption), run_time=0.4)

        # nodes in a diagram, joined by lines
        web = Node("Web", "client", icon="tabler/outline/browser", width=2.4).move_to(LEFT * 4.4)
        api = Node("API", "gateway", icon="tabler/outline/server", width=2.4)
        db = Node("Postgres", "primary", icon="tabler/outline/database", width=2.4).move_to(RIGHT * 4.4 + UP * 1.1)
        cache = Node("Redis", "cache", icon="tabler/outline/bolt", width=2.4).move_to(RIGHT * 4.4 + DOWN * 1.1)
        first, second = Connector(web, api), Connector(api, [db, cache])
        self.play(LaggedStart(*[FadeIn(n, scale=0.9) for n in (web, api, db, cache)], lag_ratio=0.15), run_time=1)
        self.play(first.grow(), second.grow())
        self.wait(0.5)
        self.play(web.to("active"))
        self.play(api.to("active"))
        self.play(db.to("active"), cache.to("active"))
        self.wait(1)
        self.play(db.to("failed"))
        self.wait(1)
        self.play(db.to("inactive"), web.to("inactive"), api.to("inactive"), cache.to("inactive"))
        self.wait(2)


class Still(Scene):
    def construct(self):
        for i, status in enumerate(("inactive", "active", "failed")):
            node = Node("API", "gateway", icon="tabler/outline/server", status=status).move_to(RIGHT * (i - 1) * 3.3 + UP * 0.55)
            self.add(node, caption(status, 1.5, "Noto Sans", 20).set_x(node.get_x()))
        small = [Node("Postgres", icon="tabler/outline/database"), Node("auth-service", status="active"),
                 Node("Queue", "orders", status="failed"), Node("CDN", icon="tabler/outline/cloud")]
        VGroup(*small).arrange(RIGHT, buff=0.7).move_to(DOWN * 1.2)
        self.add(*small)

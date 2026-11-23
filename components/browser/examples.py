"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from browser import Browser
from code_font import MONO

config.background_color = "#0d1118"
TRACK, LINE, MUTED = "#1c2130", "#3a4252", "#8a93a6"
BAR, FAINT = "#414858", "#2c3240"


def block(width, height, color, radius=0.08):
    return RoundedRectangle(corner_radius=min(radius, height / 2 - 1e-3), width=width, height=height, stroke_width=0,
                            fill_color=color, fill_opacity=1)


def shop(screen):
    """A placeholder page the size of the screen: a heading, a line of text and three cards."""
    w, h = screen.width, screen.height
    head = VGroup(block(w * 0.4, 0.22, BAR), block(w * 0.64, 0.13, FAINT)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
    cards = VGroup(*[block((w - 0.5) / 3, h - 0.85, TRACK, 0.15) for _ in range(3)]).arrange(RIGHT, buff=0.25)
    return VGroup(head, cards).arrange(DOWN, buff=0.3, aligned_edge=LEFT)


def cart(screen):
    """Another: four rows, each a thumbnail and two lines of text."""
    w, h = screen.width, screen.height
    rows = VGroup()
    for _ in range(4):
        text = VGroup(block(w * 0.55, 0.15, BAR), block(w * 0.36, 0.12, FAINT)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        rows.add(VGroup(block(0.55, 0.55, TRACK, 0.12), text).arrange(RIGHT, buff=0.3))
    return rows.arrange(DOWN, buff=(h - 4 * 0.55) / 3, aligned_edge=LEFT)


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=20, color=MUTED).move_to(DOWN * 3.4)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        b = Browser("shop.example", width=9.0, height=5.4).shift(UP * 0.45)
        self.say('b = Browser("shop.example")')
        self.play(b.draw())
        self.wait(0.6)
        self.say("b.show(shop)")
        self.play(b.show(shop(b.screen)))
        self.wait(1)
        self.say('b.go("shop.example/cart", cart)')
        self.play(b.go("shop.example/cart", cart(b.screen)))
        self.wait(1)
        self.say('b.go("shop.example/cart?coupon=SPRING")     only the address changes')
        self.play(b.go("shop.example/cart?coupon=SPRING"))
        self.wait(1)
        self.say('b.go("shop.example", shop)')
        self.play(b.go("shop.example", shop(b.screen)))
        self.wait(1.5)


class Still(Scene):
    def construct(self):
        b = Browser("shop.example", width=8.4, height=4.6)
        self.add(b, b.place(shop(b.screen)))

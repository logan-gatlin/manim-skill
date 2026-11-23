"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from code_font import MONO
from tree import Tree

config.background_color = "#0d1118"
MUTED = "#8a93a6"

SEARCH = {8: [4, 12], 4: [2, 6], 12: [10, 14]}
PAGE = {"html": ["head", "body"], "head": ["title"], "body": ["nav", "main", "footer"], "main": ["h1", "p"]}


def done(move, part=1):
    """Run an animation to its end, or part of the way."""
    move.begin()
    move.interpolate(part)
    if part == 1:
        move.finish()


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
        t = Tree(SEARCH, binary=True).scale(1.45).shift(UP * 3.0)
        self.say("t = Tree({8: [4, 12], 4: [2, 6], 12: [10, 14]}, binary=True)")
        self.play(t.draw())
        self.wait(0.8)
        for call, move in [("t.visit(8, 4, 6)", lambda: t.visit(8, 4, 6)),
                           ("t.add_node(5, 6)", lambda: t.add_node(5, 6)),
                           ("t.insert_value(11)", lambda: t.insert_value(11)),
                           ("t.fold(4)", lambda: t.fold(4)),
                           ("t.unfold(4)", lambda: t.unfold(4)),
                           ("t.remove_node(14)", lambda: t.remove_node(14)),
                           ("t.mark(10)", lambda: t.mark(10)),
                           ("t.unmark()", lambda: t.unmark())]:
            self.say(call)
            self.play(move())
            self.wait(0.7)
        self.play(FadeOut(t), run_time=0.4)

        page = Tree(PAGE).scale(1.2).shift(UP * 2.6 + LEFT * 0.6)
        self.say('page = Tree({"html": ["head", "body"], "body": ["nav", "main", "footer"], ...})')
        self.play(page.draw())
        self.wait(0.6)
        for call, move in [('page.add_node("meta", "head")', lambda: page.add_node("meta", "head")),
                           ('page.fold("body")', lambda: page.fold("body")),
                           ('page.unfold("body")', lambda: page.unfold("body"))]:
            self.say(call)
            self.play(move())
            self.wait(0.7)
        self.wait(1)


class Still(Scene):
    def construct(self):
        a = Tree(SEARCH, binary=True)
        done(a.add_node(5, 6, hold=None))
        done(a.mark(4))
        done(a.fold(12))
        b = Tree(PAGE).scale(0.85)
        done(b.remove_node("footer"), 0.25)
        for tree, x, name in [(a, -3.9, "A binary search tree"), (b, 2.9, "Any tree")]:
            tree.move_to([x, 0, 0]).shift(UP * (1.75 - tree.get_top()[1]))
            label = Text("Hg" + name, font="Noto Sans", font_size=18, color=MUTED)
            label.shift([0, 2.3, 0] - label[:2].get_center())
            words = VGroup(*label[2:])
            self.add(tree, words.shift([x - words.get_center()[0], 0, 0]))

"""Renders the image in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # code_font.py, at the skill root

from manim import *

from code_font import MONO
from table import DataTable

config.background_color = "#0d1118"
MUTED = "#8a93a6"

COLUMNS = ["id", "item", "qty", "status"]
ORDERS = [["1001", "Keyboard", 1, "shipped"], ["1002", "Monitor", 2, "paid"], ["1003", "Cable", 5, "paid"],
          ["1004", "Desk", 1, "shipped"]]


def orders():
    return DataTable(COLUMNS, ORDERS, widths={"status": 1.1})


class Demo(Scene):
    def say(self, call):
        new = Text(call, font=MONO, font_size=20, color=MUTED).move_to(DOWN * 3.2)
        if self.caption is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(FadeOut(self.caption), FadeIn(new), run_time=0.3)
        self.caption = new

    def construct(self):
        self.caption = None
        t = orders().scale(1.5).move_to(UP * 0.9)
        self.say("t = DataTable(columns, rows)")
        self.play(t.draw())
        self.wait(0.8)
        for call, move in [('t.insert_row(["1005", "Mug", 2, "new"])', lambda: t.insert_row(["1005", "Mug", 2, "new"])),
                           ('t.update_row("1002", status="shipped")', lambda: t.update_row("1002", status="shipped")),
                           ('t.delete_row("1003")', lambda: t.delete_row("1003")),
                           ('t.insert_row(["1000", "Lamp", 3, "new"], at=0)', lambda: t.insert_row(["1000", "Lamp", 3, "new"], at=0)),
                           ('t.update_row("1005", qty=12, status="paid")', lambda: t.update_row("1005", qty=12, status="paid")),
                           ('t.mark("1004")', lambda: t.mark("1004")),
                           ("t.unmark()", lambda: t.unmark())]:
            self.say(call)
            self.play(move())
            self.wait(0.7)
        self.wait(1)


class Still(Scene):
    def construct(self):
        t = orders().scale(1.25)
        # each change stopped part-way, with its bar lit
        for move, part in [(t.insert_row(["1005", "Mug", 2, "new"], hold=None), 1), (t.update_row("1002", hold=None, status="shipped"), 1),
                           (t.delete_row("1003"), 0.3)]:
            move.begin()
            move.interpolate(part)
        t.move_to(LEFT * 0.6)
        self.add(t)
        for row, name in [("1002", "updated"), (2, "deleted"), ("1005", "inserted")]:
            y = t.body[row if isinstance(row, int) else [r.values[0] for r in t.body].index(row)].bar.get_center()[1]
            label = Text("Hg" + name, font="Noto Sans", font_size=18, color=MUTED)
            label.shift([0, y, 0] - label[:2].get_center())
            self.add(VGroup(*label[2:]).shift([t.get_right()[0] + 0.7 - label[2].get_left()[0], 0, 0]))

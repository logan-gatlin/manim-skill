"""Renders the images in images/ and a demo video; see README.md for the commands."""

from manim import *

from line import INK, PANEL, Connector

LINE = "#3a4252"
MUTED = "#8a93a6"
BLUE, TEAL, VIOLET, AMBER = "#60a5fa", "#2dd4bf", "#a78bfa", "#fbbf24"
MONO = "DejaVu Sans Mono"


def box(word=None, w=1.0, h=0.6):
    b = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=LINE, stroke_width=2,
                         fill_color=PANEL, fill_opacity=1)
    if word:
        b = VGroup(b, Text(word, font="Noto Sans", font_size=16, color=INK))
    return b


def cell(title, call, make):
    """One example: its boxes and line, with the call that draws it underneath."""
    art = make()
    code = Text(call, font=MONO, font_size=13, color=MUTED)
    name = Text(title, font="Noto Sans", font_size=17, color=INK)
    return VGroup(name, art, code)


def pair(dy=0.0, **options):
    def make():
        a, b = box().move_to(LEFT * 1.9 + UP * dy / 2), box().move_to(RIGHT * 1.9 + DOWN * dy / 2)
        return VGroup(a, b, Connector(a, b, **options))
    return make


def u_turn():
    a, b = box().move_to(UP * 0.5), box().move_to(DOWN * 0.5)
    return VGroup(a, b, Connector(a, b, route="u", side=RIGHT, reach=1.4, color=AMBER)).shift(LEFT * 0.9)


def fork():
    a = box().move_to(LEFT * 1.9)
    outs = [box(h=0.44).move_to(RIGHT * 1.9 + UP * y) for y in (0.62, 0, -0.62)]
    return VGroup(a, *outs, Connector(a, outs, color=VIOLET))


def corner():
    a, b = box().move_to(LEFT * 1.9 + UP * 0.55), box(h=0.44).move_to(RIGHT * 1.4 + DOWN * 0.62)
    return VGroup(a, b, Connector(a, b, route="hv", color=TEAL))


CELLS = [
    ("Straight", "Connector(a, b)", pair()),
    ("Elbows", "Connector(a, b)", pair(1.0, color=BLUE)),
    ("One corner", 'Connector(a, b, route="hv")', corner),
    ("Two-way", "Connector(a, b, two_way=True)", pair(two_way=True, color=TEAL)),
    ("Dashed", 'Connector(a, b, style="dashed")', pair(style="dashed", color=BLUE)),
    ("Dotted", 'Connector(a, b, style="dotted")', pair(style="dotted", color=VIOLET)),
    ("Label", 'Connector(a, b, label="HTTP")', pair(label="HTTP", color=TEAL)),
    ("Plain line", "Connector(a, b, tip=False)", pair(tip=False, color=AMBER)),
    ("Fork", "Connector(a, [b, c, d])", fork),
    ("U-turn", 'Connector(a, b, route="u", side=RIGHT)', u_turn),
    ("Label on elbows", 'Connector(a, b, label="retry", mid=0.7)',
     pair(1.0, label="retry", mid=0.7, color=AMBER)),
    ("Straight at an angle", 'Connector(a, b, route="straight")', pair(1.0, route="straight")),
]


class Framed(MovingCameraScene):
    def frame_to(self, mob, pad=0.5):
        aspect = config.pixel_width / config.pixel_height
        self.camera.frame.set(width=max(mob.width + 2 * pad, (mob.height + 2 * pad) * aspect))
        self.camera.frame.move_to(mob)


class Options(Framed):
    """Every option, each with the call that draws it."""

    def construct(self):
        cells = VGroup()
        for i, (title, call, make) in enumerate(CELLS):
            name, art, code = cell(title, call, make)
            c = np.array([(i % 3) * 5.6, -(i // 3) * 2.75, 0])
            art.move_to(c)
            name.move_to(c + UP * 1.12 + LEFT * 2.4, aligned_edge=LEFT)
            code.move_to(c + DOWN * 1.12 + LEFT * 2.4, aligned_edge=LEFT)
            cells.add(name, art, code)
        self.add(cells)
        self.frame_to(cells)


class Diagram(Framed):
    """The options together in one small diagram."""

    def build(self):
        client, api = box("client", 1.4).move_to(LEFT * 5.2), box("api", 1.2).move_to(LEFT * 1.5)
        cache = box("cache", 1.3).move_to(RIGHT * 1.9 + UP * 1.3)
        db = box("db", 1.3).move_to(RIGHT * 1.9 + DOWN * 1.3)
        replica = box("replica", 1.5).move_to(RIGHT * 5.3 + DOWN * 1.3)
        links = [
            Connector(client, api, label="HTTPS", color=BLUE),
            Connector(api, [cache, db], color=TEAL),
            Connector(db, replica, style="dashed", two_way=True, color=VIOLET),
            Connector(api, api, route="u", side=UP, reach=0.7, style="dotted", color=AMBER),
        ]
        return VGroup(client, api, cache, db, replica), links

    def construct(self):
        boxes, links = self.build()
        self.add(boxes, *links)
        self.frame_to(VGroup(boxes, *links))


class Demo(Scene):
    """Each kind of line growing in."""

    def construct(self):
        boxes, links = Diagram.build(self)
        self.play(FadeIn(boxes), run_time=0.6)
        for link in links:
            self.play(link.grow(run_time=1.1))
            self.wait(0.3)
        self.wait(1.5)

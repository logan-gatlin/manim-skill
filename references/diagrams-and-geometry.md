# Shapes, arrows, labels, angles, highlighting, annotations

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `UsefulAnnotations`: Dots, labeled dots, curved arrows and double arrows for annotation.
- `VectorArrow`: Vector on a NumberPlane with coordinate labels.
- `ArrowExample`: Arrow tips, buff, and how arrow size scales with length.
- `DashedLineExample`: DashedLine variants: dash length and spacing.
- `TangentLineExample`: TangentLine to a circle at given proportions.
- `LabeledLineExample`: LabeledLine: a line with a label box on it.
- `LabeledArrowExample`: LabeledArrow: an arrow with a label box on it.
- `LabeledPolygramExample`: LabeledPolygram: label placed at the pole of inaccessibility of a shape with holes.
- `SeveralLabeledDots`: LabeledDot with text and math labels.
- `AngleExample`: Angle markers: radius, quadrant, other_angle, dot.
- `RightAngleExample`: RightAngle markers in each quadrant.
- `SurroundingRectExample`: SurroundingRectangle to highlight text blocks.
- `UnderLine`: Underline beneath text.
- `ExampleCross`: Cross over a mobject (marking something wrong).
- `ArcBraceExample`: ArcBrace around arcs of different sizes.
- `BooleanOperations`: Venn-style Union, Intersection, Difference and Exclusion with labels.
- `PolygonExample`: Polygon from arbitrary vertices.
- `RoundedRectangleExample`: RoundedRectangle corner radius.
- `AnnularSectorExample`: AnnularSector variations (ring segments).
- `CutoutExample`: Cutout: holes punched in a shape.
- `DashedVMobjectExample`: DashedVMobject applied to circles and arbitrary paths.
- `ArrowTipsShowcase`: Every arrow tip style side by side.

## UsefulAnnotations

Dots, labeled dots, curved arrows and double arrows for annotation. *still*. Source: [manim/mobject/geometry/arc.py:5](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/arc.py#L5)

```python
from manim import *
class UsefulAnnotations(Scene):
    def construct(self):
        m0 = Dot()
        m1 = AnnotationDot()
        m2 = LabeledDot("ii")
        m3 = LabeledDot(MathTex(r"\alpha").set_color(ORANGE))
        m4 = CurvedArrow(2*LEFT, 2*RIGHT, radius= -5)
        m5 = CurvedArrow(2*LEFT, 2*RIGHT, radius= 8)
        m6 = CurvedDoubleArrow(ORIGIN, 2*RIGHT)

        self.add(m0, m1, m2, m3, m4, m5, m6)
        for i, mobj in enumerate(self.mobjects):
            mobj.shift(DOWN * (i-3))
```

## VectorArrow

Vector on a NumberPlane with coordinate labels. *still*. Source: [docs/source/examples.rst:69](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L69)

```python
from manim import *
class VectorArrow(Scene):
    def construct(self):
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        numberplane = NumberPlane()
        origin_text = Text('(0, 0)').next_to(dot, DOWN)
        tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
        self.add(numberplane, dot, arrow, origin_text, tip_text)
```

## ArrowExample

Arrow tips, buff, and how arrow size scales with length. *still*. Source: [manim/mobject/geometry/line.py:528](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/line.py#L528)

```python
from manim import *
from manim.mobject.geometry.tips import ArrowSquareTip
class ArrowExample(Scene):
    def construct(self):
        arrow_1 = Arrow(start=RIGHT, end=LEFT, color=GOLD)
        arrow_2 = Arrow(start=RIGHT, end=LEFT, color=GOLD, tip_shape=ArrowSquareTip).shift(DOWN)
        g1 = Group(arrow_1, arrow_2)

        # the effect of buff
        square = Square(color=MAROON_A)
        arrow_3 = Arrow(start=LEFT, end=RIGHT)
        arrow_4 = Arrow(start=LEFT, end=RIGHT, buff=0).next_to(arrow_1, UP)
        g2 = Group(arrow_3, arrow_4, square)

        # a shorter arrow has a shorter tip and smaller stroke width
        arrow_5 = Arrow(start=ORIGIN, end=config.top).shift(LEFT * 4)
        arrow_6 = Arrow(start=config.top + DOWN, end=config.top).shift(LEFT * 3)
        g3 = Group(arrow_5, arrow_6)

        self.add(Group(g1, g2, g3).arrange(buff=2))
```

## DashedLineExample

DashedLine variants: dash length and spacing. *still*. Source: [manim/mobject/geometry/line.py:302](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/line.py#L302)

```python
from manim import *
class DashedLineExample(Scene):
    def construct(self):
        # dash_length increased
        dashed_1 = DashedLine(config.left_side, config.right_side, dash_length=2.0).shift(UP*2)
        # normal
        dashed_2 = DashedLine(config.left_side, config.right_side)
        # dashed_ratio decreased
        dashed_3 = DashedLine(config.left_side, config.right_side, dashed_ratio=0.1).shift(DOWN*2)
        self.add(dashed_1, dashed_2, dashed_3)
```

## TangentLineExample

TangentLine to a circle at given proportions. *still*. Source: [manim/mobject/geometry/line.py:435](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/line.py#L435)

```python
from manim import *
class TangentLineExample(Scene):
    def construct(self):
        circle = Circle(radius=2)
        line_1 = TangentLine(circle, alpha=0.0, length=4, color=BLUE_D) # right
        line_2 = TangentLine(circle, alpha=0.4, length=4, color=GREEN) # top left
        self.add(circle, line_1, line_2)
```

## LabeledLineExample

LabeledLine: a line with a label box on it. *still*. Source: [manim/mobject/geometry/labeled.py:140](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/labeled.py#L140)

```python
from manim import *
class LabeledLineExample(Scene):
    def construct(self):
        line = LabeledLine(
            label          = '0.5',
            label_position = 0.8,
            label_config = {
                "font_size" : 20
            },
            start=LEFT+DOWN,
            end=RIGHT+UP)

        line.set_length(line.get_length() * 2)
        self.add(line)
```

## LabeledArrowExample

LabeledArrow: an arrow with a label box on it. *still*. Source: [manim/mobject/geometry/labeled.py:211](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/labeled.py#L211)

```python
from manim import *
class LabeledArrowExample(Scene):
    def construct(self):
        l_arrow = LabeledArrow("0.5", start=LEFT*3, end=RIGHT*3 + UP*2, label_position=0.5)

        self.add(l_arrow)
```

## LabeledPolygramExample

LabeledPolygram: label placed at the pole of inaccessibility of a shape with holes. *still*. Source: [manim/mobject/geometry/labeled.py:260](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/labeled.py#L260)

```python
from manim import *
class LabeledPolygramExample(Scene):
    def construct(self):
        # Define Rings
        ring1 = [
            [-3.8, -2.4, 0], [-2.4, -2.5, 0], [-1.3, -1.6, 0], [-0.2, -1.7, 0],
            [1.7, -2.5, 0], [2.9, -2.6, 0], [3.5, -1.5, 0], [4.9, -1.4, 0],
            [4.5, 0.2, 0], [4.7, 1.6, 0], [3.5, 2.4, 0], [1.1, 2.5, 0],
            [-0.1, 0.9, 0], [-1.2, 0.5, 0], [-1.6, 0.7, 0], [-1.4, 1.9, 0],
            [-2.6, 2.6, 0], [-4.4, 1.2, 0], [-4.9, -0.8, 0], [-3.8, -2.4, 0]
        ]
        ring2 = [
            [0.2, -1.2, 0], [0.9, -1.2, 0], [1.4, -2.0, 0], [2.1, -1.6, 0],
            [2.2, -0.5, 0], [1.4, 0.0, 0], [0.4, -0.2, 0], [0.2, -1.2, 0]
        ]
        ring3 = [[-2.7, 1.4, 0], [-2.3, 1.7, 0], [-2.8, 1.9, 0], [-2.7, 1.4, 0]]

        # Create Polygons (for reference)
        p1 = Polygon(*ring1, fill_opacity=0.75)
        p2 = Polygon(*ring2, fill_color=BLACK, fill_opacity=1)
        p3 = Polygon(*ring3, fill_color=BLACK, fill_opacity=1)

        # Create Labeled Polygram
        polygram = LabeledPolygram(
            *[ring1, ring2, ring3],
            label=Text('Pole', font='sans-serif'),
            precision=0.01,
        )

        # Display Circle (for reference)
        circle = Circle(radius=polygram.radius, color=WHITE).move_to(polygram.pole)

        self.add(p1, p2, p3)
        self.add(polygram)
        self.add(circle)
```

## SeveralLabeledDots

LabeledDot with text and math labels. *still*. Source: [manim/mobject/geometry/arc.py:876](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/arc.py#L876)

```python
from manim import *
class SeveralLabeledDots(Scene):
    def construct(self):
        sq = Square(fill_color=RED, fill_opacity=1)
        self.add(sq)
        dot1 = LabeledDot(Tex("42", color=RED))
        dot2 = LabeledDot(MathTex("a", color=GREEN))
        dot3 = LabeledDot(Text("ii", color=BLUE))
        dot4 = LabeledDot("3")
        dot1.next_to(sq, UL)
        dot2.next_to(sq, UR)
        dot3.next_to(sq, DL)
        dot4.next_to(sq, DR)
        self.add(dot1, dot2, dot3, dot4)
```

## AngleExample

Angle markers: radius, quadrant, other_angle, dot. *still*. Source: [manim/mobject/geometry/line.py:933](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/line.py#L933)

```python
from manim import *
class AngleExample(Scene):
    def construct(self):
        line1 = Line( LEFT + (1/3) * UP, RIGHT + (1/3) * DOWN )
        line2 = Line( DOWN + (1/3) * RIGHT, UP + (1/3) * LEFT )
        angles = [
            Angle(line1, line2),
            Angle(line1, line2, radius=0.4, quadrant=(1,-1), other_angle=True),
            Angle(line1, line2, radius=0.5, quadrant=(-1,1), stroke_width=8, other_angle=True),
            Angle(line1, line2, radius=0.7, quadrant=(-1,-1), color=RED),
            Angle(line1, line2, other_angle=True),
            Angle(line1, line2, radius=0.4, quadrant=(1,-1)),
            Angle(line1, line2, radius=0.5, quadrant=(-1,1), stroke_width=8),
            Angle(line1, line2, radius=0.7, quadrant=(-1,-1), color=RED, other_angle=True),
        ]
        plots = VGroup()
        for angle in angles:
            plot=VGroup(line1.copy(),line2.copy(), angle)
            plots.add(VGroup(plot,SurroundingRectangle(plot, buff=0.3)))
        plots.arrange_in_grid(rows=2,buff=1)
        self.add(plots)
```

## RightAngleExample

RightAngle markers in each quadrant. *still*. Source: [manim/mobject/geometry/line.py:1205](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/line.py#L1205)

```python
from manim import *
class RightAngleExample(Scene):
    def construct(self):
        line1 = Line( LEFT, RIGHT )
        line2 = Line( DOWN, UP )
        rightangles = [
            RightAngle(line1, line2),
            RightAngle(line1, line2, length=0.4, quadrant=(1,-1)),
            RightAngle(line1, line2, length=0.5, quadrant=(-1,1), stroke_width=8),
            RightAngle(line1, line2, length=0.7, quadrant=(-1,-1), color=RED),
        ]
        plots = VGroup()
        for rightangle in rightangles:
            plot=VGroup(line1.copy(),line2.copy(), rightangle)
            plots.add(plot)
        plots.arrange(buff=1.5)
        self.add(plots)
```

## SurroundingRectExample

SurroundingRectangle to highlight text blocks. *still*. Source: [manim/mobject/geometry/shape_matchers.py:31](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/shape_matchers.py#L31)

```python
from manim import *
class SurroundingRectExample(Scene):
    def construct(self):
        title = Title("A Quote from Newton")
        quote = Text(
            "If I have seen further than others, \n"
            "it is by standing upon the shoulders of giants.",
            color=BLUE,
        ).scale(0.75)
        box = SurroundingRectangle(quote, color=YELLOW, buff=MED_LARGE_BUFF)

        t2 = Tex(r"Hello World").scale(1.5)
        box2 = SurroundingRectangle(t2, corner_radius=0.2)
        mobjects = VGroup(VGroup(box, quote), VGroup(t2, box2)).arrange(DOWN)
        self.add(title, mobjects)
```

## UnderLine

Underline beneath text. *still*. Source: [manim/mobject/geometry/shape_matchers.py:200](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/shape_matchers.py#L200)

```python
from manim import *
class UnderLine(Scene):
    def construct(self):
        man = Tex("Manim")  # Full Word
        ul = Underline(man)  # Underlining the word
        self.add(man, ul)
```

## ExampleCross

Cross over a mobject (marking something wrong). *still*. Source: [manim/mobject/geometry/shape_matchers.py:169](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/shape_matchers.py#L169)

```python
from manim import *
class ExampleCross(Scene):
    def construct(self):
        cross = Cross()
        self.add(cross)
```

## ArcBraceExample

ArcBrace around arcs of different sizes. *still*. Source: [manim/mobject/svg/brace.py:413](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/svg/brace.py#L413)

```python
from manim import *
class ArcBraceExample(Scene):
    def construct(self):
        arc_1 = Arc(radius=1.5,start_angle=0,angle=2*PI/3).set_color(RED)
        brace_1 = ArcBrace(arc_1,LEFT)
        group_1 = VGroup(arc_1,brace_1)

        arc_2 = Arc(radius=3,start_angle=0,angle=5*PI/6).set_color(YELLOW)
        brace_2 = ArcBrace(arc_2)
        group_2 = VGroup(arc_2,brace_2)

        arc_3 = Arc(radius=0.5,start_angle=-0,angle=PI).set_color(BLUE)
        brace_3 = ArcBrace(arc_3)
        group_3 = VGroup(arc_3,brace_3)

        arc_4 = Arc(radius=0.2,start_angle=0,angle=3*PI/2).set_color(GREEN)
        brace_4 = ArcBrace(arc_4)
        group_4 = VGroup(arc_4,brace_4)

        arc_group = VGroup(group_1, group_2, group_3, group_4).arrange_in_grid(buff=1.5)
        self.add(arc_group.center())
```

## BooleanOperations

Venn-style Union, Intersection, Difference and Exclusion with labels. *animation*. Source: [docs/source/examples.rst:96](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L96)

```python
from manim import *
class BooleanOperations(Scene):
    def construct(self):
        ellipse1 = Ellipse(
            width=4.0, height=5.0, fill_opacity=0.5, color=BLUE, stroke_width=10
        ).move_to(LEFT)
        ellipse2 = ellipse1.copy().set_color(color=RED).move_to(RIGHT)
        bool_ops_text = MarkupText("<u>Boolean Operation</u>").next_to(ellipse1, UP * 3)
        ellipse_group = Group(bool_ops_text, ellipse1, ellipse2).move_to(LEFT * 3)
        self.play(FadeIn(ellipse_group))

        i = Intersection(ellipse1, ellipse2, color=GREEN, fill_opacity=0.5)
        self.play(i.animate.scale(0.25).move_to(RIGHT * 5 + UP * 2.5))
        intersection_text = Text("Intersection", font_size=23).next_to(i, UP)
        self.play(FadeIn(intersection_text))

        u = Union(ellipse1, ellipse2, color=ORANGE, fill_opacity=0.5)
        union_text = Text("Union", font_size=23)
        self.play(u.animate.scale(0.3).next_to(i, DOWN, buff=union_text.height * 3))
        union_text.next_to(u, UP)
        self.play(FadeIn(union_text))

        e = Exclusion(ellipse1, ellipse2, color=YELLOW, fill_opacity=0.5)
        exclusion_text = Text("Exclusion", font_size=23)
        self.play(e.animate.scale(0.3).next_to(u, DOWN, buff=exclusion_text.height * 3.5))
        exclusion_text.next_to(e, UP)
        self.play(FadeIn(exclusion_text))

        d = Difference(ellipse1, ellipse2, color=PINK, fill_opacity=0.5)
        difference_text = Text("Difference", font_size=23)
        self.play(d.animate.scale(0.3).next_to(u, LEFT, buff=difference_text.height * 3.5))
        difference_text.next_to(d, UP)
        self.play(FadeIn(difference_text))
```

## PolygonExample

Polygon from arbitrary vertices. *still*. Source: [manim/mobject/geometry/polygram.py:323](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/polygram.py#L323)

```python
from manim import *
class PolygonExample(Scene):
    def construct(self):
        isosceles = Polygon([-5, 1.5, 0], [-2, 1.5, 0], [-3.5, -2, 0])
        position_list = [
            [4, 1, 0],  # middle right
            [4, -2.5, 0],  # bottom right
            [0, -2.5, 0],  # bottom left
            [0, 3, 0],  # top left
            [2, 1, 0],  # middle
            [4, 3, 0],  # top right
        ]
        square_and_triangles = Polygon(*position_list, color=PURPLE_B)
        self.add(isosceles, square_and_triangles)
```

## RoundedRectangleExample

RoundedRectangle corner radius. *still*. Source: [manim/mobject/geometry/polygram.py:737](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/polygram.py#L737)

```python
from manim import *
class RoundedRectangleExample(Scene):
    def construct(self):
        rect_1 = RoundedRectangle(corner_radius=0.5)
        rect_2 = RoundedRectangle(corner_radius=1.5, height=4.0, width=4.0)

        rect_group = Group(rect_1, rect_2).arrange(buff=1)
        self.add(rect_group)
```

## AnnularSectorExample

AnnularSector variations (ring segments). *still*. Source: [manim/mobject/geometry/arc.py:971](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/arc.py#L971)

```python
from manim import *
class AnnularSectorExample(Scene):
    def construct(self):
        # Changes background color to clearly visualize changes in fill_opacity.
        self.camera.background_color = WHITE

        # The default parameter start_angle is 0, so the AnnularSector starts from the +x-axis.
        s1 = AnnularSector(color=YELLOW).move_to(2 * UL)

        # Different inner_radius and outer_radius than the default.
        s2 = AnnularSector(inner_radius=1.5, outer_radius=2, angle=45 * DEGREES, color=RED).move_to(2 * UR)

        # fill_opacity is typically a number > 0 and <= 1. If fill_opacity=0, the AnnularSector is transparent.
        s3 = AnnularSector(inner_radius=1, outer_radius=1.5, angle=PI, fill_opacity=0.25, color=BLUE).move_to(2 * DL)

        # With a negative value for the angle, the AnnularSector is drawn clockwise from the start value.
        s4 = AnnularSector(inner_radius=1, outer_radius=1.5, angle=-3 * PI / 2, color=GREEN).move_to(2 * DR)

        self.add(s1, s2, s3, s4)
```

## CutoutExample

Cutout: holes punched in a shape. *animation*. Source: [manim/mobject/geometry/polygram.py:776](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/polygram.py#L776)

```python
from manim import *
class CutoutExample(Scene):
    def construct(self):
        s1 = Square().scale(2.5)
        s2 = Triangle().shift(DOWN + RIGHT).scale(0.5)
        s3 = Square().shift(UP + RIGHT).scale(0.5)
        s4 = RegularPolygon(5).shift(DOWN + LEFT).scale(0.5)
        s5 = RegularPolygon(6).shift(UP + LEFT).scale(0.5)
        c = Cutout(s1, s2, s3, s4, s5, fill_opacity=1, color=BLUE, stroke_color=RED)
        self.play(Write(c), run_time=4)
        self.wait()
```

## DashedVMobjectExample

DashedVMobject applied to circles and arbitrary paths. *still*. Source: [manim/mobject/types/vectorized_mobject.py:2882](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/types/vectorized_mobject.py#L2882)

```python
from manim import *
class DashedVMobjectExample(Scene):
    def construct(self):
        r = 0.5

        top_row = VGroup()  # Increasing num_dashes
        for dashes in range(1, 12):
            circ = DashedVMobject(Circle(radius=r, color=WHITE), num_dashes=dashes)
            top_row.add(circ)

        middle_row = VGroup()  # Increasing dashed_ratio
        for ratio in np.arange(1 / 11, 1, 1 / 11):
            circ = DashedVMobject(
                Circle(radius=r, color=WHITE), dashed_ratio=ratio
            )
            middle_row.add(circ)

        func1 = FunctionGraph(lambda t: t**5,[-1,1],color=WHITE)
        func_even = DashedVMobject(func1,num_dashes=6,equal_lengths=True)
        func_stretched = DashedVMobject(func1, num_dashes=6, equal_lengths=False)
        bottom_row = VGroup(func_even,func_stretched)


        top_row.arrange(buff=0.3)
        middle_row.arrange()
        bottom_row.arrange(buff=1)
        everything = VGroup(top_row, middle_row, bottom_row).arrange(DOWN, buff=1)
        self.add(everything)
```

## ArrowTipsShowcase

Every arrow tip style side by side. *still*. Source: [manim/mobject/geometry/tips.py:82](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/geometry/tips.py#L82)

```python
from manim import *
class ArrowTipsShowcase(Scene):
    def construct(self):
        tip_names = [
            'Default (YELLOW)', 'ArrowTriangleTip', 'Default', 'ArrowSquareTip',
            'ArrowSquareFilledTip', 'ArrowCircleTip', 'ArrowCircleFilledTip', 'StealthTip'
        ]

        big_arrows = [
            Arrow(start=[-4, 3.5, 0], end=[2, 3.5, 0], color=YELLOW),
            Arrow(start=[-4, 2.5, 0], end=[2, 2.5, 0], tip_shape=ArrowTriangleTip),
            Arrow(start=[-4, 1.5, 0], end=[2, 1.5, 0]),
            Arrow(start=[-4, 0.5, 0], end=[2, 0.5, 0], tip_shape=ArrowSquareTip),

            Arrow([-4, -0.5, 0], [2, -0.5, 0], tip_shape=ArrowSquareFilledTip),
            Arrow([-4, -1.5, 0], [2, -1.5, 0], tip_shape=ArrowCircleTip),
            Arrow([-4, -2.5, 0], [2, -2.5, 0], tip_shape=ArrowCircleFilledTip),
            Arrow([-4, -3.5, 0], [2, -3.5, 0], tip_shape=StealthTip)
        ]

        small_arrows = (
            arrow.copy().scale(0.5, scale_tips=True).next_to(arrow, RIGHT) for arrow in big_arrows
        )

        labels = (
            Text(tip_names[i], font='monospace', font_size=20, color=BLUE).next_to(big_arrows[i], LEFT) for i in range(len(big_arrows))
        )

        self.add(*big_arrows, *small_arrows, *labels)
```

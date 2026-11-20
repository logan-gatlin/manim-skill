# Scene basics: placement, styling, grouping, simple animation

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `MobjectPlacement`: Absolute and relative placement: shift, move_to, next_to, align_to.
- `MobjectStyling`: Stroke and fill styling: set_stroke, set_fill, opacity.
- `ArrangeInGrid`: arrange_in_grid with per-row/column sizing and alignment.
- `MovingAround`: Chaining .animate calls one at a time: shift, set_fill, scale, rotate.
- `MovingGroupToDestination`: Moving a whole group so a chosen member lands on a target point.
- `SomeAnimations`: Core enter/exit animations: FadeIn, Rotate, FadeOut.
- `AnimateExample`: Animating style and transform changes via .animate.
- `AnimateWithArgsExample`: Passing arguments to .animate (e.g. path_arc) for curved motion.
- `AnimatedSquareToCircle2`: Square-to-circle with Transform, the canonical first scene.
- `TransformCycle`: Cycling one mobject through shapes with Transform in a loop.
- `CountingScene`: Writing a custom Animation subclass (counting a DecimalNumber up).

## MobjectPlacement

Absolute and relative placement: shift, move_to, next_to, align_to. *animation*. Source: [docs/source/tutorials/building_blocks.rst:112](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/building_blocks.rst#L112)

```python
from manim import *
class MobjectPlacement(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        triangle = Triangle()

        # place the circle two units left from the origin
        circle.move_to(LEFT * 2)
        # place the square to the left of the circle
        square.next_to(circle, LEFT)
        # align the left border of the triangle to the left border of the circle
        triangle.align_to(circle, LEFT)

        self.add(circle, square, triangle)
        self.wait(1)
```

## MobjectStyling

Stroke and fill styling: set_stroke, set_fill, opacity. *animation*. Source: [docs/source/tutorials/building_blocks.rst:159](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/building_blocks.rst#L159)

```python
from manim import *
class MobjectStyling(Scene):
    def construct(self):
        circle = Circle().shift(LEFT)
        square = Square().shift(UP)
        triangle = Triangle().shift(RIGHT)

        circle.set_stroke(color=GREEN, width=20)
        square.set_fill(YELLOW, opacity=1.0)
        triangle.set_fill(PINK, opacity=0.5)

        self.add(circle, square, triangle)
        self.wait(1)
```

## ArrangeInGrid

arrange_in_grid with per-row/column sizing and alignment. *still*. Source: [manim/mobject/mobject.py:2844](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/mobject.py#L2844)

```python
from manim import *
class ArrangeInGrid(Scene):
    def construct(self):
        boxes = VGroup(*[
            Rectangle(WHITE, 0.5, 0.5).add(Text(str(i+1)).scale(0.5))
            for i in range(24)
        ])
        self.add(boxes)

        boxes.arrange_in_grid(
            buff=(0.25,0.5),
            col_alignments="lccccr",
            row_alignments="uccd",
            col_widths=[1, *[None]*4, 1],
            row_heights=[1, None, None, 1],
            flow_order="dr"
        )
```

## MovingAround

Chaining .animate calls one at a time: shift, set_fill, scale, rotate. *animation*. Source: [docs/source/examples.rst:155](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L155)

```python
from manim import *
class MovingAround(Scene):
    def construct(self):
        square = Square(color=BLUE, fill_opacity=1)

        self.play(square.animate.shift(LEFT))
        self.play(square.animate.set_fill(ORANGE))
        self.play(square.animate.scale(0.3))
        self.play(square.animate.rotate(0.4))
```

## MovingGroupToDestination

Moving a whole group so a chosen member lands on a target point. *animation*. Source: [docs/source/examples.rst:235](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L235)

```python
from manim import *
class MovingGroupToDestination(Scene):
    def construct(self):
        group = VGroup(Dot(LEFT), Dot(ORIGIN), Dot(RIGHT, color=RED), Dot(2 * RIGHT)).scale(1.4)
        dest = Dot([4, 3, 0], color=YELLOW)
        self.add(group, dest)
        self.play(group.animate.shift(dest.get_center() - group[2].get_center()))
        self.wait(0.5)
```

## SomeAnimations

Core enter/exit animations: FadeIn, Rotate, FadeOut. *animation*. Source: [docs/source/tutorials/building_blocks.rst:226](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/building_blocks.rst#L226)

```python
from manim import *
class SomeAnimations(Scene):
    def construct(self):
        square = Square()

        # some animations display mobjects, ...
        self.play(FadeIn(square))

        # ... some move or rotate mobjects around...
        self.play(Rotate(square, PI/4))

        # some animations remove mobjects from the screen
        self.play(FadeOut(square))

        self.wait(1)
```

## AnimateExample

Animating style and transform changes via .animate. *animation*. Source: [docs/source/tutorials/building_blocks.rst:260](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/building_blocks.rst#L260)

```python
from manim import *
class AnimateExample(Scene):
    def construct(self):
        square = Square().set_fill(RED, opacity=1.0)
        self.add(square)

        # animate the change of color
        self.play(square.animate.set_fill(WHITE))
        self.wait(1)

        # animate the change of position and the rotation at the same time
        self.play(square.animate.shift(UP).rotate(PI / 3))
        self.wait(1)
```

## AnimateWithArgsExample

Passing arguments to .animate (e.g. path_arc) for curved motion. *animation*. Source: [manim/mobject/mobject.py:394](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/mobject.py#L394)

```python
from manim import *
class AnimateWithArgsExample(Scene):
    def construct(self):
        s = Square()
        c = Circle()

        VGroup(s, c).arrange(RIGHT, buff=2)
        self.add(s, c)

        self.play(
            s.animate(run_time=2).rotate(PI / 2),
            c.animate(rate_func=there_and_back).shift(RIGHT),
        )
```

## AnimatedSquareToCircle2

Square-to-circle with Transform, the canonical first scene. *animation*. Source: [docs/source/tutorials/quickstart.rst:287](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/quickstart.rst#L287)

```python
from manim import *
class AnimatedSquareToCircle2(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        square = Square()  # create a square

        self.play(Create(square))  # show the square on screen
        self.play(square.animate.rotate(PI / 4))  # rotate the square
        self.play(Transform(square, circle))  # transform the square into a circle
        self.play(square.animate.set_fill(PINK, opacity=0.5))  # color the circle on screen
```

## TransformCycle

Cycling one mobject through shapes with Transform in a loop. *animation*. Source: [docs/source/tutorials/quickstart.rst:389](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/quickstart.rst#L389)

```python
from manim import *
class TransformCycle(Scene):
    def construct(self):
        a = Circle()
        t1 = Square()
        t2 = Triangle()
        self.add(a)
        self.wait()
        for t in [t1,t2]:
            self.play(Transform(a,t))
```

## CountingScene

Writing a custom Animation subclass (counting a DecimalNumber up). *animation*. Source: [docs/source/tutorials/building_blocks.rst:339](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/tutorials/building_blocks.rst#L339)

```python
from manim import *
class Count(Animation):
    def __init__(self, number: DecimalNumber, start: float, end: float, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(number,  **kwargs)
        # Set start and end
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        value = self.start + (self.rate_func(alpha) * (self.end - self.start))
        self.mobject.set_value(value)


class CountingScene(Scene):
    def construct(self):
        # Create Decimal Number and add it to scene
        number = DecimalNumber().set_color(WHITE).scale(5)
        # Add an updater to keep the DecimalNumber centered as its value changes
        number.add_updater(lambda number: number.move_to(ORIGIN))

        self.add(number)

        self.wait()

        # Play the Count Animation to count from 0 to 100 in 4 seconds
        self.play(Count(number, 0, 100), run_time=4, rate_func=linear)

        self.wait()
```

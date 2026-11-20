# Updaters, ValueTracker, transforms, paths, timing, emphasis

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `MovingAngle`: Angle mark and label updating as a line rotates (ValueTracker + always_redraw).
- `MovingDots`: Line kept between two dots via updaters while dots move.
- `MovingFrameBox`: SurroundingRectangle moving across parts of an equation.
- `PointWithTrace`: Hand-rolled trace: an updater extends a VMobject path as a dot moves.
- `PointMovingOnShapes`: GrowFromCenter, MoveAlongPath around a circle, Rotating about a point.
- `ValueTrackerExample`: ValueTracker driving a pointer along a NumberLine.
- `NextToUpdater`: Updater keeping a DecimalNumber beside a moving dot, showing its x.
- `DtUpdater`: Time-based (dt) updater for continuous rotation.
- `AlwaysExample`: Mobject.always shorthand for updaters.
- `TracedPathExample`: TracedPath following a rolling circle.
- `TangentAnimation`: Tangent line sliding along a curve via an updater.
- `ReplacementTransformOrTransform`: Transform vs ReplacementTransform semantics.
- `MoveToTargetExample`: generate_target / MoveToTarget for multi-property changes.
- `RestoreExample`: save_state / Restore to return a mobject to an earlier state.
- `DifferentFadeTransforms`: FadeTransform with stretch and dim_to_match options.
- `MoveAlongPathExample`: MoveAlongPath along a line.
- `SuccessionExample`: Succession: animations played one after another.
- `LaggedStartExample`: LaggedStart with lag_ratio, visualized.
- `LaggedStartMapExample`: LaggedStartMap applying one animation across a group.
- `LagRatios`: How lag_ratio values change staggered timing.
- `Indications`: Emphasis animations: Indicate, Flash, Circumscribe, Wiggle, FocusOn, ApplyWave.
- `UsingCircumscribe`: Circumscribe variants (rectangle, circle, fade).
- `Growing`: GrowFromPoint, GrowFromCenter, GrowFromEdge, GrowArrow, SpinInFromNothing.
- `Fading`: FadeIn/FadeOut with shift and scale.
- `RateFuncExample`: Chart of every built-in rate function.

## MovingAngle

Angle mark and label updating as a line rotates (ValueTracker + always_redraw). *animation*. Source: [docs/source/examples.rst:167](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L167)

```python
from manim import *
class MovingAngle(Scene):
    def construct(self):
        rotation_center = LEFT

        theta_tracker = ValueTracker(110)
        line1 = Line(LEFT, RIGHT)
        line_moving = Line(LEFT, RIGHT)
        line_ref = line_moving.copy()
        line_moving.rotate(
            theta_tracker.get_value() * DEGREES, about_point=rotation_center
        )
        a = Angle(line1, line_moving, radius=0.5, other_angle=False)
        tex = MathTex(r"\theta").move_to(
            Angle(
                line1, line_moving, radius=0.5 + 3 * SMALL_BUFF, other_angle=False
            ).point_from_proportion(0.5)
        )

        self.add(line1, line_moving, a, tex)
        self.wait()

        line_moving.add_updater(
            lambda x: x.become(line_ref.copy()).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )

        a.add_updater(
            lambda x: x.become(Angle(line1, line_moving, radius=0.5, other_angle=False))
        )
        tex.add_updater(
            lambda x: x.move_to(
                Angle(
                    line1, line_moving, radius=0.5 + 3 * SMALL_BUFF, other_angle=False
                ).point_from_proportion(0.5)
            )
        )

        self.play(theta_tracker.animate.set_value(40))
        self.play(theta_tracker.animate.increment_value(140))
        self.play(tex.animate.set_color(RED), run_time=0.5)
        self.play(theta_tracker.animate.set_value(350))
```

## MovingDots

Line kept between two dots via updaters while dots move. *animation*. Source: [docs/source/examples.rst:218](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L218)

```python
from manim import *
class MovingDots(Scene):
    def construct(self):
        d1,d2=Dot(color=BLUE),Dot(color=GREEN)
        dg=VGroup(d1,d2).arrange(RIGHT,buff=1)
        l1=Line(d1.get_center(),d2.get_center()).set_color(RED)
        x=ValueTracker(0)
        y=ValueTracker(0)
        d1.add_updater(lambda z: z.set_x(x.get_value()))
        d2.add_updater(lambda z: z.set_y(y.get_value()))
        l1.add_updater(lambda z: z.match_points(Line(d1.get_center(),d2.get_center())))
        self.add(d1,d2,l1)
        self.play(x.animate.set_value(5))
        self.play(y.animate.set_value(4))
        self.wait()
```

## MovingFrameBox

SurroundingRectangle moving across parts of an equation. *animation*. Source: [docs/source/examples.rst:245](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L245)

```python
from manim import *
class MovingFrameBox(Scene):
    def construct(self):
        text=MathTex(
            "\\frac{d}{dx}f(x)g(x)=","f(x)\\frac{d}{dx}g(x)","+",
            "g(x)\\frac{d}{dx}f(x)"
        )
        self.play(Write(text))
        framebox1 = SurroundingRectangle(text[1], buff = .1)
        framebox2 = SurroundingRectangle(text[3], buff = .1)
        self.play(
            Create(framebox1),
        )
        self.wait()
        self.play(
            ReplacementTransform(framebox1,framebox2),
        )
        self.wait()
```

## PointWithTrace

Hand-rolled trace: an updater extends a VMobject path as a dot moves. *animation*. Source: [docs/source/examples.rst:287](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L287)

```python
from manim import *
class PointWithTrace(Scene):
    def construct(self):
        path = VMobject()
        dot = Dot()
        path.set_points_as_corners([dot.get_center(), dot.get_center()])
        def update_path(path):
            previous_path = path.copy()
            previous_path.add_points_as_corners([dot.get_center()])
            path.become(previous_path)
        path.add_updater(update_path)
        self.add(path, dot)
        self.play(Rotating(dot, angle=PI, about_point=RIGHT, run_time=2))
        self.wait()
        self.play(dot.animate.shift(UP))
        self.play(dot.animate.shift(LEFT))
        self.wait()
```

## PointMovingOnShapes

GrowFromCenter, MoveAlongPath around a circle, Rotating about a point. *animation*. Source: [docs/source/examples.rst:136](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L136)

```python
from manim import *
class PointMovingOnShapes(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        dot = Dot()
        dot2 = dot.copy().shift(RIGHT)
        self.add(dot)

        line = Line([3, 0, 0], [5, 0, 0])
        self.add(line)

        self.play(GrowFromCenter(circle))
        self.play(Transform(dot, dot2))
        self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
        self.play(Rotating(dot, about_point=[2, 0, 0]), run_time=1.5)
        self.wait()
```

## ValueTrackerExample

ValueTracker driving a pointer along a NumberLine. *animation*. Source: [manim/mobject/value_tracker.py:34](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/value_tracker.py#L34)

```python
from manim import *
class ValueTrackerExample(Scene):
    def construct(self):
        number_line = NumberLine()
        pointer = Vector(DOWN)
        label = MathTex("x").add_updater(lambda m: m.next_to(pointer, UP))

        tracker = ValueTracker(0)
        pointer.add_updater(
            lambda m: m.next_to(
                        number_line.n2p(tracker.get_value()),
                        UP
                    )
        )
        self.add(number_line, pointer,label)
        tracker += 1.5
        self.wait(1)
        tracker -= 4
        self.wait(0.5)
        self.play(tracker.animate.set_value(5))
        self.wait(0.5)
        self.play(tracker.animate.set_value(3))
        self.play(tracker.animate.increment_value(-2))
        self.wait(0.5)
```

## NextToUpdater

Updater keeping a DecimalNumber beside a moving dot, showing its x. *animation*. Source: [manim/mobject/mobject.py:1182](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/mobject.py#L1182)

```python
from manim import *
class NextToUpdater(Scene):
    def construct(self):
        def update_label(mobject):
            mobject.set_value(dot.get_center()[0])
            mobject.next_to(dot)

        dot = Dot(RIGHT*3)
        label = DecimalNumber()
        label.add_updater(update_label)
        self.add(dot, label)

        self.play(Rotating(dot, angle=TAU, about_point=ORIGIN, run_time=TAU, rate_func=linear))
```

## DtUpdater

Time-based (dt) updater for continuous rotation. *animation*. Source: [manim/mobject/mobject.py:1197](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/mobject.py#L1197)

```python
from manim import *
class DtUpdater(Scene):
    def construct(self):
        square = Square()

        #Let the square rotate 90° per second
        square.add_updater(lambda mobject, dt: mobject.rotate(dt*90*DEGREES))
        self.add(square)
        self.wait(2)
```

## AlwaysExample

Mobject.always shorthand for updaters. *animation*. Source: [manim/mobject/mobject.py:445](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/mobject.py#L445)

```python
from manim import *
class AlwaysExample(Scene):
    def construct(self):
        sq = Square().to_edge(LEFT)
        t = Text("Hello World!")
        t.always.next_to(sq, UP)
        self.add(sq, t)
        self.play(sq.animate.to_edge(RIGHT))
```

## TracedPathExample

TracedPath following a rolling circle. *animation*. Source: [manim/animation/changing.py:122](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/changing.py#L122)

```python
from manim import *
class TracedPathExample(Scene):
    def construct(self):
        circ = Circle(color=RED).shift(4*LEFT)
        dot = Dot(color=RED).move_to(circ.get_start())
        rolling_circle = VGroup(circ, dot)
        trace = TracedPath(circ.get_start)
        rolling_circle.add_updater(lambda m: m.rotate(-0.3))
        self.add(trace, rolling_circle)
        self.play(rolling_circle.animate.shift(8*RIGHT), run_time=4, rate_func=linear)
```

## TangentAnimation

Tangent line sliding along a curve via an updater. *animation*. Source: [manim/animation/updaters/mobject_update_utils.py:83](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/updaters/mobject_update_utils.py#L83)

```python
from manim import *
class TangentAnimation(Scene):
    def construct(self):
        ax = Axes()
        sine = ax.plot(np.sin, color=RED)
        alpha = ValueTracker(0)
        point = always_redraw(
            lambda: Dot(
                sine.point_from_proportion(alpha.get_value()),
                color=BLUE
            )
        )
        tangent = always_redraw(
            lambda: TangentLine(
                sine,
                alpha=alpha.get_value(),
                color=YELLOW,
                length=4
            )
        )
        self.add(ax, sine, point, tangent)
        self.play(alpha.animate.set_value(1), rate_func=linear, run_time=2)
```

## ReplacementTransformOrTransform

Transform vs ReplacementTransform semantics. *animation*. Source: [manim/animation/transform.py:268](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform.py#L268)

```python
from manim import *
class ReplacementTransformOrTransform(Scene):
    def construct(self):
        # set up the numbers
        r_transform = VGroup(*[Integer(i) for i in range(1,4)])
        text_1 = Text("ReplacementTransform", color=RED)
        r_transform.add(text_1)

        transform = VGroup(*[Integer(i) for i in range(4,7)])
        text_2 = Text("Transform", color=BLUE)
        transform.add(text_2)

        ints = VGroup(r_transform, transform)
        texts = VGroup(text_1, text_2).scale(0.75)
        r_transform.arrange(direction=UP, buff=1)
        transform.arrange(direction=UP, buff=1)

        ints.arrange(buff=2)
        self.add(ints, texts)

        # The mobs replace each other and none are left behind
        self.play(ReplacementTransform(r_transform[0], r_transform[1]))
        self.play(ReplacementTransform(r_transform[1], r_transform[2]))

        # The mobs linger after the Transform()
        self.play(Transform(transform[0], transform[1]))
        self.play(Transform(transform[1], transform[2]))
        self.wait()
```

## MoveToTargetExample

generate_target / MoveToTarget for multi-property changes. *animation*. Source: [manim/animation/transform.py:417](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform.py#L417)

```python
from manim import *
class MoveToTargetExample(Scene):
    def construct(self):
        c = Circle()

        c.generate_target()
        c.target.set_fill(color=GREEN, opacity=0.5)
        c.target.shift(2*RIGHT + UP).scale(0.5)

        self.add(c)
        self.play(MoveToTarget(c))
```

## RestoreExample

save_state / Restore to return a mobject to an earlier state. *animation*. Source: [manim/animation/transform.py:606](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform.py#L606)

```python
from manim import *
class RestoreExample(Scene):
    def construct(self):
        s = Square()
        s.save_state()
        self.play(FadeIn(s))
        self.play(s.animate.set_color(PURPLE).set_opacity(0.5).shift(2*LEFT).scale(3))
        self.play(s.animate.shift(5*DOWN).rotate(PI/4))
        self.wait()
        self.play(Restore(s), run_time=2)
```

## DifferentFadeTransforms

FadeTransform with stretch and dim_to_match options. *animation*. Source: [manim/animation/transform.py:836](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform.py#L836)

```python
from manim import *
class DifferentFadeTransforms(Scene):
    def construct(self):
        starts = [Rectangle(width=4, height=1) for _ in range(3)]
        VGroup(*starts).arrange(DOWN, buff=1).shift(3*LEFT)
        targets = [Circle(fill_opacity=1).scale(0.25) for _ in range(3)]
        VGroup(*targets).arrange(DOWN, buff=1).shift(3*RIGHT)

        self.play(*[FadeIn(s) for s in starts])
        self.play(
            FadeTransform(starts[0], targets[0], stretch=True),
            FadeTransform(starts[1], targets[1], stretch=False, dim_to_match=0),
            FadeTransform(starts[2], targets[2], stretch=False, dim_to_match=1)
        )

        self.play(*[FadeOut(mobj) for mobj in self.mobjects])
```

## MoveAlongPathExample

MoveAlongPath along a line. *animation*. Source: [manim/animation/movement.py:176](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/movement.py#L176)

```python
from manim import *
class MoveAlongPathExample(Scene):
    def construct(self):
        d1 = Dot().set_color(ORANGE)
        l1 = Line(LEFT, RIGHT)
        l2 = VMobject()
        self.add(d1, l1, l2)
        l2.add_updater(lambda x: x.become(Line(LEFT, d1.get_center()).set_color(ORANGE)))
        self.play(MoveAlongPath(d1, l1), rate_func=linear)
```

## SuccessionExample

Succession: animations played one after another. *animation*. Source: [manim/animation/composition.py:217](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/composition.py#L217)

```python
from manim import *
class SuccessionExample(Scene):
    def construct(self):
        dot1 = Dot(point=LEFT * 2 + UP * 2, radius=0.16, color=BLUE)
        dot2 = Dot(point=LEFT * 2 + DOWN * 2, radius=0.16, color=MAROON)
        dot3 = Dot(point=RIGHT * 2 + DOWN * 2, radius=0.16, color=GREEN)
        dot4 = Dot(point=RIGHT * 2 + UP * 2, radius=0.16, color=YELLOW)
        self.add(dot1, dot2, dot3, dot4)

        self.play(Succession(
            dot1.animate.move_to(dot2),
            dot2.animate.move_to(dot3),
            dot3.animate.move_to(dot4),
            dot4.animate.move_to(dot1)
        ))
```

## LaggedStartExample

LaggedStart with lag_ratio, visualized. *animation*. Source: [manim/animation/composition.py:316](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/composition.py#L316)

```python
from manim import *
class LaggedStartExample(Scene):
    def construct(self):
        title = Text("lag_ratio = 0.25").to_edge(UP)

        dot1 = Dot(point=LEFT * 2 + UP, radius=0.16)
        dot2 = Dot(point=LEFT * 2, radius=0.16)
        dot3 = Dot(point=LEFT * 2 + DOWN, radius=0.16)
        line_25 = DashedLine(
            start=LEFT + UP * 2,
            end=LEFT + DOWN * 2,
            color=RED
        )
        label = Text("25%", font_size=24).next_to(line_25, UP)
        self.add(title, dot1, dot2, dot3, line_25, label)

        self.play(LaggedStart(
            dot1.animate.shift(RIGHT * 4),
            dot2.animate.shift(RIGHT * 4),
            dot3.animate.shift(RIGHT * 4),
            lag_ratio=0.25,
            run_time=4
        ))
```

## LaggedStartMapExample

LaggedStartMap applying one animation across a group. *animation*. Source: [manim/animation/composition.py:379](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/composition.py#L379)

```python
from manim import *
class LaggedStartMapExample(Scene):
    def construct(self):
        title = Tex("LaggedStartMap").to_edge(UP, buff=LARGE_BUFF)
        dots = VGroup(
            *[Dot(radius=0.16) for _ in range(35)]
            ).arrange_in_grid(rows=5, cols=7, buff=MED_LARGE_BUFF)
        self.add(dots, title)

        # Animate yellow ripple effect
        for mob in dots, title:
            self.play(LaggedStartMap(
                ApplyMethod, mob,
                lambda m : (m.set_color, YELLOW),
                lag_ratio = 0.1,
                rate_func = there_and_back,
                run_time = 2
            ))
```

## LagRatios

How lag_ratio values change staggered timing. *animation*. Source: [manim/animation/animation.py:82](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/animation.py#L82)

```python
from manim import *
class LagRatios(Scene):
    def construct(self):
        ratios = [0, 0.1, 0.5, 1, 2]  # demonstrated lag_ratios

        # Create dot groups
        group = VGroup(*[Dot() for _ in range(4)]).arrange_submobjects()
        groups = VGroup(*[group.copy() for _ in ratios]).arrange_submobjects(buff=1)
        self.add(groups)

        # Label groups
        self.add(Text("lag_ratio = ", font_size=36).next_to(groups, UP, buff=1.5))
        for group, ratio in zip(groups, ratios):
            self.add(Text(str(ratio), font_size=36).next_to(group, UP))

        #Animate groups with different lag_ratios
        self.play(AnimationGroup(*[
            group.animate(lag_ratio=ratio, run_time=1.5).shift(DOWN * 2)
            for group, ratio in zip(groups, ratios)
        ]))

        # lag_ratio also works recursively on nested submobjects:
        self.play(groups.animate(run_time=1, lag_ratio=0.1).shift(UP * 2))
```

## Indications

Emphasis animations: Indicate, Flash, Circumscribe, Wiggle, FocusOn, ApplyWave. *animation*. Source: [manim/animation/indication.py:6](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/indication.py#L6)

```python
from manim import *
class Indications(Scene):
    def construct(self):
        indications = [ApplyWave,Circumscribe,Flash,FocusOn,Indicate,ShowPassingFlash,Wiggle]
        names = [Tex(i.__name__).scale(3) for i in indications]

        self.add(names[0])
        for i in range(len(names)):
            if indications[i] is Flash:
                self.play(Flash(UP))
            elif indications[i] is ShowPassingFlash:
                self.play(ShowPassingFlash(Underline(names[i])))
            else:
                self.play(indications[i](names[i]))
            self.play(AnimationGroup(
                FadeOut(names[i], shift=UP*1.5),
                FadeIn(names[(i+1)%len(names)], shift=UP*1.5),
            ))
```

## UsingCircumscribe

Circumscribe variants (rectangle, circle, fade). *animation*. Source: [manim/animation/indication.py:599](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/indication.py#L599)

```python
from manim import *
class UsingCircumscribe(Scene):
    def construct(self):
        lbl = Tex(r"Circum-\\scribe").scale(2)
        self.add(lbl)
        self.play(Circumscribe(lbl))
        self.play(Circumscribe(lbl, Circle))
        self.play(Circumscribe(lbl, fade_out=True))
        self.play(Circumscribe(lbl, time_width=2))
        self.play(Circumscribe(lbl, Circle, True))
```

## Growing

GrowFromPoint, GrowFromCenter, GrowFromEdge, GrowArrow, SpinInFromNothing. *animation*. Source: [manim/animation/growing.py:3](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/growing.py#L3)

```python
from manim import *
class Growing(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        triangle = Triangle()
        arrow = Arrow(LEFT, RIGHT)
        star = Star()

        VGroup(square, circle, triangle).set_x(0).arrange(buff=1.5).set_y(2)
        VGroup(arrow, star).move_to(DOWN).set_x(0).arrange(buff=1.5).set_y(-2)

        self.play(GrowFromPoint(square, ORIGIN))
        self.play(GrowFromCenter(circle))
        self.play(GrowFromEdge(triangle, DOWN))
        self.play(GrowArrow(arrow))
        self.play(SpinInFromNothing(star))
```

## Fading

FadeIn/FadeOut with shift and scale. *animation*. Source: [manim/animation/fading.py:3](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/fading.py#L3)

```python
from manim import *
class Fading(Scene):
    def construct(self):
        tex_in = Tex("Fade", "In").scale(3)
        tex_out = Tex("Fade", "Out").scale(3)
        self.play(FadeIn(tex_in, shift=DOWN, scale=0.66))
        self.play(ReplacementTransform(tex_in, tex_out))
        self.play(FadeOut(tex_out, shift=DOWN * 2, scale=1.5))
```

## RateFuncExample

Chart of every built-in rate function. *still*. Source: [manim/utils/rate_functions.py:5](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/utils/rate_functions.py#L5)

```python
from manim import *
class RateFuncExample(Scene):
    def construct(self):
        x = VGroup()
        for k, v in rate_functions.__dict__.items():
            if "function" in str(v):
                if (
                    not k.startswith("__")
                    and not k.startswith("sqrt")
                    and not k.startswith("bezier")
                ):
                    try:
                        rate_func = v
                        plot = (
                            ParametricFunction(
                                lambda x: [x, rate_func(x), 0],
                                t_range=[0, 1, .01],
                                use_smoothing=False,
                                color=YELLOW,
                            )
                            .stretch_to_fit_width(1.5)
                            .stretch_to_fit_height(1)
                        )
                        plot_bg = SurroundingRectangle(plot).set_color(WHITE)
                        plot_title = (
                            Text(rate_func.__name__, weight=BOLD)
                            .scale(0.5)
                            .next_to(plot_bg, UP, buff=0.1)
                        )
                        x.add(VGroup(plot_bg, plot, plot_title))
                    except Exception: # because functions `not_quite_there`, `function squish_rate_func` are not working.
                        pass
        x.arrange_in_grid(cols=8)
        x.height = config.frame_height
        x.width = config.frame_width
        x.move_to(ORIGIN).scale(0.95)
        self.add(x)
```

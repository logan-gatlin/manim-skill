# Axes, function plots, calculus visuals, number lines/planes, charts

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `SinAndCosFunctionPlot`: Axes with sin/cos plots, axis and graph labels, and a vertical reference line.
- `GraphAreaPlot`: Shaded area between two curves and Riemann rectangles.
- `HeatDiagramPlot`: plot_line_graph from data points with Tex axis labels.
- `ArgMinExample`: ValueTracker moving a dot along a curve to its minimum.
- `PolygonOnAxes`: Rectangle under a curve that resizes as a point slides along it.
- `CoordSysExample`: Family of power curves on Axes with title and labeled corner point.
- `GetGraphLabelExample`: Labeling a curve at a chosen x with a dot.
- `GetLinesToPointExample`: Dashed lines from a point to both axes.
- `GetRiemannRectanglesExample`: get_riemann_rectangles with left, right and signed-area variants.
- `GetAreaExample`: get_area for the region under a curve over an interval.
- `DerivativeGraphExample`: Plotting a function and its derivative on a NumberPlane.
- `GetSecantSlopeGroupExample`: Secant slope group (dx/dy triangle) on a curve.
- `DiscontinuousExample`: Plotting across discontinuities: naive vs discontinuities= and dt=.
- `ImplicitExample`: Implicit curve plotting (plot_implicit_curve).
- `ParametricCurveExample`: Parametric curve on Axes (cardioid).
- `PolarGraphExample`: Polar graph on a PolarPlane (rose curve).
- `LogScalingExample`: Logarithmic y-axis scaling.
- `LineGraphExample`: Line graph from x/y data with vertex dots on a grid.
- `NumberLineExample`: NumberLine variants: ranges, tick labels, decimal steps, rotation.
- `NumberPlaneExample`: Plain NumberPlane background grid.
- `PolarPlaneExample`: PolarPlane with radian angle labels.
- `ComplexPlaneExample`: ComplexPlane with labeled complex points.
- `BarChartExample`: BarChart with names, colors and value labels.
- `ChangeBarValuesExample`: Animating BarChart values with change_bar_values.
- `GradientImageFromArray`: ImageMobject built from a NumPy gradient array.

## SinAndCosFunctionPlot

Axes with sin/cos plots, axis and graph labels, and a vertical reference line. *still*. Source: [docs/source/examples.rst:312](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L312)

```python
from manim import *
class SinAndCosFunctionPlot(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-10, 10.3, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=10,
            axis_config={"color": GREEN},
            x_axis_config={
                "numbers_to_include": np.arange(-10, 10.01, 2),
                "numbers_with_elongated_ticks": np.arange(-10, 10.01, 2),
            },
            tips=False,
        )
        axes_labels = axes.get_axis_labels()
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)

        sin_label = axes.get_graph_label(
            sin_graph, "\\sin(x)", x_val=-10, direction=UP / 2
        )
        cos_label = axes.get_graph_label(cos_graph, label="\\cos(x)")

        vert_line = axes.get_vertical_line(
            axes.i2gp(TAU, cos_graph), color=YELLOW, line_func=Line
        )
        line_label = axes.get_graph_label(
            cos_graph, r"x=2\pi", x_val=TAU, direction=UR, color=WHITE
        )

        plot = VGroup(axes, sin_graph, cos_graph, vert_line)
        labels = VGroup(axes_labels, sin_label, cos_label, line_label)
        self.add(plot, labels)
```

## GraphAreaPlot

Shaded area between two curves and Riemann rectangles. *still*. Source: [docs/source/examples.rst:379](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L379)

```python
from manim import *
class GraphAreaPlot(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 5],
            y_range=[0, 6],
            x_axis_config={"numbers_to_include": [2, 3]},
            tips=False,
        )

        labels = ax.get_axis_labels()

        curve_1 = ax.plot(lambda x: 4 * x - x ** 2, x_range=[0, 4], color=BLUE_C)
        curve_2 = ax.plot(
            lambda x: 0.8 * x ** 2 - 3 * x + 4,
            x_range=[0, 4],
            color=GREEN_B,
        )

        line_1 = ax.get_vertical_line(ax.input_to_graph_point(2, curve_1), color=YELLOW)
        line_2 = ax.get_vertical_line(ax.i2gp(3, curve_1), color=YELLOW)

        riemann_area = ax.get_riemann_rectangles(curve_1, x_range=[0.3, 0.6], dx=0.03, color=BLUE, fill_opacity=0.5)
        area = ax.get_area(curve_2, [2, 3], bounded_graph=curve_1, color=GREY, opacity=0.5)

        self.add(ax, labels, curve_1, curve_2, line_1, line_2, riemann_area, area)
```

## HeatDiagramPlot

plot_line_graph from data points with Tex axis labels. *still*. Source: [docs/source/examples.rst:468](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L468)

```python
from manim import *
class HeatDiagramPlot(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 40, 5],
            y_range=[-8, 32, 5],
            x_length=9,
            y_length=6,
            x_axis_config={"numbers_to_include": np.arange(0, 40, 5)},
            y_axis_config={"numbers_to_include": np.arange(-5, 34, 5)},
            tips=False,
        )
        labels = ax.get_axis_labels(
            x_label=Tex(r"$\Delta Q$"), y_label=Tex(r"T[$^\circ C$]")
        )

        x_vals = [0, 8, 38, 39]
        y_vals = [20, 0, 0, -5]
        graph = ax.plot_line_graph(x_values=x_vals, y_values=y_vals)

        self.add(ax, labels, graph)
```

## ArgMinExample

ValueTracker moving a dot along a curve to its minimum. *animation*. Source: [docs/source/examples.rst:353](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L353)

```python
from manim import *
class ArgMinExample(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 10], y_range=[0, 100, 10], axis_config={"include_tip": False}
        )
        labels = ax.get_axis_labels(x_label="x", y_label="f(x)")

        t = ValueTracker(0)

        def func(x):
            return 2 * (x - 5) ** 2
        graph = ax.plot(func, color=MAROON)

        initial_point = [ax.coords_to_point(t.get_value(), func(t.get_value()))]
        dot = Dot(point=initial_point)

        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), func(t.get_value()))))
        x_space = np.linspace(*ax.x_range[:2],200)
        minimum_index = func(x_space).argmin()

        self.add(ax, labels, graph, dot)
        self.play(t.animate.set_value(x_space[minimum_index]))
        self.wait()
```

## PolygonOnAxes

Rectangle under a curve that resizes as a point slides along it. *animation*. Source: [docs/source/examples.rst:410](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L410)

```python
from manim import *
class PolygonOnAxes(Scene):
    def get_rectangle_corners(self, bottom_left, top_right):
        return [
            (top_right[0], top_right[1]),
            (bottom_left[0], top_right[1]),
            (bottom_left[0], bottom_left[1]),
            (top_right[0], bottom_left[1]),
        ]

    def construct(self):
        ax = Axes(
            x_range=[0, 10],
            y_range=[0, 10],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": False},
        )

        t = ValueTracker(5)
        k = 25

        graph = ax.plot(
            lambda x: k / x,
            color=YELLOW_D,
            x_range=[k / 10, 10.0, 0.01],
            use_smoothing=False,
        )

        def get_rectangle():
            polygon = Polygon(
                *[
                    ax.c2p(*i)
                    for i in self.get_rectangle_corners(
                        (0, 0), (t.get_value(), k / t.get_value())
                    )
                ]
            )
            polygon.stroke_width = 1
            polygon.set_fill(BLUE, opacity=0.5)
            polygon.set_stroke(YELLOW_B)
            return polygon

        polygon = always_redraw(get_rectangle)

        dot = Dot()
        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), k / t.get_value())))
        dot.set_z_index(10)

        self.add(ax, graph, dot)
        self.play(Create(polygon))
        self.play(t.animate.set_value(10))
        self.play(t.animate.set_value(k / 10))
        self.play(t.animate.set_value(5))
```

## CoordSysExample

Family of power curves on Axes with title and labeled corner point. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:77](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L77)

```python
from manim import *
class CoordSysExample(Scene):
    def construct(self):
        # the location of the ticks depends on the x_range and y_range.
        grid = Axes(
            x_range=[0, 1, 0.05],  # step size determines num_decimal_places.
            y_range=[0, 1, 0.05],
            x_length=9,
            y_length=5.5,
            axis_config={
                "numbers_to_include": np.arange(0, 1 + 0.1, 0.1),
                "font_size": 24,
            },
            tips=False,
        )

        # Labels for the x-axis and y-axis.
        y_label = grid.get_y_axis_label("y", edge=LEFT, direction=LEFT, buff=0.4)
        x_label = grid.get_x_axis_label("x")
        grid_labels = VGroup(x_label, y_label)

        graphs = VGroup()
        for n in np.arange(1, 20 + 0.5, 0.5):
            graphs += grid.plot(lambda x: x ** n, color=WHITE)
            graphs += grid.plot(
                lambda x: x ** (1 / n), color=WHITE, use_smoothing=False
            )

        # Extra lines and labels for point (1,1)
        graphs += grid.get_horizontal_line(grid @ (1, 1, 0), color=BLUE)
        graphs += grid.get_vertical_line(grid @ (1, 1, 0), color=BLUE)
        graphs += Dot(point=grid @ (1, 1, 0), color=YELLOW)
        graphs += Tex("(1,1)").scale(0.75).next_to(grid @ (1, 1, 0))
        title = Title(
            # spaces between braces to prevent SyntaxError
            r"Graphs of $y=x^{ {1}\over{n} }$ and $y=x^n (n=1,2,3,...,20)$",
            include_underline=False,
            font_size=40,
        )

        self.add(title, graphs, grid, grid_labels)
```

## GetGraphLabelExample

Labeling a curve at a chosen x with a dot. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1146](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1146)

```python
from manim import *
class GetGraphLabelExample(Scene):
    def construct(self):
        ax = Axes()
        sin = ax.plot(lambda x: np.sin(x), color=PURPLE_B)
        label = ax.get_graph_label(
            graph=sin,
            label= MathTex(r"\frac{\pi}{2}"),
            x_val=PI / 2,
            dot=True,
            direction=UR,
        )

        self.add(ax, sin, label)
```

## GetLinesToPointExample

Dashed lines from a point to both axes. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:621](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L621)

```python
from manim import *
class GetLinesToPointExample(Scene):
    def construct(self):
        ax = Axes()
        circ = Circle(radius=0.5).move_to([-4, -1.5, 0])

        lines_1 = ax.get_lines_to_point(circ.get_right(), color=GREEN_B)
        lines_2 = ax.get_lines_to_point(circ.get_corner(DL), color=BLUE_B)
        self.add(ax, lines_1, lines_2, circ)
```

## GetRiemannRectanglesExample

get_riemann_rectangles with left, right and signed-area variants. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1242](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1242)

```python
from manim import *
class GetRiemannRectanglesExample(Scene):
    def construct(self):
        ax = Axes(y_range=[-2, 10])
        quadratic = ax.plot(lambda x: 0.5 * x ** 2 - 0.5)

        # the rectangles are constructed from their top right corner.
        # passing an iterable to `color` produces a gradient
        rects_right = ax.get_riemann_rectangles(
            quadratic,
            x_range=[-4, -3],
            dx=0.25,
            color=(TEAL, BLUE_B, DARK_BLUE),
            input_sample_type="right",
        )

        # the colour of rectangles below the x-axis is inverted
        # due to show_signed_area
        rects_left = ax.get_riemann_rectangles(
            quadratic, x_range=[-1.5, 1.5], dx=0.15, color=YELLOW
        )

        bounding_line = ax.plot(
            lambda x: 1.5 * x, color=BLUE_B, x_range=[3.3, 6]
        )
        bounded_rects = ax.get_riemann_rectangles(
            bounding_line,
            bounded_graph=quadratic,
            dx=0.15,
            x_range=[4, 5],
            show_signed_area=False,
            color=(MAROON_A, RED_B, PURPLE_D),
        )

        self.add(
            ax, bounding_line, quadratic, rects_right, rects_left, bounded_rects
        )
```

## GetAreaExample

get_area for the region under a curve over an interval. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1390](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1390)

```python
from manim import *
class GetAreaExample(Scene):
    def construct(self):
        ax = Axes().add_coordinates()
        curve = ax.plot(lambda x: 2 * np.sin(x), color=DARK_BLUE)
        area = ax.get_area(
            curve,
            x_range=(PI / 2, 3 * PI / 2),
            color=(GREEN_B, GREEN_D),
            opacity=1,
        )

        self.add(ax, curve, area)
```

## DerivativeGraphExample

Plotting a function and its derivative on a NumberPlane. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1529](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1529)

```python
from manim import *
class DerivativeGraphExample(Scene):
    def construct(self):
        ax = NumberPlane(y_range=[-1, 7], background_line_style={"stroke_opacity": 0.4})

        curve_1 = ax.plot(lambda x: x ** 2, color=PURPLE_B)
        curve_2 = ax.plot_derivative_graph(curve_1)
        curves = VGroup(curve_1, curve_2)

        label_1 = ax.get_graph_label(curve_1, "x^2", x_val=-2, direction=DL)
        label_2 = ax.get_graph_label(curve_2, "2x", x_val=3, direction=RIGHT)
        labels = VGroup(label_1, label_2)

        self.add(ax, curves, labels)
```

## GetSecantSlopeGroupExample

Secant slope group (dx/dy triangle) on a curve. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1660](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1660)

```python
from manim import *
class GetSecantSlopeGroupExample(Scene):
    def construct(self):
        ax = Axes(y_range=[-1, 7])
        graph = ax.plot(lambda x: 1 / 4 * x ** 2, color=BLUE)
        slopes = ax.get_secant_slope_group(
            x=2.0,
            graph=graph,
            dx=1.0,
            dx_label=Tex("dx = 1.0"),
            dy_label="dy",
            dx_line_color=GREEN_B,
            secant_line_length=4,
            secant_line_color=RED_D,
        )

        self.add(ax, graph, slopes)
```

## DiscontinuousExample

Plotting across discontinuities: naive vs discontinuities= and dt=. *still*. Source: [manim/mobject/graphing/functions.py:87](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/functions.py#L87)

```python
from manim import *
class DiscontinuousExample(Scene):
    def construct(self):
        ax1 = NumberPlane((-3, 3), (-4, 4))
        ax2 = NumberPlane((-3, 3), (-4, 4))
        VGroup(ax1, ax2).arrange()
        discontinuous_function = lambda x: (x ** 2 - 2) / (x ** 2 - 4)
        incorrect = ax1.plot(discontinuous_function, color=RED)
        correct = ax2.plot(
            discontinuous_function,
            discontinuities=[-2, 2],  # discontinuous points
            dt=0.1,  # left and right tolerance of discontinuity
            color=GREEN,
        )
        self.add(ax1, ax2, incorrect, correct)
```

## ImplicitExample

Implicit curve plotting (plot_implicit_curve). *still*. Source: [manim/mobject/graphing/coordinate_systems.py:820](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L820)

```python
from manim import *
class ImplicitExample(Scene):
    def construct(self):
        ax = Axes()
        a = ax.plot_implicit_curve(
            lambda x, y: y * (x - y) ** 2 - 4 * x - 8, color=BLUE
        )
        self.add(ax, a)
```

## ParametricCurveExample

Parametric curve on Axes (cardioid). *still*. Source: [manim/mobject/graphing/coordinate_systems.py:868](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L868)

```python
from manim import *
class ParametricCurveExample(Scene):
    def construct(self):
        ax = Axes()
        cardioid = ax.plot_parametric_curve(
            lambda t: np.array(
                [
                    np.exp(1) * np.cos(t) * (1 - np.cos(t)),
                    np.exp(1) * np.sin(t) * (1 - np.cos(t)),
                    0,
                ]
            ),
            t_range=[0, 2 * PI],
            color="#0FF1CE",
        )
        self.add(ax, cardioid)
```

## PolarGraphExample

Polar graph on a PolarPlane (rose curve). *still*. Source: [manim/mobject/graphing/coordinate_systems.py:915](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L915)

```python
from manim import *
class PolarGraphExample(Scene):
    def construct(self):
        plane = PolarPlane()
        r = lambda theta: 2 * np.sin(theta * 5)
        graph = plane.plot_polar_graph(r, [0, 2 * PI], color=ORANGE)
        self.add(plane, graph)
```

## LogScalingExample

Logarithmic y-axis scaling. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:1902](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L1902)

```python
from manim import *
class LogScalingExample(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 6, 1],
            tips=False,
            axis_config={"include_numbers": True},
            y_axis_config={"scaling": LogBase(custom_labels=True)},
        )

        # x_min must be > 0 because log is undefined at 0.
        graph = ax.plot(lambda x: x ** 2, x_range=[0.001, 10], use_smoothing=False)
        self.add(ax, graph)
```

## LineGraphExample

Line graph from x/y data with vertex dots on a grid. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:2348](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L2348)

```python
from manim import *
class LineGraphExample(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range = (0, 7),
            y_range = (0, 5),
            x_length = 7,
            axis_config={"include_numbers": True},
        )
        plane.center()
        line_graph = plane.plot_line_graph(
            x_values = [0, 1.5, 2, 2.8, 4, 6.25],
            y_values = [1, 3, 2.25, 4, 2.5, 1.75],
            line_color=GOLD_E,
            vertex_dot_style=dict(stroke_width=3,  fill_color=PURPLE),
            stroke_width = 4,
        )
        self.add(plane, line_graph)
```

## NumberLineExample

NumberLine variants: ranges, tick labels, decimal steps, rotation. *still*. Source: [manim/mobject/graphing/number_line.py:99](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/number_line.py#L99)

```python
from manim import *
class NumberLineExample(Scene):
    def construct(self):
        l0 = NumberLine(
            x_range=[-10, 10, 2],
            length=10,
            color=BLUE,
            include_numbers=True,
            label_direction=UP,
        )

        l1 = NumberLine(
            x_range=[-10, 10, 2],
            unit_size=0.5,
            numbers_with_elongated_ticks=[-2, 4],
            include_numbers=True,
            font_size=24,
        )
        num6 = l1.numbers[8]
        num6.set_color(RED)

        l2 = NumberLine(
            x_range=[-2.5, 2.5 + 0.5, 0.5],
            length=12,
            decimal_number_config={"num_decimal_places": 2},
            include_numbers=True,
        )

        l3 = NumberLine(
            x_range=[-5, 5 + 1, 1],
            length=6,
            include_tip=True,
            include_numbers=True,
            rotation=10 * DEGREES,
        )

        line_group = VGroup(l0, l1, l2, l3).arrange(DOWN, buff=1)
        self.add(line_group)
```

## NumberPlaneExample

Plain NumberPlane background grid. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:2726](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L2726)

```python
from manim import *
class NumberPlaneExample(Scene):
    def construct(self):
        number_plane = NumberPlane(
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 4,
                "stroke_opacity": 0.6
            }
        )
        self.add(number_plane)
```

## PolarPlaneExample

PolarPlane with radian angle labels. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:3018](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L3018)

```python
from manim import *
class PolarPlaneExample(Scene):
    def construct(self):
        polarplane_pi = PolarPlane(
            azimuth_units="PI radians",
            size=6,
            azimuth_label_font_size=33.6,
            radius_config={"font_size": 33.6},
        ).add_coordinates()
        self.add(polarplane_pi)
```

## ComplexPlaneExample

ComplexPlane with labeled complex points. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:3385](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L3385)

```python
from manim import *
class ComplexPlaneExample(Scene):
    def construct(self):
        plane = ComplexPlane().add_coordinates()
        self.add(plane)
        d1 = Dot(plane.n2p(2 + 1j), color=YELLOW)
        d2 = Dot(plane.n2p(-3 - 2j), color=YELLOW)
        label1 = MathTex("2+i").next_to(d1, UR, 0.1)
        label2 = MathTex("-3-2i").next_to(d2, UR, 0.1)
        self.add(
            d1,
            label1,
            d2,
            label2,
        )
```

## BarChartExample

BarChart with names, colors and value labels. *still*. Source: [manim/mobject/graphing/probability.py:255](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/probability.py#L255)

```python
from manim import *
class BarChartExample(Scene):
    def construct(self):
        chart = BarChart(
            values=[-5, 40, -10, 20, -3],
            bar_names=["one", "two", "three", "four", "five"],
            y_range=[-20, 50, 10],
            y_length=6,
            x_length=10,
            x_axis_config={"font_size": 36},
        )

        c_bar_lbls = chart.get_bar_labels(font_size=48)

        self.add(chart, c_bar_lbls)
```

## ChangeBarValuesExample

Animating BarChart values with change_bar_values. *still*. Source: [manim/mobject/graphing/probability.py:503](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/probability.py#L503)

```python
from manim import *
class ChangeBarValuesExample(Scene):
    def construct(self):
        values=[-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]

        chart = BarChart(
            values,
            y_range=[-10, 10, 2],
            y_axis_config={"font_size": 24},
        )
        self.add(chart)

        chart.change_bar_values(list(reversed(values)))
        self.add(chart.get_bar_labels(font_size=24))
```

## GradientImageFromArray

ImageMobject built from a NumPy gradient array. *still*. Source: [docs/source/examples.rst:82](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L82)

```python
from manim import *
class GradientImageFromArray(Scene):
    def construct(self):
        n = 256
        imageArray = np.uint8(
            [[i * 256 / n for i in range(0, n)] for _ in range(0, n)]
        )
        image = ImageMobject(imageArray).scale(2)
        image.background_rectangle = SurroundingRectangle(image, color=GREEN)
        self.add(image, image.background_rectangle)
```

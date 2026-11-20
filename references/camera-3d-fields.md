# Moving/zooming camera, 3D axes and surfaces, vector fields

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `FollowingGraphCamera`: MovingCameraScene following a dot along a graph.
- `MovingCameraOnGraph`: Camera zooming onto a point of a graph and back.
- `MovingAndZoomingCamera`: Moving and zooming the camera frame between objects.
- `ChangingCameraWidthAndRestore`: Changing camera width and restoring it.
- `UseZoomedScene`: ZoomedScene with an inset zoomed display.
- `FixedInFrameMObjectTest`: ThreeDScene with 2D text fixed in the frame.
- `ThreeDLightSourcePosition`: 3D sphere with a custom light source position.
- `ThreeDCameraRotation`: Ambient camera rotation, then move_camera back.
- `ThreeDCameraIllusionRotation`: 3D illusion camera rotation (wobble).
- `ThreeDSurfacePlot`: Gaussian surface plot over ThreeDAxes.
- `PlotSurfaceExample`: plot_surface with a colorscale.
- `FillByValueExample`: Surface colored by value (fill_by_value).
- `ThreeDParametricSpring`: 3D parametric curve (helix).
- `ExampleArrow3D`: Arrow3D on ThreeDAxes.
- `ExampleSphere`: Spheres with different centers, radii and resolutions.
- `Coloring`: ArrowVectorField with a custom color scheme.
- `StreamLineCreation`: StreamLines being created over a vector field.
- `ContinuousMotion`: StreamLines in continuous motion.
- `Nudging`: Mobjects nudged along a vector field.

## FollowingGraphCamera

MovingCameraScene following a dot along a graph. *animation*. Source: [docs/source/examples.rst:498](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L498)

```python
from manim import *
class FollowingGraphCamera(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()

        # create the axes and the curve
        ax = Axes(x_range=[-1, 10], y_range=[-1, 10])
        graph = ax.plot(lambda x: np.sin(x), color=BLUE, x_range=[0, 3 * PI])

        # create dots based on the graph
        moving_dot = Dot(ax.i2gp(graph.t_min, graph), color=ORANGE)
        dot_1 = Dot(ax.i2gp(graph.t_min, graph))
        dot_2 = Dot(ax.i2gp(graph.t_max, graph))

        self.add(ax, graph, dot_1, dot_2, moving_dot)
        self.play(self.camera.frame.animate.scale(0.5).move_to(moving_dot))

        def update_curve(mob):
            mob.move_to(moving_dot.get_center())

        self.camera.frame.add_updater(update_curve)
        self.play(MoveAlongPath(moving_dot, graph, rate_func=linear))
        self.camera.frame.remove_updater(update_curve)

        self.play(Restore(self.camera.frame))
```

## MovingCameraOnGraph

Camera zooming onto a point of a graph and back. *animation*. Source: [manim/scene/moving_camera_scene.py:49](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/scene/moving_camera_scene.py#L49)

```python
from manim import *
class MovingCameraOnGraph(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()

        ax = Axes(x_range=[-1, 10], y_range=[-1, 10])
        graph = ax.plot(lambda x: np.sin(x), color=WHITE, x_range=[0, 3 * PI])

        dot_1 = Dot(ax.i2gp(graph.t_min, graph))
        dot_2 = Dot(ax.i2gp(graph.t_max, graph))
        self.add(ax, graph, dot_1, dot_2)

        self.play(self.camera.frame.animate.scale(0.5).move_to(dot_1))
        self.play(self.camera.frame.animate.move_to(dot_2))
        self.play(Restore(self.camera.frame))
        self.wait()
```

## MovingAndZoomingCamera

Moving and zooming the camera frame between objects. *animation*. Source: [manim/scene/moving_camera_scene.py:36](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/scene/moving_camera_scene.py#L36)

```python
from manim import *
class MovingAndZoomingCamera(MovingCameraScene):
    def construct(self):
        s = Square(color=BLUE, fill_opacity=0.5).move_to(2 * LEFT)
        t = Triangle(color=YELLOW, fill_opacity=0.5).move_to(2 * RIGHT)
        self.add(s, t)
        self.play(self.camera.frame.animate.move_to(s).set(width=s.width*2))
        self.wait(0.3)
        self.play(self.camera.frame.animate.move_to(t).set(width=t.width*2))

        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=14))
```

## ChangingCameraWidthAndRestore

Changing camera width and restoring it. *animation*. Source: [manim/scene/moving_camera_scene.py:11](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/scene/moving_camera_scene.py#L11)

```python
from manim import *
class ChangingCameraWidthAndRestore(MovingCameraScene):
    def construct(self):
        text = Text("Hello World").set_color(BLUE)
        self.add(text)
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.set(width=text.width * 1.2))
        self.wait(0.3)
        self.play(Restore(self.camera.frame))
```

## UseZoomedScene

ZoomedScene with an inset zoomed display. *animation*. Source: [manim/scene/zoomed_scene.py:7](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/scene/zoomed_scene.py#L7)

```python
from manim import *
class UseZoomedScene(ZoomedScene):
    def construct(self):
        dot = Dot().set_color(GREEN)
        self.add(dot)
        self.wait(1)
        self.activate_zooming(animate=False)
        self.wait(1)
        self.play(dot.animate.shift(LEFT))
```

## FixedInFrameMObjectTest

ThreeDScene with 2D text fixed in the frame. *still*. Source: [docs/source/examples.rst:598](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L598)

```python
from manim import *
class FixedInFrameMObjectTest(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        text3d = Text("This is a 3D text")
        self.add_fixed_in_frame_mobjects(text3d)
        text3d.to_corner(UL)
        self.add(axes)
        self.wait()
```

## ThreeDLightSourcePosition

3D sphere with a custom light source position. *still*. Source: [docs/source/examples.rst:613](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L613)

```python
from manim import *
class ThreeDLightSourcePosition(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        sphere = Surface(
            lambda u, v: np.array([
                1.5 * np.cos(u) * np.cos(v),
                1.5 * np.cos(u) * np.sin(v),
                1.5 * np.sin(u)
            ]), v_range=[0, TAU], u_range=[-PI / 2, PI / 2],
            checkerboard_colors=[RED_D, RED_E], resolution=(15, 32)
        )
        self.renderer.camera.light_source.move_to(3*IN) # changes the source of the light
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(axes, sphere)
```

## ThreeDCameraRotation

Ambient camera rotation, then move_camera back. *animation*. Source: [docs/source/examples.rst:634](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L634)

```python
from manim import *
class ThreeDCameraRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        circle=Circle()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(circle,axes)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait()
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
        self.wait()
```

## ThreeDCameraIllusionRotation

3D illusion camera rotation (wobble). *animation*. Source: [docs/source/examples.rst:650](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L650)

```python
from manim import *
class ThreeDCameraIllusionRotation(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        circle=Circle()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(circle,axes)
        self.begin_3dillusion_camera_rotation(rate=2)
        self.wait(PI/2)
        self.stop_3dillusion_camera_rotation()
```

## ThreeDSurfacePlot

Gaussian surface plot over ThreeDAxes. *still*. Source: [docs/source/examples.rst:664](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L664)

```python
from manim import *
class ThreeDSurfacePlot(ThreeDScene):
    def construct(self):
        resolution_fa = 24
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)

        def param_gauss(u, v):
            x = u
            y = v
            sigma, mu = 0.4, [0.0, 0.0]
            d = np.linalg.norm(np.array([x - mu[0], y - mu[1]]))
            z = np.exp(-(d ** 2 / (2.0 * sigma ** 2)))
            return np.array([x, y, z])

        gauss_plane = Surface(
            param_gauss,
            resolution=(resolution_fa, resolution_fa),
            v_range=[-2, +2],
            u_range=[-2, +2]
        )

        gauss_plane.scale(2, about_point=ORIGIN)
        gauss_plane.set_style(fill_opacity=1,stroke_color=GREEN)
        gauss_plane.set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)
        axes = ThreeDAxes()
        self.add(axes,gauss_plane)
```

## PlotSurfaceExample

plot_surface with a colorscale. *still*. Source: [manim/mobject/graphing/coordinate_systems.py:975](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/coordinate_systems.py#L975)

```python
from manim import *
class PlotSurfaceExample(ThreeDScene):
    def construct(self):
        resolution_fa = 16
        self.set_camera_orientation(phi=75 * DEGREES, theta=-60 * DEGREES)
        axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-5, 5, 1))
        def param_trig(u, v):
            x = u
            y = v
            z = 2 * np.sin(x) + 2 * np.cos(y)
            return z
        trig_plane = axes.plot_surface(
            param_trig,
            resolution=(resolution_fa, resolution_fa),
            u_range = (-3, 3),
            v_range = (-3, 3),
            colorscale = [BLUE, GREEN, YELLOW, ORANGE, RED],
            )
        self.add(axes, trig_plane)
```

## FillByValueExample

Surface colored by value (fill_by_value). *still*. Source: [manim/mobject/three_d/three_dimensions.py:265](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/three_d/three_dimensions.py#L265)

```python
from manim import *
class FillByValueExample(ThreeDScene):
    def construct(self):
        resolution_fa = 8
        self.set_camera_orientation(phi=75 * DEGREES, theta=-160 * DEGREES)
        axes = ThreeDAxes(x_range=(0, 5, 1), y_range=(0, 5, 1), z_range=(-1, 1, 0.5))
        def param_surface(u, v):
            x = u
            y = v
            z = np.sin(x) * np.cos(y)
            return z
        surface_plane = Surface(
            lambda u, v: axes.c2p(u, v, param_surface(u, v)),
            resolution=(resolution_fa, resolution_fa),
            v_range=[0, 5],
            u_range=[0, 5],
            )
        surface_plane.set_style(fill_opacity=1)
        surface_plane.set_fill_by_value(axes=axes, colorscale=[(RED, -0.5), (YELLOW, 0), (GREEN, 0.5)], axis=2)
        self.add(axes, surface_plane)
```

## ThreeDParametricSpring

3D parametric curve (helix). *still*. Source: [manim/mobject/graphing/functions.py:66](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graphing/functions.py#L66)

```python
from manim import *
class ThreeDParametricSpring(ThreeDScene):
    def construct(self):
        curve1 = ParametricFunction(
            lambda u: (
                1.2 * np.cos(u),
                1.2 * np.sin(u),
                u * 0.05
            ), color=RED, t_range = (-3*TAU, 5*TAU, 0.01)
        ).set_shade_in_3d(True)
        axes = ThreeDAxes()
        self.add(axes, curve1)
        self.set_camera_orientation(phi=80 * DEGREES, theta=-60 * DEGREES)
        self.wait()
```

## ExampleArrow3D

Arrow3D on ThreeDAxes. *still*. Source: [manim/mobject/three_d/three_dimensions.py:1228](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/three_d/three_dimensions.py#L1228)

```python
from manim import *
class ExampleArrow3D(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        arrow = Arrow3D(
            start=np.array([0, 0, 0]),
            end=np.array([2, 2, 2]),
            resolution=8
        )
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.add(axes, arrow)
```

## ExampleSphere

Spheres with different centers, radii and resolutions. *still*. Source: [manim/mobject/three_d/three_dimensions.py:376](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/three_d/three_dimensions.py#L376)

```python
from manim import *
class ExampleSphere(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=PI / 6, theta=PI / 6)
        sphere1 = Sphere(center=(3, 0, 0), radius=1, resolution=(20, 20))
        sphere1.set_color(RED)
        self.add(sphere1)
        sphere2 = Sphere(center=(-1, -3, 0), radius=2, resolution=(18, 18))
        sphere2.set_color(GREEN)
        self.add(sphere2)
        sphere3 = Sphere(center=(-1, 2, 0), radius=2, resolution=(16, 16))
        sphere3.set_color(BLUE)
        self.add(sphere3)
```

## Coloring

ArrowVectorField with a custom color scheme. *still*. Source: [manim/mobject/vector_field.py:543](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/vector_field.py#L543)

```python
from manim import *
class Coloring(Scene):
    def construct(self):
        func = lambda pos: pos - LEFT * 5
        colors = [RED, YELLOW, BLUE, DARK_GRAY]
        min_radius = Circle(radius=2, color=colors[0]).shift(LEFT * 5)
        max_radius = Circle(radius=10, color=colors[-1]).shift(LEFT * 5)
        vf = ArrowVectorField(
            func, min_color_scheme_value=2, max_color_scheme_value=10, colors=colors
        )
        self.add(vf, min_radius, max_radius)
```

## StreamLineCreation

StreamLines being created over a vector field. *animation*. Source: [manim/mobject/vector_field.py:940](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/vector_field.py#L940)

```python
from manim import *
class StreamLineCreation(Scene):
    def construct(self):
        func = lambda pos: (pos[0] * UR + pos[1] * LEFT) - pos
        stream_lines = StreamLines(
            func,
            color=YELLOW,
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            stroke_width=3,
            virtual_time=1,  # use shorter lines
            max_anchors_per_line=5,  # better performance with fewer anchors
        )
        self.play(stream_lines.create())  # uses virtual_time as run_time
        self.wait()
```

## ContinuousMotion

StreamLines in continuous motion. *animation*. Source: [manim/mobject/vector_field.py:1001](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/vector_field.py#L1001)

```python
from manim import *
class ContinuousMotion(Scene):
    def construct(self):
        func = lambda pos: np.sin(pos[0] / 2) * UR + np.cos(pos[1] / 2) * LEFT
        stream_lines = StreamLines(func, stroke_width=3, max_anchors_per_line=30)
        self.add(stream_lines)
        stream_lines.start_animation(warm_up=False, flow_speed=1.5)
        self.wait(stream_lines.virtual_time / stream_lines.flow_speed)
```

## Nudging

Mobjects nudged along a vector field. *animation*. Source: [manim/mobject/vector_field.py:246](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/vector_field.py#L246)

```python
from manim import *
class Nudging(Scene):
    def construct(self):
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP
        vector_field = ArrowVectorField(
            func, x_range=[-7, 7, 1], y_range=[-4, 4, 1], length_func=lambda x: x / 2
        )
        self.add(vector_field)
        circle = Circle(radius=2).shift(LEFT)
        self.add(circle.copy().set_color(GRAY))
        dot = Dot().move_to(circle)

        vector_field.nudge(circle, -2, 60, True)
        vector_field.nudge(dot, -2, 60)

        circle.add_updater(vector_field.get_nudge_updater(pointwise=True))
        dot.add_updater(vector_field.get_nudge_updater())
        self.add(circle, dot)
        self.wait(6)
```

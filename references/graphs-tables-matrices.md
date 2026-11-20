# Node-link graphs, trees, networks, tables, matrices, linear maps

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `LabeledModifiedGraph`: Circular-layout Graph with labeled vertices and per-vertex/per-edge colors.
- `LinearNN`: Layered neural-network-style graph (partite layout).
- `Tree`: Tree layout from a networkx graph, drawn with Create.
- `MovingDiGraph`: DiGraph with vertices animated to new positions.
- `CustomDiGraph`: DiGraph with custom edge styling and tips.
- `ChangeGraphLayout`: Animating a graph between layouts.
- `ImportNetworkxGraph`: networkx random graph imported, then vertices animated onto an ellipse.
- `TableExamples`: Table, DecimalTable, MathTable, MobjectTable and IntegerTable together.
- `CreateTableExample`: Animating a table being drawn (Create).
- `DecimalTableExample`: DecimalTable of x vs f(x) values.
- `GetHighlightedCellExample`: Highlighting a single table cell.
- `MatrixExamples`: Matrix, IntegerMatrix, DecimalMatrix and MobjectMatrix with bracket styles.
- `DeterminantOfAMatrix`: get_det_text to show det(...) around a Matrix.
- `LinearTransformationSceneExample`: LinearTransformationScene: applying a matrix to a grid with basis vectors.
- `ApplyMatrixExample`: ApplyMatrix to a NumberPlane and text.

## LabeledModifiedGraph

Circular-layout Graph with labeled vertices and per-vertex/per-edge colors. *still*. Source: [manim/mobject/graph.py:1422](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1422)

```python
from manim import *
class LabeledModifiedGraph(Scene):
    def construct(self):
        vertices = [1, 2, 3, 4, 5, 6, 7, 8]
        edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                 (2, 8), (3, 4), (6, 1), (6, 2),
                 (6, 3), (7, 2), (7, 4)]
        g = Graph(vertices, edges, layout="circular", layout_scale=3,
                  labels=True, vertex_config={7: {"fill_color": RED}},
                  edge_config={(1, 7): {"stroke_color": RED},
                               (2, 7): {"stroke_color": RED},
                               (4, 7): {"stroke_color": RED}})
        self.add(g)
```

## LinearNN

Layered neural-network-style graph (partite layout). *still*. Source: [manim/mobject/graph.py:1462](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1462)

```python
from manim import *
class LinearNN(Scene):
    def construct(self):
        edges = []
        partitions = []
        c = 0
        layers = [2, 3, 3, 2]  # the number of neurons in each layer

        for i in layers:
            partitions.append(list(range(c + 1, c + i + 1)))
            c += i
        for i, v in enumerate(layers[1:]):
                last = sum(layers[:i+1])
                for j in range(v):
                    for k in range(last - layers[i], last):
                        edges.append((k + 1, j + last + 1))

        vertices = np.arange(1, sum(layers) + 1)

        graph = Graph(
            vertices,
            edges,
            layout='partite',
            partitions=partitions,
            layout_scale=3,
            vertex_config={'radius': 0.20},
        )
        self.add(graph)
```

## Tree

Tree layout from a networkx graph, drawn with Create. *animation*. Source: [manim/mobject/graph.py:1497](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1497)

```python
from manim import *
import networkx as nx

class Tree(Scene):
    def construct(self):
        G = nx.Graph()

        G.add_node("ROOT")

        for i in range(5):
            G.add_node("Child_%i" % i)
            G.add_node("Grandchild_%i" % i)
            G.add_node("Greatgrandchild_%i" % i)

            G.add_edge("ROOT", "Child_%i" % i)
            G.add_edge("Child_%i" % i, "Grandchild_%i" % i)
            G.add_edge("Grandchild_%i" % i, "Greatgrandchild_%i" % i)

        self.play(Create(
            Graph(list(G.nodes), list(G.edges), layout="tree", root_vertex="ROOT")))
```

## MovingDiGraph

DiGraph with vertices animated to new positions. *animation*. Source: [manim/mobject/graph.py:1677](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1677)

```python
from manim import *
class MovingDiGraph(Scene):
    def construct(self):
        vertices = [1, 2, 3, 4]
        edges = [(1, 2), (2, 3), (3, 4), (1, 3), (1, 4)]

        g = DiGraph(vertices, edges)

        self.add(g)
        self.play(
            g[1].animate.move_to([1, 1, 1]),
            g[2].animate.move_to([-1, 1, 2]),
            g[3].animate.move_to([1, -1, -1]),
            g[4].animate.move_to([-1, -1, 0]),
        )
        self.wait()
```

## CustomDiGraph

DiGraph with custom edge styling and tips. *animation*. Source: [manim/mobject/graph.py:1697](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1697)

```python
from manim import *
class CustomDiGraph(Scene):
    def construct(self):
        vertices = [i for i in range(5)]
        edges = [
            (0, 1),
            (1, 2),
            (3, 2),
            (3, 4),
        ]

        edge_config = {
            "stroke_width": 2,
            "tip_config": {
                "tip_shape": ArrowSquareTip,
                "tip_length": 0.15,
            },
            (3, 4): {
                "color": RED,
                "tip_config": {"tip_length": 0.25, "tip_width": 0.25}
            },
        }

        g = DiGraph(
            vertices,
            edges,
            labels=True,
            layout="circular",
            edge_config=edge_config,
        ).scale(1.4)

        self.play(Create(g))
        self.wait()
```

## ChangeGraphLayout

Animating a graph between layouts. *animation*. Source: [manim/mobject/graph.py:1248](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1248)

```python
from manim import *
class ChangeGraphLayout(Scene):
    def construct(self):
        G = Graph([1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5)],
                  layout={1: [-2, 0, 0], 2: [-1, 0, 0], 3: [0, 0, 0],
                          4: [1, 0, 0], 5: [2, 0, 0]}
                  )
        self.play(Create(G))
        self.play(G.animate.change_layout("circular"))
        self.wait()
```

## ImportNetworkxGraph

networkx random graph imported, then vertices animated onto an ellipse. *animation*. Source: [manim/mobject/graph.py:1214](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/graph.py#L1214)

```python
from manim import *
import networkx as nx

nxgraph = nx.erdos_renyi_graph(14, 0.5)

class ImportNetworkxGraph(Scene):
    def construct(self):
        G = Graph.from_networkx(nxgraph, layout="spring", layout_scale=3.5)
        self.play(Create(G))
        self.play(*[G[v].animate.move_to(5*RIGHT*np.cos(ind/7 * PI) +
                                         3*UP*np.sin(ind/7 * PI))
                    for ind, v in enumerate(G.vertices)])
        self.play(Uncreate(G))
```

## TableExamples

Table, DecimalTable, MathTable, MobjectTable and IntegerTable together. *still*. Source: [manim/mobject/table.py:6](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/table.py#L6)

```python
from manim import *
class TableExamples(Scene):
    def construct(self):
        t0 = Table(
            [["First", "Second"],
            ["Third","Fourth"]],
            row_labels=[Text("R1"), Text("R2")],
            col_labels=[Text("C1"), Text("C2")],
            top_left_entry=Text("TOP"))
        t0.add_highlighted_cell((2,2), color=GREEN)
        x_vals = np.linspace(-2,2,5)
        y_vals = np.exp(x_vals)
        t1 = DecimalTable(
            [x_vals, y_vals],
            row_labels=[MathTex("x"), MathTex("f(x)")],
            include_outer_lines=True)
        t1.add(t1.get_cell((2,2), color=RED))
        t2 = MathTable(
            [["+", 0, 5, 10],
            [0, 0, 5, 10],
            [2, 2, 7, 12],
            [4, 4, 9, 14]],
            include_outer_lines=True)
        t2.get_horizontal_lines()[:3].set_color(BLUE)
        t2.get_vertical_lines()[:3].set_color(BLUE)
        t2.get_horizontal_lines()[:3].set_z_index(1)
        cross = VGroup(
            Line(UP + LEFT, DOWN + RIGHT),
            Line(UP + RIGHT, DOWN + LEFT))
        a = Circle().set_color(RED).scale(0.5)
        b = cross.set_color(BLUE).scale(0.5)
        t3 = MobjectTable(
            [[a.copy(),b.copy(),a.copy()],
            [b.copy(),a.copy(),a.copy()],
            [a.copy(),b.copy(),b.copy()]])
        t3.add(Line(
            t3.get_corner(DL), t3.get_corner(UR)
        ).set_color(RED))
        vals = np.arange(1,21).reshape(5,4)
        t4 = IntegerTable(
            vals,
            include_outer_lines=True
        )
        g1 = Group(t0, t1).scale(0.5).arrange(buff=1).to_edge(UP, buff=1)
        g2 = Group(t2, t3, t4).scale(0.5).arrange(buff=1).to_edge(DOWN, buff=1)
        self.add(g1, g2)
```

## CreateTableExample

Animating a table being drawn (Create). *animation*. Source: [manim/mobject/table.py:958](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/table.py#L958)

```python
from manim import *
class CreateTableExample(Scene):
    def construct(self):
        table = Table(
            [["First", "Second"],
            ["Third","Fourth"]],
            row_labels=[Text("R1"), Text("R2")],
            col_labels=[Text("C1"), Text("C2")],
            include_outer_lines=True)
        self.play(table.create())
        self.wait()
```

## DecimalTableExample

DecimalTable of x vs f(x) values. *still*. Source: [manim/mobject/table.py:1165](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/table.py#L1165)

```python
from manim import *
class DecimalTableExample(Scene):
    def construct(self):
        x_vals = [-2,-1,0,1,2]
        y_vals = np.exp(x_vals)
        t0 = DecimalTable(
            [x_vals, y_vals],
            row_labels=[MathTex("x"), MathTex("f(x)=e^{x}")],
            h_buff=1,
            element_to_mobject_config={"num_decimal_places": 2})
        self.add(t0)
```

## GetHighlightedCellExample

Highlighting a single table cell. *still*. Source: [manim/mobject/table.py:866](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/table.py#L866)

```python
from manim import *
class GetHighlightedCellExample(Scene):
    def construct(self):
        table = Table(
            [["First", "Second"],
            ["Third","Fourth"]],
            row_labels=[Text("R1"), Text("R2")],
            col_labels=[Text("C1"), Text("C2")])
        highlight = table.get_highlighted_cell((2,2), color=GREEN)
        table.add_to_back(highlight)
        self.add(table)
```

## MatrixExamples

Matrix, IntegerMatrix, DecimalMatrix and MobjectMatrix with bracket styles. *still*. Source: [manim/mobject/matrix.py:6](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/matrix.py#L6)

```python
from manim import *
class MatrixExamples(Scene):
    def construct(self):
        m0 = Matrix([["\\pi", 0], [-1, 1]])
        m1 = IntegerMatrix([[1.5, 0.], [12, -1.3]],
            left_bracket="(",
            right_bracket=")")
        m2 = DecimalMatrix(
            [[3.456, 2.122], [33.2244, 12.33]],
            element_to_mobject_config={"num_decimal_places": 2},
            left_bracket=r"\{",
            right_bracket=r"\}")
        m3 = MobjectMatrix(
            [[Circle().scale(0.3), Square().scale(0.3)],
            [MathTex("\\pi").scale(2), Star().scale(0.3)]],
            left_bracket="\\langle",
            right_bracket="\\rangle")
        g = Group(m0, m1, m2, m3).arrange_in_grid(buff=2)
        self.add(g)
```

## DeterminantOfAMatrix

get_det_text to show det(...) around a Matrix. *still*. Source: [manim/mobject/matrix.py:608](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/matrix.py#L608)

```python
from manim import *
class DeterminantOfAMatrix(Scene):
    def construct(self):
        matrix = Matrix([
            [2, 0],
            [-1, 1]
        ])

        # scaling down the `det` string
        det = get_det_text(matrix,
                    determinant=3,
                    initial_scale_factor=1)

        # must add the matrix
        self.add(matrix)
        self.add(det)
```

## LinearTransformationSceneExample

LinearTransformationScene: applying a matrix to a grid with basis vectors. *animation*. Source: [manim/scene/vector_space_scene.py:625](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/scene/vector_space_scene.py#L625)

```python
from manim import *
class LinearTransformationSceneExample(LinearTransformationScene):
    def __init__(self, **kwargs):
        LinearTransformationScene.__init__(
            self,
            show_coordinates=True,
            leave_ghost_vectors=True,
            **kwargs
        )

    def construct(self):
        matrix = [[1, 1], [0, 1]]
        self.apply_matrix(matrix)
        self.wait()
```

## ApplyMatrixExample

ApplyMatrix to a NumberPlane and text. *animation*. Source: [manim/animation/transform.py:655](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform.py#L655)

```python
from manim import *
class ApplyMatrixExample(Scene):
    def construct(self):
        matrix = [[1, 1], [0, 2/3]]
        self.play(ApplyMatrix(matrix, Text("Hello World!")), ApplyMatrix(matrix, NumberPlane()))
```

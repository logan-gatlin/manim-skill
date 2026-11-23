# Boundary

A boundary around a group of things in a diagram, in [boundary.py](boundary.py): a network, a cluster, a region, a trust zone. It is a thin outline with its label set into a gap in the top edge.

Copy `boundary.py` next to the scene:

```python
from boundary import Boundary

net = Boundary(api, worker, label="Private network")
self.play(net.draw())                              # draws on, both ways round from the label
self.play(net.include(cache), FadeIn(cache))       # widens to take in another member
self.play(net.exclude(cache), FadeOut(cache))      # and closes up again
```

![boundary](images/boundary.png)

The boundary is sized from its members, with padding. It always draws behind them, whatever order things are added to the scene in.

## Changing it

Each of these returns an animation to `play`:

| Call | Effect |
|---|---|
| `net.draw()` | Draws the outline on from the label's corner, both ways round at once, so the two halves meet at the bottom. The label slides in a moment after. Adds the boundary to the scene. |
| `net.include(a, b)` | Takes in more members: the outline moves to fit. Fade the new members in alongside it. |
| `net.exclude(a)` | Lets members go: the outline closes up around the rest. |
| `net.fit()` | Moves the outline to fit its members where they are now, for after they have moved or grown. |

`net.refit()` does the same as `fit()` at once, with no animation. To make a boundary follow members that are moving, give it an updater: `net.add_updater(lambda b: b.refit())`.

Remove a boundary with `FadeOut(net)`.

## Options

`Boundary(*members, label=None, color=LINE, pad=0.28, radius=0.16, label_size=13)`

| Option | Effect |
|---|---|
| `members` | The mobjects to enclose: nodes, other boundaries, anything. |
| `label` | A word or two naming the group. Without one the outline is whole. |
| `color` | The outline's color. |
| `pad` | The space left around the members. The top gets a little more. |
| `radius` | The radius of the corners. |
| `label_size` | The label's font size. |

Boundaries nest: make the inner one first and give it to the outer one as a member, with a smaller `pad` on the inner one so the two outlines stay apart. After the inner one changes size, play `outer.fit()`.

Lines and packets cross a boundary as usual; nothing needs to be done for them.

## Regenerating the image

```bash
manim render -s -r 2400,900 --disable_caching --media_dir /tmp/manim/boundary -o boundary examples.py Still
cp /tmp/manim/boundary/images/examples/boundary.png images/
```

`examples.py` also has `Demo`, which draws a boundary, takes in two more nodes, nests a second boundary inside it and lets a node go.

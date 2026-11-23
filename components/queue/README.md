# Queue

A queue, in [fifo.py](fifo.py): items join at one end, wait their turn between a pair of brackets, and leave at the other. The head is at the right.

Copy `fifo.py` next to the scene. (It is not called `queue.py` because a file of that name would hide Python's own `queue` module.)

```python
from fifo import Queue

q = Queue(capacity=6)
self.play(FadeIn(q))
self.play(q.push(4))        # four items join, one after another
self.play(q.pop())          # the one at the head leaves
self.play(q.push(5))        # more than there is room for: the rest wait outside
self.play(q.pop(2))         # as two leave, two of those waiting move in
```

![queue](images/queue.png)

## What it shows

- **Items** are blue dots. One that joins comes in from the left and fades in as it arrives; one that leaves goes out to the right and fades.
- **A full queue** has red brackets.
- **Items with no room** wait outside the left bracket, in grey, and turn blue as they move in when room appears. This is back-pressure: the producer is held up, and nothing is thrown away.

`q.push(n)` and `q.pop(n)` return the animation of `n` items joining or leaving, one after another; everything behind a leaving item moves up. Popping more than there are takes what is there. Moves can be made ahead of being played, so `Succession(q.push(3), q.pop())` works. `q.count` is how many items are in the queue or waiting.

## Options

`Queue(capacity=6)`

| Option | Effect |
|---|---|
| `capacity` | How many items the queue holds. `None` is a queue with no limit: its brackets hug whatever is in it, the left one moving out as items join, and nothing ever waits or turns red. |

A queue is an ordinary group: bring it in with `FadeIn`, place it with `move_to` or `next_to`, and resize it with `scale`. It is laid out from its right-hand bracket, which stays put while the left one and the items move; position it by that edge when it has no limit, for example `q.move_to(RIGHT * 2, aligned_edge=RIGHT)`.

Leave room to the left for arriving and waiting items (about three places) and to the right for leaving ones (about two).

## Regenerating the image

```bash
manim render -s -r 2400,900 --disable_caching --media_dir /tmp/manim/queue -o queue examples.py Still
cp /tmp/manim/queue/images/examples/queue.png images/
```

`examples.py` also has `Demo`, which fills, overfills and drains a queue of six, then does the same with a queue that has no limit.

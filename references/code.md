# Code: highlighted snippets and animating them

`Code` highlights with Pygments, which ships with Manim, so no other library is needed. These examples are not from the Manim docs, whose only `Code` example is the still `CodeFromString` in [text-and-math.md](text-and-math.md). They were written or adapted from the sources linked on each one and render cleanly on v0.22.1. All are *animation* examples.

## Index

- `CodeTypeIn`: Typing code in line by line.
- `CodeLineSpotlight`: Highlight bar that moves between lines, dimming the rest.
- `CodeTokenFocus`: Picking out a name or token in the code (box, recolor, circle).
- `CodeMorph`: Morphing one version of the code into the next, with a reusable `morph_code` helper.

## Working with `Code`

- **API.** Write `Code(code_string=..., language="python", formatter_style="monokai", background="window", add_line_numbers=True, paragraph_config={"font_size": 20})`. Examples online often use the pre-0.19 API (`code=`, `file_name=`, `style=`, `insert_line_no=`, a `font_size=` argument, `code.code` for the lines), which fails on this version. Name `language` explicitly; guessing it is unreliable. `Code.get_styles_list()` lists the styles.
- **Colors** come from the Pygments style. `paragraph_config={"color": ...}` is ignored. Recolor glyphs after building it, or pass a custom style class as `formatter_style`.
- **Parts.** `code.background`, `code.line_numbers` (absent without line numbers) and `code.code_lines`: `code.code_lines[i]` is line `i` (0-based), and `code.code_lines[i][k]` is the k-th **non-whitespace** character of that line, since spaces have no glyph. `find_glyphs` and `tokens_of` below do this mapping.
- **Animate whole lines or single glyphs, never a slice.** `code.code_lines[i][a:b]` builds a new `VGroup`. Animating it makes Manim add it to the scene, which splits the `Code` apart: the reading-time checker then reports the code as shown for 0 s. Slices are fine for building shapes around them (`SurroundingRectangle`, `Brace`, `Circumscribe`). To move or recolor a token, animate each glyph: `*(g.animate.set_color(YELLOW) for g in token)`.
- **Line positions.** A line's own centre and height shift with its letters (`return s` sits lower than `def total(prices):`). Align bars and arrows to `code.line_numbers[i]`, which sit on an even grid.
- **Between two versions,** `TransformMatchingShapes(old, new)` works for a small edit, but it pairs identical glyphs regardless of position, so letters can fly across the block. Use `morph_code` for anything larger.
- **Reading time.** The checker counts a whole `Code` as one text, line numbers separately, so a long block needs a long hold. Call `self.wait_to_read()` before a morph, as before any change of text.

## CodeTypeIn

Window and line numbers appear, then each line types in letter by letter. *animation*. Source: written for this skill from the `Code` attributes in [code_mobject.py](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/code_mobject.py).

```python
from manim import *


class CodeTypeIn(Scene):
    def construct(self):
        src = '''def total(prices):
    s = 0
    for p in prices:
        s += p
    return s'''
        code = Code(code_string=src, language="python", background="window")
        self.play(FadeIn(code.background), FadeIn(code.line_numbers))
        for line in code.code_lines:
            self.play(AddTextLetterByLetter(line, time_per_char=0.04))
        self.wait()
```

## CodeLineSpotlight

A translucent bar walks from line to line (one line, then a block of two) while the other lines dim. *animation*. Source: adapted from the coverage-highlight pattern in [manim issue #4289](https://github.com/ManimCommunity/manim/issues/4289).

```python
from manim import *


class CodeLineSpotlight(Scene):
    def construct(self):
        src = '''def total(prices):
    s = 0
    for p in prices:
        s += p
    return s'''
        code = Code(code_string=src, language="python", background="window")

        def bar(*lines):
            # Line numbers sit on an even grid; the code glyphs' own centres don't.
            nums = VGroup(*(code.line_numbers[i] for i in lines))
            pitch = code.line_numbers[0].get_y() - code.line_numbers[1].get_y()
            return Rectangle(
                width=code.background.width - 0.1,
                height=nums.get_top()[1] - nums.get_bottom()[1] + pitch * 0.75,
                fill_color=YELLOW, fill_opacity=0.15, stroke_width=0,
            ).move_to([code.background.get_x(), nums.get_y(), 0])

        def focus(*lines):
            return [
                row.animate.set_opacity(1 if i in lines else 0.35)
                for i, row in enumerate(code.code_lines)
            ]

        self.add(code)
        spot = bar(1)
        self.play(FadeIn(spot), *focus(1))
        self.wait()
        self.play(Transform(spot, bar(2, 3)), *focus(2, 3))
        self.wait()
        self.play(Transform(spot, bar(4)), *focus(4))
        self.wait()
        self.play(FadeOut(spot), *focus(*range(len(code.code_lines))))
        self.wait()
```

## CodeTokenFocus

Every use of a variable is boxed, turned yellow, then circled, picked out by name with `find_glyphs`. *animation*. Source: written for this skill.

```python
from manim import *


def find_glyphs(code, src, line, text, occurrence=0):
    """The glyphs of `text` (no spaces) in line `line` of src, e.g. a variable name.

    Returns a VGroup for building shapes around it (SurroundingRectangle, Brace, Circumscribe).
    Animate the glyphs one by one, never the VGroup itself: Manim would add it to the
    scene as a new mobject and split the Code apart.
    """
    visible = "".join(src.splitlines()[line].split())
    start = -1
    for _ in range(occurrence + 1):
        start = visible.index(text, start + 1)
    return code.code_lines[line][start:start + len(text)]


class CodeTokenFocus(Scene):
    def construct(self):
        src = '''def total(prices):
    s = 0
    for p in prices:
        s += p
    return s'''
        code = Code(code_string=src, language="python", background="window")
        self.add(code)
        uses = [find_glyphs(code, src, 0, "prices"), find_glyphs(code, src, 2, "prices")]
        boxes = VGroup(*(SurroundingRectangle(u, color=YELLOW, buff=0.05) for u in uses))
        self.play(Create(boxes), *(g.animate.set_color(YELLOW) for u in uses for g in u))
        self.play(*(Circumscribe(u, color=YELLOW, buff=0.05) for u in uses))
        self.wait()
```

## CodeMorph

One version of a function morphs into another: removed code fades, code both versions share slides to its new place, added code fades in. `morph_code` is reusable as is. *animation*. Source: the approach of [sudosilico's Magic Move gist](https://gist.github.com/sudosilico/e56f5d4494550724f339c267d59de86a), reimplemented with `difflib` at token level.

```python
from manim import *


def tokens_of(code, src):
    """(token, [glyphs]) for each word or symbol of src, with ("\\n", None) after each line.

    Code drops whitespace, so glyph k of a line is its k-th non-whitespace character.
    The glyphs come as a list: animating a slice of a line would split the Code apart.
    """
    import re

    out = []
    for line, row in zip(src.splitlines(), code.code_lines):
        k = 0
        for tok in re.findall(r"\w+|[^\w\s]", line):
            out.append((tok, list(row[k:k + len(tok)])))
            k += len(tok)
        out.append(("\n", None))
    return out


def morph_code(scene, old, old_src, new, new_src, run_time=2.4):
    """Play old -> new in three beats: removed code fades out, the words and symbols both
    versions share slide to their new places, then added code fades in.

    Tokens are matched in reading order (difflib), so a repeated name never jumps to an
    unrelated spot the way glyphs can with TransformMatchingShapes.
    """
    import difflib
    import re

    a, b = tokens_of(old, old_src), tokens_of(new, new_src)
    # Line breaks can't anchor a match, and a lone symbol (a "+" out of "+=") isn't worth
    # moving across the screen: both only count inside a longer shared run.
    match = difflib.SequenceMatcher(
        lambda t: t == "\n", [t for t, _ in a], [t for t, _ in b], autojunk=False
    )
    gone, moves, added = [], [], []
    for op, i1, i2, j1, j2 in match.get_opcodes():
        if op == "equal" and i2 - i1 == 1 and not re.match(r"\w", a[i1][0]):
            op = "replace"
        if op == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                moves += [Transform(g, h) for g, h in zip(a[i][1] or [], b[j][1] or [])]
        else:
            gone += [g for _, gs in a[i1:i2] for g in gs or []]
            added += [g for _, gs in b[j1:j2] for g in gs or []]
    moves.append(Transform(old.background, new.background))
    if hasattr(old, "line_numbers") and hasattr(new, "line_numbers"):
        n = min(len(old.line_numbers), len(new.line_numbers))
        moves += [Transform(old.line_numbers[i], new.line_numbers[i]) for i in range(n)]
        gone += list(old.line_numbers[n:])
        added += list(new.line_numbers[n:])
    beat = run_time / 3
    if gone:
        scene.play(*(FadeOut(g) for g in gone), run_time=beat)
    scene.play(*moves, run_time=beat)
    if added:
        scene.play(*(FadeIn(g) for g in added), run_time=beat)
    scene.remove(old, *added)
    scene.add(new)


class CodeMorph(Scene):
    def construct(self):
        v1 = '''def total(prices):
    s = 0
    for p in prices:
        s += p
    return s'''
        v2 = '''def total(prices, tax=0.2):
    return sum(prices) * (1 + tax)'''
        old = Code(code_string=v1, language="python", background="window")
        new = Code(code_string=v2, language="python", background="window")
        self.add(old)
        self.wait()
        morph_code(self, old, v1, new, v2)
        self.wait()
```

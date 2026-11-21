# Text, LaTeX/Typst math, equations, code, braces, live numbers

Verbatim examples from the Manim Community v0.22.1 docs; every one renders cleanly on the installed version. *Still* examples are meant for `-s` (PNG); *animation* examples for video.

## Index

- `HelloWorld`: Plain Text at a given font size.
- `SingleLineColor`: MarkupText span coloring inside otherwise-colored text.
- `t2gExample`: Per-substring gradients with t2g.
- `TextAlignment`: Title plus left-aligned agenda list with one item highlighted via opacity.
- `MultiLanguage`: MarkupText in many scripts and languages.
- `MathTeXDemo`: MathTex and Tex with inline $...$ producing the same formula.
- `AMSLaTeX`: Tex mixing text-mode LaTeX with AMS symbols.
- `AddPackageLatex`: Adding a LaTeX package to the template (mathrsfs).
- `LaTeXSubstrings`: Coloring one part of a multi-part Tex with set_color_by_tex.
- `CorrectLaTeXSubstringColoring`: Splitting MathTex with substrings_to_isolate so coloring targets the right parts.
- `IndexLabelsMathTex`: index_labels to find submobject indices of a formula for coloring.
- `LaTeXAlignEnvironment`: Multi-line aligned equations with the align* environment.
- `BulletedListExample`: BulletedList with per-item coloring.
- `TitleExample`: Title bar with underline at the top of the frame.
- `MatchingEquationParts`: TransformMatchingTex: rearranging an equation term by term.
- `Anagram`: TransformMatchingShapes: morphing text into an anagram.
- `TypstExample`: Typst math written on screen (no LaTeX needed).
- `HelloMathTypst`: Typst display math, the Typst counterpart to MathTex.
- `TypstSelectExample`: Selecting and coloring parts of a Typst formula.
- `CodeFromString`: Code block with syntax highlighting, line numbers, and window chrome.
- `BraceAnnotation`: Brace with a text label and a brace along a sloped line.
- `BraceTextExample`: BraceText label, then changing it with change_label.
- `ChangingDecimalExample`: ChangingDecimal driving a DecimalNumber with a function of progress.
- `VariablesWithValueTracker`: Variable (label = value) bound to ValueTrackers, updating live.

## HelloWorld

Plain Text at a given font size. *still*. Source: [docs/source/guides/using_text.rst:36](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L36)

```python
from manim import *
class HelloWorld(Scene):
    def construct(self):
        text = Text("Hello world", font_size=144)
        self.add(text)
```

## SingleLineColor

MarkupText span coloring inside otherwise-colored text. *still*. Source: [docs/source/guides/using_text.rst:49](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L49)

```python
from manim import *
class SingleLineColor(Scene):
    def construct(self):
        text = MarkupText(
            f'all in red <span fgcolor="{YELLOW}">except this</span>', color=RED
        )
        self.add(text)
```

## t2gExample

Per-substring gradients with t2g. *still*. Source: [docs/source/guides/using_text.rst:190](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L190)

```python
from manim import *
class t2gExample(Scene):
    def construct(self):
        t2gindices = Text(
            'Hello',
            t2g={
                '[1:-1]': (RED,GREEN),
            },
        ).move_to(LEFT)
        t2gwords = Text(
            'World',
            t2g={
                'World':(RED,BLUE),
            },
        ).next_to(t2gindices, RIGHT)
        self.add(t2gindices, t2gwords)
```

## TextAlignment

Title plus left-aligned agenda list with one item highlighted via opacity. *still*. Source: [manim/mobject/text/text_mobject.py:26](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/text_mobject.py#L26)

```python
from manim import *
class TextAlignment(Scene):
    def construct(self):
        title = Text("K-means clustering and Logistic Regression", color=WHITE)
        title.scale(0.75)
        self.add(title.to_edge(UP))

        t1 = Text("1. Measuring").set_color(WHITE)

        t2 = Text("2. Clustering").set_color(WHITE)

        t3 = Text("3. Regression").set_color(WHITE)

        t4 = Text("4. Prediction").set_color(WHITE)

        x = VGroup(t1, t2, t3, t4).arrange(direction=DOWN, aligned_edge=LEFT).scale(0.7).next_to(ORIGIN,DR)
        x.set_opacity(0.5)
        x.submobjects[1].set_opacity(1)
        self.add(x)
```

## MultiLanguage

MarkupText in many scripts and languages. *still*. Source: [manim/mobject/text/text_mobject.py:1123](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/text_mobject.py#L1123)

```python
from manim import *
class MultiLanguage(Scene):
    def construct(self):
        morning = MarkupText("வணக்கம்", font="sans-serif")
        japanese = MarkupText(
            '<span fgcolor="blue">日本</span>へようこそ'
        )  # works as in ``Text``.
        mess = MarkupText("Multi-Language", weight=BOLD)
        russ = MarkupText("Здравствуйте मस नम म ", font="sans-serif")
        hin = MarkupText("नमस्ते", font="sans-serif")
        chinese = MarkupText("臂猿「黛比」帶著孩子", font="sans-serif")
        group = VGroup(morning, japanese, mess, russ, hin, chinese).arrange(DOWN)
        self.add(group)
```

## MathTeXDemo

MathTex and Tex with inline $...$ producing the same formula. *still*. Source: [docs/source/guides/using_text.rst:384](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L384)

```python
from manim import *
class MathTeXDemo(Scene):
    def construct(self):
        rtarrow0 = MathTex(r"\xrightarrow{x^6y^8}", font_size=96)
        rtarrow1 = Tex(r"$\xrightarrow{x^6y^8}$", font_size=96)

        self.add(VGroup(rtarrow0, rtarrow1).arrange(DOWN))
```

## AMSLaTeX

Tex mixing text-mode LaTeX with AMS symbols. *still*. Source: [docs/source/guides/using_text.rst:401](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L401)

```python
from manim import *
class AMSLaTeX(Scene):
    def construct(self):
        tex = Tex(r'$\mathtt{H} \looparrowright$ \LaTeX', font_size=144)
        self.add(tex)
```

## AddPackageLatex

Adding a LaTeX package to the template (mathrsfs). *still*. Source: [docs/source/guides/using_text.rst:430](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L430)

```python
from manim import *
class AddPackageLatex(Scene):
    def construct(self):
        myTemplate = TexTemplate()
        myTemplate.add_to_preamble(r"\usepackage{mathrsfs}")
        tex = Tex(
            r"$\mathscr{H} \rightarrow \mathbb{H}$",
            tex_template=myTemplate,
            font_size=144,
        )
        self.add(tex)
```

## LaTeXSubstrings

Coloring one part of a multi-part Tex with set_color_by_tex. *still*. Source: [docs/source/guides/using_text.rst:453](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L453)

```python
from manim import *
class LaTeXSubstrings(Scene):
    def construct(self):
        tex = Tex('Hello', r'$\bigstar$', r'\LaTeX', font_size=144)
        tex.set_color_by_tex(r'$\bigstar$', RED)
        self.add(tex)
```

## CorrectLaTeXSubstringColoring

Splitting MathTex with substrings_to_isolate so coloring targets the right parts. *still*. Source: [docs/source/guides/using_text.rst:467](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L467)

```python
from manim import *
class CorrectLaTeXSubstringColoring(Scene):
    def construct(self):
        equation = MathTex(
            r"e^{x} = x^0 + x^1 + \frac{1}{2} x^2 + \frac{1}{6} x^3 + \cdots + \frac{1}{n!} x^n + \cdots",
            substrings_to_isolate="x"
        )
        equation.set_color_by_tex("x", YELLOW)
        self.add(equation)
```

## IndexLabelsMathTex

index_labels to find submobject indices of a formula for coloring. *still*. Source: [docs/source/guides/using_text.rst:510](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L510)

```python
from manim import *
class IndexLabelsMathTex(Scene):
    def construct(self):
        text = MathTex(r"\binom{2n}{n+2}", font_size=96)

        # index the first (and only) term of the MathTex mob
        self.add(index_labels(text[0]))

        text[0][1:3].set_color(YELLOW)
        text[0][3:6].set_color(RED)
        self.add(text)
```

## LaTeXAlignEnvironment

Multi-line aligned equations with the align* environment. *still*. Source: [docs/source/guides/using_text.rst:568](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L568)

```python
from manim import *
class LaTeXAlignEnvironment(Scene):
    def construct(self):
        tex = MathTex(r'f(x) &= 3 + 2 + 1\\ &= 5 + 1 \\ &= 6', font_size=96)
        self.add(tex)
```

## BulletedListExample

BulletedList with per-item coloring. *still*. Source: [manim/mobject/text/tex_mobject.py:665](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/tex_mobject.py#L665)

```python
from manim import *
class BulletedListExample(Scene):
    def construct(self):
        blist = BulletedList("Item 1", "Item 2", "Item 3", height=2, width=2)
        blist.set_color_by_tex("Item 1", RED)
        blist.set_color_by_tex("Item 2", GREEN)
        blist.set_color_by_tex("Item 3", BLUE)
        self.add(blist)
```

## TitleExample

Title bar with underline at the top of the frame. *still*. Source: [manim/mobject/text/tex_mobject.py:727](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/tex_mobject.py#L727)

```python
from manim import *
import manim

class TitleExample(Scene):
    def construct(self):
        banner = ManimBanner()
        title = Title(f"Manim version {manim.__version__}")
        self.add(banner, title)
```

## MatchingEquationParts

TransformMatchingTex: rearranging an equation term by term. *animation*. Source: [manim/animation/transform_matching_parts.py:249](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform_matching_parts.py#L249)

```python
from manim import *
class MatchingEquationParts(Scene):
    def construct(self):
        variables = VGroup(MathTex("a"), MathTex("b"), MathTex("c")).arrange_submobjects().shift(UP)

        eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
        eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2")
        eq3 = MathTex("{{a}}^2", "=", "{{c}}^2", "-", "{{b}}^2")

        self.add(eq1)
        self.wait(0.5)
        self.play(TransformMatchingTex(Group(eq1, variables), eq2))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2, eq3))
        self.wait(0.5)
```

## Anagram

TransformMatchingShapes: morphing text into an anagram. *animation*. Source: [manim/animation/transform_matching_parts.py:191](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/transform_matching_parts.py#L191)

```python
from manim import *
class Anagram(Scene):
    def construct(self):
        src = Text("the morse code")
        tar = Text("here come dots")
        self.play(Write(src))
        self.wait(0.5)
        self.play(TransformMatchingShapes(src, tar, path_arc=PI/2))
        self.wait(0.5)
```

## TypstExample

Typst math written on screen (no LaTeX needed). *animation*. Source: [manim/mobject/text/typst_mobject.py:318](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/typst_mobject.py#L318)

```python
from manim import *
class TypstExample(Scene):
    def construct(self):
        formula = Typst(r"$ integral_a^b f(x) dif x $")
        self.play(Write(formula))
```

## HelloMathTypst

Typst display math, the Typst counterpart to MathTex. *still*. Source: [docs/source/guides/using_text.rst:331](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/guides/using_text.rst#L331)

```python
from manim import *
class HelloMathTypst(Scene):
    def construct(self):
        equation = MathTypst(r"sum_(k=1)^n k = (n(n + 1)) / 2", font_size=72)
        self.add(equation)
```

## TypstSelectExample

Selecting and coloring parts of a Typst formula. *still*. Source: [manim/mobject/text/typst_mobject.py:710](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/typst_mobject.py#L710)

```python
from manim import *
class TypstSelectExample(Scene):
    def construct(self):
        eq = MathTypst(
            "{{ a + b : num }} / {{ c : den }} = {{ lambda }} {{ x }}"
        )
        eq.select("num").set_color(RED)  # "a + b"
        eq.select("den").set_color(BLUE) # "c"
        eq.select(0).set_color(YELLOW)   # "lambda" (auto-numbered: "grp-0")
        eq.select(1).set_color(GREEN)    # "x" (auto-numbered: "grp-1")

        self.add(eq)
```

## CodeFromString

Code block with syntax highlighting, line numbers, and window chrome. *still*. Source: [manim/mobject/text/code_mobject.py:52](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/code_mobject.py#L52), with `import code_font` added, which sets the code in the skill's code font (see [code.md](code.md)).

```python
from manim import *

import code_font
class CodeFromString(Scene):
    def construct(self):
        code = '''from manim import Scene, Square

class FadeInSquare(Scene):
    def construct(self):
        s = Square()
        self.play(FadeIn(s))
        self.play(s.animate.scale(2))
        self.wait()'''

        rendered_code = Code(
            code_string=code,
            language="python",
            background="window",
            background_config={"stroke_color": "maroon"},
        )
        self.add(rendered_code)
```

## BraceAnnotation

Brace with a text label and a brace along a sloped line. *still*. Source: [docs/source/examples.rst:53](https://github.com/ManimCommunity/manim/blob/v0.22.1/docs/source/examples.rst#L53)

```python
from manim import *
class BraceAnnotation(Scene):
    def construct(self):
        dot = Dot([-2, -1, 0])
        dot2 = Dot([2, 1, 0])
        line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
        b1 = Brace(line)
        b1text = b1.get_text("Horizontal distance")
        b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
        b2text = b2.get_tex("x-x_1")
        self.add(line, dot, dot2, b1, b2, b1text, b2text)
```

## BraceTextExample

BraceText label, then changing it with change_label. *still*. Source: [manim/mobject/svg/brace.py:311](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/svg/brace.py#L311)

```python
from manim import *
class BraceTextExample(Scene):
    def construct(self):
        s1 = Square().move_to(2*LEFT)
        self.add(s1)
        br1 = BraceText(s1, "Label")
        self.add(br1)

        s2 = Square().move_to(2*RIGHT)
        self.add(s2)
        br2 = BraceText(s2, "Label")

        br2.change_label("new")
        self.add(br2)
        self.wait(0.1)
```

## ChangingDecimalExample

ChangingDecimal driving a DecimalNumber with a function of progress. *animation*. Source: [manim/animation/numbers.py:37](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/animation/numbers.py#L37)

```python
from manim import *
class ChangingDecimalExample(Scene):
    def construct(self):
        number = DecimalNumber(0)
        self.add(number)
        self.play(
            ChangingDecimal(
                number,
                lambda a: 5 * a,
                run_time=3
            )
        )
        self.wait()
```

## VariablesWithValueTracker

Variable (label = value) bound to ValueTrackers, updating live. *animation*. Source: [manim/mobject/text/numbers.py:385](https://github.com/ManimCommunity/manim/blob/v0.22.1/manim/mobject/text/numbers.py#L385)

```python
from manim import *
class VariablesWithValueTracker(Scene):
    def construct(self):
        var = 0.5
        on_screen_var = Variable(var, Text("var"), num_decimal_places=3)

        # You can also change the colours for the label and value
        on_screen_var.label.set_color(RED)
        on_screen_var.value.set_color(GREEN)

        self.play(Write(on_screen_var))
        # The above line will just display the variable with
        # its initial value on the screen. If you also wish to
        # update it, you can do so by accessing the `tracker` attribute
        self.wait()
        var_tracker = on_screen_var.tracker
        var = 10.5
        self.play(var_tracker.animate.set_value(var))
        self.wait()

        int_var = 0
        on_screen_int_var = Variable(
            int_var, Text("int_var"), var_type=Integer
        ).next_to(on_screen_var, DOWN)
        on_screen_int_var.label.set_color(RED)
        on_screen_int_var.value.set_color(GREEN)

        self.play(Write(on_screen_int_var))
        self.wait()
        var_tracker = on_screen_int_var.tracker
        var = 10.5
        self.play(var_tracker.animate.set_value(var))
        self.wait()

        # If you wish to have a somewhat more complicated label for your
        # variable with subscripts, superscripts, etc. the default class
        # for the label is MathTex
        subscript_label_var = 10
        on_screen_subscript_var = Variable(subscript_label_var, "{a}_{i}").next_to(
            on_screen_int_var, DOWN
        )
        self.play(Write(on_screen_subscript_var))
        self.wait()
```

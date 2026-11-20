---
name: manim
description: Render explanatory animations and still diagrams with Manim Community. Use when a visual would explain something better than text (math, equations, function plots, geometry, graphs/networks, tables, matrices, 3D, vector fields), or when the user asks for an animation, a diagram, or a Manim scene.
---

# Manim

Installed here: **Manim Community v0.22.1** (`manim` on PATH, a `uv tool` install with the `typst` extra), plus TeX Live and `dvisvgm` for `Tex`/`MathTex`, and Chatterbox Turbo for narration (a CPU install in its own venv under `~/.local/opt/chatterbox`, driven by `narration.py`). Scene files run on the tool's own Python, which includes `numpy`, `scipy` and `networkx`; other imports fail. Use the ManimCE API only. 3Blue1Brown's `manimgl` is a different library, so code written for it won't run here.

## Style

Manim is a tool for presenting information in a dynamic and interesting way.
If what you made could just as easily have been made as a flowchart, spreadsheet, or slideshow, you are not correctly using manim.
Avoid technical jargon, keep your presentation accessible.
Pick a set of motifs and stick to them - a concept should have a consistent visual representation.

## Steps

1. **Pick the output.** Use a still PNG for a static picture (a labeled diagram, plot, table or formula). Use an MP4 when the point is change or sequence (a derivation step by step, a moving point, a transform). Use GIF only when the place it's going can't play video.
2. **Find the closest examples.** Open the topic file(s) below, scan the index at the top, and read the 1–3 examples closest to what you need. Build your scene by adapting them: their API usage is known to work on this version.
3. **Write the scene** to `/tmp/manim/<slug>/scene.py` unless the user named a location. Start it with `from manim import *` and define one `Scene` subclass (`MovingCameraScene` / `ThreeDScene` / `ZoomedScene` when the examples use one).

   An MP4 or GIF that shows text must give viewers **reading time**, and a checker enforces it. Copy [reading_time.py](reading_time.py) next to the scene, import it with `from reading_time import ReadingTime`, and put the mixin first: `class SceneName(ReadingTime, Scene)`. Call `self.wait_to_read()` before every `play` that hides, replaces or dims text. It holds until each visible text has been on screen for 1 s plus its words at 150 wpm, with all text revealed by one `play` read together. Show new words as a new mobject (`FadeIn`, `ReplacementTransform`) rather than with `become()`, so that its time starts fresh. Motion can keep running during the hold: put `self.wait_to_read()` after an animation that plays while the text is up.

   An MP4 that explains in captions is also **narrated**: a voice reads it out. Copy [narration.py](narration.py) next to the scene and put it first: `class SceneName(Narration, ReadingTime, Scene)`. `self.speak(text)` waits for the previous line to finish, then starts the next one, and the animations that follow play while it's spoken. Put it right before the `play` that shows the caption it reads. In a narrated scene the voice sets the hold instead of the word count: text that appears while a line is spoken must stay until the narrator finishes plus a 0.5 s pause, and `self.wait_to_read()` holds exactly that long before the next change (text shown during silence keeps the word-count rule). The voice is a neural clone of a calm male narrator (Chatterbox Turbo), tuned for walking through technical diagrams. Each new line takes about 1–3× its spoken length to synthesize, draft stills included, and is cached under `media/voice`, so later renders only voice the lines you changed. Write each line to be heard, not read. Acronyms such as API, TLS and HTTP read well as written, and `narration.py` already spells out units after numbers (`200 ms`), dotted versions (`2.4.1`) and `k8s`. Say other machine strings the way a narrator would: "seventeen eleven", not "2026.11.1711". Describe paths and branch names rather than reading them out ("an auto patches release branch"), and fix any word the voice gets wrong through the scene's `pronounce` dict (`{"edgeworker": "edge worker"}`).
4. **Draft and look.** Render a low-quality still and read the PNG:
   ```bash
   cd /tmp/manim/<slug> && manim render -ql -s --media_dir media -o draft scene.py SceneName
   # -> media/images/scene/draft.png
   ```
   For an animation, also check key moments: `-s -n 0,K` stops after animation `K` (0-based; each `self.play` and each `self.wait` counts as one) and saves that frame. The frame is about 14.2 × 8 units, centred on the origin. Fix and re-render until every frame you checked shows all elements inside the frame, no overlapping labels, and readable text.

   A scene that takes text away too soon fails with `ReadingTimeError`, which lists each text, when it appeared, and how long it was shown against how long it needed. Add `self.wait_to_read()` before each listed change. To look at draft frames before the timing is fixed, prefix the command with `MANIM_READING_TIME=warn`. The final render runs without it and must pass.
5. **Final render.** Use `-qm` (720p30). 3D scenes are slow on the Cairo renderer, so draft them at `-ql`.
   ```bash
   manim render -qh --media_dir media -o final scene.py SceneName
   # -> media/videos/scene/1080p60/final.mp4   (add --format gif for a GIF; -s for a PNG at media/images/scene/final.png)
   ```
6. **Deliver.** Show the output inline when your interface can display it, which is when your instructions say Markdown image syntax embeds images or video (T3 Code's do). Copy the output file into the session's working directory, then embed it from there with its absolute path (`![title](/abs/path/out.mp4)`; this works for MP4 and PNG alike). T3 Code renders media inline only from the working directory, so an embed pointing into `/tmp` shows up as a plain link. In an interface that shows only text, such as a plain terminal, give the output file's absolute path instead. Either way, also give the scene file path so the user can tweak it.

   **Every iteration ends in a delivery.** Whenever you change a scene, whether for the user's feedback or for your own fixes, finish the turn by re-rendering every video in the set at final quality, even ones you didn't touch, and delivering each one as in step 6. Stills and frame grabs help you check your work, but they don't replace the videos. Give each round its own file names (`<name>-v2.mp4`, `<name>-v3.mp4`), so earlier messages keep showing the versions they described.

## Topic files

Each one holds verbatim, render-tested examples from the v0.22.1 docs, with an index at the top.

- [references/basics.md](references/basics.md): positioning, styling, grouping/arranging, `.animate`, `Transform`, custom animations.
- [references/text-and-math.md](references/text-and-math.md): `Text`/`MarkupText`, `Tex`/`MathTex`, Typst math, coloring parts of formulas, equation rearranging, bullet lists, titles, code blocks, braces, live numbers.
- [references/plots-and-axes.md](references/plots-and-axes.md): `Axes` plots, areas and Riemann sums, derivatives/secants, implicit/parametric/polar curves, log axes, data line graphs, number lines and planes, complex plane, bar charts.
- [references/diagrams-and-geometry.md](references/diagrams-and-geometry.md): arrows, labeled lines/dots/shapes, angles, right angles, highlighting (surrounding box, underline, cross), Venn/boolean shapes, polygons, dashed outlines.
- [references/graphs-tables-matrices.md](references/graphs-tables-matrices.md): node-link `Graph`/`DiGraph`, trees, neural-net layers, networkx import, layout changes, tables, matrices, determinants, linear transformations of the plane.
- [references/animation-and-motion.md](references/animation-and-motion.md): updaters, `ValueTracker`, `always_redraw`, traced paths, transform variants, `MoveToTarget`/`Restore`, `Succession`/`LaggedStart` timing, emphasis (`Indicate`, `Circumscribe`, `Flash`), grow/fade entrances, rate functions.
- [references/camera-3d-fields.md](references/camera-3d-fields.md): moving/zooming camera, zoomed inset, `ThreeDScene` camera control, 3D surfaces and curves, vector fields and stream lines.
- [references/complete-scenes.md](references/complete-scenes.md): two longer scenes showing how a multi-step explanation is paced.

## Looking up the API

The installed source, with full docstrings, is at `~/.local/share/uv/tools/manim/lib/python3.13/site-packages/manim/`. Grep it for a class or method's signature and options before guessing a keyword argument.

## Gotchas

- Write LaTeX strings as raw strings (`r"\frac{a}{b}"`). A LaTeX error prints the `.tex` log, and the offending line is usually near the end.
- `xelatex` is not installed, so `TexTemplateLibrary` templates that need it (e.g. `ctex`) fail. For CJK text use `Text`/`MarkupText`, which render through Pango with system fonts (`fc-list` shows them).
- `Typst` / `MathTypst` are a faster alternative to `Tex` / `MathTex` and need no LaTeX.

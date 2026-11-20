"""Fail a Manim render whose on-screen text disappears before a viewer can read it.

Copy this file next to scene.py and list the mixin before the scene base class:

    from reading_time import ReadingTime

    class MyScene(ReadingTime, Scene):
        def construct(self):
            self.play(FadeIn(caption))
            self.wait_to_read()          # holds until everything on screen is readable
            self.play(FadeOut(caption))

Text that becomes visible in the same play() is one group, read together: every text in
it must stay visible for READING_BASE + (group words) / READING_WPM. A text's time runs
from the end of the animation that revealed it to the start of the animation that hides
it, replaces it, or dims it below MIN_OPACITY. When the scene finishes, every shortfall
is listed and the render fails. With MANIM_READING_TIME=warn it only prints them.
"""

import os
import re

import manim
from manim import MarkupText, Paragraph, SingleStringMathTex, Text

READING_WPM = 150  # words a minute: subtitle pace, slowed for viewers also watching motion
READING_BASE = 1.0  # seconds to notice new text and move the eyes to it
MIN_OPACITY = 0.3  # dimmer than this counts as hidden
CHARS_PER_WORD = 6  # version strings and paths count by length, not spaces

_TEXT_TYPES = tuple(
    t for t in (Paragraph, MarkupText, Text, SingleStringMathTex, getattr(manim, "Typst", None)) if t
)


class ReadingTimeError(Exception):
    pass


def reading_exempt(mob):
    """Mark text that is never meant to be read, such as a decorative glyph."""
    mob.reading_exempt = True
    return mob


def _source(m):
    if isinstance(m, Paragraph):
        return m.lines_text.original_text
    if isinstance(m, MarkupText):
        return re.sub(r"<[^>]+>", "", m.text)
    if isinstance(m, Text):
        return m.original_text
    if isinstance(m, SingleStringMathTex):
        return re.sub(r"\\[A-Za-z]+|[{}^_$&\\]", " ", m.tex_string)
    return getattr(m, "typst_code", "") or getattr(m, "text", "")


def _words(m):
    s = _source(m)
    return max(len(s.split()), len(s.replace(" ", "")) / CHARS_PER_WORD)


class ReadingTime:
    reading_wpm = READING_WPM
    reading_base = READING_BASE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rt_shown = {}  # id -> (mobject, start, budget)
        self._rt_visible = {}
        self._rt_short = []
        construct = self.construct

        def checked_construct():
            construct()
            self._rt_finish()

        self.construct = checked_construct

    # -- public ---------------------------------------------------------
    def wait_to_read(self, extra=0.0):
        """Wait until every visible text has been on screen for its reading time."""
        now = self._rt_now()
        self._rt_sync(now, now)
        left = max((start + budget - now for _, start, budget in self._rt_shown.values()), default=0.0)
        if left + extra > 0:
            # Frames are whole, so round up by one to land past the budget.
            self.wait(left + extra + self._rt_frame())

    def play(self, *args, **kwargs):
        before = self._rt_now()
        self._rt_sync(before, before)
        super().play(*args, **kwargs)
        self._rt_sync(before, self._rt_now())

    # -- tracking -------------------------------------------------------
    def _rt_now(self):
        return float(self.renderer.time)

    def _rt_frame(self):
        return 1.0 / manim.config.frame_rate

    def _rt_texts(self):
        found = {}

        def walk(m):
            if getattr(m, "reading_exempt", False):
                return
            if isinstance(m, _TEXT_TYPES):
                pts = m.family_members_with_points()
                if pts and max(p.get_fill_opacity() for p in pts) >= MIN_OPACITY:
                    found[id(m)] = m
                return
            for s in m.submobjects:
                walk(s)

        for m in self.mobjects:
            walk(m)
        return found

    def _rt_sync(self, hidden_at, shown_at):
        now = self._rt_texts()
        for k in [k for k in self._rt_visible if k not in now]:
            self._rt_close(k, hidden_at)
        new = {k: m for k, m in now.items() if k not in self._rt_visible}
        if new:
            budget = self._rt_budget(new.values(), hidden_at, shown_at)
            for k, m in new.items():
                self._rt_shown[k] = (m, shown_at, budget)
        self._rt_visible = now

    def _rt_budget(self, texts, started, shown):
        """Seconds that `texts`, revealed by an animation from `started` to `shown`, must stay."""
        words = sum(_words(m) for m in texts)
        return self.reading_base + words * 60.0 / self.reading_wpm

    def _rt_close(self, k, t):
        m, start, budget = self._rt_shown.pop(k)
        if t - start + self._rt_frame() < budget:
            self._rt_short.append((start, t - start, budget, _source(m)))

    def _rt_finish(self):
        end = self._rt_now()
        for k in list(self._rt_shown):
            self._rt_close(k, end)
        self._rt_visible = {}
        if not self._rt_short:
            return
        lines = [
            f"  at {start:6.1f}s  shown {shown:4.1f}s of {budget:4.1f}s  {' '.join(text.split())[:70]!r}"
            for start, shown, budget, text in sorted(self._rt_short)
        ]
        report = (
            f"{len(lines)} text(s) left the screen before {self.reading_wpm} wpm reading time. "
            "Call self.wait_to_read() before each change of text:\n" + "\n".join(lines)
        )
        if os.environ.get("MANIM_READING_TIME") == "warn":
            manim.logger.warning(report)
        else:
            raise ReadingTimeError(report)

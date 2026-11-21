"""Renders the images in images/ and a demo video; see README.md for the commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # icons.py, at the skill root

from manim import *

from git_graph import INK, MONO, MUTED, GitGraph

SPACING = 1.1


def feature_history(g):
    """main: three commits; feature: two commits branched from main's second. HEAD on main."""
    return [g.commit(), g.commit(), g.checkout("feature", create=True), g.commit(),
            g.commit(), g.checkout("main"), g.commit()]


class Framed(MovingCameraScene):
    def frame_to(self, mob, pad=0.7):
        aspect = config.pixel_width / config.pixel_height
        self.camera.frame.set(width=max(mob.width + 2 * pad, (mob.height + 2 * pad) * aspect))
        self.camera.frame.move_to(mob)


class BeforeAfter(Framed):
    """Two copies of a history side by side: before and after one command."""

    command = ""
    labels = False

    def setup_history(self, g):
        return feature_history(g)

    def change(self, g):
        raise NotImplementedError

    def construct(self):
        before = GitGraph(origin=ORIGIN, spacing=SPACING, labels=self.labels)
        before.instant(*self.setup_history(before))
        after = GitGraph(origin=ORIGIN, spacing=SPACING, labels=self.labels)
        after.instant(*self.setup_history(after))
        after.instant(self.change(after))
        cmd = Text(self.command, font=MONO, font_size=22, color=INK)
        arrow = Arrow(LEFT, RIGHT, color=MUTED, stroke_width=3, buff=0).set_length(max(cmd.width, 1.2))
        mid = VGroup(cmd, arrow).arrange(DOWN, buff=0.15)
        row = Group(before, mid, after).arrange(RIGHT, buff=0.7, aligned_edge=UP)
        mid.align_to(before, UP).shift(1.2 * DOWN)
        self.add(row)
        self.frame_to(row)


class Rebase(BeforeAfter):
    command = "git rebase main"

    def setup_history(self, g):
        return feature_history(g) + [g.checkout("feature")]

    def change(self, g):
        return g.rebase("main")


class Merge(BeforeAfter):
    command = "git merge feature"

    def change(self, g):
        return g.merge("feature")


class FastForward(BeforeAfter):
    command = "git merge feature"

    def setup_history(self, g):
        return [g.commit(), g.commit(), g.checkout("feature", create=True), g.commit(),
                g.commit(), g.checkout("main")]

    def change(self, g):
        return g.merge("feature")


class CherryPick(BeforeAfter):
    command = "git cherry-pick C4"
    labels = True

    def change(self, g):
        return g.cherry_pick("C4")


class Revert(BeforeAfter):
    command = "git revert C2"
    labels = True

    def setup_history(self, g):
        return [g.commit(), g.commit(), g.commit()]

    def change(self, g):
        return g.revert("C2")


class Reset(BeforeAfter):
    command = "git reset --hard HEAD~2"

    def setup_history(self, g):
        return [g.commit(), g.commit(), g.commit(), g.commit()]

    def change(self, g):
        return g.reset("HEAD~2")


class Refs(Framed):
    """Tags, a remote-tracking branch that is behind, and a detached HEAD."""

    def construct(self):
        g = GitGraph(origin=ORIGIN, spacing=SPACING)
        g.instant(g.commit(), g.tag("v1.0"), g.commit(), g.branch("origin/main", remote=True),
                  g.commit(), g.commit(), g.tag("v1.1"), g.checkout("HEAD~2"))
        self.add(g)
        self.frame_to(g)


class Demo(Scene):
    """A short story touching every operation, with the command shown at the top."""

    def construct(self):
        g = GitGraph(origin=LEFT * 5.9 + UP * 0.7, spacing=1.05)
        self.add(g)
        cmd = None

        def run(text, op, hold=0.5):
            nonlocal cmd
            new = Text(text, font=MONO, font_size=26, color=INK).to_edge(UP, buff=0.6)
            if cmd:  # the old command leaves before the new one arrives, so they never overlap
                self.play(FadeOut(cmd, shift=UP * 0.15, run_time=0.2))
            self.play(op, FadeIn(new, shift=UP * 0.15, run_time=0.3))
            cmd = new
            self.wait(hold)

        run("git commit", g.commit())
        run("git commit", g.commit())
        run("git switch -c feature", g.checkout("feature", create=True))
        run("git commit", g.commit())
        run("git commit", g.commit())
        run("git switch main", g.checkout("main"))
        run("git commit", g.commit())
        run("git switch feature", g.checkout("feature"))
        run("git rebase main", g.rebase("main"), 1)
        run("git switch main", g.checkout("main"))
        run("git merge feature", g.merge("feature"), 1)
        run("git tag v1.0", g.tag("v1.0"))
        run("git commit", g.commit())
        run("git revert HEAD~1", g.revert("HEAD~1"), 1)
        run("git reset --hard HEAD~1", g.reset("HEAD~1"), 1)
        run("git switch -c hotfix", g.checkout("hotfix", create=True))
        run("git commit", g.commit())
        run("git switch feature", g.checkout("feature"))
        run("git cherry-pick hotfix", g.cherry_pick("hotfix"), 1)
        run("git switch main", g.checkout("main"))
        run("git commit", g.commit())
        run("git merge hotfix", g.merge("hotfix"), 1)
        run("git commit --amend", g.amend(), 1)
        run("git checkout HEAD~3", g.checkout("HEAD~3"), 1.5)

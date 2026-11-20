"""End a Manim video on a card that says which model produced it, with a link to this skill.

Copy this file next to scene.py and list the mixin first, before Narration and ReadingTime:

    from produced_by import ProducedBy

    class MyScene(ProducedBy, Narration, ReadingTime, Scene):
        produced_by = "Claude Opus 5.5"   # the model's own name

After construct() returns, and after the narration and the reading-time check finish, the
scene fades out, the card fades in, and the card holds for the last HOLD seconds of the
video. Still renders (-s) skip the card, so the saved last frame is the scene itself.
"""

import manim
from manim import DOWN, UP, FadeIn, FadeOut, Group, Text, VGroup

SKILL_URL = "github.com/logan-gatlin/manim-skill"  # where the skill lives, shown under the model name
HOLD = 0.5  # seconds the card is fully on screen at the end of the video
FADE = 0.5  # seconds for the scene to fade out, and again for the card to fade in


class ProducedBy:
    produced_by = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wrap after the other mixins have, so the card comes after their end-of-scene work.
        construct = self.construct

        def credited_construct():
            construct()
            self.show_produced_by()

        self.construct = credited_construct

    def show_produced_by(self):
        if manim.config.save_last_frame:  # a still (-s): keep the scene's own last frame
            return
        if not self.produced_by:
            raise ValueError("Set produced_by on the scene to the name of the model that made it.")
        card = VGroup(
            Text("Produced by", font_size=28, color=manim.GRAY_B),
            Text(self.produced_by, font_size=48),
            Text(SKILL_URL, font_size=22, color=manim.GRAY_B),
        ).arrange(DOWN, buff=0.25)
        card[2].shift(0.15 * DOWN)
        card.reading_exempt = True  # shown for HOLD seconds on purpose; see reading_time.py

        frame = getattr(self.camera, "frame", None)  # MovingCameraScene / ZoomedScene
        if frame is not None:
            card.scale(frame.width / manim.config.frame_width).move_to(frame.get_center())
        if hasattr(self, "add_fixed_in_frame_mobjects"):  # ThreeDScene
            self.add_fixed_in_frame_mobjects(card)
            self.remove(card)

        rest = [m for m in self.mobjects if m is not frame and m is not card]
        if rest:
            self.play(FadeOut(Group(*rest)), run_time=FADE)
        self.play(FadeIn(card, shift=0.2 * UP), run_time=FADE)
        self.wait(HOLD)

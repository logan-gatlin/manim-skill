"""Read a Manim scene's narration aloud with Chatterbox Turbo (Resemble AI), a neural TTS.

Copy this file next to scene.py and list the mixin first:

    from narration import Narration
    from reading_time import ReadingTime

    class MyScene(Narration, ReadingTime, Scene):
        pronounce = {"edgeworker": "edge worker"}   # whole-word replacements in spoken text

        def construct(self):
            self.speak("The job runs every twenty minutes.")   # starts now, plays under what follows
            self.play(FadeIn(caption))
            self.play(clock.animate.rotate(-PI))
            self.speak("Then it checks out master.")          # waits for the line before to end

speak() waits until the previous line has finished, then starts the next one at the current
scene time; the animations after it play while it is spoken. With ReadingTime, text that
appears while a line is spoken must stay until the line and its GAP have ended, and
wait_to_read() holds until then (not for a word count). The scene waits for the last line
before it ends.

The voice is cloned from VOICE, a reference clip of Phil Benson reading (Hi-Fi TTS dataset,
speaker 6097, CC BY 4.0: https://www.openslr.org/109/). Set `voice_ref` on a scene to clone
another clip (a WAV over 5 s; the first 10-15 s are used).

Chatterbox runs on CPU in its own venv (~/.local/opt/chatterbox/.venv) through one worker
process (bin/say.py --serve), started on the first uncached line and kept for the render.
Lines are cached under <media_dir>/voice; the first synthesis of a line takes about 1-3x its
spoken length. The worker's log is <media_dir>/voice/chatterbox.log.
"""

import atexit
import hashlib
import json
import os
import re
import subprocess
import wave
from pathlib import Path

import manim

HOME = Path.home() / ".local/opt/chatterbox"
PYTHON = HOME / ".venv/bin/python"
WORKER = HOME / "bin/say.py"
VOICE = HOME / "voices/phil-benson.wav"
# temperature 0.8 is Turbo's default (0.3 made it skip and garble lines). Also: top_p, top_k,
# repetition_penalty. The worker's "pace" (WSOLA time-stretch) makes the voice audibly warbly; leave it out.
TTS = {"temperature": 0.8}
GAP = 0.5  # seconds of silence after each line: room to look at the diagram

# Turbo garbles these in technical text (checked with speech recognition across 5 voices):
# "200 ms" -> "200 nus reus", "k8s" -> "K8's", "2.4.1" -> "2.41". Acronyms such as
# API, TLS, HTTP, SDK and P99 come out fine and are left alone.
TECH_PRONOUNCE = {"k8s": "Kubernetes"}
UNITS = {"ms": "milliseconds", "µs": "microseconds", "us": "microseconds", "ns": "nanoseconds"}


class NarrationError(Exception):
    pass


_worker = None


def _get_worker():
    global _worker
    if _worker is None:
        if not PYTHON.exists():
            raise NarrationError(f"Chatterbox venv not found at {PYTHON}")
        env = dict(os.environ, HF_HUB_OFFLINE="1", PYTHONUNBUFFERED="1")
        log = Path(manim.config.media_dir).resolve() / "voice" / "chatterbox.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        _worker = subprocess.Popen(
            [str(PYTHON), "-I", str(WORKER), "--serve"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log.open("w"),
            text=True, env=env, cwd="/",
        )
        atexit.register(_worker.kill)
    return _worker


def synthesize(text, voice_ref=VOICE, tts=TTS):
    """Return (path, seconds) of a WAV of `text`, synthesizing it only if not cached."""
    tts = dict(tts or {})
    ref = Path(voice_ref).read_bytes() if voice_ref else b""
    opts = json.dumps(tts, sort_keys=True).encode()
    key = hashlib.sha1(b"chatterbox-turbo\0" + hashlib.sha1(ref).digest() + opts + text.encode()).hexdigest()[:16]
    out = Path(manim.config.media_dir).resolve() / "voice" / f"{key}.wav"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        w = _get_worker()
        voice = str(Path(voice_ref).resolve()) if voice_ref else None
        w.stdin.write(json.dumps({"text": text, "out": str(out), "voice": voice, **tts}) + "\n")
        w.stdin.flush()
        if not w.stdout.readline() or not out.exists():
            raise NarrationError(f"Chatterbox worker failed; see {out.parent / 'chatterbox.log'}")
    with wave.open(str(out)) as f:
        return out, f.getnframes() / f.getframerate()


def spoken(text, pronounce=None):
    """The text as it is sent to the voice: versions, units and `pronounce` words spelled out."""
    text = re.sub(r"\b\d+(?:\.\d+){2,}\b", lambda m: " point ".join(m[0].split(".")), text)  # 2.4.1
    text = re.sub(r"(\d)\s*(ms|µs|us|ns)(?![\w-])", lambda m: f"{m[1]} {UNITS[m[2]]}", text)  # only after a number
    for word, said in {**TECH_PRONOUNCE, **(pronounce or {})}.items():
        text = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", said, text)
    return text


class Narration:
    voice_ref = VOICE
    tts = TTS
    gap = GAP
    pronounce = {}

    def __init__(self, *args, **kwargs):
        # Wrap construct before ReadingTime does, so its check runs after the last line ends.
        self._voice_until = 0.0
        construct = self.construct

        def narrated_construct():
            construct()
            self.wait_for_voice()

        self.construct = narrated_construct
        super().__init__(*args, **kwargs)

    def _rt_budget(self, texts, started, shown):
        # ReadingTime hook: text revealed while a line is spoken stays until the line and its
        # gap end, so wait_to_read() moves on when the narrator does. Text shown during
        # silence keeps the word-count budget.
        if started < self._voice_until:
            return max(0.0, self._voice_until - shown)
        return super()._rt_budget(texts, started, shown)

    def speak(self, text):
        """Start reading `text` aloud once the previous line has finished."""
        self.wait_for_voice()
        path, seconds = synthesize(spoken(text, self.pronounce), self.voice_ref, self.tts)
        self._add_voice(path)
        self._voice_until = self._voice_now() + seconds + self.gap

    def _add_voice(self, path):
        # Not Scene.add_sound: it drops the sound whenever the previous animation came from
        # Manim's partial-movie cache (the renderer stays in "skipping" mode until the next play).
        r = self.renderer
        if getattr(r, "_original_skipping_status", False):  # rendering a still: no audio track
            return
        r.file_writer.add_sound(str(path), self._voice_now())

    def wait_for_voice(self):
        """Wait until the line being spoken has finished."""
        left = self._voice_until - self._voice_now()
        if left > 0:
            self.wait(left)

    def _voice_now(self):
        return float(self.renderer.time)

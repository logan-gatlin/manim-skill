# Installing the manim skill

These steps set up the skill and everything [SKILL.md](SKILL.md) expects, on Ubuntu 24.04, the system it was built on. On another Linux distribution, install the same packages under that distribution's names. Each step ends with a check. Run it and move on only when it passes.

The paths below are the ones SKILL.md and `narration.py` read. Install to exactly these paths; they aren't configurable.

## 1. System packages

These need `sudo`. If you can't run `sudo` without a password, ask the user to run the command.

```bash
sudo apt install build-essential pkg-config libcairo2-dev libpango1.0-dev \
  texlive texlive-latex-extra texlive-fonts-extra texlive-science cm-super dvisvgm
```

Install [uv](https://docs.astral.sh/uv/) if `uv --version` fails:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Check:** `latex --version`, `dvisvgm --version` and `uv --version` all succeed.

## 2. Manim

```bash
uv tool install --python 3.13 'manim[typst]==0.22.1'
```

Pin Python 3.13: SKILL.md points agents at the source under `lib/python3.13/`.

**Check:** `manim --version` prints `Manim Community v0.22.1`, and `~/.local/share/uv/tools/manim/lib/python3.13/site-packages/manim/` exists.

## 3. The skill

Clone the repo into the skills directory your agent reads, in a folder named `manim`. Claude Code reads `~/.claude/skills/`. For other agents, look up their skills directory in their docs.

```bash
git clone git@github.com:logan-gatlin/manim-skill.git ~/.claude/skills/manim
```

**Check:** `~/.claude/skills/manim/SKILL.md` exists (or the same path under your agent's directory). Use that path as `SKILL` in the steps below.

## 4. Narration voice (Chatterbox Turbo)

Narrated videos use Chatterbox Turbo, a neural text-to-speech model that runs on the CPU in its own virtualenv. It needs about 1.7 GB for the virtualenv and 3.8 GB for the model download. No GPU is needed. Without this step, the skill can still render stills and unnarrated videos, but any narrated render fails with `NarrationError`.

```bash
SKILL=~/.claude/skills/manim
C=~/.local/opt/chatterbox
mkdir -p "$C/bin" "$C/voices"
cp "$SKILL/chatterbox/say.py" "$C/bin/"
cp "$SKILL/chatterbox/voices/phil-benson.wav" "$C/voices/"
uv venv -p 3.11 "$C/.venv"
uv pip install -p "$C/.venv/bin/python" chatterbox-tts==0.1.7 'setuptools<81' \
  --index-strategy unsafe-best-match --extra-index-url https://download.pytorch.org/whl/cpu
# Download the model weights once. Renders run offline (HF_HUB_OFFLINE=1), so they can't fetch them later.
"$C/.venv/bin/python" -c 'from chatterbox.tts_turbo import ChatterboxTurboTTS; ChatterboxTurboTTS.from_pretrained(device="cpu")'
```

`say.py` is the worker process that `narration.py` starts. `phil-benson.wav` is the reference clip the voice is cloned from. It's from the Hi-Fi TTS dataset (speaker 6097, CC BY 4.0, https://www.openslr.org/109/).

**Check:** this writes a WAV of a few seconds to `/tmp/say-check.wav`:

```bash
HF_HUB_OFFLINE=1 CHATTERBOX_VOICE="$C/voices/phil-benson.wav" \
  "$C/.venv/bin/python" -I "$C/bin/say.py" /tmp/say-check.wav "The voice is installed."
```

## 5. End-to-end check

Render a short narrated scene that uses LaTeX, the reading-time checker and the voice:

```bash
mkdir -p /tmp/manim/install-check && cd /tmp/manim/install-check
cp "$SKILL/reading_time.py" "$SKILL/narration.py" .
cat > scene.py <<'EOF'
from manim import *
from narration import Narration
from reading_time import ReadingTime

class Check(Narration, ReadingTime, Scene):
    def construct(self):
        formula = MathTex(r"e^{i\pi} + 1 = 0")
        self.speak("Euler's identity links five constants.")
        self.play(Write(formula))
        self.wait_to_read()
EOF
manim render -ql --media_dir media -o check scene.py Check
~/.local/share/uv/tools/manim/bin/python -c "import av; print(sorted(s.type for s in av.open('media/videos/scene/480p15/check.mp4').streams))"
```

**Check:** the render finishes without errors, and the last command prints `['audio', 'video']`.

## Troubleshooting

- **TLS errors behind a proxy that intercepts HTTPS:** add `--system-certs` to the `uv` commands, and prefix the model download with `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`.
- **`No module named 'pkg_resources'`** when importing Chatterbox: the virtualenv has `setuptools` 81 or later. Reinstall with `'setuptools<81'`.
- **Synthesis is very slow:** the worker uses 6 CPU threads. Set `CHATTERBOX_THREADS` to a different number when rendering. More threads can be slower on a busy machine.

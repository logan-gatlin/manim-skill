"""Chatterbox Turbo TTS worker.

One-shot:  say.py OUT.wav "text"
Server:    say.py --serve   (reads JSON lines on stdin, one reply line each on stdout)
           request: {"text": ..., "out": ..., "voice": "/ref.wav" | null,
                     "temperature": 0.8, "top_p": 0.95, "top_k": 1000, "repetition_penalty": 1.2,
                     "pace": 1.0}   # <1 slows speech (WSOLA time-stretch); audibly warbly, so off by default
           reply:   {"out": ..., "seconds": ...}
"voice" is a reference WAV (>5 s; the first 10-15 s are used) to clone; null is the
built-in voice. Optional env: CHATTERBOX_VOICE (default voice), CHATTERBOX_THREADS.
"""
import json, os, sys, time, warnings
warnings.filterwarnings("ignore")
reply, sys.stdout = sys.stdout, sys.stderr  # libraries print to stdout; keep it for replies
import torch, torchaudio
from chatterbox.tts_turbo import ChatterboxTurboTTS

torch.set_num_threads(int(os.environ.get("CHATTERBOX_THREADS", "6")))
t0 = time.time()
model = ChatterboxTurboTTS.from_pretrained(device="cpu")
builtin = model.conds
voices = {None: builtin}
print(f"model loaded in {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

SAMPLING = ("temperature", "top_p", "top_k", "repetition_penalty")


def use_voice(ref):
    if ref not in voices:
        model.prepare_conditionals(ref)
        voices[ref] = model.conds
    model.conds = voices[ref]


def stretch(wav, pace):
    from audiotsm import wsola
    from audiotsm.io.array import ArrayReader, ArrayWriter
    w = ArrayWriter(1)
    wsola(1, speed=pace).run(ArrayReader(wav.numpy()), w)
    return torch.from_numpy(w.data.astype("float32"))


def synth(text, out, voice=None, pace=None, **sampling):
    t = time.time()
    use_voice(voice)
    wav = model.generate(text, **{k: v for k, v in sampling.items() if k in SAMPLING and v is not None})
    if pace and pace != 1.0:
        wav = stretch(wav, pace)
    tmp = out + ".tmp.wav"
    torchaudio.save(tmp, wav.clamp(-1, 1), model.sr, encoding="PCM_S", bits_per_sample=16)
    os.replace(tmp, out)
    secs = wav.shape[-1] / model.sr
    print(f"{secs:.1f}s audio in {time.time()-t:.1f}s [{voice}]: {text[:60]}", file=sys.stderr, flush=True)
    return secs


if sys.argv[1:2] == ["--serve"]:
    for line in sys.stdin:
        req = json.loads(line)
        secs = synth(req.pop("text"), req["out"], req.pop("voice", None) or os.environ.get("CHATTERBOX_VOICE"),
                     pace=req.get("pace"), **{k: req.get(k) for k in SAMPLING})
        print(json.dumps({"out": req["out"], "seconds": secs}), file=reply, flush=True)
else:
    synth(sys.argv[2], sys.argv[1], os.environ.get("CHATTERBOX_VOICE"))

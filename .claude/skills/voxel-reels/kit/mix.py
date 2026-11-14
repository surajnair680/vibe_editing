#!/usr/bin/env python3
"""Voxel reels: mix voice + music (ducked under the voice) + a sound on every cue into build/mix.wav.

    python3 mix.py <project>

Needs build/vo.wav, build/timing.json (voice.py) and build/events.json (the page's cue list:
`sh tools/lemo.sh node core/render/events.mjs <abs project> --size 1080x1920 --out <abs project>/build/events.json`).
reel.json "sfx" maps a cue type (cut, pop, tick, count, type, chime) to a sound, and "music" is optional:
  "sfx":   {"cut": {"file": "assets/sfx/openverse/whoosh.mp3", "gain": -12, "peak": 0.18}, "pop": {...}, ...}
  "music": {"file": "assets/music/bed.mp3", "gain": -16, "duck": 9, "fade": 1.2}
"peak" = seconds from the start of the file to its loudest point (openverse_sfx.py measures it): the sound is placed so
the peak lands on the cue. "type" cues loop their sound for the cue's length. No sound is ever placed twice on one cue,
and "cut" sounds alternate between the files in "files" (a list) so whooshes don't repeat.
The output is not loudness-normalised: core/render/mux.sh masters it to -14 LUFS when it muxes the video.
"""
import json, os, subprocess, sys
import numpy as np
import soundfile as sf

SR = 48000


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db(x): return 10 ** (x / 20)


def main(project):
    P = lambda *a: os.path.join(project, *a)
    R = json.load(open(P("reel.json"))); T = json.load(open(P("build", "timing.json")))
    ev = json.load(open(P("build", "events.json")))
    dur = ev["dur"]; n = int(dur * SR) + SR // 2
    vo, _ = sf.read(P("build", "vo.wav"), dtype="float32")
    out = np.zeros((n, 2), np.float32)
    out[:len(vo)] += np.repeat(vo[:n, None], 2, axis=1)

    # music, ducked by the voice envelope (sidechain: fast attack, 250 ms release)
    m = R.get("music")
    if m:
        mus = decode(P(m["file"]))
        need = n
        if len(mus) < need:                        # loop whole file (find phrase boundaries first for real tracks)
            mus = np.concatenate([mus] * (need // len(mus) + 1))
        mus = mus[:need] * db(m.get("gain", -16))
        hop = SR // 100; e = np.array([np.sqrt(np.mean(vo[i:i + hop] ** 2)) for i in range(0, len(vo), hop)])
        e = np.concatenate([e, np.zeros(need // hop + 2 - len(e))]) if len(e) < need // hop + 2 else e
        on = (e > 0.01).astype(float); g = np.zeros_like(on); v = 0.0
        for i, x in enumerate(on):
            v = max(x, v * np.exp(-1 / 25))        # 10 ms steps, 250 ms release
            g[i] = v
        gain = db(-m.get("duck", 9) * g)
        gain = np.interp(np.arange(need) / hop, np.arange(len(gain)), gain)
        fade = m.get("fade", 1.2); f = np.ones(need)
        f[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
        fo = int(fade * SR); f[int(dur * SR) - fo:int(dur * SR)] = np.linspace(1, 0, fo); f[int(dur * SR):] = 0
        out += mus * (gain * f)[:, None]

    # one sound per cue
    S = R.get("sfx", {}); cache = {}; used = {}
    def snd(path):
        if path not in cache: cache[path] = decode(P(path))
        return cache[path]
    for e in ev["ev"]:
        s = S.get(e["type"])
        if not s: continue
        files = s.get("files") or [s["file"]]
        k = used.get(e["type"], 0); used[e["type"]] = k + 1
        x = snd(files[k % len(files)]) * db(s.get("gain", -12))
        if e["type"] == "type" and e.get("dur"):
            reps = int(np.ceil(e["dur"] * SR / len(x))); x = np.concatenate([x] * reps)[:int(e["dur"] * SR)]
        a = int((e["t"] - s.get("peak", 0.0)) * SR)
        if a < 0: x = x[-a:]; a = 0
        b = min(n, a + len(x)); out[a:b] += x[:b - a]
    out = out[:int(dur * SR)]
    pk = np.abs(out).max()
    if pk > 0.99: out *= 0.99 / pk
    sf.write(P("build", "mix.wav"), out, SR, subtype="FLOAT")
    print(f"mix.wav {len(out) / SR:.2f} s, {sum(used.values())} sounds placed, peak {20 * np.log10(pk + 1e-9):.1f} dBFS")


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(os.path.abspath(sys.argv[1]))

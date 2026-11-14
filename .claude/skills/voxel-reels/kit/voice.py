#!/usr/bin/env python3
"""Voxel reels: make every line's voice with ElevenLabs and build the timing files the scene reads.

    python3 voice.py <project>            generate missing lines (paid), then assemble
    python3 voice.py <project> --dry      show what would be generated and the character count, pay nothing
    python3 voice.py <project> --assemble only rebuild build/ from the line files already in voices/

Reads <project>/reel.json:
  "voices": {"ME": {"voice_id": "...", "model": "eleven_multilingual_v2",
                    "settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25}}, "SIDEKICK": {...}}
  "lines":  [{"id": 1, "who": "ME", "text": "..."}, ...]
  "gap": 0.14   seconds between lines,  "lead": 0.35  silence before the first line

Each line is one request to /v1/text-to-speech/<voice>/with-timestamps (character timings come back with the audio,
so no transcription is needed for captions). The mp3 and its alignment go to voices/<id>.mp3 and voices/<id>.json and
are never requested again while the text is unchanged (paid audio: commit voices/). Neighbouring lines of the same
speaker are sent as previous_text / next_text so the delivery flows.

Writes <project>/build/: vo.wav (48 kHz mono), timing.json {dur, fps, lines, words, env}.
env = per-frame loudness 0..1 of whoever is speaking (mouths and bounce read it).
"""
import base64, json, os, re, subprocess, sys, time, hashlib
import numpy as np
import soundfile as sf

SR = 48000
API = "https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps"


def load(project):
    with open(os.path.join(project, "reel.json")) as f:
        return json.load(f)


def text_key(line, voice):
    s = json.dumps([line["text"], voice.get("voice_id"), voice.get("model"), voice.get("settings")], sort_keys=True)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def request(vid, body):
    import urllib.request, urllib.error
    data = json.dumps(body).encode()
    for wait in (5, 10, 20, 40, None):
        req = urllib.request.Request(API.format(vid=vid), data=data, method="POST",
                                     headers={"Content-Type": "application/json", "xi-api-key": "injected-by-proxy"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code == 429 and wait:          # shared account: at most 2 requests at a time (CLAUDE.md rule 7)
                print(f"  429, retry in {wait}s: {msg[:120]}"); time.sleep(wait); continue
            sys.exit(f"ElevenLabs {e.code}: {msg}")


def generate(project, cfg, dry=False):
    vdir = os.path.join(project, "voices"); os.makedirs(vdir, exist_ok=True)
    lines, todo, chars = cfg["lines"], [], 0
    for i, ln in enumerate(lines):
        v = cfg["voices"][ln["who"]]
        key = text_key(ln, v)
        meta = os.path.join(vdir, f"{ln['id']}.json")
        if os.path.exists(meta) and json.load(open(meta)).get("key") == key and os.path.exists(meta[:-5] + ".mp3"):
            continue
        todo.append((i, ln, v, key)); chars += len(ln["text"])
    print(f"{len(todo)} of {len(lines)} lines to generate, {chars} characters")
    if dry or not todo:
        return
    for i, ln, v, key in todo:
        same = [l for l in lines if l["who"] == ln["who"]]
        k = same.index(ln)
        body = {"text": ln["text"], "model_id": v.get("model", "eleven_multilingual_v2"),
                "voice_settings": v.get("settings", {})}
        if k > 0: body["previous_text"] = same[k - 1]["text"]
        if k + 1 < len(same): body["next_text"] = same[k + 1]["text"]
        print(f"  line {ln['id']} ({ln['who']}): {ln['text']}")
        r = request(v["voice_id"], body)
        with open(os.path.join(vdir, f"{ln['id']}.mp3"), "wb") as f:
            f.write(base64.b64decode(r["audio_base64"]))
        json.dump({"key": key, "text": ln["text"], "alignment": r.get("alignment")},
                  open(os.path.join(vdir, f"{ln['id']}.json"), "w"), indent=0)


def decode(path):
    # decode from the start to WAV samples (never seek into an mp3: CLAUDE.md lesson)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def words_from_alignment(al):
    """characters + start/end times -> [(word, start, end)]"""
    if not al:
        return []
    ch, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, cur, s0, e0 = [], "", None, None
    for c, s, e in zip(ch, st, en):
        if c.isspace():
            if cur: out.append((cur, s0, e0)); cur = ""
            continue
        if not cur: s0 = s
        cur += c; e0 = e
    if cur: out.append((cur, s0, e0))
    return out


def assemble(project, cfg):
    fps = cfg.get("fps", 30); gap = cfg.get("gap", 0.14); lead = cfg.get("lead", 0.35)
    vdir = os.path.join(project, "voices"); bdir = os.path.join(project, "build"); os.makedirs(bdir, exist_ok=True)
    pieces, target = [], cfg.get("voice_db", -20.0)
    for ln in cfg["lines"]:
        x = decode(os.path.join(vdir, f"{ln['id']}.mp3"))
        meta = json.load(open(os.path.join(vdir, f"{ln['id']}.json")))
        # trim silence at both ends, measured in 10 ms windows, keeping 40 ms of room
        w = SR // 100; n = len(x) // w
        e = np.array([np.sqrt(np.mean(x[i * w:(i + 1) * w] ** 2)) for i in range(n)])
        floor = max(1e-4, e.max() * 0.02)
        on = np.where(e > floor)[0]
        a = max(0, on[0] - 4) * w if len(on) else 0
        b = min(len(x), (on[-1] + 5) * w) if len(on) else len(x)
        y = x[a:b]
        voiced = y[np.abs(y) > np.abs(y).max() * 0.05]
        y = y * 10 ** ((target - rms_db(voiced)) / 20)          # loudness-match both voices
        pieces.append((ln, y, a / SR, words_from_alignment(meta.get("alignment"))))
    out, t, lines, words = [np.zeros(int(lead * SR), np.float32)], lead, [], []
    for k, (ln, y, off, wl) in enumerate(pieces):
        start, end = t, t + len(y) / SR
        lines.append({"id": ln["id"], "who": ln["who"], "text": ln["text"], "start": round(start, 3), "end": round(end, 3)})
        for wd, s, e in wl:
            ws = min(end, start + max(0.0, s - off)); we = min(end, start + max(0.0, e - off))
            words.append({"w": wd, "line": ln["id"], "who": ln["who"], "start": round(ws, 3), "end": round(max(ws, we), 3)})
        out.append(y.astype(np.float32)); t = end
        if k + 1 < len(pieces):
            out.append(np.zeros(int(gap * SR), np.float32)); t += gap
    vo = np.concatenate(out)
    peak = np.abs(vo).max()
    if peak > 0.98: vo *= 0.98 / peak
    sf.write(os.path.join(bdir, "vo.wav"), vo, SR, subtype="FLOAT")
    dur = len(vo) / SR
    # per-frame loudness envelope (fast attack, slower release), 0..1
    hop = SR / fps; nf = int(np.ceil(dur * fps)) + 1
    env = np.zeros(nf)
    for i in range(nf):
        s = int(i * hop); seg = vo[s:s + int(hop)]
        env[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    env = env / (np.percentile(env[env > 0], 95) if (env > 0).any() else 1)
    sm = np.zeros_like(env); v = 0
    for i, x in enumerate(env):
        v = x if x > v else v * 0.6 + x * 0.4
        sm[i] = min(1.0, v)
    timing = {"dur": round(dur, 3), "fps": fps, "lines": lines, "words": words, "env": [round(float(x), 3) for x in sm]}
    json.dump(timing, open(os.path.join(bdir, "timing.json"), "w"))
    print(f"vo.wav {dur:.2f} s, {len(lines)} lines, {len(words)} words -> {bdir}/timing.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1]); cfg = load(proj)
    if "--assemble" not in sys.argv:
        generate(proj, cfg, dry="--dry" in sys.argv)
    if "--dry" not in sys.argv:
        assemble(proj, cfg)

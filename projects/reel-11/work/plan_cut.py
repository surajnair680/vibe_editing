"""Rough cut plan for reel-11 -> work/cut_plan.json.

Cut points come from the voice envelope (10 ms steps), not padded word times (lesson from reel-02):
  in  = last quiet frame before the first word's onset (so an inhale is kept), never before the previous word ends
  out = first point after the last word where the voice has decayed to the noise floor for 80 ms,
        never past the next word's start.
Word times are ElevenLabs Scribe (work/transcripts/<clip>/words.json). Run from the project folder.
"""
import json
import numpy as np
import soundfile as sf

FPS = 30
HOP = 0.01

# lo overrides: me_2 1.45 (mic still rising before that, picture checked), me_3a 12.75 (1.1 s breath before "But")
# (clip, first word start, last word end, earliest allowed in, latest allowed out, text)
LINES = [
    ("her_full", 0.64, 8.36, 0.00, 8.92, "Stop chasing perfection. Just start speaking. You know why your English is not improving? Because you are waiting for perfection."),
    ("her_full", 20.08, 24.84, 19.72, 25.00, "So listen, you don't need to speak perfect English. You just need to have courage to speak."),
    ("me_2", 1.70, 4.12, 1.45, 5.97, "I don't understand what is so inspiring about her."),
    ("me_3a", 0.68, 10.76, 0.00, 13.00, "Let's say you want to look like your favorite celebrity. Therefore, you should procrastinate for six months overthinking whether keto, intermittent fasting, or push-pull legs is the perfect plan."),
    ("me_3a", 13.00, None, 12.75, None, "But why start now when you can wait for next Monday while sitting-"),   # runs to the end of part 3a
    ("me_3b", None, 1.40, 0.00, 3.68, "on your ass gaining fat"),                                                 # from the start of part 3b
    ("me_3b", 3.68, 7.74, 1.40, 10.28, "so that you can successfully protect a physique you are unhappy with anyway."),
    ("me_3d", 1.46, 14.18, 0.00, 15.21, "Just ignore this lady and whatever you do, do not share this video with that one friend who has been starting their fitness journey next Monday since 2020. And follow me to learn how to skip the gym and stay stuck forever."),
]


def envelope(x, sr):
    n = int(HOP * sr)
    w = 2 * n
    frames = max(1, (len(x) - w) // n)
    e = np.array([np.sqrt(np.mean(x[i * n:i * n + w] ** 2) + 1e-12) for i in range(frames)])
    return 20 * np.log10(e)


def plan():
    cache, segs, t = {}, [], 0.0
    for clip, s, e, lo, hi, text in LINES:
        if clip not in cache:
            x, sr = sf.read(f"work/audio/{clip}.wav")
            env = envelope(x, sr)
            floor = np.percentile(env, 10)
            cache[clip] = (env, floor, len(x) / sr)
        env, floor, dur = cache[clip]
        quiet = env < floor + 6
        if s is None:
            a = 0.0
        else:
            i = int(s / HOP)
            # walk back from the onset to the last quiet frame (keeps the inhale), not past lo
            while i > 0 and i * HOP > lo and not (quiet[i] and quiet[max(0, i - 1)] and quiet[max(0, i - 2)]):
                i -= 1
            a = max(lo, i * HOP - 0.03)
        if e is None:
            b = dur
        else:
            j = int(e / HOP)
            hi_ = dur if hi is None else hi
            while j < len(quiet) - 8 and j * HOP < hi_ and not quiet[j:j + 8].all():
                j += 1
            b = min(hi_, j * HOP + 0.05)
        a = round(a * FPS) / FPS
        b = round(b * FPS) / FPS if e is not None else np.floor(dur * FPS) / FPS
        segs.append({"clip": clip, "src_in": round(a, 4), "src_out": round(b, 4),
                     "edit_in": round(t, 4), "text": text,
                     "floor_db": round(float(floor), 1)})
        t = round(t + b - a, 4)
    json.dump({"fps": FPS, "length": t, "segments": segs}, open("work/cut_plan.json", "w"), indent=1)
    for g in segs:
        print(f"{g['edit_in']:6.2f}  {g['clip']:6s} {g['src_in']:6.2f}-{g['src_out']:6.2f}  {g['text'][:60]}")
    print("length", round(t, 2))


if __name__ == "__main__":
    plan()

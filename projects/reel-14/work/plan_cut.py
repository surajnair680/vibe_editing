"""Rough cut plan for reel-14 -> work/cut_plan.json. Global times on the joined source (work/full.mp4,
work/parts.json offsets 0 / 42 / 71 / 99 / 127), 30 fps out. Adapted from reel-13's plan_cut.py.
Segment 0 = her reaction composite, untouched with its original audio (0 to 27.3167 s, the frame her clip ends).
After that every pause longer than GAP is cut. Cut points come from the isolated voice envelope (10 ms steps):
  out = first point after the last word where the voice stays under -45 dB for 80 ms, plus 50 ms
  in  = walk back from the line's first onset to the last quiet frames (keeps the inhale), minus 30 ms
Lines may cross the part seams (p1/p2 "So / is something", p2/p3 "balance does / not hold up"): the join is
continuous in picture and sound. Run from the project folder."""
import json, subprocess
import numpy as np, soundfile as sf

FPS, HOP, GAP, T0 = 30, 0.01, 0.38, 27.3167
P = json.load(open("work/parts.json"))
files = ["work/words.json"] + [f"work/p{i}/words.json" for i in range(2, 6)]
W = []
for off, f in zip(P["offsets"], files):
    W += [dict(w, s=round(w["s"] + off, 3), e=round(w["e"] + off, 3)) for w in json.load(open(f)) if w["w"].strip()]
json.dump(W, open("work/words_full.json", "w"), indent=0)
W = [w for w in W if w["s"] > T0]
LEAD = 0.10
def first_motion(t0, t1, thr=5):
    """first frame time in [t0, t1+0.1] where the lower half (mic hand) moves by >= thr grey levels per frame."""
    d = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", "work/full.mp4", "-frames:v", "11", "-vf",
                        "fps=30,crop=1080:900:0:1020,scale=108:90,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(d, np.uint8).reshape(-1, 90, 108).astype(float); m = np.abs(np.diff(f, axis=0)).mean((1, 2))
    hit = [t0 + (i + 1) / 30 for i, v in enumerate(m) if v >= thr]
    return hit[0] if hit else None
# per-line overrides keyed by the first word's start / last word's end (filled after looking at frames)
IN_FLOOR = {}
OUT_CEIL = {}
x, sr = sf.read("work/audio/full_iso.wav")
n = int(HOP * sr)
env = 20 * np.log10(np.array([np.sqrt(np.mean(x[i * n:i * n + 2 * n] ** 2) + 1e-12) for i in range(len(x) // n - 2)]))
floor = np.percentile(env[int(T0 / HOP):], 10)
quiet = env < floor + 8
decayed = env < -45
print("floor dB", round(floor, 1))

lines, cur = [], [W[0]]
for w in W[1:]:
    if w["s"] - cur[-1]["e"] > GAP:
        lines.append(cur); cur = [w]
    else:
        cur.append(w)
lines.append(cur)

segs = [{"src_in": 0.0, "src_out": int(T0 * FPS) / FPS, "text": "[her clip + reaction, original audio]", "audio": "orig"}]
for k, ln in enumerate(lines):
    s, e = ln[0]["s"], ln[-1]["e"]
    lo = segs[-1]["src_out"]
    hi = min(P["length"] - 1 / FPS, lines[k + 1][0]["s"] - 0.05 if k + 1 < len(lines) else 1e9)
    i = int(s / HOP)
    while i * HOP > lo and not (quiet[i] and quiet[i - 1] and quiet[i - 2]):
        i -= 1
    # he raises the mic into frame before every line (frame strips work/frames/ins.jpg): it is up about 0.1 s
    # before the first word, so start there at the earliest (trims the start of the inhale, 5 ms fade in)
    a = max(lo, i * HOP - 0.03, s - LEAD, IN_FLOOR.get(round(s, 2), 0))
    j = int(e / HOP)
    while j * HOP < hi and not decayed[j:j + 8].all():
        j += 1
    b = min(hi, j * HOP + 0.05, OUT_CEIL.get(round(e, 2), 1e9))
    # he drops the mic as he finishes a line: if the lower half starts moving before b, end at the later of
    # the -35 dB decay point + 1 frame and the first moving frame (reel-13 lesson, work/frames/cuts.jpg)
    d = int(e / HOP)
    while env[d] > -35 and d * HOP < b: d += 1
    mv = first_motion(b - 0.33, b)
    if mv is not None and mv < b: b = max(d * HOP + 1 / FPS, mv)
    a, b = round(a * FPS) / FPS, round(b * FPS) / FPS
    if k == 0: a = max(a, T0)
    segs.append({"src_in": round(a, 4), "src_out": round(b, 4), "text": " ".join(w["w"] for w in ln), "audio": "iso"})
out = [segs[0]]
for g in segs[1:]:
    if g["src_in"] - out[-1]["src_out"] < 0.1 + 1e-6 and out[-1]["audio"] == "iso":   # never jump-cut a gap under 0.1 s
        out[-1] = dict(out[-1], src_out=g["src_out"], text=out[-1]["text"] + " / " + g["text"])
    else:
        out.append(g)
t = 0.0
for g in out:
    g["edit_in"] = round(t, 4); t += g["src_out"] - g["src_in"]
json.dump({"fps": FPS, "length": round(t, 4), "segments": out}, open("work/cut_plan.json", "w"), indent=1)
for g in out:
    print(f"{g['edit_in']:6.2f}  src {g['src_in']:7.2f}-{g['src_out']:7.2f} ({g['src_out']-g['src_in']:.2f})  {g['text'][:70]}")
print("length", round(t, 2), "removed", round(P["length"] - t, 2))

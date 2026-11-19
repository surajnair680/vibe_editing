"""Rough cut plan for reel-12 -> work/cut_plan.json (times in the joined source work/full.mp4, 60 fps).

0 to 24.70 s: her clip with his reaction inset, kept exactly as it came (the hook, user: "stays the same").
From 24.70 s (frame 1482, the switch to him): every pause longer than GAP is cut out. Cut points come from the
voice envelope of the isolated voice (10 ms steps), not padded word times (lesson from reel-02):
  out = first point after the last word where the voice stays under -45 dB for 80 ms, plus 50 ms
  in  = walk back from the next word's onset to the last quiet frame (keeps the inhale), minus 30 ms
Pieces snap to whole frames of the 30 fps edit. Run from the project folder.
"""
import json
import numpy as np, soundfile as sf

FPS, HOP, GAP, HIM = 30, 0.01, 0.38, 24.70
W = json.load(open("work/words_full.json"))
# earliest in-point per line (picture checked): 77.74 'फिर' - mic still rising into frame until 77.6
IN_FLOOR = {77.74: 77.63}
x, sr = sf.read("work/audio/full_iso.wav")
n = int(HOP * sr)
env = 20 * np.log10(np.array([np.sqrt(np.mean(x[i * n:i * n + 2 * n] ** 2) + 1e-12) for i in range(len(x) // n - 2)]))
him = env[int(HIM / HOP):]
floor = np.percentile(him, 10)
quiet = env < floor + 8          # in-points: walk back through the inhale to real silence
decayed = env < -45              # out-points: word has decayed below breath / room level (phone gates to digital silence)
dur = len(x) / sr
print("floor dB", round(floor, 1))

him_words = [w for w in W if w["s"] >= HIM]
lines, cur = [], [him_words[0]]
for w in him_words[1:]:
    if w["s"] - cur[-1]["e"] > GAP:
        lines.append(cur); cur = [w]
    else:
        cur.append(w)
lines.append(cur)

segs = [{"src_in": 0.0, "src_out": HIM, "text": "[her clip + reaction inset, untouched]"}]
for k, ln in enumerate(lines):
    s, e = ln[0]["s"], ln[-1]["e"]
    lo = segs[-1]["src_out"] if k else HIM
    hi = lines[k + 1][0]["s"] - 0.05 if k + 1 < len(lines) else dur
    i = int(s / HOP)
    while i * HOP > lo and not (quiet[i] and quiet[i - 1] and quiet[i - 2]):
        i -= 1
    a = max(lo, i * HOP - 0.03)
    a = max(a, IN_FLOOR.get(round(s, 2), 0))
    j = int(e / HOP)
    while j * HOP < hi and not decayed[j:j + 8].all():
        j += 1
    b = min(hi, j * HOP + 0.05)
    a, b = round(a * FPS) / FPS, round(b * FPS) / FPS
    segs.append({"src_in": round(a, 4), "src_out": round(b, 4), "text": " ".join(w["w"] for w in ln)})
# merge pieces that touch (no real cut)
out = [segs[0]]
for g in segs[1:]:
    if g["src_in"] - out[-1]["src_out"] < 1 / FPS + 1e-6:
        out[-1] = {"src_in": out[-1]["src_in"], "src_out": g["src_out"], "text": out[-1]["text"] + " / " + g["text"]}
    else:
        out.append(g)
t = 0.0
for g in out:
    g["edit_in"] = round(t, 4); t += g["src_out"] - g["src_in"]
json.dump({"fps": FPS, "length": round(t, 4), "segments": out}, open("work/cut_plan.json", "w"), indent=1, ensure_ascii=False)
for g in out:
    print(f"{g['edit_in']:6.2f}  src {g['src_in']:7.2f}-{g['src_out']:7.2f}  {g['text'][:70]}")
print("length", round(t, 2), "removed", round(dur - t, 2))

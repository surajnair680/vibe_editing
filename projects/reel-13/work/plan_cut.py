"""Rough cut plan for reel-13 -> work/cut_plan.json. Times are global (part offsets from work/parts.json:
part1 0, part2 36.0, part3 72.0), 30 fps. Adapted from reel-12's plan_cut.py.
Every pause longer than GAP is cut. Cut points come from the isolated voice envelope (10 ms steps), not padded
word times (lesson from reel-02):
  out = first point after the last word where the voice stays under -45 dB for 80 ms, plus 50 ms
  in  = walk back from the line's first onset to the last quiet frames (keeps the inhale), minus 30 ms
No piece crosses a part seam. Run from the project folder."""
import json
import numpy as np, soundfile as sf

FPS, HOP, GAP = 30, 0.01, 0.38
P = json.load(open("work/parts.json"))
W = []
for off, f in zip(P["offsets"], ["work/words.json", "work/p2/words.json", "work/p3/words.json"]):
    W += [dict(w, s=round(w["s"] + off, 3), e=round(w["e"] + off, 3)) for w in json.load(open(f)) if w["w"].strip()]
json.dump(W, open("work/words_full.json", "w"), indent=0)
# per-line earliest in-point, keyed by the first word's start: the mic is still being raised into frame before
# these (frame strips work/frames/inpoints.jpg, motion work/mic_motion.py), so start once it is up
# per-line latest out-point, keyed by the line's last word end (user note on rough v1: after "supplements" he
# reaches out to stop the camera; the word's "s" has decayed by 71.70, the mic leaves frame from 71.60)
OUT_CEIL = {71.58: 71.70}
IN_FLOOR = {5.82: 5.66, 10.24: 10.10, 32.12: 32.00, 56.5: 56.30, 69.32: 69.10}
x, sr = sf.read("work/audio/full_iso.wav")
n = int(HOP * sr)
env = 20 * np.log10(np.array([np.sqrt(np.mean(x[i * n:i * n + 2 * n] ** 2) + 1e-12) for i in range(len(x) // n - 2)]))
floor = np.percentile(env, 10)
quiet = env < floor + 8
decayed = env < -45
print("floor dB", round(floor, 1))
ends = P["offsets"][1:] + [P["length"]]
part_of = lambda t: max(i for i, o in enumerate(P["offsets"]) if t >= o - 1e-6)

lines, cur = [], [W[0]]
for w in W[1:]:
    if w["s"] - cur[-1]["e"] > GAP or part_of(w["s"]) != part_of(cur[-1]["s"]):
        lines.append(cur); cur = [w]
    else:
        cur.append(w)
lines.append(cur)

segs = []
for k, ln in enumerate(lines):
    s, e = ln[0]["s"], ln[-1]["e"]; pi = part_of(s)
    lo = max(P["offsets"][pi], segs[-1]["src_out"] if segs else 0)
    hi = min(ends[pi] - 1 / FPS, lines[k + 1][0]["s"] - 0.05 if k + 1 < len(lines) else 1e9)
    i = int(s / HOP)
    while i * HOP > lo and not (quiet[i] and quiet[i - 1] and quiet[i - 2]):
        i -= 1
    a = max(lo, i * HOP - 0.03, IN_FLOOR.get(round(s, 2), 0))
    j = int(e / HOP)
    while j * HOP < hi and not decayed[j:j + 8].all():
        j += 1
    b = min(hi, j * HOP + 0.05)
    b = min(b, OUT_CEIL.get(round(e, 2), 1e9))
    a, b = round(a * FPS) / FPS, round(b * FPS) / FPS
    segs.append({"src_in": round(a, 4), "src_out": round(b, 4), "text": " ".join(w["w"] for w in ln)})
out = [segs[0]]
for g in segs[1:]:
    if g["src_in"] - out[-1]["src_out"] < 1 / FPS + 1e-6 and part_of(g["src_in"]) == part_of(out[-1]["src_in"]):
        out[-1] = {"src_in": out[-1]["src_in"], "src_out": g["src_out"], "text": out[-1]["text"] + " / " + g["text"]}
    else:
        out.append(g)
# trims and deletions made in the timeline editor page (tools/timeline, ids c01.. in plan order), saved by
# Claude from the page's edits/current document into work/timeline_edits.json; cleared once rendered
import os
TE = "work/timeline_edits.json"
if os.path.exists(TE):
    cuts = json.load(open(TE)).get("cuts", {})
    kept = []
    for k, g in enumerate(out):
        o = cuts.get(f"c{k + 1:02d}", {})
        if o.get("deleted"): print("timeline edit: delete", k + 1, g["text"][:30]); continue
        if "src_in" in o: g["src_in"] = round(o["src_in"], 4)
        if "src_out" in o: g["src_out"] = round(o["src_out"], 4)
        if o: print("timeline edit: cut", k + 1, g["src_in"], g["src_out"])
        kept.append(g)
    out = kept
t = 0.0
for g in out:
    g["edit_in"] = round(t, 4); t += g["src_out"] - g["src_in"]
json.dump({"fps": FPS, "length": round(t, 4), "segments": out}, open("work/cut_plan.json", "w"), indent=1)
for g in out:
    print(f"{g['edit_in']:6.2f}  src {g['src_in']:7.2f}-{g['src_out']:7.2f} ({g['src_out']-g['src_in']:.2f})  {g['text'][:70]}")
print("length", round(t, 2), "removed", round(P["length"] - t, 2))

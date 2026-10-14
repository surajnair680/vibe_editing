"""Rough cut plan for reel-02 -> work/cut_plan.json.
Clip A (hook) then clip B (story). Second takes of the two repeated lines. Pauses between lines trimmed to about
0.25 s (0.10 s lead-in, 0.16 s tail), mid-line beats kept unless longer than 0.4 s. Times snap to 1/30 s frames."""
import json

FPS = 30
A, B = "raw/VID20261007161237.mp4", "raw/1000097826.mp4"
# (source, first word start, last word end, note)  -- word times from work/*/words.json
lines = [
    (A, 0.62, 3.32, "Intelligent people like you cannot build their dream physique"),
    (A, 6.48, 9.80, "because you, my friend, have a disease called analysis paralysis"),
    (B, 0.58, 3.02, "A photography professor split his class in two."),
    (B, 6.32, 9.00, "One group would be graded only on how many photos they took."),
    (B, 11.46, 14.88, "The other group had only one chance to take one perfect photo."),
    (B, 24.50, 28.66, "At the end, the best photos all came from the group taking the most photos. (take 2)"),
    (B, 31.02, 34.38, "The perfect photo group just sat around thinking about perfection."),
    (B, 43.46, 48.28, "Repeated actions will teach you things your thoughts never can, no matter how intelligent you are. (take 2)"),
    (B, 51.02, 55.44, "Stop chasing the perfect exercise, perfect diet, and the perfect workout program."),
    (B, 57.82, 60.82, "Bring it into existence first, then make it perfect,"),
    (B, 64.30, 65.50, "not the other way around."),
    (B, 68.26, 71.02, "With whatever knowledge you have right now, just start."),
]
LEAD, TAIL = 0.10, 0.16
# Revisions 1 and 2 (user: cuts from "no matter how intelligent you are" to the end felt abrupt; then: "are" and
# "program" still clipped, too much time before "not" and "With", and the end showed the mic coming down).
# Absolute source in/out times, from the voice envelope in 10 ms steps and the picture.
EXACT = {7: (None, 48.78),      # the trailing "r" of "are" runs to 48.70
         8: (50.50, 55.85),     # "Stop" from its inhale at 50.55; the "m" of "program" hums to about 55.66
         9: (57.48, 61.05),     # "Bring" inhale at 57.54; "first, then" left uncut
         10: (64.10, 65.75),    # "not" starts at 64.20, no long breath in front
         11: (68.10, 71.60)}    # mic is up by 68.1 (eyes on the phone before that); exhale ends 71.45, mic drops at 71.8
snap = lambda t: round(t * FPS) / FPS
segs, t = [], 0.0
for i, (src, s, e, text) in enumerate(lines):
    a, b = snap(s - LEAD), snap(e + TAIL)
    if i in EXACT:
        a, b = [snap(v) if v is not None else d for v, d in zip(EXACT[i], (a, b))]
    segs.append({"src": src, "src_in": round(a, 5), "src_out": round(b, 5), "edit_in": round(t, 5), "text": text})
    t = snap(t + b - a)
json.dump({"fps": FPS, "length": round(t, 5), "segments": segs}, open("work/cut_plan.json", "w"), indent=1)
for s in segs:
    print(f"{s['edit_in']:6.2f}  {s['src'][4:7]}  {s['src_in']:6.2f}-{s['src_out']:6.2f}  {s['text']}")
print("length", round(t, 2))
